"""Component tests for src/core/gazer.py (AST-393)."""

from __future__ import annotations

import asyncio
import logging
import re
from contextlib import asynccontextmanager
from types import SimpleNamespace
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

class TestAst1195BotBlockedErrorState:
    """AST-1195 · AST-2086: JD classification is task-aware — bot / cookie name the calling task."""

    def test_bot_maps_to_task_bot_blocked(self) -> None:
        fj = gazer_mod.GAZER_CONFIG["fetch_jd"]["classified_states"]
        fr = gazer_mod.GAZER_CONFIG["fetch_relative_jd"]["classified_states"]
        assert fj == {
            "cookie": "ERROR_FETCH_JD_COOKIE", "bot": "BOT_BLOCKED_FETCH_JD",
            "missing": "JD_SCRAPE_FAIL_MISSING", "closed": "JD_SCRAPE_FAIL_CLOSED",
        }
        assert fr == {
            "cookie": "ERROR_FETCH_RELATIVE_JD_COOKIE", "bot": "BOT_BLOCKED_FETCH_RELATIVE_JD",
            "missing": "JD_SCRAPE_FAIL_MISSING", "closed": "JD_SCRAPE_FAIL_CLOSED",
        }
        # The module-level universal map is gone; callers pass their own task's map.
        assert not hasattr(gazer_mod, "_JD_ERROR_STATES")


class TestAst2004IsBotWall:
    """AST-2004: shared is_bot_wall — one detector for _classify_jd and roster select."""

    _WALL = "Acme | LinkedIn. New to LinkedIn? Join now. Sign in with Email."

    def test_threshold_hit_and_miss(self) -> None:
        assert gazer_mod.is_bot_wall(self._WALL) is True
        # One signal only is below bot_threshold (2).
        assert gazer_mod.is_bot_wall("Sign in with Email to continue") is False
        assert gazer_mod.is_bot_wall(None) is False  # type: ignore[arg-type]

    def test_classify_jd_delegates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert gazer_mod._classify_jd(self._WALL) == "bot"
        # Forcing the helper proves _classify_jd routes through it (no second copy of the loop).
        monkeypatch.setattr(gazer_mod, "is_bot_wall", lambda _t: False)
        assert gazer_mod._classify_jd(self._WALL) != "bot"


class TestAst1197ChallengeBotSignals:
    """AST-1197: parent-captured Cloudflare interstitial classifies as bot (≥2 signals)."""

    def test_captured_challenge_body_is_bot(self) -> None:
        body = (
            "Additional Verification Required\n"
            "Your Ray ID for this request is a26948de4d78f005\n"
            "Troubleshooting Cloudflare Errors"
        )
        assert gazer_mod._classify_jd(body) == "bot"


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
        assert gazer_mod._compiled_title_patterns({"candidate_data": {"contact": "bad"}}) == []

    def test_skips_invalid_regex_lines(self) -> None:
        ctx = {"candidate_data": {"contact": {"title_patterns": "[unclosed"}}}
        assert gazer_mod._compiled_title_patterns(ctx) == []

    def test_reads_title_patterns_alias(self) -> None:
        ctx = {"candidate_data": {"contact": {"TITLE_PATTERNS": "engineer"}}}
        assert len(gazer_mod._compiled_title_patterns(ctx)) == 1

    def test_coerces_falsy_pattern_source(self) -> None:
        ctx = {"candidate_data": {"contact": {"title_patterns": 0}}}
        assert gazer_mod._compiled_title_patterns(ctx) == []

    def test_coerces_truthy_non_string_pattern_source(self) -> None:
        ctx = {"candidate_data": {"contact": {"title_patterns": ("engineer",)}}}
        assert len(gazer_mod._compiled_title_patterns(ctx)) == 1

    def test_skips_blank_pattern_lines(self) -> None:
        ctx = {"candidate_data": {"contact": {"title_patterns": "\nengineer\n"}}}
        assert len(gazer_mod._compiled_title_patterns(ctx)) == 1

    def test_compiles_valid_patterns(self) -> None:
        ctx = {"candidate_data": {"contact": {"title_patterns": "engineer\n"}}}
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
        ctx = {"candidate_data": {"contact": {"title_patterns": "engineer"}}}
        jobs = [{"astral_job_id": "job-2", "job_data": {"raw_job_listing": "janitor"}}]
        out = await gazer_mod.validate_title_batch("batch-1", jobs, ctx, debug=True)
        assert out["failed"] == 1
        transition.assert_called_once_with(["job-2"], "INVALID_TITLE")

    @pytest.mark.asyncio
    async def test_rejects_without_debug_logging(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        ctx = {"candidate_data": {"contact": {"title_patterns": "engineer"}}}
        jobs = [{"astral_job_id": "job-8", "job_data": {"raw_job_listing": "janitor"}}]
        out = await gazer_mod.validate_title_batch("batch-1", jobs, ctx, debug=False)
        assert out["failed"] == 1

    @pytest.mark.asyncio
    async def test_skips_meteorite_source_roster_still_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1153 P2 / AST-1704: meteorite source SoT skipped; roster peer still INVALID_TITLE.
        # Real company_id on meteorite-track job must not re-enable title-pattern screen.
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        ctx = {"candidate_data": {"contact": {"title_patterns": "^Engineer"}}}
        jobs = [
            {
                "astral_job_id": "job-m",
                "source": "meteorite",
                "company_id": "acme",
                "company": "acme",
                "job_data": {"raw_job_listing": "Janitor Wanted"},
            },
            {
                "astral_job_id": "job-r",
                "source": "company",
                "company": "acme",
                "job_data": {"raw_job_listing": "Janitor Wanted"},
            },
        ]
        out = await gazer_mod.validate_title_batch("batch-1704-p2", jobs, ctx, debug=False)
        assert out["passed"] == 0
        assert out["failed"] == 1
        assert out["total"] == 2
        transition.assert_called_once_with(["job-r"], "INVALID_TITLE")


def _mock_batch_browser_session(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    session = MagicMock()

    @asynccontextmanager
    async def _batch():
        yield session

    monkeypatch.setattr(gazer_mod, "create_batch_browser_session", _batch)
    return session


# fetch_job_pages_batch still opens create_browser_context (not the AST-853 batch session).
def _mock_browser_context(monkeypatch: pytest.MonkeyPatch) -> None:
    @asynccontextmanager
    async def _browser():
        yield MagicMock()

    monkeypatch.setattr(gazer_mod, "create_browser_context", _browser)


class TestFetchWebsiteBatch:
    @pytest.mark.asyncio
    async def test_aborts_without_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.fetch_website_batch("batch-1", [])

    @pytest.mark.asyncio
    async def test_missing_website_and_scrape_errors_fail(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        batch_session = _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        save = MagicMock()
        scrape = AsyncMock(
            return_value={"company_website": "https://acme.com", "visible_text": "", "error": "bad scrape"},
        )
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(gazer_mod, "scrape_company_homepage_content", scrape)
        companies = [
            {"short_name": "co-empty", "company_website": ""},
            {"short_name": "co-bad", "company_website": "https://acme.com"},
        ]
        out = await gazer_mod.fetch_website_batch("batch-1", companies)
        scrape.assert_awaited_once_with(
            "co-bad", "https://acme.com", batch_session=batch_session,
        )
        assert out == {"passed": 0, "failed": 2, "errors": 0, "skipped": 0, "total": 2}
        assert transition.call_count == 2
        assert save.call_count == 2
        transition.assert_any_call("co-bad", "ERROR_FETCH_WEBSITE_UNREADABLE")

    @pytest.mark.asyncio
    async def test_success_persists_homepage_and_nav_links(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(
            gazer_mod,
            "scrape_company_homepage_content",
            AsyncMock(
                return_value={
                    "company_website": "https://canonical.example",
                    "visible_text": "homepage body",
                    "enumerated_nav_links": "1. /about\n2. /jobs",
                    "error": None,
                }
            ),
        )
        companies = [{"short_name": "acme", "company_website": "https://old.example"}]
        out = await gazer_mod.fetch_website_batch("batch-1", companies, debug=True)
        assert out == {"passed": 1, "failed": 0, "errors": 0, "skipped": 0, "total": 1}
        transition.assert_called_once_with("acme", "HOMEPAGE_READY")
        save.assert_called_once_with(
            "acme",
            {"homepage_text": "homepage body", "nav_links": "1. /about\n2. /jobs"},
        )

    @pytest.mark.asyncio
    async def test_persists_normalized_visible_text_from_scrape_helper(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", MagicMock())
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(
            gazer_mod,
            "scrape_company_homepage_content",
            AsyncMock(
                return_value={
                    "company_website": "https://acme.com",
                    "visible_text": "intro\n\nbody",
                    "enumerated_nav_links": "1. /about",
                    "error": None,
                }
            ),
        )
        companies = [{"short_name": "acme", "company_website": "https://acme.com"}]
        out = await gazer_mod.fetch_website_batch("batch-1", companies)
        assert out == {"passed": 1, "failed": 0, "errors": 0, "skipped": 0, "total": 1}
        save.assert_called_once_with(
            "acme",
            {"homepage_text": "intro\n\nbody", "nav_links": "1. /about"},
        )

    @pytest.mark.asyncio
    async def test_scrape_timeout_fails_with_labeled_infra_error(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)

        async def _slow_scrape(*_args: Any, **_kwargs: Any) -> Dict[str, Any]:
            await asyncio.sleep(5)
            return {"company_website": "https://acme.com", "visible_text": "x", "error": None}

        monkeypatch.setattr(gazer_mod, "scrape_company_homepage_content", _slow_scrape)
        monkeypatch.setitem(gazer_mod.PLAYWRIGHT_CONFIG, "company_scrape_timeout_seconds", 0.05)
        companies = [{"short_name": "acme", "company_website": "https://acme.com"}]
        out = await gazer_mod.fetch_website_batch("batch-1", companies)
        assert out == {"passed": 0, "failed": 1, "errors": 0, "skipped": 0, "total": 1}
        transition.assert_called_once_with("acme", "WEBSITE_FOUND_RETRY")
        err = save.call_args[0][1][gazer_mod.ROSTER_CONFIG["company_data_keys"]["prefilter_company_notes"]]
        assert err.startswith("[playwright:scrape_timeout]")


class TestFetchWebsiteFailRouting:
    def test_infra_prefix_detection(self) -> None:
        assert gazer_mod._is_fetch_website_infra_error("[playwright:context_closed] dead")
        assert not gazer_mod._is_fetch_website_infra_error("bad scrape")

    def test_fail_destination_routes_infra_retry_then_terminal(self) -> None:
        cfg = gazer_mod.GAZER_CONFIG["fetch_website"]
        infra = "[playwright:channel_error] boom"
        assert gazer_mod._fetch_website_fail_destination("WEBSITE_FOUND", infra, cfg) == "WEBSITE_FOUND_RETRY"
        assert gazer_mod._fetch_website_fail_destination("WEBSITE_FOUND_RETRY", infra, cfg) == "ERROR_FETCH_WEBSITE_UNREADABLE"
        assert gazer_mod._fetch_website_fail_destination("WEBSITE_FOUND", "site unreadable", cfg) == "ERROR_FETCH_WEBSITE_UNREADABLE"

    @pytest.mark.asyncio
    async def test_infra_scrape_error_retries_from_website_found(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(
            gazer_mod,
            "scrape_company_homepage_content",
            AsyncMock(
                return_value={
                    "company_website": "https://acme.com",
                    "visible_text": "",
                    "error": "[playwright:context_closed] browser dead",
                }
            ),
        )
        companies = [{"short_name": "acme", "company_website": "https://acme.com", "state": "WEBSITE_FOUND"}]
        out = await gazer_mod.fetch_website_batch("batch-1", companies)
        assert out == {"passed": 0, "failed": 1, "errors": 0, "skipped": 0, "total": 1}
        transition.assert_called_once_with("acme", "WEBSITE_FOUND_RETRY")

    @pytest.mark.asyncio
    async def test_infra_scrape_error_terminal_on_retry_state(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(
            gazer_mod,
            "scrape_company_homepage_content",
            AsyncMock(
                return_value={
                    "company_website": "https://acme.com",
                    "visible_text": "",
                    "error": "[playwright:context_closed] browser dead",
                }
            ),
        )
        companies = [
            {"short_name": "acme", "company_website": "https://acme.com", "state": "WEBSITE_FOUND_RETRY"},
        ]
        out = await gazer_mod.fetch_website_batch("batch-1", companies)
        assert out == {"passed": 0, "failed": 1, "errors": 0, "skipped": 0, "total": 1}
        transition.assert_called_once_with("acme", "ERROR_FETCH_WEBSITE_UNREADABLE")

    @pytest.mark.asyncio
    async def test_unhandled_gather_exception_increments_errors_and_continues(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)

        async def _scrape(short_name: str, *_args: Any, **_kwargs: Any) -> Dict[str, Any]:
            if short_name == "co-boom":
                raise RuntimeError("unexpected scrape failure")
            return {
                "company_website": "https://example.com",
                "visible_text": "ok",
                "enumerated_nav_links": "",
                "error": None,
            }

        monkeypatch.setattr(gazer_mod, "scrape_company_homepage_content", _scrape)
        companies = [
            {"short_name": "co-ok", "company_website": "https://a.com"},
            {"short_name": "co-boom", "company_website": "https://b.com"},
            {"short_name": "co-also-ok", "company_website": "https://c.com"},
        ]
        out = await gazer_mod.fetch_website_batch("batch-1", companies)
        assert out == {"passed": 2, "failed": 0, "errors": 1, "skipped": 0, "total": 3}
        assert transition.call_count == 2


class TestAst882HomepageReadyWfrSkip:
    """AST-882 / AST-1810: every WEBSITE_FOUND_RETRY row is scraped (AST-892 second-strike skip removed).
    The return dict keeps its "skipped" key, always 0."""

    @pytest.mark.asyncio
    async def test_scrapes_wfr_even_when_homepage_text_present(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # [AST-1810] Pre-fix this row was skipped (skipped=1, total=0, no scrape).
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        save = MagicMock()
        scrape = AsyncMock(
            return_value={
                "company_website": "https://acme.com",
                "visible_text": "fresh homepage body",
                "nav_links": [],
                "error": None,
            }
        )
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(gazer_mod, "scrape_company_homepage_content", scrape)
        companies = [
            {
                "short_name": "acme",
                "company_website": "https://acme.com",
                "state": "WEBSITE_FOUND_RETRY",
                "company_data": {"homepage_text": "already scraped body"},
            },
        ]
        out = await gazer_mod.fetch_website_batch("batch-1", companies, debug=True)
        assert out == {"passed": 1, "failed": 0, "errors": 0, "skipped": 0, "total": 1}
        scrape.assert_awaited_once()
        transition.assert_called_once_with("acme", "HOMEPAGE_READY")
        # Re-fetch replaces homepage_text via the merge save (prefilter-owned keys untouched).
        assert save.call_args.args[1]["homepage_text"] == "fresh homepage body"

    @pytest.mark.asyncio
    async def test_infra_retry_without_homepage_text_still_routes(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(
            gazer_mod,
            "scrape_company_homepage_content",
            AsyncMock(
                return_value={
                    "company_website": "https://acme.com",
                    "visible_text": "",
                    "error": "[playwright:context_closed] browser dead",
                }
            ),
        )
        companies = [
            {
                "short_name": "acme",
                "company_website": "https://acme.com",
                "state": "WEBSITE_FOUND_RETRY",
                "company_data": {},
            },
        ]
        out = await gazer_mod.fetch_website_batch("batch-1", companies)
        assert out == {"passed": 0, "failed": 1, "errors": 0, "skipped": 0, "total": 1}
        transition.assert_called_once_with("acme", "ERROR_FETCH_WEBSITE_UNREADABLE")

    @pytest.mark.asyncio
    async def test_mixed_second_strike_and_fresh_both_scrape(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """AST-1810: a second-strike row and a fresh row are both work; nothing is skipped."""
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", MagicMock())
        monkeypatch.setattr(
            gazer_mod,
            "scrape_company_homepage_content",
            AsyncMock(
                return_value={
                    "company_website": "https://need.example",
                    "visible_text": "fresh homepage body",
                    "nav_links": [],
                    "error": None,
                }
            ),
        )
        companies = [
            {
                "short_name": "already",
                "company_website": "https://already.example",
                "state": "WEBSITE_FOUND_RETRY",
                "company_data": {"homepage_text": "owned by prefilter"},
            },
            {
                "short_name": "need",
                "company_website": "https://need.example",
                "state": "WEBSITE_FOUND",
                "company_data": {},
            },
        ]
        out = await gazer_mod.fetch_website_batch("batch-1", companies, debug=True)
        assert out == {"passed": 2, "failed": 0, "errors": 0, "skipped": 0, "total": 2}
        assert {c.args for c in transition.call_args_list} == {("already", "HOMEPAGE_READY"), ("need", "HOMEPAGE_READY")}


class TestFetchJobPagesBatch:
    @pytest.mark.asyncio
    async def test_aborts_without_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.fetch_job_pages_batch("batch-1", [])

    @pytest.mark.asyncio
    @pytest.mark.parametrize("debug", [False, True])
    async def test_missing_possible_joblist_links_fails(
        self, monkeypatch: pytest.MonkeyPatch, debug: bool,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_browser_context(monkeypatch)
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", MagicMock())
        companies = [{"short_name": "co-empty", "company_data": {}}]
        out = await gazer_mod.fetch_job_pages_batch("batch-1", companies, debug=debug)
        assert out == {"passed": 0, "failed": 1, "total": 1}
        transition.assert_called_once_with("co-empty", "ERROR_FETCH_JOB_PAGES_UNREADABLE")

    @pytest.mark.asyncio
    async def test_success_transitions_pjl_ready_and_persists(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_browser_context(monkeypatch)
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(
            gazer_mod,
            "_scrape_pjl_page",
            AsyncMock(
                return_value={
                    "url": "https://acme.com/careers",
                    "visible_text": "open roles",
                    "page_links": ["https://acme.com/about"],
                    "enumerated_nav_links": "1: https://acme.com/about",
                }
            ),
        )
        companies = [
            {
                "short_name": "acme",
                "company_data": {"possible_joblist_links": ["acme.com/careers"]},
            }
        ]
        out = await gazer_mod.fetch_job_pages_batch("batch-1", companies, debug=True)
        assert out == {"passed": 1, "failed": 0, "total": 1}
        transition.assert_called_once_with("acme", "PJL_READY")
        saved = save.call_args[0][1]
        assert saved["pjl_scrape_pages"] == [
            {
                "url": "https://acme.com/careers",
                "visible_text": "open roles",
                "enumerated_nav_links": "1: https://acme.com/about",
            }
        ]
        assert "=== PAGE 1: https://acme.com/careers ===" in saved["pjl_assembled_content"]
        assert "--- NAV LINKS ---" in saved["pjl_assembled_content"]
        assert "open roles" in saved["pjl_assembled_content"]

    # AST-1995 refresh: every candidate URL is re-scraped; rows upsert by normalize_link.
    @staticmethod
    async def _run_pjl(
        monkeypatch: pytest.MonkeyPatch,
        company_data: Dict[str, Any],
        records: Dict[str, Dict[str, Any]],
        debug: bool = False,
    ):
        """Run one company through fetch_job_pages_batch; `records` maps candidate URL -> scrape record."""
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_browser_context(monkeypatch)
        transition, save, log = MagicMock(), MagicMock(), MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(gazer_mod, "_log", log)
        scrape = AsyncMock(side_effect=lambda url, _ctx, debug=False: records[url])
        monkeypatch.setattr(gazer_mod, "_scrape_pjl_page", scrape)
        companies = [{"short_name": "acme", "company_data": company_data}]
        out = await gazer_mod.fetch_job_pages_batch("batch-1", companies, debug=debug)
        # First save is the PJL persist; the fail path appends a notes-only save after it.
        return out, transition, save.call_args_list[0][0][1], scrape, log

    @pytest.mark.asyncio
    async def test_refresh_rescrapes_already_scraped_url(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        out, _t, saved, scrape, log = await self._run_pjl(
            monkeypatch,
            {
                "possible_joblist_links": ["acme.com/careers", "acme.com/jobs"],
                "pjl_scrape_pages": [{"url": "https://acme.com/careers", "visible_text": "existing"}],
            },
            {
                "acme.com/careers": {"url": "https://acme.com/careers", "visible_text": "fresh", "page_links": []},
                "acme.com/jobs": {"url": "https://acme.com/jobs", "visible_text": "more roles", "page_links": []},
            },
            debug=True,
        )
        assert out == {"passed": 1, "failed": 0, "total": 1}
        # Both URLs scraped, in candidate order — the stored careers row no longer short-circuits.
        assert [c.args[0] for c in scrape.await_args_list] == ["acme.com/careers", "acme.com/jobs"]
        # Replaced row keeps index 0; the new URL appends.
        assert saved["pjl_scrape_pages"] == [
            {"url": "https://acme.com/careers", "visible_text": "fresh"},
            {"url": "https://acme.com/jobs", "visible_text": "more roles"},
        ]
        # Style D per-URL line for every scraped URL; no ledger skip line survives.
        outcomes = [c.kwargs.get("outcome") or "" for c in log.debug_index.call_args_list]
        assert not any("skipped-already-scraped" in o for o in outcomes)
        assert any("'acme.com/careers' scraped" in o for o in outcomes)
        assert any("'acme.com/jobs' scraped" in o for o in outcomes)

    @pytest.mark.asyncio
    async def test_ast1995_repro_rescrape_replaces_row_and_rebuilds_nav(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Plan fixture verbatim (docs/features/roster/ast-719-… § Bug: AST-1995 → Repro).
        out, transition, saved, scrape, _log = await self._run_pjl(
            monkeypatch,
            {
                "possible_joblist_links": ["acme.com/careers"],
                "pjl_scrape_pages": [
                    {"url": "https://acme.com/careers", "visible_text": "OLD BOARD: Role A",
                     "enumerated_nav_links": "1: https://acme.com/jobs/a"},
                ],
                "pjl_nav_links": "1: https://acme.com/jobs/a",
            },
            {
                "acme.com/careers": {"url": "https://acme.com/careers", "visible_text": "NEW BOARD: Role B",
                                     "page_links": ["https://acme.com/jobs/b"],
                                     "enumerated_nav_links": "1: https://acme.com/jobs/b"},
            },
        )
        scrape.assert_awaited_once()
        assert saved["pjl_scrape_pages"] == [
            {"url": "https://acme.com/careers", "visible_text": "NEW BOARD: Role B",
             "enumerated_nav_links": "1: https://acme.com/jobs/b"},
        ]
        assert "NEW BOARD" in saved["pjl_assembled_content"]
        assert "OLD BOARD" not in saved["pjl_assembled_content"]
        # Rebuilt from this run only — the dead /jobs/a link drops off.
        assert saved["pjl_nav_links"] == "1: https://acme.com/jobs/b"
        assert out == {"passed": 1, "failed": 0, "total": 1}
        transition.assert_called_once_with("acme", "PJL_READY")

    @pytest.mark.asyncio
    async def test_ast1995_failed_rescrape_keeps_prior_row_and_carries_its_nav(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        prior = {"url": "https://acme.com/careers", "visible_text": "OLD BOARD",
                 "enumerated_nav_links": "1: https://acme.com/jobs/a"}
        out, transition, saved, scrape, log = await self._run_pjl(
            monkeypatch,
            {
                "possible_joblist_links": ["acme.com/careers"],
                "pjl_scrape_pages": [dict(prior)],
                # /jobs/dead is in the stored global enum but not in the row's own links.
                "pjl_nav_links": "1: https://acme.com/jobs/a\n2: https://acme.com/jobs/dead",
            },
            {"acme.com/careers": {"url": "https://acme.com/careers", "visible_text": "",
                                  "page_links": [], "error": "Timeout 30000ms exceeded"}},
            debug=True,
        )
        scrape.assert_awaited_once()
        outcomes = [c.kwargs.get("outcome") or "" for c in log.debug_index.call_args_list]
        assert any("'acme.com/careers' error=" in o for o in outcomes)
        # Transient failure never deletes stored content.
        assert saved["pjl_scrape_pages"] == [prior]
        assert "OLD BOARD" in saved["pjl_assembled_content"]
        # Prior row's last-known links carry forward; the stale global entry does not.
        assert saved["pjl_nav_links"] == "1: https://acme.com/jobs/a"
        assert out == {"passed": 1, "failed": 0, "total": 1}
        transition.assert_called_once_with("acme", "PJL_READY")

    @pytest.mark.asyncio
    async def test_ast1995_failed_scrape_without_prior_row_contributes_no_nav(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _out, _t, saved, _scrape, _log = await self._run_pjl(
            monkeypatch,
            {"possible_joblist_links": ["acme.com/careers", "acme.com/jobs"]},
            {
                "acme.com/careers": {"url": "https://acme.com/careers", "visible_text": "roles",
                                     "page_links": ["https://acme.com/jobs/b"]},
                # Empty capture with links: no stored row to fall back on, so its links are ignored.
                "acme.com/jobs": {"url": "https://acme.com/jobs", "visible_text": "  ",
                                  "page_links": ["https://acme.com/jobs/z"]},
            },
        )
        assert saved["pjl_scrape_pages"] == [{"url": "https://acme.com/careers", "visible_text": "roles"}]
        assert saved["pjl_nav_links"] == "1: https://acme.com/jobs/b"

    @pytest.mark.asyncio
    async def test_ast1995_nav_written_empty_and_non_candidate_rows_kept(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        orphan = {"url": "https://acme.com/old-careers", "visible_text": "legacy board",
                  "enumerated_nav_links": "1: https://acme.com/jobs/x"}
        _out, transition, saved, _scrape, _log = await self._run_pjl(
            monkeypatch,
            {
                "possible_joblist_links": ["acme.com/careers"],
                "pjl_scrape_pages": [
                    dict(orphan),
                    {"url": "https://acme.com/careers", "visible_text": "OLD",
                     "enumerated_nav_links": "1: https://acme.com/jobs/a"},
                ],
                "pjl_nav_links": "1: https://acme.com/jobs/x\n2: https://acme.com/jobs/a",
            },
            {"acme.com/careers": {"url": "https://acme.com/careers", "visible_text": "NEW", "page_links": []}},
        )
        # Non-candidate row stays at index 0 (no pruning); careers replaced whole-row at index 1.
        assert saved["pjl_scrape_pages"] == [
            orphan,
            {"url": "https://acme.com/careers", "visible_text": "NEW"},
        ]
        # Always written, even empty: the orphan's links and the old careers links must not survive.
        assert saved["pjl_nav_links"] == ""
        transition.assert_called_once_with("acme", "PJL_READY")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("debug", [False, True])
    async def test_all_scrapes_empty_fails_with_notes(
        self, monkeypatch: pytest.MonkeyPatch, debug: bool,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_browser_context(monkeypatch)
        transition = MagicMock()
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(
            gazer_mod,
            "_scrape_pjl_page",
            AsyncMock(return_value={"url": "https://acme.com/careers", "visible_text": "", "page_links": []}),
        )
        companies = [
            {
                "short_name": "acme",
                "company_data": {"possible_joblist_links": ["acme.com/careers"]},
            }
        ]
        out = await gazer_mod.fetch_job_pages_batch("batch-1", companies, debug=debug)
        assert out == {"passed": 0, "failed": 1, "total": 1}
        transition.assert_called_once_with("acme", "ERROR_FETCH_JOB_PAGES_UNREADABLE")
        assert save.call_args_list[-1][0][1]["prefilter_company_notes"] == (
            "fetch_job_pages: all PJL scrapes failed"
        )


class TestFetchJdBatch:
    @pytest.mark.asyncio
    async def test_aborts_without_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.fetch_jd_batch("batch-1", [])

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
        out = await gazer_mod.fetch_jd_batch("batch-1", jobs)
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
        out = await gazer_mod.fetch_jd_batch("batch-1", jobs, debug=True)
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
        out = await gazer_mod.fetch_jd_batch("batch-1", jobs)
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
        out = await gazer_mod.fetch_jd_batch("batch-1", [job], debug=False)
        assert out == {"passed": 1, "failed": 0, "total": 1, "errors": 0}
        assert job["job_data"]["note"] == "keep"

    @pytest.mark.asyncio
    async def test_collapses_consecutive_blank_lines_before_save(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        save = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", MagicMock())
        monkeypatch.setattr(gazer_mod, "save_job_data", save)
        monkeypatch.setattr(gazer_mod, "_classify_jd", MagicMock(return_value="ok"))
        raw_jd = "role summary\n\n\n\n" + ("detail " * 120)
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(return_value=raw_jd))
        job = {"astral_job_id": "job-9", "job_link": "https://example.com/j", "job_title": "Role"}
        out = await gazer_mod.fetch_jd_batch("batch-1", [job])
        assert out == {"passed": 1, "failed": 0, "total": 1, "errors": 0}
        saved = job["job_data"]["job_description"]
        assert "\n\n\n" not in saved
        assert saved.startswith("role summary\n\n")


def _rel_job(aid: str, href: str, site: str = "https://co.example/careers") -> dict[str, Any]:
    return {"astral_job_id": aid, "job_site": site, "job_link": href, "job_title": "Role"}


@pytest.fixture
def rel_env(monkeypatch: pytest.MonkeyPatch):
    """Stub connectivity / DB writes; `click` maps href → (final_url, text) or an exception."""
    monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
    env = SimpleNamespace(
        transition=MagicMock(), save=MagicMock(), persist=MagicMock(), routes={},
    )

    async def _click(list_url: str, href: str):
        out = env.routes[href]
        if isinstance(out, BaseException):
            raise out
        return out

    env.click = AsyncMock(side_effect=_click)
    monkeypatch.setattr(gazer_mod, "transition_job_state", env.transition)
    monkeypatch.setattr(gazer_mod, "save_job_data", env.save)
    monkeypatch.setattr(gazer_mod, "persist_http_job_link", env.persist)
    monkeypatch.setattr(gazer_mod, "click_through_visible_text", env.click)
    # Final state per job id, read from transition_job_state([aid], state) calls.
    env.states = lambda: {c.args[0][0]: c.args[1] for c in env.transition.call_args_list}
    return env


def _miss() -> Exception:
    return gazer_mod.PlaywrightInfraError(gazer_mod.TELESCOPE_CLICK_TARGET_MISSING, "no anchor")


# AST-2025 · AST-2022: fetch_relative_jd_batch click-through runner.
# Branches: AC4 ok / bot / closed / click miss (real _classify_jd on config signals); other
# Telescope error; non-http final_url; missing job_site / job_link; short text after click;
# no connectivity; miss = warning only vs other error = logger.exception; AC5 shared gate helper.
class TestAst2025FetchRelativeJdBatch:
    _CFG = gazer_mod.TRACKER_CONFIG["jd_classifier"]
    # Signals trail the body: _prune_jd trims the page head before classification.
    _BOT = _OK_JD + " " + " ".join(_CFG["bot_signals"][: _CFG.get("bot_threshold", 2)])
    _CLOSED = _OK_JD + " " + _CFG["closed_signals"][0]

    @pytest.mark.asyncio
    async def test_ac4_outcomes(self, rel_env) -> None:
        rel_env.routes.update({
            "/ok": ("https://ats.example/ok", _OK_JD),
            "/bot": ("https://ats.example/bot", self._BOT),
            "/closed": ("https://ats.example/closed", self._CLOSED),
            "/gone": _miss(),
        })
        jobs = [_rel_job("j-ok", "/ok"), _rel_job("j-bot", "/bot"), _rel_job("j-closed", "/closed"),
                _rel_job("j-gone", "/gone")]
        out = await gazer_mod.fetch_relative_jd_batch("b-1", jobs)
        assert out == {"passed": 1, "failed": 3, "total": 4}
        assert rel_env.states() == {
            "j-ok": "JD_READY", "j-bot": "BOT_BLOCKED_FETCH_RELATIVE_JD",
            "j-closed": "JD_SCRAPE_FAIL_CLOSED", "j-gone": "ERROR_FETCH_RELATIVE_JD_CLICK",
        }
        # Telescope opens the company job_site and clicks the stored relative href.
        assert {c.args for c in rel_env.click.await_args_list} == {
            ("https://co.example/careers", h) for h in ("/ok", "/bot", "/closed", "/gone")
        }
        # job_link resolved for every reached destination; click miss leaves it relative.
        assert {c.args for c in rel_env.persist.call_args_list} == {
            ("j-ok", "https://ats.example/ok"), ("j-bot", "https://ats.example/bot"),
            ("j-closed", "https://ats.example/closed"),
        }
        assert jobs[0]["job_data"]["job_description"].startswith("role summary")
        assert any(c.args[0] == "j-ok" and "job_description" in c.args[1] for c in rel_env.save.call_args_list)

    @pytest.mark.asyncio
    async def test_click_miss_warns_other_error_logs_exception(self, rel_env, caplog) -> None:
        rel_env.routes.update({"/gone": _miss(), "/boom": RuntimeError("telescope down")})
        with caplog.at_level(logging.WARNING, logger="src.core.gazer"):
            out = await gazer_mod.fetch_relative_jd_batch(
                "b-2", [_rel_job("j-gone", "/gone"), _rel_job("j-boom", "/boom")]
            )
        assert out == {"passed": 0, "failed": 2, "total": 2}
        assert rel_env.states() == {"j-gone": "ERROR_FETCH_RELATIVE_JD_CLICK", "j-boom": "ERROR_FETCH_RELATIVE_JD_CLICK"}
        rel_env.persist.assert_not_called()
        gone = [r for r in caplog.records if "j-gone" in r.getMessage()]
        boom = [r for r in caplog.records if "j-boom" in r.getMessage()]
        # Configured miss: one warning, no traceback. Other failure: logged once with exc_info.
        assert [r.levelname for r in gone] == ["WARNING"] and gone[0].exc_info is None
        assert [r.levelname for r in boom] == ["ERROR"] and boom[0].exc_info is not None

    @pytest.mark.asyncio
    async def test_non_http_final_url_fails_without_persist(self, rel_env) -> None:
        rel_env.routes["/odd"] = ("/still/relative", _OK_JD)
        out = await gazer_mod.fetch_relative_jd_batch("b-3", [_rel_job("j-odd", "/odd")])
        assert out["failed"] == 1
        assert rel_env.states() == {"j-odd": "ERROR_FETCH_RELATIVE_JD_CLICK"}
        rel_env.persist.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_job_site_or_link_fails_without_click(self, rel_env) -> None:
        jobs = [_rel_job("j-nosite", "/a", site=""), _rel_job("j-nolink", "")]
        out = await gazer_mod.fetch_relative_jd_batch("b-4", jobs)
        assert out == {"passed": 0, "failed": 2, "total": 2}
        assert rel_env.states() == {"j-nosite": "ERROR_FETCH_RELATIVE_JD_CLICK", "j-nolink": "ERROR_FETCH_RELATIVE_JD_CLICK"}
        rel_env.click.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_short_text_after_click_is_relative_unreadable_with_link_resolved(self, rel_env) -> None:
        rel_env.routes.update({"/short": ("https://ats.example/s", "too short"),
                               "/blank": ("https://ats.example/b", "   ")})
        out = await gazer_mod.fetch_relative_jd_batch(
            "b-5", [_rel_job("j-short", "/short"), _rel_job("j-blank", "/blank")]
        )
        assert out["failed"] == 2
        # AST-2086: destination reached → this task's own _UNREADABLE (not _CLICK, not fetch_jd's), link resolved.
        assert rel_env.states() == {
            "j-short": "ERROR_FETCH_RELATIVE_JD_UNREADABLE", "j-blank": "ERROR_FETCH_RELATIVE_JD_UNREADABLE",
        }
        assert rel_env.persist.call_count == 2

    @pytest.mark.asyncio
    async def test_aborts_without_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.fetch_relative_jd_batch("b-6", [])

    @pytest.mark.asyncio
    async def test_ac5_both_runners_call_shared_gate_helper(
        self, rel_env, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        seen: list[dict[str, Any]] = []
        real = gazer_mod._apply_jd_gates

        def spy(job, text, **kw):
            seen.append({"aid": job["astral_job_id"], **kw})
            return real(job, text, **kw)

        monkeypatch.setattr(gazer_mod, "_apply_jd_gates", spy)
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(return_value=_OK_JD))
        rel_env.routes["/ok"] = ("https://ats.example/ok", _OK_JD)
        await gazer_mod.fetch_jd_batch("b-7", [{"astral_job_id": "j-abs", "job_link": "https://x.example/j"}])
        await gazer_mod.fetch_relative_jd_batch("b-8", [_rel_job("j-rel", "/ok")])
        # AST-2086: each runner passes its own task's unreadable terminal and classified_states map.
        assert seen == [
            {"aid": "j-abs", "short_state": "ERROR_FETCH_JD_UNREADABLE", "pass_state": "JD_READY",
             "classified_states": gazer_mod.GAZER_CONFIG["fetch_jd"]["classified_states"]},
            {"aid": "j-rel", "short_state": "ERROR_FETCH_RELATIVE_JD_UNREADABLE", "pass_state": "JD_READY",
             "classified_states": gazer_mod.GAZER_CONFIG["fetch_relative_jd"]["classified_states"]},
        ]



# Branches: connectivity; missing company; cached content; no links; coat-check pass/fail (AST-874).
class TestWebsiteContentHelpers:
    def test_recorded_list_string_and_empty(self) -> None:
        assert gazer_mod._website_content_is_recorded(
            [{"url": "https://c.example/a", "content": "culture body"}]
        )
        assert gazer_mod._website_content_is_recorded("  plain culture  ")
        assert not gazer_mod._website_content_is_recorded([])
        assert not gazer_mod._website_content_is_recorded([{"url": "x", "content": "  "}])
        assert not gazer_mod._website_content_is_recorded("")
        assert not gazer_mod._website_content_is_recorded(None)

    def test_debug_summary_shapes(self) -> None:
        assert "pages=1" in gazer_mod._website_content_debug_summary(
            [{"url": "https://c.example/a", "content": "body"}]
        )
        assert gazer_mod._website_content_debug_summary("abcd") == "chars=4"
        assert gazer_mod._website_content_debug_summary(None) == "empty"


class TestFetchCulturePagesBatch:
    @pytest.mark.asyncio
    async def test_aborts_without_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.fetch_culture_pages_batch("batch-1", [])

    @pytest.mark.asyncio
    async def test_missing_company_fails_need_culture_content(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_company", MagicMock(return_value=None))
        jobs = [
            {"astral_job_id": "j-empty", "company": ""},
            {"astral_job_id": "j-miss", "company": "ghost"},
        ]
        out = await gazer_mod.fetch_culture_pages_batch("batch-1", jobs)
        assert out == {"passed": 0, "failed": 2, "total": 2}
        assert transition.call_args_list[0].args == (["j-empty"], "ERROR_FETCH_CULTURE_PAGES_UNREADABLE")
        assert transition.call_args_list[1].args == (["j-miss"], "ERROR_FETCH_CULTURE_PAGES_UNREADABLE")

    @pytest.mark.asyncio
    async def test_cached_website_content_passes_without_coat_check(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        coat = AsyncMock()
        company = {
            "short_name": "acme",
            "company_data": {
                "website_content": [{"url": "https://acme.com/culture", "content": "values"}],
            },
        }
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(gazer_mod, "get_company_data", coat)
        job = {"astral_job_id": "j-cache", "company": "acme"}
        out = await gazer_mod.fetch_culture_pages_batch("batch-1", [job], debug=True)
        assert out == {"passed": 1, "failed": 0, "total": 1}
        transition.assert_called_once_with(["j-cache"], "CULTURE_READY")
        coat.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_culture_links_transitions_no_culture_links(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        company = {"short_name": "acme", "company_data": {"culture_links_to_explore": []}}
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(gazer_mod, "get_company_data", AsyncMock())
        out = await gazer_mod.fetch_culture_pages_batch(
            "batch-1", [{"astral_job_id": "j-nolink", "company": "acme"}],
        )
        assert out == {"passed": 0, "failed": 1, "total": 1}
        transition.assert_called_once_with(["j-nolink"], "ERROR_FETCH_CULTURE_PAGES_NO_CULTURE_LINKS")

    @pytest.mark.asyncio
    async def test_coat_check_pass_and_empty_fail(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        co_ok = {
            "short_name": "okco",
            "company_data": {"culture_links_to_explore": ["https://ok.co/c"]},
        }
        co_bad = {
            "short_name": "badco",
            "company_data": {"culture_links_to_explore": ["https://bad.co/c"]},
        }
        companies = {"okco": co_ok, "badco": co_bad}

        def _get_company(key: str):
            return companies.get(key)

        async def _coat(company: Dict[str, Any], key: str):
            assert key == "website_content"
            if company["short_name"] == "okco":
                return [{"url": "https://ok.co/c", "content": "ok culture"}]
            return None

        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_company", _get_company)
        monkeypatch.setattr(gazer_mod, "get_company_data", _coat)
        jobs = [
            {"astral_job_id": "j-ok", "company": "okco"},
            {"astral_job_id": "j-bad", "company": "badco"},
        ]
        out = await gazer_mod.fetch_culture_pages_batch("batch-1", jobs)
        assert out == {"passed": 1, "failed": 1, "total": 2}
        assert transition.call_args_list[0].args == (["j-ok"], "CULTURE_READY")
        assert transition.call_args_list[1].args == (["j-bad"], "ERROR_FETCH_CULTURE_PAGES_UNREADABLE")
        assert co_ok["company_data"]["website_content"][0]["content"] == "ok culture"

    @pytest.mark.asyncio
    async def test_second_job_same_company_uses_in_memory_cache(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """After coat-check writeback, later jobs for the same company skip a second scrape."""
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        company = {
            "short_name": "acme",
            "company_data": {"culture_links_to_explore": ["https://acme.com/c"]},
        }
        coat = AsyncMock(return_value=[{"url": "https://acme.com/c", "content": "body"}])
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(gazer_mod, "get_company_data", coat)
        jobs = [
            {"astral_job_id": "j1", "company": "acme"},
            {"astral_job_id": "j2", "company": "acme"},
        ]
        out = await gazer_mod.fetch_culture_pages_batch("batch-1", jobs)
        assert out == {"passed": 2, "failed": 0, "total": 2}
        assert coat.await_count == 1
        assert transition.call_args_list[0].args == (["j1"], "CULTURE_READY")
        assert transition.call_args_list[1].args == (["j2"], "CULTURE_READY")



# AST-2070 (parent AST-2054): GET_UPSHOT culture fetch — every claimed company advances to UPSHOT_READY.
class TestAst2070FetchCompanyCulturePagesBatch:
    @pytest.mark.asyncio
    async def test_aborts_without_connectivity_before_any_transition(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        with pytest.raises(ConnectionError, match="no internet connectivity"):
            await gazer_mod.fetch_company_culture_pages_batch("b1", [{"short_name": "a"}])
        transition.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("debug", [True, False])
    async def test_every_company_advances_whatever_was_found(
        self, monkeypatch: pytest.MonkeyPatch, debug: bool,
    ) -> None:
        # AC4: cached / scraped / none found / coat-check ValueError / no company_data all → UPSHOT_READY
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)

        async def _coat(company: dict[str, Any], key: str):
            assert key == "website_content"
            if company["short_name"] == "boom":
                raise ValueError("no company_website")
            if company["short_name"] == "scraped":
                return [{"url": "https://s.co/c", "content": "culture"}]
            return None

        coat = AsyncMock(side_effect=_coat)
        monkeypatch.setattr(gazer_mod, "get_company_data", coat)
        companies = [
            {"short_name": "cached", "company_data": {"website_content": [{"url": "u", "content": "kept"}]}},
            {"short_name": "scraped", "company_data": {"culture_links_to_explore": ["https://s.co/c"]}},
            {"short_name": "empty", "company_data": {"culture_links_to_explore": []}},
            {"short_name": "boom", "company_data": {}},
            {"short_name": "nodata", "company_data": None},
        ]
        out = await gazer_mod.fetch_company_culture_pages_batch("b2", companies, debug=debug)
        assert out == {"passed": 5, "failed": 0, "total": 5}
        assert [c.args for c in transition.call_args_list] == [
            (c["short_name"], "UPSHOT_READY") for c in companies
        ]
        # cached content skips the scrape; the other four go through the coat-check
        assert [c.args[0]["short_name"] for c in coat.await_args_list] == ["scraped", "empty", "boom", "nodata"]


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



# Branches: identifier fallbacks; AST-622 debug instrumentation (no log-string asserts).
class TestGazerIdentifierHelpers:
    def test_job_identifier_falls_back_to_title_then_question(self) -> None:
        assert gazer_mod._gazer_job_identifier({"job_title": "Role"}) == "Role"
        assert gazer_mod._gazer_job_identifier({}) == "?"

    def test_company_identifier_falls_back_to_question(self) -> None:
        assert gazer_mod._gazer_company_identifier({"short_name": "acme"}) == "acme"
        assert gazer_mod._gazer_company_identifier({}) == "?"


class TestLogListingDedupeTrace:
    def test_duplicate_title_miss_and_insert_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        log = MagicMock()
        monkeypatch.setattr(
            gazer_mod,
            "raw_job_listing_is_duplicate",
            lambda _co, raw: raw == "dup",
        )
        patterns = [re.compile("engineer", re.I)]
        gazer_mod._log_listing_dedupe_trace(
            log, "co", ["dup", "janitor", "senior engineer"], patterns
        )
        assert log.debug_detail.call_count >= 3

    def test_omits_listings_beyond_cap(self, monkeypatch: pytest.MonkeyPatch) -> None:
        log = MagicMock()
        monkeypatch.setattr(gazer_mod, "raw_job_listing_is_duplicate", lambda *_: False)
        listings = [f"listing-{i}" for i in range(30)]
        gazer_mod._log_listing_dedupe_trace(log, "co", listings, None)
        messages = [str(c.args[0]) for c in log.debug_detail.call_args_list]
        assert any("omitted from dedupe trace" in m for m in messages)


class TestFetchJdBatchDebugPaths:
    @pytest.mark.asyncio
    async def test_failure_paths_with_debug_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "transition_job_state", MagicMock())
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(side_effect=RuntimeError("boom")))
        jobs = [{"astral_job_id": "job-1", "job_link": ""}]
        out = await gazer_mod.fetch_jd_batch("batch-1", jobs, debug=True)
        assert out["failed"] == 1

    @pytest.mark.asyncio
    async def test_scrape_error_empty_short_and_classified_with_debug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "transition_job_state", MagicMock())
        monkeypatch.setattr(gazer_mod, "save_job_data", MagicMock())
        monkeypatch.setattr(
            gazer_mod,
            "get_visible_text",
            AsyncMock(side_effect=[RuntimeError("net"), "   ", "short", _OK_JD]),
        )
        monkeypatch.setattr(gazer_mod, "_classify_jd", MagicMock(return_value="cookie"))
        jobs = [
            {"astral_job_id": "j1", "job_link": "https://example.com/a"},
            {"astral_job_id": "j2", "job_link": "https://example.com/b", "job_title": "B"},
            {"astral_job_id": "j3", "job_link": "https://example.com/c", "job_title": "C"},
            {"astral_job_id": "j4", "job_link": "https://example.com/d", "job_title": "D"},
        ]
        out = await gazer_mod.fetch_jd_batch("batch-1", jobs, debug=True)
        assert out["failed"] == 4


class TestValidateTitleBatchDebugPaths:
    @pytest.mark.asyncio
    async def test_pass_fail_and_summary_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        ctx = {"candidate_data": {"contact": {"title_patterns": "engineer"}}}
        jobs = [
            {"astral_job_id": "job-ok", "job_data": {"raw_job_listing": "senior engineer"}},
            {"astral_job_id": "job-bad", "job_data": {"raw_job_listing": "janitor"}},
        ]
        out = await gazer_mod.validate_title_batch("batch-1", jobs, ctx, debug=True)
        assert out == {"passed": 1, "failed": 1, "total": 2}


class TestProcessGazerBatchDebugPaths:
    @pytest.mark.asyncio
    async def test_no_parse_instructions_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(
            gazer_mod,
            "scrape_one",
            AsyncMock(return_value=("noparse", "https://example.com/noparse", "<html/>")),
        )
        monkeypatch.setattr(gazer_mod, "get_company_data", AsyncMock(return_value={}))
        record = MagicMock()
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", record)
        monkeypatch.setattr(gazer_mod, "update_company_last_scan_at", MagicMock())

        outcomes = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "noparse", "job_site": "https://example.com/noparse"}],
            debug=True,
        )
        assert outcomes[0]["status"] == "failure"
        assert "parse_instructions" in outcomes[0]["message"]

    @pytest.mark.asyncio
    async def test_dedupe_trace_with_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(
            gazer_mod,
            "scrape_one",
            AsyncMock(return_value=("goodco", "https://example.com/good", "<html>good</html>")),
        )

        async def _company_data(company: Dict[str, Any], key: str) -> Dict[str, Any]:
            return {"container": "motion", "job_tag": "a", "container_index": 0}

        monkeypatch.setattr(gazer_mod, "get_company_data", _company_data)
        monkeypatch.setattr(
            gazer_mod,
            "extract_raw_job_listings",
            MagicMock(return_value=["dup listing", "engineer listing"]),
        )
        monkeypatch.setattr(
            gazer_mod,
            "raw_job_listing_is_duplicate",
            lambda _co, raw: raw == "dup listing",
        )
        monkeypatch.setattr(
            gazer_mod,
            "ingest_jobs",
            MagicMock(return_value={"new": 1, "duplicates": 1, "invalid_title": 0}),
        )
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", MagicMock())
        monkeypatch.setattr(gazer_mod, "update_company_last_scan_at", MagicMock())

        ctx = {"candidate_data": {"contact": {"title_patterns": "engineer"}}}
        outcomes = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "goodco", "job_site": "https://example.com/good"}],
            debug=True,
            ctx=ctx,
        )
        assert outcomes[0]["status"] == "success"


class TestProcessGazerBatchDebugBranchCoverage:
    @pytest.mark.asyncio
    async def test_empty_companies_with_debug_skips_batch_start(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        outcomes = await gazer_mod.process_gazer_batch("batch-1", [], debug=True)
        assert outcomes == []

    @pytest.mark.asyncio
    async def test_failure_paths_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(
            gazer_mod,
            "scrape_one",
            AsyncMock(side_effect=RuntimeError("scrape failed")),
        )
        record = MagicMock()
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", record)

        outcomes = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "badco", "job_site": "https://example.com/bad"}],
            debug=False,
        )
        assert outcomes[0]["status"] == "failure"

    @pytest.mark.asyncio
    async def test_empty_extracted_listings_with_debug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(
            gazer_mod,
            "scrape_one",
            AsyncMock(return_value=("goodco", "https://example.com/good", "<html/>")),
        )

        async def _company_data(company: Dict[str, Any], key: str) -> Dict[str, Any]:
            return {"container": "motion", "job_tag": "a", "container_index": 0}

        monkeypatch.setattr(gazer_mod, "get_company_data", _company_data)
        monkeypatch.setattr(gazer_mod, "extract_raw_job_listings", MagicMock(return_value=[]))
        monkeypatch.setattr(
            gazer_mod,
            "ingest_jobs",
            MagicMock(return_value={"new": 0, "duplicates": 0, "invalid_title": 0}),
        )
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", MagicMock())
        monkeypatch.setattr(gazer_mod, "update_company_last_scan_at", MagicMock())

        outcomes = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "goodco", "job_site": "https://example.com/good"}],
            debug=True,
        )
        assert outcomes[0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_success_and_ingest_error_without_debug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
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
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", MagicMock())
        monkeypatch.setattr(gazer_mod, "update_company_last_scan_at", MagicMock())

        ingest = MagicMock(return_value={"new": 1, "duplicates": 0, "invalid_title": 0})
        monkeypatch.setattr(gazer_mod, "ingest_jobs", ingest)

        ok = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "goodco", "job_site": "https://example.com/good"}],
            debug=False,
        )
        assert ok[0]["status"] == "success"

        ingest.side_effect = RuntimeError("ingest failed")
        bad = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "goodco", "job_site": "https://example.com/good"}],
            debug=False,
        )
        assert bad[0]["status"] == "failure"

    @pytest.mark.asyncio
    async def test_no_parse_instructions_without_debug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(
            gazer_mod,
            "scrape_one",
            AsyncMock(return_value=("noparse", "https://example.com/noparse", "<html/>")),
        )
        monkeypatch.setattr(gazer_mod, "get_company_data", AsyncMock(return_value={}))
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", MagicMock())

        outcomes = await gazer_mod.process_gazer_batch(
            "batch-1",
            [{"short_name": "noparse", "job_site": "https://example.com/noparse"}],
            debug=False,
        )
        assert outcomes[0]["status"] == "failure"


class TestFetchJdBatchDebugBranchCoverage:
    @pytest.mark.asyncio
    async def test_classified_failure_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "transition_job_state", MagicMock())
        monkeypatch.setattr(gazer_mod, "save_job_data", MagicMock())
        monkeypatch.setattr(gazer_mod, "_classify_jd", MagicMock(return_value="cookie"))
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(return_value=_OK_JD))
        jobs = [{"astral_job_id": "job-3", "job_link": "https://example.com/a", "job_title": "A"}]
        out = await gazer_mod.fetch_jd_batch("batch-1", jobs, debug=False)
        assert out["failed"] == 1




# Branches: body vs links; Playwright mock; dedupe skips; Style D on/off (AST-1061).
class TestAst1061MeteoriteEmailIngest:
    def test_body_mode_creates_without_job_link(self, sqlite_in_memory, monkeypatch) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1061-body"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        html = "<div class='email-body'><p>" + ("Body JD text enough chars. " * 4) + "</p></div>"
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=False)
        assert out["mode"] == "body"
        assert len(out["created"]) == 1
        assert out["skipped"] == []
        row = db.get_job(out["created"][0]["astral_job_id"])
        assert row is not None
        assert row["job_link"] is None
        assert row["company_job_id"] is None

    def test_body_mode_skips_known_company_job_id(self, sqlite_in_memory) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1061-dup"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        # AST-1132: candidate-scoped id match requires company.candidate_id.
        db.save_company("acme", state="IMPORTED", candidate_id=cid)
        db.save_job("j-known", company="acme", state="NEW", company_job_id="KNOWN-EXT-77")
        html = "<p>" + ("x" * 20) + " KNOWN-EXT-77 " + ("y" * 20) + "</p>"
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=False)
        assert out["mode"] == "body"
        assert out["created"] == []
        assert out["skipped"][0]["reason"] == "known_company_job_id"
        assert out["skipped"][0]["matched_company_job_id"] == "KNOWN-EXT-77"

    def test_links_mode_playwright_create_and_dedupe(
        self, sqlite_in_memory, monkeypatch
    ) -> None:
        import asyncio
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1061-links"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        good = "https://jobs.example.com/role/good"
        known = "https://jobs.example.com/role/known"
        # AST-1132: candidate-scoped link dedupe requires company.candidate_id.
        db.save_company("acme", state="IMPORTED", candidate_id=cid)
        db.save_job("j-link", company="acme", state="NEW", job_link=known)

        async def fake_fetch(url, *, debug=False):
            if url == known:
                return ("visible text " * 10, url)
            return ("Visible JD from playwright fetch with enough length!!", url)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        html = (
            f'<a href="{good}">Apply</a>'
            f'<a href="{known}">Known</a>'
            '<a href="mailto:x@y">mail</a>'
            '<a href="https://list-manage.com/unsub">bad</a>'
        )
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=False)
        assert out["mode"] == "links"
        assert len(out["created"]) == 1
        assert out["created"][0]["astral_job_id"]
        reasons = {s["reason"] for s in out["skipped"]}
        assert "known_job_link" in reasons
        row = db.get_job(out["created"][0]["astral_job_id"])
        assert row["job_link"] == good

    def test_links_jd_too_short_skipped(self, sqlite_in_memory, monkeypatch) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1061-short"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        url = "https://jobs.example.com/role/short"

        async def fake_fetch(u, *, debug=False):
            return ("tiny", u)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(
            cid, f'<a href="{url}">x</a>', debug=False
        )
        assert out["mode"] == "links"
        assert out["created"] == []
        assert out["skipped"][0]["reason"] == "jd_too_short"

    def test_debug_true_emits_style_d_body(self, sqlite_in_memory, monkeypatch) -> None:
        from src.core import gazer as gazer_mod
        from unittest.mock import MagicMock

        db = sqlite_in_memory
        cid = "cand-1061-dbg"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "G"})
        log = MagicMock()
        monkeypatch.setattr(gazer_mod, "get_logger", lambda _n: log)
        html = "<p>" + ("Debug body JD characters enough. " * 3) + "</p>"
        gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=True)
        log.set_debug_flag.assert_called_with(True)
        outcomes = [c.kwargs.get("outcome") for c in log.debug_index.call_args_list]
        assert "found" in outcomes and "recorded" in outcomes

    def test_validation_errors(self) -> None:
        from src.core import gazer as gazer_mod
        import pytest

        with pytest.raises(ValueError, match="candidate_id is required"):
            gazer_mod.ingest_meteorite_jobs_from_email_html_sync("", "<p>x</p>")
        with pytest.raises(ValueError, match="html is required"):
            gazer_mod.ingest_meteorite_jobs_from_email_html_sync("cand", "  ")


# Branches: paste normalize before candidate links — UAT escape + bare list (AST-1131).
class TestAst1131NormalizePastedListEmailIngest:
    _UID = "9f704ad3-7a18-506a-bd5e-6a84e73b7c00"
    _DICE = f"https://www.dice.com/job-detail/{_UID}"

    def test_escaped_nested_autolink_creates_clean_job_link(
        self, sqlite_in_memory, monkeypatch
    ) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1131-escape"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "E"})

        async def fake_fetch(url, *, debug=False):
            return ("Visible JD from playwright fetch with enough length!!", url)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        html = (
            f'&lt;div xmlns="&lt;a href="http://www.w3.org/2000/svg"&gt;'
            f'http://www.w3.org/2000/svg&lt;/a&gt;"&gt;'
            f'&lt;a href="&lt;a href="{self._DICE}"&gt;{self._DICE}&lt;/a&gt;"&gt;Job&lt;/a&gt;'
            f'&lt;/div&gt;'
        )
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=False)
        assert out["mode"] == "links"
        assert len(out["created"]) == 1
        row = db.get_job(out["created"][0]["astral_job_id"])
        assert row["job_link"] == self._DICE
        assert "<a" not in (row["job_link"] or "")
        # SVG namespace must not become a created job_link candidate.
        assert all(
            "w3.org" not in (s.get("url") or "")
            for s in out["skipped"]
        )
        assert "w3.org" not in (row["job_link"] or "")

    def test_newline_bare_urls_enter_links_mode(
        self, sqlite_in_memory, monkeypatch
    ) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1131-bare"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        other = "https://jobs.example.com/role/two"

        async def fake_fetch(url, *, debug=False):
            return ("Visible JD from playwright fetch with enough length!!", url)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(
            cid, f"{self._DICE}\n{other}", debug=False
        )
        assert out["mode"] == "links"
        created_links = {db.get_job(c["astral_job_id"])["job_link"] for c in out["created"]}
        assert created_links == {self._DICE, other}


# Branches: exclude/allow, non-job visible skip, candidate-scoped dedupe (AST-1132).
class TestAst1132MeteoriteEmailIngestHygiene:
    def test_w3_org_href_excluded_from_candidates(
        self, sqlite_in_memory, monkeypatch
    ) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1132-ex"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "X"})
        good = "https://jobs.example.com/role/real"
        svg = "https://www.w3.org/2000/svg"

        async def fake_fetch(url, *, debug=False):
            return ("Visible JD from playwright fetch with enough length!!", url)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        html = (
            f'<a href="{good}">Apply</a>'
            f'<a href="{svg}">SVG</a>'
        )
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=False)
        assert out["mode"] == "links"
        assert len(out["created"]) == 1
        row = db.get_job(out["created"][0]["astral_job_id"])
        assert row["job_link"] == good
        # Silent drop at candidate collection — no skipped row for excluded href.
        assert all(s.get("url") != svg for s in out["skipped"])

    def test_non_job_visible_text_skips_create(
        self, sqlite_in_memory, monkeypatch
    ) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1132-nj"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "N"})
        url = "https://jobs.example.com/role/looks-ok"

        async def fake_fetch(u, *, debug=False):
            # Long enough for min_jd_chars but clearly an SVG/spec page.
            body = ("SVG namespace docs. " * 5) + "www.w3.org/2000/svg"
            return (body, u)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(
            cid, f'<a href="{url}">x</a>', debug=False
        )
        assert out["mode"] == "links"
        assert out["created"] == []
        assert out["skipped"][0]["reason"] == "non_job_page"
        assert out["skipped"][0]["url"] == url

    def test_final_url_excluded_link_skips(
        self, sqlite_in_memory, monkeypatch
    ) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1132-redir"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "R"})
        start = "https://jobs.example.com/role/redirect"
        final = "https://www.w3.org/2000/svg"

        async def fake_fetch(u, *, debug=False):
            return ("Visible JD from playwright fetch with enough length!!", final)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(
            cid, f'<a href="{start}">x</a>', debug=False
        )
        assert out["mode"] == "links"
        assert out["created"] == []
        assert out["skipped"][0]["reason"] == "excluded_link"
        assert out["skipped"][0]["url"] == final

    def test_cross_candidate_same_link_still_creates(
        self, sqlite_in_memory, monkeypatch
    ) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1132-mine"
        other = "cand-1132-other"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        db.save_candidate(other, state="NEW_CANDIDATE", candidate_data={"name": "O"})
        link = "https://jobs.example.com/role/shared"
        db.save_company("other-co", state="IMPORTED", candidate_id=other)
        db.save_job("j-other", company="other-co", state="NEW", job_link=link)

        async def fake_fetch(u, *, debug=False):
            return ("Visible JD from playwright fetch with enough length!!", u)

        monkeypatch.setattr(gazer_mod, "_meteorite_fetch_link_visible_text", fake_fetch)
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(
            cid, f'<a href="{link}">x</a>', debug=False
        )
        assert out["mode"] == "links"
        assert len(out["created"]) == 1
        row = db.get_job(out["created"][0]["astral_job_id"])
        assert row["job_link"] == link



# Branches: short stored company_job_id must not skip Create (AST-1146 UAT).
class TestAst1146CreateSkipShortCompanyJobId:
    def test_body_mode_short_id_does_not_skip_create(self, sqlite_in_memory) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1146-short"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        db.save_company("acme", state="IMPORTED", candidate_id=cid)
        # Junk short id previously false-matched JD text containing "29".
        db.save_job("j-junk", company="acme", state="NEW", company_job_id="29")
        html = (
            "<p>"
            + ("Lead Systems Analyst role description with enough chars. " * 3)
            + " band 29 "
            + "</p>"
        )
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=False)
        assert out["mode"] == "body"
        assert len(out["created"]) == 1
        assert out["skipped"] == []

    def test_body_mode_long_id_still_skips(self, sqlite_in_memory) -> None:
        from src.core import gazer as gazer_mod

        db = sqlite_in_memory
        cid = "cand-1146-long"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        db.save_company("acme", state="IMPORTED", candidate_id=cid)
        db.save_job("j-known", company="acme", state="NEW", company_job_id="KNOWN-EXT-77")
        html = "<p>" + ("x" * 20) + " KNOWN-EXT-77 " + ("y" * 20) + "</p>"
        out = gazer_mod.ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=False)
        assert out["mode"] == "body"
        assert out["created"] == []
        assert out["skipped"][0]["reason"] == "known_company_job_id"
        assert out["skipped"][0]["matched_company_job_id"] == "KNOWN-EXT-77"

# Branches: url validate; scheme fix; connectivity; scrape payload; cookie/bot→blocked; Style D; no job create.
class TestAst1516ContactTaskGazerScrape:
    """AST-1516: contact_task_gazer_scrape — Playwright scrape + page_status (no job create)."""

    def test_contact_page_status_collapses_cookie_and_bot(self) -> None:
        assert gazer_mod._CONTACT_PAGE_STATUS["cookie"] == "blocked"
        assert gazer_mod._CONTACT_PAGE_STATUS["bot"] == "blocked"
        assert gazer_mod._CONTACT_PAGE_STATUS["ok"] == "ok"
        assert gazer_mod._CONTACT_PAGE_STATUS["closed"] == "closed"
        assert gazer_mod._CONTACT_PAGE_STATUS["missing"] == "missing"

    @pytest.mark.asyncio
    async def test_url_required_when_param_blank(self) -> None:
        out = await gazer_mod.contact_task_gazer_scrape("c1", "  ", debug=False)
        assert out == {"ok": False, "error": "url_required", "task_key": "gazer_scrape"}

    @pytest.mark.asyncio
    async def test_no_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=False))
        out = await gazer_mod.contact_task_gazer_scrape(
            "c1", "https://jobs.example/jd", debug=False
        )
        assert out["ok"] is False
        assert out["error"] == "no_connectivity"
        assert out["url"] == "https://jobs.example/jd"

    @pytest.mark.asyncio
    async def test_scheme_fix_and_success_payload(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        page = AsyncMock()
        context = AsyncMock()

        @asynccontextmanager
        async def _browser():
            yield context

        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "create_browser_context", _browser)
        monkeypatch.setattr(gazer_mod, "get_page", AsyncMock(return_value=page))
        monkeypatch.setattr(
            gazer_mod,
            "extract_page_scrape_contract",
            AsyncMock(
                return_value={
                    "visible_text": _OK_JD,
                    "nav_urls": ["https://jobs.example/a", "https://jobs.example/b"],
                    "final_url": "https://jobs.example/jd",
                }
            ),
        )
        close = AsyncMock()
        monkeypatch.setattr(gazer_mod, "close_page", close)
        save = MagicMock()
        transition = MagicMock()
        create = MagicMock()
        monkeypatch.setattr(gazer_mod, "save_job_data", save)
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "create_meteorite_job", create)

        out = await gazer_mod.contact_task_gazer_scrape(
            "cand-1", "jobs.example/jd", debug=False
        )
        assert out["ok"] is True
        assert out["task_key"] == "gazer_scrape"
        assert out["url"] == "https://jobs.example/jd"
        assert out["final_url"] == "https://jobs.example/jd"
        assert out["page_status"] == "ok"
        assert out["classification"] == "ok"
        assert out["links"] == ["https://jobs.example/a", "https://jobs.example/b"]
        assert out["astral_candidate_id"] == "cand-1"
        assert "role summary" in out["visible_text"]
        close.assert_awaited_once_with(page)
        save.assert_not_called()
        transition.assert_not_called()
        create.assert_not_called()

    @pytest.mark.asyncio
    async def test_cookie_and_bot_map_to_blocked(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        page = AsyncMock()

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "create_browser_context", _browser)
        monkeypatch.setattr(gazer_mod, "get_page", AsyncMock(return_value=page))
        monkeypatch.setattr(gazer_mod, "close_page", AsyncMock())

        async def _run(label: str) -> str:
            monkeypatch.setattr(
                gazer_mod,
                "extract_page_scrape_contract",
                AsyncMock(
                    return_value={"visible_text": "x", "nav_urls": [], "final_url": "u"}
                ),
            )
            monkeypatch.setattr(gazer_mod, "_classify_jd", MagicMock(return_value=label))
            out = await gazer_mod.contact_task_gazer_scrape("c1", "https://x", debug=False)
            return out["page_status"]

        assert await _run("cookie") == "blocked"
        assert await _run("bot") == "blocked"

    @pytest.mark.asyncio
    async def test_scrape_exception_returns_error_dict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        @asynccontextmanager
        async def _browser():
            raise RuntimeError("browser boom")
            yield  # pragma: no cover

        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "create_browser_context", _browser)
        out = await gazer_mod.contact_task_gazer_scrape(
            "c1", "https://jobs.example/jd", debug=False
        )
        assert out["ok"] is False
        assert out["task_key"] == "gazer_scrape"
        assert "browser boom" in out["error"]

    @pytest.mark.asyncio
    async def test_debug_style_d_on_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        page = AsyncMock()

        @asynccontextmanager
        async def _browser():
            yield AsyncMock()

        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "create_browser_context", _browser)
        monkeypatch.setattr(gazer_mod, "get_page", AsyncMock(return_value=page))
        monkeypatch.setattr(gazer_mod, "close_page", AsyncMock())
        monkeypatch.setattr(
            gazer_mod,
            "extract_page_scrape_contract",
            AsyncMock(
                return_value={
                    "visible_text": _OK_JD,
                    "nav_urls": ["https://a"],
                    "final_url": "https://jobs.example/jd",
                }
            ),
        )
        log = MagicMock()
        monkeypatch.setattr(gazer_mod, "get_logger", lambda _n: log)
        out = await gazer_mod.contact_task_gazer_scrape(
            "c1", "https://jobs.example/jd", debug=True
        )
        assert out["ok"] is True
        log.set_debug_flag.assert_called_with(True)
        kwa = log.debug_index.call_args.kwargs
        assert kwa["func"] == "gazer.contact_task_gazer_scrape"
        assert kwa["outcome"] == "ok page_status=ok"
        details = " ".join(c.args[0] for c in log.debug_detail.call_args_list if c.args)
        assert "visible_chars=" in details
        assert "links_count=1" in details


# AST-2086 AC4: fetch_website / fetch_job_pages / fetch_culture_pages run the shared is_bot_wall
# detector — a bot wall lands on BOT_BLOCKED_<TASK_KEY>; plain unreadable stays ERROR_<TASK_KEY>_UNREADABLE.
class TestAst2086GazerBotWallSplit:
    _JDC = gazer_mod.TRACKER_CONFIG["jd_classifier"]
    _BOT = "Welcome. " + " ".join(_JDC["bot_signals"][: _JDC.get("bot_threshold", 2)])

    def test_bot_text_trips_shared_detector(self) -> None:
        # Guard: the fixture text must actually be a bot wall, or every test below proves nothing.
        assert gazer_mod.is_bot_wall(self._BOT)
        assert not gazer_mod.is_bot_wall("open roles at acme")

    def test_fetch_website_fail_destination_bot_first(self) -> None:
        cfg = gazer_mod.GAZER_CONFIG["fetch_website"]
        dest = gazer_mod._fetch_website_fail_destination
        assert dest("WEBSITE_FOUND", "", cfg, self._BOT) == "BOT_BLOCKED_FETCH_WEBSITE"
        # Bot wall wins over the infra retry ladder and over a retry re-fail.
        assert dest("WEBSITE_FOUND", "[playwright:channel_error] boom", cfg, self._BOT) == "BOT_BLOCKED_FETCH_WEBSITE"
        assert dest("WEBSITE_FOUND_RETRY", "site unreadable", cfg, self._BOT) == "BOT_BLOCKED_FETCH_WEBSITE"
        # No error and no wall → success path (None); plain unreadable → the _UNREADABLE failure.
        assert dest("WEBSITE_FOUND", "", cfg, "acme homepage") is None
        assert dest("WEBSITE_FOUND", "site unreadable", cfg, "") == "ERROR_FETCH_WEBSITE_UNREADABLE"

    @pytest.mark.asyncio
    async def test_fetch_website_bot_wall_is_bot_blocked_not_homepage(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        _mock_batch_browser_session(monkeypatch)
        transition, save = MagicMock(), MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_company_state", transition)
        monkeypatch.setattr(gazer_mod, "save_company_data", save)
        monkeypatch.setattr(
            gazer_mod, "scrape_company_homepage_content",
            AsyncMock(return_value={"company_website": "https://acme.com", "visible_text": self._BOT, "error": None}),
        )
        out = await gazer_mod.fetch_website_batch("b-2086", [{"short_name": "acme", "company_website": "https://acme.com"}])
        assert out == {"passed": 0, "failed": 1, "errors": 0, "skipped": 0, "total": 1}
        transition.assert_called_once_with("acme", "BOT_BLOCKED_FETCH_WEBSITE")
        # Only the notes write — the wall text is never persisted as homepage_text.
        notes_key = gazer_mod.ROSTER_CONFIG["company_data_keys"]["prefilter_company_notes"]
        save.assert_called_once_with("acme", {notes_key: "bot wall"})

    @pytest.mark.asyncio
    async def test_fetch_job_pages_all_walled_is_bot_blocked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        out, transition, saved, _scrape, _log = await TestFetchJobPagesBatch._run_pjl(
            monkeypatch,
            {"possible_joblist_links": ["acme.com/careers", "acme.com/jobs"]},
            {
                "acme.com/careers": {"url": "https://acme.com/careers", "visible_text": self._BOT, "page_links": []},
                "acme.com/jobs": {"url": "https://acme.com/jobs", "visible_text": self._BOT, "page_links": []},
            },
        )
        assert out == {"passed": 0, "failed": 1, "total": 1}
        transition.assert_called_once_with("acme", "BOT_BLOCKED_FETCH_JOB_PAGES")
        # A wall is not page content: nothing merged into the capture.
        assert saved["pjl_scrape_pages"] == []

    @pytest.mark.asyncio
    async def test_fetch_job_pages_walled_with_prior_capture_still_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        prior = {"url": "https://acme.com/careers", "visible_text": "OLD BOARD"}
        out, transition, saved, _scrape, _log = await TestFetchJobPagesBatch._run_pjl(
            monkeypatch,
            {"possible_joblist_links": ["acme.com/careers"], "pjl_scrape_pages": [prior]},
            {"acme.com/careers": {"url": "https://acme.com/careers", "visible_text": self._BOT, "page_links": []}},
        )
        assert out == {"passed": 1, "failed": 0, "total": 1}
        transition.assert_called_once_with("acme", "PJL_READY")
        assert saved["pjl_scrape_pages"] == [prior]

    @staticmethod
    def _culture_env(monkeypatch: pytest.MonkeyPatch, company: Dict[str, Any], fetched: Any) -> MagicMock:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        transition = MagicMock()
        monkeypatch.setattr(gazer_mod, "transition_job_state", transition)
        monkeypatch.setattr(gazer_mod, "get_company", MagicMock(return_value=company))
        monkeypatch.setattr(gazer_mod, "get_company_data", AsyncMock(return_value=fetched))
        return transition

    def test_website_content_bot_walled_shapes(self) -> None:
        walled = gazer_mod._website_content_bot_walled
        assert walled([{"url": "a", "content": self._BOT}, {"url": "b", "content": self._BOT}])
        assert not walled([{"url": "a", "content": self._BOT}, {"url": "b", "content": "our values"}])
        assert walled([{"url": "a", "content": self._BOT}, "not-a-page"])  # non-dict entries are ignored
        assert walled(self._BOT)  # legacy string capture
        assert not walled("")
        assert not walled([])
        assert not walled(None)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("debug", [False, True])
    async def test_fetch_culture_pages_fresh_all_walled_is_bot_blocked(self, monkeypatch: pytest.MonkeyPatch, debug: bool) -> None:
        company = {"short_name": "acme", "company_data": {"culture_links_to_explore": ["https://acme.com/c"]}}
        transition = self._culture_env(monkeypatch, company, [{"url": "https://acme.com/c", "content": self._BOT}])
        out = await gazer_mod.fetch_culture_pages_batch("b-2086", [{"astral_job_id": "j-wall", "company": "acme"}], debug=debug)
        assert out == {"passed": 0, "failed": 1, "total": 1}
        transition.assert_called_once_with(["j-wall"], "BOT_BLOCKED_FETCH_CULTURE_PAGES")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("debug", [False, True])
    async def test_fetch_culture_pages_cached_all_walled_is_bot_blocked(self, monkeypatch: pytest.MonkeyPatch, debug: bool) -> None:
        company = {"short_name": "acme", "company_data": {"website_content": [{"url": "https://acme.com/c", "content": self._BOT}]}}
        transition = self._culture_env(monkeypatch, company, None)
        out = await gazer_mod.fetch_culture_pages_batch("b-2086", [{"astral_job_id": "j-cache", "company": "acme"}], debug=debug)
        assert out == {"passed": 0, "failed": 1, "total": 1}
        transition.assert_called_once_with(["j-cache"], "BOT_BLOCKED_FETCH_CULTURE_PAGES")

    @pytest.mark.asyncio
    async def test_fetch_culture_pages_one_usable_page_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Only an all-walled capture is bot-blocked; one gradeable page is enough to pass.
        company = {"short_name": "acme", "company_data": {"culture_links_to_explore": ["https://acme.com/c"]}}
        fetched = [{"url": "https://acme.com/c", "content": self._BOT}, {"url": "https://acme.com/v", "content": "our values"}]
        transition = self._culture_env(monkeypatch, company, fetched)
        out = await gazer_mod.fetch_culture_pages_batch("b-2086", [{"astral_job_id": "j-mixed", "company": "acme"}])
        assert out == {"passed": 1, "failed": 0, "total": 1}
        transition.assert_called_once_with(["j-mixed"], "CULTURE_READY")
