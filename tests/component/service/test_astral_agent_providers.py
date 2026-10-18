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


# ---------------------------------------------------------------------------
# cursor-microservice-tweaks step 2 — async provider client (no live provider)
# ---------------------------------------------------------------------------

import asyncio

import httpx
from anthropic import RateLimitError


@pytest.fixture(autouse=True)
def _reset_provider_state(astral_agent_modules):
    """asyncio.Semaphore binds to the first loop that contends on it; each test has its own loop."""
    from providers import llm_compat_provider, openrouter_provider

    llm_compat_provider._slots.clear()
    openrouter_provider._hosts.clear()
    yield
    llm_compat_provider._slots.clear()
    openrouter_provider._hosts.clear()


def _compat_req(**overrides: Any) -> dict:
    return _req(
        protocol="anthropic_compat",
        server_id="deepseek",
        base_url="https://compat.invalid/anthropic",
        auth="x-api-key",
        **overrides,
    )


def _ok_response(provider: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        content=[SimpleNamespace(text="ok", type="text")],
        stop_reason="end_turn",
        id="msg_ok",
        provider=provider,
        usage=SimpleNamespace(
            input_tokens=1,
            output_tokens=1,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
        ),
    )


class _FakeClient:
    """Stands in for AsyncAnthropic: async context manager + messages.create."""

    def __init__(self, create) -> None:
        self.messages = SimpleNamespace(create=create)
        self.closed = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc: object) -> None:
        self.closed += 1


def _install(monkeypatch: pytest.MonkeyPatch, which: str, client: _FakeClient):
    """Patch the named provider to use `client`; return (module, request)."""
    from providers import anthropic_provider, llm_compat_provider

    if which == "anthropic":
        monkeypatch.setattr(anthropic_provider, "AsyncAnthropic", lambda **_kw: client)
        return anthropic_provider, _req()
    monkeypatch.setattr(llm_compat_provider, "_client", lambda *_a, **_kw: client)
    return llm_compat_provider, _compat_req()


async def _until(predicate, *, seconds: float = 5.0) -> None:
    async def _poll() -> None:
        while not predicate():
            await asyncio.sleep(0.005)

    await asyncio.wait_for(_poll(), seconds)


@pytest.fixture
async def silent_server():
    """TCP server that accepts, reads the request, never answers; records connect + close."""
    connected, closed = asyncio.Event(), asyncio.Event()

    async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            # "connected" = the request bytes arrived, not the TCP accept: cancelling while
            # anyio's connect_tcp task group is still finishing gets the cancel swallowed.
            if await reader.read(65536):
                connected.set()
                while await reader.read(65536):
                    pass
        finally:
            closed.set()
            writer.close()

    server = await asyncio.start_server(_handle, "127.0.0.1", 0)
    url = f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}"
    yield SimpleNamespace(url=url, connected=connected, closed=closed)
    server.close()
    await server.wait_closed()


@pytest.mark.parametrize("which", ["compat", "anthropic"])
class TestStep2AsyncProviderClient:
    async def test_cancel_aborts_the_http_call(
        self, which: str, silent_server, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from providers import anthropic_provider, llm_compat_provider

        if which == "anthropic":
            monkeypatch.setenv("ANTHROPIC_BASE_URL", silent_server.url)
            send, request = anthropic_provider.send, _req()
        else:
            send = llm_compat_provider.send
            request = _compat_req()
            request["base_url"] = silent_server.url
        task = asyncio.create_task(send(request))
        await asyncio.wait_for(silent_server.connected.wait(), 5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, 5)  # a swallowed cancel fails here instead of hanging
        # The server sees the socket drop — nothing keeps the call (or its bill) alive.
        await asyncio.wait_for(silent_server.closed.wait(), 3)

    async def test_budget_expiry_aborts_the_call(
        self, which: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        state = {"cancelled": False}

        async def _hang(**_kw: Any) -> Any:
            try:
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                state["cancelled"] = True
                raise

        client = _FakeClient(_hang)
        mod, request = _install(monkeypatch, which, client)
        out = await mod.send({**request, "timeout_seconds": 1, "grace_seconds": 0})
        assert out["success"] is False
        assert out["failure_class"] == "provider_call_timeout"
        assert state["cancelled"] is True
        assert client.closed == 1

    async def test_client_closed_after_success_and_failure(
        self, which: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _ok(**_kw: Any) -> Any:
            return _ok_response()

        async def _boom(**_kw: Any) -> Any:
            raise RuntimeError("provider exploded")

        for create, expect_ok in ((_ok, True), (_boom, False)):
            client = _FakeClient(create)
            mod, request = _install(monkeypatch, which, client)
            out = await mod.send(request)
            assert out["success"] is expect_ok
            assert client.closed == 1

    async def test_no_hidden_concurrency_cap(
        self, which: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Well past the default thread pool (min(32, cpu+4)): all must be in flight together.
        total = 100
        gate = asyncio.Event()
        started = {"n": 0}

        async def _create(**_kw: Any) -> Any:
            started["n"] += 1
            await gate.wait()
            return _ok_response()

        mod, request = _install(monkeypatch, which, _FakeClient(_create))
        tasks = [asyncio.create_task(mod.send(dict(request))) for _ in range(total)]
        await _until(lambda: started["n"] == total)
        gate.set()
        results = await asyncio.gather(*tasks)
        assert all(r["success"] for r in results)


class TestStep2CompatBackoffAndSlots:
    @staticmethod
    def _rate_limit() -> RateLimitError:
        resp = httpx.Response(429, request=httpx.Request("POST", "https://compat.invalid/v1/messages"))
        return RateLimitError("rate limited", response=resp, body=None)

    @staticmethod
    def _concurrency(**overrides: Any) -> dict:
        return {
            "rate_limit_retries": 2,
            "backoff_base_seconds": 10,
            "backoff_max_seconds": None,
            "max_concurrent": None,
            **overrides,
        }

    async def test_429_retry_sleeps_are_awaited_with_same_backoff(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from providers import llm_compat_provider

        calls = {"n": 0}
        delays: list[float] = []
        real_sleep = asyncio.sleep

        async def _create(**_kw: Any) -> Any:
            calls["n"] += 1
            if calls["n"] < 3:
                raise self._rate_limit()
            return _ok_response()

        async def _fake_sleep(delay: float) -> None:
            delays.append(delay)
            await real_sleep(0)

        monkeypatch.setattr(llm_compat_provider.random, "uniform", lambda _a, _b: 1.0)
        monkeypatch.setattr(llm_compat_provider.asyncio, "sleep", _fake_sleep)
        mod, request = _install(monkeypatch, "compat", _FakeClient(_create))
        out = await mod.send({**request, "concurrency": self._concurrency()})
        assert out["success"] is True
        assert calls["n"] == 3
        assert delays == [10.0, 20.0]

    async def test_cancel_during_backoff_sends_no_further_call(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from providers import llm_compat_provider

        calls = {"n": 0}
        sleeping = asyncio.Event()
        real_sleep = asyncio.sleep

        async def _create(**_kw: Any) -> Any:
            calls["n"] += 1
            raise self._rate_limit()

        async def _fake_sleep(_delay: float) -> None:
            sleeping.set()
            await real_sleep(3600)

        monkeypatch.setattr(llm_compat_provider.asyncio, "sleep", _fake_sleep)
        mod, request = _install(monkeypatch, "compat", _FakeClient(_create))
        task = asyncio.create_task(mod.send({**request, "concurrency": self._concurrency()}))
        await asyncio.wait_for(sleeping.wait(), 5)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert calls["n"] == 1

    async def test_max_concurrent_still_limits_in_flight(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        gate = asyncio.Event()
        live = {"now": 0, "peak": 0}

        async def _create(**_kw: Any) -> Any:
            live["now"] += 1
            live["peak"] = max(live["peak"], live["now"])
            try:
                await gate.wait()
            finally:
                live["now"] -= 1
            return _ok_response()

        mod, request = _install(monkeypatch, "compat", _FakeClient(_create))
        request["server_id"] = "limited-server"
        request["concurrency"] = self._concurrency(max_concurrent=2)
        tasks = [asyncio.create_task(mod.send(dict(request))) for _ in range(5)]
        await _until(lambda: live["now"] == 2)
        await asyncio.sleep(0.05)  # let any over-admission show up
        assert live["peak"] == 2
        gate.set()
        results = await asyncio.gather(*tasks)
        assert all(r["success"] for r in results)
        assert live["peak"] == 2


class TestStep2ProbeAndPin:
    async def test_probe_then_pin_unchanged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        seen: list[dict] = []

        async def _create(**kw: Any) -> Any:
            seen.append(kw)
            return _ok_response(provider="Venice")

        mod, request = _install(monkeypatch, "compat", _FakeClient(_create))
        request.update(server_id="openrouter", routing="openrouter", probe=True, batch_id="b-pin")
        first = await mod.send(dict(request))
        second = await mod.send(dict(request))
        assert first["success"] and second["success"]
        # probe + real call for the first job; the second job reuses the pinned host.
        assert len(seen) == 3
        assert seen[0]["extra_body"]["provider"]["zdr"] is True
        assert seen[1]["extra_body"]["provider"]["only"] == ["Venice"]
        assert seen[2]["extra_body"]["provider"]["only"] == ["Venice"]

    async def test_cancelled_waiter_does_not_break_owner_or_other_waiters(
        self, astral_agent_modules
    ) -> None:
        from providers import openrouter_provider

        gate = asyncio.Event()

        async def _send(_kwargs: Any) -> Any:
            await gate.wait()
            return SimpleNamespace(provider="Venice")

        kwargs = {"model": "m", "max_tokens": 8}

        def _get() -> asyncio.Task:
            return asyncio.create_task(
                openrouter_provider.get_batch_host("b-waiters", dict(kwargs), _send)
            )

        owner = _get()
        await asyncio.sleep(0)
        cancelled_waiter, other_waiter = _get(), _get()
        for _ in range(3):
            await asyncio.sleep(0)
        cancelled_waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await cancelled_waiter
        gate.set()
        assert await owner == ("Venice", None)
        assert await other_waiter == ("Venice", None)
