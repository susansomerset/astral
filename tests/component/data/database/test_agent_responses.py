"""Component tests for agent_responses (entity column; standalone table retired).

AST-981 removed standalone-table insert/list I/O.
AST-982 drops the table at bootstrap (`_apply_agent_responses_table_sunset`);
entity-column latest-only upserts stay until AST-984.
"""

from __future__ import annotations

import pytest

import src.data.database as db_mod


class TestAst981StandaloneTableIoRetired:
    """AST-981: data layer no longer exposes standalone-table create/read helpers."""

    def test_add_and_list_helpers_removed(self) -> None:
        assert not hasattr(db_mod, "add_agent_response_entry")
        assert not hasattr(db_mod, "list_agent_responses")
        assert not hasattr(db_mod, "_derive_agent_status")
        assert hasattr(db_mod, "append_agent_response")

    def test_hard_delete_candidate_skips_standalone_table_key(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c981", state="NEW_CANDIDATE")
        counts = db.hard_delete_candidate("c981")
        assert "agent_responses" not in counts
        assert counts["candidate"] == 1


class TestAst982StandaloneTableSunset:
    """AST-982: DROP TABLE at bootstrap; no CREATE/ensure/registry recreation."""

    def test_ensure_and_registry_symbols_removed(self) -> None:
        assert not hasattr(db_mod, "_ensure_agent_responses_schema")
        assert not hasattr(db_mod, "_agent_responses_schema_ensured")
        assert "agent_responses" not in db_mod._UPSERT_SCHEMA_ENSURE_FLAGS
        assert "agent_responses" not in db_mod._UPSERT_LAZY_SCHEMA_HANDLERS
        assert hasattr(db_mod, "_apply_agent_responses_table_sunset")
        assert hasattr(db_mod, "_agent_responses_table_sunset_applied")

    def test_bootstrap_drops_legacy_table_and_does_not_recreate(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            conn.execute(
                """
                CREATE TABLE agent_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_key TEXT,
                    entity_type TEXT,
                    entity_id TEXT,
                    created_at TEXT
                )
                """
            )
            conn.commit()
            tables = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            assert "agent_responses" in tables
        finally:
            conn.close()

        db._agent_responses_table_sunset_applied = False
        db.ensure_all_upsert_registry_schemas_at_startup()

        conn = db._get_connection()
        try:
            tables = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            assert "agent_responses" not in tables
        finally:
            conn.close()

        # Second bootstrap must not recreate the standalone table.
        db.ensure_all_upsert_registry_schemas_at_startup()
        conn = db._get_connection()
        try:
            tables = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            assert "agent_responses" not in tables
            # Entity JSON column on company still exists after registry ensures.
            cols = {r[1] for r in conn.execute("PRAGMA table_info(company)").fetchall()}
            assert "agent_responses" in cols
        finally:
            conn.close()


class TestAst726AppendAgentResponseUpsert:
    """AST-726: entity agent_responses refs upsert by task_key — latest wins."""

    def test_upserts_by_task_key_preserves_other_keys(self, seeded_db) -> None:
        db = seeded_db
        db.save_job("job-726", company="acme", state="NEW")
        db.append_agent_response(
            "job",
            "job-726",
            {"task_key": "consult_get", "created_at": "2026-06-01 00:00:00", "batch_id": "b1"},
        )
        db.append_agent_response(
            "job",
            "job-726",
            {"task_key": "consult_do", "created_at": "2026-06-01 00:00:00", "batch_id": "b2"},
        )
        db.append_agent_response(
            "job",
            "job-726",
            {"task_key": "consult_get", "created_at": "2026-06-02 00:00:00", "batch_id": "b3"},
        )
        refs = db.get_job("job-726")["agent_responses"]
        assert len(refs) == 2
        assert [r["task_key"] for r in refs] == ["consult_do", "consult_get"]
        assert refs[1]["batch_id"] == "b3"

    def test_rejects_missing_task_key(self, seeded_db) -> None:
        db = seeded_db
        db.save_job("job-726", company="acme", state="NEW")
        with pytest.raises(ValueError, match="missing task_key"):
            db.append_agent_response("job", "job-726", {"batch_id": "orphan"})
