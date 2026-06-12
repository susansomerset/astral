<!-- linear-archive: AST-337 archived 2026-06-03 -->

## Linear archive (AST-337)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-337/include-company-job-site-when-calling-qualify-job-listings  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Sometimes job_links are relative, and the agent needs to make a best effort to deduce the fully qualified job_link path.

### Comments

_No comments._

---

# AST-337 Include company job_site when calling qualify job listings

## Plan

### Context

When `qualify_job_listings` sends job listings to the Agent for evaluation, some job links are relative URLs (e.g., `/careers/job-123`). The Agent needs context to construct fully qualified URLs. Currently, only the relative job_link is provided; the Agent has no way to determine the base domain.

By appending the company's `job_site` URL (joined from the company table), the Agent can make a best-effort attempt to deduce the fully qualified job_link path. If the Agent cannot parse or construct a valid URL, that is reflected in the grade on the quality check vector.

### Design Decisions

**D1 — job_site only, not company_website.** Include only the job_site URL (where job listings are hosted), not the broader company website. This is more directly relevant to URL construction.

**D2 — Per-job data element in raw_job_listings.** Add `job_site` as a flat field in each job object in the raw_job_listings array sent to the Agent, similar to job_title, job_link, etc.

**D3 — Inner join on company.short_name.** Join the job record with the company table using `job.company = company.short_name`. Per requirements, this join will always succeed (no error handling needed).

**D4 — Database layer handles company lookup.** Add a database.py function to fetch the company.job_site column by short_name. This is a direct column lookup, not a coat-check pattern (job_site is a concrete entity field, not lazy-loaded data). Per ASTRAL_CODE_RULES 1.1 (exception), we allow this direct data layer → core layer interaction for simple field retrieval.

**D5 — No schema changes.** The response_schema for qualify_job_listings remains unchanged; job_site is input data only, not part of the Agent's response.

---

### Step 1: Job data already enriched with job_site via get_job_batch

**File:** `src/data/database.py`

**Status:** ✅ COMPLETE — Susan updated `get_job_batch()` to include job_site from the company table via inner join on company.short_name. Jobs returned from `get_job_batch()` now include the `job_site` field.

**No additional database changes needed.**

---

### Step 2: Update qualify_job_listings in consult.py to pass enriched jobs to Agent

**File:** `src/core/consult.py`

**Function:** `qualify_job_listings(batch_id, jobs, ctx, debug)`

**Change:** Updated the `assemble()` function to format job_site and raw_job_listing together for each job:

```python
def assemble(jobs):
    raw_htmls = [
        f"job_site: {j.get('job_site', '')}\nraw_job_listing: {j.get('job_data', {}).get('raw_job_listing', '')}"
        for j in jobs
    ]
    astral_ids = [j["astral_job_id"] for j in jobs]
    return enumerate_array("JOB LISTINGS", raw_htmls, index_key="astral_job_id", index_values=astral_ids)
```

This ensures each job listing includes the job_site URL, allowing the Agent to construct fully qualified URLs from relative links.

**Commit:** `dde4e77`

---

### Step 3: Verify Agent receives job_site in raw_job_listings

**File:** Agent prompt (task database / agent_task table)

**Change:** No code change needed; verify that the prompt for qualify_job_listings can access and use the job_site field when constructing URLs.

**Instruction template:** The existing prompt should already instruct the Agent on URL construction. If not, the prompt can be updated separately to explain how to use job_site with relative links.

---

## Files Changed

| File | Changes |
|------|---------|
| `src/data/database.py` | ✅ COMPLETE — `get_job_batch()` updated to include job_site from company table via inner join |
| `src/core/consult.py` | ✅ COMPLETE — Updated `assemble()` function to format job_site with each raw_job_listing for Agent |

---

## Implementation Notes

- **Inner join confidence:** Per requirements, the join always succeeds (company records exist for all jobs).
- **Grade reflection:** If the Agent cannot parse job_site or construct a URL, the grade on the quality vector should reflect that.
- **No prompt changes:** The Agent's prompt instructions should already guide URL construction; this change just provides the data.
- **Backward compatible:** Existing jobs without job_site will gracefully skip enrichment; Agent receives what's available.
- **ASTRAL_CODE_RULES 1.1 exception:** Direct column lookup from database layer (job_site is a concrete entity field, not lazy-loaded data). This is allowed per code rules exception for simple field retrieval.

---

## Testing

- Verify that jobs in qualify_job_listings include job_site field
- Confirm Agent receives job_site in raw_job_listings data
- Spot-check that Agent can construct qualified URLs from relative links + job_site

---

## Review

**Commits:** `1241d41`, `dde4e77` (fix applied)
**Branch:** `dev`
**Reviewed:** 2026-03-22

---

## What's Solid

- The approach of enriching via JOIN in `get_job_batch` is the right call — it's a single query change, no new functions, no new imports, zero ceremony. The plan identified that the data was already available and avoided over-engineering.
- Inner join is correct here: every job has a company, every company has a `short_name`. The join condition `j.company = c.short_name` matches the existing FK pattern used throughout `roster.py` and `gazer.py`.
- `_job_row_to_dict` uses `row.keys()` from `sqlite3.Row`, so the extra `c.job_site` column is picked up automatically — no schema or dict-building changes needed.
- D5 (no schema changes) is correct — `job_site` is input-only, not part of the Agent's response.

---

## Issues Resolved

### Issue 1 — job_site not in live_content ✅ FIXED

**Resolution:** Updated `assemble()` function in `qualify_job_listings` to prepend job_site to each raw_job_listing:

```python
raw_htmls = [
    f"job_site: {j.get('job_site', '')}\nraw_job_listing: {j.get('job_data', {}).get('raw_job_listing', '')}"
    for j in jobs
]
```

Agent now receives job_site for each job listing and can construct fully qualified URLs from relative links.

**Commit:** `dde4e77`

### Issue 2 — get_job_batch JOIN affects all callers ℹ️

**Status:** Advisory only. No action taken. The JOIN is benign — extra `job_site` column is harmless, and every job batch caller works correctly. Performance impact is negligible (indexed join on `short_name`).

If orphan jobs ever appear in production, recommend switching to LEFT JOIN for safety.

### Issue 3 — Plan/doc inaccuracies ✅ UPDATED

**Resolution:** Updated plan text to reflect actual implementation:
- D4: Now correctly states that `get_job_batch()` was updated with a JOIN, not that a new function was added
- Files Changed: Updated to reflect that consult.py now includes the job_site formatting change
- Step 2: Updated to describe the actual assemble() function fix

---

## Recommended Actions

| # | Severity | Status |
|---|----------|--------|
| 1 | Fix now | ✅ FIXED — job_site now included in live_content via assemble() function |
| 2 | Advisory | OK — LEFT JOIN can be considered for orphan jobs in future |
| 3 | Advisory | ✅ FIXED — Plan text updated to match implementation |

