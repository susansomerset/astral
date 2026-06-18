# -*- coding: utf-8 -*-
"""
Data layer for database operations.

SQLite operations for the ASTRAL system.
Implements database operations directly (no imports from old code).
Per code organization rules: `src/astral_database.py` -> `src/data/database.py`

Tables used (inventory):
- company   — Roster: company state, state_history, batch_id, company_data, agent_responses, job_site, candidate_id (FK to candidate), etc.
- job       — Tracker: astral_job_id, company, company_job_id, job_title, job_link, job_data, state, state_history, batch_id, etc.
- candidate — Candidate: state, candidate_data JSON blob, candidate_api_key TEXT (Fernet-encrypted Anthropic key).
- agent    — Agent: agent_id TEXT PK, content TEXT, model_code TEXT (legacy/read-only), brain_setting TEXT (Little|Medium|Big), temperature REAL, max_tokens INTEGER, updated_at TIMESTAMP.
- agent_task — Task prompt config with versioning: task_key_uuid TEXT PK, task_key TEXT, current INTEGER (1=active), agent_id TEXT, seven prompt segments (`user_prompt`; `cache_prompt` = Anthropic cache block A; `cache_prompt_b|c|d` = blocks B–D; `nocache_prompt`; `system_prompt` per-task override, empty = use agent content at runtime), `run_next`, `updated_at`. Any segment edit (all seven) retires prior row + inserts new `current=1`.
- anthropic_timesheets — Anthropic-only token/cost ledger mirror: anthropic_req_id TEXT UNIQUE, same metric columns as agent_timesheets (batch_id, token counts, calc_cost_*, agent_performance, failure_note, created_at).
- agent_timesheets — Unified token/cost ledger for all LLM providers: agent_req_id TEXT UNIQUE (vendor request id), same metric columns as anthropic_timesheets.
- agent_responses — Agent response audit (insert-only from add_agent_response_entry).
- agent_data — Prompt/response content blocks keyed by batch_id (save_agent_data, get_agent_data_by_batch, get_agent_data).
- company_job_scan — Gazer: scan outcome per company per batch (insert-only).
- dispatch_task — Dispatcher scheduling config (save/get/list/update_dispatch_task, get_due_tasks).
- dispatch_ledger — Dispatcher run history (save/update/get/list_dispatch_ledger).
- app_log — Application log storage (add_log_entry, list_log_entries).
- board_search — Saved board searches per candidate (board_search_id, candidate_id, board_key, label, criteria JSON NOT NULL,
  state TEXT ACTIVE|INACTIVE|ERROR matching BOARD_SEARCH_STATES, search_mode, deeplink_url, batch_id — claim lock only §2.4;
  nullable last_scan_at gaze cadence, not edited on user PATCH — AST-482).
- board_search_run — Per-gaze ingest metrics (batch_id, board_search_id, new/duplicates/invalid_title counts).
- company_search_terms — Per-candidate Google discovery queries (candidate_id, search_term TEXT, nullable last_scan_at,
  created_at, updated_at). Composite PRIMARY KEY (candidate_id, search_term). Source of truth for discovery terms (AST-524).
- rubric_vector — Per-candidate rubric vector identity (rubric_vector_uuid TEXT PK, candidate_id,
  task_key TEXT, task_key_uuid TEXT, code, label, content, importance INTEGER, content_fingerprint TEXT,
  current INTEGER 0|1, created_at, updated_at). Active set: rows with current=1 for (candidate_id, task_key).
  Versioning follows agent_task current=1 pattern (AST-722).
- vector_feedback — Per-run per-vector feedback grain (vector_feedback_id TEXT PK, rubric_vector_uuid,
  candidate_id, batch_id, task_key, feedback_type TEXT, value TEXT, optional agent_data_id, created_at).
  One row per feedback type per vector per run; type/value codes validated against RUBRIC_FEEDBACK_CONFIG (AST-724 writes).
- candidate_intake_session — Per-candidate Estelle intake chat (intake_session_id TEXT PK, candidate_id,
  status ACTIVE|BUILT, transcript JSON, prompt_snapshot JSON, last_ready_to_build INTEGER, built_at TIMESTAMP,
  created_at, updated_at). Resume-after-close (AST-558).

Schema checks use sqlite_master only. No other tables in the database are touched by this module.

Company: save_company, get_company, update_company; batch: set_company_batch, get_company_batch, clear_company_batch (claim_company_batch wrapper).
Job: save_job (upsert), get_job; batch: claim_job_batch, get_job_batch, clear_job_batch.
Candidate: save_candidate (upsert), get_candidate, list_candidates.
Agent: save_agent (upsert), get_agent, list_agents, update_agent, delete_agent, count_agent_task_refs.
Retry/log/crash on transient DB errors; domain outcomes
via return values (duplicate -> False, no records -> False / count).
"""

import json
import os
import sqlite3
import time
import uuid
import zlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from cryptography.fernet import Fernet, InvalidToken

from src.utils.config import (
    AGENT_CONFIG,
    ALLOWED_TIMESHEET_PROVIDERS,
    DEEPSEEK_MODEL_PRICING,
    PRONOUN_PREFERENCE_DEFAULT,
    PRONOUN_PREFERENCE_OPTIONS,
    ASTRAL_CONFIG,
    BLOCK_TYPES,
    BOARD_SEARCH_STATES,
    BOARDS_CONFIG,
    CANDIDATE_STATES,
    COMPANY_STATES,
    INFLOW_CONFIG,
    PASSED_SCORE_GATED_STATES,
    ROSTER_CONFIG,
    TASK_CONFIG,
    get_active_llm_provider,
    infer_brain_setting_from_legacy_model_code,
    resolve_brain_setting_to_anthropic_agent_key,
    resolve_brain_setting_to_deepseek_tier_meta,
    dispatch_task_admin_defaults,
    dispatch_claim_uses_score_floor,
    dispatch_claim_states,
    trigger_state_used_by_scored_dispatch_task,
    validate_allowed_brain_setting,
    RUBRIC_CRITERIA_ARTIFACT_KEYS,
)
from src.utils.cost_calculator import calculate_cost_components_deepseek_from_counts
from src.utils.logging import get_logger

DB_PATH = ASTRAL_CONFIG["db_dir"] / "astral.db"
_log = get_logger(__name__)


def _coerce_agent_brain_setting(row: Dict[str, Any]) -> str:
    raw = row.get("brain_setting")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return infer_brain_setting_from_legacy_model_code(row.get("model_code"))


def _expose_agent_public(row_dict: Dict[str, Any]) -> Dict[str, Any]:
    """brain_setting authoritative; model_code JSON key mirrors resolved SKU for admin UI."""
    out = dict(row_dict)
    bs = _coerce_agent_brain_setting(out)
    out["brain_setting"] = bs
    prov = get_active_llm_provider()
    if prov == "anthropic":
        rk = resolve_brain_setting_to_anthropic_agent_key(bs)
    elif prov == "deepseek":
        rk = str(resolve_brain_setting_to_deepseek_tier_meta(bs)["vendor_model"])
    else:
        raise ValueError(f"Unknown active LLM provider {prov!r}")
    out["resolved_model_key"] = rk
    out["model_code"] = rk
    return out


def _utc_now() -> str:
    """UTC timestamp in SQLite-compatible format (no T, no tz offset, no fractional seconds)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# -- Fernet encryption for candidate API keys --
_ENCRYPTION_KEY = os.environ.get("ASTRAL_ENCRYPTION_KEY", "")
try:
    _fernet = Fernet(_ENCRYPTION_KEY.encode()) if _ENCRYPTION_KEY else None
except (ValueError, Exception) as _init_err:
    _log.warning("ASTRAL_ENCRYPTION_KEY is set but invalid — encryption disabled: %s", _init_err)
    _fernet = None


def encrypt_value(plaintext: str) -> str:
    """Fernet-encrypt a string. Raises RuntimeError if no encryption key configured."""
    if not _fernet:
        raise RuntimeError("ASTRAL_ENCRYPTION_KEY not set or invalid — cannot encrypt")
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Fernet-decrypt a string. Raises RuntimeError/ValueError on failure."""
    if not _fernet:
        raise RuntimeError("ASTRAL_ENCRYPTION_KEY not set or invalid — cannot decrypt")
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as e:
        raise ValueError(f"Decryption failed (bad key or corrupted data): {e}")


_company_schema_ensured = False
_job_schema_ensured = False
_candidate_schema_ensured = False
_company_candidate_fk_ensured = False
_company_job_scan_schema_ensured = False
_agent_responses_schema_ensured = False
_agent_schema_ensured = False
_agent_task_schema_ensured = False
_timesheets_schema_ensured = False
_dispatch_task_schema_ensured = False
_board_search_schema_ensured = False
_board_search_run_schema_ensured = False
_company_search_terms_schema_ensured = False
_company_search_terms_migration_swept = False
_rubric_vector_schema_ensured = False
_vector_feedback_schema_ensured = False
_rubric_vector_backfill_swept = False
_intake_session_schema_ensured = False
_dispatch_ledger_schema_ensured = False
_app_log_schema_ensured = False
_agent_data_schema_ensured = False

# ---- TODO:Cleanup ----
# refactor callers of claim_company_batch to use set_company_batch.
# refactor callers of update_company_last_scan_at to use update_company directly.
# refactor callers of get_company_by_name to use get_company.
def claim_company_batch(
    batch_id: str,
    state: str,
    limit: int,
    sort_by: Optional[str] = None,
    scan_interval_hours: Optional[float] = None,
    candidate_id: Optional[str] = None,
    *,
    require_empty_website: bool = False,
    score_floor: Optional[float] = None,
    states: Optional[List[str]] = None,
    ) -> int:
    """Set batch_id, batch_created_at on company rows WHERE state=? AND batch_id IS NULL [AND scan_interval] LIMIT ?.
    Parameter order: batch_id first (caller owns it). When scan_interval_hours is set (gazer), only rows with
    last_scan_at NULL or stale. candidate_id scopes to a single candidate's companies. Returns count updated.
    score_floor: when set, only companies with company_data.prefilter_score >= floor are claimed (AST-508).
    """
    return set_company_batch(
        batch_id,
        clear=False,
        state=state,
        limit=limit,
        sort_by=sort_by,
        scan_interval_hours=scan_interval_hours,
        candidate_id=candidate_id,
        require_empty_website=require_empty_website,
        score_floor=score_floor,
        states=states,
    )

def clear_company_batch(batch_id: str) -> int:
    """Set batch_id and batch_created_at to NULL for all companies in batch. Returns count."""
    return set_company_batch(batch_id, clear=True)

def update_company_last_scan_at(short_name: str) -> None:
    """Set last_scan_at = now for company. Called on success paths only. TODO: use update_company directly."""
    now = _utc_now()
    update_company(short_name, last_scan_at=now)

def get_company_by_name(short_name: str) -> Optional[Dict[str, Any]]:
    """TODO: use get_company directly. Wrapper for legacy callers (run_gazer)."""
    return get_company(short_name)

# ---- Database ----
def _get_connection() -> sqlite3.Connection:
    """Get database connection.
    
    Returns: SQLite connection with row factory enabled
    """
    # Ensure data directory exists (DB_PATH already set above)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def _log_db_failure(fn_name: str, args: tuple, kwargs: dict, exc: BaseException) -> None:
    """Log on failure path with all vars so info persists. Call before re-raise."""
    _log.error(
        f"database.{fn_name} failed: {exc!r} | args={args!r} kwargs={kwargs!r}"
    )

def _run_with_retry(fn: Callable[[], Any]) -> Any:
    """Retry transient DB errors (config-driven). Log with all args then raise on give-up.
    fn is a nullary callable (closure over args)."""
    cfg = ASTRAL_CONFIG.get("db_retry", {}) or {}
    max_attempts = int(cfg.get("max_attempts", 3))
    base_delay = float(cfg.get("base_delay_seconds", 0.5))
    max_delay = float(cfg.get("max_delay_seconds", 5.0))
    last: Optional[Exception] = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except sqlite3.OperationalError as e:
            last = e
            if "locked" in str(e).lower() or "busy" in str(e).lower() or "timeout" in str(e).lower():
                if attempt < max_attempts - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    time.sleep(delay)
                    continue
            _log_db_failure(fn.__name__, (), {}, e)
            raise
        except sqlite3.IntegrityError:
            raise
    if last is not None:
        _log_db_failure(fn.__name__, (), {}, last)
        raise last
    raise RuntimeError("unreachable")

def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}

def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> None:
    """Merge overlay into base in place. Nested dicts recurse; other values overwrite."""
    for k, v in overlay.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


# ---- Config-table upsert helpers ----

ALLOWED_CONFIG_TABLES = frozenset({"dispatch_task", "agent_task", "candidate"})


def table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    """Return DB column names in PRAGMA order for table."""
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    if not exists:
        raise ValueError(f"unknown table: {table!r}")
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def primary_key_column_names(conn: sqlite3.Connection, table: str) -> List[str]:
    """Return SQLite primary-key column names for ``table`` (non-empty list or ValueError).

    Columns are ordered by ``PRAGMA table_info``.pk ascending, then cid ascending
    so composite PK order matches SQLite.
    """
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    if not exists:
        raise ValueError(f"unknown table: {table!r}")
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    pk_entries = [(r[5], r[0], r[1]) for r in rows if int(r[5] or 0) != 0]
    pk_entries.sort(key=lambda t: (t[0], t[1]))
    pk_cols = [t[2] for t in pk_entries]
    if not pk_cols:
        raise ValueError(f"table {table!r} has no primary key")
    return pk_cols


def _sql_quote_ident(ident: str) -> str:
    return '"' + ident.replace('"', '""') + '"'


def _copy_reject_nested_json(v: Any, human_path: str) -> None:
    if isinstance(v, (dict, list)):
        raise ValueError(f"{human_path}: copy rows must use flat JSON scalars only (reject dict/list)")


def _db_cell_equals_pasted_scalar(db_val: Any, pasted_val: Any) -> bool:
    """Compare SQLite cell to JSON-parsed scalar (None ≡ JSON null)."""
    if pasted_val is None:
        return db_val is None
    if db_val is None:
        return False
    if isinstance(pasted_val, bool):
        if isinstance(db_val, bool):
            return pasted_val == db_val
        if isinstance(db_val, int):
            return int(pasted_val) == db_val
        return False
    if isinstance(pasted_val, (int, float)) and isinstance(db_val, (int, float)):
        return pasted_val == db_val
    return db_val == pasted_val


def _validate_copy_row_keys(row: Dict[str, Any], columns_ordered: List[str], row_index_1: int) -> None:
    if set(row.keys()) != set(columns_ordered):
        raise ValueError(f"row {row_index_1}: columns must exactly match table layout (wrong keys)")


def _coerce_agent_task_current_for_import(raw: Any) -> int:
    """Normalize agent_task.current from Copy Output JSON to 0 | 1."""
    if isinstance(raw, bool):
        return int(raw)
    if raw in (0, 1):
        return int(raw)
    if isinstance(raw, str) and raw.strip().lower() in ("true", "false"):
        return 1 if raw.strip().lower() == "true" else 0
    raise ValueError(f"invalid agent_task.current value {raw!r} (want 0, 1, true, or false)")


def apply_generic_table_copy_upsert(
    conn: sqlite3.Connection, table: str, rows: list[dict[str, Any]]
) -> Dict[str, int]:
    """Generic INSERT/UPDATE-by-primary-key merge for administrator Copy Output batches.

    Row dict keys must equal ``table_columns(conn, table)`` exactly (no COMMIT).
    """
    inserted = updated = skipped = 0
    columns_ordered = table_columns(conn, table)
    pk_cols = primary_key_column_names(conn, table)
    non_pk = [c for c in columns_ordered if c not in pk_cols]
    # `ON CONFLICT… DO UPDATE SET` needs at least one non-PK assignment; all-PK tables
    # are not valid admin upsert targets (advisory from Radia review, AST-464).
    if not non_pk:
        raise ValueError(
            f"table {table!r} has only primary-key columns; copy upsert is not supported"
        )

    qt = _sql_quote_ident(table)
    iclause = ",".join(_sql_quote_ident(c) for c in columns_ordered)
    ph = ",".join(["?"] * len(columns_ordered))
    pk_q = ",".join(_sql_quote_ident(c) for c in pk_cols)
    non_pk_clause = ",".join(f"{_sql_quote_ident(c)}=excluded.{_sql_quote_ident(c)}" for c in non_pk)
    upsert_sql = (
        f"INSERT INTO {qt} ({iclause}) VALUES ({ph}) "
        f"ON CONFLICT({pk_q}) DO UPDATE SET {non_pk_clause}"
    )
    pk_where = " AND ".join(f"{_sql_quote_ident(c)} = ?" for c in pk_cols)
    sel_sql = (
        f"SELECT {','.join(_sql_quote_ident(c) for c in non_pk)} "
        f"FROM {qt} WHERE {pk_where}"
    )

    for i, row in enumerate(rows, start=1):
        _validate_copy_row_keys(row, columns_ordered, i)
        for c in columns_ordered:
            _copy_reject_nested_json(row[c], f"row {i} column {c!r}")

        pk_vals = tuple(row[c] for c in pk_cols)
        cur_non = conn.execute(sel_sql, pk_vals).fetchone()
        vals_tuple = tuple(row[c] for c in columns_ordered)

        if cur_non is None:
            conn.execute(upsert_sql, vals_tuple)
            inserted += 1
            continue
        mismatched = any(
            not _db_cell_equals_pasted_scalar(cur_non[j], row[cn]) for j, cn in enumerate(non_pk)
        )
        if mismatched:
            conn.execute(upsert_sql, vals_tuple)
            updated += 1
        else:
            skipped += 1

    return {"inserted": inserted, "updated": updated, "skipped": skipped}


def _agent_import_row_equals_db(existing: sqlite3.Row, row: Dict[str, Any], columns_ordered: List[str]) -> bool:
    for c in columns_ordered:
        if c == "updated_at":
            continue
        pv = row[c]
        ev = existing[c]
        if c == "current":
            if _coerce_agent_task_current_for_import(pv) != int(ev):
                return False
            continue
        if not _db_cell_equals_pasted_scalar(ev, pv):
            return False
    return True


def apply_agent_task_copy_upsert(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> Dict[str, int]:
    """Import agent_task Copy Output on caller-owned connection within caller transaction."""
    inserted = updated = skipped = 0
    columns_ordered = table_columns(conn, "agent_task")
    now = _utc_now()

    hist_rows: List[Dict[str, Any]] = []
    curr_rows: List[Dict[str, Any]] = []
    for ri, raw in enumerate(rows, start=1):
        _validate_copy_row_keys(raw, columns_ordered, ri)
        for c in columns_ordered:
            _copy_reject_nested_json(raw[c], f"row {ri} column {c!r}")
        cur_flag = _coerce_agent_task_current_for_import(raw["current"])
        (hist_rows if cur_flag == 0 else curr_rows).append(raw)

    qt = _sql_quote_ident("agent_task")
    cols_join = ",".join(_sql_quote_ident(c) for c in columns_ordered)
    placeholders = ",".join("?" * len(columns_ordered))

    for ri, r in enumerate(hist_rows, start=1):
        uuid_raw = r["task_key_uuid"]
        if uuid_raw is None:
            raise ValueError(f"historical row {ri}: missing task_key_uuid")
        _copy_reject_nested_json(uuid_raw, f"historical row {ri} column 'task_key_uuid'")
        uuid_pk = uuid_raw if isinstance(uuid_raw, str) else str(uuid_raw)

        sel = conn.execute(
            f"SELECT {cols_join} FROM {qt} WHERE {_sql_quote_ident('task_key_uuid')} = ?", (uuid_pk,)
        ).fetchone()
        if sel is None:
            conn.execute(f"INSERT INTO {qt} ({cols_join}) VALUES ({placeholders})", tuple(r[c] for c in columns_ordered))
            inserted += 1
        elif _agent_import_row_equals_db(sel, r, columns_ordered):
            skipped += 1
        else:
            set_parts = [_sql_quote_ident(c) + " = ?" for c in columns_ordered if c != "task_key_uuid"]
            vals_up = tuple(r[c] for c in columns_ordered if c != "task_key_uuid") + (uuid_pk,)
            conn.execute(
                f"UPDATE {qt} SET {', '.join(set_parts)} WHERE {_sql_quote_ident('task_key_uuid')} = ?",
                vals_up,
            )
            updated += 1

    task_to_row: Dict[str, Dict[str, Any]] = {}
    for ri, r in enumerate(curr_rows, start=1):
        tk_raw = r.get("task_key")
        if tk_raw is None:
            raise ValueError(f"current row {ri}: missing task_key")
        _copy_reject_nested_json(tk_raw, f"current row {ri} column 'task_key'")
        tk_str = tk_raw if isinstance(tk_raw, str) else str(tk_raw)
        if tk_str in task_to_row:
            raise ValueError(
                "invalid Copy Output: more than one current=1 row for the same task_key",
            )
        task_to_row[tk_str] = r

    def _strip_seg_imp(s: Optional[str]) -> str:
        return (s if s is not None else "").strip()

    sel_cur = """SELECT task_key_uuid, agent_id, user_prompt, cache_prompt,
                        cache_prompt_b, cache_prompt_c, cache_prompt_d,
                        nocache_prompt, run_next, system_prompt
                 FROM agent_task WHERE task_key = ? AND current = 1"""

    for tk_str in sorted(task_to_row.keys()):
        r = task_to_row[tk_str]
        cur_before = conn.execute(sel_cur, (tk_str,)).fetchone()

        skip_row = False
        if cur_before is not None:
            eu, ea, eb, ec, ed, en = (
                cur_before[2],
                cur_before[3],
                cur_before[4],
                cur_before[5],
                cur_before[6],
                cur_before[7],
            )
            p_user = "" if r["user_prompt"] is None else (
                r["user_prompt"] if isinstance(r["user_prompt"], str) else str(r["user_prompt"])
            )
            p_cache = "" if r["cache_prompt"] is None else (
                r["cache_prompt"] if isinstance(r["cache_prompt"], str) else str(r["cache_prompt"])
            )
            p_np = "" if r["nocache_prompt"] is None else (
                r["nocache_prompt"] if isinstance(r["nocache_prompt"], str) else str(r["nocache_prompt"])
            )
            rn_src = r["run_next"] if r["run_next"] is not None else ""
            new_rn = (rn_src if isinstance(rn_src, str) else str(rn_src)).strip()

            cb = _strip_seg_imp(r["cache_prompt_b"])
            cc = _strip_seg_imp(r["cache_prompt_c"])
            cd = _strip_seg_imp(r["cache_prompt_d"])

            sys_raw = "" if r["system_prompt"] is None else r["system_prompt"]
            new_sp = (sys_raw if isinstance(sys_raw, str) else str(sys_raw)).strip()
            prev_sys_row = cur_before[9]
            prev_sys = (
                prev_sys_row.strip()
                if isinstance(prev_sys_row, str)
                else str(prev_sys_row or "").strip()
            )

            ag_raw = "" if r["agent_id"] is None else r["agent_id"]
            ver_agent = ag_raw if isinstance(ag_raw, str) else str(ag_raw)

            rn_db = (cur_before[8] if cur_before[8] is not None else "") or ""
            rn_db_strip = rn_db.strip() if isinstance(rn_db, str) else str(rn_db).strip()

            ea_db = cur_before[1] if cur_before[1] is not None else ""
            content_changed = (
                p_user != eu
                or p_cache != ea
                or cb != eb
                or cc != ec
                or cd != ed
                or p_np != en
                or new_sp != prev_sys
            )
            if content_changed:
                skip_row = False
            elif ver_agent != (ea_db if isinstance(ea_db, str) else str(ea_db or "")):
                skip_row = False
            elif new_rn != rn_db_strip:
                skip_row = False
            else:
                skip_row = True

        if skip_row:
            skipped += 1
            continue

        was_absent = cur_before is None
        _save_agent_task_on_connection(
            conn,
            tk_str,
            now=now,
            agent_id=r["agent_id"],
            user_prompt=r["user_prompt"],
            cache_prompt=r["cache_prompt"],
            cache_prompt_b=r["cache_prompt_b"],
            cache_prompt_c=r["cache_prompt_c"],
            cache_prompt_d=r["cache_prompt_d"],
            nocache_prompt=r["nocache_prompt"],
            run_next=r["run_next"],
            system_prompt=r["system_prompt"],
            import_explicit=True,
        )
        if was_absent:
            inserted += 1
        else:
            updated += 1

    return {"inserted": inserted, "updated": updated, "skipped": skipped}


def apply_config_table_upsert(
    conn: sqlite3.Connection,
    table: str,
    columns: List[str],
    rows: List[List[Any]],
) -> Dict[str, Any]:
    """
    Apply upsert rows into ``table``. Caller commits or rolls back.

    ``columns`` must exactly match PRAGMA table_info order for ``table``.
    Each row must be a list of the same length as ``columns``.
    """
    if table not in ALLOWED_CONFIG_TABLES:
        raise ValueError(f"table not allowed: {table!r} (allowed: {sorted(ALLOWED_CONFIG_TABLES)})")

    ensure_table_schema_for_upsert(conn, table)

    expected = table_columns(conn, table)
    if list(columns) != expected:
        raise ValueError(
            f"{table}: column list must match local schema.\n"
            f"  got:     {list(columns)}\n  expected: {expected}"
        )

    for i, row in enumerate(rows):
        if not isinstance(row, list):
            raise ValueError(f"{table}: row {i} is not a list")
        if len(row) != len(columns):
            raise ValueError(f"{table}: row {i} has {len(row)} values, expected {len(columns)}")

    if table == "dispatch_task":
        updated = inserted = 0
        for row in rows:
            d = dict(zip(columns, row))
            cid, task_key, trigger_state = d["candidate_id"], d["task_key"], d["trigger_state"]
            cur = conn.execute(
                "SELECT id FROM dispatch_task WHERE candidate_id = ? AND task_key = ? AND trigger_state = ?",
                (cid, task_key, trigger_state),
            ).fetchone()
            assign_cols = [c for c in columns if c != "id"]
            if cur:
                uid = cur[0]
                set_clause = ", ".join(f"{c} = ?" for c in assign_cols)
                vals = [d[c] for c in assign_cols] + [uid]
                conn.execute(f"UPDATE dispatch_task SET {set_clause} WHERE id = ?", vals)
                updated += 1
            else:
                icols = [c for c in columns if c != "id"]
                ph = ", ".join("?" * len(icols))
                conn.execute(
                    f"INSERT INTO dispatch_task ({', '.join(icols)}) VALUES ({ph})",
                    [d[c] for c in icols],
                )
                inserted += 1
        return {"ok": True, "table": table, "updated": updated, "inserted": inserted, "rows": len(rows)}

    if table in ("agent_task", "candidate"):
        ph = ", ".join("?" * len(columns))
        cols = ", ".join(columns)
        conn.executemany(f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({ph})", rows)
        return {"ok": True, "table": table, "replaced": len(rows), "rows": len(rows)}

    raise AssertionError(table)


# ---- Company ----

# Company batch primitives (prefilter, locate job page, parse job page, gazer)
# Allowed ORDER BY columns for company batch claims (set_company_batch / roster).
COMPANY_BATCH_SORT_COLUMNS = frozenset({"rowid", "updated_at", "created_at", "state_updated_at", "last_scan_at"})

BOARD_SEARCH_BATCH_SORT_COLUMNS = frozenset({"rowid", "updated_at", "created_at", "last_scan_at"})
_UPDATE_COMPANY_ALLOWED = frozenset({
    "state", "company_name", "company_website", "job_site", "batch_id", "batch_created_at",
    "company_data", "agent_responses", "state_history", "last_scan_at", "updated_at", "state_updated_at",
    "candidate_id",
})

def _ensure_company_schema(conn: sqlite3.Connection) -> None:
    """Create company table with snake_case columns if not present. Idempotent.
    Adds batch_created_at if missing (migration for existing tables)."""
    global _company_schema_ensured
    if _company_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='company'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE company (
                short_name TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                company_name TEXT,
                company_website TEXT,
                job_site TEXT,
                batch_id TEXT,
                batch_created_at TIMESTAMP,
                last_scan_at TIMESTAMP,
                company_data TEXT,
                agent_responses TEXT DEFAULT '[]',
                agent_responses_legacy TEXT,
                state_history TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                state_updated_at TIMESTAMP
            )
        """)
        for _idx_name, sql in [
            ("idx_company_state", "CREATE INDEX IF NOT EXISTS idx_company_state ON company(state)"),
            ("idx_company_name", "CREATE INDEX IF NOT EXISTS idx_company_name ON company(company_name)"),
        ]:
            try:
                conn.execute(sql)
            except sqlite3.OperationalError:
                pass
        conn.commit()
    else:
        # Migration: add batch_created_at if missing
        cursor = conn.execute("PRAGMA table_info(company)")
        cols = {row[1] for row in cursor.fetchall()}
        if "batch_created_at" not in cols:
            try:
                conn.execute("ALTER TABLE company ADD COLUMN batch_created_at TIMESTAMP")
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
        if "last_scan_at" not in cols:
            try:
                conn.execute("ALTER TABLE company ADD COLUMN last_scan_at TIMESTAMP")
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
        if "state_history" not in cols:
            try:
                conn.execute("ALTER TABLE company ADD COLUMN state_history TEXT DEFAULT '[]'")
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
        if "agent_responses_legacy" not in cols:
            try:
                conn.execute("ALTER TABLE company ADD COLUMN agent_responses_legacy TEXT")
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
    _company_schema_ensured = True

def _parse_company_row(d: Dict[str, Any]) -> Dict[str, Any]:
    """Parse company_data, agent_responses, and state_history JSON in row dict. Mutates and returns d."""
    if d.get("company_data"):
        try:
            d["company_data"] = json.loads(d["company_data"])
        except (TypeError, ValueError):
            d["company_data"] = {}
    else:
        d["company_data"] = {}
    if d.get("agent_responses"):
        try:
            d["agent_responses"] = json.loads(d["agent_responses"])
        except (TypeError, ValueError):
            d["agent_responses"] = []
    else:
        d["agent_responses"] = []
    if d.get("state_history"):
        try:
            d["state_history"] = json.loads(d["state_history"])
        except (TypeError, ValueError):
            d["state_history"] = []
    else:
        d["state_history"] = []
    return d

def set_company_batch(
    batch_id: str,
    *,
    clear: bool = False,
    state: Optional[str] = None,
    limit: int = 0,
    sort_by: Optional[str] = None,
    scan_interval_hours: Optional[float] = None,
    candidate_id: Optional[str] = None,
    require_empty_website: bool = False,
    score_floor: Optional[float] = None,
    states: Optional[List[str]] = None,
    ) -> int:
    """Set batch_id on company rows: populate (claim) or clear.

    When clear=True: set batch_id and batch_created_at to NULL where batch_id matches. batch_id required.
    When clear=False: set batch_id, batch_created_at on up to limit rows where state=? AND batch_id IS NULL.
    candidate_id: when provided, scopes claim to companies belonging to this candidate.
    """
    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            if clear:
                cur = conn.execute(
                    "UPDATE company SET batch_id = NULL, batch_created_at = NULL WHERE batch_id = ?",
                    (batch_id,),
                )
                n = cur.rowcount
            else:
                if not state:
                    raise ValueError("state required when clear=False")
                claim_states = states if states is not None else [state]
                state_sql, state_params = _state_in_sql(claim_states)
                where_base = f"{state_sql} AND (batch_id IS NULL OR batch_id = '')"
                params: List[Any] = [batch_id, *state_params]
                if candidate_id is not None:
                    where_base += " AND candidate_id = ?"
                    params.append(candidate_id)
                if require_empty_website:
                    where_base += " AND (company_website IS NULL OR TRIM(company_website) = '')"
                if scan_interval_hours is not None:
                    where_base += " AND (last_scan_at IS NULL OR last_scan_at < datetime('now', '-' || ? || ' hours'))"
                    params.append(scan_interval_hours)
                if score_floor is not None:
                    score_key = ROSTER_CONFIG["company_data_keys"]["prefilter_score"]
                    where_base += (
                        f" AND json_extract(company_data, '$.{score_key}') IS NOT NULL"
                        f" AND CAST(json_extract(company_data, '$.{score_key}') AS REAL) >= ?"
                    )
                    params.append(float(score_floor))
                order_clause = (
                    f"ORDER BY {sort_by} ASC NULLS FIRST" if sort_by and sort_by in COMPANY_BATCH_SORT_COLUMNS
                    else "ORDER BY rowid"
                )
                _limit = int(limit) if limit else 0
                limit_clause = "LIMIT ?" if _limit > 0 else ""
                if _limit > 0:
                    params.append(_limit)
                cur = conn.execute(
                    f"""UPDATE company SET batch_id = ?, batch_created_at = datetime('now')
                       WHERE rowid IN (
                         SELECT rowid FROM company
                         WHERE {where_base}
                         {order_clause}
                         {limit_clause}
                       )""".strip(),
                    tuple(params),
                )
                n = cur.rowcount
            conn.commit()
            return n
        finally:
            conn.close()

    return _run_with_retry(_with_conn)

def get_company_batch(batch_id: str) -> List[Dict[str, Any]]:
    """Return companies with given batch_id as list of dicts (snake_case keys).
    Parses company_data and agent_responses JSON.
    """
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            cursor = conn.execute(
                "SELECT * FROM company WHERE batch_id = ?",
                (batch_id,),
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(_parse_company_row(_row_to_dict(row)))
            return result
        finally:
            conn.close()

    return _run_with_retry(_with_conn)

def save_company(
    short_name: str,
    state: str,
    company_website: Optional[str] = None,
    job_site: Optional[str] = None,
    company_name: Optional[str] = None,
    company_data: Optional[Dict[str, Any]] = None,
    agent_responses: Optional[List[Dict[str, Any]]] = None,
    batch_id: Optional[str] = None,
    batch_created_at: Optional[str] = None,
    last_scan_at: Optional[str] = None,
    state_history: Optional[List[Dict[str, Any]]] = None,
    candidate_id: Optional[str] = None,
    ) -> None:
    """Save or update company in database.

    When state=NEW, clears all existing jobs for this company from the job
    table to ensure fresh job detection (no false duplicates).
    Preserves batch_created_at, last_scan_at, and state_history from existing row when not provided.

    Args:
        short_name: Company short name (primary key)
        state: Company state (UPPERCASE from COMPANY_STATES)
        company_website: Original company website URL
        job_site: Job listing page URL
        company_name: Human-readable name (caller provides; roster derives from URL when creating)
        company_data: JSON-serializable blob (notes keyed by prompt index, parse_instructions)
        agent_responses: List of { timestamp, prompt_index, raw_response }
        batch_id: For batch locking
        last_scan_at: When None, preserved from existing row (avoids wiping on full save)
        state_history: JSON array of {to_state, timestamp, batch_id}; when None, preserved from existing
        candidate_id: When None, preserved from existing row (board placeholders set on first insert).

    Raises:
        ValueError: If short_name or state is missing, or state is invalid
        sqlite3.Error: On database connection or transaction failures
    """
    if not short_name or not short_name.strip():
        raise ValueError("short_name is required and cannot be empty")
    if not state or not state.strip():
        raise ValueError("state is required and cannot be empty")
    allowed = list(COMPANY_STATES.keys()) if COMPANY_STATES else []
    if not allowed or state not in allowed:
        raise ValueError(f"Invalid state '{state}'. Must be one of: {allowed}")

    if state == ASTRAL_CONFIG.get("company_state_clear_posting_jobs", "NEW"):
        _remove_jobs_by_company(short_name)

    try:
        company_data_json = json.dumps(company_data) if company_data is not None else "{}"
        agent_responses_json = json.dumps(agent_responses) if agent_responses is not None else "[]"
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize company_data or agent_responses to JSON: {e}") from e

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            _ensure_company_candidate_fk(conn)
            cursor = conn.execute(
                "SELECT batch_created_at, last_scan_at, state_history, candidate_id FROM company WHERE short_name = ?",
                (short_name,),
            )
            existing_row = cursor.fetchone()
            batch_created_at_val = batch_created_at if batch_created_at is not None else (
                existing_row["batch_created_at"] if existing_row else None
            )
            last_scan_at_val = last_scan_at if last_scan_at is not None else (
                existing_row["last_scan_at"] if existing_row else None
            )
            if candidate_id is not None:
                candidate_id_val = candidate_id
            else:
                candidate_id_val = (existing_row["candidate_id"] if existing_row else None)
            # state_history: caller-managed (overwrite when provided), preserve from existing when not
            if state_history is not None:
                state_history_json = json.dumps(state_history)
            elif existing_row and existing_row["state_history"]:
                state_history_json = existing_row["state_history"]
            else:
                state_history_json = "[]"
            conn.execute("""
                INSERT OR REPLACE INTO company
                (short_name, state, company_name, company_website, job_site, batch_id, batch_created_at,
                 last_scan_at, company_data, agent_responses, state_history, candidate_id,
                 created_at, updated_at, state_updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM company WHERE short_name = ?), CURRENT_TIMESTAMP), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                short_name,
                state,
                company_name,
                company_website,
                job_site,
                batch_id,
                batch_created_at_val,
                last_scan_at_val,
                company_data_json,
                agent_responses_json,
                state_history_json,
                candidate_id_val,
                short_name,
            ))
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise sqlite3.Error(f"Unexpected error saving company: {e}") from e
        finally:
            conn.close()

    _run_with_retry(_with_conn)

# TODO: merge update_company into save_company (add merge flag, match save_job pattern)
def update_company(short_name: str, **kwargs: Any) -> int:
    """Partial UPDATE: set only the columns passed. Allowlist enforced.
    company_data/agent_responses/state_history: dict/list serialized to JSON.
    updated_at auto-set to now if not in kwargs; state_updated_at set when state changes.
    Returns rowcount (0 or 1).
    """
    if not short_name or not short_name.strip():
        raise ValueError("short_name is required and cannot be empty")
    cols = [k for k in kwargs.keys() if k in _UPDATE_COMPANY_ALLOWED]
    if not cols:
        return 0
    now = _utc_now()
    if "updated_at" not in kwargs:
        cols.append("updated_at")
        kwargs["updated_at"] = now
    if "state" in kwargs and "state_updated_at" not in kwargs:
        cols.append("state_updated_at")
        kwargs["state_updated_at"] = now
    pairs = []
    params: List[Any] = []
    for c in cols:
        v = kwargs.get(c)
        if c in ("company_data", "agent_responses", "state_history") and v is not None:
            v = json.dumps(v) if not isinstance(v, str) else v
        pairs.append(f"{c} = ?")
        params.append(v)
    params.append(short_name)

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            _ensure_company_candidate_fk(conn)
            cur = conn.execute(
                f"UPDATE company SET {', '.join(pairs)} WHERE short_name = ?",
                tuple(params),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    return _run_with_retry(_with_conn)

def get_company(short_name: str) -> Optional[Dict[str, Any]]:
    """Select single company by short_name. Returns dict with snake_case keys or None."""
    if not short_name or not short_name.strip():
        return None

    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            cursor = conn.execute(
                "SELECT * FROM company WHERE short_name = ?",
                (short_name,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return _parse_company_row(_row_to_dict(row))
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_companies(
    states: Optional[List[str]] = None,
    exclude_states: Optional[List[str]] = None,
    candidate_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List companies with optional state IN/NOT IN filters and candidate_id scope."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            _ensure_company_candidate_fk(conn)
            clauses: List[str] = []
            params: List[Any] = []
            if states:
                clauses.append(f"state IN ({','.join('?' for _ in states)})")
                params.extend(states)
            if exclude_states:
                clauses.append(f"state NOT IN ({','.join('?' for _ in exclude_states)})")
                params.extend(exclude_states)
            if candidate_id:
                clauses.append("candidate_id = ?")
                params.append(candidate_id)
            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            rows = conn.execute(f"SELECT * FROM company{where} ORDER BY updated_at DESC", params).fetchall()
            return [_parse_company_row(_row_to_dict(r)) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def count_companies(
    states: Optional[List[str]] = None,
    exclude_states: Optional[List[str]] = None,
    candidate_id: Optional[str] = None,
) -> int:
    """COUNT(*) version of list_companies -- avoids fetching full rows just for length."""
    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            clauses: List[str] = []
            params: List[Any] = []
            if states:
                clauses.append(f"state IN ({','.join('?' for _ in states)})")
                params.extend(states)
            if exclude_states:
                clauses.append(f"state NOT IN ({','.join('?' for _ in exclude_states)})")
                params.extend(exclude_states)
            if candidate_id:
                clauses.append("candidate_id = ?")
                params.append(candidate_id)
            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            row = conn.execute(f"SELECT COUNT(*) FROM company{where}", params).fetchone()
            return row[0] if row else 0
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_active_trigger_states(candidate_id: str, entity_type: str) -> List[str]:
    """Return trigger_states for auto_mode dispatch_tasks for this candidate+entity_type."""
    def _with_conn() -> List[str]:
        conn = _get_connection()
        try:
            _ensure_dispatch_task_schema(conn)
            rows = conn.execute(
                "SELECT DISTINCT trigger_state FROM dispatch_task "
                "WHERE auto_mode = 1 AND entity_type = ? AND candidate_id = ? AND trigger_state IS NOT NULL",
                (entity_type, candidate_id),
            ).fetchall()
            return [r[0] for r in rows if r[0]]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def list_company_job_scans(candidate_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return gazer scan outcomes joined with company name, ordered by scan_completed_at DESC."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_company_job_scan_schema(conn)
            _ensure_company_schema(conn)
            _ensure_company_candidate_fk(conn)
            sql = """
                SELECT s.batch_id, s.short_name, c.company_name, s.scan_completed_at,
                       s.total_found, s.new, s.duplicates, s.title_mismatch, s.status, s.failure_message
                FROM company_job_scan s
                LEFT JOIN company c ON s.short_name = c.short_name
            """
            params: List[Any] = []
            if candidate_id:
                sql += " WHERE c.candidate_id = ?"
                params.append(candidate_id)
            sql += " ORDER BY s.scan_completed_at DESC"
            rows = conn.execute(sql, params).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


# ---- Job ----

# Allowed sort columns for job batch (avoid SQL injection)
_JOB_BATCH_SORT_COLUMNS = frozenset({"rowid", "created_at", "updated_at", "state_changed_at", "latest_score"})

def _remove_jobs_by_company(company: str) -> int:
    """Remove all jobs for a company from the job table.
    
    Args:
        company: Company shortname
    
    Returns:
        Number of records deleted
    """
    if not company:
        return 0
    
    conn = _get_connection()
    try:
        _ensure_job_schema(conn)
        cursor = conn.execute("DELETE FROM job WHERE company = ?", (company,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def _ensure_job_schema(conn: sqlite3.Connection) -> None:
    """Create job table for raw_job_listing ingest if not present. Idempotent."""
    global _job_schema_ensured
    if _job_schema_ensured:
        return
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job (
            astral_job_id TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            company_job_id TEXT,
            job_title TEXT,
            job_link TEXT,
            job_data TEXT,
            state TEXT NOT NULL,
            state_history TEXT,
            batch_id TEXT,
            batch_created_at TEXT,
            created_at TEXT,
            updated_at TEXT,
            state_changed_at TEXT
        )
    """)
    conn.commit()
    # Migration: add missing columns on existing databases
    cursor = conn.execute("PRAGMA table_info(job)")
    cols = {row[1] for row in cursor.fetchall()}
    for col, col_def in [
        ("job_link", "TEXT"),
        ("agent_responses", "TEXT DEFAULT '[]'"),
        ("latest_score", "REAL"),            # AST-350: latest numeric score for batch priority sorting
        ("board_search_id", "TEXT"),
    ]:
        if col not in cols:
            try:
                conn.execute(f"ALTER TABLE job ADD COLUMN {col} {col_def}")
                conn.commit()
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
    # AST-479: LIKE passes stay PASSED_LIKE for analysis_upshot queue; do not auto-promote to BUILD_ARTIFACTS.
    _job_schema_ensured = True

def get_company_job_counts(short_name: str) -> Dict[str, int]:
    """Return {state: count} for all jobs belonging to company short_name."""
    def _with_conn() -> Dict[str, int]:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            rows = conn.execute(
                "SELECT state, COUNT(*) FROM job WHERE company = ? GROUP BY state",
                (short_name,),
            ).fetchall()
            return {row[0]: row[1] for row in rows}
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_agent_data_for_ids(ids: List[str]) -> Dict[str, Any]:
    """Return {agent_data_id: row_dict} for a list of IDs. block_data is decompressed.
    Returns {} if ids is empty (no query issued)."""
    if not ids:
        return {}

    def _with_conn() -> Dict[str, Any]:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            placeholders = ",".join("?" for _ in ids)
            rows = conn.execute(
                f"SELECT * FROM agent_data WHERE agent_data_id IN ({placeholders})", ids
            ).fetchall()
            result = {}
            for row in rows:
                d = _row_to_dict(row)
                d["block_data"] = _decompress_payload(d["block_data"])
                result[d["agent_data_id"]] = d
            return result
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_company_job_ids(company: str) -> List[str]:
    """Return list of company_job_id for company (excludes NULL). For dedup / inverted match."""
    def _do(c: sqlite3.Connection) -> List[str]:
        _ensure_job_schema(c)
        cursor = c.execute(
            "SELECT company_job_id FROM job WHERE company = ? AND company_job_id IS NOT NULL",
            (company,),
        )
        return [row[0] for row in cursor.fetchall()]

    conn = _get_connection()
    try:
        return _do(conn)
    finally:
        conn.close()

def save_job(
    astral_job_id: str,
    *,
    company: Optional[str] = None,
    state: Optional[str] = None,
    company_job_id: Optional[str] = None,
    job_title: Optional[str] = None,
    job_link: Optional[str] = None,
    job_data: Optional[Dict[str, Any]] = None,
    merge: bool = True,
    state_history: Optional[List[Dict[str, Any]]] = None,
    state_changed_at: Optional[str] = None,
    latest_score: Optional[float] = None,
    board_search_id: Optional[str] = None,
    ) -> None:
    """Upsert a job row. Insert if new (company and state required); update provided fields if exists.
    job_data: merge=True deep-merges with existing; merge=False overwrites.
    state_history: always overwrites (caller manages append via get_job + append + save_job).
    latest_score: most recent numeric grade score (0-10); written through for batch priority sorting (AST-350).
    Raises ValueError if inserting without company/state."""
    now = _utc_now()

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            existing = conn.execute(
                "SELECT astral_job_id, job_data FROM job WHERE astral_job_id = ?",
                (astral_job_id,),
            ).fetchone()

            if existing is None:
                # INSERT: company and state required (NOT NULL in schema)
                if not company:
                    raise ValueError("company required for new job")
                if not state:
                    raise ValueError("state required for new job")
                jdata_str = json.dumps(job_data) if job_data else "{}"
                hist_str = json.dumps(state_history) if state_history else "[]"
                conn.execute(
                    """INSERT INTO job (
                        astral_job_id, company, company_job_id, job_title, job_link, job_data,
                        state, state_history, batch_id, batch_created_at,
                        board_search_id, created_at, updated_at, state_changed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?)""",
                    (astral_job_id, company, company_job_id, job_title, job_link, jdata_str,
                     state, hist_str, board_search_id, now, now, state_changed_at or now),
                )
            else:
                # UPDATE: only set provided (non-None) fields
                sets: List[str] = []
                params: List[Any] = []
                for col, val in [
                    ("company", company), ("state", state),
                    ("company_job_id", company_job_id), ("job_title", job_title),
                    ("job_link", job_link), ("state_changed_at", state_changed_at),
                    ("latest_score", latest_score), ("board_search_id", board_search_id),
                ]:
                    if val is not None:
                        sets.append(f"{col} = ?")
                        params.append(val)
                # job_data: merge or overwrite
                if job_data is not None:
                    if merge:
                        existing_data = json.loads(existing["job_data"]) if existing["job_data"] else {}
                        _deep_merge(existing_data, job_data)
                        sets.append("job_data = ?")
                        params.append(json.dumps(existing_data))
                    else:
                        sets.append("job_data = ?")
                        params.append(json.dumps(job_data))
                # state_history: always overwrite (caller manages append)
                if state_history is not None:
                    sets.append("state_history = ?")
                    params.append(json.dumps(state_history))
                if not sets:
                    return
                sets.append("updated_at = ?")
                params.append(now)
                params.append(astral_job_id)
                conn.execute(
                    f"UPDATE job SET {', '.join(sets)} WHERE astral_job_id = ?",
                    tuple(params),
                )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)

def get_job(astral_job_id: str) -> Optional[Dict[str, Any]]:
    """Select single job by astral_job_id. Returns dict with parsed job_data/state_history, or None."""
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            row = conn.execute(
                "SELECT * FROM job WHERE astral_job_id = ?", (astral_job_id,)
            ).fetchone()
            return _job_row_to_dict(row) if row else None
        finally:
            conn.close()

    return _run_with_retry(_with_conn)

def _job_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Turn job table row into dict; parse job_data, state_history, agent_responses JSON."""
    out = {k: row[k] for k in row.keys()}
    for col in ("job_data", "state_history", "agent_responses"):
        val = out.get(col)
        if isinstance(val, str) and val:
            try:
                out[col] = json.loads(val)
            except json.JSONDecodeError:
                out[col] = val
        elif val is None or val == "":
            out[col] = {} if col == "job_data" else []
    return out

def raw_job_listing_is_duplicate(company: str, raw_job_listing: str) -> bool:
    """Inverted pattern match (AST-80): True if raw_job_listing contains any existing company_job_id for company."""
    def _do(c: sqlite3.Connection) -> bool:
        _ensure_job_schema(c)
        cursor = c.execute(
            """SELECT 1 FROM job WHERE company = ? AND company_job_id IS NOT NULL
               AND ? LIKE '%' || company_job_id || '%' LIMIT 1""",
            (company, raw_job_listing),
        )
        return cursor.fetchone() is not None

    conn = _get_connection()
    try:
        return _do(conn)
    finally:
        conn.close()

def claim_job_batch(
    batch_id: str, state: str, limit: int, sort_by: Optional[str] = None,
    candidate_id: Optional[str] = None,
    score_floor: Optional[float] = None,
    *,
    claim_cap: Optional[int] = None,
    states: Optional[List[str]] = None,
    ) -> int:
    """Claim up to limit unclaimed jobs in state. Sets batch_id, batch_created_at.
    Parameter order: batch_id first (caller owns it).
    candidate_id: when provided, scopes claim to jobs whose company belongs to this candidate.
    claim_cap: when set (dispatcher AST-502 exhaustion), SQLITE LIMIT uses this count instead of
    ``limit`` — claim exactly up to concurrent eligible rows; ``limit`` stays the API chunk width from dispatch_task.batch_size elsewhere.
    Returns count claimed."""
    now = _utc_now()
    claim_states = states if states is not None else [state]
    state_sql, state_params = _state_in_sql(claim_states)
    # latest_score: highest score first; ties and NULLs break by newest state_changed_at
    order_clause = (
        "ORDER BY latest_score DESC NULLS LAST, state_changed_at DESC" if sort_by == "latest_score"
        else f"ORDER BY {sort_by} ASC NULLS FIRST" if sort_by and sort_by in _JOB_BATCH_SORT_COLUMNS
        else "ORDER BY rowid"
    )
    candidate_filter = (
        " AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)"
        if candidate_id else ""
    )
    score_filter = " AND latest_score IS NOT NULL AND latest_score >= ?" if score_floor is not None else ""

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            eff_limit = int(claim_cap) if claim_cap is not None else int(limit)
            params = [batch_id, now, *state_params]
            if candidate_id:
                params.append(candidate_id)
            if score_floor is not None:
                params.append(float(score_floor))
            params.append(eff_limit)
            # Unclaimed must match count_eligible / count_entities: NULL or '' (legacy empty string).
            cur = conn.execute(
                f"""UPDATE job SET batch_id = ?, batch_created_at = ?
                   WHERE astral_job_id IN (
                     SELECT astral_job_id FROM job
                     WHERE {state_sql} AND (batch_id IS NULL OR batch_id = '')
                     {candidate_filter}
                     {score_filter}
                     {order_clause}
                     LIMIT ?
                   )""",
                tuple(params),
            )
            n = cur.rowcount
            conn.commit()
            return n
        finally:
            conn.close()

    return _run_with_retry(_with_conn)

def get_job_batch(batch_id: str) -> List[Dict[str, Any]]:
    """Return full job records for batch_id (job_data and state_history parsed)."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            cursor = conn.execute("SELECT j.*, c.job_site FROM job j LEFT JOIN company c ON j.company = c.short_name WHERE j.batch_id = ?", (batch_id,))
            return [_job_row_to_dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)

def clear_job_batch(batch_id: str) -> int:
    """Release batch: set batch_id and batch_created_at to NULL. Returns count released."""
    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            cur = conn.execute(
                "UPDATE job SET batch_id = NULL, batch_created_at = NULL WHERE batch_id = ?",
                (batch_id,),
            )
            n = cur.rowcount
            conn.commit()
            return n
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def clear_job_batch_lock(astral_job_id: str) -> None:
    """Clear batch_id and batch_created_at for one job row (candidate cancel during BUILD_ARTIFACTS)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            conn.execute(
                "UPDATE job SET batch_id = NULL, batch_created_at = NULL, updated_at = ? WHERE astral_job_id = ?",
                (now, astral_job_id),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def list_jobs(
    states: Optional[List[str]] = None,
    candidate_id: Optional[str] = None,
    order_by: str = "state_changed_at",
) -> List[Dict[str, Any]]:
    """List jobs with optional state IN filter and candidate_id scope.
    candidate_id scopes via subquery on the company table (same pattern as claim_job_batch).
    order_by: column name; falls back to rowid if not a known sortable column."""
    _SORTABLE = {"state_changed_at", "created_at", "updated_at", "job_title", "company", "state"}

    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            clauses: List[str] = []
            params: List[Any] = []
            if states:
                clauses.append(f"state IN ({','.join('?' for _ in states)})")
                params.extend(states)
            if candidate_id:
                clauses.append("company IN (SELECT short_name FROM company WHERE candidate_id = ?)")
                params.append(candidate_id)
            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            col = order_by if order_by in _SORTABLE else "rowid"
            rows = conn.execute(
                f"SELECT * FROM job{where} ORDER BY {col} DESC NULLS LAST", params
            ).fetchall()
            return [_job_row_to_dict(r) for r in rows]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def count_jobs(
    states: Optional[List[str]] = None,
    candidate_id: Optional[str] = None,
) -> int:
    """COUNT(*) version of list_jobs — avoids fetching full rows just for length."""
    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            clauses: List[str] = []
            params: List[Any] = []
            if states:
                clauses.append(f"state IN ({','.join('?' for _ in states)})")
                params.extend(states)
            if candidate_id:
                clauses.append("company IN (SELECT short_name FROM company WHERE candidate_id = ?)")
                params.append(candidate_id)
            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            row = conn.execute(f"SELECT COUNT(*) FROM job{where}", params).fetchone()
            return row[0] if row else 0
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def score_floor_by_trigger_for_candidate(candidate_id: str) -> Dict[str, float]:
    """trigger_state -> numeric floor for this candidate's job dispatch_task rows.
    Aligns with count_eligible_for_dispatch_task / claim_job_batch (scored + default 1.0).
    When several rows share a trigger_state, the maximum floor wins (strictest gate)."""
    floors: Dict[str, float] = {}
    for t in list_dispatch_tasks():
        if t.get("candidate_id") != candidate_id or t.get("entity_type") != "job":
            continue
        ts = t.get("trigger_state")
        if not ts or ts not in PASSED_SCORE_GATED_STATES:
            continue
        task_key = t.get("task_key") or ""
        is_scored = trigger_state_used_by_scored_dispatch_task(ts)
        if not is_scored:
            continue
        eff = float(t["score_floor"]) if t.get("score_floor") is not None else 1.0
        floors[ts] = max(floors.get(ts, eff), eff)
    return floors


def job_misses_dispatch_score_floor(job: Dict[str, Any], floors: Dict[str, float]) -> bool:
    """True iff job.state has a configured floor and latest_score is null or below it (unclaimable)."""
    st = job.get("state")
    if st not in floors:
        return False
    fl = floors[st]
    ls = job.get("latest_score")
    if ls is None:
        return True
    return float(ls) < float(fl)


def count_jobs_below_dispatch_score_floor(candidate_id: str) -> int:
    """How many PASSED_* jobs are stuck under their next scored dispatch_task.score_floor."""
    floors = score_floor_by_trigger_for_candidate(candidate_id)
    if not floors:
        return 0

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            total = 0
            for st, fl in floors.items():
                row = conn.execute(
                    """SELECT COUNT(*) FROM job WHERE state = ?
                       AND (latest_score IS NULL OR latest_score < ?)
                       AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)""",
                    (st, float(fl), candidate_id),
                ).fetchone()
                total += int(row[0] or 0)
            return total
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_jobs_below_dispatch_score_floor(candidate_id: str) -> List[Dict[str, Any]]:
    """PASSED_JD / PASSED_DO / PASSED_GET rows that would not be claimed due to score_floor."""
    floors = score_floor_by_trigger_for_candidate(candidate_id)
    if not floors:
        return []
    states = [s for s in floors if s in PASSED_SCORE_GATED_STATES]
    if not states:
        return []
    rows = list_jobs(states=states, candidate_id=candidate_id, order_by="state_changed_at")
    return [r for r in rows if job_misses_dispatch_score_floor(r, floors)]


# ---- Timesheets ----

def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return (
        conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
            (name,),
        ).fetchone()[0]
        > 0
    )


def _create_anthropic_timesheets_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE anthropic_timesheets (
            anthropic_req_id TEXT UNIQUE,
            task_key_uuid TEXT,
            model_code TEXT,
            candidate_id TEXT,
            batch_id TEXT,
            batch_size INTEGER DEFAULT 1,
            cache_write_tokens INTEGER DEFAULT 0,
            cache_read_tokens INTEGER DEFAULT 0,
            no_cache_prompt_tokens INTEGER DEFAULT 0,
            no_cache_live_tokens INTEGER DEFAULT 0,
            total_no_cache_input_tokens INTEGER DEFAULT 0,
            total_output_tokens INTEGER DEFAULT 0,
            calc_cost_cache_write REAL DEFAULT 0,
            calc_cost_cache_read REAL DEFAULT 0,
            calc_cost_no_cache_input REAL DEFAULT 0,
            calc_cost_output REAL DEFAULT 0,
            agent_performance TEXT,
            failure_note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _create_agent_timesheets_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE agent_timesheets (
            agent_req_id TEXT UNIQUE,
            task_key_uuid TEXT,
            model_code TEXT,
            candidate_id TEXT,
            batch_id TEXT,
            batch_size INTEGER DEFAULT 1,
            cache_write_tokens INTEGER DEFAULT 0,
            cache_read_tokens INTEGER DEFAULT 0,
            no_cache_prompt_tokens INTEGER DEFAULT 0,
            no_cache_live_tokens INTEGER DEFAULT 0,
            total_no_cache_input_tokens INTEGER DEFAULT 0,
            total_output_tokens INTEGER DEFAULT 0,
            calc_cost_cache_write REAL DEFAULT 0,
            calc_cost_cache_read REAL DEFAULT 0,
            calc_cost_no_cache_input REAL DEFAULT 0,
            calc_cost_output REAL DEFAULT 0,
            agent_performance TEXT,
            failure_note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _ensure_timesheets_schema(conn: sqlite3.Connection) -> None:
    """Create anthropic_timesheets + agent_timesheets; rename legacy ``timesheets``; migrate pre-AST-324 v1."""
    global _timesheets_schema_ensured
    if _timesheets_schema_ensured:
        return

    # Legacy single-table name → Anthropic-only ledger (AST-494)
    if _table_exists(conn, "timesheets") and not _table_exists(conn, "anthropic_timesheets"):
        conn.execute("ALTER TABLE timesheets RENAME TO anthropic_timesheets")
        conn.commit()

    # Pre-AST-324 rows (no anthropic_req_id): rebuild anthropic_timesheets from archived v1 snapshot
    if _table_exists(conn, "anthropic_timesheets"):
        cols = {row[1] for row in conn.execute("PRAGMA table_info(anthropic_timesheets)").fetchall()}
        if "anthropic_req_id" not in cols:
            conn.execute("ALTER TABLE anthropic_timesheets RENAME TO timesheets_v1")
            _create_anthropic_timesheets_table(conn)
            conn.execute("""
                INSERT INTO anthropic_timesheets (
                    anthropic_req_id, candidate_id, batch_id,
                    cache_write_tokens, cache_read_tokens,
                    total_no_cache_input_tokens, total_output_tokens,
                    agent_performance, created_at
                )
                SELECT
                    request_id, candidate_id, batch_id,
                    COALESCE(cache_creation_tokens, 0), COALESCE(cache_read_tokens, 0),
                    COALESCE(tokens_input, 0), COALESCE(tokens_output, 0),
                    NULL, created_at
                FROM timesheets_v1
                WHERE request_id IS NOT NULL
            """)
            conn.commit()

    if not _table_exists(conn, "anthropic_timesheets"):
        _create_anthropic_timesheets_table(conn)
        conn.commit()

    if not _table_exists(conn, "agent_timesheets"):
        _create_agent_timesheets_table(conn)
        conn.commit()

    n_agent = conn.execute("SELECT COUNT(*) FROM agent_timesheets").fetchone()[0]
    n_anth = conn.execute("SELECT COUNT(*) FROM anthropic_timesheets").fetchone()[0]
    # One-shot backfill: historical Anthropic rows → unified ledger (preserve UNIQUE via OR IGNORE)
    if n_agent == 0 and n_anth > 0:
        conn.execute("""
            INSERT OR IGNORE INTO agent_timesheets (
                agent_req_id, task_key_uuid, model_code, candidate_id, batch_id, batch_size,
                cache_write_tokens, cache_read_tokens, no_cache_prompt_tokens, no_cache_live_tokens,
                total_no_cache_input_tokens, total_output_tokens,
                calc_cost_cache_write, calc_cost_cache_read, calc_cost_no_cache_input, calc_cost_output,
                agent_performance, failure_note, created_at
            )
            SELECT
                anthropic_req_id, task_key_uuid, model_code, candidate_id, batch_id, batch_size,
                cache_write_tokens, cache_read_tokens, no_cache_prompt_tokens, no_cache_live_tokens,
                total_no_cache_input_tokens, total_output_tokens,
                calc_cost_cache_write, calc_cost_cache_read, calc_cost_no_cache_input, calc_cost_output,
                agent_performance, failure_note, created_at
            FROM anthropic_timesheets
        """)
        conn.commit()

    _timesheets_schema_ensured = True


def _add_timesheet_entry(
    agent_req_id: Optional[str],
    task_key_uuid: Optional[str],
    model_code: Optional[str],
    candidate_id: Optional[str],
    batch_id: Optional[str],
    batch_size: int,
    cache_write_tokens: int,
    cache_read_tokens: int,
    no_cache_prompt_tokens: int,
    no_cache_live_tokens: int,
    total_no_cache_input_tokens: int,
    total_output_tokens: int,
    calc_cost_cache_write: float,
    calc_cost_cache_read: float,
    calc_cost_no_cache_input: float,
    calc_cost_output: float,
    agent_performance: Optional[str] = None,
    failure_note: Optional[str] = None,
    provider: str = "anthropic",
) -> bool:
    """Anthropic completions mirror into anthropic_timesheets + agent_timesheets; other providers use agent_timesheets only."""
    if provider not in ALLOWED_TIMESHEET_PROVIDERS:
        raise ValueError(f"Invalid timesheet provider {provider!r}")
    row_vals = (
        agent_req_id, task_key_uuid, model_code, candidate_id, batch_id, batch_size,
        cache_write_tokens, cache_read_tokens, no_cache_prompt_tokens, no_cache_live_tokens,
        total_no_cache_input_tokens, total_output_tokens,
        calc_cost_cache_write, calc_cost_cache_read, calc_cost_no_cache_input, calc_cost_output,
        agent_performance, failure_note,
    )
    conn = _get_connection()
    try:
        _ensure_timesheets_schema(conn)
        conn.execute("""
            INSERT OR IGNORE INTO agent_timesheets (
                agent_req_id, task_key_uuid, model_code, candidate_id, batch_id, batch_size,
                cache_write_tokens, cache_read_tokens, no_cache_prompt_tokens, no_cache_live_tokens,
                total_no_cache_input_tokens, total_output_tokens,
                calc_cost_cache_write, calc_cost_cache_read, calc_cost_no_cache_input, calc_cost_output,
                agent_performance, failure_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row_vals)
        if provider == "anthropic":
            conn.execute("""
                INSERT OR IGNORE INTO anthropic_timesheets (
                    anthropic_req_id, task_key_uuid, model_code, candidate_id, batch_id, batch_size,
                    cache_write_tokens, cache_read_tokens, no_cache_prompt_tokens, no_cache_live_tokens,
                    total_no_cache_input_tokens, total_output_tokens,
                    calc_cost_cache_write, calc_cost_cache_read, calc_cost_no_cache_input, calc_cost_output,
                    agent_performance, failure_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row_vals)
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def backfill_deepseek_agent_timesheet_costs() -> int:
    """Recompute calc_cost_* for all agent_timesheets rows with DeepSeek model_code keys."""
    model_codes = tuple(DEEPSEEK_MODEL_PRICING.keys())
    if not model_codes:
        return 0
    placeholders = ",".join("?" for _ in model_codes)

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_timesheets_schema(conn)
            rows = conn.execute(
                f"""
                SELECT agent_req_id, model_code, cache_write_tokens, cache_read_tokens,
                       total_no_cache_input_tokens, total_output_tokens
                FROM agent_timesheets
                WHERE model_code IN ({placeholders})
                """,
                model_codes,
            ).fetchall()
            updated = 0
            for row in rows:
                parts = calculate_cost_components_deepseek_from_counts(
                    row["cache_read_tokens"],
                    row["total_no_cache_input_tokens"],
                    row["total_output_tokens"],
                    row["cache_write_tokens"],
                    row["model_code"],
                )
                conn.execute(
                    """
                    UPDATE agent_timesheets
                    SET calc_cost_cache_write = ?,
                        calc_cost_cache_read = ?,
                        calc_cost_no_cache_input = ?,
                        calc_cost_output = ?
                    WHERE agent_req_id = ?
                    """,
                    (
                        parts["calc_cost_cache_write"],
                        parts["calc_cost_cache_read"],
                        parts["calc_cost_no_cache_input"],
                        parts["calc_cost_output"],
                        row["agent_req_id"],
                    ),
                )
                updated += 1
            conn.commit()
            return updated
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_timesheets(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    task_key_uuid: Optional[str] = None,
    batch_id: Optional[str] = None,
    candidate_id: Optional[str] = None,
    model_code: Optional[str] = None,
    agent_performance: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query timesheets with optional filters. All params optional; returns newest first.
    date_to is inclusive (through end of day)."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_timesheets_schema(conn)
            clauses: List[str] = []
            params: List[Any] = []
            if date_from:
                clauses.append("created_at >= ?")
                params.append(date_from)
            if date_to:
                clauses.append("created_at <= ?")
                params.append(f"{date_to}T23:59:59")
            if task_key_uuid:
                clauses.append("task_key_uuid = ?")
                params.append(task_key_uuid)
            if batch_id:
                clauses.append("batch_id = ?")
                params.append(batch_id)
            if candidate_id:
                clauses.append("candidate_id = ?")
                params.append(candidate_id)
            if model_code:
                clauses.append("model_code = ?")
                params.append(model_code)
            if agent_performance:
                clauses.append("agent_performance = ?")
                params.append(agent_performance)
            where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
            rows = conn.execute(
                f"SELECT * FROM agent_timesheets{where} ORDER BY created_at DESC", params
            ).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def sum_cost_by_batch(batch_ids: List[str]) -> Dict[str, float]:
    """Return {batch_id: total_calc_cost} for the given batch IDs."""
    if not batch_ids:
        return {}
    def _with_conn() -> Dict[str, float]:
        conn = _get_connection()
        try:
            _ensure_timesheets_schema(conn)
            placeholders = ",".join("?" for _ in batch_ids)
            rows = conn.execute(
                f"""SELECT batch_id,
                    SUM(calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output) AS total
                    FROM agent_timesheets WHERE batch_id IN ({placeholders}) GROUP BY batch_id""",
                batch_ids,
            ).fetchall()
            return {r["batch_id"]: r["total"] for r in rows}
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


# ---- Agent Responses ----

# Compress/decompress helpers for agent_responses payloads.
# New records store raw_response/parsed_response/runtime_prompt as zlib-compressed BLOBs.
# Legacy records remain as plain TEXT. The read path handles both transparently.

def _compress_payload(data: Any) -> Optional[bytes]:
    """JSON-serialize then zlib-compress. Returns None for None input."""
    if data is None:
        return None
    text = json.dumps(data) if not isinstance(data, str) else data
    return zlib.compress(text.encode("utf-8"))


def _decompress_payload(value: Any) -> Optional[str]:
    """Decompress a stored payload back to a JSON string.
    Handles both compressed (bytes/BLOB) and legacy uncompressed (str/TEXT)."""
    if value is None:
        return None
    if isinstance(value, bytes):
        return zlib.decompress(value).decode("utf-8")
    return value  # legacy TEXT row


def _ensure_agent_responses_schema(conn: sqlite3.Connection) -> None:
    """Create agent_responses table if not present. Idempotent.
    Adds status, failure_note columns on existing tables that lack them."""
    global _agent_responses_schema_ensured
    if _agent_responses_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='agent_responses'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE agent_responses (
                id TEXT PRIMARY KEY,
                task_key TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                status TEXT,
                failure_note TEXT,
                raw_response BLOB,
                parsed_response BLOB,
                runtime_prompt BLOB,
                request_id TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX idx_agent_responses_entity ON agent_responses(entity_type, entity_id)"
        )
        conn.commit()
    else:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(agent_responses)").fetchall()}
        altered = False
        for col in ("runtime_prompt", "status", "failure_note"):
            if col not in cols:
                conn.execute(f"ALTER TABLE agent_responses ADD COLUMN {col} TEXT")
                altered = True
        if altered:
            conn.commit()
    _agent_responses_schema_ensured = True

def _derive_agent_status(raw_response: Any, parsed_response: Any) -> Tuple[str, Optional[str]]:
    """Derive (status, failure_note) for the top-level queryable columns.
    parsed_response present → success. Otherwise extract from agent_performance envelope."""
    if parsed_response is not None:
        return ("success", None)
    if isinstance(raw_response, dict):
        perf = raw_response.get("agent_performance")
        if isinstance(perf, dict):
            note = perf.get("failure_note")
            if note:
                return ("error", str(note)[:1000])
    return ("error", None)


def add_agent_response_entry(
    task_key: str,
    entity_type: str,
    entity_id: str,
    raw_response: Any,
    parsed_response: Optional[Any] = None,
    runtime_prompt: Optional[Any] = None,
    request_id: Optional[str] = None
    ) -> bool:
    """Add an agent response to the database. Insert-only, non-blocking on failure.
    Extracts status/failure_note to queryable columns; compresses payloads as BLOBs.

    Args:
        task_key: Task name (e.g. prefilter_company, select_job_page)
        entity_type: 'company' or 'job'
        entity_id: short_name or job_id (from do_task index)
        raw_response: Full response dict (will be compressed)
        parsed_response: Parsed/validated response if available (will be compressed)
        runtime_prompt: Prompt blocks sent to the API (will be compressed)
        request_id: Optional Anthropic API request ID for timesheet link

    Returns:
        True if added successfully, False if error occurred
    """
    entry_id = str(uuid.uuid4())
    now = _utc_now()
    status, failure_note = _derive_agent_status(raw_response, parsed_response)
    raw_blob = _compress_payload(raw_response) if raw_response is not None else _compress_payload({})
    parsed_blob = _compress_payload(parsed_response)
    prompt_blob = _compress_payload(runtime_prompt)
    conn = _get_connection()
    try:
        _ensure_agent_responses_schema(conn)
        conn.execute("""
            INSERT INTO agent_responses
            (id, task_key, entity_type, entity_id, status, failure_note,
             raw_response, parsed_response, runtime_prompt, request_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry_id, task_key, entity_type, entity_id, status, failure_note,
              raw_blob, parsed_blob, prompt_blob, request_id, now))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def list_agent_responses(entity_type: str, entity_id: str) -> List[Dict[str, Any]]:
    """Return all agent_responses for an entity, ordered by created_at ascending.
    Decompresses payload columns transparently (handles both legacy TEXT and compressed BLOB)."""
    _PAYLOAD_COLS = ("raw_response", "parsed_response", "runtime_prompt")

    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_responses_schema(conn)
            rows = conn.execute(
                "SELECT * FROM agent_responses WHERE entity_type = ? AND entity_id = ? ORDER BY created_at ASC",
                (entity_type, entity_id),
            ).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                for col in _PAYLOAD_COLS:
                    if col in d:
                        d[col] = _decompress_payload(d[col])
                results.append(d)
            return results
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


# ---- Company Job Scan ----

def _ensure_company_job_scan_schema(conn: sqlite3.Connection) -> None:
    """Create company_job_scan table if not present. Idempotent."""
    global _company_job_scan_schema_ensured
    if _company_job_scan_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='company_job_scan'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE company_job_scan (
                batch_id TEXT NOT NULL,
                short_name TEXT NOT NULL,
                scan_completed_at TIMESTAMP NOT NULL,
                total_found INTEGER,
                new INTEGER,
                duplicates INTEGER,
                title_mismatch INTEGER,
                status TEXT NOT NULL,
                failure_message TEXT,
                PRIMARY KEY (batch_id, short_name)
            )
        """)
        conn.commit()
    cols = {row[1] for row in conn.execute("PRAGMA table_info(company_job_scan)").fetchall()}
    if "title_mismatch" not in cols:
        conn.execute("ALTER TABLE company_job_scan ADD COLUMN title_mismatch INTEGER")
        conn.commit()
    _company_job_scan_schema_ensured = True

def record_to_company_job_scan(
    batch_id: str,
    short_name: str,
    scan_completed_at: str,
    total_found: Optional[int] = None,
    new: Optional[int] = None,
    duplicates: Optional[int] = None,
    title_mismatch: Optional[int] = None,
    status: str = "success",
    failure_message: Optional[str] = None,
    ) -> None:
    """Insert one scan outcome row. Data layer is dumb: records what core passes."""
    if status not in ("success", "failure"):
        raise ValueError(f"status must be 'success' or 'failure', got {status!r}")

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_company_job_scan_schema(conn)
            conn.execute(
                """INSERT INTO company_job_scan
                   (batch_id, short_name, scan_completed_at, total_found, new, duplicates, title_mismatch, status, failure_message)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (batch_id, short_name, scan_completed_at, total_found, new, duplicates, title_mismatch, status, failure_message),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


# ---- Candidate ----

def _ensure_candidate_schema(conn: sqlite3.Connection) -> None:
    """Create candidate table if not present; add candidate_api_key if missing. Idempotent.
    astral_candidate_id is lowercase last name (e.g. 'somerset'), same convention as company short_name."""
    global _candidate_schema_ensured
    if _candidate_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='candidate'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE candidate (
                astral_candidate_id TEXT PRIMARY KEY,
                state TEXT NOT NULL DEFAULT 'NEW',
                candidate_data TEXT,
                candidate_api_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                state_changed_at TIMESTAMP
            )
        """)
        conn.commit()
    else:
        # Idempotent migration: add missing columns on existing databases
        cols = {row[1] for row in conn.execute("PRAGMA table_info(candidate)").fetchall()}
        for col, col_def in [("candidate_api_key", "TEXT"), ("agent_responses", "TEXT DEFAULT '[]'")]:
            if col not in cols:
                try:
                    conn.execute(f"ALTER TABLE candidate ADD COLUMN {col} {col_def}")
                    conn.commit()
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        raise
    _migrate_candidate_data_structure(conn)
    _migrate_pronoun_preference_backfill(conn)
    _migrate_context_arrays_to_text(conn)
    _candidate_schema_ensured = True


def _migrate_candidate_data_structure(conn: sqlite3.Connection) -> None:
    """One-time migration: restructure candidate_data from flat/mixed layout into
    profile/context/artifacts groups. Idempotent -- skips rows already migrated."""
    # Quick check: if the first row is already migrated, skip the full scan
    probe = conn.execute("SELECT candidate_data FROM candidate LIMIT 1").fetchone()
    if probe and probe[0]:
        try:
            if "profile" in json.loads(probe[0]):
                return
        except (TypeError, ValueError):
            pass
    rows = conn.execute("SELECT astral_candidate_id, candidate_data FROM candidate").fetchall()
    for row in rows:
        raw = row[1]
        if not raw:
            continue
        try:
            cd = json.loads(raw)
        except (TypeError, ValueError):
            continue
        if not isinstance(cd, dict):
            continue
        # Skip if already migrated (has a "profile" key)
        if "profile" in cd:
            continue
        # Old flat keys that signal pre-migration layout
        has_old_keys = any(k in cd for k in ("first", "last", "resume_raw", "candidate_context", "resume_base", "resume_email"))
        if not has_old_keys:
            continue

        profile_keys = ("first", "last", "contact_email", "resume_email", "reply_email", "phone", "location", "github", "linkedin_url")
        profile = {}
        for k in profile_keys:
            if k in cd:
                profile[k] = cd.pop(k)
        # Rename resume_email -> reply_email
        if "resume_email" in profile:
            profile["reply_email"] = profile.pop("resume_email")

        context = cd.pop("candidate_context", {}) or {}
        if "resume_raw" in cd:
            context["starting_resume_text"] = cd.pop("resume_raw")
        if "linkedin_raw" in cd:
            context["linkedin_profile_text"] = cd.pop("linkedin_raw")

        artifacts = {}
        if "resume_base" in cd:
            artifacts["base_resume"] = cd.pop("resume_base")

        new_cd = {**cd, "profile": profile, "context": context, "artifacts": artifacts}
        conn.execute(
            "UPDATE candidate SET candidate_data = ? WHERE astral_candidate_id = ?",
            (json.dumps(new_cd), row[0]),
        )
    conn.commit()
    # Relocate artifacts.bio_upshot → context.bio_summary (renamed field)
    _migrate_bio_upshot_to_summary(conn)


def _migrate_pronoun_preference_backfill(conn: sqlite3.Connection) -> None:
    """One-time idempotent backfill: unset profile.pronoun_preference → they/them (AST-573)."""
    rows = conn.execute("SELECT astral_candidate_id, candidate_data FROM candidate").fetchall()
    for row in rows:
        raw = row[1]
        if not raw:
            continue
        try:
            cd = json.loads(raw)
        except (TypeError, ValueError):
            continue
        if not isinstance(cd, dict):
            continue
        profile = cd.setdefault("profile", {})
        pref = profile.get("pronoun_preference")
        if isinstance(pref, str) and pref.strip() in PRONOUN_PREFERENCE_OPTIONS:
            continue
        profile["pronoun_preference"] = PRONOUN_PREFERENCE_DEFAULT
        conn.execute(
            "UPDATE candidate SET candidate_data = ? WHERE astral_candidate_id = ?",
            (json.dumps(cd), row[0]),
        )
    conn.commit()


def _migrate_bio_upshot_to_summary(conn: sqlite3.Connection) -> None:
    """Move artifacts.bio_upshot to context.bio_summary. Idempotent."""
    rows = conn.execute("SELECT astral_candidate_id, candidate_data FROM candidate").fetchall()
    for row in rows:
        raw = row[1]
        if not raw:
            continue
        try:
            cd = json.loads(raw)
        except (TypeError, ValueError):
            continue
        artifacts = cd.get("artifacts", {})
        if "bio_upshot" not in artifacts:
            continue
        context = cd.setdefault("context", {})
        if "bio_summary" not in context:
            context["bio_summary"] = artifacts.pop("bio_upshot")
        else:
            artifacts.pop("bio_upshot")
        conn.execute(
            "UPDATE candidate SET candidate_data = ? WHERE astral_candidate_id = ?",
            (json.dumps(cd), row[0]),
        )
    conn.commit()


def _flatten_context_array(items: list) -> str:
    """Convert a context array (strengths/priorities/deal_breakers/backstory) to readable text."""
    parts = []
    for item in items:
        if isinstance(item, str):
            parts.append(item)
            continue
        if not isinstance(item, dict):
            continue
        # backstory items: title, organization, job_reality, left_because, liked, tolerated
        if "title" in item or "organization" in item:
            header = " — ".join(filter(None, [item.get("title", ""), item.get("organization", "")]))
            lines = [header] if header else []
            for k in ("job_reality", "left_because"):
                if item.get(k):
                    lines.append(f"{k.replace('_', ' ').title()}: {item[k]}")
            for sub_key in ("liked", "tolerated"):
                sub_items = item.get(sub_key, [])
                if sub_items and isinstance(sub_items, list):
                    descs = [si.get("description", str(si)) if isinstance(si, dict) else str(si) for si in sub_items]
                    lines.append(f"{sub_key.title()}: {'; '.join(descs)}")
            parts.append("\n".join(lines))
        else:
            # strengths/priorities/deal_breakers: label + description
            label = item.get("label", "")
            desc = item.get("description", "")
            parts.append(f"{label}: {desc}" if label else desc)
    return "\n\n".join(parts)


def _migrate_context_arrays_to_text(conn: sqlite3.Connection) -> None:
    """Convert context.strengths/priorities/deal_breakers/backstory from arrays to text. Idempotent."""
    keys = ("strengths", "priorities", "deal_breakers", "backstory")
    rows = conn.execute("SELECT astral_candidate_id, candidate_data FROM candidate").fetchall()
    changed = False
    for row in rows:
        raw = row[1]
        if not raw:
            continue
        try:
            cd = json.loads(raw)
        except (TypeError, ValueError):
            continue
        ctx = cd.get("context")
        if not isinstance(ctx, dict):
            continue
        row_changed = False
        for key in keys:
            val = ctx.get(key)
            if isinstance(val, list):
                ctx[key] = _flatten_context_array(val)
                row_changed = True
        if row_changed:
            conn.execute(
                "UPDATE candidate SET candidate_data = ? WHERE astral_candidate_id = ?",
                (json.dumps(cd), row[0]),
            )
            changed = True
    if changed:
        conn.commit()


def _ensure_company_candidate_fk(conn: sqlite3.Connection) -> None:
    """Add candidate_id column to company table if missing. Idempotent."""
    global _company_candidate_fk_ensured
    if _company_candidate_fk_ensured:
        return
    _ensure_company_schema(conn)
    cursor = conn.execute("PRAGMA table_info(company)")
    cols = {row[1] for row in cursor.fetchall()}
    if "candidate_id" not in cols:
        try:
            conn.execute("ALTER TABLE company ADD COLUMN candidate_id TEXT")
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise
    _company_candidate_fk_ensured = True


def _ensure_company_table_for_upsert(conn: sqlite3.Connection) -> None:
    """Run all lazy company DDL needed before Copy Output key validation."""
    _ensure_company_schema(conn)
    _ensure_company_candidate_fk(conn)


def _parse_candidate_row(d: Dict[str, Any]) -> Dict[str, Any]:
    """Parse candidate_data + agent_responses JSON, decrypt candidate_api_key. Mutates and returns d."""
    if d.get("candidate_data"):
        try:
            d["candidate_data"] = json.loads(d["candidate_data"])
        except (TypeError, ValueError):
            d["candidate_data"] = {}
    else:
        d["candidate_data"] = {}
    if d.get("agent_responses"):
        try:
            d["agent_responses"] = json.loads(d["agent_responses"])
        except (TypeError, ValueError):
            d["agent_responses"] = []
    else:
        d["agent_responses"] = []
    if d.get("candidate_api_key"):
        try:
            d["candidate_api_key"] = decrypt_value(d["candidate_api_key"])
        except (RuntimeError, ValueError):
            d["candidate_api_key"] = None
    return d


def save_candidate(
    astral_candidate_id: str,
    *,
    state: Optional[str] = None,
    candidate_data: Optional[Dict[str, Any]] = None,
    candidate_api_key: Optional[str] = None,
    merge: bool = True,
    ) -> None:
    """Upsert a candidate row, following the save_job pattern.
    INSERT (new PK): state required. UPDATE (existing PK): only provided fields are set.
    candidate_data: merge=True deep-merges with existing; merge=False overwrites.
    candidate_api_key: if provided, Fernet-encrypted before storage.
    Auto-sets updated_at; auto-sets state_changed_at when state changes."""
    now = _utc_now()
    encrypted_key = encrypt_value(candidate_api_key) if candidate_api_key else None

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_candidate_schema(conn)
            existing = conn.execute(
                "SELECT astral_candidate_id, state, candidate_data FROM candidate WHERE astral_candidate_id = ?",
                (astral_candidate_id,),
            ).fetchone()

            if existing is None:
                if not state:
                    raise ValueError("state required for new candidate")
                allowed = list(CANDIDATE_STATES.keys())
                if state not in allowed:
                    raise ValueError(f"Invalid candidate state '{state}'. Must be one of: {allowed}")
                cdata_str = json.dumps(candidate_data) if candidate_data else "{}"
                conn.execute(
                    """INSERT INTO candidate (astral_candidate_id, state, candidate_data, candidate_api_key, created_at, updated_at, state_changed_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (astral_candidate_id, state, cdata_str, encrypted_key, now, now, now),
                )
            else:
                sets: List[str] = []
                params: List[Any] = []
                if state is not None:
                    allowed = list(CANDIDATE_STATES.keys())
                    if state not in allowed:
                        raise ValueError(f"Invalid candidate state '{state}'. Must be one of: {allowed}")
                    sets.append("state = ?")
                    params.append(state)
                    if existing["state"] != state:
                        sets.append("state_changed_at = ?")
                        params.append(now)
                if candidate_data is not None:
                    if merge:
                        existing_data = json.loads(existing["candidate_data"]) if existing["candidate_data"] else {}
                        _deep_merge(existing_data, candidate_data)
                        sets.append("candidate_data = ?")
                        params.append(json.dumps(existing_data))
                    else:
                        sets.append("candidate_data = ?")
                        params.append(json.dumps(candidate_data))
                if encrypted_key is not None:
                    sets.append("candidate_api_key = ?")
                    params.append(encrypted_key)
                if not sets:
                    return
                sets.append("updated_at = ?")
                params.append(now)
                params.append(astral_candidate_id)
                conn.execute(
                    f"UPDATE candidate SET {', '.join(sets)} WHERE astral_candidate_id = ?",
                    tuple(params),
                )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def clear_candidate_api_key(candidate_id: str) -> None:
    """Set candidate_api_key to NULL for a candidate."""
    now = _utc_now()
    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_candidate_schema(conn)
            conn.execute(
                "UPDATE candidate SET candidate_api_key = NULL, updated_at = ? WHERE astral_candidate_id = ?",
                (now, candidate_id),
            )
            conn.commit()
        finally:
            conn.close()
    _run_with_retry(_with_conn)


def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Select single candidate by astral_candidate_id. Returns parsed dict or None."""
    if not candidate_id or not candidate_id.strip():
        return None

    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_candidate_schema(conn)
            row = conn.execute(
                "SELECT * FROM candidate WHERE astral_candidate_id = ?", (candidate_id,)
            ).fetchone()
            return _parse_candidate_row(_row_to_dict(row)) if row else None
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_candidates() -> List[Dict[str, Any]]:
    """Return all candidates as a list of parsed dicts."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_candidate_schema(conn)
            rows = conn.execute("SELECT * FROM candidate ORDER BY created_at").fetchall()
            return [_parse_candidate_row(_row_to_dict(r)) for r in rows]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


# ---- board_search ----

def _finalize_board_search_state_schema(conn: sqlite3.Connection) -> None:
    """Drop legacy enabled + batch-status columns → single workflow `state` (AST-471)."""
    act, inactive, err = BOARD_SEARCH_STATES
    cols = {row[1] for row in conn.execute("PRAGMA table_info(board_search)").fetchall()}
    if "enabled" not in cols and "status" not in cols:
        if "state" not in cols:
            conn.execute(
                "ALTER TABLE board_search ADD COLUMN state TEXT NOT NULL DEFAULT 'ACTIVE'"
            )
            conn.commit()
        return
    if "state" not in cols:
        conn.execute("ALTER TABLE board_search ADD COLUMN state TEXT")
    conn.execute(
        """UPDATE board_search SET state = CASE
                WHEN COALESCE(enabled, 1) = 0 THEN ?
                WHEN LOWER(TRIM(COALESCE(status, ''))) = 'error' THEN ?
                ELSE ?
            END""",
        (inactive, err, act),
    )
    conn.execute(
        """
        CREATE TABLE             board_search_next (
            board_search_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            board_key TEXT NOT NULL,
            label TEXT NOT NULL,
            criteria TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'ACTIVE',
            batch_id TEXT,
            search_mode TEXT NOT NULL DEFAULT 'criteria',
            deeplink_url TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            last_scan_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        INSERT INTO board_search_next (
            board_search_id, candidate_id, board_key, label, criteria, state,
            batch_id, search_mode, deeplink_url, created_at, updated_at, last_scan_at
        )
        SELECT
            board_search_id, candidate_id, board_key, label, criteria, state,
            batch_id,
            COALESCE(NULLIF(TRIM(search_mode), ''), 'criteria'),
            deeplink_url, created_at, updated_at, last_scan_at
        FROM board_search
        """
    )
    conn.execute("DROP TABLE board_search")
    conn.execute("ALTER TABLE board_search_next RENAME TO board_search")
    conn.commit()


# update_board_search_row: omit deeplink_url column when unchanged.
_BOARD_SEARCH_PATCH_OMIT = object()

def _ensure_board_search_table(conn: sqlite3.Connection) -> None:
    """Create board_search if missing and migrate AST-457 enabled/status → state (AST-471)."""
    global _board_search_schema_ensured
    if _board_search_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='board_search'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE board_search (
                board_search_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                board_key TEXT NOT NULL,
                label TEXT NOT NULL,
                criteria TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'ACTIVE',
                batch_id TEXT,
                search_mode TEXT NOT NULL DEFAULT 'criteria',
                deeplink_url TEXT,
                last_scan_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        _board_search_schema_ensured = True
        return
    cols = {row[1] for row in conn.execute("PRAGMA table_info(board_search)").fetchall()}
    for col, col_def in (
        ("status", "TEXT DEFAULT 'active'"),
        ("batch_id", "TEXT"),
        ("enabled", "INTEGER NOT NULL DEFAULT 1"),
        ("search_mode", "TEXT NOT NULL DEFAULT 'criteria'"),
        ("deeplink_url", "TEXT"),
        ("last_scan_at", "TIMESTAMP"),
    ):
        if col not in cols:
            conn.execute(f"ALTER TABLE board_search ADD COLUMN {col} {col_def}")
            conn.commit()
    _finalize_board_search_state_schema(conn)
    _board_search_schema_ensured = True


def _parse_board_search_row(row: Dict[str, Any]) -> Dict[str, Any]:
    if row.get("criteria") and isinstance(row["criteria"], str):
        raw = row["criteria"]
        try:
            row["criteria"] = json.loads(raw)
        except json.JSONDecodeError as exc:
            # Fail loud: corrupt DB blob must not silently pass through as an unparseable str.
            bid = row.get("board_search_id") or "?"
            _log.error(
                "board_search %s: stored criteria is not valid JSON (%s chars): %s",
                bid,
                len(raw),
                exc,
            )
            raise ValueError(f"board_search {bid}: stored criteria is not valid JSON") from exc
    st = str(row.get("state") or BOARD_SEARCH_STATES[0]).strip().upper()
    row["state"] = st if st in BOARD_SEARCH_STATES else BOARD_SEARCH_STATES[0]
    if not row.get("search_mode"):
        row["search_mode"] = "criteria"
    du = row.get("deeplink_url")
    row["deeplink_url"] = None if du is None or du == "" else str(du)
    return row


def save_board_search_row(
    board_search_id: str,
    candidate_id: str,
    board_key: str,
    label: str,
    criteria_json: str,
    *,
    state: Optional[str] = None,
    search_mode: str = "criteria",
    deeplink_url: Optional[str] = None,
) -> None:
    st = (
        BOARD_SEARCH_STATES[0]
        if state is None or str(state).strip() == ""
        else str(state).strip().upper()
    )
    if st not in BOARD_SEARCH_STATES:
        raise ValueError(f"invalid board_search state: {state!r}")

    now = _utc_now()

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            conn.execute(
                """INSERT INTO board_search
                   (board_search_id, candidate_id, board_key, label, criteria,
                    state, search_mode, deeplink_url, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    board_search_id,
                    candidate_id,
                    board_key,
                    label,
                    criteria_json,
                    st,
                    search_mode,
                    deeplink_url,
                    now,
                    now,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def get_board_search_row(board_search_id: str) -> Optional[Dict[str, Any]]:
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            row = conn.execute(
                "SELECT * FROM board_search WHERE board_search_id = ?", (board_search_id,)
            ).fetchone()
            return _parse_board_search_row(_row_to_dict(row)) if row else None
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_board_search_rows(
    candidate_id: str,
    board_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            if board_key:
                rows = conn.execute(
                    """SELECT * FROM board_search
                       WHERE candidate_id = ? AND board_key = ?
                       ORDER BY created_at""",
                    (candidate_id, board_key),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM board_search WHERE candidate_id = ? ORDER BY created_at",
                    (candidate_id,),
                ).fetchall()
            return [_parse_board_search_row(_row_to_dict(r)) for r in rows]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def update_board_search_row(
    board_search_id: str,
    *,
    label: Optional[str] = None,
    criteria_json: Optional[str] = None,
    state: Optional[str] = None,
    search_mode: Optional[str] = None,
    deeplink_url: Any = _BOARD_SEARCH_PATCH_OMIT,
) -> None:
    """Update board_search. Pass deeplink_url=None for SQL NULL; omit to leave unchanged."""

    if (
        label is None
        and criteria_json is None
        and state is None
        and search_mode is None
        and deeplink_url is _BOARD_SEARCH_PATCH_OMIT
    ):
        return
    now = _utc_now()
    sets: List[str] = ["updated_at = ?"]
    params: List[Any] = [now]
    if label is not None:
        sets.append("label = ?")
        params.append(label)
    if criteria_json is not None:
        sets.append("criteria = ?")
        params.append(criteria_json)
    if state is not None:
        sets.append("state = ?")
        params.append(state)
    if search_mode is not None:
        sets.append("search_mode = ?")
        params.append(search_mode)
    if deeplink_url is not _BOARD_SEARCH_PATCH_OMIT:
        sets.append("deeplink_url = ?")
        params.append(deeplink_url)
    params.append(board_search_id)

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            conn.execute(
                f"UPDATE board_search SET {', '.join(sets)} WHERE board_search_id = ?",
                tuple(params),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def update_board_search_last_scan_at(board_search_id: str) -> None:
    """Set last_scan_at = now only; skip updated_at — scan cadence vs user edits (AST-482)."""
    now = _utc_now()

    def _inner() -> None:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            conn.execute(
                "UPDATE board_search SET last_scan_at = ? WHERE board_search_id = ?",
                (now, board_search_id),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_inner)


def claim_board_search_batch(
    batch_id: str,
    limit: int,
    candidate_id: Optional[str] = None,
    scan_interval_hours: Optional[float] = None,
    sort_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Claim board_search rows in ACTIVE with clear batch_id (§2.4 lock = batch_id only).

    Mirrors set_company_batch scan gate: optional scan_interval_hours filters to NULL or stale
    last_scan_at. sort_by whitelist → BOARD_SEARCH_BATCH_SORT_COLUMNS."""
    act = BOARD_SEARCH_STATES[0]
    now = _utc_now()

    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            where_base = "state = ? AND (batch_id IS NULL OR batch_id = '')"
            params: List[Any] = [batch_id, now, act]
            if candidate_id:
                where_base += " AND candidate_id = ?"
                params.append(candidate_id)
            if scan_interval_hours is not None:
                where_base += " AND (last_scan_at IS NULL OR last_scan_at < datetime('now', '-' || ? || ' hours'))"
                params.append(str(float(scan_interval_hours)))
            order_clause = (
                f"ORDER BY {sort_by} ASC NULLS FIRST"
                if sort_by and sort_by in BOARD_SEARCH_BATCH_SORT_COLUMNS
                else "ORDER BY rowid"
            )
            _limit = int(limit) if limit else 0
            limit_clause = "LIMIT ?" if _limit > 0 else ""
            if _limit > 0:
                params.append(_limit)
            cur = conn.execute(
                f"""UPDATE board_search SET batch_id = ?, updated_at = ?
                   WHERE rowid IN (
                       SELECT rowid FROM board_search
                       WHERE {where_base}
                       {order_clause}
                       {limit_clause}
                   )""".strip(),
                tuple(params),
            )
            if cur.rowcount == 0:
                conn.commit()
                return []
            claimed = conn.execute(
                "SELECT * FROM board_search WHERE batch_id = ? ORDER BY rowid",
                (batch_id,),
            ).fetchall()
            conn.commit()
            return [_parse_board_search_row(_row_to_dict(r)) for r in claimed]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)
def clear_board_search_batch(batch_id: str) -> int:
    now = _utc_now()

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            cur = conn.execute(
                """UPDATE board_search SET batch_id = NULL, updated_at = ?
                   WHERE batch_id = ?""",
                (now, batch_id),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def set_board_search_state(board_search_id: str, state: str) -> None:
    st = str(state).strip().upper()
    if st not in BOARD_SEARCH_STATES:
        raise ValueError(f"invalid board_search state: {state!r}")
    now = _utc_now()

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            conn.execute(
                "UPDATE board_search SET state = ?, updated_at = ? WHERE board_search_id = ?",
                (st, now, board_search_id),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def delete_board_search_row(board_search_id: str) -> bool:
    def _with_conn() -> bool:
        conn = _get_connection()
        try:
            _ensure_board_search_table(conn)
            cur = conn.execute(
                "DELETE FROM board_search WHERE board_search_id = ?", (board_search_id,)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def board_listing_is_duplicate(candidate_id: str, board_key: str, listing_key: str) -> bool:
    """True if this candidate already has a job with the same board listing_key on board_key."""
    prefix = "__board__"
    company = f"{prefix}{board_key}"

    def _with_conn() -> bool:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            _ensure_company_candidate_fk(conn)
            row = conn.execute(
                """SELECT 1 FROM job j
                   JOIN company c ON j.company = c.short_name
                   WHERE c.candidate_id = ?
                     AND json_extract(j.job_data, '$.board_key') = ?
                     AND json_extract(j.job_data, '$.board_listing_key') = ?
                   LIMIT 1""",
                (candidate_id, board_key, listing_key),
            ).fetchone()
            if row:
                return True
            # Fallback: placeholder company row without join if candidate_id not set yet
            row = conn.execute(
                """SELECT 1 FROM job
                   WHERE company = ?
                     AND json_extract(job_data, '$.board_key') = ?
                     AND json_extract(job_data, '$.board_listing_key') = ?
                   LIMIT 1""",
                (company, board_key, listing_key),
            ).fetchone()
            return row is not None
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def _ensure_board_search_run_table(conn: sqlite3.Connection) -> None:
    global _board_search_run_schema_ensured
    if _board_search_run_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='board_search_run'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE board_search_run (
                batch_id TEXT NOT NULL,
                board_search_id TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                board_key TEXT NOT NULL,
                new INTEGER NOT NULL,
                duplicates INTEGER NOT NULL,
                invalid_title INTEGER NOT NULL,
                completed_at TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                PRIMARY KEY (batch_id, board_search_id)
            )
        """)
        conn.commit()
    else:
        pk_cols = {
            row[1]
            for row in conn.execute("PRAGMA table_info(board_search_run)").fetchall()
            if row[5]
        }
        if pk_cols == {"batch_id"}:
            conn.execute("""
                CREATE TABLE board_search_run_new (
                    batch_id TEXT NOT NULL,
                    board_search_id TEXT NOT NULL,
                    candidate_id TEXT NOT NULL,
                    board_key TEXT NOT NULL,
                    new INTEGER NOT NULL,
                    duplicates INTEGER NOT NULL,
                    invalid_title INTEGER NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    PRIMARY KEY (batch_id, board_search_id)
                )
            """)
            conn.execute("""
                INSERT INTO board_search_run_new
                SELECT batch_id, board_search_id, candidate_id, board_key, new, duplicates,
                       invalid_title, completed_at, status
                FROM board_search_run
            """)
            conn.execute("DROP TABLE board_search_run")
            conn.execute("ALTER TABLE board_search_run_new RENAME TO board_search_run")
            conn.commit()
    _board_search_run_schema_ensured = True


def record_board_search_run(
    batch_id: str,
    board_search_id: str,
    candidate_id: str,
    board_key: str,
    counts: Dict[str, int],
    *,
    status: str = "COMPLETED",
) -> None:
    now = _utc_now()

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_board_search_run_table(conn)
            conn.execute(
                """INSERT OR REPLACE INTO board_search_run
                   (batch_id, board_search_id, candidate_id, board_key, new, duplicates,
                    invalid_title, completed_at, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    batch_id,
                    board_search_id,
                    candidate_id,
                    board_key,
                    counts.get("new", 0),
                    counts.get("duplicates", 0),
                    counts.get("invalid_title", 0),
                    now,
                    status,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


# ---- company_search_terms (AST-524) ----

def _search_term_lines_from_string(val: str) -> list[str]:
    """Trim/split newline list — data layer cannot import core.candidate."""
    return [ln for ln in (s.strip() for s in val.split("\n")) if ln]


def _ensure_company_search_terms_table(conn: sqlite3.Connection) -> None:
    """Create company_search_terms if missing; one-time artifact import per process."""
    global _company_search_terms_schema_ensured, _company_search_terms_migration_swept
    if _company_search_terms_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='company_search_terms'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE company_search_terms (
                candidate_id TEXT NOT NULL,
                search_term TEXT NOT NULL,
                last_scan_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                PRIMARY KEY (candidate_id, search_term)
            )
        """)
        conn.execute(
            "CREATE INDEX idx_company_search_terms_candidate ON company_search_terms (candidate_id)"
        )
        conn.commit()
    if not _company_search_terms_migration_swept:
        _migrate_company_search_terms_from_artifacts(conn)
        _company_search_terms_migration_swept = True
    _company_search_terms_schema_ensured = True


def _migrate_company_search_terms_from_artifacts(conn: sqlite3.Connection) -> None:
    """Import legacy artifacts.company_search_terms strings when table has no rows for candidate."""
    _ensure_candidate_schema(conn)
    rows = conn.execute(
        "SELECT astral_candidate_id, candidate_data FROM candidate"
    ).fetchall()
    now = _utc_now()
    for row in rows:
        cid = row[0]
        if not cid or not str(cid).strip():
            continue
        raw_cd = row[1]
        if not raw_cd:
            continue
        try:
            cd = json.loads(raw_cd) if isinstance(raw_cd, str) else raw_cd
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(cd, dict):
            continue
        arts = cd.get("artifacts") or {}
        raw = arts.get("company_search_terms")
        if not isinstance(raw, str) or not raw.strip():
            continue
        count_row = conn.execute(
            "SELECT COUNT(*) FROM company_search_terms WHERE candidate_id = ?",
            (cid,),
        ).fetchone()
        if count_row and int(count_row[0]) > 0:
            continue
        lines = _search_term_lines_from_string(raw)
        if not lines:
            continue
        seen: set[str] = set()
        for term in lines:
            if term in seen:
                continue
            seen.add(term)
            conn.execute(
                """INSERT INTO company_search_terms
                   (candidate_id, search_term, last_scan_at, created_at, updated_at)
                   VALUES (?, ?, NULL, ?, ?)""",
                (cid, term, now, now),
            )
    conn.commit()


def list_company_search_terms(candidate_id: str) -> List[Dict[str, Any]]:
    """Rows for candidate ordered by search_term ASC."""
    if not candidate_id or not str(candidate_id).strip():
        return []

    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_company_search_terms_table(conn)
            rows = conn.execute(
                """SELECT search_term, last_scan_at, created_at, updated_at
                   FROM company_search_terms
                   WHERE candidate_id = ?
                   ORDER BY search_term ASC""",
                (candidate_id,),
            ).fetchall()
            return [
                {
                    "search_term": r[0],
                    "last_scan_at": r[1],
                    "created_at": r[2],
                    "updated_at": r[3],
                }
                for r in rows
            ]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def sync_company_search_terms(candidate_id: str, terms: List[str]) -> None:
    """Upsert-and-delete: preserve last_scan_at on existing terms; drop removed terms."""
    if not candidate_id or not str(candidate_id).strip():
        return
    seen: set[str] = set()
    normalized: List[str] = []
    for raw in terms:
        term = raw.strip() if isinstance(raw, str) else ""
        if not term or term in seen:
            continue
        seen.add(term)
        normalized.append(term)
    now = _utc_now()

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_company_search_terms_table(conn)
            if not normalized:
                conn.execute(
                    "DELETE FROM company_search_terms WHERE candidate_id = ?",
                    (candidate_id,),
                )
            else:
                placeholders = ", ".join("?" for _ in normalized)
                conn.execute(
                    f"""DELETE FROM company_search_terms
                        WHERE candidate_id = ? AND search_term NOT IN ({placeholders})""",
                    [candidate_id, *normalized],
                )
                for term in normalized:
                    conn.execute(
                        """INSERT INTO company_search_terms
                           (candidate_id, search_term, last_scan_at, created_at, updated_at)
                           VALUES (?, ?, NULL, ?, ?)
                           ON CONFLICT(candidate_id, search_term) DO UPDATE SET
                               updated_at = excluded.updated_at""",
                        (candidate_id, term, now, now),
                    )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)




# ---- rubric_vector / vector_feedback (AST-722) ----

def _resolve_current_agent_task_uuid(conn: sqlite3.Connection, task_key: str) -> Optional[str]:
    """Return task_key_uuid for current agent_task row, or None if missing."""
    _ensure_agent_task_schema(conn)
    row = conn.execute(
        "SELECT task_key_uuid FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1",
        (task_key,),
    ).fetchone()
    return row[0] if row else None


def _ensure_rubric_vector_table(conn: sqlite3.Connection) -> None:
    global _rubric_vector_schema_ensured
    if _rubric_vector_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='rubric_vector'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE rubric_vector (
                rubric_vector_uuid TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                task_key TEXT NOT NULL,
                task_key_uuid TEXT NOT NULL,
                code TEXT NOT NULL,
                label TEXT NOT NULL,
                content TEXT NOT NULL,
                importance INTEGER NOT NULL,
                content_fingerprint TEXT NOT NULL,
                current INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX idx_rubric_vector_candidate_task_current "
            "ON rubric_vector (candidate_id, task_key, current)"
        )
        conn.execute(
            "CREATE INDEX idx_rubric_vector_task_key_uuid ON rubric_vector (task_key_uuid)"
        )
        conn.commit()
    _rubric_vector_schema_ensured = True


def _ensure_vector_feedback_table(conn: sqlite3.Connection) -> None:
    global _vector_feedback_schema_ensured
    if _vector_feedback_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='vector_feedback'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE vector_feedback (
                vector_feedback_id TEXT PRIMARY KEY,
                rubric_vector_uuid TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                batch_id TEXT NOT NULL,
                task_key TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                value TEXT NOT NULL,
                agent_data_id TEXT,
                created_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX idx_vector_feedback_rubric ON vector_feedback (rubric_vector_uuid)"
        )
        conn.execute(
            "CREATE INDEX idx_vector_feedback_batch ON vector_feedback (batch_id)"
        )
        conn.execute(
            "CREATE INDEX idx_vector_feedback_candidate_task "
            "ON vector_feedback (candidate_id, task_key)"
        )
        conn.commit()
    _vector_feedback_schema_ensured = True


def _insert_rubric_vector_row_on_connection(
    conn: sqlite3.Connection,
    *,
    candidate_id: str,
    task_key: str,
    task_key_uuid: str,
    code: str,
    label: str,
    content: str,
    importance: int,
    content_fingerprint: str,
    current: int = 1,
) -> str:
    _ensure_rubric_vector_table(conn)
    now = _utc_now()
    rubric_vector_uuid = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO rubric_vector (
               rubric_vector_uuid, candidate_id, task_key, task_key_uuid,
               code, label, content, importance, content_fingerprint,
               current, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            rubric_vector_uuid,
            candidate_id,
            task_key,
            task_key_uuid,
            code,
            label,
            content,
            importance,
            content_fingerprint,
            current,
            now,
            now,
        ),
    )
    conn.commit()
    return rubric_vector_uuid


def insert_rubric_vector_row(
    *,
    candidate_id: str,
    task_key: str,
    task_key_uuid: str,
    code: str,
    label: str,
    content: str,
    importance: int,
    content_fingerprint: str,
    current: int = 1,
) -> str:
    def _with_conn() -> str:
        conn = _get_connection()
        try:
            return _insert_rubric_vector_row_on_connection(
                conn,
                candidate_id=candidate_id,
                task_key=task_key,
                task_key_uuid=task_key_uuid,
                code=code,
                label=label,
                content=content,
                importance=importance,
                content_fingerprint=content_fingerprint,
                current=current,
            )
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def get_current_agent_task_uuid(task_key: str) -> Optional[str]:
    """Public helper: current agent_task UUID for task_key (AST-722 backfill)."""

    def _with_conn() -> Optional[str]:
        conn = _get_connection()
        try:
            return _resolve_current_agent_task_uuid(conn, task_key)
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_rubric_vectors(
    candidate_id: str,
    task_key: str,
    *,
    current_only: bool = True,
) -> List[Dict[str, Any]]:
    if not candidate_id or not str(candidate_id).strip() or not task_key:
        return []

    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_rubric_vector_table(conn)
            sql = """SELECT rubric_vector_uuid, candidate_id, task_key, task_key_uuid,
                            code, label, content, importance, content_fingerprint,
                            current, created_at, updated_at
                     FROM rubric_vector
                     WHERE candidate_id = ? AND task_key = ?"""
            params: List[Any] = [candidate_id, task_key]
            if current_only:
                sql += " AND current = 1"
            sql += " ORDER BY code ASC"
            rows = conn.execute(sql, tuple(params)).fetchall()
            return [
                {
                    "rubric_vector_uuid": r[0],
                    "candidate_id": r[1],
                    "task_key": r[2],
                    "task_key_uuid": r[3],
                    "code": r[4],
                    "label": r[5],
                    "content": r[6],
                    "importance": r[7],
                    "content_fingerprint": r[8],
                    "current": r[9],
                    "created_at": r[10],
                    "updated_at": r[11],
                }
                for r in rows
            ]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def count_rubric_vectors_for_candidate_task(
    candidate_id: str,
    task_key: str,
    *,
    current_only: bool = True,
) -> int:
    if not candidate_id or not str(candidate_id).strip() or not task_key:
        return 0

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_rubric_vector_table(conn)
            sql = "SELECT COUNT(*) FROM rubric_vector WHERE candidate_id = ? AND task_key = ?"
            params: List[Any] = [candidate_id, task_key]
            if current_only:
                sql += " AND current = 1"
            row = conn.execute(sql, tuple(params)).fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def purge_legacy_rubric_artifact_keys(candidate_id: str) -> List[str]:
    """Remove legacy rubric criteria keys from candidate_data.artifacts (AST-722)."""
    if not candidate_id or not str(candidate_id).strip():
        return []

    def _with_conn() -> List[str]:
        conn = _get_connection()
        try:
            _ensure_candidate_schema(conn)
            row = conn.execute(
                "SELECT candidate_data FROM candidate WHERE astral_candidate_id = ?",
                (candidate_id,),
            ).fetchone()
            if not row or not row[0]:
                return []
            try:
                cd = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            except (json.JSONDecodeError, TypeError):
                return []
            if not isinstance(cd, dict):
                return []
            arts = cd.get("artifacts")
            if not isinstance(arts, dict):
                return []
            removed: List[str] = []
            for key in RUBRIC_CRITERIA_ARTIFACT_KEYS:
                if key in arts:
                    arts.pop(key)
                    removed.append(key)
            if not removed:
                return []
            cd["artifacts"] = arts
            now = _utc_now()
            conn.execute(
                "UPDATE candidate SET candidate_data = ?, updated_at = ? WHERE astral_candidate_id = ?",
                (json.dumps(cd), now, candidate_id),
            )
            conn.commit()
            return removed
        finally:
            conn.close()

    return _run_with_retry(_with_conn)

# ---- candidate_intake_session (AST-558) ----

def _ensure_candidate_intake_session_table(conn: sqlite3.Connection) -> None:
    global _intake_session_schema_ensured
    if _intake_session_schema_ensured:
        return
    cursor = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='candidate_intake_session'"
    )
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE candidate_intake_session (
                intake_session_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL,
                status TEXT NOT NULL,
                transcript TEXT NOT NULL,
                prompt_snapshot TEXT,
                last_ready_to_build INTEGER NOT NULL DEFAULT 0,
                built_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        conn.execute(
            "CREATE INDEX idx_intake_session_candidate ON candidate_intake_session (candidate_id)"
        )
        conn.commit()
    _intake_session_schema_ensured = True


def _parse_intake_session_row(row: Dict[str, Any]) -> Dict[str, Any]:
    for key in ("transcript", "prompt_snapshot"):
        raw = row.get(key)
        if raw is None or raw == "":
            row[key] = [] if key == "transcript" else None
        elif isinstance(raw, str):
            try:
                row[key] = json.loads(raw)
            except (TypeError, ValueError):
                row[key] = [] if key == "transcript" else None
    row["last_ready_to_build"] = bool(row.get("last_ready_to_build"))
    return row


def create_intake_session(
    intake_session_id: str,
    candidate_id: str,
    transcript: Optional[List[Any]] = None,
    prompt_snapshot: Optional[Dict[str, Any]] = None,
) -> None:
    from src.utils.config import INTAKE_CONFIG

    now = _utc_now()
    tx = json.dumps(transcript if transcript is not None else [])
    snap = json.dumps(prompt_snapshot) if prompt_snapshot else None

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_candidate_intake_session_table(conn)
            conn.execute(
                """INSERT INTO candidate_intake_session
                   (intake_session_id, candidate_id, status, transcript, prompt_snapshot,
                    last_ready_to_build, built_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, 0, NULL, ?, ?)""",
                (
                    intake_session_id,
                    candidate_id,
                    INTAKE_CONFIG["session_status_active"],
                    tx,
                    snap,
                    now,
                    now,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def get_intake_session(intake_session_id: str) -> Optional[Dict[str, Any]]:
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_candidate_intake_session_table(conn)
            row = conn.execute(
                "SELECT * FROM candidate_intake_session WHERE intake_session_id = ?",
                (intake_session_id,),
            ).fetchone()
            return _parse_intake_session_row(_row_to_dict(row)) if row else None
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def update_intake_session(
    intake_session_id: str,
    *,
    transcript: List[Any],
    prompt_snapshot: Optional[Dict[str, Any]],
    last_ready_to_build: bool,
    status: str,
    built_at: Optional[str],
) -> None:
    now = _utc_now()
    tx = json.dumps(transcript)
    snap = json.dumps(prompt_snapshot) if prompt_snapshot else None

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_candidate_intake_session_table(conn)
            conn.execute(
                """UPDATE candidate_intake_session
                   SET transcript = ?, prompt_snapshot = ?, last_ready_to_build = ?,
                       status = ?, built_at = ?, updated_at = ?
                   WHERE intake_session_id = ?""",
                (
                    tx,
                    snap,
                    1 if last_ready_to_build else 0,
                    status,
                    built_at,
                    now,
                    intake_session_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def get_active_intake_session(candidate_id: str) -> Optional[Dict[str, Any]]:
    from src.utils.config import INTAKE_CONFIG

    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_candidate_intake_session_table(conn)
            row = conn.execute(
                """SELECT * FROM candidate_intake_session
                   WHERE candidate_id = ? AND status = ?
                   ORDER BY created_at DESC LIMIT 1""",
                (candidate_id, INTAKE_CONFIG["session_status_active"]),
            ).fetchone()
            return _parse_intake_session_row(_row_to_dict(row)) if row else None
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def update_company_search_term_last_scan_at(candidate_id: str, search_term: str) -> None:
    """Set last_scan_at = now only; skip updated_at — scan cadence vs user sync (AST-524)."""
    if not candidate_id or not search_term:
        return
    now = _utc_now()

    def _inner() -> None:
        conn = _get_connection()
        try:
            _ensure_company_search_terms_table(conn)
            conn.execute(
                """UPDATE company_search_terms SET last_scan_at = ?
                   WHERE candidate_id = ? AND search_term = ?""",
                (now, candidate_id, search_term),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_inner)


def count_stale_company_search_terms(candidate_id: str, scan_interval_hours: float) -> int:
    """Count terms with NULL or stale last_scan_at (AST-525 consumer)."""
    if not candidate_id or not str(candidate_id).strip():
        return 0
    if scan_interval_hours <= 0:
        return 0

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_company_search_terms_table(conn)
            row = conn.execute(
                """SELECT COUNT(*) FROM company_search_terms
                   WHERE candidate_id = ?
                     AND (last_scan_at IS NULL
                          OR last_scan_at < datetime('now', '-' || ? || ' hours'))""",
                (candidate_id, str(float(scan_interval_hours))),
            ).fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_stale_company_search_terms(candidate_id: str, scan_interval_hours: float) -> List[str]:
    """Stale term strings for inflow_discovery (AST-525); ordered search_term ASC."""
    if not candidate_id or not str(candidate_id).strip():
        return []
    if scan_interval_hours <= 0:
        return []

    def _with_conn() -> List[str]:
        conn = _get_connection()
        try:
            _ensure_company_search_terms_table(conn)
            rows = conn.execute(
                """SELECT search_term FROM company_search_terms
                   WHERE candidate_id = ?
                     AND (last_scan_at IS NULL
                          OR last_scan_at < datetime('now', '-' || ? || ' hours'))
                   ORDER BY search_term ASC""",
                (candidate_id, str(float(scan_interval_hours))),
            ).fetchall()
            return [r[0] for r in rows]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


# ---------------------------------------------------------------------------
# Agent table: system prompt templates
# ---------------------------------------------------------------------------

def _ensure_agent_schema(conn: sqlite3.Connection) -> None:
    """Create agent table if not present; migrate + seed new columns idempotently."""
    global _agent_schema_ensured
    if _agent_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='agent'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE agent (
                agent_id TEXT PRIMARY KEY,
                content TEXT,
                model_code TEXT,
                brain_setting TEXT,
                temperature REAL,
                max_tokens INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    else:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(agent)").fetchall()}
        for col_name, col_def in [
            ("model_code", "TEXT"),
            ("brain_setting", "TEXT"),
            ("temperature", "REAL"),
            ("max_tokens", "INTEGER"),
        ]:
            if col_name not in cols:
                try:
                    conn.execute(f"ALTER TABLE agent ADD COLUMN {col_name} {col_def}")
                    conn.commit()
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        raise
        cols = {row[1] for row in conn.execute("PRAGMA table_info(agent)").fetchall()}
        # Seed existing agents that have no model_code with the Sonnet defaults (legacy reads only).
        if "model_code" in cols:
            _seed_key = "claude-sonnet-4-6"
            _seed = AGENT_CONFIG[_seed_key]
            conn.execute(
                "UPDATE agent SET model_code = ?, temperature = ?, max_tokens = ? WHERE model_code IS NULL",
                (_seed_key, _seed["default_temperature"], _seed["default_max_tokens"]),
            )
            conn.execute("UPDATE agent SET model_code = 'claude-sonnet-4-6' WHERE model_code = 'claude-sonnet-4-5'")
            conn.commit()
        if "brain_setting" in cols:
            conn.execute("""
                UPDATE agent SET brain_setting = CASE COALESCE(TRIM(model_code), '')
                    WHEN 'claude-haiku-4-5' THEN 'Little'
                    WHEN 'claude-sonnet-4-6' THEN 'Medium'
                    WHEN 'claude-opus-4-6' THEN 'Big'
                    ELSE 'Medium'
                END
                WHERE brain_setting IS NULL OR TRIM(COALESCE(brain_setting, '')) = ''
            """)
            conn.commit()
    _agent_schema_ensured = True


def save_agent(
    agent_id: str,
    content: str,
    *,
    brain_setting: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> None:
    """Upsert an agent row; new rows require brain_setting (model_code column is legacy, not written)."""
    now = _utc_now()

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_agent_schema(conn)
            existing = conn.execute(
                "SELECT agent_id FROM agent WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            if existing is None:
                if brain_setting is None or not str(brain_setting).strip():
                    raise ValueError("save_agent requires brain_setting for new agent rows")
                validate_allowed_brain_setting(str(brain_setting).strip())
                conn.execute(
                    """
                    INSERT INTO agent (agent_id, content, brain_setting, temperature, max_tokens, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (agent_id, content, str(brain_setting).strip(), temperature, max_tokens, now),
                )
            else:
                sets = ["content = ?", "updated_at = ?"]
                params: List[Any] = [content, now]
                if brain_setting is not None:
                    validate_allowed_brain_setting(str(brain_setting).strip())
                    sets.append("brain_setting = ?")
                    params.append(str(brain_setting).strip())
                for col, val in [("temperature", temperature), ("max_tokens", max_tokens)]:
                    if val is not None:
                        sets.append(f"{col} = ?")
                        params.append(val)
                params.append(agent_id)
                conn.execute(f"UPDATE agent SET {', '.join(sets)} WHERE agent_id = ?", params)
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    """Return single agent by agent_id (API-shaped), or None."""
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_schema(conn)
            row = conn.execute(
                "SELECT * FROM agent WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            if not row:
                return None
            return _expose_agent_public(_row_to_dict(row))
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def list_agents() -> List[Dict[str, Any]]:
    """Return all agents including brain_setting / resolved_model_key plus UI-compat model_code."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_schema(conn)
            _ensure_agent_task_schema(conn)
            rows = conn.execute("""
                SELECT agent_id, LENGTH(content) AS content_length,
                       model_code, brain_setting, temperature, max_tokens, updated_at,
                       (SELECT COUNT(*) FROM agent_task WHERE agent_task.agent_id = agent.agent_id) AS task_count
                FROM agent ORDER BY agent_id
            """).fetchall()
            return [_expose_agent_public(_row_to_dict(r)) for r in rows]
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


_UPDATE_AGENT_ALLOWED = frozenset({"content", "brain_setting", "temperature", "max_tokens"})


def update_agent(agent_id: str, **kwargs: Any) -> int:
    """Partial UPDATE: set only the columns passed. Allowlist enforced.
    updated_at auto-set to now. Returns rowcount (0 or 1)."""
    cols = [k for k in kwargs if k in _UPDATE_AGENT_ALLOWED]
    if not cols:
        return 0
    now = _utc_now()
    pairs = [f"{c} = ?" for c in cols]
    params: List[Any] = [kwargs[c] for c in cols]
    pairs.append("updated_at = ?")
    params.append(now)
    params.append(agent_id)

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_agent_schema(conn)
            cur = conn.execute(
                f"UPDATE agent SET {', '.join(pairs)} WHERE agent_id = ?", tuple(params)
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def delete_agent(agent_id: str) -> bool:
    """Delete an agent by agent_id. Returns True if deleted, False if not found."""
    def _with_conn() -> bool:
        conn = _get_connection()
        try:
            _ensure_agent_schema(conn)
            cur = conn.execute("DELETE FROM agent WHERE agent_id = ?", (agent_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def count_agent_task_refs(agent_id: str) -> int:
    """Return the number of agent_task rows referencing this agent_id."""
    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_agent_task_schema(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM agent_task WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            return row[0]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


# ---------------------------------------------------------------------------
# Agent Task table: per-task prompt content (managed via Manage Tasks UI)
# ---------------------------------------------------------------------------

def _agent_task_run_next_edges(conn: sqlite3.Connection) -> Dict[str, str]:
    """Directed edges task_key -> run_next for current rows (non-empty, TASK_CONFIG keys only)."""
    rows = conn.execute(
        "SELECT task_key, run_next FROM agent_task WHERE current = 1"
    ).fetchall()
    edges: Dict[str, str] = {}
    for tk, rn in rows:
        dst = (rn or "").strip()
        if not dst:
            continue
        if tk not in TASK_CONFIG or dst not in TASK_CONFIG:
            # Ignore malformed historical rows here; saves still validate dst independently.
            continue
        edges[str(tk)] = dst
    return edges


def _validate_run_next_graph_acyclic(edges: Dict[str, str]) -> None:
    """Raise if run_next pointers contain a directed cycle (would repeat tasks in some chain)."""
    nodes = set(edges.keys()) | set(edges.values())
    if not nodes:
        return
    indeg: Dict[str, int] = {n: 0 for n in nodes}
    for src, dst in edges.items():
        indeg[dst] = indeg.get(dst, 0) + 1
    q = [n for n, d in indeg.items() if d == 0]
    seen = 0
    while q:
        cur = q.pop()
        seen += 1
        nxt = edges.get(cur)
        if not nxt:
            continue
        indeg[nxt] -= 1
        if indeg[nxt] == 0:
            q.append(nxt)
    if seen != len(nodes):
        raise ValueError("run_next links contain a cycle — a daisy chain would repeat a task")


def _validate_run_next(conn: sqlite3.Connection, task_key: str, run_next: Optional[str]) -> None:
    """Validate run_next before persist. None = omit at API level; '' after strip = clear chain."""
    if run_next is None:
        return
    s = (run_next or "").strip()
    if s == "":
        return
    if s == task_key:
        raise ValueError("run_next cannot equal task_key (self-loop)")
    if s not in TASK_CONFIG:
        raise ValueError(f"run_next must be a configured task_key, got {s!r}")

    edges = _agent_task_run_next_edges(conn)
    # Apply this save to the edge set in-memory before checking global acyclicity.
    edges[task_key] = s
    _validate_run_next_graph_acyclic(edges)


# AST-561: analysis_upshot JSON field guidance (Manage Tasks user_prompt seed / take_jd patch).
_AST561_TAKE_JD_PROMPT_LINE = (
    "- **take_jd** (string, required): Estelle's thoughts for the **JD** phase — candidate-facing "
    "narrative explaining what stands out about this job listing and role definition after JD consult, "
    "in the same voice and depth as **take_do**, **take_get**, and **take_like**. Place JD-phase rubric "
    "context in mind but do not dump raw grades. This is **not** **whole_jd_upshot** (overall job summary).\n"
)

_AST561_ANALYSIS_UPSHOT_USER_PROMPT_SEED = """## AGENT MESSAGE

{$SELECTED_AGENT}

## INSTRUCTIONS

Synthesize a **job analysis upshot** for {$FIRST_NAME} from the consult recap and listing context in the content blocks below. Respond with **one JSON object only** (no markdown fences, no commentary outside JSON).

### Required top-level keys

- **take_jd** (string, required): Estelle's thoughts for the **JD** phase — candidate-facing narrative explaining what stands out about this job listing and role definition after JD consult, in the same voice and depth as **take_do**, **take_get**, and **take_like**. Place JD-phase rubric context in mind but do not dump raw grades. This is **not** **whole_jd_upshot** (overall job summary).
- **take_do** (string, required): Estelle's thoughts for the **DO** phase — candidate-facing narrative on day-to-day fit and role demands (thoughts above vectors; not a grade dump).
- **take_get** (string, required): Estelle's thoughts for the **GET** phase — candidate-facing narrative on what {$FIRST_NAME} would gain and grow into.
- **take_like** (string, required): Estelle's thoughts for the **LIKE** phase — candidate-facing narrative on mutual enthusiasm and chemistry signals.
- **whole_jd_upshot** (string, required): Short overall job summary for the candidate (one cohesive upshot of the listing).
- **segment_upshots** (array, required): Objects with **segment_key** (string) and **upshot** (string) for noteworthy JD segments.
- **candidate_questions** (array, required): Objects with **text** (string) — questions {$FIRST_NAME} should ask the hiring manager.
- **caveats** (array, required): Objects with **text** (string) — honest caveats or risks to flag.

Write in direct, second-person or candidate-addressed prose consistent with other Estelle consult outputs. Use the recap grades and notes as input; synthesize — do not paste rubric tables.

We appreciate you!

-The Astral Team
"""


def _patch_ast561_take_jd_into_prompt(text: str) -> str:
    """Insert take_jd bullet before take_do when prose exists but take_jd is missing."""
    if "take_jd" in text:
        return text
    for anchor in ("- **take_do**", "**take_do**", "take_do"):
        idx = text.find(anchor)
        if idx >= 0:
            return text[:idx] + _AST561_TAKE_JD_PROMPT_LINE + text[idx:]
    return text + "\n\n### take_jd (AST-561)\n\n" + _AST561_TAKE_JD_PROMPT_LINE


def _apply_ast561_analysis_upshot_take_jd_migration(conn: sqlite3.Connection) -> None:
    """AST-561: version analysis_upshot user_prompt with take_jd; seed when row exists but prose empty."""
    try:
        row = conn.execute(
            """SELECT agent_id, user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c,
                      cache_prompt_d, nocache_prompt, system_prompt, run_next
               FROM agent_task WHERE task_key = 'analysis_upshot' AND current = 1 LIMIT 1"""
        ).fetchone()
    except sqlite3.Error:
        return
    if not row:
        return
    up_raw = row[1] or ""
    nc_raw = row[6] or ""
    if "take_jd" in up_raw or "take_jd" in nc_raw:
        return
    if not up_raw.strip() and not nc_raw.strip():
        new_up = _AST561_ANALYSIS_UPSHOT_USER_PROMPT_SEED.strip()
        new_nc = nc_raw
    else:
        new_up = _patch_ast561_take_jd_into_prompt(up_raw) if up_raw.strip() else up_raw
        new_nc = _patch_ast561_take_jd_into_prompt(nc_raw) if nc_raw.strip() else nc_raw
    _save_agent_task_on_connection(
        conn,
        "analysis_upshot",
        now=_utc_now(),
        agent_id=row[0],
        user_prompt=new_up,
        cache_prompt=row[2],
        cache_prompt_b=row[3],
        cache_prompt_c=row[4],
        cache_prompt_d=row[5],
        nocache_prompt=new_nc,
        run_next=row[8],
        system_prompt=row[7],
    )
    conn.commit()


def _apply_ast469_select_job_page_run_next_migration(conn: sqlite3.Connection) -> None:
    """AST-469: select_job_page chains to parse_job_list in roster; set run_next when blank (idempotent)."""
    try:
        row = conn.execute(
            "SELECT task_key_uuid, run_next FROM agent_task WHERE task_key = 'select_job_page' AND current = 1 LIMIT 1"
        ).fetchone()
    except sqlite3.Error:
        return
    if not row:
        return
    if (row[1] or "").strip():
        return
    try:
        _validate_run_next(conn, "select_job_page", "parse_job_list")
    except ValueError:
        return
    conn.execute(
        "UPDATE agent_task SET run_next = ?, updated_at = CURRENT_TIMESTAMP WHERE task_key_uuid = ?",
        ("parse_job_list", row[0]),
    )
    conn.commit()


def _ensure_agent_task_schema(conn: sqlite3.Connection) -> None:
    """Create agent_task table if not present. Migrates old single-row schema to versioned schema."""
    global _agent_task_schema_ensured
    if _agent_task_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='agent_task'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE agent_task (
                task_key_uuid TEXT PRIMARY KEY,
                task_key TEXT NOT NULL,
                current INTEGER DEFAULT 1,
                agent_id TEXT,
                user_prompt TEXT,
                cache_prompt TEXT,
                cache_prompt_b TEXT NOT NULL DEFAULT '',
                cache_prompt_c TEXT NOT NULL DEFAULT '',
                cache_prompt_d TEXT NOT NULL DEFAULT '',
                nocache_prompt TEXT,
                system_prompt TEXT NOT NULL DEFAULT '',
                run_next TEXT NOT NULL DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_task_key_current ON agent_task(task_key, current)")
        conn.commit()
    else:
        # Migrate old schema (task_key PK, no task_key_uuid/current) to versioned schema
        cols = {row[1] for row in conn.execute("PRAGMA table_info(agent_task)").fetchall()}
        if "task_key_uuid" not in cols:
            conn.execute("ALTER TABLE agent_task RENAME TO agent_task_v1")
            conn.execute("""
                CREATE TABLE agent_task (
                    task_key_uuid TEXT PRIMARY KEY,
                    task_key TEXT NOT NULL,
                    current INTEGER DEFAULT 1,
                    agent_id TEXT,
                    user_prompt TEXT,
                    cache_prompt TEXT,
                    cache_prompt_b TEXT NOT NULL DEFAULT '',
                    cache_prompt_c TEXT NOT NULL DEFAULT '',
                    cache_prompt_d TEXT NOT NULL DEFAULT '',
                    nocache_prompt TEXT,
                    system_prompt TEXT NOT NULL DEFAULT '',
                    run_next TEXT NOT NULL DEFAULT '',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_task_key_current ON agent_task(task_key, current)")
            # Migrate existing rows, generating UUIDs, all set current=1
            old_rows = conn.execute("SELECT task_key, agent_id, user_prompt, cache_prompt, nocache_prompt, updated_at FROM agent_task_v1").fetchall()
            for row in old_rows:
                conn.execute(
                    "INSERT INTO agent_task (task_key_uuid, task_key, current, agent_id, user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c, cache_prompt_d, nocache_prompt, system_prompt, run_next, updated_at) VALUES (?, ?, 1, ?, ?, ?, '', '', '', ?, '', '', ?)",
                    (str(uuid.uuid4()), row[0], row[1], row[2], row[3], row[4], row[5]),
                )
            conn.commit()
        cols = {row[1] for row in conn.execute("PRAGMA table_info(agent_task)").fetchall()}
        if "run_next" not in cols:
            conn.execute("ALTER TABLE agent_task ADD COLUMN run_next TEXT NOT NULL DEFAULT ''")
            conn.commit()
        cols = {row[1] for row in conn.execute("PRAGMA table_info(agent_task)").fetchall()}
        if "system_prompt" not in cols:
            conn.execute("ALTER TABLE agent_task ADD COLUMN system_prompt TEXT NOT NULL DEFAULT ''")
            conn.commit()
        cols = {row[1] for row in conn.execute("PRAGMA table_info(agent_task)").fetchall()}
        for _seg in ("cache_prompt_b", "cache_prompt_c", "cache_prompt_d"):
            if _seg not in cols:
                conn.execute(f"ALTER TABLE agent_task ADD COLUMN {_seg} TEXT NOT NULL DEFAULT ''")
                conn.commit()
            cols = {row[1] for row in conn.execute("PRAGMA table_info(agent_task)").fetchall()}
    _apply_ast469_select_job_page_run_next_migration(conn)
    _apply_ast561_analysis_upshot_take_jd_migration(conn)
    _agent_task_schema_ensured = True


def _save_agent_task_on_connection(
    conn: sqlite3.Connection,
    task_key: str,
    *,
    now: str,
    agent_id: Optional[str] = None,
    user_prompt: Optional[str] = None,
    cache_prompt: Optional[str] = None,
    cache_prompt_b: Optional[str] = None,
    cache_prompt_c: Optional[str] = None,
    cache_prompt_d: Optional[str] = None,
    nocache_prompt: Optional[str] = None,
    run_next: Optional[str] = None,
    system_prompt: Optional[str] = None,
    import_explicit: bool = False,
) -> None:
    """Upsert logic for Manage Tasks semantics on caller-owned ``conn`` (no commit / close).

    Caller must have run ``_ensure_agent_task_schema`` if needed.
    ``import_explicit`` — kwargs are pasted rows (Copy Output): ``None`` means empty value,
    not “leave untouched” (used by ``apply_agent_task_copy_upsert`` only).
    """
    def _strip_seg(s: Optional[str]) -> str:
        return (s if s is not None else "").strip()

    def _strip_sys(s: Optional[str]) -> str:
        return (s or "").strip()

    def _imp_str(v: Optional[str]) -> str:
        return "" if v is None else (v if isinstance(v, str) else str(v))

    sel = """SELECT task_key_uuid, agent_id, user_prompt, cache_prompt,
                    cache_prompt_b, cache_prompt_c, cache_prompt_d,
                    nocache_prompt, run_next, system_prompt
             FROM agent_task WHERE task_key = ? AND current = 1"""
    existing = conn.execute(sel, (task_key,)).fetchone()
    if existing is None:
        if import_explicit:
            ins_ag = "" if agent_id is None else (agent_id if isinstance(agent_id, str) else str(agent_id))
            ins_rn = ("" if run_next is None else (run_next if isinstance(run_next, str) else str(run_next))).strip()
            ins_sp = _strip_sys("" if system_prompt is None else _imp_str(system_prompt))  # type: ignore[arg-type]
            pup, pcp = _imp_str(user_prompt), _imp_str(cache_prompt)
            pnp = _imp_str(nocache_prompt)
        else:
            ins_ag = agent_id or ""
            ins_rn = run_next.strip() if run_next is not None else ""
            ins_sp = system_prompt.strip() if system_prompt is not None else ""
            pup = user_prompt or ""
            pcp = cache_prompt or ""
            pnp = nocache_prompt or ""
        _validate_run_next(conn, task_key, ins_rn if ins_rn else None)
        conn.execute(
            """INSERT INTO agent_task (
                task_key_uuid, task_key, current, agent_id,
                user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c, cache_prompt_d,
                nocache_prompt, system_prompt, run_next, updated_at)
               VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid.uuid4()),
                task_key,
                ins_ag,
                pup,
                pcp,
                (
                    _strip_seg(cache_prompt_b if cache_prompt_b is not None else "")
                    if import_explicit
                    else _strip_seg(cache_prompt_b) if cache_prompt_b is not None else ""
                ),
                (
                    _strip_seg(cache_prompt_c if cache_prompt_c is not None else "")
                    if import_explicit
                    else _strip_seg(cache_prompt_c) if cache_prompt_c is not None else ""
                ),
                (
                    _strip_seg(cache_prompt_d if cache_prompt_d is not None else "")
                    if import_explicit
                    else _strip_seg(cache_prompt_d) if cache_prompt_d is not None else ""
                ),
                pnp,
                ins_sp,
                ins_rn,
                now,
            ),
        )
    else:
        eu, ea, eb, ec, ed, en = (
            existing[2],
            existing[3],
            existing[4],
            existing[5],
            existing[6],
            existing[7],
        )
        if import_explicit:
            new_up = _imp_str(user_prompt)
            new_cp = _imp_str(cache_prompt)
            seg_b_src = cache_prompt_b if cache_prompt_b is not None else ""
            seg_c_src = cache_prompt_c if cache_prompt_c is not None else ""
            seg_d_src = cache_prompt_d if cache_prompt_d is not None else ""
            new_cb, new_cc, new_cd = _strip_seg(seg_b_src), _strip_seg(seg_c_src), _strip_seg(seg_d_src)
            new_np = _imp_str(nocache_prompt)
            new_rn = ("" if run_next is None else (run_next if isinstance(run_next, str) else str(run_next))).strip()
            prev_sys = _strip_sys(existing[9])
            new_sp = _strip_sys(_imp_str(system_prompt))
            ver_agent = "" if agent_id is None else (agent_id if isinstance(agent_id, str) else str(agent_id))
        else:
            new_up = user_prompt if user_prompt is not None else eu
            new_cp = cache_prompt if cache_prompt is not None else ea
            new_cb = _strip_seg(cache_prompt_b) if cache_prompt_b is not None else eb
            new_cc = _strip_seg(cache_prompt_c) if cache_prompt_c is not None else ec
            new_cd = _strip_seg(cache_prompt_d) if cache_prompt_d is not None else ed
            new_np = nocache_prompt if nocache_prompt is not None else en
            new_rn = run_next.strip() if run_next is not None else (existing[8] or "")
            prev_sys = _strip_sys(existing[9])
            new_sp = _strip_sys(system_prompt) if system_prompt is not None else prev_sys
            ver_agent = agent_id or existing[1] or ""
        content_changed = (
            new_up != eu
            or new_cp != ea
            or new_cb != eb
            or new_cc != ec
            or new_cd != ed
            or new_np != en
            or new_sp != prev_sys
        )
        if content_changed:
            if (new_rn or "").strip():
                _validate_run_next(conn, task_key, new_rn)
            conn.execute("UPDATE agent_task SET current = 0 WHERE task_key_uuid = ?", (existing[0],))
            conn.execute(
                """INSERT INTO agent_task (
                    task_key_uuid, task_key, current, agent_id,
                    user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c, cache_prompt_d,
                    nocache_prompt, system_prompt, run_next, updated_at)
                   VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    task_key,
                    ver_agent,
                    new_up,
                    new_cp,
                    new_cb,
                    new_cc,
                    new_cd,
                    new_np,
                    new_sp,
                    new_rn,
                    now,
                ),
            )
        else:
            sets, params = ["updated_at = ?"], [now]
            if import_explicit:
                ea_db = existing[1] if existing[1] is not None else ""
                rn_db = existing[8] if existing[8] is not None else ""
                if ver_agent != ea_db:
                    sets.append("agent_id = ?")
                    params.append(ver_agent)
                if new_rn != rn_db:
                    _validate_run_next(conn, task_key, new_rn)
                    sets.append("run_next = ?")
                    params.append(new_rn)
            else:
                if agent_id is not None:
                    sets.append("agent_id = ?")
                    params.append(agent_id)
                if run_next is not None:
                    _validate_run_next(conn, task_key, run_next)
                    sets.append("run_next = ?")
                    params.append(run_next.strip())
            params.append(existing[0])
            conn.execute(f"UPDATE agent_task SET {', '.join(sets)} WHERE task_key_uuid = ?", params)


def save_agent_task(
    task_key: str,
    *,
    agent_id: Optional[str] = None,
    user_prompt: Optional[str] = None,
    cache_prompt: Optional[str] = None,
    cache_prompt_b: Optional[str] = None,
    cache_prompt_c: Optional[str] = None,
    cache_prompt_d: Optional[str] = None,
    nocache_prompt: Optional[str] = None,
    run_next: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> None:
    """Upsert agent_task with versioning. Any change among the seven prompt segments versions the row.

    Metadata without segment edits: agent_id / run_next only — updates `updated_at`, no retire.
    All kwargs use ``None`` = leave existing value untouched (same as PUT no-key semantics)."""
    now = _utc_now()

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_agent_task_schema(conn)
            _save_agent_task_on_connection(
                conn,
                task_key,
                now=now,
                agent_id=agent_id,
                user_prompt=user_prompt,
                cache_prompt=cache_prompt,
                cache_prompt_b=cache_prompt_b,
                cache_prompt_c=cache_prompt_c,
                cache_prompt_d=cache_prompt_d,
                nocache_prompt=nocache_prompt,
                run_next=run_next,
                system_prompt=system_prompt,
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def get_agent_task(task_key: str) -> Optional[Dict[str, Any]]:
    """Return current agent_task version by task_key, or None."""
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_task_schema(conn)
            row = conn.execute(
                "SELECT * FROM agent_task WHERE task_key = ? AND current = 1", (task_key,)
            ).fetchone()
            return _row_to_dict(row) if row else None
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def list_candidate_tasks() -> List[Dict[str, Any]]:
    """Return all current agent_task versions with char counts for prompt fields."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_task_schema(conn)
            rows = conn.execute("""
                SELECT task_key_uuid, task_key, agent_id,
                       LENGTH(user_prompt) AS user_prompt_len,
                       LENGTH(cache_prompt) AS cache_prompt_len,
                       LENGTH(COALESCE(cache_prompt_b, '')) AS cache_prompt_b_len,
                       LENGTH(COALESCE(cache_prompt_c, '')) AS cache_prompt_c_len,
                       LENGTH(COALESCE(cache_prompt_d, '')) AS cache_prompt_d_len,
                       LENGTH(nocache_prompt) AS nocache_prompt_len,
                       LENGTH(system_prompt) AS system_prompt_len,
                       run_next,
                       updated_at
                FROM agent_task WHERE current = 1 ORDER BY task_key
            """).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def sync_agent_tasks(task_keys: list) -> None:
    """Ensure every task_key has a current row. Inserts blank records for missing keys."""
    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_agent_task_schema(conn)
            existing = {row[0] for row in conn.execute("SELECT task_key FROM agent_task WHERE current = 1").fetchall()}
            now = _utc_now()
            for key in task_keys:
                if key not in existing:
                    conn.execute(
                        """INSERT INTO agent_task (
                            task_key_uuid, task_key, current, agent_id,
                            user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c, cache_prompt_d,
                            nocache_prompt, system_prompt, run_next, updated_at)
                           VALUES (?, ?, 1, '', '', '', '', '', '', '', '', '', ?)""",
                        (str(uuid.uuid4()), key, now),
                    )
            conn.commit()
        finally:
            conn.close()
    _run_with_retry(_with_conn)


# ---------------------------------------------------------------------------
# Agent Data
# ---------------------------------------------------------------------------

def _ensure_agent_data_schema(conn: sqlite3.Connection) -> None:
    """Create agent_data table + index if not present. Idempotent."""
    global _agent_data_schema_ensured
    if _agent_data_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='agent_data'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE agent_data (
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
        conn.execute("CREATE INDEX idx_agent_data_batch ON agent_data(batch_id)")
        conn.commit()
    _agent_data_schema_ensured = True


def save_agent_data(
    agent_data_id: str,
    entity_type: str,
    task_key: str,
    batch_id: str,
    block_type: str,
    block_data: str,
    token_size: int = 0,
    created_at: Optional[str] = None,
) -> bool:
    """Insert a single content block into agent_data. Returns True on success, False on duplicate.
    block_data is compressed before storage. block_type must be in BLOCK_TYPES."""
    if block_type not in BLOCK_TYPES:
        raise ValueError(f"Invalid block_type '{block_type}'. Must be one of: {BLOCK_TYPES}")
    ts = created_at or _utc_now()
    blob = _compress_payload(block_data)
    def _with_conn() -> bool:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            conn.execute(
                """INSERT OR IGNORE INTO agent_data
                   (agent_data_id, entity_type, task_key, batch_id, created_at, block_type, block_data, token_size)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (agent_data_id, entity_type, task_key, batch_id, ts, block_type, blob, token_size),
            )
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_agent_data_by_batch(
    batch_id: str,
    block_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return all agent_data rows for a batch, optionally filtered by block_type.
    block_data is decompressed before return."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            if block_type:
                rows = conn.execute(
                    "SELECT * FROM agent_data WHERE batch_id = ? AND block_type = ? ORDER BY created_at",
                    (batch_id, block_type),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM agent_data WHERE batch_id = ? ORDER BY created_at",
                    (batch_id,),
                ).fetchall()
            result = []
            for row in rows:
                d = _row_to_dict(row)
                d["block_data"] = _decompress_payload(d["block_data"])
                result.append(d)
            return result
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_agent_data(agent_data_id: str) -> Optional[Dict[str, Any]]:
    """Return a single agent_data row by primary key. block_data is decompressed."""
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            row = conn.execute(
                "SELECT * FROM agent_data WHERE agent_data_id = ?", (agent_data_id,)
            ).fetchone()
            if not row:
                return None
            d = _row_to_dict(row)
            d["block_data"] = _decompress_payload(d["block_data"])
            return d
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def append_agent_response(entity_type: str, entity_id: str, entry: Dict[str, Any]) -> None:
    """Append an agent_response entry to the entity's agent_responses JSON array.
    Works for company, job, and candidate tables. entry is a lightweight dict
    (batch_id, task_key, created_at, entity_cost, prompt_blocks)."""
    _TABLE_MAP = {
        "company":   ("company",   "short_name"),
        "job":       ("job",       "astral_job_id"),
        "candidate": ("candidate", "astral_candidate_id"),
    }
    if entity_type not in _TABLE_MAP:
        raise ValueError(f"Unknown entity_type '{entity_type}'. Must be one of: {list(_TABLE_MAP.keys())}")
    table, pk_col = _TABLE_MAP[entity_type]

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            if table == "company":
                _ensure_company_schema(conn)
            elif table == "job":
                _ensure_job_schema(conn)
            else:
                _ensure_candidate_schema(conn)
            row = conn.execute(
                f"SELECT agent_responses FROM {table} WHERE {pk_col} = ?", (entity_id,)
            ).fetchone()
            if not row:
                return
            existing = []
            if row[0]:
                try:
                    parsed = json.loads(row[0])
                    # Coerce non-list (e.g. "{}" from bad default) to empty list
                    existing = parsed if isinstance(parsed, list) else []
                except (TypeError, ValueError):
                    existing = []
            existing.append(entry)
            conn.execute(
                f"UPDATE {table} SET agent_responses = ? WHERE {pk_col} = ?",
                (json.dumps(existing), entity_id),
            )
            conn.commit()
        finally:
            conn.close()
    _run_with_retry(_with_conn)


# ---------------------------------------------------------------------------
# Dispatch Ledger
# ---------------------------------------------------------------------------

def _ensure_dispatch_ledger_schema(conn: sqlite3.Connection) -> None:
    """Create dispatch_ledger table if not present; migrate missing columns. Idempotent."""
    global _dispatch_ledger_schema_ensured
    if _dispatch_ledger_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dispatch_ledger'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE dispatch_ledger (
                batch_id          TEXT PRIMARY KEY,
                task_key          TEXT,
                candidate_id      TEXT,
                entity_type       TEXT,
                batch_size        INTEGER,
                started_at        TIMESTAMP,
                completed_at      TIMESTAMP,
                status            TEXT,
                total_processed   INTEGER DEFAULT 0,
                total_passed      INTEGER DEFAULT 0,
                total_failed      INTEGER DEFAULT 0,
                total_errors      INTEGER DEFAULT 0,
                agent_performance TEXT,
                agent_note        TEXT,
                total_cost        REAL DEFAULT 0.0,
                entity_cost       REAL DEFAULT 0.0,
                prompt_blocks     TEXT
            )
        """)
        conn.commit()
    else:
        # Migrate pre-existing table: add new columns if absent
        existing = {row[1] for row in conn.execute("PRAGMA table_info(dispatch_ledger)").fetchall()}
        migrations = [
            ("entity_type",       "TEXT"),
            ("batch_size",        "INTEGER"),
            ("agent_performance", "TEXT"),
            ("agent_note",        "TEXT"),
            ("total_cost",        "REAL DEFAULT 0.0"),
            ("entity_cost",       "REAL DEFAULT 0.0"),
            ("prompt_blocks",     "TEXT"),
        ]
        for col, col_def in migrations:
            if col not in existing:
                conn.execute(f"ALTER TABLE dispatch_ledger ADD COLUMN {col} {col_def}")
        conn.commit()
    _dispatch_ledger_schema_ensured = True


def save_dispatch_ledger(
    batch_id: str,
    task_key: str,
    candidate_id: str,
    started_at: str,
    status: str = "RUNNING",
    entity_type: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> bool:
    """Insert a new dispatch_ledger record. Returns True on success, False on duplicate."""
    def _with_conn() -> bool:
        conn = _get_connection()
        try:
            _ensure_dispatch_ledger_schema(conn)
            conn.execute("""
                INSERT OR IGNORE INTO dispatch_ledger
                (batch_id, task_key, candidate_id, entity_type, batch_size, started_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (batch_id, task_key, candidate_id, entity_type, batch_size, started_at, status))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


_LEDGER_UPDATE_COLS = {
    "completed_at", "status",
    "total_processed", "total_passed", "total_failed", "total_errors",
    "agent_performance", "agent_note", "total_cost", "entity_cost", "prompt_blocks",
    "batch_size",
}


def update_dispatch_ledger(batch_id: str, **kwargs) -> None:
    """Update fields on an existing dispatch_ledger record.
    Validates column names against _LEDGER_UPDATE_COLS to catch typos."""
    if not kwargs:
        return
    bad = set(kwargs) - _LEDGER_UPDATE_COLS
    if bad:
        raise ValueError(f"Invalid dispatch_ledger columns: {bad}")
    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_dispatch_ledger_schema(conn)
            pairs = [f"{k} = ?" for k in kwargs]
            vals = list(kwargs.values()) + [batch_id]
            conn.execute(
                f"UPDATE dispatch_ledger SET {', '.join(pairs)} WHERE batch_id = ?", vals
            )
            conn.commit()
        finally:
            conn.close()
    _run_with_retry(_with_conn)


def mark_stale_ledger_interrupted(now_iso: str) -> int:
    """On startup, clean up after any crashed/redeployed process:
    1. Find all RUNNING ledger rows (orphaned batch IDs).
    2. Release batch_id locks on company and job rows for those batches.
    3. Mark those ledger rows INTERRUPTED.
    All in one transaction. Returns number of ledger rows updated."""
    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_dispatch_ledger_schema(conn)
            rows = conn.execute(
                "SELECT batch_id FROM dispatch_ledger WHERE status = 'RUNNING'"
            ).fetchall()
            if not rows:
                return 0
            batch_ids = [r[0] for r in rows]
            placeholders = ",".join("?" * len(batch_ids))
            conn.execute(
                f"UPDATE company SET batch_id = NULL, batch_created_at = NULL WHERE batch_id IN ({placeholders})",
                batch_ids,
            )
            conn.execute(
                f"UPDATE job SET batch_id = NULL, batch_created_at = NULL WHERE batch_id IN ({placeholders})",
                batch_ids,
            )
            conn.execute(
                f"UPDATE dispatch_ledger SET status = 'INTERRUPTED', completed_at = ? WHERE batch_id IN ({placeholders})",
                [now_iso] + batch_ids,
            )
            conn.commit()
            return len(batch_ids)
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_dispatch_ledger(batch_id: str) -> Optional[Dict[str, Any]]:
    """Return single dispatch_ledger record by batch_id, or None."""
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_dispatch_ledger_schema(conn)
            row = conn.execute(
                "SELECT * FROM dispatch_ledger WHERE batch_id = ?", (batch_id,)
            ).fetchone()
            return _row_to_dict(row) if row else None
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def list_dispatch_ledger(
    task_key: Optional[str] = None,
    candidate_id: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query dispatch_ledger with optional filters. Returns newest first."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_dispatch_ledger_schema(conn)
            clauses: List[str] = []
            params: List[Any] = []
            if task_key:
                clauses.append("task_key = ?")
                params.append(task_key)
            if candidate_id:
                clauses.append("candidate_id = ?")
                params.append(candidate_id)
            if status:
                clauses.append("status = ?")
                params.append(status)
            if date_from:
                clauses.append("started_at >= ?")
                params.append(date_from)
            if date_to:
                clauses.append("started_at <= ?")
                params.append(f"{date_to}T23:59:59")
            where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
            rows = conn.execute(
                f"SELECT * FROM dispatch_ledger{where} ORDER BY started_at DESC", params
            ).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_recent_ledger_summaries(task_key: str, candidate_id: str, n: int = 3) -> List[Dict[str, Any]]:
    """Return the last N completed ledger entries for a task+candidate, newest first."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_dispatch_ledger_schema(conn)
            rows = conn.execute(
                """SELECT total_processed, total_passed, total_failed FROM dispatch_ledger
                   WHERE task_key = ? AND candidate_id = ? AND status = 'COMPLETED'
                     AND total_processed > 0
                   ORDER BY completed_at DESC LIMIT ?""",
                (task_key, candidate_id, n),
            ).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


# ---------------------------------------------------------------------------
# App Log
# ---------------------------------------------------------------------------

def _ensure_app_log_schema(conn: sqlite3.Connection) -> None:
    """Create app_log table if not present. Idempotent."""
    global _app_log_schema_ensured
    if _app_log_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='app_log'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE app_log (
                id TEXT PRIMARY KEY,
                level TEXT,
                logger_name TEXT,
                message TEXT,
                batch_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    _app_log_schema_ensured = True


def add_log_entry(
    level: str,
    logger_name: str,
    message: str,
    batch_id: Optional[str] = None,
) -> bool:
    """Append a log entry. Fast write path; caller ensures valid data."""
    entry_id = str(uuid.uuid4())
    conn = _get_connection()
    try:
        _ensure_app_log_schema(conn)
        conn.execute("""
            INSERT OR IGNORE INTO app_log (id, level, logger_name, message, batch_id)
            VALUES (?, ?, ?, ?, ?)
        """, (entry_id, level, logger_name, message, batch_id))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def list_log_entries(
    batch_id: Optional[str] = None,
    level: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query app_log with optional filters. Returns newest first."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_app_log_schema(conn)
            clauses: List[str] = []
            params: List[Any] = []
            if batch_id:
                clauses.append("batch_id = ?")
                params.append(batch_id)
            if level:
                clauses.append("level = ?")
                params.append(level)
            if date_from:
                clauses.append("created_at >= ?")
                params.append(date_from)
            if date_to:
                clauses.append("created_at <= ?")
                params.append(f"{date_to}T23:59:59")
            where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
            rows = conn.execute(
                f"SELECT * FROM app_log{where} ORDER BY created_at DESC", params
            ).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


# ---------------------------------------------------------------------------
# Dispatch Task (scheduling config)
# ---------------------------------------------------------------------------

# task_key to copy settings from → new trigger_state for each retry task
_RETRY_TASK_SEED = [
    ("qualify_job_listings", "VALID_TITLE_RETRY"),
    ("evaluate_jd",          "JD_READY_RETRY"),
    ("fetch_website",        "WEBSITE_FOUND_RETRY"),
]


def _ensure_gaze_board_dispatch_tasks(conn: sqlite3.Connection) -> None:
    """INSERT OR IGNORE gaze_board rows — copy gaze settings per candidate / board_search fallback (AST-471)."""
    try:
        gb = dispatch_task_admin_defaults("gaze_board")
    except KeyError:
        return
    _ensure_board_search_table(conn)
    now = _utc_now()
    def_bs = int((BOARDS_CONFIG.get("gaze_board") or {}).get("batch_size") or 5)
    gaze_rows = conn.execute(
        """SELECT candidate_id, min_count, freq_hrs, batch_size, auto_mode, debug, skip_cache, max_runs
           FROM dispatch_task WHERE task_key = 'gaze'"""
    ).fetchall()
    have_gaze: set[Any] = set()
    for r in gaze_rows:
        cid = r[0]
        have_gaze.add(cid)
        mn, fq, bs, am, dbg, sk, mr = r[1:]
        bsz = def_bs if bs is None else int(bs)
        conn.execute(
            """INSERT OR IGNORE INTO dispatch_task
               (candidate_id, task_key, entity_type, trigger_state, sort_by, batch_call_mode,
                min_count, freq_hrs, batch_size, auto_mode, debug, skip_cache, max_runs, updated_at)
               VALUES (?, 'gaze_board', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (cid, gb["entity_type"], gb["trigger_state"], gb["sort_by"], gb["batch_call_mode"],
             mn, fq, bsz, am, dbg, sk, mr, now),
        )
    if gaze_rows:
        conn.commit()

    bs_cands = conn.execute(
        """SELECT DISTINCT candidate_id FROM board_search
           WHERE candidate_id IS NOT NULL AND TRIM(candidate_id) != ''"""
    ).fetchall()
    for (cid,) in bs_cands:
        if cid in have_gaze:
            continue
        conn.execute(
            """INSERT OR IGNORE INTO dispatch_task
               (candidate_id, task_key, entity_type, trigger_state, sort_by, batch_call_mode,
                min_count, freq_hrs, batch_size, auto_mode, debug, skip_cache, max_runs, updated_at)
               VALUES (?, 'gaze_board', ?, ?, ?, ?, 1, 0, ?, 0, 0, 0, 1, ?)""",
            (cid, gb["entity_type"], gb["trigger_state"], gb["sort_by"], gb["batch_call_mode"],
             def_bs, now),
        )
    if bs_cands:
        conn.commit()


def _ensure_dispatch_task_schema(conn: sqlite3.Connection) -> None:
    """Create dispatch_task table if not present; run column migrations. Idempotent."""
    global _dispatch_task_schema_ensured
    if _dispatch_task_schema_ensured:
        return
    cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dispatch_task'")
    if cursor.fetchone()[0] == 0:
        conn.execute("""
            CREATE TABLE dispatch_task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                task_key TEXT NOT NULL,
                entity_type TEXT,
                trigger_state TEXT,
                sort_by TEXT,
                batch_call_mode INTEGER DEFAULT 0,
                last_run_at TIMESTAMP,
                freq_hrs REAL DEFAULT 0,
                min_count INTEGER NOT NULL,
                batch_size INTEGER,
                batch_id TEXT,
                auto_mode INTEGER NOT NULL DEFAULT 0,
                debug INTEGER NOT NULL DEFAULT 0,
                skip_cache INTEGER NOT NULL DEFAULT 0,
                max_runs INTEGER DEFAULT 1,
                score_floor REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(candidate_id, task_key, trigger_state)
            )
        """)
        conn.commit()
    else:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(dispatch_task)").fetchall()}
        # Rename enabled -> auto_mode via full table rebuild (SQLite has no ALTER COLUMN RENAME)
        if "enabled" in cols and "auto_mode" not in cols:
            conn.execute("""
                CREATE TABLE dispatch_task_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL,
                    task_key TEXT NOT NULL,
                    entity_type TEXT,
                    trigger_state TEXT,
                    sort_by TEXT,
                    batch_call_mode INTEGER DEFAULT 0,
                    last_run_at TIMESTAMP,
                    freq_hrs REAL DEFAULT 0,
                    min_count INTEGER NOT NULL,
                    batch_size INTEGER,
                    batch_id TEXT,
                    auto_mode INTEGER NOT NULL DEFAULT 0,
                    debug INTEGER NOT NULL DEFAULT 0,
                    skip_cache INTEGER NOT NULL DEFAULT 0,
                    max_runs INTEGER DEFAULT 1,
                    score_floor REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(candidate_id, trigger_state)
                )
            """)
            conn.execute("""
                INSERT INTO dispatch_task_new
                    (id, candidate_id, task_key, entity_type, last_run_at, freq_hrs,
                     min_count, batch_size, batch_id, auto_mode, debug, skip_cache, max_runs, score_floor, updated_at)
                SELECT id, candidate_id, task_key, entity_type, last_run_at, freq_hrs,
                       min_count, batch_size, batch_id, enabled, debug, skip_cache, max_runs, NULL, updated_at
                FROM dispatch_task
            """)
            conn.execute("DROP TABLE dispatch_task")
            conn.execute("ALTER TABLE dispatch_task_new RENAME TO dispatch_task")
            conn.commit()
            cols = {row[1] for row in conn.execute("PRAGMA table_info(dispatch_task)").fetchall()}
        create_sql_row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='dispatch_task'"
        ).fetchone()
        create_sql = (create_sql_row[0] if create_sql_row else "") or ""
        if "UNIQUE(candidate_id, task_key)" in create_sql:
            rows = conn.execute(
                """SELECT id, candidate_id, task_key, entity_type, trigger_state, sort_by,
                          batch_call_mode, last_run_at, freq_hrs, min_count, batch_size, batch_id,
                          auto_mode, debug, skip_cache, max_runs, score_floor, updated_at
                   FROM dispatch_task
                   ORDER BY updated_at DESC, id DESC"""
            ).fetchall()
            conn.execute("""
                CREATE TABLE dispatch_task_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL,
                    task_key TEXT NOT NULL,
                    entity_type TEXT,
                    trigger_state TEXT,
                    sort_by TEXT,
                    batch_call_mode INTEGER DEFAULT 0,
                    last_run_at TIMESTAMP,
                    freq_hrs REAL DEFAULT 0,
                    min_count INTEGER NOT NULL,
                    batch_size INTEGER,
                    batch_id TEXT,
                    auto_mode INTEGER NOT NULL DEFAULT 0,
                    debug INTEGER NOT NULL DEFAULT 0,
                    skip_cache INTEGER NOT NULL DEFAULT 0,
                    max_runs INTEGER DEFAULT 1,
                    score_floor REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(candidate_id, trigger_state)
                )
            """)
            seen = set()
            for r in rows:
                key = (r[1], r[4])
                if key in seen:
                    continue
                seen.add(key)
                conn.execute(
                    """INSERT INTO dispatch_task_new
                       (id, candidate_id, task_key, entity_type, trigger_state, sort_by,
                        batch_call_mode, last_run_at, freq_hrs, min_count, batch_size, batch_id,
                        auto_mode, debug, skip_cache, max_runs, score_floor, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    tuple(r),
                )
            conn.execute("DROP TABLE dispatch_task")
            conn.execute("ALTER TABLE dispatch_task_new RENAME TO dispatch_task")
            conn.commit()
            cols = {row[1] for row in conn.execute("PRAGMA table_info(dispatch_task)").fetchall()}
        # Add any other columns that may be missing from older schemas
        _migrate_cols = {
            "entity_type":    "TEXT",
            "batch_size":     "INTEGER",
            "debug":          "INTEGER DEFAULT 0",
            "skip_cache":     "INTEGER DEFAULT 0",
            "max_runs":       "INTEGER DEFAULT 1",
            "auto_mode":      "INTEGER NOT NULL DEFAULT 0",
            "trigger_state":  "TEXT",
            "sort_by":        "TEXT",
            "batch_call_mode": "INTEGER DEFAULT 0",
            "score_floor":    "REAL",
        }
        for col, col_type in _migrate_cols.items():
            if col not in cols:
                try:
                    conn.execute(f"ALTER TABLE dispatch_task ADD COLUMN {col} {col_type}")
                    conn.commit()
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        raise
        # Backfill entity_type, trigger_state, sort_by, batch_call_mode for rows that have them NULL
        seed_rows = conn.execute(
            "SELECT id, task_key FROM dispatch_task "
            "WHERE trigger_state IS NULL OR sort_by IS NULL OR batch_call_mode IS NULL OR entity_type IS NULL"
        ).fetchall()
        for row in seed_rows:
            try:
                seed = dispatch_task_admin_defaults(row[1])
            except KeyError:
                continue
            conn.execute(
                "UPDATE dispatch_task SET entity_type = COALESCE(entity_type, ?), "
                "trigger_state = COALESCE(trigger_state, ?), "
                "sort_by = COALESCE(sort_by, ?), "
                "batch_call_mode = COALESCE(batch_call_mode, ?) WHERE id = ?",
                (seed["entity_type"], seed["trigger_state"], seed["sort_by"], seed["batch_call_mode"], row[0]),
            )
        if seed_rows:
            conn.commit()
        scored_rows = conn.execute(
            "SELECT id, task_key, trigger_state, score_floor FROM dispatch_task"
        ).fetchall()
        for row in scored_rows:
            if row[3] is not None:
                continue
            task_key = row[1] or ""
            trigger_state = row[2] or ""
            if dispatch_claim_uses_score_floor(trigger_state):
                conn.execute("UPDATE dispatch_task SET score_floor = 1.0 WHERE id = ?", (row[0],))
        if scored_rows:
            conn.commit()
        # Add retry task rows for each candidate that has the corresponding base task
        for base_key, retry_trigger in _RETRY_TASK_SEED:
            try:
                base_seed = dispatch_task_admin_defaults(base_key)
            except KeyError:
                continue
            base_rows = conn.execute(
                "SELECT candidate_id, min_count, freq_hrs, batch_size, auto_mode, debug, skip_cache, max_runs "
                "FROM dispatch_task WHERE task_key = ?",
                (base_key,),
            ).fetchall()
            for br in base_rows:
                conn.execute(
                    """INSERT OR IGNORE INTO dispatch_task
                       (candidate_id, task_key, entity_type, trigger_state, sort_by, batch_call_mode,
                        min_count, freq_hrs, batch_size, auto_mode, debug, skip_cache, max_runs, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (br[0], base_key, base_seed["entity_type"], retry_trigger,
                     base_seed["sort_by"], base_seed["batch_call_mode"],
                     br[1], br[2], br[3], br[4], br[5], br[6], br[7]),
                )
            if base_rows:
                conn.commit()
    # Legacy gaze rows used updated_at for claim order; gazer should claim oldest last_scan_at first.
    conn.execute(
        "UPDATE dispatch_task SET sort_by = 'last_scan_at' WHERE task_key = 'gaze' AND sort_by = 'updated_at'"
    )
    conn.commit()
    conn.execute(
        "UPDATE dispatch_task SET sort_by = 'last_scan_at' WHERE task_key = 'gaze_board' AND sort_by = 'updated_at'"
    )
    conn.commit()
    # AST-485: legacy locate_job_page scheduled rows → find_job_page (before NO_OPENINGS find_job_page→recheck below).
    conn.execute(
        "UPDATE dispatch_task SET task_key = 'find_job_page' WHERE task_key = 'locate_job_page'"
    )
    conn.commit()
    # Legacy NO_OPENINGS rows used task_key find_job_page + updated_at claim order; roster recheck sorts by last_scan_at.
    conn.execute(
        """UPDATE dispatch_task SET task_key = 'recheck_no_openings',
               sort_by = 'last_scan_at'
           WHERE trigger_state = 'NO_OPENINGS' AND task_key = 'find_job_page'"""
    )
    conn.commit()
    # AST-535: triple unique (candidate_id, task_key, trigger_state) replaces (candidate_id, trigger_state).
    create_sql_row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='dispatch_task'"
    ).fetchone()
    create_sql = (create_sql_row[0] if create_sql_row else "") or ""
    if (
        "UNIQUE(candidate_id, trigger_state)" in create_sql
        and "UNIQUE(candidate_id, task_key, trigger_state)" not in create_sql
    ):
        rows = conn.execute(
            """SELECT id, candidate_id, task_key, entity_type, trigger_state, sort_by,
                      batch_call_mode, last_run_at, freq_hrs, min_count, batch_size, batch_id,
                      auto_mode, debug, skip_cache, max_runs, score_floor, updated_at
               FROM dispatch_task
               ORDER BY updated_at DESC, id DESC"""
        ).fetchall()
        conn.execute("""
            CREATE TABLE dispatch_task_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                task_key TEXT NOT NULL,
                entity_type TEXT,
                trigger_state TEXT,
                sort_by TEXT,
                batch_call_mode INTEGER DEFAULT 0,
                last_run_at TIMESTAMP,
                freq_hrs REAL DEFAULT 0,
                min_count INTEGER NOT NULL,
                batch_size INTEGER,
                batch_id TEXT,
                auto_mode INTEGER NOT NULL DEFAULT 0,
                debug INTEGER NOT NULL DEFAULT 0,
                skip_cache INTEGER NOT NULL DEFAULT 0,
                max_runs INTEGER DEFAULT 1,
                score_floor REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(candidate_id, task_key, trigger_state)
            )
        """)
        seen_triple: set = set()
        for r in rows:
            triple = (r[1], r[2], r[4])
            if triple in seen_triple:
                continue
            seen_triple.add(triple)
            conn.execute(
                """INSERT INTO dispatch_task_new
                   (id, candidate_id, task_key, entity_type, trigger_state, sort_by,
                    batch_call_mode, last_run_at, freq_hrs, min_count, batch_size, batch_id,
                    auto_mode, debug, skip_cache, max_runs, score_floor, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(r),
            )
        conn.execute("DROP TABLE dispatch_task")
        conn.execute("ALTER TABLE dispatch_task_new RENAME TO dispatch_task")
        conn.commit()
    # AST-702 / AST-703: drop obsolete prefilter retry companions before retargeting base row.
    conn.execute(
        "DELETE FROM dispatch_task WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'"
    )
    conn.execute(
        "UPDATE dispatch_task SET trigger_state = 'HOMEPAGE_READY', batch_call_mode = 1 "
        "WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND'"
    )
    conn.commit()
    _ensure_gaze_board_dispatch_tasks(conn)
    _dispatch_task_schema_ensured = True


_UPSERT_SCHEMA_ENSURE_FLAGS: dict[str, tuple[str, ...]] = {
    "agent": ("_agent_schema_ensured",),
    "agent_data": ("_agent_data_schema_ensured",),
    "agent_responses": ("_agent_responses_schema_ensured",),
    "agent_task": ("_agent_task_schema_ensured",),
    "app_log": ("_app_log_schema_ensured",),
    "board_search": ("_board_search_schema_ensured",),
    "board_search_run": ("_board_search_run_schema_ensured",),
    "candidate": ("_candidate_schema_ensured",),
    "candidate_intake_session": ("_intake_session_schema_ensured",),
    "company": ("_company_schema_ensured", "_company_candidate_fk_ensured"),
    "company_job_scan": ("_company_job_scan_schema_ensured",),
    "company_search_terms": (
        "_company_search_terms_schema_ensured",
        "_company_search_terms_migration_swept",
    ),
    "dispatch_ledger": ("_dispatch_ledger_schema_ensured",),
    "dispatch_task": ("_dispatch_task_schema_ensured",),
    "job": ("_job_schema_ensured",),
}

_UPSERT_LAZY_SCHEMA_HANDLERS: dict[str, Callable[[sqlite3.Connection], None]] = {
    "agent": _ensure_agent_schema,
    "agent_data": _ensure_agent_data_schema,
    "agent_responses": _ensure_agent_responses_schema,
    "agent_task": _ensure_agent_task_schema,
    "app_log": _ensure_app_log_schema,
    "board_search": _ensure_board_search_table,
    "board_search_run": _ensure_board_search_run_table,
    "candidate": _ensure_candidate_schema,
    "candidate_intake_session": _ensure_candidate_intake_session_table,
    "company": _ensure_company_table_for_upsert,
    "company_job_scan": _ensure_company_job_scan_schema,
    "company_search_terms": _ensure_company_search_terms_table,
    "dispatch_ledger": _ensure_dispatch_ledger_schema,
    "dispatch_task": _ensure_dispatch_task_schema,
    "job": _ensure_job_schema,
}


def ensure_table_schema_for_upsert(conn: sqlite3.Connection, table: str) -> None:
    """Run idempotent lazy schema ensure for ``table`` when registered; no-op otherwise.

    Upsert must not trust process-global ``_*_schema_ensured`` shortcuts: the target DB file
    may be stale while flags were set by a prior request or DB swap in the same process."""
    handler = _UPSERT_LAZY_SCHEMA_HANDLERS.get(table)
    if handler is None:
        return
    for flag_name in _UPSERT_SCHEMA_ENSURE_FLAGS.get(table, ()):
        globals()[flag_name] = False
    handler(conn)

def save_dispatch_task(
    candidate_id: str, task_key: str, min_count: int,
    auto_mode: bool = False, entity_type: Optional[str] = None,
    trigger_state: Optional[str] = None,
    batch_size: Optional[int] = None, freq_hrs: float = 0,
    score_floor: Optional[float] = None,
) -> int:
    """Insert a new dispatch_task. Returns the new row id.
    Fills entity_type, trigger_state, sort_by, batch_call_mode from config defaults when omitted."""
    try:
        defaults = dispatch_task_admin_defaults(task_key)
    except KeyError as e:
        raise ValueError(f"dispatch_task task_key not schedulable: {task_key!r}") from e
    if not (entity_type and str(entity_type).strip()):
        entity_type = defaults["entity_type"]
    if not (trigger_state and str(trigger_state).strip()):
        trigger_state = defaults["trigger_state"]
    sort_by = defaults["sort_by"]
    batch_call_mode = defaults["batch_call_mode"]
    now = _utc_now()
    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_dispatch_task_schema(conn)
            cur = conn.execute(
                """INSERT INTO dispatch_task
                   (candidate_id, task_key, entity_type, trigger_state, sort_by, batch_call_mode,
                    freq_hrs, min_count, batch_size, auto_mode, score_floor, last_run_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (candidate_id, task_key, entity_type, trigger_state, sort_by, batch_call_mode,
                 freq_hrs, min_count, batch_size, int(auto_mode), score_floor, now, now),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_dispatch_task(task_id: int) -> Optional[Dict[str, Any]]:
    """Return single dispatch_task by id, or None."""
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_dispatch_task_schema(conn)
            row = conn.execute("SELECT * FROM dispatch_task WHERE id = ?", (task_id,)).fetchone()
            return _row_to_dict(row) if row else None
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def list_dispatch_tasks() -> List[Dict[str, Any]]:
    """Return all dispatch_task rows, newest first."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_dispatch_task_schema(conn)
            rows = conn.execute("SELECT * FROM dispatch_task ORDER BY id DESC").fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_dispatch_task_by_key(task_key: str) -> Optional[Dict[str, Any]]:
    """Return the first dispatch_task row for a given task_key, or None."""
    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_dispatch_task_schema(conn)
            row = conn.execute(
                "SELECT * FROM dispatch_task WHERE task_key = ? ORDER BY id LIMIT 1", (task_key,)
            ).fetchone()
            return _row_to_dict(row) if row else None
        finally:
            conn.close()
    return _run_with_retry(_with_conn)


def get_dispatch_row_or_seed_preview_meta(task_key: str) -> Optional[Dict[str, Any]]:
    """Sample dispatch_task row if present; else config-built defaults for admin adhoc."""
    row = get_dispatch_task_by_key(task_key)
    if row:
        return row
    try:
        return dict(dispatch_task_admin_defaults(task_key))
    except KeyError:
        return None


_DISPATCH_TASK_UPDATE_COLS = {"min_count", "batch_size", "auto_mode", "last_run_at", "entity_type", "trigger_state", "debug", "skip_cache", "freq_hrs", "max_runs", "score_floor"}


def update_dispatch_task(task_id: int, **kwargs) -> None:
    """Update fields on a dispatch_task. Column-whitelisted."""
    if not kwargs:
        return
    bad = set(kwargs) - _DISPATCH_TASK_UPDATE_COLS
    if bad:
        raise ValueError(f"Invalid dispatch_task columns: {bad}")
    now = _utc_now()
    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_dispatch_task_schema(conn)
            pairs = [f"{k} = ?" for k in kwargs]
            pairs.append("updated_at = ?")
            vals = list(kwargs.values()) + [now, task_id]
            conn.execute(
                f"UPDATE dispatch_task SET {', '.join(pairs)} WHERE id = ?", vals
            )
            conn.commit()
        finally:
            conn.close()
    _run_with_retry(_with_conn)


def get_due_tasks() -> List[Dict[str, Any]]:
    """Return auto_mode dispatch_tasks that have enough eligible entities to process.
    Each returned dict includes 'available_count' from count_eligible_for_dispatch_task (WATCH/gaze respects freq_hrs and last_scan_at)."""
    def _with_conn() -> List[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_dispatch_task_schema(conn)
            rows = conn.execute(
                "SELECT * FROM dispatch_task WHERE auto_mode = 1 ORDER BY id"
            ).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()
    all_enabled = _run_with_retry(_with_conn)
    due = []
    for task in all_enabled:
        et = task.get("entity_type")
        ts = task.get("trigger_state")
        cid = task.get("candidate_id")
        if not et or not ts or not cid:
            continue
        avail = count_eligible_for_dispatch_task(task)
        if avail >= (task.get("min_count") or 1):  # match runner threshold (or 1) to avoid noisy zero-work runs
            task["available_count"] = avail
            due.append(task)
    return due


def count_company_new_without_website(candidate_id: str) -> int:
    """Unclaimed NEW companies with empty company_website (Phase 2 inflow_resolve_website)."""
    if not candidate_id or not str(candidate_id).strip():
        return 0

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            row = conn.execute(
                """SELECT COUNT(*) FROM company
                   WHERE state = 'NEW' AND candidate_id = ?
                     AND (batch_id IS NULL OR batch_id = '')
                     AND (company_website IS NULL OR TRIM(company_website) = '')""",
                (candidate_id,),
            ).fetchone()
            return int(row[0])
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def count_candidate_inflow_discovery_eligible(
    candidate_id: str,
    freq_hrs: float,
    last_run_at: Optional[str],
) -> int:
    """inflow_discovery when LIVE_PROMPTS and ≥1 stale company_search_terms row (AST-525)."""
    del freq_hrs, last_run_at  # unused — per-term last_scan_at, not dispatch_task.last_run_at
    if not candidate_id or not str(candidate_id).strip():
        return 0
    cand = get_candidate(candidate_id)
    if not cand:
        return 0
    trigger = INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]
    if (cand.get("state") or "").strip() != trigger:
        return 0
    scan_h = float(INFLOW_CONFIG["discovery"]["scan_interval_hours"])
    if count_stale_company_search_terms(candidate_id, scan_h) > 0:
        return 1
    return 0



def _state_in_sql(states: List[str]) -> tuple[str, List[Any]]:
    """Return ('state IN (?,?)', [s0, s1]) or ('state = ?', [s0]) for non-empty states."""
    if not states:
        raise ValueError("states must be non-empty")
    if len(states) == 1:
        return "state = ?", [states[0]]
    placeholders = ",".join("?" for _ in states)
    return f"state IN ({placeholders})", list(states)

def count_eligible_for_dispatch_task(task: Dict[str, Any]) -> int:
    """Count entities this task would actually claim now (unclaimed + scan cadence for WATCH/gaze).

    For company WATCH, rows must satisfy the same last_scan_at staleness as set_company_batch:
    uses dispatch_task.freq_hrs when > 0, else COMPANY_STATES[state].batch_criteria.scan_interval_hours for company.
    For board_search gaze_board: freq_hrs when > 0, else BOARDS_CONFIG["gaze_board"]["scan_interval_hours"] — same staleness predicate as claim_board_search_batch.
    Other company states and all job states use count_entities_in_state (no per-task freq filter)."""
    entity_type = task.get("entity_type")
    state = task.get("trigger_state")
    candidate_id = task.get("candidate_id")
    if not entity_type or not state or not candidate_id:
        return 0
    claim_states = dispatch_claim_states(state, entity_type)
    if not claim_states:
        return 0
    task_key = task.get("task_key", "")
    is_scored = dispatch_claim_uses_score_floor(state)
    floor = float(task.get("score_floor")) if (is_scored and task.get("score_floor") is not None) else (1.0 if is_scored else None)
    if entity_type == "candidate":
        return count_candidate_inflow_discovery_eligible(candidate_id, 0, None)
    if entity_type == "company":
        if task_key == INFLOW_CONFIG["resolve"]["task_key"]:
            return count_company_new_without_website(candidate_id)
        floor_raw = task.get("score_floor")
        if floor_raw is not None:
            return count_companies_in_state_with_score_floor(
                candidate_id, state, float(floor_raw), states=claim_states,
            )
        bc = (COMPANY_STATES.get(state) or {}).get("batch_criteria") or {}
        freq = float(task.get("freq_hrs") or 0)
        scan_from_state = bc.get("scan_interval_hours")
        scan_h = freq if freq > 0 else scan_from_state
        # Match claim_company_batch: only WATCH (gaze) uses last_scan_at cadence unless a state defines scan_interval_hours.
        use_stale = scan_h is not None and float(scan_h) > 0 and (state == "WATCH" or scan_from_state is not None)
        if use_stale:
            hours = str(float(scan_h))

            def _with_conn() -> int:
                conn = _get_connection()
                try:
                    _ensure_company_schema(conn)
                    state_sql, state_params = _state_in_sql(claim_states)
                    row = conn.execute(
                        f"""SELECT COUNT(*) FROM company WHERE {state_sql} AND candidate_id = ?
                           AND (batch_id IS NULL OR batch_id = '')
                           AND (last_scan_at IS NULL OR last_scan_at < datetime('now', '-' || ? || ' hours'))""",
                        (*state_params, candidate_id, hours),
                    ).fetchone()
                    return int(row[0])
                finally:
                    conn.close()

            return _run_with_retry(_with_conn)
    if entity_type == "board_search":
        act = BOARD_SEARCH_STATES[0]
        freq = float(task.get("freq_hrs") or 0)
        gaze_bc = BOARDS_CONFIG.get("gaze_board") or {}
        cfg_scan_raw = gaze_bc.get("scan_interval_hours")
        scan_from_cfg = float(cfg_scan_raw) if cfg_scan_raw is not None else None
        scan_h = freq if freq > 0 else scan_from_cfg
        effective = scan_h if scan_h is not None and float(scan_h) > 0 else 24.0
        hours = str(float(effective))

        def _with_conn_bs() -> int:
            conn = _get_connection()
            try:
                _ensure_board_search_table(conn)
                row = conn.execute(
                    """SELECT COUNT(*) FROM board_search
                       WHERE candidate_id = ?
                         AND state = ?
                         AND (batch_id IS NULL OR batch_id = '')
                         AND (last_scan_at IS NULL OR last_scan_at < datetime('now', '-' || ? || ' hours'))""",
                    (candidate_id, act, hours),
                ).fetchone()
                return int(row[0])
            finally:
                conn.close()

        return _run_with_retry(_with_conn_bs)
    if entity_type == "job" and floor is not None:
        def _with_conn() -> int:
            conn = _get_connection()
            try:
                _ensure_job_schema(conn)
                state_sql, state_params = _state_in_sql(claim_states)
                row = conn.execute(
                    f"""SELECT COUNT(*) FROM job
                       WHERE {state_sql} AND (batch_id IS NULL OR batch_id = '')
                         AND latest_score IS NOT NULL AND latest_score >= ?
                         AND company IN (SELECT short_name FROM company WHERE candidate_id = ?)""",
                    (*state_params, float(floor), candidate_id),
                ).fetchone()
                return int(row[0])
            finally:
                conn.close()
        return _run_with_retry(_with_conn)
    return count_entities_in_state(entity_type, state, candidate_id, states=claim_states)


def count_companies_in_state_with_score_floor(
    candidate_id: str,
    state: str,
    score_floor: float,
    *,
    states: Optional[List[str]] = None,
) -> int:
    """Unclaimed companies in state with company_data.prefilter_score >= score_floor (AST-508)."""
    score_key = ROSTER_CONFIG["company_data_keys"]["prefilter_score"]

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            _ensure_company_schema(conn)
            claim_states = states if states is not None else [state]
            state_sql, state_params = _state_in_sql(claim_states)
            row = conn.execute(
                f"""SELECT COUNT(*) FROM company
                    WHERE {state_sql} AND candidate_id = ?
                      AND (batch_id IS NULL OR batch_id = '')
                      AND json_extract(company_data, '$.{score_key}') IS NOT NULL
                      AND CAST(json_extract(company_data, '$.{score_key}') AS REAL) >= ?""",
                (*state_params, candidate_id, float(score_floor)),
            ).fetchone()
            return int(row[0])
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def count_entities_in_state(
    entity_type: str, state: str, candidate_id: str, *, states: Optional[List[str]] = None,
) -> int:
    """Count available (unclaimed) jobs or companies in a given state for a candidate.
    Unclaimed = batch_id IS NULL OR batch_id = '' (same as claim_*_batch). Jobs are scoped via company.candidate_id."""
    claim_states = states if states is not None else [state]
    state_sql, state_params = _state_in_sql(claim_states)

    def _with_conn() -> int:
        conn = _get_connection()
        try:
            if entity_type == "company":
                _ensure_company_schema(conn)
                row = conn.execute(
                    f"SELECT COUNT(*) FROM company WHERE {state_sql} AND candidate_id = ? AND (batch_id IS NULL OR batch_id = '')",
                    (*state_params, candidate_id),
                ).fetchone()
            elif entity_type == "job":
                _ensure_job_schema(conn)
                row = conn.execute(
                    f"""SELECT COUNT(*) FROM job
                       WHERE {state_sql} AND (batch_id IS NULL OR batch_id = '') AND company IN
                       (SELECT short_name FROM company WHERE candidate_id = ?)""",
                    (*state_params, candidate_id),
                ).fetchone()
            else:
                raise ValueError(f"Unknown entity_type: {entity_type}")
            return row[0]
        finally:
            conn.close()
    return _run_with_retry(_with_conn)
