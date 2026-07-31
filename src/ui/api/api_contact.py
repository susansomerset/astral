"""Admin Contact skill ACL + Manage Slack listen/activity API (AST-1071 / AST-1067 / AST-1094).

Thin wrappers over src.core.contact.
"""

from flask import Blueprint, jsonify, request

from ui.auth import require_admin
from src.core.contact import (
    contact_is_production_deploy,
    contact_skills,
    list_estelle_activity,
    run_contact_skill,
    set_slack_listen_enabled,
    slack_listen_enabled,
)
from src.utils.deploy_status import get_deploy_label, ui_llm_debug
from src.utils.logging import get_logger

logger = get_logger(__name__)

contact_bp = Blueprint("contact", __name__, url_prefix="/api/admin/contact")


def _listen_payload() -> dict:
    return {
        "listen_enabled": slack_listen_enabled(),
        "environment": get_deploy_label(),
        "is_production": contact_is_production_deploy(),
    }


@contact_bp.route("/listen", methods=["GET"])
@require_admin
def contact_get_listen():
    return jsonify(_listen_payload()), 200


@contact_bp.route("/listen", methods=["PUT"])
@require_admin
def contact_put_listen():
    body = request.get_json(silent=True) or {}
    enabled = body.get("listen_enabled")
    if not isinstance(enabled, bool):
        return jsonify({"error": "listen_enabled must be a bool"}), 400
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        set_slack_listen_enabled(enabled, debug=debug)
    except TypeError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_contact] listen set failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify(_listen_payload()), 200



@contact_bp.route("/estelle_activity", methods=["GET"])
@require_admin
def contact_get_estelle_activity():
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        users = list_estelle_activity(debug=debug)
    except Exception as e:
        logger.warning("[api_contact] estelle_activity list failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify({"users": users}), 200


@contact_bp.route("/skills", methods=["GET"])
@require_admin
def contact_list_skills():
    # JSON-safe copy: allowed_paths as lists.
    out = {}
    for key, meta in contact_skills().items():
        row = dict(meta) if isinstance(meta, dict) else {}
        paths = row.get("allowed_paths")
        if isinstance(paths, (tuple, list)):
            row["allowed_paths"] = list(paths)
        out[key] = row
    return jsonify({"skills": out}), 200


@contact_bp.route("/skills/<skill_key>", methods=["POST"])
@require_admin
def contact_run_skill(skill_key: str):
    body = request.get_json(silent=True) or {}
    cid = body.get("astral_candidate_id")
    fields = body.get("fields")
    if not isinstance(cid, str):
        cid = ""
    if not isinstance(fields, dict):
        return jsonify({"error": "fields must be a dict"}), 400
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        result = run_contact_skill(
            skill_key,
            astral_candidate_id=cid,
            fields=fields,
            debug=debug,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_contact] skill failed key=%s: %s", skill_key, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(result), 200
