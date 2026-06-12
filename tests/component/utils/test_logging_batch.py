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
