"""Queue consumer — claims jobs up to WORKER_CONCURRENCY and runs each in its own Firefox context.

Wake-ups come from LISTEN telescope_job_new; polling every QUEUE_POLL_SECONDS is the
backstop (missed notifies, retry back-offs coming due, a dropped listener connection).
Every DB call is wrapped: a Postgres blip slows the worker down, it never kills it.
"""

from __future__ import annotations

import asyncio
import os
import socket
import time
import uuid
from typing import Any, Dict, Optional

import asyncpg

import jobqueue
from browser import Firefox
from logging_util import get_logger, set_worker_label
from scrape import ScrapeError, parse_request, run_scrape
from joblog import begin_job, end_job, short_id
from settings import settings

_log = get_logger(__name__)

_DB_RETRY_MAX_SECONDS = 30.0
_STATS_SECONDS = 60.0


def _first_line(text: str) -> str:
    return (text or "").strip().splitlines()[0] if (text or "").strip() else "-"


def make_worker_id() -> str:
    replica = os.environ.get("RAILWAY_REPLICA_ID") or socket.gethostname()
    return f"{replica}:{os.getpid()}:{uuid.uuid4().hex[:6]}"


class QueueWorker:
    def __init__(
        self,
        db: asyncpg.Pool,
        firefox: Firefox,
        *,
        worker_id: Optional[str] = None,
        concurrency: Optional[int] = None,
    ) -> None:
        self._db = db
        self._firefox = firefox
        self.worker_id = worker_id or make_worker_id()
        self._concurrency = concurrency or settings.worker_concurrency
        self._in_flight: Dict[str, asyncio.Task] = {}
        self._job_urls: Dict[str, str] = {}  # for lines logged outside the job's own task
        self._wake = asyncio.Event()
        self._stopping = asyncio.Event()
        self._listener: Optional[asyncpg.Connection] = None
        self._tasks: list[asyncio.Task] = []
        self.last_loop_at = time.monotonic()
        self.last_busy_at = time.monotonic()
        self.db_ok = False
        # Short replica label on every log line; worker_id stays unique per process.
        self.label = self.worker_id.split(":")[0][:8]
        set_worker_label(self.label)
        self._stats = {"done": 0, "retried": 0, "failed": 0}
        self._stats_at = time.monotonic()

    # -- lifecycle ---------------------------------------------------------

    async def start(self) -> None:
        await self._connect_listener()
        self._tasks = [
            asyncio.create_task(self._claim_loop(), name="telescope-claim"),
            asyncio.create_task(self._heartbeat_loop(), name="telescope-heartbeat"),
            asyncio.create_task(self._maintenance_loop(), name="telescope-maintenance"),
        ]
        _log.info(
            "%s | telescope worker started: concurrency:%d worker_id:%s",
            self.label,
            self._concurrency,
            self.worker_id,
        )

    async def stop(self) -> None:
        """Stop claiming, let in-flight scrapes finish (bounded), hand back the rest."""
        self._stopping.set()
        self._wake.set()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        draining = len(self._in_flight)
        if draining:
            _log.info(
                "%s | telescope worker draining: in_flight:%d grace:%ss",
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
                "%s | telescope worker stopped: finished:%d handed_back:%d",
                self.label,
                draining - len(leftovers),
                released,
            )
        except Exception as exc:
            # Leases expire and maintenance re-queues them — nothing is lost.
            _log.warning(
                "%s | telescope worker stopped: hand-back failed, leases will expire (%s: %s)",
                self.label,
                type(exc).__name__,
                exc,
            )
        await self._close_listener()

    @property
    def in_flight(self) -> int:
        return len(self._in_flight)

    def idle_seconds(self) -> float:
        """How long this worker has had nothing in flight (0 while busy)."""
        if self._in_flight:
            return 0.0
        return time.monotonic() - self.last_busy_at

    # -- listener ------------------------------------------------------------

    def _on_notify(self, *_args: Any) -> None:
        self._wake.set()

    async def _connect_listener(self) -> None:
        try:
            self._listener = await asyncpg.connect(settings.database_url)
            await self._listener.add_listener(jobqueue.CHANNEL_NEW, self._on_notify)
        except Exception as exc:
            self._listener = None
            _log.warning(
                "telescope listener connect failed, polling only: %s: %s",
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

    # -- loops ---------------------------------------------------------------

    async def _claim_loop(self) -> None:
        backoff = 1.0
        while not self._stopping.is_set():
            self.last_loop_at = time.monotonic()
            # Clear before claiming: anything that fires from here on (notify, a job
            # finishing) re-arms the wait below, so no wake-up is lost or spun on.
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
                        "telescope claim failed retry_in_s=%s: %s: %s",
                        backoff,
                        type(exc).__name__,
                        exc,
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, _DB_RETRY_MAX_SECONDS)
                    continue
                for job in jobs:
                    raw = job.request if isinstance(job.request, dict) else {}
                    self._job_urls[job.id] = str(raw.get("url") or "")
                    task = asyncio.create_task(self._run_job(job), name=f"job-{job.id}")
                    self._in_flight[job.id] = task
                    task.add_done_callback(lambda _t, jid=job.id: self._job_done(jid))
                claimed = len(jobs)
            if claimed and claimed == free:
                continue  # we were full-up on claims; there may be more ready
            try:
                await asyncio.wait_for(
                    self._wake.wait(), timeout=settings.queue_poll_seconds
                )
            except asyncio.TimeoutError:
                pass

    def _job_done(self, job_id: str) -> None:
        self._in_flight.pop(job_id, None)
        self._job_urls.pop(job_id, None)
        self.last_busy_at = time.monotonic()
        self._wake.set()  # a slot freed up

    async def _heartbeat_loop(self) -> None:
        while not self._stopping.is_set():
            try:
                # Judge only this snapshot — jobs claimed while the heartbeat awaits
                # weren't in the query and must not look "lost".
                checked = list(self._in_flight)
                alive = await jobqueue.heartbeat(
                    self._db,
                    worker_id=self.worker_id,
                    job_ids=checked,
                    lease_seconds=settings.lease_seconds,
                    concurrency=self._concurrency,
                )
                self.db_ok = True
                # Jobs we hold but the DB no longer gives us: cancelled or reaped.
                for job_id in checked:
                    task = self._in_flight.get(job_id)
                    if job_id not in alive and task is not None and not task.done():
                        url = self._job_urls.get(job_id, "")
                        _log.warning(
                            "%s | telescope job cancelled: %s caller gave up or lease lost",
                            short_id(job_id),
                            url or "-",
                            extra={"job": short_id(job_id), "url": url},
                        )
                        task.cancel()
                self._maybe_log_stats()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.db_ok = False
                _log.warning("telescope heartbeat failed: %s: %s", type(exc).__name__, exc)
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
                        "%s | telescope maintenance: reaped:%d (dead worker's jobs re-queued) expired:%d (never picked up)",
                        self.label,
                        counts["reaped"],
                        counts["expired"],
                    )
                if counts["pruned"]:
                    _log.debug("Pruned %d finished jobs", counts["pruned"])
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.warning("telescope maintenance failed: %s: %s", type(exc).__name__, exc)
            await asyncio.sleep(settings.maintenance_seconds)

    def _maybe_log_stats(self) -> None:
        """One line per replica per minute — only when it did something."""
        now = time.monotonic()
        if now - self._stats_at < _STATS_SECONDS:
            return
        window = now - self._stats_at
        stats, self._stats = self._stats, {"done": 0, "retried": 0, "failed": 0}
        self._stats_at = now
        if not any(stats.values()) and not self._in_flight:
            return
        firefox_id, served = self._firefox.status()
        _log.info(
            "%s | telescope stats: in_flight:%d/%d done:%d retried:%d failed:%d (%ds) firefox:%s served:%d",
            self.label,
            len(self._in_flight),
            self._concurrency,
            stats["done"],
            stats["retried"],
            stats["failed"],
            round(window),
            firefox_id,
            served,
        )

    # -- one job -------------------------------------------------------------

    def _retry_delay(self, job: jobqueue.ClaimedJob, error_class: str) -> Optional[float]:
        if error_class == "bad_request":
            return None
        if job.attempts >= job.max_attempts:
            return None
        if error_class == "timeout" and job.attempts >= settings.timeout_max_attempts:
            return None
        return settings.scrape_retry_base_delay_seconds * (2 ** (job.attempts - 1))

    async def _run_job(self, job: jobqueue.ClaimedJob) -> None:
        raw = job.request if isinstance(job.request, dict) else {}
        url = str(raw.get("url") or "")
        tokens = begin_job(
            job.id,
            attempt=job.attempts,
            max_attempts=job.max_attempts,
            debug=bool(raw.get("debug")),
            url=url,
        )
        started = time.monotonic()
        try:
            _log.debug("Claimed job %s: %s (waited %.1fs)", job.id, raw, job.wait_s)
            try:
                req, sel = parse_request(raw)
                result = await run_scrape(self._firefox, req, sel)
            except ScrapeError as exc:
                await self._record_failure(job, exc, url)
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.exception("%s | telescope job crashed: %s", short_id(job.id), url)
                await self._record_failure(
                    job, ScrapeError("scrape_failed", f"{type(exc).__name__}: {exc}"), url
                )
                return
            ours = await self._db_write(
                jobqueue.complete,
                job_id=job.id,
                worker_id=self.worker_id,
                result=result,
            )
            if not ours:
                _log.warning(
                    "%s | telescope job discarded: %s finished after it was cancelled or reaped",
                    short_id(job.id),
                    url,
                )
                return
            self._stats["done"] += 1
            _log.info(
                "%s | telescope job done: %s -> %s fields:%s scrape:%.1fs wait:%.1fs",
                short_id(job.id),
                url,
                result.get("final_url"),
                ",".join(req.fields),
                time.monotonic() - started,
                job.wait_s,
            )
        finally:
            end_job(tokens)

    async def _record_failure(
        self, job: jobqueue.ClaimedJob, exc: ScrapeError, url: str
    ) -> None:
        delay = self._retry_delay(job, exc.error_class)
        _log.debug("Attempt error detail: %s", exc)
        status = await self._db_write(
            jobqueue.fail,
            job_id=job.id,
            worker_id=self.worker_id,
            error=str(exc),
            error_class=exc.error_class,
            retry_in_seconds=delay,
        )
        if status == "queued":
            self._stats["retried"] += 1
            _log.warning(
                "%s | telescope job retry: %s %s attempt:%d/%d retry_in:%ss — %s",
                short_id(job.id),
                url,
                exc.error_class,
                job.attempts,
                job.max_attempts,
                delay,
                _first_line(str(exc)),
            )
        elif status == "failed":
            self._stats["failed"] += 1
            _log.error(
                "%s | telescope job failed: %s %s after attempt %d/%d — %s",
                short_id(job.id),
                url,
                exc.error_class,
                job.attempts,
                job.max_attempts,
                _first_line(str(exc)),
            )
        else:
            _log.warning(
                "%s | telescope job discarded: %s failed after it was cancelled or reaped (%s)",
                short_id(job.id),
                url,
                exc.error_class,
            )

    async def _db_write(self, fn, **kwargs: Any) -> Any:
        """Result writes retry through short DB blips; after that the lease expires
        and maintenance re-queues the job, so giving up here loses nothing."""
        delay = 0.5
        for attempt in range(5):
            try:
                return await fn(self._db, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.warning(
                    "telescope %s write failed attempt=%d: %s: %s",
                    fn.__name__,
                    attempt + 1,
                    type(exc).__name__,
                    exc,
                )
                await asyncio.sleep(delay)
                delay *= 2
        return None
