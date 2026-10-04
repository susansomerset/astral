# -*- coding: utf-8 -*-
"""Core-owned persistence for API cost / timesheet rows (data layer write path).

External `anthropic.send_to_anthropic` stays utils-only; core passes this as
`record_timesheet` so inline token accounting still lands immediately after each call.

Platform cost (AST-1966): after the insert, a row whose model is platform-routed gets its billed cost,
native token counts and serving host looked up on a background thread (reconcile_timesheet_platform).
The call never waits on it; a batch whose ledger row already closed is re-totalled when the cost lands.
"""

import contextvars
import threading
import time
from typing import Any, Optional

from src.data.database import (
    _add_timesheet_entry,
    get_candidate,
    get_dispatch_ledger,
    sum_cost_by_batch,
    update_dispatch_ledger,
    update_timesheet_platform,
)
from src.external.openrouter import get_generation_stats
from src.utils.config import (
    TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS,
    TIMESHEET_RECONCILE_RETRIES,
    get_model_routing,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


def record_timesheet_entry(**kwargs: Any) -> None:
    _add_timesheet_entry(**kwargs)
    agent_req_id = kwargs.get("agent_req_id")
    server_id = kwargs.get("provider", "anthropic")
    # The model's routing decides eligibility; "direct" keeps catalog cost only. Every caller builds
    # (server, SKU) from LLM_MODEL_CONFIG, so get_model_routing's ValueError here means config drift.
    if not agent_req_id or get_model_routing(server_id, kwargs.get("model_code")) == "direct":
        return
    # Own thread, not a task on the caller's loop: it outlives the batch's loop and never blocks the call.
    # copy_context carries log_debug / log_batch_id so the reconcile's debug lines follow the batch's flag.
    # Daemon: a process exit drops an in-flight lookup (no later sweep — parent decision).
    threading.Thread(
        target=contextvars.copy_context().run,
        args=(reconcile_timesheet_platform, agent_req_id, server_id, kwargs.get("candidate_id"), kwargs.get("batch_id")),
        daemon=True,
    ).start()


def reconcile_timesheet_platform(
    agent_req_id: str, server_id: str, candidate_id: Optional[str], batch_id: Optional[str]
) -> None:
    """Background: one row's billed stats → its platform columns, then re-total its batch's ledger row
    if that batch already closed. Never raises; a thrown fault is logged here once."""
    try:
        # Same key source as agent._candidate_server_key (agent imports this module, so it can't be reused).
        key = ((get_candidate(candidate_id) or {}).get("candidate_api_keys") or {}).get(server_id)
        if not key:
            logger.warning(
                "%s | batch %s -> no platform cost [candidate %s has no API key for server %s]. The row keeps its calculated cost",
                agent_req_id, batch_id or "-", candidate_id or "-", server_id,
            )
            return
        logger.debug("Beginning generation-stats loop on %s tries for %s", TIMESHEET_RECONCILE_RETRIES, agent_req_id)
        for attempt in range(TIMESHEET_RECONCILE_RETRIES):
            if attempt:
                # Base wait before the 2nd try, doubled before each later one (2, 4, 8, 16 s by default).
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
        # Closed rows only — an open row is totalled by the batch-close write, which re-sums the table.
        # Recomputed from the table every time, so running it again is harmless.
        if ledger and ledger.get("completed_at"):
            total_cost = sum_cost_by_batch([batch_id]).get(batch_id, 0.0)
            total_processed = ledger.get("total_processed") or 0
            # Same rule as the dispatcher's batch close.
            entity_cost = total_cost / total_processed if total_processed > 0 else total_cost
            update_dispatch_ledger(batch_id, total_cost=total_cost, entity_cost=round(entity_cost, 7))
    except Exception as exc:
        logger.exception(
            "%s | batch %s platform cost reconcile\n  %s: %s\n  Stopping this row's reconcile; the call and batch are unaffected",
            agent_req_id, batch_id or "-", type(exc).__name__, exc,
        )
