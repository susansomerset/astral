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


class TestAst1190EmptyResponseHelpers:
    """AST-1190: normalize blank errors; hollow conjunction; empty-response predicate."""

    def test_normalize_keeps_non_empty(self) -> None:
        assert llm_ext_mod.normalize_provider_error("boom") == "boom"
        assert llm_ext_mod.normalize_provider_error(RuntimeError("timeout")) == "timeout"

    def test_normalize_blank_exception_uses_type_name(self) -> None:
        out = llm_ext_mod.normalize_provider_error(TimeoutError())
        assert out.strip()
        assert "TimeoutError" in out
        assert "empty error detail" in out

    def test_normalize_blank_string_uses_fallback_then_generic(self) -> None:
        assert (
            llm_ext_mod.normalize_provider_error("", fallback="provider_empty_response")
            == "provider_empty_response"
        )
        assert llm_ext_mod.normalize_provider_error(None) == (
            "provider call failed with empty error detail"
        )
        assert llm_ext_mod.normalize_provider_error("   ") == (
            "provider call failed with empty error detail"
        )

    def test_is_unusable_requires_all_three(self) -> None:
        hollow = SimpleNamespace(stop_reason="?", content=[])
        assert (
            llm_ext_mod.is_unusable_provider_response(
                hollow, input_tokens=0, output_tokens=0
            )
            is True
        )
        # Real stop + tokens → not hollow even with empty content
        healthy_stop = SimpleNamespace(stop_reason="end_turn", content=[])
        assert (
            llm_ext_mod.is_unusable_provider_response(
                healthy_stop, input_tokens=10, output_tokens=5
            )
            is False
        )
        # Missing stop but positive tokens → not hollow
        assert (
            llm_ext_mod.is_unusable_provider_response(
                hollow, input_tokens=10, output_tokens=0
            )
            is False
        )
        # Missing stop + zero tokens but usable text → not hollow
        with_text = SimpleNamespace(
            stop_reason="?", content=[SimpleNamespace(text="hello")]
        )
        assert (
            llm_ext_mod.is_unusable_provider_response(
                with_text, input_tokens=0, output_tokens=0
            )
            is False
        )

    def test_is_provider_empty_response_predicate(self) -> None:
        # Lazy import — module must collect on sibling product tips without PROVIDER_EMPTY_RESPONSE
        from src.utils.config import PROVIDER_EMPTY_RESPONSE

        fc = PROVIDER_EMPTY_RESPONSE["failure_class"]
        assert llm_ext_mod.is_provider_empty_response({"failure_class": fc}) is True
        assert llm_ext_mod.is_provider_empty_response({"failure_class": "other"}) is False
        assert llm_ext_mod.is_provider_empty_response({"success": False}) is False
        assert llm_ext_mod.is_provider_empty_response(None) is False
        assert llm_ext_mod.is_provider_empty_response("nope") is False  # type: ignore[arg-type]


class TestAst1189ProviderCallBudgetHelpers:
    """AST-1189: budget readers, timeout classify, never-empty error, wall release."""

    def test_budget_readers(self) -> None:
        from src.utils.config import PROVIDER_CALL_BUDGET

        assert llm_ext_mod.provider_call_http_timeout_seconds() == float(
            PROVIDER_CALL_BUDGET["timeout_seconds"]
        )
        assert llm_ext_mod.provider_call_wait_timeout_seconds() == float(
            PROVIDER_CALL_BUDGET["timeout_seconds"]
        ) + float(PROVIDER_CALL_BUDGET["grace_seconds"])
        assert llm_ext_mod.provider_call_max_retries() == int(
            PROVIDER_CALL_BUDGET["max_retries"]
        )
        msg = llm_ext_mod.provider_call_timeout_error_message()
        assert msg.strip()
        assert "600" in msg

    def test_classify_timeout_and_cause_chain(self) -> None:
        fc = "provider_call_timeout"
        assert llm_ext_mod.classify_provider_call_timeout(TimeoutError()) == fc
        assert llm_ext_mod.classify_provider_call_timeout(TimeoutError("budget")) == fc
        # Name match for httpx-style timeouts
        read_timeout = type("ReadTimeout", (Exception,), {})("read timed out")
        assert llm_ext_mod.classify_provider_call_timeout(read_timeout) == fc
        # Cause-chain: wrapper → ReadTimeout
        wrapper = RuntimeError("api connection")
        wrapper.__cause__ = read_timeout
        assert llm_ext_mod.classify_provider_call_timeout(wrapper) == fc
        # Ordinary errors are not timeouts (AST-897 balance path stays distinct)
        assert llm_ext_mod.classify_provider_call_timeout(RuntimeError("timeout")) is None
        assert llm_ext_mod.classify_provider_call_timeout(RuntimeError("boom")) is None

    def test_non_empty_provider_error(self) -> None:
        assert llm_ext_mod.non_empty_provider_error(RuntimeError("boom"), fallback="fb") == "boom"
        assert llm_ext_mod.non_empty_provider_error(TimeoutError(), fallback="fb") == "fb"

    @pytest.mark.asyncio
    async def test_await_budget_releases_caller_without_waiting_worker(self) -> None:
        import time

        started = time.monotonic()

        def _slow() -> str:
            time.sleep(2.0)
            return "late"

        with pytest.raises(TimeoutError, match="per-call time budget"):
            await llm_ext_mod.await_provider_call_with_budget(_slow, timeout_seconds=0.15)
        elapsed = time.monotonic() - started
        # Caller released near the deadline — not after the 2s worker finishes
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_await_budget_returns_when_worker_finishes(self) -> None:
        out = await llm_ext_mod.await_provider_call_with_budget(
            lambda: "ok", timeout_seconds=2.0
        )
        assert out == "ok"
