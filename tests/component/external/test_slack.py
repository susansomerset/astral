"""Component tests for src/external/slack.py (AST-1069)."""

from __future__ import annotations

import hashlib
import hmac
import time
from unittest.mock import MagicMock

import pytest

from src.external import slack as slack_mod
from src.utils.config import CONTACT_CONFIG


def _sign(secret: str, timestamp: str, body: bytes) -> str:
    base = f"v0:{timestamp}:".encode("utf-8") + body
    return "v0=" + hmac.new(secret.encode("utf-8"), base, hashlib.sha256).hexdigest()


# Branches: good/bad/stale signature; challenge parse; post_message gated + HTTP.
class TestAst1069ExternalSlack:
    def test_verify_signature_ok_and_rejects(self) -> None:
        secret = "s3cret"
        body = b'{"ok":true}'
        ts = str(int(time.time()))
        assert slack_mod.verify_slack_signature(
            signing_secret=secret,
            timestamp=ts,
            body=body,
            signature=_sign(secret, ts, body),
        )
        assert not slack_mod.verify_slack_signature(
            signing_secret=secret,
            timestamp=ts,
            body=body,
            signature="v0=deadbeef",
        )
        # Stale timestamp (>60s).
        old = str(int(time.time()) - 120)
        assert not slack_mod.verify_slack_signature(
            signing_secret=secret,
            timestamp=old,
            body=body,
            signature=_sign(secret, old, body),
        )

    def test_parse_url_verification(self) -> None:
        assert slack_mod.parse_url_verification({"type": "url_verification", "challenge": "abc"}) == "abc"
        assert slack_mod.parse_url_verification({"type": "event_callback"}) is None
        assert slack_mod.parse_url_verification({"type": "url_verification", "challenge": 1}) is None

    def test_post_message_requires_gate_and_posts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.post_message(channel="C1", text="hi")

        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value={"ok": True, "ts": "1.2"})
        post = MagicMock(return_value=resp)
        monkeypatch.setattr(slack_mod.requests, "post", post)
        out = slack_mod.post_message(channel="C1", text="hi", thread_ts="1.0")
        assert out == {"ok": True, "ts": "1.2"}
        assert post.call_args.kwargs["json"]["thread_ts"] == "1.0"
        assert "Bearer xoxb-test" in post.call_args.kwargs["headers"]["Authorization"]


# Branches: users.info profile parse; gate; ok:false (AST-1068).
class TestAst1068FetchUserProfile:
    def test_fetch_profile_ok(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(
            return_value={
                "ok": True,
                "user": {
                    "name": "ada.lovelace",
                    "profile": {
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                        "display_name": "ada",
                    }
                },
            }
        )
        get = MagicMock(return_value=resp)
        monkeypatch.setattr(slack_mod.requests, "get", get)
        out = slack_mod.fetch_user_profile("U1")
        assert out == {
            "slack_user_id": "U1",
            "first": "Ada",
            "last": "Lovelace",
            "display_name": "ada",
            "username": "ada.lovelace",
        }
        assert get.call_args.args[0].endswith("/users.info")
        assert get.call_args.kwargs["params"]["user"] == "U1"

    def test_fetch_requires_gate_and_ok_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.fetch_user_profile("U1")

        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value={"ok": False, "error": "user_not_found"})
        monkeypatch.setattr(slack_mod.requests, "get", MagicMock(return_value=resp))
        with pytest.raises(RuntimeError, match="user_not_found"):
            slack_mod.fetch_user_profile("U1")

    def test_fetch_rejects_empty_user(self) -> None:
        with pytest.raises(ValueError, match="user_id"):
            slack_mod.fetch_user_profile("  ")


# Branches: history vs replies; gate; ok:false raises.
class TestAst1070FetchConversationHistory:
    def test_history_and_replies(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(
            return_value={"ok": True, "messages": [{"ts": "1.0", "text": "hi"}, "skip"]}
        )
        get = MagicMock(return_value=resp)
        monkeypatch.setattr(slack_mod.requests, "get", get)

        out = slack_mod.fetch_conversation_history(channel="C1", limit=10)
        assert out == [{"ts": "1.0", "text": "hi"}]
        assert get.call_args.args[0].endswith("/conversations.history")
        assert get.call_args.kwargs["params"] == {"channel": "C1", "limit": 10}

        out2 = slack_mod.fetch_conversation_history(channel="C1", thread_ts="9.0", limit=5)
        assert get.call_args.args[0].endswith("/conversations.replies")
        assert get.call_args.kwargs["params"]["ts"] == "9.0"
        assert get.call_args.kwargs["params"]["limit"] == 5

    def test_fetch_requires_gate_and_ok_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.fetch_conversation_history(channel="C1", limit=1)

        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(return_value={"ok": False, "error": "channel_not_found"})
        monkeypatch.setattr(slack_mod.requests, "get", MagicMock(return_value=resp))
        with pytest.raises(RuntimeError, match="channel_not_found"):
            slack_mod.fetch_conversation_history(channel="C1", limit=1)

# Branches: empty username when Slack omits user.name (AST-1105).
class TestAst1105FetchUserProfileUsername:
    def test_username_empty_when_omitted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json = MagicMock(
            return_value={"ok": True, "user": {"profile": {"first_name": "A"}}}
        )
        monkeypatch.setattr(slack_mod.requests, "get", MagicMock(return_value=resp))
        out = slack_mod.fetch_user_profile("U2")
        assert out["username"] == ""
        assert out["first"] == "A"


def _slack_get_resp(payload: dict) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value=payload)
    return resp


def _method_from_url(url: str) -> str:
    # https://slack.com/api/<method>
    return str(url).rsplit("/", 1)[-1]


# Branches: gate; message-author pool (not members / not users.list alone);
# replies; soft-skip; bots/deleted filter; hard ok:false raises (AST-1667).
class TestAst1667WorkspacePosterPool:
    def test_requires_gate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.list_workspace_posters()

    def test_poster_pool_excludes_bots_deleted_and_never_posted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        calls: list[str] = []

        def fake_get(url: str, **kwargs):  # type: ignore[no-untyped-def]
            method = _method_from_url(url)
            calls.append(method)
            params = kwargs.get("params") or {}
            if method == "conversations.list":
                return _slack_get_resp(
                    {
                        "ok": True,
                        "channels": [{"id": "C1"}, {"id": "  "}, "skip"],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "conversations.history":
                assert params.get("channel") == "C1"
                return _slack_get_resp(
                    {
                        "ok": True,
                        "messages": [
                            {"user": "U_ZEBRA", "ts": "1.0", "text": "hi"},
                            {"user": "U_BOT", "ts": "1.1", "text": "beep"},
                            # Thread parent — reply_count pulls thread-only poster.
                            {
                                "user": "U_ADA",
                                "ts": "2.0",
                                "reply_count": 1,
                                "text": "parent",
                            },
                            {"bot_id": "B1", "text": "no user field"},
                            "skip",
                        ],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "conversations.replies":
                assert params.get("channel") == "C1"
                assert params.get("ts") == "2.0"
                return _slack_get_resp(
                    {
                        "ok": True,
                        "messages": [
                            {"user": "U_ADA", "ts": "2.0"},
                            {"user": "U_THREAD", "ts": "2.1"},
                        ],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "users.list":
                return _slack_get_resp(
                    {
                        "ok": True,
                        "members": [
                            {"id": "U_ZEBRA", "name": "Zebra", "is_bot": False},
                            {"id": "U_BOT", "name": "roboto", "is_bot": True},
                            {"id": "U_ADA", "name": "ada", "deleted": False},
                            {"id": "U_THREAD", "name": "ThreadOnly"},
                            {"id": "U_GONE", "name": "gone", "deleted": True},
                            # Present in workspace but never posted — must not appear.
                            {"id": "U_LURKER", "name": "lurker"},
                        ],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            raise AssertionError(f"unexpected Slack method {method}")

        monkeypatch.setattr(slack_mod.requests, "get", fake_get)
        out = slack_mod.list_workspace_posters()
        assert out == [
            {"slack_user_id": "U_ADA", "username": "ada"},
            {"slack_user_id": "U_THREAD", "username": "ThreadOnly"},
            {"slack_user_id": "U_ZEBRA", "username": "Zebra"},
        ]
        assert "conversations.members" not in calls
        assert calls.count("conversations.list") == 1
        assert calls.count("conversations.history") == 1
        assert calls.count("conversations.replies") == 1
        assert calls.count("users.list") == 1

    def test_soft_skip_channel_continues(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")

        def fake_get(url: str, **kwargs):  # type: ignore[no-untyped-def]
            method = _method_from_url(url)
            params = kwargs.get("params") or {}
            if method == "conversations.list":
                return _slack_get_resp(
                    {
                        "ok": True,
                        "channels": [{"id": "C_BAD"}, {"id": "C_OK"}],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "conversations.history":
                if params.get("channel") == "C_BAD":
                    return _slack_get_resp({"ok": False, "error": "not_in_channel"})
                return _slack_get_resp(
                    {
                        "ok": True,
                        "messages": [{"user": "U1", "ts": "1.0"}],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "users.list":
                return _slack_get_resp(
                    {
                        "ok": True,
                        "members": [{"id": "U1", "name": "one"}],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            raise AssertionError(f"unexpected Slack method {method}")

        monkeypatch.setattr(slack_mod.requests, "get", fake_get)
        assert slack_mod.list_workspace_posters() == [
            {"slack_user_id": "U1", "username": "one"}
        ]

    def test_hard_failures_raise(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")

        monkeypatch.setattr(
            slack_mod.requests,
            "get",
            MagicMock(return_value=_slack_get_resp({"ok": False, "error": "invalid_auth"})),
        )
        with pytest.raises(RuntimeError, match="conversations.list"):
            slack_mod.list_workspace_posters()

        def history_hard(url: str, **kwargs):  # type: ignore[no-untyped-def]
            method = _method_from_url(url)
            if method == "conversations.list":
                return _slack_get_resp(
                    {
                        "ok": True,
                        "channels": [{"id": "C1"}],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "conversations.history":
                return _slack_get_resp({"ok": False, "error": "invalid_auth"})
            raise AssertionError(method)

        monkeypatch.setattr(slack_mod.requests, "get", history_hard)
        with pytest.raises(RuntimeError, match="conversations.history"):
            slack_mod.list_workspace_posters()

        def users_hard(url: str, **kwargs):  # type: ignore[no-untyped-def]
            method = _method_from_url(url)
            if method == "conversations.list":
                return _slack_get_resp(
                    {
                        "ok": True,
                        "channels": [{"id": "C1"}],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "conversations.history":
                return _slack_get_resp(
                    {
                        "ok": True,
                        "messages": [{"user": "U1", "ts": "1.0"}],
                        "response_metadata": {"next_cursor": ""},
                    }
                )
            if method == "users.list":
                return _slack_get_resp({"ok": False, "error": "fatal_users"})
            raise AssertionError(method)

        monkeypatch.setattr(slack_mod.requests, "get", users_hard)
        with pytest.raises(RuntimeError, match="users.list"):
            slack_mod.list_workspace_posters()

