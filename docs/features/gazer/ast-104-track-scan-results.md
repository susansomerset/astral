# AST-104 — Track Scan Results

<!-- linear-archive: AST-104 archived 2026-06-03 -->

## Linear archive (AST-104)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-104/track-scan-results  
**Status at archive:** Done  
**Project:** Astral Gazer  
**Assignee:** unassigned  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Record scan outcomes to company_job_scan table for audit trail and monitoring. Handles success/failure scenarios, updates company metadata, manages state transitions, and releases batch locks.

**Acceptance Criteria:**

**New Database Table:**

```sql
CREATE TABLE company_job_scan (
    batch_id TEXT NOT NULL,
    short_name TEXT NOT NULL,
    scan_completed_at TIMESTAMP NOT NULL,
    total_found INTEGER,
    new INTEGER,
    duplicates INTEGER,
    status TEXT NOT NULL,  -- 'success' or 'failure'
    failure_message TEXT,
    PRIMARY KEY (batch_id, short_name),
    FOREIGN KEY (short_name) REFERENCES company(short_name)
);
```

**Scan Outcomes:**

**1. Success - Jobs Found:**

```python
result = tracker.ingest_jobs(company, raw_job_listings, batch_id)

record_to_company_job_scan(
    batch_id=batch_id,
    short_name=company,
    scan_completed_at=now,
    total_found=len(raw_job_listings),
    new=result["new"],
    duplicates=result["duplicates"],
    status="success",
    failure_message=None
)

update_company(
    short_name=company,
    last_scan_at=now
)
# State stays WATCH
```

**2. Success - No Jobs (no_jobs_message found OR zero jobs in valid containers):**

```python
record_to_company_job_scan(
    batch_id=batch_id,
    short_name=company,
    scan_completed_at=now,
    total_found=0,
    new=0,
    duplicates=0,
    status="success",
    failure_message=None
)

update_company(
    short_name=company,
    last_scan_at=now
)
# State stays WATCH
```

**3. Failure - No Containers Found:**

```python
record_to_company_job_scan(
    batch_id=batch_id,
    short_name=company,
    scan_completed_at=now,
    total_found=0,
    new=None,
    duplicates=None,
    status="failure",
    failure_message="No containers found"
)

update_company(
    short_name=company,
    state="JOBSITE_WATCH_ISSUE"
)
# DON'T update last_scan_at (failed scan)
```

**4. Failure - Tracker Exception:**

```python
try:
    result = tracker.ingest_jobs(...)
except Exception as e:
    record_to_company_job_scan(
        batch_id=batch_id,
        short_name=company,
        scan_completed_at=now,
        total_found=len(raw_job_listings),
        new=None,
        duplicates=None,
        status="failure",
        failure_message=str(e)
    )
    
    # State stays WATCH (transient error, retry next batch)
    # DON'T update last_scan_at
```

**5. Failure - Network/Playwright Exception:**

```python
try:
    page_html = await scrape_job_postings(...)
except Exception as e:
    record_to_company_job_scan(
        batch_id=batch_id,
        short_name=company,
        scan_completed_at=now,
        total_found=None,
        new=None,
        duplicates=None,
        status="failure",
        failure_message=str(e)
    )
    
    # State stays WATCH
    # DON'T update last_scan_at
```

**Batch Cleanup:**

```python
# Always run after all companies in batch processed
database.clear_company_batch(batch_id)
# Sets batch_id=NULL, batch_created_at=NULL for all companies
# Allows retry in next batch if needed
```

**Scan Outcome Summary:**

| Scenario | Status | Total | New | Dupe | State | last_scan_at | Notes |
| -- | -- | -- | -- | -- | -- | -- | -- |
| Jobs found | success | N | X | Y | WATCH | ✓ updated | Normal |
| no_jobs_msg found | success | 0 | 0 | 0 | WATCH | ✓ updated | Valid empty |
| Empty containers | success | 0 | 0 | 0 | WATCH | ✓ updated | Valid empty |
| No containers | failure | 0 | NULL | NULL | JOBSITE_WATCH_ISSUE | ✗ not updated | Structural issue |
| Tracker exception | failure | N | NULL | NULL | WATCH | ✗ not updated | Transient |
| Network exception | failure | NULL | NULL | NULL | WATCH | ✗ not updated | Transient |

**State Transitions:**

WATCH → JOBSITE_WATCH_ISSUE:

* Trigger: No containers found + no_jobs_message not found
* Requires: Future AI diagnostic process to:
  * Discover actual no_jobs_message → back to WATCH
  * Determine site inactive → NO_JOB_SITE (human intervention)

**Company Table Updates:**

Success:

```python
UPDATE company SET 
    last_scan_at = ?,
    updated_at = ?
WHERE short_name = ?
```

Failure (JOBSITE_WATCH_ISSUE):

```python
UPDATE company SET
    state = 'JOBSITE_WATCH_ISSUE',
    state_changed_at = ?,
    updated_at = ?
WHERE short_name = ?
```

**Monitoring:**

* Query company_job_scan WHERE status='failure' for error review
* Repeat offenders (multiple failures) flagged for investigation
* Defensive monitoring = future Astral Monitor feature

**Database Functions:**

* record_to_company_job_scan(batch_id, short_name, ...) - Insert scan record
* update_company(short_name, last_scan_at=..., state=...) - Update company
* clear_company_batch(batch_id) - Release batch lock

**Traceability:**

* Full scan history in company_job_scan table
* batch_id links to state_history in job table (via Tracker.ingest_jobs)
* Complete lineage: Gazer batch → Company scans → Jobs created

**Error Handling Philosophy:**

* Transient failures (network, Tracker) → Keep in WATCH, retry next batch
* Structural failures (no containers) → Move to JOBSITE_WATCH_ISSUE, requires investigation
* Success with 0 jobs → Normal operation, not an error

**Future Enhancements:**

* Scan duration tracking (time taken per company)
* Job count trends over time (alert on significant drops)
* Automatic no_jobs_message discovery for JOBSITE_WATCH_ISSUE companies

# Track Scan Results

**Scope:** Define and create company_job_scan table.

**Columns:** batch_id, short_name, scan_completed_at, total_found, new, duplicates, status ('success'|'failure'), failure_message. PK (batch_id, short_name); FK short_name → company.
**Code:** Migrations or [database.py](<http://database.py>). Used for audit and monitoring.

**Ref:** gazer-features.csv New Database Table

## Metadata

* URL: [AST-123](https://linear.app/astralcareermatch/issue/AST-123/sub-company-job-scan-table-schema)
* Identifier: [AST-123](https://linear.app/astralcareermatch/issue/AST-123/sub-company-job-scan-table-schema)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:48.930Z
* Updated: 2026-02-10T00:37:38.766Z

---

# Track Scan Results

**Scope:** Data layer primitives for recording scan outcome and updating company. Data layer is dumb: it records what core passes; no outcome branching here.

**Functions:** record_to_company_job_scan(batch_id, short_name, scan_completed_at, total_found, new, duplicates, status, failure_message); update_company(short_name, last_scan_at=..., state=...). State values from config only (core passes them).

**Core** owns the outcome matrix (which state to transition to based on results); core calls these primitives with the correct arguments.

**Ref:** gazer-features.csv Database Functions; Company Table Updates; ASTRAL_CODE_RULES 2b

## Metadata

* URL: [AST-124](https://linear.app/astralcareermatch/issue/AST-124/sub-record-to-company-job-scan-and-update-company)
* Identifier: [AST-124](https://linear.app/astralcareermatch/issue/AST-124/sub-record-to-company-job-scan-and-update-company)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:49.941Z
* Updated: 2026-02-10T00:37:38.394Z

---

# Track Scan Results

**Scope:** Record success and update company for both success paths.

**Jobs found:** Record scan with total_found, new, duplicates from Tracker; status success; update last_scan_at; state stays WATCH.

**No jobs:** total_found=0, new=0, duplicates=0; status success; update last_scan_at; state stays WATCH.

**Ref:** gazer-features.csv Scan Outcomes 1 and 2

## Metadata

* URL: [AST-125](https://linear.app/astralcareermatch/issue/AST-125/sub-success-outcomes-jobs-found-and-no-jobs)
* Identifier: [AST-125](https://linear.app/astralcareermatch/issue/AST-125/sub-success-outcomes-jobs-found-and-no-jobs)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:50.951Z
* Updated: 2026-02-10T00:37:37.637Z

---

# Track Scan Results

**Scope:** When Parse Job Containers reports no containers (and no_jobs_message not found).

**Record:** status failure, failure_message "No containers found", total_found=0, new/duplicates NULL. **Company:** state JOBSITE_WATCH_ISSUE; do NOT update last_scan_at.

**Ref:** gazer-features.csv Failure - No Containers Found

## Metadata

* URL: [AST-126](https://linear.app/astralcareermatch/issue/AST-126/sub-failure-no-containers)
* Identifier: [AST-126](https://linear.app/astralcareermatch/issue/AST-126/sub-failure-no-containers)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:52.108Z
* Updated: 2026-02-10T00:37:37.599Z

---

# Track Scan Results

**Scope:** When Tracker.ingest_jobs raises or Scrape/Playwright raises.

**Tracker exception:** Record failure with total_found=len(raw_job_listings), new/duplicates NULL; state stays WATCH; do not update last_scan_at.

**Network/Playwright exception:** Record failure with total_found=None, new/duplicates NULL; state stays WATCH; do not update last_scan_at.

**Ref:** gazer-features.csv Failure - Tracker Exception; Failure - Network/Playwright

## Metadata

* URL: [AST-127](https://linear.app/astralcareermatch/issue/AST-127/sub-failure-tracker-or-network-exception)
* Identifier: [AST-127](https://linear.app/astralcareermatch/issue/AST-127/sub-failure-tracker-or-network-exception)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:53.195Z
* Updated: 2026-02-10T00:37:37.545Z

---

# Track Scan Results

**Scope:** Always release batch after all companies in batch processed.

**Action:** database.clear_company_batch(batch_id). Sets batch_id and batch_created_at NULL so companies can be retried. Run on success or failure path.

**Ref:** gazer-features.csv Batch Cleanup

## Metadata

* URL: [AST-128](https://linear.app/astralcareermatch/issue/AST-128/sub-clear-company-batch-after-batch)
* Identifier: [AST-128](https://linear.app/astralcareermatch/issue/AST-128/sub-clear-company-batch-after-batch)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:54.185Z
* Updated: 2026-02-10T00:37:37.353Z

---

# Track Scan Results

**Scope:** Core decides when to set state JOBSITE_WATCH_ISSUE (no containers found, no_jobs_message not found). State value must come from ASTRAL_CONFIG\["company_states"\] only—no hardcoded strings.

**Future:** AI diagnostic may move back to WATCH (discover no_jobs_message) or to NO_JOB_SITE (human intervention). Out of scope for this feature.

**Ref:** gazer-features.csv State Transitions; ASTRAL_CODE_RULES 2b

## Metadata

* URL: [AST-129](https://linear.app/astralcareermatch/issue/AST-129/sub-state-transition-to-jobsite-watch-issue)
* Identifier: [AST-129](https://linear.app/astralcareermatch/issue/AST-129/sub-state-transition-to-jobsite-watch-issue)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:55.281Z
* Updated: 2026-02-10T00:37:37.313Z

---

# Track Scan Results

**Scope:** Document outcome matrix (success/failure, state, last_scan_at) and monitoring use.

**Use:** Query company_job_scan WHERE status='failure' for review; repeat offenders for investigation. Defensive monitoring = future Astral Monitor.

**Ref:** gazer-features.csv Scan Outcome Summary; Monitoring

## Metadata

* URL: [AST-130](https://linear.app/astralcareermatch/issue/AST-130/sub-scan-outcome-summary-and-monitoring)
* Identifier: [AST-130](https://linear.app/astralcareermatch/issue/AST-130/sub-scan-outcome-summary-and-monitoring)
* Status: Done
* Priority: Low
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:56.311Z
* Updated: 2026-02-10T00:37:37.249Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
