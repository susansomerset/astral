"""run_board_search_gaze: deeplink bypasses interactive gate (AST-487); criteria + interactive unchanged."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Tuple
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import boards as boards_mod

# Board is interactive for criteria path, but deeplink rows must still navigate (AST-487).
_CFG_INTERACTIVE: Dict[str, Dict[str, Any]] = {
    "iboard": {
        "label": "Interactive board",
        "entry_url": "https://boards.example/start",
        "adopted": True,
        "scrape_mode": "interactive",
        "parse_instructions": {},
        "title_patterns": [],
    }
}


def _row_deeplink(url: str) -> Dict[str, Any]:
    return {
        "board_search_id": "bs-z",
        "candidate_id": "cand-x",
        "board_key": "iboard",
        "search_mode": "deeplink",
        "deeplink_url": url,
        "criteria": {},
    }


@pytest.mark.asyncio
async def test_deeplink_on_interactive_profile_calls_stored_url_with_none_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deeplink mode uses board_search_deeplink(page, url, None) before scrape_mode would block."""
    monkeypatch.setattr(boards_mod, "BOARD_CONFIG", _CFG_INTERACTIVE)
    captured: List[Tuple[str, Any]] = []

    async def _deeplink(page: Any, url: str, qp: Any) -> Tuple[str, Dict[str, Any]]:
        captured.append((url, qp))
        return "<html><div class='x'>job</div></html>", {}

    monkeypatch.setattr("src.external.playwright.check_connectivity", AsyncMock(return_value=True))
    monkeypatch.setattr("src.external.playwright.board_search_deeplink", _deeplink)
    page = AsyncMock()
    page.close = AsyncMock()

    @asynccontextmanager
    async def _browser() -> Any:
        yield MagicMock()

    monkeypatch.setattr("src.external.playwright.create_browser_context", _browser)
    monkeypatch.setattr("src.external.playwright.get_page", AsyncMock(return_value=page))
    monkeypatch.setattr(
        "src.core.tracker.ingest_board_listings",
        MagicMock(return_value={"new": 1, "duplicates": 0, "invalid_title": 0}),
    )
    monkeypatch.setattr("src.core.gazer._compiled_title_patterns", MagicMock(return_value=None))

    want = "https://boards.example/user-saved?q=1"
    out = await boards_mod.run_board_search_gaze("batch-a", _row_deeplink(want), ctx={})
    assert captured == [(want, None)]
    assert out["status"] == "success"
    assert out["new"] == 1
    page.close.assert_awaited()


@pytest.mark.asyncio
async def test_deeplink_empty_url_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(boards_mod, "BOARD_CONFIG", _CFG_INTERACTIVE)
    with pytest.raises(ValueError, match="non-empty deeplink_url"):
        await boards_mod.run_board_search_gaze("batch-a", _row_deeplink("   "), ctx={})


@pytest.mark.asyncio
async def test_criteria_interactive_still_raises_not_implemented(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(boards_mod, "BOARD_CONFIG", _CFG_INTERACTIVE)
    row = {
        "board_search_id": "bs-z",
        "candidate_id": "cand-x",
        "board_key": "iboard",
        "search_mode": "criteria",
        "criteria": {},
    }
    with pytest.raises(NotImplementedError, match="interactive gaze_board"):
        await boards_mod.run_board_search_gaze("batch-a", row, ctx={})
