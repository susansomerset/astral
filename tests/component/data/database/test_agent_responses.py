"""Component tests for agent_data latest-refs (entity agent_responses column retired).

AST-981 removed standalone-table insert/list I/O.
AST-982 drops the standalone table at bootstrap.
AST-984 drops entity JSON columns; latest-per-task via list_entity_latest_agent_refs.
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
        # AST-984: entity-column upsert removed too
        assert not hasattr(db_mod, "append_agent_response")

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
        db._entity_agent_responses_column_sunset_applied = False
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
            # AST-984: entity JSON column gone after ensure_* schema.
            cols = {r[1] for r in conn.execute("PRAGMA table_info(company)").fetchall()}
            assert "agent_responses" not in cols
        finally:
            conn.close()


class TestAst984EntityColumnRetired:
    """AST-984: no append_agent_response; latest refs from agent_data.entity_id."""

    def test_append_and_column_helpers(self) -> None:
        assert not hasattr(db_mod, "append_agent_response")
        assert hasattr(db_mod, "list_entity_latest_agent_refs")
        assert hasattr(db_mod, "ensure_batch_response_entity_ids")
        assert hasattr(db_mod, "_drop_entity_agent_responses_column")
        assert hasattr(db_mod, "_entity_agent_responses_column_sunset_applied")

    def test_list_latest_per_task_key(self, seeded_db) -> None:
        db = seeded_db
        db.save_job("job-984", company="acme", state="NEW")
        # Shared prompt blocks (no entity_id) + RESPONSE rows tagged per entity.
        db.save_agent_data(
            agent_data_id="b1-sys",
            entity_type="job",
            task_key="consult_get",
            batch_id="b1",
            block_type="SYSTEM",
            block_data="sys-1",
            token_size=1,
            created_at="2026-06-01 00:00:00",
        )
        db.save_agent_data(
            agent_data_id="b1-resp",
            entity_type="job",
            task_key="consult_get",
            batch_id="b1",
            block_type="RESPONSE",
            block_data="old-get",
            token_size=1,
            created_at="2026-06-01 00:00:00",
            entity_id="job-984",
        )
        db.save_agent_data(
            agent_data_id="b2-resp",
            entity_type="job",
            task_key="consult_do",
            batch_id="b2",
            block_type="RESPONSE",
            block_data="do-body",
            token_size=1,
            created_at="2026-06-01 00:00:00",
            entity_id="job-984",
        )
        db.save_agent_data(
            agent_data_id="b3-resp",
            entity_type="job",
            task_key="consult_get",
            batch_id="b3",
            block_type="RESPONSE",
            block_data="new-get",
            token_size=1,
            created_at="2026-06-02 00:00:00",
            entity_id="job-984",
        )
        refs = db.list_entity_latest_agent_refs("job", "job-984")
        by_task = {r["task_key"]: r for r in refs}
        assert set(by_task) == {"consult_get", "consult_do"}
        assert by_task["consult_get"]["batch_id"] == "b3"
        # prompt_blocks: non-RESPONSE from batch + this RESPONSE id only
        get_blocks = by_task["consult_get"]["prompt_blocks"]
        assert {"type": "RESPONSE", "id": "b3-resp"} in get_blocks
        assert {"type": "RESPONSE", "id": "b1-resp"} not in get_blocks

    def test_seeded_entity_rows_have_no_agent_responses_column(self, seeded_db) -> None:
        db = seeded_db
        conn = db._get_connection()
        try:
            for table in ("company", "job", "candidate"):
                cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
                assert "agent_responses" not in cols, table
        finally:
            conn.close()

    def test_ensure_batch_response_entity_ids_tags_copies(self, seeded_db) -> None:
        db = seeded_db
        db.save_job("job-a", company="acme", state="NEW")
        db.save_job("job-b", company="acme", state="NEW")
        db.save_agent_data(
            agent_data_id="batch-x-response",
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-x",
            block_type="RESPONSE",
            block_data="shared",
            token_size=2,
            created_at="2026-06-03 00:00:00",
        )
        db.ensure_batch_response_entity_ids(
            "job",
            ["job-a", "job-b"],
            {
                "task_key": "evaluate_jd",
                "batch_id": "batch-x",
                "created_at": "2026-06-03 00:00:00",
                "prompt_blocks": [{"type": "RESPONSE", "id": "batch-x-response"}],
            },
        )
        refs_a = db.list_entity_latest_agent_refs("job", "job-a")
        refs_b = db.list_entity_latest_agent_refs("job", "job-b")
        assert len(refs_a) == 1 and refs_a[0]["task_key"] == "evaluate_jd"
        assert len(refs_b) == 1 and refs_b[0]["task_key"] == "evaluate_jd"
