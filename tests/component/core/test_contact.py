"""Component tests for src/core/contact.py (AST-1066 scaffold + AST-1069 ingress + AST-1071 skill runners)."""

from __future__ import annotations

from pathlib import Path

import hashlib
import hmac
import json
import time
from unittest.mock import MagicMock, patch

import pytest

from src.core import contact as contact_mod
from src.core import candidate as candidate_mod
from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG, TASK_CONFIG


def _sign(secret: str, timestamp: str, body: bytes) -> str:
    base = f"v0:{timestamp}:".encode("utf-8") + body
    return "v0=" + hmac.new(secret.encode("utf-8"), base, hashlib.sha256).hexdigest()


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

    def test_handle_listen_off(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        out = contact_mod.handle_slack_event(
            {"event_id": "Ev1", "event": {"type": "app_mention", "user": "U1", "channel": "C1", "text": "hi"}},
        )
        assert out == {"accepted": False, "reason": "listen_off"}

    def test_handle_app_mention_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", True)
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


# Branches: hydrate/set listen; production gate; format prefix; post_contact_reply (AST-1067).
class TestAst1067ContactListenCore:
    def setup_method(self) -> None:
        contact_mod._listen_hydrated = False

    def test_hydrate_from_durable_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", tmp_path)
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        contact_mod._listen_hydrated = False
        (tmp_path / CONTACT_CONFIG["listen_state_filename"]).write_text(
            '{"listen_enabled": true}\n', encoding="utf-8"
        )
        assert contact_mod.slack_listen_enabled() is True
        assert CONTACT_CONFIG["listen_enabled"] is True
        (tmp_path / CONTACT_CONFIG["listen_state_filename"]).write_text(
            '{"listen_enabled": false}\n', encoding="utf-8"
        )
        assert contact_mod.slack_listen_enabled() is True

    def test_set_slack_listen_persists_and_applies(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", tmp_path)
        monkeypatch.setitem(CONTACT_CONFIG, "listen_enabled", False)
        contact_mod._listen_hydrated = False
        assert contact_mod.set_slack_listen_enabled(True) is True
        assert CONTACT_CONFIG["listen_enabled"] is True
        assert contact_mod.slack_listen_enabled() is True
        path = tmp_path / CONTACT_CONFIG["listen_state_filename"]
        assert path.is_file()
        assert contact_mod.set_slack_listen_enabled(False) is False
        assert CONTACT_CONFIG["listen_enabled"] is False

    def test_set_rejects_non_bool(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", tmp_path)
        contact_mod._listen_hydrated = False
        with pytest.raises(TypeError, match="bool"):
            contact_mod.set_slack_listen_enabled("yes")  # type: ignore[arg-type]

    def test_contact_is_production_deploy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "production")
        assert contact_mod.contact_is_production_deploy() is True
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "PRODUCTION")
        assert contact_mod.contact_is_production_deploy() is True
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        assert contact_mod.contact_is_production_deploy() is False
        monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        assert contact_mod.contact_is_production_deploy() is False

    def test_format_contact_reply_text_prefix(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        monkeypatch.setattr(contact_mod, "get_deploy_label", lambda: "staging")
        assert contact_mod.format_contact_reply_text("hello") == "[staging] hello"
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "production")
        assert contact_mod.format_contact_reply_text("hello") == "hello"

    def test_post_contact_reply_calls_post_message(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        monkeypatch.setattr(contact_mod, "get_deploy_label", lambda: "staging")
        posted = MagicMock(return_value={"ok": True, "ts": "1.0"})
        monkeypatch.setattr(contact_mod, "post_message", posted)
        out = contact_mod.post_contact_reply(
            channel="C1", text="hi there", thread_ts="9.9"
        )
        assert out == {"ok": True, "ts": "1.0"}
        posted.assert_called_once_with(
            channel="C1", text="[staging] hi there", thread_ts="9.9"
        )

