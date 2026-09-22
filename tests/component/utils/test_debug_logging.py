"""Component tests for AST-554 debug logging helper + AST-979 DEBUG persistence."""

from __future__ import annotations

import logging

import pytest

from src.utils import logging as logging_mod
from src.utils.logging import (
    DEBUG_DETAIL_PREFIX,
    format_debug_index_header,
    get_logger,
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
