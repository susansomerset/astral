"""Component tests for src/core/inbox.py (AST-1032)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import inbox as inbox_mod


# Branches: success passthrough; log + re-raise on failure.
class TestListInboxMessages:
    def test_returns_external_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            {
                "id": "m1",
                "thread_id": "t1",
                "subject": "Hi",
                "from_address": "a@x",
                "date": "Mon",
                "unread": True,
            }
        ]
        monkeypatch.setattr(inbox_mod, "external_list_inbox_messages", MagicMock(return_value=rows))
        assert inbox_mod.list_inbox_messages() == rows

    def test_logs_and_reraises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "external_list_inbox_messages",
            MagicMock(side_effect=RuntimeError("list fail")),
        )
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        with pytest.raises(RuntimeError, match="list fail"):
            inbox_mod.list_inbox_messages()
        warn.assert_called_once()
        assert "list_inbox_messages failed" in warn.call_args.args[0]


# Branches: success passthrough; log + re-raise on failure (includes message id).
class TestGetMessageHtml:
    def test_returns_external_payload(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {"id": "m1", "html_body": "<p>x</p>"}
        monkeypatch.setattr(inbox_mod, "external_get_message_html", MagicMock(return_value=payload))
        assert inbox_mod.get_message_html("m1") == payload

    def test_logs_and_reraises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "external_get_message_html",
            MagicMock(side_effect=RuntimeError("get fail")),
        )
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        with pytest.raises(RuntimeError, match="get fail"):
            inbox_mod.get_message_html("m9")
        warn.assert_called_once()
        assert "get_message_html failed" in warn.call_args.args[0]
        assert warn.call_args.args[1] == "m9"
