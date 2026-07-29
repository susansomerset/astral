"""
Inbox read orchestration for Meteorite seed (AST-1032).

Thin core wrapper over src.external.gmail list/get. No persistence, no admin HTTP.
AST-1033 owns the Read email admin surface and calls these functions.
AST-1047: From-address → candidate_match enrichment on list payloads.
"""

from __future__ import annotations

from src.core.candidate import get_candidate_id_for_query
from src.external.gmail import (
    GmailMessageHtml,
    get_message_html as external_get_message_html,
    list_inbox_messages as external_list_inbox_messages,
)
from src.utils.logging import get_logger, truncate_debug_content

logger = get_logger(__name__)


def _candidate_match_for_from(from_address: str, *, debug: bool = False) -> dict:
    cid = get_candidate_id_for_query(from_address or "", debug=debug)
    return {
        "matched": cid is not None,
        "astral_candidate_id": cid,
    }


def list_inbox_messages(debug: bool = False) -> list[dict]:
    """Return every INBOX message metadata row for GMAIL_USER, with From→candidate bind."""
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
        match = _candidate_match_for_from(msg.get("from_address") or "", debug=debug)
        row = dict(msg)
        row["candidate_match"] = match
        enriched.append(row)
        if debug:
            mid = (msg.get("id") or "")[:80]
            outcome = "found|matched" if match["matched"] else "found|none"
            logger.debug_index(
                func="inbox_from_bind",
                index=i,
                total=n,
                identifier=mid,
                outcome=outcome,
            )
            for line in truncate_debug_content(msg.get("from_address") or ""):
                logger.debug_detail(f"from_address={line}")
            if match["matched"]:
                logger.debug_detail(f"astral_candidate_id={match['astral_candidate_id']}")
    return enriched


def get_message_html(message_id: str) -> GmailMessageHtml:
    """Return HTML body payload for one Gmail message id."""
    try:
        return external_get_message_html(message_id)
    except Exception as e:
        logger.warning("[inbox] get_message_html failed id=%s: %s", message_id, e)
        raise
