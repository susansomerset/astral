"""System and infrastructure API endpoints: health, auth, nav config, data shapes."""

from typing import Optional

from flask import Blueprint, g, jsonify, request

from ui.auth import require_auth
from src.core.candidate import get_candidate
from src.utils.config import (
    NAV_CONFIG,
    DATA_SHAPES,
    CANDIDATE_STATES,
    IN_REVIEW_STATES,
    RECOMMENDED_JOB_STATES,
    SKIPPED_STATES,
    UI_CONFIG,
    BUILD_CONFIG,
    build_state_ui_manifest,
)
from src.utils.logging import get_logger

system_bp = Blueprint("system", __name__, url_prefix="/api")

_STATE_INDEX = {state: i for i, state in enumerate(CANDIDATE_STATES.keys())}
_log = get_logger(__name__)


def _is_at_or_past(current_state: str, required_state: str) -> bool:
    """True if current_state is at or past required_state in CANDIDATE_STATES order."""
    return _STATE_INDEX.get(current_state, -1) >= _STATE_INDEX.get(required_state, 999)


def _get_company_counts(candidate_id: Optional[str]) -> dict:
    """Fetch company view counts for nav badges. Returns path -> count mapping."""
    if not candidate_id:
        return {}
    try:
        from src.core.roster import get_active_trigger_states, list_companies, list_company_job_scans

        active = get_active_trigger_states(candidate_id, "company")
        counts = {}
        counts["/companies/watch_list"] = len(list_companies(states=["WATCH"], candidate_id=candidate_id))
        pipeline_states = [s for s in active if s not in ("WATCH", "IGNORE")]
        counts["/companies/new_list"] = len(list_companies(states=pipeline_states, candidate_id=candidate_id)) if pipeline_states else 0
        exclude = list(set(active) | {"IGNORE"})
        counts["/companies/inactive_list"] = len(list_companies(exclude_states=exclude, candidate_id=candidate_id))
        counts["/companies/ignored"] = len(list_companies(states=["IGNORE"], candidate_id=candidate_id))
        counts["/companies/watch_history"] = len(list_company_job_scans(candidate_id=candidate_id))
        return counts
    except Exception:
        _log.debug("Failed to compute company nav counts", exc_info=True)
        return {}


def _get_job_counts(candidate_id: Optional[str]) -> dict:
    """Fetch job view counts for nav badges. Returns path -> count mapping."""
    if not candidate_id:
        return {}
    try:
        from src.core.tracker import count_jobs, count_jobs_below_dispatch_score_floor

        below = count_jobs_below_dispatch_score_floor(candidate_id)
        return {
            "/jobs/recommended": count_jobs(states=list(RECOMMENDED_JOB_STATES), candidate_id=candidate_id),
            "/jobs/in_review": count_jobs(states=list(IN_REVIEW_STATES), candidate_id=candidate_id) - below,
            "/jobs/skipped": count_jobs(states=list(SKIPPED_STATES), candidate_id=candidate_id) + below,
        }
    except Exception:
        _log.debug("Failed to compute job nav counts", exc_info=True)
        return {}


def _resolve_nav(candidate_state: str, candidate_id: Optional[str] = None) -> list:
    """Walk NAV_CONFIG and resolve visible/enabled gates against candidate_state."""
    company_counts = _get_company_counts(candidate_id)
    job_counts = _get_job_counts(candidate_id)
    nav_counts = {**company_counts, **job_counts}
    resolved = []
    for group in NAV_CONFIG:
        visible_gate = group.get("visible")
        if isinstance(visible_gate, str) and not _is_at_or_past(candidate_state, visible_gate):
            continue
        resolved_items = []
        for item in group["items"]:
            enabled_gate = item.get("enabled")
            if enabled_gate is False:
                enabled = False
            elif isinstance(enabled_gate, str):
                enabled = _is_at_or_past(candidate_state, enabled_gate)
            else:
                enabled = True
            nav_item: dict = {"label": item["label"], "path": item["path"], "enabled": enabled}
            count = nav_counts.get(item["path"])
            if count is not None:
                nav_item["count"] = count
            resolved_items.append(nav_item)
        resolved.append({"label": group["label"], "items": resolved_items})
    return resolved


# --- Open endpoints (no auth) ---

@system_bp.route("/health")
def health():
    return {"status": "ok"}


# --- Authenticated endpoints ---

@system_bp.route("/me")
@require_auth
def me():
    return jsonify(g.user)


@system_bp.route("/nav_config")
@require_auth
def nav_config():
    candidate_id = request.args.get("candidate_id", "")
    candidate_state = ""
    if candidate_id:
        candidate = get_candidate(candidate_id)
        if candidate:
            candidate_state = candidate.get("state", "")
    return jsonify(_resolve_nav(candidate_state, candidate_id or None))


@system_bp.route("/shapes/<entity>")
@require_auth
def shapes(entity):
    if entity not in DATA_SHAPES:
        return jsonify({"error": f"Unknown entity: {entity}"}), 404
    return jsonify(DATA_SHAPES[entity])


@system_bp.route("/ui_config")
@require_auth
def ui_config():
    return jsonify({
        **UI_CONFIG,
        "base_resume_accent_palette": BUILD_CONFIG.get("accent_palette", []),
    })


@system_bp.route("/state_ui_manifest")
@require_auth
def state_ui_manifest():
    """G1: job/company/candidate state labels + bulk transition targets from config (single source)."""
    return jsonify(build_state_ui_manifest())


# ---------------------------------------------------------------------------
# Agent Data — read-only endpoints for prompt/response block retrieval
# ---------------------------------------------------------------------------

@system_bp.route("/agent_data/<batch_id>")
@require_auth
def get_agent_data(batch_id):
    """Return all agent_data blocks for a batch. Optional query params: block_type, entity_id."""
    # B1 lazy import: defer core.agent until request time — avoids fragile import cycles
    # during Flask blueprint registration (ui.api ↔ core.agent startup order).
    from src.core.agent import get_agent_data as _get_blocks
    block_type = request.args.get("block_type")
    entity_id = request.args.get("entity_id")
    rows = _get_blocks(batch_id, block_type=block_type, entity_id=entity_id)
    return jsonify(rows)


@system_bp.route("/agent_data/<batch_id>/entity/<entity_id>")
@require_auth
def get_entity_response(batch_id, entity_id):
    """Return the RESPONSE block for a batch, parsed for a specific entity."""
    # B1 lazy import: same rationale as get_agent_data above.
    from src.core.agent import get_entity_response as _get_resp
    row = _get_resp(batch_id, entity_id)
    if not row:
        return jsonify({"error": "No response found for batch/entity"}), 404
    return jsonify(row)
