"""In-memory SQLite fixtures for data-layer component tests (AST-392)."""

from __future__ import annotations

from pathlib import Path

import pytest

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
    "_rubric_vector_schema_ensured",
    "_vector_feedback_schema_ensured",
    "_rubric_vector_backfill_swept",
    "_ast723_rubric_token_migration_applied",
)


@pytest.fixture
def sqlite_in_memory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Fresh astral.db file per test; real SQLite, no mocks."""
    monkeypatch.setenv("ASTRAL_DB_DIR", str(tmp_path))
    from src.data import database

    monkeypatch.setattr(database, "DB_PATH", tmp_path / "astral.db")
    for flag in _SCHEMA_FLAGS:
        setattr(database, flag, False)
    return database


@pytest.fixture
def seeded_db(sqlite_in_memory):
    """Candidate row for clusters that need a parent candidate."""
    db = sqlite_in_memory
    db.save_candidate("cand-1", state="NEW", candidate_data={"name": "Test"})
    return db


@pytest.fixture
def db_factory(seeded_db):
    """Alias while cluster fixtures grow; same as seeded_db today."""
    return seeded_db
