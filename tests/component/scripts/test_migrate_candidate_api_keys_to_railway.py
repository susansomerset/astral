"""AST-2251: migrate ciphertext api_keys into Railway variables, then clear the key field."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/migrate_candidate_api_keys_to_railway.py"


def _load():
    spec = importlib.util.spec_from_file_location("migrate_candidate_api_keys_ast2251", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _plant(db, cid: str, server: str, plaintext: str) -> None:
    from cryptography.fernet import Fernet

    db.save_candidate(cid, state="NEW_CANDIDATE")
    if getattr(db, "_fernet", None) is None or not hasattr(db._fernet, "encrypt"):
        db._fernet = Fernet(Fernet.generate_key())
    token = db.encrypt_value(plaintext)
    conn = db._get_connection()
    try:
        conn.execute(
            "UPDATE candidate SET api_keys = ? WHERE astral_candidate_id = ?",
            (json.dumps([{"server": server, "key": token}]), cid),
        )
        conn.commit()
    finally:
        conn.close()


def _raw(db, cid: str):
    conn = db._get_connection()
    try:
        cell = conn.execute(
            "SELECT api_keys FROM candidate WHERE astral_candidate_id = ?", (cid,)
        ).fetchone()[0]
    finally:
        conn.close()
    return json.loads(cell)


@pytest.fixture
def db(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ASTRAL_DB_DIR", str(tmp_path))
    from src.data import database

    monkeypatch.setattr(database, "DB_PATH", tmp_path / "astral.db")
    for flag in (
        "_candidate_schema_ensured",
        "_job_schema_ensured",
        "_company_schema_ensured",
    ):
        if hasattr(database, flag):
            setattr(database, flag, False)
    return database


class TestAst2251MigrateCiphertext:
    def test_dry_run_prints_name_not_plaintext(
        self, db, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _plant(db, "ada-1", "kimi", "sk-live-value")
        mod = _load()
        import sys
        monkeypatch.setattr(sys, "argv", ["migrate"])
        assert mod.main() == 0
        out = capsys.readouterr().out
        assert "would upsert ada-1 kimi CANDIDATE_ADA_1_KIMI" in out
        assert "sk-live-value" not in out
        assert "key" in _raw(db, "ada-1")[0]

    def test_execute_upserts_then_clears_ciphertext(self, db, monkeypatch: pytest.MonkeyPatch) -> None:
        _plant(db, "ada-1", "kimi", "sk-live-value")
        mod = _load()
        seen = {}

        def _upsert(*, name: str, value: str) -> None:
            seen["name"] = name
            seen["value"] = value

        monkeypatch.setattr(mod, "upsert_service_variable", _upsert)
        import sys
        monkeypatch.setattr(sys, "argv", ["migrate", "--execute"])
        assert mod.main() == 0
        assert seen == {"name": "CANDIDATE_ADA_1_KIMI", "value": "sk-live-value"}
        assert _raw(db, "ada-1") == [{"server": "kimi", "status": "SET", "expires_at": None}]

    def test_failed_upsert_leaves_ciphertext(self, db, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.external.railway import RailwayCallFailed

        _plant(db, "ada-1", "kimi", "sk-live-value")
        before = _raw(db, "ada-1")
        mod = _load()

        def _upsert(*, name: str, value: str) -> None:
            raise RailwayCallFailed("railway upsert failed for " + name)

        monkeypatch.setattr(mod, "upsert_service_variable", _upsert)
        import sys
        monkeypatch.setattr(sys, "argv", ["migrate", "--execute"])
        with pytest.raises(RailwayCallFailed):
            mod.main()
        assert _raw(db, "ada-1") == before

    def test_undecryptable_execute_stores_not_set(
        self, db, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        db.save_candidate("ada-1", state="NEW_CANDIDATE")
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE candidate SET api_keys = ? WHERE astral_candidate_id = ?",
                (json.dumps([{"server": "kimi", "key": "not-a-token"}]), "ada-1"),
            )
            conn.commit()
        finally:
            conn.close()
        mod = _load()
        called = []
        monkeypatch.setattr(mod, "upsert_service_variable", lambda **kwargs: called.append(kwargs))
        import sys
        monkeypatch.setattr(sys, "argv", ["migrate", "--execute"])
        caplog.set_level("WARNING")
        assert mod.main() == 0
        assert called == []
        assert _raw(db, "ada-1") == [{"server": "kimi", "status": "NOT SET", "expires_at": None}]
        assert "ada-1 secret kimi ciphertext would not decrypt" in caplog.text
        assert "not-a-token" not in caplog.text
