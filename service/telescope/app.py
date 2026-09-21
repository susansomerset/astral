"""Astral Telescope FastAPI entrypoint."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Optional, Tuple, Union

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from auth import require_bearer
from browser import BrowserPool
from capture import (
    CaptureQueryError,
    capture_html,
    capture_links,
    capture_text,
    resolve_capture_query,
)
from interact import dismiss_cookies, expand_page, navigate, wait_ready_generic
from logging_util import configure_logging, get_logger
from meta import build_scrape_meta
from settings import settings

configure_logging()
_log = get_logger(__name__)

# Expand = scroll + Load More on this URL only — not numbered / Next pagination (AST-1737).
_EXPAND_DESC = (
    "Infinite-scroll + Load More/Show More on the current document. "
    "Does not navigate numbered pagination or Next-page URLs."
)


# tag + selector = same primary; class_name is optional secondary (AST-1744).
_PRIMARY_DESC = (
    "Element tag / CSS primary (alias of tag). Same slot as tag — "
    "html, div, span, body, head, ul, page, or legacy CSS."
)
_TAG_DESC = (
    "Element tag primary (alias of selector). Same slot as selector — "
    "html, div, span, body, head, ul, or page."
)
_CLASS_DESC = (
    "Secondary class filter: elements with class=\"…\". "
    "Combines with a bare tag primary as {tag}.{class}, or alone as .{class}."
)


class TelescopeRequest(BaseModel):
    url: str
    selector: Optional[str] = Field(default=None, description=_PRIMARY_DESC)
    tag: Optional[str] = Field(default=None, description=_TAG_DESC)
    class_name: Optional[str] = Field(default=None, description=_CLASS_DESC)
    expand: bool = Field(default=True, description=_EXPAND_DESC)
    wait_ready: bool = False
    links: bool = True


class TelescopeHtmlRequest(BaseModel):
    url: str
    selector: Optional[str] = Field(default=None, description=_PRIMARY_DESC)
    tag: Optional[str] = Field(default=None, description=_TAG_DESC)
    class_name: Optional[str] = Field(default=None, description=_CLASS_DESC)
    expand: bool = Field(default=True, description=_EXPAND_DESC)
    wait_ready: bool = False


def _resolve_body_selector(
    *,
    selector: Optional[str],
    tag: Optional[str],
    class_name: Optional[str],
) -> Optional[str]:
    """Map request filter fields to the CSS string capture_* expects; 400 on bad input."""
    try:
        resolved = resolve_capture_query(
            selector=selector, tag=tag, class_name=class_name
        )
    except CaptureQueryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    # Log primary (+ optional class) without dumping page content
    primary = (tag or "").strip() or (selector or "").strip() or None
    cn = (class_name or "").strip() or None
    if primary or cn:
        _log.info(
            "telescope filter mode=primary(+class) primary=%s class_name=%s resolved=%s",
            primary,
            cn,
            resolved,
        )
    return resolved


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    if not settings.bearer_token:
        raise RuntimeError("TELESCOPE_BEARER_TOKEN is required")
    pool = BrowserPool()
    await pool.start()
    app.state.pool = pool
    try:
        yield
    finally:
        await pool.stop()


app = FastAPI(title="Astral Telescope", lifespan=lifespan)

WorkFn = Callable[[Any], Awaitable[Any]]


async def _run_browser_job(
    pool: BrowserPool,
    url: str,
    expand: bool,
    wait_ready: bool,
    work: WorkFn,
) -> Tuple[Any, bool]:
    cookies_dismissed = False

    async def _job() -> Any:
        nonlocal cookies_dismissed
        async with pool.page() as page:
            await navigate(page, url)
            cookies_dismissed = await dismiss_cookies(page)
            if expand:
                await expand_page(page)
            if wait_ready:
                await wait_ready_generic(page)
            return await work(page)

    try:
        result = await asyncio.wait_for(
            _job(),
            timeout=settings.request_timeout_seconds,
        )
    except asyncio.TimeoutError:
        _log.warning(
            "telescope timeout url=%s timeout_s=%s",
            url,
            settings.request_timeout_seconds,
        )
        raise HTTPException(status_code=504, detail="timeout") from None
    except HTTPException:
        raise
    except Exception as exc:
        _log.exception(
            "telescope scrape_failed url=%s\n  %s: %s",
            url,
            type(exc).__name__,
            exc,
        )
        raise HTTPException(status_code=502, detail="scrape_failed") from None
    return result, cookies_dismissed


def _unwrap_job(
    raw: Union[Tuple[Any, bool], Any],
) -> Tuple[Any, bool]:
    """Production returns (result, cookies_dismissed); test doubles may return result only."""
    if isinstance(raw, tuple) and len(raw) == 2 and isinstance(raw[1], bool):
        return raw[0], raw[1]
    return raw, False


@app.get("/healthz", dependencies=[Depends(require_bearer)])
async def healthz(request: Request):
    pool: BrowserPool = request.app.state.pool
    try:
        ok = await pool.health_poke()
    except Exception as exc:
        _log.exception(
            "healthz browser poke failed\n  %s: %s",
            type(exc).__name__,
            exc,
        )
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
    if not ok:
        _log.warning("healthz browser disconnected after poke")
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
    return {"status": "ok"}


@app.post("/telescope", dependencies=[Depends(require_bearer)])
async def post_telescope(request: Request, body: TelescopeRequest):
    url = (body.url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    sel = _resolve_body_selector(
        selector=body.selector, tag=body.tag, class_name=body.class_name
    )
    pool: BrowserPool = request.app.state.pool

    async def work(page):
        text = await capture_text(page, sel)
        final_url = page.url
        out: dict = {"final_url": final_url, "text": text}
        if body.links:
            out["links"] = await capture_links(page, sel)
        return out

    raw = await _run_browser_job(pool, url, body.expand, body.wait_ready, work)
    result, cookies_dismissed = _unwrap_job(raw)
    result["scrape_meta"] = build_scrape_meta(
        requested_url=url,
        final_url=result.get("final_url") or "",
        text_or_html=result.get("text"),
        cookies_dismissed=cookies_dismissed,
    )
    text = result.get("text")
    if isinstance(text, list):
        chars = sum(len(t or "") for t in text)
    else:
        chars = len(text or "")
    _log.info(
        "telescope ok method=/telescope final_url=%s chars=%d",
        result.get("final_url"),
        chars,
    )
    return result


@app.post("/telescope/html", dependencies=[Depends(require_bearer)])
async def post_telescope_html(request: Request, body: TelescopeHtmlRequest):
    url = (body.url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    sel = _resolve_body_selector(
        selector=body.selector, tag=body.tag, class_name=body.class_name
    )
    pool: BrowserPool = request.app.state.pool

    async def work(page):
        html = await capture_html(page, sel)
        return {"final_url": page.url, "html": html}

    raw = await _run_browser_job(pool, url, body.expand, body.wait_ready, work)
    result, cookies_dismissed = _unwrap_job(raw)
    result["scrape_meta"] = build_scrape_meta(
        requested_url=url,
        final_url=result.get("final_url") or "",
        text_or_html=result.get("html"),
        cookies_dismissed=cookies_dismissed,
    )
    html = result.get("html")
    if isinstance(html, list):
        html_len = sum(len(h or "") for h in html)
    else:
        html_len = len(html or "")
    _log.info(
        "telescope ok method=/telescope/html final_url=%s html_len=%d",
        result.get("final_url"),
        html_len,
    )
    return result
