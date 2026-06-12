#!/usr/bin/env python3
"""
Test script for find_job_page function.

Usage:
    python3 scripts/test_find_job_page.py <url>

Example:
    python3 scripts/test_find_job_page.py https://example.com
"""

import asyncio
import json
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not installed, fall back to system environment variables
    pass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.roster import find_job_page


async def main():
    """Test find_job_page function."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/test_find_job_page.py <url> [--debug] [--max-depth N]")
        print("  --debug or -d: Enable debug output")
        print("  --max-depth N: Set crawl depth (default: 2)")
        sys.exit(1)
    
    url = sys.argv[1]
    debug = "--debug" in sys.argv or "-d" in sys.argv
    
    # Parse max_depth from command line
    max_depth = 2  # default
    try:
        if "--max-depth" in sys.argv:
            idx = sys.argv.index("--max-depth")
            if idx + 1 < len(sys.argv):
                max_depth = int(sys.argv[idx + 1])
    except (ValueError, IndexError):
        print("Warning: Invalid --max-depth value, using default of 2")
        max_depth = 2
    
    print(f"Testing find_job_page with URL: {url}")
    if debug:
        print("DEBUG mode enabled - will show live content sent to APIs")
    print(f"Using max_depth={max_depth}")
    print("-" * 60)
    
    try:
        result = await find_job_page(url, debug=debug, max_depth=max_depth)
        print("\n✓ Function completed successfully!")
        print("\nResult:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n✗ Function failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
