"""AST-2237 — FastAPI /healthz + /wake (no auth); Runtime mocked off Postgres."""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402


def _fake_worker(*, db_ok: bool = True, loop_fresh: bool = True) -> MagicMock:
    w = MagicMock()
    w.worker_id = "test-worker:1:abc"
    w.held = 0
    w.in_flight = 0
    w.db_ok = db_ok
    age = 1.0 if loop_fresh else 10_000.0
    w.last_loop_at = time.monotonic() - age
    w.start = AsyncMock()
    w.stop = AsyncMock()
    w.idle_seconds = MagicMock(return_value=0.0)
    return w


@pytest.fixture
def astral_agent_client(astral_agent_modules):
    """TestClient with Postgres/worker lifespan stubbed out."""
    import importlib

    import app as app_mod

    importlib.reload(app_mod)

    fake_pool = MagicMock()
    fake_pool.close = AsyncMock()
    worker = _fake_worker()

    async def _start_locked(self: Any) -> None:
        self.db = fake_pool
        self.worker = worker
        self.asleep = False

    async def _stop_locked(self: Any) -> None:
        self.db = self.worker = None

    with (
        patch.object(app_mod.Runtime, "_start_locked", _start_locked),
        patch.object(app_mod.Runtime, "_stop_locked", _stop_locked),
        patch.object(app_mod.Runtime, "_idle_loop", AsyncMock()),
    ):
        with TestClient(app_mod.app) as client:
            client.app.state.runtime.worker = worker
            client.app.state.runtime.asleep = False
            client.app.state.runtime.db = fake_pool
            yield client, worker, app_mod


class TestAst2237HealthzAndWake:
    def test_healthz_ok_no_auth(self, astral_agent_client) -> None:
        client, _worker, _app = astral_agent_client
        resp = client.get("/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["worker_id"] == "test-worker:1:abc"
        assert "db_ok" in body
        assert "browser_ok" not in body

    def test_healthz_asleep(self, astral_agent_client) -> None:
        client, _worker, _app = astral_agent_client
        client.app.state.runtime.asleep = True
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json() == {"status": "asleep"}

    def test_healthz_unhealthy_503(self, astral_agent_client) -> None:
        client, worker, _app = astral_agent_client
        worker.db_ok = False
        resp = client.get("/healthz")
        assert resp.status_code == 503
        assert resp.json()["status"] == "unhealthy"

    def test_wake_already_awake(self, astral_agent_client) -> None:
        client, _worker, _app = astral_agent_client
        client.app.state.runtime.asleep = False
        resp = client.get("/wake")
        assert resp.status_code == 200
        assert resp.json() == {"status": "awake", "woke": False}

    def test_wake_from_sleep(self, astral_agent_client) -> None:
        # Patched _start_locked resumes without real Postgres.
        client, _worker, _app = astral_agent_client
        client.app.state.runtime.asleep = True
        client.app.state.runtime.db = None
        client.app.state.runtime.worker = None
        resp = client.get("/wake")
        assert resp.status_code == 200
        assert resp.json() == {"status": "awake", "woke": True}
