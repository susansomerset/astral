"""Queue consumer — claims every claimable job into a holding area; the gate starts them.

Every held job (waiting or running) stays leased and heartbeated, so a crash re-queues
it and shutdown hands it back. The gate decides when a waiting job starts; every claim
and every finish wakes it. Wake-ups come from LISTEN agent_job_new; polling every
QUEUE_POLL_SECONDS is the backstop. Every DB call is wrapped: a Postgres blip slows the
worker down, it never kills it. No entity / dispatch / platform SQLite awareness.
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
from gate import AdmitAll, Gate
from logging_util import get_logger, set_worker_label
from providers.errors import ProviderJobError
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
        gate: Optional[Gate] = None,
    ) -> None:
        self._db = db
        self.worker_id = worker_id or make_worker_id()
        self._gate: Gate = gate or AdmitAll()
        # Holding area: claimed + leased, not started (insertion order = claim order).
        self._waiting: Dict[str, jobqueue.ClaimedJob] = {}
        self._running: Dict[str, asyncio.Task] = {}
        self._wake = asyncio.Event()  # claim loop: new work may be queued
        self._gate_wake = asyncio.Event()  # gate loop: a claim, a finish, or a closing
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
            asyncio.create_task(self._gate_loop(), name="astral-agent-gate"),
            asyncio.create_task(self._heartbeat_loop(), name="astral-agent-heartbeat"),
            asyncio.create_task(
                self._maintenance_loop(), name="astral-agent-maintenance"
            ),
        ]
        _log.info(
            "%s | astral-agent worker started: worker_id:%s",
            self.label,
            self.worker_id,
        )

    async def stop(self) -> None:
        """Stop claiming and admitting, let running jobs finish (bounded), hand back the rest
        (including every job still waiting in the holding area)."""
        self._stopping.set()
        self._wake.set()
        self._gate_wake.set()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        draining = len(self._running)
        if draining or self._waiting:
            _log.info(
                "%s | astral-agent worker draining: running:%d waiting:%d grace:%ss",
                self.label,
                draining,
                len(self._waiting),
                settings.shutdown_grace_seconds,
            )
        if draining:
            await asyncio.wait(
                list(self._running.values()),
                timeout=settings.shutdown_grace_seconds,
            )
        leftovers = list(self._running.values())
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
        self._waiting.clear()
        await self._close_listener()

    @property
    def in_flight(self) -> int:
        """Jobs running now."""
        return len(self._running)

    @property
    def held(self) -> int:
        """Jobs claimed and leased by this worker: waiting + running."""
        return len(self._waiting) + len(self._running)

    def idle_seconds(self) -> float:
        if self.held:
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
            try:
                # No limit: everything claimable goes into the holding area.
                jobs = await jobqueue.claim(
                    self._db,
                    limit=None,
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
                self._waiting[job.id] = job
            if jobs:
                self._gate_wake.set()
            try:
                await asyncio.wait_for(
                    self._wake.wait(), timeout=settings.queue_poll_seconds
                )
            except asyncio.TimeoutError:
                pass

    async def _gate_loop(self) -> None:
        """Start waiting jobs, oldest first, for as long as the gate admits."""
        while not self._stopping.is_set():
            self._gate_wake.clear()
            wait: Optional[float] = None
            try:
                while self._waiting and self._gate.admit(len(self._running)):
                    self._start(next(iter(self._waiting)))
                if self._waiting:
                    wait = settings.admit_interval_seconds  # gate said not yet
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.warning("astral-agent gate failed: %s: %s", type(exc).__name__, exc)
                wait = settings.queue_poll_seconds  # jobs stay held; try again
            try:
                await asyncio.wait_for(self._gate_wake.wait(), timeout=wait)
            except asyncio.TimeoutError:
                pass

    def _start(self, job_id: str) -> None:
        job = self._waiting.pop(job_id)
        task = asyncio.create_task(self._run_job(job), name=f"job-{job_id}")
        self._running[job_id] = task
        task.add_done_callback(lambda _t, jid=job_id: self._job_done(jid))

    def _job_done(self, job_id: str) -> None:
        self._running.pop(job_id, None)
        self.last_busy_at = time.monotonic()
        self._gate_wake.set()  # a finish may open the gate

    async def _heartbeat_loop(self) -> None:
        while not self._stopping.is_set():
            try:
                # Every held job keeps its lease, started or not.
                checked = [*self._waiting, *self._running]
                alive = await jobqueue.heartbeat(
                    self._db,
                    worker_id=self.worker_id,
                    job_ids=checked,
                    lease_seconds=settings.lease_seconds,
                    held=len(checked),
                    running=len(self._running),
                )
                self.db_ok = True
                for job_id in checked:
                    if job_id in alive:
                        continue
                    task = self._running.get(job_id)
                    dropped = self._waiting.pop(job_id, None) is not None  # never started
                    if not dropped and (task is None or task.done()):
                        continue
                    _log.warning(
                        "%s | astral-agent job cancelled: caller gave up or lease lost",
                        _short_id(job_id),
                        extra={"job": _short_id(job_id)},
                    )
                    if not dropped and task is not None:
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
        if not any(stats.values()) and not self.held:
            return
        _log.info(
            "%s | astral-agent stats: held:%d (waiting:%d running:%d) done:%d failed:%d (%ds)",
            self.label,
            self.held,
            len(self._waiting),
            len(self._running),
            stats["done"],
            stats["failed"],
            round(window),
        )

    async def _run_job(self, job: jobqueue.ClaimedJob) -> None:
        raw = job.request if isinstance(job.request, dict) else {}
        # The gate admitted us: charge the attempt now (claim charges nothing).
        if await self._db_write(jobqueue.start, job_id=job.id, worker_id=self.worker_id) is None:
            _log.warning(
                "%s | astral-agent job not started: no longer ours", _short_id(job.id)
            )
            return
        started = time.monotonic()
        held_s = started - job.claimed_at  # claim -> start
        _log.debug("Started job %s (held %.1fs, queued %.1fs)", job.id, held_s, job.wait_s)
        try:
            result = await executor.execute(raw)
        except asyncio.CancelledError:
            raise
        except ProviderJobError as exc:
            _log.error(
                "%s | astral-agent job rejected: %s %s",
                _short_id(job.id),
                exc.error_class,
                exc.detail,
            )
            status = await self._db_write(
                jobqueue.fail,
                job_id=job.id,
                worker_id=self.worker_id,
                error=exc.detail[:2000],
                error_class=exc.error_class,
                retry_in_seconds=None,
            )
            if status == "failed":
                self._stats["failed"] += 1
            return
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
                error_class="executor_error",
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
        if isinstance(result, dict) and result.get("success") is False:
            _log.warning(
                "%s | astral-agent provider soft-fail: %s %s",
                _short_id(job.id),
                result.get("failure_class") or "-",
                str(result.get("error") or "")[:200],
            )
        self._stats["done"] += 1
        _log.info(
            "%s | astral-agent job done: server:%s model:%s elapsed:%.1fs wait:%.1fs queued:%.1fs",
            _short_id(job.id),
            raw.get("server_id") or "-",
            raw.get("model") or "-",
            time.monotonic() - started,
            held_s,
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
