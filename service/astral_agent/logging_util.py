"""Console-only logging for astral-agent — Railway-native JSON to stdout.

No platform SQLite or product log writers. Debug lines from own modules only when
ASTRAL_AGENT_LOG_LEVEL=DEBUG (_job_debug stays False until a later sibling wires
job context).
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Callable, Optional

from settings import settings

_RAILWAY_LEVELS = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warn",
    logging.ERROR: "error",
    logging.CRITICAL: "error",
}

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

_OWN_LOGGERS = frozenset({
    "app",
    "worker",
    "jobqueue",
    "executor",
    "providers",
    "providers.anthropic_provider",
    "providers.llm_compat_provider",
    "providers.openrouter_provider",
    "providers.errors",
})

_worker_label: Optional[str] = None
_context_fields: Callable[[], dict[str, Any]] = dict
_job_debug: Callable[[], bool] = lambda: False


def set_worker_label(label: Optional[str]) -> None:
    global _worker_label
    _worker_label = label


def worker_label() -> str:
    return _worker_label or "-"


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
    """Attach the Railway JSON handler to root; honor ASTRAL_AGENT_LOG_LEVEL via settings."""
    level_name = (settings.log_level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for name in ("asyncio", "asyncpg"):
        logging.getLogger(name).setLevel(max(level, logging.INFO))
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
