# AST-1870 — gap: tests for provider balance outage path (AST-1867 board)

<!-- linear-archive: AST-1870 archived 2026-10-07 -->

## Linear archive (AST-1870)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1870/gap-tests-for-provider-balance-outage-path-ast-1867-board  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1860 — [✅/Somerset] select_job_page COMPLETED: 24 error(s) / 24 processed | select_job_page-9763cb58-c6d2-4441-a92a-59b49af4372d  
**Blocked by / blocks / related:** parent: AST-1860

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1867. Two existing tests break under the fix, and the new outage path has no coverage.

* **Broken:** `tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal::test_run_company_task_jobs_found_balance_hold_skips_error_state` and `::test_run_company_task_jobs_found_balance_failure_class_skips_error_state` assert `total_errors == 1` on a balance hold. The fix returns `total_held: 1` / `total_errors: 0`. Update them to the new contract.
* **New coverage, including a** `[bug-repro]` **that is red on the pre-fix product and green once AST-1867 lands:**
  * `run_company_task` select_job_page balance hold counts as held, not an error.
  * `_run_unified` skips the remaining entities after a balance refusal, and `_run_dispatch_loop` stops claiming batches.
  * `_dispatch_one_body` ends the run `INTERRUPTED`, sends `monitor.provider_balance_outage` instead of `auto_run_error`, and the run doesn't count toward the circuit breaker.
  * `monitor.provider_balance_outage` subject and body.
* **Regression guard:** an AST-1189 provider-call-budget `state_held` result (no balance `failure_class`) still counts `total_errors: 1`.

## Scope

### Component scope

* `tests/component/core/test_roster.py` (modified): update the two AST-897 JOBS_FOUND balance-hold assertions to the held contract. Add select_job_page balance-hold counting, plus the AST-1189 timeout guard (still an error).
* `tests/component/core/test_dispatcher.py` (modified): `_run_unified` skip-after-refusal, `_run_dispatch_loop` stop, and `_dispatch_one_body` INTERRUPTED + outage alert + breaker exclusion. This is the `[bug-repro]`.
* `tests/component/core/test_monitor.py` (modified): new `provider_balance_outage` subject/body.
* `docs/test-bible/core/roster.md`, `docs/test-bible/core/dispatcher.md`, `docs/test-bible/core/monitor.md` (modified): bible entries for the new and changed coverage.

### Technical scope

* Roster tests: modified test functions (two AST-897 cases) plus new test function(s) for held counting and the timeout guard.
* Dispatcher tests: new test function(s). The repro must fail against the pre-fix product (origin/ftr base = origin/dev at fork) and pass with AST-1867's product change.
* Monitor tests: new test function(s) for the new alert function.
* Test bible: modified entries naming the coverage.

## Boundaries

Test and bible only; product code stays on AST-1867. Betty lands the tests (engineers are banned from the test tree). No limits or caps.

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE on AST-1867 (see that comment). Plan doc: docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md (AST-1867's plan-fix section; Joan CANON: OK).

## Git branch (authoritative)

Parent `ftr/AST-1860-provider-balance-outage`, child `sub/AST-1860/AST-1870-provider-balance-outage-tests`.

### Comments

#### radia — 2026-09-29T18:31:55.640Z
[code-rubric] PROCEED (Commit: 8c4d2a5d) repro pins outage contract

#### ada — 2026-09-29T18:30:03.163Z
`origin/sub/AST-1860/AST-1870-provider-balance-outage-tests` @ `8c4d2a5d` · no new push

- `[bug-repro]` `TestAst1867ProviderBalanceOutage::test_bug_repro_balance_refusal_one_call_interrupted_outage_alert`: RED with pre-fix `src/core/{roster,dispatcher,monitor}.py` from `fbe9486e` overlaid (`assert 9 == 1` on provider call count) → GREEN on tip.
- Manifest (dispatcher.md § AST-1867 · AST-1870): 23 passed.
- Full `test_{roster,dispatcher,monitor}.py`: 69 failing, identical set to `origin/dev` @ `fbe9486e` — zero new.

#### betty — 2026-09-29T18:23:43.860Z
[bug-repro]
`origin/sub/AST-1860/AST-1870-provider-balance-outage-tests` @ `d4494bc3` · repro red@fbe9486e, green@144b8850

#### joan — 2026-09-29T18:16:25.360Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T18:16:11.113Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/{roster,dispatcher,monitor}.md — missing coverage + two broken tests (the whole ticket is test work) — land at qa-fix exactly as the plan names them: flip R1/R2 in `TestAst897HoldStateOnBalanceRefusal` to the held contract; add `test_roster.py::TestAst1867BalanceHeldCounting` (R3, R4 AST-1189 guard), `test_dispatcher.py::TestAst1867ProviderBalanceOutage` (D1 `[bug-repro]` red at `fbe9486e` / green at `144b8850`, D2–D6; D7 existing), `test_monitor.py::TestAst1867ProviderBalanceOutage` (M1–M4); three bible entries. Anchors verified on the publish ref. Plan fully covers my AST-1867 REVISE gap. Pre-existing drift (`TestCircuitBreaker` 4-arg calls, `TestAutoRunErrorSubjectPrefix`, D7 passing by accident) is outside the plan scope — flag only, no scope change requested.

#### ada — 2026-09-29T18:15:12.575Z
`origin/sub/AST-1860/AST-1870-provider-balance-outage-tests` @ `bdb238fe` · nodes + dispatcher bug-repro

---

_Implementation detail may live in git history on `origin/dev`._
