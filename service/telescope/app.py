"""Astral Telescope FastAPI entrypoint."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Literal, Optional, Tuple, Union

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

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


# tag + selector = same primary; class_name / id are optional secondaries.
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
_ID_DESC = (
    "Secondary id filter: elements with id=\"…\". "
    "Combines with bare tag / class as {tag}.{class}#id, or alone as #id."
)

CaptureField = Literal["text", "links", "html"]
CAPTURE_FIELDS = frozenset({"text", "links", "html"})

_FIELDS_DESC = (
    "What to extract from one page load. Response includes final_url, scrape_meta, "
    "and only the requested capture keys (text, links, html)."
)


class _TelescopeScrapeBody(BaseModel):
    url: str
    selector: Optional[str] = Field(default=None, description=_PRIMARY_DESC)
    tag: Optional[str] = Field(default=None, description=_TAG_DESC)
    class_name: Optional[str] = Field(default=None, description=_CLASS_DESC)
    id: Optional[str] = Field(default=None, description=_ID_DESC)
    expand: bool = Field(default=True, description=_EXPAND_DESC)
    wait_ready: bool = False


class TelescopeRequest(_TelescopeScrapeBody):
    fields: list[CaptureField] = Field(
        default_factory=lambda: ["text", "links"],
        description=_FIELDS_DESC,
    )

    @field_validator("fields")
    @classmethod
    def _normalize_fields(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("fields must include at least one of: text, links, html")
        bad = [f for f in v if f not in CAPTURE_FIELDS]
        if bad:
            raise ValueError(f"invalid fields: {bad}")
        seen: set[str] = set()
        out: list[str] = []
        for field in v:
            if field not in seen:
                seen.add(field)
                out.append(field)
        return out


class TelescopeHtmlRequest(_TelescopeScrapeBody):
    """Legacy /telescope/html — same body minus fields; always html-only."""


def _resolve_body_selector(
    *,
    selector: Optional[str],
    tag: Optional[str],
    class_name: Optional[str],
    id: Optional[str] = None,
) -> Optional[str]:
    """Map request filter fields to the CSS string capture_* expects; 400 on bad input."""
    try:
        resolved = resolve_capture_query(
            selector=selector, tag=tag, class_name=class_name, id=id
        )
    except CaptureQueryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    # Log primary (+ optional class/id) without dumping page content
    primary = (tag or "").strip() or (selector or "").strip() or None
    cn = (class_name or "").strip() or None
    eid = (id or "").strip() or None
    if primary or cn or eid:
        _log.info(
            "telescope filter mode=primary(+class/id) primary=%s class_name=%s id=%s resolved=%s",
            primary,
            cn,
            eid,
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

    max_attempts = settings.scrape_retry_count + 1
    last_exc: Optional[Exception] = None
    for attempt in range(max_attempts):
        try:
            result = await asyncio.wait_for(
                _job(),
                timeout=settings.request_timeout_seconds,
            )
            return result, cookies_dismissed
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
            last_exc = exc
            if attempt + 1 >= max_attempts:
                break
            delay_s = settings.scrape_retry_base_delay_seconds * (2**attempt)
            _log.warning(
                "telescope scrape retry url=%s attempt=%d/%d delay_s=%s err=%s: %s",
                url,
                attempt + 2,
                max_attempts,
                delay_s,
                type(exc).__name__,
                exc,
            )
            await asyncio.sleep(delay_s)

    assert last_exc is not None
    _log.exception(
        "telescope scrape_failed url=%s\n  %s: %s",
        url,
        type(last_exc).__name__,
        last_exc,
    )
    raise HTTPException(status_code=502, detail="scrape_failed") from None


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


async def _scrape_with_fields(
    pool: BrowserPool,
    *,
    url: str,
    expand: bool,
    wait_ready: bool,
    sel: Optional[str],
    fields: list[str],
) -> dict:
    want = set(fields)

    async def work(page):
        out: dict = {"final_url": page.url}
        if "text" in want:
            out["text"] = await capture_text(page, sel)
        if "links" in want:
            out["links"] = await capture_links(page, sel)
        if "html" in want:
            out["html"] = await capture_html(page, sel)
        return out

    raw = await _run_browser_job(pool, url, expand, wait_ready, work)
    result, cookies_dismissed = _unwrap_job(raw)
    meta_src = result.get("text")
    if meta_src is None:
        meta_src = result.get("html")
    result["scrape_meta"] = build_scrape_meta(
        requested_url=url,
        final_url=result.get("final_url") or "",
        text_or_html=meta_src,
        cookies_dismissed=cookies_dismissed,
    )
    return result


@app.post("/telescope", dependencies=[Depends(require_bearer)])
async def post_telescope(request: Request, body: TelescopeRequest):
    url = (body.url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    sel = _resolve_body_selector(
        selector=body.selector,
        tag=body.tag,
        class_name=body.class_name,
        id=body.id,
    )
    pool: BrowserPool = request.app.state.pool
    result = await _scrape_with_fields(
        pool,
        url=url,
        expand=body.expand,
        wait_ready=body.wait_ready,
        sel=sel,
        fields=body.fields,
    )
    _log.info(
        "telescope ok method=/telescope final_url=%s fields=%s",
        result.get("final_url"),
        list(body.fields),
    )
    return result


@app.post("/telescope/html", dependencies=[Depends(require_bearer)])
async def post_telescope_html(request: Request, body: TelescopeHtmlRequest):
    url = (body.url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    sel = _resolve_body_selector(
        selector=body.selector,
        tag=body.tag,
        class_name=body.class_name,
        id=body.id,
    )
    pool: BrowserPool = request.app.state.pool
    result = await _scrape_with_fields(
        pool,
        url=url,
        expand=body.expand,
        wait_ready=body.wait_ready,
        sel=sel,
        fields=["html"],
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
