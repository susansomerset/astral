#!/usr/bin/env python3
"""Retarget artifact-chain dispatch_task rows off the chain's output state.

CANDIDATE_REVIEW is the BUILD_ARTIFACTS chain's graduation target, so rows that claim
on it never match a dispatch-ready job. Run once per environment; idempotent.
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config import (
    ASTRAL_CONFIG,
    BUILD_ARTIFACTS_BASE_STATE,
    JOB_ARTIFACT_ENTRY_TASK_KEYS,
)

dry_run = "--apply" not in sys.argv
task_keys = sorted(JOB_ARTIFACT_ENTRY_TASK_KEYS | {"draft_cover_letter"})
placeholders = ",".join("?" for _ in task_keys)
params = (*task_keys, "CANDIDATE_REVIEW")

conn = sqlite3.connect(str(ASTRAL_CONFIG["db_dir"] / "astral.db"))
conn.row_factory = sqlite3.Row
select = f"""SELECT id, candidate_id, task_key, trigger_state FROM dispatch_task
             WHERE task_key IN ({placeholders}) AND trigger_state = ?"""
rows = conn.execute(select, params).fetchall()

for r in rows:
    print(f"  id={r['id']} {r['candidate_id']}/{r['task_key']} {r['trigger_state']} -> {BUILD_ARTIFACTS_BASE_STATE}")

if not rows:
    print("No artifact-chain rows on CANDIDATE_REVIEW — nothing to do.")
elif dry_run:
    print(f"\n{len(rows)} row(s) would change. Re-run with --apply to commit.")
else:
    update = f"""UPDATE dispatch_task SET trigger_state = ?, updated_at = CURRENT_TIMESTAMP
                 WHERE task_key IN ({placeholders}) AND trigger_state = ?"""
    cur = conn.execute(update, (BUILD_ARTIFACTS_BASE_STATE, *params))
    conn.commit()
    print(f"\nUpdated {cur.rowcount} row(s) to {BUILD_ARTIFACTS_BASE_STATE}.")

conn.close()
