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
    update_dispatch_task as _db_update_dispatch_task,
    sum_cost_by_batch as _db_sum_cost_by_batch,
)

from src.data import database
from src.core.agent import _current_agent_task_run_next, compute_batch_cost
from src.utils.config import (
    ASTRAL_CONFIG,
    INFLOW_CONFIG,
    TASK_CONFIG,
    dispatch_task_key_is_scored,
    resume_artifact_compound_state,
    resume_artifact_hop_task_keys,
    trigger_state_used_by_scored_dispatch_task,
)
from src.utils.network import check_internet_reachable
from src.utils.logging import get_logger, log_batch_id, flush_log_buffer

logger = get_logger(__name__)

_INFLOW_DISCOVERY_KEY = INFLOW_CONFIG["discovery"]["task_key"]


def _task_key_scored(task_key: str) -> bool:
    return dispatch_task_key_is_scored(task_key)


def _trigger_state_scored(trigger_state: Optional[str], task_key: str) -> bool:
    return trigger_state_used_by_scored_dispatch_task(trigger_state)


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


def update_dispatch_task(task_id: int, **kwargs) -> None:
    _db_update_dispatch_task(task_id, **kwargs)


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
    "evaluate_jd",
    "consult_do",
    "consult_get",
    "consult_like",
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
    batch_call_mode=0: per-job _warm_then_gather (legacy rows, companies, scrape_jd, …)."""
    if not check_internet_reachable():
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
    batch_call_mode = bool(task.get("batch_call_mode", 0))
    candidate_id    = ctx.get("astral_candidate_id")
    bid             = ctx.get("entity_batch_id") or log_batch_id.get()
    dispatch_task_key = (task.get("task_key") or "").strip()
    s               = dict(_SUMMARY_ZERO)
    if entity_type == "job" and dispatch_task_key in resume_artifact_hop_task_keys():
        expected = resume_artifact_compound_state(dispatch_task_key)
        if (input_state or "").strip() != expected:
            _sched_log.warning(
                "dispatch row mismatch: task_key=%s expects trigger_state=%s got %s — skipping claim",
                dispatch_task_key,
                expected,
                input_state,
            )
            return dict(_SUMMARY_ZERO)
    if debug and dispatch_task_key == _INFLOW_DISCOVERY_KEY:
        logger.set_debug_flag(True)

    if entity_type == "board_search":
        from src.data.database import claim_board_search_batch, clear_board_search_batch
        from src.utils.config import BOARDS_CONFIG

        gaze_cfg = BOARDS_CONFIG.get("gaze_board") or {}
        batch_limit = limit if limit is not None else int(gaze_cfg.get("batch_size", 5))
        freq = float(task.get("freq_hrs") or 0)
        cfg_iv = gaze_cfg.get("scan_interval_hours")
        default_scan_iv = float(cfg_iv) if cfg_iv is not None else 24.0
        eff_scan = freq if freq > 0 else default_scan_iv
        sort_bs = (task.get("sort_by") or "").strip() or None
        entities = claim_board_search_batch(
            bid,
            batch_limit,
            candidate_id=candidate_id,
            scan_interval_hours=eff_scan,
            sort_by=sort_bs,
        )
    elif entity_type == "candidate":
        entities = [ctx] if ctx else []
    elif entity_type == "job":
        task_key_run = task.get("task_key", "")
        is_scored = _trigger_state_scored(input_state, task_key_run)
        floor = float(task.get("score_floor")) if (is_scored and task.get("score_floor") is not None) else (1.0 if is_scored else None)
        claim_cap = None
        if batch_call_mode and task_key_run in _CHUNK_EXHAUST_CONSULT_JOB_KEYS:
            if task.get("batch_size") is None:
                raise ValueError(
                    "dispatch_tasks.batch_size is required for consult chunk exhaustion "
                    f"(task_key={task_key_run!r} id={task.get('id')})"
                )
            claim_cap = database.count_eligible_for_dispatch_task(task)
        bid, entities = get_new_job_batch(
            input_state,
            limit=limit,
            sort_by=sort_by,
            score_floor=floor,
            candidate_id=candidate_id,
            batch_id=bid,
            claim_cap=claim_cap,
        )
    else:
        freq = float(task.get("freq_hrs") or 0)
        # freq_hrs on dispatch_task overrides COMPANY_STATES scan_interval for gaze (WATCH) claim + count.
        scan_override = freq if freq > 0 else None
        sort_override = (task.get("sort_by") or "").strip() or None
        resolve_key = INFLOW_CONFIG["resolve"]["task_key"]
        floor = float(task["score_floor"]) if task.get("score_floor") is not None else None
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
        )

    if not entities:
        if debug and dispatch_task_key == _INFLOW_DISCOVERY_KEY:
            logger.debug_index(
                func="dispatcher._run_unified",
                index=1,
                total=1,
                identifier=f"{entity_type}/{input_state}",
                outcome="no entities claimed",
            )
        elif debug:
            logger.info("[DEBUG] _run_unified[%s/%s]: no entities claimed", entity_type, input_state)
        return s

    if debug and dispatch_task_key == _INFLOW_DISCOVERY_KEY:
        logger.debug_index(
            func="dispatcher._run_unified",
            index=1,
            total=1,
            identifier=f"{entity_type}/{input_state}",
            outcome=f"claimed {len(entities)} entity/entities",
        )
        logger.debug_detail(
            f"batch_id={bid} batch_call_mode={batch_call_mode} dispatch batch_size={limit!r}"
        )
    elif debug:
        logger.info(
            "[DEBUG] _run_unified[%s/%s]: claimed %d entities (batch=%s) batch_call_mode=%s dispatch batch_size=%r",
            entity_type,
            input_state,
            len(entities),
            bid,
            batch_call_mode,
            limit,
        )
    try:
        if batch_call_mode:
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
    finally:
        if entity_type == "job":
            clear_job_batch(bid)
        elif entity_type == "board_search":
            from src.data.database import clear_board_search_batch
            clear_board_search_batch(bid)
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
        logger.warning(
            "CIRCUIT BREAKER: %s has had %d consecutive runs with 0 passed / 0 failed — auto-disabling task %s",
            task_key, _CIRCUIT_BREAKER_THRESHOLD, task_id,
        )
        _db_update_dispatch_task(task_id, enabled=False)


async def _run_task(task: Dict, ctx: Dict, debug: bool) -> Dict[str, int]:
    """Run a single batch through the unified runner. Returns summary counts."""
    bid = log_batch_id.get()
    task_key = (task.get("task_key") or "").strip()
    if debug and task_key == _INFLOW_DISCOVERY_KEY:
        logger.debug_index(
            func="dispatcher._run_task",
            index=1,
            total=1,
            identifier=task_key,
            outcome="running",
        )
        logger.debug_detail(f"batch_size={task.get('batch_size')} batch_id={bid}")
    elif debug:
        logger.info(
            "[DEBUG] _run_task: running '%s' batch_size=%s batch_id=%s...",
            task.get("task_key"),
            task.get("batch_size"),
            bid,
        )
    summary = await _run_unified(task, ctx, debug)
    if debug and task_key == _INFLOW_DISCOVERY_KEY:
        logger.debug_detail(f"runner returned summary={summary}")
    elif debug:
        logger.info("[DEBUG] _run_task: runner returned summary=%s", summary)
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

    ctx = database.get_candidate(candidate_id)
    if not ctx or not ctx.get("candidate_api_key"):
        _sched_log.error("Skipping %s/%s — no candidate or API key", task_key, candidate_id)
        return
    ctx = dict(ctx)
    if task.get("skip_cache"):
        ctx["skip_cache"] = True

    entity_batch_id = f"{task_key}-{uuid.uuid4()}"
    has_run_next_chain = bool(_current_agent_task_run_next(task_key))
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
        _sched_log.error("[%s/%s] killed after %ds timeout", task_key, entity_batch_id, timeout)
        accumulated["total_errors"] = accumulated.get("total_errors", 0) + 1
    except asyncio.CancelledError:
        final_status = "INTERRUPTED"
        _sched_log.warning("[%s/%s] KILLED by admin — thread cleared from memory", task_key, entity_batch_id)
        accumulated["total_errors"] = accumulated.get("total_errors", 0) + 1
    except Exception:
        final_status = "FAILED"
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
            except Exception as e:
                _sched_log.error("Failed to write ledger for %s/%s: %s", task_key, dispatch_ledger_id, e)
        flush_log_buffer()
        # Alert while log_batch_id still set — monitor logs appear in the batch log view
        if dispatch_ledger_id and not is_click and accumulated.get("total_errors", 0) > 0:
            monitor.auto_run_error(task_key, dispatch_ledger_id, accumulated, final_status)
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
            _sched_log.info("[%s] drain flag set — stopping after %d run(s)", task_key, run_count)
            break
        summary = await _run_task(task, ctx, debug)
        for k in accumulated:
            accumulated[k] += summary.get(k, 0)
        run_count += 1
        # Update ledger mid-run so the execution history reflects live progress
        if dispatch_ledger_id:
            database.update_dispatch_ledger(dispatch_ledger_id, **accumulated)
        if summary.get("total_processed", 0) == 0:
            _sched_log.info("Loop mode %s: 0 processed — stopping", task_key)
            break
        if max_runs != 0:
            if max_runs is None or run_count >= max_runs:
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


def run_task(task_id: int) -> bool:
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


def _tick_loop() -> None:
    """Global tick: wakes every tick_rate_minutes, spawns due AUTO tasks up to max_auto_threads."""
    # Captured once at thread start — changes to ASTRAL_CONFIG require a server restart
    tick_secs = ASTRAL_CONFIG.get("tick_rate_minutes", 1) * 60
    max_auto = ASTRAL_CONFIG.get("max_auto_threads", 3)
    while True:
        try:
            due = database.get_due_tasks()  # returns auto_mode=1 tasks with available entities
            # Note: freq_hrs is an entity-level filter (applied during batch claim to exclude
            # recently-processed entities), NOT a task-level cooldown. The tick spawns any
            # auto_mode=1 task that has available entities; if none qualify, the runner exits cleanly.
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
    _tick_thread = threading.Thread(target=_tick_loop, daemon=True, name="astral-tick")
    _tick_thread.start()
    _sched_log.info("Scheduler started — tick every %dmin, max_auto_threads=%d",
                    ASTRAL_CONFIG.get("tick_rate_minutes", 1),
                    ASTRAL_CONFIG.get("max_auto_threads", 3))
