#!/usr/bin/env python3
"""
One-time cleanup of duplicate job identity rows and board-gaze placeholder jobs (AST-729).

Phase 1 — board-gaze: DELETE all job rows whose company matches the board placeholder
prefix (__board__*). Board-gaze is decommissioned; rows are removed, not deduped.

Phase 2 — identity dedupe: for each group sharing the same (company, job_title,
company_job_id) among non-board companies, keep the row with earliest created_at
(tie-break astral_job_id ASC) and DELETE the rest.

Related records (agent_data, agent_responses, timesheets, dispatch_ledger) for deleted
job rows are left as-is — no re-pointing or cascade deletes.

Idempotent: second live run should report dedupe_groups=0 and board_jobs_scanned=0.

Run before AST-732 unique index migration in each environment.

Recommended operator order:
  1. Backup: cp data/astral.db data/astral.db.pre-AST-729-$(date +%Y%m%d)
  2. Dry-run full cleanup (both phases):
     python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py --dry-run
  3. Spot-check one company's dedupe groups:
     python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py --dry-run --company aledade
  4. Optional: board phase only preview:
     python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py --dry-run --skip-dedupe
  5. Live run (after Susan OK):
     python scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py
  6. Verify agent_data untouched (optional):
     SELECT COUNT(*) FROM agent_data;  — same before/after
"""

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.database import _ensure_job_schema, _get_connection, _run_with_retry

_BOARD_PREFIX = "__board__"
_BOARD_LIKE = f"{_BOARD_PREFIX}%"

_COUNT_KEYS = (
    "board_jobs_scanned",
    "board_jobs_deleted",
    "dedupe_groups",
    "dedupe_survivors",
    "dedupe_deleted",
    "errors",
)


def _empty_counts() -> Dict[str, int]:
    return {k: 0 for k in _COUNT_KEYS}


def find_duplicate_identity_groups(
    conn: sqlite3.Connection,
    company_filter: Optional[str],
) -> List[Dict[str, Any]]:
    """Return duplicate identity triple groups with members ordered for survivor pick."""
    params: List[Any] = [_BOARD_LIKE]
    company_clause = ""
    if company_filter:
        company_clause = " AND company = ?"
        params.append(company_filter)

    group_rows = conn.execute(
        f"""
        SELECT company, job_title, company_job_id, COUNT(*) AS cnt
        FROM job
        WHERE company IS NOT NULL AND TRIM(company) != ''
          AND job_title IS NOT NULL AND TRIM(job_title) != ''
          AND company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
          AND company NOT LIKE ?
          {company_clause}
        GROUP BY company, job_title, company_job_id
        HAVING COUNT(*) > 1
        """,
        params,
    ).fetchall()

    groups: List[Dict[str, Any]] = []
    for row in group_rows:
        company, job_title, company_job_id = row[0], row[1], row[2]
        member_rows = conn.execute(
            """
            SELECT astral_job_id, created_at, state
            FROM job
            WHERE company = ? AND job_title = ? AND company_job_id = ?
            ORDER BY created_at ASC NULLS LAST, astral_job_id ASC
            """,
            (company, job_title, company_job_id),
        ).fetchall()
        members = [
            {
                "astral_job_id": m[0],
                "created_at": m[1],
                "state": m[2],
            }
            for m in member_rows
        ]
        groups.append(
            {
                "company": company,
                "job_title": job_title,
                "company_job_id": company_job_id,
                "members": members,
            }
        )
    return groups


def delete_jobs_by_astral_job_ids(conn: sqlite3.Connection, ids: List[str]) -> int:
    """DELETE job rows by primary key; no cascade to related tables."""
    if not ids:
        return 0
    placeholders = ",".join("?" for _ in ids)
    cursor = conn.execute(
        f"DELETE FROM job WHERE astral_job_id IN ({placeholders})",
        ids,
    )
    conn.commit()
    return cursor.rowcount


def run_identity_dedupe(
    dry_run: bool,
    company_filter: Optional[str],
    counts: Dict[str, int],
) -> None:
    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            groups = find_duplicate_identity_groups(conn, company_filter)
            for group in groups:
                try:
                    members = group["members"]
                    if len(members) < 2:
                        continue
                    survivor = members[0]
                    to_delete = members[1:]
                    delete_ids = [m["astral_job_id"] for m in to_delete]
                    counts["dedupe_groups"] += 1
                    counts["dedupe_survivors"] += 1
                    id_list = ", ".join(delete_ids)
                    prefix = "[dedupe] DRY RUN — " if dry_run else "[dedupe] "
                    print(
                        f"{prefix}group ({group['company']}, {group['job_title']}, "
                        f"{group['company_job_id']}): keep {survivor['astral_job_id']} "
                        f"(created_at={survivor['created_at']}); "
                        f"{'would delete' if dry_run else 'deleted'} "
                        f"{len(delete_ids)} rows: {id_list}"
                    )
                    if not dry_run:
                        deleted = delete_jobs_by_astral_job_ids(conn, delete_ids)
                        counts["dedupe_deleted"] += deleted
                except Exception as e:
                    print(
                        f"[dedupe] error group ({group.get('company')}, "
                        f"{group.get('job_title')}, {group.get('company_job_id')}): {e}"
                    )
                    counts["errors"] += 1
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def run_board_gaze_cleanup(dry_run: bool, counts: Dict[str, int]) -> None:
    def _with_conn() -> None:
        conn = _get_connection()
        try:
            _ensure_job_schema(conn)
            row = conn.execute(
                "SELECT COUNT(*) FROM job WHERE company LIKE ?",
                (_BOARD_LIKE,),
            ).fetchone()
            scanned = row[0] if row else 0
            counts["board_jobs_scanned"] = scanned
            if scanned == 0:
                print("[board] no placeholder-company jobs found")
                return
            if dry_run:
                print(
                    f"[board] DRY RUN — would delete {scanned} job rows "
                    f"where company LIKE '{_BOARD_LIKE}'"
                )
                counts["board_jobs_deleted"] = scanned
                return
            cursor = conn.execute(
                "DELETE FROM job WHERE company LIKE ?",
                (_BOARD_LIKE,),
            )
            conn.commit()
            counts["board_jobs_deleted"] = cursor.rowcount
            print(f"[board] deleted {counts['board_jobs_deleted']} job rows")
        finally:
            conn.close()

    _run_with_retry(_with_conn)


def run_cleanup(
    dry_run: bool,
    skip_dedupe: bool,
    skip_board: bool,
    company_filter: Optional[str],
) -> Dict[str, int]:
    counts = _empty_counts()
    if dry_run:
        print("=== DRY RUN — no DB writes ===\n")

    if not skip_board:
        run_board_gaze_cleanup(dry_run, counts)
    if not skip_dedupe:
        run_identity_dedupe(dry_run, company_filter, counts)

    print(f"\n{'=== DRY RUN SUMMARY ===' if dry_run else '=== SUMMARY ==='}")
    print(
        f"board: scanned={counts['board_jobs_scanned']} "
        f"deleted={counts['board_jobs_deleted']}"
    )
    print(
        f"dedupe: groups={counts['dedupe_groups']} "
        f"survivors_kept={counts['dedupe_survivors']} "
        f"rows_deleted={counts['dedupe_deleted']}"
    )
    print(f"errors={counts['errors']}")
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Remove board-gaze placeholder jobs and dedupe job rows by "
            "(company, job_title, company_job_id)."
        )
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without DELETE.")
    parser.add_argument(
        "--skip-board-cleanup",
        action="store_true",
        help="Run identity dedupe only.",
    )
    parser.add_argument(
        "--skip-dedupe",
        action="store_true",
        help="Run board-gaze cleanup only.",
    )
    parser.add_argument(
        "--company",
        metavar="SHORT_NAME",
        help="Restrict identity dedupe to one company short_name.",
    )
    args = parser.parse_args()
    result = run_cleanup(
        dry_run=args.dry_run,
        skip_dedupe=args.skip_dedupe,
        skip_board=args.skip_board_cleanup,
        company_filter=args.company,
    )
    if not args.dry_run and result["errors"] > 0:
        sys.exit(1)
