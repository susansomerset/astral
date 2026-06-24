"""Component tests for src/core/repo_admin_json.py (AST-782)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.core import repo_admin_json as repo_json_mod
from src.utils.config import get_repo_admin_json_path


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class TestLoadRepoAdminJsonFile:
    def test_missing_file_raises_runtime_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        missing = tmp_path / "agent.json"
        monkeypatch.setattr(
            repo_json_mod,
            "get_repo_admin_json_path",
            lambda _key: missing,
        )
        with pytest.raises(RuntimeError, match="repo admin JSON missing"):
            repo_json_mod.load_repo_admin_json_file("agent")

    def test_non_array_raises_value_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        path = tmp_path / "agent.json"
        _write_json(path, {"not": "array"})
        monkeypatch.setattr(repo_json_mod, "get_repo_admin_json_path", lambda _key: path)
        with pytest.raises(ValueError, match="JSON array"):
            repo_json_mod.load_repo_admin_json_file("agent")

    def test_nested_scalar_rejected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        path = tmp_path / "agent.json"
        _write_json(path, [{"agent_id": "a", "nested": {"x": 1}}])
        monkeypatch.setattr(repo_json_mod, "get_repo_admin_json_path", lambda _key: path)
        with pytest.raises(ValueError, match="flat JSON scalars"):
            repo_json_mod.load_repo_admin_json_file("agent")

    def test_loads_valid_row_array(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        path = tmp_path / "agent.json"
        rows = [{"agent_id": "estelle", "content": "hi"}]
        _write_json(path, rows)
        monkeypatch.setattr(repo_json_mod, "get_repo_admin_json_path", lambda _key: path)
        assert repo_json_mod.load_repo_admin_json_file("agent") == rows


class TestApplyRepoAdminJsonAtStartup:
    def test_applies_agent_then_agent_task_on_one_connection(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls: list[str] = []
        conn = MagicMock()
        monkeypatch.setattr(repo_json_mod.database, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            repo_json_mod,
            "load_repo_admin_json_file",
            lambda table_key: calls.append(f"load:{table_key}") or [],
        )
        monkeypatch.setattr(
            repo_json_mod.database,
            "apply_agent_repo_json_startup",
            lambda _c, _rows: calls.append("apply:agent"),
        )
        monkeypatch.setattr(
            repo_json_mod.database,
            "apply_agent_task_repo_json_startup",
            lambda _c, _rows: calls.append("apply:agent_task"),
        )

        repo_json_mod.apply_repo_admin_json_at_startup()

        assert calls == [
            "load:agent",
            "apply:agent",
            "load:agent_task",
            "apply:agent_task",
        ]
        conn.execute.assert_any_call("PRAGMA foreign_keys=ON")
        conn.execute.assert_any_call("BEGIN IMMEDIATE")
        conn.commit.assert_called_once()
        conn.close.assert_called_once()


class TestExportRepoAdminJsonToFiles:
    def test_writes_utf8_arrays_for_both_tables(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        agent_rows = [
            {
                "agent_id": "estelle",
                "content": "prompt",
                "brain_setting": "Medium",
                "temperature": 0.2,
                "max_tokens": 100,
                "updated_at": "2026-06-24 00:00:00",
            },
        ]
        task_rows = [{"task_key": "craft_resume_base", "current": 1}]
        conn = MagicMock()

        def _path(table_key: str) -> Path:
            return tmp_path / f"{table_key}.json"

        monkeypatch.setattr(repo_json_mod.database, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            repo_json_mod.database,
            "fetch_agent_repo_json_export_rows",
            lambda _c: agent_rows,
        )
        monkeypatch.setattr(
            repo_json_mod.database,
            "fetch_agent_task_repo_json_export_rows",
            lambda _c: task_rows,
        )
        monkeypatch.setattr(repo_json_mod, "get_repo_admin_json_path", _path)

        counts = repo_json_mod.export_repo_admin_json_to_files()

        assert counts == {"agent": 1, "agent_task": 1}
        agent_path = _path("agent")
        task_path = _path("agent_task")
        assert json.loads(agent_path.read_text(encoding="utf-8")) == agent_rows
        assert json.loads(task_path.read_text(encoding="utf-8")) == task_rows
        assert agent_path.read_text(encoding="utf-8").endswith("\n")
