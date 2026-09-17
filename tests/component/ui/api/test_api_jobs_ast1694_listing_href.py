"""AST-1694: listing_href on GET /api/jobs/<id> (job.job_link else meteorite http link)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_jobs as jobs_mod


def _patch_detail_base(monkeypatch: pytest.MonkeyPatch, job: dict) -> None:
    monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: dict(job, astral_job_id=job_id))
    monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda _job: [])
    monkeypatch.setattr(
        jobs_mod,
        "hydrate_job_artifacts_for_display",
        lambda art, debug=False, astral_job_id=None: art or {},
    )
    if hasattr(jobs_mod, "get_meteorite_by_astral_job_id"):
        monkeypatch.setattr(jobs_mod, "get_meteorite_by_astral_job_id", lambda _jid: None)


class TestAst1694ListingHref:
    """AST-1694: GET /api/jobs/<id> always sets listing_href (http(s) or null)."""

    def test_prefers_http_job_link_skips_meteorite(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_detail_base(
            monkeypatch,
            {"job_link": " https://jobs.example/from-job ", "job_data": {}},
        )
        link_mock = MagicMock(return_value="https://jobs.example/from-meta")
        monkeypatch.setattr(jobs_mod, "get_meteorite_link_by_astral_job_id", link_mock)
        resp = jobs_client.get("/api/jobs/job-1694-a", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["listing_href"] == "https://jobs.example/from-job"
        link_mock.assert_not_called()

    def test_meteorite_http_fallback_when_job_link_empty(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_detail_base(monkeypatch, {"job_link": "", "job_data": {}})
        monkeypatch.setattr(
            jobs_mod,
            "get_meteorite_link_by_astral_job_id",
            lambda jid: "https://jobs.example/from-meta" if jid == "job-1694-b" else None,
        )
        resp = jobs_client.get("/api/jobs/job-1694-b", headers=auth_headers)
        assert resp.get_json()["listing_href"] == "https://jobs.example/from-meta"

    def test_non_http_job_link_falls_back_to_meteorite(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_detail_base(
            monkeypatch, {"job_link": "gmail-breadcrumb:abc", "job_data": {}}
        )
        monkeypatch.setattr(
            jobs_mod,
            "get_meteorite_link_by_astral_job_id",
            lambda _jid: "https://jobs.example/meta-http",
        )
        body = jobs_client.get("/api/jobs/job-1694-c", headers=auth_headers).get_json()
        assert body["listing_href"] == "https://jobs.example/meta-http"

    def test_non_http_meteorite_link_yields_null(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_detail_base(monkeypatch, {"job_link": None, "job_data": {}})
        monkeypatch.setattr(
            jobs_mod,
            "get_meteorite_link_by_astral_job_id",
            lambda _jid: "dice-breadcrumb:xyz",
        )
        assert jobs_client.get("/api/jobs/job-1694-d", headers=auth_headers).get_json()[
            "listing_href"
        ] is None

    def test_lookup_exception_soft_fails_to_null(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_detail_base(
            monkeypatch,
            {"job_link": "", "candidate_id": "cand-1694", "job_data": {}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "get_meteorite_link_by_astral_job_id",
            MagicMock(side_effect=RuntimeError("db down")),
        )
        resp = jobs_client.get("/api/jobs/job-1694-e", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["listing_href"] is None

    def test_http_listing_url_helper(self) -> None:
        assert jobs_mod._http_listing_url("https://x.test/a") == "https://x.test/a"
        assert jobs_mod._http_listing_url(" http://x.test/b ") == "http://x.test/b"
        assert jobs_mod._http_listing_url("/relative") is None
        assert jobs_mod._http_listing_url(None) is None
        assert jobs_mod._http_listing_url("") is None


class TestAst1694DetailListingHrefKey:
    """Broken/obsolete detail revisions — listing_href always present; hydrate kwargs."""

    def test_detail_returns_agent_story_includes_listing_href(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id})
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [{"task_key": "x"}])
        monkeypatch.setattr(jobs_mod, "get_meteorite_link_by_astral_job_id", lambda _jid: None)
        if hasattr(jobs_mod, "get_meteorite_by_astral_job_id"):
            monkeypatch.setattr(jobs_mod, "get_meteorite_by_astral_job_id", lambda _jid: None)
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False, astral_job_id=None: art or {},
        )
        body = jobs_client.get("/api/jobs/job-1", headers=auth_headers).get_json()
        assert body["agent_story"][0]["task_key"] == "x"
        assert body["listing_href"] is None

    def test_detail_soft_fails_agent_story_includes_listing_href(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "job_title": "Analyst",
                "company": "Globex",
                "job_data": {},
            },
        )
        monkeypatch.setattr(
            jobs_mod,
            "get_entity_agent_story",
            MagicMock(side_effect=ValueError("ref target missing")),
        )
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False, astral_job_id=None: art or {},
        )
        monkeypatch.setattr(jobs_mod, "get_meteorite_link_by_astral_job_id", lambda _jid: None)
        if hasattr(jobs_mod, "get_meteorite_by_astral_job_id"):
            monkeypatch.setattr(jobs_mod, "get_meteorite_by_astral_job_id", lambda _jid: None)
        resp = jobs_client.get("/api/jobs/job-1274", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["agent_story"] == []
        assert body["listing_href"] is None
