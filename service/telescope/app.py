"""Astral Telescope FastAPI entrypoint."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Optional, Tuple, Union

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth import require_bearer
from browser import BrowserPool
from capture import capture_html, capture_links, capture_text
from interact import dismiss_cookies, expand_page, navigate, wait_ready_generic
from logging_util import configure_logging, get_logger
from meta import build_scrape_meta
from settings import settings

configure_logging()
_log = get_logger(__name__)


class TelescopeRequest(BaseModel):
    url: str
    selector: Optional[str] = None
    expand: bool = True
    wait_ready: bool = False
    links: bool = True


class TelescopeHtmlRequest(BaseModel):
    url: str
    selector: Optional[str] = None
    expand: bool = True
    wait_ready: bool = False


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
    pool: BrowserPool = request.app.state.pool

    async def work(page):
        text = await capture_text(page, body.selector)
        final_url = page.url
        out: dict = {"final_url": final_url, "text": text}
        if body.links:
            out["links"] = await capture_links(page, body.selector)
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
    pool: BrowserPool = request.app.state.pool

    async def work(page):
        html = await capture_html(page, body.selector)
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
