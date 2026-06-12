"""Component tests for AST-554 debug logging helper (gating + truncation math only)."""

from __future__ import annotations

import logging

import pytest

from src.utils.logging import (
    DEBUG_DETAIL_PREFIX,
    format_debug_index_header,
    get_logger,
    truncate_debug_content,
)


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
        caplog.set_level(logging.INFO)
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
        caplog.set_level(logging.INFO)
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

    def test_debug_detail_silent_when_flag_false(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        logger = get_logger("test.ast554.detail_off", debug_flag=False)
        logger.debug_detail("hits=3")
        assert not any("hits=3" in r.message for r in caplog.records)

    def test_debug_detail_emits_with_prefix_when_true(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        logger = get_logger("test.ast554.detail_on", debug_flag=True)
        logger.debug_detail("hits=3")
        assert any(r.message.startswith(DEBUG_DETAIL_PREFIX) for r in caplog.records)

    def test_debug_detail_block_respects_truncation(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        logger = get_logger("test.ast554.block_on", debug_flag=True)
        text = "\n".join(f"row{i}" for i in range(60))
        logger.debug_detail_block(text)
        detail_records = [r for r in caplog.records if r.message.startswith(DEBUG_DETAIL_PREFIX)]
        assert len(detail_records) == 31
        assert any("<30 lines omitted>" in r.message for r in detail_records)
