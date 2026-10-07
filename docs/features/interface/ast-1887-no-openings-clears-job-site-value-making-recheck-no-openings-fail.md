# AST-1887 — NO_OPENINGS clears job_site value, making recheck_no_openings fail

<!-- linear-archive: AST-1887 archived 2026-10-07 -->

## Linear archive (AST-1887)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1887/no-openings-clears-job-site-value-making-recheck-no-openings-fail  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Companies going from PJL_READY to NO_OPENINGS gets their job_site wiped out (if it was ever there.)

## As-is

When a company in `PJL_READY` runs the decomposed `select_job_page` hop and the agent returns `JOBLIST_NO_JOBS`, the company moves to `NO_OPENINGS` with `companies.job_site` written as an empty string. That wipes out any `job_site` it already had, and never stores the selected list-page URL. After that, `process_recheck_no_openings` in `src/core/roster.py` fails every run with `missing job_site`: it stamps `last_scan_at` and the company stays stuck in `NO_OPENINGS` forever.

Mechanism: `run_select_job_page_dispatch` calls `_find_job_page_from_assembled(..., decomposed=True)`. Non-`JOBLIST_TITLES` outcomes fall through to `_check_parse_results(..., decomposed=decomposed)`, which sets `suppress = decomposed` and passes `suppress_job_site=suppress` to `_save_company` for `JOBLIST_NO_JOBS`. `_save_company` then writes `job_site=""` and skips `_job_site_for_persist`, even though `NO_OPENINGS` is in `_PERSIST_PAGE_OPTION_URL_STATES`. This came in with `74ae56276 code(AST-720)`. AST-720's plan said `JOBLIST_NO_JOBS` would stay "unchanged", but the suppression was meant only for the `JOBLIST_IDENTIFIED` path (AST-673), where the parse sibling writes `job_site` later. `NO_OPENINGS` is terminal: no later hop ever writes it.

## To-be

A `PJL_READY` to `NO_OPENINGS` transition persists `job_site` the same way the legacy path does, through `_job_site_for_persist`: the selected list-page URL (`page_url_map[selected_page]`, falling back to the pre-run value). `recheck_no_openings` can then load the page and check `no_jobs_message` on its 24h cadence. The return dict's `job_site` matches what was written.

## Proposed steps

1. In `_check_parse_results`, stop suppressing `job_site` on the `JOBLIST_NO_JOBS` branch. Call `_save_company` without `suppress_job_site`, so `_job_site_for_persist` writes `job_site_url` because `NO_OPENINGS` is in the persist set.
2. Return `job_site_url` in that branch's return dict instead of `""`.
3. Keep `suppress_job_site=True` exactly as it is on `_finalize_joblist_identified` and the decomposed `TRY_LINKS`-exhausted exits. AST-673 still holds there.
4. Betty adds or updates a component test: decomposed `PJL_READY` plus `JOBLIST_NO_JOBS` must call `update_company` with the selected page URL as `job_site`.
5. Optional backfill, Susan's call: companies already stuck in `NO_OPENINGS` with an empty `job_site` would need a re-run, for example by resetting them to `PJL_READY`. Not in scope unless she asks.

Note, also Susan's call: the decomposed `JOBSITE_SCRAPE_ISSUE` branch in `_check_parse_results` has the same `suppress_job_site=suppress` shape, and `JOBSITE_SCRAPE_ISSUE` is also in `_PERSIST_PAGE_OPTION_URL_STATES`. It isn't covered by this ticket. If she wants it included, add it to scope before handing off.

## Component scope

* `src/core/roster.py` (modified): `_check_parse_results`, specifically the `JOBLIST_NO_JOBS` branch, is where the decomposed `suppress_job_site` wipes the column.
* `tests/component/core/test_roster.py` (modified; Betty owns it in `astral-tests`): regression coverage for decomposed `JOBLIST_NO_JOBS` persisting `job_site`.

## Technical scope

* `src/core/roster.py`: modified function `_check_parse_results`. The `JOBLIST_NO_JOBS` branch must no longer pass the decomposed suppress flag to `_save_company`, and must return the persisted `job_site`, so terminal `NO_OPENINGS` rows keep a URL that `recheck_no_openings` can scrape. No schema or config change is needed, because `NO_OPENINGS` is already in `_PERSIST_PAGE_OPTION_URL_STATES`.
* `tests/component/core/test_roster.py`: new test case (Betty's call on naming and placement) that asserts the `update_company` `job_site` write for the decomposed no-jobs outcome.

## Ancestor candidates

- [ ] AST-720 — select_job_page dispatch refactor (`docs/features/roster/ast-720-select-job-page-dispatch-refactor.md`). This introduced the decomposed path and the `suppress = decomposed` pass-through. Archived.
- [ ] AST-673 — preserve job_site on find_job_page failure (`docs/features/roster/ast-673-preserve-job-site-on-find-job-page-failure-companyjob-site-is-overwritten.md`). This is where the `job_site` suppression intent comes from. Archived.
- [ ] AST-463 — recheck_no_openings, the JOBS_FOUND state and Playwright recheck batch (`docs/features/roster/ast-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch.md`). This is the consumer that fails. Archived.
- [ ] AST-469 — roster locate/parse split (`docs/features/roster/ast-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path.md`). This defined the original `JOBLIST_NO_JOBS` to `NO_OPENINGS` behavior. Archived.

### Comments

#### chuckles — 2026-09-29T23:16:06.269Z
[bug-fix] Done — landed on dev (PR #196). @susan, three things only you can decide:
- Companies already stuck in `NO_OPENINGS` with an empty `job_site` are not backfilled. They need a re-run (for example, reset to `PJL_READY`) if you want them rechecked.
- The decomposed `JOBSITE_SCRAPE_ISSUE` branch has the same wipe and was left as is. Say the word if you want a follow-up.
- `origin/tests-clean-base` is still missing, so Betty published without the tests-branch validator again. Picking its base SHA is your call.

---

_Implementation detail may live in git history on `origin/dev`._
