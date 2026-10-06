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

---

## Bug: AST-1997 — Record real scrape exception in gaze failure_message

Parent: AST-1928 (bug mini-epic, `ftr/AST-1928-gaze-scrape-failure-reason`). Visibility only — no fix for any individual company's site/URL (e.g. `trustmarkbenefits_com`).

### As-is

`src/core/gazer.py` `process_gazer_batch` gathers `scrape_one` with `return_exceptions=True`. The exception is only used inside the `if debug:` loop (`outcome=f"scrape failed: {r!s}"`); the results loop then `continue`s past it. In the per-company loop, any company not in `results_by_short_name` records `failure_message="Scrape failed"` in `company_job_scan` and `message="Scrape failed"` in the outcome dict. `roster.py` (gaze branch, `_warn_company(short_name, error_state, o["message"])`) therefore logs `-> ERROR_GAZE [Scrape failed]` with no cause. A company with empty/blank `job_site` is never added to `to_scrape` and hits the same branch with the same message.

### To-be

- Scrape raised → `failure_message` and outcome `message` = `Scrape failed: <ExceptionType>: <str(e)>` (AST-104 Outcome 5 specified `failure_message=str(e)`; the prefix + type keep it triageable).
- No `job_site` → `failure_message` and outcome `message` = `No job_site to scrape`.
- Roster's `-> ERROR_GAZE [...]` WARNING carries the same text with no roster change.
- Same recorded reason for `debug=False` and `debug=True`.

### Repro

Fixture (no DB needed — patch the module functions, as `tests/component/core/test_gazer.py` already does):

```python
monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))
monkeypatch.setattr(gazer_mod, "scrape_one",
    AsyncMock(side_effect=RuntimeError("net::ERR_NAME_NOT_RESOLVED")))
record = MagicMock()
monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", record)

outcomes = await gazer_mod.process_gazer_batch(
    "batch-1",
    [{"short_name": "trustmarkbenefits_com", "job_site": "https://example.com/careers"},
     {"short_name": "nosite", "job_site": "  "}],
    debug=False,
)
```

As-is: both outcomes and both `record` calls carry `"Scrape failed"`. To-be: `trustmarkbenefits_com` → `"Scrape failed: RuntimeError: net::ERR_NAME_NOT_RESOLVED"`; `nosite` → `"No job_site to scrape"`.

### Root cause

The exception from `asyncio.gather` is consumed only by the debug-only logging loop and discarded by the results loop (`if isinstance(r, Exception): continue`). The failure branch has no access to it and no way to distinguish "scrape raised" from "never scraped", so it writes a hard-coded literal — drift from AST-104's `failure_message=str(e)` spec.

### Proposed change

Single file: `src/core/gazer.py`, function `process_gazer_batch`. No other function, file, schema, or config touched.

1. **Capture the reason in the existing results loop** (the `for i, r in enumerate(results):` loop that builds `results_by_short_name`). Add `scrape_errors: Dict[str, str] = {}` beside `results_by_short_name`. Replace `continue` on the exception branch with:
   - `sn, _ = to_scrape[i]`
   - `scrape_errors[sn] = f"Scrape failed: {type(r).__name__}: {r}" if str(r) else f"Scrape failed: {type(r).__name__}"` — the empty-message form covers exceptions such as a bare `asyncio.TimeoutError()` whose `str()` is `""` (avoids a trailing `": "`).
   - then `continue`.
   This runs regardless of `debug`, so both modes record the same reason (AC 3).
2. **Use it in the failure branch** (`if short_name not in results_by_short_name:`): compute `failure_message = scrape_errors.get(short_name, "No job_site to scrape")` once, and pass it to both `record_to_company_job_scan(..., failure_message=failure_message)` and the outcome dict `"message": failure_message`. The only way a non-empty `short_name` reaches this branch without an entry in `scrape_errors` is an empty/blank `job_site` (it was never added to `to_scrape`), so the default is exact, not a guess.
3. **Leave untouched:** the `if debug:` scrape-failure log loop (`scrape failed: {r!s}`, AST-622), the failure-branch debug log (`outcome="failure — scrape failed"` + `job_site=` detail), `total_found/new/duplicates=None`, `status="failure"`, and every success/parse/ingest path below.
4. **No truncation or normalization** of the exception text (Playwright messages can be multi-line with a call log). `failure_message` is `TEXT`; capping or flattening would be a heuristic needing Susan's approval — not part of this fix.

### Blast radius

- `src/core/roster.py` gaze branch reads `o["message"]` for the `-> ERROR_GAZE [...]` WARNING and transitions to `ROSTER_CONFIG["gaze"]["error_state"]` — text changes, state transition unchanged. No code change there.
- `company_job_scan.failure_message` rows for scrape failures change from the constant to the specific text; anything grouping on the literal `"Scrape failed"` would now see prefixed variants. No in-repo code matches on that literal (grep: only `gazer.py` itself).
- Tests: `tests/component/core/test_gazer.py` `test_records_scrape_parse_and_ingest_outcomes` and `test_failure_paths_without_debug` raise `RuntimeError("scrape failed")` but assert only `status`/call counts — expected to stay green. `tests/component/core/test_roster.py` stubs `process_gazer_batch` entirely — unaffected. New assertions on the message text are Betty's call (AST-1997 Component scope).

### What must still hold

- AST-104 Outcome 5 (network/Playwright exception): `status="failure"`, `total_found/new/duplicates=None`, state handling unchanged, `last_scan_at` not updated.
- AST-622 debug instrumentation: `debug=True` output byte-identical (`scrape failed: {r!s}` + `job_site=` detail; `failure — scrape failed` for un-logged failures).
- Success, no-containers, parse, and tracker-exception paths unchanged (AC 4).
- Companies with empty `short_name` still skipped; no schema change; no ERROR_GAZE transition change (Boundaries).
