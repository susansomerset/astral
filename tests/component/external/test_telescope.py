"""Component tests for src/external/telescope.py (AST-391 + AST-1726 drop-in)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.external import telescope as pw_mod


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
            "initial_html": '<div data-hubspot>jobs</div>',
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
        out = pw_mod.recommend_routing(
            {"canonical_job_url": "https://jobs.example.com"}, "https://corp.example.com"
        )
        assert out["route_to_url"] == "https://jobs.example.com"
        assert out["fallback"] is False

    def test_routes_to_iframe_when_present(self) -> None:
        out = pw_mod.recommend_routing(
            {"iframe_urls": ["https://frame.example.com"]}, "https://corp.example.com"
        )
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


# Branches: page URL helper; frame URLs empty on Telescope client (no live frames).
class TestPageUrlHelpers:
    def test_get_page_url_prefers_final_url(self) -> None:
        page = pw_mod.PageHandle(url="https://example.com/jobs")
        page._final_url = "https://example.com/final"
        assert pw_mod.get_page_url(page) == "https://example.com/final"
        assert pw_mod.get_frame_urls(page) == []

    def test_extract_tags_handles_nested_and_malformed_html(self) -> None:
        html = '<div class="posting"><div class="posting">inner</div></div><div class="posting">broken'
        chunks = pw_mod.extract_tags_in_order(html, '<div class="posting"')
        assert chunks

    def test_extract_raw_job_listings_rejects_out_of_range_container(self) -> None:
        dom = '<div class="jobs"><a class="posting">A</a></div>'
        assert pw_mod.extract_raw_job_listings(dom, "div.jobs", "a.posting", 2) == []


# Branches: production log signatures → stable failure classes (AST-853 + AST-1726 HTTP).
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

    def test_telescope_timeout_is_infra(self) -> None:
        fc = pw_mod.classify_playwright_failure(httpx.TimeoutException("telescope timeout"))
        assert fc == "telescope_timeout"
        assert pw_mod.is_playwright_infra_failure(fc)

    def test_connectivity_failure(self) -> None:
        fc = pw_mod.classify_playwright_failure(RuntimeError("connection refused"))
        assert fc == "connectivity_failure"
        assert pw_mod.is_playwright_infra_failure(fc)


class TestPlaywrightInfraError:
    def test_message_and_attributes(self) -> None:
        err = pw_mod.PlaywrightInfraError("context_closed", "browser dead")
        assert err.failure_class == "context_closed"
        assert err.detail == "browser dead"
        assert str(err) == "[context_closed] browser dead"


# Branches: get_page returns PageHandle (no Firefox); batch session wiring.
class TestGetPageDropIn:
    @pytest.mark.asyncio
    async def test_get_page_from_batch_session(self) -> None:
        session = pw_mod.BatchBrowserSession()
        page = await pw_mod.get_page(batch_session=session, url="https://example.com")
        assert isinstance(page, pw_mod.PageHandle)
        assert page.url == "https://example.com"
        await session.aclose()

    @pytest.mark.asyncio
    async def test_get_page_requires_context_or_batch(self) -> None:
        with pytest.raises(ValueError, match="requires context or batch_session"):
            await pw_mod.get_page(url="https://example.com")


# Branches: HTTP pool failover / timeout → PlaywrightInfraError (AST-1726).
class TestTelescopePoolHttp:
    @pytest.mark.asyncio
    async def test_5xx_retries_other_node_then_ok(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setitem(
            pw_mod.TELESCOPE_CONFIG,
            "base_urls",
            ["http://node-a.test", "http://node-b.test"],
        )
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "max_node_attempts", 2)
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "retry_other_node", True)
        monkeypatch.setenv("TELESCOPE_BEARER_TOKEN", "tok")
        monkeypatch.setattr(pw_mod, "require_controlled_external_io", lambda *_a, **_k: None)

        calls: list[str] = []

        class _Resp:
            def __init__(self, status: int, body: dict | None = None) -> None:
                self.status_code = status
                self._body = body or {}

            def json(self) -> dict:
                return self._body

        async def fake_request(method, url, headers=None, json=None):
            calls.append(url)
            if "node-a" in url:
                return _Resp(502)
            return _Resp(200, {"ok": True})

        client = MagicMock()
        client.request = AsyncMock(side_effect=fake_request)
        pool = pw_mod._TelescopePool()
        pool._client = client
        monkeypatch.setattr(pw_mod, "_pool", pool)

        resp = await pool.request("GET", "/healthz")
        assert resp.status_code == 200
        assert any("node-a" in u for u in calls)
        assert any("node-b" in u for u in calls)

    @pytest.mark.asyncio
    async def test_timeout_raises_telescope_timeout(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "base_urls", ["http://solo.test"])
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "max_node_attempts", 1)
        monkeypatch.setenv("TELESCOPE_BEARER_TOKEN", "tok")
        monkeypatch.setattr(pw_mod, "require_controlled_external_io", lambda *_a, **_k: None)

        client = MagicMock()
        client.request = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
        pool = pw_mod._TelescopePool()
        pool._client = client

        with pytest.raises(pw_mod.PlaywrightInfraError) as exc_info:
            await pool.request("GET", "/healthz")
        assert exc_info.value.failure_class == "telescope_timeout"

    @pytest.mark.asyncio
    async def test_missing_bearer_raises_connectivity(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "base_urls", ["http://solo.test"])
        monkeypatch.delenv("TELESCOPE_BEARER_TOKEN", raising=False)
        pool = pw_mod._TelescopePool()
        with pytest.raises(pw_mod.PlaywrightInfraError) as exc_info:
            await pool.request("GET", "/healthz")
        assert exc_info.value.failure_class == "connectivity_failure"


# Branches: cull_html_default on extract_page_dom (AST-1726 / parent AC4).
class TestCullHtmlDefault:
    @pytest.mark.asyncio
    async def test_extract_page_dom_culls_when_default_on(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "cull_html_default", True)
        page = pw_mod.PageHandle(url="https://example.com")
        monkeypatch.setattr(
            pw_mod, "_ensure_html", AsyncMock(return_value="<html><script>x</script><body>hi</body></html>")
        )
        culled = MagicMock(return_value="<body>hi</body>")
        monkeypatch.setattr(pw_mod, "_cull_html", culled)
        out = await pw_mod.extract_page_dom(page)
        assert out == "<body>hi</body>"
        culled.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_page_dom_skips_cull_when_default_off(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "cull_html_default", False)
        raw = "<html><body>raw</body></html>"
        page = pw_mod.PageHandle(url="https://example.com")
        monkeypatch.setattr(pw_mod, "_ensure_html", AsyncMock(return_value=raw))
        culled = MagicMock()
        monkeypatch.setattr(pw_mod, "_cull_html", culled)
        out = await pw_mod.extract_page_dom(page)
        assert out == raw
        culled.assert_not_called()


class TestAst1745CullPreservesRootSvgLogo:
    """AST-1745 bug-repro — class-scoped svg.logo outerHTML must survive _cull_html."""

    def test_cull_html_preserves_root_svg_logo_outerhtml(self) -> None:
        # Susan's exemplar shape: single-root svg.logo fragment from class filter.
        frag = (
            '<svg id="bLogo" role="img" class="logo" viewBox="0 0 24 24" '
            'aria-label="Microsoft Logo Image" fill="none" tabindex="0">'
            '<g class="squares">'
            '<path fill="#f26522" d="M11.4 0H0v11.4h11.4z"></path>'
            '<path fill="#8dc63f" d="M23.9 0H12.5v11.4H24z"></path>'
            "</g></svg>"
        )
        out = pw_mod._cull_html(frag)
        assert out.strip() != "", (
            "AST-1745: _cull_html must not erase a root svg.logo class-scoped fragment"
        )
        assert "<svg" in out.lower(), "AST-1745: root svg element must remain"
        assert "logo" in out
        assert "bLogo" in out or "viewBox" in out

    def test_cull_html_still_strips_nested_svg_under_page_content(self) -> None:
        # Whole-page / job HTML: nested decorative svgs stay culled.
        html = (
            "<div class=\"job\"><p>Acme role</p>"
            '<svg class="icon" viewBox="0 0 8 8"><circle r="4"></circle></svg>'
            "</div>"
        )
        out = pw_mod._cull_html(html)
        assert "Acme role" in out
        assert "<svg" not in out.lower(), (
            "AST-1745: nested svg under non-svg roots must still be culled"
        )


class TestAst1750PostTelescopeDebugDump:
    """AST-1750 bug-repro — _post_telescope debug dumps full request body + response."""

    @pytest.mark.asyncio
    async def test_post_telescope_debug_emits_request_body_and_full_response(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        from src.utils.logging import log_debug

        payload = {
            "final_url": "https://example.com/final",
            "text": "Sorry, this job is no longer available.",
            "scrape_meta": {"bot_blocked": False, "content_chars": 40},
        }

        async def fake_request(method, path, json_body=None, **_kwargs):
            resp = MagicMock()
            resp.status_code = 200
            resp.json = MagicMock(return_value=payload)
            resp.text = '{"final_url":"https://example.com/final"}'
            return resp

        monkeypatch.setattr(pw_mod._pool, "request", fake_request)
        token = log_debug.set(True)
        try:
            with caplog.at_level(logging.DEBUG, logger="src.external.telescope"):
                out = await pw_mod._post_telescope(
                    "https://example.com/job",
                    fields=["text"],
                    expand=False,
                )
        finally:
            log_debug.reset(token)

        assert out["final_url"] == payload["final_url"]
        msgs = "\n".join(r.getMessage() for r in caplog.records)
        assert "https://example.com/job" in msgs or "url" in msgs.lower(), (
            "AST-1750: debug must dump request parameters including url"
        )
        assert "expand" in msgs or "False" in msgs, (
            "AST-1750: debug callee-in must include request body fields"
        )
        assert "no longer available" in msgs or "final_url" in msgs, (
            "AST-1750: debug callee-out must dump full response (no truncation)"
        )
        assert any(
            "Calling" in r.getMessage() or "body" in r.getMessage().lower()
            or "request" in r.getMessage().lower()
            for r in caplog.records
        ), "AST-1750: missing ungated logger.debug callee-in before _pool.request"
        assert any(
            "Response" in r.getMessage() or "final_url" in r.getMessage()
            for r in caplog.records
        ), "AST-1750: missing ungated logger.debug callee-out with full JSON"


class TestExtractPageScrapeContract:
    @pytest.mark.asyncio
    async def test_homepage_contract_one_telescope_post(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Homepage text + nav links must share one page load (fields text+links)."""
        calls = {"n": 0}

        async def fake_post(url, *, fields, **kwargs):
            calls["n"] += 1
            assert fields == ["text", "links"]
            return {
                "final_url": url,
                "text": "hello world",
                "links": [{"href": "https://example.com/about", "text": "About"}],
            }

        monkeypatch.setattr(pw_mod, "_post_telescope", fake_post)
        page = pw_mod.PageHandle(url="https://example.com")
        out = await pw_mod.extract_page_scrape_contract(page)
        assert calls["n"] == 1
        assert out["visible_text"] == "hello world"
        assert "https://example.com/about" in out["nav_urls"]


# Branches: no platform playwright module (AST-1726 AC6).
class TestPlaywrightModuleGone:
    def test_src_external_playwright_import_fails(self) -> None:
        with pytest.raises(ModuleNotFoundError):
            __import__("src.external.playwright")
