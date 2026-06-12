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
