#!/usr/bin/env python3
"""
Backfill collapse_consecutive_blank_lines on persisted visible text.

Touches company_data.homepage_text, job_data.job_description, and agent_data
block_data — rows saved before AST-713 may still contain runs of consecutive
blank lines. Idempotent: skips rows already normalized; supports dry-run.

Usage:
  python scripts/migrations/backfill_collapse_blank_lines.py
  python scripts/migrations/backfill_collapse_blank_lines.py --dry-run
  python scripts/migrations/backfill_collapse_blank_lines.py --company aledade
  python scripts/migrations/backfill_collapse_blank_lines.py --job job-abc123
  python scripts/migrations/backfill_collapse_blank_lines.py --batch prefilter-abc
  python scripts/migrations/backfill_collapse_blank_lines.py --agent-data batch-system-deadbeef
  python scripts/migrations/backfill_collapse_blank_lines.py --company aledade --dry-run
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.database import (
    _compress_payload,
    _decompress_payload,
    _ensure_agent_data_schema,
    _get_connection,
    _row_to_dict,
    _run_with_retry,
    list_companies,
    list_jobs,
)
from src.core.roster import save_company_data
from src.core.tracker import save_job_data
from src.utils.formatting import collapse_consecutive_blank_lines
from src.utils.config import CHARS_PER_TOKEN, ROSTER_CONFIG, TRACKER_CONFIG

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


def _list_agent_data_rows(
    batch_id: Optional[str] = None,
    agent_data_id: Optional[str] = None,
) -> list[Dict[str, Any]]:
    def _with_conn() -> list[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            if agent_data_id:
                rows = conn.execute(
                    "SELECT * FROM agent_data WHERE agent_data_id = ?",
                    (agent_data_id,),
                ).fetchall()
            elif batch_id:
                rows = conn.execute(
                    "SELECT * FROM agent_data WHERE batch_id = ? ORDER BY created_at",
                    (batch_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM agent_data ORDER BY created_at",
                ).fetchall()
            result: list[Dict[str, Any]] = []
            for row in rows:
                d = _row_to_dict(row)
                d["block_data"] = _decompress_payload(d["block_data"])
                result.append(d)
            return result
        finally:
            conn.close()

    return _run_with_retry(_with_conn)


def _update_agent_data_block(agent_data_id: str, block_data: str) -> None:
    blob = _compress_payload(block_data)
    token_size = len(block_data) // CHARS_PER_TOKEN

    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_agent_data_schema(conn)
            conn.execute(
                "UPDATE agent_data SET block_data = ?, token_size = ? WHERE agent_data_id = ?",
                (blob, token_size, agent_data_id),
            )
            conn.commit()
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def backfill_agent_data(
    dry_run: bool,
    batch_id: Optional[str] = None,
    agent_data_id: Optional[str] = None,
) -> Dict[str, int]:
    counts = _empty_counts()
    all_rows = _list_agent_data_rows(batch_id=batch_id, agent_data_id=agent_data_id)
    if agent_data_id and not all_rows:
        print(f"Agent data '{agent_data_id}' not found.")
        return counts
    if batch_id and not all_rows:
        print(f"Batch '{batch_id}' not found.")
        return counts

    for row in all_rows:
        counts["scanned"] += 1
        row_id = row.get("agent_data_id") or ""
        block_type = row.get("block_type") or ""
        text = row.get("block_data")
        try:
            normalized, changed = _normalize_if_changed(text)
            if not changed:
                counts["unchanged"] += 1
                continue
            if dry_run:
                print(
                    f"[agent_data {row_id}] DRY RUN — would update block_data "
                    f"({block_type}, {len(text)} -> {len(normalized)} chars)"
                )
            else:
                _update_agent_data_block(row_id, normalized)
                print(f"[agent_data {row_id}] updated block_data ({block_type})")
            counts["updated"] += 1
        except Exception as e:
            print(f"[agent_data {row_id}] error ({e})")
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
    batch_id: Optional[str] = None,
    agent_data_id: Optional[str] = None,
) -> None:
    if dry_run:
        print("=== DRY RUN — no DB writes ===\n")

    batch_mode = all(
        x is None for x in (company, job_id, batch_id, agent_data_id)
    )
    run_companies = company is not None or batch_mode
    run_jobs = job_id is not None or batch_mode
    run_agent_data = batch_id is not None or agent_data_id is not None or batch_mode

    company_counts = _empty_counts()
    job_counts = _empty_counts()
    agent_data_counts = _empty_counts()

    if run_companies:
        company_counts = backfill_companies(dry_run, company)
    if run_jobs:
        job_counts = backfill_jobs(dry_run, job_id)
    if run_agent_data:
        agent_data_counts = backfill_agent_data(dry_run, batch_id, agent_data_id)

    print(f"\n{'=== DRY RUN SUMMARY ===' if dry_run else '=== SUMMARY ==='}")
    if run_companies:
        _print_section("Companies", company_counts)
    if run_jobs:
        _print_section("Jobs     ", job_counts)
    if run_agent_data:
        _print_section("Agent data", agent_data_counts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Backfill collapse_consecutive_blank_lines on persisted homepage_text, "
            "job_description, and agent_data block_data."
        )
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to DB.")
    parser.add_argument("--company", metavar="SHORT_NAME", help="Single company short_name.")
    parser.add_argument("--job", metavar="ASTRAL_JOB_ID", help="Single job astral_job_id.")
    parser.add_argument("--batch", metavar="BATCH_ID", help="Single agent_data batch_id.")
    parser.add_argument("--agent-data", metavar="AGENT_DATA_ID", help="Single agent_data row.")
    args = parser.parse_args()
    run_backfill(
        dry_run=args.dry_run,
        company=args.company,
        job_id=args.job,
        batch_id=args.batch,
        agent_data_id=args.agent_data,
    )
