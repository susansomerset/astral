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


class TestAst783RepoAdminJsonDivergence:
    def test_scalar_normalization_coerces_integer_floats(self) -> None:
        assert repo_json_mod._normalize_repo_json_scalar(1.0) == 1
        assert repo_json_mod._normalize_repo_json_scalar(3.0) == 3
        assert repo_json_mod._normalize_repo_json_scalar(2.5) == 2.5

    def _patch_repo_paths(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> tuple[Path, Path]:
        agent_path = tmp_path / "admin" / "agent.json"
        task_path = tmp_path / "admin" / "agent_task.json"
        monkeypatch.setattr(
            repo_json_mod,
            "get_repo_admin_json_path",
            lambda key: agent_path if key == "agent" else task_path,
        )
        return agent_path, task_path

    def test_status_not_diverged_when_db_matches_repo_files(
        self, sqlite_in_memory, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        agent_path, task_path = self._patch_repo_paths(monkeypatch, tmp_path)
        db = sqlite_in_memory
        db.save_agent("agent_a", "prompt-body", brain_setting="Medium")
        conn = db._get_connection()
        try:
            file_row = db.fetch_agent_repo_json_export_rows(conn)[0]
        finally:
            conn.close()
        _write_json(agent_path, [file_row])
        _write_json(task_path, [])

        status = repo_json_mod.get_repo_admin_json_divergence_status()

        assert status["agent"]["diverged"] is False
        assert status["agent_task"]["diverged"] is False

    def test_status_diverged_after_db_edit(
        self, sqlite_in_memory, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        agent_path, task_path = self._patch_repo_paths(monkeypatch, tmp_path)
        db = sqlite_in_memory
        db.save_agent("agent_a", "on-disk", brain_setting="Medium")
        conn = db._get_connection()
        try:
            file_row = db.fetch_agent_repo_json_export_rows(conn)[0]
        finally:
            conn.close()
        _write_json(agent_path, [file_row])
        _write_json(task_path, [])
        db.save_agent("agent_a", "edited-in-db", brain_setting="Medium")

        status = repo_json_mod.get_repo_admin_json_divergence_status()

        assert status["agent"]["diverged"] is True

    def test_revert_restores_db_from_repo_file(
        self, sqlite_in_memory, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        agent_path, task_path = self._patch_repo_paths(monkeypatch, tmp_path)
        db = sqlite_in_memory
        db.save_agent("agent_a", "repo-copy", brain_setting="Little")
        conn = db._get_connection()
        try:
            file_row = db.fetch_agent_repo_json_export_rows(conn)[0]
        finally:
            conn.close()
        _write_json(agent_path, [file_row])
        _write_json(task_path, [])
        db.save_agent("agent_a", "local-edit", brain_setting="Big")
        assert repo_json_mod.get_repo_admin_json_divergence_status()["agent"]["diverged"] is True

        count = repo_json_mod.revert_repo_admin_json_table("agent")

        assert count == 1
        row = db.get_agent("agent_a")
        assert row is not None
        assert row["content"] == "repo-copy"
        assert row["brain_setting"] == "Little"
        assert repo_json_mod.get_repo_admin_json_divergence_status()["agent"]["diverged"] is False

    def test_revert_unknown_table_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown repo admin JSON table"):
            repo_json_mod.revert_repo_admin_json_table("__nope__")
