"""Component tests for src/core/contact.py (AST-1066 scaffold + AST-1069 ingress + AST-1071 skill runners)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from unittest.mock import MagicMock, patch

import pytest

from src.core import contact as contact_mod
from src.core import candidate as candidate_mod
from src.utils.config import CONTACT_CONFIG, TASK_CONFIG


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

    def test_non_production_reply_prefix(self) -> None:
        assert contact_mod.non_production_reply_prefix("staging") == "[staging] "
        assert contact_mod.non_production_reply_prefix("  prod-like  ") == "[prod-like] "
        assert contact_mod.non_production_reply_prefix("") == "[] "
        assert contact_mod.non_production_reply_prefix("   ") == "[] "

    def test_skill_keys_do_not_collide_with_task_config(self) -> None:
        for skill_key in contact_mod.contact_skill_keys():
            assert skill_key not in TASK_CONFIG


# Branches: ACL inventory; meta; allowlisted write; reject path/skill/missing; Style D on/off.
class TestAst1071ContactSkillRunners:
    _PROFILE = "save_candidate_profile"
    _CONTACT = "save_candidate_contact"

    def test_contact_skill_meta_and_unknown(self) -> None:
        meta = contact_mod.contact_skill_meta(self._PROFILE)
        assert meta["entity"] == "candidate"
        assert meta["write"] is True
        assert meta["allowed_paths"] == (
            "profile.first",
            "profile.last",
            "profile.pronoun_preference",
            "profile.contact_email",
        )
        assert isinstance(meta["allowed_paths"], tuple)
        with pytest.raises(ValueError, match="unknown contact skill"):
            contact_mod.contact_skill_meta("not_a_skill")

    def test_run_writes_allowlisted_profile_path(self, sqlite_in_memory) -> None:
        cid = "c-1071-prof"
        from src.utils.config import CANDIDATE_STATES

        state = "NEW_CANDIDATE" if "NEW_CANDIDATE" in CANDIDATE_STATES else "NEW"
        sqlite_in_memory.save_candidate(cid, state=state, candidate_data={})
        out = contact_mod.run_contact_skill(
            self._PROFILE,
            astral_candidate_id=cid,
            fields={"profile.first": "Ada"},
        )
        assert out["ok"] is True
        assert out["paths_written"] == ["profile.first"]
        row = candidate_mod.get_candidate(cid)
        assert (row.get("candidate_data") or {}).get("profile", {}).get("first") == "Ada"

    def test_run_writes_allowlisted_contact_path(self, sqlite_in_memory) -> None:
        cid = "c-1071-contact"
        from src.utils.config import CANDIDATE_STATES

        state = "NEW_CANDIDATE" if "NEW_CANDIDATE" in CANDIDATE_STATES else "NEW"
        sqlite_in_memory.save_candidate(cid, state=state, candidate_data={})
        out = contact_mod.run_contact_skill(
            self._CONTACT,
            astral_candidate_id=cid,
            fields={"contact.contact_email": "ada@example.com"},
        )
        assert out["ok"] is True
        assert "contact.contact_email" in out["paths_written"]
        row = candidate_mod.get_candidate(cid)
        assert (row.get("candidate_data") or {})["contact"]["contact_email"] == "ada@example.com"

    def test_run_rejects_non_allowlisted_and_unknown_skill(self, sqlite_in_memory) -> None:
        cid = "c-1071-reject"
        from src.utils.config import CANDIDATE_STATES

        state = "NEW_CANDIDATE" if "NEW_CANDIDATE" in CANDIDATE_STATES else "NEW"
        sqlite_in_memory.save_candidate(cid, state=state, candidate_data={})
        with pytest.raises(ValueError, match="path not allowlisted"):
            contact_mod.run_contact_skill(
                self._PROFILE,
                astral_candidate_id=cid,
                fields={"profile.middle": "X"},
            )
        with pytest.raises(ValueError, match="unknown contact skill"):
            contact_mod.run_contact_skill(
                "save_everything",
                astral_candidate_id=cid,
                fields={"profile.first": "Ada"},
            )
        with pytest.raises(ValueError, match="candidate not found"):
            contact_mod.run_contact_skill(
                self._PROFILE,
                astral_candidate_id="missing",
                fields={"profile.first": "Ada"},
            )

    def test_run_debug_true_emits_style_d(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        log = MagicMock()
        monkeypatch.setattr(contact_mod, "logger", log)
        cid = "c-1071-dbg"
        from src.utils.config import CANDIDATE_STATES

        state = "NEW_CANDIDATE" if "NEW_CANDIDATE" in CANDIDATE_STATES else "NEW"
        sqlite_in_memory.save_candidate(cid, state=state, candidate_data={})
        contact_mod.run_contact_skill(
            self._PROFILE,
            astral_candidate_id=cid,
            fields={"profile.first": "Ada"},
            debug=True,
        )
        log.set_debug_flag.assert_called_with(True)
        outcomes = [c.kwargs.get("outcome") for c in log.debug_index.call_args_list]
        assert outcomes == ["found", "recorded"]
        assert log.debug_detail.call_count >= 2

    def test_run_debug_false_skips_style_d(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        log = MagicMock()
        monkeypatch.setattr(contact_mod, "logger", log)
        cid = "c-1071-quiet"
        from src.utils.config import CANDIDATE_STATES

        state = "NEW_CANDIDATE" if "NEW_CANDIDATE" in CANDIDATE_STATES else "NEW"
        sqlite_in_memory.save_candidate(cid, state=state, candidate_data={})
        contact_mod.run_contact_skill(
            self._PROFILE,
            astral_candidate_id=cid,
            fields={"profile.first": "Ada"},
            debug=False,
        )
        log.set_debug_flag.assert_not_called()
        log.debug_index.assert_not_called()
        log.debug_detail.assert_not_called()


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


# Branches: resolve hit/miss/create gate; Events accept wires resolve (AST-1068).
class TestAst1068ResolveSlackUser:
    def setup_method(self) -> None:
        contact_mod._seen_event_ids.clear()

    def test_resolve_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value="c1"))
        monkeypatch.setattr(
            contact_mod, "get_candidate", MagicMock(return_value={"state": "INTAKE_INITIATED"})
        )
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
        out = contact_mod.resolve_slack_user("U1", estelle_in_play=True)
        assert out == {"astral_candidate_id": "c1", "state": "INTAKE_INITIATED", "created": False}
        create.assert_not_called()

    def test_resolve_miss_without_estelle_does_not_create(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value=None))
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
        fetch = MagicMock()
        monkeypatch.setattr(contact_mod, "fetch_user_profile", fetch)
        out = contact_mod.resolve_slack_user("Umiss", estelle_in_play=False)
        assert out == {"astral_candidate_id": None, "state": None, "created": False}
        create.assert_not_called()
        fetch.assert_not_called()

    def test_resolve_create_prospect(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
                }
            ),
        )
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
        out = contact_mod.resolve_slack_user("Unew", estelle_in_play=True)
        assert out["created"] is True
        assert out["state"] == "PROSPECT"
        assert out["astral_candidate_id"] == "slack-unew"
        create.assert_called_once()
        assert create.call_args.args[0] == "slack-unew"
        assert create.call_args.args[1] == {"contact": {"slack_user_id": "Unew"}}
        assert create.call_args.kwargs.get("first") == "Ada"
        assert create.call_args.kwargs.get("last") == "L"

    def test_resolve_create_seeds_display_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
                }
            ),
        )
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
        contact_mod.resolve_slack_user("Ux", estelle_in_play=True)
        assert create.call_args.args[1] == {"contact": {"slack_user_id": "Ux"}}
        assert create.call_args.kwargs.get("first") == "OnlyDisplay"
        assert create.call_args.kwargs.get("last") == ""

    def test_resolve_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="slack_user_id"):
            contact_mod.resolve_slack_user("  ", estelle_in_play=True)

    def test_handle_accept_wires_resolve(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        resolved = {
            "astral_candidate_id": "slack-u9",
            "state": "PROSPECT",
            "created": True,
        }
        monkeypatch.setattr(contact_mod, "resolve_slack_user", MagicMock(return_value=resolved))
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
        assert out["astral_candidate_id"] == "slack-u9"
        assert out["candidate_state"] == "PROSPECT"
        assert out["candidate_created"] is True
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
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(return_value=None))
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

        async def _do_task(*_a, **_k):
            return do_task_result

        import src.core.agent as agent_mod

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        return {"post": post, "skill": skill}

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
            channel="C1", text="hi", message_ts="2.0", debug=False
        )
        assert out["ok"] is True
        assert out["outcome"] == "success"
        assert out["reply"] == "Hello there"
        deps["post"].assert_called_once()
        assert deps["post"].call_args.kwargs["text"] == "[prefix] Hello there"
        assert deps["post"].call_args.kwargs["thread_ts"] == "2.0"

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
        out = contact_mod.run_contact_estelle_turn(channel="C1", text="hi", debug=False)
        assert out["ok"] is False
        assert out["error"]
        deps["post"].assert_not_called()

    def test_skill_calls_acl_and_no_candidate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        deps = self._patch_turn_deps(
            monkeypatch,
            do_task_result={
                "success": True,
                "conversational_outcome": "success",
                "agent_performance": {"status": "success"},
                "parsed_response": {
                    "reply": "ok",
                    "skill_calls": [
                        {"skill_key": "save_profile_field", "fields": {"profile.first": "Ada"}},
                    ],
                },
            },
        )
        out = contact_mod.run_contact_estelle_turn(channel="C1", text="hi", debug=False)
        assert out["skill_results"] == [
            {"ok": False, "error": "no_candidate", "skill_key": "save_profile_field"}
        ]
        deps["skill"].assert_not_called()

        out2 = contact_mod.run_contact_estelle_turn(
            channel="C1", text="hi", astral_candidate_id="c1", debug=False
        )
        deps["skill"].assert_called_once()
        assert out2["skill_results"][0]["ok"] is True

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
        kwa = log.debug_index.call_args.kwargs
        assert kwa.get("func") == "contact.run_contact_estelle_turn"
        assert kwa.get("outcome") == "success"
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
