"""Component tests for src/external/gmail.py (AST-391)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.external import gmail as gmail_mod


# Branches: Gmail API success; any exception returns False.
class TestSendEmail:
    def test_send_email_success(self, monkeypatch, fake_gmail_service) -> None:
        monkeypatch.setattr(gmail_mod, "build", lambda *args, **kwargs: fake_gmail_service["service"])
        assert gmail_mod.send_email("to@example.com", "Subject", "Body") is True
        assert fake_gmail_service["calls"]

    def test_send_email_returns_false_on_failure(self, monkeypatch) -> None:
        def _boom(*_args, **_kwargs):
            raise RuntimeError("api down")

        monkeypatch.setattr(gmail_mod, "build", _boom)
        assert gmail_mod.send_email("to@example.com", "Subject", "Body") is False

    def test_send_email_uses_custom_token_uri(self, monkeypatch, fake_gmail_service) -> None:
        captured: dict = {}

        def _build(_api, _version, credentials=None, **_kwargs):
            captured["token_uri"] = credentials.token_uri
            return fake_gmail_service["service"]

        monkeypatch.setenv("GOOGLE_TOKEN_URI", "https://token.example/oauth2/token")
        monkeypatch.setattr(gmail_mod, "_TOKEN_URI", "https://token.example/oauth2/token")
        monkeypatch.setattr(gmail_mod, "build", _build)
        assert gmail_mod.send_email("to@example.com", "S", "B") is True
        assert captured["token_uri"] == "https://token.example/oauth2/token"
