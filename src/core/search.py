"""Universal entity search (AST-2173): one candidate's jobs, companies and meteorites by any string.

Which columns are searched, how results are named, and which modal a job opens all live in config
(SEARCH_ENTITY_CONFIG / SEARCH_JOB_MODAL_BY_LIST). This module tiers, orders and labels the hits.
"""

from typing import Any

from src.core import tracker
from src.data import database
from src.utils.config import (
    APPLIED_JOB_STATES,
    READY_JOB_STATES,
    REVIEW_JOB_STATES,
    SEARCH_ENTITY_CONFIG,
    SEARCH_JOB_MODAL_BY_LIST,
    SKIPPED_STATES,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _jobs_list(job: dict[str, Any], floors: dict[str, float]) -> str:
    """The Jobs page a job shows on — same rules as GET /api/jobs?view=… (a below-floor job is a virtual skip)."""
    state = job.get("state")
    if state in READY_JOB_STATES:
        return "ready"
    if state in REVIEW_JOB_STATES:
        return "review"
    if state in APPLIED_JOB_STATES:
        return "applied"
    if state in SKIPPED_STATES or tracker.job_misses_dispatch_score_floor(job, floors):
        return "skipped"
    return "processing"


def search_entities(candidate_id: str, query: str) -> dict[str, list[dict[str, Any]]]:
    """Every job, company and meteorite of candidate_id with query in a configured field.

    Keyed by entity type (all three keys always present; no match = empty list). Within a type:
    base-field hits first, then payload-only hits, each newest state_changed_at first (read order).
    """
    floors = tracker.score_floor_by_trigger_for_candidate(candidate_id)
    out: dict[str, list[dict[str, Any]]] = {}
    for entity_type, entry in SEARCH_ENTITY_CONFIG.items():
        rows = database.search_entity_rows(entity_type, candidate_id, query)
        logger.debug("Beginning %s search result loop on %d items", entity_type, len(rows))
        base: list[dict[str, Any]] = []
        payload: list[dict[str, Any]] = []
        for row in rows:
            entity_id = row[entry["id_field"]]
            name = " — ".join(str(row[f]).strip() for f in entry["name_fields"] if str(row.get(f) or "").strip())
            tier = "base" if any(f in entry["base_fields"] for f in row["matched_fields"]) else "payload"
            result: dict[str, Any] = {
                "entity_id": entity_id,
                "display_name": name or str(entity_id),
                "state": row.get("state"),
                "tier": tier,
                "matched_fields": row["matched_fields"],
            }
            if entity_type == "job":
                result["jobs_list"] = _jobs_list(row, floors)
                result["modal_kind"] = SEARCH_JOB_MODAL_BY_LIST[result["jobs_list"]]
            # Stable split keeps the read's newest-first order inside each tier.
            (base if tier == "base" else payload).append(result)
        out[entity_type] = base + payload
        logger.debug("End %s search result loop after %d items", entity_type, len(out[entity_type]))
    return out
