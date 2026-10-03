"""AST-1958: run-once migration of live agent rows to plain settings + per-SKU ids; drops brain_setting / mode."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

import src.data.database as db_mod
from src.utils import config as cfg

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/remap_agent_settings.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("remap_agent_settings", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()

# Pre-AST-1955 live shape: legacy columns, no setting columns yet (script may run before the app's first start).
_LEGACY_DDL = (
    "CREATE TABLE agent (agent_id TEXT PRIMARY KEY, content TEXT, model_id TEXT, brain_setting TEXT, "
    "mode TEXT, max_tokens INTEGER, updated_at TIMESTAMP)"
)
_SETTINGS = ("model_id", "max_tokens", "quantization", "temperature", "reasoning_effort",
             "provider_allow_fallbacks", "provider_only", "provider_ignore", "provider_sort")

# AC 11 seed, keyed by agent_id: (model_id, brain_setting, mode, max_tokens).
# Null-mode row = plan hand-check row (Big on a thinking-capable slug) per Joan's validate discuss item.
_AC11_SEED = {
    "a-claude": ("claude", "Medium", "Deterministic", 4000),
    "a-deepseek": ("deepseek-v4", "Big", "Creative", 8000),
    "a-kimi": ("kimi-k2.6", "Big", "Creative", None),
    "a-glm": ("z-ai/glm-4.6", "Medium", "Deterministic", None),
    "a-phi": ("microsoft/phi-4", "Little", "Creative", None),
    "a-null": ("openai/gpt-oss-120b", "Big", None, 2000),
}
# AC 11 after --apply, keyed by agent_id: values in _SETTINGS order. Every row: fallbacks 1, rest empty.
_AC11_APPLIED = {
    "a-claude": ("claude-sonnet-4-6", 4000, None, 0.2, None, 1, None, None, None),
    "a-deepseek": ("deepseek-v4-pro", 384000, None, 0.6, None, 1, None, None, None),
    "a-kimi": ("kimi-k2.6", 32000, None, None, None, 1, None, None, None),
    "a-glm": ("z-ai/glm-4.6", None, None, 0.2, "none", 1, None, None, None),
    "a-phi": ("microsoft/phi-4", None, None, 0.6, None, 1, None, None, None),
    # Null mode + Big -> Creative; slug can think -> the call thought: no temperature, no effort.
    "a-null": ("openai/gpt-oss-120b", 2000, None, None, None, 1, None, None, None),
}
_ALREADY_DROPPED = "brain_setting / mode already dropped. Nothing to migrate."


@pytest.fixture
def agent_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Temp file DB behind the real _get_connection; legacy agent table; schema-ensure flag reset."""
    path = tmp_path / "astral.db"
    monkeypatch.setattr(db_mod, "DB_PATH", path)
    # Fresh process in production: the script's _ensure_agent_schema call must actually run.
    monkeypatch.setattr(db_mod, "_agent_schema_ensured", False)
    conn = sqlite3.connect(path)
    conn.execute(_LEGACY_DDL)
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def script_conns(monkeypatch: pytest.MonkeyPatch):
    """Track the script's connections: it exits without closing on an exception (one-shot CLI)."""
    opened: list[sqlite3.Connection] = []
    real = _mod._get_connection
    monkeypatch.setattr(_mod, "_get_connection", lambda: opened.append(real()) or opened[-1])
    yield opened
    for conn in opened:
        conn.close()


def _seed(path: Path, seed: dict) -> None:
    conn = sqlite3.connect(path)
    conn.executemany(
        "INSERT INTO agent (agent_id, content, model_id, brain_setting, mode, max_tokens, updated_at) "
        "VALUES (?, 'sys', ?, ?, ?, ?, '2026-01-01 00:00:00')",
        [(aid, *row) for aid, row in seed.items()],
    )
    conn.commit()
    conn.close()


def _columns(path: Path) -> list[str]:
    conn = sqlite3.connect(path)
    try:
        return [r[1] for r in conn.execute("PRAGMA table_info(agent)").fetchall()]
    finally:
        conn.close()


def _rows(path: Path) -> list[tuple]:
    conn = sqlite3.connect(path)
    try:
        return conn.execute("SELECT * FROM agent ORDER BY agent_id").fetchall()
    finally:
        conn.close()


def _settings(path: Path) -> dict[str, tuple]:
    conn = sqlite3.connect(path)
    try:
        q = f"SELECT agent_id, {', '.join(_SETTINGS)} FROM agent ORDER BY agent_id"
        return {r[0]: tuple(r[1:]) for r in conn.execute(q).fetchall()}
    finally:
        conn.close()


# Branches: columns present vs already dropped; dry run vs --apply (argv vs sys.argv); mode set vs null/""
# (Big vs not); thinks (Creative x CAN_THINK) vs not; deepseek-v4 Big floor (below vs above 384000);
# kimi-k2.6 Big empty vs set max_tokens; SKU_IDS hit vs pass-through; drop failure; unknown mode.
class TestAst1958RemapAgentSettings:
    def test_ac11_dry_run_writes_nothing_and_prints_each_planned_change(
        self, agent_db: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _seed(agent_db, _AC11_SEED)
        cols_before, rows_before = _columns(agent_db), _rows(agent_db)
        assert _mod.main([]) == 0
        # Read-only: same rows, and no setting columns added (DDL runs only on --apply).
        assert (_columns(agent_db), _rows(agent_db)) == (cols_before, rows_before)
        assert capsys.readouterr().out.splitlines() == [
            "  a-claude: claude/Medium/Deterministic max_tokens=4000 -> claude-sonnet-4-6 "
            "max_tokens=4000 temperature=0.2 reasoning_effort=None",
            "  a-deepseek: deepseek-v4/Big/Creative max_tokens=8000 -> deepseek-v4-pro "
            "max_tokens=384000 temperature=0.6 reasoning_effort=None",
            "  a-glm: z-ai/glm-4.6/Medium/Deterministic max_tokens=None -> z-ai/glm-4.6 "
            "max_tokens=None temperature=0.2 reasoning_effort=none",
            "  a-kimi: kimi-k2.6/Big/Creative max_tokens=None -> kimi-k2.6 "
            "max_tokens=32000 temperature=None reasoning_effort=None",
            "  a-null: openai/gpt-oss-120b/Big/Creative max_tokens=2000 -> openai/gpt-oss-120b "
            "max_tokens=2000 temperature=None reasoning_effort=None",
            "  a-phi: microsoft/phi-4/Little/Creative max_tokens=None -> microsoft/phi-4 "
            "max_tokens=None temperature=0.6 reasoning_effort=None",
            "",
            "6 row(s) would change, then brain_setting and mode would be dropped. Re-run with --apply to commit.",
        ]

    def test_ac11_apply_writes_exact_rows_and_drops_both_columns(
        self, agent_db: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _seed(agent_db, _AC11_SEED)
        # Operator CLI path: main() with no argv reads sys.argv.
        monkeypatch.setattr(sys, "argv", ["remap_agent_settings.py", "--apply"])
        assert _mod.main() == 0
        assert capsys.readouterr().out.endswith("\nUpdated 6 row(s); dropped brain_setting and mode.\n")
        assert _settings(agent_db) == _AC11_APPLIED
        cols = _columns(agent_db)
        assert "brain_setting" not in cols and "mode" not in cols

    def test_second_run_reports_already_dropped_and_changes_nothing(
        self, agent_db: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _seed(agent_db, _AC11_SEED)
        _mod.main(["--apply"])
        after_first = _rows(agent_db)
        capsys.readouterr()
        # Idempotence is by column presence: dry run and --apply both stop at the same line.
        for argv in ([], ["--apply"]):
            assert _mod.main(argv) == 0
            assert capsys.readouterr().out.splitlines() == [_ALREADY_DROPPED]
        assert _rows(agent_db) == after_first

    def test_plan_decision_rows_and_settings_already_written_are_overwritten(self, agent_db: Path) -> None:
        # App already started once on new code: setting columns exist and carry stray values.
        conn = sqlite3.connect(agent_db)
        db_mod._ensure_agent_schema(conn)
        conn.close()
        db_mod._agent_schema_ensured = False
        _seed(agent_db, {
            "e-claude-little": ("claude", "Little", "Deterministic", None),
            "e-claude-big": ("claude", "Big", "Creative", None),
            "e-claude-odd": ("claude", "Huge", "Deterministic", None),
            "e-ds-little": ("deepseek-v4", "Little", "Deterministic", None),
            "e-ds-medium": ("deepseek-v4", "Medium", "Creative", 1000),
            "e-ds-big-high": ("deepseek-v4", "Big", "Creative", 500000),
            "e-kimi-big-set": ("kimi-k2.6", "Big", "Creative", 20000),
            "e-kimi-medium": ("kimi-k2.6", "Medium", "Deterministic", None),
            "e-null-little": ("qwen/qwen3-32b", "Little", None, None),
            "e-blank-big": ("z-ai/glm-4.6", "Big", "", None),
        })
        conn = sqlite3.connect(agent_db)
        conn.execute(
            "UPDATE agent SET quantization = 'fp8', temperature = 1.5, reasoning_effort = 'high', "
            "provider_allow_fallbacks = 0, provider_only = '[\"x\"]', provider_ignore = '[\"y\"]', "
            "provider_sort = 'price'"
        )
        conn.commit()
        conn.close()
        assert _mod.main(["--apply"]) == 0
        assert _settings(agent_db) == {
            "e-claude-little": ("claude-haiku-4-5", None, None, 0.2, None, 1, None, None, None),
            # claude could not think: Creative still sent its temperature, no effort.
            "e-claude-big": ("claude-opus-4-6", None, None, 0.6, None, 1, None, None, None),
            # Unexpected size on a direct id: id kept, no validation (code it loosely).
            "e-claude-odd": ("claude", None, None, 0.2, None, 1, None, None, None),
            "e-ds-little": ("deepseek-v4-flash", None, None, 0.2, None, 1, None, None, None),
            # Floor applies to Big only.
            "e-ds-medium": ("deepseek-v4-pro", 1000, None, 0.6, None, 1, None, None, None),
            # "At least 384000": a larger stored value wins.
            "e-ds-big-high": ("deepseek-v4-pro", 500000, None, 0.6, None, 1, None, None, None),
            # 32000 only fills an empty max_tokens; kimi Creative thought -> no temperature.
            "e-kimi-big-set": ("kimi-k2.6", 20000, None, None, None, 1, None, None, None),
            "e-kimi-medium": ("kimi-k2.6", None, None, 0.2, "none", 1, None, None, None),
            # Null mode, not Big -> Deterministic; thinking-capable slug sent thinking-off -> "none".
            "e-null-little": ("qwen/qwen3-32b", None, None, 0.2, "none", 1, None, None, None),
            # "" counts as no mode: Big -> Creative, glm thinks.
            "e-blank-big": ("z-ai/glm-4.6", None, None, None, None, 1, None, None, None),
        }

    def test_failed_drop_rolls_back_the_whole_migration(self, agent_db: Path, script_conns: list) -> None:
        _seed(agent_db, _AC11_SEED)
        # An index on mode makes DROP COLUMN mode fail after brain_setting already dropped.
        conn = sqlite3.connect(agent_db)
        conn.execute("CREATE INDEX agent_mode_idx ON agent(mode)")
        conn.commit()
        conn.close()
        with pytest.raises(sqlite3.OperationalError):
            _mod.main(["--apply"])
        # Script never commits on failure; closing its connection discards the open transaction.
        script_conns[0].close()
        conn = sqlite3.connect(agent_db)
        try:
            q = "SELECT agent_id, model_id, brain_setting, mode, max_tokens FROM agent ORDER BY agent_id"
            legacy = {r[0]: tuple(r[1:]) for r in conn.execute(q).fetchall()}
        finally:
            conn.close()
        assert legacy == _AC11_SEED

    def test_unknown_mode_raises_before_anything_writes(self, agent_db: Path, script_conns: list) -> None:
        _seed(agent_db, {**_AC11_SEED, "z-wild": ("claude", "Medium", "Wild", None)})
        cols_before, rows_before = _columns(agent_db), _rows(agent_db)
        for argv in ([], ["--apply"]):
            with pytest.raises(KeyError, match="Wild"):
                _mod.main(argv)
        assert (_columns(agent_db), _rows(agent_db)) == (cols_before, rows_before)

    def test_snapshot_tables(self) -> None:
        # Literal 2026-10-03 snapshot: 58 thinking ids; per-SKU targets resolve in today's catalog.
        assert len(_mod.CAN_THINK) == 58
        assert "kimi-k2.6" in _mod.CAN_THINK
        assert not {"claude", "deepseek-v4"} & _mod.CAN_THINK
        assert {old for old, _ in _mod.SKU_IDS} == {"claude", "deepseek-v4"}
        assert not {"claude", "deepseek-v4"} & set(cfg.LLM_MODEL_CONFIG)
        assert not [m for m in _mod.SKU_IDS.values() if m not in cfg.LLM_MODEL_CONFIG]
        assert _mod.MODE_TEMPERATURE == {"Deterministic": 0.2, "Creative": 0.6}
