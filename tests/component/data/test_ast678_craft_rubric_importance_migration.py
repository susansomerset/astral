"""Component tests for AST-678 craft rubric importance explainer agent_task migration."""

from __future__ import annotations

import sqlite3

import pytest

from src.data import database


def _current_user_prompt(conn: sqlite3.Connection, task_key: str) -> str | None:
    row = conn.execute(
        "SELECT user_prompt FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1",
        (task_key,),
    ).fetchone()
    return row[0] if row else None


def _current_agent_id(conn: sqlite3.Connection, task_key: str) -> str | None:
    row = conn.execute(
        "SELECT agent_id FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1",
        (task_key,),
    ).fetchone()
    return row[0] if row else None


def _has_current_row(conn: sqlite3.Connection, task_key: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1",
        (task_key,),
    ).fetchone()
    return row is not None


class TestAst678PatchHelper:
    def test_patch_inserts_before_response_schema(self) -> None:
        up = "Intro prose.\n\n{$RESPONSE_SCHEMA}\n\nReturn JSON."
        patched = database._patch_ast678_importance_into_user_prompt(up)
        assert database._AST678_IMPORTANCE_MARKER in patched
        assert patched.index(database._AST678_IMPORTANCE_MARKER) < patched.index("{$RESPONSE_SCHEMA}")


class TestAst678CraftRubricImportanceMigration:
    def test_migration_idempotent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(
            "craft_joblist_rubric",
            agent_id="agent-1",
            user_prompt="Before.\n\n{$RESPONSE_SCHEMA}\n",
        )
        conn = db._get_connection()
        try:
            database._apply_ast678_craft_rubric_importance_migration(conn)
            up1 = _current_user_prompt(conn, "craft_joblist_rubric")
            database._apply_ast678_craft_rubric_importance_migration(conn)
            up2 = _current_user_prompt(conn, "craft_joblist_rubric")
            assert up1 == up2
            assert database._AST678_IMPORTANCE_MARKER in (up1 or "")
        finally:
            conn.close()

    def test_prefilter_task_key_rename(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task(
            "craft_company_prefilter",
            agent_id="test_agent",
            user_prompt="Prefilter criteria.\n\n{$RESPONSE_SCHEMA}\n",
        )
        conn = db._get_connection()
        try:
            assert not _has_current_row(conn, "craft_prefilter_rubric")
            database._apply_ast678_craft_rubric_importance_migration(conn)
            assert _current_agent_id(conn, "craft_prefilter_rubric") == "test_agent"
            up = _current_user_prompt(conn, "craft_prefilter_rubric")
            assert up and database._AST678_IMPORTANCE_MARKER in up
            assert not _has_current_row(conn, "craft_company_prefilter")
        finally:
            conn.close()

    def test_all_six_keys_receive_marker(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        for task_key in database._AST678_CRAFT_RUBRIC_TASK_KEYS:
            db.save_agent_task(
                task_key,
                agent_id="agent-rubric",
                user_prompt=f"Task {task_key}.\n\n{{$RESPONSE_SCHEMA}}\n",
            )
        conn = db._get_connection()
        try:
            database._apply_ast678_craft_rubric_importance_migration(conn)
            for task_key in database._AST678_CRAFT_RUBRIC_TASK_KEYS:
                up = _current_user_prompt(conn, task_key)
                assert up and database._AST678_IMPORTANCE_MARKER in up, task_key
        finally:
            conn.close()
