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
