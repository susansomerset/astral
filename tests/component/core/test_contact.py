"""Component tests for src/core/contact.py (AST-1066 scaffold + AST-1071 skill runners)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import contact as contact_mod
from src.core import candidate as candidate_mod
from src.utils.config import CONTACT_CONFIG, TASK_CONFIG


# Branches: listen default; skills shallow copy; env-name map; prefix format; no TASK_CONFIG collision.
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
