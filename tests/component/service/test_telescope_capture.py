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
async def test_ast1733_capture_text_selector_strips_style_script_noscript() -> None:
    """AST-1733 bug-repro: CSS selector path (e.g. head) must clone-and-strip style/script."""
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=["Page Title"])
    out = await capture_mod.capture_text(page, "head")
    assert out == "Page Title"
    call = page.evaluate.await_args
    js = call.args[0]
    # Pre-fix selector path is bare el.innerText — no clone / no style strip.
    assert "cloneNode" in js, (
        "AST-1733: selector capture_text must clone match roots before innerText"
    )
    assert "style, script, noscript" in js or (
        "style" in js and "script" in js and "noscript" in js
    ), (
        "AST-1733: selector path must remove style/script/noscript before innerText"
    )
    # Page/body chrome strip must not apply on intentional CSS selectors.
    assert "header, footer, nav" not in js, (
        "AST-1733: selector path must not strip header/footer/nav (page/body-only)"
    )
    assert len(call.args) > 1 and call.args[1] == "head"


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
async def test_ast1732_capture_links_scoped_to_selector() -> None:
    """AST-1732 bug-repro: filtering selector scopes links (not whole-page a[href])."""
    page = MagicMock()
    page.evaluate = AsyncMock(
        return_value=[{"href": "https://in.example/job", "text": "Job"}]
    )
    out = await capture_mod.capture_links(page, ".job-list")
    assert out == [{"href": "https://in.example/job", "text": "Job"}]
    call = page.evaluate.await_args
    js = call.args[0]
    whole_page_only = (
        "querySelectorAll('a[href]')" in js.replace('"', "'")
        and "querySelectorAll(sel" not in js
        and "querySelectorAll(selector" not in js
    )
    assert not whole_page_only, (
        "AST-1732: capture_links with selector must scope under match roots, "
        "not document.querySelectorAll('a[href]') alone"
    )
    has_sel_arg = len(call.args) > 1 and call.args[1] == ".job-list"
    assert has_sel_arg or "job-list" in js, (
        "AST-1732: scoped capture_links must receive the CSS selector"
    )


@pytest.mark.asyncio
async def test_ast1732_capture_links_multi_match_dedupes_by_href() -> None:
    """AST-1732 bug-repro: multi-root link union dedupes by href."""
    page = MagicMock()
    page.evaluate = AsyncMock(
        return_value=[{"href": "https://ex.com/a", "text": "first"}]
    )
    await capture_mod.capture_links(page, ".card")
    js = page.evaluate.await_args.args[0]
    assert any(
        tok in js
        for tok in ("seen", "Set(", "Map(", "dedup", "href] =", "by href", "unique")
    ), (
        "AST-1732: scoped multi-match links must dedupe by href in the evaluate script"
    )


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

def _bare_class_retry_in_script(script: str) -> bool:
    """True when evaluate JS retries a bare identifier as .{selector}."""
    return (
        "querySelectorAll" in script
        and (
            "'.'" in script
            or '"."' in script
            or "+ '.'" in script
            or '+ "."' in script
            or ".${" in script
            or "`.`" in script
        )
    )


@pytest.mark.asyncio
async def test_capture_html_bare_class_token_retries_as_class() -> None:
    """AST-1731 bug-repro: bare 'points-container' must match .class, not empty tag miss."""

    async def fake_evaluate(script: str, selector: str | None = None):
        # DOM: no <points-container> tag; class .points-container exists.
        if selector == "points-container":
            if _bare_class_retry_in_script(script):
                return ["<div class=\"points-container\">hit</div>"]
            if "querySelectorAll" in script:
                return []
            return ""
        if selector == ".points-container":
            if "querySelectorAll" in script:
                return ["<div class=\"points-container\">hit</div>"]
            return "<div class=\"points-container\">hit</div>"
        return ""

    page = MagicMock()
    page.evaluate = AsyncMock(side_effect=fake_evaluate)
    out = await capture_mod.capture_html(page, "points-container")
    assert out != "", "AST-1731: bare class token must not return empty HTML"
    if isinstance(out, list):
        assert "points-container" in out[0]
    else:
        assert "points-container" in out


@pytest.mark.asyncio
async def test_capture_html_multi_match_returns_list() -> None:
    """AST-1731 bug-repro: CSS class with 2+ hits → list[str] (not first-only string)."""

    async def fake_evaluate(script: str, selector: str | None = None):
        hits = [
            "<div class=\"job\">one</div>",
            "<div class=\"job\">two</div>",
        ]
        if "querySelectorAll" in script:
            return hits
        # Pre-fix querySelector path: first match only
        return hits[0]

    page = MagicMock()
    page.evaluate = AsyncMock(side_effect=fake_evaluate)
    out = await capture_mod.capture_html(page, ".job")
    assert isinstance(out, list), "AST-1731: multi-match html must be list[str]"
    assert out == [
        "<div class=\"job\">one</div>",
        "<div class=\"job\">two</div>",
    ]


@pytest.mark.asyncio
async def test_capture_text_bare_class_token_retries_as_class() -> None:
    """AST-1731: capture_text must apply the same bare→.class retry as capture_html."""

    async def fake_evaluate(script: str, selector: str | None = None):
        if selector == "points-container":
            if _bare_class_retry_in_script(script):
                return ["blob"]
            if "querySelectorAll" in script:
                return []
            return ""
        if selector == ".points-container":
            return ["blob"]
        return []

    page = MagicMock()
    page.evaluate = AsyncMock(side_effect=fake_evaluate)
    out = await capture_mod.capture_text(page, "points-container")
    assert out == "blob", (
        "AST-1731: bare class on capture_text must resolve like .points-container"
    )
