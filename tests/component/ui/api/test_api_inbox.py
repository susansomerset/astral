"""Component tests for src/ui/api/api_inbox.py (AST-1033 / AST-1558)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_inbox as inbox_mod


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
        list_mock = MagicMock(return_value=rows)
        monkeypatch.setattr(inbox_mod, "list_inbox_messages", list_mock)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        resp = inbox_client.get("/api/admin/inbox/messages", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"messages": rows}
        list_mock.assert_called_once_with(debug=False)

    def test_list_with_candidate_id(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [{"id": "m1", "from_address": "ada@ex.com"}]
        aliases_mock = MagicMock(return_value=["ada@ex.com"])
        fetch_mock = MagicMock(return_value=rows)
        monkeypatch.setattr(inbox_mod, "_email_aliases_for_candidate", aliases_mock)
        monkeypatch.setattr(inbox_mod, "fetch_candidate_email", fetch_mock)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        resp = inbox_client.get(
            "/api/admin/inbox/messages?candidate_id=cand-ada", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.get_json() == {"messages": rows}
        aliases_mock.assert_called_once_with("cand-ada")
        fetch_mock.assert_called_once_with(["ada@ex.com"], debug=False)

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
        payload = {"id": "m1", "html_body": "<p>x</p>", "assembled_html": "<p>assembled</p>"}
        monkeypatch.setattr(
            inbox_mod,
            "get_message_with_assembled_html",
            MagicMock(return_value=payload),
        )
        resp = inbox_client.get("/api/admin/inbox/messages/m1", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == payload

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
            inbox_mod,
            "get_message_with_assembled_html",
            MagicMock(side_effect=RuntimeError("get boom")),
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


class TestAst1049InboxCreateJobApiRetired:
    def test_create_job_returns_404(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = inbox_client.post(
            "/api/admin/inbox/messages/m1/create-job",
            headers=auth_headers,
            json={},
        )
        assert resp.status_code == 404


class TestAst1558InboxLandMeteoriteApi:
    def test_land_meteorite_requires_candidate_id_400(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = inbox_client.post(
            "/api/admin/inbox/land-meteorite",
            headers=auth_headers,
            json={"message_ids": ["m1"]},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "candidate_id is required"}

    def test_land_meteorite_happy_path(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1611 [bug-repro]: Land → ingest; landable classify+insert counts passed (not failed)."""
        landable = "single_jd_no_link"
        ingest = AsyncMock(
            return_value={
                "message_id": "m1",
                "outcome": landable,
                "astral_candidate_id": "cand-1",
                "job_count": 1,
                "error": None,
            }
        )
        monkeypatch.setattr("src.core.meteorite.ingest_candidate_email_message", ingest)
        stage = AsyncMock()
        monkeypatch.setattr("src.core.meteorite.stage_meteorite", stage)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        resp = inbox_client.post(
            "/api/admin/inbox/land-meteorite",
            headers=auth_headers,
            json={"message_ids": ["m1"], "candidate_id": "cand-1"},
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["total_processed"] == 1
        assert body["total_passed"] == 1
        assert body["total_failed"] == 0
        assert body["results"][0]["message_id"] == "m1"
        assert body["results"][0]["outcome"] == landable
        assert body["results"][0]["astral_candidate_id"] == "cand-1"
        assert body["results"][0].get("error") in (None, "")
        ingest.assert_awaited_once()
        assert ingest.await_args.args[:2] == ("cand-1", "m1")
        stage.assert_not_awaited()

    def test_land_meteorite_passes_debug(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        ingest = AsyncMock(
            return_value={
                "message_id": "m1",
                "outcome": "already_ingested",
                "astral_candidate_id": "cand-1",
                "job_count": 0,
                "error": None,
            }
        )
        monkeypatch.setattr("src.core.meteorite.ingest_candidate_email_message", ingest)
        stage = AsyncMock()
        monkeypatch.setattr("src.core.meteorite.stage_meteorite", stage)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=True))
        resp = inbox_client.post(
            "/api/admin/inbox/land-meteorite?debug=1",
            headers=auth_headers,
            json={"message_ids": ["m1"], "candidate_id": "cand-1", "debug": True},
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["total_passed"] == 1
        ingest.assert_awaited_once()
        assert ingest.await_args.kwargs.get("debug") is True
        stage.assert_not_awaited()

    def test_land_meteorite_rejects_non_list_400(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = inbox_client.post(
            "/api/admin/inbox/land-meteorite",
            headers=auth_headers,
            json={"message_ids": "m1", "candidate_id": "cand-1"},
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "message_ids must be a list"}

    def test_land_meteorite_rejects_empty_400(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        missing = inbox_client.post(
            "/api/admin/inbox/land-meteorite",
            headers=auth_headers,
            json={"candidate_id": "cand-1"},
        )
        assert missing.status_code == 400
        assert missing.get_json() == {"error": "message_ids must be a list"}
        for body in (
            {"message_ids": [], "candidate_id": "cand-1"},
            {"message_ids": ["  ", ""], "candidate_id": "cand-1"},
        ):
            resp = inbox_client.post(
                "/api/admin/inbox/land-meteorite",
                headers=auth_headers,
                json=body,
            )
            assert resp.status_code == 400
            assert resp.get_json() == {"error": "message_ids is required"}

    def test_land_meteorite_upstream_502(
        self, inbox_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        boom = RuntimeError("core boom")
        monkeypatch.setattr(
            "src.core.meteorite.ingest_candidate_email_message",
            AsyncMock(side_effect=boom),
        )
        stage = AsyncMock()
        monkeypatch.setattr("src.core.meteorite.stage_meteorite", stage)
        monkeypatch.setattr(inbox_mod, "ui_llm_debug", MagicMock(return_value=False))
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        resp = inbox_client.post(
            "/api/admin/inbox/land-meteorite",
            headers=auth_headers,
            json={"message_ids": ["m1"], "candidate_id": "cand-1"},
        )
        assert resp.status_code == 502
        assert resp.get_json() == {"error": "core boom"}
        warn.assert_called_once()
        stage.assert_not_awaited()

    def test_land_meteorite_requires_auth(self, inbox_client: FlaskClient) -> None:
        assert (
            inbox_client.post(
                "/api/admin/inbox/land-meteorite",
                json={"message_ids": ["m1"], "candidate_id": "cand-1"},
            ).status_code
            == 401
        )

    def test_land_meteorite_non_admin_forbidden(
        self, inbox_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        assert (
            inbox_client.post(
                "/api/admin/inbox/land-meteorite",
                headers=non_admin_headers,
                json={"message_ids": ["m1"], "candidate_id": "cand-1"},
            ).status_code
            == 403
        )
