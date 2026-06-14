# -*- coding: utf-8 -*-
"""
Core agent orchestration module.

Single entry point for all AI agent interactions. Owns do_task, prompt assembly,
agent_data storage, and cost calculation. Keeps anthropic.py as a pure API client.

Layer: core → data, external, utils  (never ← ui)
"""

import hashlib
import json
from logging import DEBUG as _LOG_DEBUG
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.data import database
from src.data.database import (
    add_agent_response_entry,
    append_agent_response,
    get_agent_task,
    get_agent,
    save_agent_data,
    get_agent_data_by_batch,
    get_agent_data as _get_agent_data_row,
    get_agent_data_for_ids,
    sum_cost_by_batch,
)
from src.core.timesheets import record_timesheet_entry
from src.external.anthropic import send_to_anthropic, getTimestampPrefix, extract_api_response_text
from src.external.deepseek import send_to_deepseek
from src.utils.config import (
    TASK_CONFIG, BASE_SCHEMA, BLOCK_TYPES, ASTRAL_CONFIG, BUILD_CONFIG,
    resolve_tokens, get_model, CHARS_PER_TOKEN, DEEPSEEK_MODEL_PRICING,
    chain_context_selected_agent,
    get_active_llm_provider,
    resolve_brain_setting_to_anthropic_agent_key,
    resolve_brain_setting_to_deepseek_tier_meta,
    CALLER_HOP_TOKEN_NAMES,
    resume_artifact_hop_task_keys,
    resume_artifact_next_compound_state,
    _TOKEN_RE,
)
from src.utils.formatting import clean_encoded_agent_payload, coerce_grades_encoded_json_parse
from src.utils.logging import flush_log_buffer, get_logger, log_batch_id

logger = get_logger(__name__)

# Sentinel: production _store_prompt_blocks passes four cache slots; pytest uses legacy ``cache_content=``.
_PB_SLOT_OMIT = object()

# Batch encoded consult dispatch: models must return the usual JSON envelope, not bare compact lines (AST-501 / AST-503).
_STRICT_ENCODED_BATCH_CONSULT_KEYS = frozenset({
    "qualify_job_listings",
    "evaluate_jd",
    "grade_do",
    "grade_get",
    "grade_like",
})


def _strict_encoded_batch_consult_envelope_err(task_key: str, parsed: Any) -> Optional[str]:
    """Return error detail if encoded-batch consult response bypasses envelope rules; otherwise None."""
    if task_key not in _STRICT_ENCODED_BATCH_CONSULT_KEYS or parsed is None:
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
    """Walk decoded payload for grades[] or jobs[].grades[] and validate confidence rules."""
    if not isinstance(parsed, dict):
        return None
    jobs = parsed.get("jobs")
    if isinstance(jobs, list):
        for ji, job in enumerate(jobs):
            if not isinstance(job, dict):
                continue
            glist = job.get("grades")
            if isinstance(glist, list) and glist:
                err = _validate_grade_confidence_list(glist, f"{task_key} jobs[{ji}].grades")
                if err:
                    return err
    glist = parsed.get("grades")
    if isinstance(glist, list) and glist:
        return _validate_grade_confidence_list(glist, f"{task_key} grades")
    return None


def _decode_payload(task_key: str, output_type: str, payload: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Parse compact pipe-delimited agent_payload string into response_schema shape.

    Grade segments: _GRADE_SEG = 2-char code + grade letter + confidence digit (AST-357).
    pos → astral_job_id via ctx["batch_entities"].
    Vector names: ctx["vector_labels"] maps 2-char codes to full rubric labels; falls back to
    raw 2-char code when the map is absent or incomplete. _render_pass_fail ignores vector names;
    _render_score requires rubric criteria with labels — callers guard with `if rubric_list` before scoring (AST-429).
    "_meta" in output_type determines whether metadata fields after grades are accepted;
    trailing non-grade content raises ValueError for grades-only types.
    "grades_encoded_notes" (do/get/like): non-segment tail rejoins to job["notes"] only (optional).
    """
    with_meta = "_meta" in output_type or output_type == "grades_encoded_prefilter_links"
    with_notes = output_type == "grades_encoded_notes"
    batch_entities = (ctx or {}).get("batch_entities") or []
    payload = clean_encoded_agent_payload(payload or "")
    lines = [ln for ln in payload.splitlines() if ln.strip()]

    vector_labels: Dict[str, str] = (ctx or {}).get("vector_labels") or {}
    result_jobs = []
    for line in lines:
        fields = [f.strip() for f in line.split("|")]
        try:
            pos = int(fields[0])
        except (ValueError, IndexError):
            raise ValueError(f"[{task_key}] bad position field in line: {line!r}")
        if pos < 0 or pos >= len(batch_entities):
            # Model occasionally 1-indexes at round-number boundaries (e.g. returns 100 for last item in batch of 100).
            # Skip the line rather than killing the whole batch — the job stays in its current state and retries next run.
            logger.warning("[%s] skipping line with pos %d out of range (batch=%d): %r", task_key, pos, len(batch_entities), line)
            continue

        grade_segs, meta = [], []
        for f in fields[1:]:
            # Strip ASCII space, hyphen, colon for grade match only; meta keeps pipe-stripped original (AST-483).
            norm = "".join(ch for ch in f if ch not in " -:")
            if _GRADE_SEG.match(norm):
                grade_segs.append(norm)
            else:
                meta.append(f)

        if meta and not with_meta and not with_notes:
            raise ValueError(f"[{task_key}] unexpected trailing content in grades-only line: {line!r}")

        grade_rows: List[Dict[str, Any]] = []
        for seg in grade_segs:
            code, letter, conf_ch = seg[:2], seg[2], seg[3]
            conf_d = int(conf_ch)
            if letter == "X":
                if conf_d != 0:
                    raise ValueError(
                        f"[{task_key}] grade X requires confidence digit 0, got {conf_d} in segment {seg!r} (line {line!r})"
                    )
            elif conf_d not in (1, 2, 3, 4, 5):
                raise ValueError(
                    f"[{task_key}] non-X grade requires confidence 1-5, got {conf_d} in segment {seg!r} (line {line!r})"
                )
            grade_rows.append(
                {"vector": vector_labels.get(code, code), "grade": letter, "confidence": conf_d}
            )
        if logger.isEnabledFor(_LOG_DEBUG):
            logger.debug(
                "[%s] decode line pos=%d astral_job_id=%s segments=%s -> %s",
                task_key,
                pos,
                batch_entities[pos].get("astral_job_id"),
                grade_segs,
                grade_rows,
            )

        job: Dict[str, Any] = {
            "astral_job_id": batch_entities[pos]["astral_job_id"],
            "grades": grade_rows,
        }
        if with_meta:
            if output_type == "grades_encoded_prefilter_links":
                from src.core.consult import _parse_link_index_field

                for m in meta:
                    if re.match(r"^JOB:", m, re.I):
                        job["possible_job_links"] = _parse_link_index_field(m)
                    elif re.match(r"^CULT:", m, re.I):
                        job["culture_links_to_explore"] = _parse_link_index_field(m)
            else:
                for i, key in enumerate(("company_job_id", "job_title", "job_link")):
                    if i < len(meta):
                        job[key] = meta[i] or None
                # key:value extras → job_data dict (location, salary_range, company name, etc.)
                if meta[3:]:
                    job["job_data"] = {
                        k.strip(): (v.strip() or None)
                        for field in meta[3:] if ":" in field
                        for k, v in [field.split(":", 1)]
                    }
        elif with_notes and meta:
            joined = "|".join(meta).strip()
            if joined:
                job["notes"] = joined

        result_jobs.append(job)

    return {"jobs": result_jobs}


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
) -> Optional[Dict[str, str]]:
    if not _single_job_in_scope(ctx, index):
        return None
    # consult imports do_task at module load; import here only to avoid import cycle.
    from src.core import consult as _consult

    builder = getattr(_consult, "build_job_token_context", None)
    if builder is None:
        return None
    return builder(_job_row_from_ctx(ctx or {}, str(index)), cd)


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
    )


def _resolve_task_prompts(task_key: str):
    """Fetch and validate agent_task + agent rows for a task_key.
    Returns (agent_row, agent_task_row). Raises ValueError on misconfiguration."""
    agent_task_row = get_agent_task(task_key)
    if not agent_task_row:
        raise ValueError(f"No agent_task row for '{task_key}'. Run sync_agent_tasks or configure via Manage Tasks.")
    agent_id = (agent_task_row.get("agent_id") or "").strip()
    if not agent_id:
        raise ValueError(f"agent_task '{task_key}' has no agent_id assigned. Configure via Manage Tasks.")
    agent_row = get_agent(agent_id)
    if not agent_row:
        raise ValueError(f"Agent '{agent_id}' referenced by task '{task_key}' not found.")
    return agent_row, agent_task_row


def _chain_context(agent_row: Dict[str, Any], extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Chain/runtime tokens for resolve_tokens (AST-304). AST-303 merges parent-hop tokens into `extra`."""
    base = chain_context_selected_agent(agent_row.get("content"))
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


def _caller_key_status(caller_map: Dict[str, str]) -> str:
    parts: list[str] = []
    for name in CALLER_HOP_TOKEN_NAMES:
        stripped = (caller_map.get(name) or "").strip()
        if stripped:
            parts.append(f"{name}=populated(len={len(stripped)})")
        else:
            parts.append(f"{name}=empty")
    return ",".join(parts)


def _do_task_debug_logger(debug: bool):
    """Return a debug-flagged logger for do_task contract lines; caller checks debug first."""
    return get_logger(__name__, debug_flag=True) if debug else logger


def _do_task_debug_entry(
    *,
    task_key: str,
    index: Optional[str],
    batch_id: Optional[str],
    in_chain: bool,
    debug: bool,
) -> None:
    if not debug:
        return
    dbg = get_logger(__name__, debug_flag=True)
    entity_id = (index or task_key or "?").strip()
    if task_key in resume_artifact_hop_task_keys():
        keys = resume_artifact_hop_task_keys()
        hop_idx = keys.index(task_key) + 1
        hop_total = len(keys)
        dbg.debug_index(
            func=f"do_task({task_key})",
            index=hop_idx,
            total=hop_total,
            identifier=entity_id,
            outcome="hop",
        )
    else:
        dbg.debug_index(
            func="do_task",
            index=1,
            total=1,
            identifier=entity_id,
            outcome="task start",
        )
    dbg.debug_detail(
        f"task_key={task_key} batch_id={batch_id or ''} index={index or ''} "
        f"in_run_next_chain={in_chain}"
    )


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


def _mid_chain_empty_caller_tokens(
    *,
    callee_task_key: str,
    parent_task_key: str,
    chain_context: Dict[str, str],
    segment_texts: Dict[str, str],
) -> Optional[str]:
    needed = _referenced_caller_tokens(*segment_texts.values())
    for tok in needed:
        if (chain_context.get(tok) or "").strip() == "":
            return (
                f"Required caller token {{${tok}}} is empty on mid-chain hop "
                f"(task={callee_task_key}, parent={parent_task_key})"
            )
    return None


# AST-597: mid-chain resume — hydrate {$CALLER_*} from stored agent_data
def _resume_artifact_parent_hop_key(entry_task_key: str) -> Optional[str]:
    keys = resume_artifact_hop_task_keys()
    if entry_task_key not in keys:
        return None
    idx = keys.index(entry_task_key)
    if idx == 0:
        return None
    return keys[idx - 1]


_HOP_FAILURE_RESPONSE_PREFIXES = (
    "Validation failed:",
    "Schema parse failed:",
    "JSON parse failed:",
    "Required caller token",
)


def _block_text_by_type(prompt_blocks: List[Dict[str, str]], block_type: str) -> str:
    ids: List[str] = []
    for ref in prompt_blocks or []:
        if isinstance(ref, dict) and ref.get("type") == block_type and ref.get("id"):
            ids.append(str(ref["id"]))
    if not ids:
        return ""
    data_map = get_agent_data_for_ids(ids)
    for ref in prompt_blocks or []:
        if not isinstance(ref, dict) or ref.get("type") != block_type:
            continue
        bid = ref.get("id")
        if not bid:
            continue
        row = data_map.get(str(bid), {})
        data = row.get("block_data") or row.get("content") or ""
        if isinstance(data, str) and data.strip():
            return data.strip()
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


def _latest_job_hop_agent_ref(job: Dict[str, Any], hop_task_key: str) -> Optional[Dict[str, Any]]:
    entries = job.get("agent_responses") or []
    for ref in reversed(entries):
        if not isinstance(ref, dict):
            continue
        if (ref.get("task_key") or "").strip() != hop_task_key:
            continue
        blocks = ref.get("prompt_blocks") or []
        if not any(isinstance(b, dict) and b.get("type") == "RESPONSE" for b in blocks):
            continue
        response_raw = _block_text_by_type(blocks, "RESPONSE")
        if response_raw and response_raw.startswith(_HOP_FAILURE_RESPONSE_PREFIXES):
            continue
        return ref
    return None


def _caller_chain_context_from_hop_agent_ref(
    agent_ref: Dict[str, Any],
    parent_task_key: str,
) -> Dict[str, str]:
    blocks = agent_ref.get("prompt_blocks") or []
    response_raw = _block_text_by_type(blocks, "RESPONSE")
    parsed = _parsed_response_from_stored_response_text(response_raw, parent_task_key)
    hop_ctx = _chain_tokens_for_next_hop(
        parsed=parsed,
        resolved_system=_block_text_by_type(blocks, "SYSTEM"),
        resolved_cache_a=_block_text_by_type(blocks, "CACHE_A"),
        resolved_cache_b=_block_text_by_type(blocks, "CACHE_B"),
        resolved_cache_c=_block_text_by_type(blocks, "CACHE_C"),
        resolved_cache_d=_block_text_by_type(blocks, "CACHE_D"),
    )
    hop_ctx["_caller_hydration_source"] = "agent_data"
    hop_ctx["_hop_parent_task_key"] = parent_task_key
    return hop_ctx


def _hydrate_resume_entry_chain_context(
    astral_job_id: str,
    entry_task_key: str,
) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    parent = _resume_artifact_parent_hop_key(entry_task_key)
    if parent is None:
        return ({}, None)
    from src.core import tracker

    job = tracker.get_job(astral_job_id)
    if not job:
        return (None, f"Job not found: {astral_job_id}")
    ref = _latest_job_hop_agent_ref(job, parent)
    if ref is None:
        return (
            None,
            f"No stored agent_data for upstream hop {parent!r} on job {astral_job_id}",
        )
    ctx = _caller_chain_context_from_hop_agent_ref(ref, parent)
    if not any((ctx.get(k) or "").strip() for k in CALLER_HOP_TOKEN_NAMES):
        return (None, f"Stored hop {parent!r} has empty caller payload")
    return (ctx, None)


def _maybe_transition_resume_hop_progress(task_key: str, astral_job_id: Optional[str]) -> None:
    if not astral_job_id or task_key not in resume_artifact_hop_task_keys():
        return
    next_compound = resume_artifact_next_compound_state(task_key)
    if not next_compound:
        return
    from src.core import tracker

    try:
        tracker.transition_job_state([astral_job_id], next_compound)
    except ValueError as exc:
        logger.warning(
            "resume hop transition failed job=%s from_hop=%s to=%s: %s",
            astral_job_id,
            task_key,
            next_compound,
            exc,
        )


def _log_chain_entry(task_key: str, batch_id: Optional[str]) -> None:
    logger.info("run_next chain entry: task=%s batch_id=%s", task_key, batch_id or "")


def _log_run_next_hop_boundary(
    *,
    parent_task_key: str,
    child_task_key: str,
    batch_id: Optional[str],
    hop_ctx: Dict[str, str],
) -> None:
    logger.info(
        "run_next hop: %s -> %s batch_id=%s caller_keys=%s",
        parent_task_key,
        child_task_key,
        batch_id or "",
        _caller_key_status(hop_ctx),
    )


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


def _assemble_blocks_seven_segment(
    *,
    system_content: str,
    user_content: str,
    caches_resolved_four: Tuple[Optional[str], Optional[str], Optional[str], Optional[str]],
    nocache_content: Optional[str],
    live_content: Optional[str],
    model_code: str,
    skip_cache: bool = False,
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

    system_block: Dict[str, Any] = {"type": "text", "text": system_content}
    if not skip_cache:
        system_block["cache_control"] = {"type": "ephemeral"}
    system_blocks.append(system_block)
    _track("system_prompt", system_content, not skip_cache)

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
) -> List[Dict[str, str]]:
    """Store prompt blocks in agent_data. Returns prompt_blocks refs for ledger.
    Production: ``caches_resolved_four``. Legacy tests/callers: ``cache_content`` (slot A only)."""
    prompt_blocks: List[Dict[str, str]] = []

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
        )
        return agent_data_id

    prompt_blocks.append({"type": "SYSTEM",   "id": _save("SYSTEM",   system_content)})
    if cache_content is not _PB_SLOT_OMIT:
        if caches_resolved_four is not _PB_SLOT_OMIT:
            raise TypeError("_store_prompt_blocks: pass caches_resolved_four or cache_content, not both")
        if cache_content:
            prompt_blocks.append({"type": "CACHE_A", "id": _save("CACHE_A", cache_content)})
        if nocache_content:
            prompt_blocks.append({"type": "NO_CACHE","id": _save("NO_CACHE", nocache_content)})
        if live_content:
            prompt_blocks.append({"type": "NO_CACHE", "id": _save("NO_CACHE", live_content)})
        if user_content:
            prompt_blocks.append({"type": "TASK",     "id": _save("TASK",     user_content)})
        return prompt_blocks

    if caches_resolved_four is _PB_SLOT_OMIT:
        raise TypeError("_store_prompt_blocks: missing caches_resolved_four or cache_content")
    type_names = ("CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D")
    for bt, blob in zip(type_names, caches_resolved_four):
        if blob and blob.strip():
            prompt_blocks.append({"type": bt, "id": _save(bt, blob)})
    if nocache_content:
        prompt_blocks.append({"type": "NO_CACHE","id": _save("NO_CACHE", nocache_content)})
    if live_content:
        prompt_blocks.append({"type": "NO_CACHE", "id": _save("NO_CACHE", live_content)})
    if user_content:
        prompt_blocks.append({"type": "TASK",     "id": _save("TASK",     user_content)})

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


def _failure_response_block_data(index: Optional[str], body: str) -> str:
    """Prefix so get_entity_response can match one row when a batch has many RESPONSE failures."""
    if index and body is not None:
        return f"[{index}]\n{body}"
    return body


def _store_response_block(
    entity_type: str,
    task_key: str,
    batch_id: str,
    response_text: str,
    created_at: Optional[str] = None,
    index: Optional[str] = None,
) -> str:
    """Store a RESPONSE block in agent_data. On success, response_text is the decoded/validated
    payload; on failure it is the raw API text (or error / parsed fallback). Returns the agent_data_id.
    index is folded into the row id so many do_task calls sharing one dispatch batch_id still get
    distinct rows when response_text matches (INSERT OR IGNORE dedupe)."""
    content_hash = hashlib.sha256(
        f"{batch_id}:RESPONSE:{index or ''}:{response_text}".encode()
    ).hexdigest()[:16]
    agent_data_id = f"{batch_id}-response-{content_hash}"
    save_agent_data(
        agent_data_id=agent_data_id,
        entity_type=entity_type,
        task_key=task_key,
        batch_id=batch_id,
        block_type="RESPONSE",
        block_data=response_text,
        token_size=len(response_text) // CHARS_PER_TOKEN,
        created_at=created_at,
    )
    return agent_data_id


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _coerce_schema_str_fields_from_list(parsed: Dict[str, Any], schema: Dict[str, Dict]) -> None:
    """Join list-of-strings into newline text before str validation (common LLM JSON habit)."""
    payload = _inner_task_payload(parsed)
    if not isinstance(payload, dict):
        return
    for field_name, field_spec in schema.items():
        if not isinstance(field_spec, dict) or field_spec.get("type", "str") != "str":
            continue
        val = payload.get(field_name)
        if isinstance(val, list):
            lines = [str(item).strip() for item in val if item is not None and str(item).strip()]
            payload[field_name] = "\n".join(lines)
            if log_batch_id.get():
                logger.info(
                    "do_task: coerced field %r from list (%d items) to newline string",
                    field_name,
                    len(val),
                )


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

    for field_name, field_spec in schema.items():
        if not isinstance(field_spec, dict):
            continue
        val = payload.get(field_name)
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
        if type_spec == "int" and not isinstance(val, int):
            return f"Field '{field_name}' must be int, got {type(val).__name__}"
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
                item_err = _validate_response_schema(item, items_schema, task_key)
                if item_err:
                    return f"{field_name}[{idx}]: {item_err}"
    return None


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
# Audit logging
# ---------------------------------------------------------------------------

def _store_agent_response(
    task_config: Dict[str, Any],
    task_key: str,
    index: Optional[str],
    raw_response: Any,
    parsed_response: Optional[Any],
    result: Dict[str, Any],
) -> None:
    """Insert into agent_responses if task has entity_type + index. Silent on failure."""
    entity_type = task_config.get("entity_type")
    if not entity_type or not index or raw_response is None:
        return
    request_id = None
    api_resp = result.get("api_response")
    if api_resp is not None:
        request_id = getattr(api_resp, "id", None)
    try:
        add_agent_response_entry(
            task_key=task_key,
            entity_type=entity_type,
            entity_id=index,
            raw_response=raw_response,
            parsed_response=parsed_response,
            runtime_prompt=result.get("runtime_prompt"),
            request_id=request_id,
        )
    except Exception:
        logger.debug("_store_agent_response failed", exc_info=True)


# ---------------------------------------------------------------------------
# do_task — primary orchestration entry point
# ---------------------------------------------------------------------------

async def run_resume_artifact_chain_for_job(
    astral_job_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    *,
    debug: bool = False,
    store_agent_data: bool = True,
    first_task_key: Optional[str] = None,
) -> Dict[str, Any]:
    """AST-300 / AST-370: start the resume artifact do_task chain for one job; further hops use run_next.

    First hop key: ``first_task_key`` when provided (dispatch row wins, AST-534); else
    ``BUILD_CONFIG['resume_artifact_chain']['first_task_key']``. Prefer a job row already
    in ``ctx['job']`` or ``ctx['job_data']`` (matching ``astral_job_id``) so job-scoped
    tokens (``{$VISIBLE_JD}``, etc.) resolve without re-fetching the row.
    Phase E prompts carry JD via system tokens — no runtime live/nocache block.
    """
    from src.core import tracker

    chain_cfg = BUILD_CONFIG.get("resume_artifact_chain") or {}
    entry_key = (first_task_key or "").strip() or (chain_cfg.get("first_task_key") or "").strip()
    if not entry_key or entry_key not in TASK_CONFIG:
        raise ValueError(
            "BUILD_CONFIG['resume_artifact_chain']['first_task_key'] must name a TASK_CONFIG key; "
            f"got {entry_key!r}"
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

    cd = tracker._candidate_data_for_job(astral_job_id)
    company_key = job.get("company")
    company = None
    if isinstance(company_key, str) and company_key.strip():
        company = tracker.get_company(company_key.strip())
    candidate_id = company.get("candidate_id") if company else None
    if not cd:
        detail = f" (candidate_id={candidate_id})" if candidate_id else ""
        return {
            "success": False,
            "error": f"Missing candidate_data for job {astral_job_id}{detail}",
            "api_response": None,
            "parsed_response": None,
            "timesheet": {},
        }

    task_ctx: Dict[str, Any] = {
        **base,
        "batch_entities": [job],
        "batch_size": 1,
        "job": job,
        "candidate_data": cd,
    }
    if candidate_id:
        task_ctx["astral_candidate_id"] = str(candidate_id)
    if "vector_labels" not in task_ctx:
        task_ctx["vector_labels"] = {}

    seed_chain: Optional[Dict[str, str]] = None
    if _resume_artifact_parent_hop_key(entry_key):
        hydrated, err = _hydrate_resume_entry_chain_context(astral_job_id, entry_key)
        if err:
            return {
                "success": False,
                "error": err,
                "api_response": None,
                "parsed_response": None,
                "timesheet": {},
            }
        seed_chain = hydrated

    return await do_task(
        entry_key,
        index=astral_job_id,
        ctx=task_ctx,
        debug=debug,
        store_agent_data=store_agent_data,
        chain_context=seed_chain,
    )


async def run_cover_letter_artifact_chain_for_job(
    astral_job_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    *,
    debug: bool = False,
    store_agent_data: bool = True,
) -> Dict[str, Any]:
    """AST-301 / AST-368: start the cover-letter do_task chain for one job; further hops use run_next.

    First hop key: ``BUILD_CONFIG['cover_letter_artifact_chain']['first_task_key']``. Same ctx/job
    resolution as ``run_resume_artifact_chain_for_job`` so chain tokens (AST-304) and
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

    Args:
        task_key: Task name (e.g. "prefilter", "evaluate_jd")
        live_content: Dynamic content for the prompt (the TASK block)
        index: Entity identifier for context and audit (e.g. astral_job_id). Falls back to task_key.
        candidate_data: Token-resolution dict (optional; ctx supersedes).
        ctx: Full candidate raft dict. Extracts candidate_data + candidate_api_key.
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

    cd = (ctx.get("candidate_data") or {}) if ctx else (candidate_data or {})

    if task_config.get("requires_candidate_key") and not cd:
        logger.warning("do_task(%s): requires_candidate_key is True but no candidate_data provided", task_key)

    api_key_override = None
    candidate_id = ctx.get("astral_candidate_id") if ctx else None
    if candidate_id:
        # Lazy import breaks agent↔candidate cycle (candidate imports agent paths).
        from src.core.candidate import company_search_terms_joined_text
        joined = company_search_terms_joined_text(candidate_id)
        cd = dict(cd)
        arts = dict(cd.get("artifacts") or {})
        arts["company_search_terms"] = joined
        cd["artifacts"] = arts
    if ctx and task_config.get("requires_candidate_key"):
        api_key_override = ctx.get("candidate_api_key")

    agent_row, agent_task_row = _resolve_task_prompts(task_key)
    in_chain = _in_run_next_chain(chain_context=chain_context, agent_task_row=agent_task_row)
    hop_ledger_batch_id: Optional[str] = None
    hop_ledger_closed = False

    chain_entry = _is_chain_entry(chain_context)
    parent_task_key = (chain_context or {}).get("_hop_parent_task_key")
    parent_caller_summary = {
        k: (chain_context or {}).get(k, "")
        for k in CALLER_HOP_TOKEN_NAMES
        if k in (chain_context or {})
    }
    _cc = _chain_context(agent_row, chain_context)
    _jc = _job_context_for_call(ctx, index, cd)

    brain_setting = (agent_row.get("brain_setting") or "").strip()
    if not brain_setting:
        raise ValueError(
            f"Agent '{agent_row.get('agent_id')}' has no brain_setting configured."
        )

    provider = get_active_llm_provider()
    tier_meta: Optional[Dict[str, Any]] = None  # DeepSeek reasoning / vendor flags
    if provider == "anthropic":
        resolved_anthropic_key = resolve_brain_setting_to_anthropic_agent_key(brain_setting)
        model_cfg = get_model(resolved_anthropic_key)
    elif provider == "deepseek":
        resolved_anthropic_key = ""
        tier_meta = resolve_brain_setting_to_deepseek_tier_meta(brain_setting)
        vm = tier_meta["vendor_model"]
        model_cfg = DEEPSEEK_MODEL_PRICING.get(vm)
        if not model_cfg:
            raise ValueError(f"Unknown DeepSeek vendor_model for agent params: {vm!r}")
    else:
        raise ValueError(f"Unknown LLM active_provider {provider!r}")
    agent_temperature = agent_row.get("temperature") if agent_row.get("temperature") is not None else model_cfg["default_temperature"]
    agent_max_tokens = agent_row.get("max_tokens") if agent_row.get("max_tokens") is not None else model_cfg["default_max_tokens"]

    _hop_kw = dict(
        chain_entry=chain_entry,
        parent_task_key=parent_task_key or None,
        parent_caller_summary=parent_caller_summary or None,
    )
    _rt_kw = {**_hop_kw}

    system_content = resolved_task_system(agent_row, agent_task_row, cd, task_key, _cc, _jc, **_rt_kw)
    user_content = resolve_tokens(agent_task_row.get("user_prompt") or "", cd, task_key, _cc, _jc, **_hop_kw)
    rca = resolve_tokens(agent_task_row.get("cache_prompt") or "", cd, task_key, _cc, _jc, **_hop_kw)
    rcb = resolve_tokens(agent_task_row.get("cache_prompt_b") or "", cd, task_key, _cc, _jc, **_hop_kw)
    rcc = resolve_tokens(agent_task_row.get("cache_prompt_c") or "", cd, task_key, _cc, _jc, **_hop_kw)
    rcd = resolve_tokens(agent_task_row.get("cache_prompt_d") or "", cd, task_key, _cc, _jc, **_hop_kw)

    def _slot(res: str) -> Optional[str]:
        v = (res or "").strip()
        return v if v else None

    caches_four = (_slot(rca), _slot(rcb), _slot(rcc), _slot(rcd))
    nocache_content = resolve_tokens(agent_task_row.get("nocache_prompt") or "", cd, task_key, _cc, _jc, **_hop_kw) or None

    snap = (ctx or {}).get("intake_prompt_snapshot")
    if isinstance(snap, dict) and snap and task_key.startswith("intake_"):
        if "system" in snap:
            system_content = snap.get("system") or ""
        rca = snap.get("cache_a") or ""
        rcb = snap.get("cache_b") or ""
        rcc = snap.get("cache_c") or ""
        rcd = snap.get("cache_d") or ""
        caches_four = (_slot(rca), _slot(rcb), _slot(rcc), _slot(rcd))
        if "nocache" in snap:
            nocache_content = snap.get("nocache") or None

    if debug:
        dbg = get_logger(__name__, debug_flag=True)
        source = (chain_context or {}).get("_caller_hydration_source") or (
            "live_llm" if (chain_context or {}).get("_hop_parent_task_key") else "chain_entry"
        )
        dbg.debug_detail(
            f"token_overlay chain_entry={chain_entry} caller_source={source} "
            f"parent={(chain_context or {}).get('_hop_parent_task_key') or 'none'} "
            f"caller_keys={_caller_key_status(_cc)}"
        )
        if source == "agent_data":
            dbg.debug_detail(
                f"caller_hydration=agent_data upstream={(chain_context or {}).get('_hop_parent_task_key')}"
            )
        if _jc:
            populated = [k for k, v in _jc.items() if (v or "").strip()]
            dbg.debug_detail(f"job_context tokens={','.join(populated) if populated else 'none'}")

    if not chain_entry:
        segment_texts = {
            "system": (agent_task_row.get("system_prompt") or "").strip() or (agent_row.get("content") or ""),
            "user": agent_task_row.get("user_prompt") or "",
            "cache_a": agent_task_row.get("cache_prompt") or "",
            "cache_b": agent_task_row.get("cache_prompt_b") or "",
            "cache_c": agent_task_row.get("cache_prompt_c") or "",
            "cache_d": agent_task_row.get("cache_prompt_d") or "",
            "nocache": agent_task_row.get("nocache_prompt") or "",
            "live": live_content or "",
            "system_resolved": system_content or "",
            "user_resolved": user_content or "",
            "cache_a_resolved": rca or "",
            "cache_b_resolved": rcb or "",
            "cache_c_resolved": rcc or "",
            "cache_d_resolved": rcd or "",
            "nocache_resolved": nocache_content or "",
        }
        guard_err = _mid_chain_empty_caller_tokens(
            callee_task_key=task_key,
            parent_task_key=parent_task_key or "",
            chain_context=_cc,
            segment_texts=segment_texts,
        )
        if guard_err:
            logger.warning(
                "do_task(%s): %s caller_keys=%s",
                task_key,
                guard_err,
                _caller_key_status(_cc),
            )
            if debug:
                get_logger(__name__, debug_flag=True).debug_detail(
                    f"token_guard blocked: {guard_err} caller_keys={_caller_key_status(_cc)}"
                )
            return {
                "success": False,
                "error": guard_err,
                "api_response": None,
                "parsed_response": None,
                "timesheet": {},
            }

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
                "do_task(%s): run_next chain hop without astral_candidate_id — no hop ledger",
                task_key,
            )
    batch_id = hop_ledger_batch_id or log_batch_id.get()
    if chain_entry:
        _log_chain_entry(task_key, batch_id)

    if debug:
        logger.set_debug_flag(True)
    _do_task_debug_entry(
        task_key=task_key,
        index=index,
        batch_id=batch_id,
        in_chain=in_chain,
        debug=debug,
    )

    def _close_hop_ledger(*, success: bool, clear_log: bool = False) -> None:
        nonlocal hop_ledger_closed
        if hop_ledger_closed or not hop_ledger_batch_id:
            return
        _finalize_run_next_hop_ledger(
            hop_ledger_batch_id, success=success, batch_size=batch_size
        )
        hop_ledger_closed = True
        if clear_log:
            log_batch_id.set(None)

    assemble_model_tag = resolved_anthropic_key if provider == "anthropic" else tier_meta["vendor_model"]

    system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens = _assemble_blocks_seven_segment(
        system_content=system_content,
        user_content=user_content,
        caches_resolved_four=caches_four,
        nocache_content=nocache_content,
        live_content=live_content,
        model_code=assemble_model_tag,
        skip_cache=skip_cache,
    )

    if debug:
        dbg = get_logger(__name__, debug_flag=True)
        model_tag = resolved_anthropic_key if provider == "anthropic" else tier_meta["vendor_model"]
        dbg.debug_detail(
            f"llm_params provider={provider} brain_setting={brain_setting} model={model_tag} "
            f"max_tokens={agent_max_tokens} temp={agent_temperature} skip_cache={skip_cache} "
            f"candidate_id={candidate_id or ''}"
        )
        dbg.debug_detail(
            f"blocks system={len(system_blocks)} user={len(user_blocks)} "
            f"runtime_prompt_segments={len(runtime_prompt)}"
        )

    if provider == "anthropic":
        result = await send_to_anthropic(
            user_blocks,
            system_blocks=system_blocks,
            response_format=response_format,
            prompt_label=task_key,
            candidate_id=candidate_id,
            api_key_override=api_key_override,
            model_code=resolved_anthropic_key,
            temperature=agent_temperature,
            max_tokens=agent_max_tokens,
            debug=debug,
            task_key_uuid=agent_task_row.get("task_key_uuid"),
            no_cache_prompt_tokens=no_cache_prompt_tokens,
            no_cache_live_tokens=no_cache_live_tokens,
            batch_size=batch_size,
            record_timesheet=record_timesheet_entry,
        )
    else:
        result = await send_to_deepseek(
            user_blocks,
            system_blocks=system_blocks,
            response_format=response_format,
            prompt_label=task_key,
            candidate_id=candidate_id,
            api_key_override=api_key_override,
            vendor_model=tier_meta["vendor_model"],
            tier_meta=tier_meta,
            temperature=agent_temperature,
            max_tokens=agent_max_tokens,
            debug=debug,
            task_key_uuid=agent_task_row.get("task_key_uuid"),
            no_cache_prompt_tokens=no_cache_prompt_tokens,
            no_cache_live_tokens=no_cache_live_tokens,
            batch_size=batch_size,
            record_timesheet=record_timesheet_entry,
        )
    result["runtime_prompt"] = runtime_prompt

    if batch_id and not result.get("success"):
        logger.error(
            "do_task(%s) provider call failed batch_id=%s error=%s",
            task_key,
            batch_id,
            result.get("error"),
        )

    # Store prompt blocks in agent_data (non-blocking; best-effort)
    prompt_blocks: List[Dict[str, str]] = []
    _should_store = store_agent_data and batch_id and entity_type
    if _should_store:
        try:
            prompt_blocks = _store_prompt_blocks(
                entity_type=entity_type,
                task_key=task_key,
                batch_id=batch_id,
                system_content=system_content,
                caches_resolved_four=(rca or "", rcb or "", rcc or "", rcd or ""),
                nocache_content=nocache_content,
                user_content=user_content,
                live_content=live_content,
            )
        except Exception:
            logger.debug("_store_prompt_blocks failed", exc_info=True)

    if not result.get("success"):
        raw_for_audit = None
        api_resp = result.get("api_response")
        if api_resp:
            try:
                raw_for_audit = extract_api_response_text(api_resp)
            except ValueError:
                pass
        audit_body = _audit_response_body(
            raw_for_audit,
            parsed=result.get("parsed_response"),
            err=result.get("error"),
        )
        if _should_store:
            try:
                _store_response_block(
                    entity_type, task_key, batch_id, _failure_response_block_data(index, audit_body), index=index
                )
            except Exception:
                logger.debug("_store_response_block (API failure) failed", exc_info=True)
        _store_agent_response(
            task_config,
            task_key,
            index,
            raw_for_audit or result.get("error") or audit_body,
            None,
            result,
        )
        if debug:
            get_logger(__name__, debug_flag=True).debug_detail(
                f"exit provider_failed task_key={task_key} batch_id={batch_id or ''} "
                f"error={result.get('error')!r}"
            )
        _close_hop_ledger(success=False, clear_log=True)
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
    if debug and raw_text and len(raw_text.splitlines()) > 50:
        get_logger(__name__, debug_flag=True).debug_detail(
            f"raw_response task_key={task_key} lines={len(raw_text.splitlines())} chars={len(raw_text)}"
        )
        get_logger(__name__, debug_flag=True).debug_detail_block(raw_text)

    parsed = result.get("parsed_response")
    output_type = task_config.get("output_type", "")
    rubric_encoded = "_encoded" in output_type and bool(task_config.get("rubric_artifact"))
    strict_batch = task_key in _STRICT_ENCODED_BATCH_CONSULT_KEYS
    if strict_batch and isinstance(parsed, dict) and parsed.get("agent_payload") is not None and parsed.get("agent_performance") is None:
        parsed = {**parsed, "agent_performance": {}}
        result["parsed_response"] = parsed
    envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed) if strict_batch else None
    if not envelope_err and "_encoded" in output_type:
        parsed = coerce_grades_encoded_json_parse(parsed, raw_text or "")
        result["parsed_response"] = parsed
    if strict_batch and not envelope_err:
        envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed)

    if envelope_err:
        logger.error(
            "do_task strict envelope failed. task_key=%r batch_id=%r error=%s",
            task_key,
            batch_id,
            envelope_err,
        )
        _store_agent_response(task_config, task_key, index, parsed, None, result)
        if _should_store:
            try:
                _store_response_block(
                    entity_type,
                    task_key,
                    batch_id,
                    _failure_response_block_data(index, _audit_response_body(raw_text, parsed, envelope_err)),
                    index=index,
                )
            except Exception:
                logger.debug("_store_response_block failed", exc_info=True)
        _close_hop_ledger(success=False, clear_log=True)
        return {"success": False, "api_response": result.get("api_response"),
                "parsed_response": None, "error": envelope_err, "raw_response": parsed,
                "timesheet": result.get("timesheet", {})}

    if parsed is not None and response_format in ("json", "python") and not rubric_encoded:
        if isinstance(parsed, dict) and schema:
            if task_key == "craft_resume_base":
                from src.core.candidate import normalize_craft_resume_base_agent_payload

                normalize_craft_resume_base_agent_payload(parsed)
            if task_key == "draft_job_resume":
                from src.core.candidate import normalize_draft_job_resume_agent_payload

                normalize_draft_job_resume_agent_payload(parsed)
            _coerce_schema_str_fields_from_list(parsed, schema)
        err = _validate_response_schema(parsed, schema, task_key)
        if err:
            logger.error("do_task validation failed. task_key=%r error=%s", task_key, err)
            if log_batch_id.get():
                flush_log_buffer()
            _store_agent_response(task_config, task_key, index, parsed, None, result)
            if _should_store:
                try:
                    _store_response_block(
                        entity_type,
                        task_key,
                        batch_id,
                        _failure_response_block_data(index, _validation_failure_audit_body(err, raw_text, parsed)),
                        index=index,
                    )
                except Exception:
                    logger.debug("_store_response_block failed", exc_info=True)
            _close_hop_ledger(success=False, clear_log=True)
            return {"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                    "error": err, "raw_response": parsed, "timesheet": result.get("timesheet", {})}

        if task_config.get("resume_section_payload") and cd:
            from src.core.candidate import validate_draft_job_resume_payload

            cat_err = validate_draft_job_resume_payload(parsed, cd)
            if cat_err:
                logger.error("do_task validation failed. task_key=%r error=%s", task_key, cat_err)
                if log_batch_id.get():
                    flush_log_buffer()
                _store_agent_response(task_config, task_key, index, parsed, None, result)
                if _should_store:
                    try:
                        _store_response_block(
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(
                                index, _validation_failure_audit_body(cat_err, raw_text, parsed)
                            ),
                            index=index,
                        )
                    except Exception:
                        logger.debug("_store_response_block failed", exc_info=True)
                _close_hop_ledger(success=False, clear_log=True)
                return {"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                        "error": cat_err, "raw_response": parsed, "timesheet": result.get("timesheet", {})}

        inner_payload = _inner_task_payload(parsed)
        if isinstance(inner_payload, dict):
            conf_err = _validate_grade_confidence_in_payload(inner_payload, task_key)
            if conf_err:
                logger.error("do_task confidence validation failed. task_key=%r error=%s", task_key, conf_err)
                _store_agent_response(task_config, task_key, index, parsed, None, result)
                if _should_store:
                    try:
                        _store_response_block(
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(index, _audit_response_body(raw_text, parsed, conf_err)),
                            index=index,
                        )
                    except Exception:
                        logger.debug("_store_response_block failed", exc_info=True)
                _close_hop_ledger(success=False, clear_log=True)
                return {"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                        "error": conf_err, "raw_response": parsed, "timesheet": result.get("timesheet", {})}

        vectors = task_config.get("vectors")
        # AST-594: draft_job_resume is structure-keyed, not graded-consult.
        if vectors and task_key != "draft_job_resume" and isinstance(inner_payload, dict):
            grades = inner_payload.get("grades")
            if grades and isinstance(grades, list):
                grade_err = _validate_grades(grades, vectors)
                if grade_err:
                    logger.error("do_task grade validation failed. task_key=%r error=%s", task_key, grade_err)
                    _store_agent_response(task_config, task_key, index, parsed, None, result)
                    if _should_store:
                        try:
                            _store_response_block(
                                entity_type,
                                task_key,
                                batch_id,
                                _failure_response_block_data(index, _audit_response_body(raw_text, parsed, grade_err)),
                                index=index,
                            )
                        except Exception:
                            logger.debug("_store_response_block failed", exc_info=True)
                    _close_hop_ledger(success=False, clear_log=True)
                    return {"success": False, "api_response": result.get("api_response"), "parsed_response": None,
                            "error": grade_err, "raw_response": parsed, "timesheet": result.get("timesheet", {})}

    if isinstance(parsed, dict) and "agent_payload" in parsed:
        parsed = parsed["agent_payload"]
        # Model occasionally wraps lines in a list instead of joining with \n — normalize it
        if isinstance(parsed, list):
            parsed = "\n".join(str(item) for item in parsed)
        result["parsed_response"] = parsed

    output_type = task_config.get("output_type", "")
    if debug and "_encoded" in output_type:
        literal = parsed if isinstance(parsed, str) else raw_text
        if isinstance(literal, str) and literal.strip():
            dbg = get_logger(__name__, debug_flag=True)
            lines = [ln for ln in literal.splitlines() if ln.strip()]
            dbg.debug_detail(
                f"encoded_payload task_key={task_key} lines={len(lines)} chars={len(literal)}"
            )
            dbg.debug_detail_block(literal)

    # For encoded output types: normalize rubric shapes or decode compact string, then validate.
    post_rubric_decode = False
    if rubric_encoded and parsed is not None:
        try:
            from src.core.consult import _normalize_rubric_task_response

            parsed = _normalize_rubric_task_response(task_key, task_config, parsed, ctx or {})
            result["parsed_response"] = parsed
            post_rubric_decode = True
        except Exception as exc:
            logger.error("do_task normalize failed. task_key=%r error=%s", task_key, exc)
            if _should_store:
                try:
                    body = _audit_response_body(raw_text, None, str(exc))
                    if isinstance(parsed, str) and parsed.strip():
                        body = f"{body}\n--- agent_payload ---\n{parsed}"
                    _store_response_block(
                        entity_type, task_key, batch_id, _failure_response_block_data(index, body), index=index
                    )
                except Exception:
                    logger.debug("_store_response_block failed", exc_info=True)
            _close_hop_ledger(success=False, clear_log=True)
            return {"success": False, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": str(exc), "timesheet": result.get("timesheet", {})}
    elif "_encoded" in output_type and isinstance(parsed, str):
        try:
            parsed = _decode_payload(task_key, output_type, parsed, ctx or {})
            result["parsed_response"] = parsed
            post_rubric_decode = True
        except Exception as exc:
            logger.error("do_task decode failed. task_key=%r error=%s", task_key, exc)
            if logger.isEnabledFor(_LOG_DEBUG):
                snippet = (parsed or "")[:500] if isinstance(parsed, str) else repr(parsed)[:500]
                logger.debug("do_task decode failed payload snippet task_key=%r snippet=%r", task_key, snippet)
            if _should_store:
                try:
                    body = _audit_response_body(raw_text, None, str(exc))
                    # parsed is still the agent_payload string that failed decode
                    if isinstance(parsed, str) and parsed.strip():
                        body = f"{body}\n--- agent_payload ---\n{parsed}"
                    _store_response_block(
                        entity_type, task_key, batch_id, _failure_response_block_data(index, body), index=index
                    )
                except Exception:
                    logger.debug("_store_response_block failed", exc_info=True)
            _close_hop_ledger(success=False, clear_log=True)
            return {"success": False, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": str(exc), "timesheet": result.get("timesheet", {})}
    if post_rubric_decode:
        if isinstance(parsed, dict) and schema:
            if task_key == "craft_resume_base":
                from src.core.candidate import normalize_craft_resume_base_agent_payload

                normalize_craft_resume_base_agent_payload(parsed)
            if task_key == "draft_job_resume":
                from src.core.candidate import normalize_draft_job_resume_agent_payload

                normalize_draft_job_resume_agent_payload(parsed)
            _coerce_schema_str_fields_from_list(parsed, schema)
        err = _validate_response_schema(parsed, schema, task_key)
        if err:
            logger.error("do_task schema validation failed after decode. task_key=%r error=%s", task_key, err)
            if log_batch_id.get():
                flush_log_buffer()
            if _should_store:
                try:
                    _store_response_block(
                        entity_type,
                        task_key,
                        batch_id,
                        _failure_response_block_data(index, _validation_failure_audit_body(err, raw_text, parsed)),
                        index=index,
                    )
                except Exception:
                    logger.debug("_store_response_block failed", exc_info=True)
            _close_hop_ledger(success=False, clear_log=True)
            return {"success": False, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": err, "timesheet": result.get("timesheet", {})}
        if task_config.get("resume_section_payload") and cd:
            from src.core.candidate import validate_draft_job_resume_payload

            cat_err = validate_draft_job_resume_payload(parsed, cd)
            if cat_err:
                logger.error("do_task validation failed after decode. task_key=%r error=%s", task_key, cat_err)
                if log_batch_id.get():
                    flush_log_buffer()
                if _should_store:
                    try:
                        _store_response_block(
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(
                                index, _validation_failure_audit_body(cat_err, raw_text, parsed)
                            ),
                            index=index,
                        )
                    except Exception:
                        logger.debug("_store_response_block failed", exc_info=True)
                _close_hop_ledger(success=False, clear_log=True)
                return {"success": False, "api_response": result.get("api_response"),
                        "parsed_response": None, "error": cat_err, "timesheet": result.get("timesheet", {})}
        if isinstance(parsed, dict):
            conf_err = _validate_grade_confidence_in_payload(parsed, task_key)
            if conf_err:
                logger.error("do_task confidence validation failed after decode. task_key=%r error=%s", task_key, conf_err)
                if _should_store:
                    try:
                        _store_response_block(
                            entity_type,
                            task_key,
                            batch_id,
                            _failure_response_block_data(index, _audit_response_body(raw_text, parsed, conf_err)),
                            index=index,
                        )
                    except Exception:
                        logger.debug("_store_response_block failed", exc_info=True)
                _close_hop_ledger(success=False, clear_log=True)
                return {"success": False, "api_response": result.get("api_response"),
                        "parsed_response": None, "error": conf_err, "timesheet": result.get("timesheet", {})}

    # SUCCESS: store decoded/validated response block, then build agent_ref
    if _should_store and raw_text:
        try:
            store_content = json.dumps(parsed) if isinstance(parsed, (dict, list)) else (parsed or raw_text)
            resp_id = _store_response_block(entity_type, task_key, batch_id, store_content, index=index)
            prompt_blocks.append({"type": "RESPONSE", "id": resp_id})
        except Exception:
            logger.debug("_store_response_block failed", exc_info=True)

    # Build lightweight ref entry for entity's agent_responses array
    if _should_store:
        try:
            total_cost = compute_batch_cost(batch_id)
            entity_cost = total_cost / batch_size if batch_size > 0 else total_cost
            agent_ref = {
                "batch_id": batch_id,
                "task_key": task_key,
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "entity_cost": round(entity_cost, 7),
                "prompt_blocks": prompt_blocks,
            }
            result["agent_ref"] = agent_ref
            # For single-entity tasks, store directly; batch callers handle their own
            if index and entity_type:
                append_agent_response(entity_type, index, agent_ref)
        except Exception:
            logger.debug("append_agent_response failed", exc_info=True)

    _store_agent_response(task_config, task_key, index, parsed, parsed, result)

    if result.get("success") and entity_type == "job" and index:
        _maybe_transition_resume_hop_progress(task_key, index)

    planned_next = (agent_task_row.get("run_next") or "").strip()
    effective_next = planned_next
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
        except Exception:
            logger.exception("resolve_run_next_live(%s) failed", task_key)
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
        if (
            result.get("success")
            and entity_type == "job"
            and index
            and isinstance(parsed, dict)
        ):
            # Lazy import breaks agent↔tracker cycle (consult imports agent).
            from src.core.tracker import persist_job_artifact_from_parsed
            allow_resume = task_key == "finalize_job_resume"
            allow_cover = task_key == "finalize_cover_letter"
            if allow_resume or allow_cover:
                persist_job_artifact_from_parsed(
                    index,
                    parsed,
                    allow_resume=allow_resume,
                    allow_cover_letter=allow_cover,
                )
        if batch_id:
            logger.info(
                "do_task(%s) completed successfully batch_id=%s index=%s",
                task_key,
                batch_id,
                index,
            )
        if debug:
            dbg = get_logger(__name__, debug_flag=True)
            dbg.debug_index(
                func="do_task",
                index=1,
                total=1,
                identifier=(index or task_key or "?"),
                outcome="completed",
            )
            dbg.debug_detail(
                f"task_key={task_key} batch_id={batch_id or ''} success={result.get('success')}"
            )
        _close_hop_ledger(success=True, clear_log=True)
        return result
    if effective_next not in TASK_CONFIG:
        logger.warning(
            "do_task(%s): run_next=%r is not a TASK_CONFIG key — returning this hop only",
            task_key,
            effective_next,
        )
        if debug:
            get_logger(__name__, debug_flag=True).debug_detail(
                f"run_next suppressed invalid_child={effective_next!r} parent={task_key}"
            )
        _close_hop_ledger(success=True, clear_log=True)
        return result

    _close_hop_ledger(success=True, clear_log=True)
    merged_ctx = _merge_chain_context_for_next_hop(chain_context, hop_ctx)
    merged_ctx["_hop_parent_task_key"] = task_key
    if debug:
        dbg = get_logger(__name__, debug_flag=True)
        dbg.debug_detail(
            f"run_next dispatch parent={task_key} child={effective_next} "
            f"batch_id={batch_id or ''} caller_keys={_caller_key_status(hop_ctx)}"
        )
        dbg.debug_detail(f"caller_hydration=live_llm parent={task_key}")
    _log_run_next_hop_boundary(
        parent_task_key=task_key,
        child_task_key=effective_next,
        batch_id=batch_id,
        hop_ctx=hop_ctx,
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
    _cc = _chain_context(agent_row)
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
    _cc = _chain_context(agent_row, chain_context)
    system_out = resolved_task_system(agent_row, agent_task_row, cd, task_key, _cc, job_context)
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
    hop_batch_id = f"{task_key}-{uuid.uuid4()}"
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

async def run_adhoc_workbench_test(
    workbench_task_key: str,
    candidate_id: str,
    entity_id: Optional[str] = None,
    system_content: str = "",
    user_content: str = "",
    cache_content: Optional[str] = None,
    nocache_content: Optional[str] = None,
    live_content: Optional[str] = None,
    model_code: Optional[str] = None,
    *,
    tier_meta: Optional[Dict[str, Any]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[str] = "text",
    context: Optional[str] = None,
    api_key_override: Optional[str] = None,
    task_key_uuid: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Wrap run_adhoc with dispatch_ledger, log_batch_id, and agent_data for workbench Test."""
    ledger_task_key = f"adhoc-{workbench_task_key}"
    batch_id = f"{ledger_task_key}-{uuid.uuid4()}"
    entity_type = (TASK_CONFIG.get(workbench_task_key) or {}).get("entity_type") or "candidate"
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
    logger.info(
        "adhoc workbench test started task_key=%r batch_id=%s candidate_id=%s",
        workbench_task_key,
        batch_id,
        candidate_id,
    )
    result: Dict[str, Any]
    try:
        try:
            result = await run_adhoc(
                system_content=system_content,
                user_content=user_content,
                cache_content=cache_content,
                nocache_content=nocache_content,
                live_content=live_content,
                model_code=model_code,
                tier_meta=tier_meta,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                context=context,
                candidate_id=candidate_id,
                api_key_override=api_key_override,
                task_key_uuid=task_key_uuid,
                debug=debug,
            )
        except Exception:
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=started_at,
                total_processed=1,
                total_failed=0,
                total_errors=1,
            )
            raise

        try:
            _store_prompt_blocks(
                entity_type=entity_type,
                task_key=workbench_task_key,
                batch_id=batch_id,
                system_content=system_content,
                cache_content=cache_content or None,
                nocache_content=nocache_content,
                user_content=user_content,
                live_content=live_content,
            )
        except Exception:
            logger.debug("_store_prompt_blocks failed", exc_info=True)

        if not result.get("success"):
            err = result.get("error", "Ad hoc test failed")
            logger.error(
                "adhoc workbench test failed task_key=%r batch_id=%s error=%s",
                workbench_task_key,
                batch_id,
                err,
            )
            raw_for_audit = None
            api_resp = result.get("api_response")
            if api_resp:
                try:
                    raw_for_audit = extract_api_response_text(api_resp)
                except ValueError:
                    pass
            audit_body = _audit_response_body(
                raw_for_audit,
                parsed=result.get("parsed_response"),
                err=result.get("error"),
            )
            try:
                _store_response_block(
                    entity_type,
                    workbench_task_key,
                    batch_id,
                    _failure_response_block_data(entity_id, audit_body),
                    index=entity_id,
                )
            except Exception:
                logger.debug("_store_response_block (API failure) failed", exc_info=True)
        else:
            parsed = result.get("parsed_response")
            if isinstance(parsed, dict) and "agent_payload" in parsed:
                response_text = parsed["agent_payload"] or ""
            else:
                response_text = str(parsed) if parsed is not None else ""
            try:
                _store_response_block(
                    entity_type,
                    workbench_task_key,
                    batch_id,
                    response_text,
                    index=entity_id,
                )
            except Exception:
                logger.debug("_store_response_block failed", exc_info=True)

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
        logger.info(
            "adhoc workbench test finished task_key=%r batch_id=%s success=%s cost=%s",
            workbench_task_key,
            batch_id,
            bool(result.get("success")),
            total_cost,
        )
        return result
    finally:
        flush_log_buffer()
        log_batch_id.set(None)


async def run_adhoc(
    system_content: str,
    user_content: str,
    cache_content: Optional[str] = None,
    nocache_content: Optional[str] = None,
    live_content: Optional[str] = None,
    model_code: Optional[str] = None,
    *,
    tier_meta: Optional[Dict[str, Any]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[str] = "text",
    context: Optional[str] = None,
    candidate_id: Optional[str] = None,
    api_key_override: Optional[str] = None,
    task_key_uuid: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Run an ad-hoc prompt without DB prompt resolution or agent_data storage.
    Uses candidate's API key when available, falls back to system key."""
    if not model_code:
        raise ValueError("run_adhoc requires model_code (Anthropic AGENT_CONFIG key or DeepSeek vendor_model)")

    system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens = _assemble_blocks(
        system_content=system_content,
        user_content=user_content,
        cache_content=cache_content,
        nocache_content=nocache_content,
        live_content=live_content,
        model_code=model_code,
        skip_cache=False,
    )

    if tier_meta is not None:
        result = await send_to_deepseek(
            user_blocks,
            system_blocks=system_blocks,
            response_format=response_format,
            prompt_label="adhoc",
            vendor_model=model_code,
            tier_meta=tier_meta,
            temperature=temperature,
            max_tokens=max_tokens,
            candidate_id=candidate_id,
            api_key_override=api_key_override,
            task_key_uuid=task_key_uuid,
            debug=debug,
            no_cache_prompt_tokens=no_cache_prompt_tokens,
            no_cache_live_tokens=no_cache_live_tokens,
            record_timesheet=record_timesheet_entry,
        )
    else:
        result = await send_to_anthropic(
            user_blocks,
            system_blocks=system_blocks,
            response_format=response_format,
            prompt_label="adhoc",
            model_code=model_code,
            temperature=temperature,
            max_tokens=max_tokens,
            candidate_id=candidate_id,
            api_key_override=api_key_override,
            task_key_uuid=task_key_uuid,
            debug=debug,
            no_cache_prompt_tokens=no_cache_prompt_tokens,
            no_cache_live_tokens=no_cache_live_tokens,
            record_timesheet=record_timesheet_entry,
        )
    result["runtime_prompt"] = runtime_prompt
    return result


# ---------------------------------------------------------------------------
# get_agent_data — retrieve stored blocks for a batch
# ---------------------------------------------------------------------------

def get_agent_data(
    batch_id: str,
    block_type: Optional[str] = None,
    entity_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve agent_data blocks for a batch.
    When entity_id is provided and block_type is TASK or RESPONSE (or unset),
    parses the block_data content to extract the element for that entity.
    Assumes batch responses embed per-entity sections identifiable by entity_id."""
    rows = get_agent_data_by_batch(batch_id, block_type)
    if not entity_id:
        return rows

    result = []
    for row in rows:
        bt = row.get("block_type")
        if bt not in ("TASK", "RESPONSE"):
            result.append(row)
            continue
        # Extract entity-specific segment from the block content
        content = row.get("block_data") or ""
        segment = _extract_entity_segment(content, entity_id)
        if segment is not None:
            row = dict(row)
            row["block_data"] = segment
        result.append(row)
    return result


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
    Tries JSON first (looks for entity_id key in a 'jobs' list or top-level dict).
    Falls back to None (caller keeps full content)."""
    if not content or not entity_id:
        return None
    try:
        data = json.loads(content)
        # Batch responses are typically {"jobs": [{astral_job_id: ..., ...}, ...]}
        if isinstance(data, dict):
            jobs = data.get("jobs") or data.get("results") or data.get("entities")
            if isinstance(jobs, list):
                for item in jobs:
                    if isinstance(item, dict) and item.get("astral_job_id") == entity_id:
                        return json.dumps(item)
            # Flat single-entity response
            if data.get("astral_job_id") == entity_id or len(data) > 0:
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
