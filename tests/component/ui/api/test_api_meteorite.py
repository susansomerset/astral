"""Component tests for src/ui/api/api_meteorite.py (AST-1042)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_meteorite as meteorite_api


# Branches: 201; 400 validation; 404 missing candidate; 502 upstream; 401 unauth; non-admin allowed.
class TestAst1042MeteoriteCreateApi:
    def test_create_ok(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            meteorite_api,
            "create_meteorite_job",
            MagicMock(
                return_value={
                    "astral_job_id": "j1",
                    "company": "meteorite-cand-1",
                    "state": "METEORITE_NEW",
                    "latest_score": 10.0,
                    "company_inserted": True,
                    "job": {"astral_job_id": "j1"},
                }
            ),
        )
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=auth_headers,
            json={"html_body": "<p>hi</p>"},
        )
        assert resp.status_code == 201
        assert resp.get_json() == {
            "astral_job_id": "j1",
            "company": "meteorite-cand-1",
            "state": "METEORITE_NEW",
            "latest_score": 10.0,
            "company_inserted": True,
        }
        meteorite_api.create_meteorite_job.assert_called_once_with(
            "cand-1", "<p>hi</p>", debug=False
        )

    def test_create_validation_400(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            meteorite_api,
            "create_meteorite_job",
            MagicMock(side_effect=ValueError("html_body is required")),
        )
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "html_body is required"}

    def test_create_candidate_missing_404(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            meteorite_api,
            "create_meteorite_job",
            MagicMock(side_effect=ValueError("candidate not found: nope")),
        )
        resp = meteorite_client.post(
            "/api/candidates/nope/meteorite/jobs",
            headers=auth_headers,
            json={"html_body": "<p>x</p>"},
        )
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "candidate not found: nope"}

    def test_create_upstream_502(
        self, meteorite_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            meteorite_api,
            "create_meteorite_job",
            MagicMock(side_effect=RuntimeError("db down")),
        )
        warn = MagicMock()
        monkeypatch.setattr(meteorite_api.logger, "warning", warn)
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=auth_headers,
            json={"html_body": "<p>x</p>"},
        )
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "db down"}
        warn.assert_called_once()

    def test_requires_auth(self, meteorite_client: FlaskClient) -> None:
        assert (
            meteorite_client.post(
                "/api/candidates/cand-1/meteorite/jobs",
                json={"html_body": "<p>x</p>"},
            ).status_code
            == 401
        )

    def test_non_admin_allowed(
        self,
        meteorite_client: FlaskClient,
        non_admin_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            meteorite_api,
            "create_meteorite_job",
            MagicMock(
                return_value={
                    "astral_job_id": "j2",
                    "company": "meteorite-cand-1",
                    "state": "METEORITE_NEW",
                    "latest_score": 10.0,
                    "company_inserted": False,
                    "job": {},
                }
            ),
        )
        resp = meteorite_client.post(
            "/api/candidates/cand-1/meteorite/jobs",
            headers=non_admin_headers,
            json={"html_body": "<p>x</p>"},
        )
        assert resp.status_code == 201
