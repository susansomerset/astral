# -*- coding: utf-8 -*-
"""Repo-owned admin JSON for ``agent`` and ``agent_task`` (AST-782).

Boot-time apply is disabled (AST-1497 kill-switch). Export / load helpers remain
for operator use and future explicit apply. AST-381 admin snapshot export/import
remains cancelled.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.data import database
from src.utils.config import (
    REPO_ADMIN_JSON_CONFIG,
    _PROJECT_ROOT,
    get_repo_admin_json_path,
    get_repo_admin_json_table_keys,
)
from src.utils.logging import get_logger

__all__ = [
    "apply_repo_admin_json_at_startup",
    "export_repo_admin_json_to_files",
    "get_repo_admin_json_divergence_status",
    "get_repo_admin_json_table_comparison",
    "load_repo_admin_json_file",
    "repo_admin_json_paths",
    "revert_repo_admin_json_table",
]

_REPO_JSON_ROW_KEY = {"agent": "agent_id", "agent_task": "task_key"}

logger = get_logger(__name__)


def _repo_root() -> Path:
    return _PROJECT_ROOT


def repo_admin_json_paths() -> Dict[str, Path]:
    return {key: get_repo_admin_json_path(key) for key in get_repo_admin_json_table_keys()}


def _reject_nested_json(v: Any, human_path: str) -> None:
    if isinstance(v, (dict, list)):
        raise ValueError(f"{human_path}: repo JSON rows must use flat JSON scalars only")


def _normalize_repo_json_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, float):
        return value
    return str(value)


def _normalize_repo_json_row(_table_key: str, row: dict[str, Any]) -> dict[str, Any]:
    return {k: _normalize_repo_json_scalar(v) for k, v in row.items()}


def _sorted_normalized_rows(table_key: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    key_col = _REPO_JSON_ROW_KEY[table_key]
    normalized = [_normalize_repo_json_row(table_key, row) for row in rows]
    return sorted(normalized, key=lambda r: str(r.get(key_col) or ""))


def _fetch_db_repo_json_rows(conn, table_key: str) -> list[dict[str, Any]]:
    if table_key == "agent":
        return database.fetch_agent_repo_json_export_rows(conn)
    if table_key == "agent_task":
        return database.fetch_agent_task_repo_json_export_rows(conn)
    raise ValueError(f"unknown repo admin JSON table: {table_key!r}")


def _repo_admin_json_table_diverged(conn, table_key: str) -> bool:
    file_rows = load_repo_admin_json_file(table_key)
    db_rows = _fetch_db_repo_json_rows(conn, table_key)
    return _sorted_normalized_rows(table_key, db_rows) != _sorted_normalized_rows(table_key, file_rows)


def _normalized_row_maps(
    table_key: str,
    file_rows: list[dict[str, Any]],
    db_rows: list[dict[str, Any]],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    key_col = _REPO_JSON_ROW_KEY[table_key]
    file_by_key: dict[str, dict[str, Any]] = {}
    db_by_key: dict[str, dict[str, Any]] = {}
    file_norm_by_key: dict[str, dict[str, Any]] = {}
    db_norm_by_key: dict[str, dict[str, Any]] = {}
    for row in file_rows:
        k = str(row.get(key_col) or "")
        file_by_key[k] = row
        file_norm_by_key[k] = _normalize_repo_json_row(table_key, row)
    for row in db_rows:
        k = str(row.get(key_col) or "")
        db_by_key[k] = row
        db_norm_by_key[k] = _normalize_repo_json_row(table_key, row)
    return file_by_key, db_by_key, file_norm_by_key, db_norm_by_key


def get_repo_admin_json_table_comparison(table_key: str) -> dict[str, Any]:
    """Structured row/field diff for one repo admin JSON table (AST-1505)."""
    if table_key not in get_repo_admin_json_table_keys():
        raise ValueError(f"unknown repo admin JSON table: {table_key!r}")
    conn = database._get_connection()
    try:
        file_rows = load_repo_admin_json_file(table_key)
        db_rows = _fetch_db_repo_json_rows(conn, table_key)
        file_by_key, db_by_key, file_norm_by_key, db_norm_by_key = _normalized_row_maps(
            table_key, file_rows, db_rows,
        )
        file_keys = set(file_by_key)
        db_keys = set(db_by_key)
        only_in_database = [db_by_key[k] for k in sorted(db_keys - file_keys)]
        only_in_file = [file_by_key[k] for k in sorted(file_keys - db_keys)]
        changed_rows: list[dict[str, Any]] = []
        for k in sorted(file_keys & db_keys):
            file_norm = file_norm_by_key[k]
            db_norm = db_norm_by_key[k]
            fields: list[dict[str, Any]] = []
            for name in sorted(set(file_norm) | set(db_norm)):
                if file_norm.get(name) != db_norm.get(name):
                    fields.append({
                        "field": name,
                        "file_value": file_by_key[k].get(name),
                        "database_value": db_by_key[k].get(name),
                    })
            if fields:
                changed_rows.append({"row_key": k, "fields": fields})
        diverged = bool(only_in_database or only_in_file or changed_rows)
        return {
            "table_key": table_key,
            "diverged": diverged,
            "repo_relative_path": REPO_ADMIN_JSON_CONFIG["tables"][table_key]["repo_relative_path"],
            "only_in_database": only_in_database,
            "only_in_file": only_in_file,
            "changed_rows": changed_rows,
        }
    finally:
        conn.close()


def get_repo_admin_json_divergence_status() -> dict[str, dict[str, Any]]:
    """Compare live DB export rows to checked-in repo JSON per table (AST-783)."""
    conn = database._get_connection()
    try:
        status: dict[str, dict[str, Any]] = {}
        for table_key in get_repo_admin_json_table_keys():
            status[table_key] = {
                "diverged": _repo_admin_json_table_diverged(conn, table_key),
                "repo_relative_path": REPO_ADMIN_JSON_CONFIG["tables"][table_key]["repo_relative_path"],
            }
        return status
    finally:
        conn.close()


def revert_repo_admin_json_table(table_key: str) -> int:
    """Restore one table from checked-in repo JSON without server restart (AST-783)."""
    if table_key not in get_repo_admin_json_table_keys():
        raise ValueError(f"unknown repo admin JSON table: {table_key!r}")
    rows = load_repo_admin_json_file(table_key)
    conn = database._get_connection()
    txn = False
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("BEGIN IMMEDIATE")
        txn = True
        if table_key == "agent":
            database.apply_agent_repo_json_startup(conn, rows)
        else:
            database.apply_agent_task_repo_json_startup(conn, rows)
        conn.commit()
        txn = False
    except Exception:
        if txn:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
    return len(rows)


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
    """Boot-time repo JSON apply disabled (AST-1497 kill-switch).

    Export and row loaders stay for operator use / future explicit apply.
    """
    logger.info("repo_admin_json boot apply disabled (AST-1497)")
    return


def export_repo_admin_json_to_files() -> Dict[str, int]:
    """Write current DB rows to configured repo JSON paths."""
    conn = database._get_connection()
    try:
        agent_rows = database.fetch_agent_repo_json_export_rows(conn)
        task_rows = database.fetch_agent_task_repo_json_export_rows(conn)
    finally:
        conn.close()

    counts: Dict[str, int] = {}
    for table_key, rows in (("agent", agent_rows), ("agent_task", task_rows)):
        path = get_repo_admin_json_path(table_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        counts[table_key] = len(rows)
    return counts
