"""BrowserPool lifecycle — deferred recycle while pages are in use."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_recycle_deferred_while_active_pages() -> None:
    from browser import BrowserPool

    pool = BrowserPool()
    close_mock = AsyncMock()
    launch_mock = AsyncMock()
    pool._close_browser_best_effort = close_mock
    pool._launch_locked = launch_mock

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
    pool._launch_locked = launch_mock

    async with pool._lock:
        pool._active_pages = 2
        await pool._recover_locked("disconnected")

    assert close_mock.await_count == 1
    assert launch_mock.await_count == 1
