"""
Meteorite placeholder company ensure + job create (AST-1041 / AST-1042).

Lazy-insert meteorite-<candidate_id> from METEORITE_CONFIG. API-facing job create
from raw HTML lands in JD_READY with synthetic latest_score (AST-1042 carve-out).
No email ingest. No admin UI. Leave-in-place — callers must not delete these rows
on candidate exit.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.core.candidate import get_candidate
from src.data.database import get_company, get_job, save_company, save_job
from src.utils.config import METEORITE_CONFIG, TRACKER_CONFIG
from src.utils.logging import get_logger


def ensure_meteorite_company(candidate_id: str, *, debug: bool = False) -> dict[str, Any]:
    """Ensure meteorite-<candidate_id> exists in IGNORE. Idempotent.

    Returns:
      {"short_name": str, "inserted": bool, "company": dict}
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")

    short_name = METEORITE_CONFIG["short_name_template"].format(candidate_id=candidate_id)
    log = get_logger(__name__)
    log.set_debug_flag(debug)

    existing = get_company(short_name)
    if existing is not None:
        if debug:
            log.debug_index(
                func="meteorite.ensure_meteorite_company",
                index=1,
                total=1,
                identifier=short_name,
                outcome="already-present",
            )
            log.debug_detail(f"candidate_id={candidate_id}")
        return {"short_name": short_name, "inserted": False, "company": existing}

    save_company(
        short_name=short_name,
        state=METEORITE_CONFIG["company_state"],
        company_name=METEORITE_CONFIG["company_name"],
        company_data=dict(METEORITE_CONFIG["company_data"]),
        candidate_id=candidate_id,
    )
    row = get_company(short_name)
    if row is None:
        raise RuntimeError(f"meteorite company missing after save: {short_name}")
    if debug:
        log.debug_index(
            func="meteorite.ensure_meteorite_company",
            index=1,
            total=1,
            identifier=short_name,
            outcome="inserted",
        )
        log.debug_detail(f"candidate_id={candidate_id}")
    return {"short_name": short_name, "inserted": True, "company": row}


def create_meteorite_job(
    candidate_id: str,
    html_body: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Lazy-ensure meteorite company, then insert a JD_READY job from raw HTML.

    Create carve-out (not transition_job_state): first write inserts directly into
    METEORITE_CONFIG["job_create_state"] the same way ingest_jobs inserts into NEW
    (JOB_STATES prior_states=None unrestricted entry). JD_READY's registered
    prior_states remain ["PASSED_JOBLIST"] for scrape/qualify hops — this path does
    not expand those priors and does not invent a new job state.

    Returns:
      {
        "astral_job_id": str,
        "company": str,           # meteorite-<candidate_id>
        "state": str,             # job_create_state
        "latest_score": float,    # job_create_latest_score
        "company_inserted": bool, # from ensure
        "job": dict,              # get_job row after writes
      }
    """
    candidate_id = (candidate_id or "").strip()
    if not candidate_id:
        raise ValueError("candidate_id is required")
    if not isinstance(html_body, str) or not html_body.strip():
        raise ValueError("html_body is required")

    cand = get_candidate(candidate_id)
    if not cand:
        raise ValueError(f"candidate not found: {candidate_id}")

    ensured = ensure_meteorite_company(candidate_id, debug=debug)
    short_name = ensured["short_name"]
    jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
    state = METEORITE_CONFIG["job_create_state"]
    score = float(METEORITE_CONFIG["job_create_latest_score"])
    astral_job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    inserted = save_job(
        astral_job_id,
        company=short_name,
        state=state,
        job_title=None,
        job_link=None,
        company_job_id=None,
        job_data={jd_key: html_body},
        state_history=[{"to_state": state, "timestamp": now, "score": score}],
        state_changed_at=now,
        merge=False,
    )
    if not inserted:
        raise RuntimeError(f"meteorite job insert failed: {astral_job_id}")

    # INSERT path omits latest_score — update column explicitly (AST-1042 carve-out).
    save_job(astral_job_id, latest_score=score)

    row = get_job(astral_job_id)
    if row is None:
        raise RuntimeError(f"meteorite job missing after save: {astral_job_id}")
    if row.get("state") != state or row.get("latest_score") != score:
        raise RuntimeError(
            f"meteorite job postcondition failed id={astral_job_id} "
            f"state={row.get('state')!r} latest_score={row.get('latest_score')!r}"
        )

    return {
        "astral_job_id": astral_job_id,
        "company": short_name,
        "state": state,
        "latest_score": score,
        "company_inserted": ensured["inserted"],
        "job": row,
    }
