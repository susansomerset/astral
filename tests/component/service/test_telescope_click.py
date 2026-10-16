"""Component tests for Telescope click-then-capture (AST-2023): interact / scrape / worker."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import interact
import pytest
import scrape
from jobqueue import ClaimedJob
from worker import QueueWorker


async def _never(*_a, **_k):
    # Stands in for a Playwright waiter whose event never fires.
    await asyncio.Event().wait()


def _page(url: str, *, count: int = 1, popup=None, same_tab: bool = False, fail: bool = False):
    """Fake Playwright page. Exactly one of popup / same_tab / fail decides how the click lands."""
    loc = MagicMock()
    loc.count = AsyncMock(return_value=count)
    loc.first.click = AsyncMock()
    page = MagicMock()
    page.url = url
    page.locator = MagicMock(return_value=loc)
    page.wait_for_load_state = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    # Default: neither waiter ever fires.
    page.wait_for_event = MagicMock(side_effect=_never)
    page.wait_for_url = MagicMock(side_effect=_never)
    if popup is not None:
        page.wait_for_event = AsyncMock(return_value=popup)
    if same_tab:
        page.wait_for_url = AsyncMock(return_value=None)
    if fail:
        # Both waiters time out (Playwright raises a plain Error subclass).
        boom = Exception("Timeout 30000ms exceeded")
        page.wait_for_event = AsyncMock(side_effect=boom)
        page.wait_for_url = AsyncMock(side_effect=boom)
    return page, loc


# Branches: anchor missing (no click, no waiters); exact attribute selector + CSS escaping;
# same-tab navigation; new-tab popup; click that never navigates.
class TestAst2023ClickAndFollow:
    @pytest.mark.asyncio
    async def test_missing_anchor_raises_click_target_missing_without_clicking(self) -> None:
        page, loc = _page("https://co.example/jobs", count=0)
        with pytest.raises(interact.ClickTargetMissing):
            await interact.click_and_follow(page, "/jobs/404")
        # Fails on count(), not after a click / navigation timeout.
        loc.first.click.assert_not_awaited()
        page.wait_for_event.assert_not_called()
        page.wait_for_url.assert_not_called()

    @pytest.mark.asyncio
    async def test_selector_is_exact_href_attribute_with_css_escaping(self) -> None:
        page, _ = _page("https://co.example/jobs", count=0)
        with pytest.raises(interact.ClickTargetMissing):
            await interact.click_and_follow(page, '/a"b\\c')
        # Exact attribute match (no substring / resolved-URL matching); " and \ escaped.
        page.locator.assert_called_once_with('a[href="/a\\"b\\\\c"]')

    @pytest.mark.asyncio
    async def test_same_tab_navigation_returns_original_page(self) -> None:
        page, loc = _page("https://co.example/jobs", same_tab=True)
        dest = await interact.click_and_follow(page, "/jobs/1")
        assert dest is page
        loc.first.click.assert_awaited_once()
        page.wait_for_load_state.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_popup_returns_new_tab_page(self) -> None:
        popup = MagicMock(url="https://ats.example/job/1")
        popup.wait_for_load_state = AsyncMock()
        popup.wait_for_timeout = AsyncMock()
        page, _ = _page("https://co.example/jobs", popup=popup)
        dest = await interact.click_and_follow(page, "/jobs/1")
        assert dest is popup
        # Destination load wait runs on the popup, not the list page.
        popup.wait_for_load_state.assert_awaited_once()
        page.wait_for_load_state.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_click_without_navigation_is_plain_error_not_click_target_missing(self) -> None:
        page, _ = _page("https://co.example/jobs", fail=True)
        # Present-but-dead anchor → ordinary error → scrape_failed (retryable), not the missing class.
        with pytest.raises(RuntimeError, match="did not navigate"):
            await interact.click_and_follow(page, "/jobs/1")


def _firefox(page):
    @asynccontextmanager
    async def _page_cm():
        yield page

    return SimpleNamespace(page=_page_cm)


@pytest.fixture
def scrape_spies(monkeypatch: pytest.MonkeyPatch):
    """Stub every browser step in run_scrape; capture_text echoes the page it ran on."""
    calls: list[str] = []

    def _step(name, ret=None):
        async def _f(page, *_a, **_k):
            calls.append(name)
            return ret

        return _f

    monkeypatch.setattr(scrape, "navigate", _step("navigate"))
    monkeypatch.setattr(scrape, "expand_page", _step("expand"))
    monkeypatch.setattr(scrape, "wait_ready_generic", _step("wait_ready"))
    dismiss = AsyncMock(side_effect=[False, True])
    monkeypatch.setattr(scrape, "dismiss_cookies", dismiss)

    async def _capture_text(page, _sel):
        calls.append("capture")
        return f"text from {page.url} " * 10

    monkeypatch.setattr(scrape, "capture_text", _capture_text)
    return SimpleNamespace(calls=calls, dismiss=dismiss)


# Branches: no click_href → old sequence + old response keys; click_href → click after
# expand / wait_ready, capture + final_url on destination, cookie dismiss on destination;
# ClickTargetMissing → ScrapeError(click_target_missing); request model default.
class TestAst2023RunScrapeClick:
    LIST = "https://co.example/jobs"
    DEST = "https://ats.example/job/1"

    def test_request_click_href_defaults_none_and_parses(self) -> None:
        req, _ = scrape.parse_request({"url": self.LIST, "fields": ["text"]})
        assert req.click_href is None
        req, _ = scrape.parse_request({"url": self.LIST, "fields": ["text"], "click_href": "/jobs/1"})
        assert req.click_href == "/jobs/1"

    @pytest.mark.asyncio
    async def test_without_click_href_unchanged_sequence_and_shape(
        self, monkeypatch: pytest.MonkeyPatch, scrape_spies
    ) -> None:
        click = AsyncMock()
        monkeypatch.setattr(scrape, "click_and_follow", click)
        req, sel = scrape.parse_request({"url": self.LIST, "fields": ["text"]})
        out = await scrape.run_scrape(_firefox(MagicMock(url=self.LIST)), req, sel)
        click.assert_not_awaited()
        assert scrape_spies.calls == ["navigate", "expand", "capture"]
        assert scrape_spies.dismiss.await_count == 1
        # Same response keys as before AST-2023 — no click-related key added.
        assert set(out) == {"final_url", "text", "scrape_meta"}
        assert out["final_url"] == self.LIST

    @pytest.mark.asyncio
    async def test_click_href_captures_destination_after_list_page_steps(
        self, monkeypatch: pytest.MonkeyPatch, scrape_spies
    ) -> None:
        list_page, dest_page = MagicMock(url=self.LIST), MagicMock(url=self.DEST)

        async def _click(page, href):
            scrape_spies.calls.append("click")
            assert page is list_page and href == "/jobs/1"
            return dest_page

        monkeypatch.setattr(scrape, "click_and_follow", _click)
        req, sel = scrape.parse_request(
            {"url": self.LIST, "fields": ["text"], "wait_ready": True, "click_href": "/jobs/1"}
        )
        out = await scrape.run_scrape(_firefox(list_page), req, sel)
        # Expand / wait_ready are list-page steps; click precedes capture.
        assert scrape_spies.calls == ["navigate", "expand", "wait_ready", "click", "capture"]
        assert out["final_url"] == self.DEST
        assert self.DEST in out["text"] and self.LIST not in out["text"]
        # Second dismiss ran on the destination; meta ORs both attempts.
        assert scrape_spies.dismiss.await_args_list[1].args[0] is dest_page
        assert out["scrape_meta"]["cookies_dismissed"] is True
        assert out["scrape_meta"]["final_url"] == self.DEST
        assert set(out) == {"final_url", "text", "scrape_meta"}

    @pytest.mark.asyncio
    async def test_missing_target_maps_to_click_target_missing(
        self, monkeypatch: pytest.MonkeyPatch, scrape_spies
    ) -> None:
        monkeypatch.setattr(
            scrape, "click_and_follow", AsyncMock(side_effect=interact.ClickTargetMissing("nope"))
        )
        req, sel = scrape.parse_request({"url": self.LIST, "fields": ["text"], "click_href": "/x"})
        with pytest.raises(scrape.ScrapeError) as ei:
            await scrape.run_scrape(_firefox(MagicMock(url=self.LIST)), req, sel)
        assert ei.value.error_class == scrape.CLICK_TARGET_MISSING == "click_target_missing"

    @pytest.mark.asyncio
    async def test_other_click_failure_stays_scrape_failed(
        self, monkeypatch: pytest.MonkeyPatch, scrape_spies
    ) -> None:
        monkeypatch.setattr(
            scrape, "click_and_follow", AsyncMock(side_effect=RuntimeError("did not navigate"))
        )
        req, sel = scrape.parse_request({"url": self.LIST, "fields": ["text"], "click_href": "/x"})
        with pytest.raises(scrape.ScrapeError) as ei:
            await scrape.run_scrape(_firefox(MagicMock(url=self.LIST)), req, sel)
        assert ei.value.error_class == "scrape_failed"


# Branches: click_target_missing never retried (even on attempt 1); scrape_failed control retries.
class TestAst2023RetryDelay:
    @staticmethod
    def _worker() -> QueueWorker:
        return QueueWorker(MagicMock(), MagicMock(), worker_id="w-test", concurrency=1)

    def test_click_target_missing_not_retried(self) -> None:
        job = ClaimedJob(id="j1", request={}, attempts=1, max_attempts=5)
        assert self._worker()._retry_delay(job, scrape.CLICK_TARGET_MISSING) is None

    def test_scrape_failed_still_retried_control(self) -> None:
        job = ClaimedJob(id="j1", request={}, attempts=1, max_attempts=5)
        assert self._worker()._retry_delay(job, "scrape_failed") is not None
