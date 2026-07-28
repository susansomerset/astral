"""Candidate schema migrations (AST-575 pronoun backfill; AST-1014 library)."""

from __future__ import annotations

import json

from src.data import database


class TestAst575PronounPreferenceBackfill:
    """Pronoun backfill still runs before library migration; end state is columns (AST-1014)."""

    def test_pronoun_backfill_sets_default_when_missing(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c575-miss",
            state="NEW_CANDIDATE",
            candidate_data={"profile": {"first": "A"}},
        )
        # Re-run migrations like a fresh process on existing rows.
        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
        finally:
            conn.close()
        row = db.get_candidate("c575-miss")
        assert row is not None
        assert "profile" not in (row.get("candidate_data") or {})
        assert row.get("pronouns") == "they/them"
        assert row.get("first") == "A"

    def test_pronoun_backfill_skips_valid_preference(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c575-keep",
            state="NEW_CANDIDATE",
            candidate_data={"profile": {"pronoun_preference": "she/her"}},
        )
        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
        finally:
            conn.close()
        row = db.get_candidate("c575-keep")
        assert row is not None
        assert "profile" not in (row.get("candidate_data") or {})
        assert row.get("pronouns") == "she/her"

    def test_pronoun_backfill_idempotent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c575-idem",
            state="NEW_CANDIDATE",
            candidate_data={"profile": {}},
        )
        conn = db._get_connection()
        try:
            db._migrate_pronoun_preference_backfill(conn)
            db._migrate_pronoun_preference_backfill(conn)
            raw = conn.execute(
                "SELECT candidate_data FROM candidate WHERE astral_candidate_id = ?",
                ("c575-idem",),
            ).fetchone()[0]
        finally:
            conn.close()
        cd = json.loads(raw)
        # Direct helper still writes profile key; library migration is separate.
        assert cd["profile"]["pronoun_preference"] == "they/them"


def _legacy_candidate_data() -> dict:
    return {
        "profile": {
            "first": "Jane",
            "last": "Doe",
            "contact_email": "jane@example.com",
            "pronoun_preference": "she/her",
            "title_patterns": "Engineer",
            "cover_letter_signature": "Thanks",
        },
        "context": {
            "starting_resume_text": "resume body",
            "linkedin_profile_text": "linkedin paste",
            "sample_cover_text": "cover sample",
            "bio_summary": "Bio",
        },
        "artifacts": {"base_resume": {"professional_summary": "Summary"}},
    }


def _insert_legacy_row(conn, candidate_id: str = "legacy-1") -> None:
    conn.execute(
        """INSERT INTO candidate (
            astral_candidate_id, state, candidate_data, first, last, full, pronouns,
            created_at, updated_at, state_changed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            candidate_id,
            "NEW_CANDIDATE",
            json.dumps(_legacy_candidate_data()),
            "",
            "",
            "",
            "",
            "2026-07-28 00:00:00",
            "2026-07-28 00:00:00",
            "2026-07-28 00:00:00",
        ),
    )
    conn.commit()


def _fetch_row(conn, candidate_id: str = "legacy-1") -> tuple:
    return conn.execute(
        "SELECT candidate_data, first, last, full, pronouns FROM candidate WHERE astral_candidate_id = ?",
        (candidate_id,),
    ).fetchone()


class TestAst1014CandidateLibraryMigration:
    def test_migrate_profile_to_contact_columns_and_context_remaps(self, sqlite_in_memory) -> None:
        conn = sqlite_in_memory._get_connection()
        database._ensure_candidate_schema(conn)
        _insert_legacy_row(conn)

        database._migrate_candidate_library_ast1014(conn)
        conn.commit()

        raw, first, last, full, pronouns = _fetch_row(conn)
        cd = json.loads(raw)

        assert "profile" not in cd
        assert cd["contact"]["contact_email"] == "jane@example.com"
        assert cd["contact"]["title_patterns"] == "Engineer"
        assert cd["context"]["raw_resume"] == "resume body"
        assert cd["context"]["raw_profile"] == "linkedin paste"
        assert cd["context"]["raw_sample"] == "cover sample"
        assert "starting_resume_text" not in cd["context"]
        assert "linkedin_profile_text" not in cd["context"]
        assert "sample_cover_text" not in cd["context"]
        assert cd["context"]["hopes"] == ""
        assert cd["context"]["interests"] == ""
        assert cd["context"]["concerns"] == ""
        assert first == "Jane"
        assert last == "Doe"
        assert full == "Jane Doe"
        assert pronouns == "she/her"

    def test_migration_idempotent_no_dual_keys(self, sqlite_in_memory) -> None:
        conn = sqlite_in_memory._get_connection()
        database._ensure_candidate_schema(conn)
        _insert_legacy_row(conn)

        database._migrate_candidate_library_ast1014(conn)
        conn.commit()
        first_pass = _fetch_row(conn)

        database._migrate_candidate_library_ast1014(conn)
        conn.commit()
        second_pass = _fetch_row(conn)

        assert first_pass == second_pass
        cd = json.loads(second_pass[0])
        assert "profile" not in cd
        remap_sources = ("starting_resume_text", "linkedin_profile_text", "sample_cover_text")
        assert not any(k in cd.get("context", {}) for k in remap_sources)
