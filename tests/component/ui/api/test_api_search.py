"""Component tests for src/ui/api/api_search.py (AST-2173)."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from ui.api import api_search as search_api


@pytest.fixture
def search_client() -> Iterator[FlaskClient]:
    app = Flask(__name__)
    app.register_blueprint(search_api.search_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Branches: blank q → 400; missing / blank candidate_id → 400; no auth → 401 (AC2).
class TestAst2173SearchParams:
    @pytest.mark.parametrize(
        ("query", "error"),
        [
            ("q=%20&candidate_id=cand-a", "q required"),
            ("candidate_id=cand-a", "q required"),
            ("q=x", "candidate_id required"),
            ("q=x&candidate_id=%20%20", "candidate_id required"),
        ],
    )
    def test_bad_params_400_with_error(
        self, search_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, query, error
    ) -> None:
        core = MagicMock()
        monkeypatch.setattr(search_api, "search_entities", core)
        resp = search_client.get(f"/api/search?{query}", headers=auth_headers)
        assert resp.status_code == 400
        assert resp.get_json() == {"error": error}
        core.assert_not_called()

    def test_requires_auth(self, search_client: FlaskClient) -> None:
        assert search_client.get("/api/search?q=x&candidate_id=cand-a").status_code == 401


# Branches: 200 returns core result; q passed as sent, candidate_id stripped.
class TestAst2173SearchOk:
    def test_passes_q_verbatim_and_returns_core_result(
        self, search_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        result = {"job": [{"entity_id": "j1"}], "company": [], "meteorite": []}
        core = MagicMock(return_value=result)
        monkeypatch.setattr(search_api, "search_entities", core)
        resp = search_client.get("/api/search?q=%20Data%20Eng%20&candidate_id=%20cand-a%20", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == result
        core.assert_called_once_with("cand-a", " Data Eng ")


# Branches: core raises → one logger.exception at the route + server_error_from_exception 500.
class TestAst2173SearchError:
    def test_exception_logged_once_and_500(
        self, search_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(search_api, "search_entities", MagicMock(side_effect=RuntimeError("db gone")))
        log = MagicMock()
        monkeypatch.setattr(search_api, "logger", log)
        resp = search_client.get("/api/search?q=x&candidate_id=cand-a", headers=auth_headers)
        assert resp.status_code == 500
        body = resp.get_json()
        assert body["error"] == "db gone" and body["exception_type"] == "RuntimeError"
        log.exception.assert_called_once()
        assert log.info.call_count == 0


# Branches: route → core → real SQLite; keys exactly job/company/meteorite; other candidate's rows absent (AC1, AC9).
class TestAst2173SearchRealDb:
    def test_candidate_scope_and_exact_keys(
        self, search_client: FlaskClient, auth_headers: dict[str, str], sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        for cid in ("cand-a", "cand-b"):
            db.save_company(f"zebra-{cid}", state="IMPORTED", candidate_id=cid, company_name="Zebra Co")
            db.save_job(f"job-{cid}", company_id=f"zebra-{cid}", candidate_id=cid, state="NEW",
                        company_job_id=f"cj-{cid}", job_title="Zebra Wrangler")
            db.insert_meteorite_rows([{"candidate_id": cid, "source_kind": "email", "source_id": "m", "job_title": "Zebra"}])
        resp = search_client.get("/api/search?q=zebra&candidate_id=cand-a", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert set(body) == {"job", "company", "meteorite"}
        assert [j["entity_id"] for j in body["job"]] == ["job-cand-a"]
        assert [c["entity_id"] for c in body["company"]] == ["zebra-cand-a"]
        assert len(body["meteorite"]) == 1

    def test_no_match_three_empty_lists(
        self, search_client: FlaskClient, auth_headers: dict[str, str], sqlite_in_memory
    ) -> None:
        resp = search_client.get("/api/search?q=nothing&candidate_id=cand-a", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"job": [], "company": [], "meteorite": []}
