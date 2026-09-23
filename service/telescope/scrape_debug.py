"""Optional scrape debug events — console only when request debug=True."""

from __future__ import annotations

import contextvars
import threading
from typing import Any, Optional, Tuple

from logging_util import get_logger, railway_log

_log = get_logger("scrape_debug")

_scrape_debug: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "telescope_scrape_debug",
    default=False,
)

_scrape_tx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_tx",
    default=None,
)
_scrape_url: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_url",
    default=None,
)
_scrape_container: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_container",
    default=None,
)
_scrape_firefox: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "telescope_scrape_firefox",
    default=None,
)

_id_lock = threading.Lock()
_tx_counter = 0
_firefox_counter = 0

# Pool slot bookkeeping — annotate with C-xxx.
_CONTAINER_EVENTS = frozenset({
    "slot_acquired",
    "slot_released",
    "slot_created",
    "slot_wait",
    "slot_acquire_aborted",
})

# One Firefox process lifetime — annotate with F-xxx.
_FIREFOX_EVENTS = frozenset({
    "firefox_launched",
    "firefox_closed",
    "firefox_recover",
    "context_created",
    "context_closed",
    "page_created",
    "navigate_start",
    "navigate_done",
    "ready_state",
    "scrape_capture",
})


def scrape_debug_enabled() -> bool:
    return _scrape_debug.get()


def enable_scrape_debug() -> contextvars.Token[bool]:
    return _scrape_debug.set(True)


def disable_scrape_debug(token: contextvars.Token[bool]) -> None:
    _scrape_debug.reset(token)


def container_label(slot_id: Optional[int], *, ephemeral: bool = False) -> str:
    if ephemeral:
        return "ephemeral"
    if slot_id is None:
        return "unknown"
    return f"C-{slot_id + 1:03d}"


def alloc_firefox_instance_id() -> str:
    global _firefox_counter
    with _id_lock:
        _firefox_counter += 1
        return f"F-{_firefox_counter:03d}"


def firefox_label(
    slot_id: Optional[int] = None,
    *,
    ephemeral: bool = False,
    firefox_id: Optional[str] = None,
) -> str:
    """Current Firefox instance id for structured log fields."""
    if firefox_id:
        return firefox_id
    bound = _scrape_firefox.get()
    if bound:
        return bound
    if ephemeral:
        return "ephemeral"
    _ = slot_id
    return "F-?"


def _next_tx_id() -> str:
    global _tx_counter
    with _id_lock:
        _tx_counter += 1
        return f"T-{_tx_counter:03d}"


def current_tx_id() -> Optional[str]:
    return _scrape_tx.get()


def current_firefox_id() -> Optional[str]:
    return _scrape_firefox.get()


def begin_scrape_request(url: str) -> Tuple[str, Tuple[Any, ...]]:
    """Bind one transaction id + requested url for this POST /telescope."""
    tx_id = _next_tx_id()
    tokens = (
        _scrape_tx.set(tx_id),
        _scrape_url.set(url),
        _scrape_container.set(None),
        _scrape_firefox.set(None),
    )
    return tx_id, tokens


def end_scrape_request(tokens: Tuple[Any, ...]) -> None:
    _scrape_tx.reset(tokens[0])
    _scrape_url.reset(tokens[1])
    _scrape_container.reset(tokens[2])
    _scrape_firefox.reset(tokens[3])


def bind_scrape_container(slot_id: Optional[int], *, ephemeral: bool = False) -> None:
    _scrape_container.set(container_label(slot_id, ephemeral=ephemeral))


def bind_scrape_firefox(firefox_id: str) -> None:
    _scrape_firefox.set(firefox_id)


def _actor_label(event: str) -> str:
    if event in _CONTAINER_EVENTS:
        return _scrape_container.get() or "C-?"
    if event in _FIREFOX_EVENTS:
        return _scrape_firefox.get() or "F-?"
    return _scrape_tx.get() or "T-?"


def _event_message(event: str, **fields: Any) -> str:
    actor = _actor_label(event)
    msg = f"telescope scrape {actor} {event}"
    url = (
        fields.get("url")
        or fields.get("requested_url")
        or _scrape_url.get()
        or ""
    )
    if url and event in {
        "request_start",
        "navigate_start",
        "navigate_done",
        "request_done",
        "scrape_capture",
    }:
        msg += f" url={url}"
    if event == "navigate_done" and fields.get("final_url"):
        msg += f" final_url={fields['final_url']}"
    return msg


def scrape_debug_event(event: str, **fields: Any) -> None:
    """Emit one structured debug line to console when scrape debug is on."""
    if not _scrape_debug.get():
        return
    extra = dict(fields)
    for key in ("event", "tx", "container", "firefox", "requested_url"):
        extra.pop(key, None)
    railway_log(
        "debug",
        _log,
        _event_message(event, **fields),
        event=event,
        tx=_scrape_tx.get(),
        container=_scrape_container.get(),
        firefox=_scrape_firefox.get() or fields.get("firefox"),
        requested_url=_scrape_url.get(),
        **extra,
    )


def _text_size(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, list):
        return sum(len(str(item or "")) for item in value)
    return len(str(value))


def _link_count(value: Any) -> int:
    if not value:
        return 0
    if isinstance(value, list):
        return len(value)
    return 0


def log_scrape_capture(result: dict) -> None:
    """Log capture sizes after scrape work completes."""
    if not _scrape_debug.get():
        return
    railway_log(
        "debug",
        _log,
        _event_message(
            "scrape_capture",
            url=_scrape_url.get(),
            final_url=(result.get("final_url") or ""),
        ),
        event="scrape_capture",
        tx=_scrape_tx.get(),
        container=_scrape_container.get(),
        firefox=_scrape_firefox.get(),
        requested_url=_scrape_url.get(),
        text_chars=_text_size(result.get("text")),
        html_chars=_text_size(result.get("html")),
        link_count=_link_count(result.get("links")),
        final_url=(result.get("final_url") or ""),
    )
