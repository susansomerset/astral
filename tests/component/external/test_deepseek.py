"""DeepSeek response parsing — thinking blocks before answer text (AST-493 / craft UI)."""

from types import SimpleNamespace
from typing import Any, Callable, Optional

import pytest

from src.external import deepseek as deepseek_mod
from src.utils.cost_calculator import calculate_cost_components_deepseek_from_counts


class FakeDeepseekMessage:
    def __init__(self, text: str, *, usage: Optional[Any] = None) -> None:
        self.content = [SimpleNamespace(text=text)]
        self.stop_reason = "end_turn"
        self.id = "msg_ds_test"
        self.usage = usage or SimpleNamespace(
            input_tokens=100,
            output_tokens=25,
            cache_read_input_tokens=50,
        )


class FakeDeepseekClient:
    def __init__(self, *, response_text: str = "ok") -> None:
        self._response_text = response_text
        self.messages = self

    def create(self, **_kwargs: Any) -> FakeDeepseekMessage:
        return FakeDeepseekMessage(self._response_text)


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
