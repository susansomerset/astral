"""Component tests for src/ui/api/api_slack.py (AST-1069)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_slack as slack_api
from src.utils.config import CONTACT_CONFIG


# Branches: challenge 200 JSON; event ack 200 empty; 401 bad sig; path from config.
class TestAst1069SlackEventsApi:
    def test_challenge_ok(
        self, slack_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            slack_api,
            "receive_slack_events_http",
            MagicMock(return_value=(200, {"challenge": "ch"})),
        )
        monkeypatch.setattr(slack_api, "ui_llm_debug", MagicMock(return_value=False))
        path = "/api" + CONTACT_CONFIG["events_http_path"]
        resp = slack_client.post(path, data=b"{}", content_type="application/json")
        assert resp.status_code == 200
        assert resp.get_json() == {"challenge": "ch"}

    def test_event_ack_empty_body(
        self, slack_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            slack_api,
            "receive_slack_events_http",
            MagicMock(return_value=(200, "")),
        )
        monkeypatch.setattr(slack_api, "ui_llm_debug", MagicMock(return_value=False))
        path = "/api" + CONTACT_CONFIG["events_http_path"]
        resp = slack_client.post(path, data=b'{"type":"event_callback"}')
        assert resp.status_code == 200
        assert resp.data == b""

    def test_unauthorized(
        self, slack_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            slack_api,
            "receive_slack_events_http",
            MagicMock(return_value=(401, "")),
        )
        monkeypatch.setattr(slack_api, "ui_llm_debug", MagicMock(return_value=False))
        path = "/api" + CONTACT_CONFIG["events_http_path"]
        resp = slack_client.post(path, data=b"{}")
        assert resp.status_code == 401
