"""Component tests for src/ui/api/api_admin.py (AST-394)."""

from __future__ import annotations

import io
import threading
import zlib
from typing import Any
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.utils import config as cfg
from ui.api import api_admin as admin_mod


def _tier_catalog_rows_via_ast492_resolve() -> list[dict[str, Any]]:
    """Ada AST-492 contract: tiers → anthropic AGENT_CONFIG key via resolve_* then model defaults."""
    out: list[dict[str, Any]] = []
    for tier in cfg.BRAIN_SETTINGS:
        mk = cfg.resolve_brain_setting_to_anthropic_agent_key(tier)
        m = cfg.get_model(mk)
        out.append(
            {
                "brain_setting": tier,
                "label": tier,
                "default_temperature": m["default_temperature"],
                "default_max_tokens": m["default_max_tokens"],
            }
        )
    return out


# Branches: config and agent CRUD success/error paths.
class TestAdminConfigAndAgents:
    def test_admin_config(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = admin_client.get("/api/admin/config", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), dict)

    def test_list_agents_and_ids(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "list_agents", lambda: [{"agent_id": "a1"}])
        assert admin_client.get("/api/admin/agents", headers=auth_headers).get_json() == [{"agent_id": "a1", "brain_setting": "Medium"}]
        assert admin_client.get("/api/admin/agents/ids", headers=auth_headers).get_json() == ["a1"]

    def test_list_models(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = admin_client.get("/api/admin/agents/models", headers=auth_headers)
        assert resp.status_code == 200
        assert any(row.get("model_code") == "claude-haiku-4-5" for row in resp.get_json())

    def test_list_brain_settings(self, admin_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = admin_client.get("/api/admin/agents/brain_settings", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == _tier_catalog_rows_via_ast492_resolve()

    def test_get_agent_missing_and_found(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        assert admin_client.get("/api/admin/agents/missing", headers=auth_headers).status_code == 404
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id})
        row = admin_client.get("/api/admin/agents/a1", headers=auth_headers).get_json()
        assert row["agent_id"] == "a1"
        assert row["brain_setting"] == "Medium"

    def test_agent_admin_view_branches_strip_and_infer_legacy(self) -> None:
        assert admin_mod._agent_admin_view({}) == {}
        assert admin_mod._agent_admin_view({"agent_id": "x", "brain_setting": " Big "})["brain_setting"] == "Big"
        assert admin_mod._agent_admin_view({"agent_id": "x", "model_code": "claude-opus-4-6"})["brain_setting"] == cfg.BRAIN_BIG

    def test_create_agent_validation_and_success(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        assert admin_client.post("/api/admin/agents", json={}, headers=auth_headers).status_code == 400
        bad_model = admin_client.post("/api/admin/agents", json={"agent_id": "a1", "model_code": "nope"}, headers=auth_headers)
        assert bad_model.status_code == 400
        bad_tier = admin_client.post(
            "/api/admin/agents",
            json={"agent_id": "a1", "content": "x", "brain_setting": "Huge"},
            headers=auth_headers,
        )
        assert bad_tier.status_code == 400
        both_create = admin_client.post(
            "/api/admin/agents",
            json={"agent_id": "dup-fields", "content": "", "brain_setting": "Little", "model_code": "claude-haiku-4-5"},
            headers=auth_headers,
        )
        assert both_create.status_code == 400
        no_tier_row = admin_client.post(
            "/api/admin/agents",
            json={"agent_id": "no-tier", "content": "sys"},
            headers=auth_headers,
        )
        assert no_tier_row.status_code == 400
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id})
        assert (
            admin_client.post(
                "/api/admin/agents",
                json={"agent_id": "a1", "content": "x", "brain_setting": "Little"},
                headers=auth_headers,
            ).status_code
            == 409
        )
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        save = MagicMock()
        monkeypatch.setattr(admin_mod.database, "save_agent", save)
        created = admin_client.post(
            "/api/admin/agents",
            json={"agent_id": "a1", "content": "sys", "model_code": "claude-haiku-4-5", "temperature": 0.2, "max_tokens": 100},
            headers=auth_headers,
        )
        assert created.status_code == 201
        save.assert_called_once_with(
            "a1", "sys", brain_setting="Little", temperature=0.2, max_tokens=100
        )
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        save.reset_mock()
        created_tier = admin_client.post(
            "/api/admin/agents",
            json={"agent_id": "a2", "content": "sys", "brain_setting": "Big", "temperature": 0.1, "max_tokens": 50},
            headers=auth_headers,
        )
        assert created_tier.status_code == 201
        save.assert_called_once_with("a2", "sys", brain_setting="Big", temperature=0.1, max_tokens=50)
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        assert admin_client.put("/api/admin/agents/a1", json={"content": "x"}, headers=auth_headers).status_code == 404
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id})
        bad_bs = admin_client.put("/api/admin/agents/a1", json={"brain_setting": "Huge"}, headers=auth_headers)
        assert bad_bs.status_code == 400
        both_put = admin_client.put(
            "/api/admin/agents/a1",
            json={"brain_setting": "Little", "model_code": "claude-haiku-4-5"},
            headers=auth_headers,
        )
        assert both_put.status_code == 400
        assert admin_client.put("/api/admin/agents/a1", json={"model_code": "nope"}, headers=auth_headers).status_code == 400
        assert admin_client.put("/api/admin/agents/a1", json={}, headers=auth_headers).status_code == 400
        update = MagicMock()
        monkeypatch.setattr(admin_mod.database, "update_agent", update)
        resp = admin_client.put("/api/admin/agents/a1", json={"content": "new"}, headers=auth_headers)
        assert resp.status_code == 200
        update.assert_called_once()
        update.reset_mock()
        infer_put = admin_client.put("/api/admin/agents/a1", json={"model_code": "claude-opus-4-6"}, headers=auth_headers)
        assert infer_put.status_code == 200
        update.assert_called_once()
        update.reset_mock()
        # Branch: model_code key present but empty after strip — skip infer shim; still update via other kwargs.
        assert (
            admin_client.put("/api/admin/agents/a1", json={"model_code": "", "content": "u2"}, headers=auth_headers).status_code
            == 200
        )
        update.assert_called_once()
        update.reset_mock()
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
        monkeypatch.setattr(admin_mod, "get_active_llm_provider", lambda: "anthropic")
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
                "model_code": "claude-sonnet-4-6",
                "content": "agent {$name}",
                "temperature": 0.1,
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

    def test_enrich_tasks_uses_deepseek_pricing_when_active_provider_deepseek(self, monkeypatch: pytest.MonkeyPatch) -> None:
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(admin_mod, "get_active_llm_provider", lambda: "deepseek")
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": "craft_resume_base", "task_key_uuid": None, "agent_id": "a1", "cache_prompt_len": 0, "nocache_prompt_len": 0}],
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: None)
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {"agent_id": agent_id, "brain_setting": cfg.BRAIN_LITTLE, "content": "body"},
        )
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text or "")
        rows = admin_mod._enrich_tasks("")
        assert rows[0]["task_key"] == "craft_resume_base"

    def test_enrich_tasks_unknown_llm_provider_skips_tier_catalog_lookups(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Neither anthropic nor deepseek branch in _enrich_tasks — resolved_model_key and model_cfg stay empty."""
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = None
        monkeypatch.setattr(admin_mod, "_get_connection", lambda: conn)
        monkeypatch.setattr(admin_mod, "get_active_llm_provider", lambda: "mistral-unknown")
        monkeypatch.setattr(
            admin_mod.database,
            "list_candidate_tasks",
            lambda: [{"task_key": "craft_resume_base", "task_key_uuid": None, "agent_id": "a1", "cache_prompt_len": 0, "nocache_prompt_len": 0}],
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: None)
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {"agent_id": agent_id, "brain_setting": cfg.BRAIN_LITTLE, "content": "body"},
        )
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text or "")
        rows = admin_mod._enrich_tasks("")
        assert rows[0]["resolved_model_key"] == ""


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


# AST-773: PUT dispatch_tasks accepts task_key with validation and AUTO guard.
class TestAst773UpdateDispatchTaskTaskKey:
    def test_dispatch_task_key_trigger_error_helper(self) -> None:
        assert admin_mod._dispatch_task_key_trigger_error("", "NEW") == "task_key is required"
        assert admin_mod._dispatch_task_key_trigger_error("grade_do", "") == "trigger_state is required"
        err = admin_mod._dispatch_task_key_trigger_error("grade_do", "NOT_A_JOB_STATE")
        assert err is not None and "grade_do" in err
        assert admin_mod._dispatch_task_key_trigger_error("qualify_job_listings", "VALID_TITLE") is None

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
        assert kw["sort_by"] == cfg.dispatch_task_admin_defaults("grade_do")["sort_by"]
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
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
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
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
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
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: "need key")
        auto_bad = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "qualify_job_listings", "trigger_state": "VALID_TITLE", "min_count": 1, "auto_mode": True},
            headers=auth_headers,
        )
        assert auto_bad.status_code == 400
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(side_effect=Exception("UNIQUE constraint failed")))
        dup = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "qualify_job_listings", "trigger_state": "VALID_TITLE", "min_count": 1, "batch_size": 2, "freq_hrs": 1.5, "score_floor": 2.5},
            headers=auth_headers,
        )
        assert dup.status_code == 409
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(side_effect=RuntimeError("boom")))
        assert admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "custom", "trigger_state": "WATCH", "min_count": 1},
            headers=auth_headers,
        ).status_code == 500
        monkeypatch.setattr(admin_mod, "save_dispatch_task", MagicMock(return_value=42))
        ok = admin_client.post(
            "/api/admin/dispatch_tasks",
            json={"candidate_id": "c1", "task_key": "custom", "trigger_state": "WATCH", "min_count": 1},
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
            lambda task_id: {"task_key": "qualify_job_listings", "trigger_state": "VALID_TITLE", "candidate_id": "c1"},
        )
        assert admin_client.put(f"/api/admin/dispatch_tasks/1", json={}, headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: "need key")
        assert admin_client.put(
            f"/api/admin/dispatch_tasks/1",
            json={"auto_mode": True, "min_count": 2, "batch_size": 3, "debug": False, "skip_cache": True, "freq_hrs": 1.0, "max_runs": 5, "score_floor": 2.0, "trigger_state": "VALID_TITLE"},
            headers=auth_headers,
        ).status_code == 400
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
        update = MagicMock()
        monkeypatch.setattr(admin_mod, "update_dispatch_task", update)
        ok = admin_client.put(f"/api/admin/dispatch_tasks/1", json={"min_count": 2, "trigger_state": ""}, headers=auth_headers)
        assert ok.status_code == 200
        update.assert_called_once()

    def test_scheduler_and_run_controls(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda task_id: None)
        assert admin_client.post("/api/admin/dispatch_tasks/1/run", headers=auth_headers).status_code == 404
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda task_id: {"candidate_id": None})
        assert admin_client.post("/api/admin/dispatch_tasks/1/run", headers=auth_headers).status_code == 400
        monkeypatch.setattr(admin_mod.database, "get_dispatch_task", lambda task_id: {"candidate_id": "c1"})
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
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
        assert admin_mod._build_adhoc_live_content("prefilter", "missing") == ""
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
        assert "HOMEPAGE" in admin_mod._build_adhoc_live_content("prefilter", "acme")
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

        resolved, err = admin_mod._resolve_adhoc({})
        assert err is not None
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: None)
        _, err = admin_mod._resolve_adhoc({"agent_id": "a1"})
        assert err[1] == 404
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id})
        monkeypatch.setattr(admin_mod, "get_active_llm_provider", lambda: "anthropic")
        # AST-492: missing brain_setting/model_code infer Medium (legacy shim); not a client error.
        payload, err = admin_mod._resolve_adhoc({"agent_id": "a1"})
        assert err is None
        assert payload["model_code"] == cfg.resolve_brain_setting_to_anthropic_agent_key(cfg.BRAIN_MEDIUM)
        assert payload.get("tier_meta") is None
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {"agent_id": agent_id, "model_code": "claude-haiku-4-5", "content": "sys", "temperature": None, "max_tokens": None},
        )
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: {"candidate_data": {"x": 1}, "candidate_api_key": "key"})
        monkeypatch.setattr(admin_mod.database, "get_agent_task", lambda task_key: {"task_key_uuid": "uuid-1"})
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text)
        payload, err = admin_mod._resolve_adhoc({"agent_id": "a1", "candidate_id": "c1", "task_key": "craft_resume_base", "user_prompt": "u"})
        assert err is None
        assert payload["api_key_override"] == "key"

    def test_resolve_adhoc_job_entity_resolves_visible_jd_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            admin_mod.database,
            "get_agent",
            lambda agent_id: {"agent_id": agent_id, "content": "{$VISIBLE_JD}", "brain_setting": cfg.BRAIN_LITTLE},
        )
        monkeypatch.setattr(
            admin_mod.database,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"artifacts": {"jobdesc_rubric": {"criteria": []}}}},
        )
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


# AST-491/492 — _resolve_adhoc mirrors do_task tier routing under active_provider.
class TestAst492ResolveAdhocApiAdmin:
    def test_resolve_adhoc_deepseek_sets_tier_meta_and_vendor_as_model_code(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(admin_mod, "get_active_llm_provider", lambda: "deepseek")
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id, "content": "sys", "brain_setting": cfg.BRAIN_LITTLE})
        payload, err = admin_mod._resolve_adhoc({"agent_id": "z1"})
        assert err is None
        assert payload["model_code"] == "deepseek-v4-flash"
        assert payload["tier_meta"] is not None
        assert payload["tier_meta"]["thinking"] is False

    def test_resolve_adhoc_deepseek_unknown_vendor_model_returns_400(
        self, admin_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "get_active_llm_provider", lambda: "deepseek")
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id, "content": "sys", "brain_setting": cfg.BRAIN_LITTLE})
        monkeypatch.setattr(
            admin_mod,
            "resolve_brain_setting_to_deepseek_tier_meta",
            lambda _bs: {"vendor_model": "not-in-pricing-json", "thinking": False},
        )
        with admin_client.application.app_context():
            _, err = admin_mod._resolve_adhoc({"agent_id": "z1"})
        assert err is not None and err[1] == 400

    def test_resolve_adhoc_unknown_active_provider_returns_400(
        self, admin_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(admin_mod, "get_active_llm_provider", lambda: "contoso-bedrock")
        monkeypatch.setattr(admin_mod.database, "get_agent", lambda agent_id: {"agent_id": agent_id, "content": "sys", "brain_setting": cfg.BRAIN_MEDIUM})
        with admin_client.application.app_context():
            _, err = admin_mod._resolve_adhoc({"agent_id": "z1"})
        assert err is not None and err[1] == 400


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
                    "nocache": "n",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": "c1",
                    "task_key_uuid": None,
                    "api_key_override": None,
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
                    "nocache": "",
                    "model_code": "claude-haiku-4-5",
                    "temperature": 0.1,
                    "max_tokens": 10,
                    "candidate_id": "c1",
                    "task_key_uuid": None,
                    "api_key_override": None,
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
        assert admin_mod._candidate_dispatch_api_key_error(None) is not None
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        assert "not found" in admin_mod._candidate_dispatch_api_key_error("c1")
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: {"candidate_api_key": "  "})
        assert "Anthropic API key" in admin_mod._candidate_dispatch_api_key_error("c1")
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: {"candidate_api_key": "key"})
        assert admin_mod._candidate_dispatch_api_key_error("c1") is None

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
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
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
        assert admin_mod._build_adhoc_live_content("prefilter", "acme") == ""
        monkeypatch.setattr(
            admin_mod.database,
            "get_company",
            lambda short_name: {"company_data": {"homepage_text": "home", "nav_links": ["a"]}},
        )
        assert "HOMEPAGE" in admin_mod._build_adhoc_live_content("prefilter", "acme")
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
        assert admin_mod._build_adhoc_live_content("validate_title", "", ["j1"]) != ""
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
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
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
        assert keys["contemplate_job"]["trigger_state"] == cfg.resume_artifact_compound_state("contemplate_job")

    def test_ast549_task_keys_config_derivation_authoritative(self, admin_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        """Schedulable keys merge dispatch_task_admin_defaults — not removed seed dict (AST-549)."""
        monkeypatch.setattr(admin_mod, "list_dispatch_tasks", lambda: [])
        keys = admin_client.get("/api/admin/dispatch_tasks/task_keys", headers=auth_headers).get_json()
        assert keys["contemplate_job"]["trigger_state"] == cfg.resume_artifact_compound_state("contemplate_job")
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
            lambda agent_id: {"agent_id": agent_id, "model_code": "claude-haiku-4-5", "content": "sys", "temperature": 0.2, "max_tokens": 5},
        )
        monkeypatch.setattr(admin_mod, "resolve_tokens", lambda text, *args, **kwargs: text)
        payload, err = admin_mod._resolve_adhoc({"agent_id": "a1", "task_key": "adhoc"})
        assert err is None
        assert payload["candidate_id"] is None
        monkeypatch.setattr(admin_mod.database, "get_candidate", lambda candidate_id: None)
        payload, err = admin_mod._resolve_adhoc({"agent_id": "a1", "candidate_id": "c1", "task_key": "craft_resume_base"})
        assert payload["api_key_override"] is None
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
                    "api_key_override": None,
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
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: "need key")
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
        monkeypatch.setattr(admin_mod, "_candidate_dispatch_api_key_error", lambda candidate_id: None)
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
                    "api_key_override": None,
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
                    "api_key_override": None,
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
