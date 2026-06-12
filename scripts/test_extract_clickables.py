#!/usr/bin/env python3
"""
Test script for extracting clickables from a page.

This script tests the extract_page_clickables() function and shows detailed
information about widget detection, internal links, and extracted clickable text.

Usage:
    python3 scripts/test_extract_clickables.py <url> [--headless] [--wait-time N]

Example:
    python3 scripts/test_extract_clickables.py https://www.cybertrol.com/careers
    python3 scripts/test_extract_clickables.py https://www.cybertrol.com/careers --no-headless
"""

import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path to import from src/external
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.external.playwright import extract_page_clickables, create_browser_context, get_page_with_artifacts, _parse_html_for_internal_clickables


async def main():
    """Main function to test extract_page_clickables."""
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Error: URL argument required")
        print(f"Usage: python3 {sys.argv[0]} <url> [--no-headless] [--wait-time N]")
        print(f"Example: python3 {sys.argv[0]} https://www.cybertrol.com/careers")
        sys.exit(1)
    
    url = sys.argv[1]
    headless = True
    
    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--no-headless":
            headless = False
            i += 1
        else:
            print(f"Error: Unknown argument: {sys.argv[i]}", file=sys.stderr)
            sys.exit(1)
    
    try:
        print("=" * 80)
        print("CLICKABLES EXTRACTION TEST")
        print("=" * 80)
        print(f"URL: {url}")
        print(f"Headless: {headless}")
        print("-" * 80)
        
        async with create_browser_context(headless=headless) as context:
            try:
                # Navigate to page and capture artifacts
                print(f"\n[*] Navigating to: {url}")
                artifacts = await get_page_with_artifacts(context, url)
                page = artifacts["page"]
                initial_html = artifacts.get("initial_html")
                request_urls = artifacts.get("request_urls", [])
                frame_urls = artifacts.get("frame_urls", [])
                
                print("[✓] Page loaded")
                print(f"  Initial HTML captured: {initial_html is not None} ({len(initial_html) if initial_html else 0} bytes)")
                print(f"  Request URLs captured: {len(request_urls)}")
                print(f"  Frame URLs found: {len(frame_urls)}")
                
                # Check initial DOM state
                print("\n[*] Checking initial DOM state...")
                initial_check = await page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const internalLinks = links.filter(l => {
                        const href = l.getAttribute('href');
                        return href && href[0] === '/' && href[1] !== '/';
                    });
                    
                    // Check for common widget patterns
                    const widgetSelectors = {
                        hubspotLoader: document.querySelector('script[id="hubspot-web-interactives-loader"]') !== null,
                        hubspotContainer: document.querySelector('[data-hubspot-wrapper-cta-id]') !== null,
                        hubspotEmbed: document.querySelector('.hs-cta-embed') !== null,
                        anyWidget: document.querySelector('[data-hubspot-wrapper-cta-id], .hs-cta-embed') !== null
                    };
                    
                    // Look for internal links with /hs/ in href
                    const hsLinks = links.filter(l => {
                        const href = l.getAttribute('href');
                        return href && href.includes('/hs/');
                    });
                    
                    return {
                        totalLinks: links.length,
                        internalLinks: internalLinks.length,
                        widgetSelectors,
                        hsLinksFound: hsLinks.length,
                        hsLinkHrefs: hsLinks.map(l => l.getAttribute('href')).slice(0, 5),
                        htmlIncludesHs: document.documentElement.innerHTML.includes('/hs/')
                    };
                }''')
                
                print(f"  Total links: {initial_check['totalLinks']}")
                print(f"  Internal links: {initial_check['internalLinks']}")
                print(f"  Widget selectors found:")
                for selector, found in initial_check['widgetSelectors'].items():
                    print(f"    - {selector}: {found}")
                print(f"  Links with '/hs/' in href: {initial_check['hsLinksFound']}")
                if initial_check['hsLinksFound'] > 0:
                    print(f"    Sample hrefs: {initial_check['hsLinkHrefs']}")
                print(f"  '/hs/' in HTML source: {initial_check['htmlIncludesHs']}")
                
                # Wait a bit for dynamic content - but check what happens to the link
                print("\n[*] Monitoring link during wait...")
                
                # Check what the link looks like before wait
                link_before = await page.evaluate('''() => {
                    const link = document.querySelector('a[href*="/hs/cta"]');
                    if (!link) return null;
                    return {
                        hrefAttr: link.getAttribute('href'),  // Attribute value
                        hrefProperty: link.href,  // Resolved property
                        startsWithSlash: link.getAttribute('href')?.startsWith('/'),
                        outerHTML: link.outerHTML.substring(0, 300),
                        parentHTML: link.parentElement?.outerHTML.substring(0, 400) || null,
                        visible: link.offsetParent !== null
                    };
                }''')
                
                if link_before:
                    print(f"  Before wait - Link found:")
                    print(f"    href attribute: {link_before['hrefAttr'][:100]}...")
                    print(f"    href property: {link_before['hrefProperty'][:100]}...")
                    print(f"    starts with '/': {link_before['startsWithSlash']}")
                    print(f"    visible: {link_before['visible']}")
                    print(f"    parent: {link_before['parentHTML'][:200]}...")
                else:
                    print("  Before wait - No /hs/cta link found")
                
                # Wait for dynamic content
                await page.wait_for_timeout(2000)
                
                # Check what happened to the link - check both by attribute and by resolved href
                link_after = await page.evaluate('''() => {
                    // Check by attribute (what we use in extraction)
                    const linkByAttr = document.querySelector('a[href*="/hs/cta"]');
                    
                    // Check by resolved href property
                    const allLinks = Array.from(document.querySelectorAll('a'));
                    const linkByProperty = allLinks.find(l => l.href && l.href.includes('/hs/cta'));
                    
                    // Check if container still exists
                    const container = document.querySelector('[data-hubspot-wrapper-cta-id]');
                    
                    if (!linkByAttr && !linkByProperty) {
                        return {
                            linkExists: false,
                            containerExists: container !== null,
                            containerHTML: container?.outerHTML.substring(0, 500) || null
                        };
                    }
                    
                    const link = linkByAttr || linkByProperty;
                    return {
                        linkExists: true,
                        foundBy: linkByAttr ? 'attribute' : 'property',
                        hrefAttr: link.getAttribute('href'),
                        hrefProperty: link.href,
                        startsWithSlash: link.getAttribute('href')?.startsWith('/'),
                        outerHTML: link.outerHTML.substring(0, 300),
                        visible: link.offsetParent !== null
                    };
                }''')
                
                print(f"\n  After wait - Link status:")
                if link_after['linkExists']:
                    print(f"    Link still exists (found by: {link_after['foundBy']})")
                    print(f"    href attribute: {link_after['hrefAttr'][:100]}...")
                    print(f"    href property: {link_after['hrefProperty'][:100]}...")
                    print(f"    starts with '/': {link_after['startsWithSlash']}")
                    print(f"    visible: {link_after['visible']}")
                else:
                    print(f"    Link NOT FOUND by attribute selector!")
                    print(f"    Container exists: {link_after['containerExists']}")
                    if link_after['containerHTML']:
                        print(f"    Container HTML: {link_after['containerHTML'][:300]}...")
                
                # Check after wait
                after_wait_check = await page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const internalLinks = links.filter(l => {
                        const href = l.getAttribute('href');
                        return href && href[0] === '/' && href[1] !== '/';
                    });
                    
                    const widgetSelectors = {
                        hubspotLoader: document.querySelector('script[id="hubspot-web-interactives-loader"]') !== null,
                        hubspotContainer: document.querySelector('[data-hubspot-wrapper-cta-id]') !== null,
                        hubspotEmbed: document.querySelector('.hs-cta-embed') !== null
                    };
                    
                    const hsLinks = links.filter(l => {
                        const href = l.getAttribute('href');
                        return href && href.includes('/hs/');
                    });
                    
                    return {
                        totalLinks: links.length,
                        internalLinks: internalLinks.length,
                        widgetSelectors,
                        hsLinksFound: hsLinks.length,
                        hsLinkHrefs: hsLinks.map(l => l.getAttribute('href')).slice(0, 10)
                    };
                }''')
                
                print(f"  After wait - Total links: {after_wait_check['totalLinks']}")
                print(f"  After wait - Internal links: {after_wait_check['internalLinks']}")
                print(f"  After wait - Widget selectors:")
                for selector, found in after_wait_check['widgetSelectors'].items():
                    print(f"    - {selector}: {found}")
                print(f"  After wait - Links with '/hs/': {after_wait_check['hsLinksFound']}")
                if after_wait_check['hsLinksFound'] > 0:
                    print(f"    All hrefs: {after_wait_check['hsLinkHrefs']}")
                
                # Parse initial HTML for clickables (to show what was extracted from HTML)
                if initial_html:
                    html_clickables = _parse_html_for_internal_clickables(initial_html)
                    print("\n" + "-" * 80)
                    print(f"[*] Clickables extracted from initial HTML: {len(html_clickables)}")
                    if html_clickables:
                        for i, text in enumerate(html_clickables, 1):
                            print(f"    {i}. {text}")
                
                # Now test the actual extract_page_clickables function
                print("\n" + "=" * 80)
                print("[*] Testing extract_page_clickables() function (with priority merge)...")
                print("=" * 80)
                
                clickables = await extract_page_clickables(page, initial_html=initial_html)
                
                print(f"\n[✓] Extraction complete!")
                print(f"  Total clickables found: {len(clickables)}")
                
                if clickables:
                    print("\n  Extracted clickable text (priority merged: HTML > early DOM > late DOM):")
                    for i, text in enumerate(clickables, 1):
                        print(f"    {i}. {text}")
                else:
                    print("\n  [!] No clickables extracted!")
                
                # Final diagnostic check
                print("\n" + "=" * 80)
                print("FINAL DIAGNOSTIC CHECK")
                print("=" * 80)
                
                final_check = await page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const internalLinks = [];
                    
                    links.forEach(link => {
                        const href = link.getAttribute('href');
                        // Internal hrefs: start with "/" but not "//"
                        const isInternal = href && href.length > 0 && href[0] === '/' && (href.length === 1 || href[1] !== '/');
                        
                        if (isInternal) {
                            const style = window.getComputedStyle(link);
                            const isVisible = style.display !== 'none' && 
                                             style.visibility !== 'hidden' && 
                                             style.opacity !== '0' &&
                                             link.offsetParent !== null;
                            
                            // Extract text
                            const img = link.querySelector('img');
                            let text = '';
                            if (img) {
                                text = img.getAttribute('alt')?.trim() || '';
                                if (!text) {
                                    const clone = link.cloneNode(true);
                                    clone.querySelectorAll('img').forEach(i => i.remove());
                                    text = clone.textContent?.trim() || '';
                                }
                            } else {
                                text = link.textContent?.trim() || '';
                            }
                            
                            if (!text) {
                                text = link.getAttribute('aria-label')?.trim() || 
                                       link.getAttribute('title')?.trim() || '';
                            }
                            
                            internalLinks.push({
                                href,
                                visible: isVisible,
                                hasText: !!text,
                                text: text || '(no text)',
                                hasImage: !!img,
                                imageAlt: img?.getAttribute('alt') || null
                            });
                        }
                    });
                    
                    const visibleInternalLinks = internalLinks.filter(l => l.visible);
                    const visibleWithText = internalLinks.filter(l => l.visible && l.hasText);
                    
                    return {
                        totalLinks: links.length,
                        internalLinksFound: internalLinks.length,
                        internalLinks: internalLinks,
                        visibleInternalLinks: visibleInternalLinks,
                        visibleWithText: visibleWithText
                    };
                }''')
                
                print(f"  Total links in DOM: {final_check['totalLinks']}")
                print(f"  Internal links found: {final_check['internalLinksFound']}")
                print(f"  Visible internal links: {len(final_check['visibleInternalLinks'])}")
                print(f"  Visible with text: {len(final_check['visibleWithText'])}")
                
                if final_check['visibleWithText']:
                    print("\n  Internal links that should have been extracted:")
                    for i, link_info in enumerate(final_check['visibleWithText'], 1):
                        print(f"    {i}. href: {link_info['href']}")
                        print(f"       text: '{link_info['text']}'")
                        print(f"       hasImage: {link_info['hasImage']}")
                        if link_info['imageAlt']:
                            print(f"       imageAlt: '{link_info['imageAlt']}'")
                else:
                    print("\n  [!] No visible internal links with text found!")
                    if final_check['internalLinks']:
                        print("\n  Internal links found (but filtered out):")
                        for i, link_info in enumerate(final_check['internalLinks'][:10], 1):
                            print(f"    {i}. href: {link_info['href']}")
                            print(f"       visible: {link_info['visible']}, hasText: {link_info['hasText']}")
                            print(f"       text: '{link_info['text']}'")
                
                print("\n" + "=" * 80)
                
            except Exception as e:
                print(f"\n[!] Error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                sys.exit(1)
        
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
