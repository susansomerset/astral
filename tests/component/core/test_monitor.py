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
    # AST-2214 AC 1/2/4: header before the fence, WARNING/ERROR-only body, full log attached oldest-first.
    _MIXED_ROWS = [
        {"created_at": "t1", "level": "DEBUG", "message": "dbg-msg"},
        {"created_at": "t2", "level": "INFO", "message": "info-msg"},
        {"created_at": "t3", "level": "WARNING", "message": "warn-msg"},
        {"created_at": "t4", "level": "ERROR", "message": "err-msg"},
    ]

    def test_sends_header_filtered_body_and_full_log_attachment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Isolate deploy-label fallback from host ASTRAL_DEPLOY_ENV.
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        monkeypatch.setattr(monitor_mod.database, "get_candidate", lambda candidate_id: {"last": "Somerset"})
        # DB returns newest-first; monitor reverses to chronological.
        monkeypatch.setattr(
            monitor_mod.database, "list_log_entries", lambda batch_id: list(reversed(self._MIXED_ROWS)),
        )
        send = MagicMock(return_value=True)
        monkeypatch.setattr(monitor_mod, "send_email", send)

        monitor_mod.auto_run_error(
            "qualify_job_listings",
            "batch-1",
            {"total_errors": 2, "total_processed": 5, "total_passed": 3, "total_failed": 0},
            "failure",
            "cand-1",
        )

        send.assert_called_once()
        kw = send.call_args.kwargs
        assert kw["subject"].startswith("[Astral/Somerset] qualify_job_listings failure:")
        lines = kw["body"].splitlines()
        # AC 1: six labelled header lines, in order, ahead of the fence
        assert lines[:6] == [
            "Deploy: Astral",
            "Candidate: cand-1 (Somerset)",
            "Task: qualify_job_listings",
            "Batch: batch-1",
            "Status: failure",
            "Processed: 5  Passed: 3  Failed: 0  Errors: 2",
        ]
        # AC 2: blank separator, then a fence holding only WARNING + ERROR rows
        assert lines[6:] == ["", "```", "t3  [WARNING]  warn-msg", "t4  [ERROR]  err-msg", "```"]
        assert "dbg-msg" not in kw["body"] and "info-msg" not in kw["body"]
        # AC 4: exactly one <batch_id>.txt attachment, every level, oldest first
        assert kw["attachments"] == {
            "batch-1.txt": "t1  [DEBUG]  dbg-msg\nt2  [INFO]  info-msg\nt3  [WARNING]  warn-msg\nt4  [ERROR]  err-msg",
        }

    def test_logs_when_send_email_returns_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: [])
        monkeypatch.setattr(monitor_mod, "send_email", MagicMock(return_value=False))

        monitor_mod.auto_run_error("task", "batch-2", {"total_errors": 1, "total_processed": 0}, "failure")

    def test_swallows_unexpected_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: (_ for _ in ()).throw(RuntimeError("boom")))

        monitor_mod.auto_run_error("task", "batch-3", {"total_errors": 1, "total_processed": 0}, "failure")


# Branches: deploy label from env; Astral fallback; last-name suffix; blank `last` column; missing row.
class TestAutoRunErrorSubjectPrefix:
    def test_local_env_with_candidate_last_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        monkeypatch.setattr(
            monitor_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "last": "Somerset",  # name column (AST-1014), not candidate_data.profile
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
                "last": "Nguyen",
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
                "last": "Somerset",  # name column (AST-1014), not candidate_data.profile
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
        monkeypatch.setattr(monitor_mod.database, "get_candidate", lambda candidate_id: {"last": "  "})
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-no-last", {"total_errors": 1, "total_processed": 0}, "failure", "cand-4")

        assert send.call_args.kwargs["subject"].startswith("[local] task failure:")

    def test_missing_candidate_row_omits_suffix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        monkeypatch.setattr(monitor_mod.database, "get_candidate", lambda candidate_id: None)
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-no-row", {"total_errors": 1, "total_processed": 0}, "failure", "missing")

        assert send.call_args.kwargs["subject"].startswith("[staging] task failure:")


# Branches (AST-2214): no WARNING/ERROR rows -> notice, no fence; no rows at all -> attachment placeholder;
# header '-' for missing candidate / counts; bare candidate id when no last name; fence outruns inner backticks.
class TestAst2214AlertShape:
    def test_info_only_rows_give_notice_not_empty_fence(
        self, log_entries: List[Dict[str, Any]], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # AC 3: conftest log_entries carries an ERROR row; keep only the INFO one
        info_only = [e for e in log_entries if e["level"] == "INFO"]
        monkeypatch.setattr(monitor_mod.database, "list_log_entries", lambda batch_id: info_only)
        send = MagicMock(return_value=True)
        monkeypatch.setattr(monitor_mod, "send_email", send)

        monitor_mod.auto_run_error("task", "batch-info", {"total_errors": 1, "total_processed": 1}, "failure")

        kw = send.call_args.kwargs
        assert kw["body"].splitlines()[-1] == "(no WARNING or ERROR entries for this batch)"
        assert "```" not in kw["body"]
        # INFO row still rides in the attachment
        assert kw["attachments"] == {"batch-info.txt": "2026-05-13 12:00:00  [INFO]  older"}

    def test_no_rows_still_attaches_placeholder(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send = _stub_alert(monkeypatch)

        monitor_mod.auto_run_error("task", "batch-empty", {"total_errors": 1, "total_processed": 0}, "failure")

        assert send.call_args.kwargs["attachments"] == {"batch-empty.txt": "(no log entries found for this batch)"}

    def test_header_dashes_for_missing_values(self) -> None:
        header = monitor_mod._format_alert_header("", "", None, "", "", "", {}).splitlines()
        assert header == [
            "Deploy: -",
            "Candidate: -",
            "Task: -",
            "Batch: -",
            "Status: -",
            "Processed: -  Passed: -  Failed: -  Errors: -",
        ]

    def test_header_bare_candidate_id_without_last_name(self) -> None:
        header = monitor_mod._format_alert_header("local", " cand-9 ", None, "t", "b", "failure", {}).splitlines()
        assert header[1] == "Candidate: cand-9"

    def test_fence_outruns_backticks_inside_the_logs(self) -> None:
        entries = [{"created_at": "t1", "level": "ERROR", "message": "raw ```json {} ```` tail"}]
        lines = monitor_mod._format_warning_error_block(entries).splitlines()
        assert lines[0] == "`````" and lines[-1] == "`````"  # longest inner run is 4
        assert "```json" in lines[1]


# Branches: subject names the task's own server label (AST-1880); short body (no log dump); Held line only when held > 0;
# send_email False logged; unexpected exception swallowed; AST-2214 admin recipient (sorted join), empty admin -> WARNING, no send.
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
        # AST-2214: balance alerts go to the admin(s); test env has none configured
        monkeypatch.setitem(monitor_mod.AUTH_CONFIG, "admin_emails", frozenset({"admin@example.com"}))
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
        # AST-2214 AC 5: admin, not the support alias; no log, no attachment
        assert kw["to"] == "admin@example.com"
        assert kw["to"] != monitor_mod.ASTRAL_CONFIG["support_email"]
        assert "attachments" not in kw
        list_logs.assert_not_called()

    def test_no_admin_configured_warns_once_and_skips_send(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send = self._stub(monkeypatch)
        monkeypatch.setitem(monitor_mod.AUTH_CONFIG, "admin_emails", frozenset())
        log = MagicMock()
        monkeypatch.setattr(monitor_mod, "logger", log)

        monitor_mod.provider_balance_outage("task", "b-6", dict(self._ACC), {"error": self._REFUSAL_ERR, "held": 0})

        send.assert_not_called()
        log.warning.assert_called_once()
        assert "ASTRAL_ADMIN_EMAILS" in log.warning.call_args.args[0]
        assert log.warning.call_args.args[1] == "b-6"

    def test_multiple_admins_joined_in_sorted_order(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send = self._stub(monkeypatch)
        monkeypatch.setitem(monitor_mod.AUTH_CONFIG, "admin_emails", frozenset({"zed@example.com", "amy@example.com"}))

        monitor_mod.provider_balance_outage("task", "b-7", dict(self._ACC), {"error": self._REFUSAL_ERR, "held": 0})

        assert send.call_args.kwargs["to"] == "amy@example.com, zed@example.com"

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
