"""
Playwright web scraping/automation module.

External service layer for Playwright operations.
Provides functions for extracting visible text from web pages with timing metrics.
"""

import os
import time
import re
import asyncio
from contextlib import asynccontextmanager
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, TypedDict
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response
from bs4 import BeautifulSoup
from src.utils.config import ASTRAL_CONFIG, PLAYWRIGHT_CONFIG
from src.utils.integration_io import require_controlled_external_io
from src.utils.logging import get_logger

_log = get_logger(__name__)

# Public handle types: core/callers use these; implementation may be swapped later.
BrowserSession = BrowserContext
PageHandle = Page

PLAYWRIGHT_INFRA_FAILURE_CLASSES = frozenset({
    "launch_failure",
    "launch_timeout",
    "channel_error",
    "context_closed",
    "connectivity_failure",
})


def classify_playwright_failure(exc: BaseException) -> str:
    """Map Playwright/Firefox exceptions to a stable failure class string."""
    msg = f"{type(exc).__name__} {exc}".lower()
    if "channel error" in msg:
        return "channel_error"
    if (
        "target page, context or browser has been closed" in msg
        or "browser has been closed" in msg
        or "browser closed" in msg
    ):
        return "context_closed"
    if "timeout" in msg and ("launch" in msg or "firefox.launch" in msg):
        return "launch_timeout"
    if "could not launch firefox" in msg:
        return "launch_failure"
    if "timeout" in msg and ("goto" in msg or "navigation" in msg):
        return "navigation_timeout"
    return "unknown"


def is_playwright_infra_failure(failure_class: str) -> bool:
    return failure_class in PLAYWRIGHT_INFRA_FAILURE_CLASSES


class PlaywrightInfraError(Exception):
    """Raised when headless browser launch or session I/O fails (infra, not site)."""

    def __init__(self, failure_class: str, detail: str) -> None:
        self.failure_class = failure_class
        self.detail = detail
        super().__init__(f"[{failure_class}] {detail}")


def _log_browser_env() -> None:  # pragma: no cover
    """Log environment and filesystem state for Playwright browser diagnostics (DEBUG level)."""
    browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "(not set)")
    _log.debug("PLAYWRIGHT_BROWSERS_PATH=%s", browsers_path)
    _log.debug("HOME=%s", os.environ.get("HOME", "(not set)"))
    _log.debug("CWD=%s", os.getcwd())
    _log.debug("MOZ_DISABLE_CONTENT_SANDBOX=%s", os.environ.get("MOZ_DISABLE_CONTENT_SANDBOX", "(not set)"))

    if browsers_path != "(not set)":
        bp = Path(browsers_path)
        if bp.exists():
            contents = list(bp.iterdir())
            _log.debug("Browsers dir exists: %s (%d entries)", bp, len(contents))
            for item in contents[:20]:
                kind = "dir" if item.is_dir() else "file"
                _log.debug("  %s  %s", kind, item.name)
        else:
            _log.warning("Browsers dir DOES NOT EXIST: %s", bp)

    default_path = Path.home() / ".cache" / "ms-playwright"
    if default_path.exists():
        contents = list(default_path.iterdir())
        _log.debug("Default browsers dir exists: %s (%d entries)", default_path, len(contents))
        for item in contents[:20]:
            kind = "dir" if item.is_dir() else "file"
            _log.debug("  %s  %s", kind, item.name)
    else:
        _log.debug("Default browsers dir does not exist: %s", default_path)


async def _launch_browser(pw, headless: bool = True) -> Browser:  # pragma: no cover
    """Launch Firefox browser with config-driven retries."""
    require_controlled_external_io("playwright._launch_browser")
    _log_browser_env()
    cfg = PLAYWRIGHT_CONFIG
    max_attempts = cfg["launch_max_attempts"]
    _log.debug("Launching Firefox (headless=%s)...", headless)
    last_err: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            browser = await pw.firefox.launch(
                headless=headless,
                timeout=cfg["launch_timeout_ms"],
                firefox_user_prefs=cfg["firefox_user_prefs"],
            )
            _log.debug("Firefox launched successfully (attempt %d)", attempt)
            return browser
        except Exception as e:
            last_err = e
            _log.warning(
                "Firefox launch attempt %d/%d failed: %s: %s",
                attempt,
                max_attempts,
                type(e).__name__,
                e,
            )
            if attempt < max_attempts:
                await asyncio.sleep(cfg["launch_retry_delay_seconds"])
    fc = classify_playwright_failure(last_err) if last_err else "launch_failure"
    detail = str(last_err) if last_err else "unknown launch error"
    raise PlaywrightInfraError(fc, detail) from last_err


async def _create_page_context(browser: Browser) -> Tuple[BrowserContext, Page]:  # pragma: no cover
    """Create browser context and page with standard viewport.
    
    Args:
        browser: Browser instance
        
    Returns:
        Tuple of (context, page)
    """
    context = await browser.new_context(viewport={"width": 1280, "height": 2000})
    page = await context.new_page()
    return context, page


class BatchBrowserSession:
    """Recoverable Playwright session for concurrent batch scrapes (AST-853)."""

    def __init__(
        self,
        headless: bool = True,
        viewport: Optional[Dict[str, int]] = None,
    ) -> None:
        self._headless = headless
        self._viewport = viewport or {"width": 1280, "height": 2000}
        self._pw = None
        self._playwright_cm = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._lock = asyncio.Lock()

    async def ensure_context(self) -> BrowserContext:
        async with self._lock:
            if self._context is not None and self._browser is not None:
                try:
                    if self._browser.is_connected():
                        return self._context
                except Exception:
                    pass
            await self._open_fresh_locked()
            assert self._context is not None
            return self._context

    async def _open_fresh_locked(self) -> None:
        if self._pw is None:
            self._playwright_cm = async_playwright()
            self._pw = await self._playwright_cm.__aenter__()
        self._browser = await _launch_browser(self._pw, headless=self._headless)
        self._context = await self._browser.new_context(viewport=self._viewport)

    async def recover(self, failure_class: str, reason: str) -> None:
        async with self._lock:
            _log.warning(
                "playwright batch session recover failure_class=%s reason=%s",
                failure_class,
                reason,
            )
            await self._close_handles_best_effort()
            await self._open_fresh_locked()

    async def _close_handles_best_effort(self) -> None:
        for closer in (
            (self._context, "close"),
            (self._browser, "close"),
        ):
            handle, method = closer
            if handle is None:
                continue
            try:
                await getattr(handle, method)()
            except Exception:
                pass
        self._context = None
        self._browser = None

    async def aclose(self) -> None:
        async with self._lock:
            await self._close_handles_best_effort()
            if self._playwright_cm is not None:
                try:
                    await self._playwright_cm.__aexit__(None, None, None)
                except Exception:
                    pass
                self._playwright_cm = None
                self._pw = None


@asynccontextmanager
async def create_batch_browser_session(  # pragma: no cover
    headless: bool = True,
    viewport: Optional[Dict[str, int]] = None,
):
    """Batch-scoped browser session with infra recovery between companies."""
    session = BatchBrowserSession(headless=headless, viewport=viewport)
    try:
        await session.ensure_context()
        yield session
    finally:
        await session.aclose()


class PageLoadArtifacts(TypedDict, total=False):
    """Artifacts collected during page navigation for clickables and vendor detection."""
    page: PageHandle
    initial_html: Optional[str]
    request_urls: List[str]
    frame_urls: List[str]


class VendorSignals(TypedDict, total=False):
    """Vendor detection signals with provenance for confidence reasoning."""
    vendor: Optional[str]               # 'hubspot', 'greenhouse', 'lever', 'workday', ...
    confidence: float                   # 0.0 - 1.0
    evidence: List[Dict[str, str]]      # provenance records: [{"source": "network", "url": "...", "vendor": "..."}, ...]
    canonical_job_url: Optional[str]    # best direct listings URL if known
    iframe_urls: List[str]              # if job list is embedded
    api_endpoints: List[str]            # if discoverable (JSON feeds)


class RoutingRecommendation(TypedDict, total=False):
    """Routing recommendation based on vendor signals."""
    route_to_url: Optional[str]         # URL to open next (preferred)
    route_to_iframe: Optional[str]      # frame URL to scrape
    fallback: bool                      # stay on current page and attempt generic extraction


async def _try_dismiss_cookie_banner(page: Page, debug: bool = False) -> bool:  # pragma: no cover
    """Attempt to dismiss cookie consent banners.
    
    Tries selectors from ASTRAL_CONFIG["cookie_dismiss_selectors"].
    Fast no-op if no banner present.
    
    Returns: True if a cookie button was clicked, False otherwise
    """
    cookie_selectors = ASTRAL_CONFIG.get("cookie_dismiss_selectors", [])
    
    if debug:
        _log.debug(f"[Cookie dismiss] Trying {len(cookie_selectors)} configured selectors...")
    
    for selector in cookie_selectors:
        try:
            button = page.locator(selector).first
            if await button.is_visible(timeout=500):
                if debug:
                    _log.debug(f"[Cookie dismiss] Found visible button with selector: {selector}")
                await button.click()
                await page.wait_for_timeout(500)
                if debug:
                    _log.debug(f"[Cookie dismiss] Clicked! Returning True")
                return True
        except Exception as e:
            if debug:
                _log.debug(f"[Cookie dismiss] Selector '{selector}' failed: {type(e).__name__}")
            continue
    
    if debug:
        _log.debug("[Cookie dismiss] No configured selectors matched")
    return False


async def _try_dismiss_cookie_banner_fuzzy(page: Page, debug: bool = False) -> bool:  # pragma: no cover
    """Fallback cookie dismissal using fuzzy text matching.
    
    Searches for visible buttons within cookie-related containers
    that have acceptance-like text. Scoped to reduce false positives.
    
    Uses ASTRAL_CONFIG for patterns (config-driven per code rules):
    - Container patterns from html_cull["banner_patterns"]
    - Accept keywords from cookie_fuzzy_accept_keywords
    
    Returns: True if a button was clicked, False otherwise
    """
    # Get patterns from config
    container_patterns = ASTRAL_CONFIG.get("html_cull", {}).get("banner_patterns", [])
    accept_keywords = ASTRAL_CONFIG.get("cookie_fuzzy_accept_keywords", [])
    
    if debug:
        _log.debug(f"[Cookie fuzzy] Container patterns: {container_patterns}")
        _log.debug(f"[Cookie fuzzy] Accept keywords: {accept_keywords}")
    
    # First, gather debug info about what containers and buttons exist
    if debug:
        debug_info = await page.evaluate('''([containerPatterns, acceptPatterns]) => {
            const results = {
                containersFound: [],
                buttonsInContainers: [],
                matchingButtons: []
            };
            
            // Find all potential cookie containers by id/class matching patterns
            // (el.className can be SVGAnimatedString on SVG elements, so coerce to string)
            const containers = Array.from(document.querySelectorAll('*')).filter(el => {
                const id = (el.getAttribute && el.getAttribute('id') || '').toLowerCase();
                const cls = (el.getAttribute && el.getAttribute('class') || '').toLowerCase();
                return containerPatterns.some(p => id.includes(p) || cls.includes(p));
            });
            
            results.containersFound = containers.map(el => ({
                tag: el.tagName,
                id: (el.getAttribute && el.getAttribute('id')) || '',
                class: (el.getAttribute && el.getAttribute('class')) || ''
            })).slice(0, 10);  // Limit to 10 for readability
            
            // Within containers, find buttons
            for (const container of containers) {
                const buttons = container.querySelectorAll('button, [role="button"], a');
                for (const btn of buttons) {
                    const text = (btn.textContent || '').toLowerCase().trim().substring(0, 50);
                    const isAccept = acceptPatterns.some(p => text.includes(p));
                    const isVisible = btn.offsetParent !== null;
                    
                    results.buttonsInContainers.push({
                        tag: btn.tagName,
                        text: text,
                        isAccept: isAccept,
                        isVisible: isVisible
                    });
                    
                    if (isAccept && isVisible) {
                        results.matchingButtons.push({ text: text });
                    }
                }
            }
            
            return results;
        }''', [container_patterns, accept_keywords])
        
        _log.debug(f"[Cookie fuzzy] Containers found: {len(debug_info.get('containersFound', []))}")
        for c in debug_info.get('containersFound', [])[:5]:
            _log.debug(f"[Cookie fuzzy]   - {c['tag']} id='{c['id']}' class='{c['class'][:50] if c['class'] else ''}'")
        _log.debug(f"[Cookie fuzzy] Buttons in containers: {len(debug_info.get('buttonsInContainers', []))}")
        for b in debug_info.get('buttonsInContainers', [])[:10]:
            _log.debug(f"[Cookie fuzzy]   - {b['tag']} text='{b['text']}' accept={b['isAccept']} visible={b['isVisible']}")
        _log.debug(f"[Cookie fuzzy] Matching buttons: {len(debug_info.get('matchingButtons', []))}")
    
    result = await page.evaluate('''([containerPatterns, acceptPatterns]) => {
        // Find all potential cookie containers by id/class matching patterns
        // (el.className can be SVGAnimatedString on SVG elements, so coerce via getAttribute)
        const containers = Array.from(document.querySelectorAll('*')).filter(el => {
            const id = (el.getAttribute && el.getAttribute('id') || '').toLowerCase();
            const cls = (el.getAttribute && el.getAttribute('class') || '').toLowerCase();
            return containerPatterns.some(p => id.includes(p) || cls.includes(p));
        });
        
        // Within containers, find acceptance buttons
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
    }''', [container_patterns, accept_keywords])
    
    if debug:
        _log.debug(f"[Cookie fuzzy] Result: {result}")
    
    return result


async def navigate_and_wait_for_ready(page: PageHandle, url: str, timeout: int = 60000) -> None:  # pragma: no cover
    """Navigate page to URL and wait for it to be ready.
    
    Uses 'load' (not networkidle) for reliable completion on pages with continuous
    background activity (analytics, websockets, etc.). Optional short networkidle
    attempt is best-effort only.
    
    Args:
        page: Page to navigate
        url: URL to navigate to
        timeout: Navigation timeout in ms (default 60000)
    """
    await page.goto(url, wait_until="load", timeout=timeout)
    await page.wait_for_timeout(1000)
    try:
        await page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass  # networkidle optional; load is sufficient


async def wait_for_page_ready_after_navigation(page: PageHandle, timeout: int = 10000) -> None:  # pragma: no cover
    """Wait for page to be ready after a navigation (e.g. post-click).
    
    Uses 'load' (not networkidle) so we don't hang on pages with continuous
    background requests.
    
    Args:
        page: Page that just navigated
        timeout: Max wait in ms (default 10000)
    """
    try:
        await page.wait_for_load_state("load", timeout=timeout)
    except Exception:
        pass  # load may have already fired
    await page.wait_for_timeout(2000)  # brief settle for JS


async def get_page(  # pragma: no cover
    context: Optional[BrowserSession] = None,
    url: Optional[str] = None,
    *,
    batch_session: Optional[BatchBrowserSession] = None,
) -> PageHandle:
    """Create a page from ``context`` or ``batch_session``; optionally navigate."""
    cfg = PLAYWRIGHT_CONFIG
    goto_timeout = cfg["page_goto_timeout_ms"]
    recovery_max = cfg["context_recovery_max_attempts"]
    last_err: Optional[Exception] = None

    for recovery in range(recovery_max + 1):
        page: Optional[PageHandle] = None
        try:
            if batch_session is not None:
                ctx = await batch_session.ensure_context()
            else:
                ctx = context
            if ctx is None:
                raise ValueError("get_page requires context or batch_session")
            page = await ctx.new_page()

            if not url or not str(url).strip():
                return page

            await page.goto(url, wait_until="load", timeout=goto_timeout)
            await page.wait_for_timeout(1000)

            await _try_dismiss_cookie_banner(page)

            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

            await page.wait_for_timeout(1000)
            return page
        except Exception as e:
            last_err = e
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass
            fc = classify_playwright_failure(e)
            if (
                batch_session is not None
                and is_playwright_infra_failure(fc)
                and recovery < recovery_max
            ):
                await batch_session.recover(fc, str(e))
                continue
            if is_playwright_infra_failure(fc):
                raise PlaywrightInfraError(fc, str(e)) from e
            raise

    raise PlaywrightInfraError("unknown", str(last_err)) from last_err  # pragma: no cover


async def get_page_with_artifacts(context: BrowserSession, url: str) -> PageLoadArtifacts:  # pragma: no cover
    """Create a page, navigate to URL, and return page with navigation artifacts.
    
    Captures initial HTML (response.text()), request URLs during load, and frame URLs
    after load. This is used for reliable clickable extraction and vendor detection.
    
    Args:
        context: BrowserSession to create page from
        url: URL to navigate to
        
    Returns:
        PageLoadArtifacts dict with page, initial_html, request_urls, frame_urls
        
    Raises:
        Exception: If navigation fails
    """
    page = await context.new_page()
    request_urls: List[str] = []
    
    # Attach request handler before navigation to capture request URLs
    def handle_request(request):
        request_urls.append(request.url)
    
    page.on("request", handle_request)
    
    try:
        # Navigate and capture response for initial HTML
        # Use 'load' (not networkidle) - reliable on pages with continuous background activity
        response: Optional[Response] = await page.goto(url, wait_until="load", timeout=60000)
        
        initial_html: Optional[str] = None
        if response is not None:
            try:
                initial_html = await response.text()
            except Exception:
                # Response body may be unavailable (redirects, errors, etc.)
                initial_html = None
        
        await page.wait_for_timeout(2000)  # Let content render
        
        # Try to dismiss cookie banners (fast no-op if none present)
        await _try_dismiss_cookie_banner(page)
        
        # Collect frame URLs after load settles
        frame_urls: List[str] = []
        for frame in page.frames:
            frame_url = frame.url
            # Skip empty, about:blank, and main frame (same as page URL)
            if frame_url and frame_url != "about:blank" and frame_url != url:
                frame_urls.append(frame_url)
        
    finally:
        # Remove request handler to avoid memory leaks
        page.remove_listener("request", handle_request)
    
    return PageLoadArtifacts(
        page=page,
        initial_html=initial_html,
        request_urls=request_urls,
        frame_urls=frame_urls
    )


@asynccontextmanager
async def create_browser_context(headless: bool = True, viewport: Optional[Dict[str, int]] = None):  # pragma: no cover
    """Create a browser context with automatic cleanup.
    
    Context manager that creates a Playwright browser context and automatically
    cleans up resources when done. The yielded context can be passed to extract
    functions to share cookies/storage across multiple operations.
    
    Args:
        headless: Whether to run browser in headless mode (default True)
        viewport: Optional viewport dict with 'width' and 'height' keys.
                 Defaults to {"width": 1280, "height": 2000}
        
    Yields:
        BrowserContext that can be passed to extract functions
        
    Example:
        async with create_browser_context() as ctx:
            text1 = await get_visible_text(url1, context=ctx)
            pages = await extract_site_page_list(url2, context=ctx)
            # Both calls share the same context (cookies/storage)
    """
    viewport_dict = viewport or {"width": 1280, "height": 2000}

    _log.debug("create_browser_context: starting async_playwright (headless=%s)", headless)
    async with async_playwright() as pw:
        browser = await _launch_browser(pw, headless=headless)
        context = await browser.new_context(viewport=viewport_dict)
        _log.debug("create_browser_context: context ready")
        try:
            yield context
        finally:
            _log.debug("create_browser_context: closing browser")
            await browser.close()


# ---- Public page/session API (wrappers so callers need not depend on Playwright types) ----

async def new_page(session: BrowserSession) -> PageHandle:  # pragma: no cover
    """Create a new page from the session. Caller must close it when done."""
    return await session.new_page()


async def close_page(page: PageHandle) -> None:  # pragma: no cover
    """Close the page and release resources."""
    await page.close()


async def check_connectivity(timeout: Optional[int] = None) -> bool:  # pragma: no cover
    """Quick DNS + HTTP check via Playwright. Returns True if the browser can reach the internet."""
    goto_timeout = timeout if timeout is not None else PLAYWRIGHT_CONFIG["connectivity_timeout_ms"]
    try:
        async with create_browser_context() as ctx:
            page = await ctx.new_page()
            try:
                await page.goto(
                    "https://www.google.com",
                    wait_until="commit",
                    timeout=goto_timeout,
                )
                return True
            finally:
                await page.close()
    except Exception as e:
        fc = classify_playwright_failure(e)
        _log.warning("check_connectivity failed failure_class=%s: %s", fc, e)
        return False


def get_page_url(page: PageHandle) -> str:
    """Return the current URL of the page."""
    return page.url


def get_frame_urls(page: PageHandle) -> List[str]:
    """Return list of iframe/frame URLs (excludes empty, about:blank, and main frame URL)."""
    frame_urls: List[str] = []
    for frame in page.frames:
        frame_url = frame.url
        if frame_url and frame_url != "about:blank" and frame_url != page.url:
            frame_urls.append(frame_url)
    return frame_urls


async def get_link_urls_from_page(page: PageHandle) -> List[str]:  # pragma: no cover
    """Return list of http(s) link hrefs from the page (a[href])."""
    return await page.evaluate('''() => {
        const links = Array.from(document.querySelectorAll('a[href]'));
        return links.map(a => a.href).filter(href => href && href.startsWith('http'));
    }''')


async def evaluate(page: PageHandle, script: str, *args: Any) -> Any:  # pragma: no cover
    """Run JS in the page context. Optional args are passed to the script."""
    return await page.evaluate(script, *args)


async def wait_for_timeout(page: PageHandle, milliseconds: int) -> None:  # pragma: no cover
    """Wait for the given number of milliseconds."""
    await page.wait_for_timeout(milliseconds)


# ---- Extract / navigate (public API uses PageHandle / BrowserSession) ----

async def extract_visible_text(page: PageHandle) -> Dict[str, Any]:  # pragma: no cover
    """Extract visible text from a web page using Playwright.
    
    Extracts visible text content from the page body. The page must already
    be loaded and navigated to the desired URL. This function does not navigate
    or close the page - the caller manages the page lifecycle.
    
    Note: Iframe content is NOT extracted here. Instead, iframe URLs are surfaced
    as clickable options in extract_page_clickables() so the agent can navigate
    to them directly for cleaner parsing.
    
    Args:
        page: Page object that has already been navigated to the target URL
        
    Returns:
        Dictionary containing:
            - text: str - visible text content from page body
            - url: str - the URL of the page (from page.url)
            
    Raises:
        Exception: If page evaluation fails
    """
    # Extract visible text from main page using JavaScript evaluation
    body_text = await page.evaluate('''() => {
        const body = document.body.cloneNode(true);
        body.querySelectorAll('header, footer, nav, [role="banner"], [role="contentinfo"]').forEach(el => el.remove());
        body.querySelectorAll('style, script, noscript').forEach(el => el.remove());
        // Strip elements hidden via attributes, inline styles, or common CSS framework classes
        // (cloned nodes are detached from the document so innerText ignores CSS — we must strip manually)
        body.querySelectorAll('[hidden], [aria-hidden="true"], .hide, .hidden, .d-none, .visually-hidden, .sr-only, [style*="display:none"], [style*="display: none"]').forEach(el => el.remove());
        return body.innerText;
    }''')
    
    return {
        "text": body_text,
        "url": page.url
    }


async def extract_page_scrape_contract(page: PageHandle) -> Dict[str, Any]:  # pragma: no cover
    """Raw visible text + nav URL list from one loaded page (AST-759 shared contract)."""
    vt = await extract_visible_text(page)
    nav_urls: List[str] = []
    nav_error: Optional[str] = None
    try:
        nav_urls = await extract_site_page_list(page=page, max_depth=1, verify=False) or []
    except Exception as e:
        nav_error = str(e)
    out: Dict[str, Any] = {
        "visible_text": vt.get("text") or "",
        "nav_urls": nav_urls,
        "final_url": vt.get("url") or page.url,
    }
    if nav_error:
        out["nav_error"] = nav_error
    return out


async def get_visible_text(  # pragma: no cover
    url: Optional[str] = None,
    *,
    context: Optional[BrowserSession] = None,
    page: Optional[PageHandle] = None,
    return_final_url: bool = False,
):
    """Extract visible text from a URL or existing page.

    Use URL only when you just need text and don't need to hold context/page open.
    Use context= when reusing a browser session (e.g. shared cookies).
    Use page= when you already have a page (e.g. from get_page_with_artifacts).

    Args:
        url: URL to load (required when page is not provided)
        context: Optional BrowserSession to use (creates one if omitted and url given)
        page: Optional PageHandle already navigated to target (url ignored if set)
        return_final_url: If True, return (text, final_url) tuple to detect redirects

    Returns:
        str (visible text) by default, or (str, str) tuple when return_final_url=True
    """
    def _out(result):
        text = result.get("text", "") or ""
        if return_final_url:
            return text, result.get("url", url or "")
        return text

    if page is not None:
        _log.debug("get_visible_text: using provided page (url=%s)", page.url)
        return _out(await extract_visible_text(page))
    if not url:
        return ("", "") if return_final_url else ""
    if context is not None:
        _log.debug("get_visible_text: using provided context for %s", url)
        pg = await get_page(context, url)
        try:
            return _out(await extract_visible_text(pg))
        finally:
            await pg.close()
    last_err: Optional[Exception] = None
    for attempt in range(2):
        _log.debug("get_visible_text: attempt %d/2 for %s", attempt + 1, url)
        try:
            async with create_browser_context() as ctx:
                pg = await get_page(ctx, url)
                try:
                    result = await extract_visible_text(pg)
                    text_len = len(result.get("text", "") or "")
                    _log.debug("get_visible_text: got %d chars from %s", text_len, url)
                    return _out(result)
                finally:
                    await pg.close()
        except Exception as e:
            _log.warning("get_visible_text: attempt %d failed: %s: %s", attempt + 1, type(e).__name__, e)
            last_err = e
            if "Could not launch any browser" in str(e):
                break
    raise last_err  # type: ignore[misc]


class _InternalClickableHTMLParser(HTMLParser):
    """Parser for extracting internal link text from HTML source.
    
    Finds <a href="/..."> and extracts text from innerText or <img alt="...">.
    Returns both text list (for display) and mapping (text -> href) for navigation.
    """
    def __init__(self) -> None:
        super().__init__()
        self._in_internal_a = False
        self._current_text_chunks: List[str] = []
        self._current_img_alt: Optional[str] = None
        self._current_href: Optional[str] = None
        self._results: List[str] = []
        self._href_map: Dict[str, str] = {}  # text -> href mapping

    @staticmethod  # pragma: no cover
    def _is_internal_href(href: Optional[str]) -> bool:  # pragma: no cover
        if not href:  # pragma: no cover
            return False  # pragma: no cover
        # internal means "/..." but not "//..." (protocol-relative)
        return href.startswith("/") and not href.startswith("//")  # pragma: no cover

    def handle_starttag(self, tag: str, attrs):  # pragma: no cover
        attrs_d = dict(attrs)  # pragma: no cover

        if tag.lower() == "a":  # pragma: no cover
            href = attrs_d.get("href")  # pragma: no cover
            if self._is_internal_href(href):  # pragma: no cover
                self._in_internal_a = True  # pragma: no cover
                self._current_text_chunks = []  # pragma: no cover
                self._current_img_alt = None  # pragma: no cover
                self._current_href = href  # Store href for this link  # pragma: no cover

        if self._in_internal_a and tag.lower() == "img":  # pragma: no cover
            alt = attrs_d.get("alt")  # pragma: no cover
            if alt and not self._current_img_alt:  # pragma: no cover
                self._current_img_alt = alt.strip()  # pragma: no cover

    def handle_data(self, data: str):  # pragma: no cover
        if self._in_internal_a and data:  # pragma: no cover
            s = data.strip()  # pragma: no cover
            if s:  # pragma: no cover
                self._current_text_chunks.append(s)  # pragma: no cover

    def handle_endtag(self, tag: str):  # pragma: no cover
        if tag.lower() == "a" and self._in_internal_a:  # pragma: no cover
            text = " ".join(self._current_text_chunks).strip()  # pragma: no cover
            if not text:  # pragma: no cover
                text = (self._current_img_alt or "").strip()  # pragma: no cover
            if text:  # pragma: no cover
                self._results.append(text)  # pragma: no cover
                # Store href mapping (normalize text for lookup)
                normalized_text = " ".join(text.split()).casefold()  # pragma: no cover
                if self._current_href:  # pragma: no cover
                    self._href_map[normalized_text] = self._current_href  # pragma: no cover
            self._in_internal_a = False  # pragma: no cover
            self._current_text_chunks = []  # pragma: no cover
            self._current_img_alt = None  # pragma: no cover
            self._current_href = None  # pragma: no cover

    def results(self) -> List[str]:
        return self._results
    
    def href_map(self) -> Dict[str, str]:
        """Return mapping from normalized text to href."""
        return self._href_map.copy()


def _parse_html_for_internal_clickables(html: str) -> Tuple[List[str], Dict[str, str]]:
    """Parse HTML source for internal links with text/alt.
    
    Args:
        html: HTML source string
        
    Returns:
        Tuple of (list of text strings, mapping from normalized text to href)
    """
    p = _InternalClickableHTMLParser()
    p.feed(html)
    return p.results(), p.href_map()


def detect_vendor(artifacts: PageLoadArtifacts) -> VendorSignals:
    """Detect ATS/vendor integration from page artifacts.
    
    Checks in priority order: network requests > frame URLs > initial HTML > DOM.
    Rule-based and auditable - returns vendor name, confidence, and evidence.
    
    Args:
        artifacts: PageLoadArtifacts with request_urls, frame_urls, initial_html, page
        
    Returns:
        VendorSignals with vendor, confidence, evidence, canonical_job_url, iframe_urls
    """
    evidence: List[Dict[str, str]] = []
    vendor: Optional[str] = None
    confidence = 0.0
    canonical_job_url: Optional[str] = None
    iframe_urls: List[str] = []
    api_endpoints: List[str] = []
    
    request_urls = artifacts.get("request_urls", [])
    frame_urls = artifacts.get("frame_urls", [])
    initial_html = artifacts.get("initial_html")
    page = artifacts.get("page")
    
    # Vendor fingerprints: domain patterns -> vendor name
    vendor_patterns = {
        "greenhouse": [
            "greenhouse.io",
            "boards.greenhouse.io",
        ],
        "lever": [
            "lever.co",
            "jobs.lever.co",
        ],
        "workday": [
            "myworkdayjobs.com",
            "wd[0-9].myworkdayjobs.com",
        ],
        "icims": [
            "icims.com",
        ],
        "smartrecruiters": [
            "smartrecruiters.com",
        ],
        "ashby": [
            "ashbyhq.com",
            "jobs.ashbyhq.com",
        ],
        "jobvite": [
            "jobvite.com",
        ],
        "taleo": [
            "taleo.net",
        ],
    }
    
    # 1. Check network request URLs (highest signal)
    for url in request_urls:  # pragma: no cover
        try:  # pragma: no cover
            parsed = urlparse(url)  # pragma: no cover
            hostname = parsed.hostname or ""  # pragma: no cover
            hostname_lower = hostname.lower()  # pragma: no cover
            
            for ven, patterns in vendor_patterns.items():  # pragma: no cover
                for pattern in patterns:  # pragma: no cover
                    # Simple substring match (can be enhanced with regex for patterns like wd[0-9])
                    if pattern.replace("[0-9]", "") in hostname_lower or pattern in hostname_lower:  # pragma: no cover
                        if not vendor or vendor == ven:  # pragma: no cover
                            vendor = ven  # pragma: no cover
                            confidence = max(confidence, 0.9)  # pragma: no cover
                            evidence.append({  # pragma: no cover
                                "source": "network",  # pragma: no cover
                                "url": url,  # pragma: no cover
                                "vendor": ven,  # pragma: no cover
                                "pattern": pattern  # pragma: no cover
                            })  # pragma: no cover
                            
                            # Extract canonical job URL for known vendors
                            if ven == "greenhouse" and "boards.greenhouse.io" in hostname_lower:  # pragma: no cover
                                # Extract company from URL: https://boards.greenhouse.io/{company}
                                path_parts = [p for p in parsed.path.split("/") if p]  # pragma: no cover
                                if path_parts:  # pragma: no cover
                                    canonical_job_url = f"https://boards.greenhouse.io/{path_parts[0]}"  # pragma: no cover
                            
                            elif ven == "lever" and "jobs.lever.co" in hostname_lower:  # pragma: no cover
                                path_parts = [p for p in parsed.path.split("/") if p]  # pragma: no cover
                                if path_parts:  # pragma: no cover
                                    canonical_job_url = f"https://jobs.lever.co/{path_parts[0]}"  # pragma: no cover
        except Exception:  # pragma: no cover
            continue  # pragma: no cover
    
    # 2. Check frame URLs (strong signal, especially for HubSpot)
    for frame_url in frame_urls:
        try:
            parsed = urlparse(frame_url)
            hostname = parsed.hostname or ""
            hostname_lower = hostname.lower()
            
            # HubSpot frame pattern: hs-web-interactive, hs-sites-*
            if "hs-web-interactive" in hostname_lower or "hs-sites" in hostname_lower:
                vendor = "hubspot"
                confidence = max(confidence, 0.85)
                evidence.append({
                    "source": "frame",
                    "url": frame_url,
                    "vendor": "hubspot"
                })
                iframe_urls.append(frame_url)
            
            # Check other vendors in frames
            for ven, patterns in vendor_patterns.items():
                for pattern in patterns:
                    if pattern.replace("[0-9]", "") in hostname_lower:
                        vendor = ven
                        confidence = max(confidence, 0.8)
                        evidence.append({
                            "source": "frame",
                            "url": frame_url,
                            "vendor": ven
                        })
                        iframe_urls.append(frame_url)  # pragma: no cover
        except Exception:  # pragma: no cover
            continue  # pragma: no cover
    
    # 3. Check initial HTML (medium signal: script src, container IDs/classes, meta tags)
    if initial_html:  # pragma: no cover
        html_lower = initial_html.lower()  # pragma: no cover
        
        # HubSpot fingerprints
        if "hubspot" in html_lower or "hs-" in html_lower or "data-hubspot" in html_lower:  # pragma: no cover
            if vendor != "hubspot":  # pragma: no cover
                vendor = "hubspot"  # pragma: no cover
                confidence = max(confidence, 0.7)  # pragma: no cover
                evidence.append({  # pragma: no cover
                    "source": "initial_html",  # pragma: no cover
                    "vendor": "hubspot",  # pragma: no cover
                    "pattern": "hubspot/hs- markers"  # pragma: no cover
                })  # pragma: no cover
        
        # Greenhouse fingerprints
        if "greenhouse" in html_lower:  # pragma: no cover
            if not vendor or vendor == "greenhouse":  # pragma: no cover
                vendor = "greenhouse"  # pragma: no cover
                confidence = max(confidence, 0.7)  # pragma: no cover
                evidence.append({  # pragma: no cover
                    "source": "initial_html",  # pragma: no cover
                    "vendor": "greenhouse",  # pragma: no cover
                    "pattern": "greenhouse markers"  # pragma: no cover
                })  # pragma: no cover
        
        # Lever fingerprints
        if "lever.co" in html_lower or "leverhq" in html_lower:  # pragma: no cover
            if not vendor or vendor == "lever":  # pragma: no cover
                vendor = "lever"  # pragma: no cover
                confidence = max(confidence, 0.7)  # pragma: no cover
                evidence.append({  # pragma: no cover
                    "source": "initial_html",
                    "vendor": "lever",
                    "pattern": "lever markers"
                })
    
    return VendorSignals(
        vendor=vendor,
        confidence=confidence,
        evidence=evidence,
        canonical_job_url=canonical_job_url,
        iframe_urls=iframe_urls,
        api_endpoints=api_endpoints
    )


def recommend_routing(vendor_signals: VendorSignals, current_url: str) -> RoutingRecommendation:
    """Generate routing recommendation based on vendor detection.
    
    Priority: canonical_job_url > iframe_url > fallback to current page.
    
    Args:
        vendor_signals: VendorSignals from detect_vendor()
        current_url: Current page URL for fallback
        
    Returns:
        RoutingRecommendation with route_to_url, route_to_iframe, or fallback
    """
    # 1. Prefer canonical job board URL (best option)
    if vendor_signals.get("canonical_job_url"):
        return RoutingRecommendation(
            route_to_url=vendor_signals["canonical_job_url"],
            route_to_iframe=None,
            fallback=False
        )
    
    # 2. If no canonical URL but we have iframe URLs, route to iframe
    iframe_urls = vendor_signals.get("iframe_urls", [])
    if iframe_urls:
        # Prefer first iframe URL (can be enhanced with content detection)
        return RoutingRecommendation(
            route_to_url=None,
            route_to_iframe=iframe_urls[0],
            fallback=False
        )
    
    # 3. Fallback: stay on current page
    return RoutingRecommendation(
        route_to_url=None,
        route_to_iframe=None,
        fallback=True
    )


async def extract_page_clickables(page: PageHandle, initial_html: Optional[str] = None) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:  # pragma: no cover
    """Extract visible clickable element text from a web page using Playwright.
    
    Extracts text content from visible clickable elements (links) that have
    internal hrefs (relative URLs starting with "/"). The page must already be
    loaded and navigated to the desired URL. This function does not navigate or
    close the page - the caller manages the page lifecycle.
    
    Uses priority merge: response_html > dom_early > dom_late to ensure placeholder
    links are captured before widgets replace them with iframes.
    
    Args:
        page: Page object that has already been navigated to the target URL
        initial_html: Optional initial HTML from response.text() (captured before DOM modifications)
        
    Returns:
        Tuple of:
        - List of clickable element text strings (trimmed, non-empty, visible only).
          Text is extracted from textContent, image alt attributes, or aria-label/title.
        - Mapping dict from normalized text to clickable metadata: {
            'href': str (if available),
            'source': 'response_html' | 'dom_early' | 'dom_late'
          }
        
    Raises:
        Exception: If page evaluation fails
    """
    # Extract clickable text BEFORE widgets replace links with iframes
    # HubSpot and other widget systems often replace placeholder links with iframes
    # So we need to capture the text early, before the replacement happens
    
    # First, try to extract from placeholder links that might get replaced
    early_clickables = await page.evaluate('''() => {
        const earlyTexts = [];
        
        // Helper to check visibility
        function isVisible(el) {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && 
                   style.visibility !== 'hidden' && 
                   style.opacity !== '0' &&
                   el.offsetParent !== null;
        }
        
        // Helper to extract text from element
        function extractText(el) {
            const img = el.querySelector('img');
            let text = '';
            
            if (img) {
                text = img.getAttribute('alt')?.trim() || '';
                if (!text) {
                    const clone = el.cloneNode(true);
                    clone.querySelectorAll('img').forEach(i => i.remove());
                    text = clone.textContent?.trim() || '';
                }
            } else {
                text = el.textContent?.trim() || '';
            }
            
            if (!text) {
                text = el.getAttribute('aria-label')?.trim() || 
                       el.getAttribute('title')?.trim() || '';
            }
            
            return text;
        }
        
        // 1. Extract from anchor links (internal paths AND anchor links)
        const links = Array.from(document.querySelectorAll('a[href]'));
        links.forEach(link => {
            const hrefAttr = link.getAttribute('href');
            // Include internal hrefs (/) and anchor links (#)
            const isInternalHref = hrefAttr && hrefAttr.length > 0 && hrefAttr[0] === '/' && (hrefAttr.length === 1 || hrefAttr[1] !== '/');
            const isAnchorLink = hrefAttr && hrefAttr.startsWith('#');
            
            if (!isInternalHref && !isAnchorLink) return;
            if (!isVisible(link)) return;
            
            const text = extractText(link);
            if (text) {
                earlyTexts.push(text);
            }
        });
        
        // 2. Extract from button elements and elements with role="button"
        const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]'));
        buttons.forEach(btn => {
            if (!isVisible(btn)) return;
            
            let text = '';
            if (btn.tagName === 'INPUT') {
                text = btn.value?.trim() || btn.getAttribute('aria-label')?.trim() || '';
            } else {
                text = extractText(btn);
            }
            
            if (text) {
                earlyTexts.push(text);
            }
        });
        
        return earlyTexts;
    }''')
    
    # Now wait for dynamic content to load (widgets may replace links, but we already captured text)
    try:
        await page.wait_for_load_state('networkidle', timeout=5000)
    except Exception:
        # Fallback: wait a short time for any remaining dynamic content
        await page.wait_for_timeout(2000)
    
    
    debug_info = await page.evaluate('''() => {
        const debugData = [];
        const visibleClickableTexts = [];
        
        // Helper to check visibility
        function isVisible(el) {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && 
                   style.visibility !== 'hidden' && 
                   style.opacity !== '0' &&
                   el.offsetParent !== null;
        }
        
        // Helper to extract text from element
        function extractText(el) {
            const img = el.querySelector('img');
            let text = '';
            
            if (img) {
                text = img.getAttribute('alt')?.trim() || '';
                if (!text) {
                    const clone = el.cloneNode(true);
                    clone.querySelectorAll('img').forEach(i => i.remove());
                    text = clone.textContent?.trim() || '';
                }
            } else {
                text = el.textContent?.trim() || '';
            }
            
            if (!text) {
                text = el.getAttribute('aria-label')?.trim() || 
                       el.getAttribute('title')?.trim() || '';
            }
            
            return text;
        }
        
        // 1. Get all <a> tags with href attributes
        const links = Array.from(document.querySelectorAll('a[href]'));
        
        links.forEach(link => {
            const hrefAttr = link.getAttribute('href');
            const debugEntry = {
                type: 'link',
                href: hrefAttr,
                isVisible: false,
                extractedText: null,
                included: false,
                reason: ''
            };
            
            // Include internal hrefs (/) and anchor links (#)
            const isInternalHref = hrefAttr && hrefAttr.length > 0 && hrefAttr[0] === '/' && (hrefAttr.length === 1 || hrefAttr[1] !== '/');
            const isAnchorLink = hrefAttr && hrefAttr.startsWith('#');
            
            if (!isInternalHref && !isAnchorLink) {
                debugEntry.reason = 'Not internal or anchor href';
                debugData.push(debugEntry);
                return;
            }
            
            debugEntry.isVisible = isVisible(link);
            if (!debugEntry.isVisible) {
                debugEntry.reason = 'Not visible';
                debugData.push(debugEntry);
                return;
            }
            
            const text = extractText(link);
            debugEntry.extractedText = text;
            
            if (text) {
                visibleClickableTexts.push(text);
                debugEntry.included = true;
                debugEntry.reason = 'Included';
            } else {
                debugEntry.reason = 'No text extracted';
            }
            
            debugData.push(debugEntry);
        });
        
        // 2. Get button elements and elements with role="button"
        const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]'));
        buttons.forEach(btn => {
            const debugEntry = {
                type: 'button',
                tagName: btn.tagName,
                isVisible: false,
                extractedText: null,
                included: false,
                reason: ''
            };
            
            debugEntry.isVisible = isVisible(btn);
            if (!debugEntry.isVisible) {
                debugEntry.reason = 'Not visible';
                debugData.push(debugEntry);
                return;
            }
            
            let text = '';
            if (btn.tagName === 'INPUT') {
                text = btn.value?.trim() || btn.getAttribute('aria-label')?.trim() || '';
            } else {
                text = extractText(btn);
            }
            debugEntry.extractedText = text;
            
            if (text) {
                visibleClickableTexts.push(text);
                debugEntry.included = true;
                debugEntry.reason = 'Included';
            } else {
                debugEntry.reason = 'No text extracted';
            }
            
            debugData.push(debugEntry);
        });
        
        return {
            clickables: visibleClickableTexts,
            debug: debugData
        };
    }''')
    
    clickable_texts = debug_info.get('clickables', [])
    debug_data = debug_info.get('debug', [])
    
    # Merge with priority: response_html > early DOM > late DOM
    # Deduplicate by normalized text (whitespace collapsed, casefolded)
    _ws = re.compile(r"\s+")
    
    def _norm(s: str) -> str:
        """Normalize text for deduplication (collapse whitespace, casefold)."""
        return _ws.sub(" ", s).strip().casefold()
    
    ordered_sources: List[Tuple[List[str], str]] = []  # (clickables, source_label)
    clickable_map: Dict[str, Dict[str, Any]] = {}  # normalized_text -> {href, source}
    
    # 1. Parse initial HTML from response (highest priority)
    if initial_html:
        html_clickables, html_href_map = _parse_html_for_internal_clickables(initial_html)
        ordered_sources.append((html_clickables, 'response_html'))
        # Add href mappings from response HTML
        for norm_text, href in html_href_map.items():
            if norm_text not in clickable_map:
                clickable_map[norm_text] = {'href': href, 'source': 'response_html'}
    
    # 2. Early DOM snapshot (captured before widget replacement)
    ordered_sources.append((early_clickables, 'dom_early'))
    
    # 3. Late DOM snapshot (after networkidle)
    ordered_sources.append((clickable_texts, 'dom_late'))
    
    # Merge with deduplication, preserving priority order
    seen: set[str] = set()
    all_clickables: List[str] = []
    for lst, source_label in ordered_sources:
        for t in lst:
            k = _norm(t)
            if not k or k in seen:
                continue
            seen.add(k)
            all_clickables.append(t)
            # Track source if not already set (prioritize response_html)
            # If source is response_html, href should already be in map from parser
            if k not in clickable_map:
                clickable_map[k] = {'href': None, 'source': source_label}
    
    return all_clickables, clickable_map


def _cull_html(html: str) -> str:  # pragma: no cover
    """Cull HTML to keep only explicitly allowed tag types for job metadata extraction.
    
    Uses explicit inclusion: only tags in the allowed_tags list are kept. All other tags
    are removed (unwrapped) while preserving their text content. This aggressive culling
    significantly reduces HTML size by removing non-essential elements.
    
    Special exception: img tags are kept only if they have alt text or class attribute,
    and only those attributes (alt, class) are retained - image content is not included.
    
    Still removes: scripts, styles, meta tags, link tags, svg, hidden elements, and banner patterns.
    Strips noisy attributes (style, on*, srcset) while preserving job-relevant ones (href, id, class, data-*, aria-*).
    
    Deterministic: same input produces same output (for cache consistency).
    
    Configuration is read directly from ASTRAL_CONFIG["html_cull"] in src/utils/config.py.
    
    Args:
        html: Full HTML string from page
    
    Returns:
        Culled HTML string containing only allowed tag types with text content preserved
    """
    from bs4 import Comment
    
    # Get configuration from centralized config (with defensive None checks)
    if ASTRAL_CONFIG is None:
        raise ValueError("ASTRAL_CONFIG is None in _cull_html")
    
    html_cull_config = ASTRAL_CONFIG.get("html_cull")
    if html_cull_config is None:
        raise ValueError("ASTRAL_CONFIG['html_cull'] is None in _cull_html")
    
    if not isinstance(html_cull_config, dict):
        raise ValueError(f"ASTRAL_CONFIG['html_cull'] is not a dict, got {type(html_cull_config)}")
    
    # Fail fast if required keys missing
    if "allowed_tags" not in html_cull_config:
        raise ValueError("ASTRAL_CONFIG['html_cull']['allowed_tags'] is missing")
    if "banner_patterns" not in html_cull_config:
        raise ValueError("ASTRAL_CONFIG['html_cull']['banner_patterns'] is missing")
    if "strip_attributes" not in html_cull_config:
        raise ValueError("ASTRAL_CONFIG['html_cull']['strip_attributes'] is missing")
    if "strip_on_attrs" not in html_cull_config:
        raise ValueError("ASTRAL_CONFIG['html_cull']['strip_on_attrs'] is missing")
    # Get configuration values directly from config
    allowed_tags = set(html_cull_config["allowed_tags"])  # Use set for O(1) lookup
    banner_patterns = html_cull_config["banner_patterns"]
    strip_attrs_list = html_cull_config["strip_attributes"]
    strip_on_attrs = html_cull_config["strip_on_attrs"]
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract body tag first - we only cull body content, not head/html wrappers
    body_tag = soup.find('body')
    if body_tag is None:
        # Fallback: if no body tag, use the whole document
        body_soup = soup
    else:
        # Extract just the body's inner contents (not the body tag itself)
        body_contents = ''.join(str(child) for child in body_tag.children)
        body_soup = BeautifulSoup(body_contents, 'html.parser')
    
    # Use body_soup for all culling operations
    soup = body_soup
    
    # Remove script tags (including JSON blobs like __NEXT_DATA__)
    for script in soup.find_all('script'):
        script.decompose()
    
    # Remove style tags
    for style in soup.find_all('style'):
        style.decompose()
    
    # Remove noscript
    for noscript in soup.find_all('noscript'):
        noscript.decompose()
    
    # Remove meta tags
    for meta in soup.find_all('meta'):
        meta.decompose()
    
    # Remove link tags (stylesheets, icons, prefetch, etc.)
    for link in soup.find_all('link'):
        link.decompose()
    
    # Remove HTML comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()
    
    # Remove large SVG blocks (icon sprites are often huge and not job-relevant)
    for svg in soup.find_all('svg'):
        svg.decompose()
    
    # Special handling for img tags: only keep if they have alt or class, and only keep those attributes
    for img in soup.find_all('img'):
        has_alt = img.get('alt') is not None and img.get('alt') != ''
        has_class = img.get('class') is not None
        if has_alt or has_class:
            # Keep the img tag but strip all attributes except alt and class
            attrs_to_remove = []
            for attr in img.attrs:
                if attr not in ['alt', 'class']:
                    attrs_to_remove.append(attr)
            for attr in attrs_to_remove:
                del img.attrs[attr]
        else:
            # Remove img tags without alt or class
            img.decompose()
    
    # Explicit inclusion: unwrap all tags not in allowed_tags list
    # Use multiple passes to handle nested structures (unwrap from deepest to shallowest)
    # Process until no more non-allowed tags remain
    # Note: img tags are handled separately above, so exclude them from unwrapping
    max_passes = 10  # Safety limit to prevent infinite loops
    for pass_num in range(max_passes):
        # Find all elements that are not in allowed_tags (excluding img, which is handled separately)
        non_allowed = [elem for elem in soup.find_all(True) if elem.name not in allowed_tags and elem.name != 'img']
        if not non_allowed:
            break  # All remaining tags are allowed or already handled
        # Unwrap each non-allowed tag (preserves children and text content)
        for elem in non_allowed:
            try:
                elem.unwrap()
            except Exception:
                # If unwrap fails (e.g., element is already unwrapped), decompose instead
                try:
                    elem.decompose()
                except Exception:
                    pass  # Silently skip if decomposition also fails
    
    # Remove hidden elements (aria-hidden, hidden attribute, display:none, hidden CSS classes)
    # Collect elements to decompose first, then decompose after iteration (avoid modifying tree during iteration)
    hidden_class_patterns = html_cull_config.get("hidden_class_patterns", [])
    elements_to_decompose = []
    elements_to_process = []
    
    all_elems = list(soup.find_all(True))  # Convert to list to avoid iteration issues
    
    for elem in all_elems:
        if elem is None:
            continue
        if not hasattr(elem, 'get'):
            continue
        
        # Check aria-hidden
        if elem.get('aria-hidden') == 'true':
            elements_to_decompose.append(elem)
            continue
        
        # Check hidden attribute
        if elem.get('hidden') is not None:
            elements_to_decompose.append(elem)
            continue
        
        # Check inline style for display:none
        style_attr = elem.get('style', '')
        if 'display:none' in style_attr or 'display: none' in style_attr:
            elements_to_decompose.append(elem)
            continue
        
        classes = ' '.join(elem.get('class', [])).lower()
        elem_id = (elem.get('id') or '').lower()

        # Check CSS framework hiding classes (e.g. Webflow .hide, Bootstrap .d-none)
        if any(pattern in classes.split() for pattern in hidden_class_patterns):
            elements_to_decompose.append(elem)
            continue
        
        # Remove cookie/consent/banner/modal/newsletter elements by class/id patterns (configurable)
        if any(pattern in classes or pattern in elem_id for pattern in banner_patterns):
            elements_to_decompose.append(elem)
            continue
        
        # Elements that pass all checks go to processing list
        elements_to_process.append(elem)
    
    # Decompose elements marked for removal
    for elem in elements_to_decompose:
        try:
            elem.decompose()
        except Exception:
            pass  # Silently skip if decomposition fails
    
    # Process remaining elements for attribute stripping
    for elem in elements_to_process:
        # Strip noisy attributes while preserving job-relevant ones (configurable)
        attrs_to_strip = []
        if not hasattr(elem, 'attrs') or elem.attrs is None:
            continue
        for attr in elem.attrs:
            # Strip: configurable list + on* handlers (if enabled)
            should_strip = attr in strip_attrs_list
            if strip_on_attrs and attr.startswith('on'):
                should_strip = True
            if should_strip:
                attrs_to_strip.append(attr)
            # Keep: href, id, class, data-*, aria-*
            # (all others are kept by default - conservative approach)
        
        for attr in attrs_to_strip:
            del elem.attrs[attr]
    
    # Return the culled soup as string
    return str(soup)


async def get_page_dom(  # pragma: no cover
    url: Optional[str] = None,
    *,
    element: Optional[str] = None,
    context: Optional[BrowserSession] = None,
    page: Optional[PageHandle] = None,
) -> str:
    """Extract culled DOM HTML from a URL or existing page.

    Same lifecycle pattern as get_visible_text: pass url for fire-and-forget,
    context= to reuse a browser session, or page= if you already have one.

    Args:
        url: URL to load (required when page is not provided)
        element: CSS selector to extract (default: body)
        context: Optional BrowserSession to reuse
        page: Optional PageHandle already navigated

    Returns:
        Culled HTML string, or "" on failure
    """
    if page is not None:
        return await extract_page_dom(page, element)
    if not url:
        return ""
    if context is not None:
        pg = await get_page(context, url)
        try:
            return await extract_page_dom(pg, element)
        finally:
            await close_page(pg)
    async with create_browser_context() as ctx:
        pg = await get_page(ctx, url)
        try:
            return await extract_page_dom(pg, element)
        finally:
            await close_page(pg)


async def extract_page_dom(page: PageHandle, element: Optional[str] = None) -> str:  # pragma: no cover
    """Extract DOM HTML from a page, culled to remove non-job-related elements.
    
    The page must already be loaded and navigated to the desired URL.
    This function does not navigate or close the page - the caller manages
    the page lifecycle.
    
    Automatically culls HTML using ASTRAL_CONFIG["html_cull"] (allowed tags,
    banner patterns, etc.). When element is None or "body", extracts body
    content; otherwise uses document.querySelector(element) to target a
    specific part of the page.
    
    Args:
        page: Page object that has already been navigated to the target URL
        element: Optional CSS selector (e.g. "body", "main"). If None, uses body.
        
    Returns:
        Culled page HTML as string.
        
    Raises:
        Exception: If page content extraction fails
    """
    if not element or element.strip() == "" or element.strip().lower() == "body":
        raw_html = await page.evaluate('''() => {
            return document.body ? document.body.outerHTML : '';
        }''')
    else:
        # Escape single quotes in selector for JS string
        sel = element.replace("\\", "\\\\").replace("'", "\\'")
        raw_html = await page.evaluate(f'''() => {{
            const el = document.querySelector("{sel}");
            return el ? el.outerHTML : '';
        }}''')
    if not raw_html:
        full_html = await page.content()
        return _cull_html(full_html)
    return _cull_html(raw_html)




async def extract_site_page_list(url: Optional[str] = None, max_depth: int = 1, debug: bool = False, verify: bool = False, context: Optional[BrowserSession] = None, page: Optional[PageHandle] = None) -> List[str]:  # pragma: no cover
    """Extract links from a web page, optionally with recursive crawling.
    
    If a page is provided, extracts links from that page (single-page extraction).
    If no page is provided, recursively crawls starting from the provided URL.
    
    When verify=True, each URL is verified to ensure it loads successfully before
    being included in the results. When verify=False, links are collected without
    verifying pages load.
    
    Args:
        url: Starting URL to begin crawling from (required if page is None)
        max_depth: Maximum depth to crawl (default 1)
        debug: If True, print verbose output about the crawling process
        verify: If True, verify each page loads before including it (default False)
        context: Optional BrowserSession to use for pages (required if page is None and doing recursive crawl)
        page: Optional PageHandle that has already been navigated (for single-page link extraction)
        
    Returns:
        List of unique URLs as strings (verified if verify=True)
        
    Raises:
        ValueError: If both url and page are None, or if page is provided but url is also required for recursive crawl
        Exception: If browser cannot be launched
    """
    # If page is provided, use it for single-page link extraction
    if page is not None:
        if max_depth != 1 or verify:
            raise ValueError("When page is provided, max_depth must be 1 and verify must be False for single-page extraction")
        
        # Extract links from the provided page
        parsed_url = urlparse(page.url)
        base_domain = parsed_url.netloc.replace("www.", "")
        
        # Extract all links from the page (including buttons with URLs)
        link_data = await page.evaluate(r'''(baseDomain) => {
            const allLinks = [];
            
            // Extract from <a> tags
            const links = Array.from(document.querySelectorAll('a[href]'));
            links.forEach(a => {
                try {
                    const href = a.href;
                    if (!href) return;
                    
                    // Only include http/https links
                    if (!href.startsWith('http://') && !href.startsWith('https://')) {
                        return;  // Skip mailto:, tel:, javascript:, etc.
                    }
                    
                    allLinks.push(href);
                } catch (e) {
                    // Invalid URL, skip
                }
            });
            
            // Extract from button elements (onclick, data-href, etc.)
            const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"], a.button, a[class*="button"]'));
            buttons.forEach(btn => {
                try {
                    // Check href if it's an <a> tag styled as button
                    if (btn.tagName === 'A' && btn.href && (btn.href.startsWith('http://') || btn.href.startsWith('https://'))) {
                        allLinks.push(btn.href);
                        return;
                    }
                    
                    // Check data-href attribute
                    const dataHref = btn.getAttribute('data-href') || btn.getAttribute('data-url');
                    if (dataHref && (dataHref.startsWith('http://') || dataHref.startsWith('https://'))) {
                        allLinks.push(dataHref);
                        return;
                    }
                    
                    // Check onclick handler for URLs
                    const onclick = btn.getAttribute('onclick');
                    if (onclick) {
                        // Try to extract URL from onclick (common patterns: window.location, window.open, etc.)
                        const urlMatch = onclick.match(/(?:window\.(?:location|open)\(['"]|href\s*=\s*['"]|location\.href\s*=\s*['"])(https?:\/\/[^'"]+)/i);
                        if (urlMatch && urlMatch[1]) {
                            allLinks.push(urlMatch[1]);
                            return;
                        }
                    }
                    
                    // Check if button contains a link element
                    const innerLink = btn.querySelector('a[href]');
                    if (innerLink) {
                        const href = innerLink.href;
                        if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
                            allLinks.push(href);
                        }
                    }
                } catch (e) {
                    // Invalid URL, skip
                }
            });
            
            return [...new Set(allLinks)];  // Deduplicate
        }''', base_domain)
        
        # Normalize and return links (exclude current page to avoid self-reference)
        current_page_normalized = page.url.rstrip('/').split('#')[0]
        verified_pages = []
        for link in link_data:
            normalized_link = link.rstrip('/').split('#')[0]
            # Skip current page and duplicates
            if normalized_link != current_page_normalized and normalized_link not in verified_pages:
                verified_pages.append(normalized_link)
        
        # Add iframe URLs as links (for embedded ATS job boards)
        for frame in page.frames:
            frame_url = frame.url
            # Skip main frame and about:blank
            if frame == page.main_frame or not frame_url or frame_url == "about:blank":
                continue
            # Only include http/https URLs
            if frame_url.startswith("http://") or frame_url.startswith("https://"):
                normalized_frame = frame_url.rstrip('/').split('#')[0]
                # Skip current page and duplicates
                if normalized_frame != current_page_normalized and normalized_frame not in verified_pages:
                    verified_pages.append(normalized_frame)
        
        return verified_pages
    
    # Recursive crawling path (original behavior)
    if url is None:
        raise ValueError("Either url or page must be provided")
    
    # Normalize starting URL
    parsed_start = urlparse(url)
    if not parsed_start.scheme:
        url = f"https://{url}"
        parsed_start = urlparse(url)
    
    base_domain = parsed_start.netloc.replace("www.", "")
    
    # Track visited URLs and verified pages
    visited = set()
    verified_pages = []
    
    # Process level by level: start with depth 0
    current_level_urls = [url]
    
    if debug:
        _log.info("Starting crawl from %s with max_depth=%s", url, max_depth)
    
    # Define the crawling logic as a nested function to reuse with both contexts
    async def do_crawl(page: Page):  # pragma: no cover
        nonlocal current_level_urls, verified_pages, visited
        # Logic:
        # - max_depth=0: Return only starting URL (no link extraction)
        # - max_depth=1, verify=False: Load site 0, extract level 1 links, return site 0 + level 1 links (don't visit level 1)
        # - max_depth=1, verify=True: Load site 0, extract level 1 links, verify level 1 links load, 
        #   return site 0 + verified level 1 links (don't extract links from level 1)
        # - max_depth=2, verify=False: Load site 0, extract level 1 links, load level 1 links, extract level 2 links,
        #   return site 0 + level 1 + level 2 links (don't verify level 2)
        # - max_depth=2, verify=True: Load site 0, extract level 1 links, load level 1 links, extract level 2 links,
        #   verify level 2 links load, return site 0 + level 1 + verified level 2 links
        
        # Special case: max_depth=0 means just return the starting URL
        if max_depth == 0:
            normalized_start = current_level_urls[0].rstrip('/').split('#')[0]
            verified_pages.append(normalized_start)
            return
        
        # Self-healing cookie dismissal: once-only guard
        cookie_dismissal_attempted = False
        url_threshold = ASTRAL_CONFIG.get("cookie_selfheal_url_threshold", 5)
        
        depth = 0
        while depth <= max_depth:
            if not current_level_urls:
                break
            
            if debug:
                _log.info("--- Processing depth %s (%d pages) ---", depth, len(current_level_urls))
            
            # Collect all unique links from this level
            next_level_links = {}  # normalized_url -> original_url
            
            # At max_depth, handle based on verify flag
            # For depth < max_depth: always visit pages and extract links
            # For depth == max_depth: visit to verify (if verify=True) or just add to results (if verify=False)
            if depth == max_depth:
                if verify:
                    # Visit pages to verify they load, but don't extract links from them
                    for current_url in current_level_urls:
                        normalized_url = current_url.rstrip('/').split('#')[0]
                        if normalized_url in visited:
                            continue
                        visited.add(normalized_url)
                        
                        if debug:
                            _log.debug(f"Verifying [{depth}/{max_depth}]: {normalized_url}")
                        
                        try:
                            await page.goto(normalized_url, wait_until="networkidle", timeout=60000)
                            await page.wait_for_timeout(2000)
                            verified_pages.append(normalized_url)
                            if debug:
                                _log.debug(f"Verified: {normalized_url}")
                        except Exception as e:
                            if debug:
                                _log.debug(f"Skipping {normalized_url} (reason: failed to load - {str(e)})")
                            continue
                else:
                    # Don't visit pages - just add collected links to results
                    for link_url in current_level_urls:
                        normalized_link = link_url.rstrip('/').split('#')[0]
                        if normalized_link not in visited:
                            visited.add(normalized_link)
                            verified_pages.append(normalized_link)
                    if debug:
                        _log.debug(f"Added {len(current_level_urls)} links from depth {depth} to results (not visiting - verify=False)")
                break
            
            # Visit all pages at current depth
            for current_url in current_level_urls:
                # Normalize URL for deduplication (remove fragments, trailing slashes)
                normalized_url = current_url.rstrip('/').split('#')[0]
                
                # Skip if already visited
                if normalized_url in visited:
                    if debug:
                        _log.debug(f"Skipping {normalized_url} (reason: already visited)")
                    continue
                
                # Mark as visited
                visited.add(normalized_url)
                
                if debug:
                    _log.debug(f"Visiting [{depth}/{max_depth}]: {normalized_url}")
                
                try:
                    # Try to load the page (needed to extract links)
                    try:
                        if debug:
                            _log.debug(f"[crawl] goto {normalized_url} (wait_until=load, timeout=60000)")
                        await page.goto(normalized_url, wait_until="load", timeout=60000)
                        await page.wait_for_timeout(2000)  # Let content render
                        page_loaded = True
                        if debug:
                            title = await page.title()
                            _log.debug(f"[crawl] loaded ok title={title!r}")
                    except Exception as load_error:
                        # Page failed to load
                        err_type = type(load_error).__name__
                        err_msg = str(load_error)
                        if debug:
                            _log.debug(f"[crawl] goto failed: {err_type}: {err_msg}")
                        if verify:
                            # If verifying, skip this page
                            if debug:
                                _log.debug(f"Skipping {normalized_url} (reason: failed to load - {err_msg})")
                            continue
                        else:
                            # If not verifying, include it anyway but can't extract links
                            if debug:
                                _log.debug(f"Page failed to load but including in results (verify=False)")
                            verified_pages.append(normalized_url)
                            continue
                    
                    # If we got here, the page loaded successfully
                    verified_pages.append(normalized_url)
                    
                    if debug:
                        _log.debug(f"Processed {len(verified_pages)} pages so far...")
                    
                    # Extract links if we haven't reached max depth (always extract from pages we visit)
                    if depth < max_depth:
                        # Extract all links, separating internal from external
                        # Only include http/https links (exclude mailto, tel, javascript, etc.)
                        # Also extract URLs from button elements
                        link_data = await page.evaluate(r'''(baseDomain) => {
                            const allLinks = [];
                            const internalLinks = [];
                            
                            // Extract from <a> tags
                            const links = Array.from(document.querySelectorAll('a[href]'));
                            links.forEach(a => {
                                try {
                                    const href = a.href;
                                    if (!href) return;
                                    
                                    // Only include http/https links
                                    if (!href.startsWith('http://') && !href.startsWith('https://')) {
                                        return;  // Skip mailto:, tel:, javascript:, etc.
                                    }
                                    
                                    const url = new URL(href);
                                    const domain = url.hostname.replace(/^www\./, '');
                                    
                                    // Add to all links
                                    allLinks.push(href);
                                    
                                    // Check if same domain for internal links
                                    if (domain === baseDomain) {
                                        internalLinks.push(href);
                                    }
                                } catch (e) {
                                    // Invalid URL, skip
                                }
                            });
                            
                            // Extract from button elements (onclick, data-href, etc.)
                            const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]'));
                            buttons.forEach(btn => {
                                try {
                                    // Check data-href attribute
                                    const dataHref = btn.getAttribute('data-href') || btn.getAttribute('data-url');
                                    if (dataHref && (dataHref.startsWith('http://') || dataHref.startsWith('https://'))) {
                                        const url = new URL(dataHref);
                                        const domain = url.hostname.replace(/^www\./, '');
                                        allLinks.push(dataHref);
                                        if (domain === baseDomain) {
                                            internalLinks.push(dataHref);
                                        }
                                        return;
                                    }
                                    
                                    // Check onclick handler for URLs
                                    const onclick = btn.getAttribute('onclick');
                                    if (onclick) {
                                        // Try to extract URL from onclick (common patterns: window.location, window.open, etc.)
                                        const urlMatch = onclick.match(/(?:window\.(?:location|open)\(['"]|href\s*=\s*['"])(https?:\/\/[^'"]+)/i);
                                        if (urlMatch && urlMatch[1]) {
                                            const url = new URL(urlMatch[1]);
                                            const domain = url.hostname.replace(/^www\./, '');
                                            allLinks.push(urlMatch[1]);
                                            if (domain === baseDomain) {
                                                internalLinks.push(urlMatch[1]);
                                            }
                                        }
                                    }
                                    
                                    // Check if button contains a link element
                                    const innerLink = btn.querySelector('a[href]');
                                    if (innerLink) {
                                        const href = innerLink.href;
                                        if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
                                            const url = new URL(href);
                                            const domain = url.hostname.replace(/^www\./, '');
                                            allLinks.push(href);
                                            if (domain === baseDomain) {
                                                internalLinks.push(href);
                                            }
                                        }
                                    }
                                } catch (e) {
                                    // Invalid URL, skip
                                }
                            });
                            
                            return {
                                all: [...new Set(allLinks)],  // All links (internal + external)
                                internal: [...new Set(internalLinks)]  // Only internal links for crawling
                            };
                        }''', base_domain)
                        
                        all_links = link_data.get("all", [])
                        internal_links = link_data.get("internal", [])
                        
                        # Add ALL links to results (internal and external)
                        for link in all_links:
                            normalized_link = link.rstrip('/').split('#')[0]
                            if normalized_link not in visited:
                                visited.add(normalized_link)
                                verified_pages.append(normalized_link)
                        
                        # Only add INTERNAL links to next level for deeper crawling
                        for link in internal_links:
                            normalized_link = link.rstrip('/').split('#')[0]
                            if normalized_link not in visited and normalized_link not in next_level_links:
                                next_level_links[normalized_link] = link
                    
                except Exception as e:
                    if debug:
                        _log.debug(f"Skipping {normalized_url} (reason: failed to load - {str(e)})")
                    continue
            
            # Report summary for this level
            if debug and depth < max_depth:
                _log.debug(f"Found {len(next_level_links)} unique new links from depth {depth} pages")
            
            # Self-healing: after depth 0, check if we got suspiciously few URLs (cookie popup may be blocking)
            if depth == 0 and len(verified_pages) < url_threshold and not cookie_dismissal_attempted:
                cookie_dismissal_attempted = True
                
                if debug:
                    _log.debug(f"[Cookie self-heal] Only {len(verified_pages)} URLs found (threshold: {url_threshold}), attempting cookie dismissal...")
                
                # Try configured selectors first (fast path)
                dismissed = await _try_dismiss_cookie_banner(page, debug=debug)
                
                # If that failed, try fuzzy search (scoped to cookie containers)
                if not dismissed:
                    dismissed = await _try_dismiss_cookie_banner_fuzzy(page, debug=debug)
                
                if dismissed:
                    if debug:
                        _log.debug("[Cookie self-heal] Cookie dismissed, extracting links from current page...")
                    await page.wait_for_timeout(2000)  # Let banner animate away and content settle
                    
                    # Don't reload or restart - the page is already loaded, just re-extract links
                    # The cookie was blocking visibility, now it's dismissed
                    
                    # Re-extract links from the current page (same logic as in the main loop)
                    try:
                        link_data = await page.evaluate(r'''(baseDomain) => {
                            const allLinks = [];
                            const internalLinks = [];
                            
                            const links = Array.from(document.querySelectorAll('a[href]'));
                            links.forEach(a => {
                                try {
                                    const href = a.href;
                                    if (!href) return;
                                    if (!href.startsWith('http://') && !href.startsWith('https://')) return;
                                    
                                    const url = new URL(href);
                                    const domain = url.hostname.replace(/^www\./, '');
                                    allLinks.push(href);
                                    if (domain === baseDomain) {
                                        internalLinks.push(href);
                                    }
                                } catch (e) {}
                            });
                            
                            return {
                                all: [...new Set(allLinks)],
                                internal: [...new Set(internalLinks)]
                            };
                        }''', base_domain)
                        
                        all_links = link_data.get("all", [])
                        internal_links = link_data.get("internal", [])
                        
                        if debug:
                            _log.debug(f"[Cookie self-heal] Found {len(all_links)} total links, {len(internal_links)} internal")
                        
                        # Add discovered links to results and next level
                        for link in all_links:
                            normalized_link = link.rstrip('/').split('#')[0]
                            if normalized_link not in visited:
                                visited.add(normalized_link)
                                verified_pages.append(normalized_link)
                        
                        for link in internal_links:
                            normalized_link = link.rstrip('/').split('#')[0]
                            if normalized_link not in visited and normalized_link not in next_level_links:
                                next_level_links[normalized_link] = link
                        
                        if debug:
                            _log.debug(f"[Cookie self-heal] Now have {len(verified_pages)} verified pages")
                            
                    except Exception as extract_error:
                        if debug:
                            _log.debug(f"[Cookie self-heal] Link extraction failed: {extract_error}")
                else:
                    if debug:
                        _log.debug("[Cookie self-heal] No cookie banner found or dismissed, continuing...")
            
            # Set up next level
            current_level_urls = list(next_level_links.values())
            
            # Increment depth for next iteration
            depth += 1
    
    # If context provided, use it; otherwise create our own
    if context is not None:
        page = await context.new_page()
        try:
            await do_crawl(page)
        finally:
            await page.close()
    else:
        async with async_playwright() as pw:
            browser = await _launch_browser(pw)
            context, page = await _create_page_context(browser)
            
            try:
                await do_crawl(page)
            finally:
                await browser.close()
    
    # Filter out the starting URL to avoid self-reference when crawl results are used for selection
    starting_url_normalized = url.rstrip('/').split('#')[0]
    verified_pages = [p for p in verified_pages if p != starting_url_normalized]
    
    if debug:
        _log.info("Crawl complete: %d loadable pages found", len(verified_pages))
    
    return verified_pages


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (remove trailing slashes, lowercase, standardize scheme).
    
    Used for loop detection in recursion.
    
    Args:
        url: URL string to normalize
        
    Returns:
        Normalized URL string
    """
    if not url:
        return url
    
    # Parse URL
    parsed = urlparse(url)
    
    # Reconstruct with normalized components
    # Lowercase scheme and netloc, remove trailing slash from path
    scheme = parsed.scheme.lower() if parsed.scheme else 'https'
    netloc = parsed.netloc.lower() if parsed.netloc else ''
    path = parsed.path.rstrip('/') if parsed.path else ''
    
    # Reconstruct URL
    normalized = f"{scheme}://{netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    if parsed.fragment:
        normalized += f"#{parsed.fragment}"
    
    return normalized


async def extract_page_content(page_option_url: str, context: BrowserSession) -> Tuple[str, List[str], List[str], PageHandle, Dict[str, Dict[str, Any]]]:  # pragma: no cover
    """Extract visible text, links, and buttons from page option.
    
    Uses a single page load to extract text, links, and buttons sequentially.
    Returns the page object so it can be reused for DOM extraction if needed.
    
    Args:
        page_option_url: URL to extract content from
        context: BrowserSession to use for page creation
        
    Returns:
        Tuple of (visible_text, links_list, buttons_list, page_object, clickable_map)
        The caller is responsible for closing the page.
        
    Raises:
        Exception: Propagates exceptions from external services
    """
    # Create and navigate page once, capturing artifacts for clickable extraction
    artifacts = await get_page_with_artifacts(context, page_option_url)
    page = artifacts["page"]
    
    try:
        # Extract text, links, and buttons sequentially from the same page
        visible_text = await get_visible_text(page=page)
        links_list = await extract_site_page_list(page=page, max_depth=1, verify=False)
        buttons_list, clickable_map = await extract_page_clickables(page, initial_html=artifacts.get("initial_html"))
        return (visible_text, links_list, buttons_list, page, clickable_map)
    except Exception:
        # If extraction fails, close the page before re-raising
        await page.close()
        raise


async def wait_for_careers_list_readiness(
    page: PageHandle,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:  # pragma: no cover
    """Poll until careers-list content appears or bounded wait exhausts (AST-689)."""
    max_wait_ms = int(cfg.get("max_wait_ms") or 20000)
    poll_interval_ms = int(cfg.get("poll_interval_ms") or 500)
    stability_polls = int(cfg.get("stability_polls") or 2)
    min_visible_chars = int(cfg.get("min_visible_chars") or 400)
    min_listing_hits = int(cfg.get("min_listing_hits") or 1)
    listing_selectors = cfg.get("listing_selectors") or []
    run_load_all_jobs_flag = bool(cfg.get("run_load_all_jobs", True))
    load_all_jobs_after_ms = int(cfg.get("load_all_jobs_after_ms") or 3000)

    started = time.monotonic()
    stable_count = 0
    last_len = 0
    load_all_jobs_ran = False
    ready = False
    visible_chars = 0
    listing_hits = 0

    while True:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        if elapsed_ms >= max_wait_ms:
            break

        vt = await extract_visible_text(page)
        visible_len = len(vt.get("text") or "")
        visible_chars = visible_len

        listing_hits = 0
        for sel in listing_selectors:
            try:
                listing_hits += await page.locator(sel).count()
            except Exception:
                pass

        if listing_hits >= min_listing_hits:
            ready = True
            break

        if visible_len >= min_visible_chars and visible_len == last_len:
            stable_count += 1
        else:
            stable_count = 0
        last_len = visible_len

        if stable_count >= stability_polls:
            ready = True
            break

        if run_load_all_jobs_flag and not load_all_jobs_ran and elapsed_ms >= load_all_jobs_after_ms:
            await load_all_jobs(page, "roster")
            load_all_jobs_ran = True

        await page.wait_for_timeout(poll_interval_ms)

    wait_ms = int((time.monotonic() - started) * 1000)
    if visible_chars == 0:
        outcome = "empty"
    elif ready:
        outcome = "ready"
    else:
        outcome = "timeout"

    return {
        "ready": ready,
        "outcome": outcome,
        "visible_chars": visible_chars,
        "listing_hits": listing_hits,
        "wait_ms": wait_ms,
        "load_all_jobs_ran": load_all_jobs_ran,
    }


async def load_all_jobs(page: PageHandle, short_name: str = "unknown") -> None:  # pragma: no cover
    """Trigger lazy loading to get all jobs on the page.

    Handles infinite scroll and "Load More" buttons for non-Greenhouse sites.

    Args:
        page: PageHandle (caller obtains from get_page / new_page / extract_page_content)
        short_name: Company short name for logging (unused, kept for compatibility)
    """
    # Guard: document.body may be null on blank/slow pages
    initialHeight = await page.evaluate('(document.body?.scrollHeight) ?? 0')
    if initialHeight == 0:
        return
    scrollAttempts = 0
    maxScrolls = 10
    
    while scrollAttempts < maxScrolls:
        await page.evaluate('window.scrollTo(0, (document.body?.scrollHeight) ?? 0)')
        await page.wait_for_timeout(1500)

        newHeight = await page.evaluate('(document.body?.scrollHeight) ?? 0')
        if newHeight == initialHeight:
            break
            
        initialHeight = newHeight
        scrollAttempts += 1
    
    # Strategy 2: Click "Load More" button if it exists
    loadMoreClicks = 0
    maxClicks = 20
    
    while loadMoreClicks < maxClicks:
        try:
            loadMoreBtn = await page.query_selector('button:has-text("Load More"), button:has-text("Show More"), a:has-text("Load More")')
            
            if loadMoreBtn:
                await loadMoreBtn.click()
                await page.wait_for_timeout(1500)
                loadMoreClicks += 1
            else:
                break
        except Exception:
            break
    
    await page.evaluate('window.scrollTo(0, 0)')


def _html_tag_to_css_selector(html_tag: str) -> str:
    """Convert HTML tag pattern to CSS selector.
    
    Args:
        html_tag: HTML tag pattern (e.g., '<div class="vacancies__item">' or '<a class="link-module')
    
    Returns:
        CSS selector (e.g., 'div.vacancies__item' or 'a.link-module')
    """
    # Extract tag name and class from HTML pattern
    tag_match = re.search(r'<(\w+)', html_tag)
    if not tag_match:
        return html_tag  # Return as-is if can't parse
    
    tag_name = tag_match.group(1)
    
    # Try to extract all class names (handle both complete and incomplete HTML tags)
    # Pattern 1: Complete class attribute with quotes: class="..."
    class_match = re.search(r'class=["\']([^"\']+)["\']', html_tag)
    if not class_match:
        # Pattern 2: Incomplete class attribute (missing closing quote): class="...
        class_match = re.search(r'class=["\']([^"\']+)', html_tag)
    
    if class_match:
        # Extract ALL classes, not just the first one
        all_classes = class_match.group(1).split()  # Split by whitespace to get all classes
        if all_classes:
            # Escape dots in each class name and join with dots for CSS selector
            escaped_classes = [cls.replace('.', '\\.') for cls in all_classes]
            return f'{tag_name}.' + '.'.join(escaped_classes)
    
    # No class found, just use tag name
    return tag_name  # pragma: no cover


async def extract_with_javascript(page: PageHandle, config: Dict[str, Any]) -> List[str]:  # pragma: no cover
    """Extract job data using JavaScript DOM queries (for Ashby-style boards).
    
    Args:
        page: Playwright page object
        config: Format configuration with job_tag selector and parse_type
    
    Returns:
        List of HTML chunks representing job links in document order
    """
    raw_selector = config.get('job_tag') or config.get('jobTag')
    if not raw_selector:
        return []
    
    # Convert HTML tag pattern to CSS selector if needed
    selector = raw_selector
    if raw_selector.startswith('<'):
        selector = _html_tag_to_css_selector(raw_selector)
    
    # Try CSS selector first
    try:
        result = await page.evaluate("""
            (selector) => {
                try {
                    const startTime = performance.now();
                    const jobElements = Array.from(document.querySelectorAll(selector));
                    const duration = performance.now() - startTime;
                    
                    // If elements don't have href, look for links inside them
                    const htmls = jobElements.map(element => {
                        // If element itself has href, use it
                        if (element.hasAttribute('href') || element.tagName === 'A') {
                            return element.outerHTML;
                        }
                        // Otherwise, find the first link inside
                        const link = element.querySelector('a[href]');
                        if (link) {
                            return link.outerHTML;
                        }
                        // Fallback: return the container element
                        return element.outerHTML;
                    });
                    
                    return {
                        elements: htmls,
                        count: jobElements.length,
                        duration: duration
                    };
                } catch (e) {
                    return {
                        elements: [],
                        count: 0,
                        error: e.toString(),
                        duration: 0
                    };
                }
            }
        """, selector)
        
        if result.get('elements'):
            return result.get('elements', [])
    except Exception:
        pass
    
    # If CSS selector fails, search for elements containing the HTML tag pattern
    if raw_selector.startswith('<'):
        try:
            result = await page.evaluate("""
                (htmlPattern) => {
                    const allElements = Array.from(document.querySelectorAll('*'));
                    const matches = [];
                    for (let el of allElements) {
                        if (el.outerHTML && el.outerHTML.includes(htmlPattern)) {
                            // Only add if it's not already added as a child of another match
                            let isChild = false;
                            for (let existing of matches) {
                                if (existing.contains && existing.contains(el)) {
                                    isChild = true;
                                    break;
                                }
                            }
                            if (!isChild) {
                                matches.push(el);
                            }
                        }
                    }
                    return matches.map(el => {
                        if (el.hasAttribute('href') || el.tagName === 'A') {
                            return el.outerHTML;
                        }
                        const link = el.querySelector('a[href]');
                        return link ? link.outerHTML : el.outerHTML;
                    });
                }
            """, raw_selector)
            
            if result:
                return result
        except Exception:
            pass
    
    return []


def extract_tags_in_order(html: str, tag_pattern: str) -> List[str]:
    """Extract all matching tags from HTML in document order.
    
    IMPORTANT: This function is used for HTML parsing mode. It extracts job postings
    by matching the opening tag pattern (e.g., '<tr class="job-post"') and extracting
    the complete HTML element including its closing tag. This preserves the full job
    posting HTML for later parsing.
    
    Matches tag pattern flexibly - just needs to match the start of the opening tag,
    not the complete tag with all attributes.
    
    Args:
        html: Full HTML string
        tag_pattern: Opening tag pattern to match (e.g., '<div class="posting"')
    
    Returns:
        List of raw HTML chunks in the order they appear in the document
    """
    chunks = []
    search_pos = 0
    
    # Extract tag name from pattern (first word after <)
    pattern_parts = tag_pattern.split()
    if not pattern_parts:
        return []
    
    tag_name = pattern_parts[0].strip('<>').lower()
    closing_tag = f"</{tag_name}>"
    
    while search_pos < len(html):
        # Find the next occurrence of the tag pattern
        match_pos = html.find(tag_pattern, search_pos)
        
        # No more matches found
        if match_pos == -1:  # pragma: no cover
            break  # pragma: no cover
        
        # Find the end of the opening tag (next >)
        opening_tag_end = html.find('>', match_pos)  # pragma: no cover
        if opening_tag_end == -1:  # pragma: no cover
            # Malformed HTML, skip
            search_pos = match_pos + len(tag_pattern)  # pragma: no cover
            continue  # pragma: no cover
        
        # Find the corresponding closing tag by tracking depth
        depth = 1  # pragma: no cover
        scan_pos = opening_tag_end + 1  # pragma: no cover
        opening_tag = f"<{tag_name}"  # pragma: no cover
        
        while scan_pos < len(html) and depth > 0:  # pragma: no cover
            # Find next opening or closing tag of same type
            next_open = html.find(opening_tag, scan_pos)  # pragma: no cover
            next_close = html.find(closing_tag, scan_pos)  # pragma: no cover
            
            # No more closing tags found
            if next_close == -1:  # pragma: no cover
                break  # pragma: no cover
            
            # Opening tag comes first - increase depth
            if next_open != -1 and next_open < next_close:  # pragma: no cover
                depth += 1  # pragma: no cover
                scan_pos = next_open + len(opening_tag)  # pragma: no cover
            # Closing tag comes first - decrease depth
            else:  # pragma: no cover
                depth -= 1  # pragma: no cover
                scan_pos = next_close + len(closing_tag)  # pragma: no cover
                if depth == 0:  # pragma: no cover
                    # Found the matching closing tag
                    end_pos = scan_pos  # pragma: no cover
                    break  # pragma: no cover
        
        if depth != 0:  # pragma: no cover
            # Couldn't find matching closing tag, skip
            search_pos = match_pos + len(tag_pattern)  # pragma: no cover
            continue  # pragma: no cover
        
        # Extract the full chunk (opening + content + closing)
        chunk = html[match_pos:end_pos]
        chunks.append(chunk)
        
        # Move search position past this chunk
        search_pos = end_pos
    
    return chunks


def extract_raw_job_listings(dom_html: str, container: str, job_tag: str, container_index: int = 0) -> List[str]:
    """Extract raw HTML for each job element from the container at container_index.
    job_tag is split into layers: the first selector finds candidate elements,
    remaining selectors validate that each candidate contains a matching descendant.
    Returns the outer (first-layer) element when all layers match."""
    from bs4 import BeautifulSoup
    if not container or not job_tag:
        return []
    soup = BeautifulSoup(dom_html, "html.parser")
    try:
        all_containers = soup.select(container)  # pragma: no cover
    except Exception:  # pragma: no cover
        return []  # pragma: no cover
    if container_index >= len(all_containers):  # pragma: no cover
        return []  # pragma: no cover
    target = all_containers[container_index]  # pragma: no cover
    # Split job_tag into layers, stripping CSS child combinator
    parts = [p for p in job_tag.split() if p != ">"]  # pragma: no cover
    try:  # pragma: no cover
        if len(parts) == 1:  # pragma: no cover
            return [str(el) for el in target.select(parts[0])]  # pragma: no cover
        outer_sel = parts[0]  # pragma: no cover
        inner_sel = " ".join(parts[1:])  # pragma: no cover
        return [str(el) for el in target.select(outer_sel) if el.select_one(inner_sel)]  # pragma: no cover
    except Exception:
        return []
