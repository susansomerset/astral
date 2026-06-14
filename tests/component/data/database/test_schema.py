"""Component tests for schema helpers on src/data/database.py (AST-392)."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet


# Branches: missing table; PRAGMA column list.
class TestTableColumns:
    def test_raises_for_unknown_table(self, sqlite_in_memory) -> None:
        conn = sqlite_in_memory._get_connection()
        try:
            with pytest.raises(ValueError, match="unknown table"):
                sqlite_in_memory.table_columns(conn, "missing")
        finally:
            conn.close()

    def test_returns_columns_after_candidate_schema(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="NEW")
        conn = sqlite_in_memory._get_connection()
        try:
            cols = sqlite_in_memory.table_columns(conn, "candidate")
            assert "astral_candidate_id" in cols
            assert cols == [r[1] for r in conn.execute("PRAGMA table_info(candidate)").fetchall()]
        finally:
            conn.close()


# Branches: disallowed table; column mismatch; row shape; per-table upsert paths.


def _config_upsert_columns(db, conn, table: str) -> list[str]:
    """Post-AST-629: upsert always re-runs ensure; column list must match post-ensure schema."""
    db.ensure_table_schema_for_upsert(conn, table)
    return db.table_columns(conn, table)

class TestApplyConfigTableUpsert:
    def test_rejects_disallowed_table(self, sqlite_in_memory) -> None:
        conn = sqlite_in_memory._get_connection()
        try:
            with pytest.raises(ValueError, match="table not allowed"):
                sqlite_in_memory.apply_config_table_upsert(conn, "company", [], [])
        finally:
            conn.close()

    def test_rejects_column_list_mismatch(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="NEW")
        conn = sqlite_in_memory._get_connection()
        try:
            with pytest.raises(ValueError, match="column list must match"):
                sqlite_in_memory.apply_config_table_upsert(conn, "candidate", ["bad"], [])
        finally:
            conn.close()

    def test_rejects_non_list_row(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="NEW")
        conn = sqlite_in_memory._get_connection()
        try:
            cols = _config_upsert_columns(sqlite_in_memory, conn, "candidate")
            with pytest.raises(ValueError, match="is not a list"):
                sqlite_in_memory.apply_config_table_upsert(conn, "candidate", cols, [("tuple",)])
        finally:
            conn.close()

    def test_rejects_row_length_mismatch(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="NEW")
        conn = sqlite_in_memory._get_connection()
        try:
            cols = _config_upsert_columns(sqlite_in_memory, conn, "candidate")
            with pytest.raises(ValueError, match="has 1 values"):
                sqlite_in_memory.apply_config_table_upsert(conn, "candidate", cols, [["only-one"]])
        finally:
            conn.close()

    def test_upserts_candidate_rows(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_candidate("cand-1", state="NEW")
        conn = sqlite_in_memory._get_connection()
        try:
            cols = _config_upsert_columns(sqlite_in_memory, conn, "candidate")
            row = list(conn.execute("SELECT * FROM candidate WHERE astral_candidate_id = ?", ("cand-1",)).fetchone())
            out = sqlite_in_memory.apply_config_table_upsert(conn, "candidate", cols, [row])
            conn.commit()
            assert out["replaced"] == 1
        finally:
            conn.close()

    def test_inserts_and_updates_dispatch_task(self, seeded_db) -> None:
        db = seeded_db
        task_id = db.save_dispatch_task("cand-1", "qualify_job_listings", min_count=1, trigger_state="IMPORTED")
        conn = db._get_connection()
        try:
            cols = _config_upsert_columns(db, conn, "dispatch_task")
            row = list(conn.execute("SELECT * FROM dispatch_task WHERE id = ?", (task_id,)).fetchone())
            inserted = db.apply_config_table_upsert(
                conn,
                "dispatch_task",
                cols,
                [[*row[:-1], row[-1]]],  # same row → update path
            )
            conn.commit()
            assert inserted["updated"] == 1
            assert inserted["inserted"] == 0

            new_row = list(row)
            new_row[cols.index("candidate_id")] = "cand-1"
            new_row[cols.index("trigger_state")] = "WATCH"
            created = db.apply_config_table_upsert(conn, "dispatch_task", cols, [new_row])
            conn.commit()
            assert created["inserted"] == 1
        finally:
            conn.close()

    def test_replaces_agent_task_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent_task("qualify_job_listings", agent_id="agent-1", user_prompt="hi")
        conn = db._get_connection()
        try:
            cols = _config_upsert_columns(db, conn, "agent_task")
            row = list(conn.execute("SELECT * FROM agent_task LIMIT 1").fetchone())
            out = db.apply_config_table_upsert(conn, "agent_task", cols, [row])
            conn.commit()
            assert out["replaced"] == 1
        finally:
            conn.close()

    def test_config_upsert_stale_candidate_schema_ensure_before_validate(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.data import database as db

        monkeypatch.setattr(db, "_candidate_schema_ensured", False)
        cx = sqlite_in_memory._get_connection()
        try:
            cx.execute("DROP TABLE IF EXISTS candidate")
            cx.execute(
                """
                CREATE TABLE candidate (
                    astral_candidate_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL DEFAULT 'NEW',
                    candidate_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    state_changed_at TIMESTAMP
                )
                """
            )
            cx.commit()
        finally:
            cx.close()

        db._candidate_schema_ensured = False
        learn = sqlite_in_memory._get_connection()
        try:
            db._ensure_candidate_schema(learn)
            cols = db.table_columns(learn, "candidate")
        finally:
            learn.close()

        db._candidate_schema_ensured = False
        row = {
            "astral_candidate_id": "cand-ast627",
            "state": "NEW",
            "candidate_data": "{}",
            "created_at": None,
            "updated_at": None,
            "state_changed_at": None,
        }
        for c in cols:
            row.setdefault(c, None)
        row_list = [row[c] for c in cols]

        conn = sqlite_in_memory._get_connection()
        try:
            out = sqlite_in_memory.apply_config_table_upsert(
                conn, "candidate", cols, [row_list],
            )
            conn.commit()
            assert out["ok"] is True
            assert out["replaced"] == 1
        finally:
            conn.close()

    def test_config_upsert_stale_candidate_when_schema_flag_already_true(
        self, sqlite_in_memory,
    ) -> None:
        """AST-629: config upsert clears process-global ensure flags before migrating stale DB."""
        from src.data import database as db

        cx = sqlite_in_memory._get_connection()
        try:
            cx.execute("DROP TABLE IF EXISTS candidate")
            cx.execute(
                """
                CREATE TABLE candidate (
                    astral_candidate_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL DEFAULT 'NEW',
                    candidate_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    state_changed_at TIMESTAMP
                )
                """
            )
            cx.commit()
        finally:
            cx.close()

        learn = sqlite_in_memory._get_connection()
        try:
            db._ensure_candidate_schema(learn)
            cols = db.table_columns(learn, "candidate")
        finally:
            learn.close()

        db._candidate_schema_ensured = True
        row = {
            "astral_candidate_id": "cand-ast629",
            "state": "NEW",
            "candidate_data": "{}",
            "created_at": None,
            "updated_at": None,
            "state_changed_at": None,
        }
        for c in cols:
            row.setdefault(c, None)
        row_list = [row[c] for c in cols]

        conn = sqlite_in_memory._get_connection()
        try:
            out = sqlite_in_memory.apply_config_table_upsert(
                conn, "candidate", cols, [row_list],
            )
            conn.commit()
            assert out["ok"] is True
            assert out["replaced"] == 1
        finally:
            conn.close()


# Branches: missing key; encrypt/decrypt round-trip; bad ciphertext.
class TestEncryptValue:
    def test_raises_without_encryption_key(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sqlite_in_memory, "_fernet", None)
        with pytest.raises(RuntimeError, match="cannot encrypt"):
            sqlite_in_memory.encrypt_value("secret")

    def test_round_trip_with_valid_key(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        key = Fernet.generate_key().decode()
        monkeypatch.setenv("ASTRAL_ENCRYPTION_KEY", key)
        monkeypatch.setattr(sqlite_in_memory, "_fernet", Fernet(key.encode()))
        cipher = sqlite_in_memory.encrypt_value("secret")
        assert sqlite_in_memory.decrypt_value(cipher) == "secret"

    def test_decrypt_rejects_invalid_token(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        key = Fernet.generate_key().decode()
        monkeypatch.setattr(sqlite_in_memory, "_fernet", Fernet(key.encode()))
        with pytest.raises(ValueError, match="Decryption failed"):
            sqlite_in_memory.decrypt_value("not-a-token")

    def test_decrypt_requires_configured_key(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sqlite_in_memory, "_fernet", None)
        with pytest.raises(RuntimeError, match="cannot decrypt"):
            sqlite_in_memory.decrypt_value("anything")
