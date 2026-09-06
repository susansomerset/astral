"""artifact table + current-flag writers (AST-1352; rename AST-1364; singular+cid AST-1597)."""

from __future__ import annotations

import json

import pytest


# Branches: ensure+inventory; save/get round-trip; retire-and-insert history;
# identical payload new UUID; list current_only; string blob; identity/None raises.
class TestAst1352Artifacts:
    def test_ensure_creates_table_and_inventory_lists_it(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert "- artifact —" in (db.__doc__ or "")
        assert "- artifacts —" not in (db.__doc__ or "")
        conn = db._get_connection()
        try:
            db._ensure_artifact_table(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='artifact'"
            ).fetchone()
            assert row[0] == 1
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(artifact)").fetchall()
            }
            assert cols == {
                "artifact_uuid",
                "candidate_id",
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
            assert "candidate_id" in (db.__doc__ or "")
            idx = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name='idx_artifact_entity_type_current'"
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
        assert row["candidate_id"] == "cand-1"
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
        assert current["candidate_id"] == "cand-1"

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
    """Bug-repro for AST-1364: product must expose artifact / save_artifact (not astral_*)."""

    def test_public_api_and_table_use_unprefixed_names(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert hasattr(db, "save_artifact")
        assert hasattr(db, "get_current_artifact")
        assert hasattr(db, "list_artifacts")
        assert not hasattr(db, "save_astral_artifact")
        assert "- artifact —" in (db.__doc__ or "")
        assert "artifact_uuid TEXT PK" in (db.__doc__ or "")
        conn = db._get_connection()
        try:
            db._ensure_artifact_table(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='artifact'"
            ).fetchone()
            assert row[0] == 1
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(artifact)").fetchall()
            }
            assert "artifact_uuid" in cols
            assert "astral_artifact_uuid" not in cols
        finally:
            conn.close()

        uid = db.save_artifact("candidate", "cand-1", "base_resume", {"v": 1})
        row = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["candidate_id"] == "cand-1"


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
        assert row["candidate_id"] == "cand-1"
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
        assert retired["candidate_id"] == "cand-1"

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
    """AST-1591: artifact.source_artifact_ids persist + read (no existence validation)."""

    def test_ensure_adds_column_on_preexisting_table(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            # Pre-AST-1591 singular shape (has candidate_id; no source_artifact_ids).
            conn.execute(
                """CREATE TABLE artifact (
                    artifact_uuid TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
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
            db._artifact_schema_ensured = False
            db._ensure_artifact_table(conn)
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(artifact)").fetchall()
            }
            assert "source_artifact_ids" in cols
            assert "candidate_id" in cols
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
            candidate_id="cand-owner",
        )
        current = db.get_current_artifact("job", "job-1", "job_resume")
        assert current is not None
        assert current["artifact_uuid"] == uid
        assert current["candidate_id"] == "cand-owner"
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
            candidate_id="cand-owner",
        )
        uid2 = db.save_artifact(
            "job",
            "job-1",
            "job_resume",
            {"v": 2},
            source_artifact_ids=[],
            candidate_id="cand-owner",
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


# Branches: singular table+index+inventory; copy-adopt leaves plural; candidate_id resolve /
# mismatch / ownership lookup; readers return candidate_id.
class TestAst1597ArtifactSingularAndCandidateId:
    """AST-1597: artifacts→artifact rename + required candidate_id on every row."""

    def test_inventory_and_fresh_ensure_singular_with_candidate_id(
        self, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        doc = db.__doc__ or ""
        assert "- artifact —" in doc
        assert "- artifacts —" not in doc
        assert "candidate_id TEXT NOT NULL" in doc
        conn = db._get_connection()
        try:
            db._ensure_artifact_table(conn)
            names = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            assert "artifact" in names
            assert "artifacts" not in names
            cols = {
                r[1]
                for r in conn.execute("PRAGMA table_info(artifact)").fetchall()
            }
            assert "candidate_id" in cols
            idx = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name='idx_artifact_entity_type_current'"
            ).fetchone()
            assert idx is not None
            legacy = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name IN ('idx_artifacts_entity_type_current',"
                " 'idx_astral_artifacts_entity_type_current')"
            ).fetchall()
            assert legacy == []
        finally:
            conn.close()

    def test_copy_adopt_from_plural_leaves_artifacts_and_backfills_cid(
        self, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            # CASE backfill references job/company.candidate_id — production DBs have them.
            db._ensure_company_schema(conn)
            db._ensure_company_candidate_fk(conn)
            db._ensure_job_schema(conn)
            conn.execute(
                """CREATE TABLE artifacts (
                    artifact_uuid TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    artifact_data TEXT NOT NULL,
                    source_artifact_ids TEXT NOT NULL DEFAULT '[]',
                    current INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )"""
            )
            conn.execute(
                """INSERT INTO artifacts (
                       artifact_uuid, entity_type, entity_id, artifact_type,
                       artifact_data, source_artifact_ids, current, created_at, updated_at)
                   VALUES (?, 'candidate', 'cand-1', 'base_resume', ?, '[]', 1, ?, ?)""",
                ("uuid-cand-1", '{"v": 1}', "2020-01-01T00:00:00+00:00", "2020-01-01T00:00:00+00:00"),
            )
            conn.commit()
            db._artifact_schema_ensured = False
            db._ensure_artifact_table(conn)
            # Plural left for Susan to DROP; singular populated with candidate_id.
            assert (
                conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='artifacts'"
                ).fetchone()[0]
                == 1
            )
            row = conn.execute(
                "SELECT candidate_id, entity_id, artifact_data FROM artifact "
                "WHERE artifact_uuid = ?",
                ("uuid-cand-1",),
            ).fetchone()
            assert row is not None
            assert row[0] == "cand-1"
            assert row[1] == "cand-1"
        finally:
            conn.close()

        # Public readers use singular table
        got = db.get_current_artifact("candidate", "cand-1", "base_resume")
        assert got is not None
        assert got["artifact_uuid"] == "uuid-cand-1"
        assert got["candidate_id"] == "cand-1"

    def test_candidate_write_omitted_cid_equals_entity_id(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        uid = db.save_artifact("candidate", "cand-9", "base_resume", {"ok": True})
        row = db.get_artifact(uid)
        assert row is not None
        assert row["candidate_id"] == "cand-9"

    def test_candidate_write_mismatched_cid_raises(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match="candidate_id must equal entity_id"):
            db.save_artifact(
                "candidate",
                "cand-9",
                "base_resume",
                {"x": 1},
                candidate_id="other-cand",
            )

    def test_job_write_explicit_cid_and_unresolved_raises(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        uid = db.save_artifact(
            "job",
            "job-orphan",
            "job_resume",
            {"body": "x"},
            candidate_id="cand-x",
        )
        row = db.get_current_artifact("job", "job-orphan", "job_resume")
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["candidate_id"] == "cand-x"

        # Ownership lookup needs job table present (empty → unresolved → ValueError).
        conn = db._get_connection()
        try:
            db._ensure_company_schema(conn)
            db._ensure_company_candidate_fk(conn)
            db._ensure_job_schema(conn)
        finally:
            conn.close()
        with pytest.raises(ValueError, match="candidate_id required"):
            db.save_artifact("job", "job-missing", "job_resume", {"body": "y"})

    def test_job_write_resolves_cid_via_company_ownership(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("acme", state="IMPORTED", candidate_id="cand-owner")
        db.save_job("job-owned", company="acme", state="NEW")
        uid = db.save_artifact("job", "job-owned", "cover_letter", {"t": "hi"})
        row = db.get_current_artifact("job", "job-owned", "cover_letter")
        assert row is not None
        assert row["artifact_uuid"] == uid
        assert row["candidate_id"] == "cand-owner"

    def test_company_write_resolves_and_readers_return_cid(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("acme", state="IMPORTED", candidate_id="cand-co")
        uid = db.save_artifact("company", "acme", "watch_criteria", {"k": 1})
        current = db.get_current_artifact("company", "acme", "watch_criteria")
        assert current is not None
        assert current["artifact_uuid"] == uid
        assert current["candidate_id"] == "cand-co"
        listed = db.list_artifacts("company", "acme", "watch_criteria", current_only=True)
        assert listed[0]["candidate_id"] == "cand-co"
