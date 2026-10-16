"""OpenRouter host discovery (AST-1959): probe_host + the per-batch single-flight host map.
Receipt lookup (AST-2218): get_receipt against a stubbed httpx.get (TIMESHEET_RECEIPT_FIELDS shape).

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

# Branches (get_receipt, AST-2218): shared TIMESHEET_RECEIPT_FIELDS; 200+cost → billed;
# 404 / empty / null cost → error/not_ready with null platform_cost; never raises.
_KEY = "sk-or-secret-key"


class _Get:
    """Stub for httpx.get: records each call; answers with (status, json body) or raises."""

    def __init__(self, status: int = 200, body: Any = None, raise_exc: Exception | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self.status, self.body, self.raise_exc = status, body, raise_exc

    def __call__(self, url: str, **kwargs: Any) -> Any:
        self.calls.append({"url": url, **kwargs})
        if self.raise_exc:
            raise self.raise_exc
        return SimpleNamespace(status_code=self.status, text=repr(self.body), json=lambda: self.body)


class TestAst2218GetReceipt:
    """Parent AC5 OpenRouter half — billed get_receipt."""

    def _install(self, monkeypatch: pytest.MonkeyPatch, get: _Get) -> None:
        monkeypatch.setattr(openrouter.httpx, "get", get)
        monkeypatch.setattr(openrouter, "require_controlled_external_io", lambda _c: None)

    def test_two_ids_200_and_404_shared_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import TIMESHEET_RECEIPT_FIELDS

        calls: list[str] = []

        def _get(url: str, **kwargs: Any) -> Any:
            gid = kwargs.get("params", {}).get("id")
            calls.append(gid)
            if gid == "id-ok":
                body = {
                    "data": {
                        "total_cost": 0.0123,
                        "native_tokens_prompt": 10,
                        "native_tokens_completion": 20,
                        "native_tokens_cached": 3,
                    }
                }
                return SimpleNamespace(status_code=200, text="ok", json=lambda: body)
            return SimpleNamespace(status_code=404, text="missing", json=lambda: {"error": {}})

        monkeypatch.setattr(openrouter.httpx, "get", _get)
        monkeypatch.setattr(openrouter, "require_controlled_external_io", lambda _c: None)
        out = openrouter.get_receipt(["id-ok", "id-404"], _KEY)
        assert calls == ["id-ok", "id-404"]
        assert len(out) == 2
        assert set(out[0]) == set(TIMESHEET_RECEIPT_FIELDS)
        assert set(out[1]) == set(TIMESHEET_RECEIPT_FIELDS)
        assert out[0]["platform_cost"] == pytest.approx(0.0123)
        assert out[0]["completion_status"] == "success"
        assert out[0]["native_tokens_prompt"] == 10
        assert out[1]["platform_cost"] is None
        assert out[1]["completion_status"] == "error"

    def test_not_ready_null_cost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._install(monkeypatch, _Get(body={"data": {"total_cost": None}}))
        out = openrouter.get_receipt(["gen-1"], _KEY)
        assert out[0]["platform_cost"] is None
        assert out[0]["completion_status"] == "not_ready"

    def test_integration_guard_no_http(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def blocked(caller: str) -> None:
            raise RuntimeError(f"{caller}: live external I/O blocked in integration mode")

        get = _Get(body={"data": {"total_cost": 1.0}})
        monkeypatch.setattr(openrouter, "require_controlled_external_io", blocked)
        monkeypatch.setattr(openrouter.httpx, "get", get)
        out = openrouter.get_receipt(["gen-1"], _KEY)
        assert out[0]["platform_cost"] is None and out[0]["completion_status"] == "error"
        assert get.calls == []

    def test_never_raises_on_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._install(monkeypatch, _Get(raise_exc=httpx.ReadTimeout("read timed out")))
        out = openrouter.get_receipt(["gen-1"], _KEY)
        assert out[0]["completion_status"] == "error"
        assert out[0]["platform_cost"] is None
