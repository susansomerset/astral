"""Component tests for src/core/bootstrap.py (AST-654 / AST-960)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import bootstrap as bootstrap_mod
from src.utils import config as cfg


class TestValidateRuntimeCoupling:
    # Branches: validate_llm_provider_environment success / failure;
    # empty task_keys; task key missing from TASK_CONFIG;
    # live coupling passes without schedulable-frozenset inventory (AST-960).

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
        with pytest.raises(RuntimeError, match="no task keys"):
            bootstrap_mod._validate_runtime_coupling()

    def test_raises_when_task_key_missing_from_task_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(bootstrap_mod, "validate_llm_provider_environment", lambda: None)
        monkeypatch.setattr(bootstrap_mod, "get_task_keys", lambda: ["orphan_key"])
        monkeypatch.setattr(bootstrap_mod, "TASK_CONFIG", {"real_key": {}})
        with pytest.raises(RuntimeError, match="task key 'orphan_key' missing"):
            bootstrap_mod._validate_runtime_coupling()

    def test_passes_when_coupling_is_aligned(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(bootstrap_mod, "validate_llm_provider_environment", lambda: None)
        monkeypatch.setattr(bootstrap_mod, "get_task_keys", lambda: ["agent_a"])
        monkeypatch.setattr(bootstrap_mod, "TASK_CONFIG", {"agent_a": {}})
        bootstrap_mod._validate_runtime_coupling()

    def test_passes_with_live_task_config_without_gap_key_inventory(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-960: gap keys (e.g. fetch_jd) live in gazer/roster config only — not TASK_CONFIG.
        # Bootstrap must not invent a parallel inventory that requires them for boot.
        monkeypatch.setattr(bootstrap_mod, "validate_llm_provider_environment", lambda: None)
        assert "fetch_jd" not in cfg.TASK_CONFIG
        assert "prefilter" not in cfg.TASK_CONFIG
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
        monkeypatch.setattr(
            bootstrap_mod.database,
            "ensure_all_upsert_registry_schemas_at_startup",
            lambda: calls.append("schema_ensure"),
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
            "schema_ensure",
            "sync:['craft_resume_base']",
            "scheduler",
        ]
