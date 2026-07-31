"""
Core dispatcher: scheduling, batch runners, and dispatch orchestration.

Thin wrappers for layering compliance (API layer imports core, not data),
plus all batch runner logic and an in-process scheduler thread.
"""

import asyncio
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core import monitor
from src.data.database import (
    list_dispatch_ledger as _db_list_dispatch_ledger,
    get_dispatch_ledger as _db_get_dispatch_ledger,
    list_log_entries as _db_list_log_entries,
    save_dispatch_task as _db_save_dispatch_task,
    get_dispatch_task as _db_get_dispatch_task,
    list_dispatch_tasks as _db_list_dispatch_tasks,
    list_dispatch_tasks_for_candidate as _db_list_dispatch_tasks_for_candidate,
    count_dispatch_tasks_by_candidate as _db_count_dispatch_tasks_by_candidate,
    delete_dispatch_task as _db_delete_dispatch_task,
    update_dispatch_task as _db_update_dispatch_task,
    sum_cost_by_batch as _db_sum_cost_by_batch,
)

from src.data import database
from src.core.agent import _current_agent_task_run_next, compute_batch_cost
from src.utils.deploy_status import is_local_deploy_env
from src.utils.config import (
    ASTRAL_CONFIG,
    INFLOW_CONFIG,
    TASK_CONFIG,
    METEORITE_DISPATCH_TASKS,
    GAZE_EMAIL_CONFIG,
    dispatch_claim_uses_score_floor,
    dispatch_claim_states,
    dispatch_chain_claim_states_for_row,
    dispatch_chain_row_matches_job,
    dispatch_task_key_is_scored,
    is_dispatch_chain_trigger,
    template_candidate_id,
    CANDIDATE_STAGE_DISPATCH,
)
from src.utils.network import check_internet_reachable
from src.utils.logging import get_logger, log_batch_id, flush_log_buffer

logger = get_logger(__name__)


def _dispatch_entity_identifier(entity_type: str, row: Dict[str, Any]) -> str:
    """Primary debug identifier for a claimed entity row (§1.5.1 style D)."""
    if entity_type == "job":
        return str(row.get("astral_job_id") or row.get("company") or "?")
    if entity_type == "company":
        return str(row.get("short_name") or row.get("company") or "?")
    if entity_type == "candidate":
        return str(row.get("astral_candidate_id") or row.get("candidate_id") or "?")
    return str(row.get("id") or "?")


def _task_key_scored(task_key: str) -> bool:
    return dispatch_task_key_is_scored(task_key)


def _trigger_state_scored(trigger_state: Optional[str], task_key: str) -> bool:
    return dispatch_claim_uses_score_floor(trigger_state)


async def _warm_then_gather(one_fn, entities: list, zero: dict) -> list:
    """Run the first entity sequentially to warm the cache, wait for cache_warm_delay_seconds,
    then fire the rest concurrently. Gives Anthropic time to commit the cache entry."""
    if not entities:
        return []
    first = await one_fn(entities[0])
    if len(entities) == 1:
        return [first]
    delay = ASTRAL_CONFIG.get("cache_warm_delay_seconds", 1.0)
    if delay > 0:
        await asyncio.sleep(delay)
    rest = await asyncio.gather(*[one_fn(e) for e in entities[1:]], return_exceptions=True)
    cleaned = [first]
    for i, r in enumerate(rest):
        if isinstance(r, BaseException):
            logger.exception("  gather slot %d raised: %s", i + 1, r, exc_info=r)
            cleaned.append({**zero, "total_processed": 1, "total_errors": 1})
        else:
            cleaned.append(r)
    return cleaned


# ---------------------------------------------------------------------------
# Thin wrappers (API layer compliance — imports core, not data)
# ---------------------------------------------------------------------------

def list_dispatch_ledger(**kwargs) -> List[Dict[str, Any]]:
    """Enriches each row with total_cost from timesheets."""
    rows = _db_list_dispatch_ledger(**kwargs)
    batch_ids = [r["batch_id"] for r in rows if r.get("batch_id")]
    costs = _db_sum_cost_by_batch(batch_ids) if batch_ids else {}
    for r in rows:
        # Display total matches sum of agent_timesheets calc_cost_* (AST-571).
        r["total_cost"] = costs.get(r.get("batch_id"), 0.0)
    return rows


def get_dispatch_ledger(batch_id: str) -> Optional[Dict[str, Any]]:
    return _db_get_dispatch_ledger(batch_id)


def list_log_entries(**kwargs) -> List[Dict[str, Any]]:
    return _db_list_log_entries(**kwargs)


def save_dispatch_task(*args, **kwargs) -> int:
    return _db_save_dispatch_task(*args, **kwargs)


def get_dispatch_task(task_id: int) -> Optional[Dict[str, Any]]:
    return _db_get_dispatch_task(task_id)


def list_dispatch_tasks() -> List[Dict[str, Any]]:
    return _db_list_dispatch_tasks()


def list_dispatch_tasks_for_candidate(candidate_id: str) -> List[Dict[str, Any]]:
    return _db_list_dispatch_tasks_for_candidate(candidate_id)


def count_dispatch_tasks_by_candidate() -> Dict[str, int]:
    return _db_count_dispatch_tasks_by_candidate()


def delete_dispatch_task(task_id: int) -> None:
    _db_delete_dispatch_task(task_id)


def update_dispatch_task(task_id: int, **kwargs) -> None:
    _db_update_dispatch_task(task_id, **kwargs)


def set_candidate_dispatch_tasks_from_template(target_candidate_id: str) -> Dict[str, Any]:
    """Mirror config template candidate's dispatch_task set onto target (AST-875)."""
    target = str(target_candidate_id or "").strip()
    if not target:
        raise ValueError("candidate_id is required")
    template_id = template_candidate_id()
    if not template_id:
        raise ValueError("ASTRAL_CONFIG template_candidate_id is empty")
    if database.get_candidate(template_id) is None:
        raise LookupError(f"Template candidate not found: {template_id}")
    if database.get_candidate(target) is None:
        raise LookupError(f"Candidate not found: {target}")
    template_rows = database.list_dispatch_tasks_for_candidate(template_id)
    stats = database.set_dispatch_tasks_from_template_rows(target, template_rows)
    return {"candidate_id": target, "template_candidate_id": template_id, **stats}



def ensure_meteorite_dispatch_tasks(candidate_id: str) -> Dict[str, Any]:
    """Idempotent insert of meteorite dispatch_task rows; retire stale evaluate_jd@METEORITE_NEW (AST-1060)."""
    cid = str(candidate_id or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    existing = {
        ((r.get("task_key") or "").strip(), (r.get("trigger_state") or "").strip())
        for r in database.list_dispatch_tasks_for_candidate(cid)
    }
    added = 0
    skipped = 0
    skipped_missing_config = 0
    for entry in METEORITE_DISPATCH_TASKS:
        tk = str(entry["task_key"]).strip()
        ts = str(entry["trigger_state"]).strip()
        if tk not in TASK_CONFIG:
            skipped_missing_config += 1
            continue
        if (tk, ts) in existing:
            skipped += 1
            continue
        database.save_dispatch_task(
            candidate_id=cid,
            task_key=tk,
            min_count=int(entry.get("min_count") or 1),
            auto_mode=bool(entry.get("auto_mode", False)),
            trigger_state=ts,
            batch_size=entry.get("batch_size"),
            freq_hrs=float(entry.get("freq_hrs") or 0),
            score_floor=entry.get("score_floor"),
        )
        added += 1
    # AST-1060: live claim surface — drop evaluate_jd@METEORITE_NEW (keep JD_READY).
    retired = 0
    for row in database.list_dispatch_tasks_for_candidate(cid):
        tk = (row.get("task_key") or "").strip()
        ts = (row.get("trigger_state") or "").strip()
        if tk == "evaluate_jd" and ts == "METEORITE_NEW":
            delete_dispatch_task(int(row["id"]))
            retired += 1
    return {
        "candidate_id": cid,
        "added": added,
        "skipped": skipped,
        "skipped_missing_config": skipped_missing_config,
        "retired": retired,
    }


def provision_meteorite_dispatch_tasks() -> Dict[str, Any]:
    """Seed template + every candidate that already has dispatch rows (AST-1054)."""
    template_id = template_candidate_id()
    if not template_id:
        raise ValueError("ASTRAL_CONFIG template_candidate_id is empty")
    if database.get_candidate(template_id) is None:
        raise LookupError(f"Template candidate not found: {template_id}")
    tstats = ensure_meteorite_dispatch_tasks(template_id)
    added = int(tstats.get("added") or 0)
    skipped = int(tstats.get("skipped") or 0)
    skipped_missing_config = int(tstats.get("skipped_missing_config") or 0)
    retired = int(tstats.get("retired") or 0)
    touched = 0
    for cid in database.list_candidate_ids_with_dispatch_tasks():
        stats = ensure_meteorite_dispatch_tasks(cid)
        added += int(stats.get("added") or 0)
        skipped += int(stats.get("skipped") or 0)
        skipped_missing_config += int(stats.get("skipped_missing_config") or 0)
        retired += int(stats.get("retired") or 0)
        touched += 1
    return {
        "template_candidate_id": template_id,
        "candidates_touched": touched,
        "added": added,
        "skipped": skipped,
        "skipped_missing_config": skipped_missing_config,
        "retired": retired,
    }



def ensure_gaze_email_dispatch_task() -> Dict[str, Any]:
    """Idempotent insert of the shared Astral inbox gaze_email row (null candidate_id).

    Due eligibility + mailbox runner live on AST-1090 (`get_due_tasks` / `_dispatch_one`).
    AST-1098: reconcile stuck AUTO-on shared row back to seed CLICK.
    """
    tk = str(GAZE_EMAIL_CONFIG["task_key"]).strip()
    if tk not in TASK_CONFIG:
        return {
            "task_key": tk,
            "added": 0,
            "skipped": 0,
            "reconciled": 0,
            "skipped_missing_config": 1,
            "id": None,
        }
    existing = None
    for row in database.list_dispatch_tasks():
        if (row.get("task_key") or "").strip() != tk:
            continue
        cid = row.get("candidate_id")
        if cid is None or str(cid).strip() == "":
            existing = row
            break
    if existing is not None:
        # Bad-seed / prior AUTO: force seed law CLICK on this shared row only.
        if bool(existing.get("auto_mode")):
            database.update_dispatch_task(int(existing["id"]), auto_mode=False)
            return {
                "task_key": tk,
                "added": 0,
                "skipped": 0,
                "reconciled": 1,
                "skipped_missing_config": 0,
                "id": existing.get("id"),
            }
        return {
            "task_key": tk,
            "added": 0,
            "skipped": 1,
            "reconciled": 0,
            "skipped_missing_config": 0,
            "id": existing.get("id"),
        }
    new_id = database.save_dispatch_task(
        candidate_id=None,
        task_key=tk,
        min_count=int(GAZE_EMAIL_CONFIG["min_count"]),
        auto_mode=bool(GAZE_EMAIL_CONFIG["auto_mode"]),
        entity_type=GAZE_EMAIL_CONFIG["entity_type"],
        trigger_state=GAZE_EMAIL_CONFIG["trigger_state"],
        batch_size=GAZE_EMAIL_CONFIG["batch_size"],
        freq_hrs=float(GAZE_EMAIL_CONFIG["freq_hrs"] or 0),
    )
    return {
        "task_key": tk,
        "added": 1,
        "skipped": 0,
        "reconciled": 0,
        "skipped_missing_config": 0,
        "id": new_id,
    }


def provision_gaze_email_dispatch_task() -> Dict[str, Any]:
    """Startup provision for the shared gaze_email dispatch shell (AST-1088)."""
    return ensure_gaze_email_dispatch_task()


# ---------------------------------------------------------------------------
# Helpers
# Batch runners call `database` directly (not via _db_ wrappers) because
# this is core-layer code — the wrappers exist only for API-layer compliance.
# ---------------------------------------------------------------------------

_SUMMARY_ZERO: Dict[str, int] = {
    "total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0,
}

# batch_call_mode job consult exhaustion (AST-502): widen claim + chunk parallel waves for encoded batch consult (AST-501/503).
_CHUNK_EXHAUST_CONSULT_JOB_KEYS = frozenset({
    "qualify_job_listings",
    "qualify_meteorite",
    "evaluate_jd",
    "grade_do",
    "grade_get",
    "grade_like",
    "meteorite_like",
})


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")



# ---------------------------------------------------------------------------
# Unified batch runner
# ---------------------------------------------------------------------------

async def _run_unified(task: Dict, ctx: Dict, debug: bool) -> Dict[str, int]:
    """Claim a batch for the given task and dispatch to consult.run_consult_task.
    Reads entity_type, trigger_state, sort_by, batch_call_mode from the DB task row.
    batch_call_mode=1 consult (job rows): qualifying + jd + scored DO/GET/LIKE consult may claim the full backlog (≤ eligible count),
    sized into chunk_width ``batch_size`` API calls — chunk 0 cache-warm sequential, remainder parallel (AST-502).
    Other batch_call_mode=1 runners: single consult pass for all claimed rows.
    batch_call_mode=0: per-job _warm_then_gather (legacy rows, companies, fetch_jd, …)."""
    if not check_internet_reachable():
        if debug:
            logger.set_debug_flag(True)
            logger.debug_index(
                func="dispatcher._run_unified",
                index=1,
                total=1,
                identifier=(task.get("task_key") or "?").strip() or "?",
                outcome="skipped — network unreachable",
            )
            logger.debug_detail(
                f"entity_type={task.get('entity_type', '')!r} "
                f"trigger_state={task.get('trigger_state', '')!r}"
            )
        _sched_log.warning(
            "[%s/%s] dispatch skipped: network unreachable",
            task.get("task_key", "?"),
            log_batch_id.get() or "?",
        )
        return dict(_SUMMARY_ZERO)
    from src.core import consult
    from src.core.tracker import get_new_job_batch, clear_job_batch
    from src.core.roster import get_new_company_batch, clear_company_batch

    entity_type     = task.get("entity_type", "")
    input_state     = task.get("trigger_state", "")
    sort_by         = task.get("sort_by") or "updated_at"
    limit           = int(task["batch_size"]) if task.get("batch_size") is not None else None
    # Sole split between one consult call for all entities vs per-job _warm_then_gather; DB wins (dispatch_tasks.batch_call_mode).
    # AST-891: parse_job_list always full-list consult — production rows stay batch_call_mode=0.
    batch_call_mode = bool(task.get("batch_call_mode", 0))
    candidate_id    = ctx.get("astral_candidate_id")
    bid             = ctx.get("entity_batch_id") or log_batch_id.get()
    dispatch_task_key = (task.get("task_key") or "").strip()
    use_full_batch = batch_call_mode or (dispatch_task_key == "parse_job_list")
    s               = dict(_SUMMARY_ZERO)
    if debug:
        logger.set_debug_flag(True)

    claim_cap = None
    claim_states: Optional[List[str]] = None
    if entity_type == "candidate":
        claim_states = dispatch_claim_states(input_state, "candidate")
        cur = (ctx.get("state") or "").strip() if ctx else ""
        entities = [ctx] if ctx and cur in claim_states else []
    elif entity_type == "job":
        task_key_run = task.get("task_key", "")
        is_scored = _trigger_state_scored(input_state, task_key_run)
        floor = float(task.get("score_floor")) if (is_scored and task.get("score_floor") is not None) else (1.0 if is_scored else None)
        if batch_call_mode and task_key_run in _CHUNK_EXHAUST_CONSULT_JOB_KEYS:
            if task.get("batch_size") is None:
                raise ValueError(
                    "dispatch_tasks.batch_size is required for consult chunk exhaustion "
                    f"(task_key={task_key_run!r} id={task.get('id')})"
                )
            claim_cap = database.count_eligible_for_dispatch_task(task)
        claim_states = dispatch_claim_states(input_state, "job")
        if is_dispatch_chain_trigger((input_state or "").strip()):
            claim_states = dispatch_chain_claim_states_for_row(
                (input_state or "").strip(),
                task_key_run,
            )
        bid, entities = get_new_job_batch(
            input_state,
            limit=limit,
            sort_by=sort_by,
            score_floor=floor,
            candidate_id=candidate_id,
            batch_id=bid,
            claim_cap=claim_cap,
            states=claim_states,
        )
        if is_dispatch_chain_trigger((input_state or "").strip()):
            entities = [
                e for e in entities
                if dispatch_chain_row_matches_job(
                    (input_state or "").strip(),
                    dispatch_task_key,
                    (e.get("state") or ""),
                )
            ]
    else:
        freq = float(task.get("freq_hrs") or 0)
        # freq_hrs on dispatch_task overrides COMPANY_STATES scan_interval for gaze (WATCH) claim + count.
        scan_override = freq if freq > 0 else None
        sort_override = (task.get("sort_by") or "").strip() or None
        resolve_key = INFLOW_CONFIG["resolve"]["task_key"]
        floor = float(task["score_floor"]) if task.get("score_floor") is not None else None
        claim_states = dispatch_claim_states(input_state, "company")
        bid, entities = get_new_company_batch(
            input_state,
            limit=limit,
            candidate_id=candidate_id,
            batch_id=bid,
            context=f"dispatch-{input_state}",
            sort_by=sort_override,
            scan_interval_hours=scan_override,
            require_empty_website=(task.get("task_key") == resolve_key),
            score_floor=floor,
            states=claim_states,
            exclude_prefilter_second_strike=(dispatch_task_key == "fetch_website"),
        )

    if not entities:
        if entity_type == "job" and bid:
            clear_job_batch(bid)
        if debug:
            logger.debug_index(
                func="dispatcher._run_unified",
                index=1,
                total=1,
                identifier=f"{entity_type}/{input_state}",
                outcome="no entities claimed",
            )
            logger.debug_detail(
                f"task_key={dispatch_task_key} batch_id={bid} batch_call_mode={batch_call_mode} "
                f"dispatch batch_size={limit!r}"
            )
        return s

    entity_total = len(entities)
    if debug:
        logger.debug_index(
            func="dispatcher._run_unified",
            index=1,
            total=1,
            identifier=f"{entity_type}/{input_state}",
            outcome=f"claimed {entity_total} entity/entities",
        )
        logger.debug_detail(
            f"task_key={dispatch_task_key} batch_id={bid} batch_call_mode={batch_call_mode} "
            f"dispatch batch_size={limit!r} claim_cap={claim_cap!r}"
            + (f" claim_states={claim_states!r}" if claim_states is not None else "")
        )
        for ei, entity in enumerate(entities, start=1):
            logger.debug_index(
                func="dispatcher._run_unified",
                index=ei,
                total=entity_total,
                identifier=_dispatch_entity_identifier(entity_type, entity),
                outcome="claimed",
            )
            logger.debug_detail(
                f"entity_type={entity_type} trigger_state={input_state} "
                f"state={entity.get('state')!r}"
            )
    try:
        if use_full_batch:
            job_tk = task.get("task_key", "") if entity_type == "job" else ""
            use_chunk_split = (
                entity_type == "job"
                and job_tk in _CHUNK_EXHAUST_CONSULT_JOB_KEYS
                and isinstance(task.get("batch_size"), (int, str))
                and int(task["batch_size"]) > 0
                and len(entities) > int(task["batch_size"])
            )
            if use_chunk_split:
                chunk_sz = int(task["batch_size"])
                chunks = [entities[i : i + chunk_sz] for i in range(0, len(entities), chunk_sz)]
                if debug:
                    chunk_total = len(chunks)
                    for ci, chunk_rows in enumerate(chunks):
                        logger.debug_index(
                            func="dispatcher._run_unified",
                            index=ci + 1,
                            total=chunk_total,
                            identifier=f"chunk task_key={dispatch_task_key}",
                            outcome=f"consult chunk size={len(chunk_rows)}",
                        )
                        logger.debug_detail(
                            f"batch_id={bid} batch_chunk_index={ci} chunk_width={chunk_sz} "
                            f"entities_in_chunk={len(chunk_rows)}"
                        )

                async def _consult_chunk(ci: int, chunk_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
                    return await consult.run_consult_task(
                        entity_type,
                        input_state,
                        chunk_rows,
                        bid,
                        ctx,
                        debug,
                        batch_chunk_index=ci,
                        dispatch_task_key=dispatch_task_key,
                    )

                head = await _consult_chunk(0, chunks[0])
                delay_sec = float(ASTRAL_CONFIG.get("cache_warm_delay_seconds", 1.0))
                if delay_sec > 0:
                    await asyncio.sleep(delay_sec)
                tail = []
                if len(chunks) > 1:
                    tail = await asyncio.gather(*[_consult_chunk(ci, chunks[ci]) for ci in range(1, len(chunks))])
                for piece in [head] + list(tail):
                    for k in s:
                        s[k] += piece.get(k, 0)
            else:
                result = await consult.run_consult_task(
                    entity_type, input_state, entities, bid, ctx, debug,
                    dispatch_task_key=dispatch_task_key,
                )
                for k in s:
                    s[k] += result.get(k, 0)
        else:
            async def _one(e):
                return await consult.run_consult_task(
                    entity_type, input_state, [e], bid, ctx, debug,
                    dispatch_task_key=dispatch_task_key,
                )
            results = await _warm_then_gather(_one, entities, _SUMMARY_ZERO)
            for r in results:
                for k in s:
                    s[k] += r.get(k, 0)
        if debug and entity_total > 0:
            logger.debug_detail(f"batch end summary={s}")
    finally:
        if entity_type == "job":
            clear_job_batch(bid)
        elif entity_type == "candidate":
            pass
        else:
            clear_company_batch(bid)
    return s


# ---------------------------------------------------------------------------
# Dispatch orchestration
# ---------------------------------------------------------------------------

_CIRCUIT_BREAKER_THRESHOLD = 3  # consecutive zero-progress runs before auto-disable


def _check_circuit_breaker(task_key: str, candidate_id: str, task_id: int, debug: bool) -> None:
    """Auto-disable a dispatch task if the last N completed runs all had 0 passed and 0 failed."""
    recent = database.get_recent_ledger_summaries(task_key, candidate_id, n=_CIRCUIT_BREAKER_THRESHOLD)
    if len(recent) < _CIRCUIT_BREAKER_THRESHOLD:
        return
    if all(r.get("total_passed", 0) == 0 and r.get("total_failed", 0) == 0 for r in recent):
        if debug:
            logger.set_debug_flag(True)
            logger.debug_detail(
                f"circuit breaker: task_key={task_key} candidate_id={candidate_id} "
                f"task_id={task_id} consecutive_zero_progress={_CIRCUIT_BREAKER_THRESHOLD}"
            )
        logger.warning(
            "CIRCUIT BREAKER: %s has had %d consecutive runs with 0 passed / 0 failed — auto-disabling task %s",
            task_key, _CIRCUIT_BREAKER_THRESHOLD, task_id,
        )
        _db_update_dispatch_task(task_id, enabled=False)


async def _run_task(task: Dict, ctx: Dict, debug: bool) -> Dict[str, int]:
    """Run a single batch through the unified runner. Returns summary counts."""
    bid = log_batch_id.get()
    task_key = (task.get("task_key") or "").strip()
    if debug:
        logger.set_debug_flag(True)
        logger.debug_index(
            func="dispatcher._run_task",
            index=1,
            total=1,
            identifier=task_key or "?",
            outcome="running batch",
        )
        logger.debug_detail(
            f"batch_size={task.get('batch_size')} batch_id={bid} "
            f"entity_type={task.get('entity_type')!r} trigger_state={task.get('trigger_state')!r}"
        )
    summary = await _run_unified(task, ctx, debug)
    if debug:
        logger.debug_detail(f"runner returned summary={summary}")
    return summary




# ---------------------------------------------------------------------------
# Per-task thread scheduler
# ---------------------------------------------------------------------------

_sched_log = get_logger("dispatch.scheduler")

# Registry: task_id -> {thread, loop, asyncio_task, task_key, candidate_id, is_auto}
_task_registry: Dict[int, Dict[str, Any]] = {}
_registry_lock = threading.Lock()

# Tick thread (wakes every tick_rate_minutes to spawn due AUTO tasks)
_tick_thread: Optional[threading.Thread] = None
_tick_event = threading.Event()


async def _dispatch_one(task: Dict) -> None:
    """Run a single dispatch task to completion inside its own asyncio event loop.
    Registers the asyncio task for cancellation, writes ledger, clears registry on exit."""
    task_id = task["id"]
    task_key = task["task_key"]
    candidate_id = task["candidate_id"]
    timeout = ASTRAL_CONFIG.get("dispatch_timeout_seconds", 3600)
    is_click = not bool(task.get("auto_mode"))
    ui_initiated = bool(task.get("_ui_initiated"))
    failure_reason: Optional[str] = None
    debug = bool(task.get("debug")) or (ui_initiated and is_local_deploy_env())
    if debug:
        logger.set_debug_flag(True)

    # AST-1090: null-candidate gaze_email mailbox — no candidate API key; one runner call.
    if (task_key or "").strip() == GAZE_EMAIL_CONFIG["task_key"]:
        # late: keep gaze_email off module-top load (peer late imports in this file)
        from src.core.gaze_email import run_gaze_email

        entity_batch_id = f"{task_key}-{uuid.uuid4()}"
        ledger_cid = GAZE_EMAIL_CONFIG["dispatch_ledger_candidate_id"]
        if debug:
            logger.debug_index(
                func="dispatcher._dispatch_one",
                index=1,
                total=1,
                identifier=task_key,
                outcome="task start",
            )
            logger.debug_detail(
                f"gaze_email mailbox runner entity_batch_id={entity_batch_id} "
                f"mode={'AUTO' if not is_click else 'CLICK'}"
            )
        database.save_dispatch_ledger(
            entity_batch_id,
            task_key,
            ledger_cid,
            _now_iso(),
            "RUNNING",
            entity_type=None,
        )
        log_batch_id.set(entity_batch_id)
        dispatch_ledger_id = entity_batch_id
        with _registry_lock:
            entry = _task_registry.get(task_id)
            if entry:
                entry["asyncio_task"] = asyncio.current_task()
        accumulated = dict(_SUMMARY_ZERO)
        final_status = "COMPLETED"
        try:
            summary = await run_gaze_email(task, debug=debug)
            for k in ("total_processed", "total_passed", "total_failed", "total_errors"):
                accumulated[k] = int(summary.get(k, 0) or 0)
        except asyncio.CancelledError:
            final_status = "INTERRUPTED"
            failure_reason = "dispatch cancelled by admin"
            _sched_log.warning("[%s/%s] KILLED by admin — gaze_email", task_key, entity_batch_id)
            accumulated["total_errors"] = accumulated.get("total_errors", 0) + 1
        except Exception:
            final_status = "FAILED"
            failure_reason = "gaze_email runner crashed"
            _sched_log.exception("[%s/%s] gaze_email crashed", task_key, entity_batch_id)
            accumulated["total_errors"] = accumulated.get("total_errors", 0) + 1
        finally:
            if dispatch_ledger_id:
                try:
                    total_cost = compute_batch_cost(dispatch_ledger_id)
                    total_processed = accumulated.get("total_processed", 0)
                    entity_cost = total_cost / total_processed if total_processed > 0 else total_cost
                    database.update_dispatch_ledger(
                        dispatch_ledger_id,
                        status=final_status,
                        completed_at=_now_iso(),
                        total_cost=total_cost,
                        entity_cost=round(entity_cost, 7),
                        **accumulated,
                    )
                    if final_status in ("FAILED", "INTERRUPTED"):
                        logger.error(
                            "[%s/%s] batch finished %s — %s | processed=%s passed=%s failed=%s errors=%s",
                            task_key,
                            dispatch_ledger_id,
                            final_status,
                            failure_reason or "see scheduler log",
                            accumulated.get("total_processed", 0),
                            accumulated.get("total_passed", 0),
                            accumulated.get("total_failed", 0),
                            accumulated.get("total_errors", 0),
                        )
                except Exception as e:
                    _sched_log.error("Failed to write ledger for %s/%s: %s", task_key, dispatch_ledger_id, e)
            flush_log_buffer()
            log_batch_id.set(None)
            try:
                _db_update_dispatch_task(task_id, last_run_at=_now_iso())
            except Exception as e:
                _sched_log.error("Failed to update dispatch task %s: %s", task_id, e)
        return

    ctx = database.get_candidate(candidate_id)
    if not ctx or not ctx.get("candidate_api_key"):
        if debug:
            logger.debug_index(
                func="dispatcher._dispatch_one",
                index=1,
                total=1,
                identifier=task_key,
                outcome="skipped — no candidate or API key",
            )
            logger.debug_detail(f"candidate_id={candidate_id!r}")
        _sched_log.error("Skipping %s/%s — no candidate or API key", task_key, candidate_id)
        return
    ctx = dict(ctx)
    if task.get("skip_cache"):
        ctx["skip_cache"] = True
    if task_key == INFLOW_CONFIG["discovery"]["task_key"]:
        ctx["inflow_discovery_freq_hrs"] = float(task.get("freq_hrs") or 0)

    entity_batch_id = f"{task_key}-{uuid.uuid4()}"
    has_run_next_chain = bool(_current_agent_task_run_next(task_key))
    if debug:
        logger.debug_index(
            func="dispatcher._dispatch_one",
            index=1,
            total=1,
            identifier=task_key,
            outcome="task start",
        )
        logger.debug_detail(
            f"candidate_id={candidate_id} available_count={task.get('available_count', 0)} "
            f"entity_batch_id={entity_batch_id} mode={'AUTO' if not is_click else 'CLICK'} "
            f"run_next_chain={has_run_next_chain} entity_type={task.get('entity_type')!r} "
            f"trigger_state={task.get('trigger_state')!r}"
        )
    ctx["entity_batch_id"] = entity_batch_id
    dispatch_ledger_id: Optional[str] = None
    task_entity_type = task.get("entity_type")
    if not has_run_next_chain:
        database.save_dispatch_ledger(
            entity_batch_id,
            task_key,
            candidate_id,
            _now_iso(),
            "RUNNING",
            entity_type=task_entity_type,
        )
        log_batch_id.set(entity_batch_id)
        dispatch_ledger_id = entity_batch_id
    _sched_log.info("Dispatching %s — %d available, batch %s",
                    task_key, task.get("available_count", 0), entity_batch_id)

    # Register this coroutine's asyncio task immediately so cancel_task() can reach it
    # without a race window. _tracked() used to do this but ran after loop.run_until_complete
    # started, leaving a narrow gap where cancel_task would see asyncio_task=None.
    with _registry_lock:
        entry = _task_registry.get(task_id)
        if entry:
            entry["asyncio_task"] = asyncio.current_task()

    # Store asyncio task ref so cancel_task() can reach it
    async def _tracked():
        if is_click:
            # CLICK tasks run unbounded — admin uses Stop/drain to end them
            await _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id)
        else:
            await asyncio.wait_for(
                _run_dispatch_loop(ctx, task, task_key, entity_batch_id, accumulated, dispatch_ledger_id),
                timeout=timeout,
            )

    accumulated = dict(_SUMMARY_ZERO)
    final_status = "COMPLETED"
    try:
        await _tracked()
    except asyncio.TimeoutError:
        final_status = "INTERRUPTED"
        failure_reason = f"dispatch timeout after {timeout}s"
        _sched_log.error("[%s/%s] killed after %ds timeout", task_key, entity_batch_id, timeout)
        accumulated["total_errors"] = accumulated.get("total_errors", 0) + 1
    except asyncio.CancelledError:
        final_status = "INTERRUPTED"
        failure_reason = "dispatch cancelled by admin"
        _sched_log.warning("[%s/%s] KILLED by admin — thread cleared from memory", task_key, entity_batch_id)
        accumulated["total_errors"] = accumulated.get("total_errors", 0) + 1
    except Exception as exc:
        final_status = "FAILED"
        failure_reason = f"dispatch crashed: {type(exc).__name__}"
        _sched_log.exception("[%s/%s] crashed", task_key, entity_batch_id)
        accumulated["total_errors"] = accumulated.get("total_errors", 0) + 1
    finally:
        if dispatch_ledger_id:
            try:
                total_cost = compute_batch_cost(dispatch_ledger_id)
                total_processed = accumulated.get("total_processed", 0)
                entity_cost = total_cost / total_processed if total_processed > 0 else total_cost
                database.update_dispatch_ledger(
                    dispatch_ledger_id,
                    status=final_status,
                    completed_at=_now_iso(),
                    total_cost=total_cost,
                    entity_cost=round(entity_cost, 7),
                    **accumulated,
                )
                if final_status in ("FAILED", "INTERRUPTED"):
                    logger.error(
                        "[%s/%s] batch finished %s — %s | processed=%s passed=%s failed=%s errors=%s",
                        task_key,
                        dispatch_ledger_id,
                        final_status,
                        failure_reason or "see scheduler log",
                        accumulated.get("total_processed", 0),
                        accumulated.get("total_passed", 0),
                        accumulated.get("total_failed", 0),
                        accumulated.get("total_errors", 0),
                    )
                elif accumulated.get("total_errors", 0) > 0:
                    logger.warning(
                        "[%s/%s] batch finished COMPLETED with errors — processed=%s passed=%s failed=%s errors=%s",
                        task_key,
                        dispatch_ledger_id,
                        accumulated.get("total_processed", 0),
                        accumulated.get("total_passed", 0),
                        accumulated.get("total_failed", 0),
                        accumulated.get("total_errors", 0),
                    )
            except Exception as e:
                _sched_log.error("Failed to write ledger for %s/%s: %s", task_key, dispatch_ledger_id, e)
        flush_log_buffer()
        # Alert while log_batch_id still set — monitor logs appear in the batch log view
        if dispatch_ledger_id and not is_click and accumulated.get("total_errors", 0) > 0:
            monitor.auto_run_error(
                task_key, dispatch_ledger_id, accumulated, final_status, candidate_id
            )
        log_batch_id.set(None)
        try:
            _db_update_dispatch_task(task_id, last_run_at=_now_iso())
        except Exception as e:
            _sched_log.error("Failed to update dispatch task %s: %s", task_id, e)

    if final_status == "COMPLETED":
        _check_circuit_breaker(task_key, candidate_id, task_id, bool(task.get("debug")))


async def _run_dispatch_loop(
    ctx: Dict,
    task: Dict,
    task_key: str,
    entity_batch_id: str,
    accumulated: Dict,
    dispatch_ledger_id: Optional[str],
) -> None:
    """Inner loop: run batches until drained or max_runs hit. Mutates accumulated in place."""
    debug = bool(task.get("debug"))
    if debug:
        logger.set_debug_flag(True)
    max_runs = task.get("max_runs")
    is_auto = bool(task.get("auto_mode"))
    run_count = 0
    while True:
        et = task.get("entity_type")
        ts = task.get("trigger_state")
        available = database.count_eligible_for_dispatch_task(task)
        # min_count gate only applies to AUTO — CLICK runs regardless of queue depth
        effective_min = (task.get("min_count") or 1) if is_auto else 1
        if available < effective_min:
            if debug:
                if run_count == 0:
                    logger.debug_index(
                        func="dispatcher._run_dispatch_loop",
                        index=1,
                        total=1,
                        identifier=task_key,
                        outcome="skipped — below min_count",
                    )
                    logger.debug_detail(
                        f"available={available} effective_min={effective_min} is_auto={is_auto}"
                    )
                    if task_key == INFLOW_CONFIG["discovery"]["task_key"]:
                        _eligible, reason = database.describe_candidate_inflow_discovery_eligibility(
                            task.get("candidate_id") or "",
                            float(task.get("freq_hrs") or 0),
                        )
                        if reason:
                            logger.debug_detail(reason)
                else:
                    logger.debug_detail(
                        f"loop stop: remaining below min_count available={available} "
                        f"effective_min={effective_min} run_count={run_count}"
                    )
            if run_count == 0:
                _sched_log.info("Skipping %s: %d available (min_count=%s)",
                                task_key, available, effective_min)
            else:
                _sched_log.info("Loop mode %s: %d remaining — stopping after %d run(s)",
                                task_key, available, run_count)
            break
        # Honour graceful drain request — finish current batch then stop
        with _registry_lock:
            draining = _task_registry.get(task["id"], {}).get("drain", False)
        if draining:
            if debug:
                logger.debug_detail(f"loop stop: drain flag set run_count={run_count}")
            _sched_log.info("[%s] drain flag set — stopping after %d run(s)", task_key, run_count)
            break
        loop_iter = run_count + 1
        if debug:
            logger.debug_index(
                func="dispatcher._run_dispatch_loop",
                index=loop_iter,
                total=loop_iter,
                identifier=task_key,
                outcome=f"loop iteration {loop_iter} starting",
            )
            logger.debug_detail(
                f"available={available} effective_min={effective_min} max_runs={max_runs!r} "
                f"draining={draining} entity_batch_id={entity_batch_id}"
            )
        summary = await _run_task(task, ctx, debug)
        for k in accumulated:
            accumulated[k] += summary.get(k, 0)
        run_count += 1
        if debug:
            logger.debug_detail(
                f"iteration {loop_iter} summary processed={summary.get('total_processed', 0)} "
                f"passed={summary.get('total_passed', 0)} failed={summary.get('total_failed', 0)} "
                f"errors={summary.get('total_errors', 0)} accumulated={accumulated}"
            )
        # Update ledger mid-run so the execution history reflects live progress
        if dispatch_ledger_id:
            database.update_dispatch_ledger(dispatch_ledger_id, **accumulated)
        if summary.get("total_processed", 0) == 0:
            if debug:
                logger.debug_detail(f"loop stop: zero processed this iteration run_count={run_count}")
            _sched_log.info("Loop mode %s: 0 processed — stopping", task_key)
            break
        if max_runs != 0:
            if max_runs is None or run_count >= max_runs:
                if debug:
                    logger.debug_detail(
                        f"loop stop: max_runs reached max_runs={max_runs!r} run_count={run_count}"
                    )
                break


def _task_thread_target(task_id: int, task: Dict) -> None:
    """Daemon thread target: owns its asyncio event loop, cleans up registry on exit."""
    loop = asyncio.new_event_loop()
    with _registry_lock:
        if task_id in _task_registry:
            _task_registry[task_id]["loop"] = loop
    try:
        loop.run_until_complete(_dispatch_one(task))
    finally:
        loop.close()
        with _registry_lock:
            _task_registry.pop(task_id, None)
        _sched_log.info("[%s] thread exited and cleared from registry", task.get("task_key", task_id))


def run_task(task_id: int, *, ui_initiated: bool = False) -> bool:
    """Spawn a daemon thread for task_id if not already running. Returns True if started."""
    with _registry_lock:
        if task_id in _task_registry:
            return False  # already running

    task = database.get_dispatch_task(task_id)
    if not task:
        return False

    # Enrich with available_count for logging
    task_key = task.get("task_key", "")
    et = task.get("entity_type")
    ts = task.get("trigger_state")
    cid = task.get("candidate_id", "")
    task["available_count"] = database.count_eligible_for_dispatch_task(task) if et and ts else 0
    task["_ui_initiated"] = ui_initiated

    with _registry_lock:
        _task_registry[task_id] = {
            "thread": None, "loop": None, "asyncio_task": None,
            "task_key": task_key, "candidate_id": cid,
            "is_auto": bool(task.get("auto_mode")),
            "drain": False,
        }

    t = threading.Thread(
        target=_task_thread_target,
        args=(task_id, task),
        daemon=True,
        name=f"astral-task-{task_id}-{task_key}",
    )
    with _registry_lock:
        _task_registry[task_id]["thread"] = t
    t.start()
    return True


def drain_task(task_id: int) -> Dict[str, Any]:
    """Request graceful stop after current batch for task_id. Returns info dict."""
    with _registry_lock:
        entry = _task_registry.get(task_id)
        if not entry:
            return {"task_id": task_id, "draining": False, "reason": "not_running"}
        entry["drain"] = True
    _sched_log.info("drain_task(%s): graceful stop requested for %s/%s",
                    task_id, entry["task_key"], entry["candidate_id"])
    return {"task_id": task_id, "task_key": entry["task_key"],
            "candidate_id": entry["candidate_id"], "draining": True}


def cancel_task(task_id: int) -> Dict[str, Any]:
    """Cancel the running thread for task_id. Returns info about what was killed."""
    with _registry_lock:
        entry = _task_registry.get(task_id)
    if not entry:
        return {"task_id": task_id, "killed": False, "reason": "not_running"}
    loop = entry.get("loop")
    asyncio_task = entry.get("asyncio_task")
    if not loop or not asyncio_task:
        # Thread is registered but asyncio_task not yet set — task is still starting up
        return {"task_id": task_id, "task_key": entry.get("task_key"),
                "candidate_id": entry.get("candidate_id"), "killed": False, "reason": "not_yet_ready"}
    if asyncio_task.done():
        return {"task_id": task_id, "task_key": entry.get("task_key"),
                "candidate_id": entry.get("candidate_id"), "killed": False, "reason": "already_done"}
    loop.call_soon_threadsafe(asyncio_task.cancel)
    _sched_log.warning("cancel_task(%s): cancellation sent to %s/%s",
                       task_id, entry["task_key"], entry["candidate_id"])
    return {"task_id": task_id, "task_key": entry["task_key"],
            "candidate_id": entry["candidate_id"], "killed": True}


def cancel_all_tasks() -> List[Dict[str, Any]]:
    """Cancel all running task threads. Returns list of killed task info."""
    with _registry_lock:
        ids = list(_task_registry.keys())
    return [cancel_task(tid) for tid in ids]


def task_status_all() -> Dict[int, Dict[str, Any]]:
    """Return running status for all registry entries."""
    with _registry_lock:
        return {
            tid: {
                "running": bool(entry.get("thread") and entry["thread"].is_alive()),
                "draining": bool(entry.get("drain")),
                "task_key": entry["task_key"],
                "candidate_id": entry["candidate_id"],
                "is_auto": entry["is_auto"],
            }
            for tid, entry in _task_registry.items()
        }


def _debug_log_auto_off_stage_skips() -> None:
    """Style D: stage rows with AUTO off + debug on that would have met min_count (AST-1022)."""
    stage_keys = frozenset(
        str(entry["task_key"]).strip() for entry in CANDIDATE_STAGE_DISPATCH.values()
    )
    # Collect would-have-run skips first so index N/M is honest across the batch.
    eligible: List[tuple] = []
    for task in database.list_dispatch_tasks():
        tk = str(task.get("task_key") or "").strip()
        if tk not in stage_keys:
            continue
        if bool(task.get("auto_mode")) or not bool(task.get("debug")):
            continue
        if not task.get("entity_type") or not task.get("trigger_state") or not task.get("candidate_id"):
            continue
        avail = database.count_eligible_for_dispatch_task(task)
        if avail < (task.get("min_count") or 1):
            continue
        eligible.append((task, avail))
    total = len(eligible)
    if not total:
        return
    logger.set_debug_flag(True)
    for i, (task, avail) in enumerate(eligible, start=1):
        logger.debug_index(
            func="dispatcher._tick_loop",
            index=i,
            total=total,
            identifier=task.get("task_key"),
            outcome="skipped — AUTO off",
        )
        logger.debug_detail(
            f"candidate_id={task.get('candidate_id')!r} task_id={task.get('id')} "
            f"available={avail} min_count={task.get('min_count') or 1} auto_mode={task.get('auto_mode')}"
        )


def _tick_loop() -> None:
    """Global tick: wakes every tick_rate_minutes, spawns due AUTO tasks up to max_auto_threads."""
    # Captured once at thread start — changes to ASTRAL_CONFIG require a server restart
    tick_secs = ASTRAL_CONFIG.get("tick_rate_minutes", 1) * 60
    max_auto = ASTRAL_CONFIG.get("max_auto_threads", 3)
    while True:
        try:
            # late: avoid cycle with candidate → dispatcher (module-top import)
            from src.core.candidate import age_stale_candidate_states
            age_stale_candidate_states()
            due = database.get_due_tasks()  # returns auto_mode=1 tasks with available entities
            # Note: freq_hrs is an entity-level filter (applied during batch claim to exclude
            # recently-processed entities), NOT a task-level cooldown. The tick spawns any
            # auto_mode=1 task that has available entities; if none qualify, the runner exits cleanly.
            _debug_log_auto_off_stage_skips()
            with _registry_lock:
                running_auto = sum(1 for e in _task_registry.values() if e["is_auto"])
                running_ids = set(_task_registry.keys())
            slots = max_auto - running_auto
            if slots > 0:
                for task in due:
                    if slots <= 0:
                        break
                    tid = task["id"]
                    if tid in running_ids:
                        continue  # already running
                    if run_task(tid):
                        slots -= 1
        except Exception:
            _sched_log.exception("Tick loop error")
        # Sleep after work so the first server tick runs immediately (was: wait first = silent until
        # tick_rate_minutes elapsed after every process start).
        _tick_event.wait(timeout=tick_secs)
        _tick_event.clear()


def start_scheduler() -> None:
    """Start the tick daemon thread. Safe to call multiple times."""
    global _tick_thread
    if _tick_thread and _tick_thread.is_alive():
        return
    n = database.mark_stale_ledger_interrupted(_now_iso())
    if n:
        _sched_log.warning("Marked %d stale RUNNING ledger row(s) as INTERRUPTED on startup", n)
    try:
        mstats = provision_meteorite_dispatch_tasks()
        _sched_log.info(
            "AST-1054 meteorite dispatch provision template=%s touched=%s added=%s "
            "skipped=%s skipped_missing_config=%s",
            mstats.get("template_candidate_id"),
            mstats.get("candidates_touched"),
            mstats.get("added"),
            mstats.get("skipped"),
            mstats.get("skipped_missing_config"),
        )
    except Exception:
        _sched_log.exception("AST-1054 meteorite dispatch provision failed")
    try:
        gstats = provision_gaze_email_dispatch_task()
        _sched_log.info(
            "AST-1088 gaze_email dispatch provision task_key=%s added=%s skipped=%s "
            "skipped_missing_config=%s id=%s",
            gstats.get("task_key"),
            gstats.get("added"),
            gstats.get("skipped"),
            gstats.get("skipped_missing_config"),
            gstats.get("id"),
        )
    except Exception:
        _sched_log.exception("AST-1088 gaze_email dispatch provision failed")
    _tick_thread = threading.Thread(target=_tick_loop, daemon=True, name="astral-tick")
    _tick_thread.start()
    _sched_log.info("Scheduler started — tick every %dmin, max_auto_threads=%d",
                    ASTRAL_CONFIG.get("tick_rate_minutes", 1),
                    ASTRAL_CONFIG.get("max_auto_threads", 3))
