"""HTML cull parity helpers (AST-1232).

Prose authority: docs/features/surfer/ast-1232-parity-contract-and-server-cull-determinism.md
§ Parity contract (normative). Comparison/normalization only — does not cull.
"""

from __future__ import annotations

from html import unescape
from typing import Optional

from src.utils.config import ASTRAL_CONFIG

# HTML void elements — emit open form only when they appear in culled output.
_VOID_TAGS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


def assert_html_cull_anchor_config(html_cull: Optional[dict] = None) -> None:
    """Raise ValueError if html_cull cannot preserve anchors (AC3 preflight)."""
    cfg = html_cull if html_cull is not None else ASTRAL_CONFIG.get("html_cull")
    if not isinstance(cfg, dict):
        raise ValueError("html_cull config is missing or not a dict")
    if "allowed_tags" not in cfg:
        raise ValueError("html_cull['allowed_tags'] is missing")
    if "strip_attributes" not in cfg:
        raise ValueError("html_cull['strip_attributes'] is missing")
    allowed = cfg["allowed_tags"]
    strip_attrs = cfg["strip_attributes"]
    if "a" not in allowed:
        raise ValueError("html_cull['allowed_tags'] does not include 'a' — anchors cannot be preserved")
    if "href" in strip_attrs:
        raise ValueError("html_cull['strip_attributes'] includes 'href' — anchors cannot be preserved")


def extract_anchor_hrefs(html: str) -> list[str]:
    """Sorted unique hrefs per Parity contract § Anchor / job-URL preservation."""
    if not html or not isinstance(html, str):
        return []
    # Lazy import: same pattern as formatting.py HTML helpers.
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    for tag in soup.find_all("a", href=True):
        href = (tag.get("href") or "").strip()
        if not href or href == "#":
            continue
        if href.lower().startswith("javascript:"):
            continue
        seen.add(href)
    return sorted(seen)


def normalize_culled_html(html: str) -> str:
    """Canonical form per Parity contract § Normalization the comparison permits."""
    if not html or not isinstance(html, str):
        return ""
    from bs4 import BeautifulSoup, Comment, NavigableString, Tag

    # Explicit leading <body> must survive (client outerHTML mistake must fail parity).
    explicit_body = html.lstrip()[:5].lower() == "<body"

    soup = BeautifulSoup(html, "html.parser")

    def emit_text(text: str) -> str:
        # Decode entities to Unicode, then collapse whitespace.
        decoded = unescape(text)
        collapsed = " ".join(decoded.split())
        return collapsed

    def emit_attrs(tag: Tag) -> str:
        pairs = []
        for name, value in sorted(tag.attrs.items(), key=lambda kv: str(kv[0]).lower()):
            key = str(name).lower()
            if isinstance(value, list):
                raw = " ".join(str(v) for v in value)
            elif value is True or value is None:
                # Boolean / empty attr — emit key only as key=""
                raw = ""
            else:
                raw = str(value)
            raw = unescape(raw)
            escaped = (
                raw.replace("&", "&amp;")
                .replace('"', "&quot;")
                .replace("<", "&lt;")
            )
            pairs.append(f'{key}="{escaped}"')
        if not pairs:
            return ""
        return " " + " ".join(pairs)

    def emit_node(node) -> str:
        if isinstance(node, Comment):
            return ""
        if isinstance(node, NavigableString):
            return emit_text(str(node))
        if not isinstance(node, Tag):
            return ""
        name = (node.name or "").lower()
        if not name:
            return "".join(emit_node(c) for c in node.children)
        attrs = emit_attrs(node)
        if name in _VOID_TAGS:
            return f"<{name}{attrs}>"
        inner_parts = []
        for child in node.children:
            piece = emit_node(child)
            if piece:
                inner_parts.append(piece)
        # Drop whitespace-only segments between tags (already collapsed per text node).
        inner = "".join(inner_parts)
        return f"<{name}{attrs}>{inner}</{name}>"

    # Fragments: html.parser may wrap in <html><body>; unwrap only that invented shell.
    # Explicit <body> input: emit the body element itself (do not paper over outerHTML).
    parts = []
    if explicit_body:
        body = soup.find("body")
        if body is None:
            return ""
        return emit_node(body)
    body = soup.body
    if body is not None and soup.html is not None:
        roots = list(body.children)
    else:
        roots = list(soup.contents)
    for child in roots:
        piece = emit_node(child)
        if piece:
            parts.append(piece)
    return "".join(parts)


def culled_html_equivalent(a: str, b: str) -> bool:
    """True iff normalize_culled_html(a) == normalize_culled_html(b)."""
    return normalize_culled_html(a) == normalize_culled_html(b)
