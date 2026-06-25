#!/usr/bin/env python3
"""Rebuild merge ticket log for all User Testing parents whose ftr is on dev (AST-800).

Usage:
    python3 scripts/rebuild_merge_ticket_log.py [--dev-ref origin/dev] [--landing-parent AST-NNN]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.external.linear import LinearApiError, fetch_user_testing_parent_ids
from src.utils.config import MERGE_TICKET_LOG_CONFIG
from src.utils.merge_ticket_log import rebuild_merge_ticket_log


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _ftr_refs_for_parent(parent_id: str) -> list[str]:
    result = _run_git("ls-remote", "origin", "refs/heads/ftr/*")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-remote failed")
    needle = parent_id.lower()
    refs: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        _sha, ref = line.split("\t", 1)
        short = ref.removeprefix("refs/heads/")
        if needle in short.lower():
            refs.append(short)
    return sorted(refs)


def _ftr_on_dev(ftr_ref: str, dev_ref: str) -> bool:
    result = _run_git("merge-base", "--is-ancestor", ftr_ref, dev_ref)
    return result.returncode == 0


def _resolve_ftr_ref(parent_id: str, dev_ref: str) -> str | None:
    for ftr_ref in _ftr_refs_for_parent(parent_id):
        if _ftr_on_dev(ftr_ref, dev_ref):
            return ftr_ref
    return None


def _git_log_timestamp(dev_ref: str, *extra_args: str) -> str:
    result = _run_git("log", dev_ref, "-1", "--format=%cI", *extra_args)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _resolve_recorded_at(parent_id: str, dev_ref: str, ftr_ref: str) -> str:
    for grep in (
        f"prep-uat({parent_id}):",
        f"merge-parent({parent_id}):",
        f"finish-up({parent_id}):",
    ):
        recorded_at = _git_log_timestamp(dev_ref, f"--grep={grep}")
        if recorded_at:
            return recorded_at
    return _git_log_timestamp(dev_ref, ftr_ref)


def _collect_entries(
    dev_ref: str,
    uat_state_name: str,
    landing_parent: str | None = None,
) -> list[dict]:
    parent_ids: set[str] = set(fetch_user_testing_parent_ids(uat_state_name=uat_state_name))
    if landing_parent:
        normalized = landing_parent.strip().upper()
        if normalized:
            parent_ids.add(normalized)
    entries: list[dict] = []
    for parent_id in sorted(parent_ids):
        ftr_ref = _resolve_ftr_ref(parent_id, dev_ref)
        if not ftr_ref:
            continue
        recorded_at = _resolve_recorded_at(parent_id, dev_ref, ftr_ref)
        if not recorded_at:
            continue
        entries.append({"ticket_id": parent_id, "recorded_at": recorded_at})
    entries.sort(key=lambda e: e["recorded_at"])
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dev-ref",
        default="origin/dev",
        help="Git ref treated as integration line (default: origin/dev)",
    )
    parser.add_argument(
        "--landing-parent",
        default=None,
        metavar="AST-NNN",
        help="Parent id being prep-uat landed; included even if not yet User Testing in Linear",
    )
    args = parser.parse_args()
    uat = MERGE_TICKET_LOG_CONFIG["uat_state_name"]
    landing_parent = args.landing_parent
    try:
        entries = _collect_entries(args.dev_ref, uat, landing_parent=landing_parent)
    except (LinearApiError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    rebuild_merge_ticket_log(entries)
    summary = {
        "count": len(entries),
        "parents": [e["ticket_id"] for e in entries],
        "landing_parent": landing_parent.strip().upper() if landing_parent else None,
    }
    print(json.dumps(summary))
    sys.exit(0)


if __name__ == "__main__":
    main()
