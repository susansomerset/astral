"""AST-805: rebuild_merge_ticket_log.py --landing-parent prep-uat bypass."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
REBUILD_PATH = REPO_ROOT / "scripts/rebuild_merge_ticket_log.py"


def _load_rebuild_module():
    spec = importlib.util.spec_from_file_location("rebuild_merge_ticket_log", REBUILD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class TestRebuildMergeTicketLogLandingParent:
    def test_collect_entries_unions_landing_parent_not_in_linear_uat(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mod = _load_rebuild_module()
        monkeypatch.setattr(
            mod,
            "fetch_user_testing_parent_ids",
            lambda uat_state_name: ["AST-791"],
        )
        monkeypatch.setattr(
            mod,
            "_resolve_ftr_ref",
            lambda parent_id, dev_ref: (
                f"ftr/{parent_id.lower()}-slug"
                if parent_id in ("AST-791", "AST-801")
                else None
            ),
        )
        monkeypatch.setattr(
            mod,
            "_resolve_recorded_at",
            lambda parent_id, dev_ref, ftr_ref: "2026-06-25T12:00:00+00:00",
        )

        entries = mod._collect_entries(
            "origin/dev",
            "User Testing",
            landing_parent="AST-801",
        )
        ids = [entry["ticket_id"] for entry in entries]
        assert ids == ["AST-791", "AST-801"]

    def test_collect_entries_skips_landing_parent_without_ftr_on_dev(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mod = _load_rebuild_module()
        monkeypatch.setattr(mod, "fetch_user_testing_parent_ids", lambda uat_state_name: [])
        monkeypatch.setattr(
            mod,
            "_resolve_ftr_ref",
            lambda parent_id, dev_ref: None,
        )

        entries = mod._collect_entries(
            "origin/dev",
            "User Testing",
            landing_parent="AST-801",
        )
        assert entries == []

    def test_collect_entries_ignores_blank_landing_parent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mod = _load_rebuild_module()
        monkeypatch.setattr(mod, "fetch_user_testing_parent_ids", lambda uat_state_name: ["AST-791"])
        monkeypatch.setattr(
            mod,
            "_resolve_ftr_ref",
            lambda parent_id, dev_ref: "ftr/ast-791-slug" if parent_id == "AST-791" else None,
        )
        monkeypatch.setattr(
            mod,
            "_resolve_recorded_at",
            lambda parent_id, dev_ref, ftr_ref: "2026-06-25T12:00:00+00:00",
        )

        entries = mod._collect_entries("origin/dev", "User Testing", landing_parent="  ")
        assert [entry["ticket_id"] for entry in entries] == ["AST-791"]

    def test_main_json_summary_includes_landing_parent(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mod = _load_rebuild_module()
        monkeypatch.setattr(
            mod,
            "_collect_entries",
            lambda dev_ref, uat_state_name, landing_parent=None: [
                {"ticket_id": "AST-801", "recorded_at": "2026-06-25T12:00:00+00:00"}
            ],
        )
        monkeypatch.setattr(mod, "rebuild_merge_ticket_log", MagicMock())
        monkeypatch.setattr(sys, "argv", ["rebuild_merge_ticket_log.py", "--landing-parent", "ast-801"])

        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code == 0

        summary = json.loads(capsys.readouterr().out)
        assert summary["landing_parent"] == "AST-801"
        assert summary["parents"] == ["AST-801"]
