"""Queue consumer — claims jobs up to WORKER_CONCURRENCY and runs the stub executor.

Wake-ups come from LISTEN agent_job_new; polling every QUEUE_POLL_SECONDS is the
backstop. Every DB call is wrapped: a Postgres blip slows the worker down, it never
kills it. No entity / dispatch / platform SQLite awareness.
"""

from __future__ import annotations

import asyncio
import os
import socket
import time
import uuid
from typing import Any, Dict, Optional

import asyncpg

import executor
import jobqueue
from logging_util import get_logger, set_worker_label
from settings import settings

_log = get_logger(__name__)

_DB_RETRY_MAX_SECONDS = 30.0
_STATS_SECONDS = 60.0


def _short_id(job_id: str) -> str:
    return job_id[:8] if job_id else "-"


def make_worker_id() -> str:
    replica = os.environ.get("RAILWAY_REPLICA_ID") or socket.gethostname()
    return f"{replica}:{os.getpid()}:{uuid.uuid4().hex[:6]}"


class QueueWorker:
    def __init__(
        self,
        db: asyncpg.Pool,
        *,
        worker_id: Optional[str] = None,
        concurrency: Optional[int] = None,
    ) -> None:
        self._db = db
        self.worker_id = worker_id or make_worker_id()
        self._concurrency = concurrency or settings.worker_concurrency
        self._in_flight: Dict[str, asyncio.Task] = {}
        self._wake = asyncio.Event()
        self._stopping = asyncio.Event()
        self._listener: Optional[asyncpg.Connection] = None
        self._tasks: list[asyncio.Task] = []
        self.last_loop_at = time.monotonic()
        self.last_busy_at = time.monotonic()
        self.db_ok = False
        self.label = self.worker_id.split(":")[0][:8]
        set_worker_label(self.label)
        self._stats = {"done": 0, "failed": 0}
        self._stats_at = time.monotonic()

    async def start(self) -> None:
        await self._connect_listener()
        self._tasks = [
            asyncio.create_task(self._claim_loop(), name="astral-agent-claim"),
            asyncio.create_task(self._heartbeat_loop(), name="astral-agent-heartbeat"),
            asyncio.create_task(
                self._maintenance_loop(), name="astral-agent-maintenance"
            ),
        ]
        _log.info(
            "%s | astral-agent worker started: concurrency:%d worker_id:%s",
            self.label,
            self._concurrency,
            self.worker_id,
        )

    async def stop(self) -> None:
        """Stop claiming, let in-flight jobs finish (bounded), hand back the rest."""
        self._stopping.set()
        self._wake.set()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        draining = len(self._in_flight)
        if draining:
            _log.info(
                "%s | astral-agent worker draining: in_flight:%d grace:%ss",
                self.label,
                draining,
                settings.shutdown_grace_seconds,
            )
            await asyncio.wait(
                list(self._in_flight.values()),
                timeout=settings.shutdown_grace_seconds,
            )
        leftovers = list(self._in_flight.values())
        for t in leftovers:
            t.cancel()
        await asyncio.gather(*leftovers, return_exceptions=True)
        try:
            released = await jobqueue.release_all(self._db, worker_id=self.worker_id)
            _log.info(
                "%s | astral-agent worker stopped: finished:%d handed_back:%d",
                self.label,
                draining - len(leftovers),
                released,
            )
        except Exception as exc:
            _log.warning(
                "%s | astral-agent worker stopped: hand-back failed, leases will expire (%s: %s)",
                self.label,
                type(exc).__name__,
                exc,
            )
        await self._close_listener()

    @property
    def in_flight(self) -> int:
        return len(self._in_flight)

    def idle_seconds(self) -> float:
        if self._in_flight:
            return 0.0
        return time.monotonic() - self.last_busy_at

    def _on_notify(self, *_args: Any) -> None:
        self._wake.set()

    async def _connect_listener(self) -> None:
        try:
            self._listener = await asyncpg.connect(settings.database_url)
            await self._listener.add_listener(jobqueue.CHANNEL_NEW, self._on_notify)
        except Exception as exc:
            self._listener = None
            _log.warning(
                "astral-agent listener connect failed, polling only: %s: %s",
                type(exc).__name__,
                exc,
            )

    async def _close_listener(self) -> None:
        if self._listener is not None:
            try:
                await self._listener.close(timeout=5)
            except Exception:
                pass
            self._listener = None

    async def _claim_loop(self) -> None:
        backoff = 1.0
        while not self._stopping.is_set():
            self.last_loop_at = time.monotonic()
            self._wake.clear()
            free = self._concurrency - len(self._in_flight)
            claimed = 0
            if free > 0:
                try:
                    jobs = await jobqueue.claim(
                        self._db,
                        limit=free,
                        worker_id=self.worker_id,
                        lease_seconds=settings.lease_seconds,
                    )
                    self.db_ok = True
                    backoff = 1.0
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self.db_ok = False
                    _log.warning(
                        "astral-agent claim failed retry_in_s=%s: %s: %s",
                        backoff,
                        type(exc).__name__,
                        exc,
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, _DB_RETRY_MAX_SECONDS)
                    continue
                for job in jobs:
                    task = asyncio.create_task(self._run_job(job), name=f"job-{job.id}")
                    self._in_flight[job.id] = task
                    task.add_done_callback(lambda _t, jid=job.id: self._job_done(jid))
                claimed = len(jobs)
            if claimed and claimed == free:
                continue
            try:
                await asyncio.wait_for(
                    self._wake.wait(), timeout=settings.queue_poll_seconds
                )
            except asyncio.TimeoutError:
                pass

    def _job_done(self, job_id: str) -> None:
        self._in_flight.pop(job_id, None)
        self.last_busy_at = time.monotonic()
        self._wake.set()

    async def _heartbeat_loop(self) -> None:
        while not self._stopping.is_set():
            try:
                checked = list(self._in_flight)
                alive = await jobqueue.heartbeat(
                    self._db,
                    worker_id=self.worker_id,
                    job_ids=checked,
                    lease_seconds=settings.lease_seconds,
                    concurrency=self._concurrency,
                )
                self.db_ok = True
                for job_id in checked:
                    task = self._in_flight.get(job_id)
                    if job_id not in alive and task is not None and not task.done():
                        _log.warning(
                            "%s | astral-agent job cancelled: caller gave up or lease lost",
                            _short_id(job_id),
                            extra={"job": _short_id(job_id)},
                        )
                        task.cancel()
                self._maybe_log_stats()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.db_ok = False
                _log.warning(
                    "astral-agent heartbeat failed: %s: %s", type(exc).__name__, exc
                )
            await asyncio.sleep(settings.heartbeat_seconds)

    async def _maintenance_loop(self) -> None:
        while not self._stopping.is_set():
            try:
                if self._listener is None or self._listener.is_closed():
                    await self._close_listener()
                    await self._connect_listener()
                counts = await jobqueue.maintain(
                    self._db,
                    retention_hours=settings.job_retention_hours,
                    worker_stale_seconds=settings.worker_stale_seconds,
                )
                if counts["expired"] or counts["reaped"]:
                    _log.warning(
                        "%s | astral-agent maintenance: reaped:%d expired:%d",
                        self.label,
                        counts["reaped"],
                        counts["expired"],
                    )
                if counts["pruned"]:
                    _log.debug("Pruned %d finished jobs", counts["pruned"])
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.warning(
                    "astral-agent maintenance failed: %s: %s", type(exc).__name__, exc
                )
            await asyncio.sleep(settings.maintenance_seconds)

    def _maybe_log_stats(self) -> None:
        now = time.monotonic()
        if now - self._stats_at < _STATS_SECONDS:
            return
        window = now - self._stats_at
        stats, self._stats = self._stats, {"done": 0, "failed": 0}
        self._stats_at = now
        if not any(stats.values()) and not self._in_flight:
            return
        _log.info(
            "%s | astral-agent stats: in_flight:%d/%d done:%d failed:%d (%ds)",
            self.label,
            len(self._in_flight),
            self._concurrency,
            stats["done"],
            stats["failed"],
            round(window),
        )

    async def _run_job(self, job: jobqueue.ClaimedJob) -> None:
        raw = job.request if isinstance(job.request, dict) else {}
        started = time.monotonic()
        _log.debug("Claimed job %s (waited %.1fs)", job.id, job.wait_s)
        try:
            result = await executor.execute(raw)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            _log.exception(
                "%s | astral-agent job crashed: %s: %s",
                _short_id(job.id),
                type(exc).__name__,
                exc,
            )
            status = await self._db_write(
                jobqueue.fail,
                job_id=job.id,
                worker_id=self.worker_id,
                error=str(exc)[:2000],
                error_class="stub_error",
                retry_in_seconds=None,
            )
            if status == "failed":
                self._stats["failed"] += 1
            return
        ours = await self._db_write(
            jobqueue.complete,
            job_id=job.id,
            worker_id=self.worker_id,
            result=result,
        )
        if not ours:
            _log.warning(
                "%s | astral-agent job discarded: finished after cancel or reap",
                _short_id(job.id),
            )
            return
        self._stats["done"] += 1
        _log.info(
            "%s | astral-agent job done: stub elapsed:%.1fs wait:%.1fs",
            _short_id(job.id),
            time.monotonic() - started,
            job.wait_s,
        )

    async def _db_write(self, fn, **kwargs: Any) -> Any:
        delay = 0.5
        for attempt in range(5):
            try:
                return await fn(self._db, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.warning(
                    "astral-agent %s write failed attempt=%d: %s: %s",
                    fn.__name__,
                    attempt + 1,
                    type(exc).__name__,
                    exc,
                )
                await asyncio.sleep(delay)
                delay *= 2
        return None
