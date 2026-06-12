"""Component tests for src/ui/api/api_resume_html.py (AST-298)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_resume_html as resume_mod


class TestResumeHtmlRoutes:
    def test_base_requires_auth(self, resume_html_client: FlaskClient) -> None:
        assert resume_html_client.get("/candidate/resume/base").status_code == 401

    def test_base_requires_candidate_id(self, resume_html_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = resume_html_client.get("/candidate/resume/base", headers=auth_headers)
        assert resp.status_code == 400
        assert resp.get_json()["error"]

    def test_base_returns_html(self, resume_html_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(resume_mod, "build_base_resume", lambda cid: f"<html>{cid}</html>")
        resp = resume_html_client.get("/candidate/resume/base?candidate_id=somerset", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.mimetype == "text/html"
        assert b"somerset" in resp.data

    def test_base_value_error_is_404(self, resume_html_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(resume_mod, "build_base_resume", MagicMock(side_effect=ValueError("missing")))
        resp = resume_html_client.get("/candidate/resume/base?candidate_id=x", headers=auth_headers)
        assert resp.status_code == 404

    def test_job_resume_returns_html(self, resume_html_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(resume_mod, "build_resume", lambda job_id: f"<html>{job_id}</html>")
        resp = resume_html_client.get("/candidate/resume/job-1", headers=auth_headers)
        assert resp.status_code == 200
        assert b"job-1" in resp.data

    def test_job_resume_value_error_is_404(self, resume_html_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(resume_mod, "build_resume", MagicMock(side_effect=ValueError("no job")))
        resp = resume_html_client.get("/candidate/resume/missing", headers=auth_headers)
        assert resp.status_code == 404


class TestAst581CoverRoute:
    """AST-581 — GET /candidate/cover/<job_id> cover-letter HTML."""

    def test_job_cover_returns_html(self, resume_html_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(resume_mod, "build_cover_letter", lambda job_id: f"<html>cover-{job_id}</html>")
        resp = resume_html_client.get("/candidate/cover/job-581", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.mimetype == "text/html"
        assert b"cover-job-581" in resp.data

    def test_job_cover_value_error_is_404(self, resume_html_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(resume_mod, "build_cover_letter", MagicMock(side_effect=ValueError("no cover")))
        resp = resume_html_client.get("/candidate/cover/missing", headers=auth_headers)
        assert resp.status_code == 404
