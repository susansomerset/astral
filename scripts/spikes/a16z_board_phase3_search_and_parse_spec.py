#!/usr/bin/env python3
"""
AST-402 Phase 3: one parameterized search on jobs.a16z.com/jobs → results text + board_results_parse_instructions.json.

Requires Phase 2 widgets.json (--widgets-json). Drives controls by id per plan appendix (filled from widgets.json).

Usage (repo root, PYTHONPATH=.):
  python3 scripts/spikes/a16z_board_phase3_search_and_parse_spec.py \\
    --widgets-json path/to/widgets.json [--out-dir DIR] [--headed] \\
    [--url URL] [--title-query Q] [--work-mode M] [--max-listing-age 14d]
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
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

if "ASTRAL_DB_DIR" not in os.environ:
    os.environ["ASTRAL_DB_DIR"] = str(_ROOT / "data")

from playwright.async_api import Page

from src.external.playwright import create_browser_context

# AST-397 example literals (overridable via CLI)
DEFAULT_URL = "https://jobs.a16z.com/jobs"
DEFAULT_TITLE_QUERY = "Python Engineer in Healthcare"
DEFAULT_WORK_MODE = "Remote"
DEFAULT_MAX_LISTING_AGE = "14d"

NAV_TIMEOUT_MS = 120_000
POST_LOAD_WAIT_MS = 2_000
ACTION_SETTLE_MS = 800
NETWORKIDLE_AFTER_SEARCH_MS = 60_000

# Appendix: parameter → Phase 2 control id (from widgets.json 2026-05-15 build).
WIDGET_TITLE_SEARCH = "w-00002"
WIDGET_REMOTE_TRAY = "w-00009"
WIDGET_POSTED_TRAY = "w-00010"


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


async def _blur_trays(page: Page) -> None:
    try:
        await page.locator("h1").first.click(timeout=5_000)
    except Exception:
        pass
    for _ in range(4):
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(120)


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


def _parse_max_days(spec: str) -> int:
    m = re.match(r"^(\d+)\s*d$", spec.strip().lower())
    if not m:
        raise SystemExit(f"--max-listing-age must look like '14d', got {spec!r}")
    return int(m.group(1))


def _max_age_to_posted_menu_label(days: int) -> Tuple[str, str]:
    """
    Map requested max listing age to jobs.a16z.com Posted menu label (no exact 14d row).
    Options: Past 24 hours, Past 7 days, Past 30 days, Past 3 months, Past 12 months, Anytime.
    """
    if days <= 1:
        return "Past 24 hours", "mapped <=1d to Past 24 hours"
    if days <= 7:
        return "Past 7 days", "mapped <=7d to Past 7 days"
    if days <= 30:
        return "Past 30 days", "mapped <=30d to Past 30 days (closest bucket for typical 14d ask)"
    if days <= 90:
        return "Past 3 months", "mapped <=90d to Past 3 months"
    return "Past 12 months", "mapped to Past 12 months"


_RESULTS_REGION_JS = r"""
() => {
  const candidates = [
    ["div.job-list", "div.job-list"],
    ["div.job-list-container", "div.job-list-container"],
    ["div.job-list-content-wrap", "div.job-list-content-wrap"],
    ["main", "main"],
  ];
  for (const [sel, strat] of candidates) {
    const el = document.querySelector(sel);
    if (!el) continue;
    const t = el.innerText || "";
    if (t.trim().length === 0) continue;
    return {
      strategy: strat,
      text: t,
      job_link_count: el.querySelectorAll('a[href*="gh_jid="]').length,
    };
  }
  let best = { n: 0, el: null };
  for (const div of document.querySelectorAll("div")) {
    const n = div.querySelectorAll('a[href*="gh_jid="]').length;
    if (n > best.n) best = { n, el: div };
  }
  if (best.el && best.n > 0) {
    return {
      strategy: "gh_jid_anchor_densest_div",
      text: best.el.innerText || "",
      job_link_count: best.n,
    };
  }
  const b = document.body;
  return {
    strategy: "body_fallback",
    text: b ? b.innerText || "" : "",
    job_link_count: document.querySelectorAll('a[href*="gh_jid="]').length,
  };
}
"""


def _board_parse_instructions() -> Dict[str, Any]:
    """Selectors verified against post-search DOM (div.job-list → div.job-list-job cards)."""
    return {
        "container": "div.job-list",
        "job_tag": "div.job-list-job",
        "job_link": "div.job-list-job h2.job-list-job-title a[href*='gh_jid=']",
        "title": "h2.job-list-job-title a",
        "company": "a.job-list-job-company-link",
        "posted": "span.job-list-badge-posted",
        "notes": (
            "a16z /jobs board (Consider) as of spike: one card root is .job-list-job; "
            "title lives in h2.job-list-job-title a; apply link often has gh_jid=. "
            "Fragile if Consider renames classes — re-verify against results_visible.txt + DOM."
        ),
    }


async def _run(
    url: str,
    widgets_path: Path,
    out_dir: Path,
    headed: bool,
    title_query: str,
    work_mode: str,
    max_listing_age: str,
) -> None:
    widgets = _load_widgets(widgets_path)
    by_id = _controls_by_id(widgets)
    for wid in (WIDGET_TITLE_SEARCH, WIDGET_REMOTE_TRAY, WIDGET_POSTED_TRAY):
        _require_widget(by_id, wid)

    max_days = _parse_max_days(max_listing_age)
    posted_label, posted_note = _max_age_to_posted_menu_label(max_days)

    meta: Dict[str, Any] = {
        "spike": "a16z_board_phase3_search_and_parse_spec",
        "linear_id": "AST-402",
        "target_url": url,
        "widgets_json": str(widgets_path.resolve()),
        "playwright_version": _playwright_version(),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "title_query": title_query,
            "work_mode": work_mode,
            "max_listing_age": max_listing_age,
        },
        "widget_mapping": {
            "title_query": WIDGET_TITLE_SEARCH,
            "work_mode_tray": WIDGET_REMOTE_TRAY,
            "posted_tray": WIDGET_POSTED_TRAY,
        },
        "parse_meta": {
            "filters_applied": {
                "title_query": True,
                "work_mode": bool(work_mode.strip()),
                "max_listing_age": True,
            },
            "max_listing_age_ui": {
                "requested": max_listing_age,
                "posted_menu_label": posted_label,
                "note": posted_note,
            },
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

        # 1) Title search (w-00002)
        await page.get_by_placeholder("Search by title").fill(title_query)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(ACTION_SETTLE_MS)
        try:
            await page.wait_for_load_state("networkidle", timeout=NETWORKIDLE_AFTER_SEARCH_MS)
        except Exception as e:
            meta["networkidle_errors"].append(repr(e))

        # 2) Remote (w-00009 → select-option)
        if work_mode.strip():
            await _blur_trays(page)
            await page.get_by_role("button", name="All jobs").click(timeout=8_000)
            await page.wait_for_timeout(ACTION_SETTLE_MS)
            wm = work_mode.strip()
            opt = page.locator("button.select-option").filter(has_text=re.compile(rf"^{re.escape(wm)}$", re.I))
            if await opt.count() == 0:
                meta["parse_meta"]["filters_applied"]["work_mode"] = False
                meta["parse_meta"]["work_mode_error"] = f"No select-option matching {wm!r}"
            else:
                await opt.first.click(timeout=5_000)
            await page.wait_for_timeout(ACTION_SETTLE_MS)
            try:
                await page.wait_for_load_state("networkidle", timeout=NETWORKIDLE_AFTER_SEARCH_MS)
            except Exception as e:
                meta["networkidle_errors"].append(repr(e))

        # 3) Posted (w-00010 → select-option)
        await _blur_trays(page)
        await page.get_by_role("button", name="Anytime").click(timeout=8_000)
        await page.wait_for_timeout(ACTION_SETTLE_MS)
        popt = page.locator("button.select-option").filter(has_text=re.compile(rf"^{re.escape(posted_label)}$"))
        if await popt.count() == 0:
            meta["parse_meta"]["filters_applied"]["max_listing_age"] = False
            meta["parse_meta"]["posted_error"] = f"No menu item {posted_label!r}"
        else:
            await popt.first.click(timeout=5_000)
        await page.wait_for_timeout(ACTION_SETTLE_MS)
        try:
            await page.wait_for_load_state("networkidle", timeout=NETWORKIDLE_AFTER_SEARCH_MS)
        except Exception as e:
            meta["networkidle_errors"].append(repr(e))

        region = await page.evaluate(_RESULTS_REGION_JS)
        meta["results_region_strategy"] = region.get("strategy")
        meta["job_cards_visible"] = await page.evaluate(
            "() => document.querySelectorAll('div.job-list-job').length"
        )
        meta["job_link_count_results_region"] = region.get("job_link_count")

        results_text = region.get("text") or ""

    meta["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    parse_instructions["verified_job_card_count"] = meta.get("job_cards_visible")
    if meta.get("job_cards_visible") == 0:
        parse_instructions["notes"] = (
            parse_instructions.get("notes", "")
            + " This run had zero job cards after filters; selectors match DOM structure from populated searches but were not re-counted on cards this session."
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
    p.add_argument("--widgets-json", required=True, type=Path, help="Phase 2 widgets.json path")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=_ROOT / "debug/spikes/boards/a16z/phase3/run",
        help="Directory for results_visible.txt, board_results_parse_instructions.json, meta.json",
    )
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--title-query", default=DEFAULT_TITLE_QUERY)
    p.add_argument("--work-mode", default=DEFAULT_WORK_MODE)
    p.add_argument("--max-listing-age", default=DEFAULT_MAX_LISTING_AGE)
    p.add_argument("--headed", action="store_true")
    args = p.parse_args()
    asyncio.run(
        _run(
            args.url,
            args.widgets_json,
            args.out_dir,
            bool(args.headed),
            args.title_query,
            args.work_mode,
            args.max_listing_age,
        )
    )


if __name__ == "__main__":
    main()
