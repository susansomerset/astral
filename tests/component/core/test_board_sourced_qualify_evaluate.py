"""AST-419: board-sourced NEW jobs reach qualify + evaluate via normal dispatch chain."""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest

from src.core import consult as consult_mod
from src.core import gazer as gazer_mod
from src.core import tracker as tracker_mod
from src.utils.config import BOARDS_CONFIG, GAZER_CONFIG, TASK_CONFIG


def _pass_grade(vector: str = "fit") -> Dict[str, Any]:
    return {"grade": "A", "confidence": 2, "vector": vector}


def _rubric_item(label: str = "fit", code: str = "CR") -> Dict[str, Any]:
    return {
        "label": label,
        "code": code,
        "content": "body\nA = one\nB = two\nF = fail",
        "grade_descriptions": [
            {"grade": "A", "description": "one"},
            {"grade": "F", "description": "fail"},
        ],
    }


_BOARD_HTML = (
    '<motion.div class="listing">'
    '<a href="https://jobs.example.com/senior-engineer">Senior Software Engineer</a>'
    "</motion.div>"
)
_JD_TEXT = (
    "Senior Software Engineer responsibilities include designing systems, "
    "collaborating with teams, and delivering reliable software products. "
    + "engineering " * 80
)


class TestBoardSourcedQualifyEvaluateAst419:
    """Board ingest → validate_title → qualify → scrape_jd → evaluate_jd without state bypass."""

    def test_board_ingest_starts_in_new_with_board_search_id(self, seeded_db) -> None:
        db = seeded_db
        counts = tracker_mod.ingest_board_listings(
            "cand-1",
            "tst",
            "bs-419",
            "ingest-batch",
            [_BOARD_HTML],
            title_matchers=None,
            parse_instructions={"job_title": "Engineer"},
        )
        assert counts == {"new": 1, "duplicates": 0, "invalid_title": 0}

        prefix = BOARDS_CONFIG["ingest"]["placeholder_company_prefix"]
        placeholder = f"{prefix}tst"
        assert db.get_company(placeholder)["candidate_id"] == "cand-1"

        bid, jobs = tracker_mod.get_new_job_batch(
            "NEW",
            limit=5,
            candidate_id="cand-1",
            context="validate_title",
        )
        assert len(jobs) == 1
        job = jobs[0]
        assert job["state"] == "NEW"
        assert job["board_search_id"] == "bs-419"
        assert job["company"] == placeholder
        tracker_mod.clear_job_batch(bid)

    @pytest.mark.asyncio
    async def test_board_job_reaches_qualify_and_evaluate_dispatch(
        self, seeded_db, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = seeded_db
        ctx = {
            "candidate_data": {
                "artifacts": {
                    "joblist_rubric": [_rubric_item()],
                    "jobdesc_rubric": [_rubric_item()],
                }
            }
        }

        tracker_mod.ingest_board_listings(
            "cand-1",
            "tst",
            "bs-419",
            "ingest-batch",
            [_BOARD_HTML],
            title_matchers=None,
            parse_instructions={"job_title": "Engineer"},
        )

        bid_validate, jobs = tracker_mod.get_new_job_batch(
            "NEW",
            limit=5,
            candidate_id="cand-1",
            context="validate_title",
        )
        assert len(jobs) == 1
        job_id = jobs[0]["astral_job_id"]
        out = await gazer_mod.validate_title_batch(bid_validate, jobs, ctx, debug=False)
        assert out == {"passed": 1, "failed": 0, "total": 1}
        tracker_mod.clear_job_batch(bid_validate)
        assert db.get_job(job_id)["state"] == "VALID_TITLE"

        bid_qualify, jobs = tracker_mod.get_new_job_batch(
            "VALID_TITLE",
            limit=5,
            candidate_id="cand-1",
            context="qualify_job_listings",
        )
        assert len(jobs) == 1 and jobs[0]["astral_job_id"] == job_id
        monkeypatch.setattr(
            consult_mod,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "astral_job_id": job_id,
                                "grades": [_pass_grade()],
                                "job_title": "Senior Software Engineer",
                                "job_link": "https://jobs.example.com/senior-engineer",
                            }
                        ]
                    },
                    "timesheet": {},
                }
            ),
        )
        qualify_out = await consult_mod.qualify_job_listings(
            bid_qualify, jobs, ctx, debug=False
        )
        assert qualify_out["passed"] == 1
        tracker_mod.clear_job_batch(bid_qualify)
        assert db.get_job(job_id)["state"] == TASK_CONFIG["qualify_job_listings"]["pass_state"]

        bid_scrape, jobs = tracker_mod.get_new_job_batch(
            TASK_CONFIG["qualify_job_listings"]["pass_state"],
            limit=5,
            candidate_id="cand-1",
            context="scrape_jd",
        )
        assert len(jobs) == 1
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
        monkeypatch.setattr(gazer_mod, "get_visible_text", AsyncMock(return_value=_JD_TEXT))
        scrape_out = await gazer_mod.scrape_jd_batch(bid_scrape, jobs, debug=False)
        assert scrape_out["passed"] == 1
        tracker_mod.clear_job_batch(bid_scrape)
        assert db.get_job(job_id)["state"] == GAZER_CONFIG["scrape_jd"]["pass_state"]

        bid_eval, jobs = tracker_mod.get_new_job_batch(
            "JD_READY",
            limit=5,
            candidate_id="cand-1",
            context="evaluate_jd",
        )
        assert len(jobs) == 1 and jobs[0]["astral_job_id"] == job_id
        eval_out = await consult_mod.evaluate_jd_batch(bid_eval, jobs, ctx, debug=False)
        assert eval_out["passed"] == 1
        tracker_mod.clear_job_batch(bid_eval)
        assert db.get_job(job_id)["state"] == TASK_CONFIG["evaluate_jd"]["pass_state"]

        history = db.get_job(job_id).get("state_history") or []
        states = [entry["to_state"] for entry in history]
        assert states[0] == "NEW"
        assert "VALID_TITLE" in states
        assert TASK_CONFIG["qualify_job_listings"]["pass_state"] in states
        assert "JD_READY" in states
        assert TASK_CONFIG["evaluate_jd"]["pass_state"] in states
