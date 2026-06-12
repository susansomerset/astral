"""Component tests — administrator Copy Output table upsert (**AST-464**).

SQLite via ``sqlite_in_memory`` fixture; orchestrator ``apply_copy_output_table_upsert``.
"""

from __future__ import annotations

import json
import uuid

import pytest

TASK_KEY_UT = "__ast464_upsert_test_key__"


@pytest.fixture(autouse=True)
def _no_run_next_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not require TASK_CONFIG graph for canned ``agent_task`` rows."""

    from src.data import database as database_mod

    monkeypatch.setattr(database_mod, "_validate_run_next", lambda _c, _k, _rn: None)


@pytest.fixture()
def seeded_agent_task(sqlite_in_memory):
    sqlite_in_memory.save_agent_task(
        TASK_KEY_UT,
        agent_id="seed",
        user_prompt="u1",
        cache_prompt="ca",
        cache_prompt_b="b",
        cache_prompt_c="c",
        cache_prompt_d="d",
        nocache_prompt="no",
        run_next="",
        system_prompt="sys",
    )
    return sqlite_in_memory


def test_malformed_json(sqlite_in_memory) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    r = apply_copy_output_table_upsert(table_name="anything", json_payload="{")
    assert r["ok"] is False and r["inserted"] == 0
    assert "Malformed JSON" in (r["error"] or "")


def test_not_json_object_top_level(sqlite_in_memory):
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    r = apply_copy_output_table_upsert(table_name="anything", json_payload="{ }")
    assert not r["ok"] and "json array" in (r["error"] or "").lower()


def test_row_must_be_object(sqlite_in_memory) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    r = apply_copy_output_table_upsert(table_name="anything", json_payload="[1] ")
    assert r["ok"] is False and "object" in (r["error"] or "").lower()


def test_unknown_table(sqlite_in_memory) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    r = apply_copy_output_table_upsert(
        table_name="__no_such_ast464_table__", json_payload="[] ")
    assert r["ok"] is False and "unknown table" in (r["error"] or "").lower()


def test_table_without_primary_key(sqlite_in_memory) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    db = sqlite_in_memory
    cx = db._get_connection()
    try:
        cx.execute("CREATE TABLE nopk_ast464 ( id TEXT NOT NULL ) ")
        cx.commit()
    finally:
        cx.close()

    r = apply_copy_output_table_upsert(
        table_name="nopk_ast464",
        json_payload=json.dumps([{"id": "a"}]),
    )
    assert r["ok"] is False and "primary key" in (r["error"] or "").lower()


def test_generic_insert_update_skip_and_composite_pk(sqlite_in_memory) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    db = sqlite_in_memory
    cx = db._get_connection()
    try:
        cx.execute(
            """CREATE TABLE copydemo_ast464 (
                   p1 TEXT NOT NULL,
                   p2 INTEGER NOT NULL,
                   val INTEGER NOT NULL,
                   PRIMARY KEY(p1, p2)
               )"""
        )
        cx.commit()
    finally:
        cx.close()

    base = [{"p1": "a", "p2": 1, "val": 10}]

    r1 = apply_copy_output_table_upsert(
        table_name="copydemo_ast464", json_payload=json.dumps(base))
    assert r1["ok"] and r1["inserted"] == 1 and r1["updated"] == r1["skipped"] == 0

    r2 = apply_copy_output_table_upsert(
        table_name="copydemo_ast464", json_payload=json.dumps(base))
    assert r2["ok"] and r2["skipped"] == 1

    r3 = apply_copy_output_table_upsert(
        table_name="copydemo_ast464",
        json_payload=json.dumps([{"p1": "a", "p2": 1, "val": 99}]),
    )
    assert r3["ok"] and r3["updated"] == 1

    chk = db._get_connection()
    try:
        v = chk.execute(
            "SELECT val FROM copydemo_ast464 WHERE p1=? AND p2=?",
            ("a", 1),
        ).fetchone()[0]
        assert v == 99
    finally:
        chk.close()


def test_nested_cell_rejected(sqlite_in_memory) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    db = sqlite_in_memory
    cx = db._get_connection()
    try:
        cx.execute("CREATE TABLE flat_ast464 ( id TEXT PRIMARY KEY, body TEXT ) ")
        cx.commit()
    finally:
        cx.close()

    r = apply_copy_output_table_upsert(
        table_name="flat_ast464",
        json_payload=json.dumps([{"id": "z", "body": {"oops": True}}]),
    )
    assert r["ok"] is False
    err = (r["error"] or "").lower()
    assert "scalar" in err or "reject" in err


def test_fk_failure_zero_writes(sqlite_in_memory) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    db = sqlite_in_memory
    cx = db._get_connection()
    try:
        cx.execute("CREATE TABLE ppt_ast464 (pid TEXT PRIMARY KEY) ")
        cx.execute(
            """CREATE TABLE cct_ast464 (
                   cid TEXT PRIMARY KEY,
                   pid TEXT NOT NULL REFERENCES ppt_ast464(pid)
               )"""
        )
        cx.execute("INSERT INTO ppt_ast464(pid) VALUES ('parent-ok') ")
        cx.commit()
    finally:
        cx.close()

    r_ok = apply_copy_output_table_upsert(
        table_name="cct_ast464",
        json_payload=json.dumps([{"cid": "r1", "pid": "parent-ok"}]),
    )
    assert r_ok["ok"] and r_ok["inserted"] == 1

    r_bad = apply_copy_output_table_upsert(
        table_name="cct_ast464",
        json_payload=json.dumps(
            [
                {"cid": "r_good", "pid": "parent-ok"},
                {"cid": "r_bad_fk", "pid": "__missing_parent__"},
            ],
        ),
    )
    assert r_bad["ok"] is False

    chk = db._get_connection()
    try:
        n = chk.execute("SELECT COUNT(*) FROM cct_ast464 ").fetchone()[0]
        assert n == 1
    finally:
        chk.close()


def test_agent_task_two_current_same_key_rejected(seeded_agent_task) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    db = seeded_agent_task
    cx = db._get_connection()
    try:
        row = cx.execute(
            "SELECT * FROM agent_task WHERE task_key = ? AND current = 1",
            (TASK_KEY_UT,),
        ).fetchone()
        assert row is not None
        d1 = {k: row[k] for k in row.keys()}
    finally:
        cx.close()

    d2 = dict(d1)
    d2["task_key_uuid"] = str(uuid.uuid4())
    payload = json.dumps([d1, d2])

    out = apply_copy_output_table_upsert(
        table_name="agent_task",
        json_payload=payload,
    )
    assert out["ok"] is False
    assert "task_key" in (out["error"] or "").lower()


def test_agent_task_idempotent_reapply_skips(seeded_agent_task) -> None:
    from src.core.table_copy_upsert import apply_copy_output_table_upsert

    db = seeded_agent_task
    cx = db._get_connection()
    try:
        cols = db.table_columns(cx, "agent_task")
        rows = cx.execute(f"SELECT {','.join(cols)} FROM agent_task ").fetchall()
        assert rows
        batch = [dict(zip(cols, r)) for r in rows]
    finally:
        cx.close()

    r1 = apply_copy_output_table_upsert(
        table_name="agent_task",
        json_payload=json.dumps(batch),
    )
    assert r1["ok"], r1
    assert r1["skipped"] >= 1
    assert r1["updated"] == r1["inserted"] == 0
