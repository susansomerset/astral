#!/usr/bin/env python3
"""
AST-422 Phase 1: reach heavybit.com/jobs, dismiss consent if present, capture visible + a11y + meta.

Usage (repo root, PYTHONPATH=.):
  python3 scripts/spikes/heavybit_board_phase1_reach.py [--headed] [--out-dir DIR] [--url URL]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

if "ASTRAL_DB_DIR" not in os.environ:
    os.environ["ASTRAL_DB_DIR"] = str(_ROOT / "data")

from playwright.async_api import Page

from src.external.playwright import create_browser_context

DEFAULT_URL = "https://www.heavybit.com/jobs"
DEFAULT_OUT = _ROOT / "debug/spikes/AST-422"
NAV_TIMEOUT_MS = 120_000
POST_LOAD_WAIT_MS = 2_000
CONSENT_ROLE_TIMEOUT_MS = 4_000
CONSENT_LOCATOR_TIMEOUT_MS = 3_000

_VISIBLE_JS = r"""
() => {
  const links = document.querySelectorAll('a[href*="/jobs/"], a[href*="job"]');
  let best = { n: 0, el: null };
  for (const div of document.querySelectorAll('div, section, main')) {
    const n = div.querySelectorAll('a[href*="/jobs/"], a[href*="job"]').length;
    if (n > best.n) best = { n, el: div };
  }
  if (best.el && best.n > 0) return best.el.innerText || '';
  const m = document.querySelector('main');
  if (m) return m.innerText || '';
  return document.body ? document.body.innerText || '' : '';
}
"""


def _playwright_version() -> str:
    try:
        from importlib.metadata import version

        return version("playwright")
    except Exception:
        return "unknown"


async def _dismiss_consent(page: Page) -> Optional[str]:
    try:
        loc = page.get_by_role(
            "button", name=re.compile(r"accept|agree|ok|allow", re.I)
        )
        if await loc.count() > 0:
            await loc.first.click(timeout=CONSENT_ROLE_TIMEOUT_MS)
            await page.wait_for_timeout(400)
            return "get_by_role_button_regex"
    except Exception:
        pass
    for sel in ('[id*="cookie" i] button', '[class*="consent" i] button'):
        try:
            lo = page.locator(sel).first
            if await lo.is_visible(timeout=1_500):
                await lo.click(timeout=CONSENT_LOCATOR_TIMEOUT_MS)
                await page.wait_for_timeout(400)
                return sel
        except Exception:
            continue
    return None


async def _write_captures(page: Page, out_dir: Path, meta: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        inner = await page.evaluate(_VISIBLE_JS)
        (out_dir / "visible.txt").write_text(inner or "", encoding="utf-8")
        meta["visible_text_length"] = len(inner or "")
    except Exception as e:
        meta["visible_text_error"] = repr(e)
    try:
        use_main = await page.locator("main").count() > 0
        loc = page.locator("main") if use_main else page.locator("body")
        snap = await loc.aria_snapshot()
        (out_dir / "a11y.json").write_text(
            json.dumps(
                {
                    "a11y_api": "locator.aria_snapshot",
                    "root": "main" if use_main else "body",
                    "aria_snapshot": snap,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception as e:
        meta["a11y_error"] = repr(e)


async def _run(url: str, out_dir: Path, headed: bool) -> None:
    meta: Dict[str, Any] = {
        "spike": "heavybit_board_phase1_reach",
        "linear_id": "AST-422",
        "target_url": url,
        "out_dir": str(out_dir.resolve()),
        "headless": not headed,
        "headed": headed,
        "wait_until": "networkidle",
        "nav_timeout_ms": NAV_TIMEOUT_MS,
        "playwright_version": _playwright_version(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": None,
        "final_url": None,
        "failure": None,
        "consent_dismissal": None,
    }
    async with create_browser_context(headless=not headed) as ctx:
        page = await ctx.new_page()
        try:
            response = await page.goto(
                url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS
            )
            if response is not None:
                meta["http_status"] = response.status
            meta["final_url"] = page.url
        except Exception as e:
            meta["failure"] = repr(e)
            meta["final_url"] = page.url
        await page.wait_for_timeout(POST_LOAD_WAIT_MS)
        meta["consent_dismissal"] = await _dismiss_consent(page)
        await page.wait_for_timeout(500)
        await _write_captures(page, out_dir, meta)
    meta["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--headed", action="store_true")
    args = p.parse_args()
    asyncio.run(_run(args.url, Path(args.out_dir), bool(args.headed)))


if __name__ == "__main__":
    main()
