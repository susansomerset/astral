# AST-1999 — gap: PJL refresh tests — re-scrape/upsert + failure carry-forward (AST-1995 board REVISE)

<!-- linear-archive: AST-1999 archived 2026-10-13 -->

## Linear archive (AST-1999)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1999/gap-pjl-refresh-tests-re-scrapeupsert-failure-carry-forward-ast-1995  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1994 — fetch_ tasks should refresh existing content  
**Blocked by / blocks / related:** parent: AST-1994

### Description

## What this implements

Test gap from `[board-betty] TESTS: REVISE` on [AST-1995](https://linear.app/astralcareermatch/issue/AST-1995): the PJL refresh (re-scrape every candidate URL, upsert `pjl_scrape_pages` by `normalize_link`, rebuild `pjl_nav_links` from this run, keep prior row + its nav links on a failed/empty re-scrape) flips two AST-719 additive-skip tests and has no repro coverage. Update the flipped tests, add the repro + new-branch coverage ([gazer.py](<http://gazer.py>) / [roster.py](<http://roster.py>) are LOCKED_AT_100), and keep the bible honest.

## Scope

### Component scope

* `tests/component/core/test_gazer.py` — modified: `TestFetchJobPagesBatch::test_additive_skips_already_scraped_url` rewritten for refresh semantics; new cases for the AST-1995 repro and failure carry-forward.
* `tests/component/core/test_roster.py` — modified: `TestAst719PjlRosterHelpers::test_merge_pjl_scrape_record_skips_duplicate_and_empty` first assert flips to replace-in-place; new upsert / error-with-text cases.
* `docs/test-bible/core/gazer.md` — modified: AST-719/759 entries (L49 `skipped-already-scraped` prose) updated; AST-1995 nodes added.
* `docs/test-bible/core/roster.md` — modified: `_merge_pjl_scrape_record` entry updated; AST-1995 nodes added.

### Technical scope

* `test_gazer.py` — modified + new test functions: already-scraped URL is re-scraped and its row replaced in place (repro fixture in plan); `pjl_assembled_content` drops OLD BOARD; `pjl_nav_links` rebuilt from this run (dead link gone, written even when empty); failed re-scrape with a prior row keeps row + carries its nav links; failed scrape with no prior row contributes nothing; PJL_READY / JOBSITE_SCRAPE_ISSUE unchanged.
* `test_roster.py` — modified + new test functions: upsert replaces matching `normalize_link` row at same index; new URL appends; empty text or `error` (even with text) returns existing unchanged; whole-row replace (missing `enumerated_nav_links` drops the key).
* Bible — modified entries documenting those nodes.

## Boundaries

Product code stays on [AST-1995](https://linear.app/astralcareermatch/issue/AST-1995). Test tree / bible only (Betty). Canon: Joan CANON: OK — no canon gap.

## Notes for planning

Board: `[board-betty] TESTS: REVISE` on AST-1995 (full text in that comment). Plan: `docs/features/roster/ast-719-fetch-job-pages-gazer-batch-and-pjl-ready-state.md` `## Bug: AST-1995` (Repro fixture + What must still hold there are the exact asserts).

## Git branch (authoritative)

Parent `ftr/AST-1994-fetch-refresh`, child `sub/AST-1994/AST-1999-fetch-refresh-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-06T05:26:38.288Z
[code-rubric] PROCEED (Commit: 69f5bd55) PJL repro tests solid

#### hedy — 2026-10-06T05:25:37.237Z
`origin/sub/AST-1994/AST-1999-fetch-refresh-tests` @ `69f5bd55c`

[bug-repro] flip verified: all 9 of Betty's repro tests (from `e583d0a97`) fail on ftr parent `a65581d77`, each on a real assertion, and pass after sync merged in ftr with AST-1995 (`c9303baa2`). All 38 tests in the PJL classes pass. Full `test_gazer.py` + `test_roster.py`: 53 failed / 365 passed. No new failures; all 53 are on the pre-existing list from AST-1995, and the 4 `TestFetchJobPagesBatch` tests that were broken by the missing `_mock_browser_context` now pass. `test_gazer_scrape_failure.py` (AST-2002) was not run here. Paperwork pushed: `b5d260c09` docs(AST-1999) retroactive plan block, `69f5bd55c` empty code() marker.

#### betty — 2026-10-06T05:17:20.421Z
[bug-repro]
`origin/sub/AST-1994/AST-1999-fetch-refresh-tests` @ `c0c22e2ea` · repro red pre-fix, green w/ c9303baa2

---

_Implementation detail may live in git history on `origin/dev`._
