"""Per-job log context.

While a job runs, every log line carries ``job`` (first 8 chars of its id),
``attempt`` (e.g. 2/4) and, once it has a page, ``firefox`` (e.g. F-003 — the
Firefox launch serving it, numbered per process). The job's ``debug`` flag, set
by the platform from its log_debug, turns on that job's ``_log.debug`` lines.
"""

from __future__ import annotations

import contextvars
import itertools
from typing import Any, Optional, Tuple

from logging_util import register_job_context

_debug: contextvars.ContextVar[bool] = contextvars.ContextVar("telescope_job_debug", default=False)
_job: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("telescope_job", default=None)
_attempt: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("telescope_attempt", default=None)
_firefox: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("telescope_firefox", default=None)

_firefox_seq = itertools.count(1)


def short_id(job_id: str) -> str:
    return (job_id or "-")[:8]


def alloc_firefox_id() -> str:
    return f"F-{next(_firefox_seq):03d}"


def bind_firefox(firefox_id: str) -> None:
    _firefox.set(firefox_id)


def begin_job(
    job_id: str, *, attempt: int, max_attempts: int, debug: bool
) -> Tuple[Any, ...]:
    return (
        _job.set(short_id(job_id)),
        _attempt.set(f"{attempt}/{max_attempts}"),
        _firefox.set(None),
        _debug.set(bool(debug)),
    )


def end_job(tokens: Tuple[Any, ...]) -> None:
    for var, token in zip((_job, _attempt, _firefox, _debug), tokens):
        var.reset(token)


def job_debug() -> bool:
    return _debug.get()


def _fields() -> dict[str, Any]:
    out: dict[str, Any] = {}
    if _job.get():
        out["job"] = _job.get()
        out["attempt"] = _attempt.get()
    if _firefox.get():
        out["firefox"] = _firefox.get()
    return out


def capture_summary(result: dict) -> str:
    """Sizes of what a scrape captured, e.g. ``text:5120 links:37``."""
    parts = []
    for key in ("text", "links", "html"):
        if key not in result:
            continue
        val = result[key]
        if key == "links":
            parts.append(f"links:{len(val or [])}")
        elif isinstance(val, list):
            parts.append(f"{key}:{sum(len(v or '') for v in val)}({len(val)} matches)")
        else:
            parts.append(f"{key}:{len(val or '')}")
    return " ".join(parts) or "-"


register_job_context(_fields, job_debug)
