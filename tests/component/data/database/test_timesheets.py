"""Component tests for timesheets table cluster (AST-392); platform columns + platform-first totals (AST-1965)."""

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
    """AST-1878: ledger rows must name a catalog server; backfill is per server. AST-1965 dropped the
    "SKU must be catalog-priced" half — an unpriced SKU now gets a row."""

    @staticmethod
    def _row(db, req: str, sku: str, provider: str) -> bool:
        return db._add_timesheet_entry(
            req, "task-uuid", sku, "cand-1", "batch-x", 1, 0, 0, 0, 0, 10, 5, 0.0, 0.0, 0.0, 0.0,
            provider=provider,
        )

    def test_accepts_unpriced_sku_server_check_stays(self, sqlite_in_memory) -> None:
        # AST-1965 AC 3 (database half), reverses AST-1878's rejection: a SKU not priced on the row's server,
        # or not priced anywhere, returns True and the row exists. An unknown server id still raises.
        db = sqlite_in_memory
        assert self._row(db, "req-unpriced", "claude-sonnet-4-6", "deepseek") is True
        assert self._row(db, "req-unknown", "__no_sku__", "openrouter") is True
        rows = {r["agent_req_id"]: r for r in db.list_timesheets()}
        assert set(rows) == {"req-unpriced", "req-unknown"}
        assert (rows["req-unknown"]["model_code"], rows["req-unknown"]["total_output_tokens"]) == ("__no_sku__", 5)
        with pytest.raises(ValueError, match="Invalid timesheet provider '__nope__'"):
            self._row(db, "req-bad-server", "kimi-k2.6", "__nope__")
        assert len(db.list_timesheets()) == 2

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


_PLATFORM_COLS = (
    "platform_cost", "native_tokens_prompt", "native_tokens_completion", "native_tokens_cached",
    "native_tokens_reasoning", "host", "platform_reconciled_at",
)
# A fully reconciled row's platform values (AST-1965 writer args after agent_req_id).
_STATS = (0.0123, 1200, 300, 400, 50, "DeepInfra")


def _ts_row(db, req: str, batch: str, calc=(0.0, 0.0, 0.0, 0.0), sku: str = "z-ai/glm-4.7", provider: str = "openrouter") -> None:
    # Distinct token counts so an overwrite of any original column is visible.
    assert db._add_timesheet_entry(req, "task-uuid", sku, "cand-1", batch, 2, 7, 11, 13, 17, 30, 19, *calc, provider=provider) is True


def _columns(db) -> list[str]:
    conn = db._get_connection()
    try:
        return [r[1] for r in conn.execute("PRAGMA table_info(agent_timesheets)").fetchall()]
    finally:
        conn.close()


class TestAst1965PlatformColumns:
    """AST-1965: nullable platform columns on agent_timesheets, update_timesheet_platform, platform-first totals.

    Branches: create path carries the columns; _ensure_timesheets_schema ALTER adds each missing column (old db)
    and skips present ones (idempotent); writer hit (rowcount 1) / miss (0); sum_cost_by_batch COALESCE —
    platform_cost when not NULL (0.0 included), else the calc_cost_* sum.
    """

    def test_new_table_appends_nullable_platform_columns(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _ts_row(db, "req-1", "b1")
        cols = _columns(db)
        # Appended after created_at, same order as a migrated table.
        assert cols[cols.index("created_at") + 1:] == list(_PLATFORM_COLS)
        row = db.list_timesheets()[0]
        assert {c: row[c] for c in _PLATFORM_COLS} == dict.fromkeys(_PLATFORM_COLS)

    def test_existing_table_gains_columns_and_keeps_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _ts_row(db, "req-old", "b1", calc=(0.1, 0.2, 0.3, 0.4))
        before = db.list_timesheets()[0]
        # Pre-AST-1965 shape: same table without the platform columns.
        conn = db._get_connection()
        try:
            for c in _PLATFORM_COLS:
                conn.execute(f"ALTER TABLE agent_timesheets DROP COLUMN {c}")
            conn.commit()
        finally:
            conn.close()
        assert not set(_PLATFORM_COLS) & set(_columns(db))
        db._timesheets_schema_ensured = False
        row = db.list_timesheets()[0]  # runs _ensure_timesheets_schema
        assert _columns(db)[-len(_PLATFORM_COLS):] == list(_PLATFORM_COLS)
        assert row == before  # old row kept, platform columns NULL (unreconciled)
        # Second ensure on a migrated table adds nothing and doesn't raise.
        db._timesheets_schema_ensured = False
        db.list_timesheets()
        assert len(_columns(db)) == len(set(_columns(db)))

    def test_writer_sets_platform_columns_and_never_touches_originals(self, sqlite_in_memory) -> None:
        # AC 4 — calc_cost_* and original token columns equal what was inserted; platform columns equal what was written.
        db = sqlite_in_memory
        _ts_row(db, "req-1", "b1", calc=(0.001, 0.002, 0.003, 0.004))
        _ts_row(db, "req-2", "b1", calc=(0.1, 0.1, 0.1, 0.1))
        before = {r["agent_req_id"]: r for r in db.list_timesheets()}
        assert db.update_timesheet_platform("req-1", *_STATS) == 1
        after = {r["agent_req_id"]: r for r in db.list_timesheets()}
        r1 = after["req-1"]
        assert tuple(r1[c] for c in _PLATFORM_COLS[:-1]) == _STATS
        assert r1["platform_reconciled_at"]
        originals = lambda r: {k: v for k, v in r.items() if k not in _PLATFORM_COLS}  # noqa: E731
        assert originals(r1) == originals(before["req-1"])
        assert (r1["calc_cost_cache_write"], r1["calc_cost_cache_read"], r1["calc_cost_no_cache_input"], r1["calc_cost_output"]) == (0.001, 0.002, 0.003, 0.004)
        # Only the named row is written.
        assert after["req-2"] == before["req-2"]

    def test_writer_passes_missing_counts_as_null_and_misses_unknown_id(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _ts_row(db, "req-1", "b1")
        assert db.update_timesheet_platform("req-1", 0.5, None, None, None, None, None) == 1
        row = db.list_timesheets()[0]
        assert (row["platform_cost"], row["native_tokens_cached"], row["host"]) == (0.5, None, None)
        assert db.update_timesheet_platform("__no_such_req__", *_STATS) == 0
        assert db.list_timesheets()[0] == row

    def test_writer_error_rolls_back_and_raises(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        _ts_row(db, "req-1", "b1")

        def boom(_conn) -> None:
            raise RuntimeError("schema check failed")

        ensure = db._ensure_timesheets_schema
        monkeypatch.setattr(db, "_ensure_timesheets_schema", boom)
        with pytest.raises(RuntimeError, match="schema check failed"):
            db.update_timesheet_platform("req-1", *_STATS)
        # Restore only this patch — monkeypatch.undo() would also revert the fixture's DB_PATH.
        monkeypatch.setattr(db, "_ensure_timesheets_schema", ensure)
        assert db.list_timesheets()[0]["platform_cost"] is None

    def test_sum_prefers_platform_cost_per_row(self, sqlite_in_memory) -> None:
        # AC 5 — one reconciled row (calc 0.01, platform 0.03) + one not (calc 0.02) → 0.05.
        db = sqlite_in_memory
        _ts_row(db, "req-rec", "b1", calc=(0.0, 0.0, 0.004, 0.006))
        _ts_row(db, "req-calc", "b1", calc=(0.0, 0.0, 0.01, 0.01))
        _ts_row(db, "req-other", "b2", calc=(0.0, 0.0, 0.0, 0.07))
        db.update_timesheet_platform("req-rec", 0.03, 1, 1, 0, 0, "DeepInfra")
        totals = db.sum_cost_by_batch(["b1", "b2"])
        assert totals["b1"] == pytest.approx(0.05)
        assert totals["b2"] == pytest.approx(0.07)
        assert db.sum_cost_by_batch([]) == {}

    def test_sum_counts_platform_zero_as_zero(self, sqlite_in_memory) -> None:
        # NULL = not reconciled; a reconciled 0.0 (free call) is a platform cost, not a fallback to calc.
        db = sqlite_in_memory
        _ts_row(db, "req-free", "b1", calc=(0.0, 0.0, 0.01, 0.01))
        db.update_timesheet_platform("req-free", 0.0, 0, 0, 0, 0, "DeepInfra")
        assert db.sum_cost_by_batch(["b1"]) == {"b1": 0.0}

    def test_backfill_skips_unpriced_rows_and_platform_columns(self, sqlite_in_memory) -> None:
        # Boundary: backfill unchanged — an unpriced row (now insertable) is not repriced, and a reconciled
        # priced row keeps its platform columns while calc_cost_* is recomputed.
        db = sqlite_in_memory
        _ts_row(db, "req-unpriced", "b1", calc=(0.0, 0.0, 0.0, 0.0), sku="claude-sonnet-4-6", provider="deepseek")
        _ts_row(db, "req-priced", "b1", calc=(9.0, 9.0, 9.0, 9.0), sku="deepseek-v4-flash", provider="deepseek")
        db.update_timesheet_platform("req-priced", *_STATS)
        before = {r["agent_req_id"]: r for r in db.list_timesheets()}
        assert db.backfill_agent_timesheet_costs("deepseek") == 1
        after = {r["agent_req_id"]: r for r in db.list_timesheets()}
        assert after["req-unpriced"] == before["req-unpriced"]
        assert after["req-priced"]["calc_cost_output"] != 9.0
        assert {c: after["req-priced"][c] for c in _PLATFORM_COLS} == {c: before["req-priced"][c] for c in _PLATFORM_COLS}
