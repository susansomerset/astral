"""
Gmail API send + inbox read for ASTRAL.

Owns Gmail send and inbox list/get via one dual-scope OAuth client
(gmail.send + gmail.readonly). send_email returns True/False and never raises
on transient failures; list/get raise so callers can map hard failures.

Required env vars (validated at import time — missing vars raise RuntimeError at server startup):
  GMAIL_USER            — mailbox identity (e.g. astral.career.match@gmail.com)
  GOOGLE_CLIENT_ID      — OAuth2 client ID
  GOOGLE_CLIENT_SECRET  — OAuth2 client secret
  GOOGLE_REFRESH_TOKEN  — OAuth2 refresh token (long-lived, dual-scope)

Optional env vars:
  GOOGLE_TOKEN_URI      — defaults to https://oauth2.googleapis.com/token

Does not use GOOGLE_CSE_API_KEY / GOOGLE_CSE_ID.
"""

from __future__ import annotations

import base64
import os
from email.mime.text import MIMEText
from typing import TypedDict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.utils.integration_io import require_controlled_external_io

__all__ = [
    "GmailInboxMessage",
    "GmailMessageHtml",
    "send_email",
    "list_inbox_messages",
    "get_message_html",
]


class GmailInboxMessage(TypedDict):
    id: str
    thread_id: str
    subject: str
    from_address: str
    date: str
    unread: bool


class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
    subject: str
    from_address: str


# ---------------------------------------------------------------------------
# Startup validation — fail loud at import time rather than silently at send time
# ---------------------------------------------------------------------------

_REQUIRED_VARS = ["GMAIL_USER", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"]
_missing = [v for v in _REQUIRED_VARS if not os.environ.get(v)]
if _missing:  # pragma: no cover
    raise RuntimeError(f"gmail.py: missing required env vars: {', '.join(_missing)}")

_GMAIL_USER = os.environ["GMAIL_USER"]
_TOKEN_URI = os.environ.get("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token")

_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]
_LIST_PAGE_SIZE = 500  # Gmail API page size only — not a result cap; paginate until exhausted


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email via the Gmail API. Returns True on success."""
    require_controlled_external_io("gmail.send_email")
    try:
        service = _build_service()

        msg = MIMEText(body, "plain")
        msg["to"] = to
        msg["from"] = _GMAIL_USER
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return True
    except Exception:
        return False


def list_inbox_messages() -> list[GmailInboxMessage]:
    """Return every INBOX message (read + unread) with identifying metadata."""
    require_controlled_external_io("gmail.list_inbox_messages")
    service = _build_service()
    message_ids: list[str] = []
    page_token: str | None = None
    while True:
        kwargs: dict = {
            "userId": "me",
            "labelIds": ["INBOX"],
            "maxResults": _LIST_PAGE_SIZE,
        }
        if page_token:
            kwargs["pageToken"] = page_token
        listed = service.users().messages().list(**kwargs).execute()
        for row in listed.get("messages") or []:
            mid = row.get("id")
            if isinstance(mid, str) and mid:
                message_ids.append(mid)
        page_token = listed.get("nextPageToken")
        if not page_token:
            break

    results: list[GmailInboxMessage] = []
    for message_id in message_ids:
        raw = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        results.append(_message_metadata(raw if isinstance(raw, dict) else {}))
    return results


def get_message_html(message_id: str) -> GmailMessageHtml:
    """Return HTML body + Subject/From for one Gmail message id (empty html if no HTML part)."""
    require_controlled_external_io("gmail.get_message_html")
    service = _build_service()
    raw = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = raw.get("payload") if isinstance(raw, dict) else None
    payload_dict = payload if isinstance(payload, dict) else {}
    headers = _header_map(payload_dict.get("headers"))
    return {
        "id": message_id,
        "html_body": _extract_html_body(payload_dict),
        "subject": headers.get("subject", ""),
        "from_address": headers.get("from", ""),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_credentials() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri=_TOKEN_URI,
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=_GMAIL_SCOPES,
    )


def _build_service():
    return build("gmail", "v1", credentials=_build_credentials())


def _header_map(payload_headers) -> dict[str, str]:
    out: dict[str, str] = {}
    if not isinstance(payload_headers, list):
        return out
    for row in payload_headers:
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        value = row.get("value")
        if isinstance(name, str) and isinstance(value, str):
            out[name.lower()] = value
    return out


def _decode_b64url(data: str) -> str:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8", errors="replace")


def _extract_html_body(payload: dict) -> str:
    # Prefer first text/html part; do not invent HTML from text/plain.
    mime = payload.get("mimeType")
    body = payload.get("body") if isinstance(payload.get("body"), dict) else {}
    data = body.get("data")
    if mime == "text/html" and isinstance(data, str) and data:
        return _decode_b64url(data)
    parts = payload.get("parts")
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, dict):
                found = _extract_html_body(part)
                if found:
                    return found
    return ""


def _message_metadata(raw: dict) -> GmailInboxMessage:
    payload = raw.get("payload") if isinstance(raw.get("payload"), dict) else {}
    headers = _header_map(payload.get("headers"))
    label_ids = raw.get("labelIds") or []
    thread_id = raw.get("threadId")
    msg_id = raw.get("id")
    return {
        "id": msg_id if isinstance(msg_id, str) else "",
        "thread_id": thread_id if isinstance(thread_id, str) else "",
        "subject": headers.get("subject", ""),
        "from_address": headers.get("from", ""),
        "date": headers.get("date", ""),
        "unread": "UNREAD" in label_ids if isinstance(label_ids, list) else False,
    }
