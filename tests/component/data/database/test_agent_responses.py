"""Component tests for agent_responses table cluster (AST-392)."""

from __future__ import annotations


class TestAddAgentResponseEntry:
    def test_stores_and_lists_response(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        ok = db.add_agent_response_entry(
            "qualify_job_listings",
            "company",
            "acme",
            {"agent_performance": {"status": "success"}},
            parsed_response={"ok": True},
        )
        assert ok is True
        rows = db.list_agent_responses("company", "acme")
        assert len(rows) == 1
        assert rows[0]["status"] == "success"
