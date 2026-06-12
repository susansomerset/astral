#!/usr/bin/env python3
"""Optional per-file frontend branch locks after Vitest (see docs/ASTRAL_TEST_BIBLE.md §6b).

Runs after `npm run test:component:coverage`. Product default: **risk-based frontend tests** —
`LOCKED_AT_100` is empty, so any non-empty list is an explicit adoption of stricter gates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Repo-relative paths under src/ui/frontend/src/ (excluding main.tsx, vite-env.d.ts).
LOCKED_AT_100: list[str] = []


def _repo_relative_key(path_str: str, repo_root: Path) -> str | None:
    """Map Vitest summary key (often absolute) to repo-relative posix path."""
    p = Path(path_str)
    if not p.is_absolute():
        return str(p).replace("\\", "/")
    try:
        return str(p.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return None


def _normalize_summary(data: dict, repo_root: Path) -> dict[str, dict]:
    """Keys in coverage-summary.json may be absolute; normalize to repo-relative."""
    out: dict[str, dict] = {}
    for key, entry in data.items():
        if key == "total":
            continue
        rel = _repo_relative_key(key, repo_root)
        if rel is None:
            continue
        out[rel] = entry
    return out


def _branch_pct(summary: dict) -> float:
    num = summary.get("branches") or {}
    total = num.get("total") or 0
    if total == 0:
        return 100.0
    covered = num.get("covered") or 0
    return 100.0 * covered / total


def _repo_root(start: Path) -> Path:
    start = start.resolve()
    for here in (start, *start.parents):
        if (here / "scripts" / "testing" / "run_component_tests.sh").is_file():
            return here
    return start.parents[3]


def main(argv: list[str]) -> int:
    report_path = Path(argv[1] if len(argv) > 1 else "tests/.coverage/frontend/coverage-summary.json")
    if not report_path.is_file():
        print(f"missing coverage report: {report_path}", file=sys.stderr)
        return 1

    repo_root = Path(argv[2] if len(argv) > 2 else _repo_root(report_path))
    raw = json.loads(report_path.read_text(encoding="utf-8"))
    data = _normalize_summary(raw, repo_root)
    failures: list[str] = []

    for rel in LOCKED_AT_100:
        entry = data.get(rel)
        if entry is None:
            failures.append(f"{rel}: not measured")
            continue
        pct = _branch_pct(entry)
        if pct < 100.0:
            failures.append(f"{rel}: branch coverage {pct:.1f}%")

    if failures:
        print("Per-file frontend branch coverage failures:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"Per-file frontend branch coverage OK ({len(LOCKED_AT_100)} locked files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
