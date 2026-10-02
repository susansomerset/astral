"""Shared Anthropic-Messages-compatible client (AST-1877 / AST-1851).

Outbound body is intercepted at the stubbed client's messages.create — no network.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional

import httpx
import pytest
from anthropic import RateLimitError

from src.external import llm_compat
from src.utils import config as cfg
from src.utils.cost_calculator import calculate_cost_components_from_counts


class _Msg:
    def __init__(self, text: str, stop_reason: str = "end_turn") -> None:
        self.content = [SimpleNamespace(text=text)]
        self.stop_reason = stop_reason
        self.id = "msg_compat_test"
        self.usage = SimpleNamespace(input_tokens=100, output_tokens=25, cache_read_input_tokens=50,
                                     cache_creation_input_tokens=5)


class _RecordingClient:
    """messages.create records every outbound kwargs dict (the intercepted request body)."""

    def __init__(self, text: str = "ok", stop_reason: str = "end_turn", raise_on_create: Optional[Exception] = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self._text = text
        self._stop = stop_reason
        self._raise = raise_on_create
        self.messages = self

    def create(self, **kwargs: Any) -> _Msg:
        self.calls.append(kwargs)
        if self._raise:
            raise self._raise
        return _Msg(self._text, self._stop)


def _tier(model_id: str, size: str) -> dict:
    return cfg.LLM_MODEL_CONFIG[model_id]["brain_sizes"][size]


# AST-1938: every shipped openrouter tier carries its upstream pin; Kimi's is SiliconFlow, fallbacks off.
KIMI_OR_PIN = {"provider": {"order": ["siliconflow"], "allow_fallbacks": False}}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> _RecordingClient:
    c = _RecordingClient()
    monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
    return c


async def _send(**overrides: Any) -> dict:
    kwargs: dict[str, Any] = dict(
        server_id="openrouter",
        sku="moonshotai/kimi-k2.6",
        tier=_tier("kimi-k2.6-openrouter", cfg.BRAIN_LITTLE),
        api_key="sk-candidate",
        max_tokens=100,
        response_format="text",
    )
    kwargs.update(overrides)
    return await llm_compat.send_to_llm_compat([{"type": "text", "text": "hi"}], **kwargs)


class TestAst1877RequestExtras:
    """AC 9: server request_extras reach the outbound body; shipped OpenRouter sends no provider.zdr."""

    @pytest.mark.asyncio
    async def test_configured_request_extra_appears_in_outbound_body(
        self, monkeypatch: pytest.MonkeyPatch, client: _RecordingClient
    ) -> None:
        extra = {"provider": {"ast1877_test_extra": True}}
        monkeypatch.setitem(cfg.LLM_SERVER_CONFIG["openrouter"], "request_extras", extra)
        # AST-1938: shipped openrouter tiers carry a pin that would win on `provider`; strip it to see the server's.
        unpinned = {k: v for k, v in _tier("kimi-k2.6-openrouter", cfg.BRAIN_LITTLE).items() if k != "request_extras"}
        out = await _send(tier=unpinned)
        assert out["success"] is True
        assert client.calls[0]["extra_body"]["provider"] == {"ast1877_test_extra": True}

    @pytest.mark.asyncio
    async def test_shipped_openrouter_body_carries_no_zdr(self, client: _RecordingClient) -> None:
        await _send()
        body = client.calls[0]["extra_body"]
        # AST-1938: `provider` is now the SiliconFlow pin — still no zdr anywhere in the request.
        assert body["provider"] == KIMI_OR_PIN["provider"]
        assert "zdr" not in repr(client.calls[0])


class TestAst1877OutboundBody:
    @pytest.mark.asyncio
    async def test_thinking_off_sends_server_off_params_and_temperature(self, client: _RecordingClient) -> None:
        system = [{"type": "text", "text": "sys"}]
        await _send(temperature=0.6, system_blocks=system)
        call = client.calls[0]
        assert call["model"] == "moonshotai/kimi-k2.6"
        assert call["max_tokens"] == 100
        assert call["messages"] == [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]
        assert call["extra_body"] == {**cfg.LLM_SERVER_CONFIG["openrouter"]["thinking_off_params"], **KIMI_OR_PIN}
        assert call["temperature"] == 0.6
        assert call["system"] == system

    @pytest.mark.asyncio
    async def test_thinking_on_sends_tier_params_and_omits_temperature(self, client: _RecordingClient) -> None:
        await _send(tier=_tier("kimi-k2.6-openrouter", cfg.BRAIN_BIG), temperature=1.0)
        call = client.calls[0]
        assert call["extra_body"] == {"thinking": {"type": "adaptive"}, **KIMI_OR_PIN}
        assert "temperature" not in call
        assert "system" not in call

    @pytest.mark.asyncio
    async def test_extras_merge_after_thinking_body(self, monkeypatch: pytest.MonkeyPatch, client: _RecordingClient) -> None:
        monkeypatch.setitem(cfg.LLM_SERVER_CONFIG["kimi"], "request_extras", {"x_extra": 1})
        await _send(server_id="kimi", sku="kimi-k2.6", tier=_tier("kimi-k2.6", cfg.BRAIN_BIG))
        assert client.calls[0]["extra_body"] == {"thinking": {"type": "enabled"}, "x_extra": 1}


class TestAst1938ProviderPin:
    """AST-1938 AC 5: tier request_extras (OpenRouter upstream pin) land in extra_body after server extras.

    Branches: tier pin present (shortlist model, hand-written Kimi-OpenRouter); tier without request_extras
    (direct Kimi / DeepSeek → no `provider`); tier beats server on key collision; quantization filter row.
    """

    @staticmethod
    async def _send_model(model_id: str, size: str) -> None:
        m = cfg.LLM_MODEL_CONFIG[model_id]
        await _send(server_id=m["server"], sku=m["brain_sizes"][size]["sku"], tier=_tier(model_id, size))

    @pytest.mark.asyncio
    async def test_shortlist_little_pins_brief_provider_fallbacks_off(self, client: _RecordingClient) -> None:
        await self._send_model("qwen/qwen3-32b", cfg.BRAIN_LITTLE)
        call = client.calls[0]
        assert call["model"] == "qwen/qwen3-32b"
        assert call["extra_body"] == {
            **cfg.LLM_SERVER_CONFIG["openrouter"]["thinking_off_params"],
            "provider": {"order": ["deepinfra"], "allow_fallbacks": False},
        }

    @pytest.mark.asyncio
    async def test_shortlist_medium_keeps_thinking_and_pin(self, client: _RecordingClient) -> None:
        await self._send_model("qwen/qwen3-32b", cfg.BRAIN_MEDIUM)
        assert client.calls[0]["extra_body"] == {
            "thinking": {"type": "adaptive"},
            "provider": {"order": ["deepinfra"], "allow_fallbacks": False},
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("size", [cfg.BRAIN_LITTLE, cfg.BRAIN_BIG])
    async def test_kimi_openrouter_names_only_siliconflow(self, client: _RecordingClient, size: str) -> None:
        await self._send_model("kimi-k2.6-openrouter", size)
        assert client.calls[0]["extra_body"]["provider"] == KIMI_OR_PIN["provider"]

    @pytest.mark.asyncio
    async def test_quantization_filter_rides_with_pin(self, client: _RecordingClient) -> None:
        # Plan decision: DeepInfra hosts gemma-4-31b at two prices; fp8 is the brief's.
        await self._send_model("google/gemma-4-31b-it", cfg.BRAIN_LITTLE)
        assert client.calls[0]["extra_body"]["provider"] == {
            "order": ["deepinfra"], "allow_fallbacks": False, "quantizations": ["fp8"],
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("model_id", ["kimi-k2.6", "deepseek-v4"])
    @pytest.mark.parametrize("size", [cfg.BRAIN_LITTLE, cfg.BRAIN_BIG])
    async def test_direct_compat_servers_carry_no_provider(
        self, client: _RecordingClient, model_id: str, size: str
    ) -> None:
        await self._send_model(model_id, size)
        assert "provider" not in client.calls[0]["extra_body"]

    def test_non_openrouter_catalog_tiers_carry_no_pin(self) -> None:
        # Claude rides send_to_anthropic, which never receives a tier — the catalog is the only leak path.
        leaks = [
            (mid, bs) for mid, m in cfg.LLM_MODEL_CONFIG.items() if m["server"] != "openrouter"
            for bs, t in m["brain_sizes"].items() if "provider" in t.get("request_extras", {})
        ]
        assert leaks == []

    @pytest.mark.asyncio
    async def test_tier_extras_win_over_server_extras(self, monkeypatch: pytest.MonkeyPatch, client: _RecordingClient) -> None:
        monkeypatch.setitem(cfg.LLM_SERVER_CONFIG["openrouter"], "request_extras", {"provider": {"server": 1}, "s_only": 2})
        await self._send_model("qwen/qwen3-32b", cfg.BRAIN_LITTLE)
        body = client.calls[0]["extra_body"]
        assert body["provider"] == {"order": ["deepinfra"], "allow_fallbacks": False}
        assert body["s_only"] == 2


class TestAst1877Guards:
    """Bad server / sku / key raise before any client is built or request sent."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("overrides", "exc", "match"),
        [
            ({"server_id": "anthropic"}, ValueError, "not anthropic_compat"),
            ({"server_id": "__nope__"}, ValueError, "Unknown LLM server"),
            ({"sku": ""}, ValueError, "sku is required"),
            ({"api_key": ""}, ValueError, "No API key for server 'openrouter'"),
        ],
    )
    async def test_guard_raises_without_request(
        self, client: _RecordingClient, overrides: dict, exc: type, match: str
    ) -> None:
        with pytest.raises(exc, match=match):
            await _send(**overrides)
        assert client.calls == []


class TestAst1877GetClient:
    @pytest.mark.parametrize(
        ("server_id", "cred_key"),
        [("openrouter", "auth_token"), ("kimi", "auth_token"), ("deepseek", "api_key")],
    )
    def test_auth_style_selects_single_credential(
        self, monkeypatch: pytest.MonkeyPatch, server_id: str, cred_key: str
    ) -> None:
        seen: dict[str, Any] = {}
        monkeypatch.setattr(llm_compat, "Anthropic", lambda **kw: seen.update(kw) or "client")
        server = cfg.LLM_SERVER_CONFIG[server_id]
        assert llm_compat._get_client(server, "sk-candidate") == "client"
        assert seen["base_url"] == server["base_url"]
        assert seen[cred_key] == "sk-candidate"
        assert ({"api_key", "auth_token"} - {cred_key}).isdisjoint(seen)


class TestAst1877ResultContract:
    @pytest.mark.asyncio
    async def test_success_shape_and_timesheet_kwargs(self, client: _RecordingClient) -> None:
        recorded: list[dict] = []
        out = await _send(record_timesheet=lambda **kw: recorded.append(kw), candidate_id="c1", task_key_uuid="t1")
        assert set(out) == {"success", "api_response", "parsed_response", "timesheet"}
        assert out["success"] is True
        assert out["parsed_response"] == "ok"
        assert out["timesheet"]["inputtotal"] == 100
        assert out["timesheet"]["inputcached"] == 50
        assert out["timesheet"]["outputtotal"] == 25
        assert out["timesheet"]["cache_creation_tokens"] == 5
        row = recorded[0]
        assert row["provider"] == "openrouter"
        assert row["model_code"] == "moonshotai/kimi-k2.6"
        assert row["candidate_id"] == "c1" and row["task_key_uuid"] == "t1"
        assert row["agent_req_id"] == "msg_compat_test"
        assert row["agent_performance"] == "success"
        expected = calculate_cost_components_from_counts(50, 100, 25, 5, sku="moonshotai/kimi-k2.6", server_id="openrouter")
        for k, v in expected.items():
            assert row[k] == pytest.approx(v)

    @pytest.mark.asyncio
    async def test_json_parsed_and_agent_performance_propagates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        c = _RecordingClient(text='{"a": 1, "agent_performance": {"status": "failure", "failure_note": "n"}}')
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        recorded: list[dict] = []
        out = await _send(response_format="json", record_timesheet=lambda **kw: recorded.append(kw))
        assert out["parsed_response"]["a"] == 1
        assert recorded[0]["agent_performance"] == "failure"
        assert recorded[0]["failure_note"] == "n"

    @pytest.mark.asyncio
    async def test_json_truncated_at_max_tokens_fails_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        c = _RecordingClient(text='{"a": ', stop_reason="max_tokens")
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        out = await _send(response_format="json")
        assert out["success"] is False
        assert out["failure_class"] == "max_tokens"
        assert out["parsed_response"] is None

    @pytest.mark.asyncio
    async def test_hollow_response_tagged_provider_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        c = _RecordingClient(text="", stop_reason=None)
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        monkeypatch.setattr(llm_compat, "usage_to_token_counts",
                            lambda _u: {"cache_read": 0, "cache_miss": 0, "output": 0, "cache_write": 0})
        recorded: list[dict] = []
        out = await _send(record_timesheet=lambda **kw: recorded.append(kw))
        assert out["success"] is False
        assert out["failure_class"] == cfg.PROVIDER_EMPTY_RESPONSE["failure_class"]
        assert recorded[0]["agent_performance"] == "failure"

    @pytest.mark.asyncio
    async def test_unparseable_json_returns_failure_without_class(self, monkeypatch: pytest.MonkeyPatch) -> None:
        c = _RecordingClient(text="not json at all")
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        recorded: list[dict] = []
        out = await _send(response_format="json", record_timesheet=lambda **kw: recorded.append(kw))
        assert out["success"] is False
        assert out["parsed_response"] is None
        assert "failure_class" not in out
        assert recorded[0]["agent_performance"] == "failure"

    @pytest.mark.asyncio
    async def test_create_exception_returns_failure_dict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        c = _RecordingClient(raise_on_create=RuntimeError("boom"))
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        out = await _send()
        assert out["success"] is False
        assert out["api_response"] is None
        assert "boom" in out["error"]
        assert out["timesheet"]["inputtotal"] == 0


def _rate_limit() -> RateLimitError:
    req = httpx.Request("POST", "https://example.invalid/v1/messages")
    return RateLimitError("429", response=httpx.Response(429, request=req), body=None)


class _FlakyClient:
    def __init__(self, fails: int) -> None:
        self.fails = fails
        self.calls = 0
        self.messages = self

    def create(self, **_kw: Any) -> str:
        self.calls += 1
        if self.calls <= self.fails:
            raise _rate_limit()
        return "resp"


class TestAst1877ServerConcurrency:
    """_create: no cap when concurrency is None; per-server slot + 429 backoff otherwise."""

    CONC = {"max_concurrent": 2, "rate_limit_retries": 2, "backoff_base_seconds": 1.0, "backoff_max_seconds": 5.0}

    @pytest.fixture(autouse=True)
    def _no_sleep(self, monkeypatch: pytest.MonkeyPatch) -> list[float]:
        sleeps: list[float] = []
        monkeypatch.setattr(llm_compat.time, "sleep", sleeps.append)
        monkeypatch.setattr(llm_compat.random, "uniform", lambda _a, _b: 1.0)
        monkeypatch.setattr(llm_compat, "_slots", {})
        return sleeps

    def test_no_concurrency_calls_once(self) -> None:
        c = _FlakyClient(fails=0)
        assert llm_compat._create(c, {}, "srv", None) == "resp"
        assert c.calls == 1
        assert llm_compat._slots == {}

    def test_429_retries_with_backoff_then_succeeds(self, _no_sleep: list[float]) -> None:
        c = _FlakyClient(fails=2)
        assert llm_compat._create(c, {}, "srv", self.CONC) == "resp"
        assert c.calls == 3
        assert _no_sleep == [1.0, 2.0]
        assert "srv" in llm_compat._slots

    def test_429_exhausted_reraises(self) -> None:
        c = _FlakyClient(fails=5)
        with pytest.raises(RateLimitError):
            llm_compat._create(c, {}, "srv", self.CONC)
        assert c.calls == 3
