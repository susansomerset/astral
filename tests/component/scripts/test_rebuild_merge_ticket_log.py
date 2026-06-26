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


class TestRebuildMergeTicketLogTimestampResolution:
    """AST-811: per-parent recorded_at via grep chain + ftr land walk."""

    def test_resolve_recorded_at_prefers_prep_uat_grep(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mod = _load_rebuild_module()
        walk_called: list[str] = []

        def fake_grep(dev_ref: str, grep: str) -> str:
            if grep == "prep-uat(AST-716):":
                return "2026-06-18T02:08:22+00:00"
            return ""

        def fake_walk(dev_ref: str, ftr_ref: str) -> str:
            walk_called.append(ftr_ref)
            return "should-not-be-used"

        monkeypatch.setattr(mod, "_grep_land_timestamp", fake_grep)
        monkeypatch.setattr(mod, "_first_ftr_land_on_dev", fake_walk)

        recorded_at = mod._resolve_recorded_at(
            "AST-716",
            "origin/dev",
            "ftr/AST-716-find-job-page-logic-confirmation",
        )
        assert recorded_at == "2026-06-18T02:08:22+00:00"
        assert walk_called == []

    def test_resolve_recorded_at_ftr_land_grep_before_walk(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mod = _load_rebuild_module()
        ftr_ref = "ftr/AST-716-find-job-page-logic-confirmation"

        def fake_grep(dev_ref: str, grep: str) -> str:
            ritual = (
                "prep-uat(AST-716):",
                "merge-parent(AST-716):",
                "finish-up(AST-716):",
            )
            if grep in ritual:
                return ""
            if grep == f"merge origin/{ftr_ref}":
                return "2026-06-18T02:08:22Z"
            return ""

        monkeypatch.setattr(mod, "_grep_land_timestamp", fake_grep)
        monkeypatch.setattr(
            mod,
            "_first_ftr_land_on_dev",
            lambda dev_ref, ftr: pytest.fail("walk must not run when ftr grep hits"),
        )

        recorded_at = mod._resolve_recorded_at("AST-716", "origin/dev", ftr_ref)
        assert recorded_at == "2026-06-18T02:08:22Z"

    def test_collect_entries_distinct_recorded_at_when_walk_fallback(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mod = _load_rebuild_module()
        monkeypatch.setattr(
            mod,
            "fetch_user_testing_parent_ids",
            lambda uat_state_name: ["AST-716", "AST-752"],
        )
        monkeypatch.setattr(
            mod,
            "_resolve_ftr_ref",
            lambda parent_id, dev_ref: {
                "AST-716": "ftr/AST-716-find-job-page-logic-confirmation",
                "AST-752": "ftr/AST-752-agent-data-caller-content",
            }.get(parent_id),
        )
        monkeypatch.setattr(mod, "_grep_land_timestamp", lambda dev_ref, grep: "")
        monkeypatch.setattr(
            mod,
            "_first_ftr_land_on_dev",
            lambda dev_ref, ftr_ref: {
                "ftr/AST-716-find-job-page-logic-confirmation": "2026-06-18T02:08:22Z",
                "ftr/AST-752-agent-data-caller-content": "2026-06-23T20:17:09Z",
            }[ftr_ref],
        )

        entries = mod._collect_entries("origin/dev", "User Testing")
        by_id = {entry["ticket_id"]: entry["recorded_at"] for entry in entries}
        assert by_id["AST-716"] == "2026-06-18T02:08:22Z"
        assert by_id["AST-752"] == "2026-06-23T20:17:09Z"
        assert by_id["AST-716"] != by_id["AST-752"]

    def test_main_rebuild_summary_no_dev_head_timestamp_collapse(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mod = _load_rebuild_module()
        entries = [
            {"ticket_id": "AST-716", "recorded_at": "2026-06-18T02:08:22Z"},
            {"ticket_id": "AST-752", "recorded_at": "2026-06-23T20:17:09Z"},
        ]
        monkeypatch.setattr(
            mod,
            "_collect_entries",
            lambda dev_ref, uat_state_name, landing_parent=None: entries,
        )
        rebuild_mock = MagicMock()
        monkeypatch.setattr(mod, "rebuild_merge_ticket_log", rebuild_mock)
        monkeypatch.setattr(sys, "argv", ["rebuild_merge_ticket_log.py"])

        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code == 0

        rebuild_mock.assert_called_once_with(entries)
        timestamps = {entry["recorded_at"] for entry in entries}
        assert len(timestamps) == 2

        summary = json.loads(capsys.readouterr().out)
        assert summary["count"] == 2
        assert summary["parents"] == ["AST-716", "AST-752"]
