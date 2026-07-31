# -*- coding: utf-8 -*-
"""
Candidate intake orchestration (mechanical preamble validation + Estelle multi-turn sessions).

Layer: core → data, agent, candidate, utils  (never ← ui)
"""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.agent import compute_batch_cost, do_task, get_agent_data_by_batch
from src.core.candidate import (
    check_context_complete,
    get_candidate,
    get_topic_menu,
    mark_topic_menu_preamble_confirmed,
    save_candidate_data,
    save_topic_menu,
    sync_company_search_terms_from_text,
    validate_topic,
)
from src.data import database
from src.utils.config import INTAKE_CONFIG, PREAMBLE_VALIDATION_CONFIG, TOPIC_MENU_CONFIG, TOPIC_MENU_GEN_CONFIG
from src.utils.logging import flush_log_buffer, get_logger, log_batch_id, truncate_debug_content

logger = get_logger(__name__)



async def validate_preamble_answer(
    candidate_id: str,
    question: str,
    answer: str,
    *,
    step_index: int = 1,
    step_total: int = 1,
    debug: bool = False,
) -> dict:
    """Ruth Valid / Try Again / Escalate for one preamble Q/A. Never writes library fields."""
    task_key = PREAMBLE_VALIDATION_CONFIG["task_key"]
    q = (question or "").strip()
    a = (answer or "").strip()
    if not q:
        raise ValueError("question required")

    candidate = get_candidate(candidate_id)
    if not candidate:
        raise ValueError(f"Candidate not found: {candidate_id}")

    live_content = f"QUESTION:\n{q}\n\nANSWER:\n{a}"
    batch_id = f"preamble-{task_key}-{uuid.uuid4()}"
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    database.save_dispatch_ledger(
        batch_id,
        f"preamble-{task_key}",
        candidate_id,
        started_at,
        entity_type="candidate",
        batch_size=1,
    )
    log_batch_id.set(batch_id)
    outcome = None
    err = None
    success = False
    try:
        result = await do_task(
            task_key=task_key,
            live_content=live_content,
            index=candidate_id,
            ctx=candidate,
            debug=debug,
        )
        completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if not result or not result.get("success"):
            err = result.get("error", "preamble validation failed") if result else "do_task returned None"
            total_cost = compute_batch_cost(batch_id)
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=completed_at,
                total_processed=1,
                total_failed=1,
                total_cost=total_cost,
            )
        else:
            parsed = result.get("parsed_response")
            raw = parsed.get(PREAMBLE_VALIDATION_CONFIG["outcome_field"]) if isinstance(parsed, dict) else None
            if raw not in PREAMBLE_VALIDATION_CONFIG["outcomes"]:
                err = f"invalid preamble validation outcome: {raw!r}"
                total_cost = compute_batch_cost(batch_id)
                database.update_dispatch_ledger(
                    batch_id,
                    status="FAILED",
                    completed_at=completed_at,
                    total_processed=1,
                    total_failed=1,
                    total_cost=total_cost,
                )
            else:
                outcome = raw
                success = True
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
            dbg_outcome = f"found|{outcome}" if success else "found|error"
            logger.set_debug_flag(True)
            logger.debug_index(
                func="validate_preamble_answer",
                index=step_index,
                total=step_total,
                identifier=candidate_id,
                outcome=dbg_outcome,
            )
            logger.debug_detail(f"question={truncate_debug_content(q)!r}")
            logger.debug_detail(f"answer={truncate_debug_content(a)!r}")
            if err:
                logger.debug_detail(f"error={err}")
        return {"success": success, "outcome": outcome, "error": err, "batch_id": batch_id}
    finally:
        flush_log_buffer()
        log_batch_id.set(None)


def build_preamble_packet_snapshot(candidate_id: str) -> dict:
    """Snapshot name columns + context/contact packet fields for Estelle (AST-1075)."""
    candidate = get_candidate(candidate_id)
    if not candidate:
        raise ValueError(f"Candidate not found: {candidate_id}")
    cd = candidate.get("candidate_data") or {}
    if not isinstance(cd, dict):
        cd = {}
    context = cd.get("context") if isinstance(cd.get("context"), dict) else {}
    contact = cd.get("contact") if isinstance(cd.get("contact"), dict) else {}
    snapshot = {
        "name": {
            k: str(candidate.get(k) or "")
            for k in TOPIC_MENU_GEN_CONFIG["packet_name_columns"]
        },
        "context": {
            k: str(context.get(k) or "")
            for k in TOPIC_MENU_GEN_CONFIG["packet_context_keys"]
        },
        "contact": {
            k: str(contact.get(k) or "")
            for k in TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]
        },
    }
    if not snapshot["context"]["raw_resume"].strip():
        raise ValueError("preamble packet incomplete: raw_resume required")
    return snapshot


def _apply_library_patches(candidate_id: str, patches: Any, *, debug: bool = False) -> list:
    """Apply Estelle context patches; whitelist only; non-empty strings only."""
    if not isinstance(patches, dict):
        return []
    ctx = patches.get("context")
    if not isinstance(ctx, dict):
        return []
    allowed = TOPIC_MENU_GEN_CONFIG["patchable_context_keys"]
    applied: dict = {}
    for key, val in ctx.items():
        if key not in allowed:
            continue
        if not isinstance(val, str) or not val.strip():
            continue
        applied[key] = val.strip()
    if not applied:
        return []
    save_candidate_data(candidate_id, {"context": applied}, debug=debug)
    return list(applied.keys())


async def run_topic_menu_preamble_confirm(
    candidate_id: str,
    candidate_message: Optional[str] = None,
    *,
    debug: bool = False,
) -> dict:
    """Estelle confirm turn; stamps preamble_confirmed_at on outcome=accepted."""
    packet = build_preamble_packet_snapshot(candidate_id)
    live_content = json.dumps(
        {
            "PREAMBLE_PACKET": packet,
            "CANDIDATE_MESSAGE": (candidate_message or "").strip(),
        }
    )
    task_key = TOPIC_MENU_GEN_CONFIG["confirm_task_key"]
    run = await _run_intake_task(
        candidate_id,
        task_key,
        live_content,
        prompt_snapshot=None,
        debug=debug,
    )
    if not run.get("success"):
        return {
            "success": False,
            "error": run.get("error") or "confirm failed",
            "batch_id": run.get("batch_id"),
            "outcome": None,
            "assistant_message": None,
            "applied_patches": [],
            "packet": packet,
        }

    parsed = run.get("parsed_response")
    if not isinstance(parsed, dict):
        return {
            "success": False,
            "error": "confirm response must be a JSON object",
            "batch_id": run.get("batch_id"),
            "outcome": None,
            "assistant_message": None,
            "applied_patches": [],
            "packet": packet,
        }
    msg = (parsed.get("assistant_message") or "").strip()
    if not msg:
        return {
            "success": False,
            "error": "assistant_message is required",
            "batch_id": run.get("batch_id"),
            "outcome": None,
            "assistant_message": None,
            "applied_patches": [],
            "packet": packet,
        }
    outcome = parsed.get(TOPIC_MENU_GEN_CONFIG["confirm_outcome_field"])
    if outcome not in TOPIC_MENU_GEN_CONFIG["confirm_outcomes"]:
        return {
            "success": False,
            "error": f"invalid confirm outcome: {outcome!r}",
            "batch_id": run.get("batch_id"),
            "outcome": None,
            "assistant_message": None,
            "applied_patches": [],
            "packet": packet,
        }

    applied = _apply_library_patches(
        candidate_id, parsed.get("library_patches"), debug=debug
    )
    if outcome == "accepted":
        mark_topic_menu_preamble_confirmed(candidate_id, debug=debug)

    if debug:
        logger.set_debug_flag(True)
        logger.debug_index(
            func="run_topic_menu_preamble_confirm",
            index=1,
            total=2,
            identifier=candidate_id,
            outcome=f"found|{outcome}",
        )
        logger.debug_detail(f"assistant_message={truncate_debug_content(msg)!r}")
        logger.debug_detail(f"applied_patches={applied}")
        logger.debug_index(
            func="run_topic_menu_preamble_confirm",
            index=2,
            total=2,
            identifier=candidate_id,
            outcome="recorded",
        )
        logger.debug_detail(f"accepted={outcome == 'accepted'}")

    # Re-read packet so UI sees post-patch library.
    packet_out = build_preamble_packet_snapshot(candidate_id)
    return {
        "success": True,
        "outcome": outcome,
        "assistant_message": msg,
        "applied_patches": applied,
        "batch_id": run.get("batch_id"),
        "error": None,
        "packet": packet_out,
    }


async def generate_topic_menu_from_preamble(candidate_id: str, *, debug: bool = False) -> dict:
    """Pure-Estelle Topic Menu generation; save via revise=True (AST-1075)."""
    current = get_topic_menu(candidate_id)
    if not current.get("preamble_confirmed_at"):
        raise ValueError("preamble not confirmed; run confirm accept first")

    packet = build_preamble_packet_snapshot(candidate_id)
    live_content = json.dumps(
        {
            "PREAMBLE_PACKET": packet,
            "INFORMS_CATALOG": list(TOPIC_MENU_CONFIG["informs"]),
        }
    )
    task_key = TOPIC_MENU_GEN_CONFIG["generate_task_key"]
    run = await _run_intake_task(
        candidate_id,
        task_key,
        live_content,
        prompt_snapshot=None,
        debug=debug,
    )
    if not run.get("success"):
        return {
            "success": False,
            "error": run.get("error") or "generate failed",
            "batch_id": run.get("batch_id"),
            "menu": None,
            "rejected_topic_count": 0,
            "informs_covered": [],
        }

    parsed = run.get("parsed_response")
    if not isinstance(parsed, dict):
        return {
            "success": False,
            "error": "generate response must be a JSON object",
            "batch_id": run.get("batch_id"),
            "menu": None,
            "rejected_topic_count": 0,
            "informs_covered": [],
        }
    if parsed.get("informs_coverage_confirmed") is not True:
        return {
            "success": False,
            "error": "informs_coverage_confirmed must be true",
            "batch_id": run.get("batch_id"),
            "menu": None,
            "rejected_topic_count": 0,
            "informs_covered": [],
        }
    if not isinstance(parsed.get("informs_covered"), list):
        return {
            "success": False,
            "error": "informs_covered must be a list",
            "batch_id": run.get("batch_id"),
            "menu": None,
            "rejected_topic_count": 0,
            "informs_covered": [],
        }

    raw_topics = parsed.get("topics")
    if not isinstance(raw_topics, list):
        return {
            "success": False,
            "error": "topics must be a list",
            "batch_id": run.get("batch_id"),
            "menu": None,
            "rejected_topic_count": 0,
            "informs_covered": [],
        }

    validated: list = []
    rejected = 0
    if debug:
        logger.set_debug_flag(True)
        logger.debug_index(
            func="generate_topic_menu_from_preamble",
            index=1,
            total=2,
            identifier=candidate_id,
            outcome="found",
        )
        logger.debug_detail(
            f"raw_topics={len(raw_topics)} coverage_confirmed={parsed.get('informs_coverage_confirmed')}"
        )

    for topic in raw_topics:
        if not isinstance(topic, dict):
            rejected += 1
            if debug:
                logger.debug_detail("reject=non_dict_topic")
            continue
        row = dict(topic)
        if "status" not in row:
            row["status"] = TOPIC_MENU_CONFIG["default_status"]
        try:
            validated.append(validate_topic(row))
        except ValueError as exc:
            rejected += 1
            if debug:
                logger.debug_detail(f"reject={exc}")

    if not validated:
        return {
            "success": False,
            "error": "no valid topics after informs validation",
            "batch_id": run.get("batch_id"),
            "menu": None,
            "rejected_topic_count": rejected,
            "informs_covered": [],
        }

    # Authoritative coverage from survivors (catalog order, then leftovers).
    seen_informs: set = set()
    for t in validated:
        for inf in t["informs"]:
            seen_informs.add(inf)
    informs_covered_effective: list = []
    for inf in TOPIC_MENU_CONFIG["informs"]:
        if inf in seen_informs:
            informs_covered_effective.append(inf)
            seen_informs.discard(inf)
    informs_covered_effective.extend(sorted(seen_informs))

    outgoing: dict = {"topics": validated}
    if current.get("preamble_confirmed_at"):
        outgoing["preamble_confirmed_at"] = current["preamble_confirmed_at"]
    saved = save_topic_menu(candidate_id, outgoing, revise=True, debug=debug)

    if debug:
        status_counts = {s: 0 for s in TOPIC_MENU_CONFIG["statuses"]}
        for t in saved.get("topics") or []:
            st = t.get("status")
            if st in status_counts:
                status_counts[st] += 1
        logger.debug_index(
            func="generate_topic_menu_from_preamble",
            index=2,
            total=2,
            identifier=candidate_id,
            outcome="recorded",
        )
        logger.debug_detail(
            f"stored={len(saved.get('topics') or [])} rejected={rejected} "
            f"open={status_counts['open']} ready={status_counts['ready']} "
            f"retired={status_counts['retired']} informs_covered={informs_covered_effective}"
        )

    return {
        "success": True,
        "menu": saved,
        "batch_id": run.get("batch_id"),
        "rejected_topic_count": rejected,
        "informs_covered": informs_covered_effective,
        "error": None,
    }


def _ledger_task_key(task_key: str) -> str:
    return f"intake-{task_key}"


def _persist_source_materials(
    candidate_id: str,
    starting_resume_text: str,
    sample_cover_text: Optional[str],
    linkedin_profile_text: Optional[str],
) -> None:
    # Call-boundary names keep legacy param labels; storage keys are AST-1014 remaps.
    if not (starting_resume_text or "").strip():
        raise ValueError("starting_resume_text is required")
    save_candidate_data(
        candidate_id,
        {
            "context": {
                "raw_resume": starting_resume_text.strip(),
                "raw_sample": (sample_cover_text or "").strip(),
                "raw_profile": (linkedin_profile_text or "").strip(),
            }
        },
    )


def _snapshot_from_batch(batch_id: str) -> dict:
    rows = get_agent_data_by_batch(batch_id)
    out = {
        "system": "",
        "cache_a": "",
        "cache_b": "",
        "cache_c": "",
        "cache_d": "",
        "nocache": "",
    }
    nocache_seen = False
    for row in rows:
        bt = row.get("block_type") or ""
        content = row.get("block_data") or ""
        if not isinstance(content, str):
            content = str(content)
        if bt == "SYSTEM":
            out["system"] = content
        elif bt == "CACHE_A":
            out["cache_a"] = content
        elif bt == "CACHE_B":
            out["cache_b"] = content
        elif bt == "CACHE_C":
            out["cache_c"] = content
        elif bt == "CACHE_D":
            out["cache_d"] = content
        elif bt == "NO_CACHE" and not nocache_seen:
            out["nocache"] = content
            nocache_seen = True
    return out


def _validate_interview_turn(parsed: Any) -> dict:
    if not isinstance(parsed, dict):
        raise ValueError("interview turn response must be a JSON object")
    if "ready_to_build" not in parsed or not isinstance(parsed["ready_to_build"], bool):
        raise ValueError("ready_to_build must be a boolean")
    msg = (parsed.get("assistant_message") or "").strip()
    if not msg:
        raise ValueError("assistant_message is required")
    return {"ready_to_build": parsed["ready_to_build"], "assistant_message": msg}


def _append_transcript(
    transcript: list,
    *,
    role: str,
    text: str,
    ready_to_build: Optional[bool] = None,
    mode: Optional[str] = None,
) -> list:
    entry: Dict[str, Any] = {"role": role, "text": text}
    if role == "assistant":
        entry["ready_to_build"] = bool(ready_to_build)
    elif mode:
        entry["mode"] = mode
    return transcript + [entry]


def _live_content_for_turn(mode: str, message: str, transcript: list) -> str:
    del transcript
    if mode == "initiate_candidate":
        return message
    if mode == "candidate_response":
        return json.dumps({"mode": "candidate_response", "user_message": message})
    if mode == "build_request":
        return json.dumps({"mode": "build_request"})
    raise ValueError(f"unknown intake turn mode: {mode}")


def _format_initiate_payload(
    starting_resume_text: str,
    sample_cover_text: Optional[str],
    linkedin_profile_text: Optional[str],
) -> str:
    return (
        f"RESUME:\n{starting_resume_text.strip()}\n\n"
        f"COVER LETTER SAMPLE:\n{(sample_cover_text or '').strip() or '(none)'}\n\n"
        f"LINKEDIN:\n{(linkedin_profile_text or '').strip() or '(none)'}"
    )


async def _run_intake_task(
    candidate_id: str,
    task_key: str,
    live_content: str,
    *,
    prompt_snapshot: Optional[dict],
    debug: bool = False,
) -> dict:
    batch_id = f"{_ledger_task_key(task_key)}-{uuid.uuid4()}"
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    database.save_dispatch_ledger(
        batch_id,
        _ledger_task_key(task_key),
        candidate_id,
        started_at,
        entity_type="candidate",
        batch_size=1,
    )
    log_batch_id.set(batch_id)
    try:
        ctx = get_candidate(candidate_id)
        if not ctx:
            raise ValueError(f"Candidate not found: {candidate_id}")
        if prompt_snapshot:
            ctx = dict(ctx)
            ctx["intake_prompt_snapshot"] = prompt_snapshot
        result = await do_task(
            task_key=task_key,
            live_content=live_content,
            index=candidate_id,
            ctx=ctx,
            debug=debug,
        )
        completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if not result or not result.get("success"):
            err = result.get("error", "intake task failed") if result else "do_task returned None"
            total_cost = compute_batch_cost(batch_id)
            database.update_dispatch_ledger(
                batch_id,
                status="FAILED",
                completed_at=completed_at,
                total_processed=1,
                total_failed=1,
                total_cost=total_cost,
            )
            return {"success": False, "error": err, "batch_id": batch_id, "parsed_response": None}
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
        return {
            "success": True,
            "parsed_response": result.get("parsed_response"),
            "error": None,
            "batch_id": batch_id,
        }
    finally:
        flush_log_buffer()
        log_batch_id.set(None)


def _nested_merge_path(root: dict, path: str, value: str) -> None:
    parts = path.split(".")
    cur = root
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = value


def _apply_build_payload(candidate_id: str, parsed: dict) -> list[str]:
    whitelist = set(INTAKE_CONFIG["build_field_paths"])
    unknown = set(parsed.keys()) - whitelist
    if unknown:
        raise ValueError(f"unexpected build keys: {sorted(unknown)}")
    persisted: list[str] = []
    merge_data: dict = {}
    for path in INTAKE_CONFIG["build_field_paths"]:
        if path not in parsed:
            raise ValueError(f"missing build field: {path}")
        val = (parsed[path] or "").strip()
        if not val:
            raise ValueError(f"build field {path} must be non-empty")
        if path == "company_search_terms":
            sync_company_search_terms_from_text(candidate_id, val)
        else:
            _nested_merge_path(merge_data, path, val)
        persisted.append(path)
    if merge_data:
        save_candidate_data(candidate_id, merge_data)
    check_context_complete(candidate_id)
    return persisted


def _append_intakes_old(candidate_id: str, entry: dict) -> int:
    """Append one archived intake thread to candidate_data.intakes_old; return new list length."""
    cand = get_candidate(candidate_id)
    if not cand:
        raise ValueError(f"Candidate not found: {candidate_id}")
    root = dict(cand.get("candidate_data") or {})
    prior = root.get("intakes_old")
    items = list(prior) if isinstance(prior, list) else []
    items.append(entry)
    save_candidate_data(candidate_id, {"intakes_old": items})
    return len(items)


def archive_active_intake_session(candidate_id: str) -> dict:
    if not get_candidate(candidate_id):
        raise ValueError(f"Candidate not found: {candidate_id}")
    row = fetch_active_intake_session(candidate_id)
    if not row:
        raise LookupError("no active intake session")
    archived_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "intake_session_id": row["intake_session_id"],
        "archived_at": archived_at,
        "status": row.get("status") or INTAKE_CONFIG["session_status_active"],
        "transcript": list(row.get("transcript") or []),
    }
    count = _append_intakes_old(candidate_id, entry)
    database.update_intake_session(
        row["intake_session_id"],
        transcript=row.get("transcript") or [],
        prompt_snapshot=row.get("prompt_snapshot"),
        last_ready_to_build=bool(row.get("last_ready_to_build")),
        status=INTAKE_CONFIG["session_status_archived"],
        built_at=row.get("built_at"),
    )
    return {
        "archived_session_id": row["intake_session_id"],
        "archived_at": archived_at,
        "intakes_old_count": count,
    }


def _transcript_has_assistant(transcript: list) -> bool:
    return any((e or {}).get("role") == "assistant" for e in (transcript or []))


def _session_awaiting_agent(transcript: list) -> bool:
    t = transcript or []
    if not _transcript_has_assistant(t):
        return True
    return (t[-1] or {}).get("role") == "user"


def get_intake_session_dto(row: dict, *, batch_id: Optional[str] = None) -> dict:
    status = row.get("status") or INTAKE_CONFIG["session_status_active"]
    ready = bool(row.get("last_ready_to_build"))
    active = INTAKE_CONFIG["session_status_active"]
    built = INTAKE_CONFIG["session_status_built"]
    out = {
        "session_id": row["intake_session_id"],
        "status": status,
        "transcript": row.get("transcript") or [],
        "ready_to_build": ready,
        "can_build": ready and status == active,
        "build_completed": status == built,
        "awaiting_agent": (
            status == active
            and _session_awaiting_agent(row.get("transcript") or [])
        ),
    }
    if batch_id:
        out["batch_id"] = batch_id
    return out


def _schedule_intake_coroutine(coro_factory, *, label: str) -> None:
    def _worker() -> None:
        asyncio.run(coro_factory())

    threading.Thread(target=_worker, daemon=True, name=label).start()


async def _complete_initiate_turn(
    intake_session_id: str,
    candidate_id: str,
    initiate_payload: str,
    *,
    debug: bool = False,
) -> None:
    row = database.get_intake_session(intake_session_id)
    if not row:
        return
    run = await _run_intake_task(
        candidate_id,
        "intake_initiate_candidate",
        _live_content_for_turn("initiate_candidate", initiate_payload, []),
        prompt_snapshot=None,
        debug=debug,
    )
    if not run["success"]:
        database.update_intake_session(
            intake_session_id,
            transcript=[
                {
                    "role": "assistant",
                    "text": INTAKE_CONFIG["initiate_failure_message"],
                    "ready_to_build": False,
                }
            ],
            prompt_snapshot=row.get("prompt_snapshot"),
            last_ready_to_build=False,
            status=INTAKE_CONFIG["session_status_active"],
            built_at=None,
        )
        return
    turn = _validate_interview_turn(run["parsed_response"])
    initiate_ready = False  # product rule: never ready on first turn (AST-539 AC #2)
    transcript = _append_transcript(
        [],
        role="user",
        text=initiate_payload,
        mode="initiate_candidate",
    )
    transcript = _append_transcript(
        transcript,
        role="assistant",
        text=turn["assistant_message"],
        ready_to_build=initiate_ready,
    )
    snapshot = _snapshot_from_batch(run["batch_id"])
    database.update_intake_session(
        intake_session_id,
        transcript=transcript,
        prompt_snapshot=snapshot,
        last_ready_to_build=initiate_ready,
        status=INTAKE_CONFIG["session_status_active"],
        built_at=None,
    )


async def create_intake_session_and_start(
    candidate_id: str,
    starting_resume_text: str,
    sample_cover_text: Optional[str] = None,
    linkedin_profile_text: Optional[str] = None,
    *,
    debug: bool = False,
) -> dict:
    if not get_candidate(candidate_id):
        raise ValueError(f"Candidate not found: {candidate_id}")
    _persist_source_materials(
        candidate_id, starting_resume_text, sample_cover_text, linkedin_profile_text
    )
    if fetch_active_intake_session(candidate_id):
        raise ValueError("active intake session already exists for candidate")
    intake_session_id = str(uuid.uuid4())
    database.create_intake_session(intake_session_id, candidate_id, transcript=[])
    initiate_payload = _format_initiate_payload(
        starting_resume_text, sample_cover_text, linkedin_profile_text
    )
    _schedule_intake_coroutine(
        lambda: _complete_initiate_turn(
            intake_session_id, candidate_id, initiate_payload, debug=debug
        ),
        label=f"intake-initiate-{intake_session_id[:8]}",
    )
    row = database.get_intake_session(intake_session_id)
    return get_intake_session_dto(row)


async def _complete_turn_response(
    intake_session_id: str,
    candidate_id: str,
    message: str,
    transcript_with_user: list,
    prompt_snapshot: Optional[dict],
    *,
    debug: bool = False,
) -> None:
    row = database.get_intake_session(intake_session_id)
    if not row:
        return
    run = await _run_intake_task(
        candidate_id,
        "intake_candidate_response",
        _live_content_for_turn("candidate_response", message, transcript_with_user),
        prompt_snapshot=prompt_snapshot,
        debug=debug,
    )
    if not run["success"]:
        transcript = _append_transcript(
            list(transcript_with_user),
            role="assistant",
            text=INTAKE_CONFIG["initiate_failure_message"],
            ready_to_build=False,
        )
        database.update_intake_session(
            intake_session_id,
            transcript=transcript,
            prompt_snapshot=row.get("prompt_snapshot"),
            last_ready_to_build=False,
            status=INTAKE_CONFIG["session_status_active"],
            built_at=None,
        )
        return
    turn = _validate_interview_turn(run["parsed_response"])
    transcript = _append_transcript(
        transcript_with_user,
        role="assistant",
        text=turn["assistant_message"],
        ready_to_build=turn["ready_to_build"],
    )
    snapshot = _snapshot_from_batch(run["batch_id"])
    database.update_intake_session(
        intake_session_id,
        transcript=transcript,
        prompt_snapshot=snapshot,
        last_ready_to_build=turn["ready_to_build"],
        status=INTAKE_CONFIG["session_status_active"],
        built_at=None,
    )


async def post_intake_turn(
    intake_session_id: str,
    message: str,
    *,
    debug: bool = False,
) -> dict:
    row = database.get_intake_session(intake_session_id)
    if not row:
        raise LookupError(f"intake session not found: {intake_session_id}")
    if row["status"] != INTAKE_CONFIG["session_status_active"]:
        raise ValueError("session is not ACTIVE")
    if not (message or "").strip():
        raise ValueError("message is required")
    transcript = list(row.get("transcript") or [])
    transcript = _append_transcript(
        transcript,
        role="user",
        text=message.strip(),
        mode="candidate_response",
    )
    database.update_intake_session(
        intake_session_id,
        transcript=transcript,
        prompt_snapshot=row.get("prompt_snapshot"),
        last_ready_to_build=bool(row.get("last_ready_to_build")),
        status=INTAKE_CONFIG["session_status_active"],
        built_at=None,
    )
    _schedule_intake_coroutine(
        lambda: _complete_turn_response(
            intake_session_id,
            row["candidate_id"],
            message.strip(),
            transcript,
            row.get("prompt_snapshot"),
            debug=debug,
        ),
        label=f"intake-turn-{intake_session_id[:8]}",
    )
    updated = database.get_intake_session(intake_session_id)
    return get_intake_session_dto(updated)


async def post_intake_build(intake_session_id: str, *, debug: bool = False) -> dict:
    row = database.get_intake_session(intake_session_id)
    if not row:
        raise LookupError(f"intake session not found: {intake_session_id}")
    if row["status"] == INTAKE_CONFIG["session_status_built"] or row.get("built_at"):
        raise ValueError("build already completed for this session")
    if row["status"] != INTAKE_CONFIG["session_status_active"]:
        raise ValueError("session is not ACTIVE")
    run = await _run_intake_task(
        row["candidate_id"],
        "intake_build_request",
        _live_content_for_turn("build_request", "", row.get("transcript") or []),
        prompt_snapshot=row.get("prompt_snapshot"),
        debug=debug,
    )
    if not run["success"]:
        raise RuntimeError(json.dumps({"error": run["error"], "batch_id": run["batch_id"]}))
    parsed = run["parsed_response"]
    if not isinstance(parsed, dict):
        raise ValueError("build response must be a JSON object")
    persisted = _apply_build_payload(row["candidate_id"], parsed)
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    database.update_intake_session(
        intake_session_id,
        transcript=row.get("transcript") or [],
        prompt_snapshot=row.get("prompt_snapshot"),
        last_ready_to_build=True,
        status=INTAKE_CONFIG["session_status_built"],
        built_at=built_at,
    )
    updated = database.get_intake_session(intake_session_id)
    dto = get_intake_session_dto(updated, batch_id=run["batch_id"])
    dto["persisted_fields"] = persisted
    return dto


def fetch_intake_session(intake_session_id: str) -> Optional[dict]:
    return database.get_intake_session(intake_session_id)


def fetch_active_intake_session(candidate_id: str) -> Optional[dict]:
    return database.get_active_intake_session(candidate_id)
