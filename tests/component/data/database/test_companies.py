"""Component tests for company table cluster (AST-392)."""

from __future__ import annotations

import pytest


# Branches: required fields; invalid state; JSON serialization; insert + read.
class TestSaveCompany:
    def test_requires_short_name(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="short_name is required"):
            sqlite_in_memory.save_company("", state="IMPORTED")

    def test_requires_state(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="state is required"):
            sqlite_in_memory.save_company("acme", state="")

    def test_rejects_invalid_state(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Invalid state"):
            sqlite_in_memory.save_company("acme", state="NOT_A_STATE")

    def test_rejects_non_json_company_data(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Failed to serialize"):
            sqlite_in_memory.save_company("acme", state="IMPORTED", company_data={"bad": {1, 2}})  # type: ignore[arg-type]

    def test_insert_and_round_trip(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company(
            "acme",
            state="IMPORTED",
            company_name="Acme",
            company_data={"note": "hi"},
            state_history=[{"to_state": "IMPORTED", "timestamp": "t", "batch_id": "b1"}],
        )
        row = db.get_company("acme")
        assert row is not None
        assert row["company_name"] == "Acme"
        assert row["company_data"]["note"] == "hi"
        assert row["state_history"][0]["batch_id"] == "b1"


# Branches: empty kwargs; allowed column update.
class TestUpdateCompany:
    def test_returns_zero_without_allowed_columns(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_company("acme", state="IMPORTED")
        assert sqlite_in_memory.update_company("acme", unknown="x") == 0

    def test_updates_allowed_fields(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("acme", state="IMPORTED", company_name="Old")
        assert db.update_company("acme", company_name="New") == 1
        row = db.get_company("acme")
        assert row is not None
        assert row["company_name"] == "New"


class TestListCompanies:
    def test_filters_by_state_and_candidate(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED", company_name="Acme")
        db.update_company("acme", candidate_id="cand-1")
        rows = db.list_companies(states=["IMPORTED"], candidate_id="cand-1")
        assert [row["short_name"] for row in rows] == ["acme"]
