"""Component tests for src/ui/api/api_system.py (AST-394)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.utils import deploy_status as ds_mod
from ui.api import api_system as system_mod


class TestSystemHealth:
    def test_health_is_open(self, system_client: FlaskClient) -> None:
        resp = system_client.get("/api/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}


class TestSystemAuthRoutes:
    def test_me_requires_bearer(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        assert system_client.get("/api/me").status_code == 401
        resp = system_client.get("/api/me", headers=auth_headers)
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["user_id"] == "susan"
        assert payload["is_admin"] is True

    def test_me_non_admin_includes_is_admin_false(
        self, system_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = system_client.get("/api/me", headers=non_admin_headers)
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["user_id"] == "u2"
        assert payload["is_admin"] is False

    def test_shapes_unknown_entity_404(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = system_client.get("/api/shapes/missing", headers=auth_headers)
        assert resp.status_code == 404

    def test_shapes_known_entity(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = system_client.get("/api/shapes/candidates", headers=auth_headers)
        assert resp.status_code == 200
        assert "list" in resp.get_json()

    def test_ui_config_and_state_manifest(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        ui = system_client.get("/api/ui_config", headers=auth_headers)
        manifest = system_client.get("/api/state_ui_manifest", headers=auth_headers)
        assert ui.status_code == 200
        assert manifest.status_code == 200

    def test_ui_config_includes_base_resume_accent_palette(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/ui_config", headers=auth_headers).get_json()
        palette = payload.get("base_resume_accent_palette")
        assert isinstance(palette, list)
        assert palette
        assert all(isinstance(hex, str) and hex.startswith("#") for hex in palette)

    def test_ui_config_includes_list_table_layout_defaults(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/ui_config", headers=auth_headers).get_json()
        assert payload.get("list_table_frozen_data_columns") == 2
        assert payload.get("list_table_cell_truncate_chars") == 30

    def test_nav_config_without_candidate_id(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = system_client.get("/api/nav_config", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_nav_config_missing_candidate(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("ui.api.api_system.get_candidate", lambda candidate_id: None)
        resp = system_client.get("/api/nav_config?candidate_id=missing", headers=auth_headers)
        assert resp.status_code == 200

    def test_nav_config_uses_candidate_state(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("ui.api.api_system.get_candidate", lambda candidate_id: {"state": "LIVE_PROMPTS"})
        monkeypatch.setattr(system_mod, "_get_company_counts", lambda candidate_id: {"/companies/watch_list": 4})
        monkeypatch.setattr(system_mod, "_get_job_counts", lambda candidate_id: {"/jobs/in_review": 1})
        resp = system_client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers)
        payload = resp.get_json()
        assert resp.status_code == 200
        jobs = next(group for group in payload if group["label"] == "Jobs")
        assert jobs["items"][0]["count"] == 1

    def test_nav_config_admin_agent_ad_hoc_label(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/nav_config", headers=auth_headers).get_json()
        admin = next(group for group in payload if group["label"] == "Admin")
        ad_hoc = next(item for item in admin["items"] if item["path"] == "/admin/anthropic_ad_hoc")
        assert ad_hoc["label"] == "Agent Ad Hoc"

    def test_nav_config_omits_admin_group_for_non_admin(
        self, system_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        payload = system_client.get("/api/nav_config", headers=non_admin_headers).get_json()
        assert all(group.get("label") != "Admin" for group in payload)

    def test_nav_config_omits_board_searches(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/nav_config", headers=auth_headers).get_json()
        paths = [item.get("path") for group in payload for item in group.get("items", [])]
        assert "/candidate/board_searches" not in paths

    def test_agent_data_returns_rows(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.agent.get_agent_data", MagicMock(return_value=[{"id": "block-1"}]))
        resp = system_client.get("/api/agent_data/batch-1?block_type=RESPONSE&entity_id=acme", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()[0]["id"] == "block-1"

    def test_agent_data_missing_entity_404(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.agent.get_entity_response", MagicMock(return_value=None))
        resp = system_client.get("/api/agent_data/batch-1/entity/acme", headers=auth_headers)
        assert resp.status_code == 404

    def test_agent_data_entity_response(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.agent.get_entity_response", MagicMock(return_value={"block_data": "{}"}))
        resp = system_client.get("/api/agent_data/batch-1/entity/acme", headers=auth_headers)
        assert resp.status_code == 200


class TestDeployStatus:
    def test_requires_bearer(self, system_client: FlaskClient) -> None:
        assert system_client.get("/api/deploy_status").status_code == 401

    def test_non_admin_forbidden(
        self, system_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = system_client.get("/api/deploy_status", headers=non_admin_headers)
        assert resp.status_code == 403

    def test_admin_returns_payload(
        self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        expected = {
            "uptime": "5m",
            "uptime_seconds": 300,
            "environment": "local",
            "merge_tickets": [],
        }
        monkeypatch.setattr(system_mod, "get_deploy_status_payload", lambda: expected)
        resp = system_client.get("/api/deploy_status", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == expected

    def test_admin_omits_environment_when_unset(
        self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        payload = {
            "uptime": "<1m",
            "uptime_seconds": 10,
            "merge_tickets": [],
        }
        monkeypatch.setattr(system_mod, "get_deploy_status_payload", lambda: payload)
        resp = system_client.get("/api/deploy_status", headers=auth_headers)
        assert resp.status_code == 200
        assert "environment" not in resp.get_json()

    def test_admin_uptime_format_samples_via_payload_builder(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(ds_mod, "_PROCESS_BOOT_TIME", 0.0)
        cases = [
            (30, "<1m"),
            (5 * 60, "5m"),
            (75 * 60, "1h15m"),
            (3 * 86400 + 22 * 3600 + 7 * 60, "3d22h07m"),
        ]
        for seconds, expected_uptime in cases:
            monkeypatch.setattr("time.time", lambda s=seconds: float(s))
            payload = ds_mod.get_deploy_status_payload()
            assert payload["uptime"] == expected_uptime


class TestSystemNavHelpers:
    def test_is_at_or_past_compares_candidate_states(self) -> None:
        assert system_mod._is_at_or_past("LIVE_PROMPTS", "CONTEXT_READY") is True
        assert system_mod._is_at_or_past("NEW", "LIVE_PROMPTS") is False

    def test_company_counts_without_candidate(self) -> None:
        assert system_mod._get_company_counts(None) == {}

    def test_company_counts_swallow_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.roster.get_active_trigger_states", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
        assert system_mod._get_company_counts("cand-1") == {}

    def test_company_counts_with_pipeline_and_history(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.roster.get_active_trigger_states", lambda *args, **kwargs: ["WATCH", "IGNORE"])
        monkeypatch.setattr("src.core.roster.list_companies", lambda **kwargs: [1, 2] if kwargs.get("states") == ["WATCH"] else [])
        monkeypatch.setattr("src.core.roster.list_company_job_scans", lambda **kwargs: [1])
        counts = system_mod._get_company_counts("cand-1")
        assert counts["/companies/watch_list"] == 2
        assert counts["/companies/new_list"] == 0

    def test_job_counts_without_candidate(self) -> None:
        assert system_mod._get_job_counts(None) == {}

    def test_job_counts_swallow_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.tracker.count_jobs_below_dispatch_score_floor", lambda candidate_id: (_ for _ in ()).throw(RuntimeError("boom")))
        assert system_mod._get_job_counts("cand-1") == {}

    def test_resolve_nav_honors_visible_and_enabled_gates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(system_mod, "_get_company_counts", lambda candidate_id: {})
        monkeypatch.setattr(system_mod, "_get_job_counts", lambda candidate_id: {})
        nav = system_mod._resolve_nav("CONTEXT_READY", "cand-1")
        labels = {group["label"] for group in nav}
        assert "Jobs" not in labels
        artifacts = next(group for group in nav if group["label"] == "Artifacts")
        assert all(item["enabled"] for item in artifacts["items"])
        candidate = next(group for group in nav if group["label"] == "Candidate")
        assert candidate["items"][0]["enabled"] is True

    def test_resolve_nav_uses_string_enabled_gate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(system_mod, "NAV_CONFIG", [{"label": "G", "items": [{"label": "X", "path": "/x", "enabled": "LIVE_PROMPTS"}]}])
        monkeypatch.setattr(system_mod, "_get_company_counts", lambda candidate_id: {})
        monkeypatch.setattr(system_mod, "_get_job_counts", lambda candidate_id: {})
        nav = system_mod._resolve_nav("NEW", "cand-1")
        assert nav[0]["items"][0]["enabled"] is False
        nav_live = system_mod._resolve_nav("LIVE_PROMPTS", "cand-1")
        assert nav_live[0]["items"][0]["enabled"] is True
