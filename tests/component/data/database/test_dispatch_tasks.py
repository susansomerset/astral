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




class TestAst776InflowVetEligible:
    """AST-776: vet vs resolve eligibility split on inflow_discovery_blurb."""

    def test_count_new_pending_inflow_vet(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company(
            "vet_me",
            state="NEW",
            candidate_id="c776",
            company_name="vet_me",
            company_data={"inflow_discovery_blurb": "000|Co|https://co.example|snip"},
        )
        db.save_company("no_blurb", state="NEW", candidate_id="c776", company_name="no_blurb")
        assert db.count_company_new_pending_inflow_vet("c776") == 1

    def test_count_new_without_website_excludes_blurb(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company(
            "blurb_only",
            state="NEW",
            candidate_id="c776",
            company_name="blurb_only",
            company_data={"inflow_discovery_blurb": "000|Co|https://co.example|snip"},
        )
        db.save_company("legacy_new", state="NEW", candidate_id="c776", company_name="legacy_new")
        assert db.count_company_new_without_website("c776") == 1

    def test_count_eligible_vet_vs_resolve_split(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company(
            "vet_row",
            state="NEW",
            candidate_id="c776",
            company_name="vet_row",
            company_data={"inflow_discovery_blurb": "000|Co|https://vet.example|snip"},
        )
        db.save_company("resolve_row", state="NEW", candidate_id="c776", company_name="resolve_row")
        vet_task = {
            "entity_type": "company",
            "trigger_state": "NEW",
            "task_key": "vet_inflow_discovery",
            "candidate_id": "c776",
        }
        resolve_task = {
            "entity_type": "company",
            "trigger_state": "NEW",
            "task_key": "inflow_resolve_website",
            "candidate_id": "c776",
        }
        assert db.count_eligible_for_dispatch_task(vet_task) == 1
        assert db.count_eligible_for_dispatch_task(resolve_task) == 1

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
    """AST-745: schema ensure no longer re-inserts deleted *_RETRY dispatch rows."""

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


class TestAst748ConsultToGradeDispatchMigration:
    """AST-748: consult_* dispatch rows rename to grade_* under triple-unique constraint."""

    def _insert_legacy_dispatch_row(
        self, conn, candidate_id: str, task_key: str, trigger_state: str,
        batch_size: int = 1, freq_hrs: float = 0, auto_mode: int = 0,
    ) -> None:
        # Pre-AST-747 legacy rows — save_dispatch_task rejects retired keys after config cutover.
        conn.execute(
            """
            INSERT INTO dispatch_task (
                candidate_id, task_key, trigger_state, min_count, auto_mode,
                batch_size, freq_hrs, entity_type, sort_by, batch_call_mode
            ) VALUES (?, ?, ?, 1, ?, ?, ?, 'job', 'updated_at', 1)
            """,
            (candidate_id, task_key, trigger_state, auto_mode, batch_size, freq_hrs),
        )
        conn.commit()

    def test_schema_renames_consult_do_row_to_grade_do(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_legacy_dispatch_row(
                conn, "c748", "consult_do", "PASSED_JD", batch_size=8, freq_hrs=4.0, auto_mode=1,
            )
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            row = conn.execute(
                "SELECT task_key, batch_size, freq_hrs, auto_mode FROM dispatch_task "
                "WHERE candidate_id = ? AND trigger_state = 'PASSED_JD'",
                ("c748",),
            ).fetchone()
            assert row[0] == "grade_do"
            assert row[1] == 8
            assert row[2] == 4.0
            assert row[3] == 1
            legacy = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE task_key IN ('consult_do','consult_get','consult_like')",
            ).fetchone()[0]
            assert legacy == 0
        finally:
            conn.close()

    def test_schema_deletes_consult_row_when_grade_triple_exists(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("c748b", "grade_do", min_count=1, trigger_state="PASSED_JD", batch_size=5)
        conn = db._get_connection()
        try:
            self._insert_legacy_dispatch_row(
                conn, "c748b", "consult_do", "PASSED_JD", batch_size=99,
            )
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND task_key = 'grade_do' AND trigger_state = 'PASSED_JD'",
                ("c748b",),
            ).fetchone()[0]
            row = conn.execute(
                "SELECT batch_size FROM dispatch_task WHERE candidate_id = ? AND task_key = 'grade_do' AND trigger_state = 'PASSED_JD'",
                ("c748b",),
            ).fetchone()
            assert n == 1
            assert row[0] == 5
            legacy = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE task_key IN ('consult_do','consult_get','consult_like')",
            ).fetchone()[0]
            assert legacy == 0
        finally:
            conn.close()



class TestAst797DispatchKeyCutoverMigration:
    """AST-797: scrape_jd→fetch_jd rename, purge retired keys, qualify VALID_TITLE split."""

    def _insert_legacy_dispatch_row(
        self, conn, candidate_id: str, task_key: str, trigger_state: str,
        batch_size: int = 1, freq_hrs: float = 0, auto_mode: int = 0,
    ) -> None:
        conn.execute(
            """
            INSERT INTO dispatch_task (
                candidate_id, task_key, trigger_state, min_count, auto_mode,
                batch_size, freq_hrs, entity_type, sort_by, batch_call_mode
            ) VALUES (?, ?, ?, 1, ?, ?, ?, 'job', 'updated_at', 0)
            """,
            (candidate_id, task_key, trigger_state, auto_mode, batch_size, freq_hrs),
        )
        conn.commit()

    def test_scrape_jd_row_renames_to_fetch_jd(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_legacy_dispatch_row(
                conn, "c797", "scrape_jd", "PASSED_JOBLIST", batch_size=5, freq_hrs=2.0, auto_mode=1,
            )
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            row = conn.execute(
                "SELECT task_key, batch_size, freq_hrs, auto_mode FROM dispatch_task "
                "WHERE candidate_id = ? AND trigger_state = 'PASSED_JOBLIST'",
                ("c797",),
            ).fetchone()
            assert row[0] == "fetch_jd"
            assert row[1] == 5
            assert row[2] == 2.0
            assert row[3] == 1
        finally:
            conn.close()

    def test_scrape_jd_deleted_when_fetch_jd_triple_exists(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("c797b", "fetch_jd", min_count=1, trigger_state="PASSED_JOBLIST", batch_size=3)
        conn = db._get_connection()
        try:
            self._insert_legacy_dispatch_row(
                conn, "c797b", "scrape_jd", "PASSED_JOBLIST", batch_size=99,
            )
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND task_key = 'fetch_jd'",
                ("c797b",),
            ).fetchone()[0]
            row = conn.execute(
                "SELECT batch_size FROM dispatch_task WHERE candidate_id = ? AND task_key = 'fetch_jd'",
                ("c797b",),
            ).fetchone()
            assert n == 1
            assert row[0] == 3
        finally:
            conn.close()

    def test_purges_validate_title_and_gaze_board_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_legacy_dispatch_row(conn, "c797c", "validate_title", "NEW")
            self._insert_legacy_dispatch_row(conn, "c797c", "gaze_board", "ACTIVE")
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE task_key IN ('validate_title','gaze_board')",
            ).fetchone()[0]
            assert n == 0
        finally:
            conn.close()

    def test_qualify_valid_title_splits_to_new_and_retry_companion(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_legacy_dispatch_row(
                conn, "c797d", "qualify_job_listings", "VALID_TITLE", batch_size=7, freq_hrs=3.0,
            )
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            primary = conn.execute(
                "SELECT trigger_state, batch_size, freq_hrs FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'qualify_job_listings' AND trigger_state = 'NEW'",
                ("c797d",),
            ).fetchone()
            retry = conn.execute(
                "SELECT trigger_state, batch_size, freq_hrs FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'qualify_job_listings' AND trigger_state = 'VALID_TITLE_RETRY'",
                ("c797d",),
            ).fetchone()
            assert primary[0] == "NEW"
            assert primary[1] == 7
            assert primary[2] == 3.0
            assert retry[0] == "VALID_TITLE_RETRY"
            assert retry[1] == 7
            assert retry[2] == 3.0
        finally:
            conn.close()

    def test_no_legacy_task_keys_remain(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_legacy_dispatch_row(conn, "c797e", "scrape_jd", "PASSED_JOBLIST")
            self._insert_legacy_dispatch_row(conn, "c797e", "validate_title", "NEW")
            self._insert_legacy_dispatch_row(conn, "c797e", "qualify_job_listings", "VALID_TITLE")
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE task_key IN ('scrape_jd','validate_title','gaze_board')",
            ).fetchone()[0]
            assert n == 0
        finally:
            conn.close()


class TestAst766BoardSchemaSunset:
    """AST-766: board_search tables/column removed from database.py."""

    def test_fresh_db_has_no_board_tables_or_job_column(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._job_schema_ensured = False
            db._ensure_job_schema(conn)
            tables = {
                r[0]
                for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
            assert "board_search" not in tables
            assert "board_search_run" not in tables
            cols = {r[1] for r in conn.execute("PRAGMA table_info(job)").fetchall()}
            assert "board_search_id" not in cols
        finally:
            conn.close()

    def test_legacy_db_drops_board_tables_and_column(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            conn.execute(
                "CREATE TABLE board_search (board_search_id TEXT PRIMARY KEY, candidate_id TEXT)"
            )
            conn.execute("CREATE TABLE board_search_run (batch_id TEXT, board_search_id TEXT)")
            conn.execute(
                """CREATE TABLE job (
                    astral_job_id TEXT PRIMARY KEY, company TEXT NOT NULL, company_job_id TEXT,
                    job_title TEXT, job_link TEXT, job_data TEXT, state TEXT NOT NULL,
                    state_history TEXT, batch_id TEXT, batch_created_at TEXT,
                    created_at TEXT, updated_at TEXT, state_changed_at TEXT,
                    board_search_id TEXT
                )"""
            )
            conn.execute(
                "INSERT INTO job (astral_job_id, company, state, board_search_id) "
                "VALUES ('j766', 'co', 'NEW', 'bs1')"
            )
            conn.commit()
            db._job_schema_ensured = False
            db._board_schema_sunset_applied = False
            db._ensure_job_schema(conn)
            tables = {
                r[0]
                for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
            assert "board_search" not in tables
            assert "board_search_run" not in tables
            cols = {r[1] for r in conn.execute("PRAGMA table_info(job)").fetchall()}
            assert "board_search_id" not in cols
            assert conn.execute(
                "SELECT astral_job_id FROM job WHERE astral_job_id='j766'"
            ).fetchone() is not None
        finally:
            conn.close()

    def test_board_search_ddl_helpers_removed(self) -> None:
        from src.data import database as db_mod

        for name in (
            "save_board_search_row",
            "claim_board_search_batch",
            "board_listing_is_duplicate",
        ):
            assert not hasattr(db_mod, name)

    def test_count_eligible_board_search_entity_returns_zero(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c766", state="NEW")
        assert (
            db.count_eligible_for_dispatch_task(
                {
                    "entity_type": "board_search",
                    "trigger_state": "ACTIVE",
                    "candidate_id": "c766",
                    "task_key": "gaze_board",
                }
            )
            == 0
        )

