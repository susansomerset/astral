"""Optional scrape debug events — narrative T/C/F tracing when request debug=True.

T = one POST /telescope (monotonic per deployment).
C = one Playwright browser context (monotonic per deployment).
F = one Firefox process (monotonic per deployment; concurrent T may share one F).

Counters reset only on process restart / redeploy — not per POST or pool retry.
"""

from __future__ import annotations

import contextvars
import threading
from typing import Any, List, Optional, Tuple

from logging_util import get_logger, railway_log

_log = get_logger("scrape_debug")

_counter_lock = threading.Lock()
_deploy_request_seq = 0
_deploy_firefox_seq = 0
_deploy_context_seq = 0

# Globally live instances — inc on start, dec on close/recycle (debug visibility).
_live_requests = 0
_live_firefox_ids: set[str] = set()
_live_context_ids: set[str] = set()

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


def _next_request_id() -> str:
    global _deploy_request_seq
    with _counter_lock:
        _deploy_request_seq += 1
        seq = _deploy_request_seq
    return f"T-{seq:03d}"


def _next_firefox_id() -> str:
    global _deploy_firefox_seq
    with _counter_lock:
        _deploy_firefox_seq += 1
        seq = _deploy_firefox_seq
    return f"F-{seq:03d}"


def _next_context_id() -> str:
    global _deploy_context_seq
    with _counter_lock:
        _deploy_context_seq += 1
        seq = _deploy_context_seq
    return f"C-{seq:03d}"


def live_instance_counts() -> dict[str, int]:
    """Snapshot of globally live T/F/C instances (for tests and structured logs)."""
    with _counter_lock:
        return {
            "live_requests": _live_requests,
            "live_firefox": len(_live_firefox_ids),
            "live_contexts": len(_live_context_ids),
        }


def _live_suffix() -> str:
    counts = live_instance_counts()
    return (
        f" [live T={counts['live_requests']}"
        f" F={counts['live_firefox']}"
        f" C={counts['live_contexts']}]"
    )


def _adjust_live_for_event(event: str, *, firefox: Optional[str], context: Optional[str]) -> None:
    global _live_requests
    with _counter_lock:
        if event == "firefox_launched" and firefox:
            _live_firefox_ids.add(firefox)
        elif event == "firefox_closed" and firefox:
            _live_firefox_ids.discard(firefox)
        elif event == "context_created" and context:
            _live_context_ids.add(context)
        elif event == "context_closed" and context:
            _live_context_ids.discard(context)


def scrape_debug_enabled() -> bool:
    return _scrape_debug.get()


def enable_scrape_debug() -> contextvars.Token[bool]:
    return _scrape_debug.set(True)


def disable_scrape_debug(token: contextvars.Token[bool]) -> None:
    _scrape_debug.reset(token)


def alloc_firefox_instance_id() -> str:
    """Next Firefox id for a new process, or reuse id bound to this POST."""
    bound = _scrape_firefox.get()
    if bound:
        return bound
    ff_id = _next_firefox_id()
    bind_scrape_firefox(ff_id)
    return ff_id


def alloc_context_id() -> str:
    """Next context id for this POST (pool retries reuse the same id)."""
    bound = _scrape_context.get()
    if bound:
        return bound
    ctx_id = _next_context_id()
    bind_scrape_context(ctx_id)
    return ctx_id


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
    """Start one POST /telescope — assigns next deployment-wide T id."""
    global _live_requests
    request_id = _next_request_id()
    with _counter_lock:
        _live_requests += 1
    tokens = (
        _scrape_request.set(request_id),
        _scrape_url.set(url),
        _scrape_fields.set(list(fields) if fields else None),
        _scrape_firefox.set(None),
        _scrape_context.set(None),
        _scrape_pool_size.set(None),
        _scrape_pool_cap.set(None),
        _scrape_active_pages.set(None),
        _scrape_contexts_cap.set(None),
    )
    return request_id, tokens


def end_scrape_request(tokens: Tuple[Any, ...]) -> None:
    global _live_requests
    with _counter_lock:
        _live_requests = max(0, _live_requests - 1)
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

    live = _live_suffix()

    if event == "request_start":
        fl = ", ".join(str(x) for x in req_fields)
        base = f"{t}: Requested url {url}, {fl}" if fl else f"{t}: Requested url {url}"
        return f"{base}{live}"

    if event == "request_done":
        return f"{t}: Request Return Successful{live}"

    if event == "firefox_needed":
        counts = live_instance_counts()
        new_f = fields.get("firefox_id") or f
        return (
            f'{t}: Live Firefox Instances: {counts["live_firefox"]}, '
            f'creating "{new_f}"{live}'
        )

    if event == "request_context":
        return f"{t}: Requesting context from {f}{_context_cap_suffix(**fields)}{live}"

    if event == "firefox_launched":
        return f"{f}: Starting firefox app with playwright{live}"

    if event == "context_created":
        return f'{f}: Creating context "{c}"{live}'

    if event == "page_created":
        return f"{c}: Starting context{live}"

    if event == "navigate_start":
        return f"{c}: Loading Page{live}"

    if event == "navigate_done":
        final = fields.get("final_url") or url
        return f"{c}: Page loaded final_url={final}{live}"

    if event == "scrape_field":
        return f"{c}: Scraping Page for {fields.get('field', '?')}{live}"

    if event == "context_closed":
        return f"{c}: Close Page{live}"

    if event == "context_recycled":
        ctx = fields.get("context") or c
        return f'{f}: Recycle Context "{ctx}"{live}'

    if event == "firefox_closed":
        return f"{f}: Close Instance{live}"

    if event == "firefox_recover":
        reason = fields.get("reason") or "recover"
        return f"{f}: Recover Instance reason={reason}{live}"

    if event == "ready_state":
        return f"{c}: wait_ready outcome={fields.get('outcome', '?')}{live}"

    return f"telescope scrape {event}"


def scrape_debug_event(event: str, **fields: Any) -> None:
    """Emit one structured debug line to console when scrape debug is on."""
    if not _scrape_debug.get():
        return
    ff = fields.get("firefox") or _scrape_firefox.get()
    ctx = fields.get("context") or _scrape_context.get()
    _adjust_live_for_event(event, firefox=ff, context=ctx)
    msg = _event_message(event, **fields)
    counts = live_instance_counts()
    extra = dict(fields)
    for key in ("event", "request", "firefox", "context", "requested_url", "fields"):
        extra.pop(key, None)
    railway_log(
        "debug",
        _log,
        msg,
        event=event,
        request=_scrape_request.get(),
        firefox=ff,
        context=ctx,
        requested_url=_scrape_url.get(),
        live_requests=counts["live_requests"],
        live_firefox=counts["live_firefox"],
        live_contexts=counts["live_contexts"],
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
