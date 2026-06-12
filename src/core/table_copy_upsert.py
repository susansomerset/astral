# -*- coding: utf-8 -*-
"""Administrator Copy Output → SQLite upsert orchestration (core → data).

AST-465 will call ``apply_copy_output_table_upsert`` from Flask; this module stays
route-free — single transactional entry point with FK rollback on violations.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

import sqlite3

from src.data import database as database


def apply_copy_output_table_upsert(*, table_name: str, json_payload: str) -> Dict[str, Any]:
    """Parse Copy Output JSON, validate structure, upsert rows in one transaction.

    Returns ``{ok, inserted, updated, skipped, error}``; counts are zeros when ``ok`` is False."""
    zeros: Dict[str, Any] = {
        "ok": False,
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "error": None,
    }

    conn = database._get_connection()
    txn = False

    try:
        conn.execute("PRAGMA foreign_keys=ON")
        fk_row = conn.execute("PRAGMA foreign_keys").fetchone()
        if fk_row is None or int(fk_row[0]) != 1:
            raise RuntimeError("foreign key enforcement unavailable (expected PRAGMA foreign_keys=ON to stick)")

        try:
            data = json.loads(json_payload)
        except json.JSONDecodeError:
            return {**zeros, "error": "Malformed JSON"}

        if not isinstance(data, list):
            return {**zeros, "error": "Payload must be a JSON array"}

        parsed_rows: List[Dict[str, Any]] = []
        # 1-based row numbers — match data-layer shape errors for admin-facing paste.
        for i, elem in enumerate(data, start=1):
            if not isinstance(elem, dict):
                return {**zeros, "error": f"Each row must be an object (row {i})"}
            parsed_rows.append(elem)

        try:
            database.table_columns(conn, table_name)
        except ValueError as e:
            return {**zeros, "error": str(e)}

        try:
            database.primary_key_column_names(conn, table_name)
        except ValueError as e:
            return {**zeros, "error": str(e)}

        conn.execute("BEGIN IMMEDIATE")
        txn = True

        if table_name == "agent_task":
            database._ensure_agent_task_schema(conn)
            counts = database.apply_agent_task_copy_upsert(conn, parsed_rows)
        else:
            counts = database.apply_generic_table_copy_upsert(conn, table_name, parsed_rows)

        conn.commit()
        txn = False
        return {
            "ok": True,
            "inserted": counts["inserted"],
            "updated": counts["updated"],
            "skipped": counts["skipped"],
            "error": None,
        }
    except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
        if txn:
            conn.execute("ROLLBACK")
        return {**zeros, "error": str(e)}
    except ValueError as e:
        if txn:
            conn.execute("ROLLBACK")
        return {**zeros, "error": str(e)}
    except RuntimeError as e:
        if txn:
            conn.execute("ROLLBACK")
        return {**zeros, "error": str(e)}
    finally:
        conn.close()
