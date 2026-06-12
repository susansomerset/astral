"""Component tests for src/core/monitor.py (AST-393)."""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from src.core import monitor as monitor_mod


# Branches: send_email ok; send_email False; unexpected exception swallowed.
class TestAutoRunError:
    def test_sends_alert_with_log_body(self, log_entries: List[Dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
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
