"""company_search_terms table sync, migration, last_scan_at (AST-524)."""

from __future__ import annotations

import pytest


class TestAst524CompanySearchTermsTable:
    def test_migrates_legacy_artifact_string_once(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c524-mig",
            state="NEW",
            candidate_data={"artifacts": {"company_search_terms": "  alpha \n\nbeta\n"}},
        )
        rows = db.list_company_search_terms("c524-mig")
        assert [r["search_term"] for r in rows] == ["alpha", "beta"]
        assert all(r["last_scan_at"] is None for r in rows)

    def test_migration_skips_when_table_already_has_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c524-skip",
            state="NEW",
            candidate_data={"artifacts": {"company_search_terms": "legacy\nterm"}},
        )
        db.sync_company_search_terms("c524-skip", ["table-only"])
        db.save_candidate(
            "c524-skip",
            state="NEW",
            candidate_data={"artifacts": {"company_search_terms": "legacy\nterm"}},
        )
        db._company_search_terms_migration_swept = False
        conn = db._get_connection()
        try:
            db._migrate_company_search_terms_from_artifacts(conn)
        finally:
            conn.close()
        rows = db.list_company_search_terms("c524-skip")
        assert [r["search_term"] for r in rows] == ["table-only"]

    def test_sync_upsert_and_delete(self, seeded_db) -> None:
        db = seeded_db
        db.sync_company_search_terms("cand-1", ["alpha", "beta"])
        db.sync_company_search_terms("cand-1", ["beta", "gamma"])
        terms = [r["search_term"] for r in db.list_company_search_terms("cand-1")]
        assert terms == ["beta", "gamma"]

    def test_sync_empty_clears_all_rows(self, seeded_db) -> None:
        db = seeded_db
        db.sync_company_search_terms("cand-1", ["only"])
        db.sync_company_search_terms("cand-1", [])
        assert db.list_company_search_terms("cand-1") == []

    def test_sync_preserves_last_scan_at_on_unchanged_term(self, seeded_db) -> None:
        db = seeded_db
        db.sync_company_search_terms("cand-1", ["keep", "drop"])
        db.update_company_search_term_last_scan_at("cand-1", "keep")
        before = next(r for r in db.list_company_search_terms("cand-1") if r["search_term"] == "keep")
        db.sync_company_search_terms("cand-1", ["keep", "new"])
        after = {r["search_term"]: r for r in db.list_company_search_terms("cand-1")}
        assert after["keep"]["last_scan_at"] == before["last_scan_at"]
        assert "drop" not in after
        assert after["new"]["last_scan_at"] is None

    def test_count_stale_company_search_terms(self, seeded_db) -> None:
        db = seeded_db
        db.sync_company_search_terms("cand-1", ["fresh", "never"])
        db.update_company_search_term_last_scan_at("cand-1", "fresh")
        conn = db._get_connection()
        try:
            conn.execute(
                """UPDATE company_search_terms SET last_scan_at = datetime('now', '-48 hours')
                   WHERE candidate_id = ? AND search_term = ?""",
                ("cand-1", "fresh"),
            )
            conn.commit()
        finally:
            conn.close()
        assert db.count_stale_company_search_terms("cand-1", 24.0) == 2
        assert db.count_stale_company_search_terms("cand-1", 0) == 0
        assert db.count_stale_company_search_terms("", 24.0) == 0

    def test_list_stale_company_search_terms_ordered(self, seeded_db) -> None:
        db = seeded_db
        db.sync_company_search_terms("cand-1", ["zebra", "alpha"])
        db.update_company_search_term_last_scan_at("cand-1", "zebra")
        conn = db._get_connection()
        try:
            conn.execute(
                """UPDATE company_search_terms SET last_scan_at = datetime('now', '-48 hours')
                   WHERE candidate_id = ? AND search_term = ?""",
                ("cand-1", "zebra"),
            )
            conn.commit()
        finally:
            conn.close()
        assert db.list_stale_company_search_terms("cand-1", 24.0) == ["alpha", "zebra"]
        assert db.list_stale_company_search_terms("cand-1", 0) == []
