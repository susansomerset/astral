"""
Candidate-scoped Gmail list/filter (`fetch_candidate_email`) + archive
(`archive_candidate_email`); thin unenriched `list_inbox_messages` for Manage
Email All; keep `get_message_html` / assembled HTML / `strip_extract_email_html`.
Mailbox runner `check_email` (AST-1714) stages bound messages via stage_meteorite.

No From-then-To bind, no `fetch_email` runner, no land-bound stage entrypoints
(AST-1558). Land for admin is owned by `api_inbox` → meteorite.
"""

from __future__ import annotations

import functools
import html as html_module
import inspect
import os
from email.utils import getaddresses, parseaddr
from typing import Dict, Sequence

from src.external.gmail import (
    GmailMessageHtml,
    archive_message as external_archive_message,
    get_message_html as external_get_message_html,
    list_inbox_messages as external_list_inbox_messages,
)
from src.utils.config import INBOX_CREATE_JOB_CONFIG
from src.utils.formatting import normalize_pasted_list_email_html
from src.utils.logging import get_logger, log_debug

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


def list_inbox_messages(debug: bool = False) -> list[dict]:
    """Return every INBOX message metadata row for GMAIL_USER (no bind enrichment)."""
    if debug:
        logger.set_debug_flag(True)
    try:
        messages = external_list_inbox_messages()
    except Exception as e:
        logger.warning("[inbox] list_inbox_messages failed: %s", e)
        raise

    rows: list[dict] = [dict(msg) for msg in messages]
    if debug:
        n = len(rows)
        for i, msg in enumerate(rows, start=1):
            mid = (msg.get("id") or "")[:80]
            logger.debug_index(
                func="inbox.list",
                index=i,
                total=n,
                identifier=mid,
                outcome="listed",
            )
    return rows


def _alias_set_from_raw(aliases: Sequence[str]) -> set[str]:
    """Normalize caller aliases to a casefold address set (drop empties / non-emails)."""
    alias_set: set[str] = set()
    for raw in aliases or ():
        _display, parsed = parseaddr(raw or "")
        token = (parsed or raw or "").strip()
        if not token or "@" not in token:
            continue
        alias_set.add(token.casefold())
    return alias_set


def _filter_messages_by_aliases(
    messages: Sequence[dict],
    alias_set: set[str],
) -> list[dict]:
    """Keep messages whose From or To has any address in alias_set (casefold)."""
    if not alias_set:
        return []
    kept: list[dict] = []
    for msg in messages:
        headers = (msg.get("from_address") or "", msg.get("to_address") or "")
        hit = False
        for header in headers:
            for _display, addr in getaddresses([header]):
                token = (addr or "").strip()
                if token and token.casefold() in alias_set:
                    hit = True
                    break
            if hit:
                break
        if hit:
            kept.append(msg)
    return kept


def fetch_candidate_email(
    aliases: Sequence[str],
    *,
    debug: bool = False,
) -> list[dict]:
    """List inbox messages whose From or To address matches any alias (casefold)."""
    if debug:
        logger.set_debug_flag(True)

    alias_set = _alias_set_from_raw(aliases)
    if not alias_set:
        return []

    kept = _filter_messages_by_aliases(list_inbox_messages(debug=debug), alias_set)
    if debug:
        n = len(kept)
        for i, msg in enumerate(kept, start=1):
            mid = (msg.get("id") or "")[:80]
            logger.debug_index(
                func="inbox.fetch_candidate_email",
                index=i,
                total=n,
                identifier=mid,
                outcome="matched",
            )
            logger.debug_detail(f"aliases_n={len(alias_set)}")
    return kept


def archive_candidate_email(message_id: str) -> None:
    """Archive one Gmail message (remove INBOX). Raises on failure."""
    mid = (message_id or "").strip()
    if not mid:
        raise ValueError("message_id is required")
    try:
        external_archive_message(mid)
    except Exception as e:
        logger.warning("[inbox] archive_candidate_email failed id=%s: %s", mid, e)
        raise


def count_inbox_bound_by_candidate(*, debug: bool = False) -> Dict[str, int]:
    """Live {candidate_id: n} for candidate-bound mailbox rows (alias From/To match)."""
    # Late: candidate aliases + dispatch task list (avoid module-top cycles).
    from src.core.candidate import email_aliases_for_candidate
    from src.data import database
    from src.utils.config import is_meteorite_email_mailbox_task_key

    messages = list_inbox_messages(debug=debug)
    seen: set[str] = set()
    counts: Dict[str, int] = {}
    for task in database.list_dispatch_tasks():
        if not is_meteorite_email_mailbox_task_key(task.get("task_key") or ""):
            continue
        cid = str(task.get("candidate_id") or "").strip()
        if not cid or cid in seen:
            continue
        seen.add(cid)
        alias_set = _alias_set_from_raw(email_aliases_for_candidate(cid))
        counts[cid] = len(_filter_messages_by_aliases(messages, alias_set))
    return counts


def count_inbox_messages_bound_to_candidate(
    candidate_id: str, *, debug: bool = False
) -> int:
    """Live count of INBOX messages matching this candidate's email aliases."""
    from src.core.candidate import email_aliases_for_candidate

    cid = str(candidate_id or "").strip()
    if not cid:
        return 0
    return len(fetch_candidate_email(email_aliases_for_candidate(cid), debug=debug))


@_with_log_debug
async def check_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """Candidate-bound mailbox: aliases → fetch → stage_meteorite → archive → stamp."""
    # Late: avoid import cycles (meteorite already imports inbox).
    from src.core.candidate import email_aliases_for_candidate
    from src.core.meteorite import stage_meteorite
    from src.data.database import (
        list_meteorites_by_source,
        update_candidate_last_email_check,
    )
    from src.utils.config import METEORITE_EMAIL_MAILBOX_CONFIG

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
    for msg in messages:
        processed += 1
        mid = str(msg.get("id") or "").strip()
        if not mid:
            logger.warning(
                "%s — %s\n  %s",
                cid,
                "message_id is required",
                "This message is not being staged",
            )
            errors += 1
            continue

        existing = list_meteorites_by_source("email", mid)
        if existing:
            logger.warning(
                "%s — %s\n  %s",
                cid,
                f"message {mid} already ingested",
                "No new meteorite rows are being inserted",
            )
            try:
                logger.debug("Calling archive_candidate_email: [message_id=%s]", mid)
                archive_candidate_email(mid)
                logger.debug("Response from archive_candidate_email: ok")
                passed += 1
            except Exception as exc:
                logger.exception(
                    "%s | inbox archive %s\n  %s: %s\n  The message was already ingested; archive did not finish",
                    cid, mid, type(exc).__name__, exc,
                )
                errors += 1
            continue

        payload = get_message_with_assembled_html(mid)
        blob = payload["assembled_html"]
        logger.debug(
            "Calling stage_meteorite: [candidate_id=%s, source_kind=email, source_id=%s]",
            cid, mid,
        )
        stage = await stage_meteorite(
            cid, blob, source_kind="email", source_id=mid, debug=debug,
        )
        logger.debug("Response from stage_meteorite: %s", stage)

        if stage.get("error"):
            errors += 1
            continue

        try:
            logger.debug("Calling archive_candidate_email: [message_id=%s]", mid)
            archive_candidate_email(mid)
            logger.debug("Response from archive_candidate_email: ok")
            # Skip / NOT_A_JOB → failed; landable READY/SCRAPE_LINK → passed (AST-1742).
            if stage.get("skipped"):
                failed += 1
            else:
                passed += 1
        except Exception as exc:
            next_step = (
                "Classify skipped; archive did not finish"
                if stage.get("skipped")
                else "Meteorite rows were staged; archive did not finish"
            )
            logger.exception(
                "%s | inbox archive %s\n  %s: %s\n  %s",
                cid, mid, type(exc).__name__, exc, next_step,
            )
            errors += 1
    logger.debug("End inbox message loop after %s items", n)

    update_candidate_last_email_check(cid)
    logger.debug("last_email_check stamped candidate_id=%s", cid)

    return {
        "total_processed": processed,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }


def get_message_html(message_id: str) -> GmailMessageHtml:
    """Return HTML body payload for one Gmail message id."""
    try:
        return external_get_message_html(message_id)
    except Exception as e:
        logger.warning("[inbox] get_message_html failed id=%s: %s", message_id, e)
        raise


def get_message_with_assembled_html(message_id: str) -> dict:
    """Gmail HTML payload plus assembled_html (header+body strip/wrap)."""
    payload = dict(get_message_html(message_id))
    payload["assembled_html"] = strip_extract_email_html(
        payload.get("subject") or "",
        payload.get("html_body") or "",
        from_address=payload.get("from_address") or "",
        to_address=payload.get("to_address") or "",
        date=payload.get("date") or "",
    )
    return payload


def strip_extract_email_html(
    subject: str,
    html_body: str,
    *,
    from_address: str = "",
    to_address: str = "",
    date: str = "",
) -> str:
    """Cull configured tags/attrs; wrap From/To/Subject/Date + body per INBOX_CREATE_JOB_CONFIG."""
    # B1 lazy import: bs4 is heavy and only needed on the Create strip path.
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_body or "", "html.parser")
    strip_tags = {t.casefold() for t in INBOX_CREATE_JOB_CONFIG["strip_tags"]}
    for tag in list(soup.find_all(True)):
        name = (tag.name or "").casefold()
        if name in strip_tags:
            tag.decompose()

    strip_attr = {a.casefold() for a in INBOX_CREATE_JOB_CONFIG["strip_attr_names"]}
    strip_on = bool(INBOX_CREATE_JOB_CONFIG["strip_on_attrs"])
    for tag in soup.find_all(True):
        attrs = getattr(tag, "attrs", None)
        if not isinstance(attrs, dict) or not attrs:
            continue
        for attr in list(attrs):
            if not isinstance(attr, str):
                continue
            key = attr.casefold()
            if key in strip_attr or (strip_on and key.startswith("on")):
                del tag.attrs[attr]

    if soup.body is not None:
        body = soup.body.decode_contents()
    else:
        body = soup.decode_contents()

    # AST-1131: unescape / unwrap nested Gmail auto-links before header wrap.
    body = normalize_pasted_list_email_html(body)

    escaped_from = html_module.escape(from_address or "", quote=True)
    escaped_to = html_module.escape(to_address or "", quote=True)
    escaped_subject = html_module.escape(subject or "", quote=True)
    escaped_date = html_module.escape(date or "", quote=True)
    return INBOX_CREATE_JOB_CONFIG["subject_html_template"].format(
        from_address=escaped_from,
        to_address=escaped_to,
        subject=escaped_subject,
        date=escaped_date,
        body=body,
    )
