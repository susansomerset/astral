#!/usr/bin/env python3
"""
Test script for extracting visible text from web pages.

Tests get_visible_text() from src/external/playwright.py. Accepts a URL via
command-line and displays timing metrics and text preview.

Usage:
    python3 scripts/test_getVisibleText.py <url>

Example:
    python3 scripts/test_getVisibleText.py https://example.com
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path to import from src/external
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.external.playwright import get_visible_text


async def main():
    """Main function to test get_visible_text."""
    
    # Get URL from command-line argument
    if len(sys.argv) < 2:
        print("Error: URL argument required")
        print(f"Usage: python3 {sys.argv[0]} <url>")
        print(f"Example: python3 {sys.argv[0]} https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        print(f"[*] Fetching visible text from: {url}")
        print("[*] Loading page with Playwright...\n")
        
        start_time = time.time()
        text = await get_visible_text(url)
        total_time = time.time() - start_time
        
        # Display results
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"URL scraped: {url}")
        print(f"Total time: {total_time:.3f} seconds")
        print(f"Text length: {len(text)} characters")
        print("-" * 80)
        print("First 500 characters of text:")
        print("-" * 80)
        print(text[:500])
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
