"""AST-2238 — platform astral_agent enqueue/await client (Telescope-shaped queue half)."""

from __future__ import annotations

import asyncio
import json
import zlib
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.external import astral_agent as aa
from src.utils.config import ASTRAL_AGENT_CONFIG


class _ResolvingWaiters(dict):
    """submit() registers its future here; resolve it at once with a canned job row."""

    def __init__(self, row: dict[str, Any]) -> None:
        super().__init__()
        self._row = row

    def __setitem__(self, key: str, fut: asyncio.Future) -> None:
        super().__setitem__(key, fut)
        fut.set_result(self._row)


def _encode(result: Any) -> bytes:
    return zlib.compress(json.dumps(result).encode("utf-8"))


async def _drive_submit(
    monkeypatch: pytest.MonkeyPatch, row: dict[str, Any], request: dict | None = None
) -> Any:
    """Real _AstralAgentQueue.submit against mocked pool + instant waiter resolve."""
    monkeypatch.setattr(aa, "require_controlled_external_io", lambda *_a, **_k: None)
    conn = MagicMock()
    conn.execute = AsyncMock()
    conn.transaction = MagicMock(return_value=AsyncMock())
    db = MagicMock()
    db.acquire = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=conn)))
    q = aa._AstralAgentQueue()
    monkeypatch.setattr(q, "_get_db", AsyncMock(return_value=db))
    monkeypatch.setattr(q, "_state", lambda: SimpleNamespace(waiters=_ResolvingWaiters(row)))
    monkeypatch.setattr(q, "_maybe_wake", AsyncMock())
    return await q.submit(request or {"provider": "stub", "model": "m1"})


class TestAst2238ContractAndFence:
    def test_contract_constants_match_agent_job_schema(self) -> None:
        assert aa._JOB_TABLE == "agent_job"
        assert aa._WORKER_TABLE == "agent_worker"
        assert aa._CHANNEL_NEW == "agent_job_new"
        assert aa._CHANNEL_DONE == "agent_job_done"
        assert aa._TERMINAL == ("done", "failed", "cancelled")

    def test_module_has_zero_service_imports(self) -> None:
        import ast
        from pathlib import Path

        src = Path(aa.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        offenders: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "service" or alias.name.startswith("service."):
                        offenders.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "service" or node.module.startswith("service."):
                    offenders.append(node.module)
        assert offenders == [], f"service imports in astral_agent.py: {offenders}"


class TestAst2238DsnStrict:
    def test_missing_env_raises_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(ASTRAL_AGENT_CONFIG["database_url_env"], raising=False)
        q = aa._AstralAgentQueue()
        with pytest.raises(aa.AstralAgentError) as ei:
            q._dsn()
        assert ei.value.failure_class == "connectivity_failure"
        assert ASTRAL_AGENT_CONFIG["database_url_env"] in ei.value.detail

    def test_blank_env_raises_connectivity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(ASTRAL_AGENT_CONFIG["database_url_env"], "   ")
        q = aa._AstralAgentQueue()
        with pytest.raises(aa.AstralAgentError) as ei:
            q._dsn()
        assert ei.value.failure_class == "connectivity_failure"

    @pytest.mark.asyncio
    async def test_submit_connectivity_before_insert(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(aa, "require_controlled_external_io", lambda *_a, **_k: None)
        monkeypatch.delenv(ASTRAL_AGENT_CONFIG["database_url_env"], raising=False)
        q = aa._AstralAgentQueue()
        with pytest.raises(aa.AstralAgentError) as ei:
            await q.submit({"x": 1})
        assert ei.value.failure_class == "connectivity_failure"


class TestAst2238SubmitTerminal:
    @pytest.mark.asyncio
    async def test_done_returns_decoded_result(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {"stub": True, "echo": {"provider": "stub"}}
        row = {"status": "done", "result": _encode(payload), "error": None, "error_class": None}
        out = await _drive_submit(monkeypatch, row)
        assert out == payload

    @pytest.mark.asyncio
    async def test_failed_passthrough_error_class(self, monkeypatch: pytest.MonkeyPatch) -> None:
        row = {
            "status": "failed",
            "result": None,
            "error": "provider blew up",
            "error_class": "provider_rate_limit",
        }
        with pytest.raises(aa.AstralAgentError) as ei:
            await _drive_submit(monkeypatch, row)
        assert ei.value.failure_class == "provider_rate_limit"

    @pytest.mark.asyncio
    async def test_failed_timeout_maps_to_astral_agent_timeout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        row = {
            "status": "failed",
            "result": None,
            "error": "expired",
            "error_class": "timeout",
        }
        with pytest.raises(aa.AstralAgentError) as ei:
            await _drive_submit(monkeypatch, row)
        assert ei.value.failure_class == "astral_agent_timeout"

    @pytest.mark.asyncio
    async def test_cancelled_maps_to_astral_agent_cancelled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        row = {
            "status": "cancelled",
            "result": None,
            "error": "caller gave up",
            "error_class": "cancelled",
        }
        with pytest.raises(aa.AstralAgentError) as ei:
            await _drive_submit(monkeypatch, row)
        assert ei.value.failure_class == "astral_agent_cancelled"

    @pytest.mark.asyncio
    async def test_failed_unknown_class_is_job_failed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        row = {
            "status": "failed",
            "result": None,
            "error": "mystery",
            "error_class": "",
        }
        with pytest.raises(aa.AstralAgentError) as ei:
            await _drive_submit(monkeypatch, row)
        assert ei.value.failure_class == "astral_agent_job_failed"


class TestAst2238WakeUrl:
    def test_wake_url_from_base_url_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_AGENT_BASE_URL", raising=False)
        monkeypatch.delenv("ASTRAL_AGENT_BASE_URLS", raising=False)
        monkeypatch.setenv("ASTRAL_AGENT_BASE_URL", "http://agent.railway.internal:8080")
        assert aa._astral_agent_wake_url() == "http://agent.railway.internal:8080/wake"

    def test_wake_url_empty_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_AGENT_BASE_URL", raising=False)
        monkeypatch.delenv("ASTRAL_AGENT_BASE_URLS", raising=False)
        assert aa._astral_agent_wake_url() == ""


class TestAst2238OneShotLoopTeardown:
    @pytest.fixture
    def fresh_queue(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv(ASTRAL_AGENT_CONFIG["database_url_env"], "postgresql://fake/db")
        q = aa._AstralAgentQueue()
        monkeypatch.setattr(aa, "_pool", q)
        fake_db = MagicMock()
        fake_db.close = AsyncMock()
        fake_db.fetch = AsyncMock(return_value=[])
        create_pool = AsyncMock(return_value=fake_db)
        monkeypatch.setattr(aa.asyncpg, "create_pool", create_pool)
        return q, fake_db, create_pool

    @staticmethod
    def _touch(q: Any, seen: dict[str, Any]):
        async def _run() -> str:
            await q._get_db()
            loop = asyncio.get_running_loop()
            st = q._states[loop]
            st.listener = MagicMock(is_closed=MagicMock(return_value=False), close=AsyncMock())
            seen.update(loop=loop, st=st, listener=st.listener)
            return "ok"

        return _run

    def test_run_one_shot_releases_loop_state(self, fresh_queue) -> None:
        q, fake_db, _ = fresh_queue
        seen: dict[str, Any] = {}
        assert aa.run_one_shot(self._touch(q, seen)()) == "ok"
        assert seen["loop"] not in q._states
        assert fake_db.close.await_count == 1
        assert seen["listener"].close.await_count == 1

    @pytest.mark.asyncio
    async def test_module_submit_delegates_to_pool(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stub = AsyncMock(return_value={"ok": True})
        monkeypatch.setattr(aa, "_pool", SimpleNamespace(submit=stub))
        out = await aa.submit({"a": 1}, priority=2)
        assert out == {"ok": True}
        stub.assert_awaited_once_with({"a": 1}, priority=2)
