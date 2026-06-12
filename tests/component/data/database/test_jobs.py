"""Component tests for job table cluster (AST-392)."""

from __future__ import annotations

import pytest


# Branches: insert requires company/state; merge vs overwrite; read path.
class TestSaveJob:
    def test_insert_requires_company_and_state(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="company required"):
            sqlite_in_memory.save_job("job-1", state="NEW")
        with pytest.raises(ValueError, match="state required"):
            sqlite_in_memory.save_job("job-1", company="acme")

    def test_insert_and_merge_update(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-1", company="acme", state="NEW", job_data={"title": "a"})
        db.save_job("job-1", job_data={"grade": 8}, merge=True)
        row = db.get_job("job-1")
        assert row is not None
        assert row["job_data"]["title"] == "a"
        assert row["job_data"]["grade"] == 8

    def test_overwrite_job_data(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-1", company="acme", state="NEW", job_data={"title": "a"})
        db.save_job("job-1", job_data={"title": "only"}, merge=False)
        row = db.get_job("job-1")
        assert row is not None
        assert row["job_data"] == {"title": "only"}


class TestGetJob:
    def test_returns_none_when_missing(self, sqlite_in_memory) -> None:
        assert sqlite_in_memory.get_job("missing") is None


class TestRawJobListingIsDuplicate:
    def test_detects_existing_listing(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-1", company="acme", state="NEW", company_job_id="abc123")
        assert db.raw_job_listing_is_duplicate("acme", "prefix-abc123-suffix") is True
        assert db.raw_job_listing_is_duplicate("acme", "no-match") is False
