"""Surfer API — pacing config (AST-1236) + consent (AST-1235)."""

from flask import Blueprint, jsonify, request

from src.core.candidate import (
    get_candidate,
    opt_in_surfer_consent,
    opt_out_surfer_consent,
    surfer_consent_dto,
)
from src.utils.config import SURFER_PACING_CONFIG
from src.utils.deploy_status import ui_llm_debug
from ui.auth import require_auth

# Shared /api prefix so pacing stays at /api/surfer/... and consent at /api/candidates/...
surfer_bp = Blueprint("surfer", __name__, url_prefix="/api")


def _debug_flag() -> bool:
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    return ui_llm_debug(explicit_debug=explicit)


@surfer_bp.route("/surfer/pacing_config", methods=["GET"])
@require_auth
def pacing_config():
    # Return a plain dict copy so callers cannot mutate the config module.
    return jsonify({
        "dwell_center_seconds": SURFER_PACING_CONFIG["dwell_center_seconds"],
        "dwell_spread_seconds": SURFER_PACING_CONFIG["dwell_spread_seconds"],
        "max_tabs": SURFER_PACING_CONFIG["max_tabs"],
        "mv3_idle_ceiling_seconds": SURFER_PACING_CONFIG["mv3_idle_ceiling_seconds"],
    })


@surfer_bp.route("/candidates/<candidate_id>/surfer/consent", methods=["GET"])
@require_auth
def get_surfer_consent_route(candidate_id):
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    return jsonify(surfer_consent_dto(candidate_id))


@surfer_bp.route("/candidates/<candidate_id>/surfer/consent", methods=["PUT"])
@require_auth
def put_surfer_consent_route(candidate_id):
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    body = request.get_json(silent=True) or {}
    action = body.get("action")
    try:
        if action == "opt_in":
            dto = opt_in_surfer_consent(
                candidate_id, body.get("accepted_version"), debug=_debug_flag()
            )
        elif action == "opt_out":
            dto = opt_out_surfer_consent(candidate_id, debug=_debug_flag())
        else:
            return jsonify({"error": "action must be opt_in or opt_out"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(dto)
