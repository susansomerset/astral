# AST-1997 — Record real scrape exception in gaze failure_message (gaze scrape failure reason)

<!-- linear-archive: AST-1997 archived 2026-10-16 -->

## Linear archive (AST-1997)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1997/record-real-scrape-exception-in-gaze-failure-message-gaze-scrape  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1928 — [✅/Johnson] gaze COMPLETED: 1 error(s) / 83 processed | gaze-530061f0-7162-4c11-84b6-3878ce93319f  
**Blocked by / blocks / related:** parent: AST-1928

### Description

## What this implements

Make gaze scrape failures record their real reason. `process_gazer_batch` currently drops the `scrape_one` exception (only logged under `debug=True`) and writes a hard-coded `failure_message="Scrape failed"`, so a company parked in `ERROR_GAZE` (e.g. `trustmarkbenefits_com` in batch `gaze-530061f0-…`) can't be triaged. Visibility only — fixing any individual company's site/URL is out of scope.

## As-is

`asyncio.gather(..., return_exceptions=True)` captures the scrape exception, but the per-company failure branch records `failure_message="Scrape failed"` and outcome `message="Scrape failed"` regardless of cause. A company with an empty `job_site` (never scraped) gets the same generic message.

## To-be

`failure_message` (in `company_job_scan` and the outcome dict, hence the `-> ERROR_GAZE [...]` WARNING line) carries the actual reason, e.g. `Scrape failed: <ExceptionType>: <message>`, and a distinct message for "no job_site". AST-104's original spec recorded `failure_message=str(e)`.

## Scope

## Component scope

* `src/core/gazer.py` (modified): `process_gazer_batch` is where the scrape exception is dropped and the generic "Scrape failed" message is written.
* `tests/component/...` gazer batch test (modified or new, Betty's call): needs to assert that a raised scrape exception's text reaches `failure_message`.

## Technical scope

* `src/core/gazer.py`: modify `process_gazer_batch`. Keep each per-company scrape exception outside the debug-only block and use it for the `failure_message` and outcome `message` in the failure branch. Also tell "scrape raised" apart from "no job_site to scrape" so each failure records its real reason. No schema change, because `company_job_scan.failure_message` is already `TEXT`.

## Acceptance criteria

1. A company whose `scrape_one` raises gets `failure_message` containing the exception type and message, in both `company_job_scan` and the returned outcome.
2. A company with no `job_site` gets a distinct, explicit failure message.
3. `debug=False` / `debug=True` both record the same reason; debug logging otherwise unchanged.
4. Successful-scrape paths unchanged.

## Boundaries

Does not fix `trustmarkbenefits_com`'s site or URL. No schema change. No change to ERROR_GAZE state transitions.

## Notes for planning

No ancestor candidate was checked by Susan — work from this ticket and AST-1928's Description. Context (unchecked): `docs/features/gazer/ast-104-track-scan-results.md` (failure_message spec), `docs/features/foundation/ast-622-gazer-company-gaze-job-cache-debug-instrumentation.md` (debug-only scrape-failure log).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1928-gaze-scrape-failure-reason`, child `sub/AST-1928/<this-id>-surface-scrape-exception`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-06T05:20:08.330Z
[code-rubric] PROCEED (Commit: a00abace) scrape errors surfaced

#### joan — 2026-10-06T05:13:13.250Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T05:13:00.258Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/gazer.md (TestProcessGazerBatch / TestProcessGazerBatchDebugBranchCoverage) — missing coverage — no test asserts failure_message/outcome message text; need repro asserting "Scrape failed: RuntimeError: <msg>" (+ empty-str form) and "No job_site to scrape" on both record_to_company_job_scan and outcomes, debug=False and True. Existing nodes (status-only) and test_roster "scrape failed" asserts (_fetch_job_links_content) stay green; no integration scenario affected.

#### hedy — 2026-10-06T05:11:53.055Z
`origin/sub/AST-1928/AST-1997-surface-scrape-exception` @ `275837548` · surface real scrape failure reason

---

_Implementation detail may live in git history on `origin/dev`._
