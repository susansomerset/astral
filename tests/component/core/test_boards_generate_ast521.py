"""AST-521 — run_board_search_generation writes user- prefixed dispatch_ledger rows."""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from src.core import boards as boards_mod

_ROW = {"board_search_id": "bs-1", "candidate_id": "somerset", "board_key": "linkedin"}


class TestRunBoardSearchGenerationAst521:
    @pytest.fixture
    def ledger_trackers(self, monkeypatch: pytest.MonkeyPatch) -> Dict[str, Any]:
        saves: List[Any] = []
        updates: List[Any] = []
        monkeypatch.setattr(boards_mod, "TASK_CONFIG", {"craft_board_search_criteria": {}})
        monkeypatch.setattr(boards_mod, "get_board_search", lambda board_search_id: dict(_ROW))
        monkeypatch.setattr(
            boards_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id},
        )
        monkeypatch.setattr(
            boards_mod.database,
            "save_dispatch_ledger",
            lambda *args, **kwargs: saves.append((args, kwargs)),
        )
        monkeypatch.setattr(
            boards_mod.database,
            "update_dispatch_ledger",
            lambda batch_id, **kwargs: updates.append((batch_id, kwargs)),
        )
        monkeypatch.setattr(boards_mod, "compute_batch_cost", lambda batch_id: 0.5)
        monkeypatch.setattr(
            boards_mod.uuid,
            "uuid4",
            lambda: __import__("uuid").UUID("00000000-0000-0000-0000-000000000003"),
        )
        return {"saves": saves, "updates": updates}

    def test_success_uses_user_prefixed_ledger_task_key(
        self, monkeypatch: pytest.MonkeyPatch, ledger_trackers: Dict[str, Any]
    ) -> None:
        monkeypatch.setattr(
            boards_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": {"label": "ok"}})),
        )
        body, status = boards_mod.run_board_search_generation(
            "bs-1", "craft_board_search_criteria", None
        )
        assert status == 200
        assert body["batch_id"] == "user-craft_board_search_criteria-00000000-0000-0000-0000-000000000003"
        assert ledger_trackers["saves"][0][0][1] == "user-craft_board_search_criteria"
        assert ledger_trackers["updates"][-1][1]["status"] == "COMPLETED"

    def test_failure_marks_ledger_failed_with_user_prefix(
        self, monkeypatch: pytest.MonkeyPatch, ledger_trackers: Dict[str, Any]
    ) -> None:
        monkeypatch.setattr(
            boards_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": False, "error": "nope"})),
        )
        body, status = boards_mod.run_board_search_generation(
            "bs-1", "craft_board_search_criteria", None
        )
        assert status == 500
        assert body["batch_id"].startswith("user-craft_board_search_criteria-")
        assert ledger_trackers["saves"][0][0][1] == "user-craft_board_search_criteria"
        assert ledger_trackers["updates"][-1][1]["status"] == "FAILED"
        assert ledger_trackers["updates"][-1][1]["total_failed"] == 1

    def test_missing_board_search_skips_ledger(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(boards_mod, "TASK_CONFIG", {"craft_board_search_criteria": {}})
        monkeypatch.setattr(boards_mod, "get_board_search", lambda board_search_id: None)
        monkeypatch.setattr(boards_mod.database, "save_dispatch_ledger", save)
        body, status = boards_mod.run_board_search_generation(
            "missing", "craft_board_search_criteria", None
        )
        assert status == 404
        save.assert_not_called()
