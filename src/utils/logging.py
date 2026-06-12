"""
Centralized logging utility for ASTRAL.

Provides a standardized logger interface that can be used across all layers.
Uses Python's standard logging module with consistent formatting.

Log output goes to both stdout and the app_log database table. The database
handler is the abstraction boundary — switching to Better Stack or another
provider means updating this module only.

B2 / D2 (AST-388): `add_log_entry` is imported inside `_flush_buffer` only (late import — utils must not load `data` at module import time). Handler errors print one line to stderr so failures are visible without crashing the logging caller.

The `log_batch_id` context var is set by the Dispatcher (ast-282) at the
start of each batch run. All log entries emitted during that run are
automatically tagged with the batch_id. Callers never set it directly.

Usage:
    from src.utils.logging import get_logger

    logger = get_logger(__name__, debug_flag=debug)
    logger.set_debug_flag(debug)
    logger.debug_index(
        func="module.batch_fn",
        index=1,
        total=10,
        identifier="acme",
        outcome="passed",
    )
    logger.debug_detail("hits=3")
    logger.debug_detail_block(long_multiline_text)

    logger.debug("Debug message")  # Automatically prefixed with "[ ~ ] "
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
"""

import atexit
import contextvars
import logging
import sys
import threading
from typing import Any, Optional

# Dispatcher sets this at batch run start; logging handler reads it on each emit
log_batch_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "log_batch_id", default=None
)

_FLUSH_THRESHOLD = 50

DEBUG_DETAIL_PREFIX = " | "  # two spaces, pipe, two spaces — working-log detail only
DEBUG_LINE_THRESHOLD = 50
DEBUG_HEAD_LINES = 15
DEBUG_TAIL_LINES = 15


def truncate_debug_content(text: str) -> list[str]:
    """Split text into lines; omit middle when over DEBUG_LINE_THRESHOLD lines.

    Callers should pass normalized text; splitlines() drops a terminal empty line.
    """
    lines = text.splitlines()
    if not lines:
        return []
    n = len(lines)
    if n <= DEBUG_LINE_THRESHOLD:
        return lines
    omitted = n - DEBUG_HEAD_LINES - DEBUG_TAIL_LINES
    return (
        lines[:DEBUG_HEAD_LINES]
        + [f"<{omitted} lines omitted>"]
        + lines[-DEBUG_TAIL_LINES:]
    )


def format_debug_index_header(
    *,
    func: str,
    index: int,
    total: int,
    identifier: str,
    outcome: str,
) -> str:
    """Per-index batch header (style D) — no DEBUG_DETAIL_PREFIX."""
    if total < 1 or index < 1 or index > total:
        raise ValueError(f"index must be 1..{total}, got {index}/{total}")
    return f"{func} index {index}/{total} {identifier} -> {outcome}"


def _db_handler_stderr(line: str) -> None:
    """Last-resort visibility when DB log buffering fails (D2 — never silent)."""
    try:
        sys.stderr.write(line + "\n")
    except Exception:
        pass


class _DatabaseLogHandler(logging.Handler):
    """Buffers log records and flushes to app_log table in batches.
    Late-imports database to avoid circular imports (utils must not import
    data at module load time)."""

    def __init__(self) -> None:
        super().__init__()
        self._buffer: list = []
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = {
                "level": record.levelname,
                "logger_name": record.name,
                "message": self.format(record),
                "batch_id": log_batch_id.get(),
            }
            with self._lock:
                self._buffer.append(entry)
                if len(self._buffer) >= _FLUSH_THRESHOLD:
                    self._flush_buffer()
        except Exception as ex:
            # Handler must not crash caller; stderr keeps D2 from silent loss (AST-388).
            _db_handler_stderr(f"[astral-log] emit failed: {ex!r}")

    def flush(self) -> None:
        """Flush buffered entries to database. Called by Dispatcher at batch end
        and by atexit on normal shutdown."""
        with self._lock:
            self._flush_buffer()

    def _flush_buffer(self) -> None:
        """Write all buffered entries to database. Caller holds _lock."""
        if not self._buffer:
            return
        entries = self._buffer[:]
        self._buffer.clear()
        try:
            from src.data.database import add_log_entry  # late import — B2 cycle guard (AST-388)
            for e in entries:
                add_log_entry(**e)
        except Exception as ex:
            _db_handler_stderr(
                f"[astral-log] app_log flush failed, {len(entries)} entries lost: {ex!r}"
            )


_db_handler_attached = False
_db_handler_instance: Optional[_DatabaseLogHandler] = None


def flush_log_buffer() -> None:
    """Flush the database log buffer. Called by Dispatcher at batch end."""
    if _db_handler_instance:
        _db_handler_instance.flush()


def log_llm_batch_summary(
    logger: logging.Logger,
    provider: str,
    prompt_label: str,
    duration: float,
    *,
    response: Any = None,
    error: Optional[str] = None,
) -> None:
    """One INFO/ERROR per LLM call when log_batch_id is set (Execution History / app_log)."""
    if not log_batch_id.get():
        return
    if error:
        logger.error(
            "LLM %s task=%s %.1fs error=%s",
            provider,
            prompt_label,
            duration,
            error,
        )
        return
    stop = getattr(response, "stop_reason", "?") if response is not None else "?"
    usage = getattr(response, "usage", None) if response is not None else None
    in_tok = getattr(usage, "input_tokens", 0) if usage else 0
    out_tok = getattr(usage, "output_tokens", 0) if usage else 0
    logger.info(
        "LLM %s task=%s %.1fs stop=%s tokens in=%s out=%s",
        provider,
        prompt_label,
        duration,
        stop,
        in_tok,
        out_tok,
    )


class _PrefixedLogger:
    """Logger wrapper that adds '[ ~ ] ' prefix to all debug messages"""

    def __init__(self, base_logger: logging.Logger, debug_flag: bool = False):
        """Initialize with a base logger from logging.getLogger()"""
        self._logger = base_logger
        self._debug_flag = debug_flag

    def set_debug_flag(self, flag: bool):
        """Set the debug flag for .test() method.

        This allows enabling/disabling test logging on an existing logger instance.
        Useful when the debug flag is determined at runtime (e.g., from function parameters).
        """
        self._debug_flag = flag

    def isEnabledFor(self, level: int) -> bool:
        """Match stdlib logging.Logger API — used for cheap guards before expensive debug work."""
        return self._logger.isEnabledFor(level)

    def debug(self, message: str, *args, **kwargs):
        """Debug logging with '[ ~ ] ' prefix"""
        self._logger.debug(f"[ ~ ] {message}", *args, **kwargs)

    def test(self, message: str):
        """Test logging - uses info level but only when debug flag is set.

        This avoids conflicts with third-party libraries (like httpcore) that use
        .debug() method. Use this for instrumentation/logging that should only
        appear when debugging is enabled.
        """
        if self._debug_flag:
            self._logger.info(f"[ ~ ] {message}")

    def debug_index(
        self,
        *,
        func: str,
        index: int,
        total: int,
        identifier: str,
        outcome: str,
    ) -> None:
        """Emit per-index batch header at INFO when debug_flag is True."""
        if not self._debug_flag:
            return
        self._logger.info(
            format_debug_index_header(
                func=func,
                index=index,
                total=total,
                identifier=identifier,
                outcome=outcome,
            )
        )

    def debug_detail(self, message: str) -> None:
        """Emit working detail line with DEBUG_DETAIL_PREFIX when debug_flag is True."""
        if not self._debug_flag:
            return
        self._logger.info(f"{DEBUG_DETAIL_PREFIX}{message}")

    def debug_detail_block(self, text: str) -> None:
        """Emit truncated multiline detail via debug_detail."""
        if not self._debug_flag:
            return
        for line in truncate_debug_content(text):
            self.debug_detail(line)

    def info(self, message: str, *args, **kwargs):
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._logger.error(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        self._logger.exception(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self._logger.critical(message, *args, **kwargs)


def get_logger(name: Optional[str] = None, debug_flag: bool = False) -> _PrefixedLogger:
    """
    Get a logger instance for the given module name.

    Args:
        name: Module name (typically __name__). If None, returns root logger.
        debug_flag: If True, .test() method will log messages (default: False)

    Returns:
        Logger instance with debug prefix support

    Example:
        logger = get_logger(__name__, debug_flag=True)
        logger.debug("This will have [ ~ ] prefix")
        logger.test("This will only log if debug_flag is True")
        logger.info("This will not have prefix")
    """
    base_logger = logging.getLogger(name)

    # Configure logging if not already configured
    if not base_logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )

    # Attach database handler once to the root logger
    global _db_handler_attached, _db_handler_instance
    if not _db_handler_attached:
        _db_handler_instance = _DatabaseLogHandler()
        _db_handler_instance.setLevel(logging.INFO)
        _db_handler_instance.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(_db_handler_instance)
        atexit.register(flush_log_buffer)
        _db_handler_attached = True

    return _PrefixedLogger(base_logger, debug_flag=debug_flag)
