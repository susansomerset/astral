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
from src.utils.logging import get_logger, log_debug

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
        self._in_flight: Dict[str, int] = {}
        self._client: Optional[httpx.AsyncClient] = None
        # Loop-bound resources (client/lock/sem) must be rebuilt when the running
        # loop changes — admin uses asyncio.run() per request (fresh loop each time),
        # which otherwise reuses a client tied to a closed loop → "Event loop is closed".
        self._loop: Optional[asyncio.AbstractEventLoop] = None

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

    def _ensure_loop(self) -> None:
        loop = asyncio.get_running_loop()
        if self._loop is None:
            # First use — adopt this loop; keep any preexisting client (incl. injected).
            self._loop = loop
            if self._client is None:
                self._client = httpx.AsyncClient(
                    timeout=float(TELESCOPE_CONFIG["request_timeout_seconds"])
                )
            return
        if self._loop is loop:
            return
        # Loop actually changed (e.g. new asyncio.run) → rebuild loop-bound state.
        self._loop = loop
        self._client = httpx.AsyncClient(
            timeout=float(TELESCOPE_CONFIG["request_timeout_seconds"])
        )
        self._lock = asyncio.Lock()
        self._in_flight = {}

    async def _get_client(self) -> httpx.AsyncClient:
        self._ensure_loop()
        assert self._client is not None
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
        self._ensure_loop()  # rebuild loop-bound client/lock/sem before use
        bases = await self._pick_bases()
        token = self._bearer()
        headers = {"Authorization": f"Bearer {token}"}
        max_attempts = min(
            int(TELESCOPE_CONFIG["max_node_attempts"]),
            len(bases),
        )
        last_err: Optional[BaseException] = None
        client = await self._get_client()
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

CAPTURE_FIELDS = frozenset({"text", "links", "html"})


async def _post_telescope(
    url: str,
    *,
    fields: List[str],
    selector: Optional[str] = None,
    tag: Optional[str] = None,
    class_name: Optional[str] = None,
    id: Optional[str] = None,
    expand: Optional[bool] = None,
    wait_ready: Optional[bool] = None,
    debug: Optional[bool] = None,
) -> dict:
    """One POST /telescope — one page load, only requested capture keys in response."""
    want = [f for f in fields if f in CAPTURE_FIELDS]
    if not want:
        raise ValueError("fields must include at least one of: text, links, html")
    scrape_debug = log_debug.get() if debug is None else bool(debug)
    body: Dict[str, Any] = {
        "url": url,
        "fields": want,
        "expand": TELESCOPE_CONFIG["default_expand"] if expand is None else expand,
        "wait_ready": (
            TELESCOPE_CONFIG["default_wait_ready"]
            if wait_ready is None
            else wait_ready
        ),
        "debug": scrape_debug,
    }
    if selector is not None:
        body["selector"] = selector
    if tag is not None:
        body["tag"] = tag
    if class_name is not None:
        body["class_name"] = class_name
    if id is not None:
        body["id"] = id
    path = TELESCOPE_CONFIG["telescope_path"]
    _log.debug("Calling _post_telescope: [path=%s, body=%s]", path, body)
    resp = await _pool.request("POST", path, json_body=body)
    if resp.status_code >= 400:
        _log.debug(
            "Response from _post_telescope: status=%s path=%s body=%s",
            resp.status_code,
            path,
            resp.text,
        )
        raise PlaywrightInfraError(
            "telescope_http_error",
            f"POST /telescope HTTP {resp.status_code}: {resp.text[:200]}",
        )
    data = resp.json()
    _log.debug("Response from _post_telescope: %s", data)
    _log.info(
        "telescope ok path=/telescope fields=%s final_url=%s",
        want,
        data.get("final_url"),
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


async def admin_telescope_scrape(
    url: str,
    *,
    response_type: str,
    expand: Optional[bool] = None,
    wait_ready: Optional[bool] = None,
    links: bool = True,
    selector: Optional[str] = None,
    tag: Optional[str] = None,
    class_name: Optional[str] = None,
    id: Optional[str] = None,
    cull: bool = False,
    debug: bool = False,
) -> dict:
    """Admin workbench scrape — returns full Telescope JSON (incl. scrape_meta)."""
    rt = (response_type or "").strip().lower()
    if rt not in ("text", "html"):
        raise ValueError("response_type must be text or html")
    if rt == "text":
        scrape_fields = ["text"]
        if links:
            scrape_fields.append("links")
        data = await _post_telescope(
            url,
            fields=scrape_fields,
            selector=selector,
            tag=tag,
            class_name=class_name,
            id=id,
            expand=expand,
            wait_ready=wait_ready,
            debug=debug,
        )
    else:
        data = await _post_telescope(
            url,
            fields=["html"],
            selector=selector,
            tag=tag,
            class_name=class_name,
            id=id,
            expand=expand,
            wait_ready=wait_ready,
            debug=debug,
        )
        if cull and "html" in data:
            raw_html = data["html"]
            if isinstance(raw_html, list):
                data = {**data, "html": [_cull_html(h or "") for h in raw_html]}
            else:
                data = {**data, "html": _cull_html(raw_html or "")}
    _log.info(
        "telescope admin scrape type=%s final_url=%s",
        rt,
        data.get("final_url"),
    )
    return data


async def _ensure_fields(page: PageHandle, *fields: str) -> None:
    """Fetch any missing capture fields in one Telescope POST."""
    if page._closed:
        raise PlaywrightInfraError("context_closed", "page is closed")
    need: List[str] = []
    for field in fields:
        if field not in CAPTURE_FIELDS:
            continue
        if field == "text" and page._text is None:
            need.append("text")
        elif field == "links" and page._links is None:
            need.append("links")
        elif field == "html" and page._html is None:
            need.append("html")
    if not need:
        return
    if not (page.url or "").strip():
        if "text" in need:
            page._text = ""
        if "links" in need:
            page._links = []
        if "html" in need:
            page._html = ""
        return
    data = await _post_telescope(
        page.url,
        fields=need,
        expand=page.expand,
        wait_ready=page.wait_ready,
    )
    if "text" in need:
        text = data.get("text")
        if isinstance(text, list):
            page._text = "\n\n".join(t for t in text if t)
        else:
            page._text = text or ""
    if "links" in need:
        page._links = data.get("links") or []
    if "html" in need:
        html = data.get("html") or ""
        if isinstance(html, list):
            html = html[0] if html else ""
        page._html = html
    final = data.get("final_url")
    if final:
        page._final_url = final
        page.url = final


async def _ensure_text(page: PageHandle, *, links: bool = False) -> None:
    want = ["text"]
    if links:
        want.append("links")
    await _ensure_fields(page, *want)


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
    data = await _post_telescope(
        page.url,
        fields=["html"],
        selector=selector,
        expand=page.expand,
        wait_ready=page.wait_ready,
    )
    html = data.get("html") or ""
    if isinstance(html, list):
        html = html[0] if html else ""
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



# ---------------------------------------------------------------------------
# Scrape-backed public API (Telescope HTTP + local post-render)
# ---------------------------------------------------------------------------


async def extract_visible_text(page: PageHandle) -> Dict[str, Any]:
    await _ensure_text(page, links=False)
    return {"text": page._text or "", "url": page._final_url or page.url}


async def extract_page_scrape_contract(page: PageHandle) -> Dict[str, Any]:
    await _ensure_fields(page, "text", "links")
    vt = {"text": page._text or "", "url": page._final_url or page.url}
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


async def get_visible_text(
    url: Optional[str] = None,
    *,
    context: Optional[BrowserSession] = None,
    page: Optional[PageHandle] = None,
    return_final_url: bool = False,
):
    def _out(result):
        text = result.get("text", "") or ""
        if return_final_url:
            return text, result.get("url", url or "")
        return text

    if page is not None:
        return _out(await extract_visible_text(page))
    if not url:
        return ("", "") if return_final_url else ""
    if context is not None:
        pg = await get_page(context, url)
        try:
            return _out(await extract_visible_text(pg))
        finally:
            await close_page(pg)
    last_err: Optional[Exception] = None
    for attempt in range(2):
        try:
            async with create_browser_context() as ctx:
                pg = await get_page(ctx, url)
                try:
                    return _out(await extract_visible_text(pg))
                finally:
                    await close_page(pg)
        except Exception as e:
            _log.warning(
                "get_visible_text: attempt %d failed: %s: %s",
                attempt + 1,
                type(e).__name__,
                e,
            )
            last_err = e
    if last_err is not None:
        raise last_err
    return ("", "") if return_final_url else ""


async def get_page_dom(
    url: Optional[str] = None,
    *,
    element: Optional[str] = None,
    context: Optional[BrowserSession] = None,
    page: Optional[PageHandle] = None,
) -> str:
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


async def extract_page_dom(page: PageHandle, element: Optional[str] = None) -> str:
    raw_html = await _ensure_html(page, selector=element)
    if not raw_html:
        return ""
    if TELESCOPE_CONFIG.get("cull_html_default", True):
        return _cull_html(raw_html)
    return raw_html


async def load_all_jobs(page: PageHandle, short_name: str = "unknown") -> None:
    _log.debug("load_all_jobs: flag expand on handle short_name=%s", short_name)
    page.expand = True
    page._invalidate()


async def wait_for_careers_list_readiness(
    page: PageHandle,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    """Map readiness to Telescope wait_ready (+ expand); listing selectors unavailable remotely."""
    started = time.monotonic()
    page.wait_ready = True
    if bool(cfg.get("run_load_all_jobs", True)):
        page.expand = True
    page._invalidate()
    load_all_jobs_ran = bool(cfg.get("run_load_all_jobs", True))
    await _ensure_text(page, links=False)
    visible_chars = len(page._text or "")
    wait_ms = int((time.monotonic() - started) * 1000)
    if visible_chars == 0:
        outcome = "empty"
    else:
        outcome = "ready"
    return {
        "outcome": outcome,
        "wait_ms": wait_ms,
        "visible_chars": visible_chars,
        "listing_hits": 0,
        "load_all_jobs_ran": load_all_jobs_ran,
        "ready": outcome == "ready",
    }


async def get_page_with_artifacts(context: BrowserSession, url: str) -> PageLoadArtifacts:
    page = await get_page(context, url)
    html = await _ensure_html(page)
    return PageLoadArtifacts(
        page=page,
        initial_html=html,
        request_urls=[],
        frame_urls=[],
    )


async def extract_page_clickables(
    page: PageHandle, initial_html: Optional[str] = None
) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    html = initial_html
    if not html:
        html = await _ensure_html(page)
    texts, href_map = _parse_html_for_internal_clickables(html or "")
    clickable_map: Dict[str, Dict[str, Any]] = {}
    for text, href in href_map.items():
        clickable_map[text] = {"href": href, "kind": "internal_a"}
    return texts, clickable_map


async def extract_page_content(
    page_option_url: str, context: BrowserSession
) -> Tuple[str, List[str], List[str], PageHandle, Dict[str, Dict[str, Any]]]:
    artifacts = await get_page_with_artifacts(context, page_option_url)
    page = artifacts["page"]
    try:
        visible_text = await get_visible_text(page=page)
        links_list = await extract_site_page_list(page=page, max_depth=1, verify=False)
        buttons_list, clickable_map = await extract_page_clickables(
            page, initial_html=artifacts.get("initial_html")
        )
        return (visible_text, links_list, buttons_list, page, clickable_map)
    except Exception:
        await page.close()
        raise


async def extract_with_javascript(page: PageHandle, config: Dict[str, Any]) -> List[str]:
    """HTML-first stand-in: unsupported live evaluate — return empty (callers rare)."""
    _ = page, config
    _log.warning("extract_with_javascript unsupported on Telescope client — returning []")
    return []


async def extract_site_page_list(
    url: Optional[str] = None,
    max_depth: int = 1,
    debug: bool = False,
    verify: bool = False,
    context: Optional[BrowserSession] = None,
    page: Optional[PageHandle] = None,
) -> List[str]:
    """Collect http(s) links via Telescope; optional shallow crawl."""

    async def _links_from_handle(pg: PageHandle) -> List[str]:
        await _ensure_text(pg, links=True)
        out = []
        for lnk in pg._links or []:
            href = (lnk.get("href") or "").strip()
            if href.startswith("http"):
                out.append(href)
        return out

    if page is not None:
        return await _links_from_handle(page)

    if not url:
        raise ValueError("extract_site_page_list requires url or page")

    async def _crawl(start_url: str, ctx: BrowserSession) -> List[str]:
        seen: set = set()
        results: List[str] = []
        queue: List[Tuple[str, int]] = [(start_url, 0)]
        start_host = urlparse(start_url).netloc.lower()
        while queue:
            cur, depth = queue.pop(0)
            key = normalize_url(cur)
            if key in seen:
                continue
            seen.add(key)
            pg = await get_page(ctx, cur)
            try:
                if verify and depth > 0:
                    # verifying means a successful telescope fetch
                    await _ensure_text(pg, links=False)
                hrefs = await _links_from_handle(pg)
                for href in hrefs:
                    n = normalize_url(href)
                    if n not in seen and n not in results:
                        if urlparse(href).netloc.lower() == start_host:
                            results.append(href)
                            if depth + 1 < max_depth:
                                queue.append((href, depth + 1))
                        elif depth == 0:
                            # include off-host links discovered on the start page
                            results.append(href)
                if debug:
                    _log.info(
                        "extract_site_page_list depth=%s url=%s links=%s",
                        depth,
                        cur,
                        len(hrefs),
                    )
            finally:
                await close_page(pg)
        # drop starting url from results (match former behavior)
        start_n = normalize_url(start_url)
        return [p for p in results if normalize_url(p) != start_n]

    if context is not None:
        return await _crawl(url, context)
    async with create_browser_context() as ctx:
        return await _crawl(url, ctx)


# ---- Ported post-render / HTML helpers (from former playwright.py) ----

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
    had_body = body_tag is not None
    if body_tag is None:
        # Fallback: if no body tag, use the whole document
        body_soup = soup
    else:
        # Extract just the body's inner contents (not the body tag itself)
        body_contents = ''.join(str(child) for child in body_tag.children)
        body_soup = BeautifulSoup(body_contents, 'html.parser')
    
    # Use body_soup for all culling operations
    soup = body_soup

    # AST-1745: class-scoped fragments whose top-level nodes are <svg> (e.g. svg.logo)
    # must keep that outerHTML; nested svg under non-svg roots still get stripped below.
    preserve_root_svgs = set()
    if not had_body:
        for child in list(soup.children):
            if getattr(child, "name", None) == "svg":
                preserve_root_svgs.add(child)

    def _in_preserved_svg(elem) -> bool:
        if elem in preserve_root_svgs:
            return True
        return any(p in preserve_root_svgs for p in getattr(elem, "parents", []))
    
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
    
    # Remove large SVG blocks (icon sprites are often huge and not job-relevant).
    # Keep fragment-root svgs (and their descendants) — AST-1745 class-scoped logos.
    for svg in soup.find_all('svg'):
        if _in_preserved_svg(svg):
            continue
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
    # Note: img tags are handled separately above, so exclude them from unwrapping.
    # AST-1745: also leave preserved root-svg trees intact (svg/g/path not in allowed_tags).
    max_passes = 10  # Safety limit to prevent infinite loops
    for pass_num in range(max_passes):
        # Find all elements that are not in allowed_tags (excluding img, which is handled separately)
        non_allowed = [
            elem
            for elem in soup.find_all(True)
            if elem.name not in allowed_tags
            and elem.name != "img"
            and not _in_preserved_svg(elem)
        ]
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

