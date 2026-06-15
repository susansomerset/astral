"""AST-687 shared LLM external helpers — attribution and response text extraction."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.utils import llm_external as llm_ext_mod


class TestExtractApiResponseText:
    def test_last_text_block_wins(self) -> None:
        api_response = SimpleNamespace(
            content=[
                SimpleNamespace(text="first"),
                SimpleNamespace(text="last"),
            ]
        )
        assert llm_ext_mod.extract_api_response_text(api_response) == "last"

    def test_skips_blocks_without_text(self) -> None:
        api_response = SimpleNamespace(
            content=[
                SimpleNamespace(thinking="internal chain"),
                SimpleNamespace(text="answer"),
            ]
        )
        assert llm_ext_mod.extract_api_response_text(api_response) == "answer"

    def test_raises_when_no_text_blocks(self) -> None:
        api_response = SimpleNamespace(content=[SimpleNamespace(thinking="only")])
        with pytest.raises(ValueError, match="missing text"):
            llm_ext_mod.extract_api_response_text(api_response)


class TestEmitLlmCallDebug:
    def test_uses_logger_name_parameter(self) -> None:
        with patch.object(llm_ext_mod, "get_logger", return_value=MagicMock()) as mock_get:
            llm_ext_mod.emit_llm_call_debug(
                logger_name="src.external.deepseek",
                func_name="send_to_deepseek",
                prompt_label="t",
                model="deepseek-v4-flash",
                duration=1.0,
                stop_reason="end_turn",
                input_total=1,
                input_cached=0,
                cache_creation_tokens=0,
                output_total=1,
            )
            mock_get.assert_called_once_with("src.external.deepseek", debug_flag=True)
