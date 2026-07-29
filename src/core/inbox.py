"""
Inbox read orchestration for Meteorite seed (AST-1032).

Thin core wrapper over src.external.gmail list/get. No persistence, no admin HTTP.
AST-1033 owns the Read email admin surface and calls these functions.
"""

from __future__ import annotations

from src.external.gmail import (
    GmailInboxMessage,
    GmailMessageHtml,
    get_message_html as external_get_message_html,
    list_inbox_messages as external_list_inbox_messages,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)


def list_inbox_messages() -> list[GmailInboxMessage]:
    """Return every INBOX message metadata row for GMAIL_USER (read + unread)."""
    try:
        return external_list_inbox_messages()
    except Exception as e:
        logger.warning("[inbox] list_inbox_messages failed: %s", e)
        raise


def get_message_html(message_id: str) -> GmailMessageHtml:
    """Return HTML body payload for one Gmail message id."""
    try:
        return external_get_message_html(message_id)
    except Exception as e:
        logger.warning("[inbox] get_message_html failed id=%s: %s", message_id, e)
        raise
