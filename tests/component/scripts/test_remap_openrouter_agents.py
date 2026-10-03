"""AST-1950: run-once agent remap — starting modes, new OpenRouter sizes, Kimi fold."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest

import src.data.database as db_mod
from src.utils import config as cfg

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/remap_openrouter_agents.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("remap_openrouter_agents", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()

# AC 13 seed: (agent_id, model_id, brain_setting) — all rows without mode.
_AC13_SEED = (
    ("a1", "qwen/qwen3-32b", "Little"),
    ("a2", "qwen/qwen3-32b", "Medium"),
    ("a3", "gryphe/mythomax-l2-13b", "Little"),
    ("a4", "kimi-k2.6-openrouter", "Little"),
    ("a5", "kimi-k2.6-openrouter", "Big"),
    ("a6", "morph/morph-v3-large", "Little"),
    ("a7", "claude", "Big"),
    ("a8", "deepseek-v4", "Medium"),
)
# AC 13 expected after --apply: agent_id -> (model_id, brain_setting, mode).
_AC13_APPLIED = {
    "a1": ("qwen/qwen3-32b", "Medium", "Deterministic"),
    "a2": ("qwen/qwen3-32b", "Medium", "Deterministic"),
    "a3": ("gryphe/mythomax-l2-13b", "Big", "Deterministic"),
    "a4": ("moonshotai/kimi-k2.6", "Little", "Deterministic"),
    # Mode judged on the pre-remap size: Big -> Creative even though the fold lands on Little.
    "a5": ("moonshotai/kimi-k2.6", "Little", "Creative"),
    # Removed model: model + size untouched, still gets a starting mode.
    "a6": ("morph/morph-v3-large", "Little", "Deterministic"),
    "a7": ("claude", "Big", "Creative"),
    "a8": ("deepseek-v4", "Medium", "Deterministic"),
}


@pytest.fixture
def agent_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Temp file DB with the real post-AST-1948 agent schema; the script's DB seam points at it."""
    path = tmp_path / "astral.db"
    conn = sqlite3.connect(path)
    monkeypatch.setattr(db_mod, "_agent_schema_ensured", False)
    db_mod._ensure_agent_schema(conn)
    conn.close()
    monkeypatch.setattr(_mod, "_get_connection", lambda: sqlite3.connect(path))
    return path


def _seed(path: Path, rows) -> None:
    conn = sqlite3.connect(path)
    conn.executemany(
        "INSERT INTO agent (agent_id, content, model_id, brain_setting, mode, updated_at) "
        "VALUES (?, 'sys', ?, ?, ?, '2026-01-01 00:00:00')",
        rows,
    )
    conn.commit()
    conn.close()


def _rows(path: Path) -> list[tuple]:
    conn = sqlite3.connect(path)
    try:
        return conn.execute("SELECT * FROM agent ORDER BY agent_id").fetchall()
    finally:
        conn.close()


def _state(path: Path) -> dict[str, tuple]:
    conn = sqlite3.connect(path)
    try:
        q = "SELECT agent_id, model_id, brain_setting, mode FROM agent ORDER BY agent_id"
        return {aid: (m, b, mode) for aid, m, b, mode in conn.execute(q).fetchall()}
    finally:
        conn.close()


# Branches: dry run vs --apply vs nothing-to-change; mode missing (NULL / "") vs kept; model in REMAP
# (kept slug / Kimi fold) vs REMOVED vs direct; snapshot tables consistent with the AST-1947 catalog.
class TestAst1950RemapOpenrouterAgents:
    def test_ac13_dry_run_writes_nothing_and_lists_removed(
        self, agent_db: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _seed(agent_db, [(*r, None) for r in _AC13_SEED])
        before = _rows(agent_db)
        assert _mod.main([]) == 0
        assert _rows(agent_db) == before
        out = capsys.readouterr().out
        assert "removed model: a6 on morph/morph-v3-large (Little), left as-is" in out
        assert "a4: kimi-k2.6-openrouter/Little/None -> moonshotai/kimi-k2.6/Little/Deterministic" in out
        assert "8 row(s) would change. Re-run with --apply to commit." in out

    def test_ac13_apply_remaps_exact_rows_and_non_removed_validate(
        self, agent_db: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _seed(agent_db, [(*r, None) for r in _AC13_SEED])
        assert _mod.main(["--apply"]) == 0
        assert "Updated 8 row(s)." in capsys.readouterr().out
        got = _state(agent_db)
        assert got == _AC13_APPLIED
        for aid, (model_id, size, mode) in got.items():
            cfg.validate_agent_mode(mode)
            if model_id in _mod.REMOVED:
                assert model_id not in cfg.LLM_MODEL_CONFIG
                continue
            cfg.validate_brain_setting_for_model(model_id, size)

    def test_second_apply_changes_nothing(self, agent_db: Path, capsys: pytest.CaptureFixture[str]) -> None:
        _seed(agent_db, [(*r, None) for r in _AC13_SEED])
        _mod.main(["--apply"])
        after_first = _rows(agent_db)
        capsys.readouterr()
        assert _mod.main(["--apply"]) == 0
        # Removed-model rows are reported on every run; nothing else is planned.
        assert capsys.readouterr().out.splitlines() == [
            "  removed model: a6 on morph/morph-v3-large (Little), left as-is",
            "No agent rows to change.",
        ]
        assert _rows(agent_db) == after_first

    def test_existing_mode_kept_size_still_remapped_and_blank_mode_filled(
        self, agent_db: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Plan decisions: a set mode is kept (size remap is independent); "" counts as no mode.
        _seed(agent_db, [
            ("k1", "qwen/qwen3-32b", "Little", "Creative"),
            ("k2", "claude", "Big", "Deterministic"),
            ("k3", "deepseek-v4", "Big", ""),
        ])
        assert _mod.main(["--apply"]) == 0
        assert _state(agent_db) == {
            "k1": ("qwen/qwen3-32b", "Medium", "Creative"),
            "k2": ("claude", "Big", "Deterministic"),
            "k3": ("deepseek-v4", "Big", "Creative"),
        }
        out = capsys.readouterr().out
        assert "k2:" not in out and "Updated 2 row(s)." in out

    def test_snapshot_tables_match_ast1947_catalog(self) -> None:
        # Literal snapshot: 63 kept slugs + Kimi fold, 12 removed; targets are each model's one size.
        assert (len(_mod.REMAP), len(_mod.REMOVED)) == (64, 12)
        assert not set(_mod.REMAP) & set(_mod.REMOVED)
        for old, (model_id, size) in _mod.REMAP.items():
            assert cfg.model_brain_sizes(model_id) == (size,), old
            cfg.validate_brain_setting_for_model(model_id, size)
        assert _mod.REMAP["kimi-k2.6-openrouter"] == ("moonshotai/kimi-k2.6", "Little")
        assert not [m for m in _mod.REMOVED if m in cfg.LLM_MODEL_CONFIG]
        # Direct models pass through by absence from both tables.
        assert not {"claude", "kimi-k2.6", "deepseek-v4"} & (set(_mod.REMAP) | set(_mod.REMOVED))
