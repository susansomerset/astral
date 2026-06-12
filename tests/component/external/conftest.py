"""Shared external-layer mocks for component tests (AST-391 canon for core)."""

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

import pytest

# Gmail validates env at import time — set defaults before any gmail import in this tree.
os.environ.setdefault("GMAIL_USER", "astral.test@example.com")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test-refresh-token")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")


class FakeAnthropicMessage:
    def __init__(self, text: str, *, stop_reason: str = "end_turn", usage: Optional[Any] = None) -> None:
        self.content = [SimpleNamespace(text=text)]
        self.stop_reason = stop_reason
        self.id = "msg_test"
        self.usage = usage or SimpleNamespace(
            input_tokens=10,
            output_tokens=5,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
        )


class FakeAnthropicClient:
    def __init__(self, *, response_text: str = '{"ok": true}', raise_on_create: Optional[Exception] = None) -> None:
        self._response_text = response_text
        self._raise_on_create = raise_on_create
        self.messages = self

    def create(self, **_kwargs: Any) -> FakeAnthropicMessage:
        if self._raise_on_create:
            raise self._raise_on_create
        return FakeAnthropicMessage(self._response_text)


@pytest.fixture
def fake_anthropic_client() -> Callable[..., FakeAnthropicClient]:
    def _factory(**kwargs: Any) -> FakeAnthropicClient:
        return FakeAnthropicClient(**kwargs)

    return _factory


@pytest.fixture
def fake_gmail_service() -> Dict[str, Any]:
    calls: List[Dict[str, Any]] = []

    class _Send:
        def execute(self) -> Dict[str, str]:
            calls.append({"sent": True})
            return {"id": "msg-1"}

    class _Messages:
        def send(self, **kwargs: Any) -> _Send:
            calls.append(kwargs)
            return _Send()

    class _Users:
        def messages(self) -> _Messages:
            return _Messages()

    service = SimpleNamespace(users=lambda: _Users())
    return {"service": service, "calls": calls}
