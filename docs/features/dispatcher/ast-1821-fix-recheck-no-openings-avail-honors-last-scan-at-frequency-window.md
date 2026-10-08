# AST-1821 — fix: recheck_no_openings Avail honors last_scan_at frequency window

<!-- linear-archive: AST-1821 archived 2026-10-07 -->

## Linear archive (AST-1821)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1821/fix-recheck-no-openings-avail-honors-last-scan-at-frequency-window  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1820 — recheck_no_openings avail count  
**Blocked by / blocks / related:** parent: AST-1820

### Description

## What this implements

`recheck_no_openings` Available count follows the row's frequency: a NO_OPENINGS company scanned within the window (`freq_hrs`, or the 24h state default when 0) is neither counted nor claimed, including companies whose last recheck attempt failed. Every count path (admin list, `get_due_tasks`, dispatcher loop) matches the claim in `set_company_batch`.

## Scope

## Component scope

* `src/core/roster.py` (modified): `process_recheck_no_openings` decides whether a failed recheck stamps `company.last_scan_at`. That is the likely reason the count never drops.
* `src/data/database.py` (modified): `count_eligible_for_dispatch_task` (company branch) is the Available count. It has to match `set_company_batch`'s claim filter for `last_scan_at` and `score_floor`.

## Technical scope

* `src/core/roster.py`: modified function `process_recheck_no_openings`. Its failure returns (missing `job_site`, missing `no_jobs_message`, Playwright exception) get the same `last_scan_at` stamp as the success paths, so the frequency window covers every attempt, not just successes.
* `src/data/database.py`: modified function `count_eligible_for_dispatch_task`. The company branch applies the `last_scan_at` staleness filter when `score_floor` is set too, and looks up the state's `batch_criteria` through the registered base state, so Avail matches the claim for every trigger shape. No new table or field: `company.last_scan_at` and `dispatch_task.freq_hrs` already exist.

## Boundaries

Product code only. Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). No new table or field. Don't change NO_OPENINGS → JOBS_FOUND routing.

## Notes for planning

Parent bug AST-1820's Description (As-is / To-be / Proposed steps) is authoritative. Susan approved the reading by reassigning, and that includes stamping `last_scan_at` on failed recheck attempts (this overturns AST-463's "don't bump on failure" rule). Approved ancestor: AST-460 (archived; no live link). Feature doc to patch: `docs/features/roster/ast-460-recheck-no-openings-24h-playwright-recheck-for-no-openings.md`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1820-recheck-no-openings-avail-count`, child `sub/AST-1820/AST-1821-recheck-no-openings-avail-count`. Created at bug-fix.

### Comments

#### radia — 2026-09-27T06:29:19.219Z
[code-rubric] PROCEED (Commit: 4dd0af80) Company Avail matches claim. Clean, no fix-now or discuss items; test coverage lands on gap AST-1822.

#### hedy — 2026-09-27T06:25:40.278Z
test-fix (lighter path, no qa-fix manifest) — `origin/sub/AST-1820/AST-1821-recheck-no-openings-avail-count` @ `4dd0af80`

- py_compile OK on `src/core/roster.py`, `src/data/database.py`.
- `TestProcessRecheckNoOpenings` (6) all PASS, including `test_guards_missing_fields` / `test_playwright_failure_no_state_change` — the unpatched `update_company_last_scan_at` did **not** break them; they just don't assert the new stamp. That assertion (plus score_floor+window, `_RETRY` base lookup, `scan_interval_hours` kwarg) is AST-1822's gap.
- Touched-area suites (test_roster, test_dispatch_tasks, test_dispatcher, test_api_admin, test_repo_admin_json, test_config): zero new failures vs pre-fix `4dd0af80~1`; all remaining failures are pre-existing on the base.

#### joan — 2026-09-27T06:21:33.457Z
[board-joan]  CANON: OK

Stamping failed rechecks and composing `last_scan_at` with `score_floor` / base-state `batch_criteria` in the company count follows `patt.entity.batch-criteria` and `astral.dispatch.entity-state-bound`. There's a pre-existing tension with `patt.task.dispatch-retry` arc 5 (failures aren't routed to `_RETRY`), but this fix doesn't introduce it. No F3.

#### betty — 2026-09-27T06:21:05.541Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md + docs/test-bible/data/database.md (test_dispatch_tasks) — broken test + missing coverage — `TestProcessRecheckNoOpenings::test_guards_missing_fields` / `test_playwright_failure_no_state_change` leave `update_company_last_scan_at` unpatched, so the new failure-path stamps hit the real DB and nothing asserts them (short_name guard must stay unstamped); no test covers the repro: NO_OPENINGS company Avail with `score_floor` set ignoring the `last_scan_at` window, `{base}_RETRY` trigger base-state `batch_criteria` lookup, or the new `scan_interval_hours` kwarg on `count_companies_in_state_with_score_floor`. Dispatcher/api_admin tests mock the count, so they're unaffected.

#### hedy — 2026-09-27T06:20:08.669Z
`origin/sub/AST-1820/AST-1821-recheck-no-openings-avail-count` @ `cb3b1f72` · stamp failures, compose count filters

---

_Implementation detail may live in git history on `origin/dev`._
