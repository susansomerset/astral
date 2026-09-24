"""Optional scrape debug events — narrative T/F/C tracing when a job has debug=True.

T = one queue job attempt (monotonic per process).
F = one Firefox launch (monotonic per process; concurrent T share the live F).
C = one Playwright browser context (monotonic per process; one per T).

Counters reset only on process restart / redeploy.
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
    """Next Firefox id for a new launch."""
    return _next_firefox_id()


def alloc_context_id() -> str:
    """Next context id, bound to the current job."""
    ctx_id = _next_context_id()
    bind_scrape_context(ctx_id)
    return ctx_id


def current_request_id() -> Optional[str]:
    return _scrape_request.get()


def current_context_id() -> Optional[str]:
    return _scrape_context.get()


def current_firefox_id() -> Optional[str]:
    return _scrape_firefox.get()


def scrape_correlation_tag(*, request_id: Optional[str] = None) -> str:
    """T with bound F/C — for info-level ok lines."""
    t = request_id or current_request_id() or "T-?"
    parts = [p for p in (_scrape_firefox.get(), _scrape_context.get()) if p]
    return f"{t} ({' '.join(parts)})" if parts else t


def firefox_label(*, firefox_id: Optional[str] = None) -> str:
    if firefox_id:
        return firefox_id
    return _scrape_firefox.get() or "F-?"


def begin_scrape_request(url: str, *, fields: Optional[List[str]] = None) -> Tuple[str, Tuple[Any, ...]]:
    """Start one job attempt — assigns the next T id."""
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


def bind_scrape_firefox(firefox_id: str) -> None:
    _scrape_firefox.set(firefox_id)


def bind_scrape_context(context_id: str) -> None:
    _scrape_context.set(context_id)


def _url_suffix(url: str) -> str:
    """Requested url tail — appended on scrape narrative lines when known."""
    u = (url or "").strip()
    return f" url={u}" if u else ""


def _request_with_fc(
    *,
    firefox: Optional[str] = None,
    context: Optional[str] = None,
) -> str:
    """T label with bound F/C when assigned."""
    t = _scrape_request.get() or "T-?"
    parts = [
        p
        for p in (firefox or _scrape_firefox.get(), context or _scrape_context.get())
        if p
    ]
    if parts:
        return f"{t} ({' '.join(parts)})"
    return t


def _actor_prefix(
    kind: str,
    *,
    firefox: Optional[str] = None,
    context: Optional[str] = None,
) -> str:
    """Leading F/C label on per-actor narrative lines."""
    if kind == "f":
        return firefox or _scrape_firefox.get() or "F-?"
    return context or _scrape_context.get() or "C-?"


def _event_message(event: str, **fields: Any) -> str:
    t = _scrape_request.get() or "T-?"
    f = fields.get("firefox") or _scrape_firefox.get() or "F-?"
    c = fields.get("context") or _scrape_context.get() or "C-?"
    url = fields.get("url") or _scrape_url.get() or ""
    req_fields = fields.get("fields") or _scrape_fields.get() or []

    live = _live_suffix()

    url_tail = _url_suffix(url)

    if event == "request_start":
        fl = ", ".join(str(x) for x in req_fields)
        base = f"{t}: Accepted, {fl}" if fl else f"{t}: Accepted"
        return f"{base} (awaiting F/C){url_tail}{live}"

    if event == "request_serving":
        tag = _request_with_fc(
            firefox=f if f != "F-?" else None,
            context=c if c != "C-?" else None,
        )
        fl = ", ".join(str(x) for x in req_fields)
        base = f"{tag}: Requesting, {fl}" if fl else f"{tag}: Requesting"
        return f"{base}{url_tail}{live}"

    if event == "request_done":
        tag = _request_with_fc()
        return f"{tag}: Request Return Successful{url_tail}{live}"

    if event == "firefox_launched":
        actor = _actor_prefix("f", firefox=f if f != "F-?" else None)
        return f"{actor}: Starting firefox app with playwright{url_tail}{live}"

    if event == "context_created":
        actor = _actor_prefix("f", firefox=f if f != "F-?" else None)
        return f'{actor}: Creating context "{c}"{url_tail}{live}'

    if event == "page_created":
        actor = _actor_prefix("c", context=c if c != "C-?" else None)
        return f"{actor}: Starting context{url_tail}{live}"

    if event == "navigate_start":
        actor = _actor_prefix("c", context=c if c != "C-?" else None)
        return f"{actor}: Loading Page{url_tail}{live}"

    if event == "navigate_done":
        final = fields.get("final_url") or url
        actor = _actor_prefix("c", context=c if c != "C-?" else None)
        return f"{actor}: Page loaded final_url={final}{url_tail}{live}"

    if event == "scrape_field":
        actor = _actor_prefix("c", context=c if c != "C-?" else None)
        return f"{actor}: Scraping Page for {fields.get('field', '?')}{url_tail}{live}"

    if event == "context_closed":
        actor = _actor_prefix("c", context=c if c != "C-?" else None)
        return f"{actor}: Close Page{url_tail}{live}"

    if event == "context_recycled":
        ctx = fields.get("context") or c
        actor = _actor_prefix("f", firefox=f if f != "F-?" else None)
        return f'{actor}: Recycle Context "{ctx}"{url_tail}{live}'

    if event == "firefox_closed":
        actor = _actor_prefix("f", firefox=f if f != "F-?" else None)
        return f"{actor}: Close Instance{url_tail}{live}"

    if event == "firefox_recover":
        reason = fields.get("reason") or "recover"
        actor = _actor_prefix("f", firefox=f if f != "F-?" else None)
        return f"{actor}: Recover Instance reason={reason}{url_tail}{live}"

    if event == "ready_state":
        actor = _actor_prefix("c", context=c if c != "C-?" else None)
        return f"{actor}: wait_ready outcome={fields.get('outcome', '?')}{url_tail}{live}"

    return f"telescope scrape {event}"


def scrape_debug_event(event: str, **fields: Any) -> None:
    """Emit one structured debug line to console when scrape debug is on.

    Live F/C counters update on every event, debug or not — Firefox usually
    launches outside any debug job, and the counts must still be right.
    """
    _adjust_live_for_event(
        event,
        firefox=fields.get("firefox") or _scrape_firefox.get(),
        context=fields.get("context") or _scrape_context.get(),
    )
    if not _scrape_debug.get():
        return
    ff = fields.get("firefox") or _scrape_firefox.get()
    ctx = fields.get("context") or _scrape_context.get()
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
