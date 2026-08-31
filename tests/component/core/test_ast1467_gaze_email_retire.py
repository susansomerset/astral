"""AST-1467 [bug-repro]: gaze_email identity retired; mailbox lives on meteorite_email only.

Fails on the pre-fix tip (legacy gaze_email still live). Passes once AST-1466 make-fix
lands the rehome. Root cause: duplicate mailbox identity after AST-1128 + later consolidations.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from src.utils import config as cfg


class TestAst1467GazeEmailRetired:
    """Inventory gate — AssertionError (not ImportError) while gaze_email still ships."""

    def test_agent_task_seed_has_no_gaze_email(self) -> None:
        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        keys = {r["task_key"] for r in rows if r.get("current") == 1}
        assert "gaze_email" not in keys
        assert "meteorite_email" in keys

    def test_uat_fixture_lockstep_has_no_gaze_email(self) -> None:
        rows = json.loads(
            Path("docs/uat-fixtures/AST-756/expected-agent_task.json").read_text(
                encoding="utf-8"
            )
        )
        keys = {r["task_key"] for r in rows if r.get("current") == 1}
        assert "gaze_email" not in keys
        assert "meteorite_email" in keys

    def test_gaze_email_config_and_task_shell_gone(self) -> None:
        assert not hasattr(cfg, "GAZE_EMAIL_CONFIG")
        assert "gaze_email" not in cfg.TASK_CONFIG

    def test_mailbox_config_is_meteorite_email_only(self) -> None:
        assert hasattr(cfg, "METEORITE_EMAIL_MAILBOX_CONFIG")
        m = cfg.METEORITE_EMAIL_MAILBOX_CONFIG
        assert m["task_key"] == "meteorite_email"
        assert m["account_address"] == "astral.career.match@gmail.com"
        assert m["debug_func"] == "meteorite.check_inbox"
        assert "unbound_retention_days" not in m
        assert "debug_func_selected" not in m
        assert not hasattr(cfg, "INBOX_BIND_CONFIG")

    def test_gaze_email_module_gone_meteorite_email_deleted(self) -> None:
        assert importlib.util.find_spec("src.core.gaze_email") is None
        assert importlib.util.find_spec("src.core.meteorite_email") is None

    def test_dispatcher_provision_symbols_rehomed(self) -> None:
        from src.core import dispatcher as d

        assert not hasattr(d, "provision_gaze_email_dispatch_tasks")
        assert not hasattr(d, "ensure_gaze_email_dispatch_task")
        assert not hasattr(d, "_gaze_email_due_tasks")
        assert hasattr(d, "provision_meteorite_email_dispatch_tasks")
        assert hasattr(d, "ensure_meteorite_email_dispatch_task")
        assert hasattr(d, "_meteorite_email_due_tasks")
