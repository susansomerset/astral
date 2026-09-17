"""meteorite staging table + claim/insert/update/retention helpers (AST-1557)."""

from __future__ import annotations

import pytest

from src.utils.config import METEORITE_STATES, METEORITE_STATES_RETENTION


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
    """Fan-out insert forces NEW; empty list is a no-op."""

    def test_insert_n_rows_forces_new_and_unclaimed(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        ids = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "c1",
                    "source_kind": "email",
                    "source_id": "mid-a",
                    "content": "jd-1",
                    "state": "READY",  # ignored — force NEW
                },
                {
                    "candidate_id": "c1",
                    "source_kind": "email",
                    "source_id": "mid-a",
                    "link": "https://example.com/job",
                    "classify_outcome": "link",
                },
            ]
        )
        assert len(ids) == 2
        assert ids[0] != ids[1]
        for mid in ids:
            row = db.get_meteorite(mid)
            assert row is not None
            assert row["state"] == "NEW"
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
        db.update_meteorite(b, state="ERROR")
        n = db.claim_meteorite_batch(
            "union-batch",
            "NEW",
            10,
            states=["NEW", "ERROR"],
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
                {"candidate_id": "c", "source_kind": "email", "source_id": "m1"},
                {"candidate_id": "c", "source_kind": "email", "source_id": "m2"},
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
            [{"candidate_id": "c", "source_kind": "email", "source_id": "m"}]
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
            [{"candidate_id": "c", "source_kind": "email", "source_id": "old"}]
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
            [{"candidate_id": "c", "source_kind": "email", "source_id": "fresh"}]
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
