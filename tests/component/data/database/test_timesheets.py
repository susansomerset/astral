"""Component tests for timesheets table cluster (AST-392)."""

from __future__ import annotations

import pytest

from src.data.database import backfill_deepseek_agent_timesheet_costs
from src.utils.cost_calculator import calculate_cost_components_deepseek_from_counts


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
        expected = calculate_cost_components_deepseek_from_counts(
            50, 100, 25, 0, "deepseek-v4-pro"
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
        assert backfill_deepseek_agent_timesheet_costs() == 1
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
