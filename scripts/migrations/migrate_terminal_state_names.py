#!/usr/bin/env python3
"""
Retired terminal-state remap (AST-2087).

Moves job / company / candidate / meteorite `state` and live dispatch_task.trigger_state
off retired names using config RETIRED_TERMINAL_STATE_MAP (AST-2086). Rows it can't
resolve, and dead-state rows, are left as-is and counted. Never rewrites state_history
or state_changed_at; never runs from schema-ensure.

Recommended:
  1. cp data/astral.db data/astral.db.pre-AST-2087-$(date +%Y%m%d)
  2. python scripts/migrations/migrate_terminal_state_names.py
  3. After Susan OK: python scripts/migrations/migrate_terminal_state_names.py --execute
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import migrate_terminal_state_names


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Apply changes (default is dry-run)",
    )
    args = ap.parse_args()
    result = migrate_terminal_state_names(dry_run=not args.execute)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
