"""Firefox lifecycle — pooled (AST-1725) or ephemeral (one process per scrape)."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncIterator, List, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from logging_util import get_logger
from scrape_debug import firefox_label, scrape_debug_event
from settings import settings

_log = get_logger(__name__)


@dataclass
class _BrowserSlot:
    """One Firefox process in the pool — fresh context per acquire."""

    slot_id: int
    browser: Optional[Browser] = None
    request_count: int = 0
    active_pages: int = 0
    recycle_pending: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class BrowserPool:
    """Pooled: up to W Firefox processes, fresh context per URL.

    Ephemeral (``settings.browser_per_request``): launch Firefox per scrape,
    close browser + context before returning.
    """

    def __init__(self) -> None:
        self._playwright = None
        self._playwright_cm = None
        self._slots: List[_BrowserSlot] = []
        self._pool_lock = asyncio.Lock()
        self._slot_available = asyncio.Condition(self._pool_lock)
        self._pool_size = settings.browser_pool_size
        self._max_contexts_per_browser = settings.max_contexts_per_browser
        self._recycle_after_n = settings.recycle_after_n

    async def start(self) -> None:
        self._playwright_cm = async_playwright()
        self._playwright = await self._playwright_cm.__aenter__()

    async def stop(self) -> None:
        if settings.browser_per_request:
            if self._playwright_cm is not None:
                try:
                    await self._playwright_cm.__aexit__(None, None, None)
                except Exception:
                    pass
                self._playwright_cm = None
                self._playwright = None
            return

        async with self._pool_lock:
            for slot in self._slots:
                async with slot.lock:
                    await self._close_slot_browser_best_effort(slot)
            self._slots.clear()
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
        async with self._pool_lock:
            slots = list(self._slots)
        for slot in slots:
            async with slot.lock:
                await self._recover_when_idle_locked(slot, reason)

    def _slot_needs_recover(self, slot: _BrowserSlot) -> bool:
        return slot.browser is not None and not self._browser_connected(slot.browser)

    def _slot_has_capacity(self, slot: _BrowserSlot) -> bool:
        if slot.recycle_pending:
            return False
        if slot.request_count >= self._recycle_after_n:
            return False
        if slot.active_pages >= self._max_contexts_per_browser:
            return False
        # Disconnected with in-flight pages: drain only — never assign new contexts.
        if self._slot_needs_recover(slot) and slot.active_pages > 0:
            return False
        return True

    def _pick_slot(self) -> Optional[_BrowserSlot]:
        candidates = [s for s in self._slots if self._slot_has_capacity(s)]
        if not candidates:
            return None
        return min(candidates, key=lambda s: s.active_pages)

    async def _acquire_slot(self) -> _BrowserSlot:
        async with self._pool_lock:
            while True:
                slot = self._pick_slot()
                if slot is not None:
                    slot.active_pages += 1
                    scrape_debug_event(
                        "slot_acquired",
                        firefox=firefox_label(slot.slot_id),
                        slot_id=slot.slot_id,
                        active_pages=slot.active_pages,
                    )
                    return slot
                if len(self._slots) < self._pool_size:
                    slot = _BrowserSlot(slot_id=len(self._slots))
                    self._slots.append(slot)
                    slot.active_pages += 1
                    scrape_debug_event(
                        "slot_created",
                        firefox=firefox_label(slot.slot_id),
                        slot_id=slot.slot_id,
                        pool_size=len(self._slots),
                    )
                    scrape_debug_event(
                        "slot_acquired",
                        firefox=firefox_label(slot.slot_id),
                        slot_id=slot.slot_id,
                        active_pages=slot.active_pages,
                    )
                    return slot
                scrape_debug_event(
                    "slot_wait",
                    pool_size=len(self._slots),
                    waiting_slots=len(self._slots),
                )
                await self._slot_available.wait()

    async def _abort_slot_acquire(self, slot: _BrowserSlot) -> None:
        async with self._pool_lock:
            slot.active_pages -= 1
            scrape_debug_event(
                "slot_acquire_aborted",
                firefox=firefox_label(slot.slot_id),
                slot_id=slot.slot_id,
                active_pages=slot.active_pages,
            )
            self._slot_available.notify_all()

    async def _release_slot(self, slot: _BrowserSlot) -> None:
        recover_reason: Optional[str] = None
        async with self._pool_lock:
            slot.request_count += 1
            slot.active_pages -= 1
            if slot.request_count >= self._recycle_after_n and slot.active_pages > 0:
                slot.recycle_pending = True
            if slot.active_pages == 0:
                if self._slot_needs_recover(slot):
                    slot.recycle_pending = True
                    recover_reason = "disconnected"
                elif slot.recycle_pending or slot.request_count >= self._recycle_after_n:
                    slot.recycle_pending = True
                    recover_reason = "recycle"
            scrape_debug_event(
                "slot_released",
                firefox=firefox_label(slot.slot_id),
                slot_id=slot.slot_id,
                active_pages=slot.active_pages,
                request_count=slot.request_count,
            )
            self._slot_available.notify_all()

        if recover_reason is not None:
            async with slot.lock:
                await self._recover_when_idle_locked(slot, recover_reason)

    async def _recover_slot_locked(self, slot: _BrowserSlot, reason: str) -> None:
        _log.warning(
            "telescope browser recover reason=%s slot_id=%d",
            reason,
            slot.slot_id,
        )
        scrape_debug_event(
            "firefox_recover",
            firefox=firefox_label(slot.slot_id),
            slot_id=slot.slot_id,
            reason=reason,
        )
        await self._close_slot_browser_best_effort(slot)
        slot.browser = await self._launch_firefox(slot)
        slot.request_count = 0
        slot.recycle_pending = False

    async def _recover_when_idle_locked(self, slot: _BrowserSlot, reason: str) -> None:
        """Count-based recycle must not close Firefox while other pages are in use."""
        if slot.active_pages > 0:
            slot.recycle_pending = True
            _log.info(
                "telescope recycle deferred reason=%s slot_id=%d active_pages=%d",
                reason,
                slot.slot_id,
                slot.active_pages,
            )
            return
        await self._recover_slot_locked(slot, reason)

    async def _launch_firefox(
        self,
        slot: Optional[_BrowserSlot] = None,
        *,
        ephemeral: bool = False,
    ) -> Browser:
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
                scrape_debug_event(
                    "firefox_launched",
                    firefox=firefox_label(
                        slot.slot_id if slot is not None else None,
                        ephemeral=ephemeral,
                    ),
                    slot_id=slot.slot_id if slot is not None else None,
                    browser_id=id(browser),
                    attempt=attempt,
                )
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

    async def _close_slot_browser_best_effort(self, slot: _BrowserSlot) -> None:
        if slot.browser is None:
            return
        browser_id = id(slot.browser)
        try:
            await slot.browser.close()
        except Exception:
            pass
        scrape_debug_event(
            "firefox_closed",
            firefox=firefox_label(slot.slot_id),
            slot_id=slot.slot_id,
            browser_id=browser_id,
        )
        slot.browser = None

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
            scrape_debug_event(
                "firefox_closed",
                firefox=firefox_label(None, ephemeral=True),
                browser_id=id(browser),
            )
            _log.info("telescope firefox closed ephemeral")

    def _browser_connected(self, browser: Optional[Browser]) -> bool:
        if browser is None:
            return False
        try:
            return browser.is_connected()
        except Exception:
            return False

    async def _ensure_slot_browser(self, slot: _BrowserSlot) -> bool:
        """Return True when the slot has a live browser; False to retry another slot."""
        async with slot.lock:
            if self._browser_connected(slot.browser):
                return True
            if slot.browser is not None:
                await self._recover_when_idle_locked(slot, "disconnected")
                return self._browser_connected(slot.browser)
            slot.browser = await self._launch_firefox(slot)
            return self._browser_connected(slot.browser)

    @asynccontextmanager
    async def _ephemeral_page(self) -> AsyncIterator[Page]:
        browser: Optional[Browser] = None
        context: Optional[BrowserContext] = None
        context_id: Optional[int] = None
        try:
            browser = await self._launch_firefox(ephemeral=True)
            context = await browser.new_context(viewport=settings.viewport)
            context_id = id(context)
            scrape_debug_event(
                "context_created",
                firefox=firefox_label(None, ephemeral=True),
                browser_id=id(browser),
                context_id=context_id,
            )
            page = await context.new_page()
            scrape_debug_event(
                "page_created",
                firefox=firefox_label(None, ephemeral=True),
                browser_id=id(browser),
                context_id=context_id,
                page_id=id(page),
            )
            yield page
        finally:
            if context_id is not None:
                scrape_debug_event(
                    "context_closed",
                    firefox=firefox_label(None, ephemeral=True),
                    browser_id=id(browser) if browser is not None else None,
                    context_id=context_id,
                )
            await self._close_ephemeral_best_effort(context=context, browser=browser)

    @asynccontextmanager
    async def _pooled_page(self) -> AsyncIterator[Page]:
        while True:
            slot = await self._acquire_slot()
            if not await self._ensure_slot_browser(slot):
                await self._abort_slot_acquire(slot)
                continue
            retry = False
            context: Optional[BrowserContext] = None
            context_id: Optional[int] = None
            browser_id: Optional[int] = None
            async with slot.lock:
                if slot.recycle_pending or not self._browser_connected(slot.browser):
                    retry = True
                else:
                    browser_id = id(slot.browser)
                    context = await slot.browser.new_context(
                        viewport=settings.viewport
                    )
                    context_id = id(context)
                    scrape_debug_event(
                        "context_created",
                        firefox=firefox_label(slot.slot_id),
                        slot_id=slot.slot_id,
                        browser_id=browser_id,
                        context_id=context_id,
                        active_pages=slot.active_pages,
                    )
                    page = await context.new_page()
                    scrape_debug_event(
                        "page_created",
                        firefox=firefox_label(slot.slot_id),
                        slot_id=slot.slot_id,
                        browser_id=browser_id,
                        context_id=context_id,
                        page_id=id(page),
                    )
            if retry:
                await self._abort_slot_acquire(slot)
                continue
            try:
                yield page
            finally:
                try:
                    if context is not None:
                        scrape_debug_event(
                            "context_closed",
                            firefox=firefox_label(slot.slot_id),
                            slot_id=slot.slot_id,
                            browser_id=browser_id,
                            context_id=context_id,
                        )
                        await context.close()
                except Exception:
                    pass
                await self._release_slot(slot)
            return

    @asynccontextmanager
    async def page(self) -> AsyncIterator[Page]:
        if settings.browser_per_request:
            async with self._ephemeral_page() as page:
                yield page
            return
        async with self._pooled_page() as page:
            yield page

    async def health_poke(self) -> bool:
        if settings.browser_per_request:
            async with self.page() as page:
                await page.goto(
                    "about:blank",
                    wait_until="domcontentloaded",
                    timeout=settings.page_goto_timeout_ms,
                )
            return True
        # Pooled: any live browser is enough — no context churn on health probes.
        async with self._pool_lock:
            return any(
                self._browser_connected(slot.browser) for slot in self._slots
            ) or self._playwright is not None
