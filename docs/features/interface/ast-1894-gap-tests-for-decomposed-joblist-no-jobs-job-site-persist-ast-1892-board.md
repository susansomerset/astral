# AST-1894 — gap: tests for decomposed JOBLIST_NO_JOBS job_site persist (AST-1892 board)

<!-- linear-archive: AST-1894 archived 2026-10-07 -->

## Linear archive (AST-1894)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1894/gap-tests-for-decomposed-joblist-no-jobs-job-site-persist-ast-1892  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-1887 — NO_OPENINGS clears job_site value, making recheck_no_openings fail  
**Blocked by / blocks / related:** parent: AST-1887

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1892. Nothing existing breaks: the three current `JOBLIST_NO_JOBS` tests all use the legacy path and only assert state. The decomposed path has no coverage, and the bible describes the bug as intended.

* **New coverage, a** `[bug-repro]` **that is red on the pre-fix product and green once AST-1892 lands:** in `TestAst720PjlReadySelectDispatch` (or next to it), `_check_parse_results` / the `PJL_READY` dispatch with `decomposed=True` and response `JOBLIST_NO_JOBS` must persist `update_company(..., job_site=<selected page URL>)` and return `out["job_site"] == <selected page URL>`, with state `NO_OPENINGS`. This is plan-fix's Repro.
* **Bible correction:** the AST-720 entry in `docs/test-bible/core/roster.md` says `JOBLIST_NO_JOBS` runs "with `suppress_job_site`". Rewrite it so `JOBLIST_NO_JOBS` persists `job_site` (NO_OPENINGS ∈ `_PERSIST_PAGE_OPTION_URL_STATES`), while `JOBLIST_IDENTIFIED` and the TRY_LINKS-exhausted exits still suppress (AST-673).

## Scope

### Component scope

* `tests/component/core/test_roster.py` (modified): new decomposed `JOBLIST_NO_JOBS` test as the `[bug-repro]`.
* `docs/test-bible/core/roster.md` (modified): corrected AST-720 prose plus a bible row for the new test.

### Technical scope

* Roster tests: new test function asserting the `update_company` `job_site` write and the returned `job_site` on the decomposed no-jobs outcome. This is the `[bug-repro]`: red before AST-1892's change, green after.
* Test bible: a modified entry for AST-720's `JOBLIST_NO_JOBS` wording, plus a new entry for the repro test.

## Boundaries

Test and bible only; product code stays on AST-1892. Betty lands the tests (engineers are banned from the test tree). No limits or caps.

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE on AST-1892 (see that comment). Plan doc: docs/features/roster/ast-720-select-job-page-dispatch-refactor.md, AST-1892's plan-fix section (Joan CANON: OK).

## Git branch (authoritative)

Parent `ftr/AST-1887-no-openings-job-site`, child `sub/AST-1887/AST-1894-no-openings-job-site-tests`.

### Comments

#### radia — 2026-09-29T23:14:39.868Z
[code-rubric] PROCEED (Commit: 8d77672) bug-repro pins decomposed job_site

#### betty — 2026-09-29T23:10:44.158Z
[bug-repro]
`origin/sub/AST-1887/AST-1894-no-openings-job-site-tests` @ `6fe2697c6` · repro red pre-fix, green on ftr
Repro: `tests/component/core/test_roster.py::TestAst720PjlReadySelectDispatch::test_joblist_no_jobs_persists_selected_job_site` — red on origin/dev roster.py (`assert '' == 'https://acme.com/careers'`), green on ftr 91577d1c6 (class 10/10). Bible: docs/test-bible/core/roster.md AST-720 prose + AST-1892 section. validate-tests-branch.sh skipped per Chuckles (tests-clean-base missing on origin). @Hedy

#### joan — 2026-09-29T23:07:52.273Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T23:07:36.762Z
[board-betty] TESTS: OK
Covers the AST-1892 REVISE in full: [bug-repro] `TestAst720PjlReadySelectDispatch::test_joblist_no_jobs_persists_selected_job_site` (update_company job_site + return job_site + transition + no_jobs_message), AST-720 bible prose corrected, AST-1892 bible section added. Assumptions verified against origin/ftr/AST-1887-no-openings-job-site @ 91577d1c6 (helper page_url_map, single update_company, _company short_name). qa-fix still owns the red-on-pre-fix check.

#### hedy — 2026-09-29T23:06:17.827Z
`origin/sub/AST-1887/AST-1894-no-openings-job-site-tests` @ `fda36774f` · repro test + bible fix

---

_Implementation detail may live in git history on `origin/dev`._
