"""Component tests for agent_responses (entity column + schema leftovers).

AST-981 removed standalone-table insert/list I/O (`add_agent_response_entry` /
`list_agent_responses`). Entity-column latest-only upserts stay until AST-984;
schema ensure stays until AST-982.
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
        # Schema ensure remains for AST-982 drop sibling.
        assert hasattr(db_mod, "_ensure_agent_responses_schema")
        assert hasattr(db_mod, "append_agent_response")

    def test_hard_delete_candidate_skips_standalone_table_key(self, seeded_db) -> None:
        db = seeded_db
        db.save_candidate("c981", state="NEW_CANDIDATE")
        counts = db.hard_delete_candidate("c981")
        assert "agent_responses" not in counts
        assert counts["candidate"] == 1


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
