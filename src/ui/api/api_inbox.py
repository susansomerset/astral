"""Read-email admin API (AST-1033 / Meteorite seed).

Thin Flask wrappers over src.core.inbox. No Gmail I/O here; no persistence.
AST-1047: pass ui_llm_debug into list for From→candidate_match enrichment.
AST-1049: POST create-job — strip/extract + meteorite create orchestration.
"""

from flask import Blueprint, jsonify, request

from ui.auth import require_admin
from src.core.inbox import (
    create_meteorite_job_from_inbox_message,
    get_message_html,
    list_inbox_messages,
)
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger

logger = get_logger(__name__)

inbox_bp = Blueprint("inbox", __name__, url_prefix="/api/admin/inbox")


@inbox_bp.route("/messages", methods=["GET"])
@require_admin
def inbox_list_messages():
    debug = ui_llm_debug(
        explicit_debug=request.args.get("debug", "").lower() in ("1", "true", "yes")
    )
    try:
        messages = list_inbox_messages(debug=debug)
    except Exception as e:
        logger.warning("[api_inbox] list failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify({"messages": messages}), 200


@inbox_bp.route("/messages/<message_id>", methods=["GET"])
@require_admin
def inbox_get_message(message_id: str):
    mid = (message_id or "").strip()
    if not mid:
        return jsonify({"error": "message_id is required"}), 400
    try:
        payload = get_message_html(mid)
    except Exception as e:
        logger.warning("[api_inbox] get failed id=%s: %s", mid, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(payload), 200


@inbox_bp.route("/messages/<message_id>/create-job", methods=["POST"])
@require_admin
def inbox_create_job_from_message(message_id: str):
    mid = (message_id or "").strip()
    if not mid:
        return jsonify({"error": "message_id is required"}), 400
    body = request.get_json(silent=True) or {}
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        result = create_meteorite_job_from_inbox_message(mid, debug=debug)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_inbox] create-job failed id=%s: %s", mid, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(
        {
            "astral_job_id": result["astral_job_id"],
            "company": result["company"],
            "state": result["state"],
            "latest_score": result["latest_score"],
            "company_inserted": result["company_inserted"],
            "astral_candidate_id": result["astral_candidate_id"],
        }
    ), 201
