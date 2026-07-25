"""Shared fixtures for integration scenarios (AST-711)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from flask import Flask

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Import-time env before external modules load (mirror component UI/external conftest).
os.environ.setdefault("ASTRAL_ALLOWED_IPS", "")
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
)


@pytest.fixture(autouse=True)
def _register_mock_authenticator(monkeypatch: pytest.MonkeyPatch) -> None:
    """AST-611 token stub — same map as tests/component/ui/conftest.py."""
    from src.utils import auth as utils_auth

    utils_auth._authenticate = None

    def _mock(token: str) -> dict:
        if token == "test-token":
            return {"user_id": "susan", "name": "Susan", "email": "susan@susansomerset.com"}
        if token == "good-jwt":
            return {"user_id": "u1", "name": "Test User", "email": "test@example.com"}
        if token == "non-admin-jwt":
            return {"user_id": "u2", "name": "Regular User", "email": "plain@example.com"}
        raise ValueError("invalid token")

    utils_auth.register_token_authenticator(_mock)
    monkeypatch.setattr(
        utils_auth,
        "AUTH_CONFIG",
        {
            "admin_user_ids": frozenset({"susan"}),
            "admin_emails": frozenset({"susan@susansomerset.com"}),
        },
        raising=False,
    )


@pytest.fixture
def integration_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Real SQLite per test — same pattern as tests/component/data/conftest.py."""
    monkeypatch.setenv("ASTRAL_DB_DIR", str(tmp_path))
    from src.data import database

    monkeypatch.setattr(database, "DB_PATH", tmp_path / "astral.db")
    for flag in _SCHEMA_FLAGS:
        setattr(database, flag, False)
    return database


@pytest.fixture
def seeded_candidate(integration_db):
    integration_db.save_candidate(
        "cand-1",
        state="ACTIVE_SEARCH",
        candidate_data={"name": "Integration Test"},
    )
    return integration_db


@pytest.fixture
def integration_app(monkeypatch: pytest.MonkeyPatch) -> Flask:
    """Minimal Flask app: system + candidate blueprints only (no core mocks)."""
    from ui.api.api_candidate import candidate_bp
    from ui.api.api_system import system_bp

    app = Flask(__name__)
    app.register_blueprint(system_bp)
    app.register_blueprint(candidate_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}
