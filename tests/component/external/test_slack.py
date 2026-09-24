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


# Branches: list_bot_channels pagination/sort/types; is_channel_member early-exit /
# empty inputs / hard fail; fetch_full_conversation_history multi-page ascending
# + no soft-skip (AST-1787).
class TestAst1787ChannelListMembershipFullHistory:
    def test_list_bot_channels_requires_gate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.list_bot_channels()

    def test_list_bot_channels_paginates_sorts_public_private_only(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        pages = [
            {
                "ok": True,
                "channels": [
                    {"id": "C_ZED", "name": "zed"},
                    {"id": "  ", "name": "bad"},
                    "skip",
                    {"id": "C_ALPHA", "name": "Alpha"},
                ],
                "response_metadata": {"next_cursor": "page2"},
            },
            {
                "ok": True,
                "channels": [
                    {"id": "C_EMPTY", "name": None},
                    {"id": "C_BETA", "name": "beta"},
                ],
                "response_metadata": {"next_cursor": ""},
            },
        ]
        seen_types: list[str] = []

        def fake_get(url: str, **kwargs):  # type: ignore[no-untyped-def]
            method = _method_from_url(url)
            assert method == "conversations.list"
            params = kwargs.get("params") or {}
            seen_types.append(str(params.get("types") or ""))
            assert params.get("exclude_archived") is True
            if not pages:
                raise AssertionError("extra conversations.list call")
            return _slack_get_resp(pages.pop(0))

        monkeypatch.setattr(slack_mod.requests, "get", fake_get)
        out = slack_mod.list_bot_channels()
        # Empty name sorts before letter names (name.lower(), id).
        assert out == [
            {"id": "C_EMPTY", "name": ""},
            {"id": "C_ALPHA", "name": "Alpha"},
            {"id": "C_BETA", "name": "beta"},
            {"id": "C_ZED", "name": "zed"},
        ]
        assert all(t == "public_channel,private_channel" for t in seen_types)
        assert len(seen_types) == 2

    def test_list_bot_channels_ok_false_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        monkeypatch.setattr(
            slack_mod.requests,
            "get",
            MagicMock(return_value=_slack_get_resp({"ok": False, "error": "invalid_auth"})),
        )
        with pytest.raises(RuntimeError, match="conversations.list"):
            slack_mod.list_bot_channels()

    def test_is_channel_member_requires_gate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.is_channel_member(channel="C1", slack_user_id="U1")

    def test_is_channel_member_empty_inputs_raise(self) -> None:
        with pytest.raises(ValueError, match="channel is required"):
            slack_mod.is_channel_member(channel="  ", slack_user_id="U1")
        with pytest.raises(ValueError, match="slack_user_id is required"):
            slack_mod.is_channel_member(channel="C1", slack_user_id="  ")

    def test_is_channel_member_true_early_exit_across_pages(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        pages = [
            {
                "ok": True,
                "members": ["U_A", "U_B"],
                "response_metadata": {"next_cursor": "more"},
            },
            {
                "ok": True,
                "members": ["U_TARGET", "U_C"],
                "response_metadata": {"next_cursor": "never"},
            },
        ]
        calls = 0

        def fake_get(url: str, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal calls
            method = _method_from_url(url)
            assert method == "conversations.members"
            calls += 1
            params = kwargs.get("params") or {}
            assert params.get("channel") == "C9"
            return _slack_get_resp(pages.pop(0))

        monkeypatch.setattr(slack_mod.requests, "get", fake_get)
        assert slack_mod.is_channel_member(channel=" C9 ", slack_user_id=" U_TARGET ") is True
        assert calls == 2  # early exit — third page cursor never fetched

    def test_is_channel_member_false_after_exhaust(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")

        def fake_get(url: str, **kwargs):  # type: ignore[no-untyped-def]
            assert _method_from_url(url) == "conversations.members"
            return _slack_get_resp(
                {
                    "ok": True,
                    "members": ["U_OTHER"],
                    "response_metadata": {"next_cursor": ""},
                }
            )

        monkeypatch.setattr(slack_mod.requests, "get", fake_get)
        assert slack_mod.is_channel_member(channel="C1", slack_user_id="U_MISS") is False

    def test_is_channel_member_ok_false_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        monkeypatch.setattr(
            slack_mod.requests,
            "get",
            MagicMock(return_value=_slack_get_resp({"ok": False, "error": "channel_not_found"})),
        )
        with pytest.raises(RuntimeError, match="conversations.members"):
            slack_mod.is_channel_member(channel="C1", slack_user_id="U1")

    def test_fetch_full_requires_gate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", raising=False)
        with pytest.raises(Exception):
            slack_mod.fetch_full_conversation_history(channel="C1")

    def test_fetch_full_empty_channel_raises(self) -> None:
        with pytest.raises(ValueError, match="channel is required"):
            slack_mod.fetch_full_conversation_history(channel="  ")

    def test_fetch_full_paginates_and_sorts_ascending(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        # Slack pages newest-first; helper must return oldest→newest across pages.
        pages = [
            {
                "ok": True,
                "messages": [
                    {"ts": "3.0", "text": "newest-page1"},
                    {"ts": "2.0", "text": "mid"},
                    {"text": "no-ts-first"},
                ],
                "response_metadata": {"next_cursor": "p2"},
            },
            {
                "ok": True,
                "messages": [
                    {"ts": "1.0", "text": "oldest"},
                    {"text": "no-ts-second"},
                ],
                "response_metadata": {"next_cursor": ""},
            },
        ]

        def fake_get(url: str, **kwargs):  # type: ignore[no-untyped-def]
            assert _method_from_url(url) == "conversations.history"
            params = kwargs.get("params") or {}
            assert params.get("channel") == "C_SNAP"
            return _slack_get_resp(pages.pop(0))

        monkeypatch.setattr(slack_mod.requests, "get", fake_get)
        out = slack_mod.fetch_full_conversation_history(channel=" C_SNAP ")
        assert [m.get("ts") for m in out] == ["1.0", "2.0", "3.0", None, None]
        assert out[0]["text"] == "oldest"
        assert out[3]["text"] == "no-ts-first"
        assert out[4]["text"] == "no-ts-second"
    def test_fetch_full_ok_false_raises_no_soft_skip(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_ALLOW_LIVE_EXTERNAL_IO", "1")
        monkeypatch.setenv(CONTACT_CONFIG["bot_token_env"], "xoxb-test")
        monkeypatch.setattr(
            slack_mod.requests,
            "get",
            MagicMock(
                return_value=_slack_get_resp({"ok": False, "error": "not_in_channel"})
            ),
        )
        with pytest.raises(RuntimeError, match="conversations.history"):
            slack_mod.fetch_full_conversation_history(channel="C1")

