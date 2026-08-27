"""
Meteorite placeholder company ensure, legacy create, and public land_meteorite (AST-1470 / AST-1493 / AST-1495).

Lazy-insert stem-keyed companies into METEORITE from METEORITE_CONFIG (default
stem → meteorite-<candidate_id>). Track = company state METEORITE or legacy
short_name_prefix. Public entry is land_meteorite: scraps → optional Playwright
visible text → qualify_meteorite packet enrich → per-row Ruth company_stem ensure
→ tracker.save_meteorite_job. No email/Gmail/mailbox I/O here — inbox and Contact
call land (siblings). create_meteorite_job accepts optional stem= for legacy callers.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.candidate import get_candidate
from src.core import tracker
from src.data.database import get_company, get_job, save_company, save_job
from src.external.playwright import get_visible_text
from src.utils.config import METEORITE_CONFIG, TASK_CONFIG, TRACKER_CONFIG
from src.utils.logging import get_logger


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
