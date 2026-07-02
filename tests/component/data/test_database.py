"""Thin smoke for src/data/database.py (AST-392)."""

from __future__ import annotations


def test_database_module_imports() -> None:
    from src.data import database

    assert callable(database.save_company)
    assert callable(database.table_columns)


class TestAst843BootstrapSchemaEnsure:
    """AST-843: registry-wide schema ensure at bootstrap is idempotent on legacy company."""

    def test_ensure_all_upsert_registry_schemas_at_startup_idempotent(
        self, sqlite_in_memory,
    ) -> None:
        db = sqlite_in_memory
        db._company_schema_ensured = False
        db._company_candidate_fk_ensured = False
        conn = db._get_connection()
        try:
            conn.execute("DROP TABLE IF EXISTS company")
            conn.execute(
                """
                CREATE TABLE company (
                    short_name TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    company_name TEXT,
                    company_website TEXT,
                    job_site TEXT,
                    batch_id TEXT,
                    company_data TEXT,
                    agent_responses TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    state_updated_at TIMESTAMP
                )
                """
            )
            conn.commit()
            before = [row[1] for row in conn.execute("PRAGMA table_info(company)").fetchall()]
            assert "batch_created_at" not in before
        finally:
            conn.close()

        db.ensure_all_upsert_registry_schemas_at_startup()

        conn = db._get_connection()
        try:
            after_first = [
                row[1] for row in conn.execute("PRAGMA table_info(company)").fetchall()
            ]
            assert "batch_created_at" in after_first
            first_count = len(after_first)
        finally:
            conn.close()

        db.ensure_all_upsert_registry_schemas_at_startup()

        conn = db._get_connection()
        try:
            after_second = [
                row[1] for row in conn.execute("PRAGMA table_info(company)").fetchall()
            ]
            assert after_second == after_first
            assert len(after_second) == first_count
        finally:
            conn.close()
