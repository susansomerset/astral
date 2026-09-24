"""Astral Telescope — Postgres queue consumer with a Firefox pool.

No scrape HTTP API: the platform enqueues jobs in telescope_job and waits for results
(see jobqueue.py). The HTTP server exists only for Railway's /healthz probe.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import jobqueue
from browser import BrowserPool
from logging_util import configure_logging, get_logger
from settings import settings
from worker import QueueWorker

configure_logging()
_log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    if not settings.database_url:
        raise RuntimeError("ASTRAL_DATABASE_URL is required")
    db = await jobqueue.create_pool(
        settings.database_url, max_size=settings.db_pool_max_size
    )
    await jobqueue.ensure_schema(db)
    pool = BrowserPool()
    await pool.start()
    worker = QueueWorker(db, pool)
    await worker.start()
    app.state.pool = pool
    app.state.worker = worker
    try:
        yield
    finally:
        await worker.stop()
        await pool.stop()
        await db.close()


app = FastAPI(title="Astral Telescope", lifespan=lifespan)


@app.get("/healthz")
async def healthz(request: Request):
    worker: QueueWorker = request.app.state.worker
    pool: BrowserPool = request.app.state.pool
    # The claim loop wakes at least every queue_poll_seconds; a long silence means it's stuck.
    loop_age_s = time.monotonic() - worker.last_loop_at
    loop_ok = loop_age_s < max(30.0, settings.queue_poll_seconds * 10)
    try:
        browser_ok = await pool.health_poke()
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
