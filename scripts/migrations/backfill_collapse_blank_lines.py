#!/usr/bin/env python3
"""
Backfill collapse_consecutive_blank_lines on persisted gazer visible text.

Touches company_data.homepage_text and job_data.job_description only — rows
saved before AST-713 may still contain runs of consecutive blank lines.
Idempotent: skips rows already normalized; supports dry-run.

Usage:
  python scripts/migrations/backfill_collapse_blank_lines.py
  python scripts/migrations/backfill_collapse_blank_lines.py --dry-run
  python scripts/migrations/backfill_collapse_blank_lines.py --company aledade
  python scripts/migrations/backfill_collapse_blank_lines.py --job job-abc123
  python scripts/migrations/backfill_collapse_blank_lines.py --company aledade --dry-run
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.database import list_companies, list_jobs
from src.core.roster import save_company_data
from src.core.tracker import save_job_data
from src.utils.formatting import collapse_consecutive_blank_lines
from src.utils.config import ROSTER_CONFIG, TRACKER_CONFIG

_HOMEPAGE_KEY = ROSTER_CONFIG["company_data_keys"]["homepage_text"]
_JD_KEY = TRACKER_CONFIG["job_data_keys"]["job_description"]

_COUNT_KEYS = ("scanned", "updated", "unchanged", "errors")


def _empty_counts() -> Dict[str, int]:
    return {k: 0 for k in _COUNT_KEYS}


def _normalize_if_changed(text: Any) -> tuple[Optional[str], bool]:
    """Return (normalized_text, changed). Non-str / empty -> (None, False) skip."""
    if not isinstance(text, str) or not text:
        return None, False
    normalized = collapse_consecutive_blank_lines(text)
    if normalized == text:
        return None, False
    return normalized, True


def backfill_companies(dry_run: bool, company: Optional[str]) -> Dict[str, int]:
    counts = _empty_counts()
    all_rows = list_companies()
    if company:
        all_rows = [c for c in all_rows if c.get("short_name") == company]
        if not all_rows:
            print(f"Company '{company}' not found.")
            return counts

    for row in all_rows:
        counts["scanned"] += 1
        short_name = row.get("short_name") or ""
        cd = row.get("company_data") or {}
        text = cd.get(_HOMEPAGE_KEY)
        try:
            normalized, changed = _normalize_if_changed(text)
            if not changed:
                counts["unchanged"] += 1
                continue
            if dry_run:
                print(
                    f"[company {short_name}] DRY RUN — would update {_HOMEPAGE_KEY} "
                    f"({len(text)} -> {len(normalized)} chars)"
                )
            else:
                save_company_data(short_name, {_HOMEPAGE_KEY: normalized})
                print(f"[company {short_name}] updated {_HOMEPAGE_KEY}")
            counts["updated"] += 1
        except Exception as e:
            print(f"[company {short_name}] error ({e})")
            counts["errors"] += 1

    return counts


def backfill_jobs(dry_run: bool, job_id: Optional[str]) -> Dict[str, int]:
    counts = _empty_counts()
    all_rows = list_jobs()
    if job_id:
        all_rows = [j for j in all_rows if j.get("astral_job_id") == job_id]
        if not all_rows:
            print(f"Job '{job_id}' not found.")
            return counts

    for row in all_rows:
        counts["scanned"] += 1
        astral_job_id = row.get("astral_job_id") or ""
        jd = row.get("job_data") or {}
        text = jd.get(_JD_KEY)
        try:
            normalized, changed = _normalize_if_changed(text)
            if not changed:
                counts["unchanged"] += 1
                continue
            if dry_run:
                print(
                    f"[job {astral_job_id}] DRY RUN — would update {_JD_KEY} "
                    f"({len(text)} -> {len(normalized)} chars)"
                )
            else:
                save_job_data(astral_job_id, {_JD_KEY: normalized})
                print(f"[job {astral_job_id}] updated {_JD_KEY}")
            counts["updated"] += 1
        except Exception as e:
            print(f"[job {astral_job_id}] error ({e})")
            counts["errors"] += 1

    return counts


def _print_section(label: str, counts: Dict[str, int]) -> None:
    print(
        f"{label}: scanned={counts['scanned']} updated={counts['updated']} "
        f"unchanged={counts['unchanged']} errors={counts['errors']}"
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
        description="Backfill collapse_consecutive_blank_lines on persisted homepage_text and job_description."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to DB.")
    parser.add_argument("--company", metavar="SHORT_NAME", help="Single company short_name.")
    parser.add_argument("--job", metavar="ASTRAL_JOB_ID", help="Single job astral_job_id.")
    args = parser.parse_args()
    run_backfill(dry_run=args.dry_run, company=args.company, job_id=args.job)
