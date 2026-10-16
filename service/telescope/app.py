"""Astral Telescope — Postgres queue consumer driving one Firefox per process.

No scrape HTTP API: the platform enqueues jobs in telescope_job and waits for results
(see jobqueue.py). HTTP serves only /healthz and /wake.

Serverless: after IDLE_SLEEP_SECONDS with nothing queued, running or in flight, the
process drops its Postgres connections and Firefox. With no outbound traffic, Railway
puts the container to sleep. The platform wakes it with GET /wake when it enqueues.
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import jobqueue
from browser import Firefox
from logging_util import configure_logging, get_logger, worker_label
from settings import settings
from worker import QueueWorker

configure_logging()
_log = get_logger(__name__)

_IDLE_CHECK_SECONDS = 15.0


class Runtime:
    """Postgres pool + Firefox + queue worker, which can sleep and wake together."""

    def __init__(self) -> None:
        self.db: Optional[asyncpg.Pool] = None
        self.firefox: Optional[Firefox] = None
        self.worker: Optional[QueueWorker] = None
        self.asleep = False
        self._lock = asyncio.Lock()
        self._idle_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        async with self._lock:
            await self._start_locked()
        self._idle_task = asyncio.create_task(self._idle_loop(), name="telescope-idle")

    async def close(self) -> None:
        if self._idle_task is not None:
            self._idle_task.cancel()
            await asyncio.gather(self._idle_task, return_exceptions=True)
        async with self._lock:
            if not self.asleep:
                await self._stop_locked()

    async def wake(self) -> bool:
        """Resume if asleep. Returns True when this call woke the process."""
        async with self._lock:
            if not self.asleep:
                return False
            _log.info("%s | telescope waking", worker_label())
            await self._start_locked()
            return True

    async def _start_locked(self) -> None:
        self.db = await jobqueue.create_pool(
            settings.database_url, max_size=settings.db_pool_max_size
        )
        await jobqueue.ensure_schema(self.db)
        self.firefox = Firefox()
        self.worker = QueueWorker(self.db, self.firefox)  # sets the worker label before Firefox logs
        await self.firefox.start()
        await self.worker.start()
        self.asleep = False

    async def _stop_locked(self) -> None:
        if self.worker is not None:
            await self.worker.stop()
        if self.firefox is not None:
            await self.firefox.stop()
        if self.db is not None:
            await self.db.close()
        self.db = self.firefox = self.worker = None

    async def _idle_loop(self) -> None:
        while True:
            await asyncio.sleep(_IDLE_CHECK_SECONDS)
            try:
                await self._maybe_sleep()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log.warning(
                    "%s | telescope idle check failed: %s: %s",
                    worker_label(),
                    type(exc).__name__,
                    exc,
                )

    async def _maybe_sleep(self) -> None:
        async with self._lock:
            if self.asleep or self.worker is None or self.db is None:
                return
            idle = self.worker.idle_seconds()
            if idle < settings.idle_sleep_seconds:
                return
            if await jobqueue.has_pending(self.db):
                return  # retries waiting on backoff, or another replica's work
            await self.worker.stop()  # also deletes our telescope_worker row
            # Race guard: the platform inserts a job, then checks for a live worker
            # before pinging /wake. We delete our worker row, then check the queue.
            # Whichever side goes second sees the other, so no job is stranded.
            if await jobqueue.has_pending(self.db):
                _log.info(
                    "%s | telescope staying awake: work arrived while going to sleep",
                    worker_label(),
                )
                self.worker = QueueWorker(self.db, self.firefox)
                await self.worker.start()
                return
            await self.firefox.stop()
            await self.db.close()
            self.db = self.firefox = self.worker = None
            self.asleep = True
            _log.info(
                "%s | telescope sleeping: idle %ds, Postgres and Firefox closed until GET /wake",
                worker_label(),
                round(idle),
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    if not settings.database_url:
        raise RuntimeError("ASTRAL_DATABASE_URL is required")
    runtime = Runtime()
    await runtime.start()
    app.state.runtime = runtime
    try:
        yield
    finally:
        await runtime.close()


app = FastAPI(title="Astral Telescope", lifespan=lifespan)


@app.get("/wake")
async def wake(request: Request):
    runtime: Runtime = request.app.state.runtime
    try:
        woke = await runtime.wake()
    except Exception as exc:
        _log.exception(
            "%s | telescope wake failed: %s: %s", worker_label(), type(exc).__name__, exc
        )
        return JSONResponse(status_code=503, content={"status": "wake_failed"})
    return {"status": "awake", "woke": woke}


@app.get("/healthz")
async def healthz(request: Request):
    runtime: Runtime = request.app.state.runtime
    if runtime.asleep:
        return {"status": "asleep"}  # healthy by design; /wake resumes it
    worker = runtime.worker
    firefox = runtime.firefox
    # The claim loop wakes at least every queue_poll_seconds; a long silence means it's stuck.
    loop_age_s = time.monotonic() - worker.last_loop_at
    loop_ok = loop_age_s < max(30.0, settings.queue_poll_seconds * 10)
    try:
        browser_ok = await firefox.health_poke()
    except Exception as exc:
        _log.exception("healthz browser poke failed\n  %s: %s", type(exc).__name__, exc)
        browser_ok = False
    body = {
        "status": "ok" if (loop_ok and browser_ok and worker.db_ok) else "unhealthy",
        "worker_id": worker.worker_id,
        "in_flight": worker.in_flight,
        "db_ok": worker.db_ok,
        "browser_ok": browser_ok,
        "claim_loop_age_s": round(loop_age_s, 1),
    }
    if body["status"] != "ok":
        _log.warning("healthz unhealthy %s", body)
        return JSONResponse(status_code=503, content=body)
    return body
