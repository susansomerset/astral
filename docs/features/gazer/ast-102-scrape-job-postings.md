# AST-102 — Scrape Job Postings

<!-- linear-archive: AST-102 archived 2026-06-03 -->

## Linear archive (AST-102)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-102/scrape-job-postings  
**Status at archive:** Done  
**Project:** Astral Gazer  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Web scraping orchestration for job listing pages. Uses Playwright to load job sites, handle pagination/lazy loading, validate page structure, and extract DOM content for parsing.

**Acceptance Criteria:**

**Input:**

* company: Dict (company record with job_site, parse_instructions)
* batch_id: str (for lineage tracking)

**Processing Flow:**

**1. Initialize Playwright:**

* Create browser context
* Navigate to company\["job_site"\]
* Handle retries (2 attempts) for network failures

**2. Trigger Pagination:**

```python
await navigate_and_wait_for_ready(page, job_site)
await load_all_jobs(page, short_name)
```

load_all_jobs() handles:

* Infinite scroll (scroll to bottom, detect new content, repeat - max 10 scrolls)
* "Load More" buttons (click repeatedly until exhausted - max 20 clicks)
* Ensures all jobs visible in DOM

**3. Validate Page Structure:**

**If parse_instructions contains no_jobs_message:**

```python
if "no_jobs_message" in parse_instructions:
    msg = parse_instructions["no_jobs_message"]
    if msg in page_text:
        # Legitimate "no openings" - record success with 0 jobs
        record_scan_success(total_found=0, new=0, duplicates=0)
        update_company(last_scan_at=now)
        return
```

**4. Extract DOM:**

```python
page_html = await extract_page_dom(page)
# Returns culled HTML (scripts, styles, meta removed)
```

**5. Pass to Parser:**
Return (page_html, parse_instructions) for container parsing

**Playwright Retry Logic:**

* navigate_and_wait_for_ready() retries 2x on timeout/failure
* After 2 retries, raise exception (caught by Track Scan Results)

**Error Scenarios:**

**Network/Load Failures:**

* Exception raised after retries
* Tracked as failure in company_job_scan
* Company stays in WATCH state for retry

**Bot Detection:**

* Exception raised ("bot block" error message)
* Tracked as failure
* Future: May trigger separate bot mitigation workflow

**Configuration:**

```python
"gazer": {
    "concurrent_batch_size": 5,  # Max parallel browser instances
    "page_load_timeout": 60000,  # Milliseconds
    "scroll_max_attempts": 10,
    "load_more_max_clicks": 20
}
```

**Playwright Functions Used:**

* navigate_and_wait_for_ready(page, url) - Load page with retry
* wait_for_page_ready_after_navigation(page) - Wait for dynamic content
* load_all_jobs(page, short_name) - Trigger pagination
* extract_page_dom(page) - Get culled HTML

**Output:**

* On success: (page_html, parse_instructions)
* On failure: Raise exception with error details

**Browser Lifecycle:**

* Create context per company (isolation)
* Close browser after DOM extraction
* Async/concurrent execution within configured limits

**Dependencies:**

* src/external/playwright.py (existing functions)
* parse_instructions from company record
* Config for concurrency and timeouts

**Future Enhancements:**

* Bot mitigation strategies (captcha solving, proxy rotation)
* Headless browser fingerprint randomization
* Selective DOM extraction (only container regions)

**Note on no_jobs_message:**

* If message found: Early return with success status
* Avoids unnecessary parsing when site legitimately has no openings
* Allows continued monitoring without error state

# Scrape Job Postings

**Scope:** Define input and entry into scrape flow.

**Input:** company (dict with job_site, parse_instructions), batch_id (str).

**Steps:** Create browser context; navigate to company\["job_site"\]; retries (e.g. 2) for network failures.

**Validation:** company and job_site present; fail fast on invalid input.

**Ref:** gazer-features.csv Input; Processing Flow 1

## Metadata

* URL: [AST-110](https://linear.app/astralcareermatch/issue/AST-110/sub-input-contract-and-playwright-entry)
* Identifier: [AST-110](https://linear.app/astralcareermatch/issue/AST-110/sub-input-contract-and-playwright-entry)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:34.699Z
* Updated: 2026-02-10T00:37:39.678Z

---

# Scrape Job Postings

**Scope:** Trigger pagination so all jobs are in DOM.

**Behavior:** navigate_and_wait_for_ready(page, job_site); then load_all_jobs(page, short_name).

**load_all_jobs:** Infinite scroll (scroll to bottom, detect new content, repeat — max scrolls from config); "Load More" buttons (click until exhausted — max clicks from config).

**Ref:** gazer-features.csv Trigger Pagination; load_all_jobs

## Metadata

* URL: [AST-111](https://linear.app/astralcareermatch/issue/AST-111/sub-load-all-jobs-pagination-and-ready-wait)
* Identifier: [AST-111](https://linear.app/astralcareermatch/issue/AST-111/sub-load-all-jobs-pagination-and-ready-wait)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:35.654Z
* Updated: 2026-02-10T00:37:39.588Z

---

# Scrape Job Postings

**Scope:** When parse_instructions contains no_jobs_message, check page text.

**If** message found in page text → legitimate no openings; return success with 0 jobs (do not parse). Caller records scan success and updates last_scan_at.

**Ref:** gazer-features.csv Validate Page Structure; no_jobs_message

## Metadata

* URL: [AST-112](https://linear.app/astralcareermatch/issue/AST-112/sub-no-jobs-message-early-exit)
* Identifier: [AST-112](https://linear.app/astralcareermatch/issue/AST-112/sub-no-jobs-message-early-exit)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:36.643Z
* Updated: 2026-02-10T00:37:39.531Z

---

# Scrape Job Postings

**Scope:** Extract culled DOM (scripts, styles, meta removed) and return for parsing.

**Function:** page_html = await extract_page_dom(page). Return (page_html, parse_instructions) to Parse Job Containers.

**Output:** On success (page_html, parse_instructions). On failure raise with error details.

**Ref:** gazer-features.csv Extract DOM; Pass to Parser

## Metadata

* URL: [AST-113](https://linear.app/astralcareermatch/issue/AST-113/sub-extract-page-dom-and-pass-to-parser)
* Identifier: [AST-113](https://linear.app/astralcareermatch/issue/AST-113/sub-extract-page-dom-and-pass-to-parser)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:38.127Z
* Updated: 2026-02-10T00:37:39.465Z

---

# Scrape Job Postings

**Scope:** Retry logic and error semantics.

**Retries:** navigate_and_wait_for_ready retries 2x on timeout/failure; after 2 retries raise. Exception caught by Track Scan Results.

**Scenarios:** Network/load → failure record, company stays WATCH. Bot detection → failure record; future bot mitigation out of scope.

**Ref:** gazer-features.csv Playwright Retry Logic; Error Scenarios

## Metadata

* URL: [AST-114](https://linear.app/astralcareermatch/issue/AST-114/sub-retry-and-error-handling)
* Identifier: [AST-114](https://linear.app/astralcareermatch/issue/AST-114/sub-retry-and-error-handling)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:39.158Z
* Updated: 2026-02-10T00:37:39.401Z

---

# Scrape Job Postings

**Scope:** Config-driven timeouts and limits for scrape.

**Keys (example):** concurrent_batch_size, page_load_timeout, scroll_max_attempts, load_more_max_clicks.

**Ref:** gazer-features.csv Configuration

## Metadata

* URL: [AST-115](https://linear.app/astralcareermatch/issue/AST-115/sub-config-for-timeouts-and-pagination-limits)
* Identifier: [AST-115](https://linear.app/astralcareermatch/issue/AST-115/sub-config-for-timeouts-and-pagination-limits)
* Status: Done
* Priority: Low
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:40.625Z
* Updated: 2026-02-10T00:37:39.350Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
