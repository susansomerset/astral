"""Page capture — text, links, raw HTML (no cull)."""

from __future__ import annotations

from typing import Dict, List, Union


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

    blobs = await page.evaluate(
        """(selector) => {
            const nodes = Array.from(document.querySelectorAll(selector));
            return nodes.map(el => (el.innerText || '').trim());
        }""",
        sel,
    )
    if not blobs:
        return ""
    if len(blobs) == 1:
        return blobs[0]
    return list(blobs)


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
    # Scoped: union under match roots, dedupe by href (first text wins)
    return await page.evaluate(
        """(selector) => {
            const roots = Array.from(document.querySelectorAll(selector));
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
        }""",
        sel,
    )


async def capture_html(page, selector: str | None) -> str:
    sel = (selector or "").strip()
    # Omitted / "page" → full document (AST-1729); explicit "body" stays body-only
    if not sel or sel.lower() == "page":
        return await page.evaluate(
            "() => document.documentElement ? document.documentElement.outerHTML : ''"
        )
    if sel.lower() == "body":
        return await page.evaluate(
            "() => document.body ? document.body.outerHTML : ''"
        )
    return await page.evaluate(
        """(selector) => {
            const el = document.querySelector(selector);
            return el ? el.outerHTML : '';
        }""",
        sel,
    )
