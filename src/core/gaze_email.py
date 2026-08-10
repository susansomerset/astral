"""AST-1136: candidate-bound gaze_email mailbox runner.

List Astral inbox → filter From→selected candidate → unbound age→Trash
(shared hygiene) → bound shape route → Ruth parse (that candidate’s API key)
/ scrape / per-candidate dedupe → METEORITE_NEW create → archive; stamp
last_email_check. Style D when debug=True. Never calls qualify/GDL or global
AST-1061 job_link helpers. process_gaze_email_messages is the AST-1129 reuse path.

AST-1140: ``run_gaze_email_selected_ids`` — Land Meteorite selected-ids ingest
sharing the same bound helper; does not stamp ``candidate.last_email_check``.

AST-1213: Ruth live payload is visible text + links (not raw HTML); link list
uses ``ruth_payload_link_exclude_substrings`` (not Playwright excludes).
"""

from __future__ import annotations

import os
import time
from typing import Optional
from urllib.parse import urlparse

from src.core.agent import do_task
from src.core.candidate import get_candidate
from src.core.gazer import (
    _meteorite_email_body_text,
    _meteorite_fetch_link_visible_text,
)
from src.core.inbox import get_message_html, list_inbox_messages
from src.core.meteorite import create_meteorite_job
from src.data.database import (
    job_link_exists_for_candidate,
    update_candidate_last_email_check,
)
from src.external.gmail import archive_message, trash_message
from src.utils.config import (
    GAZE_EMAIL_CONFIG,
    METEORITE_EMAIL_INGEST_CONFIG,
    METEORITE_EMAIL_PARSE_CONFIG,
)
from src.utils.formatting import normalize_link
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)


def _subject_is_url(subject: str) -> bool:
    # strip; urlparse; scheme in GAZE_EMAIL_CONFIG["subject_url_schemes"] and netloc non-empty
    s = (subject or "").strip()
    if not s:
        return False
    parsed = urlparse(s)
    schemes = set(GAZE_EMAIL_CONFIG["subject_url_schemes"])
    return (parsed.scheme or "").lower() in schemes and bool(parsed.netloc)


def _body_text(html_body: str) -> str:
    # BeautifulSoup get_text — lazy-import bs4 like inbox.strip_extract
    from bs4 import BeautifulSoup

    return BeautifulSoup(html_body or "", "html.parser").get_text(" ", strip=True)


def _body_is_empty(html_body: str) -> bool:
    return not _body_text(html_body)


def _unbound_is_stale(internal_date_ms: int, *, now_ms: int) -> bool:
    days = int(GAZE_EMAIL_CONFIG["unbound_retention_days"])
    if internal_date_ms <= 0:
        return False  # unknown age → leave untouched
    age_ms = now_ms - internal_date_ms
    return age_ms > days * 24 * 60 * 60 * 1000


def _dbg(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=GAZE_EMAIL_CONFIG["debug_func"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )


def _dbg_selected(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=GAZE_EMAIL_CONFIG["debug_func_selected"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )


def _detail(debug: bool, line: str) -> None:
    if debug:
        logger.debug_detail(line)


async def _ingest_link(
    cid: str,
    url: str,
    *,
    jd_suffix: Optional[str],
    debug: bool,
) -> str:
    """Return created|skipped|error for one URL under this candidate."""
    try:
        text, final_url = await _meteorite_fetch_link_visible_text(url, debug=debug)
    except Exception as exc:
        _detail(debug, f"scrape_error={type(exc).__name__}")
        return "error"
    link = (final_url or url).strip()
    if job_link_exists_for_candidate(cid, link):
        _detail(debug, f"skipped-duplicate job_link={link[:120]}")
        return "skipped"
    if len((text or "").strip()) < int(METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"]):
        _detail(debug, "skipped-short")
        return "skipped"
    jd = text if not jd_suffix else f"{text.rstrip()}\n\n{jd_suffix.lstrip()}"
    try:
        result = create_meteorite_job(cid, jd, job_link=link, debug=debug)
        _detail(debug, f"recorded astral_job_id={result.get('astral_job_id')}")
        return "created"
    except Exception as exc:
        _detail(debug, f"create_error={type(exc).__name__}")
        return "error"


def _ruth_candidate_links(html: str) -> list[str]:
    """Ordered unique http(s) hrefs for Ruth --- LINKS --- (ruth_payload excludes)."""
    # B1 lazy import: bs4 only on Ruth payload assembly (same pattern as gazer).
    from bs4 import BeautifulSoup

    cfg = METEORITE_EMAIL_INGEST_CONFIG
    schemes = {s.casefold() for s in cfg["link_schemes"]}
    excludes = tuple(s.casefold() for s in cfg["ruth_payload_link_exclude_substrings"])
    allows = tuple(s.casefold() for s in cfg["link_allow_substrings"])
    soup = BeautifulSoup(html or "", "html.parser")
    seen: set[str] = set()
    out: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = (tag.get("href") or "").strip()
        if not href or href in seen:
            continue
        parsed = urlparse(href)
        scheme = (parsed.scheme or "").casefold()
        if scheme not in schemes:
            continue
        low = href.casefold()
        if any(frag in low for frag in excludes):
            continue
        if allows and not any(frag in low for frag in allows):
            continue
        seen.add(href)
        out.append(href)
    return out


def _ruth_live_parts(html: str) -> tuple[str, list[str]]:
    """Return (visible_text, ruth_candidate_links) from email HTML."""
    return _meteorite_email_body_text(html), _ruth_candidate_links(html)


def _format_ruth_live_body(text: str, links: list[str]) -> str:
    """Visible text + optional --- LINKS --- enumeration (JD-scrape payload shape)."""
    parts = [text] if (text or "").strip() else ["(no visible text)"]
    if links:
        parts.append("--- LINKS ---")
        for i, lnk in enumerate(links, 1):
            parts.append(f"{i}. {lnk}")
    return "\n".join(parts)


def _ensure_html_links_jobs_complete(
    jobs: list,
    payload_links: list[str],
    *,
    debug: bool,
) -> list:
    """Ensure every Ruth --- LINKS --- href appears in jobs used for ingest.

    Keeps Ruth rows (order preserved). Appends stub rows ``{job_link, job_title: None}``
    for payload links not covered under ``normalize_link``. Style D only when
    ``debug`` and at least one payload link was missing from Ruth's list.
    """
    out: list = []
    covered: set[str] = set()
    for job in jobs or []:
        if not isinstance(job, dict):
            continue
        link = (job.get("job_link") or "").strip()
        if not link:
            continue
        out.append(job)
        norm = normalize_link(link)
        if norm:
            covered.add(norm)

    missing: list[str] = []
    for href in payload_links or []:
        norm = normalize_link(href)
        if not norm or norm in covered:
            continue
        missing.append(href)
        covered.add(norm)
        out.append({"job_link": href, "job_title": None})

    if debug and missing:
        # Path-tail ids for UAT scan (Dice UUID); fall back to full URL if empty.
        missing_ids = ",".join(
            ((u.rstrip("/").rsplit("/", 1)[-1]) if u.rstrip("/") else u) or u
            for u in missing
        )
        logger.debug_index(
            func="gaze_email._ensure_html_links_jobs_complete",
            index=1,
            total=1,
            identifier="html_links",
            outcome="reconciled",
        )
        logger.debug_detail(
            f"found={len(payload_links)} recorded={len(payload_links) - len(missing)} "
            f"missing={missing_ids}"
        )
    return out


async def _ruth_parse(
    *,
    mode: str,
    live: str,
    msg_id: str,
    ctx: dict,
    debug: bool,
) -> Optional[dict]:
    try:
        resp = await do_task(
            task_key=METEORITE_EMAIL_PARSE_CONFIG["task_key"],
            live_content=live,
            index=msg_id,
            ctx=ctx,
            debug=debug,
        )
    except Exception as exc:
        _detail(debug, f"ruth_error={type(exc).__name__}")
        return None
    if not isinstance(resp, dict) or not resp.get("success"):
        _detail(debug, f"ruth_fail={resp.get('error') if isinstance(resp, dict) else 'no-resp'}")
        return None
    parsed = resp.get("parsed_response")
    return parsed if isinstance(parsed, dict) else None


async def _finalize_archive(
    msg_id: str,
    outcomes: list[str],
    *,
    debug: bool,
    index: int,
    total: int,
    index_dbg=_dbg,
) -> tuple[int, int, int, str]:
    """Archive when ≥1 create or all attempts were skips. Returns (passed, failed, error, outcome)."""
    if not outcomes:
        index_dbg(debug, index=index, total=total, mid=msg_id, outcome="ignored-empty")
        return (1, 0, 0, "ignored-empty")  # leave inbox; count as intentional pass
    n_created = outcomes.count("created")
    n_skipped = outcomes.count("skipped")
    n_error = outcomes.count("error")
    if n_created > 0 or (n_skipped > 0 and n_error == 0 and n_created == 0):
        # all-duplicate / short skips still archive (AC5)
        try:
            archive_message(msg_id)
        except Exception as exc:
            _detail(debug, f"archive_error={type(exc).__name__}")
            index_dbg(debug, index=index, total=total, mid=msg_id, outcome="error")
            return (0, 0, 1, "error")
        _detail(debug, f"created={n_created} skipped={n_skipped}")
        index_dbg(debug, index=index, total=total, mid=msg_id, outcome="archived")
        return (1, 0, 0, "archived")
    # only errors → leave inbox
    index_dbg(debug, index=index, total=total, mid=msg_id, outcome="error")
    return (0, 0, 1, "error")


async def _handle_bound(
    msg: dict,
    match: dict,
    *,
    debug: bool,
    index: int,
    total: int,
    index_dbg=_dbg,
) -> tuple[int, int, int, int, str]:
    """Returns (processed, passed, failed, errors, outcome) for one bound message."""
    cid = match.get("astral_candidate_id") or ""
    mid = msg.get("id") or ""
    ctx = get_candidate(cid) if cid else None
    if not ctx or not ctx.get("candidate_api_key"):
        index_dbg(debug, index=index, total=total, mid=mid, outcome="error")
        _detail(debug, "missing candidate or API key — leave inbox")
        return (1, 0, 1, 0, "failed")

    try:
        payload = get_message_html(mid)
    except Exception as exc:
        index_dbg(debug, index=index, total=total, mid=mid, outcome="error")
        _detail(debug, f"get_html_error={type(exc).__name__}")
        return (1, 0, 0, 1, "error")

    subject = (payload.get("subject") or "").strip()
    html = payload.get("html_body") or ""
    empty_body = _body_is_empty(html)
    modes = METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]
    html_mode, subject_mode = modes[0], modes[1]

    # Shape: ignore (non-URL subject + empty body) — leave inbox
    if subject and not _subject_is_url(subject) and empty_body:
        index_dbg(debug, index=index, total=total, mid=mid, outcome="ignored")
        _detail(debug, "shape=ignore")
        return (1, 1, 0, 0, "ignored")

    # Both empty → ignore
    if not subject and empty_body:
        index_dbg(debug, index=index, total=total, mid=mid, outcome="ignored")
        _detail(debug, "shape=ignore-empty")
        return (1, 1, 0, 0, "ignored")

    outcomes: list[str] = []

    # html_links: no subject + non-empty body
    if not subject and not empty_body:
        _detail(debug, "shape=html_links")
        text, links = _ruth_live_parts(html)
        body = _format_ruth_live_body(text, links)
        live = f"PARSE_MODE: {html_mode}\n\n{body}"
        _detail(debug, f"ruth_payload visible_chars={len(text)} links={len(links)}")
        for line in truncate_debug_content(live):
            _detail(debug, line)
        parsed = await _ruth_parse(mode=html_mode, live=live, msg_id=mid, ctx=ctx, debug=debug)
        if parsed is None:
            index_dbg(debug, index=index, total=total, mid=mid, outcome="error")
            return (1, 0, 0, 1, "error")
        jobs = parsed.get("jobs") if isinstance(parsed.get("jobs"), list) else []
        jobs = _ensure_html_links_jobs_complete(jobs, links, debug=debug)
        parsed["jobs"] = jobs
        for job in jobs:
            if not isinstance(job, dict):
                continue
            link = (job.get("job_link") or "").strip()
            if not link:
                continue
            outcomes.append(await _ingest_link(cid, link, jd_suffix=None, debug=debug))
        p, f, e, outcome = await _finalize_archive(
            mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
        )
        return (1, p, f, e, outcome)

    # subject_url: URL subject + empty body
    if subject and _subject_is_url(subject) and empty_body:
        _detail(debug, "shape=subject_url")
        outcomes.append(await _ingest_link(cid, subject, jd_suffix=None, debug=debug))
        p, f, e, outcome = await _finalize_archive(
            mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
        )
        return (1, p, f, e, outcome)

    # subject_body: subject + non-empty body (URL subject with body uses this path)
    if subject and not empty_body:
        _detail(debug, "shape=subject_body")
        text, links = _ruth_live_parts(html)
        body = _format_ruth_live_body(text, links)
        live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{body}"
        _detail(debug, f"ruth_payload visible_chars={len(text)} links={len(links)}")
        for line in truncate_debug_content(live):
            _detail(debug, line)
        parsed = await _ruth_parse(mode=subject_mode, live=live, msg_id=mid, ctx=ctx, debug=debug)
        if parsed is None:
            index_dbg(debug, index=index, total=total, mid=mid, outcome="error")
            return (1, 0, 0, 1, "error")
        jd_link = (parsed.get("jd_link") or "").strip()
        content_text = (parsed.get("content_text") or "").strip()
        body_txt = _body_text(html)
        min_chars = int(METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"])
        if jd_link:
            suffix = f"SUBJECT: {subject}\n\n{body_txt}"
            outcomes.append(await _ingest_link(cid, jd_link, jd_suffix=suffix, debug=debug))
        else:
            jd = content_text or f"{subject}\n\n{body_txt}"
            if len(jd.strip()) < min_chars:
                index_dbg(debug, index=index, total=total, mid=mid, outcome="ignored-empty")
                return (1, 1, 0, 0, "ignored-empty")
            # no link-based dedupe — always create with job_link=None (AC5 is link-scoped)
            try:
                result = create_meteorite_job(cid, jd, job_link=None, debug=debug)
                _detail(debug, f"recorded astral_job_id={result.get('astral_job_id')}")
                outcomes.append("created")
            except Exception as exc:
                _detail(debug, f"create_error={type(exc).__name__}")
                outcomes.append("error")
        p, f, e, outcome = await _finalize_archive(
            mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
        )
        return (1, p, f, e, outcome)

    index_dbg(debug, index=index, total=total, mid=mid, outcome="ignored")
    return (1, 1, 0, 0, "ignored")


async def process_gaze_email_messages(
    candidate_id: str,
    messages: list[dict],
    *,
    debug: bool = False,
) -> dict[str, int]:
    """Bound-ingest only for messages whose From binds to candidate_id.

    Same Ruth/scrape/dedupe/create/archive outcomes as the dispatch runner.
    Does not list Gmail, does not Trash unbound mail, does not stamp
    last_email_check. AST-1129 Land Meteorite calls this with selected rows.
    """
    cid = str(candidate_id or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if debug:
        logger.set_debug_flag(True)

    n = len(messages)
    processed = passed = failed = errors = 0
    for i, msg in enumerate(messages, start=1):
        mid = msg.get("id") or ""
        try:
            _dbg(debug, index=i, total=n, mid=mid, outcome="found")
            _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
            match = msg.get("candidate_match") or {}
            if not match.get("matched"):
                _dbg(debug, index=i, total=n, mid=mid, outcome="skipped-unbound")
                _detail(debug, "process_gaze_email_messages does not mutate unbound mail")
                processed += 1
                passed += 1
                continue
            bound_cid = str(match.get("astral_candidate_id") or "").strip()
            if bound_cid != cid:
                _dbg(debug, index=i, total=n, mid=mid, outcome="skipped-other-candidate")
                processed += 1
                passed += 1
                continue
            _detail(debug, f"astral_candidate_id={bound_cid}")
            # 5th return is outcome string for selected-ids; ignore here
            p, pa, fa, er, _outcome = await _handle_bound(
                msg, match, debug=debug, index=i, total=n
            )
            processed += p
            passed += pa
            failed += fa
            errors += er
        except Exception as exc:
            errors += 1
            processed += 1
            _dbg(debug, index=i, total=n, mid=mid, outcome="error")
            _detail(debug, f"message_error={type(exc).__name__}: {exc}")
            for line in truncate_debug_content(str(exc)):
                _detail(debug, line)

    return {
        "total_processed": processed,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }


async def run_gaze_email_selected_ids(
    message_ids: list[str],
    *,
    debug: bool = False,
) -> dict:
    """Land Meteorite: ingest only these Astral inbox message ids (AST-1140).

    Same bind/route/scrape/dedupe/create/archive outcomes as dispatcher gaze_email.
    Does not stamp candidate.last_email_check. Does not call Create strip/extract.
    """
    if debug:
        logger.set_debug_flag(True)

    # Preserve caller order; strip empties — do not invent ids.
    normalized_ids = [raw.strip() for raw in (message_ids or []) if (raw or "").strip()]
    by_id = {(m.get("id") or ""): m for m in list_inbox_messages(debug=debug)}

    results: list[dict] = []
    total_processed = total_passed = total_failed = total_errors = total_skipped = 0
    n = len(normalized_ids)

    for i, mid in enumerate(normalized_ids, start=1):
        _dbg_selected(debug, index=i, total=n, mid=mid, outcome="found")
        if mid not in by_id:
            outcome = GAZE_EMAIL_CONFIG["selected_outcome_skipped_not_in_inbox"]
            results.append(
                {"message_id": mid, "outcome": outcome, "astral_candidate_id": None}
            )
            total_skipped += 1
            total_processed += 1
            _dbg_selected(debug, index=i, total=n, mid=mid, outcome=outcome)
            continue

        msg = by_id[mid]
        match = msg.get("candidate_match") or {}
        cid = (match.get("astral_candidate_id") or "").strip()
        if not match.get("matched") or not cid:
            # Skip only — retention Trash stays on the dispatcher hygiene path.
            if not match.get("matched"):
                outcome = GAZE_EMAIL_CONFIG["selected_outcome_skipped_unbound"]
            else:
                outcome = GAZE_EMAIL_CONFIG["selected_outcome_skipped_unmatched"]
            results.append(
                {"message_id": mid, "outcome": outcome, "astral_candidate_id": None}
            )
            total_skipped += 1
            total_processed += 1
            _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
            _dbg_selected(debug, index=i, total=n, mid=mid, outcome=outcome)
            continue

        _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
        _detail(debug, f"astral_candidate_id={cid}")
        p, pa, fa, er, outcome = await _handle_bound(
            msg, match, debug=debug, index=i, total=n, index_dbg=_dbg_selected
        )
        results.append(
            {
                "message_id": mid,
                "outcome": outcome,
                "astral_candidate_id": match["astral_candidate_id"],
            }
        )
        total_processed += p
        total_passed += pa
        total_failed += fa
        total_errors += er

    return {
        "results": results,
        "total_processed": total_processed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "total_skipped": total_skipped,
    }


async def run_gaze_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """AST-1136: candidate-bound mailbox run + unbound hygiene + last_email_check stamp."""
    cid = str((task or {}).get("candidate_id") or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if debug:
        logger.set_debug_flag(True)
        _dbg(debug, index=1, total=1, mid=cid, outcome="run-start")
        env_user = (os.environ.get("GMAIL_USER") or "").casefold()
        expected = (GAZE_EMAIL_CONFIG["account_address"] or "").casefold()
        if env_user != expected:
            _detail(True, f"account_mismatch GMAIL_USER={env_user!r} expected={expected!r}")

    messages = list_inbox_messages(debug=debug)
    n = len(messages)
    processed = passed = failed = errors = 0
    now_ms = int(time.time() * 1000)

    for i, msg in enumerate(messages, start=1):
        mid = msg.get("id") or ""
        try:
            _dbg(debug, index=i, total=n, mid=mid, outcome="found")
            _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
            match = msg.get("candidate_match") or {}
            if not match.get("matched"):
                if _unbound_is_stale(int(msg.get("internal_date_ms") or 0), now_ms=now_ms):
                    trash_message(mid)
                    _dbg(debug, index=i, total=n, mid=mid, outcome="trashed")
                else:
                    _dbg(debug, index=i, total=n, mid=mid, outcome="ignored-unbound")
                processed += 1
                passed += 1
                continue

            bound_cid = str(match.get("astral_candidate_id") or "").strip()
            if bound_cid != cid:
                _dbg(debug, index=i, total=n, mid=mid, outcome="skipped-other-candidate")
                processed += 1
                passed += 1
                continue

            _detail(debug, f"astral_candidate_id={bound_cid}")
            p, pa, fa, er, _outcome = await _handle_bound(
                msg, match, debug=debug, index=i, total=n
            )
            processed += p
            passed += pa
            failed += fa
            errors += er
        except Exception as exc:
            errors += 1
            processed += 1
            _dbg(debug, index=i, total=n, mid=mid, outcome="error")
            _detail(debug, f"message_error={type(exc).__name__}: {exc}")
            for line in truncate_debug_content(str(exc)):
                _detail(debug, line)

    # Stamp after a completed run (incl. zero bound matches / empty inbox).
    update_candidate_last_email_check(cid)
    if debug:
        _dbg(debug, index=1, total=1, mid=cid, outcome="run-complete")
        _detail(debug, "last_email_check=stamped")
        _detail(
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
