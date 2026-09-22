"""Scrape-health metadata for Telescope responses (AST-1728). Never import src."""

from __future__ import annotations

from typing import Any, List, Union

# Fixed bot-challenge substrings — service-owned (import fence).
_BOT_MARKERS = (
    "cloudflare",
    "attention required",
    "just a moment",
    "captcha",
    "are you a robot",
    "verify you are human",
    "access denied",
    "unusual traffic",
    "enable javascript and cookies",
)


def _content_chars(text_or_html: Union[str, List[str], None]) -> int:
    if text_or_html is None:
        return 0
    if isinstance(text_or_html, list):
        return sum(len(t or "") for t in text_or_html)
    return len(text_or_html or "")


def build_scrape_meta(
    *,
    requested_url: str,
    final_url: str,
    text_or_html: Union[str, List[str], None],
    cookies_dismissed: bool,
) -> dict[str, Any]:
    """Additive scrape-health block on every scrape response."""
    chars = _content_chars(text_or_html)
    if isinstance(text_or_html, list):
        hay = "\n".join(t or "" for t in text_or_html).lower()
    else:
        hay = (text_or_html or "").lower()
    bot_blocked = any(m in hay for m in _BOT_MARKERS)
    issues: List[str] = []
    if bot_blocked:
        issues.append("bot_blocked")
    if chars == 0:
        issues.append("empty_content")
    elif chars < 80:
        issues.append("short_content")
    return {
        "bot_blocked": bot_blocked,
        "cookies_dismissed": bool(cookies_dismissed),
        "issues": issues,
        "content_chars": chars,
        # retained for operators; not required by bug-repro asserts
        "requested_url": requested_url or "",
        "final_url": final_url or "",
    }
