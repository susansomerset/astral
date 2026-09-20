"""Astral Telescope FastAPI entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from auth import require_bearer
from browser import BrowserPool
from logging_util import configure_logging, get_logger
from settings import settings

configure_logging()
_log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    if not settings.bearer_token:
        raise RuntimeError("TELESCOPE_BEARER_TOKEN is required")
    pool = BrowserPool()
    await pool.start()
    app.state.pool = pool
    try:
        yield
    finally:
        await pool.stop()


app = FastAPI(title="Astral Telescope", lifespan=lifespan)


@app.get("/healthz", dependencies=[Depends(require_bearer)])
async def healthz(request: Request):
    pool: BrowserPool = request.app.state.pool
    try:
        ok = await pool.health_poke()
    except Exception as exc:
        _log.exception(
            "healthz browser poke failed\n  %s: %s",
            type(exc).__name__,
            exc,
        )
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
    if not ok:
        _log.warning("healthz browser disconnected after poke")
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
    return {"status": "ok"}
