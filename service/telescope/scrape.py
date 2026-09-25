"""One scrape job: validate the request, drive one page load, return the capture dict."""

from __future__ import annotations

import asyncio
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

from browser import Firefox
from capture import (
    CaptureQueryError,
    capture_html,
    capture_links,
    capture_text,
    resolve_capture_query,
)
from interact import dismiss_cookies, expand_page, navigate, wait_ready_generic
from logging_util import get_logger
from meta import build_scrape_meta
from joblog import capture_summary
from settings import settings

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
    "What to extract from one page load. Result includes final_url, scrape_meta, "
    "and only the requested capture keys (text, links, html)."
)


class TelescopeRequest(BaseModel):
    url: str
    fields: list[CaptureField] = Field(
        default_factory=lambda: ["text", "links"],
        description=_FIELDS_DESC,
    )
    selector: Optional[str] = Field(default=None, description=_PRIMARY_DESC)
    tag: Optional[str] = Field(default=None, description=_TAG_DESC)
    class_name: Optional[str] = Field(default=None, description=_CLASS_DESC)
    id: Optional[str] = Field(default=None, description=_ID_DESC)
    expand: bool = Field(default=True, description=_EXPAND_DESC)
    wait_ready: bool = False
    debug: bool = Field(
        default=False,
        description=(
            "When true, emit structured scrape debug events to the service console "
            "(Firefox / context lifecycle, navigation, ready state, capture sizes)."
        ),
    )

    @field_validator("url")
    @classmethod
    def _require_url(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("url required")
        return v

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


class ScrapeError(Exception):
    """A failed attempt. error_class drives retry: bad_request never retries."""

    def __init__(self, error_class: str, message: str) -> None:
        super().__init__(message)
        self.error_class = error_class


def parse_request(raw: Any) -> tuple[TelescopeRequest, Optional[str]]:
    """Validate a job's request payload and resolve its CSS selector."""
    try:
        req = TelescopeRequest.model_validate(raw)
    except ValidationError as exc:
        raise ScrapeError("bad_request", str(exc)) from None
    try:
        sel = resolve_capture_query(
            selector=req.selector, tag=req.tag, class_name=req.class_name, id=req.id
        )
    except CaptureQueryError as exc:
        raise ScrapeError("bad_request", str(exc)) from None
    primary = (req.tag or "").strip() or (req.selector or "").strip() or None
    cn = (req.class_name or "").strip() or None
    eid = (req.id or "").strip() or None
    if primary or cn or eid:
        _log.debug(
            "Filter: primary=%s class_name=%s id=%s resolved=%s",
            primary,
            cn,
            eid,
            sel,
        )
    return req, sel


async def run_scrape(
    firefox: Firefox, req: TelescopeRequest, sel: Optional[str]
) -> dict:
    """One attempt. Raises ScrapeError("timeout" | "scrape_failed", …) on failure."""
    want = set(req.fields)
    cookies_dismissed = False

    async def _scrape(page: Any) -> dict:
        nonlocal cookies_dismissed
        await navigate(page, req.url)
        cookies_dismissed = await dismiss_cookies(page)
        if req.expand:
            await expand_page(page)
        if req.wait_ready:
            await wait_ready_generic(page)
        out: dict = {"final_url": page.url}
        if "text" in want:
            out["text"] = await capture_text(page, sel)
        if "links" in want:
            out["links"] = await capture_links(page, sel)
        if "html" in want:
            out["html"] = await capture_html(page, sel)
        _log.debug("Captured %s", capture_summary(out))
        return out

    try:
        # Scrape budget starts once the job has its page (Firefox relaunch excluded).
        async with firefox.page() as page:
            result = await asyncio.wait_for(
                _scrape(page), timeout=settings.request_timeout_seconds
            )
    except asyncio.TimeoutError:
        raise ScrapeError(
            "timeout", f"scrape exceeded {settings.request_timeout_seconds}s"
        ) from None
    except Exception as exc:
        raise ScrapeError("scrape_failed", f"{type(exc).__name__}: {exc}") from exc

    meta_src = result.get("text")
    if meta_src is None:
        meta_src = result.get("html")
    result["scrape_meta"] = build_scrape_meta(
        requested_url=req.url,
        final_url=result.get("final_url") or "",
        text_or_html=meta_src,
        cookies_dismissed=cookies_dismissed,
    )
    return result
