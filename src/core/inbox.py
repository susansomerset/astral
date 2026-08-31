"""
Candidate-scoped Gmail list/filter (`fetch_candidate_email`) + archive
(`archive_candidate_email`); thin unenriched `list_inbox_messages` for Manage
Email All; keep `get_message_html` / assembled HTML / `strip_extract_email_html`.

No From-then-To bind, no `fetch_email` runner, no land-bound stage entrypoints
(AST-1558). Land for admin is owned by `api_inbox` → meteorite.
"""

from __future__ import annotations

import html as html_module
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
from src.utils.logging import get_logger

logger = get_logger(__name__)


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


def fetch_candidate_email(
    aliases: Sequence[str],
    *,
    debug: bool = False,
) -> list[dict]:
    """List inbox messages whose From or To address matches any alias (casefold)."""
    if debug:
        logger.set_debug_flag(True)

    alias_set: set[str] = set()
    for raw in aliases or ():
        _display, parsed = parseaddr(raw or "")
        token = (parsed or raw or "").strip()
        if not token or "@" not in token:
            continue
        alias_set.add(token.casefold())
    if not alias_set:
        return []

    kept: list[dict] = []
    for msg in list_inbox_messages(debug=debug):
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
    """Retired with From-then-To bind (AST-1558); empty until AST-1559 eligibility."""
    _ = debug
    return {}


def count_inbox_messages_bound_to_candidate(
    candidate_id: str, *, debug: bool = False
) -> int:
    """Retired with From-then-To bind (AST-1558); 0 until AST-1559 eligibility."""
    _ = candidate_id
    _ = debug
    return 0


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
