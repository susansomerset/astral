"""Component tests for src/ui/api/api_surfer.py (AST-1236)."""

from __future__ import annotations

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
