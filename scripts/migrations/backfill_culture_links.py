#!/usr/bin/env python3
"""
Backfill culture_links_to_explore for companies that went through prefilter
before that field was being saved.

Finds all companies in active/post-prefilter states that are missing
culture_links_to_explore, scrapes their homepage + nav links, calls the
prefilter_company AI task, and saves only the culture_links_to_explore
(and nav_links if freshly scraped). No state change. Idempotent.

Excluded states: IGNORE (intentionally rejected), and pre-prefilter states
(IMPORTED, WEBSITE_FOUND, NO_WEBSITE, WEBSITE_REVIEW) and CANNOT_READ_WEBSITE
(unscrapeable — would fail again).

Usage:
  python scripts/migrations/backfill_culture_links.py
  python scripts/migrations/backfill_culture_links.py --dry-run
  python scripts/migrations/backfill_culture_links.py --company aledade
  python scripts/migrations/backfill_culture_links.py --state WATCH TO_WATCH
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.database import list_companies
from src.core.roster import save_company_data
from src.core.agent import do_task
from src.external.playwright import create_browser_context, get_visible_text, extract_site_page_list
from src.utils.formatting import enumerate_array

# States to skip — not worth scraping
EXCLUDE_STATES = [
    "IGNORE",
    "IMPORTED",
    "WEBSITE_FOUND",
    "NO_WEBSITE",
    "WEBSITE_REVIEW",
    "CANNOT_READ_WEBSITE",
]

# Outcome labels for summary counter
_OUTCOMES = ["already_has_links", "no_website", "updated", "no_links_found", "error"]


async def backfill_one(company: Dict[str, Any], dry_run: bool) -> str:
    """Process one company. Returns outcome label."""
    cd = company.get("company_data") or {}

    # Already done — skip
    if cd.get("culture_links_to_explore"):
        return "already_has_links"

    short_name = company.get("short_name", "")
    state = company.get("state", "?")
    url = (company.get("company_website") or company.get("job_site") or "").strip()

    if not url:
        print(f"[{short_name}] {state} → no_website")
        return "no_website"

    try:
        async with create_browser_context() as browser_context:
            # Scrape homepage visible text
            visible_text = await get_visible_text(url, context=browser_context)
            if not visible_text or not visible_text.strip():
                print(f"[{short_name}] {state} → error (no visible text from {url})")
                return "error"

            # Scrape nav links from the same browser context
            nav_links_str = ""
            try:
                url_list = await extract_site_page_list(
                    url, max_depth=1, verify=False, context=browser_context
                )
                if url_list:
                    nav_links_str = enumerate_array("", url_list)
            except Exception as nav_err:
                # Non-fatal — proceed without nav links
                print(f"[{short_name}] {state} → nav_links failed (non-fatal): {nav_err}")

        # Assemble live_content exactly as prefilter_company expects
        parts = [f"[company_id={short_name}]", f"\n## Homepage Content\n{visible_text.strip()}"]
        if nav_links_str:
            parts.append(f"\n## Navigation Links\n{nav_links_str}")
        live_content = "\n".join(parts)

        # Call the AI — no candidate ctx needed (prefilter_company doesn't require_candidate_key)
        api_result = await do_task(
            task_key="prefilter_company",
            live_content=live_content,
            index=short_name,
        )

        if not api_result.get("success"):
            err = api_result.get("error", "do_task failed")
            print(f"[{short_name}] {state} → error ({err})")
            return "error"

        parsed = api_result.get("parsed_response") or {}
        culture_links = parsed.get("culture_links_to_explore")

        if not culture_links:
            print(f"[{short_name}] {state} → no_links_found")
            return "no_links_found"

        data_to_save: Dict[str, Any] = {"culture_links_to_explore": culture_links}
        # Save nav_links too if we freshly scraped them and they aren't already stored
        if nav_links_str and not cd.get("nav_links"):
            data_to_save["nav_links"] = nav_links_str

        if dry_run:
            print(f"[{short_name}] {state} → DRY RUN — would save {len(culture_links)} culture link(s): {culture_links}")
            return "updated"

        save_company_data(short_name, data_to_save)
        print(f"[{short_name}] {state} → updated ({len(culture_links)} culture link(s))")
        return "updated"

    except Exception as e:
        print(f"[{short_name}] {state} → error ({e})")
        return "error"


async def main(dry_run: bool, states: Optional[List[str]], company: Optional[str]) -> None:
    if dry_run:
        print("=== DRY RUN — no DB writes ===\n")

    # Load companies
    if company:
        # Single-company mode: load all, then filter by short_name
        all_companies = list_companies(exclude_states=EXCLUDE_STATES)
        companies = [c for c in all_companies if c.get("short_name") == company]
        if not companies:
            print(f"Company '{company}' not found (or in an excluded state).")
            return
    elif states:
        companies = list_companies(states=states)
    else:
        companies = list_companies(exclude_states=EXCLUDE_STATES)

    total = len(companies)
    print(f"Processing {total} company/companies...\n")

    counts = {k: 0 for k in _OUTCOMES}
    for c in companies:
        outcome = await backfill_one(c, dry_run)
        counts[outcome] = counts.get(outcome, 0) + 1

    print(f"\n{'=== DRY RUN SUMMARY ===' if dry_run else '=== SUMMARY ==='}")
    print(
        f"Total: {total} | "
        + " | ".join(f"{k}: {counts[k]}" for k in _OUTCOMES if counts[k] > 0)
    )


def run_backfill(dry_run: bool = False, states: Optional[List[str]] = None, company: Optional[str] = None) -> None:
    """Synchronous entry point for the API layer (runs the async main in a new event loop)."""
    asyncio.run(main(dry_run=dry_run, states=states, company=company))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill culture_links_to_explore for companies.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to DB.")
    parser.add_argument("--state", nargs="+", metavar="STATE",
                        help="Restrict to specific company state(s). Default: all non-excluded states.")
    parser.add_argument("--company", metavar="SHORT_NAME",
                        help="Run for a single company by short_name.")
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run, states=args.state, company=args.company))
