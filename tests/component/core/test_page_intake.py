"""Component tests for src/core/page_intake.py (AST-1227)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import page_intake as page_intake_mod
from src.utils.config import METEORITE_CONFIG, TRACKER_CONFIG


# Branches: validation; create + METEORITE_NEW + job_link; known_job_link /
# known_company_job_id dupes; cross-candidate; Style D on/off (AST-1227).
class TestAst1227IngestRecognizedListing:
    def test_validation_errors(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-ok", state="NEW_CANDIDATE", candidate_data={"name": "Ok"})
        with pytest.raises(ValueError, match="candidate_id is required"):
            page_intake_mod.ingest_recognized_listing("", "https://x.example/j", "<p>jd</p>")
        with pytest.raises(ValueError, match="candidate_id is required"):
            page_intake_mod.ingest_recognized_listing("   ", "https://x.example/j", "<p>jd</p>")
        with pytest.raises(ValueError, match="page_url is required"):
            page_intake_mod.ingest_recognized_listing("cand-ok", "", "<p>jd</p>")
        with pytest.raises(ValueError, match="page_url is required"):
            page_intake_mod.ingest_recognized_listing("cand-ok", "   ", "<p>jd</p>")
        with pytest.raises(ValueError, match="html_body is required"):
            page_intake_mod.ingest_recognized_listing("cand-ok", "https://x.example/j", "   ")
        with pytest.raises(ValueError, match="html_body is required"):
            page_intake_mod.ingest_recognized_listing(
                "cand-ok", "https://x.example/j", None  # type: ignore[arg-type]
            )

    def test_creates_meteorite_new_with_job_link(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-1227-create"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "C"})
        url = "https://jobs.example.com/role/fresh"
        html = "<p>" + ("Surfer listing JD text with enough content. " * 3) + "</p>"
        out = page_intake_mod.ingest_recognized_listing(cid, url, html, debug=False)
        landing = METEORITE_CONFIG["job_create_state"]
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        assert out["outcome"] == "created"
        assert out["reason"] is None
        assert out["matched_company_job_id"] is None
        assert out["page_url"] == url
        assert out["state"] == landing == "METEORITE_NEW"
        assert out["astral_job_id"]
        row = db.get_job(out["astral_job_id"])
        assert row is not None
        assert row["job_link"] == url
        assert row["company_job_id"] is None
        assert row["state"] == landing
        assert row["job_data"][jd_key] == html

    def test_second_call_same_url_is_known_job_link_duplicate(
        self, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1227-dup-link"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        url = "https://jobs.example.com/role/dup"
        html = "<p>" + ("First create body. " * 5) + "</p>"
        first = page_intake_mod.ingest_recognized_listing(cid, url, html, debug=False)
        assert first["outcome"] == "created"
        jobs_before = db.list_jobs(candidate_id=cid)
        second = page_intake_mod.ingest_recognized_listing(
            cid, url, "<p>" + ("Different body text. " * 5) + "</p>", debug=False
        )
        assert second["outcome"] == "duplicate"
        assert second["reason"] == "known_job_link"
        assert second["matched_company_job_id"] is None
        assert second["page_url"] == url
        assert "astral_job_id" not in second
        jobs_after = db.list_jobs(candidate_id=cid)
        assert len(jobs_after) == len(jobs_before) == 1

    def test_known_company_job_id_duplicate(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1227-dup-id"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "I"})
        db.save_company("acme", state="IMPORTED", candidate_id=cid)
        db.save_job("j-known", company="acme", state="NEW", company_job_id="KNOWN-EXT-77")
        url = "https://jobs.example.com/role/id-match"
        html = "<p>" + ("x" * 20) + " KNOWN-EXT-77 " + ("y" * 20) + "</p>"
        log = MagicMock()
        monkeypatch.setattr(page_intake_mod, "get_logger", lambda _n: log)
        out = page_intake_mod.ingest_recognized_listing(cid, url, html, debug=True)
        assert out["outcome"] == "duplicate"
        assert out["reason"] == "known_company_job_id"
        assert out["matched_company_job_id"] == "KNOWN-EXT-77"
        assert out["page_url"] == url
        assert "astral_job_id" not in out
        assert log.debug_index.call_args.kwargs["outcome"] == "skipped-duplicate"
        assert "known_company_job_id" in log.debug_detail.call_args.args[0]
        # No meteorite company/job created for this candidate via ingest.
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
        assert db.get_company(short) is None

    def test_cross_candidate_same_link_still_creates(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-1227-mine"
        other = "cand-1227-other"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        db.save_candidate(other, state="NEW_CANDIDATE", candidate_data={"name": "O"})
        link = "https://jobs.example.com/role/shared"
        db.save_company("other-co", state="IMPORTED", candidate_id=other)
        db.save_job("j-other", company="other-co", state="NEW", job_link=link)
        html = "<p>" + ("Shared listing JD for Surfer ingest. " * 3) + "</p>"
        out = page_intake_mod.ingest_recognized_listing(cid, link, html, debug=False)
        assert out["outcome"] == "created"
        row = db.get_job(out["astral_job_id"])
        assert row is not None
        assert row["job_link"] == link

    def test_debug_true_found_recorded_and_skipped_duplicate(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1227-dbg"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "G"})
        url = "https://jobs.example.com/role/dbg"
        html = "<p>" + ("Debug listing JD characters enough. " * 3) + "</p>"
        log = MagicMock()
        monkeypatch.setattr(page_intake_mod, "get_logger", lambda _n: log)

        page_intake_mod.ingest_recognized_listing(cid, url, html, debug=True)
        log.set_debug_flag.assert_called_with(True)
        outcomes = [c.kwargs.get("outcome") for c in log.debug_index.call_args_list]
        assert "found" in outcomes and "recorded" in outcomes
        funcs = {c.kwargs.get("func") for c in log.debug_index.call_args_list}
        assert "page_intake.ingest_recognized_listing" in funcs

        log.reset_mock()
        page_intake_mod.ingest_recognized_listing(cid, url, html, debug=True)
        log.set_debug_flag.assert_called_with(True)
        dup_outcomes = [c.kwargs.get("outcome") for c in log.debug_index.call_args_list]
        assert "skipped-duplicate" in dup_outcomes
        assert any(
            "known_job_link" in (a.args[0] if a.args else "")
            for a in log.debug_detail.call_args_list
        )

    def test_debug_false_skips_style_d(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1227-quiet"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Q"})
        log = MagicMock()
        monkeypatch.setattr(page_intake_mod, "get_logger", lambda _n: log)
        page_intake_mod.ingest_recognized_listing(
            cid,
            "https://jobs.example.com/role/quiet",
            "<p>" + ("Quiet create body. " * 5) + "</p>",
            debug=False,
        )
        log.set_debug_flag.assert_called_with(False)
        log.debug_index.assert_not_called()
        log.debug_detail.assert_not_called()
