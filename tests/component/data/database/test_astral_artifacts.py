"""astral_artifacts table + current-flag writers (AST-1352)."""

from __future__ import annotations

import json

import pytest


# Branches: ensure+inventory; save/get round-trip; retire-and-insert history;
# identical payload new UUID; list current_only; string blob; identity/None raises.
class TestAst1352AstralArtifacts:
    def test_ensure_creates_table_and_inventory_lists_it(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert "astral_artifacts" in (db.__doc__ or "")
        conn = db._get_connection()
        try:
            db._ensure_astral_artifacts_table(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='astral_artifacts'"
            ).fetchone()
            assert row[0] == 1
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(astral_artifacts)").fetchall()
            }
            assert cols == {
                "astral_artifact_uuid",
                "entity_type",
                "entity_id",
                "artifact_type",
                "artifact_data",
                "current",
                "created_at",
                "updated_at",
            }
            idx = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name='idx_astral_artifacts_entity_type_current'"
            ).fetchone()
            assert idx is not None
        finally:
            conn.close()

    def test_save_get_round_trip_dict_payload(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        payload = {"text": "base resume v1", "sections": ["summary"]}
        uid = db.save_astral_artifact("candidate", "cand-1", "base_resume", payload)
        assert uid
        row = db.get_current_astral_artifact("candidate", "cand-1", "base_resume")
        assert row is not None
        assert row["astral_artifact_uuid"] == uid
        assert row["entity_type"] == "candidate"
        assert row["entity_id"] == "cand-1"
        assert row["artifact_type"] == "base_resume"
        assert row["artifact_data"] == payload
        assert row["current"] == 1

    def test_second_save_retires_prior_and_keeps_history(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        uid1 = db.save_astral_artifact("candidate", "cand-1", "base_resume", {"v": 1})
        uid2 = db.save_astral_artifact("candidate", "cand-1", "base_resume", {"v": 2})
        assert uid1 != uid2
        current = db.get_current_astral_artifact("candidate", "cand-1", "base_resume")
        assert current is not None
        assert current["astral_artifact_uuid"] == uid2
        assert current["artifact_data"] == {"v": 2}
        assert current["current"] == 1

        history = db.list_astral_artifacts(
            "candidate", "cand-1", "base_resume", current_only=False
        )
        assert len(history) == 2
        assert [r["astral_artifact_uuid"] for r in history] == [uid1, uid2]
        assert history[0]["current"] == 0
        assert history[0]["artifact_data"] == {"v": 1}
        assert history[1]["current"] == 1

        only_current = db.list_astral_artifacts(
            "candidate", "cand-1", "base_resume", current_only=True
        )
        assert len(only_current) == 1
        assert only_current[0]["astral_artifact_uuid"] == uid2

    def test_identical_payload_still_inserts_new_uuid(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        payload = {"same": True}
        uid1 = db.save_astral_artifact("candidate", "cand-1", "base_resume", payload)
        uid2 = db.save_astral_artifact("candidate", "cand-1", "base_resume", payload)
        assert uid1 != uid2
        history = db.list_astral_artifacts(
            "candidate", "cand-1", "base_resume", current_only=False
        )
        assert len(history) == 2

    def test_get_current_none_when_empty(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.get_current_astral_artifact("candidate", "cand-1", "base_resume") is None
        assert (
            db.list_astral_artifacts("candidate", "cand-1", "base_resume", current_only=False)
            == []
        )

    def test_string_payload_stored_as_is_non_json_round_trips(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        raw = "not-json-plain-text"
        uid = db.save_astral_artifact("candidate", "cand-1", "base_resume", raw)
        row = db.get_current_astral_artifact("candidate", "cand-1", "base_resume")
        assert row is not None
        assert row["astral_artifact_uuid"] == uid
        assert row["artifact_data"] == raw

        json_text = json.dumps({"already": "encoded"})
        uid2 = db.save_astral_artifact("candidate", "cand-1", "base_resume", json_text)
        row2 = db.get_current_astral_artifact("candidate", "cand-1", "base_resume")
        assert row2 is not None
        assert row2["astral_artifact_uuid"] == uid2
        # stored TEXT was JSON → reader json.loads back to dict
        assert row2["artifact_data"] == {"already": "encoded"}

    def test_identity_and_payload_validation(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match="entity_type"):
            db.save_astral_artifact("  ", "cand-1", "base_resume", {"x": 1})
        with pytest.raises(ValueError, match="entity_id"):
            db.save_astral_artifact("candidate", "", "base_resume", {"x": 1})
        with pytest.raises(ValueError, match="artifact_type"):
            db.save_astral_artifact("candidate", "cand-1", "   ", {"x": 1})
        with pytest.raises(ValueError, match="invalid entity_type"):
            db.save_astral_artifact("not-an-entity", "cand-1", "base_resume", {"x": 1})
        with pytest.raises(ValueError, match="artifact_data required"):
            db.save_astral_artifact("candidate", "cand-1", "base_resume", None)
        with pytest.raises(ValueError, match="entity_type"):
            db.get_current_astral_artifact("", "cand-1", "base_resume")
        with pytest.raises(ValueError, match="invalid entity_type"):
            db.list_astral_artifacts("widget", "cand-1", "base_resume")
