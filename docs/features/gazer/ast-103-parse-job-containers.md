# AST-103 — Parse Job Containers

<!-- linear-archive: AST-103 archived 2026-06-03 -->

## Linear archive (AST-103)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-103/parse-job-containers  
**Status at archive:** Done  
**Project:** Astral Gazer  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Extract individual job listings from page DOM using configured selectors. Implements two-stage parsing: container extraction followed by job_tag extraction. Validates structure and generates raw HTML job listings for Tracker ingestion.

**Acceptance Criteria:**

**New Playwright Function:**

```python
parse_by_element(
    source: Union[Page, str],
    element: str,
    outer: bool = True
) -> List[str]
```

**Parameters:**

* source: Either Page object or HTML string
* element: CSS selector (e.g., "div.job-list", "div.jobby")
* outer: True = outerHTML, False = innerHTML

**Returns:**

* List\[str\] of HTML strings
* Empty list if no matches

**Input:**

* page_html: str (culled HTML from Scrape Job Postings)
* parse_instructions: Dict with:
  * container: str (CSS selector for job list container)
  * job_tag: str (CSS selector for individual job elements)

**Two-Stage Parsing:**

**Stage 1 - Extract Containers (innerHTML):**

```python
job_lists = parse_by_element(page_html, container_selector, outer=False)
# Returns: ["<container1 innerHTML>", "<container2 innerHTML>", ...]
```

**Validation - No Containers Found:**

```python
if len(job_lists) == 0:
    # Container selector matched zero elements
    
    # Check if no_jobs_message explains it
    if no_jobs_message and no_jobs_message in page_html:
        record_scan_success(total_found=0, new=0, duplicates=0)
        update_company(last_scan_at=now)
        return
    else:
        # Structural problem - containers should exist
        record_scan_failure(
            total_found=0,
            failure_message="No containers found"
        )
        update_company(state="JOBSITE_WATCH_ISSUE")
        return
```

**Stage 2 - Extract Job Tags (outerHTML):**

```python
all_raw_job_listings = []
for job_list_html in job_lists:
    if not job_list_html.strip():
        continue  # Skip empty containers
    
    job_items = parse_by_element(job_list_html, job_tag_selector, outer=True)
    all_raw_job_listings.extend(job_items)
# Returns: ["<div class='jobby'>A</div>", "<div class='jobby'>B</div>", ...]
```

**Character Accounting:**
Sum of all job_items outerHTML characters should equal total innerHTML of all containers (minus empty containers).

**Example:**

```html
<!-- Input: page_html contains -->
<div class="job-list">
  <div class="jobby">Job A</div>
  <div class="jobby">Job B</div>
</div>
<div class="job-list">
  <div class="jobby">Job C</div>
</div>

<!-- Stage 1: Extract containers (innerHTML) -->
job_lists = [
  "<div class='jobby'>Job A</div><div class='jobby'>Job B</div>",
  "<div class='jobby'>Job C</div>"
]

<!-- Stage 2: Extract job_tags (outerHTML) -->
all_raw_job_listings = [
  "<div class='jobby'>Job A</div>",
  "<div class='jobby'>Job B</div>",
  "<div class='jobby'>Job C</div>"
]
```

**Send to Tracker:**

```python
result = tracker.ingest_jobs(
    company=company["short_name"],
    raw_job_listings=all_raw_job_listings,
    batch_id=batch_id
)
# Returns: {"new": X, "duplicates": Y}
```

**Edge Cases:**

**Multiple Containers (Departments/Locations):**

* Parse all containers found
* Combine all job_tags into single list
* Tracker treats as flat list (no department metadata yet)

**Empty Containers:**

* Skip silently (not an error)
* Only error if NO containers found

**Zero Jobs in Valid Containers:**

```python
if len(all_raw_job_listings) == 0:
    # Legitimate "no openings" scenario
    # Containers exist but no jobs currently
    record_scan_success(total_found=0, new=0, duplicates=0)
    update_company(last_scan_at=now)
    return
```

**Implementation in **[**playwright.py**](<http://playwright.py>)**:**

parse_by_element() needs to:

1. Detect source type (Page object vs string)
2. Apply CSS selector
3. Extract innerHTML vs outerHTML based on flag
4. Return list of HTML strings

**Browser Context:**

* parse_by_element() with Page object executes JavaScript in browser
* parse_by_element() with string uses BeautifulSoup or similar parser

**Output:**

* all_raw_job_listings: List\[str\] (raw HTML job listings)
* Ready for Tracker.ingest_jobs()

**Error Handling:**

* If selector syntax invalid: Exception raised, caught by Track Scan Results
* If parsing fails: Exception raised
* Gazer does not retry parsing errors (structural issue)

**Future Enhancement:**

* Extract metadata from containers (department, location) for job enrichment
* Support for nested containers (e.g., department → location → jobs)

# Parse Job Containers

**Scope:** New Playwright/parser helper for selector-based extraction. Lives in src/external/playwright.py (parsing by HTML tags).

**Signature:** parse_by_element(source: Union\[Page, str\], element: str, outer: bool = True) -> List\[str\].

**Parameters:** source = Page or HTML string; element = CSS selector; outer = True for outerHTML, False for innerHTML.

**Returns:** List of HTML strings; empty if no matches. When source is string, use BeautifulSoup (or equivalent); when Page, use browser.

**DRY:** One function, two source types (Page vs string)—same selector logic, no duplication. Comment in code that the string-vs-Page branching is intentional for DRY.

**Ref:** gazer-features.csv New Playwright Function; Implementation

## Metadata

* URL: [AST-116](https://linear.app/astralcareermatch/issue/AST-116/sub-parse-by-element-signature-and-behavior)
* Identifier: [AST-116](https://linear.app/astralcareermatch/issue/AST-116/sub-parse-by-element-signature-and-behavior)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:41.629Z
* Updated: 2026-02-10T00:37:39.284Z

---

# Parse Job Containers

**Scope:** First stage of two-stage parse: extract container regions.

**Input:** page_html, parse_instructions\["container"\] (CSS selector).

**Action:** job_lists = parse_by_element(page_html, container_selector, outer=False). Result: list of innerHTML strings per container.

**Ref:** gazer-features.csv Stage 1

## Metadata

* URL: [AST-117](https://linear.app/astralcareermatch/issue/AST-117/sub-stage-1-extract-containers-innerhtml)
* Identifier: [AST-117](https://linear.app/astralcareermatch/issue/AST-117/sub-stage-1-extract-containers-innerhtml)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:42.653Z
* Updated: 2026-02-10T00:37:39.234Z

---

# Parse Job Containers

**Scope:** When zero containers matched: distinguish no-jobs vs structural problem.

**If** no_jobs_message present and in page_html → record success 0 jobs, update last_scan_at, return. **Else** record scan failure (e.g. "No containers found"), set company state to value from ASTRAL_CONFIG\["company_states"\] (e.g. JOBSITE_WATCH_ISSUE)—no hardcoded state strings.

**Ref:** gazer-features.csv Validation - No Containers Found; ASTRAL_CODE_RULES 2b

## Metadata

* URL: [AST-118](https://linear.app/astralcareermatch/issue/AST-118/sub-no-containers-found-validation-and-state)
* Identifier: [AST-118](https://linear.app/astralcareermatch/issue/AST-118/sub-no-containers-found-validation-and-state)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:43.725Z
* Updated: 2026-02-10T00:37:39.173Z

---

# Parse Job Containers

**Scope:** Second stage: from each container innerHTML, extract job elements.

**Input:** job_lists from Stage 1; parse_instructions\["job_tag"\] (CSS selector).

**Action:** For each non-empty job_list_html, parse_by_element(..., outer=True); concatenate all results into all_raw_job_listings. Skip empty containers.

**Output:** List of raw HTML job listing strings for Tracker.

**Ref:** gazer-features.csv Stage 2

## Metadata

* URL: [AST-119](https://linear.app/astralcareermatch/issue/AST-119/sub-stage-2-extract-job-tags-outerhtml-and-combine)
* Identifier: [AST-119](https://linear.app/astralcareermatch/issue/AST-119/sub-stage-2-extract-job-tags-outerhtml-and-combine)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:44.982Z
* Updated: 2026-02-10T00:37:39.083Z

---

# Parse Job Containers

**Scope:** When containers exist but all_raw_job_listings is empty.

**Action:** Legitimate no openings; record scan success total_found=0, new=0, duplicates=0; update company last_scan_at; state stays WATCH.

**Ref:** gazer-features.csv Zero Jobs in Valid Containers

## Metadata

* URL: [AST-120](https://linear.app/astralcareermatch/issue/AST-120/sub-zero-jobs-in-valid-containers)
* Identifier: [AST-120](https://linear.app/astralcareermatch/issue/AST-120/sub-zero-jobs-in-valid-containers)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:45.930Z
* Updated: 2026-02-10T00:37:39.021Z

---

# Parse Job Containers

**Scope:** Send extracted raw job listings to Tracker.

**Call:** tracker.ingest_jobs(company=short_name, raw_job_listings=all_raw_job_listings, batch_id=batch_id). Returns {"new": X, "duplicates": Y}.

**Contract:** Gazer passes list; Tracker returns counts. Exceptions handled by Track Scan Results.

**Ref:** gazer-features.csv Send to Tracker

## Metadata

* URL: [AST-121](https://linear.app/astralcareermatch/issue/AST-121/sub-call-tracker-ingest-jobs)
* Identifier: [AST-121](https://linear.app/astralcareermatch/issue/AST-121/sub-call-tracker-ingest-jobs)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:46.921Z
* Updated: 2026-02-10T00:37:38.917Z

---

# Parse Job Containers

**Scope:** Edge cases for container list.

**Multiple containers:** Parse all; combine job_tags into single list (no department metadata yet). **Empty containers:** Skip silently; only error when NO containers found.

**Ref:** gazer-features.csv Edge Cases

## Metadata

* URL: [AST-122](https://linear.app/astralcareermatch/issue/AST-122/sub-multiple-and-empty-containers)
* Identifier: [AST-122](https://linear.app/astralcareermatch/issue/AST-122/sub-multiple-and-empty-containers)
* Status: Done
* Priority: Low
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:47.935Z
* Updated: 2026-02-10T00:37:38.823Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
