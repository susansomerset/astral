"""Component tests for src/core/tracker.py (AST-393)."""

from __future__ import annotations

import re
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import tracker as tracker_mod


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
class TestIngestBoardListings:
    def test_requires_ids_and_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with pytest.raises(ValueError, match="required"):
            tracker_mod.ingest_board_listings("", "bk", "bs", "b1", [], None, {})
        with pytest.raises(ValueError, match="list"):
            tracker_mod.ingest_board_listings(
                "cand-1",
                "bk",
                "bs",
                "b1",
                "not-a-list",
                title_matchers=None,
                parse_instructions={},
            )  # type: ignore[arg-type]

    def test_creates_placeholder_company_and_inserts(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save_co = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "get_company", lambda _s: None)
        monkeypatch.setattr(tracker_mod.database, "save_company", save_co)
        monkeypatch.setattr(tracker_mod.database, "update_company", MagicMock())
        monkeypatch.setattr(tracker_mod.database, "board_listing_is_duplicate", lambda _c, _b, _k: False)
        monkeypatch.setattr(tracker_mod.database, "save_job", MagicMock())
        mock_record = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "record_board_search_run", mock_record)
        counts = tracker_mod.ingest_board_listings(
            "cand-board",
            "tst",
            "search-9",
            "batch-board",
            ['<div><a href="https://x.example/j/y">Senior Engineer role</a></div>'],
            title_matchers=None,
            parse_instructions={"job_title": "Engineer"},
        )
        assert counts == {"new": 1, "duplicates": 0, "invalid_title": 0}
        save_co.assert_called_once()
        mock_record.assert_called_once_with(
            "batch-board",
            "search-9",
            "cand-board",
            "tst",
            {"new": 1, "duplicates": 0, "invalid_title": 0},
        )

    def test_placeholder_company_already_exists_updates_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_company",
            lambda _short: {"short_name": _short},
        )
        save_co = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "save_company", save_co)
        up_co = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "update_company", up_co)
        monkeypatch.setattr(tracker_mod.database, "board_listing_is_duplicate", lambda _c, _b, _k: True)
        monkeypatch.setattr(tracker_mod.database, "record_board_search_run", MagicMock())
        counts = tracker_mod.ingest_board_listings(
            "cand-board",
            "tst",
            "search-x",
            "batch-x",
            ["<p>duplicate blob</p>"],
            title_matchers=None,
            parse_instructions={},
        )
        assert counts["duplicates"] == 1 and counts["new"] == 0
        save_co.assert_not_called()
        up_co.assert_called_once()

    def test_invalid_title_increment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_company",
            lambda _short: {"short_name": _short},
        )
        monkeypatch.setattr(tracker_mod.database, "save_company", MagicMock())
        monkeypatch.setattr(tracker_mod.database, "update_company", MagicMock())
        monkeypatch.setattr(
            tracker_mod.database,
            "board_listing_is_duplicate",
            lambda _c, _b, _k: False,
        )
        save_job = MagicMock()
        monkeypatch.setattr(tracker_mod.database, "save_job", save_job)
        monkeypatch.setattr(tracker_mod.database, "record_board_search_run", MagicMock())
        counts = tracker_mod.ingest_board_listings(
            "cand-board",
            "tst",
            "search-i",
            "batch-i",
            ["bogus title blob", '<a href="https://jobs.example/q">Matched engineer role</a>'],
            title_matchers=[re.compile(r"engineer", re.I)],
            parse_instructions={},
        )
        assert counts == {"new": 1, "duplicates": 0, "invalid_title": 1}
        save_job.assert_called_once()

    def test_counts_identity_duplicate_bounce_from_save_job(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            tracker_mod.database,
            "get_company",
            lambda _short: {"short_name": _short},
        )
        monkeypatch.setattr(tracker_mod.database, "save_company", MagicMock())
        monkeypatch.setattr(tracker_mod.database, "update_company", MagicMock())
        monkeypatch.setattr(tracker_mod.database, "board_listing_is_duplicate", lambda _c, _b, _k: False)
        monkeypatch.setattr(tracker_mod.database, "save_job", MagicMock(return_value=False))
        monkeypatch.setattr(tracker_mod.database, "record_board_search_run", MagicMock())
        counts = tracker_mod.ingest_board_listings(
            "cand-board",
            "tst",
            "search-dup",
            "batch-dup",
            ['<a href="https://jobs.example/1">Engineer opening</a>'],
            title_matchers=None,
            parse_instructions={},
        )
        assert counts == {"new": 0, "duplicates": 1, "invalid_title": 0}


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
        monkeypatch.setattr("src.core.gazer.scrape_jd_batch", scrape)

        await tracker_mod.get_job_data(job, "job_description")

        scrape.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_self_heal_failure_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job: Dict[str, Any] = {"astral_job_id": "job-2", "job_data": {}}
        monkeypatch.setattr("src.core.gazer.scrape_jd_batch", AsyncMock(side_effect=RuntimeError("boom")))

        assert await tracker_mod.get_job_data(job, "job_description") is None

    @pytest.mark.asyncio
    async def test_initializes_non_dict_job_data(self, monkeypatch: pytest.MonkeyPatch) -> None:
        job: Dict[str, Any] = {"job_data": None}
        monkeypatch.setattr("src.core.gazer.scrape_jd_batch", AsyncMock())

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

    def test_get_and_clear_batch_delegate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(tracker_mod.database, "get_job_batch", lambda batch_id: ["job"])
        monkeypatch.setattr(tracker_mod.database, "clear_job_batch", lambda batch_id: 2)

        assert tracker_mod.get_job_batch("batch-1") == ["job"]
        assert tracker_mod.clear_job_batch("batch-1") == 2


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
        # consult routes company / agent_response appends / admin timesheets through these wrappers (AST-486).
        monkeypatch.setattr(
            tracker_mod.database,
            "get_company",
            lambda short_name: {"short_name": short_name},
        )
        called: list[tuple[Any, ...]] = []
        monkeypatch.setattr(
            tracker_mod.database,
            "append_agent_response",
            lambda et, eid, ent: called.append((et, eid, ent)),
        )
        monkeypatch.setattr(
            tracker_mod.database,
            "list_timesheets",
            lambda **kwargs: [{"batch_id": kwargs.get("batch_id")}],
        )
        assert tracker_mod.get_company("acme")["short_name"] == "acme"
        tracker_mod.append_agent_response("job", "j1", {"k": 1})
        assert called == [("job", "j1", {"k": 1})]
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
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        tracker_mod.save_job_artifact_cover_letter("job-1", {"re_line": "Re", "body": "Hi"})
        assert saved[0]["artifacts"]["cover_letter"] == {"Subject": "Re", "Letter": "Hi", "signature": ""}


class TestPersistJobArtifactFromParsed:
    def test_returns_false_without_job_or_non_dict_payload(self) -> None:
        assert tracker_mod.persist_job_artifact_from_parsed("", {"re_line": "", "body": "", "signature": ""}) is False
        assert tracker_mod.persist_job_artifact_from_parsed("job-1", "not-a-dict") is False

    def test_parsed_matches_returns_false_non_dict_payload(self) -> None:
        assert tracker_mod.parsed_matches_artifact_shape("x", "cover_letter") is False

    def test_persists_resume_and_cover_shapes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[dict[str, object]] = []
        monkeypatch.setattr(tracker_mod, "save_job_data", lambda jid, payload: saved.append(payload))
        monkeypatch.setattr(tracker_mod, "_candidate_data_for_job", lambda jid: {})
        resume = {
            "candidate_name": "A",
            "candidate_title": "T",
            "candidate_contact_detail": "c",
            "professional_summary": "s",
            "core_competencies": "c",
            "experience": "e",
        }
        assert tracker_mod.persist_job_artifact_from_parsed("job-1", resume) is True
        assert saved[0]["artifacts"]["resume_content"]["professional_summary"] == "s"
        saved.clear()
        assert tracker_mod.persist_job_artifact_from_parsed(
            "job-1", {"re_line": "Re", "body": "Hi", "signature": ""}
        ) is True
        assert saved[0]["artifacts"]["cover_letter"]["Letter"] == "Hi"


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
        from src.utils.config import resume_artifact_first_compound_state

        db = seeded_db
        db.save_company("acme", state="IMPORTED")
        db.save_job("job-562", company="acme", state="RECOMMENDED", job_data={"artifacts": {}})
        first = resume_artifact_first_compound_state()
        assert tracker_mod.start_artifact_build("job-562") == first
        assert db.get_job("job-562")["state"] == first

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
        with pytest.raises(ValueError, match="cancel only from BUILD_ARTIFACTS in-progress hop states"):
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
