"""Astral-agent settings — ASTRAL_DATABASE_URL from environ (required); tunables from agent_config."""

from __future__ import annotations

import os
from dataclasses import dataclass

from agent_config import (
    DB_POOL_MAX_SIZE,
    HEARTBEAT_SECONDS,
    IDLE_SLEEP_SECONDS,
    JOB_RETENTION_HOURS,
    LEASE_SECONDS,
    LOG_LEVEL,
    MAINTENANCE_SECONDS,
    PORT,
    QUEUE_POLL_SECONDS,
    SHUTDOWN_GRACE_SECONDS,
    WORKER_CONCURRENCY,
    WORKER_STALE_SECONDS,
)


@dataclass(frozen=True)
class Settings:
    database_url: str
    worker_concurrency: int
    queue_poll_seconds: float
    lease_seconds: int
    heartbeat_seconds: float
    maintenance_seconds: float
    job_retention_hours: int
    worker_stale_seconds: int
    shutdown_grace_seconds: float
    idle_sleep_seconds: float
    db_pool_max_size: int
    port: int
    log_level: str


def load_settings() -> Settings:
    # Secret/env-specific: required, no .get() fallback (astral.config.secrets-and-env-specific-from-environ).
    database_url = os.environ["ASTRAL_DATABASE_URL"].strip()
    if "ASTRAL_AGENT_IDLE_SLEEP_SECONDS" in os.environ:
        idle = float(os.environ["ASTRAL_AGENT_IDLE_SLEEP_SECONDS"])
    else:
        idle = float(IDLE_SLEEP_SECONDS)
    return Settings(
        database_url=database_url,
        worker_concurrency=WORKER_CONCURRENCY,
        queue_poll_seconds=QUEUE_POLL_SECONDS,
        lease_seconds=LEASE_SECONDS,
        heartbeat_seconds=HEARTBEAT_SECONDS,
        maintenance_seconds=MAINTENANCE_SECONDS,
        job_retention_hours=JOB_RETENTION_HOURS,
        worker_stale_seconds=WORKER_STALE_SECONDS,
        shutdown_grace_seconds=SHUTDOWN_GRACE_SECONDS,
        idle_sleep_seconds=idle,
        db_pool_max_size=DB_POOL_MAX_SIZE,
        port=PORT,
        log_level=(os.environ.get("ASTRAL_AGENT_LOG_LEVEL") or LOG_LEVEL).strip()
        or LOG_LEVEL,
    )


settings = load_settings()
