#!/usr/bin/env python3
"""Export current agent / agent_task rows to repo JSON under data/admin/ (AST-782).

Usage:
    python3 scripts/export_repo_admin_json.py

Does not restart the server. Overwrites data/admin/agent.json and agent_task.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.repo_admin_json import export_repo_admin_json_to_files  # noqa: E402


def main() -> int:
    counts = export_repo_admin_json_to_files()
    print(f"agent: {counts['agent']} row(s) -> data/admin/agent.json")
    print(f"agent_task: {counts['agent_task']} row(s) -> data/admin/agent_task.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
