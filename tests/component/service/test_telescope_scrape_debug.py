"""Scrape debug flag — narrative T/C/F tracing when request debug=True."""

from __future__ import annotations

import importlib
import json
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
    def test_tcf_narrative_messages(self, capsys) -> None:
        """T = URL request, C = context (1:1 with T), F = Firefox process."""
        import scrape_debug as dbg

        request_id, tokens = dbg.begin_scrape_request(
            "https://www.scrapeme.com", fields=["text", "links"]
        )
        debug_token = dbg.enable_scrape_debug()
        try:
            dbg.scrape_debug_event("request_start")
            dbg.scrape_debug_event(
                "firefox_needed", live_count=0, firefox_id="F-001"
            )
            dbg.bind_scrape_firefox("F-001")
            dbg.scrape_debug_event("firefox_launched", firefox="F-001")
            ctx = dbg.alloc_context_id()
            dbg.scrape_debug_event(
                "request_serving", firefox="F-001", context=ctx,
            )
            dbg.scrape_debug_event("context_created", firefox="F-001", context=ctx)
            dbg.scrape_debug_event("page_created")
            dbg.scrape_debug_event("navigate_start")
            dbg.scrape_debug_event("scrape_field", field="text")
            dbg.scrape_debug_event("scrape_field", field="links")
            dbg.scrape_debug_event("context_closed")
            dbg.scrape_debug_event("firefox_closed", firefox="F-001")
            dbg.scrape_debug_event("request_done")
        finally:
            dbg.disable_scrape_debug(debug_token)
            dbg.end_scrape_request(tokens)

        messages = [
            json.loads(ln)["message"]
            for ln in capsys.readouterr().out.strip().splitlines()
            if ln
        ]
        assert request_id == "T-001"
        assert ctx == "C-001"
        assert messages[0].startswith("T-001: Accepted url https://www.scrapeme.com, text, links")
        assert "(awaiting F/C)" in messages[0]
        assert 'creating "F-001"' in messages[1]
        assert messages[2] == "F-001: Starting firefox app with playwright [live T=1 F=1 C=0]"
        assert (
            messages[3]
            == "T-001 (F-001 C-001): Requesting url https://www.scrapeme.com, text, links [live T=1 F=1 C=0]"
        )
        assert messages[4] == 'F-001: Creating context "C-001" [live T=1 F=1 C=1]'
        assert messages[5] == "C-001: Starting context [live T=1 F=1 C=1]"
        assert messages[6] == "C-001: Loading Page [live T=1 F=1 C=1]"
        assert messages[7] == "C-001: Scraping Page for text [live T=1 F=1 C=1]"
        assert messages[8] == "C-001: Scraping Page for links [live T=1 F=1 C=1]"
        assert messages[9] == "C-001: Close Page [live T=1 F=1 C=0]"
        assert messages[10] == "F-001: Close Instance [live T=1 F=0 C=0]"
        assert (
            messages[11]
            == "T-001 (F-001 C-001): Request Return Successful for url https://www.scrapeme.com [live T=1 F=0 C=0]"
        )

    def test_live_counters_track_start_and_recycle(self) -> None:
        import scrape_debug as dbg

        _, tokens = dbg.begin_scrape_request("https://a.example")
        assert dbg.live_instance_counts() == {
            "live_requests": 1, "live_firefox": 0, "live_contexts": 0,
        }
        debug_token = dbg.enable_scrape_debug()
        try:
            dbg.scrape_debug_event("firefox_launched", firefox="F-001")
            dbg.scrape_debug_event("context_created", firefox="F-001", context="C-001")
            assert dbg.live_instance_counts() == {
                "live_requests": 1, "live_firefox": 1, "live_contexts": 1,
            }
            dbg.scrape_debug_event("context_closed", context="C-001")
            assert dbg.live_instance_counts() == {
                "live_requests": 1, "live_firefox": 1, "live_contexts": 0,
            }
            dbg.scrape_debug_event("firefox_closed", firefox="F-001")
            assert dbg.live_instance_counts() == {
                "live_requests": 1, "live_firefox": 0, "live_contexts": 0,
            }
        finally:
            dbg.disable_scrape_debug(debug_token)
            dbg.end_scrape_request(tokens)
        assert dbg.live_instance_counts() == {
            "live_requests": 0, "live_firefox": 0, "live_contexts": 0,
        }

    def test_deployment_ids_monotonic_across_requests(self) -> None:
        import scrape_debug as dbg

        t1, tokens1 = dbg.begin_scrape_request("https://a.example")
        f1 = dbg.alloc_firefox_instance_id()
        c1 = dbg.alloc_context_id()
        # Pool/retry loops must not bump ids mid-request.
        assert dbg.alloc_firefox_instance_id() == f1
        assert dbg.alloc_context_id() == c1
        dbg.end_scrape_request(tokens1)

        t2, tokens2 = dbg.begin_scrape_request("https://b.example")
        assert int(t2[2:]) == int(t1[2:]) + 1
        assert dbg.alloc_firefox_instance_id() != f1
        assert dbg.alloc_context_id() != c1
        dbg.end_scrape_request(tokens2)

    def test_debug_events_suppressed_by_default(self, capsys) -> None:
        import scrape_debug as dbg

        dbg.scrape_debug_event("should_not_appear", url="https://example.com")
        assert capsys.readouterr().out.strip() == ""

    def test_debug_events_emit_when_enabled(self, capsys) -> None:
        import scrape_debug as dbg

        token = dbg.enable_scrape_debug()
        try:
            dbg.bind_scrape_firefox("F-001")
            dbg.bind_scrape_context("C-001")
            dbg.scrape_debug_event(
                "context_created",
                firefox="F-001",
                context="C-001",
            )
            dbg.log_scrape_capture(
                {"final_url": "https://example.com/", "text": "hello", "links": []},
                capture_fields=["text"],
            )
        finally:
            dbg.disable_scrape_debug(token)

        payloads = [
            json.loads(ln)
            for ln in capsys.readouterr().out.strip().splitlines()
            if ln
        ]
        assert any(p.get("event") == "context_created" for p in payloads)
        scrape_lines = [p for p in payloads if p.get("event") == "scrape_field"]
        assert len(scrape_lines) == 1
        assert "C-001: Scraping Page for text" in scrape_lines[0]["message"]
        assert scrape_lines[0]["live_contexts"] == 1
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
