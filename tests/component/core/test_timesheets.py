"""Component tests for src/core/timesheets.py — fetch_timesheet runner (AST-2218); daemon reconcile retired."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from src.core import timesheets as timesheets_mod
from src.utils.config import TIMESHEET_RECEIPT_FIELDS, TIMESHEET_SEARCH_SERVER_ID


def _empty_receipt(*, completion_status: str, platform_cost: Optional[float] = None) -> Dict[str, Any]:
    row = {k: None for k in TIMESHEET_RECEIPT_FIELDS}
    row.update(
        native_tokens_prompt=0,
        native_tokens_completion=0,
        native_tokens_cached=0,
        cache_write_tokens=0,
        response_item_count=0,
        response_char_length=0,
        platform_cost=platform_cost,
        completion_status=completion_status,
    )
    return row


def _seed_ledger(db, batch_id: str, candidate_id: str, *, state: str = "NEW") -> None:
    assert db.save_dispatch_ledger(batch_id, "evaluate_jd", candidate_id, "2026-10-15 12:00:00") is True
    db.update_dispatch_ledger(
        batch_id,
        status="COMPLETED",
        completed_at="2026-10-15 12:05:00",
        total_processed=2,
        total_passed=2,
        total_failed=0,
        total_cost=0.02,
        timesheet_state=state,
    )


def _add_or_row(db, req: str, batch: str, *, calc=(0.0, 0.0, 0.01, 0.01), provider: str = "openrouter") -> None:
    assert db._add_timesheet_entry(
        req, "task-uuid", "z-ai/glm-4.7", "cand-1", batch, 1,
        0, 0, 0, 0, 10, 5, *calc, provider=provider,
        request_type="DISPATCH_AGENT",
    ) is True


class TestRecordTimesheetEntry:
    """AST-2218: insert only — no reconcile thread."""

    def test_delegates_to_database_add(self, monkeypatch: pytest.MonkeyPatch) -> None:
        add = MagicMock(return_value=True)
        monkeypatch.setattr(timesheets_mod, "_add_timesheet_entry", add)
        row = dict(agent_req_id="req-1", batch_id="batch-1", batch_size=1, provider="deepseek")
        timesheets_mod.record_timesheet_entry(**row)
        add.assert_called_once_with(**row)

    def test_insert_starts_no_thread(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC1 — no threading.Thread in the record path.
        import threading as threading_mod

        started: list = []
        real_thread = threading_mod.Thread

        class _SpyThread(real_thread):
            def start(self) -> None:  # type: ignore[override]
                started.append(self)
                raise AssertionError("record_timesheet_entry must not start a thread")

        monkeypatch.setattr(threading_mod, "Thread", _SpyThread)
        timesheets_mod.record_timesheet_entry(
            agent_req_id="gen-x", task_key_uuid="t", model_code="z-ai/glm-4.7",
            candidate_id="cand-1", batch_id="b1", batch_size=1,
            cache_write_tokens=0, cache_read_tokens=0, no_cache_prompt_tokens=0,
            no_cache_live_tokens=0, total_no_cache_input_tokens=10, total_output_tokens=5,
            calc_cost_cache_write=0.0, calc_cost_cache_read=0.0,
            calc_cost_no_cache_input=0.01, calc_cost_output=0.01, provider="openrouter",
        )
        assert started == []
        assert sqlite_in_memory.list_timesheets()[0]["agent_req_id"] == "gen-x"


class TestRecordSearchTimesheetEntry:
    def test_writes_dispatch_search_google_cse_row(self, sqlite_in_memory) -> None:
        timesheets_mod.record_search_timesheet_entry("cand-1", "batch-s", hit_count=7)
        row = sqlite_in_memory.list_timesheets()[0]
        assert row["provider"] == TIMESHEET_SEARCH_SERVER_ID
        assert row["request_type"] == "DISPATCH_SEARCH"
        assert row["response_item_count"] == 7
        assert row["total_output_tokens"] == 0


class TestAst2218RunFetchTimesheet:
    """Parent AC 6 / 7 / 10 — NEW→FETCHING→RECEIPTED/NEW; stub null cost; closed-ledger catch-up."""

    def test_ac6_walk_receipted_and_retry_not_ready(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        _seed_ledger(db, "batch-a", "cand-1")
        _seed_ledger(db, "batch-b", "cand-1")
        _seed_ledger(db, "batch-other", "cand-2")  # must never be claimed/looked up
        _add_or_row(db, "gen-a1", "batch-a")
        _add_or_row(db, "gen-a2", "batch-a")
        _add_or_row(db, "gen-b1", "batch-b")
        _add_or_row(db, "gen-other", "batch-other")

        seen_ids: list[list[str]] = []
        mid_states: list[Dict[str, str]] = []
        # Round 1: A ready, B not_ready. Round 2: B ready.
        scripts = [
            {
                "gen-a1": _empty_receipt(completion_status="success", platform_cost=0.05),
                "gen-a2": _empty_receipt(completion_status="success", platform_cost=0.06),
                "gen-b1": _empty_receipt(completion_status="not_ready"),
            },
            {
                "gen-b1": _empty_receipt(completion_status="success", platform_cost=0.07),
            },
        ]
        round_i = {"n": 0}

        def fake_get_receipt(ids: List[str], api_key: str) -> List[Dict[str, Any]]:
            seen_ids.append(list(ids))
            mid_states.append({
                "a": db.get_dispatch_ledger("batch-a")["timesheet_state"],
                "b": db.get_dispatch_ledger("batch-b")["timesheet_state"],
            })
            script = scripts[min(round_i["n"], len(scripts) - 1)]
            return [script[i] for i in ids]

        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {
            "candidate_api_keys": {"openrouter": "sk-or"},
        })
        monkeypatch.setattr(
            "src.external.openrouter.get_receipt", fake_get_receipt,
        )

        out1 = timesheets_mod.run_fetch_timesheet("cand-1")
        assert out1["total_processed"] == 3
        assert out1["total_passed"] == 2
        assert mid_states[0] == {"a": "FETCHING", "b": "FETCHING"}
        assert set(seen_ids[0]) == {"gen-a1", "gen-a2", "gen-b1"}
        assert "gen-other" not in seen_ids[0]
        assert db.get_dispatch_ledger("batch-a")["timesheet_state"] == "RECEIPTED"
        assert db.get_dispatch_ledger("batch-b")["timesheet_state"] == "NEW"
        assert db.list_timesheets(batch_id="batch-b")[0]["platform_cost"] is None
        assert db.get_dispatch_ledger("batch-other")["timesheet_state"] == "NEW"

        round_i["n"] = 1
        out2 = timesheets_mod.run_fetch_timesheet("cand-1")
        assert out2["total_processed"] == 1
        assert out2["total_passed"] == 1
        assert seen_ids[1] == ["gen-b1"]
        assert db.get_dispatch_ledger("batch-b")["timesheet_state"] == "RECEIPTED"
        assert db.list_timesheets(batch_id="batch-b")[0]["platform_cost"] == pytest.approx(0.07)

    def test_ac6_exception_releases_fetching_to_new(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        _seed_ledger(db, "batch-a", "cand-1")
        _seed_ledger(db, "batch-b", "cand-1")
        _add_or_row(db, "gen-a1", "batch-a")
        _add_or_row(db, "gen-b1", "batch-b")

        def boom(ids: List[str], api_key: str) -> List[Dict[str, Any]]:
            raise RuntimeError("network down")

        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {
            "candidate_api_keys": {"openrouter": "sk-or"},
        })
        monkeypatch.setattr("src.external.openrouter.get_receipt", boom)
        out = timesheets_mod.run_fetch_timesheet("cand-1")
        assert out["total_errors"] == 1
        assert db.get_dispatch_ledger("batch-a")["timesheet_state"] == "NEW"
        assert db.get_dispatch_ledger("batch-b")["timesheet_state"] == "NEW"

    def test_ac7_stub_null_cost_keeps_calc_openrouter_platform_wins(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Closed ledger: Anthropic calc 0.04 + stub null platform; OpenRouter platform 0.06 wins over calc.
        db = sqlite_in_memory
        _seed_ledger(db, "batch-mix", "cand-1")
        assert db._add_timesheet_entry(
            "anth-1", "task-uuid", "claude-sonnet-4-6", "cand-1", "batch-mix", 1,
            0, 0, 0, 0, 10, 5, 0.0, 0.0, 0.02, 0.02, provider="anthropic",
        ) is True
        _add_or_row(db, "gen-or", "batch-mix", calc=(0.0, 0.0, 0.01, 0.01))

        def receipts(ids: List[str], api_key: str) -> List[Dict[str, Any]]:
            out = []
            for i in ids:
                if i.startswith("anth"):
                    out.append(_empty_receipt(completion_status="stub", platform_cost=None))
                else:
                    out.append(_empty_receipt(completion_status="success", platform_cost=0.06))
            return out

        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {
            "candidate_api_keys": {"openrouter": "sk-or", "anthropic": "sk-ant"},
        })
        monkeypatch.setattr("src.external.openrouter.get_receipt", receipts)
        monkeypatch.setattr("src.external.anthropic.get_receipt", receipts)
        timesheets_mod.run_fetch_timesheet("cand-1")
        # 0.04 (anth calc) + 0.06 (or platform) = 0.10
        assert db.sum_cost_by_batch(["batch-mix"])["batch-mix"] == pytest.approx(0.10)
        assert db.get_dispatch_ledger("batch-mix")["timesheet_state"] == "RECEIPTED"

    def test_ac10_refresh_closed_ledger_totals(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Closed ledger total_processed=2, total_cost=0.02; one OR row receipted at 0.06 → total 0.06, entity 0.03.
        db = sqlite_in_memory
        _seed_ledger(db, "batch-catch", "cand-1")
        _add_or_row(db, "gen-1", "batch-catch", calc=(0.0, 0.0, 0.005, 0.005))

        def one_billed(ids: List[str], api_key: str) -> List[Dict[str, Any]]:
            return [_empty_receipt(completion_status="success", platform_cost=0.06)]

        monkeypatch.setattr(timesheets_mod, "get_candidate", lambda cid: {
            "candidate_api_keys": {"openrouter": "sk-or"},
        })
        monkeypatch.setattr("src.external.openrouter.get_receipt", one_billed)
        timesheets_mod.run_fetch_timesheet("cand-1")
        led = db.get_dispatch_ledger("batch-catch")
        assert led["timesheet_state"] == "RECEIPTED"
        assert led["total_cost"] == pytest.approx(0.06)
        assert led["entity_cost"] == pytest.approx(0.03)
