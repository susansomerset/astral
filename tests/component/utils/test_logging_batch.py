"""Batch-scoped LLM log lines for Execution History (UI generate / dispatch)."""

from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from src.utils import logging as logging_mod


class TestLogLlmBatchSummary:
    def test_emits_only_when_batch_id_set(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        logger = logging.getLogger("test.logging_batch")
        token = logging_mod.log_batch_id.set("user-craft_x-abc")
        try:
            logging_mod.log_llm_batch_summary(
                logger,
                "deepseek",
                "craft_company_search_terms",
                1.2,
                response=SimpleNamespace(
                    stop_reason="end_turn",
                    usage=SimpleNamespace(input_tokens=100, output_tokens=50),
                ),
            )
        finally:
            logging_mod.log_batch_id.reset(token)

        assert any("LLM deepseek" in r.message for r in caplog.records)

    def test_skips_when_no_batch_id(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        logger = logging.getLogger("test.logging_batch_skip")
        logging_mod.log_llm_batch_summary(
            logger,
            "deepseek",
            "craft_x",
            0.5,
            response=SimpleNamespace(
                stop_reason="end_turn",
                usage=SimpleNamespace(input_tokens=1, output_tokens=1),
            ),
        )
        assert not [r for r in caplog.records if "LLM deepseek" in r.message]

    def test_empty_error_string_uses_error_path_not_healthy_summary(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """AST-1190: error=\"\" must not fake a healthy stop=? / zero-token INFO line."""
        caplog.set_level(logging.INFO)
        logger = logging.getLogger("test.logging_batch_empty_error")
        token = logging_mod.log_batch_id.set("batch-empty-err")
        try:
            logging_mod.log_llm_batch_summary(
                logger,
                "deepseek",
                "anticipate_scan",
                0.1,
                response=SimpleNamespace(
                    stop_reason="?",
                    usage=SimpleNamespace(input_tokens=0, output_tokens=0),
                ),
                error="",
            )
        finally:
            logging_mod.log_batch_id.reset(token)

        err_msgs = [r.message for r in caplog.records if r.levelname == "ERROR"]
        info_msgs = [r.message for r in caplog.records if r.levelname == "INFO"]
        assert any("error=(empty error)" in m for m in err_msgs)
        assert not any("stop=?" in m and "tokens in=0" in m for m in info_msgs)

    def test_omitted_error_still_logs_healthy_summary(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """error=None (omitted) keeps the INFO response= path."""
        caplog.set_level(logging.INFO)
        logger = logging.getLogger("test.logging_batch_healthy")
        token = logging_mod.log_batch_id.set("batch-healthy")
        try:
            logging_mod.log_llm_batch_summary(
                logger,
                "deepseek",
                "anticipate_scan",
                1.0,
                response=SimpleNamespace(
                    stop_reason="end_turn",
                    usage=SimpleNamespace(input_tokens=10, output_tokens=5),
                ),
            )
        finally:
            logging_mod.log_batch_id.reset(token)

        assert any(
            "stop=end_turn" in r.message and "tokens in=10" in r.message
            for r in caplog.records
            if r.levelname == "INFO"
        )
