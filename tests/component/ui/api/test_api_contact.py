"""Component tests for src/ui/api/api_contact.py (AST-1071 / AST-1067)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_contact as contact_api


# Branches: list 200; run 200; ValueError 400; upstream 502; auth 401/403.
class TestAst1071ContactSkillsApi:
    def test_list_skills_ok(
        self, contact_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_api,
            "contact_skills",
            MagicMock(
                return_value={
                    "save_candidate_profile": {
                        "entity": "candidate",
                        "write": True,
                        "description": "profile",
                        "allowed_paths": ("profile.first",),
                    }
                }
            ),
        )
        resp = contact_client.get("/api/admin/contact/skills", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert "skills" in body
        assert body["skills"]["save_candidate_profile"]["allowed_paths"] == ["profile.first"]

    def test_run_skill_ok(
        self, contact_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        run = MagicMock(
            return_value={
                "ok": True,
                "skill_key": "save_candidate_profile",
                "astral_candidate_id": "c1",
                "paths_written": ["profile.first"],
            }
        )
        monkeypatch.setattr(contact_api, "run_contact_skill", run)
        monkeypatch.setattr(contact_api, "ui_llm_debug", MagicMock(return_value=False))
        resp = contact_client.post(
            "/api/admin/contact/skills/save_candidate_profile",
            headers=auth_headers,
            json={"astral_candidate_id": "c1", "fields": {"profile.first": "Ada"}},
        )
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True
        run.assert_called_once_with(
            "save_candidate_profile",
            astral_candidate_id="c1",
            fields={"profile.first": "Ada"},
            debug=False,
        )

    def test_run_value_error_400(
        self, contact_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_api,
            "run_contact_skill",
            MagicMock(side_effect=ValueError("path not allowlisted")),
        )
        monkeypatch.setattr(contact_api, "ui_llm_debug", MagicMock(return_value=False))
        resp = contact_client.post(
            "/api/admin/contact/skills/save_candidate_profile",
            headers=auth_headers,
            json={"astral_candidate_id": "c1", "fields": {"profile.middle": "X"}},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "path not allowlisted"}

    def test_run_fields_not_dict_400(
        self, contact_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = contact_client.post(
            "/api/admin/contact/skills/save_candidate_profile",
            headers=auth_headers,
            json={"astral_candidate_id": "c1", "fields": ["nope"]},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "fields must be a dict"}

    def test_run_upstream_502(
        self, contact_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_api,
            "run_contact_skill",
            MagicMock(side_effect=RuntimeError("db down")),
        )
        monkeypatch.setattr(contact_api, "ui_llm_debug", MagicMock(return_value=False))
        warn = MagicMock()
        monkeypatch.setattr(contact_api.logger, "warning", warn)
        resp = contact_client.post(
            "/api/admin/contact/skills/save_candidate_profile",
            headers=auth_headers,
            json={"astral_candidate_id": "c1", "fields": {"profile.first": "Ada"}},
        )
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "db down"}
        warn.assert_called_once()

    def test_list_requires_auth(self, contact_client: FlaskClient) -> None:
        assert contact_client.get("/api/admin/contact/skills").status_code == 401

    def test_list_non_admin_forbidden(
        self, contact_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        assert (
            contact_client.get("/api/admin/contact/skills", headers=non_admin_headers).status_code
            == 403
        )

    def test_run_requires_auth(self, contact_client: FlaskClient) -> None:
        assert (
            contact_client.post(
                "/api/admin/contact/skills/save_candidate_profile",
                json={"astral_candidate_id": "c1", "fields": {}},
            ).status_code
            == 401
        )


# Branches: GET/PUT listen payload; 400; auth 401/403 (AST-1067).
class TestAst1067ContactListenApi:
    def test_get_listen_ok(
        self, contact_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_api, "slack_listen_enabled", MagicMock(return_value=False))
        monkeypatch.setattr(contact_api, "get_deploy_label", MagicMock(return_value="staging"))
        monkeypatch.setattr(contact_api, "contact_is_production_deploy", MagicMock(return_value=False))
        resp = contact_client.get("/api/admin/contact/listen", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {
            "listen_enabled": False,
            "environment": "staging",
            "is_production": False,
        }

    def test_put_listen_ok(
        self, contact_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        set_fn = MagicMock(return_value=True)
        monkeypatch.setattr(contact_api, "set_slack_listen_enabled", set_fn)
        monkeypatch.setattr(contact_api, "ui_llm_debug", MagicMock(return_value=False))
        monkeypatch.setattr(contact_api, "slack_listen_enabled", MagicMock(return_value=True))
        monkeypatch.setattr(contact_api, "get_deploy_label", MagicMock(return_value="staging"))
        monkeypatch.setattr(contact_api, "contact_is_production_deploy", MagicMock(return_value=False))
        resp = contact_client.put(
            "/api/admin/contact/listen",
            headers=auth_headers,
            json={"listen_enabled": True},
        )
        assert resp.status_code == 200
        assert resp.get_json()["listen_enabled"] is True
        set_fn.assert_called_once_with(True, debug=False)

    def test_put_listen_non_bool_400(
        self, contact_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = contact_client.put(
            "/api/admin/contact/listen",
            headers=auth_headers,
            json={"listen_enabled": "yes"},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "listen_enabled must be a bool"}

    def test_put_upstream_502(
        self, contact_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_api,
            "set_slack_listen_enabled",
            MagicMock(side_effect=RuntimeError("disk full")),
        )
        monkeypatch.setattr(contact_api, "ui_llm_debug", MagicMock(return_value=False))
        warn = MagicMock()
        monkeypatch.setattr(contact_api.logger, "warning", warn)
        resp = contact_client.put(
            "/api/admin/contact/listen",
            headers=auth_headers,
            json={"listen_enabled": True},
        )
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "disk full"}
        warn.assert_called_once()

    def test_listen_requires_auth(self, contact_client: FlaskClient) -> None:
        assert contact_client.get("/api/admin/contact/listen").status_code == 401

    def test_listen_non_admin_forbidden(
        self, contact_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        assert (
            contact_client.get("/api/admin/contact/listen", headers=non_admin_headers).status_code
            == 403
        )

