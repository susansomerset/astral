"""
Platform astral-agent client (AST-2238).

Contract mirror: service/astral_agent/jobqueue.py owns the schema. Same table and
channel names; the import fence forbids sharing code — change both sides together.

Callers (future AST-2240) enqueue an assembled provider request jsonb and await
the terminal result. Decode, grade, and daisy-chain stay on the platform.
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import threading
import time
import uuid
import zlib
from typing import Any, Awaitable, Dict, List, Optional
from urllib.parse import urlsplit, urlunsplit

import asyncpg
import httpx

from src.utils.config import ASTRAL_AGENT_CONFIG
from src.utils.integration_io import require_controlled_external_io
from src.utils.logging import get_logger

_log = get_logger(__name__)

# Contract mirror: service/astral_agent/jobqueue.py (AST-2237).
_JOB_TABLE = "agent_job"
_WORKER_TABLE = "agent_worker"
_CHANNEL_NEW = "agent_job_new"
_CHANNEL_DONE = "agent_job_done"
_TERMINAL = ("done", "failed", "cancelled")

_PASSTHROUGH_SKIP = frozenset({"timeout", "expired", "cancelled"})


class AstralAgentError(Exception):
    def __init__(self, failure_class: str, detail: str) -> None:
        self.failure_class = failure_class
        self.detail = detail
        super().__init__(f"[{failure_class}] {detail}")


def _decode_result(blob: Optional[bytes]) -> Any:
    if blob is None:
        return None
    return json.loads(zlib.decompress(blob).decode("utf-8"))


def _astral_agent_wake_url() -> str:
    """Private base url + wake path, or "" when no base url is set."""
    for env_key in ASTRAL_AGENT_CONFIG["base_url_envs"]:
        first = (os.environ.get(env_key) or "").split(",")[0].strip()
        if first:
            return first.rstrip("/") + ASTRAL_AGENT_CONFIG["wake_path"]
    return ""


def _row_failure(job_id: str, row: Any) -> AstralAgentError:
    status = row["status"]
    error_class = (row["error_class"] or "").strip()
    detail = f"job {job_id} {status} ({error_class or 'unknown'}): {row['error'] or ''}"
    if status == "cancelled" or error_class == "cancelled":
        failure_class = "astral_agent_cancelled"
    elif error_class in ("timeout", "expired"):
        failure_class = "astral_agent_timeout"
    elif error_class and error_class not in _PASSTHROUGH_SKIP:
        failure_class = error_class
    else:
        failure_class = "astral_agent_job_failed"
    return AstralAgentError(failure_class, detail)


class _LoopState:
    """Everything bound to one event loop: pool, listener, waiters, poller."""

    def __init__(self) -> None:
        self.db: Optional[asyncpg.Pool] = None
        self.listener: Optional[asyncpg.Connection] = None
        self.waiters: Dict[str, asyncio.Future] = {}
        self.wake = asyncio.Event()
        self.poller: Optional[asyncio.Task] = None
        self.init_lock = asyncio.Lock()
        self.wake_tasks: set = set()


class _AstralAgentQueue:
    """Enqueue a provider job and await its result.

    One shared poller per event loop resolves every waiting caller with a single
    query; LISTEN agent_job_done only wakes it early, so a dropped notification
    costs at most poll_interval_seconds, never a lost result.

    State is kept per event loop so asyncpg connections, Events, and Futures
    never cross loops.
    """

    def __init__(self) -> None:
        self._states: Dict[asyncio.AbstractEventLoop, _LoopState] = {}
        self._states_lock = threading.Lock()
        # Serverless wake throttle — process-wide, shared across loops/threads.
        self._last_wake = float("-inf")
        self._wake_lock = threading.Lock()

    def _dsn(self) -> str:
        env_key = ASTRAL_AGENT_CONFIG["database_url_env"]
        try:
            raw = os.environ[env_key]
        except KeyError:
            raise AstralAgentError("connectivity_failure", f"{env_key} not set") from None
        dsn = raw.strip()
        if not dsn:
            raise AstralAgentError("connectivity_failure", f"{env_key} not set")
        return dsn

    def _state(self) -> _LoopState:
        loop = asyncio.get_running_loop()
        with self._states_lock:
            st = self._states.get(loop)
            if st is None:
                for old in [lp for lp in self._states if lp.is_closed()]:
                    del self._states[old]
                st = self._states[loop] = _LoopState()
            return st

    async def _get_db(self) -> asyncpg.Pool:
        st = self._state()
        async with st.init_lock:
            if st.db is None:
                try:
                    st.db = await asyncpg.create_pool(
                        self._dsn(),
                        min_size=1,
                        max_size=int(ASTRAL_AGENT_CONFIG["db_pool_max_size"]),
                    )
                except AstralAgentError:
                    raise
                except Exception as e:
                    raise AstralAgentError(
                        "connectivity_failure", f"astral_agent queue db: {e}"
                    ) from e
            if st.poller is None or st.poller.done():
                st.poller = asyncio.create_task(
                    self._poll_loop(st), name="astral-agent-result-poller"
                )
        return st.db

    async def _ensure_listener(self, st: _LoopState) -> None:
        if st.listener is not None and not st.listener.is_closed():
            return
        try:
            st.listener = await asyncpg.connect(self._dsn())
            await st.listener.add_listener(_CHANNEL_DONE, lambda *_a: st.wake.set())
        except Exception as e:
            st.listener = None
            _log.warning("astral_agent result listener unavailable (polling only): %s", e)

    async def _poll_loop(self, st: _LoopState) -> None:
        interval = float(ASTRAL_AGENT_CONFIG["poll_interval_seconds"])
        while True:
            try:
                try:
                    await asyncio.wait_for(st.wake.wait(), timeout=interval)
                except asyncio.TimeoutError:
                    pass
                st.wake.clear()
                ids = [i for i, f in st.waiters.items() if not f.done()]
                if not ids:
                    continue
                await self._ensure_listener(st)
                rows = await st.db.fetch(
                    f"""
                    SELECT id, status, result, error, error_class FROM {_JOB_TABLE}
                    WHERE id = ANY($1::uuid[]) AND status = ANY($2::text[])
                    """,
                    ids,
                    list(_TERMINAL),
                )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                _log.warning("astral_agent result poll failed: %s: %s", type(e).__name__, e)
                await asyncio.sleep(interval)
                continue
            for row in rows:
                fut = st.waiters.get(str(row["id"]))
                if fut is not None and not fut.done():
                    fut.set_result(row)

    async def aclose_current_loop(self) -> None:
        """Cancel this loop's poller and close its listener/db pool. Call before the loop closes."""
        with self._states_lock:
            st = self._states.pop(asyncio.get_running_loop(), None)
        if st is None:
            return
        if st.poller is not None and not st.poller.done():
            st.poller.cancel()
            await asyncio.gather(st.poller, return_exceptions=True)
        for t in list(st.wake_tasks):
            t.cancel()
        if st.listener is not None and not st.listener.is_closed():
            try:
                await st.listener.close()
            except Exception:
                pass
        if st.db is not None:
            try:
                await st.db.close()
            except Exception:
                pass

    async def submit(
        self, request: Dict[str, Any], *, priority: Optional[int] = None
    ) -> dict:
        """Enqueue one provider job and wait for its result dict (or raise AstralAgentError)."""
        require_controlled_external_io("astral_agent.submit")
        db = await self._get_db()
        st = self._state()
        deadline = float(ASTRAL_AGENT_CONFIG["job_deadline_seconds"])
        job_id = str(uuid.uuid4())
        _log.debug("Calling astral_agent job %s", job_id)
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        st.waiters[job_id] = fut
        try:
            try:
                async with db.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(
                            f"""
                            INSERT INTO {_JOB_TABLE}
                                (id, request, priority, max_attempts, expires_at)
                            VALUES ($1, $2::jsonb, $3, $4,
                                    now() + make_interval(secs => $5))
                            """,
                            job_id,
                            json.dumps(request),
                            int(
                                ASTRAL_AGENT_CONFIG["default_priority"]
                                if priority is None
                                else priority
                            ),
                            int(ASTRAL_AGENT_CONFIG["max_attempts"]),
                            deadline,
                        )
                        await conn.execute("SELECT pg_notify($1, '')", _CHANNEL_NEW)
                await self._maybe_wake(db, st)
            except asyncpg.UndefinedTableError as e:
                raise AstralAgentError(
                    "connectivity_failure",
                    f"{_JOB_TABLE} missing — has the astral-agent worker ever started? {e}",
                ) from e
            except AstralAgentError:
                raise
            except Exception as e:
                raise AstralAgentError(
                    "connectivity_failure", f"astral_agent enqueue failed: {e}"
                ) from e
            try:
                row = await asyncio.wait_for(asyncio.shield(fut), timeout=deadline)
            except asyncio.TimeoutError:
                await self._cancel(db, job_id)
                _log.warning(
                    "%s | astral_agent job cancelled: deadline %ss exceeded",
                    job_id[:8],
                    deadline,
                )
                raise AstralAgentError(
                    "astral_agent_timeout", f"job {job_id} exceeded {deadline}s"
                ) from None
            except asyncio.CancelledError:
                await asyncio.shield(self._cancel(db, job_id))
                raise
        finally:
            st.waiters.pop(job_id, None)
        if row["status"] == "done":
            data = _decode_result(row["result"])
            bits = [
                f"{key}={request.get(key)}"
                for key in ("provider", "model", "task_key")
                if request.get(key)
            ]
            _log.info(
                "%s | astral_agent job done: %s",
                job_id[:8],
                " ".join(bits) or "(no provider/model/task_key)",
            )
            return data
        raise _row_failure(job_id, row)

    async def _cancel(self, db: Any, job_id: str) -> None:
        """Best effort: stop a worker spending provider time on a result nobody wants."""
        try:
            await db.execute(
                f"""
                UPDATE {_JOB_TABLE}
                SET status = 'cancelled', error_class = 'cancelled',
                    error = 'caller gave up', finished_at = now()
                WHERE id = $1 AND status IN ('queued', 'running')
                """,
                job_id,
            )
        except Exception as e:
            _log.warning("astral_agent cancel job=%s failed: %s", job_id, e)

    async def _live_workers(self, db: Any) -> int:
        return int(
            await db.fetchval(
                f"""
                SELECT count(*) FROM {_WORKER_TABLE}
                WHERE last_seen > now() - make_interval(secs => $1)
                """,
                float(ASTRAL_AGENT_CONFIG["worker_stale_seconds"]),
            )
            or 0
        )

    async def _maybe_wake(self, db: Any, st: _LoopState) -> None:
        """Throttled fire-and-forget GET /wake when no astral-agent worker is live."""
        url = _astral_agent_wake_url()
        throttle = float(ASTRAL_AGENT_CONFIG["wake_throttle_seconds"])
        with self._wake_lock:
            if time.monotonic() - self._last_wake < throttle:
                return
        try:
            if await self._live_workers(db):
                return
        except Exception as e:
            _log.debug("astral_agent wake check failed, pinging anyway: %s", e)
        with self._wake_lock:
            if time.monotonic() - self._last_wake < throttle:
                return
            self._last_wake = time.monotonic()
        if not url:
            _log.warning(
                "astral_agent wake skipped: no live worker and %s is not set; "
                "queued jobs wait until a worker starts",
                " / ".join(ASTRAL_AGENT_CONFIG["base_url_envs"]),
            )
            return
        task = asyncio.create_task(self._ping_wake(url))
        st.wake_tasks.add(task)
        task.add_done_callback(st.wake_tasks.discard)

    async def _ping_wake(self, url: str) -> None:
        """GET /wake on every replica — one request wakes only the replica it lands on."""
        targets = await _wake_targets(url)
        _log.debug("Calling astral_agent wake: %s replica(s) %s", len(targets), targets)
        await asyncio.gather(*[self._ping_one(t) for t in targets])

    async def _ping_one(self, url: str) -> None:
        try:
            async with httpx.AsyncClient(
                timeout=float(ASTRAL_AGENT_CONFIG["wake_timeout_seconds"])
            ) as client:
                resp = await client.get(url)
            _log.debug(
                "Response from astral_agent wake: %s %s %s",
                url,
                resp.status_code,
                resp.text[:200],
            )
        except Exception as e:
            _log.debug(
                "Response from astral_agent wake: %s %s: %s", url, type(e).__name__, e
            )

    async def healthy(self) -> bool:
        """Queue reachable. Does not wake astral-agent — only an enqueue does."""
        await self._get_db()
        return True


async def _wake_targets(url: str) -> List[str]:
    """One wake URL per replica address behind the private hostname.

    Railway's private DNS returns every replica's address; a request to the name hits
    just one. Prefers IPv4 when present, else IPv6. Falls back to the original URL
    when resolution fails or there is one address.
    """
    parts = urlsplit(url)
    host = parts.hostname or ""
    port = parts.port or (443 if parts.scheme == "https" else 80)
    try:
        infos = await asyncio.get_running_loop().getaddrinfo(
            host, port, type=socket.SOCK_STREAM
        )
    except Exception as e:
        _log.debug("astral_agent wake: resolving %s failed, pinging the name: %s", host, e)
        return [url]
    v4 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET})
    v6 = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET6})
    addrs = v4 or v6
    if len(addrs) <= 1:
        return [url]
    return [
        urlunsplit((
            parts.scheme,
            f"[{a}]:{port}" if ":" in a else f"{a}:{port}",
            parts.path,
            parts.query,
            "",
        ))
        for a in addrs
    ]


_pool = _AstralAgentQueue()


async def submit(request: Dict[str, Any], *, priority: Optional[int] = None) -> dict:
    """Enqueue one provider job and await its result dict (or raise AstralAgentError)."""
    return await _pool.submit(request, priority=priority)


async def close_loop_resources() -> None:
    """Release astral-agent queue resources bound to the running event loop."""
    await _pool.aclose_current_loop()


def run_one_shot(coro: Awaitable[Any]) -> Any:
    """asyncio.run for one-shot callers: releases this loop's queue state before the loop closes."""
    async def _main() -> Any:
        try:
            return await coro
        finally:
            await close_loop_resources()
    return asyncio.run(_main())
