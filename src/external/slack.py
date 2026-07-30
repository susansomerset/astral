"""Slack Events API + Web API helpers (external layer only).

Production: signature verify, URL challenge parse, chat.postMessage.
Local/dev only: Socket Mode websocket helper (scripts/slack_socket_mode_dev.py).

Secrets from ``os.environ[CONTACT_CONFIG[…_env]]`` at **call time** (strict) —
never at import, so missing Slack env does not break unrelated processes.
No outcome logging here (callers / Style D).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Callable, Dict, Optional

import requests

from src.utils.config import CONTACT_CONFIG
from src.utils.integration_io import require_controlled_external_io

_SLACK_API = "https://slack.com/api"
_SIGNATURE_MAX_SKEW_SEC = 60
_POST_TIMEOUT_SEC = 30

__all__ = [
    "verify_slack_signature",
    "parse_url_verification",
    "post_message",
    "open_socket_mode_connection",
]


def verify_slack_signature(
    *,
    signing_secret: str,
    timestamp: str,
    body: bytes,
    signature: str,
) -> bool:
    """Slack v0 HMAC-SHA256 over ``v0:{timestamp}:{body}``; reject stale timestamps."""
    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False
    if abs(time.time() - ts) > _SIGNATURE_MAX_SKEW_SEC:
        return False
    basestring = f"v0:{timestamp}:".encode("utf-8") + body
    expected = "v0=" + hmac.new(
        signing_secret.encode("utf-8"),
        basestring,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")


def parse_url_verification(payload: dict) -> Optional[str]:
    """Return challenge string when payload is URL verification; else None."""
    if not isinstance(payload, dict):
        return None
    if payload.get("type") != "url_verification":
        return None
    challenge = payload.get("challenge")
    return challenge if isinstance(challenge, str) else None


def post_message(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
) -> dict:
    """POST chat.postMessage; raise on HTTP/transport failure. Does not log."""
    require_controlled_external_io("slack.post_message")
    token = os.environ[CONTACT_CONFIG["bot_token_env"]]
    body: Dict[str, Any] = {"channel": channel, "text": text}
    if thread_ts:
        body["thread_ts"] = thread_ts
    resp = requests.post(
        f"{_SLACK_API}/chat.postMessage",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json=body,
        timeout=_POST_TIMEOUT_SEC,
    )
    resp.raise_for_status()
    return resp.json()


def open_socket_mode_connection(handler: Callable[[dict], None]) -> None:
    """Local/dev Socket Mode loop — apps.connections.open + websocket.

    Invokes ``handler(payload_dict)`` with the Events API-shaped envelope payload
    (``payload`` field of ``events_api`` frames). Must not be imported by UI.
    """
    # websocket-client is a Stage 5 dep — import here so production UI path
    # never needs the package at import time of this module.
    from websocket import WebSocketApp  # type: ignore[import-untyped]

    require_controlled_external_io("slack.open_socket_mode_connection")
    app_token = os.environ[CONTACT_CONFIG["app_token_env"]]
    # Bot token required for Socket Mode apps; fail fast if missing.
    _ = os.environ[CONTACT_CONFIG["bot_token_env"]]

    open_resp = requests.post(
        f"{_SLACK_API}/apps.connections.open",
        headers={"Authorization": f"Bearer {app_token}"},
        timeout=_POST_TIMEOUT_SEC,
    )
    open_resp.raise_for_status()
    open_json = open_resp.json()
    if not open_json.get("ok"):
        raise RuntimeError(f"apps.connections.open failed: {open_json.get('error')}")
    ws_url = open_json["url"]

    def _on_message(ws: Any, message: str) -> None:
        try:
            frame = json.loads(message)
        except json.JSONDecodeError:
            return
        envelope_id = frame.get("envelope_id")
        if envelope_id:
            # Ack within Slack's Socket Mode window before handler work.
            ws.send(json.dumps({"envelope_id": envelope_id}))
        if frame.get("type") != "events_api":
            return
        payload = frame.get("payload")
        if isinstance(payload, dict):
            handler(payload)

    ws_app = WebSocketApp(ws_url, on_message=_on_message)
    # Blocks until disconnect — local/dev script owns the process lifetime.
    ws_app.run_forever()
