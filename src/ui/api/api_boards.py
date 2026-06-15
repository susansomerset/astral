"""Board catalog (AST-415) and saved board_search CRUD + craft generation (AST-416).

Read-only adopted-board list/detail plus `/searches` routes share this blueprint.
"""

from __future__ import annotations

import re

from flask import Blueprint, jsonify, request

from src.core.boards import (
    _BOARD_SEARCH_TASK_KEYS,
    _PATCH_UNSET,
    DeeplinkDomainMismatchError,
    DuplicateBoardSearchError,
    delete_board_search,
    get_board_search,
    list_board_searches,
    run_board_search_generation,
    save_board_search,
    update_board_search,
)
from src.utils.config import get_board_entry, list_adopted_boards
from src.utils.deploy_status import ui_llm_debug
from ui.auth import require_auth

boards_bp = Blueprint("boards", __name__, url_prefix="/api/boards")

_CREDENTIAL_KEY = re.compile(r"(?i)(password|username|cookie|token|credential)")


def _reject_credentials(obj) -> bool:
    """True if any key in nested dict/list looks like a credential field."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if _CREDENTIAL_KEY.search(str(k)):
                return True
            if _reject_credentials(v):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if _reject_credentials(item):
                return True
    return False


def _serialize_board_search(row: dict):
    """API wire: expose `mode` instead of internal `search_mode`."""
    if not row:
        return row
    out = dict(row)
    out["mode"] = out.pop("search_mode", None) or "criteria"
    out.pop("enabled", None)  # legacy — AST-471 uses workflow `state`
    return out


@boards_bp.route("/searches", methods=["GET"])
@require_auth
def list_searches():
    candidate_id = request.args.get("candidate_id")
    if not candidate_id:
        return jsonify({"error": "candidate_id required"}), 400
    board_key = request.args.get("board_key")
    rows = list_board_searches(candidate_id, board_key=board_key or None)
    return jsonify([_serialize_board_search(r) for r in rows])


@boards_bp.route("/searches", methods=["POST"])
@require_auth
def create_search():
    body = request.get_json(silent=True) or {}
    if _reject_credentials(body):
        return jsonify({"error": "board credentials not supported"}), 400
    if "enabled" in body:
        return (
            jsonify({"error": "field 'enabled' removed — send 'state': ACTIVE | INACTIVE (default ACTIVE)"}),
            400,
        )
    for field in ("candidate_id", "board_key", "label"):
        if field not in body:
            return jsonify({"error": f"{field} required"}), 400
    mode_raw = body.get("mode") or "criteria"
    mode = mode_raw.strip() if isinstance(mode_raw, str) else str(mode_raw)
    state_payload = body.get("state")

    criteria_payload = None
    deeplink_payload = None
    if mode == "deeplink":
        if "criteria" in body:
            return jsonify({"error": "mutually_exclusive fields"}), 400
        url = body.get("deeplink_url")
        if not url or str(url).strip() == "":
            return jsonify({"error": "deeplink_url required when mode is deeplink"}), 400
        deeplink_payload = url
        criteria_payload = {}
    else:
        dv = body.get("deeplink_url")
        if dv is not None and str(dv).strip() != "":
            return jsonify({"error": "mutually_exclusive fields"}), 400
        if "criteria" not in body:
            return jsonify({"error": "criteria required unless mode is deeplink"}), 400
        criteria_payload = body["criteria"]

    try:
        row = save_board_search(
            body["candidate_id"],
            body["board_key"],
            body["label"],
            criteria_payload,
            state=state_payload,
            search_mode=mode,
            deeplink_url=deeplink_payload,
        )
    except DuplicateBoardSearchError:
        return jsonify({"error": "duplicate board search"}), 409
    except DeeplinkDomainMismatchError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(_serialize_board_search(row)), 201


@boards_bp.route("/searches/<board_search_id>", methods=["GET"])
@require_auth
def get_search(board_search_id):
    row = get_board_search(board_search_id)
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(_serialize_board_search(row))


@boards_bp.route("/searches/<board_search_id>", methods=["PATCH"])
@require_auth
def patch_search(board_search_id):
    body = request.get_json(silent=True) or {}
    if not body:
        return jsonify({"error": "body required"}), 400
    if _reject_credentials(body):
        return jsonify({"error": "board credentials not supported"}), 400
    if "enabled" in body:
        return (
            jsonify({"error": "field 'enabled' removed — PATCH 'state' (ACTIVE | INACTIVE; ERROR clears via ACTIVE)"}),
            400,
        )

    kw: dict = {
        "label": _PATCH_UNSET,
        "state": _PATCH_UNSET,
        "mode": _PATCH_UNSET,
        "criteria": _PATCH_UNSET,
        "deeplink_url": _PATCH_UNSET,
    }
    if "label" in body:
        kw["label"] = body["label"]
    if "state" in body:
        st = body["state"]
        kw["state"] = st.strip() if isinstance(st, str) else str(st)
    if "mode" in body:
        mr = body["mode"]
        kw["mode"] = mr.strip() if isinstance(mr, str) else str(mr)
    if "criteria" in body:
        kw["criteria"] = body["criteria"]
    if "deeplink_url" in body:
        kw["deeplink_url"] = body["deeplink_url"]

    try:
        row = update_board_search(
            board_search_id,
            label=kw["label"],
            state=kw["state"],
            mode=kw["mode"],
            criteria=kw["criteria"],
            deeplink_url=kw["deeplink_url"],
        )
    except DuplicateBoardSearchError:
        return jsonify({"error": "duplicate board search"}), 409
    except DeeplinkDomainMismatchError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        msg = str(e)
        if msg == "mutually_exclusive":
            return jsonify({"error": "mutually_exclusive fields"}), 400
        return jsonify({"error": msg}), 400
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(_serialize_board_search(row))


@boards_bp.route("/searches/<board_search_id>", methods=["DELETE"])
@require_auth
def remove_search(board_search_id):
    if not delete_board_search(board_search_id):
        return jsonify({"error": "Not found"}), 404
    return jsonify({"deleted": board_search_id})


@boards_bp.route("/searches/<board_search_id>/generate/<task_key>", methods=["POST"])
@require_auth
def generate_search(board_search_id, task_key):
    if task_key not in _BOARD_SEARCH_TASK_KEYS:
        return jsonify({"error": f"Unknown board search task: {task_key}"}), 400
    body, status = run_board_search_generation(
        board_search_id, task_key, None, debug=ui_llm_debug()
    )
    return jsonify(body), status


@boards_bp.route("")
@require_auth
def list_view():
    """List adopted boards (adopted:true keys only)."""
    return jsonify(list_adopted_boards())


@boards_bp.route("/<board_key>")
@require_auth
def detail(board_key: str):
    """Full config for one adopted board."""
    entry = get_board_entry(board_key)
    if entry is None:
        return jsonify({"error": "not found"}), 404
    return jsonify({"board_key": board_key, **entry})
