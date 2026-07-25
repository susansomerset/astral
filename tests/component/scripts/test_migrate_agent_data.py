"""AST-981: migrate_agent_data retired — no standalone-table SQL path."""

from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/migrate_agent_data.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("migrate_agent_data_ast981", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()


class TestAst981MigrateAgentDataRetired:
    def test_module_entrypoints_exit_retired(self) -> None:
        with pytest.raises(SystemExit) as ei:
            _mod.get_migratable_task_keys()
        assert "retired" in str(ei.value).lower()
        assert "AST-981" in str(ei.value)

        with pytest.raises(SystemExit) as ei2:
            _mod.run_agent_data_migration("evaluate_jd")
        assert "retired" in str(ei2.value).lower()

    def test_cli_exits_2(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(sys, "argv", ["migrate_agent_data.py"])
        with pytest.raises(SystemExit) as ei:
            runpy.run_path(str(_SCRIPT), run_name="__main__")
        assert ei.value.code == 2
        err = capsys.readouterr().err
        assert "retired" in err.lower()
        assert "AST-981" in err
