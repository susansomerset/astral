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
        body_lines = kwargs["body"].splitlines()
        assert body_lines[0] == "```" and body_lines[-1] == "```"
        assert body_lines[1].endswith("older")
        assert body_lines[-2].endswith("newer")

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
        lines = body.splitlines()
        assert lines[0] == "```" and lines[-1] == "```"  # fenced for Linear
        assert lines[1].endswith("older")
        assert lines[-2].endswith("newer")

    def test_fence_outruns_backticks_inside_the_logs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entries = [{"created_at": "t1", "level": "ERROR", "message": "raw ```json {} ```` tail"}]
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: entries)
        lines = monitor_mod._format_log_body("batch-z").splitlines()
        assert lines[0] == "`````" and lines[-1] == "`````"  # longest inner run is 4
        assert "```json" in lines[1]


# Branches: subject names the task's own server label (AST-1880); short body (no log dump); Held line only when held > 0;
# send_email False logged; unexpected exception swallowed.
class TestAst1867ProviderBalanceOutage:
    """AST-1867 / AST-1870: one short alert per AUTO run stopped by a provider balance refusal."""

    _REFUSAL_ERR = "Error code: 402 - Insufficient Balance"
    _ACC = {"total_processed": 1, "total_passed": 0, "total_failed": 0, "total_errors": 0}

    @staticmethod
    def _stub(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        # direct patches keep the subject independent of host env / candidate DB
        # AST-1880: provider label comes from the refused task's agent server, not a global setting
        monkeypatch.setattr(monitor_mod, "task_llm_server_id", lambda task_key: "deepseek")
        monkeypatch.setattr(monitor_mod, "get_deploy_label", lambda: "local")
        monkeypatch.setattr(monitor_mod, "_resolve_candidate_last_name", lambda cid: "Somerset")
        return _stub_alert(monkeypatch)

    def test_subject_names_provider_and_body_is_short(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send = self._stub(monkeypatch)
        list_logs = MagicMock(return_value=[])
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", list_logs)

        monitor_mod.provider_balance_outage(
            "select_job_page", "b-1", dict(self._ACC), {"error": self._REFUSAL_ERR, "held": 2}, "cand-1",
        )

        kw = send.call_args.kwargs
        assert kw["subject"] == "[local/Somerset] DeepSeek insufficient balance — select_job_page stopped | b-1"
        assert kw["body"].splitlines() == [
            "Provider: DeepSeek",
            f"Refusal: {self._REFUSAL_ERR}",
            "Task: select_job_page   Batch: b-1",
            "Processed: 1  Passed: 0  Failed: 0  Errors: 0",
            "Held (state unchanged): 2",
            "Entity state was held; the task stays enabled and resumes once provider credit is restored.",
        ]
        assert kw["to"] == monitor_mod.ASTRAL_CONFIG["support_email"]
        # no batch log dump
        list_logs.assert_not_called()

    def test_provider_label_resolved_from_refused_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send = self._stub(monkeypatch)
        seen: List[str] = []
        monkeypatch.setattr(monitor_mod, "task_llm_server_id", lambda task_key: seen.append(task_key) or "openrouter")

        monitor_mod.provider_balance_outage(
            "evaluate_jd", "b-5", dict(self._ACC), {"error": self._REFUSAL_ERR, "held": 0}, "cand-1",
        )

        assert seen == ["evaluate_jd"]
        assert " OpenRouter insufficient balance — evaluate_jd stopped" in send.call_args.kwargs["subject"]
        assert send.call_args.kwargs["body"].splitlines()[0] == "Provider: OpenRouter"

    def test_held_line_omitted_when_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send = self._stub(monkeypatch)

        monitor_mod.provider_balance_outage(
            "evaluate_jd", "b-2", dict(self._ACC), {"error": self._REFUSAL_ERR, "held": 0}, "cand-1",
        )

        assert not any(ln.startswith("Held") for ln in send.call_args.kwargs["body"].splitlines())

    def test_logs_when_send_email_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub(monkeypatch)
        monkeypatch.setattr(monitor_mod, "send_email", MagicMock(return_value=False))

        monitor_mod.provider_balance_outage("task", "b-3", dict(self._ACC), {"error": self._REFUSAL_ERR, "held": 1})

    def test_swallows_unexpected_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send = self._stub(monkeypatch)

        def _boom(task_key: str) -> str:
            raise ValueError("no agent")

        monkeypatch.setattr(monitor_mod, "task_llm_server_id", _boom)

        monitor_mod.provider_balance_outage("task", "b-4", dict(self._ACC), {"error": self._REFUSAL_ERR, "held": 1})

        send.assert_not_called()
