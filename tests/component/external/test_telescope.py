"""Component tests for src/external/telescope.py (AST-391 + AST-1726 drop-in)."""

from __future__ import annotations

import asyncio
import json
import zlib
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

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
        fc = pw_mod.classify_playwright_failure(asyncio.TimeoutError("telescope timeout"))
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


# Branches: Postgres queue client — enqueue, await, failure mapping, deadline.
class _FakeConn:
    def __init__(self) -> None:
        self.execute = AsyncMock()

    @asynccontextmanager
    async def transaction(self):
        yield


class _FakeDb:
    def __init__(self) -> None:
        self.conn = _FakeConn()
        self.execute = AsyncMock()

    @asynccontextmanager
    async def acquire(self):
        yield self.conn


def _queue_with_fake_db(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pw_mod, "require_controlled_external_io", lambda *_a, **_k: None)
    q = pw_mod._TelescopeQueue()
    db = _FakeDb()

    async def fake_get_db():
        q._ensure_loop()
        q._db = db
        return db

    monkeypatch.setattr(q, "_get_db", fake_get_db)
    return q, db


async def _submit_and_resolve(q, row: dict) -> Any:
    task = asyncio.create_task(q.submit({"url": "https://example.com", "fields": ["text"]}))
    while not q._waiters:
        await asyncio.sleep(0)
    next(iter(q._waiters.values())).set_result(row)
    return await task


class TestTelescopeQueueClient:
    @pytest.mark.asyncio
    async def test_done_returns_decoded_result_and_notifies_worker(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        q, db = _queue_with_fake_db(monkeypatch)
        payload = {"final_url": "https://example.com/", "text": "hi \x00"}
        blob = zlib.compress(json.dumps(payload).encode())
        out = await _submit_and_resolve(q, {"status": "done", "result": blob})
        assert out == payload
        sql = " ".join(str(c.args[0]) for c in db.conn.execute.await_args_list)
        assert "INSERT INTO telescope_job" in sql and "pg_notify" in sql
        assert q._waiters == {}

    @pytest.mark.parametrize(
        "error_class, failure_class",
        [
            ("timeout", "telescope_timeout"),
            ("expired", "telescope_timeout"),
            ("bad_request", "telescope_bad_request"),
            ("scrape_failed", "telescope_job_failed"),
            ("lease_expired", "telescope_job_failed"),
        ],
    )
    @pytest.mark.asyncio
    async def test_failed_job_maps_to_failure_class(
        self, monkeypatch: pytest.MonkeyPatch, error_class: str, failure_class: str,
    ) -> None:
        q, _db = _queue_with_fake_db(monkeypatch)
        row = {"status": "failed", "result": None, "error": "x", "error_class": error_class}
        with pytest.raises(pw_mod.PlaywrightInfraError) as exc_info:
            await _submit_and_resolve(q, row)
        assert exc_info.value.failure_class == failure_class

    @pytest.mark.asyncio
    async def test_deadline_cancels_job_and_raises_timeout(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        q, db = _queue_with_fake_db(monkeypatch)
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "job_deadline_seconds", 0.05)
        with pytest.raises(pw_mod.PlaywrightInfraError) as exc_info:
            await q.submit({"url": "https://example.com", "fields": ["text"]})
        assert exc_info.value.failure_class == "telescope_timeout"
        assert "status = 'cancelled'" in db.execute.await_args.args[0]
        assert q._waiters == {}

    @pytest.mark.asyncio
    async def test_missing_database_url_raises_connectivity(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(pw_mod, "require_controlled_external_io", lambda *_a, **_k: None)
        monkeypatch.delenv("ASTRAL_DATABASE_URL", raising=False)
        with pytest.raises(pw_mod.PlaywrightInfraError) as exc_info:
            await pw_mod._TelescopeQueue().submit({"url": "https://example.com"})
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
    """AST-1750 bug-repro — _post_telescope debug dumps request body + response (truncated)."""

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

        async def fake_submit(body, priority=None):
            return payload

        monkeypatch.setattr(pw_mod._pool, "submit", fake_submit)
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
            "AST-1750: debug callee-out must include response fields"
        )

    @pytest.mark.asyncio
    async def test_post_telescope_debug_truncates_long_response_text(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        from src.utils.logging import DEBUG_STRING_HEAD_CHARS, DEBUG_STRING_TAIL_CHARS, log_debug

        head = "H" * DEBUG_STRING_HEAD_CHARS
        tail = "T" * DEBUG_STRING_TAIL_CHARS
        payload = {
            "final_url": "https://example.com/final",
            "text": head + ("M" * 500) + tail,
            "scrape_meta": {"bot_blocked": False},
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
                await pw_mod._post_telescope(
                    "https://example.com/job",
                    fields=["text"],
                    expand=False,
                )
        finally:
            log_debug.reset(token)

        msgs = "\n".join(r.getMessage() for r in caplog.records)
        assert "chars omitted>" in msgs
        assert "M" not in msgs
        assert "final_url" in msgs
        assert head[:100] in msgs
        assert tail[-100:] in msgs
        assert any(
            "Calling" in r.getMessage() or "body" in r.getMessage().lower()
            or "request" in r.getMessage().lower()
            for r in caplog.records
        ), "AST-1750: missing ungated logger.debug callee-in before _pool.submit"
        assert any(
            "Response" in r.getMessage() or "final_url" in r.getMessage()
            for r in caplog.records
        ), "AST-1750: missing ungated logger.debug callee-out with full JSON"


class TestPostTelescopeDebugFlag:
    """Platform client passes debug in the job request (service scrape_debug events)."""

    @pytest.mark.asyncio
    async def test_post_telescope_debug_false_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.logging import log_debug

        seen: dict = {}

        async def fake_submit(body, priority=None):
            seen["body"] = body
            return {"final_url": "https://example.com", "text": "x"}

        monkeypatch.setattr(pw_mod._pool, "submit", fake_submit)
        token = log_debug.set(False)
        try:
            await pw_mod._post_telescope("https://example.com", fields=["text"])
        finally:
            log_debug.reset(token)

        assert seen["body"]["debug"] is False

    @pytest.mark.asyncio
    async def test_post_telescope_debug_follows_log_debug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.logging import log_debug

        seen: dict = {}

        async def fake_submit(body, priority=None):
            seen["body"] = body
            return {"final_url": "https://example.com", "text": "x"}

        monkeypatch.setattr(pw_mod._pool, "submit", fake_submit)
        token = log_debug.set(True)
        try:
            await pw_mod._post_telescope("https://example.com", fields=["text"])
        finally:
            log_debug.reset(token)

        assert seen["body"]["debug"] is True

    @pytest.mark.asyncio
    async def test_post_telescope_debug_explicit_overrides_log_debug(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.logging import log_debug

        seen: dict = {}

        async def fake_submit(body, priority=None):
            seen["body"] = body
            return {"final_url": "https://example.com", "text": "x"}

        monkeypatch.setattr(pw_mod._pool, "submit", fake_submit)
        token = log_debug.set(True)
        try:
            await pw_mod._post_telescope(
                "https://example.com", fields=["text"], debug=False
            )
        finally:
            log_debug.reset(token)

        assert seen["body"]["debug"] is False


# Branches: no platform playwright module (AST-1726 AC6).
class TestPlaywrightModuleGone:
    def test_src_external_playwright_import_fails(self) -> None:
        with pytest.raises(ModuleNotFoundError):
            __import__("src.external.playwright")


class TestFetchCareersListTextAndDom:
    """parse_job_list scrape: one Telescope job for body text + body html."""

    @pytest.mark.asyncio
    async def test_one_body_scoped_job_for_text_and_html(self, monkeypatch) -> None:
        calls: list[dict] = []

        async def fake_submit(body, priority=None):
            calls.append(body)
            return {
                "final_url": "https://acme.com/careers/",
                "text": ["Engineer", "Designer"],
                "html": ["<body><div class='jobs'>x</div></body>"],
            }

        monkeypatch.setattr(pw_mod._pool, "submit", fake_submit)
        monkeypatch.setattr(pw_mod, "_cull_html", lambda h: f"CULLED:{h}")
        page = pw_mod.PageHandle("https://acme.com/careers", session=pw_mod.BrowserSession())

        text, dom, meta = await pw_mod.fetch_careers_list_text_and_dom(
            page, {"run_load_all_jobs": True}
        )

        assert len(calls) == 1
        assert calls[0]["fields"] == ["text", "html"]
        assert calls[0]["selector"] == "body"
        assert calls[0]["wait_ready"] is True and calls[0]["expand"] is True
        assert text == "Engineer\n\nDesigner"
        assert dom == "CULLED:<body><div class='jobs'>x</div></body>"
        assert meta["ready"] is True and meta["visible_chars"] == len(text)
        assert page.url == "https://acme.com/careers/"

    @pytest.mark.asyncio
    async def test_empty_text_is_not_ready_and_cull_can_be_off(self, monkeypatch) -> None:
        async def fake_submit(body, priority=None):
            return {"text": "", "html": "<body></body>"}

        monkeypatch.setattr(pw_mod._pool, "submit", fake_submit)
        monkeypatch.setitem(pw_mod.TELESCOPE_CONFIG, "cull_html_default", False)
        page = pw_mod.PageHandle("https://acme.com/careers", session=pw_mod.BrowserSession())
        text, dom, meta = await pw_mod.fetch_careers_list_text_and_dom(
            page, {"run_load_all_jobs": False}
        )
        assert (text, dom) == ("", "<body></body>")
        assert meta["outcome"] == "empty" and meta["ready"] is False

    @pytest.mark.asyncio
    async def test_blank_url_skips_telescope(self, monkeypatch) -> None:
        submit = AsyncMock()
        monkeypatch.setattr(pw_mod._pool, "submit", submit)
        page = pw_mod.PageHandle("", session=pw_mod.BrowserSession())
        assert (await pw_mod.fetch_careers_list_text_and_dom(page, {}))[:2] == ("", "")
        submit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_closed_page_raises(self) -> None:
        page = pw_mod.PageHandle("https://acme.com", session=pw_mod.BrowserSession())
        await page.close()
        with pytest.raises(pw_mod.PlaywrightInfraError):
            await pw_mod.fetch_careers_list_text_and_dom(page, {})


class TestTelescopeWake:
    """Serverless Telescope: throttled fire-and-forget GET /wake when no worker is live."""

    def _queue(self, monkeypatch, *, live: int, url: str = "http://telescope.railway.internal:8080/wake"):
        if url:
            monkeypatch.setenv("TELESCOPE_WAKE_URL", url)
        else:
            monkeypatch.delenv("TELESCOPE_WAKE_URL", raising=False)
        q = pw_mod._TelescopeQueue()
        monkeypatch.setattr(q, "_live_workers", AsyncMock(return_value=live))
        ping = AsyncMock()
        monkeypatch.setattr(q, "_ping_wake", ping)
        return q, ping

    @pytest.mark.asyncio
    async def test_pings_once_when_no_worker_then_throttles(self, monkeypatch) -> None:
        q, ping = self._queue(monkeypatch, live=0)
        for _ in range(50):
            await q._maybe_wake(MagicMock())
        await asyncio.sleep(0)
        ping.assert_awaited_once_with("http://telescope.railway.internal:8080/wake")

    @pytest.mark.asyncio
    async def test_no_ping_when_a_worker_is_live(self, monkeypatch) -> None:
        q, ping = self._queue(monkeypatch, live=2)
        await q._maybe_wake(MagicMock())
        await asyncio.sleep(0)
        ping.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_ping_without_wake_url(self, monkeypatch) -> None:
        q, ping = self._queue(monkeypatch, live=0, url="")
        await q._maybe_wake(MagicMock())
        await asyncio.sleep(0)
        ping.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_ping_errors_are_swallowed(self, monkeypatch) -> None:
        class _Boom:
            def __init__(self, *a, **k): ...
            async def __aenter__(self): raise OSError("502 while booting")
            async def __aexit__(self, *a): return False

        monkeypatch.setattr(pw_mod.httpx, "AsyncClient", _Boom)
        await pw_mod._TelescopeQueue()._ping_wake("http://x/wake")  # no raise

    @pytest.mark.asyncio
    async def test_healthy_means_queue_reachable_and_wakes(self, monkeypatch) -> None:
        q, ping = self._queue(monkeypatch, live=0)
        monkeypatch.setattr(q, "_get_db", AsyncMock(return_value=MagicMock()))
        assert await q.healthy() is True  # no live worker is fine: Telescope may be asleep
        await asyncio.sleep(0)
        ping.assert_awaited_once()
