"""artifacts table + current-flag writers (AST-1352; rename AST-1364)."""

from __future__ import annotations

import json

import pytest


# Branches: ensure+inventory; save/get round-trip; retire-and-insert history;
# identical payload new UUID; list current_only; string blob; identity/None raises.
class TestAst1352Artifacts:
    def test_ensure_creates_table_and_inventory_lists_it(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert "- artifacts —" in (db.__doc__ or "")
        conn = db._get_connection()
        try:
            db._ensure_artifacts_table(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='artifacts'"
            ).fetchone()
            assert row[0] == 1
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(artifacts)").fetchall()
            }
            assert cols == {
                "artifact_uuid",
                "entity_type",
                "entity_id",
                "artifact_type",
                "artifact_data",
                "source_artifact_ids",
                "current",
                "created_at",
                "updated_at",
            }
            assert "source_artifact_ids" in (db.__doc__ or "")
            idx = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name='idx_artifacts_entity_type_current'"
            ).fetchone()
            assert idx is not None
        finally:
            conn.close()

    def test_save_get_round_trip_dict_payload(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        payload = {"text": "base resume v1", "sections": ["summary"]}
        uid = db.save_artifact("candidate", "cand-1", "base_resume", payload)
        assert uid
        row = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["entity_type"] == "candidate"
        assert row["entity_id"] == "cand-1"
        assert row["artifact_type"] == "base_resume"
        assert row["artifact_data"] == payload
        assert row["current"] == 1

    def test_second_save_retires_prior_and_keeps_history(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        uid1 = db.save_artifact("candidate", "cand-1", "base_resume", {"v": 1})
        uid2 = db.save_artifact("candidate", "cand-1", "base_resume", {"v": 2})
        assert uid1 != uid2
        current = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert current is not None
        assert current["artifact_uuid"] == uid2
        assert current["artifact_data"] == {"v": 2}
        assert current["current"] == 1

        history = db.list_artifacts(
            "candidate", "cand-1", "base_resume", current_only=False
        )
        assert len(history) == 2
        assert [r["artifact_uuid"] for r in history] == [uid1, uid2]
        assert history[0]["current"] == 0
        assert history[0]["artifact_data"] == {"v": 1}
        assert history[1]["current"] == 1

        only_current = db.list_artifacts(
            "candidate", "cand-1", "base_resume", current_only=True
        )
        assert len(only_current) == 1
        assert only_current[0]["artifact_uuid"] == uid2

    def test_identical_payload_still_inserts_new_uuid(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        payload = {"same": True}
        uid1 = db.save_artifact("candidate", "cand-1", "base_resume", payload)
        uid2 = db.save_artifact("candidate", "cand-1", "base_resume", payload)
        assert uid1 != uid2
        history = db.list_artifacts(
            "candidate", "cand-1", "base_resume", current_only=False
        )
        assert len(history) == 2

    def test_get_current_none_when_empty(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.get_current_artifact("candidate", "cand-1", "base_resume") is None
        assert (
            db.list_artifacts("candidate", "cand-1", "base_resume", current_only=False)
            == []
        )

    def test_string_payload_stored_as_is_non_json_round_trips(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        raw = "not-json-plain-text"
        uid = db.save_artifact("candidate", "cand-1", "base_resume", raw)
        row = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["artifact_data"] == raw

        json_text = json.dumps({"already": "encoded"})
        uid2 = db.save_artifact("candidate", "cand-1", "base_resume", json_text)
        row2 = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert row2 is not None
        assert row2["artifact_uuid"] == uid2
        # stored TEXT was JSON → reader json.loads back to dict
        assert row2["artifact_data"] == {"already": "encoded"}

    def test_identity_and_payload_validation(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match="entity_type"):
            db.save_artifact("  ", "cand-1", "base_resume", {"x": 1})
        with pytest.raises(ValueError, match="entity_id"):
            db.save_artifact("candidate", "", "base_resume", {"x": 1})
        with pytest.raises(ValueError, match="artifact_type"):
            db.save_artifact("candidate", "cand-1", "   ", {"x": 1})
        with pytest.raises(ValueError, match="invalid entity_type"):
            db.save_artifact("not-an-entity", "cand-1", "base_resume", {"x": 1})
        with pytest.raises(ValueError, match="artifact_data required"):
            db.save_artifact("candidate", "cand-1", "base_resume", None)
        with pytest.raises(ValueError, match="entity_type"):
            db.get_current_artifact("", "cand-1", "base_resume")
        with pytest.raises(ValueError, match="invalid entity_type"):
            db.list_artifacts("widget", "cand-1", "base_resume")


# Branches: public API rename; inventory/table/PK names; no legacy astral_* symbols.
class TestAst1364RenameArtifacts:
    """Bug-repro for AST-1364: product must expose artifacts / save_artifact (not astral_*)."""

    def test_public_api_and_table_use_unprefixed_names(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert hasattr(db, "save_artifact")
        assert hasattr(db, "get_current_artifact")
        assert hasattr(db, "list_artifacts")
        assert not hasattr(db, "save_astral_artifact")
        assert "- artifacts —" in (db.__doc__ or "")
        assert "artifact_uuid TEXT PK" in (db.__doc__ or "")
        conn = db._get_connection()
        try:
            db._ensure_artifacts_table(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='artifacts'"
            ).fetchone()
            assert row[0] == 1
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(artifacts)").fetchall()
            }
            assert "artifact_uuid" in cols
            assert "astral_artifact_uuid" not in cols
        finally:
            conn.close()

        uid = db.save_artifact("candidate", "cand-1", "base_resume", {"v": 1})
        row = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert row is not None
        assert row["artifact_uuid"] == uid

# Branches: PK hit/miss; blank uuid; retired pin still by-uuid; shape matches get_current.
class TestAst1584GetArtifact:
    """AST-1584: database.get_artifact by artifact_uuid (patt.artifact.read-operative)."""

    def test_get_by_uuid_returns_row_dict(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        payload = {"text": "pinned body", "sections": ["summary"]}
        uid = db.save_artifact("candidate", "cand-1", "base_resume", payload)
        row = db.get_artifact(uid)
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["entity_type"] == "candidate"
        assert row["entity_id"] == "cand-1"
        assert row["artifact_type"] == "base_resume"
        assert row["artifact_data"] == payload
        assert row["current"] == 1

    def test_get_by_uuid_returns_retired_row(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        uid1 = db.save_artifact("candidate", "cand-1", "base_resume", {"v": 1})
        uid2 = db.save_artifact("candidate", "cand-1", "base_resume", {"v": 2})
        assert uid1 != uid2
        assert db.get_current_artifact("candidate", "cand-1", "base_resume")["artifact_uuid"] == uid2
        retired = db.get_artifact(uid1)
        assert retired is not None
        assert retired["artifact_uuid"] == uid1
        assert retired["current"] == 0
        assert retired["artifact_data"] == {"v": 1}

    def test_get_by_uuid_miss_and_blank(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.get_artifact("00000000-0000-0000-0000-000000000000") is None
        with pytest.raises(ValueError, match="artifact_uuid required"):
            db.get_artifact("")
        with pytest.raises(ValueError, match="artifact_uuid required"):
            db.get_artifact("   ")


# Branches: source_artifact_ids column/ensure; save persist; get-current/get-by-uuid/list return;
# omit→[]; strip empties; bad type raises; no UUID existence validation.
class TestAst1591SourceArtifactIds:
    """AST-1591: artifacts.source_artifact_ids persist + read (no existence validation)."""

    def test_ensure_adds_column_on_preexisting_table(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            # Pre-AST-1591 shape (no source_artifact_ids) — ensure must ALTER-add.
            conn.execute(
                """CREATE TABLE artifacts (
                    artifact_uuid TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    artifact_data TEXT NOT NULL,
                    current INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )"""
            )
            conn.commit()
            db._artifacts_schema_ensured = False
            db._ensure_artifacts_table(conn)
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(artifacts)").fetchall()
            }
            assert "source_artifact_ids" in cols
        finally:
            conn.close()

    def test_save_omitted_sources_default_empty_list(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        uid = db.save_artifact("candidate", "cand-1", "base_resume", {"v": 1})
        row = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["source_artifact_ids"] == []
        by_uuid = db.get_artifact(uid)
        assert by_uuid is not None
        assert by_uuid["source_artifact_ids"] == []

    def test_save_persist_and_readers_return_sources(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        seed_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        seed_b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        uid = db.save_artifact(
            "job",
            "job-1",
            "job_resume",
            {"body": "derived"},
            source_artifact_ids=[seed_a, "  ", seed_b, ""],
        )
        current = db.get_current_artifact("job", "job-1", "job_resume")
        assert current is not None
        assert current["artifact_uuid"] == uid
        # empties stripped; order preserved; unknown uuids accepted (no existence check)
        assert current["source_artifact_ids"] == [seed_a, seed_b]
        by_uuid = db.get_artifact(uid)
        assert by_uuid is not None
        assert by_uuid["source_artifact_ids"] == [seed_a, seed_b]
        listed = db.list_artifacts("job", "job-1", "job_resume", current_only=True)
        assert len(listed) == 1
        assert listed[0]["source_artifact_ids"] == [seed_a, seed_b]

    def test_second_save_can_change_sources_independently(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        uid1 = db.save_artifact(
            "job",
            "job-1",
            "job_resume",
            {"v": 1},
            source_artifact_ids=["src-1"],
        )
        uid2 = db.save_artifact(
            "job",
            "job-1",
            "job_resume",
            {"v": 2},
            source_artifact_ids=[],
        )
        assert uid1 != uid2
        retired = db.get_artifact(uid1)
        assert retired is not None
        assert retired["current"] == 0
        assert retired["source_artifact_ids"] == ["src-1"]
        current = db.get_current_artifact("job", "job-1", "job_resume")
        assert current is not None
        assert current["artifact_uuid"] == uid2
        assert current["source_artifact_ids"] == []

    def test_source_artifact_ids_bad_type_raises(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match="source_artifact_ids"):
            db.save_artifact(
                "candidate",
                "cand-1",
                "base_resume",
                {"x": 1},
                source_artifact_ids="not-a-list",  # type: ignore[arg-type]
            )
