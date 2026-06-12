"""Component tests for src/core/gazer.py (AST-393)."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import gazer as gazer_mod

_OK_JD = "role summary " + ("detail " * 120)


# Branches: skip empty needles; tail vs head pruning.
class TestPruneJd:
    def test_trims_tail_boilerplate(self) -> None:
        text = "keep this equal opportunity junk"
        assert gazer_mod._prune_jd(text).startswith("keep this")

    def test_leaves_unmatched_text_unchanged(self) -> None:
        text = "plain description without prune markers"
        assert gazer_mod._prune_jd(text) == text

    def test_applies_tail_and_head_rules_in_order(self) -> None:
        text = "intro Engineer keep body apply for this extra"
        assert gazer_mod._prune_jd(text, "Engineer") == "Engineer keep body"

    def test_skips_unknown_prune_rule_types(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cfg = dict(gazer_mod.TRACKER_CONFIG)
        cfg["jd_prune_rules"] = [{"prune_text": "marker", "prune_type": "middle"}]
        monkeypatch.setattr(gazer_mod, "TRACKER_CONFIG", cfg)
        assert gazer_mod._prune_jd("before marker after") == "before marker after"

class TestClassifyJd:
    def test_detects_closed_posting(self) -> None:
        assert gazer_mod._classify_jd("role no longer available") == "closed"

    def test_detects_bot_wall(self) -> None:
        text = "Access Denied verify you are human " + ("x " * 200)
        assert gazer_mod._classify_jd(text) == "bot"

    def test_detects_cookie_wall(self) -> None:
        text = "we use cookies cookie policy Accept all " + ("y " * 50)
        assert gazer_mod._classify_jd(text) == "cookie"

    def test_detects_short_cookie_wall(self) -> None:
        text = "we use cookies"
        assert gazer_mod._classify_jd(text) == "cookie"

    def test_detects_missing_page(self) -> None:
        assert gazer_mod._classify_jd("tiny") == "missing"

    def test_detects_whitespace_shell(self) -> None:
        text = (" " * 1000) + " ".join(["word"] * 150)
        assert gazer_mod._classify_jd(text) == "missing"

    def test_detects_job_board_date_stamps(self) -> None:
        text = " ".join(["May 1, 2026"] * 6) + (" detail" * 120)
        assert gazer_mod._classify_jd(text) == "missing"

    def test_accepts_long_clean_text(self) -> None:
        assert gazer_mod._classify_jd(_OK_JD) == "ok"


class TestCompiledTitlePatterns:
    def test_returns_empty_for_bad_context(self) -> None:
        assert gazer_mod._compiled_title_patterns({"candidate_data": "bad"}) == []

    def test_returns_empty_for_non_dict_profile(self) -> None:
        assert gazer_mod._compiled_title_patterns({"candidate_data": {"profile": "bad"}}) == []

    def test_skips_invalid_regex_lines(self) -> None:
        ctx = {"candidate_data": {"profile": {"title_patterns": "[unclosed"}}}
        assert gazer_mod._compiled_title_patterns(ctx) == []

    def test_reads_title_patterns_alias(self) -> None:
        ctx = {"candidate_data": {"profile": {"TITLE_PATTERNS": "engineer"}}}
        assert len(gazer_mod._compiled_title_patterns(ctx)) == 1

    def test_coerces_falsy_pattern_source(self) -> None:
        ctx = {"candidate_data": {"profile": {"title_patterns": 0}}}
        assert gazer_mod._compiled_title_patterns(ctx) == []

    def test_coerces_truthy_non_string_pattern_source(self) -> None:
        ctx = {"candidate_data": {"profile": {"title_patterns": ("engineer",)}}}
        assert len(gazer_mod._compiled_title_patterns(ctx)) == 1

    def test_skips_blank_pattern_lines(self) -> None:
        ctx = {"candidate_data": {"profile": {"title_patterns": "\nengineer\n"}}}
        assert len(gazer_mod._compiled_title_patterns(ctx)) == 1

    def test_compiles_valid_patterns(self) -> None:
        ctx = {"candidate_data": {"profile": {"title_patterns": "engineer\n"}}}
        patterns = gazer_mod._compiled_title_patterns(ctx)
        assert len(patterns) == 1
        assert patterns[0].search("senior engineer role")


class TestValidateTitleBatch:
    @pytest.mark.asyncio
    async def test_marks_all_valid_without_patterns(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        jobs = [{"astral_job_id": "job-1", "job_data": {"raw_job_listing": "anything"}}]
        out = await gazer_mod.validate_title_batch("batch-1", jobs, {"candidate_data": {}}, debug=True)
        assert out == {"passed": 1, "failed": 0, "total": 1}
        transition.assert_called_once_with(["job-1"], "VALID_TITLE")

    @pytest.mark.asyncio
    async def test_coerces_non_string_listing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        jobs = [{"astral_job_id": "job-3", "job_data": {"raw_job_listing": 123}}]
        out = await gazer_mod.validate_title_batch("batch-1", jobs, {"candidate_data": {}})
        assert out["passed"] == 1

    @pytest.mark.asyncio
    async def test_rejects_non_matching_listing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        ctx = {"candidate_data": {"profile": {"title_patterns": "engineer"}}}
        jobs = [{"astral_job_id": "job-2", "job_data": {"raw_job_listing": "janitor"}}]
        out = await gazer_mod.validate_title_batch("batch-1", jobs, ctx, debug=True)
        assert out["failed"] == 1
        transition.assert_called_once_with(["job-2"], "INVALID_TITLE")

    @pytest.mark.asyncio
    async def test_rejects_without_debug_logging(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        ctx = {"candidate_data": {"profile": {"title_patterns": "engineer"}}}
        jobs = [{"astral_job_id": "job-8", "job_data": {"raw_job_listing": "janitor"}}]
        out = await gazer_mod.validate_title_batch("batch-1", jobs, ctx, debug=False)
        assert out["failed"] == 1


class TestScrapeJdBatch:
    @pytest.mark.asyncio
    async def test_aborts_without_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.scrape_jd_batch("batch-1", [])

    @pytest.mark.asyncio
    async def test_handles_missing_link_and_scrape_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(side_effect=RuntimeError("boom")))
        jobs = [
            {"astral_job_id": "job-1", "job_link": ""},
            {"astral_job_id": "job-2", "job_link": "https://example.com/j", "job_title": "Role"},
        ]
        out = await gazer_mod.scrape_jd_batch("batch-1", jobs)
        assert out == {"passed": 0, "failed": 2, "total": 2}
        assert transition.call_count == 2

    @pytest.mark.asyncio
    async def test_routes_classified_failures_and_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "save_job_data", save)
        monkeypatch.setattr(gazer_mod, "_classify_jd", MagicMock(side_effect=["cookie", "ok"]))
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(return_value=_OK_JD))
        jobs = [
            {"astral_job_id": "job-3", "job_link": "https://example.com/a", "job_title": "A"},
            {"astral_job_id": "job-4", "job_link": "https://example.com/b", "job_title": "B", "job_data": None},
        ]
        out = await gazer_mod.scrape_jd_batch("batch-1", jobs, debug=True)
        assert out == {"passed": 1, "failed": 1, "total": 2}
        save.assert_called()
        assert jobs[1]["job_data"]["job_description"].startswith("role summary")

    @pytest.mark.asyncio
    async def test_fails_empty_and_short_job_descriptions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(side_effect=["   ", "short text"]))
        jobs = [
            {"astral_job_id": "job-5", "job_link": "https://example.com/c"},
            {"astral_job_id": "job-6", "job_link": "https://example.com/d", "job_title": "Role"},
        ]
        out = await gazer_mod.scrape_jd_batch("batch-1", jobs)
        assert out["failed"] == 2

    @pytest.mark.asyncio
    async def test_passes_with_existing_job_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "save_job_data", MagicMock())
        monkeypatch.setattr(gazer_mod, "_classify_jd", MagicMock(return_value="ok"))
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(return_value=_OK_JD))
        job = {"astral_job_id": "job-7", "job_link": "https://example.com/z", "job_title": "Role", "job_data": {"note": "keep"}}
        out = await gazer_mod.scrape_jd_batch("batch-1", [job], debug=False)
        assert out == {"passed": 1, "failed": 0, "total": 1}
        assert job["job_data"]["note"] == "keep"


class TestScrapeOne:
    @pytest.mark.asyncio
    async def test_returns_page_dom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        page = AsyncMock()
        page.close = AsyncMock()
        context = AsyncMock()

        @asynccontextmanager
        async def _browser():
            yield context

        monkeypatch.setattr(gazer_mod, "create_browser_context", _browser)
        monkeypatch.setattr(gazer_mod, "get_page", AsyncMock(return_value=page))
        monkeypatch.setattr(gazer_mod, "load_all_jobs", AsyncMock())
        monkeypatch.setattr(gazer_mod, "extract_page_dom", AsyncMock(return_value="<html>dom</html>"))

        short_name, job_site, dom = await gazer_mod.scrape_one("co", "https://example.com/jobs")
        assert (short_name, job_site, dom) == ("co", "https://example.com/jobs", "<html>dom</html>")
        page.close.assert_awaited_once()


class TestProcessGazerBatch:
    @pytest.mark.asyncio
    async def test_aborts_without_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.process_gazer_batch("batch-1", [])

    @pytest.mark.asyncio
    async def test_records_scrape_parse_and_ingest_outcomes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(
            gazer_mod,
            "scrape_one",
            AsyncMock(side_effect=[
                ("goodco", "https://example.com/good", "<html>good</html>"),
                RuntimeError("scrape failed"),
                ("noparse", "https://example.com/noparse", "<html>noparse</html>"),
            ]),
        )

        async def _company_data(company: Dict[str, Any], key: str) -> Dict[str, Any]:
            if company["short_name"] == "goodco":
                return {"container": "motion", "job_tag": "a", "container_index": 0}
            return {}

        monkeypatch.setattr(gazer_mod, "get_company_data", _company_data)
        monkeypatch.setattr(gazer_mod, "extract_raw_job_listings", MagicMock(return_value=["listing"]))
        monkeypatch.setattr(
            gazer_mod,
            "ingest_jobs",
            MagicMock(side_effect=RuntimeError("ingest failed")),
        )
        record = MagicMock()
        update_scan = MagicMock()
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", record)
        monkeypatch.setattr(gazer_mod, "update_company_last_scan_at", update_scan)

        companies = [
            {"short_name": "goodco", "job_site": "https://example.com/good"},
            {"short_name": "badco", "job_site": "https://example.com/bad"},
            {"short_name": "noparse", "job_site": "https://example.com/noparse"},
            {"short_name": "", "job_site": "https://example.com/ignored"},
        ]

        outcomes = await gazer_mod.process_gazer_batch("batch-1", companies, debug=True)

        statuses = {row["short_name"]: row["status"] for row in outcomes}
        assert statuses["goodco"] == "failure"
        assert statuses["badco"] == "failure"
        assert statuses["noparse"] == "failure"
        update_scan.assert_not_called()
        assert record.call_count >= 3

    @pytest.mark.asyncio
    async def test_records_successful_ingest(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(
            gazer_mod,
            "scrape_one",
            AsyncMock(return_value=("goodco", "https://example.com/good", "<html>good</html>")),
        )

        async def _company_data(company: Dict[str, Any], key: str) -> Dict[str, Any]:
            return {"container": "motion", "job_tag": "a", "container_index": 0}

        monkeypatch.setattr(gazer_mod, "get_company_data", _company_data)
        monkeypatch.setattr(gazer_mod, "extract_raw_job_listings", MagicMock(return_value=["listing"]))
        monkeypatch.setattr(
            gazer_mod,
            "ingest_jobs",
            MagicMock(return_value={"new": 2, "duplicates": 1, "title_mismatch": 0}),
        )
        record = MagicMock()
        update_scan = MagicMock()
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", record)
        monkeypatch.setattr(gazer_mod, "update_company_last_scan_at", update_scan)

        outcomes = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "goodco", "job_site": "https://example.com/good"}],
            debug=True,
        )

        assert outcomes[0]["status"] == "success"
        assert outcomes[0]["new"] == 2
        update_scan.assert_called_once_with("goodco")


class TestProcessGazeBoardBatch:
    @pytest.mark.asyncio
    async def test_success_failure_and_skips_empty_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        gaze = AsyncMock(
            side_effect=[
                {"board_search_id": "bs-1", "new": 2, "duplicates": 0, "invalid_title": 0},
                RuntimeError("scrape failed"),
            ]
        )
        monkeypatch.setattr("src.core.boards.run_board_search_gaze", gaze)
        set_state = MagicMock()
        monkeypatch.setattr(gazer_mod, "set_board_search_state", set_state)
        bump_scan = MagicMock()
        monkeypatch.setattr(gazer_mod, "update_board_search_last_scan_at", bump_scan)

        searches: List[Dict[str, Any]] = [
            {"board_search_id": "bs-1", "board_key": "a16z"},
            {"board_search_id": "bs-2", "board_key": "a16z"},
            {"board_key": "a16z"},
        ]
        outcomes = await gazer_mod.process_gaze_board_batch(
            "batch-board", searches, debug=False, ctx={}
        )

        assert len(outcomes) == 2
        assert outcomes[0]["status"] == "success"
        assert outcomes[0]["new"] == 2
        assert outcomes[1]["status"] == "failure"
        assert "scrape failed" in outcomes[1]["error"]
        set_state.assert_any_call("bs-1", "ACTIVE")
        set_state.assert_any_call("bs-2", "ERROR")
        assert gaze.await_count == 2
        bump_scan.assert_called_once_with("bs-1")

    @pytest.mark.asyncio
    async def test_logs_error_on_gaze_failure(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        gaze = AsyncMock(side_effect=RuntimeError("boom"))
        monkeypatch.setattr("src.core.boards.run_board_search_gaze", gaze)
        monkeypatch.setattr(gazer_mod, "set_board_search_state", MagicMock())
        monkeypatch.setattr(gazer_mod, "update_board_search_last_scan_at", MagicMock())

        searches: List[Dict[str, Any]] = [{"board_search_id": "bs-2", "board_key": "a16z"}]
        caplog.clear()
        with caplog.at_level(logging.ERROR, logger="src.core.gazer"):
            await gazer_mod.process_gaze_board_batch("batch-board", searches, debug=False)
        joined = "\n".join(r.getMessage() for r in caplog.records)
        assert "bs-2" in joined
        assert "a16z" in joined
        assert "boom" in joined
