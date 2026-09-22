"""Optional scrape debug events — console only when request debug=True."""

from __future__ import annotations

import contextvars
from typing import Any, Optional

from logging_util import get_logger, railway_log

_log = get_logger("scrape_debug")

_scrape_debug: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "telescope_scrape_debug",
    default=False,
)


def scrape_debug_enabled() -> bool:
    return _scrape_debug.get()


def enable_scrape_debug() -> contextvars.Token[bool]:
    return _scrape_debug.set(True)


def disable_scrape_debug(token: contextvars.Token[bool]) -> None:
    _scrape_debug.reset(token)


def scrape_debug_event(event: str, **fields: Any) -> None:
    """Emit one structured debug line to console when scrape debug is on."""
    if not _scrape_debug.get():
        return
    railway_log(
        "debug",
        _log,
        f"telescope scrape {event}",
        event=event,
        **fields,
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
        "telescope scrape scrape_capture",
        event="scrape_capture",
        text_chars=_text_size(result.get("text")),
        html_chars=_text_size(result.get("html")),
        link_count=_link_count(result.get("links")),
        final_url=(result.get("final_url") or ""),
    )


def firefox_label(slot_id: Optional[int], *, ephemeral: bool = False) -> str:
    if ephemeral:
        return "ephemeral"
    if slot_id is None:
        return "unknown"
    return f"slot_{slot_id}"
