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
                "candidate_match": {"matched": False, "astral_candidate_id": None},
            }
        ]
        list_mock = MagicMock(return_value=rows)
        monkeypatch.setattr(inbox_mod, "list_inbox_messages", list_mock)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        resp = inbox_client.get("/api/admin/inbox/messages", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"messages": rows}
        list_mock.assert_called_once_with(debug=False)

    def test_list_passes_ui_llm_debug(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        list_mock = MagicMock(return_value=[])
        monkeypatch.setattr(inbox_mod, "list_inbox_messages", list_mock)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=True))
        resp = inbox_client.get("/api/admin/inbox/messages?debug=1", headers=auth_headers)
        assert resp.status_code == 200
        list_mock.assert_called_once_with(debug=True)

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


# AST-1049: POST create-job orchestration endpoint.
# AST-1061: multi created/skipped payload; 201 if any created, 200 if only skips.
class TestAst1049InboxCreateJobApi:
    def test_create_job_201(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        created_row = {
            "astral_job_id": "job-1",
            "company": "meteorite-cand-1",
            "state": "METEORITE_NEW",
            "latest_score": 10.0,
            "company_inserted": True,
        }
        create = MagicMock(
            return_value={
                "astral_job_id": "job-1",
                "company": "meteorite-cand-1",
                "state": "METEORITE_NEW",
                "latest_score": 10.0,
                "company_inserted": True,
                "astral_candidate_id": "cand-1",
                "mode": "body",
                "created": [created_row],
                "skipped": [],
            }
        )
        monkeypatch.setattr(inbox_mod, "create_meteorite_job_from_inbox_message", create)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        resp = inbox_client.post(
            "/api/admin/inbox/messages/m1/create-job",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["astral_job_id"] == "job-1"
        assert body["astral_candidate_id"] == "cand-1"
        assert body["mode"] == "body"
        assert body["created"] == [
            {
                "astral_job_id": "job-1",
                "company": "meteorite-cand-1",
                "state": "METEORITE_NEW",
                "latest_score": 10.0,
                "company_inserted": True,
            }
        ]
        assert body["skipped"] == []
        create.assert_called_once_with("m1", debug=False)

    def test_create_job_all_skipped_200(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        skipped = [
            {
                "reason": "known_job_link",
                "url": "https://jobs.example.com/x",
                "matched_company_job_id": None,
            }
        ]
        create = MagicMock(
            return_value={
                "astral_job_id": None,
                "company": "meteorite-cand-1",
                "state": None,
                "latest_score": None,
                "company_inserted": False,
                "astral_candidate_id": "cand-1",
                "mode": "links",
                "created": [],
                "skipped": skipped,
            }
        )
        monkeypatch.setattr(inbox_mod, "create_meteorite_job_from_inbox_message", create)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        resp = inbox_client.post(
            "/api/admin/inbox/messages/m1/create-job",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["created"] == []
        assert body["skipped"] == skipped
        assert body["astral_job_id"] is None

    def test_create_job_passes_debug(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        create = MagicMock(
            return_value={
                "astral_job_id": "job-1",
                "company": "meteorite-cand-1",
                "state": "METEORITE_NEW",
                "latest_score": 10.0,
                "company_inserted": False,
                "astral_candidate_id": "cand-1",
                "mode": "body",
                "created": [
                    {
                        "astral_job_id": "job-1",
                        "company": "meteorite-cand-1",
                        "state": "METEORITE_NEW",
                        "latest_score": 10.0,
                        "company_inserted": False,
                    }
                ],
                "skipped": [],
            }
        )
        monkeypatch.setattr(inbox_mod, "create_meteorite_job_from_inbox_message", create)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=True))
        resp = inbox_client.post(
            "/api/admin/inbox/messages/m1/create-job?debug=1",
            headers=auth_headers,
            json={"debug": True},
        )
        assert resp.status_code == 201
        create.assert_called_once_with("m1", debug=True)

    def test_create_job_value_error_400(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "create_meteorite_job_from_inbox_message",
            MagicMock(side_effect=ValueError("message is not matched to a candidate")),
        )
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        resp = inbox_client.post(
            "/api/admin/inbox/messages/m1/create-job",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "message is not matched to a candidate"}

    def test_create_job_blank_id_400(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = inbox_client.post(
            "/api/admin/inbox/messages/%20%20/create-job",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "message_id is required"}

    def test_create_job_upstream_502(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "create_meteorite_job_from_inbox_message",
            MagicMock(side_effect=RuntimeError("gmail down")),
        )
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        resp = inbox_client.post(
            "/api/admin/inbox/messages/m1/create-job",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "gmail down"}
        warn.assert_called_once()

    def test_create_job_requires_auth(self, inbox_client: FlaskClient) -> None:
        assert (
            inbox_client.post("/api/admin/inbox/messages/m1/create-job", json={}).status_code
            == 401
        )

    def test_create_job_non_admin_forbidden(
        self, inbox_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        assert (
            inbox_client.post(
                "/api/admin/inbox/messages/m1/create-job",
                headers=non_admin_headers,
                json={},
            ).status_code
            == 403
        )
