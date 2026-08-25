"""
Inbox read orchestration for Meteorite seed (AST-1032).

Thin core wrapper over src.external.gmail list/get. No persistence, no admin HTTP.
AST-1033 owns the Read email admin surface and calls these functions.
AST-1047 / AST-1313: From-then-To → candidate_match enrichment on list payloads.
AST-1049: strip/extract + Create orchestration.
AST-1061: Create routes through gazer email ingest (Playwright + dedupe) → multi create.
"""

from __future__ import annotations

import html as html_module
from email.utils import getaddresses, parseaddr
from typing import Dict

from src.core.candidate import get_candidate_id_for_query
from src.core.gazer import ingest_meteorite_jobs_from_email_html_sync
from src.external.gmail import (
    GmailMessageHtml,
    get_message_html as external_get_message_html,
    list_inbox_messages as external_list_inbox_messages,
)
from src.utils.config import INBOX_BIND_CONFIG, INBOX_CREATE_JOB_CONFIG, METEORITE_CONFIG
from src.utils.formatting import normalize_pasted_list_email_html
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)


def _inbox_addr_folded() -> str:
    raw = INBOX_BIND_CONFIG["inbox_address"] or ""
    _display, parsed = parseaddr(raw)
    token = (parsed or raw).strip()
    return token.casefold()


def _remaining_to_addresses(to_header: str) -> list[str]:
    # Unique remaining mailbox tokens after dropping the Astral inbox (casefold).
    inbox = _inbox_addr_folded()
    remaining: list[str] = []
    seen: set[str] = set()
    for _display, addr in getaddresses([to_header or ""]):
        token = (addr or "").strip()
        if not token or "@" not in token:
            continue
        folded = token.casefold()
        if inbox and folded == inbox:
            continue
        if folded in seen:
            continue
        seen.add(folded)
        remaining.append(token)
    return remaining


def _bind_inbox_message(
    from_address: str,
    to_address: str,
    *,
    debug: bool = False,
) -> tuple[dict, str, str]:
    """From unique hit wins; else To when exactly one remaining address uniquely matches.

    Returns (candidate_match, bind_header, bind_address).
    bind_header is "from", "to", or "" when no header was eligible / no unique hit.
    candidate_match shape is only {"matched", "astral_candidate_id"} — do not add bind_header.
    """
    bind_header = ""
    bind_address = ""
    cid = None
    for header in INBOX_BIND_CONFIG["header_order"]:
        if header == "from":
            raw = from_address or ""
            cid = get_candidate_id_for_query(raw, debug=debug)
            if cid is None:
                continue
            bind_header = "from"
            _display, parsed = parseaddr(raw)
            bind_address = (parsed or "").strip() or raw.strip()
            break
        if header == "to":
            remaining = _remaining_to_addresses(to_address or "")
            if len(remaining) != 1:
                continue
            raw = remaining[0]
            cid = get_candidate_id_for_query(raw, debug=debug)
            bind_header = "to"
            bind_address = raw
            break
        raise ValueError(f"unsupported inbox bind header: {header!r}")
    return (
        {"matched": cid is not None, "astral_candidate_id": cid},
        bind_header,
        bind_address,
    )


def list_inbox_messages(debug: bool = False) -> list[dict]:
    """Return every INBOX message metadata row for GMAIL_USER, with From-then-To candidate bind."""
    if debug:
        logger.set_debug_flag(True)
    try:
        messages = external_list_inbox_messages()
    except Exception as e:
        logger.warning("[inbox] list_inbox_messages failed: %s", e)
        raise

    enriched: list[dict] = []
    n = len(messages)
    for i, msg in enumerate(messages, start=1):
        match, bind_header, bind_address = _bind_inbox_message(
            msg.get("from_address") or "",
            msg.get("to_address") or "",
            debug=debug,
        )
        row = dict(msg)
        row["candidate_match"] = match
        enriched.append(row)
        if debug:
            mid = (msg.get("id") or "")[:80]
            outcome = "found|matched" if match["matched"] else "found|none"
            logger.debug_index(
                func="inbox_bind",
                index=i,
                total=n,
                identifier=mid,
                outcome=outcome,
            )
            logger.debug_detail(f"bind_header={bind_header}")
            for line in truncate_debug_content(bind_address):
                logger.debug_detail(f"bind_address={line}")
            if match["matched"]:
                logger.debug_detail(f"astral_candidate_id={match['astral_candidate_id']}")
            else:
                logger.debug_detail("astral_candidate_id=")
    return enriched


def count_inbox_bound_by_candidate(*, debug: bool = False) -> Dict[str, int]:
    """One inbox list → {astral_candidate_id: message_count} for matched From-then-To binds."""
    counts: Dict[str, int] = {}
    for msg in list_inbox_messages(debug=debug):
        match = msg.get("candidate_match") or {}
        if not match.get("matched"):
            continue
        cid = str(match.get("astral_candidate_id") or "").strip()
        if not cid:
            continue
        counts[cid] = counts.get(cid, 0) + 1
    return counts


def count_inbox_messages_bound_to_candidate(
    candidate_id: str, *, debug: bool = False
) -> int:
    """Live count of current inbox messages whose From-then-To bind is candidate_id."""
    cid = str(candidate_id or "").strip()
    if not cid:
        return 0
    return int(count_inbox_bound_by_candidate(debug=debug).get(cid, 0))


def get_message_html(message_id: str) -> GmailMessageHtml:
    """Return HTML body payload for one Gmail message id."""
    try:
        return external_get_message_html(message_id)
    except Exception as e:
        logger.warning("[inbox] get_message_html failed id=%s: %s", message_id, e)
        raise


def strip_extract_email_html(subject: str, html_body: str) -> str:
    """Cull configured tags/attrs; wrap subject + body per INBOX_CREATE_JOB_CONFIG."""
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

    # AST-1131: unescape / unwrap nested Gmail auto-links before subject wrap.
    body = normalize_pasted_list_email_html(body)

    escaped_subject = html_module.escape(subject or "", quote=True)
    return INBOX_CREATE_JOB_CONFIG["subject_html_template"].format(
        subject=escaped_subject,
        body=body,
    )


def create_meteorite_job_from_inbox_message(
    message_id: str,
    *,
    debug: bool = False,
) -> dict:
    """Fetch message, rematch From-then-To→candidate, strip/extract, gazer ingest → meteorite jobs."""
    mid = (message_id or "").strip()
    if not mid:
        raise ValueError("message_id is required")
    if debug:
        logger.set_debug_flag(True)

    payload = get_message_html(mid)
    subject = payload.get("subject") or ""
    from_address = payload.get("from_address") or ""
    to_address = payload.get("to_address") or ""
    raw_html = payload.get("html_body") or ""
    if debug:
        logger.debug_index(
            func="inbox_create_job",
            index=1,
            total=4,
            identifier=mid[:80],
            outcome="found",
        )
        logger.debug_detail(f"message_id={mid[:80]}")
        for line in truncate_debug_content(subject):
            logger.debug_detail(f"subject={line}")
        logger.debug_detail(f"raw_html_len={len(raw_html)}")

    match, bind_header, bind_address = _bind_inbox_message(
        from_address, to_address, debug=False
    )
    cid = match["astral_candidate_id"] if match["matched"] else None
    if cid is None:
        raise ValueError("message is not matched to a candidate")
    if debug:
        logger.debug_index(
            func="inbox_create_job",
            index=2,
            total=4,
            identifier=mid[:80],
            outcome="matched",
        )
        logger.debug_detail(f"astral_candidate_id={cid}")
        logger.debug_detail(f"bind_header={bind_header}")
        for line in truncate_debug_content(bind_address):
            logger.debug_detail(f"bind_address={line}")

    html = strip_extract_email_html(subject, raw_html)
    if not html.strip():
        raise ValueError("stripped email HTML is empty")
    if debug:
        logger.debug_index(
            func="inbox_create_job",
            index=3,
            total=4,
            identifier=mid[:80],
            outcome="extracted",
        )
        for line in truncate_debug_content(html):
            logger.debug_detail(line)

    ingest = ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=debug)
    created = ingest.get("created") or []
    skipped = ingest.get("skipped") or []
    if not created and not skipped:
        raise ValueError("no meteorite jobs created")

    if debug:
        logger.debug_index(
            func="inbox_create_job",
            index=4,
            total=4,
            identifier=mid[:80],
            outcome="recorded" if created else "skipped",
        )
        logger.debug_detail(
            f"created={len(created)} skipped={len(skipped)} mode={ingest.get('mode')}"
        )
        if created:
            logger.debug_detail(f"astral_job_id={created[0].get('astral_job_id')}")

    company_fallback = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
    first = created[0] if created else None
    return {
        "astral_candidate_id": cid,
        "mode": ingest.get("mode"),
        "created": created,
        "skipped": skipped,
        "astral_job_id": first["astral_job_id"] if first else None,
        "company": first["company"] if first else company_fallback,
        "state": first["state"] if first else None,
        "latest_score": first["latest_score"] if first else None,
        "company_inserted": any(c.get("company_inserted") for c in created),
    }
