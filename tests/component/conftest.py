"""Shared component env defaults (all pytest under tests/component/)."""

from __future__ import annotations

import os

os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("DEEPSEEK_API_KEY", "test-deepseek-key")
os.environ.setdefault("GMAIL_USER", "astral.test@example.com")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test-refresh-token")

# AST-960 deleted DISPATCH_SCHEDULABLE_TASK_KEYS — historical ftr tips that still
# needed the constant used local skipifs beside the asserting module (see bible §7.12c).

