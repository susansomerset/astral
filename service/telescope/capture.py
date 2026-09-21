"""Page capture — text, links, raw HTML (no cull)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union

# querySelectorAll; bare CSS ident with zero hits → retry as .{selector}.
_BARE_CLASS_RETRY = """
    const pick = (sel) => Array.from(document.querySelectorAll(sel));
    let nodes = pick(selector);
    if (nodes.length === 0 && /^[A-Za-z_][\\w-]*$/.test(selector)) {
        nodes = pick('.' + selector);
    }
"""

# Selector path: clone each match, strip style/script/noscript + hidden (AST-1733).
# Do not strip header/footer/nav — those chrome removals are page/body-only.
_QUERY_TEXT_JS = (
    """(selector) => {"""
    + _BARE_CLASS_RETRY
    + """
    return nodes.map(el => {
        const root = el.cloneNode(true);
        root.querySelectorAll('style, script, noscript').forEach(n => n.remove());
        root.querySelectorAll('[hidden], [aria-hidden="true"], .hide, .hidden, .d-none, .visually-hidden, .sr-only, [style*="display:none"], [style*="display: none"]').forEach(n => n.remove());
        return (root.innerText || '').trim();
    });
}"""
)

_QUERY_HTML_JS = (
    """(selector) => {"""
    + _BARE_CLASS_RETRY
    + """
    return nodes.map(el => el.outerHTML);
}"""
)

# Scoped links: bare→.class retry (AST-1736); emit every http(s) anchor under roots.
# Href merge + text[] lives in `_dedupe_links_by_href` (AST-1747), not first-wins JS.
_QUERY_LINKS_JS = (
    """(selector) => {"""
    + _BARE_CLASS_RETRY
    + """
    const out = [];
    for (const root of nodes) {
        for (const a of Array.from(root.querySelectorAll('a[href]'))) {
            const href = a.href;
            if (!href || !href.startsWith('http')) continue;
            out.push({ href, text: (a.innerText || '').trim() });
        }
    }
    return out;
}"""
)

_CLASS_NAME_RE = re.compile(r"^[A-Za-z_][\w-]*$")
_TAG_RE = re.compile(r"^[A-Za-z][\w-]*$")


class CaptureQueryError(ValueError):
    """Ambiguous or invalid tag/class_name/id/selector filter (maps to HTTP 400)."""


def resolve_capture_query(
    *,
    selector: Optional[str] = None,
    tag: Optional[str] = None,
    class_name: Optional[str] = None,
    id: Optional[str] = None,
) -> Optional[str]:
    """Build CSS for capture_* from unified tag/selector + optional class/id.

    ``tag`` and ``selector`` are the same primary slot (AST-1744). ``class_name``
    and ``id`` are secondary filters (AST-1746 for id).
    """
    sel = (selector or "").strip()
    t = (tag or "").strip()
    cn = (class_name or "").strip()
    eid = (id or "").strip()

    # Primary = unified tag/selector aliases
    if sel and t and sel != t:
        raise CaptureQueryError("ambiguous primary: tag and selector differ")
    primary = t or sel or ""

    # Explicit id → CSS #id (optionally with tag / class_name); no bare→# retry.
    if eid:
        if not _CLASS_NAME_RE.match(eid):
            raise CaptureQueryError("invalid id")
        if cn and not _CLASS_NAME_RE.match(cn):
            raise CaptureQueryError("invalid class_name")
        if primary:
            if not _TAG_RE.match(primary):
                raise CaptureQueryError(
                    "id only combines with a bare tag primary (or alone)"
                )
            if cn:
                return f"{primary}.{cn}#{eid}"
            return f"{primary}#{eid}"
        if cn:
            return f".{cn}#{eid}"
        return f"#{eid}"

    if cn:
        if not _CLASS_NAME_RE.match(cn):
            raise CaptureQueryError("invalid class_name")
        # page/body specials do not apply when class filters — class-only CSS
        if not primary or primary.lower() in ("page", "body"):
            return f".{cn}"
        if not _TAG_RE.match(primary):
            raise CaptureQueryError(
                "class_name only combines with a bare tag primary (or alone)"
            )
        return f"{primary}.{cn}"

    if primary:
        # Explicit tag path validates; selector-only may be full CSS / page / body
        if t and not _TAG_RE.match(primary):
            raise CaptureQueryError("invalid tag")
        return primary

    return None



def _fold_blobs(blobs) -> Union[str, List[str]]:
    # Evaluate always returns a list from our JS; tolerate a bare str from older mocks.
    if blobs is None or blobs == "" or blobs == []:
        return ""
    if isinstance(blobs, str):
        return blobs
    if len(blobs) == 1:
        return blobs[0]
    return list(blobs)


def _dedupe_links_by_href(raw: Optional[List]) -> List[Dict[str, Any]]:
    """One object per href; `text` is a deduped list[str] in first-seen order (AST-1747)."""
    if not raw:
        return []
    out: List[Dict[str, Any]] = []
    by_href: Dict[str, Dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        href = item.get("href")
        if not href or not isinstance(href, str):
            continue
        if href not in by_href:
            entry: Dict[str, Any] = {"href": href, "text": []}
            by_href[href] = entry
            out.append(entry)
        label = item.get("text")
        if not isinstance(label, str):
            continue
        text = label.strip()
        texts: List[str] = by_href[href]["text"]
        if text not in texts:
            texts.append(text)
    return out


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


async def capture_links(page, selector: str | None = None) -> List[Dict[str, Any]]:
    sel = (selector or "").strip()
    # Whole-document only for omit / "page"; explicit "body"/"head" are element-scoped (AST-1735)
    if not sel or sel.lower() == "page":
        raw = await page.evaluate(
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
        return _dedupe_links_by_href(raw)
    # Scoped: bare→.class (AST-1736) + union under roots; fold href/text[] (AST-1747)
    raw = await page.evaluate(_QUERY_LINKS_JS, sel)
    return _dedupe_links_by_href(raw)


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
