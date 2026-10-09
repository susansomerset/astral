"""OpenRouter host discovery (AST-1959): probe_host + the per-batch single-flight host map.
Generation-stats lookup (AST-1964): get_generation_stats against a stubbed httpx.get.

`send` / `record_probe` are plain fakes here — the llm_compat wiring (stubbed client, AC 1–6) lives in
tests/component/external/test_llm_compat.py::TestAst1959ProbeHostLock.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from types import SimpleNamespace
from typing import Any

import httpx
import pytest

from src.external import openrouter
from src.utils import config as cfg
from src.utils.logging import log_debug

# Branches (probe_host): provider present → host; provider None / "" / absent → raise after recording;
# send raises → propagates, nothing recorded.
# Branches (get_batch_host): owner probes; waiter awaits the owner's future (same loop and another
# thread's loop); later caller hits the map; probe exception / no provider → remembered (None, error);
# owner cancelled → waiters get the "probe cancelled" failure; key = batch id + args minus messages/system.
# Branches (probe_host error text, AST-2098): response has an `error` attr → its text; no `error` attr →
# the whole response rendered; `None` response → "empty body".

REAL = {
    "model": "openai/gpt-oss-120b",
    "max_tokens": 100,
    "temperature": 0.2,
    "messages": [{"role": "user", "content": [{"type": "text", "text": "entity 7", "cache_control": {"type": "ephemeral"}}]}],
    "system": [{"type": "text", "text": "sys", "cache_control": {"type": "ephemeral"}}],
    "extra_body": {"output_config": {"effort": "high"}, "provider": {"quantizations": ["bf16"], "allow_fallbacks": True}},
}


@pytest.fixture(autouse=True)
def _fresh_host_map(monkeypatch: pytest.MonkeyPatch) -> None:
    # The map is process-global and never evicted; every test starts empty.
    monkeypatch.setattr(openrouter, "_hosts", {})


class _Send:
    """Fake send: records each kwargs dict; answers with `provider` or raises."""

    def __init__(self, provider: Any = "DeepInfra", raise_exc: Exception | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self.provider = provider
        self.raise_exc = raise_exc

    async def __call__(self, kwargs: dict[str, Any]) -> Any:
        self.calls.append(kwargs)
        await asyncio.sleep(0)  # yield so concurrent callers really overlap the probe
        if self.raise_exc:
            raise self.raise_exc
        return SimpleNamespace(provider=self.provider, id="probe_resp")


class TestAst1959ProbeHost:
    @pytest.mark.asyncio
    async def test_probe_swaps_content_drops_system_keeps_everything_else(self) -> None:
        send, recorded = _Send(), []
        assert await openrouter.probe_host(REAL, send, recorded.append) == "DeepInfra"
        probe = send.calls[0]
        assert probe["messages"] == [{"role": "user", "content": [{"type": "text", "text": cfg.LLM_PROBE_MESSAGE}]}]
        assert "system" not in probe and "cache_control" not in repr(probe)
        # max_tokens, temperature, effort and the agent's provider object are the real call's.
        # zdr is added on the probe copy only.
        expected = {k: v for k, v in REAL.items() if k not in ("messages", "system")}
        expected["extra_body"] = {**REAL["extra_body"], "provider": {**REAL["extra_body"]["provider"], "zdr": True}}
        assert {k: v for k, v in probe.items() if k != "messages"} == expected
        # The real call's kwargs are not mutated by building the probe.
        assert REAL["system"] and REAL["messages"][0]["content"][0]["text"] == "entity 7"
        assert "zdr" not in REAL["extra_body"]["provider"]
        assert [r.id for r in recorded] == ["probe_resp"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("provider", [None, ""])
    async def test_no_provider_raises_after_recording(self, provider: Any) -> None:
        send, recorded = _Send(provider=provider), []
        with pytest.raises(ValueError, match="named no provider"):
            await openrouter.probe_host(REAL, send, recorded.append)
        # The probe was paid for, so its cost still reaches the timesheet.
        assert len(recorded) == 1

    @pytest.mark.asyncio
    async def test_send_error_propagates_and_records_nothing(self) -> None:
        send, recorded = _Send(raise_exc=RuntimeError("429 rate limited")), []
        with pytest.raises(RuntimeError, match="429"):
            await openrouter.probe_host(REAL, send, recorded.append)
        assert recorded == []


class TestAst2098ProbeErrorText:
    """AST-2098: a hollow probe's ValueError names what the response carried, so the held-batch WARNING says why."""

    @pytest.mark.asyncio
    async def test_hollow_probe_names_provider_error_body(self) -> None:
        hollow = SimpleNamespace(id="gen-hollow", provider=None, usage=None,
                                 error={"message": "No endpoints found matching your data policy", "code": 404})
        recorded: list[Any] = []

        async def send(_kwargs: dict[str, Any]) -> Any:
            return hollow

        with pytest.raises(ValueError) as exc:
            await openrouter.probe_host(REAL, send, recorded.append)
        assert str(exc.value).startswith("Probe response named no provider: ")
        assert "No endpoints found matching your data policy" in str(exc.value)
        # Still recorded once: the hollow probe reaches the timesheet.
        assert recorded == [hollow]

    @pytest.mark.asyncio
    async def test_hollow_probe_with_no_body_says_empty_body(self) -> None:
        recorded: list[Any] = []

        async def send(_kwargs: dict[str, Any]) -> Any:
            return None

        with pytest.raises(ValueError) as exc:
            await openrouter.probe_host(REAL, send, recorded.append)
        assert str(exc.value) == "Probe response named no provider: empty body"
        assert recorded == [None]


class TestAst1959BatchHostMap:
    @pytest.mark.asyncio
    async def test_concurrent_first_callers_share_one_probe(self) -> None:
        send = _Send()
        outs = await asyncio.gather(*(openrouter.get_batch_host("b1", REAL, send, lambda _r: None) for _ in range(4)))
        assert len(send.calls) == 1
        assert outs == [("DeepInfra", None)] * 4

    @pytest.mark.asyncio
    async def test_later_caller_hits_the_map_without_sending(self) -> None:
        send = _Send()
        await openrouter.get_batch_host("b1", REAL, send, lambda _r: None)
        assert await openrouter.get_batch_host("b1", REAL, send, lambda _r: None) == ("DeepInfra", None)
        assert len(send.calls) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("send", "error"),
        [
            (_Send(raise_exc=RuntimeError("429 rate limited")), "Host probe failed: 429 rate limited"),
            # AST-2098: the no-provider error names what came back (here _Send's whole response, no `error` attr).
            (_Send(provider=None),
             "Host probe failed: Probe response named no provider: namespace(provider=None, id='probe_resp')"),
        ],
    )
    async def test_failed_probe_is_remembered_for_the_key(self, send: _Send, error: str) -> None:
        send.calls.clear()
        outs = await asyncio.gather(*(openrouter.get_batch_host("b1", REAL, send, lambda _r: None) for _ in range(4)))
        assert outs == [(None, error)] * 4
        # No second probe: a later call for the same key gets the remembered failure.
        assert await openrouter.get_batch_host("b1", REAL, send, lambda _r: None) == (None, error)
        assert len(send.calls) == 1

    @pytest.mark.asyncio
    async def test_key_ignores_content_and_system_not_settings_or_batch(self) -> None:
        send = _Send()
        other_entity = {**REAL, "messages": [{"role": "user", "content": "entity 8"}], "system": [{"type": "text", "text": "x"}]}
        no_system = {k: v for k, v in REAL.items() if k != "system"}
        for kwargs in (REAL, other_entity, no_system):
            await openrouter.get_batch_host("b1", kwargs, send, lambda _r: None)
        assert len(send.calls) == 1
        # Different settings or a different batch → a fresh probe each.
        await openrouter.get_batch_host("b1", {**REAL, "max_tokens": 200}, send, lambda _r: None)
        await openrouter.get_batch_host("b2", REAL, send, lambda _r: None)
        assert len(send.calls) == 3

    @pytest.mark.asyncio
    async def test_cancelled_owner_releases_waiters_with_failure(self) -> None:
        gate = asyncio.Event()

        async def hang(_kwargs: dict[str, Any]) -> Any:
            await gate.wait()  # never set: the owner is cancelled mid-probe

        owner = asyncio.create_task(openrouter.get_batch_host("b1", REAL, hang, lambda _r: None))
        await asyncio.sleep(0)
        waiter = asyncio.create_task(openrouter.get_batch_host("b1", REAL, hang, lambda _r: None))
        await asyncio.sleep(0)
        owner.cancel()
        with pytest.raises(asyncio.CancelledError):
            await owner
        assert await asyncio.wait_for(waiter, 1) == (None, "Host probe failed: probe cancelled")

    def test_waiter_on_another_thread_and_loop_gets_the_owners_host(self) -> None:
        # Callers may run on different event loops / worker threads (module comment) — the map must bridge them.
        release = threading.Event()
        calls: list[dict[str, Any]] = []

        async def slow_send(kwargs: dict[str, Any]) -> Any:
            calls.append(kwargs)
            await asyncio.to_thread(release.wait, 5)
            return SimpleNamespace(provider="DeepInfra")

        results: dict[str, Any] = {}

        def run(name: str) -> None:
            results[name] = asyncio.run(openrouter.get_batch_host("b1", REAL, slow_send, lambda _r: None))

        owner = threading.Thread(target=run, args=("owner",))
        owner.start()
        while not calls:  # owner has registered the future and is mid-probe
            threading.Event().wait(0.01)
        waiter = threading.Thread(target=run, args=("waiter",))
        waiter.start()
        threading.Event().wait(0.05)  # let the waiter block on the owner's future before the probe returns
        release.set()
        owner.join(5)
        waiter.join(5)
        assert results == {"owner": ("DeepInfra", None), "waiter": ("DeepInfra", None)}
        assert len(calls) == 1


# Branches (get_generation_stats, AST-1964): 200 + total_cost → success; non-200 → error; 200 with no data /
# null body / total_cost null → not-ready error; any exception (timeout, integration-mode guard) → error.
_KEY = "sk-or-secret-key"


class _Get:
    """Stub for httpx.get (the stubbed lookup): records each call; answers with (status, json body) or raises."""

    def __init__(self, status: int = 200, body: Any = None, raise_exc: Exception | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self.status, self.body, self.raise_exc = status, body, raise_exc

    def __call__(self, url: str, **kwargs: Any) -> Any:
        self.calls.append({"url": url, **kwargs})
        if self.raise_exc:
            raise self.raise_exc
        return SimpleNamespace(status_code=self.status, text=repr(self.body), json=lambda: self.body)


class TestAst1964GenerationStats:
    def _run(self, monkeypatch: pytest.MonkeyPatch, get: _Get) -> dict[str, Any]:
        monkeypatch.setattr(openrouter.httpx, "get", get)
        return openrouter.get_generation_stats("gen-123", _KEY)

    def test_200_returns_billed_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 2 — values verbatim from the stub; request = generation endpoint, id param, bearer key, provider timeout.
        get = _Get(body={"data": {"total_cost": 0.0123, "native_tokens_prompt": 1200, "native_tokens_completion": 300,
                                  "native_tokens_cached": 400, "native_tokens_reasoning": 50, "provider_name": "DeepInfra"}})
        out = self._run(monkeypatch, get)
        assert out == {"success": True, "total_cost": 0.0123, "native_tokens_prompt": 1200, "native_tokens_completion": 300,
                       "native_tokens_cached": 400, "native_tokens_reasoning": 50, "provider_name": "DeepInfra"}
        assert get.calls == [{
            "url": "https://openrouter.ai/api/v1/generation",
            "params": {"id": "gen-123"},
            "headers": {"Authorization": f"Bearer {_KEY}"},
            "timeout": openrouter.provider_call_http_timeout_seconds(),
        }]

    def test_200_with_only_cost_passes_missing_fields_as_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 2 stub body exactly; total_cost is the only required field, the rest pass through as sent.
        out = self._run(monkeypatch, _Get(body={"data": {"total_cost": 0.0123, "native_tokens_cached": 400, "provider_name": "DeepInfra"}}))
        assert (out["success"], out["total_cost"], out["native_tokens_cached"], out["provider_name"]) == (True, 0.0123, 400, "DeepInfra")
        assert (out["native_tokens_prompt"], out["native_tokens_completion"], out["native_tokens_reasoning"]) == (None, None, None)

    @pytest.mark.parametrize(
        ("get", "error"),
        [
            (_Get(status=404, body={"error": {"message": "Generation not found"}}), "Generation stats HTTP 404"),
            (_Get(status=500, body=None), "Generation stats HTTP 500"),
            (_Get(raise_exc=httpx.ReadTimeout("read timed out")), "Generation stats lookup failed: read timed out"),
            # Not ready yet: record exists but no cost, empty data, or a null body.
            (_Get(body={"data": {"total_cost": None, "provider_name": "DeepInfra"}}), "not ready"),
            (_Get(body={"data": None}), "not ready"),
            (_Get(body=None), "not ready"),
        ],
        ids=["404", "500", "timeout", "cost-null", "data-null", "body-null"],
    )
    def test_failure_returns_error_and_no_cost(self, monkeypatch: pytest.MonkeyPatch, get: _Get, error: str) -> None:
        # AC 2 — nothing raises, no cost key on any failure.
        out = self._run(monkeypatch, get)
        assert out["success"] is False and error in out["error"]
        assert set(out) == {"success", "error"}

    def test_integration_guard_becomes_error_without_http(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def blocked(caller: str) -> None:
            raise RuntimeError(f"{caller}: live external I/O blocked in integration mode")

        monkeypatch.setattr(openrouter, "require_controlled_external_io", blocked)
        get = _Get(body={"data": {"total_cost": 1.0}})
        out = self._run(monkeypatch, get)
        assert out == {"success": False, "error": "Generation stats lookup failed: openrouter.get_generation_stats: live external I/O blocked in integration mode"}
        assert get.calls == []

    @pytest.mark.parametrize("get", [_Get(body={"data": {"total_cost": 0.5}}), _Get(raise_exc=httpx.ReadTimeout("t"))], ids=["ok", "timeout"])
    def test_debug_request_and_response_never_the_key(self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, get: _Get) -> None:
        # stat.logging.debug — request and response logged at debug with the generation id; the key never appears.
        # The project logger's debug() emits only while the log_debug context var is on.
        token = log_debug.set(True)
        try:
            with caplog.at_level(logging.DEBUG, logger="src.external.openrouter"):
                self._run(monkeypatch, get)
        finally:
            log_debug.reset(token)
        lines = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
        # debug() prefixes each line with the caller's line number ("<lineno>: …").
        assert any("Calling GET generation: id=gen-123" in m for m in lines)
        assert any("Response from GET generation: id=gen-123" in m for m in lines)
        assert not any(_KEY in r.getMessage() for r in caplog.records)
