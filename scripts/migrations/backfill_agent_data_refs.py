#!/usr/bin/env python3
"""Backfill ref_agent_data_id on duplicate agent_data content rows (AST-978).

Sets refs to the earliest identical twin. Never clears or deletes block_data.
Default is dry-run; pass --execute to write.

Usage:
  python scripts/migrations/backfill_agent_data_refs.py
  python scripts/migrations/backfill_agent_data_refs.py --execute
  python scripts/migrations/backfill_agent_data_refs.py --execute --debug
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import backfill_agent_data_refs
from src.utils.logging import get_logger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply ref updates (default is dry-run)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Emit §1.5.1 per-index found/recorded trail",
    )
    args = parser.parse_args()
    dry_run = not args.execute

    if dry_run:
        print("=== DRY RUN — no DB writes ===")

    result = backfill_agent_data_refs(dry_run=dry_run)

    if args.debug:
        log = get_logger(__name__, debug_flag=True)
        actions = result["actions"]
        total = len(actions)
        for i, action in enumerate(actions, start=1):
            log.debug_index(
                func="backfill_agent_data_refs",
                index=i,
                total=total,
                identifier=str(action.get("agent_data_id") or ""),
                outcome=(
                    f"{action.get('outcome')} "
                    f"ref_agent_data_id={action.get('ref_agent_data_id')!r}"
                ),
            )

    summary = {
        k: result[k]
        for k in (
            "scanned",
            "updated",
            "unchanged",
            "skipped_already_ref",
            "errors",
        )
    }
    print(json.dumps(summary, indent=2))
    return 0 if result.get("errors", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
