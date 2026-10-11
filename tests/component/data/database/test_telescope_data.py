"""Component tests for telescope_data table helpers (AST-2131)."""

from __future__ import annotations

import uuid

from src.utils.config import TELESCOPE_DATA_CONFIG


def _rows(db, sql: str, params: tuple = ()) -> list:
    conn = db._get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


# Branches: startup registry ensure on an existing DB; idempotent re-run through the DDL;
# save returns uuid with no data_type gate; compressed at rest; read by id / ids
# (hit, missing, empty-list short-circuit).
class TestAst2131TelescopeData:
    def test_registry_creates_table_and_index_idempotently(self, seeded_db) -> None:
        # AC1 on an existing DB: seeded candidate row is already present before ensure.
        db = seeded_db
        assert db._UPSERT_SCHEMA_ENSURE_FLAGS["telescope_data"] == ("_telescope_data_schema_ensured",)
        assert db._UPSERT_LAZY_SCHEMA_HANDLERS["telescope_data"] is db._ensure_telescope_data_schema
        assert _rows(db, "SELECT name FROM sqlite_master WHERE name='telescope_data'") == []

        db.ensure_all_upsert_registry_schemas_at_startup()
        db._telescope_data_schema_ensured = False  # force the second pass through the DDL
        db.ensure_all_upsert_registry_schemas_at_startup()

        cols = {r[1]: r for r in _rows(db, "PRAGMA table_info(telescope_data)")}
        assert set(cols) == {"telescope_data_id", "candidate_id", "url", "data_type", "content", "created_at"}
        assert cols["telescope_data_id"][5] == 1  # pk flag
        assert cols["content"][2].upper() == "BLOB"
        idx = _rows(db, "PRAGMA index_info(idx_telescope_data_candidate_created)")
        assert [r[2] for r in idx] == ["candidate_id", "created_at"]
        assert db.get_candidate("cand-1") is not None

    def test_save_accepts_any_data_type_and_returns_uuid(self, sqlite_in_memory) -> None:
        # AC2: "JSON" is not a configured data_type and still saves.
        db = sqlite_in_memory
        assert "JSON" not in TELESCOPE_DATA_CONFIG["data_types"]
        new_id = db.save_telescope_data("cand-1", "https://x.test", "JSON", '{"a": 1}')
        assert str(uuid.UUID(new_id)) == new_id

        (row,) = _rows(
            db,
            "SELECT candidate_id, url, data_type, content, created_at FROM telescope_data "
            "WHERE telescope_data_id=?",
            (new_id,),
        )
        assert tuple(row[:3]) == ("cand-1", "https://x.test", "JSON")
        # Compressed at rest (same zlib helper as agent_data), not the plain string.
        assert isinstance(row[3], bytes) and row[3] != b'{"a": 1}'
        assert db._decompress_payload(row[3]) == '{"a": 1}'
        assert row[4]

    def test_reads_return_plain_content_and_skip_missing(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        vt = TELESCOPE_DATA_CONFIG["data_types"]["VISIBLE_TEXT"]
        pl = TELESCOPE_DATA_CONFIG["data_types"]["PAGE_LINKS"]
        a = db.save_telescope_data("cand-1", "https://a.test", vt, "hello page")
        b = db.save_telescope_data(None, None, pl, "[]")
        assert a != b

        assert db.get_telescope_data(a) == "hello page"
        assert db.get_telescope_data("no-such-id") is None
        assert db.get_telescope_data_for_ids([a, b, "no-such-id"]) == {a: "hello page", b: "[]"}
        assert db.get_telescope_data_for_ids([]) == {}
