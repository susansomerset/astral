"""Component tests for AST-554 debug logging helper + AST-979 DEBUG persistence."""

from __future__ import annotations

import io
import json
import logging
import sys

import pytest

from src.utils import logging as logging_mod
from src.utils.logging import (
    DEBUG_DETAIL_PREFIX,
    format_debug_index_header,
    get_logger,
    log_debug,
    truncate_debug_content,
)


def _clear_db_buffer() -> list:
    """Drain the shared DB handler buffer; return a copy of drained entries."""
    handler = logging_mod._db_handler_instance
    if handler is None:
        return []
    with handler._lock:
        drained = list(handler._buffer)
        handler._buffer.clear()
        return drained


class TestTruncateDebugContent:
    def test_short_text_returns_all_lines(self) -> None:
        text = "\n".join(f"line{i}" for i in range(10))
        lines = truncate_debug_content(text)
        assert len(lines) == 10
        assert "<" not in " ".join(lines)

    def test_exactly_threshold_returns_all_lines(self) -> None:
        text = "\n".join(f"line{i}" for i in range(50))
        lines = truncate_debug_content(text)
        assert len(lines) == 50
        assert "<" not in " ".join(lines)

    def test_over_threshold_inserts_omitted_marker(self) -> None:
        text = "\n".join(f"line{i}" for i in range(51))
        lines = truncate_debug_content(text)
        assert len(lines) == 31
        assert lines[15] == "<21 lines omitted>"

    def test_empty_string_returns_empty_list(self) -> None:
        assert truncate_debug_content("") == []


class TestFormatDebugIndexHeader:
    def test_happy_path_shape(self) -> None:
        out = format_debug_index_header(
            func="roster.ingest",
            index=2,
            total=5,
            identifier="acme",
            outcome="passed",
        )
        assert out == "roster.ingest index 2/5 acme -> passed"

    def test_index_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            format_debug_index_header(
                func="x", index=0, total=5, identifier="a", outcome="b"
            )
        with pytest.raises(ValueError):
            format_debug_index_header(
                func="x", index=6, total=5, identifier="a", outcome="b"
            )


class TestPrefixedLoggerDebugGating:
    def test_debug_index_silent_when_flag_false(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.ast554.index_off", debug_flag=False)
        logger.debug_index(
            func="roster.ingest",
            index=1,
            total=1,
            identifier="acme",
            outcome="passed",
        )
        assert not any("index 1/1" in r.message for r in caplog.records)

    def test_debug_index_emits_when_flag_true(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        # AST-979: helpers emit at DEBUG (was INFO); caplog must listen at DEBUG.
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.ast554.index_on", debug_flag=True)
        logger.debug_index(
            func="roster.ingest",
            index=1,
            total=1,
            identifier="acme",
            outcome="passed",
        )
        matches = [r for r in caplog.records if "index 1/1" in r.message and " -> " in r.message]
        assert len(matches) == 1
        assert matches[0].levelname == "DEBUG"

    def test_debug_detail_silent_when_flag_false(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.ast554.detail_off", debug_flag=False)
        logger.debug_detail("hits=3")
        assert not any("hits=3" in r.message for r in caplog.records)

    def test_debug_detail_emits_with_prefix_when_true(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.ast554.detail_on", debug_flag=True)
        logger.debug_detail("hits=3")
        matches = [r for r in caplog.records if r.message.startswith(DEBUG_DETAIL_PREFIX)]
        assert matches
        assert all(r.levelname == "DEBUG" for r in matches)

    def test_debug_detail_block_respects_truncation(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        logger = get_logger("test.ast554.block_on", debug_flag=True)
        text = "\n".join(f"row{i}" for i in range(60))
        logger.debug_detail_block(text)
        detail_records = [r for r in caplog.records if r.message.startswith(DEBUG_DETAIL_PREFIX)]
        assert len(detail_records) == 31
        assert any("<30 lines omitted>" in r.message for r in detail_records)
        assert all(r.levelname == "DEBUG" for r in detail_records)


class TestAst979DebugLevelPersistence:
    """Persisted severity in the DB handler buffer (app_log level column)."""

    def test_debug_gated_helpers_buffer_debug_when_flag_true(self) -> None:
        get_logger("test.ast979.attach")  # ensure handler attached
        _clear_db_buffer()
        logger = get_logger("test.ast979.gated_on", debug_flag=True)
        logger.debug_index(
            func="roster.ingest",
            index=1,
            total=1,
            identifier="acme",
            outcome="passed",
        )
        logger.debug_detail("hits=3")
        logger.test("probe")
        entries = _clear_db_buffer()
        by_msg = {e["message"]: e["level"] for e in entries}
        assert by_msg.get("roster.ingest index 1/1 acme -> passed") == "DEBUG"
        assert by_msg.get(f"{DEBUG_DETAIL_PREFIX}hits=3") == "DEBUG"
        assert by_msg.get("[ ~ ] probe") == "DEBUG"

    def test_debug_gated_helpers_silent_when_flag_false(self) -> None:
        get_logger("test.ast979.attach2")
        _clear_db_buffer()
        logger = get_logger("test.ast979.gated_off", debug_flag=False)
        logger.debug_index(
            func="roster.ingest",
            index=1,
            total=1,
            identifier="acme",
            outcome="passed",
        )
        logger.debug_detail("hits=3")
        logger.test("probe")
        entries = _clear_db_buffer()
        assert entries == []

    def test_ordinary_info_stays_info_with_debug_flag_true(self) -> None:
        get_logger("test.ast979.attach3")
        _clear_db_buffer()
        logger = get_logger("test.ast979.info_on", debug_flag=True)
        logger.info("ordinary production line")
        entries = _clear_db_buffer()
        assert len(entries) == 1
        assert entries[0]["level"] == "INFO"
        assert entries[0]["message"] == "ordinary production line"

    def test_warning_and_error_levels_unchanged(self) -> None:
        get_logger("test.ast979.attach4")
        _clear_db_buffer()
        logger = get_logger("test.ast979.warn_err", debug_flag=True)
        logger.warning("warn line")
        logger.error("err line")
        entries = _clear_db_buffer()
        by_msg = {e["message"]: e["level"] for e in entries}
        assert by_msg.get("warn line") == "WARNING"
        assert by_msg.get("err line") == "ERROR"

    def test_set_debug_flag_false_restores_named_logger_level(self) -> None:
        logger = get_logger("test.ast979.level_restore", debug_flag=True)
        assert logger._logger.level == logging.DEBUG
        logger.set_debug_flag(False)
        assert logger._logger.level == logging.INFO

    def test_debug_emits_when_named_logger_is_notset_under_info_root(self) -> None:
        """stat.logging.debug: log_debug true must emit even if the named logger is NOTSET."""
        root = logging.getLogger()
        prior_root = root.level
        root.setLevel(logging.INFO)
        name = "test.ast979.notset_debug"
        named = logging.getLogger(name)
        prior_named = named.level
        named.setLevel(logging.NOTSET)
        token = log_debug.set(True)
        try:
            get_logger("test.ast979.notset_attach")
            _clear_db_buffer()
            logger = get_logger(name)
            logger.debug("Beginning consult loop on %s items", 2)
            entries = _clear_db_buffer()
            hit = [e for e in entries if "Beginning consult loop on 2 items" in e["message"]]
            assert len(hit) == 1
            assert hit[0]["level"] == "DEBUG"
            assert hit[0]["logger_name"] == name
            off = log_debug.set(False)
            try:
                _clear_db_buffer()
                logger.debug("Beginning consult loop on %s items", 2)
                assert _clear_db_buffer() == []
            finally:
                log_debug.reset(off)
        finally:
            log_debug.reset(token)
            named.setLevel(prior_named)
            root.setLevel(prior_root)


class TestConsoleFormat:
    """Stdout shows level + logger name; app_log message stays the product line."""

    def test_console_line_includes_level_and_logger_name(self) -> None:
        record = logging.LogRecord(
            "src.core.meteorite", logging.INFO, __file__, 0, "hello", (), None
        )
        assert logging_mod._CONSOLE_FORMATTER.format(record) == (
            "INFO src.core.meteorite: hello"
        )

    def test_db_handler_message_is_message_only(self) -> None:
        get_logger("test.console.db")
        handler = logging_mod._db_handler_instance
        assert handler is not None
        record = logging.LogRecord(
            "src.core.meteorite", logging.WARNING, __file__, 0, "hello", (), None
        )
        assert handler.format(record) == "hello"


class TestAst1778RailwayConsoleTransport:
    """Railway JSON level map + stdout console; DB handler path unchanged (AC1–5)."""

    def test_railway_json_formatter_maps_levels(self) -> None:
        fmt = logging_mod._RailwayJsonFormatter()
        cases = (
            (logging.DEBUG, "debug"),
            (logging.INFO, "info"),
            (logging.WARNING, "warn"),
            (logging.ERROR, "error"),
            (logging.CRITICAL, "error"),
        )
        for levelno, railway_level in cases:
            record = logging.LogRecord(
                "src.core.roster", levelno, __file__, 0, "progress line", (), None
            )
            payload = json.loads(fmt.format(record))
            assert payload["level"] == railway_level
            assert payload["message"] == "src.core.roster: progress line"
            assert "WARNING" not in payload["level"]
            assert "INFO" not in payload["level"]

    def test_ensure_repoints_stderr_handler_to_stdout(self) -> None:
        root = logging.getLogger()
        # Drop prior console StreamHandlers so this case owns the only one.
        for h in list(root.handlers):
            if isinstance(h, logging_mod._DatabaseLogHandler):
                continue
            if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in (
                sys.stdout,
                sys.stderr,
            ):
                root.removeHandler(h)
        stderr_handler = logging.StreamHandler(sys.stderr)
        root.addHandler(stderr_handler)
        try:
            logging_mod._ensure_stdout_console_handler()
            assert stderr_handler.stream is sys.stdout
        finally:
            root.removeHandler(stderr_handler)

    def test_apply_formatter_switches_on_railway_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        root.addHandler(handler)
        try:
            monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
            logging_mod._apply_console_formatter()
            assert handler.formatter is logging_mod._CONSOLE_FORMATTER

            monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
            logging_mod._apply_console_formatter()
            assert handler.formatter is logging_mod._RAILWAY_JSON_FORMATTER
        finally:
            root.removeHandler(handler)
            monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
            logging_mod._apply_console_formatter()

    def test_off_railway_emit_is_plain_stdout_shape(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        captured = io.StringIO()

        class _StdoutCapture(logging.StreamHandler):
            def __init__(self) -> None:
                logging.Handler.__init__(self)
                self.stream = sys.stdout

            def emit(self, record: logging.LogRecord) -> None:
                try:
                    captured.write(self.format(record) + self.terminator)
                except Exception:
                    self.handleError(record)

        for h in list(root.handlers):
            if isinstance(h, logging_mod._DatabaseLogHandler):
                continue
            if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in (
                sys.stdout,
                sys.stderr,
            ):
                root.removeHandler(h)
        capture_h = _StdoutCapture()
        root.addHandler(capture_h)
        try:
            logger = get_logger("test.ast1778.plain")
            logger.info("healthy progress")
            line = captured.getvalue().strip()
            assert line == "INFO test.ast1778.plain: healthy progress"
            assert not line.startswith("{")
        finally:
            root.removeHandler(capture_h)
            logging_mod._apply_console_formatter()

    def test_on_railway_emit_is_json_with_level(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAILWAY_ENVIRONMENT", "1")
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        captured = io.StringIO()

        class _StdoutCapture(logging.StreamHandler):
            def __init__(self) -> None:
                logging.Handler.__init__(self)
                self.stream = sys.stdout

            def emit(self, record: logging.LogRecord) -> None:
                try:
                    captured.write(self.format(record) + self.terminator)
                except Exception:
                    self.handleError(record)

        for h in list(root.handlers):
            if isinstance(h, logging_mod._DatabaseLogHandler):
                continue
            if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in (
                sys.stdout,
                sys.stderr,
            ):
                root.removeHandler(h)
        capture_h = _StdoutCapture()
        root.addHandler(capture_h)
        try:
            logger = get_logger("test.ast1778.railway")
            logger.warning("soft fail")
            payload = json.loads(captured.getvalue().strip())
            assert payload["level"] == "warn"
            assert payload["message"] == "test.ast1778.railway: soft fail"
        finally:
            root.removeHandler(capture_h)
            monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
            logging_mod._apply_console_formatter()

    def test_db_buffer_levels_unchanged_when_on_railway(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("RAILWAY_ENVIRONMENT", "1")
        logging.getLogger().setLevel(logging.INFO)
        try:
            get_logger("test.ast1778.db.attach")
            _clear_db_buffer()
            logger = get_logger("test.ast1778.db")
            logger.info("info row")
            logger.warning("warn row")
            logger.error("err row")
            entries = _clear_db_buffer()
            by_msg = {e["message"]: e["level"] for e in entries}
            assert by_msg.get("info row") == "INFO"
            assert by_msg.get("warn row") == "WARNING"
            assert by_msg.get("err row") == "ERROR"
        finally:
            monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
            logging_mod._apply_console_formatter()
