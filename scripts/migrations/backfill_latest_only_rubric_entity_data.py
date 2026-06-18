#!/usr/bin/env python3
"""
Backfill latest-only agent_responses refs on job and company entity rows (AST-727).

Collapses duplicate agent_responses entries per task_key (latest created_at wins),
drops legacy empty-task_key refs, and leaves agent_data history untouched.
Idempotent: a second live run reports unchanged when data is already normalized.

Recommended operator order:
  1. Backup: cp data/astral.db data/astral.db.pre-AST-727-$(date +%Y%m%d)
  2. Dry-run full scan:
     python scripts/migrations/backfill_latest_only_rubric_entity_data.py --dry-run
  3. Spot-check one entity:
     python scripts/migrations/backfill_latest_only_rubric_entity_data.py --dry-run --job <id>
  4. Live run (after Susan OK):
     python scripts/migrations/backfill_latest_only_rubric_entity_data.py

Verify agent_data untouched: SELECT COUNT(*) FROM agent_data before/after if desired.
Candidates are excluded — job and company rows only.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.roster import normalize_agent_responses_for_backfill
from src.data.database import (
    _ensure_job_schema,
    _get_connection,
    _run_with_retry,
    list_companies,
    list_jobs,
    update_company,
)

_COUNT_KEYS = (
    "scanned",
    "updated",
    "unchanged",
    "errors",
    "dropped_empty_key_total",
    "deduped_refs_removed_total",
)


def _empty_counts() -> Dict[str, int]:
    return {k: 0 for k in _COUNT_KEYS}


def _agent_responses_json(entries: List[Dict[str, Any]]) -> str:
    return json.dumps(entries, sort_keys=True, default=str)


def _set_job_agent_responses(astral_job_id: str, entries: List[Dict[str, Any]]) -> None:
    """Replace job.agent_responses JSON array (full SET, not append)."""

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            conn.execute(
                "UPDATE job SET agent_responses = ? WHERE astral_job_id = ?",
                (json.dumps(entries), astral_job_id),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def _backfill_one_entity(
    entity_type: str,
    entity_id: str,
    entries: Any,
    dry_run: bool,
) -> Tuple[str, Dict[str, int]]:
    """Return (outcome, stats) where outcome is updated|unchanged|error."""
    stats = {"dropped_empty_key": 0, "deduped_removed": 0}
    try:
        raw = entries if isinstance(entries, list) else []
        normalized, stats = normalize_agent_responses_for_backfill(raw)
        if _agent_responses_json(normalized) == _agent_responses_json(raw):
            return "unchanged", stats
        label = "company" if entity_type == "company" else "job"
        if dry_run:
            print(
                f"[{label} {entity_id}] DRY RUN — would set agent_responses "
                f"{len(raw)} -> {len(normalized)} refs "
                f"(dropped_empty={stats['dropped_empty_key']}, "
                f"deduped_removed={stats['deduped_removed']})"
            )
        elif entity_type == "company":
            update_company(entity_id, agent_responses=normalized)
            print(f"[company {entity_id}] updated agent_responses")
        else:
            _set_job_agent_responses(entity_id, normalized)
            print(f"[job {entity_id}] updated agent_responses")
        return "updated", stats
    except Exception as exc:
        print(f"[{entity_type} {entity_id}] error ({exc})")
        return "error", stats


def backfill_companies(dry_run: bool, company: Optional[str]) -> Dict[str, int]:
    counts = _empty_counts()
    rows = list_companies()
    if company:
        rows = [c for c in rows if c.get("short_name") == company]
        if not rows:
            print(f"Company '{company}' not found.")
            return counts

    for row in rows:
        counts["scanned"] += 1
        short_name = row.get("short_name") or ""
        outcome, stats = _backfill_one_entity(
            "company", short_name, row.get("agent_responses"), dry_run
        )
        counts[f"{outcome}"] += 1
        counts["dropped_empty_key_total"] += stats["dropped_empty_key"]
        counts["deduped_refs_removed_total"] += stats["deduped_removed"]

    return counts


def backfill_jobs(dry_run: bool, job_id: Optional[str]) -> Dict[str, int]:
    counts = _empty_counts()
    rows = list_jobs()
    if job_id:
        rows = [j for j in rows if j.get("astral_job_id") == job_id]
        if not rows:
            print(f"Job '{job_id}' not found.")
            return counts

    for row in rows:
        counts["scanned"] += 1
        astral_job_id = row.get("astral_job_id") or ""
        outcome, stats = _backfill_one_entity(
            "job", astral_job_id, row.get("agent_responses"), dry_run
        )
        counts[f"{outcome}"] += 1
        counts["dropped_empty_key_total"] += stats["dropped_empty_key"]
        counts["deduped_refs_removed_total"] += stats["deduped_removed"]

    return counts


def _print_section(label: str, counts: Dict[str, int]) -> None:
    print(
        f"{label}: scanned={counts['scanned']} updated={counts['updated']} "
        f"unchanged={counts['unchanged']} errors={counts['errors']} "
        f"dropped_empty_key={counts['dropped_empty_key_total']} "
        f"deduped_refs_removed={counts['deduped_refs_removed_total']}"
    )


def run_backfill(
    dry_run: bool = False,
    company: Optional[str] = None,
    job_id: Optional[str] = None,
) -> None:
    if dry_run:
        print("=== DRY RUN — no DB writes ===\n")

    run_companies = company is not None or (company is None and job_id is None)
    run_jobs = job_id is not None or (company is None and job_id is None)

    company_counts = _empty_counts()
    job_counts = _empty_counts()

    if run_companies:
        company_counts = backfill_companies(dry_run, company)
    if run_jobs:
        job_counts = backfill_jobs(dry_run, job_id)

    print(f"\n{'=== DRY RUN SUMMARY ===' if dry_run else '=== SUMMARY ==='}")
    if run_companies:
        _print_section("Companies", company_counts)
    if run_jobs:
        _print_section("Jobs     ", job_counts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill latest-only agent_responses on job and company entity rows."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to DB.")
    parser.add_argument("--company", metavar="SHORT_NAME", help="Single company short_name.")
    parser.add_argument("--job", metavar="ASTRAL_JOB_ID", help="Single job astral_job_id.")
    args = parser.parse_args()
    run_backfill(dry_run=args.dry_run, company=args.company, job_id=args.job)
