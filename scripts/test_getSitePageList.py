#!/usr/bin/env python3
"""
Test script for getting site page list.

This is a test/maintenance script for testing the extract_site_page_list()
function from src/external/playwright.py. It accepts a URL via command-line
and displays all loadable pages found on the site.

Usage:
    python3 scripts/test_getSitePageList.py <url> [--max-depth N] [--debug] [--no-verify]

Example:
    python3 scripts/test_getSitePageList.py https://swordhealth.com
    python3 scripts/test_getSitePageList.py https://swordhealth.com --max-depth 3 --debug
    python3 scripts/test_getSitePageList.py https://swordhealth.com --max-depth 1 --no-verify
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import from src/external
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.external.playwright import extract_site_page_list


async def main():
    """Main function to test extract_site_page_list."""
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Error: URL argument required")
        print(f"Usage: python3 {sys.argv[0]} <url> [--max-depth N] [--debug] [--no-verify]")
        print(f"Example: python3 {sys.argv[0]} https://swordhealth.com")
        print(f"Example: python3 {sys.argv[0]} https://swordhealth.com --max-depth 3 --debug")
        print(f"Example: python3 {sys.argv[0]} https://swordhealth.com --max-depth 1 --no-verify")
        sys.exit(1)
    
    url = sys.argv[1]
    max_depth = 5
    debug = False
    verify = True
    
    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--max-depth" and i + 1 < len(sys.argv):
            try:
                max_depth = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"Error: --max-depth requires a number, got: {sys.argv[i + 1]}", file=sys.stderr)
                sys.exit(1)
        elif sys.argv[i] == "--debug":
            debug = True
            i += 1
        elif sys.argv[i] == "--no-verify":
            verify = False
            i += 1
        else:
            print(f"Error: Unknown argument: {sys.argv[i]}", file=sys.stderr)
            sys.exit(1)
    
    try:
        print(f"[*] Crawling site starting from: {url}")
        print(f"[*] Max depth: {max_depth}")
        print(f"[*] Debug mode: {debug}")
        print(f"[*] Verify pages: {verify}")
        print("[*] Loading pages with Playwright...\n")
        
        # Call the extract_site_page_list function
        pages = await extract_site_page_list(url, max_depth=max_depth, debug=debug, verify=verify)
        
        # Display results
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Total loadable pages found: {len(pages)}")
        print("-" * 80)
        print("Pages:")
        print("-" * 80)
        
        # Display all pages
        for i, page_url in enumerate(pages, 1):
            print(f"{i:3d}. {page_url}")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
