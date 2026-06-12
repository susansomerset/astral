"""Component tests for src/external/playwright.py (AST-391)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

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


# AST-418/458: board_search deeplink navigates with URL-encoded params.
class TestBoardSearchDeeplink:
    @pytest.mark.asyncio
    async def test_appends_question_mark_when_no_query(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(pw_mod, "_try_dismiss_cookie_banner", AsyncMock())
        dom = "<html><body>x</body></html>"
        page = AsyncMock()
        page.content = AsyncMock(return_value=dom)
        html, meta = await pw_mod.board_search_deeplink(
            page,
            "https://example.com/jobs",
            {"q": "rust", "skip_empty": "", "skip_none": None},
        )
        page.goto.assert_awaited_once()
        called_url = page.goto.await_args.args[0]
        assert called_url.startswith("https://example.com/jobs?q=rust") or "?q=rust" in called_url
        assert meta["url"] == called_url and meta["mode"] == "deep_link"
        assert html == dom

    @pytest.mark.asyncio
    async def test_appends_ampersand_when_query_present(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(pw_mod, "_try_dismiss_cookie_banner", AsyncMock())
        page = AsyncMock()
        page.content = AsyncMock(return_value="<html></html>")
        html, meta = await pw_mod.board_search_deeplink(
            page,
            "https://example.com/list?tag=corp",
            {"q": "go"},
        )
        url = meta["url"]
        assert "tag=corp" in url and "&q=go" in url

    @pytest.mark.asyncio
    async def test_empty_params_keeps_trimmed_entry_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(pw_mod, "_try_dismiss_cookie_banner", AsyncMock())
        page = AsyncMock()
        page.content = AsyncMock(return_value="<html/>")
        _html, meta = await pw_mod.board_search_deeplink(
            page,
            "  https://corp.example/board  ",
            {"empty_str": "", "none_val": None},
        )
        assert meta["mode"] == "deep_link"
        assert meta["url"] == "https://corp.example/board"
        goto_url = page.goto.await_args.args[0]
        assert goto_url == "https://corp.example/board"
