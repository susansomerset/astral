"""Component tests for agent_data table cluster (AST-392, AST-977)."""

from __future__ import annotations

import sqlite3
from typing import Any, Optional

import pytest


def _raw_row(db: Any, agent_data_id: str) -> Optional[tuple]:
    conn = db._get_connection()
    try:
        return conn.execute(
            "SELECT block_data, ref_agent_data_id FROM agent_data WHERE agent_data_id = ?",
            (agent_data_id,),
        ).fetchone()
    finally:
        conn.close()


def _agent_data_cols(db: Any) -> set[str]:
    conn = db._get_connection()
    try:
        return {row[1] for row in conn.execute("PRAGMA table_info(agent_data)").fetchall()}
    finally:
        conn.close()


class TestSaveAgentData:
    def test_rejects_invalid_block_type(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Invalid block_type"):
            sqlite_in_memory.save_agent_data(
                "id-1",
                "company",
                "qualify_job_listings",
                "batch-1",
                "NOT_A_BLOCK",
                "payload",
            )

    def test_saves_and_reads_batch_blocks(self, sqlite_in_memory) -> None:
        # AST-977: save returns outcome dict (was bool); callers still get plain text on read.
        db = sqlite_in_memory
        result = db.save_agent_data(
            "id-1", "company", "qualify_job_listings", "batch-1", "RESPONSE", "payload"
        )
        assert result["inserted"] is True
        assert result["outcome"] == "new_content"
        assert result["agent_data_id"] == "id-1"
        assert result["ref_agent_data_id"] is None
        rows = db.get_agent_data_by_batch("batch-1", block_type="RESPONSE")
        assert len(rows) == 1
        assert rows[0]["block_data"] == "payload"
        assert rows[0].get("ref_agent_data_id") in (None, "")


class TestAst977AgentDataSelfRefDedupe:
    """Branches: schema ensure; new vs ref write; transparent resolve; cycle/missing ref."""

    def test_ensure_schema_adds_ref_column_on_fresh_and_legacy(
        self, sqlite_in_memory, tmp_path, monkeypatch
    ) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            db._ensure_agent_data_schema(conn)
        finally:
            conn.close()
        assert "ref_agent_data_id" in _agent_data_cols(db)

        # Legacy table without the column — ALTER path after flag reset.
        legacy = tmp_path / "legacy"
        legacy.mkdir()
        monkeypatch.setenv("ASTRAL_DB_DIR", str(legacy))
        monkeypatch.setattr(db, "DB_PATH", legacy / "astral.db")
        db._agent_data_schema_ensured = False
        conn = sqlite3.connect(str(legacy / "astral.db"))
        try:
            conn.execute(
                """CREATE TABLE agent_data (
                    agent_data_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    task_key TEXT NOT NULL,
                    batch_id TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    block_type TEXT NOT NULL,
                    block_data BLOB,
                    token_size INTEGER DEFAULT 0
                )"""
            )
            conn.commit()
        finally:
            conn.close()
        conn2 = db._get_connection()
        try:
            db._ensure_agent_data_schema(conn2)
        finally:
            conn2.close()
        assert "ref_agent_data_id" in _agent_data_cols(db)

    def test_identical_write_refs_earliest_and_omits_payload(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        first = db.save_agent_data(
            "canon-1", "company", "qualify_job_listings", "batch-a", "SYSTEM", "same-body",
            created_at="2026-01-01T00:00:00+00:00",
        )
        assert first["outcome"] == "new_content"
        assert first["ref_agent_data_id"] is None
        raw_first = _raw_row(db, "canon-1")
        assert raw_first is not None
        assert raw_first[0] is not None  # compressed payload present
        assert raw_first[1] is None

        # Different block_type still matches on exact logical block_data only.
        second = db.save_agent_data(
            "audit-2", "company", "qualify_job_listings", "batch-b", "RESPONSE", "same-body",
            created_at="2026-01-02T00:00:00+00:00",
        )
        assert second == {
            "inserted": True,
            "outcome": "ref_existing",
            "agent_data_id": "audit-2",
            "ref_agent_data_id": "canon-1",
        }
        raw_second = _raw_row(db, "audit-2")
        assert raw_second is not None
        assert raw_second[0] is None  # omit duplicate payload
        assert raw_second[1] == "canon-1"

        # Third identical also points at earliest canonical, not the audit row.
        third = db.save_agent_data(
            "audit-3", "job", "evaluate_jd", "batch-c", "TASK", "same-body",
            created_at="2026-01-03T00:00:00+00:00",
        )
        assert third["outcome"] == "ref_existing"
        assert third["ref_agent_data_id"] == "canon-1"

    def test_reads_resolve_ref_to_plain_text(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_data(
            "canon-1", "company", "t", "batch-r", "SYSTEM", "hello-world",
            created_at="2026-01-01T00:00:00+00:00",
        )
        db.save_agent_data(
            "audit-2", "company", "t", "batch-r", "RESPONSE", "hello-world",
            created_at="2026-01-02T00:00:00+00:00",
        )

        by_id = db.get_agent_data("audit-2")
        assert by_id is not None
        assert by_id["block_data"] == "hello-world"
        assert by_id["ref_agent_data_id"] == "canon-1"

        by_batch = db.get_agent_data_by_batch("batch-r")
        payloads = {row["agent_data_id"]: row["block_data"] for row in by_batch}
        assert payloads["canon-1"] == "hello-world"
        assert payloads["audit-2"] == "hello-world"

        by_ids = db.get_agent_data_for_ids(["audit-2", "canon-1"])
        assert by_ids["audit-2"]["block_data"] == "hello-world"
        assert by_ids["canon-1"]["block_data"] == "hello-world"

    def test_duplicate_primary_key_returns_duplicate_id(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        first = db.save_agent_data(
            "same-id", "company", "t", "batch-d", "SYSTEM", "once",
        )
        assert first["outcome"] == "new_content"
        again = db.save_agent_data(
            "same-id", "company", "t", "batch-d", "SYSTEM", "once",
        )
        assert again == {
            "inserted": False,
            "outcome": "duplicate_id",
            "agent_data_id": "same-id",
            "ref_agent_data_id": None,
        }

    def test_resolve_raises_on_missing_ref_and_cycle(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn0 = db._get_connection()
        try:
            db._ensure_agent_data_schema(conn0)
        finally:
            conn0.close()
        conn = db._get_connection()
        try:
            conn.execute(
                """INSERT INTO agent_data
                   (agent_data_id, entity_type, task_key, batch_id, created_at,
                    block_type, block_data, token_size, ref_agent_data_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "missing-ref", "company", "t", "batch-x",
                    "2026-01-01T00:00:00+00:00", "SYSTEM", None, 0, "does-not-exist",
                ),
            )
            conn.execute(
                """INSERT INTO agent_data
                   (agent_data_id, entity_type, task_key, batch_id, created_at,
                    block_type, block_data, token_size, ref_agent_data_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?), (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "cycle-a", "company", "t", "batch-y",
                    "2026-01-01T00:00:00+00:00", "SYSTEM", None, 0, "cycle-b",
                    "cycle-b", "company", "t", "batch-y",
                    "2026-01-02T00:00:00+00:00", "SYSTEM", None, 0, "cycle-a",
                ),
            )
            conn.commit()
        finally:
            conn.close()

        with pytest.raises(ValueError, match="ref target missing"):
            db.get_agent_data("missing-ref")
        with pytest.raises(ValueError, match="ref cycle"):
            db.get_agent_data("cycle-a")

def _insert_content_row(
    db,
    *,
    agent_data_id: str,
    plain: str,
    created_at: str,
    ref_agent_data_id=None,
    block_data_override=None,
) -> bytes:
    """Insert a legacy-style content row (both payload present) for backfill seeding."""
    blob = block_data_override if block_data_override is not None else db._compress_payload(plain)
    conn = db._get_connection()
    try:
        db._ensure_agent_data_schema(conn)
        conn.execute(
            """INSERT INTO agent_data
               (agent_data_id, entity_type, task_key, batch_id, created_at,
                block_type, block_data, token_size, ref_agent_data_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                agent_data_id, "company", "qualify_job_listings", "batch-978",
                created_at, "SYSTEM", blob, 0, ref_agent_data_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return blob


class TestAst978BackfillAgentDataRefs:
    """Branches: dry-run vs live; canonical untouched; already_ref; idempotent; payload intact."""

    def test_dry_run_would_set_ref_without_writing(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        blob = _insert_content_row(
            db, agent_data_id="early", plain="dup-body",
            created_at="2026-01-01T00:00:00+00:00",
        )
        _insert_content_row(
            db, agent_data_id="late", plain="dup-body",
            created_at="2026-01-02T00:00:00+00:00",
        )
        result = db.backfill_agent_data_refs(dry_run=True)
        assert result["scanned"] == 2
        assert result["updated"] == 1
        assert result["unchanged"] == 1
        by_id = {a["agent_data_id"]: a for a in result["actions"]}
        assert by_id["early"]["outcome"] == "canonical_or_unique"
        assert by_id["late"] == {
            "agent_data_id": "late",
            "outcome": "would_set_ref",
            "ref_agent_data_id": "early",
        }
        # No writes on dry-run
        conn = db._get_connection()
        try:
            rows = {
                r[0]: (r[1], r[2])
                for r in conn.execute(
                    "SELECT agent_data_id, block_data, ref_agent_data_id FROM agent_data"
                ).fetchall()
            }
        finally:
            conn.close()
        assert rows["early"][1] is None
        assert rows["late"][1] is None
        assert rows["late"][0] == blob

    def test_live_sets_ref_leaves_block_data_and_is_idempotent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        blob = _insert_content_row(
            db, agent_data_id="early", plain="dup-body",
            created_at="2026-01-01T00:00:00+00:00",
        )
        _insert_content_row(
            db, agent_data_id="late", plain="dup-body",
            created_at="2026-01-02T00:00:00+00:00",
        )
        # Unique content stays canonical
        _insert_content_row(
            db, agent_data_id="solo", plain="unique-body",
            created_at="2026-01-03T00:00:00+00:00",
        )
        live = db.backfill_agent_data_refs(dry_run=False)
        assert live["updated"] == 1
        assert live["unchanged"] == 2
        by_id = {a["agent_data_id"]: a for a in live["actions"]}
        assert by_id["late"]["outcome"] == "set_ref"
        assert by_id["late"]["ref_agent_data_id"] == "early"
        assert by_id["early"]["outcome"] == "canonical_or_unique"
        assert by_id["solo"]["outcome"] == "canonical_or_unique"

        conn = db._get_connection()
        try:
            rows = {
                r[0]: (r[1], r[2])
                for r in conn.execute(
                    "SELECT agent_data_id, block_data, ref_agent_data_id FROM agent_data"
                ).fetchall()
            }
        finally:
            conn.close()
        assert rows["early"] == (blob, None)
        assert rows["late"][0] == blob  # payload unchanged
        assert rows["late"][1] == "early"
        assert rows["solo"][1] is None

        again = db.backfill_agent_data_refs(dry_run=False)
        # late now already_ref (has ref + still has block_data); early+solo unchanged
        assert again["updated"] == 0
        assert again["skipped_already_ref"] == 1
        assert again["unchanged"] == 2

    def test_skips_already_ref_and_records_decompress_error(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _insert_content_row(
            db, agent_data_id="canon", plain="shared",
            created_at="2026-01-01T00:00:00+00:00",
        )
        _insert_content_row(
            db, agent_data_id="pre-ref", plain="shared",
            created_at="2026-01-02T00:00:00+00:00",
            ref_agent_data_id="canon",
        )
        _insert_content_row(
            db, agent_data_id="bad-blob", plain="x",
            created_at="2026-01-03T00:00:00+00:00",
            block_data_override=b"not-valid-zlib",
        )
        result = db.backfill_agent_data_refs(dry_run=False)
        by_id = {a["agent_data_id"]: a for a in result["actions"]}
        assert by_id["pre-ref"]["outcome"] == "already_ref"
        assert by_id["bad-blob"]["outcome"] == "error"
        assert result["errors"] == 1
        assert result["skipped_already_ref"] == 1


class TestAst1274ResolveNullBlockDataRef:
    """AST-1274: null/empty local + populated ref resolves; populated ref always follows chain."""

    def test_empty_string_block_data_with_ref_resolves(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_data(
            "canon-1", "company", "t", "batch-1274", "SYSTEM", "canonical-body",
            created_at="2026-01-01T00:00:00+00:00",
        )
        conn = db._get_connection()
        try:
            db._ensure_agent_data_schema(conn)
            # Empty BLOB (not NULL) + populated ref — must follow, not return blank.
            conn.execute(
                """INSERT INTO agent_data
                   (agent_data_id, entity_type, task_key, batch_id, created_at,
                    block_type, block_data, token_size, ref_agent_data_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "alias-empty", "company", "t", "batch-1274",
                    "2026-01-02T00:00:00+00:00", "RESPONSE", "", 0, "canon-1",
                ),
            )
            conn.commit()
        finally:
            conn.close()

        by_id = db.get_agent_data("alias-empty")
        assert by_id is not None
        assert by_id["block_data"] == "canonical-body"
        by_ids = db.get_agent_data_for_ids(["alias-empty"])
        assert by_ids["alias-empty"]["block_data"] == "canonical-body"


    def test_populated_ref_follows_chain_even_with_local_body(self, sqlite_in_memory) -> None:
        # Resolve discuss: product dropped has_local — populated ref always wins (plan Stage 1).
        db = sqlite_in_memory
        db.save_agent_data(
            "canon-1", "company", "t", "batch-1274b", "SYSTEM", "from-ref",
            created_at="2026-01-01T00:00:00+00:00",
        )
        _insert_content_row(
            db,
            agent_data_id="alias-local",
            plain="from-local",
            created_at="2026-01-02T00:00:00+00:00",
            ref_agent_data_id="canon-1",
        )
        row = db.get_agent_data("alias-local")
        assert row is not None
        assert row["block_data"] == "from-ref"
        assert row["ref_agent_data_id"] == "canon-1"
