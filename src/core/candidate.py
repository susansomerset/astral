"""
Core candidate: candidate lifecycle management (AST-216).

In-scope: initiate_candidate, save_candidate_data, get_candidate,
transition_candidate_state, parse_candidate_resume, check_context_complete.
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
    CANDIDATE_STATES,
    CANDIDATE_STAGE_DISPATCH,
    CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY,
    CRAFT_RUBRIC_UI_TASK_KEYS,
    EMBEDDED_COMPANY_PREFILTER_CRITERIA,
    RESUME_STRUCTURE_CONTACT_SECTION_IDS,
    RESUME_STRUCTURE_DEFAULT,
    RESUME_STRUCTURE_KNOWN_SECTION_IDS,
    RUBRIC_CRITERIA_ARTIFACT_KEYS,
    RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY,
    rubric_owner_task_key,
)
from src.utils.logging import flush_log_buffer, get_logger, log_batch_id

logger = get_logger(__name__)

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


def initiate_candidate(astral_candidate_id: str, candidate_data: Optional[Dict[str, Any]] = None) -> None:
    """Create a new candidate record with CANDIDATE_CONFIG initial_state."""
    initial = CANDIDATE_CONFIG["initial_state"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    database.save_candidate(
        astral_candidate_id,
        state=initial,
        candidate_data=candidate_data or {},
        state_history=_append_candidate_state_history({}, "", initial, now),
    )

def save_candidate_data(candidate_id: str, data: Dict[str, Any], replace: bool = False) -> None:
    """Merge (or replace) candidate_data. Follows save_job_data pattern.
    Pure data persistence — no side effects, no AI calls."""
    database.save_candidate(candidate_id, candidate_data=data, merge=not replace)


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
    return {k: str(v) for k, v in content.items() if k in section_ids}


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


def _coerce_resume_section_string(val: Any) -> Optional[str]:
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
    sections = raw_struct.get("sections")
    if not isinstance(sections, dict):
        return

    def _promote(sid: str, val: Any) -> None:
        if sid not in RESUME_STRUCTURE_KNOWN_SECTION_IDS:
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
            if _coerce_resume_section_string(inner.get(sid)):
                continue
            text = _coerce_resume_section_string(val)
            if text:
                inner[sid] = text
    for key, val in list(inner.items()):
        if key in _DRAFT_JOB_RESUME_METADATA_KEYS or key == "resume_structure":
            continue
        if isinstance(val, (list, dict)):
            text = _coerce_resume_section_string(val)
            if text:
                inner[key] = text
    _apply_draft_job_resume_section_aliases(inner)


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
        text = _coerce_resume_section_string(val)
        if text is None:
            return f"Section '{key}' must be prose text (string or coercible list)"
        if text != val:
            payload[key] = text
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
    content: Dict[str, str] = {}
    for key in enabled_ids:
        if key not in parsed:
            continue
        val = parsed[key]
        if isinstance(val, str):
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
    """Keep string values for enabled section ids; omit empty strings."""
    if not isinstance(content, dict):
        return {}
    allowed = set(enabled_resume_section_ids(resume_structure))
    if not allow_contact:
        allowed -= set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
    out: Dict[str, str] = {}
    for key in allowed:
        val = content.get(key)
        if isinstance(val, str) and val.strip():
            out[key] = val
    return out


async def parse_candidate_resume(candidate_id: str) -> Dict[str, Any]:
    """Parse context.starting_resume_text via do_task('craft_resume_base').
    Reads from candidate_data.context.starting_resume_text, writes parsed
    result to candidate_data.artifacts.base_resume.
    Does not change candidate state (AST-970 — no PROFILE_READY auto-hop).

    Async — called from CLI/scripts via asyncio.run(), never from Flask handlers."""
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        return {"success": False, "error": f"Candidate not found: {candidate_id}"}
    resume_raw = (candidate.get("candidate_data") or {}).get("context", {}).get("starting_resume_text", "")
    if not resume_raw or not resume_raw.strip():
        return {"success": False, "error": "No starting_resume_text in candidate_data.context"}

    response = await do_task(
        task_key="craft_resume_base",
        live_content=resume_raw,
        index=candidate_id,
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
    return {"success": True, "parsed": parsed}


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
    live = ((candidate.get("candidate_data") or {}).get("context") or {}).get("starting_resume_text") or ""
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
