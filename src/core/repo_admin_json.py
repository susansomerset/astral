# -*- coding: utf-8 -*-
"""Repo-owned admin JSON for ``agent`` and ``agent_task`` (AST-782).

Applied once per process at startup via ``bootstrap_runtime()`` — not on admin save.
AST-381 admin snapshot export/import remains cancelled.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.data import database
from src.utils.config import (
    _PROJECT_ROOT,
    get_repo_admin_json_path,
    get_repo_admin_json_table_keys,
)
from src.utils.logging import get_logger

__all__ = [
    "apply_repo_admin_json_at_startup",
    "export_repo_admin_json_to_files",
    "load_repo_admin_json_file",
    "repo_admin_json_paths",
]

logger = get_logger(__name__)


def _repo_root() -> Path:
    return _PROJECT_ROOT


def repo_admin_json_paths() -> Dict[str, Path]:
    return {key: get_repo_admin_json_path(key) for key in get_repo_admin_json_table_keys()}


def _reject_nested_json(v: Any, human_path: str) -> None:
    if isinstance(v, (dict, list)):
        raise ValueError(f"{human_path}: repo JSON rows must use flat JSON scalars only")


def load_repo_admin_json_file(table_key: str) -> List[Dict[str, Any]]:
    """Load one repo JSON file; bare Copy Output array of row objects."""
    path = get_repo_admin_json_path(table_key)
    if not path.is_file():
        raise RuntimeError(f"repo admin JSON missing: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"repo admin JSON unreadable: {path}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"repo admin JSON malformed ({path}): {exc}") from exc

    if not isinstance(data, list):
        raise ValueError(f"repo admin JSON must be a JSON array ({path})")

    rows: List[Dict[str, Any]] = []
    for i, elem in enumerate(data, start=1):
        if not isinstance(elem, dict):
            raise ValueError(f"repo admin JSON row must be an object ({table_key} row {i})")
        for key, val in elem.items():
            _reject_nested_json(val, f"{table_key} row {i} column {key!r}")
        rows.append(elem)
    return rows


def apply_repo_admin_json_at_startup() -> None:
    """Load repo JSON files and apply to DB in one transaction (repo wins)."""
    conn = database._get_connection()
    txn = False
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("BEGIN IMMEDIATE")
        txn = True
        for table_key in get_repo_admin_json_table_keys():
            rows = load_repo_admin_json_file(table_key)
            if table_key == "agent":
                database.apply_agent_repo_json_startup(conn, rows)
            elif table_key == "agent_task":
                database.apply_agent_task_repo_json_startup(conn, rows)
            else:
                raise RuntimeError(f"unknown repo admin JSON table: {table_key!r}")
            logger.info("repo_admin_json applied table=%s rows=%d", table_key, len(rows))
        conn.commit()
        txn = False
    except Exception:
        if txn:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def export_repo_admin_json_to_files() -> Dict[str, int]:
    raise NotImplementedError("AST-782 Stage 4")
