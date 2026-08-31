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
            contact_mod,
            "get_candidate",
            MagicMock(
                return_value={
                    "state": "INTAKE_INITIATED",
                    "candidate_data": {"contact": {"slack_user_id": "U1", "slack_username": "ada"}},
                }
            ),
        )
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
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
        create.assert_not_called()
        save.assert_not_called()

    def test_resolve_miss_without_estelle_does_not_create(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(contact_mod, "get_candidate_id_for_query", MagicMock(return_value=None))
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
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
                    "username": "ada.lovelace",
                }
            ),
        )
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
        out = contact_mod.resolve_slack_user("Unew", estelle_in_play=True)
        assert out["created"] is True
        assert out["state"] == "PROSPECT"
        assert out["astral_candidate_id"] == "slack-unew"
        assert out["slack_username"] == "ada.lovelace"
        assert out["slack_display_name"] == "ada"
        create.assert_called_once()
        assert create.call_args.args[0] == "slack-unew"
        assert create.call_args.args[1] == {
            "contact": {"slack_user_id": "Unew", "slack_username": "ada.lovelace"}
        }
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
                    "username": "onlydisplay",
                }
            ),
        )
        create = MagicMock()
        monkeypatch.setattr(contact_mod, "initiate_prospect_candidate", create)
        contact_mod.resolve_slack_user("Ux", estelle_in_play=True)
        assert create.call_args.args[1] == {
            "contact": {"slack_user_id": "Ux", "slack_username": "onlydisplay"}
        }
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
        post.assert_called_once()
        assert post.call_args.kwargs["channel"] == "C-hear"
        assert post.call_args.kwargs["thread_ts"] == "3.3"
        text = post.call_args.kwargs["text"]
        assert text.startswith("[staging] ")
        assert CONTACT_CONFIG["hear_ack_reply_text"] in text
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
        post.assert_not_called()

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
        # All six handlers resolve after AST-1517 — mock missing import path.
        monkeypatch.setattr(
            contact_mod, "_resolve_contact_task_handler", lambda _h: None
        )
        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="c1",
            markup_spans=[("create_contact_meteorite", "https://x.example/jd")],
        )
        assert len(results) == 1
        assert results[0]["ok"] is False
        assert results[0]["error"] == "handler_unavailable"
        assert results[0]["task_key"] == "create_contact_meteorite"

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
            markup_spans=[("create_contact_meteorite", "u")],
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
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(return_value=None))
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
                        "reply": "Sure! ~~/create_contact_meteorite https://jobs.example/1~~",
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
                        "reply": "Checking ~~/create_contact_meteorite https://x.example~~",
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
                }
            ]
        )[0]
        db.update_meteorite(
            row_id,
            state="BOT_BLOCKED",
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
                }
            ]
        )[0]
        db.update_meteorite(row_id, state="BOT_BLOCKED")
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
                }
            ]
        )[0]
        db.update_meteorite(row_id, state="BOT_BLOCKED")
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
        monkeypatch.setattr(
            contact_mod,
            "load_slack_conversation_context",
            MagicMock(return_value={"channel": "D1", "thread_ts": "", "messages": [], "source": "cache"}),
        )
        monkeypatch.setattr(contact_mod, "get_candidate", MagicMock(return_value=None))
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

