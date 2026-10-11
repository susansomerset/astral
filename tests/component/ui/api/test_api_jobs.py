"""Component tests for src/ui/api/api_jobs.py (AST-394)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.utils import config as cfg
from ui.api import api_jobs as jobs_mod


class TestFlattenGrades:
    def test_lifts_job_data_fields_and_latest_score(self) -> None:
        job = jobs_mod._flatten_grades({"job_data": {"joblist_grades": [1], "joblist_score": 7.5}})
        assert job["joblist_grades"] == [1]
        assert job["latest_score"] == 7.5


class TestAst1347FlattenScoreBreakdown:
    """AST-1347: lift {jd,do,get,like}_score_breakdown; do not invent when absent."""

    def test_lifts_phase_score_breakdowns(self) -> None:
        suffix = cfg.PHASE_SCORE_BREAKDOWN_KEY_SUFFIX
        trio = {"earned": 100.0, "possible": 150.0, "max": 320.0}
        jd = {f"{p}_{suffix}": dict(trio) for p in ("jd", "do", "get", "like")}
        jd["jd_score"] = 7.5
        job = jobs_mod._flatten_grades({"job_data": jd, "astral_job_id": "j1"})
        for p in ("jd", "do", "get", "like"):
            assert job[f"{p}_{suffix}"] == trio
        assert job["jd_score"] == 7.5

    def test_absent_breakdown_not_invented(self) -> None:
        # Grades + score without rubric — AST-1348 derive gate also requires rubric
        suffix = cfg.PHASE_SCORE_BREAKDOWN_KEY_SUFFIX
        job = jobs_mod._flatten_grades(
            {"job_data": {"jd_grades": [{"vector": "fit"}], "jd_score": 8.0}}
        )
        assert job["jd_score"] == 8.0
        for p in ("jd", "do", "get", "like"):
            assert f"{p}_{suffix}" not in job


class TestAst1348FlattenDeriveBreakdown:
    """AST-1348: derive missing breakdown at read; never invent on unscored / incomplete."""

    _RUBRIC = [{"label": "fit", "importance": 5}]
    _GRADES = [{"vector": "fit", "grade": "A", "confidence": 5}]

    def test_derives_when_stored_trio_absent(self) -> None:
        suffix = cfg.PHASE_SCORE_BREAKDOWN_KEY_SUFFIX
        job = jobs_mod._flatten_grades(
            {
                "job_data": {
                    "jd_grades": list(self._GRADES),
                    "jd_score": 10.6,
                    "jd_rubric": list(self._RUBRIC),
                }
            }
        )
        key = f"jd_{suffix}"
        assert key in job
        assert set(job[key]) == set(cfg.PHASE_SCORE_BREAKDOWN_FIELDS)
        assert all(isinstance(job[key][f], float) for f in cfg.PHASE_SCORE_BREAKDOWN_FIELDS)
        # Response-only: job_data blob unchanged
        assert key not in (job.get("job_data") or {})

    def test_keeps_stored_trio_without_recompute(self) -> None:
        suffix = cfg.PHASE_SCORE_BREAKDOWN_KEY_SUFFIX
        stored = {"earned": 1.0, "possible": 2.0, "max": 3.0}
        job = jobs_mod._flatten_grades(
            {
                "job_data": {
                    "jd_grades": list(self._GRADES),
                    "jd_score": 9.0,
                    "jd_rubric": list(self._RUBRIC),
                    f"jd_{suffix}": dict(stored),
                }
            }
        )
        assert job[f"jd_{suffix}"] == stored

    def test_omits_when_score_missing(self) -> None:
        # Dealbreaker / unscored — grades + rubric but no *_score
        suffix = cfg.PHASE_SCORE_BREAKDOWN_KEY_SUFFIX
        job = jobs_mod._flatten_grades(
            {
                "job_data": {
                    "jd_grades": list(self._GRADES),
                    "jd_rubric": list(self._RUBRIC),
                }
            }
        )
        assert f"jd_{suffix}" not in job


class TestJobsRoutes:
    def test_retired_in_review_view_falls_through(self, jobs_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        # AST-1974: in_review / recommended / responded views removed — unknown view → [].
        for view in ("in_review", "recommended", "responded"):
            resp = jobs_client.get(f"/api/jobs?view={view}", headers=auth_headers)
            assert resp.status_code == 200
            assert resp.get_json() == []

    def test_list_processing_filters_score_floor(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"astral_job_id": "job-1", "job_data": {}}, {"astral_job_id": "job-2", "job_data": {}}]
        captured: dict[str, object] = {}

        def _list_jobs(**kwargs: object) -> list[dict[str, object]]:
            captured.update(kwargs)
            return rows

        monkeypatch.setattr(jobs_mod, "list_jobs", _list_jobs)
        monkeypatch.setattr(jobs_mod, "score_floor_by_trigger_for_candidate", lambda candidate_id: {"NEW": 5.0})
        monkeypatch.setattr(jobs_mod, "job_misses_dispatch_score_floor", lambda row, floors: row["astral_job_id"] == "job-2")
        resp = jobs_client.get("/api/jobs?view=processing&candidate_id=cand-1", headers=auth_headers)
        # AST-2133 revision: every list row carries the composed JD (empty when nothing stored).
        assert resp.get_json() == [{"astral_job_id": "job-1", "job_data": {"job_description": ""}}]
        # AC 7: Processing = exclusion of the four explicit lists, never an include-list.
        assert captured.get("exclude_states") == list(cfg.JOBS_PROCESSING_EXCLUDED_STATES)
        assert captured.get("states") is None

    def test_list_processing_without_score_floors(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"astral_job_id": "job-1", "job_data": {}}]
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kwargs: rows)
        monkeypatch.setattr(jobs_mod, "score_floor_by_trigger_for_candidate", lambda candidate_id: {})
        resp = jobs_client.get("/api/jobs?view=processing&candidate_id=cand-1", headers=auth_headers)
        assert resp.get_json() == rows

    def test_list_processing_without_candidate_skips_floor_read(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"astral_job_id": "job-1", "job_data": {}}]
        floors = MagicMock(return_value={"NEW": 5.0})
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kwargs: rows)
        monkeypatch.setattr(jobs_mod, "score_floor_by_trigger_for_candidate", floors)
        resp = jobs_client.get("/api/jobs?view=processing", headers=auth_headers)
        assert resp.get_json() == rows
        floors.assert_not_called()

    def test_list_skipped_view_appends_virtual_rows(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kwargs: [{"astral_job_id": "job-1", "state_changed_at": "2026-01-02", "job_data": {}}])
        monkeypatch.setattr(jobs_mod, "score_floor_by_trigger_for_candidate", lambda candidate_id: {"NEW": 5.0})
        monkeypatch.setattr(
            jobs_mod,
            "list_jobs_below_dispatch_score_floor",
            lambda candidate_id: [{"astral_job_id": "job-2", "state": "NEW", "state_changed_at": "2026-01-03", "job_data": {}}],
        )
        resp = jobs_client.get("/api/jobs?view=skipped&candidate_id=cand-1", headers=auth_headers)
        payload = resp.get_json()
        assert payload[0]["astral_job_id"] == "job-2"
        assert payload[0]["virtual_skip"] is True

    def test_list_skipped_without_candidate_id(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kwargs: [{"astral_job_id": "job-1", "job_data": {}}])
        resp = jobs_client.get("/api/jobs?view=skipped", headers=auth_headers)
        assert resp.get_json()[0]["astral_job_id"] == "job-1"

    def test_list_ready_review_and_default(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1974 AC 2 / AC 3: ready → READY_JOB_STATES, review → REVIEW_JOB_STATES; default view = ready.
        calls: list[dict[str, object]] = []

        def _list_jobs(**kwargs: object) -> list[dict[str, object]]:
            calls.append(dict(kwargs))
            return [{"astral_job_id": "job-1", "job_data": {"joblist_score": 1}}]

        monkeypatch.setattr(jobs_mod, "list_jobs", _list_jobs)
        ready = jobs_client.get("/api/jobs?view=ready&candidate_id=cand-1", headers=auth_headers)
        assert ready.get_json()[0]["latest_score"] == 1
        review = jobs_client.get("/api/jobs?view=review&candidate_id=cand-1", headers=auth_headers)
        assert review.get_json()[0]["latest_score"] == 1
        default = jobs_client.get("/api/jobs?candidate_id=cand-1", headers=auth_headers)
        assert default.status_code == 200
        assert [c["states"] for c in calls] == [
            list(cfg.READY_JOB_STATES), list(cfg.REVIEW_JOB_STATES), list(cfg.READY_JOB_STATES),
        ]
        assert all(c["candidate_id"] == "cand-1" and c["order_by"] == "state_changed_at" for c in calls)
        # Unknown views still fall through to [].
        other = jobs_client.get("/api/jobs?view=not_a_real_view", headers=auth_headers)
        assert other.get_json() == []

    def test_list_applied_uses_applied_job_states(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1479: view=applied lists APPLIED_JOB_STATES (not empty fall-through).
        calls: list[dict[str, object]] = []

        def _list_jobs(**kwargs: object) -> list[dict[str, object]]:
            calls.append(dict(kwargs))
            return [{"astral_job_id": "job-applied", "job_data": {}}]

        monkeypatch.setattr(jobs_mod, "list_jobs", _list_jobs)
        resp = jobs_client.get(
            "/api/jobs?view=applied&candidate_id=cand-1",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()[0]["astral_job_id"] == "job-applied"
        primary = next(c for c in calls if c.get("candidate_id") == "cand-1")
        assert primary.get("order_by") == "state_changed_at"
        assert list(primary.get("states") or []) == list(cfg.APPLIED_JOB_STATES)

    def test_list_applied_single_scoped_read_no_repair_ast1974(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1974 AC 4 (supersedes AST-1498 repair-on-read): job.candidate_id scoping (AST-1598) is the
        # only read — never list_jobs(candidate_id=None) (raises), never company-linkage repair writes.
        calls: list[dict[str, object]] = []

        def _list_jobs(**kwargs: object) -> list[dict[str, object]]:
            calls.append(dict(kwargs))
            return [{"astral_job_id": "job-applied-1", "state": "CANDIDATE_APPLIED", "job_data": {}}]

        update_company = MagicMock(return_value=1)
        monkeypatch.setattr(jobs_mod, "list_jobs", _list_jobs)
        monkeypatch.setattr(jobs_mod, "update_company", update_company)
        resp = jobs_client.get("/api/jobs?view=applied&candidate_id=cand-a", headers=auth_headers)
        assert resp.status_code == 200
        assert [row["astral_job_id"] for row in resp.get_json()] == ["job-applied-1"]
        assert len(calls) == 1 and calls[0]["candidate_id"] == "cand-a"
        update_company.assert_not_called()
        assert not hasattr(jobs_mod, "_list_applied_jobs_for_candidate")

    def test_bulk_state_requires_body(self, jobs_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = jobs_client.post("/api/jobs/bulk_state", json={}, headers=auth_headers)
        assert resp.status_code == 400

    def test_bulk_state_updates_jobs(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1156: bulk_state uses transition_job_state (priors + history), not save_job.
        transition = MagicMock(side_effect=[None, ValueError("missing")])
        monkeypatch.setattr(jobs_mod, "transition_job_state", transition)
        resp = jobs_client.post(
            "/api/jobs/bulk_state",
            json={"astral_job_ids": ["job-1", "job-2"], "to_state": "PASSED_JD"},
            headers=auth_headers,
        )
        assert resp.get_json()["updated"] == 1
        assert transition.call_args_list[0].args == (["job-1"], "PASSED_JD")

    def test_detail_not_found(self, jobs_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = jobs_client.get("/api/jobs/missing", headers=auth_headers)
        assert resp.status_code == 404

    def test_detail_returns_agent_story(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id})
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [{"task_key": "x"}])
        monkeypatch.setattr(jobs_mod, "get_meteorite_by_astral_job_id", lambda _jid: None)
        resp = jobs_client.get("/api/jobs/job-1", headers=auth_headers)
        body = resp.get_json()
        assert body["agent_story"][0]["task_key"] == "x"
        assert body["related_meteorite"] is None

    def test_detail_soft_fails_agent_story(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1274: story hydrate failure must not 500 detail.
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
        monkeypatch.setattr(jobs_mod, "get_meteorite_by_astral_job_id", lambda _jid: None)
        resp = jobs_client.get("/api/jobs/job-1274", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["astral_job_id"] == "job-1274"
        assert body["agent_story"] == []
        assert body["related_meteorite"] is None

    def test_detail_related_meteorite_object(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1691 AC2: projected flat object when reverse link hits.
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {}},
        )
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [])
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False, astral_job_id=None: art or {},
        )
        monkeypatch.setattr(
            jobs_mod,
            "get_meteorite_by_astral_job_id",
            lambda jid: {
                "id": 42,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
                "state_changed_at": "2026-01-03T00:00:00Z",
                "estelle_notified_at": None,
                "link": "https://jobs.example/m",
                "classify_outcome": "posting",
                "content": "jd text",
                "state": "LANDED",
                "source_kind": "email",
                "source_id": "mid-1",
                "error": None,
                "batch_id": "should-not-leak",
            },
        )
        resp = jobs_client.get("/api/jobs/job-1691", headers=auth_headers)
        assert resp.status_code == 200
        rm = resp.get_json()["related_meteorite"]
        assert rm["id"] == 42
        assert rm["link"] == "https://jobs.example/m"
        assert rm["classify_outcome"] == "posting"
        assert rm["content"] == "jd text"
        assert rm["state"] == "LANDED"
        assert rm["source_kind"] == "email"
        assert rm["source_id"] == "mid-1"
        assert "batch_id" not in rm

    def test_detail_related_meteorite_soft_fail(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1691: lookup throw → related_meteorite null (not 500).
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "candidate_id": "c1", "job_data": {}},
        )
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [])
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False, astral_job_id=None: art or {},
        )
        monkeypatch.setattr(
            jobs_mod,
            "get_meteorite_by_astral_job_id",
            MagicMock(side_effect=RuntimeError("db down")),
        )
        resp = jobs_client.get("/api/jobs/job-1691-fail", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["related_meteorite"] is None

    def test_detail_related_meteorite_source_entity_fallback(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1769 [bug-repro]: reverse astral_job_id miss + source=meteorite + digit
        # source_entity_id → related_meteorite via get_meteorite(sid) (pre-fix: stays null).
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "source": "meteorite",
                "source_entity_id": "42",
                "job_data": {},
            },
        )
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [])
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False, astral_job_id=None: art or {},
        )
        monkeypatch.setattr(jobs_mod, "get_meteorite_by_astral_job_id", lambda _jid: None)
        monkeypatch.setattr(
            jobs_mod,
            "get_meteorite",
            lambda mid: {
                "id": mid,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
                "state_changed_at": "2026-01-03T00:00:00Z",
                "estelle_notified_at": None,
                "link": "https://example.com/jobs/1",
                "classify_outcome": "job",
                "content": "staging jd",
                "state": "LANDED",
                "source_kind": "email",
                "source_id": "msg-42",
                "error": None,
            },
            raising=False,  # pre-fix: name not imported yet; post-fix make-fix imports it
        )
        resp = jobs_client.get("/api/jobs/job-1769", headers=auth_headers)
        assert resp.status_code == 200
        rm = resp.get_json()["related_meteorite"]
        assert rm is not None
        assert rm["id"] == 42
        assert rm["link"] == "https://example.com/jobs/1"
        assert rm["classify_outcome"] == "job"
        assert rm["state"] == "LANDED"


    def test_skip_job_updates_state(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1974: route delegates to core candidate_skip_job; exactly one completion info line (AC 9).
        monkeypatch.setattr(
            jobs_mod, "get_job",
            lambda job_id: {"astral_job_id": job_id, "state": "CANDIDATE_REVIEW", "candidate_id": "cand-1"},
        )
        skip = MagicMock(return_value="CANDIDATE_SKIPPED")
        logger = MagicMock()
        monkeypatch.setattr(jobs_mod, "candidate_skip_job", skip)
        monkeypatch.setattr(jobs_mod, "logger", logger)
        resp = jobs_client.post("/api/jobs/job-1/skip", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True}
        skip.assert_called_once_with("job-1")
        logger.info.assert_called_once_with(
            "%s | api %s completed: POST %s", "cand-1", "/api/jobs/job-1/skip", 200,
        )

    def test_skip_job_logs_dash_without_candidate(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "NEW"})
        monkeypatch.setattr(jobs_mod, "candidate_skip_job", MagicMock(return_value="CANDIDATE_SKIPPED"))
        logger = MagicMock()
        monkeypatch.setattr(jobs_mod, "logger", logger)
        assert jobs_client.post("/api/jobs/job-1/skip", headers=auth_headers).status_code == 200
        assert logger.info.call_args.args[1] == "-"

    def test_skip_job_missing_returns_404(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: None)
        resp = jobs_client.post("/api/jobs/job-1/skip", headers=auth_headers)
        assert resp.status_code == 404

    def test_skip_job_invalid_transition_returns_409(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "CANDIDATE_APPLIED"})
        monkeypatch.setattr(
            jobs_mod,
            "candidate_skip_job",
            MagicMock(side_effect=ValueError("Invalid transition: CANDIDATE_APPLIED -> CANDIDATE_SKIPPED")),
        )
        logger = MagicMock()
        monkeypatch.setattr(jobs_mod, "logger", logger)
        resp = jobs_client.post("/api/jobs/job-1/skip", headers=auth_headers)
        assert resp.status_code == 409
        assert "Invalid transition" in resp.get_json()["error"]
        # 409 is not a completion — no info line.
        logger.info.assert_not_called()

    def test_candidate_action_applied_records_result(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "CANDIDATE_REVIEW"})
        set_result = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(jobs_mod, "set_candidate_result", set_result)
        monkeypatch.setattr(jobs_mod, "transition_job_state", transition)
        resp = jobs_client.post(
            "/api/jobs/job-1/candidate_action",
            json={"action": "applied", "notes": "sent"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        set_result.assert_called_once_with("job-1", "applied", notes="sent")
        transition.assert_called_once_with(["job-1"], "CANDIDATE_APPLIED")

    def test_candidate_action_invalid_returns_400(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id})
        resp = jobs_client.post("/api/jobs/job-1/candidate_action", json={"action": "nope"}, headers=auth_headers)
        assert resp.status_code == 400

    def test_candidate_action_invalid_transition_returns_409(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "NEW"})
        monkeypatch.setattr(jobs_mod, "set_candidate_result", MagicMock())
        monkeypatch.setattr(
            jobs_mod,
            "transition_job_state",
            MagicMock(side_effect=ValueError("Invalid transition: NEW -> CANDIDATE_APPLIED")),
        )
        resp = jobs_client.post(
            "/api/jobs/job-1/candidate_action",
            json={"action": "applied"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert "Invalid transition" in resp.get_json()["error"]

    def test_candidate_action_review_skips_result_row(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "state": "CANDIDATE_REVIEW"},
        )
        set_result = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(jobs_mod, "set_candidate_result", set_result)
        monkeypatch.setattr(jobs_mod, "transition_job_state", transition)
        resp = jobs_client.post(
            "/api/jobs/job-1/candidate_action",
            json={"action": "review", "notes": "later"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        set_result.assert_not_called()
        transition.assert_called_once_with(["job-1"], "CANDIDATE_REVIEW")

    def test_candidate_action_returns_404_when_job_missing(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: None)
        resp = jobs_client.post(
            "/api/jobs/missing-job/candidate_action",
            json={"action": "applied"},
            headers=auth_headers,
        )
        assert resp.status_code == 404
        assert "not found" in (resp.get_json() or {}).get("error", "").lower()

    def test_put_resume_content_persists_via_tracker(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: list[tuple[str, dict[str, str]]] = []
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"artifacts": {}}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_artifact_resume_content",
            lambda job_id, content: captured.append((job_id, content)),
        )
        resp = jobs_client.put(
            "/api/jobs/job-553/artifacts/resume_content",
            json={"resume_content": {"professional_summary": "Draft"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True}
        assert captured == [("job-553", {"professional_summary": "Draft"})]

    def test_put_resume_content_404_when_job_missing(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: None)
        resp = jobs_client.put(
            "/api/jobs/missing/artifacts/resume_content",
            json={"resume_content": {"professional_summary": "x"}},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_put_resume_content_400_when_not_dict(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id})
        resp = jobs_client.put(
            "/api/jobs/job-1/artifacts/resume_content",
            json={"resume_content": "not-a-dict"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "dict" in resp.get_json()["error"]

    def test_put_cover_letter_persists_via_tracker(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1592: PUT → save_job_artifact with catalog key.
        captured: list[tuple] = []
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"artifacts": {}}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_artifact",
            lambda job_id, key, content, *a, **k: captured.append((job_id, key, content)),
        )
        resp = jobs_client.put(
            "/api/jobs/job-565/artifacts/cover_letter",
            json={"cover_letter": {"Subject": "Hi", "Letter": "Body"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert captured == [
            ("job-565", "job.artifacts.cover_letter", {"Subject": "Hi", "Letter": "Body"})
        ]

    def test_put_application_responses_persists_via_save_job_data(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: list[tuple[str, dict]] = []
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"artifacts": {}}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_data",
            lambda job_id, payload: captured.append((job_id, payload)),
        )
        resp = jobs_client.put(
            "/api/jobs/job-565/artifacts/application_responses",
            json={"application_responses": {"q1": "answer"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert captured == [
            ("job-565", {"artifacts": {"application_responses": {"q1": "answer"}}}),
        ]

    def test_approve_artifacts_from_recommended(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        flat = cfg.BUILD_ARTIFACTS_BASE_STATE
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "RECOMMENDED"})
        start = MagicMock(return_value=flat)
        monkeypatch.setattr(jobs_mod, "start_artifact_build", start)
        resp = jobs_client.post("/api/jobs/job-595/approve_artifacts", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True, "state": flat}
        start.assert_called_once_with("job-595")

    def test_approve_artifacts_wrong_state_returns_409(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "state": cfg.BUILD_ARTIFACTS_BASE_STATE},
        )
        resp = jobs_client.post("/api/jobs/job-595/approve_artifacts", headers=auth_headers)
        assert resp.status_code == 409
        assert "RECOMMENDED" in resp.get_json()["error"]

    def test_approve_artifacts_missing_job_returns_404(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: None)
        resp = jobs_client.post("/api/jobs/missing/approve_artifacts", headers=auth_headers)
        assert resp.status_code == 404


class TestAst562GenerateCancelRoutes:
    """AST-562 — Generate Artifacts / Cancel artifact build API (Recommended Job Modal)."""

    def test_generate_artifacts_happy_path(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        flat = cfg.BUILD_ARTIFACTS_BASE_STATE
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "RECOMMENDED"})
        start = MagicMock(return_value=flat)
        monkeypatch.setattr(jobs_mod, "start_artifact_build", start)
        resp = jobs_client.post("/api/jobs/job-562/generate_artifacts", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True, "state": flat}
        start.assert_called_once_with("job-562")

    def test_cancel_artifact_build_happy_path(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "state": cfg.BUILD_ARTIFACTS_BASE_STATE},
        )
        cancel = MagicMock(return_value="RECOMMENDED")
        monkeypatch.setattr(jobs_mod, "cancel_artifact_build", cancel)
        resp = jobs_client.post("/api/jobs/job-562/cancel_artifact_build", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True, "state": "RECOMMENDED"}
        cancel.assert_called_once_with("job-562")

    def test_generate_artifacts_404_when_missing(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: None)
        resp = jobs_client.post("/api/jobs/missing/generate_artifacts", headers=auth_headers)
        assert resp.status_code == 404

    def test_cancel_artifact_build_404_when_missing(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: None)
        resp = jobs_client.post("/api/jobs/missing/cancel_artifact_build", headers=auth_headers)
        assert resp.status_code == 404

    def test_generate_artifacts_409_wrong_state(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "NEW"})
        monkeypatch.setattr(
            jobs_mod,
            "start_artifact_build",
            MagicMock(side_effect=ValueError("generate only from RECOMMENDED")),
        )
        resp = jobs_client.post("/api/jobs/job-562/generate_artifacts", headers=auth_headers)
        assert resp.status_code == 409
        assert "RECOMMENDED" in resp.get_json()["error"]

    def test_cancel_artifact_build_409_wrong_state(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "RECOMMENDED"})
        monkeypatch.setattr(
            jobs_mod,
            "cancel_artifact_build",
            MagicMock(side_effect=ValueError("cancel only from BUILD_ARTIFACTS in-progress hop states")),
        )
        resp = jobs_client.post("/api/jobs/job-562/cancel_artifact_build", headers=auth_headers)
        assert resp.status_code == 409
        assert "BUILD_ARTIFACTS" in resp.get_json()["error"]


class TestAst1100JobArtifactPinResolveApi:
    """AST-1100: GET hydrates pin slots; PUT aliases for remapped keys."""

    def test_detail_hydrates_pin_slots(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "job_data": {"artifacts": {"job_resume": "pin-1", "analysis_upshot": {"s": 1}}},
            },
        )
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [])
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False: {
                **(art or {}),
                "job_resume": {"professional_summary": "from-pin"},
            },
        )
        resp = jobs_client.get("/api/jobs/job-1100", headers=auth_headers)
        assert resp.status_code == 200
        art = resp.get_json()["job_data"]["artifacts"]
        assert art["job_resume"] == {"professional_summary": "from-pin"}
        assert art["analysis_upshot"] == {"s": 1}

    def test_put_job_resume_persists_via_tracker_body_helper(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1592: PUT stays thin → save_job_artifact(catalog key) (table SoT in tracker).
        body_writes: list[tuple] = []
        raw_saves: list[tuple[str, dict]] = []
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "job_data": {"artifacts": {}},
            },
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_artifact",
            lambda job_id, key, content, *a, **k: body_writes.append((job_id, key, content)),
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_data",
            lambda job_id, payload: raw_saves.append((job_id, payload)),
            raising=False,
        )
        resp = jobs_client.put(
            "/api/jobs/job-1100/artifacts/job_resume",
            json={"job_resume": {"professional_summary": "Edited"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert body_writes == [
            ("job-1100", "job.artifacts.job_resume", {"professional_summary": "Edited"})
        ]
        assert raw_saves == []

    def test_put_proposed_answers_writes_body_dict(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: list[tuple[str, dict]] = []
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"artifacts": {}}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_data",
            lambda job_id, payload: captured.append((job_id, payload)),
        )
        resp = jobs_client.put(
            "/api/jobs/job-1100/artifacts/proposed_answers",
            json={"proposed_answers": {"q1": "a"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert captured == [
            ("job-1100", {"artifacts": {"proposed_answers": {"q1": "a"}}}),
        ]

    def test_put_job_resume_400_when_not_dict(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id})
        resp = jobs_client.put(
            "/api/jobs/job-1100/artifacts/job_resume",
            json={"job_resume": "not-a-dict"},
            headers=auth_headers,
        )
        assert resp.status_code == 400


class TestAst1420CopySnapshotRoute:
    """AST-1420: GET /api/jobs/<id>/copy — auth, 404, assembler wrap, no hydrate."""

    def test_unauthenticated_rejected(
        self, jobs_client: FlaskClient
    ) -> None:
        resp = jobs_client.get("/api/jobs/job-1420/copy")
        assert resp.status_code == 401
        assert resp.get_json()["error"] == "Missing or invalid session credentials"

    def test_missing_job_404(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "assemble_job_copy_snapshot", lambda *a, **k: None)
        resp = jobs_client.get("/api/jobs/missing/copy", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Not found"}

    def test_success_returns_assembler_json_without_hydrate(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        hydrate = MagicMock()
        flatten = MagicMock()
        story = MagicMock()
        monkeypatch.setattr(jobs_mod, "hydrate_job_artifacts_for_display", hydrate)
        monkeypatch.setattr(jobs_mod, "_flatten_grades", flatten)
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", story)
        snapshot = {
            "job": {"astral_job_id": "job-1420", "job_data": {"artifacts": {"job_resume": "pin-1"}}},
            "agent_data": {"pin-1": {"id": "pin-1", "blocks": {"RESPONSE": {"id": "pin-1", "content": "body"}}}},
        }
        monkeypatch.setattr(jobs_mod, "assemble_job_copy_snapshot", lambda *a, **k: snapshot)
        resp = jobs_client.get("/api/jobs/job-1420/copy", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == snapshot
        hydrate.assert_not_called()
        flatten.assert_not_called()
        story.assert_not_called()

    def test_assembler_exception_500(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "assemble_job_copy_snapshot",
            MagicMock(side_effect=RuntimeError("boom")),
        )
        resp = jobs_client.get("/api/jobs/job-1420/copy", headers=auth_headers)
        assert resp.status_code == 500
        assert resp.get_json() == {"error": "boom"}

    def test_debug_query_flags_passed_to_ui_llm_debug(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: list[bool] = []

        def _dbg(*, explicit_debug: bool = False) -> bool:
            captured.append(explicit_debug)
            return False

        monkeypatch.setattr(jobs_mod, "ui_llm_debug", _dbg)
        monkeypatch.setattr(jobs_mod, "assemble_job_copy_snapshot", lambda *a, **k: {"job": {}, "agent_data": {}})
        for qs in ("", "?debug=1", "?debug=true", "?debug=yes", "?debug=no"):
            jobs_client.get(f"/api/jobs/job-1420/copy{qs}", headers=auth_headers)
        assert captured == [False, True, True, True, False]


class TestAst1453SkippedEditMetaAndPut:
    """AST-1453: GET fields_editable/legal_next_states; PUT persist + status mapping."""

    def _detail_wire(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        job: dict | None,
        successors: list[str] | None = None,
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda jid: None if job is None else dict(job))
        monkeypatch.setattr(
            jobs_mod,
            "legal_job_successor_states",
            lambda state: list(successors or ["NEW", "ERROR_GRADE_DO"]),
        )
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False, astral_job_id=None: art or {},
        )
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [])
        monkeypatch.setattr(jobs_mod, "get_job_artifacts", lambda job: {})

    def test_get_detail_skipped_attaches_meta(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._detail_wire(
            monkeypatch,
            job={
                "astral_job_id": "job-1453",
                "state": "CANDIDATE_SKIPPED",
                "job_data": {},
            },
            successors=["NEW"],
        )
        resp = jobs_client.get("/api/jobs/job-1453", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["fields_editable"] is True
        assert body["legal_next_states"] == ["NEW"]

    def test_get_detail_non_skipped_meta_locked(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        called: list[str] = []

        def _succ(state: str) -> list[str]:
            called.append(state)
            return ["SHOULD_NOT"]

        self._detail_wire(
            monkeypatch,
            job={"astral_job_id": "job-1453", "state": "RECOMMENDED", "job_data": {}},
        )
        monkeypatch.setattr(jobs_mod, "legal_job_successor_states", _succ)
        resp = jobs_client.get("/api/jobs/job-1453", headers=auth_headers)
        body = resp.get_json()
        assert body["fields_editable"] is False
        assert body["legal_next_states"] == []
        assert called == []

    def test_put_unauthenticated_401(self, jobs_client: FlaskClient) -> None:
        resp = jobs_client.put("/api/jobs/job-1453", json={"job_title": "T"})
        assert resp.status_code == 401

    def test_put_empty_body_400(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = jobs_client.put("/api/jobs/job-1453", json={"nope": 1}, headers=auth_headers)
        assert resp.status_code == 400
        assert "No valid fields" in resp.get_json()["error"]

    def test_put_missing_404(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda jid: None)
        resp = jobs_client.put(
            "/api/jobs/missing",
            json={"job_title": "T"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_put_not_skipped_409(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda jid: {"astral_job_id": jid, "state": "RECOMMENDED", "job_data": {}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "persist_skipped_job_edits",
            MagicMock(side_effect=ValueError("Job is not in a skipped state")),
        )
        resp = jobs_client.put(
            "/api/jobs/job-1453",
            json={"job_title": "T"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert resp.get_json()["error"] == "Job is not in a skipped state"

    def test_put_unregistered_state_409(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1811: registry keys never 409 on the skipped path; non-JOB_STATES targets do.
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda jid: {"astral_job_id": jid, "state": "CANDIDATE_SKIPPED", "job_data": {}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "persist_skipped_job_edits",
            MagicMock(side_effect=ValueError("Value 'PASSED_GET_RETRY' not in allowed list: [...]")),
        )
        resp = jobs_client.put(
            "/api/jobs/job-1453",
            json={"state": "PASSED_GET_RETRY"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert "not in allowed list" in resp.get_json()["error"]

    def test_put_empty_title_400(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda jid: {"astral_job_id": jid, "state": "CANDIDATE_SKIPPED", "job_data": {}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "persist_skipped_job_edits",
            MagicMock(side_effect=ValueError("job_title required")),
        )
        resp = jobs_client.put(
            "/api/jobs/job-1453",
            json={"job_title": "  "},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "job_title required"

    def test_put_success_returns_detail_shape(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        persist = MagicMock(return_value={"astral_job_id": "job-1453", "state": "NEW"})
        monkeypatch.setattr(jobs_mod, "persist_skipped_job_edits", persist)
        # After persist, detail() reloads job — non-skipped meta.
        self._detail_wire(
            monkeypatch,
            job={
                "astral_job_id": "job-1453",
                "state": "NEW",
                "job_title": "Saved",
                "job_data": {},
            },
            successors=[],
        )
        # get_job: first call (pre-persist existence) + detail reload
        jobs = {
            "pre": {"astral_job_id": "job-1453", "state": "CANDIDATE_SKIPPED", "job_data": {}},
            "post": {
                "astral_job_id": "job-1453",
                "state": "NEW",
                "job_title": "Saved",
                "job_data": {},
            },
        }
        calls = {"n": 0}

        def _get(jid: str):
            calls["n"] += 1
            return dict(jobs["pre"] if calls["n"] == 1 else jobs["post"])

        monkeypatch.setattr(jobs_mod, "get_job", _get)
        monkeypatch.setattr(jobs_mod, "legal_job_successor_states", lambda s: [])
        resp = jobs_client.put(
            "/api/jobs/job-1453",
            json={"job_title": "Saved", "state": "NEW"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["job_title"] == "Saved"
        assert body["fields_editable"] is False
        assert body["legal_next_states"] == []
        persist.assert_called_once_with(
            "job-1453", {"job_title": "Saved", "state": "NEW"}
        )

# AST-2133: responses carry the composed JD (preamble + telescope capture); PUT never writes the JD.
class TestAst2133ComposedJdResponses:
    _RAW = "Nav\n\nEngineer\nBuild things.\nApply for this job\nfooter"

    @pytest.fixture(autouse=True)
    def _db(self, sqlite_in_memory):
        return sqlite_in_memory

    def _ref(self) -> str:
        from src.core import gazer
        return gazer.keep_telescope_data(None, "https://jobs.example/1", "VISIBLE_TEXT", self._RAW)

    def _wire_detail(self, monkeypatch: pytest.MonkeyPatch, job: dict) -> None:
        TestAst1453SkippedEditMetaAndPut()._detail_wire(monkeypatch, job=job, successors=[])

    def test_ac7_detail_composes_referenced_capture_without_writing_back(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stored = {"job_description": "Email pre", "jd_telescope_data_id": self._ref(), "note": "n"}
        job = {"astral_job_id": "job-2133", "state": "NEW", "job_title": "Engineer", "job_data": stored}
        self._wire_detail(monkeypatch, job)
        resp = jobs_client.get("/api/jobs/job-2133", headers=auth_headers)
        assert resp.status_code == 200
        jd = resp.get_json()["job_data"]
        assert jd["job_description"] == "Email pre\n\nEngineer\nBuild things."
        assert jd["note"] == "n"
        # Response-only: the stored job_data dict (shared via the shallow get_job copy) is untouched
        assert stored["job_description"] == "Email pre"

    def test_ac7_detail_no_reference_returns_stored_text_exactly(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        pre = "Pasted JD\n\n\n\nverbatim  "
        self._wire_detail(monkeypatch, {"astral_job_id": "j", "state": "NEW", "job_data": {"job_description": pre}})
        assert jobs_client.get("/api/jobs/j", headers=auth_headers).get_json()["job_data"]["job_description"] == pre

    @pytest.mark.parametrize("view", ["ready", "review", "applied", "skipped"])
    def test_ac7_list_rows_compose_referenced_capture(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, view: str
    ) -> None:
        rows = [{"astral_job_id": "j", "job_title": "Engineer", "job_data": {"jd_telescope_data_id": self._ref()}}]
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kw: [dict(r) for r in rows])
        resp = jobs_client.get(f"/api/jobs?view={view}", headers=auth_headers)
        assert resp.get_json()[0]["job_data"]["job_description"] == "Engineer\nBuild things."

    def test_ac7_virtual_skip_rows_compose(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        virt = {"astral_job_id": "v", "state": "NEW", "job_title": "Engineer",
                "job_data": {"job_description": "pre", "jd_telescope_data_id": self._ref()}}
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kw: [])
        monkeypatch.setattr(jobs_mod, "list_jobs_below_dispatch_score_floor", lambda cid: [virt])
        monkeypatch.setattr(jobs_mod, "score_floor_by_trigger_for_candidate", lambda cid: {"NEW": 5.0})
        out = jobs_client.get("/api/jobs?view=skipped&candidate_id=cand-1", headers=auth_headers).get_json()
        assert [r["job_data"]["job_description"] for r in out] == ["pre\n\nEngineer\nBuild things."]

    def test_ac9_put_jd_only_400_without_persist(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        persist = MagicMock()
        monkeypatch.setattr(jobs_mod, "persist_skipped_job_edits", persist)
        resp = jobs_client.put("/api/jobs/j", json={"job_description": "pasted"}, headers=auth_headers)
        assert resp.status_code == 400
        assert "No valid fields" in resp.get_json()["error"]
        persist.assert_not_called()

    def test_ac9_put_title_and_jd_persists_title_only(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        persist = MagicMock(return_value={"astral_job_id": "j", "state": "CANDIDATE_SKIPPED"})
        monkeypatch.setattr(jobs_mod, "persist_skipped_job_edits", persist)
        self._wire_detail(monkeypatch, {"astral_job_id": "j", "state": "CANDIDATE_SKIPPED", "job_data": {}})
        resp = jobs_client.put(
            "/api/jobs/j", json={"job_title": "T", "job_description": "pasted"}, headers=auth_headers
        )
        assert resp.status_code == 200
        persist.assert_called_once_with("j", {"job_title": "T"})


# AST-2133 AC9 end-to-end: real tmp DB — PUT never changes the stored job_data.
class TestAst2133PutJdReadOnlyE2E:
    @pytest.fixture
    def app_client(self, seeded_db) -> FlaskClient:
        from flask import Flask

        from ui.api.api_jobs import jobs_bp

        seeded_db.save_company("acme", state="IMPORTED", candidate_id="cand-1")
        seeded_db.save_job("j-2133", company="acme", state="CANDIDATE_SKIPPED", candidate_id="cand-1",
                           job_title="Old", job_link="https://old.example",
                           job_data={"job_description": "stored pre"})
        app = Flask(__name__)
        app.register_blueprint(jobs_bp)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_ac9_jd_only_400_and_title_plus_jd_saves_title_only(
        self, app_client: FlaskClient, auth_headers: dict[str, str], seeded_db
    ) -> None:
        resp = app_client.put("/api/jobs/j-2133", json={"job_description": "x"}, headers=auth_headers)
        assert resp.status_code == 400
        assert seeded_db.get_job("j-2133")["job_data"] == {"job_description": "stored pre"}

        resp = app_client.put(
            "/api/jobs/j-2133", json={"job_title": "New", "job_description": "x"}, headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.get_json()["job_data"]["job_description"] == "stored pre"
        row = seeded_db.get_job("j-2133")
        assert row["job_title"] == "New"
        assert row["job_data"] == {"job_description": "stored pre"}


# Branches: detail exposes parent/track fields + inherited job_link (AST-1704).
class TestAst1704JobsDetailParentFields:
    def test_detail_exposes_source_entity_and_job_link(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        crumb = "From:a@x.com 9/17 14:05 Eastern To:b@y.com"
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "job_title": "Analyst",
                "company_id": "acme",
                "source": "meteorite",
                "source_entity_id": "mid-1",
                "job_link": crumb,
                "job_data": {},
            },
        )
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [])
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, astral_job_id=None, debug=False: art or {},
        )
        resp = jobs_client.get("/api/jobs/job-1704", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["company_id"] == "acme"
        assert body["source"] == "meteorite"
        assert body["source_entity_id"] == "mid-1"
        assert body["job_link"] == crumb


# Branches: detail can_skip (AST-1872) — real core prior-state rule, not mocked; missing state → False.
class TestAst1872DetailCanSkip:
    @pytest.mark.parametrize(
        ("state", "expected"),
        [
            ("RECOMMENDED", True),
            ("CANDIDATE_REVIEW", True),
            (f"{cfg.BUILD_ARTIFACTS_BASE_STATE}.draft_job_resume", True),
            ("CANDIDATE_SKIPPED", False),
            ("CANDIDATE_APPLIED", False),
            (None, False),
        ],
    )
    def test_detail_can_skip_by_state(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
        state, expected: bool,
    ) -> None:
        job = {"astral_job_id": "job-1872", "job_data": {}}
        if state is not None:
            job["state"] = state
        monkeypatch.setattr(jobs_mod, "get_job", lambda jid: dict(job))
        monkeypatch.setattr(jobs_mod, "get_entity_agent_story", lambda job: [])
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False, astral_job_id=None: art or {},
        )
        monkeypatch.setattr(jobs_mod, "get_meteorite_by_astral_job_id", lambda _jid: None)
        resp = jobs_client.get("/api/jobs/job-1872", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["can_skip"] is expected


# AST-1974 · AST-1970: real SQLite — five views partition every job once; nav counts == list lengths;
# skip legal from Processing states (claim released), illegal from Applied; below-floor rows Skipped-only.
class TestAst1974JobsPartitionRealDb:
    _VIEWS = ("ready", "review", "applied", "processing", "skipped")
    _PROCESSING = ("NEW", "PASSED_JD", "METEORITE_QUALIFIED", cfg.BUILD_ARTIFACTS_BASE_STATE,
                   cfg.resume_artifact_compound_state("anticipate_scan"))

    @pytest.fixture
    def app_client(self, seeded_db) -> FlaskClient:
        from flask import Flask
        from ui.api.api_jobs import jobs_bp
        from ui.api.api_system import system_bp

        db = seeded_db
        db.save_company("acme", state="IMPORTED", candidate_id="cand-1")
        seeds = {
            "j-ready": "CANDIDATE_REVIEW",
            "j-review": "RECOMMENDED",
            "j-applied": "CANDIDATE_APPLIED",
            # AST-2086: build-chain terminals are per hop (ERROR_<HOP>); BUILD_FAILED is retired.
            "j-err-build": "ERROR_ANTICIPATE_SCAN",
            "j-err-cover": "ERROR_DRAFT_COVER_LETTER",
            "j-skipped": "CANDIDATE_SKIPPED",
            **{f"j-proc-{i}": s for i, s in enumerate(self._PROCESSING)},
        }
        for jid, state in seeds.items():
            db.save_job(jid, company="acme", state=state, candidate_id="cand-1")
        # Below-floor virtual skip: PASSED_JD trigger floor 7.0, score 2.0 → Skipped only.
        db.save_dispatch_task("cand-1", "evaluate_jd", min_count=1, trigger_state="PASSED_JD", score_floor=7.0)
        db.save_job("j-below", company="acme", state="PASSED_JD", candidate_id="cand-1")
        db.save_job("j-below", latest_score=2.0)
        db.save_job("j-proc-1", latest_score=9.0)  # PASSED_JD above floor stays Processing
        app = Flask(__name__)
        app.register_blueprint(jobs_bp)
        app.register_blueprint(system_bp)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def _ids(self, client: FlaskClient, headers: dict[str, str], view: str) -> list[str]:
        resp = client.get(f"/api/jobs?view={view}&candidate_id=cand-1", headers=headers)
        assert resp.status_code == 200, view
        return [r["astral_job_id"] for r in resp.get_json()]

    def test_views_partition_every_job_exactly_once(self, app_client: FlaskClient, auth_headers: dict[str, str], seeded_db) -> None:
        # AC 2 / 3 / 4 / 5 / 6.
        views = {v: self._ids(app_client, auth_headers, v) for v in self._VIEWS}
        assert views["ready"] == ["j-ready"]
        assert views["review"] == ["j-review"]
        assert views["applied"] == ["j-applied"]
        assert set(views["skipped"]) == {"j-err-build", "j-err-cover", "j-skipped", "j-below"}
        assert set(views["processing"]) == {f"j-proc-{i}" for i in range(len(self._PROCESSING))}
        union = [jid for v in self._VIEWS for jid in views[v]]
        assert len(union) == len(set(union))
        with seeded_db._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM job WHERE candidate_id='cand-1'").fetchone()[0]
        assert len(union) == total

    def test_nav_counts_match_list_lengths(self, app_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        # AC 1 / AC 10 — six Jobs items, each carrying a count equal to its page's list length.
        nav = app_client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers).get_json()
        jobs = next(g for g in nav if g["label"] == "Jobs")
        counts = {it["path"]: it["count"] for it in jobs["items"]}
        assert list(counts) == [f"/jobs/{v}" for v in ("ready", "review", "applied", "processing", "skipped", "meteorites")]
        for v in self._VIEWS:
            assert counts[f"/jobs/{v}"] == len(self._ids(app_client, auth_headers, v)), v
        assert counts["/jobs/meteorites"] == 0

    def test_skip_from_processing_states_releases_claim(self, app_client: FlaskClient, auth_headers: dict[str, str], seeded_db) -> None:
        # AC 8 — every Processing seed skips; a held batch claim is cleared; Applied still 409.
        assert seeded_db.claim_job_batch("b-1974", "NEW", 10, candidate_id="cand-1") >= 1
        assert seeded_db.get_job("j-proc-0")["batch_id"] == "b-1974"
        for i in range(len(self._PROCESSING)):
            resp = app_client.post(f"/api/jobs/j-proc-{i}/skip", headers=auth_headers)
            assert resp.status_code == 200, self._PROCESSING[i]
        assert seeded_db.get_job("j-proc-0")["batch_id"] in (None, "")
        skipped = self._ids(app_client, auth_headers, "skipped")
        processing = self._ids(app_client, auth_headers, "processing")
        for i in range(len(self._PROCESSING)):
            assert f"j-proc-{i}" in skipped and f"j-proc-{i}" not in processing
            assert seeded_db.get_job(f"j-proc-{i}")["state"] == "CANDIDATE_SKIPPED"
        assert app_client.post("/api/jobs/j-applied/skip", headers=auth_headers).status_code == 409
        assert seeded_db.get_job("j-applied")["state"] == "CANDIDATE_APPLIED"

    def test_error_build_artifacts_detail_editable_with_retry(self, app_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        # AC 5 — terminal build failure on Skipped is editable and retries to RECOMMENDED.
        resp = app_client.get("/api/jobs/j-err-build", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["fields_editable"] is True
        assert "RECOMMENDED" in body["legal_next_states"]


# AST-2067 Branches (both job routes): missing job 404; PUT body not a dict / uuid missing-blank 400;
# core ValueError 400 (candidate key on job route, cross-key/cross-job uuid = AC7, current
# unchanged); unexpected Exception → logged once + 500 payload; 200 (PUT logs one completion line,
# candidate_id from the job row or "-").
class TestAst2067JobVersionRoutes:
    _BASE = "/api/jobs/job-1/artifacts/job.artifacts.cover_letter"

    @pytest.fixture
    def db(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            jobs_mod, "get_job", lambda jid: {"astral_job_id": jid, "candidate_id": "cand-1"} if jid == "job-1" else None
        )
        return sqlite_in_memory

    def _seed(self, db, eid: str = "job-1", at: str = "cover_letter", n: int = 3) -> list:
        return [
            db.save_artifact("job", eid, at, {"Subject": "S", "Letter": f"v{i}", "signature": ""}, candidate_id="cand-1")
            for i in range(1, n + 1)
        ]

    def test_list_and_set_current_200(
        self, jobs_client: FlaskClient, auth_headers, db, caplog: pytest.LogCaptureFixture
    ) -> None:
        v1, v2, v3 = self._seed(db)
        got = jobs_client.get(f"{self._BASE}/versions", headers=auth_headers)
        assert got.status_code == 200
        versions = got.get_json()["versions"]
        assert sorted(versions, key=lambda u: versions[u]["position"]) == [v1, v2, v3]
        caplog.set_level("INFO")
        put = jobs_client.put(f"{self._BASE}/current", json={"artifact_uuid": v2}, headers=auth_headers)
        assert put.status_code == 200
        assert put.get_json()["current"] == v2
        assert db.get_current_artifact("job", "job-1", "cover_letter")["artifact_data"]["Letter"] == "v2"
        assert any(
            m.startswith("cand-1 | api") and "completed: PUT 200" in m for m in (r.getMessage() for r in caplog.records)
        )

    def test_cross_key_uuid_400_current_unchanged(self, jobs_client: FlaskClient, auth_headers, db) -> None:
        # AC7: job_resume uuid and other-job uuid on the cover_letter route → 400; v3 stays current.
        _, _, v3 = self._seed(db)
        other_key = self._seed(db, at="job_resume", n=1)[0]
        other_job = self._seed(db, eid="job-2", n=1)[0]
        for uid in (other_key, other_job):
            res = jobs_client.put(f"{self._BASE}/current", json={"artifact_uuid": uid}, headers=auth_headers)
            assert res.status_code == 400
            assert "is not a version of" in res.get_json()["error"]
        assert db.get_current_artifact("job", "job-1", "cover_letter")["artifact_uuid"] == v3

    @pytest.mark.parametrize(
        "method,suffix,body", [("get", "versions", None), ("put", "current", {"artifact_uuid": "u"})]
    )
    def test_missing_job_404(self, jobs_client: FlaskClient, auth_headers, db, method, suffix, body) -> None:
        res = getattr(jobs_client, method)(
            f"/api/jobs/nope/artifacts/job.artifacts.cover_letter/{suffix}", json=body, headers=auth_headers
        )
        assert res.status_code == 404
        assert res.get_json() == {"error": "Not found"}

    @pytest.mark.parametrize("body", [["not", "a", "dict"], {}, {"artifact_uuid": "  "}, {"artifact_uuid": 7}])
    def test_put_bad_body_400(self, jobs_client: FlaskClient, auth_headers, db, body) -> None:
        res = jobs_client.put(f"{self._BASE}/current", json=body, headers=auth_headers)
        assert res.status_code == 400
        assert res.get_json() == {"error": "artifact_uuid required"}

    @pytest.mark.parametrize(
        "method,suffix,body", [("get", "versions", None), ("put", "current", {"artifact_uuid": "u"})]
    )
    def test_candidate_key_on_job_route_400(
        self, jobs_client: FlaskClient, auth_headers, db, method, suffix, body
    ) -> None:
        res = getattr(jobs_client, method)(
            f"/api/jobs/job-1/artifacts/candidate.artifacts.base_resume/{suffix}", json=body, headers=auth_headers
        )
        assert res.status_code == 400
        assert "not job-scoped" in res.get_json()["error"]

    @pytest.mark.parametrize(
        "patch,method,suffix,body",
        [
            ("list_job_artifact_versions", "get", "versions", None),
            ("set_job_artifact_current", "put", "current", {"artifact_uuid": "u"}),
        ],
    )
    @pytest.mark.parametrize("job_cid", ["cand-1", None])
    def test_unexpected_error_logged_once_500(
        self,
        jobs_client: FlaskClient,
        auth_headers,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
        patch,
        method,
        suffix,
        body,
        job_cid,
    ) -> None:
        def _boom(*a, **k):
            raise RuntimeError("db down")

        monkeypatch.setattr(jobs_mod, "get_job", lambda jid: {"astral_job_id": jid, "candidate_id": job_cid})
        monkeypatch.setattr(jobs_mod, patch, _boom)
        caplog.set_level("ERROR")
        res = getattr(jobs_client, method)(f"{self._BASE}/{suffix}", json=body, headers=auth_headers)
        assert res.status_code == 500
        assert res.get_json()["exception_type"] == "RuntimeError"
        errors = [r.getMessage() for r in caplog.records if r.levelname == "ERROR" and "failed" in r.getMessage()]
        assert len(errors) == 1 and errors[0].startswith(f"{job_cid or '-'} | api")


# Branches: GET /api/jobs/<id>/resume_structure — missing job 404 / 200 / unexpected 500 (cid set / "-").
# PUT /api/jobs/<id>/artifacts/job_resume_structure — missing job 404 / body not dict (json not dict,
# key missing, value not dict) 400 / ValueError 400 (no log) / unexpected 500 / 200 + INFO.
class TestAst2081JobResumeStructureRoutes:
    _GET = "/api/jobs/{}/resume_structure"
    _PUT = "/api/jobs/{}/artifacts/job_resume_structure"

    @staticmethod
    def _cd() -> dict:
        from src.core import candidate as core_candidate

        raw = core_candidate.default_resume_structure()
        raw["sections"]["professional_summary"]["title"] = "Candidate Summary"
        return {"artifacts": {"resume_structure": raw, "base_resume": {"awards": "Prize"}}}

    @pytest.fixture
    def db(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch):
        from src.core import tracker as tracker_mod

        monkeypatch.setattr(
            jobs_mod, "get_job", lambda jid: {"astral_job_id": jid, "candidate_id": "cand-1"} if jid in ("job-a", "job-b") else None
        )
        monkeypatch.setattr(tracker_mod, "_candidate_id_for_job", lambda jid: "cand-1")
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._cd())
        return sqlite_in_memory

    def _inherited_payload(self) -> dict:
        from src.core import candidate as core_candidate

        cd = self._cd()
        resolved = core_candidate.hydrate_resume_structure_from_base_resume(
            core_candidate.resolve_resume_structure(cd), cd["artifacts"]["base_resume"]
        )
        return core_candidate.resume_structure_editor_payload(resolved)

    @pytest.mark.parametrize("method,url", [("get", _GET), ("put", _PUT)])
    def test_missing_job_404(self, jobs_client: FlaskClient, auth_headers, db, method, url) -> None:
        res = getattr(jobs_client, method)(url.format("nope"), json={"job_resume_structure": {}}, headers=auth_headers)
        assert res.status_code == 404
        assert res.get_json() == {"error": "Not found"}

    def test_get_inherits_candidate_and_writes_nothing(self, jobs_client: FlaskClient, auth_headers, db) -> None:
        # AC16: unedited job → candidate's all_sections (hydrated like the candidate GET); no row written.
        res = jobs_client.get(self._GET.format("job-a"), headers=auth_headers)
        assert res.status_code == 200
        body = res.get_json()
        assert body == self._inherited_payload()
        assert "awards" in {r["id"] for r in body["all_sections"]}
        assert body["catalog"]["body_format_details"]["line"]["label"] == "Line"
        assert db.list_artifacts("job", "job-a", "job_resume_structure") == []

    def test_put_then_get_isolated_per_job(
        self, jobs_client: FlaskClient, auth_headers, db, caplog: pytest.LogCaptureFixture
    ) -> None:
        # AC15 + AC18: job A edits (rename / format / reorder / accent) show on A only; B still inherits.
        from src.core import candidate as core_candidate

        raw = self._cd()["artifacts"]["resume_structure"]
        secs = raw["sections"]
        secs["professional_summary"]["title"] = "Profile"
        secs["highlights"]["format"] = "line"
        secs["core_competencies"]["order"], secs["technical_skills"]["order"] = 10, 5
        accent = cfg.BUILD_CONFIG["accent_palette"][2].upper()
        caplog.set_level("INFO")
        put = jobs_client.put(
            self._PUT.format("job-a"),
            json={"job_resume_structure": {"sections": secs, "accent_color": accent}},
            headers=auth_headers,
        )
        assert put.status_code == 200 and put.get_json() == {"ok": True}
        info = [r.getMessage() for r in caplog.records if r.levelname == "INFO" and "completed: PUT 200" in r.getMessage()]
        assert info == ["cand-1 | api /api/jobs/job-a/artifacts/job_resume_structure completed: PUT 200"]
        a = jobs_client.get(self._GET.format("job-a"), headers=auth_headers).get_json()
        rows = {r["id"]: r for r in a["all_sections"]}
        assert rows["professional_summary"]["title"] == "Profile"
        assert rows["highlights"]["format"] == "line"
        assert rows["technical_skills"]["order"] < rows["core_competencies"]["order"]
        assert a["accent_color"] == accent
        assert jobs_client.get(self._GET.format("job-b"), headers=auth_headers).get_json() == self._inherited_payload()
        assert db.list_artifacts("candidate", "cand-1", "resume_structure") == []
        assert core_candidate.resolve_resume_structure(self._cd())["sections"]["professional_summary"]["title"] == (
            "Candidate Summary"
        )

    @pytest.mark.parametrize(
        "body", [["not", "a", "dict"], {}, {"job_resume_structure": "x"}, {"job_resume_structure": ["x"]}]
    )
    def test_put_body_not_dict_400(self, jobs_client: FlaskClient, auth_headers, db, body) -> None:
        res = jobs_client.put(self._PUT.format("job-a"), json=body, headers=auth_headers)
        assert res.status_code == 400
        assert res.get_json() == {"error": "job_resume_structure must be a dict"}

    def test_put_invalid_structure_400_no_log(
        self, jobs_client: FlaskClient, auth_headers, db, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level("INFO")
        res = jobs_client.put(
            self._PUT.format("job-a"), json={"job_resume_structure": {"accent_color": "#123456"}}, headers=auth_headers
        )
        assert res.status_code == 400
        assert "accent_palette" in res.get_json()["error"]
        assert not [r for r in caplog.records if r.name == jobs_mod.logger.name]
        assert db.list_artifacts("job", "job-a", "job_resume_structure") == []

    @pytest.mark.parametrize(
        "patch,method,url",
        [("get_job_effective_resume_structure", "get", _GET), ("save_job_artifact", "put", _PUT)],
    )
    @pytest.mark.parametrize("job_cid", ["cand-1", None])
    def test_unexpected_error_logged_once_500(
        self,
        jobs_client: FlaskClient,
        auth_headers,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
        patch,
        method,
        url,
        job_cid,
    ) -> None:
        def _boom(*a, **k):
            raise RuntimeError("db down")

        monkeypatch.setattr(jobs_mod, "get_job", lambda jid: {"astral_job_id": jid, "candidate_id": job_cid})
        monkeypatch.setattr(jobs_mod, patch, _boom)
        caplog.set_level("ERROR")
        res = getattr(jobs_client, method)(
            url.format("job-a"), json={"job_resume_structure": {"sections": {}}}, headers=auth_headers
        )
        assert res.status_code == 500
        assert res.get_json()["exception_type"] == "RuntimeError"
        errors = [r.getMessage() for r in caplog.records if r.levelname == "ERROR" and "failed" in r.getMessage()]
        assert len(errors) == 1 and errors[0].startswith(f"{job_cid or '-'} | api")
