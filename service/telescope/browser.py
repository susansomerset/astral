"""One Firefox per process — a fresh context per job.

The queue decides how much work this process takes on (WORKER_CONCURRENCY), so
there is no pool here: every job gets its own context in the one live Firefox.
All this module does is keep that Firefox alive:
  - launch it at startup,
  - relaunch it if it disconnects,
  - swap in a new one after RECYCLE_AFTER_N jobs (sheds memory creep). The old
    one keeps serving the jobs already on it and closes when the last one ends.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from logging_util import get_logger
from scrape_debug import (
    alloc_context_id,
    alloc_firefox_instance_id,
    bind_scrape_firefox,
    scrape_debug_event,
)
from settings import settings

_log = get_logger(__name__)


@dataclass(eq=False)  # identity hash — instances live in a set while draining
class _Instance:
    """One Firefox launch. Retired instances drain, then close."""

    browser: Browser
    firefox_id: str
    served: int = 0
    active: int = 0
    retired: bool = False

    def connected(self) -> bool:
        try:
            return self.browser.is_connected()
        except Exception:
            return False


class Firefox:
    def __init__(self) -> None:
        self._playwright = None
        self._playwright_cm = None
        self._current: Optional[_Instance] = None
        self._draining: set[_Instance] = set()
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        self._playwright_cm = async_playwright()
        self._playwright = await self._playwright_cm.__aenter__()
        await self._ensure_current()

    async def stop(self) -> None:
        async with self._lock:
            instances = [*self._draining, *([self._current] if self._current else [])]
            self._current = None
            self._draining.clear()
        for inst in instances:
            await self._close(inst)
        if self._playwright_cm is not None:
            try:
                await self._playwright_cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._playwright_cm = None
            self._playwright = None

    async def health_poke(self) -> bool:
        """True when a connected Firefox is ready (relaunching one if it died)."""
        inst = await self._ensure_current()
        return inst.connected()

    # -- lifecycle -----------------------------------------------------------

    async def _ensure_current(self) -> _Instance:
        async with self._lock:
            inst = self._current
            if inst is not None and not inst.retired and inst.connected():
                return inst
            if inst is not None:
                reason = "recycle" if inst.connected() else "disconnected"
                _log.info(
                    "telescope firefox %s retiring reason=%s served=%d active=%d",
                    inst.firefox_id,
                    reason,
                    inst.served,
                    inst.active,
                )
                scrape_debug_event(
                    "firefox_recover", firefox=inst.firefox_id, reason=reason
                )
                inst.retired = True
                if inst.active:
                    self._draining.add(inst)
                else:
                    await self._close(inst)
            self._current = await self._launch()
            return self._current

    async def _launch(self) -> _Instance:
        assert self._playwright is not None
        last_err: Optional[Exception] = None
        for attempt in range(1, settings.launch_max_attempts + 1):
            try:
                browser = await self._playwright.firefox.launch(
                    headless=True,
                    timeout=settings.launch_timeout_ms,
                    firefox_user_prefs=settings.firefox_user_prefs,
                )
                ff_id = alloc_firefox_instance_id()
                _log.info("telescope firefox %s launched attempt=%d", ff_id, attempt)
                scrape_debug_event("firefox_launched", firefox=ff_id, attempt=attempt)
                return _Instance(browser=browser, firefox_id=ff_id)
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
        _log.error(
            "telescope firefox launch failed after %d attempts\n  %s: %s",
            settings.launch_max_attempts,
            type(last_err).__name__ if last_err else "?",
            last_err,
        )
        raise RuntimeError(f"Firefox launch failed: {last_err}") from last_err

    async def _close(self, inst: _Instance) -> None:
        try:
            await inst.browser.close()
        except Exception:
            pass
        scrape_debug_event("firefox_closed", firefox=inst.firefox_id)
        _log.info("telescope firefox %s closed served=%d", inst.firefox_id, inst.served)

    # -- one job -------------------------------------------------------------

    @asynccontextmanager
    async def page(self) -> AsyncIterator[Page]:
        inst = await self._ensure_current()
        inst.active += 1
        inst.served += 1
        if inst.served >= settings.recycle_after_n:
            inst.retired = True  # the next job launches a replacement
        bind_scrape_firefox(inst.firefox_id)
        ctx_id = alloc_context_id()
        context: Optional[BrowserContext] = None
        try:
            scrape_debug_event("request_serving", firefox=inst.firefox_id, context=ctx_id)
            context = await inst.browser.new_context(viewport=settings.viewport)
            scrape_debug_event("context_created", firefox=inst.firefox_id, context=ctx_id)
            page = await context.new_page()
            scrape_debug_event("page_created")
            yield page
        finally:
            if context is not None:
                scrape_debug_event("context_closed")
                try:
                    await context.close()
                except Exception:
                    pass
                scrape_debug_event(
                    "context_recycled", context=ctx_id, firefox=inst.firefox_id
                )
            inst.active -= 1
            if inst.retired and inst.active == 0 and inst is not self._current:
                self._draining.discard(inst)
                await self._close(inst)
