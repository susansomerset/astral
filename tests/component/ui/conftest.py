"""Shared Flask UI fixtures for component tests (AST-394)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

os.environ.setdefault("ASTRAL_ALLOWED_IPS", "")
os.environ.setdefault("GMAIL_USER", "astral.test@example.com")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test-refresh-token")


@pytest.fixture(autouse=True)
def _ui_default_anthropic_llm_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.utils import config as cfg_mod

    monkeypatch.setattr(cfg_mod, "get_active_llm_provider", lambda: "anthropic")
    import importlib

    mod = importlib.import_module("src.ui.api.api_admin")
    monkeypatch.setattr(mod, "get_active_llm_provider", lambda: "anthropic")


@pytest.fixture(autouse=True)
def _register_mock_authenticator(monkeypatch: pytest.MonkeyPatch) -> None:
    """AST-611: Stytch validate_bearer_token stub for UI route tests."""
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
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def non_admin_headers() -> dict[str, str]:
    return {"Authorization": "Bearer non-admin-jwt"}


_DB_SCHEMA_FLAGS = (
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
)


@pytest.fixture
def seeded_db(tmp_path, monkeypatch: pytest.MonkeyPatch):
    """Real SQLite for UI routes that write through core/database (AST-524)."""
    monkeypatch.setenv("ASTRAL_DB_DIR", str(tmp_path))
    from src.data import database

    monkeypatch.setattr(database, "DB_PATH", tmp_path / "astral.db")
    for flag in _DB_SCHEMA_FLAGS:
        setattr(database, flag, False)
    database.save_candidate("cand-1", state="NEW", candidate_data={"name": "Test"})
    return database


@pytest.fixture
def system_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[FlaskClient]:
    monkeypatch.setattr("src.core.candidate.get_candidate", lambda candidate_id: {"state": "LIVE_PROMPTS"})
    app = Flask(__name__)
    from ui.api.api_system import system_bp

    app.register_blueprint(system_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def candidate_client() -> Iterator[FlaskClient]:
    app = Flask(__name__)
    from ui.api.api_candidate import candidate_bp

    app.register_blueprint(candidate_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def companies_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[FlaskClient]:
    monkeypatch.setattr("ui.api.api_companies.list_companies", lambda **kwargs: [{"short_name": "acme", "company_data": {}}])
    monkeypatch.setattr("ui.api.api_companies.get_active_trigger_states", lambda *args, **kwargs: ["WATCH"])
    monkeypatch.setattr("ui.api.api_companies.count_companies", lambda **kwargs: 1)
    monkeypatch.setattr("ui.api.api_companies.list_company_job_scans", lambda **kwargs: [])
    monkeypatch.setattr("ui.api.api_companies.get_company", lambda short_name: None)
    app = Flask(__name__)
    from ui.api.api_companies import companies_bp

    app.register_blueprint(companies_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def jobs_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[FlaskClient]:
    monkeypatch.setattr("ui.api.api_jobs.list_jobs", lambda **kwargs: [])
    monkeypatch.setattr("ui.api.api_jobs.score_floor_by_trigger_for_candidate", lambda candidate_id: {})
    monkeypatch.setattr("ui.api.api_jobs.list_jobs_below_dispatch_score_floor", lambda candidate_id: [])
    monkeypatch.setattr("ui.api.api_jobs.get_job", lambda job_id: None)
    app = Flask(__name__)
    from ui.api.api_jobs import jobs_bp

    app.register_blueprint(jobs_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def resume_html_client() -> Iterator[FlaskClient]:
    app = Flask(__name__)
    from ui.api.api_resume_html import resume_html_bp

    app.register_blueprint(resume_html_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def intake_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[FlaskClient]:
    monkeypatch.setattr("ui.auth._ALLOWED_IPS", set())
    app = Flask(__name__)
    from ui.api.api_intake import intake_bp

    app.register_blueprint(intake_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_client() -> Iterator[FlaskClient]:
    app = Flask(__name__)
    from ui.api.api_admin import admin_bp

    app.register_blueprint(admin_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def server_client(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Iterator[FlaskClient]:
    # AST-654: server import calls bootstrap_runtime(); stub before reload.
    monkeypatch.setattr("src.core.bootstrap.bootstrap_runtime", lambda: None)
    monkeypatch.setattr("src.core.dispatcher.start_scheduler", lambda: None)
    monkeypatch.setattr("src.data.database.sync_agent_tasks", lambda *args, **kwargs: None)
    import ui.auth as auth_mod

    auth_mod._ALLOWED_IPS = set()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    import importlib
    import ui.server as server_mod

    importlib.reload(server_mod)
    monkeypatch.setattr(server_mod, "_DIST", dist)
    server_mod.app.config["TESTING"] = True
    with server_mod.app.test_client() as client:
        yield client
