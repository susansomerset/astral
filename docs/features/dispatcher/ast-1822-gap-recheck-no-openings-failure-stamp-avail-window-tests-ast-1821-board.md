# AST-1822 — gap: recheck_no_openings failure-stamp + Avail window tests (AST-1821 board)

<!-- linear-archive: AST-1822 archived 2026-10-07 -->

## Linear archive (AST-1822)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1822/gap-recheck-no-openings-failure-stamp-avail-window-tests-ast-1821  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1820 — recheck_no_openings avail count  
**Blocked by / blocks / related:** parent: AST-1820

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1821. Fix the recheck failure-path tests the new `last_scan_at` stamps break, and cover the Avail repro: NO_OPENINGS Avail with `score_floor` set still honors the `last_scan_at` window, a `{base}_RETRY` trigger resolves `batch_criteria` through the base state, and the new `scan_interval_hours` kwarg on `count_companies_in_state_with_score_floor` filters.

## Scope

### Component scope

* `tests/component/core/test_roster.py` (modified): `TestProcessRecheckNoOpenings::test_guards_missing_fields` / `test_playwright_failure_no_state_change` patch and assert `update_company_last_scan_at` on the failure paths. The short_name guard stays unstamped.
* `tests/component/data/test_dispatch_tasks.py` (or wherever the `count_eligible_for_dispatch_task` tests live) (modified): Avail cases for `score_floor` + `last_scan_at` window, a `_RETRY` trigger base-state lookup, and the `scan_interval_hours` kwarg.
* `docs/test-bible/core/roster.md` and `docs/test-bible/data/database.md` (modified): bible entries for the new and revised coverage.

### Technical scope

* Roster recheck tests: revised cases asserting the failure paths stamp `last_scan_at`, with the short_name guard untouched.
* Dispatch-task count tests: new cases that fail against the pre-AST-1821 product and pass after it lands.
* Test bible: modified entries naming the coverage.

## Boundaries

Test and bible only; product code stays on AST-1821. Betty lands the tests (engineers are banned from the test tree).

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE: docs/test-bible/core/roster.md + docs/test-bible/data/database.md (test_dispatch_tasks), broken test + missing coverage (see the AST-1821 comment). Plan doc: docs/features/roster/ast-460-recheck-no-openings-24h-playwright-recheck-for-no-openings.md.

## Git branch (authoritative)

Parent `ftr/AST-1820-recheck-no-openings-avail-count`, child `sub/AST-1820/AST-1822-recheck-no-openings-avail-count-tests`.

### Comments

#### radia — 2026-09-27T06:35:30.877Z
[code-rubric] REVIEW (Commit: 9d554fcd) Strip the AST-1768 carry before dev. fix-now: merge-tests brought in AST-1768 frontend/api tests and bible entries whose product is not on dev. In-scope tests are solid; repro gate OK.

#### betty — 2026-09-27T06:32:32.482Z
[bug-repro]
`origin/sub/AST-1820/AST-1822-recheck-no-openings-avail-count-tests` @ `93b10c43` · repro red pre-fix, green on ftr

Repro gate (manifest = plan § Bug: AST-1822): pre-fix product `0d08e9b1` → 7 failed / 6 passed (all 7 new/revised nodes red for the planned reason: stamp mock not called ×2, Avail 3≠2 / 3≠1 / 3≠2 / 2≠1, `TypeError` on `scan_interval_hours`). Post-fix `origin/ftr/AST-1820-recheck-no-openings-avail-count` @ `c9819bc6` → 13 passed. Sub ref is still on the pre-fix base, so merge `origin/ftr/...` before running.

#### joan — 2026-09-27T06:29:20.195Z
[board-joan]  CANON: OK

Test and bible only: this locks in AST-1821 conformance with `patt.entity.batch-criteria`. No directive amendment, no F3.

#### betty — 2026-09-27T06:28:03.100Z
[board-betty] TESTS: OK

#### hedy — 2026-09-27T06:27:24.322Z
`origin/sub/AST-1820/AST-1822-recheck-no-openings-avail-count-tests` @ `5ee200b2` · test nodes + bible planned

---

_Implementation detail may live in git history on `origin/dev`._
