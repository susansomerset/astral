"""Telescope serverless — sleep when idle, wake on GET /wake, race guard."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("asyncpg")

from fastapi.testclient import TestClient  # noqa: E402

import app as app_mod  # noqa: E402


def _awake_runtime(monkeypatch, *, idle: float, pending: list[bool]):
    """Runtime with fake db / Firefox / worker; has_pending answers from `pending` in order."""
    rt = app_mod.Runtime()
    rt.db = MagicMock(close=AsyncMock())
    rt.firefox = MagicMock(stop=AsyncMock())
    rt.worker = MagicMock(stop=AsyncMock(), idle_seconds=MagicMock(return_value=idle))
    answers = iter(pending)
    monkeypatch.setattr(app_mod.jobqueue, "has_pending", AsyncMock(side_effect=lambda _db: next(answers)))
    return rt


class TestSleep:
    async def test_sleeps_when_idle_and_queue_empty(self, monkeypatch) -> None:
        rt = _awake_runtime(monkeypatch, idle=301, pending=[False, False])
        db, firefox, worker = rt.db, rt.firefox, rt.worker
        await rt._maybe_sleep()
        assert rt.asleep is True
        worker.stop.assert_awaited_once()
        firefox.stop.assert_awaited_once()
        db.close.assert_awaited_once()
        assert rt.db is None and rt.worker is None and rt.firefox is None

    async def test_stays_up_before_idle_timeout(self, monkeypatch) -> None:
        rt = _awake_runtime(monkeypatch, idle=10, pending=[])
        await rt._maybe_sleep()
        assert rt.asleep is False
        rt.worker.stop.assert_not_awaited()

    async def test_stays_up_while_work_is_pending(self, monkeypatch) -> None:
        rt = _awake_runtime(monkeypatch, idle=301, pending=[True])
        await rt._maybe_sleep()
        assert rt.asleep is False
        rt.worker.stop.assert_not_awaited()

    async def test_race_guard_restarts_worker_when_job_lands_mid_sleep(self, monkeypatch) -> None:
        rt = _awake_runtime(monkeypatch, idle=301, pending=[False, True])
        new_worker = MagicMock(start=AsyncMock())
        monkeypatch.setattr(app_mod, "QueueWorker", MagicMock(return_value=new_worker))
        firefox = rt.firefox
        await rt._maybe_sleep()
        assert rt.asleep is False
        assert rt.worker is new_worker
        new_worker.start.assert_awaited_once()
        firefox.stop.assert_not_awaited()  # Firefox kept for the restarted worker


class TestWake:
    async def test_wake_restarts_only_when_asleep(self, monkeypatch) -> None:
        rt = app_mod.Runtime()
        start = AsyncMock()
        monkeypatch.setattr(rt, "_start_locked", start)
        assert await rt.wake() is False
        rt.asleep = True
        assert await rt.wake() is True
        start.assert_awaited_once()

    def test_wake_endpoint(self, monkeypatch) -> None:
        rt = app_mod.Runtime()
        rt.wake = AsyncMock(return_value=True)
        app_mod.app.state.runtime = rt
        resp = TestClient(app_mod.app).get("/wake")
        assert resp.status_code == 200 and resp.json() == {"status": "awake", "woke": True}

    def test_wake_failure_is_503(self) -> None:
        rt = app_mod.Runtime()
        rt.wake = AsyncMock(side_effect=OSError("db down"))
        app_mod.app.state.runtime = rt
        resp = TestClient(app_mod.app).get("/wake")
        assert resp.status_code == 503
