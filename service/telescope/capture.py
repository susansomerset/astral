"""Page capture — text, links, raw HTML (no cull)."""

from __future__ import annotations

from typing import Dict, List, Union

# querySelectorAll; bare CSS ident with zero hits → retry as .{selector}.
_BARE_CLASS_RETRY = """
    const pick = (sel) => Array.from(document.querySelectorAll(sel));
    let nodes = pick(selector);
    if (nodes.length === 0 && /^[A-Za-z_][\\w-]*$/.test(selector)) {
        nodes = pick('.' + selector);
    }
"""

_QUERY_TEXT_JS = (
    """(selector) => {"""
    + _BARE_CLASS_RETRY
    + """
    return nodes.map(el => (el.innerText || '').trim());
}"""
)

_QUERY_HTML_JS = (
    """(selector) => {"""
    + _BARE_CLASS_RETRY
    + """
    return nodes.map(el => el.outerHTML);
}"""
)


def _fold_blobs(blobs) -> Union[str, List[str]]:
    # Evaluate always returns a list from our JS; tolerate a bare str from older mocks.
    if blobs is None or blobs == "" or blobs == []:
        return ""
    if isinstance(blobs, str):
        return blobs
    if len(blobs) == 1:
        return blobs[0]
    return list(blobs)


async def capture_text(page, selector: str | None) -> Union[str, List[str]]:
    sel = (selector or "").strip()
    if not sel or sel.lower() in ("page", "body"):
        return await page.evaluate(
            """() => {
                const body = document.body.cloneNode(true);
                body.querySelectorAll('header, footer, nav, [role="banner"], [role="contentinfo"]').forEach(el => el.remove());
                body.querySelectorAll('style, script, noscript').forEach(el => el.remove());
                body.querySelectorAll('[hidden], [aria-hidden="true"], .hide, .hidden, .d-none, .visually-hidden, .sr-only, [style*="display:none"], [style*="display: none"]').forEach(el => el.remove());
                return body.innerText;
            }"""
        )

    blobs = await page.evaluate(_QUERY_TEXT_JS, sel)
    return _fold_blobs(blobs)


async def capture_links(page) -> List[Dict[str, str]]:
    return await page.evaluate(
        """() => {
            const links = Array.from(document.querySelectorAll('a[href]'));
            return links
                .map(a => ({
                    href: a.href,
                    text: (a.innerText || '').trim(),
                }))
                .filter(item => item.href && item.href.startsWith('http'));
        }"""
    )


async def capture_html(page, selector: str | None) -> Union[str, List[str]]:
    sel = (selector or "").strip()
    # body / page / empty: leave specials alone (AST-1729 owns empty→document).
    if not sel or sel.lower() == "body":
        return await page.evaluate(
            "() => document.body ? document.body.outerHTML : ''"
        )
    if sel.lower() == "page":
        return await page.evaluate(
            "() => document.documentElement ? document.documentElement.outerHTML : ''"
        )
    blobs = await page.evaluate(_QUERY_HTML_JS, sel)
    return _fold_blobs(blobs)
