"""Component tests for dispatch_ledger table cluster (AST-392)."""

from __future__ import annotations

import pytest


class TestSaveDispatchLedger:
    def test_inserts_running_row(self, seeded_db) -> None:
        db = seeded_db
        ok = db.save_dispatch_ledger("batch-1", "qualify_job_listings", "cand-1", "2026-05-13 12:00:00")
        assert ok is True
        row = db.get_dispatch_ledger("batch-1")
        assert row is not None
        assert row["status"] == "RUNNING"

    def test_duplicate_batch_returns_false(self, seeded_db) -> None:
        db = seeded_db
        assert db.save_dispatch_ledger("batch-1", "qualify_job_listings", "cand-1", "2026-05-13 12:00:00") is True
        assert db.save_dispatch_ledger("batch-1", "qualify_job_listings", "cand-1", "2026-05-13 12:00:01") is False


class TestUpdateDispatchLedger:
    def test_rejects_unknown_columns(self, seeded_db) -> None:
        db = seeded_db
        db.save_dispatch_ledger("batch-1", "qualify_job_listings", "cand-1", "2026-05-13 12:00:00")
        with pytest.raises(ValueError, match="Invalid dispatch_ledger columns"):
            db.update_dispatch_ledger("batch-1", not_a_column="x")

    def test_updates_allowed_columns(self, seeded_db) -> None:
        db = seeded_db
        db.save_dispatch_ledger("batch-1", "qualify_job_listings", "cand-1", "2026-05-13 12:00:00")
        db.update_dispatch_ledger("batch-1", status="DONE", total_processed=3)
        row = db.get_dispatch_ledger("batch-1")
        assert row is not None
        assert row["status"] == "DONE"
        assert row["total_processed"] == 3


# AST-1960: `host` column (served LLM host). Branches: fresh CREATE carries it; pre-existing table without it
# gets the ALTER (old rows NULL, no backfill — AST-1497); update accepts it; both readers return it.
class TestAst1960LedgerHostColumn:
    def test_fresh_table_has_host_and_update_round_trips_through_readers(self, seeded_db) -> None:
        db = seeded_db
        db.save_dispatch_ledger("batch-1", "anticipate_scan", "cand-1", "2026-10-04 00:00:00")
        assert db.get_dispatch_ledger("batch-1")["host"] is None
        db.update_dispatch_ledger("batch-1", host="DeepInfra")
        assert db.get_dispatch_ledger("batch-1")["host"] == "DeepInfra"
        assert [r["host"] for r in db.list_dispatch_ledger() if r["batch_id"] == "batch-1"] == ["DeepInfra"]

    def test_legacy_table_gains_host_and_old_rows_stay_null(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            # Pre-AST-1960 shape: every column except host.
            conn.execute(
                "CREATE TABLE dispatch_ledger (batch_id TEXT PRIMARY KEY, task_key TEXT, candidate_id TEXT, "
                "entity_type TEXT, batch_size INTEGER, started_at TIMESTAMP, completed_at TIMESTAMP, status TEXT, "
                "total_processed INTEGER DEFAULT 0, total_passed INTEGER DEFAULT 0, total_failed INTEGER DEFAULT 0, "
                "total_errors INTEGER DEFAULT 0, agent_performance TEXT, agent_note TEXT, "
                "total_cost REAL DEFAULT 0.0, entity_cost REAL DEFAULT 0.0, prompt_blocks TEXT)"
            )
            conn.execute("INSERT INTO dispatch_ledger (batch_id, status) VALUES ('old-batch', 'COMPLETED')")
            conn.commit()
        finally:
            conn.close()
        db.save_dispatch_ledger("new-batch", "anticipate_scan", "cand-1", "2026-10-04 00:00:00")
        db.update_dispatch_ledger("new-batch", host="Anthropic")
        assert db.get_dispatch_ledger("old-batch")["host"] is None
        assert db.get_dispatch_ledger("new-batch")["host"] == "Anthropic"


# AST-2008 Step 4: llm_call_seconds REAL + llm_failure_class TEXT. Branches: fresh CREATE carries both;
# pre-existing (AST-1960 shape) table gets the ALTERs, old rows NULL; update allowlist accepts both.
class TestAst2008LedgerCallOutcomeColumns:
    def test_fresh_table_has_both_and_update_round_trips(self, seeded_db) -> None:
        db = seeded_db
        db.save_dispatch_ledger("batch-1", "meteorite_grade_do", "cand-1", "2026-10-06 00:00:00")
        row = db.get_dispatch_ledger("batch-1")
        assert "llm_call_seconds" in row and row["llm_call_seconds"] is None
        assert "llm_failure_class" in row and row["llm_failure_class"] is None
        db.update_dispatch_ledger("batch-1", llm_call_seconds=613.9, llm_failure_class="provider_call_timeout")
        row = db.get_dispatch_ledger("batch-1")
        assert (row["llm_call_seconds"], row["llm_failure_class"]) == (613.9, "provider_call_timeout")
        listed = next(r for r in db.list_dispatch_ledger() if r["batch_id"] == "batch-1")
        assert listed["llm_failure_class"] == "provider_call_timeout"

    def test_legacy_table_gains_both_and_old_rows_stay_null(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            # Pre-AST-2008 shape: AST-1960 columns, host included, no call-outcome columns.
            conn.execute(
                "CREATE TABLE dispatch_ledger (batch_id TEXT PRIMARY KEY, task_key TEXT, candidate_id TEXT, "
                "entity_type TEXT, batch_size INTEGER, started_at TIMESTAMP, completed_at TIMESTAMP, status TEXT, "
                "total_processed INTEGER DEFAULT 0, total_passed INTEGER DEFAULT 0, total_failed INTEGER DEFAULT 0, "
                "total_errors INTEGER DEFAULT 0, agent_performance TEXT, agent_note TEXT, "
                "total_cost REAL DEFAULT 0.0, entity_cost REAL DEFAULT 0.0, prompt_blocks TEXT, host TEXT)"
            )
            conn.execute("INSERT INTO dispatch_ledger (batch_id, status) VALUES ('old-batch', 'COMPLETED')")
            conn.commit()
        finally:
            conn.close()
        db.save_dispatch_ledger("new-batch", "meteorite_grade_do", "cand-1", "2026-10-06 00:00:00")
        db.update_dispatch_ledger("new-batch", llm_call_seconds=1.5, llm_failure_class=None)
        old = db.get_dispatch_ledger("old-batch")
        assert (old.get("llm_call_seconds", "missing"), old.get("llm_failure_class", "missing")) == (None, None)
        assert db.get_dispatch_ledger("new-batch")["llm_call_seconds"] == 1.5
