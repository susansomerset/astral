"""AST-2237 — settings, stub executor, encode/decode, insert→claim→terminal + dual-replica."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
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
    started: bool = False  # start() ran for the current claim (started_at IS NOT NULL)


@dataclass
class FakeAgentJobStore:
    jobs: Dict[str, _JobRow] = field(default_factory=dict)
    heartbeats: list = field(default_factory=list)  # (job_ids, held, running) per call

    def insert(self, request: dict, *, job_id: Optional[str] = None) -> str:
        jid = job_id or str(uuid.uuid4())
        self.jobs[jid] = _JobRow(id=jid, request=dict(request))
        return jid

    async def claim(
        self, _pool: Any, *, limit: Optional[int], worker_id: str, lease_seconds: int
    ) -> list:
        from jobqueue import ClaimedJob

        out: list = []
        for row in self.jobs.values():
            if limit is not None and len(out) >= limit:
                break
            if row.status != "queued":
                continue
            row.status = "running"  # leased; a claim charges no attempt
            row.started = False
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

    async def start(self, _pool: Any, *, job_id: str, worker_id: str) -> Optional[int]:
        row = self.jobs.get(job_id)
        if row is None or row.status != "running" or row.worker_id != worker_id:
            return None
        row.attempts += 1
        row.started = True
        return row.attempts

    async def heartbeat(
        self,
        _pool: Any,
        *,
        worker_id: str,
        job_ids: Any,
        lease_seconds: int,
        held: int,
        running: int,
    ) -> set:
        self.heartbeats.append((list(job_ids), held, running))
        return {
            j
            for j in job_ids
            if j in self.jobs
            and self.jobs[j].status == "running"
            and self.jobs[j].worker_id == worker_id
        }

    async def release_all(self, _pool: Any, *, worker_id: str) -> int:
        n = 0
        for row in self.jobs.values():
            if row.status == "running" and row.worker_id == worker_id:
                row.attempts = max(row.attempts - int(row.started), 0)  # refund started only
                row.status, row.worker_id, row.started = "queued", None, False
                n += 1
        return n

    def reap(self, worker_id: str) -> None:
        """A crash: leases expire; maintain() re-queues (or fails when attempts are used up)."""
        for row in self.jobs.values():
            if row.status == "running" and row.worker_id == worker_id:
                row.status = "failed" if row.attempts >= row.max_attempts else "queued"
                row.worker_id = None

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
        assert not hasattr(settings_mod.settings, "worker_concurrency")  # no claim cap
        assert settings_mod.settings.admit_interval_seconds == 0.1
        assert settings_mod.settings.lease_seconds == 300
        assert settings_mod.settings.port == 8080


def _assembled_request(**overrides: Any) -> dict:
    """Minimal AST-2239 assembled provider request (platform-owned wire shape)."""
    req = {
        "protocol": "anthropic",
        "server_id": "anthropic",
        "model": "claude-haiku-4-5",
        "api_key": "sk-test",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 64,
    }
    req.update(overrides)
    return req


class TestAst2237Executor:
    """AST-2239: stub echo retired — validate + dispatch (providers mocked)."""

    @pytest.mark.asyncio
    async def test_dispatches_anthropic_provider(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import executor
        from providers import anthropic_provider

        sent: dict[str, Any] = {}

        async def _fake(req: dict) -> dict:
            sent["req"] = req
            return {"success": True, "api_response": "ok", "usage": {"input_tokens": 1}}

        monkeypatch.setattr(anthropic_provider, "send", _fake)
        out = await executor.execute(_assembled_request())
        assert out["success"] is True
        assert sent["req"]["protocol"] == "anthropic"

    @pytest.mark.asyncio
    async def test_non_dict_raises_bad_request(self, astral_agent_modules: Path) -> None:
        import executor
        from providers.errors import ProviderJobError

        with pytest.raises(ProviderJobError) as ei:
            await executor.execute("not-a-dict")  # type: ignore[arg-type]
        assert ei.value.error_class == "bad_request"


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
    async def test_insert_claim_complete_provider_terminal(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import executor
        import jobqueue
        from worker import QueueWorker

        store = FakeAgentJobStore()
        req = _assembled_request()
        jid = store.insert(req)
        monkeypatch.setattr(jobqueue, "claim", store.claim)
        monkeypatch.setattr(jobqueue, "start", store.start)
        monkeypatch.setattr(jobqueue, "complete", store.complete)
        monkeypatch.setattr(jobqueue, "fail", store.fail)

        async def _ok(_req: dict) -> dict:
            return {
                "success": True,
                "api_response": "pong",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            }

        monkeypatch.setattr(executor, "execute", _ok)

        w_a = QueueWorker(MagicMock(), worker_id="replica-a")
        claimed = await jobqueue.claim(
            MagicMock(), limit=1, worker_id=w_a.worker_id, lease_seconds=300
        )
        assert len(claimed) == 1
        assert claimed[0].id == jid
        await w_a._run_job(claimed[0])
        row = store.jobs[jid]
        assert row.status == "done"
        assert row.result["success"] is True
        assert row.result["api_response"] == "pong"

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
    async def test_executor_crash_writes_failed_terminal(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import executor
        import jobqueue
        from worker import QueueWorker

        store = FakeAgentJobStore()
        jid = store.insert(_assembled_request())
        monkeypatch.setattr(jobqueue, "claim", store.claim)
        monkeypatch.setattr(jobqueue, "start", store.start)
        monkeypatch.setattr(jobqueue, "complete", store.complete)
        monkeypatch.setattr(jobqueue, "fail", store.fail)

        async def _raise(_req: dict) -> dict:
            raise RuntimeError("provider exploded")

        monkeypatch.setattr(executor, "execute", _raise)

        w = QueueWorker(MagicMock(), worker_id="replica-a")
        claimed = await jobqueue.claim(
            MagicMock(), limit=1, worker_id=w.worker_id, lease_seconds=300
        )
        await w._run_job(claimed[0])
        row = store.jobs[jid]
        assert row.status == "failed"
        assert row.error_class == "executor_error"
        assert "provider exploded" in (row.error or "")

    @pytest.mark.asyncio
    async def test_provider_job_error_fails_with_error_class(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import executor
        import jobqueue
        from providers.errors import ProviderJobError
        from worker import QueueWorker

        store = FakeAgentJobStore()
        jid = store.insert({})
        monkeypatch.setattr(jobqueue, "claim", store.claim)
        monkeypatch.setattr(jobqueue, "start", store.start)
        monkeypatch.setattr(jobqueue, "complete", store.complete)
        monkeypatch.setattr(jobqueue, "fail", store.fail)

        async def _bad(_req: dict) -> dict:
            raise ProviderJobError("bad_request", "missing protocol")

        monkeypatch.setattr(executor, "execute", _bad)

        w = QueueWorker(MagicMock(), worker_id="replica-a")
        claimed = await jobqueue.claim(
            MagicMock(), limit=1, worker_id=w.worker_id, lease_seconds=300
        )
        await w._run_job(claimed[0])
        row = store.jobs[jid]
        assert row.status == "failed"
        assert row.error_class == "bad_request"
        assert "missing protocol" in (row.error or "")

    @pytest.mark.asyncio
    async def test_soft_fail_still_completes_job(
        self, astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import executor
        import jobqueue
        from worker import QueueWorker

        store = FakeAgentJobStore()
        jid = store.insert(_assembled_request())
        monkeypatch.setattr(jobqueue, "claim", store.claim)
        monkeypatch.setattr(jobqueue, "start", store.start)
        monkeypatch.setattr(jobqueue, "complete", store.complete)
        monkeypatch.setattr(jobqueue, "fail", store.fail)

        async def _soft(_req: dict) -> dict:
            return {
                "success": False,
                "error": "rate limited",
                "failure_class": "provider_rate_limit",
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }

        monkeypatch.setattr(executor, "execute", _soft)

        w = QueueWorker(MagicMock(), worker_id="replica-a")
        claimed = await jobqueue.claim(
            MagicMock(), limit=1, worker_id=w.worker_id, lease_seconds=300
        )
        await w._run_job(claimed[0])
        row = store.jobs[jid]
        assert row.status == "done"
        assert row.result["success"] is False
        assert row.result["failure_class"] == "provider_rate_limit"


# ---------------------------------------------------------------------------
# Step 3 — holding area + gate (U1): claim everything, gate starts, attempts charged at start
# ---------------------------------------------------------------------------


class _FakeGate:
    """Admits while fewer than `limit` jobs run (None = admit everything)."""

    def __init__(self, limit: Optional[int] = None) -> None:
        self.limit = limit

    def admit(self, running: int) -> bool:
        return self.limit is None or running < self.limit


async def _until(pred, timeout: float = 2.0) -> None:
    import asyncio

    loop = asyncio.get_running_loop()
    end = loop.time() + timeout
    while not pred():
        assert loop.time() < end, "condition not reached"
        await asyncio.sleep(0.01)


@pytest.fixture
def holding(astral_agent_modules: Path, monkeypatch: pytest.MonkeyPatch):
    """(store, make_worker, executor_calls, release) with the queue + executor faked."""
    import asyncio
    import dataclasses

    import executor
    import jobqueue
    import worker as worker_mod

    store = FakeAgentJobStore()
    for name in ("claim", "start", "complete", "fail", "heartbeat", "release_all"):
        monkeypatch.setattr(jobqueue, name, getattr(store, name))
    monkeypatch.setattr(
        worker_mod,
        "settings",
        dataclasses.replace(worker_mod.settings, shutdown_grace_seconds=0.05),
    )
    calls: list = []
    release: Dict[int, asyncio.Event] = {}

    async def _execute(req: dict) -> dict:
        calls.append(req["n"])
        await release.setdefault(req["n"], asyncio.Event()).wait()
        return {"success": True, "api_response": "ok", "usage": {}}

    monkeypatch.setattr(executor, "execute", _execute)
    made: list = []

    def make_worker(gate: Optional[_FakeGate] = None):
        w = worker_mod.QueueWorker(MagicMock(), worker_id="replica-a", gate=gate)
        w._tasks = [
            asyncio.create_task(w._claim_loop()),
            asyncio.create_task(w._gate_loop()),
        ]
        made.append(w)
        return w

    yield store, make_worker, calls, release
    for w in made:
        w._stopping.set()
        for t in [*w._tasks, *w._running.values()]:
            t.cancel()


class TestStep3HoldingArea:
    @pytest.mark.asyncio
    async def test_claims_every_job_no_cap_and_admit_all_starts_them(self, holding) -> None:
        store, make_worker, calls, _release = holding
        for n in range(12):  # old cap was 4
            store.insert({"n": n})
        w = make_worker()
        await _until(lambda: w.in_flight == 12)
        assert w.held == 12 and not w._waiting
        assert sorted(calls) == list(range(12))

    @pytest.mark.asyncio
    async def test_closed_gate_holds_jobs_leased_and_heartbeated(self, holding) -> None:
        import asyncio

        store, make_worker, calls, _release = holding
        ids = [store.insert({"n": n}) for n in range(5)]
        w = make_worker(_FakeGate(limit=0))
        await _until(lambda: len(w._waiting) == 5)
        assert calls == [] and w.in_flight == 0
        # Leased in the DB (status running), nothing charged yet.
        assert all(store.jobs[i].status == "running" for i in ids)
        assert all(store.jobs[i].attempts == 0 for i in ids)
        hb = asyncio.create_task(w._heartbeat_loop())
        w._tasks.append(hb)
        await _until(lambda: store.heartbeats)
        job_ids, held, running = store.heartbeats[0]
        assert sorted(job_ids) == sorted(ids) and (held, running) == (5, 0)

    @pytest.mark.asyncio
    async def test_finish_wakes_gate_and_oldest_waiting_starts_first(self, holding) -> None:
        store, make_worker, calls, release = holding
        ids = [store.insert({"n": n}) for n in range(3)]
        w = make_worker(_FakeGate(limit=1))
        await _until(lambda: calls == [0])
        assert len(w._waiting) == 2
        for n in range(3):
            await _until(lambda n=n: n in release)  # job n has started
            release[n].set()
            await _until(lambda n=n: store.jobs[ids[n]].status == "done")
        assert calls == [0, 1, 2]
        # Charged one attempt each, at start.
        assert [store.jobs[i].attempts for i in ids] == [1, 1, 1]

    @pytest.mark.asyncio
    async def test_heartbeat_drops_cancelled_waiting_job_without_starting_it(
        self, holding
    ) -> None:
        import asyncio

        store, make_worker, calls, _release = holding
        gate = _FakeGate(limit=0)
        a = store.insert({"n": 0})
        b = store.insert({"n": 1})
        w = make_worker(gate)
        await _until(lambda: len(w._waiting) == 2)
        store.jobs[a].status = "cancelled"  # the caller gave up
        w._tasks.append(asyncio.create_task(w._heartbeat_loop()))
        await _until(lambda: a not in w._waiting)
        assert list(w._waiting) == [b]
        gate.limit = None
        w._gate_wake.set()
        await _until(lambda: calls == [1])  # only the surviving job starts

    @pytest.mark.asyncio
    async def test_stop_hands_back_waiting_jobs_and_refunds_only_the_started(
        self, holding
    ) -> None:
        store, make_worker, calls, _release = holding
        ids = [store.insert({"n": n}) for n in range(3)]
        w = make_worker(_FakeGate(limit=1))
        await _until(lambda: calls == [0] and len(w._waiting) == 2)
        assert store.jobs[ids[0]].attempts == 1
        await w.stop()
        assert calls == [0]  # waiting jobs never started during the drain
        for i in ids:
            row = store.jobs[i]
            assert (row.status, row.worker_id, row.attempts) == ("queued", None, 0)

    @pytest.mark.asyncio
    async def test_crash_with_big_waiting_line_charges_only_started_jobs(
        self, holding
    ) -> None:
        store, make_worker, calls, _release = holding
        ids = [store.insert({"n": n}) for n in range(20)]
        for i in ids:
            store.jobs[i].max_attempts = 1
        w = make_worker(_FakeGate(limit=2))
        await _until(lambda: len(calls) == 2 and len(w._waiting) == 18)
        store.reap("replica-a")  # crash: leases expire, nothing handed back
        statuses = [store.jobs[i].status for i in ids]
        assert statuses.count("failed") == 2  # the two that began used up their only attempt
        assert statuses.count("queued") == 18  # the waiting line was never charged
        assert all(store.jobs[i].attempts == 0 for i in ids[2:])

    @pytest.mark.asyncio
    async def test_gate_error_keeps_jobs_held(self, holding) -> None:
        store, make_worker, calls, _release = holding

        class _Broken:
            def admit(self, running: int) -> bool:
                raise OSError("cgroup gone")

        store.insert({"n": 0})
        w = make_worker(_Broken())
        await _until(lambda: len(w._waiting) == 1)
        assert calls == [] and w.held == 1


_TIMEOUT = {"success": False, "api_response": "", "failure_class": "provider_call_timeout", "usage": {}}


class TestStep4TimeoutRetryOnce:
    """A timed-out call goes back in the waiting line once (same attempt); the second timeout is final."""

    @pytest.fixture
    def scripted(self, holding, monkeypatch: pytest.MonkeyPatch):
        """executor.execute answers from per-job scripts: req["script"] = results popped one per run."""
        import executor

        store, make_worker, _calls, _release = holding
        runs: list = []

        async def _execute(req: dict) -> dict:
            runs.append(req["n"])
            return req["script"].pop(0)

        monkeypatch.setattr(executor, "execute", _execute)
        return store, make_worker, runs

    @pytest.mark.asyncio
    async def test_first_timeout_goes_behind_the_line_second_is_final(self, scripted) -> None:
        store, make_worker, runs = scripted
        ok = {"success": True, "api_response": "ok", "usage": {}}
        slow = store.insert({"n": 0, "script": [dict(_TIMEOUT), dict(_TIMEOUT)]})
        fast = store.insert({"n": 1, "script": [ok]})
        make_worker(_FakeGate(limit=1))
        await _until(lambda: store.jobs[slow].status == "done" and store.jobs[fast].status == "done")
        # The retry waited behind the job that was already in line.
        assert runs == [0, 1, 0]
        assert store.jobs[slow].result["failure_class"] == "provider_call_timeout"
        assert store.jobs[fast].result["success"] is True
        # Same attempt: charged once at the first start, never again for the retry.
        assert store.jobs[slow].attempts == 1

    @pytest.mark.asyncio
    async def test_a_retry_that_succeeds_completes_normally(self, scripted) -> None:
        store, make_worker, runs = scripted
        ok = {"success": True, "api_response": "ok", "usage": {}}
        jid = store.insert({"n": 0, "script": [dict(_TIMEOUT), ok]})
        w = make_worker()
        await _until(lambda: store.jobs[jid].status == "done")
        assert (runs, store.jobs[jid].result["success"], store.jobs[jid].attempts) == ([0, 0], True, 1)
        await _until(lambda: w.held == 0)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("failure_class", ["provider_rate_limit", "provider_balance_refusal", "max_tokens", None])
    async def test_every_other_failure_completes_without_a_retry(self, scripted, failure_class) -> None:
        store, make_worker, runs = scripted
        soft = {"success": False, "api_response": "", "usage": {}, "failure_class": failure_class}
        jid = store.insert({"n": 0, "script": [soft]})
        make_worker()
        await _until(lambda: store.jobs[jid].status == "done")
        assert runs == [0]

    @pytest.mark.asyncio
    async def test_waiting_for_its_retry_the_job_stays_leased_and_heartbeated(self, scripted) -> None:
        import asyncio

        store, make_worker, runs = scripted
        jid = store.insert({"n": 0, "script": [dict(_TIMEOUT), dict(_TIMEOUT)]})

        class _Once:  # admits the first start only, so the retry stays in the waiting line
            n = 1

            def admit(self, running: int) -> bool:
                self.n, was = 0, self.n
                return bool(was)

        w = make_worker(_Once())
        await _until(lambda: jid in w._waiting and jid not in w._running)
        assert runs == [0]
        assert w._waiting[jid].timed_out is True and store.jobs[jid].status == "running"
        w._tasks.append(asyncio.create_task(w._heartbeat_loop()))
        await _until(lambda: store.heartbeats)
        assert store.heartbeats[0][0] == [jid] and store.heartbeats[0][1:] == (1, 0)

    @pytest.mark.asyncio
    async def test_job_in_both_waiting_and_running_does_not_break_heartbeat_or_stats(
        self, holding, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import asyncio

        import dataclasses

        import worker as worker_mod

        monkeypatch.setattr(
            worker_mod, "settings", dataclasses.replace(worker_mod.settings, heartbeat_seconds=0.02)
        )
        store, make_worker, _calls, _release = holding
        jid = store.insert({"n": 0})
        w = make_worker(_FakeGate(limit=0))
        await _until(lambda: jid in w._waiting)
        # The moment after a timeout: back in the waiting line, old task finished but not yet reaped.
        old = asyncio.create_task(asyncio.sleep(0))
        await old
        w._running[jid] = old
        assert w.held == 2  # a brief double count is fine
        hb = asyncio.create_task(w._heartbeat_loop())
        w._tasks.append(hb)
        await _until(lambda: store.heartbeats)
        assert not hb.done()
        w._stats_at -= 3600
        w._maybe_log_stats()  # must not raise
        # Cancelled by the caller while in both: dropped from the line once, nothing to cancel, loop alive.
        store.jobs[jid].status = "cancelled"
        await _until(lambda: jid not in w._waiting)
        assert not hb.done()

    @pytest.mark.asyncio
    async def test_old_tasks_done_callback_does_not_pop_the_new_task(self, holding) -> None:
        import asyncio

        _store, make_worker, _calls, _release = holding
        w = make_worker(_FakeGate(limit=0))
        old, new = asyncio.create_task(asyncio.sleep(0)), asyncio.create_task(asyncio.sleep(3600))
        w._running["j"] = new  # the retry already restarted under a new task
        w._job_done("j", old)
        assert w._running["j"] is new
        w._job_done("j", new)
        assert "j" not in w._running
        new.cancel()


class _SqlPool:
    """Records the SQL + args the queue functions send (no Postgres)."""

    def __init__(self) -> None:
        self.calls: list = []

    async def fetch(self, sql: str, *args: Any) -> list:
        self.calls.append(("fetch", sql, args))
        return []

    async def fetchval(self, sql: str, *args: Any) -> Any:
        self.calls.append(("fetchval", sql, args))
        return 2

    async def execute(self, sql: str, *args: Any) -> str:
        self.calls.append(("execute", sql, args))
        return "DELETE 0"


class TestStep3QueueSql:
    @pytest.mark.asyncio
    async def test_claim_takes_no_limit_and_charges_nothing(
        self, astral_agent_modules: Path
    ) -> None:
        import jobqueue

        pool = _SqlPool()
        await jobqueue.claim(pool, limit=None, worker_id="w", lease_seconds=300)
        _kind, sql, args = pool.calls[0]
        assert args[0] is None  # LIMIT NULL = no cap
        assert "attempts" not in sql.split("SET", 1)[1].split("FROM picked")[0]
        assert "started_at = NULL" in sql

    @pytest.mark.asyncio
    async def test_start_charges_attempt_and_stamps_started_at(
        self, astral_agent_modules: Path
    ) -> None:
        import jobqueue

        pool = _SqlPool()
        assert await jobqueue.start(pool, job_id="j", worker_id="w") == 2
        _kind, sql, args = pool.calls[0]
        assert "attempts = attempts + 1, started_at = now()" in sql
        assert "worker_id = $2 AND status = 'running'" in sql
        assert args == ("j", "w")

    @pytest.mark.asyncio
    async def test_release_all_refunds_only_jobs_that_started(
        self, astral_agent_modules: Path
    ) -> None:
        import jobqueue

        pool = _SqlPool()
        await jobqueue.release_all(pool, worker_id="w")
        sql = pool.calls[0][1]
        assert "GREATEST(attempts - (started_at IS NOT NULL)::int, 0)" in sql
        assert "started_at = NULL" in sql

    @pytest.mark.asyncio
    async def test_heartbeat_reports_held_and_running_on_worker_row(
        self, astral_agent_modules: Path
    ) -> None:
        import jobqueue

        class _Conn:
            def __init__(self) -> None:
                self.calls: list = []

            async def execute(self, sql: str, *args: Any) -> None:
                self.calls.append((sql, args))

            async def fetch(self, sql: str, *args: Any) -> list:
                return []

        class _Acquire:
            def __init__(self, conn: _Conn) -> None:
                self.conn = conn

            async def __aenter__(self) -> _Conn:
                return self.conn

            async def __aexit__(self, *_a: object) -> None:
                return None

        conn = _Conn()
        pool = MagicMock()
        pool.acquire = lambda: _Acquire(conn)
        await jobqueue.heartbeat(
            pool, worker_id="w", job_ids=["a", "b", "c"], lease_seconds=300, held=3, running=1
        )
        sql, args = conn.calls[0]
        assert "concurrency = $2, in_flight = $3" in sql
        assert args == ("w", 3, 1)
