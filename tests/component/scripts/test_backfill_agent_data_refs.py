"""AST-978: operator CLI for agent_data ref backfill."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/backfill_agent_data_refs.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("backfill_agent_data_refs", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()


def _fake_result(**overrides: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "scanned": 2,
        "updated": 1,
        "unchanged": 1,
        "skipped_already_ref": 0,
        "errors": 0,
        "actions": [
            {
                "agent_data_id": "early",
                "outcome": "canonical_or_unique",
                "ref_agent_data_id": None,
            },
            {
                "agent_data_id": "late",
                "outcome": "would_set_ref",
                "ref_agent_data_id": "early",
            },
        ],
    }
    base.update(overrides)
    return base


class TestAst978BackfillAgentDataRefsCli:
    def test_default_dry_run_prints_banner_and_summary(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = []

        def fake(*, dry_run: bool = True):
            calls.append(dry_run)
            return _fake_result()

        monkeypatch.setattr(_mod, "backfill_agent_data_refs", fake)
        monkeypatch.setattr(sys, "argv", ["backfill_agent_data_refs.py"])
        assert _mod.main() == 0
        assert calls == [True]
        out = capsys.readouterr().out
        assert "=== DRY RUN — no DB writes ===" in out
        summary = json.loads(out.split("=== DRY RUN — no DB writes ===", 1)[1].strip())
        assert summary["scanned"] == 2
        assert summary["updated"] == 1

    def test_execute_passes_dry_run_false(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = []

        def fake(*, dry_run: bool = True):
            calls.append(dry_run)
            return _fake_result(
                updated=1,
                actions=[
                    {
                        "agent_data_id": "late",
                        "outcome": "set_ref",
                        "ref_agent_data_id": "early",
                    }
                ],
            )

        monkeypatch.setattr(_mod, "backfill_agent_data_refs", fake)
        monkeypatch.setattr(sys, "argv", ["backfill_agent_data_refs.py", "--execute"])
        assert _mod.main() == 0
        assert calls == [False]
        out = capsys.readouterr().out
        assert "DRY RUN" not in out

    def test_debug_emits_index_lines_and_quiet_without(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(_mod, "backfill_agent_data_refs", lambda *, dry_run=True: _fake_result())
        caplog.set_level("INFO")
        monkeypatch.setattr(sys, "argv", ["backfill_agent_data_refs.py", "--debug"])
        assert _mod.main() == 0
        combined = "\n".join(r.message for r in caplog.records)
        assert "index 1/2" in combined or "1/2" in combined
        assert "canonical_or_unique" in combined
        assert "would_set_ref" in combined
        assert "late" in combined
        capsys.readouterr()  # drain

        caplog.clear()
        monkeypatch.setattr(sys, "argv", ["backfill_agent_data_refs.py"])
        assert _mod.main() == 0
        quiet = "\n".join(r.message for r in caplog.records)
        assert "would_set_ref" not in quiet
        assert "canonical_or_unique" not in quiet

    def test_errors_exit_nonzero(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            _mod,
            "backfill_agent_data_refs",
            lambda *, dry_run=True: _fake_result(errors=1, updated=0),
        )
        monkeypatch.setattr(sys, "argv", ["backfill_agent_data_refs.py"])
        assert _mod.main() == 1
        capsys.readouterr()
