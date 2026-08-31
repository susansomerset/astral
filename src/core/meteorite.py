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
inbox owns fetch/archive. create_meteorite_job accepts optional stem= for legacy callers.
create_contact_meteorite (AST-1517 contact-task create) wraps scrape-or-text → create.
"""
from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timezone
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
    get_company,
    get_job,
    get_meteorite,
    get_meteorite_batch,
    insert_meteorite_rows,
    list_meteorites_by_source,
    list_meteorites_by_state,
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
    STAGE_METEORITE_CONFIG,
    TASK_CONFIG,
    TRACKER_CONFIG,
)
from src.utils.formatting import normalize_pasted_list_email_html
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)


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
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    existing = get_company(short_name)
    if existing is not None:
        if debug:
            log.debug_index(
                func="meteorite.ensure_meteorite_company",
                index=1,
                total=1,
                identifier=short_name,
                outcome="already-present",
            )
            log.debug_detail(f"candidate_id={candidate_id}")
            log.debug_detail(f"stem={resolved_stem}")
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
    if debug:
        log.debug_index(
            func="meteorite.ensure_meteorite_company",
            index=1,
            total=1,
            identifier=short_name,
            outcome="inserted",
        )
        log.debug_detail(f"candidate_id={candidate_id}")
        log.debug_detail(f"stem={resolved_stem}")
        log.debug_detail(f"company_state={METEORITE_CONFIG['company_state']}")
    return {"short_name": short_name, "inserted": True, "company": row}


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

    ensured = ensure_meteorite_company(candidate_id, stem=stem, debug=debug)
    short_name = ensured["short_name"]
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    state = METEORITE_CONFIG["job_create_state"]
    score = float(METEORITE_CONFIG["job_create_latest_score"])
    astral_job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    link = job_link.strip() if job_link and str(job_link).strip() else None

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

async def create_contact_meteorite(
    astral_candidate_id: str,
    param: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Contact-task: land meteorite from URL (scrape-first) or pasted page text."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    def _style_d(
        *,
        identifier: str,
        mode: str,
        param_for_detail: str,
        error: Optional[str] = None,
        created: Optional[Dict[str, Any]] = None,
        job_link: Optional[str] = None,
        page_status: Optional[str] = None,
    ) -> None:
        if not debug:
            return
        log.debug_index(
            func="meteorite.create_contact_meteorite",
            index=1,
            total=2,
            identifier=identifier[:80],
            outcome="found",
        )
        log.debug_detail(f"mode={mode}")
        for line in truncate_debug_content(f"param={param_for_detail}"):
            log.debug_detail(line)
        if error:
            log.debug_index(
                func="meteorite.create_contact_meteorite",
                index=2,
                total=2,
                identifier=identifier[:80],
                outcome=f"failed error={error}",
            )
            return
        log.debug_index(
            func="meteorite.create_contact_meteorite",
            index=2,
            total=2,
            identifier=identifier[:80],
            outcome=(
                f"recorded astral_job_id={(created or {}).get('astral_job_id')} "
                f"state={(created or {}).get('state')}"
            ),
        )
        log.debug_detail(f"company={(created or {}).get('company')}")
        log.debug_detail(f"job_link={job_link}")
        if page_status is not None:
            log.debug_detail(f"page_status={page_status}")

    cid = (astral_candidate_id or "").strip()
    if not cid:
        out: Dict[str, Any] = {
            "ok": False,
            "error": "no_candidate",
            "task_key": "create_contact_meteorite",
        }
        _style_d(
            identifier="no_candidate",
            mode="",
            param_for_detail=(param or ""),
            error="no_candidate",
        )
        return out

    raw = (param or "").strip()
    if not raw:
        out = {
            "ok": False,
            "error": "param_required",
            "task_key": "create_contact_meteorite",
        }
        _style_d(
            identifier=cid,
            mode="",
            param_for_detail="",
            error="param_required",
        )
        return out

    ident = raw[:80]
    scrape: Optional[Dict[str, Any]] = None
    if _contact_param_looks_like_url(raw):
        mode = "link"
        # Late-import: gazer imports create_meteorite_job at module top.
        from src.core.gazer import contact_task_gazer_scrape

        scrape = await contact_task_gazer_scrape(cid, raw, debug=debug)
        if not isinstance(scrape, dict) or not scrape.get("ok"):
            err = (
                (scrape.get("error") if isinstance(scrape, dict) else "scrape_failed")
                or "scrape_failed"
            )
            out = {
                "ok": False,
                "error": err,
                "task_key": "create_contact_meteorite",
                "mode": mode,
                "scrape": scrape if isinstance(scrape, dict) else None,
            }
            _style_d(
                identifier=ident,
                mode=mode,
                param_for_detail=raw,
                error=err,
            )
            return out
        visible = (scrape.get("visible_text") or "").strip()
        if not visible:
            out = {
                "ok": False,
                "error": "empty_visible_text",
                "task_key": "create_contact_meteorite",
                "mode": mode,
                "scrape": scrape,
            }
            _style_d(
                identifier=ident,
                mode=mode,
                param_for_detail=raw,
                error="empty_visible_text",
                page_status=scrape.get("page_status"),
            )
            return out
        html_body = visible
        job_link = (scrape.get("final_url") or scrape.get("url") or raw).strip()
    else:
        mode = "text"
        html_body = raw
        job_link = None

    try:
        created = create_meteorite_job(
            cid,
            html_body,
            job_link=job_link,
            debug=debug,
        )
    except Exception as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "task_key": "create_contact_meteorite",
            "mode": mode,
        }
        _style_d(
            identifier=ident,
            mode=mode,
            param_for_detail=raw,
            error=str(exc),
        )
        return out

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
    _style_d(
        identifier=ident,
        mode=mode,
        param_for_detail=raw,
        created=created,
        job_link=job_link,
        page_status=out.get("page_status"),
    )
    return out


async def _land_fetch_link_text(url: str, *, debug: bool = False) -> tuple[str, str]:
    """Return (visible_text, final_url) via Playwright; empty text on failure."""
    _ = debug
    try:
        result = await get_visible_text(url=url, return_final_url=True)
    except Exception:
        return ("", url)
    if isinstance(result, tuple):
        text, final_url = result
        return (text or ""), (final_url or url)
    return (result or ""), url


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
    log = get_logger(__name__)
    log.set_debug_flag(debug)

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
        return _err("candidate_id is required")
    cand = get_candidate(cid)
    if not cand:
        return _err(f"candidate not found: {cid}")

    # Late-import: consult loads is_meteorite_company at module top.
    from src.core.consult import invoke_stage_meteorite

    ctx = dict(cand) if isinstance(cand, dict) else {}
    ctx["astral_candidate_id"] = cid
    invoke = await invoke_stage_meteorite(
        cid, blob, source_kind=source_kind, source_id=source_id, ctx=ctx, debug=debug,
    )
    batch_id = invoke.get("batch_id")

    if not invoke.get("success"):
        if debug:
            log.debug_index(
                func="meteorite.stage_meteorite",
                index=1,
                total=1,
                identifier=cid,
                outcome="stage_invoke_failed",
            )
            log.debug_detail(f"error={invoke.get('error')!r} batch_id={batch_id!r}")
        return _err(invoke.get("error") or "stage invoke failed", batch_id=batch_id)

    stage_outcome = invoke["outcome"]
    kind = (source_kind or "").strip()
    sid = (source_id or "").strip()

    if stage_outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
        if debug:
            log.debug_index(
                func="meteorite.stage_meteorite",
                index=1,
                total=1,
                identifier=cid,
                outcome=str(stage_outcome),
            )
            log.debug_detail(
                f"source_kind={kind} source_id={sid} job_count=0 land=skip"
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
    if debug:
        log.debug_index(
            func="meteorite.stage_meteorite",
            index=1,
            total=1,
            identifier=cid,
            outcome=str(stage_outcome),
        )
        log.debug_detail(
            f"source_kind={kind} source_id={sid} job_count={len(jobs)} classify_only=1"
        )

    return {
        "outcome": stage_outcome,
        "stage_outcome": stage_outcome,
        "skipped": False,
        "jobs": jobs,
        "error": None,
        "batch_id": batch_id,
    }


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
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    if scraps is not None and not isinstance(scraps, list):
        raise ValueError("scraps must be a list or None")

    cid = (candidate_id or "").strip()
    if not cid:
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
            return {
                "outcome": err_key,
                "error": "scraps required (link and/or text)",
                "outcomes": [],
                "company": None,
                "company_inserted": False,
            }

    cand = get_candidate(cid)
    if not cand:
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
    enrich = await enrich_meteorite_land_packet(cid, work, ctx=ctx, debug=debug)
    if not enrich.get("success") or not enrich.get("jobs"):
        return {
            "outcome": err_key,
            "error": enrich.get("error") or "enrichment produced no jobs",
            "outcomes": [],
            "company": None,
            "company_inserted": False,
        }

    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    emp_key = METEORITE_CONFIG["employer_name_job_data_key"]
    outcomes: List[Dict[str, Any]] = []
    enriched_jobs = enrich["jobs"]
    n = len(enriched_jobs)
    first_company: Optional[str] = None
    first_company_inserted = False
    for i, row in enumerate(enriched_jobs, start=1):
        found_link = row.get("job_link") or ""
        found_title = row.get("job_title") or ""
        found_jd = row.get("jd_text") or ""
        found_emp = row.get("employer_name") or ""
        row_stem = (row.get("company_stem") or "").strip() if isinstance(row.get("company_stem"), str) else ""
        try:
            ensured_row = ensure_meteorite_company(cid, stem=row_stem or None, debug=debug)
            row_company = ensured_row["short_name"]
            if first_company is None:
                first_company = row_company
                first_company_inserted = bool(ensured_row["inserted"])
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
            outcomes.append(save)
            if debug:
                recorded = save.get("job") or {}
                rec_jd = len((recorded.get("job_data") or {}).get(jd_key, "") or "")
                rec_emp = (recorded.get("job_data") or {}).get(emp_key) or ""
                log.debug_index(
                    func="meteorite.land_meteorite",
                    index=i,
                    total=n,
                    identifier=save.get("astral_job_id") or cid,
                    outcome=str(save.get("outcome") or err_key),
                )
                log.debug_detail(
                    f"found link={found_link!r} title={found_title!r} jd_chars={len(found_jd)} "
                    f"employer={found_emp!r} stem={row_stem!r} company={row_company!r} | "
                    f"recorded link={recorded.get('job_link')!r} "
                    f"title={recorded.get('job_title')!r} jd_chars={rec_jd} employer={rec_emp!r}"
                )
        except (ValueError, RuntimeError) as e:
            outcomes.append({
                "outcome": err_key,
                "error": str(e),
                "astral_job_id": None,
            })
            if debug:
                log.debug_index(
                    func="meteorite.land_meteorite",
                    index=i,
                    total=n,
                    identifier=cid,
                    outcome=err_key,
                )
                log.debug_detail(f"error={e!r}")

    rollup = _land_rollup_outcome(outcomes)
    top_error = None
    if rollup == err_key and not any(
        o.get("outcome") in (
            METEORITE_CONFIG["land_outcome_created"],
            METEORITE_CONFIG["land_outcome_duplicate_skip"],
            METEORITE_CONFIG["land_outcome_superseded"],
        )
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

def _sanitize_meteorite_monitor_subject(raw: str) -> str:
    text = str(raw or "")
    for ch in ("\r", "\n", "\t"):
        text = text.replace(ch, " ")
    text = " ".join(text.split()).strip()
    limit = int(METEORITE_MONITORING_CONFIG["subject_max_len"])
    if len(text) <= limit:
        return text
    if limit <= 1:
        return "…"
    return text[: limit - 1] + "…"


def log_meteorite_inbox_classify(
    *,
    from_address: str,
    message_id: str,
    internal_date_ms: int,
    subject: str,
    candidate_id: str,
    classify_outcome: str,
    job_count: int,
) -> None:
    line = METEORITE_MONITORING_CONFIG["inbox_classify_line"].format(
        from_address=(from_address or "")[:120],
        message_id=(message_id or "")[:80],
        internal_date_ms=int(internal_date_ms or 0),
        subject=_sanitize_meteorite_monitor_subject(subject),
        candidate_id=(candidate_id or "").strip(),
        classify_outcome=(classify_outcome or "").strip(),
        job_count=int(job_count or 0),
    )
    logger.info(line)


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


def _check_inbox_dbg(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )


def _check_inbox_detail(debug: bool, line: str) -> None:
    if debug:
        logger.debug_detail(line)


def _monitor_message_fields(msg: dict, payload: dict | None = None) -> dict[str, Any]:
    payload = payload or {}
    return {
        "from_address": (msg.get("from_address") or payload.get("from_address") or "")[:120],
        "message_id": msg.get("id") or "",
        "internal_date_ms": int(msg.get("internal_date_ms") or 0),
        "subject": (payload.get("subject") or msg.get("subject") or ""),
    }


async def check_inbox(task: dict, *, debug: bool = False) -> dict[str, int]:
    """Candidate-bound mailbox: aliases → fetch → classify → fan-out → archive."""
    cid = str((task or {}).get("candidate_id") or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if debug:
        logger.set_debug_flag(True)
        _check_inbox_dbg(debug, index=1, total=1, mid=cid, outcome="run-start")
        env_user = (os.environ.get("GMAIL_USER") or "").casefold()
        expected = (METEORITE_EMAIL_MAILBOX_CONFIG["account_address"] or "").casefold()
        if env_user != expected:
            _check_inbox_detail(True, f"account_mismatch GMAIL_USER={env_user!r} expected={expected!r}")

    aliases = email_aliases_for_candidate(cid)
    messages = fetch_candidate_email(aliases, debug=debug)
    n = len(messages)
    processed = passed = failed = errors = 0

    for i, msg in enumerate(messages, start=1):
        mid = msg.get("id") or ""
        monitor_base = _monitor_message_fields(msg)
        try:
            _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="found")
            _check_inbox_detail(debug, f"from_address={monitor_base['from_address'][:120]}")

            existing = list_meteorites_by_source("email", mid)
            if existing:
                log_meteorite_inbox_classify(
                    **monitor_base,
                    candidate_id=cid,
                    classify_outcome=METEORITE_MONITORING_CONFIG["outcome_already_ingested"],
                    job_count=len(existing),
                )
                try:
                    archive_candidate_email(mid)
                    processed += 1
                    passed += 1
                    _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="archived")
                except Exception as exc:
                    errors += 1
                    processed += 1
                    _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="error")
                    _check_inbox_detail(debug, f"archive_error={type(exc).__name__}")
                continue

            payload = get_message_html(mid)
            monitor_base = _monitor_message_fields(msg, payload)
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

            invoke = await invoke_stage_meteorite(
                cid,
                blob,
                source_kind="email",
                source_id=mid,
                ctx=ctx,
                debug=debug,
            )

            if not invoke.get("success"):
                log_meteorite_inbox_classify(
                    **monitor_base,
                    candidate_id=cid,
                    classify_outcome="classify_failed",
                    job_count=0,
                )
                errors += 1
                processed += 1
                _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="error")
                _check_inbox_detail(debug, f"classify_error={invoke.get('error')!r}")
                continue

            stage_outcome = invoke["outcome"]
            if stage_outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
                log_meteorite_inbox_classify(
                    **monitor_base,
                    candidate_id=cid,
                    classify_outcome=str(stage_outcome),
                    job_count=0,
                )
                try:
                    archive_candidate_email(mid)
                    processed += 1
                    passed += 1
                    _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome=str(stage_outcome))
                except Exception as exc:
                    errors += 1
                    processed += 1
                    _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="error")
                    _check_inbox_detail(debug, f"archive_error={type(exc).__name__}")
                continue

            row_dicts, map_err = _map_classify_jobs_to_meteorite_rows(
                stage_outcome,
                invoke.get("jobs") or [],
                candidate_id=cid,
                source_kind="email",
                source_id=mid,
            )
            if map_err:
                log_meteorite_inbox_classify(
                    **monitor_base,
                    candidate_id=cid,
                    classify_outcome="map_failed",
                    job_count=0,
                )
                errors += 1
                processed += 1
                _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="error")
                _check_inbox_detail(debug, f"map_error={map_err!r}")
                continue

            job_list = invoke.get("jobs") or []
            ids = insert_meteorite_rows(row_dicts)
            if len(ids) != len(row_dicts) or len(row_dicts) != len(job_list):
                log_meteorite_inbox_classify(
                    **monitor_base,
                    candidate_id=cid,
                    classify_outcome="map_failed",
                    job_count=0,
                )
                errors += 1
                processed += 1
                _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="error")
                _check_inbox_detail(
                    debug,
                    f"insert_count_mismatch ids={len(ids)} rows={len(row_dicts)} jobs={len(job_list)}",
                )
                continue

            log_meteorite_inbox_classify(
                **monitor_base,
                candidate_id=cid,
                classify_outcome=str(stage_outcome),
                job_count=len(ids),
            )
            try:
                archive_candidate_email(mid)
                processed += 1
                passed += 1
                _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="archived")
                _check_inbox_detail(debug, f"inserted={len(ids)} outcome={stage_outcome!r}")
            except Exception as exc:
                errors += 1
                processed += 1
                _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="error")
                _check_inbox_detail(debug, f"archive_error={type(exc).__name__}")

        except Exception as exc:
            errors += 1
            processed += 1
            _check_inbox_dbg(debug, index=i, total=n, mid=mid, outcome="error")
            _check_inbox_detail(debug, f"message_error={type(exc).__name__}: {exc}")
            for line in truncate_debug_content(str(exc)):
                _check_inbox_detail(debug, line)

    update_candidate_last_email_check(cid)
    if debug:
        _check_inbox_dbg(debug, index=1, total=1, mid=cid, outcome="run-complete")
        _check_inbox_detail(debug, "last_email_check=stamped")
        _check_inbox_detail(
            debug,
            f"summary={{total_processed={processed}, total_passed={passed}, "
            f"total_failed={failed}, total_errors={errors}}}",
        )

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


def log_meteorite_row_transition(
    *,
    row_id: int,
    candidate_id: str,
    state: str,
    task_key: str = "",
    link: str = "",
    astral_job_id: str = "",
    error: str = "",
) -> None:
    """Always-on info row-transition line (AST-1560); not Style D."""
    cfg = METEORITE_MONITORING_CONFIG
    if state == "BOT_BLOCKED":
        fmt = cfg["row_bot_blocked_line"]
        line = fmt.format(
            row_id=row_id,
            candidate_id=candidate_id,
            link=link or "",
        )
    elif state == "LANDED":
        fmt = cfg["row_landed_line"]
        line = fmt.format(
            row_id=row_id,
            candidate_id=candidate_id,
            astral_job_id=astral_job_id or "",
        )
    elif state == "ERROR":
        fmt = cfg["row_error_line"]
        line = fmt.format(
            row_id=row_id,
            candidate_id=candidate_id,
            task_key=task_key or "",
            error=error or "",
        )
    else:
        return
    get_logger(__name__).info(line)


async def run_stage_meteorite(task: Dict[str, Any], *, debug: bool = False) -> Dict[str, int]:
    """Dispatch runner: NEW → SCRAPE_LINK | READY (AST-1560)."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    task_key = str((task or {}).get("task_key") or cfg["stage_task_key"])
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")

    summary = dict(_ZERO_SUMMARY)
    claim_meteorite_batch(batch_id, cfg["stage_trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    if not rows:
        return summary

    try:
        for i, row in enumerate(rows, start=1):
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            try:
                outcome = (row.get("classify_outcome") or "").strip()
                if not outcome:
                    update_meteorite(row_id, state="ERROR", error="missing classify_outcome")
                    log_meteorite_row_transition(
                        row_id=row_id,
                        candidate_id=cid,
                        state="ERROR",
                        task_key=task_key,
                        error="missing classify_outcome",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue
                if outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
                    update_meteorite(row_id, state="ERROR", error="skip outcome on row")
                    log_meteorite_row_transition(
                        row_id=row_id,
                        candidate_id=cid,
                        state="ERROR",
                        task_key=task_key,
                        error="skip outcome on row",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue
                if outcome in STAGE_METEORITE_CONFIG["url_scrape_outcomes"]:
                    link = (row.get("link") or "").strip()
                    if not _is_http_url(link):
                        update_meteorite(row_id, state="ERROR", error="missing link")
                        log_meteorite_row_transition(
                            row_id=row_id,
                            candidate_id=cid,
                            state="ERROR",
                            task_key=task_key,
                            error="missing link",
                        )
                        summary["total_failed"] += 1
                        summary["total_errors"] += 1
                        continue
                    update_meteorite(row_id, state="SCRAPE_LINK", link=link)
                    summary["total_passed"] += 1
                    if debug:
                        log.debug_index(
                            func="meteorite.run_stage_meteorite",
                            index=i,
                            total=len(rows),
                            identifier=str(row_id),
                            outcome="SCRAPE_LINK",
                        )
                    continue
                if outcome in STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]:
                    content = (row.get("content") or "").strip()
                    if not content:
                        update_meteorite(row_id, state="ERROR", error="missing content")
                        log_meteorite_row_transition(
                            row_id=row_id,
                            candidate_id=cid,
                            state="ERROR",
                            task_key=task_key,
                            error="missing content",
                        )
                        summary["total_failed"] += 1
                        summary["total_errors"] += 1
                        continue
                    update_meteorite(row_id, state="READY")
                    summary["total_passed"] += 1
                    if debug:
                        log.debug_index(
                            func="meteorite.run_stage_meteorite",
                            index=i,
                            total=len(rows),
                            identifier=str(row_id),
                            outcome="READY",
                        )
                    continue
                err = f"unhandled classify_outcome: {outcome}"
                update_meteorite(row_id, state="ERROR", error=err)
                log_meteorite_row_transition(
                    row_id=row_id,
                    candidate_id=cid,
                    state="ERROR",
                    task_key=task_key,
                    error=err,
                )
                summary["total_failed"] += 1
                summary["total_errors"] += 1
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                log.warning("[meteorite] run_stage_meteorite row=%s failed: %s", row_id, exc)
    finally:
        clear_meteorite_batch(batch_id)
    return summary


async def run_scrape_meteorite(task: Dict[str, Any], *, debug: bool = False) -> Dict[str, int]:
    """Dispatch runner: SCRAPE_LINK → READY | BOT_BLOCKED | ERROR (AST-1560)."""
    from src.core.gazer import _CONTACT_PAGE_STATUS, _classify_jd

    log = get_logger(__name__)
    log.set_debug_flag(debug)
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    task_key = str((task or {}).get("task_key") or cfg["scrape_task_key"])
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")
    status_map = cfg["scrape_page_status_states"]

    summary = dict(_ZERO_SUMMARY)
    claim_meteorite_batch(batch_id, cfg["scrape_trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    if not rows:
        return summary

    try:
        for i, row in enumerate(rows, start=1):
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            link = (row.get("link") or "").strip()
            try:
                if not _is_http_url(link):
                    update_meteorite(row_id, state="ERROR", error="missing link")
                    log_meteorite_row_transition(
                        row_id=row_id,
                        candidate_id=cid,
                        state="ERROR",
                        task_key=task_key,
                        error="missing link",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue

                visible_text, final_url = await _land_fetch_link_text(link, debug=debug)
                page_status = _CONTACT_PAGE_STATUS.get(_classify_jd(visible_text), "missing")

                if page_status == "blocked":
                    update_meteorite(row_id, state=status_map["blocked"])
                    log_meteorite_row_transition(
                        row_id=row_id,
                        candidate_id=cid,
                        state="BOT_BLOCKED",
                        link=link,
                    )
                    summary["total_passed"] += 1
                    if debug:
                        log.debug_index(
                            func="meteorite.run_scrape_meteorite",
                            index=i,
                            total=len(rows),
                            identifier=link[:80],
                            outcome="BOT_BLOCKED",
                        )
                    continue

                if page_status == "ok" and visible_text.strip():
                    update_meteorite(
                        row_id,
                        state="READY",
                        content=visible_text,
                        link=final_url or link,
                    )
                    summary["total_passed"] += 1
                    if debug:
                        log.debug_index(
                            func="meteorite.run_scrape_meteorite",
                            index=i,
                            total=len(rows),
                            identifier=link[:80],
                            outcome="READY",
                        )
                    continue

                err = "empty visible text" if page_status == "ok" else f"scrape_{page_status}"
                update_meteorite(row_id, state=status_map.get(page_status, "ERROR"), error=err)
                log_meteorite_row_transition(
                    row_id=row_id,
                    candidate_id=cid,
                    state="ERROR",
                    task_key=task_key,
                    error=err,
                )
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                if debug:
                    log.debug_index(
                        func="meteorite.run_scrape_meteorite",
                        index=i,
                        total=len(rows),
                        identifier=link[:80],
                        outcome="ERROR",
                    )
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                log.warning("[meteorite] run_scrape_meteorite row=%s failed: %s", row_id, exc)
    finally:
        clear_meteorite_batch(batch_id)
    return summary


async def run_land_meteorite(task: Dict[str, Any], *, debug: bool = False) -> Dict[str, int]:
    """Dispatch runner: READY → LANDED + job create (AST-1560)."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    task_key = str((task or {}).get("task_key") or cfg["land_task_key"])
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
    claim_meteorite_batch(batch_id, cfg["land_trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    if not rows:
        return summary

    try:
        for i, row in enumerate(rows, start=1):
            summary["total_processed"] += 1
            row_id = int(row["id"])
            cid = str(row.get("candidate_id") or "")
            try:
                content = (row.get("content") or "").strip()
                if not content:
                    update_meteorite(row_id, state="ERROR", error="missing content")
                    log_meteorite_row_transition(
                        row_id=row_id,
                        candidate_id=cid,
                        state="ERROR",
                        task_key=task_key,
                        error="missing content",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue

                ensured = ensure_meteorite_company(cid, debug=debug)
                existing_link = (row.get("link") or "").strip()
                job_link = existing_link if _is_http_url(existing_link) else None
                save = tracker.save_meteorite_job(
                    cid,
                    company=ensured["short_name"],
                    job_data={jd_key: content},
                    job_link=job_link,
                    company_job_id=None,
                    employer_name=None,
                    debug=debug,
                )
                if save.get("outcome") in ok_outcomes:
                    job_id = str(save.get("astral_job_id") or "")
                    update_meteorite(row_id, state="LANDED", astral_job_id=job_id)
                    log_meteorite_row_transition(
                        row_id=row_id,
                        candidate_id=cid,
                        state="LANDED",
                        astral_job_id=job_id,
                    )
                    summary["total_passed"] += 1
                    if debug:
                        log.debug_index(
                            func="meteorite.run_land_meteorite",
                            index=i,
                            total=len(rows),
                            identifier=job_id or str(row_id),
                            outcome="LANDED",
                        )
                    continue

                err = str(save.get("error") or "land failed")
                update_meteorite(row_id, state="ERROR", error=err)
                log_meteorite_row_transition(
                    row_id=row_id,
                    candidate_id=cid,
                    state="ERROR",
                    task_key=task_key,
                    error=err,
                )
                summary["total_failed"] += 1
                summary["total_errors"] += 1
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                log.warning("[meteorite] run_land_meteorite row=%s failed: %s", row_id, exc)
    finally:
        clear_meteorite_batch(batch_id)
    return summary


async def run_notify_meteorite_bot_blocked(
    task: Dict[str, Any], *, debug: bool = False
) -> Dict[str, int]:
    """Dispatch runner: BOT_BLOCKED → Estelle DM + nag → ABANDONED (AST-1561)."""
    log = get_logger(__name__)
    log.set_debug_flag(debug)
    cfg = METEORITE_BOT_BLOCKED_NOTIFY_CONFIG
    task_key = str((task or {}).get("task_key") or cfg["task_key"])
    batch_size = int((task or {}).get("batch_size") or cfg["batch_size"])
    batch_id = str((task or {}).get("entity_batch_id") or "").strip()
    if not batch_id:
        raise ValueError("entity_batch_id is required")

    summary = dict(_ZERO_SUMMARY)
    claim_meteorite_batch(batch_id, cfg["trigger_state"], limit=batch_size)
    rows = get_meteorite_batch(batch_id)
    if not rows:
        return summary

    nag_limit = int(cfg["nag_limit"])
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
                    summary["total_passed"] += 1
                    continue

                channel = _resolve_slack_dm_channel_for_candidate(cid)
                if not channel:
                    update_meteorite(row_id, error="no slack dm channel")
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

                resp = contact_post_message(
                    channel=channel, text=message, thread_ts=None, debug=debug
                )
                if not resp.get("ok"):
                    err = str(resp.get("error") or "slack post failed")
                    update_meteorite(row_id, error=err)
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
                summary["total_passed"] += 1
            except Exception as exc:
                summary["total_failed"] += 1
                summary["total_errors"] += 1
                log.warning(
                    "[meteorite] run_notify_meteorite_bot_blocked row=%s failed: %s",
                    row_id,
                    exc,
                )
    finally:
        clear_meteorite_batch(batch_id)
    return summary


async def run_meteorite_retention(
    task: Dict[str, Any], *, debug: bool = False
) -> Dict[str, int]:
    """Dispatch runner: purge old LANDED + info-list stale rows (AST-1562)."""
    return dict(_ZERO_SUMMARY)


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


def apply_paste(meteorite_id: int, pasted_text: str, *, debug: bool = False) -> dict:
    log = get_logger(__name__)
    log.set_debug_flag(debug)
    row = get_meteorite(meteorite_id)
    if not row:
        return {"ok": False, "error": "not_found"}
    if row.get("state") != "BOT_BLOCKED":
        return {
            "ok": False,
            "error": "invalid_state",
            "state": row.get("state"),
        }
    content = _normalize_apply_paste_content(pasted_text)
    if not content:
        return {"ok": False, "error": "empty_paste"}
    update_meteorite(meteorite_id, content=content, state="READY", error=None)
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
