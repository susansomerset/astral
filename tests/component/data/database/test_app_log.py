"""Component tests for app_log table cluster (AST-392, AST-1266)."""

from __future__ import annotations

from typing import Tuple


def _app_log_id_pragma(db) -> Tuple[str, int]:
    """Return (declared type, pk flag) for app_log.id."""
    conn = db._get_connection()
    try:
        cols = list(conn.execute("PRAGMA table_info(app_log)").fetchall())
        id_col = next(r for r in cols if r[1] == "id")
        return str(id_col[2] or ""), int(id_col[5])
    finally:
        conn.close()


def _seed_legacy_text_pk_app_log(db, *, with_stray_new: bool = False) -> None:
    """Create pre-AST-1266 TEXT PK app_log (+ optional leftover rebuild temp)."""
    conn = db._get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE app_log (
                id TEXT PRIMARY KEY,
                level TEXT,
                logger_name TEXT,
                message TEXT,
                batch_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT INTO app_log (id, level, logger_name, message, batch_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "uuid-legacy-1",
                "INFO",
                "tests",
                "legacy-msg",
                "batch-1",
                "2026-01-01T00:00:00",
            ),
        )
        if with_stray_new:
            # Interrupted prior rebuild left the temp table behind
            conn.execute(
                """
                CREATE TABLE app_log_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    logger_name TEXT,
                    message TEXT,
                    batch_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.commit()
    finally:
        conn.close()
    db._app_log_schema_ensured = False


# Branches: append row; filter by batch/level.
class TestAddLogEntry:
    def test_appends_log_row(self, sqlite_in_memory) -> None:
        assert sqlite_in_memory.add_log_entry("INFO", "tests", "hello", batch_id="batch-1") is True


class TestListLogEntries:
    def test_filters_by_batch_and_level(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.add_log_entry("INFO", "tests", "keep", batch_id="batch-1")
        db.add_log_entry("ERROR", "tests", "drop", batch_id="batch-2")
        rows = db.list_log_entries(batch_id="batch-1", level="INFO")
        assert len(rows) == 1
        assert rows[0]["message"] == "keep"


class TestAst1266IntegerPk:
    """AST-1266: integer AUTOINCREMENT PK, TEXT→INTEGER migrate, write cutover."""

    def test_fresh_schema_integer_autoincrement_pk(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.add_log_entry("INFO", "tests", "fresh", batch_id="b1") is True
        id_type, pk = _app_log_id_pragma(db)
        assert id_type.upper() == "INTEGER"
        assert pk == 1
        rows = db.list_log_entries(batch_id="b1")
        assert len(rows) == 1
        assert isinstance(rows[0]["id"], int)
        assert rows[0]["id"] >= 1

    def test_write_assigns_distinct_positive_ints_without_client_id(
        self, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        assert db.add_log_entry("INFO", "tests", "a", batch_id="b1") is True
        assert db.add_log_entry("WARNING", "tests", "b", batch_id="b1") is True
        rows = db.list_log_entries(batch_id="b1")
        ids = sorted(r["id"] for r in rows)
        assert ids == [1, 2]
        assert all(isinstance(i, int) for i in ids)
        # UUID strings must not appear as ids after cutover
        assert all(not isinstance(r["id"], str) for r in rows)

    def test_migrates_text_pk_preserving_payload(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _seed_legacy_text_pk_app_log(db)
        # Trigger ensure via list (read path also migrates)
        rows = db.list_log_entries(batch_id="batch-1")
        id_type, pk = _app_log_id_pragma(db)
        assert id_type.upper() == "INTEGER"
        assert pk == 1
        assert len(rows) == 1
        assert rows[0]["message"] == "legacy-msg"
        assert rows[0]["level"] == "INFO"
        assert rows[0]["logger_name"] == "tests"
        assert rows[0]["batch_id"] == "batch-1"
        assert rows[0]["created_at"] == "2026-01-01T00:00:00"
        assert isinstance(rows[0]["id"], int)
        assert rows[0]["id"] != "uuid-legacy-1"
        # Subsequent write must succeed without client UUID
        assert db.add_log_entry("ERROR", "tests", "after-migrate", batch_id="batch-1") is True
        after = db.list_log_entries(batch_id="batch-1", level="ERROR")
        assert len(after) == 1
        assert isinstance(after[0]["id"], int)

    def test_leftover_app_log_new_does_not_brick_rebuild(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        _seed_legacy_text_pk_app_log(db, with_stray_new=True)
        assert db.add_log_entry("INFO", "tests", "post-retry", batch_id="batch-1") is True
        id_type, _pk = _app_log_id_pragma(db)
        assert id_type.upper() == "INTEGER"
        conn = db._get_connection()
        try:
            names = {
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        finally:
            conn.close()
        assert "app_log" in names
        assert "app_log_new" not in names
        messages = {r["message"] for r in db.list_log_entries(batch_id="batch-1")}
        assert "legacy-msg" in messages
        assert "post-retry" in messages

    def test_already_integer_is_noop(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        assert db.add_log_entry("INFO", "tests", "once", batch_id="b1") is True
        before = db.list_log_entries(batch_id="b1")[0]
        db._app_log_schema_ensured = False
        again = db.list_log_entries(batch_id="b1")
        assert len(again) == 1
        assert again[0]["id"] == before["id"]
        assert again[0]["message"] == "once"
        id_type, pk = _app_log_id_pragma(db)
        assert id_type.upper() == "INTEGER"
        assert pk == 1
