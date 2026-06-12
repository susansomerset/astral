#!/usr/bin/env python3
"""AST-445: read-only trace of evaluate_jd batch jobs — JD text lengths in job_data.

Usage (repo root):
  python3 scripts/spikes/ast445_evaluate_jd_batch_trace.py
  python3 scripts/spikes/ast445_evaluate_jd_batch_trace.py --batch-id <uuid>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.data import database
from src.utils.config import ASTRAL_CONFIG

DEFAULT_BATCH = "34e38ddb-6801-4202-9634-808338f58fae"


def _jd_len(job: Dict[str, Any]) -> int:
    jd = (job.get("job_data") or {}).get("job_description") or ""
    return len(jd.strip())


def _jobs_by_batch(batch_id: str) -> List[Dict[str, Any]]:
    return database.get_job_batch(batch_id)


def _jobs_by_states(states: List[str], limit: int) -> List[Dict[str, Any]]:
    placeholders = ",".join("?" * len(states))
    sql = (
        f"SELECT j.*, c.job_site FROM job j "
        f"LEFT JOIN company c ON j.company = c.short_name "
        f"WHERE j.state IN ({placeholders}) ORDER BY j.state_changed_at DESC LIMIT ?"
    )
    conn = sqlite3.connect(str(ASTRAL_CONFIG["db_dir"] / "astral.db"))
    conn.row_factory = sqlite3.Row
    try:
        database._ensure_job_schema(conn)
        cur = conn.execute(sql, (*states, limit))
        return [database._job_row_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--batch-id", default=DEFAULT_BATCH)
    p.add_argument("--states", default="JD_READY,JD_READY_RETRY")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--out-dir", type=Path, default=_ROOT / "debug/spikes/AST-445")
    args = p.parse_args()

    jobs = _jobs_by_batch(args.batch_id)
    source = f"batch_id={args.batch_id}"
    if not jobs:
        states = [s.strip() for s in args.states.split(",") if s.strip()]
        jobs = _jobs_by_states(states, args.limit)
        source = f"states={states} limit={args.limit} (batch empty/missing)"

    lengths = [_jd_len(j) for j in jobs]
    empty = sum(1 for n in lengths if n == 0)
    nonempty = [n for n in lengths if n > 0]

    for j in jobs:
        aid = j.get("astral_job_id", "?")
        print(
            f"{aid}\t{j.get('state', '')}\tjd_chars={_jd_len(j)}\t"
            f"updated={j.get('state_changed_at', '')}"
        )

    summary = {
        "source": source,
        "total": len(jobs),
        "empty_jd": empty,
        "nonempty_jd": len(nonempty),
        "max_len": max(lengths) if lengths else 0,
        "min_len_nonempty": min(nonempty) if nonempty else None,
    }
    print(json.dumps(summary, indent=2))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "summary.json"
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
