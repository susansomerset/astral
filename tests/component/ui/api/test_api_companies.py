"""Component tests for src/ui/api/api_companies.py (AST-394)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_companies as companies_mod


class TestFlattenForView:
    def test_lifts_prefilter_notes(self) -> None:
        row = companies_mod._flatten_for_view({"company_data": {"prefilter_company_notes": "ok"}})
        assert row["prefilter_company_notes"] == "ok"


class TestCompaniesRoutes:
    def test_list_watch_view(self, companies_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = companies_client.get("/api/companies?view=watch_list", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()[0]["short_name"] == "acme"

    def test_list_new_inactive_ignored_and_default_views(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(companies_mod, "get_active_trigger_states", lambda candidate_id, entity_type: ["TO_WATCH", "WATCH", "IGNORE"])
        monkeypatch.setattr(companies_mod, "list_companies", lambda **kwargs: [{"short_name": "co", "company_data": {}}])
        for view in ("new_list", "inactive_list", "ignored", "other"):
            resp = companies_client.get(f"/api/companies?view={view}&candidate_id=cand-1", headers=auth_headers)
            assert resp.status_code == 200
            assert resp.get_json()[0]["short_name"] == "co"

    def test_list_new_view_without_pipeline_states(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(companies_mod, "get_active_trigger_states", lambda candidate_id, entity_type: ["WATCH", "IGNORE"])
        monkeypatch.setattr(companies_mod, "list_companies", lambda **kwargs: [])
        resp = companies_client.get("/api/companies?view=new_list&candidate_id=cand-1", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_scan_history_and_counts(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(companies_mod, "list_company_job_scans", lambda **kwargs: [{"scan": 1}])
        monkeypatch.setattr(companies_mod, "get_active_trigger_states", lambda candidate_id, entity_type: ["TO_WATCH"])
        monkeypatch.setattr(companies_mod, "count_companies", lambda **kwargs: 2)
        history = companies_client.get("/api/companies/scan_history?candidate_id=cand-1", headers=auth_headers)
        counts = companies_client.get("/api/companies/counts?candidate_id=cand-1", headers=auth_headers)
        assert history.status_code == 200
        assert counts.status_code == 200
        assert counts.get_json()["/companies/watch_list"] == 2

    def test_detail_not_found(self, companies_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = companies_client.get("/api/companies/missing", headers=auth_headers)
        assert resp.status_code == 404

    def test_detail_returns_story_and_counts(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(companies_mod, "get_company", lambda short_name: {"short_name": short_name, "company_data": {}})
        monkeypatch.setattr(companies_mod, "get_company_job_state_counts", lambda short_name: {"WATCH": 1})
        monkeypatch.setattr(companies_mod, "get_entity_agent_story", lambda company: [{"task_key": "x"}])
        resp = companies_client.get("/api/companies/acme", headers=auth_headers)
        payload = resp.get_json()
        assert resp.status_code == 200
        assert payload["job_state_counts"]["WATCH"] == 1
        assert payload["agent_story"][0]["task_key"] == "x"

    def test_edit_blocks_watch_and_requires_fields(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(companies_mod, "get_company", lambda short_name: {"state": "WATCH"})
        blocked = companies_client.put("/api/companies/acme", json={"company_name": "Acme"}, headers=auth_headers)
        assert blocked.status_code == 400
        monkeypatch.setattr(companies_mod, "get_company", lambda short_name: {"state": "TO_WATCH"})
        missing = companies_client.put("/api/companies/acme", json={"not_allowed": "x"}, headers=auth_headers)
        assert missing.status_code == 400

    def test_edit_updates_allowed_fields(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(companies_mod, "get_company", lambda short_name: {"state": "TO_WATCH"})
        update = MagicMock()
        monkeypatch.setattr(companies_mod, "update_company", update)
        resp = companies_client.put("/api/companies/acme", json={"company_name": "Acme"}, headers=auth_headers)
        assert resp.status_code == 200
        update.assert_called_once_with("acme", company_name="Acme")

    def test_edit_not_found(self, companies_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = companies_client.put("/api/companies/missing", json={"company_name": "Acme"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_bulk_state_requires_body(self, companies_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = companies_client.post("/api/companies/bulk_state", json={}, headers=auth_headers)
        assert resp.status_code == 400

    def test_bulk_state_updates_companies(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(companies_mod, "update_company", lambda short_name, **kwargs: 1)
        resp = companies_client.post("/api/companies/bulk_state", json={"short_names": ["acme"], "to_state": "IGNORE"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["updated"] == 1

    def test_import_requires_rows(self, companies_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = companies_client.post("/api/companies/import", json={}, headers=auth_headers)
        assert resp.status_code == 400

    def test_import_creates_companies(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        update = MagicMock()
        monkeypatch.setattr(companies_mod, "save_company", save)
        monkeypatch.setattr(companies_mod, "update_company", update)
        resp = companies_client.post(
            "/api/companies/import",
            json={"candidate_id": "cand-1", "rows": [{"short_name": "acme", "company_name": "Acme", "company_website": "https://acme.com"}, {"short_name": ""}]},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.get_json()["created"] == 1
        save.assert_called_once()
        update.assert_called_once_with("acme", candidate_id="cand-1")

    def test_import_without_candidate_id(self, companies_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        update = MagicMock()
        monkeypatch.setattr(companies_mod, "save_company", save)
        monkeypatch.setattr(companies_mod, "update_company", update)
        resp = companies_client.post("/api/companies/import", json={"rows": [{"short_name": "acme"}]}, headers=auth_headers)
        assert resp.status_code == 201
        save.assert_called_once()
        update.assert_not_called()
