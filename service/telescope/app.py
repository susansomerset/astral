"""Astral Telescope FastAPI entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from auth import require_bearer
from logging_util import configure_logging
from settings import settings

configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Bearer required before serving; browser pool lands in Stage 2.
    if not settings.bearer_token:
        raise RuntimeError("TELESCOPE_BEARER_TOKEN is required")
    yield


app = FastAPI(title="Astral Telescope", lifespan=lifespan)


@app.get("/healthz", dependencies=[Depends(require_bearer)])
async def healthz() -> dict:
    # Stage 1 stub — Stage 2 replaces with a live browser poke.
    return {"status": "starting"}
