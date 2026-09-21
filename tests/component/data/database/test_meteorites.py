"""meteorite staging table + claim/insert/update/retention helpers (AST-1557)."""

from __future__ import annotations

import pytest

from src.utils.config import METEORITE_CONFIG, METEORITE_STATES, METEORITE_STATES_RETENTION


class TestAst1557MeteoriteSchema:
    """Fresh CREATE + indexes for the meteorite staging spine."""

    def test_ensure_creates_columns_and_indexes(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db._meteorite_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_meteorite_schema(conn)
            cols = {r[1]: r for r in conn.execute("PRAGMA table_info(meteorite)").fetchall()}
            for name in (
                "id",
                "candidate_id",
                "source_kind",
                "source_id",
                "source_ref",
                "state",
                "content",
                "classify_outcome",
                "link",
                "astral_job_id",
                "estelle_thread_ts",
                "estelle_notified_at",
                "nag_count",
                "error",
                "batch_id",
                "batch_created_at",
                "created_at",
                "updated_at",
                "state_changed_at",
            ):
                assert name in cols, name
            assert cols["batch_id"][3] == 0  # nullable
            assert cols["batch_created_at"][3] == 0
            idx = {
                r[1]
                for r in conn.execute("PRAGMA index_list(meteorite)").fetchall()
            }
            assert "idx_meteorite_state_batch" in idx
            assert "idx_meteorite_source" in idx
        finally:
            conn.close()


class TestAst1557InsertMeteoriteRows:
    """Fan-out insert persists caller state (AST-1713); empty list is a no-op."""

    def test_insert_n_rows_persists_caller_state_and_unclaimed(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        ids = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "c1",
                    "source_kind": "email",
                    "source_id": "mid-a",
                    "content": "jd-1",
                    "state": "READY",
                },
                {
                    "candidate_id": "c1",
                    "source_kind": "email",
                    "source_id": "mid-a",
                    "link": "https://example.com/job",
                    "classify_outcome": "link",
                    "state": "NEW",
                },
            ]
        )
        assert len(ids) == 2
        assert ids[0] != ids[1]
        assert db.get_meteorite(ids[0])["state"] == "READY"
        assert db.get_meteorite(ids[1])["state"] == "NEW"
        for mid in ids:
            row = db.get_meteorite(mid)
            assert row is not None
            assert not row.get("batch_id")
            assert row["nag_count"] == 0
            assert row["created_at"]
            assert row["updated_at"]
            assert row["state_changed_at"]
        by_src = db.list_meteorites_by_source("email", "mid-a")
        assert {r["id"] for r in by_src} == set(ids)

    def test_empty_rows_returns_empty(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.insert_meteorite_rows([]) == []


class TestAst1557MeteoriteBatchClaim:
    """Claim → get → clear pool parity with candidate/job batch helpers."""

    def _seed_new(self, db, n: int, *, state: str = "NEW") -> list[int]:
        ids = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "c1557",
                    "source_kind": "email",
                    "source_id": f"mid-{i}",
                    "state": "NEW",
                }
                for i in range(n)
            ]
        )
        if state != "NEW":
            for mid in ids:
                db.update_meteorite(mid, state=state)
        return ids

    def test_claim_get_clear_multi_row_pool(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_new(db, 3)
        n = db.claim_meteorite_batch("meteorite-batch-a", "NEW", 2)
        assert n == 2
        rows = db.get_meteorite_batch("meteorite-batch-a")
        assert len(rows) == 2
        for r in rows:
            assert r["batch_id"] == "meteorite-batch-a"
            assert r.get("batch_created_at")
        # Concurrent claim cannot steal locked rows
        n2 = db.claim_meteorite_batch("meteorite-batch-b", "NEW", 2)
        assert n2 == 1  # one unclaimed left
        assert len(db.get_meteorite_batch("meteorite-batch-b")) == 1
        cleared = db.clear_meteorite_batch("meteorite-batch-a")
        assert cleared == 2
        for r in db.get_meteorite_batch("meteorite-batch-a"):
            assert False, "batch should be empty after clear"
        # Released rows reclaimable
        n3 = db.claim_meteorite_batch("meteorite-reclaim", "NEW", 10)
        assert n3 == 2

    def test_claim_unions_states(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        a = self._seed_new(db, 1)[0]
        b = self._seed_new(db, 1)[0]
        # ERROR retired — SCRAPE_ERROR is a live union peer of NEW.
        db.update_meteorite(b, state="SCRAPE_ERROR")
        n = db.claim_meteorite_batch(
            "union-batch",
            "NEW",
            10,
            states=["NEW", "SCRAPE_ERROR"],
        )
        assert n == 2
        ids = {r["id"] for r in db.get_meteorite_batch("union-batch")}
        assert ids == {a, b}


class TestAst1557MeteoriteReadUpdate:
    """get / list-by-state / update whitelist + state key gate (no prior_states)."""

    def test_list_by_state_and_get_missing(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        ids = db.insert_meteorite_rows(
            [
                {"candidate_id": "c", "source_kind": "email", "source_id": "m1",
                    "state": "NEW",
                },
                {"candidate_id": "c", "source_kind": "email", "source_id": "m2",
                    "state": "NEW",
                },
            ]
        )
        db.update_meteorite(ids[1], state="READY")
        assert [r["id"] for r in db.list_meteorites_by_state("NEW")] == [ids[0]]
        assert [r["id"] for r in db.list_meteorites_by_state("READY")] == [ids[1]]
        assert len(db.list_meteorites_by_state("NEW", limit=1)) == 1
        assert db.get_meteorite(999999) is None

    def test_update_whitelist_and_unknown_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        mid = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "m",
                    "state": "NEW",
                }]
        )[0]
        before = db.get_meteorite(mid)
        assert before is not None
        db.update_meteorite(mid, state="SCRAPE_LINK", link="https://x", error="retry")
        after = db.get_meteorite(mid)
        assert after is not None
        assert after["state"] == "SCRAPE_LINK"
        assert after["link"] == "https://x"
        assert after["error"] == "retry"
        assert after["state_changed_at"] >= before["state_changed_at"]
        # Data layer does not enforce prior_states — BOT_BLOCKED from NEW is allowed here
        db.update_meteorite(mid, state="BOT_BLOCKED")
        assert db.get_meteorite(mid)["state"] == "BOT_BLOCKED"
        with pytest.raises(ValueError, match="unknown meteorite state"):
            db.update_meteorite(mid, state="NOT_A_STATE")
        with pytest.raises(ValueError, match="unknown meteorite fields"):
            db.update_meteorite(mid, batch_id="nope")


class TestAst1557MeteoriteRetention:
    """Retention select by states+cutoff; delete by ids (caller owns day math)."""

    def test_list_for_retention_and_delete(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        mid = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "old",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(mid, state="LANDED")
        # Force an old state_changed_at so retention cutoff can match
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE meteorite SET state_changed_at = ? WHERE id = ?",
                ("2000-01-01T00:00:00+00:00", mid),
            )
            conn.commit()
        finally:
            conn.close()
        fresh = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "fresh",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(fresh, state="LANDED")

        purge_states = list(METEORITE_STATES_RETENTION["purge_states"])
        assert set(purge_states) <= set(METEORITE_STATES)
        hit = db.list_meteorites_for_retention(
            states=purge_states,
            older_than="2010-01-01T00:00:00+00:00",
        )
        assert [r["id"] for r in hit] == [mid]

        assert db.delete_meteorites_by_ids([]) == 0
        n = db.delete_meteorites_by_ids([mid])
        assert n == 1
        assert db.get_meteorite(mid) is None
        assert db.get_meteorite(fresh) is not None

@pytest.mark.skipif(
    "electronic_contact_column" not in METEORITE_CONFIG,
    reason="AST-1689 electronic_contact column not on this publish tip",
)
class TestAst1689ElectronicContactColumn:
    """AST-1689: meteorite electronic_contact column + allowlist + insert bind."""

    def test_ensure_creates_electronic_contact_column(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db._meteorite_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_meteorite_schema(conn)
            cols = {r[1] for r in conn.execute("PRAGMA table_info(meteorite)").fetchall()}
            col = METEORITE_CONFIG["electronic_contact_column"]
            assert col == "electronic_contact"
            assert col in cols
            assert col in db._UPDATE_METEORITE_ALLOWED
        finally:
            conn.close()

    def test_alter_adds_column_on_legacy_table(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        col = METEORITE_CONFIG["electronic_contact_column"]
        conn = db._get_connection()
        try:
            conn.execute("DROP TABLE IF EXISTS meteorite")
            # Minimal pre-AST-1689 shape (no electronic_contact).
            conn.execute(
                """
                CREATE TABLE meteorite (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_ref TEXT,
                    state TEXT NOT NULL,
                    content TEXT,
                    classify_outcome TEXT,
                    link TEXT,
                    astral_job_id TEXT,
                    estelle_thread_ts TEXT,
                    estelle_notified_at TEXT,
                    nag_count INTEGER DEFAULT 0,
                    error TEXT,
                    batch_id TEXT,
                    batch_created_at TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    state_changed_at TEXT
                )
                """
            )
            conn.commit()
            db._meteorite_schema_ensured = False
            db._ensure_meteorite_schema(conn)
            cols = {r[1] for r in conn.execute("PRAGMA table_info(meteorite)").fetchall()}
            assert col in cols
        finally:
            conn.close()

    def test_insert_binds_contact_or_null(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        col = METEORITE_CONFIG["electronic_contact_column"]
        ids = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "c1689",
                    "source_kind": "email",
                    "source_id": "mid-contact",
                    "content": "jd",
                    col: "hiring@example.com",
                    "state": "NEW",
                },
                {
                    "candidate_id": "c1689",
                    "source_kind": "email",
                    "source_id": "mid-empty",
                    "content": "jd2",
                    "state": "NEW",
                },
            ]
        )
        assert db.get_meteorite(ids[0])[col] == "hiring@example.com"
        assert db.get_meteorite(ids[1]).get(col) in (None, "")

    def test_update_allowlist_accepts_contact(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        col = METEORITE_CONFIG["electronic_contact_column"]
        mid = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "m",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(mid, **{col: "ops@example.com"})
        assert db.get_meteorite(mid)[col] == "ops@example.com"

class TestAst1694GetMeteoriteLinkByAstralJobId:
    """AST-1694: link-only reverse lookup (not full-row provenance)."""

    def test_blank_id_returns_none(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.get_meteorite_link_by_astral_job_id(None) is None  # type: ignore[arg-type]
        assert db.get_meteorite_link_by_astral_job_id("") is None
        assert db.get_meteorite_link_by_astral_job_id("   ") is None

    def test_hit_miss_blank_link_and_newest_wins(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.get_meteorite_link_by_astral_job_id("job-miss") is None
        older = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "old-link",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(
            older, state="LANDED", astral_job_id="job-1694", link="https://old.example/j"
        )
        newer = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "new-link",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(
            newer, state="LANDED", astral_job_id="job-1694", link="https://new.example/j"
        )
        assert db.get_meteorite_link_by_astral_job_id("job-1694") == "https://new.example/j"
        blank = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "blank-link",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(blank, state="LANDED", astral_job_id="job-blank", link="  ")
        assert db.get_meteorite_link_by_astral_job_id("job-blank") is None

class TestAst1691GetMeteoriteByAstralJobId:
    """AST-1691: reverse-link get_meteorite_by_astral_job_id (newest id wins)."""

    def test_blank_id_returns_none_without_row(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.get_meteorite_by_astral_job_id(None) is None  # type: ignore[arg-type]
        assert db.get_meteorite_by_astral_job_id("") is None
        assert db.get_meteorite_by_astral_job_id("   ") is None

    def test_hit_and_miss_and_newest_wins(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.get_meteorite_by_astral_job_id("job-miss") is None
        older = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "old-link",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(older, state="LANDED", astral_job_id="job-1691")
        newer = db.insert_meteorite_rows(
            [{"candidate_id": "c", "source_kind": "email", "source_id": "new-link",
                    "state": "NEW",
                }]
        )[0]
        db.update_meteorite(
            newer,
            state="LANDED",
            astral_job_id="job-1691",
            link="https://jobs.example/1691",
            classify_outcome="ok",
            content="jd body",
        )
        row = db.get_meteorite_by_astral_job_id("job-1691")
        assert row is not None
        assert row["id"] == newer
        assert row["link"] == "https://jobs.example/1691"
        assert row["classify_outcome"] == "ok"
        assert row["content"] == "jd body"
        assert row["state"] == "LANDED"


class TestAst1748ListMeteoritesForCandidate:
    """AST-1748: candidate-scoped list ordered by state_changed_at DESC."""

    def test_blank_candidate_returns_empty_without_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.list_meteorites_for_candidate(None) == []  # type: ignore[arg-type]
        assert db.list_meteorites_for_candidate("") == []
        assert db.list_meteorites_for_candidate("   ") == []

    def test_scopes_to_candidate_and_orders_by_state_changed_at_desc(
        self, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        a_old = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "cand-A",
                    "source_kind": "email",
                    "source_id": "a-old",
                    "state": "READY",
                    "job_title": "Old A",
                }
            ]
        )[0]
        a_new = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "cand-A",
                    "source_kind": "email",
                    "source_id": "a-new",
                    "state": "LANDED",
                    "link": "not-a-url",
                }
            ]
        )[0]
        b_only = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "cand-B",
                    "source_kind": "email",
                    "source_id": "b-only",
                    "state": "NEW",
                }
            ]
        )[0]
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE meteorite SET state_changed_at = ? WHERE id = ?",
                ("2020-01-01T00:00:00+00:00", a_old),
            )
            conn.execute(
                "UPDATE meteorite SET state_changed_at = ? WHERE id = ?",
                ("2024-06-01T00:00:00+00:00", a_new),
            )
            conn.commit()
        finally:
            conn.close()

        rows = db.list_meteorites_for_candidate("cand-A")
        assert [r["id"] for r in rows] == [a_new, a_old]
        assert all(r["candidate_id"] == "cand-A" for r in rows)
        assert b_only not in {r["id"] for r in rows}
        assert rows[0]["link"] == "not-a-url"
        assert db.list_meteorites_for_candidate("cand-empty") == []
