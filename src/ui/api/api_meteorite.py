"""Meteorite listing intake API (AST-1471).

Thin Flask wrapper over src.core.meteorite.land_meteorite.
No admin UI; no email ingest; no Gmail I/O.
AST-1748: candidate-scoped list + detail GET for Jobs → Meteorites.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Tuple

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.meteorite import land_meteorite
from src.data.database import get_meteorite, list_meteorites_for_candidate
from src.utils.config import (
    JOBS_METEORITES_LIST_COLUMNS,
    JOBS_METEORITES_MODAL_SECTIONS,
    METEORITE_CONFIG,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)

meteorite_bp = Blueprint("meteorite", __name__, url_prefix="/api")

# List omits heavy content; detail carries full content + AC metadata.
_LIST_KEYS: Tuple[str, ...] = (
    "id", "candidate_id", "state", "job_title", "employer_name",
    "classify_outcome", "link", "astral_job_id",
    "created_at", "updated_at", "state_changed_at",
    "source_kind", "source_id",
)

_DETAIL_KEYS: Tuple[str, ...] = (
    "id", "candidate_id", "source_kind", "source_id", "source_ref",
    "state", "content", "classify_outcome", "link", "electronic_contact",
    "job_title", "employer_name", "astral_job_id", "error",
    "created_at", "updated_at", "state_changed_at", "estelle_notified_at",
)


def _project_meteorite(row: dict, keys: tuple) -> dict:
    """Field mapping only — link / astral_job_id returned as stored (no rewrite)."""
    return {k: row.get(k) for k in keys}


def _land_request_payload(data: dict) -> Dict[str, Any]:
    """Map JSON body → land_meteorite kwargs (field mapping only)."""
    debug = bool(data.get("debug", False))
    scraps_raw = data.get("scraps")
    if isinstance(scraps_raw, list) and scraps_raw:
        scraps = [s for s in scraps_raw if isinstance(s, dict)]
        if scraps:
            return {"scraps": scraps, "debug": debug}

    kwargs: Dict[str, Any] = {"debug": debug}
    text = data.get("text")
    if isinstance(text, str) and text.strip():
        kwargs["text"] = text.strip()
    job_link = data.get("job_link")
    if isinstance(job_link, str) and job_link.strip():
        kwargs["job_link"] = job_link.strip()
    employer_name = data.get("employer_name")
    if isinstance(employer_name, str) and employer_name.strip():
        kwargs["employer_name"] = employer_name.strip()

    # Legacy AST-1042: html_body → text when no scrap/text/link supplied.
    if "text" not in kwargs and "job_link" not in kwargs:
        html_body = data.get("html_body")
        if isinstance(html_body, str) and html_body.strip():
            kwargs["text"] = html_body.strip()

    return kwargs


def _land_http_response(result: dict):
    """HTTP status + JSON body matching land_meteorite outcome shape."""
    body = {
        "outcome": result.get("outcome"),
        "outcomes": result.get("outcomes") or [],
        "company": result.get("company"),
        "company_inserted": bool(result.get("company_inserted")),
        "error": result.get("error"),
    }
    outcome = result.get("outcome")
    created = METEORITE_CONFIG["land_outcome_created"]
    skip = METEORITE_CONFIG["land_outcome_duplicate_skip"]
    superseded = METEORITE_CONFIG["land_outcome_superseded"]
    err = METEORITE_CONFIG["land_outcome_error"]

    if outcome == created:
        return jsonify(body), 201
    if outcome in (skip, superseded):
        return jsonify(body), 200
    if outcome == err:
        err_msg = result.get("error") or ""
        if isinstance(err_msg, str) and err_msg.startswith("candidate not found"):
            return jsonify(body), 404
        return jsonify(body), 400
    return jsonify(body), 400


def _run_land(candidate_id: str, data: dict):
    kwargs = _land_request_payload(data)
    try:
        result = asyncio.run(land_meteorite(candidate_id, **kwargs))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_meteorite] land failed candidate_id=%s: %s", candidate_id, e)
        return jsonify({"error": str(e)}), 502
    return _land_http_response(result)


@meteorite_bp.route("/candidates/<candidate_id>/meteorites", methods=["GET"])
@require_auth
def meteorite_list_for_candidate(candidate_id: str):
    """Candidate-scoped meteorite list for Jobs → Meteorites (AST-1748)."""
    route = f"/api/candidates/{candidate_id}/meteorites"
    try:
        logger.debug(
            "Calling list_meteorites_for_candidate: [candidate_id=%s]",
            candidate_id,
        )
        rows = list_meteorites_for_candidate(candidate_id)
        logger.debug("Response from list_meteorites_for_candidate: %s", rows)
        projected = [_project_meteorite(r, _LIST_KEYS) for r in rows]
        return jsonify({
            "columns": list(JOBS_METEORITES_LIST_COLUMNS),
            "meteorites": projected,
        })
    except Exception as exc:
        logger.exception(
            "%s | api %s list failed\n  %s: %s\n  Returning 500; list not delivered",
            candidate_id or "-",
            route,
            type(exc).__name__,
            exc,
        )
        return jsonify({"error": "meteorite list failed"}), 500


@meteorite_bp.route("/meteorites/<int:meteorite_id>", methods=["GET"])
@require_auth
def meteorite_detail(meteorite_id: int):
    """Single meteorite detail for Jobs → Meteorites modal (AST-1748)."""
    route = f"/api/meteorites/{meteorite_id}"
    try:
        logger.debug("Calling get_meteorite: [meteorite_id=%s]", meteorite_id)
        row = get_meteorite(meteorite_id)
        logger.debug("Response from get_meteorite: %s", row)
        if row is None:
            return jsonify({"error": "meteorite not found"}), 404
        return jsonify({
            "sections": list(JOBS_METEORITES_MODAL_SECTIONS),
            "meteorite": _project_meteorite(row, _DETAIL_KEYS),
        })
    except Exception as exc:
        logger.exception(
            "%s | api %s detail failed\n  %s: %s\n  Returning 500; detail not delivered",
            "-",
            route,
            type(exc).__name__,
            exc,
        )
        return jsonify({"error": "meteorite detail failed"}), 500


@meteorite_bp.route("/candidates/<candidate_id>/meteorite/land", methods=["POST"])
@require_auth
def meteorite_land(candidate_id: str):
    data = request.get_json(silent=True) or {}
    return _run_land(candidate_id, data)


@meteorite_bp.route("/candidates/<candidate_id>/meteorite/jobs", methods=["POST"])
@require_auth
def meteorite_create_job(candidate_id: str):
    # Alias of /land — same outcome shape (no parallel create).
    data = request.get_json(silent=True) or {}
    return _run_land(candidate_id, data)
