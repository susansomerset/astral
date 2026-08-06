"""Component tests for src/ui/api/api_slack.py (AST-1069 / AST-1207)."""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.utils.config import CONTACT_CONFIG
from ui.api import api_slack as slack_api


# Branches: Events blueprint passes durable SoT; no ui_llm_debug (AST-1207).
class TestAst1207SlackEventsDebugSot:
    def test_events_post_passes_slack_debug_enabled(
        self, slack_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        sot = MagicMock(return_value=True)
        recv = MagicMock(return_value=(200, ""))
        monkeypatch.setattr(slack_api, "slack_debug_enabled", sot)
        monkeypatch.setattr(slack_api, "receive_slack_events_http", recv)
        resp = slack_client.post(
            f"/api{CONTACT_CONFIG['events_http_path']}",
            data=b"{}",
            headers={
                "X-Slack-Request-Timestamp": "1",
                "X-Slack-Signature": "v0=x",
                "Content-Type": "application/json",
            },
        )
        assert resp.status_code == 200
        sot.assert_called()
        recv.assert_called_once()
        assert recv.call_args.kwargs["debug"] is True

    def test_events_post_passes_debug_false_when_sot_off(
        self, slack_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(slack_api, "slack_debug_enabled", MagicMock(return_value=False))
        recv = MagicMock(return_value=(200, {"challenge": "x"}))
        monkeypatch.setattr(slack_api, "receive_slack_events_http", recv)
        resp = slack_client.post(
            f"/api{CONTACT_CONFIG['events_http_path']}",
            data=b'{"type":"url_verification","challenge":"x"}',
            headers={
                "X-Slack-Request-Timestamp": "1",
                "X-Slack-Signature": "v0=x",
                "Content-Type": "application/json",
            },
        )
        assert resp.status_code == 200
        assert resp.get_json() == {"challenge": "x"}
        assert recv.call_args.kwargs["debug"] is False

    def test_module_does_not_import_ui_llm_debug(self) -> None:
        # Docstring may mention ui_llm_debug as the retired SoT — ban the import only.
        src = inspect.getsource(slack_api)
        assert "from src.utils.deploy_status import ui_llm_debug" not in src
        assert "import ui_llm_debug" not in src
        assert "slack_debug_enabled" in src
        assert hasattr(slack_api, "slack_debug_enabled")
        assert not hasattr(slack_api, "ui_llm_debug")
