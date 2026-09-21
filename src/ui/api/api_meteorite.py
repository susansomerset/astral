"""Meteorite listing intake API (AST-1471).

Thin Flask wrapper over src.core.meteorite.land_meteorite.
No admin UI; no email ingest; no Gmail I/O.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.meteorite import land_meteorite
from src.utils.config import METEORITE_CONFIG
from src.utils.logging import get_logger

logger = get_logger(__name__)

meteorite_bp = Blueprint("meteorite", __name__, url_prefix="/api")


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
