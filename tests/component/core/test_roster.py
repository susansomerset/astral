"""Component tests for src/core/roster.py (AST-393)."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from src.core import roster as roster_mod
from src.utils.config import COMPANY_STATES, ROSTER_CONFIG, TASK_CONFIG


def _prefilter_rubric_ctx(*, multi_vector: bool = False) -> Dict[str, Any]:
    # AST-603: prefilter hydrates reasons from rubric — include F for dealbreaker tests.
    criteria = [
        {
            "label": "fit",
            "content": "body\nA = one\nB = two\nF = fail",
            "importance": 5,
            "code": "fit",
            "grade_descriptions": [
                {"grade": "A", "description": "one"},
                {"grade": "F", "description": "fail"},
            ],
        },
    ]
    if multi_vector:
        criteria.append(
            {
                "label": "culture",
                "content": "body\nA = one\nB = two",
                "importance": 3,
                "code": "culture",
                "grade_descriptions": [{"grade": "A", "description": "one"}],
            },
        )
    return {"candidate_data": {"artifacts": {"company_prefilter": criteria}}}


def _artifact_mp_us_only_ctx() -> Dict[str, Any]:
    """AST-707 UAT repro: company_prefilter artifact without RC (embedded supplies RC)."""
    return {
        "candidate_data": {
            "artifacts": {
                "company_prefilter": [
                    {
                        "code": "MP",
                        "label": "Mission & Product",
                        "importance": 5,
                        "grade_descriptions": [{"grade": "B", "description": "ok mp"}],
                    },
                    {
                        "code": "US",
                        "label": "US Presence",
                        "importance": 3,
                        "grade_descriptions": [{"grade": "A", "description": "us ok"}],
                    },
                ]
            }
        }
    }


def _ast603_prefilter_rubric_ctx() -> Dict[str, Any]:
    """Three-vector company_prefilter matching AST-602 repro alias keys."""
    return {
        "candidate_data": {
            "artifacts": {
                "company_prefilter": [
                    {
                        "label": "Reality Check",
                        "code": "RC",
                        "content": "body\nA = real\nB = ok",
                        "importance": 5,
                        "grade_descriptions": [{"grade": "A", "description": "real company"}],
                    },
                    {
                        "label": "Mission Product Orientation",
                        "code": "MP",
                        "content": "body\nA = aligned\nB = ok",
                        "importance": 5,
                        "grade_descriptions": [{"grade": "B", "description": "decent fit"}],
                    },
                    {
                        "label": "US Presence",
                        "code": "UP",
                        "content": "body\nA = us\nB = ok",
                        "importance": 3,
                        "grade_descriptions": [{"grade": "A", "description": "US based"}],
                    },
                ]
            }
        }
    }


def _encoded_prefilter_response(grades: List[Dict[str, Any]], **job_extra: Any) -> Dict[str, Any]:
    job: Dict[str, Any] = {"grades": grades}
    job.update(job_extra)
    return {"jobs": [job]}


_RC_VECTOR = "Reality Check"
_RC_REASON = "Company is clearly real, active, and independently verifiable."


def _rc_grade(grade: str = "A", confidence: int = 5, reason: str = "") -> Dict[str, Any]:
    row: Dict[str, Any] = {"grade": grade, "vector": _RC_VECTOR, "confidence": confidence}
    if reason:
        row["reason"] = reason
    return row


def _prefilter_grades(*rows: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Embedded RC (AST-707) plus artifact vectors for company_prefilter mocks."""
    if any(r.get("vector") == _RC_VECTOR for r in rows):
        return list(rows)
    return [_rc_grade()] + list(rows)


def _patch_prefilter_candidate_rubric(monkeypatch: pytest.MonkeyPatch) -> None:
    """Coat-check paths load rubric from candidate artifacts when candidate_id is set."""
    monkeypatch.setattr(
        "src.core.candidate.get_candidate",
        MagicMock(return_value=_prefilter_rubric_ctx().get("candidate_data") or {}),
    )


def _hydrated_prefilter_notes(*, include_fit: bool = False) -> str:
    parts = [f"Reality Check=A: {_RC_REASON}"]
    if include_fit:
        parts.append("fit=A: one")
    return " | ".join(parts)


def _prefilter_nav_urls() -> List[str]:
    return ["https://Acme.com/careers/"]


def _patch_prefilter_scrape_with_nav(
    monkeypatch: pytest.MonkeyPatch, urls: Optional[List[str]] = None
) -> None:
    nav = urls if urls is not None else _prefilter_nav_urls()
    monkeypatch.setattr(
        roster_mod, "get_visible_text", AsyncMock(return_value=("hello", "https://acme.com"))
    )
    monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=nav))
    monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())


def _company(
    short_name: str = "acme",
    *,
    company_website: str = "https://www.acme.com",
    company_data: Optional[Dict[str, Any]] = None,
    state: str = "WEBSITE_FOUND",
    state_history: Optional[List[Dict[str, str]]] = None,
    job_site: Optional[str] = None,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "short_name": short_name,
        "company_website": company_website,
        "company_data": company_data or {},
        "state": state,
        "state_history": state_history if state_history is not None else [],
        "batch_id": "batch-1",
    }
    if job_site is not None:
        row["job_site"] = job_site
    return row


class TestExtractCompanyName:
    def test_returns_none_for_empty_url(self) -> None:
        assert roster_mod._extract_company_name_from_url(None) is None
        assert roster_mod._extract_company_name_from_url("") is None

    def test_parses_domain_and_strips_www(self) -> None:
        assert roster_mod._extract_company_name_from_url("https://www.acme.com/jobs") == "Acme"
        assert roster_mod._extract_company_name_from_url("acme.co.uk") == "Co"

    def test_handles_single_part_domain(self) -> None:
        assert roster_mod._extract_company_name_from_url("https://localhost/path") == "Localhost"

    def test_swallows_parse_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _boom(_url: str) -> None:
            raise RuntimeError("parse failed")

        monkeypatch.setattr(roster_mod, "urlparse", _boom)
        assert roster_mod._extract_company_name_from_url("https://acme.com") is None


class TestSaveCompanyData:
    def test_replace_overwrites_company_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        roster_mod.save_company_data("acme", {"nav_links": "1. /"}, replace=True)
        update.assert_called_once_with("acme", company_data={"nav_links": "1. /"})

    def test_merge_raises_when_company_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=None))
        with pytest.raises(ValueError, match="Company not found"):
            roster_mod.save_company_data("missing", {"nav_links": "1. /"})

    def test_merge_updates_existing_company_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(return_value={"company_data": {"prefilter_company_notes": "old"}}),
        )
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        roster_mod.save_company_data("acme", {"nav_links": "1. /"})
        update.assert_called_once_with(
            "acme",
            company_data={"prefilter_company_notes": "old", "nav_links": "1. /"},
        )


class TestTransitionCompanyState:
    def test_appends_history_and_updates_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company()
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        roster_mod.transition_company_state("acme", "TO_WATCH")
        update.assert_called_once()
        assert update.call_args.kwargs["state"] == "TO_WATCH"
        assert update.call_args.kwargs["state_history"][-1]["to_state"] == "TO_WATCH"

    def test_no_logger_when_transitioning_to_current_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(state="TO_WATCH")
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        roster_mod.transition_company_state("acme", "TO_WATCH")
        update.assert_called_once()
        assert update.call_args.kwargs["state"] == "TO_WATCH"

    def test_rejects_missing_company(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=None))
        with pytest.raises(ValueError, match="Company not found"):
            roster_mod.transition_company_state("acme", "TO_WATCH")


class TestBatchApi:
    def test_get_new_company_batch_requires_batch_id_or_context(self) -> None:
        with pytest.raises(ValueError, match="batch_id or context"):
            roster_mod.get_new_company_batch("WEBSITE_FOUND")

    def test_get_new_company_batch_rejects_unknown_state(self) -> None:
        with pytest.raises(ValueError, match="state must be one of"):
            roster_mod.get_new_company_batch("NOT_A_STATE", context="ctx")

    def test_get_new_company_batch_claims_and_returns_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        claim = MagicMock()
        monkeypatch.setattr(roster_mod, "claim_company_batch", claim)
        rows = [_company()]
        monkeypatch.setattr(roster_mod, "get_company_batch", MagicMock(return_value=rows))
        bid, companies = roster_mod.get_new_company_batch(
            "WEBSITE_FOUND",
            limit=3,
            candidate_id="cand-1",
            batch_id="batch-9",
            sort_by="not-a-column",
            scan_interval_hours=0,
        )
        assert bid == "batch-9"
        assert companies == rows
        claim.assert_called_once_with(
            "batch-9",
            "WEBSITE_FOUND",
            3,
            sort_by="updated_at",
            scan_interval_hours=None,
            candidate_id="cand-1",
            require_empty_website=False,
            score_floor=None,
            states=None,
        )

    def test_get_new_company_batch_generates_batch_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "claim_company_batch", MagicMock())
        monkeypatch.setattr(roster_mod, "get_company_batch", MagicMock(return_value=[]))
        bid, _ = roster_mod.get_new_company_batch("WEBSITE_FOUND", context="roster")
        assert bid.startswith("roster-")

    def test_get_new_company_batch_honors_positive_scan_interval(self, monkeypatch: pytest.MonkeyPatch) -> None:
        claim = MagicMock()
        monkeypatch.setattr(roster_mod, "claim_company_batch", claim)
        monkeypatch.setattr(roster_mod, "get_company_batch", MagicMock(return_value=[]))
        roster_mod.get_new_company_batch("WEBSITE_FOUND", context="roster", scan_interval_hours=12)
        assert claim.call_args.kwargs["scan_interval_hours"] == 12

    def test_clear_company_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        clear = MagicMock(return_value=2)
        monkeypatch.setattr(roster_mod, "set_company_batch", clear)
        assert roster_mod.clear_company_batch("batch-1") == 2
        clear.assert_called_once_with("batch-1", clear=True)


class TestDeriveShortname:
    def test_lowercases_domain(self) -> None:
        assert roster_mod._derive_shortname_from_url("https://WWW.Acme.com/careers") == "acme"

    def test_handles_single_part_host(self) -> None:
        assert roster_mod._derive_shortname_from_url("https://localhost/jobs") == "localhost"

    def test_raises_when_url_unparseable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _boom(_url: str) -> None:
            raise RuntimeError("bad")

        monkeypatch.setattr(roster_mod, "urlparse", _boom)
        with pytest.raises(ValueError, match="Failed to derive shortname"):
            roster_mod._derive_shortname_from_url("not-a-url")


class TestAst469LocateParseResolver:
    def test_make_locate_parse_resolver_returns_culled_dom_and_visible(self) -> None:
        """Hedy tuple contract (dom_map, visible_map) → (culled_fragments, stripped visible text)."""
        dom = "<motion class='jobs'><a>Engineer opening</a></motion>"
        resolver = roster_mod.make_locate_parse_resolver({1: dom}, {1: " Role listing plain "})
        culled, visible = resolver({"selected_page": 1, "job_titles": ["Engineer"]})
        assert "Engineer" in culled
        assert visible == "Role listing plain"


class TestRunCompanyTask:
    @pytest.mark.asyncio
    async def test_website_found_monolithic_dispatch_removed(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-702: scrape+evaluate on WEBSITE_FOUND removed; batch uses HOMEPAGE_READY via consult."""
        prefilter = AsyncMock()
        monkeypatch.setattr(roster_mod, "prefilter_company", prefilter)
        out = await roster_mod.run_company_task(
            "WEBSITE_FOUND", _company(), "batch-1", dispatch_task_key="prefilter",
        )
        assert out["total_errors"] == 1
        prefilter.assert_not_called()

    @pytest.mark.asyncio
    async def test_to_watch_unhandled_after_monolith_removal(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-721: TO_WATCH locate monolith removed; batch rows at TO_WATCH count as errors."""
        entity = _company(state="TO_WATCH")
        out = await roster_mod.run_company_task("TO_WATCH", entity, "batch-1")
        assert out["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_prefilter_passed_unhandled_without_fetch_batch(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-721: PREFILTER_PASSED no longer routes to find_job_page via run_company_task."""
        locate = AsyncMock(return_value={"state": "WATCH"})
        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", locate)
        entity = _company(state="PREFILTER_PASSED")
        out = await roster_mod.run_company_task("PREFILTER_PASSED", entity, "batch-508")
        assert out["total_errors"] == 1
        locate.assert_not_called()

    @pytest.mark.asyncio
    async def test_jobs_found_dispatch_pass_fail_ast469(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AST-469: locate_job_page batch includes JOBS_FOUND → jobs_found_process_job_site."""
        jf_ok = AsyncMock(return_value={"state": "WATCH"})
        jf_err = AsyncMock(return_value={"error": "boom"})
        monkeypatch.setattr(roster_mod, "jobs_found_process_job_site", jf_ok)

        entity = _company(state="JOBS_FOUND", job_site="https://acme.com/jobs")
        ok = await roster_mod.run_company_task("JOBS_FOUND", entity, "batch-jf")
        assert ok["total_passed"] == 1
        jf_ok.assert_awaited_once()

        monkeypatch.setattr(roster_mod, "jobs_found_process_job_site", jf_err)
        tran = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", tran)
        bad = await roster_mod.run_company_task("JOBS_FOUND", entity, "batch-jf2")
        assert bad["total_errors"] == 1
        tran.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_openings_routes_to_recheck_not_find_job_page(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-463: NO_OPENINGS uses process_recheck_no_openings; locate batch is JOBS_FOUND only."""
        recheck_ok = AsyncMock(return_value={"success": True, "message": "ok", "new_state": "NO_OPENINGS"})
        recheck_bad = AsyncMock(return_value={"success": False, "message": "no_jobs_message missing", "new_state": ""})
        monkeypatch.setattr(roster_mod, "process_recheck_no_openings", recheck_ok)
        entity = _company(state="NO_OPENINGS", company_data={"no_jobs_message": "closed"}, job_site="https://acme.com/jobs")
        ok = await roster_mod.run_company_task("NO_OPENINGS", entity, "batch-1")
        assert ok["total_passed"] == 1
        recheck_ok.assert_awaited_once()

        monkeypatch.setattr(roster_mod, "process_recheck_no_openings", recheck_bad)
        bad = await roster_mod.run_company_task("NO_OPENINGS", entity, "batch-2")
        assert bad["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_watch_and_unhandled_states(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _Gazer:
            @staticmethod
            async def process_gazer_batch(
                _bid: str, _entities: List[Dict[str, Any]], debug: bool = False, **_kwargs: Any
            ):
                return [{"status": "success", "message": "ok"}]

        monkeypatch.setitem(__import__("sys").modules, "src.core.gazer", _Gazer)
        passed = await roster_mod.run_company_task("WATCH", _company(), "batch-1")
        assert passed["total_passed"] == 1

        class _GazerFail:
            @staticmethod
            async def process_gazer_batch(
                _bid: str, _entities: List[Dict[str, Any]], debug: bool = False, **_kwargs: Any
            ):
                return [{"status": "failure", "message": "gaze failed"}]

        monkeypatch.setitem(__import__("sys").modules, "src.core.gazer", _GazerFail)
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        errored = await roster_mod.run_company_task("WATCH", _company(), "batch-1")
        assert errored["total_errors"] == 1
        transition.assert_called_once()

        unknown = await roster_mod.run_company_task("IMPORTED", _company(), "batch-1")
        assert unknown["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_website_found_retry_returns_error_without_prefilter(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        prefilter = AsyncMock()
        monkeypatch.setattr(roster_mod, "prefilter_company", prefilter)
        out = await roster_mod.run_company_task("WEBSITE_FOUND_RETRY", _company(), "batch-1")
        assert out["total_errors"] == 1
        prefilter.assert_not_called()


class TestAst721ParseDispatchRouting:
    """AST-721 — JOBLIST_IDENTIFIED / RETRY honor dispatch_task_key parse_job_list."""

    @pytest.mark.asyncio
    async def test_parse_job_list_dispatch_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        parse = AsyncMock(return_value={"state": "WATCH"})
        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", parse)
        entity = _company(state="JOBLIST_IDENTIFIED")
        out = await roster_mod.run_company_task(
            "JOBLIST_IDENTIFIED", entity, "batch-721", dispatch_task_key="parse_job_list",
        )
        assert out["total_passed"] == 1
        parse.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_retry_state_parse_dispatch_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        parse = AsyncMock(return_value={"state": "JOBLIST_IDENTIFIED_RETRY"})
        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", parse)
        entity = _company(state="JOBLIST_IDENTIFIED_RETRY")
        out = await roster_mod.run_company_task(
            "JOBLIST_IDENTIFIED_RETRY", entity, "batch-721", dispatch_task_key="parse_job_list",
        )
        assert out["total_passed"] == 1
        parse.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_wrong_dispatch_task_key_counts_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        parse = AsyncMock()
        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", parse)
        entity = _company(state="JOBLIST_IDENTIFIED")
        out = await roster_mod.run_company_task(
            "JOBLIST_IDENTIFIED", entity, "batch-721", dispatch_task_key="select_job_page",
        )
        assert out["total_errors"] == 1
        parse.assert_not_called()

    @pytest.mark.asyncio
    async def test_to_watch_monolith_routes_removed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        parse = AsyncMock()
        select = AsyncMock()
        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", parse)
        monkeypatch.setattr(roster_mod, "run_select_job_page_dispatch", select)
        entity = _company(state="TO_WATCH")
        for key in ("parse_job_list", "select_job_page", ""):
            out = await roster_mod.run_company_task(
                "TO_WATCH", entity, "batch-535", dispatch_task_key=key or None,
            )
            assert out["total_errors"] == 1
        parse.assert_not_called()
        select.assert_not_called()


class TestProcessRecheckNoOpenings:
    """AST-463 NO_OPENINGS Playwright-only recheck; JOBS_FOUND when no_jobs_message absent from visible text."""

    @staticmethod
    def _browser_cm():
        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        return _browser

    @pytest.mark.asyncio
    async def test_guards_missing_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        base: Dict[str, Any] = {"short_name": "", "job_site": "https://x", "company_data": {"no_jobs_message": "no"}}
        r = await roster_mod.process_recheck_no_openings(base, "b")
        assert r["success"] is False and "short_name" in r["message"]

        base["short_name"] = "co"
        base["job_site"] = ""
        r2 = await roster_mod.process_recheck_no_openings(base, "b")
        assert r2["success"] is False and "job_site" in r2["message"]

        entity = {"short_name": "co", "job_site": "https://j", "company_data": {}}
        r3 = await roster_mod.process_recheck_no_openings(entity, "b")
        assert r3["success"] is False and r3["message"] == "no_jobs_message missing"

    @pytest.mark.asyncio
    async def test_playwright_failure_no_state_change(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "create_browser_context", TestProcessRecheckNoOpenings._browser_cm())

        async def boom(*_a, **_k):
            raise RuntimeError("net down")

        monkeypatch.setattr(roster_mod, "get_visible_text", boom)
        ent = _company(
            short_name="acme",
            company_data={"no_jobs_message": "no openings"},
            job_site="https://acme.com/jobs",
            state="NO_OPENINGS",
        )
        out = await roster_mod.process_recheck_no_openings(ent, "bid")
        assert out["success"] is False
        assert "playwright scrape" in out["message"]

    @pytest.mark.asyncio
    async def test_message_present_updates_scan_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "create_browser_context", TestProcessRecheckNoOpenings._browser_cm())
        monkeypatch.setattr(
            roster_mod,
            "get_visible_text",
            AsyncMock(return_value=("We have no openings right now.", "https://acme.com/jobs")),
        )
        bump = MagicMock()
        tran = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company_last_scan_at", bump)
        monkeypatch.setattr(roster_mod, "transition_company_state", tran)

        ent = _company(
            short_name="acme",
            company_data={"no_jobs_message": "no openings"},
            job_site="https://acme.com/jobs",
            state="NO_OPENINGS",
        )
        out = await roster_mod.process_recheck_no_openings(ent, "bid")
        assert out == {"success": True, "message": "no_jobs_message_present", "new_state": "NO_OPENINGS"}
        bump.assert_called_once_with("acme")
        tran.assert_not_called()

    @pytest.mark.asyncio
    async def test_message_absent_to_jobs_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "create_browser_context", TestProcessRecheckNoOpenings._browser_cm())
        monkeypatch.setattr(
            roster_mod,
            "get_visible_text",
            AsyncMock(return_value=("Apply today for dozens of roles.", "https://acme.com/jobs")),
        )
        bump = MagicMock()
        tran = MagicMock()
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=_company(short_name="acme")))
        monkeypatch.setattr(roster_mod, "update_company", MagicMock())
        monkeypatch.setattr(roster_mod, "update_company_last_scan_at", bump)
        monkeypatch.setattr(roster_mod, "transition_company_state", tran)

        ent = _company(
            short_name="acme",
            company_data={"no_jobs_message": "no openings"},
            job_site="https://acme.com/jobs",
            state="NO_OPENINGS",
        )
        out = await roster_mod.process_recheck_no_openings(ent, "bid")
        assert out == {"success": True, "message": "no_jobs_message_absent", "new_state": "JOBS_FOUND"}
        tran.assert_called_once_with("acme", "JOBS_FOUND")
        bump.assert_called_once_with("acme")

    @pytest.mark.asyncio
    async def test_redirect_normalizes_job_site(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "create_browser_context", TestProcessRecheckNoOpenings._browser_cm())
        monkeypatch.setattr(
            roster_mod,
            "get_visible_text",
            AsyncMock(return_value=("no openings forever", "https://final.example/path")),
        )
        monkeypatch.setattr(roster_mod, "update_company_last_scan_at", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        uc = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", uc)

        ent = _company(
            short_name="acme",
            company_data={"no_jobs_message": "no openings"},
            job_site="https://old.example",
            state="NO_OPENINGS",
        )
        await roster_mod.process_recheck_no_openings(ent, "bid")
        uc.assert_called_once_with("acme", job_site="https://final.example/path")


class TestAst759SharedPageScrapeContract:
    """AST-759: shared page scrape contract + select live content parity."""

    def test_finalize_page_scrape_contract_collapses_and_enumerates(self) -> None:
        raw = {
            "visible_text": "intro\n\n\nbody",
            "nav_urls": ["https://acme.com/jobs"],
            "final_url": "https://acme.com",
        }
        out = roster_mod.finalize_page_scrape_contract(raw)
        assert out["visible_text"] == "intro\n\nbody"
        assert "acme.com/jobs" in out["enumerated_nav_links"]

    def test_finalize_page_scrape_contract_empty_nav(self) -> None:
        out = roster_mod.finalize_page_scrape_contract(
            {"visible_text": "body", "nav_urls": []},
        )
        assert out["enumerated_nav_links"] == ""

    def test_build_select_job_page_live_content_appends_nav_block(self) -> None:
        assembled = "=== PAGE 1 ===\nroles"
        nav = "1: https://acme.com/careers"
        out = roster_mod._build_select_job_page_live_content(assembled, nav)
        assert "=== NAV LINKS ===" in out
        assert nav in out
        assert out.startswith("=== PAGE 1")

    def test_build_select_job_page_live_content_idempotent(self) -> None:
        nav = "1: https://acme.com/careers"
        assembled = f"content\n{nav}"
        assert roster_mod._build_select_job_page_live_content(assembled, nav) == assembled

    def test_build_select_job_page_live_content_blank_nav(self) -> None:
        assert roster_mod._build_select_job_page_live_content("page body", "  ") == "page body"


class TestAst719PjlRosterHelpers:
    """AST-719: additive PJL scrape ledger helpers."""

    def test_merge_pjl_scrape_record_skips_duplicate_and_empty(self) -> None:
        existing = [{"url": "https://acme.com/careers", "visible_text": "keep"}]
        assert roster_mod._merge_pjl_scrape_record(
            existing,
            {"url": "https://acme.com/careers", "visible_text": "dup"},
        ) == existing
        assert roster_mod._merge_pjl_scrape_record(
            existing,
            {"url": "https://acme.com/jobs", "visible_text": "  "},
        ) == existing
        merged = roster_mod._merge_pjl_scrape_record(
            existing,
            {"url": "https://acme.com/jobs", "visible_text": "new page"},
        )
        assert len(merged) == 2
        assert merged[1]["visible_text"] == "new page"

    def test_merge_pjl_scrape_record_persists_enumerated_nav_links(self) -> None:
        merged = roster_mod._merge_pjl_scrape_record(
            [],
            {
                "url": "https://acme.com/careers",
                "visible_text": "roles",
                "enumerated_nav_links": "1: /jobs",
            },
        )
        assert merged[0]["enumerated_nav_links"] == "1: /jobs"

    def test_assemble_pjl_content_sections(self) -> None:
        pages = [
            {"url": "https://acme.com/careers", "visible_text": "roles"},
            {"url": "https://acme.com/jobs", "visible_text": "list"},
        ]
        out = roster_mod._assemble_pjl_content(pages)
        assert out == (
            "=== PAGE 1: https://acme.com/careers ===\nroles\n\n"
            "=== PAGE 2: https://acme.com/jobs ===\nlist"
        )

    def test_assemble_pjl_content_includes_per_page_nav_section(self) -> None:
        pages = [
            {
                "url": "https://acme.com/careers",
                "visible_text": "roles",
                "enumerated_nav_links": "1: /about",
            },
        ]
        out = roster_mod._assemble_pjl_content(pages)
        assert "--- NAV LINKS ---" in out
        assert "1: /about" in out

    def test_merge_pjl_nav_links_appends_deduped(self) -> None:
        existing = "1: https://acme.com/about\n2: https://acme.com/careers"
        merged = roster_mod._merge_pjl_nav_links(
            existing,
            ["https://acme.com/careers/", "https://acme.com/team"],
        )
        assert "acme.com/about" in merged
        assert "acme.com/careers" in merged
        assert "acme.com/team" in merged
        assert merged.count("acme.com/careers") == 1


class TestAst720PjlMapsAndLedger:
    """AST-720: persisted PJL assembly + try_links ledger merge."""

    def test_pjl_maps_prefers_assembled_content(self) -> None:
        cdata = {
            "pjl_assembled_content": "=== PAGE 1: https://acme.com/careers ===\nroles",
            "pjl_scrape_pages": [{"url": "https://acme.com/other", "visible_text": "skip"}],
        }
        assembled, url_map, vis_map = roster_mod._pjl_maps_from_company_data(cdata)
        assert assembled.startswith("=== PAGE 1:")
        assert url_map == {1: "https://acme.com/other"}
        assert vis_map == {1: "skip"}

    def test_pjl_maps_rebuilds_from_scrape_pages_when_assembled_empty(self) -> None:
        cdata = {
            "pjl_scrape_pages": [{"url": "https://acme.com/careers", "visible_text": "roles"}],
        }
        assembled, url_map, vis_map = roster_mod._pjl_maps_from_company_data(cdata)
        assert "roles" in assembled
        assert url_map == {1: "https://acme.com/careers"}
        assert vis_map == {1: "roles"}

    def test_merge_try_links_appends_new_normalized_urls(self) -> None:
        nav = "1: https://acme.com/careers\n2: https://acme.com/newjobs"
        updated = roster_mod._merge_try_links_into_pjl_ledger(
            "acme",
            [2],
            nav,
            "",
            ["acme.com/careers"],
        )
        assert updated == ["acme.com/careers", "https://acme.com/newjobs"]

    def test_nav_links_for_try_links_prefers_pjl_nav(self) -> None:
        assert roster_mod._nav_links_for_try_links(
            {"pjl_nav_links": "1: /pjl", "nav_links": "1: /home"}
        ) == "1: /pjl"


class TestAst720PjlReadySelectDispatch:
    """AST-720: PJL_READY decomposed select_job_page outcomes."""

    @staticmethod
    def _pjl_ready_company(**extra: Any) -> Dict[str, Any]:
        company_data = {
            "pjl_assembled_content": "=== PAGE 1: https://acme.com/careers ===\nopen roles",
            "pjl_scrape_pages": [{"url": "https://acme.com/careers", "visible_text": "open roles"}],
            "possible_joblist_links": ["acme.com/careers"],
            "nav_links": "1: https://acme.com/careers",
        }
        company_data.update(extra)
        return _company(
            state="PJL_READY",
            company_website="https://acme.com",
            company_data=company_data,
        )

    @pytest.mark.asyncio
    async def test_select_dispatch_passes_live_content_with_nav_links(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        nav = "1: https://acme.com/careers\n2: https://acme.com/newjobs"
        company = self._pjl_ready_company(pjl_nav_links=nav)
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "update_company", MagicMock())
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        captured: Dict[str, Any] = {}

        async def fake_find(**kwargs: Any) -> Dict[str, Any]:
            captured["assembled_content"] = kwargs.get("assembled_content")
            return {
                "state": "JOBLIST_IDENTIFIED",
                "response_type": "JOBLIST_TITLES",
                "job_site": "",
            }

        monkeypatch.setattr(roster_mod, "_find_job_page_from_assembled", fake_find)
        await roster_mod.run_select_job_page_dispatch(company, "batch-759")
        live = captured.get("assembled_content") or ""
        assert "=== NAV LINKS ===" in live
        assert nav in live

    @pytest.mark.asyncio
    async def test_joblist_titles_identified_without_job_site_column(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        company = self._pjl_ready_company()
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        update = MagicMock()
        save = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "response_type": "JOBLIST_TITLES",
                        "selected_page": 1,
                        "job_titles": ["Engineer"],
                    },
                }
            ),
        )
        out = await roster_mod.run_select_job_page_dispatch(
            company, "batch-720", debug=True
        )
        assert out["state"] == "JOBLIST_IDENTIFIED"
        assert out["job_site"] == ""
        assert out["response_type"] == "JOBLIST_TITLES"
        update.assert_called_once()
        assert update.call_args.kwargs.get("job_site") == ""
        save.assert_called()
        saved = save.call_args_list[0][0][1]
        assert saved["job_titles"] == ["Engineer"]
        assert saved["selected_pjl_url"] == "https://acme.com/careers"

    @pytest.mark.asyncio
    async def test_try_links_appends_ledger_and_retries(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        company = self._pjl_ready_company(
            pjl_nav_links="1: https://acme.com/careers\n2: https://acme.com/newjobs",
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        save = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "response_type": "TRY_LINKS",
                        "try_links": [2],
                    },
                }
            ),
        )
        out = await roster_mod.run_select_job_page_dispatch(company, "batch-720")
        assert out["state"] == "PREFILTER_PASSED_RETRY"
        assert out["job_site"] == ""
        transition.assert_called_once_with("acme", "PREFILTER_PASSED_RETRY")
        saved = save.call_args[0][1]
        assert saved["possible_joblist_links"] == [
            "acme.com/careers",
            "https://acme.com/newjobs",
        ]

    @pytest.mark.asyncio
    async def test_try_links_exhausted_routes_no_pjl_selected(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        company = self._pjl_ready_company()
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "response_type": "TRY_LINKS",
                        "try_links": ["https://acme.com/careers"],
                    },
                }
            ),
        )
        out = await roster_mod.run_select_job_page_dispatch(company, "batch-720")
        assert out["state"] == "NO_PJL_SELECTED"
        assert out["job_site"] == ""

    @pytest.mark.asyncio
    async def test_jobsite_scrape_issue_suppresses_job_site(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        company = self._pjl_ready_company()
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "response_type": "JOBSITE_SCRAPE_ISSUE",
                        "selected_page": 1,
                        "scrape_issue_summary": "blocked",
                    },
                }
            ),
        )
        out = await roster_mod.run_select_job_page_dispatch(company, "batch-720")
        assert out["state"] == "JOBSITE_SCRAPE_ISSUE"
        assert out["job_site"] == ""

    @pytest.mark.asyncio
    async def test_empty_assembled_routes_no_pjl_selected(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        company = _company(
            state="PJL_READY",
            company_website="https://acme.com",
            company_data={},
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "do_task", AsyncMock())
        out = await roster_mod.run_select_job_page_dispatch(company, "batch-720")
        assert out["state"] == "NO_PJL_SELECTED"
        assert out["response_type"] == "NO_PJL_ASSEMBLED"
        roster_mod.do_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_company_task_pjl_ready_select_key(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        select = AsyncMock(return_value={"state": "JOBLIST_IDENTIFIED"})
        monkeypatch.setattr(roster_mod, "run_select_job_page_dispatch", select)
        entity = self._pjl_ready_company()
        out = await roster_mod.run_company_task(
            "PJL_READY", entity, "batch-720", dispatch_task_key="select_job_page",
        )
        assert out["total_passed"] == 1
        select.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_company_task_pjl_ready_wrong_key_errors(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        entity = self._pjl_ready_company()
        out = await roster_mod.run_company_task(
            "PJL_READY", entity, "batch-720", dispatch_task_key="find_job_page",
        )
        assert out["total_errors"] == 1


class TestAst721ParseDispatchHelpers:
    """AST-721: parse dispatch URL resolution and failure-state ladder."""

    def test_resolve_selected_pjl_url(self) -> None:
        assert roster_mod._resolve_selected_pjl_url({"selected_pjl_url": " https://acme.com/jobs "}) == "https://acme.com/jobs"
        assert roster_mod._resolve_selected_pjl_url({}) == ""

    def test_parse_dispatch_failure_state_ladder(self) -> None:
        assert roster_mod._parse_dispatch_failure_state("JOBLIST_IDENTIFIED") == "JOBLIST_IDENTIFIED_RETRY"
        assert roster_mod._parse_dispatch_failure_state("JOBLIST_IDENTIFIED_RETRY") == "COULD_NOT_PARSE_JOBLIST"
        assert roster_mod._parse_dispatch_failure_state("UNKNOWN") == "COULD_NOT_PARSE_JOBLIST"


class TestAst721ParseJobListDispatch:
    """AST-721: decomposed parse_job_list from JOBLIST_IDENTIFIED / RETRY."""

    @staticmethod
    def _browser_cm():
        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        return _browser

    @staticmethod
    def _identified_company(state: str = "JOBLIST_IDENTIFIED", **extra: Any) -> Dict[str, Any]:
        company_data = {
            "selected_pjl_url": "https://acme.com/jobs",
            "job_titles": ["Engineer"],
        }
        company_data.update(extra)
        return _company(
            state=state,
            company_website="https://acme.com",
            company_data=company_data,
        )

    @pytest.mark.asyncio
    async def test_success_watch_and_parse_instructions(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        company = self._identified_company()
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        save_data = MagicMock()
        save_co = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save_data)
        monkeypatch.setattr(roster_mod, "_save_company", save_co)
        monkeypatch.setattr(roster_mod, "create_browser_context", self._browser_cm())
        monkeypatch.setattr(
            roster_mod, "_scrape_list_page_dom_for_parse", AsyncMock(return_value="<html>dom</html>"),
        )
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["<div>Engineer</div>"]))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_parse_job_list",
            AsyncMock(return_value={"job_container": "div", "job_tag": "a", "job_ids": ["j1"]}),
        )
        monkeypatch.setattr(roster_mod, "_validate_parse_job_list_raw_job_listings", MagicMock(return_value=(None, [], [])))
        out = await roster_mod.run_parse_job_list_dispatch(company, "batch-721", debug=True)
        assert out["state"] == "WATCH"
        assert out["job_site"] == "https://acme.com/jobs"
        assert out["response_type"] == "PARSE_DISPATCH_OK"
        save_data.assert_called()
        saved = save_data.call_args[0][1]
        assert saved["parse_instructions"]["container"] == "div"
        save_co.assert_called_once()
        assert save_co.call_args.kwargs.get("state") == "WATCH"

    @pytest.mark.asyncio
    async def test_first_fail_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = self._identified_company()
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        save_data = MagicMock()
        save_co = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save_data)
        monkeypatch.setattr(roster_mod, "_save_company", save_co)
        monkeypatch.setattr(roster_mod, "create_browser_context", self._browser_cm())
        monkeypatch.setattr(roster_mod, "_scrape_list_page_dom_for_parse", AsyncMock(return_value=""))
        out = await roster_mod.run_parse_job_list_dispatch(company, "batch-721")
        assert out["state"] == "JOBLIST_IDENTIFIED_RETRY"
        assert out["response_type"] == "PARSE_DISPATCH_EMPTY_DOM"
        save_co.assert_called_once()
        assert save_co.call_args.kwargs.get("state") == "JOBLIST_IDENTIFIED_RETRY"

    @pytest.mark.asyncio
    async def test_second_fail_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = self._identified_company(state="JOBLIST_IDENTIFIED_RETRY")
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        save_co = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save_co)
        monkeypatch.setattr(roster_mod, "create_browser_context", self._browser_cm())
        monkeypatch.setattr(roster_mod, "_scrape_list_page_dom_for_parse", AsyncMock(return_value=""))
        out = await roster_mod.run_parse_job_list_dispatch(company, "batch-721")
        assert out["state"] == "COULD_NOT_PARSE_JOBLIST"
        assert save_co.call_args.kwargs.get("state") == "COULD_NOT_PARSE_JOBLIST"

    @pytest.mark.asyncio
    async def test_missing_url_or_titles(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())

        no_url = _company(
            state="JOBLIST_IDENTIFIED",
            company_website="https://acme.com",
            company_data={"job_titles": ["E"]},
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=no_url))
        out_url = await roster_mod.run_parse_job_list_dispatch(no_url, "batch-721")
        assert out_url["state"] == "JOBLIST_IDENTIFIED_RETRY"
        assert out_url["response_type"] == "PARSE_DISPATCH_MISSING_URL"

        no_titles = _company(
            state="JOBLIST_IDENTIFIED",
            company_website="https://acme.com",
            company_data={"selected_pjl_url": "https://acme.com/jobs"},
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=no_titles))
        out_titles = await roster_mod.run_parse_job_list_dispatch(no_titles, "batch-721")
        assert out_titles["state"] == "JOBLIST_IDENTIFIED_RETRY"
        assert out_titles["response_type"] == "PARSE_DISPATCH_MISSING_TITLES"

    @pytest.mark.asyncio
    async def test_run_company_task_routes_identified_and_retry(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        parse = AsyncMock(return_value={"state": "WATCH"})
        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", parse)
        entity = self._identified_company()
        ok = await roster_mod.run_company_task(
            "JOBLIST_IDENTIFIED", entity, "batch-721", dispatch_task_key="parse_job_list",
        )
        assert ok["total_passed"] == 1
        retry_entity = self._identified_company(state="JOBLIST_IDENTIFIED_RETRY")
        retry = AsyncMock(return_value={"state": "COULD_NOT_PARSE_JOBLIST"})
        monkeypatch.setattr(roster_mod, "run_parse_job_list_dispatch", retry)
        bad = await roster_mod.run_company_task(
            "JOBLIST_IDENTIFIED_RETRY", retry_entity, "batch-721b", dispatch_task_key="parse_job_list",
        )
        assert bad["total_passed"] == 1
        retry.assert_awaited_once()


class TestAst701ScrapeCompanyHomepageContent:
    @staticmethod
    def _mock_browser_page(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        ctx = MagicMock()
        monkeypatch.setattr(roster_mod, "get_page", AsyncMock(return_value=MagicMock()))
        monkeypatch.setattr(roster_mod, "close_page", AsyncMock())
        return ctx

    @pytest.mark.asyncio
    async def test_scrape_exception_returns_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ctx = self._mock_browser_page(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "scrape_loaded_page_contract",
            AsyncMock(side_effect=RuntimeError("blocked")),
        )
        out = await roster_mod.scrape_company_homepage_content(
            "acme", "https://acme.com", browser_context=ctx,
        )
        assert out["error"] == "blocked"
        assert out["visible_text"] == ""

    @pytest.mark.asyncio
    async def test_redirect_and_empty_text_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ctx = self._mock_browser_page(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "scrape_loaded_page_contract",
            AsyncMock(side_effect=[
                {
                    "visible_text": "hello",
                    "final_url": "https://canonical.example",
                    "enumerated_nav_links": "1. /about",
                    "nav_urls": ["https://canonical.example/about"],
                },
                {
                    "visible_text": "   ",
                    "final_url": "https://acme.com",
                    "enumerated_nav_links": "",
                    "nav_urls": [],
                },
            ]),
        )
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        redirected = await roster_mod.scrape_company_homepage_content(
            "acme", "https://old.example", browser_context=ctx,
        )
        assert redirected["error"] is None
        assert redirected["company_website"] == "https://canonical.example"
        assert redirected["enumerated_nav_links"] == "1. /about"
        update.assert_called_once_with("acme", company_website="https://canonical.example")

        empty = await roster_mod.scrape_company_homepage_content(
            "acme", "https://acme.com", browser_context=ctx,
        )
        assert empty["error"] == "No visible text extracted"

    @pytest.mark.asyncio
    async def test_nav_failure_is_non_fatal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ctx = self._mock_browser_page(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "scrape_loaded_page_contract",
            AsyncMock(
                return_value={
                    "visible_text": "hello world",
                    "final_url": "https://acme.com",
                    "enumerated_nav_links": "",
                    "nav_urls": [],
                }
            ),
        )
        out = await roster_mod.scrape_company_homepage_content(
            "acme", "https://acme.com", browser_context=ctx,
        )
        assert out["error"] is None
        assert out["visible_text"] == "hello world"
        assert out["enumerated_nav_links"] == ""

    @pytest.mark.asyncio
    async def test_collapses_consecutive_blank_lines_at_scrape(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx = self._mock_browser_page(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "scrape_loaded_page_contract",
            AsyncMock(
                return_value={
                    "visible_text": "intro\n\nbody",
                    "final_url": "https://acme.com",
                    "enumerated_nav_links": "1. /about",
                    "nav_urls": ["https://acme.com/about"],
                }
            ),
        )
        out = await roster_mod.scrape_company_homepage_content(
            "acme", "https://acme.com", browser_context=ctx,
        )
        assert out["error"] is None
        assert out["visible_text"] == "intro\n\nbody"


class TestPrefilterCompany:
    @pytest.mark.asyncio
    async def test_requires_company_website(self) -> None:
        out = await roster_mod.prefilter_company("acme", "")
        assert out["error"] == "No company_website"

    @pytest.mark.asyncio
    async def test_scrape_failure_transitions_cannot_read(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(side_effect=RuntimeError("blocked")))
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        out = await roster_mod.prefilter_company("acme", "https://acme.com")
        assert out["state"] == "CANNOT_READ_WEBSITE"
        transition.assert_called_once_with("acme", "CANNOT_READ_WEBSITE")
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_redirect_and_empty_text_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_visible_text",
            AsyncMock(side_effect=[
                ("hello", "https://canonical.example"),
                ("   ", "https://acme.com"),
            ]),
        )
        update = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=["https://acme.com/about"]))
        monkeypatch.setattr(roster_mod, "enumerate_array", MagicMock(return_value="1. /about"))
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response([_rc_grade()]),
                }
            ),
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=_company()))
        redirected = await roster_mod.prefilter_company("acme", "https://old.example")
        assert redirected["state"] == ROSTER_CONFIG["prefilter"]["no_pjl_state"]
        update.assert_called_once_with("acme", company_website="https://canonical.example")

        empty = await roster_mod.prefilter_company("acme", "https://acme.com")
        assert empty["state"] == "CANNOT_READ_WEBSITE"

    @pytest.mark.asyncio
    async def test_api_failure_and_missing_parsed_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("hello", "https://acme.com")))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(side_effect=RuntimeError("nav")))
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(side_effect=[
                {"success": False, "error": "api down"},
                {"success": True, "parsed_response": None},
            ]),
        )
        hard_fail = await roster_mod.prefilter_company("acme", "https://acme.com")
        missing_parse = await roster_mod.prefilter_company("acme", "https://acme.com")
        assert hard_fail["decision"] == "ERROR"
        assert hard_fail["state"] == ROSTER_CONFIG["prefilter"]["error_state"]
        assert missing_parse["decision"] == "RETRY"
        assert missing_parse["state"] == ROSTER_CONFIG["prefilter"]["retry_state"]
        assert transition.call_count == 2

    @pytest.mark.asyncio
    async def test_pass_and_fail_grades_persist_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AST-507/718: encoded jobs[0] shape; decomposed monolithic path uses PREFILTER_* / NO_PREFILTER_JOBLISTS."""
        _patch_prefilter_scrape_with_nav(monkeypatch)
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=_company(state_history=[])))
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(side_effect=[
                {
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades({"grade": "F", "vector": "fit", "confidence": 2, "reason": "nope"}),
                        possible_job_links=[1],
                    ),
                },
                {
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades(
                            {"grade": "A", "vector": "fit", "confidence": 5, "reason": "yes"},
                        ),
                        possible_job_links=[1],
                        culture_links_to_explore=[3],
                    ),
                },
            ]),
        )
        fail = await roster_mod.prefilter_company("acme", "https://acme.com", ctx=_prefilter_rubric_ctx())
        passed = await roster_mod.prefilter_company("acme", "https://acme.com", ctx=_prefilter_rubric_ctx())
        assert fail["decision"] == "IGNORE"
        assert fail["state"] == "PREFILTER_FAILED"
        assert passed["decision"] == "TO_WATCH"
        assert passed["state"] == "PREFILTER_PASSED"
        assert save.call_count == 2
        assert "prefilter_score" in save.call_args_list[1][0][1]

    @pytest.mark.asyncio
    async def test_exception_sets_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("hello", "https://acme.com")))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        monkeypatch.setattr(roster_mod, "do_task", AsyncMock(side_effect=RuntimeError("boom")))
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        out = await roster_mod.prefilter_company("acme", "https://acme.com")
        assert out["state"] == ROSTER_CONFIG["prefilter"]["error_state"]
        transition.assert_called_once()


class TestAst507EncodedPrefilter:
    """AST-507: grades_encoded prefilter, dealbreaker F2+, inflow PREFILTER_* vs legacy TO_WATCH."""

    @staticmethod
    def _scrape_ready(monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("hello", "https://acme.com")))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())

    @pytest.mark.asyncio
    async def test_inflow_dealbreaker_f2_prefilter_failed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._scrape_ready(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(
                return_value={
                    "short_name": "acme",
                    "state_history": [{"from_state": "NEW", "to_state": "WEBSITE_FOUND"}],
                }
            ),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades({"grade": "F", "vector": "fit", "confidence": 2, "reason": "nope"}),
                    ),
                }
            ),
        )
        out = await roster_mod.prefilter_company("acme", "https://acme.com", ctx=_prefilter_rubric_ctx())
        assert out["state"] == "PREFILTER_FAILED"
        assert out["decision"] == "IGNORE"

    @pytest.mark.asyncio
    async def test_inflow_f1_no_dealbreaker_prefilter_passed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """F1 on one vector is not a dealbreaker when another vector has confidence > 1."""
        _patch_prefilter_scrape_with_nav(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(
                return_value=_company(
                    state_history=[{"from_state": "NEW", "to_state": "WEBSITE_FOUND"}],
                )
            ),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades(
                            {"grade": "F", "vector": "fit", "confidence": 1},
                            {"grade": "A", "vector": "culture", "confidence": 5},
                        ),
                        possible_job_links=[1],
                    ),
                }
            ),
        )
        out = await roster_mod.prefilter_company(
            "acme", "https://acme.com", ctx=_prefilter_rubric_ctx(multi_vector=True)
        )
        assert out["state"] == "PREFILTER_PASSED"
        assert out["decision"] == "TO_WATCH"

    @pytest.mark.asyncio
    async def test_legacy_empty_history_maps_pass_to_to_watch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Legacy branch: non-inflow WEBSITE_FOUND when cfg input_state is not HOMEPAGE_READY."""
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(return_value=_company(state_history=[], state="WEBSITE_FOUND")),
        )
        cfg = {**ROSTER_CONFIG["prefilter"], "input_state": ""}
        flat = {
            "grades": _prefilter_grades({"grade": "A", "vector": "fit", "confidence": 5}),
            "possible_job_links": [],
        }
        new_state = roster_mod._apply_prefilter_decoded_company_outcome(
            "acme",
            flat,
            cfg,
            _prefilter_rubric_ctx(),
            nav_links_from_data="",
        )
        assert new_state == "TO_WATCH"
        transition.assert_called_once_with("acme", "TO_WATCH")


class TestAst718PrefilterPjlRouting:
    """AST-718: decomposed-path routing, PJL URL hydration, legacy TO_WATCH unchanged."""

    @staticmethod
    def _inflow_company(monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(
                return_value=_company(
                    state_history=[{"from_state": "NEW", "to_state": "WEBSITE_FOUND"}],
                )
            ),
        )

    @pytest.mark.asyncio
    async def test_inflow_empty_links_routes_no_prefilter_joblists(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_prefilter_scrape_with_nav(monkeypatch)
        self._inflow_company(monkeypatch)
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades({"grade": "A", "vector": "fit", "confidence": 5}),
                    ),
                }
            ),
        )
        out = await roster_mod.prefilter_company("acme", "https://acme.com", ctx=_prefilter_rubric_ctx())
        assert out["state"] == "NO_PREFILTER_JOBLISTS"
        assert out["decision"] == "IGNORE"
        saved = save.call_args[0][1]
        assert saved["possible_joblist_links"] == []
        assert saved["possible_job_links"] == []

    @pytest.mark.asyncio
    async def test_inflow_pass_hydrates_possible_joblist_links(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_prefilter_scrape_with_nav(monkeypatch)
        self._inflow_company(monkeypatch)
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades({"grade": "A", "vector": "fit", "confidence": 5}),
                        possible_job_links=[1],
                    ),
                }
            ),
        )
        out = await roster_mod.prefilter_company("acme", "https://acme.com", ctx=_prefilter_rubric_ctx())
        assert out["state"] == "PREFILTER_PASSED"
        saved = save.call_args[0][1]
        assert saved["possible_job_links"] == [1]
        assert saved["possible_joblist_links"] == ["acme.com/careers"]

    @pytest.mark.asyncio
    async def test_inflow_unhydratable_indices_route_no_prefilter_joblists(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_prefilter_scrape_with_nav(monkeypatch)
        self._inflow_company(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades({"grade": "A", "vector": "fit", "confidence": 5}),
                        possible_job_links=[99],
                    ),
                }
            ),
        )
        out = await roster_mod.prefilter_company("acme", "https://acme.com", ctx=_prefilter_rubric_ctx())
        assert out["state"] == "NO_PREFILTER_JOBLISTS"

    @pytest.mark.asyncio
    async def test_batch_homepage_ready_pass_requires_hydrated_pjl(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "passco",
                                "grades": _prefilter_grades(
                                    {"grade": "A", "vector": "fit", "confidence": 5, "reason": "yes"},
                                ),
                                "possible_job_links": [1],
                            },
                            {
                                "astral_job_id": "nolinks",
                                "grades": _prefilter_grades(
                                    {"grade": "A", "vector": "fit", "confidence": 5, "reason": "yes"},
                                ),
                            },
                        ],
                    },
                    "timesheet": {},
                }
            ),
        )
        companies = [
            {
                "short_name": "passco",
                "state": "HOMEPAGE_READY",
                "company_data": {
                    "homepage_text": "good homepage",
                    "nav_links": "1: https://acme.com/careers",
                },
            },
            {
                "short_name": "nolinks",
                "state": "HOMEPAGE_READY",
                "company_data": {"homepage_text": "other homepage"},
            },
        ]
        out = await roster_mod.prefilter_company_batch(
            "batch-718", companies, ctx=_prefilter_rubric_ctx(), debug=False
        )
        assert out["passed"] == 1
        assert out["failed"] == 1
        assert out["total"] == 2


class TestAst603ConsultParityHydration:
    """AST-603: prefilter hydrates rubric reasons; dict-envelope path; AST-507 score regression."""

    @staticmethod
    def _scrape_ready(monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("hello", "https://acme.com")))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())

    @pytest.mark.asyncio
    async def test_karbon_dict_envelope_hydrates_notes_and_links(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_prefilter_scrape_with_nav(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(
                return_value=_company(
                    state_history=[{"from_state": "NEW", "to_state": "WEBSITE_FOUND"}],
                )
            ),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        # Grades lack reason — roster must hydrate from rubric artifact (AST-603).
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "grades": [
                                    {"vector": "Reality Check", "grade": "A", "confidence": 3},
                                    {"vector": "Mission Product Orientation", "grade": "B", "confidence": 3},
                                    {"vector": "US Presence", "grade": "A", "confidence": 3},
                                ],
                                "possible_job_links": [1],
                                "culture_links_to_explore": [75, 76],
                            }
                        ]
                    },
                }
            ),
        )
        out = await roster_mod.prefilter_company(
            "acme", "https://acme.com", ctx=_ast603_prefilter_rubric_ctx()
        )
        assert out["state"] == "PREFILTER_PASSED"
        saved = save.call_args[0][1]
        notes = saved["prefilter_company_notes"]
        assert "independently verifiable" in notes  # embedded RC (AST-707)
        assert "decent fit" in notes
        assert "US based" in notes
        assert saved["possible_job_links"] == [1]
        assert saved["possible_joblist_links"] == ["acme.com/careers"]
        assert saved["culture_links_to_explore"] == [75, 76]

    @pytest.mark.asyncio
    async def test_inflow_pass_persists_prefilter_score(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AST-507 regression: scored pass still writes prefilter_score."""
        _patch_prefilter_scrape_with_nav(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(
                return_value=_company(
                    state_history=[{"from_state": "NEW", "to_state": "WEBSITE_FOUND"}],
                )
            ),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        [
                            {"grade": "A", "vector": "Reality Check", "confidence": 5, "reason": "ok"},
                            {"grade": "A", "vector": "Mission Product Orientation", "confidence": 5, "reason": "ok"},
                            {"grade": "A", "vector": "US Presence", "confidence": 5, "reason": "ok"},
                        ],
                        possible_job_links=[1],
                    ),
                }
            ),
        )
        out = await roster_mod.prefilter_company(
            "acme", "https://acme.com", ctx=_ast603_prefilter_rubric_ctx()
        )
        assert out["state"] == "PREFILTER_PASSED"
        assert "prefilter_score" in save.call_args[0][1]


class TestAst698PrefilterDebugPassthrough:
    @pytest.mark.asyncio
    async def test_prefilter_company_forwards_debug_to_do_task(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            roster_mod, "get_visible_text", AsyncMock(return_value=("hello", "https://acme.com"))
        )
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(
            roster_mod, "get_company", MagicMock(return_value=_company(state_history=[]))
        )
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        do_task = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": _encoded_prefilter_response([_rc_grade()]),
            }
        )
        monkeypatch.setattr(roster_mod, "do_task", do_task)
        await roster_mod.prefilter_company("acme", "https://acme.com", debug=True)
        assert do_task.await_args is not None
        assert do_task.await_args.kwargs.get("debug") is True

    @pytest.mark.asyncio
    async def test_prefilter_company_batch_forwards_debug_to_do_task(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        batch = AsyncMock(return_value={"passed": 1, "failed": 0, "total": 1})
        monkeypatch.setattr(roster_mod, "prefilter_company_batch", batch)
        company = _company(
            state="HOMEPAGE_READY",
            company_data={"homepage_text": "hello world"},
        )
        await roster_mod.prefilter_company_batch("batch-1", [company], debug=True)
        assert batch.await_args is not None
        assert batch.await_args.kwargs.get("debug") is True


class TestAst702PrefilterCompanyBatch:
    @pytest.mark.asyncio
    async def test_skips_not_ready_without_do_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        save = MagicMock()
        do_task = AsyncMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(roster_mod, "do_task", do_task)
        companies = [
            {"short_name": "empty", "state": "HOMEPAGE_READY", "company_data": {}},
            {"short_name": "blank", "state": "HOMEPAGE_READY", "company_data": {"homepage_text": "  "}},
        ]
        out = await roster_mod.prefilter_company_batch("batch-skip", companies, debug=False)
        assert out == {"passed": 0, "failed": 0, "total": 2, "skipped": 2}
        do_task.assert_not_called()
        assert transition.call_count == 2
        save.assert_called()

    @pytest.mark.asyncio
    async def test_batch_pass_and_fail_counts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "passco",
                                "grades": _prefilter_grades(
                                    {"grade": "A", "vector": "fit", "confidence": 5, "reason": "yes"},
                                ),
                                "possible_job_links": [1],
                            },
                            {
                                "astral_job_id": "failco",
                                "grades": _prefilter_grades(
                                    {"grade": "F", "vector": "fit", "confidence": 2, "reason": "nope"},
                                ),
                            },
                        ],
                    },
                    "timesheet": {},
                }
            ),
        )
        companies = [
            {
                "short_name": "passco",
                "state": "HOMEPAGE_READY",
                "company_data": {
                    "homepage_text": "good homepage",
                    "nav_links": "1: https://acme.com/careers",
                },
            },
            {
                "short_name": "failco",
                "state": "HOMEPAGE_READY",
                "company_data": {"homepage_text": "other homepage"},
            },
        ]
        ctx = _prefilter_rubric_ctx()
        out = await roster_mod.prefilter_company_batch("batch-mix", companies, ctx=ctx, debug=False)
        assert out["passed"] == 1
        assert out["failed"] == 1
        assert out["total"] == 2
        assert out.get("skipped", 0) == 0

    @pytest.mark.asyncio
    async def test_do_task_failure_transitions_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"success": False, "error": "api down"}),
        )
        companies = [
            {
                "short_name": "acme",
                "state": "HOMEPAGE_READY",
                "company_data": {"homepage_text": "hello"},
            },
        ]
        out = await roster_mod.prefilter_company_batch("batch-fail", companies, debug=False)
        assert out == {"passed": 0, "failed": 0, "total": 1}
        transition.assert_called_once_with("acme", "WEBSITE_FOUND_RETRY")


class TestAst702PrefilterBatchHelpers:
    def test_company_homepage_ready(self) -> None:
        assert roster_mod._company_homepage_ready({"company_data": {"homepage_text": "hi"}})
        assert not roster_mod._company_homepage_ready({"company_data": {}})
        assert not roster_mod._company_homepage_ready({"company_data": {"homepage_text": "  "}})

    def test_prefilter_batch_fail_dest_from_homepage_ready(self) -> None:
        cfg = ROSTER_CONFIG["prefilter"]
        assert roster_mod._prefilter_batch_fail_dest("HOMEPAGE_READY", cfg) == "WEBSITE_FOUND_RETRY"
        assert roster_mod._prefilter_batch_fail_dest("WEBSITE_FOUND_RETRY", cfg) == "ERROR_PREFILTER"


class TestAst707EmbeddedRcBatchHydration:
    @pytest.mark.asyncio
    async def test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """UAT repro: artifact MP/US only + grades with vector RC must not mass-retry on hydration."""
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=_company(state_history=[])))
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": "acme",
                                "grades": [
                                    {"grade": "D", "vector": "Reality Check", "confidence": 3},
                                    {"grade": "B", "vector": "Mission & Product", "confidence": 3},
                                    {"grade": "A", "vector": "US Presence", "confidence": 3},
                                ],
                            },
                        ],
                    },
                    "timesheet": {},
                }
            ),
        )
        companies = [
            {
                "short_name": "acme",
                "state": "HOMEPAGE_READY",
                "company_data": {"homepage_text": "Acme Corp builds widgets in the USA."},
            },
        ]
        out = await roster_mod.prefilter_company_batch(
            "batch-rc",
            companies,
            ctx=_artifact_mp_us_only_ctx(),
            debug=False,
        )
        assert out == {"passed": 1, "failed": 0, "total": 1}
        retry_calls = [
            call.args[1]
            for call in transition.call_args_list
            if call.args[0] == "acme"
        ]
        assert "WEBSITE_FOUND_RETRY" not in retry_calls
        assert save.called
        saved_grades = save.call_args.args[1].get("prefilter_grades") or []
        rc_row = next(g for g in saved_grades if g.get("vector") == "Reality Check")
        assert rc_row.get("reason")


@pytest.mark.skip(reason="AST-721: find_job_page monolith removed; covered by decomposed AST-718–721 tests")
class TestFindJobPage:
    @pytest.mark.asyncio
    async def test_missing_links_short_circuits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=_company(company_data={})))
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", debug=True)
        assert out["state"] == "NO_JOBLIST"
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_happy_path_delegates_to_check_parse(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(return_value=("content", {1: "https://acme.com/jobs"}, {1: "<html/>"}, {1: "visible jobs"})),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"response_type": "JOBLIST_NO_JOBS", "selected_page": 1},
                }
            ),
        )
        check = AsyncMock(
            return_value={"short_name": "acme", "state": "NO_OPENINGS", "job_site": "https://acme.com/jobs", "response_type": "JOBLIST_NO_JOBS"}
        )
        monkeypatch.setattr(roster_mod, "_check_parse_results", check)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", company_website="https://acme.com")
        assert out["state"] == "NO_OPENINGS"
        check.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_try_links_retry_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(
                side_effect=[
                    ("content", {1: "https://acme.com/jobs"}, {}, {}),
                    ("retry", {2: "https://acme.com/careers"}, {}, {}),
                ]
            ),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                side_effect=[
                    {"success": True, "parsed_response": {"response_type": "TRY_LINKS", "try_links": [2], "selected_page": 1}},
                    {"success": True, "parsed_response": {"response_type": "NOPE", "selected_page": 2}},
                ]
            ),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        failed = await roster_mod.find_job_page("https://acme.com", short_name="acme", debug=True)
        assert failed["state"] == "NO_JOBLIST"

    @pytest.mark.asyncio
    async def test_try_links_without_suggestions_and_empty_scrape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(side_effect=[("content", {1: "https://acme.com/jobs"}, {}, {}), ("", {}, {}, {})]),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"response_type": "TRY_LINKS", "try_links": [], "selected_page": 1}}),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        empty_scrape = await roster_mod.find_job_page("https://acme.com", short_name="acme", debug=True)
        assert empty_scrape["state"] == "NO_JOBLIST"
        save.assert_called()


class TestFetchJobLinksContent:
    @pytest.mark.asyncio
    async def test_skips_missing_urls_and_records_scrape_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/jobs"}))
        page = AsyncMock()
        monkeypatch.setattr(roster_mod, "get_page", AsyncMock(side_effect=[page, RuntimeError("blocked")]))
        monkeypatch.setattr(roster_mod, "extract_visible_text", AsyncMock(return_value={"text": "Job A"}))
        monkeypatch.setattr(roster_mod, "extract_page_dom", AsyncMock(return_value="<div>Job A</motion>"))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=["https://acme.com/new"]))
        monkeypatch.setattr(roster_mod, "close_page", AsyncMock())
        content, url_map, dom_map, vis_map = await roster_mod._fetch_job_links_content(
            [1, 2, "https://direct.example/jobs"],
            "1. https://acme.com/jobs",
            AsyncMock(),
            debug=True,
        )
        assert "Job A" in content
        assert url_map[1] == "https://acme.com/jobs"
        assert dom_map[1].startswith("<div>")
        assert vis_map[1] == "Job A"
        assert "scrape failed" in content

    @pytest.mark.asyncio
    async def test_skips_invalid_link_ids_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/jobs"}))
        page = AsyncMock()
        monkeypatch.setattr(roster_mod, "get_page", AsyncMock(return_value=page))
        monkeypatch.setattr(roster_mod, "extract_visible_text", AsyncMock(return_value={"text": "Job A"}))
        monkeypatch.setattr(roster_mod, "extract_page_dom", AsyncMock(return_value=""))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        monkeypatch.setattr(roster_mod, "close_page", AsyncMock())
        content, url_map, dom_map, vis_map = await roster_mod._fetch_job_links_content(
            ["bad-id"],
            "1. https://acme.com/jobs",
            AsyncMock(),
            debug=False,
        )
        assert content == ""
        assert url_map == {}
        assert dom_map == {}
        assert vis_map == {}


class TestCheckParseResults:
    @pytest.mark.asyncio
    async def test_no_jobs_and_unknown_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)
        no_jobs = await roster_mod._check_parse_results(
            {"no_jobs_message": "closed"},
            "JOBLIST_NO_JOBS",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {},
            debug=True,
        )
        assert no_jobs["state"] == "NO_OPENINGS"
        unknown = await roster_mod._check_parse_results({}, "OTHER", "acme", "https://acme.com", "https://acme.com/jobs", {})
        assert unknown["state"] == "NO_JOBLIST"

    @pytest.mark.asyncio
    async def test_joblist_titles_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save_company = MagicMock()
        save_data = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save_company)
        monkeypatch.setattr(roster_mod, "save_company_data", save_data)
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=[]))
        no_dom = await roster_mod._check_parse_results(
            {"job_titles": ["Role"]},
            "JOBLIST_TITLES",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {},
            selected_page=1,
            debug=True,
        )
        assert no_dom["state"] == "NO_JOBLIST"

        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["<div>Role</div>"]))
        monkeypatch.setattr(roster_mod, "_fetch_parse_job_list", AsyncMock(return_value={}))
        no_parse = await roster_mod._check_parse_results(
            {"job_titles": ["Role"]},
            "JOBLIST_TITLES",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {1: "<div>Role</motion>"},
            selected_page=1,
        )
        assert no_parse["state"] == "CANNOT_PARSE_JOB_SITE"

        monkeypatch.setattr(
            roster_mod,
            "_fetch_parse_job_list",
            AsyncMock(return_value={"job_container": ".jobs", "job_tag": "a", "job_ids": ["id-1"]}),
        )
        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=("mismatch", None, [])),
        )
        invalid = await roster_mod._check_parse_results(
            {"job_titles": ["Role"]},
            "JOBLIST_TITLES",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {1: "<div class='jobs'><a>Role id-1</a></div>"},
            selected_page=1,
        )
        assert invalid["state"] == "CANNOT_PARSE_JOB_SITE"

        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=(None, ["<a>Role id-1</a>"], [])),
        )
        monkeypatch.setattr(roster_mod, "_compute_container_index", MagicMock(return_value=0))
        success = await roster_mod._check_parse_results(
            {"job_titles": ["Role"]},
            "JOBLIST_TITLES",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {1: "<motion class='jobs'><a>Role id-1</a></motion>"},
            selected_page=1,
        )
        assert success["state"] == "WATCH"
        assert success["parse_instructions"]["container"] == ".jobs"


class TestJobSiteForPersist673:
    def test_watch_writes_page_option_url(self) -> None:
        assert roster_mod._job_site_for_persist(
            terminal_state="WATCH",
            page_option_url="https://confirmed.example/jobs",
            pre_run_job_site="https://careers.example/jobs",
        ) == "https://confirmed.example/jobs"

    def test_no_joblist_preserves_pre_run_job_site(self) -> None:
        assert roster_mod._job_site_for_persist(
            terminal_state="NO_JOBLIST",
            page_option_url="https://example.com",
            pre_run_job_site="https://careers.example/jobs",
        ) == "https://careers.example/jobs"

    def test_no_joblist_empty_baseline_stays_empty(self) -> None:
        assert roster_mod._job_site_for_persist(
            terminal_state="NO_JOBLIST",
            page_option_url="https://example.com",
            pre_run_job_site="",
        ) == ""

    @pytest.mark.parametrize("terminal_state", ["NO_OPENINGS", "CANNOT_PARSE_JOB_SITE"])
    def test_success_states_write_page_option_url(self, terminal_state: str) -> None:
        assert roster_mod._job_site_for_persist(
            terminal_state=terminal_state,
            page_option_url="https://careers.example/jobs",
            pre_run_job_site="https://old.example/jobs",
        ) == "https://careers.example/jobs"


@pytest.mark.skip(reason="AST-721: find_job_page monolith removed; covered by decomposed AST-718–721 tests")
class TestFindJobPageAst673:
    @pytest.mark.asyncio
    async def test_find_job_page_with_job_site_delegates_jobs_found_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        company = _company(
            job_site="https://careers.example/jobs",
            company_website="https://example.com",
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        jf = AsyncMock(return_value={"state": "WATCH", "job_site": "https://careers.example/jobs"})
        monkeypatch.setattr(roster_mod, "jobs_found_process_job_site", jf)
        out = await roster_mod.find_job_page(
            "https://example.com", short_name="acme", company_website="https://example.com"
        )
        jf.assert_awaited_once_with(
            "acme", "https://example.com", "https://careers.example/jobs", debug=False, ctx=None
        )
        assert out["state"] == "WATCH"

    def test_save_company_no_joblist_preserves_pre_run_job_site(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(
                return_value=_company(
                    job_site="https://careers.example/jobs",
                    company_website="https://example.com",
                )
            ),
        )
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        roster_mod._save_company("acme", "https://example.com", "NO_JOBLIST", "https://example.com")
        assert update.call_args.kwargs["job_site"] == "https://careers.example/jobs"

    @pytest.mark.asyncio
    async def test_find_job_page_failure_empty_job_site_stays_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        company = _company(company_website="https://example.com", company_data={})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://example.com", short_name="acme", debug=True)
        assert out["state"] == "NO_JOBLIST"
        update.assert_called_once()
        assert update.call_args.kwargs["job_site"] == ""

    def test_save_company_watch_writes_confirmed_job_site(self, monkeypatch: pytest.MonkeyPatch) -> None:
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(return_value=_company(job_site="https://old.example/jobs")),
        )
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        roster_mod._save_company(
            "acme",
            "https://example.com",
            "WATCH",
            "https://confirmed.example/jobs",
        )
        assert update.call_args.kwargs["job_site"] == "https://confirmed.example/jobs"


class TestJobSiteDistinct674:
    @pytest.mark.parametrize(
        "job_site,company_website,expected",
        [
            ("https://careers.example/jobs", "https://example.com", True),
            ("https://example.com", "https://example.com", False),
            ("https://example.com/", "https://example.com", False),
            ("", "https://example.com", False),
        ],
    )
    def test_is_verified_job_site_distinct(
        self, job_site: str, company_website: str, expected: bool
    ) -> None:
        assert roster_mod._is_verified_job_site_distinct(job_site, company_website) is expected


@pytest.mark.skip(reason="AST-721: find_job_page monolith removed; covered by decomposed AST-718–721 tests")
class TestFindJobPageAst674:
    @pytest.mark.asyncio
    async def test_distinct_job_site_delegates_before_empty_pjl_exit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        company = _company(
            job_site="https://careers.example/jobs",
            company_website="https://example.com",
            company_data={},
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        jf = AsyncMock(return_value={"state": "WATCH", "job_site": "https://careers.example/jobs"})
        monkeypatch.setattr(roster_mod, "jobs_found_process_job_site", jf)
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page(
            "https://example.com",
            short_name="acme",
            company_website="https://example.com",
            ctx={"entity_batch_id": "find_job_page-674"},
        )
        jf.assert_awaited_once_with(
            "acme",
            "https://example.com",
            "https://careers.example/jobs",
            debug=False,
            ctx={"entity_batch_id": "find_job_page-674"},
        )
        save.assert_not_called()
        assert out["state"] == "WATCH"

    @pytest.mark.asyncio
    async def test_equal_job_site_falls_through_to_pjl_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        company = _company(
            job_site="https://example.com",
            company_website="https://example.com",
            company_data={},
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        jf = AsyncMock()
        monkeypatch.setattr(roster_mod, "jobs_found_process_job_site", jf)
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page(
            "https://example.com", short_name="acme", company_website="https://example.com"
        )
        jf.assert_not_awaited()
        save.assert_called_once()
        assert out["state"] == "NO_JOBLIST"

    @pytest.mark.asyncio
    async def test_no_pjl_emits_no_llm_log(self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
        company = _company(company_website="https://example.com", company_data={})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        with caplog.at_level("INFO", logger="src.core.roster"):
            await roster_mod.find_job_page(
                "https://example.com", short_name="acme", company_website="https://example.com"
            )
        assert any("NO_JOBLIST without LLM" in r.message and "reason=no_pjl_or_nav" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_all_pjl_scrapes_failed_emits_no_llm_log(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        company = _company(
            company_website="https://example.com",
            company_data={"possible_job_links": [1], "nav_links": "1. https://example.com/jobs"},
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(return_value=("   ", {}, {}, {})),
        )
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        with caplog.at_level("INFO", logger="src.core.roster"):
            await roster_mod.find_job_page(
                "https://example.com", short_name="acme", company_website="https://example.com"
            )
        assert any(
            "NO_JOBLIST without LLM" in r.message and "reason=all_pjl_scrapes_failed" in r.message
            for r in caplog.records
        )

    @pytest.mark.asyncio
    async def test_find_assembled_select_job_page_uses_entity_log_batch_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils import logging as logging_mod

        entity_batch = "find_job_page-674-entity"
        token = logging_mod.log_batch_id.set(entity_batch)
        captured: Dict[str, Any] = {}

        async def capture_do_task(task_key: str, **kwargs: Any) -> Dict[str, Any]:
            captured["task_key"] = task_key
            captured["batch"] = logging_mod.log_batch_id.get()
            captured["ctx"] = dict(kwargs.get("ctx") or {})
            return {
                "success": True,
                "parsed_response": {"response_type": "JOBLIST_NO_JOBS", "selected_page": 1},
            }

        monkeypatch.setattr(roster_mod, "do_task", capture_do_task)
        monkeypatch.setattr(
            roster_mod,
            "_check_parse_results",
            AsyncMock(
                return_value={
                    "short_name": "acme",
                    "state": "NO_OPENINGS",
                    "job_site": "https://careers.example/jobs",
                    "response_type": "JOBLIST_NO_JOBS",
                }
            ),
        )
        try:
            await roster_mod._find_job_page_from_assembled(
                short_name="acme",
                company_website="https://example.com",
                assembled_content="asm",
                page_url_map={1: "https://careers.example/jobs"},
                page_dom_map={1: "<motion/>"},
                visible_map={1: ""},
                nav_links="",
                browser_context=MagicMock(),
                debug=False,
                ctx={"entity_batch_id": entity_batch, "astral_candidate_id": "c674"},
            )
        finally:
            logging_mod.log_batch_id.reset(token)

        assert captured["task_key"] == "select_job_page"
        assert captured["batch"] == entity_batch
        assert captured["ctx"]["entity_batch_id"] == entity_batch
        assert captured["ctx"]["astral_candidate_id"] == "c674"


class TestSaveCompany:
    def test_persists_optional_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        update = MagicMock()
        save_data = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(roster_mod, "save_company_data", save_data)
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        roster_mod._save_company(
            "acme",
            "https://acme.com",
            "NO_OPENINGS",
            "https://acme.com/jobs",
            raw_response={"response_type": "JOBLIST_NO_JOBS"},
            no_jobs_message="closed",
            parse_type="css",
            job_tag="a",
        )
        save_data.assert_called_once()
        transition.assert_called_once_with("acme", "NO_OPENINGS")


class TestCoatCheckHandlers:
    @pytest.mark.asyncio
    async def test_nav_links_requires_identifiers(self) -> None:
        with pytest.raises(ValueError, match="short_name and company_website"):
            await roster_mod._fetch_nav_links({"short_name": "", "company_website": ""})

    @pytest.mark.asyncio
    async def test_nav_links_saves_enumerated_links(self, monkeypatch: pytest.MonkeyPatch) -> None:
        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=["https://acme.com/about"]))
        monkeypatch.setattr(roster_mod, "enumerate_array", MagicMock(return_value="1. /about"))
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        out = await roster_mod._fetch_nav_links(_company())
        assert out == "1. /about"
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_nav_links_returns_none_on_empty_or_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        assert await roster_mod._fetch_nav_links(_company()) is None
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(side_effect=RuntimeError("boom")))
        assert await roster_mod._fetch_nav_links(_company()) is None

    @pytest.mark.asyncio
    async def test_prefilter_notes_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert await roster_mod._fetch_prefilter_notes({"short_name": "", "company_website": ""}) is None
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=""))
        assert await roster_mod._fetch_prefilter_notes(_company()) is None
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value="hello"))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(side_effect=RuntimeError("nav")))
        monkeypatch.setattr(roster_mod, "do_task", AsyncMock(return_value={"success": False}))
        assert await roster_mod._fetch_prefilter_notes(_company()) is None
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response([_rc_grade()]),
                }
            ),
        )
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        out = await roster_mod._fetch_prefilter_notes(_company())
        assert out == _hydrated_prefilter_notes()

    @pytest.mark.asyncio
    async def test_website_content_requires_nav_links(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert await roster_mod._fetch_website_content({"short_name": ""}) is None
        monkeypatch.setattr(roster_mod, "get_company_data", AsyncMock(return_value=None))
        assert await roster_mod._fetch_website_content(_company(company_data={"culture_links_to_explore": [1]})) is None

    @pytest.mark.asyncio
    async def test_website_content_scrapes_selected_pages(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(
            company_data={
                "culture_links_to_explore": [1],
                "nav_links": "1. https://acme.com/culture",
            },
        )
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/culture"}))

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value="culture text"))
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        out = await roster_mod._fetch_website_content(company)
        assert out == [{"url": "https://acme.com/culture", "content": "culture text"}]
        save.assert_called_once()


class TestGetCompanyData:
    @pytest.mark.asyncio
    async def test_returns_cached_or_registered_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cached = _company(company_data={"nav_links": "1. /"})
        assert await roster_mod.get_company_data(cached, "nav_links") == "1. /"
        assert await roster_mod.get_company_data(_company(), "missing_key") is None
        monkeypatch.setattr(roster_mod, "_COATCHECK_HANDLERS", {})
        assert await roster_mod.get_company_data(_company(), "nav_links") is None
        handler = AsyncMock(return_value="fresh")
        monkeypatch.setattr(roster_mod, "_COATCHECK_HANDLERS", {"nav_links": handler})
        assert await roster_mod.get_company_data(_company(), "nav_links") == "fresh"

    @pytest.mark.asyncio
    async def test_non_dict_company_data_is_treated_as_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company()
        company["company_data"] = "not-a-dict"  # type: ignore[assignment]
        handler = AsyncMock(return_value="fresh")
        monkeypatch.setattr(roster_mod, "_COATCHECK_HANDLERS", {"nav_links": handler})
        assert await roster_mod.get_company_data(company, "nav_links") == "fresh"


class TestComputeContainerIndex:
    def test_returns_zero_for_single_or_invalid_selector(self) -> None:
        assert roster_mod._compute_container_index("<div>one</div>", "div", ["Role"]) == 0
        assert roster_mod._compute_container_index("<div>one</div>", "not[a valid", ["Role"]) == 0
        assert roster_mod._compute_container_index("<div>one</div>", "motion", []) == 0

    def test_picks_container_with_matching_title(self) -> None:
        dom = "<motion>other</motion><motion>Role A</motion>"
        assert roster_mod._compute_container_index(dom, "motion", ["Role A"]) == 1


class TestFetchParseJobList:
    @pytest.mark.asyncio
    async def test_failure_and_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(roster_mod, "do_task", AsyncMock(return_value={"success": False, "error": "bad"}))
        assert await roster_mod._fetch_parse_job_list("<html/>", "acme") == {}
        save.assert_called_once()
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"job_container": ".jobs"}}),
        )
        parsed = await roster_mod._fetch_parse_job_list("<html/>", "acme")
        assert parsed["job_container"] == ".jobs"


class TestValidateParseJobListRawJobListings:
    def test_rejects_missing_selector_parts(self) -> None:
        err, listings, missing = roster_mod._validate_parse_job_list_raw_job_listings("<html/>", "", "a", [])
        assert err is not None and listings is None

    def test_rejects_invalid_selector_and_count_mismatch(self) -> None:
        err, _, _ = roster_mod._validate_parse_job_list_raw_job_listings("<html/>", "not[valid", "a", ["1"])
        assert err and "selector invalid" in err
        dom = "<div class='jobs'><a>one</a></div>"
        err, _, _ = roster_mod._validate_parse_job_list_raw_job_listings(dom, ".jobs", "a", ["1", "2"])
        assert err and "count" in err

    def test_rejects_missing_job_ids_and_blank_ids(self) -> None:
        dom = "<div class='jobs'><a>one</a><a>two</a></motion>"
        err, _, missing = roster_mod._validate_parse_job_list_raw_job_listings(dom, ".jobs", "a", ["missing", ""])
        assert err and missing == ["missing"]

    def test_accepts_matching_job_ids(self) -> None:
        dom = "<div class='jobs'><a>Role id-1</a></div>"
        err, listings, missing = roster_mod._validate_parse_job_list_raw_job_listings(dom, ".jobs", "a", ["id-1"])
        assert err is None and listings and not missing


class TestEntityAgentStory:
    def test_returns_empty_without_entries(self) -> None:
        assert roster_mod.get_entity_agent_story({}) == []

    def test_enriches_scored_response_blocks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_agent_data_for_ids",
            MagicMock(return_value={"block-1": {"block_data": json.dumps({"jobs": [{"astral_job_id": "job-1", "title": "Role"}]})}}),
        )
        scored_key = "qualify_job_listings"
        entity = {
            "astral_job_id": "job-1",
            "agent_responses": [
                {
                    "task_key": scored_key,
                    "prompt_blocks": [{"type": "RESPONSE", "id": "block-1"}],
                }
            ],
            "job_data": {"joblist_grades": {"fit": "A"}},
        }
        story = roster_mod.get_entity_agent_story(entity)
        assert story[0]["vector_grades"] == {"fit": "A"}
        assert story[0]["blocks"][0]["content"]

    def test_ast520_agent_story_phase_and_print_label(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_agent_data_for_ids",
            MagicMock(return_value={"block-1": {"block_data": '{"note": "scan insight"}'}}),
        )
        entity = {
            "astral_job_id": "job-520",
            "agent_responses": [
                {
                    "task_key": "anticipate_scan",
                    "prompt_blocks": [{"type": "RESPONSE", "id": "block-1"}],
                }
            ],
        }
        story = roster_mod.get_entity_agent_story(entity)
        assert story[0]["task_key"] == "anticipate_scan"
        assert story[0]["blocks"][0]["content"] == '{"note": "scan insight"}'


class TestFilterResponseBlock:
    def test_non_json_and_single_job_responses(self) -> None:
        assert roster_mod._filter_response_block("plain text", "job-1") == "plain text"
        assert roster_mod._filter_response_block(json.dumps({"title": "Role"}), "job-1") == json.dumps({"title": "Role"})

    def test_batch_response_filters_matching_job(self) -> None:
        payload = {"jobs": [{"astral_job_id": "job-1", "title": "Role"}]}
        out = roster_mod._filter_response_block(json.dumps(payload), "job-1")
        assert '"job-1"' in out
        assert roster_mod._filter_response_block(json.dumps({"jobs": [{"title": "old"}]}), "job-1") == ""
        assert roster_mod._filter_response_block(json.dumps({"jobs": [{"astral_job_id": "other"}]}), "job-1") == ""


class TestGetCompanyJobStateCounts:
    def test_delegates_to_database(self, monkeypatch: pytest.MonkeyPatch) -> None:
        counts = MagicMock(return_value={"WATCH": 2})
        monkeypatch.setattr(roster_mod, "get_company_job_counts", counts)
        assert roster_mod.get_company_job_state_counts("acme") == {"WATCH": 2}
        counts.assert_called_once_with("acme")


@pytest.mark.skip(reason="AST-721: find_job_page monolith removed; covered by decomposed AST-718–721 tests")
class TestFindJobPageEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_assembled_content_returns_no_joblist(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "_fetch_job_links_content", AsyncMock(return_value=("   ", {}, {}, {})))
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", short_name="acme")
        assert out["response_type"] == "NO_JOBLIST_FOUND"
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_try_links_retry_success_reaches_chain_finalize(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        monkeypatch.setattr(roster_mod, "_compute_container_index", MagicMock(return_value=0))
        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=(None, ["<a>Role id-1</a>"], [])),
        )

        sel_parse = {"response_type": "JOBLIST_TITLES", "selected_page": 2, "job_titles": ["Role"]}
        dom2 = "<motion class='jobs'><a>Role id-1</a></motion>"
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                side_effect=[
                    {
                        "success": True,
                        "parsed_response": {"response_type": "TRY_LINKS", "try_links": [2], "selected_page": 1},
                    },
                    {
                        "success": True,
                        "parsed_response": {"job_container": "motion", "job_tag": "a", "job_ids": ["id-1"]},
                        "run_next_parent_parsed": sel_parse,
                    },
                ]
            ),
        )

        page_dom = {2: dom2}

        async def fjlc(*args: Any, **kwargs: Any):
            seq = getattr(fjlc, "_n", 0)
            setattr(fjlc, "_n", seq + 1)
            if seq == 0:
                return ("content", {1: "https://acme.com/jobs"}, {}, {})
            return ("retry", {2: "https://acme.com/careers"}, page_dom, {2: "Role visible"})

        monkeypatch.setattr(roster_mod, "_fetch_job_links_content", fjlc)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", short_name="acme", debug=True)
        assert out["state"] == "WATCH"
        cd_call = roster_mod.save_company_data.call_args_list
        merged_job_list_vis = any(
            len(c[0]) > 1 and isinstance(c[0][1], dict) and c[0][1].get("job_list_visible") == "Role visible" for c in cd_call
        )
        assert merged_job_list_vis


class TestFetchSelectJobPage:
    @pytest.mark.asyncio
    async def test_raises_when_parsed_response_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "do_task", AsyncMock(return_value={"parsed_response": None, "error": "bad"}))
        with pytest.raises(ValueError, match="select_job_page failed"):
            await roster_mod._fetch_select_job_page("content", "acme")

    @pytest.mark.asyncio
    async def test_returns_parsed_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"parsed_response": {"response_type": "JOBLIST_TITLES"}}),
        )
        out = await roster_mod._fetch_select_job_page("content", "acme")
        assert out["response_type"] == "JOBLIST_TITLES"


class TestRunCompanyTaskEdgeCases:
    @pytest.mark.asyncio
    async def test_locate_error_without_configured_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "find_job_page", AsyncMock(return_value={"error": "boom"}))
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        cfg = roster_mod.ROSTER_CONFIG["locate_job_page"]
        roster_mod.ROSTER_CONFIG["locate_job_page"] = {**cfg, "error_state": None}
        try:
            out = await roster_mod.run_company_task("TO_WATCH", _company(), "batch-1")
        finally:
            roster_mod.ROSTER_CONFIG["locate_job_page"] = cfg
        assert out["total_errors"] == 1
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_watch_failure_without_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _Gazer:
            @staticmethod
            async def process_gazer_batch(
                _bid: str, _entities: List[Dict[str, Any]], debug: bool = False, **_kwargs: Any
            ):
                return []

        monkeypatch.setitem(__import__("sys").modules, "src.core.gazer", _Gazer)
        cfg = roster_mod.ROSTER_CONFIG["gaze"]
        roster_mod.ROSTER_CONFIG["gaze"] = {**cfg, "error_state": None}
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        try:
            out = await roster_mod.run_company_task("WATCH", _company(), "batch-1")
        finally:
            roster_mod.ROSTER_CONFIG["gaze"] = cfg
        assert out["total_passed"] == 1
        transition.assert_not_called()


class TestPrefilterCompanyEdgeCases:
    @pytest.mark.asyncio
    async def test_exception_without_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("hello", "https://acme.com")))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        monkeypatch.setattr(roster_mod, "do_task", AsyncMock(side_effect=RuntimeError("boom")))
        cfg = roster_mod.ROSTER_CONFIG["prefilter"]
        roster_mod.ROSTER_CONFIG["prefilter"] = {**cfg, "error_state": None}
        try:
            out = await roster_mod.prefilter_company("acme", "https://acme.com")
        finally:
            roster_mod.ROSTER_CONFIG["prefilter"] = cfg
        assert out["error"] == "boom"
        assert out["state"] is None


class TestSaveCompanyBranches:
    def test_parse_instructions_take_precedence_over_legacy_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        update = MagicMock()
        save_data = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(roster_mod, "save_company_data", save_data)
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        roster_mod._save_company(
            "acme",
            "https://acme.com",
            "WATCH",
            "https://acme.com/jobs",
            parse_instructions={"container": ".jobs"},
            parse_type="css",
            job_tag="a",
        )
        save_data.assert_called_once_with("acme", {"parse_instructions": {"container": ".jobs"}})

    def test_skips_company_data_save_when_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save_data = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", MagicMock())
        monkeypatch.setattr(roster_mod, "save_company_data", save_data)
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        roster_mod._save_company("acme", "https://acme.com", "WATCH", "https://acme.com/jobs")
        save_data.assert_not_called()


class TestFetchPrefilterNotesBranches:
    @pytest.mark.asyncio
    async def test_persists_optional_fields_and_handles_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value="hello"))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=["https://acme.com/about"]))
        monkeypatch.setattr(roster_mod, "enumerate_array", MagicMock(return_value="1. /about"))
        _patch_prefilter_candidate_rubric(monkeypatch)
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(return_value={**_company(), "candidate_id": "cand-1"}),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response(
                        _prefilter_grades(
                            {"grade": "A", "vector": "fit", "confidence": 5, "reason": "ok"},
                        ),
                        possible_job_links=[1],
                        culture_links_to_explore=[2],
                    ),
                }
            ),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        assert await roster_mod._fetch_prefilter_notes({**_company(), "candidate_id": "cand-1"}) == (
            _hydrated_prefilter_notes(include_fit=True)
        )
        save.assert_called_once()

        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(side_effect=RuntimeError("boom")))
        assert await roster_mod._fetch_prefilter_notes(_company()) is None


class TestWebsiteContentBranches:
    @pytest.mark.asyncio
    async def test_handles_missing_culture_links_and_scrape_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Coat-check may fetch nav_links via save_company_data; in-memory fixtures have no DB row.
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        assert await roster_mod._fetch_website_content(_company(company_data={})) is None
        company = _company(company_data={"culture_links_to_explore": [], "nav_links": "1. /culture"})
        assert await roster_mod._fetch_website_content(company) is None
        company = _company(company_data={"culture_links_to_explore": [9], "nav_links": "1. /culture"})
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={}))
        assert await roster_mod._fetch_website_content(company) is None

        company = _company(company_data={"culture_links_to_explore": [1], "nav_links": "1. https://acme.com/culture"})

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/culture"}))
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(side_effect=RuntimeError("blocked")))
        assert await roster_mod._fetch_website_content(company) is None

        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value="   "))
        assert await roster_mod._fetch_website_content(company) is None

    @pytest.mark.asyncio
    async def test_logs_outer_fetch_failures(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"culture_links_to_explore": [1], "nav_links": "1. https://acme.com/culture"})
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/culture"}))

        @asynccontextmanager
        async def _browser():
            raise RuntimeError("browser down")
            yield AsyncMock()  # pragma: no cover

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        assert await roster_mod._fetch_website_content(company) is None

    @pytest.mark.asyncio
    async def test_reraises_value_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"culture_links_to_explore": [1], "nav_links": "1. https://acme.com/culture"})
        monkeypatch.setattr(roster_mod, "get_company_data", AsyncMock(side_effect=ValueError("bad key")))
        with pytest.raises(ValueError, match="bad key"):
            await roster_mod._fetch_website_content(company)


class TestFetchNavLinksBranches:
    @pytest.mark.asyncio
    async def test_reraises_value_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        @asynccontextmanager
        async def _browser():
            raise ValueError("bad nav")
            yield AsyncMock()  # pragma: no cover

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        with pytest.raises(ValueError, match="bad nav"):
            await roster_mod._fetch_nav_links(_company())


class TestComputeContainerIndexBranches:
    def test_returns_zero_when_titles_do_not_match(self) -> None:
        dom = "<motion>other</motion><motion>still other</motion>"
        assert roster_mod._compute_container_index(dom, "motion", ["Role A"]) == 0

    def test_returns_zero_when_titles_are_blank(self) -> None:
        dom = "<motion>Role A</motion><motion>Role B</motion>"
        assert roster_mod._compute_container_index(dom, "motion", ["   "]) == 0


class TestRunCompanyTaskGazeBranches:
    @pytest.mark.asyncio
    async def test_gaze_failure_without_error_state_skips_transition(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _Gazer:
            @staticmethod
            async def process_gazer_batch(
                _bid: str, _entities: List[Dict[str, Any]], debug: bool = False, **_kwargs: Any
            ):
                return [{"status": "failure", "message": "gaze failed"}]

        monkeypatch.setitem(__import__("sys").modules, "src.core.gazer", _Gazer)
        cfg = roster_mod.ROSTER_CONFIG["gaze"]
        roster_mod.ROSTER_CONFIG["gaze"] = {**cfg, "error_state": None}
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        try:
            out = await roster_mod.run_company_task("WATCH", _company(), "batch-1")
        finally:
            roster_mod.ROSTER_CONFIG["gaze"] = cfg
        assert out["total_errors"] == 1
        transition.assert_not_called()


@pytest.mark.skip(reason="AST-721: find_job_page monolith removed; covered by decomposed AST-718–721 tests")
class TestFindJobPageTryLinksBranches:
    @pytest.mark.asyncio
    async def test_try_links_with_empty_retry_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(side_effect=[("content", {1: "https://acme.com/jobs"}, {}, {}), ("   ", {}, {}, {})]),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"response_type": "TRY_LINKS", "try_links": [2], "selected_page": 1}}),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", short_name="acme", debug=False)
        assert out["state"] == "NO_JOBLIST"

    @pytest.mark.asyncio
    async def test_try_links_retry_still_not_joblist(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(
                side_effect=[
                    ("content", {1: "https://acme.com/jobs"}, {}, {}),
                    ("retry", {2: "https://acme.com/careers"}, {}, {}),
                ]
            ),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                side_effect=[
                    {"success": True, "parsed_response": {"response_type": "TRY_LINKS", "try_links": [2], "selected_page": 1}},
                    {"success": True, "parsed_response": {"response_type": "TRY_LINKS", "try_links": [], "selected_page": 1}},
                ]
            ),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", short_name="acme", debug=True)
        assert out["state"] == "NO_JOBLIST"


class TestFetchJobLinksContentBranches:
    @pytest.mark.asyncio
    async def test_records_visible_text_without_dom_or_new_links(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/jobs"}))
        page = AsyncMock()
        monkeypatch.setattr(roster_mod, "get_page", AsyncMock(return_value=page))
        monkeypatch.setattr(roster_mod, "extract_visible_text", AsyncMock(return_value={"text": ""}))
        monkeypatch.setattr(roster_mod, "extract_page_dom", AsyncMock(return_value=""))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=["https://acme.com/jobs"]))
        monkeypatch.setattr(roster_mod, "close_page", AsyncMock())
        content, url_map, dom_map, vis_map = await roster_mod._fetch_job_links_content(
            [1, 1],
            "1. https://acme.com/jobs",
            AsyncMock(),
            debug=False,
        )
        assert "(no visible text)" in content
        assert url_map[1] == "https://acme.com/jobs"
        assert dom_map == {}
        assert vis_map == {}

    @pytest.mark.asyncio
    async def test_records_scrape_failure_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/jobs"}))
        monkeypatch.setattr(roster_mod, "get_page", AsyncMock(side_effect=RuntimeError("blocked")))
        content, _, _, _ = await roster_mod._fetch_job_links_content(
            [1],
            "1. https://acme.com/jobs",
            AsyncMock(),
            debug=False,
        )
        assert "scrape failed" in content


class TestCheckParseResultsBranches:
    @pytest.mark.asyncio
    async def test_no_jobs_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        out = await roster_mod._check_parse_results(
            {"no_jobs_message": "closed"},
            "JOBLIST_NO_JOBS",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {},
            debug=False,
        )
        assert out["state"] == "NO_OPENINGS"

    @pytest.mark.asyncio
    async def test_missing_containers_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=[]))
        out = await roster_mod._check_parse_results(
            {"job_titles": ["Role"]},
            "JOBLIST_TITLES",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {1: "<motion>Role</motion>"},
            selected_page=1,
            debug=False,
        )
        assert out["state"] == "CANNOT_PARSE_JOB_SITE"

    @pytest.mark.asyncio
    async def test_missing_containers_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=[]))
        out = await roster_mod._check_parse_results(
            {"job_titles": ["Role"]},
            "JOBLIST_TITLES",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {1: "<motion>Role</motion>"},
            selected_page=1,
            debug=True,
        )
        assert out["state"] == "CANNOT_PARSE_JOB_SITE"


class TestDeriveShortnameBranches:
    def test_uses_single_label_host(self) -> None:
        assert roster_mod._derive_shortname_from_url("custom://singlehost/path") == "singlehost"


class TestFetchPrefilterNotesMoreBranches:
    @pytest.mark.asyncio
    async def test_returns_none_without_reasons_or_nav_links(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value="hello"))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response([_rc_grade(grade="X")]),
                }
            ),
        )
        assert await roster_mod._fetch_prefilter_notes(_company()) is None


class TestEntityAgentStoryBranches:
    def test_skips_invalid_block_refs_and_labels_duplicates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_agent_data_for_ids",
            MagicMock(return_value={"b1": {"block_data": "one"}, "b2": {"block_data": "two"}}),
        )
        entity = {
            "agent_responses": [
                {
                    "task_key": "parse_job_list",
                    "prompt_blocks": ["bad", {"type": "NO_CACHE", "id": "b1"}, {"type": "NO_CACHE", "id": "b2"}],
                }
            ]
        }
        story = roster_mod.get_entity_agent_story(entity)
        assert story[0]["blocks"][0]["type"] == "NO_CACHE"
        assert story[0]["blocks"][1]["type"] == "NO_CACHE (2)"

    def test_scored_response_without_job_id_keeps_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_agent_data_for_ids",
            MagicMock(return_value={"block-1": {"block_data": json.dumps({"jobs": [{"title": "Role"}]})}}),
        )
        scored_key = next(key for key, cfg in TASK_CONFIG.items() if cfg.get("scored"))
        entity = {
            "astral_job_id": "job-1",
            "agent_responses": [{"task_key": scored_key, "prompt_blocks": [{"type": "RESPONSE", "id": "block-1"}]}],
        }
        story = roster_mod.get_entity_agent_story(entity)
        assert story[0]["blocks"][0]["content"] == ""


class TestRosterCoverageGaps:
    def test_derive_shortname_uses_single_part_domain(self) -> None:
        assert roster_mod._derive_shortname_from_url("https://localhost/jobs") == "localhost"

    @pytest.mark.asyncio
    async def test_fetch_job_links_content_dom_new_links_and_scrape_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "wait_for_careers_list_readiness",
            AsyncMock(
                return_value={
                    "ready": True,
                    "outcome": "ready",
                    "visible_chars": 0,
                    "listing_hits": 0,
                    "wait_ms": 0,
                    "load_all_jobs_ran": False,
                }
            ),
        )
        monkeypatch.setattr(
            roster_mod,
            "parse_enumerate_array",
            MagicMock(return_value={1: "https://acme.com/jobs", 2: "https://acme.com/about"}),
        )
        page = AsyncMock()
        monkeypatch.setattr(roster_mod, "get_page", AsyncMock(side_effect=[page, RuntimeError("blocked")]))
        monkeypatch.setattr(roster_mod, "close_page", AsyncMock())
        monkeypatch.setattr(roster_mod, "extract_visible_text", AsyncMock(return_value={"text": ""}))
        monkeypatch.setattr(roster_mod, "extract_page_dom", AsyncMock(return_value=""))
        monkeypatch.setattr(
            roster_mod,
            "extract_site_page_list",
            AsyncMock(return_value=["https://acme.com/jobs", "https://acme.com/new"]),
        )
        content, url_map, dom_map, _vis_map = await roster_mod._fetch_job_links_content(
            [1, 2],
            "1. https://acme.com/jobs\n2. https://acme.com/about",
            AsyncMock(),
            debug=True,
        )
        assert "(no visible text)" in content
        assert "NEW LINKS" in content
        assert "scrape failed" in content
        assert url_map[1] == "https://acme.com/jobs"
        assert 1 not in dom_map

    @pytest.mark.asyncio
    async def test_check_parse_results_logs_empty_containers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=[]))
        out = await roster_mod._check_parse_results(
            {"job_titles": ["Role"]},
            "JOBLIST_TITLES",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {1: "<div>Role</div>"},
            selected_page=1,
            debug=True,
        )
        assert out["state"] == "CANNOT_PARSE_JOB_SITE"

    @pytest.mark.asyncio
    async def test_check_parse_results_logs_no_jobs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        out = await roster_mod._check_parse_results(
            {"no_jobs_message": "closed"},
            "JOBLIST_NO_JOBS",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {},
            debug=True,
        )
        assert out["state"] == "NO_OPENINGS"

    def test_derive_shortname_strips_www_from_bare_domain(self) -> None:
        assert roster_mod._derive_shortname_from_url("www.acme.com") == "acme"

    def test_derive_shortname_strips_www_from_single_label_host(self) -> None:
        assert roster_mod._derive_shortname_from_url("https://www.lan/jobs") == "lan"

    @pytest.mark.asyncio
    async def test_prefilter_notes_returns_saved_notes_with_nav_links(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value="homepage"))
        monkeypatch.setattr(
            roster_mod,
            "extract_site_page_list",
            AsyncMock(return_value=["https://Acme.com/careers/"]),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={
                "success": True,
                "parsed_response": _encoded_prefilter_response(
                    [_rc_grade()],
                    possible_job_links=[1],
                    culture_links_to_explore=[2],
                ),
            }),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        assert await roster_mod._fetch_prefilter_notes(_company()) == _hydrated_prefilter_notes()
        saved = save.call_args[0][1]
        assert saved["possible_joblist_links"] == ["acme.com/careers"]
        save.assert_called_once()

    def test_validate_parse_job_list_skips_blank_job_ids(self) -> None:
        dom = "<motion><a>one</a><a>two</a></motion>"
        err, listings, missing = roster_mod._validate_parse_job_list_raw_job_listings(dom, "motion", "a", ["", "two"])
        assert err is None and listings and not missing

    @pytest.mark.asyncio
    async def test_find_job_page_try_links_empty_retry_keeps_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(side_effect=[("content", {1: "https://acme.com/jobs"}, {}, {}), ("   ", {}, {}, {})]),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"response_type": "TRY_LINKS", "try_links": [2], "selected_page": 1}}),
        )
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", short_name="acme", debug=True)
        assert out["state"] == "NO_JOBLIST"
        save.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_job_page_try_links_retry_failure_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(company_data={"possible_job_links": [1], "nav_links": "1. https://acme.com/jobs"})
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(side_effect=[("content", {1: "https://acme.com/jobs"}, {}, {}), ("retry", {2: "https://acme.com/careers"}, {}, {})]),
        )
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                side_effect=[
                    {"success": True, "parsed_response": {"response_type": "TRY_LINKS", "try_links": [2], "selected_page": 1}},
                    {"success": True, "parsed_response": {"response_type": "NOPE", "selected_page": 2}},
                ]
            ),
        )
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _browser)
        out = await roster_mod.find_job_page("https://acme.com", short_name="acme", debug=False)
        assert out["state"] == "NO_JOBLIST"

    @pytest.mark.asyncio
    async def test_watch_failure_transitions_configured_error_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import src.core.gazer as gazer_mod

        monkeypatch.setattr(
            gazer_mod,
            "process_gazer_batch",
            AsyncMock(return_value=[{"status": "failure", "message": "gaze failed"}]),
        )
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        out = await roster_mod.run_company_task("WATCH", _company(), "batch-1")
        assert out["total_errors"] == 1
        transition.assert_called_once_with("acme", ROSTER_CONFIG["gaze"]["error_state"])

    @pytest.mark.asyncio
    async def test_prefilter_notes_returns_none_without_reasons(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value="homepage"))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=["https://acme.com/about"]))
        monkeypatch.setattr(roster_mod, "enumerate_array", MagicMock(return_value="1. /about"))
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _encoded_prefilter_response([_rc_grade(grade="X")]),
                }
            ),
        )
        assert await roster_mod._fetch_prefilter_notes(_company()) is None

    def test_compute_container_index_matches_title_in_later_container(self) -> None:
        dom = "<motion>other</motion><motion>Role A</motion>"
        assert roster_mod._compute_container_index(dom, "motion", ["Role A"]) == 1


class TestMakeLocateParseResolver469:
    def test_non_dict_parsed_returns_empty(self) -> None:
        r = roster_mod.make_locate_parse_resolver({1: "x"}, {1: "v"})
        assert r(None) == ("", "")  # type: ignore[arg-type]

    def test_selected_page_that_cannot_convert(self) -> None:
        r = roster_mod.make_locate_parse_resolver({1: "<div>X</div>"}, {})
        assert r({"selected_page": {}, "job_titles": ["X"]}) == ("", "")

    def test_missing_selected_page(self) -> None:
        r = roster_mod.make_locate_parse_resolver({1: "<div>X</div>"}, {})
        assert r({"job_titles": ["X"]}) == ("", "")

    def test_empty_dom_fallback_visible(self) -> None:
        r = roster_mod.make_locate_parse_resolver({1: "  "}, {1: " vt "})
        c, v = r({"selected_page": 1, "job_titles": ["Dev"]})
        assert c == "" and v == "vt"

    def test_culled_containers_and_visible_strip(self) -> None:
        html = "<motion><a>Dev</a></motion>"
        r = roster_mod.make_locate_parse_resolver({1: html}, {1: " vis "})
        c, v = r({"selected_page": "1", "job_titles": ["Dev"]})
        assert "Dev" in c and v == "vis"

    def test_resolver_no_matching_containers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=[]))
        r = roster_mod.make_locate_parse_resolver({1: "<p>plain</p>"}, {1: "only_vis"})
        c, v = r({"selected_page": 1, "job_titles": ["Absent"]})
        assert c == "" and v == "only_vis"


class TestStripCompanyDataKeys469:
    def test_no_company_early_exit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=None))
        upd = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", upd)
        roster_mod._strip_company_data_keys("sn", ("job_list_visible",))
        upd.assert_not_called()

    def test_key_absent_skips_save(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(return_value={"company_data": {"keep": 1}}),
        )
        upd = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", upd)
        roster_mod._strip_company_data_keys("sn", ("nope_field",))
        upd.assert_not_called()

    def test_strips_registered_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_company",
            MagicMock(return_value={"company_data": {"job_list_visible": "x", "keep": True}}),
        )
        upd = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", upd)
        roster_mod._strip_company_data_keys("sn", ("job_list_visible",))
        upd.assert_called_once_with("sn", company_data={"keep": True})


@pytest.mark.asyncio
async def test_run_company_task_jobs_found_watch_counts_passed(monkeypatch: pytest.MonkeyPatch) -> None:
    ent = _company(state="JOBS_FOUND", job_site="https://jobs")
    monkeypatch.setattr(
        roster_mod,
        "jobs_found_process_job_site",
        AsyncMock(return_value={"state": "WATCH"}),
    )
    out = await roster_mod.run_company_task("JOBS_FOUND", ent, "b1")
    assert out["total_passed"] == 1


@pytest.mark.asyncio
async def test_run_company_task_jobs_found_other_state_counts_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    ent = _company(state="JOBS_FOUND", job_site="https://jobs")
    monkeypatch.setattr(
        roster_mod,
        "jobs_found_process_job_site",
        AsyncMock(return_value={"state": "NO_JOBLIST"}),
    )
    out = await roster_mod.run_company_task("JOBS_FOUND", ent, "b1")
    assert out["total_failed"] == 1


@pytest.mark.asyncio
async def test_run_company_task_jobs_found_error_moves_locate_error_state(monkeypatch: pytest.MonkeyPatch) -> None:
    ent = _company(state="JOBS_FOUND", job_site="https://jobs")
    monkeypatch.setattr(
        roster_mod,
        "jobs_found_process_job_site",
        AsyncMock(return_value={"error": "boom", "state": "NO_JOBLIST"}),
    )
    transition = MagicMock()
    monkeypatch.setattr(roster_mod, "transition_company_state", transition)
    await roster_mod.run_company_task("JOBS_FOUND", ent, "b1")
    transition.assert_called_once_with("acme", ROSTER_CONFIG["locate_job_page"]["error_state"])


@pytest.mark.asyncio
async def test_run_company_task_jobs_found_error_without_error_state_skips_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """215→217 false branch: dispatcher error cleared in config."""
    ent = _company(state="JOBS_FOUND", job_site="https://jobs")
    monkeypatch.setattr(
        roster_mod,
        "jobs_found_process_job_site",
        AsyncMock(return_value={"error": "boom"}),
    )
    loc = dict(ROSTER_CONFIG["locate_job_page"])
    loc.pop("error_state", None)
    monkeypatch.setitem(roster_mod.ROSTER_CONFIG, "locate_job_page", loc)
    transition = MagicMock()
    monkeypatch.setattr(roster_mod, "transition_company_state", transition)
    await roster_mod.run_company_task("JOBS_FOUND", ent, "b1")
    transition.assert_not_called()


class TestJobsFoundProcessJobSite469:
    @pytest.mark.asyncio
    async def test_missing_site_response(self) -> None:
        out = await roster_mod.jobs_found_process_job_site("acme", "https://corp", "")
        assert out["response_type"] == "MISSING_JOB_SITE"
        assert out["job_site"] == ""

    @pytest.mark.asyncio
    async def test_scrape_empty_preserves_pre_run_job_site(self, monkeypatch: pytest.MonkeyPatch) -> None:
        company = _company(
            job_site="https://careers.example/jobs",
            company_website="https://example.com",
        )
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(roster_mod, "_strip_company_data_keys", MagicMock())
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("t", "")))
        monkeypatch.setattr(roster_mod, "enumerate_array", MagicMock(return_value="nl"))
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "update_company", update)
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(return_value=("   ", {}, {}, {})),
        )

        @asynccontextmanager
        async def _ctx():
            yield MagicMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _ctx)
        out = await roster_mod.jobs_found_process_job_site(
            "acme", "https://example.com", "https://careers.example/jobs", debug=False,
        )
        assert out["response_type"] == "JOBS_FOUND_SCRAPE_EMPTY"
        assert update.call_args.kwargs["job_site"] == "https://careers.example/jobs"

    @pytest.mark.asyncio
    async def test_scrape_error_without_transition_when_no_error_state(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "_strip_company_data_keys", MagicMock())
        loc = dict(ROSTER_CONFIG["locate_job_page"])
        loc["error_state"] = None
        monkeypatch.setitem(roster_mod.ROSTER_CONFIG, "locate_job_page", loc)
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(side_effect=IOError()))
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        await roster_mod.jobs_found_process_job_site(
            "acme", "https://corp", "https://jobs", debug=False,
        )
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_scrape_error_transition_when_error_state_present(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "_strip_company_data_keys", MagicMock())
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(side_effect=ValueError()))
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        await roster_mod.jobs_found_process_job_site(
            "acme", "https://corp", "https://jobs", debug=False,
        )
        transition.assert_called_once_with("acme", ROSTER_CONFIG["locate_job_page"]["error_state"])

    @pytest.mark.asyncio
    async def test_redirect_writes_final_job_site_then_empty_bundle(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "_strip_company_data_keys", MagicMock())
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("t", "https://final")))
        monkeypatch.setattr(roster_mod, "enumerate_array", MagicMock(return_value="nl"))
        monkeypatch.setattr(roster_mod, "update_company", MagicMock())
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(return_value=("   ", {}, {}, {})),
        )
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())

        @asynccontextmanager
        async def _ctx():
            yield MagicMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _ctx)
        out = await roster_mod.jobs_found_process_job_site(
            "acme", "https://corp", "https://other", debug=False,
        )
        assert out["response_type"] == "JOBS_FOUND_SCRAPE_EMPTY"

    @pytest.mark.asyncio
    async def test_nonempty_content_calls_find_chain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "_strip_company_data_keys", MagicMock())
        monkeypatch.setattr(roster_mod, "get_visible_text", AsyncMock(return_value=("txt", "")))
        monkeypatch.setattr(roster_mod, "enumerate_array", MagicMock(return_value="nl"))
        inner = AsyncMock(return_value={"state": "WATCH"})
        monkeypatch.setattr(roster_mod, "_find_job_page_from_assembled", inner)
        monkeypatch.setattr(
            roster_mod,
            "_fetch_job_links_content",
            AsyncMock(return_value=("dom", {1: "u"}, {1: "<a/>"}, {})),
        )

        @asynccontextmanager
        async def _ctx():
            yield MagicMock()

        monkeypatch.setattr(roster_mod, "create_browser_context", _ctx)
        await roster_mod.jobs_found_process_job_site(
            "acme", "https://corp", "https://jobs", debug=False, ctx={"k": True},
        )
        inner.assert_awaited_once()
        assert inner.await_args.kwargs["ctx"] == {"k": True}


@pytest.mark.asyncio
async def test_find_assembled_do_task_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(roster_mod, "do_task", AsyncMock(return_value={"success": False, "error": "bad"}))
    saver = MagicMock()
    monkeypatch.setattr(roster_mod, "_save_company", saver)
    out = await roster_mod._find_job_page_from_assembled(
        short_name="acme",
        company_website="https://cw",
        assembled_content="asm",
        page_url_map={1: "https://jobs"},
        page_dom_map={1: "<motion/>"},
        visible_map={1: ""},
        nav_links="",
        browser_context=MagicMock(),
        debug=False,
        ctx=None,
    )
    assert out["response_type"] == "SELECT_FAILED"
    saver.assert_called()


@pytest.mark.asyncio
async def test_find_assembled_non_dict_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        roster_mod,
        "do_task",
        AsyncMock(return_value={"success": True, "parsed_response": [], "run_next_parent_parsed": None}),
    )
    saver = MagicMock()
    monkeypatch.setattr(roster_mod, "_save_company", saver)
    out = await roster_mod._find_job_page_from_assembled(
        short_name="acme",
        company_website="https://cw",
        assembled_content="asm",
        page_url_map={1: "https://jobs"},
        page_dom_map={1: "<motion/>"},
        visible_map={1: ""},
        nav_links="",
        browser_context=MagicMock(),
        debug=False,
        ctx=None,
    )
    assert out["response_type"] == "NO_JOBLIST_FOUND"
    saver.assert_called()


@pytest.mark.asyncio
async def test_find_assembled_try_links_exits_when_no_links(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        roster_mod,
        "do_task",
        AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {"response_type": "TRY_LINKS", "try_links": []},
                "run_next_parent_parsed": None,
            },
        ),
    )
    saver = MagicMock()
    monkeypatch.setattr(roster_mod, "_save_company", saver)
    out = await roster_mod._find_job_page_from_assembled(
        short_name="acme",
        company_website="https://cw",
        assembled_content="asm",
        page_url_map={},
        page_dom_map={},
        visible_map={},
        nav_links="",
        browser_context=MagicMock(),
        debug=False,
        ctx=None,
    )
    assert out["response_type"] == "TRY_LINKS"
    saver.assert_called()


@pytest.mark.asyncio
async def test_find_joblist_titles_routes_after_chain_when_run_next_parent_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """562→563 JOBLIST_TITLES + pp not None ⇒ `_finalize_joblist_titles_after_chain`."""

    parsed_top = {"response_type": "JOBLIST_TITLES", "job_titles": ["Dev"], "selected_page": 1}

    monkeypatch.setattr(
        roster_mod,
        "do_task",
        AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {"job_container": "div", "job_tag": "a"},
                "run_next_parent_parsed": parsed_top,
            },
        ),
    )
    fin = AsyncMock(return_value={"state": "DONE"})
    monkeypatch.setattr(roster_mod, "_finalize_joblist_titles_after_chain", fin)
    out = await roster_mod._find_job_page_from_assembled(
        short_name="acme",
        company_website="https://cw",
        assembled_content="asm",
        page_url_map={1: "https://js"},
        page_dom_map={1: "<div/>"},
        visible_map={},
        nav_links="",
        browser_context=MagicMock(),
        debug=False,
        ctx=None,
    )
    assert out["state"] == "DONE"
    fin.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_joblist_titles_routes_select_only_when_run_next_parent_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """567: JOBLIST_TITLES and no run_next_parent_parsed → `_finalize_joblist_titles_select_only`."""
    monkeypatch.setattr(
        roster_mod,
        "do_task",
        AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {
                    "response_type": "JOBLIST_TITLES",
                    "job_titles": ["Dev"],
                    "selected_page": 1,
                },
            },
        ),
    )
    fin_sel = AsyncMock(return_value={"state": "PICKED_SELECT_ONLY"})
    fin_chain = AsyncMock()
    monkeypatch.setattr(roster_mod, "_finalize_joblist_titles_select_only", fin_sel)
    monkeypatch.setattr(roster_mod, "_finalize_joblist_titles_after_chain", fin_chain)
    out = await roster_mod._find_job_page_from_assembled(
        short_name="acme",
        company_website="https://cw",
        assembled_content="asm",
        page_url_map={1: "https://js"},
        page_dom_map={1: "<div/>"},
        visible_map={1: ""},
        nav_links="",
        browser_context=MagicMock(),
        debug=False,
        ctx=None,
    )
    assert out["state"] == "PICKED_SELECT_ONLY"
    fin_sel.assert_awaited_once()
    fin_chain.assert_not_called()


class TestFinalize469BranchCoverage:
    @pytest.mark.asyncio
    async def test_after_chain_empty_containers_debug_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=[]))
        saver = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", saver)
        out = await roster_mod._finalize_joblist_titles_after_chain(
            {"job_titles": ["Absent"], "response_type": "JOBLIST_TITLES"},
            {"parsed_response": {"job_container": "m", "job_tag": "a"}},
            "acme",
            "https://cw",
            "https://js",
            {1: "<div/>"},
            {},
            1,
            "JOBLIST_TITLES",
            False,
            {},
        )
        assert out["state"] == "CANNOT_PARSE_JOB_SITE"

    @pytest.mark.asyncio
    async def test_after_chain_whitespace_only_container_notes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["f"]))
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        out = await roster_mod._finalize_joblist_titles_after_chain(
            {"job_titles": ["Dev"], "response_type": "JOBLIST_TITLES"},
            {"parsed_response": {"job_container": "  \t", "job_tag": "a"}},
            "acme",
            "https://cw",
            "https://js",
            {1: "<div><a>Dev</a></div>"},
            {},
            1,
            "JOBLIST_TITLES",
            False,
            {},
        )
        assert out["state"] == "CANNOT_PARSE_JOB_SITE"

    @pytest.mark.asyncio
    async def test_after_chain_value_error_vis_empty_still_watch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["f"]))
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=(None, [], [])),
        )
        monkeypatch.setattr(roster_mod, "_compute_container_index", MagicMock(return_value=0))
        out = await roster_mod._finalize_joblist_titles_after_chain(
            {"job_titles": ["Dev"], "response_type": "JOBLIST_TITLES"},
            {"parsed_response": {"job_container": "div", "job_tag": "a"}},
            "acme",
            "https://cw",
            "https://js",
            {"2.5": "<div><a>Dev</a></div>"},
            {},
            "2.5",
            "JOBLIST_TITLES",
            False,
            {},
        )
        assert out["state"] == "WATCH"

    @pytest.mark.asyncio
    async def test_after_chain_persists_job_list_visible_strip(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["f"]))
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=(None, [], [])),
        )
        monkeypatch.setattr(roster_mod, "_compute_container_index", MagicMock(return_value=0))
        out = await roster_mod._finalize_joblist_titles_after_chain(
            {"job_titles": ["Dev"], "response_type": "JOBLIST_TITLES"},
            {"parsed_response": {"job_container": "div", "job_tag": "a"}},
            "acme",
            "https://cw",
            "https://js",
            {1: "<div><a>Dev</a></div>"},
            {1: "  persisted  "},
            1,
            "JOBLIST_TITLES",
            False,
            {},
        )
        assert out["state"] == "WATCH"

    @pytest.mark.asyncio
    async def test_select_only_string_page_int_error_yields_watch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["s"]))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_parse_job_list",
            AsyncMock(side_effect=[
                {"job_container": "div", "job_tag": "a", "job_ids": []},
                {"job_container": "div", "job_tag": "a", "job_ids": []},
            ]),
        )
        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=(None, [], [])),
        )
        monkeypatch.setattr(roster_mod, "_compute_container_index", MagicMock(return_value=0))
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        out = await roster_mod._finalize_joblist_titles_select_only(
            {"job_titles": ["Dev"], "response_type": "JOBLIST_TITLES"},
            "acme",
            "https://cw",
            "https://js",
            {"blob": "<div><a>H</a></div>"},
            "blob",
            "JOBLIST_TITLES",
            False,
            {},
            {},
        )
        assert out["state"] == "WATCH"

    @pytest.mark.asyncio
    async def test_select_only_persist_visible_on_int_coercion_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["s"]))
        monkeypatch.setattr(
            roster_mod,
            "_fetch_parse_job_list",
            AsyncMock(side_effect=[
                {"job_container": "div", "job_tag": "a", "job_ids": []},
                {"job_container": "div", "job_tag": "a", "job_ids": []},
            ]),
        )
        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=(None, [], [])),
        )
        monkeypatch.setattr(roster_mod, "_compute_container_index", MagicMock(return_value=0))
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        out = await roster_mod._finalize_joblist_titles_select_only(
            {"job_titles": ["Dev"], "response_type": "JOBLIST_TITLES"},
            "acme",
            "https://cw",
            "https://js",
            {9: "<div><a>H</a></div>"},
            9,
            "JOBLIST_TITLES",
            False,
            {},
            {9: " hello "},
        )
        assert out["state"] == "WATCH"

    @pytest.mark.asyncio
    async def test_after_chain_no_dom_for_selected_page(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        saver = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", saver)
        out = await roster_mod._finalize_joblist_titles_after_chain(
            {"job_titles": ["X"], "response_type": "JOBLIST_TITLES"},
            {"parsed_response": {"job_container": "d", "job_tag": "a"}},
            "acme",
            "https://cw",
            "https://js",
            {},  # dom missing for selected page
            {},
            9,
            "JOBLIST_TITLES",
            False,
            {},
        )
        assert out["state"] == "NO_JOBLIST"
        saver.assert_called_once()

    @pytest.mark.asyncio
    async def test_after_chain_empty_containers_debug_true_logs(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=[]))
        monkeypatch.setattr(roster_mod, "_save_company", MagicMock())
        log_note = MagicMock()
        monkeypatch.setattr(roster_mod.logger, "test", log_note)
        await roster_mod._finalize_joblist_titles_after_chain(
            {"job_titles": ["Y"], "response_type": "JOBLIST_TITLES"},
            {"parsed_response": {"job_container": "m", "job_tag": "a"}},
            "acme",
            "https://cw",
            "https://js",
            {1: "<x/>"},
            {},
            1,
            "JOBLIST_TITLES",
            True,
            {},
        )
        log_note.assert_called()

    @pytest.mark.asyncio
    async def test_after_chain_validation_error_stores_notes(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(roster_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(roster_mod, "find_job_containers", MagicMock(return_value=["fragment"]))
        saver = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", saver)
        monkeypatch.setattr(
            roster_mod,
            "_validate_parse_job_list_raw_job_listings",
            MagicMock(return_value=("parse-bad", [], [])),
        )
        out = await roster_mod._finalize_joblist_titles_after_chain(
            {"job_titles": ["Dev"], "response_type": "JOBLIST_TITLES"},
            {"parsed_response": {"job_container": "div", "job_tag": "a"}},
            "acme",
            "https://cw",
            "https://js",
            {1: "<div><a>Dev</a></div>"},
            {},
            1,
            "JOBLIST_TITLES",
            False,
            {},
        )
        assert out["state"] == "CANNOT_PARSE_JOB_SITE"
        saver.assert_called_once()


class TestAst505InflowDiscovery:
    """AST-505: CSE discovery batch, vet ingest, URL dedupe, NEW/WEBSITE_FOUND states."""

    def test_normalize_company_url_strips_www(self) -> None:
        assert roster_mod._normalize_company_url_for_dedupe("https://www.Acme.com/jobs/") == "https://acme.com/jobs"

    def test_ingest_creates_new_without_website(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate(
            "c505",
            state="LIVE_PROMPTS",
            candidate_data={"artifacts": {"company_search_terms": "x"}},
        )
        assert roster_mod.ingest_new_companies("c505", "acme_inflow", None) is True
        row = db.get_company("acme_inflow")
        assert row is not None
        assert row["state"] == "NEW"
        assert row["candidate_id"] == "c505"

    def test_ingest_creates_website_found_with_url(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c505", state="LIVE_PROMPTS", candidate_data={})
        assert roster_mod.ingest_new_companies("c505", "with_site", "https://withsite.example") is True
        row = db.get_company("with_site")
        assert row is not None
        assert row["state"] == "WEBSITE_FOUND"
        assert row["company_website"] == "https://withsite.example"

    def test_ingest_rejects_invalid_slug(self, seeded_db) -> None:
        assert roster_mod.ingest_new_companies("cand-1", "Bad Slug!", None) is False

    def test_ingest_rejects_duplicate_slug(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("dupe_co", state="NEW", candidate_id="cand-1", company_name="dupe_co")
        assert roster_mod.ingest_new_companies("cand-1", "dupe_co", None) is False

    def test_ingest_rejects_duplicate_url(self, seeded_db) -> None:
        db = seeded_db
        db.save_company(
            "existing",
            state="WEBSITE_FOUND",
            candidate_id="cand-1",
            company_website="https://www.existing.com",
            company_name="existing",
        )
        assert roster_mod.ingest_new_companies("cand-1", "newco", "https://existing.com") is False

    def test_ingest_saves_discovery_notes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save_data = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save_data)
        monkeypatch.setattr(roster_mod, "get_company", MagicMock(return_value=None))
        monkeypatch.setattr(roster_mod, "save_company", MagicMock())
        roster_mod.ingest_new_companies(
            "cand-1",
            "hitco",
            "https://hit.co",
            source_hit={"url": "https://src.example"},
        )
        save_data.assert_called_once_with("hitco", {"inflow_discovery_notes": "https://src.example"})

    @pytest.mark.asyncio
    async def test_run_batch_no_stale_terms_returns_zero_errors(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c1", state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms("c1", ["fresh"])
        db.update_company_search_term_last_scan_at("c1", "fresh")
        out = await roster_mod.run_inflow_discovery_batch(
            {"astral_candidate_id": "c1", "candidate_data": {}},
            "batch-1",
            {"inflow_discovery_freq_hrs": 168.0},
            False,
        )
        assert out["total_errors"] == 0

    @pytest.mark.asyncio
    async def test_run_batch_happy_path(self, seeded_db, monkeypatch: pytest.MonkeyPatch) -> None:
        db = seeded_db
        db.save_candidate("c1", state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms("c1", ["fintech"])
        hits = [{"title": "Co", "url": "https://co.example", "snippet": "snip"}]
        monkeypatch.setattr(roster_mod, "search_google_cse", MagicMock(return_value=hits))
        cand = {"astral_candidate_id": "c1", "candidate_data": {}}
        out = await roster_mod.run_inflow_discovery_batch(cand, "batch-505", cand, False)
        assert out["total_passed"] == 1
        assert out["total_failed"] == 0
        assert out["total_errors"] == 0
        row = db.get_company("co_example")
        assert row is not None
        assert row["state"] == "NEW"
        term_row = next(r for r in db.list_company_search_terms("c1") if r["search_term"] == "fintech")
        assert term_row["last_scan_at"] is not None

    @pytest.mark.asyncio
    async def test_run_batch_cse_failure_continues(self, seeded_db, monkeypatch: pytest.MonkeyPatch) -> None:
        db = seeded_db
        db.save_candidate("c1", state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms("c1", ["bad", "good"])

        def _cse(query: str, **kwargs: Any) -> List[Dict[str, str]]:
            if query == "bad":
                raise RuntimeError("quota")
            return [{"title": "Ok", "url": "https://ok.example", "snippet": ""}]

        monkeypatch.setattr(roster_mod, "search_google_cse", _cse)
        cand = {"astral_candidate_id": "c1", "candidate_data": {}}
        out = await roster_mod.run_inflow_discovery_batch(cand, "b", {}, False)
        assert out["total_errors"] == 1
        rows = {r["search_term"]: r["last_scan_at"] for r in db.list_company_search_terms("c1")}
        assert rows["good"] is not None
        assert rows["bad"] is None
        assert db.get_company("ok_example") is not None

    @pytest.mark.asyncio
    async def test_run_batch_searches_only_stale_terms(self, seeded_db, monkeypatch: pytest.MonkeyPatch) -> None:
        db = seeded_db
        db.save_candidate("c1", state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms("c1", ["fresh", "stale"])
        db.update_company_search_term_last_scan_at("c1", "fresh")
        searched: list[str] = []

        def _cse(query: str, **kwargs: Any) -> List[Dict[str, str]]:
            searched.append(query)
            return []

        monkeypatch.setattr(roster_mod, "search_google_cse", _cse)
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"results": []}}),
        )
        cand = {"astral_candidate_id": "c1", "candidate_data": {}}
        await roster_mod.run_inflow_discovery_batch(
            cand, "b", {"inflow_discovery_freq_hrs": 168.0}, False
        )
        assert searched == ["stale"]

    @pytest.mark.asyncio
    async def test_run_batch_freq_hrs_zero_searches_fresh_terms(
        self, seeded_db, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = seeded_db
        db.save_candidate("c814", state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms("c814", ["fresh"])
        db.update_company_search_term_last_scan_at("c814", "fresh")
        searched: list[str] = []

        def _cse(query: str, **kwargs: Any) -> List[Dict[str, str]]:
            searched.append(query)
            return []

        monkeypatch.setattr(roster_mod, "search_google_cse", _cse)
        cand = {"astral_candidate_id": "c814", "candidate_data": {}}
        await roster_mod.run_inflow_discovery_batch(
            cand, "b", {"inflow_discovery_freq_hrs": 0}, False
        )
        assert searched == ["fresh"]

    @pytest.mark.asyncio
    async def test_consult_routes_candidate_entity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import consult as consult_mod

        proc = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr(roster_mod, "run_inflow_discovery_batch", proc)
        cand = {
            "astral_candidate_id": "c505",
            "candidate_data": {"artifacts": {"company_search_terms": "fintech"}},
        }
        out = await consult_mod.run_consult_task("candidate", "LIVE_PROMPTS", [cand], "batch-505", cand, False)
        assert out["total_passed"] == 1
        proc.assert_awaited_once_with(cand, "batch-505", cand, False)


class TestAst775InflowDiscoveryRecordNew:
    """AST-775: discovery batch records NEW rows only — no inline vet_inflow_discovery."""

    def test_slug_from_discovery_url_hostname(self) -> None:
        assert roster_mod._slug_from_discovery_url("https://www.Acme.Corp/jobs") == "acme_corp"

    def test_slug_from_discovery_url_hash_fallback(self) -> None:
        slug = roster_mod._slug_from_discovery_url("")
        assert slug.startswith("inflow_")
        assert len(slug) == len("inflow_") + 12

    def test_discovery_blurb_line_truncates_snippet(self) -> None:
        long_snip = "x" * 600
        line = roster_mod._discovery_blurb_line(
            {"title": "T", "url": "https://u.example", "snippet": long_snip},
            index=3,
        )
        assert line.startswith("003|T|https://u.example|")
        assert len(line.split("|", 3)[-1]) == 500

    def test_record_hit_creates_new_with_blurb_and_notes(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c775", state="LIVE_PROMPTS", candidate_data={})
        hit = {"title": "Hit Co", "url": "https://hit.example", "snippet": "about"}
        ok, outcome = roster_mod.record_inflow_discovery_hit("c775", hit, index=0)
        assert ok is True
        assert "recorded NEW slug=hit_example" in outcome
        row = db.get_company("hit_example")
        assert row is not None
        assert row["state"] == "NEW"
        cdata = row.get("company_data") or {}
        assert cdata.get("inflow_discovery_notes") == "https://hit.example"
        assert cdata.get("inflow_discovery_blurb") == "000|Hit Co|https://hit.example|about"

    def test_record_hit_skips_duplicate_url_via_notes(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c775", state="LIVE_PROMPTS", candidate_data={})
        db.save_company(
            "existing",
            state="NEW",
            candidate_id="c775",
            company_name="existing",
            company_data={"inflow_discovery_notes": "https://dup.example"},
        )
        ok, outcome = roster_mod.record_inflow_discovery_hit(
            "c775",
            {"title": "X", "url": "https://www.dup.example", "snippet": ""},
        )
        assert ok is False
        assert "skipped duplicate url" in outcome

    def test_record_hit_skips_duplicate_url_via_blurb(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c775", state="LIVE_PROMPTS", candidate_data={})
        db.save_company(
            "from_blurb",
            state="NEW",
            candidate_id="c775",
            company_name="from_blurb",
            company_data={
                "inflow_discovery_blurb": "000|T|https://blurb.example|snip",
            },
        )
        ok, _ = roster_mod.record_inflow_discovery_hit(
            "c775",
            {"title": "Y", "url": "https://blurb.example", "snippet": ""},
        )
        assert ok is False

    def test_record_hit_slug_collision_suffix_other_candidate(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c775", state="LIVE_PROMPTS", candidate_data={})
        db.save_candidate("other", state="LIVE_PROMPTS", candidate_data={})
        db.save_company(
            "shared_example",
            state="NEW",
            candidate_id="other",
            company_name="shared_example",
        )
        ok, outcome = roster_mod.record_inflow_discovery_hit(
            "c775",
            {"title": "Z", "url": "https://shared.example", "snippet": ""},
        )
        assert ok is True
        assert "shared_example_2" in outcome
        assert db.get_company("shared_example_2") is not None

    @pytest.mark.asyncio
    async def test_run_batch_no_deduped_hits_is_success(self, seeded_db, monkeypatch: pytest.MonkeyPatch) -> None:
        db = seeded_db
        db.save_candidate("c1", state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms("c1", ["empty"])
        monkeypatch.setattr(roster_mod, "search_google_cse", MagicMock(return_value=[]))
        cand = {"astral_candidate_id": "c1", "candidate_data": {}}
        out = await roster_mod.run_inflow_discovery_batch(cand, "batch-775", cand, False)
        assert out == {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}


class TestAst776VetInflowDiscoveryCompany:
    """AST-776: company vet_inflow_discovery dispatch on NEW + blurb → WEBSITE_FOUND | VET_FAILED."""

    @pytest.mark.asyncio
    async def test_vet_missing_blurb_is_error(self) -> None:
        entity = _company(
            state="NEW",
            company_website="",
            company_data={},
        )
        out = await roster_mod.vet_inflow_discovery_company("co_new", entity, "batch-776", {}, False)
        assert out["success"] is False
        assert out["error"] == "missing inflow_discovery_blurb"

    @pytest.mark.asyncio
    async def test_vet_ignore_transitions_vet_failed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"results": [{"action": "ignore", "hit_index": 0}]},
                }
            ),
        )
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        entity = _company(
            state="NEW",
            company_website="",
            company_data={"inflow_discovery_blurb": "000|Co|https://co.example|snip"},
        )
        out = await roster_mod.vet_inflow_discovery_company("co_new", entity, "batch-776", {}, False)
        assert out == {"success": True, "state": "VET_FAILED", "error": None}
        transition.assert_called_once_with("co_new", "VET_FAILED")

    @pytest.mark.asyncio
    async def test_vet_slug_sets_website_and_website_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "results": [
                            {
                                "action": "slug",
                                "website": "https://home.example",
                                "hit_index": 0,
                            },
                        ],
                    },
                }
            ),
        )
        transition = MagicMock()
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "update_company", update)
        entity = _company(
            state="NEW",
            company_website="",
            company_data={"inflow_discovery_blurb": "000|Co|https://co.example|snip"},
        )
        out = await roster_mod.vet_inflow_discovery_company("co_new", entity, "batch-776", {}, False)
        assert out == {"success": True, "state": "WEBSITE_FOUND", "error": None}
        update.assert_called_once_with("co_new", company_website="https://home.example")
        transition.assert_called_once_with("co_new", "WEBSITE_FOUND")

    @pytest.mark.asyncio
    async def test_run_company_task_routes_vet_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        vet = AsyncMock(return_value={"success": True, "state": "WEBSITE_FOUND", "error": None})
        resolve = AsyncMock()
        monkeypatch.setattr(roster_mod, "vet_inflow_discovery_company", vet)
        monkeypatch.setattr(roster_mod, "resolve_company_website", resolve)
        entity = _company(
            state="NEW",
            company_website="",
            company_data={"inflow_discovery_blurb": "000|Co|https://co.example|snip"},
        )
        out = await roster_mod.run_company_task(
            "NEW",
            entity,
            "batch-776",
            {},
            False,
            dispatch_task_key="vet_inflow_discovery",
        )
        assert out["total_passed"] == 1
        vet.assert_awaited_once()
        resolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_company_task_routes_resolve_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        vet = AsyncMock()
        resolve = AsyncMock(return_value={"success": True, "state": "NO_WEBSITE", "error": None})
        monkeypatch.setattr(roster_mod, "vet_inflow_discovery_company", vet)
        monkeypatch.setattr(roster_mod, "resolve_company_website", resolve)
        entity = _company(state="NEW", company_website="")
        out = await roster_mod.run_company_task(
            "NEW",
            entity,
            "batch-776",
            {},
            False,
            dispatch_task_key="inflow_resolve_website",
        )
        assert out["total_passed"] == 1
        resolve.assert_awaited_once()
        vet.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_company_task_new_without_key_errors(self) -> None:
        entity = _company(state="NEW", company_website="")
        out = await roster_mod.run_company_task("NEW", entity, "batch-776", {}, False)
        assert out["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_consult_routes_company_vet_via_run_company_task(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.core import consult as consult_mod

        company_task = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr(roster_mod, "run_company_task", company_task)
        entity = {
            "short_name": "co_new",
            "candidate_id": "c776",
            "company_state": "NEW",
            "company_data": {"inflow_discovery_blurb": "000|Co|https://co.example|snip"},
        }
        ctx = {"astral_candidate_id": "c776"}
        out = await consult_mod.run_consult_task(
            "company",
            "NEW",
            [entity],
            "batch-776",
            ctx,
            False,
            dispatch_task_key="vet_inflow_discovery",
        )
        assert out["total_passed"] == 1
        company_task.assert_awaited_once()
        assert company_task.await_args.kwargs["dispatch_task_key"] == "vet_inflow_discovery"


class TestAst506InflowResolve:
    """AST-506: Phase 2 CSE resolution + find_company_website → WEBSITE_FOUND | NO_WEBSITE."""

    @pytest.mark.asyncio
    async def test_resolve_skips_when_website_present(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cse = MagicMock()
        monkeypatch.setattr(roster_mod, "search_google_cse", cse)
        entity = _company(state="NEW", company_website="https://already.example")
        out = await roster_mod.resolve_company_website("acme", entity, {}, False)
        assert out == {"success": True, "state": "WEBSITE_FOUND", "error": None}
        cse.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolve_empty_hits_no_website(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "search_google_cse", MagicMock(return_value=[]))
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        entity = _company(state="NEW", company_website="")
        out = await roster_mod.resolve_company_website("acme", entity, {}, False)
        assert out["state"] == "NO_WEBSITE"
        transition.assert_called_once_with("acme", "NO_WEBSITE")

    @pytest.mark.asyncio
    async def test_resolve_success_website_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        hits = [{"title": "Acme", "url": "https://acme.example", "snippet": "official"}]
        monkeypatch.setattr(roster_mod, "search_google_cse", MagicMock(return_value=hits))
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"task_success": True, "website": "https://acme.example"},
                }
            ),
        )
        transition = MagicMock()
        update = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        monkeypatch.setattr(roster_mod, "update_company", update)
        entity = _company(state="NEW", company_website="")
        entity["company_name"] = "Acme Corp"
        out = await roster_mod.resolve_company_website("acme", entity, {}, False)
        assert out["state"] == "WEBSITE_FOUND"
        update.assert_called_once_with("acme", company_website="https://acme.example")
        transition.assert_called_once_with("acme", "WEBSITE_FOUND")

    @pytest.mark.asyncio
    async def test_resolve_ai_decline_no_website(self, monkeypatch: pytest.MonkeyPatch) -> None:
        hits = [{"title": "Acme", "url": "https://acme.example", "snippet": ""}]
        monkeypatch.setattr(roster_mod, "search_google_cse", MagicMock(return_value=hits))
        monkeypatch.setattr(
            roster_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"task_success": False}}),
        )
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        entity = _company(state="NEW", company_website="")
        out = await roster_mod.resolve_company_website("acme", entity, {}, False)
        assert out["state"] == "NO_WEBSITE"
        transition.assert_called_once_with("acme", "NO_WEBSITE")

    @pytest.mark.asyncio
    async def test_resolve_cse_failure_returns_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(roster_mod, "search_google_cse", MagicMock(side_effect=RuntimeError("quota")))
        transition = MagicMock()
        monkeypatch.setattr(roster_mod, "transition_company_state", transition)
        entity = _company(state="NEW", company_website="")
        out = await roster_mod.resolve_company_website("acme", entity, {}, False)
        assert out["success"] is False
        assert out["error"] == "quota"
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_company_task_new_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            roster_mod,
            "resolve_company_website",
            AsyncMock(side_effect=[
                {"success": True, "state": "WEBSITE_FOUND", "error": None},
                {"success": True, "state": "NO_WEBSITE", "error": None},
                {"success": False, "state": None, "error": "boom"},
            ]),
        )
        entity = _company(state="NEW", company_website="")
        ok = await roster_mod.run_company_task("NEW", entity, "batch-506")
        no_site = await roster_mod.run_company_task("NEW", entity, "batch-506")
        err = await roster_mod.run_company_task("NEW", entity, "batch-506")
        assert ok["total_passed"] == 1
        assert no_site["total_passed"] == 1
        assert err["total_errors"] == 1


class TestAst689ScrapeReadiness:
    """AST-689: careers-list scrape readiness gate before select_job_page extract."""

    @pytest.mark.asyncio
    async def test_wait_for_careers_list_readiness_ready_on_listing_hits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.external import playwright as pw_mod
        from src.external.playwright import wait_for_careers_list_readiness

        poll_n = {"n": 0}

        async def count_side_effect() -> int:
            poll_n["n"] += 1
            return 0 if poll_n["n"] == 1 else 2

        locator = MagicMock()
        locator.count = AsyncMock(side_effect=count_side_effect)
        page = MagicMock()
        page.locator = MagicMock(return_value=locator)
        page.wait_for_timeout = AsyncMock()
        monkeypatch.setattr(
            pw_mod,
            "extract_visible_text",
            AsyncMock(side_effect=[{"text": "x" * 100}, {"text": "x" * 200}]),
        )

        result = await wait_for_careers_list_readiness(
            page,
            {
                "max_wait_ms": 5000,
                "poll_interval_ms": 10,
                "min_listing_hits": 1,
                "listing_selectors": ["a[href*='/job']"],
                "run_load_all_jobs": False,
            },
        )
        assert result["ready"] is True
        assert result["outcome"] == "ready"
        assert result["listing_hits"] >= 1

    @pytest.mark.asyncio
    async def test_wait_for_careers_list_readiness_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.external import playwright as pw_mod
        from src.external.playwright import wait_for_careers_list_readiness

        locator = MagicMock()
        locator.count = AsyncMock(return_value=0)
        page = MagicMock()
        page.locator = MagicMock(return_value=locator)
        page.wait_for_timeout = AsyncMock()
        monkeypatch.setattr(pw_mod, "extract_visible_text", AsyncMock(return_value={"text": "short"}))

        result = await wait_for_careers_list_readiness(
            page,
            {
                "max_wait_ms": 100,
                "poll_interval_ms": 50,
                "stability_polls": 2,
                "min_visible_chars": 400,
                "min_listing_hits": 1,
                "listing_selectors": ["a"],
                "run_load_all_jobs": False,
            },
        )
        assert result["ready"] is False
        assert result["outcome"] == "timeout"

    @pytest.mark.asyncio
    async def test_fetch_job_links_content_calls_readiness(self, monkeypatch: pytest.MonkeyPatch) -> None:
        call_order: List[str] = []
        readiness = AsyncMock(
            return_value={
                "ready": True,
                "outcome": "ready",
                "visible_chars": 500,
                "listing_hits": 3,
                "wait_ms": 100,
                "load_all_jobs_ran": False,
            }
        )

        async def readiness_track(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            call_order.append("readiness")
            return await readiness(*args, **kwargs)

        extract = AsyncMock(return_value={"text": "Role A"})

        async def extract_track(*args: Any, **kwargs: Any) -> Dict[str, str]:
            call_order.append("extract")
            return await extract(*args, **kwargs)

        monkeypatch.setattr(roster_mod, "wait_for_careers_list_readiness", readiness_track)
        monkeypatch.setattr(roster_mod, "parse_enumerate_array", MagicMock(return_value={1: "https://acme.com/jobs"}))
        page = AsyncMock()
        monkeypatch.setattr(roster_mod, "get_page", AsyncMock(return_value=page))
        monkeypatch.setattr(roster_mod, "close_page", AsyncMock())
        monkeypatch.setattr(roster_mod, "extract_visible_text", extract_track)
        monkeypatch.setattr(roster_mod, "extract_page_dom", AsyncMock(return_value="<div/>"))
        monkeypatch.setattr(roster_mod, "extract_site_page_list", AsyncMock(return_value=[]))

        await roster_mod._fetch_job_links_content([1], "1. https://acme.com/jobs", AsyncMock(), debug=True)

        readiness.assert_awaited_once()
        extract.assert_awaited_once()
        assert call_order == ["readiness", "extract"]


class TestAst692JobsiteScrapeIssue:
    """AST-692: JOBSITE_SCRAPE_ISSUE terminal roster flow — no parse_job_list chain."""

    @pytest.mark.asyncio
    async def test_check_parse_results_jobsite_scrape_issue(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        strip = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)
        monkeypatch.setattr(roster_mod, "_strip_company_data_keys", strip)
        result = {
            "response_type": "JOBSITE_SCRAPE_ISSUE",
            "selected_page": 1,
            "scrape_issue_summary": "Listing region empty",
            "scrape_issue_evidence": "Filters visible, zero titles",
        }
        out = await roster_mod._check_parse_results(
            result,
            "JOBSITE_SCRAPE_ISSUE",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {},
            debug=True,
        )
        assert out["state"] == "JOBSITE_SCRAPE_ISSUE"
        assert out["job_site"] == "https://acme.com/jobs"
        assert out["response_type"] == "JOBSITE_SCRAPE_ISSUE"
        strip.assert_called_once_with("acme", ("job_list_visible",))
        save.assert_called_once()
        kwargs = save.call_args.kwargs
        assert kwargs["state"] == "JOBSITE_SCRAPE_ISSUE"
        assert kwargs["page_option_url"] == "https://acme.com/jobs"
        assert kwargs["jobsite_scrape_issue_summary"] == "Listing region empty"
        assert kwargs["raw_response"]["scrape_issue_summary"] == "Listing region empty"

    @pytest.mark.asyncio
    async def test_find_job_page_from_assembled_jobsite_scrape_issue_no_chain(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        do_task = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {
                    "response_type": "JOBSITE_SCRAPE_ISSUE",
                    "selected_page": 1,
                    "scrape_issue_summary": "shell only",
                },
            }
        )
        check = AsyncMock(
            return_value={
                "short_name": "acme",
                "state": "JOBSITE_SCRAPE_ISSUE",
                "job_site": "https://acme.com/jobs",
                "response_type": "JOBSITE_SCRAPE_ISSUE",
            }
        )
        fin_chain = AsyncMock()
        monkeypatch.setattr(roster_mod, "do_task", do_task)
        monkeypatch.setattr(roster_mod, "_check_parse_results", check)
        monkeypatch.setattr(roster_mod, "_finalize_joblist_titles_after_chain", fin_chain)

        out = await roster_mod._find_job_page_from_assembled(
            short_name="acme",
            company_website="https://acme.com",
            assembled_content="=== PAGE 1 ===",
            page_url_map={1: "https://acme.com/jobs"},
            page_dom_map={1: "<div/>"},
            visible_map={1: "filters only"},
            nav_links="1. https://acme.com/jobs",
            browser_context=MagicMock(),
            debug=False,
            ctx=None,
            chain_parse=True,
        )

        do_task.assert_awaited_once()
        assert do_task.await_args.args[0] == "select_job_page"
        check.assert_awaited_once()
        fin_chain.assert_not_awaited()
        assert out["state"] == "JOBSITE_SCRAPE_ISSUE"
        assert out["response_type"] == "JOBSITE_SCRAPE_ISSUE"

    @pytest.mark.asyncio
    async def test_unknown_response_type_still_no_joblist(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "_save_company", save)
        out = await roster_mod._check_parse_results(
            {"response_type": "OTHER"},
            "OTHER",
            "acme",
            "https://acme.com",
            "https://acme.com/jobs",
            {},
        )
        assert out["state"] == "NO_JOBLIST"
        assert out["response_type"] == "OTHER"


class TestAst726LatestOnlyRosterStory:
    """AST-726: modal story dedup + latest-only company prefilter outcomes."""

    def test_dedupe_agent_responses_latest_wins_per_task_key(self) -> None:
        entries = [
            {"task_key": "consult_get", "created_at": "2026-06-01 00:00:00", "batch_id": "old"},
            {"task_key": "consult_do", "created_at": "2026-06-01 00:00:00", "batch_id": "do"},
            {"task_key": "consult_get", "created_at": "2026-06-02 00:00:00", "batch_id": "new"},
        ]
        deduped = roster_mod.dedupe_agent_responses_latest(entries)
        assert len(deduped) == 2
        assert deduped[0]["task_key"] == "consult_get"
        assert deduped[0]["batch_id"] == "new"
        assert deduped[1]["task_key"] == "consult_do"

    def test_company_prefilter_vector_grades_from_company_data(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            roster_mod,
            "get_agent_data_for_ids",
            MagicMock(return_value={"block-726": {"block_data": "{}"}}),
        )
        entity = {
            "short_name": "acme",
            "agent_responses": [
                {
                    "task_key": "prefilter_company",
                    "prompt_blocks": [{"type": "RESPONSE", "id": "block-726"}],
                }
            ],
            "company_data": {"prefilter_grades": [{"grade": "A", "vector": "fit"}]},
        }
        story = roster_mod.get_entity_agent_story(entity)
        assert story[0]["vector_grades"] == [{"grade": "A", "vector": "fit"}]

    def test_prefilter_fail_clears_score(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(roster_mod, "save_company_data", save)
        monkeypatch.setattr(roster_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(roster_mod, "_company_on_decomposed_pjl_path", lambda *a, **k: False)
        flat = {
            "grades": _prefilter_grades({"grade": "F", "vector": "fit", "confidence": 2, "reason": "nope"}),
            "possible_job_links": [],
        }
        cfg = {**ROSTER_CONFIG["prefilter"]}
        roster_mod._apply_prefilter_decoded_company_outcome(
            "acme", flat, cfg, _prefilter_rubric_ctx()
        )
        saved = save.call_args[0][1]
        assert saved["prefilter_score"] is None



class TestAst727NormalizeAgentResponsesForBackfill:
    """AST-727: shared backfill normalizer matches runtime dedupe rules."""

    def test_drops_empty_task_key_and_dedupes(self) -> None:
        entries = [
            {"task_key": "", "batch_id": "orphan"},
            {"task_key": "consult_get", "created_at": "2026-06-01 00:00:00", "batch_id": "old"},
            {"task_key": "consult_get", "created_at": "2026-06-02 00:00:00", "batch_id": "new"},
            "bad",
        ]
        normalized, stats = roster_mod.normalize_agent_responses_for_backfill(entries)
        assert stats == {"dropped_empty_key": 1, "deduped_removed": 1}
        assert len(normalized) == 1
        assert normalized[0]["batch_id"] == "new"

    def test_coerces_non_list_to_empty(self) -> None:
        normalized, stats = roster_mod.normalize_agent_responses_for_backfill({})
        assert normalized == []
        assert stats == {"dropped_empty_key": 0, "deduped_removed": 0}

    def test_idempotent_on_already_normalized(self) -> None:
        entries = [
            {"task_key": "consult_do", "created_at": "2026-06-01 00:00:00", "batch_id": "b1"},
        ]
        normalized, stats = roster_mod.normalize_agent_responses_for_backfill(entries)
        assert normalized == entries
        assert stats == {"dropped_empty_key": 0, "deduped_removed": 0}
