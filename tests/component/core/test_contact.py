"""Component tests for src/core/contact.py (AST-1066)."""

from __future__ import annotations

from src.core import contact as contact_mod
from src.utils.config import CONTACT_CONFIG, TASK_CONFIG


# Branches: listen default; empty skills ACL; env-name map; prefix format; no TASK_CONFIG collision.
class TestAst1066ContactScaffold:
    def test_slack_listen_enabled_default_off(self) -> None:
        assert contact_mod.slack_listen_enabled() is False
        assert CONTACT_CONFIG["listen_enabled"] is False

    def test_contact_skills_empty_shallow_copy(self) -> None:
        skills = contact_mod.contact_skills()
        assert skills == {}
        assert contact_mod.contact_skill_keys() == ()
        # Shallow copy — mutating return must not touch CONTACT_CONFIG.
        skills["should_not_leak"] = {}
        assert "should_not_leak" not in CONTACT_CONFIG["skills"]
        assert contact_mod.contact_skill_keys() == ()

    def test_slack_env_names_are_names_only(self) -> None:
        names = contact_mod.slack_env_names()
        assert names == {
            "bot_token": "SLACK_BOT_TOKEN",
            "signing_secret": "SLACK_SIGNING_SECRET",
        }
        # Values never returned — keys are logical, values are environ *names*.
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
