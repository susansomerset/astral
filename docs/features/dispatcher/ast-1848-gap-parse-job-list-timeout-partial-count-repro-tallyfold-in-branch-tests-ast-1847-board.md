# AST-1848 — gap: parse_job_list timeout partial-count repro + tally/fold-in branch tests (AST-1847 board)

<!-- linear-archive: AST-1848 archived 2026-10-07 -->

## Linear archive (AST-1848)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1848/gap-parse-job-list-timeout-partial-count-repro-tallyfold-in-branch  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1845 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-42590bc8-d1cf-406e-bc23-f8d76d5a0c01  
**Blocked by / blocks / related:** parent: AST-1845

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1847. No test reaches the timeout-with-partial-counts repro: `test_auto_dispatch_uses_timeout` only checks that `wait_for` was awaited, with no ledger or log assertions, and every `parse_job_list_batch` test passes `ctx=None`. Add a bug-repro that times out a `parse_job_list` dispatch after some companies finished. It must go red on the pre-fix product (ledger `total_processed` 0) and green once AST-1847 lands (ledger and timeout log carry the real partial counts). Cover every new branch on the LOCKED_AT_100 files: the `_tally` partial-present and key-None paths, the `_counted` except-path, `_run_unified`'s `dispatch_partial` set/pop, and the timeout-branch fold-in.

## Scope

### Component scope

* `tests/component/core/test_dispatcher.py` (modified): timeout bug-repro asserting the ledger `total_*` and the timeout log line carry partial counts; `_run_unified` `dispatch_partial` set/pop; the timeout-branch fold-in.
* `tests/component/core/test_roster.py` (modified): `parse_job_list_batch` with a real `ctx` carrying `dispatch_partial` (tally per company, key absent/None, `_counted` except-path). Existing `ctx=None` tests stay green.
* `docs/test-bible/core/dispatcher.md`, `docs/test-bible/core/roster.md` (modified): bible entries for the new coverage (AST-891 block).

### Technical scope

* Dispatcher tests: new cases. The repro must fail against the pre-fix product (origin/ftr base = origin/dev at fork) and pass after AST-1847.
* Roster tests: new branch-coverage cases for the per-company tally, with existing cases unchanged.
* Test bible: modified entries naming the coverage.

## Boundaries

Test and bible only; product code stays on AST-1847. Betty lands the tests (engineers are banned from the test tree). Existing tests should survive unchanged. No limits or caps (Susan, 2026-09-28).

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE on AST-1847 (see that comment). Plan doc: docs/features/roster/ast-891-parse-job-list-browser-and-batch.md (AST-1847's plan-fix patch, § Bug: AST-1847).

## Git branch (authoritative)

Parent `ftr/AST-1845-parse-job-list-timeout-partial-counts`, child `sub/AST-1845/AST-1848-parse-job-list-timeout-partial-counts-tests`.

### Comments

#### radia — 2026-09-28T21:24:27.128Z
[code-rubric] PROCEED (Commit: e5718649) repro pins ledger+log

#### hedy — 2026-09-28T21:22:55.221Z
`origin/sub/AST-1845/AST-1848-parse-job-list-timeout-partial-counts-tests` @ `e5718649` · [bug-repro] flip verified

- Pre-fix product (`src/core/{roster,dispatcher}.py` @ `8e7b77a5` under these tests, scratch worktree): **7 failed / 4 passed**, and the 7 are exactly the repro nodes, each failing on its planned assertion (ledger `(0,0,0,1)` vs `(3,2,0,1)`; fold-in `(5,4,0,2)` vs `(7,5,0,3)`; stale/zero partials; `KeyError: 'dispatch_partial'` on cancel).
- Tip: manifest **11 passed**.
- Full test_dispatcher + test_roster: 364 passed / 66 failed. The 66 are node-for-node identical to `origin/dev` @ `8e7b77a5`, so no new failures.

#### hedy — 2026-09-28T21:21:57.383Z
`origin/sub/AST-1845/AST-1848-parse-job-list-timeout-partial-counts-tests` @ `e5718649` · ftr (AST-1847 fix) synced under tests

- Manifest (7 specs → 11 tests): **11 passed** at tip; product files identical to `ba60f8e4`.
- Branch lock (`--cov-branch`, test_dispatcher + test_roster): AST-1847 added lines — dispatcher 16 / roster 23 — **0 missing lines, 0 missing branches**.
- Full two-module run: 364 passed / 66 failed; the 66 are node-for-node identical to `origin/dev` @ `8e7b77a5`.
- Plan-doc conflict resolved: AST-1847 plan/Joan/Radia/disposition first, then AST-1848 plan/Joan.

#### betty — 2026-09-28T21:17:09.625Z
[bug-repro]
`origin/sub/AST-1845/AST-1848-parse-job-list-timeout-partial-counts-tests` @ `ca645d07` · repro red at 8e7b77a5, green on ba60f8e4 overlay

#### joan — 2026-09-28T21:10:22.707Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T21:10:11.239Z
[board-betty] TESTS: REVISE
What: docs/test-bible/README.md §6a/§7.12 (`LOCKED_AT_100`) — missing coverage gate — the manifest is narrowed node ids only, so `check_per_file_coverage.py` never runs on `src/core/roster.py` / `src/core/dispatcher.py`, and "every AST-1847 line covered" in What-must-still-hold is claimed, not proven (same gap as AST-1846). Add a branch-lock run on those two files with the `ba60f8e4` overlay, and narrow the `TestAst891ParseJobListBatch` class line to exclude the known-stale `test_scrape_timeout_labeled_infra_and_counts_passed`. The rest is right as written: I checked nodes 1–9 against the `8e7b77a5..ba60f8e4` diff and they hit every new branch (`_tally` present/None-key/absent, `_counted` except, `_run_unified` set/pop/cancel, fold-in items/empty); all stub targets and bible anchors exist; no existing test breaks.

#### hedy — 2026-09-28T21:09:09.965Z
`origin/sub/AST-1845/AST-1848-parse-job-list-timeout-partial-counts-tests` @ `f297da95` · nine test nodes planned

---

_Implementation detail may live in git history on `origin/dev`._
