"""Optional scrape debug events — narrative T/C/F tracing when request debug=True.

T = one POST /telescope (the URL request you are following).
C = one Playwright browser context (1:1 with T for that request).
F = one Firefox process (may serve many concurrent T/C pairs).
"""

from __future__ import annotations

import contextvars
from typing import Any, List, Optional, Tuple

# Per-request narrative ids — reset each POST /telescope (not global serials).
_REQUEST_ID = "T-001"
_CONTEXT_ID = "C-001"
_FIREFOX_ID = "F-001"

from logging_util import get_logger, railway_log

_log = get_logger("scrape_debug")

_scrape_debug: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "telescope_scrape_debug",
    default=False,
)

_scrape_request: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_request",
    default=None,
)
_scrape_url: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_url",
    default=None,
)
_scrape_fields: contextvars.ContextVar[Optional[List[str]]] = contextvars.ContextVar(
    "telescope_scrape_fields",
    default=None,
)
_scrape_firefox: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_firefox",
    default=None,
)
_scrape_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_context",
    default=None,
)
_scrape_pool_size: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "telescope_scrape_pool_size",
    default=None,
)
_scrape_pool_cap: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "telescope_scrape_pool_cap",
    default=None,
)
_scrape_active_pages: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "telescope_scrape_active_pages",
    default=None,
)
_scrape_contexts_cap: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar(
    "telescope_scrape_contexts_cap",
    default=None,
)

# Internal pool bookkeeping — not part of the T/C/F call story.
_POOL_EVENTS = frozenset({
    "slot_acquired",
    "slot_released",
    "slot_created",
    "slot_wait",
    "slot_acquire_aborted",
})


def scrape_debug_enabled() -> bool:
    return _scrape_debug.get()


def enable_scrape_debug() -> contextvars.Token[bool]:
    return _scrape_debug.set(True)


def disable_scrape_debug(token: contextvars.Token[bool]) -> None:
    _scrape_debug.reset(token)


def alloc_firefox_instance_id() -> str:
    """Narrative Firefox id for this request (always F-001)."""
    return _FIREFOX_ID


def alloc_context_id() -> str:
    """Narrative context id for this request (always C-001, 1:1 with T)."""
    return _CONTEXT_ID


def current_request_id() -> Optional[str]:
    return _scrape_request.get()


def current_context_id() -> Optional[str]:
    return _scrape_context.get()


def current_firefox_id() -> Optional[str]:
    return _scrape_firefox.get()


def firefox_label(*, firefox_id: Optional[str] = None) -> str:
    if firefox_id:
        return firefox_id
    return _scrape_firefox.get() or "F-?"


def begin_scrape_request(url: str, *, fields: Optional[List[str]] = None) -> Tuple[str, Tuple[Any, ...]]:
    """Bind T-001 for one POST /telescope (the URL call to follow)."""
    tokens = (
        _scrape_request.set(_REQUEST_ID),
        _scrape_url.set(url),
        _scrape_fields.set(list(fields) if fields else None),
        _scrape_firefox.set(None),
        _scrape_context.set(None),
        _scrape_pool_size.set(None),
        _scrape_pool_cap.set(None),
        _scrape_active_pages.set(None),
        _scrape_contexts_cap.set(None),
    )
    return _REQUEST_ID, tokens


def end_scrape_request(tokens: Tuple[Any, ...]) -> None:
    _scrape_request.reset(tokens[0])
    _scrape_url.reset(tokens[1])
    _scrape_fields.reset(tokens[2])
    _scrape_firefox.reset(tokens[3])
    _scrape_context.reset(tokens[4])
    _scrape_pool_size.reset(tokens[5])
    _scrape_pool_cap.reset(tokens[6])
    _scrape_active_pages.reset(tokens[7])
    _scrape_contexts_cap.reset(tokens[8])


def bind_scrape_firefox(firefox_id: str) -> None:
    _scrape_firefox.set(firefox_id)


def bind_scrape_context(context_id: str) -> None:
    _scrape_context.set(context_id)


def bind_pool_caps(
    *,
    pool_size: Optional[int] = None,
    pool_cap: Optional[int] = None,
    active_pages: Optional[int] = None,
    contexts_cap: Optional[int] = None,
) -> None:
    if pool_size is not None:
        _scrape_pool_size.set(pool_size)
    if pool_cap is not None:
        _scrape_pool_cap.set(pool_cap)
    if active_pages is not None:
        _scrape_active_pages.set(active_pages)
    if contexts_cap is not None:
        _scrape_contexts_cap.set(contexts_cap)


def _pool_cap_suffix(**fields: Any) -> str:
    cap = fields.get("pool_cap", _scrape_pool_cap.get())
    idx = fields.get("pool_size", _scrape_pool_size.get())
    if idx is None and fields.get("slot_id") is not None:
        idx = int(fields["slot_id"]) + 1
    if idx is not None and cap is not None:
        return f" ({idx} of {cap})"
    return ""


def _context_cap_suffix(**fields: Any) -> str:
    active = fields.get("active_pages", _scrape_active_pages.get())
    cap = fields.get("contexts_cap", _scrape_contexts_cap.get())
    if active is not None and cap is not None:
        return f" ({active} of {cap})"
    return ""


def _event_message(event: str, **fields: Any) -> str:
    t = _scrape_request.get() or "T-?"
    f = fields.get("firefox") or _scrape_firefox.get() or "F-?"
    c = fields.get("context") or _scrape_context.get() or "C-?"
    url = fields.get("url") or _scrape_url.get() or ""
    req_fields = fields.get("fields") or _scrape_fields.get() or []

    if event in _POOL_EVENTS:
        slot = fields.get("slot_id")
        label = f"S-{int(slot) + 1:03d}" if slot is not None else "S-?"
        return f"telescope pool {label}{_pool_cap_suffix(**fields)} {event}"

    if event == "request_start":
        fl = ", ".join(str(x) for x in req_fields)
        return f"{t}: Requested url {url}, {fl}" if fl else f"{t}: Requested url {url}"

    if event == "request_done":
        return f"{t}: Request Return Successful"

    if event == "firefox_needed":
        live = fields.get("live_count", 0)
        new_f = fields.get("firefox_id") or f
        return f'{t}: Live Firefox Instances: {live}, creating "{new_f}"'

    if event == "request_context":
        return f"{t}: Requesting context from {f}{_context_cap_suffix(**fields)}"

    if event == "firefox_launched":
        return f"{f}: Starting firefox app with playwright"

    if event == "context_created":
        return f'{f}: Creating context "{c}"'

    if event == "page_created":
        return f"{c}: Starting context"

    if event == "navigate_start":
        return f"{c}: Loading Page"

    if event == "navigate_done":
        final = fields.get("final_url") or url
        return f"{c}: Page loaded final_url={final}"

    if event == "scrape_field":
        return f"{c}: Scraping Page for {fields.get('field', '?')}"

    if event == "context_closed":
        return f"{c}: Close Page"

    if event == "context_recycled":
        ctx = fields.get("context") or c
        return f'{f}: Recycle Context "{ctx}"'

    if event == "firefox_closed":
        return f"{f}: Close Instance"

    if event == "firefox_recover":
        reason = fields.get("reason") or "recover"
        return f"{f}: Recover Instance reason={reason}"

    if event == "ready_state":
        return f"{c}: wait_ready outcome={fields.get('outcome', '?')}"

    # Fallback for any unexpected event name.
    return f"telescope scrape {event}"


def scrape_debug_event(event: str, **fields: Any) -> None:
    """Emit one structured debug line to console when scrape debug is on."""
    if not _scrape_debug.get():
        return
    extra = dict(fields)
    for key in ("event", "request", "firefox", "context", "requested_url", "fields"):
        extra.pop(key, None)
    railway_log(
        "debug",
        _log,
        _event_message(event, **fields),
        event=event,
        request=_scrape_request.get(),
        firefox=_scrape_firefox.get() or fields.get("firefox"),
        context=_scrape_context.get() or fields.get("context"),
        requested_url=_scrape_url.get(),
        **extra,
    )


def log_scrape_capture(result: dict, *, capture_fields: Optional[List[str]] = None) -> None:
    """Log per-field capture on C — one line per requested capture key."""
    _ = result
    if not _scrape_debug.get():
        return
    fields = capture_fields if capture_fields is not None else (_scrape_fields.get() or [])
    for field in fields:
        if field in ("text", "links", "html"):
            scrape_debug_event("scrape_field", field=field)
