"""Scrape debug flag — narrative T/F/C tracing when a job has debug=True."""

from __future__ import annotations

import json


class TestScrapeDebugHelpers:
    def test_tfc_narrative_messages(self, capsys) -> None:
        """T = job attempt, F = Firefox launch, C = context (ids are per process)."""
        import scrape_debug as dbg

        request_id, tokens = dbg.begin_scrape_request(
            "https://www.scrapeme.com", fields=["text", "links"]
        )
        debug_token = dbg.enable_scrape_debug()
        try:
            dbg.scrape_debug_event("request_start")
            ff = dbg.alloc_firefox_instance_id()
            dbg.bind_scrape_firefox(ff)
            dbg.scrape_debug_event("firefox_launched", firefox=ff)
            ctx = dbg.alloc_context_id()
            dbg.scrape_debug_event("request_serving", firefox=ff, context=ctx)
            dbg.scrape_debug_event("context_created", firefox=ff, context=ctx)
            dbg.scrape_debug_event("page_created")
            dbg.scrape_debug_event("navigate_start")
            dbg.scrape_debug_event("scrape_field", field="text")
            dbg.scrape_debug_event("context_closed")
            dbg.scrape_debug_event("firefox_closed", firefox=ff)
            dbg.scrape_debug_event("request_done")
        finally:
            dbg.disable_scrape_debug(debug_token)
            dbg.end_scrape_request(tokens)

        messages = [
            json.loads(ln)["message"]
            for ln in capsys.readouterr().out.strip().splitlines()
            if ln
        ]
        url = "url=https://www.scrapeme.com"
        tag = f"{request_id} ({ff} {ctx})"
        assert messages[0].startswith(f"{request_id}: Accepted, text, links (awaiting F/C) {url}")
        assert messages[1].startswith(f"{ff}: Starting firefox app with playwright {url}")
        assert messages[2].startswith(f"{tag}: Requesting, text, links {url}")
        assert messages[3].startswith(f'{ff}: Creating context "{ctx}" {url}')
        assert messages[4].startswith(f"{ctx}: Starting context {url}")
        assert messages[5].startswith(f"{ctx}: Loading Page {url}")
        assert messages[6].startswith(f"{ctx}: Scraping Page for text {url}")
        assert messages[7].startswith(f"{ctx}: Close Page {url}")
        assert messages[8].startswith(f"{ff}: Close Instance {url}")
        assert messages[9].startswith(f"{tag}: Request Return Successful {url}")
        assert not any("S-" in m for m in messages)

    def test_live_firefox_counted_without_debug(self) -> None:
        """Firefox launches outside any debug job — live F must still count it."""
        import scrape_debug as dbg

        before = dbg.live_instance_counts()["live_firefox"]
        ff = dbg.alloc_firefox_instance_id()
        dbg.scrape_debug_event("firefox_launched", firefox=ff)
        assert dbg.live_instance_counts()["live_firefox"] == before + 1
        dbg.scrape_debug_event("firefox_closed", firefox=ff)
        assert dbg.live_instance_counts()["live_firefox"] == before

    def test_live_counters_track_start_and_recycle(self) -> None:
        import scrape_debug as dbg

        def delta(base: dict) -> dict:
            now = dbg.live_instance_counts()
            return {k: now[k] - base[k] for k in now}

        base = dbg.live_instance_counts()
        _, tokens = dbg.begin_scrape_request("https://a.example")
        assert delta(base) == {"live_requests": 1, "live_firefox": 0, "live_contexts": 0}
        ff = dbg.alloc_firefox_instance_id()
        dbg.scrape_debug_event("firefox_launched", firefox=ff)
        dbg.scrape_debug_event("context_created", firefox=ff, context="C-live")
        assert delta(base) == {"live_requests": 1, "live_firefox": 1, "live_contexts": 1}
        dbg.scrape_debug_event("context_closed", context="C-live")
        assert delta(base) == {"live_requests": 1, "live_firefox": 1, "live_contexts": 0}
        dbg.scrape_debug_event("firefox_closed", firefox=ff)
        dbg.end_scrape_request(tokens)
        assert delta(base) == {"live_requests": 0, "live_firefox": 0, "live_contexts": 0}

    def test_deployment_ids_monotonic_across_requests(self) -> None:
        import scrape_debug as dbg

        t1, tokens1 = dbg.begin_scrape_request("https://a.example")
        f1 = dbg.alloc_firefox_instance_id()
        c1 = dbg.alloc_context_id()
        assert dbg.current_context_id() == c1
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

        _, tokens = dbg.begin_scrape_request("https://example.com")
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
            dbg.end_scrape_request(tokens)

        payloads = [
            json.loads(ln)
            for ln in capsys.readouterr().out.strip().splitlines()
            if ln
        ]
        assert any(p.get("event") == "context_created" for p in payloads)
        scrape_lines = [p for p in payloads if p.get("event") == "scrape_field"]
        assert len(scrape_lines) == 1
        assert scrape_lines[0]["message"].startswith("C-001: Scraping Page for text url=https://example.com")
        assert "slot" not in scrape_lines[0]
        assert scrape_lines[0]["firefox"] == "F-001" and scrape_lines[0]["context"] == "C-001"
        assert all(p.get("level") == "debug" for p in payloads)
