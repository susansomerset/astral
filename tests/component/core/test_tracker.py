"""Component tests for src/core/tracker.py (AST-393)."""

from __future__ import annotations

import re
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import tracker as tracker_mod
from src.utils import config as cfg


# Branches: invalid company, batch_id, raw_job_listings; duplicate vs new ingest.
class TestIngestJobs:
    def test_rejects_invalid_inputs(self) -> None:
        with pytest.raises(ValueError, match="company"):
            tracker_mod.ingest_jobs("", "batch", [])
        with pytest.raises(ValueError, match="batch_id"):
            tracker_mod.ingest_jobs("co", "", [])
        with pytest.raises(ValueError, match="raw_job_listings"):
            tracker_mod.ingest_jobs("co", "batch", "nope")  # type: ignore[arg-type]

    def test_counts_new_and_duplicate_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dup = MagicMock(side_effect=[True, False])
        save = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "raw_job_listing_is_duplicate", dup)
        monkeypatch.setattr(tracker_mod.database, "save_job", save)

        counts = tracker_mod.ingest_jobs("co", "batch-1", ["dup", "fresh"])

        # Keys match tracker.ingest_jobs() return shape (invalid_title replaces legacy title_mismatch).
        assert counts["new"] == 1 and counts["duplicates"] == 1 and counts["invalid_title"] == 0
        save.assert_called_once()
        _, kwargs = save.call_args
        assert kwargs["company"] == "co"
        assert kwargs["state"] == "NEW"

    def test_counts_invalid_title_when_regex_filters_listing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "raw_job_listing_is_duplicate", lambda *args, **kwargs: False)
        save = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "save_job", save)

        counts = tracker_mod.ingest_jobs(
            "co", "batch-1", ["bad title", "Engineer II"], title_matchers=[re.compile(r"Engineer")]
        )

        assert counts["new"] == 1 and counts["duplicates"] == 0 and counts["invalid_title"] == 1
        save.assert_called_once()

    def test_counts_identity_duplicate_bounce_from_save_job(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "raw_job_listing_is_duplicate", lambda *args, **kwargs: False)
        monkeypatch.setattr(tracker_mod.database, "save_job", MagicMock(return_value=False))

        counts = tracker_mod.ingest_jobs("co", "batch-1", ["Engineer role listing"])

        assert counts == {"new": 0, "duplicates": 1, "invalid_title": 0}


# Branches: merge vs replace save_job_data.

class TestSaveJobData:
    def test_merge_and_replace_delegate_to_database(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "save_job", save)

        tracker_mod.save_job_data("job-1", {"a": 1})
        tracker_mod.save_job_data("job-1", {"b": 2}, replace=True)

        assert save.call_args_list[0].kwargs["merge"] is True
        assert save.call_args_list[1].kwargs["merge"] is False


# Branches: existing value; short JD; non-JD missing; self-heal success/failure; job_data coercion.
class TestGetJobData:
    @pytest.mark.asyncio
    async def test_returns_existing_non_jd_value(self) -> None:
        job = {"job_data": {"note": "ok"}}
        assert await tracker_mod.get_job_data(job, "note") == "ok"

    @pytest.mark.asyncio
    async def test_returns_long_job_description_without_scrape(self) -> None:
        jd = "x" * 200
        job = {"job_data": {"job_description": jd}}
        assert await tracker_mod.get_job_data(job, "job_description") == jd

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_non_jd_key(self) -> None:
        job: Dict[str, Any] = {"job_data": {}}
        assert await tracker_mod.get_job_data(job, "missing") is None

    @pytest.mark.asyncio
    async def test_self_heals_short_job_description(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job: Dict[str, Any] = {"astral_job_id": "job-1", "job_data": {"job_description": "short"}}
        scrape = AsyncMock()
        monkeypatch.setattr("src.core.gazer.fetch_jd_batch", scrape)

        await tracker_mod.get_job_data(job, "job_description")

        scrape.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_self_heal_failure_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job: Dict[str, Any] = {"astral_job_id": "job-2", "job_data": {}}
        monkeypatch.setattr("src.core.gazer.fetch_jd_batch", AsyncMock(side_effect=RuntimeError("boom")))

        assert await tracker_mod.get_job_data(job, "job_description") is None

    @pytest.mark.asyncio
    async def test_initializes_non_dict_job_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job: Dict[str, Any] = {"job_data": None}
        monkeypatch.setattr("src.core.gazer.fetch_jd_batch", AsyncMock())

        await tracker_mod.get_job_data(job, "job_description")

        assert isinstance(job["job_data"], dict)


# Branches: missing required parsed fields; nested job_data flatten; column vs metadata split.
class TestInitializeJob:
    def test_requires_title_and_link(self) -> None:
        with pytest.raises(ValueError, match="missing required fields"):
            tracker_mod.initialize_job("job-1", "co", {"company_job_id": "ext-1"})

    def test_omits_nested_job_data_when_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "save_job", save)

        tracker_mod.initialize_job(
            "job-2",
            "co",
            {"company_job_id": "ext-2", "job_title": "Only", "job_link": "https://example.com/only"},
        )

        _, kwargs = save.call_args
        assert kwargs["job_data"] is None

    def test_splits_columns_and_metadata(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "save_job", save)

        tracker_mod.initialize_job(
            "job-1",
            "co",
            {
                "company_job_id": "ext-1",
                "job_title": "Title",
                "job_link": "https://example.com/j",
                "grades": {"x": 1},
                "job_data": {"extra": "value"},
            },
        )

        _, kwargs = save.call_args
        assert kwargs["job_title"] == "Title"
        assert kwargs["job_data"] == {"extra": "value"}
        assert "grades" not in (kwargs["job_data"] or {})


# Branches: canonical lookup; delete single row; collision delete on qualify path.
class TestAst733InitializeJobCollision:
    def test_deletes_current_row_when_canonical_exists(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job(
            "canonical",
            company="acme",
            state="NEW",
            job_title="Engineer",
            company_job_id="ext-1",
            job_link="https://canonical.example/j",
        )
        db.save_job(
            "collision",
            company="acme",
            state="NEW",
            job_title="Temp",
            company_job_id="old",
            job_link="https://collision.example/y",
        )

        assert tracker_mod.initialize_job(
            "collision",
            "acme",
            {
                "company_job_id": "ext-1",
                "job_title": "Engineer",
                "job_link": "https://new.example/j",
            },
        ) is False
        assert db.get_job("collision") is None
        canonical = db.get_job("canonical")
        assert canonical is not None
        assert canonical["job_title"] == "Engineer"
        assert canonical["company_job_id"] == "ext-1"

    def test_saves_when_no_collision(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-new", company="acme", state="NEW", job_link="https://x.example/y")

        assert tracker_mod.initialize_job(
            "job-new",
            "acme",
            {
                "company_job_id": "ext-99",
                "job_title": "Engineer",
                "job_link": "https://example.com/j",
            },
        ) is True
        row = db.get_job("job-new")
        assert row is not None
        assert row["company_job_id"] == "ext-99"
        assert row["job_title"] == "Engineer"

    def test_incomplete_identity_skips_collision_lookup(self, seeded_db, monkeypatch: pytest.MonkeyPatch) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job(
            "job-a",
            company="acme",
            state="NEW",
            job_title="Only",
            company_job_id="x",
            job_link="https://a.example",
        )
        lookup = MagicMock(return_value="canonical")
        monkeypatch.setattr(tracker_mod.database, "get_job_id_by_identity", lookup)
        db.save_job("job-b", company="acme", state="NEW", job_title="Pending", job_link="https://b.example")

        assert tracker_mod.initialize_job(
            "job-b",
            "acme",
            {"job_title": "Only", "job_link": "https://b.example"},
        ) is True
        lookup.assert_not_called()


# Branches: missing job; invalid transition; score optional on transition.
class TestTransitionJobState:
    def test_rejects_missing_job(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "get_job", lambda job_id: None)
        with pytest.raises(ValueError, match="Job not found"):
            tracker_mod.transition_job_state(["job-1"], "VALID_TITLE")

    def test_rejects_invalid_prior_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "get_job", lambda job_id: {"state": "PASSED_JD", "state_history": []})
        with pytest.raises(ValueError, match="Invalid transition"):
            tracker_mod.transition_job_state(["job-1"], "VALID_TITLE")

    def test_appends_history_without_score(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            tracker_mod.database,
            "get_job",
            lambda job_id: {"state": "NEW", "state_history": [], "batch_id": "batch-1"},
        )
        monkeypatch.setattr(tracker_mod.database, "save_job", save)

        tracker_mod.transition_job_state(["job-1"], "VALID_TITLE")

        _, kwargs = save.call_args
        assert "latest_score" not in kwargs
        assert "score" not in kwargs["state_history"][-1]

    def test_appends_history_and_score(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            tracker_mod.database,
            "get_job",
            lambda job_id: {"state": "NEW", "state_history": [], "batch_id": "batch-1"},
        )
        monkeypatch.setattr(tracker_mod.database, "save_job", save)

        tracker_mod.transition_job_state(["job-1"], "VALID_TITLE", score=0.75)

        _, kwargs = save.call_args
        assert kwargs["state"] == "VALID_TITLE"
        assert kwargs["latest_score"] == 0.75
        assert kwargs["state_history"][-1]["score"] == 0.75


# Branches: generated batch_id vs provided; missing context/batch_id error.
class TestBatchApi:
    def test_requires_context_when_batch_id_missing(self) -> None:
        with pytest.raises(ValueError, match="batch_id or context"):
            tracker_mod.get_new_job_batch("NEW")

    def test_claims_and_returns_jobs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        claim = MagicMock()
        jobs: List[Dict[str, Any]] = [{"astral_job_id": "job-1"}]
        monkeypatch.setattr(tracker_mod.database, "claim_job_batch", claim)
        monkeypatch.setattr(tracker_mod.database, "get_job_batch", lambda batch_id: jobs)

        bid, out = tracker_mod.get_new_job_batch("NEW", batch_id="fixed-batch", limit=3, sort_by="state_changed_at")

        assert bid == "fixed-batch"
        assert out == jobs
        claim.assert_called_once()

    def test_compound_build_artifacts_hop_claimable_without_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        claim = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "claim_job_batch", claim)
        monkeypatch.setattr(tracker_mod.database, "get_job_batch", lambda batch_id: [])

        bid, out = tracker_mod.get_new_job_batch(
            "BUILD_ARTIFACTS.finalize_job_resume",
            batch_id="batch-828",
        )

        assert bid == "batch-828"
        assert out == []
        claim.assert_called_once()

    def test_invalid_compound_suffix_still_rejects(self) -> None:
        with pytest.raises(ValueError, match="not in allowed list"):
            tracker_mod.get_new_job_batch(
                "BUILD_ARTIFACTS.not_a_hop",
                batch_id="batch-bad",
            )

    def test_states_list_accepts_legacy_compound_hop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        claim = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "claim_job_batch", claim)
        monkeypatch.setattr(tracker_mod.database, "get_job_batch", lambda batch_id: [])

        tracker_mod.get_new_job_batch(
            "NEW",
            batch_id="batch-multi",
            states=["CANDIDATE_REVIEW", "BUILD_ARTIFACTS.finalize_job_resume"],
        )

        claim.assert_called_once()

    def test_get_and_clear_batch_delegate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "get_job_batch", lambda batch_id: ["job"])
        monkeypatch.setattr(tracker_mod.database, "clear_job_batch", lambda batch_id: 2)

        assert tracker_mod.get_job_batch("batch-1") == ["job"]
        assert tracker_mod.clear_job_batch("batch-1") == 2


class TestAst848DispatchChainTracker:
    """AST-848: runtime hop labels and terminal chain graduation."""

    def test_write_job_dispatch_hop_label(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saves: list[tuple[str, Dict[str, Any]]] = []
        job = {
            "astral_job_id": "job-848",
            "state": cfg.BUILD_ARTIFACTS_BASE_STATE,
            "state_history": [],
            "batch_id": "batch-848",
        }
        monkeypatch.setattr(tracker_mod.database, "get_job", lambda jid: dict(job))
        monkeypatch.setattr(
            tracker_mod.database,
            "save_job",
            lambda jid, **kw: saves.append((jid, kw)),
        )
        label = tracker_mod.write_job_dispatch_hop_label(
            "job-848", cfg.BUILD_ARTIFACTS_BASE_STATE, "anticipate_scan",
        )
        assert label == f"{cfg.BUILD_ARTIFACTS_BASE_STATE}.anticipate_scan"
        assert saves[-1][1]["state"] == label
        assert saves[-1][1]["state_history"][-1]["to_state"] == label

    def test_graduate_from_runtime_hop_label(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        label = cfg.dispatch_hop_label(cfg.BUILD_ARTIFACTS_BASE_STATE, "finalize_job_resume")
        job = {
            "astral_job_id": "job-grad",
            "state": label,
            "state_history": [],
            "batch_id": "batch-grad",
        }
        monkeypatch.setattr(tracker_mod.database, "get_job", lambda jid: dict(job))
        monkeypatch.setattr(tracker_mod, "transition_job_state", transition)
        to_state = tracker_mod.graduate_job_from_dispatch_chain(
            "job-grad", cfg.BUILD_ARTIFACTS_BASE_STATE,
        )
        assert to_state == "CANDIDATE_REVIEW"
        transition.assert_called_once_with(["job-grad"], "CANDIDATE_REVIEW")

    def test_graduate_rejects_unrelated_from_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_job",
            lambda jid: {"astral_job_id": jid, "state": "RECOMMENDED"},
        )
        with pytest.raises(ValueError, match="Invalid chain graduation"):
            tracker_mod.graduate_job_from_dispatch_chain("job-bad", cfg.BUILD_ARTIFACTS_BASE_STATE)


# Branches: thin database facades for UI/API callers.
class TestTrackerFacades:
    def test_delegates_to_database(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "get_job", lambda job_id: {"astral_job_id": job_id})
        monkeypatch.setattr(tracker_mod.database, "list_jobs", lambda **kwargs: ["job"])
        monkeypatch.setattr(tracker_mod.database, "count_jobs", lambda **kwargs: 4)
        monkeypatch.setattr(tracker_mod.database, "save_job", MagicMock())
        monkeypatch.setattr(tracker_mod.database, "score_floor_by_trigger_for_candidate", lambda candidate_id: {"PASSED_JD": 0.5})
        monkeypatch.setattr(tracker_mod.database, "job_misses_dispatch_score_floor", lambda job, floors: True)
        monkeypatch.setattr(tracker_mod.database, "count_jobs_below_dispatch_score_floor", lambda candidate_id: 1)
        monkeypatch.setattr(tracker_mod.database, "list_jobs_below_dispatch_score_floor", lambda candidate_id: ["job"])

        assert tracker_mod.get_job("job-1")["astral_job_id"] == "job-1"
        assert tracker_mod.list_jobs(states=["NEW"]) == ["job"]
        assert tracker_mod.count_jobs(states=["NEW"]) == 4
        tracker_mod.save_job("job-1", state="NEW")
        assert tracker_mod.score_floor_by_trigger_for_candidate("cand-1") == {"PASSED_JD": 0.5}
        assert tracker_mod.job_misses_dispatch_score_floor({}, {}) is True
        assert tracker_mod.count_jobs_below_dispatch_score_floor("cand-1") == 1
        assert tracker_mod.list_jobs_below_dispatch_score_floor("cand-1") == ["job"]

    def test_ast486_consult_layer_facades_delegate_to_database(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # consult routes company / admin timesheets through these wrappers (AST-486).
        # AST-984: append_agent_response facade retired with entity columns.
        monkeypatch.setattr(
            tracker_mod.database,
            "get_company",
            lambda short_name: {"short_name": short_name},
        )
        monkeypatch.setattr(
            tracker_mod.database,
            "list_timesheets",
            lambda **kwargs: [{"batch_id": kwargs.get("batch_id")}],
        )
        assert tracker_mod.get_company("acme")["short_name"] == "acme"
        assert not hasattr(tracker_mod, "append_agent_response")
        assert tracker_mod.list_timesheets(batch_id="b1") == [{"batch_id": "b1"}]


class TestAst302JobArtifacts:
    def test_get_job_artifacts_empty_when_missing(self) -> None:
        assert tracker_mod.get_job_artifacts({}) == {}
        assert tracker_mod.get_job_artifacts({"job_data": "nope"}) == {}

    def test_get_job_artifacts_returns_dict(self) -> None:
        job = {"job_data": {"artifacts": {"resume_content": {"x": 1}}}}
        assert tracker_mod.get_job_artifacts(job) == {"resume_content": {"x": 1}}

    def test_save_job_artifact_resume_content_merges(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: {})
        tracker_mod.save_job_artifact_resume_content("job-1", {"headline": "ok"})
        rc = saved[0]["artifacts"]["resume_content"]
        assert isinstance(rc, dict)
        assert "headline" not in rc


class TestAst309CoverLetterArtifact:
    def test_normalize_cover_letter_coerces_strings(self) -> None:
        out = tracker_mod.normalize_cover_letter_artifact({"re_line": "Re", "body": 1, "signature": None})
        assert out == {"Subject": "Re", "Letter": "1", "signature": ""}

    def test_normalize_cover_letter_non_dict(self) -> None:
        assert tracker_mod.normalize_cover_letter_artifact("text") == {"Subject": "", "Letter": "", "signature": ""}

    def test_save_job_artifact_cover_letter_normalizes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1592: cover lands via catalog write (normalize still applies).
        table: list[tuple] = []
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: table.append(
                (et, eid, at, data, source_artifact_ids)
            )
            or "uuid-cl",
        )
        monkeypatch.setattr(tracker_mod, "_candidate_id_for_job", lambda jid: None)
        uid = tracker_mod.save_job_artifact(
            "job-1", "job.artifacts.cover_letter", {"re_line": "Re", "body": "Hi"}
        )
        assert uid == "uuid-cl"
        assert table[0][:3] == ("job", "job-1", "cover_letter")
        assert table[0][3] == {"Subject": "Re", "Letter": "Hi", "signature": ""}


class TestPersistJobArtifactFromParsed:
    def test_returns_false_without_job_or_non_dict_payload(self) -> None:
        assert tracker_mod.persist_job_artifact_from_parsed("", {"re_line": "", "body": "", "signature": ""}) is False
        assert tracker_mod.persist_job_artifact_from_parsed("job-1", "not-a-dict") is False

    def test_parsed_matches_returns_false_non_dict_payload(self) -> None:
        assert tracker_mod.parsed_matches_artifact_shape("x", "cover_letter") is False

    def test_persists_resume_and_cover_shapes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1592: from-parsed lands via save_job_artifact (catalog keys), not job_data SoT.
        table: list[tuple] = []
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: table.append(
                (et, eid, at, data)
            )
            or f"uuid-{at}",
        )
        monkeypatch.setattr(tracker_mod, "_candidate_id_for_job", lambda jid: None)
        monkeypatch.setattr(
            tracker_mod,
            "_candidate_data_for_job",
            lambda jid: {
                "artifacts": {
                    "resume_structure": [
                        {"id": "professional_summary", "enabled": True, "order": 1},
                        {"id": "core_competencies", "enabled": True, "order": 2},
                        {"id": "experience", "enabled": True, "order": 3},
                    ]
                }
            },
        )
        resume = {
            "candidate_name": "A",
            "candidate_title": "T",
            "candidate_contact_detail": "c",
            "professional_summary": "s",
            "core_competencies": "c",
            "experience": "e",
        }
        assert tracker_mod.persist_job_artifact_from_parsed("job-1", resume) is True
        assert any(t[2] == "job_resume" and t[3].get("professional_summary") == "s" for t in table)
        table.clear()
        assert tracker_mod.persist_job_artifact_from_parsed(
            "job-1", {"re_line": "Re", "body": "Hi", "signature": ""}
        ) is True
        assert any(t[2] == "cover_letter" and t[3].get("Letter") == "Hi" for t in table)


class TestAst518JobResumeArtifacts:
    """AST-518: job resume_content filtered to candidate catalog; cover letter canonical keys."""

    def _candidate_data(self) -> dict:
        from src.core import candidate as candidate_mod

        structure = candidate_mod.default_resume_structure()
        base = {
            "candidate_name": "Ada Lovelace",
            "candidate_title": "Engineer",
            "candidate_contact_detail": "ada@example.com",
            "professional_summary": "Base summary",
        }
        return {"artifacts": {"resume_structure": structure, "base_resume": base}}

    def test_prepare_job_resume_content_strips_orphan_and_snapshots_contact(self) -> None:
        cd = self._candidate_data()
        prepared = tracker_mod._prepare_job_resume_content(
            {
                "orphan_section": "drop me",
                "professional_summary": "Job summary",
                "candidate_name": "Override Name",
            },
            cd,
        )
        assert "orphan_section" not in prepared
        assert prepared["professional_summary"] == "Job summary"
        assert prepared["candidate_name"] == "Override Name"
        assert prepared["candidate_contact_detail"] == "ada@example.com"

    def test_save_job_artifact_resume_content_filters_orphans(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._candidate_data())
        tracker_mod.save_job_artifact_resume_content(
            "job-1",
            {"orphan_section": "nope", "professional_summary": "kept"},
        )
        rc = saved[0]["artifacts"]["resume_content"]
        assert isinstance(rc, dict)
        assert "orphan_section" not in rc
        assert rc["professional_summary"] == "kept"

    def test_normalize_cover_letter_canonical_and_legacy_aliases(self) -> None:
        assert tracker_mod.normalize_cover_letter_artifact(
            {"Subject": "Subj", "Letter": "Body", "signature": "Sig"}
        ) == {"Subject": "Subj", "Letter": "Body", "signature": "Sig"}
        assert tracker_mod.normalize_cover_letter_artifact({"re_line": "Re", "body": "Hi"}) == {
            "Subject": "Re",
            "Letter": "Hi",
            "signature": "",
        }

    def test_parsed_matches_cover_letter_subject_letter_or_legacy(self) -> None:
        assert tracker_mod.parsed_matches_artifact_shape({"Subject": "S", "Letter": "L"}, "cover_letter") is True
        assert tracker_mod.parsed_matches_artifact_shape({"re_line": "R", "body": "B"}, "cover_letter") is True
        assert tracker_mod.parsed_matches_artifact_shape({"Subject": "S"}, "cover_letter") is False


class TestAst551StructureAlignedResumeChain:
    """AST-551: structure-keyed terminal resume persist (subset catalog, no global shape gate)."""

    def _subset_candidate_data(self) -> dict:
        from src.core import candidate as candidate_mod

        structure = candidate_mod.default_resume_structure()
        for sid in list(structure["sections"]):
            structure["sections"][sid]["enabled"] = sid in ("professional_summary", "experience")
        return {"artifacts": {"resume_structure": structure, "base_resume": {}}}

    def test_parsed_matches_resume_content_subset_of_enabled_catalog(self) -> None:
        cd = self._subset_candidate_data()
        assert tracker_mod.parsed_matches_resume_content_shape(
            {"professional_summary": "Summary", "experience": "Exp body"}, cd
        ) is True
        assert tracker_mod.parsed_matches_resume_content_shape(
            {"professional_summary": "only one"}, cd
        ) is True
        assert tracker_mod.parsed_matches_resume_content_shape(
            {"agent_payload": {"professional_summary": "via wrapper", "experience": "e"}}, cd
        ) is True
        assert tracker_mod.parsed_matches_resume_content_shape(
            {"core_competencies": "disabled section"}, cd
        ) is False

    def test_persist_resume_content_without_global_required_keys(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        cd = self._subset_candidate_data()
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: cd)
        assert tracker_mod.persist_job_artifact_from_parsed(
            "job-1", {"professional_summary": "s", "experience": "e"}
        ) is True
        rc = saved[0]["artifacts"]["resume_content"]
        assert isinstance(rc, dict)
        assert rc["professional_summary"] == "s"
        assert rc["experience"] == "e"

    def test_parsed_matches_resume_content_false_when_no_enabled_body(self) -> None:
        cd = self._subset_candidate_data()
        assert tracker_mod.parsed_matches_resume_content_shape(
            {"professional_summary": "   ", "experience": ""}, cd
        ) is False
        assert tracker_mod.parsed_matches_resume_content_shape(
            {"core_competencies": "wrong catalog key only"}, cd
        ) is False


class TestAst552BuildArtifactsGate:
    """AST-552: BUILD_ARTIFACTS gate helpers — structure match, persist body gate, rollback."""

    def _subset_candidate_data(self) -> dict:
        from src.core import candidate as candidate_mod

        structure = candidate_mod.default_resume_structure()
        for sid in list(structure["sections"]):
            structure["sections"][sid]["enabled"] = sid in ("professional_summary", "experience")
        return {"artifacts": {"resume_structure": structure, "base_resume": {}}}

    def test_parsed_matches_job_resume_content_requires_non_contact_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cd = self._subset_candidate_data()
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: cd)
        assert tracker_mod.parsed_matches_job_resume_content("job-1", {"professional_summary": "Summary"}) is True
        assert tracker_mod.parsed_matches_job_resume_content(
            "job-1",
            {
                "candidate_name": "Ada",
                "candidate_title": "Eng",
                "candidate_contact_detail": "ada@example.com",
            },
        ) is False
        assert tracker_mod.parsed_matches_job_resume_content("job-1", {"core_competencies": "disabled"}) is False

    def test_job_has_persisted_resume_body_checks_non_contact_sections(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cd = self._subset_candidate_data()
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: cd)
        assert tracker_mod.job_has_persisted_resume_body(
            "job-1",
            {"job_data": {"artifacts": {"resume_content": {"professional_summary": "ok"}}}},
        ) is True
        assert tracker_mod.job_has_persisted_resume_body(
            "job-1",
            {"job_data": {"artifacts": {"resume_content": {"candidate_name": "only contact"}}}},
        ) is False

    def test_clear_job_artifact_resume_content_drops_resume_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[tuple[str, dict, bool]] = []

        def _save(jid: str, payload: dict, replace: bool = False) -> None:
            saved.append((jid, payload, replace))

        monkeypatch.setattr(
            tracker_mod,
            "get_job",
            lambda jid: {
                "astral_job_id": jid,
                "job_data": {"artifacts": {"resume_content": {"professional_summary": "x"}, "cover_letter": {}}},
            },
        )
        monkeypatch.setattr(tracker_mod, "save_job_data", _save)
        tracker_mod.clear_job_artifact_resume_content("job-1")
        assert saved[0][0] == "job-1"
        art = saved[0][1]["artifacts"]
        assert "resume_content" not in art
        assert "cover_letter" in art


class TestAst562ArtifactBuildTransitions:
    """AST-562 — explicit generate/cancel; clear partial artifacts + batch lock on cancel."""

    def _set_job_batch(self, db, job_id: str, batch_id: str) -> None:
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE job SET batch_id = ?, batch_created_at = datetime('now') WHERE astral_job_id = ?",
                (batch_id, job_id),
            )
            conn.commit()
        finally:
            conn.close()

    def test_start_artifact_build_from_recommended(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-562", company="acme", state="RECOMMENDED", job_data={"artifacts": {}})
        assert tracker_mod.start_artifact_build("job-562") == cfg.BUILD_ARTIFACTS_BASE_STATE
        assert db.get_job("job-562")["state"] == cfg.BUILD_ARTIFACTS_BASE_STATE

    def test_start_artifact_build_rejects_wrong_state(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-562", company="acme", state="NEW", job_data={})
        with pytest.raises(ValueError, match="generate only from RECOMMENDED"):
            tracker_mod.start_artifact_build("job-562")

    def test_clear_job_build_artifacts_patches_listed_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[tuple[str, dict, bool]] = []

        def _save(jid: str, payload: dict, replace: bool = False) -> None:
            saved.append((jid, payload, replace))

        monkeypatch.setattr(
            tracker_mod,
            "get_job",
            lambda jid: {
                "job_data": {
                    "artifacts": {
                        "resume_content": {"professional_summary": "draft"},
                        "cover_letter": {"body": "hi"},
                        "analysis_upshot": {"summary": "keep"},
                    }
                }
            },
        )
        monkeypatch.setattr(tracker_mod, "save_job_data", _save)
        tracker_mod.clear_job_build_artifacts("job-562")
        assert saved[0][0] == "job-562"
        assert saved[0][2] is True
        art = saved[0][1]["artifacts"]
        assert "resume_content" not in art
        assert "cover_letter" not in art
        assert art["analysis_upshot"] == {"summary": "keep"}

    def test_cancel_transitions_and_releases_batch_lock(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job(
            "job-562",
            company="acme",
            state="RECOMMENDED",
            job_data={
                "artifacts": {
                    "resume_content": {"professional_summary": "draft"},
                    "cover_letter": {"body": "hi"},
                    "analysis_upshot": {"summary": "keep"},
                }
            },
        )
        tracker_mod.start_artifact_build("job-562")
        self._set_job_batch(db, "job-562", "batch-562")
        assert tracker_mod.cancel_artifact_build("job-562") == "RECOMMENDED"
        row = db.get_job("job-562")
        assert row["state"] == "RECOMMENDED"
        assert row["batch_id"] is None
        assert row["job_data"]["artifacts"]["analysis_upshot"] == {"summary": "keep"}

    def test_cancel_persists_cleared_build_artifact_keys(self, seeded_db) -> None:
        """AC: partial artifacts cleared on cancel — fails until tracker removes keys or replace-merge (AST-552 pattern)."""
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job(
            "job-562b",
            company="acme",
            state="RECOMMENDED",
            job_data={
                "artifacts": {
                    "resume_content": {"professional_summary": "draft"},
                    "cover_letter": {"body": "hi"},
                }
            },
        )
        tracker_mod.start_artifact_build("job-562b")
        tracker_mod.cancel_artifact_build("job-562b")
        art = db.get_job("job-562b")["job_data"]["artifacts"]
        assert "resume_content" not in art
        assert "cover_letter" not in art

    def test_cancel_from_mid_hop_compound_state(self, seeded_db) -> None:
        from src.utils.config import resume_artifact_compound_state

        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        mid = resume_artifact_compound_state("contemplate_job")
        db.save_job("job-562mid", company="acme", state=mid, job_data={"artifacts": {"resume_content": {"x": 1}}})
        assert tracker_mod.cancel_artifact_build("job-562mid") == "RECOMMENDED"
        assert db.get_job("job-562mid")["state"] == "RECOMMENDED"

    def test_cancel_rejects_wrong_state(self, seeded_db) -> None:
        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-562", company="acme", state="RECOMMENDED", job_data={})
        with pytest.raises(ValueError, match="cancel only from BUILD_ARTIFACTS in-progress states"):
            tracker_mod.cancel_artifact_build("job-562")


class TestAst311CandidateResults:
    def test_get_candidate_results_defaults_empty(self) -> None:
        assert tracker_mod.get_candidate_results({}) == {}

    def test_set_candidate_result_writes_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        tracker_mod.set_candidate_result("job-1", "applied", notes="note")
        entry = saved[0]["candidate_results"]["applied"]
        assert entry["notes"] == "note"
        assert "timestamp" in entry


class TestAst997ExperienceJobArrayPersist:
    """AST-997: tracker resume persist/match gates keep experience job arrays."""

    def _jobs(self) -> list[dict[str, str]]:
        return [
            {
                "company": "Acme Corp",
                "title": "Engineer",
                "dates": "2020-2023",
                "location": "Remote",
                "accomplishments": "Shipped widgets",
            }
        ]

    def _subset_cd(self) -> dict:
        from src.core import candidate as candidate_mod

        structure = candidate_mod.default_resume_structure()
        for sid in list(structure["sections"]):
            structure["sections"][sid]["enabled"] = sid in ("professional_summary", "experience")
        return {
            "artifacts": {
                "resume_structure": structure,
                "base_resume": {"experience": self._jobs()},
            }
        }

    def test_resume_payload_body_keeps_job_array(self) -> None:
        jobs = self._jobs()
        body = tracker_mod._resume_payload_body(
            {"professional_summary": "S", "experience": jobs, "orphan": {"x": 1}}
        )
        assert body["professional_summary"] == "S"
        assert body["experience"] == jobs
        assert "orphan" not in body

    def test_parsed_matches_when_experience_is_job_array_only(self) -> None:
        cd = self._subset_cd()
        assert tracker_mod.parsed_matches_resume_content_shape({"experience": self._jobs()}, cd) is True
        assert tracker_mod.parsed_matches_resume_content_shape({"experience": []}, cd) is False

    def test_persist_stores_experience_job_array(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._subset_cd())
        jobs = self._jobs()
        assert tracker_mod.persist_job_artifact_from_parsed(
            "job-997", {"professional_summary": "S", "experience": jobs}
        ) is True
        rc = saved[0]["artifacts"]["resume_content"]
        assert rc["experience"] == jobs
        assert rc["professional_summary"] == "S"

    def test_job_has_persisted_resume_body_for_job_array(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._subset_cd())
        job = {"job_data": {"artifacts": {"resume_content": {"experience": self._jobs()}}}}
        assert tracker_mod.job_has_persisted_resume_body("job-997", job) is True
        empty = {"job_data": {"artifacts": {"resume_content": {"experience": []}}}}
        assert tracker_mod.job_has_persisted_resume_body("job-997", empty) is False


class TestAst1099PinJobArtifactAgentDataId:
    """AST-1099: pin RESPONSE agent_data_id into job_data.artifacts (never store empty)."""

    def test_pins_nonempty_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        assert tracker_mod.pin_job_artifact_agent_data_id(
            "job-1099", "job_resume", "batch-1-response-abcd"
        ) is True
        assert saved == [{"artifacts": {"job_resume": "batch-1-response-abcd"}}]

    def test_strips_whitespace_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        assert tracker_mod.pin_job_artifact_agent_data_id(
            "job-1099", "cover_letter", "  id-42  "
        ) is True
        assert saved[0]["artifacts"]["cover_letter"] == "id-42"

    def test_empty_id_skips_write(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        assert tracker_mod.pin_job_artifact_agent_data_id("job-1099", "job_resume", "") is False
        assert tracker_mod.pin_job_artifact_agent_data_id("job-1099", "job_resume", "   ") is False
        assert tracker_mod.pin_job_artifact_agent_data_id("job-1099", "job_resume", None) is False
        assert saved == []

    def test_missing_job_or_key_skips(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        assert tracker_mod.pin_job_artifact_agent_data_id("", "job_resume", "id-1") is False
        assert tracker_mod.pin_job_artifact_agent_data_id("job-1099", "", "id-1") is False
        assert saved == []

    def test_debug_true_logs_recorded_and_skip(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: None)
        caplog.set_level("DEBUG")
        assert tracker_mod.pin_job_artifact_agent_data_id(
            "job-1099", "proposed_answers", "resp-9", debug=True
        ) is True
        assert tracker_mod.pin_job_artifact_agent_data_id(
            "job-1099", "proposed_answers", "", debug=True
        ) is False
        combined = "\n".join(r.message for r in caplog.records)
        assert "artifact_pin key=proposed_answers agent_data_id=resp-9 recorded" in combined
        assert "artifact_pin key=proposed_answers skipped reason=empty_agent_data_id" in combined

    def test_clear_job_build_artifacts_removes_pin_slots(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saved: list[tuple[str, dict, bool]] = []

        def _save(jid: str, payload: dict, replace: bool = False) -> None:
            saved.append((jid, payload, replace))

        monkeypatch.setattr(
            tracker_mod,
            "get_job",
            lambda jid: {
                "job_data": {
                    "artifacts": {
                        "job_resume": "id-resume",
                        "cover_letter": "id-cover",
                        "proposed_answers": "id-answers",
                        "analysis_upshot": {"summary": "keep"},
                    }
                }
            },
        )
        monkeypatch.setattr(tracker_mod, "save_job_data", _save)
        tracker_mod.clear_job_build_artifacts("job-1099")
        art = saved[0][1]["artifacts"]
        assert "job_resume" not in art
        assert "cover_letter" not in art
        assert "proposed_answers" not in art
        assert art["analysis_upshot"] == {"summary": "keep"}


class TestAst1100ResolveHydrateJobArtifactPins:
    """AST-1100: pin string → agent_data body resolve + display hydrate (no save)."""

    def test_resolve_returns_parsed_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_agent_data",
            lambda aid: {"block_data": '{"professional_summary": "Pinned"}'},
        )
        body = tracker_mod.resolve_job_artifact_agent_data_body("batch-1-response-aaaa")
        assert body == {"professional_summary": "Pinned"}

    def test_resolve_unwraps_agent_payload(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_agent_data",
            lambda aid: {"block_data": '{"agent_payload": {"re_line": "Re", "body": "Hi"}}'},
        )
        body = tracker_mod.resolve_job_artifact_agent_data_body("id-1")
        assert body == {"re_line": "Re", "body": "Hi"}

    def test_resolve_empty_or_missing_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "get_agent_data", lambda aid: None)
        assert tracker_mod.resolve_job_artifact_agent_data_body("") is None
        assert tracker_mod.resolve_job_artifact_agent_data_body("   ") is None
        assert tracker_mod.resolve_job_artifact_agent_data_body(None) is None
        assert tracker_mod.resolve_job_artifact_agent_data_body("missing-id") is None

    def test_resolve_debug_logs_recorded_and_skip(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_agent_data",
            lambda aid: {"block_data": '{"x": 1}'},
        )
        caplog.set_level("DEBUG")
        assert tracker_mod.resolve_job_artifact_agent_data_body("id-ok", debug=True) == {"x": 1}
        assert tracker_mod.resolve_job_artifact_agent_data_body("", debug=True) is None
        combined = "\n".join(r.message for r in caplog.records)
        assert "artifact_resolve agent_data_id=id-ok recorded" in combined
        assert "artifact_resolve skipped reason=empty_agent_data_id" in combined

    def test_hydrate_operator_slots_no_pin_resolve_proposed_answers_still_resolves(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1548/1554: job_resume/cover_letter pin strings stay; proposed_answers still resolves.
        resolve_calls: list[str] = []

        def _resolve(pin: str, debug: bool = False) -> dict:
            resolve_calls.append(pin)
            return {"body": pin}

        monkeypatch.setattr(tracker_mod, "resolve_job_artifact_agent_data_body", _resolve)
        out = tracker_mod.hydrate_job_artifacts_for_display(
            {
                "job_resume": "pin-resume",
                "cover_letter": {"Subject": "keep"},
                "proposed_answers": "pin-answers",
                "analysis_upshot": {"summary": "x"},
            }
        )
        assert out["job_resume"] == "pin-resume"
        # AST-1116: legacy/partial cover dicts normalize to Subject/Letter/signature spine.
        assert out["cover_letter"] == {"Subject": "keep", "Letter": "", "signature": ""}
        assert out["proposed_answers"] == {"body": "pin-answers"}
        assert out["analysis_upshot"] == {"summary": "x"}
        assert resolve_calls == ["pin-answers"]

    def test_hydrate_job_resume_dict_wins_over_resume_content_sibling(self) -> None:
        out = tracker_mod.hydrate_job_artifacts_for_display(
            {
                "job_resume": {"professional_summary": "on-slot"},
                "resume_content": {"professional_summary": "sibling"},
            }
        )
        assert out["job_resume"] == {"professional_summary": "on-slot"}

    def test_hydrate_overlays_resume_content_when_job_resume_pin_or_empty(self) -> None:
        out_pin = tracker_mod.hydrate_job_artifacts_for_display(
            {
                "job_resume": "legacy-pin",
                "resume_content": {"professional_summary": "sibling"},
            }
        )
        assert out_pin["job_resume"] == {"professional_summary": "sibling"}
        out_empty = tracker_mod.hydrate_job_artifacts_for_display(
            {
                "job_resume": {},
                "resume_content": {"professional_summary": "sibling"},
            }
        )
        assert out_empty["job_resume"] == {"professional_summary": "sibling"}

    def test_hydrate_non_dict_returns_empty(self) -> None:
        assert tracker_mod.hydrate_job_artifacts_for_display(None) == {}
        assert tracker_mod.hydrate_job_artifacts_for_display("nope") == {}

    def test_hydrate_does_not_save(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda *a, **k: saved.append(1))
        monkeypatch.setattr(
            tracker_mod,
            "resolve_job_artifact_agent_data_body",
            lambda pin, debug=False: {"ok": True},
        )
        tracker_mod.hydrate_job_artifacts_for_display({"proposed_answers": "pin-1"})
        assert saved == []

class TestAst1116HydrateCoverLetterNormalize:
    """AST-1116/1548: hydrate overlay normalizes cover_letter dict; pin strings → no resolve."""

    def test_hydrate_leaves_cover_pin_string_without_resolve(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        resolve_calls: list[str] = []
        monkeypatch.setattr(
            tracker_mod,
            "resolve_job_artifact_agent_data_body",
            lambda pin, debug=False: resolve_calls.append(pin) or {
                "re_line": "Re: Role",
                "body": "Hello",
                "signature": "Ada",
            },
        )
        out = tracker_mod.hydrate_job_artifacts_for_display({"cover_letter": "pin-cover"})
        assert out["cover_letter"] == "pin-cover"
        assert resolve_calls == []

    def test_hydrate_normalizes_legacy_body_dict(self) -> None:
        out = tracker_mod.hydrate_job_artifacts_for_display(
            {"cover_letter": {"re_line": "Re", "body": "Hi", "signature": ""}}
        )
        assert out["cover_letter"] == {"Subject": "Re", "Letter": "Hi", "signature": ""}

    def test_hydrate_cover_normalize_does_not_save(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saved: list = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda *a, **k: saved.append(1))
        tracker_mod.hydrate_job_artifacts_for_display(
            {"cover_letter": {"re_line": "Re", "body": "Hi"}}
        )
        assert saved == []


class TestAst1504CoverLetterHydrateDisplayGaps:
    """AST-1504 gaps flipped for AST-1548: operator hydrate uses job cover dict only (no pin resolve)."""

    def test_hydrate_unwraps_nested_cover_dict_to_subject_letter(self) -> None:
        """Nested cover keys on the job dict become Subject/Letter for JAR tabs."""
        out = tracker_mod.hydrate_job_artifacts_for_display(
            {
                "cover_letter": {
                    "hop": {
                        "re_line": "Re: Nest",
                        "body": "Nested letter body",
                        "signature": "Ada",
                    },
                }
            }
        )
        assert out["cover_letter"] == {
            "Subject": "Re: Nest",
            "Letter": "Nested letter body",
            "signature": "Ada",
        }

    def test_hydrate_does_not_install_empty_spine_for_non_cover_dict(self) -> None:
        """Nonempty gate — unrelated dict must not become an all-empty Subject/Letter/signature spine."""
        out = tracker_mod.hydrate_job_artifacts_for_display(
            {"cover_letter": {"unrelated": "meta"}}
        )
        empty_spine = {"Subject": "", "Letter": "", "signature": ""}
        assert out["cover_letter"] != empty_spine
        assert out["cover_letter"] == {"unrelated": "meta"}

    def test_hydrate_leaves_cover_pin_string(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1548: pin string on cover_letter is not resolved for operator hydrate."""
        monkeypatch.setattr(
            tracker_mod,
            "resolve_job_artifact_agent_data_body",
            lambda pin, debug=False: {"unrelated": "meta"},
        )
        out = tracker_mod.hydrate_job_artifacts_for_display({"cover_letter": "pin-cover"})
        assert out["cover_letter"] == "pin-cover"


class TestAst1554BodyReplicaPersistHelpers:
    """AST-1554 body-replica helpers — AST-1592 routes via save_job_artifact / prepare_job_replica_body."""

    def _resume_cd(self) -> dict:
        return {
            "artifacts": {
                "resume_structure": [
                    {"id": "professional_summary", "enabled": True, "order": 1},
                    {"id": "experience", "enabled": True, "order": 2},
                ]
            }
        }

    def test_save_job_artifact_job_resume_writes_artifacts_table(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1556/1592: authoritative write is database.save_artifact via catalog key.
        table: list[tuple] = []
        job_data: list[dict] = []
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: table.append(
                (et, eid, at, data, source_artifact_ids)
            )
            or "uuid-jr",
        )
        monkeypatch.setattr(
            tracker_mod, "save_job_data", lambda jid, payload, **k: job_data.append(payload)
        )
        monkeypatch.setattr(tracker_mod, "_candidate_id_for_job", lambda jid: None)
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._resume_cd())
        uid = tracker_mod.save_job_artifact(
            "job-1554",
            "job.artifacts.job_resume",
            {"professional_summary": "S", "experience": []},
        )
        assert uid == "uuid-jr"
        assert table, "expected artifacts-table write for job_resume"
        assert table[0][0] == "job"
        assert table[0][1] == "job-1554"
        assert table[0][2] == "job_resume"
        assert table[0][3]["professional_summary"] == "S"
        assert table[0][4] == []  # no base_resume → empty sources
        for payload in job_data:
            art = (payload or {}).get("artifacts") or {}
            assert "job_resume" not in art
            assert "resume_content" not in art

    def test_prepare_job_replica_body_resume_coat_check(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            tracker_mod, "parsed_matches_job_resume_content", lambda jid, parsed: False
        )
        assert (
            tracker_mod.prepare_job_replica_body(
                "job.artifacts.job_resume", {}, astral_job_id="job-1554"
            )
            is None
        )

    def test_save_job_artifact_cover_letter_writes_artifacts_table(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        table: list[tuple] = []
        job_data: list[dict] = []
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: table.append(
                (et, eid, at, data, source_artifact_ids)
            )
            or "uuid-cl",
        )
        monkeypatch.setattr(
            tracker_mod, "save_job_data", lambda jid, payload, **k: job_data.append(payload)
        )
        uid = tracker_mod.save_job_artifact(
            "job-1554",
            "job.artifacts.cover_letter",
            {"re_line": "Re: Role", "body": "Hello", "signature": "Ada"},
        )
        assert uid == "uuid-cl"
        assert table
        assert table[0][:3] == ("job", "job-1554", "cover_letter")
        assert table[0][3] == {
            "Subject": "Re: Role",
            "Letter": "Hello",
            "signature": "Ada",
        }
        for payload in job_data:
            art = (payload or {}).get("artifacts") or {}
            assert "cover_letter" not in art

    def test_prepare_job_replica_body_cover_coat_check_empty(self) -> None:
        assert (
            tracker_mod.prepare_job_replica_body(
                "job.artifacts.cover_letter",
                {"re_line": "", "body": "", "signature": ""},
                astral_job_id="job-1554",
            )
            is None
        )


class TestAst1556JobArtifactsTableSoT:
    """AST-1556 [bug-repro]: job_resume/cover_letter SoT is artifacts table (not job_data blob)."""

    def _resume_cd(self) -> dict:
        return {
            "artifacts": {
                "resume_structure": [
                    {"id": "professional_summary", "enabled": True, "order": 1},
                    {"id": "experience", "enabled": True, "order": 2},
                ]
            }
        }

    def test_save_job_resume_body_writes_artifacts_table_not_job_data(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """[bug-repro] After Save/finalize, current row must exist in artifacts table — not job_data."""
        table: list[tuple] = []
        job_data: list[dict] = []
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: table.append(
                (et, eid, at, data)
            )
            or "uuid-1556",
        )
        monkeypatch.setattr(
            tracker_mod, "save_job_data", lambda jid, payload, **k: job_data.append(payload)
        )
        monkeypatch.setattr(tracker_mod, "_candidate_id_for_job", lambda jid: None)
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._resume_cd())
        tracker_mod.save_job_artifact(
            "job-1556",
            "job.artifacts.job_resume",
            {"professional_summary": "Table SoT", "experience": []},
        )
        assert table, "pre-fix writes job_data only — make-fix must call save_artifact"
        assert table[0] == (
            "job",
            "job-1556",
            "job_resume",
            table[0][3],
        )
        assert table[0][3]["professional_summary"] == "Table SoT"
        for payload in job_data:
            art = (payload or {}).get("artifacts") or {}
            assert "job_resume" not in art and "resume_content" not in art

    def test_save_cover_letter_writes_artifacts_table_not_job_data(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """[bug-repro] Cover editable body must land as artifacts-table current row."""
        table: list[tuple] = []
        job_data: list[dict] = []
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: table.append(
                (et, eid, at, data)
            )
            or "uuid-cl",
        )
        monkeypatch.setattr(
            tracker_mod, "save_job_data", lambda jid, payload, **k: job_data.append(payload)
        )
        tracker_mod.save_job_artifact(
            "job-1556",
            "job.artifacts.cover_letter",
            {"re_line": "Re: Role", "body": "Hello", "signature": "Ada"},
        )
        assert table, "pre-fix cover save writes job_data only"
        assert table[0][:3] == ("job", "job-1556", "cover_letter")
        assert table[0][3] == {
            "Subject": "Re: Role",
            "Letter": "Hello",
            "signature": "Ada",
        }
        for payload in job_data:
            assert "cover_letter" not in ((payload or {}).get("artifacts") or {})

    def test_hydrate_overlays_artifacts_table_currents(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """[bug-repro] Operator hydrate must read get_current_artifact for job_resume/cover_letter."""
        import inspect

        gets: list[tuple] = []

        def _get(et: str, eid: str, at: str):
            gets.append((et, eid, at))
            if at == "job_resume":
                return {"artifact_data": {"professional_summary": "from-table"}, "current": 1}
            if at == "cover_letter":
                return {
                    "artifact_data": {"Subject": "Re", "Letter": "Hi", "signature": "A"},
                    "current": 1,
                }
            return None

        monkeypatch.setattr(tracker_mod.database, "get_current_artifact", _get)
        sig = inspect.signature(tracker_mod.hydrate_job_artifacts_for_display)
        kwargs = {"astral_job_id": "job-1556"} if "astral_job_id" in sig.parameters else {}
        out = tracker_mod.hydrate_job_artifacts_for_display({}, **kwargs)
        assert ("job", "job-1556", "job_resume") in gets
        assert ("job", "job-1556", "cover_letter") in gets
        assert out.get("job_resume", {}).get("professional_summary") == "from-table"
        assert out.get("cover_letter", {}).get("Letter") == "Hi"

    def test_clear_job_build_artifacts_retires_table_currents(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """[bug-repro] Cancel must retire artifacts-table currents for job_resume/cover_letter."""
        retired: list[tuple] = []

        def _retire(et: str, eid: str, at: str) -> bool:
            retired.append((et, eid, at))
            return True

        monkeypatch.setattr(
            tracker_mod.database, "retire_current_artifact", _retire, raising=False
        )
        monkeypatch.setattr(
            tracker_mod,
            "get_job",
            lambda jid: {
                "astral_job_id": jid,
                "job_data": {
                    "artifacts": {
                        "job_resume": {"professional_summary": "x"},
                        "cover_letter": {"Subject": "Re"},
                        "resume_content": {"professional_summary": "x"},
                    }
                },
            },
        )
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda *a, **k: None)
        tracker_mod.clear_job_build_artifacts("job-1556")
        assert ("job", "job-1556", "job_resume") in retired
        assert ("job", "job-1556", "cover_letter") in retired


class TestAst1270NestedResumePayloadBody:
    """AST-1270: _resume_payload_body prefers nested resume; ignores notes envelope."""

    def test_prefers_nested_resume_dict(self) -> None:
        body = tracker_mod._resume_payload_body(
            {
                "agent_payload": {
                    "resume": {
                        "professional_summary": "from-nest",
                        "experience": "nested-jobs",
                    },
                    "professional_summary": "flat-should-lose",
                    "notes": ["skipped UAT claim"],
                }
            }
        )
        assert body == {
            "professional_summary": "from-nest",
            "experience": "nested-jobs",
        }
        assert "notes" not in body
        assert "resume" not in body

    def test_flat_unwrapped_payload_unchanged(self) -> None:
        body = tracker_mod._resume_payload_body(
            {"agent_payload": {"professional_summary": "S", "experience": "E"}}
        )
        assert body == {"professional_summary": "S", "experience": "E"}


class TestAst1523NotesMetadataRetention:
    """AST-1523: extract/save freeform notes; resume body never includes metadata keys."""

    def test_extract_nested_envelope_reads_notes(self) -> None:
        parsed = {
            "agent_payload": {
                "resume": {"professional_summary": "S"},
                "notes": ["skipped UAT claim"],
            }
        }
        assert tracker_mod.extract_draft_job_resume_notes(parsed) == ["skipped UAT claim"]

    def test_extract_absent_returns_none(self) -> None:
        assert (
            tracker_mod.extract_draft_job_resume_notes(
                {"agent_payload": {"professional_summary": "S"}}
            )
            is None
        )

    def test_extract_coerces_string_and_drops_blanks(self) -> None:
        assert tracker_mod.extract_draft_job_resume_notes(
            {"agent_payload": {"notes": "  one note  "}}
        ) == ["one note"]
        assert tracker_mod.extract_draft_job_resume_notes(
            {"agent_payload": {"notes": ["keep", "  ", ""]}}
        ) == ["keep"]

    def test_persist_saves_under_artifact_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict] = []
        monkeypatch.setattr(
            tracker_mod,
            "save_job_data",
            lambda jid, payload: saved.append({"jid": jid, **payload}),
        )
        ok = tracker_mod.persist_draft_job_resume_notes(
            "job-1523",
            {"agent_payload": {"notes": ["a", "b"], "professional_summary": "S"}},
        )
        assert ok is True
        assert saved == [{"jid": "job-1523", "artifacts": {"notes": ["a", "b"]}}]

    def test_persist_absent_key_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda *a, **k: saved.append(1))
        assert (
            tracker_mod.persist_draft_job_resume_notes(
                "job-1523", {"agent_payload": {"professional_summary": "S"}}
            )
            is False
        )
        assert saved == []

    def test_resume_body_skips_notes_metadata(self) -> None:
        body = tracker_mod._resume_payload_body(
            {
                "agent_payload": {
                    "professional_summary": "S",
                    "notes": "looks-like-a-section",
                }
            }
        )
        assert body == {"professional_summary": "S"}
        assert "notes" not in body

    def test_persist_job_artifact_writes_notes_not_resume_content(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.core import candidate as candidate_mod

        saved: list[dict] = []
        monkeypatch.setattr(
            tracker_mod,
            "save_job_data",
            lambda jid, payload: saved.append(payload),
        )
        monkeypatch.setattr(
            tracker_mod,
            "_candidate_data_for_job",
            lambda jid: {
                "artifacts": {
                    "base_resume": {"professional_summary": "base"},
                    "resume_structure": candidate_mod.default_resume_structure(),
                }
            },
        )
        parsed = {
            "agent_payload": {
                "resume": {"professional_summary": "tailored"},
                "notes": ["note"],
            }
        }
        assert tracker_mod.persist_job_artifact_from_parsed("job-1523", parsed) is True
        arts = [p.get("artifacts") for p in saved]
        resume_writes = [a for a in arts if a and "resume_content" in a]
        note_writes = [a for a in arts if a and "notes" in a]
        assert resume_writes
        assert "notes" not in resume_writes[0]["resume_content"]
        assert note_writes and note_writes[0]["notes"] == ["note"]

    def test_clear_job_build_artifacts_removes_notes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saved: list[tuple[str, dict, bool]] = []

        def _save(jid: str, payload: dict, replace: bool = False) -> None:
            saved.append((jid, payload, replace))

        monkeypatch.setattr(
            tracker_mod,
            "get_job",
            lambda jid: {
                "job_data": {
                    "artifacts": {
                        "resume_content": {"professional_summary": "draft"},
                        "notes": ["old note"],
                        "analysis_upshot": {"summary": "keep"},
                    }
                }
            },
        )
        monkeypatch.setattr(tracker_mod, "save_job_data", _save)
        tracker_mod.clear_job_build_artifacts("job-1523")
        art = saved[0][1]["artifacts"]
        assert "notes" not in art
        assert "resume_content" not in art
        assert art["analysis_upshot"] == {"summary": "keep"}


class TestAst1523EpicHelpersRemoved:
    """AST-1523: hard-contract persist/validate helpers removed from tracker."""

    def test_epic_helpers_removed(self) -> None:
        assert not hasattr(tracker_mod, "extract_draft_job_resume_deviations")
        assert not hasattr(tracker_mod, "persist_draft_job_resume_deviations")
        assert not hasattr(tracker_mod, "extract_draft_job_resume_advice_adherence")
        assert not hasattr(tracker_mod, "persist_draft_job_resume_advice_adherence")
        assert not hasattr(tracker_mod, "get_job_resume_advice_codes")
        assert not hasattr(tracker_mod, "extract_advise_job_resume_coded_advice")
        assert not hasattr(tracker_mod, "persist_advise_job_resume_coded_advice")


class TestAst1305JobResumeExtras:
    """AST-1305: job persist keeps base-derived extras; invented keys stay out."""

    def test_prepare_keeps_base_extra_and_drops_invented(self) -> None:
        from src.core import candidate as candidate_mod

        structure = candidate_mod.default_resume_structure()
        cd = {
            "artifacts": {
                "resume_structure": structure,
                "base_resume": {
                    "professional_summary": "S",
                    "highlights": "Won awards",
                },
            }
        }
        prepared = tracker_mod._prepare_job_resume_content(
            {
                "professional_summary": "Job S",
                "highlights": "Job highlights",
                "invented_section": "nope",
            },
            cd,
        )
        assert prepared["professional_summary"] == "Job S"
        assert prepared["highlights"] == "Job highlights"
        assert "invented_section" not in prepared


class TestAst1420AssembleJobCopySnapshot:
    """AST-1420: stored job + populated hop blocks; artifact pins stay ids."""

    _PIN = "pin-resp"
    _HOP = "hop-task"
    _JOB = {
        "astral_job_id": "job-1420",
        "job_data": {"artifacts": {"job_resume": "pin-resp"}},
        "state": "IN_REVIEW",
        "n": 7,  # non-string walk ignore
    }

    def _wire(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        job: Any,
        hits: List[str] | None = None,
        refs: List[dict] | None = None,
        seeds: Dict[str, Any] | None = None,
        batches: Dict[str, List[dict]] | None = None,
        refs_exc: Exception | None = None,
        seed_exc: Dict[str, Exception] | None = None,
    ) -> MagicMock:
        hits = hits or []
        seeds = seeds or {}
        batches = batches or {}
        seed_exc = seed_exc or {}
        batch_calls: list[str] = []

        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: job)

        def _for_ids(ids: List[str]) -> dict:
            return {i: {"agent_data_id": i} for i in ids if i in hits}

        monkeypatch.setattr(tracker_mod.database, "get_agent_data_for_ids", _for_ids)

        if refs_exc is not None:
            monkeypatch.setattr(
                tracker_mod.database,
                "list_entity_latest_agent_refs",
                MagicMock(side_effect=refs_exc),
            )
        else:
            monkeypatch.setattr(
                tracker_mod.database,
                "list_entity_latest_agent_refs",
                lambda et, eid: list(refs or []),
            )

        def _seed(aid: str) -> Any:
            if aid in seed_exc:
                raise seed_exc[aid]
            return seeds.get(aid)

        def _batch(bid: str) -> List[dict]:
            batch_calls.append(bid)
            return list(batches.get(bid) or [])

        monkeypatch.setattr(tracker_mod.database, "get_agent_data", _seed)
        monkeypatch.setattr(tracker_mod.database, "get_agent_data_by_batch", _batch)
        spy = MagicMock()
        spy.batch_calls = batch_calls
        return spy

    def test_missing_job_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._wire(monkeypatch, job=None)
        assert tracker_mod.assemble_job_copy_snapshot("missing") is None

    def test_empty_walk_and_no_refs_returns_empty_agent_data(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # No string values → skip get_agent_data_for_ids (else {}).
        called: list[object] = []
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: {"n": 1, "xs": [2, None], "pad": "   "})
        monkeypatch.setattr(
            tracker_mod.database,
            "get_agent_data_for_ids",
            lambda ids: called.append(ids) or {},
        )
        monkeypatch.setattr(
            tracker_mod.database, "list_entity_latest_agent_refs", lambda et, eid: []
        )
        snap = tracker_mod.assemble_job_copy_snapshot("job-empty")
        assert snap == {"job": {"n": 1, "xs": [2, None], "pad": "   "}, "agent_data": {}}
        assert called == []

    def test_pins_stay_ids_and_blocks_follow_config_types(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Pin string on the stored job is an agent_data id; hop from latest refs unions in.
        monkeypatch.setattr(tracker_mod, "BLOCK_TYPES", ["SYSTEM", "RESPONSE", "FEEDBACK"])
        batches = {
            "b-pin": [
                {"block_type": "SYSTEM", "agent_data_id": "sys-1", "block_data": "sys text"},
                {"block_type": "RESPONSE", "agent_data_id": self._PIN, "block_data": "resolved pin"},
                # last RESPONSE wins
                {"block_type": "RESPONSE", "agent_data_id": "resp-newer", "block_data": None},
            ],
            "b-hop": [
                {"block_type": "TASK", "agent_data_id": self._HOP, "block_data": "task body"},
                {"block_type": "RESPONSE", "agent_data_id": "hop-resp", "block_data": "hop resp"},
            ],
        }
        self._wire(
            monkeypatch,
            job=self._JOB,
            hits=[self._PIN],
            refs=[
                {
                    "prompt_blocks": [
                        "skip-non-dict",
                        {"id": None},
                        {"id": "  "},
                        {"id": self._HOP},
                        {"id": self._PIN},  # duplicate of walk hit — first-seen wins
                    ]
                }
            ],
            seeds={
                self._PIN: {"block_type": "RESPONSE", "batch_id": "b-pin", "task_key": "draft"},
                self._HOP: {"block_type": "TASK", "batch_id": "b-hop", "task_key": None},
            },
            batches=batches,
        )
        snap = tracker_mod.assemble_job_copy_snapshot("job-1420")
        assert snap["job"]["job_data"]["artifacts"]["job_resume"] == self._PIN
        pin_blocks = snap["agent_data"][self._PIN]["blocks"]
        assert set(pin_blocks) == {"SYSTEM", "RESPONSE"}  # FEEDBACK omitted — no row
        assert pin_blocks["RESPONSE"] == {"id": "resp-newer", "content": ""}  # None → ""
        assert pin_blocks["SYSTEM"]["content"] == "sys text"
        hop = snap["agent_data"][self._HOP]
        assert hop["task_key"] == ""
        assert "TASK" not in hop["blocks"]  # not in patched BLOCK_TYPES
        assert hop["blocks"]["RESPONSE"]["content"] == "hop resp"

    def test_latest_refs_failure_keeps_stored_ids(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level("WARNING")
        self._wire(
            monkeypatch,
            job=self._JOB,
            hits=[self._PIN],
            refs_exc=RuntimeError("refs down"),
            seeds={self._PIN: {"block_type": "RESPONSE", "batch_id": "b-pin", "task_key": "t"}},
            batches={"b-pin": [{"block_type": "RESPONSE", "agent_data_id": self._PIN, "block_data": "ok"}]},
        )
        snap = tracker_mod.assemble_job_copy_snapshot("job-1420")
        assert self._PIN in snap["agent_data"]
        assert "list_entity_latest_agent_refs failed" in caplog.text

    def test_skips_missing_row_no_batch_and_hop_error(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level("WARNING")
        job = {
            "astral_job_id": "job-1420",
            "a": "gone",
            "b": "nobatch",
            "c": "boom",
            "d": "ok-id",
        }
        self._wire(
            monkeypatch,
            job=job,
            hits=["gone", "nobatch", "boom", "ok-id"],
            seeds={
                "nobatch": {"block_type": "RESPONSE", "batch_id": "  ", "task_key": "t"},
                "ok-id": {"block_type": "RESPONSE", "batch_id": "b-ok", "task_key": "t"},
            },
            seed_exc={"boom": ValueError("cyclic pointer")},
            batches={
                "b-ok": [
                    {
                        "block_type": "RESPONSE",
                        "agent_data_id": "",
                        "block_data": {"not": "str"},
                    }
                ]
            },
        )
        snap = tracker_mod.assemble_job_copy_snapshot("job-1420", debug=True)
        assert set(snap["agent_data"]) == {"ok-id"}
        assert snap["agent_data"]["ok-id"]["blocks"]["RESPONSE"]["id"] == ""
        assert "hop failed" in caplog.text

    def test_shared_batch_queried_once(self, monkeypatch: pytest.MonkeyPatch) -> None:
        spy = self._wire(
            monkeypatch,
            job={"x": "id-a", "y": "id-b"},
            hits=["id-a", "id-b"],
            seeds={
                "id-a": {"block_type": "SYSTEM", "batch_id": "shared", "task_key": "t"},
                "id-b": {"block_type": "RESPONSE", "batch_id": "shared", "task_key": "t"},
            },
            batches={
                "shared": [
                    {"block_type": "SYSTEM", "agent_data_id": "id-a", "block_data": "s"},
                    {"block_type": "RESPONSE", "agent_data_id": "id-b", "block_data": "r"},
                ]
            },
        )
        snap = tracker_mod.assemble_job_copy_snapshot("job-1420")
        assert spy.batch_calls == ["shared"]
        assert snap["agent_data"]["id-a"]["blocks"] == snap["agent_data"]["id-b"]["blocks"]

    def test_debug_true_emits_index_false_is_silent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        dbg = MagicMock()
        monkeypatch.setattr(tracker_mod, "get_logger", lambda *a, **k: dbg)
        self._wire(monkeypatch, job={"n": 1}, refs=[])
        tracker_mod.assemble_job_copy_snapshot("job-empty", debug=False)
        dbg.debug_index.assert_not_called()
        tracker_mod.assemble_job_copy_snapshot("job-empty", debug=True)
        job_hdr = dbg.debug_index.call_args_list[0].kwargs
        assert job_hdr["func"] == "assemble_job_copy_snapshot"
        assert job_hdr["outcome"] == "assembled_no_ids"

    def test_debug_recorded_and_skip_outcomes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        dbg = MagicMock()
        monkeypatch.setattr(tracker_mod, "get_logger", lambda *a, **k: dbg)
        self._wire(
            monkeypatch,
            job={"a": "gone", "b": self._PIN},
            hits=[self._PIN, "gone"],
            seeds={
                self._PIN: {"block_type": "RESPONSE", "batch_id": "b-pin", "task_key": "draft"},
            },
            batches={
                "b-pin": [
                    {"block_type": "RESPONSE", "agent_data_id": self._PIN, "block_data": "body"}
                ]
            },
        )
        tracker_mod.assemble_job_copy_snapshot("job-1420", debug=True)
        outcomes = [c.kwargs["outcome"] for c in dbg.debug_index.call_args_list]
        assert outcomes[0] == "assembled"
        assert "missing_row" in outcomes
        assert "recorded" in outcomes
        dbg.debug_detail_block.assert_called()
        assert "body" in dbg.debug_detail_block.call_args.args[0]


class TestAst1453LegalJobSuccessorStates:
    """AST-1453: successors == JOB_STATES keys transition would accept, minus from_state."""

    def test_excludes_self_includes_unrestricted_and_listed_priors(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Tiny registry: None prior = unrestricted; listed prior must match current.
        monkeypatch.setattr(
            tracker_mod,
            "JOB_STATES",
            {
                "A": {"prior_states": None},
                "B": {"prior_states": ["A"]},
                "C": {"prior_states": ["Z"]},
            },
        )
        assert tracker_mod.legal_job_successor_states("A") == ["B"]
        assert set(tracker_mod.legal_job_successor_states("X")) == {"A"}
        assert tracker_mod.legal_job_successor_states("B") == ["A"]


class TestAst1453PersistSkippedJobEdits:
    """AST-1453: skipped-only field writes; transition after columns/JD; empty JD ok."""

    _SKIP = "CANDIDATE_SKIPPED"
    _JD_KEY = "job_description"

    def _job(self, **over: Any) -> Dict[str, Any]:
        base: Dict[str, Any] = {
            "astral_job_id": "job-1453",
            "state": self._SKIP,
            "job_title": "Old",
            "job_link": "https://old.example",
            "state_history": [],
        }
        base.update(over)
        return base

    def test_missing_job_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: None)
        with pytest.raises(ValueError, match="Job not found"):
            tracker_mod.persist_skipped_job_edits("missing", {"job_title": "T"})

    def test_non_skipped_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: self._job(state="RECOMMENDED"))
        with pytest.raises(ValueError, match="not in a skipped state"):
            tracker_mod.persist_skipped_job_edits("job-1453", {"job_title": "T"})

    def test_empty_title_and_link_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: self._job())
        with pytest.raises(ValueError, match="job_title required"):
            tracker_mod.persist_skipped_job_edits("job-1453", {"job_title": "  "})
        with pytest.raises(ValueError, match="job_link required"):
            tracker_mod.persist_skipped_job_edits("job-1453", {"job_link": ""})

    def test_writes_title_link_jd_then_transition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        order: List[str] = []
        jobs = {"job-1453": self._job()}

        def _get(jid: str) -> Any:
            return jobs.get(jid)

        def _save(jid: str, **kw: Any) -> bool:
            order.append("save_job")
            jobs[jid] = {**jobs[jid], **kw}
            return True

        def _save_data(jid: str, patch: Dict[str, Any]) -> None:
            order.append("save_job_data")
            assert patch == {self._JD_KEY: "pasted JD"}

        def _transition(ids: List[str], to_state: str) -> None:
            order.append("transition")
            assert ids == ["job-1453"] and to_state == "NEW"
            jobs["job-1453"] = {**jobs["job-1453"], "state": to_state}

        monkeypatch.setattr(tracker_mod, "get_job", _get)
        monkeypatch.setattr(tracker_mod, "save_job", _save)
        monkeypatch.setattr(tracker_mod, "save_job_data", _save_data)
        monkeypatch.setattr(tracker_mod, "transition_job_state", _transition)
        out = tracker_mod.persist_skipped_job_edits(
            "job-1453",
            {
                "job_title": " New Title ",
                "job_link": " https://new.example ",
                "job_description": "pasted JD",
                "state": "NEW",
            },
        )
        # JD write then column save, then hop (plan: fields before transition).
        assert order == ["save_job_data", "save_job", "transition"]
        assert out["job_title"] == "New Title"
        assert out["job_link"] == "https://new.example"
        assert out["state"] == "NEW"

    def test_empty_jd_persists_without_strip_whole_blob(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        patches: List[Dict[str, Any]] = []
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: self._job())
        monkeypatch.setattr(
            tracker_mod,
            "save_job_data",
            lambda jid, patch: patches.append(patch),
        )
        monkeypatch.setattr(tracker_mod, "save_job", MagicMock())
        monkeypatch.setattr(tracker_mod, "transition_job_state", MagicMock())
        tracker_mod.persist_skipped_job_edits("job-1453", {"job_description": ""})
        tracker_mod.persist_skipped_job_edits("job-1453", {"job_description": None})
        assert patches == [{self._JD_KEY: ""}, {self._JD_KEY: ""}]

    def test_same_state_skips_transition(self, monkeypatch: pytest.MonkeyPatch) -> None:
        transition = MagicMock()
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: self._job())
        monkeypatch.setattr(tracker_mod, "save_job", MagicMock())
        monkeypatch.setattr(tracker_mod, "save_job_data", MagicMock())
        monkeypatch.setattr(tracker_mod, "transition_job_state", transition)
        tracker_mod.persist_skipped_job_edits("job-1453", {"state": self._SKIP})
        transition.assert_not_called()

    def test_field_writes_before_illegal_transition_propagates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock(return_value=True)
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: self._job())
        monkeypatch.setattr(tracker_mod, "save_job", save)
        monkeypatch.setattr(tracker_mod, "save_job_data", MagicMock())
        monkeypatch.setattr(
            tracker_mod,
            "transition_job_state",
            MagicMock(side_effect=ValueError("Invalid transition: CANDIDATE_SKIPPED -> PASSED_JD")),
        )
        with pytest.raises(ValueError, match="Invalid transition"):
            tracker_mod.persist_skipped_job_edits(
                "job-1453", {"job_title": "Kept", "state": "PASSED_JD"}
            )
        save.assert_called_once()
        assert save.call_args.kwargs["job_title"] == "Kept"


# Branches: pattern match / ownership refuse / hydrate / Style D (AST-1518).
class TestAst1518ContactTaskReads:
    """AST-1518: contact_task_* read wrappers + get_job_by_pattern."""

    def _job(self, jid: str = "j1", company: str = "acme", title: str = "Engineer") -> Dict[str, Any]:
        return {
            "astral_job_id": jid,
            "company": company,
            "job_title": title,
            "job_link": f"https://jobs.example/{jid}",
            "state": "RECOMMENDED",
        }

    def _patch_story(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "src.core.agent.get_entity_agent_story",
            lambda entity: [{"role": "assistant", "content": "story"}],
        )

    def test_get_job_by_pattern_exact_one(self, monkeypatch: pytest.MonkeyPatch) -> None:
        jobs = [self._job("j1", title="Staff Engineer"), self._job("j2", title="Analyst")]
        monkeypatch.setattr(tracker_mod, "list_jobs", lambda **kwargs: jobs)
        assert tracker_mod.get_job_by_pattern("c1", "Staff")["astral_job_id"] == "j1"
        assert tracker_mod.get_job_by_pattern("c1", "missing") is None
        jobs2 = [self._job("j1", title="Engineer A"), self._job("j2", title="Engineer B")]
        monkeypatch.setattr(tracker_mod, "list_jobs", lambda **kwargs: jobs2)
        assert tracker_mod.get_job_by_pattern("c1", "Engineer") is None

    def test_contact_task_get_job_by_pattern_happy_and_errors(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch_story(monkeypatch)
        job = self._job()
        monkeypatch.setattr(tracker_mod, "list_jobs", lambda **kwargs: [job])
        monkeypatch.setattr(
            tracker_mod, "get_company", lambda sn: {"short_name": sn, "candidate_id": "c1"}
        )
        out = tracker_mod.contact_task_get_job_by_pattern("c1", "Engineer")
        assert out["ok"] is True and out["task_key"] == "get_job_by_pattern"
        assert out["result"]["astral_job_id"] == "j1"
        assert out["result"]["agent_story"]

        assert tracker_mod.contact_task_get_job_by_pattern("", "x")["error"] == "no_candidate"
        assert tracker_mod.contact_task_get_job_by_pattern("c1", "")["error"] == "unmatched_pattern"
        monkeypatch.setattr(tracker_mod, "list_jobs", lambda **kwargs: [])
        assert tracker_mod.contact_task_get_job_by_pattern("c1", "x")["error"] == "unmatched_pattern"
        monkeypatch.setattr(
            tracker_mod,
            "list_jobs",
            lambda **kwargs: [self._job("j1"), self._job("j2", title="Engineer Two")],
        )
        assert (
            tracker_mod.contact_task_get_job_by_pattern("c1", "Engineer")["error"]
            == "ambiguous_pattern"
        )

    def test_contact_task_get_job_data_ownership(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_story(monkeypatch)
        job = self._job()
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: job if jid == "j1" else None)
        monkeypatch.setattr(
            tracker_mod, "get_company", lambda sn: {"short_name": sn, "candidate_id": "c1"}
        )
        ok = tracker_mod.contact_task_get_job_data("c1", "j1")
        assert ok["ok"] is True and "agent_story" in ok["result"]

        monkeypatch.setattr(
            tracker_mod, "get_company", lambda sn: {"short_name": sn, "candidate_id": "other"}
        )
        refused = tracker_mod.contact_task_get_job_data("c1", "j1")
        assert refused["error"] == "refused_cross_candidate"

        assert tracker_mod.contact_task_get_job_data("c1", "missing")["error"] == "not_found"
        assert tracker_mod.contact_task_get_job_data("", "j1")["error"] == "no_candidate"

    def test_contact_task_get_company_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_story(monkeypatch)
        monkeypatch.setattr(
            tracker_mod,
            "get_company",
            lambda sn: {"short_name": sn, "candidate_id": "c1"} if sn == "acme" else None,
        )
        out = tracker_mod.contact_task_get_company_data("c1", "acme")
        assert out["ok"] is True and out["result"]["short_name"] == "acme"
        assert out["result"]["agent_story"]
        assert tracker_mod.contact_task_get_company_data("c1", "nope")["error"] == "not_found"
        monkeypatch.setattr(
            tracker_mod,
            "get_company",
            lambda sn: {"short_name": sn, "candidate_id": "other"},
        )
        assert (
            tracker_mod.contact_task_get_company_data("c1", "acme")["error"]
            == "refused_cross_candidate"
        )

    def test_contact_task_get_candidate_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_story(monkeypatch)
        row = {
            "astral_candidate_id": "c1",
            "candidate_data": {"profile": {"first": "Ada"}},
        }
        monkeypatch.setattr(tracker_mod.candidate_mod, "get_candidate", lambda cid: row if cid == "c1" else None)
        full = tracker_mod.contact_task_get_candidate_data("c1", "")
        assert full["ok"] is True and full["result"]["agent_story"]
        leaf = tracker_mod.contact_task_get_candidate_data("c1", "profile.first")
        assert leaf["ok"] is True and leaf["result"] == "Ada"
        assert tracker_mod.contact_task_get_candidate_data("c1", "profile.missing")["error"] == "not_found"
        assert tracker_mod.contact_task_get_candidate_data("", "")["error"] == "no_candidate"

    def test_style_d_debug_on_job_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_story(monkeypatch)
        log = MagicMock()
        monkeypatch.setattr(tracker_mod, "get_logger", lambda _n: log)
        monkeypatch.setattr(tracker_mod, "get_job", lambda jid: self._job())
        monkeypatch.setattr(
            tracker_mod, "get_company", lambda sn: {"short_name": sn, "candidate_id": "c1"}
        )
        tracker_mod.contact_task_get_job_data("c1", "j1", debug=True)
        outcomes = [c.kwargs.get("outcome") for c in log.debug_index.call_args_list]
        assert outcomes == ["found", "recorded"]
        assert log.debug_index.call_args_list[0].kwargs["func"] == "tracker.contact_task_get_job_data"


# Branches: save_job_artifact/get_job_current catalog shape; job_resume→base_resume citation;
# cover sources pass-through; type-specific public saves gone; hydrate via get_job_current.
class TestAst1592TrackerCatalogWriteReadCitation:
    """AST-1592: generic job catalog write/read + job_resume cites base_resume."""

    def _resume_cd(self) -> dict:
        return {
            "artifacts": {
                "resume_structure": [
                    {"id": "professional_summary", "enabled": True, "order": 1},
                    {"id": "experience", "enabled": True, "order": 2},
                ]
            }
        }

    def test_type_specific_public_saves_removed(self) -> None:
        assert not hasattr(tracker_mod, "save_job_artifact_job_resume_body")
        assert not hasattr(tracker_mod, "save_job_artifact_cover_letter")
        assert not hasattr(tracker_mod, "persist_finalize_job_resume_content")
        assert not hasattr(tracker_mod, "persist_finalize_cover_letter_content")
        assert hasattr(tracker_mod, "save_job_artifact")
        assert hasattr(tracker_mod, "get_job_current")
        assert hasattr(tracker_mod, "prepare_job_replica_body")

    def test_get_job_current_hit_miss_and_key_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_current_artifact",
            lambda et, eid, at: (
                {"artifact_data": {"professional_summary": "cur"}, "current": 1}
                if at == "job_resume"
                else None
            ),
        )
        assert tracker_mod.get_job_current("job-1", "job.artifacts.job_resume") == {
            "professional_summary": "cur"
        }
        assert tracker_mod.get_job_current("job-1", "job.artifacts.cover_letter") is None
        with pytest.raises(ValueError, match="unknown catalog key"):
            tracker_mod.get_job_current("job-1", "not.a.key")
        with pytest.raises(ValueError, match="artifact_key required"):
            tracker_mod.get_job_current("job-1", "   ")
        with pytest.raises(ValueError, match="astral_job_id required"):
            tracker_mod.get_job_current("  ", "job.artifacts.job_resume")

    def test_job_resume_cites_current_base_resume_uuid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves: list[dict] = []

        def _get(et: str, eid: str, at: str):
            if et == "candidate" and at == "base_resume":
                return {"artifact_uuid": "base-uuid-99", "artifact_data": {"x": 1}}
            return None

        monkeypatch.setattr(tracker_mod.database, "get_current_artifact", _get)
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: saves.append(
                {
                    "et": et,
                    "eid": eid,
                    "at": at,
                    "data": data,
                    "sources": source_artifact_ids,
                }
            )
            or "new-jr",
        )
        monkeypatch.setattr(tracker_mod, "_candidate_id_for_job", lambda jid: "cand-9")
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._resume_cd())
        # Caller-supplied sources must be ignored for job_resume (always auto-cite).
        uid = tracker_mod.save_job_artifact(
            "job-9",
            "job.artifacts.job_resume",
            {"professional_summary": "Cited", "experience": []},
            source_artifact_ids=["caller-should-ignore"],
        )
        assert uid == "new-jr"
        assert saves[0]["sources"] == ["base-uuid-99"]
        assert saves[0]["at"] == "job_resume"
        assert saves[0]["data"]["professional_summary"] == "Cited"

    def test_job_resume_empty_sources_when_no_base_resume(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves: list[dict] = []
        monkeypatch.setattr(
            tracker_mod.database, "get_current_artifact", lambda *a, **k: None
        )
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: saves.append(
                source_artifact_ids
            )
            or "new-jr",
        )
        monkeypatch.setattr(tracker_mod, "_candidate_id_for_job", lambda jid: "cand-9")
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: self._resume_cd())
        tracker_mod.save_job_artifact(
            "job-9",
            "job.artifacts.job_resume",
            {"professional_summary": "No base", "experience": []},
        )
        assert saves[0] == []

    def test_cover_letter_passes_caller_sources(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves: list = []
        monkeypatch.setattr(
            tracker_mod.database,
            "save_artifact",
            lambda et, eid, at, data, source_artifact_ids=None: saves.append(
                source_artifact_ids
            )
            or "cl",
        )
        tracker_mod.save_job_artifact(
            "job-9",
            "job.artifacts.cover_letter",
            {"Subject": "S", "Letter": "L", "signature": ""},
            source_artifact_ids=["seed-1"],
        )
        assert saves[0] == ["seed-1"]
