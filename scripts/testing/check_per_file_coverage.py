#!/usr/bin/env python3
"""Enforce per-file branch coverage locks for component tests."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

LOCKED_AT_100 = [
    "src/utils/config.py",
    "src/utils/formatting.py",
    "src/external/anthropic.py",
    "src/external/gmail.py",
    "src/external/playwright.py",
    "src/core/monitor.py",
    "src/core/timesheets.py",
    "src/core/tracker.py",
    "src/core/candidate.py",
    "src/core/gazer.py",
    "src/core/dispatcher.py",
    "src/core/consult.py",
    "src/core/builder.py",
    "src/core/agent.py",
    "src/core/roster.py",
    "src/ui/auth.py",
    "src/ui/server.py",
    "src/ui/api/api_system.py",
    "src/ui/api/api_candidate.py",
    "src/ui/api/api_companies.py",
    "src/ui/api/api_jobs.py",
    "src/ui/api/api_admin.py",
]


def _branch_pct(summary: dict) -> float:
    num = summary.get("num_branches") or 0
    if num == 0:
        return 100.0
    covered = summary.get("covered_branches") or 0
    return 100.0 * covered / num


def main(argv: list[str]) -> int:
    report_path = Path(argv[1] if len(argv) > 1 else "tests/.coverage/component.json")
    if not report_path.is_file():
        print(f"missing coverage report: {report_path}", file=sys.stderr)
        return 1

    data = json.loads(report_path.read_text(encoding="utf-8"))
    files = data.get("files", {})
    failures: list[str] = []
    integration = os.environ.get("ASTRAL_FTR_COVERAGE_INTEGRATION") == "1"

    for rel in LOCKED_AT_100:
        entry = files.get(str(Path(rel)))
        if entry is None:
            failures.append(f"{rel}: not measured")
            continue
        pct = _branch_pct(entry.get("summary", {}))
        if pct < 100.0:
            if integration:
                print(
                    f"integration branch: not gating {rel} ({pct:.1f}% branches)",
                    file=sys.stderr,
                )
                continue
            failures.append(f"{rel}: branch coverage {pct:.1f}%")

    if failures:
        print("Per-file branch coverage failures:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"Per-file branch coverage OK ({len(LOCKED_AT_100)} locked files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
