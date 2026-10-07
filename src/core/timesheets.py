# -*- coding: utf-8 -*-
"""Core-owned persistence for API cost / timesheet rows (data layer write path).

External `anthropic.send_to_anthropic` stays utils-only; core passes this as
`record_timesheet` so inline token accounting still lands immediately after each call.

OpenRouter platform cost: after a dispatch batch completes, a daemon thread runs
`reconcile_pending_gen_platform` — passive /generation lookups for all gen-* rows
still missing platform_cost (6 passes at 30…180s), then refreshes closed ledger totals
for every batch that gained platform_cost on that pass.
Per-call background reconcile (AST-1966) stays off via TIMESHEET_RECONCILE_ENABLED.
"""

import contextvars
import json
import threading
import time
from typing import Any, Optional

from src.data.database import (
    _add_timesheet_entry,
    count_pending_gen_platform_timesheets,
    get_candidate,
    get_dispatch_ledger,
    list_pending_gen_platform_timesheets,
    sum_cost_by_batch,
    update_dispatch_ledger,
    update_timesheet_platform,
)
from src.external.openrouter import get_generation_record, get_generation_stats
from src.utils.config import (
    TIMESHEET_BATCH_RECONCILE_ENABLED,
    TIMESHEET_BATCH_RECONCILE_PING_AT_SECONDS,
    TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS,
    TIMESHEET_RECONCILE_ENABLED,
    TIMESHEET_RECONCILE_INITIAL_WAIT_SECONDS,
    TIMESHEET_RECONCILE_RETRIES,
    get_model_routing,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)

_OPENROUTER_SERVER = "openrouter"


def record_timesheet_entry(**kwargs: Any) -> None:
    _add_timesheet_entry(**kwargs)
    if not TIMESHEET_RECONCILE_ENABLED:
        return
    agent_req_id = kwargs.get("agent_req_id")
    server_id = kwargs.get("provider", "anthropic")
    if not agent_req_id or get_model_routing(server_id, kwargs.get("model_code")) == "direct":
        return
    threading.Thread(
        target=contextvars.copy_context().run,
        args=(reconcile_timesheet_platform, agent_req_id, server_id, kwargs.get("candidate_id"), kwargs.get("batch_id")),
        daemon=True,
    ).start()


def start_batch_openrouter_platform_reconcile(batch_id: Optional[str]) -> None:
    """Queue OpenRouter platform reconcile after dispatch; no-op when disabled or nothing pending globally."""
    if not TIMESHEET_BATCH_RECONCILE_ENABLED:
        return
    if count_pending_gen_platform_timesheets() == 0:
        logger.debug(
            "No pending gen-* timesheet rows (trigger batch %s); skipping platform reconcile",
            batch_id or "-",
        )
        return
    threading.Thread(
        target=contextvars.copy_context().run,
        args=(reconcile_pending_gen_platform,),
        daemon=True,
    ).start()


def _sleep_until(deadline: float) -> None:
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 1.0))


def _openrouter_key_for_candidate(candidate_id: Optional[str]) -> Optional[str]:
    key = ((get_candidate(candidate_id) or {}).get("candidate_api_keys") or {}).get(_OPENROUTER_SERVER)
    return key if key else None


def _try_reconcile_gen_row(agent_req_id: str, candidate_id: Optional[str]) -> bool:
    """One /generation lookup; writes platform columns + metadata blob on success. Never raises."""
    key = _openrouter_key_for_candidate(candidate_id)
    if not key:
        logger.debug("%s | no openrouter key for candidate %s; skipping platform lookup", agent_req_id, candidate_id or "-")
        return False
    logger.debug("Calling get_generation_record: id=%s", agent_req_id)
    record = get_generation_record(agent_req_id, key)
    logger.debug("Response from get_generation_record: id=%s success=%s", agent_req_id, record.get("success"))
    if not record.get("success"):
        return False
    data = record["data"]
    update_timesheet_platform(
        agent_req_id,
        float(data["total_cost"]),
        data.get("native_tokens_prompt"),
        data.get("native_tokens_completion"),
        data.get("native_tokens_cached"),
        data.get("native_tokens_reasoning"),
        data.get("provider_name"),
        platform_metadata=json.dumps(data, separators=(",", ":"), default=str),
    )
    return True


def _refresh_closed_batch_ledger_total(batch_id: str) -> None:
    ledger = get_dispatch_ledger(batch_id)
    if not ledger or not ledger.get("completed_at"):
        return
    total_cost = sum_cost_by_batch([batch_id]).get(batch_id, 0.0)
    total_processed = ledger.get("total_processed") or 0
    entity_cost = total_cost / total_processed if total_processed > 0 else total_cost
    update_dispatch_ledger(batch_id, total_cost=total_cost, entity_cost=round(entity_cost, 7))


def reconcile_pending_gen_platform() -> None:
    """Passive gen-* platform fill globally: ping at 30…180s while any rows lack platform_cost."""
    try:
        if count_pending_gen_platform_timesheets() == 0:
            return
        started = time.monotonic()
        logger.debug("Beginning global platform reconcile at %s", TIMESHEET_BATCH_RECONCILE_PING_AT_SECONDS)
        for ping_at in TIMESHEET_BATCH_RECONCILE_PING_AT_SECONDS:
            _sleep_until(started + float(ping_at))
            pending = list_pending_gen_platform_timesheets()
            if not pending:
                logger.debug("No pending gen-* rows at %ss; stopping reconcile", ping_at)
                break
            batches_touched: set[str] = set()
            for row in pending:
                if _try_reconcile_gen_row(row["agent_req_id"], row.get("candidate_id")):
                    bid = str(row.get("batch_id") or "").strip()
                    if bid:
                        batches_touched.add(bid)
            for bid in batches_touched:
                _refresh_closed_batch_ledger_total(bid)
        logger.debug("End global platform reconcile")
    except Exception as exc:
        logger.exception(
            "global platform cost reconcile\n  %s: %s\n  Stopping reconcile; dispatch is unaffected",
            type(exc).__name__,
            exc,
        )


def reconcile_timesheet_platform(
    agent_req_id: str, server_id: str, candidate_id: Optional[str], batch_id: Optional[str]
) -> None:
    """Legacy per-call background reconcile (TIMESHEET_RECONCILE_ENABLED). Never raises."""
    try:
        key = ((get_candidate(candidate_id) or {}).get("candidate_api_keys") or {}).get(server_id)
        if not key:
            logger.warning(
                "%s | batch %s -> no platform cost [candidate %s has no API key for server %s]. The row keeps its calculated cost",
                agent_req_id, batch_id or "-", candidate_id or "-", server_id,
            )
            return
        logger.debug("Beginning generation-stats loop on %s tries for %s", TIMESHEET_RECONCILE_RETRIES, agent_req_id)
        logger.debug(
            "Waiting %s s before the first generation-stats lookup for %s",
            TIMESHEET_RECONCILE_INITIAL_WAIT_SECONDS, agent_req_id,
        )
        time.sleep(TIMESHEET_RECONCILE_INITIAL_WAIT_SECONDS)
        stats: dict[str, Any] = {"success": False, "error": "not started"}
        for attempt in range(TIMESHEET_RECONCILE_RETRIES):
            if attempt:
                wait = TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)
                logger.debug("Retrying get_generation_stats for %s in %s s (try %s)", agent_req_id, wait, attempt + 1)
                time.sleep(wait)
            logger.debug("Calling get_generation_stats: id=%s", agent_req_id)
            stats = get_generation_stats(agent_req_id, key)
            logger.debug("Response from get_generation_stats: %s", stats)
            if stats["success"]:
                break
        logger.debug("End generation-stats loop after %s tries for %s", attempt + 1, agent_req_id)
        if not stats["success"]:
            logger.warning(
                "%s | batch %s -> no platform cost after %s tries [%s]. The row keeps its calculated cost",
                agent_req_id, batch_id or "-", TIMESHEET_RECONCILE_RETRIES, stats["error"],
            )
            return
        update_timesheet_platform(
            agent_req_id, stats["total_cost"], stats["native_tokens_prompt"], stats["native_tokens_completion"],
            stats["native_tokens_cached"], stats["native_tokens_reasoning"], stats["provider_name"],
        )
        ledger = get_dispatch_ledger(batch_id) if batch_id else None
        if ledger and ledger.get("completed_at"):
            total_cost = sum_cost_by_batch([batch_id]).get(batch_id, 0.0)
            total_processed = ledger.get("total_processed") or 0
            entity_cost = total_cost / total_processed if total_processed > 0 else total_cost
            update_dispatch_ledger(batch_id, total_cost=total_cost, entity_cost=round(entity_cost, 7))
    except Exception as exc:
        logger.exception(
            "%s | batch %s platform cost reconcile\n  %s: %s\n  Stopping this row's reconcile; the call and batch are unaffected",
            agent_req_id, batch_id or "-", type(exc).__name__, exc,
        )
