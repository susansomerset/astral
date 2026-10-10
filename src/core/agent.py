# -*- coding: utf-8 -*-
"""
Core agent orchestration module.

Single entry point for all AI agent interactions. Owns do_task, prompt assembly,
agent_data storage, and cost calculation. Keeps anthropic.py as a pure API client.

Land packet enrichment (AST-1470): consult.enrich_meteorite_land_packet calls
do_task(task_key="qualify_meteorite", index="qualify_meteorite_batch_{batch_id}")
with log_batch_id set to qualify_meteorite-land-{uuid} before a job row exists;
agent_data for that index is audit-only (no latest-ref consumers until Tracker save).

Company stem (AST-1494): qualify_meteorite RESPONSE items may include optional
company_stem (TASK_CONFIG schema); land enrich maps it in consult; do_task validation
uses the existing schema path — no new decode helper.

Layer: core → data, external, utils  (never ← ui)
"""

import asyncio
import functools
import hashlib
import inspect
import json
import copy
import re
import sys
import uuid
_uuid4 = uuid.uuid4  # bind at import — hop/adhoc ledger IDs avoid test patches on uuid module
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.data import database
from src.data.database import (
    get_agent_task,
    get_agent,
    save_agent_data,
    get_agent_data_by_batch,
    list_agent_data_batches,
    get_agent_data as _get_agent_data_row,
    get_agent_data_for_ids,
    sum_cost_by_batch,
    store_feedback_block,
    insert_vector_feedback_rows,
    list_rubric_vector_uuid_by_code,
)
from src.core.timesheets import record_timesheet_entry
from src.external.anthropic import send_to_anthropic, getTimestampPrefix
from src.utils.llm_external import (
    extract_api_response_text,
    normalize_provider_error,
)
from src.external.llm_compat import send_to_llm_compat
from src.utils.config import (
    TASK_CONFIG, BASE_SCHEMA, BLOCK_TYPES, ASTRAL_CONFIG, BUILD_CONFIG,
    INFLOW_CONFIG,
    resolve_tokens, CHARS_PER_TOKEN,
    chain_context_selected_agent,
    get_llm_server,
    resolve_agent_settings,
    CALLER_HOP_TOKEN_NAMES,
    ENTITY_TYPES,
    _CRAFT_RESUME_NORMALIZE_TASK_KEYS,
    get_task_keys,
    dispatch_chain_graduation_target,
    _TOKEN_RE,
    list_artifact_keys_in_prompt_texts,
    RUBRIC_FEEDBACK_CONFIG,
    is_vector_feedback_task,
    is_conversational_task,
    CONVERSATIONAL_PERFORMANCE_SCHEMA,
    rubric_owner_task_key,
    JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK,
    resolve_task_key_for_content,
    METEORITE_EMAIL_PARSE_CONFIG,
)
from src.utils.rubric_feedback import (
    format_vector_reviews_raw,
    normalize_vector_reviews_raw,
    parse_vector_reviews_diagnostic,
)
from src.utils.formatting import (
    clean_encoded_agent_payload,
    coerce_grades_encoded_json_parse,
    hydrate_entity_labels,
    split_entity_segments,
)
from src.utils.logging import flush_log_buffer, get_logger, log_batch_id, log_candidate_id, log_debug

logger = get_logger(__name__)


def _with_log_debug(fn):
    """Set log_debug from debug= for this frame; nested do_task set/reset is correct."""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        bound = inspect.signature(fn).bind_partial(*args, **kwargs)
        bound.apply_defaults()
        _dbg = log_debug.set(
            True if bound.arguments.get("debug", False) else log_debug.get()
        )
        try:
            return await fn(*args, **kwargs)
        finally:
            log_debug.reset(_dbg)
    return wrapper


def _warn_hop_no_success(task_key: str, why: str) -> None:
    logger.warning(
        "%s skipped — %s\n  This hop is not persisting a success RESPONSE",
        task_key,
        why,
    )


def _log_swallowed_agent_data(who: Any, what: str, exc: Optional[BaseException] = None) -> None:
    if exc is None:
        exc = sys.exc_info()[1]
    logger.exception(
        "%s | %s\n  %s: %s\n  Continuing without that agent_data row",
        who or "-",
        what,
        type(exc).__name__ if exc is not None else "Exception",
        exc,
    )


# Sentinel: production _store_prompt_blocks passes four cache slots; pytest uses legacy ``cache_content=``.
_PB_SLOT_OMIT = object()

# Batch encoded consult dispatch: models must return the usual JSON envelope, not bare compact lines (AST-501 / AST-503).
_STRICT_ENCODED_BATCH_CONSULT_KEYS = frozenset({
    "qualify_job_listings",
    "evaluate_jd",
    "evaluate_meteorite",
    "grade_do",
    "grade_get",
    "grade_like",
    "meteorite_like",
})


def _is_strict_encoded_batch_consult(task_key: str) -> bool:
    """True when task_key (or its content master) is in the strict encoded-batch set."""
    return resolve_task_key_for_content(task_key) in _STRICT_ENCODED_BATCH_CONSULT_KEYS


def _strict_encoded_batch_consult_envelope_err(task_key: str, parsed: Any) -> Optional[str]:
    """Return error detail if encoded-batch consult response bypasses envelope rules; otherwise None."""
    if not _is_strict_encoded_batch_consult(task_key) or parsed is None:
        return None
    if isinstance(parsed, str):
        return (
            "Encoded batch consult tasks require JSON with agent_performance "
            "and agent_payload keys; bare text / compact lines alone are rejected"
        )
    if not isinstance(parsed, dict):
        return "Response must be the standard JSON envelope object"
    perf = parsed.get("agent_performance")
    apl = parsed.get("agent_payload")
    if perf is None or apl is None:
        return "Response must include non-null agent_performance and agent_payload (standard envelope)"
    if isinstance(apl, dict):
        return "agent_payload must be the newline-separated encoded string (or list of lines), not structured JSON rows"
    return None


# ---------------------------------------------------------------------------
# _decode_payload — compact encoded payload → response_schema shape
# ---------------------------------------------------------------------------

# Built from config so valid_grades is the single source of truth for grade letters.
_valid_grade_letters = "".join(ASTRAL_CONFIG.get("valid_grades", []))
# Each segment: 2-char vector code + 1 grade letter + 1 confidence digit (0 for X, 1–5 otherwise).
_GRADE_SEG = re.compile(rf"^[A-Z]{{2}}[{_valid_grade_letters}][0-5]$")


def _validate_grade_confidence_list(grades: list, label: str) -> Optional[str]:
    """AST-357: every grade row must carry confidence; X uses 0, all other letters use 1–5."""
    for idx, g in enumerate(grades):
        if not isinstance(g, dict):
            return f"{label}[{idx}] must be object, got {type(g).__name__}"
        letter = g.get("grade", "")
        conf = g.get("confidence")
        if not isinstance(conf, int):
            return f"{label}[{idx}] confidence must be int, got {type(conf).__name__}"
        if letter == "X":
            if conf != 0:
                return f"{label}[{idx}] grade X requires confidence 0, got {conf}"
        else:
            if conf not in (1, 2, 3, 4, 5):
                return f"{label}[{idx}] confidence must be 1-5 for non-X, got {conf}"
    return None


def _inner_task_payload(parsed: Any) -> Any:
    """Resolve agent_payload (or flat) task field object from API parse."""
    if not isinstance(parsed, dict):
        return parsed
    ap = parsed.get("agent_payload")
    if ap is not None:
        return ap
    return parsed


def _effective_entity_type(task_config: Dict[str, Any], index: Optional[str]) -> str:
    """TASK_CONFIG entity_type, or candidate when craft tasks omit it but have an index."""
    et = (task_config.get("entity_type") or "").strip()
    if et:
        return et
    if task_config.get("requires_candidate_key") and index:
        return "candidate"
    return ""


def _validate_grade_confidence_in_payload(parsed: Any, task_key: str) -> Optional[str]:
    """Walk decoded payload for grades[] or jobs/companies[].grades[] and validate confidence rules."""
    if not isinstance(parsed, dict):
        return None
    for arr_key in ("jobs", "companies"):
        rows = parsed.get(arr_key)
        if isinstance(rows, list):
            for ji, row in enumerate(rows):
                if not isinstance(row, dict):
                    continue
                glist = row.get("grades")
                if isinstance(glist, list) and glist:
                    err = _validate_grade_confidence_list(
                        glist, f"{task_key} {arr_key}[{ji}].grades"
                    )
                    if err:
                        return err
    glist = parsed.get("grades")
    if isinstance(glist, list) and glist:
        return _validate_grade_confidence_list(glist, f"{task_key} grades")
    return None


def _decode_payload(task_key: str, output_type: str, payload: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Parse compact pipe-delimited agent_payload string into response_schema shape.

    Grade segments: _GRADE_SEG = 2-char code + grade letter + confidence digit (AST-357).
    pos → astral_job_id (job) or company_id (company entity_type) via ctx["batch_index_map"] (batch-unique
    index → entity) when supplied, else positionally via ctx["batch_entities"]. Under a map, an unknown index
    is skipped (entity falls out as omitted) and an index on several lines is one decode_failure (AST-2093).
    Vector names: ctx["vector_labels"] maps 2-char codes to full rubric labels; falls back to
    raw 2-char code when the map is absent or incomplete. _render_pass_fail ignores vector names;
    _render_score requires rubric criteria with labels — callers guard with `if rubric_list` before scoring (AST-429).
    "_meta" in output_type determines whether metadata fields after grades are accepted;
    trailing non-grade content on a grades-only line, an X segment with nonzero
    confidence, and a "grades_encoded_notes" line with no grade segments (AST-2126) are recorded in "decode_failures" (id, pos, reason) and the line is skipped so the caller can
    retry that entity; other per-line errors still raise (AST-1996).
    A letter segment with confidence 0 is stored as X0 (AST-2124).
    "grades_encoded_notes" (do/get/like): non-segment tail rejoins to job["notes"] only (optional).
    """
    with_meta = "_meta" in output_type or output_type == "grades_encoded_prefilter_links"
    with_notes = output_type == "grades_encoded_notes"
    batch_entities = (ctx or {}).get("batch_entities") or []
    payload = clean_encoded_agent_payload(payload or "")
    lines = [ln for ln in payload.splitlines() if ln.strip()]

    # AST-880: link-type vet → results[{hit_index, grade, website, confidence}]
    if output_type == "grades_encoded_vet_meta":
        vet_cfg = INFLOW_CONFIG["vet"]
        vector_code = vet_cfg["grade_vector_code"]
        allowed_grades = vet_cfg["pass_grades"] | vet_cfg["fail_grades"]
        valid_letters = set(ASTRAL_CONFIG.get("valid_grades", []))
        result_rows: List[Dict[str, Any]] = []
        logger.debug("Beginning decode loop on %s items", len(lines))
        for line in lines:
            fields = [f.strip() for f in line.split("|")]
            try:
                pos = int(fields[0])
            except (ValueError, IndexError):
                raise ValueError(f"[{task_key}] bad position field in line: {line!r}")
            if pos < 0 or pos >= len(batch_entities):
                logger.warning(
                    "%s skipped — pos %s out of range for this batch\n  This line is not being graded",
                    task_key,
                    pos,
                )
                continue
            if len(fields) < 3:
                raise ValueError(f"[{task_key}] vet line needs pos|LT{{grade}}{{conf}}|website: {line!r}")
            norm = "".join(ch for ch in fields[1] if ch not in " -:")
            if not _GRADE_SEG.match(norm) or norm[:2] != vector_code:
                raise ValueError(f"[{task_key}] bad LT grade segment in line: {line!r}")
            grade, conf_d = norm[2], int(norm[3])
            if conf_d not in (1, 2, 3, 4, 5):
                raise ValueError(
                    f"[{task_key}] non-X grade requires confidence 1-5, got {conf_d} in segment {norm!r} (line {line!r})"
                )
            website = "|".join(fields[2:]).strip()
            if not website:
                raise ValueError(f"[{task_key}] missing website on vet line: {line!r}")
            if grade not in valid_letters or grade not in allowed_grades:
                raise ValueError(f"[{task_key}] illegal vet grade {grade!r} in line: {line!r}")
            result_rows.append({
                "hit_index": pos,
                "grade": grade,
                "website": website,
                "confidence": conf_d,
            })
        logger.debug("End decode loop after %s items", len(result_rows))
        return {"results": result_rows}

    # Company vs job id field / result array (AST-1723) — job path unchanged.
    entity_type = (TASK_CONFIG.get(task_key) or {}).get("entity_type") or ""
    company_decode = entity_type == "company"
    id_key = "company_id" if company_decode else "astral_job_id"
    array_key = "companies" if company_decode else "jobs"

    vector_labels: Dict[str, str] = (ctx or {}).get("vector_labels") or {}
    result_rows: List[Dict[str, Any]] = []
    decode_failures: List[Dict[str, Any]] = []
    # AST-2093: batch-unique index → entity. When present, a line binds by its index, never by list position.
    index_map: Dict[int, Dict[str, Any]] = (ctx or {}).get("batch_index_map") or {}
    index_counts: Dict[int, int] = {}
    if index_map:
        # Pre-pass: an index echoed on several lines can't be trusted for any of them.
        for line in lines:
            try:
                p = int(line.split("|")[0].strip())
            except ValueError:
                raise ValueError(f"[{task_key}] bad position field in line: {line!r}")
            index_counts[p] = index_counts.get(p, 0) + 1
    dup_reported: set = set()
    logger.debug("Beginning decode loop on %s items", len(lines))
    for line in lines:
        fields = [f.strip() for f in line.split("|")]
        try:
            pos = int(fields[0])
        except (ValueError, IndexError):
            raise ValueError(f"[{task_key}] bad position field in line: {line!r}")
        if index_map:
            ent = index_map.get(pos)
            if ent is None:
                # Unknown index — its intended entity falls out as "omitted from response" and retries.
                logger.warning(
                    "%s skipped — index %s not in this batch\n  This line is not being graded",
                    task_key,
                    pos,
                )
                continue
            n = index_counts.get(pos, 0)
            if n > 1:
                # One failure per collided index; every line carrying it is dropped.
                if pos not in dup_reported:
                    dup_reported.add(pos)
                    decode_failures.append({
                        id_key: ent[id_key],
                        "pos": pos,
                        "reason": f"[{task_key}] duplicate row index {pos:03d} on {n} lines",
                    })
                continue
        elif pos < 0 or pos >= len(batch_entities):
            # Model occasionally 1-indexes at round-number boundaries (e.g. returns 100 for last item in batch of 100).
            # Skip the line rather than killing the whole batch — the job stays in its current state and retries next run.
            logger.warning(
                "%s skipped — pos %s out of range for this batch\n  This line is not being graded",
                task_key,
                pos,
            )
            continue
        else:
            ent = batch_entities[pos]

        grade_segs, meta = [], []
        for f in fields[1:]:
            # Strip ASCII space, hyphen, colon for grade match only; meta keeps pipe-stripped original (AST-483).
            norm = "".join(ch for ch in f if ch not in " -:")
            if _GRADE_SEG.match(norm):
                grade_segs.append(norm)
            else:
                meta.append(f)

        if meta and not with_meta and not with_notes:
            # One malformed line must not sink the batch — caller routes this entity retry/error (AST-1996).
            # Reason text matches the old ValueError so existing log greps keep working.
            decode_failures.append({
                id_key: ent[id_key],
                "pos": pos,
                "reason": f"[{task_key}] unexpected trailing content in grades-only line: {line!r}",
            })
            continue
        if with_notes and not grade_segs:
            # A notes-only line has no grades to score — retry the entity, keep the raw line (AST-2126).
            decode_failures.append({
                id_key: ent[id_key],
                "pos": pos,
                "reason": f"[{task_key}] no grade segments in encoded line: {line!r}",
            })
            continue

        codes = [seg[:2] for seg in grade_segs]
        if len(codes) != len(set(codes)):
            dupes = sorted({c for c in codes if codes.count(c) > 1})
            raise ValueError(
                f"[{task_key}] duplicate vector code {','.join(dupes)} in encoded line: {line!r}"
            )

        grade_rows: List[Dict[str, Any]] = []
        bad_conf: Optional[str] = None
        for seg in grade_segs:
            code, letter, conf_ch = seg[:2], seg[2], seg[3]
            conf_d = int(conf_ch)
            # Illegal confidence is a bad line, not a hop failure. Caller retries that entity.
            # Reason text matches the old ValueError so existing log greps keep working.
            if letter == "X" and conf_d != 0:
                bad_conf = (
                    f"[{task_key}] grade X requires confidence digit 0, got {conf_d} in segment {seg!r} (line {line!r})"
                )
                break
            # Sanctioned slip (astral.agent.confidence-bounds): models write {letter}0 for "no signal" — store X0 (AST-2124).
            if letter != "X" and conf_d == 0:
                letter = "X"
            grade_rows.append(
                {"vector": vector_labels.get(code, code), "grade": letter, "confidence": conf_d}
            )
        if bad_conf:
            decode_failures.append({
                id_key: ent[id_key],
                "pos": pos,
                "reason": bad_conf,
            })
            continue

        row: Dict[str, Any] = {
            id_key: ent[id_key],
            "grades": grade_rows,
        }
        if with_meta:
            if output_type == "grades_encoded_prefilter_links":
                from src.core.consult import _apply_prefilter_encoded_link_meta

                _apply_prefilter_encoded_link_meta(row, meta)
            else:
                for i, key in enumerate(("company_job_id", "job_title", "job_link")):
                    if i < len(meta):
                        row[key] = meta[i] or None
                # key:value extras → job_data dict (location, salary_range, company name, etc.)
                if meta[3:]:
                    row["job_data"] = {
                        k.strip(): (v.strip() or None)
                        for field in meta[3:] if ":" in field
                        for k, v in [field.split(":", 1)]
                    }
        elif with_notes and meta:
            joined = "|".join(meta).strip()
            if joined:
                row["notes"] = joined

        result_rows.append(row)

    logger.debug("End decode loop after %s items", len(result_rows))
    out: Dict[str, Any] = {array_key: result_rows}
    # Key only when a line failed — clean payloads keep the exact {array_key: [...]} shape.
    if decode_failures:
        out["decode_failures"] = decode_failures
    return out


# ---------------------------------------------------------------------------

def _single_job_in_scope(ctx: Optional[Dict[str, Any]], index: Optional[str]) -> bool:
    """True when exactly one job entity is in scope for AST-513 job tokens."""
    if not ctx or not index:
        return False
    bs = ctx.get("batch_size")
    if bs is not None and int(bs) != 1:
        return False
    entities = ctx.get("batch_entities") or []
    if isinstance(entities, list) and len(entities) == 1:
        return str(entities[0].get("astral_job_id") or "") == str(index)
    job = ctx.get("job")
    if isinstance(job, dict) and str(job.get("astral_job_id") or "") == str(index):
        return True
    return False


def _job_row_from_ctx(ctx: Dict[str, Any], index: str) -> Dict[str, Any]:
    row = ctx.get("job")
    if isinstance(row, dict) and str(row.get("astral_job_id") or "") == str(index):
        return row
    for ent in ctx.get("batch_entities") or []:
        if isinstance(ent, dict) and str(ent.get("astral_job_id") or "") == str(index):
            return ent
    return {"astral_job_id": index, "job_data": {}}


def _job_context_for_call(
    ctx: Optional[Dict[str, Any]],
    index: Optional[str],
    cd: dict,
    *,
    debug: bool = False,
) -> Optional[Dict[str, str]]:
    if not _single_job_in_scope(ctx, index):
        return None
    # consult imports do_task at module load; import here only to avoid import cycle.
    from src.core import consult as _consult

    builder = getattr(_consult, "build_job_token_context", None)
    if builder is None:
        return None
    cd_copy = dict(cd)
    cid = str((ctx or {}).get("astral_candidate_id") or "")
    if cid:
        cd_copy["_astral_candidate_id"] = cid
    return builder(
        _job_row_from_ctx(ctx or {}, str(index)), cd_copy, candidate_id=cid, debug=debug
    )


def _token_view_for_do_task(
    ctx: Optional[Dict[str, Any]],
    candidate_data: Optional[Dict[str, Any]],
    index: Optional[str] = None,
) -> dict:
    """Walkable resolve_tokens dict: name columns + library blobs (AST-1192 / AST-1014)."""
    # Lazy import breaks agent↔candidate cycle (candidate imports agent paths).
    from src.core.candidate import (
        build_candidate_token_view,
        get_candidate,
        is_candidate_row_with_name_columns,
        is_candidate_token_view,
    )

    cid = str((ctx or {}).get("astral_candidate_id") or "").strip()
    if cid:
        row = get_candidate(cid)
        if row:
            return build_candidate_token_view(row)
    if is_candidate_row_with_name_columns(ctx):
        return build_candidate_token_view(ctx)  # type: ignore[arg-type]
    # Contact-style: index=<astral_candidate_id>, no ctx — load current-bearing view.
    idx = str(index or "").strip()
    if idx:
        row = get_candidate(idx)
        if row:
            return build_candidate_token_view(row)
    if is_candidate_token_view(candidate_data):
        return dict(candidate_data)  # type: ignore[arg-type]
    return dict(candidate_data or (ctx or {}).get("candidate_data") or {})


def _candidate_identity_material_present(cd: dict) -> bool:
    """True when first/last/full or contact/context hold non-empty identity material."""
    if str(cd.get("first") or "").strip() or str(cd.get("last") or "").strip():
        return True
    if str(cd.get("full") or "").strip():
        return True
    for key in ("contact", "context"):
        blob = cd.get(key)
        if not isinstance(blob, dict):
            continue
        if any(isinstance(v, str) and v.strip() for v in blob.values()):
            return True
    return False


def resolved_task_system(
    agent_row: Dict[str, Any],
    agent_task_row: Dict[str, Any],
    cd: dict,
    task_key: str,
    chain_context: Optional[Dict[str, str]],
    job_context: Optional[Dict[str, str]] = None,
    *,
    chain_entry: bool = False,
    parent_task_key: Optional[str] = None,
    parent_caller_summary: Optional[Dict[str, str]] = None,
    warn_on_empty: bool = True,
    empty_tokens: Optional[list] = None,
) -> str:
    """System block text: per-task ``system_prompt`` when non-empty, else agent ``content`` (AST-305 / AST-361)."""
    raw = (agent_task_row.get("system_prompt") or "").strip()
    base = raw if raw else (agent_row.get("content") or "")
    return resolve_tokens(
        base,
        cd,
        task_key,
        chain_context,
        job_context,
        chain_entry=chain_entry,
        parent_task_key=parent_task_key,
        parent_caller_summary=parent_caller_summary,
        warn_on_empty=warn_on_empty,
        empty_tokens=empty_tokens,
    )


def _resolve_task_prompts(task_key: str):
    """Fetch and validate agent_task + agent rows for prompt/content lookup.

    Alias keys resolve to master_task_key for DB rows (AST-1221); caller identity
    stays the original task_key at do_task / preview call sites.
    """
    content_key = resolve_task_key_for_content(task_key)
    agent_task_row = get_agent_task(content_key)
    # Mailbox fold: empty agent_id on stage_email_meteorite falls back to
    # legacy_agent_task_key parse_meteorite_email. Key lives on METEORITE_EMAIL_PARSE_CONFIG.
    cfg = METEORITE_EMAIL_PARSE_CONFIG
    if content_key == cfg["task_key"] and (
        not agent_task_row or not (agent_task_row.get("agent_id") or "").strip()
    ):
        legacy_row = get_agent_task(cfg["legacy_agent_task_key"])
        if legacy_row and (legacy_row.get("agent_id") or "").strip():
            agent_task_row = legacy_row
            content_key = cfg["legacy_agent_task_key"]
    if not agent_task_row:
        raise ValueError(
            f"No agent_task row for '{content_key}'"
            + (f" (alias '{task_key}')" if content_key != (task_key or "").strip() else "")
            + ". Run sync_agent_tasks or configure via Manage Tasks."
        )
    agent_id = (agent_task_row.get("agent_id") or "").strip()
    if not agent_id:
        raise ValueError(
            f"agent_task '{content_key}' has no agent_id assigned. Configure via Manage Tasks."
        )
    agent_row = get_agent(agent_id)
    if not agent_row:
        raise ValueError(
            f"Agent '{agent_id}' referenced by task '{content_key}' not found."
        )
    return agent_row, agent_task_row


def resolved_agent_content(
    agent_row: Dict[str, Any],
    candidate_data: dict,
    task_key: str,
    job_context: Optional[Dict[str, str]] = None,
    *,
    chain_entry: bool = False,
    parent_task_key: Optional[str] = None,
    parent_caller_summary: Optional[Dict[str, str]] = None,
    warn_on_empty: bool = True,
    empty_tokens: Optional[list] = None,
) -> str:
    """Resolve non-chain tokens in agent.content before SELECTED_AGENT injection (AST-631)."""
    return resolve_tokens(
        agent_row.get("content") or "",
        candidate_data,
        task_key,
        None,  # chain tokens not expected in agent rows
        job_context,
        chain_entry=chain_entry,
        parent_task_key=parent_task_key,
        parent_caller_summary=parent_caller_summary,
        warn_on_empty=warn_on_empty,
        empty_tokens=empty_tokens,
    )


def _chain_context(
    agent_row: Dict[str, Any],
    candidate_data: dict,
    task_key: str,
    job_context: Optional[Dict[str, str]] = None,
    extra: Optional[Dict[str, str]] = None,
    *,
    chain_entry: bool = False,
    parent_task_key: Optional[str] = None,
    parent_caller_summary: Optional[Dict[str, str]] = None,
    warn_on_empty: bool = True,
    empty_tokens: Optional[list] = None,
) -> Dict[str, str]:
    """Chain/runtime tokens for resolve_tokens (AST-304). SELECTED_AGENT = resolved agent body (AST-631)."""
    resolved_body = resolved_agent_content(
        agent_row,
        candidate_data,
        task_key,
        job_context,
        chain_entry=chain_entry,
        parent_task_key=parent_task_key,
        parent_caller_summary=parent_caller_summary,
        warn_on_empty=warn_on_empty,
        empty_tokens=empty_tokens,
    )
    base = chain_context_selected_agent(resolved_body)
    if not extra:
        return base
    out = dict(base)
    for k, v in extra.items():
        if not k.startswith("_"):
            out[k] = v
    return out


def _caller_response_blob(parsed: Any) -> str:
    if isinstance(parsed, (dict, list)):
        return json.dumps(parsed, ensure_ascii=False, default=str)
    if parsed is not None:
        return str(parsed)
    return ""


def _chain_tokens_for_next_hop(
    *,
    parsed: Any,
    resolved_system: str = "",
    resolved_cache_a: str = "",
    resolved_cache_b: str = "",
    resolved_cache_c: str = "",
    resolved_cache_d: str = "",
    **legacy_kw: Any,
) -> Dict[str, str]:
    """Hop tokens for the next hop. AST-455: {$CALLER_*}. Legacy ABI (pre-455 tests): CACHE_BLOCK_* from block-shaped text."""
    caller = _caller_response_blob(parsed)
    if legacy_kw:
        extras = set(legacy_kw.keys()) - {"system_content", "cache_content", "nocache_content", "live_content"}
        if extras:
            raise TypeError(f"_chain_tokens_for_next_hop() got unexpected keyword arguments: {sorted(extras)}")
        sys_c_raw = legacy_kw.get("system_content", "")
        sys_c = sys_c_raw if isinstance(sys_c_raw, str) else ("" if sys_c_raw is None else str(sys_c_raw))
        cc_slot = legacy_kw.get("cache_content") or ""
        nc_slot = legacy_kw.get("nocache_content") or ""
        lv_slot = legacy_kw.get("live_content") or ""
        return {
            "CALLER_RESPONSE": caller,
            "CACHE_BLOCK_A": sys_c or "",
            "CACHE_BLOCK_B": (f"--- CACHED CONTEXT ---\n{cc_slot}") if cc_slot else "",
            "CACHE_BLOCK_C": (f"--- ADDITIONAL CONTEXT ---\n{nc_slot}") if nc_slot else "",
            "CACHE_BLOCK_D": (f"--- CONTENT ---\n{lv_slot}") if lv_slot else "",
        }
    return {
        "CALLER_RESPONSE": caller,
        "CALLER_SYSTEM": resolved_system or "",
        "CALLER_CACHE_A": resolved_cache_a or "",
        "CALLER_CACHE_B": resolved_cache_b or "",
        "CALLER_CACHE_C": resolved_cache_c or "",
        "CALLER_CACHE_D": resolved_cache_d or "",
    }


def _merge_chain_context_for_next_hop(
    parent_chain_context: Optional[Dict[str, str]],
    hop_ctx: Dict[str, str],
) -> Dict[str, str]:
    """AST-370: inherit outer chain keys across run_next hops; hop_ctx wins on overlap.

    Parent SELECTED_AGENT is omitted so each hop still gets the current agent from chain_context_selected_agent.
    AST-597: omit _caller_hydration_source so chained hops report caller_source=live_llm (Radia review).
    """
    merged: Dict[str, str] = {}
    if parent_chain_context:
        for k, v in parent_chain_context.items():
            if k not in ("SELECTED_AGENT", "_caller_hydration_source"):
                merged[k] = v
    merged.update(hop_ctx)
    return merged


def _incoming_chain_context(chain_context: Optional[Dict[str, str]]) -> Dict[str, str]:
    return dict(chain_context) if chain_context else {}


def _is_chain_entry(incoming: Optional[Dict[str, str]]) -> bool:
    """True when no CALLER_* keys on the incoming hop context (chain dispatch entry)."""
    ctx = _incoming_chain_context(incoming)
    return not any(k.startswith("CALLER_") for k in ctx)


def _referenced_caller_tokens(*texts: Optional[str]) -> set[str]:
    needed: set[str] = set()
    for text in texts:
        if not text:
            continue
        for match in _TOKEN_RE.finditer(text):
            name = match.group(1)
            if name in CALLER_HOP_TOKEN_NAMES:
                needed.add(name)
    return needed


# AST-597: mid-chain resume — hydrate {$CALLER_*} from stored agent_data
_HOP_FAILURE_RESPONSE_PREFIXES = (
    "Validation failed:",
    "Schema parse failed:",
    "JSON parse failed:",
    "Required caller token",
)


def _block_text_by_type(
    prompt_blocks: List[Dict[str, str]],
    block_type: str,
    *,
    debug: bool = False,
) -> str:
    ids: List[str] = []
    for ref in prompt_blocks or []:
        if isinstance(ref, dict) and ref.get("type") == block_type and ref.get("id"):
            ids.append(str(ref["id"]))
    if not ids:
        return ""
    data_map = get_agent_data_for_ids(ids)
    logger.debug("Beginning agent_data_read loop on %s items", len(ids))
    for ref in prompt_blocks or []:
        if not isinstance(ref, dict) or ref.get("type") != block_type:
            continue
        bid = ref.get("id")
        if not bid:
            continue
        row = data_map.get(str(bid), {})
        data = row.get("block_data") or row.get("content") or ""
        if isinstance(data, str) and data.strip():
            logger.debug("End agent_data_read loop after %s items", 1)
            return data.strip()
    logger.debug("End agent_data_read loop after %s items", 0)
    return ""


def _parsed_response_from_stored_response_text(text: str, task_key: str) -> Any:
    stripped = (text or "").strip()
    if not stripped:
        return None
    parsed: Any
    if stripped[0] in "{[":
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            parsed = stripped
    else:
        parsed = stripped
    if isinstance(parsed, dict) and "agent_payload" in parsed:
        parsed = parsed["agent_payload"]
        if isinstance(parsed, list):
            parsed = "\n".join(str(item) for item in parsed)
    return parsed


def _entity_row(entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
    if entity_type == "job":
        from src.core import tracker

        return tracker.get_job(entity_id)
    if entity_type == "company":
        from src.core import tracker

        return tracker.get_company(entity_id)
    if entity_type == "candidate":
        from src.core.candidate import get_candidate

        return get_candidate(entity_id)
    return None


def _anchor_batch_id_from_state_history(entity: Dict[str, Any]) -> Optional[str]:
    history = entity.get("state_history") or []
    if not history:
        return None
    current_state = (entity.get("state") or "").strip()
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        if (entry.get("to_state") or "").strip() != current_state:
            continue
        batch_id = entry.get("batch_id")
        if isinstance(batch_id, str) and batch_id.strip():
            return batch_id.strip()
    return None


def _caller_anchor_batch_id(
    entity: Dict[str, Any],
    chain_context: Optional[Dict[str, str]],
) -> Optional[str]:
    raw = (chain_context or {}).get("_caller_anchor_batch_id")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    bid = log_batch_id.get()
    if isinstance(bid, str) and bid.strip():
        return bid.strip()
    return _anchor_batch_id_from_state_history(entity)


def _parent_hop_task_key_for_child(child_task_key: str) -> Optional[str]:
    matches: List[str] = []
    for tk in get_task_keys():
        row = get_agent_task(tk)
        if not row:
            continue
        if (row.get("run_next") or "").strip() == child_task_key:
            matches.append(tk)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        logger.warning(
            "%s has more than one run_next parent: %s\n  Parent hop will not be hydrated from agent_data",
            child_task_key,
            matches,
        )
        return None
    return None


def _hop_agent_ref_for_parent(
    entity_type: str,
    entity_id: str,
    parent_task_key: str,
    anchor_batch_id: Optional[str],
    *,
    debug: bool = False,
) -> Optional[Dict[str, Any]]:
    # AST-984: latest-per-task refs from agent_data.entity_id (not entity JSON column)
    entries = database.list_entity_latest_agent_refs(entity_type, entity_id)
    candidates = [
        ref for ref in entries
        if isinstance(ref, dict) and (ref.get("task_key") or "").strip() == parent_task_key
    ]
    ordered = candidates
    if anchor_batch_id:
        anchored = [
            ref for ref in candidates
            if (ref.get("batch_id") or "").strip() == anchor_batch_id
        ]
        ordered = anchored + [r for r in candidates if r not in anchored]
    for ref in ordered:
        blocks = ref.get("prompt_blocks") or []
        if not any(isinstance(b, dict) and b.get("type") == "RESPONSE" for b in blocks):
            continue
        response_raw = _block_text_by_type(blocks, "RESPONSE", debug=debug)
        if response_raw and response_raw.startswith(_HOP_FAILURE_RESPONSE_PREFIXES):
            continue
        return ref
    return None


def _task_prompt_texts(
    agent_task_row: Dict[str, Any],
    live_content: Optional[str],
) -> Dict[str, str]:
    return {
        "system": (agent_task_row.get("system_prompt") or "").strip(),
        "user": agent_task_row.get("user_prompt") or "",
        "cache_a": agent_task_row.get("cache_prompt") or "",
        "cache_b": agent_task_row.get("cache_prompt_b") or "",
        "cache_c": agent_task_row.get("cache_prompt_c") or "",
        "cache_d": agent_task_row.get("cache_prompt_d") or "",
        "nocache": agent_task_row.get("nocache_prompt") or "",
        "live": live_content or "",
    }


def harvest_source_artifact_ids(
    *texts: str,
    candidate_id: Optional[str] = None,
) -> list[str]:
    """Deduped current artifact_uuid pins for artifact-typed {$TOKEN}s in ``texts``.

    Parse/classify via config ``list_artifact_keys_in_prompt_texts``; resolve each
    key with ``get_candidate_current_artifact_uuid``. Missing candidate_id or
    missing current rows omit that id (no coat-check, no invent). Order = first
    successful resolve; UUID duplicates collapsed (set semantics).
    """
    if not (candidate_id or "").strip():
        return []
    keys = list_artifact_keys_in_prompt_texts(*texts)
    # Late import: avoid agent↔candidate cycle if candidate later imports agent.
    from src.core.candidate import get_candidate_current_artifact_uuid

    out: list[str] = []
    seen: set[str] = set()
    for key in keys:
        try:
            uuid = get_candidate_current_artifact_uuid(candidate_id, key)
        except ValueError:
            continue
        if not isinstance(uuid, str) or not uuid.strip():
            continue
        if uuid in seen:
            continue
        seen.add(uuid)
        out.append(uuid)
    return out


def _task_references_caller_tokens(
    agent_task_row: Dict[str, Any],
    live_content: Optional[str],
) -> bool:
    return bool(
        _referenced_caller_tokens(*_task_prompt_texts(agent_task_row, live_content).values())
    )


def _hydrate_caller_chain_context(
    entity_type: str,
    entity_id: str,
    entry_task_key: str,
    parent_task_key: str,
    chain_context: Optional[Dict[str, str]],
    *,
    debug: bool = False,
) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    if entity_type not in ENTITY_TYPES:
        return (None, f"Unknown entity_type: {entity_type!r}")
    entity = _entity_row(entity_type, entity_id)
    if not entity:
        return (None, f"{entity_type} not found: {entity_id} (hop={entry_task_key!r})")
    anchor = _caller_anchor_batch_id(entity, chain_context)
    ref = _hop_agent_ref_for_parent(entity_type, entity_id, parent_task_key, anchor)
    if ref is None and anchor:
        ref = _hop_agent_ref_for_parent(entity_type, entity_id, parent_task_key, None)
    if ref is None:
        return (
            None,
            f"No stored agent_data for upstream hop {parent_task_key!r} on {entity_type} {entity_id} (entry={entry_task_key!r})",
        )
    ctx = _caller_chain_context_from_hop_agent_ref(ref, parent_task_key, debug=debug)
    if not any((ctx.get(k) or "").strip() for k in CALLER_HOP_TOKEN_NAMES):
        return (None, f"Stored hop {parent_task_key!r} has empty caller payload (entry={entry_task_key!r})")
    return (ctx, None)


def _merge_hydrated_caller_context(
    incoming: Optional[Dict[str, str]],
    hydrated: Dict[str, str],
) -> Dict[str, str]:
    merged: Dict[str, str] = dict(incoming or {})
    for k in CALLER_HOP_TOKEN_NAMES:
        if k in hydrated:
            merged[k] = hydrated[k]
    if "_caller_hydration_source" in hydrated:
        merged["_caller_hydration_source"] = hydrated["_caller_hydration_source"]
    if "_hop_parent_task_key" in hydrated:
        merged["_hop_parent_task_key"] = hydrated["_hop_parent_task_key"]
    return merged


def _caller_chain_context_from_hop_agent_ref(
    agent_ref: Dict[str, Any],
    parent_task_key: str,
    *,
    debug: bool = False,
) -> Dict[str, str]:
    blocks = agent_ref.get("prompt_blocks") or []
    response_raw = _block_text_by_type(blocks, "RESPONSE", debug=debug)
    parsed = _parsed_response_from_stored_response_text(response_raw, parent_task_key)
    hop_ctx = _chain_tokens_for_next_hop(
        parsed=parsed,
        resolved_system=_block_text_by_type(blocks, "SYSTEM", debug=debug),
        resolved_cache_a=_block_text_by_type(blocks, "CACHE_A", debug=debug),
        resolved_cache_b=_block_text_by_type(blocks, "CACHE_B", debug=debug),
        resolved_cache_c=_block_text_by_type(blocks, "CACHE_C", debug=debug),
        resolved_cache_d=_block_text_by_type(blocks, "CACHE_D", debug=debug),
    )
    hop_ctx["_caller_hydration_source"] = "agent_data"
    hop_ctx["_hop_parent_task_key"] = parent_task_key
    return hop_ctx


def _hydrate_resume_entry_chain_context(
    astral_job_id: str,
    entry_task_key: str,
) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    parent = _parent_hop_task_key_for_child(entry_task_key)
    if parent is None:
        return ({}, None)
    return _hydrate_caller_chain_context(
        "job", astral_job_id, entry_task_key, parent, None
    )


def _dispatch_chain_ctx(ctx: Optional[Dict[str, Any]]) -> tuple[str, bool]:
    if not ctx:
        return "", False
    trigger = str(ctx.get("dispatch_trigger_state") or "").strip()
    graduate = bool(ctx.get("dispatch_chain_graduate_on_terminal"))
    return trigger, graduate


def _should_write_dispatch_hop_label(
    *,
    entity_type: str,
    index: Optional[str],
    ctx: Optional[Dict[str, Any]],
    trigger_state: str,
) -> bool:
    if entity_type != "job" or not index or not trigger_state:
        return False
    return dispatch_chain_graduation_target(trigger_state) is not None


def _should_write_candidate_craft_hop_label(
    *,
    entity_type: str,
    index: Optional[str],
    ctx: Optional[Dict[str, Any]],
    trigger_state: str,
) -> bool:
    """AST-1388 / AST-1434: candidate craft chain success labels (parallel to job gate)."""
    if entity_type != "candidate" or not index or not trigger_state:
        return False
    return bool((ctx or {}).get("persist_candidate_craft_hops"))


def _write_dispatch_hop_label_on_success(
    *,
    task_key: str,
    entity_type: str,
    index: Optional[str],
    ctx: Optional[Dict[str, Any]],
    trigger_state: str,
    debug: bool,
) -> None:
    write_job = _should_write_dispatch_hop_label(
        entity_type=entity_type, index=index, ctx=ctx, trigger_state=trigger_state,
    )
    write_cand = _should_write_candidate_craft_hop_label(
        entity_type=entity_type, index=index, ctx=ctx, trigger_state=trigger_state,
    )
    if not write_job and not write_cand:
        return

    if ctx is not None and "_dispatch_chain_hop_index" not in ctx:
        ctx["_dispatch_chain_hop_index"] = 1
    elif ctx is not None:
        ctx["_dispatch_chain_hop_index"] = int(ctx.get("_dispatch_chain_hop_index") or 0) + 1

    if write_job:
        from src.core import tracker as tracker_mod
        tracker_mod.write_job_dispatch_hop_label(index, trigger_state, task_key)
    else:
        # Lazy import breaks agent↔candidate cycle (candidate imports agent).
        from src.core.candidate import write_candidate_dispatch_hop_label
        write_candidate_dispatch_hop_label(index, trigger_state, task_key)


def _maybe_graduate_dispatch_chain(
    *,
    job_id: str,
    trigger_state: str,
    graduate_on_terminal: bool,
    debug: bool,
) -> None:
    if not graduate_on_terminal or not dispatch_chain_graduation_target(trigger_state):
        return
    from src.core import tracker as tracker_mod

    to_state = tracker_mod.graduate_job_from_dispatch_chain(job_id, trigger_state)
    logger.info(
        "%s | job state: %s -> %s (batch: %s)",
        job_id,
        trigger_state,
        to_state,
        log_batch_id.get() or "-",
    )


# Outcome of dispatch-chain hop failure side effects (AST-1191); every exit returns a dict.
_HOP_FAILURE_NOOP = {
    "apply_error_state": False,
    "error_state": "",
    "batch_released": False,
}


def _apply_dispatch_chain_hop_failure(
    *,
    entity_type: str,
    index: Optional[str],
    ctx: Optional[Dict[str, Any]],
    task_config: Dict[str, Any],
    error: str,
    debug: bool,
    provider_failed: bool = False,
    failure_class: Optional[str] = None,
) -> Dict[str, Any]:
    trigger_state, _ = _dispatch_chain_ctx(ctx)
    from src.core import tracker as tracker_mod
    # Hop-label-false: no error_state write; defense-in-depth claim release only (AST-1298).
    if not _should_write_dispatch_hop_label(
        entity_type=entity_type, index=index, ctx=ctx, trigger_state=trigger_state,
    ):
        batch_released = False
        if provider_failed and index and entity_type == "job":
            tracker_mod.release_job_dispatch_claim(index)
            batch_released = True
        return {
            "apply_error_state": False,
            "error_state": "",
            "batch_released": batch_released,
        }
    err_state = (task_config.get("error_state") or "").strip()
    # Only a missing job / missing candidate_data is unrecoverable. Provider failures (balance
    # or otherwise) hold the last happy state / hop label; the finally release below lets the
    # next dispatch sweep reclaim and retry the hop. No retry cap by design.
    hard = bool(err_state) and (
        "Job not found" in error
        or "Missing candidate_data" in error
    )
    apply_error_state = False
    batch_released = False
    # Transition first (history stamps in-flight batch_id); release in finally so
    # non-ValueError from transition cannot skip claim clear (AST-1298 / AST-1191).
    try:
        if hard and err_state and index:
            try:
                tracker_mod.transition_job_state([index], err_state)
                apply_error_state = True
            except ValueError as exc:
                logger.warning(
                    "%s skipped error_state %s — %s\n  The job claim is still being released",
                    index,
                    err_state,
                    exc,
                )
    finally:
            tracker_mod.release_job_dispatch_claim(index)
            batch_released = True
    return {
        "apply_error_state": apply_error_state,
        "error_state": err_state if apply_error_state else "",
        "batch_released": batch_released,
    }


def _build_context(task_key: str, task_config: Dict[str, Any], index: Optional[str]) -> str:
    """Build context string from task's context_format + index. Falls back to task_key."""
    if index is None:
        return task_key
    fmt = task_config.get("context_format")
    if not fmt or "{index}" not in fmt:
        return task_key
    try:
        return fmt.format(index=index)
    except KeyError:
        return fmt.replace("{index}", index)


# Leading run of AST-1639 cache-isolation markers, any id, no separators between them.
_CANDIDATE_PREFIX_RUN_RE = re.compile(r"^(?:\[astral-[^\]]*\])+")


def _system_text_with_candidate_prefix(system_content: str, candidate_id: Optional[str]) -> str:
    """Leading cache-isolation marker: first system bytes are ``[astral-<id>]`` then body.

    Idempotent: any leading ``[astral-…]`` run is replaced by exactly one ``[astral-<cid>]``.
    """
    cid = (candidate_id or "").strip()
    if not cid:
        raise ValueError(
            "candidate id required for agent system prompt "
            "(no omit / no sentinel — every agent call must carry an Astral candidate id)"
        )
    # Idempotent: drop any existing leading marker run (any id) so re-fed text gets exactly one.
    body = _CANDIDATE_PREFIX_RUN_RE.sub("", system_content, count=1)
    return f"[astral-{cid}]{body}"


def _assemble_blocks_seven_segment(
    *,
    system_content: str,
    user_content: str,
    caches_resolved_four: Tuple[Optional[str], Optional[str], Optional[str], Optional[str]],
    nocache_content: Optional[str],
    live_content: Optional[str],
    model_code: str,
    skip_cache: bool = False,
    candidate_id: Optional[str] = None,
) -> tuple:
    """Build Anthropic payloads: ≤5 cached ``system`` blocks (system + non-empty cache A–D raw text)
    plus user-role blocks for nocache + live + stamped user."""
    system_blocks: List[Dict[str, Any]] = []
    user_blocks: List[Dict[str, Any]] = []
    runtime_prompt: List[Dict[str, Any]] = []

    def _track(label: str, text: str, cached: bool) -> None:
        runtime_prompt.append({label: {
            "size": len(text), "cache": cached, "model": model_code, "content": text,
        }})

    # Per-candidate divergence at byte zero — before shared system / cache A–D text.
    system_for_wire = _system_text_with_candidate_prefix(system_content, candidate_id)
    system_block: Dict[str, Any] = {"type": "text", "text": system_for_wire}
    if not skip_cache:
        system_block["cache_control"] = {"type": "ephemeral"}
    system_blocks.append(system_block)
    _track("system_prompt", system_for_wire, not skip_cache)

    slot_labels = ("cache_a", "cache_b", "cache_c", "cache_d")
    for lbl, ct in zip(slot_labels, caches_resolved_four):
        seg = (ct or "").strip()
        if not seg:
            continue
        blk: Dict[str, Any] = {"type": "text", "text": seg}
        if not skip_cache:
            blk["cache_control"] = {"type": "ephemeral"}
        system_blocks.append(blk)
        _track(lbl, seg, not skip_cache)

    if nocache_content:
        nocache_text = f"--- ADDITIONAL CONTEXT ---\n{nocache_content}"
        user_blocks.append({"type": "text", "text": nocache_text})
        _track("nocache_context", nocache_text, False)

    if live_content:
        live_text = f"--- CONTENT ---\n{live_content}"
        user_blocks.append({"type": "text", "text": live_text})
        _track("live_content", live_text, False)

    full_user = getTimestampPrefix() + user_content
    user_blocks.append({"type": "text", "text": full_user})
    _track("user_prompt", full_user, False)

    no_cache_prompt_tokens = (len(nocache_content or "") + len(user_content or "")) // CHARS_PER_TOKEN
    no_cache_live_tokens = len(live_content or "") // CHARS_PER_TOKEN

    return system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens


def _assemble_blocks(
    system_content: str,
    user_content: str,
    cache_content: Optional[str],
    nocache_content: Optional[str],
    live_content: Optional[str],
    model_code: str,
    skip_cache: bool = False,
    candidate_id: Optional[str] = None,
) -> tuple:
    """Legacy entry: maps single ``cache_content`` blob to slot A — see AST-454/455."""
    return _assemble_blocks_seven_segment(
        system_content=system_content,
        user_content=user_content,
        caches_resolved_four=(cache_content, None, None, None),
        nocache_content=nocache_content,
        live_content=live_content,
        model_code=model_code,
        skip_cache=skip_cache,
        candidate_id=candidate_id,
    )


# ---------------------------------------------------------------------------
# agent_data storage
# ---------------------------------------------------------------------------

def _store_prompt_blocks(
    entity_type: str,
    task_key: str,
    batch_id: str,
    system_content: str,
    *,
    nocache_content: Optional[str] = None,
    user_content: str = "",
    live_content: Optional[str] = None,
    created_at: Optional[str] = None,
    caches_resolved_four: Any = _PB_SLOT_OMIT,
    cache_content: Any = _PB_SLOT_OMIT,
    debug: bool = False,
    entity_id: Optional[str] = None,  # AST-1431 prompt-row stamp tests (do_task / helper / Ad Hoc)
    entity_ids: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """Store prompt blocks in agent_data. Returns prompt_blocks refs for ledger.
    Production: ``caches_resolved_four``. Legacy tests/callers: ``cache_content`` (slot A only).
    entity_id is the entity index (AST-1429), distinct from inner _save's Style D loop index."""

    def _save(block_type: str, content: str) -> str:
        content_hash = hashlib.sha256(f"{batch_id}:{block_type}:{content}".encode()).hexdigest()[:16]
        agent_data_id = f"{batch_id}-{block_type.lower()}-{content_hash}"
        save_agent_data(
            agent_data_id=agent_data_id,
            entity_type=entity_type,
            task_key=task_key,
            batch_id=batch_id,
            block_type=block_type,
            block_data=content,
            token_size=len(content) // CHARS_PER_TOKEN,
            created_at=created_at,
            entity_id=entity_id if entity_id else None,
        )
        return agent_data_id

    # Collect membership first so Style D can emit index N/M per stored prompt block.
    segments: List[Tuple[str, str]] = [("SYSTEM", system_content)]
    if cache_content is not _PB_SLOT_OMIT:
        if caches_resolved_four is not _PB_SLOT_OMIT:
            raise TypeError("_store_prompt_blocks: pass caches_resolved_four or cache_content, not both")
        if cache_content:
            segments.append(("CACHE_A", cache_content))
        if nocache_content:
            segments.append(("NO_CACHE", nocache_content))
        if live_content:
            # AST-2029: stored copy only — wire blocks were already built from unhydrated live_content
            segments.append(("NO_CACHE", hydrate_entity_labels(live_content, entity_ids)))
        if user_content:
            segments.append(("TASK", user_content))
    else:
        if caches_resolved_four is _PB_SLOT_OMIT:
            raise TypeError("_store_prompt_blocks: missing caches_resolved_four or cache_content")
        type_names = ("CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D")
        for bt, blob in zip(type_names, caches_resolved_four):
            if blob and blob.strip():
                segments.append((bt, blob))
        if nocache_content:
            segments.append(("NO_CACHE", nocache_content))
        if live_content:
            # AST-2029: stored copy only — wire blocks were already built from unhydrated live_content
            segments.append(("NO_CACHE", hydrate_entity_labels(live_content, entity_ids)))
        if user_content:
            segments.append(("TASK", user_content))

    prompt_blocks: List[Dict[str, str]] = []
    logger.debug(
        "Calling _store_prompt_blocks: [entity_type=%s, task_key=%s, batch_id=%s, entity_id=%s, n=%s, n_ids=%s]",
        entity_type, task_key, batch_id, entity_id, len(segments), len(entity_ids or []),
    )
    for block_type, content in segments:
        prompt_blocks.append({"type": block_type, "id": _save(block_type, content)})
    logger.debug("Response from _store_prompt_blocks: %s", prompt_blocks)
    return prompt_blocks


def _audit_response_body(
    raw_text: Optional[str],
    parsed: Any = None,
    err: Optional[str] = None,
) -> str:
    """Best-effort body for a RESPONSE agent_data row when debugging failures (API, parse, decode)."""
    if raw_text:
        return raw_text
    if parsed is not None:
        if isinstance(parsed, (dict, list)):
            return json.dumps(parsed)
        return str(parsed)
    return err or "(no model response body captured)"


def _validation_failure_audit_body(err: str, raw_text: Optional[str], parsed: Any) -> str:
    """RESPONSE row body for schema/catalog failures — error message always visible (AST-594)."""
    body = _audit_response_body(raw_text, parsed, None)
    return f"Validation failed: {err}\n\n--- model response ---\n{body}"


def _provider_failure_audit_body(
    err: str,
    raw_text: Optional[str],
    parsed: Any = None,
    *,
    failure_class: Optional[str] = None,
) -> str:
    """RESPONSE row for provider failures — banner so success-shaped envelopes are not mistaken for finished hops (AST-1380)."""
    body = _audit_response_body(raw_text, parsed, None)
    head = f"Provider failed: {err}"
    if failure_class:
        head = f"Provider failed ({failure_class}): {err}"
    return f"{head}\n\n--- model response ---\n{body}"


def _failure_response_block_data(index: Optional[str], body: str) -> str:
    """Prefix so get_entity_response can match one row when a batch has many RESPONSE failures."""
    if index and body is not None:
        return f"[{index}]\n{body}"
    return body


def _agent_performance_status(perf: Any) -> Optional[str]:
    """Normalize agent_performance.status from dict or legacy string envelope."""
    if isinstance(perf, dict):
        status = perf.get("status")
        return str(status).strip().lower() if status is not None else None
    if isinstance(perf, str):
        return perf.strip().lower()
    return None


def _normalize_rubric_envelope_for_capture(parsed: Any) -> Any:
    """Coerce rubric envelope shape before snapshot — vector_reviews + status for capture (AST-860)."""
    if not isinstance(parsed, dict):
        return parsed
    perf = parsed.get("agent_performance")
    if perf is None:
        perf = {}
        parsed["agent_performance"] = perf
    elif not isinstance(perf, dict):
        return parsed
    top_reviews = parsed.get("vector_reviews")
    if top_reviews is not None and perf.get("vector_reviews") is None:
        perf["vector_reviews"] = top_reviews
    if normalize_vector_reviews_raw(perf.get("vector_reviews")):
        status = perf.get("status")
        status_norm = str(status).strip().lower() if status is not None else ""
        if status_norm != "failure" and not status_norm:
            perf["status"] = "success"
    return parsed


def _rubric_feedback_owner_and_candidate(
    task_key: str,
    cd: Dict[str, Any],
    ctx: Optional[Dict[str, Any]],
) -> Tuple[Optional[str], Optional[str]]:
    owner = rubric_owner_task_key(task_key)
    cid = (cd or {}).get("_astral_candidate_id")
    if not cid and ctx:
        cid = ctx.get("astral_candidate_id")
    return owner, (str(cid).strip() if cid else None) or None


def _capture_rubric_vector_feedback(
    *,
    task_key: str,
    owner_task_key: str,
    candidate_id: str,
    batch_id: str,
    entity_type: str,
    index: Optional[str],
    perf: Any,
    debug: bool,
    prompt_blocks: List[Dict[str, str]],
    batch_size: int,
    completed_at: Optional[str] = None,
) -> None:
    """Lenient vector_reviews capture on SUCCESS — parse failures never fail the run (AST-724 / AST-816 / AST-820)."""
    perf_status = _agent_performance_status(perf)
    if perf_status != "success":
        return
    if not (batch_id or "").strip():
        return
    from src.core.candidate import rubric_criteria_for_task

    code_to_uuid = list_rubric_vector_uuid_by_code(candidate_id, owner_task_key)
    criteria_codes = frozenset(
        str(c.get("code")).strip().upper()
        for c in rubric_criteria_for_task(candidate_id, owner_task_key)
        if isinstance(c, dict) and c.get("code")
    )
    uuid_codes = frozenset(code_to_uuid.keys())
    expected_codes = criteria_codes & uuid_codes
    if not expected_codes:
        return
    perf_dict = perf if isinstance(perf, dict) else {}
    raw_list = normalize_vector_reviews_raw(perf_dict.get("vector_reviews"))
    parsed_rows, *_ = parse_vector_reviews_diagnostic(
        raw_list if raw_list is not None else perf_dict.get("vector_reviews"),
        expected_codes,
        code_to_uuid,
    )

    if parsed_rows is None:
        try:
            fb_id = store_feedback_block(
                entity_type,
                task_key,
                batch_id,
                format_vector_reviews_raw(perf_dict),
                index=index,
            )
            prompt_blocks.append({"type": "FEEDBACK", "id": fb_id})
        except Exception as exc:
            _log_swallowed_agent_data(index, task_key, exc)
        return
    try:
        insert_vector_feedback_rows(
            parsed_rows,
            candidate_id=candidate_id,
            batch_id=batch_id,
            task_key=task_key,
            batch_size=batch_size,
            completed_at=completed_at,
        )
    except Exception as exc:
        logger.exception(
            "%s | %s\n  %s: %s\n  This hop is still success; vector feedback was not saved",
            index or "-",
            task_key,
            type(exc).__name__,
            exc,
        )
        return
    try:
        fb_id = store_feedback_block(
            entity_type,
            task_key,
            batch_id,
            format_vector_reviews_raw(perf_dict),
            index=index,
        )
        prompt_blocks.append({"type": "FEEDBACK", "id": fb_id})
    except Exception as exc:
        _log_swallowed_agent_data(index, task_key, exc)


def _store_response_block(
    entity_type: str,
    task_key: str,
    batch_id: str,
    response_text: str,
    created_at: Optional[str] = None,
    index: Optional[str] = None,
    *,
    debug: bool = False,
    entity_ids: Optional[List[str]] = None,
) -> str:
    """Store a RESPONSE block in agent_data. On success, response_text is the decoded/validated
    payload; on failure it is the raw API text (or error / parsed fallback). Returns the agent_data_id.
    index is folded into the row id so many do_task calls sharing one dispatch batch_id still get
    distinct rows when response_text matches (INSERT OR IGNORE dedupe)."""
    logger.debug(
        "Calling _store_response_block: [entity_type=%s, task_key=%s, batch_id=%s, index=%s]",
        entity_type, task_key, batch_id, index,
    )
    # AST-2029: hash + stored row both use the hydrated text
    response_text = hydrate_entity_labels(response_text, entity_ids)
    content_hash = hashlib.sha256(
        f"{batch_id}:RESPONSE:{index or ''}:{response_text}".encode()
    ).hexdigest()[:16]
    agent_data_id = f"{batch_id}-response-{content_hash}"
    # AST-984: tag RESPONSE with entity_id for list_entity_latest_agent_refs
    save_agent_data(
        agent_data_id=agent_data_id,
        entity_type=entity_type,
        task_key=task_key,
        batch_id=batch_id,
        block_type="RESPONSE",
        block_data=response_text,
        token_size=len(response_text) // CHARS_PER_TOKEN,
        created_at=created_at,
        entity_id=index if index else None,
    )
    logger.debug("Response from _store_response_block: %s", agent_data_id)
    return agent_data_id


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _coerce_schema_str_fields_from_list(
    parsed: Dict[str, Any], schema: Dict[str, Dict], *, debug: bool = False
) -> None:
    """Soft-coerce schema-str fields before type validation (list→join, int→str; nested items_schema)."""
    payload = _inner_task_payload(parsed)
    if not isinstance(payload, dict):
        return
    # Collect int→str events; emit Style D once after the walk (index/total stable).
    int_coerce_events: list[tuple[str, int, str]] = []

    def _walk(obj: Dict[str, Any], fields_schema: Dict[str, Dict], path_prefix: str) -> None:
        for field_name, field_spec in fields_schema.items():
            if not isinstance(field_spec, dict):
                continue
            type_spec = field_spec.get("type", "str")
            val = obj.get(field_name)
            field_path = f"{path_prefix}.{field_name}" if path_prefix else field_name
            if type_spec == "str" and isinstance(val, list):
                lines = [str(item).strip() for item in val if item is not None and str(item).strip()]
                obj[field_name] = "\n".join(lines)
            elif type_spec == "str" and type(val) is int:
                # type() is int — bool is a subclass of int; isinstance would soft-accept True/False.
                coerced = str(val)
                obj[field_name] = coerced
                int_coerce_events.append((field_path, val, coerced))
            elif type_spec == "list" and field_spec.get("items_schema") and isinstance(val, list):
                items_schema = field_spec["items_schema"]
                for idx, item in enumerate(val):
                    if isinstance(item, dict):
                        _walk(item, items_schema, f"{field_path}[{idx}]")

    _walk(payload, schema, "")
    logger.debug("Beginning int-coerce loop on %s items", len(int_coerce_events))
    logger.debug("End int-coerce loop after %s items", len(int_coerce_events))


def _validate_schema_object_fields(
    obj: Dict[str, Any], fields_schema: Dict[str, Dict], *, when_required: bool = False
) -> Optional[str]:
    """Validate a plain object against a field schema (not an agent envelope)."""
    for field_name, field_spec in fields_schema.items():
        if not isinstance(field_spec, dict):
            continue
        val = obj.get(field_name)
        required = field_spec.get("required", False)
        if required == "when_task_success":
            required = when_required
        if required and val is None:
            return f"Missing required field '{field_name}'"
        if val is None:
            continue
        type_spec = field_spec.get("type", "str")
        if type_spec == "bool" and not isinstance(val, bool):
            return f"Field '{field_name}' must be bool, got {type(val).__name__}"
        if type_spec == "str" and not isinstance(val, str):
            return f"Field '{field_name}' must be str, got {type(val).__name__}"
        if type_spec == "int":
            if isinstance(val, bool):
                return f"Field '{field_name}' must be int, got bool"
            if not isinstance(val, int):
                return f"Field '{field_name}' must be int, got {type(val).__name__}"
            min_val = field_spec.get("min")
            max_val = field_spec.get("max")
            if min_val is not None and val < min_val:
                return f"Field '{field_name}' must be >= {min_val}, got {val}"
            if max_val is not None and val > max_val:
                return f"Field '{field_name}' must be <= {max_val}, got {val}"
        if type_spec == "list" and not isinstance(val, list):
            return f"Field '{field_name}' must be list, got {type(val).__name__}"
        if type_spec in ("object", "dict") and not isinstance(val, dict):
            return f"Field '{field_name}' must be dict, got {type(val).__name__}"
        enum_vals = field_spec.get("enum")
        if enum_vals is not None and val not in enum_vals:
            return f"Field '{field_name}' must be one of {enum_vals}, got {val!r}"
        items_schema = field_spec.get("items_schema")
        if items_schema and type_spec == "list" and isinstance(val, list):
            for idx, item in enumerate(val):
                if not isinstance(item, dict):
                    return f"{field_name}[{idx}] must be object, got {type(item).__name__}"
                item_err = _validate_schema_object_fields(item, items_schema, when_required=when_required)
                if item_err:
                    return f"{field_name}[{idx}]: {item_err}"
    return None


def _validate_response_schema(
    parsed: Dict[str, Any], schema: Dict[str, Dict], task_key: str
    ) -> Optional[str]:
    """Validate the { agent_performance, agent_payload } envelope.
    Returns error string or None."""
    if not parsed or not isinstance(parsed, dict):
        return "Parsed response is empty or not a dict"

    perf = parsed.get("agent_performance")
    payload = parsed.get("agent_payload")

    if perf is None and payload is None:
        perf = parsed
        payload = parsed

    # AST-1072: CHAT ternary envelope — concern is not Agent failure; admin_aside required.
    if is_conversational_task(task_key):
        if isinstance(perf, dict):
            perf_err = _validate_schema_object_fields(perf, CONVERSATIONAL_PERFORMANCE_SCHEMA)
            if perf_err:
                return perf_err
            status = _agent_performance_status(perf)
            if status == "failure":
                note = perf.get("failure_note") or "Agent returned status=failure with no note"
                return f"Agent failure: {note}"
            if status == "concern":
                aside = perf.get("admin_aside")
                if not isinstance(aside, str) or not aside.strip():
                    return "Conversational concern requires non-empty admin_aside"
        elif perf == "failure":
            note = parsed.get("failure_note") or "Agent returned failure with no note"
            return f"Agent failure: {note}"
        elif isinstance(perf, str) and perf.strip().lower() == "concern":
            return "Conversational concern requires non-empty admin_aside"
        # else: success / other handled via schema enum when dict
    else:
        # Handle both string ("failure") and legacy dict ({"status": "failure"}) forms
        if perf == "failure":
            note = parsed.get("failure_note") or "Agent returned failure with no note"
            return f"Agent failure: {note}"
        if isinstance(perf, dict) and perf.get("status") == "failure":
            note = perf.get("failure_note") or "Agent returned status=failure with no note"
            return f"Agent failure: {note}"

    if payload is None:
        return "Response missing 'agent_payload'"

    # String payloads (e.g. qualify_job_output abbreviated text) — no field validation needed
    if not isinstance(payload, dict):
        return None

    task_success = payload.get("task_success") if isinstance(payload.get("task_success"), bool) else None
    when_required = task_success is True

    # Payload fields (incl. list items_schema) — not recursive envelope on nested objects.
    err = _validate_schema_object_fields(payload, schema, when_required=when_required)
    return err


def conversational_turn_from_do_task_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Shape for AST-1073 callers: outcome, reply, admin_aside, success."""
    if not isinstance(result, dict):
        return {"success": False, "outcome": None, "reply": None, "admin_aside": None}
    perf = result.get("agent_performance")
    perf_dict = perf if isinstance(perf, dict) else {}
    parsed = result.get("parsed_response")
    reply = None
    if isinstance(parsed, dict):
        reply = parsed.get("reply")
    elif isinstance(parsed, str):
        reply = parsed
    outcome = result.get("conversational_outcome") or _agent_performance_status(perf_dict or perf)
    aside = perf_dict.get("admin_aside") if perf_dict else None
    return {
        "success": bool(result.get("success")),
        "outcome": outcome,
        "reply": reply,
        "admin_aside": aside if isinstance(aside, str) else None,
    }


def _validate_grades(grades: list, vectors: list) -> Optional[str]:
    """Validate grade array against expected vectors config. Returns error string or None."""
    expected = {v["name"] for v in vectors}
    actual = {g.get("vector") for g in grades}
    missing = expected - actual
    if missing:
        return f"Missing vectors: {sorted(missing)}"
    extra = actual - expected
    if extra:
        return f"Unexpected vectors: {sorted(extra)}"
    allowed = set(ASTRAL_CONFIG.get("valid_grades", ["A", "B", "C", "D", "F", "X"]))
    for g in grades:
        if g.get("grade", "") not in allowed:
            return (
                f"Invalid grade '{g.get('grade')}' for vector '{g.get('vector')}' "
                f"(must be one of {sorted(allowed)})"
            )
    return _validate_grade_confidence_list(grades, "grades")



# ---------------------------------------------------------------------------
# do_task — primary orchestration entry point
# ---------------------------------------------------------------------------

async def run_cover_letter_artifact_chain_for_job(
    astral_job_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    *,
    debug: bool = False,
    store_agent_data: bool = True,
) -> Dict[str, Any]:
    """AST-301 / AST-368: start the cover-letter do_task chain for one job; further hops use run_next.

    First hop key: ``BUILD_CONFIG['cover_letter_artifact_chain']['first_task_key']``. Same ctx/job
    resolution as ``do_chain_for_job`` so chain tokens (AST-304) and
    ``{$WRITING_PREFERENCES}`` / ``{$COVER_LETTER_SIGNATURE}`` resolve on each hop via shared
    ``do_task`` chain_context merge (AST-370).
    """
    # consult imports do_task at module load; import here only to avoid import cycle.
    from src.core import consult as _consult
    from src.core import tracker

    chain_cfg = BUILD_CONFIG.get("cover_letter_artifact_chain") or {}
    first_key = (chain_cfg.get("first_task_key") or "").strip()
    if not first_key or first_key not in TASK_CONFIG:
        raise ValueError(
            "BUILD_CONFIG['cover_letter_artifact_chain']['first_task_key'] must name a TASK_CONFIG key; "
            f"got {first_key!r}"
        )

    base = dict(ctx) if ctx else {}
    job: Optional[Dict[str, Any]] = None
    for k in ("job", "job_data"):
        row = base.get(k)
        if isinstance(row, dict) and row.get("astral_job_id") == astral_job_id:
            job = dict(row)
            break
    if job is None:
        fetched = tracker.get_job(astral_job_id)
        if not fetched:
            return {
                "success": False,
                "error": f"Job not found: {astral_job_id}",
                "api_response": None,
                "parsed_response": None,
                "timesheet": {},
            }
        job = dict(fetched)

    company = None
    cid = job.get("company")
    if cid:
        company = tracker.get_company(cid)

    live_content = await _consult._prep_live_content(job, company, scoring_task_key=first_key)
    if not live_content:
        return {
            "success": False,
            "error": "live_content prep failed (missing JD or company website unavailable)",
            "api_response": None,
            "parsed_response": None,
            "timesheet": {},
        }

    task_ctx: Dict[str, Any] = {
        **base,
        "batch_entities": [job],
        "batch_size": 1,
    }
    if "vector_labels" not in task_ctx:
        task_ctx["vector_labels"] = {}

    return await do_task(
        first_key,
        live_content=live_content,
        index=astral_job_id,
        ctx=task_ctx,
        debug=debug,
        store_agent_data=store_agent_data,
    )


def _agent_llm_route(agent_row: Dict[str, Any]) -> Dict[str, Any]:
    """Agent model_id + plain settings → resolve_agent_settings route (server, SKU, tier) (AST-1956).
    Raises ValueError on a missing or unknown model_id; settings are passed through unchecked."""
    aid = agent_row.get("agent_id")
    model_id = (agent_row.get("model_id") or "").strip()
    if not model_id:
        raise ValueError(f"Agent '{aid}' has no model_id configured.")
    return resolve_agent_settings(model_id, agent_row)


def task_llm_server_id(task_key: str) -> str:
    """Catalog server behind task_key's agent model — dispatcher key gate (AST-1879)."""
    agent_row, _ = _resolve_task_prompts(task_key)
    return _agent_llm_route(agent_row)["server_id"]


def task_llm_server_id_or_none(task_key: str) -> Optional[str]:
    """task_llm_server_id, or None when the task has no LLM agent (AST-1944).

    No agent_task row, empty agent_id, or the "telescope" sentinel → no model, no server to gate on.
    Any other resolution failure (unknown real agent, missing model_id) still raises — a
    misconfigured LLM task must stay loud.
    """
    try:
        # Strict path first: the stage_email_meteorite mailbox fold resolves a real agent here.
        return task_llm_server_id(task_key)
    except ValueError:
        row = get_agent_task(resolve_task_key_for_content(task_key))
        if ((row or {}).get("agent_id") or "").strip() in ("", "telescope"):
            return None
        raise


def _candidate_server_key(
    ctx: Optional[Dict[str, Any]], candidate_id: Optional[str], server_id: str
) -> Optional[str]:
    """The candidate's key for server_id only — never env, never another platform's key (AST-1879).

    ctx["candidate_api_keys"] wins (session paste carries a map but no candidate id);
    otherwise load the map by candidate id (callers that pass only astral_candidate_id).
    """
    keys = (ctx or {}).get("candidate_api_keys")
    if keys is None and candidate_id:
        keys = (database.get_candidate(candidate_id) or {}).get("candidate_api_keys")
    return (keys or {}).get(server_id) or None


def _missing_server_key_result(candidate_id: Optional[str], server_id: str) -> Dict[str, Any]:
    """Failure envelope when the candidate holds no key for the route's server — no request was sent."""
    return {
        "success": False,
        "error": f"Candidate {candidate_id or '-'} has no API key for server {server_id!r}",
        "api_response": None,
        "parsed_response": None,
        "timesheet": {},
    }


async def _send_to_server(
    user_blocks: List[Dict[str, Any]],
    *,
    server_id: str,
    sku: str,
    tier: Dict[str, Any],
    api_key: str,
    system_blocks: List[Dict[str, Any]],
    response_format: Optional[str],
    prompt_label: str,
    candidate_id: Optional[str],
    temperature: Optional[float],
    max_tokens: Optional[int],
    debug: bool,
    task_key_uuid: Optional[str],
    no_cache_prompt_tokens: int,
    no_cache_live_tokens: int,
    batch_size: int = 1,
) -> Dict[str, Any]:
    """One outbound call on the server's protocol client: Anthropic SDK or the shared compat client."""
    common = dict(
        system_blocks=system_blocks,
        response_format=response_format,
        prompt_label=prompt_label,
        candidate_id=candidate_id,
        temperature=temperature,
        max_tokens=max_tokens,
        task_key_uuid=task_key_uuid,
        no_cache_prompt_tokens=no_cache_prompt_tokens,
        no_cache_live_tokens=no_cache_live_tokens,
        batch_size=batch_size,
        record_timesheet=record_timesheet_entry,
    )
    if get_llm_server(server_id)["protocol"] == "anthropic":
        # api_key is always non-empty here, so send_to_anthropic never takes its env-key client.
        return await send_to_anthropic(
            user_blocks, model_code=sku, api_key_override=api_key, debug=debug,
            reasoning_effort=tier.get("reasoning_effort"), **common,
        )
    return await send_to_llm_compat(user_blocks, server_id=server_id, sku=sku, tier=tier, api_key=api_key, **common)


@_with_log_debug
async def do_task(
    task_key: str,
    live_content: Optional[str] = None,
    index: Optional[str] = None,
    candidate_data: Optional[Dict[str, Any]] = None,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    store_agent_data: bool = True,
    chain_context: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Run a task by key. Fetches prompts from DB, resolves tokens, calls Anthropic API.
    Stores prompt + response blocks in agent_data when store_agent_data=True.

    Dispatch run_next chain ctx keys (set by consult before entry hop):
      dispatch_trigger_state — dispatch row trigger_state (e.g. BUILD_ARTIFACTS)
      dispatch_chain_graduate_on_terminal — True when full chain should graduate on terminal hop

    Args:
        task_key: Task name (e.g. "prefilter", "evaluate_jd")
        live_content: Dynamic content for the prompt (the TASK block)
        index: Entity identifier for context and audit (e.g. astral_job_id). Falls back to task_key.
            Land enrich (AST-1470) may pass ``qualify_meteorite_batch_{batch_id}`` with
            ``log_batch_id`` set — audit-only entity_id, not a job row UUID.
        candidate_data: Token-resolution dict (optional; ctx supersedes).
        ctx: Full candidate raft dict. Extracts candidate_data + candidate_api_keys (server → key map).
        debug: Emit verbose log lines.
        store_agent_data: When True, persist prompt/response blocks to agent_data table.
        chain_context: Optional extra chain-source token values (AST-303 parent hop → child).

    Returns:
        Dict with success, api_response, parsed_response, timesheet, error (if failed).
    """
    task_config = TASK_CONFIG.get(task_key)
    if not task_config:
        raise ValueError(f"Unknown task_key: {task_key}. Valid: {list(TASK_CONFIG.keys())}")

    schema = task_config.get("response_schema")
    if schema is None:
        raise ValueError(
            f"Task '{task_key}' is missing required response_schema. "
            "Add response_schema to TASK_CONFIG for this task."
        )

    cd = _token_view_for_do_task(ctx, candidate_data, index=index)

    # Dict truthiness is always true for the 8-key view; check identity material (AST-1192 resolve).
    if task_config.get("requires_candidate_key") and not _candidate_identity_material_present(cd):
        logger.warning(
            "%s — no candidate_data\n  The call is still going out without candidate identity",
            task_key,
        )

    candidate_id = ctx.get("astral_candidate_id") if ctx else None
    if candidate_id:
        # Lazy import breaks agent↔candidate cycle (candidate imports agent paths).
        from src.core.candidate import company_search_terms_joined_text
        joined = company_search_terms_joined_text(candidate_id)
        cd = dict(cd)
        cd["_astral_candidate_id"] = candidate_id
        arts = dict(cd.get("artifacts") or {})
        arts["company_search_terms"] = joined
        cd["artifacts"] = arts

    agent_row, agent_task_row = _resolve_task_prompts(task_key)
    # AST-1698: harvest artifact pins from unresolved prompt templates (before resolve).
    _system_unresolved = (
        (agent_task_row.get("system_prompt") or "").strip()
        or (agent_row.get("content") or "")
    )
    source_artifact_ids = harvest_source_artifact_ids(
        _system_unresolved,
        agent_task_row.get("user_prompt") or "",
        agent_task_row.get("cache_prompt") or "",
        agent_task_row.get("cache_prompt_b") or "",
        agent_task_row.get("cache_prompt_c") or "",
        agent_task_row.get("cache_prompt_d") or "",
        agent_task_row.get("nocache_prompt") or "",
        live_content or "",
        candidate_id=candidate_id,
    )

    def _with_harvest(payload: Dict[str, Any]) -> Dict[str, Any]:
        payload["source_artifact_ids"] = list(source_artifact_ids)
        return payload

    effective_chain_context = chain_context
    entity_type_pre = _effective_entity_type(task_config, index)
    parent_for_hydration = (chain_context or {}).get("_hop_parent_task_key")
    if not parent_for_hydration and index and entity_type_pre:
        if _task_references_caller_tokens(agent_task_row, live_content):
            parent_for_hydration = _parent_hop_task_key_for_child(task_key)
    if parent_for_hydration and index and entity_type_pre:
        if _task_references_caller_tokens(agent_task_row, live_content):
            # AST-1264: fail-open to live CALLER — skip hydrate when persist recurse has CALLER_*
            # (re-inject on parent). Dead hydr_err fallback removed (Radia).
            _live_caller = bool((ctx or {}).get("persist_candidate_craft_hops")) and any(
                ((chain_context or {}).get(k) or "").strip() for k in CALLER_HOP_TOKEN_NAMES
            )
            if _live_caller:
                effective_chain_context = chain_context
            else:
                hydrated, hydr_err = _hydrate_caller_chain_context(
                    entity_type_pre,
                    index,
                    task_key,
                    parent_for_hydration,
                    chain_context,
                    debug=debug,
                )
                if hydr_err:
                    return _with_harvest({
                        "success": False,
                        "error": hydr_err,
                        "api_response": None,
                        "parsed_response": None,
                        "timesheet": {},
                    })
                effective_chain_context = _merge_hydrated_caller_context(
                    chain_context, hydrated
                )
    in_chain = _in_run_next_chain(chain_context=chain_context, agent_task_row=agent_task_row)
    hop_ledger_batch_id: Optional[str] = None
    hop_ledger_closed = False

    chain_entry = _is_chain_entry(effective_chain_context)
    parent_task_key = (effective_chain_context or {}).get("_hop_parent_task_key")
    parent_caller_summary = {
        k: (effective_chain_context or {}).get(k, "")
        for k in CALLER_HOP_TOKEN_NAMES
        if k in (effective_chain_context or {})
    }
    _jc = _job_context_for_call(ctx, index, cd, debug=debug)
    # AST-2000: per-segment empty-token collectors (snapshot-replaced segments are dropped below).
    _empties: Dict[str, list] = {
        seg: [] for seg in ("selected_agent", "system", "user", "cache_a", "cache_b", "cache_c", "cache_d", "nocache")
    }
    # Agent content only reaches the model via {$SELECTED_AGENT} (system fallback collects itself).
    _selects_agent = any(
        "{$SELECTED_AGENT}" in s for s in _task_prompt_texts(agent_task_row, None).values()
    )
    _cc = _chain_context(
        agent_row,
        cd,
        task_key,
        _jc,
        effective_chain_context,
        chain_entry=chain_entry,
        parent_task_key=parent_task_key or None,
        parent_caller_summary=parent_caller_summary or None,
        warn_on_empty=False,
        empty_tokens=_empties["selected_agent"] if _selects_agent else None,
    )

    # AST-1879 / AST-1956: the agent row's model + plain settings pick the server, SKU, and tier.
    # Contact Estelle is her own agent row (AST-1878), so there is no conversational override.
    route = _agent_llm_route(agent_row)
    server_id = route["server_id"]
    sku = route["sku"]
    tier = route["tier"]
    api_key = _candidate_server_key(ctx, candidate_id, server_id)
    if not api_key:
        logger.warning(
            "%s | %s skipped — no %s API key on the candidate\n  This call is not going out",
            candidate_id or "-",
            task_key,
            server_id,
        )
        return _with_harvest(_missing_server_key_result(candidate_id, server_id))
    # AST-1956: temperature is the agent row's own setting, sent as stored (None → not sent).
    agent_temperature = tier["temperature"]
    agent_max_tokens = tier["max_tokens"]

    _hop_kw = dict(
        chain_entry=chain_entry,
        parent_task_key=parent_task_key or None,
        parent_caller_summary=parent_caller_summary or None,
    )
    _rt_kw = {**_hop_kw}

    system_content = resolved_task_system(
        agent_row, agent_task_row, cd, task_key, _cc, _jc, **_rt_kw, empty_tokens=_empties["system"]
    )
    user_content = resolve_tokens(
        agent_task_row.get("user_prompt") or "", cd, task_key, _cc, _jc, **_hop_kw, empty_tokens=_empties["user"]
    )
    rca = resolve_tokens(
        agent_task_row.get("cache_prompt") or "", cd, task_key, _cc, _jc, **_hop_kw, empty_tokens=_empties["cache_a"]
    )
    rcb = resolve_tokens(
        agent_task_row.get("cache_prompt_b") or "", cd, task_key, _cc, _jc, **_hop_kw, empty_tokens=_empties["cache_b"]
    )
    rcc = resolve_tokens(
        agent_task_row.get("cache_prompt_c") or "", cd, task_key, _cc, _jc, **_hop_kw, empty_tokens=_empties["cache_c"]
    )
    rcd = resolve_tokens(
        agent_task_row.get("cache_prompt_d") or "", cd, task_key, _cc, _jc, **_hop_kw, empty_tokens=_empties["cache_d"]
    )

    def _slot(res: str) -> Optional[str]:
        v = (res or "").strip()
        return v if v else None

    caches_four = (_slot(rca), _slot(rcb), _slot(rcc), _slot(rcd))
    nocache_content = resolve_tokens(
        agent_task_row.get("nocache_prompt") or "", cd, task_key, _cc, _jc, **_hop_kw, empty_tokens=_empties["nocache"]
    ) or None

    if is_vector_feedback_task(task_key):
        _fb_suffix = (RUBRIC_FEEDBACK_CONFIG.get("prompt_suffix") or "").strip()
        if _fb_suffix:
            if (user_content or "").strip():
                user_content = (user_content.rstrip() + "\n\n" + _fb_suffix).strip()
            elif (nocache_content or "").strip():
                nocache_content = (nocache_content.rstrip() + "\n\n" + _fb_suffix).strip()

    snap = (ctx or {}).get("intake_prompt_snapshot")
    if isinstance(snap, dict) and snap and task_key.startswith("intake_"):
        if "system" in snap:
            system_content = snap.get("system") or ""
            _empties["system"] = []
        rca = snap.get("cache_a") or ""
        rcb = snap.get("cache_b") or ""
        rcc = snap.get("cache_c") or ""
        rcd = snap.get("cache_d") or ""
        caches_four = (_slot(rca), _slot(rcb), _slot(rcc), _slot(rcd))
        for _seg in ("cache_a", "cache_b", "cache_c", "cache_d"):
            _empties[_seg] = []
        if "nocache" in snap:
            nocache_content = snap.get("nocache") or None
            _empties["nocache"] = []

    # dict.fromkeys = ordered-unique across segments (segment order above).
    empty_names = list(dict.fromkeys(n for names in _empties.values() for n in names))
    if empty_names:
        # AST-2000: an incomplete prompt is never sent — one ERROR, no per-token WARNINGs.
        logger.error(
            "%s | %s skipped — empty tokens %s\n  This call is not going out",
            index or candidate_id or "-",
            task_key,
            ", ".join(empty_names),
        )
        return _with_harvest({
            "success": False,
            "error": f"Empty tokens: {', '.join(empty_names)} (task={task_key})",
            "empty_tokens": empty_names,
            "empty_token_task": task_key,
            "api_response": None,
            "parsed_response": None,
            "timesheet": {},
        })

    context = _build_context(task_key, task_config, index)
    response_format = task_config.get("response_format", "text")
    skip_cache = bool(ctx.get("skip_cache")) if ctx else False
    batch_size = ctx.get("batch_size", 1) if ctx else 1
    entity_type = _effective_entity_type(task_config, index)
    if in_chain:
        if candidate_id:
            hop_ledger_batch_id = _open_run_next_hop_ledger(
                task_key, candidate_id, entity_type, batch_size=batch_size
            )
        else:
            logger.warning(
                "%s skipped — no candidate_id for hop ledger\n  This hop is still running without a hop ledger",
                task_key,
            )
    batch_id = hop_ledger_batch_id or log_batch_id.get()

    def _close_hop_ledger(
        *,
        success: bool,
        clear_log: bool = False,
        failure_error: Optional[str] = None,
        provider_failed: bool = False,
        failure_class: Optional[str] = None,
    ) -> Dict[str, Any]:
        nonlocal hop_ledger_closed
        if not success and failure_error:
            outcome = _apply_dispatch_chain_hop_failure(
                entity_type=entity_type or "",
                index=index,
                ctx=ctx,
                task_config=task_config,
                error=failure_error,
                debug=debug,
                provider_failed=provider_failed,
                failure_class=failure_class,
            )
        else:
            outcome = dict(_HOP_FAILURE_NOOP)
        # Must return outcome — hop_ledger_batch_id is None for non-chain / no candidate.
        if hop_ledger_closed or not hop_ledger_batch_id:
            return outcome
        _finalize_run_next_hop_ledger(
            hop_ledger_batch_id, success=success, batch_size=batch_size
        )
        hop_ledger_closed = True
        if clear_log:
            log_batch_id.set(None)
            log_candidate_id.set(None)
        return outcome

    system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens = _assemble_blocks_seven_segment(
        system_content=system_content,
        user_content=user_content,
        caches_resolved_four=caches_four,
        nocache_content=nocache_content,
        live_content=live_content,
        model_code=sku,
        skip_cache=skip_cache,
        candidate_id=candidate_id,
    )

    prompt_blocks: List[Dict[str, str]] = []
    _should_store = store_agent_data and batch_id and entity_type
    # AST-2029: real ids for stored labels — every batch entity must carry one, else store positional text
    _ents = (ctx or {}).get("batch_entities") or []
    _id_key = "company_id" if entity_type == "company" else "astral_job_id"
    _store_ids = [str(e.get(_id_key) or "") if isinstance(e, dict) else "" for e in _ents]
    _store_ids = _store_ids if _store_ids and all(_store_ids) else None
    if _should_store:
        try:
            # Off the loop: a locked DB must not stall other companies' provider timers (AST-1842)
            prompt_blocks = await asyncio.to_thread(
                _store_prompt_blocks,
                entity_type=entity_type,
                task_key=task_key,
                batch_id=batch_id,
                # Same prefix as wire first system block (helper once on unresolved body).
                system_content=_system_text_with_candidate_prefix(system_content, candidate_id),
                caches_resolved_four=(rca or "", rcb or "", rcc or "", rcd or ""),
                nocache_content=nocache_content,
                user_content=user_content,
                live_content=live_content,
                debug=debug,
                entity_id=index if index else None,
                entity_ids=_store_ids,
            )
        except Exception as exc:
            _log_swallowed_agent_data(index, task_key, exc)

    logger.debug(
        "Calling _send_to_server: [task_key=%s, server=%s, model=%s, max_tokens=%s, temp=%s, effort=%s, skip_cache=%s, candidate=%s]",
        task_key, server_id, sku, agent_max_tokens, agent_temperature, tier.get("reasoning_effort"), skip_cache, candidate_id or "",
    )
    result = await _send_to_server(
        user_blocks,
        server_id=server_id,
        sku=sku,
        tier=tier,
        api_key=api_key,
        system_blocks=system_blocks,
        response_format=response_format,
        prompt_label=task_key,
        candidate_id=candidate_id,
        temperature=agent_temperature,
        max_tokens=agent_max_tokens,
        debug=debug,
        task_key_uuid=agent_task_row.get("task_key_uuid"),
        no_cache_prompt_tokens=no_cache_prompt_tokens,
        no_cache_live_tokens=no_cache_live_tokens,
        batch_size=batch_size,
    )
    logger.debug("Response from _send_to_server: %s", result)
    # Call outcome onto the active batch's ledger row — dispatcher batch, or the hop row
    # _open_run_next_hop_ledger set log_batch_id to.
    ledger_batch_id = log_batch_id.get()
    if ledger_batch_id:
        # AST-2008: every call writes duration + failure class (NULL on success). Several calls can share
        # one row; the last call wins, so the pair always describes the same call (Decision A).
        cols: Dict[str, Any] = {
            "llm_call_seconds": (result.get("timesheet") or {}).get("duration"),
            "llm_failure_class": None if result.get("success")
            else (str(result.get("failure_class") or "").strip() or "provider_failed"),
        }
        # AST-1960: host on successful calls only — a call that never reached a host carries the server
        # label, which must not overwrite the real host a sibling call wrote.
        if result.get("success"):
            # Anthropic-direct results carry no host; that server is its own host, so its label stands in.
            cols["host"] = result.get("host") or get_llm_server(server_id)["label"]
        logger.debug("Calling database.update_dispatch_ledger: [batch_id=%s, cols=%s]", ledger_batch_id, cols)
        try:
            # Off the loop like the agent_data writes: a locked DB must not stall provider timers (AST-1842).
            await asyncio.to_thread(database.update_dispatch_ledger, ledger_batch_id, **cols)
        except Exception:
            # A ledger hiccup must never change the call's own outcome.
            logger.exception(
                "%s | %s\n  Ledger call outcome write failed for batch %s\n  Continuing without it on that ledger row",
                index or "-",
                task_key,
                ledger_batch_id,
            )
    result["runtime_prompt"] = runtime_prompt
    result["source_artifact_ids"] = list(source_artifact_ids)

    if not result.get("success"):
        err = normalize_provider_error(
            result.get("error"), fallback=result.get("failure_class")
        )
        if not (isinstance(result.get("error"), str) and result.get("error").strip()):
            result["error"] = err
        if not batch_id:
            _warn_hop_no_success(task_key, f"provider failed: {err}")
        raw_for_audit = None
        api_resp = result.get("api_response")
        if api_resp:
            try:
                raw_for_audit = extract_api_response_text(api_resp)
            except ValueError:
                pass
        # Banner so raw agent_performance.status=success envelopes are not mistaken for finished hops (AST-1380).
        _fc = result.get("failure_class")
        _fc_s = str(_fc).strip() if _fc is not None else ""
        audit_body = _provider_failure_audit_body(
            str(result.get("error") or "Generation failed"),
            raw_for_audit,
            parsed=result.get("parsed_response"),
            failure_class=_fc_s or None,
        )
        if _should_store:
            try:
                await asyncio.to_thread(_store_response_block,
                    entity_type, task_key, batch_id, _failure_response_block_data(index, audit_body), index=index,
                    debug=debug, entity_ids=_store_ids)
            except Exception as exc:
                _log_swallowed_agent_data(index, task_key, exc)
        hop_fail_outcome = _close_hop_ledger(
            success=False,
            clear_log=True,
            failure_error=str(result.get("error") or "provider_failed"),
            provider_failed=True,
            failure_class=(
                str(result.get("failure_class")).strip()
                if result.get("failure_class") is not None
                else None
            ) or None,
        )
        hop_fail_outcome = hop_fail_outcome or _HOP_FAILURE_NOOP
        return result

    # Capture raw_text now; RESPONSE block storage is deferred until after validation/decode.
    # On success we store decoded content; on any failure we store raw_text.
    raw_text = None
    if _should_store:
        api_resp = result.get("api_response")
        if api_resp:
            try:
                raw_text = extract_api_response_text(api_resp)
            except ValueError:
                pass
    parsed = result.get("parsed_response")
    output_type = task_config.get("output_type", "")
    rubric_encoded = "_encoded" in output_type and bool(task_config.get("rubric_artifact"))
    strict_batch = _is_strict_encoded_batch_consult(task_key)
    if strict_batch and isinstance(parsed, dict) and parsed.get("agent_payload") is not None and parsed.get("agent_performance") is None:
        parsed = {**parsed, "agent_performance": {}}
        result["parsed_response"] = parsed
    envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed) if strict_batch else None
    if not envelope_err and "_encoded" in output_type:
        parsed = coerce_grades_encoded_json_parse(parsed, raw_text or "")
        result["parsed_response"] = parsed
    if strict_batch and not envelope_err:
        envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed)

    if is_vector_feedback_task(task_key) and isinstance(parsed, dict):
        parsed = _normalize_rubric_envelope_for_capture(parsed)
        result["parsed_response"] = parsed

    envelope_snapshot = None
    if is_vector_feedback_task(task_key) and isinstance(parsed, dict) and "agent_performance" in parsed:
        envelope_snapshot = copy.deepcopy(parsed)

    if envelope_err:
        _warn_hop_no_success(task_key, envelope_err)
        if _should_store:
            try:
                await asyncio.to_thread(_store_response_block,
                    entity_type,
                    task_key,
                    batch_id,
                    _failure_response_block_data(index, _audit_response_body(raw_text, parsed, envelope_err)),
                    index=index,
                    debug=debug, entity_ids=_store_ids)
            except Exception as exc:
                _log_swallowed_agent_data(index, task_key, exc)
        _close_hop_ledger(success=False, clear_log=True, failure_error=str(envelope_err))
        return _with_harvest({"success": False, "api_response": result.get("api_response"),
                "parsed_response": None, "error": envelope_err, "raw_response": parsed,
                "timesheet": result.get("timesheet", {})})

    if parsed is not None and response_format in ("json", "python") and not rubric_encoded:
        if isinstance(parsed, dict) and schema:
            if task_key in _CRAFT_RESUME_NORMALIZE_TASK_KEYS:
                from src.core.candidate import normalize_craft_resume_base_agent_payload

                normalize_craft_resume_base_agent_payload(parsed)
            if task_key == "draft_job_resume":
                from src.core.candidate import normalize_draft_job_resume_agent_payload

                normalize_draft_job_resume_agent_payload(parsed, debug=debug)
            _coerce_schema_str_fields_from_list(parsed, schema, debug=debug)
        err = _validate_response_schema(parsed, schema, task_key)
        if err:
            _warn_hop_no_success(task_key, err)
            if log_batch_id.get():
                flush_log_buffer()
            if _should_store:
                try:
                    await asyncio.to_thread(_store_response_block,
                        entity_type,
                        task_key,
                        batch_id,
                        _failure_response_block_data(index, _validation_failure_audit_body(err, raw_text, parsed)),
                        index=index,
                    debug=debug, entity_ids=_store_ids)
                except Exception:
                    _log_swallowed_agent_data(index, task_key)
            _close_hop_ledger(success=False, clear_log=True, failure_error=str(err))
            return _with_harvest({"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                    "error": err, "raw_response": parsed, "timesheet": result.get("timesheet", {})})

        if task_config.get("resume_section_payload") and cd:
            from src.core.candidate import validate_draft_job_resume_payload

            cat_err = validate_draft_job_resume_payload(parsed, cd, debug=debug)
            if cat_err:
                _warn_hop_no_success(task_key, cat_err)
                if log_batch_id.get():
                    flush_log_buffer()
                if _should_store:
                    try:
                        await asyncio.to_thread(_store_response_block,
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(
                                index, _validation_failure_audit_body(cat_err, raw_text, parsed)
                            ),
                            index=index,
                        debug=debug, entity_ids=_store_ids)
                    except Exception:
                        _log_swallowed_agent_data(index, task_key)
                _close_hop_ledger(success=False, clear_log=True, failure_error=str(cat_err))
                return _with_harvest({"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                        "error": cat_err, "raw_response": parsed, "timesheet": result.get("timesheet", {})})

        inner_payload = _inner_task_payload(parsed)
        if isinstance(inner_payload, dict):
            conf_err = _validate_grade_confidence_in_payload(inner_payload, task_key)
            if conf_err:
                _warn_hop_no_success(task_key, conf_err)
                if _should_store:
                    try:
                        await asyncio.to_thread(_store_response_block,
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(index, _audit_response_body(raw_text, parsed, conf_err)),
                            index=index,
                        debug=debug, entity_ids=_store_ids)
                    except Exception:
                        _log_swallowed_agent_data(index, task_key)
                _close_hop_ledger(success=False, clear_log=True, failure_error=str(conf_err))
                return _with_harvest({"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                        "error": conf_err, "raw_response": parsed, "timesheet": result.get("timesheet", {})})

        vectors = task_config.get("vectors")
        # AST-594: draft_job_resume is structure-keyed, not graded-consult.
        if vectors and task_key != "draft_job_resume" and isinstance(inner_payload, dict):
            grades = inner_payload.get("grades")
            if grades and isinstance(grades, list):
                grade_err = _validate_grades(grades, vectors)
                if grade_err:
                    _warn_hop_no_success(task_key, grade_err)
                    if _should_store:
                        try:
                            await asyncio.to_thread(_store_response_block,
                                entity_type,
                                task_key,
                                batch_id,
                                _failure_response_block_data(index, _audit_response_body(raw_text, parsed, grade_err)),
                                index=index,
                            debug=debug, entity_ids=_store_ids)
                        except Exception:
                            _log_swallowed_agent_data(index, task_key)
                    _close_hop_ledger(success=False, clear_log=True, failure_error=str(grade_err))
                    return _with_harvest({"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                            "error": grade_err, "raw_response": parsed, "timesheet": result.get("timesheet", {})})

    if isinstance(parsed, dict) and "agent_payload" in parsed:
        # AST-1839: rubric-encoded tasks skip _validate_response_schema, so the envelope status is
        # lost on unwrap — surface a model-reported failure (bad source content) as agent_failure.
        _perf = parsed.get("agent_performance")
        if rubric_encoded and _agent_performance_status(_perf) == "failure":
            _note = (_perf.get("failure_note") if isinstance(_perf, dict) else None) or parsed.get("failure_note")
            agent_err = f"Agent failure: {_note or 'Agent returned status=failure with no note'}"
            _warn_hop_no_success(task_key, agent_err)
            # Keep cleanly decoded lines so a batch caller fails only the gaps, not the batch (AST-2089).
            # Same validation bar as the success path; any error → None → caller fails the whole batch.
            salvaged = None
            if (ctx or {}).get("batch_entities"):
                try:
                    from src.core.consult import _normalize_rubric_task_response

                    _cand = _normalize_rubric_task_response(task_key, task_config, parsed["agent_payload"], ctx)
                    if isinstance(_cand, dict) and schema:
                        _coerce_schema_str_fields_from_list(_cand, schema, debug=debug)
                    if (isinstance(_cand, dict) and (_cand.get("jobs") or _cand.get("companies"))
                            and not _validate_response_schema(_cand, schema, task_key)
                            and not _validate_grade_confidence_in_payload(_cand, task_key)):
                        salvaged = _cand
                except Exception as exc:
                    logger.debug("%s | no salvage after agent failure: %s: %s", task_key, type(exc).__name__, exc)
            if _should_store:
                try:
                    await asyncio.to_thread(_store_response_block,
                        entity_type,
                        task_key,
                        batch_id,
                        _failure_response_block_data(index, _audit_response_body(raw_text, parsed, agent_err)),
                        index=index,
                        debug=debug, entity_ids=_store_ids)
                except Exception as exc:
                    _log_swallowed_agent_data(index, task_key, exc)
            _close_hop_ledger(success=False, clear_log=True, failure_error=agent_err)
            return _with_harvest({"success": False, "agent_failure": True, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": agent_err, "raw_response": parsed,
                    "salvaged_response": salvaged, "timesheet": result.get("timesheet", {})})
        # AST-1072: preserve conversational outcome on result before unwrapping payload.
        if is_conversational_task(task_key):
            _perf_keep = parsed.get("agent_performance")
            if isinstance(_perf_keep, dict):
                result["agent_performance"] = _perf_keep
                result["conversational_outcome"] = _agent_performance_status(_perf_keep)
        parsed = parsed["agent_payload"]
        # Model occasionally wraps lines in a list instead of joining with \n — normalize it
        if isinstance(parsed, list):
            parsed = "\n".join(str(item) for item in parsed)
        result["parsed_response"] = parsed

    output_type = task_config.get("output_type", "")
    # For encoded output types: normalize rubric shapes or decode compact string, then validate.
    post_rubric_decode = False
    if rubric_encoded and parsed is not None:
        try:
            from src.core.consult import _normalize_rubric_task_response

            logger.debug(
                "Calling _normalize_rubric_task_response: [task_key=%s, parsed=%s]",
                task_key, parsed,
            )
            parsed = _normalize_rubric_task_response(task_key, task_config, parsed, ctx or {})
            logger.debug("Response from _normalize_rubric_task_response: %s", parsed)
            result["parsed_response"] = parsed
            post_rubric_decode = True
        except Exception as exc:
            logger.exception(
                "%s | %s\n  %s: %s\n  Returning this hop as failed",
                index or "-",
                task_key,
                type(exc).__name__,
                exc,
            )
            if _should_store:
                try:
                    body = _audit_response_body(raw_text, None, str(exc))
                    if isinstance(parsed, str) and parsed.strip():
                        body = f"{body}\n--- agent_payload ---\n{parsed}"
                    await asyncio.to_thread(_store_response_block,
                        entity_type, task_key, batch_id, _failure_response_block_data(index, body), index=index,
                    debug=debug, entity_ids=_store_ids)
                except Exception:
                    _log_swallowed_agent_data(index, task_key)
            _close_hop_ledger(success=False, clear_log=True, failure_error=str(exc))
            return _with_harvest({"success": False, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": str(exc), "timesheet": result.get("timesheet", {})})
    elif "_encoded" in output_type and isinstance(parsed, str):
        try:
            logger.debug(
                "Calling _decode_payload: [task_key=%s, output_type=%s, parsed=%s]",
                task_key, output_type, parsed,
            )
            parsed = _decode_payload(task_key, output_type, parsed, ctx or {})
            logger.debug("Response from _decode_payload: %s", parsed)
            result["parsed_response"] = parsed
            post_rubric_decode = True
        except Exception as exc:
            logger.exception(
                "%s | %s\n  %s: %s\n  Returning this hop as failed",
                index or "-",
                task_key,
                type(exc).__name__,
                exc,
            )
            if _should_store:
                try:
                    body = _audit_response_body(raw_text, None, str(exc))
                    # parsed is still the agent_payload string that failed decode
                    if isinstance(parsed, str) and parsed.strip():
                        body = f"{body}\n--- agent_payload ---\n{parsed}"
                    await asyncio.to_thread(_store_response_block,
                        entity_type, task_key, batch_id, _failure_response_block_data(index, body), index=index,
                    debug=debug, entity_ids=_store_ids)
                except Exception:
                    _log_swallowed_agent_data(index, task_key)
            _close_hop_ledger(success=False, clear_log=True, failure_error=str(exc))
            return _with_harvest({"success": False, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": str(exc), "timesheet": result.get("timesheet", {})})
    if post_rubric_decode:
        if isinstance(parsed, dict) and schema:
            if task_key in _CRAFT_RESUME_NORMALIZE_TASK_KEYS:
                from src.core.candidate import normalize_craft_resume_base_agent_payload

                normalize_craft_resume_base_agent_payload(parsed)
            if task_key == "draft_job_resume":
                from src.core.candidate import normalize_draft_job_resume_agent_payload

                normalize_draft_job_resume_agent_payload(parsed, debug=debug)
            _coerce_schema_str_fields_from_list(parsed, schema, debug=debug)
        err = _validate_response_schema(parsed, schema, task_key)
        if err:
            _warn_hop_no_success(task_key, err)
            if log_batch_id.get():
                flush_log_buffer()
            if _should_store:
                try:
                    await asyncio.to_thread(_store_response_block,
                        entity_type,
                        task_key,
                        batch_id,
                        _failure_response_block_data(index, _validation_failure_audit_body(err, raw_text, parsed)),
                        index=index,
                    debug=debug, entity_ids=_store_ids)
                except Exception:
                    _log_swallowed_agent_data(index, task_key)
            _close_hop_ledger(success=False, clear_log=True, failure_error=str(err))
            return _with_harvest({"success": False, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": err, "timesheet": result.get("timesheet", {})})
        if task_config.get("resume_section_payload") and cd:
            from src.core.candidate import validate_draft_job_resume_payload

            cat_err = validate_draft_job_resume_payload(parsed, cd, debug=debug)
            if cat_err:
                _warn_hop_no_success(task_key, cat_err)
                if log_batch_id.get():
                    flush_log_buffer()
                if _should_store:
                    try:
                        await asyncio.to_thread(_store_response_block,
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(
                                index, _validation_failure_audit_body(cat_err, raw_text, parsed)
                            ),
                            index=index,
                        debug=debug, entity_ids=_store_ids)
                    except Exception:
                        _log_swallowed_agent_data(index, task_key)
                _close_hop_ledger(success=False, clear_log=True, failure_error=str(cat_err))
                return _with_harvest({"success": False, "api_response": result.get("api_response"),
                        "parsed_response": None, "error": cat_err, "timesheet": result.get("timesheet", {})})
        if isinstance(parsed, dict):
            conf_err = _validate_grade_confidence_in_payload(parsed, task_key)
            if conf_err:
                _warn_hop_no_success(task_key, conf_err)
                if _should_store:
                    try:
                        await asyncio.to_thread(_store_response_block,
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(index, _audit_response_body(raw_text, parsed, conf_err)),
                            index=index,
                        debug=debug, entity_ids=_store_ids)
                    except Exception:
                        _log_swallowed_agent_data(index, task_key)
                _close_hop_ledger(success=False, clear_log=True, failure_error=str(conf_err))
                return _with_harvest({"success": False, "api_response": result.get("api_response"),
                        "parsed_response": None, "error": conf_err, "timesheet": result.get("timesheet", {})})

    # AST-997: pin experience metadata after finalize schema OK; Style D job detail on tailor hops.
    if task_key in ("draft_job_resume", "finalize_job_resume") and isinstance(parsed, dict):
        from src.core.candidate import pin_experience_job_facts_from_base

        if task_key == "finalize_job_resume" and cd:
            pin_experience_job_facts_from_base(parsed, cd)
    # SUCCESS: store decoded/validated response block, then build agent_ref
    if envelope_snapshot is not None:
        _perf = envelope_snapshot.get("agent_performance")
        if _perf is not None:
            _owner, _cid = _rubric_feedback_owner_and_candidate(task_key, cd, ctx)
            if _owner and _cid:
                _capture_rubric_vector_feedback(
                    task_key=task_key,
                    owner_task_key=_owner,
                    candidate_id=_cid,
                    batch_id=batch_id,
                    entity_type=entity_type,
                    index=index,
                    perf=_perf,
                    debug=debug,
                    prompt_blocks=prompt_blocks,
                    batch_size=batch_size,
                    completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                )

    # AST-1099/1603: pin proposed_answers; job catalog land via TASK_CONFIG.artifact_key (before run_next).
    resp_id = None
    if _should_store and raw_text:
        try:
            store_content = json.dumps(parsed) if isinstance(parsed, (dict, list)) else (parsed or raw_text)
            resp_id = await asyncio.to_thread(_store_response_block, entity_type, task_key, batch_id, store_content, index=index, debug=debug, entity_ids=_store_ids)
            prompt_blocks.append({"type": "RESPONSE", "id": resp_id})
        except Exception:
            _log_swallowed_agent_data(index, task_key)

    pin_slot = JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK.get(task_key)
    task_cfg = TASK_CONFIG.get(task_key) or {}
    catalog_key = task_cfg.get("artifact_key")
    # Job catalog land via TASK_CONFIG.artifact_key (AST-1603). Candidate craft
    # uses a separate persist_candidate_craft_hops gate below — do not share this branch.
    if (
        result.get("success")
        and task_cfg.get("entity_type") == "job"
        and isinstance(catalog_key, str)
        and catalog_key.strip()
    ):
        if index:
            # Body land uses in-memory parsed — do not gate on resp_id (AST-1600).
            # Lazy import breaks agent↔tracker cycle (consult imports agent).
            try:
                from src.core.tracker import (
                    _coerce_job_replica_parsed,
                    _prepare_job_replica_body,
                    save_job_artifact,
                )

                # Text-format finalize leaves parsed as raw JSON string (AST-1613).
                land_parsed = (
                    _coerce_job_replica_parsed(parsed)
                    if isinstance(parsed, str)
                    else parsed
                )
                body = _prepare_job_replica_body(
                    catalog_key, land_parsed, astral_job_id=index
                )
                if body is None:
                    logger.warning(
                        "%s skipped — catalog %s empty\n  The hop is still success; the replica was not saved",
                        index,
                        catalog_key,
                    )
                else:
                    # AST-1700: pass do_task harvest; job_resume auto-cite stays in tracker.
                    landed = save_job_artifact(
                        index,
                        catalog_key,
                        body,
                        source_artifact_ids=list(source_artifact_ids),
                    )
                    if landed is None:
                        logger.warning(
                            "%s skipped — catalog %s empty\n  The hop is still success; the replica was not saved",
                            index,
                            catalog_key,
                        )
            except Exception as persist_err:
                logger.exception(
                    "%s | %s\n  %s: %s\n  The hop is still success; the replica was not saved",
                    index,
                    task_key,
                    type(persist_err).__name__,
                    persist_err,
                )
    elif pin_slot and result.get("success"):
        if index and resp_id:
            # Lazy import breaks agent↔tracker cycle (consult imports agent).
            from src.core.tracker import pin_job_artifact_agent_data_id
            pin_job_artifact_agent_data_id(index, pin_slot, resp_id, debug=debug)
    # AST-1523: retain draft freeform notes as job artifact metadata (best-effort; do not fail hop).
    if task_key == "draft_job_resume" and result.get("success") and index:
        try:
            # Lazy import breaks agent↔tracker cycle (consult imports agent).
            from src.core.tracker import persist_draft_job_resume_notes

            persist_draft_job_resume_notes(index, parsed)
        except Exception as persist_err:
            logger.exception(
                "%s | %s\n  %s: %s\n  The hop is still success; the notes were not saved",
                index,
                task_key,
                type(persist_err).__name__,
                persist_err,
            )

    # AST-1252: per-hop candidate craft persist (dispatch path; UI keeps suppress_run_next).
    candidate_craft_persisted = False
    if result.get("success") and (ctx or {}).get("persist_candidate_craft_hops") and index:
        try:
            # Lazy import breaks agent↔candidate cycle (candidate imports agent).
            from src.core.candidate import (
                _persist_craft_dispatch_success,
                save_candidate_data,
                split_craft_resume_base_payload,
            )

            parsed_for_persist = result.get("parsed_response")
            task_cfg = TASK_CONFIG.get(task_key) or {}
            artifact_key = task_cfg.get("artifact_key")
            if isinstance(artifact_key, str) and artifact_key.strip():
                if not isinstance(parsed_for_persist, dict):
                    raise ValueError(
                        f"{task_key} parsed_response must be a dict"
                    )
                structure, content = split_craft_resume_base_payload(
                    parsed_for_persist
                )
                save_candidate_data(
                    str(index),
                    "candidate.artifacts.resume_structure",
                    structure,
                )
                # AST-1700: harvest only on operative str-path insert of craft body.
                save_candidate_data(
                    str(index),
                    artifact_key,
                    content,
                    source_artifact_ids=list(source_artifact_ids),
                )
            else:
                _persist_craft_dispatch_success(
                    str(index), task_key, parsed_for_persist
                )
            candidate_craft_persisted = True
        except Exception as persist_err:
            logger.exception(
                "%s | %s\n  %s: %s\n  This hop is failing closed",
                index,
                task_key,
                type(persist_err).__name__,
                persist_err,
            )
            _close_hop_ledger(
                success=False, clear_log=True, failure_error=str(persist_err),
            )
            return _with_harvest({
                "success": False,
                "api_response": result.get("api_response"),
                "parsed_response": None,
                "error": str(persist_err),
                "timesheet": result.get("timesheet") or {},
            })

    # Lightweight agent_ref for batch callers (roster/consult tag RESPONSE entity_ids)
    if _should_store:
        try:
            total_cost = compute_batch_cost(batch_id)
            entity_cost = total_cost / batch_size if batch_size > 0 else total_cost
            result["agent_ref"] = {
                "batch_id": batch_id,
                "task_key": task_key,
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "entity_cost": round(entity_cost, 7),
                "prompt_blocks": prompt_blocks,
            }
        except Exception as exc:
            _log_swallowed_agent_data(index, task_key, exc)


    trigger_state, graduate_on_terminal = _dispatch_chain_ctx(ctx)
    _write_dispatch_hop_label_on_success(
        task_key=task_key,
        entity_type=entity_type or "",
        index=index,
        ctx=ctx,
        trigger_state=trigger_state,
        debug=debug,
    )

    planned_next = (agent_task_row.get("run_next") or "").strip()
    effective_next = planned_next
    # AST-1113: caller walks run_next itself (per-hop persist) — do not recurse here.
    if (ctx or {}).get("suppress_run_next"):
        effective_next = ""
    # AST-469: roster select_job_page chains to parse_job_list only when titles were confirmed —
    # DB run_next may be set unconditionally; suppress for other response_type values.
    if effective_next and task_key == "select_job_page":  # pragma: no branch
        rp_sel = parsed if isinstance(parsed, dict) else None
        if not (rp_sel and str(rp_sel.get("response_type") or "") == "JOBLIST_TITLES"):  # pragma: no branch
            effective_next = ""

    hop_ctx = _chain_tokens_for_next_hop(
        resolved_system=system_content,
        resolved_cache_a=rca or "",
        resolved_cache_b=rcb or "",
        resolved_cache_c=rcc or "",
        resolved_cache_d=rcd or "",
        parsed=result.get("parsed_response"),
    )
    child_live = live_content
    if effective_next and ctx and callable(ctx.get("resolve_run_next_live")):  # pragma: no branch
        try:
            raw = ctx["resolve_run_next_live"](parsed)
        except Exception as exc:
            logger.exception(
                "%s | %s\n  %s: %s\n  Continuing with live_content as-is",
                index or "-",
                task_key,
                type(exc).__name__,
                exc,
            )
            raw = None
        if isinstance(raw, tuple) and len(raw) == 2:  # pragma: no branch
            dom_next, vis_next = raw[0], raw[1]
            dom_next = (dom_next or "").strip()
            vis_next = (vis_next or "").strip()
            if vis_next:  # pragma: no branch
                hop_ctx["JOB_LIST_VISIBLE"] = vis_next
            if dom_next:  # pragma: no branch
                child_live = dom_next
            else:
                child_live = live_content
                if task_key == "select_job_page" and planned_next == "parse_job_list":  # pragma: no branch
                    effective_next = ""
        elif isinstance(raw, str):  # pragma: no branch
            sdom = raw.strip()
            child_live = sdom if sdom else live_content
        # else: keep child_live = live_content
    # Empty TASK / culled DOM would send wrong parent PJL blob into parse_job_list — suppress chain instead.
    if effective_next and task_key == "select_job_page" and planned_next == "parse_job_list":  # pragma: no branch
        if not (child_live or "").strip():  # pragma: no branch
            effective_next = ""

    if not effective_next:
        # AST-1548: finalize resume/cover body replicas (+ proposed_answers pin) already ran above;
        # do not re-enable terminal persist_job_artifact_from_parsed here.
        if result.get("success") and index:
            _maybe_graduate_dispatch_chain(
                job_id=index,
                trigger_state=trigger_state,
                graduate_on_terminal=graduate_on_terminal,
                debug=debug,
            )
        _close_hop_ledger(success=True, clear_log=True)
        return result
    if effective_next not in TASK_CONFIG:
        logger.warning(
            "%s skipped successor %s\n  Returning this hop only",
            task_key,
            effective_next,
        )
        _close_hop_ledger(success=True, clear_log=True)
        return result

    _close_hop_ledger(success=True, clear_log=True)
    caller_only_hop = {
        k: v
        for k, v in hop_ctx.items()
        if k.startswith("CALLER_")
        or k in ("CACHE_BLOCK_A", "CACHE_BLOCK_B", "CACHE_BLOCK_C", "CACHE_BLOCK_D")
    }
    non_caller_hop = {k: v for k, v in hop_ctx.items() if k not in caller_only_hop}
    merged_ctx = _merge_chain_context_for_next_hop(chain_context, non_caller_hop)
    merged_ctx["_hop_parent_task_key"] = task_key
    merged_ctx["_caller_anchor_batch_id"] = batch_id or ""
    for k in CALLER_HOP_TOKEN_NAMES:
        merged_ctx.pop(k, None)
    merged_ctx.pop("_caller_hydration_source", None)
    # AST-1264: re-inject live CALLER_* for candidate-craft recurse (child skip/fail-open).
    if (ctx or {}).get("persist_candidate_craft_hops") and effective_next:
        for k in CALLER_HOP_TOKEN_NAMES:
            val = caller_only_hop.get(k)
            if (val or "").strip():
                merged_ctx[k] = val
    logger.debug(
        "Calling do_task: [task_key=%s, index=%s, batch=%s]",
        effective_next, index, batch_id,
    )
    inner = await do_task(
        effective_next,
        live_content=child_live,
        index=index,
        candidate_data=candidate_data,
        ctx=ctx,
        debug=debug,
        store_agent_data=store_agent_data,
        chain_context=merged_ctx,
    )
    logger.debug("Response from do_task: %s", inner)
    # AST-469: chained parse hop replaces parsed_response shape — preserve select_job_page payload for roster.
    if isinstance(inner, dict):  # pragma: no branch
        inner = dict(inner)
        inner["run_next_parent_parsed"] = parsed
    return inner


# ---------------------------------------------------------------------------
# preview_prompt — ad-hoc prompt preview (no API call)
# ---------------------------------------------------------------------------

def simulated_chain_context_for_preview(
    parent_task_key: str,
    candidate_data: dict,
    simulate_parsed: Optional[str] = None,
    job_context: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Build callee ``chain_context`` as if parent hop completed with ``simulate_parsed`` payload (admin preview)."""
    agent_row, agent_task_row = _resolve_task_prompts(parent_task_key)
    cd = candidate_data or {}
    _cc = _chain_context(agent_row, cd, parent_task_key, job_context)
    sys_c = resolved_task_system(agent_row, agent_task_row, cd, parent_task_key, _cc, job_context)
    rca = resolve_tokens(agent_task_row.get("cache_prompt") or "", cd, parent_task_key, _cc, job_context)
    rcb = resolve_tokens(agent_task_row.get("cache_prompt_b") or "", cd, parent_task_key, _cc, job_context)
    rcc = resolve_tokens(agent_task_row.get("cache_prompt_c") or "", cd, parent_task_key, _cc, job_context)
    rcd = resolve_tokens(agent_task_row.get("cache_prompt_d") or "", cd, parent_task_key, _cc, job_context)
    parsed_val: Any = simulate_parsed
    if isinstance(simulate_parsed, str) and simulate_parsed.strip().startswith(("{", "[")):
        try:
            parsed_val = json.loads(simulate_parsed)
        except json.JSONDecodeError:
            parsed_val = simulate_parsed
    return _chain_tokens_for_next_hop(
        resolved_system=sys_c,
        resolved_cache_a=rca or "",
        resolved_cache_b=rcb or "",
        resolved_cache_c=rcc or "",
        resolved_cache_d=rcd or "",
        parsed=parsed_val,
    )


def preview_prompt(
    task_key: str,
    candidate_data: dict,
    chain_context: Optional[Dict[str, str]] = None,
    job_context: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Assemble resolved segment text as for ``do_task`` (no Anthropic call).

    Returns ``cache`` legacy alias = cache block A; adds ``cache_a``…``cache_d`` keys."""
    agent_row, agent_task_row = _resolve_task_prompts(task_key)
    cd = candidate_data or {}
    _cc = _chain_context(agent_row, cd, task_key, job_context, chain_context)
    system_out = resolved_task_system(agent_row, agent_task_row, cd, task_key, _cc, job_context)
    # Opaque Astral candidate id only — same stamp do_task / candidate preview use.
    cid = cd.get("_astral_candidate_id") or cd.get("astral_candidate_id") or ""
    system_out = _system_text_with_candidate_prefix(system_out, cid)
    user_out = getTimestampPrefix() + resolve_tokens(agent_task_row.get("user_prompt") or "", cd, task_key, _cc, job_context)
    ca = resolve_tokens(agent_task_row.get("cache_prompt") or "", cd, task_key, _cc, job_context)
    cb = resolve_tokens(agent_task_row.get("cache_prompt_b") or "", cd, task_key, _cc, job_context)
    cc = resolve_tokens(agent_task_row.get("cache_prompt_c") or "", cd, task_key, _cc, job_context)
    cd_ = resolve_tokens(agent_task_row.get("cache_prompt_d") or "", cd, task_key, _cc, job_context)
    noc = resolve_tokens(agent_task_row.get("nocache_prompt") or "", cd, task_key, _cc, job_context)
    return {
        "system": system_out,
        "user": user_out,
        "cache": ca,
        "cache_a": ca,
        "cache_b": cb,
        "cache_c": cc,
        "cache_d": cd_,
        "nocache": noc,
    }


# ---------------------------------------------------------------------------
# AST-531 — per-hop dispatch_ledger for run_next chains (entity claim batch_id
# stays on dispatcher ctx["entity_batch_id"]; hop audit batch_id is separate).
# ---------------------------------------------------------------------------

def _current_agent_task_run_next(task_key: str) -> str:
    """Return stripped run_next from current agent_task row, or '' if none (non-LLM dispatch keys)."""
    row = get_agent_task(task_key)
    if not row:
        return ""
    return (row.get("run_next") or "").strip()


def _in_run_next_chain(
    *,
    chain_context: Optional[Dict[str, str]],
    agent_task_row: Dict[str, Any],
) -> bool:
    """True when this do_task invocation is a run_next hop (child or entry with a planned next hop)."""
    if (chain_context or {}).get("_hop_parent_task_key"):
        return True
    return bool((agent_task_row.get("run_next") or "").strip())


def _open_run_next_hop_ledger(
    task_key: str,
    candidate_id: str,
    entity_type: str,
    batch_size: int = 1,
) -> str:
    hop_batch_id = f"{task_key}-{_uuid4()}"
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    database.save_dispatch_ledger(
        hop_batch_id,
        task_key,
        candidate_id,
        started_at,
        status="RUNNING",
        entity_type=entity_type,
        batch_size=batch_size,
    )
    log_batch_id.set(hop_batch_id)
    log_candidate_id.set(candidate_id)
    return hop_batch_id


def _finalize_run_next_hop_ledger(
    hop_batch_id: str,
    *,
    success: bool,
    batch_size: int = 1,
) -> None:
    completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    total_cost = compute_batch_cost(hop_batch_id)
    if success:
        database.update_dispatch_ledger(
            hop_batch_id,
            status="COMPLETED",
            completed_at=completed_at,
            total_processed=1,
            total_passed=1,
            total_failed=0,
            total_errors=0,
            total_cost=total_cost,
            entity_cost=total_cost,
        )
    else:
        database.update_dispatch_ledger(
            hop_batch_id,
            status="FAILED",
            completed_at=completed_at,
            total_processed=1,
            total_passed=0,
            total_failed=1,
            total_errors=0,
            total_cost=total_cost,
            entity_cost=total_cost,
        )


# ---------------------------------------------------------------------------
# run_adhoc_workbench_test — workbench Test with ledger + agent_data
# run_adhoc — bare ad-hoc calls (no ledger / agent_data; use wrapper for Test)
# ---------------------------------------------------------------------------

@_with_log_debug
async def run_adhoc_workbench_test(
    workbench_task_key: str,
    candidate_id: str,
    entity_id: Optional[str] = None,
    system_content: str = "",
    user_content: str = "",
    cache_content: Optional[str] = None,
    cache_content_b: Optional[str] = None,
    cache_content_c: Optional[str] = None,
    cache_content_d: Optional[str] = None,
    nocache_content: Optional[str] = None,
    live_content: Optional[str] = None,
    model_code: Optional[str] = None,
    *,
    server_id: Optional[str] = None,
    tier: Optional[Dict[str, Any]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[str] = "text",
    context: Optional[str] = None,
    candidate_api_keys: Optional[Dict[str, str]] = None,
    task_key_uuid: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Wrap run_adhoc with dispatch_ledger, log_batch_id, and agent_data for workbench Test."""
    catalog_task_key = (workbench_task_key or "").strip()
    if catalog_task_key.startswith("adhoc-"):
        catalog_task_key = catalog_task_key[len("adhoc-"):]
    ledger_task_key = f"adhoc-{catalog_task_key}"
    batch_id = f"{ledger_task_key}-{_uuid4()}"
    entity_type = (TASK_CONFIG.get(catalog_task_key) or {}).get("entity_type") or "candidate"
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    database.save_dispatch_ledger(
        batch_id,
        ledger_task_key,
        candidate_id,
        started_at,
        status="RUNNING",
        entity_type=entity_type,
        batch_size=1,
    )
    log_batch_id.set(batch_id)
    log_candidate_id.set(candidate_id or None)
    logger.info(
        "%s | dispatch %s starting %s — 1 available (batch: %s)",
        candidate_id or "-",
        entity_type or "-",
        ledger_task_key,
        batch_id,
    )
    result: Dict[str, Any]
    try:
        try:
            _store_prompt_blocks(
                entity_type=entity_type,
                task_key=workbench_task_key,
                batch_id=batch_id,
                # Match run_adhoc wire prefix (assembly prefixes the unresolved body again).
                system_content=_system_text_with_candidate_prefix(system_content, candidate_id),
                caches_resolved_four=(
                    cache_content or "",
                    cache_content_b or "",
                    cache_content_c or "",
                    cache_content_d or "",
                ),
                nocache_content=nocache_content,
                user_content=user_content,
                live_content=live_content,
                debug=debug,
                entity_id=entity_id if entity_id else None,
            )
        except Exception as exc:
            _log_swallowed_agent_data(entity_id or candidate_id, workbench_task_key, exc)

        try:
            logger.debug(
                "Calling run_adhoc: [task_key=%s, candidate=%s, server=%s, model=%s]",
                workbench_task_key, candidate_id, server_id, model_code,
            )
            result = await run_adhoc(
                system_content=system_content,
                user_content=user_content,
                cache_content=cache_content,
                cache_content_b=cache_content_b,
                cache_content_c=cache_content_c,
                cache_content_d=cache_content_d,
                nocache_content=nocache_content,
                live_content=live_content,
                model_code=model_code,
                server_id=server_id,
                tier=tier,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                context=context,
                candidate_id=candidate_id,
                candidate_api_keys=candidate_api_keys,
                task_key_uuid=task_key_uuid,
                debug=debug,
            )
            logger.debug("Response from run_adhoc: %s", result)
        except Exception as exc:
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=started_at,
                total_processed=1,
                total_failed=0,
                total_errors=1,
            )
            logger.exception(
                "%s | adhoc %s\n  %s: %s\n  This test is recorded FAILED",
                candidate_id or "-",
                ledger_task_key,
                type(exc).__name__,
                exc,
            )
            raise

        if not result.get("success"):
            err = result.get("error", "Ad hoc test failed")
            logger.warning(
                "%s skipped — adhoc failed: %s\n  This test is recorded FAILED",
                candidate_id or "-",
                err,
            )
            raw_for_audit = None
            api_resp = result.get("api_response")
            if api_resp:
                try:
                    raw_for_audit = extract_api_response_text(api_resp)
                except ValueError:
                    pass
            _fc = result.get("failure_class")
            _fc_s = str(_fc).strip() if _fc is not None else ""
            audit_body = _provider_failure_audit_body(
                str(result.get("error") or "Generation failed"),
                raw_for_audit,
                parsed=result.get("parsed_response"),
                failure_class=_fc_s or None,
            )
            try:
                _store_response_block(
                    entity_type,
                    workbench_task_key,
                    batch_id,
                    _failure_response_block_data(entity_id, audit_body),
                    index=entity_id,
                    debug=debug)
            except Exception as exc:
                _log_swallowed_agent_data(entity_id or candidate_id, workbench_task_key, exc)
        else:
            parsed = result.get("parsed_response")
            if isinstance(parsed, dict) and "agent_payload" in parsed:
                body = parsed["agent_payload"]
            else:
                body = parsed
            try:
                response_text = _caller_response_blob(body)
                _store_response_block(
                    entity_type,
                    workbench_task_key,
                    batch_id,
                    response_text,
                    index=entity_id,
                    debug=debug)
            except Exception:
                _log_swallowed_agent_data(entity_id or candidate_id, workbench_task_key)

        completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        total_cost = compute_batch_cost(batch_id)
        if result.get("success"):
            database.update_dispatch_ledger(
                batch_id,
                status="COMPLETED",
                completed_at=completed_at,
                total_processed=1,
                total_passed=1,
                total_failed=0,
                total_errors=0,
                total_cost=total_cost,
            )
            logger.info(
                "%s | dispatch %s task completed: %s pass:%s fail:%s error:%s (batch: %s)",
                candidate_id or "-",
                entity_type or "-",
                ledger_task_key,
                1,
                0,
                0,
                batch_id,
            )
        else:
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=completed_at,
                total_processed=1,
                total_passed=0,
                total_failed=1,
                total_errors=0,
                total_cost=total_cost,
            )
        result["batch_id"] = batch_id
        return result
    finally:
        flush_log_buffer()
        log_batch_id.set(None)
        log_candidate_id.set(None)


async def run_adhoc(
    system_content: str,
    user_content: str,
    cache_content: Optional[str] = None,
    cache_content_b: Optional[str] = None,
    cache_content_c: Optional[str] = None,
    cache_content_d: Optional[str] = None,
    nocache_content: Optional[str] = None,
    live_content: Optional[str] = None,
    model_code: Optional[str] = None,
    *,
    server_id: Optional[str] = None,
    tier: Optional[Dict[str, Any]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[str] = "text",
    context: Optional[str] = None,
    candidate_id: Optional[str] = None,
    candidate_api_keys: Optional[Dict[str, str]] = None,
    task_key_uuid: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Run an ad-hoc prompt without DB prompt resolution or agent_data storage.
    Routes by catalog server; sends only the candidate's key for that server (no fallback — AST-1879)."""
    if not model_code:
        raise ValueError("run_adhoc requires model_code (catalog SKU)")
    if not server_id or tier is None:
        raise ValueError("run_adhoc requires server_id and tier (resolve_agent_settings route)")
    api_key = (candidate_api_keys or {}).get(server_id)
    if not api_key:
        return _missing_server_key_result(candidate_id, server_id)

    system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens = _assemble_blocks_seven_segment(
        system_content=system_content,
        user_content=user_content,
        caches_resolved_four=(cache_content, cache_content_b, cache_content_c, cache_content_d),
        nocache_content=nocache_content,
        live_content=live_content,
        model_code=model_code,
        skip_cache=False,
        candidate_id=candidate_id,
    )

    logger.debug(
        "Calling _send_to_server: [task_key=adhoc, server=%s, model=%s, max_tokens=%s, temp=%s, effort=%s, candidate=%s]",
        server_id, model_code, max_tokens, temperature, tier.get("reasoning_effort"), candidate_id or "",
    )
    result = await _send_to_server(
        user_blocks,
        server_id=server_id,
        sku=model_code,
        tier=tier,
        api_key=api_key,
        system_blocks=system_blocks,
        response_format=response_format,
        prompt_label="adhoc",
        candidate_id=candidate_id,
        temperature=temperature,
        max_tokens=max_tokens,
        debug=debug,
        task_key_uuid=task_key_uuid,
        no_cache_prompt_tokens=no_cache_prompt_tokens,
        no_cache_live_tokens=no_cache_live_tokens,
    )
    result["runtime_prompt"] = runtime_prompt
    return result



# ---------------------------------------------------------------------------
# Entity agent story (AST-984 / AST-1354) — lives with agent_data, not roster
# ---------------------------------------------------------------------------

def get_entity_agent_story(entity: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Expand latest-per-task agent refs (agent_data.entity_id) with block content.

    Entity type from astral_job_id / short_name / astral_candidate_id presence.
    For job / company entities, NO_CACHE and RESPONSE blocks of every task are cut to this
    entity via _slice_entity_block (AST-2030): a block carrying only other entities becomes ""
    (frontend skips it); a block with no id-keyed segments (legacy) shows whole.
    Scored tasks also attach vector_grades and rubric_artifact for display.

    Duplicate block types get a counter suffix: NO_CACHE, NO_CACHE (2).
    """
    if entity.get("astral_job_id"):
        entity_type, entity_id = "job", entity["astral_job_id"]
    elif entity.get("astral_candidate_id"):
        entity_type, entity_id = "candidate", entity["astral_candidate_id"]
    elif entity.get("short_name"):
        entity_type, entity_id = "company", entity["short_name"]
    else:
        return []

    # AST-1274/AST-1354: soft-fail (empty/partial story); log the throw then continue.
    try:
        entries = database.list_entity_latest_agent_refs(entity_type, entity_id)
    except Exception as exc:
        logger.exception(
            "%s | %s story\n  %s: %s\n  Returning an empty story",
            entity_id,
            entity_type,
            type(exc).__name__,
            exc,
        )
        return []
    if not entries:
        return []

    # Per-id resolve: one dangling sibling must not blank healthy RESPONSE content.
    all_ids = [
        b["id"]
        for e in entries
        for b in (e.get("prompt_blocks") or [])
        if isinstance(b, dict) and b.get("id")
    ]
    data_map: Dict[str, Any] = {}
    for bid in all_ids:
        if bid in data_map:
            continue
        try:
            row = _get_agent_data_row(bid)
            if row:
                data_map[bid] = row
        except Exception as exc:
            logger.exception(
                "%s | %s story block %s\n  %s: %s\n  Continuing with a partial story",
                entity_id,
                entity_type,
                bid,
                type(exc).__name__,
                exc,
            )

    entity_ref_id = entity.get("astral_job_id") or entity.get("short_name")

    enriched = []
    logger.debug("Beginning get_entity_agent_story loop on %s items", len(entries))
    for e in entries:
        task_key = e.get("task_key", "")
        task_cfg = TASK_CONFIG.get(task_key, {})
        is_scored = bool(task_cfg.get("scored"))

        type_counts: Dict[str, int] = {}
        blocks = []
        for ref in (e.get("prompt_blocks") or []):
            if not isinstance(ref, dict):
                continue
            btype = ref.get("type", "UNKNOWN")
            bid = ref.get("id", "")
            type_counts[btype] = type_counts.get(btype, 0) + 1
            label = btype if type_counts[btype] == 1 else f"{btype} ({type_counts[btype]})"
            content = data_map.get(bid, {}).get("block_data", "") or ""

            if btype in ("NO_CACHE", "RESPONSE") and entity_ref_id:
                # AST-2030: every task, not only scored; another chunk's block → "" (D2)
                content = _slice_entity_block(content, entity_ref_id) or ""

            blocks.append({"type": label, "id": bid, "content": content})

        entry = {**e, "blocks": blocks}

        # AST-1550: optional display name from live agent_task (omit when blank).
        task_name = ((get_agent_task(task_key) or {}).get("task_name") or "").strip()
        if task_name:
            entry["task_name"] = task_name

        if is_scored:
            grades_key = task_cfg.get("grades_key")
            data_blob = entity.get("job_data") if entity.get("astral_job_id") else entity.get("company_data")
            data_blob = data_blob if isinstance(data_blob, dict) else {}
            entry["vector_grades"] = data_blob.get(grades_key) if grades_key else None
            entry["rubric_artifact"] = task_cfg.get("rubric_artifact")

        enriched.append(entry)

    logger.debug("End get_entity_agent_story loop after %s items", len(enriched))
    return enriched


def _slice_entity_block(content: str, entity_id: str) -> Optional[str]:
    """One entity's slice of a stored NO_CACHE / TASK / RESPONSE block (AST-2030).

    Whole block when it has no id-keyed segments (legacy positional, single-entity, shared prompt);
    None when it has segments but none for entity_id (another chunk's call in the same batch).
    """
    segments = split_entity_segments(content)
    out = segments.get(entity_id) if segments else content
    logger.debug("Response from _slice_entity_block: %s", out)
    return out


def _entity_call_view(content: str, entity_id: str) -> Optional[str]:
    """Block as a one-entity (Each-mode) call would have stored it (AST-2052).

    JSON companies[] / jobs[] → same object with only this entity's item; tagged text → preamble
    before the first [entity_id=…] tag + this entity's segment. Whole / None exactly as _slice_entity_block.
    """
    seg = _slice_entity_block(content, entity_id)
    if seg is None or seg == content:
        return seg  # other chunk's call, or no id-keyed segments (legacy / shared prompt)
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        data = None
    # Same array precedence as split_entity_segments: companies[] first, else jobs[]
    arr_key, id_key = next(
        ((k, i) for k, i in (("companies", "company_id"), ("jobs", "astral_job_id"))
         if isinstance(data, dict) and isinstance(data.get(k), list)),
        (None, None),
    )
    if arr_key:
        items = [it for it in data[arr_key] if isinstance(it, dict) and str(it.get(id_key)) == entity_id]
        out = json.dumps({**data, arr_key: items})
    else:
        out = content[: max(content.find("[entity_id="), 0)] + seg
    logger.debug("Response from _entity_call_view: %s", out)
    return out


# ---------------------------------------------------------------------------
# get_agent_data — retrieve stored blocks for a batch
# ---------------------------------------------------------------------------

def get_agent_data(
    batch_id: str,
    block_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve agent_data blocks for a batch.
    With entity_id (AST-2030 / AST-2052), rows read as one Each-mode call for that entity: NO_CACHE / TASK / RESPONSE via _entity_call_view (other chunks' rows dropped, rows without id-keyed segments whole), blank rows omitted.
    SYSTEM / CACHE_A–D are shared prompt and pass through."""
    rows = get_agent_data_by_batch(batch_id, block_type)
    if not entity_id:
        return rows

    result = []
    logger.debug("Beginning get_agent_data slice loop on %s items", len(rows))
    for row in rows:
        if row.get("block_type") not in ("NO_CACHE", "TASK", "RESPONSE"):
            if (row.get("block_data") or "").strip():
                result.append(row)
            continue
        segment = _entity_call_view(row.get("block_data") or "", entity_id)
        if segment is None:
            continue  # another chunk's call — carries only other entities
        if not segment.strip():
            continue  # AST-2052: skip empty prompt content
        result.append({**row, "block_data": segment})
    logger.debug("End get_agent_data slice loop after %s items", len(result))
    return result


def list_agent_data_runs(
    *,
    candidate_id: Optional[str] = None,
    task_key: Optional[str] = None,
    limit: Optional[int] = None,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """Ad Hoc import list: filtered/capped agent_data batches, newest first."""
    _dbg = log_debug.set(bool(debug))
    try:
        rows = list_agent_data_batches(
            candidate_id=candidate_id,
            task_key=task_key,
            limit=limit,
        )
        logger.debug("Beginning list_agent_data_runs loop on %s items", len(rows))
        logger.debug("End list_agent_data_runs loop after %s items", len(rows))
        return rows
    finally:
        log_debug.reset(_dbg)


def get_entity_response(batch_id: str, entity_id: str) -> Optional[Dict[str, Any]]:
    """Return the RESPONSE block for a batch and extract entity-specific content.
    If batch_size was 1, returns the full response. Otherwise extracts the segment
    whose key matches entity_id.
    Multiple RESPONSE rows per batch (parallel per-entity do_task) are scanned newest-first."""
    rows = get_agent_data_by_batch(batch_id, block_type="RESPONSE")
    if not rows:
        return None
    # Prefer a row whose content maps to this entity (JSON jobs[], text [id] prefix, etc.)
    for row in reversed(rows):
        content = row.get("block_data") or ""
        segment = _extract_entity_segment(content, entity_id)
        if segment is not None:
            result = dict(row)
            result["block_data"] = segment
            return result
    row = rows[-1]
    content = row.get("block_data") or ""
    segment = _extract_entity_segment(content, entity_id)
    result = dict(row)
    result["block_data"] = segment if segment is not None else content
    return result


def _extract_entity_segment(content: str, entity_id: str) -> Optional[str]:
    """Pull the entity-specific section out of a batch response string.
    Tries JSON first (jobs/companies/results lists keyed by astral_job_id or company_id).
    Falls back to None (caller keeps full content)."""
    if not content or not entity_id:
        return None
    try:
        data = json.loads(content)
        # Batch responses: jobs[{astral_job_id}], companies[{company_id}], results[], entities[]
        if isinstance(data, dict):
            for arr_key, id_key in (
                ("companies", "company_id"),
                ("jobs", "astral_job_id"),
                ("results", "astral_job_id"),
                ("entities", "astral_job_id"),
            ):
                rows = data.get(arr_key)
                if not isinstance(rows, list):
                    continue
                for item in rows:
                    if not isinstance(item, dict):
                        continue
                    if item.get(id_key) == entity_id or item.get("company_id") == entity_id:
                        return json.dumps(item)
            # Flat single-entity response
            if (
                data.get("astral_job_id") == entity_id
                or data.get("company_id") == entity_id
                or len(data) > 0
            ):
                return content
    except (json.JSONDecodeError, TypeError):
        pass
    # Plain text: look for an entity_id boundary marker
    marker = f"[{entity_id}]"
    if marker in content:
        start = content.index(marker)
        # Find next marker to delimit the segment
        rest = content[start + len(marker):]
        next_bracket = rest.find("[") if "[" in rest else -1
        return rest[:next_bracket].strip() if next_bracket > 0 else rest.strip()
    return None


# ---------------------------------------------------------------------------
# compute_batch_cost — sum timesheets for a batch
# ---------------------------------------------------------------------------

def compute_batch_cost(batch_id: str) -> float:
    """Sum all timesheet cost components for a batch_id. Returns total cost as float."""
    costs = sum_cost_by_batch([batch_id])
    return costs.get(batch_id, 0.0)
