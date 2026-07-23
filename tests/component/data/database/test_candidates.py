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
