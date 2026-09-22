"""Console-only logging for Telescope — Railway-native JSON to stdout."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

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
    """Attach Railway JSON handler to root; honor TELESCOPE_LOG_LEVEL via settings."""
    level_name = (settings.log_level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    for handler in root.handlers:
        if isinstance(handler, RailwayJsonHandler):
            handler.setLevel(level)
            return
    handler = RailwayJsonHandler()
    handler.setLevel(level)
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def railway_log(
    level: str,
    logger: logging.Logger,
    message: str,
    **fields: Any,
) -> None:
    """Emit one Railway JSON line with an explicit severity (bypasses logger level gate)."""
    lvl = (level or "info").lower()
    if lvl not in ("debug", "info", "warn", "error"):
        lvl = "info"
    payload: dict[str, Any] = {
        "message": message,
        "level": lvl,
        "logger": logger.name,
    }
    payload.update(fields)
    sys.stdout.write(json.dumps(payload, default=str, ensure_ascii=False) + "\n")
    sys.stdout.flush()
