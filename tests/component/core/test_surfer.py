"""Component tests for src/core/surfer.py (AST-1229)."""

from __future__ import annotations

import re

import pytest

from src.core import surfer as surfer_mod
from src.core.candidate import get_candidate
from src.utils.config import SURFER_BATCH_CONFIG

_POINTER_KEY = SURFER_BATCH_CONFIG["candidate_data_lifecycle_key"]
_BATCH_ID_RE = re.compile(
    rf"^{re.escape(SURFER_BATCH_CONFIG['batch_id_prefix'])}-"
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


def _seed_candidate(db, cid: str = "cand-surf") -> str:
    db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Surf"})
    return cid


def _pointer(cid: str):
    cand = get_candidate(cid)
    assert cand is not None
    life = (cand.get("candidate_data") or {}).get("lifecycle") or {}
    return life.get(_POINTER_KEY)


# Branches: validation; create RUNNING+pointer+started_at; one active batch;
# URL pending/delivered stay non-terminal; all-terminal auto-COMPLETE + clear;
# CANCELLED clears without all-terminal; COMPLETED blocked on non-terminal URLs;
# job_ids list survives claim/clear (AC6/AC7).
class TestAst1229SurferBatchEntity:
    def test_create_sets_running_pointer_and_readable_started_at(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = _seed_candidate(db)
        urls = ["https://jobs.example/a", "https://jobs.example/b", "https://jobs.example/a"]
        batch = surfer_mod.create_surfer_batch(cid, urls)
        assert _BATCH_ID_RE.match(batch["batch_id"])
        assert batch["status"] == SURFER_BATCH_CONFIG["initial_status"]
        assert batch["candidate_id"] == cid
        assert isinstance(batch["started_at"], str) and len(batch["started_at"]) >= 19
        assert batch["job_ids"] == []
        # Deduped order-preserving URL worklist; initial outcomes from config.
        assert [e["url"] for e in batch["urls"]] == [
            "https://jobs.example/a",
            "https://jobs.example/b",
        ]
        assert all(
            e["outcome"] == SURFER_BATCH_CONFIG["initial_url_outcome"] for e in batch["urls"]
        )
        assert _pointer(cid) == batch["batch_id"]
        active = surfer_mod.get_active_surfer_batch(cid)
        assert active is not None and active["batch_id"] == batch["batch_id"]

    def test_create_validation_and_one_active_batch(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = _seed_candidate(db)
        with pytest.raises(ValueError, match="candidate_id is required"):
            surfer_mod.create_surfer_batch("", ["https://x"])
        with pytest.raises(ValueError, match="Candidate not found"):
            surfer_mod.create_surfer_batch("missing", ["https://x"])
        with pytest.raises(ValueError, match="non-empty list"):
            surfer_mod.create_surfer_batch(cid, [])
        with pytest.raises(ValueError, match="non-empty strings"):
            surfer_mod.create_surfer_batch(cid, ["  "])

        first = surfer_mod.create_surfer_batch(cid, ["https://a.example"])
        with pytest.raises(ValueError, match="already has a non-terminal"):
            surfer_mod.create_surfer_batch(cid, ["https://b.example"])
        assert _pointer(cid) == first["batch_id"]

    def test_url_outcomes_and_auto_complete_clears_pointer(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = _seed_candidate(db, "cand-ac4")
        batch = surfer_mod.create_surfer_batch(
            cid,
            ["https://ex.com/1", "https://ex.com/2"],
        )
        bid = batch["batch_id"]

        # Delivered is non-terminal — batch stays RUNNING (AC4).
        mid = surfer_mod.set_surfer_batch_url_outcome(bid, "https://ex.com/1", "delivered")
        assert mid["status"] == "RUNNING"
        assert mid["urls"][0]["outcome"] == "delivered"
        assert _pointer(cid) == bid

        # Never-visited sibling still pending → still non-terminal.
        mid2 = surfer_mod.set_surfer_batch_url_outcome(bid, "https://ex.com/1", "success")
        assert mid2["status"] == "RUNNING"
        assert _pointer(cid) == bid

        # All terminal → auto-complete via requires_all_urls_terminal (not "COMPLETED" literal).
        done = surfer_mod.set_surfer_batch_url_outcome(bid, "https://ex.com/2", "failed")
        auto = next(
            name
            for name, cfg in SURFER_BATCH_CONFIG["statuses"].items()
            if cfg["requires_all_urls_terminal"]
        )
        assert done["status"] == auto
        assert SURFER_BATCH_CONFIG["statuses"][auto]["terminal"] is True
        # Stored lifecycle key is JSON null (None) — AC5 clear path.
        assert _pointer(cid) is None
        assert surfer_mod.get_active_surfer_batch(cid) is None

    def test_cancel_clears_pointer_without_all_urls_terminal(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = _seed_candidate(db, "cand-cancel")
        batch = surfer_mod.create_surfer_batch(cid, ["https://ex.com/c"])
        bid = batch["batch_id"]
        out = surfer_mod.transition_surfer_batch_status(bid, "CANCELLED")
        assert out["status"] == "CANCELLED"
        assert out["urls"][0]["outcome"] == "pending"
        assert _pointer(cid) is None

    def test_completed_requires_all_urls_terminal(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = _seed_candidate(db, "cand-block")
        batch = surfer_mod.create_surfer_batch(cid, ["https://ex.com/x"])
        auto = next(
            name
            for name, cfg in SURFER_BATCH_CONFIG["statuses"].items()
            if cfg["requires_all_urls_terminal"]
        )
        with pytest.raises(ValueError, match="not terminal"):
            surfer_mod.transition_surfer_batch_status(batch["batch_id"], auto)
        assert db.get_surfer_batch(batch["batch_id"])["status"] == "RUNNING"

    def test_job_association_survives_dispatcher_claim_and_clear(
        self, sqlite_in_memory,
    ) -> None:
        """AC6/AC7: Surfer job_ids independent of job.batch_id claim lock."""
        db = sqlite_in_memory
        cid = _seed_candidate(db, "cand-jobs")
        batch = surfer_mod.create_surfer_batch(cid, ["https://ex.com/j"])
        bid = batch["batch_id"]
        db.save_job("job-surf-1", company="acme", state="NEW")
        db.save_job("job-surf-2", company="acme", state="NEW")
        surfer_mod.add_surfer_batch_job(bid, "job-surf-1")
        surfer_mod.add_surfer_batch_job(bid, "job-surf-2")
        # Idempotent append.
        surfer_mod.add_surfer_batch_job(bid, "job-surf-1")
        assert db.get_surfer_batch(bid)["job_ids"] == ["job-surf-1", "job-surf-2"]

        claimed = db.claim_job_batch("dispatch-batch-1", "NEW", limit=10)
        assert claimed == 2
        assert db.get_job("job-surf-1")["batch_id"] == "dispatch-batch-1"
        # Surfer list does not depend on job.batch_id.
        jobs = surfer_mod.list_surfer_batch_jobs(bid)
        assert [j["astral_job_id"] for j in jobs] == ["job-surf-1", "job-surf-2"]

        released = db.clear_job_batch("dispatch-batch-1")
        assert released == 2
        assert db.get_job("job-surf-1")["batch_id"] is None
        jobs_after = surfer_mod.list_surfer_batch_jobs(bid)
        assert [j["astral_job_id"] for j in jobs_after] == ["job-surf-1", "job-surf-2"]
        # Dispatcher claim/clear still operate on job.batch_id (unchanged paths).
        assert db.get_surfer_batch(bid)["job_ids"] == ["job-surf-1", "job-surf-2"]
