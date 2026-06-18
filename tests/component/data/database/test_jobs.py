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


# Branches: partial unique index lazy migration; insert identity bounce; NULL triple outside index.
class TestAst732JobIdentityUniqueIndex:
    def test_ensure_job_schema_creates_partial_unique_index(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-idx", company="acme", state="NEW", job_title="Eng", company_job_id="x1")
        conn = db._get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='index' AND name='idx_job_identity_unique'"
            ).fetchone()
            assert row is not None
            sql_row = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_job_identity_unique'"
            ).fetchone()
            assert sql_row is not None
            sql = (sql_row[0] or "").upper()
            assert "UNIQUE" in sql and "COMPANY_JOB_ID IS NOT NULL" in sql
        finally:
            conn.close()

    def test_index_ensure_idempotent_on_second_open(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-a", company="acme", state="NEW", job_title="A", company_job_id="id-a")
        conn = db._get_connection()
        try:
            db._ensure_job_schema(conn)
            db._ensure_job_schema(conn)
            count = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name='idx_job_identity_unique'"
            ).fetchone()[0]
            assert count == 1
        finally:
            conn.close()


class TestAst732SaveJobDuplicateBounce:
    def test_insert_duplicate_complete_triple_returns_false(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        assert db.save_job(
            "job-1", company="acme", state="NEW", job_title="Engineer", company_job_id="123"
        ) is True
        assert db.save_job(
            "job-2", company="acme", state="NEW", job_title="Engineer", company_job_id="123"
        ) is False
        assert db.get_job("job-2") is None
        assert db.get_job("job-1") is not None

    def test_incomplete_identity_allows_multiple_inserts(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        assert db.save_job("job-1", company="acme", state="NEW", job_title="Same") is True
        assert db.save_job("job-2", company="acme", state="NEW", job_title="Same") is True

    def test_update_existing_row_still_returns_true(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-1", company="acme", state="NEW", job_title="Eng", company_job_id="99")
        assert db.save_job("job-1", state="RECOMMENDED") is True
        row = db.get_job("job-1")
        assert row is not None
        assert row["state"] == "RECOMMENDED"
