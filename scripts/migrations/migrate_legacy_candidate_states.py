#!/usr/bin/env python3
"""
Legacy candidate state + dispatch_task trigger remap (AST-973).

Phase A (pre-cutover DELETED hard-delete) runs only on CLI --execute with phases
including A. Schema-ensure runs Phase B/C remaps only.

Recommended:
  1. cp data/astral.db data/astral.db.pre-AST-973-$(date +%Y%m%d)
  2. python scripts/migrations/migrate_legacy_candidate_states.py --dry-run
  3. After Susan OK: python scripts/migrations/migrate_legacy_candidate_states.py --execute
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.core.candidate import is_candidate_reap_due, list_candidates, purge_reap_due_candidates
from src.data.database import migrate_legacy_candidate_states


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Apply changes (default is dry-run)",
    )
    ap.add_argument(
        "--phases",
        default="ABC",
        help="A | BC | ABC (default ABC for operator cutover)",
    )
    ap.add_argument(
        "--purge-reap-due",
        action="store_true",
        help="Also purge DELETED candidates past reap due (AST-970 timer)",
    )
    args = ap.parse_args()
    dry_run = not args.execute

    result = migrate_legacy_candidate_states(dry_run=dry_run, phases=args.phases)
    print(json.dumps(result, indent=2, default=str))

    if args.purge_reap_due:
        if dry_run:
            due = [
                c.get("astral_candidate_id")
                for c in list_candidates(include_deleted=True)
                if (c.get("state") or "") == "DELETED" and is_candidate_reap_due(c)
            ]
            print(json.dumps({"purge_reap_due_dry_run": due}, indent=2))
        else:
            n = purge_reap_due_candidates()
            print(json.dumps({"purge_reap_due_deleted": n}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
