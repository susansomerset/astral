"""Candidate schema migrations (AST-575 pronoun backfill)."""

from __future__ import annotations

import json


class TestAst575PronounPreferenceBackfill:
    def test_pronoun_backfill_sets_default_when_missing(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c575-miss",
            state="NEW",
            candidate_data={"profile": {"first": "A"}},
        )
        # First ensure ran before insert; re-run migrations like a fresh process on existing rows.
        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
        finally:
            conn.close()
        row = db.get_candidate("c575-miss")
        assert row is not None
        assert row["candidate_data"]["profile"]["pronoun_preference"] == "they/them"

    def test_pronoun_backfill_skips_valid_preference(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c575-keep",
            state="NEW",
            candidate_data={"profile": {"pronoun_preference": "she/her"}},
        )
        row = db.get_candidate("c575-keep")
        assert row is not None
        assert row["candidate_data"]["profile"]["pronoun_preference"] == "she/her"

    def test_pronoun_backfill_idempotent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c575-idem",
            state="NEW",
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
        assert cd["profile"]["pronoun_preference"] == "they/them"
