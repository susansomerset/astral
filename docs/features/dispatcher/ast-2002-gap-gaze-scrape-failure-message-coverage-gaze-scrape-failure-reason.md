# AST-2002 — Gap: gaze scrape failure_message coverage (gaze scrape failure reason)

<!-- linear-archive: AST-2002 archived 2026-10-16 -->

## Linear archive (AST-2002)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2002/gap-gaze-scrape-failure-message-coverage-gaze-scrape-failure-reason  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-1928 — [✅/Johnson] gaze COMPLETED: 1 error(s) / 83 processed | gaze-530061f0-7162-4c11-84b6-3878ce93319f  
**Blocked by / blocks / related:** parent: AST-1928

### Description

## What this implements

Test-gap sibling of AST-1997 (orphaned-bug fix-board TESTS: REVISE — not run inline on the fix child). Land repro coverage asserting the gaze scrape failure reason text, so `process_gazer_batch` can't regress to the generic "Scrape failed".

## As-is

`TestProcessGazerBatch` / `TestProcessGazerBatchDebugBranchCoverage` only assert status and call counts. Nothing asserts `failure_message` / outcome `message` text.

## To-be

At least one test fails against the pre-fix tree and passes once AST-1997 lands: `"Scrape failed: <ExceptionType>: <msg>"` (plus the empty-message form) and `"No job_site to scrape"`, on both `record_to_company_job_scan` and the returned outcomes, with debug=False and True. Bible entry names that coverage.

## Board brief (from AST-1997)

```
[board-betty] TESTS: REVISE
What: docs/test-bible/core/gazer.md (TestProcessGazerBatch / TestProcessGazerBatchDebugBranchCoverage) — missing coverage — no test asserts failure_message/outcome message text; need repro asserting "Scrape failed: RuntimeError: <msg>" (+ empty-str form) and "No job_site to scrape" on both record_to_company_job_scan and outcomes, debug=False and True. Existing nodes (status-only) and test_roster "scrape failed" asserts (_fetch_job_links_content) stay green; no integration scenario affected.
```

## Scope

## Component scope

* `tests/component/...` gazer batch test (modified or new, Betty's call): needs to assert that a raised scrape exception's text reaches `failure_message`.
* `docs/test-bible/core/gazer.md` (modified): name the new coverage.

## Technical scope

* Gazer batch component tests: new test case(s) asserting the failure message text on `record_to_company_job_scan` and outcomes, debug on and off.

## Boundaries

Does not implement the product change (AST-1997). No bible sweep.

## Git branch (authoritative)

parent `ftr/AST-1928-gaze-scrape-failure-reason`, child `sub/AST-1928/<this-id>-scrape-failure-message-coverage`.

### Comments

#### radia — 2026-10-06T05:24:06.849Z
[code-rubric] PROCEED (Commit: 44a2bce) bug-repro coverage landed

#### hedy — 2026-10-06T05:22:57.598Z
`origin/sub/AST-1928/AST-2002-scrape-failure-message-coverage` @ `5115871eb` · repro flips red→green

- `[bug-repro]` `tests/component/core/test_gazer_scrape_failure.py::TestProcessGazerBatchFailureMessage`: **2 failed** on pre-fix `gazer.py` (`f6f0a2b2d`), **2 passed** on `ftr` (AST-1997 `a00abace7`).
- Manifest (`docs/test-bible/core/gazer.md` § AST-2002, `run_component_tests.sh` with `ASTRAL_PYTHON`): **10 passed**.
- Merge-gate heads-up for merge-child: `validate-sub-log.sh` → `BLOCKED: missing plan(AST-2002): code(AST-2002): docs(AST-2002): resolve(AST-2002):`. The sub has a real `test()` + `merge-tests()`, so a `docs-acceptance` marker wouldn't fit and wouldn't clear `plan()`/`docs()` anyway. No commit made — gap-child gate handling is Chuckles' call.

#### betty — 2026-10-06T05:16:07.215Z
[bug-repro]
`origin/sub/AST-1928/AST-2002-scrape-failure-message-coverage` @ `5115871eb` · repro lands red, awaits fix

Repro: `tests/component/core/test_gazer_scrape_failure.py::TestProcessGazerBatchFailureMessage` (debug False/True). Red on `origin/ftr/AST-1928-gaze-scrape-failure-reason` (hard-coded "Scrape failed"). Manifest: `docs/test-bible/core/gazer.md` § AST-2002.

---

_Implementation detail may live in git history on `origin/dev`._
