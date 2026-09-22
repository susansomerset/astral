"""Firefox lifecycle — pooled (AST-1725) or ephemeral (one process per scrape)."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from logging_util import get_logger
from settings import settings

_log = get_logger(__name__)


class BrowserPool:
    """Pooled: one Firefox per replica, fresh context per URL.

    Ephemeral (``settings.browser_per_request``): launch Firefox per scrape,
    close browser + context before returning.
    """

    def __init__(self) -> None:
        self._playwright = None
        self._playwright_cm = None
        self._browser: Optional[Browser] = None
        self._lock = asyncio.Lock()
        self._request_count = 0
        self._recycle_after_n = settings.recycle_after_n
        self._active_pages = 0
        self._recycle_pending = False

    async def start(self) -> None:
        self._playwright_cm = async_playwright()
        self._playwright = await self._playwright_cm.__aenter__()
        if not settings.browser_per_request:
            await self._launch_pooled()

    async def stop(self) -> None:
        async with self._lock:
            if not settings.browser_per_request:
                await self._close_browser_best_effort()
            if self._playwright_cm is not None:
                try:
                    await self._playwright_cm.__aexit__(None, None, None)
                except Exception:
                    pass
                self._playwright_cm = None
                self._playwright = None

    async def recover(self, reason: str) -> None:
        if settings.browser_per_request:
            return
        async with self._lock:
            await self._recover_locked(reason)

    async def _recover_locked(self, reason: str) -> None:
        _log.warning("telescope browser recover reason=%s", reason)
        await self._close_browser_best_effort()
        await self._launch_pooled()
        self._request_count = 0
        self._recycle_pending = False

    async def _recover_when_idle_locked(self, reason: str) -> None:
        """Count-based recycle must not close Firefox while other pages are in use."""
        if self._active_pages > 0:
            self._recycle_pending = True
            _log.info(
                "telescope recycle deferred reason=%s active_pages=%d",
                reason,
                self._active_pages,
            )
            return
        await self._recover_locked(reason)

    async def _launch_firefox(self) -> Browser:
        assert self._playwright is not None
        last_err: Optional[Exception] = None
        for attempt in range(1, settings.launch_max_attempts + 1):
            try:
                browser = await self._playwright.firefox.launch(
                    headless=True,
                    timeout=settings.launch_timeout_ms,
                    firefox_user_prefs=settings.firefox_user_prefs,
                )
                _log.info("telescope firefox launched attempt=%d", attempt)
                return browser
            except Exception as e:
                last_err = e
                _log.warning(
                    "Firefox launch attempt %d/%d failed: %s: %s",
                    attempt,
                    settings.launch_max_attempts,
                    type(e).__name__,
                    e,
                )
                if attempt < settings.launch_max_attempts:
                    await asyncio.sleep(settings.launch_retry_delay_seconds)
        _log.exception(
            "telescope firefox launch failed after %d attempts\n  %s: %s",
            settings.launch_max_attempts,
            type(last_err).__name__ if last_err else "?",
            last_err,
        )
        raise RuntimeError(f"Firefox launch failed: {last_err}") from last_err

    async def _launch_pooled(self) -> None:
        self._browser = await self._launch_firefox()

    async def _close_browser_best_effort(self) -> None:
        if self._browser is None:
            return
        try:
            await self._browser.close()
        except Exception:
            pass
        self._browser = None

    async def _close_ephemeral_best_effort(
        self,
        *,
        context: Optional[BrowserContext],
        browser: Optional[Browser],
    ) -> None:
        if context is not None:
            try:
                await context.close()
            except Exception:
                pass
        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass
            _log.info("telescope firefox closed ephemeral")

    def _browser_connected(self) -> bool:
        if self._browser is None:
            return False
        try:
            return self._browser.is_connected()
        except Exception:
            return False

    @asynccontextmanager
    async def _ephemeral_page(self) -> AsyncIterator[Page]:
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        try:
            browser = await self._launch_firefox()
            context = await browser.new_context(viewport=settings.viewport)
            page = await context.new_page()
            yield page
        finally:
            await self._close_ephemeral_best_effort(context=context, browser=browser)

    @asynccontextmanager
    async def _pooled_page(self) -> AsyncIterator[Page]:
        # Concurrency is governed by dispatch batch_size on the platform — no local cap.
        async with self._lock:
            disconnected = not self._browser_connected()
            need_recycle = self._request_count >= self._recycle_after_n
            if disconnected:
                await self._recover_locked("disconnected")
            elif need_recycle or self._recycle_pending:
                await self._recover_when_idle_locked("recycle")
            assert self._browser is not None
            context = await self._browser.new_context(viewport=settings.viewport)
            page = await context.new_page()
            self._active_pages += 1
        try:
            yield page
        finally:
            try:
                await context.close()
            except Exception:
                pass
            async with self._lock:
                self._request_count += 1
                self._active_pages -= 1
                if self._active_pages == 0 and self._recycle_pending:
                    await self._recover_when_idle_locked("recycle")

    @asynccontextmanager
    async def page(self) -> AsyncIterator[Page]:
        if settings.browser_per_request:
            async with self._ephemeral_page() as page:
                yield page
            return
        async with self._pooled_page() as page:
            yield page

    async def health_poke(self) -> bool:
        async with self.page() as page:
            await page.goto(
                "about:blank",
                wait_until="domcontentloaded",
                timeout=settings.page_goto_timeout_ms,
            )
        if settings.browser_per_request:
            return True
        return self._browser_connected()
