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


AST786_EXPECTED_TASK_KEYS = frozenset(
    {
        "advise_job_resume",
        "analysis_upshot",
        "anticipate_scan",
        "check_cover_letter",
        "check_job_resume",
        "contemplate_job",
        "craft_company_search_terms",
        "craft_do_rubric",
        "craft_get_rubric",
        "craft_jobdesc_rubric",
        "craft_joblist_rubric",
        "craft_like_rubric",
        "craft_prefilter_rubric",
        "craft_resume_base",
        "draft_cover_letter",
        "draft_job_resume",
        "evaluate_jd",
        "fetch_jd",
        "fetch_job_pages",
        "fetch_website",
        "finalize_cover_letter",
        "finalize_job_resume",
        "gaze",
        "grade_do",
        "grade_get",
        "grade_like",
        "inflow_discovery",
        "intake_build_request",
        "intake_candidate_response",
        "intake_initiate_candidate",
        "parse_job_list",
        "prefilter_company",
        "propose_application_responses",
        "qualify_job_listings",
        "recheck_no_openings",
        "select_job_page",
        "vet_inflow_discovery",
    },
)


class TestAst786AgentTaskRepoJsonSeed:
    """AST-786 UAT: populated 37-row agent_task repo JSON from UAT fixture."""

    def test_repo_json_matches_uat_fixture_byte_for_byte(self) -> None:
        repo = Path("data/admin/agent_task.json")
        fixture = Path("docs/uat-fixtures/AST-756/expected-agent_task.json")
        assert repo.is_file() and fixture.is_file()
        assert repo.read_bytes() == fixture.read_bytes()

    def test_repo_json_has_37_current_catalog_keys(self) -> None:
        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        assert len(rows) == 37
        assert frozenset(row["task_key"] for row in rows) == AST786_EXPECTED_TASK_KEYS
        assert all(row["current"] == 1 for row in rows)

    def test_spot_check_rows_have_agent_id_and_user_prompt(self) -> None:
        by_key = {
            row["task_key"]: row
            for row in json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        }
        for task_key in ("prefilter_company", "grade_get", "anticipate_scan"):
            row = by_key[task_key]
            assert str(row["agent_id"]).strip()
            assert str(row["user_prompt"]).strip()

    def test_startup_apply_loads_all_37_current_rows(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.data import database as database_mod

        monkeypatch.setattr(database_mod, "_validate_run_next", lambda _c, _k, _rn: None)
        rows = repo_json_mod.load_repo_admin_json_file("agent_task")
        conn = sqlite_in_memory._get_connection()
        try:
            sqlite_in_memory._ensure_agent_task_schema(conn)
            expected_cols = set(sqlite_in_memory.table_columns(conn, "agent_task"))
            for index, row in enumerate(rows, start=1):
                assert set(row.keys()) == expected_cols, f"row {index} {row['task_key']}"
            sqlite_in_memory.apply_agent_task_repo_json_startup(conn, rows)
            conn.commit()
            count = conn.execute(
                "SELECT COUNT(*) FROM agent_task WHERE current = 1",
            ).fetchone()[0]
            assert count == 37
            loaded = sqlite_in_memory.get_agent_task("prefilter_company")
            assert loaded is not None
            assert loaded["agent_id"] == "job_analyst_grace"
            assert loaded["user_prompt"]
        finally:
            conn.close()


AST787_EXPECTED_AGENT_IDS = frozenset(
    {
        "ats_expert_atlas",
        "college_intern_ruth",
        "content_writer_judith",
        "job_analyst_grace",
        "principal_recruiter_estelle",
        "web_scraper_laslo",
    },
)

AST787_AGENT_REPO_COLUMNS = (
    "agent_id",
    "content",
    "brain_setting",
    "temperature",
    "max_tokens",
    "updated_at",
)


def _ast787_fixture_repo_row(fixture_row: dict[str, object]) -> dict[str, object]:
    return {column: fixture_row[column] for column in AST787_AGENT_REPO_COLUMNS}


class TestAst787AgentRepoJsonSeed:
    """AST-787 UAT: six persona rows in agent repo JSON mapped from UAT fixture."""

    def test_repo_json_has_six_sorted_persona_ids(self) -> None:
        rows = json.loads(Path("data/admin/agent.json").read_text(encoding="utf-8"))
        assert len(rows) == 6
        assert frozenset(row["agent_id"] for row in rows) == AST787_EXPECTED_AGENT_IDS
        assert [row["agent_id"] for row in rows] == sorted(AST787_EXPECTED_AGENT_IDS)

    def test_repo_rows_match_fixture_repo_column_mapping(self) -> None:
        repo_rows = json.loads(Path("data/admin/agent.json").read_text(encoding="utf-8"))
        fixture_by_id = {
            row["agent_id"]: row
            for row in json.loads(
                Path("docs/uat-fixtures/AST-756/expected-agent.json").read_text(encoding="utf-8"),
            )
        }
        for repo_row in repo_rows:
            expected = _ast787_fixture_repo_row(fixture_by_id[repo_row["agent_id"]])
            assert repo_row == expected

    def test_repo_rows_use_repo_columns_only(self) -> None:
        expected_cols = set(AST787_AGENT_REPO_COLUMNS)
        for row in json.loads(Path("data/admin/agent.json").read_text(encoding="utf-8")):
            assert set(row.keys()) == expected_cols
            assert "model_code" not in row

    def test_spot_check_personas_have_content_and_brain_setting(self) -> None:
        by_id = {
            row["agent_id"]: row
            for row in json.loads(Path("data/admin/agent.json").read_text(encoding="utf-8"))
        }
        for agent_id in (
            "job_analyst_grace",
            "ats_expert_atlas",
            "principal_recruiter_estelle",
        ):
            row = by_id[agent_id]
            assert str(row["content"]).strip()
            assert str(row["brain_setting"]).strip()

    def test_startup_apply_loads_all_six_agents(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        rows = repo_json_mod.load_repo_admin_json_file("agent")
        conn = sqlite_in_memory._get_connection()
        try:
            sqlite_in_memory.apply_agent_repo_json_startup(conn, rows)
            conn.commit()
            listed = {row["agent_id"] for row in sqlite_in_memory.list_agents()}
            assert listed == AST787_EXPECTED_AGENT_IDS
            grace = sqlite_in_memory.get_agent("job_analyst_grace")
            assert grace is not None
            assert grace["brain_setting"] == "Medium"
            assert grace["content"]
        finally:
            conn.close()
<<<<<<< HEAD
=======

class TestAst793AgentTaskRevertDivergence:
    """AST-793 UAT: revert clears agent_task divergence via exact repo JSON apply."""

    @pytest.fixture(autouse=True)
    def _no_run_next_graph(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.data import database as database_mod

        monkeypatch.setattr(database_mod, "_validate_run_next", lambda _c, _k, _rn: None)

    def _seed_agent_task_from_repo(self, db) -> dict[str, object]:
        rows = repo_json_mod.load_repo_admin_json_file("agent_task")
        conn = db._get_connection()
        try:
            db._ensure_agent_task_schema(conn)
            db.apply_agent_task_repo_json_startup(conn, rows)
            conn.commit()
        finally:
            conn.close()
        return {row["task_key"]: row for row in rows}

    def test_revert_clears_agent_task_divergence_after_db_edit(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_agent_task_from_repo(db)
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE agent_task SET task_name = task_name || ' uat-edit' "
                "WHERE task_key = 'prefilter_company' AND current = 1",
            )
            conn.commit()
        finally:
            conn.close()

        assert repo_json_mod.get_repo_admin_json_divergence_status()["agent_task"]["diverged"] is True
        repo_json_mod.revert_repo_admin_json_table("agent_task")
        assert repo_json_mod.get_repo_admin_json_divergence_status()["agent_task"]["diverged"] is False

    def test_revert_preserves_repo_task_key_uuid(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        file_by_key = self._seed_agent_task_from_repo(db)
        expected_uuid = file_by_key["prefilter_company"]["task_key_uuid"]
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE agent_task SET task_name = task_name || ' uat-edit' "
                "WHERE task_key = 'prefilter_company' AND current = 1",
            )
            conn.commit()
        finally:
            conn.close()

        repo_json_mod.revert_repo_admin_json_table("agent_task")

        conn = db._get_connection()
        try:
            got = conn.execute(
                "SELECT task_key_uuid FROM agent_task WHERE task_key = ? AND current = 1",
                ("prefilter_company",),
            ).fetchone()[0]
        finally:
            conn.close()
        assert got == expected_uuid

    def test_double_revert_agent_task_stays_not_diverged(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        self._seed_agent_task_from_repo(db)
        conn = db._get_connection()
        try:
            conn.execute(
                "UPDATE agent_task SET user_prompt = user_prompt || ' x' "
                "WHERE task_key = 'anticipate_scan' AND current = 1",
            )
            conn.commit()
        finally:
            conn.close()

        repo_json_mod.revert_repo_admin_json_table("agent_task")
        repo_json_mod.revert_repo_admin_json_table("agent_task")
        assert repo_json_mod.get_repo_admin_json_divergence_status()["agent_task"]["diverged"] is False

>>>>>>> 7b2051b
