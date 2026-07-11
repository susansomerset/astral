"""Thin smoke for src/data/database.py (AST-392)."""

from __future__ import annotations

import sqlite3

_JOB_IDENTITY_UNIQUE_INDEX = "idx_job_identity_unique"


def _prepare_job_table_no_unique_index(db) -> None:
    """Ensure job DDL without unique index so legacy duplicate fixtures can load."""
    db._job_schema_ensured = False
    conn = db._get_connection()
    try:
        db._ensure_job_schema(conn)
        conn.execute(f"DROP INDEX IF EXISTS {_JOB_IDENTITY_UNIQUE_INDEX}")
        conn.commit()
    finally:
        conn.close()
    db._job_schema_ensured = False


def _insert_job(
    conn: sqlite3.Connection,
    *,
    astral_job_id: str,
    company: str,
    job_title: str | None = None,
    company_job_id: str | None = None,
    created_at: str | None = None,
    state: str = "JD_READY",
) -> None:
    conn.execute(
        """
        INSERT INTO job (
            astral_job_id, company, job_title, company_job_id, state, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (astral_job_id, company, job_title, company_job_id, state, created_at),
    )
    conn.commit()


def _unique_index_exists(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?",
        (_JOB_IDENTITY_UNIQUE_INDEX,),
    ).fetchone()
    return row is not None


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


class TestAst846JobSchemaEnsureDedupeBeforeUniqueIndex:
    """AST-846: dedupe legacy job identity triples before idx_job_identity_unique create."""

    def test_duplicate_triples_index_succeeds(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _prepare_job_table_no_unique_index(db)
        conn = db._get_connection()
        try:
            _insert_job(
                conn,
                astral_job_id="job-old",
                company="acme",
                job_title="Engineer",
                company_job_id="123",
                created_at="2026-01-01 00:00:00",
            )
            _insert_job(
                conn,
                astral_job_id="job-new",
                company="acme",
                job_title="Engineer",
                company_job_id="123",
                created_at="2026-06-01 00:00:00",
            )
        finally:
            conn.close()

        db._job_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_job_schema(conn)
            assert _unique_index_exists(conn)
            rows = conn.execute(
                "SELECT astral_job_id, created_at FROM job ORDER BY astral_job_id"
            ).fetchall()
            assert len(rows) == 1
            assert rows[0][0] == "job-old"
            assert rows[0][1] == "2026-01-01 00:00:00"
        finally:
            conn.close()

    def test_board_placeholders_removed_before_index(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _prepare_job_table_no_unique_index(db)
        conn = db._get_connection()
        try:
            _insert_job(
                conn,
                astral_job_id="board-a",
                company="__board__indeed",
                job_title="Nurse",
                company_job_id="b1",
                created_at="2026-01-01 00:00:00",
            )
            _insert_job(
                conn,
                astral_job_id="board-b",
                company="__board__indeed",
                job_title="Nurse",
                company_job_id="b1",
                created_at="2026-06-01 00:00:00",
            )
        finally:
            conn.close()

        db._job_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_job_schema(conn)
            assert _unique_index_exists(conn)
            board_count = conn.execute(
                "SELECT COUNT(*) FROM job WHERE company LIKE '__board__%'"
            ).fetchone()[0]
            assert board_count == 0
        finally:
            conn.close()

    def test_idempotent_second_ensure(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _prepare_job_table_no_unique_index(db)
        conn = db._get_connection()
        try:
            _insert_job(
                conn,
                astral_job_id="job-old",
                company="acme",
                job_title="Engineer",
                company_job_id="123",
                created_at="2026-01-01 00:00:00",
            )
            _insert_job(
                conn,
                astral_job_id="job-new",
                company="acme",
                job_title="Engineer",
                company_job_id="123",
                created_at="2026-06-01 00:00:00",
            )
        finally:
            conn.close()

        db._job_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_job_schema(conn)
            count_after_first = conn.execute("SELECT COUNT(*) FROM job").fetchone()[0]
        finally:
            conn.close()

        db._job_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_job_schema(conn)
            assert _unique_index_exists(conn)
            count_after_second = conn.execute("SELECT COUNT(*) FROM job").fetchone()[0]
            assert count_after_second == count_after_first == 1
        finally:
            conn.close()

    def test_incomplete_triples_untouched(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _prepare_job_table_no_unique_index(db)
        conn = db._get_connection()
        try:
            _insert_job(
                conn,
                astral_job_id="incomplete-a",
                company="acme",
                job_title="Engineer",
                company_job_id=None,
            )
            _insert_job(
                conn,
                astral_job_id="incomplete-b",
                company="acme",
                job_title="Engineer",
                company_job_id=None,
            )
        finally:
            conn.close()

        db._job_schema_ensured = False
        conn = db._get_connection()
        try:
            db._ensure_job_schema(conn)
            assert _unique_index_exists(conn)
            rows = conn.execute(
                "SELECT astral_job_id FROM job ORDER BY astral_job_id"
            ).fetchall()
            assert [row[0] for row in rows] == ["incomplete-a", "incomplete-b"]
        finally:
            conn.close()

    def test_bootstrap_registry_path(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _prepare_job_table_no_unique_index(db)
        conn = db._get_connection()
        try:
            _insert_job(
                conn,
                astral_job_id="job-old",
                company="acme",
                job_title="Engineer",
                company_job_id="123",
                created_at="2026-01-01 00:00:00",
            )
            _insert_job(
                conn,
                astral_job_id="job-new",
                company="acme",
                job_title="Engineer",
                company_job_id="123",
                created_at="2026-06-01 00:00:00",
            )
        finally:
            conn.close()

        db._job_schema_ensured = True
        db.ensure_all_upsert_registry_schemas_at_startup()

        conn = db._get_connection()
        try:
            assert _unique_index_exists(conn)
            row = conn.execute(
                "SELECT astral_job_id, created_at FROM job"
            ).fetchone()
            assert row is not None
            assert row[0] == "job-old"
            assert row[1] == "2026-01-01 00:00:00"
        finally:
            conn.close()
