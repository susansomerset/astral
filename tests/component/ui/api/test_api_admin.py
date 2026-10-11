"""Component tests for src/ui/api/api_admin.py (AST-394)."""

from __future__ import annotations

import io
import json
import threading
import zlib
from typing import Any
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.core import dispatcher as dispatcher_mod
from src.utils import config as cfg
from ui.api import api_admin as admin_mod


# Branches: config; agent list/get pass-through; /agents/models flat per-SKU catalog (AST-1957); brain_settings retired;
# create needs agent_id + model_id; settings pass as sent, retired keys ignored; data-layer ValueError → 400; delete.
class TestAdminConfigAndAgents:
    def test_admin_config(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = admin_client.get("/api/admin/config", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), dict)

    def test_list_agents_and_ids(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1880: rows go out as the data layer exposes them (AST-1955: decoded settings), no admin-side shaping.
        row = {"agent_id": "a1", "model_id": "kimi-k2.6", "temperature": 0.6, "provider_only": ["groq"]}
        monkeypatch.setattr(admin_mod.database, "list_agents", lambda: [dict(row)])
        assert admin_client.get("/api/admin/agents", headers=auth_headers).get_json() == [row]
        assert admin_client.get("/api/admin/agents/ids", headers=auth_headers).get_json() == ["a1"]

    def test_list_models_is_flat_catalog_with_default_output_budget(
        self, admin_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        # AST-1957: id → label, server and the model's own default output budget; no brain sizes; `order` keeps catalog order.
        resp = admin_client.get("/api/admin/agents/models", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert list(cfg.LLM_MODEL_CONFIG) == sorted(body, key=lambda mid: body[mid]["order"])
        for i, (mid, m) in enumerate(cfg.LLM_MODEL_CONFIG.items()):
            assert body[mid] == {
                "order": i,
                "label": m["label"],
                "server_id": m["server"],
                "server_label": cfg.LLM_SERVER_CONFIG[m["server"]]["label"],
                "default_max_tokens": m["default_max_tokens"],
            }

    def test_brain_settings_route_and_admin_view_retired(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1880: global tier catalog gone; the path now falls through to GET /agents/<agent_id>.
        seen: list = []
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: seen.append(agent_id))
        assert admin_client.get("/api/admin/agents/brain_settings", headers=auth_headers).status_code == 404
        assert seen == ["brain_settings"]
        assert not hasattr(admin_mod, "list_brain_settings")
        assert not hasattr(admin_mod, "_agent_admin_view")

    def test_get_agent_missing_and_found(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        assert admin_client.get("/api/admin/agents/missing", headers=auth_headers).status_code == 404
        monkeypatch.setattr(
            admin_mod.database, "get_agent",
            lambda agent_id: {"agent_id": agent_id, "model_id": "claude-sonnet-4-6", "temperature": 0.2},
        )
        assert admin_client.get("/api/admin/agents/a1", headers=auth_headers).get_json() == {
            "agent_id": "a1", "model_id": "claude-sonnet-4-6", "temperature": 0.2,
        }

    @pytest.mark.parametrize(
        "body",
        [
            {},
            {"model_id": "claude-haiku-4-5"},
            {"agent_id": "a1"},
            {"agent_id": "a1", "model_id": "  "},
            # legacy shape: model_code alone names no model
            {"agent_id": "a1", "model_code": "claude-haiku-4-5"},
            # AST-1957: retired keys never stand in for a model
            {"agent_id": "a1", "brain_setting": "Big", "mode": "Creative"},
        ],
        ids=["empty", "no_agent_id", "no_model_id", "blank_model_id", "legacy_model_code", "retired_keys_only"],
    )
    def test_create_agent_requires_id_and_model(
        self, body, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(admin_mod.database, "save_agent", save)
        resp = admin_client.post("/api/admin/agents", json=body, headers=auth_headers)
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "agent_id and model_id are required"
        save.assert_not_called()

    def test_create_agent_conflict_success_and_data_layer_rejection(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1957: settings present in the body pass as sent (no strip, no checks); absent ones are not passed;
        # brain_setting / mode / model_code are ignored like any unknown key.
        good = {
            "agent_id": " a1 ", "content": "sys", "model_id": " kimi-k2.6 ", "max_tokens": 100,
            "temperature": 0.2, "reasoning_effort": " high ", "quantization": None,
            "provider_allow_fallbacks": False, "provider_only": ["groq"],
            "brain_setting": "Big", "mode": "Creative", "model_code": "x",
        }
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id})
        assert admin_client.post("/api/admin/agents", json=good, headers=auth_headers).status_code == 409
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        save = MagicMock()
        monkeypatch.setattr(admin_mod.database, "save_agent", save)
        created = admin_client.post("/api/admin/agents", json=good, headers=auth_headers)
        assert (created.status_code, created.get_json()) == (201, {"created": "a1"})
        save.assert_called_once_with(
            "a1", "sys", model_id="kimi-k2.6", max_tokens=100, temperature=0.2, reasoning_effort=" high ",
            quantization=None, provider_allow_fallbacks=False, provider_only=["groq"],
        )
        monkeypatch.setattr(admin_mod.database, "save_agent", MagicMock(side_effect=ValueError("temperature must be a number")))
        bad = admin_client.post("/api/admin/agents", json=good, headers=auth_headers)
        assert (bad.status_code, bad.get_json()) == (400, {"error": "temperature must be a number"})

    def test_update_agent_fields_strip_and_errors(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        assert admin_client.put("/api/admin/agents/a1", json={"content": "x"}, headers=auth_headers).status_code == 404
        stored = {"agent_id": "a1", "model_id": "claude-sonnet-4-6", "temperature": 0.2}
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: dict(stored))
        update = MagicMock()
        monkeypatch.setattr(admin_mod.database, "update_agent", update)
        # Retired / unknown keys alone leave nothing to update.
        for body in ({}, {"model_code": "claude-opus-4-6"}, {"brain_setting": "Big", "mode": "Creative"}):
            resp = admin_client.put("/api/admin/agents/a1", json=body, headers=auth_headers)
            assert (resp.status_code, resp.get_json()) == (400, {"error": "No updatable fields provided"}), body
        update.assert_not_called()
        # AST-1957: mode is no longer required — a content-only PUT goes through.
        resp = admin_client.put("/api/admin/agents/a1", json={"content": "x"}, headers=auth_headers)
        assert (resp.status_code, resp.get_json()) == (200, stored)
        update.assert_called_once_with("a1", content="x")
        update.reset_mock()
        resp = admin_client.put(
            "/api/admin/agents/a1",
            json={
                "content": " keep ", "model_id": " deepseek-v4-pro ", "max_tokens": 9,
                "quantization": "fp8", "temperature": 0.3, "reasoning_effort": "none", "provider_allow_fallbacks": True,
                "provider_only": None, "provider_ignore": ["x"], "provider_sort": "price",
                "brain_setting": "Medium", "mode": "Creative", "model_code": "x",
            },
            headers=auth_headers,
        )
        assert (resp.status_code, resp.get_json()) == (200, stored)
        # model_id stripped; settings as sent (None clears in the data layer); retired keys not forwarded.
        update.assert_called_once_with(
            "a1", content=" keep ", model_id="deepseek-v4-pro", max_tokens=9, quantization="fp8", temperature=0.3,
            reasoning_effort="none", provider_allow_fallbacks=True, provider_only=None, provider_ignore=["x"],
            provider_sort="price",
        )
        monkeypatch.setattr(admin_mod.database, "update_agent", MagicMock(side_effect=ValueError("provider_only must be a list")))
        bad = admin_client.put("/api/admin/agents/a1", json={"provider_only": "groq"}, headers=auth_headers)
        assert (bad.status_code, bad.get_json()) == (400, {"error": "provider_only must be a list"})

    def test_ast1957_settings_round_trip_and_wrong_types_rejected(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], sqlite_in_memory
    ) -> None:
        # AST-1957 against the real data layer (AST-1955 type checks): create → read → clear; wrong type → 400, row unchanged.
        db = sqlite_in_memory
        created = admin_client.post(
            "/api/admin/agents",
            json={
                "agent_id": "s_agent", "content": "sys", "model_id": "qwen/qwen3-32b",
                "temperature": 0.2, "provider_only": ["groq"], "brain_setting": "Big", "mode": "Creative",
            },
            headers=auth_headers,
        )
        assert created.status_code == 201
        got = admin_client.get("/api/admin/agents/s_agent", headers=auth_headers).get_json()
        # New row: fallbacks default true; unsent settings empty; no retired keys on the row.
        assert {k: got[k] for k in ("model_id", "temperature", "provider_only", "provider_allow_fallbacks", "quantization")} == {
            "model_id": "qwen/qwen3-32b", "temperature": 0.2, "provider_only": ["groq"],
            "provider_allow_fallbacks": True, "quantization": None,
        }
        assert not {"brain_setting", "mode"} & set(got)
        before = db.get_agent("s_agent")
        for body in ({"temperature": "warm"}, {"provider_only": "groq"}, {"provider_allow_fallbacks": "yes"}, {"model_id": "claude"}):
            bad = admin_client.put("/api/admin/agents/s_agent", json=body, headers=auth_headers)
            assert bad.status_code == 400 and bad.get_json()["error"], body
            assert db.get_agent("s_agent") == before, body
        ok = admin_client.put(
            "/api/admin/agents/s_agent",
            json={"temperature": None, "provider_only": None, "provider_allow_fallbacks": False, "reasoning_effort": "high"},
            headers=auth_headers,
        )
        assert ok.status_code == 200
        reread = admin_client.get("/api/admin/agents/s_agent", headers=auth_headers).get_json()
        for body in (ok.get_json(), reread):
            assert (body["temperature"], body["provider_only"], body["provider_allow_fallbacks"], body["reasoning_effort"]) == (
                None, None, False, "high",
            )
        post = admin_client.post(
            "/api/admin/agents",
            json={"agent_id": "bad", "content": "", "model_id": "claude-haiku-4-5", "temperature": "hot"},
            headers=auth_headers,
        )
        assert post.status_code == 400 and post.get_json()["error"]
        assert db.get_agent("bad") is None

    def test_models_route_lists_whole_catalog(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        # AST-1947 + AST-1955: 101 models — per-SKU direct ids; claude / deepseek-v4 and kimi-k2.6-openrouter retired.
        body = admin_client.get("/api/admin/agents/models", headers=auth_headers).get_json()
        assert len(body) == len(cfg.LLM_MODEL_CONFIG) == 101
        assert body["qwen/qwen3-32b"]["server_id"] == "openrouter"
        assert body["moonshotai/kimi-k2.6"]["server_id"] == "openrouter"
        assert body["claude-sonnet-4-6"]["server_id"] == "anthropic"
        assert not {"claude", "deepseek-v4", "kimi-k2.6-openrouter"} & set(body)

    def test_delete_agent_paths(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        assert admin_client.delete("/api/admin/agents/a1", headers=auth_headers).status_code == 404
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id})
        monkeypatch.setattr(admin_mod.database, "count_agent_task_refs", lambda agent_id: 2)
        assert admin_client.delete("/api/admin/agents/a1", headers=auth_headers).status_code == 409
        monkeypatch.setattr(admin_mod.database, "count_agent_task_refs", lambda agent_id: 0)
        delete = MagicMock()
        monkeypatch.setattr(admin_mod.database, "delete_agent", delete)
        ok = admin_client.delete("/api/admin/agents/a1", headers=auth_headers)
        assert ok.status_code == 200
        delete.assert_called_once()

    def test_ast632_manage_agents_token_meta_and_preview(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-632: GET /agents/meta/tokens; POST /agents/preview with candidate resolution."""
        meta = admin_client.get("/api/admin/agents/meta/tokens", headers=auth_headers)
        assert meta.status_code == 200
        tokens = meta.get_json()
        assert tokens == cfg.get_manage_agents_tokens()
        assert "SELECTED_AGENT" not in tokens

        assert admin_client.post("/api/admin/agents/preview", json={}, headers=auth_headers).status_code == 400

        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda cid: None)
        bad_cand = admin_client.post(
            "/api/admin/agents/preview",
            json={"content": "hi", "candidate_id": "missing"},
            headers=auth_headers,
        )
        assert bad_cand.status_code == 400
        assert "not found" in bad_cand.get_json()["error"].lower()

        monkeypatch.setattr(admin_mod.database, "list_candidates", lambda: [])
        no_cands = admin_client.post("/api/admin/agents/preview", json={"content": "hi"}, headers=auth_headers)
        assert no_cands.status_code == 400

        monkeypatch.setattr(
            admin_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {"profile": {"first": "Ada"}}},
        )
        monkeypatch.setattr(
            admin_mod,
            "resolved_agent_content",
            lambda agent_row, cd, task_key, job_context=None: "resolved Ada",
        )
        ok = admin_client.post(
            "/api/admin/agents/preview",
            json={"content": "{$FIRST_NAME}", "candidate_id": "c1"},
            headers=auth_headers,
        )
        assert ok.status_code == 200
        body = ok.get_json()
        assert body["candidate_id"] == "c1"
        assert body["content"] == "resolved Ada"

        monkeypatch.setattr(
            admin_mod.database,
            "list_candidates",
            lambda: [{"astral_candidate_id": "c0", "candidate_data": {"profile": {"first": "Z"}}}],
        )
        fallback = admin_client.post("/api/admin/agents/preview", json={"content": "x"}, headers=auth_headers)
        assert fallback.get_json()["candidate_id"] == "c0"


# Branches: enrich rows with/without candidate, agent, task, cache, and timesheet averages.
class TestEnrichTasks:
    def test_enrich_tasks_covers_agent_and_cache_branches(self, monkeypatch: pytest.MonkeyPatch) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = (12.5, 3.0)
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [
                {
                    "task_key": "craft_resume_base",
                    "task_key_uuid": "uuid-1",
                    "agent_id": "agent-1",
                    "cache_prompt_len": 80,
                    "nocache_prompt_len": 40,
                    "run_next": "next",
                    "updated_at": "now",
                },
                {"task_key": "", "task_key_uuid": None, "agent_id": "", "cache_prompt_len": 0, "nocache_prompt_len": 0},
            ],
        )
        monkeypatch.setattr(
            admin_mod.database,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"name": "Susan"}},
        )
        # AST-1855: hydrated loader (AST-1854) reads artifacts — keep it off the repo DB.
        monkeypatch.setattr(admin_mod.database, "get_current_artifact", lambda *a: None)
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {
                "cache_prompt": "cache {$name}",
                "system_prompt": "override",
                "task_key_uuid": "uuid-1",
            }
            if task_key
            else None,
        )
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {
                "model_id": "claude-sonnet-4-6",
                "temperature": 0.2,
                "content": "agent {$name}",
                "max_tokens": 10,
            }
            if agent_id
            else None,
        )
        monkeypatch.setattr(admin_mod, "resolved_task_system", lambda *args, **kwargs: "resolved-system" * 20000)
        monkeypatch.setattr(
            admin_mod,
            "resolve_tokens",
            lambda text, *args, **kwargs: text.replace("{$name}", "Susan" * 20000),
        )
        rows = admin_mod._enrich_tasks("cand-1")
        # AST-1880 / AST-1957: SKU + cache threshold from the agent's own model via resolve_agent_settings.
        route = cfg.resolve_agent_settings("claude-sonnet-4-6", {"temperature": 0.2})
        assert (rows[0]["resolved_model_key"], rows[0]["model_code"]) == (route["sku"], route["sku"])
        # AST-1957: the task row no longer carries a brain size.
        assert "brain_setting" not in rows[0]
        assert rows[0]["cache_min_tokens"] == route["pricing"]["cache_min_tokens"] > 0
        assert rows[0]["cache_satisfied"] is True
        assert rows[0]["parsed_cache_tokens"] is not None
        assert rows[1]["system_prompt_tokens"] == 0

    def test_enrich_tasks_without_candidate_and_unresolved_cache(self, monkeypatch: pytest.MonkeyPatch) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": "craft_resume_base", "task_key_uuid": "uuid-2", "agent_id": "agent-1", "cache_prompt_len": 0, "nocache_prompt_len": 0}],
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {"cache_prompt": "{$missing}", "system_prompt": None},
        )
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {"model_code": "claude-haiku-4-5", "content": "only-agent"},
        )
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text)
        rows = admin_mod._enrich_tasks("")
        assert rows[0]["task_ready"] is False
        assert rows[0]["parsed_cache_tokens"] is None
        conn.close.assert_called_once()

    @staticmethod
    def _one_agent_row(monkeypatch: pytest.MonkeyPatch, agent: dict) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": "craft_resume_base", "task_key_uuid": None, "agent_id": "a1", "cache_prompt_len": 0, "nocache_prompt_len": 0}],
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: None)
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id, "content": "body", **agent})
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text or "")

    def test_enrich_tasks_uses_catalog_pricing_for_agent_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1880: a DeepSeek agent resolves its own SKU (no global provider switch); AST-1955 per-SKU id.
        self._one_agent_row(monkeypatch, {"model_id": "deepseek-v4-flash", "temperature": 0.6})
        route = cfg.resolve_agent_settings("deepseek-v4-flash", {})
        row = admin_mod._enrich_tasks("")[0]
        assert row["resolved_model_key"] == "deepseek-v4-flash"
        assert "brain_setting" not in row
        assert row["cache_min_tokens"] == route["pricing"].get("cache_min_tokens", 0)

    @pytest.mark.parametrize(
        "agent",
        [
            # AST-1955: pre-migration direct ids (AST-1958 moves live rows) blank the row, not 500.
            {"model_id": "claude"},
            {"model_id": "__no_model__"},
            {},
        ],
        ids=["retired_direct_id", "unknown_model", "no_model_id"],
    )
    def test_enrich_tasks_unroutable_agent_leaves_row_blank_and_warns(
        self, agent: dict, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Display row only: one misconfigured agent must not 500 the task manager.
        self._one_agent_row(monkeypatch, agent)
        with caplog.at_level("WARNING"):
            row = admin_mod._enrich_tasks("")[0]
        assert (row["resolved_model_key"], row["cache_min_tokens"], row["cache_satisfied"]) == ("", 0, False)
        assert "task manager craft_resume_base agent a1 has no routable model" in caplog.text


# Branches: task routes, preview errors, and update validation.
class TestTaskRoutes:
    def test_list_tasks_and_tokens(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "_enrich_tasks", lambda candidate_id: [{"task_key": "t1"}])
        assert admin_client.get("/api/admin/tasks?candidate_id=c1", headers=auth_headers).get_json()[0]["task_key"] == "t1"
        assert isinstance(admin_client.get("/api/admin/tasks/meta/tokens", headers=auth_headers).get_json(), list)
        # Branch lock: /tasks/meta/chain_tokens (§LOCKED api_admin) — was unexercised vs full component run.
        assert isinstance(
            admin_client.get("/api/admin/tasks/meta/chain_tokens", headers=auth_headers).get_json(),
            list,
        )

    def test_preview_task_and_get_update(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "preview_task_prompt", MagicMock(side_effect=ValueError("bad preview")))
        assert admin_client.get("/api/admin/tasks/t1/preview", headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod, "preview_task_prompt", MagicMock(return_value={"ok": True}))
        assert admin_client.get("/api/admin/tasks/t1/preview?candidate_id=c1", headers=auth_headers).get_json()["ok"] is True
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: None)
        assert admin_client.get("/api/admin/tasks/missing", headers=auth_headers).status_code == 404
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {
                "task_key": task_key,
                "task_group_name": "A. Candidate Context",
                "task_group_order": "A. Candidate Context",
                "task_seq": 1.0,
                "task_name": task_key,
            },
        )
        got = admin_client.get("/api/admin/tasks/craft_resume_base", headers=auth_headers)
        body = got.get_json()
        assert body["task_group_name"] == "A. Candidate Context"
        assert "phase" not in body
        assert "seq" not in body
        monkeypatch.setattr(admin_mod.database, "save_agent_task", MagicMock(side_effect=ValueError("bad save")))
        assert admin_client.put("/api/admin/tasks/t1", json={"run_next": "x"}, headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod.database, "save_agent_task", MagicMock())
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: {"task_key": task_key, "run_next": "x"})
        assert admin_client.put("/api/admin/tasks/t1", json={"system_prompt": "sp"}, headers=auth_headers).status_code == 200

    def test_preview_task_chain_ctx_override_parsing(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        """Hit preview_task's chain_ctx_* loop: empty key suffix is skipped; named keys become overrides (AST-455)."""
        captured: dict = {}

        def _capture(task_key: str, candidate_id: str, **kwargs: Any) -> dict:  # type: ignore[name-defined]
            captured["kwargs"] = kwargs
            return {"ok": True}

        monkeypatch.setattr(admin_mod, "preview_task_prompt", _capture)
        admin_client.get(
            "/api/admin/tasks/t_nested/preview?chain_ctx_=skipped&chain_ctx_CALLER_RESPONSE=z",
            headers=auth_headers,
        )
        kw = captured.get("kwargs") or {}
        assert kw.get("chain_overrides") == {"CALLER_RESPONSE": "z"}

    def test_preview_task_forwards_astral_job_id(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict = {}

        def _capture(task_key: str, candidate_id: str = "", **kwargs: Any) -> dict:  # type: ignore[name-defined]
            captured.update(kwargs)
            return {"ok": True}

        monkeypatch.setattr(admin_mod, "preview_task_prompt", _capture)
        admin_client.get(
            "/api/admin/tasks/contemplate_job/preview?candidate_id=c1&astral_job_id=job-513",
            headers=auth_headers,
        )
        assert captured.get("astral_job_id") == "job-513"


# AST-738: Manage Tasks grouping metadata from DB (not TASK_CONFIG phase/seq).
class TestAst738TaskGroupingApi:
    def test_grouping_from_agent_task_row_db_fields_only(self) -> None:
        out = admin_mod._grouping_from_agent_task_row(
            {
                "task_group_order": "B. Phase",
                "task_group_name": "B. Phase",
                "task_seq": 2.0,
                "task_name": "Label",
            },
            "some_key",
        )
        assert out["task_group_name"] == "B. Phase"
        assert out["task_seq"] == 2.0
        assert out["task_name"] == "Label"
        assert "phase" not in out
        assert "seq" not in out

    def test_get_task_surfaces_db_grouping(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {
                "task_key": task_key,
                "task_group_order": "Z",
                "task_group_name": "Z",
                "task_seq": 5.0,
                "task_name": "Display",
            },
        )
        body = admin_client.get("/api/admin/tasks/t1", headers=auth_headers).get_json()
        assert body["task_group_name"] == "Z"
        assert body["task_seq"] == 5.0
        assert "phase" not in body
        assert "seq" not in body

    def test_update_task_persists_grouping_fields(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saved: dict = {}

        def _save(task_key: str, **kwargs: Any) -> None:
            saved.update(kwargs)

        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: {"task_key": task_key})
        monkeypatch.setattr(admin_mod.database, "save_agent_task", _save)
        resp = admin_client.put(
            "/api/admin/tasks/t1",
            json={
                "task_group_order": "G1",
                "task_group_name": "Group One",
                "task_seq": 7.5,
                "task_name": "Friendly",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert saved["task_group_order"] == "G1"
        assert saved["task_group_name"] == "Group One"
        assert saved["task_seq"] == 7.5
        assert saved["task_name"] == "Friendly"

    def test_update_task_invalid_task_seq_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: {"task_key": task_key})
        resp = admin_client.put("/api/admin/tasks/t1", json={"task_seq": "not-a-number"}, headers=auth_headers)
        assert resp.status_code == 400
        assert "task_seq" in resp.get_json()["error"]


# AST-740: backward-compat phase/seq keys removed from Manage Tasks API payloads.
class TestAst740NoConfigPhaseSeqInApi:
    def test_get_task_payload_has_grouping_without_phase_seq(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {
                "task_key": task_key,
                "task_group_order": "G",
                "task_group_name": "G",
                "task_seq": 1.0,
                "task_name": "Label",
            },
        )
        body = admin_client.get("/api/admin/tasks/t1", headers=auth_headers).get_json()
        assert set(body.keys()) & {"phase", "seq"} == set()
        assert body["task_group_name"] == "G"


# AST-739: dispatch task_keys returns DB grouping metadata (not config phase/seq).
class TestAst739DispatchTaskKeysGrouping:
    def test_dispatch_task_keys_grouping_from_agent_task_row(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {
                "task_group_order": "Z-order",
                "task_group_name": "Z-name",
                "task_seq": 4.5,
                "task_name": "Pretty",
            }
            if task_key == "grade_do"
            else None,
        )
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["grade_do"]["task_group_name"] == "Z-name"
        assert keys["grade_do"]["task_group_order"] == "Z-order"
        assert keys["grade_do"]["task_seq"] == 4.5
        assert keys["grade_do"]["task_name"] == "Pretty"
        assert "phase" not in keys["grade_do"]
        assert "seq" not in keys["grade_do"]

    def test_dispatch_task_keys_orphan_empty_grouping(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [{"task_key": "orphan_only", "entity_type": "job", "trigger_state": "NEW"}],
        )
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["orphan_only"]["task_group_order"] == ""
        assert keys["orphan_only"]["task_group_name"] == ""
        assert keys["orphan_only"]["task_seq"] is None
        assert keys["orphan_only"]["task_name"] == ""


# AST-1675 / AST-825: lasting catalog key prefilter_company carries agent_task grouping meta.
class TestAst825PrefilterDispatchTaskKeysGrouping:
    def test_dispatch_task_keys_prefilter_grouping_from_prefilter_company_catalog(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {
                "task_group_order": "3000",
                "task_group_name": "Company Roster",
                "task_seq": 5.0,
                "task_name": "Prefilter Company",
            }
            if task_key == "prefilter_company"
            else None,
        )
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        pf = keys["prefilter_company"]
        assert pf["task_group_name"] == "Company Roster"
        assert pf["task_group_order"] == "3000"
        assert pf["task_seq"] == 5.0
        assert pf["task_name"] == "Prefilter Company"
        assert pf["entity_type"] == "company"
        assert pf["trigger_state"] == "HOMEPAGE_READY"
        assert "prefilter" not in keys


# AST-749: retired consult_* absent from task_keys even when list_dispatch_tasks returns legacy rows.
class TestAst749DispatchTaskKeysRetiredFilter:
    def test_dispatch_task_keys_excludes_retired_consult_keys(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {"task_key": "consult_do", "entity_type": "job", "trigger_state": "PASSED_JD"},
                {"task_key": "consult_get", "entity_type": "job", "trigger_state": "PASSED_DO"},
                {"task_key": "grade_do", "entity_type": "", "trigger_state": ""},
            ],
        )
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert "consult_do" not in keys
        assert "consult_get" not in keys
        assert "consult_like" not in keys
        assert "grade_do" in keys
        assert keys["grade_do"]["entity_type"] == "job"
        assert keys["grade_do"]["trigger_state"] == "PASSED_JD"


# AST-2025 AC6: fetch_relative_jd (agent_task catalog) in the Scheduled Actions picker as job / RELATIVE_JOB_LINK.
class TestAst2025FetchRelativeJdDispatchTaskKey:
    def test_picker_lists_fetch_relative_jd_job_relative_job_link(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", list)
        monkeypatch.setattr(admin_mod.database, "list_candidate_tasks", lambda: [{"task_key": "fetch_relative_jd"}])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["fetch_relative_jd"]["entity_type"] == "job"
        assert keys["fetch_relative_jd"]["trigger_state"] == "RELATIVE_JOB_LINK"


# AST-796 / AST-960 / AST-1214: fetch_jd gazer hop; retired still excluded; live agent_task union in picker.
_AST1214_AGENT_TASK_ONLY_KEYS = (
    "fetch_culture_pages",
    "fetch_jd",
    "fetch_job_pages",
    "fetch_website",
    "gaze",
    "inflow_discovery",
    "parse_meteorite_email",
    "recheck_no_openings",
)


class TestAst796FetchJdRetiredDispatchKeys:
    def test_dispatch_task_keys_includes_agent_task_union_excludes_retired(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1214: agent_task-only keys join the picker via live catalog (not frozenset); retired stay out.
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": tk} for tk in _AST1214_AGENT_TASK_ONLY_KEYS],
        )
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        for tk in _AST1214_AGENT_TASK_ONLY_KEYS:
            assert tk in keys
        assert "grade_do" in keys
        for retired in ("scrape_jd", "validate_title", "gaze_board"):
            assert retired not in keys

    def test_dispatch_task_keys_includes_fetch_jd_from_db_row(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "task_key": "fetch_jd",
                    "entity_type": "job",
                    "trigger_state": "PASSED_JOBLIST",
                }
            ],
        )
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert "fetch_jd" in keys
        assert keys["fetch_jd"]["entity_type"] == "job"
        assert keys["fetch_jd"]["trigger_state"] == "PASSED_JOBLIST"

    def test_create_dispatch_task_rejects_retired_scrape_jd(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "scrape_jd",
                "trigger_state": "PASSED_JOBLIST",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        err = resp.get_json()["error"]
        assert "retired" in err
        assert "fetch_jd" in err

    def test_create_dispatch_task_rejects_retired_validate_title(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "validate_title",
                "trigger_state": "NEW",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        err = resp.get_json()["error"]
        assert "retired" in err
        assert "inline" in err

    def test_create_dispatch_task_rejects_retired_gaze_board(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "gaze_board",
                "trigger_state": "ACTIVE",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        err = resp.get_json()["error"]
        assert "retired" in err
        assert "decommissioned" in err


# AST-781: legacy board_search entity_type rows do not 500 list_dtasks enrichment.
class TestAst781ListDtasksRetiredEntityType:
    def test_list_dtasks_legacy_board_search_row_returns_zero_available_count(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "id": 99,
                    "task_key": "gaze_board",
                    "trigger_state": "ACTIVE",
                    "entity_type": "board_search",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
            ],
        )
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        resp = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers)
        assert resp.status_code == 200
        rows = resp.get_json()
        assert len(rows) == 1
        assert rows[0]["task_key"] == "gaze_board"
        assert rows[0]["entity_type"] == "board_search"
        assert rows[0]["available_count"] == 0


# AST-785: list_dtasks filters retired keys; enrichment errors do not 500 the list.
class TestAst785ListDtasksRobustness:
    def test_list_dtasks_omits_retired_task_keys(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "id": 1,
                    "task_key": "consult_do",
                    "trigger_state": "PASSED_JD",
                    "entity_type": "job",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
                {
                    "id": 2,
                    "task_key": "vet_inflow_discovery",
                    "trigger_state": "NEW",
                    "entity_type": "company",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
                {
                    "id": 3,
                    "task_key": "scan_jobs",
                    "trigger_state": "NEW",
                    "entity_type": "job",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
            ],
        )
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        monkeypatch.setattr(admin_mod.database, "count_eligible_for_dispatch_task", lambda row: 4)
        rows = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        keys = [r["task_key"] for r in rows]
        assert "consult_do" not in keys
        assert "vet_inflow_discovery" in keys
        assert "scan_jobs" in keys

    def test_list_dtasks_enrichment_failure_returns_zero_count_not_500(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "id": 1,
                    "task_key": "scan_jobs",
                    "trigger_state": "NEW",
                    "entity_type": "job",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
                {
                    "id": 2,
                    "task_key": "watch_cos",
                    "trigger_state": "WATCH",
                    "entity_type": "company",
                    "candidate_id": "c2",
                    "score_floor": None,
                },
            ],
        )
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())

        def count(row: dict[str, Any]) -> int:
            if row.get("id") == 1:
                raise RuntimeError("boom")
            return 5

        monkeypatch.setattr(admin_mod.database, "count_eligible_for_dispatch_task", count)
        resp = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers)
        assert resp.status_code == 200
        rows = resp.get_json()
        assert len(rows) == 2
        by_id = {r["id"]: r for r in rows}
        assert by_id[1]["available_count"] == 0
        assert by_id[2]["available_count"] == 5


# AST-1106: list_dtasks stamps always_visible_under_avail_gt0 from ADMIN_CONFIG.
@pytest.mark.skipif(
    not hasattr(admin_mod, "admin_always_visible_under_avail_gt0_dispatch_task_keys"),
    reason="AST-1106 always-visible stamp not on this publish tip",
)
class TestAst1106ListDtasksAlwaysVisibleFlag:
    def test_meteorite_email_flag_true_other_false_avail_unchanged(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "id": 1,
                    "task_key": "meteorite_email",
                    "trigger_state": None,
                    "entity_type": None,
                    "candidate_id": None,
                    "score_floor": None,
                },
                {
                    "id": 2,
                    "task_key": "scan_jobs",
                    "trigger_state": "NEW",
                    "entity_type": "job",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
            ],
        )
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        monkeypatch.setattr(
            admin_mod,
            "admin_always_visible_under_avail_gt0_dispatch_task_keys",
            lambda: frozenset({"meteorite_email"}),
        )

        def _count(row):
            et, ts, cid = row.get("entity_type"), row.get("trigger_state"), row.get("candidate_id")
            return 9 if (et and ts and cid) else 0

        monkeypatch.setattr(admin_mod.database, "count_eligible_for_dispatch_task", _count)
        rows = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        by = {r["id"]: r for r in rows}
        assert by[1]["available_count"] == 0
        assert by[1]["always_visible_under_avail_gt0"] is True
        assert by[2]["available_count"] == 9
        assert by[2]["always_visible_under_avail_gt0"] is False



# AST-1135 / AST-1467: list_dtasks stamps live bind-filtered available_count for mailbox rows.
@pytest.mark.skipif(
    not hasattr(admin_mod, "is_meteorite_email_mailbox_task_key"),
    reason="AST-1466 meteorite mailbox Avail stamp path on tip",
)
class TestAst1135ListDtasksMeteoriteMailboxAvail:
    def test_stamps_bound_counts_once(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "id": 1,
                    "task_key": "stage_email_meteorite",
                    "trigger_state": None,
                    "entity_type": None,
                    "candidate_id": "A",
                    "score_floor": None,
                },
                {
                    "id": 2,
                    "task_key": "stage_email_meteorite",
                    "trigger_state": None,
                    "entity_type": None,
                    "candidate_id": "B",
                    "score_floor": None,
                },
                {
                    "id": 3,
                    "task_key": "scan_jobs",
                    "trigger_state": "NEW",
                    "entity_type": "job",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
            ],
        )
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        monkeypatch.setattr(
            admin_mod,
            "admin_always_visible_under_avail_gt0_dispatch_task_keys",
            lambda: frozenset(),
        )
        bound = MagicMock(return_value={"A": 2, "B": 0})
        monkeypatch.setattr(admin_mod, "count_inbox_bound_by_candidate", bound)
        monkeypatch.setattr(
            admin_mod.database,
            "count_eligible_for_dispatch_task",
            lambda row: 9,
        )
        rows = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        by = {r["id"]: r for r in rows}
        assert by[1]["available_count"] == 2
        assert by[2]["available_count"] == 0
        assert by[3]["available_count"] == 9
        assert by[1]["always_visible_under_avail_gt0"] is False
        bound.assert_called_once_with()


# AST-773: PUT dispatch_tasks accepts task_key with validation and AUTO guard.
class TestAst773UpdateDispatchTaskTaskKey:
    def test_dispatch_task_key_trigger_error_helper(self) -> None:
        assert admin_mod._dispatch_task_key_trigger_error("", "NEW") == "task_key is required"
        assert admin_mod._dispatch_task_key_trigger_error("grade_do", "") == "trigger_state is required"
        err = admin_mod._dispatch_task_key_trigger_error("grade_do", "NOT_A_JOB_STATE")
        assert err is not None and "grade_do" in err
        assert admin_mod._dispatch_task_key_trigger_error("qualify_job_listings", "VALID_TITLE") is None

    def test_ast1807_trigger_error_accepts_implicit_retry(self) -> None:
        # AST-1807 / AST-1805: {base}_RETRY validates through its registered base at both sites.
        # General (job) branch.
        assert admin_mod._dispatch_task_key_trigger_error("fetch_jd", "PASSED_JOBLIST_RETRY") is None
        assert admin_mod._dispatch_task_key_trigger_error("fetch_jd", "NOPE_RETRY") == (
            "task_key 'fetch_jd' (job) is not valid for trigger_state 'NOPE_RETRY'"
        )
        # Mailbox candidate branch.
        assert admin_mod._dispatch_task_key_trigger_error("stage_email_meteorite", "RESUME_READY_RETRY") is None
        assert admin_mod._dispatch_task_key_trigger_error("stage_email_meteorite", "NOPE_RETRY") == (
            "task_key 'stage_email_meteorite' (candidate) is not valid for trigger_state 'NOPE_RETRY'"
        )

    def test_dispatch_chain_hop_label_must_match_task_key(self) -> None:
        hop_ts = cfg.dispatch_hop_label(cfg.BUILD_ARTIFACTS_BASE_STATE, "anticipate_scan")
        err = admin_mod._dispatch_task_key_trigger_error("contemplate_job", hop_ts)
        assert err is not None and "does not match hop" in err
        assert admin_mod._dispatch_task_key_trigger_error("anticipate_scan", hop_ts) is None

    def test_update_dispatch_task_task_key_persists_derived_columns(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "qualify_job_listings",
                "trigger_state": "VALID_TITLE",
                "candidate_id": "c1",
                "auto_mode": 0,
            },
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"task_key": "grade_do", "trigger_state": "NEW"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        kw = update.call_args.kwargs
        assert kw["task_key"] == "grade_do"
        assert kw["entity_type"] == "job"
        # AST-1618: sort_by follows effective trigger (NEW), not catalog default PASSED_JD
        assert kw["sort_by"] == cfg.dispatch_task_admin_defaults(
            "grade_do", trigger_state="NEW"
        )["sort_by"]
        assert kw["batch_call_mode"] == cfg.dispatch_task_admin_defaults("grade_do")["batch_call_mode"]

    def test_update_dispatch_task_invalid_task_key_trigger_combo_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "scan_jobs", "trigger_state": "NEW", "candidate_id": "c1", "auto_mode": 0},
        )
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"task_key": "watch_cos", "trigger_state": "NEW"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "watch_cos" in resp.get_json()["error"]

    def test_update_dispatch_task_auto_mode_blocks_non_toggle_edit_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "scan_jobs", "trigger_state": "NEW", "candidate_id": "c1", "auto_mode": 1},
        )
        blocked = admin_client.put("/api/admin/dispatch_tasks/1", json={"min_count": 2}, headers=auth_headers)
        assert blocked.status_code == 400
        assert "AUTO" in blocked.get_json()["error"]
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        toggle = admin_client.put("/api/admin/dispatch_tasks/1", json={"auto_mode": False}, headers=auth_headers)
        assert toggle.status_code == 200
        update.assert_called_once()

    def test_update_dispatch_task_unique_collision_409_new_triple(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "scan_jobs", "trigger_state": "NEW", "candidate_id": "c1", "auto_mode": 0},
        )
        monkeypatch.setattr(
            admin_mod,
            "update_dispatch_task",
            MagicMock(side_effect=Exception("UNIQUE constraint failed: dispatch_task")),
        )
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"task_key": "grade_do", "trigger_state": "PASSED_JD"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        err = resp.get_json()["error"]
        assert "grade_do" in err
        assert "PASSED_JD" in err
        assert "c1" in err


# AST-804: candidate entity_type admin validation + state_options exposure.
# AST-970: candidate registry vocab (ACTIVE_SEARCH / NEW_CANDIDATE).
# AST-1214: inflow_discovery is first-class writable (helper-resolvable).
class TestAst804CandidateDispatchAdminValidation:
    def test_dispatch_task_key_trigger_error_candidate_paths(self) -> None:
        assert admin_mod._dispatch_task_key_trigger_error("intake_initiate_candidate", "ACTIVE_SEARCH") is None
        bad = admin_mod._dispatch_task_key_trigger_error("intake_initiate_candidate", "NOT_A_CANDIDATE_STATE")
        assert bad is not None and "intake_initiate_candidate" in bad
        job_bad = admin_mod._dispatch_task_key_trigger_error("intake_initiate_candidate", "PASSED_JD")
        assert job_bad is not None and "intake_initiate_candidate" in job_bad
        assert admin_mod._dispatch_task_key_trigger_error("grade_do", "PASSED_JD") is None
        assert admin_mod._dispatch_task_key_trigger_error("vet_inflow_discovery", "NEW") is None
        # AST-1214: inflow_discovery is first-class writable via helper-resolvable path
        assert admin_mod._dispatch_task_key_trigger_error("inflow_discovery", "ACTIVE_SEARCH") is None

    def test_state_options_includes_candidate_with_active_search(
        self, admin_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        states = admin_client.get("/api/admin/dispatch_tasks/state_options", headers=auth_headers).get_json()
        assert "candidate" in states
        assert "ACTIVE_SEARCH" in states["candidate"]
        assert "LIVE_PROMPTS" not in states["candidate"]

    def test_create_dispatch_task_rejects_invalid_candidate_trigger_state(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "intake_initiate_candidate",
                "trigger_state": "PASSED_JD",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "intake_initiate_candidate" in resp.get_json()["error"]

    def test_create_dispatch_task_candidate_entity_success(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        save = MagicMock(return_value=55)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "intake_initiate_candidate",
                "trigger_state": "ACTIVE_SEARCH",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert save.call_args.kwargs["task_key"] == "intake_initiate_candidate"
        assert save.call_args.kwargs["trigger_state"] == "ACTIVE_SEARCH"

    def test_update_dispatch_task_trigger_state_only_candidate_row(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "intake_initiate_candidate",
                "trigger_state": "ACTIVE_SEARCH",
                "entity_type": "candidate",  # AST-1618: sort recompute needs row entity
                "candidate_id": "c1",
                "auto_mode": 0,
            },
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        ok = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"trigger_state": "NEW_CANDIDATE"},
            headers=auth_headers,
        )
        assert ok.status_code == 200
        update.assert_called_once()
        bad = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"trigger_state": "PASSED_JD"},
            headers=auth_headers,
        )
        assert bad.status_code == 400
        assert "intake_initiate_candidate" in bad.get_json()["error"]


# Branches: timesheet list/export with optional req_dict filters.
class TestTimesheets:
    def test_list_and_export_timesheets(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        row = {"anthropic_req_id": "r1", "created_at": "now", "candidate_id": "c1", "batch_id": "b1", "task_key_uuid": "u1", "model_code": "m", "batch_size": 1,
               "cache_write_tokens": 0, "cache_read_tokens": 0, "no_cache_prompt_tokens": 0, "no_cache_live_tokens": 0,
               "total_no_cache_input_tokens": 0, "total_output_tokens": 0, "calc_cost_cache_write": 0, "calc_cost_cache_read": 0,
               "calc_cost_no_cache_input": 0, "calc_cost_output": 0, "agent_performance": "", "failure_note": ""}
        enriched = {**row, "total_cost": 0.0}
        monkeypatch.setattr(admin_mod, "list_timesheets", lambda **kwargs: [row])
        plain = admin_client.get("/api/admin/timesheets?candidate_id=c1", headers=auth_headers)
        assert plain.get_json() == [enriched]
        shaped = admin_client.get("/api/admin/timesheets?req_dict=1", headers=auth_headers)
        assert shaped.get_json()["rows"] == [enriched]
        export = admin_client.get("/api/admin/timesheets/export?candidate_id=c1", headers=auth_headers)
        assert export.status_code == 200
        assert "text/csv" in export.headers["Content-Type"]


# Branches: dispatch ledger list/detail/logs.
class TestDispatchLedger:
    def test_ledger_routes(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_ledger", lambda **kwargs: [{"batch_id": "b1"}])
        assert admin_client.get("/api/admin/dispatch_ledger?status=done", headers=auth_headers).get_json()[0]["batch_id"] == "b1"
        monkeypatch.setattr(admin_mod, "get_dispatch_ledger", lambda batch_id: None)
        assert admin_client.get("/api/admin/dispatch_ledger/missing", headers=auth_headers).status_code == 404
        monkeypatch.setattr(admin_mod, "get_dispatch_ledger", lambda batch_id: {"batch_id": batch_id})
        assert admin_client.get("/api/admin/dispatch_ledger/b1", headers=auth_headers).get_json()["batch_id"] == "b1"
        monkeypatch.setattr(admin_mod, "list_log_entries", lambda batch_id: [{"line": "ok"}])
        assert admin_client.get("/api/admin/dispatch_ledger/b1/logs", headers=auth_headers).get_json()[0]["line"] == "ok"


# Branches: scored dispatch tasks, create/update validation, scheduler controls.
class TestDispatchTasks:
    def test_list_dispatch_tasks_and_keys(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {"task_key": "qualify_job_listings", "trigger_state": "PASSED_JOBLIST", "entity_type": "job", "candidate_id": "c1", "score_floor": None},
                {"task_key": "qualify_job_listings", "trigger_state": "VALID_TITLE", "entity_type": "job", "candidate_id": "c1", "score_floor": 2.5},
                {"task_key": "custom", "trigger_state": "WATCH", "entity_type": "company", "candidate_id": "", "score_floor": 2.0},
            ],
        )
        monkeypatch.setattr(admin_mod.database, "count_eligible_for_dispatch_task", lambda row: 7)
        rows = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        assert rows[0]["is_scored"] is True
        assert rows[0]["score_floor"] == 1.0
        assert rows[1]["is_scored"] is False
        assert rows[1]["score_floor"] is None
        assert rows[2]["available_count"] == 0
        shaped = admin_client.get("/api/admin/dispatch_tasks?req_dict=1", headers=auth_headers)
        assert shaped.get_json()["rows"][0]["available_count"] == 7
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["qualify_job_listings"]["entity_type"] == "job"
        assert keys["custom"]["trigger_state"] == "WATCH"
        states = admin_client.get("/api/admin/dispatch_tasks/state_options", headers=auth_headers)
        assert "NEW" in states.get_json()["job"]
        if hasattr(cfg, "dispatch_score_floor_option_labels"):
            floors = admin_client.get("/api/admin/dispatch_tasks/score_floor_options", headers=auth_headers)
            floor_values = floors.get_json()["values"]
            assert len(floor_values) == 21
            assert floor_values[0] == "0.00"
            assert floor_values[1] == "0.50"
            assert floor_values[-1] == "10.00"


    def test_create_dispatch_task_rejects_retired_consult_key(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "consult_do",
                "trigger_state": "PASSED_JD",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        err = resp.get_json()["error"]
        assert "retired" in err
        assert "grade_do" in err

    def test_create_dispatch_task_rejects_retired_consult_key(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "consult_do",
                "trigger_state": "PASSED_JD",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        err = resp.get_json()["error"]
        assert "retired" in err
        assert "grade_do" in err

    def test_create_dispatch_task_paths(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        assert admin_client.post("/api/admin/dispatch_tasks", json={"task_key": "t"}, headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: "need key")
        auto_bad = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "qualify_job_listings", "trigger_state": "VALID_TITLE", "min_count": 1, "auto_mode": True},
            headers=auth_headers,
        )
        assert auto_bad.status_code == 400
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(side_effect=Exception("UNIQUE constraint failed")))
        dup = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "qualify_job_listings", "trigger_state": "VALID_TITLE", "min_count": 1, "batch_size": 2, "freq_hrs": 1.5, "score_floor": 2.5},
            headers=auth_headers,
        )
        assert dup.status_code == 409
        # AST-955: membership is TASK_CONFIG — junk keys 400 before save (no fake custom/WATCH).
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(side_effect=RuntimeError("boom")))
        assert admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "min_count": 1,
            },
            headers=auth_headers,
        ).status_code == 500
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(return_value=42))
        ok = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert ok.status_code == 201
        save = admin_mod.save_dispatch_task
        scored_default = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "qualify_job_listings", "trigger_state": "PASSED_JOBLIST", "min_count": 1},
            headers=auth_headers,
        )
        assert scored_default.status_code == 201
        assert save.call_args.kwargs["score_floor"] == 1.0
        save.reset_mock()
        valid_title = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "qualify_job_listings", "trigger_state": "VALID_TITLE", "min_count": 1},
            headers=auth_headers,
        )
        assert valid_title.status_code == 201
        assert save.call_args.kwargs["score_floor"] is None

    def test_update_dispatch_task_paths(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "qualify_job_listings",
                "trigger_state": "VALID_TITLE",
                "entity_type": "job",
                "candidate_id": "c1",
                "auto_mode": 0,
            },
        )
        assert admin_client.put(f"/api/admin/dispatch_tasks/1", json={}, headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: "need key")
        assert admin_client.put(
            f"/api/admin/dispatch_tasks/1",
            json={"auto_mode": True, "min_count": 2, "batch_size": 3, "debug": False, "skip_cache": True, "freq_hrs": 1.0, "max_runs": 5, "score_floor": 2.0, "trigger_state": "VALID_TITLE"},
            headers=auth_headers,
        ).status_code == 400
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        # Schedule-only update (no empty trigger — blank trigger_state is 400)
        ok = admin_client.put(f"/api/admin/dispatch_tasks/1", json={"min_count": 2}, headers=auth_headers)
        assert ok.status_code == 200
        update.assert_called_once()

    def test_scheduler_and_run_controls(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda task_id: None)
        assert admin_client.post("/api/admin/dispatch_tasks/1/run", headers=auth_headers).status_code == 404
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda task_id: {"candidate_id": None})
        assert admin_client.post("/api/admin/dispatch_tasks/1/run", headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda task_id: {"candidate_id": "c1", "task_key": "qualify_job_listings"})
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_empty_render_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(admin_mod, "rubric_dispatch_error", lambda candidate_id, task_key: None, raising=False)  # AST-2091
        monkeypatch.setattr(admin_mod, "run_task", lambda task_id, ui_initiated=False: True)
        assert admin_client.post("/api/admin/dispatch_tasks/1/run", headers=auth_headers).get_json()["started"] is True
        monkeypatch.setattr(admin_mod, "drain_task", lambda task_id: {"drained": True})
        monkeypatch.setattr(admin_mod, "cancel_task", lambda task_id: {"killed": True})
        assert admin_client.post("/api/admin/dispatch_tasks/1/stop", headers=auth_headers).get_json()["drained"] is True
        assert admin_client.post("/api/admin/dispatch_tasks/1/kill", headers=auth_headers).get_json()["killed"] is True
        monkeypatch.setattr(admin_mod, "task_status_all", lambda: {})
        assert admin_client.get("/api/admin/scheduler/thread_status", headers=auth_headers).get_json() == {}
        monkeypatch.setattr(admin_mod, "cancel_all_tasks", lambda: 2)
        assert admin_client.post("/api/admin/scheduler/stop_all", headers=auth_headers).get_json()["killed"] == 2


# Branches: adhoc entity listing and live-content assembly.
class TestAdhocHelpers:
    def test_trigger_state_helpers(self) -> None:
        # Resolved from config (AST-468): scored dispatch detection no longer keyed per admin helper call.
        assert cfg.trigger_state_used_by_scored_dispatch_task(None) is False
        assert cfg.trigger_state_used_by_scored_dispatch_task("VALID_TITLE_RETRY") is False
        assert cfg.trigger_state_used_by_scored_dispatch_task("PASSED_JOBLIST") is True
        assert cfg.dispatch_task_key_is_scored("grade_do") is True
        # AST-586: claim gating diverges from legacy graded-trigger helper.
        assert cfg.dispatch_claim_uses_score_floor("VALID_TITLE") is False
        assert cfg.dispatch_claim_uses_score_floor("PASSED_JD") is True

    def test_build_adhoc_live_content_company_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "company"})
        assert admin_mod._build_adhoc_live_content("prefilter_company", "missing") == ""
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {
                "company_data": {
                    "homepage_text": "home",
                    "nav_links": ["a"],
                    "job_page_dom": "dom",
                    "website_content": [{"url": "u", "content": "c"}],
                }
            },
        )
        assert "HOMEPAGE" in admin_mod._build_adhoc_live_content("prefilter_company", "acme")
        # locate + select share nav_links preview; parse uses job_page_dom (AST-721).
        locate_s = admin_mod._build_adhoc_live_content("locate_job_page", "acme")
        sel_s = admin_mod._build_adhoc_live_content("select_job_page", "acme")
        assert locate_s == sel_s
        assert admin_mod._build_adhoc_live_content("parse_job_list", "acme") == "dom"
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {"company_data": {"website_content": "plain"}},
        )
        assert admin_mod._build_adhoc_live_content("gaze", "acme") == "plain"

    def test_build_adhoc_live_content_job_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "job"})
        monkeypatch.setattr(
            admin_mod.database,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"raw_job_listing": f"raw-{job_id}"}, "company": "acme"},
        )
        monkeypatch.setattr(admin_mod.database, "get_company", lambda short_name: {"job_site": "site", "data": {"website_content": [{"url": "u", "content": "v"}]}})
        batch = admin_mod._build_adhoc_live_content("qualify_job_listings", "", ["j1", "j2"])
        assert "JOB LISTINGS" in batch
        single = admin_mod._build_adhoc_live_content("evaluate_jd", "j1")
        assert "[astral_job_id=j1]" in single
        monkeypatch.setitem(admin_mod.TASK_CONFIG, "evaluate_jd", {**admin_mod.TASK_CONFIG["evaluate_jd"], "requires_company": True})
        like = admin_mod._build_adhoc_live_content("evaluate_jd", "j1")
        assert "COMPANY CONTEXT" in like
        monkeypatch.setattr(admin_mod.database, "get_job", lambda job_id: None)
        assert admin_mod._build_adhoc_live_content("evaluate_jd", "missing") == ""

    def test_build_adhoc_live_content_qualify_meteorite(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "job"})
        from src.utils.config import TRACKER_CONFIG

        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        monkeypatch.setattr(
            admin_mod.database,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "job_link": f"https://jobs.example.com/{job_id}",
                "job_data": {jd_key: f"jd-{job_id}"},
            },
        )
        batch = admin_mod._build_adhoc_live_content("qualify_meteorite", "", ["j1", "j2"])
        assert batch.startswith("METEORITE JOBS:")
        assert "000: job_link:" in batch
        # AST-1197: lockstep with consult assemble CONTENT label.
        assert "CONTENT:\njd-j1" in batch and "CONTENT:\njd-j2" in batch
        assert "jd-j1" in batch and "jd-j2" in batch
        monkeypatch.setattr(admin_mod.database, "get_job", lambda job_id: None)
        assert admin_mod._build_adhoc_live_content("qualify_meteorite", "", ["missing"]) == ""

    def test_adhoc_entities_and_resolve(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: None)
        assert admin_client.get("/api/admin/adhoc/entities?task_key=missing", headers=auth_headers).status_code == 404
        monkeypatch.setattr(
            admin_mod,
            "get_dispatch_task_by_key",
            lambda task_key: {"entity_type": "company", "trigger_state": "WATCH", "batch_mode": True},
        )
        monkeypatch.setattr(admin_mod.database, "list_companies", lambda **kwargs: [{"short_name": "acme", "company_name": "Acme"}])
        company = admin_client.get("/api/admin/adhoc/entities?task_key=t1&candidate_id=c1", headers=auth_headers).get_json()
        assert company["entities"][0]["id"] == "acme"
        monkeypatch.setattr(
            admin_mod,
            "get_dispatch_task_by_key",
            lambda task_key: {"entity_type": "job", "trigger_state": "NEW", "batch_mode": False},
        )
        monkeypatch.setattr(admin_mod.database, "list_jobs", lambda **kwargs: [{"astral_job_id": "j1", "job_title": "Eng"}])
        job = admin_client.get("/api/admin/adhoc/entities?task_key=t2", headers=auth_headers).get_json()
        assert job["entities"][0]["label"] == "Eng"
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "other", "trigger_state": "X"})
        other = admin_client.get("/api/admin/adhoc/entities?task_key=t3", headers=auth_headers).get_json()
        assert other["entities"] == []

        with admin_client.application.app_context():
            resolved, err = admin_mod._resolve_adhoc({})
            assert err is not None
            monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
            _, err = admin_mod._resolve_adhoc({"agent_id": "a1"})
            assert err[1] == 404
            # AST-1880: no legacy Medium inference — an agent without a model is a client error.
            monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id})
            _, err = admin_mod._resolve_adhoc({"agent_id": "a1"})
            assert err[1] == 400
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {
                "agent_id": agent_id, "model_id": "claude-haiku-4-5", "content": "sys", "max_tokens": None,
            },
        )
        monkeypatch.setattr(
            admin_mod.database, "get_candidate",
            lambda candidate_id: {"candidate_data": {"x": 1}, "candidate_api_keys": {"anthropic": "key"}, "candidate_api_key": "legacy"},
        )
        # AST-1855: hydrated loader (AST-1854) reads artifacts — keep it off the repo DB.
        monkeypatch.setattr(admin_mod.database, "get_current_artifact", lambda *a: None)
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: {"task_key_uuid": "uuid-1"})
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text)
        payload, err = admin_mod._resolve_adhoc({"agent_id": "a1", "candidate_id": "c1", "task_key": "craft_resume_base", "user_prompt": "u"})
        assert err is None
        # AST-1880: whole key map handed to core; core picks the route's server (AST-1879)
        assert payload["candidate_api_keys"] == {"anthropic": "key"}
        assert "api_key_override" not in payload
        assert (payload["model_code"], payload["server_id"]) == ("claude-haiku-4-5", "anthropic")

    def test_resolve_adhoc_job_entity_resolves_visible_jd_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {
                "agent_id": agent_id, "content": "{$VISIBLE_JD}", "model_id": "claude-haiku-4-5",
            },
        )
        monkeypatch.setattr(
            admin_mod.database,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"artifacts": {"jobdesc_rubric": {"criteria": []}}}},
        )
        # AST-1855: hydrated loader (AST-1854) reads artifacts — keep it off the repo DB.
        monkeypatch.setattr(admin_mod.database, "get_current_artifact", lambda *a: None)
        monkeypatch.setattr(
            admin_mod.database,
            "get_job",
            lambda job_id: {
                "astral_job_id": job_id,
                "job_data": {"job_description": "Preview JD body"},
            },
        )
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda task_key: {"task_key_uuid": "uuid-contemplate"},
        )
        payload, err = admin_mod._resolve_adhoc(
            {
                "agent_id": "a1",
                "candidate_id": "c1",
                "task_key": "contemplate_job",
                "entity_id": "job-513",
            }
        )
        assert err is None
        assert payload["system"] == "Preview JD body"


# AST-1880 — _resolve_adhoc routes by the agent's own model (catalog), no global provider.
# AST-1957: tier from resolve_agent_settings(model_id, agent row) — settings as stored, empty → None.
# Branches: catalog defaults; temperature as stored (incl. 0 / None); max_tokens override; OpenRouter provider
# object from the row; retired / unknown / no model → 400.
class TestAst1880ResolveAdhocCatalogRoute:
    @staticmethod
    def _agent(monkeypatch: pytest.MonkeyPatch, **agent: Any) -> None:
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id, "content": "sys", **agent})

    def test_deepseek_flash_uses_catalog_sku_server_tier_and_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._agent(monkeypatch, model_id="deepseek-v4-flash")
        route = cfg.resolve_agent_settings("deepseek-v4-flash", {})
        payload, err = admin_mod._resolve_adhoc({"agent_id": "z1"})
        assert err is None
        assert (payload["model_code"], payload["server_id"], payload["tier"]) == ("deepseek-v4-flash", "deepseek", route["tier"])
        # AST-1957: no stored temperature → None (not sent); empty max_tokens → the model's default.
        assert (payload["temperature"], payload["max_tokens"]) == (None, route["tier"]["default_max_tokens"])
        assert payload["candidate_api_keys"] is None
        assert "tier_meta" not in payload

    @pytest.mark.parametrize("temperature", [0, 0.6, None], ids=["zero", "set", "empty"])
    def test_temperature_as_stored_and_max_tokens_override_wins(
        self, temperature: float | None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # principal_recruiter_estelle shape: Kimi, max_tokens 384000. AST-1957: temperature / effort pass through as stored.
        self._agent(monkeypatch, model_id="kimi-k2.6", temperature=temperature, reasoning_effort="high", max_tokens=384000)
        payload, err = admin_mod._resolve_adhoc({"agent_id": "z1"})
        assert err is None
        assert (payload["server_id"], payload["model_code"]) == ("kimi", "kimi-k2.6")
        assert (payload["temperature"], payload["max_tokens"]) == (temperature, 384000)
        assert (payload["tier"]["temperature"], payload["tier"]["reasoning_effort"]) == (temperature, "high")
        assert "thinking" not in payload["tier"]

    def test_openrouter_agent_row_settings_become_the_provider_object(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1957: the resolver gets the whole agent row, so the OpenRouter routing object reflects it.
        self._agent(
            monkeypatch, model_id="qwen/qwen3-32b", quantization="fp8", provider_allow_fallbacks=False,
            provider_only=["groq"], provider_ignore=None, provider_sort="price",
        )
        payload, err = admin_mod._resolve_adhoc({"agent_id": "z1"})
        assert err is None
        assert payload["server_id"] == "openrouter"
        assert payload["tier"]["provider"] == {
            "quantizations": ["fp8"], "allow_fallbacks": False, "only": ["groq"], "sort": "price",
        }

    def test_adhoc_test_forwards_route_and_key_map_to_core(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, Any] = {}
        tier = cfg.resolve_agent_settings("kimi-k2.6", {"temperature": 0})["tier"]
        monkeypatch.setattr(
            admin_mod, "_resolve_adhoc",
            lambda _b: ({"system": "s", "user": "u", "cache": "", "cache_a": "", "cache_b": "", "cache_c": "", "cache_d": "",
                         "nocache": "", "model_code": "kimi-k2.6", "server_id": "kimi", "tier": tier, "temperature": 0,
                         "max_tokens": 384000, "candidate_id": "c1", "task_key_uuid": None,
                         "candidate_api_keys": {"kimi": "sk-k"}}, None),
        )

        async def run_ok(**kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return {"success": True, "parsed_response": "ok", "timesheet": {}}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_ok)
        resp = admin_client.post("/api/admin/adhoc/test", json={"agent_id": "a1", "task_key": "evaluate_jd"}, headers=auth_headers)
        assert resp.status_code == 200
        assert (captured["model_code"], captured["server_id"], captured["tier"]) == ("kimi-k2.6", "kimi", tier)
        assert (captured["temperature"], captured["max_tokens"]) == (0, 384000)
        assert captured["candidate_api_keys"] == {"kimi": "sk-k"}
        assert {"api_key_override", "tier_meta"}.isdisjoint(captured)

    @pytest.mark.parametrize(
        "agent",
        [
            # AST-1955: pre-migration direct id (AST-1958 moves live rows) is a client error.
            {"model_id": "claude"},
            {"model_id": "__no_model__"},
            {},
            {"model_code": "claude-haiku-4-5"},
        ],
        ids=["retired_direct_id", "unknown_model", "no_model_id", "legacy_model_code_only"],
    )
    def test_unroutable_agent_returns_400(self, agent: dict, admin_client: FlaskClient, monkeypatch: pytest.MonkeyPatch) -> None:
        self._agent(monkeypatch, **agent)
        with admin_client.application.app_context():
            payload, err = admin_mod._resolve_adhoc({"agent_id": "z1"})
            assert payload is None
            assert err[1] == 400
            assert err[0].get_json()["error"]


# Branches: adhoc preview/test success and failure envelopes.
class TestAdhocRoutes:
    def test_adhoc_preview_and_test(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "_resolve_adhoc",
            lambda body: (
                {
                    "system": "s",
                    "user": "u",
                    "cache": "c",
                    "cache_a": "c",
                    "cache_b": "",
                    "cache_c": "",
                    "cache_d": "",
                    "nocache": "n",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": "c1",
                    "task_key_uuid": None,
                    "server_id": "anthropic",
                    "tier": {},
                    "candidate_api_keys": None,
                },
                None,
            ),
        )
        monkeypatch.setattr(admin_mod, "_build_adhoc_live_content", lambda *args, **kwargs: "live")
        preview = admin_client.post(
            "/api/admin/adhoc/preview",
            json={"agent_id": "a1", "task_key": "evaluate_jd", "entity_id": "j1"},
            headers=auth_headers,
        )
        assert preview.get_json()["live_content"] == "live"
        async def run_fail(**kwargs):
            raise RuntimeError("boom")

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_fail)
        failed = admin_client.post("/api/admin/adhoc/test", json={"agent_id": "a1", "task_key": "evaluate_jd"}, headers=auth_headers)
        assert failed.status_code == 500

        async def run_unsuccessful(**kwargs):
            return {"success": False, "error": "nope"}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_unsuccessful)
        assert admin_client.post("/api/admin/adhoc/test", json={"agent_id": "a1", "task_key": "evaluate_jd"}, headers=auth_headers).status_code == 500
        async def run_ok(**kwargs):
            return {"success": True, "parsed_response": {"agent_payload": "payload"}, "timesheet": {"t": 1}}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_ok)
        ok = admin_client.post(
            "/api/admin/adhoc/test",
            json={"agent_id": "a1", "task_key": "grade_do", "entity_ids": ["j1"], "entity_id": "j1"},
            headers=auth_headers,
        )
        assert ok.get_json()["response_text"] == "payload"
        async def run_numeric(**kwargs):
            return {"success": True, "parsed_response": 123, "timesheet": {}}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_numeric)
        numeric = admin_client.post("/api/admin/adhoc/test", json={"agent_id": "a1", "task_key": "evaluate_jd"}, headers=auth_headers)
        assert numeric.get_json()["response_text"] == "123"
        async def run_encoded(**kwargs):
            return {"success": True, "parsed_response": "encoded", "timesheet": {}}

        monkeypatch.setattr(admin_mod, "_decode_payload", MagicMock(side_effect=ValueError("decode")))
        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_encoded)
        hydrated = admin_client.post("/api/admin/adhoc/test", json={"agent_id": "a1", "task_key": "grade_do"}, headers=auth_headers)
        assert hydrated.get_json()["hydrated"]["error"] == "decode"

    def test_adhoc_preview_does_not_create_dispatch_ledger(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save_ledger = MagicMock()
        monkeypatch.setattr(admin_mod.database, "save_dispatch_ledger", save_ledger)
        workbench = MagicMock()
        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", workbench)
        monkeypatch.setattr(
            admin_mod,
            "_resolve_adhoc",
            lambda body: (
                {
                    "system": "s",
                    "user": "u",
                    "cache": "",
                    "cache_a": "",
                    "cache_b": "",
                    "cache_c": "",
                    "cache_d": "",
                    "nocache": "",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": "c1",
                    "task_key_uuid": None,
                    "server_id": "anthropic",
                    "tier": {},
                    "candidate_api_keys": None,
                },
                None,
            ),
        )
        monkeypatch.setattr(admin_mod, "_build_adhoc_live_content", lambda *args, **kwargs: "")
        assert (
            admin_client.post(
                "/api/admin/adhoc/preview",
                json={"agent_id": "a1", "task_key": "evaluate_jd"},
                headers=auth_headers,
            ).status_code
            == 200
        )
        save_ledger.assert_not_called()
        workbench.assert_not_called()


# Branches: SQL runner, config upsert, and data-sync endpoints.
class TestDataManagement:
    def test_run_sql_paths(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        assert admin_client.post("/api/admin/data/sql", json={}, headers=auth_headers).status_code == 400
        conn = MagicMock()
        cursor = MagicMock()
        cursor.description = [("created_at",), ("payload",)]
        cursor.fetchall.return_value = [("2026-01-01", zlib.compress(b"hello"))]
        conn.execute.return_value = cursor
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        select = admin_client.post("/api/admin/data/sql", json={"sql": "select 1"}, headers=auth_headers)
        assert select.get_json()["type"] == "select"
        shaped = admin_client.post("/api/admin/data/sql", json={"sql": "select 1", "req_dict": True}, headers=auth_headers)
        assert shaped.get_json()["columns"][0]["type"] == "datetime"
        cursor.description = None
        cursor.rowcount = 3
        execute = admin_client.post("/api/admin/data/sql", json={"sql": "delete from t"}, headers=auth_headers)
        assert execute.get_json()["rows_affected"] == 3
        conn.execute.side_effect = RuntimeError("bad sql")
        assert admin_client.post("/api/admin/data/sql", json={"sql": "bad"}, headers=auth_headers).status_code == 400
        conn.close.assert_called()

    def test_infer_col_type_and_decode_blob_values(self) -> None:
        assert admin_mod._infer_col_type("created_at") == "datetime"
        assert admin_mod._infer_col_type("calc_cost") == "currency"
        assert admin_mod._infer_col_type("batch_id") == "str"
        assert admin_mod._infer_col_type("name") == "str"
        row = admin_mod._decode_blob_values({"payload": zlib.compress(b"ok"), "raw": b"\x00\x01"})
        assert row["payload"] == "ok"
        assert row["raw"].startswith("<binary")

    def test_upsert_config_table_paths(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        assert admin_client.post("/api/admin/data/upsert_config_table", json={"table": "nope"}, headers=auth_headers).status_code == 400
        assert admin_client.post("/api/admin/data/upsert_config_table", json={"table": "agent_task", "columns": [], "rows": []}, headers=auth_headers).status_code == 400
        assert admin_client.post("/api/admin/data/upsert_config_table", json={"table": "agent_task", "columns": ["a"], "rows": "nope"}, headers=auth_headers).status_code == 400
        conn = MagicMock()
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(admin_mod, "apply_config_table_upsert", MagicMock(side_effect=ValueError("bad rows")))
        assert admin_client.post("/api/admin/data/upsert_config_table", json={"table": "agent_task", "columns": ["a"], "rows": []}, headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod, "apply_config_table_upsert", MagicMock(side_effect=RuntimeError("boom")))
        assert admin_client.post("/api/admin/data/upsert_config_table", json={"table": "agent_task", "columns": ["a"], "rows": []}, headers=auth_headers).status_code == 500
        monkeypatch.setattr(admin_mod, "apply_config_table_upsert", MagicMock(return_value={"ok": True}))
        ok = admin_client.post("/api/admin/data/upsert_config_table", json={"table": "agent_task", "columns": ["a"], "rows": []}, headers=auth_headers)
        assert ok.get_json()["ok"] is True

    def test_data_sync_routes(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        conn = MagicMock()
        conn.__enter__ = lambda self: conn
        conn.__exit__ = lambda *args: None
        conn.execute.return_value.fetchall.return_value = [{"name": "jobs"}]
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        tables = admin_client.get("/api/admin/data/tables", headers=auth_headers)
        assert tables.get_json()["tables"] == ["jobs"]
        conn.execute.return_value.fetchone.return_value = None
        assert admin_client.get("/api/admin/data/table/missing", headers=auth_headers).status_code == 404
        conn.execute.return_value.fetchone.return_value = (1,)
        conn.execute.return_value.fetchall.side_effect = [
            [{"name": "id"}, {"name": "title"}],
            [("j1", "Eng")],
        ]
        full = admin_client.get("/api/admin/data/table/jobs", headers=auth_headers)
        assert full.get_json()["rows"] == [["j1", "Eng"]]
        conn.execute.return_value.fetchall.side_effect = [[{"name": "id"}]]
        schema = admin_client.get("/api/admin/data/table/jobs?schema_only=1", headers=auth_headers)
        assert schema.get_json()["rows"] == []
        monkeypatch.setattr(admin_mod, "send_file", lambda *args, **kwargs: ("db-bytes", 200, {}))
        download = admin_client.get("/api/admin/data/download", headers=auth_headers)
        assert download.status_code == 200


# Branches: culture-link backfill start/status/companies and candidate key helper.
class TestBackfillAndCandidateKey:
    def test_candidate_dispatch_api_key_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1880: the key required is the one for the task agent's server, named by its label.
        err = admin_mod._candidate_dispatch_api_key_error
        assert err(None, "select_job_page") == "This dispatch task has no candidate; set one before Run or Auto."
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        assert err("c1", "select_job_page") == "Candidate not found: c1"
        asked: list = []
        monkeypatch.setattr(admin_mod, "task_llm_server_id", lambda task_key: asked.append(task_key) or "kimi")
        need_kimi = "Set this candidate's Kimi API key before using Run or Auto on this task."
        for cand in ({"astral_candidate_id": "c1"}, {"candidate_api_keys": None}, {"candidate_api_keys": {"anthropic": "sk-a"}}, {"candidate_api_keys": {"kimi": ""}},
                     {"candidate_api_key": "legacy-ciphertext"}):
            monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id, c=cand: c)
            assert err("c1", "select_job_page") == need_kimi, cand
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: {"candidate_api_keys": {"kimi": "sk-k"}})
        assert err("c1", "select_job_page") is None
        assert set(asked) == {"select_job_page"}

    def test_candidate_dispatch_api_key_error_agentless_task_needs_no_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Table runners / notify tasks have no agent model → no platform key to require.
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: {"candidate_api_keys": {}})

        def _no_agent(task_key: str) -> str:
            raise ValueError(f"no agent for {task_key}")

        monkeypatch.setattr(admin_mod, "task_llm_server_id", _no_agent)
        assert admin_mod._candidate_dispatch_api_key_error("c1", "meteorite_retention") is None

    def test_backfill_routes(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        admin_mod._backfill_thread = None
        admin_mod._backfill_status.update(status="idle", message="")
        monkeypatch.setattr(admin_mod, "run_backfill", lambda **kwargs: None)
        started = admin_client.post("/api/admin/script/backfill_culture_links", json={"dry_run": True, "company": "acme"}, headers=auth_headers)
        assert started.get_json()["started"] is True
        if admin_mod._backfill_thread:
            admin_mod._backfill_thread.join(timeout=2)
        blocker = threading.Event()
        admin_mod._backfill_thread = threading.Thread(target=blocker.wait, args=(2,))
        admin_mod._backfill_thread.start()
        assert admin_client.post("/api/admin/script/backfill_culture_links", json={}, headers=auth_headers).status_code == 409
        blocker.set()
        admin_mod._backfill_thread.join(timeout=2)
        admin_mod._backfill_thread = None
        status = admin_client.get("/api/admin/script/backfill_culture_links/status", headers=auth_headers)
        assert status.get_json()["status"] in {"idle", "running", "done", "error"}
        monkeypatch.setattr(
            admin_mod.database,
            "list_companies",
            lambda **kwargs: [
                {"short_name": "b", "company_name": "Beta", "company_data": {}},
                {"short_name": "a", "company_name": "Alpha", "company_data": {"culture_links_to_explore": ["x"]}},
            ],
        )
        companies = admin_client.get("/api/admin/script/backfill_culture_links/companies", headers=auth_headers)
        assert companies.get_json()["companies"][0]["short_name"] == "b"


# Branches: remaining helper and route edges for full branch lock.
class TestApiAdminBranchGaps:
    def test_enrich_tasks_agent_only_system_prompt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": "craft_resume_base", "task_key_uuid": None, "agent_id": "agent-1", "cache_prompt_len": 0, "nocache_prompt_len": 0}],
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: None)
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"model_code": "claude-haiku-4-5", "content": "agent-only"})
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text)
        rows = admin_mod._enrich_tasks("")
        assert rows[0]["system_prompt_tokens"] > 0

    def test_update_task_missing_returns_404(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: None)
        assert admin_client.put("/api/admin/tasks/missing", json={"run_next": "x"}, headers=auth_headers).status_code == 404

    def test_dispatch_task_keys_db_row_adds_orphan_key(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [{"task_key": "dup", "entity_type": "job", "trigger_state": "NEW"}])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["dup"]["entity_type"] == "job"
        assert keys["dup"]["trigger_state"] == "NEW"

    def test_create_dispatch_task_auto_mode_success(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_empty_render_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(admin_mod, "rubric_dispatch_error", lambda candidate_id, task_key: None, raising=False)  # AST-2091
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(return_value=9))
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "qualify_job_listings", "trigger_state": "PASSED_JOBLIST", "min_count": 1, "auto_mode": True},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    def test_build_adhoc_live_content_remaining_company_and_job_edges(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "company"})
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {"company_data": {"homepage_text": "", "website_content": "", "nav_links": []}},
        )
        assert admin_mod._build_adhoc_live_content("prefilter_company", "acme") == ""
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {"company_data": {"homepage_text": "home", "nav_links": ["a"]}},
        )
        assert "HOMEPAGE" in admin_mod._build_adhoc_live_content("prefilter_company", "acme")
        assert admin_mod._build_adhoc_live_content("select_job_page", "acme") != ""
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {"company_data": {"website_content": [{"url": "u", "content": ""}, {"url": "u2", "content": "body"}]}},
        )
        assert "body" in admin_mod._build_adhoc_live_content("gaze", "acme")
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "job"})
        monkeypatch.setattr(
            admin_mod.database,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"raw_job_listing": "raw"}, "company": "acme"},
        )
        monkeypatch.setattr(admin_mod.database, "get_company", lambda short_name: {"job_site": "site"})
        assert admin_mod._build_adhoc_live_content("qualify_job_listings", "", ["j1"]) != ""
        # Retired validate_title has no dedicated live-content branch — single-entity JD/raw path.
        assert "raw" in admin_mod._build_adhoc_live_content("validate_title", "j1")
        monkeypatch.setattr(admin_mod.database, "get_job", lambda job_id: None)
        assert admin_mod._build_adhoc_live_content("qualify_job_listings", "", ["missing"]) == ""
        monkeypatch.setitem(admin_mod.TASK_CONFIG, "evaluate_jd", {**admin_mod.TASK_CONFIG["evaluate_jd"], "requires_company": True})
        monkeypatch.setattr(admin_mod.database, "get_job", lambda job_id: {"astral_job_id": job_id, "job_data": {"job_description": "jd"}, "company": "acme"})
        monkeypatch.setattr(admin_mod.database, "get_company", lambda short_name: {"data": {"website_content": [{"url": "u", "content": "vibes"}]}})
        assert "COMPANY CONTEXT" in admin_mod._build_adhoc_live_content("evaluate_jd", "j1")
        monkeypatch.setattr(admin_mod.database, "get_company", lambda short_name: {"data": {"website_content": ""}})
        assert "COMPANY CONTEXT" not in admin_mod._build_adhoc_live_content("evaluate_jd", "j1")
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "other"})
        assert admin_mod._build_adhoc_live_content("noop", "x") == ""

    def test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert "locate_job_page" not in keys
        assert "find_job_page" not in keys
        for k in ("select_job_page", "parse_job_list"):
            assert k in keys
            assert keys[k]["entity_type"] == "company"
        assert keys["select_job_page"]["trigger_state"] == "PJL_READY"
        assert keys["parse_job_list"]["trigger_state"] == "JOBLIST_IDENTIFIED"

    def test_ast535_create_dispatch_task_triple_unique_409(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(
            admin_mod,
            "save_dispatch_task",
            MagicMock(side_effect=Exception("UNIQUE constraint failed: dispatch_task")),
        )
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c535",
                "task_key": "parse_job_list",
                "trigger_state": "JOBLIST_IDENTIFIED",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 409
        err = resp.get_json()["error"]
        assert "c535" in err and "parse_job_list" in err and "JOBLIST_IDENTIFIED" in err

    def test_dispatch_task_keys_includes_task_config_registry(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        """Scheduled Actions select lists every TASK_CONFIG key, not dispatch seed only (AST-516)."""
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        for tk in admin_mod.get_task_keys():
            assert tk in keys
        assert keys["anticipate_scan"]["entity_type"] == "job"
        assert keys["contemplate_job"]["trigger_state"] == cfg.BUILD_ARTIFACTS_BASE_STATE

    def test_ast549_task_keys_config_derivation_authoritative(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        """Schedulable keys merge dispatch_task_admin_defaults — not removed seed dict (AST-549)."""
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["contemplate_job"]["trigger_state"] == cfg.BUILD_ARTIFACTS_BASE_STATE
        assert keys["parse_job_list"]["entity_type"] == "company"
        assert keys["parse_job_list"]["trigger_state"] == "JOBLIST_IDENTIFIED"
        # AST-739 / AST-747: grade_do catalog row for grouping — not TASK_CONFIG phase/seq.
        assert "phase" not in keys["grade_do"]
        assert "seq" not in keys["grade_do"]
        assert "task_group_name" in keys["grade_do"]

    def test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task_by_key", lambda tk: None)
        monkeypatch.setattr(
            admin_mod.database,
            "list_companies",
            lambda **kwargs: [{"short_name": "acme", "company_name": "Acme Corp"}],
        )
        resp = admin_client.get(
            "/api/admin/adhoc/entities?task_key=select_job_page&candidate_id=c1",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["entities"][0]["id"] == "acme"

    def test_resolve_adhoc_candidate_and_preview_errors(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {
                "agent_id": agent_id, "model_id": "claude-haiku-4-5", "content": "sys", "max_tokens": 5,
            },
        )
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text)
        payload, err = admin_mod._resolve_adhoc({"agent_id": "a1", "task_key": "adhoc"})
        assert err is None
        assert payload["candidate_id"] is None
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        payload, err = admin_mod._resolve_adhoc({"agent_id": "a1", "candidate_id": "c1", "task_key": "craft_resume_base"})
        assert payload["candidate_api_keys"] is None
        assert admin_client.post("/api/admin/adhoc/preview", json={}, headers=auth_headers).status_code == 400
        assert admin_client.post("/api/admin/adhoc/test", json={}, headers=auth_headers).status_code == 400

    def test_adhoc_test_decodes_encoded_payload(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "_resolve_adhoc",
            lambda body: (
                {
                    "system": "s",
                    "user": "u",
                    "cache": "",
                    "nocache": "",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": None,
                    "task_key_uuid": None,
                    "server_id": "anthropic",
                    "tier": {},
                    "candidate_api_keys": None,
                },
                None,
            ),
        )

        async def run_encoded(**kwargs):
            return {"success": True, "parsed_response": "encoded", "timesheet": {}}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_encoded)
        monkeypatch.setattr(admin_mod, "_decode_payload", MagicMock(return_value={"jobs": []}))
        resp = admin_client.post("/api/admin/adhoc/test", json={"agent_id": "a1", "task_key": "grade_do"}, headers=auth_headers)
        assert resp.get_json()["hydrated"] == {"jobs": []}

    def test_backfill_thread_records_error(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        admin_mod._backfill_thread = None
        admin_mod._backfill_status.update(status="idle", message="")
        monkeypatch.setattr(admin_mod, "run_backfill", MagicMock(side_effect=RuntimeError("boom")))
        started = admin_client.post("/api/admin/script/backfill_culture_links", json={"dry_run": False}, headers=auth_headers)
        assert started.get_json()["started"] is True
        if admin_mod._backfill_thread:
            admin_mod._backfill_thread.join(timeout=2)
        assert admin_client.get("/api/admin/script/backfill_culture_links/status", headers=auth_headers).get_json()["status"] == "error"

    def test_dispatch_list_preserves_existing_score_floor(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [{"task_key": "qualify_job_listings", "trigger_state": "PASSED_JOBLIST", "entity_type": "job", "candidate_id": "c1", "score_floor": 2.5}],
        )
        monkeypatch.setattr(admin_mod.database, "count_eligible_for_dispatch_task", lambda row: 1)
        rows = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        assert rows[0]["score_floor"] == 2.5

    def test_update_dispatch_task_score_floor_and_auto_mode_error(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "custom", "trigger_state": "WATCH", "candidate_id": "c1"},
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        ok = admin_client.put("/api/admin/dispatch_tasks/1", json={"score_floor": 2.0}, headers=auth_headers)
        assert ok.status_code == 200
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: "need key")
        bad = admin_client.put("/api/admin/dispatch_tasks/1", json={"auto_mode": True}, headers=auth_headers)
        assert bad.status_code == 400

    def test_build_adhoc_live_content_company_list_website_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "company"})
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {"company_data": {"website_content": [{"url": "u", "content": "page"}]}},
        )
        assert "page" in admin_mod._build_adhoc_live_content("gaze", "acme")

    def test_build_adhoc_live_content_recheck_no_openings_job_site_field(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "company"})
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {"job_site": "https://careers/acme"},
        )
        assert admin_mod._build_adhoc_live_content("recheck_no_openings", "acme") == "https://careers/acme"

    def test_update_dispatch_task_scored_score_floor_and_auto_mode_success(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "qualify_job_listings", "trigger_state": "PASSED_JOBLIST", "candidate_id": "c1"},
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_empty_render_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(admin_mod, "rubric_dispatch_error", lambda candidate_id, task_key: None, raising=False)  # AST-2091
        scored = admin_client.put("/api/admin/dispatch_tasks/1", json={"score_floor": 2.5, "auto_mode": True}, headers=auth_headers)
        assert scored.status_code == 200
        assert update.call_args.kwargs["score_floor"] == 2.5
        assert update.call_args.kwargs["auto_mode"] == 1

    def test_update_dispatch_task_scored_default_score_floor(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "qualify_job_listings", "trigger_state": "PASSED_JOBLIST", "candidate_id": "c1"},
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put("/api/admin/dispatch_tasks/1", json={"score_floor": None}, headers=auth_headers)
        assert resp.status_code == 200
        assert update.call_args.kwargs["score_floor"] == 1.0

    def test_update_dispatch_task_scored_zero_score_floor(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "qualify_job_listings", "trigger_state": "PASSED_JOBLIST", "candidate_id": "c1"},
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put("/api/admin/dispatch_tasks/1", json={"score_floor": 0}, headers=auth_headers)
        assert resp.status_code == 200
        assert update.call_args.kwargs["score_floor"] == 0.0

    def test_update_dispatch_task_unscored_score_floor_null(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"task_key": "custom", "trigger_state": "WATCH", "candidate_id": "c1"},
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put("/api/admin/dispatch_tasks/1", json={"score_floor": None}, headers=auth_headers)
        assert resp.status_code == 200
        assert update.call_args.kwargs["score_floor"] is None

    def test_build_adhoc_live_content_skips_missing_company_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "job"})
        monkeypatch.setitem(admin_mod.TASK_CONFIG, "evaluate_jd", {**admin_mod.TASK_CONFIG["evaluate_jd"], "requires_company": True})
        monkeypatch.setattr(
            admin_mod.database,
            "get_job",
            lambda job_id: {"astral_job_id": job_id, "job_data": {"job_description": "jd"}, "company": "missing"},
        )
        monkeypatch.setattr(admin_mod.database, "get_company", lambda short_name: None)
        assert admin_mod._build_adhoc_live_content("evaluate_jd", "j1") == "[astral_job_id=j1]\njd"

    def test_adhoc_test_hydrates_encoded_payload_with_entities(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "_resolve_adhoc",
            lambda body: (
                {
                    "system": "s",
                    "user": "u",
                    "cache": "",
                    "nocache": "",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": None,
                    "task_key_uuid": None,
                    "server_id": "anthropic",
                    "tier": {},
                    "candidate_api_keys": None,
                },
                None,
            ),
        )

        async def run_encoded(**kwargs):
            return {"success": True, "parsed_response": "encoded", "timesheet": {}}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_encoded)
        decode = MagicMock(return_value={"jobs": [{"astral_job_id": "j1"}]})
        monkeypatch.setattr(admin_mod, "_decode_payload", decode)
        # Isolate hydrate/decode path from real DB: full suite may set _board_search_schema_ensured
        # without board_search on the shared ASTRAL_DB_DIR file (schema ensure side effects).
        monkeypatch.setattr(admin_mod, "_build_adhoc_live_content", lambda *args, **kwargs: "")
        resp = admin_client.post(
            "/api/admin/adhoc/test",
            json={"agent_id": "a1", "task_key": "grade_do", "entity_id": "j1", "entity_ids": ["j1"]},
            headers=auth_headers,
        )
        assert resp.get_json()["hydrated"]["jobs"][0]["astral_job_id"] == "j1"
        decode.assert_called_once()

    def test_adhoc_test_skips_decode_without_response_text(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "_resolve_adhoc",
            lambda body: (
                {
                    "system": "s",
                    "user": "u",
                    "cache": "",
                    "nocache": "",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": None,
                    "task_key_uuid": None,
                    "server_id": "anthropic",
                    "tier": {},
                    "candidate_api_keys": None,
                },
                None,
            ),
        )

        async def run_empty(**kwargs):
            return {"success": True, "parsed_response": "", "timesheet": {}}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_empty)
        resp = admin_client.post("/api/admin/adhoc/test", json={"agent_id": "a1", "task_key": "grade_do"}, headers=auth_headers)
        assert resp.get_json()["hydrated"] is None

    def test_table_copy_upsert_validation_apply_and_errors(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        url = "/api/admin/data/table_copy_upsert"
        assert admin_client.post(url, json={}, headers=auth_headers).status_code == 400
        assert admin_client.post(url, json={"table": "job"}, headers=auth_headers).status_code == 400
        assert admin_client.post(url, json={"table": "job", "json_payload": []}, headers=auth_headers).status_code == 400
        seq = MagicMock(side_effect=[RuntimeError("upsert boom"), {"ok": False, "error": "parse"}, {"ok": True, "rows": 1}])
        monkeypatch.setattr(admin_mod, "apply_copy_output_table_upsert", seq)
        assert admin_client.post(url, json={"table": "job", "json_payload": "[]"}, headers=auth_headers).status_code == 500
        r400 = admin_client.post(url, json={"table": "job", "json_payload": "[]"}, headers=auth_headers)
        assert r400.status_code == 400
        ok = admin_client.post(url, json={"table": "job", "json_payload": "[]"}, headers=auth_headers)
        assert ok.status_code == 200 and ok.get_json().get("ok") is True
        assert seq.call_count == 3


class TestAst725VectorFeedback:
    def test_list_vector_feedback_and_req_dict(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        row = {
            "vector_feedback_id": "vf-1",
            "candidate_id": "c1",
            "batch_id": "b1",
            "task_key": "grade_get",
            "feedback_type": "relevance",
            "value": "A",
            "vector_code": "G1",
        }
        monkeypatch.setattr(admin_mod, "list_vector_feedback", lambda **kwargs: [row])
        plain = admin_client.get("/api/admin/vector_feedback?candidate_id=c1", headers=auth_headers)
        enriched = plain.get_json()[0]
        assert enriched["value_label"] == cfg.RUBRIC_FEEDBACK_CONFIG["value_labels"]["A"]
        shaped = admin_client.get("/api/admin/vector_feedback?req_dict=1", headers=auth_headers)
        body = shaped.get_json()
        assert body["rows"][0]["vector_feedback_id"] == "vf-1"
        assert any(c["key"] == "value_label" for c in body["columns"])
        col_keys = {c["key"] for c in body["columns"]}
        assert {"batch_size", "completed_at"}.issubset(col_keys)

    def test_summary_requires_candidate_and_owner_task_key(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        missing = admin_client.get("/api/admin/vector_feedback/summary", headers=auth_headers)
        assert missing.status_code == 400

    def test_summary_and_task_keys(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        summary_row = {
            "code": "G1",
            "label": "G1",
            "importance": 5,
            "batch_count": 1,
            "feedback_row_count": 3,
            "relevance_dist": "A:1",
            "clarity_dist": "O:1",
            "verdict_dist": "K:1",
        }
        monkeypatch.setattr(admin_mod, "aggregate_vector_feedback_by_vector", lambda cid, owner: [summary_row])
        resp = admin_client.get(
            "/api/admin/vector_feedback/summary?candidate_id=c1&owner_task_key=grade_get&req_dict=1",
            headers=auth_headers,
        )
        body = resp.get_json()
        assert body["rows"][0]["code"] == "G1"
        keys = admin_client.get("/api/admin/vector_feedback/task_keys", headers=auth_headers).get_json()
        assert "grade_get" in keys


class TestAst809VectorFeedbackBatchMetadata:
    def test_list_returns_batch_metadata_fields(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        row = {
            "vector_feedback_id": "vf-809",
            "candidate_id": "c1",
            "batch_id": "batch-809",
            "batch_size": 6,
            "completed_at": "2026-06-25 12:00:00",
            "task_key": "grade_get",
            "feedback_type": "relevance",
            "value": "A",
        }
        monkeypatch.setattr(admin_mod, "list_vector_feedback", lambda **kwargs: [row])
        body = admin_client.get("/api/admin/vector_feedback?req_dict=1", headers=auth_headers).get_json()
        assert body["rows"][0]["batch_size"] == 6
        assert body["rows"][0]["completed_at"] == "2026-06-25 12:00:00"


class TestAst808VectorFeedbackHydration:
    def test_list_enriches_assessment_header_and_columns(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        row = {
            "vector_feedback_id": "vf-808",
            "candidate_id": "c1",
            "batch_id": "b1",
            "task_key": "grade_get",
            "vector_code": "G1",
            "vector_label": "Grade fit",
            "vector_content": "Criterion body",
            "vector_importance": 8,
            "feedback_type": "relevance",
            "value": "A",
        }
        monkeypatch.setattr(admin_mod, "list_vector_feedback", lambda **kwargs: [row])
        body = admin_client.get("/api/admin/vector_feedback?req_dict=1", headers=auth_headers).get_json()
        enriched = body["rows"][0]
        assert enriched["vector_assessment_header"] == "8 - Grade fit (G1)"
        assert enriched["vector_content"] == "Criterion body"
        col_keys = {c["key"] for c in body["columns"]}
        assert {"vector_assessment_header", "vector_content"}.issubset(col_keys)

    def test_rubric_lookup_returns_code_map(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_rubric_vectors",
            lambda cid, owner, current_only=True: [
                {"code": "G1", "label": "Grade fit", "content": "Body", "importance": 5},
            ],
        )
        body = admin_client.get(
            "/api/admin/vector_feedback/rubric_lookup?candidate_id=c1&owner_task_key=grade_get",
            headers=auth_headers,
        ).get_json()
        assert body["G1"]["label"] == "Grade fit"
        assert body["G1"]["content"] == "Body"

    def test_hydrate_reviews_endpoint(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "_rubric_lookup_by_code",
            lambda cid, owner: {
                "G1": {"label": "Grade fit", "content": "Criterion body", "importance": 5},
            },
        )
        resp = admin_client.post(
            "/api/admin/vector_feedback/hydrate_reviews",
            json={
                "candidate_id": "c1",
                "owner_task_key": "grade_get",
                "vector_reviews": ["G1RACOVK"],
            },
            headers=auth_headers,
        )
        rows = resp.get_json()["rows"]
        assert len(rows) == 1
        assert rows[0]["code"] == "G1"
        assert rows[0]["label"] == "Grade fit"
        assert "Criterion body" in rows[0]["content"]


class TestAst783RepoJsonApi:
    def test_repo_json_status_returns_divergence_map(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "get_repo_admin_json_divergence_status",
            lambda: {
                "agent": {"diverged": True, "repo_relative_path": "data/admin/agent.json"},
                "agent_task": {"diverged": False, "repo_relative_path": "data/admin/agent_task.json"},
            },
        )
        resp = admin_client.get("/api/admin/repo_json/status", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["agent"]["diverged"] is True
        assert body["agent_task"]["diverged"] is False

    def test_repo_json_status_surfaces_core_errors(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def _boom() -> dict:
            raise RuntimeError("repo admin JSON missing")

        monkeypatch.setattr(admin_mod, "get_repo_admin_json_divergence_status", _boom)
        resp = admin_client.get("/api/admin/repo_json/status", headers=auth_headers)
        assert resp.status_code == 500
        assert "missing" in resp.get_json()["error"]

    def test_repo_json_revert_invalid_table_key(
        self, admin_client: FlaskClient, auth_headers: dict[str, str],
    ) -> None:
        resp = admin_client.post("/api/admin/repo_json/revert/nope", headers=auth_headers)
        assert resp.status_code == 400
        assert "agent or agent_task" in resp.get_json()["error"]

    def test_repo_json_revert_success(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(admin_mod, "revert_repo_admin_json_table", lambda key: 4 if key == "agent" else 9)
        resp = admin_client.post("/api/admin/repo_json/revert/agent", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        assert body["table_key"] == "agent"
        assert body["row_count"] == 4


class TestAst875DispatchTasksSetFromTemplate:
    """AST-875: admin counts + set_from_template endpoints (no run_task)."""

    def test_dispatch_task_counts(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "count_dispatch_tasks_by_candidate", lambda: {"somerset": 3, "other": 1})
        resp = admin_client.get("/api/admin/dispatch_tasks/counts", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"counts": {"somerset": 3, "other": 1}}

    def test_set_from_template_success_and_errors(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        run = MagicMock()
        monkeypatch.setattr(admin_mod, "run_task", run, raising=False)
        monkeypatch.setattr(
            admin_mod,
            "set_candidate_dispatch_tasks_from_template",
            lambda candidate_id: {
                "candidate_id": candidate_id,
                "template_candidate_id": "somerset",
                "inserted": 2,
                "updated": 1,
                "deleted": 0,
                "count": 3,
            },
        )
        ok = admin_client.post(
            "/api/admin/dispatch_tasks/set_from_template",
            json={"candidate_id": "tgt"},
            headers=auth_headers,
        )
        assert ok.status_code == 200
        body = ok.get_json()
        assert body["candidate_id"] == "tgt"
        assert body["template_candidate_id"] == "somerset"
        assert body["count"] == 3
        run.assert_not_called()

        bad = admin_client.post(
            "/api/admin/dispatch_tasks/set_from_template",
            json={"candidate_id": "  "},
            headers=auth_headers,
        )
        assert bad.status_code == 400
        assert "candidate_id" in bad.get_json()["error"]

        def _missing(candidate_id: str):
            raise LookupError(f"Candidate not found: {candidate_id}")

        monkeypatch.setattr(admin_mod, "set_candidate_dispatch_tasks_from_template", _missing)
        missing = admin_client.post(
            "/api/admin/dispatch_tasks/set_from_template",
            json={"candidate_id": "nope"},
            headers=auth_headers,
        )
        assert missing.status_code == 404
        assert "nope" in missing.get_json()["error"]

        def _bad_value(candidate_id: str):
            raise ValueError("ASTRAL_CONFIG template_candidate_id is empty")

        monkeypatch.setattr(admin_mod, "set_candidate_dispatch_tasks_from_template", _bad_value)
        ve = admin_client.post(
            "/api/admin/dispatch_tasks/set_from_template",
            json={"candidate_id": "tgt"},
            headers=auth_headers,
        )
        assert ve.status_code == 400


# AST-955: Save accepts registered TASK_CONFIG keys (picker catalog), not schedulable-only.
class TestAst955AlignScheduledActionsSave:
    def test_helper_accepts_check_cover_letter(self) -> None:
        assert (
            admin_mod._dispatch_task_key_trigger_error("check_cover_letter", "CANDIDATE_REVIEW")
            is None
        )

    def test_helper_unknown_task_key_wording(self) -> None:
        err = admin_mod._dispatch_task_key_trigger_error("not_a_registered_task_key", "NEW")
        assert err is not None
        assert "Unknown task_key" in err
        assert "non-schedulable" not in err

    def test_helper_retired_consult_still_blocked(self) -> None:
        err = admin_mod._dispatch_task_key_trigger_error("consult_do", "PASSED_JD")
        assert err is not None and "retired" in err

    def test_create_check_cover_letter_201(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        save = MagicMock(return_value=77)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "somerset",
                "task_key": "check_cover_letter",
                "trigger_state": "CANDIDATE_REVIEW",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert "non-schedulable" not in (resp.get_json() or {}).get("error", "")
        assert save.call_args.kwargs["task_key"] == "check_cover_letter"
        assert save.call_args.kwargs["trigger_state"] == "CANDIDATE_REVIEW"

    def test_create_check_job_resume_regression(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        save = MagicMock(return_value=78)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "somerset",
                "task_key": "check_job_resume",
                "trigger_state": cfg.BUILD_ARTIFACTS_BASE_STATE,
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert save.call_args.kwargs["task_key"] == "check_job_resume"

    def test_update_task_key_to_check_cover_letter(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "candidate_id": "somerset",
                "auto_mode": 0,
            },
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"task_key": "check_cover_letter", "trigger_state": "CANDIDATE_REVIEW"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        kw = update.call_args.kwargs
        assert kw["task_key"] == "check_cover_letter"
        assert kw["entity_type"] == "job"
        assert kw["sort_by"] == cfg.dispatch_task_admin_defaults(
            "check_cover_letter", trigger_state="CANDIDATE_REVIEW"
        )["sort_by"]


# AST-960: no frozenset merge. AST-1214: live agent_task ∪ TASK_CONFIG ∪ dispatch orphans.
class TestAst960TaskKeysNoFrozensetInventory:
    def test_grade_do_form_meta_still_derived(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        monkeypatch.setattr(admin_mod.database, "list_candidate_tasks", lambda: [])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["grade_do"]["entity_type"] == "job"
        assert keys["grade_do"]["trigger_state"] == "PASSED_JD"

    def test_check_cover_letter_form_meta_keeps_task_config_fields(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        monkeypatch.setattr(admin_mod.database, "list_candidate_tasks", lambda: [])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert "check_cover_letter" in keys
        # Mid-chain: no default trigger rule — form meta falls through to TASK_CONFIG fields.
        assert keys["check_cover_letter"]["entity_type"] == "job"

    def test_agent_task_only_keys_present_non_agent_gaps_absent(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Eight live agent_task-only keys in picker; prefilter / inflow_resolve_website stay out
        # (not agent_task keys — writer may still accept them if POSTed).
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": tk} for tk in _AST1214_AGENT_TASK_ONLY_KEYS],
        )
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        for tk in _AST1214_AGENT_TASK_ONLY_KEYS:
            assert tk in keys
        assert "prefilter" not in keys
        assert "inflow_resolve_website" not in keys


# AST-986: Admin POST /session_resume/parse — thin delegate; no candidate write in route.
# AST-1880: forwards the selected candidate_id (stripped; "" when absent) so core uses that candidate's key.
class TestAst986SessionResumeParseApi:
    def test_requires_admin(
        self, admin_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = admin_client.post(
            "/api/admin/session_resume/parse",
            json={"resume_text": "x"},
            headers=non_admin_headers,
        )
        assert resp.status_code == 403

    def test_empty_body_and_non_string_resume_text_delegate_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[tuple[str, bool]] = []

        def _fake(resume_text: str, *, candidate_id: str, debug: bool = False) -> tuple[dict[str, Any], int]:
            calls.append((resume_text, candidate_id, debug))
            return ({"success": False, "error": "resume_text is required"}, 400)

        monkeypatch.setattr(admin_mod, "run_session_resume_parse", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        empty = admin_client.post("/api/admin/session_resume/parse", json={}, headers=auth_headers)
        assert empty.status_code == 400
        assert empty.get_json()["success"] is False
        non_str = admin_client.post(
            "/api/admin/session_resume/parse",
            json={"resume_text": 99},
            headers=auth_headers,
        )
        assert non_str.status_code == 400
        assert calls == [("", "", False), ("", "", False)]

    def test_no_json_body_uses_empty_dict(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[str] = []

        def _fake(resume_text: str, *, candidate_id: str, debug: bool = False) -> tuple[dict[str, Any], int]:
            calls.append((resume_text, candidate_id))
            return ({"success": False, "error": "resume_text is required"}, 400)

        monkeypatch.setattr(admin_mod, "run_session_resume_parse", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        resp = admin_client.post(
            "/api/admin/session_resume/parse",
            data="not-json",
            content_type="text/plain",
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert calls == [("", "")]

    def test_success_forwards_debug_and_body(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, Any] = {}

        def _fake(resume_text: str, *, candidate_id: str, debug: bool = False) -> tuple[dict[str, Any], int]:
            captured["resume_text"] = resume_text
            captured["candidate_id"] = candidate_id
            captured["debug"] = debug
            return (
                {
                    "success": True,
                    "resume_structure": {"sections": {}},
                    "base_resume": {"experience": "x"},
                    "parsed_response": {"experience": "x"},
                    "batch_id": "user-session-parse-resume-1",
                    "timesheet": {},
                },
                200,
            )

        monkeypatch.setattr(admin_mod, "run_session_resume_parse", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: True)
        resp = admin_client.post(
            "/api/admin/session_resume/parse",
            json={"resume_text": "paste block", "candidate_id": " cand-7 "},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["base_resume"]["experience"] == "x"
        assert captured == {"resume_text": "paste block", "candidate_id": "cand-7", "debug": True}

    def test_failure_status_passthrough(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "run_session_resume_parse",
            lambda resume_text, *, candidate_id, debug=False: (
                {"success": False, "error": "agent down", "batch_id": "b1"},
                500,
            ),
        )
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        resp = admin_client.post(
            "/api/admin/session_resume/parse",
            json={"resume_text": "paste"},
            headers=auth_headers,
        )
        assert resp.status_code == 500
        assert resp.get_json()["success"] is False
        assert resp.get_json()["error"] == "agent down"


# AST-987: Admin POST /session_resume/html — in-memory structure → text/html.
class TestAst987SessionResumeHtmlApi:
    def test_requires_admin(
        self, admin_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = admin_client.post(
            "/api/admin/session_resume/html",
            json={"resume_structure": {"sections": {}}, "base_resume": {"x": "y"}},
            headers=non_admin_headers,
        )
        assert resp.status_code == 403

    def test_400_when_structure_or_content_missing(
        self, admin_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        bad = admin_client.post(
            "/api/admin/session_resume/html",
            json={},
            headers=auth_headers,
        )
        assert bad.status_code == 400
        assert bad.get_json()["success"] is False
        non_obj = admin_client.post(
            "/api/admin/session_resume/html",
            json={"resume_structure": [], "base_resume": {}},
            headers=auth_headers,
        )
        assert non_obj.status_code == 400

    def test_400_on_builder_value_error(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "build_session_base_resume",
            MagicMock(side_effect=ValueError("base_resume content is required")),
        )
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        resp = admin_client.post(
            "/api/admin/session_resume/html",
            json={"resume_structure": {"sections": {}}, "base_resume": {"a": "b"}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "base_resume content is required"

    def test_200_returns_html(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, Any] = {}

        def _fake(structure: dict, content: dict, *, debug: bool = False) -> str:
            captured["structure"] = structure
            captured["content"] = content
            captured["debug"] = debug
            return "<html><body>session</body></html>"

        monkeypatch.setattr(admin_mod, "build_session_base_resume", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: True)
        resp = admin_client.post(
            "/api/admin/session_resume/html",
            json={
                "resume_structure": {"sections": {"experience": {"id": "experience"}}},
                "base_resume": {"experience": "Jobs"},
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.mimetype == "text/html"
        assert b"session" in resp.data
        assert captured["debug"] is True
        assert captured["content"]["experience"] == "Jobs"


# AST-1024: Admin POST /session_cover_letter/html — in-memory fields → text/html.
class TestAst1024SessionCoverLetterHtmlApi:
    def _payload(self, **overrides: Any) -> dict[str, Any]:
        body: dict[str, Any] = {
            "from_block": "Susan Somerset",
            "letter_date": "July 27, 2026",
            "to_block": "",
            "subject": "",
            "letter": "Dear Team,\n\nThanks.",
            "signoff_closing": "Best,",
            "signature": "Susan Somerset",
        }
        body.update(overrides)
        return body

    def test_requires_admin(
        self, admin_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = admin_client.post(
            "/api/admin/session_cover_letter/html",
            json=self._payload(),
            headers=non_admin_headers,
        )
        assert resp.status_code == 403

    def test_400_when_body_not_object(
        self, admin_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = admin_client.post(
            "/api/admin/session_cover_letter/html",
            json=["not", "an", "object"],
            headers=auth_headers,
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False
        assert "JSON object" in body["error"]

    def test_400_on_builder_value_error(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "build_session_cover_letter",
            MagicMock(side_effect=ValueError("from_block is required")),
        )
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        resp = admin_client.post(
            "/api/admin/session_cover_letter/html",
            json=self._payload(from_block=""),
            headers=auth_headers,
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False
        assert body["error"] == "from_block is required"

    def test_200_returns_html_fields_from_config_keys(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured: dict[str, Any] = {}

        def _fake(
            fields: dict, *, candidate_id: str | None = None, debug: bool = False
        ) -> str:
            captured["fields"] = fields
            captured["candidate_id"] = candidate_id
            captured["debug"] = debug
            return "<html><body>session-cover</body></html>"

        monkeypatch.setattr(admin_mod, "build_session_cover_letter", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: True)
        field_keys = set(cfg.BUILD_CONFIG["session_cover_letter"]["fields"])
        resp = admin_client.post(
            "/api/admin/session_cover_letter/html",
            json={
                **self._payload(letter="Hello cover"),
                "candidate_id": None,
                "noise_key": "should-not-reach-fields",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.mimetype == "text/html"
        assert b"session-cover" in resp.data
        assert captured["debug"] is True
        assert captured["candidate_id"] is None
        assert set(captured["fields"]) == field_keys
        assert "noise_key" not in captured["fields"]
        assert captured["fields"]["letter"] == "Hello cover"

    def test_blank_candidate_id_becomes_none(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured: dict[str, Any] = {}

        def _fake(
            fields: dict, *, candidate_id: str | None = None, debug: bool = False
        ) -> str:
            captured["candidate_id"] = candidate_id
            return "<html>ok</html>"

        monkeypatch.setattr(admin_mod, "build_session_cover_letter", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        resp = admin_client.post(
            "/api/admin/session_cover_letter/html",
            json=self._payload(candidate_id="  "),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert captured["candidate_id"] is None

    def test_forwards_candidate_id(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured: dict[str, Any] = {}

        def _fake(
            fields: dict, *, candidate_id: str | None = None, debug: bool = False
        ) -> str:
            captured["candidate_id"] = candidate_id
            return "<html>ok</html>"

        monkeypatch.setattr(admin_mod, "build_session_cover_letter", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        resp = admin_client.post(
            "/api/admin/session_cover_letter/html",
            json=self._payload(candidate_id="cand-9"),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert captured["candidate_id"] == "cand-9"

    def test_non_string_candidate_id_ignored(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured: dict[str, Any] = {}

        def _fake(
            fields: dict, *, candidate_id: str | None = None, debug: bool = False
        ) -> str:
            captured["candidate_id"] = candidate_id
            return "<html>ok</html>"

        monkeypatch.setattr(admin_mod, "build_session_cover_letter", _fake)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        resp = admin_client.post(
            "/api/admin/session_cover_letter/html",
            json=self._payload(candidate_id=123),
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert captured["candidate_id"] is None


# AST-1214: live alphabetical Admin catalog + first-class write / mailbox fold.
class TestAst1214AdminCatalogAlphabeticalWritable:
    def test_catalog_keys_alphabetical_and_mailbox_form_meta(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": tk} for tk in _AST1214_AGENT_TASK_ONLY_KEYS],
        )
        resp = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers)
        assert resp.status_code == 200
        # Raw body order is the contract (sorted(membership)), not only Flask jsonify sorting.
        raw_keys = list(resp.get_json().keys())
        assert raw_keys == sorted(raw_keys)
        keys = resp.get_json()
        assert keys["parse_meteorite_email"]["entity_type"] == "candidate"
        assert keys["parse_meteorite_email"]["trigger_state"] == ""
        assert keys["fetch_jd"]["entity_type"] == "job"
        assert keys["fetch_jd"]["trigger_state"] == "PASSED_JOBLIST"

    def test_mailbox_trigger_null_only_and_unsupported_craft_wording(self) -> None:
        for tk in ("parse_meteorite_email", "stage_email_meteorite"):
            assert admin_mod._dispatch_task_key_trigger_error(tk, None) is None
            assert admin_mod._dispatch_task_key_trigger_error(tk, "") is None
            bad = admin_mod._dispatch_task_key_trigger_error(tk, "ACTIVE_SEARCH")
            assert bad is not None and "mailbox poller" in bad
        # Registered TASK_CONFIG without entity helper → unsupported, not Unknown.
        craft_err = admin_mod._dispatch_task_key_trigger_error("craft_do_rubric", "NEW")
        assert craft_err is not None and "unsupported entity_type" in craft_err
        assert "Unknown task_key" not in craft_err

    def test_post_fetch_jd_and_parse_meteorite_email_create(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        save = MagicMock(side_effect=[71, 72])
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        fetch = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "fetch_jd",
                "trigger_state": "PASSED_JOBLIST",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert fetch.status_code == 201
        assert fetch.get_json()["id"] == 71
        mailbox = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "parse_meteorite_email",
                "trigger_state": None,
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert mailbox.status_code == 201
        assert mailbox.get_json()["id"] == 72
        assert save.call_count == 2

    def test_list_dtasks_meteorite_mailbox_avail_without_extra_mailbox_row(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # need_gaze_counts + per-row stamp must fire for mailbox keys without a legacy gaze row.
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "id": 1,
                    "task_key": "parse_meteorite_email",
                    "trigger_state": None,
                    "entity_type": "candidate",
                    "candidate_id": "A",
                    "score_floor": None,
                },
                {
                    "id": 2,
                    "task_key": "scan_jobs",
                    "trigger_state": "NEW",
                    "entity_type": "job",
                    "candidate_id": "c1",
                    "score_floor": None,
                },
            ],
        )
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        monkeypatch.setattr(
            admin_mod,
            "admin_always_visible_under_avail_gt0_dispatch_task_keys",
            lambda: frozenset(),
        )
        bound = MagicMock(return_value={"A": 3})
        monkeypatch.setattr(admin_mod, "count_inbox_bound_by_candidate", bound)
        monkeypatch.setattr(
            admin_mod.database,
            "count_eligible_for_dispatch_task",
            lambda row: 9,
        )
        rows = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        by = {r["id"]: r for r in rows}
        assert by[1]["available_count"] == 3
        assert by[2]["available_count"] == 9
        bound.assert_called_once_with()


# Branches: adhoc/test success body via _caller_response_blob (dict/list JSON vs
# plain str vs empty {}/[]; extract agent_payload vs whole parsed; 500 on fail).
class TestAst1394AdhocTestResponseText:
    """AST-1394: POST /api/admin/adhoc/test returns serialized body as str."""

    def _patch_resolve(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "_resolve_adhoc",
            lambda _body: (
                {
                    "system": "s",
                    "user": "u",
                    "cache": "c",
                    "nocache": "n",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": "c1",
                    "task_key_uuid": None,
                    "server_id": "anthropic",
                    "tier": {},
                    "candidate_api_keys": None,
                },
                None,
            ),
        )

    def _post_ok(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
        parsed: Any,
        *,
        task_key: str = "evaluate_jd",
    ) -> Any:
        async def run_ok(**_k: Any) -> dict[str, Any]:
            return {"success": True, "parsed_response": parsed, "timesheet": {}}

        self._patch_resolve(monkeypatch)
        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_ok)
        return admin_client.post(
            "/api/admin/adhoc/test",
            json={"agent_id": "a1", "task_key": task_key},
            headers=auth_headers,
        )

    @pytest.mark.parametrize(
        "parsed, expected",
        [
            (
                {
                    "agent_performance": {"status": "success"},
                    "agent_payload": {"search_terms": "alpha\nbeta"},
                },
                json.dumps({"search_terms": "alpha\nbeta"}, ensure_ascii=False, default=str),
            ),
            ({"agent_payload": {}}, "{}"),
            ({"agent_payload": []}, "[]"),
            ({"agent_payload": "payload"}, "payload"),
            ("plain ok", "plain ok"),
            (123, "123"),
        ],
        ids=[
            "object-payload",
            "empty-dict",
            "empty-list",
            "str-payload",
            "plain-text",
            "numeric",
        ],
    )
    def test_success_response_text_is_serialized_str(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
        parsed: Any,
        expected: str,
    ) -> None:
        resp = self._post_ok(admin_client, auth_headers, monkeypatch, parsed)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert isinstance(body["response_text"], str)
        assert body["response_text"] == expected

    def test_failure_stays_500_without_success_body(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def run_fail(**_k: Any) -> dict[str, Any]:
            return {"success": False, "error": "nope"}

        self._patch_resolve(monkeypatch)
        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_fail)
        resp = admin_client.post(
            "/api/admin/adhoc/test",
            json={"agent_id": "a1", "task_key": "evaluate_jd"},
            headers=auth_headers,
        )
        assert resp.status_code == 500
        body = resp.get_json()
        assert body["success"] is False
        assert "response_text" not in body
        assert body["error"] == "nope"


# Branches: seven-segment _resolve_adhoc / Preview keys; empty System → agent content
# when the editor sends the key; omitted key keeps the DB task system; Test forwards
# cache_b–d and returns batch_id on 200 and soft-fail 500.
class TestAst1411AdhocSevenSegment:
    """AST-1411: Ad Hoc preview/test seven-segment resolve + Test identity."""

    def _stub_agent(self, monkeypatch: pytest.MonkeyPatch, *, content: str = "agent-sys", task_system: str = "task-sys") -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {
                "agent_id": agent_id,
                "content": content,
                "model_id": "claude-haiku-4-5",
                "max_tokens": 10,
            },
        )
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent_task",
            lambda _task_key: {"task_key_uuid": "uuid-1411", "system_prompt": task_system},
        )
        # Cache/user slots resolve in api_admin; system uses agent.resolved_task_system (no tokens here).
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text)

    def test_resolve_preview_seven_segment_and_system_fallback(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._stub_agent(monkeypatch)
        save_ad = MagicMock()
        monkeypatch.setattr(admin_mod.database, "save_agent_data", save_ad)

        seven = {
            "agent_id": "a1",
            "task_key": "evaluate_jd",
            "system_prompt": "sys-ed",
            "cache_prompt": "A",
            "cache_prompt_c": "C",
            "user_prompt": "U",
        }
        payload, err = admin_mod._resolve_adhoc(seven)
        assert err is None
        assert payload["system"] == "sys-ed"
        assert payload["cache"] == payload["cache_a"] == "A"
        assert payload["cache_c"] == "C"
        assert payload["cache_b"] == payload["cache_d"] == ""
        assert payload["user"] == "U"

        preview = admin_client.post("/api/admin/adhoc/preview", json=seven, headers=auth_headers)
        body = preview.get_json()
        assert preview.status_code == 200
        assert body["cache"] == body["cache_a"] == "A"
        assert body["cache_c"] == "C"
        assert body["cache_b"] == body["cache_d"] == ""
        assert body["system"] == "sys-ed"
        save_ad.assert_not_called()

        # Empty editor System still sends agent content (production fallback). Omitted key keeps the task row.
        empty_sys, err = admin_mod._resolve_adhoc(
            {"agent_id": "a1", "task_key": "evaluate_jd", "system_prompt": ""}
        )
        assert err is None
        assert empty_sys["system"] == "agent-sys"
        omitted, err = admin_mod._resolve_adhoc({"agent_id": "a1", "task_key": "evaluate_jd"})
        assert err is None
        assert omitted["system"] == "task-sys"

    def test_adhoc_test_forwards_caches_and_returns_batch_id(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, Any] = {}

        monkeypatch.setattr(
            admin_mod,
            "_resolve_adhoc",
            lambda _body: (
                {
                    "system": "s",
                    "user": "u",
                    "cache": "A",
                    "cache_a": "A",
                    "cache_b": "",
                    "cache_c": "C",
                    "cache_d": "",
                    "nocache": "",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": "c1",
                    "task_key_uuid": None,
                    "server_id": "anthropic",
                    "tier": {},
                    "candidate_api_keys": None,
                },
                None,
            ),
        )

        async def run_ok(**kwargs: Any) -> dict[str, Any]:
            captured.update(kwargs)
            return {
                "success": True,
                "parsed_response": {"agent_payload": "ok"},
                "timesheet": {},
                "batch_id": "adhoc-evaluate_jd-1411",
            }

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_ok)
        ok = admin_client.post(
            "/api/admin/adhoc/test",
            json={"agent_id": "a1", "task_key": "evaluate_jd"},
            headers=auth_headers,
        )
        assert ok.status_code == 200
        assert ok.get_json()["batch_id"] == "adhoc-evaluate_jd-1411"
        assert captured["cache_content"] == "A"
        assert captured["cache_content_c"] == "C"
        assert captured["cache_content_b"] is None
        assert captured["cache_content_d"] is None

        async def run_fail(**_k: Any) -> dict[str, Any]:
            return {"success": False, "error": "nope", "batch_id": "adhoc-evaluate_jd-1411"}

        monkeypatch.setattr(admin_mod, "run_adhoc_workbench_test", run_fail)
        failed = admin_client.post(
            "/api/admin/adhoc/test",
            json={"agent_id": "a1", "task_key": "evaluate_jd"},
            headers=auth_headers,
        )
        assert failed.status_code == 500
        fail_body = failed.get_json()
        assert fail_body["success"] is False
        assert fail_body["batch_id"] == "adhoc-evaluate_jd-1411"
        assert "response_text" not in fail_body


# AST-1412: Ad Hoc overwrite ● / has-content reads seven *_len fields from _enrich_tasks.
_LEN_KEYS = (
    "user_prompt_len",
    "cache_prompt_len",
    "cache_prompt_b_len",
    "cache_prompt_c_len",
    "cache_prompt_d_len",
    "nocache_prompt_len",
    "system_prompt_len",
)


class TestAst1412EnrichTaskLens:
    def test_enrich_tasks_passes_seven_segment_lens_including_cache_b_only(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [
                {
                    "task_key": "task_b_only",
                    "task_key_uuid": None,
                    "agent_id": "",
                    "cache_prompt_len": 0,
                    "cache_prompt_b_len": 9,
                    "cache_prompt_c_len": 0,
                    "cache_prompt_d_len": 0,
                    "nocache_prompt_len": 0,
                    "user_prompt_len": 0,
                    "system_prompt_len": 0,
                    "updated_at": "now",
                }
            ],
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: None)
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        rows = admin_mod._enrich_tasks("")
        for key in _LEN_KEYS:
            assert key in rows[0]
            assert isinstance(rows[0][key], int)
        assert rows[0]["cache_prompt_b_len"] == 9
        assert rows[0]["cache_prompt_len"] == 0
        assert rows[0]["system_prompt_len"] == 0


class TestAst1451AdhocRuns:
    """AST-1451 (revised AST-1534): GET /api/admin/adhoc/runs admin-auth; debug via ui_llm_debug."""

    _ROWS = [
        {
            "batch_id": "b1",
            "created_at": "2026-08-01 12:00:00",
            "entity_id": "job-1",
            "task_key": "evaluate_jd",
        },
        {
            "batch_id": "b2",
            "created_at": "2026-07-01 00:00:00",
            "entity_id": None,
            "task_key": "adhoc-evaluate_jd",
        },
    ]

    def test_admin_returns_json_array_and_forwards_debug(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        seen: list[bool] = []

        def _list(*, debug: bool = False, **_kw) -> list[dict[str, Any]]:
            seen.append(debug)
            return list(self._ROWS)

        monkeypatch.setattr(admin_mod, "list_agent_data_runs", _list)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: True)
        resp = admin_client.get("/api/admin/adhoc/runs", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == self._ROWS
        assert seen == [True]

    def test_unauthenticated_401(self, admin_client: FlaskClient) -> None:
        assert admin_client.get("/api/admin/adhoc/runs").status_code == 401

    def test_non_admin_403(
        self, admin_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = admin_client.get("/api/admin/adhoc/runs", headers=non_admin_headers)
        assert resp.status_code == 403


class TestAst1534AdhocRunsScoped:
    """AST-1534: query params + config cap; blank candidate → []; ignore client limit."""

    def test_forwards_candidate_task_and_config_limit(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        seen: list[dict[str, Any]] = []

        def _list(**kw) -> list[dict[str, Any]]:
            seen.append(kw)
            return [
                {
                    "batch_id": "b1",
                    "created_at": "2026-08-01 12:00:00",
                    "entity_id": "job-1",
                    "task_key": "adhoc-evaluate_jd",
                }
            ]

        monkeypatch.setattr(admin_mod, "list_agent_data_runs", _list)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        monkeypatch.setitem(admin_mod.UI_CONFIG, "adhoc_import_runs_limit", 10)
        resp = admin_client.get(
            "/api/admin/adhoc/runs?candidate_id=cand-1&task_key=evaluate_jd&limit=999",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()[0]["batch_id"] == "b1"
        assert seen == [
            {
                "candidate_id": "cand-1",
                "task_key": "evaluate_jd",
                "limit": 10,
                "debug": False,
            }
        ]

    def test_blank_candidate_passes_none(
        self,
        admin_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        seen: list[dict[str, Any]] = []

        def _list(**kw) -> list[dict[str, Any]]:
            seen.append(kw)
            return []

        monkeypatch.setattr(admin_mod, "list_agent_data_runs", _list)
        monkeypatch.setattr(admin_mod, "ui_llm_debug", lambda: False)
        monkeypatch.setitem(admin_mod.UI_CONFIG, "adhoc_import_runs_limit", 10)
        resp = admin_client.get("/api/admin/adhoc/runs", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []
        assert seen[0]["candidate_id"] is None
        assert seen[0]["task_key"] is None
        assert seen[0]["limit"] == 10


# AST-1618: admin create/update persist explicit entity_type + sort for chosen entity.
class TestAst1618PersistEntityTypeAdmin:
    def test_trigger_error_honors_entity_override(self) -> None:
        # grade_do catalog is job; company WEBSITE_FOUND is valid only with override
        assert (
            admin_mod._dispatch_task_key_trigger_error(
                "grade_do", "WEBSITE_FOUND", entity_type="company"
            )
            is None
        )
        bad = admin_mod._dispatch_task_key_trigger_error(
            "grade_do", "WEBSITE_FOUND", entity_type="job"
        )
        assert bad is not None and "grade_do" in bad
        unsupported = admin_mod._dispatch_task_key_trigger_error(
            "grade_do", "NEW", entity_type="not_an_entity"
        )
        assert unsupported is not None and "unsupported entity_type" in unsupported

    def test_create_forwards_entity_type(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        save = MagicMock(return_value=1618)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "grade_do",
                "trigger_state": "WATCH",
                "entity_type": "company",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert save.call_args.kwargs["entity_type"] == "company"
        assert save.call_args.kwargs["trigger_state"] == "WATCH"

    def test_create_rejects_entity_trigger_mismatch(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        save = MagicMock(return_value=1)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "grade_do",
                "trigger_state": "WATCH",
                "entity_type": "job",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "grade_do" in resp.get_json()["error"]
        save.assert_not_called()

    def test_create_rejects_empty_and_unknown_entity(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        empty = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "entity_type": "  ",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert empty.status_code == 400
        assert "non-empty" in empty.get_json()["error"]
        unknown = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "entity_type": "board_search",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert unknown.status_code == 400
        assert "unsupported entity_type" in unknown.get_json()["error"]

    def test_update_entity_type_without_task_key(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "entity_type": "job",
                "candidate_id": "c1",
                "auto_mode": 0,
                "sort_by": "latest_score",
            },
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        # Keep trigger; switch entity to company with a company-valid trigger
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"entity_type": "company", "trigger_state": "WATCH"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        kw = update.call_args.kwargs
        assert kw["entity_type"] == "company"
        assert kw["sort_by"] == cfg._dispatch_sort_by_for("company", "WATCH")
        assert "task_key" not in kw

    def test_update_rejects_mismatched_entity_trigger(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "entity_type": "job",
                "candidate_id": "c1",
                "auto_mode": 0,
            },
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"entity_type": "company"},  # PASSED_JD not in company registry
            headers=auth_headers,
        )
        assert resp.status_code == 400
        update.assert_not_called()

    def test_update_null_entity_type_treated_as_omit(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "grade_do",
                "trigger_state": "PASSED_JD",
                "entity_type": "job",
                "candidate_id": "c1",
                "auto_mode": 0,
            },
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"entity_type": None, "min_count": 3},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        kw = update.call_args.kwargs
        assert kw["min_count"] == 3
        assert "entity_type" not in kw


class TestAst1623AdminMeteoriteStateOptionsAvail:
    """AST-1623: state_options meteorite + Available without candidate_id short-circuit."""

    def test_state_options_includes_meteorite(
        self, admin_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        from src.utils.config import METEORITE_STATES, dispatch_entity_state_registry

        states = admin_client.get("/api/admin/dispatch_tasks/state_options", headers=auth_headers).get_json()
        assert "meteorite" in states
        assert set(states["meteorite"]) == set(METEORITE_STATES)
        assert states["meteorite"] == list(dispatch_entity_state_registry("meteorite").keys())
        # Existing keys stay present (order not rebuilt from ENTITY_TYPES).
        assert "job" in states and "company" in states and "candidate" in states

    def test_list_dtasks_meteorite_avail_without_candidate_id(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod,
            "list_dispatch_tasks",
            lambda: [
                {
                    "id": 1,
                    "task_key": "stage_meteorite",
                    "trigger_state": "NEW",
                    "entity_type": "meteorite",
                    "candidate_id": None,
                    "score_floor": None,
                },
                {
                    "id": 2,
                    "task_key": "grade_do",
                    "trigger_state": "PASSED_JD",
                    "entity_type": "job",
                    "candidate_id": None,
                    "score_floor": None,
                },
                {
                    "id": 3,
                    "task_key": "scrape_meteorite",
                    "trigger_state": "SCRAPE_LINK",
                    "entity_type": "meteorite",
                    "candidate_id": "c-x",
                    "score_floor": None,
                },
            ],
        )
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())

        def count(row: dict[str, Any]) -> int:
            return 7 if row.get("entity_type") == "meteorite" else 3

        monkeypatch.setattr(admin_mod.database, "count_eligible_for_dispatch_task", count)
        rows = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        by = {r["id"]: r for r in rows}
        assert by[1]["available_count"] == 7
        assert by[2]["available_count"] == 0  # job still requires candidate_id
        assert by[3]["available_count"] == 7

    def test_create_accepts_meteorite_entity_type(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        save = MagicMock(return_value=1623)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "grade_do",
                "trigger_state": "NEW",
                "entity_type": "meteorite",
                "min_count": 1,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert save.call_args.kwargs["entity_type"] == "meteorite"
        assert save.call_args.kwargs["trigger_state"] == "NEW"


# Branches: list empty_render + force AUTO off; create/PUT/run 400 gates; pass when helper clear.
class TestAst1780EmptyRenderListGatesForceOff:
    """AST-1780: list enrich empty_render, AUTO/Run 400 gates, force AUTO off."""

    @pytest.fixture(autouse=True)
    def _rubric_ok(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-2091: rubric gate is a separate reason source; keep these on the token/key paths.
        monkeypatch.setattr(admin_mod, "rubric_dispatch_error", lambda cid, tk: None, raising=False)

    def test_list_sets_empty_render_and_forces_auto_off(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [
            {
                "id": 7,
                "task_key": "qualify_job_listings",
                "trigger_state": "NEW",
                "entity_type": "job",
                "candidate_id": "c1",
                "score_floor": None,
                "auto_mode": 1,
            }
        ]
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        monkeypatch.setattr(
            admin_mod,
            "_evaluate_dispatch_empty_render",
            lambda cid, tk: {"empty_render": True, "empty_tokens": ["FIRST_NAME"]},
        )
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda cid, tk: None)
        updates: list[tuple] = []
        monkeypatch.setattr(
            admin_mod,
            "update_dispatch_task",
            lambda tid, **kw: updates.append((tid, kw)),
        )
        resp = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers)
        assert resp.status_code == 200
        out = resp.get_json()
        assert out[0]["empty_render"] is True
        # AST-1819: token list rides on the row for the Invalid tooltip.
        assert out[0]["empty_tokens"] == ["FIRST_NAME"]
        assert out[0]["invalid_reason"] == ""
        assert out[0]["auto_mode"] == 0
        assert updates == [(7, {"auto_mode": 0})]

    def test_list_empty_render_false_keeps_auto(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [
            {
                "id": 8,
                "task_key": "qualify_job_listings",
                "trigger_state": "NEW",
                "entity_type": "job",
                "candidate_id": "c1",
                "score_floor": None,
                "auto_mode": 1,
            }
        ]
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        monkeypatch.setattr(
            admin_mod,
            "_evaluate_dispatch_empty_render",
            lambda cid, tk: {"empty_render": False, "empty_tokens": []},
        )
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda cid, tk: None)
        updates: list = []
        monkeypatch.setattr(
            admin_mod, "update_dispatch_task", lambda *a, **k: updates.append(k)
        )
        out = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        assert out[0]["empty_render"] is False
        assert out[0]["empty_tokens"] == []  # AST-1819: always a list
        assert out[0]["invalid_reason"] == ""  # AST-1880: always a string
        assert out[0]["auto_mode"] == 1
        assert updates == []

    def test_list_missing_platform_key_is_invalid_with_reason_and_forces_auto_off(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        # AST-1880 AC 5: prompts render fine, but the candidate lacks the task server's key.
        rows = [{"id": 9, "task_key": "select_job_page", "trigger_state": "NEW", "entity_type": "company",
                 "candidate_id": "c1", "score_floor": None, "auto_mode": 1}]
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        monkeypatch.setattr(admin_mod, "_evaluate_dispatch_empty_render", lambda cid, tk: {"empty_render": False, "empty_tokens": []})
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda cid: {"candidate_api_keys": {"anthropic": "sk-a"}})
        monkeypatch.setattr(admin_mod, "task_llm_server_id", lambda tk: "kimi")
        updates: list = []
        monkeypatch.setattr(admin_mod, "update_dispatch_task", lambda tid, **kw: updates.append((tid, kw)))
        with caplog.at_level("WARNING"):
            out = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        need = "Set this candidate's Kimi API key before using Run or Auto on this task."
        assert (out[0]["empty_render"], out[0]["invalid_reason"], out[0]["empty_tokens"]) == (True, need, [])
        assert out[0]["auto_mode"] == 0
        assert updates == [(9, {"auto_mode": 0})]
        assert f"{need} — AUTO forced off" in caplog.text

    def test_run_missing_platform_key_400_never_starts(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1880 AC 5: Run refuses before any request; the key checked is the row task's server.
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda tid: {"id": tid, "task_key": "select_job_page", "candidate_id": "c1"})
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda cid: {"candidate_api_keys": {"anthropic": "sk-a"}})
        asked: list = []
        monkeypatch.setattr(admin_mod, "task_llm_server_id", lambda tk: asked.append(tk) or "kimi")
        run = MagicMock()
        monkeypatch.setattr(admin_mod, "run_task", run)
        resp = admin_client.post("/api/admin/dispatch_tasks/9/run", headers=auth_headers)
        assert (resp.status_code, resp.get_json()) == (
            400, {"error": "Set this candidate's Kimi API key before using Run or Auto on this task.", "started": False},
        )
        assert asked == ["select_job_page"]
        run.assert_not_called()

    def test_create_auto_on_empty_render_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(
            admin_mod,
            "_candidate_dispatch_empty_render_error",
            lambda cid, tk: "Prompt tokens resolve empty for this candidate (cannot Auto/Run): FIRST_NAME",
        )
        save = MagicMock()
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={
                "candidate_id": "c1",
                "task_key": "qualify_job_listings",
                "trigger_state": "PASSED_JOBLIST",
                "min_count": 1,
                "auto_mode": True,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "FIRST_NAME" in resp.get_json()["error"]
        save.assert_not_called()

    def test_put_auto_on_empty_render_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "id": 1,
                "task_key": "qualify_job_listings",
                "trigger_state": "PASSED_JOBLIST",
                "candidate_id": "c1",
                "auto_mode": 0,
                "entity_type": "job",
            },
        )
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(
            admin_mod,
            "_candidate_dispatch_empty_render_error",
            lambda cid, tk: "Cannot Auto/Run: prompts could not be validated for empty-render on this candidate/task.",
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put(
            "/api/admin/dispatch_tasks/1",
            json={"auto_mode": True},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "Cannot Auto/Run" in resp.get_json()["error"]
        update.assert_not_called()

    def test_run_empty_render_400_started_false(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"candidate_id": "c1", "task_key": "qualify_job_listings"},
        )
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        monkeypatch.setattr(
            admin_mod,
            "_candidate_dispatch_empty_render_error",
            lambda cid, tk: "Prompt tokens resolve empty for this candidate (cannot Auto/Run): FIRST_NAME",
        )
        run = MagicMock(return_value=True)
        monkeypatch.setattr(admin_mod, "run_task", run)
        resp = admin_client.post("/api/admin/dispatch_tasks/1/run", headers=auth_headers)
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["started"] is False
        assert "FIRST_NAME" in body["error"]
        run.assert_not_called()

    def test_error_helper_none_when_evaluate_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod,
            "_evaluate_dispatch_empty_render",
            lambda cid, tk: {"empty_render": False, "empty_tokens": []},
        )
        assert admin_mod._candidate_dispatch_empty_render_error("c1", "qualify_job_listings") is None


class TestAst2091RubricDispatchGate:
    """AST-2091 [bug-repro]: duplicate-code / empty rubric makes a rubric-backed row Invalid (list, AUTO-on, Run)."""

    DUP = "Rubric 'do_rubric' has duplicate vector codes: TP"
    EMPTY = "Rubric 'do_rubric' is empty for this candidate."

    @pytest.fixture(autouse=True)
    def _rubrics(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Plan Repro fixture; real rubric_dispatch_error runs behind the stubbed table read.
        tp = {"code": "TP", "label": "Hands-On Technical Partnership With Engineers", "content": "…", "importance": 8}
        sa = {"code": "SA", "label": "Systems Architecture", "content": "…", "importance": 7}
        rubrics = {("somerset", "grade_do"): [tp, dict(tp), sa]}
        monkeypatch.setattr(
            "src.data.database.list_rubric_vectors",
            lambda cid, owner, current_only=False: rubrics.get((cid, owner), []),
        )
        # Key / token gates pass unless a test says otherwise.
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda cid, tk: None)
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_empty_render_error", lambda cid, tk: None)
        monkeypatch.setattr(admin_mod, "_evaluate_dispatch_empty_render", lambda cid, tk: {"empty_render": False, "empty_tokens": []})
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())

    def _list(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, rows: list) -> tuple:
        updates: list = []
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(admin_mod, "update_dispatch_task", lambda tid, **kw: updates.append((tid, kw)))
        return admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json(), updates

    @staticmethod
    def _row(cid: str, task_key: str = "meteorite_grade_do", rid: int = 21) -> dict:
        return {"id": rid, "task_key": task_key, "trigger_state": "METEORITE_PASSED_JD", "entity_type": "meteorite",
                "candidate_id": cid, "score_floor": None, "auto_mode": 1}

    @pytest.mark.parametrize("cid,reason", [("somerset", DUP), ("empty_cand", EMPTY)])
    def test_list_bad_rubric_invalid_and_forces_auto_off(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture, cid: str, reason: str,
    ) -> None:
        # Repro 1 / 4: was empty_render False, invalid_reason "", AUTO left on.
        with caplog.at_level("WARNING"):
            out, updates = self._list(admin_client, auth_headers, monkeypatch, [self._row(cid)])
        assert (out[0]["empty_render"], out[0]["invalid_reason"], out[0]["auto_mode"]) == (True, reason, 0)
        assert out[0]["empty_tokens"] == []
        assert updates == [(21, {"auto_mode": 0})]
        assert f"{reason} — AUTO forced off" in caplog.text

    @pytest.mark.parametrize("task_key", ["craft_do_rubric", "select_job_page"])
    def test_list_craft_and_non_rubric_rows_unaffected_by_empty_rubric(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, task_key: str
    ) -> None:
        out, updates = self._list(admin_client, auth_headers, monkeypatch, [self._row("empty_cand", task_key)])
        assert (out[0]["empty_render"], out[0]["invalid_reason"], out[0]["auto_mode"]) == (False, "", 1)
        assert updates == []

    def test_list_precedence_key_then_rubric_then_tokens(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Tokens empty on both rows; row 31 also lacks its key.
        monkeypatch.setattr(admin_mod, "_evaluate_dispatch_empty_render", lambda cid, tk: {"empty_render": True, "empty_tokens": ["FIRST_NAME"]})
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda cid, tk: "need key" if cid == "nokey" else None)
        rubric_reads: list = []
        monkeypatch.setattr(
            "src.data.database.list_rubric_vectors",
            lambda cid, owner, current_only=False: rubric_reads.append(cid) or [],
        )
        out, _ = self._list(admin_client, auth_headers, monkeypatch, [self._row("nokey", rid=31), self._row("empty_cand", rid=32)])
        by_id = {r["id"]: r for r in out}
        assert by_id[31]["invalid_reason"] == "need key"
        assert by_id[32]["invalid_reason"] == self.EMPTY
        # AST-1819 tooltip list still rides along under the higher-precedence reasons.
        assert by_id[31]["empty_tokens"] == by_id[32]["empty_tokens"] == ["FIRST_NAME"]
        assert "empty_cand" in rubric_reads

    @pytest.mark.parametrize("cid,reason", [("somerset", DUP), ("empty_cand", EMPTY)])
    def test_create_auto_on_bad_rubric_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, cid: str, reason: str
    ) -> None:
        save = MagicMock(return_value=9)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": cid, "task_key": "meteorite_grade_do", "trigger_state": "METEORITE_PASSED_JD",
                  "min_count": 1, "auto_mode": True},
            headers=auth_headers,
        )
        assert (resp.status_code, resp.get_json()) == (400, {"error": reason})
        save.assert_not_called()

    def test_put_auto_on_bad_rubric_400(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        row = self._row("somerset")
        row["auto_mode"] = 0
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda tid: dict(row))
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        resp = admin_client.put("/api/admin/dispatch_tasks/21", json={"auto_mode": True}, headers=auth_headers)
        assert (resp.status_code, resp.get_json()) == (400, {"error": self.DUP})
        update.assert_not_called()

    @pytest.mark.parametrize("cid,reason", [("somerset", DUP), ("empty_cand", EMPTY)])
    def test_run_bad_rubric_400_never_starts(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, cid: str, reason: str
    ) -> None:
        # Repro 2: was 200 {"started": true}. Rubric reason outranks the token reason.
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda tid: self._row(cid))
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_empty_render_error", lambda c, tk: "Prompt tokens resolve empty")
        run = MagicMock(return_value=True)
        monkeypatch.setattr(admin_mod, "run_task", run)
        resp = admin_client.post("/api/admin/dispatch_tasks/21/run", headers=auth_headers)
        assert (resp.status_code, resp.get_json()) == (400, {"error": reason, "started": False})
        run.assert_not_called()

    def test_run_key_error_outranks_rubric(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda tid: self._row("somerset"))
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda cid, tk: "need key")
        resp = admin_client.post("/api/admin/dispatch_tasks/21/run", headers=auth_headers)
        assert (resp.status_code, resp.get_json()) == (400, {"error": "need key", "started": False})


class TestAst1791NoPromptValueErrorEmptyRender:
    """AST-1792 / AST-1791: prompt-load ValueError soft-miss → empty_render false (no eval monkeypatch)."""

    @staticmethod
    def _stub_no_agent_task_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
        # Real evaluate path: candidate exists, prompt load raises (no agent_task).
        monkeypatch.setattr(
            admin_mod.database,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": "c1",
                "first": "Ada",
                "last": "Lovelace",
                "candidate_data": {},
            },
        )
        # AST-1855: hydrated loader (AST-1854) reads artifacts — keep it off the repo DB.
        monkeypatch.setattr(admin_mod.database, "get_current_artifact", lambda *a: None)
        monkeypatch.setattr(admin_mod, "build_candidate_token_view", lambda cand: {"first": "Ada"})
        monkeypatch.setattr(
            admin_mod,
            "_dispatch_empty_render_prompt_texts",
            lambda tk: (_ for _ in ()).throw(ValueError(f"No agent_task row for '{tk}'")),
        )

    def test_evaluate_valueerror_no_agent_task_empty_render_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # [bug-repro] red on pre-AST-1791 (ValueError → true); green after soft-miss → false.
        self._stub_no_agent_task_prompts(monkeypatch)
        assert admin_mod._evaluate_dispatch_empty_render("c1", "gaze") == {
            "empty_render": False,
            "empty_tokens": [],
        }
        assert admin_mod._candidate_dispatch_empty_render_error("c1", "gaze") is None

    def test_evaluate_valueerror_soft_miss_no_warning(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # [bug-repro] red on pre-AST-1794 (soft-miss still warns); green after silence.
        self._stub_no_agent_task_prompts(monkeypatch)
        warn = MagicMock()
        monkeypatch.setattr(admin_mod.logger, "warning", warn)
        assert admin_mod._evaluate_dispatch_empty_render("c1", "gaze") == {
            "empty_render": False,
            "empty_tokens": [],
        }
        # Soft-miss must not emit AST-1791's "no prompts to validate" warning.
        soft_miss = [
            c
            for c in warn.call_args_list
            if "no prompts to validate" in " ".join(str(a) for a in c.args)
        ]
        assert soft_miss == []
        assert warn.call_count == 0

    def test_list_valueerror_no_prompts_keeps_auto(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._stub_no_agent_task_prompts(monkeypatch)
        rows = [
            {
                "id": 9,
                "task_key": "gaze",
                "trigger_state": "NEW",
                "entity_type": "company",
                "candidate_id": "c1",
                "score_floor": None,
                "auto_mode": 1,
            }
        ]
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: rows)
        monkeypatch.setattr(admin_mod, "admin_hidden_dispatch_task_keys", lambda: frozenset())
        updates: list[tuple] = []
        monkeypatch.setattr(
            admin_mod,
            "update_dispatch_task",
            lambda tid, **kw: updates.append((tid, kw)),
        )
        out = admin_client.get("/api/admin/dispatch_tasks", headers=auth_headers).get_json()
        assert out[0]["empty_render"] is False
        assert out[0]["auto_mode"] == 1
        assert updates == []

    def test_run_valueerror_no_prompts_allowed(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._stub_no_agent_task_prompts(monkeypatch)
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {"candidate_id": "c1", "task_key": "gaze"},
        )
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id, task_key: None)
        run = MagicMock(return_value=True)
        monkeypatch.setattr(admin_mod, "run_task", run)
        resp = admin_client.post("/api/admin/dispatch_tasks/1/run", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["started"] is True
        run.assert_called_once()


# Branches: artifact-only / neither / legacy-blob Ideal Day through the real hydrated loader (AST-1854).
class TestAst1854HydratedCandidateEmptyRender:
    """AST-1855 / AST-1854: dispatch empty-render reads the hydrated candidate (artifact overlay), no eval / loader / token-view monkeypatch."""

    @staticmethod
    def _stub_hydrated_candidates(monkeypatch: pytest.MonkeyPatch) -> None:
        # DB edges only — loader, hydrate_operative_*, token view, resolve_tokens and
        # empty_render_for_prompts stay real, or the raw-vs-hydrated defect is hidden.
        def _rows() -> dict[str, dict[str, Any]]:
            # Fresh dicts per call: the hydrated loader mutates candidate_data in place.
            return {
                "c1": {"astral_candidate_id": "c1", "first": "Ada", "last": "Lovelace",
                       "candidate_data": {"context": {}}},
                "c2": {"astral_candidate_id": "c2", "first": "Bea", "last": "Blank",
                       "candidate_data": {"context": {}}},
                "c3": {"astral_candidate_id": "c3", "first": "Cy", "last": "Legacy",
                       "candidate_data": {"context": {"ideal_day": "Legacy blob ideal day."}}},
            }

        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda cid: _rows()[cid])
        # Same src.data.database object candidate.get_candidate_current calls — answers all
        # nine hydrate reads; only c1 has a current Ideal Day artifact.
        monkeypatch.setattr(
            admin_mod.database,
            "get_current_artifact",
            lambda entity_type, entity_id, artifact_type: (
                {"artifact_data": "Deep work mornings, collaborative afternoons."}
                if (entity_id, artifact_type) == ("c1", "ideal_day")
                else None
            ),
        )
        # Single candidate-scoped token, so a blank fill names exactly IDEAL_DAY.
        monkeypatch.setattr(
            admin_mod, "_dispatch_empty_render_prompt_texts", lambda tk: ["Ideal day: {$IDEAL_DAY}"]
        )

    def test_evaluate_artifact_only_ideal_day_empty_render_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # [bug-repro] red on pre-AST-1854 (raw row → IDEAL_DAY blank); green after hydrated loader.
        self._stub_hydrated_candidates(monkeypatch)
        assert admin_mod._evaluate_dispatch_empty_render("c1", "craft_do_rubric") == {
            "empty_render": False,
            "empty_tokens": [],
        }
        assert admin_mod._candidate_dispatch_empty_render_error("c1", "craft_do_rubric") is None

    def test_evaluate_no_ideal_day_anywhere_empty_render_true(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._stub_hydrated_candidates(monkeypatch)
        assert admin_mod._evaluate_dispatch_empty_render("c2", "craft_do_rubric") == {
            "empty_render": True,
            "empty_tokens": ["IDEAL_DAY"],
        }
        assert "IDEAL_DAY" in admin_mod._candidate_dispatch_empty_render_error("c2", "craft_do_rubric")

    def test_evaluate_legacy_blob_ideal_day_empty_render_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Hydrate miss leaves the legacy context.ideal_day blob in place.
        self._stub_hydrated_candidates(monkeypatch)
        assert admin_mod._evaluate_dispatch_empty_render("c3", "craft_do_rubric") == {
            "empty_render": False,
            "empty_tokens": [],
        }


# Branches: _parse_sweep_hrs None / "" / non-numeric / negative / valid; create 400 vs save kwarg;
# update "sweep_hrs" in body (400 vs value / null clear); AUTO edit lock unchanged; column metadata key.
@pytest.mark.skipif(
    not hasattr(admin_mod, "_parse_sweep_hrs"),
    reason="AST-1830 sweep_hrs admin API not on this publish tip",
)
class TestAst1830SweepHrsAdminApi:
    """AST-1830: dispatch_task sweep_hrs on admin create/update + list column metadata."""

    _BODY = {"candidate_id": "c1", "task_key": "grade_do", "trigger_state": "PASSED_JD", "min_count": 1}

    @pytest.mark.parametrize(
        "raw,expected",
        [(2.5, 2.5), ("3", 3.0), (0, 0.0), (None, None), ("", None), ("  ", None)],
        ids=["float", "numeric_str", "zero", "null", "empty", "blank"],
    )
    def test_create_passes_sweep_hrs(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, raw, expected
    ) -> None:
        save = MagicMock(return_value=42)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks", json={**self._BODY, "sweep_hrs": raw}, headers=auth_headers
        )
        assert resp.status_code == 201
        assert save.call_args.kwargs["sweep_hrs"] == expected

    def test_create_omitted_sweep_hrs_is_null(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock(return_value=42)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        assert admin_client.post("/api/admin/dispatch_tasks", json=self._BODY, headers=auth_headers).status_code == 201
        assert save.call_args.kwargs["sweep_hrs"] is None

    @pytest.mark.parametrize("raw", [-1, "-0.5", "abc", [1]], ids=["neg", "neg_str", "non_numeric", "list"])
    def test_create_rejects_bad_sweep_hrs(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, raw
    ) -> None:
        save = MagicMock(return_value=42)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", save)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks", json={**self._BODY, "sweep_hrs": raw}, headers=auth_headers
        )
        assert resp.status_code == 400
        assert "sweep_hrs" in resp.get_json()["error"]
        save.assert_not_called()

    def _stub_row(self, monkeypatch: pytest.MonkeyPatch, auto_mode: int = 0) -> MagicMock:
        monkeypatch.setattr(
            admin_mod.database,
            "get_dispatch_task",
            lambda task_id: {
                "task_key": "grade_do", "trigger_state": "PASSED_JD", "candidate_id": "c1",
                "auto_mode": auto_mode, "sweep_hrs": 1.0,
            },
        )
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        return update

    # AC 11: PUT on AUTO-off row — 4 persists 4, null clears to NULL
    @pytest.mark.parametrize("raw,expected", [(4, 4.0), (None, None), ("", None)], ids=["four", "null", "empty"])
    def test_update_sets_or_clears_sweep_hrs(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, raw, expected
    ) -> None:
        update = self._stub_row(monkeypatch)
        resp = admin_client.put("/api/admin/dispatch_tasks/1", json={"sweep_hrs": raw}, headers=auth_headers)
        assert resp.status_code == 200
        assert "sweep_hrs" in update.call_args.kwargs
        assert update.call_args.kwargs["sweep_hrs"] == expected

    @pytest.mark.parametrize("raw", [-4, "nope"], ids=["neg", "non_numeric"])
    def test_update_rejects_bad_sweep_hrs(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, raw
    ) -> None:
        update = self._stub_row(monkeypatch)
        resp = admin_client.put("/api/admin/dispatch_tasks/1", json={"sweep_hrs": raw}, headers=auth_headers)
        assert resp.status_code == 400
        assert "sweep_hrs" in resp.get_json()["error"]
        update.assert_not_called()

    def test_update_auto_row_edit_lock_unchanged(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        update = self._stub_row(monkeypatch, auto_mode=1)
        resp = admin_client.put("/api/admin/dispatch_tasks/1", json={"sweep_hrs": 2}, headers=auth_headers)
        assert resp.status_code == 400
        assert "AUTO" in resp.get_json()["error"]
        update.assert_not_called()

    def test_update_without_sweep_key_leaves_it_untouched(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        update = self._stub_row(monkeypatch)
        assert admin_client.put("/api/admin/dispatch_tasks/1", json={"min_count": 3}, headers=auth_headers).status_code == 200
        assert "sweep_hrs" not in update.call_args.kwargs

    # AC 11: list req_dict column metadata exposes sweep_hrs (float) right after freq_hrs
    def test_column_metadata_includes_sweep_hrs(self) -> None:
        keys = [c["key"] for c in admin_mod._DISPATCH_TASK_COLUMNS]
        col = next(c for c in admin_mod._DISPATCH_TASK_COLUMNS if c["key"] == "sweep_hrs")
        assert col["type"] == "float"
        assert keys.index("sweep_hrs") == keys.index("freq_hrs") + 1


# Branches: create_dtask max_runs follow-up — present non-null (0 / N / numeric str → update) vs absent / null (no update).
class TestAst1831CreateMaxRuns:
    """AST-1831: POST /dispatch_tasks persists max_runs via update_dispatch_task follow-up (save has no max_runs param)."""

    _BODY = {"candidate_id": "c1", "task_key": "grade_do", "trigger_state": "PASSED_JD", "min_count": 1}

    def _mocks(self, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(return_value=42))
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        return update

    # 0 = loop until drained; N = cap; str coerced like update_dt.
    @pytest.mark.parametrize("raw,expected", [(0, 0), (5, 5), ("3", 3)], ids=["drain", "cap", "numeric_str"])
    def test_create_persists_max_runs(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, raw, expected
    ) -> None:
        update = self._mocks(monkeypatch)
        resp = admin_client.post(
            "/api/admin/dispatch_tasks", json={**self._BODY, "max_runs": raw}, headers=auth_headers
        )
        assert resp.status_code == 201
        update.assert_called_once_with(42, max_runs=expected)

    # Absent / null → no follow-up; row keeps column DEFAULT 1.
    @pytest.mark.parametrize("extra", [{}, {"max_runs": None}], ids=["absent", "null"])
    def test_create_without_max_runs_skips_follow_up(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch, extra
    ) -> None:
        update = self._mocks(monkeypatch)
        resp = admin_client.post("/api/admin/dispatch_tasks", json={**self._BODY, **extra}, headers=auth_headers)
        assert resp.status_code == 201
        update.assert_not_called()


# Branches: GET payload (effective + default + bounds); POST setter accept → payload, ValueError → 400;
# require_admin 401 / 403 on both verbs. Real dispatcher getter/setter (no stubs) so GET-after-POST is end-to-end.
class TestAst1916AutoThreadCapApi:
    """AST-1916: GET/POST /api/admin/scheduler/auto_thread_cap."""

    _URL = "/api/admin/scheduler/auto_thread_cap"

    @pytest.fixture(autouse=True)
    def _reset_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # api_admin binds src.core.dispatcher's setter — restore that module's override after each test.
        monkeypatch.setattr(dispatcher_mod, "_auto_thread_cap_override", None)

    def _cap(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> int:
        return admin_client.get(self._URL, headers=auth_headers).get_json()["max_auto_threads"]

    def test_get_reports_default_and_bounds(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = admin_client.get(self._URL, headers=auth_headers)
        assert resp.status_code == 200
        default = cfg.ASTRAL_CONFIG["max_auto_threads"]
        assert resp.get_json() == {"max_auto_threads": default, "default": default, "min": 1, "max": 100}

    @pytest.mark.parametrize("value", [1, 100], ids=["min", "max"])
    def test_post_in_range_returns_payload_and_get_reflects(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], value: int
    ) -> None:
        resp = admin_client.post(self._URL, json={"max_auto_threads": value}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["max_auto_threads"] == value
        assert resp.get_json()["default"] == cfg.ASTRAL_CONFIG["max_auto_threads"]
        assert self._cap(admin_client, auth_headers) == value

    # AC 3 values plus missing key / empty body (body.get → None) — all 400, prior cap kept.
    @pytest.mark.parametrize(
        "body",
        [{"max_auto_threads": 0}, {"max_auto_threads": 101}, {"max_auto_threads": "abc"},
         {"max_auto_threads": 2.5}, {}, None],
        ids=["zero", "over_max", "str", "float", "missing_key", "no_body"],
    )
    def test_post_rejects_and_keeps_prior_cap(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], body: Any
    ) -> None:
        assert admin_client.post(self._URL, json={"max_auto_threads": 7}, headers=auth_headers).status_code == 200
        resp = admin_client.post(self._URL, json=body, headers=auth_headers)
        assert resp.status_code == 400
        assert "whole number between 1 and 100" in resp.get_json()["error"]
        assert self._cap(admin_client, auth_headers) == 7

    @pytest.mark.parametrize("method", ["get", "post"])
    def test_requires_admin(
        self, admin_client: FlaskClient, non_admin_headers: dict[str, str], method: str
    ) -> None:
        call = getattr(admin_client, method)
        assert call(self._URL, json={"max_auto_threads": 5}).status_code == 401
        assert call(self._URL, json={"max_auto_threads": 5}, headers=non_admin_headers).status_code == 403
        assert dispatcher_mod._auto_thread_cap_override is None


# AST-1978: Manage Tasks RSC — raw {$RESPONSE_SCHEMA} count served on every /api/admin/tasks row.
# Branches: non-blank task system_prompt wins over agent content; blank / whitespace / None system_prompt
# falls back to agent content; no task / no agent → 0; count is pre-resolution and candidate-independent.
class TestAst1978ResponseSchemaCount:
    RS = "{$RESPONSE_SCHEMA}"

    @classmethod
    def _wire(cls, monkeypatch: pytest.MonkeyPatch, task: dict | None, agent: dict | None) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": "t_rsc", "task_key_uuid": None, "agent_id": "a1" if agent else "",
                      "cache_prompt_len": 0, "nocache_prompt_len": 0}],
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda cid: {"candidate_data": {"name": "Susan"}})
        monkeypatch.setattr(admin_mod.database, "get_current_artifact", lambda *a: None)
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda k: task)
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda a: agent)
        # Resolution substitutes the token away — a served count > 0 proves RSC reads the raw text (AC 2).
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *a, **k: (text or "").replace(cls.RS, "SCHEMA"))
        monkeypatch.setattr(admin_mod, "resolved_task_system", lambda *a, **k: "SCHEMA")

    def _count(self, monkeypatch: pytest.MonkeyPatch, task: dict | None, agent: dict | None) -> Any:
        self._wire(monkeypatch, task, agent)
        return admin_mod._enrich_tasks("")[0]["response_schema_count"]

    def test_sums_raw_token_across_all_seven_segments(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rs = self.RS
        task = {
            "system_prompt": f"a {rs} b {rs}",   # 2
            "cache_prompt": rs,                    # 1
            "cache_prompt_b": f"x{rs}",            # 1
            "cache_prompt_c": "",                  # 0
            "cache_prompt_d": f"{rs}\n",           # 1
            "nocache_prompt": rs,                  # 1
            "user_prompt": f"{rs} and {rs}",      # 2
        }
        # Agent content is ignored when the task's own system_prompt is non-blank.
        count = self._count(monkeypatch, task, {"content": f"{rs} {rs} {rs}"})
        assert type(count) is int and count == 8

    @pytest.mark.parametrize("system_prompt", ["", "   \n", None], ids=["empty", "whitespace", "none"])
    def test_blank_system_prompt_falls_back_to_agent_content(
        self, monkeypatch: pytest.MonkeyPatch, system_prompt: str | None
    ) -> None:
        task = {"system_prompt": system_prompt, "cache_prompt": "no token", "user_prompt": "plain"}
        assert self._count(monkeypatch, task, {"content": f"agent {self.RS} body"}) == 1

    @pytest.mark.parametrize(
        ("task", "agent", "expected"),
        [
            (None, None, 0),
            (None, {"content": "agent {$RESPONSE_SCHEMA}"}, 1),
            ({"system_prompt": "own {$RESPONSE_SCHEMA}"}, None, 1),
            ({"system_prompt": "s", "user_prompt": "{$RESPONSE_SCHEMA_X} {$OTHER}"}, {"content": "c"}, 0),
        ],
        ids=["no_task_no_agent", "agent_only", "task_without_agent", "other_tokens_only"],
    )
    def test_missing_rows_and_other_tokens(
        self, monkeypatch: pytest.MonkeyPatch, task: dict | None, agent: dict | None, expected: int
    ) -> None:
        count = self._count(monkeypatch, task, agent)
        assert type(count) is int and count == expected

    def test_route_serves_same_count_with_and_without_candidate(
        self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._wire(monkeypatch, {"system_prompt": self.RS, "nocache_prompt": self.RS}, {"content": "c"})
        bare = admin_client.get("/api/admin/tasks", headers=auth_headers).get_json()
        scoped = admin_client.get("/api/admin/tasks?candidate_id=c1", headers=auth_headers).get_json()
        assert [r["response_schema_count"] for r in bare] == [r["response_schema_count"] for r in scoped] == [2]


class TestAst2006EnrichTasksProbeSilent:
    """AST-2006 / AST-2000: the Manage Tasks token-count probe never logs empty-token WARNINGs; preview still does."""

    _SYSTEM = "JD {$VISIBLE_JD}\n{$ANALYSIS_JD}"

    def test_enrich_tasks_job_tokens_without_job_are_silent(self, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        # Real resolve_tokens / resolved_task_system / _chain_context; candidate present, no job → job tokens blank.
        import logging

        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(
            admin_mod.database, "list_candidate_tasks",
            lambda: [{"task_key": "anticipate_scan", "task_key_uuid": "u1", "agent_id": "agent-1", "cache_prompt_len": 0, "nocache_prompt_len": 0}],
        )
        monkeypatch.setattr(
            admin_mod.database, "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "first": "Ann", "candidate_data": {}},
        )
        monkeypatch.setattr(admin_mod.database, "get_current_artifact", lambda *a: None)
        monkeypatch.setattr(
            admin_mod.database, "get_agent_task",
            lambda task_key: {"system_prompt": self._SYSTEM, "cache_prompt": "do {$ANALYSIS_DO}", "task_key_uuid": "u1"},
        )
        monkeypatch.setattr(
            admin_mod.database, "get_agent",
            lambda agent_id: {"model_id": "claude-sonnet-4-6", "temperature": 0.2, "content": "agent", "max_tokens": 10},
        )
        with caplog.at_level(logging.WARNING):
            rows = admin_mod._enrich_tasks("cand-1")
        assert not [r.getMessage() for r in caplog.records if "resolved to empty" in r.getMessage()]
        # Token counting still runs on the (blank-substituted) system text.
        assert len(rows) == 1 and rows[0]["system_prompt_tokens"] > 0

    def test_preview_resolution_still_warns(self, monkeypatch: pytest.MonkeyPatch, caplog) -> None:
        # Control: /tasks/<task>/preview → preview_task_prompt → agent.preview_prompt keeps default warn_on_empty.
        import logging

        from src.core import agent as agent_mod

        monkeypatch.setattr(
            agent_mod, "_resolve_task_prompts",
            lambda task_key: ({"content": "agent", "model_id": "claude-sonnet-4-6"}, {"system_prompt": self._SYSTEM}),
        )
        with caplog.at_level(logging.WARNING):
            agent_mod.preview_prompt("anticipate_scan", {"first": "Ann", "_astral_candidate_id": "cand-1"})
        msgs = [r.getMessage() for r in caplog.records if "resolved to empty (job_context, task=anticipate_scan)" in r.getMessage()]
        assert len(msgs) == 2  # VISIBLE_JD + ANALYSIS_JD


# AST-2134: admin ad-hoc preview resolves company telescope ids via gazer; job previews read the composed JD.
class TestAst2134AdhocPreviewTelescope:
    @pytest.fixture(autouse=True)
    def _db(self, sqlite_in_memory):
        return sqlite_in_memory

    def _keep(self, text: str, data_type: str = "VISIBLE_TEXT") -> str:
        from src.core import gazer
        return gazer.keep_telescope_data(None, "https://acme.com/p", data_type, text)

    def _company(self, monkeypatch: pytest.MonkeyPatch, cdata: dict) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "company"})
        monkeypatch.setattr(admin_mod.database, "get_company", lambda short_name: {"company_data": dict(cdata)})

    def _previews(self, monkeypatch: pytest.MonkeyPatch, cdata: dict) -> dict:
        self._company(monkeypatch, cdata)
        return {t: admin_mod._build_adhoc_live_content(t, "acme") for t in ("prefilter_company", "select_job_page", "gaze")}

    def test_ac6_company_previews_byte_identical_text_vs_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        nav = "1: https://acme.com/about\n2: https://acme.com/careers"
        legacy = {
            "homepage_text": "Acme homepage body",
            "nav_links": nav,
            "website_content": [{"url": "https://acme.com/c1", "content": "Culture one"},
                                {"url": "https://acme.com/c2", "content": "Culture two"}],
        }
        ids = {
            "homepage_text": self._keep("Acme homepage body"),
            "nav_links": self._keep(nav, "PAGE_LINKS"),
            # Fresh captures are raw (unstripped); the preview strips like the pre-AST-2130 blob
            "website_content": [{"url": "https://acme.com/c1", "id": self._keep("  Culture one\n")},
                                {"url": "https://acme.com/c2", "id": self._keep("Culture two")}],
        }
        before = self._previews(monkeypatch, legacy)
        after = self._previews(monkeypatch, ids)
        assert after == before
        assert all(before.values())  # non-vacuous: every preview has content
        assert "Acme homepage body" in before["prefilter_company"]

    def test_ac6_prefilter_falls_back_to_website_content_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        legacy = {"website_content": "Plain culture text"}
        ids = {"website_content": self._keep("Plain culture text")}
        assert self._previews(monkeypatch, ids) == self._previews(monkeypatch, legacy)

    def test_gone_capture_previews_empty(self, monkeypatch: pytest.MonkeyPatch, sqlite_in_memory) -> None:
        rid = self._keep("Culture")
        conn = sqlite_in_memory._get_connection()
        try:
            conn.execute("DELETE FROM telescope_data WHERE telescope_data_id = ?", (rid,))
            conn.commit()
        finally:
            conn.close()
        assert self._previews(monkeypatch, {"website_content": [{"url": "u", "id": rid}]})["gaze"] == ""

    def _jobs(self, monkeypatch: pytest.MonkeyPatch, job_data: dict, company_data: dict | None = None) -> None:
        monkeypatch.setattr(admin_mod, "get_dispatch_task_by_key", lambda task_key: {"entity_type": "job"})
        monkeypatch.setattr(admin_mod.database, "get_job", lambda jid: {
            "astral_job_id": jid, "job_title": "Engineer", "job_link": f"https://jobs.example/{jid}",
            "company": "acme", "job_data": dict(job_data),
        })
        monkeypatch.setattr(admin_mod.database, "get_company", lambda short_name: {"data": dict(company_data or {})})

    def test_job_previews_read_composed_jd(self, monkeypatch: pytest.MonkeyPatch) -> None:
        ref = self._keep("Nav\n\nEngineer\nBuild things.\nApply for this job\nfooter")
        self._jobs(monkeypatch, {"job_description": "Email pre", "jd_telescope_data_id": ref,
                                 "raw_job_listing": "raw"})
        composed = "Email pre\n\nEngineer\nBuild things."
        assert admin_mod._build_adhoc_live_content("evaluate_jd", "j1").startswith(f"[astral_job_id=j1]\n{composed}")
        batch = admin_mod._build_adhoc_live_content("qualify_meteorite", "", ["j1"])
        assert batch == f"METEORITE JOBS:\n000: job_link: https://jobs.example/j1\nCONTENT:\n{composed}"

    def test_job_preview_raw_listing_fallback_when_no_jd(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._jobs(monkeypatch, {"raw_job_listing": "raw listing"})
        assert admin_mod._build_adhoc_live_content("evaluate_jd", "j1") == "[astral_job_id=j1]\nraw listing"

    def test_like_company_context_resolves_website_content_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(admin_mod.TASK_CONFIG, "evaluate_jd",
                            {**admin_mod.TASK_CONFIG["evaluate_jd"], "requires_company": True})
        legacy = {"website_content": [{"url": "https://acme.com/c", "content": "Vibes"}]}
        ids = {"website_content": [{"url": "https://acme.com/c", "id": self._keep(" Vibes \n")}]}
        self._jobs(monkeypatch, {"job_description": "JD"}, legacy)
        before = admin_mod._build_adhoc_live_content("evaluate_jd", "j1")
        self._jobs(monkeypatch, {"job_description": "JD"}, ids)
        assert admin_mod._build_adhoc_live_content("evaluate_jd", "j1") == before
        assert "COMPANY CONTEXT" in before and "Vibes" in before
