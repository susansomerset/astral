"""Component tests for agent_task table cluster (AST-392, AST-454, AST-738)."""

from __future__ import annotations

import sqlite3

import pytest

from scripts.migrations.backfill_task_grouping_metadata import (
    backfill_task_grouping_metadata,
    seed_values_for_task_key,
)

TASK_KEY_QJL = "qualify_job_listings"
TASK_KEY_CRAFT = "craft_resume_base"

# placeholder removed = "qualify_job_listings"


class TestSaveAgentTask:
    def test_saves_and_reads_task(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_QJL, agent_id="agent-1", user_prompt="prompt")
        row = db.get_agent_task(TASK_KEY_QJL)
        assert row is not None
        assert row["agent_id"] == "agent-1"
        assert row["user_prompt"] == "prompt"


# AST-454: seven prompt segments (system; cache blocks A–D; no-cache; user) + versioning.
class TestAst454SevenSegmentPersistence:
    def test_seven_segment_round_trip_and_len_fields(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(
            TASK_KEY_QJL,
            agent_id="agent-1",
            system_prompt="sys",
            cache_prompt="block-a",
            cache_prompt_b=" block-b ",
            cache_prompt_c="block-c",
            cache_prompt_d="block-d",
            nocache_prompt="noc",
            user_prompt="user",
        )
        row = db.get_agent_task(TASK_KEY_QJL)
        assert row is not None
        assert row["system_prompt"] == "sys"
        assert row["cache_prompt"] == "block-a"
        assert row["cache_prompt_b"] == "block-b"
        assert row["cache_prompt_c"] == "block-c"
        assert row["cache_prompt_d"] == "block-d"
        assert row["nocache_prompt"] == "noc"
        assert row["user_prompt"] == "user"
        listed = db.list_candidate_tasks()
        ours = next(t for t in listed if t["task_key"] == TASK_KEY_QJL)
        assert ours["cache_prompt_len"] == len("block-a")
        assert ours["cache_prompt_b_len"] == len("block-b")
        assert ours["cache_prompt_c_len"] == len("block-c")
        assert ours["cache_prompt_d_len"] == len("block-d")

    def test_segment_edit_versions_row_prior_retired(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_QJL, agent_id="agent-1", user_prompt="v1-user", cache_prompt="v1-ca")
        row1 = db.get_agent_task(TASK_KEY_QJL)
        assert row1["user_prompt"] == "v1-user"
        uuid1 = row1["task_key_uuid"]
        db.save_agent_task(TASK_KEY_QJL, user_prompt="v2-user")
        row2 = db.get_agent_task(TASK_KEY_QJL)
        assert row2["user_prompt"] == "v2-user"
        assert row2["cache_prompt"] == "v1-ca"
        assert row2["task_key_uuid"] != uuid1
        conn = db._get_connection()
        try:
            currents = conn.execute(
                "SELECT task_key_uuid, current FROM agent_task WHERE task_key = ? ORDER BY current DESC",
                (TASK_KEY_QJL,),
            ).fetchall()
            assert len(currents) == 2
            assert {currents[0][1], currents[1][1]} == {0, 1}
            fresh = conn.execute(
                "SELECT COUNT(*) FROM agent_task WHERE task_key = ? AND current = 1",
                (TASK_KEY_QJL,),
            ).fetchone()[0]
            assert fresh == 1
        finally:
            conn.close()

    def test_metadata_edit_without_segment_change_keeps_same_version_uuid(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_QJL, agent_id="agent-a", user_prompt="same-user", cache_prompt="same-cache")
        u1 = db.get_agent_task(TASK_KEY_QJL)["task_key_uuid"]
        db.save_agent_task(TASK_KEY_QJL, agent_id="agent-b")
        row = db.get_agent_task(TASK_KEY_QJL)
        assert row["task_key_uuid"] == u1
        assert row["agent_id"] == "agent-b"
        conn = db._get_connection()
        try:
            n = conn.execute(
                "SELECT COUNT(*) FROM agent_task WHERE task_key = ?",
                (TASK_KEY_QJL,),
            ).fetchone()[0]
            assert n == 1
        finally:
            conn.close()

    def test_migrate_pre_uuid_agent_task_keeps_legacy_cache_as_block_a(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_DB_DIR", str(tmp_path))
        from src.data import database

        monkeypatch.setattr(database, "DB_PATH", tmp_path / "astral.db")
        monkeypatch.setattr(database, "_agent_task_schema_ensured", False)
        db_path = tmp_path / "astral.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """CREATE TABLE agent_task (
                    task_key TEXT PRIMARY KEY,
                    agent_id TEXT,
                    user_prompt TEXT,
                    cache_prompt TEXT,
                    nocache_prompt TEXT,
                    updated_at TEXT
                )
            """
        )
        conn.execute(
            "INSERT INTO agent_task (task_key, agent_id, user_prompt, cache_prompt, nocache_prompt, updated_at) VALUES (?,?,?,?,?,?)",
            (TASK_KEY_QJL, "ag", "uu", "legacy-cache-slot-a", "", "2026-05-01T00:00:00Z"),
        )
        conn.commit()
        conn.close()
        row = database.get_agent_task(TASK_KEY_QJL)
        assert row is not None
        assert row["cache_prompt"] == "legacy-cache-slot-a"
        assert row["cache_prompt_b"] == ""
        assert row["cache_prompt_c"] == ""
        assert row["cache_prompt_d"] == ""
        assert row["user_prompt"] == "uu"

# AST-738: global-per-task_key grouping columns seeded from TASK_CONFIG phase/seq.
class TestAst738TaskGroupingMetadata:
    def test_seed_values_for_task_key_from_config(self) -> None:
        vals = seed_values_for_task_key(TASK_KEY_CRAFT)
        assert vals["task_group_name"] == "A. Candidate Context"
        assert vals["task_group_order"] == "A. Candidate Context"
        assert vals["task_seq"] == 1.0
        assert vals["task_name"] == TASK_KEY_CRAFT

    def test_new_row_defaults_grouping_from_config(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_QJL, agent_id="agent-1", user_prompt="prompt")
        row = db.get_agent_task(TASK_KEY_QJL)
        expected = seed_values_for_task_key(TASK_KEY_QJL)
        assert row is not None
        assert row["task_group_name"] == expected["task_group_name"]
        assert row["task_group_order"] == expected["task_group_order"]
        assert row["task_seq"] == expected["task_seq"]
        assert row["task_name"] == expected["task_name"]

    def test_grouping_only_edit_keeps_version_uuid(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_QJL, agent_id="agent-a", user_prompt="same-user")
        u1 = db.get_agent_task(TASK_KEY_QJL)["task_key_uuid"]
        db.save_agent_task(
            TASK_KEY_QJL,
            task_group_name="Custom Group",
            task_seq=42.0,
            task_name="Pretty Label",
        )
        row = db.get_agent_task(TASK_KEY_QJL)
        assert row["task_key_uuid"] == u1
        assert row["task_group_name"] == "Custom Group"
        assert row["task_seq"] == 42.0
        assert row["task_name"] == "Pretty Label"

    def test_segment_edit_copies_grouping_forward(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(
            TASK_KEY_QJL,
            agent_id="agent-1",
            user_prompt="v1",
            task_group_name="Keep Group",
            task_seq=3.0,
        )
        uuid1 = db.get_agent_task(TASK_KEY_QJL)["task_key_uuid"]
        db.save_agent_task(TASK_KEY_QJL, user_prompt="v2")
        row = db.get_agent_task(TASK_KEY_QJL)
        assert row["user_prompt"] == "v2"
        assert row["task_key_uuid"] != uuid1
        assert row["task_group_name"] == "Keep Group"
        assert row["task_seq"] == 3.0

    def test_list_candidate_tasks_includes_grouping_columns(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(
            TASK_KEY_QJL,
            agent_id="agent-1",
            user_prompt="p",
            task_group_order="D. Job Analysis",
            task_group_name="D. Job Analysis",
            task_seq=1.0,
            task_name="Qualify",
        )
        listed = db.list_candidate_tasks()
        ours = next(t for t in listed if t["task_key"] == TASK_KEY_QJL)
        assert ours["task_group_order"] == "D. Job Analysis"
        assert ours["task_group_name"] == "D. Job Analysis"
        assert ours["task_seq"] == 1.0
        assert ours["task_name"] == "Qualify"

    def test_backfill_skips_when_operator_already_seeded(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_QJL, agent_id="a1", user_prompt="p", task_group_name="Edited")
        conn = db._get_connection()
        try:
            db._ensure_agent_task_schema(conn)
            counts = backfill_task_grouping_metadata(conn, dry_run=True)
            assert counts["updated"] == 0
            assert counts["skipped"] >= 1
        finally:
            conn.close()

