"""AST-984: backfill_latest_only_rubric_entity_data retired — entity columns gone."""

from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/backfill_latest_only_rubric_entity_data.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "backfill_latest_only_rubric_entity_data_ast984", _SCRIPT
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()


class TestAst984BackfillEntityColumnsRetired:
    def test_cli_exits_2(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(sys, "argv", ["backfill_latest_only_rubric_entity_data.py"])
        with pytest.raises(SystemExit) as ei:
            runpy.run_path(str(_SCRIPT), run_name="__main__")
        assert ei.value.code == 2
        err = capsys.readouterr().err
        assert "retired" in err.lower()
        assert "AST-984" in err

    def test_main_returns_2(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert _mod.main() == 2
        err = capsys.readouterr().err
        assert "list_entity_latest_agent_refs" in err
