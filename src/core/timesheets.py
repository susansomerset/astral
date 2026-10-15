# -*- coding: utf-8 -*-
"""Core-owned persistence for service_timesheet rows and the fetch_timesheet runner (AST-2218).

External clients pass `record_timesheet` so inline token accounting lands after each call.
Platform receipts are fetched by the candidate-bound `fetch_timesheet` dispatch task — no daemon
threads. Search-call recording is exposed for AST-2219; roster wiring is out of this module's callers.
"""

import uuid
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from src.data.database import (
    _add_timesheet_entry,
    claim_ledger_timesheet_fetching,
    get_candidate,
    get_dispatch_ledger,
    list_timesheet_rows_for_batches,
    set_ledger_timesheet_state,
    sum_cost_by_batch,
    update_dispatch_ledger,
    update_timesheet_platform,
)
from src.utils.config import TIMESHEET_SEARCH_SERVER_ID
from src.utils.logging import get_logger

logger = get_logger(__name__)

_SUMMARY_ZERO: Dict[str, int] = {
    "total_processed": 0,
    "total_passed": 0,
    "total_failed": 0,
    "total_errors": 0,
}

# completion_status values that mean "not receipted yet" (OpenRouter get_receipt).
_NOT_RECEIPTED_STATUSES = frozenset({"error", "not_ready"})


def record_timesheet_entry(**kwargs: Any) -> None:
    """Write one timesheet row. No background reconcile (AST-2218)."""
    _add_timesheet_entry(**kwargs)


def record_search_timesheet_entry(
    candidate_id: Optional[str],
    batch_id: Optional[str],
    hit_count: int,
    *,
    call_start: Optional[str] = None,
    call_stop: Optional[str] = None,
    completion_status: str = "success",
) -> None:
    """Record one DISPATCH_SEARCH row (AST-2218 recorder; AST-2219 wires roster call sites)."""
    record_timesheet_entry(
        agent_req_id=f"search-{uuid.uuid4()}",
        task_key_uuid=None,
        model_code=None,
        candidate_id=candidate_id,
        batch_id=batch_id,
        batch_size=1,
        cache_write_tokens=0,
        cache_read_tokens=0,
        no_cache_prompt_tokens=0,
        no_cache_live_tokens=0,
        total_no_cache_input_tokens=0,
        total_output_tokens=0,
        calc_cost_cache_write=0.0,
        calc_cost_cache_read=0.0,
        calc_cost_no_cache_input=0.0,
        calc_cost_output=0.0,
        provider=TIMESHEET_SEARCH_SERVER_ID,
        request_type="DISPATCH_SEARCH",
        entity_type=None,
        entity_id=None,
        call_start=call_start,
        call_stop=call_stop,
        response_item_count=int(hit_count or 0),
        response_char_length=0,
        completion_status=completion_status,
    )


def _api_key_for_server(candidate_id: str, server_id: str) -> Optional[str]:
    key = ((get_candidate(candidate_id) or {}).get("candidate_api_keys") or {}).get(server_id)
    return key if key else None


def _get_receipt_fn(provider: str):
    """Resolve the billing external's get_receipt by timesheet provider (server id)."""
    if provider == "openrouter":
        from src.external.openrouter import get_receipt
        return get_receipt
    if provider == "anthropic":
        from src.external.anthropic import get_receipt
        return get_receipt
    from src.external.llm_compat import get_receipt
    return get_receipt


def _receipt_is_applied(receipt: Dict[str, Any]) -> bool:
    """True when the receipt should stamp platform columns (billed or stub-complete)."""
    status = str(receipt.get("completion_status") or "")
    return status not in _NOT_RECEIPTED_STATUSES


def _apply_receipt(agent_req_id: str, receipt: Dict[str, Any]) -> None:
    """Write vendor half onto the timesheet row; host/reasoning left None (not on shared shape)."""
    update_timesheet_platform(
        agent_req_id,
        receipt.get("platform_cost"),
        receipt.get("native_tokens_prompt"),
        receipt.get("native_tokens_completion"),
        receipt.get("native_tokens_cached"),
        None,  # native_tokens_reasoning — not on TIMESHEET_RECEIPT_FIELDS
        None,  # host
    )


def _refresh_closed_ledger_totals(batch_id: str) -> None:
    ledger = get_dispatch_ledger(batch_id)
    if not ledger or not ledger.get("completed_at"):
        return
    total_cost = sum_cost_by_batch([batch_id]).get(batch_id, 0.0)
    total_processed = ledger.get("total_processed") or 0
    entity_cost = total_cost / total_processed if total_processed > 0 else total_cost
    update_dispatch_ledger(batch_id, total_cost=total_cost, entity_cost=round(entity_cost, 7))


def run_fetch_timesheet(candidate_id: str) -> Dict[str, int]:
    """Claim NEW ledger rows → FETCHING, fetch receipts, RECEIPTED/NEW, release on finally.

    Returns dispatcher summary counts. Never leaves rows in FETCHING after return.
    """
    cid = str(candidate_id or "").strip()
    summary = dict(_SUMMARY_ZERO)
    claimed: List[str] = []
    receipted_ids: Set[str] = set()
    logger.debug("fetch_timesheet begin candidate_id=%s", cid or "-")
    try:
        if not cid:
            return summary
        claimed = claim_ledger_timesheet_fetching(cid)
        if not claimed:
            logger.debug("fetch_timesheet end candidate_id=%s claimed=0", cid)
            return summary
        rows = list_timesheet_rows_for_batches(claimed)
        summary["total_processed"] = len(rows)

        by_provider: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            prov = str(row.get("provider") or "").strip() or "anthropic"
            by_provider[prov].append(row)

        for provider, group in by_provider.items():
            ids = [str(r.get("agent_req_id") or "") for r in group if r.get("agent_req_id")]
            if not ids:
                continue
            key = _api_key_for_server(cid, provider)
            if not key:
                logger.warning(
                    "fetch_timesheet | candidate %s has no API key for server %s — skipping %s id(s)",
                    cid, provider, len(ids),
                )
                summary["total_failed"] += len(ids)
                continue
            get_receipt = _get_receipt_fn(provider)
            logger.debug("Calling get_receipt: provider=%s ids=%s", provider, ids)
            receipts = get_receipt(ids, key)
            logger.debug("Response from get_receipt: provider=%s n=%s", provider, len(receipts))
            # Align by index with the ids we sent.
            for agent_req_id, receipt in zip(ids, receipts):
                if not _receipt_is_applied(receipt):
                    logger.warning(
                        "fetch_timesheet | id %s provider %s not receipted [%s]",
                        agent_req_id, provider, receipt.get("completion_status"),
                    )
                    summary["total_failed"] += 1
                    continue
                _apply_receipt(agent_req_id, receipt)
                receipted_ids.add(agent_req_id)
                summary["total_passed"] += 1

        # Per claimed ledger: RECEIPTED iff every timesheet row for that batch is receipted
        # (vacuous when the batch has zero timesheet rows — plan Stage 3g).
        rows_by_batch: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            bid = str(row.get("batch_id") or "").strip()
            if bid:
                rows_by_batch[bid].append(row)
        for batch_id in claimed:
            batch_rows = rows_by_batch.get(batch_id, [])
            all_done = all(
                str(r.get("agent_req_id") or "") in receipted_ids for r in batch_rows
            )
            if all_done:
                set_ledger_timesheet_state(batch_id, "RECEIPTED")
                _refresh_closed_ledger_totals(batch_id)
            else:
                set_ledger_timesheet_state(batch_id, "NEW")
        logger.debug(
            "fetch_timesheet end candidate_id=%s processed=%s passed=%s failed=%s",
            cid, summary["total_processed"], summary["total_passed"], summary["total_failed"],
        )
        return summary
    except Exception as exc:
        summary["total_errors"] = 1
        logger.exception(
            "fetch_timesheet | candidate %s\n  %s: %s\n  Releasing FETCHING rows to NEW",
            cid or "-", type(exc).__name__, exc,
        )
        return summary
    finally:
        # Release any still-FETCHING claim (exception or partial path).
        for batch_id in claimed:
            ledger = get_dispatch_ledger(batch_id)
            if ledger and ledger.get("timesheet_state") == "FETCHING":
                set_ledger_timesheet_state(batch_id, "NEW")
