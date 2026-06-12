"""Component tests for batch/score helper cluster (AST-392)."""

from __future__ import annotations


# Branches: legacy wrappers delegate to public APIs.
class TestCompanyBatchWrappers:
    def test_claim_company_batch_delegates(self, seeded_db, monkeypatch) -> None:
        db = seeded_db
        calls: list[tuple] = []

        def _fake_set(batch_id, clear=False, **kwargs):
            calls.append((batch_id, clear, kwargs))
            return 3

        monkeypatch.setattr(db, "set_company_batch", _fake_set)
        count = db.claim_company_batch("batch-1", "IMPORTED", 5, candidate_id="cand-1")
        assert count == 3
        assert calls[0][0] == "batch-1"
        assert calls[0][2]["candidate_id"] == "cand-1"

    def test_clear_company_batch_delegates(self, seeded_db, monkeypatch) -> None:
        db = seeded_db
        monkeypatch.setattr(db, "set_company_batch", lambda batch_id, clear=False, **kwargs: 2 if clear else 0)
        assert db.clear_company_batch("batch-1") == 2


class TestCompanyLookupWrappers:
    def test_get_company_by_name_delegates(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED", company_name="Acme")
        assert db.get_company_by_name("acme") == db.get_company("acme")

    def test_update_company_last_scan_at_sets_timestamp(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.update_company_last_scan_at("acme")
        row = db.get_company("acme")
        assert row is not None
        assert row["last_scan_at"]
