"""
Core tracker: job lifecycle management (AST-75).

In-scope: ingest_jobs, save_meteorite_job, save_job_data, get_job_data, initialize_job,
transition_job_state, get_new_job_batch, get_job_batch, clear_job_batch, assemble_job_copy_snapshot.
All writes go through database.save_job (upsert); state transition logic lives here, not in data layer.
get_job_data: coat-check pattern — return value if present, self-heal if missing (e.g. fetch JD via playwright).
AST-1518: contact-task read wrappers + get_job_by_pattern (candidate-scoped; no coat-check scrape).
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.core import candidate as candidate_mod
from src.data import database
from src.utils.config import (
    BLOCK_TYPES,
    BUILD_CONFIG,
    BUILD_ARTIFACTS_BASE_STATE,
    JOB_BUILD_ARTIFACT_CLEAR_KEYS,
    JOB_SOURCE_DEFAULT,
    JOB_SOURCE_METEORITE,
    JOB_STATES,
    METEORITE_CONFIG,
    RESUME_STRUCTURE_CONTACT_SECTION_IDS,
    SKIPPED_STATES,
    TASK_CONFIG,
    TRACKER_CONFIG,
    dispatch_chain_graduation_target,
    dispatch_hop_label,
    job_source_transition_allowed,
    parse_dispatch_hop_label,
    is_build_artifacts_in_progress,
    is_valid_job_batch_claim_state,
    legacy_build_artifacts_hop,
    validate_job_source,
    validate_value,
)
from src.utils.logging import get_logger, truncate_debug_content
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


def _assert_job_source_write(current: Optional[str], new: str) -> None:
    """Validate one-way job source write (AST-1469): meteorite → gazed forbidden."""
    validate_job_source(new)
    if not job_source_transition_allowed(current, new):
        raise ValueError(
            f"Invalid job source transition: {current!r} -> {new!r} "
            f"(meteorite → gazed forbidden)"
        )


def set_job_source(astral_job_id: str, source: str) -> None:
    """Admin/core helper: validate one-way source write on an existing job (AST-1469)."""
    job = database.get_job(astral_job_id)
    if not job:
        raise ValueError(f"Job not found: {astral_job_id}")
    _assert_job_source_write(job.get("source"), source)
    database.save_job(astral_job_id, source=source)


def save_meteorite_job(
    candidate_id: str,
    *,
    company: str,
    company_job_id: Optional[str] = None,
    job_title: Optional[str] = None,
    job_link: Optional[str] = None,
    job_data: Optional[Dict[str, Any]] = None,
    employer_name: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Tracker meteorite save: dedupe before write; create / gazed-supersede / never clobber (AST-1469).

    Caller supplies already-ensured meteorite company short_name (land owns ensure).
    Supersede uses direct save_job into job_create_state (METEORITE_NEW) — carve-out twin of
    create_meteorite_job; does not gate on the gazed job's prior state (parent AC2).
    """
    cid = (candidate_id or "").strip()
    company_key = (company or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if not company_key:
        raise ValueError("company is required")

    log = get_logger(__name__)
    log.set_debug_flag(debug)

    prepared: Dict[str, Any] = dict(job_data or {})
    emp = (employer_name or "").strip() if employer_name is not None else ""
    if emp:
        prepared[METEORITE_CONFIG["employer_name_job_data_key"]] = emp

    cid_job = (company_job_id or "").strip() or None
    title = (job_title or "").strip() or None
    link = (job_link or "").strip() or None
    state = METEORITE_CONFIG["job_create_state"]
    score = float(METEORITE_CONFIG["job_create_latest_score"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    match = database.find_meteorite_dedupe_match(
        cid, company_job_id=cid_job, job_link=link
    )

    def _debug(outcome: str, astral_id: str, *, matched_id: Optional[str] = None, src_before: Any = None) -> None:
        if not debug:
            return
        log.debug_index(
            func="tracker.save_meteorite_job",
            index=1,
            total=1,
            identifier=astral_id or cid,
            outcome=outcome,
        )
        log.debug_detail(f"candidate_id={cid}")
        log.debug_detail(f"company={company_key}")
        if matched_id:
            log.debug_detail(f"matched_id={matched_id}")
        if src_before is not None:
            log.debug_detail(f"source_before={src_before!r} source_after={JOB_SOURCE_METEORITE!r}")

    if match is not None:
        match_source = (match.get("source") or "").strip() or JOB_SOURCE_DEFAULT
        match_id = match["astral_job_id"]

        # Branch A — existing meteorite: never clobber
        if match_source == JOB_SOURCE_METEORITE:
            _debug(
                METEORITE_CONFIG["land_outcome_duplicate_skip"],
                match_id,
                matched_id=match_id,
                src_before=match_source,
            )
            return {
                "outcome": METEORITE_CONFIG["land_outcome_duplicate_skip"],
                "astral_job_id": match_id,
                "job": match,
                "source": JOB_SOURCE_METEORITE,
            }

        # Branch B — gazed supersede (any prior job state; keep company)
        if match_source == JOB_SOURCE_DEFAULT:
            _assert_job_source_write(match.get("source"), JOB_SOURCE_METEORITE)
            history = list(match.get("state_history") or [])
            history.append({"to_state": state, "timestamp": now, "score": score})
            save_kwargs: Dict[str, Any] = {
                "state": state,
                "source": JOB_SOURCE_METEORITE,
                "job_data": prepared if prepared else None,
                "state_history": history,
                "state_changed_at": now,
                "latest_score": score,
                "merge": True,
            }
            if cid_job is not None:
                save_kwargs["company_job_id"] = cid_job
            if title is not None:
                save_kwargs["job_title"] = title
            if link is not None:
                save_kwargs["job_link"] = link
            database.save_job(match_id, **save_kwargs)
            row = database.get_job(match_id)
            if row is None:
                raise RuntimeError(f"meteorite supersede missing after save: {match_id}")
            _debug(
                METEORITE_CONFIG["land_outcome_superseded"],
                match_id,
                matched_id=match_id,
                src_before=match_source,
            )
            return {
                "outcome": METEORITE_CONFIG["land_outcome_superseded"],
                "astral_job_id": match_id,
                "job": row,
                "source": JOB_SOURCE_METEORITE,
            }

        raise ValueError(f"Unexpected job source on dedupe match: {match_source!r}")

    # Branch C — create under caller-supplied meteorite company
    astral_job_id = str(uuid.uuid4())
    inserted = database.save_job(
        astral_job_id,
        company=company_key,
        state=state,
        source=JOB_SOURCE_METEORITE,
        company_job_id=cid_job,
        job_title=title,
        job_link=link,
        job_data=prepared if prepared else None,
        state_history=[{"to_state": state, "timestamp": now, "score": score}],
        state_changed_at=now,
        merge=False,
    )
    if not inserted:
        # Identity unique bounce — treat as duplicate when re-findable
        bounced = database.find_meteorite_dedupe_match(
            cid, company_job_id=cid_job, job_link=link
        )
        if bounced is None and cid_job and title:
            bounced_id = database.get_job_id_by_identity(company_key, title, cid_job)
            bounced = database.get_job(bounced_id) if bounced_id else None
        if bounced is not None:
            _debug(
                METEORITE_CONFIG["land_outcome_duplicate_skip"],
                bounced["astral_job_id"],
                matched_id=bounced["astral_job_id"],
                src_before=bounced.get("source"),
            )
            return {
                "outcome": METEORITE_CONFIG["land_outcome_duplicate_skip"],
                "astral_job_id": bounced["astral_job_id"],
                "job": bounced,
                "source": (bounced.get("source") or JOB_SOURCE_METEORITE),
            }
        raise RuntimeError(f"meteorite job insert failed: {astral_job_id}")

    # INSERT path omits latest_score — update column explicitly (create carve-out twin)
    database.save_job(astral_job_id, latest_score=score)
    row = database.get_job(astral_job_id)
    if row is None:
        raise RuntimeError(f"meteorite job missing after save: {astral_job_id}")
    _debug(METEORITE_CONFIG["land_outcome_created"], astral_job_id)
    return {
        "outcome": METEORITE_CONFIG["land_outcome_created"],
        "astral_job_id": astral_job_id,
        "job": row,
        "source": JOB_SOURCE_METEORITE,
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


def _prepare_job_resume_content(resume_content: Dict[str, Any], candidate_data: dict) -> Dict[str, Any]:
    """Filter to candidate catalog; snapshot contact sections from payload or base_resume."""
    structure = candidate_mod.resolve_resume_structure(candidate_data)
    filtered = candidate_mod.filter_content_to_resume_structure(
        resume_content if isinstance(resume_content, dict) else {},
        structure,
        allow_contact=False,
    )
    allowed = set(candidate_mod.draft_job_resume_allowed_section_keys(candidate_data))
    contact = set(RESUME_STRUCTURE_CONTACT_SECTION_IDS)
    for sid, val in (resume_content or {}).items():
        if sid in allowed and sid not in filtered and sid not in contact:
            if candidate_mod.is_experience_job_array(val) and val:
                filtered[sid] = val
            elif isinstance(val, str) and val.strip():
                filtered[sid] = val
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
    merged: Dict[str, Any] = dict(filtered)
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


_COVER_LETTER_FIELD_KEYS = frozenset({"Subject", "re_line", "Letter", "body", "signature"})


def _cover_letter_display_nonempty(normalized: Dict[str, str]) -> bool:
    return any(str(normalized.get(k) or "").strip() for k in ("Subject", "Letter", "signature"))


def _cover_letter_dict_for_normalize(raw: dict) -> dict:
    """Flat cover dict, or one nested dict that carries cover keys (hop envelope)."""
    if _cover_letter_display_nonempty(normalize_cover_letter_artifact(raw)):
        return raw
    # Prefer known nest keys, then a single nested dict that looks like cover fields.
    for nest_key in ("agent_payload", "cover_letter"):
        inner = raw.get(nest_key)
        if isinstance(inner, dict) and _COVER_LETTER_FIELD_KEYS.intersection(inner.keys()):
            return inner
    nested = [
        v for v in raw.values()
        if isinstance(v, dict) and _COVER_LETTER_FIELD_KEYS.intersection(v.keys())
    ]
    if len(nested) == 1:
        return nested[0]
    return raw


def cover_letter_artifact_for_display(
    raw: Any,
    *,
    debug: bool = False,
) -> Optional[Dict[str, str]]:
    """AST-1499: pin or dict → nonempty Subject/Letter/signature for JAR; else None (no empty overlay)."""
    body: Any = raw
    if isinstance(raw, str) and raw.strip():
        body = resolve_job_artifact_agent_data_body(raw, debug=debug)
        if not isinstance(body, dict):
            return None
    elif not isinstance(raw, dict):
        return None
    normalized = normalize_cover_letter_artifact(_cover_letter_dict_for_normalize(body))
    if not _cover_letter_display_nonempty(normalized):
        return None
    return normalized


def save_job_artifact_cover_letter(astral_job_id: str, cover_letter: Dict[str, Any]) -> None:
    """Merge cover_letter object into job_data.artifacts. AST-309."""
    save_job_data(astral_job_id, {"artifacts": {"cover_letter": normalize_cover_letter_artifact(cover_letter)}})



def extract_draft_job_resume_notes(parsed: Any) -> Optional[List[str]]:
    """Normalize notes from nested or flat draft payload; None if key absent."""
    if not isinstance(parsed, dict):
        return None
    body: Any = parsed.get("agent_payload") if isinstance(parsed.get("agent_payload"), dict) else parsed
    if not isinstance(body, dict):
        return None
    meta_key = TASK_CONFIG["draft_job_resume"]["notes_artifact_key"]
    # Nested resume body is a sibling of notes — always read meta from the outer envelope.
    if meta_key not in body:
        return None
    raw = body.get(meta_key)
    if raw is None:
        return []
    if isinstance(raw, str):
        text = raw.strip()
        return [text] if text else []
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    text = str(raw).strip()
    return [text] if text else []


def save_job_artifact_notes(astral_job_id: str, notes: List[str]) -> None:
    """Merge freeform notes list into job_data.artifacts (AST-1523 / AST-1271 shape)."""
    if not astral_job_id or not str(astral_job_id).strip():
        return
    key = TASK_CONFIG["draft_job_resume"]["notes_artifact_key"]
    save_job_data(astral_job_id, {"artifacts": {key: list(notes)}})


def persist_draft_job_resume_notes(astral_job_id: str, parsed: Any) -> bool:
    """Extract notes from parsed draft response and save when the key is present."""
    extracted = extract_draft_job_resume_notes(parsed)
    if extracted is None:
        return False
    save_job_artifact_notes(astral_job_id, extracted)
    return True


def persist_finalize_job_resume_content(astral_job_id: str, parsed: Any) -> bool:
    """AST-1428: copy unwrapped finalize resume onto resume_content; pin slot untouched."""
    if not parsed_matches_job_resume_content(astral_job_id, parsed):
        return False
    save_job_artifact_resume_content(astral_job_id, _resume_payload_body(parsed))
    return True


def pin_job_artifact_agent_data_id(
    astral_job_id: str,
    artifact_key: str,
    agent_data_id: Any,
    *,
    debug: bool = False,
) -> bool:
    """AST-1099: merge RESPONSE agent_data_id into job_data.artifacts[key]. Never store empty."""
    dbg = get_logger(__name__, debug_flag=True) if debug else None

    def _skip(reason: str, key: str = "") -> bool:
        if dbg is not None:
            dbg.debug_detail(f"artifact_pin key={key or artifact_key} skipped reason={reason}")
        return False

    if not astral_job_id or not str(astral_job_id).strip():
        return _skip("missing_job_id")
    if not artifact_key or not str(artifact_key).strip():
        return _skip("missing_artifact_key")
    pin_id = str(agent_data_id).strip() if agent_data_id is not None else ""
    if not pin_id:
        return _skip("empty_agent_data_id", str(artifact_key))
    save_job_data(astral_job_id, {"artifacts": {str(artifact_key): pin_id}})
    if dbg is not None:
        dbg.debug_detail(f"artifact_pin key={artifact_key} agent_data_id={pin_id} recorded")
    return True


_JOB_ARTIFACT_PIN_KEYS = ("job_resume", "cover_letter", "proposed_answers")


def resolve_job_artifact_agent_data_body(
    agent_data_id: Any,
    *,
    debug: bool = False,
) -> Any:
    """AST-1100: load RESPONSE body by pin id. Never writes. Blank/missing → None."""
    dbg = get_logger(__name__, debug_flag=True) if debug else None

    def _skip(reason: str) -> None:
        if dbg is not None:
            dbg.debug_detail(f"artifact_resolve skipped reason={reason}")

    pin_id = str(agent_data_id).strip() if agent_data_id is not None else ""
    if not pin_id:
        _skip("empty_agent_data_id")
        return None
    row = database.get_agent_data(pin_id)
    if not row:
        _skip("missing_agent_data_row")
        return None
    text = row.get("block_data") or row.get("content") or ""
    if not isinstance(text, str) or not text.strip():
        _skip("empty_block_data")
        return None
    # Lazy: reuse agent parse (JSON / agent_payload unwrap) without import cycle at module load.
    from src.core.agent import _parsed_response_from_stored_response_text

    body = _parsed_response_from_stored_response_text(text, "")
    if dbg is not None:
        dbg.debug_detail(f"artifact_resolve agent_data_id={pin_id} recorded")
    return body


def hydrate_job_artifacts_for_display(
    artifacts: Any,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """AST-1100: shallow-copy artifacts; replace pin-slot strings with resolved bodies (no save)."""
    if not isinstance(artifacts, dict):
        return {}
    out = dict(artifacts)
    rc = out.get("resume_content")
    job_resume_blob = rc if isinstance(rc, dict) and rc else None
    for key in _JOB_ARTIFACT_PIN_KEYS:
        if key == "job_resume" and job_resume_blob is not None:
            # AST-1428: JAR reads job_resume; overlay sibling blob (disk pin unchanged).
            out[key] = dict(job_resume_blob)
            continue
        # AST-1499: cover display helper owns pin resolve + nonempty Subject/Letter (no empty overwrite).
        if key == "cover_letter":
            continue
        raw = out.get(key)
        if not isinstance(raw, str) or not raw.strip():
            continue
        body = resolve_job_artifact_agent_data_body(raw, debug=debug)
        if body is None:
            continue
        if key == "job_resume":
            # Pin resolve is agent_payload; unwrap .resume so section ids are top-level.
            unwrapped = _resume_payload_body(body)
            if unwrapped:
                out[key] = unwrapped
            continue
        out[key] = body
    # AST-1116/1499: Subject/Letter spine for ArtifactEditor only when nonempty (overlay only).
    display_cover = cover_letter_artifact_for_display(out.get("cover_letter"), debug=debug)
    if display_cover is not None:
        out["cover_letter"] = display_cover
    return out


def _artifact_shape_required_keys(shape_name: str) -> List[str]:
    shape = (BUILD_CONFIG.get("artifact_shapes") or {}).get(shape_name) or {}
    return [
        k for k, spec in shape.items()
        if isinstance(spec, dict) and spec.get("required")
    ]


def _resume_section_has_body(sid: str, val: Any) -> bool:
    if candidate_mod.is_experience_job_array(val) and val:
        return True
    return isinstance(val, str) and bool(val.strip())


def _resume_payload_body(parsed: Any) -> Dict[str, Any]:
    """Flat section dict from terminal hop JSON (strings + experience job arrays)."""
    if not isinstance(parsed, dict):
        return {}
    body: Any = parsed.get("agent_payload") if isinstance(parsed.get("agent_payload"), dict) else parsed
    if not isinstance(body, dict):
        return {}
    task_cfg = TASK_CONFIG["draft_job_resume"]
    # AST-1270: prefer nested resume body so envelope keys never look like sections.
    nest_key = task_cfg["nested_resume_key"]
    meta_keys = set(task_cfg["payload_metadata_keys"])
    nested = body.get(nest_key)
    if isinstance(nested, dict):
        body = nested
    out: Dict[str, Any] = {}
    for k, v in body.items():
        # AST-1271: nest key + payload metadata never enter resume body (even if string-typed).
        if k == nest_key or k in meta_keys:
            continue
        if isinstance(v, str):
            out[k] = v
        elif candidate_mod.is_experience_job_array(v):
            out[k] = v
    return out


def parsed_matches_resume_content_shape(parsed: Any, candidate_data: dict) -> bool:
    """True when at least one enabled catalog section has body content (AST-551)."""
    structure = candidate_mod.resolve_resume_structure(candidate_data)
    enabled = set(candidate_mod.enabled_resume_section_ids(structure))
    if not enabled:
        return False
    body = _resume_payload_body(parsed)
    return any(_resume_section_has_body(sid, body.get(sid)) for sid in enabled)


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
        if _resume_section_has_body(sid, body.get(sid)):
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
        if _resume_section_has_body(sid, rc.get(sid)):
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
    # AST-1523: sibling notes metadata (manual/API defense-in-depth; live path is do_task).
    if persist_draft_job_resume_notes(astral_job_id, parsed):
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
    """RECOMMENDED → BUILD_ARTIFACTS via explicit UI/API only (no dispatch). AST-562 / AST-803."""
    job = get_job(astral_job_id)
    if not job:
        raise ValueError(f"Job not found: {astral_job_id}")
    if job.get("state") != "RECOMMENDED":
        raise ValueError("generate only from RECOMMENDED")
    transition_job_state([astral_job_id], BUILD_ARTIFACTS_BASE_STATE)
    return BUILD_ARTIFACTS_BASE_STATE


def cancel_artifact_build(astral_job_id: str) -> str:
    """BUILD_ARTIFACTS* → RECOMMENDED; clear partial artifacts and batch lock. AST-562 / AST-803."""
    job = get_job(astral_job_id)
    if not job:
        raise ValueError(f"Job not found: {astral_job_id}")
    if not is_build_artifacts_in_progress(job.get("state") or ""):
        raise ValueError("cancel only from BUILD_ARTIFACTS in-progress states")
    clear_job_build_artifacts(astral_job_id)
    if job.get("batch_id"):
        database.clear_job_batch_lock(astral_job_id)
    transition_job_state([astral_job_id], "RECOMMENDED")
    return "RECOMMENDED"


def list_dispatch_tasks_for_candidate(
    candidate_id: str,
    *,
    trigger_state: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Dispatch rows for one candidate; optional trigger_state filter (flat or legacy compound)."""
    cid = str(candidate_id or "").strip()
    if not cid:
        return []
    ts = (trigger_state or "").strip() if trigger_state is not None else ""
    out: List[Dict[str, Any]] = []
    for row in database.list_dispatch_tasks():
        if str(row.get("candidate_id") or "").strip() != cid:
            continue
        row_ts = (row.get("trigger_state") or "").strip()
        if ts:
            if row_ts != ts:
                parsed = parse_dispatch_hop_label(row_ts)
                if not (parsed and parsed[0] == ts):
                    continue
        out.append(dict(row))
    return out


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


def assemble_job_copy_snapshot(
    astral_job_id: str,
    *,
    debug: bool = False,
) -> Optional[Dict[str, Any]]:
    """Stored job plus populated hop blocks for every agent_data id on the record."""
    job = get_job(astral_job_id)
    if not job:
        return None
    job_copy = dict(job)

    collected: List[str] = []
    seen: set[str] = set()

    def _add(raw: Any) -> None:
        aid = str(raw).strip() if raw is not None else ""
        if not aid or aid in seen:
            return
        seen.add(aid)
        collected.append(aid)

    walk_strings = _collect_job_string_values(job_copy)
    hit_map = database.get_agent_data_for_ids(walk_strings) if walk_strings else {}
    for candidate in walk_strings:
        if candidate in hit_map:
            _add(candidate)

    try:
        refs = database.list_entity_latest_agent_refs("job", astral_job_id)
    except Exception as exc:
        logger.warning(
            "assemble_job_copy_snapshot: list_entity_latest_agent_refs failed "
            "astral_job_id=%s: %s",
            astral_job_id,
            exc,
        )
        refs = []
    for ref in refs:
        for block in (ref.get("prompt_blocks") or []):
            if isinstance(block, dict):
                _add(block.get("id"))

    agent_data: Dict[str, Any] = {}
    outcomes: Dict[str, str] = {}
    if collected:
        batch_cache: Dict[str, List[Dict[str, Any]]] = {}
        for aid in collected:
            try:
                seed = database.get_agent_data(aid)
                if not seed:
                    outcomes[aid] = "missing_row"
                    continue
                batch_id = str(seed.get("batch_id") or "").strip()
                if not batch_id:
                    outcomes[aid] = "skipped_no_batch"
                    continue
                if batch_id not in batch_cache:
                    batch_cache[batch_id] = database.get_agent_data_by_batch(batch_id)
                blocks = _hop_blocks_for_batch(batch_cache[batch_id])
                agent_data[aid] = {
                    "id": aid,
                    "block_type": seed.get("block_type") or "",
                    "batch_id": batch_id,
                    "task_key": seed.get("task_key") or "",
                    "blocks": blocks,
                }
                outcomes[aid] = "recorded"
            except Exception as exc:
                logger.warning(
                    "assemble_job_copy_snapshot: hop failed astral_job_id=%s id=%s: %s",
                    astral_job_id,
                    aid,
                    exc,
                )
                outcomes[aid] = "skipped_error"

    snapshot = {"job": job_copy, "agent_data": agent_data}
    if debug:
        dbg = get_logger(__name__, debug_flag=True)
        job_outcome = "assembled" if agent_data else "assembled_no_ids"
        dbg.debug_index(
            func="assemble_job_copy_snapshot",
            index=1,
            total=1,
            identifier=astral_job_id,
            outcome=job_outcome,
        )
        dbg.debug_detail(
            f"found_ids={len(collected)} recorded={len(agent_data)}"
        )
        total = len(collected)
        for i, aid in enumerate(collected, start=1):
            entry = agent_data.get(aid)
            outcome = outcomes.get(aid, "skipped_error")
            dbg.debug_index(
                func="assemble_job_copy_snapshot",
                index=i,
                total=total,
                identifier=aid,
                outcome=outcome,
            )
            if entry is None:
                continue
            hop_types = ",".join(entry["blocks"].keys())
            dbg.debug_detail(
                f"block_type={entry['block_type']} batch_id={entry['batch_id']} "
                f"task_key={entry['task_key']} hop_block_types={hop_types}"
            )
            for block in entry["blocks"].values():
                content = block.get("content")
                if isinstance(content, str):
                    dbg.debug_detail_block(content)
    return snapshot


def _collect_job_string_values(obj: Any) -> List[str]:
    found: List[str] = []
    if isinstance(obj, dict):
        for value in obj.values():
            found.extend(_collect_job_string_values(value))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_collect_job_string_values(item))
    elif isinstance(obj, str):
        stripped = obj.strip()
        if stripped:
            found.append(stripped)
    return found


def _hop_blocks_for_batch(batch_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    blocks: Dict[str, Dict[str, str]] = {}
    for block_type in BLOCK_TYPES:
        last = None
        for row in batch_rows:
            if row.get("block_type") == block_type:
                last = row
        if last is None:
            continue
        blocks[block_type] = {
            "id": str(last.get("agent_data_id") or ""),
            "content": last.get("block_data") or "",
        }
    return blocks


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

def _job_state_matches_prior(current_state: str, prior_states: Optional[List[str]]) -> bool:
    """True when current_state is allowed as a predecessor for a registered transition."""
    if prior_states is None:
        return True
    st = (current_state or "").strip()
    if st in prior_states:
        return True
    parsed = parse_dispatch_hop_label(st)
    if parsed and parsed[0] in prior_states:
        return True
    if legacy_build_artifacts_hop(st) and BUILD_ARTIFACTS_BASE_STATE in prior_states:
        return True
    return False


def legal_job_successor_states(from_state: str) -> List[str]:
    """JOB_STATES keys that transition_job_state would accept from from_state, excluding from_state."""
    current = (from_state or "").strip()
    out: List[str] = []
    for name, cfg in JOB_STATES.items():
        if name == current:
            continue
        if _job_state_matches_prior(current, cfg.get("prior_states")):
            out.append(name)
    return out


def persist_skipped_job_edits(astral_job_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """Persist title/link/JD (and optional state hop) only when job.state is in SKIPPED_STATES."""
    job = get_job(astral_job_id)
    if not job:
        raise ValueError(f"Job not found: {astral_job_id}")
    if (job.get("state") or "") not in SKIPPED_STATES:
        raise ValueError("Job is not in a skipped state")

    # Column + JD writes first so an illegal hop still keeps field edits
    col: Dict[str, Any] = {}
    if "job_title" in fields:
        title = fields["job_title"] if fields["job_title"] is not None else ""
        title = str(title).strip()
        if not title:
            raise ValueError("job_title required")
        col["job_title"] = title
    if "job_link" in fields:
        link = fields["job_link"] if fields["job_link"] is not None else ""
        link = str(link).strip()
        if not link:
            raise ValueError("job_link required")
        col["job_link"] = link
    if "job_description" in fields:
        text = "" if fields["job_description"] is None else str(fields["job_description"])
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        save_job_data(astral_job_id, {jd_key: text})
    if col:
        try:
            if save_job(astral_job_id, **col) is False:
                raise ValueError("job identity collision")
        except sqlite3.IntegrityError as exc:
            if _is_job_identity_unique_violation(exc):
                raise ValueError("job identity collision") from exc
            raise

    if "state" in fields:
        to_state = str(fields["state"] or "").strip()
        if not to_state:
            raise ValueError("state required")
        if to_state != (job.get("state") or ""):
            transition_job_state([astral_job_id], to_state)

    out = get_job(astral_job_id)
    if not out:
        raise ValueError(f"Job not found: {astral_job_id}")
    return out


def write_job_dispatch_hop_label(job_id: str, trigger_state: str, completed_task_key: str) -> str:
    """Write runtime dispatch hop label to job.state (not a JOB_STATES registry key)."""
    label = dispatch_hop_label(trigger_state, completed_task_key)
    job = database.get_job(job_id)
    if not job:
        raise ValueError(f"Job not found: {job_id}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    history = job.get("state_history", [])
    history.append({
        "to_state": label,
        "timestamp": now,
        "batch_id": job.get("batch_id"),
    })
    database.save_job(job_id, state=label, state_history=history, state_changed_at=now)
    return label


def graduate_job_from_dispatch_chain(job_id: str, trigger_state: str) -> str:
    """Terminal chain graduation: runtime hop label or trigger → registered successor state."""
    job = database.get_job(job_id)
    if not job:
        raise ValueError(f"Job not found: {job_id}")
    ts = (trigger_state or "").strip()
    to_state = dispatch_chain_graduation_target(ts)
    if not to_state:
        raise ValueError(f"No graduation target for trigger_state={trigger_state!r}")
    from_state = (job.get("state") or "").strip()
    parsed_hop = parse_dispatch_hop_label(from_state)
    allowed = (
        from_state == ts
        or (parsed_hop is not None and parsed_hop[0] == ts)
        or (ts == BUILD_ARTIFACTS_BASE_STATE and legacy_build_artifacts_hop(from_state) is not None)
    )
    if not allowed:
        raise ValueError(f"Invalid chain graduation from {from_state!r} trigger={trigger_state!r}")
    transition_job_state([job_id], to_state)
    return to_state


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
        if not _job_state_matches_prior(job.get("state") or "", prior_states):
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

def _assert_valid_job_batch_claim_state(state: str) -> None:
    if not is_valid_job_batch_claim_state(state):
        raise ValueError(
            f"Value {state!r} not in allowed list: {_JOB_STATE_LIST} "
            f"(legacy BUILD_ARTIFACTS.<hop> holding states are claim-only)"
        )


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
        _assert_valid_job_batch_claim_state(state)
    else:
        for s in states:
            _assert_valid_job_batch_claim_state(s)
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


def list_timesheets(**kwargs: Any) -> List[Dict[str, Any]]:
    """Thin delegate for layering — UI/core timesheet reads go through tracker, not database."""
    return database.list_timesheets(**kwargs)


def job_misses_dispatch_score_floor(job: Dict[str, Any], floors: Dict[str, float]) -> bool:
    return database.job_misses_dispatch_score_floor(job, floors)


def count_jobs_below_dispatch_score_floor(candidate_id: str) -> int:
    return database.count_jobs_below_dispatch_score_floor(candidate_id)


def list_jobs_below_dispatch_score_floor(candidate_id: str) -> List[Dict[str, Any]]:
    return database.list_jobs_below_dispatch_score_floor(candidate_id)


# ---- AST-1518: contact-task reads (pattern resolve + hydrated getters) ----


def _contact_task_hydrate_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Shallow-copy job and attach agent_story (no coat-check / gazer)."""
    out = dict(job)
    from src.core.agent import get_entity_agent_story

    out["agent_story"] = get_entity_agent_story(out)
    return out


def _job_owned_by_candidate(job: Dict[str, Any], cid: str) -> bool:
    """True when job's company.candidate_id matches cid (not job['candidate_id'])."""
    company_key = job.get("company")
    if not isinstance(company_key, str) or not company_key.strip():
        return False
    company = get_company(company_key.strip())
    if not company:
        return False
    owner = company.get("candidate_id")
    return isinstance(owner, str) and bool(owner.strip()) and owner.strip() == cid


def _match_jobs_by_pattern(cid: str, pat: str) -> List[Dict[str, Any]]:
    """Candidate-scoped jobs whose title/company/link/id match pattern (casefold)."""
    pat_cf = pat.casefold()
    matches: List[Dict[str, Any]] = []
    for job in list_jobs(candidate_id=cid):
        if not isinstance(job, dict):
            continue
        for field in ("astral_job_id", "job_title", "company", "job_link"):
            raw = job.get(field)
            if not isinstance(raw, str) or not raw:
                continue
            if raw == pat or raw.casefold() == pat_cf or pat_cf in raw.casefold():
                matches.append(job)
                break
    return matches


def get_job_by_pattern(
    astral_candidate_id: str, pattern: str
) -> Optional[Dict[str, Any]]:
    """Return the single candidate-scoped job matching pattern, or None if 0/many."""
    cid = (astral_candidate_id or "").strip()
    pat = (pattern or "").strip()
    if not cid or not pat:
        return None
    matches = _match_jobs_by_pattern(cid, pat)
    if len(matches) != 1:
        return None
    return matches[0]


def _contact_task_style_d(
    log,
    *,
    func: str,
    identifier: str,
    found_detail: str,
    recorded_detail: str,
    debug: bool,
) -> None:
    if not debug:
        return
    log.set_debug_flag(True)
    log.debug_index(func=func, index=1, total=2, identifier=identifier, outcome="found")
    for line in truncate_debug_content(found_detail):
        log.debug_detail(line)
    log.debug_index(
        func=func, index=2, total=2, identifier=identifier, outcome="recorded"
    )
    for line in truncate_debug_content(recorded_detail):
        log.debug_detail(line)


def contact_task_get_job_by_pattern(
    astral_candidate_id: str, param: str, *, debug: bool = False
) -> dict:
    """CONTACT_TASK_CONFIG handler: resolve one hydrated job by text pattern."""
    log = get_logger(__name__)
    task_key = "get_job_by_pattern"
    cid = (astral_candidate_id or "").strip()
    pat = (param or "").strip()
    found = f"param={pat!r}"

    if not cid:
        row = {"ok": False, "error": "no_candidate", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_by_pattern",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=no_candidate",
            debug=debug,
        )
        return row
    if not pat:
        row = {"ok": False, "error": "unmatched_pattern", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_by_pattern",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=unmatched_pattern",
            debug=debug,
        )
        return row

    matches = _match_jobs_by_pattern(cid, pat)
    if len(matches) == 0:
        row = {"ok": False, "error": "unmatched_pattern", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_by_pattern",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=unmatched_pattern",
            debug=debug,
        )
        return row
    if len(matches) > 1:
        row = {"ok": False, "error": "ambiguous_pattern", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_by_pattern",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=ambiguous_pattern",
            debug=debug,
        )
        return row

    job = matches[0]
    if not _job_owned_by_candidate(job, cid):
        row = {"ok": False, "error": "refused_cross_candidate", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_by_pattern",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=refused_cross_candidate",
            debug=debug,
        )
        return row

    hydrated = _contact_task_hydrate_job(job)
    row = {"ok": True, "task_key": task_key, "result": hydrated}
    _contact_task_style_d(
        log,
        func="tracker.contact_task_get_job_by_pattern",
        identifier=task_key,
        found_detail=found,
        recorded_detail=f"ok=True astral_job_id={hydrated.get('astral_job_id')!r}",
        debug=debug,
    )
    return row


def contact_task_get_job_data(
    astral_candidate_id: str, param: str, *, debug: bool = False
) -> dict:
    """CONTACT_TASK_CONFIG handler: hydrated job by id (candidate-owned only)."""
    log = get_logger(__name__)
    task_key = "get_job_data"
    cid = (astral_candidate_id or "").strip()
    jid = (param or "").strip()
    found = f"param={jid!r}"

    if not cid:
        row = {"ok": False, "error": "no_candidate", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=no_candidate",
            debug=debug,
        )
        return row
    if not jid:
        row = {"ok": False, "error": "not_found", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=not_found",
            debug=debug,
        )
        return row

    job = get_job(jid)
    if not job:
        row = {"ok": False, "error": "not_found", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=not_found",
            debug=debug,
        )
        return row
    if not _job_owned_by_candidate(job, cid):
        row = {"ok": False, "error": "refused_cross_candidate", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_job_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=refused_cross_candidate",
            debug=debug,
        )
        return row

    hydrated = _contact_task_hydrate_job(job)
    row = {"ok": True, "task_key": task_key, "result": hydrated}
    _contact_task_style_d(
        log,
        func="tracker.contact_task_get_job_data",
        identifier=task_key,
        found_detail=found,
        recorded_detail=f"ok=True astral_job_id={hydrated.get('astral_job_id')!r}",
        debug=debug,
    )
    return row


def contact_task_get_company_data(
    astral_candidate_id: str, param: str, *, debug: bool = False
) -> dict:
    """CONTACT_TASK_CONFIG handler: company by short_name (candidate-scoped)."""
    log = get_logger(__name__)
    task_key = "get_company_data"
    cid = (astral_candidate_id or "").strip()
    sn = (param or "").strip()
    found = f"param={sn!r}"

    if not cid:
        row = {"ok": False, "error": "no_candidate", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_company_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=no_candidate",
            debug=debug,
        )
        return row
    if not sn:
        row = {"ok": False, "error": "not_found", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_company_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=not_found",
            debug=debug,
        )
        return row

    company = get_company(sn)
    if not company:
        row = {"ok": False, "error": "not_found", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_company_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=not_found",
            debug=debug,
        )
        return row

    owner = company.get("candidate_id")
    if isinstance(owner, str) and owner.strip():
        scoped = owner.strip() == cid
    else:
        short = company.get("short_name") or sn
        scoped = any(
            isinstance(j, dict) and j.get("company") == short
            for j in list_jobs(candidate_id=cid)
        )
    if not scoped:
        row = {"ok": False, "error": "refused_cross_candidate", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_company_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=refused_cross_candidate",
            debug=debug,
        )
        return row

    from src.core.agent import get_entity_agent_story

    out = dict(company)
    out["agent_story"] = get_entity_agent_story(out)
    row = {"ok": True, "task_key": task_key, "result": out}
    _contact_task_style_d(
        log,
        func="tracker.contact_task_get_company_data",
        identifier=task_key,
        found_detail=found,
        recorded_detail=f"ok=True short_name={out.get('short_name')!r}",
        debug=debug,
    )
    return row


def contact_task_get_candidate_data(
    astral_candidate_id: str, param: str, *, debug: bool = False
) -> dict:
    """CONTACT_TASK_CONFIG handler: candidate row or dotted candidate_data path."""
    log = get_logger(__name__)
    task_key = "get_candidate_data"
    cid = (astral_candidate_id or "").strip()
    path = (param or "").strip()
    found = f"param={path!r}"

    if not cid:
        row = {"ok": False, "error": "no_candidate", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_candidate_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=no_candidate",
            debug=debug,
        )
        return row

    cand = candidate_mod.get_candidate(cid)
    if not cand:
        row = {"ok": False, "error": "not_found", "task_key": task_key}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_candidate_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail="ok=False error=not_found",
            debug=debug,
        )
        return row

    if path:
        cur: Any = cand.get("candidate_data")
        if not isinstance(cur, dict):
            row = {"ok": False, "error": "not_found", "task_key": task_key}
            _contact_task_style_d(
                log,
                func="tracker.contact_task_get_candidate_data",
                identifier=task_key,
                found_detail=found,
                recorded_detail="ok=False error=not_found",
                debug=debug,
            )
            return row
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                row = {"ok": False, "error": "not_found", "task_key": task_key}
                _contact_task_style_d(
                    log,
                    func="tracker.contact_task_get_candidate_data",
                    identifier=task_key,
                    found_detail=found,
                    recorded_detail="ok=False error=not_found",
                    debug=debug,
                )
                return row
            cur = cur[part]
        row = {"ok": True, "task_key": task_key, "result": cur}
        _contact_task_style_d(
            log,
            func="tracker.contact_task_get_candidate_data",
            identifier=task_key,
            found_detail=found,
            recorded_detail=f"ok=True path={path!r}",
            debug=debug,
        )
        return row

    from src.core.agent import get_entity_agent_story

    out = dict(cand)
    out["agent_story"] = get_entity_agent_story(out)
    row = {"ok": True, "task_key": task_key, "result": out}
    _contact_task_style_d(
        log,
        func="tracker.contact_task_get_candidate_data",
        identifier=task_key,
        found_detail=found,
        recorded_detail=f"ok=True astral_candidate_id={cid!r}",
        debug=debug,
    )
    return row
