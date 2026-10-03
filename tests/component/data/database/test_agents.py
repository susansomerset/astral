"""Component tests for agent table cluster (AST-392)."""

from __future__ import annotations

import pytest

# AST-1948: every agent write carries mode (Deterministic|Creative); the row temperature is gone.
_DET = "Deterministic"


# Branches: insert with brain_setting; update optional fields; delete; task refs.
class TestSaveAgent:
    def test_insert_and_update(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt", mode=_DET, brain_setting="Medium", max_tokens=100)
        row = db.get_agent("agent-1")
        assert row is not None
        assert row["content"] == "prompt"
        assert row["brain_setting"] == "Medium"
        assert row["mode"] == _DET
        db.save_agent("agent-1", "prompt-2", mode="Creative")
        row = db.get_agent("agent-1")
        assert row is not None
        assert row["content"] == "prompt-2"
        assert row["mode"] == "Creative"
        # Retired columns never surface on the row.
        assert "temperature" not in row and "model_code" not in row

    def test_insert_requires_brain_setting(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="brain_setting"):
            sqlite_in_memory.save_agent("agent-new", "prompt", mode=_DET)


class TestListAgents:
    def test_returns_saved_agents(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_agent("agent-1", "one", mode=_DET, brain_setting="Little")
        sqlite_in_memory.save_agent("agent-2", "two", mode="Creative", brain_setting="Big")
        rows = {row["agent_id"]: row for row in sqlite_in_memory.list_agents()}
        assert set(rows) == {"agent-1", "agent-2"}
        assert (rows["agent-1"]["mode"], rows["agent-2"]["mode"]) == (_DET, "Creative")


class TestDeleteAgent:
    def test_deletes_existing_agent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt", mode=_DET, brain_setting="Medium")
        assert db.delete_agent("agent-1") is True
        assert db.get_agent("agent-1") is None


class TestCountAgentTaskRefs:
    def test_counts_task_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt", mode=_DET, brain_setting="Medium")
        db.save_agent_task("qualify_job_listings", agent_id="agent-1", user_prompt="hi")
        assert db.count_agent_task_refs("agent-1") == 1


def _agent_repo_row(
    agent_id: str,
    *,
    content: str = "prompt",
    brain_setting: str = "Medium",
    model_id: str | None = "claude",
    mode: str | None = _DET,
    max_tokens: int | None = 100,
    updated_at: str = "2026-06-24 00:00:00",
) -> dict:
    return {
        "agent_id": agent_id,
        "content": content,
        # AST-1878: repo JSON rows require a catalog model whose sizes include brain_setting.
        "model_id": model_id,
        "brain_setting": brain_setting,
        # AST-1948: mode replaces temperature in the repo JSON shape.
        "mode": mode,
        "max_tokens": max_tokens,
        "updated_at": updated_at,
    }


# AST-782: repo-owned agent JSON startup upsert + export queries.
class TestAst782AgentRepoJsonStartup:
    def test_apply_upserts_updates_and_deletes_absent_agents(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("keep-me", "old", mode=_DET, brain_setting="Little")
        db.save_agent("drop-me", "gone", mode=_DET, brain_setting="Big")
        conn = db._get_connection()
        try:
            db.apply_agent_repo_json_startup(
                conn,
                [
                    _agent_repo_row("keep-me", content="from-json", brain_setting="Medium", mode="Creative"),
                    _agent_repo_row("new-agent", content="fresh"),
                ],
            )
            conn.commit()
            kept = db.get_agent("keep-me")
            assert kept is not None
            assert kept["content"] == "from-json"
            assert kept["brain_setting"] == "Medium"
            assert kept["mode"] == "Creative"
            assert db.get_agent("drop-me") is None
            assert db.get_agent("new-agent")["mode"] == _DET
            listed = {row["agent_id"] for row in db.list_agents()}
            assert listed == {"keep-me", "new-agent"}
        finally:
            conn.close()

    def test_fetch_export_rows_use_repo_columns(self, sqlite_in_memory) -> None:
        from src.utils.config import REPO_ADMIN_JSON_CONFIG

        db = sqlite_in_memory
        db.save_agent("agent-a", "body", mode="Creative", brain_setting="Little", max_tokens=50)
        conn = db._get_connection()
        try:
            rows = db.fetch_agent_repo_json_export_rows(conn)
            assert len(rows) == 1
            assert set(rows[0].keys()) == set(REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"])
            assert rows[0]["agent_id"] == "agent-a"
            assert rows[0]["content"] == "body"
            assert rows[0]["mode"] == "Creative"
        finally:
            conn.close()

    def test_rejects_wrong_row_keys(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            with pytest.raises(ValueError, match="keys must be"):
                db.apply_agent_repo_json_startup(conn, [{"agent_id": "a", "content": "x"}])
        finally:
            conn.close()


class TestAst1878AgentModelField:
    """AST-1878: agent.model_id (LLM_MODEL_CONFIG key); brain size validated against that model's sizes.

    Branches: save insert with/without model; save update model-only / brain-only / neither; blank model;
    update_agent model/brain re-check + missing row + blank model; repo JSON model required / wrong size;
    _expose_agent_public SKU from model (None without model).
    """

    def test_save_with_model_exposes_catalog_sku(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", mode=_DET, brain_setting="Big", model_id=" kimi-k2.6 ")
        row = db.get_agent("a1")
        assert row["model_id"] == "kimi-k2.6"
        # AST-1948: model_code retired — resolved_model_key is the only SKU surface.
        assert row["resolved_model_key"] == "kimi-k2.6" and "model_code" not in row
        listed = {r["agent_id"]: r for r in db.list_agents()}
        assert listed["a1"]["model_id"] == "kimi-k2.6"
        assert listed["a1"]["resolved_model_key"] == "kimi-k2.6"

    def test_model_less_row_exposes_no_sku_and_uses_global_tiers(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", mode=_DET, brain_setting="Medium")
        row = db.get_agent("a1")
        assert row["model_id"] is None
        assert row["resolved_model_key"] is None
        with pytest.raises(ValueError, match="Invalid brain_setting 'Huge'"):
            db.save_agent("a2", "p", mode=_DET, brain_setting="Huge")

    def test_save_insert_rejects_size_model_lacks(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="Invalid brain_setting 'Medium' for model 'kimi-k2.6'"):
            sqlite_in_memory.save_agent("a1", "p", mode=_DET, brain_setting="Medium", model_id="kimi-k2.6")
        assert sqlite_in_memory.get_agent("a1") is None

    def test_save_rejects_blank_or_unknown_model(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="model_id must be non-empty"):
            sqlite_in_memory.save_agent("a1", "p", mode=_DET, brain_setting="Big", model_id="  ")
        with pytest.raises(ValueError, match="Unknown LLM model"):
            sqlite_in_memory.save_agent("a1", "p", mode=_DET, brain_setting="Big", model_id="__nope__")

    def test_save_update_rechecks_effective_pair(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", mode=_DET, brain_setting="Medium", model_id="claude")
        # Model-only change re-checks the stored size against the new model.
        with pytest.raises(ValueError, match="for model 'kimi-k2.6'"):
            db.save_agent("a1", "p2", mode=_DET, model_id="kimi-k2.6")
        db.save_agent("a1", "p2", mode=_DET, brain_setting="Big", model_id="kimi-k2.6")
        # Brain-only change checks against the stored model.
        with pytest.raises(ValueError, match="for model 'kimi-k2.6'"):
            db.save_agent("a1", "p3", mode=_DET, brain_setting="Medium")
        # Neither passed: content-only update, no check.
        db.save_agent("a1", "p4", mode=_DET)
        row = db.get_agent("a1")
        assert (row["content"], row["model_id"], row["brain_setting"]) == ("p4", "kimi-k2.6", "Big")

    def test_update_agent_model_and_brain_checks(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", mode=_DET, brain_setting="Little", model_id="deepseek-v4")
        assert db.update_agent("a1", model_id="kimi-k2.6") == 1
        with pytest.raises(ValueError, match="for model 'kimi-k2.6'"):
            db.update_agent("a1", brain_setting="Medium")
        with pytest.raises(ValueError, match="model_id must be non-empty"):
            db.update_agent("a1", model_id=" ")
        with pytest.raises(ValueError, match="model_id must be non-empty"):
            db.update_agent("a1", model_id=None)
        assert db.update_agent("missing", model_id="claude") == 0
        assert db.get_agent("a1")["model_id"] == "kimi-k2.6"

    def test_repo_json_requires_model_with_valid_size(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            with pytest.raises(ValueError, match="row 1: model_id required"):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a", model_id=None)])
            with pytest.raises(ValueError, match="row 1: model_id required"):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a", model_id="  ")])
            with pytest.raises(ValueError, match="row 2: Invalid brain_setting 'Medium' for model 'kimi-k2.6'"):
                db.apply_agent_repo_json_startup(
                    conn, [_agent_repo_row("a"), _agent_repo_row("b", model_id="kimi-k2.6")]
                )
            # Validation runs before any write.
            assert db.list_agents() == []
            db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a", model_id="kimi-k2.6", brain_setting="Big")])
            conn.commit()
        finally:
            conn.close()
        assert db.get_agent("a")["model_id"] == "kimi-k2.6"


class TestAst1948AgentModeColumn:
    """AST-1948 AC 2/3/7: mode persisted and validated on every write path; temperature / model_code dropped.

    Branches: schema ensure on the pre-1948 shape (drop old columns, add mode, keep row data, mode-less row
    still lists with its SKU); save_agent bad mode (insert + update, nothing written); update_agent mode
    valid / invalid / retired keys ignored; repo JSON bad / missing mode rejected before any write.
    """

    def test_schema_ensure_drops_retired_columns_and_adds_mode(self, sqlite_in_memory, monkeypatch) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            # Pre-AST-1948 table shape with a live row.
            conn.execute(
                "CREATE TABLE agent (agent_id TEXT PRIMARY KEY, content TEXT, model_id TEXT, brain_setting TEXT, "
                "model_code TEXT, temperature REAL, max_tokens INTEGER, updated_at TIMESTAMP)"
            )
            conn.execute(
                "INSERT INTO agent VALUES ('old', 'body', 'kimi-k2.6', 'Big', 'kimi-k2.6', 0.7, 50, '2026-01-01')"
            )
            conn.commit()
        finally:
            conn.close()
        monkeypatch.setattr(db, "_agent_schema_ensured", False)
        row = db.get_agent("old")
        conn = db._get_connection()
        try:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(agent)").fetchall()}
        finally:
            conn.close()
        assert "mode" in cols and not cols & {"temperature", "model_code"}
        # DDL only: data kept, no mode backfill (AST-1950 sets starting modes); SKU still resolves.
        assert (row["content"], row["max_tokens"], row["mode"]) == ("body", 50, None)
        assert row["resolved_model_key"] == "kimi-k2.6"
        assert {r["agent_id"] for r in db.list_agents()} == {"old"}

    def test_save_agent_rejects_unknown_mode(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match="Invalid mode 'Wild'"):
            db.save_agent("a1", "p", mode="Wild", brain_setting="Medium")
        assert db.get_agent("a1") is None
        db.save_agent("a1", "p", mode=_DET, brain_setting="Medium")
        with pytest.raises(ValueError, match="Invalid mode 'Wild'"):
            db.save_agent("a1", "p2", mode="Wild")
        assert (db.get_agent("a1")["content"], db.get_agent("a1")["mode"]) == ("p", _DET)

    def test_update_agent_mode_validated_and_retired_keys_ignored(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", mode=_DET, brain_setting="Medium")
        assert db.update_agent("a1", mode="Creative") == 1
        with pytest.raises(ValueError, match="Invalid mode 'Wild'"):
            db.update_agent("a1", mode="Wild")
        with pytest.raises(ValueError, match="Invalid mode None"):
            db.update_agent("a1", mode=None)
        # temperature / model_code are off the allow-list: nothing to write.
        assert db.update_agent("a1", temperature=0.9, model_code="x") == 0
        assert db.get_agent("a1")["mode"] == "Creative"

    def test_repo_json_rejects_bad_or_missing_mode(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            with pytest.raises(ValueError, match="row 2: Invalid mode 'Wild'"):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a"), _agent_repo_row("b", mode="Wild")])
            with pytest.raises(ValueError, match="row 1: Invalid mode None"):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a", mode=None)])
            # Old shape (temperature instead of mode) fails the key check.
            old = _agent_repo_row("a")
            del old["mode"]
            old["temperature"] = 0.2
            with pytest.raises(ValueError, match="keys must be"):
                db.apply_agent_repo_json_startup(conn, [old])
            assert db.list_agents() == []
        finally:
            conn.close()
