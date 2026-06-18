"""Component tests for agent_responses table cluster (AST-392)."""

from __future__ import annotations

import pytest


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
