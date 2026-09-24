"""Queue consumer — claims jobs up to WORKER_CONCURRENCY and runs them on the pool.

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
from browser import BrowserPool
from logging_util import get_logger
from scrape import ScrapeError, parse_request, run_scrape
from scrape_debug import (
    begin_scrape_request,
    disable_scrape_debug,
    enable_scrape_debug,
    end_scrape_request,
    scrape_correlation_tag,
    scrape_debug_event,
)
from settings import settings

_log = get_logger(__name__)

_DB_RETRY_MAX_SECONDS = 30.0


def make_worker_id() -> str:
    replica = os.environ.get("RAILWAY_REPLICA_ID") or socket.gethostname()
    return f"{replica}:{os.getpid()}:{uuid.uuid4().hex[:6]}"


class QueueWorker:
    def __init__(
        self,
        db: asyncpg.Pool,
        browser_pool: BrowserPool,
        *,
        worker_id: Optional[str] = None,
        concurrency: Optional[int] = None,
    ) -> None:
        self._db = db
        self._browser_pool = browser_pool
        self.worker_id = worker_id or make_worker_id()
        self._concurrency = concurrency or settings.worker_concurrency
        self._in_flight: Dict[str, asyncio.Task] = {}
        self._wake = asyncio.Event()
        self._stopping = asyncio.Event()
        self._listener: Optional[asyncpg.Connection] = None
        self._tasks: list[asyncio.Task] = []
        self.last_loop_at = time.monotonic()
        self.db_ok = False

    # -- lifecycle ---------------------------------------------------------

    async def start(self) -> None:
        await self._connect_listener()
        self._tasks = [
            asyncio.create_task(self._claim_loop(), name="telescope-claim"),
            asyncio.create_task(self._heartbeat_loop(), name="telescope-heartbeat"),
            asyncio.create_task(self._maintenance_loop(), name="telescope-maintenance"),
        ]
        _log.info(
            "telescope worker started worker_id=%s concurrency=%d",
            self.worker_id,
            self._concurrency,
        )

    async def stop(self) -> None:
        """Stop claiming, let in-flight scrapes finish (bounded), hand back the rest."""
        self._stopping.set()
        self._wake.set()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        if self._in_flight:
            _log.info(
                "telescope worker draining in_flight=%d grace_s=%s",
                len(self._in_flight),
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
            _log.info("telescope worker stopped released=%d", released)
        except Exception as exc:
            # Leases expire and maintenance re-queues them — nothing is lost.
            _log.warning("telescope worker release failed: %s: %s", type(exc).__name__, exc)
        await self._close_listener()

    @property
    def in_flight(self) -> int:
        return len(self._in_flight)

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
                "telescope listener connect failed (polling only): %s: %s",
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
                        _log.info("telescope job %s no longer ours — cancelling", job_id)
                        task.cancel()
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
                if any(counts.values()):
                    _log.info(
                        "telescope maintenance expired=%d reaped=%d pruned=%d",
                        counts["expired"],
                        counts["reaped"],
                        counts["pruned"],
                    )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.warning("telescope maintenance failed: %s: %s", type(exc).__name__, exc)
            await asyncio.sleep(settings.maintenance_seconds)

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
        fields = raw.get("fields")
        request_id, scrape_tokens = begin_scrape_request(
            url, fields=list(fields) if isinstance(fields, list) else None
        )
        debug_token = enable_scrape_debug() if raw.get("debug") else None
        started = time.monotonic()
        try:
            scrape_debug_event("request_start", url=url, fields=fields, job_id=job.id)
            try:
                req, sel = parse_request(raw)
                result = await run_scrape(self._browser_pool, req, sel)
            except ScrapeError as exc:
                await self._record_failure(job, exc, url)
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.exception("telescope job=%s unexpected error", job.id)
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
            _log.info(
                "telescope ok %s job=%s attempt=%d/%d url=%s final_url=%s fields=%s elapsed_s=%.1f%s",
                scrape_correlation_tag(request_id=request_id),
                job.id,
                job.attempts,
                job.max_attempts,
                url,
                result.get("final_url"),
                req.fields,
                time.monotonic() - started,
                "" if ours else " (discarded: job no longer ours)",
            )
            scrape_debug_event("request_done", url=url, final_url=result.get("final_url"))
        finally:
            if debug_token is not None:
                disable_scrape_debug(debug_token)
            end_scrape_request(scrape_tokens)

    async def _record_failure(
        self, job: jobqueue.ClaimedJob, exc: ScrapeError, url: str
    ) -> None:
        delay = self._retry_delay(job, exc.error_class)
        status = await self._db_write(
            jobqueue.fail,
            job_id=job.id,
            worker_id=self.worker_id,
            error=str(exc),
            error_class=exc.error_class,
            retry_in_seconds=delay,
        )
        log = _log.warning if status == "queued" else _log.error
        log(
            "telescope %s job=%s attempt=%d/%d url=%s status=%s retry_in_s=%s\n  %s",
            exc.error_class,
            job.id,
            job.attempts,
            job.max_attempts,
            url,
            status,
            delay,
            exc,
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
