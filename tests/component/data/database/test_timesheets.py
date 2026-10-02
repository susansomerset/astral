"""Component tests for timesheets table cluster (AST-392)."""

from __future__ import annotations

import pytest

from src.data.database import backfill_agent_timesheet_costs
from src.utils.cost_calculator import (
    calculate_cost_components_from_counts,
)


# Branches: write row; list filters; sum by batch.
class TestAddTimesheetEntry:
    def test_writes_row(self, sqlite_in_memory) -> None:
        ok = sqlite_in_memory._add_timesheet_entry(
            "req-1",
            "task-uuid",
            "claude-sonnet-4-6",
            "cand-1",
            "batch-1",
            1,
            0,
            0,
            10,
            0,
            10,
            5,
            0.0,
            0.0,
            0.01,
            0.02,
        )
        assert ok is True


class TestListTimesheets:
    def test_filters_by_batch(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db._add_timesheet_entry(
            "req-1",
            "task-uuid",
            "claude-sonnet-4-6",
            "cand-1",
            "batch-1",
            1,
            0,
            0,
            10,
            0,
            10,
            5,
            0.0,
            0.0,
            0.01,
            0.02,
        )
        rows = db.list_timesheets(batch_id="batch-1")
        assert len(rows) == 1
        assert rows[0]["agent_req_id"] == "req-1"


class TestSumCostByBatch:
    def test_sums_cost_fields(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db._add_timesheet_entry(
            "req-1",
            "task-uuid",
            "claude-sonnet-4-6",
            "cand-1",
            "batch-1",
            1,
            0,
            0,
            10,
            0,
            10,
            5,
            0.0,
            0.0,
            0.01,
            0.02,
        )
        totals = db.sum_cost_by_batch(["batch-1"])
        assert totals["batch-1"] == pytest.approx(0.03)


class TestBackfillDeepseekAgentTimesheetCosts:
    def test_recomputes_deepseek_costs_leaves_anthropic_unchanged(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        expected = calculate_cost_components_from_counts(
            50, 100, 25, 0, sku="deepseek-v4-pro", server_id="deepseek"
        )
        db._add_timesheet_entry(
            "req-ds",
            "task-uuid",
            "deepseek-v4-pro",
            "cand-1",
            "batch-ds",
            1,
            0,
            50,
            0,
            0,
            100,
            25,
            9.0,
            9.0,
            9.0,
            9.0,
            provider="deepseek",
        )
        db._add_timesheet_entry(
            "req-anth",
            "task-uuid",
            "claude-sonnet-4-6",
            "cand-1",
            "batch-anth",
            1,
            0,
            0,
            10,
            0,
            10,
            5,
            0.0,
            0.0,
            0.01,
            0.02,
            provider="anthropic",
        )
        assert backfill_agent_timesheet_costs("deepseek") == 1
        rows = {r["agent_req_id"]: r for r in db.list_timesheets()}
        ds = rows["req-ds"]
        assert ds["calc_cost_cache_write"] == pytest.approx(expected["calc_cost_cache_write"])
        assert ds["calc_cost_cache_read"] == pytest.approx(expected["calc_cost_cache_read"])
        assert ds["calc_cost_no_cache_input"] == pytest.approx(
            expected["calc_cost_no_cache_input"]
        )
        assert ds["calc_cost_output"] == pytest.approx(expected["calc_cost_output"])
        anth = rows["req-anth"]
        assert anth["calc_cost_no_cache_input"] == pytest.approx(0.01)
        assert anth["calc_cost_output"] == pytest.approx(0.02)


class TestAst1878TimesheetCatalogValidation:
    """AST-1878: ledger rows must name a SKU the catalog prices on the row's server; backfill is per server."""

    @staticmethod
    def _row(db, req: str, sku: str, provider: str) -> bool:
        return db._add_timesheet_entry(
            req, "task-uuid", sku, "cand-1", "batch-x", 1, 0, 0, 0, 0, 10, 5, 0.0, 0.0, 0.0, 0.0,
            provider=provider,
        )

    def test_rejects_sku_not_priced_on_server(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Unknown SKU 'claude-sonnet-4-6'"):
            self._row(sqlite_in_memory, "req-bad", "claude-sonnet-4-6", "deepseek")
        with pytest.raises(ValueError, match="Unknown SKU"):
            self._row(sqlite_in_memory, "req-bad2", "__no_sku__", "anthropic")
        assert sqlite_in_memory.list_timesheets() == []

    def test_accepts_compat_server_sku(self, sqlite_in_memory) -> None:
        assert self._row(sqlite_in_memory, "req-kimi", "kimi-k2.6", "kimi") is True
        assert self._row(sqlite_in_memory, "req-or", "moonshotai/kimi-k2.6", "openrouter") is True

    def test_backfill_unknown_server_raises(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Unknown LLM server"):
            sqlite_in_memory.backfill_agent_timesheet_costs("__nope__")

    def test_backfill_scoped_to_server(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._row(db, "req-kimi", "kimi-k2.6", "kimi")
        self._row(db, "req-ds", "deepseek-v4-flash", "deepseek")
        assert db.backfill_agent_timesheet_costs("kimi") == 1
        rows = {r["agent_req_id"]: r for r in db.list_timesheets()}
        expected = calculate_cost_components_from_counts(0, 10, 5, 0, sku="kimi-k2.6", server_id="kimi")
        assert rows["req-kimi"]["calc_cost_output"] == pytest.approx(expected["calc_cost_output"])
        assert rows["req-ds"]["calc_cost_output"] == 0.0
        assert db.backfill_agent_timesheet_costs("openrouter") == 0
