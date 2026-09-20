"""AST-1725 — capture_text / capture_html / capture_links (no real browser)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("fastapi")

import capture as capture_mod  # noqa: E402  # path set in service conftest


@pytest.mark.asyncio
async def test_capture_text_body_selector_uses_visible_text_js() -> None:
    page = MagicMock()
    page.evaluate = AsyncMock(return_value="visible body")
    out = await capture_mod.capture_text(page, None)
    assert out == "visible body"
    page.evaluate.assert_awaited_once()
    js = page.evaluate.await_args.args[0]
    assert "cloneNode" in js
    assert "header, footer, nav" in js


@pytest.mark.asyncio
async def test_capture_text_multi_match_returns_list() -> None:
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=["one", "two", "three"])
    out = await capture_mod.capture_text(page, ".job")
    assert out == ["one", "two", "three"]


@pytest.mark.asyncio
async def test_capture_text_single_match_returns_string() -> None:
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=["only"])
    out = await capture_mod.capture_text(page, ".job")
    assert out == "only"


@pytest.mark.asyncio
async def test_capture_text_zero_matches_returns_empty_string() -> None:
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=[])
    out = await capture_mod.capture_text(page, ".missing")
    assert out == ""


@pytest.mark.asyncio
async def test_capture_links_filters_http() -> None:
    page = MagicMock()
    page.evaluate = AsyncMock(
        return_value=[{"href": "https://ex.com/a", "text": "A"}]
    )
    out = await capture_mod.capture_links(page)
    assert out == [{"href": "https://ex.com/a", "text": "A"}]


@pytest.mark.asyncio
async def test_capture_html_page_vs_body_vs_selector() -> None:
    page = MagicMock()
    page.evaluate = AsyncMock(side_effect=["<html/>", "<body/>", "<div/>"])
    assert await capture_mod.capture_html(page, "page") == "<html/>"
    assert await capture_mod.capture_html(page, "body") == "<body/>"
    assert await capture_mod.capture_html(page, "#main") == "<div/>"


@pytest.mark.asyncio
async def test_capture_html_omitted_selector_uses_document_element() -> None:
    """AST-1729 bug-repro: None/'' default to full document (same as 'page'), not body."""
    for selector in (None, ""):
        page = MagicMock()
        page.evaluate = AsyncMock(return_value="<html><head></head><body>x</body></html>")
        out = await capture_mod.capture_html(page, selector)
        assert out.startswith("<html"), f"selector={selector!r} should return full document"
        js = page.evaluate.await_args.args[0]
        assert "documentElement" in js, (
            f"AST-1729: omitted selector ({selector!r}) must evaluate documentElement, not body"
        )
        assert "document.body ? document.body.outerHTML" not in js
