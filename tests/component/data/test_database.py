"""Thin smoke for src/data/database.py (AST-392)."""

from __future__ import annotations


def test_database_module_imports() -> None:
    from src.data import database

    assert callable(database.save_company)
    assert callable(database.table_columns)
