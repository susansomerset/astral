# AST-138 — Capture Nav Links During Job Page Discovery

<!-- linear-archive: AST-138 archived 2026-06-03 -->

## Linear archive (AST-138)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-138/capture-nav-links-during-job-page-discovery  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** unassigned  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

During Roster's locate_job_page step, capture top-level site navigation links as a byproduct and store in company_data\["nav_links"\]. Provides the menu of pages for the Consult LIKE culture page selection.

**Acceptance Criteria:**

**During locate_job_page processing:**

* While navigating the company website, extract top-level nav links (header/footer navigation)
* Store as ordered list in company_data\["nav_links"\]
* Includes link text and URL for each nav item

**Data Shape:**

```json
{
    "nav_links": [
        {"text": "About", "url": "https://example.com/about"},
        {"text": "Products", "url": "https://example.com/products"},
        {"text": "Blog", "url": "https://example.com/blog"},
        {"text": "Careers", "url": "https://example.com/careers"}
    ]
}
```

**Scope:**

* Low-effort add-on to existing Playwright navigation in locate_job_page
* Extract from header/footer nav elements during page load
* Merge into company_data (don't clobber existing parse_instructions, etc.)
* If extraction fails, log and continue — locate_job_page should not fail because of this

**Consumer:** Prep Company Culture Pages (Astral Consult) uses nav_links to let AI analyst pick culture-relevant pages

**Layer:** Touches src/external/playwright.py (extraction) and src/core/roster.py (save to company_data)

# Capture Nav Links During Job Page Discovery

**Scope:** While navigating, extract header/footer nav; ordered list of {text, url}.

**Ref:** consult-features During locate_job_page processing.

## Metadata

* URL: [AST-166](https://linear.app/astralcareermatch/issue/AST-166/sub-extract-nav-links-during-locate-job-page)
* Identifier: [AST-166](https://linear.app/astralcareermatch/issue/AST-166/sub-extract-nav-links-during-locate-job-page)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Roster](https://linear.app/astralcareermatch/project/astral-roster-c7b66eee5115). Finds company metadata and parses job site pages to identify relevant selectors
* Created: 2026-02-10T21:45:19.205Z
* Updated: 2026-03-02T19:20:12.215Z

---

# Capture Nav Links During Job Page Discovery

**Scope:** company_data\["nav_links"\]; merge, don't clobber parse_instructions etc.; extraction failure to log and continue.

**Ref:** consult-features Data Shape; Scope; Consumer.

## Metadata

* URL: [AST-167](https://linear.app/astralcareermatch/issue/AST-167/sub-store-in-company-data-and-merge)
* Identifier: [AST-167](https://linear.app/astralcareermatch/issue/AST-167/sub-store-in-company-data-and-merge)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Roster](https://linear.app/astralcareermatch/project/astral-roster-c7b66eee5115). Finds company metadata and parses job site pages to identify relevant selectors
* Created: 2026-02-10T21:45:20.464Z
* Updated: 2026-03-02T19:20:12.136Z

---

# Capture Nav Links During Job Page Discovery

**Scope:** roster.get_company_data(company, key); key from config; case-style handling so for nav_links key, if missing, fetch via extract_site_page_list, enumerate_array, merge-save, return. Config for key name. Extensible for future self-heal keys. **Ref:** plan coat-check pattern.

## Metadata

* URL: [AST-171](https://linear.app/astralcareermatch/issue/AST-171/sub-generic-get-company-data-and-fetch-on-missing-for-nav-links-coat)
* Identifier: [AST-171](https://linear.app/astralcareermatch/issue/AST-171/sub-generic-get-company-data-and-fetch-on-missing-for-nav-links-coat)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Roster](https://linear.app/astralcareermatch/project/astral-roster-c7b66eee5115). Finds company metadata and parses job site pages to identify relevant selectors
* Created: 2026-02-10T23:28:22.094Z
* Updated: 2026-03-02T19:20:12.077Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
