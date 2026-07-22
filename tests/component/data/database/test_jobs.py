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


# Branches: identity lookup; single-row delete (post-qualify collision path).
class TestAst733JobIdentityHelpers:
    def test_get_job_id_by_identity_finds_canonical_excludes_self(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job(
            "canonical", company="acme", state="NEW", job_title="Eng", company_job_id="99"
        )
        db.save_job(
            "collision", company="acme", state="NEW", job_title="Other", company_job_id="old"
        )
        assert db.get_job_id_by_identity("acme", "Eng", "99") == "canonical"
        assert (
            db.get_job_id_by_identity("acme", "Eng", "99", exclude_astral_job_id="canonical")
            is None
        )
        assert (
            db.get_job_id_by_identity("acme", "Eng", "99", exclude_astral_job_id="collision")
            == "canonical"
        )

    def test_delete_job_removes_row(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-del", company="acme", state="NEW", job_title="X")
        assert db.delete_job("job-del") is True
        assert db.get_job("job-del") is None
        assert db.delete_job("") is False
        assert db.delete_job("missing") is False


# Branches: floors map keys via dispatch_claim_uses_score_floor; list/count below-floor
# membership for PASSED_JOBLIST + existing PASSED_SCORE_GATED states (AST-908).
class TestAst908BelowDispatchScoreFloorViews:
    """Jobs UI floors follow claim score-floor gate (includes PASSED_JOBLIST)."""

    def _seed_candidate_company(self, db, candidate_id: str = "c908", short_name: str = "acme") -> None:
        db.save_company(short_name, state="IMPORTED", candidate_id=candidate_id)

    def _save_job_with_score(
        self, db, astral_job_id: str, *, company: str, state: str, latest_score: float | None,
    ) -> None:
        # save_job INSERT omits latest_score; set score on the UPDATE path (same as dispatch_tasks tests).
        db.save_job(astral_job_id, company=company, state=state)
        if latest_score is not None:
            db.save_job(astral_job_id, latest_score=latest_score)

    def test_floors_map_includes_passed_joblist_excludes_pre_score_triggers(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_candidate_company(db)
        # Claim-gated transition outcome (AST-908 gap vs PASSED_SCORE_GATED_STATES).
        db.save_dispatch_task(
            "c908", "fetch_jd", min_count=1, trigger_state="PASSED_JOBLIST", score_floor=6.0,
        )
        # Still claim-gated consult state — max floor wins if duplicated later.
        db.save_dispatch_task(
            "c908", "evaluate_jd", min_count=1, trigger_state="PASSED_JD", score_floor=7.0,
        )
        # Pre-score In Review triggers must never appear in the floors map.
        db.save_dispatch_task(
            "c908", "qualify_job_listings", min_count=1, trigger_state="VALID_TITLE", score_floor=9.0,
        )
        floors = db.score_floor_by_trigger_for_candidate("c908")
        assert floors["PASSED_JOBLIST"] == 6.0
        assert floors["PASSED_JD"] == 7.0
        assert "VALID_TITLE" not in floors
        assert "JD_READY" not in floors

    def test_null_score_floor_defaults_to_one(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_candidate_company(db)
        db.save_dispatch_task(
            "c908", "fetch_jd", min_count=1, trigger_state="PASSED_JOBLIST", score_floor=None,
        )
        assert db.score_floor_by_trigger_for_candidate("c908") == {"PASSED_JOBLIST": 1.0}

    def test_list_and_count_below_floor_for_passed_joblist(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_candidate_company(db)
        db.save_dispatch_task(
            "c908", "fetch_jd", min_count=1, trigger_state="PASSED_JOBLIST", score_floor=6.0,
        )
        self._save_job_with_score(db, "below", company="acme", state="PASSED_JOBLIST", latest_score=5.0)
        self._save_job_with_score(db, "null_score", company="acme", state="PASSED_JOBLIST", latest_score=None)
        self._save_job_with_score(db, "at_floor", company="acme", state="PASSED_JOBLIST", latest_score=6.0)
        self._save_job_with_score(db, "above", company="acme", state="PASSED_JOBLIST", latest_score=8.0)
        # Real skipped / non-floor state — must not join the virtual below-floor set.
        self._save_job_with_score(db, "failed", company="acme", state="FAILED_JOBLIST", latest_score=1.0)

        below = db.list_jobs_below_dispatch_score_floor("c908")
        below_ids = {r["astral_job_id"] for r in below}
        assert below_ids == {"below", "null_score"}
        assert db.count_jobs_below_dispatch_score_floor("c908") == 2
        assert not any(r["astral_job_id"] == "failed" for r in below)

    def test_passed_jd_below_floor_still_listed(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_candidate_company(db)
        db.save_dispatch_task(
            "c908", "evaluate_jd", min_count=1, trigger_state="PASSED_JD", score_floor=7.0,
        )
        self._save_job_with_score(db, "jd_below", company="acme", state="PASSED_JD", latest_score=6.5)
        self._save_job_with_score(db, "jd_ok", company="acme", state="PASSED_JD", latest_score=7.0)
        below_ids = {r["astral_job_id"] for r in db.list_jobs_below_dispatch_score_floor("c908")}
        assert below_ids == {"jd_below"}
        assert db.count_jobs_below_dispatch_score_floor("c908") == 1

    def test_other_candidate_dispatch_ignored(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_candidate_company(db, candidate_id="c908")
        db.save_company("otherco", state="IMPORTED", candidate_id="other")
        db.save_dispatch_task(
            "other", "fetch_jd", min_count=1, trigger_state="PASSED_JOBLIST", score_floor=9.0,
        )
        self._save_job_with_score(db, "job-other", company="otherco", state="PASSED_JOBLIST", latest_score=1.0)
        assert db.score_floor_by_trigger_for_candidate("c908") == {}
        assert db.list_jobs_below_dispatch_score_floor("c908") == []
        assert db.count_jobs_below_dispatch_score_floor("c908") == 0
