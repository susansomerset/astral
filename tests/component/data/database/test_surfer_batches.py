"""Component tests for surfer_batch table helpers (AST-1229)."""

from __future__ import annotations

import pytest

from src.utils.config import SURFER_BATCH_CONFIG


# Branches: insert/get round-trip; duplicate PK False; list order; update fields;
# missing/empty update raises; upsert registry registration.
class TestAst1229SurferBatchData:
    def test_insert_get_list_and_duplicate(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        urls = [
            {
                "url": "https://example.com/a",
                "outcome": SURFER_BATCH_CONFIG["initial_url_outcome"],
                "updated_at": None,
            }
        ]
        assert (
            db.insert_surfer_batch(
                "surfer-t1",
                "cand-1",
                SURFER_BATCH_CONFIG["initial_status"],
                "2026-08-07 01:00:00",
                urls,
                [],
            )
            is True
        )
        row = db.get_surfer_batch("surfer-t1")
        assert row is not None
        assert row["candidate_id"] == "cand-1"
        assert row["status"] == SURFER_BATCH_CONFIG["initial_status"]
        assert row["started_at"] == "2026-08-07 01:00:00"
        assert row["urls"] == urls
        assert row["job_ids"] == []
        assert db.insert_surfer_batch(
            "surfer-t1",
            "cand-1",
            SURFER_BATCH_CONFIG["initial_status"],
            "2026-08-07 01:00:00",
            urls,
            [],
        ) is False
        assert db.get_surfer_batch("missing") is None

        assert (
            db.insert_surfer_batch(
                "surfer-t0",
                "cand-1",
                SURFER_BATCH_CONFIG["initial_status"],
                "2026-08-07 00:30:00",
                urls,
                ["job-a"],
            )
            is True
        )
        listed = db.list_surfer_batches_for_candidate("cand-1")
        assert [r["batch_id"] for r in listed] == ["surfer-t1", "surfer-t0"]
        assert listed[1]["job_ids"] == ["job-a"]

    def test_update_status_urls_job_ids_and_errors(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.insert_surfer_batch(
            "surfer-u1",
            "cand-u",
            "RUNNING",
            "2026-08-07 02:00:00",
            [{"url": "https://ex.com/1", "outcome": "pending", "updated_at": None}],
            [],
        )
        before = db.get_surfer_batch("surfer-u1")
        assert before is not None
        db.update_surfer_batch(
            "surfer-u1",
            status="CANCELLED",
            urls=[{"url": "https://ex.com/1", "outcome": "failed", "updated_at": "2026-08-07 02:01:00"}],
            job_ids=["job-1", "job-2"],
        )
        after = db.get_surfer_batch("surfer-u1")
        assert after is not None
        assert after["status"] == "CANCELLED"
        assert after["urls"][0]["outcome"] == "failed"
        assert after["job_ids"] == ["job-1", "job-2"]
        assert after["started_at"] == "2026-08-07 02:00:00"
        assert after["candidate_id"] == "cand-u"
        assert after["updated_at"] >= before["updated_at"]

        with pytest.raises(ValueError, match="at least one field"):
            db.update_surfer_batch("surfer-u1")
        with pytest.raises(ValueError, match="not found"):
            db.update_surfer_batch("surfer-missing", status="RUNNING")

    def test_upsert_registry_lists_surfer_batch(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert "surfer_batch" in db._UPSERT_SCHEMA_ENSURE_FLAGS
        assert db._UPSERT_SCHEMA_ENSURE_FLAGS["surfer_batch"] == ("_surfer_batch_schema_ensured",)
        assert db._UPSERT_LAZY_SCHEMA_HANDLERS["surfer_batch"] is db._ensure_surfer_batch_schema
        db._surfer_batch_schema_ensured = False
        db.ensure_all_upsert_registry_schemas_at_startup()
        assert db._surfer_batch_schema_ensured is True
        assert db.insert_surfer_batch(
            "surfer-reg",
            "cand-r",
            "RUNNING",
            "2026-08-07 03:00:00",
            [],
            [],
        )
