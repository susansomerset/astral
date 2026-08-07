"""Surfer page_intake listing→meteorite ingest (AST-1227).

Classification and HTTP surface are siblings (AST-1226 / AST-1228). Reuses
create_meteorite_job and per-candidate dedupe helpers — does not scrape.
"""

from __future__ import annotations

from typing import Any, Optional

from src.core.meteorite import create_meteorite_job
from src.data.database import (
    job_link_exists_for_candidate,
    text_matches_known_company_job_id_for_candidate,
)
from src.utils.logging import get_logger


def ingest_recognized_listing(
    candidate_id: str,
    page_url: str,
    html_body: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Dedupe then create a meteorite job for a classified single listing.

    Caller is responsible for having classified the page as a single listing
    (AST-1226 / AST-1228). This function does not classify or fetch.

    Returns:
      {
        "outcome": "created" | "duplicate",
        "reason": None | "known_job_link" | "known_company_job_id",
        "matched_company_job_id": Optional[str],  # set when reason is known_company_job_id
        "page_url": str,
        # when outcome == "created", also the create_meteorite_job fields:
        "astral_job_id": str,
        "company": str,
        "state": str,
        "latest_score": float,
        "company_inserted": bool,
        "job": dict,
        # when outcome == "duplicate":
        # astral_job_id / company / state / latest_score / company_inserted / job are absent
      }
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")
    page_url = (page_url or "").strip()
    if not page_url:
        raise ValueError("page_url is required")
    if not isinstance(html_body, str) or not html_body.strip():
        raise ValueError("html_body is required")

    log = get_logger(__name__)
    log.set_debug_flag(debug)

    if job_link_exists_for_candidate(candidate_id, page_url):
        if debug:
            log.debug_index(
                func="page_intake.ingest_recognized_listing",
                index=1,
                total=1,
                identifier=page_url[:80],
                outcome="skipped-duplicate",
            )
            log.debug_detail("reason=known_job_link")
        return {
            "outcome": "duplicate",
            "reason": "known_job_link",
            "matched_company_job_id": None,
            "page_url": page_url,
        }

    haystack = f"{page_url}\n{html_body}"
    matched = text_matches_known_company_job_id_for_candidate(candidate_id, haystack)
    if matched:
        if debug:
            log.debug_index(
                func="page_intake.ingest_recognized_listing",
                index=1,
                total=1,
                identifier=page_url[:80],
                outcome="skipped-duplicate",
            )
            log.debug_detail(f"reason=known_company_job_id matched={matched}")
        return {
            "outcome": "duplicate",
            "reason": "known_company_job_id",
            "matched_company_job_id": matched,
            "page_url": page_url,
        }

    if debug:
        log.debug_index(
            func="page_intake.ingest_recognized_listing",
            index=1,
            total=1,
            identifier=page_url[:80],
            outcome="found",
        )
        log.debug_detail(f"jd_len={len(html_body)} candidate_id={candidate_id}")

    result = create_meteorite_job(
        candidate_id, html_body, job_link=page_url, debug=debug
    )

    if debug:
        log.debug_index(
            func="page_intake.ingest_recognized_listing",
            index=1,
            total=1,
            identifier=page_url[:80],
            outcome="recorded",
        )
        log.debug_detail(f"astral_job_id={result['astral_job_id']}")

    return {
        "outcome": "created",
        "reason": None,
        "matched_company_job_id": None,
        "page_url": page_url,
        **result,
    }
