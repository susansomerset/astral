"""
Gmail API email sender for ASTRAL.

Sends email via the Gmail API using OAuth2 credentials from environment variables.
Returns True/False — never raises on transient failures. Caller (core layer) decides how to log.

Required env vars (validated at import time — missing vars raise RuntimeError at server startup):
  GMAIL_USER            — the sending address (e.g. astral.career.match@gmail.com)
  GOOGLE_CLIENT_ID      — OAuth2 client ID
  GOOGLE_CLIENT_SECRET  — OAuth2 client secret
  GOOGLE_REFRESH_TOKEN  — OAuth2 refresh token (long-lived)

Optional env vars:
  GOOGLE_TOKEN_URI      — defaults to https://oauth2.googleapis.com/token
"""

import base64
import os
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ---------------------------------------------------------------------------
# Startup validation — fail loud at import time rather than silently at send time
# ---------------------------------------------------------------------------

_REQUIRED_VARS = ["GMAIL_USER", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"]
_missing = [v for v in _REQUIRED_VARS if not os.environ.get(v)]
if _missing:  # pragma: no cover
    raise RuntimeError(f"gmail.py: missing required env vars: {', '.join(_missing)}")

_GMAIL_USER = os.environ["GMAIL_USER"]
_TOKEN_URI = os.environ.get("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token")


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email via the Gmail API. Returns True on success."""
    try:
        creds = Credentials(
            token=None,
            refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
            token_uri=_TOKEN_URI,
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )
        service = build("gmail", "v1", credentials=creds)

        msg = MIMEText(body, "plain")
        msg["to"] = to
        msg["from"] = _GMAIL_USER
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return True
    except Exception:
        return False
