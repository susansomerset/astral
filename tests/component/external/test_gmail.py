"""Component tests for src/external/gmail.py (AST-391, AST-1032)."""

from __future__ import annotations

import base64
from types import SimpleNamespace
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from src.external import gmail as gmail_mod


def _b64url(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii").rstrip("=")


def _inbox_service(
    *,
    list_pages: List[Dict[str, Any]],
    metadata_by_id: Optional[Dict[str, Any]] = None,
    full_by_id: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Minimal Gmail users().messages() stub for list/get."""
    calls: List[Dict[str, Any]] = []
    metadata_by_id = metadata_by_id or {}
    full_by_id = full_by_id or {}
    list_iter = iter(list_pages)

    class _Exec:
        def __init__(self, payload: Any) -> None:
            self._payload = payload

        def execute(self) -> Any:
            return self._payload

    class _Messages:
        def list(self, **kwargs: Any) -> _Exec:
            calls.append({"op": "list", **kwargs})
            return _Exec(next(list_iter))

        def get(self, **kwargs: Any) -> _Exec:
            calls.append({"op": "get", **kwargs})
            mid = kwargs["id"]
            if kwargs.get("format") == "full":
                return _Exec(full_by_id[mid])
            return _Exec(metadata_by_id[mid])

        def send(self, **kwargs: Any) -> _Exec:
            calls.append({"op": "send", **kwargs})
            return _Exec({"id": "sent-1"})

    service = SimpleNamespace(users=lambda: SimpleNamespace(messages=lambda: _Messages()))
    return {"service": service, "calls": calls}


# Branches: Gmail API success; any exception returns False; dual-scope creds.
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

    def test_send_email_uses_dual_gmail_scopes(self, monkeypatch, fake_gmail_service) -> None:
        captured: dict = {}

        def _build(_api, _version, credentials=None, **_kwargs):
            captured["scopes"] = list(credentials.scopes or [])
            return fake_gmail_service["service"]

        monkeypatch.setattr(gmail_mod, "build", _build)
        assert gmail_mod.send_email("to@example.com", "S", "B") is True
        assert captured["scopes"] == gmail_mod._GMAIL_SCOPES
        assert "https://www.googleapis.com/auth/gmail.send" in captured["scopes"]
        assert "https://www.googleapis.com/auth/gmail.readonly" in captured["scopes"]


# Branches: empty inbox; pagination; skip bad ids; raise on API failure; unread flag.
class TestListInboxMessages:
    def test_empty_inbox(self, monkeypatch) -> None:
        fake = _inbox_service(list_pages=[{"messages": None}])
        monkeypatch.setattr(gmail_mod, "build", lambda *a, **k: fake["service"])
        assert gmail_mod.list_inbox_messages() == []

    def test_paginates_and_preserves_order(self, monkeypatch) -> None:
        fake = _inbox_service(
            list_pages=[
                {"messages": [{"id": "m1"}, {"id": ""}, {"id": 99}, {"id": "m2"}], "nextPageToken": "p2"},
                {"messages": [{"id": "m3"}]},
            ],
            metadata_by_id={
                "m1": {
                    "id": "m1",
                    "threadId": "t1",
                    "labelIds": ["INBOX", "UNREAD"],
                    "payload": {
                        "headers": [
                            {"name": "Subject", "value": "One"},
                            {"name": "From", "value": "a@x"},
                            {"name": "Date", "value": "Mon, 1 Jan 2026"},
                        ]
                    },
                },
                "m2": {
                    "id": "m2",
                    "labelIds": ["INBOX"],
                    "payload": {"headers": [{"name": "Subject", "value": "Two"}]},
                },
                "m3": {
                    "id": "m3",
                    "threadId": "t3",
                    "labelIds": "UNREAD",  # non-list → unread False
                    "payload": {"headers": "not-a-list"},
                },
            },
        )
        monkeypatch.setattr(gmail_mod, "build", lambda *a, **k: fake["service"])
        rows = gmail_mod.list_inbox_messages()
        assert [r["id"] for r in rows] == ["m1", "m2", "m3"]
        assert rows[0] == {
            "id": "m1",
            "thread_id": "t1",
            "subject": "One",
            "from_address": "a@x",
            "date": "Mon, 1 Jan 2026",
            "unread": True,
        }
        assert rows[1]["unread"] is False
        assert rows[1]["thread_id"] == ""
        assert rows[2]["unread"] is False
        assert rows[2]["subject"] == ""
        list_calls = [c for c in fake["calls"] if c["op"] == "list"]
        assert list_calls[0]["labelIds"] == ["INBOX"]
        assert list_calls[0]["maxResults"] == gmail_mod._LIST_PAGE_SIZE
        assert "pageToken" not in list_calls[0]
        assert list_calls[1]["pageToken"] == "p2"

    def test_non_dict_metadata_payload_yields_empty_fields(self, monkeypatch) -> None:
        fake = _inbox_service(
            list_pages=[{"messages": [{"id": "m9"}]}],
            metadata_by_id={"m9": "not-a-dict"},
        )
        monkeypatch.setattr(gmail_mod, "build", lambda *a, **k: fake["service"])
        rows = gmail_mod.list_inbox_messages()
        assert rows == [
            {
                "id": "",
                "thread_id": "",
                "subject": "",
                "from_address": "",
                "date": "",
                "unread": False,
            }
        ]

    def test_raises_on_list_failure(self, monkeypatch) -> None:
        monkeypatch.setattr(gmail_mod, "build", MagicMock(side_effect=RuntimeError("list boom")))
        with pytest.raises(RuntimeError, match="list boom"):
            gmail_mod.list_inbox_messages()


# Branches: html part present; nested parts; no html → ""; non-dict raw/payload; raise.
class TestGetMessageHtml:
    def test_extracts_nested_html_body(self, monkeypatch) -> None:
        html = "<p>hi</p>"
        fake = _inbox_service(
            list_pages=[],
            full_by_id={
                "m1": {
                    "payload": {
                        "mimeType": "multipart/alternative",
                        "parts": [
                            {"mimeType": "text/plain", "body": {"data": _b64url("plain")}},
                            {
                                "mimeType": "multipart/related",
                                "parts": [
                                    "skip-me",
                                    {
                                        "mimeType": "text/html",
                                        "body": {"data": _b64url(html)},
                                    },
                                ],
                            },
                        ],
                    }
                }
            },
        )
        monkeypatch.setattr(gmail_mod, "build", lambda *a, **k: fake["service"])
        assert gmail_mod.get_message_html("m1") == {
            "id": "m1",
            "html_body": html,
            "subject": "",
            "from_address": "",
        }

    def test_includes_subject_and_from_headers(self, monkeypatch) -> None:
        fake = _inbox_service(
            list_pages=[],
            full_by_id={
                "m1": {
                    "payload": {
                        "mimeType": "text/html",
                        "headers": [
                            {"name": "Subject", "value": "JD role"},
                            {"name": "From", "value": "Ada <ada@ex.com>"},
                        ],
                        "body": {"data": _b64url("<p>body</p>")},
                    }
                }
            },
        )
        monkeypatch.setattr(gmail_mod, "build", lambda *a, **k: fake["service"])
        assert gmail_mod.get_message_html("m1") == {
            "id": "m1",
            "html_body": "<p>body</p>",
            "subject": "JD role",
            "from_address": "Ada <ada@ex.com>",
        }

    def test_top_level_html_and_empty_when_missing(self, monkeypatch) -> None:
        fake = _inbox_service(
            list_pages=[],
            full_by_id={
                "html": {
                    "payload": {
                        "mimeType": "text/html",
                        "body": {"data": _b64url("<b>x</b>")},
                    }
                },
                "plain": {
                    "payload": {
                        "mimeType": "text/plain",
                        "body": {"data": _b64url("only plain")},
                    }
                },
                "empty-data": {
                    "payload": {"mimeType": "text/html", "body": {"data": ""}},
                },
                "bad-body": {
                    "payload": {"mimeType": "text/html", "body": "not-dict"},
                },
                "parts-no-html": {
                    "payload": {
                        "mimeType": "multipart/alternative",
                        "parts": [
                            {"mimeType": "text/plain", "body": {"data": _b64url("plain")}},
                        ],
                    }
                },
                "non-dict-raw": "nope",
                "no-payload": {"payload": None},
            },
        )
        monkeypatch.setattr(gmail_mod, "build", lambda *a, **k: fake["service"])
        assert gmail_mod.get_message_html("html")["html_body"] == "<b>x</b>"
        assert gmail_mod.get_message_html("html")["subject"] == ""
        assert gmail_mod.get_message_html("html")["from_address"] == ""
        assert gmail_mod.get_message_html("plain") == {
            "id": "plain",
            "html_body": "",
            "subject": "",
            "from_address": "",
        }
        assert gmail_mod.get_message_html("empty-data")["html_body"] == ""
        assert gmail_mod.get_message_html("bad-body")["html_body"] == ""
        assert gmail_mod.get_message_html("parts-no-html")["html_body"] == ""
        assert gmail_mod.get_message_html("non-dict-raw") == {
            "id": "non-dict-raw",
            "html_body": "",
            "subject": "",
            "from_address": "",
        }
        assert gmail_mod.get_message_html("no-payload")["html_body"] == ""

    def test_raises_on_get_failure(self, monkeypatch) -> None:
        monkeypatch.setattr(gmail_mod, "build", MagicMock(side_effect=RuntimeError("get boom")))
        with pytest.raises(RuntimeError, match="get boom"):
            gmail_mod.get_message_html("m1")


# Branches: header_map skips; decode padding; message_metadata id/thread types.
class TestGmailHelpers:
    def test_header_map_skips_invalid_rows(self) -> None:
        assert gmail_mod._header_map("nope") == {}
        assert gmail_mod._header_map(
            [
                "skip",
                {"name": 1, "value": "x"},
                {"name": "From", "value": 2},
                {"name": "Subject", "value": "Ok"},
            ]
        ) == {"subject": "Ok"}

    def test_decode_b64url_pads_and_replaces(self) -> None:
        # length % 4 == 2 needs padding; invalid utf-8 bytes → replace
        raw = base64.urlsafe_b64encode(b"hi\xff").decode("ascii").rstrip("=")
        assert "hi" in gmail_mod._decode_b64url(raw)

    def test_message_metadata_non_string_ids(self) -> None:
        row = gmail_mod._message_metadata({"id": 1, "threadId": 2, "labelIds": None, "payload": {}})
        assert row["id"] == ""
        assert row["thread_id"] == ""
        assert row["unread"] is False


# Branches: integration harness blocks live Gmail send/list/get without live opt-in.
class TestControlledExternalIo:
    @pytest.fixture
    def integration_block(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_INTEGRATION_MODE", "1")
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)

    def test_send_email_blocked(self, integration_block, monkeypatch) -> None:
        build = MagicMock()
        monkeypatch.setattr(gmail_mod, "build", build)
        with pytest.raises(RuntimeError, match="gmail.send_email"):
            gmail_mod.send_email("to@example.com", "S", "B")
        build.assert_not_called()

    def test_list_inbox_blocked(self, integration_block, monkeypatch) -> None:
        build = MagicMock()
        monkeypatch.setattr(gmail_mod, "build", build)
        with pytest.raises(RuntimeError, match="gmail.list_inbox_messages"):
            gmail_mod.list_inbox_messages()
        build.assert_not_called()

    def test_get_message_html_blocked(self, integration_block, monkeypatch) -> None:
        build = MagicMock()
        monkeypatch.setattr(gmail_mod, "build", build)
        with pytest.raises(RuntimeError, match="gmail.get_message_html"):
            gmail_mod.get_message_html("m1")
        build.assert_not_called()

    def test_live_opt_in_allows_list(self, monkeypatch, fake_gmail_service) -> None:
        monkeypatch.setenv("ASTRAL_INTEGRATION_MODE", "1")
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        fake = _inbox_service(list_pages=[{"messages": []}])
        monkeypatch.setattr(gmail_mod, "build", lambda *a, **k: fake["service"])
        assert gmail_mod.list_inbox_messages() == []
