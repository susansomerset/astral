#!/usr/bin/env python3
"""Local/dev Slack Socket Mode listener (AST-1069).

Production must use the Events API Request URL (`POST /api/slack/events`).
This script opens Socket Mode and feeds Events API-shaped payloads into
``contact.handle_slack_event`` — same inbound path as the webhook.

Requires environ: SLACK_APP_TOKEN, SLACK_BOT_TOKEN (names from CONTACT_CONFIG).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

from dotenv import load_dotenv

load_dotenv(_REPO / ".env")

from src.core.contact import handle_slack_event  # noqa: E402
from src.external.slack import open_socket_mode_connection  # noqa: E402
from src.utils.config import CONTACT_CONFIG  # noqa: E402


def main() -> int:
    app_env = CONTACT_CONFIG["app_token_env"]
    bot_env = CONTACT_CONFIG["bot_token_env"]
    missing = [n for n in (app_env, bot_env) if not os.environ.get(n)]
    if missing:
        print(
            f"slack_socket_mode_dev: missing environ {', '.join(missing)} "
            "(local/dev Socket Mode only)",
            file=sys.stderr,
        )
        return 1

    def _on_payload(payload: dict) -> None:
        handle_slack_event(payload, debug=True)

    print(
        "slack_socket_mode_dev: connecting (local/dev only; "
        "production uses /api/slack/events)…",
        flush=True,
    )
    open_socket_mode_connection(_on_payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
