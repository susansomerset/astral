"""Page capture — text, links, raw HTML (no cull)."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Union

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

# Scoped links: same bare→.class retry as html/text (AST-1736), then collect under roots.
_QUERY_LINKS_JS = (
    """(selector) => {"""
    + _BARE_CLASS_RETRY
    + """
    const roots = nodes;
    const seen = new Set();
    const out = [];
    for (const root of roots) {
        for (const a of Array.from(root.querySelectorAll('a[href]'))) {
            const href = a.href;
            if (!href || !href.startsWith('http') || seen.has(href)) continue;
            seen.add(href);
            out.push({ href, text: (a.innerText || '').trim() });
        }
    }
    return out;
}"""
)

_CLASS_NAME_RE = re.compile(r"^[A-Za-z_][\w-]*$")
_TAG_RE = re.compile(r"^[A-Za-z][\w-]*$")


class CaptureQueryError(ValueError):
    """Ambiguous or invalid tag/class_name/selector filter (maps to HTTP 400)."""


def resolve_capture_query(
    *,
    selector: Optional[str] = None,
    tag: Optional[str] = None,
    class_name: Optional[str] = None,
) -> Optional[str]:
    """Build the CSS string for capture_* from selector and/or explicit tag/class.

    Returns None when nothing was set (whole-document / page defaults in capture_*).
    Raises CaptureQueryError on ambiguity or invalid tokens.
    """
    sel = (selector or "").strip()
    t = (tag or "").strip()
    cn = (class_name or "").strip()

    if sel and (t or cn):
        raise CaptureQueryError(
            "ambiguous filter: use selector or tag/class_name, not both"
        )

    if cn:
        if not _CLASS_NAME_RE.match(cn):
            raise CaptureQueryError("invalid class_name")
        if t:
            if not _TAG_RE.match(t):
                raise CaptureQueryError("invalid tag")
            return f"{t}.{cn}"
        return f".{cn}"

    if t:
        if not _TAG_RE.match(t):
            raise CaptureQueryError("invalid tag")
        return t

    return sel or None


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


async def capture_links(page, selector: str | None = None) -> List[Dict[str, str]]:
    sel = (selector or "").strip()
    # Whole-page (omit / page / body) — unchanged document-wide collect
    if not sel or sel.lower() in ("page", "body"):
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
    # Scoped: bare→.class retry (AST-1736) + union under roots, dedupe by href (AST-1732)
    return await page.evaluate(_QUERY_LINKS_JS, sel)


async def capture_html(page, selector: str | None) -> Union[str, List[str]]:
    sel = (selector or "").strip()
    # Omitted / "page" → full document (AST-1729); explicit "body" stays body-only.
    if not sel or sel.lower() == "page":
        return await page.evaluate(
            "() => document.documentElement ? document.documentElement.outerHTML : ''"
        )
    if sel.lower() == "body":
        return await page.evaluate(
            "() => document.body ? document.body.outerHTML : ''"
        )
    # CSS path only: bare-class retry + multi-match list (AST-1731).
    blobs = await page.evaluate(_QUERY_HTML_JS, sel)
    return _fold_blobs(blobs)
