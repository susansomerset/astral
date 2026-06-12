#!/usr/bin/env python3
"""
Analyze DOM elements on a page by counting element types.

Usage:
    python3 scripts/analyze_dom_elements.py <url>
"""

import sys
import asyncio
from collections import Counter
from pathlib import Path
from html.parser import HTMLParser

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright
from src.external.playwright import _cull_html


class ElementCounter(HTMLParser):
    """Simple parser to count HTML elements by tag name."""
    
    def __init__(self):
        super().__init__()
        self.element_counts = Counter()
        self.total_elements = 0
    
    def handle_starttag(self, tag, attrs):
        self.element_counts[tag.lower()] += 1
        self.total_elements += 1


async def analyze_page(url: str):
    """Extract DOM and count elements by type."""
    print(f"Analyzing page: {url}")
    print("=" * 80)
    
    async with async_playwright() as pw:
        try:
            browser = await pw.firefox.launch(headless=True)
        except Exception:
            try:
                browser = await pw.webkit.launch(headless=True)
            except Exception:
                print("ERROR: Could not launch browser")
                return
        
        context = await browser.new_context(viewport={"width": 1280, "height": 2000})
        page = await context.new_page()
        
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(2000)
            
            # Extract body HTML
            print("Extracting body HTML...")
            body_html = await page.evaluate('''() => {
                return document.body ? document.body.outerHTML : '';
            }''')
            
            if not body_html:
                print("WARNING: No body element found")
                return
            
            # Get sizes before and after culling
            pre_cull_size = len(body_html.encode('utf-8'))
            print(f"Body HTML (pre-cull): {pre_cull_size:,} bytes ({len(body_html):,} characters)")
            
            print("Culling HTML...")
            culled_html = _cull_html(body_html)
            post_cull_size = len(culled_html.encode('utf-8'))
            print(f"Body HTML (post-cull): {post_cull_size:,} bytes ({len(culled_html):,} characters)")
            reduction = pre_cull_size - post_cull_size
            reduction_pct = (reduction / pre_cull_size * 100) if pre_cull_size > 0 else 0
            print(f"Reduction: {reduction:,} bytes ({reduction_pct:.1f}%)")
            print("=" * 80)
            
            # Count elements (using culled HTML)
            print("Counting elements in culled HTML...")
            counter = ElementCounter()
            counter.feed(culled_html)
            
            print(f"\nTotal elements: {counter.total_elements}")
            print("=" * 80)
            print("\nElement counts (sorted by count, descending):")
            print("-" * 80)
            
            for tag, count in counter.element_counts.most_common():
                percentage = (count / counter.total_elements) * 100
                print(f"  {tag:20s}: {count:6d} ({percentage:5.1f}%)")
            
            print("=" * 80)
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/analyze_dom_elements.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    asyncio.run(analyze_page(url))


if __name__ == "__main__":
    main()
