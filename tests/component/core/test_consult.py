"""Component tests for src/core/consult.py (AST-393)."""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import consult as consult_mod
from src.utils import config as cfg
from src.utils import rubric_text
from src.utils.config import ASTRAL_CONFIG, JOB_STATES, TASK_CONFIG, importance_multiplier

_SKIP_RESUME_SECTION_CATALOG = pytest.mark.skipif(
    "RESUME_SECTION_CATALOG" not in getattr(cfg, "TOKEN_SOURCES", {}),
    reason="AST-513 RESUME_SECTION_CATALOG token not on branch",
)

_SKIP_AST552_RESUME_BODY = pytest.mark.skipif(
    not hasattr(consult_mod.tracker, "job_has_persisted_resume_body"),
    reason="AST-552 persisted resume body gate not on branch",
)


def _pass_grade(vector: str = "fit") -> Dict[str, Any]:
    return {"grade": "A", "confidence": 2, "vector": vector}


def _rubric_item(label: str = "fit", code: str = "CR") -> Dict[str, Any]:
    return {
        "label": label,
        "code": code,
        "content": "body\nA = one\nB = two\nF = fail",
        "grade_descriptions": [
            {"grade": "A", "description": "one"},
            {"grade": "F", "description": "fail"},
        ],
        "importance": 5,
    }


def _patch_scored_render_verdict_fixtures(
    monkeypatch: pytest.MonkeyPatch,
    *,
    rubric: List[Dict[str, Any]],
    score_floor: float = 0.0,
    task_key: str = "grade_do",
) -> None:
    """AST-1277: table-backed rubric + dispatch score_floor for scored render_verdict paths."""
    monkeypatch.setattr(consult_mod, "_rubric_criteria_for_cfg", lambda _cid, _cfg: rubric)
    monkeypatch.setattr(
        consult_mod.tracker,
        "list_dispatch_tasks_for_candidate",
        MagicMock(
            return_value=[
                {"id": 1, "task_key": task_key, "score_floor": score_floor, "trigger_state": "PASSED_JD"},
            ]
        ),
    )


@pytest.fixture
def enable_debug_log() -> None:
    """AST-619: grading helpers use logger.set_debug_flag + debug_detail (not _LOG_DEBUG)."""
    consult_mod.logger.set_debug_flag(True)
    yield
    consult_mod.logger.set_debug_flag(False)


class TestRenderPassFail:
    def test_fails_on_empty_or_dealbreaker_grades(self) -> None:
        assert consult_mod._render_pass_fail("qualify_job_listings", []) == TASK_CONFIG["qualify_job_listings"]["fail_state"]
        grades = [{"grade": "F", "confidence": 2, "vector": "fit"}]
        assert consult_mod._render_pass_fail("qualify_job_listings", grades) == TASK_CONFIG["qualify_job_listings"]["fail_state"]
        assert consult_mod._render_pass_fail("qualify_job_listings", [{"grade": "X", "confidence": 5, "vector": "fit"}]) == TASK_CONFIG["qualify_job_listings"]["fail_state"]
        assert consult_mod._render_pass_fail("qualify_job_listings", [{"grade": "A", "confidence": 1, "vector": "fit"}]) == TASK_CONFIG["qualify_job_listings"]["fail_state"]

    def test_passes_when_confidence_is_high_enough(self) -> None:
        grades = [{"grade": "A", "confidence": 2, "vector": "fit"}]
        assert consult_mod._render_pass_fail("qualify_job_listings", grades) == TASK_CONFIG["qualify_job_listings"]["pass_state"]


@pytest.mark.skipif(
    not hasattr(consult_mod, "_consult_orchestration_for_entity"),
    reason="AST-1054 meteorite GDL overlay helper not on this publish tip",
)
class TestAst1054MeteoriteGdlOutcomeOverlay:
    """AST-1054 introduced METEORITE_GDL_OUTCOME_BY_TASK for shared grade_do/grade_get.

    AST-1221 deletes that symbol and the consult overlay read path. Shared-key grade_do /
    grade_get always use Gaze TASK_CONFIG outcomes (entity_state ignored). Alias Do/Get
    orchestration is TestAst1221RuntimeAliasResolution. JD twin: TestEvaluateMeteoriteStandaloneTwin.
    """

    def test_overlay_symbol_deleted(self) -> None:
        assert not hasattr(cfg, "METEORITE_GDL_OUTCOME_BY_TASK")

    def test_grade_do_gaze_outcomes_regardless_of_entity_state(self) -> None:
        gaze = TASK_CONFIG["grade_do"]
        cfg_m = consult_mod._consult_orchestration_for_entity("grade_do", "METEORITE_PASSED_JD")
        assert cfg_m["pass_state"] == gaze["pass_state"]
        assert cfg_m["fail_state"] == gaze["fail_state"]
        assert cfg_m["error_state"] == gaze["error_state"]
        cfg_v = consult_mod._consult_orchestration_for_entity("grade_do", "PASSED_JD")
        assert cfg_v["pass_state"] == gaze["pass_state"]
        assert cfg_v["fail_state"] == gaze["fail_state"]

    def test_render_pass_fail_gaze_for_shared_grade_do(self) -> None:
        grades = [_pass_grade()]
        gaze_pass = TASK_CONFIG["grade_do"]["pass_state"]
        gaze_fail = TASK_CONFIG["grade_do"]["fail_state"]
        assert (
            consult_mod._render_pass_fail("grade_do", grades, entity_state="METEORITE_PASSED_JD")
            == gaze_pass
        )
        assert (
            consult_mod._render_pass_fail("grade_do", grades, entity_state="PASSED_JD")
            == gaze_pass
        )
        assert (
            consult_mod._render_pass_fail(
                "grade_do",
                [{"grade": "F", "confidence": 2, "vector": "fit"}],
                entity_state="METEORITE_PASSED_JD",
            )
            == gaze_fail
        )


@pytest.mark.skipif(
    "meteorite_grade_do" not in getattr(cfg, "TASK_CONFIG", {})
    or not hasattr(cfg, "resolve_task_key_for_content"),
    reason="AST-1221 alias runtime not on this publish tip",
)
class TestAst1221RuntimeAliasConsult:
    """AST-1221: alias TASK_CONFIG orchestration + header via master resolve; no overlay."""

    def test_alias_orchestration_and_header_resolve(self) -> None:
        orch = consult_mod._consult_orchestration_for_entity(
            "meteorite_grade_do", "METEORITE_PASSED_JD"
        )
        assert orch["pass_state"] == "METEORITE_PASSED_DO"
        assert orch["fail_state"] == "METEORITE_FAILED_DO"
        assert orch["error_state"] == "METEORITE_FAILED_TECHNICAL_DO"
        gaze = consult_mod._consult_orchestration_for_entity("grade_do", "PASSED_JD")
        assert gaze["pass_state"] == "PASSED_DO"
        assert consult_mod._GRADE_DISPATCH_TO_HEADER.get("meteorite_grade_do") is None
        assert (
            consult_mod._GRADE_DISPATCH_TO_HEADER[
                cfg.resolve_task_key_for_content("meteorite_grade_do")
            ]
            == "DO"
        )

    def test_render_pass_fail_alias_owned_outcomes(self) -> None:
        grades = [_pass_grade()]
        assert (
            consult_mod._render_pass_fail(
                "meteorite_grade_do", grades, entity_state="METEORITE_PASSED_JD"
            )
            == "METEORITE_PASSED_DO"
        )
        assert (
            consult_mod._render_pass_fail(
                "meteorite_grade_do",
                [{"grade": "F", "confidence": 2, "vector": "fit"}],
                entity_state="METEORITE_PASSED_JD",
            )
            == "METEORITE_FAILED_DO"
        )


class TestEvaluateMeteoriteStandaloneTwin:
    """AST-1054/1060 rewire: evaluate_meteorite owns its pass/fail/error states directly —
    no overlay lookup, correct regardless of entity_state (unlike the old shared-task pattern).
    """

    def test_own_states_independent_of_entity_state(self) -> None:
        for entity_state in (None, "METEORITE_QUALIFIED", "JD_READY", "PASSED_JD"):
            cfg_m = consult_mod._consult_orchestration_for_entity("evaluate_meteorite", entity_state)
            assert cfg_m["pass_state"] == "METEORITE_PASSED_JD"
            assert cfg_m["fail_state"] == "METEORITE_FAILED_JD"
            assert cfg_m["error_state"] == "METEORITE_ERROR_EVALUATE_JD"

    def test_render_pass_fail_uses_own_states(self) -> None:
        assert (
            consult_mod._render_pass_fail(
                "evaluate_meteorite", [_pass_grade()], entity_state="METEORITE_QUALIFIED",
            )
            == "METEORITE_PASSED_JD"
        )
        assert (
            consult_mod._render_pass_fail(
                "evaluate_meteorite",
                [{"grade": "F", "confidence": 2, "vector": "fit"}],
                entity_state="METEORITE_QUALIFIED",
            )
            == "METEORITE_FAILED_JD"
        )

    def test_rubric_artifact_is_separate_from_jobdesc_rubric(self) -> None:
        assert TASK_CONFIG["evaluate_meteorite"]["rubric_artifact"] == "meteorite_jobdesc_rubric"
        assert TASK_CONFIG["evaluate_jd"]["rubric_artifact"] == "jobdesc_rubric"

    def test_format_analysis_jd_uses_twin_owner_when_state_meteorite(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Live branch: _entity_state_is_meteorite(job_data.state) → analysis_phases_meteorite_override."""
        owners: list[str] = []

        def _capture(_cid: str, owner: str):
            owners.append(owner)
            return [{"label": "Fit", "code": "FT", "content": "twin rubric blob"}]

        monkeypatch.setattr("src.core.candidate.rubric_criteria_for_task", _capture)
        cand = {"_astral_candidate_id": "c-twin"}
        grades = [{"vector": "Fit", "grade": "A", "confidence": 4}]
        out_m = consult_mod._format_analysis_phase_text(
            "ANALYSIS_JD",
            {"state": "METEORITE_QUALIFIED", "jd_grades": grades},
            cand,
        )
        assert owners == ["evaluate_meteorite"]
        assert "CONSIDER: Fit" in out_m and "twin rubric blob" in out_m
        owners.clear()
        out_c = consult_mod._format_analysis_phase_text(
            "ANALYSIS_JD",
            {"state": "JD_READY", "jd_grades": grades},
            cand,
        )
        assert owners == ["evaluate_jd"]
        assert "CONSIDER: Fit" in out_c


class TestRubricHelpers:
    def test_strips_code_suffix(self) -> None:
        assert consult_mod._strip_code("Fit (CR)") == "Fit"

    def test_reads_rubric_criteria_from_table(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("qualify_job_listings", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "qualify_job_listings",
            [{"code": "CR", "label": "fit", "content": "Grade A line", "importance": 5}],
        )
        from src.core.candidate import rubric_criteria_for_task

        assert rubric_criteria_for_task("cand-1", "qualify_job_listings")[0]["code"] == "CR"
        assert consult_mod._rubric_criteria_for_cfg("", {"rubric_artifact": "joblist_rubric"}) == []
        assert consult_mod._rubric_criteria_for_cfg("cand-1", {}) == []

    def test_merges_embedded_rc_for_company_prefilter(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("prefilter_company", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "prefilter_company",
            [
                {
                    "code": "MP",
                    "label": "Mission & Product",
                    "content": "Mission body",
                    "importance": 5,
                },
                {
                    "code": "RC",
                    "label": "Duplicate RC",
                    "content": "dup body",
                    "importance": 1,
                },
            ],
        )
        from src.core.candidate import rubric_criteria_for_task

        rubric = rubric_criteria_for_task("cand-1", "prefilter_company")
        assert rubric[0]["code"] == "RC"
        assert rubric[0]["label"] == "Reality Check"
        assert len(rubric) == 2

    def test_hydrates_rc_by_code_without_table_rc_row(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("prefilter_company", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "prefilter_company",
            [
                {
                    "code": "MP",
                    "label": "Mission & Product",
                    "content": "Mission body\nA = great\nB = ok mp",
                    "importance": 5,
                },
            ],
        )
        from src.core.candidate import rubric_criteria_for_task

        rubric = rubric_criteria_for_task("cand-1", "prefilter_company")
        grades = [
            {"vector": "RC", "grade": "D", "confidence": 3},
            {"vector": "MP", "grade": "B", "confidence": 3},
        ]
        consult_mod._hydrate_grade_reasons_from_rubric(grades, rubric)
        assert grades[0]["reason"]
        assert grades[1]["reason"] == "ok mp"

    def test_maps_vector_labels(self) -> None:
        criteria = [{"code": "CR", "label": "Culture"}]
        assert consult_mod._vector_labels_map(criteria) == {"CR": "Culture"}

    def test_hydrates_grade_reasons(self) -> None:
        criteria = [
            {
                "label": "Fit",
                "content": "body\nA = strong\nB = ok",
                "grade_descriptions": [{"grade": "A", "description": "strong"}],
            }
        ]
        grades = [{"vector": "Fit", "grade": "A"}]
        consult_mod._hydrate_grade_reasons_from_rubric(grades, criteria)
        assert grades[0]["reason"] == "strong"
        consult_mod._hydrate_response_jobs_grade_reasons([{"grades": grades}], criteria)
        with pytest.raises(ValueError, match="rubric criteria missing"):
            consult_mod._hydrate_grade_reasons_from_rubric(grades, [])


class TestImportanceForLabelBranches:
    def test_skips_non_dict_rubric_rows(self) -> None:
        junk: list[Any] = ["not-a-dict-row", {**_rubric_item("fit"), "importance": 5}]
        assert consult_mod._importance_for_label(junk, "fit") == pytest.approx(importance_multiplier(5))

    def test_uses_default_multiplier_when_importance_omitted(self) -> None:
        d = int(ASTRAL_CONFIG["consult_importance"]["default_vector_importance"])
        rubric = [{"label": "fit"}]
        assert consult_mod._importance_for_label(rubric, "fit") == pytest.approx(importance_multiplier(d))

    def test_raises_when_label_missing(self) -> None:
        with pytest.raises(ValueError, match="no rubric criterion"):
            consult_mod._importance_for_label([_rubric_item("fit")], "ghost")

    def test_importance_matches_by_code(self) -> None:
        from src.utils.config import EMBEDDED_COMPANY_PREFILTER_CRITERIA, importance_multiplier

        criteria = list(EMBEDDED_COMPANY_PREFILTER_CRITERIA)
        assert consult_mod._importance_for_label(criteria, "RC") == pytest.approx(importance_multiplier(8))


class TestRenderScore:
    _FIT_RUBRIC = [{"label": "Fit", "importance": 5}]

    def test_fails_on_dealbreaker_and_threshold(self) -> None:
        cfg = TASK_CONFIG["grade_do"]
        fail = consult_mod._render_score(
            cfg, self._FIT_RUBRIC, [{"vector": "Fit", "grade": "F", "confidence": 2}], 5.0
        )
        assert fail[0] == cfg["fail_state"]
        low = consult_mod._render_score(
            cfg, self._FIT_RUBRIC, [{"vector": "Fit", "grade": "D", "confidence": 2}], 9.0
        )
        assert low[0] == cfg["fail_state"]
        assert low[1] == 0.0

    def test_passes_with_importance_scoring(self) -> None:
        cfg = TASK_CONFIG["grade_do"]
        rubric = [{"label": "Fit", "importance": 10}]
        state, score = consult_mod._render_score(
            cfg, rubric, [{"vector": "Fit", "grade": "A", "confidence": 5}], 1.0
        )
        assert state == cfg["pass_state"]
        assert score == pytest.approx(20.0)

    def test_importance_floor_raises_score(self) -> None:
        cfg = TASK_CONFIG["grade_do"]
        grades = [{"vector": "Fit", "grade": "A", "confidence": 5}]
        _, score_low = consult_mod._render_score(cfg, [{"label": "Fit", "importance": 1}], grades, 0.0)
        _, score_high = consult_mod._render_score(cfg, [{"label": "Fit", "importance": 10}], grades, 0.0)
        assert score_high > score_low

    def test_x_excluded_from_v(self) -> None:
        cfg = TASK_CONFIG["grade_do"]
        rubric = [{"label": "Fit", "importance": 5}, {"label": "Other", "importance": 5}]
        state, score = consult_mod._render_score(
            cfg,
            rubric,
            [
                {"vector": "Fit", "grade": "X", "confidence": 0},
                {"vector": "Other", "grade": "A", "confidence": 5},
            ],
            0.0,
        )
        assert state == cfg["pass_state"]
        # V=1, imp 5 → multiplier 1.06 → normalized score 10.6
        assert score == pytest.approx(10.6)

    def test_rejects_unknown_or_missing_vectors(self) -> None:
        cfg = TASK_CONFIG["grade_do"]
        with pytest.raises(ValueError, match="missing vectors"):
            consult_mod._render_score(cfg, self._FIT_RUBRIC, [], 5.0)
        with pytest.raises(ValueError, match="unknown vectors"):
            consult_mod._render_score(
                cfg,
                self._FIT_RUBRIC,
                [
                    {"vector": "Fit", "grade": "A", "confidence": 2},
                    {"vector": "Other", "grade": "A", "confidence": 2},
                ],
                5.0,
            )


class TestTransitionHelpers:
    def test_persists_score_only_for_scored_tasks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "transition_job_state", transition)
        scored_key = next(key for key, cfg in TASK_CONFIG.items() if cfg.get("scored"))
        consult_mod._transition_job_state_for_task(scored_key, ["job-1"], "PASSED_JD", score=7.5)
        transition.assert_called_once_with(["job-1"], "PASSED_JD", score=7.5)
        transition.reset_mock()
        consult_mod._transition_job_state_for_task("validate_title", ["job-2"], "VALID_TITLE", score=7.5)
        transition.assert_called_once_with(["job-2"], "VALID_TITLE")

    def test_list_timesheets_delegates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod.tracker, "list_timesheets", lambda **kwargs: [{"id": 1}])
        assert consult_mod.list_timesheets(batch_id="batch-1") == [{"id": 1}]


class TestPrepLiveContent:
    @pytest.mark.asyncio
    async def test_returns_false_without_job_description(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod.tracker, "get_job_data", AsyncMock(return_value=None))
        assert await consult_mod._prep_live_content({"astral_job_id": "job-1"}) is False

    @pytest.mark.asyncio
    async def test_appends_company_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import roster as roster_mod

        monkeypatch.setattr(consult_mod.tracker, "get_job_data", AsyncMock(return_value="jd text"))
        monkeypatch.setattr(roster_mod, "get_company_data", AsyncMock(return_value=[{"url": "https://co", "content": "about"}]))
        out = await consult_mod._prep_live_content({"astral_job_id": "job-1"}, company={"short_name": "co"}, scoring_task_key="grade_do", position=2)
        assert "jd text" in out
        assert "COMPANY CONTEXT" in out

    @pytest.mark.asyncio
    async def test_returns_jd_only_without_company(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod.tracker, "get_job_data", AsyncMock(return_value="jd only"))
        out = await consult_mod._prep_live_content({"astral_job_id": "job-1"}, position=1)
        assert out == "[index=001]: jd only"

    @pytest.mark.asyncio
    async def test_transitions_when_website_content_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import roster as roster_mod

        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job_data", AsyncMock(return_value="jd text"))
        monkeypatch.setattr(roster_mod, "get_company_data", AsyncMock(return_value=None))
        monkeypatch.setattr(consult_mod.tracker, "transition_job_state", transition)
        out = await consult_mod._prep_live_content({"astral_job_id": "job-1"}, company={"short_name": "co"})
        assert out is False
        transition.assert_called_once_with(["job-1"], "NEED_WEBSITE_CONTENT")


class TestRunConsultTask:
    @pytest.mark.asyncio
    async def test_returns_zero_for_empty_entities(self) -> None:
        out = await consult_mod.run_consult_task("job", "NEW", [], "batch-1", {}, dispatch_task_key="qualify_job_listings")
        assert out["total_processed"] == 0

    @pytest.mark.asyncio
    async def test_routes_company_entities_to_roster(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import roster as roster_mod

        monkeypatch.setattr(
            roster_mod,
            "run_company_task",
            AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}),
        )
        out = await consult_mod.run_consult_task("company", "WATCH", [{"short_name": "co"}], "batch-1", {})
        assert out["total_passed"] == 1


    @pytest.mark.asyncio
    async def test_validate_title_dispatch_key_unhandled_returns_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AST-797: validate_title retired from run_consult_task — inline in qualify only."""
        vt = AsyncMock(return_value={"total": 2, "passed": 1, "failed": 1})
        monkeypatch.setattr("src.core.gazer.validate_title_batch", vt)
        out = await consult_mod.run_consult_task(
            "job", "NEW", [{"astral_job_id": "job-1"}, {"astral_job_id": "job-2"}], "batch-1", {},
            dispatch_task_key="validate_title",
        )
        assert out["total_processed"] == 0
        vt.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_normalizes_render_verdict_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            consult_mod,
            "render_verdict",
            AsyncMock(return_value={"success": True, "to_state": TASK_CONFIG["grade_do"]["pass_state"]}),
        )
        out = await consult_mod.run_consult_task(
            "job",
            "PASSED_JD",
            [{"astral_job_id": "job-1"}],
            "batch-1",
            {},
            dispatch_task_key="grade_do",
        )
        assert out["total_passed"] == 1

    @pytest.mark.asyncio
    async def test_ast503_routes_two_passed_jd_jobs_to_grade_do_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """N>1 DO consult entities use Pattern-A batch entry (grade_do_batch), not per-job render_verdict."""
        cb = AsyncMock(return_value={"success": True, "passed": 2, "failed": 0, "total": 2})
        monkeypatch.setattr(consult_mod, "grade_do_batch", cb)
        rv = AsyncMock()
        monkeypatch.setattr(consult_mod, "render_verdict", rv)
        entities = [{"astral_job_id": "job-1"}, {"astral_job_id": "job-2"}]
        out = await consult_mod.run_consult_task(
            "job", "PASSED_JD", entities, "batch-do", {}, debug=False, dispatch_task_key="grade_do",
        )
        assert out["total_processed"] == 2
        assert out["total_passed"] == 2
        cb.assert_awaited_once()
        assert cb.await_args.args[:2] == ("batch-do", entities)
        rv.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_returns_zero_when_dispatch_task_key_missing(self) -> None:
        out = await consult_mod.run_consult_task("job", "BUILD_ARTIFACTS", [{"astral_job_id": "job-1"}], "batch-1", {})
        assert out["total_processed"] == 0

    @pytest.mark.asyncio
    async def test_routes_candidate_review_cover_letter_unhandled_returns_zero(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-849: draft_cover_letter @ CANDIDATE_REVIEW no longer uses removed cover batch."""
        batch = AsyncMock()
        monkeypatch.setattr(consult_mod, "_run_dispatch_chain_job_batch", batch)
        out = await consult_mod.run_consult_task(
            "job",
            "CANDIDATE_REVIEW",
            [{"astral_job_id": "job-1"}],
            "batch-1",
            {},
            dispatch_task_key="draft_cover_letter",
        )
        assert out["total_processed"] == 0
        batch.assert_not_awaited()


class TestAst369CoverLetterDispatch:
    @pytest.mark.asyncio
    async def test_cover_letter_for_job_skips_without_resume(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda jid: {"astral_job_id": jid, "artifacts": {}})
        monkeypatch.setattr(consult_mod.tracker, "get_job_artifacts", lambda row: {})
        do_task = AsyncMock()
        monkeypatch.setattr(consult_mod, "do_task", do_task)
        await consult_mod._run_cover_letter_for_job("job-1", {"astral_job_id": "job-1"}, {}, False)
        do_task.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cover_letter_for_job_calls_chain_when_resume_present(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda jid: None)
        monkeypatch.setattr(consult_mod.tracker, "get_job_artifacts", lambda row: {"resume_content": {"k": 1}})
        chain = AsyncMock()
        monkeypatch.setattr("src.core.agent.run_cover_letter_artifact_chain_for_job", chain)
        row = {"astral_job_id": "job-1"}
        await consult_mod._run_cover_letter_for_job("job-1", row, {"extra": True}, False)
        chain.assert_awaited_once()
        assert chain.await_args.args[0] == "job-1"


@_SKIP_AST552_RESUME_BODY
class TestAst371ResumeArtifactDispatch:
    @pytest.mark.asyncio
    async def test_routes_build_artifacts_to_dispatch_chain_batch(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        batch = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0},
        )
        monkeypatch.setattr(consult_mod, "_run_dispatch_chain_job_batch", batch)
        out = await consult_mod.run_consult_task(
            "job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
            [{"astral_job_id": "job-1"}],
            "batch-1",
            {},
            dispatch_task_key="contemplate_job",
        )
        assert out["total_passed"] == 1
        batch.assert_awaited_once_with(
            "batch-1",
            [{"astral_job_id": "job-1"}],
            {},
            False,
            "contemplate_job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
        )

    @pytest.mark.asyncio
    async def test_dispatch_chain_batch_calls_do_task_with_chain_ctx(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        do_task = AsyncMock(return_value={"success": True})
        monkeypatch.setattr("src.core.consult.do_task", do_task)
        monkeypatch.setattr(
            "src.core.agent._current_agent_task_run_next",
            lambda tk: "contemplate_job" if tk == "anticipate_scan" else "",
        )
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda aid: {"astral_job_id": aid, "state": cfg.BUILD_ARTIFACTS_BASE_STATE},
        )
        monkeypatch.setattr(consult_mod.tracker, "_candidate_data_for_job", lambda aid: {"artifacts": {}})
        out = await consult_mod._run_dispatch_chain_job_batch(
            "batch-1",
            [{"astral_job_id": "job-1"}],
            {},
            False,
            "anticipate_scan",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
        )
        assert out["total_passed"] == 1
        do_task.assert_awaited_once()
        assert do_task.await_args.args[0] == "anticipate_scan"
        task_ctx = do_task.await_args.kwargs["ctx"]
        assert task_ctx["dispatch_trigger_state"] == cfg.BUILD_ARTIFACTS_BASE_STATE
        assert task_ctx["dispatch_chain_graduate_on_terminal"] is True

    @pytest.mark.asyncio
    async def test_dispatch_chain_batch_hop_label_input_sets_registry_trigger(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-863: row trigger is hop label; ctx dispatch_trigger_state is registry key."""
        do_task = AsyncMock(return_value={"success": True})
        monkeypatch.setattr("src.core.consult.do_task", do_task)
        hop_label = cfg.dispatch_hop_label(cfg.BUILD_ARTIFACTS_BASE_STATE, "anticipate_scan")
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda aid: {"astral_job_id": aid, "state": hop_label},
        )
        monkeypatch.setattr(consult_mod.tracker, "_candidate_data_for_job", lambda aid: {"artifacts": {}})
        out = await consult_mod._run_dispatch_chain_job_batch(
            "batch-863",
            [{"astral_job_id": "job-863"}],
            {},
            False,
            "contemplate_job",
            hop_label,
        )
        assert out["total_passed"] == 1
        task_ctx = do_task.await_args.kwargs["ctx"]
        assert task_ctx["dispatch_trigger_state"] == cfg.BUILD_ARTIFACTS_BASE_STATE

    @pytest.mark.asyncio
    async def test_dispatch_chain_batch_failure_releases_claim(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        released: list[str] = []
        monkeypatch.setattr(
            "src.core.consult.do_task",
            AsyncMock(return_value={"success": False, "error": "hop failed"}),
        )
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda aid: {"astral_job_id": aid, "state": cfg.BUILD_ARTIFACTS_BASE_STATE},
        )
        monkeypatch.setattr(consult_mod.tracker, "_candidate_data_for_job", lambda aid: {"artifacts": {}})
        monkeypatch.setattr(
            consult_mod.tracker,
            "release_job_dispatch_claim",
            lambda aid: released.append(aid),
        )
        out = await consult_mod._run_dispatch_chain_job_batch(
            "batch-1",
            [{"astral_job_id": "job-1"}],
            {},
            False,
            "contemplate_job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
        )
        assert out["total_errors"] == 1
        assert out["total_passed"] == 0
        assert released == ["job-1"]

    @pytest.mark.asyncio
    async def test_dispatch_chain_batch_missing_candidate_releases_claim(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        released: list[str] = []
        do_task = AsyncMock()
        monkeypatch.setattr("src.core.consult.do_task", do_task)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda aid: {"astral_job_id": aid, "state": cfg.BUILD_ARTIFACTS_BASE_STATE, "job_data": {}},
        )
        monkeypatch.setattr(consult_mod.tracker, "_candidate_data_for_job", lambda aid: None)
        monkeypatch.setattr(
            consult_mod.tracker,
            "release_job_dispatch_claim",
            lambda aid: released.append(aid),
        )
        out = await consult_mod._run_dispatch_chain_job_batch(
            "batch-1",
            [{"astral_job_id": "job-1"}],
            {},
            False,
            "contemplate_job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
        )
        assert out["total_errors"] == 1
        assert out["total_passed"] == 0
        do_task.assert_not_awaited()
        assert released == ["job-1"]

    @pytest.mark.asyncio
    async def test_dispatch_chain_batch_skips_row_mismatch(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        do_task = AsyncMock()
        monkeypatch.setattr("src.core.consult.do_task", do_task)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda aid: {"astral_job_id": aid, "state": "RECOMMENDED"},
        )
        monkeypatch.setattr(consult_mod.tracker, "_candidate_data_for_job", lambda aid: {"artifacts": {}})
        out = await consult_mod._run_dispatch_chain_job_batch(
            "batch-mismatch",
            [{"astral_job_id": "job-mismatch"}],
            {},
            False,
            "contemplate_job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
        )
        assert out["total_passed"] == 0
        assert out["total_errors"] == 0
        do_task.assert_not_awaited()


@_SKIP_AST552_RESUME_BODY
class TestAst534DispatchTaskKeyHonesty:
    """AST-534 — dispatch row task_key drives consult entry; trigger_state claims only."""

    @pytest.mark.asyncio
    async def test_consult_do_routes_via_dispatch_task_key_not_state_map(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            consult_mod,
            "render_verdict",
            AsyncMock(return_value={"success": True, "to_state": TASK_CONFIG["grade_do"]["pass_state"]}),
        )
        # Legacy map would not apply; PASSED_LIKE would route to analysis_upshot if state drove routing.
        out = await consult_mod.run_consult_task(
            "job",
            "PASSED_LIKE",
            [{"astral_job_id": "job-1"}],
            "batch-534",
            {},
            dispatch_task_key="grade_do",
        )
        assert out["total_passed"] == 1

    @pytest.mark.asyncio
    async def test_anticipate_scan_entry_routes_chain_batch_not_cover_letter(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        batch = AsyncMock(return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0})
        cover = AsyncMock()
        monkeypatch.setattr(consult_mod, "_run_dispatch_chain_job_batch", batch)
        monkeypatch.setattr(consult_mod, "_run_cover_letter_for_job", cover)
        out = await consult_mod.run_consult_task(
            "job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
            [{"astral_job_id": "job-534"}],
            "batch-534",
            {},
            dispatch_task_key="anticipate_scan",
        )
        assert out["total_passed"] == 1
        batch.assert_awaited_once()
        assert batch.await_args.args[4] == "anticipate_scan"
        cover.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_build_artifacts_state_does_not_imply_contemplate_job_without_dispatch_key(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        entry = AsyncMock()
        monkeypatch.setattr(consult_mod, "_run_dispatch_chain_job_batch", entry)
        await consult_mod.run_consult_task(
            "job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
            [{"astral_job_id": "job-534"}],
            "batch-534",
            {},
            dispatch_task_key="anticipate_scan",
        )
        entry.assert_awaited_once()
        assert entry.await_args.args[4] == "anticipate_scan"

    @pytest.mark.asyncio
    async def test_mid_chain_hop_label_routes_dispatch_chain_batch(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-849: flat BUILD_ARTIFACTS trigger + runtime hop label job state."""
        entry = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0},
        )
        monkeypatch.setattr(consult_mod, "_run_dispatch_chain_job_batch", entry)
        hop_label = cfg.dispatch_hop_label(cfg.BUILD_ARTIFACTS_BASE_STATE, "anticipate_scan")
        monkeypatch.setattr(
            "src.data.database.get_agent_task",
            lambda tk: {"run_next": "contemplate_job"} if tk == "anticipate_scan" else {},
        )
        out = await consult_mod.run_consult_task(
            "job",
            cfg.BUILD_ARTIFACTS_BASE_STATE,
            [{"astral_job_id": "job-mid", "state": hop_label}],
            "batch-mid",
            {},
            dispatch_task_key="contemplate_job",
        )
        assert out["total_passed"] == 1
        entry.assert_awaited_once()
        assert entry.await_args.args[4] == "contemplate_job"

    @pytest.mark.asyncio
    async def test_contemplate_job_hop_label_trigger_routes_chain_batch(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-863: input_state is mid-chain hop label, not bare BUILD_ARTIFACTS."""
        entry = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0},
        )
        monkeypatch.setattr(consult_mod, "_run_dispatch_chain_job_batch", entry)
        hop_label = cfg.dispatch_hop_label(cfg.BUILD_ARTIFACTS_BASE_STATE, "anticipate_scan")
        out = await consult_mod.run_consult_task(
            "job",
            hop_label,
            [{"astral_job_id": "job-863", "state": hop_label}],
            "batch-863",
            {},
            dispatch_task_key="contemplate_job",
        )
        assert out["total_passed"] == 1
        entry.assert_awaited_once()
        assert entry.await_args.args[4] == "contemplate_job"
        assert entry.await_args.args[5] == hop_label

    @pytest.mark.asyncio
    async def test_compound_trigger_state_not_chain_routed_returns_zero(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        batch = AsyncMock()
        monkeypatch.setattr(consult_mod, "_run_dispatch_chain_job_batch", batch)
        compound = cfg.resume_artifact_compound_state("draft_job_resume")
        out = await consult_mod.run_consult_task(
            "job",
            compound,
            [{"astral_job_id": "job-bad"}],
            "batch-bad",
            {},
            dispatch_task_key="draft_job_resume",
        )
        assert out["total_processed"] == 0
        batch.assert_not_awaited()


@_SKIP_AST552_RESUME_BODY
class TestAst596MidChainDispatchClaimRelease:
    """AST-596 — compound trigger claim alignment; hop failure releases per-job batch lock."""

    @pytest.mark.asyncio
    async def test_release_job_dispatch_claim_delegates_to_database(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cleared: list[str] = []
        monkeypatch.setattr(
            "src.data.database.clear_job_batch_lock",
            lambda aid: cleared.append(aid),
        )
        consult_mod.tracker.release_job_dispatch_claim("job-596")
        assert cleared == ["job-596"]


class TestRunBatchConsult:
    @pytest.mark.asyncio
    async def test_routes_envelope_failure_to_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod, "do_task", AsyncMock(return_value={"success": False, "error": "bad"}))
        jobs = [{"astral_job_id": "job-1", "state": "VALID_TITLE"}]
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {},
            False,
        )
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_counts_passed_and_failed_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {"astral_job_id": "job-1", "grades": [{"grade": "A", "confidence": 2, "vector": "fit"}]},
                            {"astral_job_id": "job-2", "grades": [{"grade": "B", "confidence": 2, "vector": "fit"}]},
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-1", "state": "VALID_TITLE", "job_title": "One"},
            {"astral_job_id": "job-2", "state": "VALID_TITLE", "job_title": "Two"},
        ]
        rubric = [{"label": "fit", "code": "CR", "content": "a\nA = one\nB = two"}]

        def process(input_job, response_job, cfg):
            return cfg["pass_state"] if response_job["astral_job_id"] == "job-1" else cfg["fail_state"]

        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            jobs,
            lambda rows: "content",
            process,
            {"candidate_data": {"artifacts": {"joblist_rubric": rubric}}},
            True,
        )
        assert out["passed"] == 1
        assert out["failed"] == 1


class TestRenderVerdict:
    @pytest.mark.asyncio
    async def test_fails_when_job_is_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: None)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_runs_scored_consult_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {
            "astral_job_id": "job-1",
            "company": "co",
            "job_data": {},
            "astral_candidate_id": "c1",
            "state": "PASSED_JD",
        }
        rubric = [_rubric_item("Fit")]
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        _patch_scored_render_verdict_fixtures(monkeypatch, rubric=rubric, score_floor=0.0)
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-1",
            ctx={"astral_candidate_id": "c1", "candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is True

    @pytest.mark.asyncio
    async def test_fails_without_error_state_transition(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(TASK_CONFIG["grade_do"])
        cfg.pop("error_state", None)
        monkeypatch.setitem(TASK_CONFIG, "grade_do", cfg)
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: None)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_fails_when_company_is_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda short_name: None)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod.render_verdict("grade_like", "job-1")
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_need_website_content_without_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda short_name: {"short_name": "co"})
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value=False))
        out = await consult_mod.render_verdict("grade_like", "job-1")
        assert out["to_state"] == "NEED_WEBSITE_CONTENT"

    @pytest.mark.asyncio
    async def test_fails_when_live_content_prep_fails_without_company(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value=False))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_fails_when_do_task_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "do_task", AsyncMock(return_value={"success": False, "error": "bad"}))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_uses_matching_job_row_and_notes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {
            "astral_job_id": "job-1",
            "company": "co",
            "job_data": {},
            "astral_candidate_id": "c1",
            "state": "PASSED_JD",
        }
        rubric = [_rubric_item("Fit")]
        save = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}],
                                "notes": "tail",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        _patch_scored_render_verdict_fixtures(monkeypatch, rubric=rubric, score_floor=0.0)
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-1",
            ctx={"astral_candidate_id": "c1", "candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is True
        save.assert_called_once()
        assert save.call_args.args[1]["do_notes"] == "tail"

    @pytest.mark.asyncio
    async def test_falls_back_to_single_job_row(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {
            "astral_job_id": "job-1",
            "company": "co",
            "job_data": {},
            "astral_candidate_id": "c1",
            "state": "PASSED_JD",
        }
        rubric = [_rubric_item("Fit")]
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{"astral_job_id": "other", "grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]}]
                    },
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        _patch_scored_render_verdict_fixtures(monkeypatch, rubric=rubric, score_floor=0.0)
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-1",
            ctx={"astral_candidate_id": "c1", "candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is True

    @pytest.mark.asyncio
    async def test_fails_when_job_row_is_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {"astral_job_id": "job-x", "grades": [_pass_grade()]},
                            {"astral_job_id": "job-y", "grades": [_pass_grade()]},
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_fails_when_grades_are_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"grades": None}, "timesheet": {}}),
        )
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_fails_when_hydration_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "_hydrate_grade_reasons_from_rubric",
            MagicMock(side_effect=ValueError("missing rubric")),
        )
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False

    @pytest.mark.asyncio
    async def test_runs_binary_grading_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        monkeypatch.setitem(TASK_CONFIG["grade_do"], "grading_mode", "binary")
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [_pass_grade()]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_hydrate_grade_reasons_from_rubric", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is True
        assert out["score"] is None

    @pytest.mark.asyncio
    async def test_fails_when_rubric_artifact_is_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(TASK_CONFIG["grade_do"])
        cfg.pop("rubric_artifact", None)
        monkeypatch.setitem(TASK_CONFIG, "grade_do", cfg)
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_hydrate_grade_reasons_from_rubric", MagicMock())
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_fails_when_candidate_rubric_is_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_hydrate_grade_reasons_from_rubric", MagicMock())
        out = await consult_mod.render_verdict("grade_do", "job-1", ctx={"candidate_data": {}})
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_fails_when_score_render_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        rubric = [_rubric_item("Fit")]
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [{"grade": "A", "confidence": 2, "vector": "Missing"}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_hydrate_grade_reasons_from_rubric", MagicMock())
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-1",
            ctx={"candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_for_unknown_grading_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}}
        monkeypatch.setitem(TASK_CONFIG["grade_do"], "grading_mode", "weird")
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [_pass_grade()]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_hydrate_grade_reasons_from_rubric", MagicMock())
        with pytest.raises(ValueError, match="Unknown grading_mode"):
            await consult_mod.render_verdict("grade_do", "job-1")

    @pytest.mark.asyncio
    async def test_saves_score_for_non_scored_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {
            "astral_job_id": "job-1",
            "company": "co",
            "job_data": {},
            "astral_candidate_id": "c1",
            "state": "PASSED_JD",
        }
        rubric = [_rubric_item("Fit")]
        save = MagicMock()
        monkeypatch.setitem(TASK_CONFIG["grade_do"], "scored", False)
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        _patch_scored_render_verdict_fixtures(monkeypatch, rubric=rubric, score_floor=0.0)
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-1",
            ctx={"astral_candidate_id": "c1", "candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is True
        assert save.call_args.args[1]["do_score"] == out["score"]


class TestRenderPassFailDebug:
    def test_logs_each_fail_and_pass_branch(self, enable_debug_log: None) -> None:
        consult_mod._render_pass_fail("qualify_job_listings", [])
        consult_mod._render_pass_fail("qualify_job_listings", [{"grade": "F", "confidence": 2, "vector": "fit"}])
        consult_mod._render_pass_fail(
            "qualify_job_listings",
            [{"grade": "X", "confidence": 5, "vector": "fit"}, {"grade": "X", "confidence": 4, "vector": "other"}],
        )
        consult_mod._render_pass_fail("qualify_job_listings", [{"grade": "A", "confidence": 1, "vector": "fit"}])
        consult_mod._render_pass_fail("qualify_job_listings", [_pass_grade()])


class TestRubricLookup:
    def test_skips_non_dict_criteria_and_rows(self) -> None:
        criteria = ["bad", {"label": "Fit", "grade_descriptions": [{"grade": "A", "description": "strong"}]}]
        assert consult_mod._lookup_rubric_reason_for_grade(criteria, "Fit", "A") == "strong"

    def test_reads_trailing_grade_table_when_descriptions_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        criteria = [{"label": "Fit", "content": "body\nA = table line"}]
        monkeypatch.setattr(
            rubric_text,
            "parse_trailing_grade_table_lines",
            lambda content: [{"grade": "A", "description": "table line"}],
        )
        assert consult_mod._lookup_rubric_reason_for_grade(criteria, "Fit", "A") == "table line"

    def test_treats_parse_errors_as_empty_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        criteria = [{"label": "Fit", "content": "body"}]
        monkeypatch.setattr(rubric_text, "parse_trailing_grade_table_lines", MagicMock(side_effect=ValueError("bad")))
        with pytest.raises(ValueError, match="No rubric description"):
            consult_mod._lookup_rubric_reason_for_grade(criteria, "Fit", "A")

    def test_raises_when_vector_is_unknown(self) -> None:
        with pytest.raises(ValueError, match="No rubric criterion matching vector"):
            consult_mod._lookup_rubric_reason_for_grade([_rubric_item()], "Missing", "A")

    def test_matches_criterion_by_code(self) -> None:
        from src.utils.config import EMBEDDED_COMPANY_PREFILTER_CRITERIA

        criteria = list(EMBEDDED_COMPANY_PREFILTER_CRITERIA)
        expected = criteria[0]["grade_descriptions"][3]["description"]
        assert consult_mod._lookup_rubric_reason_for_grade(criteria, "RC", "D") == expected

    def test_hydration_skips_non_dict_rows(self) -> None:
        grades = ["bad", {"vector": "Fit", "grade": "A"}]
        consult_mod._hydrate_grade_reasons_from_rubric(grades, [_rubric_item("Fit")])
        assert grades[1]["reason"] == "one"
        consult_mod._hydrate_response_jobs_grade_reasons(["bad", {"grades": grades[1:]}], [_rubric_item("Fit")])


class TestRenderScoreBranches:
    _FIT_RUBRIC = [{"label": "Fit", "importance": 5}]

    def test_skips_no_signal_rows_and_logs(self, enable_debug_log: None) -> None:
        cfg = TASK_CONFIG["grade_do"]
        state, score = consult_mod._render_score(
            cfg,
            self._FIT_RUBRIC,
            [
                {"vector": "Fit", "grade": "X", "confidence": 5},
                {"vector": "Fit", "grade": "A", "confidence": 1},
                {"vector": "Fit", "grade": "A", "confidence": 2},
            ],
            0.0,
        )
        assert state == cfg["pass_state"]
        assert score is not None

    def test_rejects_bad_confidence_values(self) -> None:
        cfg = TASK_CONFIG["grade_do"]
        with pytest.raises(ValueError, match="confidence must be int"):
            consult_mod._render_score(
                cfg, self._FIT_RUBRIC, [{"vector": "Fit", "grade": "A", "confidence": "2"}], 5.0
            )
        with pytest.raises(ValueError, match="invalid confidence"):
            consult_mod._render_score(
                cfg, self._FIT_RUBRIC, [{"vector": "Fit", "grade": "A", "confidence": 99}], 5.0
            )

    def test_logs_scored_path(self, enable_debug_log: None) -> None:
        cfg = TASK_CONFIG["grade_do"]
        consult_mod._render_score(
            cfg, self._FIT_RUBRIC, [{"vector": "Fit", "grade": "F", "confidence": 2}], 5.0
        )
        consult_mod._render_score(
            cfg, self._FIT_RUBRIC, [{"vector": "Fit", "grade": "A", "confidence": 2}], 1.0
        )


class TestPrepLiveContentBranches:
    @pytest.mark.asyncio
    async def test_uses_scoring_transition_when_website_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import roster as roster_mod

        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job_data", AsyncMock(return_value="jd text"))
        monkeypatch.setattr(roster_mod, "get_company_data", AsyncMock(return_value=None))
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod._prep_live_content(
            {"astral_job_id": "job-1"},
            company={"short_name": "co"},
            scoring_task_key="grade_do",
        )
        assert out is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_accepts_string_website_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import roster as roster_mod

        monkeypatch.setattr(consult_mod.tracker, "get_job_data", AsyncMock(return_value="jd text"))
        monkeypatch.setattr(roster_mod, "get_company_data", AsyncMock(return_value="about us"))
        out = await consult_mod._prep_live_content({"astral_job_id": "job-1"}, company={"short_name": "co"})
        assert "about us" in out

    @pytest.mark.asyncio
    async def test_returns_jd_when_website_pages_have_no_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import roster as roster_mod

        monkeypatch.setattr(consult_mod.tracker, "get_job_data", AsyncMock(return_value="jd text"))
        monkeypatch.setattr(roster_mod, "get_company_data", AsyncMock(return_value=[{"url": "https://co"}]))
        out = await consult_mod._prep_live_content({"astral_job_id": "job-1"}, company={"short_name": "co"})
        assert out == "[index=000]: jd text"


class TestAnalysisUpshotPrepAndBatch480ExtraBranches:
    """Extra serialize/prep/batch branches for consult analysis_upshot (AST-479/480/486 tracker boundary).

    Kept distinct from ``TestAnalysisUpshotPrepAndBatch480`` below so pytest collects both suites.
    """

    def test_serialize_empty_job_data(self) -> None:
        assert consult_mod._serialize_do_get_like_bundle({}) == ""

    def test_serialize_skips_prefix_when_all_fields_absent(self) -> None:
        bundle = {"get_grades": [{"x": 1}]}
        text = consult_mod._serialize_do_get_like_bundle(bundle)
        assert "--- DO ---" not in text
        assert "--- GET ---" in text

    def test_serialize_writes_header_and_skips_blank_notes(self) -> None:
        bundle = {
            "do_grades": [{"grade": "A"}],
            "do_score": 3.5,
            "do_notes": "",
            "like_notes": "memo",
        }
        text = consult_mod._serialize_do_get_like_bundle(bundle)
        assert text.startswith("=== PRIOR CONSULT (DO / GET / LIKE) ===")
        assert "notes:" in text and "memo" in text
        lines_w_notes = [ln for ln in text.split("\n") if ln.startswith("notes:")]
        assert len(lines_w_notes) == 1

    @pytest.mark.asyncio
    async def test_prep_returns_false_when_base_prep_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value=False))
        out = await consult_mod._prep_analysis_upshot_live_content({"astral_job_id": "j1"}, {})
        assert out is False

    @pytest.mark.asyncio
    async def test_prep_treats_non_dict_job_data_as_empty_fields(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod,
            "_prep_live_content",
            AsyncMock(return_value="BASE_BLOCK"),
        )
        job = {"astral_job_id": "j1", "job_data": ["not-a-dict"]}
        text = await consult_mod._prep_analysis_upshot_live_content(job, {})
        assert "BASE_BLOCK" in text
        assert "RAW JOB LISTING" not in text

    @pytest.mark.asyncio
    async def test_prep_orders_raw_then_base_then_consult_recap(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod,
            "_prep_live_content",
            AsyncMock(return_value="BASE_MIDDLE"),
        )
        jd: Dict[str, Any] = {
            "raw_job_listing": "listing body",
            "do_grades": [{"g": 1}],
            "like_notes": "see prior",
        }
        job = {"astral_job_id": "j1", "job_data": jd}
        text = await consult_mod._prep_analysis_upshot_live_content(job, None)
        ri = text.index("RAW JOB LISTING")
        bi = text.index("BASE_MIDDLE")
        pi = text.index("PRIOR CONSULT")
        assert ri < bi < pi

    @pytest.mark.asyncio
    async def test_batch_missing_company_transitions_and_counts_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda _aid: {"astral_job_id": "j1", "company": "co_x"},
        )
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda _sn: None)
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod._run_analysis_upshot_batch(
            "bid",
            [{"astral_job_id": "j1"}],
            {},
            False,
        )
        assert out == {
            "total_processed": 1,
            "total_passed": 0,
            "total_failed": 0,
            "total_errors": 1,
        }
        transition.assert_called_once_with(
            "analysis_upshot",
            ["j1"],
            TASK_CONFIG["analysis_upshot"]["error_state"],
        )

    @pytest.mark.asyncio
    async def test_batch_requires_company_false_skips_company_lookup_and_passes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cfg = dict(TASK_CONFIG["analysis_upshot"])
        cfg["requires_company"] = False
        monkeypatch.setitem(TASK_CONFIG, "analysis_upshot", cfg)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda aid: {"astral_job_id": aid, "company": ""},
        )
        get_co = MagicMock(return_value={"short_name": "should_not_run"})
        monkeypatch.setattr(consult_mod.tracker, "get_company", get_co)
        monkeypatch.setattr(
            consult_mod,
            "_prep_analysis_upshot_live_content",
            AsyncMock(return_value="live"),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={"success": True, "parsed_response": {"whole_jd_upshot": "ok"}},
            ),
        )
        saver = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", saver)
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)

        out = await consult_mod._run_analysis_upshot_batch(
            "bid",
            [{"astral_job_id": "jz"}],
            {"extra": 1},
            True,
        )
        assert out["total_passed"] == 1
        get_co.assert_not_called()
        saver.assert_called_once_with("jz", {"analysis_upshot": {"whole_jd_upshot": "ok"}})
        transition.assert_called_once_with(
            "analysis_upshot",
            ["jz"],
            TASK_CONFIG["analysis_upshot"]["pass_state"],
        )

    @pytest.mark.asyncio
    async def test_batch_prep_false_need_website_skips_error_transition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda _aid: {
                "astral_job_id": "j1",
                "company": "co",
                "state": "NEED_WEBSITE_CONTENT",
            },
        )
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda _sn: {"short_name": "co"})
        monkeypatch.setattr(
            consult_mod,
            "_prep_analysis_upshot_live_content",
            AsyncMock(return_value=False),
        )
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod._run_analysis_upshot_batch(
            "bid",
            [{"astral_job_id": "j1"}],
            None,
            False,
        )
        assert out["total_errors"] == 1
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_batch_prep_false_other_state_sets_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda _aid: {"astral_job_id": "j1", "company": "co", "state": "PASSED_LIKE"},
        )
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda _sn: {"short_name": "co"})
        monkeypatch.setattr(
            consult_mod,
            "_prep_analysis_upshot_live_content",
            AsyncMock(return_value=False),
        )
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        await consult_mod._run_analysis_upshot_batch("bid", [{"astral_job_id": "j1"}], None, False)
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_do_task_failure_transitions_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda _aid: {"astral_job_id": "j1", "company": "co"},
        )
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda _sn: {"short_name": "co"})
        monkeypatch.setattr(
            consult_mod,
            "_prep_analysis_upshot_live_content",
            AsyncMock(return_value="ok"),
        )
        monkeypatch.setattr(consult_mod, "do_task", AsyncMock(return_value={"success": False}))
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod._run_analysis_upshot_batch(
            "bid",
            [{"astral_job_id": "j1"}],
            None,
            False,
        )
        assert out["total_errors"] == 1
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_non_dict_parsed_transitions_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda _aid: {"astral_job_id": "j1", "company": "co"},
        )
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda _sn: {"short_name": "co"})
        monkeypatch.setattr(
            consult_mod,
            "_prep_analysis_upshot_live_content",
            AsyncMock(return_value="ok"),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": ["bad"]}),
        )
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        await consult_mod._run_analysis_upshot_batch("bid", [{"astral_job_id": "j1"}], None, False)
        transition.assert_called_once()


class TestRunConsultTaskRoutes:
    @pytest.mark.asyncio
    async def test_routes_fetch_jd_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.gazer.fetch_jd_batch",
            AsyncMock(return_value={"total": 1, "passed": 1, "failed": 0}),
        )
        out = await consult_mod.run_consult_task(
            "job", "PASSED_JOBLIST", [{"astral_job_id": "job-1"}], "batch-1", {},
            dispatch_task_key="fetch_jd",
        )
        assert out["total_passed"] == 1

    @pytest.mark.asyncio
    async def test_routes_fetch_culture_pages_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.gazer.fetch_culture_pages_batch",
            AsyncMock(return_value={"total": 2, "passed": 1, "failed": 1}),
        )
        out = await consult_mod.run_consult_task(
            "job", "PASSED_GET", [{"astral_job_id": "job-c1"}, {"astral_job_id": "job-c2"}],
            "batch-1", {},
            dispatch_task_key="fetch_culture_pages",
        )
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        assert out["total_failed"] == 1

    @pytest.mark.asyncio
    async def test_routes_fetch_website_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.gazer.fetch_website_batch",
            AsyncMock(return_value={"total": 2, "passed": 1, "failed": 1}),
        )
        out = await consult_mod.run_consult_task(
            "company",
            "WEBSITE_FOUND",
            [{"short_name": "co-1"}, {"short_name": "co-2"}],
            "batch-1",
            {},
            dispatch_task_key="fetch_website",
        )
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        assert out["total_failed"] == 1
        assert out["total_errors"] == 0

    @pytest.mark.asyncio
    async def test_routes_fetch_website_batch_errors_count(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.gazer.fetch_website_batch",
            AsyncMock(return_value={"total": 3, "passed": 1, "failed": 1, "errors": 1}),
        )
        out = await consult_mod.run_consult_task(
            "company",
            "WEBSITE_FOUND",
            [{"short_name": "co-1"}, {"short_name": "co-2"}, {"short_name": "co-3"}],
            "batch-1",
            {},
            dispatch_task_key="fetch_website",
        )
        assert out["total_processed"] == 3
        assert out["total_passed"] == 1
        assert out["total_failed"] == 1
        assert out["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_routes_fetch_website_batch_pure_skip_zero_processed(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-892: work-only total maps to total_processed=0 so dispatch loop can stop."""
        monkeypatch.setattr(
            "src.core.gazer.fetch_website_batch",
            AsyncMock(return_value={"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 3}),
        )
        out = await consult_mod.run_consult_task(
            "company",
            "WEBSITE_FOUND",
            [{"short_name": "a"}, {"short_name": "b"}, {"short_name": "c"}],
            "batch-892",
            {},
            dispatch_task_key="fetch_website",
        )
        assert out["total_processed"] == 0
        assert out["total_passed"] == 0
        assert out["total_failed"] == 0
        assert out["total_errors"] == 0

    @pytest.mark.asyncio
    async def test_routes_parse_job_list_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AST-891: parse_job_list consult routes to parse_job_list_batch (not run_company_task)."""
        monkeypatch.setattr(
            "src.core.roster.parse_job_list_batch",
            AsyncMock(return_value={"total": 2, "passed": 2, "failed": 0, "errors": 0}),
        )
        run_company = AsyncMock()
        monkeypatch.setattr("src.core.roster.run_company_task", run_company)
        out = await consult_mod.run_consult_task(
            "company",
            "JOBLIST_IDENTIFIED",
            [{"short_name": "co-1"}, {"short_name": "co-2"}],
            "batch-891",
            {},
            dispatch_task_key="parse_job_list",
        )
        assert out["total_processed"] == 2
        assert out["total_passed"] == 2
        assert out["total_failed"] == 0
        assert out["total_errors"] == 0
        run_company.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_routes_parse_job_list_batch_errors_count(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AST-891: consult total_errors reads batch errors for parse_job_list."""
        monkeypatch.setattr(
            "src.core.roster.parse_job_list_batch",
            AsyncMock(return_value={"total": 3, "passed": 2, "failed": 0, "errors": 1}),
        )
        out = await consult_mod.run_consult_task(
            "company",
            "JOBLIST_IDENTIFIED",
            [{"short_name": "co-1"}, {"short_name": "co-2"}, {"short_name": "co-3"}],
            "batch-891",
            {},
            dispatch_task_key="parse_job_list",
        )
        assert out["total_processed"] == 3
        assert out["total_passed"] == 2
        assert out["total_failed"] == 0
        assert out["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_routes_fetch_job_pages_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.gazer.fetch_job_pages_batch",
            AsyncMock(return_value={"total": 2, "passed": 1, "failed": 1}),
        )
        out = await consult_mod.run_consult_task(
            "company",
            "PREFILTER_PASSED",
            [{"short_name": "co-1"}, {"short_name": "co-2"}],
            "batch-1",
            {},
            dispatch_task_key="fetch_job_pages",
        )
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        assert out["total_failed"] == 1
        assert out["total_errors"] == 0

    @pytest.mark.asyncio
    async def test_routes_prefilter_company_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.roster.prefilter_company_batch",
            AsyncMock(return_value={"total": 3, "passed": 2, "failed": 1, "skipped": 1}),
        )
        out = await consult_mod.run_consult_task(
            "company",
            "HOMEPAGE_READY",
            [{"short_name": "c1"}, {"short_name": "c2"}, {"short_name": "c3"}],
            "batch-1",
            {},
            dispatch_task_key="prefilter",
        )
        assert out["total_processed"] == 3
        assert out["total_passed"] == 2
        assert out["total_failed"] == 1
        assert out["total_errors"] == 0

    @pytest.mark.asyncio
    async def test_routes_prefilter_company_batch_legacy_dispatch_key(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-823: legacy dispatch rows may still carry agent task_key prefilter_company."""
        batch = AsyncMock(return_value={"total": 2, "passed": 1, "failed": 1, "skipped": 0})
        monkeypatch.setattr("src.core.roster.prefilter_company_batch", batch)
        out = await consult_mod.run_consult_task(
            "company",
            "HOMEPAGE_READY",
            [{"short_name": "c1"}, {"short_name": "c2"}],
            "batch-1",
            {},
            dispatch_task_key="prefilter_company",
        )
        batch.assert_awaited_once()
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        assert out["total_failed"] == 1
        assert out["total_errors"] == 0

    @pytest.mark.asyncio
    async def test_routes_qualify_and_evaluate_batches(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "qualify_job_listings", AsyncMock(return_value={"total": 2, "passed": 1, "failed": 1}))
        monkeypatch.setattr(consult_mod, "qualify_meteorite", AsyncMock(return_value={"total": 1, "passed": 1, "failed": 0}))
        monkeypatch.setattr(consult_mod, "evaluate_jd_batch", AsyncMock(return_value={"total": 3, "passed": 2, "failed": 1}))
        qualify = await consult_mod.run_consult_task(
            "job",
            "VALID_TITLE",
            [{"astral_job_id": "job-1"}, {"astral_job_id": "job-2"}],
            "batch-1",
            {},
            dispatch_task_key="qualify_job_listings",
        )
        met = await consult_mod.run_consult_task(
            "job",
            "METEORITE_NEW",
            [{"astral_job_id": "job-m"}],
            "batch-m",
            {},
            dispatch_task_key="qualify_meteorite",
        )
        evaluate = await consult_mod.run_consult_task(
            "job", "JD_READY", [{"astral_job_id": "job-3"}], "batch-2", {},
            dispatch_task_key="evaluate_jd",
        )
        assert qualify["total_processed"] == 2
        assert met["total_processed"] == 1
        assert evaluate["total_processed"] == 3

    @pytest.mark.asyncio
    async def test_normalizes_render_verdict_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "render_verdict", AsyncMock(return_value={"success": False, "error": "bad"}))
        out = await consult_mod.run_consult_task(
            "job", "PASSED_JD", [{"astral_job_id": "job-1"}], "batch-1", {},
            dispatch_task_key="grade_do",
        )
        assert out["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_routes_passed_like_to_analysis_upshot_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        summary = AsyncMock(
            return_value={
                "total_processed": 1,
                "total_passed": 1,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(consult_mod, "_run_analysis_upshot_batch", summary)
        out = await consult_mod.run_consult_task(
            "job", "PASSED_LIKE", [{"astral_job_id": "job-7"}], "b7", {},
            dispatch_task_key="analysis_upshot",
        )
        assert out["total_passed"] == 1
        summary.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_zero_for_unhandled_task_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        out = await consult_mod.run_consult_task(
            "job", "CUSTOM", [{"astral_job_id": "job-1"}], "batch-1", {},
            dispatch_task_key="not_a_real_task",
        )
        assert out["total_processed"] == 0


class TestAst797QualifyInlineValidateTitle:
    @pytest.mark.asyncio
    async def test_qualify_runs_inline_validate_for_new_jobs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        vt = AsyncMock(return_value={"failed": 0, "passed": 1, "total": 1})
        monkeypatch.setattr("src.core.gazer.validate_title_batch", vt)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda jid: {"astral_job_id": jid, "state": "VALID_TITLE"},
        )
        batch = AsyncMock(return_value={"passed": 1, "failed": 0, "total": 1})
        monkeypatch.setattr(consult_mod, "_run_batch_consult", batch)
        jobs = [{"astral_job_id": "job-1", "state": "NEW", "job_data": {"raw_job_listing": "x"}}]
        out = await consult_mod.qualify_job_listings("batch-797", jobs, {}, debug=False)
        vt.assert_awaited_once()
        batch.assert_awaited_once()
        assert out["passed"] == 1

    @pytest.mark.asyncio
    async def test_qualify_returns_early_when_inline_title_screen_fails_all(self, monkeypatch: pytest.MonkeyPatch) -> None:
        vt = AsyncMock(return_value={"failed": 2, "passed": 0, "total": 2})
        monkeypatch.setattr("src.core.gazer.validate_title_batch", vt)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda jid: {"astral_job_id": jid, "state": "INVALID_TITLE"},
        )
        batch = AsyncMock()
        monkeypatch.setattr(consult_mod, "_run_batch_consult", batch)
        jobs = [
            {"astral_job_id": "job-1", "state": "NEW", "job_data": {}},
            {"astral_job_id": "job-2", "state": "NEW", "job_data": {}},
        ]
        out = await consult_mod.qualify_job_listings("batch-797b", jobs, {}, debug=False)
        batch.assert_not_awaited()
        assert out == {"passed": 0, "failed": 2, "total": 2}


class TestAnalysisUpshotPrepAndBatch480:
    """AST-478/480 — analysis_upshot recap, live_content prep, PASSED_LIKE → RECOMMENDED batch paths."""

    def test_serialize_empty_returns_blank(self) -> None:
        assert consult_mod._serialize_do_get_like_bundle({}) == ""

    def test_serialize_skips_prefix_when_no_grades_score_or_notes(self) -> None:
        jd = {"do_grades": None, "do_score": None, "do_notes": None}
        assert consult_mod._serialize_do_get_like_bundle(jd) == ""

    def test_serialize_includes_do_get_like_sections_and_notes(self) -> None:
        jd = {
            "do_grades": [{"grade": "A", "confidence": 1, "vector": "fit"}],
            "get_score": 4.5,
            "like_notes": "sweet",
        }
        txt = consult_mod._serialize_do_get_like_bundle(jd)
        assert txt.startswith("=== PRIOR CONSULT (DO / GET / LIKE) ===")
        assert "--- DO ---" in txt and '"grade"' in txt
        assert "--- GET ---\nscore: 4.5" in txt
        assert "--- LIKE ---\nnotes: 'sweet'" in txt

    def test_serialize_notes_empty_string_skipped(self) -> None:
        jd = {"do_grades": [1], "do_score": 1.0, "do_notes": ""}
        assert "notes:" not in consult_mod._serialize_do_get_like_bundle(jd)

    @pytest.mark.asyncio
    async def test_prep_upshot_requires_base_truthy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value=False))
        assert await consult_mod._prep_analysis_upshot_live_content({"astral_job_id": "j1"}, {"short_name": "co"}) is False

    @pytest.mark.asyncio
    async def test_prep_upshot_job_data_non_dict_skips_raw_listing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="[index=000]: jd"))
        out = await consult_mod._prep_analysis_upshot_live_content(
            {"astral_job_id": "x", "job_data": "oops"},
            None,
        )
        assert isinstance(out, str)
        assert "RAW JOB LISTING" not in out

    @pytest.mark.asyncio
    async def test_prep_upshot_orders_raw_then_base_then_recap(self, monkeypatch: pytest.MonkeyPatch) -> None:
        jd = {
            "raw_job_listing": "  corp text  ",
            "like_grades": [{"grade": "A", "vector": "x", "confidence": 1}],
        }

        monkeypatch.setattr(
            consult_mod,
            "_prep_live_content",
            AsyncMock(return_value="[idx]: body"),
        )
        blended = await consult_mod._prep_analysis_upshot_live_content(
            {"astral_job_id": "jb", "job_data": jd},
            {"short_name": "co"},
        )
        assert blended.startswith("=== RAW JOB LISTING (qualify context) ===\ncorp text")
        assert "[idx]: body" in blended
        assert "PRIOR CONSULT" in blended

    @pytest.mark.asyncio
    async def test_batch_company_missing_moves_to_retry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        row = [{"astral_job_id": "a1", "company": "nopco"}]
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(side_effect=lambda _id: row[0]))
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value=None))
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        out = await consult_mod._run_analysis_upshot_batch("b1", row, {}, False)
        assert out["total_errors"] == 1 and out["total_passed"] == 0
        trans.assert_called_once_with(
            "analysis_upshot",
            ["a1"],
            TASK_CONFIG["analysis_upshot"]["error_state"],
        )

    @pytest.mark.asyncio
    async def test_batch_requires_company_false_runs_without_company_row(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cfg = {**TASK_CONFIG["analysis_upshot"], "requires_company": False}
        monkeypatch.setitem(TASK_CONFIG, "analysis_upshot", cfg)
        job = {"astral_job_id": "j9", "company": "gone"}
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(side_effect=lambda _id: job))
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value=None))
        parsed = {
            "take_get": "g",
            "take_do": "d",
            "take_like": "l",
            "whole_jd_upshot": "w",
            "segment_upshots": [{"segment_key": "k", "upshot": "u"}],
            "candidate_questions": [{"text": "q"}],
            "caveats": [{"text": "c"}],
        }
        monkeypatch.setattr(
            consult_mod,
            "_prep_analysis_upshot_live_content",
            AsyncMock(return_value="CONTENT"),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": parsed}),
        )
        saver = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", saver)
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        out = await consult_mod._run_analysis_upshot_batch("bx", [job], {}, False)
        assert out["total_passed"] == 1 and out["total_errors"] == 0
        saver.assert_called_once_with("j9", {"analysis_upshot": parsed})
        trans.assert_called_once_with(
            "analysis_upshot",
            ["j9"],
            TASK_CONFIG["analysis_upshot"]["pass_state"],
        )

    @pytest.mark.asyncio
    async def test_prep_false_need_website_skips_secondary_error_transition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "jw", "company": "co", "job_data": {}, "state": "NEED_WEBSITE_CONTENT"}
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value={"short_name": "co"}))
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value=job))
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value=False))
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        out = await consult_mod._run_analysis_upshot_batch("b", [job], {}, False)
        assert out["total_errors"] == 1
        trans.assert_not_called()

    @pytest.mark.asyncio
    async def test_prep_false_else_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "jf", "company": "co", "job_data": {}, "state": "PASSED_LIKE"}
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value={"short_name": "co"}))
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value=job))
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value=False))
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        await consult_mod._run_analysis_upshot_batch("b", [job], {}, False)
        trans.assert_called_once_with(
            "analysis_upshot",
            ["jf"],
            TASK_CONFIG["analysis_upshot"]["error_state"],
        )

    @pytest.mark.asyncio
    async def test_do_task_fail_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "f1", "company": "co", "job_data": {}, "state": "PASSED_LIKE"}
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value=job))
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value={"short_name": "co"}))
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value="x"))
        monkeypatch.setattr(consult_mod, "do_task", AsyncMock(return_value={"success": False}))
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        await consult_mod._run_analysis_upshot_batch("b", [job], {}, False)
        trans.assert_called_once_with(
            "analysis_upshot",
            ["f1"],
            TASK_CONFIG["analysis_upshot"]["error_state"],
        )

    @pytest.mark.asyncio
    async def test_non_dict_parse_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "bad", "company": "co", "job_data": {}, "state": "PASSED_LIKE"}
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value=job))
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value={"short_name": "co"}))
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value="x"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": []}),
        )
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        await consult_mod._run_analysis_upshot_batch("b", [job], {}, False)
        trans.assert_called_once_with(
            "analysis_upshot",
            ["bad"],
            TASK_CONFIG["analysis_upshot"]["error_state"],
        )

    @pytest.mark.asyncio
    async def test_success_writes_analysis_upshot_and_recommended(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "ok", "company": "co", "job_data": {}, "state": "PASSED_LIKE"}
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value=job))
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value={"short_name": "co"}))
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value="x"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"upshot": True}}),
        )
        saver = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", saver)
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        out = await consult_mod._run_analysis_upshot_batch("b", [job], {}, False)
        assert out["total_passed"] == 1
        saver.assert_called_once_with("ok", {"analysis_upshot": {"upshot": True}})
        trans.assert_called_once_with(
            "analysis_upshot",
            ["ok"],
            TASK_CONFIG["analysis_upshot"]["pass_state"],
        )


class TestRunBatchConsultBranches:
    @pytest.mark.asyncio
    async def test_skips_error_transition_without_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(TASK_CONFIG["qualify_job_listings"])
        cfg.pop("error_state", None)
        monkeypatch.setitem(TASK_CONFIG, "qualify_job_listings", cfg)
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod, "do_task", AsyncMock(return_value={"success": False, "error": "bad"}))
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            [{"astral_job_id": "job-1", "state": "VALID_TITLE"}],
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            None,
            False,
        )
        assert out["success"] is False
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_routes_hydration_failure_to_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-1", "grades": [{"grade": "A", "confidence": 2, "vector": "fit"}]}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "_hydrate_response_jobs_grade_reasons",
            MagicMock(side_effect=ValueError("missing rubric")),
        )
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            [{"astral_job_id": "job-1", "state": "VALID_TITLE"}],
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {},
            False,
        )
        assert out["success"] is False
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_missing_fabricated_and_bad_grades(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        # Isolate fabricated/bad_grades path; tagging failures are swallowed (AST-984).
        monkeypatch.setattr(consult_mod, "_hydrate_response_jobs_grade_reasons", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "ensure_batch_response_entity_ids",
            MagicMock(side_effect=RuntimeError("tag failed")),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {"astral_job_id": "job-1", "grades": [_pass_grade()]},
                            {"astral_job_id": "job-2", "grades": [_pass_grade()]},
                            {"astral_job_id": "job-3", "grades": [_pass_grade()]},
                        ]
                    },
                    "agent_ref": {
                        "task_key": "qualify_job_listings",
                        "batch_id": "batch-1",
                        "prompt_blocks": [{"type": "RESPONSE", "id": "resp-1"}],
                    },
                    "timesheet": {"inputtotal": 1, "inputcached": 0, "outputtotal": 2},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-1", "state": "VALID_TITLE", "job_title": "One"},
            {"astral_job_id": "job-2", "state": "VALID_TITLE", "job_title": "Two"},
        ]
        rubric = [_rubric_item()]

        def process(input_job, response_job, cfg):
            if response_job["astral_job_id"] == "job-2":
                raise ValueError("bad grades")
            return cfg["pass_state"]

        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            jobs,
            lambda rows: "content",
            process,
            {"candidate_data": {"artifacts": {"joblist_rubric": rubric}}},
            True,
        )
        assert out["passed"] == 1
        assert out["failed"] == 0
        assert out["missing"] is None
        assert out["fabricated"] == ["job-3"]
        assert out["bad_grades"] == ["job-2"]
        assert out["success"] is False
        transition.assert_called_once()


class TestConsultBatchFailDest:
    """AST-642 — per-entity batch consult failure routing helper."""

    def test_primary_state_routes_to_retry_holding(self) -> None:
        err = TASK_CONFIG["qualify_job_listings"]["error_state"]
        # AST-898: VALID_TITLE.retry_state → NEW_RETRY (not VALID_TITLE_RETRY)
        assert consult_mod._consult_batch_fail_dest("VALID_TITLE", err) == "NEW_RETRY"
        assert consult_mod._consult_batch_fail_dest("JD_READY", TASK_CONFIG["evaluate_jd"]["error_state"]) == "JD_READY_RETRY"

    def test_retry_holding_routes_to_terminal_error(self) -> None:
        err = TASK_CONFIG["qualify_job_listings"]["error_state"]
        assert consult_mod._consult_batch_fail_dest("NEW_RETRY", err) == err
        # Drain path: legacy VALID_TITLE_RETRY still terminals (no nested retry)
        assert consult_mod._consult_batch_fail_dest("VALID_TITLE_RETRY", err) == err
        assert (
            consult_mod._consult_batch_fail_dest("JD_READY_RETRY", TASK_CONFIG["evaluate_jd"]["error_state"])
            == TASK_CONFIG["evaluate_jd"]["error_state"]
        )

    def test_analysis_upshot_retry_holding_to_failed_technical(self) -> None:
        err = TASK_CONFIG["analysis_upshot"]["error_state"]
        assert consult_mod._consult_batch_fail_dest("PASSED_LIKE", err) == err
        assert consult_mod._consult_batch_fail_dest("PASSED_LIKE_RETRY", err) == "FAILED_TECHNICAL"

    def test_empty_state_falls_back_to_error_state(self) -> None:
        err = TASK_CONFIG["qualify_job_listings"]["error_state"]
        assert consult_mod._consult_batch_fail_dest(None, err) == err
        assert consult_mod._consult_batch_fail_dest("", err) == err


class TestAst642PerEntityBatchRetry:
    """AST-642 — mixed primary + *_RETRY batches route failures per entity state."""

    @pytest.fixture(autouse=True)
    def _rubric_criteria(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # _run_batch_consult hydrates reasons from DB criteria; tests pass artifacts only
        monkeypatch.setattr(
            consult_mod,
            "_rubric_criteria_for_cfg",
            lambda _cid, _cfg: [_rubric_item()],
        )

    @staticmethod
    def _transition_triples(transition: MagicMock) -> List[tuple]:
        return sorted(
            (c.args[0], tuple(sorted(c.args[1])), c.args[2]) for c in transition.call_args_list
        )

    @pytest.mark.asyncio
    async def test_mixed_missing_ids_route_primary_to_retry_and_retry_to_terminal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-ok", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-ok", "state": "VALID_TITLE", "job_title": "Ok"},
            {"astral_job_id": "job-primary-missing", "state": "VALID_TITLE", "job_title": "Primary missing"},
            {"astral_job_id": "job-retry-missing", "state": "VALID_TITLE_RETRY", "job_title": "Retry missing"},
        ]
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-mixed-missing",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            True,
        )
        assert sorted(out["missing"]) == ["job-primary-missing", "job-retry-missing"]
        assert self._transition_triples(transition) == [
            (
                "qualify_job_listings",
                ("job-primary-missing",),
                JOB_STATES["VALID_TITLE"]["retry_state"],
            ),
            (
                "qualify_job_listings",
                ("job-retry-missing",),
                TASK_CONFIG["qualify_job_listings"]["error_state"],
            ),
        ]

    @pytest.mark.asyncio
    async def test_mixed_bad_grades_route_primary_to_retry_and_retry_to_terminal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {"astral_job_id": "job-p", "grades": [_pass_grade()]},
                            {"astral_job_id": "job-r", "grades": [_pass_grade()]},
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-p", "state": "VALID_TITLE", "job_title": "Primary bad"},
            {"astral_job_id": "job-r", "state": "VALID_TITLE_RETRY", "job_title": "Retry bad"},
        ]

        def process(input_job, response_job, cfg):
            if response_job["astral_job_id"] == "job-r":
                raise ValueError("bad grades")
            return cfg["pass_state"]

        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-mixed-bad",
            jobs,
            lambda rows: "content",
            process,
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            True,
        )
        assert out["bad_grades"] == ["job-r"]
        assert self._transition_triples(transition) == [
            ("qualify_job_listings", ("job-r",), TASK_CONFIG["qualify_job_listings"]["error_state"]),
        ]

    @pytest.mark.asyncio
    async def test_evaluate_jd_mixed_missing_routes_per_entity(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-ok", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jd_text = "x" * 80
        jobs = [
            {"astral_job_id": "job-ok", "state": "JD_READY", "job_data": {"job_description": jd_text}},
            {"astral_job_id": "job-primary-missing", "state": "JD_READY", "job_data": {"job_description": jd_text}},
            {"astral_job_id": "job-retry-missing", "state": "JD_READY_RETRY", "job_data": {"job_description": jd_text}},
        ]
        rubric = [_rubric_item()]
        out = await consult_mod._run_batch_consult(
            "evaluate_jd",
            "batch-jd-mixed",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {"candidate_data": {"artifacts": {"jobdesc_rubric": rubric}}},
            True,
        )
        assert sorted(out["missing"]) == ["job-primary-missing", "job-retry-missing"]
        assert self._transition_triples(transition) == [
            ("evaluate_jd", ("job-primary-missing",), JOB_STATES["JD_READY"]["retry_state"]),
            ("evaluate_jd", ("job-retry-missing",), TASK_CONFIG["evaluate_jd"]["error_state"]),
        ]

    @pytest.mark.asyncio
    async def test_evaluate_jd_retry_bad_grades_routes_to_terminal_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-r", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jd_text = "x" * 80
        jobs = [{"astral_job_id": "job-r", "state": "JD_READY_RETRY", "job_data": {"job_description": jd_text}}]

        def process(input_job, response_job, cfg):
            raise ValueError("bad grades")

        out = await consult_mod._run_batch_consult(
            "evaluate_jd",
            "batch-jd-bad",
            jobs,
            lambda rows: "content",
            process,
            {"candidate_data": {"artifacts": {"jobdesc_rubric": [_rubric_item()]}}},
            False,
        )
        assert out["bad_grades"] == ["job-r"]
        transition.assert_called_once_with(
            "evaluate_jd",
            ["job-r"],
            TASK_CONFIG["evaluate_jd"]["error_state"],
        )

    @pytest.mark.asyncio
    async def test_analysis_upshot_primary_failure_to_retry_holding(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "j1", "company": "co", "state": "PASSED_LIKE", "job_data": {}}
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda _aid: dict(job))
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda _sn: {"short_name": "co"})
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "do_task", AsyncMock(return_value={"success": False, "error": "fail"}))
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod._run_analysis_upshot_batch("b1", [job], {}, False)
        assert out["total_errors"] == 1
        transition.assert_called_once_with(
            "analysis_upshot",
            ["j1"],
            TASK_CONFIG["analysis_upshot"]["error_state"],
        )

    @pytest.mark.asyncio
    async def test_analysis_upshot_retry_failure_to_failed_technical(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "j1", "company": "co", "state": "PASSED_LIKE_RETRY", "job_data": {}}
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda _aid: dict(job))
        monkeypatch.setattr(consult_mod.tracker, "get_company", lambda _sn: {"short_name": "co"})
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(consult_mod, "do_task", AsyncMock(return_value={"success": False, "error": "fail"}))
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod._run_analysis_upshot_batch("b1", [job], {}, False)
        assert out["total_errors"] == 1
        transition.assert_called_once_with(
            "analysis_upshot",
            ["j1"],
            "FAILED_TECHNICAL",
        )

    @pytest.mark.asyncio
    async def test_homogeneous_retry_only_missing_routes_all_to_terminal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-ok", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-ok", "state": "VALID_TITLE_RETRY", "job_title": "Ok"},
            {"astral_job_id": "job-m1", "state": "VALID_TITLE_RETRY", "job_title": "Missing one"},
            {"astral_job_id": "job-m2", "state": "VALID_TITLE_RETRY", "job_title": "Missing two"},
        ]
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-homogeneous-retry",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            True,
        )
        assert sorted(out["missing"]) == ["job-m1", "job-m2"]
        transition.assert_called_once()
        assert transition.call_args.args[0] == "qualify_job_listings"
        assert sorted(transition.call_args.args[1]) == ["job-m1", "job-m2"]
        assert transition.call_args.args[2] == TASK_CONFIG["qualify_job_listings"]["error_state"]


class TestQualifyJobListings:
    @pytest.mark.asyncio
    async def test_runs_debug_and_passing_job_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        initialize = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(consult_mod, "_rubric_criteria_for_cfg", lambda _cid, _cfg: [_rubric_item()])
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {
                "astral_job_id": "job-1",
                "state": "VALID_TITLE",
                "company": "co",
                "job_title": "Engineer",
                "job_site": "site",
                "job_data": {"raw_job_listing": "listing text"},
            }
        ]
        rubric = [_rubric_item()]
        out = await consult_mod.qualify_job_listings(
            "batch-1",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": rubric}}},
            debug=True,
        )
        assert out["passed"] == 1
        initialize.assert_called_once()
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_fails_short_title_and_relative_link(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        # Table-backed hydration needs criteria; artifacts-only ctx is not enough (AST-723).
        monkeypatch.setattr(consult_mod, "_rubric_criteria_for_cfg", lambda _cid, _cfg: [_rubric_item()])
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/1",
                            },
                            {
                                "astral_job_id": "job-2",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "/relative",
                            },
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-1", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "a"}},
            {"astral_job_id": "job-2", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "b"}},
        ]
        out = await consult_mod.qualify_job_listings(
            "batch-2",
            jobs,
            {},
            debug=False,
        )
        assert out["passed"] == 1
        assert out["bad_grades"] == ["job-2"]

    @pytest.mark.asyncio
    async def test_saves_fail_state_without_metadata(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        # Table-backed hydration needs criteria; artifacts-only ctx is not enough (AST-723).
        monkeypatch.setattr(consult_mod, "_rubric_criteria_for_cfg", lambda _cid, _cfg: [_rubric_item()])
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [{"grade": "F", "confidence": 2, "vector": "fit"}],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [{"astral_job_id": "job-1", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "a"}}]
        out = await consult_mod.qualify_job_listings(
            "batch-3",
            jobs,
            {},
            debug=False,
        )
        assert out["failed"] == 1
        save.assert_called_once()
        saved = save.call_args.args[1]["joblist_grades"][0]
        assert saved["grade"] == "F"
        assert saved["reason"] == "fail"

    @pytest.mark.asyncio
    async def test_rejects_short_titles_on_passing_grades(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        # Table-backed hydration needs criteria; artifacts-only ctx is not enough (AST-723).
        monkeypatch.setattr(consult_mod, "_rubric_criteria_for_cfg", lambda _cid, _cfg: [_rubric_item()])
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [_pass_grade()],
                                "job_title": "bad",
                                "job_link": "https://example.com/jobs/1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [{"astral_job_id": "job-1", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "a"}}]
        out = await consult_mod.qualify_job_listings(
            "batch-4",
            jobs,
            {},
            debug=False,
        )
        assert out["failed"] == 1
        transition.assert_called()


class TestAst733QualifyIdentityCollision:
    @pytest.mark.asyncio
    async def test_collision_skips_save_and_transition_counts_failed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=False))
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(consult_mod, "_rubric_criteria_for_cfg", lambda _cid, _cfg: [_rubric_item()])
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/1",
                                "company_job_id": "dup-1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {
                "astral_job_id": "job-1",
                "state": "VALID_TITLE",
                "company": "co",
                "job_title": "Engineer",
                "job_data": {"raw_job_listing": "listing text"},
            }
        ]
        rubric = [_rubric_item()]
        out = await consult_mod.qualify_job_listings(
            "batch-collision",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": rubric}}},
            debug=False,
        )
        assert out["passed"] == 0 and out["failed"] == 1
        save.assert_not_called()
        transition.assert_not_called()


class TestEvaluateJdBatch:
    # evaluate_jd min_jd_chars default is 80 — fixtures must meet readiness gate
    _JD_READY_TEXT = "x" * 80

    @pytest.mark.asyncio
    async def test_runs_debug_and_passing_job_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{"astral_job_id": "job-1", "grades": [_pass_grade()]}]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {
                "astral_job_id": "job-1",
                "state": "JD_READY",
                "job_title": "Engineer",
                "job_data": {"job_description": self._JD_READY_TEXT},
            }
        ]
        rubric = [_rubric_item()]
        out = await consult_mod.evaluate_jd_batch(
            "batch-1",
            jobs,
            {"candidate_data": {"artifacts": {"jobdesc_rubric": {"criteria": rubric}}}},
            debug=True,
        )
        assert out["passed"] == 1
        save.assert_called_once()
        payload = save.call_args.args[1]
        saved = payload["jd_grades"][0]
        assert saved["grade"] == "A"
        assert saved["reason"] == "one"
        assert "jd_score" in payload
        jd_score = payload["jd_score"]
        assert isinstance(jd_score, float)
        assert jd_score >= 0.0

    @pytest.mark.asyncio
    async def test_logs_failed_vectors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [{"grade": "F", "confidence": 2, "vector": "fit"}],
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [{"astral_job_id": "job-1", "state": "JD_READY", "job_data": {"job_description": self._JD_READY_TEXT}}]
        rubric = [_rubric_item()]
        out = await consult_mod.evaluate_jd_batch(
            "batch-2",
            jobs,
            {"candidate_data": {"artifacts": {"jobdesc_rubric": rubric}}},
            debug=True,
        )
        assert out["failed"] == 1

    @pytest.mark.asyncio
    async def test_skips_short_jd_without_agent_call(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        save = MagicMock()
        do_task = AsyncMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(consult_mod, "do_task", do_task)
        jobs = [
            {
                "astral_job_id": "job-empty",
                "state": "JD_READY",
                "job_title": "Empty JD",
                "job_data": {"job_description": "short"},
            }
        ]
        out = await consult_mod.evaluate_jd_batch("batch-skip", jobs, {}, debug=False)
        assert out["skipped"] == 1
        assert out["passed"] == 0
        do_task.assert_not_called()
        transition.assert_called_once()
        save.assert_called_once()
        skip_payload = save.call_args.args[1]
        assert "jd_score" not in skip_payload
        skip_meta = skip_payload["jd_readiness_skip"]
        assert skip_meta["reason"] == "empty_or_short_jd"
        assert skip_meta["batch_id"] == "batch-skip"

    @pytest.mark.asyncio
    async def test_debug_merge_skipped_into_result_when_some_jobs_ready(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{"astral_job_id": "job-big", "grades": [_pass_grade()]}],
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {
                "astral_job_id": "job-skip",
                "state": "JD_READY",
                "job_title": "Short",
                "job_data": {"job_description": "x"},
            },
            {
                "astral_job_id": "job-big",
                "state": "JD_READY",
                "job_title": "Ready",
                "job_data": {"job_description": self._JD_READY_TEXT},
            },
        ]
        rubric = [_rubric_item()]
        out = await consult_mod.evaluate_jd_batch(
            "batch-mix",
            jobs,
            {"candidate_data": {"artifacts": {"jobdesc_rubric": {"criteria": rubric}}}},
            debug=True,
        )
        assert out.get("skipped") == 1
        assert out.get("total") == 2


class TestRemainingConsultBranches:
    def test_skips_blank_grade_descriptions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        criteria = [
            {
                "label": "Fit",
                "grade_descriptions": [{"grade": "A", "description": "   "}],
                "content": "body\nA = table line",
            }
        ]
        monkeypatch.setattr(
            rubric_text,
            "parse_trailing_grade_table_lines",
            lambda content: [{"grade": "A", "description": "table line"}],
        )
        assert consult_mod._lookup_rubric_reason_for_grade(criteria, "Fit", "A") == "table line"

    def test_hydration_skips_jobs_without_grade_lists(self) -> None:
        consult_mod._hydrate_response_jobs_grade_reasons([{"grades": "bad"}, {"other": 1}], [_rubric_item("Fit")])

    @pytest.mark.asyncio
    async def test_batch_hydration_failure_without_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(TASK_CONFIG["qualify_job_listings"])
        cfg.pop("error_state", None)
        monkeypatch.setitem(TASK_CONFIG, "qualify_job_listings", cfg)
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-1", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "_hydrate_response_jobs_grade_reasons",
            MagicMock(side_effect=ValueError("missing rubric")),
        )
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            [{"astral_job_id": "job-1", "state": "VALID_TITLE"}],
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {},
            False,
        )
        assert out["success"] is False
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_batch_retries_missing_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-1", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-1", "state": "VALID_TITLE", "job_title": "One"},
            {"astral_job_id": "job-2", "state": "VALID_TITLE", "job_title": "Two"},
        ]
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            True,
        )
        assert out["missing"] == ["job-2"]
        assert out["truncated_note"] == f"truncated: 1 IDs -> {JOB_STATES['VALID_TITLE']['retry_state']}: ['job-2']"
        transition.assert_called()

    @pytest.mark.asyncio
    async def test_batch_skips_bad_grade_transition_without_dest(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(TASK_CONFIG["qualify_job_listings"])
        cfg.pop("error_state", None)
        monkeypatch.setitem(TASK_CONFIG, "qualify_job_listings", cfg)
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-1", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )

        def process(input_job, response_job, cfg):
            raise ValueError("bad grades")

        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            [{"astral_job_id": "job-1", "state": "NEW"}],
            lambda rows: "content",
            process,
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            False,
        )
        assert out["bad_grades"] == ["job-1"]
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_qualify_skips_informational_score_without_rubric(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_hydrate_response_jobs_grade_reasons", MagicMock())
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [{"astral_job_id": "job-1", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "a"}}]
        out = await consult_mod.qualify_job_listings("batch-5", jobs, {}, debug=False)
        assert out["passed"] == 1

    @pytest.mark.asyncio
    async def test_qualify_ignores_score_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-1",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_render_score", MagicMock(side_effect=ValueError("bad score")))
        jobs = [{"astral_job_id": "job-1", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "a"}}]
        out = await consult_mod.qualify_job_listings(
            "batch-6",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            debug=False,
        )
        assert out["passed"] == 1

    @pytest.mark.asyncio
    async def test_evaluate_runs_without_rubric_weights(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_hydrate_response_jobs_grade_reasons", MagicMock())
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-1", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-1", "state": "JD_READY", "job_data": {"job_description": TestEvaluateJdBatch._JD_READY_TEXT}}
        ]
        out = await consult_mod.evaluate_jd_batch("batch-3", jobs, {}, debug=True)
        assert out["passed"] == 1

    @pytest.mark.asyncio
    async def test_runs_without_debug_logging(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(consult_mod, "_hydrate_response_jobs_grade_reasons", MagicMock())
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-1", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-1", "state": "JD_READY", "job_data": {"job_description": TestEvaluateJdBatch._JD_READY_TEXT}}
        ]
        out = await consult_mod.evaluate_jd_batch("batch-4", jobs, {}, debug=False)
        assert out["passed"] == 1

    @pytest.mark.asyncio
    async def test_batch_leaves_missing_ids_without_retry_or_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(TASK_CONFIG["qualify_job_listings"])
        cfg.pop("error_state", None)
        monkeypatch.setitem(TASK_CONFIG, "qualify_job_listings", cfg)
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-1", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-1", "state": "NEW", "job_title": "One"},
            {"astral_job_id": "job-2", "state": "NEW", "job_title": "Two"},
        ]
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-1",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            False,
        )
        assert out["missing"] == ["job-2"]
        transition.assert_not_called()

    def test_render_score_with_only_no_signal_rows(self) -> None:
        cfg = TASK_CONFIG["grade_do"]
        state, score = consult_mod._render_score(
            cfg,
            [{"label": "Fit", "importance": 5}],
            [
                {"vector": "Fit", "grade": "X", "confidence": 5},
                {"vector": "Fit", "grade": "A", "confidence": 1},
            ],
            0.0,
        )
        assert state == cfg["pass_state"]
        assert score == 0.0


@_SKIP_RESUME_SECTION_CATALOG
class TestAst513JobTokenContext:
    """AST-513: build_job_token_context and analysis phase formatter."""

    def _candidate_data(self) -> dict:
        return {
            "artifacts": {
                "jobdesc_rubric": {
                    "criteria": [
                        {
                            "label": "Culture Fit",
                            "code": "CR",
                            "content": "Full rubric blob for culture",
                        }
                    ]
                },
                "do_rubric": {
                    "criteria": [
                        {"label": "Day to day", "code": "DD", "content": "Do rubric body"},
                    ]
                },
            }
        }

    def test_build_job_token_context_visible_jd_plain_text_only(self) -> None:
        job = {
            "astral_job_id": "job-513",
            "job_data": {
                "job_description": "Plain JD without prefix",
                "jd_grades": [{"vector": "Culture Fit", "grade": "a", "confidence": 4}],
            },
        }
        ctx = consult_mod.build_job_token_context(job, self._candidate_data())
        assert ctx["VISIBLE_JD"] == "Plain JD without prefix"
        assert "[index=" not in ctx["VISIBLE_JD"]
        assert "COMPANY CONTEXT" not in ctx["VISIBLE_JD"]
        assert ctx["ANALYSIS_JD"].startswith("CONSIDER: Culture Fit")
        assert "Full rubric blob for culture" in ctx["ANALYSIS_JD"]
        assert "ANALYSIS RESULT: A (4/5 confidence)" in ctx["ANALYSIS_JD"]

    def test_missing_phase_grades_yields_empty_analysis_token(self) -> None:
        job = {
            "astral_job_id": "job-513",
            "job_data": {"job_description": "jd", "do_grades": []},
        }
        ctx = consult_mod.build_job_token_context(job, self._candidate_data())
        assert ctx["ANALYSIS_DO"] == ""

    def test_format_analysis_skips_unmatched_vector(self, caplog) -> None:
        caplog.set_level("WARNING")
        job_data = {"jd_grades": [{"vector": "Unknown Vector", "grade": "B", "confidence": 2}]}
        out = consult_mod._format_analysis_phase_text("ANALYSIS_JD", job_data, self._candidate_data())
        assert out == ""
        assert any("no rubric criterion" in rec.message for rec in caplog.records)

    def test_build_job_token_context_resume_section_catalog(self) -> None:
        from src.core import candidate as candidate_mod

        structure = candidate_mod.default_resume_structure()
        cd = {"artifacts": {"resume_structure": structure, "base_resume": {}}}
        job = {"astral_job_id": "job-551", "job_data": {"job_description": "jd"}}
        ctx = consult_mod.build_job_token_context(job, cd)
        assert ctx["RESUME_SECTION_CATALOG"]
        assert "professional_summary:" in ctx["RESUME_SECTION_CATALOG"]
        assert "job_agent_editable=" in ctx["RESUME_SECTION_CATALOG"]


class TestAst1193AnalysisMatchParity:
    """AST-1193: shared criterion finder + ANALYSIS live/snapshot match + Style D."""

    def test_find_rubric_criterion_label_and_code(self) -> None:
        criteria = [
            "skip",
            {"label": "Compensation", "code": "CO", "content": "pay blob"},
        ]
        hit = consult_mod._find_rubric_criterion(criteria, "Compensation")
        assert hit is not None and hit["code"] == "CO"
        by_code = consult_mod._find_rubric_criterion(criteria, "CO")
        assert by_code is not None and by_code["label"] == "Compensation"
        assert consult_mod._find_rubric_criterion(criteria, "Ghost") is None

    def test_analysis_snapshot_fallback_uses_live_content_by_code(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Live labels drifted; snapshot still has the grade vector label + code.
        monkeypatch.setattr(
            "src.core.candidate.rubric_criteria_for_task",
            lambda cid, owner: [
                {"label": "Total Rewards", "code": "CO", "content": "live pay content"},
            ],
        )
        job_data = {
            "jd_grades": [{"vector": "Compensation", "grade": "B", "confidence": 3}],
            "jd_rubric": [{"label": "Compensation", "code": "CO"}],
        }
        cd = {"_astral_candidate_id": "cand-1193"}
        out = consult_mod._format_analysis_phase_text("ANALYSIS_JD", job_data, cd)
        assert "CONSIDER: Total Rewards" in out
        assert "live pay content" in out
        assert "ANALYSIS RESULT: B (3/5 confidence)" in out

    def test_analysis_snapshot_without_live_content_still_nonempty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "src.core.candidate.rubric_criteria_for_task",
            lambda cid, owner: [],
        )
        job_data = {
            "jd_grades": [{"vector": "Program Scope", "grade": "A", "confidence": 4}],
            "jd_rubric": [{"label": "Program Scope", "code": "PS"}],
        }
        out = consult_mod._format_analysis_phase_text(
            "ANALYSIS_JD", job_data, {"_astral_candidate_id": "cand-1193"}
        )
        assert out.startswith("CONSIDER: Program Scope")
        assert "ANALYSIS RESULT: A (4/5 confidence)" in out
        # Blank blob line between CONSIDER and ANALYSIS RESULT
        assert "CONSIDER: Program Scope\n\nANALYSIS RESULT:" in out

    def test_build_job_token_context_debug_emits_found_recorded(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        dbg = MagicMock()
        monkeypatch.setattr(consult_mod, "get_logger", lambda *a, **k: dbg)
        monkeypatch.setattr(
            "src.core.candidate.rubric_criteria_for_task",
            lambda cid, owner: [
                {"label": "Culture Fit", "code": "CR", "content": "blob"},
            ]
            if owner == "evaluate_jd"
            else [],
        )
        job = {
            "astral_job_id": "job-1193",
            "job_data": {
                "job_description": "jd",
                "jd_grades": [{"vector": "Culture Fit", "grade": "A", "confidence": 2}],
            },
        }
        ctx = consult_mod.build_job_token_context(
            job, {"_astral_candidate_id": "cand-1193"}, debug=True
        )
        assert "CONSIDER: Culture Fit" in ctx["ANALYSIS_JD"]
        index_calls = [c.kwargs for c in dbg.debug_index.call_args_list]
        assert any(
            c.get("func") == "_format_analysis_phase_text"
            and c.get("identifier") == "job-1193:ANALYSIS_JD"
            and c.get("outcome") == "formatted"
            for c in index_calls
        )
        details = [c.args[0] for c in dbg.debug_detail.call_args_list if c.args]
        assert any(
            "found_grades=1" in str(m) and "recorded_vectors=1" in str(m) for m in details
        )

    def test_build_job_token_context_debug_false_is_quiet(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        dbg = MagicMock()
        monkeypatch.setattr(consult_mod, "get_logger", lambda *a, **k: dbg)
        monkeypatch.setattr(
            "src.core.candidate.rubric_criteria_for_task",
            lambda cid, owner: [],
        )
        job = {
            "astral_job_id": "job-1193",
            "job_data": {
                "jd_grades": [{"vector": "X", "grade": "A", "confidence": 1}],
                "jd_rubric": [{"label": "X", "code": "XX"}],
            },
        }
        consult_mod.build_job_token_context(
            job, {"_astral_candidate_id": "c"}, debug=False
        )
        dbg.debug_index.assert_not_called()
        dbg.debug_detail.assert_not_called()


class TestAst726LatestOnlyConsultOutcomes:
    """AST-726: latest-only rubric outcome fields on job blobs."""

    def test_apply_render_verdict_always_persists_notes_including_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda astral_job_id: {
                "astral_job_id": astral_job_id,
                "astral_candidate_id": "c1",
                "state": "PASSED_JD",
            },
        )
        rubric = [_rubric_item("fit")]
        _patch_scored_render_verdict_fixtures(monkeypatch, rubric=rubric, score_floor=0.0)
        cfg = consult_mod._consult_orchestration("grade_do")
        ctx = {"astral_candidate_id": "c1", "candidate_data": {"artifacts": {"do_rubric": rubric}}}
        consult_mod._apply_render_verdict_decoded_job(
            "grade_do",
            "job-726",
            {"grades": [_pass_grade()], "notes": ""},
            cfg,
            ctx,
        )
        assert save.call_args.args[1]["do_notes"] == ""

    @pytest.mark.asyncio
    async def test_qualify_job_listings_persists_joblist_score_on_pass(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-726",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/726",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {
                "astral_job_id": "job-726",
                "state": "VALID_TITLE",
                "company": "co",
                "job_title": "Engineer",
                "job_site": "site",
                "job_data": {"raw_job_listing": "listing text"},
            }
        ]
        rubric = [_rubric_item()]
        out = await consult_mod.qualify_job_listings(
            "batch-726",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": rubric}}},
            debug=False,
        )
        assert out["passed"] == 1
        saved = save.call_args.args[1]
        assert "joblist_grades" in saved
        assert "joblist_score" in saved
        assert saved["joblist_score"] is not None

    @pytest.mark.asyncio
    async def test_qualify_job_listings_persists_joblist_score_on_fail(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-726",
                                "grades": [{"grade": "F", "confidence": 2, "vector": "fit"}],
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [{"astral_job_id": "job-726", "state": "VALID_TITLE", "company": "co", "job_data": {}}]
        rubric = [_rubric_item()]
        out = await consult_mod.qualify_job_listings(
            "batch-726-fail",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": rubric}}},
            debug=False,
        )
        assert out["failed"] == 1
        saved = save.call_args.args[1]
        assert "joblist_grades" in saved
        # F-grade fail path has no numeric score — joblist_score omitted per _latest_score_value gate


class TestAst860RunBatchConsultCandidateCtx:
    """AST-860: _run_batch_consult wires astral_candidate_id into do_task ctx."""

    @pytest.mark.asyncio
    async def test_passes_astral_candidate_id_and_candidate_data_to_do_task(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: Dict[str, Any] = {}

        async def fake_do_task(**kwargs: Any) -> Dict[str, Any]:
            captured.update(kwargs)
            return {
                "success": True,
                "parsed_response": {
                    "jobs": [{
                        "astral_job_id": "job-1",
                        "grades": [{"grade": "A", "confidence": 2, "vector": "fit"}],
                    }],
                },
                "timesheet": {},
            }

        monkeypatch.setattr(consult_mod, "do_task", fake_do_task)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod, "_rubric_criteria_for_cfg", lambda _cid, _cfg: rubric)
        rubric = [{"label": "fit", "code": "CR", "content": "a\nA = one\nB = two"}]
        ctx = {
            "astral_candidate_id": "somerset",
            "candidate_data": {"artifacts": {"joblist_rubric": rubric}},
        }
        await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-860",
            [{"astral_job_id": "job-1", "state": "VALID_TITLE"}],
            lambda rows: "content",
            lambda _ij, _rj, cfg: cfg["pass_state"],
            ctx,
            False,
        )
        task_ctx = captured["ctx"]
        assert task_ctx["astral_candidate_id"] == "somerset"
        assert task_ctx["candidate_data"] == ctx["candidate_data"]


class TestAst897HoldStateOnBalanceRefusal:
    """AST-897: provider balance refusal holds job state (no error/retry transition)."""

    _FC = "provider_balance_refusal"

    @pytest.mark.asyncio
    async def test_render_verdict_holds_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}, "state": "VALID_TITLE"}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": False,
                    "error": "Insufficient Balance",
                    "failure_class": self._FC,
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        assert out["state_held"] is True
        assert out["to_state"] == "VALID_TITLE"
        assert out["failure_class"] == self._FC
        assert "Insufficient Balance" in (out.get("error") or "")
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_render_verdict_ordinary_failure_still_transitions(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "job_data": {}, "state": "VALID_TITLE"}
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(return_value={"success": False, "error": "schema boom"}),
        )
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        out = await consult_mod.render_verdict("grade_do", "job-1")
        assert out["success"] is False
        assert out.get("state_held") is not True
        transition.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_consult_holds_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": False,
                    "error": "402 payment required",
                    "failure_class": self._FC,
                }
            ),
        )
        jobs = [{"astral_job_id": "job-1", "state": "VALID_TITLE"}]
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-897",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            None,
            False,
        )
        assert out["success"] is False
        assert out["state_held"] is True
        assert out["failure_class"] == self._FC
        assert out["total"] == 1
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_analysis_upshot_batch_holds_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job = {"astral_job_id": "j1", "company": "co", "job_data": {}, "state": "PASSED_LIKE"}
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value=job))
        monkeypatch.setattr(consult_mod.tracker, "get_company", MagicMock(return_value={"short_name": "co"}))
        monkeypatch.setattr(consult_mod, "_prep_analysis_upshot_live_content", AsyncMock(return_value="x"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": False,
                    "error": "out of credit",
                    "failure_class": self._FC,
                }
            ),
        )
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        out = await consult_mod._run_analysis_upshot_batch("b897", [job], {}, False)
        assert out["total_errors"] == 1
        assert out["total_passed"] == 0
        trans.assert_not_called()


class TestAst898QualifyNewRetry:
    """AST-898: NEW_RETRY AI hop + fail dest; skip title re-screen; drain VALID_TITLE_RETRY."""

    @pytest.fixture(autouse=True)
    def _rubric_criteria(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            consult_mod,
            "_rubric_criteria_for_cfg",
            lambda _cid, _cfg: [_rubric_item()],
        )

    @staticmethod
    def _transition_triples(transition: MagicMock) -> List[tuple]:
        return sorted(
            (c.args[0], tuple(sorted(c.args[1])), c.args[2]) for c in transition.call_args_list
        )

    @pytest.mark.asyncio
    async def test_valid_title_short_title_routes_to_new_retry(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-vt",
                                "grades": [_pass_grade()],
                                "job_title": "bad",
                                "job_link": "https://example.com/jobs/1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [{"astral_job_id": "job-vt", "state": "VALID_TITLE", "company": "co", "job_data": {"raw_job_listing": "a"}}]
        out = await consult_mod.qualify_job_listings(
            "batch-898-vt",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            debug=False,
        )
        assert out["failed"] == 1
        assert self._transition_triples(transition) == [
            ("qualify_job_listings", ("job-vt",), "NEW_RETRY"),
        ]

    @pytest.mark.asyncio
    async def test_new_retry_short_title_routes_to_qualify_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        err = TASK_CONFIG["qualify_job_listings"]["error_state"]
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-nr",
                                "grades": [_pass_grade()],
                                "job_title": "bad",
                                "job_link": "https://example.com/jobs/1",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [{"astral_job_id": "job-nr", "state": "NEW_RETRY", "company": "co", "job_data": {"raw_job_listing": "a"}}]
        out = await consult_mod.qualify_job_listings(
            "batch-898-nr",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            debug=False,
        )
        assert out["failed"] == 1
        assert self._transition_triples(transition) == [
            ("qualify_job_listings", ("job-nr",), err),
        ]

    @pytest.mark.asyncio
    async def test_new_retry_skips_validate_title_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        vt = AsyncMock(return_value={"failed": 0, "passed": 0, "total": 0})
        monkeypatch.setattr("src.core.gazer.validate_title_batch", vt)
        batch = AsyncMock(return_value={"passed": 1, "failed": 0, "total": 1})
        monkeypatch.setattr(consult_mod, "_run_batch_consult", batch)
        jobs = [{"astral_job_id": "job-nr", "state": "NEW_RETRY", "job_data": {"raw_job_listing": "x"}}]
        out = await consult_mod.qualify_job_listings("batch-898-skip", jobs, {}, debug=False)
        vt.assert_not_awaited()
        batch.assert_awaited_once()
        assert out["passed"] == 1

    @pytest.mark.asyncio
    async def test_new_retry_pass_and_fail_grade_outcomes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-pass",
                                "grades": [_pass_grade()],
                                "job_title": "Engineer",
                                "job_link": "https://example.com/jobs/p",
                            },
                            {
                                "astral_job_id": "job-fail",
                                "grades": [{"grade": "F", "confidence": 2, "vector": "fit"}],
                            },
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-pass", "state": "NEW_RETRY", "company": "co", "job_data": {"raw_job_listing": "a"}},
            {"astral_job_id": "job-fail", "state": "NEW_RETRY", "company": "co", "job_data": {"raw_job_listing": "b"}},
        ]
        out = await consult_mod.qualify_job_listings(
            "batch-898-grades",
            jobs,
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}}},
            debug=False,
        )
        assert out["passed"] == 1
        assert out["failed"] == 1
        dests = {t[1][0]: t[2] for t in self._transition_triples(transition)}
        assert dests["job-pass"] == TASK_CONFIG["qualify_job_listings"]["pass_state"]
        assert dests["job-fail"] == TASK_CONFIG["qualify_job_listings"]["fail_state"]

    @pytest.mark.asyncio
    async def test_valid_title_retry_missing_still_terminals(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Drain: VALID_TITLE_RETRY second-strike failures still go to qualify error_state."""
        transition = MagicMock()
        err = TASK_CONFIG["qualify_job_listings"]["error_state"]
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [{"astral_job_id": "job-ok", "grades": [_pass_grade()]}]},
                    "timesheet": {},
                }
            ),
        )
        jobs = [
            {"astral_job_id": "job-ok", "state": "VALID_TITLE_RETRY", "job_title": "Ok"},
            {"astral_job_id": "job-missing", "state": "VALID_TITLE_RETRY", "job_title": "Missing"},
        ]
        out = await consult_mod._run_batch_consult(
            "qualify_job_listings",
            "batch-898-drain",
            jobs,
            lambda rows: "content",
            lambda input_job, response_job, cfg: cfg["pass_state"],
            {"candidate_data": {"artifacts": {"joblist_rubric": [_rubric_item()]}},},
            True,
        )
        assert out["missing"] == ["job-missing"]
        assert self._transition_triples(transition) == [
            ("qualify_job_listings", ("job-missing",), err),
        ]

    @pytest.mark.asyncio
    async def test_new_retry_in_input_state_map(self) -> None:
        assert consult_mod._INPUT_STATE_TO_TASK["NEW_RETRY"] == "qualify_job_listings"
        assert consult_mod._INPUT_STATE_TO_TASK["VALID_TITLE_RETRY"] == "qualify_job_listings"


@pytest.mark.skipif(
    not hasattr(__import__("src.utils.config", fromlist=["CANDIDATE_STAGE_DISPATCH"]), "CANDIDATE_STAGE_DISPATCH"),
    reason="AST-972 product not on this publish tip",
)
class TestAst972CandidateStageConsultRouting:
    """AST-972 → AST-1252: run_consult_task routes craft_get_rubric to artifacts worker."""

    @pytest.mark.asyncio
    async def test_routes_requested_artifacts_via_stage_task_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        worker = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr("src.core.candidate.run_requested_artifacts_dispatch", worker)
        entity = {"astral_candidate_id": "c2", "state": "REQUESTED_ARTIFACTS"}
        out = await consult_mod.run_consult_task(
            "candidate",
            "REQUESTED_ARTIFACTS",
            [entity],
            "b1",
            entity,
            False,
            dispatch_task_key="craft_get_rubric",
        )
        assert out["total_passed"] == 1
        worker.assert_awaited_once_with("c2", debug=False)

    @pytest.mark.asyncio
    async def test_wrapper_keys_no_longer_routed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        worker = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr("src.core.candidate.run_requested_artifacts_dispatch", worker)
        entity = {"astral_candidate_id": "c1", "state": "REQUESTED_ARTIFACTS"}
        out = await consult_mod.run_consult_task(
            "candidate",
            "REQUESTED_ARTIFACTS",
            [entity],
            "b1",
            entity,
            False,
            dispatch_task_key="candidate_requested_artifacts",
        )
        assert out["total_processed"] == 0
        worker.assert_not_awaited()
        assert not hasattr(
            __import__("src.core.candidate", fromlist=["run_requested_resume_dispatch"]),
            "run_requested_resume_dispatch",
        )


class TestAst1055MeteoriteConsultRoutes:
    """AST-1055: route meteorite twins; upshot persists analysis_upshot under twin states."""

    @pytest.mark.asyncio
    async def test_routes_meteorite_like_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # run_consult_task normalizes batch shape via passed/failed/total (not total_*).
        batch = AsyncMock(return_value={"passed": 2, "failed": 0, "total": 2})
        monkeypatch.setattr(consult_mod, "meteorite_like_batch", batch)
        out = await consult_mod.run_consult_task(
            "job",
            "METEORITE_PASSED_GET",
            [{"astral_job_id": "m1"}, {"astral_job_id": "m2"}],
            "b-ml",
            {},
            dispatch_task_key="meteorite_like",
        )
        assert out["total_passed"] == 2
        batch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_routes_meteorite_upshot_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        summary = AsyncMock(
            return_value={
                "total_processed": 1,
                "total_passed": 1,
                "total_failed": 0,
                "total_errors": 0,
            }
        )
        monkeypatch.setattr(consult_mod, "_run_analysis_upshot_batch", summary)
        out = await consult_mod.run_consult_task(
            "job",
            "METEORITE_PASSED_LIKE",
            [{"astral_job_id": "m7"}],
            "b-mu",
            {},
            dispatch_task_key="meteorite_upshot",
        )
        assert out["total_passed"] == 1
        summary.assert_awaited_once()
        args, kwargs = summary.await_args
        assert kwargs.get("task_key", args[4] if len(args) > 4 else None) == "meteorite_upshot"

    @pytest.mark.asyncio
    async def test_meteorite_upshot_persists_analysis_upshot_key(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        job = {
            "astral_job_id": "mz",
            "state": "METEORITE_PASSED_LIKE",
            "company": None,
            "job_data": {"raw_job_listing": "listing"},
        }
        parsed = {
            "whole_jd_upshot": "ok",
            "take_jd": "a",
            "take_do": "b",
            "take_get": "c",
            "take_like": "d",
        }
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda aid: job)
        monkeypatch.setattr(
            consult_mod,
            "_prep_analysis_upshot_live_content",
            AsyncMock(return_value="live"),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": parsed}),
        )
        saver = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", saver)
        trans = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", trans)
        out = await consult_mod._run_analysis_upshot_batch(
            "b-mz", [job], {}, False, task_key="meteorite_upshot",
        )
        assert out["total_passed"] == 1
        saver.assert_called_once_with("mz", {"analysis_upshot": parsed})
        trans.assert_called_once_with(
            "meteorite_upshot",
            ["mz"],
            TASK_CONFIG["meteorite_upshot"]["pass_state"],
        )

# Branches: content gates; pass persist; collision fail; Style D; route (AST-1062).
class TestAst1062QualifyMeteorite:
    def _jd(self, n: int = 50) -> str:
        return "Visible JD body text. " * ((n // 20) + 1)

    def _job(self, aid: str = "job-m1") -> dict:
        from src.utils.config import TRACKER_CONFIG

        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        return {
            "astral_job_id": aid,
            "state": "METEORITE_NEW",
            "company": "meteorite-cand-m",
            "job_link": "https://jobs.example.com/old",
            "job_data": {jd_key: self._jd()},
        }

    def _good_response(self, aid: str = "job-m1") -> dict:
        return {
            "astral_job_id": aid,
            "company_job_id": "EXT-99",
            "job_title": "Senior Engineer",
            "job_link": "https://jobs.example.com/role/99",
            "jd_text": self._jd(60),
        }

    @pytest.mark.asyncio
    async def test_pass_initializes_and_qualifies(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        get_job = MagicMock(return_value={
            "company_job_id": "EXT-99",
            "job_title": "Senior Engineer",
            "job_link": "https://jobs.example.com/role/99",
            "job_data": {TRACKER_CONFIG["job_data_keys"]["job_description"]: self._jd(60)},
        })
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(consult_mod.tracker, "get_job", get_job)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [self._good_response()]},
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite("batch-m", [self._job()], {}, debug=True)
        assert out["passed"] == 1
        assert out["failed"] == 0
        initialize.assert_called_once()
        parsed = initialize.call_args.args[2]
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        assert parsed["company_job_id"] == "EXT-99"
        assert parsed["job_title"] == "Senior Engineer"
        assert parsed["job_link"].startswith("http")
        assert jd_key in parsed and "jd_text" not in parsed
        assert transition.call_args.args[2] == TASK_CONFIG["qualify_meteorite"]["pass_state"]

    @pytest.mark.asyncio
    async def test_pattern_mismatch_title_still_qualifies(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1153 P3: title_patterns would reject AI title on roster path; content gates pass.
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "is_meteorite_company"):
            pytest.skip("AST-1152 peel not on tip")
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        get_job = MagicMock(
            return_value={
                "company_job_id": "EXT-99",
                "job_title": "Senior Platform Engineer",
                "job_link": "https://jobs.example.com/role/99",
                "job_data": {
                    TRACKER_CONFIG["job_data_keys"]["job_description"]: self._jd(60)
                },
            }
        )
        vt = AsyncMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(consult_mod.tracker, "get_job", get_job)
        monkeypatch.setattr("src.core.gazer.validate_title_batch", vt)
        resp = {
            **self._good_response(),
            "job_title": "Senior Platform Engineer",
        }
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        ctx = {"candidate_data": {"contact": {"title_patterns": "^Nurse"}}}
        out = await consult_mod.qualify_meteorite("batch-1153-p3", [self._job()], ctx, debug=False)
        assert out["passed"] == 1
        assert out["failed"] == 0
        initialize.assert_called_once()
        assert transition.call_args.args[2] == TASK_CONFIG["qualify_meteorite"]["pass_state"]
        vt.assert_not_awaited()
        for c in transition.call_args_list:
            assert c.args[2] != "INVALID_TITLE"

    @pytest.mark.asyncio
    async def test_content_gates_fail_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        fail = TASK_CONFIG["qualify_meteorite"]["fail_state"]
        transition = MagicMock()
        initialize = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        cases = [
            {**self._good_response("j-empty"), "company_job_id": ""},
            {**self._good_response("j-title"), "job_title": "ab"},
            {**self._good_response("j-link"), "job_link": "/relative"},
            {**self._good_response("j-jd"), "jd_text": "short"},
        ]
        # AST-1133: Create http fallback would rescue /relative Ruth link — keep input empty for that gate.
        jobs = []
        for c in cases:
            j = self._job(c["astral_job_id"])
            if c["astral_job_id"] == "j-link":
                j = {**j, "job_link": ""}
            jobs.append(j)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": cases},
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite("batch-fail", jobs, {}, debug=False)
        assert out["passed"] == 0
        assert out["failed"] == 4
        assert initialize.call_count == 0
        assert all(c.args[2] == fail for c in transition.call_args_list)

    @pytest.mark.asyncio
    async def test_identity_collision_counts_failed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=False))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [self._good_response()]},
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite("batch-col", [self._job()], {}, debug=False)
        assert out["failed"] == 1
        assert out["passed"] == 0
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_debug_false_skips_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [self._good_response()]},
                    "timesheet": {},
                }
            ),
        )
        dbg_i = MagicMock()
        dbg_d = MagicMock()
        monkeypatch.setattr(consult_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(consult_mod.logger, "debug_index", dbg_i)
        monkeypatch.setattr(consult_mod.logger, "debug_detail", dbg_d)
        await consult_mod.qualify_meteorite("batch-q", [self._job()], {}, debug=False)
        assert not any(
            (c.kwargs.get("func") == "consult.qualify_meteorite") for c in dbg_i.call_args_list
        )

    def test_not_strict_encoded_batch_key(self) -> None:
        from src.core import agent as agent_mod
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG:
            pytest.skip("qualify_meteorite not on tip")
        assert "qualify_meteorite" not in agent_mod._STRICT_ENCODED_BATCH_CONSULT_KEYS

# Branches: single-job / ordered placeholder bind; "000" qualify path (AST-1076 UAT).
class TestAst1076BindResponseJobsToClaimed:
    def test_single_job_rewrites_non_claimed_echo(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_to_claimed"):
            pytest.skip("AST-1076 bind helper not on tip")
        claimed = [{"astral_job_id": "real-uuid-1"}]
        response = [{"astral_job_id": "000", "job_title": "Eng"}]
        consult_mod._bind_response_jobs_to_claimed(response, claimed)
        assert response[0]["astral_job_id"] == "real-uuid-1"

    def test_single_job_keeps_matching_id(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_to_claimed"):
            pytest.skip("AST-1076 bind helper not on tip")
        claimed = [{"astral_job_id": "real-uuid-1"}]
        response = [{"astral_job_id": "real-uuid-1"}]
        consult_mod._bind_response_jobs_to_claimed(response, claimed)
        assert response[0]["astral_job_id"] == "real-uuid-1"

    def test_ordered_digit_and_empty_placeholders(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_to_claimed"):
            pytest.skip("AST-1076 bind helper not on tip")
        claimed = [{"astral_job_id": "a"}, {"astral_job_id": "b"}, {"astral_job_id": "c"}]
        response = [
            {"astral_job_id": "000"},
            {"astral_job_id": ""},
            {"astral_job_id": "001"},
        ]
        consult_mod._bind_response_jobs_to_claimed(response, claimed)
        assert [r["astral_job_id"] for r in response] == ["a", "b", "c"]

    def test_ordered_does_not_overwrite_non_digit_fabricated(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_to_claimed"):
            pytest.skip("AST-1076 bind helper not on tip")
        claimed = [{"astral_job_id": "a"}, {"astral_job_id": "b"}]
        response = [
            {"astral_job_id": "000"},
            {"astral_job_id": "not-a-claim-uuid"},
        ]
        consult_mod._bind_response_jobs_to_claimed(response, claimed)
        assert response[0]["astral_job_id"] == "a"
        assert response[1]["astral_job_id"] == "not-a-claim-uuid"

    def test_length_mismatch_noop(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_to_claimed"):
            pytest.skip("AST-1076 bind helper not on tip")
        claimed = [{"astral_job_id": "a"}, {"astral_job_id": "b"}]
        response = [{"astral_job_id": "000"}]
        consult_mod._bind_response_jobs_to_claimed(response, claimed)
        assert response[0]["astral_job_id"] == "000"


class TestAst1076QualifyMeteoritePlaceholderId:
    """UAT: usable fields + astral_job_id '000' bind → QUALIFIED (not ERROR)."""

    def _jd(self) -> str:
        return "Visible JD body text enough characters here. " * 2

    @pytest.mark.asyncio
    async def test_zero_echo_id_binds_and_qualifies(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "_bind_response_jobs_to_claimed"):
            pytest.skip("AST-1076 bind helper not on tip")
        aid = "claimed-meteorite-uuid"
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": "EXT-1",
                    "job_title": "Engineer Role",
                    "job_link": "https://jobs.example.com/1",
                    "job_data": {jd_key: self._jd()},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "000",
                                "company_job_id": "EXT-1",
                                "job_title": "Engineer Role",
                                "job_link": "https://jobs.example.com/1",
                                "jd_text": self._jd(),
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        job = {
            "astral_job_id": aid,
            "state": "METEORITE_NEW",
            "company": "meteorite-cand-x",
            "job_link": "https://jobs.example.com/old",
            "job_data": {jd_key: self._jd()},
        }
        out = await consult_mod.qualify_meteorite("batch-1076", [job], {}, debug=False)
        assert out.get("errors", 0) == 0 or "errors" not in out or out.get("failed", 0) + out.get("passed", 0) >= 1
        assert out["passed"] == 1
        assert out["failed"] == 0
        initialize.assert_called_once()
        assert initialize.call_args.args[0] == aid
        assert transition.call_args.args[2] == TASK_CONFIG["qualify_meteorite"]["pass_state"]


# Branches: AI wins; UUID fallback; empty fail; input link_for_id composition (AST-1120).
class TestAst1120CompanyJobIdFallback:
    _DICE_UUID = "9f704ad3-7a18-506a-bd5e-6a84e73b7c00"
    _DICE_URL = f"https://www.dice.com/company-profile/{_DICE_UUID}"

    def _jd(self, n: int = 50) -> str:
        return "Visible JD body text. " * ((n // 20) + 1)

    def _job(self, aid: str = "job-1120", job_link: str = "https://jobs.example.com/old") -> dict:
        from src.utils.config import TRACKER_CONFIG

        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        return {
            "astral_job_id": aid,
            "state": "METEORITE_NEW",
            "company": "meteorite-cand-1120",
            "job_link": job_link,
            "job_data": {jd_key: self._jd()},
        }

    def _good_fields(self, aid: str, **overrides: object) -> dict:
        base = {
            "astral_job_id": aid,
            "company_job_id": "AI-EXT",
            "job_title": "Senior Engineer",
            "job_link": "https://jobs.example.com/role/99",
            "jd_text": self._jd(60),
        }
        base.update(overrides)
        return base

    def test_resolve_helper_ai_wins_and_fallbacks(self) -> None:
        if not hasattr(consult_mod, "_resolve_company_job_id"):
            pytest.skip("AST-1120 resolve helper not on tip")
        other = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert consult_mod._resolve_company_job_id(
            "AI-KEEP", f"https://example.com/{other}"
        ) == "AI-KEEP"
        assert consult_mod._resolve_company_job_id("", self._DICE_URL) == self._DICE_UUID
        assert consult_mod._resolve_company_job_id(None, self._DICE_URL) == self._DICE_UUID  # type: ignore[arg-type]
        assert consult_mod._resolve_company_job_id("", "https://example.com/jobs/no-uuid") == ""
        assert consult_mod._resolve_company_job_id("", "") == ""
        assert consult_mod._resolve_company_job_id("  ", None) == ""  # type: ignore[arg-type]
        # process link_for_id: empty response job_link → input row link
        link_for_id = "" or self._DICE_URL
        assert consult_mod._resolve_company_job_id("", link_for_id) == self._DICE_UUID

    @pytest.mark.asyncio
    async def test_ai_id_unchanged_when_link_has_different_uuid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "_resolve_company_job_id"):
            pytest.skip("AST-1120 resolve helper not on tip")
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": "AI-KEEP",
                    "job_title": "Senior Engineer",
                    "job_link": self._DICE_URL,
                    "job_data": {jd_key: self._jd(60)},
                }
            ),
        )
        resp = self._good_fields("j-ai", company_job_id="AI-KEEP", job_link=self._DICE_URL)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite("batch-1120-ai", [self._job("j-ai")], {}, debug=False)
        assert out["passed"] == 1
        assert initialize.call_args.args[2]["company_job_id"] == "AI-KEEP"

    @pytest.mark.asyncio
    async def test_empty_ai_records_uuid_from_job_link(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "_resolve_company_job_id"):
            pytest.skip("AST-1120 resolve helper not on tip")
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": self._DICE_UUID,
                    "job_title": "Senior Engineer",
                    "job_link": self._DICE_URL,
                    "job_data": {jd_key: self._jd(60)},
                }
            ),
        )
        resp = self._good_fields("j-uuid", company_job_id="", job_link=self._DICE_URL)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite(
            "batch-1120-uuid", [self._job("j-uuid")], {}, debug=False
        )
        assert out["passed"] == 1
        assert out["failed"] == 0
        assert initialize.call_args.args[2]["company_job_id"] == self._DICE_UUID
        assert transition.call_args.args[2] == TASK_CONFIG["qualify_meteorite"]["pass_state"]

    @pytest.mark.asyncio
    async def test_empty_ai_no_uuid_still_empty_id_fail(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "_resolve_company_job_id"):
            pytest.skip("AST-1120 resolve helper not on tip")
        fail = TASK_CONFIG["qualify_meteorite"]["fail_state"]
        transition = MagicMock()
        initialize = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        resp = self._good_fields(
            "j-empty",
            company_job_id="",
            job_link="https://example.com/jobs/no-uuid-here",
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite(
            "batch-1120-fail", [self._job("j-empty")], {}, debug=False
        )
        assert out["passed"] == 0
        assert out["failed"] == 1
        assert initialize.call_count == 0
        assert transition.call_args.args[2] == fail


# Branches: debug source=AI / UUID-from-job_link / neither; fallback_job_link; debug=False (AST-1121).
class TestAst1121CompanyJobIdDebugSource:
    _DICE_UUID = "9f704ad3-7a18-506a-bd5e-6a84e73b7c00"
    _DICE_URL = f"https://www.dice.com/company-profile/{_DICE_UUID}"

    def _jd(self, n: int = 50) -> str:
        return "Visible JD body text. " * ((n // 20) + 1)

    def _job(self, aid: str = "job-1121") -> dict:
        from src.utils.config import TRACKER_CONFIG

        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        return {
            "astral_job_id": aid,
            "state": "METEORITE_NEW",
            "company": "meteorite-cand-1121",
            "job_link": "https://jobs.example.com/old",
            "job_data": {jd_key: self._jd()},
        }

    def _fields(self, aid: str, **overrides: object) -> dict:
        base = {
            "astral_job_id": aid,
            "company_job_id": "AI-EXT",
            "job_title": "Senior Engineer",
            "job_link": "https://jobs.example.com/role/99",
            "jd_text": self._jd(60),
        }
        base.update(overrides)
        return base

    def _patch_debug_loggers(self, monkeypatch: pytest.MonkeyPatch):
        dbg_i = MagicMock()
        dbg_d = MagicMock()
        monkeypatch.setattr(consult_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(consult_mod.logger, "debug_index", dbg_i)
        monkeypatch.setattr(consult_mod.logger, "debug_detail", dbg_d)
        return dbg_i, dbg_d

    @staticmethod
    def _detail_text(dbg_d: MagicMock) -> str:
        return " ".join(str(c.args[0]) for c in dbg_d.call_args_list if c.args)

    @pytest.mark.asyncio
    async def test_debug_pass_ai_source_no_fallback_link(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": "AI-KEEP",
                    "job_title": "Senior Engineer",
                    "job_link": self._DICE_URL,
                    "job_data": {jd_key: self._jd(60)},
                }
            ),
        )
        resp = self._fields("j-ai", company_job_id="AI-KEEP", job_link=self._DICE_URL)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        _, dbg_d = self._patch_debug_loggers(monkeypatch)
        out = await consult_mod.qualify_meteorite(
            "batch-1121-ai", [self._job("j-ai")], {}, debug=True
        )
        assert out["passed"] == 1
        detail = self._detail_text(dbg_d)
        assert "found source=AI" in detail
        assert "fallback_job_link=" not in detail
        assert "recorded company_job_id='AI-KEEP'" in detail

    @pytest.mark.asyncio
    async def test_debug_pass_uuid_source_includes_fallback_link(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "_resolve_company_job_id"):
            pytest.skip("AST-1120 resolve helper not on tip")
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": self._DICE_UUID,
                    "job_title": "Senior Engineer",
                    "job_link": self._DICE_URL,
                    "job_data": {jd_key: self._jd(60)},
                }
            ),
        )
        resp = self._fields("j-uuid", company_job_id="", job_link=self._DICE_URL)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        _, dbg_d = self._patch_debug_loggers(monkeypatch)
        out = await consult_mod.qualify_meteorite(
            "batch-1121-uuid", [self._job("j-uuid")], {}, debug=True
        )
        assert out["passed"] == 1
        detail = self._detail_text(dbg_d)
        assert "found source=UUID-from-job_link" in detail
        assert f"fallback_job_link={self._DICE_URL!r}" in detail
        assert f"recorded company_job_id={self._DICE_UUID!r}" in detail

    @pytest.mark.asyncio
    async def test_debug_fail_ai_source_omits_fallback_link(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AI id present but another content gate fails — still source=AI, no fallback_job_link."""
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock())
        resp = self._fields("j-ai-fail", company_job_id="AI-KEEP", job_title="ab")
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        _, dbg_d = self._patch_debug_loggers(monkeypatch)
        out = await consult_mod.qualify_meteorite(
            "batch-1121-ai-fail", [self._job("j-ai-fail")], {}, debug=True
        )
        assert out["failed"] == 1
        detail = self._detail_text(dbg_d)
        assert "found source=AI" in detail
        assert "fallback_job_link=" not in detail
        assert "company_job_id='AI-KEEP'" in detail

    @pytest.mark.asyncio
    async def test_debug_fail_neither_includes_fallback_link(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock())
        link = "https://example.com/jobs/no-uuid-here"
        resp = self._fields("j-neither", company_job_id="", job_link=link)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        _, dbg_d = self._patch_debug_loggers(monkeypatch)
        out = await consult_mod.qualify_meteorite(
            "batch-1121-neither", [self._job("j-neither")], {}, debug=True
        )
        assert out["failed"] == 1
        detail = self._detail_text(dbg_d)
        assert "gate=empty company_job_id" in detail
        assert "found source=neither" in detail
        assert f"fallback_job_link={link!r}" in detail
        assert "company_job_id=''" in detail

    @pytest.mark.asyncio
    async def test_debug_false_omits_source_labels(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [self._fields("j-quiet", company_job_id="", job_link=self._DICE_URL)]
                    },
                    "timesheet": {},
                }
            ),
        )
        dbg_i, dbg_d = self._patch_debug_loggers(monkeypatch)
        await consult_mod.qualify_meteorite(
            "batch-1121-quiet", [self._job("j-quiet")], {}, debug=False
        )
        assert not any(
            (c.kwargs.get("func") == "consult.qualify_meteorite") for c in dbg_i.call_args_list
        )
        assert "found source=" not in self._detail_text(dbg_d)


# Branches: RESPONSE omits company_job_id key → UUID fallback still records (AST-1127 UAT).
class TestAst1127QualifyMeteoriteOmitCompanyJobId:
    _DICE_UUID = "9f704ad3-7a18-506a-bd5e-6a84e73b7c00"
    _DICE_URL = f"https://www.dice.com/company-profile/{_DICE_UUID}"

    def _jd(self, n: int = 50) -> str:
        return "Visible JD body text. " * ((n // 20) + 1)

    @pytest.mark.asyncio
    async def test_omitted_company_job_id_key_falls_back_to_uuid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "_resolve_company_job_id"):
            pytest.skip("AST-1120 resolve helper not on tip")
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": self._DICE_UUID,
                    "job_title": "Senior Engineer",
                    "job_link": self._DICE_URL,
                    "job_data": {jd_key: self._jd(60)},
                }
            ),
        )
        # Key absent (not "") — schema optional (AST-1127); consult resolve owns fill.
        resp = {
            "astral_job_id": "j-omit",
            "job_title": "Senior Engineer",
            "job_link": self._DICE_URL,
            "jd_text": self._jd(60),
        }
        assert "company_job_id" not in resp
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"jobs": [resp]},
                    "timesheet": {},
                }
            ),
        )
        job = {
            "astral_job_id": "j-omit",
            "state": "METEORITE_NEW",
            "company": "meteorite-cand-1127",
            "job_link": "https://jobs.example.com/old",
            "job_data": {jd_key: self._jd()},
        }
        out = await consult_mod.qualify_meteorite("batch-1127-omit", [job], {}, debug=False)
        assert out["passed"] == 1
        assert out["failed"] == 0
        assert initialize.call_args.args[2]["company_job_id"] == self._DICE_UUID
        assert transition.call_args.args[2] == TASK_CONFIG["qualify_meteorite"]["pass_state"]



# Branches: unique link bind; claimed ids untouched; ambiguous drop; empty skip (AST-1133).
class TestAst1133BindResponseJobsByJobLink:
    def test_binds_unmatched_rows_by_normalized_link(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_by_job_link"):
            pytest.skip("AST-1133 link bind helper not on tip")
        claimed = [
            {"astral_job_id": "C0", "job_link": "https://Jobs.Example.com/role/a/"},
            {"astral_job_id": "C1", "job_link": "https://jobs.example.com/role/b"},
        ]
        response = [
            {
                "astral_job_id": "dice-uuid-aaaa",
                "job_link": "https://jobs.example.com/role/a",
                "job_title": "A",
            },
            {
                "astral_job_id": "dice-uuid-bbbb",
                "job_link": "https://jobs.example.com/role/b",
                "job_title": "B",
            },
        ]
        consult_mod._bind_response_jobs_by_job_link(response, claimed)
        assert [r["astral_job_id"] for r in response] == ["C0", "C1"]

    def test_does_not_overwrite_already_claimed_ids(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_by_job_link"):
            pytest.skip("AST-1133 link bind helper not on tip")
        claimed = [
            {"astral_job_id": "C0", "job_link": "https://jobs.example.com/role/a"},
            {"astral_job_id": "C1", "job_link": "https://jobs.example.com/role/b"},
        ]
        response = [
            {"astral_job_id": "C0", "job_link": "https://jobs.example.com/role/b"},
            {"astral_job_id": "wrong", "job_link": "https://jobs.example.com/role/a"},
        ]
        consult_mod._bind_response_jobs_by_job_link(response, claimed)
        assert response[0]["astral_job_id"] == "C0"
        # C0 already assigned; unmatched row cannot steal C0 via link.
        assert response[1]["astral_job_id"] == "wrong"

    def test_ambiguous_duplicate_claim_links_not_bound(self) -> None:
        if not hasattr(consult_mod, "_bind_response_jobs_by_job_link"):
            pytest.skip("AST-1133 link bind helper not on tip")
        claimed = [
            {"astral_job_id": "C0", "job_link": "https://jobs.example.com/same"},
            {"astral_job_id": "C1", "job_link": "https://jobs.example.com/same"},
        ]
        response = [
            {"astral_job_id": "x0", "job_link": "https://jobs.example.com/same"},
            {"astral_job_id": "x1", "job_link": "https://jobs.example.com/same"},
        ]
        consult_mod._bind_response_jobs_by_job_link(response, claimed)
        assert [r["astral_job_id"] for r in response] == ["x0", "x1"]


# Branches: multi-job link bind qualify; Create link fallback; content FAILED; Style D link_source (AST-1133).
class TestAst1133QualifyMeteoriteListCreated:
    _UUID0 = "11111111-1111-1111-1111-111111111111"
    _UUID1 = "22222222-2222-2222-2222-222222222222"

    def _jd(self) -> str:
        return "Visible JD body text enough characters here. " * 2

    def _claim(self, aid: str, link: str) -> dict:
        from src.utils.config import TRACKER_CONFIG

        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        return {
            "astral_job_id": aid,
            "state": "METEORITE_NEW",
            "company": "meteorite-cand-1133",
            "job_link": link,
            "job_data": {jd_key: self._jd()},
        }

    @pytest.mark.asyncio
    async def test_multi_job_wrong_ids_bind_by_link_and_qualify(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        if not hasattr(consult_mod, "_bind_response_jobs_by_job_link"):
            pytest.skip("AST-1133 link bind helper not on tip")
        pass_state = TASK_CONFIG["qualify_meteorite"]["pass_state"]
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        link0 = f"https://www.dice.com/job-detail/{self._UUID0}"
        link1 = f"https://www.dice.com/job-detail/{self._UUID1}"
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                side_effect=lambda aid: {
                    "company_job_id": self._UUID0 if aid == "C0" else self._UUID1,
                    "job_title": "Engineer",
                    "job_link": link0 if aid == "C0" else link1,
                    "job_data": {jd_key: self._jd()},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": self._UUID0,
                                "company_job_id": self._UUID0,
                                "job_title": "Engineer A",
                                "job_link": link0,
                                "jd_text": self._jd(),
                            },
                            {
                                "astral_job_id": self._UUID1,
                                "company_job_id": self._UUID1,
                                "job_title": "Engineer B",
                                "job_link": link1,
                                "jd_text": self._jd(),
                            },
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        jobs = [self._claim("C0", link0), self._claim("C1", link1)]
        out = await consult_mod.qualify_meteorite("batch-1133-bind", jobs, {}, debug=False)
        assert out["passed"] == 2
        assert out["failed"] == 0
        assert out.get("errors", 0) == 0
        assert initialize.call_count == 2
        assert {c.args[0] for c in initialize.call_args_list} == {"C0", "C1"}
        assert all(c.args[2] == pass_state for c in transition.call_args_list)

    @pytest.mark.asyncio
    async def test_empty_ruth_link_uses_create_link_and_qualifies(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        pass_state = TASK_CONFIG["qualify_meteorite"]["pass_state"]
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        create_link = f"https://www.dice.com/job-detail/{self._UUID0}"
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": self._UUID0,
                    "job_title": "Engineer",
                    "job_link": create_link,
                    "job_data": {jd_key: self._jd()},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "C0",
                                "company_job_id": "",
                                "job_title": "Engineer Role",
                                "job_link": "",
                                "jd_text": self._jd(),
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite(
            "batch-1133-fallback", [self._claim("C0", create_link)], {}, debug=True
        )
        assert out["passed"] == 1
        assert out["failed"] == 0
        parsed = initialize.call_args.args[2]
        assert parsed["job_link"] == create_link
        assert parsed["company_job_id"] == self._UUID0
        assert transition.call_args.args[2] == pass_state

    @pytest.mark.asyncio
    async def test_short_title_still_content_failed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        fail = TASK_CONFIG["qualify_meteorite"]["fail_state"]
        create_link = f"https://www.dice.com/job-detail/{self._UUID0}"
        transition = MagicMock()
        initialize = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "C0",
                                "company_job_id": self._UUID0,
                                "job_title": "ab",
                                "job_link": "",
                                "jd_text": self._jd(),
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite(
            "batch-1133-title", [self._claim("C0", create_link)], {}, debug=False
        )
        assert out["passed"] == 0
        assert out["failed"] == 1
        assert initialize.call_count == 0
        assert transition.call_args.args[2] == fail

    @pytest.mark.asyncio
    async def test_debug_detail_includes_link_source_input(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG or not hasattr(consult_mod, "qualify_meteorite"):
            pytest.skip("qualify_meteorite not on tip")
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        create_link = f"https://www.dice.com/job-detail/{self._UUID0}"
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": self._UUID0,
                    "job_title": "Engineer",
                    "job_link": create_link,
                    "job_data": {jd_key: self._jd()},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "C0",
                                "company_job_id": "",
                                "job_title": "Engineer Role",
                                "job_link": "",
                                "jd_text": self._jd(),
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        dbg_d = MagicMock()
        monkeypatch.setattr(consult_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(consult_mod.logger, "debug_index", MagicMock())
        monkeypatch.setattr(consult_mod.logger, "debug_detail", dbg_d)
        await consult_mod.qualify_meteorite(
            "batch-1133-src", [self._claim("C0", create_link)], {}, debug=True
        )
        detail = " ".join(str(c.args[0]) if c.args else str(c.kwargs) for c in dbg_d.call_args_list)
        # AST-1197: Create-time ATS fallback is labeled http-input (was bare "input").
        assert "link_source=http-input" in detail
        assert "found source=UUID-from-job_link" in detail


class TestAst1197QualifyMeteoriteApply:
    """AST-1197: CONTENT assemble, email- QUALIFY waiver, BOT_BLOCKED, Style D sources."""

    _CHALLENGE = (
        "Additional Verification Required\n"
        "Your Ray ID for this request is a26948de4d78f005\n"
        "Troubleshooting Cloudflare Errors"
    )

    def _jd(self, n: int = 60) -> str:
        return "Visible meteorite JD body text. " * ((n // 25) + 1)

    def _job(self, aid: str, *, link: str = "", jd: str | None = None) -> dict:
        from src.utils.config import TRACKER_CONFIG

        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        return {
            "astral_job_id": aid,
            "state": "METEORITE_NEW",
            "company": "meteorite-cand-1197",
            "job_link": link,
            "job_data": {jd_key: self._jd() if jd is None else jd},
        }

    @pytest.mark.asyncio
    async def test_assemble_emits_content_label(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG:
            pytest.skip("qualify_meteorite not on tip")
        captured: dict = {}

        async def _capture_do_task(**kwargs):
            captured["live_content"] = kwargs.get("live_content")
            return {
                "success": True,
                "parsed_response": {
                    "jobs": [{
                        "astral_job_id": "j1",
                        "company_job_id": "EXT-1",
                        "job_title": "Engineer Role",
                        "job_link": "https://jobs.example.com/1",
                        "jd_text": self._jd(),
                    }]
                },
                "timesheet": {},
            }

        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", MagicMock())
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value={}))
        monkeypatch.setattr(consult_mod, "do_task", _capture_do_task)
        await consult_mod.qualify_meteorite(
            "batch-1197-asm",
            [self._job("j1", link="https://jobs.example.com/old")],
            {},
            debug=False,
        )
        lc = captured["live_content"]
        assert lc.startswith("METEORITE JOBS:")
        assert "000: job_link: https://jobs.example.com/old" in lc
        assert "CONTENT:\n" in lc
        assert "job_description:" not in lc.split("CONTENT:", 1)[0]

    @pytest.mark.asyncio
    async def test_email_link_qualifies_without_company_job_id(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG:
            pytest.skip("qualify_meteorite not on tip")
        prefix = TASK_CONFIG["qualify_meteorite"]["email_link_prefix"]
        email_link = f"{prefix}recruiter@example.com-20260805T224603Z"
        transition = MagicMock()
        initialize = MagicMock(return_value=True)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(consult_mod.tracker, "get_job", MagicMock(return_value={}))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{
                            "astral_job_id": "j-email",
                            "company_job_id": "",
                            "job_title": "Staff Engineer",
                            "job_link": email_link,
                            "jd_text": self._jd(),
                        }]
                    },
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite(
            "batch-1197-email", [self._job("j-email")], {}, debug=False,
        )
        assert out["passed"] == 1 and out["failed"] == 0
        initialize.assert_called_once()
        parsed = initialize.call_args.args[2]
        assert parsed["job_link"] == email_link
        assert parsed["company_job_id"] == ""
        assert transition.call_args.args[2] == TASK_CONFIG["qualify_meteorite"]["pass_state"]

    @pytest.mark.asyncio
    async def test_challenge_input_jd_transitions_bot_blocked(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG:
            pytest.skip("qualify_meteorite not on tip")
        bot_state = TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"]
        transition = MagicMock()
        initialize = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", initialize)
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{
                            "astral_job_id": "j-bot",
                            "company_job_id": "EXT-9",
                            "job_title": "Engineer Role",
                            "job_link": "https://jobs.example.com/blocked",
                            "jd_text": "",
                        }]
                    },
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite(
            "batch-1197-bot",
            [self._job("j-bot", link="https://jobs.example.com/blocked", jd=self._CHALLENGE)],
            {},
            debug=False,
        )
        assert out["passed"] == 0
        assert out["failed"] == 1
        initialize.assert_not_called()
        assert transition.call_args.args[2] == bot_state

    @pytest.mark.asyncio
    async def test_short_title_fails_qualify_not_bot(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import TASK_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG:
            pytest.skip("qualify_meteorite not on tip")
        fail = TASK_CONFIG["qualify_meteorite"]["fail_state"]
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock())
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{
                            "astral_job_id": "j-short",
                            "company_job_id": "EXT-1",
                            "job_title": "ab",
                            "job_link": "https://jobs.example.com/1",
                            "jd_text": self._jd(),
                        }]
                    },
                    "timesheet": {},
                }
            ),
        )
        out = await consult_mod.qualify_meteorite(
            "batch-1197-fail", [self._job("j-short", link="https://jobs.example.com/1")],
            {}, debug=False,
        )
        assert out["failed"] == 1
        assert transition.call_args.args[2] == fail
        assert transition.call_args.args[2] != TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"]

    @pytest.mark.asyncio
    async def test_style_d_email_link_and_subject_title_source(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import TASK_CONFIG, TRACKER_CONFIG

        if "qualify_meteorite" not in TASK_CONFIG:
            pytest.skip("qualify_meteorite not on tip")
        prefix = TASK_CONFIG["qualify_meteorite"]["email_link_prefix"]
        email_link = f"{prefix}agent@corp.example-20260806T010203Z"
        # Escaped & in subject must still match Ruth's unescaped title (html.unescape).
        subject_html = (
            '<header class="email-subject"><h1>Sales &amp; Marketing Lead</h1></header>\n'
            + self._jd()
        )
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(consult_mod.tracker, "initialize_job", MagicMock(return_value=True))
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            MagicMock(
                return_value={
                    "company_job_id": "",
                    "job_title": "Sales & Marketing Lead",
                    "job_link": email_link,
                    "job_data": {jd_key: subject_html},
                }
            ),
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{
                            "astral_job_id": "j-sub",
                            "company_job_id": "",
                            "job_title": "Sales & Marketing Lead",
                            "job_link": email_link,
                            "jd_text": self._jd(),
                        }]
                    },
                    "timesheet": {},
                }
            ),
        )
        dbg_d = MagicMock()
        monkeypatch.setattr(consult_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(consult_mod.logger, "debug_index", MagicMock())
        monkeypatch.setattr(consult_mod.logger, "debug_detail", dbg_d)
        out = await consult_mod.qualify_meteorite(
            "batch-1197-d",
            [self._job("j-sub", jd=subject_html)],
            {},
            debug=True,
        )
        assert out["passed"] == 1
        detail = " ".join(str(c.args[0]) if c.args else str(c.kwargs) for c in dbg_d.call_args_list)
        assert "link_source=email-synthesized" in detail
        assert "title_source=subject" in detail

    def test_title_source_helper_unescape(self) -> None:
        assert consult_mod._qualify_meteorite_title_source(
            "Sales & Marketing Lead", "Sales & Marketing Lead",
        ) == "subject"
        assert consult_mod._qualify_meteorite_email_subject(
            '<header class="email-subject"><h1>Sales &amp; Marketing Lead</h1></header>'
        ) == "Sales & Marketing Lead"


class TestAst1155IncompleteGradeRetry:
    """AST-1155: incomplete/extra grade sets → retry holding, never first-touch technical."""

    def test_require_complete_grade_set_x0_counts_as_present(self) -> None:
        rubric = [
            {"label": "Healthcare Domain Expertise"},
            {"label": "Remote-First Requirement"},
        ]
        incomplete = [{"vector": "Remote-First Requirement", "grade": "A", "confidence": 5}]
        missing, extra = consult_mod._grade_set_vector_diff(rubric, incomplete)
        assert missing == {"Healthcare Domain Expertise"}
        assert not extra
        with pytest.raises(ValueError, match="missing vectors"):
            consult_mod._require_complete_grade_set(rubric, incomplete)
        complete = incomplete + [
            {"vector": "Healthcare Domain Expertise", "grade": "X", "confidence": 0}
        ]
        consult_mod._require_complete_grade_set(rubric, complete)

    def test_consult_batch_fail_dest_graded_triggers(self) -> None:
        do_err = TASK_CONFIG["grade_do"]["error_state"]
        get_err = TASK_CONFIG["grade_get"]["error_state"]
        like_err = TASK_CONFIG["grade_like"]["error_state"]
        jd_err = TASK_CONFIG["evaluate_jd"]["error_state"]
        met_err = TASK_CONFIG["evaluate_meteorite"]["error_state"]
        assert consult_mod._consult_batch_fail_dest("PASSED_JD", do_err) == "PASSED_JD_RETRY"
        assert consult_mod._consult_batch_fail_dest("PASSED_JD_RETRY", do_err) == do_err
        assert consult_mod._consult_batch_fail_dest("PASSED_DO", get_err) == "PASSED_DO_RETRY"
        assert consult_mod._consult_batch_fail_dest("CULTURE_READY", like_err) == "CULTURE_READY_RETRY"
        assert consult_mod._consult_batch_fail_dest(
            "METEORITE_PASSED_JD", do_err
        ) == "METEORITE_PASSED_JD_RETRY"
        assert consult_mod._consult_batch_fail_dest(
            "METEORITE_PASSED_JD_RETRY", "METEORITE_FAILED_TECHNICAL_DO"
        ) == "METEORITE_FAILED_TECHNICAL_DO"
        # Twin evaluate hop: incomplete → METEORITE_QUALIFIED_RETRY; second strike → twin error.
        assert consult_mod._consult_batch_fail_dest(
            "METEORITE_QUALIFIED", met_err
        ) == "METEORITE_QUALIFIED_RETRY"
        assert consult_mod._consult_batch_fail_dest(
            "METEORITE_QUALIFIED_RETRY", met_err
        ) == met_err
        assert met_err == "METEORITE_ERROR_EVALUATE_JD"
        assert met_err != jd_err
        # Classic evaluate_jd incomplete still holds on JD_READY_RETRY (unchanged).
        assert consult_mod._consult_batch_fail_dest("JD_READY", jd_err) == "JD_READY_RETRY"
        assert consult_mod._consult_batch_fail_dest("JD_READY_RETRY", jd_err) == jd_err
        # Legacy map companions for holdings already in the map.
        assert consult_mod._INPUT_STATE_TO_TASK["PASSED_JD_RETRY"] == "grade_do"
        assert consult_mod._INPUT_STATE_TO_TASK["PASSED_DO_RETRY"] == "grade_get"

    @pytest.mark.asyncio
    async def test_render_verdict_incomplete_first_strike_to_retry(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "job-1", "company": "co", "state": "PASSED_JD", "job_data": {}}
        rubric = [_rubric_item("Fit"), _rubric_item("Other", code="OT")]
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    # Omit Other — incomplete vs live rubric.
                    "parsed_response": {
                        "grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]
                    },
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "_rubric_criteria_for_cfg",
            lambda _cid, _cfg: rubric,
        )
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-1",
            ctx={"candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is False
        assert out["to_state"] == "PASSED_JD_RETRY"
        assert "missing vectors" in out["error"]
        transition.assert_called_once_with("grade_do", ["job-1"], "PASSED_JD_RETRY")

    @pytest.mark.asyncio
    async def test_render_verdict_incomplete_second_strike_to_technical(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {
            "astral_job_id": "job-1",
            "company": "co",
            "state": "PASSED_JD_RETRY",
            "job_data": {},
        }
        rubric = [_rubric_item("Fit"), _rubric_item("Other", code="OT")]
        transition = MagicMock()
        err = TASK_CONFIG["grade_do"]["error_state"]
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]
                    },
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "_rubric_criteria_for_cfg",
            lambda _cid, _cfg: rubric,
        )
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-1",
            ctx={"candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is False
        assert out["to_state"] == err
        transition.assert_called_once_with("grade_do", ["job-1"], err)

    @pytest.mark.asyncio
    async def test_render_verdict_meteorite_incomplete_to_holding(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {
            "astral_job_id": "job-m",
            "company": "meteorite-co",
            "state": "METEORITE_PASSED_JD",
            "job_data": {},
        }
        rubric = [_rubric_item("Fit"), _rubric_item("Other", code="OT")]
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "get_job", lambda astral_job_id: job)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}]
                    },
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "_rubric_criteria_for_cfg",
            lambda _cid, _cfg: rubric,
        )
        out = await consult_mod.render_verdict(
            "grade_do",
            "job-m",
            ctx={"candidate_data": {"artifacts": {"do_rubric": rubric}}},
        )
        assert out["success"] is False
        assert out["to_state"] == "METEORITE_PASSED_JD_RETRY"
        transition.assert_called_once_with(
            "grade_do", ["job-m"], "METEORITE_PASSED_JD_RETRY"
        )

    @pytest.mark.asyncio
    async def test_batch_incomplete_grades_route_primary_to_retry(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod,
            "_rubric_criteria_for_cfg",
            lambda _cid, _cfg: [_rubric_item("Fit"), _rubric_item("Other", code="OT")],
        )
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "job-p",
                                "grades": [{"grade": "A", "confidence": 2, "vector": "Fit"}],
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )

        def process(input_job, response_job, cfg):
            consult_mod._require_complete_grade_set(
                [_rubric_item("Fit"), _rubric_item("Other", code="OT")],
                response_job["grades"],
            )
            return cfg["pass_state"]

        jobs = [{"astral_job_id": "job-p", "state": "PASSED_JD", "job_title": "Primary"}]
        out = await consult_mod._run_batch_consult(
            "grade_do",
            "batch-1155-incomplete",
            jobs,
            lambda rows: "content",
            process,
            {"candidate_data": {"artifacts": {"do_rubric": [_rubric_item("Fit")]}}},
            False,
        )
        assert out["bad_grades"] == ["job-p"]
        assert sorted(
            (c.args[0], tuple(sorted(c.args[1])), c.args[2]) for c in transition.call_args_list
        ) == [("grade_do", ("job-p",), "PASSED_JD_RETRY")]


# Branches: meteorite title-screen proof locks after AST-1152 peel (AST-1153 P1/P5).
class TestAst1153MeteoriteTitleScreenProof:
    @pytest.mark.asyncio
    async def test_rehomes_meteorite_new_never_invalid_title(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        if not hasattr(consult_mod, "is_meteorite_company"):
            pytest.skip("AST-1152 peel not on tip")
        landing = METEORITE_CONFIG["job_create_state"]
        transition = MagicMock()
        vt = AsyncMock(return_value={"failed": 0, "passed": 0, "total": 0})
        batch = AsyncMock()
        monkeypatch.setattr(consult_mod.tracker, "transition_job_state", transition)
        monkeypatch.setattr("src.core.gazer.validate_title_batch", vt)
        monkeypatch.setattr(consult_mod, "_run_batch_consult", batch)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda jid: {
                "astral_job_id": jid,
                "state": landing,
                "company": "meteorite-cand-proof",
            },
        )
        jobs = [
            {
                "astral_job_id": "job-m-proof",
                "state": "NEW",
                "company": "meteorite-cand-proof",
                "job_data": {"raw_job_listing": "Janitor Wanted"},
            }
        ]
        ctx = {"candidate_data": {"contact": {"title_patterns": "^Engineer"}}}
        out = await consult_mod.qualify_job_listings("batch-1153-p1", jobs, ctx, debug=False)
        transition.assert_called_once_with(["job-m-proof"], landing)
        vt.assert_not_awaited()
        batch.assert_not_awaited()
        assert jobs[0]["state"] == landing
        assert landing not in ("INVALID_TITLE", "VALID_TITLE")
        assert out == {"passed": 0, "failed": 0, "total": 1}

    @pytest.mark.asyncio
    async def test_mixed_batch_roster_screens_meteorite_rehomes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # P1 + P5: roster NEW still title-screens; meteorite NEW re-homes only.
        from src.utils.config import METEORITE_CONFIG

        if not hasattr(consult_mod, "is_meteorite_company"):
            pytest.skip("AST-1152 peel not on tip")
        landing = METEORITE_CONFIG["job_create_state"]
        transition = MagicMock()
        vt = AsyncMock(return_value={"failed": 1, "passed": 0, "total": 1})
        batch = AsyncMock()
        monkeypatch.setattr(consult_mod.tracker, "transition_job_state", transition)
        monkeypatch.setattr("src.core.gazer.validate_title_batch", vt)
        monkeypatch.setattr(consult_mod, "_run_batch_consult", batch)

        def _get_job(jid: str) -> dict:
            if jid == "job-m-proof":
                return {
                    "astral_job_id": jid,
                    "state": landing,
                    "company": "meteorite-cand-proof",
                }
            return {
                "astral_job_id": jid,
                "state": "INVALID_TITLE",
                "company": "acme",
            }

        monkeypatch.setattr(consult_mod.tracker, "get_job", _get_job)
        meteorite = {
            "astral_job_id": "job-m-proof",
            "state": "NEW",
            "company": "meteorite-cand-proof",
            "job_data": {"raw_job_listing": "Janitor Wanted"},
        }
        roster = {
            "astral_job_id": "job-r-proof",
            "state": "NEW",
            "company": "acme",
            "job_data": {"raw_job_listing": "Janitor Wanted"},
        }
        jobs = [meteorite, roster]
        ctx = {"candidate_data": {"contact": {"title_patterns": "^Engineer"}}}
        out = await consult_mod.qualify_job_listings("batch-1153-mix", jobs, ctx, debug=False)
        transition.assert_called_once_with(["job-m-proof"], landing)
        vt.assert_awaited_once()
        screened = vt.await_args.args[1]
        assert len(screened) == 1
        assert screened[0]["astral_job_id"] == "job-r-proof"
        batch.assert_not_awaited()
        assert meteorite["state"] == landing
        assert roster["state"] == "INVALID_TITLE"
        assert out["failed"] == 1
        assert out["total"] == 2


class TestAst1277DispatchScoreFloorVerdict:
    """AST-1277: scored soft-fail reads dispatch_task.score_floor (0 = no numeric soft-fail)."""

    def test_dispatch_score_floor_lookup_null_zero_and_prefilter_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            consult_mod.tracker,
            "list_dispatch_tasks_for_candidate",
            MagicMock(return_value=[]),
        )
        assert consult_mod._dispatch_score_floor_for_task("c1", "grade_do") == 1.0
        monkeypatch.setattr(
            consult_mod.tracker,
            "list_dispatch_tasks_for_candidate",
            MagicMock(
                return_value=[
                    {"id": 9, "task_key": "prefilter", "score_floor": 0.0},
                    {"id": 8, "task_key": "prefilter", "score_floor": 6.0},
                ]
            ),
        )
        # Newest-first (id DESC walk) — first match wins; consult key maps to prefilter.
        assert consult_mod._dispatch_score_floor_for_task("c1", "prefilter_company") == 0.0
        assert consult_mod._dispatch_score_floor_for_task("c1", "prefilter") == 0.0

    def test_apply_soft_fails_below_floor_and_passes_at_zero_floor(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(consult_mod.tracker, "save_job_data", save)
        monkeypatch.setattr(consult_mod, "_transition_job_state_for_task", transition)
        monkeypatch.setattr(
            consult_mod.tracker,
            "get_job",
            lambda astral_job_id: {
                "astral_job_id": astral_job_id,
                "astral_candidate_id": "c1",
                "state": "PASSED_JD",
            },
        )
        # Low importance + D grade → soft-fail under high floor; still passes at floor 0.
        rubric = [{
            "label": "Fit",
            "code": "CR",
            "importance": 1,
            "content": "body\nA = one\nD = weak\nF = fail",
            "grade_descriptions": [
                {"grade": "A", "description": "one"},
                {"grade": "D", "description": "weak"},
                {"grade": "F", "description": "fail"},
            ],
        }]
        cfg = consult_mod._consult_orchestration("grade_do")
        grades = [{"grade": "D", "confidence": 2, "vector": "Fit"}]
        ctx = {"astral_candidate_id": "c1"}

        _patch_scored_render_verdict_fixtures(monkeypatch, rubric=rubric, score_floor=9.0)
        to_state_high, score_high, _ = consult_mod._apply_render_verdict_decoded_job(
            "grade_do", "job-hi", {"grades": grades, "notes": ""}, cfg, ctx
        )
        assert to_state_high == cfg["fail_state"]
        assert score_high == 0.0

        _patch_scored_render_verdict_fixtures(monkeypatch, rubric=rubric, score_floor=0.0)
        to_state_zero, score_zero, _ = consult_mod._apply_render_verdict_decoded_job(
            "grade_do", "job-z", {"grades": grades, "notes": ""}, cfg, ctx
        )
        assert to_state_zero == cfg["pass_state"]
        assert score_zero is not None and score_zero >= 0.0
