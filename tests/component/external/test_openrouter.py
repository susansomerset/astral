"""OpenRouter host discovery (AST-1959): probe_host + the per-batch single-flight host map.

`send` / `record_probe` are plain fakes here — the llm_compat wiring (stubbed client, AC 1–6) lives in
tests/component/external/test_llm_compat.py::TestAst1959ProbeHostLock.
"""

from __future__ import annotations

import asyncio
import threading
from types import SimpleNamespace
from typing import Any

import pytest

from src.external import openrouter
from src.utils import config as cfg

# Branches (probe_host): provider present → host; provider None / "" / absent → raise after recording;
# send raises → propagates, nothing recorded.
# Branches (get_batch_host): owner probes; waiter awaits the owner's future (same loop and another
# thread's loop); later caller hits the map; probe exception / no provider → remembered (None, error);
# owner cancelled → waiters get the "probe cancelled" failure; key = batch id + args minus messages/system.

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
        # max_tokens, temperature, effort and the agent's provider object are the real call's, untouched.
        assert {k: v for k, v in probe.items() if k != "messages"} == {
            k: v for k, v in REAL.items() if k not in ("messages", "system")}
        # The real call's kwargs are not mutated by building the probe.
        assert REAL["system"] and REAL["messages"][0]["content"][0]["text"] == "entity 7"
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
            (_Send(provider=None), "Host probe failed: Probe response named no provider"),
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
