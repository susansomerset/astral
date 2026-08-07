"""Component tests for src/ui/api/api_surfer.py (AST-1236 pacing; AST-1235 consent)."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from src.utils.config import SURFER_PACING_CONFIG


# Branches: 200 payload mirrors config; 401 unauth; non-admin allowed; response not live config.
class TestAst1236SurferPacingConfigApi:
    def test_get_pacing_config_ok(
        self, surfer_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = surfer_client.get("/api/surfer/pacing_config", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body == {
            "dwell_center_seconds": SURFER_PACING_CONFIG["dwell_center_seconds"],
            "dwell_spread_seconds": SURFER_PACING_CONFIG["dwell_spread_seconds"],
            "max_tabs": SURFER_PACING_CONFIG["max_tabs"],
            "mv3_idle_ceiling_seconds": SURFER_PACING_CONFIG["mv3_idle_ceiling_seconds"],
        }
        # jsonify copy — mutating the response must not touch the config module.
        body["max_tabs"] = 99
        assert SURFER_PACING_CONFIG["max_tabs"] == 1

    def test_requires_auth(self, surfer_client: FlaskClient) -> None:
        assert surfer_client.get("/api/surfer/pacing_config").status_code == 401

    def test_non_admin_allowed(
        self, surfer_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = surfer_client.get("/api/surfer/pacing_config", headers=non_admin_headers)
        assert resp.status_code == 200
        assert resp.get_json()["max_tabs"] == SURFER_PACING_CONFIG["max_tabs"]


# Branches: GET DTO; PUT opt_in/opt_out; 400/404; @require_auth (AST-1235).
class TestAst1235SurferConsentApi:
    def test_get_consent_default_dto(
        self,
        surfer_consent_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        monkeypatch.setattr(
            "src.ui.api.api_surfer.get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        monkeypatch.setattr(
            "src.ui.api.api_surfer.surfer_consent_dto",
            lambda cid: {
                "status": "none",
                "accepted_version": None,
                "updated_at": None,
                "current_version": SURFER_CONSENT_CONFIG["current_version"],
                "disclosure_copy": SURFER_CONSENT_CONFIG["disclosure_copy"],
                "is_current": False,
            },
        )
        resp = surfer_consent_client.get(
            "/api/candidates/c1/surfer/consent", headers=auth_headers
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "none"
        assert body["is_current"] is False
        assert body["current_version"] == SURFER_CONSENT_CONFIG["current_version"]
        assert body["disclosure_copy"] == SURFER_CONSENT_CONFIG["disclosure_copy"]

    def test_get_consent_404(
        self,
        surfer_consent_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("src.ui.api.api_surfer.get_candidate", lambda cid: None)
        resp = surfer_consent_client.get(
            "/api/candidates/missing/surfer/consent", headers=auth_headers
        )
        assert resp.status_code == 404
        assert "not found" in resp.get_json()["error"].lower()

    def test_put_opt_in_ok(
        self,
        surfer_consent_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        monkeypatch.setattr(
            "src.ui.api.api_surfer.get_candidate",
            lambda cid: {"astral_candidate_id": cid},
        )
        captured: dict = {}

        def _opt_in(cid, ver, *, debug=False):
            captured["cid"] = cid
            captured["ver"] = ver
            captured["debug"] = debug
            return {
                "status": "opted_in",
                "accepted_version": ver,
                "updated_at": "2026-08-07 00:00:00",
                "current_version": SURFER_CONSENT_CONFIG["current_version"],
                "disclosure_copy": SURFER_CONSENT_CONFIG["disclosure_copy"],
                "is_current": True,
            }

        monkeypatch.setattr("src.ui.api.api_surfer.opt_in_surfer_consent", _opt_in)
        resp = surfer_consent_client.put(
            "/api/candidates/c1/surfer/consent",
            headers=auth_headers,
            json={
                "action": "opt_in",
                "accepted_version": SURFER_CONSENT_CONFIG["current_version"],
            },
        )
        assert resp.status_code == 200
        assert resp.get_json()["is_current"] is True
        assert captured["cid"] == "c1"
        assert captured["ver"] == SURFER_CONSENT_CONFIG["current_version"]

    def test_put_opt_in_version_mismatch_400(
        self,
        surfer_consent_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "src.ui.api.api_surfer.get_candidate",
            lambda cid: {"astral_candidate_id": cid},
        )

        def _opt_in(cid, ver, *, debug=False):
            raise ValueError("accepted_version does not match current disclosure version")

        monkeypatch.setattr("src.ui.api.api_surfer.opt_in_surfer_consent", _opt_in)
        resp = surfer_consent_client.put(
            "/api/candidates/c1/surfer/consent",
            headers=auth_headers,
            json={"action": "opt_in", "accepted_version": "stale"},
        )
        assert resp.status_code == 400
        assert "version" in resp.get_json()["error"].lower()

    def test_put_opt_out_ok(
        self,
        surfer_consent_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        monkeypatch.setattr(
            "src.ui.api.api_surfer.get_candidate",
            lambda cid: {"astral_candidate_id": cid},
        )
        monkeypatch.setattr(
            "src.ui.api.api_surfer.opt_out_surfer_consent",
            lambda cid, *, debug=False: {
                "status": "opted_out",
                "accepted_version": SURFER_CONSENT_CONFIG["current_version"],
                "updated_at": "2026-08-07 00:00:01",
                "current_version": SURFER_CONSENT_CONFIG["current_version"],
                "disclosure_copy": SURFER_CONSENT_CONFIG["disclosure_copy"],
                "is_current": False,
            },
        )
        resp = surfer_consent_client.put(
            "/api/candidates/c1/surfer/consent",
            headers=auth_headers,
            json={"action": "opt_out"},
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "opted_out"
        assert body["is_current"] is False
        assert body["accepted_version"] == SURFER_CONSENT_CONFIG["current_version"]

    def test_put_bad_action_400(
        self,
        surfer_consent_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "src.ui.api.api_surfer.get_candidate",
            lambda cid: {"astral_candidate_id": cid},
        )
        resp = surfer_consent_client.put(
            "/api/candidates/c1/surfer/consent",
            headers=auth_headers,
            json={"action": "shrug"},
        )
        assert resp.status_code == 400
        assert "opt_in" in resp.get_json()["error"]

    def test_requires_auth(self, surfer_consent_client: FlaskClient) -> None:
        assert (
            surfer_consent_client.get("/api/candidates/c1/surfer/consent").status_code
            == 401
        )
        assert (
            surfer_consent_client.put(
                "/api/candidates/c1/surfer/consent", json={"action": "opt_out"}
            ).status_code
            == 401
        )
