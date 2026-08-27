"""Candidate-bound meteorite_email mailbox runner.

List Astral inbox → filter From→selected candidate → unbound age→Trash
(shared hygiene) → Susan decision tree → land_meteorite / BOT_BLOCKED →
archive on success (error leaves inbox); stamp last_email_check.
Style D when debug=True. Never calls qualify/GDL. Ruth runs after a job
row exists (qualify), not in this runner.

AST-1140: ``run_meteorite_email_selected_ids`` — Land Meteorite selected-ids
sharing the same bound helper; does not stamp ``candidate.last_email_check``.

AST-1521: completes AST-1472's deferred retarget — bound path uses
``land_meteorite`` for JD-text ingress (not Ruth-first html_links).

AST-1522: test/bible gap only — no further product change on this sub.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any, Optional
from urllib.parse import urlparse

from src.core.agent import do_task  # noqa: F401 — AST-1522 [bug-repro] still monkeypatches this name
from src.core.candidate import get_candidate
from src.core.gazer import (
    _meteorite_fetch_link_visible_text,
)
from src.core.inbox import get_message_html, list_inbox_messages
from src.core.tracker import save_meteorite_job, transition_job_state
from src.data.database import (
    job_link_exists_for_candidate,
    update_candidate_last_email_check,
)
from src.external.gmail import archive_message, trash_message
from src.utils.config import (
    METEORITE_CONFIG,
    METEORITE_EMAIL_MAILBOX_CONFIG,
    METEORITE_EMAIL_INGEST_CONFIG,
    TASK_CONFIG,
)
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)


def _subject_is_url(subject: str) -> bool:
    # strip; urlparse; scheme in METEORITE_EMAIL_MAILBOX_CONFIG["subject_url_schemes"] and netloc non-empty
    s = (subject or "").strip()
    if not s:
        return False
    parsed = urlparse(s)
    schemes = set(METEORITE_EMAIL_MAILBOX_CONFIG["subject_url_schemes"])
    return (parsed.scheme or "").lower() in schemes and bool(parsed.netloc)


def _body_text(html_body: str) -> str:
    # BeautifulSoup get_text — lazy-import bs4 like inbox.strip_extract
    from bs4 import BeautifulSoup

    return BeautifulSoup(html_body or "", "html.parser").get_text(" ", strip=True)


def _body_is_empty(html_body: str) -> bool:
    return not _body_text(html_body)


def _unbound_is_stale(internal_date_ms: int, *, now_ms: int) -> bool:
    days = int(METEORITE_EMAIL_MAILBOX_CONFIG["unbound_retention_days"])
    if internal_date_ms <= 0:
        return False  # unknown age → leave untouched
    age_ms = now_ms - internal_date_ms
    return age_ms > days * 24 * 60 * 60 * 1000


def _dbg(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )


def _dbg_selected(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=METEORITE_EMAIL_MAILBOX_CONFIG["debug_func_selected"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )


def _detail(debug: bool, line: str) -> None:
    if debug:
        logger.debug_detail(line)


def _body_http_links(html: str) -> list[str]:
    """Ordered unique http(s) hrefs (ruth_payload exclude/allow filters)."""
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


def _body_looks_like_inspector_html(html: str) -> bool:
    """True when structural-tag density looks like an inspector paste (config-driven)."""
    cfg = METEORITE_EMAIL_INGEST_CONFIG
    tags = tuple(t.casefold() for t in cfg["inspector_structural_tags"])
    min_n = int(cfg["inspector_min_structural_tags"])
    if not tags or min_n <= 0:
        return False
    # Count opening tags whose name is in the structural set (ignore attributes).
    names = re.findall(r"<\s*([a-zA-Z][\w:-]*)\b", html or "")
    count = sum(1 for n in names if n.casefold() in tags)
    return count >= min_n


def _land_outcome_token(land: dict[str, Any]) -> str:
    """Map land_meteorite rollup → archive tokens created|skipped|error."""
    outcome = (land or {}).get("outcome") or METEORITE_CONFIG["land_outcome_error"]
    if outcome == METEORITE_CONFIG["land_outcome_created"]:
        return "created"
    if outcome in (
        METEORITE_CONFIG["land_outcome_duplicate_skip"],
        METEORITE_CONFIG["land_outcome_superseded"],
    ):
        return "skipped"
    return "error"


async def _land_jd(
    cid: str,
    *,
    text: str,
    job_link: Optional[str] = None,
    debug: bool = False,
) -> str:
    """Land JD text via land_meteorite; empty text → error (no call)."""
    body = (text or "").strip()
    if not body:
        _detail(debug, "land_jd empty text — skip land")
        return "error"
    # Late-import so tests can monkeypatch src.core.meteorite.land_meteorite.
    from src.core.meteorite import land_meteorite

    link = (job_link or "").strip() or None
    land = await land_meteorite(cid, text=body, job_link=link, debug=debug)
    token = _land_outcome_token(land)
    _detail(debug, f"land_jd outcome={token} job_link={(link or '')[:120]}")
    return token


def _create_bot_blocked_job(cid: str, job_link: str, *, debug: bool = False) -> str:
    """Create METEORITE_NEW with job_link then transition to BOT_BLOCKED (no JD)."""
    link = (job_link or "").strip()
    if not link:
        return "error"
    if job_link_exists_for_candidate(cid, link):
        _detail(debug, f"bot_blocked skipped-duplicate job_link={link[:120]}")
        return "skipped"
    # Late-import ensure (same cycle caution as inbox land helpers).
    from src.core.meteorite import ensure_meteorite_company

    try:
        ensured = ensure_meteorite_company(cid, debug=debug)
        short_name = ensured["short_name"]
        save = save_meteorite_job(
            cid,
            company=short_name,
            job_link=link,
            job_data={},
            debug=debug,
        )
    except Exception as exc:
        _detail(debug, f"bot_blocked_create_error={type(exc).__name__}")
        return "error"

    outcome = save.get("outcome") or METEORITE_CONFIG["land_outcome_error"]
    if outcome in (
        METEORITE_CONFIG["land_outcome_duplicate_skip"],
        METEORITE_CONFIG["land_outcome_superseded"],
    ):
        return "skipped"
    if outcome != METEORITE_CONFIG["land_outcome_created"]:
        _detail(debug, f"bot_blocked_save outcome={outcome}")
        return "error"

    astral_id = save.get("astral_job_id")
    if not astral_id:
        return "error"
    bot_state = TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"]
    try:
        transition_job_state([astral_id], bot_state)
    except Exception as exc:
        _detail(debug, f"bot_blocked_transition_error={type(exc).__name__}")
        return "error"
    _detail(debug, f"bot_blocked astral_job_id={astral_id}")
    return "created"


async def _scrape_land_or_bot_blocked(
    cid: str,
    url: str,
    *,
    jd_suffix: Optional[str] = None,
    debug: bool = False,
) -> str:
    """Scrape URL → land JD+link, or BOT_BLOCKED create when scrape fails/short."""
    link_in = (url or "").strip()
    if not link_in:
        return "error"
    if job_link_exists_for_candidate(cid, link_in):
        _detail(debug, f"scrape skipped-duplicate job_link={link_in[:120]}")
        return "skipped"

    try:
        text, final_url = await _meteorite_fetch_link_visible_text(link_in, debug=debug)
    except Exception as exc:
        _detail(debug, f"scrape_error={type(exc).__name__}")
        text, final_url = "", link_in

    link = (final_url or link_in).strip()
    visible = (text or "").strip()
    min_chars = int(METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"])
    if len(visible) >= min_chars:
        jd = visible if not jd_suffix else f"{visible.rstrip()}\n\n{jd_suffix.lstrip()}"
        return await _land_jd(cid, text=jd, job_link=link, debug=debug)

    _detail(debug, f"scrape short/empty → BOT_BLOCKED link={link[:120]}")
    return _create_bot_blocked_job(cid, link, debug=debug)


async def _finalize_archive(
    msg_id: str,
    outcomes: list[str],
    *,
    debug: bool,
    index: int,
    total: int,
    index_dbg=_dbg,
) -> tuple[int, int, int, str]:
    """Archive when ≥1 create or all attempts were skips. Empty outcomes → error."""
    if not outcomes:
        # No pass-without-ingest — leave inbox and fail the run.
        index_dbg(debug, index=index, total=total, mid=msg_id, outcome="error")
        return (0, 0, 1, "error")
    n_created = outcomes.count("created")
    n_skipped = outcomes.count("skipped")
    n_error = outcomes.count("error")
    if n_created > 0 or (n_skipped > 0 and n_error == 0 and n_created == 0):
        # all-duplicate / supersede skips still archive
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
    # Same visible text as _body_is_empty / Betty repro (not a second strip path).
    visible_body = _body_text(html) if not empty_body else ""
    links = _body_http_links(html) if not empty_body else []

    # Intentional ignore (non-URL subject + empty body) — leave inbox
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

    # URL subject + body → job_link=subject, text=body
    if subject and _subject_is_url(subject) and not empty_body:
        _detail(debug, "shape=url_subject_with_body")
        outcomes.append(
            await _land_jd(cid, text=visible_body, job_link=subject, debug=debug)
        )
        p, f, e, outcome = await _finalize_archive(
            mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
        )
        return (1, p, f, e, outcome)

    # URL subject + empty body → scrape or BOT_BLOCKED
    if subject and _subject_is_url(subject) and empty_body:
        _detail(debug, "shape=url_subject_empty_body")
        outcomes.append(await _scrape_land_or_bot_blocked(cid, subject, debug=debug))
        p, f, e, outcome = await _finalize_archive(
            mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
        )
        return (1, p, f, e, outcome)

    # Non-URL subject + body
    if subject and not empty_body:
        if links:
            _detail(debug, "shape=subject_body_with_link")
            first = links[0]
            try:
                scraped, final_url = await _meteorite_fetch_link_visible_text(
                    first, debug=debug
                )
            except Exception as exc:
                _detail(debug, f"scrape_error={type(exc).__name__}")
                scraped, final_url = "", first
            scraped_txt = (scraped or "").strip()
            min_chars = int(METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"])
            if len(scraped_txt) >= min_chars:
                link = (final_url or first).strip()
                jd = f"{subject}\n\n{visible_body}\n\n{scraped_txt}"
                outcomes.append(
                    await _land_jd(cid, text=jd, job_link=link, debug=debug)
                )
            else:
                # Scrape fail → land subject+body only (no BOT_BLOCKED on this fork)
                outcomes.append(
                    await _land_jd(
                        cid, text=f"{subject}\n\n{visible_body}", debug=debug
                    )
                )
        else:
            _detail(debug, "shape=subject_body_no_link")
            outcomes.append(
                await _land_jd(cid, text=f"{subject}\n\n{visible_body}", debug=debug)
            )
        p, f, e, outcome = await _finalize_archive(
            mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
        )
        return (1, p, f, e, outcome)

    # No subject + body
    if not subject and not empty_body:
        inspector = _body_looks_like_inspector_html(html)
        if inspector and links:
            _detail(debug, f"shape=inspector_multi_link n={len(links)}")
            for link in links:
                outcomes.append(
                    await _scrape_land_or_bot_blocked(cid, link, debug=debug)
                )
        else:
            # Plain JD text (reported case) or inspector with no links
            _detail(debug, "shape=no_subject_jd_text" if not inspector else "shape=inspector_no_links")
            outcomes.append(await _land_jd(cid, text=visible_body, debug=debug))
        p, f, e, outcome = await _finalize_archive(
            mid, outcomes, debug=debug, index=index, total=total, index_dbg=index_dbg
        )
        return (1, p, f, e, outcome)

    index_dbg(debug, index=index, total=total, mid=mid, outcome="ignored")
    return (1, 1, 0, 0, "ignored")


async def process_meteorite_email_messages(
    candidate_id: str,
    messages: list[dict],
    *,
    debug: bool = False,
) -> dict[str, int]:
    """Bound-ingest only for messages whose From binds to candidate_id.

    Same land/BOT_BLOCKED/archive outcomes as the dispatch runner.
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
                _detail(debug, "process_meteorite_email_messages does not mutate unbound mail")
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


async def run_meteorite_email_selected_ids(
    message_ids: list[str],
    *,
    debug: bool = False,
) -> dict:
    """Land Meteorite: ingest only these Astral inbox message ids (AST-1140).

    Same bind/tree/land/archive outcomes as dispatcher meteorite_email.
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
            outcome = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_not_in_inbox"]
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
                outcome = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_unbound"]
            else:
                outcome = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_unmatched"]
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


async def run_meteorite_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """Candidate-bound mailbox run + unbound hygiene + last_email_check stamp."""
    cid = str((task or {}).get("candidate_id") or "").strip()
    if not cid:
        raise ValueError("candidate_id is required")
    if debug:
        logger.set_debug_flag(True)
        _dbg(debug, index=1, total=1, mid=cid, outcome="run-start")
        env_user = (os.environ.get("GMAIL_USER") or "").casefold()
        expected = (METEORITE_EMAIL_MAILBOX_CONFIG["account_address"] or "").casefold()
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
