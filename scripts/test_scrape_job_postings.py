#!/usr/bin/env python3
"""Test scrape by batch. Scrapes all companies in the given batch.

Usage:
  python scripts/test_scrape_job_postings.py BATCH_ID

Example:
  python scripts/test_scrape_job_postings.py bd70d1f9-20e2-4384-88bc-a2477e79b4ad
"""
import asyncio
import sys
from pathlib import Path
from typing import Tuple

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.gazer import scrape_batch
from src.core.roster import _fetch_parse_job_list
from src.data.database import get_company_batch


def _count_selectors(html: str, container: str, job_tag: str) -> Tuple[int, int]:
    """Count container matches and job_tag matches (within container). Returns (container_count, job_tag_count)."""
    if not html or (not container and not job_tag):
        return (0, 0)
    soup = BeautifulSoup(html, "html.parser")
    container_count = len(soup.select(container)) if container else 0
    combined = f"{container} {job_tag}".strip() if container and job_tag else (job_tag or container)
    job_tag_count = len(soup.select(combined)) if combined else 0
    return (container_count, job_tag_count)


async def _run(batch_id: str):
    companies = get_company_batch(batch_id)
    if not companies:
        print(f"No companies in batch {batch_id}", file=sys.stderr)
        return 1
    try:
        results = await scrape_batch(batch_id)
        for short_name, job_site, page_html in results:
            content_size = len(page_html)
            print(f"\n--- {short_name} ---")
            print(f"  job_site: {job_site}")
            print(f"  content_size: {content_size}")
            try:
                parse_info = await _fetch_parse_job_list(page_html, short_name)
                container = (parse_info.get("job_container") or "").strip()
                job_tag = (parse_info.get("job_tag") or "").strip()
                container_count, job_tag_count = _count_selectors(page_html, container, job_tag)
                print(f"  job_container: {container!r}  found={container_count}")
                print(f"  job_tag: {job_tag!r}  found={job_tag_count}")
            except Exception as parse_err:
                print(f"  parse_error: {parse_err}")
        return 0
    except Exception as e:
        print(f"FAIL {e}", file=sys.stderr)
        return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_scrape_job_postings.py BATCH_ID", file=sys.stderr)
        return 1
    batch_id = sys.argv[1]
    return asyncio.run(_run(batch_id))


if __name__ == "__main__":
    sys.exit(main())
