#!/usr/bin/env python3
"""Retired (AST-984): entity-row agent_responses JSON columns are gone.

Latest-per-task refs live on agent_data.entity_id via list_entity_latest_agent_refs.
This CLI no longer writes entity columns.
"""
import sys

_MSG = (
    "AST-984: backfill_latest_only_rubric_entity_data.py is retired. "
    "Entity agent_responses JSON columns were dropped; use agent_data.entity_id / "
    "list_entity_latest_agent_refs instead."
)


def main() -> int:
    print(_MSG, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
