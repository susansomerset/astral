"""BrowserPool lifecycle — deferred recycle while pages are in use."""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import AsyncMock, MagicMock

import pytest


def test_request_timeout_seconds_default() -> None:
    from telescope_config import REQUEST_TIMEOUT_SECONDS

    assert REQUEST_TIMEOUT_SECONDS == 120


def test_browser_per_request_default_is_true_for_science_experiment() -> None:
    from telescope_config import BROWSER_PER_REQUEST

    assert BROWSER_PER_REQUEST is True


@pytest.mark.asyncio
async def test_ephemeral_page_launches_and_closes_firefox(monkeypatch) -> None:
    import browser as browser_mod
    from browser import BrowserPool

    monkeypatch.setattr(
        browser_mod,
        "settings",
        replace(browser_mod.settings, browser_per_request=True),
    )

    pool = BrowserPool()
    pool._playwright = MagicMock()

    browser = MagicMock()
    browser.new_context = AsyncMock(
        return_value=MagicMock(
            new_page=AsyncMock(return_value=MagicMock()),
        )
    )
    launch_mock = AsyncMock(return_value=browser)
    pool._launch_firefox = launch_mock
    close_mock = AsyncMock()
    pool._close_ephemeral_best_effort = close_mock

    async with pool.page():
        pass

    launch_mock.assert_awaited_once()
    close_mock.assert_awaited_once()
    _, kwargs = close_mock.await_args
    assert kwargs["browser"] is browser


@pytest.mark.asyncio
async def test_recycle_deferred_while_active_pages() -> None:
    from browser import BrowserPool

    pool = BrowserPool()
    close_mock = AsyncMock()
    launch_mock = AsyncMock()
    pool._close_browser_best_effort = close_mock
    pool._launch_pooled = launch_mock

    async with pool._lock:
        pool._active_pages = 2
        await pool._recover_when_idle_locked("recycle")

    assert close_mock.await_count == 0
    assert pool._recycle_pending is True

    async with pool._lock:
        pool._active_pages = 0
        await pool._recover_when_idle_locked("recycle")

    assert close_mock.await_count == 1
    assert launch_mock.await_count == 1
    assert pool._recycle_pending is False


@pytest.mark.asyncio
async def test_disconnected_recover_does_not_defer() -> None:
    from browser import BrowserPool

    pool = BrowserPool()
    close_mock = AsyncMock()
    launch_mock = AsyncMock()
    pool._close_browser_best_effort = close_mock
    pool._launch_pooled = launch_mock

    async with pool._lock:
        pool._active_pages = 2
        await pool._recover_locked("disconnected")

    assert close_mock.await_count == 1
    assert launch_mock.await_count == 1
