"""
Meteorite placeholder company ensure, legacy create, and public land_meteorite (AST-1470 / AST-1493 / AST-1495).

Dispatch `stage_meteorite` / `scrape_meteorite` / `land_meteorite` rows (AST-1560) are table
transition runners — not Ruth classify hops; dispatcher custom branch only.

Lazy-insert stem-keyed companies into METEORITE from METEORITE_CONFIG (default
stem → meteorite-<candidate_id>). Track = company state METEORITE or legacy
short_name_prefix. Public stage_meteorite (AST-1530 / AST-1560): classify blob+source handle
only — table ingress uses dispatch transition runners for map/land. Public land_meteorite:
scraps → optional Playwright visible text → qualify_meteorite packet enrich →
per-row Ruth company_stem ensure → tracker.save_meteorite_job. check_inbox (AST-1559):
aliases → fetch → inline classify → fan-out staging rows → archive; no Gmail I/O here —
inbox owns fetch/archive.
create_meteorite_job accepts optional stem= for legacy callers.
create_contact_meteorite (AST-1517 contact-task create) wraps scrape-or-text → create.
"""
from __future__ import annotations

import functools
import inspect
import os
import re
import uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
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
from src.external.telescope import get_visible_text
from src.utils.config import (
    METEORITE_BOT_BLOCKED_NOTIFY_CONFIG,
    METEORITE_CONFIG,
    METEORITE_EMAIL_MAILBOX_CONFIG,
    METEORITE_INGRESS_DISPATCH_CONFIG,
    METEORITE_MONITORING_CONFIG,
    STAGE_METEORITE_CONFIG,
    TASK_CONFIG,
    TRACKER_CONFIG,
    format_contact_timezone_clock,
    format_job_link_breadcrumb,
)
from src.utils.formatting import normalize_pasted_list_email_html, uuid_path_segment_from_url
from src.utils.logging import get_logger, log_batch_id, log_debug

logger = get_logger(__name__)


def _hold_log_batch(batch_id: str):
    """Stamp log_batch_id only when a parent dispatch batch is not already set."""
    if log_batch_id.get():
        return None
    return log_batch_id.set(batch_id)


def _resolve_company_job_id(ai_company_job_id: str, job_link: str) -> str:
    """Prefer non-empty AI company_job_id; else UUID path segment from job_link; else ''."""
    ai = (ai_company_job_id or "").strip()
    if ai:
        return ai
    link = (job_link or "").strip()
    if not link:
        return ""
    fallback = uuid_path_segment_from_url(link, TRACKER_CONFIG["uuid_path_segment_pattern"])
    return fallback or ""


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


def _optional_real_company_id(
    *, company_stem: Optional[str], candidate_id: str
) -> Optional[str]:
    """Real employer short_name only — never invent meteorite placeholders (AST-1702)."""
    _ = candidate_id
    stem = (company_stem or "").strip()
    if not stem:
        return None
    if stem in (
        METEORITE_CONFIG["default_stem"],
        METEORITE_CONFIG["meteorite_self_stem"],
    ):
        return None
    row = get_company(stem)
    if row is None:
        return None
    if (row.get("state") or "") == METEORITE_CONFIG["company_state"]:
        return None
    return stem


def _append_jd(existing: str, addition: str) -> str:
    a = (existing or "").strip()
    b = (addition or "").strip()
    if not b:
        return a
    if not a:
        return b
    return f"{a}\n\n{b}"


def _insert_paste_meteorite_parent(
    candidate_id: str,
    *,
    content: Optional[str] = None,
    link: Optional[str] = None,
) -> int:
    """Insert a paste staging row and mark READY so land can parent to it (AST-1702)."""
    logger.debug(
        "Calling insert_meteorite_rows: [candidate_id=%s, source_kind=paste]",
        candidate_id,
    )
    ids = insert_meteorite_rows(
        [
            {
                "candidate_id": candidate_id,
                "source_kind": "paste",
                "source_id": str(uuid.uuid4()),
                "state": "NEW",
                "content": content,
                "link": link,
                "classify_outcome": None,
            }
        ]
    )
    logger.debug("Response from insert_meteorite_rows: %s", ids)
    mid = int(ids[0])
    update_meteorite(mid, state="READY")
    return mid


async def _land_link_check_append(
    scrap: Dict[str, Any], *, candidate_id: str = "", debug: bool = False
) -> None:
    """Fetch thin-body http link; bot-block continues land; ok text is appended (AST-1702)."""
    existing_body = _land_scrap_body(scrap)
    link = (scrap.get("job_link") or "").strip() if isinstance(scrap.get("job_link"), str) else ""
    min_jd = int(TASK_CONFIG["qualify_meteorite"]["min_jd_chars"])
    if not _is_http_url(link) or len(existing_body) >= min_jd:
        return

    visible, final_url = await _land_fetch_link_text(link, debug=debug)
    from src.core.gazer import _CONTACT_PAGE_STATUS, _classify_jd

    page_status = _CONTACT_PAGE_STATUS.get(_classify_jd(visible), "missing")
    if page_status == "blocked":
        logger.warning(
            "%s — land link bot-block at %s\n  Land continuing without scraped JD",
            candidate_id or "land_meteorite",
            link,
        )
        return
    if page_status == "ok" and (visible or "").strip():
        scrap["content"] = _append_jd(existing_body, visible.strip())
        if final_url:
            scrap["job_link"] = final_url


def _electronic_contact_from_job(job: Dict[str, Any]) -> Optional[str]:
    """Normalize Ruth jobs[] electronic_contact → meteorite column value (or None)."""
    key = STAGE_METEORITE_CONFIG["electronic_contact_response_key"]
    raw = job.get(key)
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    return text or None


def _soft_persist_meteorite_electronic_contact(
    meteorite_id: int,
    contact: Optional[str],
    *,
    who: Any,
) -> Optional[str]:
    """Best-effort contact write after a good insert/transition. Warns; never fails the row."""
    col = METEORITE_CONFIG["electronic_contact_column"]
    try:
        update_meteorite(int(meteorite_id), **{col: contact})
        row = get_meteorite(int(meteorite_id))
        recorded = (row or {}).get(col)
        return recorded if isinstance(recorded, str) else recorded
    except Exception as exc:
        _warn_item(
            who,
            f"{col} persist failed: {type(exc).__name__}: {exc}",
            "This meteorite row continues without a contact write",
        )
        return None


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
    meteorite_id: Optional[Any] = None,
    job_link: Optional[str] = None,
    company_id: Optional[str] = None,
    debug: bool = False,
) -> dict[str, Any]:
    """Create/supersede a job under a meteorite-row parent (AST-1702).

    When meteorite_id is omitted, inserts a paste staging row so gazer/contact
    callers keep working without ensure_meteorite_company as job parent.
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")
    if not isinstance(html_body, str) or not html_body.strip():
        raise ValueError("html_body is required")

    cand = get_candidate(candidate_id)
    if not cand:
        raise ValueError(f"candidate not found: {candidate_id}")

    link = job_link.strip() if job_link and str(job_link).strip() else None
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    state = METEORITE_CONFIG["job_create_state"]
    score = float(METEORITE_CONFIG["job_create_latest_score"])

    if meteorite_id is not None and str(meteorite_id).strip():
        mid = int(meteorite_id) if not isinstance(meteorite_id, int) else meteorite_id
        mid = int(mid)
    else:
        mid = _insert_paste_meteorite_parent(
            candidate_id, content=html_body, link=link
        )

    mrow = get_meteorite(mid)
    if mrow is None:
        raise RuntimeError(f"meteorite missing after parent resolve: {mid}")
    existing_link = (mrow.get("link") or "").strip()
    if link and not existing_link:
        update_meteorite(mid, link=link)
        existing_link = link
    inherited = existing_link or link or None
    emp = company_id if company_id is not None else None
    if emp is not None:
        emp = (emp or "").strip() or None
    else:
        emp = None

    logger.debug(
        "Calling tracker.save_meteorite_job: [candidate_id=%s, meteorite_id=%s]",
        candidate_id, mid,
    )
    save = tracker.save_meteorite_job(
        candidate_id,
        meteorite_id=mid,
        company_id=emp,
        job_data={jd_key: html_body},
        job_link=inherited,
        company_job_id=None,
        employer_name=None,
        debug=debug,
    )
    logger.debug("Response from tracker.save_meteorite_job: %s", save)
    row = save.get("job") or get_job(save.get("astral_job_id") or "")
    if row is None:
        raise RuntimeError(f"meteorite job missing after save: {save.get('astral_job_id')}")
    astral_job_id = str(save.get("astral_job_id") or row.get("astral_job_id") or "")
    if save.get("outcome") == METEORITE_CONFIG["land_outcome_created"]:
        update_meteorite(mid, state="LANDED", astral_job_id=astral_job_id)
        _entity_info(
            astral_job_id, "job", METEORITE_CONFIG["land_outcome_created"], state
        )
    return {
        "astral_job_id": astral_job_id,
        "company_id": row.get("company_id"),
        "meteorite_id": mid,
        "state": row.get("state") or state,
        "latest_score": row.get("latest_score") if row.get("latest_score") is not None else score,
        "company_inserted": False,
        "job": row,
        "outcome": save.get("outcome"),
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


@_with_log_debug
async def enrich_meteorite_land_packet(
    candidate_id: str,
    scraps: List[Dict[str, Any]],
    *,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Pre-create land packet enrich via qualify_meteorite do_task (AST-1470).

    No claim, no initialize_job, no state transition — dispatch qualify_meteorite
    still owns METEORITE_NEW → METEORITE_QUALIFIED.
    """
    from src.core.agent import do_task

    cid = (candidate_id or "").strip()
    if not cid:
        return {"success": False, "error": "candidate_id is required", "jobs": []}
    if not isinstance(scraps, list) or not scraps:
        return {"success": False, "error": "scraps is required", "jobs": []}

    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    rows: List[Dict[str, Any]] = []
    for raw in scraps:
        if not isinstance(raw, dict):
            continue
        link = (raw.get("job_link") or "").strip() if isinstance(raw.get("job_link"), str) else ""
        body = _land_scrap_body(raw)
        if not link and not body:
            continue
        emp = raw.get("employer_name")
        emp_s = emp.strip() if isinstance(emp, str) else ""
        rows.append({
            "job_link": link,
            "content": body,
            "employer_name": emp_s,
        })
    if not rows:
        return {"success": False, "error": "no usable scraps (need link or text)", "jobs": []}

    task_key = "qualify_meteorite"
    live_lines = [
        f"{i:03d}: job_link: {r['job_link']}\nCONTENT:\n{r['content']}"
        for i, r in enumerate(rows)
    ]
    live_content = "METEORITE JOBS:\n" + "\n".join(live_lines)

    # Stub batch_entities (no astral_job_id) so decode helpers peeking ctx stay safe.
    batch_entities = [
        {"job_link": r["job_link"] or None, "job_data": {jd_key: r["content"]}}
        for r in rows
    ]
    task_ctx: Dict[str, Any] = {
        **(ctx or {}),
        "astral_candidate_id": cid,
        "batch_size": len(rows),
        "batch_entities": batch_entities,
    }
    if ctx and ctx.get("candidate_data") is not None:
        task_ctx["candidate_data"] = ctx["candidate_data"]

    batch_id = f"{task_key}-land-{uuid.uuid4()}"
    do_index = f"{task_key}_batch_{batch_id}"
    token = _hold_log_batch(batch_id)
    try:
        logger.debug(
            "Calling agent.do_task: [task_key=%s, index=%s, scraps=%s]",
            task_key, do_index, len(rows),
        )
        result = await do_task(
            task_key=task_key,
            live_content=live_content,
            index=do_index,
            ctx=task_ctx,
            debug=debug,
        )
        logger.debug("Response from agent.do_task: %s", result)

        if not result.get("success"):
            logger.debug("enrich_failed batch_id=%s error=%r", batch_id, result.get("error"))
            logger.warning(
                "%s — land packet enrich failed: %s\n  Jobs are not landing from this packet",
                cid, result.get("error") or "do_task failed",
            )
            return {
                "success": False,
                "error": result.get("error") or "do_task failed",
                "jobs": [],
                "raw": result,
                "batch_id": batch_id,
            }

        parsed = result.get("parsed_response") if isinstance(result.get("parsed_response"), dict) else {}
        response_jobs = parsed.get("jobs") if isinstance(parsed.get("jobs"), list) else []
        out_jobs: List[Dict[str, Any]] = []
        for i, scrap in enumerate(rows):
            rj = response_jobs[i] if i < len(response_jobs) and isinstance(response_jobs[i], dict) else {}
            ruth_link = (rj.get("job_link") or "").strip() if isinstance(rj.get("job_link"), str) else ""
            job_link = ruth_link or scrap["job_link"]
            ai_cid = (rj.get("company_job_id") or "").strip() if isinstance(rj.get("company_job_id"), str) else ""
            company_job_id = _resolve_company_job_id(ai_cid, job_link)
            job_title = (rj.get("job_title") or "").strip() if isinstance(rj.get("job_title"), str) else ""
            jd_text = (rj.get("jd_text") or "").strip() if isinstance(rj.get("jd_text"), str) else ""
            ruth_emp = (rj.get("employer_name") or "").strip() if isinstance(rj.get("employer_name"), str) else ""
            employer_name = ruth_emp or scrap["employer_name"]
            stem_key = TASK_CONFIG["qualify_meteorite"]["company_stem_response_key"]
            ruth_stem = (rj.get(stem_key) or "").strip() if isinstance(rj.get(stem_key), str) else ""
            out_jobs.append({
                "company_job_id": company_job_id,
                "job_title": job_title,
                "job_link": job_link,
                "jd_text": jd_text,
                "employer_name": employer_name,
                "company_stem": ruth_stem,
                "scrap_index": i,
            })
            logger.debug(
                "enriched %s/%s link=%r content_chars_in=%s jd_chars=%s employer_name=%s company_stem=%r",
                i + 1, len(rows), job_link, len(scrap["content"]), len(jd_text),
                "yes" if employer_name else "no", ruth_stem,
            )

        return {"success": True, "jobs": out_jobs, "error": None, "batch_id": batch_id}
    finally:
        if token is not None:
            log_batch_id.reset(token)


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


async def _classify_stage_blob(
    candidate_id: str,
    blob: str,
    *,
    source_kind: str,
    source_id: str,
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Ruth classify via stage_meteorite do_task. No insert."""
    from src.core.agent import do_task

    empty = {"success": False, "outcome": None, "jobs": [], "batch_id": None}
    cid = (candidate_id or "").strip()
    if not cid:
        return {**empty, "error": "candidate_id is required"}
    kind = (source_kind or "").strip()
    if kind not in STAGE_METEORITE_CONFIG["source_ref_prefixes"]:
        return {**empty, "error": "invalid source_kind"}
    sid = (source_id or "").strip()
    if not sid:
        return {**empty, "error": "source_id is required"}
    body = blob if isinstance(blob, str) else ""
    if not body.strip():
        return {**empty, "error": "blob is required"}

    # Source handle for core source-refs; Ruth classifies CONTENT.
    live_content = f"SOURCE_KIND: {kind}\nSOURCE_ID: {sid}\nCONTENT:\n{body}"
    task_key = STAGE_METEORITE_CONFIG["task_key"]
    batch_id = f"{task_key}-stage-{uuid.uuid4()}"
    do_index = f"{task_key}_batch_{batch_id}"
    task_ctx: Dict[str, Any] = {**(ctx or {}), "astral_candidate_id": cid}
    if ctx and ctx.get("candidate_data") is not None:
        task_ctx["candidate_data"] = ctx["candidate_data"]
    if ctx and ctx.get("candidate_api_key") is not None:
        task_ctx["candidate_api_key"] = ctx["candidate_api_key"]

    token = _hold_log_batch(batch_id)
    try:
        logger.debug(
            "Calling agent.do_task: [task_key=%s, index=%s, source_kind=%s]",
            task_key, do_index, kind,
        )
        result = await do_task(
            task_key=task_key,
            live_content=live_content,
            index=do_index,
            ctx=task_ctx,
            debug=debug,
        )
        logger.debug("Response from agent.do_task: %s", result)

        if not result.get("success"):
            logger.debug("stage_failed batch_id=%s error=%r", batch_id, result.get("error"))
            logger.warning(
                "%s — stage_meteorite failed: %s\n  This blob is not classifying",
                cid, result.get("error") or "do_task failed",
            )
            return {
                "success": False,
                "error": result.get("error") or "do_task failed",
                "outcome": None,
                "jobs": [],
                "batch_id": batch_id,
                "raw": result,
            }

        parsed = result.get("parsed_response") if isinstance(result.get("parsed_response"), dict) else {}
        raw_outcome = parsed.get("outcome")
        outcome = raw_outcome.strip() if isinstance(raw_outcome, str) else ""
        raw_jobs = parsed.get("jobs") if isinstance(parsed.get("jobs"), list) else []
        jobs = [j for j in raw_jobs if isinstance(j, dict)]

        if outcome not in STAGE_METEORITE_CONFIG["outcomes"]:
            logger.warning(
                "%s — invalid stage outcome %r\n  This blob is not classifying",
                cid, outcome,
            )
            return {
                "success": False,
                "error": "invalid stage outcome",
                "outcome": outcome or None,
                "jobs": [],
                "batch_id": batch_id,
                "raw": result,
            }
        if outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
            jobs = []

        logger.debug(
            "stage outcome=%s batch_id=%s job_count=%s source_kind=%s",
            outcome, batch_id, len(jobs), kind,
        )
        return {
            "success": True,
            "outcome": outcome,
            "jobs": jobs,
            "error": None,
            "batch_id": batch_id,
            "raw": result,
        }
    finally:
        if token is not None:
            log_batch_id.reset(token)


def _stage_field(job: Dict[str, Any], key: str) -> Optional[str]:
    raw = job.get(key)
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    return text or None


def _new_email_error_row(
    cid: str,
    kind: str,
    sid: str,
    error: str,
    classify_outcome: Optional[str] = None,
) -> Dict[str, Any]:
    col = METEORITE_CONFIG["electronic_contact_column"]
    return {
        "candidate_id": cid,
        "source_kind": kind,
        "source_id": sid,
        "state": "NEW_EMAIL_ERROR",
        "classify_outcome": classify_outcome,
        "content": None,
        "link": None,
        "job_title": None,
        "employer_name": None,
        col: None,
        "error": error,
    }


def _insert_stage_rows(row_dicts: List[Dict[str, Any]]) -> Tuple[List[int], Optional[str]]:
    logger.debug("Calling insert_meteorite_rows: [n=%s]", len(row_dicts))
    ids = insert_meteorite_rows(row_dicts)
    logger.debug("Response from insert_meteorite_rows: %s", ids)
    if len(ids) != len(row_dicts):
        return ids, f"insert_count_mismatch ids={len(ids)} rows={len(row_dicts)}"
    logger.debug("Beginning stage row info loop on %s items", len(ids))
    for row_id, row in zip(ids, row_dicts):
        _meteorite_state_info(row_id, row["state"])
    logger.debug("End stage row info loop after %s items", len(ids))
    return ids, None


@_with_log_debug
async def stage_meteorite(
    candidate_id: str,
    blob: str,
    *,
    source_kind: str,
    source_id: str,
    debug: bool = False,
) -> Dict[str, Any]:
    """Classify a blob with Ruth and insert the meteorite row in this pass."""
    err_key = METEORITE_CONFIG["land_outcome_error"]
    col = METEORITE_CONFIG["electronic_contact_column"]

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
    kind = (source_kind or "").strip()
    sid = (source_id or "").strip()
    prefixes = STAGE_METEORITE_CONFIG["source_ref_prefixes"]
    can_insert = kind in prefixes and bool(sid)

    if not cid:
        _warn_item(
            "stage_meteorite",
            "candidate_id is required",
            "This blob is not being classified",
        )
        return _err("candidate_id is required")
    if not can_insert:
        why = "invalid source_kind" if kind not in prefixes else "source_id is required"
        _warn_item(cid, why, "This blob is not being saved")
        return _err(why)

    def _save_error(
        error: str,
        classify_outcome=None,
        *,
        batch_id=None,
        insert_fail_step: str = "This blob is not being saved as a classified row",
    ):
        try:
            _ids, mismatch = _insert_stage_rows([
                _new_email_error_row(cid, kind, sid, error, classify_outcome),
            ])
        except Exception as exc:
            logger.exception(
                "%s | stage_meteorite %s %s\n  %s: %s\n  %s",
                cid, kind, sid, type(exc).__name__, exc, insert_fail_step,
            )
            return _err(error, batch_id=batch_id, stage_outcome=classify_outcome)
        if mismatch:
            _warn_item(cid, mismatch, "This blob is not being saved as a classified row")
            return _err(mismatch, batch_id=batch_id, stage_outcome=classify_outcome)
        return None

    cand = get_candidate(cid)
    if not cand:
        _warn_item(cid, "candidate not found", "This blob is not being classified")
        missed = f"candidate not found: {cid}"
        failed = _save_error(missed)
        return failed or _err(missed)

    ctx = dict(cand) if isinstance(cand, dict) else {}
    ctx["astral_candidate_id"] = cid
    try:
        logger.debug(
            "Calling _classify_stage_blob: [candidate_id=%s, source_kind=%s, source_id=%s]",
            cid, kind, sid,
        )
        classify = await _classify_stage_blob(
            cid, blob, source_kind=kind, source_id=sid, ctx=ctx, debug=debug,
        )
        logger.debug("Response from _classify_stage_blob: %s", classify)
    except Exception as exc:
        logger.exception(
            "%s | stage_meteorite %s %s\n  %s: %s\n  This blob is not being saved as a classified row",
            cid, kind, sid, type(exc).__name__, exc,
        )
        failed = _save_error(str(exc), insert_fail_step="The error row was not inserted")
        return failed or _err(str(exc))

    batch_id = classify.get("batch_id")
    outcome = classify.get("outcome")
    skip = STAGE_METEORITE_CONFIG["skip_outcomes"]
    text_outcomes = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]
    url_outcomes = STAGE_METEORITE_CONFIG["url_scrape_outcomes"]

    if classify.get("success") and outcome in skip:
        row = {
            "candidate_id": cid,
            "source_kind": kind,
            "source_id": sid,
            "state": "NOT_A_JOB",
            "classify_outcome": outcome,
            "content": None,
            "link": None,
            "job_title": None,
            "employer_name": None,
            col: None,
            "error": None,
        }
        try:
            _ids, mismatch = _insert_stage_rows([row])
        except Exception as exc:
            logger.exception(
                "%s | stage_meteorite %s %s\n  %s: %s\n  This blob is not being saved as a classified row",
                cid, kind, sid, type(exc).__name__, exc,
            )
            return _err(str(exc), batch_id=batch_id, stage_outcome=outcome)
        if mismatch:
            _warn_item(cid, mismatch, "This blob is not being saved as a classified row")
            return _err(mismatch, batch_id=batch_id, stage_outcome=outcome)
        return {
            "outcome": outcome,
            "stage_outcome": outcome,
            "skipped": True,
            "jobs": [],
            "error": None,
            "batch_id": batch_id,
        }

    if classify.get("success") and outcome in (*text_outcomes, *url_outcomes):
        row_dicts, map_err = _map_classify_jobs_to_meteorite_rows(
            outcome,
            classify.get("jobs") or [],
            candidate_id=cid,
            source_kind=kind,
            source_id=sid,
            timezone_key=_candidate_contact_timezone(cid),
        )
        if map_err:
            failed = _save_error(str(map_err), outcome, batch_id=batch_id)
            return failed or _err(str(map_err), batch_id=batch_id, stage_outcome=outcome)
        state = "READY" if outcome in text_outcomes else "SCRAPE_LINK"
        job_dicts = [j for j in (classify.get("jobs") or []) if isinstance(j, dict)]
        for row, job in zip(row_dicts, job_dicts):
            row["state"] = state
            row["job_title"] = _stage_field(job, "job_title")
            row["employer_name"] = _stage_field(job, "employer_name")
        try:
            _ids, mismatch = _insert_stage_rows(row_dicts)
        except Exception as exc:
            logger.exception(
                "%s | stage_meteorite %s %s\n  %s: %s\n  This blob is not being saved as a classified row",
                cid, kind, sid, type(exc).__name__, exc,
            )
            return _err(str(exc), batch_id=batch_id, stage_outcome=outcome)
        if mismatch:
            _warn_item(cid, mismatch, "This blob is not being saved as a classified row")
            return _err(mismatch, batch_id=batch_id, stage_outcome=outcome)
        return {
            "outcome": outcome,
            "stage_outcome": outcome,
            "skipped": False,
            "jobs": classify.get("jobs") or [],
            "error": None,
            "batch_id": batch_id,
        }

    err = classify.get("error") or "stage failed"
    failed = _save_error(err, outcome, batch_id=batch_id)
    return failed or _err(err, batch_id=batch_id, stage_outcome=outcome)


@_with_log_debug
async def land_meteorite(
    candidate_id: str,
    *,
    scraps: Optional[List[Dict[str, Any]]] = None,
    text: Optional[str] = None,
    job_link: Optional[str] = None,
    employer_name: Optional[str] = None,
    meteorite_id: Optional[Any] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Public meteorite land: scraps → enrich → Tracker save under meteorite parent (AST-1702).

    Returns company_id + outcomes[] + rollup outcome. Never a silent no-op.
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

    # Optional link scrape when body is thin — bot-block continues; ok JD appends.
    for scrap in work:
        link = (scrap.get("job_link") or "").strip() if isinstance(scrap.get("job_link"), str) else ""
        if link:
            scrap["job_link"] = link
        await _land_link_check_append(scrap, candidate_id=cid, debug=debug)

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
    shared_mid: Optional[int] = None
    if meteorite_id is not None and str(meteorite_id).strip():
        shared_mid = int(meteorite_id)
    logger.debug("Beginning land enrich job loop on %s items", n)
    for i, row in enumerate(enriched_jobs, start=1):
        found_jd = row.get("jd_text") or ""
        found_emp = row.get("employer_name") or ""
        row_stem = (row.get("company_stem") or "").strip() if isinstance(row.get("company_stem"), str) else ""
        row_link = (row.get("job_link") or "").strip() if isinstance(row.get("job_link"), str) else ""
        try:
            if shared_mid is not None:
                mid = shared_mid
            else:
                mid = _insert_paste_meteorite_parent(
                    cid, content=found_jd or None, link=row_link or None
                )
            mrow = get_meteorite(mid) or {}
            mlink = (mrow.get("link") or "").strip()
            if not mlink and row_link:
                update_meteorite(mid, link=row_link)
                mlink = row_link
            emp = _optional_real_company_id(company_stem=row_stem or None, candidate_id=cid)
            logger.debug(
                "Calling tracker.save_meteorite_job: [candidate_id=%s, meteorite_id=%s]",
                cid, mid,
            )
            save = tracker.save_meteorite_job(
                cid,
                meteorite_id=mid,
                company_id=emp,
                company_job_id=row.get("company_job_id") or None,
                job_title=row.get("job_title") or None,
                job_link=mlink or None,
                job_data={jd_key: found_jd},
                employer_name=found_emp or None,
                debug=debug,
            )
            logger.debug("Response from tracker.save_meteorite_job: %s", save)
            outcomes.append(save)
            if save.get("outcome") in ok_outcomes:
                job_id = str(save.get("astral_job_id") or "")
                if shared_mid is None:
                    update_meteorite(mid, state="LANDED", astral_job_id=job_id)
                elif job_id:
                    update_meteorite(mid, state="LANDED", astral_job_id=job_id)
                if emp and first_company is None:
                    first_company = emp
                _entity_info(
                    job_id,
                    "job",
                    save.get("outcome"),
                    mid,
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
        "company_inserted": False,
        "outcomes": outcomes,
        "outcome": rollup,
        "error": top_error,
    }


# --- check_inbox (AST-1559) ---

def _candidate_contact_timezone(candidate_id: str) -> str:
    """Manage Candidate contact.timezone IANA key (empty → UTC via format helper)."""
    row = get_candidate((candidate_id or "").strip())
    if not isinstance(row, dict):
        return ""
    cd = row.get("candidate_data") if isinstance(row.get("candidate_data"), dict) else {}
    contact = cd.get("contact") if isinstance(cd.get("contact"), dict) else {}
    if not contact:
        top = row.get("contact")
        contact = top if isinstance(top, dict) else {}
    return (contact.get("timezone") or "").strip()


def _email_breadcrumb_link(
    *,
    from_email: str,
    to_email: str,
    sent_at: str,
    timezone_key: str,
) -> str:
    """Assemble non-http meteorite.link breadcrumb via AST-1701 helpers (AST-1703)."""
    from_email = (from_email or "").strip()
    to_email = (to_email or "").strip()
    sent_at = (sent_at or "").strip()
    if not from_email:
        raise ValueError("from_email required")
    if not to_email:
        raise ValueError("to_email required")
    if not sent_at:
        raise ValueError("sent_at required")

    dt: Optional[datetime] = None
    try:
        dt = datetime.fromisoformat(sent_at.replace("Z", "+00:00"))
    except ValueError:
        dt = None
    if dt is None:
        try:
            dt = parsedate_to_datetime(sent_at)
        except (TypeError, ValueError, IndexError):
            dt = None
    if dt is None:
        raise ValueError("unparseable sent_at")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    tz_key = (timezone_key or "").strip()
    logger.debug(
        "Calling format_contact_timezone_clock: [dt=%s, timezone_key=%s]",
        dt.isoformat(), tz_key,
    )
    clock = format_contact_timezone_clock(dt, tz_key)
    logger.debug("Response from format_contact_timezone_clock: %s", clock)
    logger.debug(
        "Calling format_job_link_breadcrumb: [from_email=%s, to_email=%s, clock=%s]",
        from_email, to_email, clock,
    )
    breadcrumb = format_job_link_breadcrumb(from_email, to_email, clock)
    logger.debug("Response from format_job_link_breadcrumb: %s", breadcrumb)
    return breadcrumb


def _map_classify_jobs_to_meteorite_rows(
    outcome: str,
    jobs: List[Dict[str, Any]],
    *,
    candidate_id: str,
    source_kind: str,
    source_id: str,
    timezone_key: str = "",
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
            link: Optional[str] = None
            if source_kind == "email":
                from_email = (
                    (job.get("from_email") or "").strip()
                    if isinstance(job.get("from_email"), str) else ""
                )
                to_email = (
                    (job.get("to_email") or "").strip()
                    if isinstance(job.get("to_email"), str) else ""
                )
                sent_at = (
                    (job.get("sent_at") or "").strip()
                    if isinstance(job.get("sent_at"), str) else ""
                )
                try:
                    link = _email_breadcrumb_link(
                        from_email=from_email,
                        to_email=to_email,
                        sent_at=sent_at,
                        timezone_key=timezone_key,
                    )
                except ValueError as exc:
                    return [], str(exc)
            col = METEORITE_CONFIG["electronic_contact_column"]
            out.append({
                "candidate_id": cid,
                "source_kind": source_kind,
                "source_id": sid,
                "classify_outcome": outcome,
                "content": text,
                "link": link,
                col: _electronic_contact_from_job(job),
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
            col = METEORITE_CONFIG["electronic_contact_column"]
            out.append({
                "candidate_id": cid,
                "source_kind": source_kind,
                "source_id": sid,
                "classify_outcome": outcome,
                "content": text or None,
                "link": link,
                col: _electronic_contact_from_job(job),
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

        logger.debug(
            "Calling stage_meteorite: [candidate_id=%s, source_kind=email, source_id=%s]",
            cid, mid,
        )
        stage = await stage_meteorite(
            cid, blob, source_kind="email", source_id=mid, debug=debug,
        )
        logger.debug("Response from stage_meteorite: %s", stage)

        if stage.get("error"):
            return _row(
                err_key,
                counter="error",
                error=str(stage.get("error")),
            )
        jobs = stage.get("jobs") or []
        skipped = bool(stage.get("skipped"))
        try:
            logger.debug("Calling archive_candidate_email: [message_id=%s]", mid)
            archive_candidate_email(mid)
            logger.debug("Response from archive_candidate_email: ok")
            if skipped:
                return _row(str(stage.get("outcome")), counter="passed")
            return _row(
                str(stage.get("outcome")),
                counter="passed",
                job_count=len(jobs),
            )
        except Exception as exc:
            next_step = (
                "Classify skipped; archive did not finish"
                if stage.get("skipped")
                else "Meteorite rows were inserted; archive did not finish"
            )
            logger.exception(
                "%s | inbox archive %s\n  %s: %s\n  %s",
                cid, mid, type(exc).__name__, exc, next_step,
            )
            if skipped:
                return _row(str(stage.get("outcome")), counter="error", error=str(exc))
            return _row(
                str(stage.get("outcome")),
                counter="error",
                error=str(exc),
                job_count=len(jobs),
            )

    except Exception as exc:
        logger.exception(
            "%s | inbox message %s\n  %s: %s\n  This message is not being ingested",
            cid, mid, type(exc).__name__, exc,
        )
        return _row(err_key, counter="error", error=str(exc))


@_with_log_debug
async def check_inbox(task: dict, *, debug: bool = False) -> dict[str, int]:
    """Fetch, then stage_meteorite via ingest, then archive. Not the Ruth classify runner."""
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
    entity_candidate_id = str((task or {}).get("candidate_id") or "").strip()
    if not entity_candidate_id:
        raise ValueError("candidate_id is required")

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s, candidate_id=%s]",
        batch_id, cfg["stage_trigger_state"], batch_size, entity_candidate_id,
    )
    claim_meteorite_batch(batch_id, cfg["stage_trigger_state"], limit=batch_size, candidate_id=entity_candidate_id)
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
                    update_meteorite(row_id, state="SCRAPE_ERROR", error="missing classify_outcome")
                    _row_miss(
                        row_id, cid, "missing classify_outcome", "This row is ERROR",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue
                if outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]:
                    update_meteorite(row_id, state="SCRAPE_ERROR", error="skip outcome on row")
                    _row_miss(
                        row_id, cid, "skip outcome on row", "This row is ERROR",
                    )
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue
                if outcome in STAGE_METEORITE_CONFIG["url_scrape_outcomes"]:
                    link = (row.get("link") or "").strip()
                    if not _is_http_url(link):
                        update_meteorite(row_id, state="SCRAPE_ERROR", error="missing link")
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
                        update_meteorite(row_id, state="SCRAPE_ERROR", error="missing content")
                        _row_miss(row_id, cid, "missing content", "This row is ERROR")
                        summary["total_failed"] += 1
                        summary["total_errors"] += 1
                        continue
                    # AST-1703: email text rows must already carry breadcrumb on link.
                    kind = (row.get("source_kind") or "").strip()
                    link = (row.get("link") or "").strip()
                    if kind == "email" and not link:
                        update_meteorite(
                            row_id, state="SCRAPE_ERROR", error="missing breadcrumb link",
                        )
                        _row_miss(
                            row_id, cid, "missing breadcrumb link", "This row is ERROR",
                        )
                        summary["total_failed"] += 1
                        summary["total_errors"] += 1
                        continue
                    update_meteorite(row_id, state="READY")
                    _meteorite_state_info(row_id, "READY", from_state="NEW")
                    summary["total_passed"] += 1
                    continue
                err = f"unhandled classify_outcome: {outcome}"
                update_meteorite(row_id, state="SCRAPE_ERROR", error=err)
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

    entity_candidate_id = str((task or {}).get("candidate_id") or "").strip()
    if not entity_candidate_id:
        raise ValueError("candidate_id is required")

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s, candidate_id=%s]",
        batch_id, cfg["scrape_trigger_state"], batch_size, entity_candidate_id,
    )
    claim_meteorite_batch(batch_id, cfg["scrape_trigger_state"], limit=batch_size, candidate_id=entity_candidate_id)
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
                    update_meteorite(row_id, state="SCRAPE_ERROR", error="missing link")
                    _row_miss(row_id, cid, "missing link", "This row is ERROR")
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue

                visible_text, final_url = await _land_fetch_link_text(link, debug=debug)
                page_status = _CONTACT_PAGE_STATUS.get(_classify_jd(visible_text), "missing")

                if page_status == "blocked":
                    # AST-1689: state-only — do not clear electronic_contact (AC4).
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
                update_meteorite(row_id, state=status_map.get(page_status, "SCRAPE_ERROR"), error=err)
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
    """Dispatch runner: READY|BOT_BLOCKED(+content) → LANDED + job create (AST-1560 / AST-1693)."""
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
    land_states = ["READY", "BOT_BLOCKED"]

    entity_candidate_id = str((task or {}).get("candidate_id") or "").strip()
    if not entity_candidate_id:
        raise ValueError("candidate_id is required")

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, states=%s, limit=%s, candidate_id=%s]",
        batch_id, land_states, batch_size, entity_candidate_id,
    )
    claim_meteorite_batch(
        batch_id,
        cfg["land_trigger_state"],
        limit=batch_size,
        candidate_id=entity_candidate_id,
        states=land_states,
    )
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
                from_state = (row.get("state") or "").strip()
                if not content:
                    # Empty BOT_BLOCKED stays for Estelle paste (AST-1561); READY → ERROR.
                    if from_state == "BOT_BLOCKED":
                        logger.debug(
                            "land skip empty BOT_BLOCKED meteorite %s for AST-1561",
                            row_id,
                        )
                        continue
                    update_meteorite(row_id, state="SCRAPE_ERROR", error="missing content")
                    _row_miss(row_id, cid, "missing content", "This row is ERROR")
                    summary["total_failed"] += 1
                    summary["total_errors"] += 1
                    continue

                link_text = (row.get("link") or "").strip()
                logger.debug(
                    "Calling tracker.save_meteorite_job: [candidate_id=%s, meteorite_id=%s]",
                    cid, row_id,
                )
                save = tracker.save_meteorite_job(
                    cid,
                    meteorite_id=row_id,
                    company_id=None,
                    job_data={jd_key: content},
                    job_link=link_text or None,
                    company_job_id=None,
                    employer_name=None,
                    debug=debug,
                )
                logger.debug("Response from tracker.save_meteorite_job: %s", save)
                if save.get("outcome") in ok_outcomes:
                    job_id = str(save.get("astral_job_id") or "")
                    if link_text and (save.get("job") or {}).get("job_link") != link_text:
                        save_job(job_id, job_link=link_text)
                    update_meteorite(row_id, state="LANDED", astral_job_id=job_id)
                    _meteorite_state_info(row_id, "LANDED", from_state=from_state or "READY")
                    _entity_info(job_id, "job", save.get("outcome"), row_id)
                    summary["total_passed"] += 1
                    continue

                err = str(save.get("error") or "land failed")
                update_meteorite(row_id, state="SCRAPE_ERROR", error=err)
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

    entity_candidate_id = str((task or {}).get("candidate_id") or "").strip()
    if not entity_candidate_id:
        raise ValueError("candidate_id is required")

    summary = dict(_ZERO_SUMMARY)
    logger.debug(
        "Calling claim_meteorite_batch: [batch_id=%s, state=%s, limit=%s, candidate_id=%s]",
        batch_id, cfg["trigger_state"], batch_size, entity_candidate_id,
    )
    claim_meteorite_batch(batch_id, cfg["trigger_state"], limit=batch_size, candidate_id=entity_candidate_id)
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
                # AST-1693: contentful BOT_BLOCKED belongs to land, not Estelle DM.
                if (row.get("content") or "").strip():
                    logger.debug(
                        "notify skip contentful BOT_BLOCKED meteorite %s for land",
                        row_id,
                    )
                    continue

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
