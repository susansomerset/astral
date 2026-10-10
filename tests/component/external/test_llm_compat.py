"""Shared Anthropic-Messages-compatible client (AST-1877 / AST-1851).

Outbound body is intercepted at the stubbed client's messages.create — no network.
"""

from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace
from typing import Any, Optional

import httpx
import pytest
from anthropic import RateLimitError

from src.external import llm_compat, openrouter
from src.utils import config as cfg
from src.utils.logging import log_batch_id


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


def _tier(model_id: str = "moonshotai/kimi-k2.6", **settings: Any) -> dict:
    # AST-1956: the call tier is resolve_agent_settings over the agent row's plain settings (no mode / size).
    return cfg.resolve_agent_settings(model_id, settings)["tier"]


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> _RecordingClient:
    c = _RecordingClient()
    monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
    return c


async def _send(**overrides: Any) -> dict:
    kwargs: dict[str, Any] = dict(
        server_id="openrouter",
        sku="moonshotai/kimi-k2.6",
        tier=_tier(provider_allow_fallbacks=True),
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
        # AST-1956: a row with no provider settings resolves provider None, so the server's extra survives.
        out = await _send(tier=_tier())
        assert out["success"] is True
        assert client.calls[0]["extra_body"]["provider"] == {"ast1877_test_extra": True}

    @pytest.mark.asyncio
    async def test_shipped_openrouter_body_carries_no_zdr(self, client: _RecordingClient) -> None:
        await _send()
        body = client.calls[0]["extra_body"]
        # AST-1956: `provider` is the agent's own object (fallbacks only here) — no zdr, no host `order` pin.
        assert body["provider"] == {"allow_fallbacks": True}
        assert "zdr" not in repr(client.calls[0]) and "order" not in body["provider"]


class TestAst1877OutboundBody:
    @pytest.mark.asyncio
    async def test_body_shape_with_temperature_and_system(self, client: _RecordingClient) -> None:
        system = [{"type": "text", "text": "sys"}]
        await _send(tier=_tier(temperature=0.2, provider_allow_fallbacks=True), temperature=0.2, system_blocks=system)
        call = client.calls[0]
        assert call["model"] == "moonshotai/kimi-k2.6"
        assert call["max_tokens"] == 100
        assert call["messages"] == [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]
        assert call["extra_body"] == {"provider": {"allow_fallbacks": True}}
        assert call["temperature"] == 0.2
        assert call["system"] == system

    @pytest.mark.asyncio
    async def test_server_extras_merge_after_effort_body(
        self, monkeypatch: pytest.MonkeyPatch, client: _RecordingClient
    ) -> None:
        monkeypatch.setitem(cfg.LLM_SERVER_CONFIG["kimi"], "request_extras", {"x_extra": 1})
        await _send(server_id="kimi", sku="kimi-k2.6", tier=_tier("kimi-k2.6", reasoning_effort="high"))
        assert client.calls[0]["extra_body"] == {"output_config": {"effort": "high"}, "x_extra": 1}

    @pytest.mark.asyncio
    async def test_agent_provider_wins_over_server_extra(
        self, monkeypatch: pytest.MonkeyPatch, client: _RecordingClient
    ) -> None:
        # Later wins on key collision: the agent's provider object beats a server extra of the same name.
        monkeypatch.setitem(cfg.LLM_SERVER_CONFIG["openrouter"], "request_extras", {"provider": {"server": 1}, "s_only": 2})
        await _send(tier=_tier(quantization="fp8", provider_allow_fallbacks=False))
        body = client.calls[0]["extra_body"]
        assert body["provider"] == {"quantizations": ["fp8"], "allow_fallbacks": False}
        assert body["s_only"] == 2


# AST-1956: the agent's settings go on the wire exactly as stored — nothing derived, nothing gated by model.
# Branches: temperature None vs set (0.0 included); effort empty / "none" / other; provider object
# present (OpenRouter) vs None (direct servers); a rejected setting returns the plain failure envelope.
class TestAst1956SettingsOnTheWire:
    @pytest.mark.asyncio
    async def test_ac1_provider_object_from_the_agent_row(self, client: _RecordingClient) -> None:
        await _send(sku="openai/gpt-oss-120b",
                    tier=_tier("openai/gpt-oss-120b", quantization="bf16", provider_allow_fallbacks=True))
        await _send(sku="openai/gpt-oss-120b",
                    tier=_tier("openai/gpt-oss-120b", quantization="bf16", provider_allow_fallbacks=True,
                               provider_only=["crusoe"], provider_sort="price"))
        # Whole body equality: no other key, no `order` pin.
        assert client.calls[0]["extra_body"] == {"provider": {"quantizations": ["bf16"], "allow_fallbacks": True}}
        assert client.calls[1]["extra_body"] == {"provider": {
            "quantizations": ["bf16"], "allow_fallbacks": True, "only": ["crusoe"], "sort": "price"}}

    @pytest.mark.asyncio
    async def test_ac2_empty_settings_send_nothing(self, client: _RecordingClient) -> None:
        tier = _tier("openai/gpt-oss-120b", provider_allow_fallbacks=True)
        await _send(sku="openai/gpt-oss-120b", tier=tier, temperature=tier["temperature"])
        call = client.calls[0]
        assert not {"temperature", "output_config", "thinking"} & set(call)
        assert call["extra_body"] == {"provider": {"allow_fallbacks": True}}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("settings", "expected"),
        [
            ({"temperature": 0.3}, {"temperature": 0.3}),
            # 0.0 is a value, not "empty".
            ({"temperature": 0.0}, {"temperature": 0.0}),
            ({"reasoning_effort": "high"}, {"extra_body": {"output_config": {"effort": "high"}}}),
            ({"reasoning_effort": "none"}, {"extra_body": {"thinking": {"type": "disabled"}}}),
            # No vocabulary: an effort no SDK literal knows still goes out verbatim.
            ({"reasoning_effort": "ultra"}, {"extra_body": {"output_config": {"effort": "ultra"}}}),
        ],
    )
    async def test_ac3_temperature_and_effort_exactly_as_set(
        self, client: _RecordingClient, settings: dict, expected: dict
    ) -> None:
        tier = _tier("z-ai/glm-4.6", **settings)
        await _send(sku="z-ai/glm-4.6", tier=tier, temperature=tier["temperature"])
        call = client.calls[0]
        for key, value in expected.items():
            assert call[key] == value
        if "temperature" not in expected:
            assert "temperature" not in call

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("server_id", "model_id"),
        # AST-1958 CAN_THINK snapshot: neither could think under the old config — "high" still goes out.
        [("openrouter", "microsoft/phi-4"), ("deepseek", "deepseek-v4-pro")],
    )
    async def test_ac3_no_gating_on_models_that_could_not_think(
        self, client: _RecordingClient, server_id: str, model_id: str
    ) -> None:
        await _send(server_id=server_id, sku=model_id, tier=_tier(model_id, reasoning_effort="high"))
        assert client.calls[0]["extra_body"] == {"output_config": {"effort": "high"}}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("server_id", "model_id"), [("kimi", "kimi-k2.6"), ("deepseek", "deepseek-v4-flash")])
    async def test_direct_servers_get_no_provider_object(
        self, client: _RecordingClient, server_id: str, model_id: str
    ) -> None:
        # Provider settings stored on a direct-server agent never reach the body (resolver builds it for OpenRouter only).
        tier = _tier(model_id, quantization="fp8", provider_allow_fallbacks=True, provider_only=["x"])
        await _send(server_id=server_id, sku=model_id, tier=tier)
        assert client.calls[0]["extra_body"] == {}

    @pytest.mark.asyncio
    async def test_ac4_rejected_setting_is_a_plain_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        msg = "Error code: 400 - Reasoning is mandatory for this endpoint and cannot be disabled"
        c = _RecordingClient(raise_on_create=RuntimeError(msg))
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        out = await _send(sku="openai/gpt-oss-120b", tier=_tier("openai/gpt-oss-120b", reasoning_effort="none"))
        assert c.calls[0]["extra_body"] == {"thinking": {"type": "disabled"}}
        assert out["success"] is False and msg in out["error"]
        assert "failure_class" not in out


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
        # AST-1959: `host` on every result; no router `provider` on the response → the server label.
        assert set(out) == {"success", "api_response", "parsed_response", "timesheet", "host"}
        assert out["host"] == "OpenRouter"
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
        # openrouter routing: tokens only at insert; dollars from platform reconcile.
        zero_calc = dict.fromkeys(
            ("calc_cost_cache_write", "calc_cost_cache_read", "calc_cost_no_cache_input", "calc_cost_output"),
            0.0,
        )
        assert {k: row[k] for k in zero_calc} == zero_calc

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
        assert out["host"] == "OpenRouter"


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


# AST-2009 log body (the SDK's APIStatusError prefix + router envelope).
_AST2009_429 = (
    "Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'Rate limit exceeded'}, "
    "'metadata': {'provider_name': 'DekaLLM', 'limit_source': 'upstream_provider_shared_pool'}}"
)


def _rate_limit_2009() -> RateLimitError:
    req = httpx.Request("POST", "https://example.invalid/v1/messages")
    return RateLimitError(_AST2009_429, response=httpx.Response(429, request=req), body=None)


# AST-2010 — retry-only block (no max_concurrent / backoff_max_seconds) doubles with jitter and
# no cap; OpenRouter (exhausted_stops_batch) tags an exhausted 429 provider_rate_limit; DeepSeek
# (retry block, no opt-in) and Kimi (no block) keep today's untagged result; balance wins a tie.
class TestAst2010OpenRouterRateLimit:
    FC = "provider_rate_limit"

    @pytest.fixture(autouse=True)
    def _no_sleep(self, monkeypatch: pytest.MonkeyPatch) -> list[float]:
        sleeps: list[float] = []
        monkeypatch.setattr(llm_compat.time, "sleep", sleeps.append)
        monkeypatch.setattr(llm_compat.random, "uniform", lambda _a, _b: 1.0)
        monkeypatch.setattr(llm_compat, "_slots", {})
        return sleeps

    def test_retry_only_block_doubles_with_no_cap_or_ceiling(self, _no_sleep: list[float]) -> None:
        # [bug-repro] pre-fix: _create demands max_concurrent → KeyError before the first call.
        c = _FlakyClient(fails=99)
        with pytest.raises(RateLimitError):
            llm_compat._create(c, {}, "srv", {"rate_limit_retries": 5, "backoff_base_seconds": 2.0})
        assert c.calls == 6
        # 32s on the last retry: no ceiling clipped the doubling
        assert _no_sleep == [2.0, 4.0, 8.0, 16.0, 32.0]
        # no max_concurrent → no process-wide slot
        assert llm_compat._slots == {}

    def test_retry_only_block_keeps_jitter(self, monkeypatch: pytest.MonkeyPatch, _no_sleep: list[float]) -> None:
        bounds: list[tuple] = []
        monkeypatch.setattr(llm_compat.random, "uniform", lambda a, b: bounds.append((a, b)) or 0.5)
        c = _FlakyClient(fails=2)
        assert llm_compat._create(c, {}, "srv", {"rate_limit_retries": 5, "backoff_base_seconds": 2.0}) == "resp"
        assert c.calls == 3
        assert _no_sleep == [1.0, 2.0] and bounds == [(0.5, 1.0)] * 2

    @pytest.mark.asyncio
    async def test_openrouter_exhausted_429_is_tagged(self, monkeypatch: pytest.MonkeyPatch, _no_sleep) -> None:
        # [bug-repro] pre-fix: one call (concurrency None), result untagged.
        c = _RecordingClient(raise_on_create=_rate_limit_2009())
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        out = await _send()
        assert len(c.calls) == 6 and len(_no_sleep) == 5
        assert out["success"] is False
        assert out["failure_class"] == self.FC
        assert out["host"] == "OpenRouter"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("server_id", "sku", "calls"),
        [("deepseek", "deepseek-v4-flash", 5), ("kimi", "kimi-k2.6", 1)],
    )
    async def test_exhausted_429_untagged_without_opt_in(
        self, monkeypatch: pytest.MonkeyPatch, server_id: str, sku: str, calls: int
    ) -> None:
        # DeepSeek keeps its 4 retries and today's untagged result; Kimi has no retry block at all.
        c = _RecordingClient(raise_on_create=_rate_limit_2009())
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        out = await _send(server_id=server_id, sku=sku, tier=_tier(sku))
        assert len(c.calls) == calls
        assert out["success"] is False
        assert "failure_class" not in out

    @pytest.mark.asyncio
    async def test_balance_wins_over_rate_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        req = httpx.Request("POST", "https://example.invalid/v1/messages")
        exc = RateLimitError("Error code: 429 - insufficient credit", response=httpx.Response(429, request=req), body=None)
        c = _RecordingClient(raise_on_create=exc)
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        out = await _send()
        assert out["failure_class"] == "provider_balance_refusal"


def _is_probe(call: dict[str, Any]) -> bool:
    return call["messages"] == [{"role": "user", "content": [{"type": "text", "text": cfg.LLM_PROBE_MESSAGE}]}]


class _HostClient(_RecordingClient):
    """Responses carry the router's `provider`; the probe alone can be made to raise."""

    def __init__(self, provider: Optional[str] = "DeepInfra", raise_on_probe: Optional[Exception] = None) -> None:
        super().__init__()
        self.provider = provider
        self.raise_on_probe = raise_on_probe

    def create(self, **kwargs: Any) -> _Msg:
        if self.raise_on_probe and _is_probe(kwargs):
            self.calls.append(kwargs)
            raise self.raise_on_probe
        msg = super().create(**kwargs)
        if self.provider is not None:
            msg.provider = self.provider
        return msg


# AST-1959 — AC 1–6 through send_to_llm_compat with the stubbed client.
# Branches: probe flag on + batch id → probe / lock; remembered probe failure → no request; flag off
# (kimi, deepseek) or no batch id → today's request; host = response provider, else server label.
class TestAst1959ProbeHostLock:
    BF16 = dict(quantization="bf16", provider_allow_fallbacks=True)

    @pytest.fixture(autouse=True)
    def _fresh_host_map(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(openrouter, "_hosts", {})

    @pytest.fixture
    def batch(self):
        token = log_batch_id.set("batch-1959")
        yield "batch-1959"
        log_batch_id.reset(token)

    @staticmethod
    def _install(monkeypatch: pytest.MonkeyPatch, c: _HostClient) -> _HostClient:
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        return c

    async def _one_then_three(self, **kw: Any) -> list[dict]:
        # AC wording: one awaited call, then three concurrent calls for the same model and settings.
        first = await _send(**kw)
        return [first, *await asyncio.gather(*(_send(**kw) for _ in range(3)))]

    @pytest.mark.asyncio
    async def test_ac1_one_probe_per_batch_key_before_first_real_call(self, monkeypatch, batch) -> None:
        c = self._install(monkeypatch, _HostClient())
        outs = await self._one_then_three(tier=_tier(**self.BF16))
        assert len(c.calls) == 5
        assert _is_probe(c.calls[0]) and not any(_is_probe(x) for x in c.calls[1:])
        assert all(o["success"] for o in outs)

    @pytest.mark.asyncio
    async def test_ac1_concurrent_first_callers_wait_on_one_probe(self, monkeypatch, batch) -> None:
        c = self._install(monkeypatch, _HostClient())
        await asyncio.gather(*(_send(tier=_tier(**self.BF16)) for _ in range(4)))
        assert len(c.calls) == 5
        assert _is_probe(c.calls[0]) and sum(map(_is_probe, c.calls)) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("settings", "probe_only"),
        [
            ({}, None),
            # The agent's own `only` rides on the probe; the real call's `only` is replaced by the host.
            ({"provider_only": ["crusoe"]}, ["crusoe"]),
        ],
    )
    async def test_ac2_probe_matches_real_call_and_carries_no_cache(
        self, monkeypatch, batch, settings: dict, probe_only: Optional[list]
    ) -> None:
        c = self._install(monkeypatch, _HostClient())
        tier = _tier(temperature=0.2, reasoning_effort="high", **self.BF16, **settings)
        system = [{"type": "text", "text": "sys", "cache_control": {"type": "ephemeral"}}]
        await _send(tier=tier, temperature=0.2, system_blocks=system)
        probe, real = c.calls
        assert "system" not in probe and "cache_control" not in repr(probe)
        assert real["system"] == system
        assert probe["extra_body"]["provider"].get("only") == probe_only
        # Everything but content / system / the host lock is identical (max_tokens, temperature, effort, provider).
        unlocked = {**real["extra_body"], "provider": {k: v for k, v in real["extra_body"]["provider"].items() if k != "only"}}
        if probe_only:
            unlocked["provider"]["only"] = probe_only
        unlocked["provider"]["zdr"] = True  # probe copy only (AST-1959)
        assert {k: v for k, v in probe.items() if k != "messages"} == {
            **{k: v for k, v in real.items() if k not in ("messages", "system")}, "extra_body": unlocked}

    @pytest.mark.asyncio
    async def test_ac3_warm_and_gather_locked_to_probe_host(self, monkeypatch, batch) -> None:
        c = self._install(monkeypatch, _HostClient(provider="DeepInfra"))
        tier = _tier(**self.BF16)
        await self._one_then_three(tier=tier)
        for call in c.calls[1:]:
            assert call["extra_body"]["provider"] == {"quantizations": ["bf16"], "allow_fallbacks": True, "only": ["DeepInfra"]}
        # The lock is a new dict: the agent's tier object is not mutated across the batch.
        assert tier["provider"] == {"quantizations": ["bf16"], "allow_fallbacks": True}

    @pytest.mark.asyncio
    async def test_ac4_failed_probe_fails_the_batch_with_no_fallback(self, monkeypatch, batch) -> None:
        # AST-2010: the probe rides _create's OpenRouter retry block — 1 + 5 retries, never a real call;
        # the exhausted 429 tags every caller in the batch (waiters share the cached probe error).
        monkeypatch.setattr(llm_compat.time, "sleep", lambda _s: None)
        monkeypatch.setattr(llm_compat, "_slots", {})
        # Real SDK str ("Error code: 429 - …"): the probe hands the classifier a string, not the exception.
        c = self._install(monkeypatch, _HostClient(raise_on_probe=_rate_limit_2009()))
        outs = await self._one_then_three(tier=_tier(**self.BF16))
        assert len(c.calls) == 6 and all(map(_is_probe, c.calls))
        assert [o["success"] for o in outs] == [False] * 4
        assert all(o["error"].startswith("Host probe failed:") and o["host"] == "OpenRouter" for o in outs)
        assert [o.get("failure_class") for o in outs] == ["provider_rate_limit"] * 4

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("server_id", "sku", "in_batch", "label"),
        [
            ("kimi", "kimi-k2.6", True, "Kimi"),
            ("deepseek", "deepseek-v4-flash", True, "DeepSeek"),
            ("openrouter", "moonshotai/kimi-k2.6", False, "OpenRouter"),
        ],
    )
    async def test_ac5_no_probe_outside_scope(self, monkeypatch, server_id, sku, in_batch, label) -> None:
        c = self._install(monkeypatch, _HostClient(provider=None))
        token = log_batch_id.set("batch-1959" if in_batch else "")
        try:
            outs = [await _send(server_id=server_id, sku=sku, tier=_tier(sku, **self.BF16)) for _ in range(2)]
        finally:
            log_batch_id.reset(token)
        assert len(c.calls) == 2 and not any(map(_is_probe, c.calls))
        assert not any("only" in (x["extra_body"].get("provider") or {}) for x in c.calls)
        # No router `provider` on the response → host is the server's own label.
        assert [o["host"] for o in outs] == [label, label]

    @pytest.mark.asyncio
    async def test_ac6_host_on_result_and_info_line(self, monkeypatch, batch, caplog) -> None:
        self._install(monkeypatch, _HostClient(provider="DeepInfra"))
        with caplog.at_level(logging.INFO):
            out = await _send(tier=_tier(**self.BF16), prompt_label="gather_x")
        assert out["host"] == "DeepInfra"
        lines = [r.message for r in caplog.records if r.levelname == "INFO" and "task=gather_x" in r.message]
        assert len(lines) == 1 and "host=DeepInfra" in lines[0]

    @pytest.mark.asyncio
    async def test_probe_cost_lands_on_the_timesheet(self, monkeypatch, batch) -> None:
        self._install(monkeypatch, _HostClient())
        recorded: list[dict] = []
        await _send(tier=_tier(**self.BF16), record_timesheet=lambda **kw: recorded.append(kw))
        # Probe row first, then the real call's row; both on this server and batch.
        assert len(recorded) == 2
        assert all(r["provider"] == "openrouter" and r["batch_id"] == "batch-1959" for r in recorded)
        assert recorded[0]["agent_performance"] == "success" and recorded[0]["failure_note"] is None

    @pytest.mark.asyncio
    async def test_probe_timesheet_failure_never_fails_the_probe(self, monkeypatch, batch) -> None:
        c = self._install(monkeypatch, _HostClient())

        def boom(**_kw: Any) -> None:
            raise RuntimeError("timesheet down")

        out = await _send(tier=_tier(**self.BF16), record_timesheet=boom)
        assert out["success"] is True and len(c.calls) == 2


_HOLLOW_ERR = {"message": "No endpoints found matching your data policy", "code": 404}


class _HollowProbeClient(_RecordingClient):
    """The probe gets AST-2016's hollow reply (no provider, no usage, an error body); real calls answer normally."""

    def create(self, **kwargs: Any) -> Any:
        if _is_probe(kwargs):
            self.calls.append(kwargs)
            return SimpleNamespace(id="gen-hollow", provider=None, usage=None, content=[], stop_reason=None,
                                   error=_HOLLOW_ERR)
        return super().create(**kwargs)


class _HollowRealClient(_RecordingClient):
    """Every call answers hollow: no usage, no content, no stop reason (AST-1190 shape on a non-probe server)."""

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(id="gen-hollow-real", usage=None, content=[], stop_reason=None)


# AST-2098 — a non-429 probe failure is tagged provider_probe_failure (the caller holds state); a missing
# usage reads as zero tokens with no ERROR traceback, on the probe row and on a hollow real call.
# Literals only (no AST-2098 imports) so these fail by assertion on the pre-fix tree.
class TestAst2098ProbeFailureTagged:
    FC = "provider_probe_failure"
    BF16 = TestAst1959ProbeHostLock.BF16

    @pytest.fixture(autouse=True)
    def _fresh_host_map(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(openrouter, "_hosts", {})
        monkeypatch.setattr(llm_compat.time, "sleep", lambda _s: None)
        monkeypatch.setattr(llm_compat, "_slots", {})

    @pytest.fixture
    def batch(self):
        token = log_batch_id.set("batch-2098")
        yield "batch-2098"
        log_batch_id.reset(token)

    @staticmethod
    def _errors(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
        return [r for r in caplog.records if r.name == "src.external.llm_compat" and r.levelno >= logging.ERROR]

    @pytest.mark.asyncio
    async def test_hollow_probe_tagged_held_no_traceback(self, monkeypatch, batch, caplog) -> None:
        c = _HollowProbeClient()
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        rows: list[dict] = []
        with caplog.at_level(logging.ERROR, logger="src.external.llm_compat"):
            out = await _send(tier=_tier(**self.BF16), record_timesheet=lambda **kw: rows.append(kw))
        # The probe alone went out; nothing is sent after a failed probe.
        assert len(c.calls) == 1 and _is_probe(c.calls[0])
        assert out["success"] is False
        assert out["failure_class"] == self.FC
        assert out["error"].startswith("Host probe failed: Probe response named no provider: ")
        assert "No endpoints found matching your data policy" in out["error"]
        assert out["host"] == "OpenRouter"
        assert len(rows) == 1
        r = rows[0]
        assert (r["cache_read_tokens"], r["total_no_cache_input_tokens"], r["total_output_tokens"],
                r["cache_write_tokens"]) == (0, 0, 0, 0)
        # AST-2016's AttributeError traceback on the probe row is gone.
        assert self._errors(caplog) == []

    @pytest.mark.asyncio
    async def test_non_429_probe_exception_tags_every_caller(self, monkeypatch, batch) -> None:
        c = _HostClient(raise_on_probe=RuntimeError("upstream 503"))
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        kw = {"tier": _tier(**self.BF16)}
        first = await _send(**kw)
        outs = [first, *await asyncio.gather(*(_send(**kw) for _ in range(3)))]
        # One probe; waiters and later callers share the cached failure, all tagged alike.
        assert len(c.calls) == 1
        assert [o["success"] for o in outs] == [False] * 4
        assert [o.get("failure_class") for o in outs] == [self.FC] * 4

    @pytest.mark.asyncio
    async def test_hollow_real_call_is_empty_response_without_traceback(self, monkeypatch, caplog) -> None:
        c = _HollowRealClient()
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        with caplog.at_level(logging.ERROR, logger="src.external.llm_compat"):
            out = await _send(server_id="kimi", sku="kimi-k2.6", tier=_tier("kimi-k2.6"))
        # AST-1190 routing unchanged; usage=None now reads as zero tokens instead of raising.
        assert len(c.calls) == 1
        assert out["success"] is False
        assert out["failure_class"] == "provider_empty_response"
        assert self._errors(caplog) == []


# AST-1966: every call gets a timesheet row. Branches (_timesheet_kwargs_for): token counts raise → zero tokens,
# logged once; direct routing + catalog price raises → zero calc_cost_*, logged once; openrouter routing skips catalog.
class TestAst1966UnpricedRowRecorded:
    _ZERO_CALC = dict.fromkeys(("calc_cost_cache_write", "calc_cost_cache_read", "calc_cost_no_cache_input", "calc_cost_output"), 0.0)

    @staticmethod
    def _errors(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
        return [r for r in caplog.records if r.name == "src.external.llm_compat" and r.levelno >= logging.ERROR]

    @pytest.mark.asyncio
    async def test_openrouter_routing_skips_catalog_pricing(
        self, monkeypatch: pytest.MonkeyPatch, client: _RecordingClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        def boom(*_a: Any, **_k: Any) -> dict:
            raise ValueError("catalog must not run")

        monkeypatch.setattr(llm_compat, "calculate_cost_components_from_counts", boom)
        recorded: list[dict] = []
        with caplog.at_level(logging.ERROR, logger="src.external.llm_compat"):
            out = await _send(record_timesheet=lambda **kw: recorded.append(kw))
        assert out["success"] is True
        assert {k: recorded[0][k] for k in self._ZERO_CALC} == self._ZERO_CALC
        assert self._errors(caplog) == []

    @pytest.mark.asyncio
    async def test_direct_routing_pricing_raises_row_recorded_with_zero_cost(
        self, monkeypatch: pytest.MonkeyPatch, client: _RecordingClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        def unpriced(*_a: Any, **_k: Any) -> dict:
            raise ValueError("Unknown SKU 'kimi-k2.6'")

        monkeypatch.setattr(llm_compat, "calculate_cost_components_from_counts", unpriced)
        recorded: list[dict] = []
        with caplog.at_level(logging.ERROR, logger="src.external.llm_compat"):
            out = await llm_compat.send_to_llm_compat(
                [{"type": "text", "text": "hi"}],
                server_id="kimi",
                sku="kimi-k2.6",
                tier=_tier("kimi-k2.6"),
                api_key="sk-candidate",
                max_tokens=100,
                response_format="text",
                record_timesheet=lambda **kw: recorded.append(kw),
            )
        assert out["success"] is True
        assert len(recorded) == 1
        row = recorded[0]
        assert {k: row[k] for k in self._ZERO_CALC} == self._ZERO_CALC
        assert (row["cache_read_tokens"], row["total_no_cache_input_tokens"], row["total_output_tokens"]) == (50, 100, 25)
        assert (row["model_code"], row["provider"]) == ("kimi-k2.6", "kimi")
        errors = self._errors(caplog)
        assert len(errors) == 1 and errors[0].exc_info and "timesheet catalog price" in errors[0].getMessage()

    @pytest.mark.asyncio
    async def test_probe_token_counts_raise_row_recorded_with_zero_tokens(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        # The token-count fallback is live on the probe row only: the main call path reads usage itself
        # before the helper (unchanged), so an unreadable usage there still fails the call. First read = probe.
        monkeypatch.setattr(openrouter, "_hosts", {})
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: _HostClient())
        real, reads = llm_compat.usage_to_token_counts, []

        def unreadable_once(usage: Any) -> dict:
            reads.append(usage)
            if len(reads) == 1:
                raise AttributeError("usage has no input_tokens")
            return real(usage)

        monkeypatch.setattr(llm_compat, "usage_to_token_counts", unreadable_once)
        recorded: list[dict] = []
        token = log_batch_id.set("batch-1966")
        try:
            with caplog.at_level(logging.ERROR, logger="src.external.llm_compat"):
                out = await _send(tier=_tier(quantization="bf16", provider_allow_fallbacks=True),
                                  record_timesheet=lambda **kw: recorded.append(kw))
        finally:
            log_batch_id.reset(token)
        assert out["success"] is True
        probe, call = recorded
        assert (probe["cache_read_tokens"], probe["total_no_cache_input_tokens"], probe["total_output_tokens"], probe["cache_write_tokens"]) == (0, 0, 0, 0)
        # Zero tokens priced on a real SKU = zero cost.
        assert {k: probe[k] for k in self._ZERO_CALC} == self._ZERO_CALC
        assert call["total_output_tokens"] == 25
        errors = self._errors(caplog)
        assert len(errors) == 1 and errors[0].exc_info and "timesheet token counts" in errors[0].getMessage()

    @pytest.mark.asyncio
    async def test_failure_path_unpriced_row_still_recorded(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Same helper feeds the failure rows: unparseable JSON + unpriced → one failure row, zero cost.
        c = _RecordingClient(text="not json at all")
        monkeypatch.setattr(llm_compat, "_get_client", lambda *_a, **_k: c)
        monkeypatch.setattr(llm_compat, "calculate_cost_components_from_counts", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("unpriced")))
        recorded: list[dict] = []
        out = await _send(response_format="json", record_timesheet=lambda **kw: recorded.append(kw))
        assert out["success"] is False
        assert [r["agent_performance"] for r in recorded] == ["failure"]
        assert {k: recorded[0][k] for k in self._ZERO_CALC} == self._ZERO_CALC
