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
