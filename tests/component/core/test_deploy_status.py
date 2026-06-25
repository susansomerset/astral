"""Component tests for src/core/deploy_status.py (AST-792)."""

from __future__ import annotations

import pytest

from src.core import deploy_status as core_ds
from src.external.linear import LinearApiError


class TestCoreGetDeployStatusPayload:
    def test_payload_includes_filtered_merge_tickets_most_recent_first(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        entries = [
            {"ticket_id": "AST-100", "recorded_at": "2026-01-01T00:00:00+00:00"},
            {"ticket_id": "AST-200", "recorded_at": "2026-01-02T00:00:00+00:00"},
            {"ticket_id": "AST-300", "recorded_at": "2026-01-03T00:00:00+00:00"},
        ]
        monkeypatch.setattr(core_ds, "read_merge_ticket_log", lambda: entries)
        monkeypatch.setattr(
            core_ds,
            "fetch_parent_issue_states",
            lambda _ids: {
                "AST-100": "User Testing",
                "AST-200": "Done",
                "AST-300": "User Testing",
            },
        )
        monkeypatch.setattr(
            core_ds.utils_ds,
            "get_deploy_status_payload",
            lambda: {"uptime": "1m", "uptime_seconds": 60},
        )
        payload = core_ds.get_deploy_status_payload()
        assert [row["ticket_id"] for row in payload["merge_tickets"]] == [
            "AST-300",
            "AST-100",
        ]

    def test_payload_empty_merge_tickets_when_log_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(core_ds, "read_merge_ticket_log", lambda: [])
        monkeypatch.setattr(
            core_ds.utils_ds,
            "get_deploy_status_payload",
            lambda: {"uptime": "1m", "uptime_seconds": 60},
        )
        payload = core_ds.get_deploy_status_payload()
        assert payload["merge_tickets"] == []

    def test_payload_empty_merge_tickets_on_linear_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        entries = [{"ticket_id": "AST-100", "recorded_at": "2026-01-01T00:00:00+00:00"}]
        monkeypatch.setattr(core_ds, "read_merge_ticket_log", lambda: entries)

        def _raise(_ids: list[str]) -> dict[str, str | None]:
            raise LinearApiError("boom")

        monkeypatch.setattr(core_ds, "fetch_parent_issue_states", _raise)
        monkeypatch.setattr(
            core_ds.utils_ds,
            "get_deploy_status_payload",
            lambda: {"uptime": "1m", "uptime_seconds": 60},
        )
        payload = core_ds.get_deploy_status_payload()
        assert payload["merge_tickets"] == []

    def test_payload_excludes_done_parents(self, monkeypatch: pytest.MonkeyPatch) -> None:
        entries = [
            {"ticket_id": "AST-100", "recorded_at": "2026-01-01T00:00:00+00:00"},
            {"ticket_id": "AST-200", "recorded_at": "2026-01-02T00:00:00+00:00"},
        ]
        monkeypatch.setattr(core_ds, "read_merge_ticket_log", lambda: entries)
        monkeypatch.setattr(
            core_ds,
            "fetch_parent_issue_states",
            lambda _ids: {"AST-100": "User Testing", "AST-200": "Done"},
        )
        monkeypatch.setattr(
            core_ds.utils_ds,
            "get_deploy_status_payload",
            lambda: {"uptime": "1m", "uptime_seconds": 60},
        )
        payload = core_ds.get_deploy_status_payload()
        assert payload["merge_tickets"] == [entries[0]]
