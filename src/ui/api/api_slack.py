"""Slack Events API webhook (AST-1069).

Transport only: raw body + Slack signature headers → Contact core.
No ``src.external`` imports; signing verify lives in Contact.
AST-1207: durable Contact debug SoT via ``slack_debug_enabled`` (not ui_llm_debug).
"""

from flask import Blueprint, jsonify, request

from src.core.contact import receive_slack_events_http, slack_debug_enabled
from src.utils.config import CONTACT_CONFIG

slack_bp = Blueprint("slack", __name__, url_prefix="/api")


@slack_bp.route(CONTACT_CONFIG["events_http_path"], methods=["POST"])
def slack_events():
    # Slack cannot send Astral Bearer tokens — signature verify in Contact is auth.
    raw_body = request.get_data()
    status, body = receive_slack_events_http(
        raw_body,
        timestamp=request.headers.get("X-Slack-Request-Timestamp") or "",
        signature=request.headers.get("X-Slack-Signature") or "",
        debug=slack_debug_enabled(),
    )
    if isinstance(body, dict):
        return jsonify(body), status
    return body, status
