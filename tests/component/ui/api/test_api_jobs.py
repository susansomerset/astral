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
    def test_list_in_review_view(self, jobs_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = jobs_client.get("/api/jobs?view=in_review", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_in_review_filters_score_floor(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"astral_job_id": "job-1", "job_data": {}}, {"astral_job_id": "job-2", "job_data": {}}]
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kwargs: rows)
        monkeypatch.setattr(jobs_mod, "score_floor_by_trigger_for_candidate", lambda candidate_id: {"NEW": 5.0})
        monkeypatch.setattr(jobs_mod, "job_misses_dispatch_score_floor", lambda row, floors: row["astral_job_id"] == "job-2")
        resp = jobs_client.get("/api/jobs?view=in_review&candidate_id=cand-1", headers=auth_headers)
        assert resp.get_json() == [{"astral_job_id": "job-1", "job_data": {}}]

    def test_list_in_review_without_score_floors(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"astral_job_id": "job-1", "job_data": {}}]
        monkeypatch.setattr(jobs_mod, "list_jobs", lambda **kwargs: rows)
        monkeypatch.setattr(jobs_mod, "score_floor_by_trigger_for_candidate", lambda candidate_id: {})
        resp = jobs_client.get("/api/jobs?view=in_review&candidate_id=cand-1", headers=auth_headers)
        assert resp.get_json() == rows

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

    def test_list_recommended_and_default(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict[str, object] = {}

        def _list_jobs(**kwargs: object) -> list[dict[str, object]]:
            captured.update(kwargs)
            return [{"astral_job_id": "job-1", "job_data": {"joblist_score": 1}}]

        monkeypatch.setattr(jobs_mod, "list_jobs", _list_jobs)
        recommended = jobs_client.get("/api/jobs?view=recommended", headers=auth_headers)
        assert recommended.get_json()[0]["latest_score"] == 1
        states = captured.get("states") or []
        assert "RECOMMENDED" in states
        assert cfg.BUILD_ARTIFACTS_BASE_STATE in states
        other = jobs_client.get("/api/jobs?view=applied", headers=auth_headers)
        assert other.get_json() == []

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
        resp = jobs_client.get("/api/jobs/job-1", headers=auth_headers)
        assert resp.get_json()["agent_story"][0]["task_key"] == "x"

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
            lambda art, debug=False: art or {},
        )
        resp = jobs_client.get("/api/jobs/job-1274", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["astral_job_id"] == "job-1274"
        assert body["agent_story"] == []

    def test_skip_job_updates_state(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "CANDIDATE_REVIEW", "state_history": []})
        transition = MagicMock()
        monkeypatch.setattr(jobs_mod, "transition_job_state", transition)
        resp = jobs_client.post("/api/jobs/job-1/skip", headers=auth_headers)
        assert resp.status_code == 200
        transition.assert_called_once_with(["job-1"], "CANDIDATE_SKIPPED")

    def test_skip_job_missing_returns_404(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: None)
        resp = jobs_client.post("/api/jobs/job-1/skip", headers=auth_headers)
        assert resp.status_code == 404

    def test_skip_job_invalid_transition_returns_409(self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(jobs_mod, "get_job", lambda job_id: {"astral_job_id": job_id, "state": "NEW"})
        monkeypatch.setattr(
            jobs_mod,
            "transition_job_state",
            MagicMock(side_effect=ValueError("Invalid transition: NEW -> CANDIDATE_SKIPPED")),
        )
        resp = jobs_client.post("/api/jobs/job-1/skip", headers=auth_headers)
        assert resp.status_code == 409
        assert "Invalid transition" in resp.get_json()["error"]

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
        captured: list[tuple[str, dict[str, str]]] = []
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"artifacts": {}}},
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_artifact_cover_letter",
            lambda job_id, content: captured.append((job_id, content)),
        )
        resp = jobs_client.put(
            "/api/jobs/job-565/artifacts/cover_letter",
            json={"cover_letter": {"Subject": "Hi", "Letter": "Body"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert captured == [("job-565", {"Subject": "Hi", "Letter": "Body"})]

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

    def test_put_job_resume_writes_resume_content_keeps_pin(
        self, jobs_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1430 / AST-1428: editor save writes the sibling blob, never a dict onto the pin.
        blob: list[tuple[str, dict]] = []
        pin_writes: list[tuple[str, dict]] = []
        monkeypatch.setattr(
            jobs_mod,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "job_data": {"artifacts": {"job_resume": "pin-keep"}},
            },
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_artifact_resume_content",
            lambda job_id, content: blob.append((job_id, content)),
        )
        monkeypatch.setattr(
            jobs_mod,
            "save_job_data",
            lambda job_id, payload: pin_writes.append((job_id, payload)),
        )
        resp = jobs_client.put(
            "/api/jobs/job-1100/artifacts/job_resume",
            json={"job_resume": {"professional_summary": "Edited"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert blob == [("job-1100", {"professional_summary": "Edited"})]
        assert pin_writes == []

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
            lambda state: list(successors or ["NEW", "FAILED_TECHNICAL"]),
        )
        monkeypatch.setattr(
            jobs_mod,
            "hydrate_job_artifacts_for_display",
            lambda art, debug=False: art or {},
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

    def test_put_illegal_transition_409(
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
            MagicMock(side_effect=ValueError("Invalid transition: CANDIDATE_SKIPPED -> PASSED_JD")),
        )
        resp = jobs_client.put(
            "/api/jobs/job-1453",
            json={"state": "PASSED_JD"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert "Invalid transition" in resp.get_json()["error"]

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
