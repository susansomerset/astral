"""Component tests for src/utils/deploy_status.py (AST-646)."""

from __future__ import annotations

import pytest

from src.utils import deploy_status as ds


class TestFormatUptimeSeconds:
    def test_under_one_minute(self) -> None:
        assert ds.format_uptime_seconds(30) == "<1m"
        assert ds.format_uptime_seconds(59.9) == "<1m"

    def test_minutes_only_under_one_hour(self) -> None:
        assert ds.format_uptime_seconds(60) == "1m"
        assert ds.format_uptime_seconds(5 * 60 + 30) == "5m"

    def test_hours_and_minutes_under_one_day(self) -> None:
        assert ds.format_uptime_seconds(75 * 60) == "1h15m"

    def test_days_with_zero_padded_minutes(self) -> None:
        assert ds.format_uptime_seconds(3 * 86400 + 22 * 3600 + 7 * 60) == "3d22h07m"


class TestGetDeployLabel:
    def test_returns_env_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        assert ds.get_deploy_label() == "local"

    def test_returns_astral_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        assert ds.get_deploy_label() == "Astral"

    def test_returns_astral_when_whitespace_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "   ")
        assert ds.get_deploy_label() == "Astral"


class TestResolveEnvironment:
    def test_unset_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        assert ds._resolve_environment() is None

    def test_valid_local(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        assert ds._resolve_environment() == "local"

    def test_non_allowlisted_value_returns_raw(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "eu-west")
        assert ds._resolve_environment() == "eu-west"

    def test_whitespace_only_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "   ")
        assert ds._resolve_environment() is None


class TestLocalDeployDebug:
    def test_is_local_deploy_env_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        assert ds.is_local_deploy_env() is True

    def test_is_local_deploy_env_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "LOCAL")
        assert ds.is_local_deploy_env() is True

    def test_is_local_deploy_env_false_for_staging(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        assert ds.is_local_deploy_env() is False

    def test_is_local_deploy_env_false_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        assert ds.is_local_deploy_env() is False

    def test_ui_llm_debug_explicit_overrides_non_local(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        assert ds.ui_llm_debug(explicit_debug=True) is True

    def test_ui_llm_debug_local_without_explicit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        assert ds.ui_llm_debug() is True

    def test_ui_llm_debug_false_non_local_no_explicit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        assert ds.ui_llm_debug() is False


class TestGetDeployStatusPayload:
    def test_includes_uptime_without_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        monkeypatch.setattr(ds, "_PROCESS_BOOT_TIME", 1_000_000.0)
        monkeypatch.setattr("time.time", lambda: 1_000_045.0)
        payload = ds.get_deploy_status_payload()
        assert payload["uptime"] == "<1m"
        assert payload["uptime_seconds"] == 45
        assert "environment" not in payload
        assert payload["merge_tickets"] == []

    def test_includes_environment_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        monkeypatch.setattr(ds, "_PROCESS_BOOT_TIME", 0.0)
        monkeypatch.setattr("time.time", lambda: 3661.0)
        payload = ds.get_deploy_status_payload()
        assert payload["environment"] == "staging"
        assert payload["uptime"] == "1h1m"
        assert payload["merge_tickets"] == []

    def test_merge_tickets_most_recent_first(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entries = [
            {"ticket_id": "AST-100", "recorded_at": "2026-01-01T00:00:00+00:00"},
            {"ticket_id": "AST-200", "recorded_at": "2026-01-02T00:00:00+00:00"},
        ]
        monkeypatch.setattr(ds, "read_merge_ticket_log", lambda: entries)
        monkeypatch.setattr(ds, "_PROCESS_BOOT_TIME", 0.0)
        monkeypatch.setattr("time.time", lambda: 10.0)
        payload = ds.get_deploy_status_payload()
        assert payload["merge_tickets"][0]["ticket_id"] == "AST-200"
        assert payload["merge_tickets"][1]["ticket_id"] == "AST-100"

    def test_merge_tickets_empty_when_log_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ds, "read_merge_ticket_log", lambda: [])
        monkeypatch.setattr(ds, "_PROCESS_BOOT_TIME", 0.0)
        monkeypatch.setattr("time.time", lambda: 10.0)
        payload = ds.get_deploy_status_payload()
        assert payload["merge_tickets"] == []
