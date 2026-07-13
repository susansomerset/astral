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


class TestAst802InflowDiscoveryEligible:
    """AST-802: legacy artifact blob reconciles into table for inflow_discovery eligibility."""

    def test_eligible_after_artifact_only_reconcile(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c802",
            state="LIVE_PROMPTS",
            candidate_data={"artifacts": {"company_search_terms": "fintech\nsaas"}},
        )
        assert db.count_candidate_inflow_discovery_eligible("c802", 168.0, None) == 1
        rows = db.list_company_search_terms("c802")
        assert len(rows) == 2
        assert {r["search_term"] for r in rows} == {"fintech", "saas"}

    def test_reconcile_strips_legacy_artifact_blob(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c802",
            state="LIVE_PROMPTS",
            candidate_data={"artifacts": {"company_search_terms": "term1", "other": "keep"}},
        )
        db.count_candidate_inflow_discovery_eligible("c802", 168.0, None)
        cand = db.get_candidate("c802")
        arts = (cand.get("candidate_data") or {}).get("artifacts") or {}
        assert "company_search_terms" not in arts
        assert arts.get("other") == "keep"

    def test_count_eligible_for_dispatch_task_after_artifact_reconcile(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c802",
            state="LIVE_PROMPTS",
            candidate_data={"artifacts": {"company_search_terms": "alpha"}},
        )
        task = {
            "entity_type": "candidate",
            "trigger_state": "LIVE_PROMPTS",
            "candidate_id": "c802",
            "task_key": "inflow_discovery",
        }
        assert db.count_eligible_for_dispatch_task(task) == 1

    def test_describe_eligibility_reason_wrong_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c802", state="NEW", candidate_data={})
        eligible, reason = db.describe_candidate_inflow_discovery_eligibility("c802", 168.0)
        assert eligible == 0
        assert "eligibility:" in reason
        assert "LIVE_PROMPTS" in reason


class TestAst814InflowDiscoveryFreqHrs:
    """AST-814: dispatch_task.freq_hrs drives stale helpers and eligibility (not config 168)."""

    def _seed_live_fresh(self, db, cid: str = "c814", terms: list[str] | None = None) -> None:
        db.save_candidate(cid, state="LIVE_PROMPTS", candidate_data={})
        db.sync_company_search_terms(cid, terms or ["alpha", "beta"])
        for term in terms or ["alpha", "beta"]:
            db.update_company_search_term_last_scan_at(cid, term)

    def test_freq_hrs_zero_eligible_and_lists_all_fresh_terms(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live_fresh(db)
        assert db.count_candidate_inflow_discovery_eligible("c814", 0.0, None) == 1
        assert db.count_stale_company_search_terms("c814", 0.0) == 2
        assert db.list_stale_company_search_terms("c814", 0.0) == ["alpha", "beta"]
        task = {
            "entity_type": "candidate",
            "trigger_state": "LIVE_PROMPTS",
            "candidate_id": "c814",
            "task_key": "inflow_discovery",
            "freq_hrs": 0,
        }
        assert db.count_eligible_for_dispatch_task(task) == 1

    def test_freq_hrs_168_all_fresh_not_eligible(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live_fresh(db)
        assert db.count_candidate_inflow_discovery_eligible("c814", 168.0, None) == 0
        eligible, reason = db.describe_candidate_inflow_discovery_eligibility("c814", 168.0)
        assert eligible == 0
        assert "freq_hrs=168" in reason
        assert "scan_interval_hours" not in reason

    def test_dispatch_task_freq_zero_overrides_fresh_exclusion(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_live_fresh(db)
        task = {
            "entity_type": "candidate",
            "trigger_state": "LIVE_PROMPTS",
            "candidate_id": "c814",
            "task_key": "inflow_discovery",
            "freq_hrs": 0,
        }
        assert db.count_eligible_for_dispatch_task(task) == 1
        assert db.count_candidate_inflow_discovery_eligible("c814", 168.0, None) == 0


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


class TestAst823PrefilterDispatchMigration:
    """AST-823 UAT: legacy prefilter_company dispatch rows and stale batch_call_mode retarget."""

    def _insert_legacy_company_dispatch_row(
        self, conn, candidate_id: str, task_key: str, trigger_state: str, batch_call_mode: int = 0,
    ) -> None:
        conn.execute(
            """
            INSERT INTO dispatch_task (
                candidate_id, task_key, trigger_state, min_count, auto_mode,
                batch_size, freq_hrs, entity_type, sort_by, batch_call_mode
            ) VALUES (?, ?, ?, 1, 0, 1, 0, 'company', 'updated_at', ?)
            """,
            (candidate_id, task_key, trigger_state, batch_call_mode),
        )
        conn.commit()

    def test_schema_retargets_prefilter_company_agent_key_row(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_legacy_company_dispatch_row(
                conn, "c823", "prefilter_company", "WEBSITE_FOUND",
            )
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            row = conn.execute(
                "SELECT task_key, trigger_state, batch_call_mode FROM dispatch_task "
                "WHERE candidate_id = ?",
                ("c823",),
            ).fetchone()
            assert tuple(row) == ("prefilter", "HOMEPAGE_READY", 1)
        finally:
            conn.close()

    def test_schema_enables_batch_call_mode_on_stale_homepage_ready_row(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_legacy_company_dispatch_row(
                conn, "c823b", "prefilter", "HOMEPAGE_READY", batch_call_mode=0,
            )
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            row = conn.execute(
                "SELECT trigger_state, batch_call_mode FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'prefilter'",
                ("c823b",),
            ).fetchone()
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

class TestAst874FetchCulturePagesDispatchMigration:
    """AST-874: seed fetch_culture_pages @ PASSED_GET; retarget grade_like → CULTURE_READY."""

    def _insert_grade_like_passed_get(
        self, conn, candidate_id: str, *, batch_size: int = 4, freq_hrs: float = 1.5,
        auto_mode: int = 1, score_floor: float = 0.7,
    ) -> None:
        # Raw insert — save_dispatch_task defaults grade_like to CULTURE_READY after AST-874.
        conn.execute(
            """
            INSERT INTO dispatch_task (
                candidate_id, task_key, trigger_state, min_count, auto_mode,
                batch_size, freq_hrs, entity_type, sort_by, batch_call_mode, score_floor
            ) VALUES (?, 'grade_like', 'PASSED_GET', 1, ?, ?, ?, 'job', 'updated_at', 0, ?)
            """,
            (candidate_id, auto_mode, batch_size, freq_hrs, score_floor),
        )
        conn.commit()

    def test_retargets_grade_like_and_seeds_fetch_culture_pages(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_grade_like_passed_get(conn, "c874")
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            like = conn.execute(
                "SELECT trigger_state, batch_size, score_floor FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'grade_like'",
                ("c874",),
            ).fetchone()
            fetch = conn.execute(
                "SELECT trigger_state, batch_size, freq_hrs, auto_mode, score_floor FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'fetch_culture_pages'",
                ("c874",),
            ).fetchone()
            assert like is not None
            assert like[0] == "CULTURE_READY"
            assert like[1] == 4
            assert float(like[2]) == 0.7
            assert fetch is not None
            assert fetch[0] == "PASSED_GET"
            assert fetch[1] == 4
            assert float(fetch[2]) == 1.5
            assert fetch[3] == 1
            assert float(fetch[4]) == 0.7
        finally:
            conn.close()

    def test_seeds_when_grade_like_already_culture_ready(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task(
            "c874b", "grade_like", min_count=1, trigger_state="CULTURE_READY",
            batch_size=6, freq_hrs=2.0, score_floor=0.55,
        )
        conn = db._get_connection()
        try:
            n_before = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND task_key = 'fetch_culture_pages'",
                ("c874b",),
            ).fetchone()[0]
            assert n_before == 0
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            fetch = conn.execute(
                "SELECT trigger_state, batch_size, freq_hrs, score_floor FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'fetch_culture_pages'",
                ("c874b",),
            ).fetchone()
            assert fetch is not None
            assert fetch[0] == "PASSED_GET"
            assert fetch[1] == 6
            assert float(fetch[2]) == 2.0
            assert float(fetch[3]) == 0.55
        finally:
            conn.close()

    def test_idempotent_no_duplicate_fetch_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            self._insert_grade_like_passed_get(conn, "c874c", batch_size=3)
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            db._dispatch_task_schema_ensured = False
            db._ensure_dispatch_task_schema(conn)
            n_like = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task WHERE candidate_id = ? AND task_key = 'grade_like'",
                ("c874c",),
            ).fetchone()[0]
            n_fetch = conn.execute(
                "SELECT COUNT(*) FROM dispatch_task "
                "WHERE candidate_id = ? AND task_key = 'fetch_culture_pages' AND trigger_state = 'PASSED_GET'",
                ("c874c",),
            ).fetchone()[0]
            assert n_like == 1
            assert n_fetch == 1
        finally:
            conn.close()



class TestAst875SetDispatchTasksFromTemplate:
    """AST-875: list/count/delete helpers + transactional set-from-template upsert+prune."""

    def _stamp_runtime(self, db, task_id: int, *, last_run_at: str, batch_id: str) -> None:
        # batch_id is not on update_dispatch_task whitelist — stamp via SQL for AC3 setup.
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE dispatch_task SET last_run_at = ?, batch_id = ? WHERE id = ?",
                (last_run_at, batch_id, task_id),
            )
            conn.commit()
        finally:
            conn.close()

    def test_list_and_count_helpers(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.list_dispatch_tasks_for_candidate("") == []
        assert db.list_dispatch_tasks_for_candidate("   ") == []
        db.save_dispatch_task("tmpl", "fetch_website", min_count=1, trigger_state="WEBSITE_FOUND")
        db.save_dispatch_task("tmpl", "fetch_website", min_count=1, trigger_state="WEBSITE_FOUND_RETRY")
        db.save_dispatch_task("other", "qualify_job_listings", min_count=1, trigger_state="VALID_TITLE")
        rows = db.list_dispatch_tasks_for_candidate("tmpl")
        assert len(rows) == 2
        assert all(r["candidate_id"] == "tmpl" for r in rows)
        assert [r["id"] for r in rows] == sorted(r["id"] for r in rows)
        counts = db.count_dispatch_tasks_by_candidate()
        assert counts["tmpl"] == 2
        assert counts["other"] == 1
        assert "missing" not in counts

    def test_delete_dispatch_task_noop_and_delete(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        tid = db.save_dispatch_task("c875", "fetch_jd", min_count=1, trigger_state="PASSED_JOBLIST")
        db.delete_dispatch_task(tid)
        assert db.get_dispatch_task(tid) is None
        db.delete_dispatch_task(tid)  # no-op if missing

    def test_set_upsert_prune_clears_runtime_and_is_idempotent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        # Template set: two keys; target starts with one match + one extra.
        t1 = db.save_dispatch_task(
            "tmpl", "fetch_website", min_count=2, trigger_state="WEBSITE_FOUND",
            auto_mode=True, batch_size=5, freq_hrs=12.0, score_floor=None,
        )
        t2 = db.save_dispatch_task(
            "tmpl", "qualify_job_listings", min_count=1, trigger_state="VALID_TITLE",
            auto_mode=False, batch_size=3, freq_hrs=0.0,
        )
        db.update_dispatch_task(t1, debug=1, skip_cache=1)
        keep = db.save_dispatch_task(
            "tgt", "fetch_website", min_count=9, trigger_state="WEBSITE_FOUND", auto_mode=False,
        )
        extra = db.save_dispatch_task(
            "tgt", "evaluate_jd", min_count=1, trigger_state="JD_READY",
        )
        self._stamp_runtime(db, keep, last_run_at="2020-01-01 00:00:00", batch_id="batch-old")
        self._stamp_runtime(db, extra, last_run_at="2020-02-02 00:00:00", batch_id="batch-extra")

        template_rows = db.list_dispatch_tasks_for_candidate("tmpl")
        stats = db.set_dispatch_tasks_from_template_rows("tgt", template_rows)
        assert stats == {"inserted": 1, "updated": 1, "deleted": 1, "count": 2}

        tgt = { (r["task_key"], r["trigger_state"]): r for r in db.list_dispatch_tasks_for_candidate("tgt") }
        assert set(tgt) == {("fetch_website", "WEBSITE_FOUND"), ("qualify_job_listings", "VALID_TITLE")}
        fw = tgt[("fetch_website", "WEBSITE_FOUND")]
        assert fw["auto_mode"] in (1, True)
        assert int(fw["min_count"]) == 2
        assert int(fw["batch_size"]) == 5
        assert float(fw["freq_hrs"]) == 12.0
        assert int(fw["debug"]) == 1
        assert int(fw["skip_cache"]) == 1
        assert fw["last_run_at"] is None
        assert fw["batch_id"] is None
        qjl = tgt[("qualify_job_listings", "VALID_TITLE")]
        assert qjl["last_run_at"] is None and qjl["batch_id"] is None
        assert db.get_dispatch_task(extra) is None

        # Idempotent re-run: update both, delete none, insert none; runtime stays cleared.
        self._stamp_runtime(db, fw["id"], last_run_at="2021-01-01 00:00:00", batch_id="batch-again")
        stats2 = db.set_dispatch_tasks_from_template_rows("tgt", template_rows)
        assert stats2 == {"inserted": 0, "updated": 2, "deleted": 0, "count": 2}
        again = db.get_dispatch_task(fw["id"])
        assert again is not None
        assert again["last_run_at"] is None and again["batch_id"] is None

    def test_empty_template_deletes_all_target_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_dispatch_task("tgt", "fetch_jd", min_count=1, trigger_state="PASSED_JOBLIST")
        stats = db.set_dispatch_tasks_from_template_rows("tgt", [])
        assert stats == {"inserted": 0, "updated": 0, "deleted": 1, "count": 0}
        assert db.list_dispatch_tasks_for_candidate("tgt") == []

    def test_blank_target_and_blank_task_key_raise(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match="candidate_id is required"):
            db.set_dispatch_tasks_from_template_rows("", [])
        with pytest.raises(ValueError, match="task_key"):
            db.set_dispatch_tasks_from_template_rows("tgt", [{"task_key": "  ", "min_count": 1}])


class TestAst882HomepageReadyClaimsWfr:
    """AST-882: primary prefilter/HOMEPAGE_READY row claims WEBSITE_FOUND_RETRY via retry_state."""

    def test_count_eligible_homepage_ready_unions_wfr(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "c882"
        db.save_company("hr", state="HOMEPAGE_READY", candidate_id=cid, company_name="hr")
        db.save_company("wfr", state="WEBSITE_FOUND_RETRY", candidate_id=cid, company_name="wfr")
        db.save_company("other", state="NEW", candidate_id=cid, company_name="other")
        task = {
            "entity_type": "company",
            "trigger_state": "HOMEPAGE_READY",
            "task_key": "prefilter",
            "candidate_id": cid,
        }
        assert db.count_eligible_for_dispatch_task(task) == 2

    def test_claim_company_batch_homepage_ready_and_wfr(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "c882b"
        db.save_company("hr", state="HOMEPAGE_READY", candidate_id=cid, company_name="hr")
        db.save_company("wfr", state="WEBSITE_FOUND_RETRY", candidate_id=cid, company_name="wfr")
        n = db.claim_company_batch(
            "batch-882",
            "HOMEPAGE_READY",
            10,
            candidate_id=cid,
            states=["HOMEPAGE_READY", "WEBSITE_FOUND_RETRY"],
        )
        assert n == 2
        rows = db.get_company_batch("batch-882")
        assert {r["short_name"] for r in rows} == {"hr", "wfr"}
