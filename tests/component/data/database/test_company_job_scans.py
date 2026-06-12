"""Component tests for company_job_scan table cluster (AST-392)."""

from __future__ import annotations

import pytest


class TestRecordToCompanyJobScan:
    def test_rejects_invalid_status(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="status must be"):
            sqlite_in_memory.record_to_company_job_scan("batch-1", "acme", "2026-05-13 12:00:00", status="bad")

    def test_records_success_scan(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.record_to_company_job_scan("batch-1", "acme", "2026-05-13 12:00:00", total_found=2, new=1)
        rows = db.list_company_job_scans()
        assert len(rows) == 1
        assert rows[0]["short_name"] == "acme"
