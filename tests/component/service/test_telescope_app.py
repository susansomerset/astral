"""AST-1725 — FastAPI contract: auth, defaults, healthz, scrape routes, timeout/502."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402


def _fake_pool(*, health_ok: bool = True) -> MagicMock:
    """BrowserPool stand-in — no Playwright Firefox."""
    pool = MagicMock()
    pool.start = AsyncMock()
    pool.stop = AsyncMock()
    pool.health_poke = AsyncMock(return_value=health_ok)

    page = MagicMock()
    page.url = "https://example.com/final"
    page.goto = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.evaluate = AsyncMock(return_value="hello")
    page.locator = MagicMock()

    @asynccontextmanager
    async def page_cm() -> AsyncIterator[Any]:
        yield page

    pool.page = page_cm
    pool._page = page  # test access
    return pool


@pytest.fixture
def telescope_app_client(bearer_headers):
    """TestClient with mocked BrowserPool lifespan."""
    pool = _fake_pool()

    with patch("app.BrowserPool", return_value=pool):
        # Fresh import after path/env from conftest
        import importlib

        import app as app_mod

        importlib.reload(app_mod)
        with patch.object(app_mod, "BrowserPool", return_value=pool):
            # Rebuild app with patched pool — reload already bound lifespan
            # Re-patch lifespan factory by replacing state after enter
            with TestClient(app_mod.app) as client:
                # Lifespan may have started a real BrowserPool if patch missed —
                # force our pool onto app.state
                client.app.state.pool = pool
                yield client, pool, bearer_headers


class TestTelescopeRequestDefaults:
    def test_expand_fields_default_wait_ready_off(self) -> None:
        import app as app_mod

        body = app_mod.TelescopeRequest(url="https://example.com")
        assert body.expand is True
        assert body.fields == ["text", "links"]
        assert body.wait_ready is False

    def test_html_request_defaults(self) -> None:
        import app as app_mod

        body = app_mod.TelescopeHtmlRequest(url="https://example.com")
        assert body.expand is True
        assert body.wait_ready is False


class TestBearerAuth:
    def test_healthz_missing_bearer_401(self, telescope_app_client) -> None:
        client, _pool, _headers = telescope_app_client
        resp = client.get("/healthz")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "unauthorized"

    def test_healthz_wrong_bearer_401(self, telescope_app_client) -> None:
        client, _pool, _headers = telescope_app_client
        resp = client.get(
            "/healthz", headers={"Authorization": "Bearer wrong-token-xx"}
        )
        assert resp.status_code == 401

    def test_telescope_missing_bearer_401(self, telescope_app_client) -> None:
        client, _pool, _headers = telescope_app_client
        resp = client.post("/telescope", json={"url": "https://example.com"})
        assert resp.status_code == 401


class TestHealthz:
    def test_healthz_ok(self, telescope_app_client) -> None:
        client, pool, headers = telescope_app_client
        pool.health_poke = AsyncMock(return_value=True)
        resp = client.get("/healthz", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
        pool.health_poke.assert_awaited()

    def test_healthz_unhealthy_503(self, telescope_app_client) -> None:
        client, pool, headers = telescope_app_client
        pool.health_poke = AsyncMock(return_value=False)
        resp = client.get("/healthz", headers=headers)
        assert resp.status_code == 503
        assert resp.json() == {"status": "unhealthy"}


class TestTelescopeRoutes:
    def test_post_telescope_defaults_include_links(
        self, telescope_app_client, monkeypatch
    ) -> None:
        client, pool, headers = telescope_app_client
        calls: dict[str, Any] = {}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            calls["expand"] = expand
            calls["wait_ready"] = wait_ready
            calls["url"] = url
            page = MagicMock()
            page.url = "https://example.com/final"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)

        async def capt_text(page, selector):
            return "body text"

        async def capt_links(page, selector=None):
            return [{"href": "https://a.com", "text": "A"}]

        monkeypatch.setattr(app_mod, "capture_text", capt_text)
        monkeypatch.setattr(app_mod, "capture_links", capt_links)

        resp = client.post(
            "/telescope",
            headers=headers,
            json={"url": "https://example.com"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["final_url"] == "https://example.com/final"
        assert data["text"] == "body text"
        assert data["links"] == [{"href": "https://a.com", "text": "A"}]
        assert calls["expand"] is True
        assert calls["wait_ready"] is False

    def test_ast1732_post_telescope_passes_selector_to_capture_links(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1732 bug-repro: app must forward body.selector into capture_links."""
        client, _pool, headers = telescope_app_client
        seen: dict[str, Any] = {}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/jobs"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)

        async def capt_text(page, selector):
            return "scoped"

        async def capt_links(page, selector=None):
            seen["selector"] = selector
            return [{"href": "https://example.com/in", "text": "In"}]

        monkeypatch.setattr(app_mod, "capture_text", capt_text)
        monkeypatch.setattr(app_mod, "capture_links", capt_links)

        resp = client.post(
            "/telescope",
            headers=headers,
            json={
                "url": "https://example.com/jobs",
                "selector": ".job-list",
                "fields": ["text", "links"],
            },
        )
        assert resp.status_code == 200
        assert seen.get("selector") == ".job-list", (
            "AST-1732: POST /telescope must call capture_links(page, body.selector)"
        )

    def test_post_telescope_text_only_omits_links(
        self, telescope_app_client, monkeypatch
    ) -> None:
        client, _pool, headers = telescope_app_client

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/final"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)
        monkeypatch.setattr(
            app_mod, "capture_text", AsyncMock(return_value="t")
        )
        links_mock = AsyncMock(return_value=[{"href": "https://x", "text": "x"}])
        monkeypatch.setattr(app_mod, "capture_links", links_mock)

        resp = client.post(
            "/telescope",
            headers=headers,
            json={"url": "https://example.com", "fields": ["text"]},
        )
        assert resp.status_code == 200
        assert "links" not in resp.json()
        links_mock.assert_not_awaited()

    def test_post_telescope_text_and_links_one_load(
        self, telescope_app_client, monkeypatch
    ) -> None:
        client, _pool, headers = telescope_app_client
        job_calls = {"n": 0}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            job_calls["n"] += 1
            page = MagicMock()
            page.url = "https://example.com/final"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)
        monkeypatch.setattr(
            app_mod, "capture_text", AsyncMock(return_value="body text")
        )
        monkeypatch.setattr(
            app_mod,
            "capture_links",
            AsyncMock(return_value=[{"href": "https://a.com", "text": "A"}]),
        )

        resp = client.post(
            "/telescope",
            headers=headers,
            json={"url": "https://example.com", "fields": ["text", "links"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["text"] == "body text"
        assert data["links"] == [{"href": "https://a.com", "text": "A"}]
        assert job_calls["n"] == 1

    def test_post_telescope_all_fields_one_load(
        self, telescope_app_client, monkeypatch
    ) -> None:
        client, _pool, headers = telescope_app_client
        seen: dict[str, bool] = {}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/all"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)

        async def capt_text(page, selector):
            seen["text"] = True
            return "t"

        async def capt_links(page, selector=None):
            seen["links"] = True
            return []

        async def capt_html(page, selector=None):
            seen["html"] = True
            return "<html/>"

        monkeypatch.setattr(app_mod, "capture_text", capt_text)
        monkeypatch.setattr(app_mod, "capture_links", capt_links)
        monkeypatch.setattr(app_mod, "capture_html", capt_html)

        resp = client.post(
            "/telescope",
            headers=headers,
            json={
                "url": "https://example.com",
                "fields": ["text", "links", "html"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["text"] == "t"
        assert data["links"] == []
        assert data["html"] == "<html/>"
        assert seen == {"text": True, "links": True, "html": True}

    def test_post_telescope_empty_url_400(self, telescope_app_client) -> None:
        client, _pool, headers = telescope_app_client
        resp = client.post(
            "/telescope", headers=headers, json={"url": "  "}
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "url required"

    def test_post_telescope_html(self, telescope_app_client, monkeypatch) -> None:
        client, _pool, headers = telescope_app_client

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/h"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)
        monkeypatch.setattr(
            app_mod, "capture_html", AsyncMock(return_value="<html/>")
        )

        resp = client.post(
            "/telescope/html",
            headers=headers,
            json={"url": "https://example.com"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["final_url"] == "https://example.com/h"
        assert data["html"] == "<html/>"
        assert "scrape_meta" in data

    def test_ast1736_html_class_name_resolves_to_dot_class(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1736 bug-repro: class_name 'shaders' → capture_html gets '.shaders'."""
        client, _pool, headers = telescope_app_client
        seen: dict[str, Any] = {}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/s"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)

        async def capt_html(page, selector=None):
            seen["selector"] = selector
            return '<div class="shaders">hit</div>'

        monkeypatch.setattr(app_mod, "capture_html", capt_html)

        resp = client.post(
            "/telescope/html",
            headers=headers,
            json={
                "url": "https://example.com/s",
                "class_name": "shaders",
                "expand": False,
            },
        )
        assert resp.status_code == 200
        assert seen.get("selector") == ".shaders", (
            "AST-1736: class_name must resolve to CSS .shaders before capture_html"
        )
        html = resp.json().get("html") or ""
        assert "shaders" in html

    def test_ast1744_bare_primary_plus_class_name_resolves_to_tag_class(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1744 bug-repro: bare primary (selector alias) + class_name → tag.class.

        Rewrites AST-1736 XOR assert — bare selector + class_name is no longer 400.
        """
        client, _pool, headers = telescope_app_client
        seen: dict[str, Any] = {}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/x"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)

        async def capt_html(page, selector=None):
            seen["selector"] = selector
            return '<div class="logo">hit</div>'

        monkeypatch.setattr(app_mod, "capture_html", capt_html)

        resp = client.post(
            "/telescope/html",
            headers=headers,
            json={
                "url": "https://example.com/x",
                "selector": "div",
                "class_name": "logo",
                "expand": False,
            },
        )
        assert resp.status_code == 200, (
            "AST-1744: bare selector primary + class_name must combine, not 400"
        )
        assert seen.get("selector") == "div.logo", (
            "AST-1744: must resolve to CSS div.logo"
        )

    def test_ast1744_tag_plus_class_name_resolves_to_tag_class(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1744: explicit tag + class_name → tag.class."""
        client, _pool, headers = telescope_app_client
        seen: dict[str, Any] = {}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/t"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)

        async def capt_html(page, selector=None):
            seen["selector"] = selector
            return '<div class="logo">hit</div>'

        monkeypatch.setattr(app_mod, "capture_html", capt_html)

        resp = client.post(
            "/telescope/html",
            headers=headers,
            json={
                "url": "https://example.com/t",
                "tag": "div",
                "class_name": "logo",
                "expand": False,
            },
        )
        assert resp.status_code == 200
        assert seen.get("selector") == "div.logo", (
            "AST-1744: tag + class_name must resolve to div.logo"
        )

    def test_ast1744_complex_selector_plus_class_name_still_400(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1744: complex CSS primary + class_name stays ambiguous → 400."""
        client, _pool, headers = telescope_app_client

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/c"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)
        monkeypatch.setattr(
            app_mod, "capture_html", AsyncMock(return_value="<div/>")
        )

        resp = client.post(
            "/telescope/html",
            headers=headers,
            json={
                "url": "https://example.com/c",
                "selector": ".other",
                "class_name": "logo",
                "expand": False,
            },
        )
        assert resp.status_code == 400, (
            "AST-1744: complex CSS selector + class_name must still 400"
        )


class TestRunBrowserJobErrors:
    @pytest.mark.asyncio
    async def test_timeout_raises_504(self, monkeypatch) -> None:
        import app as app_mod
        from dataclasses import replace

        from fastapi import HTTPException

        monkeypatch.setattr(
            app_mod,
            "settings",
            replace(app_mod.settings, request_timeout_seconds=0.01),
        )

        pool = _fake_pool()

        @asynccontextmanager
        async def ok_page():
            yield MagicMock()

        pool.page = ok_page

        async def slow_navigate(page, url):
            await asyncio.sleep(10)

        monkeypatch.setattr(app_mod, "navigate", slow_navigate)
        monkeypatch.setattr(app_mod, "dismiss_cookies", AsyncMock(return_value=False))
        monkeypatch.setattr(app_mod, "expand_page", AsyncMock())

        with pytest.raises(HTTPException) as exc:
            await app_mod._run_browser_job(
                pool, "https://example.com", True, False, AsyncMock()
            )
        assert exc.value.status_code == 504
        assert exc.value.detail == "timeout"

    @pytest.mark.asyncio
    async def test_slot_wait_does_not_count_against_scrape_timeout(
        self, monkeypatch
    ) -> None:
        """Queue wait for pool.page() must not consume the scrape timeout budget."""
        import app as app_mod
        from dataclasses import replace

        monkeypatch.setattr(
            app_mod,
            "settings",
            replace(app_mod.settings, request_timeout_seconds=0.05),
        )
        pool = _fake_pool()

        @asynccontextmanager
        async def slow_acquire_page():
            await asyncio.sleep(0.2)
            yield MagicMock()

        pool.page = slow_acquire_page
        monkeypatch.setattr(app_mod, "navigate", AsyncMock())
        monkeypatch.setattr(app_mod, "dismiss_cookies", AsyncMock(return_value=False))
        monkeypatch.setattr(app_mod, "expand_page", AsyncMock())
        work = AsyncMock(return_value={"ok": True})

        result, cookies = await app_mod._run_browser_job(
            pool, "https://example.com", False, False, work
        )
        assert result == {"ok": True}
        assert cookies is False

    @pytest.mark.asyncio
    async def test_scrape_failed_raises_502_after_retries(self, monkeypatch) -> None:
        import app as app_mod
        from dataclasses import replace
        from fastapi import HTTPException

        monkeypatch.setattr(
            app_mod,
            "settings",
            replace(
                app_mod.settings,
                scrape_retry_count=2,
                scrape_retry_base_delay_seconds=0.0,
            ),
        )
        sleep_mock = AsyncMock()
        monkeypatch.setattr(app_mod.asyncio, "sleep", sleep_mock)

        pool = _fake_pool()
        calls = {"n": 0}

        @asynccontextmanager
        async def boom_page():
            calls["n"] += 1
            raise RuntimeError("firefox died")
            yield  # pragma: no cover

        pool.page = boom_page

        with pytest.raises(HTTPException) as exc:
            await app_mod._run_browser_job(
                pool, "https://example.com", False, False, AsyncMock()
            )
        assert exc.value.status_code == 502
        assert exc.value.detail == "scrape_failed"
        assert calls["n"] == 3
        assert sleep_mock.await_count == 2
        sleep_mock.assert_any_await(0.0)
        sleep_mock.assert_any_await(0.0)

    @pytest.mark.asyncio
    async def test_scrape_retry_succeeds_on_second_attempt(self, monkeypatch) -> None:
        import app as app_mod
        from dataclasses import replace

        monkeypatch.setattr(
            app_mod,
            "settings",
            replace(
                app_mod.settings,
                scrape_retry_count=3,
                scrape_retry_base_delay_seconds=0.0,
            ),
        )
        monkeypatch.setattr(app_mod.asyncio, "sleep", AsyncMock())
        monkeypatch.setattr(app_mod, "navigate", AsyncMock())
        monkeypatch.setattr(app_mod, "dismiss_cookies", AsyncMock(return_value=False))
        monkeypatch.setattr(app_mod, "expand_page", AsyncMock())

        pool = _fake_pool()
        work = AsyncMock(
            side_effect=[RuntimeError("document.body is null"), {"ok": True}]
        )

        @asynccontextmanager
        async def ok_page():
            yield MagicMock()

        pool.page = ok_page

        result, cookies = await app_mod._run_browser_job(
            pool, "https://example.com", False, False, work
        )
        assert result == {"ok": True}
        assert cookies is False
        assert work.await_count == 2

    @pytest.mark.asyncio
    async def test_scrape_retry_telescoping_delays(self, monkeypatch) -> None:
        import app as app_mod
        from dataclasses import replace
        from fastapi import HTTPException

        monkeypatch.setattr(
            app_mod,
            "settings",
            replace(
                app_mod.settings,
                scrape_retry_count=3,
                scrape_retry_base_delay_seconds=2.0,
            ),
        )
        sleep_mock = AsyncMock()
        monkeypatch.setattr(app_mod.asyncio, "sleep", sleep_mock)
        monkeypatch.setattr(app_mod, "navigate", AsyncMock())
        monkeypatch.setattr(app_mod, "dismiss_cookies", AsyncMock(return_value=False))
        monkeypatch.setattr(app_mod, "expand_page", AsyncMock())

        pool = _fake_pool()
        work = AsyncMock(side_effect=RuntimeError("flake"))

        @asynccontextmanager
        async def ok_page():
            yield MagicMock()

        pool.page = ok_page

        with pytest.raises(HTTPException):
            await app_mod._run_browser_job(
                pool, "https://example.com", False, False, work
            )

        assert sleep_mock.await_args_list == [((2.0,),), ((4.0,),), ((8.0,),)]


class TestAst1728ScrapeMeta:
    """AST-1728 bug-repro — additive scrape_meta on contract endpoints (pre-fix red)."""

    def test_post_telescope_includes_scrape_meta(
        self, telescope_app_client, monkeypatch
    ) -> None:
        client, _pool, headers = telescope_app_client

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/final"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)
        monkeypatch.setattr(
            app_mod, "capture_text", AsyncMock(return_value="visible body text")
        )
        monkeypatch.setattr(
            app_mod, "capture_links", AsyncMock(return_value=[])
        )

        resp = client.post(
            "/telescope",
            headers=headers,
            json={"url": "https://example.com", "fields": ["text"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "scrape_meta" in data, "AST-1728: service must attach scrape_meta"
        meta = data["scrape_meta"]
        for key in ("bot_blocked", "cookies_dismissed", "issues", "content_chars"):
            assert key in meta, f"scrape_meta missing {key}"

    def test_post_telescope_html_includes_scrape_meta(
        self, telescope_app_client, monkeypatch
    ) -> None:
        client, _pool, headers = telescope_app_client

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/h"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)
        monkeypatch.setattr(
            app_mod, "capture_html", AsyncMock(return_value="<html/>")
        )

        resp = client.post(
            "/telescope/html",
            headers=headers,
            json={"url": "https://example.com"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "scrape_meta" in data, "AST-1728: html endpoint must attach scrape_meta"
        assert "content_chars" in data["scrape_meta"]
