# AST-1847 — fix: parse_job_list timeout keeps partial passed/error counts in dispatch ledger

<!-- linear-archive: AST-1847 archived 2026-10-07 -->

## Linear archive (AST-1847)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1847/fix-parse-job-list-timeout-keeps-partial-passederror-counts-in  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1845 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-42590bc8-d1cf-406e-bc23-f8d76d5a0c01  
**Blocked by / blocks / related:** parent: AST-1845

### Description

## What this implements

When the dispatch timeout cancels a `parse_job_list` batch, the dispatch ledger records what actually got done. Passed/failed/error counts from companies that finished before the cancel survive and land in the ledger row's `total_*` columns, and the timeout log line carries the same counts. An INTERRUPTED batch then shows e.g. `12 processed`, not `0 processed`.

## Scope

## Component scope

* `src/core/roster.py` — modified: `parse_job_list_batch` holds its running `passed`/`errors` in locals that are lost when the dispatch timeout cancels it.
* `src/core/dispatcher.py` — modified: `_run_unified` / `_dispatch_one_body` build the `accumulated` summary written to the dispatch ledger, which only receives counts from a batch that returned normally.

## Technical scope

* `src/core/roster.py`: modified function `parse_job_list_batch`. Per-company outcomes are published as they finish (e.g. into a shared summary the dispatcher owns), so counts survive a cancel.
* `src/core/dispatcher.py`: modified functions `_run_unified` and `_dispatch_one_body` (timeout branch). Partial counts from the cancelled batch are merged into `accumulated` before the ledger update, so INTERRUPTED rows show the real processed/passed/errors totals. No new table or field: the ledger's `total_*` columns already exist.

## Boundaries

Product code only. Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). Steps 1–2 of the bug's original read (linear `find_job_containers`, cull moved off the event loop) already shipped in AST-1840, so don't touch them again. **No size cap or truncation on cull output** (not approved by Susan). Per-company state writes and `clear_company_batch` release already happen on timeout, so don't redesign them. This ticket is only about getting the counts into the ledger.

## Notes for planning

Parent bug AST-1845's Description (As-is / To-be / Proposed steps, Susan's comments 2026-09-28) is authoritative. Susan approved partial ledger counts ("do the partial counts in the ledger to reflect reality"). No ancestor box was checked, so there's no related-issue link. Feature doc to patch (Chuckles' best read): `docs/features/roster/ast-891-parse-job-list-browser-and-batch.md`, whose AC4 says successful parses in a batch aren't stranded by failures elsewhere. The timeout branch is in `_dispatch_one_body` (`except asyncio.TimeoutError`) in `src/core/dispatcher.py`. `accumulated` only gets counts from runs that returned normally.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1845-parse-job-list-timeout-partial-counts`, child `sub/AST-1845/AST-1847-parse-job-list-timeout-partial-counts`. Created at bug-fix.

### Comments

#### radia — 2026-09-28T21:19:18.543Z
[code-rubric] PROCEED (Commit: ba60f8e4) partial ledger counts hold

#### hedy — 2026-09-28T21:12:24.334Z
`origin/sub/AST-1845/AST-1847-parse-job-list-timeout-partial-counts` @ `ba60f8e4` · lighter check (no qa-fix manifest; Betty's REVISE lives on AST-1848)

- `py_compile` roster.py / dispatcher.py: OK
- `/home/susan/astral/.venv/bin/python -m pytest tests/component/core/test_dispatcher.py tests/component/core/test_roster.py --no-cov`: 66 failed / 356 passed / 18 skipped. **Identical 66-node failure set on `origin/dev` @ `8e7b77a5`** (zero only-at-tip). Pre-existing, not AST-1847.
- Near the touched code, stale on dev: `TestRunUnified::test_ast891_parse_job_list_full_batch_despite_batch_call_mode_zero` (dev dropped the parse_job_list full-batch override), `TestAst841DispatchTerminalLogging::*` ("batch finished …" line gone from src). FYI @Betty White for the AST-1848 manifest baseline.

#### joan — 2026-09-28T20:58:08.394Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T20:57:32.686Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/dispatcher.md + core/roster.md (AST-891 block) — missing coverage — no test reaches the timeout-with-partial-counts repro (`test_auto_dispatch_uses_timeout` only asserts `wait_for` awaited, no ledger/log asserts; all `parse_job_list_batch` tests pass `ctx=None`), and both files are LOCKED_AT_100 so the new `_tally` (partial present / key None), `_counted` except-path, `_run_unified` set/pop and timeout fold-in branches need nodes; no existing test breaks.

#### hedy — 2026-09-28T20:56:37.101Z
`origin/sub/AST-1845/AST-1847-parse-job-list-timeout-partial-counts` @ `bd850855` · partial counts via ctx summary

---

_Implementation detail may live in git history on `origin/dev`._
