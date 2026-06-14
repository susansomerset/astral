"""Component tests for src/core/boards.py — gaze path (AST-459)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import boards as boards_mod

_GAZE_DEMO_BOARD: Dict[str, Any] = {
    "tst": {
        "label": "Test board",
        "entry_url": "https://boards.example/start",
        "adopted": True,
        "craft_task_key": "craft_board_search_criteria",
        "scrape_mode": "deep_link",
        "parse_instructions": {"job_title": "h2", "job_link": "http"},
        "criteria_param_map": {},
        "title_patterns": [],
    },
}


@pytest.fixture
def gaze_mocks(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(boards_mod, "BOARD_CONFIG", _GAZE_DEMO_BOARD)
    monkeypatch.setattr(
        "src.external.playwright.check_connectivity", AsyncMock(return_value=True)
    )
    deeplink = AsyncMock(return_value=("<html><a href='#'>Title</a></html>", {}))
    monkeypatch.setattr("src.external.playwright.board_search_deeplink", deeplink)
    page = AsyncMock()
    page.close = AsyncMock()

    @asynccontextmanager
    async def _browser():
        yield MagicMock()

    monkeypatch.setattr("src.external.playwright.create_browser_context", _browser)
    monkeypatch.setattr("src.external.playwright.get_page", AsyncMock(return_value=page))
    ingest = MagicMock(return_value={"new": 1, "invalid_title": 0})
    monkeypatch.setattr("src.core.tracker.ingest_board_listings", ingest)
    yield {"deeplink": deeplink, "ingest": ingest, "page": page}


class TestRunBoardSearchGazeAst459:
    """Criteria qp from row; deeplink mode navigates stored deeplink_url (AST-459)."""

    @pytest.mark.asyncio
    async def test_deeplink_row_uses_stored_deeplink_url(self, gaze_mocks: dict[str, Any]) -> None:
        deeplink_fn = gaze_mocks["deeplink"]
        row = {
            "board_search_id": "bs-d",
            "candidate_id": "c1",
            "board_key": "tst",
            "search_mode": "deeplink",
            "deeplink_url": "https://boards.example/saved?view=all",
            "criteria": {},
        }
        await boards_mod.run_board_search_gaze("batch-bd", row, ctx=None)
        deeplink_fn.assert_awaited_once()
        _, url, qp = deeplink_fn.await_args.args
        assert url == "https://boards.example/saved?view=all"
        assert qp is None

    @pytest.mark.asyncio
    async def test_criteria_mode_builds_query_params_from_criteria_keys(
        self, gaze_mocks: dict[str, Any]
    ) -> None:
        deeplink_fn = gaze_mocks["deeplink"]
        row = {
            "board_search_id": "bs-c",
            "candidate_id": "c1",
            "board_key": "tst",
            "search_mode": "criteria",
            "deeplink_url": None,
            "criteria": {
                "title_query": "Rust",
                "work_mode": "remote",
                "extra_ignored": "x",
            },
        }
        await boards_mod.run_board_search_gaze("batch-bc", row, ctx=None)
        deeplink_fn.assert_awaited_once()
        _, url, qp = deeplink_fn.await_args.args
        assert url == "https://boards.example/start"
        assert qp == {"title_query": "Rust", "work_mode": "remote"}

    @pytest.mark.asyncio
    async def test_deeplink_blank_url_raises(self, gaze_mocks: dict[str, Any]) -> None:
        deeplink_fn = gaze_mocks["deeplink"]
        row = {
            "board_search_id": "bs-bad",
            "candidate_id": "c1",
            "board_key": "tst",
            "search_mode": "deeplink",
            "deeplink_url": "   ",
            "criteria": {},
        }
        with pytest.raises(ValueError, match="non-empty deeplink_url"):
            await boards_mod.run_board_search_gaze("batch-bad", row, ctx=None)
        deeplink_fn.assert_not_awaited()
