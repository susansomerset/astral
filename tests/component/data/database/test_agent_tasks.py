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

# AST-738/740: grouping columns; seed defaults unassigned when TASK_CONFIG lacks phase/seq (AST-740).
class TestAst738TaskGroupingMetadata:
    def test_seed_values_for_task_key_unassigned_without_config_phase(self) -> None:
        vals = seed_values_for_task_key(TASK_KEY_CRAFT)
        assert vals["task_group_name"] == "(unassigned)"
        assert vals["task_group_order"] == "ZZZ"
        assert vals["task_seq"] == 999.0
        assert vals["task_name"] == TASK_KEY_CRAFT

    def test_new_row_defaults_grouping_unassigned_without_config_phase(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_QJL, agent_id="agent-1", user_prompt="prompt")
        row = db.get_agent_task(TASK_KEY_QJL)
        assert row is not None
        assert row["task_group_name"] == "(unassigned)"
        assert row["task_group_order"] == "ZZZ"
        assert row["task_seq"] == 999.0
        assert row["task_name"] == TASK_KEY_QJL

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


TASK_KEY_REPO_A = "__ast782_repo_task_a__"
TASK_KEY_REPO_B = "__ast782_repo_task_b__"
TASK_KEY_GROUPING = "__ast790_grouping_task__"


# AST-782: repo-owned agent_task JSON startup upsert + export queries.
class TestAst782AgentTaskRepoJsonStartup:
    @pytest.fixture(autouse=True)
    def _no_run_next_graph(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.data import database as database_mod

        monkeypatch.setattr(database_mod, "_validate_run_next", lambda _c, _k, _rn: None)

    def _current_row_dict(self, db, task_key: str) -> dict:
        conn = db._get_connection()
        try:
            cols = db.table_columns(conn, "agent_task")
            row = conn.execute(
                f"SELECT {','.join(cols)} FROM agent_task WHERE task_key = ? AND current = 1",
                (task_key,),
            ).fetchone()
            assert row is not None
            return dict(zip(cols, row))
        finally:
            conn.close()

    def test_startup_retires_absent_keys_and_imports_json(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_REPO_A, agent_id="a1", user_prompt="seed-a")
        db.save_agent_task(TASK_KEY_REPO_B, agent_id="b1", user_prompt="seed-b")
        json_row = self._current_row_dict(db, TASK_KEY_REPO_A)
        json_row["user_prompt"] = "repo-wins"
        conn = db._get_connection()
        try:
            db.apply_agent_task_repo_json_startup(conn, [json_row])
            conn.commit()
            current_a = db.get_agent_task(TASK_KEY_REPO_A)
            assert current_a is not None
            assert current_a["user_prompt"] == "repo-wins"
            assert db.get_agent_task(TASK_KEY_REPO_B) is None
            retired = conn.execute(
                "SELECT COUNT(*) FROM agent_task WHERE task_key = ? AND current = 0",
                (TASK_KEY_REPO_B,),
            ).fetchone()[0]
            assert retired >= 1
        finally:
            conn.close()

    def test_fetch_export_rows_only_current(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_REPO_A, agent_id="a1", user_prompt="current")
        db.save_agent_task(TASK_KEY_REPO_A, user_prompt="retired")
        conn = db._get_connection()
        try:
            rows = db.fetch_agent_task_repo_json_export_rows(conn)
            keys = {row["task_key"] for row in rows}
            assert TASK_KEY_REPO_A in keys
            assert all(row["current"] == 1 for row in rows)
            assert len([row for row in rows if row["task_key"] == TASK_KEY_REPO_A]) == 1
        finally:
            conn.close()

class TestAst790AgentTaskGroupingImport:
    """AST-790 UAT: repo JSON import forwards task grouping metadata on startup/revert."""

    @pytest.fixture(autouse=True)
    def _no_run_next_graph(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.data import database as database_mod

        monkeypatch.setattr(database_mod, "_validate_run_next", lambda _c, _k, _rn: None)

    def _current_row_dict(self, db, task_key: str) -> dict:
        conn = db._get_connection()
        try:
            cols = db.table_columns(conn, "agent_task")
            row = conn.execute(
                f"SELECT {','.join(cols)} FROM agent_task WHERE task_key = ? AND current = 1",
                (task_key,),
            ).fetchone()
            assert row is not None
            return dict(zip(cols, row))
        finally:
            conn.close()

    def test_startup_import_forwards_grouping_metadata(self, sqlite_in_memory) -> None:
        from src.core.repo_admin_json import load_repo_admin_json_file

        db = sqlite_in_memory
        rows = load_repo_admin_json_file("agent_task")
        conn = db._get_connection()
        try:
            db.apply_agent_task_repo_json_startup(conn, rows)
            conn.commit()
            task = db.get_agent_task("anticipate_scan")
            assert task is not None
            assert task["task_group_name"] == "Job Artifacts"
            assert task["task_group_order"] == "5000"
            assert task["task_name"] == "Anticipate Scan"
            assert float(task["task_seq"]) == 1.0
        finally:
            conn.close()

    def test_copy_upsert_updates_grouping_when_prompts_unchanged(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(TASK_KEY_GROUPING, agent_id="a1", user_prompt="same-prompt")
        import_row = self._current_row_dict(db, TASK_KEY_GROUPING)
        import_row["task_group_name"] = "Job Artifacts"
        import_row["task_group_order"] = "5000"
        import_row["task_name"] = "Anticipate Scan"
        import_row["task_seq"] = 1
        conn = db._get_connection()
        try:
            counts = db.apply_agent_task_copy_upsert(conn, [import_row])
            conn.commit()
            assert counts["updated"] == 1
            assert counts["skipped"] == 0
            task = db.get_agent_task(TASK_KEY_GROUPING)
            assert task is not None
            assert task["user_prompt"] == "same-prompt"
            assert task["task_group_name"] == "Job Artifacts"
            assert task["task_group_order"] == "5000"
            assert task["task_name"] == "Anticipate Scan"
            assert float(task["task_seq"]) == 1.0
        finally:
            conn.close()

    def test_revert_restores_grouping_when_prompts_match(self, sqlite_in_memory) -> None:
        from src.core import repo_admin_json as repo_json_mod

        db = sqlite_in_memory
        rows = repo_json_mod.load_repo_admin_json_file("agent_task")
        conn = db._get_connection()
        try:
            db.apply_agent_task_repo_json_startup(conn, rows)
            conn.commit()
            uuid = conn.execute(
                "SELECT task_key_uuid FROM agent_task WHERE task_key = ? AND current = 1",
                ("anticipate_scan",),
            ).fetchone()[0]
            conn.execute(
                """UPDATE agent_task
                   SET task_group_name = '(unassigned)', task_group_order = 'ZZZ',
                       task_name = 'anticipate_scan', task_seq = 999
                   WHERE task_key_uuid = ?""",
                (uuid,),
            )
            conn.commit()
        finally:
            conn.close()

        repo_json_mod.revert_repo_admin_json_table("agent_task")

        task = db.get_agent_task("anticipate_scan")
        assert task is not None
        assert task["task_group_name"] == "Job Artifacts"
        assert task["task_group_order"] == "5000"
        assert task["task_name"] == "Anticipate Scan"
        assert float(task["task_seq"]) == 1.0

