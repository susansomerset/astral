"""
Meteorite placeholder company ensure, legacy create, and public land_meteorite (AST-1470 / AST-1493 / AST-1495).

Dispatch `stage_meteorite` / `scrape_meteorite` / `land_meteorite` rows (AST-1560) are table
transition runners — not Ruth consult hops; dispatcher custom branch only.

Lazy-insert stem-keyed companies into METEORITE from METEORITE_CONFIG (default
stem → meteorite-<candidate_id>). Track = company state METEORITE or legacy
short_name_prefix. Public stage_meteorite (AST-1530 / AST-1560): classify blob+source handle
only — table ingress uses dispatch transition runners for map/land. Public land_meteorite:
scraps → optional Playwright visible text → qualify_meteorite packet enrich →
per-row Ruth company_stem ensure → tracker.save_meteorite_job. check_inbox (AST-1559):
aliases → fetch → inline classify → fan-out staging rows → archive; no Gmail I/O here —
inbox owns fetch/archive. run_meteorite_retention (AST-1562): scheduled purge of old LANDED
rows + warn stale ERROR/BOT_BLOCKED/ABANDONED; meteorite_email.py retired AST-1562.
create_meteorite_job accepts optional stem= for legacy callers.
create_contact_meteorite (AST-1517 contact-task create) wraps scrape-or-text → create.
"""
from __future__ import annotations

import functools
import inspect
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.core.candidate import email_aliases_for_candidate, get_candidate
from src.core.inbox import (
    archive_candidate_email,
    fetch_candidate_email,
    get_message_html,
    strip_extract_email_html,
)
from src.core import tracker
from src.data.database import (
    claim_meteorite_batch,
    clear_meteorite_batch,
    delete_meteorites_by_ids,
    get_company,
    get_job,
    get_meteorite,
    get_meteorite_batch,
    insert_meteorite_rows,
    list_meteorites_by_source,
    list_meteorites_by_state,
    list_meteorites_for_retention,
    save_company,
    save_job,
    update_candidate_last_email_check,
    update_meteorite,
)
from src.external.playwright import get_visible_text
from src.utils.config import (
    METEORITE_BOT_BLOCKED_NOTIFY_CONFIG,
    METEORITE_CONFIG,
    METEORITE_EMAIL_MAILBOX_CONFIG,
    METEORITE_INGRESS_DISPATCH_CONFIG,
    METEORITE_MONITORING_CONFIG,
    METEORITE_RETENTION_CONFIG,
    METEORITE_STATES_RETENTION,
    STAGE_METEORITE_CONFIG,
    TASK_CONFIG,
    TRACKER_CONFIG,
)
from src.utils.formatting import normalize_pasted_list_email_html
from src.utils.logging import get_logger, log_batch_id, log_debug

logger = get_logger(__name__)


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


def _entity_info(entity_id: Any, entity_type: str, event: str, detail: Any) -> None:
    logger.info(
        "%s | %s %s: %s (batch: %s)",
        entity_id,
        entity_type,
        event,
        detail,
        log_batch_id.get() or "-",
    )


def _meteorite_state_info(
    row_id: Any, to_state: str, *, from_state: Optional[str] = None
) -> None:
    detail = f"{from_state} -> {to_state}" if from_state else to_state
    _entity_info(row_id, "meteorite", "state", detail)


def _warn_item(who: Any, why: str, next_step: str) -> None:
    logger.warning("%s — %s\n  %s", who, why, next_step)


def is_meteorite_company(short_name: Optional[str]) -> bool:
    """True on METEORITE-state companies or legacy meteorite- prefix (AST-1152 / AST-1493)."""
    if not short_name:
        return False
    sn = str(short_name)
    prefix = METEORITE_CONFIG["short_name_prefix"]
    if sn.startswith(prefix):
        return True
    row = get_company(sn)
    if row is None:
        return False
    return (row.get("state") or "") == METEORITE_CONFIG["company_state"]


@_with_log_debug
def ensure_meteorite_company(
    candidate_id: str,
    *,
    stem: Optional[str] = None,
    debug: bool = False,
) -> dict[str, Any]:
    """Ensure {stem}-{candidate_id} exists in METEORITE. Idempotent.

    Omitting stem uses METEORITE_CONFIG default_stem (meteorite-{candidate_id}).
    Existing rows are left as-is (no IGNORE→METEORITE rewrite).

    Returns:
      {"short_name": str, "inserted": bool, "company": dict}
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")

    resolved_stem = (stem or "").strip() or METEORITE_CONFIG["default_stem"]
    short_name = METEORITE_CONFIG["stem_short_name_template"].format(
        stem=resolved_stem,
        candidate_id=candidate_id,
    )
    logger.debug(
        "Calling ensure_meteorite_company: [candidate_id=%s, stem=%s]",
        candidate_id, resolved_stem,
    )
    existing = get_company(short_name)
    if existing is not None:
        logger.debug("Response from ensure_meteorite_company: already-present %s", short_name)
        return {"short_name": short_name, "inserted": False, "company": existing}

    save_company(
        short_name=short_name,
        state=METEORITE_CONFIG["company_state"],
        company_name=METEORITE_CONFIG["company_name"],
        company_data=dict(METEORITE_CONFIG["company_data"]),
        candidate_id=candidate_id,
    )
    row = get_company(short_name)
    if row is None:
        raise RuntimeError(f"meteorite company missing after save: {short_name}")
    _entity_info(short_name, "company", "created", METEORITE_CONFIG["company_state"])
    logger.debug("Response from ensure_meteorite_company: inserted %s", short_name)
    return {"short_name": short_name, "inserted": True, "company": row}


@_with_log_debug
def create_meteorite_job(
    candidate_id: str,
    html_body: str,
    *,
    job_link: Optional[str] = None,
    stem: Optional[str] = None,
    debug: bool = False,
) -> dict[str, Any]:
    """Lazy-ensure meteorite company, then insert a job from raw HTML.

    Create carve-out (not transition_job_state): first write inserts directly into
    METEORITE_CONFIG["job_create_state"] (METEORITE_NEW after AST-1056) the same
    way ingest_jobs inserts into NEW (JOB_STATES prior_states=None unrestricted
    entry). METEORITE_NEW is unrestricted; this path does not expand normal
    JD_READY priors and does not invent a new job state.
    Optional job_link for link-sourced ingest (AST-1061); company_job_id stays None
    (Ruth enrichment owns external UUID). Optional stem= when caller already knows
    the company short_name stem; email-bound land uses land_meteorite, not this helper.

    Returns:
      {
        "astral_job_id": str,
        "company": str,           # meteorite-<candidate_id>
        "state": str,             # job_create_state
        "latest_score": float,    # job_create_latest_score
        "company_inserted": bool, # from ensure
        "job": dict,              # get_job row after writes
      }
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")
    if not isinstance(html_body, str) or not html_body.strip():
        raise ValueError("html_body is required")

    cand = get_candidate(candidate_id)
    if not cand:
        raise ValueError(f"candidate not found: {candidate_id}")

    logger.debug(
        "Calling ensure_meteorite_company: [candidate_id=%s, stem=%s]",
        candidate_id, stem,
    )
    ensured = ensure_meteorite_company(candidate_id, stem=stem, debug=debug)
    logger.debug(
        "Response from ensure_meteorite_company: inserted=%s short_name=%s",
        ensured["inserted"], ensured["short_name"],
    )
    short_name = ensured["short_name"]
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    state = METEORITE_CONFIG["job_create_state"]
    score = float(METEORITE_CONFIG["job_create_latest_score"])
    astral_job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    link = job_link.strip() if job_link and str(job_link).strip() else None

    logger.debug(
        "Calling save_job: [astral_job_id=%s, company=%s, state=%s]",
        astral_job_id, short_name, state,
    )
    inserted = save_job(
        astral_job_id,
        company=short_name,
        state=state,
        job_title=None,
        job_link=link,
        company_job_id=None,
        job_data={jd_key: html_body},
        state_history=[{"to_state": state, "timestamp": now, "score": score}],
        state_changed_at=now,
        merge=False,
    )
    if not inserted:
        raise RuntimeError(f"meteorite job insert failed: {astral_job_id}")

    # INSERT path omits latest_score — update column explicitly (AST-1042 carve-out).
    save_job(astral_job_id, latest_score=score)

    row = get_job(astral_job_id)
    if row is None:
        raise RuntimeError(f"meteorite job missing after save: {astral_job_id}")
    if row.get("state") != state or row.get("latest_score") != score:
        raise RuntimeError(
            f"meteorite job postcondition failed id={astral_job_id} "
            f"state={row.get('state')!r} latest_score={row.get('latest_score')!r}"
        )

    _entity_info(
        astral_job_id, "job", METEORITE_CONFIG["land_outcome_created"], state
    )
    logger.debug("Response from save_job: %s", astral_job_id)
    return {
        "astral_job_id": astral_job_id,
        "company": short_name,
        "state": state,
        "latest_score": score,
        "company_inserted": ensured["inserted"],
        "job": row,
    }


def _contact_param_looks_like_url(param: str) -> bool:
    """True when param is a single-line URL / bare host-path (link mode)."""
    s = (param or "").strip()
    if not s:
        return False
    if "\n" in s or "\r" in s:
        return False
    if " " in s or "\t" in s:
        return False
    if "://" in s:
        return True
    return "." in s and not s.startswith(".")


# ---- Contact-task create (AST-1517) ----

@_with_log_debug
async def create_contact_meteorite(
    astral_candidate_id: str,
    param: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Contact-task: land meteorite from URL (scrape-first) or pasted page text."""
    cid = (astral_candidate_id or "").strip()
    if not cid:
        _warn_item(
            "create_contact_meteorite",
            "no candidate id",
            "This contact create is not landing a job",
        )
        return {
            "ok": False,
            "error": "no_candidate",
            "task_key": "create_contact_meteorite",
        }

    raw = (param or "").strip()
    if not raw:
        _warn_item(
            cid,
            "param required",
            "This contact create is not landing a job",
        )
        return {
            "ok": False,
            "error": "param_required",
            "task_key": "create_contact_meteorite",
        }

    scrape: Optional[Dict[str, Any]] = None
    if _contact_param_looks_like_url(raw):
        mode = "link"
        # Late-import: gazer imports create_meteorite_job at module top.
        from src.core.gazer import contact_task_gazer_scrape

        logger.debug("Calling contact_task_gazer_scrape: [candidate_id=%s, url=%s]", cid, raw)
        scrape = await contact_task_gazer_scrape(cid, raw, debug=debug)
        logger.debug("Response from contact_task_gazer_scrape: %s", scrape)
        if not isinstance(scrape, dict) or not scrape.get("ok"):
            err = (
                (scrape.get("error") if isinstance(scrape, dict) else "scrape_failed")
                or "scrape_failed"
            )
            _warn_item(
                cid,
                f"scrape failed ({err})",
                "This contact create is not landing a job",
            )
            return {
                "ok": False,
                "error": err,
                "task_key": "create_contact_meteorite",
                "mode": mode,
                "scrape": scrape if isinstance(scrape, dict) else None,
            }
        visible = (scrape.get("visible_text") or "").strip()
        if not visible:
            _warn_item(
                cid,
                "scrape returned empty visible text",
                "This contact create is not landing a job",
            )
            return {
                "ok": False,
                "error": "empty_visible_text",
                "task_key": "create_contact_meteorite",
                "mode": mode,
                "scrape": scrape,
            }
        html_body = visible
        job_link = (scrape.get("final_url") or scrape.get("url") or raw).strip()
    else:
        mode = "text"
        html_body = raw
        job_link = None

    logger.debug(
        "Calling create_meteorite_job: [candidate_id=%s, mode=%s, job_link=%s]",
        cid, mode, job_link,
    )
    try:
        created = create_meteorite_job(
            cid,
            html_body,
            job_link=job_link,
            debug=debug,
        )
    except Exception as exc:
        logger.exception(
            "%s | create_contact_meteorite %s\n  %s: %s\n  This contact create is not landing a job",
            cid,
            mode,
            type(exc).__name__,
            exc,
        )
        return {
            "ok": False,
            "error": str(exc),
            "task_key": "create_contact_meteorite",
            "mode": mode,
        }
    logger.debug("Response from create_meteorite_job: %s", created)

    out = {
        "ok": True,
        "task_key": "create_contact_meteorite",
        "mode": mode,
        "astral_candidate_id": cid,
        "result": created,
    }
    if mode == "link" and isinstance(scrape, dict):
        out["url"] = scrape.get("url")
        out["final_url"] = scrape.get("final_url")
        out["page_status"] = scrape.get("page_status")
    return out


async def _land_fetch_link_text(url: str, *, debug: bool = False) -> tuple[str, str]:
    """Return (visible_text, final_url) via Playwright; empty text on failure."""
    _ = debug
    logger.debug("Calling get_visible_text: [url=%s]", url)
    try:
        result = await get_visible_text(url=url, return_final_url=True)
    except Exception:
        logger.debug("Response from get_visible_text: empty (fetch failed)")
        return ("", url)
    if isinstance(result, tuple):
        text, final_url = result
        out = (text or ""), (final_url or url)
        logger.debug("Response from get_visible_text: %s", out)
        return out
    out = (result or ""), url
    logger.debug("Response from get_visible_text: %s", out)
    return out


def _land_scrap_body(scrap: Dict[str, Any]) -> str:
    for key in ("content", "text", "html_body"):
        val = scrap.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _land_rollup_outcome(outcomes: List[Dict[str, Any]]) -> str:
    """Roll up per-row Tracker outcomes (AST-1470 Decision)."""
    created = METEORITE_CONFIG["land_outcome_created"]
    skip = METEORITE_CONFIG["land_outcome_duplicate_skip"]
    super_o = METEORITE_CONFIG["land_outcome_superseded"]
    err = METEORITE_CONFIG["land_outcome_error"]
    if not outcomes:
        return err
    labels = [(o.get("outcome") or err) for o in outcomes]
    if all(x == skip for x in labels):
        return skip
    if any(x == created for x in labels):
        return created
    if any(x == super_o for x in labels):
        return super_o
    if any(x == skip for x in labels):
        return skip
    return err


@_with_log_debug
async def stage_meteorite(
    candidate_id: str,
    blob: str,
    *,
    source_kind: str,
    source_id: str,
    debug: bool = False,
) -> Dict[str, Any]:
    """Public ingress stage: classify blob only (AST-1530 / AST-1560).

    Returns classify outcome + jobs[]; table path uses dispatch transition runners
    for stage/scrape/land. Does not claim METEORITE_NEW or run qualify_meteorite dispatch.
    """
    err_key = METEORITE_CONFIG["land_outcome_error"]

    def _err(error: str, *, batch_id=None, stage_outcome=None) -> Dict[str, Any]:
        return {
            "outcome": err_key,
            "stage_outcome": stage_outcome,
            "skipped": False,
            "jobs": [],
            "error": error,
            "batch_id": batch_id,
        }

    cid = (candidate_id or "").strip()
    if not cid:
        _warn_item(
            "stage_meteorite",
            "candidate_id is required",
            "This blob is not being classified",
        )
        return _err("candidate_id is required")
    cand = get_candidate(cid)
    if not cand:
        _warn_item(
            cid,
            "candidate not found",
            "This blob is not being classified",
        )
        return _err(f"candidate not found: {cid}")

    # Late-import: consult loads is_meteorite_company at module top.
    from src.core.consult import invoke_stage_meteorite

    ctx = dict(cand) if isinstance(cand, dict) else {}
    ctx["astral_candidate_id"] = cid
    logger.debug(
        "Calling invoke_stage_meteorite: [candidate_id=%s, source_kind=%s, source_id=%s]",
        cid, source_kind, source_id,
    )
    invoke = await invoke_stage_meteorite(
        cid, blob, source_kind=source_kind, source_id=source_id, ctx=ctx, debug=debug,
    )
    logger.debug("Response from invoke_stage_meteorite: %s", invoke)
    batch_id = invoke.get("batch_id")

    if not invoke.get("success"):
        _warn_item(
            cid,
            invoke.get("error") or "stage invoke failed",
            "This blob is not being classified into meteorite rows",
        )
        return _err(invoke.get("error") or "stage invoke failed", batch_id=batch_id)

    stage_outcome = invoke["outcome"]
    kind = (source_kind or "").strip()
    sid = (source_id or "").strip()

    if stage_outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
        _warn_item(
            cid,
            f"classify skipped ({stage_outcome})",
            "No meteorite rows are being inserted",
        )
        return {
            "outcome": stage_outcome,
            "stage_outcome": stage_outcome,
            "skipped": True,
            "jobs": [],
            "error": None,
            "batch_id": batch_id,
        }

    jobs = invoke.get("jobs") or []
    logger.debug(
        "stage_meteorite classify_only source_kind=%s source_id=%s job_count=%s",
        kind, sid, len(jobs),
    )
    return {
        "outcome": stage_outcome,
        "stage_outcome": stage_outcome,
        "skipped": False,
        "jobs": jobs,
        "error": None,
        "batch_id": batch_id,
    }


@_with_log_debug
async def land_meteorite(
    candidate_id: str,
    *,
    scraps: Optional[List[Dict[str, Any]]] = None,
    text: Optional[str] = None,
    job_link: Optional[str] = None,
    employer_name: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Public meteorite land: scraps → enrich → Tracker save (AST-1470).

    Returns company + outcomes[] + rollup outcome. Never a silent no-op.
    """
    err_key = METEORITE_CONFIG["land_outcome_error"]
    ok_outcomes = (
        METEORITE_CONFIG["land_outcome_created"],
        METEORITE_CONFIG["land_outcome_duplicate_skip"],
        METEORITE_CONFIG["land_outcome_superseded"],
    )

    if scraps is not None and not isinstance(scraps, list):
        raise ValueError("scraps must be a list or None")

    cid = (candidate_id or "").strip()
    if not cid:
        _warn_item(
            "land_meteorite",
            "candidate_id is required",
            "No job is being saved",
        )
        return {
            "outcome": err_key,
            "error": "candidate_id is required",
            "outcomes": [],
            "company": None,
            "company_inserted": False,
        }

    # Normalize scraps: list from caller, or one row from top-level text/link/employer.
    if scraps is not None and len(scraps) > 0:
        work: List[Dict[str, Any]] = [dict(s) for s in scraps if isinstance(s, dict)]
    else:
        work = [{
            "job_link": (job_link or "").strip() if job_link else "",
            "text": (text or "").strip() if text else "",
            "employer_name": (employer_name or "").strip() if employer_name else "",
        }]
        if not work[0]["job_link"] and not work[0]["text"]:
            _warn_item(
                cid,
                "scraps required (link and/or text)",
                "No job is being saved",
            )
            return {
                "outcome": err_key,
                "error": "scraps required (link and/or text)",
                "outcomes": [],
                "company": None,
                "company_inserted": False,
            }

    cand = get_candidate(cid)
    if not cand:
        _warn_item(
            cid,
            "candidate not found",
            "No job is being saved",
        )
        return {
            "outcome": err_key,
            "error": f"candidate not found: {cid}",
            "outcomes": [],
            "company": None,
            "company_inserted": False,
        }

    min_jd = int(TASK_CONFIG["qualify_meteorite"]["min_jd_chars"])

    # Optional link scrape when body is thin.
    for scrap in work:
        link = (scrap.get("job_link") or "").strip() if isinstance(scrap.get("job_link"), str) else ""
        if link:
            scrap["job_link"] = link
        body = _land_scrap_body(scrap)
        if link and len(body) < min_jd:
            visible, final_url = await _land_fetch_link_text(link, debug=debug)
            if visible:
                scrap["content"] = visible
            if final_url:
                scrap["job_link"] = final_url

    # Late-import: consult loads is_meteorite_company at module top.
    from src.core.consult import enrich_meteorite_land_packet

    ctx = dict(cand) if isinstance(cand, dict) else {}
    ctx["astral_candidate_id"] = cid
    logger.debug(
        "Calling enrich_meteorite_land_packet: [candidate_id=%s, scraps=%s]",
        cid, len(work),
    )
    enrich = await enrich_meteorite_land_packet(cid, work, ctx=ctx, debug=debug)
    logger.debug("Response from enrich_meteorite_land_packet: %s", enrich)
    if not enrich.get("success") or not enrich.get("jobs"):
        _warn_item(
            cid,
            enrich.get("error") or "enrichment produced no jobs",
            "No job is being saved",
        )
        return {
            "outcome": err_key,
            "error": enrich.get("error") or "enrichment produced no jobs",
            "outcomes": [],
            "company": None,
            "company_inserted": False,
        }

    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    outcomes: List[Dict[str, Any]] = []
    enriched_jobs = enrich["jobs"]
    n = len(enriched_jobs)
    first_company: Optional[str] = None
    first_company_inserted = False
    logger.debug("Beginning land enrich job loop on %s items", n)
    for i, row in enumerate(enriched_jobs, start=1):
        found_jd = row.get("jd_text") or ""
        found_emp = row.get("employer_name") or ""
        row_stem = (row.get("company_stem") or "").strip() if isinstance(row.get("company_stem"), str) else ""
        try:
            logger.debug(
                "Calling ensure_meteorite_company: [candidate_id=%s, stem=%s]",
                cid, row_stem or None,
            )
            ensured_row = ensure_meteorite_company(cid, stem=row_stem or None, debug=debug)
            logger.debug(
                "Response from ensure_meteorite_company: inserted=%s short_name=%s",
                ensured_row["inserted"], ensured_row["short_name"],
            )
            row_company = ensured_row["short_name"]
            if first_company is None:
                first_company = row_company
                first_company_inserted = bool(ensured_row["inserted"])
            logger.debug(
                "Calling tracker.save_meteorite_job: [candidate_id=%s, company=%s]",
                cid, row_company,
            )
            save = tracker.save_meteorite_job(
                cid,
                company=row_company,
                company_job_id=row.get("company_job_id") or None,
                job_title=row.get("job_title") or None,
                job_link=row.get("job_link") or None,
                job_data={jd_key: found_jd},
                employer_name=found_emp or None,
                debug=debug,
            )
            logger.debug("Response from tracker.save_meteorite_job: %s", save)
            outcomes.append(save)
            if save.get("outcome") in ok_outcomes:
                _entity_info(
                    save.get("astral_job_id"),
                    "job",
                    save.get("outcome"),
                    row_company,
                )
        except (ValueError, RuntimeError) as e:
            outcomes.append({
                "outcome": err_key,
                "error": str(e),
                "astral_job_id": None,
            })
            _warn_item(
                cid,
                str(e),
                "This scrap is not being saved as a job",
            )

    logger.debug("End land enrich job loop after %s items", n)
    rollup = _land_rollup_outcome(outcomes)
    top_error = None
    if rollup == err_key and not any(
        o.get("outcome") in ok_outcomes
        for o in outcomes
    ):
        top_error = next((o.get("error") for o in outcomes if o.get("error")), "land failed")

    return {
        "company": first_company,
        "company_inserted": first_company_inserted,
        "outcomes": outcomes,
        "outcome": rollup,
        "error": top_error,
    }


# --- check_inbox (AST-1559) ---

def _map_classify_jobs_to_meteorite_rows(
    outcome: str,
    jobs: List[Dict[str, Any]],
    *,
    candidate_id: str,
    source_kind: str,
    source_id: str,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Map classify jobs → insert_meteorite_rows dicts (no source_ref synthesis)."""
    if source_kind not in STAGE_METEORITE_CONFIG["source_ref_prefixes"]:
        return [], "invalid source_kind"
    if outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
        return [], None

    cid = (candidate_id or "").strip()
    sid = (source_id or "").strip()
    if not cid or not sid:
        return [], "candidate_id and source_id required"

    rows = [j for j in jobs if isinstance(j, dict)]
    out: List[Dict[str, Any]] = []

    if outcome in STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]:
        if len(rows) < 1:
            return [], "text outcome produced no jobs"
        for job in rows:
            text = (job.get("jd_text") or "").strip() if isinstance(job.get("jd_text"), str) else ""
            if not text:
                return [], "text scrap missing jd_text"
            out.append({
                "candidate_id": cid,
                "source_kind": source_kind,
                "source_id": sid,
                "classify_outcome": outcome,
                "content": text,
                "link": None,
            })
        return out, None

    if outcome in STAGE_METEORITE_CONFIG["url_scrape_outcomes"]:
        if len(rows) < 1:
            return [], "url outcome produced no jobs"
        for job in rows:
            link = (job.get("job_link") or "").strip() if isinstance(job.get("job_link"), str) else ""
            if not (link.startswith("http://") or link.startswith("https://")):
                return [], "url scrap missing http(s) job_link"
            text = (job.get("jd_text") or "").strip() if isinstance(job.get("jd_text"), str) else ""
            out.append({
                "candidate_id": cid,
                "source_kind": source_kind,
                "source_id": sid,
                "classify_outcome": outcome,
                "content": text or None,
                "link": link,
            })
        return out, None

    return [], "unhandled stage outcome"


def _monitor_message_fields(msg: dict, payload: dict | None = None) -> dict[str, Any]:
    payload = payload or {}
    return {
        "from_address": (msg.get("from_address") or payload.get("from_address") or ""),
        "message_id": msg.get("id") or "",
        "internal_date_ms": int(msg.get("internal_date_ms") or 0),
        "subject": (payload.get("subject") or msg.get("subject") or ""),
    }


@_with_log_debug
async def ingest_candidate_email_message(
    candidate_id: str,
    message_id: str,
    *,
    debug: bool = False,
    msg: dict | None = None,
    index: int = 1,
    total: int = 1,
) -> dict[str, Any]:
    """One mid: dedup → classify → fan-out/skip → archive (shared by check_inbox + Land).

    Returns Land-shaped row: message_id, outcome, astral_candidate_id, optional error /
    job_count / inserted_ids, plus counter passed|error for mailbox rollup.
    """
    err_key = METEORITE_CONFIG["land_outcome_error"]
    already = METEORITE_MONITORING_CONFIG["outcome_already_ingested"]
    cid = str(candidate_id or "").strip()
    mid = str(message_id or "").strip()
    base_msg = dict(msg) if isinstance(msg, dict) else {"id": mid}
    if mid and not base_msg.get("id"):
        base_msg["id"] = mid

    def _row(
        outcome: str,
        *,
        counter: str,
        error: str | None = None,
        job_count: int = 0,
        inserted_ids: list | None = None,
    ) -> dict[str, Any]:
        out: dict[str, Any] = {
            "message_id": mid,
            "outcome": outcome,
            "astral_candidate_id": cid,
            "job_count": job_count,
            "counter": counter,
        }
        if error:
            out["error"] = error
        if inserted_ids is not None:
            out["inserted_ids"] = inserted_ids
        return out

    if not cid:
        _warn_item(
            "ingest_candidate_email_message",
            "candidate_id is required",
            "This message is not being ingested",
        )
        return _row(err_key, counter="error", error="candidate_id is required")
    if not mid:
        _warn_item(
            cid,
            "message_id is required",
            "This message is not being ingested",
        )
        return _row(err_key, counter="error", error="message_id is required")

    monitor_base = _monitor_message_fields(base_msg)
    try:
        logger.debug(
            "Calling ingest_candidate_email_message: [index=%s/%s, mid=%s, from=%s]",
            index, total, mid, monitor_base["from_address"],
        )

        existing = list_meteorites_by_source("email", mid)
        if existing:
            _warn_item(
                cid,
                f"message {mid} already ingested",
                "No new meteorite rows are being inserted",
            )
            try:
                logger.debug("Calling archive_candidate_email: [message_id=%s]", mid)
                archive_candidate_email(mid)
                logger.debug("Response from archive_candidate_email: ok")
                return _row(already, counter="passed", job_count=len(existing))
            except Exception as exc:
                logger.exception(
                    "%s | inbox archive %s\n  %s: %s\n  The message was already ingested; archive did not finish",
                    cid, mid, type(exc).__name__, exc,
                )
                return _row(
                    already,
                    counter="error",
                    error=str(exc),
                    job_count=len(existing),
                )

        payload = get_message_html(mid)
        monitor_base = _monitor_message_fields(base_msg, payload)
        logger.debug(
            "inbox message guts subject=%s from=%s",
            monitor_base["subject"], monitor_base["from_address"],
        )
        blob = strip_extract_email_html(
            payload.get("subject") or "",
            payload.get("html_body") or "",
            from_address=payload.get("from_address") or "",
            to_address=payload.get("to_address") or "",
            date=payload.get("date") or "",
        )

        cand = get_candidate(cid)
        ctx = dict(cand) if isinstance(cand, dict) else {}
        ctx["astral_candidate_id"] = cid
        # Late-import: consult loads is_meteorite_company at module top.
        from src.core.consult import invoke_stage_meteorite

        logger.debug(
            "Calling invoke_stage_meteorite: [candidate_id=%s, source_kind=email, source_id=%s]",
            cid, mid,
        )
        invoke = await invoke_stage_meteorite(
            cid,
            blob,
            source_kind="email",
            source_id=mid,
            ctx=ctx,
            debug=debug,
        )
        logger.debug("Response from invoke_stage_meteorite: %s", invoke)

        if not invoke.get("success"):
            _warn_item(
                cid,
                str(invoke.get("error") or "classify_failed"),
                "This message is not being ingested",
            )
            return _row(
                err_key,
                counter="error",
                error=str(invoke.get("error") or "classify_failed"),
            )

        stage_outcome = invoke["outcome"]
        if stage_outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
            _warn_item(
                cid,
                f"classify skipped ({stage_outcome})",
                "No meteorite rows are being inserted",
            )
            try:
                logger.debug("Calling archive_candidate_email: [message_id=%s]", mid)
                archive_candidate_email(mid)
                logger.debug("Response from archive_candidate_email: ok")
                return _row(str(stage_outcome), counter="passed")
            except Exception as exc:
                logger.exception(
                    "%s | inbox archive %s\n  %s: %s\n  Classify skipped; archive did not finish",
                    cid, mid, type(exc).__name__, exc,
                )
                return _row(str(stage_outcome), counter="error", error=str(exc))

        row_dicts, map_err = _map_classify_jobs_to_meteorite_rows(
            stage_outcome,
            invoke.get("jobs") or [],
            candidate_id=cid,
            source_kind="email",
            source_id=mid,
        )
        if map_err:
            _warn_item(
                cid,
                str(map_err),
                "This message is not being ingested",
            )
            return _row(err_key, counter="error", error=str(map_err))

        job_list = invoke.get("jobs") or []
        logger.debug("Calling insert_meteorite_rows: [n=%s]", len(row_dicts))
        ids = insert_meteorite_rows(row_dicts)
        logger.debug("Response from insert_meteorite_rows: %s", ids)
        if len(ids) != len(row_dicts) or len(row_dicts) != len(job_list):
            _warn_item(
                cid,
                (
                    f"insert_count_mismatch ids={len(ids)} "
                    f"rows={len(row_dicts)} jobs={len(job_list)}"
                ),
                "This message is not being ingested",
            )
            return _row(
                err_key,
                counter="error",
                error=(
                    f"insert_count_mismatch ids={len(ids)} "
                    f"rows={len(row_dicts)} jobs={len(job_list)}"
                ),
            )

        for row_id in ids:
            _meteorite_state_info(row_id, "NEW")
        try:
            logger.debug("Calling archive_candidate_email: [message_id=%s]", mid)
            archive_candidate_email(mid)
            logger.debug("Response from archive_candidate_email: ok")
            return _row(
                str(stage_outcome),
                counter="passed",
                job_count=len(ids),
                inserted_ids=ids,
            )
        except Exception as exc:
            logger.exception(
                "%s | inbox archive %s\n  %s: %s\n  Meteorite rows were inserted; archive did not finish",
                cid, mid, type(exc).__name__, exc,
            )
            return _row(
                str(stage_outcome),
                counter="error",
                error=str(exc),
                job_count=len(ids),
                inserted_ids=ids,
            )

    except Exception as exc:
        logger.exception(
            "%s | inbox message %s\n  %s: %s\n  This message is not being ingested",
            cid, mid, type(exc).__name__, exc,
        )
        return _row(err_key, counter="error", error=str(exc))


@_with_log_debug
async def check_inbox(task: dict, *, debug: bool = False) -> dict[str, int]:
    """Candidate-bound mailbox: aliases → fetch → classify → fan-out → archive."""
    cid = str((task or {}).get("candidate_id") or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    env_user = (os.environ.get("GMAIL_USER") or "").casefold()
    expected = (METEORITE_EMAIL_MAILBOX_CONFIG["account_address"] or "").casefold()
    if env_user != expected:
        logger.debug(
            "account_mismatch GMAIL_USER=%r expected=%r", env_user, expected
        )

    aliases = email_aliases_for_candidate(cid)
    logger.debug("Calling fetch_candidate_email: [aliases=%s]", aliases)
    messages = fetch_candidate_email(aliases, debug=debug)
    logger.debug("Response from fetch_candidate_email: %s", messages)
    n = len(messages)
    processed = passed = failed = errors = 0

    logger.debug("Beginning inbox message loop on %s items", n)
    for i, msg in enumerate(messages, start=1):
        mid = msg.get("id") or ""
        row = await ingest_candidate_email_message(
            cid, mid, debug=debug, msg=msg, index=i, total=n,
        )
        processed += 1
        if row.get("counter") == "passed":
            passed += 1
        else:
            errors += 1
    logger.debug("End inbox message loop after %s items", n)

    update_candidate_last_email_check(cid)
    _entity_info(cid, "candidate", "last_email_check", "stamped")

    return {
        "total_processed": processed,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }


# --- dispatch transition runners (AST-1560) ---

_ZERO_SUMMARY: Dict[str, int] = {
    "total_processed": 0,
    "total_passed": 0,
    "total_failed": 0,
    "total_errors": 0,
}


def _is_http_url(link: str) -> bool:
    return link.startswith("http://") or link.startswith("https://")


def _row_miss(row_id: Any, cid: str, why: str, next_step: str) -> None:
    _warn_item(f"meteorite {row_id} for {cid}", why, next_step)


@_with_log_debug
async def run_stage_meteorite(task: Dict[str, Any], *, debug: bool = False) -> Dict[str, int]:
    """Dispatch runner: NEW → SCRAPE_LINK | READY (AST-1560)."""
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s]",
        batch_id, cfg["stage_trigger_state"], batch_size,
    )
    claim_meteorite_batch(batch_id, cfg["stage_trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    logger.debug("Response from get_meteorite_batch: %s", rows)
    if not rows:
        return summary

    logger.debug("Beginning stage meteorite loop on %s items", len(rows))
    try:
        for row in rows:
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            try:
                outcome = (row.get("classify_outcome") or "").strip()
                if not outcome:
                    update_meteorite(row_id, state="ERROR", error="missing classify_outcome")
                    _row_miss(
                        row_id, cid, "missing classify_outcome", "This row is ERROR",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue
                if outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
                    update_meteorite(row_id, state="ERROR", error="skip outcome on row")
                    _row_miss(
                        row_id, cid, "skip outcome on row", "This row is ERROR",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue
                if outcome in STAGE_METEORITE_CONFIG["url_scrape_outcomes"]:
                    link = (row.get("link") or "").strip()
                    if not _is_http_url(link):
                        update_meteorite(row_id, state="ERROR", error="missing link")
                        _row_miss(row_id, cid, "missing link", "This row is ERROR")
                        summary["total_failed"] += 1
                        summary["total_errors"] += 1
                        continue
                    update_meteorite(row_id, state="SCRAPE_LINK", link=link)
                    _meteorite_state_info(row_id, "SCRAPE_LINK", from_state="NEW")
                    summary["total_passed"] += 1
                    continue
                if outcome in STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]:
                    content = (row.get("content") or "").strip()
                    if not content:
                        update_meteorite(row_id, state="ERROR", error="missing content")
                        _row_miss(row_id, cid, "missing content", "This row is ERROR")
                        summary["total_failed"] += 1
                        summary["total_errors"] += 1
                        continue
                    update_meteorite(row_id, state="READY")
                    _meteorite_state_info(row_id, "READY", from_state="NEW")
                    summary["total_passed"] += 1
                    continue
                err = f"unhandled classify_outcome: {outcome}"
                update_meteorite(row_id, state="ERROR", error=err)
                _row_miss(row_id, cid, err, "This row is ERROR")
                summary["total_failed"] += 1
                summary["total_errors"] += 1
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                logger.exception(
                    "%s | meteorite %s run_stage_meteorite\n  %s: %s\n  Continuing to the next row",
                    cid, row_id, type(exc).__name__, exc,
                )
    finally:
        logger.debug("End stage meteorite loop after %s items", summary["total_processed"])
        clear_meteorite_batch(batch_id)
    return summary


@_with_log_debug
async def run_scrape_meteorite(task: Dict[str, Any], *, debug: bool = False) -> Dict[str, int]:
    """Dispatch runner: SCRAPE_LINK → READY | BOT_BLOCKED | ERROR (AST-1560)."""
    from src.core.gazer import _CONTACT_PAGE_STATUS, _classify_jd

    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")
    status_map = cfg["scrape_page_status_states"]

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s]",
        batch_id, cfg["scrape_trigger_state"], batch_size,
    )
    claim_meteorite_batch(batch_id, cfg["scrape_trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    logger.debug("Response from get_meteorite_batch: %s", rows)
    if not rows:
        return summary

    logger.debug("Beginning scrape meteorite loop on %s items", len(rows))
    try:
        for row in rows:
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            link = (row.get("link") or "").strip()
            try:
                if not _is_http_url(link):
                    update_meteorite(row_id, state="ERROR", error="missing link")
                    _row_miss(row_id, cid, "missing link", "This row is ERROR")
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue

                visible_text, final_url = await _land_fetch_link_text(link, debug=debug)
                page_status = _CONTACT_PAGE_STATUS.get(_classify_jd(visible_text), "missing")

                if page_status == "blocked":
                    update_meteorite(row_id, state=status_map["blocked"])
                    _row_miss(
                        row_id, cid,
                        f"scrape blocked at {link}",
                        "This row is BOT_BLOCKED",
                    )
                    summary["total_passed"] += 1
                    continue

                if page_status == "ok" and visible_text.strip():
                    update_meteorite(
                        row_id,
                        state="READY",
                        content=visible_text,
                        link=final_url or link,
                    )
                    _meteorite_state_info(row_id, "READY", from_state="SCRAPE_LINK")
                    summary["total_passed"] += 1
                    continue

                err = "empty visible text" if page_status == "ok" else f"scrape_{page_status}"
                update_meteorite(row_id, state=status_map.get(page_status, "ERROR"), error=err)
                _row_miss(row_id, cid, err, "This row is ERROR")
                summary["total_failed"] += 1
                summary["total_errors"] += 1
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                logger.exception(
                    "%s | meteorite %s run_scrape_meteorite\n  %s: %s\n  Continuing to the next row",
                    cid, row_id, type(exc).__name__, exc,
                )
    finally:
        logger.debug("End scrape meteorite loop after %s items", summary["total_processed"])
        clear_meteorite_batch(batch_id)
    return summary


@_with_log_debug
async def run_land_meteorite(task: Dict[str, Any], *, debug: bool = False) -> Dict[str, int]:
    """Dispatch runner: READY → LANDED + job create (AST-1560)."""
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    ok_outcomes = (
        METEORITE_CONFIG["land_outcome_created"],
        METEORITE_CONFIG["land_outcome_duplicate_skip"],
        METEORITE_CONFIG["land_outcome_superseded"],
    )

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s]",
        batch_id, cfg["land_trigger_state"], batch_size,
    )
    claim_meteorite_batch(batch_id, cfg["land_trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    logger.debug("Response from get_meteorite_batch: %s", rows)
    if not rows:
        return summary

    logger.debug("Beginning land meteorite loop on %s items", len(rows))
    try:
        for row in rows:
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            try:
                content = (row.get("content") or "").strip()
                if not content:
                    update_meteorite(row_id, state="ERROR", error="missing content")
                    _row_miss(row_id, cid, "missing content", "This row is ERROR")
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue

                logger.debug("Calling ensure_meteorite_company: [candidate_id=%s]", cid)
                ensured = ensure_meteorite_company(cid, debug=debug)
                logger.debug(
                    "Response from ensure_meteorite_company: inserted=%s short_name=%s",
                    ensured["inserted"], ensured["short_name"],
                )
                existing_link = (row.get("link") or "").strip()
                job_link = existing_link if _is_http_url(existing_link) else None
                logger.debug(
                    "Calling tracker.save_meteorite_job: [candidate_id=%s, company=%s]",
                    cid, ensured["short_name"],
                )
                save = tracker.save_meteorite_job(
                    cid,
                    company=ensured["short_name"],
                    job_data={jd_key: content},
                    job_link=job_link,
                    company_job_id=None,
                    employer_name=None,
                    debug=debug,
                )
                logger.debug("Response from tracker.save_meteorite_job: %s", save)
                if save.get("outcome") in ok_outcomes:
                    job_id = str(save.get("astral_job_id") or "")
                    update_meteorite(row_id, state="LANDED", astral_job_id=job_id)
                    _meteorite_state_info(row_id, "LANDED", from_state="READY")
                    _entity_info(job_id, "job", save.get("outcome"), ensured["short_name"])
                    summary["total_passed"] += 1
                    continue

                err = str(save.get("error") or "land failed")
                update_meteorite(row_id, state="ERROR", error=err)
                _row_miss(row_id, cid, err, "This row is ERROR")
                summary["total_failed"] += 1
                summary["total_errors"] += 1
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                logger.exception(
                    "%s | meteorite %s run_land_meteorite\n  %s: %s\n  Continuing to the next row",
                    cid, row_id, type(exc).__name__, exc,
                )
    finally:
        logger.debug("End land meteorite loop after %s items", summary["total_processed"])
        clear_meteorite_batch(batch_id)
    return summary


@_with_log_debug
async def run_notify_meteorite_bot_blocked(
    task: Dict[str, Any], *, debug: bool = False
) -> Dict[str, int]:
    """Dispatch runner: BOT_BLOCKED → Estelle DM + nag → ABANDONED (AST-1561)."""
    cfg = METEORITE_BOT_BLOCKED_NOTIFY_CONFIG
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s]",
        batch_id, cfg["trigger_state"], batch_size,
    )
    claim_meteorite_batch(batch_id, cfg["trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    logger.debug("Response from get_meteorite_batch: %s", rows)
    if not rows:
        return summary

    nag_limit = int(cfg["nag_limit"])
    logger.debug("Beginning notify meteorite loop on %s items", len(rows))
    try:
        for row in rows:
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            nag_count = int(row.get("nag_count") or 0)
            try:
                if nag_count >= nag_limit:
                    update_meteorite(
                        row_id, state="ABANDONED", error="nag limit exceeded"
                    )
                    _row_miss(
                        row_id, cid,
                        "nag limit exceeded",
                        "This row is ABANDONED",
                    )
                    summary["total_passed"] += 1
                    continue

                channel = _resolve_slack_dm_channel_for_candidate(cid)
                if not channel:
                    update_meteorite(row_id, error="no slack dm channel")
                    _row_miss(
                        row_id, cid,
                        "no slack dm channel",
                        "This row is staying BOT_BLOCKED",
                    )
                    summary["total_failed"] += 1
                    continue

                first = row.get("estelle_notified_at") is None
                message = _format_bot_blocked_dm(
                    row,
                    nag_count=nag_count + 1,
                    nag_limit=nag_limit,
                    first=first,
                )
                from src.core.contact import contact_post_message

                logger.debug(
                    "Calling contact_post_message: [channel=%s]",
                    channel,
                )
                resp = contact_post_message(
                    channel=channel, text=message, thread_ts=None, debug=debug
                )
                logger.debug("Response from contact_post_message: %s", resp)
                if not resp.get("ok"):
                    err = str(resp.get("error") or "slack post failed")
                    update_meteorite(row_id, error=err)
                    _row_miss(
                        row_id, cid, err, "This row is staying BOT_BLOCKED",
                    )
                    summary["total_failed"] += 1
                    continue

                thread_ts = str(
                    resp.get("ts")
                    or (resp.get("message") or {}).get("ts")
                    or ""
                ).strip()
                notified_at = datetime.now(timezone.utc).isoformat()
                update_meteorite(
                    row_id,
                    estelle_notified_at=notified_at,
                    estelle_thread_ts=thread_ts or row.get("estelle_thread_ts"),
                    nag_count=nag_count + 1,
                    error=None,
                )
                _entity_info(
                    row_id,
                    "meteorite",
                    "notified",
                    f"nag {nag_count + 1} of {nag_limit}",
                )
                summary["total_passed"] += 1
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                logger.exception(
                    "%s | meteorite %s run_notify_meteorite_bot_blocked\n  %s: %s\n  Continuing to the next row",
                    cid, row_id, type(exc).__name__, exc,
                )
    finally:
        logger.debug("End notify meteorite loop after %s items", summary["total_processed"])
        clear_meteorite_batch(batch_id)
    return summary


@_with_log_debug
async def run_meteorite_retention(
    task: Dict[str, Any], *, debug: bool = False
) -> Dict[str, int]:
    """Dispatch runner: purge old LANDED + warn stale rows (AST-1562)."""
    cfg = METEORITE_RETENTION_CONFIG
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    now = datetime.now(timezone.utc)
    landed_cutoff = (now - timedelta(days=int(cfg["landed_purge_days"]))).isoformat()
    stale_cutoff = (now - timedelta(days=int(cfg["stale_list_days"]))).isoformat()
    summary = dict(_ZERO_SUMMARY)

    purge_states = list(METEORITE_STATES_RETENTION["purge_states"])
    logger.debug(
        "Calling list_meteorites_for_retention: [states=%s, older_than=%s]",
        purge_states, landed_cutoff,
    )
    landed_rows = list_meteorites_for_retention(
        states=purge_states, older_than=landed_cutoff, limit=batch_size
    )
    logger.debug("Response from list_meteorites_for_retention landed: %s", landed_rows)
    if landed_rows:
        ids = [int(r["id"]) for r in landed_rows]
        logger.debug("Beginning landed purge loop on %s items", len(ids))
        n = delete_meteorites_by_ids(ids)
        summary["total_processed"] += n
        summary["total_passed"] += n
        for row_id in ids:
            _meteorite_state_info(row_id, "purged", from_state="LANDED")
        logger.debug("End landed purge loop after %s items", n)

    stale_states = list(METEORITE_STATES_RETENTION["stale_list_states"])
    logger.debug(
        "Calling list_meteorites_for_retention: [states=%s, older_than=%s]",
        stale_states, stale_cutoff,
    )
    stale_rows = list_meteorites_for_retention(
        states=stale_states, older_than=stale_cutoff, limit=batch_size
    )
    logger.debug("Response from list_meteorites_for_retention stale: %s", stale_rows)
    logger.debug("Beginning stale meteorite loop on %s items", len(stale_rows))
    for row in stale_rows:
        summary["total_processed"] += 1
        row_id = int(row["id"])
        cid = str(row.get("candidate_id") or "")
        state = str(row.get("state") or "")
        changed = row.get("state_changed_at") or row.get("updated_at") or ""
        _row_miss(
            row_id,
            cid,
            f"still {state} since {changed}",
            "This row is not being purged",
        )
        summary["total_passed"] += 1
    logger.debug("End stale meteorite loop after %s items", len(stale_rows))

    return summary


def _normalize_apply_paste_content(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    if "<" in text and ">" in text:
        text = normalize_pasted_list_email_html(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
    return "\n\n".join(line.strip() for line in text.splitlines() if line.strip())


def _pick_single_bot_blocked_row(rows: List[dict]) -> Optional[dict]:
    if not rows:
        return None
    if len(rows) == 1:
        return rows[0]
    return max(rows, key=lambda r: int(r["id"]))


def find_meteorite_for_estelle_thread(
    *, candidate_id: str, thread_ts: str
) -> Optional[dict]:
    cid = (candidate_id or "").strip()
    anchor = (thread_ts or "").strip()
    if not cid or not anchor:
        return None
    matches = [
        row
        for row in list_meteorites_by_state("BOT_BLOCKED")
        if str(row.get("candidate_id") or "") == cid
        and str(row.get("estelle_thread_ts") or "").strip() == anchor
    ]
    return _pick_single_bot_blocked_row(matches)


def find_meteorite_bot_blocked_paste_source(*, candidate_id: str) -> Optional[dict]:
    cid = (candidate_id or "").strip()
    if not cid:
        return None
    matches = [
        row
        for row in list_meteorites_by_state("BOT_BLOCKED")
        if str(row.get("candidate_id") or "") == cid
        and str(row.get("source_kind") or "").strip() == "paste"
    ]
    return _pick_single_bot_blocked_row(matches)


@_with_log_debug
def apply_paste(meteorite_id: int, pasted_text: str, *, debug: bool = False) -> dict:
    row = get_meteorite(meteorite_id)
    if not row:
        _warn_item(
            f"meteorite {meteorite_id}",
            "not found",
            "This paste is not moving a row to READY",
        )
        return {"ok": False, "error": "not_found"}
    if row.get("state") != "BOT_BLOCKED":
        _warn_item(
            f"meteorite {meteorite_id} for {row.get('candidate_id')}",
            f"invalid_state {row.get('state')}",
            "This paste is not moving a row to READY",
        )
        return {
            "ok": False,
            "error": "invalid_state",
            "state": row.get("state"),
        }
    content = _normalize_apply_paste_content(pasted_text)
    if not content:
        _warn_item(
            f"meteorite {meteorite_id} for {row.get('candidate_id')}",
            "empty paste",
            "This paste is not moving a row to READY",
        )
        return {"ok": False, "error": "empty_paste"}
    update_meteorite(meteorite_id, content=content, state="READY", error=None)
    _meteorite_state_info(meteorite_id, "READY", from_state="BOT_BLOCKED")
    return {"ok": True, "meteorite_id": meteorite_id, "state": "READY"}


def _resolve_slack_dm_channel_for_candidate(candidate_id: str) -> Optional[str]:
    row = get_candidate((candidate_id or "").strip())
    if not row:
        return None
    cd = row.get("candidate_data") if isinstance(row.get("candidate_data"), dict) else {}
    contact = cd.get("contact") if isinstance(cd.get("contact"), dict) else {}
    uid = contact.get("slack_user_id")
    if not isinstance(uid, str) or not uid.strip():
        return None
    from src.data.contact_estelle_activity import load_estelle_activity_store

    store = load_estelle_activity_store()
    by = store.get("by_slack_user_id")
    if not isinstance(by, dict):
        return None
    activity = by.get(uid.strip())
    if not isinstance(activity, dict):
        return None
    channel = activity.get("last_channel")
    if isinstance(channel, str) and channel.startswith("D"):
        return channel
    return None


def _format_bot_blocked_dm(
    row: dict, *, nag_count: int, nag_limit: int, first: bool
) -> str:
    cfg = METEORITE_BOT_BLOCKED_NOTIFY_CONFIG
    link = (row.get("link") or "").strip() or "(no link)"
    tpl = cfg["dm_first_template"] if first else cfg["dm_nag_template"]
    return tpl.format(link=link, nag_count=nag_count, nag_limit=nag_limit)
