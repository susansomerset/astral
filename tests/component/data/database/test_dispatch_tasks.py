"""Component tests for dispatch_task table cluster (AST-392)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


class TestSaveDispatchTask:
    def test_inserts_and_reads_task(self, seeded_db) -> None:
        db = seeded_db
        task_id = db.save_dispatch_task("cand-1", "qualify_job_listings", min_count=1, trigger_state="IMPORTED")
        row = db.get_dispatch_task(task_id)
        assert row is not None
        assert row["candidate_id"] == "cand-1"
        assert row["task_key"] == "qualify_job_listings"


class TestAst525InflowDiscoveryEligible:
    """AST-525: per-term last_scan_at staleness; dispatch last_run_at ignored."""

    def _seed_live(self, db, cid: str = "c525", terms: list[str] | None = None) -> None:
        db.save_candidate(cid, state="LIVE_PROMPTS", candidate_data={})
        if terms:
            db.sync_company_search_terms(cid, terms)

    def test_eligible_when_stale_term_in_table(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live(db, terms=["fintech"])
        assert db.count_candidate_inflow_discovery_eligible("c525", 168.0, None) == 1

    def test_not_eligible_wrong_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c525", state="NEW", candidate_data={})
        db.sync_company_search_terms("c525", ["term"])
        assert db.count_candidate_inflow_discovery_eligible("c525", 168.0, None) == 0

    def test_not_eligible_no_table_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c525", state="LIVE_PROMPTS", candidate_data={})
        assert db.count_candidate_inflow_discovery_eligible("c525", 168.0, None) == 0

    def test_not_eligible_when_all_terms_fresh(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live(db, terms=["term"])
        db.update_company_search_term_last_scan_at("c525", "term")
        assert db.count_candidate_inflow_discovery_eligible("c525", 168.0, None) == 0

    def test_last_run_at_ignored_when_stale_term_exists(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live(db, terms=["term"])
        recent = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        assert db.count_candidate_inflow_discovery_eligible("c525", 168.0, recent) == 1

    def test_eligible_when_one_stale_among_fresh(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live(db, terms=["fresh", "stale"])
        db.update_company_search_term_last_scan_at("c525", "fresh")
        conn = db._get_connection()
        try:
            conn.execute(
                """UPDATE company_search_terms SET last_scan_at = datetime('now', '-200 hours')
                   WHERE candidate_id = ? AND search_term = ?""",
                ("c525", "stale"),
            )
            conn.commit()
        finally:
            conn.close()
        assert db.count_candidate_inflow_discovery_eligible("c525", 168.0, None) == 1

    def test_count_eligible_for_dispatch_task_uses_table_staleness(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live(db, terms=["term"])
        task = {
            "entity_type": "candidate",
            "trigger_state": "LIVE_PROMPTS",
            "candidate_id": "c525",
            "freq_hrs": 168,
            "last_run_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
        assert db.count_eligible_for_dispatch_task(task) == 1



class TestAst506InflowResolveEligible:
    """AST-506: company NEW without website eligibility for inflow_resolve_website."""

    def test_count_new_without_website(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("no_site", state="NEW", candidate_id="c506", company_name="no_site")
        db.save_company(
            "has_site",
            state="NEW",
            candidate_id="c506",
            company_website="https://has.example",
            company_name="has_site",
        )
        assert db.count_company_new_without_website("c506") == 1

    def test_count_excludes_claimed_batch(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("claimed", state="NEW", candidate_id="c506", company_name="claimed")
        db.claim_company_batch("batch-506", "NEW", 1, candidate_id="c506", require_empty_website=True)
        assert db.count_company_new_without_website("c506") == 0

    def test_claim_skips_new_with_website(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("skip_me", state="NEW", candidate_id="c506", company_website="https://x.example")
        db.save_company("claim_me", state="NEW", candidate_id="c506", company_name="claim_me")
        n = db.claim_company_batch("batch-506", "NEW", 10, candidate_id="c506", require_empty_website=True)
        assert n == 1
        rows = db.get_company_batch("batch-506")
        assert len(rows) == 1
        assert rows[0]["short_name"] == "claim_me"

    def test_count_eligible_for_dispatch_task_resolve(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("resolve_me", state="NEW", candidate_id="c506", company_name="resolve_me")
        task = {
            "entity_type": "company",
            "trigger_state": "NEW",
            "task_key": "inflow_resolve_website",
            "candidate_id": "c506",
        }
        assert db.count_eligible_for_dispatch_task(task) == 1


class TestAst508PrefilterPassedEligible:
    """AST-508: company dispatch score_floor on claim/count for PREFILTER_PASSED."""

    def _seed_scored_companies(self, db) -> None:
        db.save_company(
            "below_floor",
            state="PREFILTER_PASSED",
            candidate_id="c508",
            company_name="below_floor",
            company_data={"prefilter_score": 6.5},
        )
        db.save_company(
            "at_floor",
            state="PREFILTER_PASSED",
            candidate_id="c508",
            company_name="at_floor",
            company_data={"prefilter_score": 7.0},
        )
        db.save_company(
            "above_floor",
            state="PREFILTER_PASSED",
            candidate_id="c508",
            company_name="above_floor",
            company_data={"prefilter_score": 8.0},
        )
        db.save_company(
            "no_score",
            state="PREFILTER_PASSED",
            candidate_id="c508",
            company_name="no_score",
        )

    def test_count_companies_in_state_with_score_floor(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_scored_companies(db)
        assert db.count_companies_in_state_with_score_floor("c508", "PREFILTER_PASSED", 7.0) == 2

    def test_claim_skips_below_floor_and_missing_score(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_scored_companies(db)
        n = db.claim_company_batch(
            "batch-508",
            "PREFILTER_PASSED",
            10,
            candidate_id="c508",
            score_floor=7.0,
        )
        assert n == 2
        rows = db.get_company_batch("batch-508")
        names = {r["short_name"] for r in rows}
        assert names == {"at_floor", "above_floor"}

    def test_count_eligible_for_dispatch_task_with_score_floor(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_scored_companies(db)
        task = {
            "entity_type": "company",
            "trigger_state": "PREFILTER_PASSED",
            "task_key": "find_job_page",
            "candidate_id": "c508",
            "score_floor": 7.0,
        }
        assert db.count_eligible_for_dispatch_task(task) == 2


class TestAst535DispatchTaskTripleUnique:
    """AST-535: UNIQUE(candidate_id, task_key, trigger_state); TO_WATCH trio rows."""

    def test_fresh_schema_enforces_triple_unique(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            create_sql = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='dispatch_task'"
            ).fetchone()[0]
            assert "UNIQUE(candidate_id, task_key, trigger_state)" in create_sql
        finally:
            conn.close()

    def test_same_to_watch_different_task_keys_coexist(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        for task_key in ("find_job_page", "select_job_page", "parse_job_list"):
            db.save_dispatch_task("c535", task_key, min_count=1, trigger_state="TO_WATCH")
        conn = db._get_connection()
        try:
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND trigger_state = ?",
                ("c535", "TO_WATCH"),
            ).fetchone()[0]
            assert n == 3
        finally:
            conn.close()

    def test_duplicate_triple_rejected_on_insert(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("c535", "find_job_page", min_count=1, trigger_state="TO_WATCH")
        with pytest.raises(Exception, match="UNIQUE"):
            db.save_dispatch_task("c535", "find_job_page", min_count=1, trigger_state="TO_WATCH")


class TestAst641UnionClaimCount:
    """AST-641: primary trigger rows union companion *_RETRY for claim/count; retry-only rows unchanged."""

    def _seed_valid_title_jobs(self, db, cid: str = "c641") -> None:
        db.save_company("co641", state="IMPORTED", candidate_id=cid, company_name="co641")
        db.save_job("job-primary", company="co641", state="VALID_TITLE")
        db.save_job("job-retry", company="co641", state="VALID_TITLE_RETRY")
        db.save_job("job-other", company="co641", state="JD_READY")

    def test_count_eligible_primary_job_unions_retry(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_valid_title_jobs(db)
        task = {
            "entity_type": "job",
            "trigger_state": "VALID_TITLE",
            "task_key": "qualify_job_listings",
            "candidate_id": "c641",
        }
        assert db.count_eligible_for_dispatch_task(task) == 2

    def test_count_eligible_retry_only_job_single_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_valid_title_jobs(db)
        task = {
            "entity_type": "job",
            "trigger_state": "VALID_TITLE_RETRY",
            "task_key": "qualify_job_listings",
            "candidate_id": "c641",
        }
        assert db.count_eligible_for_dispatch_task(task) == 1

    def test_claim_job_batch_unions_primary_and_retry(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_valid_title_jobs(db)
        n = db.claim_job_batch(
            "batch-641",
            "VALID_TITLE",
            10,
            candidate_id="c641",
            states=["VALID_TITLE", "VALID_TITLE_RETRY"],
        )
        assert n == 2
        rows = db.get_job_batch("batch-641")
        assert {r["astral_job_id"] for r in rows} == {"job-primary", "job-retry"}

    def test_count_eligible_company_prefilter_unions_retry(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "c641c"
        db.save_company("wf", state="WEBSITE_FOUND", candidate_id=cid, company_name="wf")
        db.save_company("wfr", state="WEBSITE_FOUND_RETRY", candidate_id=cid, company_name="wfr")
        db.save_company("other", state="NEW", candidate_id=cid, company_name="other")
        task = {
            "entity_type": "company",
            "trigger_state": "WEBSITE_FOUND",
            "task_key": "prefilter",
            "candidate_id": cid,
        }
        assert db.count_eligible_for_dispatch_task(task) == 2

    def test_claim_company_batch_unions_primary_and_retry(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "c641c"
        db.save_company("wf", state="WEBSITE_FOUND", candidate_id=cid, company_name="wf")
        db.save_company("wfr", state="WEBSITE_FOUND_RETRY", candidate_id=cid, company_name="wfr")
        n = db.claim_company_batch(
            "batch-641c",
            "WEBSITE_FOUND",
            10,
            candidate_id=cid,
            states=["WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"],
        )
        assert n == 2
        rows = db.get_company_batch("batch-641c")
        assert {r["short_name"] for r in rows} == {"wf", "wfr"}

    def test_scored_primary_count_applies_floor_across_union(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "c641s"
        db.save_company("co", state="IMPORTED", candidate_id=cid, company_name="co")
        db.save_job("j-pass", company="co", state="PASSED_LIKE")
        db.save_job("j-pass", latest_score=8.0)
        db.save_job("j-retry-pass", company="co", state="PASSED_LIKE_RETRY")
        db.save_job("j-retry-pass", latest_score=8.0)
        db.save_job("j-below", company="co", state="PASSED_LIKE")
        db.save_job("j-below", latest_score=0.5)
        task = {
            "entity_type": "job",
            "trigger_state": "PASSED_LIKE",
            "task_key": "consult_like",
            "candidate_id": cid,
            "score_floor": 7.0,
        }
        assert db.count_eligible_for_dispatch_task(task) == 2


class TestAst745StopAutomaticDispatchRowSeeding:
    """AST-745: schema ensure no longer re-inserts deleted *_RETRY or gaze_board dispatch rows."""

    def test_schema_ensure_does_not_reinsert_deleted_retry_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("c745", "fetch_website", min_count=1, trigger_state="WEBSITE_FOUND")
        db.save_dispatch_task("c745", "fetch_website", min_count=1, trigger_state="WEBSITE_FOUND_RETRY")
        conn = db._get_connection()
        try:
            conn.execute(
                "DELETE FROM dispatch_task WHERE candidate_id = ? AND trigger_state LIKE '%_RETRY'",
                ("c745",),
            )
            conn.commit()
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND trigger_state LIKE '%_RETRY'",
                ("c745",),
            ).fetchone()[0]
            assert n == 0
        finally:
            conn.close()

    def test_schema_ensure_does_not_reinsert_gaze_board_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "c745gb"
        db.save_dispatch_task(cid, "gaze", min_count=1, trigger_state="ACTIVE")
        db.save_board_search_row("bs745", cid, "tst", "lbl", "{}", state="ACTIVE")
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND task_key = 'gaze_board'",
                (cid,),
            ).fetchone()[0]
            assert n == 0
        finally:
            conn.close()

    def test_primary_row_claims_retry_entities_without_retry_dispatch_row(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "c745q"
        db.save_company("co745", state="IMPORTED", candidate_id=cid, company_name="co745")
        db.save_job("jp", company="co745", state="VALID_TITLE")
        db.save_job("jr", company="co745", state="VALID_TITLE_RETRY")
        db.save_dispatch_task(cid, "qualify_job_listings", min_count=1, trigger_state="VALID_TITLE")
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            retry_rows = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task "
                "WHERE candidate_id = ? AND trigger_state = 'VALID_TITLE_RETRY'",
                (cid,),
            ).fetchone()[0]
            assert retry_rows == 0
        finally:
            conn.close()
        task = {
            "entity_type": "job",
            "trigger_state": "VALID_TITLE",
            "task_key": "qualify_job_listings",
            "candidate_id": cid,
        }
        assert db.count_eligible_for_dispatch_task(task) == 2


class TestAst702PrefilterDispatchMigration:
    """AST-702: prefilter rows migrate to HOMEPAGE_READY batch mode; obsolete retry rows removed."""

    def test_schema_migrates_prefilter_base_row_to_homepage_ready(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("c702", "prefilter", min_count=1, trigger_state="WEBSITE_FOUND")
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            row = conn.execute(
                "SELECT trigger_state, batch_call_mode FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'prefilter'",
                ("c702",),
            ).fetchone()
            assert tuple(row) == ("HOMEPAGE_READY", 1)
        finally:
            conn.close()

    def test_schema_deletes_obsolete_prefilter_retry_companion_row(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("c702b", "prefilter", min_count=1, trigger_state="WEBSITE_FOUND_RETRY")
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'",
                ("c702b",),
            ).fetchone()[0]
            assert n == 0
        finally:
            conn.close()

class TestAst703PrefilterMigrationUniqueCollision:
    """AST-703 UAT: legacy dual prefilter rows migrate without UNIQUE violation."""

    def test_schema_migrates_when_both_website_found_and_retry_exist(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("c703", "prefilter", min_count=1, trigger_state="WEBSITE_FOUND")
        db.save_dispatch_task("c703", "prefilter", min_count=1, trigger_state="WEBSITE_FOUND_RETRY")
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND task_key = 'prefilter'",
                ("c703",),
            ).fetchone()[0]
            row = conn.execute(
                "SELECT trigger_state, batch_call_mode FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'prefilter'",
                ("c703",),
            ).fetchone()
            assert n == 1
            assert tuple(row) == ("HOMEPAGE_READY", 1)
        finally:
            conn.close()
