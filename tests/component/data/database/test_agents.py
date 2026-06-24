"""Component tests for agent table cluster (AST-392)."""

from __future__ import annotations

import pytest


# Branches: insert with brain_setting; update optional fields; delete; task refs.
class TestSaveAgent:
    def test_insert_and_update(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt", brain_setting="Medium", temperature=0.2, max_tokens=100)
        row = db.get_agent("agent-1")
        assert row is not None
        assert row["content"] == "prompt"
        assert row["brain_setting"] == "Medium"
        db.save_agent("agent-1", "prompt-2", temperature=0.5)
        row = db.get_agent("agent-1")
        assert row is not None
        assert row["content"] == "prompt-2"
        assert row["temperature"] == 0.5

    def test_insert_requires_brain_setting(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="brain_setting"):
            sqlite_in_memory.save_agent("agent-new", "prompt")


class TestListAgents:
    def test_returns_saved_agents(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_agent("agent-1", "one", brain_setting="Little")
        sqlite_in_memory.save_agent("agent-2", "two", brain_setting="Big")
        ids = {row["agent_id"] for row in sqlite_in_memory.list_agents()}
        assert ids == {"agent-1", "agent-2"}


class TestDeleteAgent:
    def test_deletes_existing_agent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt", brain_setting="Medium")
        assert db.delete_agent("agent-1") is True
        assert db.get_agent("agent-1") is None


class TestCountAgentTaskRefs:
    def test_counts_task_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt", brain_setting="Medium")
        db.save_agent_task("qualify_job_listings", agent_id="agent-1", user_prompt="hi")
        assert db.count_agent_task_refs("agent-1") == 1


def _agent_repo_row(
    agent_id: str,
    *,
    content: str = "prompt",
    brain_setting: str = "Medium",
    temperature: float | None = 0.2,
    max_tokens: int | None = 100,
    updated_at: str = "2026-06-24 00:00:00",
) -> dict:
    return {
        "agent_id": agent_id,
        "content": content,
        "brain_setting": brain_setting,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "updated_at": updated_at,
    }


# AST-782: repo-owned agent JSON startup upsert + export queries.
class TestAst782AgentRepoJsonStartup:
    def test_apply_upserts_updates_and_deletes_absent_agents(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("keep-me", "old", brain_setting="Little")
        db.save_agent("drop-me", "gone", brain_setting="Big")
        conn = db._get_connection()
        try:
            db.apply_agent_repo_json_startup(
                conn,
                [
                    _agent_repo_row("keep-me", content="from-json", brain_setting="Medium"),
                    _agent_repo_row("new-agent", content="fresh"),
                ],
            )
            conn.commit()
            kept = db.get_agent("keep-me")
            assert kept is not None
            assert kept["content"] == "from-json"
            assert kept["brain_setting"] == "Medium"
            assert db.get_agent("drop-me") is None
            assert db.get_agent("new-agent") is not None
            listed = {row["agent_id"] for row in db.list_agents()}
            assert listed == {"keep-me", "new-agent"}
        finally:
            conn.close()

    def test_fetch_export_rows_use_repo_columns(self, sqlite_in_memory) -> None:
        from src.utils.config import REPO_ADMIN_JSON_CONFIG

        db = sqlite_in_memory
        db.save_agent("agent-a", "body", brain_setting="Little", temperature=0.1, max_tokens=50)
        conn = db._get_connection()
        try:
            rows = db.fetch_agent_repo_json_export_rows(conn)
            assert len(rows) == 1
            assert set(rows[0].keys()) == set(REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"])
            assert rows[0]["agent_id"] == "agent-a"
            assert rows[0]["content"] == "body"
        finally:
            conn.close()

    def test_rejects_wrong_row_keys(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            with pytest.raises(ValueError, match="keys must be"):
                db.apply_agent_repo_json_startup(conn, [{"agent_id": "a", "content": "x"}])
        finally:
            conn.close()
