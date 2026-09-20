"""Browser interaction — navigate, cookies, expand, generic wait_ready."""

from __future__ import annotations

import time
from typing import Any, Dict

from logging_util import get_logger
from settings import settings

_log = get_logger(__name__)


async def navigate(page, url: str) -> None:
    _log.debug("Calling navigate: [url=%s]", url)
    await page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=settings.page_goto_timeout_ms,
    )
    await page.wait_for_timeout(500)
    _log.debug("Response from navigate: final_url=%s", page.url)


async def _try_dismiss_cookie_banner(page) -> bool:
    for selector in settings.cookie_dismiss_selectors:
        try:
            button = page.locator(selector).first
            if await button.is_visible(timeout=500):
                await button.click()
                await page.wait_for_timeout(500)
                _log.debug("cookie dismiss clicked selector=%s", selector)
                return True
        except Exception:
            continue
    return False


async def _try_dismiss_cookie_banner_fuzzy(page) -> bool:
    # Container patterns duplicated from platform html_cull banner_patterns
    result = await page.evaluate(
        """([containerPatterns, acceptPatterns]) => {
            const containers = Array.from(document.querySelectorAll('*')).filter(el => {
                const id = (el.getAttribute && el.getAttribute('id') || '').toLowerCase();
                const cls = (el.getAttribute && el.getAttribute('class') || '').toLowerCase();
                return containerPatterns.some(p => id.includes(p) || cls.includes(p));
            });
            for (const container of containers) {
                const buttons = container.querySelectorAll('button, [role="button"], a');
                for (const btn of buttons) {
                    const text = (btn.textContent || '').toLowerCase().trim();
                    const isAccept = acceptPatterns.some(p => text.includes(p));
                    const isVisible = btn.offsetParent !== null;
                    if (isAccept && isVisible) {
                        btn.click();
                        return true;
                    }
                }
            }
            return false;
        }""",
        [list(settings.cookie_banner_patterns), list(settings.cookie_fuzzy_accept_keywords)],
    )
    return bool(result)


async def dismiss_cookies(page) -> None:
    try:
        clicked = await _try_dismiss_cookie_banner(page)
        if not clicked:
            clicked = await _try_dismiss_cookie_banner_fuzzy(page)
        _log.debug("cookie dismiss result clicked=%s", clicked)
    except Exception as exc:
        _log.debug("cookie dismiss soft-fail %s: %s", type(exc).__name__, exc)


async def expand_page(page) -> None:
    _log.debug("Calling expand_page: []")
    initial_height = await page.evaluate("(document.body?.scrollHeight) ?? 0")
    if initial_height == 0:
        _log.debug("Response from expand_page: skipped empty body")
        return
    scroll_attempts = 0
    max_scrolls = 10
    while scroll_attempts < max_scrolls:
        await page.evaluate("window.scrollTo(0, (document.body?.scrollHeight) ?? 0)")
        await page.wait_for_timeout(1500)
        new_height = await page.evaluate("(document.body?.scrollHeight) ?? 0")
        if new_height == initial_height:
            break
        initial_height = new_height
        scroll_attempts += 1

    load_more_clicks = 0
    max_clicks = 20
    while load_more_clicks < max_clicks:
        try:
            load_more_btn = await page.query_selector(
                'button:has-text("Load More"), button:has-text("Show More"), a:has-text("Load More")'
            )
            if load_more_btn:
                await load_more_btn.click()
                await page.wait_for_timeout(1500)
                load_more_clicks += 1
            else:
                break
        except Exception:
            break

    await page.evaluate("window.scrollTo(0, 0)")
    _log.debug(
        "Response from expand_page: scrolls=%d clicks=%d",
        scroll_attempts,
        load_more_clicks,
    )


async def _visible_char_count(page) -> int:
    text = await page.evaluate(
        """() => {
            const body = document.body ? document.body.cloneNode(true) : null;
            if (!body) return 0;
            body.querySelectorAll('header, footer, nav, [role="banner"], [role="contentinfo"]').forEach(el => el.remove());
            body.querySelectorAll('style, script, noscript').forEach(el => el.remove());
            body.querySelectorAll('[hidden], [aria-hidden="true"], .hide, .hidden, .d-none, .visually-hidden, .sr-only, [style*="display:none"], [style*="display: none"]').forEach(el => el.remove());
            return (body.innerText || '').length;
        }"""
    )
    return int(text or 0)


async def wait_ready_generic(page) -> Dict[str, Any]:
    """Stability / min_chars only — no careers listing selectors."""
    max_wait_ms = settings.wait_ready_max_ms
    poll_ms = settings.wait_ready_poll_ms
    stability_polls = settings.wait_ready_stability_polls
    min_chars = settings.wait_ready_min_chars

    started = time.monotonic()
    stable_count = 0
    last_len = 0
    ready = False
    visible_chars = 0

    while True:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        if elapsed_ms >= max_wait_ms:
            break
        visible_chars = await _visible_char_count(page)
        if visible_chars >= min_chars and visible_chars == last_len:
            stable_count += 1
        else:
            stable_count = 0
        last_len = visible_chars
        if stable_count >= stability_polls:
            ready = True
            break
        await page.wait_for_timeout(poll_ms)

    wait_ms = int((time.monotonic() - started) * 1000)
    if visible_chars == 0:
        outcome = "empty"
    elif ready:
        outcome = "ready"
    else:
        outcome = "timeout"
    result = {
        "ready": ready,
        "outcome": outcome,
        "visible_chars": visible_chars,
        "wait_ms": wait_ms,
    }
    _log.debug("Response from wait_ready_generic: %s", result)
    return result
