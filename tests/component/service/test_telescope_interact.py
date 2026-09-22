"""Telescope interact helpers — expand_page soft-fail on navigation."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.asyncio
async def test_expand_page_soft_fails_when_execution_context_destroyed() -> None:
    from interact import expand_page

    page = MagicMock()
    page.wait_for_timeout = AsyncMock()
    page.evaluate = AsyncMock(
        side_effect=Exception(
            "Page.evaluate: Execution context was destroyed, most likely because of a navigation"
        )
    )
    page.query_selector = AsyncMock(return_value=None)

    await expand_page(page)

    page.query_selector.assert_not_called()
