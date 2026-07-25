#!/usr/bin/env python3
"""Retired (AST-981 / AST-975): standalone agent_responses table → agent_data migration.

Historical one-shot migrator that SELECTed/JOINed the standalone ``agent_responses``
table. Durable content already lives in ``agent_data``; parent Open question 2
approved hard-drop of remaining standalone-table rows. Do not reintroduce table SQL.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List

_RETIRED_MSG = (
    "migrate_agent_data is retired under AST-981/AST-975 "
    "(standalone agent_responses table → agent_data). Do not run."
)


def get_migratable_task_keys() -> List[str]:
    """Retired — previously listed task_keys from the standalone agent_responses table."""
    raise SystemExit(_RETIRED_MSG)


def run_agent_data_migration(task_key: str) -> Dict[str, Any]:
    """Retired — previously migrated standalone-table rows into agent_data."""
    raise SystemExit(_RETIRED_MSG)


if __name__ == "__main__":
    print(_RETIRED_MSG, file=sys.stderr)
    sys.exit(2)
