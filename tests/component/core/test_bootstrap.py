"""Component tests for src/core/bootstrap.py (AST-654)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import bootstrap as bootstrap_mod


class TestValidateRuntimeCoupling:
    # Branches: validate_llm_provider_environment success / failure;
    # empty task_keys; task key missing from TASK_CONFIG;
    # dispatch schedulable key missing from TASK_CONFIG.

    def test_raises_when_llm_environment_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            bootstrap_mod,
            "validate_llm_provider_environment",
            MagicMock(side_effect=RuntimeError("missing LLM key")),
        )
        with pytest.raises(RuntimeError, match="missing LLM key"):
            bootstrap_mod._validate_runtime_coupling()

    def test_raises_when_task_config_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(bootstrap_mod, "validate_llm_provider_environment", lambda: None)
        monkeypatch.setattr(bootstrap_mod, "get_task_keys", lambda: [])
        monkeypatch.setattr(bootstrap_mod, "DISPATCH_SCHEDULABLE_TASK_KEYS", frozenset())
        with pytest.raises(RuntimeError, match="no task keys"):
            bootstrap_mod._validate_runtime_coupling()

    def test_raises_when_task_key_missing_from_task_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(bootstrap_mod, "validate_llm_provider_environment", lambda: None)
        monkeypatch.setattr(bootstrap_mod, "get_task_keys", lambda: ["orphan_key"])
        monkeypatch.setattr(bootstrap_mod, "TASK_CONFIG", {"real_key": {}})
        monkeypatch.setattr(bootstrap_mod, "DISPATCH_SCHEDULABLE_TASK_KEYS", frozenset())
        with pytest.raises(RuntimeError, match="task key 'orphan_key' missing"):
            bootstrap_mod._validate_runtime_coupling()

    def test_raises_when_dispatch_key_missing_from_task_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(bootstrap_mod, "validate_llm_provider_environment", lambda: None)
        monkeypatch.setattr(bootstrap_mod, "get_task_keys", lambda: ["agent_a"])
        monkeypatch.setattr(bootstrap_mod, "TASK_CONFIG", {"agent_a": {}})
        monkeypatch.setattr(
            bootstrap_mod, "DISPATCH_SCHEDULABLE_TASK_KEYS", frozenset({"dispatch_x"})
        )
        with pytest.raises(RuntimeError, match="dispatch schedulable key 'dispatch_x' missing"):
            bootstrap_mod._validate_runtime_coupling()

    def test_passes_when_coupling_is_aligned(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(bootstrap_mod, "validate_llm_provider_environment", lambda: None)
        monkeypatch.setattr(bootstrap_mod, "get_task_keys", lambda: ["agent_a"])
        monkeypatch.setattr(bootstrap_mod, "TASK_CONFIG", {"agent_a": {}, "dispatch_x": {}})
        monkeypatch.setattr(
            bootstrap_mod, "DISPATCH_SCHEDULABLE_TASK_KEYS", frozenset({"dispatch_x"})
        )
        bootstrap_mod._validate_runtime_coupling()


class TestBootstrapRuntime:
    def test_runs_validation_sync_and_scheduler_in_order(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[str] = []

        monkeypatch.setattr(
            bootstrap_mod,
            "_validate_runtime_coupling",
            lambda: calls.append("validate"),
        )
        monkeypatch.setattr(
            bootstrap_mod,
            "apply_repo_admin_json_at_startup",
            lambda: calls.append("repo_json"),
        )
        monkeypatch.setattr(bootstrap_mod, "get_task_keys", lambda: ["craft_resume_base"])
        monkeypatch.setattr(
            bootstrap_mod.database,
            "sync_agent_tasks",
            lambda keys: calls.append(f"sync:{keys!r}"),
        )
        monkeypatch.setattr(
            bootstrap_mod,
            "start_scheduler",
            lambda: calls.append("scheduler"),
        )

        bootstrap_mod.bootstrap_runtime()

        assert calls == [
            "validate",
            "repo_json",
            "sync:['craft_resume_base']",
            "scheduler",
        ]
