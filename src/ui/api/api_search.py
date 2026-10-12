"""Universal entity search API (AST-2173): GET /api/search?q=…&candidate_id=…"""

from flask import Blueprint, jsonify, request

from src.core.search import search_entities
from src.utils.logging import get_logger
from ui.api_errors import error_json, server_error_from_exception
from ui.auth import require_auth

search_bp = Blueprint("search", __name__, url_prefix="/api/search")
logger = get_logger(__name__)


@search_bp.route("")
@require_auth
def search():
    """Results keyed by job / company / meteorite. q is searched as sent (blank = 400).
    Idempotent read — no api info line (stat.logging.info.api)."""
    q = request.args.get("q") or ""
    candidate_id = (request.args.get("candidate_id") or "").strip()
    if not q.strip():
        return error_json("q required")
    if not candidate_id:
        return error_json("candidate_id required")
    try:
        return jsonify(search_entities(candidate_id, q))
    except Exception as exc:
        logger.exception(
            "%s | api %s failed\n  %s: %s\n  Returning 500; the search results page shows no results",
            candidate_id,
            "/api/search",
            type(exc).__name__,
            exc,
        )
        return server_error_from_exception(exc)
