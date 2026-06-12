#!/usr/bin/env python3
"""AST-489: spike — Google Custom Search Engine for exemplar company-discovery queries.

Usage (repo root, with GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID set in the environment or repo `.env`):

  # Built-in exemplar batch (AST-489 acceptance runs)
  python3 scripts/spikes/ast489_google_cse_company_search_spike.py

  # Ad-hoc query with site restriction (alias or raw domain fragment)
  python3 scripts/spikes/ast489_google_cse_company_search_spike.py --site linkedin \\
      Small businesses making smart watches for dolls

  python3 scripts/spikes/ast489_google_cse_company_search_spike.py --days 7 \\
      healthtech SaaS remote

Non-interactive; prints labeled title / URL / snippet per hit per run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=_ROOT / ".env")
except ImportError:
    pass

from src.external.google_cse import search_google_cse

# Verbatim exemplar queries from AST-489 description
EXEMPLAR_QUERIES = (
    'healthtech SaaS platform "Series B" OR "Series C" remote',
    "healthcare software platform integration company 2024 2025",
    "clinical data platform SaaS company remote-first",
)

# Canonical site tokens (plan § Stage 2)
SITE_LINKEDIN_COMPANY = "linkedin.com/company"
SITE_CRUNCHBASE = "www.crunchbase.com/organization"
SITE_BUILTIN = "builtin.com"
SITE_WELLFOUND = "wellfound.com"
SITE_INDEED = "indeed.com"

# Short names for --site (case-insensitive); anything with "." passes through as-is
SITE_ALIASES: dict[str, str] = {
    "linkedin": SITE_LINKEDIN_COMPANY,
    "crunchbase": SITE_CRUNCHBASE,
    "builtin": SITE_BUILTIN,
    "wellfound": SITE_WELLFOUND,
    "indeed": SITE_INDEED,
}

RUNS = [
    {
        "query": EXEMPLAR_QUERIES[0],
        "site_filters": (SITE_LINKEDIN_COMPANY,),
        "max_results": 10,
    },
    {
        "query": EXEMPLAR_QUERIES[1],
        "site_filters": (SITE_CRUNCHBASE, SITE_BUILTIN),
        "max_results": 10,
    },
    {
        "query": EXEMPLAR_QUERIES[2],
        "site_filters": (SITE_WELLFOUND, SITE_INDEED),
        "max_results": 10,
    },
]


def resolve_site_filter(raw: str) -> str:
    token = raw.strip()
    if not token:
        raise ValueError("empty --site value")
    if "." in token:
        return token
    key = token.lower()
    if key not in SITE_ALIASES:
        known = ", ".join(sorted(SITE_ALIASES))
        raise ValueError(f"unknown site alias {raw!r} — use one of: {known}, or a domain like linkedin.com/company")
    return SITE_ALIASES[key]


def run_search(
    *,
    query: str,
    site_filters: tuple[str, ...],
    max_results: int,
    days: int | None = None,
) -> None:
    print("=" * 72)
    print(f"QUERY: {query}")
    extra = f"site_filters={site_filters!r} max_results={max_results}"
    if days is not None:
        extra += f" days={days}"
    print(extra)
    print("=" * 72)
    try:
        hits = search_google_cse(
            query,
            max_results=max_results,
            site_filters=site_filters or None,
            days=days,
        )
    except Exception as exc:  # noqa: BLE001 — spike surfaces any failure plainly
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if not hits:
        print(
            (
                "WARNING: zero organic hits returned for this run "
                f"(query={query!r} site_filters={site_filters!r})."
            ),
            file=sys.stderr,
        )
        return

    for hit in hits:
        print(f"Title: {hit['title']}")
        print(f"URL: {hit['url']}")
        print(f"Snippet: {hit['snippet']}")
        print()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Google CSE company-discovery spike (AST-489).",
    )
    parser.add_argument(
        "--site",
        "-s",
        action="append",
        dest="sites",
        metavar="NAME",
        help=(
            "Restrict results to a site (repeatable). "
            "Aliases: linkedin, crunchbase, builtin, wellfound, indeed — "
            "or pass a raw fragment such as linkedin.com/company or www.crunchbase.com/organization."
        ),
    )
    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=10,
        metavar="N",
        help="Max hits to return (0 = unlimited per google_cse API pagination). Default: 10.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        metavar="N",
        help="Restrict to results indexed within the last N days (Google dateRestrict=dN).",
    )
    parser.add_argument(
        "query_words",
        nargs="*",
        metavar="QUERY",
        help="Free-text search query (omit to run built-in exemplars only).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    query = " ".join(args.query_words).strip()

    if args.days is not None and args.days < 1:
        print("ERROR: --days must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    if args.sites and not query:
        print("ERROR: QUERY is required when --site is set.", file=sys.stderr)
        sys.exit(1)

    if query:
        try:
            site_filters = tuple(resolve_site_filter(s) for s in (args.sites or []))
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        run_search(
            query=query,
            site_filters=site_filters,
            max_results=args.max_results,
            days=args.days,
        )
        return

    for spec in RUNS:
        run_search(
            query=spec["query"],
            site_filters=spec["site_filters"],
            max_results=spec["max_results"],
            days=args.days,
        )


if __name__ == "__main__":
    main()
