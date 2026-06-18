#!/usr/bin/env python3
"""Seed agent_task grouping metadata from TASK_CONFIG phase/seq (AST-738).

CLI: python scripts/migrations/backfill_task_grouping_metadata.py [--dry-run]
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.config import ASTRAL_CONFIG, TASK_CONFIG, get_task_keys


def seed_values_for_task_key(task_key: str) -> dict:
    """Default grouping metadata for a catalog task_key."""
    cfg = TASK_CONFIG.get(task_key) or {}
    phase = (cfg.get("phase") or "").strip()
    seq_raw = cfg.get("seq")
    return {
        "task_group_name": phase if phase else "(unassigned)",
        "task_group_order": phase if phase else "ZZZ",
        "task_seq": float(seq_raw) if seq_raw is not None else 999.0,
        "task_name": task_key,
    }


_UNASSIGNED = {
    "task_group_name": "(unassigned)",
    "task_group_order": "ZZZ",
    "task_seq": 999.0,
    "task_name": "",  # filled per row
}


def backfill_task_grouping_metadata(
    conn: sqlite3.Connection, *, dry_run: bool = False
) -> dict[str, int]:
    """Copy TASK_CONFIG phase/seq into agent_task grouping columns (current=1 only).

    Caller must have run _ensure_agent_task_schema so columns exist.
    Skips entirely when any current row already has non-empty task_group_name.
    """
    counts = {"updated": 0, "skipped": 0, "skipped_no_row": 0}
    seeded = conn.execute(
        "SELECT COUNT(*) FROM agent_task WHERE current = 1 AND task_group_name != ''"
    ).fetchone()[0]
    if seeded > 0:
        counts["skipped"] = int(seeded)
        return counts

    catalog = set(get_task_keys())
    for task_key in get_task_keys():
        row = conn.execute(
            "SELECT 1 FROM agent_task WHERE task_key = ? AND current = 1 LIMIT 1",
            (task_key,),
        ).fetchone()
        if not row:
            counts["skipped_no_row"] += 1
            continue
        vals = seed_values_for_task_key(task_key)
        conn.execute(
            """UPDATE agent_task
               SET task_group_order = ?, task_group_name = ?, task_seq = ?, task_name = ?
               WHERE task_key = ? AND current = 1""",
            (
                vals["task_group_order"],
                vals["task_group_name"],
                vals["task_seq"],
                vals["task_name"],
                task_key,
            ),
        )
        counts["updated"] += 1

    orphan_rows = conn.execute(
        "SELECT task_key FROM agent_task WHERE current = 1"
    ).fetchall()
    for (task_key,) in orphan_rows:
        if task_key in catalog:
            continue
        vals = {**_UNASSIGNED, "task_name": task_key}
        conn.execute(
            """UPDATE agent_task
               SET task_group_order = ?, task_group_name = ?, task_seq = ?, task_name = ?
               WHERE task_key = ? AND current = 1""",
            (
                vals["task_group_order"],
                vals["task_group_name"],
                vals["task_seq"],
                vals["task_name"],
                task_key,
            ),
        )
        counts["updated"] += 1

    if not dry_run:
        conn.commit()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report counts without committing")
    args = parser.parse_args()
    db_path = ASTRAL_CONFIG["db_dir"] / "astral.db"
    conn = sqlite3.connect(str(db_path))
    try:
        from src.data import database

        database._ensure_agent_task_schema(conn)
        counts = backfill_task_grouping_metadata(conn, dry_run=args.dry_run)
        print(counts)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
