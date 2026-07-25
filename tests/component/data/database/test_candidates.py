"""Component tests for candidate table cluster (AST-392 / AST-971)."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet


# Branches: insert requires state; invalid state; update merge vs overwrite; api key encrypt.
class TestSaveCandidate:
    def test_insert_requires_state(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="state required"):
            sqlite_in_memory.save_candidate("cand-1")

    def test_rejects_invalid_state(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Invalid candidate state"):
            sqlite_in_memory.save_candidate("cand-1", state="NOT_A_STATE")

    def test_insert_and_merge_update(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_data={"bio": "a"})
        db.save_candidate("cand-1", state="INTAKE_INITIATED", candidate_data={"summary": "b"}, merge=True)
        row = db.get_candidate("cand-1")
        assert row is not None
        assert row["state"] == "INTAKE_INITIATED"
        assert row["candidate_data"]["bio"] == "a"
        assert row["candidate_data"]["summary"] == "b"

    def test_overwrite_candidate_data(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_data={"bio": "a"})
        db.save_candidate("cand-1", candidate_data={"summary": "only"}, merge=False)
        row = db.get_candidate("cand-1")
        assert row is not None
        assert row["candidate_data"] == {"summary": "only"}

    def test_stores_encrypted_api_key(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        key = Fernet.generate_key().decode()
        monkeypatch.setattr(sqlite_in_memory, "_fernet", Fernet(key.encode()))
        sqlite_in_memory.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_api_key="secret-key")
        row = sqlite_in_memory.get_candidate("cand-1")
        assert row is not None
        assert row["candidate_api_key"] == "secret-key"


# Branches: blank id; missing row; list all.
class TestGetCandidate:
    def test_returns_none_for_blank_id(self, sqlite_in_memory) -> None:
        assert sqlite_in_memory.get_candidate("") is None

    def test_returns_none_when_missing(self, sqlite_in_memory) -> None:
        assert sqlite_in_memory.get_candidate("missing") is None


class TestListCandidates:
    def test_returns_saved_rows(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="NEW_CANDIDATE")
        sqlite_in_memory.save_candidate("cand-2", state="INTAKE_INITIATED")
        ids = {row["astral_candidate_id"] for row in sqlite_in_memory.list_candidates()}
        assert ids == {"cand-1", "cand-2"}


class TestClearCandidateApiKey:
    def test_clears_stored_key(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        key = Fernet.generate_key().decode()
        monkeypatch.setattr(sqlite_in_memory, "_fernet", Fernet(key.encode()))
        db = sqlite_in_memory
        db.save_candidate("cand-1", state="NEW_CANDIDATE", candidate_api_key="secret-key")
        db.clear_candidate_api_key("cand-1")
        row = db.get_candidate("cand-1")
        assert row is not None
        assert row["candidate_api_key"] is None


class TestAst971CandidateStateHistoryColumn:
    """AST-971: state_history column — parse, persist, preserve-when-omitted."""

    def test_insert_defaults_empty_history(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c971", state="NEW_CANDIDATE")
        row = db.get_candidate("c971")
        assert row["state_history"] == []

    def test_insert_persists_history_list(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        hist = [{"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "2026-01-01 00:00:00", "batch_id": None}]
        db.save_candidate("c971", state="NEW_CANDIDATE", state_history=hist)
        row = db.get_candidate("c971")
        assert row["state_history"] == hist

    def test_update_preserves_history_when_omitted(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        hist = [{"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None}]
        db.save_candidate("c971", state="NEW_CANDIDATE", state_history=hist)
        db.save_candidate("c971", state="INTAKE_INITIATED")
        row = db.get_candidate("c971")
        assert row["state"] == "INTAKE_INITIATED"
        assert row["state_history"] == hist

    def test_update_overwrites_history_when_provided(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate(
            "c971",
            state="NEW_CANDIDATE",
            state_history=[{"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None}],
        )
        nxt = [
            {"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None},
            {"from_state": "NEW_CANDIDATE", "to_state": "INTAKE_INITIATED", "timestamp": "t1", "batch_id": None},
        ]
        db.save_candidate("c971", state="INTAKE_INITIATED", state_history=nxt)
        assert db.get_candidate("c971")["state_history"] == nxt

    def test_invalid_json_parses_to_empty_list(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c971", state="NEW_CANDIDATE")
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE candidate SET state_history = ? WHERE astral_candidate_id = ?",
                ("not-json", "c971"),
            )
            conn.commit()
        finally:
            conn.close()
        assert db.get_candidate("c971")["state_history"] == []


class TestAst973LegacyCandidateMigration:
    """AST-973: hard_delete + migrate phases A/B/C."""

    def _force_state(self, db, cid: str, state: str, *, candidate_data: str | None = None, state_changed_at: str | None = None) -> None:
        """Bypass save_candidate validation so legacy rows can be staged for migrate."""
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
            cols = "astral_candidate_id, state, candidate_data, state_changed_at, updated_at, created_at"
            # Upsert: delete then insert minimal row
            conn.execute("DELETE FROM candidate WHERE astral_candidate_id = ?", (cid,))
            cd = candidate_data if candidate_data is not None else "{}"
            sca = state_changed_at or "2020-01-01 00:00:00"
            now = "2026-07-23 00:00:00"
            conn.execute(
                f"INSERT INTO candidate ({cols}) VALUES (?, ?, ?, ?, ?, ?)",
                (cid, state, cd, sca, now, now),
            )
            conn.commit()
        finally:
            conn.close()

    def test_hard_delete_removes_satellites(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c973", state="ACTIVE_SEARCH", candidate_data={})
        db.save_dispatch_task(
            candidate_id="c973",
            task_key="evaluate_jd",
            min_count=1,
            trigger_state="JD_READY",
        )
        db.sync_company_search_terms("c973", ["fintech"])
        counts = db.hard_delete_candidate("c973")
        assert counts["candidate"] == 1
        assert counts["dispatch_task"] >= 1
        assert counts["company_search_terms"] >= 1
        assert db.get_candidate("c973") is None
        assert db.list_dispatch_tasks_for_candidate("c973") == []

    def test_phase_b_remaps_legacy_preserves_state_changed_at(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        stamped = "2019-06-01 12:00:00"
        self._force_state(db, "legacy", "LIVE_PROMPTS", state_changed_at=stamped)
        self._force_state(db, "newish", "NEW", state_changed_at=stamped)
        self._force_state(db, "weird", "TOTALLY_UNKNOWN", state_changed_at=stamped)
        out = db.migrate_legacy_candidate_states(dry_run=False, phases="BC")
        assert out["states_remapped"] >= 3
        assert any(x["astral_candidate_id"] == "weird" for x in out["states_unknown_to_new_candidate"])
        assert db.get_candidate("legacy")["state"] == "ACTIVE_SEARCH"
        assert db.get_candidate("newish")["state"] == "NEW_CANDIDATE"
        assert db.get_candidate("weird")["state"] == "NEW_CANDIDATE"
        # Preserve aging clock
        conn = db._get_connection()
        try:
            row = conn.execute(
                "SELECT state_changed_at FROM candidate WHERE astral_candidate_id = ?",
                ("legacy",),
            ).fetchone()
            assert row[0] == stamped
        finally:
            conn.close()
        # Idempotent
        out2 = db.migrate_legacy_candidate_states(dry_run=False, phases="BC")
        assert out2["states_remapped"] == 0

    def test_phase_a_hard_deletes_pre_cutover_deleted_only(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        import json
        self._force_state(db, "pre", "DELETED", candidate_data="{}")
        self._force_state(
            db,
            "post",
            "DELETED",
            candidate_data=json.dumps({"lifecycle": {"reap_started_at": "2026-01-01T00:00:00Z"}}),
        )
        dry = db.migrate_legacy_candidate_states(dry_run=True, phases="A")
        assert dry["deleted_hard_pre_cutover"] == 1
        # Dry-run must not delete — check raw
        conn = db._get_connection()
        try:
            ids = {r[0] for r in conn.execute("SELECT astral_candidate_id FROM candidate").fetchall()}
        finally:
            conn.close()
        assert "pre" in ids and "post" in ids
        live = db.migrate_legacy_candidate_states(dry_run=False, phases="A")
        assert live["deleted_hard_pre_cutover"] == 1
        conn = db._get_connection()
        try:
            ids = {r[0] for r in conn.execute("SELECT astral_candidate_id FROM candidate").fetchall()}
        finally:
            conn.close()
        assert "pre" not in ids
        assert "post" in ids

    def test_phase_c_remaps_candidate_triggers_not_company_new(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("c973c", state="ACTIVE_SEARCH", candidate_data={})
        conn = db._get_connection()
        try:
            db._ensure_dispatch_task_schema(conn)
            # Candidate legacy trigger LIVE_PROMPTS → ACTIVE_SEARCH
            conn.execute(
                "INSERT INTO dispatch_task "
                "(candidate_id, task_key, entity_type, trigger_state, min_count, auto_mode, "
                "batch_size, freq_hrs, sort_by, batch_call_mode, updated_at) "
                "VALUES (?, 'craft_resume_base', 'candidate', 'LIVE_PROMPTS', 1, 0, 1, 0, "
                "'updated_at', 0, datetime('now'))",
                ("c973c",),
            )
            # Company NEW must stay (job/company registry)
            conn.execute(
                "INSERT INTO dispatch_task "
                "(candidate_id, task_key, entity_type, trigger_state, min_count, auto_mode, "
                "batch_size, freq_hrs, sort_by, batch_call_mode, updated_at) "
                "VALUES (?, 'evaluate_jd', 'company', 'NEW', 1, 0, 1, 0, "
                "'updated_at', 0, datetime('now'))",
                ("c973c",),
            )
            # Candidate NEW → NEW_CANDIDATE
            conn.execute(
                "INSERT INTO dispatch_task "
                "(candidate_id, task_key, entity_type, trigger_state, min_count, auto_mode, "
                "batch_size, freq_hrs, sort_by, batch_call_mode, updated_at) "
                "VALUES (?, 'bootstrap_candidate_context', 'candidate', 'NEW', 1, 0, 1, 0, "
                "'updated_at', 0, datetime('now'))",
                ("c973c",),
            )
            conn.commit()
        finally:
            conn.close()
        out = db.migrate_legacy_candidate_states(dry_run=False, phases="BC")
        assert out["dispatch_triggers_remapped"] >= 2
        rows = {
            (r["task_key"], r["trigger_state"], r.get("entity_type"))
            for r in db.list_dispatch_tasks_for_candidate("c973c")
        }
        assert ("craft_resume_base", "ACTIVE_SEARCH", "candidate") in rows
        assert ("evaluate_jd", "NEW", "company") in rows
        assert ("bootstrap_candidate_context", "NEW_CANDIDATE", "candidate") in rows

    def test_ensure_runs_bc_not_phase_a(self, sqlite_in_memory) -> None:
        """Schema ensure must not hard-delete pre-cutover DELETED."""
        db = sqlite_in_memory
        self._force_state(db, "keep_deleted", "DELETED", candidate_data="{}")
        db._candidate_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_candidate_schema(conn)
        finally:
            conn.close()
        conn = db._get_connection()
        try:
            ids = {r[0] for r in conn.execute("SELECT astral_candidate_id FROM candidate").fetchall()}
        finally:
            conn.close()
        assert "keep_deleted" in ids
