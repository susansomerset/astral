"""Slack Events API + Web API helpers (external layer only).

Production: signature verify, URL challenge parse, chat.postMessage, users.info,
workspace poster pool (``list_workspace_posters``), workspace members
(``list_workspace_members`` for Manage Candidates bind).
Local/dev only: Socket Mode websocket helper (scripts/slack_socket_mode_dev.py).

Secrets from ``os.environ[CONTACT_CONFIG[…_env]]`` at **call time** (strict) —
never at import, so missing Slack env does not break unrelated processes.
No ``logger.info`` outcome lines here (callers / Style D). Use ``logger.debug``
at loop joints; fatal Slack/transport failures raise for the caller to handle.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Callable, Dict, List, Optional, Set

import requests

from src.utils.config import CONTACT_CONFIG
from src.utils.integration_io import require_controlled_external_io
from src.utils.logging import get_logger

_SLACK_API = "https://slack.com/api"
_SIGNATURE_MAX_SKEW_SEC = 60
_POST_TIMEOUT_SEC = 30
_PAGE_LIMIT = 200
# Per-channel history/replies: soft-skip these ok:false errors and continue.
_SOFT_SKIP_ERRORS = frozenset(
    {
        "channel_not_found",
        "not_in_channel",
        "missing_scope",
        "is_archived",
        "method_not_supported_for_channel",
    }
)

logger = get_logger(__name__)

__all__ = [
    "verify_slack_signature",
    "parse_url_verification",
    "post_message",
    "fetch_conversation_history",
    "fetch_user_profile",
    "list_workspace_posters",
    "list_workspace_members",
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


def fetch_conversation_history(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    limit: int,
) -> list[dict]:
    """Fetch recent messages from Slack (SoT). Raise on HTTP/transport / ok:false."""
    require_controlled_external_io("slack.fetch_conversation_history")
    token = os.environ[CONTACT_CONFIG["bot_token_env"]]
    params: Dict[str, Any] = {"channel": channel, "limit": int(limit)}
    if thread_ts:
        # Thread replies — ts is the parent message timestamp.
        method = "conversations.replies"
        params["ts"] = thread_ts
    else:
        method = "conversations.history"
    resp = requests.get(
        f"{_SLACK_API}/{method}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=_POST_TIMEOUT_SEC,
    )
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("ok"):
        raise RuntimeError(f"{method} failed: {payload.get('error')}")
    messages = payload.get("messages") or []
    if not isinstance(messages, list):
        return []
    return [m for m in messages if isinstance(m, dict)]


def fetch_user_profile(user_id: str) -> dict:
    """GET users.info; return a small profile dict. Call-time bot token. No logging."""
    require_controlled_external_io("slack.fetch_user_profile")
    sid = (user_id or "").strip()
    if not sid:
        raise ValueError("user_id is required")
    token = os.environ[CONTACT_CONFIG["bot_token_env"]]
    resp = requests.get(
        f"{_SLACK_API}/users.info",
        headers={"Authorization": f"Bearer {token}"},
        params={"user": sid},
        timeout=_POST_TIMEOUT_SEC,
    )
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("ok"):
        raise RuntimeError(f"users.info failed: {payload.get('error')}")
    user = payload.get("user") or {}
    if not isinstance(user, dict):
        user = {}
    profile = user.get("profile") or {}
    if not isinstance(profile, dict):
        profile = {}
    first = str(profile.get("first_name") or "").strip()
    last = str(profile.get("last_name") or "").strip()
    display = str(
        profile.get("display_name") or profile.get("real_name") or ""
    ).strip()
    # Slack workspace username/handle (not display name).
    username = str(user.get("name") or "").strip()
    return {
        "slack_user_id": sid,
        "first": first,
        "last": last,
        "display_name": display,
        "username": username,
    }


def _slack_bot_get(method: str, params: Dict[str, Any]) -> dict:
    """GET a Slack Web API method with the bot token. Caller checks ``ok``."""
    token = os.environ[CONTACT_CONFIG["bot_token_env"]]
    resp = requests.get(
        f"{_SLACK_API}/{method}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=_POST_TIMEOUT_SEC,
    )
    resp.raise_for_status()
    payload = resp.json()
    return payload if isinstance(payload, dict) else {}


def _iter_conversations() -> List[str]:
    """Paginate conversations.list; return channel ids the bot can see."""
    channel_ids: List[str] = []
    cursor = ""
    logger.debug("Beginning conversations.list loop on unknown items")
    while True:
        params: Dict[str, Any] = {
            "types": "public_channel,private_channel,im,mpim",
            "exclude_archived": True,
            "limit": _PAGE_LIMIT,
        }
        if cursor:
            params["cursor"] = cursor
        payload = _slack_bot_get("conversations.list", params)
        if not payload.get("ok"):
            raise RuntimeError(f"conversations.list failed: {payload.get('error')}")
        channels = payload.get("channels") or []
        if isinstance(channels, list):
            for ch in channels:
                if isinstance(ch, dict):
                    cid = ch.get("id")
                    if isinstance(cid, str) and cid.strip():
                        channel_ids.append(cid.strip())
        meta = payload.get("response_metadata") or {}
        cursor = str(meta.get("next_cursor") or "").strip() if isinstance(meta, dict) else ""
        if not cursor:
            break
    logger.debug("End conversations.list loop after %s items", len(channel_ids))
    return channel_ids


def _collect_user_ids_from_messages(messages: list) -> Set[str]:
    """Collect non-empty message ``user`` strings (skip bot-only shapes)."""
    out: Set[str] = set()
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        user = msg.get("user")
        if isinstance(user, str) and user.strip():
            out.add(user.strip())
    return out


def _paginate_messages(
    method: str,
    base_params: Dict[str, Any],
    *,
    soft_skip: bool,
) -> Optional[List[dict]]:
    """Paginate history/replies. Soft-skip → None; hard ok:false → raise."""
    all_msgs: List[dict] = []
    cursor = ""
    while True:
        params = dict(base_params)
        if cursor:
            params["cursor"] = cursor
        payload = _slack_bot_get(method, params)
        if not payload.get("ok"):
            err = str(payload.get("error") or "")
            if soft_skip and err in _SOFT_SKIP_ERRORS:
                logger.debug(
                    "Soft-skip %s channel=%s error=%s",
                    method,
                    base_params.get("channel"),
                    err,
                )
                return None
            raise RuntimeError(f"{method} failed: {payload.get('error')}")
        messages = payload.get("messages") or []
        if isinstance(messages, list):
            all_msgs.extend(m for m in messages if isinstance(m, dict))
        meta = payload.get("response_metadata") or {}
        cursor = str(meta.get("next_cursor") or "").strip() if isinstance(meta, dict) else ""
        if not cursor:
            break
    return all_msgs


def _collect_poster_ids_for_channel(channel_id: str) -> Set[str]:
    """Union message authors from history (+ thread replies) for one channel."""
    poster_ids: Set[str] = set()
    logger.debug("Beginning channel poster scan for %s", channel_id)
    history = _paginate_messages(
        "conversations.history",
        {"channel": channel_id, "limit": _PAGE_LIMIT},
        soft_skip=True,
    )
    if history is None:
        logger.debug("End channel poster scan for %s after soft-skip (0 ids)", channel_id)
        return poster_ids
    poster_ids |= _collect_user_ids_from_messages(history)
    for msg in history:
        reply_count = msg.get("reply_count")
        ts = msg.get("ts")
        if not isinstance(reply_count, int) or reply_count <= 0:
            continue
        if not isinstance(ts, str) or not ts.strip():
            continue
        replies = _paginate_messages(
            "conversations.replies",
            {"channel": channel_id, "ts": ts.strip(), "limit": _PAGE_LIMIT},
            soft_skip=True,
        )
        if replies is None:
            continue
        poster_ids |= _collect_user_ids_from_messages(replies)
    logger.debug(
        "End channel poster scan for %s after %s ids",
        channel_id,
        len(poster_ids),
    )
    return poster_ids


def _enrich_posters(poster_ids: Set[str]) -> List[dict]:
    """Intersect poster ids with users.list; drop bots/deleted; sort for UI."""
    logger.debug("Beginning users.list enrich loop on %s poster ids", len(poster_ids))
    rows: List[dict] = []
    if not poster_ids:
        logger.debug("End users.list enrich loop after 0 items")
        return rows
    cursor = ""
    while True:
        params: Dict[str, Any] = {"limit": _PAGE_LIMIT}
        if cursor:
            params["cursor"] = cursor
        payload = _slack_bot_get("users.list", params)
        if not payload.get("ok"):
            raise RuntimeError(f"users.list failed: {payload.get('error')}")
        members = payload.get("members") or []
        if isinstance(members, list):
            for user in members:
                if not isinstance(user, dict):
                    continue
                uid = user.get("id")
                if not isinstance(uid, str) or uid not in poster_ids:
                    continue
                if user.get("is_bot") or user.get("deleted"):
                    continue
                rows.append(
                    {
                        "slack_user_id": uid,
                        "username": str(user.get("name") or "").strip(),
                    }
                )
        meta = payload.get("response_metadata") or {}
        cursor = str(meta.get("next_cursor") or "").strip() if isinstance(meta, dict) else ""
        if not cursor:
            break
    rows.sort(key=lambda r: (str(r.get("username") or "").lower(), str(r.get("slack_user_id") or "")))
    logger.debug("End users.list enrich loop after %s items", len(rows))
    return rows


def list_workspace_posters() -> list[dict]:
    """Return unique human workspace posters (slack_user_id + username).

    Pool = authors of messages the bot can read across conversations.list,
    not conversations.members and not users.list alone. Bots/deleted omitted.
    """
    require_controlled_external_io("slack.list_workspace_posters")
    logger.debug("Calling list_workspace_posters: []")
    channel_ids = _iter_conversations()
    poster_ids: Set[str] = set()
    logger.debug("Beginning channel poster scan loop on %s items", len(channel_ids))
    for channel_id in channel_ids:
        poster_ids |= _collect_poster_ids_for_channel(channel_id)
    logger.debug("End channel poster scan loop after %s items", len(channel_ids))
    logger.debug("Calling _enrich_posters: poster_ids=%s", len(poster_ids))
    out = _enrich_posters(poster_ids)
    logger.debug("Response from _enrich_posters: %s", out)
    # Full payload on outer response (Joan validate note on debug callee-out).
    logger.debug("Response from list_workspace_posters: %s", out)
    return out


def list_workspace_members() -> list[dict]:
    """Return unique human workspace members/guests (slack_user_id + username).

    Pool = paginated users.list humans (not is_bot / not deleted). Used for
    Manage Candidates bind (AST-1738); not the poster-derived set.
    """
    require_controlled_external_io("slack.list_workspace_members")
    logger.debug("Calling list_workspace_members: []")
    rows: List[dict] = []
    cursor = ""
    logger.debug("Beginning users.list members loop on unknown items")
    while True:
        params: Dict[str, Any] = {"limit": _PAGE_LIMIT}
        if cursor:
            params["cursor"] = cursor
        payload = _slack_bot_get("users.list", params)
        if not payload.get("ok"):
            raise RuntimeError(f"users.list failed: {payload.get('error')}")
        members = payload.get("members") or []
        if isinstance(members, list):
            for user in members:
                if not isinstance(user, dict):
                    continue
                if user.get("is_bot") or user.get("deleted"):
                    continue
                uid = user.get("id")
                if not isinstance(uid, str) or not uid.strip():
                    continue
                rows.append(
                    {
                        "slack_user_id": uid.strip(),
                        "username": str(user.get("name") or "").strip(),
                    }
                )
        meta = payload.get("response_metadata") or {}
        cursor = str(meta.get("next_cursor") or "").strip() if isinstance(meta, dict) else ""
        if not cursor:
            break
    rows.sort(
        key=lambda r: (str(r.get("username") or "").lower(), str(r.get("slack_user_id") or ""))
    )
    logger.debug("End users.list members loop after %s items", len(rows))
    logger.debug("Response from list_workspace_members: %s", rows)
    return rows


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
