"""AST-1500 [bug-repro]: push/upsert scripts hard-fail on dispatch_task.

Fails on the pre-fix tip (scripts still accept/push dispatch_task). Passes once
AST-1496 make-fix bans the table before any DB/network work.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load(name: str, rel: str):
    path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_push = _load("push_tables_to_prod_ast1500", "scripts/push_tables_to_prod.py")
_upsert = _load("upsert_tables_from_prod_ast1500", "scripts/upsert_tables_from_prod.py")


class TestAst1500DispatchTaskScriptBan:
    """Script gate — SystemExit + ban stderr before DB/network."""

    def test_push_tables_hard_fails_on_explicit_dispatch_task(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        db = tmp_path / "astral.db"
        db.write_bytes(b"")  # exists so pre-fix tip gets past LOCAL_DB check
        monkeypatch.setattr(_push, "PROD_URL", "https://example.invalid")
        monkeypatch.setattr(_push, "LOCAL_DB", db)
        pushed: list[str] = []

        def _boom(*_a, **_k):
            pushed.append("called")
            raise AssertionError("push_table must not run when dispatch_task is banned")

        monkeypatch.setattr(_push, "push_table", _boom)
        monkeypatch.setattr(sys, "argv", ["push_tables_to_prod.py", "dispatch_task"])
        with pytest.raises(SystemExit) as ei:
            _push.main()
        assert ei.value.code not in (0, None)
        err = capsys.readouterr().err.lower()
        assert "dispatch_task" in err
        assert "ban" in err or "banned" in err or "refused" in err or "not allowed" in err
        assert pushed == []

    def test_upsert_tables_hard_fails_on_explicit_dispatch_task(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        db = tmp_path / "astral.db"
        db.write_bytes(b"")
        monkeypatch.setattr(_upsert, "PROD_URL", "https://example.invalid")
        monkeypatch.setattr(_upsert, "LOCAL_DB", db)
        upserted: list[str] = []

        def _boom(*_a, **_k):
            upserted.append("called")
            raise AssertionError("upsert_table must not run when dispatch_task is banned")

        monkeypatch.setattr(_upsert, "upsert_table", _boom)
        monkeypatch.setattr(sys, "argv", ["upsert_tables_from_prod.py", "dispatch_task"])
        with pytest.raises(SystemExit) as ei:
            _upsert.main()
        assert ei.value.code not in (0, None)
        err = capsys.readouterr().err.lower()
        assert "dispatch_task" in err
        assert "ban" in err or "banned" in err or "refused" in err or "not allowed" in err
        assert upserted == []

    def test_push_tables_hard_fails_when_default_all_includes_dispatch_task(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        db = tmp_path / "astral.db"
        db.write_bytes(b"")
        monkeypatch.setattr(_push, "PROD_URL", "https://example.invalid")
        monkeypatch.setattr(_push, "LOCAL_DB", db)
        monkeypatch.setattr(_push, "push_table", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("no")))
        monkeypatch.setattr(sys, "argv", ["push_tables_to_prod.py"])
        with pytest.raises(SystemExit) as ei:
            _push.main()
        assert ei.value.code not in (0, None)
        err = capsys.readouterr().err.lower()
        assert "dispatch_task" in err
