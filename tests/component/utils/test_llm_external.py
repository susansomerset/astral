"""AST-687 shared LLM external helpers — attribution and response text extraction."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.utils import llm_external as llm_ext_mod
from src.utils.config import PROVIDER_BALANCE_REFUSAL


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


class TestAst897ProviderBalanceRefusal:
    """AST-897: classify HTTP 402 / credit-exhausted messages; predicate on result dicts."""

    def test_classify_by_status_code_attr(self) -> None:
        exc = type("E", (Exception,), {"status_code": 402})("payment required")
        assert (
            llm_ext_mod.classify_provider_balance_refusal(exc)
            == PROVIDER_BALANCE_REFUSAL["failure_class"]
        )

    def test_classify_by_response_status_code(self) -> None:
        # Some SDK errors nest status on .response
        exc = type("E", (Exception,), {})("nope")
        exc.response = SimpleNamespace(status_code=402)
        assert (
            llm_ext_mod.classify_provider_balance_refusal(exc)
            == PROVIDER_BALANCE_REFUSAL["failure_class"]
        )

    def test_classify_by_message_substring(self) -> None:
        assert (
            llm_ext_mod.classify_provider_balance_refusal(RuntimeError("Insufficient Balance"))
            == PROVIDER_BALANCE_REFUSAL["failure_class"]
        )

    def test_classify_ignores_unrelated_errors(self) -> None:
        assert llm_ext_mod.classify_provider_balance_refusal(RuntimeError("timeout")) is None
        assert llm_ext_mod.classify_provider_balance_refusal(RuntimeError("429 rate limit")) is None

    def test_is_provider_balance_refusal_predicate(self) -> None:
        fc = PROVIDER_BALANCE_REFUSAL["failure_class"]
        assert llm_ext_mod.is_provider_balance_refusal({"failure_class": fc}) is True
        assert llm_ext_mod.is_provider_balance_refusal({"failure_class": "other"}) is False
        assert llm_ext_mod.is_provider_balance_refusal({"success": False}) is False
        assert llm_ext_mod.is_provider_balance_refusal(None) is False
        assert llm_ext_mod.is_provider_balance_refusal("nope") is False  # type: ignore[arg-type]
