"""Component tests for src/external/playwright.py (AST-391)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.external import playwright as pw_mod


# Branches: empty URL passthrough; scheme/path/query normalization.
class TestNormalizeUrl:
    def test_normalizes_scheme_host_and_trailing_slash(self) -> None:
        assert pw_mod.normalize_url("HTTPS://Example.COM/jobs/") == "https://example.com/jobs"

    def test_preserves_query_and_fragment(self) -> None:
        assert pw_mod.normalize_url("https://example.com/jobs/?q=1#top") == "https://example.com/jobs?q=1#top"

    def test_empty_url_returns_empty(self) -> None:
        assert pw_mod.normalize_url("") == ""


# Branches: network/frame/html vendor fingerprints and canonical URLs.
class TestDetectVendor:
    def test_detects_greenhouse_from_network_request(self) -> None:
        artifacts = {
            "request_urls": ["https://boards.greenhouse.io/acme/jobs"],
            "frame_urls": [],
            "initial_html": "",
        }
        out = pw_mod.detect_vendor(artifacts)
        assert out["vendor"] == "greenhouse"
        assert out["canonical_job_url"] == "https://boards.greenhouse.io/acme"

    def test_detects_hubspot_frame_and_html_markers(self) -> None:
        artifacts = {
            "request_urls": [],
            "frame_urls": ["https://hs-sites.example/widget"],
            "initial_html": "<div data-hubspot>jobs</div>",
        }
        out = pw_mod.detect_vendor(artifacts)
        assert out["vendor"] == "hubspot"
        assert out["iframe_urls"]

    def test_detects_lever_from_html_and_frames(self) -> None:
        artifacts = {
            "request_urls": [],
            "frame_urls": ["https://jobs.lever.co/acme"],
            "initial_html": "<script>lever.co board</script>",
        }
        out = pw_mod.detect_vendor(artifacts)
        assert out["vendor"] == "lever"

    def test_detects_workday_request(self) -> None:
        artifacts = {
            "request_urls": ["https://acme.wd5.myworkdayjobs.com/en-US/jobs"],
            "frame_urls": [],
            "initial_html": "",
        }
        out = pw_mod.detect_vendor(artifacts)
        assert out["vendor"] == "workday"


# Branches: canonical URL; iframe route; fallback.
class TestRecommendRouting:
    def test_prefers_canonical_job_url(self) -> None:
        out = pw_mod.recommend_routing({"canonical_job_url": "https://jobs.example.com"}, "https://corp.example.com")
        assert out["route_to_url"] == "https://jobs.example.com"
        assert out["fallback"] is False

    def test_routes_to_iframe_when_present(self) -> None:
        out = pw_mod.recommend_routing({"iframe_urls": ["https://frame.example.com"]}, "https://corp.example.com")
        assert out["route_to_iframe"] == "https://frame.example.com"

    def test_falls_back_to_current_page(self) -> None:
        out = pw_mod.recommend_routing({}, "https://corp.example.com")
        assert out["fallback"] is True


# Branches: anchor text collection and href map.
class TestParseHtmlForInternalClickables:
    def test_collects_image_alt_when_link_text_missing(self) -> None:
        html = '<a href="/jobs"><img alt="Open Jobs" src="/x.png"></a>'
        texts, hrefs = pw_mod._parse_html_for_internal_clickables(html)
        assert texts == ["Open Jobs"]
        assert hrefs["open jobs"] == "/jobs"

    def test_skips_external_and_protocol_relative_links(self) -> None:
        html = '<a href="https://example.com">Ext</a><a href="//cdn.example.com">Proto</a>'
        texts, _ = pw_mod._parse_html_for_internal_clickables(html)
        assert texts == []


# Branches: class extraction; incomplete class attribute; tag-only fallback.
class TestHtmlTagToCssSelector:
    def test_converts_classed_tag(self) -> None:
        assert pw_mod._html_tag_to_css_selector('<div class="vacancies__item">') == "div.vacancies__item"

    def test_handles_incomplete_class_attribute(self) -> None:
        assert pw_mod._html_tag_to_css_selector('<a class="link-module') == "a.link-module"

    def test_returns_original_when_unparseable(self) -> None:
        assert pw_mod._html_tag_to_css_selector("not-a-tag") == "not-a-tag"


# Branches: nested tag extraction and malformed openings.
class TestExtractTagsInOrder:
    def test_extracts_matching_chunks(self) -> None:
        html = '<div class="posting">one</div><div class="posting">two</div>'
        chunks = pw_mod.extract_tags_in_order(html, '<div class="posting"')
        assert len(chunks) == 2

    def test_returns_empty_for_blank_pattern(self) -> None:
        assert pw_mod.extract_tags_in_order("<div></div>", "   ") == []


# Branches: missing selectors; invalid CSS; layered job_tag validation.
class TestExtractRawJobListings:
    def test_extracts_outer_elements_matching_layers(self) -> None:
        dom = '<div class="jobs"><a class="posting">A</a><a class="posting">B</a></div>'
        out = pw_mod.extract_raw_job_listings(dom, "div.jobs", "a.posting", 0)
        assert len(out) == 2

    def test_returns_empty_for_missing_container_or_bad_selector(self) -> None:
        assert pw_mod.extract_raw_job_listings("<div></div>", "", "a", 0) == []
        assert pw_mod.extract_raw_job_listings("<div></div>", "div", "[", 0) == []


# Branches: page/frame URL helpers.
class TestPageUrlHelpers:
    def test_get_page_url_and_frame_urls(self) -> None:
        page = SimpleNamespace(
            url="https://example.com/jobs",
            frames=[
                SimpleNamespace(url="about:blank"),
                SimpleNamespace(url="https://example.com/jobs"),
                SimpleNamespace(url="https://frame.example.com"),
            ],
        )
        assert pw_mod.get_page_url(page) == "https://example.com/jobs"
        assert pw_mod.get_frame_urls(page) == ["https://frame.example.com"]

    def test_extract_tags_handles_nested_and_malformed_html(self) -> None:
        html = '<div class="posting"><div class="posting">inner</div></div><div class="posting">broken'
        chunks = pw_mod.extract_tags_in_order(html, '<div class="posting"')
        assert chunks

    def test_extract_raw_job_listings_rejects_out_of_range_container(self) -> None:
        dom = '<div class="jobs"><a class="posting">A</a></div>'
        assert pw_mod.extract_raw_job_listings(dom, "div.jobs", "a.posting", 2) == []


# Branches: production log signatures → stable failure classes (AST-853).
class TestClassifyPlaywrightFailure:
    def test_channel_error_from_message(self) -> None:
        exc = RuntimeError("Exiting due to channel error")
        assert pw_mod.classify_playwright_failure(exc) == "channel_error"

    def test_context_closed_variants(self) -> None:
        assert pw_mod.classify_playwright_failure(
            RuntimeError("Target page, context or browser has been closed"),
        ) == "context_closed"
        assert pw_mod.classify_playwright_failure(RuntimeError("browser has been closed")) == "context_closed"

    def test_launch_timeout_and_failure(self) -> None:
        assert pw_mod.classify_playwright_failure(
            TimeoutError("firefox.launch timeout exceeded"),
        ) == "launch_timeout"
        assert pw_mod.classify_playwright_failure(
            RuntimeError("could not launch firefox"),
        ) == "launch_failure"

    def test_navigation_timeout_not_infra(self) -> None:
        fc = pw_mod.classify_playwright_failure(TimeoutError("page.goto timeout"))
        assert fc == "navigation_timeout"
        assert not pw_mod.is_playwright_infra_failure(fc)


class TestPlaywrightInfraError:
    def test_message_and_attributes(self) -> None:
        err = pw_mod.PlaywrightInfraError("context_closed", "browser dead")
        assert err.failure_class == "context_closed"
        assert err.detail == "browser dead"
        assert str(err) == "[context_closed] browser dead"


# Branches: batch session recovery on infra new_page failure (AST-853).
class TestGetPageBatchRecovery:
    @pytest.mark.asyncio
    async def test_recovers_once_on_context_closed_then_succeeds(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls = {"new_page": 0}
        page = MagicMock()
        page.goto = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        page.close = AsyncMock()
        page.wait_for_load_state = AsyncMock()

        ctx = MagicMock()

        async def _new_page() -> MagicMock:
            calls["new_page"] += 1
            if calls["new_page"] == 1:
                raise RuntimeError("Target page, context or browser has been closed")
            return page

        ctx.new_page = AsyncMock(side_effect=_new_page)

        session = MagicMock()
        session.ensure_context = AsyncMock(return_value=ctx)
        session.recover = AsyncMock()
        monkeypatch.setattr(pw_mod, "_try_dismiss_cookie_banner", AsyncMock(return_value=False))

        result = await pw_mod.get_page(batch_session=session, url="https://example.com")
        assert result is page
        assert calls["new_page"] == 2
        session.recover.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_raises_playwright_infra_error_when_recovery_exhausted(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        ctx = MagicMock()
        ctx.new_page = AsyncMock(
            side_effect=RuntimeError("Target page, context or browser has been closed"),
        )
        session = MagicMock()
        session.ensure_context = AsyncMock(return_value=ctx)
        session.recover = AsyncMock()
        monkeypatch.setattr(pw_mod, "_try_dismiss_cookie_banner", AsyncMock(return_value=False))
        monkeypatch.setitem(pw_mod.PLAYWRIGHT_CONFIG, "context_recovery_max_attempts", 0)

        with pytest.raises(pw_mod.PlaywrightInfraError) as exc_info:
            await pw_mod.get_page(batch_session=session, url="https://example.com")
        assert exc_info.value.failure_class == "context_closed"

