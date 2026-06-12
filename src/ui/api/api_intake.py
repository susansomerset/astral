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
    get_intake_session_dto,
    post_intake_build,
    post_intake_turn,
)
from ui.auth import require_auth

intake_bp = Blueprint("intake", __name__, url_prefix="/api/candidates")


def _debug_flag() -> bool:
    return request.args.get("debug", "").lower() in ("1", "true", "yes")


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
