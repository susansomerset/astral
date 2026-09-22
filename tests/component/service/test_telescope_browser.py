"""BrowserPool lifecycle — pool sizing, deferred recycle while pages are in use."""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import AsyncMock, MagicMock

import pytest


def test_request_timeout_seconds_default() -> None:
    from telescope_config import REQUEST_TIMEOUT_SECONDS

    assert REQUEST_TIMEOUT_SECONDS == 120


def test_pooled_mode_defaults() -> None:
    from telescope_config import (
        BROWSER_PER_REQUEST,
        BROWSER_POOL_SIZE,
        MAX_CONTEXTS_PER_BROWSER,
        RECYCLE_AFTER_N,
    )

    assert BROWSER_PER_REQUEST is False
    assert BROWSER_POOL_SIZE == 10
    assert MAX_CONTEXTS_PER_BROWSER == 20
    assert RECYCLE_AFTER_N == 50


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
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    slot = _BrowserSlot(slot_id=0)
    close_mock = AsyncMock()
    launch_mock = AsyncMock()
    pool._close_slot_browser_best_effort = close_mock
    pool._launch_firefox = launch_mock

    async with slot.lock:
        slot.active_pages = 2
        await pool._recover_when_idle_locked(slot, "recycle")

    assert close_mock.await_count == 0
    assert slot.recycle_pending is True

    async with slot.lock:
        slot.active_pages = 0
        await pool._recover_when_idle_locked(slot, "recycle")

    assert close_mock.await_count == 1
    assert launch_mock.await_count == 1
    assert slot.recycle_pending is False


@pytest.mark.asyncio
async def test_disconnected_recover_does_not_defer() -> None:
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    slot = _BrowserSlot(slot_id=0)
    close_mock = AsyncMock()
    launch_mock = AsyncMock(return_value=MagicMock())
    pool._close_slot_browser_best_effort = close_mock
    pool._launch_firefox = launch_mock

    async with slot.lock:
        slot.active_pages = 2
        await pool._recover_slot_locked(slot, "disconnected")

    assert close_mock.await_count == 1
    assert launch_mock.await_count == 1


@pytest.mark.asyncio
async def test_release_slot_recycles_when_idle_and_count_at_threshold() -> None:
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    pool._recycle_after_n = 3
    slot = _BrowserSlot(slot_id=0, active_pages=1, request_count=2)
    slot.browser = MagicMock()
    slot.browser.is_connected.return_value = True
    pool._slots = [slot]

    recover_mock = AsyncMock()
    pool._recover_when_idle_locked = recover_mock

    await pool._release_slot(slot)

    assert slot.request_count == 3
    assert slot.active_pages == 0
    assert slot.recycle_pending is True
    recover_mock.assert_awaited_once_with(slot, "recycle")


@pytest.mark.asyncio
async def test_release_slot_marks_recycle_pending_while_still_busy() -> None:
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    pool._recycle_after_n = 2
    slot = _BrowserSlot(slot_id=0, active_pages=2, request_count=1)
    pool._slots = [slot]

    recover_mock = AsyncMock()
    pool._recover_when_idle_locked = recover_mock

    await pool._release_slot(slot)

    assert slot.request_count == 2
    assert slot.active_pages == 1
    assert slot.recycle_pending is True
    recover_mock.assert_not_awaited()


def test_disconnected_slot_has_no_capacity_while_draining() -> None:
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    browser = MagicMock()
    browser.is_connected.return_value = False
    slot = _BrowserSlot(slot_id=0, browser=browser, active_pages=5)

    assert pool._slot_has_capacity(slot) is False


def test_disconnected_slot_idle_has_capacity_for_recover() -> None:
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    browser = MagicMock()
    browser.is_connected.return_value = False
    slot = _BrowserSlot(slot_id=0, browser=browser, active_pages=0)

    assert pool._slot_has_capacity(slot) is True


@pytest.mark.asyncio
async def test_ensure_slot_browser_defers_recover_while_active_pages() -> None:
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    browser = MagicMock()
    browser.is_connected.return_value = False
    slot = _BrowserSlot(slot_id=0, browser=browser, active_pages=3)
    recover_mock = AsyncMock()
    pool._recover_when_idle_locked = recover_mock

    ok = await pool._ensure_slot_browser(slot)

    assert ok is False
    recover_mock.assert_awaited_once_with(slot, "disconnected")


@pytest.mark.asyncio
async def test_acquire_slot_picks_least_loaded() -> None:
    from browser import BrowserPool, _BrowserSlot

    pool = BrowserPool()
    pool._max_contexts_per_browser = 20
    pool._recycle_after_n = 50
    pool._slots = [
        _BrowserSlot(slot_id=0, active_pages=5),
        _BrowserSlot(slot_id=1, active_pages=1),
    ]

    slot = await pool._acquire_slot()

    assert slot.slot_id == 1
    assert slot.active_pages == 2
