"""Component tests for src/core/search.py (AST-2173)."""

from __future__ import annotations

from typing import Any

import pytest

from src.core import search as search_mod
from src.utils.config import APPLIED_JOB_STATES, SKIPPED_STATES


def _stub_reads(monkeypatch: pytest.MonkeyPatch, rows_by_type: dict[str, list[dict[str, Any]]], floors=None) -> list:
    """Stub the one read per type + the floor read; returns the (entity_type, cid, query) call log."""
    calls: list = []

    def _rows(entity_type: str, candidate_id: str, needle: str) -> list[dict[str, Any]]:
        calls.append((entity_type, candidate_id, needle))
        return [dict(r) for r in rows_by_type.get(entity_type, [])]

    monkeypatch.setattr(search_mod.database, "search_entity_rows", _rows)
    monkeypatch.setattr(search_mod.tracker, "score_floor_by_trigger_for_candidate", lambda cid: dict(floors or {}))
    return calls


def _job_row(jid: str, matched: list[str], **kw) -> dict[str, Any]:
    return {"astral_job_id": jid, "job_title": "T", "company_id": "acme", "state": "NEW", "matched_fields": matched, **kw}


# Branches: all three keys always present; each type read once with cid + query passed through.
class TestAst2173Keys:
    def test_no_match_is_three_empty_lists(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _stub_reads(monkeypatch, {})
        out = search_mod.search_entities("cand-a", " raw q ")
        assert out == {"job": [], "company": [], "meteorite": []}
        assert calls == [(t, "cand-a", " raw q ") for t in ("job", "company", "meteorite")]


# Branches: tier = base iff any matched field is a base field; base list then payload list, read order kept.
class TestAst2173Tiering:
    def test_base_before_payload_with_stable_order(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _stub_reads(
            monkeypatch,
            {
                "job": [
                    _job_row("p1", ["job_data"]),
                    _job_row("b1", ["job_title", "job_data"]),
                    _job_row("p2", ["job_data"]),
                    _job_row("b2", ["state"]),
                ]
            },
        )
        jobs = search_mod.search_entities("cand-a", "q")["job"]
        assert [(j["entity_id"], j["tier"]) for j in jobs] == [
            ("b1", "base"), ("b2", "base"), ("p1", "payload"), ("p2", "payload"),
        ]
        assert jobs[0]["matched_fields"] == ["job_title", "job_data"]

    def test_company_and_meteorite_payload_tier(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _stub_reads(
            monkeypatch,
            {
                "company": [{"short_name": "acme", "company_name": "Acme", "state": "IMPORTED", "matched_fields": ["company_data"]}],
                "meteorite": [{"id": 7, "job_title": "Dev", "employer_name": "Orbit", "state": "NEW", "matched_fields": ["error"]}],
            },
        )
        out = search_mod.search_entities("cand-a", "q")
        assert out["company"][0]["tier"] == "payload"
        assert out["meteorite"][0]["tier"] == "payload"


# Branches: display_name joins non-blank name_fields with " — "; all blank → str(entity_id); job-only keys.
class TestAst2173ResultShape:
    def test_display_names_and_entity_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _stub_reads(
            monkeypatch,
            {
                "job": [_job_row("j1", ["job_title"], job_title=" Dev Lead ", company_id="acme")],
                "company": [{"short_name": "acme", "company_name": "", "state": "IMPORTED", "matched_fields": ["short_name"]}],
                "meteorite": [
                    {"id": 7, "job_title": "Dev", "employer_name": None, "state": "NEW", "matched_fields": ["id"]},
                    {"id": 8, "job_title": "  ", "employer_name": None, "state": "NEW", "matched_fields": ["id"]},
                ],
            },
        )
        out = search_mod.search_entities("cand-a", "q")
        assert out["job"][0]["display_name"] == "Dev Lead — acme"
        assert out["company"][0] == {
            "entity_id": "acme", "display_name": "acme", "state": "IMPORTED", "tier": "base", "matched_fields": ["short_name"],
        }
        assert [(m["entity_id"], m["display_name"]) for m in out["meteorite"]] == [(7, "Dev"), (8, "8")]
        assert "jobs_list" not in out["meteorite"][0] and "modal_kind" not in out["meteorite"][0]

    def test_job_carries_jobs_list_and_modal_kind(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _stub_reads(monkeypatch, {"job": [_job_row("j1", ["job_title"], state="CANDIDATE_REVIEW")]})
        job = search_mod.search_entities("cand-a", "q")["job"][0]
        assert (job["jobs_list"], job["modal_kind"]) == ("ready", "report")


# Branches: _jobs_list ready / review / applied / skipped-state / below-floor / processing (AC8 API half).
class TestAst2173JobsListAndModal:
    def test_six_jobs_on_real_sqlite(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        db.save_company("acme", state="IMPORTED", candidate_id="cand-a")
        cases = {
            "j-ready": ("CANDIDATE_REVIEW", None, "ready", "report"),
            "j-review": ("RECOMMENDED", None, "review", "report"),
            "j-applied": (APPLIED_JOB_STATES[0], None, "applied", "report"),
            "j-proc": ("NEW", None, "processing", "detail"),
            "j-skip": (SKIPPED_STATES[0], None, "skipped", "detail"),
            "j-floor": ("PASSED_JD", 3.0, "skipped", "detail"),
            "j-above": ("PASSED_JD", 9.0, "processing", "detail"),
        }
        for jid, (state, score, _, _) in cases.items():
            db.save_job(jid, company_id="acme", candidate_id="cand-a", state=state, company_job_id=jid,
                        job_title="Numbat role")
            if score is not None:
                # save_job's INSERT ignores latest_score; only the update path writes it.
                db.save_job(jid, latest_score=score)
        # Floor read stubbed (its own tests live in tracker/database); the miss comparison runs for real.
        monkeypatch.setattr(search_mod.tracker, "score_floor_by_trigger_for_candidate", lambda cid: {"PASSED_JD": 7.0})
        got = {j["entity_id"]: (j["jobs_list"], j["modal_kind"]) for j in search_mod.search_entities("cand-a", "numbat")["job"]}
        assert got == {jid: (c[2], c[3]) for jid, c in cases.items()}


# Branches: AC4 end to end — base hit outranks a newer payload-only hit; each entity once.
class TestAst2173BaseBeforePayloadReal:
    def test_title_hit_before_newer_job_data_hit(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_company("acme", state="IMPORTED", candidate_id="cand-a")
        db.save_job("J1", company_id="acme", candidate_id="cand-a", state="NEW", company_job_id="c1",
                    job_title="Quokka Wrangler", job_data={"n": "quokka too"}, state_changed_at="2026-01-01T00:00:00Z")
        db.save_job("J2", company_id="acme", candidate_id="cand-a", state="NEW", company_job_id="c2",
                    job_title="Plain", job_data={"n": "quokka"}, state_changed_at="2026-09-01T00:00:00Z")
        jobs = search_mod.search_entities("cand-a", "QUOKKA")["job"]
        assert [(j["entity_id"], j["tier"]) for j in jobs] == [("J1", "base"), ("J2", "payload")]
