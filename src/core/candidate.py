"""
Core candidate: candidate lifecycle management (AST-216).

In-scope: initiate_candidate, save_candidate_data, get_candidate,
transition_candidate_state, parse_candidate_resume, check_context_complete,
contact uniqueness enforcement on save (AST-1080).
All writes go through database.save_candidate (upsert); state transition logic lives here.

parse_candidate_resume is async (matching do_task convention). It is called from CLI/scripts,
never from Flask request handlers — AI calls don't belong in synchronous web requests.
"""

import asyncio
import copy
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from email.utils import parseaddr
from typing import Any, Dict, Optional, Tuple

from src.data import database
from src.core.agent import (
    _current_agent_task_run_next,
    compute_batch_cost,
    do_task,
    get_entity_response,
    preview_prompt,
    simulated_chain_context_for_preview,
)
from src.core import dispatcher as _dispatcher
from src.utils import rubric_text
from src.utils.config import (
    ASTRAL_CONFIG,
    BUILD_CONFIG,
    CANDIDATE_CONFIG,
    CANDIDATE_CONTACT_UNIQUENESS_CONFIG,
    CANDIDATE_LIBRARY_CONFIG,
    CANDIDATE_LOOKUP_CONFIG,
    TOPIC_MENU_CONFIG,
    CANDIDATE_STATES,
    CANDIDATE_STAGE_DISPATCH,
    CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY,
    CRAFT_RUBRIC_UI_TASK_KEYS,
    EMBEDDED_COMPANY_PREFILTER_CRITERIA,
    PRONOUN_PREFERENCE_DEFAULT,
    PRONOUN_PREFERENCE_OPTIONS,
    RESUME_STRUCTURE_CONTACT_SECTION_IDS,
    RESUME_STRUCTURE_DEFAULT,
    RESUME_STRUCTURE_KNOWN_SECTION_IDS,
    RUBRIC_CRITERIA_ARTIFACT_KEYS,
    RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY,
    rubric_owner_task_key,
)
from src.utils.logging import flush_log_buffer, get_logger, log_batch_id, truncate_debug_content

logger = get_logger(__name__)


_NAME_COLUMNS = CANDIDATE_LIBRARY_CONFIG["name_columns"]
_LIBRARY_BLOB_KEYS = ("contact", "context", "artifacts")


def build_candidate_token_view(candidate: dict) -> dict:
    """Walkable dict for resolve_tokens: name columns + library blobs (no meta)."""
    cd = candidate.get("candidate_data") or {}
    if not isinstance(cd, dict):
        cd = {}
    return {
        "first": candidate.get("first") or "",
        "last": candidate.get("last") or "",
        "full": candidate.get("full") or "",
        "pronouns": candidate.get("pronouns") or "",
        "contact": cd.get("contact") if isinstance(cd.get("contact"), dict) else {},
        "context": cd.get("context") if isinstance(cd.get("context"), dict) else {},
        "artifacts": cd.get("artifacts") if isinstance(cd.get("artifacts"), dict) else {},
        "_astral_candidate_id": candidate.get("astral_candidate_id") or "",
    }


def recompute_full_name(first: str, last: str) -> str:
    join = CANDIDATE_LIBRARY_CONFIG["full_name_join"]
    parts = [p for p in ((first or "").strip(), (last or "").strip()) if p]
    return join.join(parts)


def normalize_contact_urls(contact: dict) -> None:
    """URL-or-username → URL for linkedin_url / github (mutates in place)."""
    if not isinstance(contact, dict):
        return
    for key, base in (
        ("linkedin_url", CANDIDATE_LIBRARY_CONFIG["linkedin_url_base"]),
        ("github", CANDIDATE_LIBRARY_CONFIG["github_url_base"]),
    ):
        raw = contact.get(key)
        if not isinstance(raw, str):
            continue
        val = raw.strip()
        if not val:
            continue
        if "://" in val:
            contact[key] = val
            continue
        handle = val.lstrip("@").strip()
        contact[key] = f"{base}{handle}" if handle else val


def _uniqueness_compare_token(raw: Any, mode: str) -> str:
    """Strip + compare-mode normalize for uniqueness tokens (AST-1080)."""
    if not isinstance(raw, str):
        return ""
    stripped = raw.strip()
    if not stripped:
        return ""
    if mode == "exact":
        return stripped
    return stripped.casefold()


def _iter_uniqueness_path_values(source: Dict[str, Any], dotted_path: str) -> list:
    """Raw stripped string values for one uniqueness path (scalar or list)."""
    cfg = CANDIDATE_CONTACT_UNIQUENESS_CONFIG
    # List-valued: non-email list_paths + email_list_paths (shared email pool).
    if dotted_path in cfg["list_paths"] or dotted_path in cfg["email_list_paths"]:
        parts = dotted_path.split(".")
        cur: Any = source.get("candidate_data") or {}
        if not isinstance(cur, dict):
            return []
        for seg in parts:
            if not isinstance(cur, dict):
                return []
            cur = cur.get(seg)
        out: list = []
        if isinstance(cur, list):
            for item in cur:
                if isinstance(item, str) and item.strip():
                    out.append(item.strip())
        elif isinstance(cur, str) and cur.strip():
            out.append(cur.strip())
        return out
    v = _lookup_path_value(source, dotted_path)
    return [v] if v else []


def _collect_uniqueness_tokens_from_candidate(candidate: Dict[str, Any]) -> list:
    """Return [(compare_token, path), ...] in config path order."""
    cfg = CANDIDATE_CONTACT_UNIQUENESS_CONFIG
    compare = cfg["compare"]
    out: list = []
    # Email pool first (scalars then list emails), then other identity groups.
    groups = (
        (cfg["email_paths"], compare["email"]),
        (cfg["email_list_paths"], compare["email"]),
        (cfg["scalar_paths"], compare["scalar"]),
        (cfg["list_paths"], compare["list"]),
        (cfg["slack_user_id_paths"], compare["slack_user_id"]),
    )
    for paths, mode in groups:
        for path in paths:
            for raw in _iter_uniqueness_path_values(candidate, path):
                tok = _uniqueness_compare_token(raw, mode)
                if tok:
                    out.append((tok, path))
    return out


def _collect_uniqueness_tokens_from_contact(contact: Dict[str, Any]) -> list:
    """Tokens from a bare contact dict (write-side proposed blob)."""
    return _collect_uniqueness_tokens_from_candidate(
        {"candidate_data": {"contact": contact}}
    )


def _dedupe_contact_list_path(
    contact: dict, path: str, mode: str, seen: set, notes: list
) -> None:
    """Keep-first rebuild for one contact.* list uniqueness path."""
    if not path.startswith("contact."):
        return
    key = path.split(".", 1)[1]
    raw_list = contact.get(key)
    if not isinstance(raw_list, list):
        return
    kept: list = []
    for item in raw_list:
        if not isinstance(item, str):
            kept.append(item)
            continue
        tok = _uniqueness_compare_token(item, mode)
        if not tok:
            kept.append(item)
            continue
        if tok in seen:
            notes.append(f"removed duplicate from {path}")
            continue
        seen.add(tok)
        kept.append(item)
    contact[key] = kept


def _dedupe_contact_within(contact: dict) -> list:
    """Collapse duplicate uniqueness tokens inside one contact blob (mutates)."""
    cfg = CANDIDATE_CONTACT_UNIQUENESS_CONFIG
    compare = cfg["compare"]
    seen: set = set()
    notes: list = []
    # Scalar / email / slack under contact.* — keep first, clear later dups.
    scalar_groups = (
        (cfg["email_paths"], compare["email"]),
        (cfg["scalar_paths"], compare["scalar"]),
        (cfg["slack_user_id_paths"], compare["slack_user_id"]),
    )
    for paths, mode in scalar_groups:
        for path in paths:
            if not path.startswith("contact."):
                continue
            key = path.split(".", 1)[1]
            raw = contact.get(key)
            tok = _uniqueness_compare_token(raw, mode)
            if not tok:
                continue
            if tok in seen:
                contact[key] = ""
                notes.append(f"cleared {path} (duplicate)")
            else:
                seen.add(tok)
    # Email list paths (extra_emails) then non-email lists (websites).
    for path in cfg["email_list_paths"]:
        _dedupe_contact_list_path(contact, path, compare["email"], seen, notes)
    for path in cfg["list_paths"]:
        _dedupe_contact_list_path(contact, path, compare["list"], seen, notes)
    return notes


def _find_cross_candidate_contact_collision(
    candidate_id: str, contact: dict
) -> Optional[Tuple[str, str, str]]:
    """Return (display_value, path, other_id) on first cross-candidate token hit."""
    mine = _collect_uniqueness_tokens_from_contact(contact)
    if not mine:
        return None
    mine_map = {tok: path for tok, path in mine}
    self_id = (candidate_id or "").strip()
    # Display values from this contact (path → first stripped raw).
    display_by_path: Dict[str, str] = {}
    for path in (
        tuple(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_paths"])
        + tuple(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_list_paths"])
        + tuple(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"])
        + tuple(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"])
        + tuple(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["slack_user_id_paths"])
    ):
        if not path.startswith("contact."):
            continue
        for raw in _iter_uniqueness_path_values(
            {"candidate_data": {"contact": contact}}, path
        ):
            display_by_path.setdefault(path, raw)
    for other in list_candidates(include_deleted=False):
        other_id = (other.get("astral_candidate_id") or "").strip()
        if not other_id or other_id == self_id:
            continue
        for tok, _opath in _collect_uniqueness_tokens_from_candidate(other):
            if tok not in mine_map:
                continue
            path = mine_map[tok]
            display = display_by_path.get(path) or tok
            return (display, path, other_id)
    return None


def _coerce_contact_string_lists(contact: dict) -> None:
    """Trim websites / extra_emails lists in place (AST-1081 / AST-1092 / AST-1095)."""
    for list_key in ("websites", "extra_emails"):
        if list_key not in contact:
            continue
        raw_list = contact[list_key]
        if raw_list is None:
            contact[list_key] = []
        elif isinstance(raw_list, list):
            contact[list_key] = [
                str(x).strip() for x in raw_list if str(x).strip()
            ]
        else:
            raise ValueError(f"contact.{list_key} must be a list of strings")


def _enforce_contact_uniqueness(
    candidate_id: str, contact: dict, *, debug: bool = False
) -> None:
    """Within-candidate collapse + cross-candidate hard-fail (AST-1080)."""
    notes = _dedupe_contact_within(contact)
    if debug:
        logger.debug_index(
            func="enforce_contact_uniqueness",
            index=1,
            total=2,
            identifier=candidate_id,
            outcome="recorded|within_dedupe" if notes else "found|within_clean",
        )
        if notes:
            for line in truncate_debug_content("; ".join(notes)):
                logger.debug_detail(f"within={line}")
        else:
            logger.debug_detail("within=clean")
        logger.debug_detail(
            f"token_count={len(_collect_uniqueness_tokens_from_contact(contact))}"
        )
    hit = _find_cross_candidate_contact_collision(candidate_id, contact)
    if hit:
        display, path, other_id = hit
        if debug:
            logger.debug_index(
                func="enforce_contact_uniqueness",
                index=2,
                total=2,
                identifier=candidate_id,
                outcome="found|cross_collision",
            )
            logger.debug_detail(f"path={path}")
            for line in truncate_debug_content(display):
                logger.debug_detail(f"value={line}")
            logger.debug_detail(f"other_candidate_id={other_id}")
        shown = display if len(display) <= 80 else display[:80]
        raise ValueError(
            f"This contact info is already used by another candidate ({shown})."
        )
    if debug:
        logger.debug_index(
            func="enforce_contact_uniqueness",
            index=2,
            total=2,
            identifier=candidate_id,
            outcome="recorded|cross_clear",
        )
        logger.debug_detail("cross=clear")


_PENDING_CRAFT_GENERATIONS_KEY = "pending_craft_generations"

def _ledger_task_key_for_ui_generate(task_key: str) -> str:
    return f"user-{task_key}"


def _is_craft_rubric_ui_task(task_key: str) -> bool:
    return task_key in CRAFT_RUBRIC_UI_TASK_KEYS


def _craft_rubric_criteria_count(parsed_response: Any) -> int:
    if isinstance(parsed_response, dict):
        return len(parsed_response.get("criteria") or [])
    return 0


def _stash_pending_craft_generation(
    candidate_id: str,
    task_key: str,
    batch_id: Optional[str],
    parsed_response: Any,
) -> bool:
    """Persist successful craft rubric generate for page-return recovery (not artifact Save).

    Returns True when the pending stash was written; False if the candidate is gone
    or save fails (caller must not return HTTP 200 / COMPLETED without a stash).
    """
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        logger.error(
            "pending craft stash skipped — candidate missing candidate_id=%s "
            "task_key=%r batch_id=%s",
            candidate_id,
            task_key,
            batch_id,
        )
        return False
    cd = candidate.get("candidate_data") or {}
    pending = dict(cd.get(_PENDING_CRAFT_GENERATIONS_KEY) or {})
    pending[task_key] = {
        "batch_id": batch_id,
        "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "parsed_response": parsed_response,
    }
    try:
        database.save_candidate(
            candidate_id,
            candidate_data={_PENDING_CRAFT_GENERATIONS_KEY: pending},
            merge=True,
        )
    except Exception as e:
        logger.error(
            "pending craft stash save failed candidate_id=%s task_key=%r "
            "batch_id=%s error=%s",
            candidate_id,
            task_key,
            batch_id,
            e,
        )
        return False
    return True


def _clear_pending_craft_generation(candidate_id: str, task_key: str) -> None:
    """Drop one task_key from pending_craft_generations (RMW — deep_merge cannot delete keys)."""
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return
    cd = dict(candidate.get("candidate_data") or {})
    pending = dict(cd.get(_PENDING_CRAFT_GENERATIONS_KEY) or {})
    if task_key not in pending:
        return
    pending.pop(task_key, None)
    if pending:
        cd[_PENDING_CRAFT_GENERATIONS_KEY] = pending
    else:
        cd.pop(_PENDING_CRAFT_GENERATIONS_KEY, None)
    database.save_candidate(candidate_id, candidate_data=cd, merge=False)


def _normalize_importance_value(raw: Any, ci: dict) -> int:
    """Coerce artifact criterion importance to int in [min, max]; default when missing."""
    default = int(ci["default_vector_importance"])
    lo, hi = int(ci["min"]), int(ci["max"])
    if raw is None:
        return default
    if isinstance(raw, bool):
        raise ValueError("importance must be an integer, not a boolean")
    if isinstance(raw, int):
        n = raw
    elif isinstance(raw, float):
        if not raw.is_integer():
            raise ValueError("importance must be a whole number")
        n = int(raw)
    elif isinstance(raw, str):
        s = raw.strip()
        if s.isdigit():
            n = int(s)
        else:
            raise ValueError("importance must be an integer from 1 to 10")
    else:
        raise ValueError("importance must be an integer from 1 to 10")
    if n < lo or n > hi:
        n = max(lo, min(hi, n))
    return n


def _append_candidate_state_history(
    candidate: Dict[str, Any],
    from_state: str,
    to_state: str,
    timestamp: str,
) -> list:
    """Return candidate state_history plus one company-shaped entry (no DB write)."""
    history = list(candidate.get("state_history") or [])
    history.append({
        "from_state": from_state,
        "to_state": to_state,
        "timestamp": timestamp,
        "batch_id": candidate.get("batch_id"),
    })
    return history


def initiate_candidate(
    astral_candidate_id: str,
    candidate_data: Optional[Dict[str, Any]] = None,
    *,
    first: Optional[str] = None,
    last: Optional[str] = None,
    full: Optional[str] = None,
    pronouns: Optional[str] = None,
) -> None:
    """Create a new candidate record with CANDIDATE_CONFIG initial_state."""
    initial = CANDIDATE_CONFIG["initial_state"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cd = dict(candidate_data or {})
    if "profile" in cd:
        raise ValueError("profile was renamed to contact; refuse shadow write")
    contact = cd.get("contact")
    if isinstance(contact, dict):
        _coerce_contact_string_lists(contact)
        normalize_contact_urls(contact)
        _enforce_contact_uniqueness(astral_candidate_id, contact, debug=False)
    first_v = "" if first is None else str(first)
    last_v = "" if last is None else str(last)
    full_v = full if full is not None else recompute_full_name(first_v, last_v)
    pronouns_v = ("" if pronouns is None else str(pronouns)).strip()
    if pronouns_v not in PRONOUN_PREFERENCE_OPTIONS:
        pronouns_v = PRONOUN_PREFERENCE_DEFAULT
    database.save_candidate(
        astral_candidate_id,
        state=initial,
        candidate_data=cd,
        first=first_v,
        last=last_v,
        full=full_v,
        pronouns=pronouns_v,
        state_history=_append_candidate_state_history({}, "", initial, now),
    )



def initiate_prospect_candidate(
    astral_candidate_id: str,
    candidate_data: Optional[Dict[str, Any]] = None,
    *,
    first: Optional[str] = None,
    last: Optional[str] = None,
) -> None:
    """Create a candidate row in PROSPECT (Slack create-on-miss). Not NEW_CANDIDATE."""
    cid = (astral_candidate_id or "").strip()
    if not cid:
        raise ValueError("astral_candidate_id is required")
    if get_candidate(cid) is not None:
        raise ValueError(f"candidate already exists: {cid}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cd = dict(candidate_data or {})
    if "profile" in cd:
        raise ValueError("profile was renamed to contact; refuse shadow write")
    contact = cd.get("contact")
    if isinstance(contact, dict):
        _coerce_contact_string_lists(contact)
        normalize_contact_urls(contact)
        _enforce_contact_uniqueness(astral_candidate_id, contact, debug=False)
    first_v = "" if first is None else str(first)
    last_v = "" if last is None else str(last)
    full_v = recompute_full_name(first_v, last_v)
    database.save_candidate(
        cid,
        state="PROSPECT",
        candidate_data=cd,
        first=first_v,
        last=last_v,
        full=full_v,
        pronouns=PRONOUN_PREFERENCE_DEFAULT,
        state_history=_append_candidate_state_history({}, "", "PROSPECT", now),
    )


def save_candidate_data(
    candidate_id: str,
    data: Dict[str, Any],
    replace: bool = False,
    *,
    debug: bool = False,
) -> None:
    """Merge (or replace) library blobs + optional name columns (AST-1014).
    Pure data persistence — no AI calls. Rejects legacy ``profile`` writes."""
    logger.set_debug_flag(debug)
    if not isinstance(data, dict):
        raise ValueError("candidate data must be a dict")
    if "profile" in data:
        raise ValueError("profile was renamed to contact; refuse shadow write")

    col_kwargs: Dict[str, Any] = {}
    blob: Dict[str, Any] = {}
    for key, val in data.items():
        if key in _NAME_COLUMNS:
            col_kwargs[key] = "" if val is None else str(val)
        else:
            blob[key] = val

    if "first" in col_kwargs or "last" in col_kwargs:
        if "full" not in col_kwargs:
            # Merge with existing columns when only one side provided
            existing = database.get_candidate(candidate_id) or {}
            first = col_kwargs.get("first", existing.get("first") or "")
            last = col_kwargs.get("last", existing.get("last") or "")
            col_kwargs["full"] = recompute_full_name(str(first), str(last))

    if "pronouns" in col_kwargs:
        pref = (col_kwargs["pronouns"] or "").strip()
        if pref and pref not in PRONOUN_PREFERENCE_OPTIONS:
            raise ValueError(f"Invalid pronouns value: {pref!r}")

    contact = blob.get("contact")
    if isinstance(contact, dict):
        # Coerce websites / extra_emails (AST-1081 / AST-1092 / AST-1095).
        _coerce_contact_string_lists(contact)
        normalize_contact_urls(contact)
        # Proposed contact after merge (merge=True) or replace payload (merge=False).
        if not replace:
            existing = database.get_candidate(candidate_id) or {}
            existing_cd = existing.get("candidate_data") or {}
            if not isinstance(existing_cd, dict):
                existing_cd = {}
            existing_contact = existing_cd.get("contact")
            if isinstance(existing_contact, dict):
                proposed = copy.deepcopy(existing_contact)
                # Match database._deep_merge overwrite/list-replace for contact keys.
                for k, v in contact.items():
                    if (
                        k in proposed
                        and isinstance(proposed[k], dict)
                        and isinstance(v, dict)
                    ):
                        inner = copy.deepcopy(proposed[k])
                        for ik, iv in v.items():
                            inner[ik] = iv
                        proposed[k] = inner
                    else:
                        proposed[k] = v
            else:
                proposed = copy.deepcopy(contact)
        else:
            proposed = copy.deepcopy(contact)
        _enforce_contact_uniqueness(candidate_id, proposed, debug=debug)
        blob["contact"] = proposed

    steps = []
    if col_kwargs:
        steps.append(("columns", sorted(col_kwargs.keys())))
    for bk in _LIBRARY_BLOB_KEYS:
        if bk in blob:
            steps.append((bk, "recorded"))
    meta_keys = [k for k in blob if k not in _LIBRARY_BLOB_KEYS]
    if meta_keys:
        steps.append(("meta", meta_keys))

    if debug and steps:
        total = len(steps)
        for i, (label, detail) in enumerate(steps, start=1):
            logger.debug_index(
                func="save_candidate_data",
                index=i,
                total=total,
                identifier=candidate_id,
                outcome=f"recorded|{label}",
            )
            logger.debug_detail(f"{label}={detail!r}")

    save_kwargs: Dict[str, Any] = dict(col_kwargs)
    if blob:
        save_kwargs["candidate_data"] = blob
        save_kwargs["merge"] = not replace
    elif col_kwargs:
        pass
    else:
        return
    database.save_candidate(candidate_id, **save_kwargs)


def _topic_menu_key() -> str:
    return str(TOPIC_MENU_CONFIG["candidate_data_key"])


def empty_topic_menu() -> dict:
    """Empty Topic Menu envelope (AST-1074)."""
    return {"topics": []}


def normalize_topic_menu(raw: Any) -> dict:
    """Coerce stored/raw menu to ``{"topics": list}`` without validating members."""
    if not isinstance(raw, dict):
        return empty_topic_menu()
    topics = raw.get("topics")
    if not isinstance(topics, list):
        return empty_topic_menu()
    out: dict = {"topics": list(topics)}
    confirmed = raw.get("preamble_confirmed_at")
    if isinstance(confirmed, str) and confirmed.strip():
        out["preamble_confirmed_at"] = confirmed.strip()
    return out


def get_topic_menu(candidate_id: str) -> dict:
    """Load ``candidate_data.topic_menu`` (normalized). Raises if candidate missing."""
    cand = get_candidate(candidate_id)
    if not cand:
        raise ValueError(f"Candidate not found: {candidate_id}")
    cd = cand.get("candidate_data") or {}
    if not isinstance(cd, dict):
        cd = {}
    return normalize_topic_menu(cd.get(_topic_menu_key()))


def validate_topic(topic: Any) -> dict:
    """Return a normalized topic dict or raise ValueError."""
    if not isinstance(topic, dict):
        raise ValueError("topic must be a dict")
    tid = topic.get("id")
    if not isinstance(tid, str) or not tid.strip():
        raise ValueError("topic id must be a non-empty string")
    tid = tid.strip()
    name = topic.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"topic {tid!r}: name must be a non-empty string")
    name = name.strip()
    ask = topic.get("ask")
    if not isinstance(ask, str) or not ask.strip():
        raise ValueError(f"topic {tid!r}: ask must be a non-empty string")
    ask = ask.strip()
    required = topic.get("required")
    if not isinstance(required, bool):
        raise ValueError(f"topic {tid!r}: required must be a bool")
    informs_raw = topic.get("informs")
    if not isinstance(informs_raw, list) or not informs_raw:
        raise ValueError(f"topic {tid!r}: informs must be a non-empty list")
    allowed = TOPIC_MENU_CONFIG["informs"]
    seen: set = set()
    informs: list = []
    for item in informs_raw:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"topic {tid!r}: informs entries must be non-empty strings")
        key = item.strip()
        if key not in allowed:
            raise ValueError(f"topic {tid!r}: informs target {key!r} not in TOPIC_MENU_CONFIG")
        if key in seen:
            continue
        seen.add(key)
        informs.append(key)
    if not informs:
        raise ValueError(f"topic {tid!r}: informs must be non-empty after dedupe")
    status = topic.get("status", TOPIC_MENU_CONFIG["default_status"])
    if status not in TOPIC_MENU_CONFIG["statuses"]:
        raise ValueError(f"topic {tid!r}: status {status!r} not in TOPIC_MENU_CONFIG")
    return {
        "id": tid,
        "name": name,
        "ask": ask,
        "required": required,
        "informs": informs,
        "status": status,
    }


def validate_topic_menu(menu: Any) -> dict:
    """Validate a full menu; raise on duplicate topic ids."""
    normalized = normalize_topic_menu(menu)
    out: list = []
    seen_ids: set = set()
    for topic in normalized["topics"]:
        row = validate_topic(topic)
        if row["id"] in seen_ids:
            raise ValueError(f"duplicate topic id: {row['id']!r}")
        seen_ids.add(row["id"])
        out.append(row)
    result: dict = {"topics": out}
    if "preamble_confirmed_at" in normalized:
        result["preamble_confirmed_at"] = normalized["preamble_confirmed_at"]
    return result


def revise_topic_menu(existing: Any, incoming: Any) -> dict:
    """Merge incoming topics onto existing by id; missing ids become retired (no wipe)."""
    existing_n = validate_topic_menu(existing)
    incoming_n = validate_topic_menu(incoming)
    incoming_ids = {t["id"] for t in incoming_n["topics"]}
    out: list = []
    for topic in incoming_n["topics"]:
        out.append(topic)
    for topic in existing_n["topics"]:
        if topic["id"] in incoming_ids:
            continue
        retired = dict(topic)
        retired["status"] = "retired"
        out.append(retired)
    result: dict = {"topics": out}
    # Prefer incoming stamp when both set; else keep existing.
    if "preamble_confirmed_at" in incoming_n:
        result["preamble_confirmed_at"] = incoming_n["preamble_confirmed_at"]
    elif "preamble_confirmed_at" in existing_n:
        result["preamble_confirmed_at"] = existing_n["preamble_confirmed_at"]
    return result


def save_topic_menu(
    candidate_id: str,
    menu: Any,
    *,
    revise: bool = True,
    debug: bool = False,
) -> dict:
    """Persist Topic Menu under candidate_data; default revise keeps retired history."""
    logger.set_debug_flag(debug)
    current = get_topic_menu(candidate_id)
    if revise:
        to_store = revise_topic_menu(current, menu)
    else:
        to_store = validate_topic_menu(menu)

    if debug:
        cur_ids = [t.get("id") for t in current.get("topics") or [] if isinstance(t, dict)]
        logger.debug_index(
            func="candidate.save_topic_menu",
            index=1,
            total=2,
            identifier=candidate_id,
            outcome="found",
        )
        logger.debug_detail(f"current_count={len(cur_ids)} revise={revise}")
        id_blob = ",".join(str(x) for x in cur_ids)
        for line in truncate_debug_content(id_blob):
            logger.debug_detail(f"current_ids={line}")

    save_candidate_data(candidate_id, {_topic_menu_key(): to_store}, debug=debug)

    if debug:
        status_counts = {s: 0 for s in TOPIC_MENU_CONFIG["statuses"]}
        for t in to_store["topics"]:
            st = t.get("status")
            if st in status_counts:
                status_counts[st] += 1
        logger.debug_index(
            func="candidate.save_topic_menu",
            index=2,
            total=2,
            identifier=candidate_id,
            outcome="recorded",
        )
        logger.debug_detail(
            f"stored_count={len(to_store['topics'])} "
            f"open={status_counts['open']} ready={status_counts['ready']} "
            f"retired={status_counts['retired']} revise={revise}"
        )
    return to_store


def mark_topic_menu_preamble_confirmed(
    candidate_id: str,
    *,
    when: str | None = None,
    debug: bool = False,
) -> dict:
    """Stamp ``preamble_confirmed_at`` on topic_menu without wiping topics (AST-1075)."""
    logger.set_debug_flag(debug)
    menu = get_topic_menu(candidate_id)
    if debug:
        logger.debug_index(
            func="candidate.mark_topic_menu_preamble_confirmed",
            index=1,
            total=2,
            identifier=candidate_id,
            outcome="found",
        )
        logger.debug_detail(f"topics={len(menu.get('topics') or [])}")
    stamp = when or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    menu["preamble_confirmed_at"] = stamp
    save_candidate_data(candidate_id, {_topic_menu_key(): menu}, debug=debug)
    if debug:
        logger.debug_index(
            func="candidate.mark_topic_menu_preamble_confirmed",
            index=2,
            total=2,
            identifier=candidate_id,
            outcome="recorded",
        )
        logger.debug_detail(f"preamble_confirmed_at={stamp}")
    return menu


def normalize_rubric_artifacts_on_save(artifacts: dict) -> None:
    """For each rubric criteria artifact in ``artifacts``, parse trailing grade tables, set
    ``grade_descriptions``, and coerce ``importance`` (1–10). Mutates criterion dicts in place.
    Raises ``ValueError`` with a safe message if validation fails (caller → HTTP 400)."""
    if not isinstance(artifacts, dict):
        return
    ci = ASTRAL_CONFIG["consult_importance"]
    for key, val in artifacts.items():
        if key not in RUBRIC_CRITERIA_ARTIFACT_KEYS:
            continue
        if val is None:
            continue
        if not isinstance(val, list):
            raise ValueError(f"Artifact {key!r} must be a list of rubric criteria.")
        for idx, item in enumerate(val):
            if not isinstance(item, dict):
                raise ValueError(f"Artifact {key!r}: criterion {idx + 1} must be an object.")
            label = (item.get("label") or item.get("code") or "").strip() or f"#{idx + 1}"
            try:
                rubric_text.ensure_criterion_grade_table(item)
            except ValueError as e:
                raise ValueError(f"Rubric {key!r}, vector {label!r}: {e}") from e
            try:
                item["importance"] = _normalize_importance_value(item.get("importance"), ci)
            except ValueError as e:
                raise ValueError(f"Rubric {key!r}, vector {label!r}: {e}") from e


def _rubric_rows_to_criteria(rows: list) -> list:
    """Map rubric_vector DB rows to consult/UI criterion dicts (AST-723)."""
    out: list = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = {
            "code": row.get("code"),
            "label": row.get("label"),
            "content": row.get("content"),
            "importance": row.get("importance"),
        }
        try:
            rubric_text.ensure_criterion_grade_table(item)
        except ValueError:
            # Legacy/backfill rows may lack trailing grade tables; consult hydrates on demand.
            pass
        out.append(item)
    return out


def rubric_criteria_for_task(candidate_id: str, owner_task_key: str) -> list:
    """Active rubric criteria from rubric_vector for (candidate, owner task_key)."""
    if not candidate_id or not owner_task_key:
        return []
    rows = database.list_rubric_vectors(candidate_id, owner_task_key, current_only=True)
    criteria = _rubric_rows_to_criteria(rows)
    if owner_task_key == "prefilter_company":
        embedded_codes = {
            str(c.get("code")).strip().upper()
            for c in EMBEDDED_COMPANY_PREFILTER_CRITERIA
            if isinstance(c, dict) and c.get("code")
        }
        tail = [
            c
            for c in criteria
            if isinstance(c, dict) and str(c.get("code") or "").strip().upper() not in embedded_codes
        ]
        return list(EMBEDDED_COMPANY_PREFILTER_CRITERIA) + tail
    return criteria


def rubric_criteria_for_token(candidate_id: str, owner_task_key: str) -> list:
    """Token resolver entry — same list shape as rubric_criteria_for_task."""
    return rubric_criteria_for_task(candidate_id, owner_task_key)


def apply_rubric_vectors_save(candidate_id: str, artifacts: dict) -> None:
    """Sync rubric criteria artifacts to rubric_vector; drop keys from artifacts blob (AST-723).

    Legacy artifact purge: scripts/migrations/backfill_rubric_vectors.py --purge-artifacts
    --confirm-purge after AC#9 verify — not automatic here."""
    if not isinstance(artifacts, dict):
        return
    for key, val in list(artifacts.items()):
        if key not in RUBRIC_CRITERIA_ARTIFACT_KEYS:
            continue
        if val is None:
            continue
        owner = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(key)
        if not owner:
            raise ValueError(f"No rubric owner task_key for artifact {key!r}")
        if not isinstance(val, list):
            raise ValueError(f"Artifact {key!r} must be a list of rubric criteria.")
        database.sync_rubric_vectors_from_criteria(candidate_id, owner, val)
        del artifacts[key]


def hydrate_rubric_artifacts_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay table-backed rubric lists into GET response artifacts (display only)."""
    if not isinstance(cd, dict):
        return
    arts = cd.get("artifacts")
    if not isinstance(arts, dict):
        arts = {}
        cd["artifacts"] = arts
    for artifact_key, owner in RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.items():
        arts[artifact_key] = rubric_criteria_for_task(candidate_id, owner)


def _normalize_search_term_lines(val: str) -> list[str]:
    return [line for line in (s.strip() for s in val.split("\n")) if line]


def _company_search_terms_lines_from_string(val: str) -> list[str]:
    return _normalize_search_term_lines(val)


def normalize_company_search_terms_on_save(artifacts: dict) -> None:
    """Normalize artifacts.company_search_terms to trimmed non-empty lines joined by newline."""
    if not isinstance(artifacts, dict):
        return
    if "company_search_terms" not in artifacts:
        return
    val = artifacts["company_search_terms"]
    if val is None:
        return
    if not isinstance(val, str):
        raise ValueError("Artifact 'company_search_terms' must be a string.")
    normalized = "\n".join(_normalize_search_term_lines(val))
    if not normalized:
        raise ValueError("Artifact 'company_search_terms' must contain at least one non-empty search term.")
    artifacts["company_search_terms"] = normalized


def company_search_terms_lines(candidate_id: str) -> list[str]:
    """Table-backed search term lines (AST-525); artifact path removed."""
    return company_search_terms_lines_for_candidate(candidate_id)


def ensure_company_search_terms_table_synced(candidate_id: str) -> None:
    """Reconcile legacy artifact blob into table; strip blob after import (AST-802)."""
    database.reconcile_company_search_terms_from_artifact(candidate_id)
    candidate = get_candidate(candidate_id)
    if not candidate:
        return
    cd = copy.deepcopy(candidate.get("candidate_data") or {})
    arts = cd.get("artifacts")
    if not isinstance(arts, dict) or "company_search_terms" not in arts:
        return
    # Migration may import via nested reconcile in the same call stack — strip when table is authoritative.
    if not database.list_company_search_terms(candidate_id):
        return
    updated_arts = dict(arts)
    del updated_arts["company_search_terms"]
    cd["artifacts"] = updated_arts
    # replace=True — deep-merge cannot delete nested artifact keys (AST-802).
    save_candidate_data(candidate_id, cd, replace=True)


def company_search_terms_lines_for_candidate(candidate_id: str) -> list[str]:
    """Table-backed search term lines (AST-524)."""
    ensure_company_search_terms_table_synced(candidate_id)
    return [row["search_term"] for row in database.list_company_search_terms(candidate_id)]


def company_search_terms_joined_text(candidate_id: str) -> str:
    return "\n".join(company_search_terms_lines_for_candidate(candidate_id))


def sync_company_search_terms_from_text(candidate_id: str, text: str) -> None:
    """Normalize textarea content and upsert-and-delete table rows."""
    artifacts = {"company_search_terms": text}
    normalize_company_search_terms_on_save(artifacts)
    database.sync_company_search_terms(
        candidate_id,
        _normalize_search_term_lines(artifacts["company_search_terms"]),
    )


def apply_company_search_terms_save(candidate_id: str, artifacts: dict) -> None:
    """Sync table from artifacts.company_search_terms; stop persisting artifact blob."""
    if not isinstance(artifacts, dict) or "company_search_terms" not in artifacts:
        return
    text = artifacts["company_search_terms"]
    if text is None:
        return
    sync_company_search_terms_from_text(candidate_id, text)
    del artifacts["company_search_terms"]


def get_candidate(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Fetch candidate by ID. Needed because the API layer can't import database directly."""
    return database.get_candidate(candidate_id)


def list_candidates(include_deleted: bool = False) -> list:
    """Return all candidates. Filters out DELETED by default."""
    all_candidates = database.list_candidates()
    if include_deleted:
        return all_candidates
    return [c for c in all_candidates if c.get("state") != "DELETED"]


def _lookup_path_value(candidate: Dict[str, Any], dotted_path: str) -> str:
    """Resolve one CANDIDATE_LOOKUP_CONFIG path against a candidate row + candidate_data."""
    parts = dotted_path.split(".")
    if len(parts) == 1:
        val = candidate.get(parts[0])
    else:
        cur: Any = candidate.get("candidate_data") or {}
        if not isinstance(cur, dict):
            return ""
        for seg in parts:
            if not isinstance(cur, dict):
                return ""
            cur = cur.get(seg)
        val = cur
    if not isinstance(val, str):
        return ""
    return val.strip()


def get_candidate_id_for_query(
    query: str,
    *,
    debug: bool = False,
) -> Optional[str]:
    """Match a string against configured email/name homes; return id only on unique hit."""
    if debug:
        logger.set_debug_flag(True)

    raw = (query or "").strip()
    if not raw:
        if debug:
            logger.debug_index(
                func="get_candidate_id_for_query",
                index=1,
                total=1,
                identifier="",
                outcome="found|empty_query",
            )
            logger.debug_detail("query=")
            logger.debug_detail("needle=")
        return None

    _display, parsed_email = parseaddr(raw)
    addr = (parsed_email or "").strip()
    needle = addr if "@" in addr else raw
    casefold = bool(CANDIDATE_LOOKUP_CONFIG["match_casefold"])
    needle_cmp = needle.casefold() if casefold else needle

    hit_ids: set[str] = set()
    paths = (
        tuple(CANDIDATE_LOOKUP_CONFIG["email_paths"])
        + tuple(CANDIDATE_LOOKUP_CONFIG["name_paths"])
        + tuple(CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"])
    )
    for candidate in list_candidates(include_deleted=False):
        values = []
        for path in paths:
            v = _lookup_path_value(candidate, path)
            if v:
                values.append(v.casefold() if casefold else v)
        if needle_cmp not in values:
            continue
        cid = (candidate.get("astral_candidate_id") or "").strip()
        if cid:
            hit_ids.add(cid)

    if len(hit_ids) == 1:
        matched_id = next(iter(hit_ids))
        if debug:
            ident = next(iter(truncate_debug_content(needle)), needle[:80])
            logger.debug_index(
                func="get_candidate_id_for_query",
                index=1,
                total=1,
                identifier=ident,
                outcome="found|matched",
            )
            for line in truncate_debug_content(raw):
                logger.debug_detail(f"query={line}")
            for line in truncate_debug_content(needle):
                logger.debug_detail(f"needle={line}")
            logger.debug_detail(f"candidate_id={matched_id}")
        return matched_id

    if debug:
        ident = next(iter(truncate_debug_content(needle)), needle[:80])
        outcome = "found|ambiguous" if len(hit_ids) >= 2 else "found|none"
        logger.debug_index(
            func="get_candidate_id_for_query",
            index=1,
            total=1,
            identifier=ident,
            outcome=outcome,
        )
        for line in truncate_debug_content(raw):
            logger.debug_detail(f"query={line}")
        for line in truncate_debug_content(needle):
            logger.debug_detail(f"needle={line}")
        if len(hit_ids) >= 2:
            logger.debug_detail(f"candidate_ids={sorted(hit_ids)}")
    return None


def preview_task_prompt(
    task_key: str,
    candidate_id: str = "",
    *,
    astral_job_id: Optional[str] = None,
    chain_sim_enabled: bool = False,
    chain_simulate_parent: Optional[str] = None,
    chain_simulate_parsed: Optional[str] = None,
    chain_overrides: Optional[Dict[str, str]] = None,
) -> dict:
    """Preview resolved prompt text for a task. Uses candidate_id if provided,
    otherwise falls back to the first active candidate.

    When ``chain_sim_enabled`` is true and a parent task key or per-key overrides
    are supplied, builds the same synthesized ``chain_context`` as multi-hop previews (AST-455)."""
    if candidate_id:
        candidate = get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_id}")
    else:
        candidates = list_candidates()
        if not candidates:
            raise ValueError("No active candidate found for preview.")
        candidate = candidates[0]
    cd = candidate.get("candidate_data") or {}
    cid = candidate.get("astral_candidate_id") or candidate_id
    jc: Optional[Dict[str, str]] = None
    if astral_job_id and str(astral_job_id).strip():
        job = database.get_job(str(astral_job_id).strip())
        if not job:
            raise ValueError(f"Job not found: {astral_job_id}")
        from src.core.consult import build_job_token_context

        jc = build_job_token_context(job, cd, candidate_id=cid or "")
    if cid:
        joined = company_search_terms_joined_text(cid)
        cd = dict(cd)
        cd["_astral_candidate_id"] = cid
        arts = dict(cd.get("artifacts") or {})
        arts["company_search_terms"] = joined
        cd["artifacts"] = arts
    synthesized_chain: Optional[Dict[str, str]] = None
    if chain_sim_enabled and (
        (chain_simulate_parent and chain_simulate_parent.strip())
        or (chain_overrides and len(chain_overrides) > 0)
    ):
        synthesized_chain = {}
        if chain_simulate_parent and chain_simulate_parent.strip():
            synthesized_chain.update(
                simulated_chain_context_for_preview(
                    chain_simulate_parent.strip(),
                    cd,
                    chain_simulate_parsed,
                    job_context=jc,
                )
            )
        if chain_overrides:
            synthesized_chain.update(chain_overrides)
    result = preview_prompt(task_key, cd, chain_context=synthesized_chain, job_context=jc)
    result["candidate_id"] = candidate.get("astral_candidate_id", "")
    return result


def delete_candidate(candidate_id: str) -> None:
    """Logical delete — transition to DELETED (starts reap timer)."""
    transition_candidate_state(candidate_id, "DELETED")


def _candidate_prior_states(to_state: str):
    cfg = CANDIDATE_STATES.get(to_state)
    if cfg is None:
        raise ValueError(f"Unknown candidate state: {to_state}")
    return cfg.get("prior_states")


def _candidate_state_allowed(from_state: str, to_state: str) -> bool:
    prior = _candidate_prior_states(to_state)
    if prior is None:
        return True
    return from_state in prior


def _start_candidate_reap_timer(candidate_id: str) -> None:
    hours = int(CANDIDATE_STATES["DELETED"]["reap_after_hours"])
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    database.save_candidate(
        candidate_id,
        candidate_data={
            "lifecycle": {"reap_after_hours": hours, "reap_started_at": started},
        },
        merge=True,
    )


def _parse_utc_ts(raw: Any) -> Optional[datetime]:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    # Accept "Z" and space-separated SQLite timestamps
    s = s.replace(" ", "T")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def candidate_reap_due_at(candidate: dict) -> Optional[datetime]:
    """UTC due datetime when state is DELETED and lifecycle.reap_started_at is set."""
    if (candidate.get("state") or "") != "DELETED":
        return None
    life = ((candidate.get("candidate_data") or {}).get("lifecycle") or {})
    started = _parse_utc_ts(life.get("reap_started_at"))
    if started is None:
        return None
    hours = life.get("reap_after_hours")
    if hours is None:
        hours = CANDIDATE_STATES["DELETED"].get("reap_after_hours", 0)
    try:
        hours_i = int(hours)
    except (TypeError, ValueError):
        return None
    return started + timedelta(hours=hours_i)


def is_candidate_reap_due(candidate: dict, *, now: Optional[datetime] = None) -> bool:
    """True when DELETED and now >= candidate_reap_due_at."""
    due = candidate_reap_due_at(candidate)
    if due is None:
        return False
    clock = now if now is not None else datetime.now(timezone.utc)
    if clock.tzinfo is None:
        clock = clock.replace(tzinfo=timezone.utc)
    return clock.astimezone(timezone.utc) >= due


def hard_delete_candidate(candidate_id: str) -> Dict[str, int]:
    """Physical delete — database.hard_delete_candidate. Not a state transition."""
    return database.hard_delete_candidate(candidate_id)


def purge_reap_due_candidates(*, now: Optional[datetime] = None) -> int:
    """Hard-delete every candidate where is_candidate_reap_due(...). Return count."""
    n = 0
    for row in list_candidates(include_deleted=True):
        if (row.get("state") or "") != "DELETED":
            continue
        if not is_candidate_reap_due(row, now=now):
            continue
        cid = row.get("astral_candidate_id")
        if not cid:
            continue
        hard_delete_candidate(cid)
        n += 1
    return n


def transition_candidate_state(candidate_id: str, to_state: str) -> None:
    """Validate prior_states on CANDIDATE_STATES, then update state.
    Raises ValueError if the hop is disallowed."""
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        raise ValueError(f"Candidate not found: {candidate_id}")
    if to_state not in CANDIDATE_STATES:
        raise ValueError(f"Unknown candidate state: {to_state}")
    from_state = candidate["state"]
    if not _candidate_state_allowed(from_state, to_state):
        raise ValueError(
            f"Invalid candidate state transition: {from_state} -> {to_state}"
        )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    history = _append_candidate_state_history(candidate, from_state, to_state, now)
    database.save_candidate(candidate_id, state=to_state, state_history=history)
    if to_state == "DELETED":
        _start_candidate_reap_timer(candidate_id)


_CONTEXT_TEXT_KEYS = ("strengths", "priorities", "deal_breakers", "backstory")


def check_context_complete(candidate_id: str) -> bool:
    """True when all four context text fields are non-empty (no state write).
    Already-advanced candidates (progress_rank >= ALL_TOPICS_READY) count as complete."""
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return False
    current_state = candidate.get("state", "")
    rank = int((CANDIDATE_STATES.get(current_state) or {}).get("progress_rank", -1))
    ready_rank = int(CANDIDATE_STATES["ALL_TOPICS_READY"]["progress_rank"])
    if rank >= ready_rank and rank >= 0:
        return True
    ctx = (candidate.get("candidate_data") or {}).get("context", {})
    for key in _CONTEXT_TEXT_KEYS:
        if not (ctx.get(key) or "").strip():
            return False
    return True


def age_stale_candidate_states(*, now: Optional[datetime] = None) -> int:
    """Move waiting-stage candidates past stale_after_hours into stale_state.
    Returns count of successful transitions. No scheduler wiring (AST-972)."""
    clock = now if now is not None else datetime.now(timezone.utc)
    if clock.tzinfo is None:
        clock = clock.replace(tzinfo=timezone.utc)
    clock = clock.astimezone(timezone.utc)
    moved = 0
    for row in list_candidates(include_deleted=False):
        state = row.get("state") or ""
        cfg = CANDIDATE_STATES.get(state) or {}
        stale_state = cfg.get("stale_state")
        hours = cfg.get("stale_after_hours")
        if not stale_state or hours is None:
            continue
        if state == stale_state:
            continue
        changed = _parse_utc_ts(row.get("state_changed_at"))
        if changed is None:
            continue
        try:
            hours_i = int(hours)
        except (TypeError, ValueError):
            continue
        if clock < changed + timedelta(hours=hours_i):
            continue
        cid = row.get("astral_candidate_id")
        if not cid:
            continue
        try:
            transition_candidate_state(cid, stale_state)
            moved += 1
        except ValueError:
            continue
    return moved


_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def default_resume_structure() -> dict:
    """Deep copy of config default section catalog for new or missing structure."""
    return copy.deepcopy(RESUME_STRUCTURE_DEFAULT)


def normalize_resume_structure(raw: dict) -> dict:
    """Validate and coerce artifacts.resume_structure; raises ValueError on invalid input."""
    if not isinstance(raw, dict):
        raise ValueError("resume_structure must be a dict")
    sections_in = raw.get("sections")
    if not isinstance(sections_in, dict) or not sections_in:
        raise ValueError("resume_structure.sections must be a non-empty dict")
    palette = {c.upper() for c in (BUILD_CONFIG.get("accent_palette") or [])}
    out: Dict[str, Any] = {"sections": {}}
    if "accent_color" in raw and raw["accent_color"] is not None:
        ac = str(raw["accent_color"]).strip().upper()
        if not _HEX_COLOR_RE.match(ac):
            raise ValueError("resume_structure.accent_color must be #RRGGBB")
        if ac not in palette:
            raise ValueError("resume_structure.accent_color not in accent_palette")
        out["accent_color"] = ac
    for sid, spec in sections_in.items():
        if sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS:
            raise ValueError(f"unknown resume section id: {sid}")
        if not isinstance(spec, dict):
            raise ValueError(f"section {sid} must be a dict")
        sec_id = str(spec.get("id") or sid).strip()
        if sec_id != sid:
            raise ValueError(f"section id mismatch for key {sid}")
        title = spec.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"section {sid} requires non-empty title")
        enabled = spec.get("enabled")
        if not isinstance(enabled, bool):
            raise ValueError(f"section {sid} enabled must be boolean")
        order = spec.get("order")
        if not isinstance(order, int):
            raise ValueError(f"section {sid} order must be int")
        job_ed = spec.get("job_agent_editable")
        if not isinstance(job_ed, bool):
            raise ValueError(f"section {sid} job_agent_editable must be boolean")
        out["sections"][sid] = {
            "id": sid,
            "title": title.strip(),
            "enabled": enabled,
            "order": order,
            "job_agent_editable": job_ed,
        }
    if not out["sections"]:
        raise ValueError("resume_structure must include at least one section")
    return out


def enabled_resume_structure_sections(resolved: dict) -> list:
    """Enabled sections as {id, label} sorted by order then id (read-only on resolved)."""
    sections = resolved.get("sections") if isinstance(resolved.get("sections"), dict) else {}
    enabled = [
        {"id": spec["id"], "label": spec["title"]}
        for spec in sections.values()
        if isinstance(spec, dict) and spec.get("enabled") and spec.get("id")
    ]
    order_by_id = {
        sid: (spec.get("order", 0) if isinstance(spec.get("order"), int) else 0)
        for sid, spec in sections.items()
        if isinstance(spec, dict)
    }
    enabled.sort(key=lambda s: (order_by_id.get(s["id"], 0), s["id"]))
    return enabled


def filter_base_resume_to_structure(content: dict, section_ids: set) -> dict:
    """Keep only section-id keys; drop accent_color and other non-section keys."""
    if not isinstance(content, dict):
        return {}
    out: Dict[str, Any] = {}
    for k, v in content.items():
        if k not in section_ids:
            continue
        if k == "experience" and _is_experience_job_array(v):
            out[k] = v
        elif isinstance(v, str):
            out[k] = v
        # else: drop unexpected shapes (do not str()-corrupt)
    return out


def format_base_resume_for_token(candidate_data: dict) -> str:
    """{$BASE_RESUME}: section-id-keyed JSON for agent prompts (AST-607), never markdown."""
    cd = candidate_data if isinstance(candidate_data, dict) else {}
    artifacts = cd.get("artifacts") if isinstance(cd.get("artifacts"), dict) else {}
    raw = artifacts.get("base_resume")
    structure = resolve_resume_structure(cd)
    sections = structure.get("sections") if isinstance(structure.get("sections"), dict) else {}
    section_ids = {
        sid for sid, spec in sections.items() if isinstance(spec, dict) and spec.get("id")
    }
    title_to_id = {
        (spec.get("title") or "").strip(): sid
        for sid, spec in sections.items()
        if isinstance(spec, dict) and spec.get("id")
    }
    if isinstance(raw, dict):
        payload = filter_base_resume_to_structure(raw, section_ids)
    elif isinstance(raw, list):
        legacy: dict[str, str] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            label = (item.get("label") or "").strip()
            sid = title_to_id.get(label)
            if not sid or sid not in section_ids:
                continue
            legacy[sid] = str(item.get("content") if item.get("content") is not None else "")
        payload = filter_base_resume_to_structure(legacy, section_ids)
    else:
        payload = {}
    return json.dumps(payload, indent=2) if payload else ""


def resolve_resume_structure(candidate_data: dict) -> dict:
    """Normalized structure from artifacts or default; legacy accent shim from base_resume."""
    cd = candidate_data if isinstance(candidate_data, dict) else {}
    artifacts = cd.get("artifacts") if isinstance(cd.get("artifacts"), dict) else {}
    raw = artifacts.get("resume_structure")
    if isinstance(raw, dict) and raw.get("sections"):
        try:
            return normalize_resume_structure(raw)
        except ValueError:
            # Corrupt or legacy blob: bounded fallback to default (see test_resolve_falls_back_to_default_when_invalid).
            pass
    resolved = default_resume_structure()
    br = artifacts.get("base_resume")
    if isinstance(br, dict):
        ac = br.get("accent_color")
        if isinstance(ac, str) and ac.strip():
            acu = ac.strip().upper()
            palette = {c.upper() for c in (BUILD_CONFIG.get("accent_palette") or [])}
            if _HEX_COLOR_RE.match(acu) and acu in palette:
                resolved["accent_color"] = acu
    return resolved


_CRAFT_RESUME_NESTED_CONTENT_KEYS = ("content", "text", "value", "body")
_CRAFT_RESUME_CONTENT_DICT_KEYS = ("content", "section_content", "base_resume")


def _is_experience_job_array(val: Any) -> bool:
    return isinstance(val, list) and all(isinstance(item, dict) for item in val)


# Public alias for tracker / builder (AST-996 / AST-997 / AST-998).
is_experience_job_array = _is_experience_job_array


def _coerce_resume_section_string(val: Any) -> Optional[str]:
    if _is_experience_job_array(val):
        return None
    if isinstance(val, str) and val.strip():
        return val
    if isinstance(val, list):
        lines = [str(item).strip() for item in val if item is not None and str(item).strip()]
        if lines:
            return "\n".join(lines)
    return None


def _flatten_craft_resume_section_strings(payload: dict) -> None:
    """Promote nested section strings onto top-level payload keys (mutates payload)."""
    if not isinstance(payload, dict):
        return
    raw_struct = payload.get("resume_structure")
    if not isinstance(raw_struct, dict):
        return
    # AST-1005: still promote content / direct keys when sections is missing (before default wipe).
    sections = raw_struct.get("sections")
    if not isinstance(sections, dict):
        sections = None

    def _promote(sid: str, val: Any) -> None:
        if sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS:
            return
        if sid == "experience" and _is_experience_job_array(payload.get(sid)):
            return
        if sid == "experience" and _is_experience_job_array(val):
            payload[sid] = val
            return
        if _coerce_resume_section_string(payload.get(sid)):
            return
        text = _coerce_resume_section_string(val)
        if text:
            payload[sid] = text

    nested = raw_struct.get("content")
    if isinstance(nested, dict):
        for sid, val in nested.items():
            _promote(sid, val)

    for nest_key in _CRAFT_RESUME_CONTENT_DICT_KEYS:
        block = payload.get(nest_key)
        if isinstance(block, dict):
            for sid, val in block.items():
                _promote(sid, val)

    # Direct keys on resume_structure (e.g. candidate_name) — not sections/content metadata.
    for sid in RESUME_STRUCTURE_KNOWN_SECTION_IDS:
        if sid in raw_struct:
            _promote(sid, raw_struct[sid])

    if sections is None:
        return
    for sid, spec in sections.items():
        if not isinstance(spec, dict) or not spec.get("enabled"):
            continue
        if _coerce_resume_section_string(payload.get(sid)):
            continue
        for ck in _CRAFT_RESUME_NESTED_CONTENT_KEYS:
            if ck not in spec:
                continue
            text = _coerce_resume_section_string(spec.get(ck))
            if text:
                payload[sid] = text
                break


def normalize_craft_resume_base_agent_payload(parsed: dict) -> None:
    """Before craft_resume_base schema validation: flatten nested section strings."""
    if not isinstance(parsed, dict):
        return
    payload = parsed.get("agent_payload")
    if payload is None and "resume_structure" in parsed:
        payload = parsed
    elif not isinstance(payload, dict):
        payload = parsed
    if isinstance(payload, dict):
        _flatten_craft_resume_section_strings(payload)
        raw_struct = payload.get("resume_structure")
        if not isinstance(raw_struct, dict) or not raw_struct.get("sections"):
            payload["resume_structure"] = default_resume_structure()


_DRAFT_JOB_RESUME_METADATA_KEYS = frozenset({"astral_job_id", "company", "title", "task_success"})
_DRAFT_JOB_RESUME_CONSULT_KEYS = frozenset(
    {"grades", "dealbreakers", "clarifications", "overall_assessment", "ja_notes"}
)
# Common LLM key aliases → candidate catalog section ids (AST-604).
_DRAFT_JOB_RESUME_SECTION_ALIASES = {
    "candidate_contact": "candidate_contact_detail",
}


def _apply_draft_job_resume_section_aliases(inner: dict) -> None:
    for alias, canonical in _DRAFT_JOB_RESUME_SECTION_ALIASES.items():
        if alias not in inner:
            continue
        alias_val = inner.pop(alias)
        if canonical not in inner or inner.get(canonical) in (None, ""):
            inner[canonical] = alias_val


def normalize_draft_job_resume_agent_payload(parsed: dict) -> None:
    """Before draft_job_resume validation: flatten nested/wrapped section strings (AST-594)."""
    if not isinstance(parsed, dict):
        return
    payload = parsed.get("agent_payload")
    if isinstance(payload, dict):
        inner = payload
    elif isinstance(parsed, dict):
        inner = parsed
    else:
        return
    if "resume_structure" in inner:
        _flatten_craft_resume_section_strings(inner)
    for nest_key in _CRAFT_RESUME_CONTENT_DICT_KEYS:
        block = inner.get(nest_key)
        if not isinstance(block, dict):
            continue
        for sid, val in block.items():
            if sid == "experience" and _is_experience_job_array(val):
                continue
            if _coerce_resume_section_string(inner.get(sid)):
                continue
            text = _coerce_resume_section_string(val)
            if text:
                inner[sid] = text
    for key, val in list(inner.items()):
        if key in _DRAFT_JOB_RESUME_METADATA_KEYS or key == "resume_structure":
            continue
        if key == "experience" and _is_experience_job_array(val):
            continue
        if isinstance(val, (list, dict)):
            text = _coerce_resume_section_string(val)
            if text:
                inner[key] = text
    _apply_draft_job_resume_section_aliases(inner)


def pin_experience_job_facts_from_base(payload: dict, candidate_data: dict) -> None:
    """Restore company/title/dates/location from base jobs matched by (company, title)."""
    if not isinstance(payload, dict) or not isinstance(candidate_data, dict):
        return
    artifacts = candidate_data.get("artifacts")
    base = artifacts.get("base_resume") if isinstance(artifacts, dict) else None
    if not isinstance(base, dict):
        return
    base_exp = base.get("experience")
    tailored = payload.get("experience")
    if not _is_experience_job_array(base_exp) or not _is_experience_job_array(tailored):
        return
    unused = list(base_exp)
    for job in tailored:
        if not isinstance(job, dict):
            continue
        pair = (
            str(job.get("company") or "").strip().lower(),
            str(job.get("title") or "").strip().lower(),
        )
        match_i = None
        for i, base_job in enumerate(unused):
            if not isinstance(base_job, dict):
                continue
            base_pair = (
                str(base_job.get("company") or "").strip().lower(),
                str(base_job.get("title") or "").strip().lower(),
            )
            if base_pair == pair:
                match_i = i
                break
        if match_i is None:
            continue
        base_job = unused.pop(match_i)
        for field in ("company", "title", "dates", "location"):
            if field in base_job:
                job[field] = base_job[field]
            elif field == "location":
                job[field] = ""


def validate_draft_job_resume_payload(parsed: dict, candidate_data: dict) -> Optional[str]:
    """Catalog whitelist for draft_job_resume section keys; all sections optional."""
    normalize_draft_job_resume_agent_payload(parsed)
    payload = parsed.get("agent_payload") if isinstance(parsed.get("agent_payload"), dict) else parsed
    if not isinstance(payload, dict):
        return "agent_payload must be a dict"
    structure = resolve_resume_structure(candidate_data)
    allowed = set(enabled_resume_section_ids(structure))
    if not allowed:
        return "candidate has no enabled resume sections"
    for key, val in payload.items():
        if key in _DRAFT_JOB_RESUME_METADATA_KEYS or key == "resume_structure":
            continue
        if key in _DRAFT_JOB_RESUME_CONSULT_KEYS:
            return f"Unknown or disallowed field '{key}' on draft_job_resume"
        if key not in allowed:
            return f"Unknown resume section key '{key}' (not in candidate catalog: {sorted(allowed)})"
        if val is None or val == "":
            continue
        if key == "experience":
            if _is_experience_job_array(val):
                for job in val:
                    if not isinstance(job, dict):
                        return "Section 'experience' must be a job array or prose string"
                    if not isinstance(job.get("location"), str):
                        job["location"] = "" if job.get("location") is None else str(job.get("location") or "")
                continue
            if isinstance(val, str):
                continue
            if isinstance(val, (list, dict)):
                return "Section 'experience' must be a job array or prose string"
        text = _coerce_resume_section_string(val)
        if text is None:
            return f"Section '{key}' must be prose text (string or coercible list)"
        if text != val:
            payload[key] = text
    pin_experience_job_facts_from_base(payload, candidate_data)
    return None


def split_craft_resume_base_payload(parsed: dict) -> tuple[dict, dict]:
    """Split craft_resume_base agent JSON into (structure, content) for persistence."""
    if not isinstance(parsed, dict):
        raise ValueError("parsed craft_resume_base payload must be a dict")
    _flatten_craft_resume_section_strings(parsed)
    raw_struct = parsed.get("resume_structure")
    if isinstance(raw_struct, dict) and raw_struct.get("sections"):
        structure = normalize_resume_structure(raw_struct)
    else:
        structure = default_resume_structure()
    enabled_ids = {
        sid for sid, spec in structure["sections"].items() if spec.get("enabled")
    }
    content: Dict[str, Any] = {}
    for key in enabled_ids:
        if key not in parsed:
            continue
        val = parsed[key]
        if key == "experience" and _is_experience_job_array(val):
            content[key] = val
        elif isinstance(val, str):
            content[key] = val
    return structure, content


def enabled_resume_section_ids(resume_structure: dict) -> list[str]:
    """Enabled section ids sorted by catalog order ascending."""
    sections = (resume_structure or {}).get("sections") or {}
    if not isinstance(sections, dict):
        return []
    rows = [spec for spec in sections.values() if isinstance(spec, dict) and spec.get("enabled")]
    rows.sort(key=lambda s: int(s.get("order", 0)))
    return [str(s["id"]) for s in rows if s.get("id")]


def resume_section_titles(resume_structure: dict) -> dict[str, str]:
    """Display title per enabled section id."""
    titles: Dict[str, str] = {}
    for sid in enabled_resume_section_ids(resume_structure):
        spec = (resume_structure.get("sections") or {}).get(sid) or {}
        titles[sid] = str(spec.get("title") or sid.replace("_", " ").title())
    return titles


def filter_content_to_resume_structure(
    content: dict,
    resume_structure: dict,
    *,
    allow_contact: bool = True,
) -> dict:
    """Keep values for enabled section ids; omit empty strings / empty job arrays."""
    if not isinstance(content, dict):
        return {}
    allowed = set(enabled_resume_section_ids(resume_structure))
    if not allow_contact:
        allowed -= set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
    out: Dict[str, Any] = {}
    for key in allowed:
        val = content.get(key)
        if key == "experience" and _is_experience_job_array(val) and val:
            out[key] = val
        elif isinstance(val, str) and val.strip():
            out[key] = val
    return out


async def parse_candidate_resume(candidate_id: str, *, debug: bool = False) -> Dict[str, Any]:
    """Parse context.raw_resume via do_task('craft_resume_base').
    Reads from candidate_data.context.raw_resume, writes parsed
    result to candidate_data.artifacts.base_resume.
    Does not change candidate state (AST-970 — no PROFILE_READY auto-hop).

    Async — called from CLI/scripts via asyncio.run(), never from Flask handlers."""
    logger.set_debug_flag(debug)
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return {"success": False, "error": f"Candidate not found: {candidate_id}"}
    resume_raw = (candidate.get("candidate_data") or {}).get("context", {}).get("raw_resume", "")
    if not resume_raw or not resume_raw.strip():
        return {"success": False, "error": "No raw_resume in candidate_data.context"}

    response = await do_task(
        task_key="craft_resume_base",
        live_content=resume_raw,
        index=candidate_id,
        debug=debug,
    )
    if response is None:
        return {"success": False, "error": "do_task returned None for parse_resume"}
    if not response.get("success"):
        return {"success": False, "error": response.get("error", "parse_resume failed"), "raw_response": response.get("raw_response")}

    parsed = response.get("parsed_response")
    if parsed is None:
        return {"success": False, "error": "parse_resume returned None parsed_response"}

    structure, content = split_craft_resume_base_payload(parsed)
    database.save_candidate(
        candidate_id,
        candidate_data={"artifacts": {"resume_structure": structure, "base_resume": content}},
        merge=True,
    )
    if debug:
        logger.debug_index(
            func="parse_candidate_resume",
            index=1,
            total=1,
            identifier=candidate_id,
            outcome="ok",
        )
        _debug_experience_jobs(logger, content)
    return {"success": True, "parsed": parsed}


def _debug_experience_jobs(log, content_or_parsed: Any) -> None:
    """Style D detail for recorded experience jobs (AST-996)."""
    blob = content_or_parsed if isinstance(content_or_parsed, dict) else {}
    exp = blob.get("experience")
    if _is_experience_job_array(exp):
        for i, job in enumerate(exp):
            if not isinstance(job, dict):
                log.debug_detail(f"experience[{i}] shape=non_dict")
                continue
            log.debug_detail(
                f"experience[{i}] company={job.get('company')!r} title={job.get('title')!r} "
                f"dates={job.get('dates')!r} location={job.get('location')!r}"
            )
            acc = job.get("accomplishments")
            if isinstance(acc, str) and acc.strip():
                for line in truncate_debug_content(acc):
                    log.debug_detail(f"experience[{i}] accomplishments: {line}")
            else:
                log.debug_detail(f"experience[{i}] accomplishments=<empty>")
        return
    if isinstance(exp, str):
        log.debug_detail("experience_shape=str")
    elif exp is None:
        log.debug_detail("experience_shape=missing")
    else:
        log.debug_detail(f"experience_shape=other type={type(exp).__name__}")


# Public alias for agent tailor hops (AST-997).
debug_experience_jobs = _debug_experience_jobs


def save_candidate_admin(candidate_id: str, **kwargs: Any) -> None:
    """Direct candidate row updates from admin API (state override, api_key, etc.)."""
    database.save_candidate(candidate_id, **kwargs)


def clear_candidate_api_key(candidate_id: str) -> None:
    database.clear_candidate_api_key(candidate_id)


def get_pending_craft_generation(
    candidate_id: str,
    task_key: str,
) -> Tuple[Dict[str, Any], int]:
    """Recover last successful craft_*_rubric generate: pending stash, else ledger+agent_data."""
    if not _is_craft_rubric_ui_task(task_key):
        return ({"error": "Not a craft rubric task"}, 400)
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return ({"error": f"Candidate not found: {candidate_id}"}, 404)

    # AST-905: do not recover over an already-populated stored rubric
    owner = rubric_owner_task_key(task_key)
    if owner:
        existing = rubric_criteria_for_task(candidate_id, owner)
        if isinstance(existing, list) and len(existing) > 0:
            return ({"error": "No recoverable generation"}, 404)

    cd = candidate.get("candidate_data") or {}
    pending = (cd.get(_PENDING_CRAFT_GENERATIONS_KEY) or {}).get(task_key)
    if isinstance(pending, dict):
        parsed = pending.get("parsed_response")
        if _craft_rubric_criteria_count(parsed) > 0:
            return (
                {
                    "success": True,
                    "parsed_response": parsed,
                    "batch_id": pending.get("batch_id"),
                    "recovered": True,
                    "source": "pending_stash",
                },
                200,
            )

    # Fallback: newest COMPLETED user-{task_key} ledger + agent_data RESPONSE
    # Attribute lookup (not bound import) so monkeypatches on dispatcher.list_dispatch_ledger apply.
    rows = _dispatcher.list_dispatch_ledger(
        task_key=_ledger_task_key_for_ui_generate(task_key),
        candidate_id=candidate_id,
        status="COMPLETED",
    )
    if not rows:
        return ({"error": "No recoverable generation"}, 404)
    batch_id = rows[0].get("batch_id")
    if not batch_id:
        return ({"error": "No recoverable generation"}, 404)
    resp_row = get_entity_response(batch_id, candidate_id)
    if not resp_row:
        return ({"error": "No recoverable generation"}, 404)
    block = resp_row.get("block_data") or ""
    try:
        parsed = json.loads(block) if isinstance(block, str) else block
    except (json.JSONDecodeError, TypeError):
        return ({"error": "No recoverable generation"}, 404)
    if _craft_rubric_criteria_count(parsed) == 0:
        return ({"error": "No recoverable generation"}, 404)
    return (
        {
            "success": True,
            "parsed_response": parsed,
            "batch_id": batch_id,
            "recovered": True,
            "source": "ledger_agent_data",
        },
        200,
    )



def _persist_craft_dispatch_success(candidate_id: str, task_key: str, parsed: Any) -> None:
    """Persist craft success for REQUESTED_* dispatch (AST-972) — no nested ledger."""
    if task_key == "craft_resume_base":
        if not isinstance(parsed, dict):
            raise ValueError("craft_resume_base parsed_response must be a dict")
        structure, content = split_craft_resume_base_payload(parsed)
        database.save_candidate(
            candidate_id,
            candidate_data={"artifacts": {"resume_structure": structure, "base_resume": content}},
            merge=True,
        )
        return
    if task_key == "craft_company_search_terms":
        if not isinstance(parsed, dict):
            raise ValueError("craft_company_search_terms parsed_response must be a dict")
        terms = parsed.get("search_terms")
        if not isinstance(terms, str):
            raise ValueError("craft_company_search_terms search_terms must be a string")
        apply_company_search_terms_save(candidate_id, {"company_search_terms": terms})
        return
    artifact_key = CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.get(task_key)
    if artifact_key:
        if not isinstance(parsed, dict):
            raise ValueError(f"{task_key} parsed_response must be a dict")
        criteria = parsed.get("criteria")
        if not isinstance(criteria, list) or len(criteria) == 0:
            raise ValueError(f"{task_key} returned no criteria")
        arts = {artifact_key: criteria}
        normalize_rubric_artifacts_on_save(arts)
        apply_rubric_vectors_save(candidate_id, arts)
        return
    raise ValueError(f"unsupported craft task_key for dispatch persist: {task_key!r}")


def _requested_stage_failure_target(primary_state: str, current_state: str) -> str:
    """Primary → retry_state; already on retry (or other) → error_state."""
    cfg = CANDIDATE_STATES[primary_state]
    retry = cfg["retry_state"]
    error = cfg["error_state"]
    if current_state == primary_state:
        return retry
    return error


async def run_requested_resume_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
    """Claim worker: REQUESTED_RESUME → craft_resume_base → RESUME_READY / retry / error."""
    zero = {"total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0}
    logger.set_debug_flag(debug)
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return {**zero, "total_processed": 1, "total_errors": 1}
    stage = CANDIDATE_STAGE_DISPATCH["requested_resume"]
    primary = stage["trigger_state"]
    pass_state = stage["pass_state"]
    craft_key = stage["craft_task_key"]
    current = (candidate.get("state") or "").strip()
    live = ((candidate.get("candidate_data") or {}).get("context") or {}).get("raw_resume") or ""
    try:
        response = await do_task(
            task_key=craft_key,
            live_content=live,
            index=candidate_id,
            ctx=candidate,
            debug=debug,
        )
        if not response or not response.get("success"):
            raise RuntimeError(
                (response or {}).get("error") if response else "do_task returned None"
            )
        parsed = response.get("parsed_response")
        _persist_craft_dispatch_success(candidate_id, craft_key, parsed)
        transition_candidate_state(candidate_id, pass_state)
        return {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
    except Exception as e:
        logger.error("run_requested_resume_dispatch failed candidate_id=%s error=%s", candidate_id, e)
        target = _requested_stage_failure_target(primary, current)
        try:
            transition_candidate_state(candidate_id, target)
        except ValueError:
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}
        return {"total_processed": 1, "total_passed": 0, "total_failed": 1, "total_errors": 0}


async def run_requested_artifacts_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
    """Claim worker: REQUESTED_ARTIFACTS → sequential craft_* → ARTIFACTS_READY / retry / error."""
    zero = {"total_processed": 0, "total_passed": 0, "total_failed": 0, "total_errors": 0}
    logger.set_debug_flag(debug)
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return {**zero, "total_processed": 1, "total_errors": 1}
    stage = CANDIDATE_STAGE_DISPATCH["requested_artifacts"]
    primary = stage["trigger_state"]
    pass_state = stage["pass_state"]
    current = (candidate.get("state") or "").strip()
    try:
        for craft_key in stage["craft_task_keys"]:
            # Refresh ctx each hop so later crafts see earlier persists.
            candidate = database.get_candidate(candidate_id) or candidate
            response = await do_task(
                task_key=craft_key,
                live_content="",
                index=candidate_id,
                ctx=candidate,
                debug=debug,
            )
            if not response or not response.get("success"):
                raise RuntimeError(
                    (response or {}).get("error") if response else f"do_task None for {craft_key}"
                )
            _persist_craft_dispatch_success(candidate_id, craft_key, response.get("parsed_response"))
        transition_candidate_state(candidate_id, pass_state)
        return {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
    except Exception as e:
        logger.error("run_requested_artifacts_dispatch failed candidate_id=%s error=%s", candidate_id, e)
        target = _requested_stage_failure_target(primary, current)
        try:
            transition_candidate_state(candidate_id, target)
        except ValueError:
            return {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 1}
        return {"total_processed": 1, "total_passed": 0, "total_failed": 1, "total_errors": 0}


def run_session_resume_parse(
    resume_text: str,
    *,
    debug: bool = False,
) -> Tuple[Dict[str, Any], int]:
    """Parse pasted resume text via simple_resume_parse (Ruth / Little); no candidate bind/persist.

    Returns (json_body, http_status) for Admin session-resume paste (AST-986 / AST-1038).
    """
    if not isinstance(resume_text, str) or not resume_text.strip():
        return ({"success": False, "error": "resume_text is required"}, 400)

    logger.set_debug_flag(debug)
    paste = resume_text.strip()
    structure = default_resume_structure()
    # Synthetic token ctx only — no astral_candidate_id (do not load a real candidate).
    ctx = {
        "candidate_data": {
            "context": {"raw_resume": paste},
            "artifacts": {"resume_structure": structure},
        },
    }

    ledger_task_key = "user-session-parse-resume"
    batch_id = f"{ledger_task_key}-{uuid.uuid4()}"
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    database.save_dispatch_ledger(
        batch_id,
        ledger_task_key,
        "session",  # sentinel for Admin cost visibility — not an astral_candidate_id
        started_at,
        entity_type=None,
        batch_size=1,
    )
    log_batch_id.set(batch_id)
    try:
        try:
            result = asyncio.run(
                do_task(
                    task_key="simple_resume_parse",
                    live_content=paste,
                    index=batch_id,
                    ctx=ctx,
                    debug=debug,
                )
            )
        except Exception as e:
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                total_processed=1,
                total_failed=1,
            )
            logger.error(
                "session resume parse exception batch_id=%s error=%s",
                batch_id,
                e,
            )
            if debug:
                logger.debug_index(
                    func="run_session_resume_parse",
                    index=1,
                    total=1,
                    identifier=batch_id,
                    outcome="exception",
                )
                logger.debug_detail(str(e))
            return ({"success": False, "error": str(e), "batch_id": batch_id}, 500)

        completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if not result or not result.get("success"):
            err = (
                result.get("error", "Generation failed")
                if result
                else "do_task returned None"
            )
            total_cost = compute_batch_cost(batch_id)
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=completed_at,
                total_processed=1,
                total_passed=0,
                total_failed=1,
                total_cost=total_cost,
            )
            logger.error(
                "session resume parse failed batch_id=%s error=%s",
                batch_id,
                err,
            )
            if debug:
                logger.debug_index(
                    func="run_session_resume_parse",
                    index=1,
                    total=1,
                    identifier=batch_id,
                    outcome="failed",
                )
                logger.debug_detail(str(err))
            return ({"success": False, "error": err, "batch_id": batch_id}, 500)

        parsed = result.get("parsed_response")
        if not isinstance(parsed, dict):
            total_cost = compute_batch_cost(batch_id)
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=completed_at,
                total_processed=1,
                total_passed=0,
                total_failed=1,
                total_cost=total_cost,
            )
            err = "simple_resume_parse returned non-dict parsed_response"
            if debug:
                logger.debug_index(
                    func="run_session_resume_parse",
                    index=1,
                    total=1,
                    identifier=batch_id,
                    outcome="invalid payload",
                )
                logger.debug_detail(err)
            return ({"success": False, "error": err, "batch_id": batch_id}, 500)

        structure_out, content = split_craft_resume_base_payload(parsed)
        total_cost = compute_batch_cost(batch_id)
        database.update_dispatch_ledger(
            batch_id,
            status="COMPLETED",
            completed_at=completed_at,
            total_processed=1,
            total_passed=1,
            total_failed=0,
            total_cost=total_cost,
        )
        if debug:
            logger.debug_index(
                func="run_session_resume_parse",
                index=1,
                total=1,
                identifier=batch_id,
                outcome="ok",
            )
            _debug_experience_jobs(logger, content)
        return (
            {
                "success": True,
                "resume_structure": structure_out,
                "base_resume": content,
                "parsed_response": parsed,
                "batch_id": batch_id,
                "timesheet": result.get("timesheet", {}),
            },
            200,
        )
    finally:
        flush_log_buffer()
        log_batch_id.set(None)


def run_candidate_artifact_generation(
    candidate_id: str,
    task_key: str,
    live_content: Optional[str],
    debug: bool = False,
) -> Tuple[Dict[str, Any], int]:
    """Run a craft_* do_task with dispatch_ledger + log_batch_id; returns (json_body, http_status)."""
    logger.set_debug_flag(debug)
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return ({"error": f"Candidate not found: {candidate_id}"}, 404)

    skip_outer_ledger = bool(_current_agent_task_run_next(task_key))
    batch_id: Optional[str] = None
    if not skip_outer_ledger:
        ledger_task_key = _ledger_task_key_for_ui_generate(task_key)
        batch_id = f"{ledger_task_key}-{uuid.uuid4()}"
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        database.save_dispatch_ledger(
            batch_id,
            ledger_task_key,
            candidate_id,
            started_at,
            entity_type="candidate",
            batch_size=1,
        )
        log_batch_id.set(batch_id)
        logger.info(
            "UI generate started task_key=%r ledger_task_key=%s batch_id=%s candidate_id=%s",
            task_key,
            ledger_task_key,
            batch_id,
            candidate_id,
        )
    try:
        try:
            result = asyncio.run(
                do_task(
                    task_key=task_key,
                    live_content=live_content or "",
                    index=candidate_id,
                    ctx=candidate,
                    debug=debug,
                )
            )
        except Exception as e:
            if batch_id:
                database.update_dispatch_ledger(
                    batch_id,
                    status="FAILED",
                    completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    total_processed=1,
                    total_failed=1,
                )
            logger.error(
                "artifact generation exception task_key=%r batch_id=%s error=%s",
                task_key,
                batch_id or log_batch_id.get(),
                e,
            )
            return ({"success": False, "error": str(e)}, 500)

        completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        response_batch_id = batch_id or log_batch_id.get()
        if not result or not result.get("success"):
            err = (
                result.get("error", "Generation failed")
                if result
                else "do_task returned None"
            )
            logger.error(
                "artifact generation failed task_key=%r batch_id=%s error=%s",
                task_key,
                response_batch_id,
                err,
            )
            if batch_id:
                total_cost = compute_batch_cost(batch_id)
                database.update_dispatch_ledger(
                    batch_id,
                    status="FAILED",
                    completed_at=completed_at,
                    total_processed=1,
                    total_passed=0,
                    total_failed=1,
                    total_cost=total_cost,
                )
            return (
                {
                    "success": False,
                    "error": err,
                    "batch_id": response_batch_id,
                },
                500,
            )

        parsed_response = result.get("parsed_response")
        # Craft rubric: reject empty criteria; stash pending before ledger COMPLETED.
        criteria_count: Optional[int] = None
        if _is_craft_rubric_ui_task(task_key):
            criteria_count = _craft_rubric_criteria_count(parsed_response)
            if criteria_count == 0:
                if debug:
                    logger.debug_index(
                        func="run_candidate_artifact_generation",
                        index=1,
                        total=1,
                        identifier=task_key,
                        outcome="empty criteria",
                    )
                logger.error(
                    "craft rubric generate returned empty criteria task_key=%r batch_id=%s",
                    task_key,
                    response_batch_id,
                )
                if batch_id:
                    total_cost = compute_batch_cost(batch_id)
                    database.update_dispatch_ledger(
                        batch_id,
                        status="FAILED",
                        completed_at=completed_at,
                        total_processed=1,
                        total_passed=0,
                        total_failed=1,
                        total_cost=total_cost,
                    )
                return (
                    {
                        "success": False,
                        "error": "Generation returned no criteria",
                        "batch_id": response_batch_id,
                    },
                    500,
                )
            if not _stash_pending_craft_generation(
                candidate_id, task_key, response_batch_id, parsed_response
            ):
                if batch_id:
                    total_cost = compute_batch_cost(batch_id)
                    database.update_dispatch_ledger(
                        batch_id,
                        status="FAILED",
                        completed_at=completed_at,
                        total_processed=1,
                        total_passed=0,
                        total_failed=1,
                        total_cost=total_cost,
                    )
                return (
                    {
                        "success": False,
                        "error": "Generation completed but could not stash for recovery",
                        "batch_id": response_batch_id,
                    },
                    500,
                )
            if debug:
                logger.debug_index(
                    func="run_candidate_artifact_generation",
                    index=1,
                    total=1,
                    identifier=task_key,
                    outcome=f"criteria_count={criteria_count}",
                )
                logger.debug_detail_block(json.dumps(parsed_response))

        if batch_id:
            total_cost = compute_batch_cost(batch_id)
            database.update_dispatch_ledger(
                batch_id,
                status="COMPLETED",
                completed_at=completed_at,
                total_processed=1,
                total_passed=1,
                total_failed=0,
                total_cost=total_cost,
            )
            if criteria_count is not None:
                logger.info(
                    "UI generate completed task_key=%r batch_id=%s status=COMPLETED "
                    "cost=%s criteria_count=%s",
                    task_key,
                    batch_id,
                    total_cost,
                    criteria_count,
                )
            else:
                logger.info(
                    "UI generate completed task_key=%r batch_id=%s status=COMPLETED cost=%s",
                    task_key,
                    batch_id,
                    total_cost,
                )
        if task_key == "craft_resume_base" and parsed_response is not None:
            structure, content = split_craft_resume_base_payload(parsed_response)
            database.save_candidate(
                candidate_id,
                candidate_data={"artifacts": {"resume_structure": structure, "base_resume": content}},
                merge=True,
            )
            if debug:
                logger.debug_index(
                    func="run_candidate_artifact_generation",
                    index=1,
                    total=1,
                    identifier=task_key,
                    outcome="craft_resume_base persisted",
                )
                _debug_experience_jobs(logger, content)
        return (
            {
                "success": True,
                "parsed_response": parsed_response,
                "timesheet": result.get("timesheet", {}),
                "batch_id": response_batch_id,
            },
            200,
        )
    finally:
        flush_log_buffer()
        log_batch_id.set(None)
