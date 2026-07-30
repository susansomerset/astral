"""
Contact: Slack foundation + CONTACT_CONFIG skills ACL (Astral Contact / AST-1066).

AST-1069: Events HTTP ingress (`receive_slack_events_http`) + inbound routing
(`handle_slack_event`). AST-1071: ACL-gated entity-save skill runners.
AST-1070: Slack-sourced conversation context load / process-local cache / append.
Siblings: Manage Slack listen UI (AST-1067), resolve/PROSPECT (AST-1068).
Estelle turn loop: AST-1046 — not here.
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

from src.core.candidate import get_candidate, save_candidate_data
from src.external.slack import (
    fetch_conversation_history,
    parse_url_verification,
    post_message,
    verify_slack_signature,
)
from src.utils.config import CONTACT_CONFIG
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)

# Process-local event_id dedupe (single gunicorn worker). OrderedDict as ring.
_seen_event_ids: "OrderedDict[str, None]" = OrderedDict()
_seen_lock = threading.Lock()

# Process-local conversation cache: key → {messages, fetched_at}. LRU by access.
# Key is (channel, Slack thread_ts or "") — never message ts (would shard one DM).
_context_cache: "OrderedDict[Tuple[str, str], Dict[str, Any]]" = OrderedDict()
_context_lock = threading.Lock()

_TEXT_DEBUG_MAX = 200


def load_slack_conversation_context(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    refresh: bool = False,
    debug: bool = False,
) -> dict:
    """Return recent conversation messages for a channel or thread.

    SoT is Slack. Cache is process-local only — never a DB transcript store.
    Envelope: ``{"channel", "thread_ts", "messages", "source": "cache"|"slack"}``.
    """
    log = get_logger(__name__)
    log.set_debug_flag(debug)
    channel_n = (channel or "").strip()
    if not channel_n:
        raise ValueError("channel must be a non-empty string")
    thread_n = thread_ts or ""
    key = _context_cache_key(channel_n, thread_n)
    now = time.time()
    ttl = float(CONTACT_CONFIG["context_cache_ttl_seconds"])
    limit = int(CONTACT_CONFIG["context_history_limit"])

    if not refresh:
        with _context_lock:
            entry = _context_cache.get(key)
            if entry is not None and (now - float(entry["fetched_at"])) < ttl:
                _context_cache.move_to_end(key)
                messages = list(entry["messages"])
                out = {
                    "channel": channel_n,
                    "thread_ts": thread_n,
                    "messages": messages,
                    "source": "cache",
                }
                if debug:
                    log.debug_index(
                        func="contact.load_slack_conversation_context",
                        index=1,
                        total=1,
                        identifier=f"{channel_n}:{thread_n or '-'}",
                        outcome="cache",
                    )
                    log.debug_detail(
                        f"source=cache channel={channel_n!r} thread_ts={thread_n!r} "
                        f"len(messages)={len(messages)}"
                    )
                return out

    messages = fetch_conversation_history(
        channel=channel_n,
        thread_ts=thread_n or None,
        limit=limit,
    )
    _context_cache_put(key, {"messages": list(messages), "fetched_at": now})
    out = {
        "channel": channel_n,
        "thread_ts": thread_n,
        "messages": list(messages),
        "source": "slack",
    }
    if debug:
        log.debug_index(
            func="contact.load_slack_conversation_context",
            index=1,
            total=1,
            identifier=f"{channel_n}:{thread_n or '-'}",
            outcome="slack",
        )
        log.debug_detail(
            f"source=slack channel={channel_n!r} thread_ts={thread_n!r} "
            f"len(messages)={len(messages)} refresh={refresh}"
        )
    return out


def append_slack_conversation_message(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    message: dict,
    debug: bool = False,
) -> None:
    """Append one message into the process-local cache for that conversation key."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)
    if not isinstance(message, dict) or "text" not in message or "ts" not in message:
        raise ValueError("message must be a dict with text and ts")
    if not isinstance(message["text"], str) or not isinstance(message["ts"], str):
        raise ValueError("message text and ts must be strings")

    key = _context_cache_key(channel, thread_ts)
    limit = int(CONTACT_CONFIG["context_history_limit"])
    now = time.time()
    with _context_lock:
        entry = _context_cache.get(key)
        if entry is None:
            entry = {"messages": [dict(message)], "fetched_at": now}
        else:
            msgs = list(entry["messages"])
            msgs.append(dict(message))
            # Keep newest N (Slack history order varies; trim from the front).
            if len(msgs) > limit:
                msgs = msgs[-limit:]
            entry = {"messages": msgs, "fetched_at": entry.get("fetched_at", now)}
            del _context_cache[key]
        _context_cache[key] = entry
        max_n = int(CONTACT_CONFIG["context_cache_max_conversations"])
        while len(_context_cache) > max_n:
            _context_cache.popitem(last=False)

    if debug:
        log.debug_index(
            func="contact.append_slack_conversation_message",
            index=1,
            total=1,
            identifier=f"{key[0]}:{key[1] or '-'}",
            outcome="appended",
        )
        preview = message["text"]
        if len(preview) > _TEXT_DEBUG_MAX:
            preview = preview[:_TEXT_DEBUG_MAX] + "…"
        log.debug_detail(f"ts={message['ts']!r} text={preview!r}")


def contact_post_message(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Post via external slack.post_message, then append outbound text into cache."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)
    resp = post_message(channel=channel, text=text, thread_ts=thread_ts)
    if resp.get("ok"):
        # Prefer Slack response ts; fall back so cache still warms if shape odd.
        out_ts = resp.get("ts") or (resp.get("message") or {}).get("ts") or ""
        if not isinstance(out_ts, str):
            out_ts = str(out_ts) if out_ts else ""
        if out_ts:
            append_slack_conversation_message(
                channel=channel,
                thread_ts=thread_ts,
                message={
                    "user": "estelle",
                    "bot_id": "estelle",
                    "text": text,
                    "ts": out_ts,
                },
                debug=debug,
            )
    if debug:
        log.debug_index(
            func="contact.contact_post_message",
            index=1,
            total=1,
            identifier=channel,
            outcome="ok" if resp.get("ok") else "api_error",
        )
        log.debug_detail(f"ok={resp.get('ok')!r} error={resp.get('error')!r}")
    return resp


def _context_cache_key(channel: str, thread_ts: Optional[str]) -> Tuple[str, str]:
    """Cache key = (channel, Slack thread_ts only). Missing thread → \"\"."""
    return (channel, thread_ts or "")


def _context_cache_put(key: Tuple[str, str], entry: Dict[str, Any]) -> None:
    """Insert/refresh cache entry; evict oldest when over max conversations."""
    max_n = int(CONTACT_CONFIG["context_cache_max_conversations"])
    with _context_lock:
        if key in _context_cache:
            del _context_cache[key]
        _context_cache[key] = entry
        while len(_context_cache) > max_n:
            _context_cache.popitem(last=False)


def slack_listen_enabled() -> bool:
    """Return CONTACT_CONFIG listen flag (default False until Manage Slack flips it)."""
    return bool(CONTACT_CONFIG["listen_enabled"])


def contact_skills() -> Dict[str, Any]:
    """Shallow copy of CONTACT_CONFIG['skills'] ACL map."""
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


def contact_skill_meta(skill_key: str) -> Dict[str, Any]:
    """Return a shallow copy of one skill ACL entry, or raise ValueError if unknown."""
    key = (skill_key or "").strip()
    if key not in CONTACT_CONFIG["skills"]:
        raise ValueError(f"unknown contact skill: {key!r}")
    meta = dict(CONTACT_CONFIG["skills"][key])
    meta["allowed_paths"] = tuple(meta["allowed_paths"])
    return meta


def run_contact_skill(
    skill_key: str,
    *,
    astral_candidate_id: str,
    fields: Dict[str, Any],
    debug: bool = False,
) -> Dict[str, Any]:
    """ACL-gated entity save for Contact. Writes only allowlisted candidate_data paths."""
    if debug:
        logger.set_debug_flag(True)

    cid = (astral_candidate_id or "").strip()
    if not cid:
        raise ValueError("astral_candidate_id is required")

    key = (skill_key or "").strip()
    meta = contact_skill_meta(key)
    if meta.get("write") is not True:
        raise ValueError(f"contact skill is not a write skill: {key!r}")
    if not isinstance(fields, dict):
        raise ValueError("fields must be a dict")

    allowed = set(meta["allowed_paths"])
    for path, value in fields.items():
        if path not in allowed:
            raise ValueError(f"path not allowlisted for skill {key!r}: {path!r}")
        if value is not None and not isinstance(value, str):
            raise ValueError(f"field {path!r} must be a string or null")

    row = get_candidate(cid)
    if not row:
        raise ValueError(f"candidate not found: {cid}")

    if debug:
        logger.debug_index(
            func="run_contact_skill",
            index=1,
            total=2,
            identifier=cid[:80],
            outcome="found",
        )
        logger.debug_detail(f"skill_key={key}")
        for path, value in fields.items():
            if value is None:
                continue
            for line in truncate_debug_content(str(value)):
                logger.debug_detail(f"{path}={line}")

    merge_dict: Dict[str, Any] = {}
    paths_written: List[str] = []
    for path, value in fields.items():
        if value is None:
            continue
        _deep_merge(merge_dict, _nest_dotted_path(path, value))
        paths_written.append(path)

    if merge_dict:
        save_candidate_data(cid, merge_dict)

    paths_written = sorted(paths_written)
    if debug:
        logger.debug_index(
            func="run_contact_skill",
            index=2,
            total=2,
            identifier=cid[:80],
            outcome="recorded",
        )
        logger.debug_detail(f"paths_written={','.join(paths_written)}")

    return {
        "ok": True,
        "skill_key": key,
        "astral_candidate_id": cid,
        "paths_written": paths_written,
    }


def _nest_dotted_path(path: str, value: Any) -> Dict[str, Any]:
    """Turn 'a.b.c' + value into {'a': {'b': {'c': value}}}."""
    parts = path.split(".")
    out: Any = value
    for part in reversed(parts):
        out = {part: out}
    return out


def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    """Merge src into dst in place; dict values recurse. Return dst."""
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


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
    channel = event.get("channel")
    msg_ts = event.get("ts")
    result = {
        "accepted": True,
        "event_id": event_id,
        "event_type": etype,
        "user": event.get("user"),
        "channel": channel,
        "ts": msg_ts,
        "thread_ts": event.get("thread_ts"),
        "text": text,
    }
    # Warm process-local cache — key uses Slack thread_ts only (never message ts).
    if isinstance(channel, str) and channel and isinstance(msg_ts, str) and msg_ts:
        append_slack_conversation_message(
            channel=channel,
            thread_ts=event.get("thread_ts"),
            message={
                "user": event.get("user"),
                "text": text,
                "ts": msg_ts,
            },
            debug=debug,
        )
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
            f"channel={channel!r} text={preview!r}"
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
