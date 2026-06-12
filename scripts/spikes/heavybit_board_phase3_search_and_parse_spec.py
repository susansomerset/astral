#!/usr/bin/env python3
"""
AST-424 Phase 3: one parameterized search on heavybit.com/jobs → results text + board_results_parse_instructions.json.

Requires Phase 2 widgets.json (--widgets-json). Heavybit Phase 2 had no filter trays — title search only (w-00002).

Usage (repo root, PYTHONPATH=.):
  python3 scripts/spikes/heavybit_board_phase3_search_and_parse_spec.py \\
    --widgets-json path/to/widgets.json [--out-dir DIR] [--headed] [--url URL] [--title-query Q]
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
DEFAULT_TITLE_QUERY = "Engineer"
DEFAULT_WIDGETS_JSON = _ROOT / "debug/spikes/AST-423/widgets.json"

NAV_TIMEOUT_MS = 120_000
POST_LOAD_WAIT_MS = 2_000
ACTION_SETTLE_MS = 800
NETWORKIDLE_AFTER_SEARCH_MS = 60_000

WIDGET_TITLE_SEARCH = "w-00002"
TITLE_PLACEHOLDER = "SEARCH FOR TITLES, THEMES, KEYWORDS..."


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
            await loc.first.click(timeout=4_000)
            await page.wait_for_timeout(400)
            return "get_by_role_button_regex"
    except Exception:
        pass
    for sel in ('[id*="cookie" i] button', '[class*="consent" i] button'):
        try:
            lo = page.locator(sel).first
            if await lo.is_visible(timeout=1_500):
                await lo.click(timeout=3_000)
                await page.wait_for_timeout(400)
                return sel
        except Exception:
            continue
    return None


def _load_widgets(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("controls"), list):
        raise SystemExit("widgets.json: missing controls array")
    return data


def _controls_by_id(widgets: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for c in widgets["controls"]:
        cid = c.get("id")
        if cid:
            out[cid] = c
    return out


def _require_widget(by_id: Dict[str, Dict[str, Any]], wid: str) -> None:
    if wid not in by_id:
        raise SystemExit(
            f"widgets.json missing control {wid!r}; regenerate Phase 2 or fix appendix."
        )


_RESULTS_REGION_JS = r"""
() => {
  const triggers = document.querySelectorAll('[id^="collapsible-trigger-"]');
  if (triggers.length > 0) {
    let best = null;
    let bestN = 0;
    for (const el of document.querySelectorAll("section, main, div")) {
      const n = el.querySelectorAll('[id^="collapsible-trigger-"]').length;
      if (n > bestN) {
        bestN = n;
        best = el;
      }
    }
    if (best && bestN > 0) {
      return {
        strategy: "collapsible_trigger_densest_section",
        text: best.innerText || "",
        job_link_count: bestN,
      };
    }
  }
  const main = document.querySelector("main");
  if (main) {
    const t = main.innerText || "";
    if (t.trim()) {
      return {
        strategy: "main",
        text: t,
        job_link_count: document.querySelectorAll('[id^="collapsible-trigger-"]').length,
      };
    }
  }
  const b = document.body;
  return {
    strategy: "body_fallback",
    text: b ? b.innerText || "" : "",
    job_link_count: document.querySelectorAll('[id^="collapsible-trigger-"]').length,
  };
}
"""


def _board_parse_instructions() -> Dict[str, Any]:
    return {
        "container": "main",
        "job_tag": '[id^="collapsible-trigger-"]',
        "job_link": '[id^="collapsible-trigger-"]',
        "title": '[id^="collapsible-trigger-"]',
        "company": '[id^="collapsible-trigger-"]',
        "posted": "",
        "notes": (
            "Heavybit /jobs: job rows are collapsible triggers; "
            "title/company/location in trigger visible_text. Phase 2 had no filter trays."
        ),
    }


async def _run(
    url: str,
    widgets_path: Path,
    out_dir: Path,
    headed: bool,
    title_query: str,
) -> None:
    widgets = _load_widgets(widgets_path)
    by_id = _controls_by_id(widgets)
    _require_widget(by_id, WIDGET_TITLE_SEARCH)

    meta: Dict[str, Any] = {
        "spike": "heavybit_board_phase3_search_and_parse_spec",
        "linear_id": "AST-424",
        "entry_url": url,
        "target_url": url,
        "widgets_json": str(widgets_path.resolve()),
        "playwright_version": _playwright_version(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": {"title_query": title_query},
        "widget_mapping": {"title_query": WIDGET_TITLE_SEARCH},
        "filters_applied": {
            "title_query": True,
            "note": "title-only; Phase 2 had no block_tray_option_lists",
        },
        "consent_dismissal": None,
        "networkidle_errors": [],
    }

    parse_instructions = _board_parse_instructions()
    parse_instructions["parse_meta_crossref"] = (
        "Written from static DOM inspection; card count in meta confirms selectors."
    )

    async with create_browser_context(headless=not headed) as ctx:
        page = await ctx.new_page()
        await page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
        await page.wait_for_timeout(POST_LOAD_WAIT_MS)
        meta["consent_dismissal"] = await _dismiss_consent(page)
        await page.wait_for_timeout(400)

        await page.get_by_placeholder(TITLE_PLACEHOLDER).fill(title_query)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(ACTION_SETTLE_MS)
        try:
            await page.wait_for_load_state("networkidle", timeout=NETWORKIDLE_AFTER_SEARCH_MS)
        except Exception as e:
            meta["networkidle_errors"].append(repr(e))

        region = await page.evaluate(_RESULTS_REGION_JS)
        meta["results_region_strategy"] = region.get("strategy")
        meta["job_cards_visible"] = await page.evaluate(
            '() => document.querySelectorAll(\'[id^="collapsible-trigger-"]\').length'
        )
        meta["job_link_count_results_region"] = region.get("job_link_count")
        results_text = region.get("text") or ""

    meta["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    parse_instructions["verified_job_card_count"] = meta.get("job_cards_visible")
    if meta.get("job_cards_visible") == 0:
        parse_instructions["notes"] = (
            parse_instructions.get("notes", "")
            + " Zero collapsible job rows after title search; re-verify selectors."
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results_visible.txt").write_text(results_text, encoding="utf-8")
    (out_dir / "board_results_parse_instructions.json").write_text(
        json.dumps(parse_instructions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--widgets-json",
        type=Path,
        default=DEFAULT_WIDGETS_JSON,
        help="Phase 2 widgets.json path",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=_ROOT / "debug/spikes/AST-424",
        help="Directory for results_visible.txt, board_results_parse_instructions.json, meta.json",
    )
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--title-query", default=DEFAULT_TITLE_QUERY)
    p.add_argument("--headed", action="store_true")
    args = p.parse_args()
    if not args.widgets_json.is_file():
        raise SystemExit(f"widgets.json not found: {args.widgets_json}")
    asyncio.run(
        _run(
            args.url,
            args.widgets_json,
            args.out_dir,
            bool(args.headed),
            args.title_query,
        )
    )


if __name__ == "__main__":
    main()
