#!/usr/bin/env python3
"""Migrate historical agent_responses audit data into the agent_data framework.

Runs one task_key at a time. Designed to be called from the admin API endpoint
(background thread) or directly via CLI: python scripts/migrations/migrate_agent_data.py <task_key>

Steps:
  0. Backup tables (first run only, count-verified)
  1. Backfill dispatch_ledger inferable columns for matching batches
  2. Archive old-format company.agent_responses (company task_keys only, once)
  3. Populate agent_data blocks from agent_responses audit records
  4. Verify counts
"""

import hashlib
import json
import sqlite3
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config import ASTRAL_CONFIG, TASK_CONFIG, resolve_dispatch_task_config_key
from src.utils.logging import get_logger, log_batch_id, flush_log_buffer

logger = get_logger(__name__)

DB_PATH = ASTRAL_CONFIG["db_dir"] / "astral.db"
MIGRATION_DATE_CUTOFF = "2026-03-17"
CHARS_PER_TOKEN = 4
BACKUP_TABLES = ["company", "dispatch_ledger", "agent_responses", "anthropic_timesheets", "agent_timesheets"]

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _decompress(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bytes):
        return zlib.decompress(value).decode("utf-8")
    return value


def _make_agent_data_id(batch_id: str, block_type: str, content: str) -> str:
    content_hash = hashlib.sha256(f"{batch_id}:{block_type}:{content}".encode()).hexdigest()[:16]
    return f"{batch_id}-{block_type.lower()}-{content_hash}"


def _resolve_entity_type(task_key: str) -> Optional[str]:
    """Entity type for dispatch or orchestration task_key (consult_* → grade_*)."""
    rk = resolve_dispatch_task_config_key(task_key)
    return TASK_CONFIG.get(rk, {}).get("entity_type")


def _extract_entity_ids_from_response(response_raw: str, entity_type: str) -> List[str]:
    """Parse response JSON to pull individual entity IDs for batch-mode tasks.
    qualify_job_listings & evaluate_jd both return {"jobs": [{"astral_job_id": ...}, ...]}."""
    try:
        parsed = json.loads(response_raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if entity_type == "job":
        return [j["astral_job_id"] for j in parsed.get("jobs", [])
                if isinstance(j, dict) and "astral_job_id" in j]
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_migratable_task_keys() -> List[str]:
    """Return distinct task_keys from agent_responses within the migration date range."""
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT DISTINCT task_key FROM agent_responses WHERE created_at >= ? ORDER BY task_key",
            (MIGRATION_DATE_CUTOFF,),
        ).fetchall()
        return [r["task_key"] for r in rows]
    finally:
        conn.close()


def _ensure_agent_data_table(conn: sqlite3.Connection) -> None:
    """Create agent_data table if it doesn't exist yet."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_data (
            agent_data_id TEXT PRIMARY KEY,
            entity_type   TEXT NOT NULL,
            task_key      TEXT NOT NULL,
            batch_id      TEXT NOT NULL,
            created_at    TIMESTAMP NOT NULL,
            block_type    TEXT NOT NULL,
            block_data    BLOB,
            token_size    INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_data_batch ON agent_data(batch_id)")
    conn.commit()


def run_agent_data_migration(task_key: str) -> Dict[str, Any]:
    """Run all migration steps for a single task_key. Returns summary dict."""
    import uuid
    log_batch_id.set(f"migrate_agent_data-{uuid.uuid4()}")
    logger.info("=== migrate_agent_data START task_key=%s ===", task_key)
    summary: Dict[str, Any] = {"task_key": task_key, "steps": {}}

    try:
        conn = _conn()
        try:
            _ensure_agent_data_table(conn)
        finally:
            conn.close()
        # Ensure timesheet ledger migration (timesheets → anthropic_timesheets + agent_timesheets) before SQL uses new names
        from src.data.database import _ensure_timesheets_schema

        conn_ts = _conn()
        try:
            _ensure_timesheets_schema(conn_ts)
        finally:
            conn_ts.close()
        summary["steps"]["backup"] = _step0_backup()
        summary["steps"]["backfill_ledger"] = _step1_backfill_ledger(task_key)
        summary["steps"]["archive_company"] = _step2_archive_company(task_key)
        summary["steps"]["populate_agent_data"] = _step3_populate_agent_data(task_key)
        summary["steps"]["verify"] = _step4_verify(task_key)
        summary["status"] = "done"
        logger.info("=== migrate_agent_data DONE task_key=%s ===", task_key)
    except Exception as e:
        summary["status"] = "error"
        summary["error"] = str(e)
        logger.error("=== migrate_agent_data FAILED task_key=%s error=%s ===", task_key, e, exc_info=True)
    finally:
        flush_log_buffer()

    return summary


# ---------------------------------------------------------------------------
# Step 0 — Backup tables
# ---------------------------------------------------------------------------

def _step0_backup() -> Dict[str, str]:
    """Create backup tables if they don't exist (or recreate if counts don't match)."""
    conn = _conn()
    results: Dict[str, str] = {}
    date_suffix = datetime.now(timezone.utc).strftime("%Y%m%d")
    try:
        for table in BACKUP_TABLES:
            has_table = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()[0]
            if not has_table:
                results[table] = "skipped (source table absent)"
                logger.info("Backup %s: skipped (source table absent)", table)
                continue
            backup_name = f"{table}_backup_{date_suffix}"
            exists = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (backup_name,)
            ).fetchone()[0]

            if exists:
                source_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                backup_count = conn.execute(f"SELECT COUNT(*) FROM {backup_name}").fetchone()[0]
                if source_count == backup_count:
                    results[table] = f"skipped (backup exists, {backup_count} rows match)"
                    logger.info("Backup %s: skipped (counts match: %d)", backup_name, backup_count)
                    continue
                # Count mismatch — drop and recreate
                conn.execute(f"DROP TABLE {backup_name}")
                logger.warning("Backup %s: dropped (count mismatch: source=%d backup=%d)",
                               backup_name, source_count, backup_count)

            conn.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {table}")
            conn.commit()
            count = conn.execute(f"SELECT COUNT(*) FROM {backup_name}").fetchone()[0]
            results[table] = f"created ({count} rows)"
            logger.info("Backup %s: created (%d rows)", backup_name, count)
    finally:
        conn.close()
    return results


# ---------------------------------------------------------------------------
# Step 1 — Backfill dispatch_ledger
# ---------------------------------------------------------------------------

def _step1_backfill_ledger(task_key: str) -> Dict[str, int]:
    """UPDATE dispatch_ledger rows for batches related to this agent task_key.
    Uses the agent_responses→agent_timesheets join to find batch_ids, since the dispatch_ledger
    task_key (e.g. 'prefilter') differs from the agent_responses task_key (e.g. 'prefilter_company')."""
    conn = _conn()
    counts = {"entity_type": 0, "batch_size": 0, "total_cost": 0, "entity_cost": 0}

    # Find batch_ids that contain this agent task_key via the agent_timesheets/agent_responses join
    batch_rows = conn.execute("""
        SELECT DISTINCT t.batch_id FROM agent_timesheets t
        JOIN agent_responses ar ON ar.request_id = t.agent_req_id
        WHERE ar.task_key = ? AND ar.created_at >= ?
        AND t.batch_id IS NOT NULL
    """, (task_key, MIGRATION_DATE_CUTOFF)).fetchall()
    batch_ids = [r["batch_id"] for r in batch_rows]

    if not batch_ids:
        logger.info("Step 1 backfill_ledger task_key=%s: no matching batches found", task_key)
        conn.close()
        return counts

    entity_type = _resolve_entity_type(task_key)

    try:
        placeholders = ",".join("?" for _ in batch_ids)

        # 1a. entity_type
        if entity_type:
            cur = conn.execute(
                f"UPDATE dispatch_ledger SET entity_type = ? "
                f"WHERE batch_id IN ({placeholders}) AND entity_type IS NULL",
                [entity_type] + batch_ids,
            )
            counts["entity_type"] = cur.rowcount
            conn.commit()

        # 1b. batch_size from total_processed
        cur = conn.execute(
            f"UPDATE dispatch_ledger SET batch_size = total_processed "
            f"WHERE batch_id IN ({placeholders}) AND batch_size IS NULL AND total_processed > 0",
            batch_ids,
        )
        counts["batch_size"] = cur.rowcount
        conn.commit()

        # 1c. total_cost from agent_timesheets — batch by batch
        for i in range(0, len(batch_ids), 100):
            chunk = batch_ids[i:i + 100]
            ph = ",".join("?" for _ in chunk)
            cost_rows = conn.execute(
                f"SELECT batch_id, "
                f"SUM(calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output) AS total "
                f"FROM agent_timesheets WHERE batch_id IN ({ph}) GROUP BY batch_id",
                chunk,
            ).fetchall()
            for cr in cost_rows:
                if cr["total"] and cr["total"] > 0:
                    conn.execute(
                        "UPDATE dispatch_ledger SET total_cost = ? WHERE batch_id = ? AND (total_cost IS NULL OR total_cost = 0)",
                        (cr["total"], cr["batch_id"]),
                    )
                    counts["total_cost"] += 1
        conn.commit()

        # 1d. entity_cost from total_cost / batch_size
        cur = conn.execute(
            f"UPDATE dispatch_ledger SET entity_cost = ROUND(total_cost * 1.0 / batch_size, 7) "
            f"WHERE batch_id IN ({placeholders}) AND (entity_cost IS NULL OR entity_cost = 0) "
            f"AND total_cost > 0 AND batch_size > 0",
            batch_ids,
        )
        counts["entity_cost"] = cur.rowcount
        conn.commit()

        logger.info("Step 1 backfill_ledger task_key=%s: %d batches, %s", task_key, len(batch_ids), counts)
    finally:
        conn.close()
    return counts


# ---------------------------------------------------------------------------
# Step 2 — Archive company.agent_responses
# ---------------------------------------------------------------------------

def _step2_archive_company(task_key: str) -> str:
    """Archive old-format company.agent_responses to legacy column. Only for company task_keys."""
    entity_type = _resolve_entity_type(task_key)
    if entity_type != "company":
        msg = "skipped (not a company task_key)"
        logger.info("Step 2 archive_company: %s", msg)
        return msg

    conn = _conn()
    try:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(company)").fetchall()}
        if "agent_responses_legacy" in cols:
            msg = "skipped (legacy column already exists)"
            logger.info("Step 2 archive_company: %s", msg)
            return msg

        conn.execute("ALTER TABLE company ADD COLUMN agent_responses_legacy TEXT")
        cur = conn.execute(
            "UPDATE company SET agent_responses_legacy = agent_responses "
            "WHERE agent_responses IS NOT NULL AND agent_responses != '[]'"
        )
        archived = cur.rowcount
        conn.execute("UPDATE company SET agent_responses = '[]'")
        conn.commit()
        msg = f"archived {archived} companies, reset agent_responses to '[]'"
        logger.info("Step 2 archive_company: %s", msg)
        return msg
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Step 3 — Populate agent_data from agent_responses audit records
# ---------------------------------------------------------------------------

def _step3_populate_agent_data(task_key: str) -> Dict[str, int]:
    """Reconstruct agent_data blocks from historical agent_responses audit records."""
    conn = _conn()
    counts = {"records_processed": 0, "blocks_inserted": 0, "entity_refs_appended": 0,
              "mode_a": 0, "mode_b": 0, "skipped_no_batch": 0}

    try:
        # Fetch audit records with their timesheet batch_id via request_id join (unified agent_req_id)
        rows = conn.execute("""
            SELECT ar.id, ar.task_key, ar.entity_type, ar.entity_id, ar.status,
                   ar.raw_response, ar.parsed_response, ar.runtime_prompt,
                   ar.request_id, ar.created_at,
                   t.batch_id, t.batch_size,
                   t.calc_cost_cache_write + t.calc_cost_cache_read +
                   t.calc_cost_no_cache_input + t.calc_cost_output AS call_cost
            FROM agent_responses ar
            LEFT JOIN agent_timesheets t ON ar.request_id = t.agent_req_id
            WHERE ar.task_key = ? AND ar.created_at >= ?
            ORDER BY ar.created_at
        """, (task_key, MIGRATION_DATE_CUTOFF)).fetchall()

        resolved_entity_type = _resolve_entity_type(task_key) or "unknown"

        for row in rows:
            batch_id = row["batch_id"]
            if not batch_id:
                counts["skipped_no_batch"] += 1
                continue

            entity_type = row["entity_type"] or resolved_entity_type
            entity_id = row["entity_id"]
            created_at = row["created_at"]
            batch_size = row["batch_size"] or 1
            call_cost = row["call_cost"] or 0.0

            prompt_blocks: List[Dict[str, str]] = []

            # Try Mode A: parse runtime_prompt
            runtime_raw = _decompress(row["runtime_prompt"])
            if runtime_raw:
                try:
                    prompt_data = json.loads(runtime_raw)
                    blocks_inserted = _mode_a_from_runtime_prompt(
                        conn, prompt_data, entity_type, task_key, batch_id, created_at, prompt_blocks
                    )
                    counts["blocks_inserted"] += blocks_inserted
                    counts["mode_a"] += 1
                except (json.JSONDecodeError, Exception) as e:
                    logger.debug("Mode A parse failed for ar.id=%s, falling through to Mode B: %s",
                                 row["id"], e)
                    runtime_raw = None  # fall through to Mode B

            if not runtime_raw:
                counts["mode_b"] += 1

            # Store response block
            response_raw = _decompress(row["parsed_response"]) or _decompress(row["raw_response"])
            if response_raw:
                resp_id = _insert_agent_data(
                    conn, entity_type, task_key, batch_id, "RESPONSE", response_raw, created_at
                )
                prompt_blocks.append({"type": "RESPONSE", "id": resp_id})
                counts["blocks_inserted"] += 1

            # Append entity refs — try parsing response for individual IDs first (batch tasks),
            # fall back to audit record entity_id for single-entity tasks
            if prompt_blocks:
                per_entity_ids = _extract_entity_ids_from_response(response_raw, entity_type) if response_raw else []
                if per_entity_ids:
                    per_cost = round(call_cost / len(per_entity_ids), 7)
                    for eid in per_entity_ids:
                        _append_entity_ref(conn, entity_type, eid, {
                            "batch_id": batch_id,
                            "task_key": task_key,
                            "created_at": created_at,
                            "entity_cost": per_cost,
                            "prompt_blocks": prompt_blocks,
                        })
                        counts["entity_refs_appended"] += 1
                else:
                    entity_cost = round(call_cost / batch_size, 7) if batch_size > 0 else call_cost
                    _append_entity_ref(conn, entity_type, entity_id, {
                        "batch_id": batch_id,
                        "task_key": task_key,
                        "created_at": created_at,
                        "entity_cost": entity_cost,
                        "prompt_blocks": prompt_blocks,
                    })
                    counts["entity_refs_appended"] += 1

            counts["records_processed"] += 1

        conn.commit()
        logger.info("Step 3 populate_agent_data task_key=%s: %s", task_key, counts)
    finally:
        conn.close()
    return counts


def _mode_a_from_runtime_prompt(
    conn: sqlite3.Connection,
    prompt_data: list,
    entity_type: str,
    task_key: str,
    batch_id: str,
    created_at: str,
    prompt_blocks: List[Dict[str, str]],
) -> int:
    """Parse runtime_prompt list and store blocks. Returns count of blocks inserted.

    runtime_prompt is a list of single-key dicts:
      [{"system_prompt": {"content": "...", "cache": true, ...}},
       {"cached_context": {"content": "...", ...}},
       {"nocache_context": {"content": "...", ...}},
       {"user_prompt": {"content": "...", ...}}]
    """
    # Map runtime_prompt labels → block_type.
    # Note: "user_prompt" in runtime_prompt is the concatenation of user_content + live_content.
    # Production _store_prompt_blocks splits these into separate NO_CACHE + TASK blocks.
    # For historical data we store the combined content as a single TASK block.
    LABEL_MAP = {
        "system_prompt":   "SYSTEM",
        "cached_context":  "CACHE_A",
        "nocache_context": "NO_CACHE",
        "user_prompt":     "TASK",
    }
    inserted = 0
    for item in prompt_data:
        if not isinstance(item, dict):
            continue
        for label, payload in item.items():
            block_type = LABEL_MAP.get(label)
            if not block_type or not isinstance(payload, dict):
                continue
            content = payload.get("content", "")
            if not content:
                continue
            agent_data_id = _insert_agent_data(
                conn, entity_type, task_key, batch_id, block_type, content, created_at
            )
            prompt_blocks.append({"type": block_type, "id": agent_data_id})
            inserted += 1
    return inserted


def _insert_agent_data(
    conn: sqlite3.Connection,
    entity_type: str, task_key: str, batch_id: str,
    block_type: str, content: str, created_at: str,
) -> str:
    """INSERT OR IGNORE a single agent_data block. Returns the deterministic agent_data_id."""
    agent_data_id = _make_agent_data_id(batch_id, block_type, content)
    blob = zlib.compress(content.encode("utf-8"))
    token_size = len(content) // CHARS_PER_TOKEN
    conn.execute(
        "INSERT OR IGNORE INTO agent_data "
        "(agent_data_id, entity_type, task_key, batch_id, created_at, block_type, block_data, token_size) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (agent_data_id, entity_type, task_key, batch_id, created_at, block_type, blob, token_size),
    )
    return agent_data_id


def _append_entity_ref(
    conn: sqlite3.Connection, entity_type: str, entity_id: str, entry: Dict[str, Any]
) -> None:
    """Append a lightweight reference to the entity's agent_responses JSON array.
    Deduplicates by batch_id to prevent duplicate entries on re-run."""
    table_map = {
        "company":   ("company",   "short_name"),
        "job":       ("job",       "astral_job_id"),
        "candidate": ("candidate", "astral_candidate_id"),
    }
    if entity_type not in table_map:
        return
    table, pk_col = table_map[entity_type]

    row = conn.execute(
        f"SELECT agent_responses FROM {table} WHERE {pk_col} = ?", (entity_id,)
    ).fetchone()
    if not row:
        return

    existing = []
    if row[0]:
        try:
            existing = json.loads(row[0])
        except (TypeError, ValueError):
            existing = []

    # Dedup: skip if batch_id + task_key combo already present (multiple task_keys can share a batch_id)
    if any(e.get("batch_id") == entry["batch_id"] and e.get("task_key") == entry.get("task_key")
           for e in existing if isinstance(e, dict)):
        return

    existing.append(entry)
    conn.execute(
        f"UPDATE {table} SET agent_responses = ? WHERE {pk_col} = ?",
        (json.dumps(existing), entity_id),
    )


# ---------------------------------------------------------------------------
# Step 4 — Verify
# ---------------------------------------------------------------------------

def _step4_verify(task_key: str) -> Dict[str, Any]:
    """Run count checks after migration."""
    conn = _conn()
    try:
        agent_data_count = conn.execute(
            "SELECT COUNT(*) FROM agent_data WHERE task_key = ?", (task_key,)
        ).fetchone()[0]

        # Find batch_ids via the same join used in Step 1/3
        batch_rows = conn.execute("""
            SELECT DISTINCT t.batch_id FROM agent_timesheets t
            JOIN agent_responses ar ON ar.request_id = t.agent_req_id
            WHERE ar.task_key = ? AND ar.created_at >= ? AND t.batch_id IS NOT NULL
        """, (task_key, MIGRATION_DATE_CUTOFF)).fetchall()
        batch_ids = [r["batch_id"] for r in batch_rows]

        ledger_filled = 0
        ledger_total = 0
        if batch_ids:
            ph = ",".join("?" for _ in batch_ids)
            ledger_filled = conn.execute(
                f"SELECT COUNT(*) FROM dispatch_ledger WHERE batch_id IN ({ph}) AND entity_type IS NOT NULL",
                batch_ids,
            ).fetchone()[0]
            ledger_total = conn.execute(
                f"SELECT COUNT(*) FROM dispatch_ledger WHERE batch_id IN ({ph})",
                batch_ids,
            ).fetchone()[0]

        result = {
            "agent_data_rows": agent_data_count,
            "ledger_rows_with_entity_type": ledger_filled,
            "ledger_rows_total": ledger_total,
            "batches_found": len(batch_ids),
        }
        logger.info("Step 4 verify task_key=%s: %s", task_key, result)
        return result
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <task_key>")
        print(f"Available: {get_migratable_task_keys()}")
        sys.exit(1)
    result = run_agent_data_migration(sys.argv[1])
    print(json.dumps(result, indent=2))
