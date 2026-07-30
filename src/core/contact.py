"""
Contact: Slack foundation + CONTACT_CONFIG skills ACL (Astral Contact / AST-1066).

AST-1069: Events HTTP ingress (`receive_slack_events_http`) + inbound routing
(`handle_slack_event`). Siblings: Manage Slack listen UI (AST-1067),
resolve/PROSPECT (AST-1068), conversation context (AST-1070), skill runners (AST-1071).
Estelle conversational turn loop lives on AST-1046 — not here.
"""

from __future__ import annotations

import json
import os
import threading
from collections import OrderedDict
from typing import Any, Dict, Tuple

from src.external.slack import parse_url_verification, verify_slack_signature
from src.utils.config import CONTACT_CONFIG
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Process-local event_id dedupe (single gunicorn worker). OrderedDict as ring.
_seen_event_ids: "OrderedDict[str, None]" = OrderedDict()
_seen_lock = threading.Lock()

_TEXT_DEBUG_MAX = 200


def slack_listen_enabled() -> bool:
    """Return CONTACT_CONFIG listen flag (default False until Manage Slack flips it)."""
    return bool(CONTACT_CONFIG["listen_enabled"])


def contact_skills() -> Dict[str, Any]:
    """Shallow copy of CONTACT_CONFIG['skills'] ACL map (empty until AST-1071)."""
    return dict(CONTACT_CONFIG["skills"])


def contact_skill_keys() -> Tuple[str, ...]:
    """Ordered tuple of allowlisted Contact skill keys."""
    return tuple(CONTACT_CONFIG["skills"].keys())


def slack_env_names() -> Dict[str, str]:
    """Map logical secret → environ variable name (values never returned)."""
    return {
        "bot_token": str(CONTACT_CONFIG["bot_token_env"]),
        "signing_secret": str(CONTACT_CONFIG["signing_secret_env"]),
    }


def non_production_reply_prefix(environment: str) -> str:
    """Format CONTACT_CONFIG non-production reply prefix (AST-1067 applies when listen on)."""
    env = (environment or "").strip()
    return str(CONTACT_CONFIG["non_production_reply_prefix_template"]).format(
        environment=env
    )


def _remember_event_id(event_id: str) -> bool:
    """Return True if event_id is new; False if duplicate. Cap by event_id_dedupe_max."""
    max_n = int(CONTACT_CONFIG["event_id_dedupe_max"])
    with _seen_lock:
        if event_id in _seen_event_ids:
            return False
        _seen_event_ids[event_id] = None
        while len(_seen_event_ids) > max_n:
            _seen_event_ids.popitem(last=False)
        return True


def _is_dm_message(event: dict) -> bool:
    # Prefer channel_type when Slack sends it; else DM channels are D… ids.
    channel_type = event.get("channel_type")
    if channel_type is not None:
        return channel_type == "im"
    channel = event.get("channel") or ""
    return isinstance(channel, str) and channel.startswith("D")


def handle_slack_event(payload: dict, *, debug: bool = False) -> dict:
    """Route one Slack Events API payload into Contact (listen-gated)."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    if not slack_listen_enabled():
        if debug:
            log.debug_index(
                func="contact.handle_slack_event",
                index=1,
                total=1,
                identifier="listen",
                outcome="listen_off",
            )
            log.debug_detail("accepted=False reason=listen_off")
        return {"accepted": False, "reason": "listen_off"}

    event_id = payload.get("event_id") if isinstance(payload, dict) else None
    if not event_id or not isinstance(event_id, str):
        if debug:
            log.debug_index(
                func="contact.handle_slack_event",
                index=1,
                total=1,
                identifier="event_id",
                outcome="missing_event_id",
            )
            log.debug_detail("accepted=False reason=missing_event_id")
        return {"accepted": False, "reason": "missing_event_id"}

    if not _remember_event_id(event_id):
        if debug:
            log.debug_index(
                func="contact.handle_slack_event",
                index=1,
                total=1,
                identifier=event_id,
                outcome="duplicate_event",
            )
            log.debug_detail("accepted=False reason=duplicate_event")
        return {"accepted": False, "reason": "duplicate_event"}

    event = payload.get("event") or {}
    if not isinstance(event, dict):
        event = {}
    etype = event.get("type")
    if etype not in CONTACT_CONFIG["bot_event_types"]:
        if debug:
            log.debug_index(
                func="contact.handle_slack_event",
                index=1,
                total=1,
                identifier=event_id,
                outcome="type_skipped",
            )
            log.debug_detail(f"accepted=False reason=type_skipped etype={etype!r}")
        return {"accepted": False, "reason": "type_skipped"}

    if etype == "message":
        # Ignore bot echoes / edits / subtypes; only human DM text.
        if event.get("subtype") or event.get("bot_id"):
            if debug:
                log.debug_index(
                    func="contact.handle_slack_event",
                    index=1,
                    total=1,
                    identifier=event_id,
                    outcome="message_skipped",
                )
                log.debug_detail("accepted=False reason=message_skipped")
            return {"accepted": False, "reason": "message_skipped"}
        if not _is_dm_message(event):
            if debug:
                log.debug_index(
                    func="contact.handle_slack_event",
                    index=1,
                    total=1,
                    identifier=event_id,
                    outcome="not_dm",
                )
                log.debug_detail("accepted=False reason=not_dm")
            return {"accepted": False, "reason": "not_dm"}
    # app_mention: accept as channel @Estelle

    text = event.get("text") or ""
    if not isinstance(text, str):
        text = ""
    result = {
        "accepted": True,
        "event_id": event_id,
        "event_type": etype,
        "user": event.get("user"),
        "channel": event.get("channel"),
        "ts": event.get("ts"),
        "thread_ts": event.get("thread_ts"),
        "text": text,
    }
    if debug:
        preview = text if len(text) <= _TEXT_DEBUG_MAX else text[:_TEXT_DEBUG_MAX] + "…"
        log.debug_index(
            func="contact.handle_slack_event",
            index=1,
            total=1,
            identifier=event_id,
            outcome="accepted",
        )
        log.debug_detail(
            f"accepted=True event_type={etype!r} user={event.get('user')!r} "
            f"channel={event.get('channel')!r} text={preview!r}"
        )
    return result


def receive_slack_events_http(
    raw_body: bytes,
    *,
    timestamp: str,
    signature: str,
    debug: bool = False,
) -> tuple[int, object]:
    """Verify Slack signature, answer URL challenge, or accept an event payload.

    Returns (status_code, body) where body is ``dict`` (JSON), ``bytes``, or ``str``.
    """
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    signing_secret = os.environ[CONTACT_CONFIG["signing_secret_env"]]
    if not verify_slack_signature(
        signing_secret=signing_secret,
        timestamp=timestamp or "",
        body=raw_body,
        signature=signature or "",
    ):
        if debug:
            log.debug_index(
                func="contact.receive_slack_events_http",
                index=1,
                total=1,
                identifier="signature",
                outcome="unauthorized",
            )
            log.debug_detail("status=401 reason=bad_signature")
        return (401, "")

    try:
        payload = json.loads(raw_body.decode("utf-8") if isinstance(raw_body, bytes) else raw_body)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
        if debug:
            log.debug_index(
                func="contact.receive_slack_events_http",
                index=1,
                total=1,
                identifier="body",
                outcome="bad_json",
            )
            log.debug_detail("status=400 reason=bad_json")
        return (400, "")

    if not isinstance(payload, dict):
        return (400, "")

    challenge = parse_url_verification(payload)
    if challenge is not None:
        if debug:
            log.debug_index(
                func="contact.receive_slack_events_http",
                index=1,
                total=1,
                identifier="url_verification",
                outcome="challenge",
            )
            log.debug_detail("status=200 reason=url_verification")
        return (200, {"challenge": challenge})

    # Ack immediately; process off the request thread (Slack ~3s window).
    threading.Thread(
        target=handle_slack_event,
        args=(payload,),
        kwargs={"debug": debug},
        daemon=True,
    ).start()
    if debug:
        log.debug_index(
            func="contact.receive_slack_events_http",
            index=1,
            total=1,
            identifier=str(payload.get("event_id") or "event"),
            outcome="acked",
        )
        log.debug_detail("status=200 reason=event_acked")
    return (200, "")
