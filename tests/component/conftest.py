"""Shared component env defaults (all pytest under tests/component/)."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("DEEPSEEK_API_KEY", "test-deepseek-key")

from src.utils import config as _cfg_mod

_SKIP_UNLESS_DISPATCH_SCHEDULABLE = pytest.mark.skipif(
    not hasattr(_cfg_mod, "DISPATCH_SCHEDULABLE_TASK_KEYS"),
    reason="DISPATCH_SCHEDULABLE_TASK_KEYS absent until AST-471 lands on branch",
)
