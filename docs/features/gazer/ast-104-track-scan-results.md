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

## Joan fix-board (AST-1997)

Registry skim (`canon/docs/DIRECTIVES-DIRECTORY.md` + grep on `canon/directives/active/` and `canon/statutes/astral/**` for gazer / `failure_message` / `ERROR_GAZE`): nothing in force fixes the literal `"Scrape failed"` or forbids storing exception text in `company_job_scan.failure_message`. The change is single-file `gazer.py`, keeps AST-622 debug paths byte-identical per plan, does not change transitions (`astral.state.core-decides-transitions` / roster wiring), and only enriches the roster warning "why" (`stat.logging.warning` shape) — i.e. conformance with archived AST-104 Outcome 5 intent, not a new carve-out or statute edit. No frozen Canon Scope on the bug ticket; overlap triage only.

```
[board-joan]  CANON: OK
```

## Radia review (AST-1997)

```
[code-rubric]
**Ticket:** AST-1997
**Publish ref:** `a00abace71dc3d2e55a7c644850b5809235752ad` (`origin/sub/AST-1928/AST-1997-surface-scrape-exception`)
**Diff reviewed:** `origin/ftr/AST-1928-gaze-scrape-failure-reason...origin/sub/AST-1928/AST-1997-surface-scrape-exception`
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`
**Overall:** CLEAN

## Canon scores

Frozen **Canon Scope** on AST-1997 is empty (Linear Description has no directive list; Joan fix-board: “No frozen Canon Scope on the bug ticket; overlap triage only”). No directive rows on the frozen list; roll-up from canon grades is vacuously clean.

**Board overlap (informational only — not on frozen list):**

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| `astral.state.core-decides-transitions` | A | | No roster/state transition logic changed; only `failure_message` / outcome `message` text in `process_gazer_batch`. |
| `stat.logging.warning` | A | | Richer per-item “why” on gaze failure path; roster still logs `-> ERROR_GAZE [message]` — conforms to who+why intent. |
| `patt.entity.batch-processing` | X | | Gazer batch shape unchanged; not a batch-claim/dispatch change. |

## Column diff vs plan stage

`no plan-stage validate-plan scores attached` — fix-board Joan `CANON: OK`; Radia aligns with board triage, not re-litigating F2.

## Frame diff

(none)

## Fix-specific checks

- **`[bug-repro]`:** not applicable — clean board opt-out (`[board-betty] TESTS: REVISE` routed to sibling **AST-2002**; no `[bug-repro]` on this tip per spawn).
- **`## What must still hold`:** OK — traced on product diff (`src/core/gazer.py` only):
  - AST-104 Outcome 5 scrape-failure shape: `status="failure"`, `total_found/new/duplicates=None`; `update_company_last_scan_at` still only on success path below the edited branch.
  - AST-622: `if debug:` scrape-failure loop (`scrape failed: {r!s}`, `job_site=`) untouched; failure-branch debug still `outcome="failure — scrape failed"` + `job_site=` for non-logged failures (e.g. blank `job_site`).
  - Success / parse / ingest / no-containers paths: no edits in diff hunks.
  - Empty `short_name` still `continue`; no schema or ERROR_GAZE transition change.

## Findings

**fix-now:** none

**discuss:**
- **Unrelated doc hunk on publish ref** — `docs/features/candidate/ast-1598-job-and-app-log-candidate-id.md` gains an AST-1987 epic `## Threads` mirror; plan-fix scoped **only** `src/core/gazer.py` + `ast-104` bug patch. @susan: keep the stray mirror on this sub for registry convenience, or drop it before merge? **Default:** revert that file to `origin/ftr/AST-1928-gaze-scrape-failure-reason` on the next doc-only commit so the bug branch stays single-purpose (no product impact).

**advisory:**
- Three-dot diff product footprint is one commit’s worth in `gazer.py` (`scrape_errors` map + `failure_message` / outcome `message`); matches `## Proposed change` (including empty-`str(e)` `TimeoutError` form).
- Message assertions / `[bug-repro]` live on **AST-2002** per Betty board; existing gazer tests that only check `status`/counts remain valid per plan blast radius.
- Publish tip (`a00abace`) is ahead of Hedy’s Linear note (`275837548`); review used current `origin/sub/...` tip after fetch.

## What’s solid

- Exception capture uses `to_scrape[i]` index parity with `asyncio.gather` — correct mapping per company.
- `scrape_errors.get(short_name, "No job_site to scrape")` cleanly separates scrape-raised vs never-scraped blank `job_site`.
- Debug and non-debug paths share the same stored reason without altering AST-622 log strings.

## Recommended actions

| Action | Item |
|--------|------|
| none (ship product) | 0 fix-now |
| optional doc hygiene | discuss default: revert unrelated `ast-1598` threads hunk |

## Chuckles disposition

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal (AST-1928 mini-epic, `ftr` live) | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing**; `resolve-child` **skipped**. Test-gap sibling **AST-2002** remains separate. |

context_tokens≈9500
```

```
[code-rubric] PROCEED (Commit: a00abace) scrape errors surfaced
```

**Chuckles note on discuss item:** the `ast-1598` hunk is `40d0fe70e`, already on `origin/dev` (pulled in by sync-child); zero diff vs dev — no revert needed.

```

**Test delivery (AST-1997):** docs-acceptance on this child — no test-tree change here; the `[bug-repro]` (`tests/component/core/test_gazer_scrape_failure.py`) is carried by test-gap sibling AST-2002 per fix-board TESTS: REVISE routing.

## Bug: AST-2002 — gaze scrape failure_message coverage (test-gap sibling of AST-1997)

Plan: fix-board on AST-1997 returned `[board-betty] TESTS: REVISE` — no test asserted `failure_message` / outcome `message` text in `process_gazer_batch`. Orphaned-bug routing filed this gap child instead of running qa-fix inline on AST-1997. Deliverable: a `[bug-repro]` asserting `Scrape failed: <ExceptionType>: <msg>` (plus the empty-message form) and `No job_site to scrape` on both `record_to_company_job_scan` and outcomes, debug=False and True; red on pre-fix ftr, green once AST-1997 lands. Bible: `docs/test-bible/core/gazer.md` § AST-2002.

**Product delivery (AST-2002):** none — test-only gap child; product change is AST-1997 (`src/core/gazer.py`). Repro: `tests/component/core/test_gazer_scrape_failure.py::TestProcessGazerBatchFailureMessage` (red pre-fix, green on ftr — verified in test-fix).

## Radia review (AST-2002)

```
[code-rubric]
**Ticket:** AST-2002
**Publish ref:** `44a2bce7da1dedd1d394bff2f767f3fa8f192cce` (`origin/sub/AST-1928/AST-2002-scrape-failure-message-coverage`)
**Diff reviewed:** `origin/ftr/AST-1928-gaze-scrape-failure-reason...origin/sub/AST-1928/AST-2002-scrape-failure-message-coverage`
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`
**Overall:** CLEAN

## Canon scores

Frozen **Canon Scope** on AST-2002 is empty (Linear Description has no directive list; test-gap child scoped to tests + bible only). No directive rows on the frozen list; roll-up from canon grades is vacuously clean.

**Board overlap (informational only — not on frozen list):**

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| `patt.test.component-isolation` / bible hygiene | A | | Mocks `check_connectivity`, `scrape_one`, `record_to_company_job_scan`; no DB; bible § AST-2002 names node + manifest. |
| `stat.logging.warning` | X | | Product path under test, not modified on this tip. |

## Column diff vs plan stage

`no plan-stage validate-plan scores attached` — gap child filed from AST-1997 fix-board Betty `TESTS: REVISE`; no Joan F3 column on this ticket.

## Frame diff

(none)

## Fix-specific checks

- **`[bug-repro]`:** OK — `tests/component/core/test_gazer_scrape_failure.py::TestProcessGazerBatchFailureMessage` pins concrete `_EXPECTED` strings aligned with AST-1997 plan § Proposed change / To-be (`RuntimeError` with message, bare `TimeoutError` → no trailing `": "`, `No job_site to scrape`). Asserts both outcome `message` and `record_to_company_job_scan(..., failure_message=…)`; `@pytest.mark.parametrize("debug", [False, True])`. Would fail on pre-fix `process_gazer_batch` (hard-coded `"Scrape failed"` for scrape failures and nosite); credible repro-first per Betty thread + Hedy test-fix note. Module docstring names bug-repro; file lacks a first-line `# [bug-repro]` tag (see advisory).
- **`## What must still hold`:** **discuss (process)** — plan-fix patch on `ast-104-track-scan-results.md` § Bug: AST-2002 has no `## What must still hold` block (only deliverable summary). For a test-only gap child, implicit bar is “no `src/**` change; existing gazer/roster nodes stay green.” **Default:** treat Boundaries + bible manifest as sufficient; no recall unless Chuckles wants a formal hold list on gap tickets.

**Trace against implicit holds (on diff):** no `src/**` changes; bible manifest runs new node plus existing `TestProcessGazerBatch` / `TestProcessGazerBatchDebugBranchCoverage` — matches board brief.

## Findings

**fix-now:** none

**discuss:**
- **Missing `## What must still hold` in plan-fix patch** — see fix-specific check; **Default:** no engineer action before UT.

**advisory:**
- Add optional first-line `# [bug-repro]` (or docstring tag) in `test_gazer_scrape_failure.py` for parity with qa-fix grep conventions; not required for assertion quality.
- Hedy `validate-sub-log` heads-up (`plan`/`docs`/`resolve` tokens on gap child) — Chuckles merge-child / commit-shape only; not a Radia product finding.
- Tip `44a2bce` includes `code(AST-2002): no product change` after Betty qa-fix @ `5115871eb`; review used current `origin/sub/...` after fetch.

## What’s solid

- One parametrized test covers three failure shapes and both debug modes without tautology.
- `_log` mock prevents `debug=True` from leaking global debug state into later tests.
- Bible § AST-2002 documents red/green contract and manifest command.

## Recommended actions

| Action | Item |
|--------|------|
| none (ship tests) | 0 fix-now |
| optional | first-line `[bug-repro]` tag; formal hold list on gap plan template |

## Chuckles disposition

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal (AST-1928 mini-epic, `ftr` live) | → **Review Posted** → §3h clean-review shortcut → **User Testing**; `resolve-child` **skipped** unless Susan wants the discuss default acted on. Stack assumes AST-1997 product already on `origin/ftr/AST-1928-gaze-scrape-failure-reason`. |

context_tokens≈7200
```

```
[code-rubric] PROCEED (Commit: 44a2bce) bug-repro coverage landed
```
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Hedy | engineer | `/home/susan/.cursor/chats/1e7a3f1eafdb0b7ecc7478b0bd30c5d1/c923fd97-cda0-45a8-9494-79a26e330115/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/3bd55873-7322-4849-a902-774af7ddab2a/store.db` |
| Radia | review | `/home/susan/.cursor/chats/1e7a3f1eafdb0b7ecc7478b0bd30c5d1/858b2340-c402-46b3-ab4f-e21495b6633a/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1928 (parent) | ftr/AST-1928-gaze-scrape-failure-reason |
| AST-1997 | sub/AST-1928/AST-1997-surface-scrape-exception |
| AST-2002 | sub/AST-1928/AST-2002-scrape-failure-message-coverage |

**Epic worktree:** `astral-AST-1928/` — one active sub checked out at a time.
