"""Admin Contact skill ACL + Manage Slack listen/activity/debug API (AST-1071 / AST-1067 / AST-1094 / AST-1206).

Thin wrappers over src.core.contact.
"""

from flask import Blueprint, jsonify, request

from ui.auth import require_admin
from src.core.contact import (
    check_admin_slack_channel_membership,
    contact_is_production_deploy,
    contact_skills,
    get_admin_slack_channel_snapshot,
    list_admin_slack_channels,
    list_estelle_activity,
    list_unbound_slack_users,
    run_contact_skill,
    set_slack_debug_enabled,
    set_slack_listen_enabled,
    slack_debug_enabled,
    slack_listen_enabled,
)
from src.utils.deploy_status import get_deploy_label, ui_llm_debug
from src.utils.logging import get_logger

logger = get_logger(__name__)

contact_bp = Blueprint("contact", __name__, url_prefix="/api/admin/contact")


def _api_completed(candidate_id: str, route: str, method: str, status: int) -> None:
    cid = (candidate_id or "").strip() or "-"
    logger.info("%s | api %s completed: %s %s", cid, route, method, status)


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
        logger.exception(
            "%s | api %s\n  %s: %s\n  Returning 502",
            "-", "/api/admin/contact/listen", type(e).__name__, e,
        )
        return jsonify({"error": str(e)}), 502
    _api_completed("-", "/api/admin/contact/listen", "PUT", 200)
    return jsonify(_listen_payload()), 200


def _debug_payload() -> dict:
    return {
        "debug_enabled": slack_debug_enabled(),
        "environment": get_deploy_label(),
        "is_production": contact_is_production_deploy(),
    }


@contact_bp.route("/debug", methods=["GET"])
@require_admin
def contact_get_debug():
    return jsonify(_debug_payload()), 200


@contact_bp.route("/debug", methods=["PUT"])
@require_admin
def contact_put_debug():
    body = request.get_json(silent=True) or {}
    enabled = body.get("debug_enabled")
    if not isinstance(enabled, bool):
        return jsonify({"error": "debug_enabled must be a bool"}), 400
    explicit = (
        request.args.get("debug", "").lower() in ("1", "true", "yes")
        or bool(body.get("debug"))
    )
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        set_slack_debug_enabled(enabled, debug=debug)
    except TypeError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception(
            "%s | api %s\n  %s: %s\n  Returning 502",
            "-", "/api/admin/contact/debug", type(e).__name__, e,
        )
        return jsonify({"error": str(e)}), 502
    _api_completed("-", "/api/admin/contact/debug", "PUT", 200)
    return jsonify(_debug_payload()), 200


@contact_bp.route("/estelle_activity", methods=["GET"])
@require_admin
def contact_get_estelle_activity():
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        users = list_estelle_activity(debug=debug)
    except Exception as e:
        logger.exception(
            "%s | api %s\n  %s: %s\n  Returning 502",
            "-", "/api/admin/contact/estelle_activity", type(e).__name__, e,
        )
        return jsonify({"error": str(e)}), 502
    return jsonify({"users": users}), 200


@contact_bp.route("/unbound_slack_users", methods=["GET"])
@require_admin
def contact_get_unbound_slack_users():
    # Idempotent GET — no progress info line (stat.logging.info.api).
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        users = list_unbound_slack_users(debug=debug)
    except Exception as e:
        logger.exception(
            "- | api /api/admin/contact/unbound_slack_users failed: %s: %s\n"
            "  Unbound list was not returned",
            type(e).__name__,
            e,
        )
        return jsonify({"error": str(e)}), 502
    return jsonify({"users": users}), 200


@contact_bp.route("/slack_channels", methods=["GET"])
@require_admin
def contact_get_slack_channels():
    # Idempotent GET — no progress info line (stat.logging.info.api).
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        channels = list_admin_slack_channels(debug=debug)
    except Exception as e:
        logger.exception(
            "- | api /api/admin/contact/slack_channels failed: %s: %s\n"
            "  Channel list was not returned",
            type(e).__name__,
            e,
        )
        return jsonify({"error": str(e)}), 502
    return jsonify({"channels": channels}), 200


@contact_bp.route("/slack_channel_membership", methods=["GET"])
@require_admin
def contact_get_slack_channel_membership():
    # Idempotent GET — no progress info line (stat.logging.info.api).
    cid = (request.args.get("astral_candidate_id") or "").strip()
    channel = (request.args.get("channel") or "").strip()
    if not cid:
        return jsonify({"error": "astral_candidate_id is required"}), 400
    if not channel:
        return jsonify({"error": "channel is required"}), 400
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        payload = check_admin_slack_channel_membership(
            astral_candidate_id=cid, channel=channel, debug=debug
        )
    except ValueError as e:
        msg = str(e)
        if msg == "candidate not found":
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except Exception as e:
        logger.exception(
            "%s | api /api/admin/contact/slack_channel_membership failed: %s: %s\n"
            "  Membership check was not returned",
            cid or "-",
            type(e).__name__,
            e,
        )
        return jsonify({"error": str(e)}), 502
    return jsonify(payload), 200


@contact_bp.route("/slack_channel_snapshot", methods=["GET"])
@require_admin
def contact_get_slack_channel_snapshot():
    # Idempotent GET — no progress info line (stat.logging.info.api).
    cid = (request.args.get("astral_candidate_id") or "").strip()
    if not cid:
        return jsonify({"error": "astral_candidate_id is required"}), 400
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    debug = ui_llm_debug(explicit_debug=explicit)
    try:
        payload = get_admin_slack_channel_snapshot(
            astral_candidate_id=cid, debug=debug
        )
    except ValueError as e:
        msg = str(e)
        if msg == "candidate not found":
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except Exception as e:
        logger.exception(
            "%s | api /api/admin/contact/slack_channel_snapshot failed: %s: %s\n"
            "  Channel snapshot was not returned",
            cid or "-",
            type(e).__name__,
            e,
        )
        return jsonify({"error": str(e)}), 502
    return jsonify(payload), 200


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
        logger.exception(
            "%s | api %s\n  %s: %s\n  Returning 502",
            cid or "-", f"/api/admin/contact/skills/{skill_key}", type(e).__name__, e,
        )
        return jsonify({"error": str(e)}), 502
    _api_completed(cid, f"/api/admin/contact/skills/{skill_key}", "POST", 200)
    return jsonify(result), 200
