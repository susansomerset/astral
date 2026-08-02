"""AST-1090: gaze_email mailbox runner for the null-candidate dispatch row.

List Astral inbox → From-bind → unbound age→Trash → bound shape route →
Ruth parse (candidate API key) / scrape / per-candidate dedupe → METEORITE_NEW
create → archive on success or all-duplicate skip. Style D when debug=True.
Never calls qualify/GDL or global AST-1061 job_link helpers.

AST-1140: ``run_gaze_email_selected_ids`` — Land Meteorite selected-ids ingest
sharing the same bound helper; does not stamp ``candidate.last_email_check``.
"""

from __future__ import annotations

import os
import time
from typing import Optional
from urllib.parse import urlparse

from src.core.agent import do_task
from src.core.candidate import get_candidate
from src.core.gazer import _meteorite_fetch_link_visible_text
from src.core.inbox import get_message_html, list_inbox_messages
from src.core.meteorite import create_meteorite_job
from src.data.database import job_link_exists_for_candidate
from src.external.gmail import archive_message, trash_message
from src.utils.config import (
    GAZE_EMAIL_CONFIG,
    METEORITE_EMAIL_INGEST_CONFIG,
    METEORITE_EMAIL_PARSE_CONFIG,
)
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
        live = f"PARSE_MODE: {html_mode}\n\n{html}"
        parsed = await _ruth_parse(mode=html_mode, live=live, msg_id=mid, ctx=ctx, debug=debug)
        if parsed is None:
            index_dbg(debug, index=index, total=total, mid=mid, outcome="error")
            return (1, 0, 0, 1, "error")
        jobs = parsed.get("jobs") if isinstance(parsed.get("jobs"), list) else []
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
        live = f"PARSE_MODE: {subject_mode}\nSUBJECT: {subject}\n\n{html}"
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


async def run_gaze_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """AST-1090: process Astral inbox for the null-candidate gaze_email dispatch row."""
    del task  # row identity unused — runner always uses shared Astral inbox
    if debug:
        logger.set_debug_flag(True)

    messages = list_inbox_messages(debug=debug)
    n = len(messages)
    if debug:
        env_user = (os.environ.get("GMAIL_USER") or "").casefold()
        expected = (GAZE_EMAIL_CONFIG["account_address"] or "").casefold()
        if env_user != expected:
            _detail(True, f"account_mismatch GMAIL_USER={env_user!r} expected={expected!r}")

    processed = passed = failed = errors = 0
    now_ms = int(time.time() * 1000)

    for i, msg in enumerate(messages, start=1):
        mid = msg.get("id") or ""
        try:
            _dbg(debug, index=i, total=n, mid=mid, outcome="found")
            _detail(debug, f"from_address={(msg.get('from_address') or '')[:120]}")
            match = msg.get("candidate_match") or {}
            if not match.get("matched"):
                # unbound path
                if _unbound_is_stale(int(msg.get("internal_date_ms") or 0), now_ms=now_ms):
                    trash_message(mid)
                    _dbg(debug, index=i, total=n, mid=mid, outcome="trashed")
                else:
                    _dbg(debug, index=i, total=n, mid=mid, outcome="ignored-unbound")
                processed += 1
                passed += 1
                continue

            _detail(debug, f"astral_candidate_id={match.get('astral_candidate_id')}")
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
