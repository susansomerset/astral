"""Meteorite job-create API (AST-1042 / Support meteorite jobs).

Thin Flask wrapper over src.core.meteorite.create_meteorite_job.
No admin UI; no email ingest; no Gmail I/O.
"""

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.meteorite import create_meteorite_job
from src.utils.logging import get_logger

logger = get_logger(__name__)

meteorite_bp = Blueprint("meteorite", __name__, url_prefix="/api")


@meteorite_bp.route("/candidates/<candidate_id>/meteorite/jobs", methods=["POST"])
@require_auth
def meteorite_create_job(candidate_id: str):
    data = request.get_json(silent=True) or {}
    html_body = data.get("html_body")
    debug = bool(data.get("debug", False))
    try:
        payload = create_meteorite_job(candidate_id, html_body, debug=debug)
    except ValueError as e:
        msg = str(e)
        if msg.startswith("candidate not found"):
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except Exception as e:
        logger.warning("[api_meteorite] create failed candidate_id=%s: %s", candidate_id, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(
        {
            "astral_job_id": payload["astral_job_id"],
            "company": payload["company"],
            "state": payload["state"],
            "latest_score": payload["latest_score"],
            "company_inserted": payload["company_inserted"],
        }
    ), 201
