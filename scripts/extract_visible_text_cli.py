#!/usr/bin/env python3
"""
CLI script to extract visible text from a company website by shortname.

Usage:
    python3 scripts/extract_visible_text_cli.py <shortname>

Example:
    python3 scripts/extract_visible_text_cli.py twinhealth
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.external.playwright import get_visible_text


async def main():
    """Main function to extract visible text for a company shortname."""
    
    # Get shortname from command-line argument
    if len(sys.argv) < 2:
        print("Error: shortname argument required")
        print(f"Usage: python3 {sys.argv[0]} <shortname>")
        print(f"Example: python3 {sys.argv[0]} twinhealth")
        sys.exit(1)
    
    shortname = sys.argv[1]
    
    # Load roster
    roster_path = Path(__file__).parent.parent / "data" / "companies" / "_roster.json"
    
    if not roster_path.exists():
        print(f"[!] Roster not found: {roster_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(roster_path, 'r') as f:
        roster = json.load(f)
    
    # Find company across all categories
    company = None
    category = None
    
    for cat in ['active', 'watch', 'new', 'ignore']:
        if cat in roster and shortname in roster[cat]:
            company = roster[cat][shortname].copy()
            category = cat
            break
    
    if not company:
        print(f"[!] Company not found: {shortname}", file=sys.stderr)
        sys.exit(1)
    
    website_url = company.get('companyWebsite')
    if not website_url:
        print(f"[!] No website URL for: {shortname}", file=sys.stderr)
        sys.exit(1)
    
    company_name = company.get('companyName', shortname)
    print(f"[*] Extracting visible text for {company_name}: {website_url}")
    
    try:
        print(f"[*] Extracting visible text...")
        text = await get_visible_text(website_url)
        
        # Display results
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Company: {company_name} ({shortname})")
        print(f"URL: {website_url}")
        print(f"Text length: {len(text)} characters")
        print("-" * 80)
        print("Extracted text:")
        print("-" * 80)
        print(text)
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
