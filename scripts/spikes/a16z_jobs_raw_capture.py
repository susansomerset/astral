#!/usr/bin/env python3
"""
AST-398: Playwright capture of jobs.a16z.com → findings_raw.json (schema v1 in plan doc).

Runbook (local, gitignored): debug/spikes/older/a16z-jobs-spike-ast-398-notes.md

Usage (repo root, PYTHONPATH=.):
  python3 scripts/spikes/a16z_jobs_raw_capture.py [--headed] [--dry-run]
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

# Repo root on sys.path (matches other scripts/)
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Importing src.external.playwright loads config.py, which requires ASTRAL_DB_DIR.
if "ASTRAL_DB_DIR" not in os.environ:
    os.environ["ASTRAL_DB_DIR"] = str(_ROOT / "data")

from playwright.async_api import Page

from src.external.playwright import create_browser_context

# Default matches AST-397 example parameters (resolved board URL).
DEFAULT_SOURCE = "https://jobs.a16z.com/our-jobs"
DEFAULT_TITLE_QUERY = "Python Engineer in Healthcare"
DEFAULT_WORK_MODE = "Remote"
DEFAULT_MAX_AGE = "14d"

POSTED_RE = re.compile(
    r"Posted\s+(\d+)\s*(hour|hours|day|days|week|weeks)\s+ago",
    re.IGNORECASE,
)


def _playwright_version() -> str:
    try:
        from importlib.metadata import version

        return version("playwright")
    except Exception:
        return "unknown"


def _parse_max_listing_days(spec: str) -> int:
    spec = spec.strip().lower()
    m = re.match(r"^(\d+)\s*d$", spec)
    if not m:
        raise ValueError(f"max_listing_age must look like '14d', got {spec!r}")
    return int(m.group(1))


def _posted_to_freshness_days(n: int, unit: str) -> int:
    u = unit.lower()
    if u.startswith("hour"):
        return 0
    if u.startswith("day"):
        return n
    if u.startswith("week"):
        return n * 7
    return n


def _row_matches_title(blob: str, title_query: str) -> bool:
    """Board cards omit wording; match_parent spike params from AST-397."""
    lower = blob.lower()
    q = title_query.lower()
    if "python" not in lower:
        return False
    if "health" in q or "healthcare" in q:
        if "health" not in lower and "healthcare" not in lower:
            return False
    for needle in ("engineer", "developer"):
        if needle in q and needle not in lower:
            # Soft requirement — titles vary ("Software Engineer", etc.)
            pass
    return True


def _row_matches_work_mode(blob: str, work_mode: str) -> bool:
    if not work_mode.strip():
        return True
    return re.search(rf"\b{re.escape(work_mode.strip())}\b", blob, re.IGNORECASE) is not None


async def _expand_results(page: Page, stable_rounds: int = 3) -> Tuple[int, str]:
    """Click 'Show more jobs' and scroll until unique gh_jid count plateaus."""
    prev = -1
    stable = 0
    notes: List[str] = []
    while stable < stable_rounds:
        cnt = await page.evaluate(
            """() => new Set([...document.querySelectorAll('a[href*="gh_jid="]')]
              .map(a => a.href.split('#')[0])).size"""
        )
        if cnt == prev:
            stable += 1
        else:
            stable = 0
        prev = cnt
        try:
            btn = page.get_by_role("button", name="Show more jobs")
            if await btn.count():
                await btn.click(timeout=8000)
                notes.append("clicked_show_more")
        except Exception:
            notes.append("show_more_unavailable_or_failed")
        await page.mouse.wheel(0, 4500)
        await page.wait_for_timeout(900)
    return prev, ";".join(notes[-5:])


async def _collect_raw_cards(page: Page) -> List[Dict[str, Any]]:
    """One object per unique job URL from listing DOM."""
    return await page.evaluate(
        """() => {
      const links = [...document.querySelectorAll('a[href*="gh_jid="]')];
      const out = [];
      const seen = new Set();
      for (const a of links) {
        const href = a.href.split('#')[0];
        if (seen.has(href)) continue;
        seen.add(href);
        let cur = a;
        let blob = '';
        for (let i = 0; i < 14 && cur; i++) {
          blob = cur.innerText || '';
          if (blob.includes('Posted')) break;
          cur = cur.parentElement;
        }
        const title = (a.innerText || '').trim().split(/\s+/).slice(0, 12).join(' ');
        out.push({ href, blob, anchor_title: title });
      }
      return out;
    }"""
    )


def _parse_row_dates(blob: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    m = POSTED_RE.search(blob)
    if not m:
        return None, None, None
    raw_span = m.group(0)
    n = int(m.group(1))
    unit = m.group(2)
    days = _posted_to_freshness_days(n, unit)
    # ISO approximate: posted instant ~= now - days (midnight fidelity not provided by site)
    return raw_span, days, None


async def _row_snapshot(page: Page, href: str, blob_for_fallback: str) -> Dict[str, str]:
    """Prefer compact HTML for the anchor row; fallback to text blob excerpt."""
    canon = href.split("#")[0]
    content = await page.evaluate(
        """(href) => {
      const links = [...document.querySelectorAll('a[href*="gh_jid="]')];
      const a = links.find(x => x.href.split('#')[0] === href);
      if (!a) return '';
      let cur = a;
      for (let i = 0; i < 14 && cur; i++) {
        const t = cur.innerText || '';
        if (t.includes('Posted')) return cur.outerHTML.slice(0, 33000);
        cur = cur.parentElement;
      }
      return a.outerHTML.slice(0, 33000);
    }""",
        canon,
    )
    kind = "compact_html"
    if not content.strip():
        kind = "text_blob"
        content = blob_for_fallback[:33000]
    if len(content) > 32000:
        content = content[:32000] + "\n<!-- truncated per spike cap -->"
    return {"kind": kind, "content": content}


async def run_capture(args: argparse.Namespace) -> Dict[str, Any]:
    max_days = _parse_max_listing_days(args.max_listing_age)
    gaps: Dict[str, Any] = {}
    gap_i = 0
    warned_no_date = False

    def add_gap(severity: str, message: str) -> None:
        nonlocal gap_i
        gap_i += 1
        gaps[f"gap-{gap_i:03d}"] = {"severity": severity, "message": message}

    captured_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    meta_notes: List[str] = []

    async with create_browser_context(headless=not args.headed) as ctx:
        page = await ctx.new_page()
        await page.goto(args.source_site, wait_until="networkidle", timeout=args.timeout_ms)
        await page.wait_for_timeout(2500)
        # UI filters (Roles) often zero results when over-constrained; optional single-keyword assist.
        if args.try_roles_filter:
            try:
                await page.locator("button").filter(has_text="Roles").first.click(timeout=8000)
                await page.wait_for_timeout(600)
                inp = page.locator("input:visible").first
                q = args.roles_filter_query or "Python"
                await inp.fill(q)
                await inp.press("Enter")
                await page.wait_for_timeout(3500)
                meta_notes.append(f"roles_filter={q!r}")
            except Exception as exc:
                add_gap("warning", f"Roles filter skipped: {exc}")
        final_count, expand_notes = await _expand_results(page)
        meta_notes.append(f"expand={expand_notes}")
        meta_notes.append(f"unique_gh_links_end_state={final_count}")

        cards = await _collect_raw_cards(page)
        if final_count < 50:
            add_gap(
                "info",
                "Listing count stayed modest after Show more + scroll; board may lazy-load via "
                f"conditions not met in headless run (final unique={final_count}).",
            )

        findings_order: List[str] = []
        findings: Dict[str, Any] = {}
        row_idx = 0

        for card in cards:
            href = card["href"]
            blob = card.get("blob") or ""
            title_guess = (card.get("anchor_title") or "").strip()

            if not _row_matches_title(blob, args.title_query):
                continue
            if not _row_matches_work_mode(blob, args.work_mode):
                continue

            date_raw, freshness_days, date_iso = _parse_row_dates(blob)
            if date_raw is None and not warned_no_date:
                warned_no_date = True
                add_gap(
                    "warning",
                    "One or more matched listings lack a parsed 'Posted … ago' line; "
                    "freshness left null and passes_max_age_rule false.",
                )

            passes = (
                freshness_days is not None and freshness_days < max_days
                if max_days > 0
                else False
            )
            # Title line: first non-Apply line from blob
            listing_title = title_guess
            for line in blob.split("\n"):
                ln = line.strip()
                if ln and ln.lower() != "apply" and len(ln) > 2:
                    listing_title = ln
                    break

            company_name = ""
            lines = [ln.strip() for ln in blob.split("\n") if ln.strip()]
            if len(lines) >= 2:
                # Heuristic: company often follows location block (trial-and-error documented in notes)
                for i, ln in enumerate(lines[1:6], start=1):
                    if re.match(r"^Posted\b", ln):
                        break
                    if "ago" in ln or "United States" in ln or "," in ln:
                        continue
                    if ln.lower() in {"apply", listing_title.lower()}:
                        continue
                    company_name = ln
                    break

            row_idx += 1
            fid = f"row-{row_idx:05d}"
            findings_order.append(fid)
            snap = await _row_snapshot(page, href, blob)
            findings[fid] = {
                "job_link": href,
                "listing_title": listing_title,
                "company_name": company_name,
                "date_visible_raw": date_raw,
                "date_parsed_utc": date_iso,
                "freshness_days": freshness_days,
                "passes_max_age_rule": passes,
                "row_snapshot": snap,
                "source_page_url": page.url,
                "listing_index_on_page": row_idx - 1,
            }

        if not findings_order:
            add_gap(
                "error",
                "Zero listings matched title/work_mode/date heuristics after capture — "
                "see notes for UI filter behavior; widen queries or run headed for debugging.",
            )

        payload = {
            "spike_meta": {
                "source_site": args.source_site,
                "title_query": args.title_query,
                "work_mode": args.work_mode,
                "max_listing_age": args.max_listing_age,
                "captured_at_utc": captured_at,
                "playwright_version": _playwright_version(),
                "notes": " | ".join(meta_notes),
            },
            "gaps": gaps,
            "findings_order": findings_order,
            "findings": findings,
        }
        await page.close()
        return payload


def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AST-398 jobs.a16z.com raw capture spike.")
    p.add_argument("--source-site", default=DEFAULT_SOURCE)
    p.add_argument("--title-query", default=DEFAULT_TITLE_QUERY)
    p.add_argument("--work-mode", default=DEFAULT_WORK_MODE)
    p.add_argument("--max-listing-age", default=DEFAULT_MAX_AGE)
    p.add_argument(
        "--out",
        default=str(_ROOT / "debug/spikes/boards/a16z/findings_raw.json"),
        help="Output JSON path",
    )
    p.add_argument("--headed", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="Print resolved args and exit.")
    p.add_argument("--timeout-ms", type=int, default=120_000)
    p.add_argument(
        "--try-roles-filter",
        action="store_true",
        help="Open Roles filter and type --roles-filter-query (often narrows DOM).",
    )
    p.add_argument(
        "--roles-filter-query",
        default="",
        help="Substring for Roles typeahead when --try-roles-filter is set.",
    )
    return p


async def _async_main() -> int:
    args = build_arg_parser().parse_args()
    if args.dry_run:
        print(json.dumps(vars(args), indent=2))
        return 0
    data = await run_capture(args)
    out = Path(args.out)
    _atomic_write_json(out, data)
    print(f"Wrote {out} findings={len(data.get('findings_order', []))}")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_async_main()))


if __name__ == "__main__":
    main()
