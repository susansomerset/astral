"""
Contact: Slack foundation + CONTACT_CONFIG skills ACL (Astral Contact / AST-1066).

AST-1069: Events HTTP ingress (`receive_slack_events_http`) + inbound routing
(`handle_slack_event`). AST-1071: ACL-gated entity-save skill runners.
AST-1068: `resolve_slack_user` + PROSPECT create-on-miss (wired on accept).
AST-1070: Slack-sourced conversation context load / process-local cache / append.
AST-1067: Manage Slack listen hydrate/set + non-prod reply prefix / post helper.
AST-1206: Manage Slack debug get/set.
AST-1207: Events/Socket ingress hydrates debug from Manage Slack durable SoT
(`slack_debug_enabled`); Style D found/recorded depth on Contact Slack path.
AST-1073: Contact Estelle turn loop (`run_contact_estelle_turn`).
Conversational envelope contract: AST-1072.
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

from src.core.candidate import (
    get_candidate,
    get_candidate_id_for_query,
    initiate_prospect_candidate,
    save_candidate_data,
)
from src.data.contact_debug import (
    load_contact_debug_enabled,
    save_contact_debug_enabled,
)
from src.data.contact_listen import (
    load_contact_listen_enabled,
    save_contact_listen_enabled,
)
from src.external.slack import (
    fetch_conversation_history,
    fetch_user_profile,
    parse_url_verification,
    post_message,
    verify_slack_signature,
)
from src.utils.config import CONTACT_CONFIG, CONTACT_ESTELLE_CONFIG
from src.utils.deploy_status import get_deploy_label
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
    """Cache key = (channel, Slack thread_ts only). Missing thread → empty string."""
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
    """Return Contact listen flag (durable file under db_dir is SoT when present)."""
    # Re-read every call — sticky once-hydrate left listen stuck off after Admin toggle (AST-1101).
    loaded = load_contact_listen_enabled()
    if loaded is not None:
        CONTACT_CONFIG["listen_enabled"] = loaded
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


def contact_is_production_deploy() -> bool:
    """True when ASTRAL_DEPLOY_ENV matches CONTACT_CONFIG production_deploy_env (case-insensitive)."""
    raw = os.environ.get("ASTRAL_DEPLOY_ENV", "").strip()
    return raw.lower() == str(CONTACT_CONFIG["production_deploy_env"]).strip().lower()


def set_slack_listen_enabled(enabled: bool, *, debug: bool = False) -> bool:
    """Persist + apply listen flag for this deploy environment. Returns the stored bool."""
    if debug:
        logger.set_debug_flag(True)
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    save_contact_listen_enabled(enabled)
    CONTACT_CONFIG["listen_enabled"] = enabled
    if debug:
        logger.debug_index(
            func="contact.set_slack_listen_enabled",
            index=1,
            total=2,
            identifier="listen",
            outcome="found",
        )
        logger.debug_detail(f"requested={enabled}")
        logger.debug_index(
            func="contact.set_slack_listen_enabled",
            index=2,
            total=2,
            identifier="listen",
            outcome="recorded",
        )
        logger.debug_detail(
            f"listen_enabled={CONTACT_CONFIG['listen_enabled']} "
            f"environment={get_deploy_label()}"
        )
    return bool(CONTACT_CONFIG["listen_enabled"])


def slack_debug_enabled() -> bool:
    """Return Contact Slack debug flag (durable file under db_dir is SoT when present)."""
    # Re-read every call — same posture as slack_listen_enabled (AST-1101).
    loaded = load_contact_debug_enabled()
    if loaded is not None:
        CONTACT_CONFIG["debug_enabled"] = loaded
    return bool(CONTACT_CONFIG["debug_enabled"])


def set_slack_debug_enabled(enabled: bool, *, debug: bool = False) -> bool:
    """Persist + apply Contact Slack debug flag for this deploy environment. Returns the stored bool."""
    if debug:
        logger.set_debug_flag(True)
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    save_contact_debug_enabled(enabled)
    CONTACT_CONFIG["debug_enabled"] = enabled
    if debug:
        logger.debug_index(
            func="contact.set_slack_debug_enabled",
            index=1,
            total=2,
            identifier="debug",
            outcome="found",
        )
        logger.debug_detail(f"requested={enabled}")
        logger.debug_index(
            func="contact.set_slack_debug_enabled",
            index=2,
            total=2,
            identifier="debug",
            outcome="recorded",
        )
        logger.debug_detail(
            f"debug_enabled={CONTACT_CONFIG['debug_enabled']} "
            f"environment={get_deploy_label()}"
        )
    return bool(CONTACT_CONFIG["debug_enabled"])


def list_estelle_activity(*, debug: bool = False) -> list[dict]:
    """Return durable @Estelle activity rows for Manage Slack (AST-1094)."""
    from src.data.contact_estelle_activity import list_estelle_activity_rows

    rows = list_estelle_activity_rows()
    if debug:
        log = get_logger(__name__)
        log.set_debug_flag(True)
        log.debug_index(
            func="contact.list_estelle_activity",
            index=1,
            total=1,
            identifier="activity",
            outcome="listed",
        )
        log.debug_detail(f"row_count={len(rows)}")
    return rows


def format_contact_reply_text(text: str) -> str:
    """Prefix non-production Contact replies with ``[<environment>] ``; production unchanged."""
    body = text if isinstance(text, str) else ""
    if contact_is_production_deploy():
        return body
    return non_production_reply_prefix(get_deploy_label()) + body


def post_contact_reply(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Format outbound text (non-prod prefix) then ``external.slack.post_message``."""
    if debug:
        logger.set_debug_flag(True)
    outbound = format_contact_reply_text(text)
    if debug:
        logger.debug_index(
            func="contact.post_contact_reply",
            index=1,
            total=2,
            identifier=str(channel)[:80],
            outcome="found",
        )
        for line in truncate_debug_content(str(text) if text is not None else ""):
            logger.debug_detail(f"text={line}")
        logger.debug_index(
            func="contact.post_contact_reply",
            index=2,
            total=2,
            identifier=str(channel)[:80],
            outcome="recorded",
        )
        prefixed = outbound != (text if isinstance(text, str) else "")
        logger.debug_detail(f"prefixed={prefixed}")
        for line in truncate_debug_content(outbound):
            logger.debug_detail(f"outbound={line}")
    return post_message(channel=channel, text=outbound, thread_ts=thread_ts)


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


def resolve_slack_user(
    slack_user_id: str,
    *,
    estelle_in_play: bool,
    debug: bool = False,
) -> dict:
    """Lookup Slack user → astral candidate; create PROSPECT only when estelle_in_play."""
    if debug:
        logger.set_debug_flag(True)

    sid = (slack_user_id or "").strip()
    if not sid:
        raise ValueError("slack_user_id is required")

    def _identity_from_contact(row: Optional[dict]) -> Tuple[str, str]:
        cd = (row or {}).get("candidate_data") or {}
        contact = cd.get("contact") if isinstance(cd, dict) else None
        if not isinstance(contact, dict):
            return "", ""
        uname = contact.get("slack_username")
        return (
            uname.strip() if isinstance(uname, str) else "",
            "",
        )

    cid = get_candidate_id_for_query(sid, debug=debug)
    if cid is not None:
        row = get_candidate(cid)
        state = (row or {}).get("state")
        username, _ = _identity_from_contact(row)
        display = ""
        # users.info for activity display; persist username when contact lacks it (AST-1105).
        try:
            profile = fetch_user_profile(sid)
            fetched_user = str(profile.get("username") or "").strip()
            display = str(profile.get("display_name") or "").strip()
            if fetched_user:
                if not username:
                    save_candidate_data(
                        cid,
                        {
                            "contact": {
                                "slack_user_id": sid,
                                "slack_username": fetched_user,
                            }
                        },
                        debug=debug,
                    )
                username = fetched_user
        except Exception as exc:
            logger.error(
                "contact resolve_slack_user username backfill failed: %s",
                exc,
                exc_info=True,
            )
        if debug:
            logger.debug_index(
                func="contact.resolve_slack_user",
                index=1,
                total=1,
                identifier=sid[:80],
                outcome="found|matched",
            )
            logger.debug_detail(f"slack_user_id={sid}")
            logger.debug_detail(f"candidate_id={cid}")
            logger.debug_detail(f"state={state}")
            logger.debug_detail(f"slack_username={username!r}")
        return {
            "astral_candidate_id": cid,
            "state": state,
            "created": False,
            "slack_username": username,
            "slack_display_name": display,
        }

    if not estelle_in_play:
        if debug:
            logger.debug_index(
                func="contact.resolve_slack_user",
                index=1,
                total=1,
                identifier=sid[:80],
                outcome="found|none",
            )
            logger.debug_detail(f"slack_user_id={sid}")
        return {
            "astral_candidate_id": None,
            "state": None,
            "created": False,
            "slack_username": "",
            "slack_display_name": "",
        }

    profile = fetch_user_profile(sid)
    new_id = (
        CONTACT_CONFIG["prospect_candidate_id_template"]
        .format(slack_user_id=sid)
        .strip()
        .lower()
    )
    first = str(profile.get("first") or "").strip()
    last = str(profile.get("last") or "").strip()
    display = str(profile.get("display_name") or "").strip()
    username = str(profile.get("username") or "").strip()
    if not first and not last and display:
        first = display
    candidate_data = {
        "contact": {
            "slack_user_id": sid,
            "slack_username": username,
        },
    }
    try:
        initiate_prospect_candidate(new_id, candidate_data, first=first, last=last)
    except ValueError:
        # Race: another accept already created — re-lookup.
        cid = get_candidate_id_for_query(sid, debug=debug)
        if cid is None:
            raise
        row = get_candidate(cid)
        uname, _ = _identity_from_contact(row)
        return {
            "astral_candidate_id": cid,
            "state": (row or {}).get("state"),
            "created": False,
            "slack_username": uname or username,
            "slack_display_name": display,
        }

    if debug:
        logger.debug_index(
            func="contact.resolve_slack_user",
            index=1,
            total=1,
            identifier=sid[:80],
            outcome="recorded|created",
        )
        logger.debug_detail(f"slack_user_id={sid}")
        logger.debug_detail(f"candidate_id={new_id}")
        logger.debug_detail("state=PROSPECT")
        logger.debug_detail(f"slack_username={username!r}")

    return {
        "astral_candidate_id": new_id,
        "state": "PROSPECT",
        "created": True,
        "slack_username": username,
        "slack_display_name": display,
    }



def run_contact_estelle_turn(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    message_ts: Optional[str] = None,
    astral_candidate_id: Optional[str] = None,
    candidate_state: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """One Contact Estelle conversational turn (AST-1073).

    Returns a dict with at least:
      ok, outcome, reply, admin_aside, skill_results, slack_post, error
    """
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    empty = {
        "ok": False,
        "outcome": None,
        "reply": None,
        "admin_aside": None,
        "skill_results": [],
        "slack_post": None,
        "error": None,
    }

    # a. Listen re-check (defense in depth — handle_slack_event already gates).
    if not slack_listen_enabled():
        out = dict(empty)
        out["error"] = "listen_off"
        return out

    # Late import avoids core→agent cycles at module load.
    from src.core.agent import conversational_turn_from_do_task_result, do_task

    max_chars = int(CONTACT_ESTELLE_CONFIG["turn_context_text_max_chars"])
    msg_limit = int(CONTACT_ESTELLE_CONFIG["turn_context_message_limit"])

    def _trim(s: str) -> str:
        raw = s if isinstance(s, str) else ""
        if len(raw) <= max_chars:
            return raw
        return raw[:max_chars] + "…"

    # b. Context → live_content
    ctx = load_slack_conversation_context(
        channel=channel, thread_ts=thread_ts, debug=debug
    )
    lines = [
        f"channel={channel}",
        f"thread_ts={thread_ts or ''}",
        f"astral_candidate_id={astral_candidate_id or ''}",
        f"candidate_state={candidate_state or ''}",
        "",
        "## Available Contact skills (ACL)",
        "Only emit skill_calls entries whose skill_key is listed below;",
        "fields keys must be allowlisted paths; omit skill_calls when none.",
    ]
    for skill_key, meta in contact_skills().items():
        desc = (meta or {}).get("description") or ""
        paths = (meta or {}).get("allowed_paths") or ()
        path_s = ", ".join(str(x) for x in paths)
        lines.append(f"- {skill_key}: {desc} | paths: {path_s}")
    lines.append("")
    lines.append("## Conversation")
    messages = list(ctx.get("messages") or [])
    if msg_limit > 0 and len(messages) > msg_limit:
        messages = messages[-msg_limit:]
    for m in messages:
        if not isinstance(m, dict):
            continue
        who = m.get("user") or m.get("bot_id") or "unknown"
        lines.append(f"[{who}] {_trim(m.get('text') or '')}")
    lines.append("")
    lines.append("## Latest inbound")
    lines.append(_trim(text if isinstance(text, str) else ""))
    live_content = "\n".join(lines)

    # c. Candidate raft for tokens
    candidate_data: dict = {}
    if isinstance(astral_candidate_id, str) and astral_candidate_id.strip():
        row = get_candidate(astral_candidate_id)
        if isinstance(row, dict):
            cd = row.get("candidate_data")
            candidate_data = cd if isinstance(cd, dict) else {}

    # d. do_task + envelope helper
    task_key = CONTACT_ESTELLE_CONFIG["task_key"]
    result = asyncio.run(
        do_task(
            task_key,
            live_content=live_content,
            index=astral_candidate_id or channel,
            candidate_data=candidate_data,
            debug=debug,
            store_agent_data=True,
        )
    )
    turn = conversational_turn_from_do_task_result(result)

    # e. Optional skill_calls (ACL via run_contact_skill)
    skill_results = []
    parsed = result.get("parsed_response") if isinstance(result, dict) else None
    raw_calls = parsed.get("skill_calls") if isinstance(parsed, dict) else None
    calls = raw_calls if isinstance(raw_calls, list) else []
    for item in calls:
        if not isinstance(item, dict):
            continue
        skill_key = item.get("skill_key")
        fields = item.get("fields")
        if not isinstance(skill_key, str) or not isinstance(fields, dict):
            continue
        if not (isinstance(astral_candidate_id, str) and astral_candidate_id.strip()):
            skill_results.append(
                {"ok": False, "error": "no_candidate", "skill_key": skill_key}
            )
            continue
        try:
            skill_results.append(
                run_contact_skill(
                    skill_key,
                    astral_candidate_id=astral_candidate_id,
                    fields=fields,
                    debug=debug,
                )
            )
        except Exception as exc:  # ValueError + unexpected — keep turn alive
            skill_results.append(
                {"ok": False, "error": str(exc), "skill_key": skill_key}
            )

    # f. Outbound reply — only success/concern with non-empty reply
    reply = turn.get("reply")
    slack_post = None
    outcome = turn.get("outcome")
    reply_ok = (
        bool(turn.get("success"))
        and isinstance(reply, str)
        and bool(reply.strip())
        and outcome in ("success", "concern")
    )
    if reply_ok:
        reply_thread_ts = thread_ts or message_ts
        outbound = format_contact_reply_text(reply)
        slack_post = contact_post_message(
            channel=channel,
            text=outbound,
            thread_ts=reply_thread_ts,
            debug=debug,
        )

    # g. Admin aside → logs only (never Slack)
    aside = turn.get("admin_aside")
    if outcome == "concern" and isinstance(aside, str) and aside.strip():
        aside_preview = aside if len(aside) <= _TEXT_DEBUG_MAX else aside[:_TEXT_DEBUG_MAX] + "…"
        log.warning(
            "contact estelle concern aside candidate=%s aside=%s",
            astral_candidate_id,
            aside_preview,
        )

    do_task_error = None
    if isinstance(result, dict) and not result.get("success"):
        do_task_error = result.get("error")

    out = {
        "ok": bool(turn.get("success")) and do_task_error is None,
        "outcome": outcome,
        "reply": reply if isinstance(reply, str) else None,
        "admin_aside": aside if isinstance(aside, str) else None,
        "skill_results": skill_results,
        "slack_post": slack_post,
        "error": do_task_error,
    }

    # h. Style D (debug=True only) — lengths/counts, not full blobs
    if debug:
        ident = (
            astral_candidate_id
            if isinstance(astral_candidate_id, str) and astral_candidate_id.strip()
            else str(channel)
        )
        log.debug_index(
            func="contact.run_contact_estelle_turn",
            index=1,
            total=1,
            identifier=ident,
            outcome=str(outcome or out.get("error") or "unknown"),
        )
        skill_ok = sum(1 for r in skill_results if isinstance(r, dict) and r.get("ok"))
        reply_len = len(reply) if isinstance(reply, str) else 0
        aside_len = len(aside) if isinstance(aside, str) else 0
        slack_ok = None
        if isinstance(slack_post, dict):
            slack_ok = bool(slack_post.get("ok"))
        log.debug_detail(
            f"outcome={outcome!r} success={bool(turn.get('success'))} "
            f"reply_len={reply_len} admin_aside_len={aside_len} "
            f"skill_calls={len(calls)} skill_ok={skill_ok} slack_ok={slack_ok}"
        )

    return out


def handle_slack_event(payload: dict, *, debug: bool = False) -> dict:
    """Route one Slack Events API payload into Contact (listen-gated)."""
    # AST-1207: Manage Slack Debug is sole SoT for Contact Slack Events (Archie).
    # Caller kwarg kept for signature compat; durable file wins every call.
    debug = slack_debug_enabled()
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
    user = result.get("user")
    # AST-1105: identity for activity rows (filled by resolve or fallback fetch).
    resolved_meta = {"slack_username": None, "slack_display_name": None}
    if isinstance(user, str) and user.strip():
        try:
            resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)
            result["astral_candidate_id"] = resolved["astral_candidate_id"]
            result["candidate_state"] = resolved["state"]
            result["candidate_created"] = resolved["created"]
            uname = resolved.get("slack_username")
            dname = resolved.get("slack_display_name")
            resolved_meta["slack_username"] = (
                uname if isinstance(uname, str) and uname.strip() else None
            )
            resolved_meta["slack_display_name"] = (
                dname if isinstance(dname, str) and dname.strip() else None
            )
        except Exception as exc:
            log.error("contact resolve_slack_user failed: %s", exc, exc_info=True)
            result["astral_candidate_id"] = None
            result["candidate_state"] = None
            result["candidate_created"] = False
            result["resolve_error"] = str(exc)
            # Activity names only — do not create candidate here.
            try:
                profile = fetch_user_profile(user.strip())
                uname = str(profile.get("username") or "").strip()
                dname = str(profile.get("display_name") or "").strip()
                resolved_meta["slack_username"] = uname or None
                resolved_meta["slack_display_name"] = dname or None
            except Exception as fetch_exc:
                log.error(
                    "contact activity identity fetch failed: %s",
                    fetch_exc,
                    exc_info=True,
                )
    else:
        result["astral_candidate_id"] = None
        result["candidate_state"] = None
        result["candidate_created"] = False
    # AST-1094 / AST-1105: durable activity summary for Manage Slack (not conversation SoT).
    user_for_activity = user if isinstance(user, str) and user.strip() else None
    if user_for_activity is not None:
        bind_ok = isinstance(result.get("astral_candidate_id"), str) and bool(
            result.get("astral_candidate_id")
        )
        try:
            from src.data.contact_estelle_activity import record_estelle_activity

            record_estelle_activity(
                slack_user_id=user_for_activity,
                bind_ok=bind_ok,
                astral_candidate_id=result.get("astral_candidate_id")
                if isinstance(result.get("astral_candidate_id"), str)
                else None,
                candidate_state=result.get("candidate_state")
                if isinstance(result.get("candidate_state"), str)
                else None,
                last_channel=channel if isinstance(channel, str) else None,
                last_message_ts=msg_ts if isinstance(msg_ts, str) else None,
                slack_username=resolved_meta.get("slack_username"),
                slack_display_name=resolved_meta.get("slack_display_name"),
            )
            if debug:
                log.debug_index(
                    func="contact.handle_slack_event",
                    index=1,
                    total=1,
                    identifier=event_id,
                    outcome="activity_recorded",
                )
                log.debug_detail(
                    f"activity user={user_for_activity!r} bind_ok={bind_ok} "
                    f"channel={channel!r} ts={msg_ts!r}"
                )
        except Exception as exc:
            log.error("contact estelle activity record failed: %s", exc, exc_info=True)
    elif result.get("accepted"):
        # Accepted event with no Slack user → cannot key a row; skip record.
        if debug:
            log.debug_index(
                func="contact.handle_slack_event",
                index=1,
                total=1,
                identifier=event_id,
                outcome="activity_skipped_no_user",
            )
            log.debug_detail("activity skipped: missing slack user")
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
    # AST-1073: one Estelle turn after accept + resolve + inbound cache append.
    if result.get("accepted") and isinstance(channel, str) and channel:
        try:
            turn_out = run_contact_estelle_turn(
                channel=channel,
                text=text,
                thread_ts=event.get("thread_ts"),
                message_ts=msg_ts if isinstance(msg_ts, str) else None,
                astral_candidate_id=result.get("astral_candidate_id"),
                candidate_state=result.get("candidate_state"),
                debug=debug,
            )
            result["estelle_turn"] = turn_out
        except Exception as exc:
            log.error("contact estelle turn failed: %s", exc, exc_info=True)
            result["estelle_turn"] = {"ok": False, "error": str(exc)}
        # AST-1101: hear-ack when Estelle turn did not successfully post to Slack.
        turn_out = result.get("estelle_turn")
        slack_post = turn_out.get("slack_post") if isinstance(turn_out, dict) else None
        posted = isinstance(slack_post, dict) and slack_post.get("ok") is True
        if not posted:
            try:
                outbound = format_contact_reply_text(
                    str(CONTACT_CONFIG["hear_ack_reply_text"])
                )
                reply_thread_ts = event.get("thread_ts")
                if not reply_thread_ts and isinstance(msg_ts, str):
                    reply_thread_ts = msg_ts
                result["hear_ack_post"] = contact_post_message(
                    channel=channel,
                    text=outbound,
                    thread_ts=reply_thread_ts,
                    debug=debug,
                )
                if debug:
                    preview = (
                        outbound
                        if len(outbound) <= _TEXT_DEBUG_MAX
                        else outbound[:_TEXT_DEBUG_MAX] + "…"
                    )
                    log.debug_index(
                        func="contact.handle_slack_event",
                        index=1,
                        total=1,
                        identifier=event_id,
                        outcome="hear_ack_posted",
                    )
                    log.debug_detail(f"hear_ack outbound={preview!r}")
            except Exception as exc:
                log.error("contact hear_ack post failed: %s", exc, exc_info=True)
                result["hear_ack_post"] = {"ok": False, "error": str(exc)}
                if debug:
                    log.debug_index(
                        func="contact.handle_slack_event",
                        index=1,
                        total=1,
                        identifier=event_id,
                        outcome="hear_ack_failed",
                    )
                    log.debug_detail(f"hear_ack error={exc!r}")
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


def _run_handle_slack_event_background(payload: dict, debug: bool = False) -> None:
    """Background Events worker — log failures; never raise into the ack path."""
    try:
        handle_slack_event(payload, debug=debug)
    except Exception as exc:
        get_logger(__name__).error(
            "contact handle_slack_event background failed: %s", exc, exc_info=True
        )


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
    # AST-1207: Manage Slack Debug is sole SoT for Contact Slack Events (Archie).
    # Caller kwarg kept for signature compat; durable file wins every call.
    debug = slack_debug_enabled()
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
        target=_run_handle_slack_event_background,
        args=(payload, debug),
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
