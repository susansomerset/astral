"""
Core tracker: job lifecycle management (AST-75).

In-scope: ingest_jobs, save_job_data, get_job_data, initialize_job, transition_job_state,
get_new_job_batch, get_job_batch, clear_job_batch.
All writes go through database.save_job (upsert); state transition logic lives here, not in data layer.
get_job_data: coat-check pattern — return value if present, self-heal if missing (e.g. fetch JD via playwright).
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.core import candidate as candidate_mod
from src.data import database
from src.utils.config import (
    BUILD_CONFIG,
    JOB_BUILD_ARTIFACT_CLEAR_KEYS,
    JOB_STATES,
    RESUME_STRUCTURE_CONTACT_SECTION_IDS,
    TRACKER_CONFIG,
    is_resume_artifact_in_progress,
    resume_artifact_first_compound_state,
    validate_value,
)
from src.utils.logging import get_logger
from src.utils.formatting import parse_text

logger = get_logger(__name__)

_JOB_STATE_LIST = list(JOB_STATES.keys())
_JOB_COLUMN_FIELDS = {"company_job_id", "job_title", "job_link"}  # initialize_job: parsed_job keys -> job table columns
_JOB_REQUIRED_COLUMN_FIELDS = {"job_title", "job_link"}           # subset that must be present


def _identity_triple_complete(company_job_id: Optional[str], job_title: Optional[str]) -> bool:
    return bool(
        company_job_id and job_title
        and str(company_job_id).strip()
        and str(job_title).strip()
    )


def _is_job_identity_unique_violation(exc: sqlite3.IntegrityError) -> bool:
    msg = str(exc).lower()
    return "idx_job_identity_unique" in msg or (
        "unique constraint failed" in msg
        and "job.company" in msg
        and "job.job_title" in msg
        and "job.company_job_id" in msg
    )

# ---- Ingest ----

def ingest_jobs(
    company: str,
    batch_id: str,
    raw_job_listings: List[str],
    title_matchers: Optional[List[Any]] = None,
    ) -> Dict[str, int]:
    """Ingest raw HTML job listings from Gazer (AST-85). Validates input; dedup; insert new; return counts.

    Input contract (AST-79): company and batch_id must be present; raw_job_listings must be a list (may be empty).
    Fails fast with ValueError on invalid input.

    Returns (AST-457): {"new": N, "duplicates": M, "invalid_title": T}. When title_matchers is set,
    listings that fail every regex are skipped (not inserted) and counted in invalid_title.
    """
    if not company or not isinstance(company, str):
        raise ValueError("company must be a non-empty string")
    if not batch_id or not isinstance(batch_id, str):
        raise ValueError("batch_id must be a non-empty string")
    if not isinstance(raw_job_listings, list):
        raise ValueError("raw_job_listings must be a list")

    initial_state = TRACKER_CONFIG["ingest"]["initial_state"]
    validate_value(_JOB_STATE_LIST, initial_state)
    new_count = 0
    dup_count = 0
    title_mismatch_count = 0
    filter_titles = bool(title_matchers)

    for raw_job_listing in raw_job_listings:
        if database.raw_job_listing_is_duplicate(company, raw_job_listing):
            dup_count += 1
            continue
        if filter_titles and not any(m.search(raw_job_listing) for m in title_matchers):
            title_mismatch_count += 1
            continue
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        inserted = database.save_job(
            str(uuid.uuid4()),
            job_title=parse_text(raw_job_listing),
            company=company,
            state=initial_state,
            job_data={"raw_job_listing": raw_job_listing},
            state_history=[{"to_state": initial_state, "timestamp": now, "batch_id": batch_id}],
            state_changed_at=now,
        )
        if not inserted:
            dup_count += 1
            continue
        new_count += 1

    return {
        "new": new_count,
        "duplicates": dup_count,
        "invalid_title": title_mismatch_count,
    }


# ---- Job data ----

def get_job_artifacts(job: Dict[str, Any]) -> Dict[str, Any]:
    """Return job_data.artifacts dict (may be empty). AST-302."""
    jd = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    art = jd.get("artifacts")
    return art if isinstance(art, dict) else {}


def _candidate_data_for_job(astral_job_id: str) -> dict:
    """Inner candidate_data blob for the job's owning candidate, or {}."""
    job = get_job(astral_job_id)
    if not job:
        return {}
    company_key = job.get("company")
    if not isinstance(company_key, str) or not company_key.strip():
        return {}
    company = get_company(company_key.strip())
    if not company:
        return {}
    candidate_id = company.get("candidate_id")
    if not candidate_id:
        return {}
    row = candidate_mod.get_candidate(str(candidate_id))
    if not row:
        return {}
    cd = row.get("candidate_data")
    return cd if isinstance(cd, dict) else {}


def _prepare_job_resume_content(resume_content: Dict[str, Any], candidate_data: dict) -> Dict[str, str]:
    """Filter to candidate catalog; snapshot contact sections from payload or base_resume."""
    structure = candidate_mod.resolve_resume_structure(candidate_data)
    filtered = candidate_mod.filter_content_to_resume_structure(
        resume_content if isinstance(resume_content, dict) else {},
        structure,
        allow_contact=False,
    )
    artifacts = candidate_data.get("artifacts") if isinstance(candidate_data.get("artifacts"), dict) else {}
    base_resume = artifacts.get("base_resume") if isinstance(artifacts.get("base_resume"), dict) else {}
    snapshot: Dict[str, str] = {}
    for sid in RESUME_STRUCTURE_CONTACT_SECTION_IDS:
        spec = (structure.get("sections") or {}).get(sid) or {}
        if not spec.get("enabled"):
            continue
        val = resume_content.get(sid) if isinstance(resume_content, dict) else None
        if isinstance(val, str) and val.strip():
            snapshot[sid] = val
        else:
            base_val = base_resume.get(sid)
            snapshot[sid] = str(base_val) if isinstance(base_val, str) else ""
    merged = dict(filtered)
    merged.update(snapshot)
    return merged


def save_job_artifact_resume_content(astral_job_id: str, resume_content: Dict[str, Any]) -> None:
    """Merge resume_content into job_data.artifacts. AST-302; keys filtered to candidate structure."""
    cd = _candidate_data_for_job(astral_job_id)
    prepared = _prepare_job_resume_content(resume_content, cd)
    save_job_data(astral_job_id, {"artifacts": {"resume_content": prepared}})


def normalize_cover_letter_artifact(cover_letter: Any) -> Dict[str, str]:
    """AST-309/518: stored cover_letter uses Subject, Letter, signature (legacy read aliases)."""
    if not isinstance(cover_letter, dict):
        return {"Subject": "", "Letter": "", "signature": ""}
    return {
        "Subject": str(cover_letter.get("Subject") or cover_letter.get("re_line") or ""),
        "Letter": str(cover_letter.get("Letter") or cover_letter.get("body") or ""),
        "signature": str(cover_letter.get("signature") or ""),
    }


def save_job_artifact_cover_letter(astral_job_id: str, cover_letter: Dict[str, Any]) -> None:
    """Merge cover_letter object into job_data.artifacts. AST-309."""
    save_job_data(astral_job_id, {"artifacts": {"cover_letter": normalize_cover_letter_artifact(cover_letter)}})


def _artifact_shape_required_keys(shape_name: str) -> List[str]:
    shape = (BUILD_CONFIG.get("artifact_shapes") or {}).get(shape_name) or {}
    return [
        k for k, spec in shape.items()
        if isinstance(spec, dict) and spec.get("required")
    ]


def _resume_payload_body(parsed: Any) -> Dict[str, str]:
    """Flat string section dict from terminal hop JSON (optional agent_payload wrapper)."""
    if not isinstance(parsed, dict):
        return {}
    body: Any = parsed.get("agent_payload") if isinstance(parsed.get("agent_payload"), dict) else parsed
    if not isinstance(body, dict):
        return {}
    return {k: v for k, v in body.items() if isinstance(v, str)}


def parsed_matches_resume_content_shape(parsed: Any, candidate_data: dict) -> bool:
    """True when at least one enabled catalog section has non-empty string content (AST-551)."""
    structure = candidate_mod.resolve_resume_structure(candidate_data)
    enabled = set(candidate_mod.enabled_resume_section_ids(structure))
    if not enabled:
        return False
    body = _resume_payload_body(parsed)
    return any((body.get(sid) or "").strip() for sid in enabled)


def parsed_matches_job_resume_content(astral_job_id: str, parsed: Any) -> bool:
    """True when parsed has at least one enabled non-contact resume section with body text."""
    if not isinstance(parsed, dict):
        return False
    cd = _candidate_data_for_job(astral_job_id)
    structure = candidate_mod.resolve_resume_structure(cd)
    contact = set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
    body = _resume_payload_body(parsed)
    for sid in candidate_mod.enabled_resume_section_ids(structure):
        if sid in contact:
            continue
        val = body.get(sid)
        if isinstance(val, str) and val.strip():
            return True
    return False


def job_has_persisted_resume_body(astral_job_id: str, job: Optional[Dict[str, Any]] = None) -> bool:
    """Non-empty resume_content for an enabled non-contact section (post-persist gate)."""
    row = job if job is not None else get_job(astral_job_id)
    if not row:
        return False
    rc = get_job_artifacts(row).get("resume_content")
    if not isinstance(rc, dict) or not rc:
        return False
    cd = _candidate_data_for_job(astral_job_id)
    structure = candidate_mod.resolve_resume_structure(cd)
    contact = set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
    for sid in candidate_mod.enabled_resume_section_ids(structure):
        if sid in contact:
            continue
        val = rc.get(sid)
        if isinstance(val, str) and val.strip():
            return True
    return False


def clear_job_artifact_resume_content(astral_job_id: str) -> None:
    """Remove resume_content from job_data (failed artifact run rollback)."""
    job = get_job(astral_job_id)
    if not job:
        return
    jd = job.get("job_data")
    if not isinstance(jd, dict):
        return
    art = jd.get("artifacts")
    if not isinstance(art, dict) or "resume_content" not in art:
        return
    new_jd = {**jd, "artifacts": {k: v for k, v in art.items() if k != "resume_content"}}
    save_job_data(astral_job_id, new_jd, replace=True)


def parsed_matches_artifact_shape(parsed: Any, shape_name: str) -> bool:
    if not isinstance(parsed, dict):
        return False
    if shape_name == "cover_letter":
        has_subject = "Subject" in parsed or "re_line" in parsed
        has_letter = "Letter" in parsed or "body" in parsed
        return has_subject and has_letter
    keys = _artifact_shape_required_keys(shape_name)
    return bool(keys) and all(k in parsed for k in keys)


def slice_parsed_for_artifact_shape(parsed: Dict[str, Any], shape_name: str) -> Dict[str, Any]:
    if shape_name == "cover_letter":
        out: Dict[str, Any] = {}
        for k in ("Subject", "Letter", "signature", "re_line", "body"):
            if k in parsed:
                out[k] = parsed[k]
        return out
    shape = (BUILD_CONFIG.get("artifact_shapes") or {}).get(shape_name) or {}
    return {k: parsed[k] for k in shape if k in parsed}


def persist_job_artifact_from_parsed(
    astral_job_id: str,
    parsed: Any,
    *,
    allow_resume: bool = True,
    allow_cover_letter: bool = True,
) -> bool:
    """AST-369/371: merge parsed task JSON into job_data.artifacts when shape matches."""
    if not astral_job_id or not isinstance(parsed, dict):
        return False
    wrote = False
    if allow_cover_letter and parsed_matches_artifact_shape(parsed, "cover_letter"):
        save_job_artifact_cover_letter(astral_job_id, slice_parsed_for_artifact_shape(parsed, "cover_letter"))
        wrote = True
    if allow_resume:
        cd = _candidate_data_for_job(astral_job_id)
        if parsed_matches_job_resume_content(astral_job_id, parsed):
            structure = candidate_mod.resolve_resume_structure(cd)
            body = _resume_payload_body(parsed)
            filtered = candidate_mod.filter_content_to_resume_structure(
                body, structure, allow_contact=True,
            )
            save_job_artifact_resume_content(astral_job_id, filtered)
            wrote = True
    return wrote


def clear_job_build_artifacts(astral_job_id: str) -> None:
    """Remove partial build artifact keys on cancel (AST-552 replace-merge pattern). AST-562."""
    job = get_job(astral_job_id)
    if not job:
        raise ValueError(f"Job not found: {astral_job_id}")
    jd = job.get("job_data")
    if not isinstance(jd, dict):
        return
    art = jd.get("artifacts")
    if not isinstance(art, dict) or not any(k in art for k in JOB_BUILD_ARTIFACT_CLEAR_KEYS):
        return
    new_jd = {
        **jd,
        "artifacts": {k: v for k, v in art.items() if k not in JOB_BUILD_ARTIFACT_CLEAR_KEYS},
    }
    save_job_data(astral_job_id, new_jd, replace=True)


def start_artifact_build(astral_job_id: str) -> str:
    """RECOMMENDED → BUILD_ARTIFACTS.<first_hop> via explicit UI/API only (no dispatch). AST-562 / AST-595."""
    job = get_job(astral_job_id)
    if not job:
        raise ValueError(f"Job not found: {astral_job_id}")
    if job.get("state") != "RECOMMENDED":
        raise ValueError("generate only from RECOMMENDED")
    first = resume_artifact_first_compound_state()
    transition_job_state([astral_job_id], first)
    return first


def cancel_artifact_build(astral_job_id: str) -> str:
    """BUILD_ARTIFACTS.* → RECOMMENDED; clear partial artifacts and batch lock. AST-562 / AST-595."""
    job = get_job(astral_job_id)
    if not job:
        raise ValueError(f"Job not found: {astral_job_id}")
    if not is_resume_artifact_in_progress(job.get("state") or ""):
        raise ValueError("cancel only from BUILD_ARTIFACTS in-progress hop states")
    clear_job_build_artifacts(astral_job_id)
    if job.get("batch_id"):
        database.clear_job_batch_lock(astral_job_id)
    transition_job_state([astral_job_id], "RECOMMENDED")
    return "RECOMMENDED"


def get_candidate_results(job: Dict[str, Any]) -> Dict[str, Any]:
    """AST-311: job_data.candidate_results or {}."""
    jd = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
    cr = jd.get("candidate_results")
    return cr if isinstance(cr, dict) else {}


def set_candidate_result(astral_job_id: str, action_key: str, notes: Optional[str] = None) -> None:
    """AST-311: last write wins per action key; server timestamp."""
    now = datetime.now(timezone.utc).isoformat()
    entry = {"timestamp": now, "notes": notes or ""}
    save_job_data(astral_job_id, {"candidate_results": {action_key: entry}})


def save_job_data(
    astral_job_id: str,
    job_data: Dict[str, Any],
    replace: bool = False,
    ) -> None:
    """Update job_data for a job (AST-76). replace=False: deep merge; replace=True: full overwrite.
    Raises ValueError if astral_job_id does not exist. job_data must be JSON-serializable.
    replace=True overwrites the entire job_data blob; use only when intentionally replacing."""
    database.save_job(astral_job_id, job_data=job_data, merge=not replace)

async def get_job_data(job: Dict[str, Any], key: str) -> Any:
    """Return job_data[key]. For job_description key (from config), if missing: fetch via playwright
    get_visible_text with the job's job_link, save to job_data, then return. Caller gets value either
    way (coat-check pattern). Returns None if key not present and not a self-healable key."""
    # Always read directly from job["job_data"] so Phase 1 write-backs are visible here
    if not isinstance(job.get("job_data"), dict):
        job["job_data"] = {}
    job_data = job["job_data"]
    jd_key = TRACKER_CONFIG.get("job_data_keys", {}).get("job_description", "job_description")
    min_chars = TRACKER_CONFIG.get("jd_min_chars", 200)
    # Happy path: value already present and long enough
    if key in job_data and job_data[key]:
        if key != jd_key or len(job_data[key]) >= min_chars:
            return job_data[key]
    if key != jd_key:
        return None
    # Self-heal: belt-and-suspenders before any agent call sees a missing JD.
    # Delegates to fetch_jd_batch (single job) so prune rules live in one place.
    astral_job_id = job.get("astral_job_id", "")
    logger.warning(f"[{astral_job_id}] coat-check self-heal: JD missing, invoking fetch_jd_batch")
    try:
        from src.core.gazer import fetch_jd_batch
        await fetch_jd_batch(str(uuid.uuid4()), [job])
    except Exception as e:
        logger.warning(f"get_job_data: fetch_jd_batch self-heal failed for {astral_job_id}: {e}")
        return None
    # job["job_data"] was written back by fetch_jd_batch if successful
    return job["job_data"].get(jd_key)


def get_job(astral_job_id: str) -> Optional[Dict[str, Any]]:
    """Job-by-ID for render and id-only callers; not ``get_job_batch`` (dispatch-scoped).
    Thin delegate to the data layer. Consult should migrate off ``database.get_job`` per AST-372."""
    return database.get_job(astral_job_id)


def initialize_job(
    astral_job_id: str,
    company: str,
    parsed_job: Dict[str, Any],
    ) -> bool:
    """Populate structured job fields from AI-parsed thumbprint data. One-time per job.
    Splits parsed_job: column fields -> top-level job columns, everything else -> merge into job_data.
    Consult calls initialize_job and transition_job_state separately (no composite).
    Returns True when saved; False when current row deleted due to identity collision."""
    # These columns are NULL at ingest and can't be NOT NULL in the schema due to lifecycle;
    # initialize_job is the enforcement point the database can't provide.
    missing = _JOB_REQUIRED_COLUMN_FIELDS - parsed_job.keys()
    if missing:
        raise ValueError(f"initialize_job: parsed_job missing required fields: {missing}")
    # Column fields -> top-level job table columns (absent optional fields default to None)
    col_kwargs = {k: parsed_job.get(k) for k in _JOB_COLUMN_FIELDS}
    # Remaining fields (excluding astral_job_id echo-back and grades which are verdict data, not job metadata) -> job_data
    metadata = {k: v for k, v in parsed_job.items() if k not in _JOB_COLUMN_FIELDS and k not in ("astral_job_id", "grades")}
    # Flatten nested job_data dict — decoded payloads pack extras there; merge into top-level metadata
    if isinstance(metadata.get("job_data"), dict):
        metadata.update(metadata.pop("job_data"))
    cid = col_kwargs.get("company_job_id")
    title = col_kwargs.get("job_title")
    if _identity_triple_complete(cid, title):
        canonical = database.get_job_id_by_identity(
            company,
            str(title).strip(),
            str(cid).strip(),
            exclude_astral_job_id=astral_job_id,
        )
        if canonical is not None:
            database.delete_job(astral_job_id)
            return False
    try:
        database.save_job(
            astral_job_id,
            company_job_id=col_kwargs["company_job_id"],
            job_title=col_kwargs["job_title"],
            job_link=col_kwargs["job_link"],
            job_data=metadata if metadata else None,
            merge=True,
        )
    except sqlite3.IntegrityError as e:
        if _is_job_identity_unique_violation(e):
            database.delete_job(astral_job_id)
            return False
        raise
    return True

# ---- State transition ----

def transition_job_state(job_ids: List[str], to_state: str, score: Optional[float] = None) -> None:
    """Record state transition for jobs (AST-77). Appends to state_history; updates state.
    score: when provided, recorded in the state_history entry and written to latest_score column (AST-350).
    Validates to_state against JOB_STATES and prior_states rules. Raises ValueError if invalid."""
    validate_value(_JOB_STATE_LIST, to_state)
    prior_states = JOB_STATES[to_state].get("prior_states")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for job_id in job_ids:
        job = database.get_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        if prior_states is not None and job.get("state") not in prior_states:
            raise ValueError(f"Invalid transition: {job.get('state')} -> {to_state}")
        history = job.get("state_history", [])
        entry: Dict[str, Any] = {"to_state": to_state, "timestamp": now, "batch_id": job.get("batch_id")}
        if score is not None:
            entry["score"] = score
        history.append(entry)
        save_kwargs: Dict[str, Any] = {
            "state": to_state,
            "state_history": history,
            "state_changed_at": now,
        }
        if score is not None:
            save_kwargs["latest_score"] = score
        database.save_job(job_id, **save_kwargs)


# ---- Batch API ----

def get_new_job_batch(
    state: str,
    limit: Optional[int] = None,
    sort_by: Optional[str] = None,
    score_floor: Optional[float] = None,
    candidate_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    context: Optional[str] = None,
    *,
    claim_cap: Optional[int] = None,
    states: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
    """Claim jobs in state (AST-78). Returns (batch_id, jobs).
    limit/sort_by from the caller (dispatcher reads from DB task row); limit defaults to 10 if omitted.
    claim_cap: optional upper bound matching count_eligible_for_dispatch_task — AST-502 multi-chunk exhaustion.
    candidate_id: when provided, scopes claim to jobs whose company belongs to this candidate.
    batch_id: when provided, uses this batch_id instead of generating a new one.
    context: prefix for auto-generated batch_id (required when batch_id is not provided)."""
    if states is None:
        validate_value(_JOB_STATE_LIST, state)
    else:
        for s in states:
            validate_value(_JOB_STATE_LIST, s)
    limit_val = limit if limit is not None else 10
    sort_by_val = sort_by
    if not batch_id and not context:
        raise ValueError("batch_id or context is required for batch_id generation")
    bid = batch_id or f"{context}-{uuid.uuid4()}"
    database.claim_job_batch(
        bid,
        state,
        limit_val,
        sort_by=sort_by_val,
        candidate_id=candidate_id,
        score_floor=score_floor,
        claim_cap=claim_cap,
        states=states,
    )
    jobs = database.get_job_batch(bid)
    return (bid, jobs)


def get_job_batch(batch_id: str) -> List[Dict[str, Any]]:
    """Return all jobs in batch (AST-78)."""
    return database.get_job_batch(batch_id)


def clear_job_batch(batch_id: str) -> int:
    """Release batch so jobs can be reclaimed (AST-78). Returns count released."""
    return database.clear_job_batch(batch_id)


def release_job_dispatch_claim(astral_job_id: str) -> None:
    """Clear batch_id lock on one job so the next dispatch tick can reclaim (AST-596)."""
    database.clear_job_batch_lock(astral_job_id)


# ---- UI API facades (AST-321): Flask blueprints import these instead of database ----


def list_jobs(
    states: Optional[List[str]] = None,
    candidate_id: Optional[str] = None,
    order_by: str = "state_changed_at",
) -> List[Dict[str, Any]]:
    return database.list_jobs(states=states, candidate_id=candidate_id, order_by=order_by)


def count_jobs(
    states: Optional[List[str]] = None,
    candidate_id: Optional[str] = None,
) -> int:
    return database.count_jobs(states=states, candidate_id=candidate_id)


def save_job(astral_job_id: str, **kwargs: Any) -> bool:
    """Direct job row upsert for admin/API callers. Returns False on identity duplicate insert bounce."""
    return database.save_job(astral_job_id, **kwargs)


def score_floor_by_trigger_for_candidate(candidate_id: str) -> Dict[str, float]:
    return database.score_floor_by_trigger_for_candidate(candidate_id)


# Consult / API facades — delegate reads-writes AST-486 (consult must not import database).

def get_company(short_name: str) -> Optional[Dict[str, Any]]:
    """Thin delegate: company row by short_name (same as database.get_company)."""
    return database.get_company(short_name)


def append_agent_response(entity_type: str, entity_id: str, entry: Dict[str, Any]) -> None:
    """Thin delegate — upserts by task_key; latest ref wins; full history stays in agent_data."""
    database.append_agent_response(entity_type, entity_id, entry)


def list_timesheets(**kwargs: Any) -> List[Dict[str, Any]]:
    """Thin delegate for layering — UI/core timesheet reads go through tracker, not database."""
    return database.list_timesheets(**kwargs)


def job_misses_dispatch_score_floor(job: Dict[str, Any], floors: Dict[str, float]) -> bool:
    return database.job_misses_dispatch_score_floor(job, floors)


def count_jobs_below_dispatch_score_floor(candidate_id: str) -> int:
    return database.count_jobs_below_dispatch_score_floor(candidate_id)


def list_jobs_below_dispatch_score_floor(candidate_id: str) -> List[Dict[str, Any]]:
    return database.list_jobs_below_dispatch_score_floor(candidate_id)
