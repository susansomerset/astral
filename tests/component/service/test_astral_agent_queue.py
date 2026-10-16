"""AST-2237 — settings, stub executor, encode/decode, insert→claim→terminal + dual-replica."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

pytest.importorskip("asyncpg")


# ---------------------------------------------------------------------------
# In-memory job store — mirrors claim/complete/fail semantics without Postgres.
# Dual-replica non-claim: status=running rows are ineligible for a second claim.
# ---------------------------------------------------------------------------


@dataclass
class _JobRow:
    id: str
    request: dict
    status: str = "queued"
    attempts: int = 0
    max_attempts: int = 4
    worker_id: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    error_class: Optional[str] = None


@dataclass
class FakeAgentJobStore:
    jobs: Dict[str, _JobRow] = field(default_factory=dict)

    def insert(self, request: dict, *, job_id: Optional[str] = None) -> str:
        jid = job_id or str(uuid.uuid4())
        self.jobs[jid] = _JobRow(id=jid, request=dict(request))
        return jid

    async def claim(
        self, _pool: Any, *, limit: int, worker_id: str, lease_seconds: int
    ) -> list:
        from jobqueue import ClaimedJob

        out: list = []
        for row in self.jobs.values():
            if len(out) >= limit:
                break
            if row.status != "queued":
                continue
            row.status = "running"
            row.attempts += 1
            row.worker_id = worker_id
            out.append(
                ClaimedJob(
                    id=row.id,
                    request=row.request,
                    attempts=row.attempts,
                    max_attempts=row.max_attempts,
                )
            )
        return out

    async def complete(
        self, _pool: Any, *, job_id: str, worker_id: str, result: Any
    ) -> bool:
        row = self.jobs.get(job_id)
        if row is None or row.status != "running" or row.worker_id != worker_id:
            return False
        row.status = "done"
        row.result = result
        row.worker_id = worker_id
        return True

    async def fail(
        self,
        _pool: Any,
        *,
        job_id: str,
        worker_id: str,
        error: str,
        error_class: str,
        retry_in_seconds: Optional[float],
    ) -> Optional[str]:
        row = self.jobs.get(job_id)
        if row is None or row.status != "running" or row.worker_id != worker_id:
            return None
        if retry_in_seconds is None:
            row.status = "failed"
            row.error = error[:2000]
            row.error_class = error_class
            return "failed"
        row.status = "queued"
        row.error = error[:2000]
        row.error_class = error_class
        row.worker_id = None
        return "queued"


# ---------------------------------------------------------------------------
# Settings / executor / codec (no Postgres)
# ---------------------------------------------------------------------------


class TestAst2237Settings:
    def test_missing_database_url_crashes_loud(self, astral_agent_root: Path) -> None:
        env = {k: v for k, v in os.environ.items() if k != "ASTRAL_DATABASE_URL"}
        code = (
            "import sys\n"
            f"sys.path.insert(0, {str(astral_agent_root)!r})\n"
            "import settings\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode != 0
        blob = (proc.stderr or "") + (proc.stdout or "")
        assert "ASTRAL_DATABASE_URL" in blob or "KeyError" in blob

    def test_load_settings_reads_required_dsn(self, astral_agent_modules: Path) -> None:
        import settings as settings_mod

        assert settings_mod.settings.database_url == "postgresql://astral-agent-test/harness"
        assert settings_mod.settings.worker_concurrency == 4
        assert settings_mod.settings.lease_seconds == 300
        assert settings_mod.settings.port == 8080


class TestAst2237Executor:
    @pytest.mark.asyncio
    async def test_stub_echoes_request(self, astral_agent_modules: Path) -> None:
        import executor

        req = {"model": "stub", "messages": [{"role": "user", "content": "hi"}]}
        out = await executor.execute(req)
        assert out == {
            "stub": True,
            "echo": req,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }

    @pytest.mark.asyncio
    async def test_non_dict_raises(self, astral_agent_modules: Path) -> None:
        import executor

        with pytest.raises(ValueError, match="request must be a dict"):
            await executor.execute("not-a-dict")  # type: ignore[arg-type]


class TestAst2237ResultCodec:
    def test_encode_decode_roundtrip(self, astral_agent_modules: Path) -> None:
        import jobqueue

        payload = {"stub": True, "echo": {"x": 1}}
        blob = jobqueue.encode_result(payload)
        assert isinstance(blob, (bytes, bytearray))
        assert jobqueue.decode_result(blob) == payload
        assert jobqueue.decode_result(None) is None

    def test_claim_sql_uses_skip_locked_and_agent_job(
        self, astral_agent_modules: Path
    ) -> None:
        """Contract: real claim SQL must SKIP LOCKED on agent_job (AC2 dual-replica)."""
        import inspect

        import jobqueue

        src = inspect.getsource(jobqueue.claim)
        assert "FOR UPDATE SKIP LOCKED" in src
        assert "agent_job" in jobqueue.JOB_TABLE
        assert jobqueue.JOB_TABLE == "agent_job"
        assert jobqueue.CHANNEL_NEW == "agent_job_new"


# ---------------------------------------------------------------------------
# AC2 — insert → claim → terminal; second replica cannot claim running lease
# ---------------------------------------------------------------------------


class TestAst2237ClaimLeaseTerminal:
    @pytest.mark.asyncio
    async def test_insert_claim_complete_stub_terminal(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import jobqueue
        from worker import QueueWorker

        store = FakeAgentJobStore()
        jid = store.insert({"prompt": "ping"})
        monkeypatch.setattr(jobqueue, "claim", store.claim)
        monkeypatch.setattr(jobqueue, "complete", store.complete)
        monkeypatch.setattr(jobqueue, "fail", store.fail)

        w_a = QueueWorker(MagicMock(), worker_id="replica-a", concurrency=1)
        claimed = await jobqueue.claim(
            MagicMock(), limit=1, worker_id=w_a.worker_id, lease_seconds=300
        )
        assert len(claimed) == 1
        assert claimed[0].id == jid
        assert store.jobs[jid].status == "running"
        assert store.jobs[jid].worker_id == "replica-a"

        await w_a._run_job(claimed[0])
        row = store.jobs[jid]
        assert row.status == "done"
        assert row.result == {
            "stub": True,
            "echo": {"prompt": "ping"},
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }

    @pytest.mark.asyncio
    async def test_dual_replica_second_claim_empty_while_leased(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import jobqueue

        store = FakeAgentJobStore()
        store.insert({"n": 1})
        monkeypatch.setattr(jobqueue, "claim", store.claim)

        first = await jobqueue.claim(
            MagicMock(), limit=1, worker_id="replica-a", lease_seconds=300
        )
        assert len(first) == 1
        second = await jobqueue.claim(
            MagicMock(), limit=1, worker_id="replica-b", lease_seconds=300
        )
        assert second == []

    @pytest.mark.asyncio
    async def test_stub_crash_writes_failed_terminal(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import executor
        import jobqueue
        from worker import QueueWorker

        store = FakeAgentJobStore()
        jid = store.insert({"boom": True})
        monkeypatch.setattr(jobqueue, "claim", store.claim)
        monkeypatch.setattr(jobqueue, "complete", store.complete)
        monkeypatch.setattr(jobqueue, "fail", store.fail)

        async def _raise(_req: dict) -> dict:
            raise RuntimeError("stub exploded")

        monkeypatch.setattr(executor, "execute", _raise)

        w = QueueWorker(MagicMock(), worker_id="replica-a", concurrency=1)
        claimed = await jobqueue.claim(
            MagicMock(), limit=1, worker_id=w.worker_id, lease_seconds=300
        )
        await w._run_job(claimed[0])
        row = store.jobs[jid]
        assert row.status == "failed"
        assert row.error_class == "stub_error"
        assert "stub exploded" in (row.error or "")
