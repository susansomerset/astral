"""Shared component env defaults (all pytest under tests/component/)."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("DEEPSEEK_API_KEY", "test-deepseek-key")
os.environ.setdefault("GMAIL_USER", "astral.test@example.com")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test-refresh-token")

from src.utils import config as _cfg_mod

_SKIP_UNLESS_DISPATCH_SCHEDULABLE = pytest.mark.skipif(
    not hasattr(_cfg_mod, "DISPATCH_SCHEDULABLE_TASK_KEYS"),
    reason="DISPATCH_SCHEDULABLE_TASK_KEYS absent until AST-471 lands on branch",
)
