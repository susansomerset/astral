"""Component tests for src/core/monitor.py (AST-393, AST-667)."""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from src.core import monitor as monitor_mod


def _stub_alert(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: [])
    send = MagicMock(return_value=True)
    monkeypatch.setattr(monitor_mod, "send_email", send)
    return send


# Branches: send_email ok; send_email False; unexpected exception swallowed.
class TestAutoRunError:
    def test_sends_alert_with_log_body(self, log_entries: List[Dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
        # Isolate deploy-label fallback from host ASTRAL_DEPLOY_ENV (AC 3).
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        # DB returns newest-first; monitor reverses for the email body.
        monkeypatch.setattr(
            monitor_mod.database,
            "list_log_entries",
            lambda batch_id: list(reversed(log_entries)),
        )
        send = MagicMock(return_value=True)
        monkeypatch.setattr(monitor_mod, "send_email", send)

        monitor_mod.auto_run_error(
            "qualify_job_listings",
            "batch-1",
            {"total_errors": 2, "total_processed": 5},
            "failure",
        )

        send.assert_called_once()
        _, kwargs = send.call_args
        assert kwargs["subject"].startswith("[Astral] qualify_job_listings failure:")
        assert kwargs["body"].splitlines()[0].endswith("older")
        assert kwargs["body"].splitlines()[-1].endswith("newer")

    def test_logs_when_send_email_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: [])
        monkeypatch.setattr(monitor_mod, "send_email", MagicMock(return_value=False))

        monitor_mod.auto_run_error("task", "batch-2", {"total_errors": 1, "total_processed": 0}, "failure")

    def test_swallows_unexpected_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: (_ for _ in ()).throw(RuntimeError("boom")))

        monitor_mod.auto_run_error("task", "batch-3", {"total_errors": 1, "total_processed": 0}, "failure")


# Branches: deploy label from env; Astral fallback; last-name suffix; missing profile last.
class TestAutoRunErrorSubjectPrefix:
    def test_local_env_with_candidate_last_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        monkeypatch.setattr(
            monitor_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "candidate_data": {"profile": {"last": "Somerset"}},
            },
        )
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error(
            "evaluate_jd",
            "batch-local",
            {"total_errors": 1, "total_processed": 3},
            "failure",
            "cand-1",
        )

        subject = send.call_args.kwargs["subject"]
        assert subject.startswith("[local/Somerset] evaluate_jd failure:")
        assert subject.endswith("| batch-local")

    def test_eu_west_preserves_case(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "eu-west")
        monkeypatch.setattr(
            monitor_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "candidate_data": {"profile": {"last": "Nguyen"}},
            },
        )
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-eu", {"total_errors": 2, "total_processed": 0}, "failure", "cand-2")

        assert send.call_args.kwargs["subject"].startswith("[eu-west/Nguyen] task failure:")

    def test_unset_env_falls_back_to_astral_without_last_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-astral", {"total_errors": 1, "total_processed": 0}, "failure")

        assert send.call_args.kwargs["subject"].startswith("[Astral] task failure:")

    def test_unset_env_with_candidate_last_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        monkeypatch.setattr(
            monitor_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "candidate_data": {"profile": {"last": "Somerset"}},
            },
        )
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-astral-name", {"total_errors": 1, "total_processed": 0}, "failure", "cand-3")

        assert send.call_args.kwargs["subject"].startswith("[Astral/Somerset] task failure:")

    def test_whitespace_env_falls_back_to_astral(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "   ")
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-ws", {"total_errors": 1, "total_processed": 0}, "failure")

        assert send.call_args.kwargs["subject"].startswith("[Astral] task failure:")

    def test_missing_candidate_last_name_omits_suffix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        monkeypatch.setattr(monitor_mod.database, "get_candidate", lambda candidate_id: {"candidate_data": {"profile": {}}})
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-no-last", {"total_errors": 1, "total_processed": 0}, "failure", "cand-4")

        assert send.call_args.kwargs["subject"].startswith("[local] task failure:")

    def test_missing_candidate_row_omits_suffix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        monkeypatch.setattr(monitor_mod.database, "get_candidate", lambda candidate_id: None)
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-no-row", {"total_errors": 1, "total_processed": 0}, "failure", "missing")

        assert send.call_args.kwargs["subject"].startswith("[staging] task failure:")


# Branches: empty log list; chronological formatting.
class TestFormatLogBody:
    def test_returns_placeholder_when_no_entries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: [])
        assert monitor_mod._format_log_body("batch-x") == "(no log entries found for this batch)"

    def test_formats_entries_chronologically(self, log_entries: List[Dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: list(reversed(log_entries)))
        body = monitor_mod._format_log_body("batch-y")
        assert body.splitlines()[0].endswith("older")
        assert body.splitlines()[-1].endswith("newer")
