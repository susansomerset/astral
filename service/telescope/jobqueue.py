"""Postgres job queue — schema + every SQL statement the worker runs.

Contract mirror: src/external/telescope.py (_TelescopeQueue) inserts jobs and reads
results with the same table/column/channel names. Import fence forbids sharing code,
so change both sides together.

Lifecycle: queued → running → done | failed | cancelled.
  - Claim is FOR UPDATE SKIP LOCKED; attempts count claims (not failures), so a URL
    that crashes the worker still runs out of attempts.
  - A running job holds a lease the worker heartbeats; an expired lease means the
    worker died and the job is re-queued (or failed when out of attempts).
  - Result is zlib-compressed JSON in bytea — jsonb rejects NUL and lone surrogates,
    which scraped pages do contain.
"""

from __future__ import annotations

import json
import zlib
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence

import asyncpg

JOB_TABLE = "telescope_job"
WORKER_TABLE = "telescope_worker"
CHANNEL_NEW = "telescope_job_new"
CHANNEL_DONE = "telescope_job_done"

# Advisory lock key so concurrent replicas don't race CREATE TABLE IF NOT EXISTS.
_SCHEMA_LOCK_KEY = 0x7E1E5C09E

SCHEMA_SQL = f"""
CREATE TABLE IF NOT EXISTS {JOB_TABLE} (
    id           uuid PRIMARY KEY,
    status       text NOT NULL DEFAULT 'queued'
                 CHECK (status IN ('queued', 'running', 'done', 'failed', 'cancelled')),
    priority     smallint NOT NULL DEFAULT 0,
    request      jsonb NOT NULL,
    result       bytea,
    error        text,
    error_class  text,
    attempts     int NOT NULL DEFAULT 0,
    max_attempts int NOT NULL DEFAULT 4,
    run_after    timestamptz NOT NULL DEFAULT now(),
    expires_at   timestamptz NOT NULL,
    lease_until  timestamptz,
    worker_id    text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    started_at   timestamptz,
    finished_at  timestamptz
);
CREATE INDEX IF NOT EXISTS {JOB_TABLE}_ready_idx
    ON {JOB_TABLE} (priority DESC, created_at) WHERE status = 'queued';
CREATE INDEX IF NOT EXISTS {JOB_TABLE}_lease_idx
    ON {JOB_TABLE} (lease_until) WHERE status = 'running';
CREATE INDEX IF NOT EXISTS {JOB_TABLE}_finished_idx
    ON {JOB_TABLE} (finished_at) WHERE status IN ('done', 'failed', 'cancelled');

CREATE TABLE IF NOT EXISTS {WORKER_TABLE} (
    worker_id   text PRIMARY KEY,
    started_at  timestamptz NOT NULL DEFAULT now(),
    last_seen   timestamptz NOT NULL DEFAULT now(),
    concurrency int NOT NULL,
    in_flight   int NOT NULL DEFAULT 0
);
"""

_TERMINAL = ("done", "failed", "cancelled")


@dataclass(frozen=True)
class ClaimedJob:
    id: str
    request: dict
    attempts: int
    max_attempts: int
    wait_s: float = 0.0  # time since the job became claimable (queue wait)


def encode_result(result: Any) -> bytes:
    return zlib.compress(json.dumps(result).encode("utf-8"))


def decode_result(blob: Optional[bytes]) -> Any:
    if blob is None:
        return None
    return json.loads(zlib.decompress(blob).decode("utf-8"))


async def _init_connection(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


async def create_pool(dsn: str, *, max_size: int) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        dsn, min_size=1, max_size=max_size, init=_init_connection
    )


async def ensure_schema(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock($1)", _SCHEMA_LOCK_KEY)
            await conn.execute(SCHEMA_SQL)


async def claim(
    pool: asyncpg.Pool, *, limit: int, worker_id: str, lease_seconds: int
) -> List[ClaimedJob]:
    rows = await pool.fetch(
        f"""
        WITH picked AS (
            SELECT id FROM {JOB_TABLE}
            WHERE status = 'queued' AND run_after <= now() AND expires_at > now()
            ORDER BY priority DESC, created_at
            LIMIT $1
            FOR UPDATE SKIP LOCKED
        )
        UPDATE {JOB_TABLE} j
        SET status = 'running',
            attempts = j.attempts + 1,
            worker_id = $2,
            lease_until = now() + make_interval(secs => $3),
            started_at = now()
        FROM picked
        WHERE j.id = picked.id
        RETURNING j.id, j.request, j.attempts, j.max_attempts,
                  EXTRACT(EPOCH FROM now() - j.run_after)::float8 AS wait_s
        """,
        limit,
        worker_id,
        float(lease_seconds),
    )
    return [
        ClaimedJob(
            id=str(r["id"]),
            request=r["request"],
            attempts=r["attempts"],
            max_attempts=r["max_attempts"],
            wait_s=max(0.0, r["wait_s"] or 0.0),
        )
        for r in rows
    ]


async def complete(
    pool: asyncpg.Pool, *, job_id: str, worker_id: str, result: Any
) -> bool:
    """Store the result; False when the job is no longer ours (cancelled / lease lost)."""
    blob = encode_result(result)
    async with pool.acquire() as conn:
        async with conn.transaction():
            status = await conn.fetchval(
                f"""
                UPDATE {JOB_TABLE}
                SET status = 'done', result = $3, error = NULL, error_class = NULL,
                    lease_until = NULL, finished_at = now()
                WHERE id = $1 AND worker_id = $2 AND status = 'running'
                RETURNING status
                """,
                job_id,
                worker_id,
                blob,
            )
            if status is None:
                return False
            await conn.execute("SELECT pg_notify($1, $2)", CHANNEL_DONE, job_id)
    return True


async def fail(
    pool: asyncpg.Pool,
    *,
    job_id: str,
    worker_id: str,
    error: str,
    error_class: str,
    retry_in_seconds: Optional[float],
) -> Optional[str]:
    """Re-queue after retry_in_seconds, or fail terminally when it is None.

    Returns the new status, or None when the job is no longer ours.
    """
    async with pool.acquire() as conn:
        async with conn.transaction():
            status = await conn.fetchval(
                f"""
                UPDATE {JOB_TABLE}
                SET status = CASE WHEN $5::float8 IS NULL THEN 'failed' ELSE 'queued' END,
                    error = $3, error_class = $4,
                    worker_id = CASE WHEN $5::float8 IS NULL THEN worker_id END,
                    lease_until = NULL,
                    run_after = now() + make_interval(secs => COALESCE($5::float8, 0)),
                    finished_at = CASE WHEN $5::float8 IS NULL THEN now() END
                WHERE id = $1 AND worker_id = $2 AND status = 'running'
                RETURNING status
                """,
                job_id,
                worker_id,
                error[:2000],
                error_class,
                retry_in_seconds,
            )
            if status == "failed":
                await conn.execute("SELECT pg_notify($1, $2)", CHANNEL_DONE, job_id)
            elif status == "queued":
                await conn.execute("SELECT pg_notify($1, '')", CHANNEL_NEW)
    return status


async def heartbeat(
    pool: asyncpg.Pool,
    *,
    worker_id: str,
    job_ids: Sequence[str],
    lease_seconds: int,
    concurrency: int,
) -> set[str]:
    """Extend leases; return the ids still ours (missing ids were cancelled/reaped)."""
    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            INSERT INTO {WORKER_TABLE} (worker_id, concurrency, in_flight)
            VALUES ($1, $2, $3)
            ON CONFLICT (worker_id)
            DO UPDATE SET last_seen = now(), concurrency = $2, in_flight = $3
            """,
            worker_id,
            concurrency,
            len(job_ids),
        )
        if not job_ids:
            return set()
        rows = await conn.fetch(
            f"""
            UPDATE {JOB_TABLE}
            SET lease_until = now() + make_interval(secs => $3)
            WHERE id = ANY($2::uuid[]) AND worker_id = $1 AND status = 'running'
            RETURNING id
            """,
            worker_id,
            list(job_ids),
            float(lease_seconds),
        )
    return {str(r["id"]) for r in rows}


async def maintain(
    pool: asyncpg.Pool, *, retention_hours: int, worker_stale_seconds: int
) -> dict[str, int]:
    """Idempotent housekeeping — safe for every replica to run concurrently."""
    async with pool.acquire() as conn:
        expired = await conn.fetch(
            f"""
            UPDATE {JOB_TABLE}
            SET status = 'cancelled', error = 'expired before a worker picked it up',
                error_class = 'expired', finished_at = now()
            WHERE status = 'queued' AND expires_at <= now()
            RETURNING id
            """
        )
        reaped = await conn.fetch(
            f"""
            UPDATE {JOB_TABLE}
            SET status = CASE WHEN attempts >= max_attempts OR expires_at <= now()
                              THEN 'failed' ELSE 'queued' END,
                error = 'worker lost (lease expired)', error_class = 'lease_expired',
                worker_id = NULL, lease_until = NULL, run_after = now(),
                finished_at = CASE WHEN attempts >= max_attempts OR expires_at <= now()
                                   THEN now() END
            WHERE status = 'running' AND lease_until < now()
            RETURNING id, status
            """
        )
        for r in [*expired, *[r for r in reaped if r["status"] == "failed"]]:
            await conn.execute("SELECT pg_notify($1, $2)", CHANNEL_DONE, str(r["id"]))
        if any(r["status"] == "queued" for r in reaped):
            await conn.execute("SELECT pg_notify($1, '')", CHANNEL_NEW)
        pruned = await conn.execute(
            f"""
            DELETE FROM {JOB_TABLE}
            WHERE status IN {_TERMINAL!r}
              AND finished_at < now() - make_interval(hours => $1)
            """,
            retention_hours,
        )
        await conn.execute(
            f"DELETE FROM {WORKER_TABLE} "
            "WHERE last_seen < now() - make_interval(secs => $1)",
            float(worker_stale_seconds),
        )
    return {
        "expired": len(expired),
        "reaped": len(reaped),
        "pruned": int(pruned.split()[-1]),
    }


async def release_all(pool: asyncpg.Pool, *, worker_id: str) -> int:
    """Shutdown: hand unfinished jobs back without charging them an attempt."""
    rows = await pool.fetch(
        f"""
        UPDATE {JOB_TABLE}
        SET status = 'queued', attempts = GREATEST(attempts - 1, 0),
            worker_id = NULL, lease_until = NULL, run_after = now()
        WHERE worker_id = $1 AND status = 'running'
        RETURNING id
        """,
        worker_id,
    )
    await pool.execute(f"DELETE FROM {WORKER_TABLE} WHERE worker_id = $1", worker_id)
    if rows:
        await pool.execute("SELECT pg_notify($1, '')", CHANNEL_NEW)
    return len(rows)
