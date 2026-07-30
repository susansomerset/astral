"""
Contact: Slack foundation + CONTACT_CONFIG skills ACL (Astral Contact / AST-1066).

AST-1069: Events HTTP ingress (`receive_slack_events_http`) + inbound routing
(`handle_slack_event`). AST-1071: ACL-gated entity-save skill runners.
AST-1068: `resolve_slack_user` + PROSPECT create-on-miss (wired on accept).
Siblings: Manage Slack listen UI (AST-1067), conversation context (AST-1070).
Estelle turn loop: AST-1046 — not here.
"""

from __future__ import annotations

import json
import os
import threading
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

from src.core.candidate import (
    get_candidate,
    get_candidate_id_for_query,
    initiate_prospect_candidate,
    save_candidate_data,
)
from src.external.slack import (
    fetch_user_profile,
    parse_url_verification,
    verify_slack_signature,
)
from src.utils.config import CONTACT_CONFIG
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)

# Process-local event_id dedupe (single gunicorn worker). OrderedDict as ring.
_seen_event_ids: "OrderedDict[str, None]" = OrderedDict()
_seen_lock = threading.Lock()

_TEXT_DEBUG_MAX = 200


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

    cid = get_candidate_id_for_query(sid, debug=debug)
    if cid is not None:
        row = get_candidate(cid)
        state = (row or {}).get("state")
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
        return {
            "astral_candidate_id": cid,
            "state": state,
            "created": False,
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
    if not first and not last and display:
        first = display
    candidate_data = {
        "contact": {"slack_user_id": sid},
    }
    try:
        initiate_prospect_candidate(new_id, candidate_data, first=first, last=last)
    except ValueError:
        # Race: another accept already created — re-lookup.
        cid = get_candidate_id_for_query(sid, debug=debug)
        if cid is None:
            raise
        row = get_candidate(cid)
        return {
            "astral_candidate_id": cid,
            "state": (row or {}).get("state"),
            "created": False,
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

    return {
        "astral_candidate_id": new_id,
        "state": "PROSPECT",
        "created": True,
    }


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
    user = result.get("user")
    if isinstance(user, str) and user.strip():
        resolved = resolve_slack_user(user, estelle_in_play=True, debug=debug)
        result["astral_candidate_id"] = resolved["astral_candidate_id"]
        result["candidate_state"] = resolved["state"]
        result["candidate_created"] = resolved["created"]
    else:
        result["astral_candidate_id"] = None
        result["candidate_state"] = None
        result["candidate_created"] = False
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
