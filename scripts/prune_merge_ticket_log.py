#!/usr/bin/env python3
"""Prune merge ticket log to User Testing parents only (AST-792).

One-time / maintenance: drop log rows whose parent is not User Testing in Linear;
dedupe by ticket_id keeping latest recorded_at per surviving id.

Usage:
    python3 scripts/prune_merge_ticket_log.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.external.linear import LinearApiError, fetch_parent_issue_states
from src.utils.config import MERGE_TICKET_LOG_CONFIG
from src.utils.merge_ticket_log import read_merge_ticket_log, rewrite_merge_ticket_log


def main() -> None:
    entries = read_merge_ticket_log()
    before = len(entries)
    if not entries:
        print("removed=0")
        sys.exit(0)

    ticket_ids = list(
        dict.fromkeys(e.get("ticket_id", "") for e in entries if e.get("ticket_id"))
    )
    try:
        state_by_id = fetch_parent_issue_states(ticket_ids)
    except (LinearApiError, KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    uat = MERGE_TICKET_LOG_CONFIG["uat_state_name"]
    uat_entries = [
        e
        for e in entries
        if state_by_id.get(e.get("ticket_id", "")) == uat
    ]
    # Latest recorded_at per ticket_id, file order preserved for survivors.
    latest_by_id: dict[str, dict] = {}
    for entry in uat_entries:
        ticket_id = entry.get("ticket_id", "")
        if not ticket_id:
            continue
        prev = latest_by_id.get(ticket_id)
        if prev is None or entry.get("recorded_at", "") >= prev.get("recorded_at", ""):
            latest_by_id[ticket_id] = entry
    pruned = [latest_by_id[tid] for tid in latest_by_id]
    pruned.sort(key=lambda e: e.get("recorded_at", ""))
    rewrite_merge_ticket_log(pruned)
    print(f"removed={before - len(pruned)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
