#!/usr/bin/env python3
"""
Quick test script to verify extraction validation is working.

Usage:
    python3 scripts/test_extraction_validation.py <shortName>
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

from src.core.roster import find_job_page


async def test_company(short_name: str, url: str):
    """Test find_job_page for a specific company."""
    print(f"\n{'='*60}")
    print(f"Testing: {short_name}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    result = await find_job_page(
        url=url,
        short_name=short_name,
        debug=True
    )
    print(f"\n{'='*60}")
    print("RESULT:")
    print(f"{'='*60}")
    print(f"State: {result.get('state')}")
    print(f"job_site: {result.get('job_site')}")
    print(f"job_tag: {result.get('job_tag')}")
    print(f"parse_type: {result.get('parse_type')}")
    print(f"Extraction Validated: {result.get('extraction_validated')}")
    if result.get('validation_error'):
        print(f"Validation Error: {result.get('validation_error')}")
    print(f"{'='*60}\n")
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/test_extraction_validation.py <shortName> <url>")
        sys.exit(1)
    
    short_name = sys.argv[1]
    url = sys.argv[2]
    
    asyncio.run(test_company(short_name, url))
