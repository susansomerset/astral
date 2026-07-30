"""Candidate intake session REST API (AST-558). Katherine UI (AST-559) consumes these routes."""

from __future__ import annotations

import asyncio
import json

from flask import Blueprint, jsonify, request

from src.core.candidate import get_candidate
from src.core.intake import (
    create_intake_session_and_start,
    fetch_active_intake_session,
    fetch_intake_session,
    generate_topic_menu_from_preamble,
    get_intake_session_dto,
    post_intake_build,
    post_intake_turn,
    run_topic_menu_preamble_confirm,
    validate_preamble_answer,
)
from src.utils.deploy_status import ui_llm_debug
from ui.auth import require_auth

intake_bp = Blueprint("intake", __name__, url_prefix="/api/candidates")


def _debug_flag() -> bool:
    explicit = request.args.get("debug", "").lower() in ("1", "true", "yes")
    return ui_llm_debug(explicit_debug=explicit)


def _runtime_error_response(exc: RuntimeError):
    try:
        payload = json.loads(str(exc))
    except (TypeError, ValueError, json.JSONDecodeError):
        payload = {"error": str(exc)}
    body = {"error": payload.get("error", "intake task failed")}
    if payload.get("batch_id"):
        body["batch_id"] = payload["batch_id"]
    return jsonify(body), 500


@intake_bp.route("/<candidate_id>/intake/sessions", methods=["POST"])
@require_auth
def create_session(candidate_id):
    candidate = get_candidate(candidate_id)
    if not candidate:
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    body = request.get_json(silent=True) or {}
    try:
        dto = asyncio.run(
            create_intake_session_and_start(
                candidate_id,
                body.get("starting_resume_text") or "",
                sample_cover_text=body.get("sample_cover_text"),
                linkedin_profile_text=body.get("linkedin_profile_text"),
                debug=_debug_flag(),
            )
        )
    except ValueError as e:
        if str(e) == "active intake session already exists for candidate":
            return jsonify({"error": str(e)}), 409
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return _runtime_error_response(e)
    return jsonify(dto), 201


@intake_bp.route("/<candidate_id>/intake/sessions/<session_id>", methods=["GET"])
@require_auth
def get_session(candidate_id, session_id):
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    row = fetch_intake_session(session_id)
    if not row or row.get("candidate_id") != candidate_id:
        return jsonify({"error": "intake session not found"}), 404
    return jsonify(get_intake_session_dto(row))


@intake_bp.route("/<candidate_id>/intake/sessions/active", methods=["GET"])
@require_auth
def get_active_session(candidate_id):
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    row = fetch_active_intake_session(candidate_id)
    if not row:
        return jsonify({"error": "no active intake session"}), 404
    return jsonify(get_intake_session_dto(row))


@intake_bp.route("/<candidate_id>/intake/sessions/<session_id>/turns", methods=["POST"])
@require_auth
def post_turn(candidate_id, session_id):
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    row = fetch_intake_session(session_id)
    if not row or row.get("candidate_id") != candidate_id:
        return jsonify({"error": "intake session not found"}), 404
    body = request.get_json(silent=True) or {}
    try:
        dto = asyncio.run(
            post_intake_turn(session_id, body.get("message") or "", debug=_debug_flag())
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return _runtime_error_response(e)
    return jsonify(dto)


@intake_bp.route("/<candidate_id>/intake/sessions/<session_id>/build", methods=["POST"])
@require_auth
def post_build(candidate_id, session_id):
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    row = fetch_intake_session(session_id)
    if not row or row.get("candidate_id") != candidate_id:
        return jsonify({"error": "intake session not found"}), 404
    try:
        dto = asyncio.run(post_intake_build(session_id, debug=_debug_flag()))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return _runtime_error_response(e)
    return jsonify(dto)


@intake_bp.route("/<candidate_id>/preamble/validate", methods=["POST"])
@require_auth
def post_preamble_validate(candidate_id):
    """Ruth Valid / Try Again / Escalate for one preamble answer (AST-1015). No library writes."""
    body = request.get_json(silent=True) or {}
    question = body.get("question")
    answer = body.get("answer", "")
    step_index = body.get("step_index", 1)
    step_total = body.get("step_total", 1)
    try:
        step_index = int(step_index)
        step_total = int(step_total)
    except (TypeError, ValueError):
        return jsonify({"error": "step_index and step_total must be integers"}), 400
    try:
        result = asyncio.run(
            validate_preamble_answer(
                candidate_id,
                question,
                answer,
                step_index=step_index,
                step_total=step_total,
                debug=_debug_flag(),
            )
        )
    except ValueError as e:
        msg = str(e)
        if msg.startswith("Candidate not found"):
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({k: result[k] for k in ("success", "outcome", "error", "batch_id")}), 200


@intake_bp.route("/<candidate_id>/topic-menu/confirm", methods=["POST"])
@require_auth
def post_topic_menu_confirm(candidate_id):
    """Estelle preamble confirm turn (AST-1075)."""
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    body = request.get_json(silent=True) or {}
    message = body.get("message")
    try:
        result = asyncio.run(
            run_topic_menu_preamble_confirm(
                candidate_id,
                candidate_message=message if isinstance(message, str) else None,
                debug=_debug_flag(),
            )
        )
    except ValueError as e:
        msg = str(e)
        if msg.startswith("Candidate not found"):
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if not result.get("success"):
        body_out = {"error": result.get("error") or "confirm failed"}
        if result.get("batch_id"):
            body_out["batch_id"] = result["batch_id"]
        return jsonify(body_out), 500
    return jsonify(
        {
            k: result[k]
            for k in (
                "success",
                "outcome",
                "assistant_message",
                "applied_patches",
                "packet",
                "batch_id",
                "error",
            )
        }
    ), 200


@intake_bp.route("/<candidate_id>/topic-menu/generate", methods=["POST"])
@require_auth
def post_topic_menu_generate(candidate_id):
    """Estelle Topic Menu generation after preamble confirm (AST-1075)."""
    if not get_candidate(candidate_id):
        return jsonify({"error": f"Candidate not found: {candidate_id}"}), 404
    try:
        result = asyncio.run(
            generate_topic_menu_from_preamble(candidate_id, debug=_debug_flag())
        )
    except ValueError as e:
        msg = str(e)
        if msg.startswith("Candidate not found"):
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if not result.get("success"):
        body_out = {"error": result.get("error") or "generate failed"}
        if result.get("batch_id"):
            body_out["batch_id"] = result["batch_id"]
        if "rejected_topic_count" in result:
            body_out["rejected_topic_count"] = result["rejected_topic_count"]
        return jsonify(body_out), 500
    return jsonify(
        {
            k: result[k]
            for k in (
                "success",
                "menu",
                "batch_id",
                "rejected_topic_count",
                "informs_covered",
                "error",
            )
        }
    ), 200

