"""Logging refactor: clean PASS/FAIL verdicts at INFO, could-not-process at WARNING,
ERROR only for our own code/infra, tracebacks and failed envelopes at DEBUG."""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import agent as agent_mod
from src.core import consult as consult_mod
from src.core import roster as roster_mod
from src.utils.logging import get_logger, log_debug


def _levels(caplog: pytest.LogCaptureFixture, needle: str) -> list[str]:
    return [r.levelname for r in caplog.records if needle in r.getMessage()]


class TestExcHelpers:
    """warn_exc / error_exc: one-liner at the level, traceback only at DEBUG (gated by log_debug)."""

    @pytest.mark.parametrize(("method", "level"), [("warn_exc", "WARNING"), ("error_exc", "ERROR")])
    def test_no_traceback_when_debug_off(self, caplog: pytest.LogCaptureFixture, method: str, level: str) -> None:
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.logmod.off")
        token = log_debug.set(False)
        try:
            try:
                raise ValueError("kaboom")
            except ValueError:
                getattr(logger, method)("thing failed\n  ValueError: kaboom")
        finally:
            log_debug.reset(token)
        records = [r for r in caplog.records if r.name == "test.logmod.off"]
        assert [r.levelname for r in records] == [level]
        assert records[0].exc_info is None

    @pytest.mark.parametrize(("method", "level"), [("warn_exc", "WARNING"), ("error_exc", "ERROR")])
    def test_traceback_rides_debug(self, caplog: pytest.LogCaptureFixture, method: str, level: str) -> None:
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.logmod.on")
        token = log_debug.set(True)
        try:
            try:
                raise ValueError("kaboom")
            except ValueError:
                getattr(logger, method)("thing failed")
        finally:
            log_debug.reset(token)
        records = [r for r in caplog.records if r.name == "test.logmod.on"]
        assert [r.levelname for r in records] == [level, "DEBUG"]
        assert records[0].exc_info is None
        assert "Traceback (most recent call last)" in records[1].getMessage()
        assert "ValueError: kaboom" in records[1].getMessage()

    def test_exc_info_instance_from_gather(self, caplog: pytest.LogCaptureFixture) -> None:
        # asyncio.gather(return_exceptions=True) hands back instances, not an active except block.
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.logmod.gather")
        token = log_debug.set(True)
        try:
            logger.error_exc("entity failed", exc_info=RuntimeError("from gather"))
        finally:
            log_debug.reset(token)
        records = [r for r in caplog.records if r.name == "test.logmod.gather"]
        assert [r.levelname for r in records] == ["ERROR", "DEBUG"]
        assert "RuntimeError: from gather" in records[1].getMessage()


class TestVetPassFailLogging:
    @pytest.mark.asyncio
    async def test_pass_fail_info_and_missing_row_warning(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level(logging.DEBUG)
        # Model returns rows 0 and 1 only: co_c has no row (the original unlogged "1 error").
        monkeypatch.setattr(roster_mod, "do_task", AsyncMock(return_value={
            "success": True,
            "parsed_response": {"results": [
                {"hit_index": 0, "grade": "A", "website": "https://a.example"},
                {"hit_index": 1, "grade": "F", "website": "https://b.example"},
            ]},
        }))
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(roster_mod, "update_company", MagicMock())
        companies = [
            {"short_name": n, "company_data": {"inflow_discovery_blurb": f"000|{n}|https://{n}.example|s"}}
            for n in ("co_a", "co_b", "co_c")
        ]
        out = await roster_mod.vet_inflow_discovery_company_batch("b1", companies, debug=False)
        assert out == {"passed": 1, "failed": 1, "skipped": 0, "total": 3}
        assert _levels(caplog, "co_a | company PASS") == ["INFO"]
        assert _levels(caplog, "co_b | company FAIL") == ["INFO"]
        assert _levels(caplog, "co_c -> - [missing results row hit_index=2]") == ["WARNING"]
        # A graded F is a verdict, not a warning; nothing here is ours to fix, so no ERROR.
        assert "WARNING" not in _levels(caplog, "co_b")
        assert not [r for r in caplog.records if r.levelno >= logging.ERROR]

    def test_missing_website_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        r = roster_mod._apply_vet_inflow_result_row(
            "co_x", {"grade": "A", "website": ""}, roster_mod.INFLOW_CONFIG["vet"], None, False, index=1, total=1,
        )
        assert r["error"] == "missing website"
        assert _levels(caplog, "co_x -> - [missing website]") == ["WARNING"]


class TestPrefilterPassFailLogging:
    """prefilter_company is a rubric task: its verdicts log INFO PASS/FAIL (same split as the batch tally)."""

    @staticmethod
    def _env(monkeypatch: pytest.MonkeyPatch, decomposed: bool) -> None:
        rubric = [{"label": "fit", "code": "fit", "importance": 5, "content": "body",
                   "grade_descriptions": [{"grade": "A", "description": "one"}, {"grade": "F", "description": "fail"}]}]
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value={"state_history": []}))
        monkeypatch.setattr(roster_mod, "_company_on_decomposed_pjl_path", lambda *a, **k: decomposed)
        monkeypatch.setattr("src.core.candidate.rubric_criteria_for_task", lambda *_a, **_k: rubric)
        monkeypatch.setattr("src.core.consult._dispatch_score_floor_for_task", lambda *_a, **_k: 0.0)

    @staticmethod
    def _apply(grade: str) -> str:
        return roster_mod._apply_prefilter_decoded_company_outcome(
            "acme_com",
            {"grades": [{"vector": "fit", "grade": grade, "confidence": 5}], "possible_job_links": []},
            {**roster_mod.ROSTER_CONFIG["prefilter"]},
            {"astral_candidate_id": "c1"},
        )

    def test_pass_and_fail_verdicts_are_info(self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        self._env(monkeypatch, decomposed=False)
        assert self._apply("A") == "TO_WATCH"
        assert self._apply("F") == "IGNORE"
        assert _levels(caplog, "acme_com | company PASS: TO_WATCH") == ["INFO"]
        assert _levels(caplog, "acme_com | company FAIL: IGNORE [fit]") == ["INFO"]
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]

    def test_no_joblist_links_is_a_fail_line(self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
        # Passed the rubric but no job links: the batch tally counts it failed, so it logs FAIL (not PASS).
        caplog.set_level(logging.INFO)
        self._env(monkeypatch, decomposed=True)
        state = self._apply("A")
        assert state == roster_mod.ROSTER_CONFIG["prefilter"]["no_pjl_state"]
        assert _levels(caplog, f"acme_com | company FAIL: {state} [no joblist links]") == ["INFO"]


class TestJobPassFailInfo:
    def test_pass_and_fail_lines_are_info(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        consult_mod._job_consult_pass("job-1", "PASSED_JD")
        consult_mod._job_consult_fail("job-2", "FAILED_JD", "fit, pay")
        assert _levels(caplog, "job-1 | job PASS: PASSED_JD") == ["INFO"]
        assert _levels(caplog, "job-2 | job FAIL: FAILED_JD [fit, pay]") == ["INFO"]

    def test_non_rubric_hops_keep_consult_completed(self, caplog: pytest.LogCaptureFixture) -> None:
        # Upshot / craft hops aren't rubric verdicts — their line is unchanged.
        caplog.set_level(logging.INFO)
        consult_mod._job_consult_info("job-4", "RECOMMENDED")
        assert _levels(caplog, "job-4 | job consult completed: RECOMMENDED") == ["INFO"]

    def test_fail_dest_is_warning_never_error(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        consult_mod._log_fail_dest("job-3", "ERROR_GRADE_DO", "do_task failed")
        roster_mod._log_fail_dest("co_3", "ERROR_PREFILTER_COMPANY", "do_task failed")
        assert _levels(caplog, "job-3 -> ERROR_GRADE_DO") == ["WARNING"]
        assert _levels(caplog, "co_3 -> ERROR_PREFILTER_COMPANY") == ["WARNING"]


class TestFailedEnvelopeDebug:
    def test_envelope_detail_at_debug_only(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)
        envelope: Any = {
            "agent_performance": {"status": "failure", "failure_note": "bad source"},
            "agent_payload": {},
        }
        token = log_debug.set(True)
        try:
            agent_mod._warn_hop_no_success("evaluate_jd", "Agent failure: bad source", envelope)
        finally:
            log_debug.reset(token)
        assert _levels(caplog, "evaluate_jd skipped") == ["WARNING"]
        dbg = [r for r in caplog.records if r.levelname == "DEBUG" and "failed envelope" in r.getMessage()]
        assert len(dbg) == 1 and "bad source" in dbg[0].getMessage()

    def test_no_envelope_no_debug_line(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)
        token = log_debug.set(True)
        try:
            agent_mod._warn_hop_no_success("evaluate_jd", "provider failed: x")
        finally:
            log_debug.reset(token)
        assert not [r for r in caplog.records if "failed envelope" in r.getMessage()]
