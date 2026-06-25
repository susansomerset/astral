"""Shared core-layer fixtures for component tests (AST-393)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock

import pytest

os.environ.setdefault("GMAIL_USER", "astral.test@example.com")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test-refresh-token")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")

_SCHEMA_FLAGS = (
    "_company_schema_ensured",
    "_job_schema_ensured",
    "_candidate_schema_ensured",
    "_company_candidate_fk_ensured",
    "_company_job_scan_schema_ensured",
    "_agent_responses_schema_ensured",
    "_agent_schema_ensured",
    "_agent_task_schema_ensured",
    "_timesheets_schema_ensured",
    "_dispatch_task_schema_ensured",
    "_dispatch_ledger_schema_ensured",
    "_app_log_schema_ensured",
    "_agent_data_schema_ensured",
    "_company_search_terms_schema_ensured",
    "_company_search_terms_migration_swept",
    "_intake_session_schema_ensured",
    "_rubric_vector_schema_ensured",
    "_vector_feedback_schema_ensured",
    "_ast723_rubric_token_migration_applied",
)


@pytest.fixture
def sqlite_in_memory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Fresh astral.db file per test; real SQLite for core integration paths."""
    monkeypatch.setenv("ASTRAL_DB_DIR", str(tmp_path))
    from src.data import database

    monkeypatch.setattr(database, "DB_PATH", tmp_path / "astral.db")
    for flag in _SCHEMA_FLAGS:
        setattr(database, flag, False)
    return database


@pytest.fixture
def seeded_db(sqlite_in_memory):
    """Candidate row for tests that need a parent candidate."""
    db = sqlite_in_memory
    db.save_candidate("cand-1", state="NEW", candidate_data={"name": "Test"})
    return db


@pytest.fixture(autouse=True)
def _core_default_anthropic_llm_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Legacy core mocks patch send_to_anthropic; product default active_provider is deepseek."""
    from src.utils import config as cfg_mod

    monkeypatch.setattr(cfg_mod, "get_active_llm_provider", lambda: "anthropic")
    import importlib

    for mod_name in ("src.core.agent", "src.core.consult"):
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "get_active_llm_provider"):
            monkeypatch.setattr(mod, "get_active_llm_provider", lambda: "anthropic")
        if hasattr(mod, "send_to_deepseek"):
            monkeypatch.setattr(mod, "send_to_deepseek", AsyncMock())


@pytest.fixture
def log_entries() -> List[Dict[str, Any]]:
    return [
        {"created_at": "2026-05-13 12:00:00", "level": "INFO", "message": "older"},
        {"created_at": "2026-05-13 12:00:01", "level": "ERROR", "message": "newer"},
    ]
