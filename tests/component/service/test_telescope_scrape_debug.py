"""Scrape debug flag — structured console events when request debug=True."""

from __future__ import annotations

import importlib
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402


def _fake_pool() -> MagicMock:
    pool = MagicMock()
    pool.start = AsyncMock()
    pool.stop = AsyncMock()
    pool.health_poke = AsyncMock(return_value=True)

    page = MagicMock()
    page.url = "https://example.com/final"

    @asynccontextmanager
    async def page_cm() -> AsyncIterator[Any]:
        yield page

    pool.page = page_cm
    return pool


@pytest.fixture
def telescope_debug_client(bearer_headers):
    pool = _fake_pool()
    import app as app_mod

    importlib.reload(app_mod)
    with patch.object(app_mod, "BrowserPool", return_value=pool):
        with TestClient(app_mod.app) as client:
            client.app.state.pool = pool
            yield client, bearer_headers


class TestScrapeDebugHelpers:
    def test_debug_events_suppressed_by_default(self, capsys) -> None:
        import scrape_debug as dbg

        dbg.scrape_debug_event("should_not_appear", url="https://example.com")
        assert capsys.readouterr().out.strip() == ""

    def test_debug_events_emit_when_enabled(self, capsys) -> None:
        import scrape_debug as dbg

        token = dbg.enable_scrape_debug()
        try:
            dbg.scrape_debug_event(
                "context_created",
                firefox="slot_0",
                context_id=123,
            )
            dbg.log_scrape_capture(
                {
                    "final_url": "https://example.com/",
                    "text": "hello",
                    "links": [{"href": "/a", "text": "A"}],
                }
            )
        finally:
            dbg.disable_scrape_debug(token)

        payloads = [
            json.loads(ln)
            for ln in capsys.readouterr().out.strip().splitlines()
            if ln
        ]
        assert any(p.get("event") == "context_created" for p in payloads)
        assert any(p.get("event") == "scrape_capture" for p in payloads)
        assert any(p.get("text_chars") == 5 for p in payloads)
        assert any(p.get("link_count") == 1 for p in payloads)
        assert all(p.get("level") == "debug" for p in payloads)


class TestScrapeDebugApiFlag:
    def test_request_debug_defaults_false(self) -> None:
        import app as app_mod

        body = app_mod.TelescopeRequest(url="https://example.com")
        assert body.debug is False

    def test_post_telescope_debug_emits_request_events(
        self, telescope_debug_client, monkeypatch, capsys
    ) -> None:
        client, headers = telescope_debug_client
        import app as app_mod

        monkeypatch.setattr(
            app_mod,
            "_scrape_with_fields",
            AsyncMock(
                return_value={
                    "final_url": "https://example.com/final",
                    "text": "body",
                    "links": [],
                    "scrape_meta": {},
                }
            ),
        )

        resp = client.post(
            "/telescope",
            headers=headers,
            json={"url": "https://example.com", "debug": True},
        )
        assert resp.status_code == 200
        debug_events = [
            json.loads(ln).get("event")
            for ln in capsys.readouterr().out.strip().splitlines()
            if ln and '"level": "debug"' in ln
        ]
        assert "request_start" in debug_events
        assert "request_done" in debug_events

    def test_post_telescope_debug_false_emits_no_debug_events(
        self, telescope_debug_client, monkeypatch, capsys
    ) -> None:
        client, headers = telescope_debug_client
        import app as app_mod

        monkeypatch.setattr(
            app_mod,
            "_scrape_with_fields",
            AsyncMock(
                return_value={
                    "final_url": "https://example.com/",
                    "text": "x",
                    "links": [],
                    "scrape_meta": {},
                }
            ),
        )

        resp = client.post(
            "/telescope",
            headers=headers,
            json={"url": "https://example.com", "debug": False},
        )
        assert resp.status_code == 200
        out = capsys.readouterr().out
        assert '"level": "debug"' not in out
