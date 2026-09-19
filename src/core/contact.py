"""
Contact: Slack foundation + CONTACT_CONFIG skills ACL (Astral Contact / AST-1066).

AST-1069: Events HTTP ingress (`receive_slack_events_http`) + inbound routing
(`handle_slack_event`). AST-1071: ACL-gated entity-save skill runners.
AST-1068 / AST-1668: `resolve_slack_user` lookup-only (no create-on-miss);
unbound Slack poster pool + known/unknown recognition replies on accept.
AST-1070: Slack-sourced conversation context load / process-local cache / append.
AST-1067: Manage Slack listen hydrate/set + non-prod reply prefix / post helper.
AST-1206: Manage Slack debug get/set.
AST-1207: Events/Socket ingress hydrates debug from Manage Slack durable SoT
(`slack_debug_enabled`); logger.debug on the Contact Slack path (log_debug ContextVar).
AST-1073: Contact Estelle turn loop (`run_contact_estelle_turn`).
Conversational envelope contract: AST-1072.
AST-1471 / AST-1531: Contact scrap path → `contact_land_meteorite` → `stage_meteorite`.
AST-1561: BOT_BLOCKED paste recovery via `apply_paste` (no re-classify).
AST-1515: Contact-task markup parse/dispatch + same-event follow-up turn.
AST-1585 / patt.artifact.read-operative — Estelle pin→body for pilot
base_resume via get_operative_base_resume.
"""

from __future__ import annotations

import asyncio
import copy
import functools
import importlib
import inspect
import json
import os
import re
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

from src.core.candidate import (
    get_candidate,
    get_candidate_id_for_query,
    get_operative_base_resume,
    save_candidate_data,
)
from src.data import database
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
    list_workspace_posters,
    parse_url_verification,
    post_message,
    verify_slack_signature,
)
from src.utils.config import (
    CONTACT_CONFIG,
    CONTACT_ESTELLE_CONFIG,
    CONTACT_TASK_CONFIG,
    METEORITE_CONFIG,
    STAGE_METEORITE_CONFIG,
)
from src.utils.deploy_status import get_deploy_label
from src.utils.logging import get_logger, log_debug

logger = get_logger(__name__)

# Process-local event_id dedupe (single gunicorn worker). OrderedDict as ring.
_seen_event_ids: "OrderedDict[str, None]" = OrderedDict()
_seen_lock = threading.Lock()

# Process-local conversation cache: key → {messages, fetched_at}. LRU by access.
# Key is (channel, Slack thread_ts or "") — never message ts (would shard one DM).
_context_cache: "OrderedDict[Tuple[str, str], Dict[str, Any]]" = OrderedDict()
_context_lock = threading.Lock()


def _with_log_debug(fn):
    """Set log_debug from debug= for this frame; nested set/reset is correct."""
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            bound = inspect.signature(fn).bind_partial(*args, **kwargs)
            bound.apply_defaults()
            token = log_debug.set(bool(bound.arguments.get("debug", False)))
            try:
                return await fn(*args, **kwargs)
            finally:
                log_debug.reset(token)
        return async_wrapper

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        bound = inspect.signature(fn).bind_partial(*args, **kwargs)
        bound.apply_defaults()
        token = log_debug.set(bool(bound.arguments.get("debug", False)))
        try:
            return fn(*args, **kwargs)
        finally:
            log_debug.reset(token)
    return wrapper


def _contact_listen_info(
    candidate_id: Any,
    event_type: Any,
    outcome: Any,
    skill_keys: Any,
    channel: Any,
    aside: Any,
) -> None:
    cid = (str(candidate_id).strip() if candidate_id is not None else "") or "-"
    et = (str(event_type).strip() if event_type is not None else "") or "-"
    oc = (str(outcome).strip() if outcome is not None else "") or "-"
    if isinstance(skill_keys, (list, tuple)):
        action = ",".join(str(k) for k in skill_keys if k) or "-"
    else:
        action = (str(skill_keys).strip() if skill_keys else "") or "-"
    ch = (str(channel).strip() if channel is not None else "") or "-"
    aside_s = aside.strip() if isinstance(aside, str) and aside.strip() else "-"
    logger.info(
        "%s | contact listen %s %s: action:%s (channel: %s) aside: %s",
        cid, et, oc, action, ch, aside_s,
    )


@_with_log_debug
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
    channel_n = (channel or "").strip()
    if not channel_n:
        raise ValueError("channel must be a non-empty string")
    thread_n = thread_ts or ""
    key = _context_cache_key(channel_n, thread_n)
    now = time.time()
    ttl = float(CONTACT_CONFIG["context_cache_ttl_seconds"])
    limit = int(CONTACT_CONFIG["context_history_limit"])
    logger.debug(
        "Calling load_slack_conversation_context: [channel=%r, thread_ts=%r, refresh=%s]",
        channel_n, thread_n, refresh,
    )

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
                logger.debug("Response from load_slack_conversation_context: %s", out)
                return out

    logger.debug(
        "Calling fetch_conversation_history: [channel=%r, thread_ts=%r, limit=%s]",
        channel_n, thread_n or None, limit,
    )
    messages = fetch_conversation_history(
        channel=channel_n,
        thread_ts=thread_n or None,
        limit=limit,
    )
    logger.debug("Response from fetch_conversation_history: %s", messages)
    _context_cache_put(key, {"messages": list(messages), "fetched_at": now})
    out = {
        "channel": channel_n,
        "thread_ts": thread_n,
        "messages": list(messages),
        "source": "slack",
    }
    logger.debug("Response from load_slack_conversation_context: %s", out)
    return out


@_with_log_debug
def append_slack_conversation_message(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    message: dict,
    debug: bool = False,
) -> None:
    """Append one message into the process-local cache for that conversation key."""
    if not isinstance(message, dict) or "text" not in message or "ts" not in message:
        raise ValueError("message must be a dict with text and ts")
    if not isinstance(message["text"], str) or not isinstance(message["ts"], str):
        raise ValueError("message text and ts must be strings")

    key = _context_cache_key(channel, thread_ts)
    limit = int(CONTACT_CONFIG["context_history_limit"])
    now = time.time()
    logger.debug(
        "Calling append_slack_conversation_message: [channel=%r, thread_ts=%r, ts=%r, text=%r]",
        key[0], key[1], message["ts"], message["text"],
    )
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
    logger.debug(
        "Response from append_slack_conversation_message: len(messages)=%s",
        len(entry["messages"]),
    )


@_with_log_debug
def contact_post_message(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Post via external slack.post_message, then append outbound text into cache."""
    logger.debug(
        "Calling post_message: [channel=%r, thread_ts=%r, text=%r]",
        channel, thread_ts, text,
    )
    resp = post_message(channel=channel, text=text, thread_ts=thread_ts)
    logger.debug("Response from post_message: %s", resp)
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


@_with_log_debug
def set_slack_listen_enabled(enabled: bool, *, debug: bool = False) -> bool:
    """Persist + apply listen flag for this deploy environment. Returns the stored bool."""
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    logger.debug("Calling save_contact_listen_enabled: [enabled=%s]", enabled)
    save_contact_listen_enabled(enabled)
    CONTACT_CONFIG["listen_enabled"] = enabled
    stored = bool(CONTACT_CONFIG["listen_enabled"])
    logger.debug(
        "Response from save_contact_listen_enabled: listen_enabled=%s environment=%s",
        stored, get_deploy_label(),
    )
    return stored


def slack_debug_enabled() -> bool:
    """Return Contact Slack debug flag (durable file under db_dir is SoT when present)."""
    # Re-read every call — same posture as slack_listen_enabled (AST-1101).
    loaded = load_contact_debug_enabled()
    if loaded is not None:
        CONTACT_CONFIG["debug_enabled"] = loaded
    return bool(CONTACT_CONFIG["debug_enabled"])


@_with_log_debug
def set_slack_debug_enabled(enabled: bool, *, debug: bool = False) -> bool:
    """Persist + apply Contact Slack debug flag for this deploy environment. Returns the stored bool."""
    if not isinstance(enabled, bool):
        raise TypeError("enabled must be bool")
    logger.debug("Calling save_contact_debug_enabled: [enabled=%s]", enabled)
    save_contact_debug_enabled(enabled)
    CONTACT_CONFIG["debug_enabled"] = enabled
    stored = bool(CONTACT_CONFIG["debug_enabled"])
    logger.debug(
        "Response from save_contact_debug_enabled: debug_enabled=%s environment=%s",
        stored, get_deploy_label(),
    )
    return stored


@_with_log_debug
def list_estelle_activity(*, debug: bool = False) -> list[dict]:
    """Return durable @Estelle activity rows for Manage Slack (AST-1094)."""
    from src.data.contact_estelle_activity import list_estelle_activity_rows

    logger.debug("Calling list_estelle_activity_rows: []")
    rows = list_estelle_activity_rows()
    logger.debug("Response from list_estelle_activity_rows: row_count=%s", len(rows))
    return rows


def format_contact_reply_text(text: str) -> str:
    """Prefix non-production Contact replies with ``[<environment>] ``; production unchanged."""
    body = text if isinstance(text, str) else ""
    if contact_is_production_deploy():
        return body
    return non_production_reply_prefix(get_deploy_label()) + body


@_with_log_debug
def post_contact_reply(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Format outbound text (non-prod prefix) then ``external.slack.post_message``."""
    outbound = format_contact_reply_text(text)
    logger.debug(
        "Calling post_message: [channel=%r, thread_ts=%r, text=%r, outbound=%r]",
        channel, thread_ts, text, outbound,
    )
    resp = post_message(channel=channel, text=outbound, thread_ts=thread_ts)
    logger.debug("Response from post_message: %s", resp)
    return resp


def contact_skill_meta(skill_key: str) -> Dict[str, Any]:
    """Return a shallow copy of one skill ACL entry, or raise ValueError if unknown."""
    key = (skill_key or "").strip()
    if key not in CONTACT_CONFIG["skills"]:
        raise ValueError(f"unknown contact skill: {key!r}")
    meta = dict(CONTACT_CONFIG["skills"][key])
    meta["allowed_paths"] = tuple(meta["allowed_paths"])
    return meta


@_with_log_debug
def run_contact_skill(
    skill_key: str,
    *,
    astral_candidate_id: str,
    fields: Dict[str, Any],
    debug: bool = False,
) -> Dict[str, Any]:
    """ACL-gated entity save for Contact. Writes only allowlisted paths (name columns or library blobs)."""
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

    logger.debug(
        "Calling get_candidate: [astral_candidate_id=%r, skill_key=%s, fields=%s]",
        cid, key, fields,
    )
    row = get_candidate(cid)
    logger.debug("Response from get_candidate: %s", row)
    if not row:
        raise ValueError(f"candidate not found: {cid}")

    merge_dict: Dict[str, Any] = {}
    paths_written: List[str] = []
    for path, value in fields.items():
        if value is None:
            continue
        _deep_merge(merge_dict, _nest_dotted_path(path, value))
        paths_written.append(path)

    if merge_dict:
        logger.debug("Calling save_candidate_data: [astral_candidate_id=%r, merge=%s]", cid, merge_dict)
        save_candidate_data(cid, merge_dict)
        logger.debug("Response from save_candidate_data: paths_written=%s", paths_written)

    paths_written = sorted(paths_written)
    return {
        "ok": True,
        "skill_key": key,
        "astral_candidate_id": cid,
        "paths_written": paths_written,
    }


def try_meteorite_apply_paste_from_slack(
    *,
    astral_candidate_id: Optional[str],
    channel: str,
    thread_ts: Optional[str],
    message_ts: Optional[str],
    text: str,
    debug: bool = False,
) -> dict:
    """AST-1561: thread-first BOT_BLOCKED paste recovery before Estelle classify."""
    if not (isinstance(astral_candidate_id, str) and astral_candidate_id.strip()):
        return {"applied": False}
    if not (isinstance(text, str) and text.strip()):
        return {"applied": False}

    from src.core.meteorite import (
        apply_paste,
        find_meteorite_bot_blocked_paste_source,
        find_meteorite_for_estelle_thread,
    )

    row = None
    anchor = (thread_ts or message_ts or "").strip()
    if anchor:
        row = find_meteorite_for_estelle_thread(
            candidate_id=astral_candidate_id, thread_ts=anchor
        )
    if row is None:
        row = find_meteorite_bot_blocked_paste_source(candidate_id=astral_candidate_id)
    if row is None:
        return {"applied": False}

    result = apply_paste(int(row["id"]), text, debug=debug)
    return {"applied": True, "result": result}


def contact_land_meteorite(
    astral_candidate_id: str,
    *,
    source_kind: str,
    source_id: str,
    scraps: Optional[List[Dict[str, Any]]] = None,
    text: Optional[str] = None,
    job_link: Optional[str] = None,
    employer_name: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Contact/Estelle sync entry to stage_meteorite (AST-1531)."""
    err = {
        "outcome": METEORITE_CONFIG["land_outcome_error"],
        "error": "source_kind/source_id required",
        "skipped": False,
        "scraps": [],
        "land": None,
        "outcomes": [],
        "company": None,
        "company_inserted": False,
    }
    kind = (source_kind or "").strip()
    sid = (source_id or "").strip()
    if kind not in STAGE_METEORITE_CONFIG["source_ref_prefixes"] or not sid:
        return err

    parts: List[str] = []
    if isinstance(text, str) and text.strip():
        parts.append(text.strip())
    elif isinstance(scraps, list) and scraps:
        for scrap in scraps:
            if not isinstance(scrap, dict):
                continue
            for key in ("text", "content", "html_body"):
                val = scrap.get(key)
                if isinstance(val, str) and val.strip():
                    parts.append(val.strip())
            link = scrap.get("job_link")
            if isinstance(link, str) and link.strip():
                parts.append(link.strip())
    blob = "\n\n".join(parts)
    link_kw = job_link.strip() if isinstance(job_link, str) else ""
    if link_kw and link_kw not in blob:
        blob = f"{blob}\n\n{link_kw}" if blob else link_kw
    emp = employer_name.strip() if isinstance(employer_name, str) else ""
    if emp:
        blob = f"{blob}\n\nEmployer: {emp}" if blob else f"Employer: {emp}"
    if not blob.strip():
        out = dict(err)
        out["error"] = "blob is required"
        return out

    from src.core.meteorite import stage_meteorite

    return asyncio.run(
        stage_meteorite(
            astral_candidate_id,
            blob,
            source_kind=kind,
            source_id=sid,
            debug=debug,
        )
    )


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


@_with_log_debug
def resolve_slack_user(
    slack_user_id: str,
    *,
    estelle_in_play: bool,
    debug: bool = False,
) -> dict:
    """Lookup Slack user → astral candidate; never creates PROSPECT (AST-1668)."""
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

    logger.debug(
        "Calling get_candidate_id_for_query: [slack_user_id=%r, estelle_in_play=%s]",
        sid, estelle_in_play,
    )
    cid = get_candidate_id_for_query(sid, debug=debug)
    logger.debug("Response from get_candidate_id_for_query: %s", cid)
    if cid is not None:
        row = get_candidate(cid)
        state = (row or {}).get("state")
        username, _ = _identity_from_contact(row)
        display = ""
        # users.info for activity display; persist username when contact lacks it (AST-1105).
        try:
            logger.debug("Calling fetch_user_profile: [slack_user_id=%r]", sid)
            profile = fetch_user_profile(sid)
            logger.debug("Response from fetch_user_profile: %s", profile)
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
            logger.exception(
                "%s | contact resolve_slack_user\n  %s: %s\n  Continuing with the candidate already bound",
                cid, type(exc).__name__, exc,
            )
        logger.debug(
            "Response from resolve_slack_user: candidate_id=%s state=%s slack_username=%r",
            cid, state, username,
        )
        return {
            "astral_candidate_id": cid,
            "state": state,
            "created": False,
            "slack_username": username,
            "slack_display_name": display,
        }

    # Miss: lookup-only — never mint PROSPECT (estelle_in_play only gates profile fetch).
    username = ""
    display = ""
    if estelle_in_play:
        logger.debug("Calling fetch_user_profile: [slack_user_id=%r]", sid)
        profile = fetch_user_profile(sid)
        logger.debug("Response from fetch_user_profile: %s", profile)
        username = str(profile.get("username") or "").strip()
        display = str(profile.get("display_name") or "").strip()

    logger.debug("Response from resolve_slack_user: candidate_id=None")
    return {
        "astral_candidate_id": None,
        "state": None,
        "created": False,
        "slack_username": username,
        "slack_display_name": display,
    }


def list_unbound_slack_users(*, debug: bool = False) -> list[dict]:
    """Workspace posters whose Slack id is not bound on any non-deleted candidate."""
    log = get_logger(__name__)
    if debug:
        log.set_debug_flag(True)

    log.debug("Calling list_workspace_posters: []")
    posters = list_workspace_posters()
    log.debug("Response from list_workspace_posters: %s", posters)

    out: List[dict] = []
    log.debug("Beginning unbound filter loop on %s items", len(posters))
    for poster in posters:
        if not isinstance(poster, dict):
            continue
        sid = poster.get("slack_user_id")
        if not isinstance(sid, str) or not sid.strip():
            continue
        sid = sid.strip()
        if get_candidate_id_for_query(sid, debug=debug) is not None:
            continue
        uname = poster.get("username")
        out.append(
            {
                "slack_user_id": sid,
                "username": uname.strip() if isinstance(uname, str) else "",
            }
        )
    log.debug("End unbound filter loop after %s items", len(out))
    return out


_CONTACT_TASK_MARKUP_RE = re.compile(
    r"~~/([a-z][a-z0-9_]*)\s*(.*?)\s*~~",
    re.DOTALL,
)


def contact_tasks() -> Dict[str, Any]:
    """Shallow copy of CONTACT_TASK_CONFIG allowlist."""
    return dict(CONTACT_TASK_CONFIG)


def parse_contact_task_markup(text: str) -> List[Tuple[str, str]]:
    """Return ordered (task_key, param) pairs from Estelle reply markup."""
    raw = text if isinstance(text, str) else ""
    out: List[Tuple[str, str]] = []
    for m in _CONTACT_TASK_MARKUP_RE.finditer(raw):
        key = (m.group(1) or "").strip()
        param = (m.group(2) or "").strip()
        if key:
            out.append((key, param))
    return out


def strip_contact_task_markup(text: str) -> str:
    """Remove all contact-task markup spans; collapse runs of blank lines to one."""
    raw = text if isinstance(text, str) else ""
    stripped = _CONTACT_TASK_MARKUP_RE.sub("", raw)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    return stripped.strip()


def _resolve_contact_task_handler(handler: str):
    """Import a contact-task handler by dotted path; None when unavailable."""
    h = (handler or "").strip()
    if not h or "." not in h:
        return None
    module_path, _, attr_name = h.rpartition(".")
    if not module_path or not attr_name:
        return None
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, attr_name)
    except (ImportError, AttributeError, ValueError):
        return None


_ARTIFACT_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _is_artifact_uuid(value: str) -> bool:
    return bool(_ARTIFACT_UUID_RE.match((value or "").strip()))


@_with_log_debug
def resolve_pinned_base_resume(
    astral_candidate_id: str,
    artifact_uuid: str,
    *,
    debug: bool = False,
) -> Optional[Any]:
    """Pin→body for pilot base_resume; None on miss / wrong owner / non-pilot.

    Calls candidate.get_operative_base_resume. No candidate_data blob fallback.
    """
    cid = (astral_candidate_id or "").strip()
    uid = (artifact_uuid or "").strip()
    logger.debug(
        "Calling resolve_pinned_base_resume: [astral_candidate_id=%r, artifact_uuid=%r]",
        cid, uid,
    )
    if not cid or not uid:
        logger.debug("Response from resolve_pinned_base_resume: hit=False")
        return None

    row = database.get_artifact(uid)
    hit = False
    body: Optional[Any] = None
    if row is not None and str(row.get("entity_id") or "").strip() == cid:
        body = get_operative_base_resume(uid)
        hit = body is not None

    logger.debug("Response from resolve_pinned_base_resume: hit=%s", hit)
    return body


@_with_log_debug
def run_contact_task_dispatch(
    *,
    astral_candidate_id: str,
    markup_spans: List[Tuple[str, str]],
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """Run allowlisted contact tasks from parsed reply markup (AST-1515)."""
    results: List[Dict[str, Any]] = []
    cid = (astral_candidate_id or "").strip()
    logger.debug("Beginning contact-task loop on %s items", len(markup_spans))

    for key, param in markup_spans:
        if key not in CONTACT_TASK_CONFIG:
            continue
        meta = CONTACT_TASK_CONFIG[key]
        logger.debug("Calling contact task %s: [param=%r, candidate_id=%r]", key, param, cid)

        if meta.get("requires_candidate") and not cid:
            row = {"ok": False, "error": "no_candidate", "task_key": key}
            logger.warning("%s -> %s [%s]", key, "task_failed", "no_candidate")
            results.append(row)
            logger.debug("Response from contact task %s: %s", key, row)
            continue

        # AST-1585: pin→body / refuse blob dual-read for get_candidate_data.
        if key == "get_candidate_data":
            param_n = (param or "").strip()
            if _is_artifact_uuid(param_n):
                body = resolve_pinned_base_resume(cid, param_n, debug=debug)
                if body is not None:
                    row = {
                        "ok": True,
                        "task_key": "get_candidate_data",
                        "result": body,
                    }
                else:
                    row = {
                        "ok": False,
                        "error": "not_found",
                        "task_key": "get_candidate_data",
                    }
                    logger.warning("%s -> %s [%s]", key, "task_failed", "not_found")
                results.append(row)
                logger.debug("Response from contact task %s: %s", key, row)
                continue
            if param_n == "artifacts.base_resume":
                row = {
                    "ok": False,
                    "error": "pin_required",
                    "task_key": "get_candidate_data",
                }
                logger.warning("%s -> %s [%s]", key, "task_failed", "pin_required")
                results.append(row)
                logger.debug("Response from contact task %s: %s", key, row)
                continue

        handler = _resolve_contact_task_handler(meta.get("handler") or "")
        if handler is None:
            row = {"ok": False, "error": "handler_unavailable", "task_key": key}
            logger.warning("%s -> %s [%s]", key, "task_failed", "handler_unavailable")
            results.append(row)
            logger.debug("Response from contact task %s: %s", key, row)
            continue

        try:
            if asyncio.iscoroutinefunction(handler):
                raw_result = asyncio.run(handler(cid, param, debug=debug))
            else:
                raw_result = handler(cid, param, debug=debug)
            if isinstance(raw_result, dict):
                row = dict(raw_result)
                row.setdefault("task_key", key)
                if "ok" not in row:
                    row["ok"] = True
            else:
                row = {"ok": True, "result": raw_result, "task_key": key}
        except Exception as exc:
            row = {"ok": False, "error": str(exc), "task_key": key}
            logger.warning("%s -> %s [%s]", key, "task_failed", str(exc))

        results.append(row)
        logger.debug("Response from contact task %s: %s", key, row)

    logger.debug("End contact-task loop after %s items", len(results))
    return results


@_with_log_debug
def run_contact_estelle_turn(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    message_ts: Optional[str] = None,
    astral_candidate_id: Optional[str] = None,
    candidate_state: Optional[str] = None,
    base_resume_artifact_id: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """One Contact Estelle conversational turn (AST-1073).

    Returns a dict with at least:
      ok, outcome, reply, admin_aside, skill_results, slack_post, error
    """
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

    logger.debug(
        "Calling run_contact_estelle_turn: [channel=%r, thread_ts=%r, "
        "astral_candidate_id=%r, candidate_state=%r, text=%r]",
        channel, thread_ts, astral_candidate_id, candidate_state, text,
    )

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
    lines.append("## Available contact tasks (markup)")
    lines.append("Embed instructions in agent_payload.reply only — not skill_calls.")
    lines.append("Syntax: ~~/<task_key> <parameters>~~")
    lines.append(
        "Only use task keys listed below. Contact executes markup after your turn "
        "and strips it from the Slack-visible reply. Do not paste raw task payloads "
        "into reply — stay conversational."
    )
    for task_key, meta in contact_tasks().items():
        desc = (meta or {}).get("description") or ""
        hint = (meta or {}).get("param_hint") or ""
        lines.append(f"- {task_key}: {desc} | param: {hint}")
    lines.append("")
    lines.append("## Land meteorite (job scraps)")
    lines.append(
        "When the candidate shares a job listing (link and/or text), emit land_calls as a"
    )
    lines.append("JSON list. Each item may be either:")
    lines.append(
        '  - {"scraps": [ {"text": "...", "job_link": "...", "employer_name": "..."}, ... ]}'
    )
    lines.append(
        '  - {"text": "...", "job_link": "...", "employer_name": "..."}  (single scrap)'
    )
    lines.append("Omit land_calls when none. Do not invent job content.")
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

    # c. Candidate raft for tokens (AST-1585: strip blob base_resume; pin→body when supplied)
    candidate_data: dict = {}
    if isinstance(astral_candidate_id, str) and astral_candidate_id.strip():
        row = get_candidate(astral_candidate_id)
        if isinstance(row, dict):
            cd = row.get("candidate_data")
            if isinstance(cd, dict):
                candidate_data = copy.deepcopy(cd)
            arts = candidate_data.get("artifacts")
            if isinstance(arts, dict) and "base_resume" in arts:
                arts = dict(arts)
                del arts["base_resume"]
                candidate_data["artifacts"] = arts
            pin = (base_resume_artifact_id or "").strip()
            if pin:
                body = resolve_pinned_base_resume(
                    astral_candidate_id, pin, debug=debug
                )
                if body is not None:
                    candidate_data.setdefault("artifacts", {})["base_resume"] = body

    # d. do_task + envelope helper
    task_key = CONTACT_ESTELLE_CONFIG["task_key"]
    logger.debug(
        "Calling agent.do_task: [task_key=%s, index=%s]",
        task_key, astral_candidate_id or channel,
    )
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
    logger.debug("Response from agent.do_task: %s", result)
    turn = conversational_turn_from_do_task_result(result)

    reply_raw = turn.get("reply") if isinstance(turn.get("reply"), str) else ""
    markup_spans = parse_contact_task_markup(reply_raw)
    reply_stripped = strip_contact_task_markup(reply_raw)
    contact_task_results = run_contact_task_dispatch(
        astral_candidate_id=astral_candidate_id or "",
        markup_spans=markup_spans,
        debug=debug,
    )
    listed_markup = any(key in CONTACT_TASK_CONFIG for key, _ in markup_spans)
    reply_for_slack = reply_stripped
    if listed_markup:
        follow_lines = [
            f"channel={channel}",
            f"thread_ts={thread_ts or ''}",
            f"astral_candidate_id={astral_candidate_id or ''}",
            f"candidate_state={candidate_state or ''}",
            "",
            "## Contact task results (same inbound event)",
        ]
        for row in contact_task_results:
            follow_lines.append(_trim(json.dumps(row, default=str)))
        follow_lines.append("")
        follow_lines.append("## Conversation")
        for m in messages:
            if not isinstance(m, dict):
                continue
            who = m.get("user") or m.get("bot_id") or "unknown"
            follow_lines.append(f"[{who}] {_trim(m.get('text') or '')}")
        follow_lines.append("")
        follow_lines.append("## Latest inbound")
        follow_lines.append(_trim(text if isinstance(text, str) else ""))
        follow_live_content = "\n".join(follow_lines)
        logger.debug(
            "Calling agent.do_task: [task_key=%s, index=%s, follow_up=True]",
            task_key, astral_candidate_id or channel,
        )
        follow_result = asyncio.run(
            do_task(
                task_key,
                live_content=follow_live_content,
                index=astral_candidate_id or channel,
                candidate_data=candidate_data,
                debug=debug,
                store_agent_data=True,
            )
        )
        logger.debug("Response from agent.do_task: %s", follow_result)
        follow_turn = conversational_turn_from_do_task_result(follow_result)
        turn = follow_turn
        reply_for_slack = strip_contact_task_markup(
            follow_turn.get("reply") if isinstance(follow_turn.get("reply"), str) else ""
        )

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
            logger.warning("%s -> %s [%s]", skill_key, "skill_failed", "no_candidate")
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
            logger.warning("%s -> %s [%s]", skill_key, "skill_failed", str(exc))

    # e2. Optional land_calls → contact_land_meteorite (AST-1531; not ACL skill)
    land_results: List[Dict[str, Any]] = []
    raw_land = parsed.get("land_calls") if isinstance(parsed, dict) else None
    land_items = raw_land if isinstance(raw_land, list) else []
    # Prefer message_ts, then thread_ts, then channel for Slack source-ref id.
    slack_sid = ""
    for cand in (message_ts, thread_ts, channel):
        if isinstance(cand, str) and cand.strip():
            slack_sid = cand.strip()
            break
    for item in land_items:
        if not isinstance(item, dict):
            continue
        if not (isinstance(astral_candidate_id, str) and astral_candidate_id.strip()):
            land_results.append({"ok": False, "error": "no_candidate"})
            logger.warning("%s -> %s [%s]", "land_meteorite", "land_failed", "no_candidate")
            continue
        try:
            from src.core.meteorite import (
                apply_paste,
                find_meteorite_bot_blocked_paste_source,
            )

            paste_row = find_meteorite_bot_blocked_paste_source(
                candidate_id=astral_candidate_id
            )
            if paste_row is not None and isinstance(text, str) and text.strip():
                apply_out = apply_paste(int(paste_row["id"]), text, debug=debug)
                land_results.append({"ok": True, "result": apply_out, "via": "apply_paste"})
                continue
            if isinstance(item.get("scraps"), list) and item["scraps"]:
                land_out = contact_land_meteorite(
                    astral_candidate_id,
                    source_kind="slack",
                    source_id=slack_sid,
                    scraps=item["scraps"],
                    debug=debug,
                )
            else:
                land_out = contact_land_meteorite(
                    astral_candidate_id,
                    source_kind="slack",
                    source_id=slack_sid,
                    text=item.get("text") if isinstance(item.get("text"), str) else None,
                    job_link=(
                        item.get("job_link")
                        if isinstance(item.get("job_link"), str)
                        else None
                    ),
                    employer_name=(
                        item.get("employer_name")
                        if isinstance(item.get("employer_name"), str)
                        else None
                    ),
                    debug=debug,
                )
            land_results.append({"ok": True, "result": land_out})
        except Exception as exc:
            land_results.append({"ok": False, "error": str(exc)})
            logger.warning("%s -> %s [%s]", "land_meteorite", "land_failed", str(exc))

    # f. Outbound reply — only success/concern with non-empty reply
    reply = turn.get("reply")
    slack_post = None
    outcome = turn.get("outcome")
    reply_ok = (
        bool(turn.get("success"))
        and isinstance(reply_for_slack, str)
        and bool(reply_for_slack.strip())
        and outcome in ("success", "concern")
    )
    if reply_ok:
        reply_thread_ts = thread_ts or message_ts
        outbound = format_contact_reply_text(reply_for_slack)
        slack_post = contact_post_message(
            channel=channel,
            text=outbound,
            thread_ts=reply_thread_ts,
            debug=debug,
        )

    # g. Admin aside rides the always-on listen info line (never Slack, never a warning).
    aside = turn.get("admin_aside")

    do_task_error = None
    if isinstance(result, dict) and not result.get("success"):
        do_task_error = result.get("error")

    out = {
        "ok": bool(turn.get("success")) and do_task_error is None,
        "outcome": outcome,
        "reply": reply if isinstance(reply, str) else None,
        "admin_aside": aside if isinstance(aside, str) else None,
        "skill_results": skill_results,
        "land_results": land_results,
        "contact_task_results": contact_task_results,
        "slack_post": slack_post,
        "error": do_task_error,
    }
    logger.debug("Response from run_contact_estelle_turn: %s", out)
    return out


def _emit_listen_info(result: dict, event_type: Any, channel: Any, turn_out: Any) -> None:
    keys: List[str] = []
    aside = None
    outcome = None
    if isinstance(turn_out, dict):
        outcome = turn_out.get("outcome")
        aside = turn_out.get("admin_aside")
        for row in turn_out.get("skill_results") or []:
            if isinstance(row, dict) and row.get("skill_key"):
                keys.append(str(row["skill_key"]))
    _contact_listen_info(
        result.get("astral_candidate_id") if isinstance(result, dict) else None,
        event_type,
        outcome,
        keys,
        channel,
        aside,
    )


def handle_slack_event(payload: dict, *, debug: bool = False) -> dict:
    """Route one Slack Events API payload into Contact (listen-gated)."""
    # AST-1207: Manage Slack Debug is sole SoT for Contact Slack Events (Archie).
    # Caller kwarg kept for signature compat; durable file wins every call.
    debug = slack_debug_enabled()
    token = log_debug.set(debug)
    try:
        return _handle_slack_event_body(payload, debug)
    finally:
        log_debug.reset(token)


def _handle_slack_event_body(payload: dict, debug: bool) -> dict:
    if not slack_listen_enabled():
        logger.debug("Response from handle_slack_event: accepted=False reason=listen_off")
        return {"accepted": False, "reason": "listen_off"}

    event_id = payload.get("event_id") if isinstance(payload, dict) else None
    if not event_id or not isinstance(event_id, str):
        logger.debug("Response from handle_slack_event: accepted=False reason=missing_event_id")
        return {"accepted": False, "reason": "missing_event_id"}

    if not _remember_event_id(event_id):
        logger.debug("Response from handle_slack_event: accepted=False reason=duplicate_event")
        return {"accepted": False, "reason": "duplicate_event"}

    event = payload.get("event") or {}
    if not isinstance(event, dict):
        event = {}
    etype = event.get("type")
    if etype not in CONTACT_CONFIG["bot_event_types"]:
        logger.debug(
            "Response from handle_slack_event: accepted=False reason=type_skipped etype=%r",
            etype,
        )
        return {"accepted": False, "reason": "type_skipped"}

    if etype == "message":
        # Ignore bot echoes / edits / subtypes; only human DM text.
        if event.get("subtype") or event.get("bot_id"):
            logger.debug("Response from handle_slack_event: accepted=False reason=message_skipped")
            return {"accepted": False, "reason": "message_skipped"}
        if not _is_dm_message(event):
            logger.debug("Response from handle_slack_event: accepted=False reason=not_dm")
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
    logger.debug(
        "Calling handle_slack_event: [event_id=%r, event_type=%r, user=%r, channel=%r, text=%r]",
        event_id, etype, event.get("user"), channel, text,
    )
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
            logger.exception(
                "%s | contact resolve_slack_user\n  %s: %s\n  Continuing without a bound candidate",
                "-", type(exc).__name__, exc,
            )
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
                logger.exception(
                    "%s | contact activity identity fetch\n  %s: %s\n  Manage Slack will show this user without a name",
                    "-", type(fetch_exc).__name__, fetch_exc,
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
            logger.debug(
                "Response from record_estelle_activity: user=%r bind_ok=%s channel=%r ts=%r",
                user_for_activity, bind_ok, channel, msg_ts,
            )
        except Exception as exc:
            logger.exception(
                "%s | contact estelle activity record\n  %s: %s\n  Manage Slack activity was not updated",
                result.get("astral_candidate_id") or "-", type(exc).__name__, exc,
            )
    elif result.get("accepted"):
        logger.debug("Response from record_estelle_activity: skipped missing slack user")
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
    # AST-1668: known/unknown recognition, then Estelle only when bound.
    if result.get("accepted") and isinstance(channel, str) and channel:
        user_ok = isinstance(user, str) and bool(user.strip())
        resolve_ok = user_ok and not result.get("resolve_error")
        known = isinstance(result.get("astral_candidate_id"), str) and bool(
            result.get("astral_candidate_id")
        )
        if resolve_ok:
            text_key = (
                "known_recognition_reply_text"
                if known
                else "unknown_recognition_reply_text"
            )
            try:
                outbound = format_contact_reply_text(str(CONTACT_CONFIG[text_key]))
                reply_thread_ts = event.get("thread_ts")
                if not reply_thread_ts and isinstance(msg_ts, str):
                    reply_thread_ts = msg_ts
                result["recognition_post"] = contact_post_message(
                    channel=channel,
                    text=outbound,
                    thread_ts=reply_thread_ts,
                    debug=debug,
                )
            except Exception as exc:
                logger.exception(
                    "%s | contact recognition post\n  %s: %s\n  Recognition reply was not posted",
                    result.get("astral_candidate_id") or "-", type(exc).__name__, exc,
                )
                result["recognition_post"] = {"ok": False, "error": str(exc)}

        # Unknown bound miss: recognition only — do not run Estelle as if bound.
        if resolve_ok and not known:
            result["estelle_turn"] = {
                "ok": True,
                "outcome": "unrecognized",
                "skipped": True,
            }
            _emit_listen_info(result, etype, channel, result["estelle_turn"])
        else:
            # AST-1561: paste recovery before Estelle turn (no re-classify).
            paste_out = try_meteorite_apply_paste_from_slack(
                astral_candidate_id=result.get("astral_candidate_id"),
                channel=channel,
                thread_ts=event.get("thread_ts"),
                message_ts=msg_ts if isinstance(msg_ts, str) else None,
                text=text,
                debug=debug,
            )
            result["meteorite_apply_paste"] = paste_out
            if paste_out.get("applied") and paste_out.get("result", {}).get("ok"):
                try:
                    ack = format_contact_reply_text(
                        "Got it — pasted job description saved for review."
                    )
                    reply_thread_ts = event.get("thread_ts")
                    if not reply_thread_ts and isinstance(msg_ts, str):
                        reply_thread_ts = msg_ts
                    result["estelle_turn"] = {
                        "ok": True,
                        "outcome": "paste_applied",
                        "meteorite_apply_paste": paste_out,
                        "slack_post": contact_post_message(
                            channel=channel,
                            text=ack,
                            thread_ts=reply_thread_ts,
                            debug=debug,
                        ),
                    }
                except Exception as exc:
                    logger.exception(
                        "%s | contact paste ack\n  %s: %s\n  Paste was saved; Slack ack was not posted",
                        result.get("astral_candidate_id") or "-", type(exc).__name__, exc,
                    )
                    result["estelle_turn"] = {
                        "ok": True,
                        "outcome": "paste_applied",
                        "meteorite_apply_paste": paste_out,
                        "slack_post": {"ok": False, "error": str(exc)},
                    }
            else:
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
                    logger.exception(
                        "%s | contact estelle turn\n  %s: %s\n  The inbound event is accepted; Estelle did not complete this turn",
                        result.get("astral_candidate_id") or "-", type(exc).__name__, exc,
                    )
                    result["estelle_turn"] = {"ok": False, "error": str(exc)}
            turn_out = result.get("estelle_turn")
            if isinstance(turn_out, dict) and turn_out.get("outcome") is not None:
                _emit_listen_info(result, etype, channel, turn_out)
            # AST-1101: hear-ack when Estelle turn did not successfully post to Slack.
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
                    logger.debug(
                        "Response from hear_ack post_message: %s", result["hear_ack_post"]
                    )
                except Exception as exc:
                    logger.exception(
                        "%s | contact hear_ack\n  %s: %s\n  Estelle did not post; hear-ack was not sent",
                        result.get("astral_candidate_id") or "-", type(exc).__name__, exc,
                    )
                    result["hear_ack_post"] = {"ok": False, "error": str(exc)}
    logger.debug("Response from handle_slack_event: %s", result)
    return result

def _run_handle_slack_event_background(payload: dict, debug: bool = False) -> None:
    """Background Events worker — log failures; never raise into the ack path."""
    try:
        handle_slack_event(payload, debug=debug)
    except Exception as exc:
        logger.exception(
            "%s | contact handle_slack_event background\n  %s: %s\n  The Slack ack already returned; this event was not processed",
            "-", type(exc).__name__, exc,
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
    token = log_debug.set(debug)
    try:
        signing_secret = os.environ[CONTACT_CONFIG["signing_secret_env"]]
        if not verify_slack_signature(
            signing_secret=signing_secret,
            timestamp=timestamp or "",
            body=raw_body,
            signature=signature or "",
        ):
            logger.debug("Response from receive_slack_events_http: status=401 reason=bad_signature")
            return (401, "")

        try:
            payload = json.loads(raw_body.decode("utf-8") if isinstance(raw_body, bytes) else raw_body)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
            logger.debug("Response from receive_slack_events_http: status=400 reason=bad_json")
            return (400, "")

        if not isinstance(payload, dict):
            return (400, "")

        challenge = parse_url_verification(payload)
        if challenge is not None:
            logger.debug("Response from receive_slack_events_http: status=200 reason=url_verification")
            return (200, {"challenge": challenge})

        # Ack immediately; process off the request thread (Slack ~3s window).
        threading.Thread(
            target=_run_handle_slack_event_background,
            args=(payload, debug),
            daemon=True,
        ).start()
        logger.debug(
            "Response from receive_slack_events_http: status=200 reason=event_acked event_id=%s",
            payload.get("event_id"),
        )
        return (200, "")
    finally:
        log_debug.reset(token)
