"""Component tests for src/core/contact.py (AST-1066 scaffold + AST-1069 ingress + AST-1071 skill runners)."""

from __future__ import annotations

import hashlib
from pathlib import Path
import hmac
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core import contact as contact_mod
from src.core import candidate as candidate_mod
from src.utils.config import CONTACT_CONFIG, CONTACT_TASK_CONFIG, TASK_CONFIG


def _sign(secret: str, timestamp: str, body: bytes) -> str:
    base = f"v0:{timestamp}:".encode("utf-8") + body
    return "v0=" + hmac.new(secret.encode("utf-8"), base, hashlib.sha256).hexdigest()



def _stub_estelle_turn(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """AST-1073: accept-path tests must not invoke real do_task via turn loop."""
    stub = MagicMock(
        return_value={
            "ok": True,
            "outcome": "success",
            "reply": "stub-reply",
            "admin_aside": None,
            "skill_results": [],
            "slack_post": {"ok": True},
            "error": None,
        }
    )
    monkeypatch.setattr(contact_mod, "run_contact_estelle_turn", stub)
    return stub



@pytest.fixture(autouse=True)
def _ast2061_private_channel_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # AST-2061: app_mention looks up channel type; default every case to a private channel.
    # raising=False keeps the pre-fix module importable for [bug-repro] runs.
    monkeypatch.setattr(contact_mod, "fetch_channel_type", lambda _ch: "group", raising=False)


class _ImmediateThread:
    """Run Thread target synchronously so receive_slack_events_http tests stay deterministic."""

    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}

    def start(self) -> None:
        if self._target:
            self._target(*self._args, **self._kwargs)


# Branches: listen default; empty skills shallow copy; env-name map; prefix; no TASK_CONFIG collision.
class TestAst1066ContactScaffold:
    def test_slack_listen_enabled_default_off(self) -> None:
        assert contact_mod.slack_listen_enabled() is False
        assert CONTACT_CONFIG["listen_enabled"] is False

    def test_contact_skills_shallow_copy(self) -> None:
        # AST-1071 populates skills; AST-1066 still requires a non-mutating shallow copy.
        skills = contact_mod.contact_skills()
        assert isinstance(skills, dict)
        assert set(skills.keys()) == set(CONTACT_CONFIG["skills"].keys())
        keys = contact_mod.contact_skill_keys()
        assert keys == tuple(CONTACT_CONFIG["skills"].keys())
        skills["should_not_leak"] = {}
        assert "should_not_leak" not in CONTACT_CONFIG["skills"]
        assert contact_mod.contact_skill_keys() == keys

    def test_slack_env_names_are_names_only(self) -> None:
        names = contact_mod.slack_env_names()
        assert names == {
            "bot_token": "SLACK_BOT_TOKEN",
            "signing_secret": "SLACK_SIGNING_SECRET",
        }
        assert "xoxb-" not in str(names.values())
        assert names["bot_token"] == CONTACT_CONFIG["bot_token_env"]
        assert names["signing_secret"] == CONTACT_CONFIG["signing_secret_env"]

    def test_skill_keys_do_not_collide_with_task_config(self) -> None:
        for skill_key in contact_mod.contact_skill_keys():
            assert skill_key not in TASK_CONFIG


# Branches: registry empty (AST-2061 retired save_candidate_*); any key → unknown, no candidate write.
class TestAst2061ContactSkillsRetired:
    def test_skills_registry_empty(self) -> None:
        assert contact_mod.contact_skills() == {}
        assert contact_mod.contact_skill_keys() == ()

    def test_run_contact_skill_refuses_any_key(self, sqlite_in_memory) -> None:
        cid = "c-2061-skill"
        from src.utils.config import CANDIDATE_STATES

        state = "NEW_CANDIDATE" if "NEW_CANDIDATE" in CANDIDATE_STATES else "NEW"
        sqlite_in_memory.save_candidate(cid, state=state, candidate_data={})
        with pytest.raises(ValueError, match="unknown contact skill"):
            contact_mod.run_contact_skill(
                "save_profile_field",
                astral_candidate_id=cid,
                fields={"contact.contact_email": "x@evil.test"},
            )
        row = candidate_mod.get_candidate(cid)
        assert "contact" not in (row.get("candidate_data") or {})


class TestAst1069ContactSlackIngress:
    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def _stub_resolve(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1068 wires resolve on accept — stub so ingress tests stay transport-focused.
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c-stub",
                    "state": "PROSPECT",
                    "created": False,
                }
            ),
        )

    def test_handle_listen_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        out = contact_mod.handle_slack_event(
            {"event_id": "Ev1", "event": {"type": "app_mention", "user": "U1", "channel": "C1", "text": "hi"}},
        )
        assert out == {"accepted": False, "reason": "listen_off"}

    def test_handle_app_mention_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        self._stub_resolve(monkeypatch)
        _stub_estelle_turn(monkeypatch)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-mention",
                "event": {
                    "type": "app_mention",
                    "user": "U1",
                    "channel": "C1",
                    "ts": "1.0",
                    "text": "<@BOT> hello",
                },
            },
        )
        assert out["accepted"] is True
        assert out["event_type"] == "app_mention"
        assert out["user"] == "U1"
        # Duplicate event_id rejected.
        dup = contact_mod.handle_slack_event(
            {"event_id": "Ev-mention", "event": {"type": "app_mention", "user": "U1", "channel": "C1", "text": "x"}},
        )
        assert dup == {"accepted": False, "reason": "duplicate_event"}

    def test_handle_dm_message_accepted_channel_skipped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        self._stub_resolve(monkeypatch)
        _stub_estelle_turn(monkeypatch)
        dm = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-dm",
                "event": {
                    "type": "message",
                    "channel_type": "im",
                    "channel": "D123",
                    "user": "U2",
                    "ts": "2.0",
                    "text": "dm hi",
                },
            },
        )
        assert dm["accepted"] is True
        assert dm["event_type"] == "message"
        ch = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-ch",
                "event": {
                    "type": "message",
                    "channel_type": "channel",
                    "channel": "C999",
                    "user": "U2",
                    "text": "not a dm",
                },
            },
        )
        assert ch == {"accepted": False, "reason": "not_dm"}

    def test_handle_message_bot_subtype_skipped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-bot",
                "event": {
                    "type": "message",
                    "channel_type": "im",
                    "channel": "D1",
                    "bot_id": "B1",
                    "text": "echo",
                },
            },
        )
        assert out == {"accepted": False, "reason": "message_skipped"}

    def test_receive_bad_signature_401(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(CONTACT_CONFIG["signing_secret_env"], "sec")
        status, body = contact_mod.receive_slack_events_http(
            b'{"type":"event_callback"}',
            timestamp=str(int(time.time())),
            signature="v0=bad",
        )
        assert status == 401
        assert body == ""

    def test_receive_url_verification_challenge(self, monkeypatch: pytest.MonkeyPatch) -> None:
        secret = "signing-secret"
        monkeypatch.setenv(CONTACT_CONFIG["signing_secret_env"], secret)
        body = json.dumps({"type": "url_verification", "challenge": "ch-123"}).encode()
        ts = str(int(time.time()))
        status, out = contact_mod.receive_slack_events_http(
            body,
            timestamp=ts,
            signature=_sign(secret, ts, body),
        )
        assert status == 200
        assert out == {"challenge": "ch-123"}

    def test_receive_event_acks_and_schedules_handler(self, monkeypatch: pytest.MonkeyPatch) -> None:
        secret = "signing-secret"
        monkeypatch.setenv(CONTACT_CONFIG["signing_secret_env"], secret)
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        self._stub_resolve(monkeypatch)
        _stub_estelle_turn(monkeypatch)
        monkeypatch.setattr(contact_mod.threading, "Thread", _ImmediateThread)
        payload = {
            "type": "event_callback",
            "event_id": "Ev-http",
            "event": {
                "type": "app_mention",
                "user": "U9",
                "channel": "C9",
                "text": "hi",
                "ts": "9.0",
            },
        }
        body = json.dumps(payload).encode()
        ts = str(int(time.time()))
        status, out = contact_mod.receive_slack_events_http(
            body,
            timestamp=ts,
            signature=_sign(secret, ts, body),
        )
        assert status == 200
        assert out == ""
        # Handler ran via ImmediateThread — event remembered.
        assert "Ev-http" in contact_mod._seen_event_ids


# Branches: resolve hit/miss lookup-only (AST-1068; create-on-miss retired AST-1668).
class TestAst1068ResolveSlackUser:
    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def test_resolve_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value="c1"))
        monkeypatch.setattr(
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "state": "INTAKE_INITIATED",
                    "candidate_data": {"contact": {"slack_user_id": "U1", "slack_username": "ada"}},
                }
            ),
        )
        # AST-1105 found path always calls users.info for display / backfill check.
        monkeypatch.setattr(
            contact_mod,
            "fetch_user_profile",
            MagicMock(
                return_value={
                    "slack_user_id": "U1",
                    "username": "ada",
                    "display_name": "Ada",
                    "first": "Ada",
                    "last": "L",
                }
            ),
        )
        save = MagicMock()
        monkeypatch.setattr(contact_mod, "save_candidate_data", save)
        out = contact_mod.resolve_slack_user("U1", estelle_in_play=True)
        assert out == {
            "astral_candidate_id": "c1",
            "state": "INTAKE_INITIATED",
            "created": False,
            "slack_username": "ada",
            "slack_display_name": "Ada",
        }
        save.assert_not_called()
        # AST-1668: create-on-miss retired — symbol must not live on contact module.
        assert not hasattr(contact_mod, "initiate_prospect_candidate")

    def test_resolve_miss_without_estelle_does_not_create(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value=None))
        fetch = MagicMock()
        monkeypatch.setattr(contact_mod, "fetch_user_profile", fetch)
        out = contact_mod.resolve_slack_user("Umiss", estelle_in_play=False)
        assert out == {
            "astral_candidate_id": None,
            "state": None,
            "created": False,
            "slack_username": "",
            "slack_display_name": "",
        }
        fetch.assert_not_called()

    def test_resolve_miss_estelle_lookup_only_no_prospect(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1668: miss + estelle_in_play fetches profile but never mints PROSPECT.
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value=None))
        monkeypatch.setattr(
            contact_mod,
            "fetch_user_profile",
            MagicMock(
                return_value={
                    "slack_user_id": "Unew",
                    "first": "Ada",
                    "last": "L",
                    "display_name": "ada",
                    "username": "ada.lovelace",
                }
            ),
        )
        out = contact_mod.resolve_slack_user("Unew", estelle_in_play=True)
        assert out == {
            "astral_candidate_id": None,
            "state": None,
            "created": False,
            "slack_username": "ada.lovelace",
            "slack_display_name": "ada",
        }
        assert not hasattr(contact_mod, "initiate_prospect_candidate")

    def test_resolve_miss_estelle_returns_display_when_names_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value=None))
        monkeypatch.setattr(
            contact_mod,
            "fetch_user_profile",
            MagicMock(
                return_value={
                    "slack_user_id": "Ux",
                    "first": "",
                    "last": "",
                    "display_name": "OnlyDisplay",
                    "username": "onlydisplay",
                }
            ),
        )
        out = contact_mod.resolve_slack_user("Ux", estelle_in_play=True)
        assert out["created"] is False
        assert out["astral_candidate_id"] is None
        assert out["slack_username"] == "onlydisplay"
        assert out["slack_display_name"] == "OnlyDisplay"

    def test_resolve_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="slack_user_id"):
            contact_mod.resolve_slack_user("  ", estelle_in_play=True)

    def test_handle_accept_wires_resolve(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        resolved = {
            "astral_candidate_id": "c-known",
            "state": "INTAKE_INITIATED",
            "created": False,
        }
        monkeypatch.setattr(contact_mod, "resolve_slack_user", MagicMock(return_value=resolved))
        monkeypatch.setattr(
            contact_mod,
            "contact_post_message",
            MagicMock(return_value={"ok": True, "ts": "1.1"}),
        )
        _stub_estelle_turn(monkeypatch)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-resolve",
                "event": {
                    "type": "app_mention",
                    "user": "U9",
                    "channel": "C1",
                    "text": "hi",
                    "ts": "1.0",
                },
            }
        )
        assert out["accepted"] is True
        assert out["astral_candidate_id"] == "c-known"
        assert out["candidate_state"] == "INTAKE_INITIATED"
        assert out["candidate_created"] is False
        contact_mod.resolve_slack_user.assert_called_once_with(
            "U9", estelle_in_play=True, debug=False
        )


# Branches: envelope hit/miss/TTL/refresh; empty channel; append; DM key; post append (AST-1070).
class TestAst1070ContactConversationContext:
    def setup_method(self) -> None:
        contact_mod._context_cache.clear()
        contact_mod._seen_event_ids.clear()

    def test_load_rejects_empty_channel(self) -> None:
        with pytest.raises(ValueError, match="channel"):
            contact_mod.load_slack_conversation_context(channel="  ")

    def test_load_fetches_then_cache_hit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fetch = MagicMock(return_value=[{"ts": "1.0", "text": "a", "user": "U1"}])
        monkeypatch.setattr(contact_mod, "fetch_conversation_history", fetch)
        first = contact_mod.load_slack_conversation_context(channel="C1", thread_ts=None)
        assert first == {
            "channel": "C1",
            "thread_ts": "",
            "messages": [{"ts": "1.0", "text": "a", "user": "U1"}],
            "source": "slack",
        }
        fetch.assert_called_once_with(
            channel="C1",
            thread_ts=None,
            limit=CONTACT_CONFIG["context_history_limit"],
        )
        second = contact_mod.load_slack_conversation_context(channel="C1")
        assert second["source"] == "cache"
        assert second["messages"] == first["messages"]
        assert second["channel"] == "C1"
        assert second["thread_ts"] == ""
        fetch.assert_called_once()

    def test_load_refresh_bypasses_cache(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fetch = MagicMock(
            side_effect=[
                [{"ts": "1.0", "text": "old"}],
                [{"ts": "2.0", "text": "new"}],
            ]
        )
        monkeypatch.setattr(contact_mod, "fetch_conversation_history", fetch)
        contact_mod.load_slack_conversation_context(channel="C1")
        out = contact_mod.load_slack_conversation_context(channel="C1", refresh=True)
        assert out == {
            "channel": "C1",
            "thread_ts": "",
            "messages": [{"ts": "2.0", "text": "new"}],
            "source": "slack",
        }
        assert fetch.call_count == 2

    def test_load_ttl_expiry_refetches(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fetch = MagicMock(
            side_effect=[
                [{"ts": "1.0", "text": "a"}],
                [{"ts": "2.0", "text": "b"}],
            ]
        )
        monkeypatch.setattr(contact_mod, "fetch_conversation_history", fetch)
        times = iter(
            [1000.0, 1000.0 + float(CONTACT_CONFIG["context_cache_ttl_seconds"]) + 1.0]
        )
        monkeypatch.setattr(contact_mod.time, "time", lambda: next(times))
        contact_mod.load_slack_conversation_context(channel="C1")
        out = contact_mod.load_slack_conversation_context(channel="C1")
        assert out["source"] == "slack"
        assert out["messages"] == [{"ts": "2.0", "text": "b"}]
        assert fetch.call_count == 2

    def test_load_strips_channel(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fetch = MagicMock(return_value=[])
        monkeypatch.setattr(contact_mod, "fetch_conversation_history", fetch)
        out = contact_mod.load_slack_conversation_context(channel="  C1  ", thread_ts="9.0")
        assert out["channel"] == "C1"
        assert out["thread_ts"] == "9.0"
        assert out["source"] == "slack"
        fetch.assert_called_once_with(
            channel="C1",
            thread_ts="9.0",
            limit=CONTACT_CONFIG["context_history_limit"],
        )

    def test_append_warms_and_trims(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "context_history_limit", 2)
        contact_mod.append_slack_conversation_message(
            channel="D1", thread_ts=None, message={"text": "1", "ts": "1.0"},
        )
        contact_mod.append_slack_conversation_message(
            channel="D1", message={"text": "2", "ts": "2.0"},
        )
        contact_mod.append_slack_conversation_message(
            channel="D1", message={"text": "3", "ts": "3.0"},
        )
        key = contact_mod._context_cache_key("D1", None)
        msgs = contact_mod._context_cache[key]["messages"]
        assert [m["ts"] for m in msgs] == ["2.0", "3.0"]

    def test_append_rejects_bad_message(self) -> None:
        with pytest.raises(ValueError, match="text and ts"):
            contact_mod.append_slack_conversation_message(
                channel="C1", message={"text": "x"}
            )

    def test_dm_cache_key_ignores_message_ts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        # Tip may wire resolve on accept — stub so DM path stays on cache assert.
        if hasattr(contact_mod, "resolve_slack_user"):
            monkeypatch.setattr(
                contact_mod,
                "resolve_slack_user",
                MagicMock(
                    return_value={
                        "astral_candidate_id": None,
                        "state": None,
                        "created": False,
                    }
                ),
            )
        _stub_estelle_turn(monkeypatch)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-dm-cache",
                "event": {
                    "type": "message",
                    "channel_type": "im",
                    "channel": "Ddm",
                    "user": "U1",
                    "ts": "99.9",
                    "text": "hello dm",
                },
            },
        )
        assert out["accepted"] is True
        assert ("Ddm", "") in contact_mod._context_cache
        assert ("Ddm", "99.9") not in contact_mod._context_cache

    def test_contact_post_message_appends_outbound(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            contact_mod,
            "post_message",
            MagicMock(return_value={"ok": True, "ts": "5.5"}),
        )
        resp = contact_mod.contact_post_message(channel="C1", text="bye", thread_ts="1.0")
        assert resp["ok"] is True
        key = contact_mod._context_cache_key("C1", "1.0")
        msgs = contact_mod._context_cache[key]["messages"]
        assert msgs[-1]["ts"] == "5.5"
        assert msgs[-1]["text"] == "bye"
        assert msgs[-1]["bot_id"] == "estelle"




def _turn_candidate_row(cid: str) -> dict:
    """AST-1879: Estelle turn needs a resolved candidate row (key map rides into do_task ctx)."""
    return {"astral_candidate_id": cid, "candidate_data": {}, "candidate_api_keys": {"kimi": "sk-kimi"}}


class TestAst1073ContactEstelleTurnLoop:
    """AST-1073: run_contact_estelle_turn — listen, do_task envelope, skills, Slack post, Style D."""

    def setup_method(self) -> None:
        contact_mod._context_cache.clear()
        contact_mod._seen_event_ids.clear()

    def _patch_turn_deps(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        do_task_result: dict,
        listen: bool = True,
    ) -> dict:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", listen)
        monkeypatch.setattr(
            contact_mod,
            "load_slack_conversation_context",
            MagicMock(
                return_value={
                    "channel": "C1",
                    "thread_ts": "",
                    "messages": [{"user": "U1", "text": "prior", "ts": "1.0"}],
                    "source": "cache",
                }
            ),
        )
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(side_effect=_turn_candidate_row))
        monkeypatch.setattr(contact_mod, "contact_skills", MagicMock(return_value={}))
        post = MagicMock(return_value={"ok": True, "ts": "9.0"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        monkeypatch.setattr(
            contact_mod,
            "format_contact_reply_text",
            lambda text: f"[prefix] {text}",
        )
        skill = MagicMock(return_value={"ok": True, "skill_key": "save_profile_field"})
        monkeypatch.setattr(contact_mod, "run_contact_skill", skill)
        do_task_calls: list = []

        async def _do_task(*a, **k):
            do_task_calls.append((a, k))
            return do_task_result

        import src.core.agent as agent_mod

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        return {"post": post, "skill": skill, "do_task_calls": do_task_calls}

    def test_listen_off_skips_do_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        deps = self._patch_turn_deps(
            monkeypatch,
            do_task_result={"success": True},
            listen=False,
        )
        out = contact_mod.run_contact_estelle_turn(channel="C1", text="hi", debug=False)
        assert out["ok"] is False
        assert out["error"] == "listen_off"
        deps["post"].assert_not_called()

    def test_success_posts_prefixed_reply(self, monkeypatch: pytest.MonkeyPatch) -> None:
        deps = self._patch_turn_deps(
            monkeypatch,
            do_task_result={
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "Hello there"},
            },
        )
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", message_ts="2.0", astral_candidate_id="c1", debug=False
        )
        assert out["ok"] is True
        assert out["outcome"] == "success"
        assert out["reply"] == "Hello there"
        deps["post"].assert_called_once()
        assert deps["post"].call_args.kwargs["text"] == "[prefix] Hello there"
        # AST-2072: default threads_only — a top-level inbound gets a top-level reply.
        assert deps["post"].call_args.kwargs["thread_ts"] is None
        assert deps["post"].call_args.kwargs["reply_broadcast"] is False

    def test_concern_posts_and_logs_aside(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        deps = self._patch_turn_deps(
            monkeypatch,
            do_task_result={
                "success": True,
                "conversational_outcome": "concern",
                "agent_performance": {
                    "status": "concern",
                    "admin_aside": "user frustrated",
                },
                "parsed_response": {"reply": "Sorry this is hard"},
            },
        )
        with caplog.at_level(logging.WARNING):
            out = contact_mod.run_contact_estelle_turn(
                channel="C1", text="ugh", astral_candidate_id="c1", debug=False
            )
        assert out["ok"] is True
        assert out["outcome"] == "concern"
        assert out["admin_aside"] == "user frustrated"
        deps["post"].assert_called_once()
        assert "user frustrated" in caplog.text
        assert "admin_aside" not in (deps["post"].call_args.kwargs["text"] or "")

    def test_failure_does_not_post(self, monkeypatch: pytest.MonkeyPatch) -> None:
        deps = self._patch_turn_deps(
            monkeypatch,
            do_task_result={
                "success": False,
                "error": "Agent failure: blocked",
                "conversational_outcome": "failure",
                "agent_performance": {"status": "failure", "failure_note": "blocked"},
                "parsed_response": None,
            },
        )
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", astral_candidate_id="c1", debug=False
        )
        assert out["ok"] is False
        assert out["error"] != "no_candidate"
        assert len(deps["do_task_calls"]) == 1
        deps["post"].assert_not_called()

    def test_ast2061_skill_calls_never_write_candidate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # [bug-repro] AST-2061: Estelle output carrying skill_calls must not reach run_contact_skill
        # or save_candidate_data, and the turn prompt no longer advertises a skills ACL.
        deps = self._patch_turn_deps(
            monkeypatch,
            do_task_result={
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {
                    "reply": "ok",
                    "skill_calls": [
                        {"skill_key": "save_profile_field", "fields": {"contact.contact_email": "x@evil.test"}},
                    ],
                },
            },
        )
        save = MagicMock()
        monkeypatch.setattr(contact_mod, "save_candidate_data", save)
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", astral_candidate_id="c1", debug=False
        )
        deps["skill"].assert_not_called()
        save.assert_not_called()
        assert out["skill_results"] == []
        assert "## Available Contact skills (ACL)" not in deps["do_task_calls"][0][1]["live_content"]

    def test_debug_style_d_index_and_detail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_turn_deps(
            monkeypatch,
            do_task_result={
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "ok"},
            },
        )
        log = MagicMock()
        monkeypatch.setattr(contact_mod, "get_logger", lambda _n: log)
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", astral_candidate_id="c1", debug=True
        )
        assert out["ok"] is True
        log.set_debug_flag.assert_called_with(True)
        log.debug_index.assert_called()
        # AST-1207: turn bookend is found→recorded (was single outcome="success").
        outcomes = [c.kwargs.get("outcome") for c in log.debug_index.call_args_list]
        assert outcomes == ["found", "recorded"]
        kwa = log.debug_index.call_args.kwargs
        assert kwa.get("func") == "contact.run_contact_estelle_turn"
        assert kwa.get("outcome") == "recorded"
        details = [c.args[0] for c in log.debug_detail.call_args_list if c.args]
        assert any("reply_len=" in str(m) for m in details)

    def test_handle_slack_event_attaches_estelle_turn(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "state": "PROSPECT",
                    "created": False,
                }
            ),
        )
        turn = _stub_estelle_turn(monkeypatch)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-estelle",
                "event": {
                    "type": "app_mention",
                    "user": "U1",
                    "channel": "C1",
                    "ts": "1.0",
                    "text": "hi",
                },
            },
            debug=False,
        )
        assert out["accepted"] is True
        assert out["estelle_turn"]["ok"] is True
        turn.assert_called_once()
        assert turn.call_args.kwargs["channel"] == "C1"
        assert turn.call_args.kwargs["astral_candidate_id"] == "c1"


# Branches: no/blank/unresolved candidate → no_candidate before do_task; resolved → ctx key map (AST-1879).
class TestAst1879EstelleTurnCandidateCtx:
    """AST-1879 AC 10: every Estelle turn runs on the candidate's key — no candidate, no request."""

    def setup_method(self) -> None:
        contact_mod._context_cache.clear()
        contact_mod._seen_event_ids.clear()

    _OK = {
        "success": True,
        "conversational_outcome": "success",
        "agent_performance": {"status": "success"},
        "parsed_response": {"reply": "Hi"},
    }

    def _patch(self, monkeypatch: pytest.MonkeyPatch, get_candidate: MagicMock) -> dict:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        ctx_load = MagicMock(return_value={"channel": "C1", "thread_ts": "", "messages": [], "source": "cache"})
        monkeypatch.setattr(contact_mod, "load_slack_conversation_context", ctx_load)
        monkeypatch.setattr(contact_mod, "get_candidate", get_candidate)
        monkeypatch.setattr(contact_mod, "contact_skills", MagicMock(return_value={}))
        post = MagicMock(return_value={"ok": True, "ts": "9.0"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        monkeypatch.setattr(contact_mod, "format_contact_reply_text", lambda text: text)
        calls: list = []

        async def _do_task(*a, **k):
            calls.append((a, k))
            return dict(self._OK)

        import src.core.agent as agent_mod

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        return {"post": post, "calls": calls, "ctx_load": ctx_load}

    @pytest.mark.parametrize("cid", [None, "", "   "])
    def test_no_candidate_id_fails_before_do_task(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, cid: object
    ) -> None:
        get_candidate = MagicMock(return_value=_turn_candidate_row("c1"))
        deps = self._patch(monkeypatch, get_candidate)
        with caplog.at_level("WARNING", logger="src.core.contact"):
            out = contact_mod.run_contact_estelle_turn(
                channel="C1", text="hi", astral_candidate_id=cid, debug=False
            )
        assert out["ok"] is False
        assert out["error"] == "no_candidate"
        assert deps["calls"] == []
        deps["post"].assert_not_called()
        get_candidate.assert_not_called()
        # Early return: no Slack context load either.
        deps["ctx_load"].assert_not_called()
        assert any(
            "C1 | contact estelle turn skipped — no candidate for this Slack user" in r.getMessage()
            and "Estelle is not replying" in r.getMessage()
            for r in caplog.records
        )

    def test_unresolved_candidate_id_fails_before_do_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get_candidate = MagicMock(return_value=None)
        deps = self._patch(monkeypatch, get_candidate)
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", astral_candidate_id="ghost", debug=False
        )
        assert out["error"] == "no_candidate"
        get_candidate.assert_called_once_with("ghost")
        assert deps["calls"] == []
        deps["post"].assert_not_called()

    def test_resolved_candidate_passes_ctx_with_key_map(self, monkeypatch: pytest.MonkeyPatch) -> None:
        row = {
            "astral_candidate_id": "c1",
            "candidate_data": {"profile": {"first": "Ada"}},
            "candidate_api_keys": {"kimi": "sk-kimi", "anthropic": "sk-ant"},
        }
        deps = self._patch(monkeypatch, MagicMock(return_value=row))
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", astral_candidate_id=" c1 ", debug=False
        )
        assert out["ok"] is True
        (args, kwargs), = deps["calls"]
        assert args[0] == "contact_estelle_turn"
        assert "candidate_data" not in kwargs
        ctx = kwargs["ctx"]
        assert ctx == {
            "astral_candidate_id": "c1",
            "candidate_data": {"profile": {"first": "Ada"}},
            "candidate_api_keys": {"kimi": "sk-kimi", "anthropic": "sk-ant"},
        }
        # Copied map, not the row's own dict.
        assert ctx["candidate_api_keys"] is not row["candidate_api_keys"]

    def test_resolved_candidate_without_keys_sends_empty_map(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Missing key is do_task's call (server-naming failure) — the turn still hands over an empty map.
        deps = self._patch(monkeypatch, MagicMock(return_value={"astral_candidate_id": "c1", "candidate_data": {}}))
        contact_mod.run_contact_estelle_turn(channel="C1", text="hi", astral_candidate_id="c1", debug=False)
        (_a, kwargs), = deps["calls"]
        assert kwargs["ctx"]["candidate_api_keys"] == {}


# Branches: list_estelle_activity; record on accept; listen_off skips (AST-1094).
class TestAst1094EstelleActivity:
    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def test_list_estelle_activity_delegates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [{"slack_user_id": "U1", "bind_ok": True, "inbound_message_count": 1}]
        monkeypatch.setattr(
            "src.data.contact_estelle_activity.list_estelle_activity_rows",
            lambda: rows,
        )
        assert contact_mod.list_estelle_activity() == rows

    def test_handle_records_activity_on_accept(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "state": "PROSPECT",
                    "created": False,
                }
            ),
        )
        _stub_estelle_turn(monkeypatch)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-act-1",
                "event": {
                    "type": "app_mention",
                    "user": "U-act",
                    "channel": "C-act",
                    "ts": "9.9",
                    "text": "<@BOT> hi",
                },
            },
        )
        assert out["accepted"] is True
        rows = contact_mod.list_estelle_activity()
        assert len(rows) == 1
        assert rows[0]["slack_user_id"] == "U-act"
        assert rows[0]["bind_ok"] is True
        assert rows[0]["astral_candidate_id"] == "c1"
        assert rows[0]["inbound_message_count"] == 1
        assert rows[0]["last_channel"] == "C-act"
        assert rows[0]["last_message_ts"] == "9.9"

    def test_listen_off_does_not_record(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-off",
                "event": {
                    "type": "app_mention",
                    "user": "U-off",
                    "channel": "C1",
                    "ts": "1.0",
                    "text": "x",
                },
            },
        )
        assert out == {"accepted": False, "reason": "listen_off"}
        assert contact_mod.list_estelle_activity() == []

# Branches: listen re-read; hear-ack fallback; background log wrap (AST-1101).
class TestAst1101ChannelHearEvidence:
    """AST-1101: durable listen SoT; hear-ack when Estelle turn does not post."""

    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def _stub_resolve(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "state": "PROSPECT",
                    "created": False,
                }
            ),
        )

    def test_slack_listen_rereads_durable_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.data.contact_listen import save_contact_listen_enabled
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        save_contact_listen_enabled(True)
        assert contact_mod.slack_listen_enabled() is True
        assert CONTACT_CONFIG["listen_enabled"] is True
        save_contact_listen_enabled(False)
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        assert contact_mod.slack_listen_enabled() is False

    def test_hear_ack_when_turn_does_not_post(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        self._stub_resolve(monkeypatch)
        monkeypatch.setattr(
            contact_mod,
            "run_contact_estelle_turn",
            MagicMock(
                return_value={
                    "ok": False,
                    "outcome": "failure",
                    "reply": None,
                    "slack_post": {"ok": False, "error": "no_token"},
                    "error": "no_token",
                }
            ),
        )
        post = MagicMock(return_value={"ok": True, "ts": "10.0"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        monkeypatch.setattr(
            contact_mod, "contact_is_production_deploy", MagicMock(return_value=False)
        )
        monkeypatch.setattr(contact_mod, "get_deploy_label", MagicMock(return_value="staging"))
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-hear-1",
                "event": {
                    "type": "app_mention",
                    "user": "U-hear",
                    "channel": "C-hear",
                    "ts": "3.3",
                    "text": "<@BOT> ping",
                },
            },
        )
        assert out["accepted"] is True
        assert out["hear_ack_post"]["ok"] is True
        # AST-2072: no recognition post for a bound sender — hear-ack is the only post,
        # top-level under the default threads_only.
        assert "recognition_post" not in out
        post.assert_called_once()
        hear = post.call_args.kwargs
        assert hear["channel"] == "C-hear"
        assert hear["thread_ts"] is None
        # AST-2085: no env prefix, even off production.
        assert hear["text"] == CONTACT_CONFIG["hear_ack_reply_text"]
        rows = contact_mod.list_estelle_activity()
        assert len(rows) == 1
        assert rows[0]["slack_user_id"] == "U-hear"
        assert rows[0]["last_channel"] == "C-hear"

    def test_no_hear_ack_when_turn_posted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        self._stub_resolve(monkeypatch)
        _stub_estelle_turn(monkeypatch)
        post = MagicMock(return_value={"ok": True, "ts": "11.0"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-hear-skip",
                "event": {
                    "type": "app_mention",
                    "user": "U2",
                    "channel": "C2",
                    "ts": "4.0",
                    "text": "hi",
                },
            },
        )
        assert out["accepted"] is True
        assert "hear_ack_post" not in out
        # AST-2072: no recognition post; the (stubbed) turn already posted so no hear-ack either.
        post.assert_not_called()
        assert "recognition_post" not in out


    def test_listen_off_skips_hear_ack(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        post = MagicMock()
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-hear-off",
                "event": {
                    "type": "app_mention",
                    "user": "U3",
                    "channel": "C3",
                    "ts": "5.0",
                    "text": "x",
                },
            },
        )
        assert out == {"accepted": False, "reason": "listen_off"}
        post.assert_not_called()

    def test_background_wrapper_logs_exception(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        monkeypatch.setattr(
            contact_mod,
            "handle_slack_event",
            MagicMock(side_effect=RuntimeError("boom")),
        )
        with caplog.at_level(logging.ERROR):
            contact_mod._run_handle_slack_event_background({"event_id": "Ev-x"}, False)
        assert "handle_slack_event background failed" in caplog.text
        assert "boom" in caplog.text


# Branches: username backfill on match; activity gets identity (AST-1105).
class TestAst1105SlackUsernameDisplay:
    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def test_resolve_backfills_missing_username(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value="c1"))
        monkeypatch.setattr(
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "state": "PROSPECT",
                    "candidate_data": {"contact": {"slack_user_id": "U1"}},
                }
            ),
        )
        monkeypatch.setattr(
            contact_mod,
            "fetch_user_profile",
            MagicMock(
                return_value={
                    "slack_user_id": "U1",
                    "username": "backfilled",
                    "display_name": "BF",
                    "first": "",
                    "last": "",
                }
            ),
        )
        save = MagicMock()
        monkeypatch.setattr(contact_mod, "save_candidate_data", save)
        out = contact_mod.resolve_slack_user("U1", estelle_in_play=True)
        assert out["slack_username"] == "backfilled"
        assert out["slack_display_name"] == "BF"
        assert out["created"] is False
        save.assert_called_once()
        assert save.call_args.args[0] == "c1"
        assert save.call_args.args[1] == {
            "contact": {"slack_user_id": "U1", "slack_username": "backfilled"}
        }

    def test_handle_records_activity_identity(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "state": "PROSPECT",
                    "created": False,
                    "slack_username": "ada",
                    "slack_display_name": "Ada L",
                }
            ),
        )
        _stub_estelle_turn(monkeypatch)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-1105",
                "event": {
                    "type": "app_mention",
                    "user": "U-1105",
                    "channel": "C-1105",
                    "ts": "1.1",
                    "text": "<@BOT> hi",
                },
            },
        )
        assert out["accepted"] is True
        row = contact_mod.list_estelle_activity()[0]
        assert row["slack_user_id"] == "U-1105"
        assert row["slack_username"] == "ada"
        assert row["slack_display_name"] == "Ada L"


# Branches: debug default; durable re-read; set persist; listen file untouched (AST-1206).
class TestAst1206ContactDebugFlag:
    """AST-1206: durable Contact Slack debug SoT — mirror listen get/set, separate file."""

    def test_slack_debug_enabled_default_off(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "debug_enabled", False)
        assert contact_mod.slack_debug_enabled() is False
        assert CONTACT_CONFIG["debug_enabled"] is False

    def test_slack_debug_rereads_durable_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.data.contact_debug import save_contact_debug_enabled
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "debug_enabled", False)
        save_contact_debug_enabled(True)
        assert contact_mod.slack_debug_enabled() is True
        assert CONTACT_CONFIG["debug_enabled"] is True
        save_contact_debug_enabled(False)
        monkeypatch.setitem(CONTACT_CONFIG, "debug_enabled", True)
        assert contact_mod.slack_debug_enabled() is False

    def test_set_slack_debug_enabled_persists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.data.contact_debug import load_contact_debug_enabled
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        monkeypatch.setitem(CONTACT_CONFIG, "debug_enabled", False)
        assert contact_mod.set_slack_debug_enabled(True, debug=False) is True
        assert CONTACT_CONFIG["debug_enabled"] is True
        assert load_contact_debug_enabled() is True
        assert contact_mod.slack_debug_enabled() is True
        path = tmp_path / CONTACT_CONFIG["debug_state_filename"]
        assert path.is_file()
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw == {"debug_enabled": True}

    def test_set_debug_does_not_touch_listen_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        listen = tmp_path / CONTACT_CONFIG["listen_state_filename"]
        listen.write_text(
            json.dumps({"listen_enabled": True}, indent=2) + "\n",
            encoding="utf-8",
        )
        before = listen.read_text(encoding="utf-8")
        contact_mod.set_slack_debug_enabled(True, debug=False)
        assert listen.read_text(encoding="utf-8") == before
        assert (tmp_path / CONTACT_CONFIG["debug_state_filename"]).is_file()

    def test_set_rejects_non_bool(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import ASTRAL_CONFIG

        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        with pytest.raises(TypeError, match="enabled must be bool"):
            contact_mod.set_slack_debug_enabled("yes", debug=False)  # type: ignore[arg-type]


# Branches: Events hydrate debug from durable SoT; kwarg ignored (AST-1207).
class TestAst1207DurableDebugSot:
    """AST-1207: Manage Slack durable debug is sole SoT for Events/handle ingress."""

    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def test_handle_ignores_kwarg_when_durable_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "slack_debug_enabled", MagicMock(return_value=False))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        log = MagicMock()
        monkeypatch.setattr(contact_mod, "get_logger", lambda _n: log)
        out = contact_mod.handle_slack_event(
            {"event_id": "Ev-sot-off", "event": {"type": "app_mention", "user": "U1"}},
            debug=True,
        )
        assert out == {"accepted": False, "reason": "listen_off"}
        log.set_debug_flag.assert_called_with(False)
        log.debug_index.assert_not_called()

    def test_handle_hydrates_on_and_passes_debug_to_turn(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "slack_debug_enabled", MagicMock(return_value=True))
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "state": "PROSPECT",
                    "created": False,
                }
            ),
        )
        turn = _stub_estelle_turn(monkeypatch)
        log = MagicMock()
        monkeypatch.setattr(contact_mod, "get_logger", lambda _n: log)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-sot-on",
                "event": {
                    "type": "app_mention",
                    "user": "U1",
                    "channel": "C1",
                    "ts": "1.0",
                    "text": "hi",
                },
            },
            debug=False,
        )
        assert out["accepted"] is True
        log.set_debug_flag.assert_called_with(True)
        turn.assert_called_once()
        assert turn.call_args.kwargs["debug"] is True

    def test_receive_ignores_kwarg_when_durable_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        secret = "signing-secret"
        monkeypatch.setenv(CONTACT_CONFIG["signing_secret_env"], secret)
        monkeypatch.setattr(contact_mod, "slack_debug_enabled", MagicMock(return_value=False))
        log = MagicMock()
        monkeypatch.setattr(contact_mod, "get_logger", lambda _n: log)
        body = json.dumps({"type": "url_verification", "challenge": "ch-sot"}).encode()
        ts = str(int(time.time()))
        status, out = contact_mod.receive_slack_events_http(
            body,
            timestamp=ts,
            signature=_sign(secret, ts, body),
            debug=True,
        )
        assert status == 200
        assert out == {"challenge": "ch-sot"}
        log.set_debug_flag.assert_called_with(False)


# Branches: markup parse/strip; dispatch allowlist + handler_unavailable; turn strip/follow-up (AST-1515).
class TestAst1515ContactTaskMarkup:
    """AST-1515: contact-task markup helpers and dispatch router."""

    def test_parse_and_strip_markup(self) -> None:
        text = "Hello ~~/gazer_scrape https://example.com/jd~~ world ~~/unknown_key x~~"
        spans = contact_mod.parse_contact_task_markup(text)
        assert spans == [
            ("gazer_scrape", "https://example.com/jd"),
            ("unknown_key", "x"),
        ]
        stripped = contact_mod.strip_contact_task_markup(text)
        assert "~~/" not in stripped
        assert "Hello" in stripped and "world" in stripped

    def test_strip_collapses_blank_lines(self) -> None:
        assert contact_mod.strip_contact_task_markup("a\n\n\n\nb") == "a\n\nb"

    def test_contact_tasks_shallow_copy(self) -> None:
        tasks = contact_mod.contact_tasks()
        tasks["gazer_scrape"] = {"mutated": True}
        assert "mutated" not in contact_mod.contact_tasks()["gazer_scrape"]

    def test_dispatch_skips_unknown_keys(self) -> None:
        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="c1",
            markup_spans=[("not_a_real_key", "x")],
        )
        assert results == []

    def test_dispatch_handler_unavailable_for_listed_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # All five handlers resolve — mock missing import path.
        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: None
        )
        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="c1",
            markup_spans=[("gazer_scrape", "https://x.example/jd")],
        )
        assert len(results) == 1
        assert results[0]["ok"] is False
        assert results[0]["error"] == "handler_unavailable"
        assert results[0]["task_key"] == "gazer_scrape"

    def test_dispatch_no_candidate_when_required(self) -> None:
        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="",
            markup_spans=[("gazer_scrape", "https://x.example/jd")],
        )
        assert results[0]["error"] == "no_candidate"

    def test_dispatch_sync_handler(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _fake_handler(cid, param, debug=False):
            return {"ok": True, "payload": param, "candidate": cid}

        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: _fake_handler
        )
        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="c99",
            markup_spans=[("get_job_data", "job-1")],
        )
        assert results[0]["ok"] is True
        assert results[0]["payload"] == "job-1"

    def test_dispatch_debug_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        log = MagicMock()
        monkeypatch.setattr(contact_mod, "get_logger", lambda _n: log)
        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: None
        )
        contact_mod.run_contact_task_dispatch(
            astral_candidate_id="c1",
            markup_spans=[("gazer_scrape", "u")],
            debug=True,
        )
        log.set_debug_flag.assert_called_with(True)
        outcomes = [c.kwargs.get("outcome") for c in log.debug_index.call_args_list]
        assert outcomes == ["found", "recorded"]
        assert log.debug_index.call_args.kwargs["func"] == "contact.run_contact_task_dispatch"


class TestAst1515ContactEstelleTurnMarkup:
    """AST-1515: Estelle turn strips markup, dispatches, optional same-event follow-up."""

    def setup_method(self) -> None:
        contact_mod._context_cache.clear()
        contact_mod._seen_event_ids.clear()

    def _patch_turn(
        self,
        monkeypatch: pytest.MonkeyPatch,
        side_effect,
    ) -> tuple[MagicMock, dict]:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "load_slack_conversation_context",
            MagicMock(
                return_value={
                    "channel": "C1",
                    "thread_ts": "",
                    "messages": [],
                    "source": "cache",
                }
            ),
        )
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(side_effect=_turn_candidate_row))
        monkeypatch.setattr(contact_mod, "contact_skills", MagicMock(return_value={}))
        post = MagicMock(return_value={"ok": True, "ts": "9.0"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        monkeypatch.setattr(contact_mod, "format_contact_reply_text", lambda text: text)
        calls = {"n": 0}

        async def _do_task(*_a, **kwargs):
            idx = calls["n"]
            calls["n"] += 1
            return side_effect(idx, kwargs)

        import src.core.agent as agent_mod

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        return post, calls

    def test_strips_markup_before_slack_post(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: None
        )

        def side(idx, _kwargs):
            if idx == 0:
                return {
                    "success": True,
                    "conversational_outcome": "success",
                    "agent_performance": {"status": "success"},
                    "parsed_response": {
                        "reply": "Sure! ~~/gazer_scrape https://jobs.example/1~~",
                    },
                }
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "I'll check that posting for you."},
            }

        post, calls = self._patch_turn(monkeypatch, side)
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="link?", astral_candidate_id="c1", debug=False
        )
        assert out["ok"] is True
        assert calls["n"] == 2
        assert "~~/" not in post.call_args.kwargs["text"]
        assert post.call_args.kwargs["text"] == "I'll check that posting for you."
        assert len(out["contact_task_results"]) == 1
        assert out["contact_task_results"][0]["error"] == "handler_unavailable"

    def test_no_follow_up_for_unknown_markup_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def side(idx, _kwargs):
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "Ok ~~/not_in_config foo~~"},
            }

        post, calls = self._patch_turn(monkeypatch, side)
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="?", astral_candidate_id="c1", debug=False
        )
        assert calls["n"] == 1
        assert out["contact_task_results"] == []
        assert post.call_args.kwargs["text"] == "Ok"

    def test_follow_up_turn_includes_task_results_in_live_content(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: None
        )
        captured: dict = {}

        def side(idx, kwargs):
            if idx == 0:
                return {
                    "success": True,
                    "conversational_outcome": "success",
                    "agent_performance": {"status": "success"},
                    "parsed_response": {
                        "reply": "Checking ~~/gazer_scrape https://x.example~~",
                    },
                }
            captured["live"] = kwargs.get("live_content") or ""
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "Page looks ok."},
            }

        post, calls = self._patch_turn(monkeypatch, side)
        out = contact_mod.run_contact_estelle_turn(
            channel="C1", text="?", astral_candidate_id="c1", debug=False
        )
        assert calls["n"] == 2
        assert "## Contact task results (same inbound event)" in captured["live"]
        assert post.call_args.kwargs["text"] == "Page looks ok."

    def test_live_content_lists_contact_tasks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict = {}

        def side(idx, kwargs):
            if idx == 0:
                captured["live"] = kwargs.get("live_content") or ""
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "Hi"},
            }

        self._patch_turn(monkeypatch, side)
        contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", astral_candidate_id="c1", debug=False
        )
        live = captured["live"]
        assert "## Available contact tasks (markup)" in live
        for key in CONTACT_TASK_CONFIG:
            assert f"- {key}:" in live


# --- AST-1531: contact_land_meteorite → stage_meteorite ---


class TestAst1531ContactLandStageCutover:
    """contact_land_meteorite requires source handle and stages blob (no raw land)."""

    def test_requires_source_kind_and_id(self) -> None:
        from src.utils.config import METEORITE_CONFIG

        err = METEORITE_CONFIG["land_outcome_error"]
        out = contact_mod.contact_land_meteorite("c1", source_kind="", source_id="x", text="JD")
        assert out["outcome"] == err
        out2 = contact_mod.contact_land_meteorite(
            "c1", source_kind="email", source_id="", text="JD"
        )
        assert out2["outcome"] == err
        out3 = contact_mod.contact_land_meteorite(
            "c1", source_kind="not-a-kind", source_id="s1", text="JD"
        )
        assert out3["outcome"] == err

    def test_stages_text_blob_with_source_handle(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.core import meteorite as meteorite_mod
        from src.utils.config import METEORITE_CONFIG

        created = METEORITE_CONFIG["land_outcome_created"]
        seen = {}

        async def _stage(cid, blob, *, source_kind, source_id, debug=False):
            seen.update(
                {
                    "cid": cid,
                    "blob": blob,
                    "source_kind": source_kind,
                    "source_id": source_id,
                }
            )
            return {
                "skipped": False,
                "outcome": created,
                "land": {"outcome": created, "error": None},
                "error": None,
                "scraps": [],
            }

        monkeypatch.setattr(meteorite_mod, "stage_meteorite", _stage)
        out = contact_mod.contact_land_meteorite(
            "c1",
            source_kind="slack",
            source_id="T1.msg9",
            text="Senior eng JD text",
            job_link="https://jobs.example.com/r",
            debug=False,
        )
        assert out["outcome"] == created
        assert seen["cid"] == "c1"
        assert seen["source_kind"] == "slack"
        assert seen["source_id"] == "T1.msg9"
        assert "Senior eng JD text" in seen["blob"]
        assert "https://jobs.example.com/r" in seen["blob"]

    def test_empty_blob_errors_without_stage(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import meteorite as meteorite_mod
        from src.utils.config import METEORITE_CONFIG

        stage = AsyncMock()
        monkeypatch.setattr(meteorite_mod, "stage_meteorite", stage)
        out = contact_mod.contact_land_meteorite(
            "c1", source_kind="paste", source_id="p1", text="  ", scraps=None
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_error"]
        assert "blob" in (out.get("error") or "").lower()
        stage.assert_not_awaited()


@pytest.mark.skipif(
    not hasattr(contact_mod, "try_meteorite_apply_paste_from_slack"),
    reason="AST-1561 contact paste routing not on this publish tip",
)
class TestAst1561ContactPasteRouting:
    """AST-1561: Slack paste → apply_paste before Estelle classify."""

    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def test_try_apply_paste_thread_match(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-slack-paste"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        row_id = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": cid,
                    "source_kind": "email",
                    "source_id": "m1",
                    "link": "https://x/j",
                    "state": "NEW",
                }
            ]
        )[0]
        db.update_meteorite(
            row_id,
            state="BOT_BLOCKED_SCRAPE_METEORITE",
            estelle_thread_ts="7777.8888",
        )
        out = contact_mod.try_meteorite_apply_paste_from_slack(
            astral_candidate_id=cid,
            channel="D1",
            thread_ts="7777.8888",
            message_ts=None,
            text="Pasted JD " + ("y" * 40),
        )
        assert out["applied"] is True
        assert out["result"]["ok"] is True
        assert db.get_meteorite(row_id)["state"] == "READY"

    def test_handle_slack_event_skips_estelle_turn_on_paste(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-slack-hook"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "H"})
        row_id = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": cid,
                    "source_kind": "paste",
                    "source_id": "blob-hook",
                    "state": "NEW",
                }
            ]
        )[0]
        db.update_meteorite(row_id, state="BOT_BLOCKED_SCRAPE_METEORITE")
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": cid,
                    "state": "PROSPECT",
                    "created": False,
                }
            ),
        )
        turn = _stub_estelle_turn(monkeypatch)
        monkeypatch.setattr(
            contact_mod,
            "contact_post_message",
            MagicMock(return_value={"ok": True, "ts": "1.1"}),
        )
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-paste-hook",
                "event": {
                    "type": "message",
                    "user": "U1",
                    "channel": "D1",
                    "ts": "1.0",
                    "text": "JD body " + ("z" * 40),
                },
            },
            debug=False,
        )
        assert out["accepted"] is True
        assert out["estelle_turn"]["outcome"] == "paste_applied"
        turn.assert_not_called()
        assert db.get_meteorite(row_id)["state"] == "READY"

    def test_estelle_turn_land_calls_use_apply_paste(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-turn-paste"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "T"})
        row_id = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": cid,
                    "source_kind": "paste",
                    "source_id": "blob-turn",
                    "state": "NEW",
                }
            ]
        )[0]
        db.update_meteorite(row_id, state="BOT_BLOCKED_SCRAPE_METEORITE")
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "load_slack_conversation_context",
            MagicMock(return_value={"channel": "D1", "thread_ts": "", "messages": [], "source": "cache"}),
        )
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(side_effect=_turn_candidate_row))
        monkeypatch.setattr(contact_mod, "contact_skills", MagicMock(return_value={}))
        monkeypatch.setattr(contact_mod, "contact_post_message", MagicMock(return_value={"ok": True}))
        monkeypatch.setattr(contact_mod, "format_contact_reply_text", lambda t: t)
        land = MagicMock()
        monkeypatch.setattr(contact_mod, "contact_land_meteorite", land)

        async def _do_task(*_a, **_k):
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {
                    "reply": "thanks",
                    "land_calls": [{"text": "ignored"}],
                },
            }

        import src.core.agent as agent_mod

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        out = contact_mod.run_contact_estelle_turn(
            channel="D1",
            text="Turn paste " + ("q" * 40),
            astral_candidate_id=cid,
            debug=False,
        )
        assert out["ok"] is True
        assert out["land_results"][0]["via"] == "apply_paste"
        land.assert_not_called()
        assert db.get_meteorite(row_id)["state"] == "READY"


# Branches: resolve hit/miss/owner; dispatch UUID / pin_required; Estelle raft strip+inject.
class TestAst1585ContactPinnedBaseResume:
    """AST-1585: Contact pin→body + refuse blob dual-read for pilot base_resume."""

    def test_resolve_hit_and_owner_gate(self, seeded_db) -> None:
        db = seeded_db
        blob = {"professional_summary": "pinned-v1", "candidate_name": "Ada"}
        uid = db.save_artifact("candidate", "cand-1", "base_resume", blob)
        assert contact_mod.resolve_pinned_base_resume("cand-1", uid) == blob
        assert contact_mod.resolve_pinned_base_resume("other", uid) is None
        assert contact_mod.resolve_pinned_base_resume("cand-1", "missing-uuid") is None
        assert contact_mod.resolve_pinned_base_resume("", uid) is None
        assert contact_mod.resolve_pinned_base_resume("cand-1", "") is None

    def test_dispatch_uuid_short_circuit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        pin = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        body = {"professional_summary": "from-pin"}
        spy = MagicMock(return_value=body)
        monkeypatch.setattr(contact_mod, "resolve_pinned_base_resume", spy)
        handler = MagicMock(return_value={"ok": True, "result": "blob"})
        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: handler
        )
        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="cand-1",
            markup_spans=[("get_candidate_data", pin)],
        )
        assert results == [
            {"ok": True, "task_key": "get_candidate_data", "result": body}
        ]
        spy.assert_called_once_with("cand-1", pin, debug=False)
        handler.assert_not_called()

        spy.return_value = None
        miss = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="cand-1",
            markup_spans=[("get_candidate_data", pin)],
        )
        assert miss[0]["ok"] is False
        assert miss[0]["error"] == "not_found"
        handler.assert_not_called()

    def test_dispatch_refuses_blob_dotted_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        handler = MagicMock(return_value={"ok": True, "result": "blob"})
        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: handler
        )
        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="cand-1",
            markup_spans=[("get_candidate_data", "artifacts.base_resume")],
        )
        assert results == [
            {
                "ok": False,
                "error": "pin_required",
                "task_key": "get_candidate_data",
            }
        ]
        handler.assert_not_called()

    def test_estelle_turn_strips_blob_and_injects_pin(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        pin = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        pinned = {"professional_summary": "operative"}
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "load_slack_conversation_context",
            MagicMock(
                return_value={
                    "channel": "C1",
                    "thread_ts": "",
                    "messages": [],
                    "source": "cache",
                }
            ),
        )
        monkeypatch.setattr(
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "astral_candidate_id": "cand-1",
                    "candidate_data": {
                        "artifacts": {
                            "base_resume": {"professional_summary": "blob-stale"},
                            "resume_structure": {"sections": {}},
                        }
                    },
                }
            ),
        )
        monkeypatch.setattr(
            contact_mod, "resolve_pinned_base_resume", MagicMock(return_value=pinned)
        )
        monkeypatch.setattr(contact_mod, "contact_skills", MagicMock(return_value={}))
        monkeypatch.setattr(
            contact_mod, "contact_post_message", MagicMock(return_value={"ok": True})
        )
        monkeypatch.setattr(contact_mod, "format_contact_reply_text", lambda text: text)
        captured: dict = {}

        async def _do_task(*_a, **kwargs):
            captured["candidate_data"] = kwargs["ctx"]["candidate_data"]
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "Hi"},
            }

        import src.core.agent as agent_mod

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        out = contact_mod.run_contact_estelle_turn(
            channel="C1",
            text="hi",
            astral_candidate_id="cand-1",
            base_resume_artifact_id=pin,
            debug=False,
        )
        assert out["ok"] is True
        raft = captured["candidate_data"]
        assert raft["artifacts"]["base_resume"] == pinned
        assert raft["artifacts"]["base_resume"]["professional_summary"] != "blob-stale"
        contact_mod.resolve_pinned_base_resume.assert_called_once_with(
            "cand-1", pin, debug=False
        )

        # No pin: blob stripped, no inject
        captured.clear()
        monkeypatch.setattr(
            contact_mod, "resolve_pinned_base_resume", MagicMock(return_value=pinned)
        )
        contact_mod.run_contact_estelle_turn(
            channel="C1",
            text="hi",
            astral_candidate_id="cand-1",
            debug=False,
        )
        raft2 = captured["candidate_data"]
        assert "base_resume" not in (raft2.get("artifacts") or {})
        contact_mod.resolve_pinned_base_resume.assert_not_called()



# Branches: unbound filter; known/unknown recognition; unknown skips Estelle (AST-1668).
class TestAst1668UnboundAndRecognition:
    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def test_list_unbound_omits_bound_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1738: unbound source becomes list_workspace_members; keep posters stub so
        # pre-fix trees still exercise the filter until make-fix lands.
        pool = [
            {"slack_user_id": "U_FREE", "username": "free"},
            {"slack_user_id": "U_BOUND", "username": "bound"},
            {"slack_user_id": "  ", "username": "blank"},
            "skip",
        ]
        monkeypatch.setattr(contact_mod, "list_workspace_posters", MagicMock(return_value=pool))
        monkeypatch.setattr(
            contact_mod, "list_workspace_members", MagicMock(return_value=pool), raising=False
        )

        def _lookup(sid: str, *, debug: bool = False):
            return "c1" if sid == "U_BOUND" else None

        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", _lookup)
        out = contact_mod.list_unbound_slack_users()
        assert out == [{"slack_user_id": "U_FREE", "username": "free"}]

    def test_bound_sender_no_recognition_then_estelle(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "state": "INTAKE_INITIATED",
                    "created": False,
                }
            ),
        )
        turn = _stub_estelle_turn(monkeypatch)
        post = MagicMock(return_value={"ok": True, "ts": "9.9"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-1668-known",
                "event": {
                    "type": "app_mention",
                    "user": "U1",
                    "channel": "C1",
                    "ts": "1.0",
                    "text": "hi",
                },
            },
        )
        assert out["accepted"] is True
        # AST-2072: the canned known-recognition reply is gone; the turn is the only answer.
        assert "recognition_post" not in out
        post.assert_not_called()
        turn.assert_called_once()
        assert out["estelle_turn"]["ok"] is True
        assert out["estelle_turn"].get("skipped") is not True

    def test_unknown_recognition_skips_estelle(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(
                return_value={
                    "astral_candidate_id": None,
                    "state": None,
                    "created": False,
                    "slack_username": "stranger",
                    "slack_display_name": "Stranger",
                }
            ),
        )
        turn = _stub_estelle_turn(monkeypatch)
        paste = MagicMock(return_value={"applied": False})
        monkeypatch.setattr(contact_mod, "try_meteorite_apply_paste_from_slack", paste)
        post = MagicMock(return_value={"ok": True, "ts": "8.8"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        out = contact_mod.handle_slack_event(
            {
                "event_id": "Ev-1668-unk",
                "event": {
                    "type": "app_mention",
                    "user": "U-new",
                    "channel": "C1",
                    "ts": "2.0",
                    "text": "hi",
                },
            },
        )
        assert out["accepted"] is True
        assert out["candidate_created"] is False
        assert out["astral_candidate_id"] is None
        assert out["recognition_post"]["ok"] is True
        assert CONTACT_CONFIG["unknown_recognition_reply_text"] in post.call_args.kwargs["text"]
        assert out["estelle_turn"] == {
            "ok": True,
            "outcome": "unrecognized",
            "skipped": True,
        }
        turn.assert_not_called()
        paste.assert_not_called()
        assert "hear_ack_post" not in out


# Branches: unbound from members when posters empty (AST-1738 bug-repro).
class TestAst1738UnboundMembersNotPosters:
    """[bug-repro] empty poster pool must not empty the unbound bind list."""

    def test_unbound_lists_members_when_posters_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Pre-fix: list_unbound_slack_users only calls list_workspace_posters → [].
        # Post-fix: calls list_workspace_members → humans below.
        members = [
            {"slack_user_id": "U_FREE", "username": "free.user"},
            {"slack_user_id": "U_BOUND", "username": "bound.user"},
        ]
        posters = MagicMock(return_value=[])
        monkeypatch.setattr(contact_mod, "list_workspace_posters", posters)
        monkeypatch.setattr(
            contact_mod,
            "list_workspace_members",
            MagicMock(return_value=members),
            raising=False,
        )

        def _lookup(sid: str, *, debug: bool = False):
            return "c1" if sid == "U_BOUND" else None

        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", _lookup)
        out = contact_mod.list_unbound_slack_users()
        assert out == [{"slack_user_id": "U_FREE", "username": "free.user"}]
        posters.assert_not_called()



# Branches: channel list passthrough; membership unbound/member/not_member;
# snapshot missing channel / happy path (AST-1788).
class TestAst1788AdminSlackChannelOrchestration:
    def test_list_admin_slack_channels_passthrough(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        channels = [{"id": "C1", "name": "alpha"}]
        stub = MagicMock(return_value=channels)
        monkeypatch.setattr(contact_mod, "list_bot_channels", stub)
        assert contact_mod.list_admin_slack_channels() == channels
        stub.assert_called_once_with()

    def test_membership_unbound_skips_external(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "candidate_data": {"contact": {}},
                }
            ),
        )
        ext = MagicMock()
        monkeypatch.setattr(contact_mod, "is_channel_member", ext)
        out = contact_mod.check_admin_slack_channel_membership(
            astral_candidate_id="c1", channel=" C9 "
        )
        assert out == {
            "channel": "C9",
            "slack_user_id": "",
            "is_member": False,
            "warn": True,
            "warn_reason": "unbound",
        }
        ext.assert_not_called()

    def test_membership_member_and_not_member(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "candidate_data": {
                        "contact": {"slack_user_id": " U1 "}
                    },
                }
            ),
        )
        ext = MagicMock(return_value=True)
        monkeypatch.setattr(contact_mod, "is_channel_member", ext)
        out = contact_mod.check_admin_slack_channel_membership(
            astral_candidate_id="c1", channel="C1"
        )
        assert out["is_member"] is True
        assert out["warn"] is False
        assert out["warn_reason"] is None
        assert out["slack_user_id"] == "U1"
        ext.assert_called_once_with(channel="C1", slack_user_id="U1")

        ext.return_value = False
        out2 = contact_mod.check_admin_slack_channel_membership(
            astral_candidate_id="c1", channel="C1"
        )
        assert out2["is_member"] is False
        assert out2["warn"] is True
        assert out2["warn_reason"] == "not_member"

    def test_membership_missing_candidate_and_channel(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(return_value=None))
        with pytest.raises(ValueError, match="candidate not found"):
            contact_mod.check_admin_slack_channel_membership(
                astral_candidate_id="missing", channel="C1"
            )
        with pytest.raises(ValueError, match="channel is required"):
            contact_mod.check_admin_slack_channel_membership(
                astral_candidate_id="c1", channel="  "
            )

    def test_snapshot_requires_stored_channel(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "candidate_data": {"contact": {"slack_channel_name": "x"}},
                }
            ),
        )
        with pytest.raises(ValueError, match="slack_channel_id is required"):
            contact_mod.get_admin_slack_channel_snapshot(astral_candidate_id="c1")

    def test_snapshot_happy_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "astral_candidate_id": "c1",
                    "candidate_data": {
                        "contact": {
                            "slack_channel_id": " C_SNAP ",
                            "slack_channel_name": " snap ",
                        }
                    },
                }
            ),
        )
        msgs = [{"ts": "1.0", "text": "hi"}]
        hist = MagicMock(return_value=msgs)
        monkeypatch.setattr(contact_mod, "fetch_full_conversation_history", hist)
        out = contact_mod.get_admin_slack_channel_snapshot(astral_candidate_id=" c1 ")
        assert out == {
            "astral_candidate_id": "c1",
            "channel_id": "C_SNAP",
            "channel_name": "snap",
            "messages": msgs,
        }
        hist.assert_called_once_with(channel="C_SNAP")


# AST-2035: leading @Estelle /<command> intercept via CONTACT_CONFIG["commands"] (ticket AC1–AC9).
# Branches: parse hit (bare / label link / bare <url> / |label mention / no mention / multi-line) vs
# miss (mid-sentence, unregistered, non-str); code ok → one ack, no turn, no hear-ack; code handler
# soft-fail → no ack, hear-ack; empty payload → usage; agent → one turn with result in live content;
# unbound → unknown reply, no insert; BOT_BLOCKED_SCRAPE_METEORITE row untouched, paste recovery skipped.
class TestAst2035ContactCommandIntercept:
    URL = "http://www.dice.com/jobs/13234abcd"
    TS = "1700000000.000100"

    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def _bound(self, monkeypatch: pytest.MonkeyPatch, cid: str | None = "cand-2035") -> MagicMock:
        """Listen on, sender resolves to cid (None = unbound), posts captured; returns post mock."""
        import src.data.contact_estelle_activity as activity_mod

        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(return_value={"astral_candidate_id": cid, "state": "PROSPECT", "created": False}),
        )
        # Keep the durable activity file out of the repo tree.
        monkeypatch.setattr(activity_mod, "record_estelle_activity", MagicMock())
        post = MagicMock(return_value={"ok": True, "ts": "9.9"})
        monkeypatch.setattr(contact_mod, "contact_post_message", post)
        return post

    def _handle(self, text: str, eid: str, *, channel: str = "C1", etype: str = "app_mention") -> dict:
        return contact_mod.handle_slack_event(
            {
                "event_id": eid,
                "event": {"type": etype, "user": "U1", "channel": channel, "ts": self.TS, "text": text},
            },
            debug=False,
        )

    @staticmethod
    def _posts_with(post: MagicMock, needle: str) -> list:
        return [c for c in post.call_args_list if needle in str(c.kwargs.get("text") or "")]

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("<@UBOT> /add-job", ("add-job", "")),
            (f"<@UBOT> /add-job <{URL}|www.dice.com/jobs/13234abcd>", ("add-job", URL)),
            (f"<@UBOT> /add-job <{URL}>", ("add-job", URL)),
            (f"<@UBOT|estelle> /add-job {URL}", ("add-job", URL)),
            (f"/add-job {URL}", ("add-job", URL)),
            ("<@UBOT> <@UOTHER> /add-job line one\nline two", ("add-job", "line one\nline two")),
            ("<@UBOT> can you /add-job this later", None),
            ("<@UBOT> /not-a-command payload", None),
            (None, None),
        ],
    )
    def test_parse_contact_command(self, text, expected) -> None:
        assert contact_mod.parse_contact_command(text) == expected

    def test_registry_ships_add_job_code_mode(self) -> None:
        from src.core import meteorite as meteorite_mod

        meta = CONTACT_CONFIG["commands"]["add-job"]
        assert meta["mode"] == "code"
        assert contact_mod._resolve_contact_task_handler(meta["handler"]) is meteorite_mod.insert_slack_meteorite
        assert "{meteorite_id}" in meta["ack_reply_template"]

    def test_ac1_link_markup_lands_raw_at_new(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        self._bound(monkeypatch)
        out = self._handle(f"<@UBOT> /add-job <{self.URL}|www.dice.com/jobs/13234abcd>", "Ev-2035-ac1")
        rows = db.list_meteorites_by_source("slack", f"C1:{self.TS}")
        assert len(rows) == 1
        row = rows[0]
        assert (row["candidate_id"], row["state"], row["source_kind"]) == ("cand-2035", "NEW", "slack")
        assert row["classify_outcome"] is None
        assert row["content"] == self.URL
        assert not any(ch in row["content"] for ch in "<>|")
        assert row["estelle_thread_ts"] == self.TS
        assert out["estelle_turn"]["command"]["meteorite_id"] == row["id"]

    def test_ac2_multiline_text_in_dm_lands_one_row(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        self._bound(monkeypatch)
        jd = "Senior Engineer\nAcme Corp\n\nResponsibilities:\n- build things"
        self._handle(f"<@UBOT> /add-job {jd}", "Ev-2035-ac2", channel="D1", etype="message")
        rows = db.list_meteorites_by_source("slack", f"D1:{self.TS}")
        assert len(rows) == 1
        assert rows[0]["state"] == "NEW" and rows[0]["classify_outcome"] is None
        assert rows[0]["content"] == jd
        assert "/add-job" not in rows[0]["content"] and "<@" not in rows[0]["content"]

    def test_ac3_code_mode_no_llm_one_ack_no_hear_ack(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import src.core.agent as agent_mod

        post = self._bound(monkeypatch)
        do_task = AsyncMock()
        monkeypatch.setattr(agent_mod, "do_task", do_task)
        out = self._handle(f"<@UBOT> /add-job {self.URL}", "Ev-2035-ac3")
        do_task.assert_not_called()
        turn = out["estelle_turn"]
        assert turn["outcome"] == "add-job"
        mid = turn["command"]["meteorite_id"]
        assert isinstance(mid, int)
        # AST-2072 dropped the recognition post, so the ack is the only post and names the new id.
        post.assert_called_once()
        assert len(self._posts_with(post, str(mid))) == 1
        assert "hear_ack_post" not in out
        assert self._posts_with(post, CONTACT_CONFIG["hear_ack_reply_text"]) == []

    def test_ac4_agent_mode_one_turn_with_id(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        monkeypatch.setitem(CONTACT_CONFIG["commands"]["add-job"], "mode", "agent")
        self._bound(monkeypatch)
        turn = _stub_estelle_turn(monkeypatch)
        out = self._handle(f"<@UBOT> /add-job {self.URL}", "Ev-2035-ac4")
        rows = db.list_meteorites_by_source("slack", f"C1:{self.TS}")
        assert len(rows) == 1
        turn.assert_called_once()
        extra = turn.call_args.kwargs["extra_context"]
        assert json.loads(extra)["meteorite_id"] == rows[0]["id"]
        # Slack reply is the turn's reply.
        assert out["estelle_turn"]["reply"] == "stub-reply"
        assert out["estelle_turn"]["command"]["mode"] == "agent"

    def test_ac4_extra_context_reaches_turn_live_content(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import src.core.agent as agent_mod

        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "load_slack_conversation_context",
            MagicMock(return_value={"channel": "C1", "thread_ts": "", "messages": [], "source": "cache"}),
        )
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(side_effect=_turn_candidate_row))
        monkeypatch.setattr(contact_mod, "contact_skills", MagicMock(return_value={}))
        monkeypatch.setattr(contact_mod, "contact_post_message", MagicMock(return_value={"ok": True}))
        seen: list = []

        async def _do_task(*_args, **kwargs):
            seen.append(kwargs.get("live_content") or "")
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": "saved it"},
            }

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        contact_mod.run_contact_estelle_turn(
            channel="C1", text="/add-job x", astral_candidate_id="cand-2035",
            extra_context='{"id": "add-job", "meteorite_id": 4242}', debug=False,
        )
        assert len(seen) == 1
        assert "## Command result (this inbound event)" in seen[0]
        assert "4242" in seen[0]

    def test_ac5_bot_blocked_row_untouched_paste_skipped(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-2035"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        blocked = db.insert_meteorite_rows(
            [{"candidate_id": cid, "source_kind": "paste", "source_id": "blob-2035", "state": "NEW"}]
        )[0]
        db.update_meteorite(blocked, state="BOT_BLOCKED_SCRAPE_METEORITE", estelle_thread_ts=self.TS)
        before = db.get_meteorite(blocked)
        self._bound(monkeypatch, cid)
        paste = MagicMock(return_value={"applied": False})
        monkeypatch.setattr(contact_mod, "try_meteorite_apply_paste_from_slack", paste)
        jd = "Pasted JD " + ("p" * 60)
        self._handle(f"<@UBOT> /add-job {jd}", "Ev-2035-ac5")
        paste.assert_not_called()
        after = db.get_meteorite(blocked)
        assert after["state"] == "BOT_BLOCKED_SCRAPE_METEORITE"
        assert after["content"] == before["content"]
        rows = db.list_meteorites_by_source("slack", f"C1:{self.TS}")
        assert len(rows) == 1 and rows[0]["state"] == "NEW" and rows[0]["content"] == jd

    def test_ac6_unbound_sender_no_insert(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        post = self._bound(monkeypatch, None)
        out = self._handle(f"<@UBOT> /add-job {self.URL}", "Ev-2035-ac6-unk")
        assert db.list_meteorites_by_source("slack", f"C1:{self.TS}") == []
        assert out["estelle_turn"]["outcome"] == "unrecognized"
        assert len(self._posts_with(post, CONTACT_CONFIG["unknown_recognition_reply_text"])) == 1

    def test_ac6_bare_command_posts_usage_no_insert(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        post = self._bound(monkeypatch)
        out = self._handle("<@UBOT> /add-job", "Ev-2035-ac6-bare")
        assert db.list_meteorites_by_source("slack", f"C1:{self.TS}") == []
        assert out["estelle_turn"]["command"]["error"] == "empty_payload"
        usage = CONTACT_CONFIG["commands"]["add-job"]["usage_reply_text"]
        assert len(self._posts_with(post, usage)) == 1
        assert "hear_ack_post" not in out

    def test_ac7_mid_sentence_takes_normal_turn(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        self._bound(monkeypatch)
        monkeypatch.setattr(
            contact_mod, "try_meteorite_apply_paste_from_slack", MagicMock(return_value={"applied": False})
        )
        turn = _stub_estelle_turn(monkeypatch)
        out = self._handle("<@UBOT> can you /add-job this later", "Ev-2035-ac7")
        turn.assert_called_once()
        assert turn.call_args.kwargs.get("extra_context") is None
        assert out["estelle_turn"]["outcome"] == "success"
        assert db.list_meteorites_by_source("slack", f"C1:{self.TS}") == []

    def test_code_mode_handler_miss_no_ack_hear_ack_fires(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Plan Decision: a soft-fail posts no ack, so the AST-1101 hear-ack fallback fires.
        self._bound(monkeypatch)
        handler = MagicMock(return_value={"ok": False, "meteorite_id": None, "error": "db locked"})
        monkeypatch.setattr(contact_mod, "_resolve_contact_task_handler", MagicMock(return_value=handler))
        out = self._handle(f"<@UBOT> /add-job {self.URL}", "Ev-2035-miss")
        handler.assert_called_once()
        assert handler.call_args.kwargs["source_id"] == f"C1:{self.TS}"
        assert out["estelle_turn"]["slack_post"] is None
        assert out["estelle_turn"]["command"]["error"] == "db locked"
        assert out["hear_ack_post"]["ok"] is True

    def test_ac8_no_command_literals_in_core(self) -> None:
        import re

        pat = re.compile(r"['\"]/?add-job['\"]")
        hits = [
            f"{p}:{n}"
            for p in Path("src/core").rglob("*.py")
            for n, line in enumerate(p.read_text().splitlines(), 1)
            if pat.search(line)
        ]
        assert hits == []

    def test_ac9_info_lines_with_debug_off(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        self._bound(monkeypatch)
        with caplog.at_level(logging.INFO):
            out = self._handle(f"<@UBOT> /add-job {self.URL}", "Ev-2035-ac9")
        mid = out["estelle_turn"]["command"]["meteorite_id"]
        infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
        listen = [
            m for m in infos
            if m.startswith("cand-2035 | contact listen app_mention add-job:")
            and "add-job:code" in m and f"meteorite:{mid}" in m
        ]
        assert len(listen) == 1
        assert sum(m.startswith(f"{mid} | meteorite state: NEW") for m in infos) == 1


# Branches: app_mention public/mpim/lookup-error refused before resolve; group passes;
# event channel_type skips lookup; DM message not gated (AST-2061).
class TestAst2061PrivateChannelGate:
    @staticmethod
    def _event(**overrides: str) -> dict:
        # Public-channel mention carrying a bound /add-job command (the AST-2061 repro fixture).
        event = {
            "type": "app_mention",
            "user": "U1",
            "channel": "C1PUBLIC",
            "ts": "1.0",
            "text": "<@UBOT> /add-job https://x.io/1",
        }
        event.update(overrides)
        return event

    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def _patch(self, monkeypatch: pytest.MonkeyPatch, *, ctype=None, side_effect=None) -> dict:
        import src.data.contact_estelle_activity as activity_mod

        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        lookup = MagicMock(return_value=ctype, side_effect=side_effect)
        # raising=False: pre-fix contact has no fetch_channel_type ([bug-repro] runs).
        monkeypatch.setattr(contact_mod, "fetch_channel_type", lookup, raising=False)
        mocks = {
            "lookup": lookup,
            "resolve": MagicMock(
                return_value={"astral_candidate_id": "c1", "state": "PROSPECT", "created": False}
            ),
            "command": MagicMock(return_value={"ok": True}),
            "paste": MagicMock(return_value={"applied": False}),
            "post": MagicMock(return_value={"ok": True}),
        }
        monkeypatch.setattr(contact_mod, "resolve_slack_user", mocks["resolve"])
        monkeypatch.setattr(contact_mod, "_run_contact_command", mocks["command"])
        monkeypatch.setattr(contact_mod, "try_meteorite_apply_paste_from_slack", mocks["paste"])
        monkeypatch.setattr(contact_mod, "contact_post_message", mocks["post"])
        mocks["turn"] = _stub_estelle_turn(monkeypatch)
        # Keep the tracked data/contact_estelle_activity.json out of the repo tree.
        monkeypatch.setattr(activity_mod, "record_estelle_activity", MagicMock())
        return mocks

    @staticmethod
    def _handle(event: dict, eid: str) -> dict:
        return contact_mod.handle_slack_event({"event_id": eid, "event": dict(event)}, debug=False)

    @staticmethod
    def _assert_refused(out: dict, mocks: dict) -> None:
        assert out == {"accepted": False, "reason": "channel_not_private"}
        for key in ("resolve", "command", "paste", "turn", "post"):
            mocks[key].assert_not_called()

    def test_public_mention_refused_no_command_turn_or_save(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # [bug-repro] AST-2061: a public-channel mention gets no resolve, command, turn, or save.
        mocks = self._patch(monkeypatch, ctype="channel")
        out = self._handle(self._event(), "Ev-2061-public")
        self._assert_refused(out, mocks)

    def test_mpim_mention_refused(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mocks = self._patch(monkeypatch, ctype="mpim")
        out = self._handle(self._event(), "Ev-2061-mpim")
        self._assert_refused(out, mocks)

    def test_lookup_error_fails_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mocks = self._patch(monkeypatch, side_effect=RuntimeError("missing_scope"))
        out = self._handle(self._event(), "Ev-2061-lookup-err")
        self._assert_refused(out, mocks)

    def test_private_group_mention_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mocks = self._patch(monkeypatch, ctype="group")
        out = self._handle(self._event(text="hi"), "Ev-2061-group")
        assert out["accepted"] is True
        mocks["lookup"].assert_called_once_with("C1PUBLIC")
        mocks["turn"].assert_called_once()

    def test_event_channel_type_skips_lookup(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mocks = self._patch(monkeypatch, ctype="channel")
        out = self._handle(self._event(text="hi", channel_type="im"), "Ev-2061-evtype")
        assert out["accepted"] is True
        mocks["lookup"].assert_not_called()

    def test_dm_message_not_gated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mocks = self._patch(monkeypatch, ctype="channel")
        event = {"type": "message", "user": "U1", "channel": "D1", "channel_type": "im", "ts": "1.0", "text": "hi"}
        out = self._handle(event, "Ev-2061-dm")
        assert out["accepted"] is True
        mocks["lookup"].assert_not_called()


# Branches: land blob unwrap+sanitize; markup-only blob → blob is required; Slack paste unwrap (AST-2061).
class TestAst2061ContactSanitizeEntry:
    @staticmethod
    def _capture_stage(monkeypatch: pytest.MonkeyPatch) -> dict:
        from src.core import meteorite as meteorite_mod
        from src.utils.config import METEORITE_CONFIG

        created = METEORITE_CONFIG["land_outcome_created"]
        seen: dict = {"calls": 0}

        async def _stage(cid, blob, *, source_kind, source_id, debug=False):
            seen["calls"] += 1
            seen["blob"] = blob
            return {
                "skipped": False,
                "outcome": created,
                "land": {"outcome": created, "error": None},
                "error": None,
                "scraps": [],
            }

        monkeypatch.setattr(meteorite_mod, "stage_meteorite", _stage)
        return seen

    def test_land_blob_unwrapped_then_sanitized(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # [bug-repro] AST-2061: Slack link unwrapped, markup stripped, entities decoded before staging.
        seen = self._capture_stage(monkeypatch)
        contact_mod.contact_land_meteorite(
            "c1",
            source_kind="slack",
            source_id="C1:1",
            text="<https://x.io/job?id=1&amp;src=slack|Job> <img src=x onerror=alert(1)>Senior Eng",
            employer_name="Acme",
        )
        assert seen["blob"] == "https://x.io/job?id=1&src=slack Senior Eng\n\nEmployer: Acme"

    def test_land_markup_only_blob_is_required_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        seen = self._capture_stage(monkeypatch)
        out = contact_mod.contact_land_meteorite(
            "c1", source_kind="slack", source_id="C1:2", text="<script>alert(1)</script>"
        )
        assert out["error"] == "blob is required"
        assert seen["calls"] == 0

    def test_slack_paste_unwrapped_before_apply_paste(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # [bug-repro] AST-2061: raw Slack link markup is unwrapped, not mangled by the HTML branch.
        from src.core import meteorite as meteorite_mod

        db = sqlite_in_memory
        db.save_candidate("c1", state="NEW_CANDIDATE", candidate_data={"name": "P"})
        row_id = db.insert_meteorite_rows(
            [
                {
                    "candidate_id": "c1",
                    "source_kind": "email",
                    "source_id": "mid-2061-paste",
                    "classify_outcome": None,
                    "content": None,
                    "link": "https://blocked.example/j",
                    "state": "NEW",
                }
            ]
        )[0]
        db.update_meteorite(row_id, state="BOT_BLOCKED_SCRAPE_METEORITE", link="https://blocked.example/j")
        monkeypatch.setattr(meteorite_mod, "find_meteorite_for_estelle_thread", lambda **_k: {"id": row_id})
        out = contact_mod.try_meteorite_apply_paste_from_slack(
            astral_candidate_id="c1",
            channel="D1",
            thread_ts="1.0",
            message_ts="1.0",
            text="Full JD <https://x.io/j?a=1&amp;b=2|link>",
        )
        assert out["applied"] is True
        row = db.get_meteorite(row_id)
        assert row["content"] == "Full JD https://x.io/j?a=1&b=2"
        assert row["state"] == "READY"


# Branches: _contact_reply_placement 3 modes x top-level/in-thread; contact_post_message broadcast
# pass-through + top-level cache key; every handle_slack_event reply site (turn, usage, code ack,
# paste ack, hear-ack, unknown) per thread_response; bound turn = one post; /add-job handler anchor
# stays the message ts; listen info line; exact unknown / fallback text; AC1/AC9 source scans (AST-2072).
class TestAst2072ThreadResponsePlacement:
    TS = "1700000000.000200"
    THREAD = "1699999999.000100"
    URL = "http://www.dice.com/jobs/2072"

    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()
        contact_mod._context_cache.clear()

    def _wire(
        self, monkeypatch: pytest.MonkeyPatch, mode: str, *, cid: str | None = "c1", reply: str | None = "Hi from Estelle"
    ) -> MagicMock:
        """Listen on, sender resolves to cid (None = unbound), real turn with stubbed do_task.

        Patches the external ``post_message`` (not ``contact_post_message``) so the real reply path,
        broadcast pass-through and cache append all run. Production deploy = no ``[env]`` prefix.
        Returns the external post mock.
        """
        import src.core.agent as agent_mod
        import src.data.contact_estelle_activity as activity_mod

        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setitem(CONTACT_CONFIG, "thread_response", mode)
        monkeypatch.setattr(
            contact_mod,
            "resolve_slack_user",
            MagicMock(return_value={"astral_candidate_id": cid, "state": "PROSPECT", "created": False}),
        )
        # Keep the durable activity file out of the repo tree.
        monkeypatch.setattr(activity_mod, "record_estelle_activity", MagicMock())
        monkeypatch.setattr(
            contact_mod,
            "load_slack_conversation_context",
            MagicMock(return_value={"channel": "C1", "thread_ts": "", "messages": [], "source": "cache"}),
        )
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(side_effect=_turn_candidate_row))
        # raising=False: AST-2061 retires contact_skills; this class must not care which side of it runs.
        monkeypatch.setattr(contact_mod, "contact_skills", MagicMock(return_value={}), raising=False)
        monkeypatch.setattr(
            contact_mod, "try_meteorite_apply_paste_from_slack", MagicMock(return_value={"applied": False})
        )
        monkeypatch.setattr(contact_mod, "contact_is_production_deploy", MagicMock(return_value=True))

        async def _do_task(*_a, **_k):
            # reply=None -> failed turn, nothing posted, so the hear-ack fallback fires.
            if reply is None:
                return {"success": False}
            return {
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {"reply": reply},
            }

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        post = MagicMock(return_value={"ok": True, "ts": "9.9"})
        monkeypatch.setattr(contact_mod, "post_message", post)
        return post

    def _handle(self, eid: str, text: str = "<@UBOT> hi", *, thread_ts: str | None = None) -> dict:
        event = {"type": "app_mention", "user": "U1", "channel": "C1", "ts": self.TS, "text": text}
        if thread_ts:
            event["thread_ts"] = thread_ts
        return contact_mod.handle_slack_event({"event_id": eid, "event": event}, debug=False)

    @staticmethod
    def _placements(post: MagicMock) -> list:
        return [(c.kwargs["thread_ts"], c.kwargs["reply_broadcast"]) for c in post.call_args_list]

    @pytest.mark.parametrize(
        ("mode", "thread_ts", "expected"),
        [
            ("threads_only", None, (None, False)),
            ("threads_only", "7.0", ("7.0", False)),
            ("always_no_share", None, ("5.0", False)),
            ("always_no_share", "7.0", ("7.0", False)),
            ("always_with_share", None, ("5.0", True)),
            ("always_with_share", "7.0", ("7.0", True)),
        ],
    )
    def test_placement_helper(self, monkeypatch: pytest.MonkeyPatch, mode, thread_ts, expected) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "thread_response", mode)
        assert contact_mod._contact_reply_placement(thread_ts, "5.0") == expected

    def test_contact_post_message_broadcast_and_top_level_cache_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        post = MagicMock(return_value={"ok": True, "ts": "6.6"})
        monkeypatch.setattr(contact_mod, "post_message", post)
        contact_mod.contact_post_message(channel="C1", text="threaded", thread_ts="7.0", reply_broadcast=True)
        assert post.call_args.kwargs == {
            "channel": "C1", "text": "threaded", "thread_ts": "7.0", "reply_broadcast": True,
        }
        contact_mod.contact_post_message(channel="C1", text="top")
        assert (post.call_args.kwargs["thread_ts"], post.call_args.kwargs["reply_broadcast"]) == (None, False)
        # Cache keys on the thread actually posted to: threaded -> (C1, 7.0), top-level -> (C1, "").
        assert contact_mod._context_cache[("C1", "7.0")]["messages"][-1]["text"] == "threaded"
        assert contact_mod._context_cache[("C1", "")]["messages"][-1]["text"] == "top"

    def test_ac3_bound_turn_is_the_only_post(self, monkeypatch: pytest.MonkeyPatch) -> None:
        post = self._wire(monkeypatch, "threads_only")
        out = self._handle("Ev-2072-ac3")
        post.assert_called_once()
        assert post.call_args.kwargs["text"] == "Hi from Estelle"
        assert "recognition_post" not in out and "hear_ack_post" not in out

    @pytest.mark.parametrize(
        ("mode", "in_thread", "expected"),
        [
            ("threads_only", False, (None, False)),
            ("threads_only", True, (THREAD, False)),
            ("always_no_share", False, (TS, False)),
            ("always_no_share", True, (THREAD, False)),
            ("always_with_share", False, (TS, True)),
            ("always_with_share", True, (THREAD, True)),
        ],
    )
    def test_ac4_to_7_turn_reply_placement(
        self, monkeypatch: pytest.MonkeyPatch, mode, in_thread, expected
    ) -> None:
        post = self._wire(monkeypatch, mode)
        self._handle(f"Ev-2072-{mode}-{in_thread}", thread_ts=self.THREAD if in_thread else None)
        assert self._placements(post) == [expected]

    @pytest.mark.parametrize("mode", ["threads_only", "always_with_share"])
    @pytest.mark.parametrize("site", ["turn", "usage", "code_ack", "paste_ack", "hear_ack", "unknown"])
    def test_ac8_every_reply_site_obeys_setting(self, monkeypatch: pytest.MonkeyPatch, mode, site) -> None:
        post = self._wire(
            monkeypatch, mode,
            cid=None if site == "unknown" else "c1",
            reply=None if site == "hear_ack" else "Hi from Estelle",
        )
        text = "<@UBOT> hi"
        if site == "usage":
            text = "<@UBOT> /add-job"
        elif site == "code_ack":
            text = f"<@UBOT> /add-job {self.URL}"
            handler = MagicMock(return_value={"ok": True, "meteorite_id": 42})
            monkeypatch.setattr(contact_mod, "_resolve_contact_task_handler", MagicMock(return_value=handler))
        elif site == "paste_ack":
            monkeypatch.setattr(
                contact_mod,
                "try_meteorite_apply_paste_from_slack",
                MagicMock(return_value={"applied": True, "result": {"ok": True}}),
            )
        out = self._handle(f"Ev-2072-ac8-{site}-{mode}", text)
        # Guard against the event silently taking a different branch than the site under test.
        expected_outcome = {
            "turn": "success", "usage": "add-job", "code_ack": "add-job",
            # A failed do_task leaves the turn without an outcome; the hear-ack is what posts.
            "paste_ack": "paste_applied", "hear_ack": None, "unknown": "unrecognized",
        }[site]
        assert out["estelle_turn"]["outcome"] == expected_outcome
        assert ("hear_ack_post" in out) is (site == "hear_ack")
        # Top-level inbound: threads_only -> top-level, no broadcast; always_with_share -> under msg ts + broadcast.
        expected = (None, False) if mode == "threads_only" else (self.TS, True)
        assert self._placements(post) == [expected]

    def test_ac10_handler_anchor_is_message_ts_under_threads_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        post = self._wire(monkeypatch, "threads_only")
        handler = MagicMock(return_value={"ok": True, "meteorite_id": 42})
        monkeypatch.setattr(contact_mod, "_resolve_contact_task_handler", MagicMock(return_value=handler))
        self._handle("Ev-2072-ac10", f"<@UBOT> /add-job {self.URL}")
        # Reply goes top-level, but the stored anchor is still the inbound message ts.
        assert handler.call_args.kwargs["thread_ts"] == self.TS
        assert self._placements(post) == [(None, False)]

    def test_ac12_one_listen_info_line_debug_off(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        self._wire(monkeypatch, "threads_only")
        with caplog.at_level(logging.INFO):
            self._handle("Ev-2072-ac12")
        infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
        assert sum("| contact listen app_mention " in m for m in infos) == 1

    def test_ac13_unbound_sender_exact_text_no_turn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        post = self._wire(monkeypatch, "threads_only", cid=None)
        turn = _stub_estelle_turn(monkeypatch)
        out = self._handle("Ev-2072-ac13")
        post.assert_called_once()
        assert post.call_args.kwargs["text"] == "Sorry, I don't recognize you, yet.  Let's check with @susan"
        assert post.call_args.kwargs["text"] == CONTACT_CONFIG["unknown_recognition_reply_text"]
        turn.assert_not_called()
        assert out["estelle_turn"]["outcome"] == "unrecognized"

    def test_ac14_failed_turn_posts_exact_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        post = self._wire(monkeypatch, "threads_only", reply=None)
        out = self._handle("Ev-2072-ac14")
        post.assert_called_once()
        assert post.call_args.kwargs["text"] == "That didn't work as planned.  Let's ask @susan."
        assert post.call_args.kwargs["text"] == CONTACT_CONFIG["hear_ack_reply_text"]
        assert out["hear_ack_post"]["ok"] is True

    def test_ac1_ac14_retired_strings_absent_from_src(self) -> None:
        import re

        src_root = Path(contact_mod.__file__).resolve().parents[1]
        # \b keeps unknown_recognition_reply_text (still shipped) from matching the retired key.
        pat = re.compile(r"\bknown_recognition_reply_text\b|I know who that is|Heard you")
        hits = [
            f"{p}:{i}"
            for p in src_root.rglob("*.py")
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            if pat.search(line)
        ]
        assert hits == []

    def test_ac9_placement_logic_only_in_helper_and_anchors(self) -> None:
        import ast
        import re

        src = Path(contact_mod.__file__).read_text(encoding="utf-8")
        pat = re.compile(r"thread_ts or message_ts|thread_ts or msg_ts|reply_thread_ts = event\.get")
        funcs = [n for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        def owner(lineno: int) -> str:
            # Innermost def whose span covers the line ("<module>" = placement logic outside any function).
            spans = [f for f in funcs if f.lineno <= lineno <= f.end_lineno]
            return max(spans, key=lambda f: f.lineno).name if spans else "<module>"

        owners = sorted(owner(i) for i, line in enumerate(src.splitlines(), 1) if pat.search(line))
        # Plan Stage 2 step 7: the helper, the _run_contact_command handler anchor, and the
        # paste-recovery lookup anchor (not a reply site) — no per-site placement copies.
        assert owners == ["_contact_reply_placement", "_run_contact_command", "try_meteorite_apply_paste_from_slack"]
