"""Telescope step 3 / T3 + T6 — MemoryGate (cgroup v2 working set) and the holding area."""

from __future__ import annotations

import asyncio
import dataclasses
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import gate as gate_mod
import jobqueue
import pytest
import worker as worker_mod
from gate import MemoryGate
from scrape import ScrapeError


def _cgroup(
    tmp_path: Path, *, limit: str = "1000", current: int = 600, inactive: Optional[int] = 0
) -> Path:
    (tmp_path / "memory.max").write_text(f"{limit}\n")
    (tmp_path / "memory.current").write_text(f"{current}\n")
    stat = "anon 1\nfile 2\n" + (f"inactive_file {inactive}\n" if inactive is not None else "")
    (tmp_path / "memory.stat").write_text(stat)
    return tmp_path


def _gate(path: Path, *, cutoff: float = 70, interval: float = 0.0) -> MemoryGate:
    return MemoryGate(cutoff, interval, cgroup_dir=str(path))


class TestMemoryGate:
    def test_admits_below_cutoff_and_refuses_at_it(self, tmp_path: Path) -> None:
        g = _gate(_cgroup(tmp_path, current=699))
        assert g.admit(running=3) is True
        (tmp_path / "memory.current").write_text("700\n")  # exactly 70%
        assert g.admit(running=3) is False

    def test_working_set_subtracts_inactive_file_page_cache(self, tmp_path: Path) -> None:
        g = _gate(_cgroup(tmp_path, current=900, inactive=400))  # 50% working set
        assert g.used_percent() == 50
        assert g.admit(running=3) is True

    def test_nothing_running_always_admits_one(self, tmp_path: Path) -> None:
        g = _gate(_cgroup(tmp_path, current=990))
        assert g.admit(running=0) is True
        assert g.admit(running=1) is False

    def test_admissions_are_paced_by_the_interval(self, tmp_path: Path) -> None:
        g = _gate(_cgroup(tmp_path, current=100), interval=60.0)
        assert g.admit(running=1) is True
        assert g.admit(running=1) is False  # too soon after the last one

    def test_limit_is_read_live_on_every_admit(self, tmp_path: Path) -> None:
        g = _gate(_cgroup(tmp_path, current=800))
        assert g.admit(running=3) is False
        (tmp_path / "memory.max").write_text("2000\n")  # Railway scaled the container up
        assert g.admit(running=3) is True

    @pytest.mark.parametrize(
        "kwargs",
        [{"limit": "max"}, {"inactive": None}],
        ids=["no-container-limit", "no-inactive-file"],
    )
    def test_unreadable_memory_fails_loud_at_startup(self, tmp_path: Path, kwargs: dict) -> None:
        with pytest.raises(RuntimeError, match="cgroup v2 memory not readable"):
            _gate(_cgroup(tmp_path, **kwargs))

    def test_missing_cgroup_fails_loud_at_startup(self, tmp_path: Path) -> None:
        with pytest.raises(RuntimeError, match="cgroup v2 memory not readable"):
            _gate(tmp_path / "nope")


# ---------------------------------------------------------------------------
# Holding area (worker) — in-memory queue, scrape faked
# ---------------------------------------------------------------------------


class _Store:
    """claim / start / heartbeat / release_all semantics of jobqueue, without Postgres."""

    def __init__(self) -> None:
        self.rows: Dict[str, dict] = {}
        self.heartbeats: list = []
        self.fails: list = []

    def insert(self, n: int, *, max_attempts: int = 4) -> str:
        jid = f"00000000-0000-0000-0000-{n:012d}"
        self.rows[jid] = {
            "n": n,
            "status": "queued",
            "attempts": 0,
            "max_attempts": max_attempts,
            "worker": None,
            "started": False,
        }
        return jid

    async def claim(self, _p: Any, *, limit: Optional[int], worker_id: str, lease_seconds: int):
        out = []
        for jid, r in self.rows.items():
            if r["status"] == "queued" and (limit is None or len(out) < limit):
                r.update(status="running", worker=worker_id, started=False)  # no charge
                out.append(
                    jobqueue.ClaimedJob(
                        id=jid,
                        request={"url": f"https://x/{r['n']}"},
                        attempts=r["attempts"],
                        max_attempts=r["max_attempts"],
                    )
                )
        return out

    async def start(self, _p: Any, *, job_id: str, worker_id: str) -> Optional[int]:
        r = self.rows.get(job_id)
        if not r or r["status"] != "running" or r["worker"] != worker_id:
            return None
        r["attempts"] += 1
        r["started"] = True
        return r["attempts"]

    async def complete(self, _p: Any, *, job_id: str, worker_id: str, result: Any) -> bool:
        self.rows[job_id]["status"] = "done"
        return True

    async def fail(self, _p: Any, *, job_id: str, worker_id: str, error: str, error_class: str,
                   retry_in_seconds: Optional[float]):
        self.fails.append((job_id, error_class, retry_in_seconds))
        self.rows[job_id]["status"] = "failed" if retry_in_seconds is None else "queued"
        return self.rows[job_id]["status"]

    async def heartbeat(self, _p: Any, *, worker_id: str, job_ids: Any, lease_seconds: int,
                        held: int, running: int) -> set:
        self.heartbeats.append((list(job_ids), held, running))
        return {j for j in job_ids if self.rows[j]["status"] == "running"}

    async def release_all(self, _p: Any, *, worker_id: str) -> int:
        n = 0
        for r in self.rows.values():
            if r["status"] == "running" and r["worker"] == worker_id:
                r["attempts"] = max(r["attempts"] - int(r["started"]), 0)
                r.update(status="queued", worker=None, started=False)
                n += 1
        return n


class _Gate:
    def __init__(self, limit: Optional[int] = None) -> None:
        self.limit = limit

    def admit(self, running: int) -> bool:
        return self.limit is None or running < self.limit


async def _until(pred, timeout: float = 2.0) -> None:
    loop = asyncio.get_running_loop()
    end = loop.time() + timeout
    while not pred():
        assert loop.time() < end, "condition not reached"
        await asyncio.sleep(0.01)


@pytest.fixture
def holding(monkeypatch: pytest.MonkeyPatch):
    store = _Store()
    for name in ("claim", "start", "complete", "fail", "heartbeat", "release_all"):
        monkeypatch.setattr(jobqueue, name, getattr(store, name))
    monkeypatch.setattr(
        worker_mod,
        "settings",
        dataclasses.replace(worker_mod.settings, shutdown_grace_seconds=0.05),
    )
    calls: list = []
    release: Dict[str, asyncio.Event] = {}
    fail_with: Dict[str, ScrapeError] = {}

    def _parse(raw: dict):
        return SimpleNamespace(fields=["text"], url=raw["url"]), None

    async def _run(_ff: Any, req: Any, _sel: Any) -> dict:
        calls.append(req.url)
        if req.url in fail_with:
            raise fail_with[req.url]
        await release.setdefault(req.url, asyncio.Event()).wait()
        return {"final_url": req.url}

    monkeypatch.setattr(worker_mod, "parse_request", _parse)
    monkeypatch.setattr(worker_mod, "run_scrape", _run)
    made: list = []

    def make_worker(gate: Optional[_Gate] = None):
        w = worker_mod.QueueWorker(MagicMock(), MagicMock(), worker_id="w-a", gate=gate)
        w._tasks = [
            asyncio.create_task(w._claim_loop()),
            asyncio.create_task(w._gate_loop()),
        ]
        made.append(w)
        return w

    yield store, make_worker, calls, release, fail_with
    for w in made:
        w._stopping.set()
        for t in [*w._tasks, *w._running.values()]:
            t.cancel()


class TestTelescopeHoldingArea:
    @pytest.mark.asyncio
    async def test_claims_all_and_holds_leased_until_the_gate_opens(self, holding) -> None:
        store, make_worker, calls, _release, _f = holding
        ids = [store.insert(n) for n in range(25)]  # old cap was 20
        gate = _Gate(limit=0)
        w = make_worker(gate)
        await _until(lambda: len(w._waiting) == 25)
        assert calls == []
        assert all(store.rows[i]["status"] == "running" for i in ids)  # leased
        assert all(store.rows[i]["attempts"] == 0 for i in ids)  # not charged
        gate.limit = None
        w._gate_wake.set()
        await _until(lambda: w.in_flight == 25)
        assert w.held == 25

    @pytest.mark.asyncio
    async def test_oldest_starts_first_and_a_finish_wakes_the_gate(self, holding) -> None:
        store, make_worker, calls, release, _f = holding
        ids = [store.insert(n) for n in range(3)]
        make_worker(_Gate(limit=1))
        await _until(lambda: calls == ["https://x/0"])
        for n in range(3):
            await _until(lambda n=n: f"https://x/{n}" in release)
            release[f"https://x/{n}"].set()
            await _until(lambda n=n: store.rows[ids[n]]["status"] == "done")
        assert calls == [f"https://x/{n}" for n in range(3)]

    @pytest.mark.asyncio
    async def test_heartbeat_covers_waiting_jobs_and_reports_held_vs_running(
        self, holding
    ) -> None:
        store, make_worker, calls, _release, _f = holding
        ids = [store.insert(n) for n in range(4)]
        w = make_worker(_Gate(limit=1))
        await _until(lambda: calls and len(w._waiting) == 3)
        w._tasks.append(asyncio.create_task(w._heartbeat_loop()))
        await _until(lambda: store.heartbeats)
        job_ids, held, running = store.heartbeats[0]
        assert sorted(job_ids) == sorted(ids) and (held, running) == (4, 1)

    @pytest.mark.asyncio
    async def test_stop_never_starts_waiting_jobs_and_refunds_only_started(
        self, holding
    ) -> None:
        store, make_worker, calls, _release, _f = holding
        ids = [store.insert(n) for n in range(3)]
        w = make_worker(_Gate(limit=1))
        await _until(lambda: len(calls) == 1 and len(w._waiting) == 2)
        await w.stop()
        assert len(calls) == 1
        assert all(
            (store.rows[i]["status"], store.rows[i]["attempts"]) == ("queued", 0) for i in ids
        )

    @pytest.mark.asyncio
    async def test_started_attempt_count_feeds_the_retry_decision(self, holding) -> None:
        store, make_worker, _calls, _release, fail_with = holding
        # max_attempts=1: the start charges attempt 1, so the failure is final (no retry).
        jid = store.insert(0, max_attempts=1)
        fail_with["https://x/0"] = ScrapeError("scrape_failed", "boom")
        make_worker(_Gate())
        await _until(lambda: store.fails)
        assert store.fails == [(jid, "scrape_failed", None)]

    @pytest.mark.asyncio
    async def test_gate_failure_keeps_jobs_held(self, holding) -> None:
        store, make_worker, calls, _release, _f = holding

        class _Broken:
            def admit(self, running: int) -> bool:
                raise OSError("cgroup gone")

        store.insert(0)
        w = make_worker(_Broken())
        await _until(lambda: len(w._waiting) == 1)
        assert calls == [] and w.held == 1


def test_default_gate_is_the_memory_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list = []
    monkeypatch.setattr(worker_mod, "MemoryGate", lambda *a: created.append(a) or MagicMock())
    worker_mod.QueueWorker(MagicMock(), MagicMock(), worker_id="w")
    assert created == [
        (worker_mod.settings.memory_cutoff_percent, worker_mod.settings.admit_interval_seconds)
    ]
    assert worker_mod.settings.memory_cutoff_percent == 70
    assert worker_mod.settings.admit_interval_seconds == 0.1
    assert not hasattr(worker_mod.settings, "worker_concurrency")
    assert gate_mod.MemoryGate is MemoryGate


class _SqlPool:
    def __init__(self) -> None:
        self.calls: list = []

    async def fetch(self, sql: str, *args: Any) -> list:
        self.calls.append((sql, args))
        return []

    async def fetchval(self, sql: str, *args: Any) -> Any:
        self.calls.append((sql, args))
        return 2

    async def execute(self, sql: str, *args: Any) -> str:
        self.calls.append((sql, args))
        return "DELETE 0"


class TestTelescopeQueueSql:
    @pytest.mark.asyncio
    async def test_claim_start_release_contract(self) -> None:
        pool = _SqlPool()
        await jobqueue.claim(pool, limit=None, worker_id="w", lease_seconds=60)
        claim_sql, claim_args = pool.calls[0]
        assert claim_args[0] is None and "started_at = NULL" in claim_sql
        assert "attempts" not in claim_sql.split("SET", 1)[1].split("FROM picked")[0]

        assert await jobqueue.start(pool, job_id="j", worker_id="w") == 2
        assert "attempts = attempts + 1, started_at = now()" in pool.calls[1][0]

        await jobqueue.release_all(pool, worker_id="w")
        assert "GREATEST(attempts - (started_at IS NOT NULL)::int, 0)" in pool.calls[2][0]
