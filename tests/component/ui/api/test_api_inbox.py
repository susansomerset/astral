"""Component tests for src/ui/api/api_inbox.py (AST-1033)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_inbox as inbox_mod


# Branches: list 200; list 502; get 200; get 400 blank id; get 502; auth 401/403.
class TestAst1033InboxApi:
    def test_list_messages_ok(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
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
        monkeypatch.setattr(inbox_mod, "list_inbox_messages", MagicMock(return_value=rows))
        resp = inbox_client.get("/api/admin/inbox/messages", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"messages": rows}

    def test_list_messages_upstream_failure_502(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod, "list_inbox_messages", MagicMock(side_effect=RuntimeError("gmail down"))
        )
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        resp = inbox_client.get("/api/admin/inbox/messages", headers=auth_headers)
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "gmail down"}
        warn.assert_called_once()

    def test_get_message_ok(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(return_value={"id": "m1", "html_body": "<p>x</p>"}),
        )
        resp = inbox_client.get("/api/admin/inbox/messages/m1", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"id": "m1", "html_body": "<p>x</p>"}

    def test_get_message_blank_id_400(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = inbox_client.get("/api/admin/inbox/messages/%20%20", headers=auth_headers)
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "message_id is required"}

    def test_get_message_upstream_failure_502(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod, "get_message_html", MagicMock(side_effect=RuntimeError("get boom"))
        )
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        resp = inbox_client.get("/api/admin/inbox/messages/m9", headers=auth_headers)
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "get boom"}
        warn.assert_called_once()
        assert "m9" in warn.call_args.args

    def test_list_requires_auth(self, inbox_client: FlaskClient) -> None:
        assert inbox_client.get("/api/admin/inbox/messages").status_code == 401

    def test_list_non_admin_forbidden(
        self, inbox_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        assert (
            inbox_client.get("/api/admin/inbox/messages", headers=non_admin_headers).status_code
            == 403
        )

    def test_get_requires_auth(self, inbox_client: FlaskClient) -> None:
        assert inbox_client.get("/api/admin/inbox/messages/m1").status_code == 401

    def test_get_non_admin_forbidden(
        self, inbox_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        assert (
            inbox_client.get("/api/admin/inbox/messages/m1", headers=non_admin_headers).status_code
            == 403
        )
