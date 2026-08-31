"""
Inbox read orchestration + fetch_email → stage_meteorite (AST-1531).

Thin core wrapper over src.external.gmail list/get. No gaze_email.
AST-1033 owns the Read email admin surface and calls these functions.
AST-1047 / AST-1313: From-then-To → candidate_match enrichment on list payloads.
AST-1049 / AST-1472 / AST-1537: strip/extract + header+body assembly ownership
stays here; land/fetch_email and message-get share that shape; Land/fetch_email
stage then land-inside-stage (not raw land_meteorite on the stripped blob).
"""

from __future__ import annotations

import asyncio
import html as html_module
from email.utils import getaddresses, parseaddr
from typing import Any, Dict, List, Optional

from src.core.candidate import get_candidate_id_for_query
from src.external.gmail import (
    GmailMessageHtml,
    get_message_html as external_get_message_html,
    list_inbox_messages as external_list_inbox_messages,
)
from src.utils.config import (
    FETCH_EMAIL_CONFIG,
    INBOX_BIND_CONFIG,
    INBOX_CREATE_JOB_CONFIG,
    METEORITE_CONFIG,
    METEORITE_EMAIL_MAILBOX_CONFIG,
    STAGE_METEORITE_CONFIG,
)
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


async def _land_bound_inbox_message(
    message_id: str,
    candidate_id: str,
    *,
    debug: bool = False,
) -> dict:
    """Fetch + strip one bound message, then stage_meteorite (AST-1531)."""
    mid = (message_id or "").strip()
    cid = (candidate_id or "").strip()
    err_key = METEORITE_CONFIG["land_outcome_error"]
    dbg_func = FETCH_EMAIL_CONFIG.get("debug_func") or "inbox.land_bound_message"

    payload = get_message_html(mid)
    subject = payload.get("subject") or ""
    raw_html = payload.get("html_body") or ""
    html = strip_extract_email_html(
        subject,
        raw_html,
        from_address=payload.get("from_address") or "",
        to_address=payload.get("to_address") or "",
        date=payload.get("date") or "",
    )
    if not html.strip():
        if debug:
            logger.set_debug_flag(True)
            logger.debug_index(
                func=dbg_func,
                index=1,
                total=1,
                identifier=mid[:80],
                outcome=err_key,
            )
            logger.debug_detail(f"message_id={mid[:80]}")
            logger.debug_detail(f"astral_candidate_id={cid}")
            logger.debug_detail("html_len=0")
        return {
            "outcome": err_key,
            "error": "stripped email HTML is empty",
            "outcomes": [],
            "company": None,
            "company_inserted": False,
        }

    from src.core.meteorite import stage_meteorite

    stage = await stage_meteorite(
        cid,
        html,
        source_kind="email",
        source_id=mid,
        debug=debug,
    )
    if debug:
        logger.set_debug_flag(True)
        logger.debug_index(
            func=dbg_func,
            index=1,
            total=1,
            identifier=mid[:80],
            outcome=str(stage.get("outcome") or err_key),
        )
        logger.debug_detail(f"message_id={mid[:80]}")
        logger.debug_detail(f"astral_candidate_id={cid}")
        logger.debug_detail(f"html_len={len(html)}")
        logger.debug_detail(f"stage_outcome={stage.get('stage_outcome')!r}")
        logger.debug_detail(f"skipped={stage.get('skipped')!r}")
        logger.debug_detail(f"company={stage.get('company')!r}")
    return stage


async def run_fetch_email(
    task: Optional[dict] = None,
    *,
    debug: bool = False,
) -> dict:
    """Null-candidate fetch_email shell: list → bind → stage matched (AST-1531)."""
    _ = task  # shell row — no entity claim queue
    if debug:
        logger.set_debug_flag(True)

    messages = list_inbox_messages(debug=debug)
    created_k = METEORITE_CONFIG["land_outcome_created"]
    skip_k = METEORITE_CONFIG["land_outcome_duplicate_skip"]
    super_k = METEORITE_CONFIG["land_outcome_superseded"]
    err_k = METEORITE_CONFIG["land_outcome_error"]

    total_processed = total_passed = total_failed = total_errors = 0
    n = len(messages)
    dbg_func = FETCH_EMAIL_CONFIG.get("debug_func") or "inbox.fetch_email"

    for i, msg in enumerate(messages, start=1):
        mid = (msg.get("id") or "").strip()
        match = msg.get("candidate_match") or {}
        cid = str(match.get("astral_candidate_id") or "").strip()
        if debug:
            logger.debug_index(
                func=dbg_func,
                index=i,
                total=n,
                identifier=mid[:80] or "?",
                outcome="found",
            )
        if not match.get("matched") or not cid:
            total_processed += 1
            total_passed += 1
            if debug:
                logger.debug_index(
                    func=dbg_func,
                    index=i,
                    total=n,
                    identifier=mid[:80] or "?",
                    outcome="skipped-unbound",
                )
            continue

        land = await _land_bound_inbox_message(mid, cid, debug=debug)
        outcome = land.get("outcome") or err_k
        total_processed += 1
        if (
            land.get("skipped")
            or outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]
            or outcome in (created_k, skip_k, super_k)
        ):
            total_passed += 1
        elif outcome == err_k:
            total_failed += 1
            if land.get("error"):
                total_errors += 1
        else:
            total_failed += 1

    return {
        "total_processed": total_processed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
    }


async def land_inbox_message_ids(
    message_ids: list[str],
    *,
    debug: bool = False,
) -> dict:
    """Admin Land Meteorite: selected inbox ids → stage_meteorite (AST-1531)."""
    if debug:
        logger.set_debug_flag(True)

    normalized_ids = [raw.strip() for raw in (message_ids or []) if (raw or "").strip()]
    by_id = {(m.get("id") or ""): m for m in list_inbox_messages(debug=debug)}

    skip_missing = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_not_in_inbox"]
    skip_unbound = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_unbound"]
    skip_unmatched = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_unmatched"]
    created_k = METEORITE_CONFIG["land_outcome_created"]
    skip_k = METEORITE_CONFIG["land_outcome_duplicate_skip"]
    super_k = METEORITE_CONFIG["land_outcome_superseded"]
    err_k = METEORITE_CONFIG["land_outcome_error"]

    results: list[dict] = []
    total_processed = total_passed = total_failed = total_errors = total_skipped = 0

    for mid in normalized_ids:
        if mid not in by_id:
            results.append(
                {"message_id": mid, "outcome": skip_missing, "astral_candidate_id": None}
            )
            total_skipped += 1
            total_processed += 1
            continue

        msg = by_id[mid]
        match = msg.get("candidate_match") or {}
        cid = str(match.get("astral_candidate_id") or "").strip()
        if not match.get("matched"):
            results.append(
                {
                    "message_id": mid,
                    "outcome": skip_unbound,
                    "astral_candidate_id": None,
                }
            )
            total_skipped += 1
            total_processed += 1
            continue
        if not cid:
            results.append(
                {
                    "message_id": mid,
                    "outcome": skip_unmatched,
                    "astral_candidate_id": None,
                }
            )
            total_skipped += 1
            total_processed += 1
            continue

        land = await _land_bound_inbox_message(mid, cid, debug=debug)
        land_outcome = land.get("outcome") or err_k
        results.append(
            {
                "message_id": mid,
                "outcome": land_outcome,
                "astral_candidate_id": cid,
                "land": land,
            }
        )
        total_processed += 1
        if (
            land.get("skipped")
            or land_outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]
            or land_outcome in (created_k, skip_k, super_k)
        ):
            total_passed += 1
        elif land_outcome == err_k:
            total_failed += 1
            if land.get("error"):
                total_errors += 1
        else:
            total_failed += 1

    return {
        "results": results,
        "total_processed": total_processed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "total_skipped": total_skipped,
    }


def create_meteorite_job_from_inbox_message(
    message_id: str,
    *,
    debug: bool = False,
) -> dict:
    """Fetch message, rematch From-then-To→candidate, strip/extract, land_meteorite."""
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

    html = strip_extract_email_html(
        subject,
        raw_html,
        from_address=from_address,
        to_address=to_address,
        date=payload.get("date") or "",
    )
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

    # Late-import: land already strip-validated above — skip second Gmail get.
    from src.core.meteorite import land_meteorite

    land = asyncio.run(land_meteorite(cid, text=html, debug=debug))
    created_k = METEORITE_CONFIG["land_outcome_created"]
    skip_k = METEORITE_CONFIG["land_outcome_duplicate_skip"]
    super_k = METEORITE_CONFIG["land_outcome_superseded"]
    outcomes = land.get("outcomes") or []
    created = [o for o in outcomes if o.get("outcome") == created_k]
    skipped = [o for o in outcomes if o.get("outcome") in (skip_k, super_k)]
    first_id = outcomes[0].get("astral_job_id") if outcomes else None

    if debug:
        logger.debug_index(
            func="inbox_create_job",
            index=4,
            total=4,
            identifier=mid[:80],
            outcome=str(land.get("outcome") or "recorded"),
        )
        logger.debug_detail(
            f"created={len(created)} skipped={len(skipped)} mode=land_meteorite"
        )
        logger.debug_detail(f"company={land.get('company')!r}")
        if first_id:
            logger.debug_detail(f"astral_job_id={first_id}")

    return {
        "astral_candidate_id": cid,
        "outcome": land.get("outcome"),
        "outcomes": outcomes,
        "company": land.get("company"),
        "company_inserted": bool(land.get("company_inserted")),
        "error": land.get("error"),
        "astral_job_id": first_id,
        "created": created,
        "skipped": skipped,
        "mode": "land_meteorite",
        "state": None,
        "latest_score": None,
    }
