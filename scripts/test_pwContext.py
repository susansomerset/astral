#!/usr/bin/env python3
"""
Test script for browser context management.

This script demonstrates using a shared browser context across multiple
extract function calls. It shows how cookies and session data are preserved
when using the same context for different operations.

Usage:
    python3 scripts/test_pwContext.py <url> [--headless] [--no-verify]

Example:
    python3 scripts/test_pwContext.py https://swordhealth.com
    python3 scripts/test_pwContext.py https://swordhealth.com --headless
    python3 scripts/test_pwContext.py https://swordhealth.com --no-verify
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import from src/external
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.external.playwright import create_browser_context, get_visible_text, extract_site_page_list


async def main():
    """Main function to test shared browser context."""
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Error: URL argument required")
        print(f"Usage: python3 {sys.argv[0]} <url> [--headless]")
        print(f"Example: python3 {sys.argv[0]} https://swordhealth.com")
        sys.exit(1)
    
    url = sys.argv[1]
    headless = True
    verify = False
    
    # Parse optional arguments
    if "--headless" in sys.argv:
        headless = True
    elif "--no-headless" in sys.argv or "--headed" in sys.argv:
        headless = False
    
    if "--no-verify" in sys.argv:
        verify = False
    elif "--verify" in sys.argv:
        verify = True
    
    try:
        print("=" * 80)
        print("BROWSER CONTEXT TEST")
        print("=" * 80)
        print(f"URL: {url}")
        print(f"Headless mode: {headless}")
        print(f"Verify pages: {verify}")
        print("\n[*] Creating shared browser context...")
        print("[*] Both operations will use the same context (shared cookies/storage)\n")
        
        # Use shared context for both operations
        async with create_browser_context(headless=headless) as ctx:
            print(f"[*] Extracting visible text from {url}...")
            text = await get_visible_text(url, context=ctx)
            
            print(f"\n[*] Text extraction complete:")
            print(f"    - Text length: {len(text)} characters")
            
            print(f"\n[*] Extracting site page list from {url}...")
            page_list = await extract_site_page_list(url, context=ctx, max_depth=2, debug=True, verify=verify)
            
            print(f"\n[*] Page list extraction complete:")
            print(f"    - Pages found: {len(page_list)}")
            if page_list:
                print(f"    - First 5 pages:")
                for i, page_url in enumerate(page_list[:5], 1):
                    print(f"      {i}. {page_url}")
                if len(page_list) > 5:
                    print(f"    - ... and {len(page_list) - 5} more")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        print("[*] Browser context automatically closed")
        print("[*] Both operations shared the same context successfully")
        
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
