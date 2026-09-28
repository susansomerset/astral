"""Console-only logging for Telescope — Railway-native JSON to stdout.

Every line carries the replica's ``worker`` label; lines logged while a job runs
also carry ``job`` / ``attempt`` / ``firefox`` (see joblog.py). Railway's log
search can filter on those fields.

Debug lines from Telescope's own modules print only while a job with debug=True
is running (or when TELESCOPE_LOG_LEVEL=DEBUG) — callers just call ``_log.debug``.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Callable, Optional

from settings import settings

# Python levelno → Railway Log Explorer severity (debug | info | warn | error).
_RAILWAY_LEVELS = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warn",
    logging.ERROR: "error",
    logging.CRITICAL: "error",
}

# LogRecord attrs we never copy into the JSON payload.
_SKIP_RECORD_KEYS = frozenset(
    {
        "name",
        "msg",
        "args",
        "created",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "exc_info",
        "exc_text",
        "thread",
        "threadName",
        "taskName",
    }
)


# Loggers whose debug lines follow a job's debug flag (library loggers never do).
_OWN_LOGGERS = frozenset(
    {"app", "worker", "browser", "scrape", "interact", "capture", "meta", "jobqueue", "joblog"}
)

_worker_label: Optional[str] = None
_context_fields: Callable[[], dict[str, Any]] = dict
_job_debug: Callable[[], bool] = lambda: False


def set_worker_label(label: Optional[str]) -> None:
    global _worker_label
    _worker_label = label


def worker_label() -> str:
    return _worker_label or "-"


def register_job_context(
    fields: Callable[[], dict[str, Any]], debug: Callable[[], bool]
) -> None:
    """joblog.py plugs in the current job's fields and debug flag."""
    global _context_fields, _job_debug
    _context_fields = fields
    _job_debug = debug


class _LevelOrJobDebug(logging.Filter):
    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= self.level:
            return True
        return record.name in _OWN_LOGGERS and _job_debug()


class RailwayJsonHandler(logging.Handler):
    """Emit one JSON object per line on stdout for Railway level coloring/filtering."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = _RAILWAY_LEVELS.get(record.levelno, "info")
            payload: dict[str, Any] = {
                "message": record.getMessage(),
                "level": level,
                "logger": record.name,
            }
            if _worker_label:
                payload["worker"] = _worker_label
            ctx = _context_fields()
            payload.update(ctx)
            if record.levelno < logging.INFO and _worker_label:
                # Debug text carries the replica (and job) so a text filter on the
                # worker id finds the walk-through, not only the structured field.
                job = ctx.get("job")
                prefix = f"{_worker_label} {job}" if job else _worker_label
                payload["message"] = f"{prefix} | {payload['message']}"
            if record.exc_info:
                payload["exception"] = self.formatException(record.exc_info)
            for key, value in record.__dict__.items():
                if key in _SKIP_RECORD_KEYS or key.startswith("_"):
                    continue
                payload[key] = value
            sys.stdout.write(
                json.dumps(payload, default=str, ensure_ascii=False) + "\n"
            )
            sys.stdout.flush()
        except Exception:
            self.handleError(record)


def configure_logging() -> None:
    """Attach the Railway JSON handler to root; honor TELESCOPE_LOG_LEVEL via settings."""
    level_name = (settings.log_level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    # Root passes everything; the handler filter decides (level, or a debug job).
    root.setLevel(logging.DEBUG)
    for name in ("asyncio", "asyncpg", "playwright"):
        logging.getLogger(name).setLevel(max(level, logging.INFO))
    # uvicorn's own logging setup (run before this, at Config() construction time) gives
    # uvicorn.error/uvicorn.access their own handler wired to stderr/stdout with propagate=False —
    # INFO lifecycle lines ("Uvicorn running on...", "Shutting down") land on stderr regardless of
    # level, and Railway reads severity off the stream, so they show up flagged as errors. Strip
    # uvicorn's handlers and let these loggers fall through to our RailwayJsonHandler instead, so
    # they get the same stdout JSON payload (with a correct "level" field) as everything else.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True
        lg.setLevel(max(level, logging.INFO))
    for handler in root.handlers:
        if isinstance(handler, RailwayJsonHandler):
            handler.filters = [_LevelOrJobDebug(level)]
            return
    handler = RailwayJsonHandler()
    handler.addFilter(_LevelOrJobDebug(level))
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
