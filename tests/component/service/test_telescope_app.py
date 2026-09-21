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
    def test_expand_links_on_wait_ready_off(self) -> None:
        import app as app_mod

        body = app_mod.TelescopeRequest(url="https://example.com")
        assert body.expand is True
        assert body.links is True
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
                "links": True,
            },
        )
        assert resp.status_code == 200
        assert seen.get("selector") == ".job-list", (
            "AST-1732: POST /telescope must call capture_links(page, body.selector)"
        )

    def test_post_telescope_links_false_omits_links(
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
            json={"url": "https://example.com", "links": False},
        )
        assert resp.status_code == 200
        assert "links" not in resp.json()
        links_mock.assert_not_awaited()

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
        assert resp.json() == {
            "final_url": "https://example.com/h",
            "html": "<html/>",
        }

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

    def test_ast1736_selector_plus_class_name_returns_400(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1736 bug-repro: selector + class_name together is ambiguous → 400."""
        client, _pool, headers = telescope_app_client

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/x"
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
                "url": "https://example.com/x",
                "selector": ".other",
                "class_name": "shaders",
                "expand": False,
            },
        )
        assert resp.status_code == 400, (
            "AST-1736: selector + class_name must be rejected as ambiguous"
        )

    def test_ast1746_html_id_resolves_to_hash_id(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1746 bug-repro: id 'hero' → capture_html gets '#hero'."""
        client, _pool, headers = telescope_app_client
        seen: dict[str, Any] = {}

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/h"
            return await work(page)

        import app as app_mod

        monkeypatch.setattr(app_mod, "_run_browser_job", fake_run)

        async def capt_html(page, selector=None):
            seen["selector"] = selector
            return '<div id="hero">hit</div>'

        monkeypatch.setattr(app_mod, "capture_html", capt_html)

        resp = client.post(
            "/telescope/html",
            headers=headers,
            json={
                "url": "https://example.com/h",
                "id": "hero",
                "expand": False,
            },
        )
        assert resp.status_code == 200
        assert seen.get("selector") == "#hero", (
            "AST-1746: id must resolve to CSS #hero before capture_html"
        )
        html = resp.json().get("html") or ""
        assert "hero" in html

    def test_ast1746_selector_plus_id_returns_400(
        self, telescope_app_client, monkeypatch
    ) -> None:
        """AST-1746 bug-repro: selector + id together is ambiguous → 400."""
        client, _pool, headers = telescope_app_client

        async def fake_run(pool_arg, url, expand, wait_ready, work):
            page = MagicMock()
            page.url = "https://example.com/x"
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
                "url": "https://example.com/x",
                "selector": ".other",
                "id": "hero",
                "expand": False,
            },
        )
        assert resp.status_code == 400, (
            "AST-1746: selector + id must be rejected as ambiguous"
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
        async def hanging_page():
            await asyncio.sleep(10)
            yield MagicMock()

        pool.page = hanging_page

        with pytest.raises(HTTPException) as exc:
            await app_mod._run_browser_job(
                pool, "https://example.com", True, False, AsyncMock()
            )
        assert exc.value.status_code == 504
        assert exc.value.detail == "timeout"

    @pytest.mark.asyncio
    async def test_scrape_failed_raises_502(self) -> None:
        import app as app_mod
        from fastapi import HTTPException

        pool = _fake_pool()

        @asynccontextmanager
        async def boom_page():
            raise RuntimeError("firefox died")
            yield  # pragma: no cover

        pool.page = boom_page

        with pytest.raises(HTTPException) as exc:
            await app_mod._run_browser_job(
                pool, "https://example.com", False, False, AsyncMock()
            )
        assert exc.value.status_code == 502
        assert exc.value.detail == "scrape_failed"


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
            json={"url": "https://example.com", "links": False},
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
