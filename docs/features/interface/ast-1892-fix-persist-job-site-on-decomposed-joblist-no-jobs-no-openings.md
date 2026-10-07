# AST-1892 — fix: persist job_site on decomposed JOBLIST_NO_JOBS → NO_OPENINGS

<!-- linear-archive: AST-1892 archived 2026-10-07 -->

## Linear archive (AST-1892)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1892/fix-persist-job-site-on-decomposed-joblist-no-jobs-no-openings  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-1887 — NO_OPENINGS clears job_site value, making recheck_no_openings fail  
**Blocked by / blocks / related:** parent: AST-1887

### Description

## What this implements

A company that goes from `PJL_READY` to `NO_OPENINGS` through the decomposed `select_job_page` hop keeps a real `companies.job_site`: the selected list-page URL, persisted through `_job_site_for_persist` the same way the legacy path does. Today the `JOBLIST_NO_JOBS` branch of `_check_parse_results` passes the decomposed `suppress_job_site` flag, which writes `job_site=""`. That wipes any existing value, and `process_recheck_no_openings` then fails every run with `missing job_site`.

## Scope

## Component scope

* `src/core/roster.py` (modified): `_check_parse_results`, specifically the `JOBLIST_NO_JOBS` branch, is where the decomposed `suppress_job_site` wipes the column.
* `tests/component/core/test_roster.py` (modified; Betty owns it in `astral-tests`): regression coverage for decomposed `JOBLIST_NO_JOBS` persisting `job_site`.

## Technical scope

* `src/core/roster.py`: modified function `_check_parse_results`. The `JOBLIST_NO_JOBS` branch must no longer pass the decomposed suppress flag to `_save_company`, and must return the persisted `job_site`, so terminal `NO_OPENINGS` rows keep a URL that `recheck_no_openings` can scrape. No schema or config change is needed, because `NO_OPENINGS` is already in `_PERSIST_PAGE_OPTION_URL_STATES`.
* `tests/component/core/test_roster.py`: new test case (Betty's call on naming and placement) that asserts the `update_company` `job_site` write for the decomposed no-jobs outcome.

## Boundaries

Product code only. Tests and the test bible belong to Betty; a gap sibling gets filed if fix-board asks for one. Keep `suppress_job_site=True` on `_finalize_joblist_identified` and the decomposed `TRY_LINKS`-exhausted exits, so AST-673's intent still holds there. The decomposed `JOBSITE_SCRAPE_ISSUE` branch has the same shape but is out of scope unless Susan widens it. No backfill of companies already stuck in `NO_OPENINGS`. No new limits, caps, or retries.

## Notes for planning

Parent bug AST-1887's Description (As-is / To-be / Proposed steps) is authoritative; Susan approved it by reassigning. She checked no ancestor box. The Description ties the root cause to `74ae56276 code(AST-720)` (`docs/features/roster/ast-720-select-job-page-dispatch-refactor.md`). Other candidates listed there: AST-673, AST-463, AST-469. All are archived, so there's no related link.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1887-no-openings-job-site`, child `sub/AST-1887/AST-1892-no-openings-job-site`. Created at bug-fix.

### Comments

#### radia — 2026-09-29T23:06:40.636Z
[code-rubric] PROCEED (Commit: e21863a) Decomposed NO_OPENINGS persists job_site

#### joan — 2026-09-29T23:01:36.413Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T23:01:15.535Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md § AST-720 (TestAst720PjlReadySelectDispatch) — missing coverage — no decomposed=True JOBLIST_NO_JOBS test (all 3 existing NO_JOBS tests are legacy, state-only, none break); add the plan's Repro as [bug-repro] asserting update_company job_site="https://jobs" + out["job_site"]=="https://jobs", and fix bible prose that pins JOBLIST_NO_JOBS "with suppress_job_site".

#### hedy — 2026-09-29T23:00:00.744Z
`origin/sub/AST-1887/AST-1892-no-openings-job-site` @ `2734230a1` · un-suppress NO_OPENINGS job_site

---

_Implementation detail may live in git history on `origin/dev`._
