"""AST-2239 — service provider errors, executor dispatch, classify helpers (no live HTTP)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest


def _req(**overrides: Any) -> dict:
    base = {
        "protocol": "anthropic",
        "server_id": "anthropic",
        "model": "claude-haiku-4-5",
        "api_key": "sk-test",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 64,
    }
    base.update(overrides)
    return base


class TestAst2239ProviderErrors:
    def test_classify_balance_by_status_and_substring(
        self, astral_agent_modules
    ) -> None:
        from providers.errors import classify_provider_balance_refusal

        exc402 = SimpleNamespace(status_code=402)
        assert classify_provider_balance_refusal(exc402) == "provider_balance_refusal"
        assert (
            classify_provider_balance_refusal(Exception("Insufficient credit remaining"))
            == "provider_balance_refusal"
        )
        assert classify_provider_balance_refusal(Exception("other")) is None

    def test_classify_rate_limit_and_timeout(self, astral_agent_modules) -> None:
        from providers.errors import (
            classify_provider_call_timeout,
            classify_provider_rate_limit,
        )

        assert (
            classify_provider_rate_limit(SimpleNamespace(status_code=429))
            == "provider_rate_limit"
        )
        assert classify_provider_call_timeout(TimeoutError("x")) == "provider_call_timeout"
        assert classify_provider_call_timeout(ValueError("nope")) is None

    def test_soft_fail_and_success_result_shapes(self, astral_agent_modules) -> None:
        from providers.errors import soft_fail, success_result, tool_use_json

        soft = soft_fail(error="boom", failure_class="provider_empty_response")
        assert soft["success"] is False
        assert soft["failure_class"] == "provider_empty_response"
        assert soft["usage"]["input_tokens"] == 0

        text_resp = SimpleNamespace(
            content=[SimpleNamespace(text="hello", type="text")],
            stop_reason="end_turn",
            id="msg_1",
            usage=SimpleNamespace(
                input_tokens=2,
                output_tokens=3,
                cache_read_input_tokens=0,
                cache_creation_input_tokens=0,
            ),
        )
        ok = success_result(text_resp)
        assert ok["success"] is True
        assert ok["api_response"] == "hello"
        assert ok["usage"]["output_tokens"] == 3

        tool_resp = SimpleNamespace(
            content=[
                SimpleNamespace(type="tool_use", input={"grade": "A"}, name="g"),
            ],
            stop_reason="tool_use",
            id="msg_2",
            usage=SimpleNamespace(
                input_tokens=1,
                output_tokens=1,
                cache_read_input_tokens=0,
                cache_creation_input_tokens=0,
            ),
        )
        assert '"grade": "A"' in (tool_use_json(tool_resp) or "")
        assert success_result(tool_resp)["api_response"]


class TestAst2239ExecutorValidate:
    @pytest.mark.asyncio
    async def test_missing_required_keys(self, astral_agent_modules) -> None:
        import executor
        from providers.errors import ProviderJobError

        with pytest.raises(ProviderJobError) as ei:
            await executor.execute({"protocol": "anthropic"})
        assert ei.value.error_class == "bad_request"
        assert "missing" in ei.value.detail

    @pytest.mark.asyncio
    async def test_unknown_protocol(self, astral_agent_modules) -> None:
        import executor
        from providers.errors import ProviderJobError

        with pytest.raises(ProviderJobError) as ei:
            await executor.execute(_req(protocol="openai"))
        assert ei.value.error_class == "bad_request"
        assert "unknown protocol" in ei.value.detail

    @pytest.mark.asyncio
    async def test_compat_requires_base_url_and_auth(
        self, astral_agent_modules
    ) -> None:
        import executor
        from providers.errors import ProviderJobError

        with pytest.raises(ProviderJobError) as ei:
            await executor.execute(_req(protocol="anthropic_compat"))
        assert "base_url" in ei.value.detail

        with pytest.raises(ProviderJobError) as ei2:
            await executor.execute(
                _req(protocol="anthropic_compat", base_url="https://x", auth="basic")
            )
        assert "auth" in ei2.value.detail

    @pytest.mark.asyncio
    async def test_dispatches_compat_provider(
        self, astral_agent_modules, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import executor
        from providers import llm_compat_provider

        monkeypatch.setattr(
            llm_compat_provider,
            "send",
            AsyncMock(return_value={"success": True, "api_response": "compat"}),
        )
        out = await executor.execute(
            _req(
                protocol="anthropic_compat",
                server_id="openrouter",
                base_url="https://openrouter.ai/api/v1",
                auth="bearer",
            )
        )
        assert out["api_response"] == "compat"
        llm_compat_provider.send.assert_awaited_once()
