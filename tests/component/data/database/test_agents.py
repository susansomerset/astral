"""Component tests for agent table cluster (AST-392)."""

from __future__ import annotations

import json

import pytest

# AST-1955: brain_setting / mode retired; the row carries plain call settings (type-checked only).
_RETIRED = ("brain_setting", "mode", "model_code")


# Branches: insert defaults; update leaves None columns as is; delete; task refs.
class TestSaveAgent:
    def test_insert_and_update(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt", model_id="claude-sonnet-4-6", max_tokens=100, temperature=0.3)
        row = db.get_agent("agent-1")
        assert row is not None
        assert (row["content"], row["max_tokens"], row["temperature"]) == ("prompt", 100, 0.3)
        db.save_agent("agent-1", "prompt-2", reasoning_effort="high")
        row = db.get_agent("agent-1")
        assert row is not None
        # None on update leaves the stored value; passed values are written.
        assert (row["content"], row["temperature"], row["reasoning_effort"]) == ("prompt-2", 0.3, "high")
        db.save_agent("agent-1", "prompt-3", temperature=0.0)
        assert db.get_agent("agent-1")["temperature"] == 0.0
        # Retired columns never surface on the row.
        assert not set(_RETIRED) & set(db.get_agent("agent-1"))

    def test_insert_without_settings_defaults_fallbacks_true(self, sqlite_in_memory) -> None:
        # AST-1955: nothing is required on insert; new rows default provider_allow_fallbacks to True.
        sqlite_in_memory.save_agent("agent-new", "prompt")
        row = sqlite_in_memory.get_agent("agent-new")
        assert row["provider_allow_fallbacks"] is True
        assert [row[k] for k in ("quantization", "temperature", "reasoning_effort", "provider_only",
                                 "provider_ignore", "provider_sort")] == [None] * 6


class TestListAgents:
    def test_returns_saved_agents(self, sqlite_in_memory) -> None:
        sqlite_in_memory.save_agent("agent-1", "one", provider_only=["crusoe"])
        sqlite_in_memory.save_agent("agent-2", "two", provider_allow_fallbacks=False)
        rows = {row["agent_id"]: row for row in sqlite_in_memory.list_agents()}
        assert set(rows) == {"agent-1", "agent-2"}
        # Settings decoded to API types in the list view too.
        assert (rows["agent-1"]["provider_only"], rows["agent-2"]["provider_allow_fallbacks"]) == (["crusoe"], False)
        assert not set(_RETIRED) & set(rows["agent-1"])


class TestDeleteAgent:
    def test_deletes_existing_agent(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt")
        assert db.delete_agent("agent-1") is True
        assert db.get_agent("agent-1") is None


class TestCountAgentTaskRefs:
    def test_counts_task_rows(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("agent-1", "prompt")
        db.save_agent_task("qualify_job_listings", agent_id="agent-1", user_prompt="hi")
        assert db.count_agent_task_refs("agent-1") == 1


def _agent_repo_row(
    agent_id: str,
    *,
    content: str = "prompt",
    model_id: str | None = "claude-sonnet-4-6",
    max_tokens: int | None = 100,
    updated_at: str = "2026-06-24 00:00:00",
    **settings,
) -> dict:
    # AST-1955 repo JSON shape: model_id + max_tokens + seven plain settings; list settings are JSON-array text.
    row = {
        "agent_id": agent_id,
        "content": content,
        "model_id": model_id,
        "max_tokens": max_tokens,
        "quantization": None,
        "temperature": None,
        "reasoning_effort": None,
        "provider_allow_fallbacks": True,
        "provider_only": None,
        "provider_ignore": None,
        "provider_sort": None,
        "updated_at": updated_at,
    }
    row.update(settings)
    return row


# AST-782: repo-owned agent JSON startup upsert + export queries.
class TestAst782AgentRepoJsonStartup:
    def test_apply_upserts_updates_and_deletes_absent_agents(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("keep-me", "old", temperature=0.9)
        db.save_agent("drop-me", "gone")
        conn = db._get_connection()
        try:
            db.apply_agent_repo_json_startup(
                conn,
                [
                    _agent_repo_row("keep-me", content="from-json", temperature=0.2),
                    _agent_repo_row("new-agent", content="fresh", provider_only='["crusoe"]'),
                ],
            )
            conn.commit()
            kept = db.get_agent("keep-me")
            assert kept is not None
            assert (kept["content"], kept["temperature"]) == ("from-json", 0.2)
            assert db.get_agent("drop-me") is None
            assert db.get_agent("new-agent")["provider_only"] == ["crusoe"]
            listed = {row["agent_id"] for row in db.list_agents()}
            assert listed == {"keep-me", "new-agent"}
        finally:
            conn.close()

    def test_fetch_export_rows_use_repo_columns(self, sqlite_in_memory) -> None:
        from src.utils.config import REPO_ADMIN_JSON_CONFIG

        db = sqlite_in_memory
        db.save_agent("agent-a", "body", max_tokens=50, provider_only=["crusoe"], provider_allow_fallbacks=False)
        conn = db._get_connection()
        try:
            rows = db.fetch_agent_repo_json_export_rows(conn)
            assert len(rows) == 1
            assert set(rows[0].keys()) == set(REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"])
            assert rows[0]["agent_id"] == "agent-a"
            assert rows[0]["content"] == "body"
            # Export: bool stays bool (true/false in JSON); list settings stay JSON-array text (flat scalar).
            assert rows[0]["provider_allow_fallbacks"] is False
            assert rows[0]["provider_only"] == '["crusoe"]'
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
    """AST-1878: agent.model_id (LLM_MODEL_CONFIG key). AST-1955 kept the model check and retired the size check.

    Branches: save insert with/without model; blank / unknown model on save; update_agent model re-check +
    missing row + blank model; repo JSON model required; _expose_agent_public SKU from model (None without one).
    """

    def test_save_with_model_exposes_catalog_sku(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", model_id=" deepseek-v4-pro ")
        row = db.get_agent("a1")
        assert row["model_id"] == "deepseek-v4-pro"
        # AST-1948: model_code retired — resolved_model_key is the only SKU surface.
        assert row["resolved_model_key"] == "deepseek-v4-pro" and "model_code" not in row
        listed = {r["agent_id"]: r for r in db.list_agents()}
        assert listed["a1"]["model_id"] == "deepseek-v4-pro"
        assert listed["a1"]["resolved_model_key"] == "deepseek-v4-pro"

    def test_model_less_row_exposes_no_sku(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p")
        row = db.get_agent("a1")
        assert row["model_id"] is None
        assert row["resolved_model_key"] is None

    def test_save_rejects_blank_or_unknown_model(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="model_id must be non-empty"):
            sqlite_in_memory.save_agent("a1", "p", model_id="  ")
        # AST-1955: the retired pre-split ids are unknown to the catalog.
        for bad in ("__nope__", "claude", "deepseek-v4"):
            with pytest.raises(ValueError, match="Unknown LLM model"):
                sqlite_in_memory.save_agent("a1", "p", model_id=bad)
        assert sqlite_in_memory.get_agent("a1") is None

    def test_update_agent_model_checks(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", model_id="deepseek-v4-flash")
        assert db.update_agent("a1", model_id="kimi-k2.6") == 1
        with pytest.raises(ValueError, match="model_id must be non-empty"):
            db.update_agent("a1", model_id=" ")
        with pytest.raises(ValueError, match="model_id must be non-empty"):
            db.update_agent("a1", model_id=None)
        with pytest.raises(ValueError, match="Unknown LLM model"):
            db.update_agent("a1", model_id="claude")
        assert db.update_agent("missing", model_id="claude-opus-4-6") == 0
        assert db.get_agent("a1")["model_id"] == "kimi-k2.6"

    def test_repo_json_requires_known_model(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            with pytest.raises(ValueError, match="row 1: model_id must be non-empty"):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a", model_id=None)])
            with pytest.raises(ValueError, match="row 1: model_id must be non-empty"):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a", model_id="  ")])
            with pytest.raises(ValueError, match="row 2: Unknown LLM model 'claude'"):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a"), _agent_repo_row("b", model_id="claude")])
            # Validation runs before any write.
            assert db.list_agents() == []
            db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a", model_id="kimi-k2.6")])
            conn.commit()
        finally:
            conn.close()
        assert db.get_agent("a")["model_id"] == "kimi-k2.6"


class TestAst1955AgentSettings:
    """AST-1955: seven plain agent settings, type-checked only; brain_setting / mode leave every write path.

    Branches: _check_agent_setting None / right type / wrong type (str, number-not-bool, bool, list of str) on
    save_agent, update_agent and repo JSON (nothing written); list settings JSON-text in DB + seed, decoded on
    read; update_agent None clears; retired kwargs ignored; schema ensure on the pre-1955 shape (adds settings,
    keeps brain_setting / mode for AST-1958, drops model_code, no backfill); seed round-trip + revert (AC 8).
    """

    @pytest.mark.parametrize(
        ("kwargs", "match"),
        [
            ({"quantization": 8}, "quantization must be str"),
            ({"temperature": "0.2"}, "temperature must be int/float"),
            ({"temperature": True}, "temperature must be int/float"),
            ({"reasoning_effort": 1}, "reasoning_effort must be str"),
            ({"provider_allow_fallbacks": "yes"}, "provider_allow_fallbacks must be bool"),
            ({"provider_only": "crusoe"}, "provider_only must be list"),
            ({"provider_ignore": ["ok", 3]}, "provider_ignore must be list"),
            ({"provider_sort": ["price"]}, "provider_sort must be str"),
        ],
    )
    def test_wrong_type_rejected_on_every_write(self, sqlite_in_memory, kwargs: dict, match: str) -> None:
        db = sqlite_in_memory
        with pytest.raises(ValueError, match=match):
            db.save_agent("a1", "p", **kwargs)
        assert db.get_agent("a1") is None
        db.save_agent("a1", "p")
        with pytest.raises(ValueError, match=match):
            db.update_agent("a1", **kwargs)
        # List settings travel as JSON text in repo JSON (a non-JSON string fails decoding instead); the rest as-is.
        name, value = next(iter(kwargs.items()))
        repo_value = json.dumps(value) if name in ("provider_only", "provider_ignore") and isinstance(value, list) else value
        conn = db._get_connection()
        try:
            with pytest.raises(ValueError, match="agent repo JSON row 1: "):
                db.apply_agent_repo_json_startup(conn, [_agent_repo_row("a1", content="repo", **{name: repo_value})])
        finally:
            conn.close()
        assert db.get_agent("a1")["content"] == "p"

    def test_any_value_of_the_right_type_is_accepted(self, sqlite_in_memory) -> None:
        # No vocabulary list, no per-model check (Susan: "code it loosely").
        db = sqlite_in_memory
        db.save_agent("a1", "p", model_id="claude-haiku-4-5", quantization="anything", temperature=7,
                      reasoning_effort="whatever", provider_sort="nonsense", provider_ignore=[])
        row = db.get_agent("a1")
        assert (row["quantization"], row["temperature"], row["reasoning_effort"], row["provider_sort"]) == (
            "anything", 7, "whatever", "nonsense")
        assert row["provider_ignore"] == []

    def test_update_agent_sets_clears_and_ignores_retired_keys(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_agent("a1", "p", temperature=0.6, provider_only=["crusoe"])
        assert db.update_agent("a1", quantization="bf16", provider_only=None, provider_allow_fallbacks=False) == 1
        row = db.get_agent("a1")
        assert (row["quantization"], row["provider_only"], row["provider_allow_fallbacks"], row["temperature"]) == (
            "bf16", None, False, 0.6)
        # brain_setting / mode / model_code are off the allow-list: nothing to write.
        assert db.update_agent("a1", brain_setting="Big", mode="Creative", model_code="x") == 0

    def test_retired_kwargs_rejected_by_save_agent(self, sqlite_in_memory) -> None:
        for kw in ("brain_setting", "mode"):
            with pytest.raises(TypeError):
                sqlite_in_memory.save_agent("a1", "p", **{kw: "x"})

    def test_schema_ensure_on_pre_1955_table(self, sqlite_in_memory, monkeypatch) -> None:
        db = sqlite_in_memory
        conn = db._get_connection()
        try:
            # Pre-AST-1955 live shape (AST-1948 + a leftover model_code) with a row on a retired model id.
            conn.execute(
                "CREATE TABLE agent (agent_id TEXT PRIMARY KEY, content TEXT, model_id TEXT, brain_setting TEXT, "
                "mode TEXT, model_code TEXT, max_tokens INTEGER, updated_at TIMESTAMP)"
            )
            conn.execute("INSERT INTO agent VALUES ('old', 'body', 'claude', 'Medium', 'Deterministic', 'x', 50, '2026-01-01')")
            conn.commit()
        finally:
            conn.close()
        monkeypatch.setattr(db, "_agent_schema_ensured", False)
        row = db.get_agent("old")
        conn = db._get_connection()
        try:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(agent)").fetchall()}
            legacy = conn.execute("SELECT brain_setting, mode FROM agent WHERE agent_id = 'old'").fetchone()
        finally:
            conn.close()
        settings = {"quantization", "temperature", "reasoning_effort", "provider_allow_fallbacks",
                    "provider_only", "provider_ignore", "provider_sort"}
        assert settings <= cols and "model_code" not in cols
        # DDL only: brain_setting / mode stay for the AST-1958 migration to read, with their data.
        assert {"brain_setting", "mode"} <= cols and tuple(legacy) == ("Medium", "Deterministic")
        # No backfill (fallbacks stays NULL until the seed / AST-1958 sets it); retired columns never reach the API.
        assert (row["content"], row["max_tokens"], row["provider_allow_fallbacks"]) == ("body", 50, None)
        assert not {"brain_setting", "mode"} & set(row)
        # A retired model id still lists (no SKU) instead of blanking Manage Agents before AST-1958 runs.
        assert row["resolved_model_key"] is None
        assert [(r["agent_id"], r["resolved_model_key"]) for r in db.list_agents()] == [("old", None)]

    def test_seed_round_trips_and_revert_restores_it(self, sqlite_in_memory) -> None:
        # AC 8: the checked-in seed validates, applies, exports back equal, and Revert-to-file restores it.
        from src.core import repo_admin_json as repo_json_mod

        db = sqlite_in_memory
        seed = repo_json_mod.load_repo_admin_json_file("agent")
        conn = db._get_connection()
        try:
            db.apply_agent_repo_json_startup(conn, seed)
            conn.commit()
            assert db.fetch_agent_repo_json_export_rows(conn) == sorted(seed, key=lambda r: r["agent_id"])
        finally:
            conn.close()
        db.update_agent("job_analyst_grace", temperature=0.9, provider_sort="price")
        assert repo_json_mod.get_repo_admin_json_divergence_status()["agent"]["diverged"] is True
        assert repo_json_mod.revert_repo_admin_json_table("agent") == len(seed)
        grace = db.get_agent("job_analyst_grace")
        assert (grace["temperature"], grace["provider_sort"], grace["model_id"]) == (0.2, None, "deepseek-v4-pro")
        assert repo_json_mod.get_repo_admin_json_divergence_status()["agent"]["diverged"] is False
