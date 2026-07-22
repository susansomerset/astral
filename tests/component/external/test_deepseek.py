"""DeepSeek response parsing — thinking blocks before answer text (AST-493 / craft UI)."""

from types import SimpleNamespace
from typing import Any, Callable, Optional
from unittest.mock import MagicMock, patch

import pytest

from src.external import deepseek as deepseek_mod
from src.utils.cost_calculator import calculate_cost_components_deepseek_from_counts


class FakeDeepseekMessage:
    def __init__(
        self,
        text: str,
        *,
        stop_reason: str = "end_turn",
        usage: Optional[Any] = None,
    ) -> None:
        self.content = [SimpleNamespace(text=text)]
        self.stop_reason = stop_reason
        self.id = "msg_ds_test"
        self.usage = usage or SimpleNamespace(
            input_tokens=100,
            output_tokens=25,
            cache_read_input_tokens=50,
        )


class FakeDeepseekClient:
    def __init__(
        self,
        *,
        response_text: str = "ok",
        raise_on_create: Optional[Exception] = None,
        stop_reason: str = "end_turn",
    ) -> None:
        self._response_text = response_text
        self._raise_on_create = raise_on_create
        self._stop_reason = stop_reason
        self.messages = self

    def create(self, **_kwargs: Any) -> FakeDeepseekMessage:
        if self._raise_on_create:
            raise self._raise_on_create
        return FakeDeepseekMessage(self._response_text, stop_reason=self._stop_reason)


@pytest.fixture
def fake_deepseek_client() -> Callable[..., FakeDeepseekClient]:
    def _factory(**kwargs: Any) -> FakeDeepseekClient:
        return FakeDeepseekClient(**kwargs)

    return _factory


class TestDeepseekParseApiResponse:
    @pytest.mark.asyncio
    async def test_extracts_text_after_thinking_block(self) -> None:
        response = {
            "success": True,
            "api_response": SimpleNamespace(
                content=[
                    SimpleNamespace(thinking="internal chain"),
                    SimpleNamespace(text='{"search_terms":"foo\\nbar"}'),
                ]
            ),
        }
        assert (
            await deepseek_mod._parse_api_response(response)
            == '{"search_terms":"foo\\nbar"}'
        )

    @pytest.mark.asyncio
    async def test_raises_when_no_text_blocks(self) -> None:
        with pytest.raises(ValueError, match="missing text attribute"):
            await deepseek_mod._parse_api_response(
                {
                    "success": True,
                    "api_response": SimpleNamespace(content=[SimpleNamespace()]),
                }
            )


class TestSendToDeepseekTimesheetMapping:
    @pytest.mark.asyncio
    async def test_record_timesheet_kwargs_match_deepseek_buckets(
        self, monkeypatch: pytest.MonkeyPatch, fake_deepseek_client: Callable[..., FakeDeepseekClient]
    ) -> None:
        client = fake_deepseek_client(response_text="plain")
        monkeypatch.setattr(deepseek_mod, "_get_client", lambda *_a, **_k: client)
        recorded: list[dict] = []

        def _record(**kwargs: Any) -> None:
            recorded.append(kwargs)

        out = await deepseek_mod.send_to_deepseek(
            [{"type": "text", "text": "hi"}],
            vendor_model="deepseek-v4-pro",
            tier_meta={"thinking": False},
            response_format="text",
            record_timesheet=_record,
        )
        assert out["success"] is True
        assert len(recorded) == 1
        row = recorded[0]
        assert row["cache_read_tokens"] == 50
        assert row["total_no_cache_input_tokens"] == 100
        assert row["total_output_tokens"] == 25
        assert row["cache_write_tokens"] == 0
        assert row["provider"] == "deepseek"
        expected = calculate_cost_components_deepseek_from_counts(50, 100, 25, 0, "deepseek-v4-pro")
        assert row["calc_cost_cache_read"] == pytest.approx(expected["calc_cost_cache_read"])
        assert row["calc_cost_no_cache_input"] == pytest.approx(
            expected["calc_cost_no_cache_input"]
        )
        assert row["calc_cost_output"] == pytest.approx(expected["calc_cost_output"])
        assert row["calc_cost_cache_write"] == 0.0

    @pytest.mark.asyncio
    async def test_debug_true_emits_under_deepseek_module(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_deepseek_client: Callable[..., FakeDeepseekClient],
    ) -> None:
        client = fake_deepseek_client(response_text="plain")
        monkeypatch.setattr(deepseek_mod, "_get_client", lambda *_a, **_k: client)
        get_logger_calls: list[tuple[str, dict[str, Any]]] = []

        def _track_get_logger(name: str, **kwargs: Any) -> MagicMock:
            get_logger_calls.append((name, kwargs))
            return MagicMock()

        with patch("src.utils.llm_external.get_logger", side_effect=_track_get_logger):
            await deepseek_mod.send_to_deepseek(
                [{"type": "text", "text": "hi"}],
                vendor_model="deepseek-v4-pro",
                tier_meta={"thinking": False},
                response_format="text",
                prompt_label="select_job_page",
                debug=True,
            )

        assert any(
            name == "src.external.deepseek" and kwargs.get("debug_flag") is True
            for name, kwargs in get_logger_calls
        )


class TestAst897BalanceRefusalTagging:
    """AST-897: deepseek API exceptions tag failure_class for balance/credit refusals."""

    @pytest.mark.asyncio
    async def test_status_402_tags_failure_class(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_deepseek_client: Callable[..., FakeDeepseekClient],
    ) -> None:
        from src.utils.config import PROVIDER_BALANCE_REFUSAL

        err = type("BalanceErr", (Exception,), {"status_code": 402})("payment required")
        client = fake_deepseek_client(raise_on_create=err)
        monkeypatch.setattr(deepseek_mod, "_get_client", lambda *_a, **_k: client)
        out = await deepseek_mod.send_to_deepseek(
            [{"type": "text", "text": "hi"}],
            vendor_model="deepseek-v4-flash",
            tier_meta={"thinking": False},
            response_format="text",
        )
        assert out["success"] is False
        assert out["failure_class"] == PROVIDER_BALANCE_REFUSAL["failure_class"]

    @pytest.mark.asyncio
    async def test_ordinary_api_failure_omits_failure_class(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_deepseek_client: Callable[..., FakeDeepseekClient],
    ) -> None:
        client = fake_deepseek_client(raise_on_create=RuntimeError("timeout"))
        monkeypatch.setattr(deepseek_mod, "_get_client", lambda *_a, **_k: client)
        out = await deepseek_mod.send_to_deepseek(
            [{"type": "text", "text": "hi"}],
            vendor_model="deepseek-v4-flash",
            tier_meta={"thinking": False},
            response_format="text",
        )
        assert out["success"] is False
        assert "failure_class" not in out


class TestAst903JsonMaxTokensHardFail:
    """AST-903: JSON + stop_reason=max_tokens fails closed (no heal/parse success)."""

    @pytest.mark.asyncio
    async def test_json_max_tokens_returns_failure_class(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_deepseek_client: Callable[..., FakeDeepseekClient],
    ) -> None:
        # Truncated mid-string body — must not be healed into success
        client = fake_deepseek_client(
            response_text='{"criteria":[{"content":"A == The JD',
            stop_reason="max_tokens",
        )
        monkeypatch.setattr(deepseek_mod, "_get_client", lambda *_a, **_k: client)
        recorded: list[dict] = []
        out = await deepseek_mod.send_to_deepseek(
            [{"type": "text", "text": "hi"}],
            vendor_model="deepseek-v4-pro",
            tier_meta={"thinking": False},
            response_format="json",
            record_timesheet=lambda **kwargs: recorded.append(kwargs),
        )
        assert out["success"] is False
        assert out["failure_class"] == "max_tokens"
        assert "max_tokens" in out["error"]
        assert out["parsed_response"] is None
        assert recorded and recorded[0]["agent_performance"] == "failure"

    @pytest.mark.asyncio
    async def test_text_max_tokens_still_succeeds(
        self,
        monkeypatch: pytest.MonkeyPatch,
        fake_deepseek_client: Callable[..., FakeDeepseekClient],
    ) -> None:
        client = fake_deepseek_client(response_text="plain truncated ok", stop_reason="max_tokens")
        monkeypatch.setattr(deepseek_mod, "_get_client", lambda *_a, **_k: client)
        out = await deepseek_mod.send_to_deepseek(
            [{"type": "text", "text": "hi"}],
            vendor_model="deepseek-v4-pro",
            tier_meta={"thinking": False},
            response_format="text",
        )
        assert out["success"] is True
        assert "failure_class" not in out
