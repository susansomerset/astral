"""
Platform Telescope client + Surfer-ready post-render helpers (AST-1726).

Drop-in replacement for the former playwright module: same public names/params.
Headless scrape I/O goes to the Telescope HTTP service; post-render helpers
(cull, delimiter splits, extract-from-HTML, etc.) stay in this file.
No in-process Firefox.
"""

from __future__ import annotations

import asyncio
import os
import re
import time
from contextlib import asynccontextmanager
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple, TypedDict
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from src.utils.config import ASTRAL_CONFIG, PLAYWRIGHT_CONFIG, TELESCOPE_CONFIG
from src.utils.integration_io import require_controlled_external_io
from src.utils.logging import get_logger

_log = get_logger(__name__)

PLAYWRIGHT_INFRA_FAILURE_CLASSES = frozenset({
    "launch_failure",
    "launch_timeout",
    "channel_error",
    "context_closed",
    "connectivity_failure",
    "telescope_timeout",
    "telescope_http_error",
})


def classify_playwright_failure(exc: BaseException) -> str:
    """Map Playwright/Firefox/Telescope-client exceptions to a stable failure class."""
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
    if isinstance(exc, httpx.TimeoutException) or "telescope_timeout" in msg:
        return "telescope_timeout"
    if "timeout" in msg and ("goto" in msg or "navigation" in msg or "telescope" in msg):
        return "telescope_timeout"
    if "connect" in msg or "connection" in msg:
        return "connectivity_failure"
    if "telescope_http" in msg or " 5" in msg and "http" in msg:
        return "telescope_http_error"
    return "unknown"


def is_playwright_infra_failure(failure_class: str) -> bool:
    return failure_class in PLAYWRIGHT_INFRA_FAILURE_CLASSES


class PlaywrightInfraError(Exception):
    """Raised when Telescope HTTP or former browser-infra I/O fails (infra, not site)."""

    def __init__(self, failure_class: str, detail: str) -> None:
        self.failure_class = failure_class
        self.detail = detail
        super().__init__(f"[{failure_class}] {detail}")


# ---------------------------------------------------------------------------
# Client-side session / page handles (drop-in for former BrowserContext / Page)
# ---------------------------------------------------------------------------


class BrowserSession:
    """Client-side session handle (no Firefox)."""

    def __init__(self) -> None:
        self._alive = True

    async def aclose(self) -> None:
        self._alive = False


class PageHandle:
    """Bound URL + scrape flags + optional cached Telescope artifacts."""

    def __init__(
        self,
        url: str = "",
        *,
        session: Optional[BrowserSession] = None,
        expand: Optional[bool] = None,
        wait_ready: Optional[bool] = None,
    ) -> None:
        self.url = url or ""
        self._session = session
        self.expand = (
            TELESCOPE_CONFIG["default_expand"] if expand is None else bool(expand)
        )
        self.wait_ready = (
            TELESCOPE_CONFIG["default_wait_ready"]
            if wait_ready is None
            else bool(wait_ready)
        )
        self._html: Optional[str] = None
        self._text: Optional[Any] = None
        self._links: Optional[List[Dict[str, str]]] = None
        self._final_url: Optional[str] = None
        self._closed = False

    def _invalidate(self) -> None:
        self._html = None
        self._text = None
        self._links = None
        self._final_url = None

    async def close(self) -> None:
        self._closed = True
        self._invalidate()


class BatchBrowserSession:
    """Recoverable batch scrape session — client-side only (no Firefox)."""

    def __init__(
        self,
        headless: bool = True,
        viewport: Optional[Dict[str, int]] = None,
    ) -> None:
        self._headless = headless
        self._viewport = viewport or {"width": 1280, "height": 2000}
        self._inner = BrowserSession()
        self._lock = asyncio.Lock()

    async def ensure_context(self) -> BrowserSession:
        async with self._lock:
            if not self._inner._alive:
                self._inner = BrowserSession()
            return self._inner

    async def recover(self, failure_class: str, reason: str) -> None:
        async with self._lock:
            _log.warning(
                "telescope batch session recover failure_class=%s reason=%s",
                failure_class,
                reason,
            )
            await self._inner.aclose()
            self._inner = BrowserSession()

    async def aclose(self) -> None:
        async with self._lock:
            await self._inner.aclose()


# ---------------------------------------------------------------------------
# HTTP pool
# ---------------------------------------------------------------------------


class _TelescopePool:
    def __init__(self) -> None:
        self._rr = 0
        self._lock = asyncio.Lock()
        self._sem = asyncio.Semaphore(int(TELESCOPE_CONFIG["max_in_flight"]))
        self._in_flight: Dict[str, int] = {}
        self._client: Optional[httpx.AsyncClient] = None

    def _bases(self) -> List[str]:
        return list(TELESCOPE_CONFIG.get("base_urls") or [])

    def _bearer(self) -> str:
        env_key = TELESCOPE_CONFIG["bearer_env"]
        tok = (os.environ.get(env_key) or "").strip()
        if not tok:
            raise PlaywrightInfraError(
                "connectivity_failure", f"{env_key} not set"
            )
        return tok

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=float(TELESCOPE_CONFIG["client_timeout_seconds"])
            )
        return self._client

    async def _pick_bases(self) -> List[str]:
        bases = self._bases()
        if not bases:
            raise PlaywrightInfraError(
                "connectivity_failure", "TELESCOPE_BASE_URL(S) not configured"
            )
        async with self._lock:
            start = self._rr % len(bases)
            self._rr += 1
        # round-robin primary, then remaining in order (least-in-flight soft preference)
        ordered = bases[start:] + bases[:start]
        if TELESCOPE_CONFIG.get("retry_other_node") and len(ordered) > 1:
            # sort secondary by current in-flight
            primary = ordered[0]
            rest = sorted(ordered[1:], key=lambda b: self._in_flight.get(b, 0))
            return [primary] + rest
        return ordered

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[dict] = None,
    ) -> httpx.Response:
        require_controlled_external_io("telescope.request")
        bases = await self._pick_bases()
        token = self._bearer()
        headers = {"Authorization": f"Bearer {token}"}
        max_attempts = min(
            int(TELESCOPE_CONFIG["max_node_attempts"]),
            len(bases),
        )
        last_err: Optional[BaseException] = None
        client = await self._get_client()
        async with self._sem:
            for attempt, base in enumerate(bases[:max_attempts]):
                url = base.rstrip("/") + path
                self._in_flight[base] = self._in_flight.get(base, 0) + 1
                try:
                    resp = await client.request(
                        method, url, headers=headers, json=json_body
                    )
                    if resp.status_code in (401, 403):
                        _log.error(
                            "telescope auth failed status=%s base=%s path=%s",
                            resp.status_code,
                            base,
                            path,
                        )
                        raise PlaywrightInfraError(
                            "connectivity_failure",
                            f"telescope auth {resp.status_code}",
                        )
                    if resp.status_code >= 500:
                        _log.warning(
                            "telescope 5xx status=%s base=%s path=%s",
                            resp.status_code,
                            base,
                            path,
                        )
                        last_err = PlaywrightInfraError(
                            "telescope_http_error",
                            f"HTTP {resp.status_code} from {base}",
                        )
                        if attempt + 1 < max_attempts:
                            continue
                        raise last_err
                    return resp
                except PlaywrightInfraError:
                    raise
                except httpx.TimeoutException as e:
                    _log.warning(
                        "telescope timeout base=%s path=%s: %s", base, path, e
                    )
                    last_err = PlaywrightInfraError(
                        "telescope_timeout", f"timeout talking to {base}: {e}"
                    )
                    if attempt + 1 < max_attempts:
                        continue
                    raise last_err from e
                except httpx.HTTPError as e:
                    _log.warning(
                        "telescope connect error base=%s path=%s: %s", base, path, e
                    )
                    last_err = PlaywrightInfraError(
                        "connectivity_failure", f"connect {base}: {e}"
                    )
                    if attempt + 1 < max_attempts:
                        continue
                    raise last_err from e
                finally:
                    self._in_flight[base] = max(
                        0, self._in_flight.get(base, 1) - 1
                    )
        raise last_err or PlaywrightInfraError(
            "connectivity_failure", "telescope request failed"
        )


_pool = _TelescopePool()


async def _post_telescope(
    url: str,
    *,
    selector: Optional[str] = None,
    expand: Optional[bool] = None,
    wait_ready: Optional[bool] = None,
    links: bool = True,
) -> dict:
    body: Dict[str, Any] = {
        "url": url,
        "expand": TELESCOPE_CONFIG["default_expand"] if expand is None else expand,
        "wait_ready": (
            TELESCOPE_CONFIG["default_wait_ready"]
            if wait_ready is None
            else wait_ready
        ),
        "links": links,
    }
    if selector is not None:
        body["selector"] = selector
    resp = await _pool.request(
        "POST", TELESCOPE_CONFIG["telescope_path"], json_body=body
    )
    if resp.status_code >= 400:
        raise PlaywrightInfraError(
            "telescope_http_error",
            f"POST /telescope HTTP {resp.status_code}: {resp.text[:200]}",
        )
    data = resp.json()
    _log.info(
        "telescope ok path=/telescope final_url=%s",
        data.get("final_url"),
    )
    return data


async def _post_telescope_html(
    url: str,
    *,
    selector: Optional[str] = None,
    expand: Optional[bool] = None,
    wait_ready: Optional[bool] = None,
) -> dict:
    body: Dict[str, Any] = {
        "url": url,
        "expand": TELESCOPE_CONFIG["default_expand"] if expand is None else expand,
        "wait_ready": (
            TELESCOPE_CONFIG["default_wait_ready"]
            if wait_ready is None
            else wait_ready
        ),
    }
    if selector is not None:
        body["selector"] = selector
    resp = await _pool.request(
        "POST", TELESCOPE_CONFIG["telescope_html_path"], json_body=body
    )
    if resp.status_code >= 400:
        raise PlaywrightInfraError(
            "telescope_http_error",
            f"POST /telescope/html HTTP {resp.status_code}: {resp.text[:200]}",
        )
    data = resp.json()
    _log.info(
        "telescope ok path=/telescope/html final_url=%s html_len=%s",
        data.get("final_url"),
        len(data.get("html") or ""),
    )
    return data


async def _get_healthz() -> bool:
    try:
        resp = await _pool.request("GET", TELESCOPE_CONFIG["healthz_path"])
        if resp.status_code != 200:
            return False
        body = resp.json()
        return (body.get("status") or "").lower() == "ok"
    except Exception as e:
        fc = classify_playwright_failure(e)
        _log.warning("check_connectivity failed failure_class=%s: %s", fc, e)
        return False


async def _ensure_text(page: PageHandle, *, links: bool = False) -> None:
    if page._closed:
        raise PlaywrightInfraError("context_closed", "page is closed")
    if page._text is not None and (not links or page._links is not None):
        return
    if not (page.url or "").strip():
        page._text = ""
        page._links = []
        return
    data = await _post_telescope(
        page.url,
        expand=page.expand,
        wait_ready=page.wait_ready,
        links=links,
    )
    text = data.get("text")
    if isinstance(text, list):
        page._text = "\n\n".join(t for t in text if t)
    else:
        page._text = text or ""
    if "links" in data:
        page._links = data.get("links") or []
    elif links:
        page._links = []
    final = data.get("final_url")
    if final:
        page._final_url = final
        page.url = final


async def _ensure_html(
    page: PageHandle, selector: Optional[str] = None
) -> str:
    if page._closed:
        raise PlaywrightInfraError("context_closed", "page is closed")
    # Re-fetch when selector changes or cache empty
    if page._html is not None and selector is None:
        return page._html
    if not (page.url or "").strip():
        page._html = ""
        return ""
    data = await _post_telescope_html(
        page.url,
        selector=selector,
        expand=page.expand,
        wait_ready=page.wait_ready,
    )
    html = data.get("html") or ""
    if selector is None:
        page._html = html
    final = data.get("final_url")
    if final:
        page._final_url = final
        page.url = final
    return html


# ---------------------------------------------------------------------------
# Session factories
# ---------------------------------------------------------------------------


@asynccontextmanager
async def create_batch_browser_session(
    headless: bool = True,
    viewport: Optional[Dict[str, int]] = None,
):
    session = BatchBrowserSession(headless=headless, viewport=viewport)
    try:
        await session.ensure_context()
        yield session
    finally:
        await session.aclose()


@asynccontextmanager
async def create_browser_context(
    headless: bool = True, viewport: Optional[Dict[str, int]] = None
):
    _ = headless, viewport
    session = BrowserSession()
    try:
        yield session
    finally:
        await session.aclose()


async def get_page(
    context: Optional[BrowserSession] = None,
    url: Optional[str] = None,
    *,
    batch_session: Optional[BatchBrowserSession] = None,
) -> PageHandle:
    if batch_session is not None:
        session = await batch_session.ensure_context()
    else:
        session = context
    if session is None:
        raise ValueError("get_page requires context or batch_session")
    return PageHandle(url=url or "", session=session)


async def new_page(session: BrowserSession) -> PageHandle:
    return PageHandle(url="", session=session)


async def close_page(page: PageHandle) -> None:
    await page.close()


async def check_connectivity(timeout: Optional[int] = None) -> bool:
    _ = timeout
    return await _get_healthz()


def get_page_url(page: PageHandle) -> str:
    return page._final_url or page.url


def get_frame_urls(page: PageHandle) -> List[str]:
    _ = page
    return []


async def get_link_urls_from_page(page: PageHandle) -> List[str]:
    await _ensure_text(page, links=True)
    return [
        (lnk.get("href") or "")
        for lnk in (page._links or [])
        if (lnk.get("href") or "").startswith("http")
    ]


async def evaluate(page: PageHandle, script: str, *args: Any) -> Any:
    _ = page, script, args
    raise PlaywrightInfraError(
        "unknown", "evaluate unsupported on Telescope client"
    )


async def wait_for_timeout(page: PageHandle, milliseconds: int) -> None:
    _ = page
    await asyncio.sleep(max(0, milliseconds) / 1000.0)


async def navigate_and_wait_for_ready(
    page: PageHandle, url: str, timeout: Optional[int] = None
) -> None:
    _ = timeout
    page.url = url
    page._invalidate()
    page.wait_ready = True


async def wait_for_page_ready_after_navigation(
    page: PageHandle, timeout: Optional[int] = None
) -> None:
    _ = timeout
    page.wait_ready = True
    page._invalidate()

