"""Component tests for src/core/timesheets.py (AST-393); background platform cost reconcile (AST-1966)."""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.core import timesheets as timesheets_mod
from src.utils.logging import log_batch_id


@pytest.fixture
def reconcile_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """AST-2008: TIMESHEET_RECONCILE_ENABLED ships False; the AST-1966 routing/thread branches run only when on."""
    monkeypatch.setattr(timesheets_mod, "TIMESHEET_RECONCILE_ENABLED", True, raising=False)


# AST-2008 Step 6: flag off → row inserted, then return before routing — no thread, no lookup.
class TestAst2008ReconcileSwitch:
    def test_flag_off_inserts_row_and_starts_no_thread(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        # Repro 6 — today an openrouter-routed row always spawns the reconcile thread.
        db = sqlite_in_memory
        thread, routing = MagicMock(), MagicMock(return_value="openrouter")
        monkeypatch.setattr(timesheets_mod, "TIMESHEET_RECONCILE_ENABLED", False, raising=False)
        monkeypatch.setattr(timesheets_mod.threading, "Thread", thread)
        monkeypatch.setattr(timesheets_mod, "get_model_routing", routing)
        timesheets_mod.record_timesheet_entry(**_row_kwargs("gen-x", "batch-1"))
        thread.assert_not_called()
        routing.assert_not_called()
        assert _row(db, "gen-x")["platform_cost"] is None


@pytest.mark.usefixtures("reconcile_on")
class TestRecordTimesheetEntry:
    def test_delegates_to_database_add(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1966: a row with a generation id must name a catalog model (routing lookup); direct → no reconcile.
        add = MagicMock(return_value=True)
        started = MagicMock()
        monkeypatch.setattr(timesheets_mod, "_add_timesheet_entry", add)
        monkeypatch.setattr(timesheets_mod, "reconcile_timesheet_platform", started)
        row = dict(agent_req_id="req-1", batch_id="batch-1", batch_size=1, model_code="deepseek-v4-pro", provider="deepseek")
        timesheets_mod.record_timesheet_entry(**row)
        add.assert_called_once_with(**row)
        started.assert_not_called()

    def test_row_without_generation_id_skips_routing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # No agent_req_id → nothing to look up, so no model is required (the pre-AST-1966 call shape).
        add = MagicMock(return_value=True)
        routing = MagicMock()
        monkeypatch.setattr(timesheets_mod, "_add_timesheet_entry", add)
        monkeypatch.setattr(timesheets_mod, "get_model_routing", routing)
        timesheets_mod.record_timesheet_entry(agent_req_id=None, batch_id="batch-1", batch_size=1)
        add.assert_called_once_with(agent_req_id=None, batch_id="batch-1", batch_size=1)
        routing.assert_not_called()


# ---------------------------------------------------------------------------
# AST-1966 background reconcile. Branches (record_timesheet_entry): no generation id → return; direct → return;
# openrouter → thread started; unknown (server, SKU) → ValueError after the insert. Branches
# (reconcile_timesheet_platform): no key → warn + stop; success on try N (waits base·2^(n-1)); all tries fail →
# one warning; success → platform write, then ledger: no batch / no ledger row / open / closed (processed > 0 or 0);
# any exception → one logger.exception, nothing raised.
# ---------------------------------------------------------------------------
_OR_SKU = "z-ai/glm-4.7"
_KEY = "sk-or-cand"
_CALC = (0.0, 0.0, 0.004, 0.006)  # calc_cost_* sum 0.01
_OK = {"success": True, "total_cost": 0.03, "native_tokens_prompt": 1200, "native_tokens_completion": 300,
       "native_tokens_cached": 400, "native_tokens_reasoning": 50, "provider_name": "DeepInfra"}
_NOT_READY = {"success": False, "error": "Generation stats not ready: no total_cost"}
_PLATFORM_COLS = ("platform_cost", "native_tokens_prompt", "native_tokens_completion", "native_tokens_cached",
                  "native_tokens_reasoning", "host", "platform_reconciled_at")


def _row_kwargs(req: str, batch: str | None, sku: str = _OR_SKU, provider: str = "openrouter", calc=_CALC) -> dict[str, Any]:
    return dict(
        agent_req_id=req, task_key_uuid="task-uuid", model_code=sku, candidate_id="cand-1", batch_id=batch,
        batch_size=1, cache_write_tokens=7, cache_read_tokens=11, no_cache_prompt_tokens=13, no_cache_live_tokens=17,
        total_no_cache_input_tokens=30, total_output_tokens=19, calc_cost_cache_write=calc[0],
        calc_cost_cache_read=calc[1], calc_cost_no_cache_input=calc[2], calc_cost_output=calc[3], provider=provider,
    )


def _row(db, req: str) -> dict[str, Any]:
    return next(r for r in db.list_timesheets() if r["agent_req_id"] == req)


class _Stats:
    """Stubbed lookup: answers from a script (last answer repeats), records (generation id, key) per call."""

    def __init__(self, *answers: Any) -> None:
        self.answers, self.calls = list(answers), []

    def __call__(self, generation_id: str, api_key: str) -> dict[str, Any]:
        self.calls.append((generation_id, api_key))
        ans = self.answers[min(len(self.calls), len(self.answers)) - 1]
        if isinstance(ans, Exception):
            raise ans
        return ans


@pytest.fixture
def keyed(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Candidate holds an OpenRouter key; sleep recorded, not slept. Returns the recorded waits."""
    waits: list[float] = []
    monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {"candidate_api_keys": {"openrouter": _KEY}})
    monkeypatch.setattr(timesheets_mod.time, "sleep", waits.append)
    return waits


@pytest.mark.usefixtures("reconcile_on")
class TestAst1966RecordNeverWaits:
    def test_openrouter_row_returns_before_blocked_lookup(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 4 — lookup blocked on a gate: record returns at once, row exists with NULL platform cost; the
        # background thread carries the caller's context (log_batch_id) and writes once the gate opens.
        db = sqlite_in_memory
        gate, seen = threading.Event(), {}
        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {"candidate_api_keys": {"openrouter": _KEY}})
        # Real sleep on the thread — skip the pre-lookup wait so the 5s poll below can see the write.
        monkeypatch.setattr(timesheets_mod, "TIMESHEET_RECONCILE_INITIAL_WAIT_SECONDS", 0)

        def blocked(generation_id: str, api_key: str) -> dict[str, Any]:
            seen.update(id=generation_id, key=api_key, batch=log_batch_id.get(), daemon=threading.current_thread().daemon)
            gate.wait(5)
            return _OK

        monkeypatch.setattr(timesheets_mod, "get_generation_stats", blocked)
        token = log_batch_id.set("batch-1")
        try:
            t0 = time.monotonic()
            timesheets_mod.record_timesheet_entry(**_row_kwargs("gen-1", "batch-1"))
            elapsed = time.monotonic() - t0
        finally:
            log_batch_id.reset(token)
        assert elapsed < 1.0
        assert _row(db, "gen-1")["platform_cost"] is None
        gate.set()
        deadline = time.monotonic() + 5
        while _row(db, "gen-1")["platform_cost"] is None and time.monotonic() < deadline:
            time.sleep(0.02)
        assert _row(db, "gen-1")["platform_cost"] == 0.03
        assert seen == {"id": "gen-1", "key": _KEY, "batch": "batch-1", "daemon": True}

    @pytest.mark.parametrize(("sku", "provider"), [("deepseek-v4-pro", "deepseek"), ("kimi-k2.6", "kimi"), ("claude-sonnet-4-6", "anthropic")])
    def test_direct_row_is_never_looked_up(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, sku: str, provider: str) -> None:
        # AC 4 — direct-routed rows: no thread, stub never called, row keeps calc cost.
        db = sqlite_in_memory
        stats, started = _Stats(_OK), MagicMock()
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", stats)
        monkeypatch.setattr(timesheets_mod, "reconcile_timesheet_platform", started)
        timesheets_mod.record_timesheet_entry(**_row_kwargs("gen-d", "batch-1", sku=sku, provider=provider))
        started.assert_not_called()
        assert stats.calls == []
        assert _row(db, "gen-d")["platform_cost"] is None

    def test_unknown_model_raises_after_insert_without_thread(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        # Plan: (server, SKU) not in the catalog = config drift → ValueError; the row is already written.
        # Callers in llm_compat / anthropic wrap record_timesheet, so the LLM call is unaffected.
        db = sqlite_in_memory
        started = MagicMock()
        monkeypatch.setattr(timesheets_mod, "reconcile_timesheet_platform", started)
        with pytest.raises(ValueError, match="No LLM model for server 'openrouter' and SKU '__unpriced__'"):
            timesheets_mod.record_timesheet_entry(**_row_kwargs("gen-u", "batch-1", sku="__unpriced__"))
        started.assert_not_called()
        assert _row(db, "gen-u")["model_code"] == "__unpriced__"


class TestAst1966RetryThenGiveUp:
    def test_not_ready_four_times_then_200(self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 5 — exactly 5 calls, waits double from the base, platform columns set, calc_cost_* unchanged.
        db = sqlite_in_memory
        db._add_timesheet_entry(**_row_kwargs("gen-1", "batch-1"))
        stats = _Stats(_NOT_READY, _NOT_READY, _NOT_READY, _NOT_READY, _OK)
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", stats)
        timesheets_mod.reconcile_timesheet_platform("gen-1", "openrouter", "cand-1", "batch-1")
        assert stats.calls == [("gen-1", _KEY)] * 5
        assert keyed == [2, 4, 8, 16]
        row = _row(db, "gen-1")
        assert (row["platform_cost"], row["native_tokens_prompt"], row["native_tokens_completion"], row["native_tokens_cached"],
                row["native_tokens_reasoning"], row["host"]) == (0.03, 1200, 300, 400, 50, "DeepInfra")
        assert row["platform_reconciled_at"]
        assert (row["calc_cost_cache_write"], row["calc_cost_cache_read"], row["calc_cost_no_cache_input"], row["calc_cost_output"]) == _CALC

    def test_fails_every_time_gives_up_with_one_warning(
        self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        # AC 5 — 5 calls, platform cost NULL, calc_cost_* unchanged, exactly one WARNING naming req id + batch id.
        db = sqlite_in_memory
        db._add_timesheet_entry(**_row_kwargs("gen-1", "batch-9"))
        before = _row(db, "gen-1")
        stats = _Stats({"success": False, "error": "Generation stats HTTP 404: not found"})
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", stats)
        with caplog.at_level(logging.WARNING, logger="src.core.timesheets"):
            timesheets_mod.reconcile_timesheet_platform("gen-1", "openrouter", "cand-1", "batch-9")
        assert len(stats.calls) == 5
        assert keyed == [2, 4, 8, 16]
        assert _row(db, "gen-1") == before
        warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1
        assert "gen-1" in warnings[0] and "batch-9" in warnings[0] and "5 tries" in warnings[0]
        assert not [r for r in caplog.records if r.levelno >= logging.ERROR]

    @pytest.mark.parametrize(("retries", "base", "waits"), [(3, 2.0, [2.0, 4.0]), (4, 0.5, [0.5, 1.0, 2.0]), (1, 2.0, [])])
    def test_count_and_base_come_from_config(
        self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch, retries: int, base: float, waits: list[float]
    ) -> None:
        sqlite_in_memory._add_timesheet_entry(**_row_kwargs("gen-1", "batch-1"))
        stats = _Stats(_NOT_READY)
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", stats)
        monkeypatch.setattr(timesheets_mod, "TIMESHEET_RECONCILE_RETRIES", retries)
        monkeypatch.setattr(timesheets_mod, "TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS", base)
        timesheets_mod.reconcile_timesheet_platform("gen-1", "openrouter", "cand-1", "batch-1")
        assert len(stats.calls) == retries
        assert keyed == waits

    @pytest.mark.parametrize("cand", [None, {}, {"candidate_api_keys": None}, {"candidate_api_keys": {"kimi": "sk-k"}}, {"candidate_api_keys": {"openrouter": ""}}])
    def test_no_key_warns_once_and_never_looks_up(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, cand: Any
    ) -> None:
        db = sqlite_in_memory
        db._add_timesheet_entry(**_row_kwargs("gen-1", "batch-1"))
        stats = _Stats(_OK)
        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: cand)
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", stats)
        with caplog.at_level(logging.WARNING, logger="src.core.timesheets"):
            timesheets_mod.reconcile_timesheet_platform("gen-1", "openrouter", "cand-1", "batch-1")
        assert stats.calls == []
        warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warnings) == 1 and "gen-1" in warnings[0] and "no API key" in warnings[0]
        assert _row(db, "gen-1")["platform_cost"] is None

    def test_exception_logged_once_never_raised(
        self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        db = sqlite_in_memory
        db._add_timesheet_entry(**_row_kwargs("gen-1", "batch-1"))
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", _Stats(RuntimeError("socket closed")))
        with caplog.at_level(logging.WARNING, logger="src.core.timesheets"):
            timesheets_mod.reconcile_timesheet_platform("gen-1", "openrouter", "cand-1", "batch-1")
        errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(errors) == 1 and errors[0].exc_info
        assert "gen-1" in errors[0].getMessage() and "socket closed" in errors[0].getMessage()
        assert _row(db, "gen-1")["platform_cost"] is None


class TestAst1966ClosedLedgerRefresh:
    @staticmethod
    def _ledger(db, batch: str, completed: bool, processed: int, total: float) -> None:
        db.save_dispatch_ledger(batch, "task_x", "cand-1", "2026-10-04T00:00:00")
        fields = dict(total_processed=processed, total_cost=total, entity_cost=total / processed if processed else total)
        if completed:
            fields["completed_at"] = "2026-10-04T00:01:00"
        db.update_dispatch_ledger(batch, **fields)

    def _reconcile(self, db, monkeypatch: pytest.MonkeyPatch, batch: str | None, cost: float = 0.06) -> None:
        db._add_timesheet_entry(**_row_kwargs("gen-1", batch, calc=(0.0, 0.0, 0.01, 0.01)))
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", _Stats({**_OK, "total_cost": cost}))
        timesheets_mod.reconcile_timesheet_platform("gen-1", "openrouter", "cand-1", batch)

    def test_closed_row_is_retotalled(self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 6 — closed, processed 2, total 0.02 → platform 0.06 → total 0.06, entity 0.03.
        db = sqlite_in_memory
        self._ledger(db, "batch-1", completed=True, processed=2, total=0.02)
        self._reconcile(db, monkeypatch, "batch-1")
        led = db.get_dispatch_ledger("batch-1")
        assert led["total_cost"] == pytest.approx(0.06)
        assert led["entity_cost"] == pytest.approx(0.03)

    def test_closed_row_with_zero_processed_takes_total_as_entity_cost(
        self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Same rule as the dispatcher's batch close: nothing processed → entity cost = total.
        db = sqlite_in_memory
        self._ledger(db, "batch-1", completed=True, processed=0, total=0.02)
        self._reconcile(db, monkeypatch, "batch-1")
        led = db.get_dispatch_ledger("batch-1")
        assert (led["total_cost"], led["entity_cost"]) == (pytest.approx(0.06), pytest.approx(0.06))

    def test_open_row_untouched(self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 6 — completed_at NULL → ledger row unchanged (the batch-close write totals it); platform row still written.
        db = sqlite_in_memory
        self._ledger(db, "batch-1", completed=False, processed=2, total=0.02)
        before = db.get_dispatch_ledger("batch-1")
        self._reconcile(db, monkeypatch, "batch-1")
        assert db.get_dispatch_ledger("batch-1") == before
        assert _row(db, "gen-1")["platform_cost"] == 0.06

    def test_no_batch_or_no_ledger_row_writes_platform_only(
        self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        get_ledger = MagicMock(return_value=None)
        monkeypatch.setattr(timesheets_mod, "get_dispatch_ledger", get_ledger)
        self._reconcile(db, monkeypatch, None)
        get_ledger.assert_not_called()
        assert _row(db, "gen-1")["platform_cost"] == 0.06
        # Batch id with no ledger row: looked up, nothing to refresh, no raise.
        monkeypatch.setattr(timesheets_mod, "get_dispatch_ledger", db.get_dispatch_ledger)
        db._add_timesheet_entry(**_row_kwargs("gen-2", "batch-none"))
        monkeypatch.setattr(timesheets_mod, "get_generation_stats", _Stats(_OK))
        timesheets_mod.reconcile_timesheet_platform("gen-2", "openrouter", "cand-1", "batch-none")
        assert _row(db, "gen-2")["platform_cost"] == 0.03
        assert db.get_dispatch_ledger("batch-none") is None

    def test_rerun_is_idempotent(self, sqlite_in_memory, keyed: list[float], monkeypatch: pytest.MonkeyPatch) -> None:
        # Recomputed from the table each time — a second reconcile of the same row leaves the same totals.
        db = sqlite_in_memory
        self._ledger(db, "batch-1", completed=True, processed=2, total=0.02)
        self._reconcile(db, monkeypatch, "batch-1")
        timesheets_mod.reconcile_timesheet_platform("gen-1", "openrouter", "cand-1", "batch-1")
        led = db.get_dispatch_ledger("batch-1")
        assert (led["total_cost"], led["entity_cost"]) == (pytest.approx(0.06), pytest.approx(0.03))


_GEN_RECORD = {
    "id": "gen-1",
    "total_cost": 0.04,
    "provider_name": "DeepInfra",
    "native_tokens_prompt": 100,
    "native_tokens_completion": 50,
    "native_tokens_cached": 0,
    "native_tokens_reasoning": 10,
    "provider_responses": [{"provider_name": "DeepInfra", "status": 200}],
}


class TestBatchOpenrouterPlatformReconcile:
    def test_start_skips_without_pending_gen_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        thread = MagicMock()
        monkeypatch.setattr(timesheets_mod, "count_pending_gen_platform_timesheets", lambda: 0)
        monkeypatch.setattr(timesheets_mod.threading, "Thread", thread)
        timesheets_mod.start_batch_openrouter_platform_reconcile("batch-1")
        thread.assert_not_called()

    def test_batch_pass_fills_cost_host_and_metadata(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        db = sqlite_in_memory
        db._add_timesheet_entry(**_row_kwargs("gen-1", "batch-x"))
        monkeypatch.setattr(timesheets_mod, "TIMESHEET_BATCH_RECONCILE_PING_AT_SECONDS", (0,))
        monkeypatch.setattr(timesheets_mod, "_sleep_until", lambda _d: None)
        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {"candidate_api_keys": {"openrouter": _KEY}})
        monkeypatch.setattr(
            timesheets_mod,
            "get_generation_record",
            lambda gid, key: {"success": True, "data": {**_GEN_RECORD, "id": gid}},
        )
        with caplog.at_level(logging.WARNING, logger="src.core.timesheets"):
            timesheets_mod.reconcile_pending_gen_platform()
        row = _row(db, "gen-1")
        assert row["platform_cost"] == 0.04
        assert row["host"] == "DeepInfra"
        meta = json.loads(row["platform_metadata"])
        assert meta["provider_responses"][0]["provider_name"] == "DeepInfra"
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]

    def test_not_ready_api_leaves_row_unchanged_without_warning(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        db = sqlite_in_memory
        db._add_timesheet_entry(**_row_kwargs("gen-1", "batch-x"))
        before = _row(db, "gen-1")
        monkeypatch.setattr(timesheets_mod, "TIMESHEET_BATCH_RECONCILE_PING_AT_SECONDS", (0,))
        monkeypatch.setattr(timesheets_mod, "_sleep_until", lambda _d: None)
        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {"candidate_api_keys": {"openrouter": _KEY}})
        monkeypatch.setattr(timesheets_mod, "get_generation_record", lambda gid, key: _NOT_READY)
        with caplog.at_level(logging.WARNING, logger="src.core.timesheets"):
            timesheets_mod.reconcile_pending_gen_platform()
        assert _row(db, "gen-1") == before
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
