# AST-1820 — recheck_no_openings avail count

<!-- linear-archive: AST-1820 archived 2026-10-07 -->

## Linear archive (AST-1820)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1820/recheck-no-openings-avail-count  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

The `recheck_no_openings` dispatch row (entity `company`, trigger `NO_OPENINGS`) shows an Available count that doesn't move when the row's frequency (`freq_hrs`) changes. The count code already filters on `company.last_scan_at`: `count_eligible_for_dispatch_task` in `src/data/database.py` counts unclaimed NO_OPENINGS companies where `last_scan_at IS NULL OR last_scan_at < now - N hours`, with N = `freq_hrs` when > 0, else the 24 from `COMPANY_STATES["NO_OPENINGS"].batch_criteria.scan_interval_hours`. So the problem isn't that `last_scan_at` is ignored. More likely, the rows being counted never get a fresh `last_scan_at`, so every frequency window counts the same rows. Leading suspects, from reading the code on `origin/dev` (no prod DB to confirm against):

1. **Failures never stamp** `last_scan_at`**.** `process_recheck_no_openings` in `src/core/roster.py` only calls `update_company_last_scan_at` on its two success paths. Missing `job_site`, missing `company_data.no_jobs_message`, and Playwright exceptions all return without stamping. AST-463 chose this on purpose ("eligible for retry"). The side effect: those companies stay NULL or stale forever, count as Available at any frequency, and get reclaimed every run.
2. `freq_hrs` **= 0 and 24 are the same number.** With `freq_hrs` 0, the count falls back to the state's 24h default, so switching between 0 and 24 can't change the count.
3. **Minor mismatch between the count path and the claim path.** In the company branch of `count_eligible_for_dispatch_task`, a non-null `score_floor` on the row skips the `last_scan_at` filter completely. The admin list nulls `score_floor` for unscored states before counting, so the number on screen is unaffected. The runner's `get_due_tasks` path doesn't null it, though, so if a stray `score_floor` is on the row, the runner's count differs from what claim uses.

## To-be

A `recheck_no_openings` company that was scanned within the row's frequency window (`freq_hrs`, or the 24h state default when 0) is not counted as Available and is not claimed. Changing the frequency changes the Available count to match the companies whose `company.last_scan_at` is older than that window. Every count path (admin list, `get_due_tasks`, dispatcher loop) gives the same number as the claim in `set_company_batch`.

## Proposed steps

1. Confirm against the real DB which suspect it is: for the recheck row's candidate, count NO_OPENINGS companies with `last_scan_at` NULL, older than 24h, and newer than 1h, and check how many are missing `job_site` or `no_jobs_message`.
2. If it's suspect 1: stamp `last_scan_at` on the attempted-but-failed paths in `process_recheck_no_openings` too, so the frequency throttles retries. This overturns AST-463's "don't stamp on failure" decision and needs Susan's yes. The alternative is to route those companies to a retry or triage state instead of leaving them in NO_OPENINGS.
3. Make the company branch of `count_eligible_for_dispatch_task` apply the `last_scan_at` filter together with `score_floor`, the way `set_company_batch` does, so the runner and admin counts agree.
4. Look up `batch_criteria` through the registered base state (as `get_new_company_batch` does since [AST-1806](https://linear.app/astralcareermatch/issue/AST-1806/fix-purge-explicit-retry-states-from-entity-state-registries)), so a `NO_OPENINGS_RETRY` trigger keeps the cadence.

## Component scope

* `src/core/roster.py` (modified): `process_recheck_no_openings` decides whether a failed recheck stamps `company.last_scan_at`. That is the likely reason the count never drops.
* `src/data/database.py` (modified): `count_eligible_for_dispatch_task` (company branch) is the Available count. It has to match `set_company_batch`'s claim filter for `last_scan_at` and `score_floor`.
* `src/ui/api/api_admin.py` (modified): `create_dtask` (`POST /api/admin/dispatch_tasks`) drops `max_runs`, so every form-created row gets the column default 1 ([AST-1831](https://linear.app/astralcareermatch/issue/AST-1831/recheck-no-openings-runs-one-batch-of-10-regardless-of-batch-size-max)).

## Technical scope

* `src/core/roster.py`: modified function `process_recheck_no_openings`. Its failure returns (missing `job_site`, missing `no_jobs_message`, Playwright exception) get the same `last_scan_at` stamp as the success paths, so the frequency window covers every attempt, not just successes.
* `src/data/database.py`: modified function `count_eligible_for_dispatch_task`. The company branch applies the `last_scan_at` staleness filter when `score_floor` is set too, and looks up the state's `batch_criteria` through the registered base state, so Avail matches the claim for every trigger shape. No new table or field: `company.last_scan_at` and `dispatch_task.freq_hrs` already exist.
* `src/ui/api/api_admin.py`: modified function `create_dtask`. It persists `max_runs` from the create form with a guarded follow-up `update_dispatch_task`, mirroring the existing `skip_daisy_chain` / `batch_call_mode` follow-ups, so new rows keep the run cap Susan set.

## Ancestor candidates

- [ ] AST-463: recheck_no_openings, JOBS_FOUND state and Playwright recheck batch (`docs/features/roster/ast-463-recheck-no-openings-jobs-found-state-and-playwright-recheck-batch.md`). Built the NO_OPENINGS 24h cadence and the "no `last_scan_at` bump on failure" rule.
- [X] AST-460: recheck-no-openings, 24h Playwright recheck for NO_OPENINGS (`docs/features/roster/ast-460-recheck-no-openings-24h-playwright-recheck-for-no-openings.md`). Parent definition. Its AC says a company scanned within 24h is not claimed.
- [ ] AST-641: union claim and count for primary + retry trigger states (`docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md`). Count/claim parity across `_RETRY` states.
- [ ] AST-537: regression tests, dispatch without agent_task rows (gaze, recheck_no_openings) (`docs/features/dispatcher/ast-537-regression-tests-dispatch-without-agent-task-rows-gaze-recheck-no-openings.md`). Test coverage for this dispatch path.

---

## Original report (Susan)

dispatch task for recheck_no_openings is for the company entity, and the frequency is set to 24 hours, but the available count does not change with the frequency setting.  I believe company has last_scan_at as a field, please use that.

### Comments

#### chuckles — 2026-09-28T21:27:48.100Z
[check-linear] answered — that was a mistake. The AST-1831 bug-fix pass only moved this parent to In Progress, because all 3 bug children are at User Testing and merged into the ftr. It didn't change the assignee. One second later, a separate Chuckles session (the AST-1845 fix-lane run) switched the assignee to you. Nothing is needed from you on AST-1820. To continue, assign it to Chuckles and datt will run prep-uat.

#### susan — 2026-09-28T21:27:08.947Z
@chuckles Why was this ticket assigned to me?

#### chuckles — 2026-09-28T05:51:04.637Z
[fix-intake] Filed AST-1831 (recheck_no_openings: one batch of 10 regardless of batch_size / max_runs) at Discussion for your review. It has a first read: no special routing; suspect the row stores NULL batch_size / max_runs, or those runs were Sweeps.

#### susan — 2026-09-28T04:54:18.607Z
\[bug\] recheck no openings only runs a single batch of 10 no matter what the batch_size or max_runs are set to.  Is this getting special handling for some reason?  Why isn't it working like all the other dispatch tasks?

#### chuckles — 2026-09-27T06:41:14.816Z
@susan finish-up is stuck: `gh pr edit` fails on gh 2.46 (retired Projects classic API), so `create-dev-pr.py` can’t update [PR #171](https://github.com/susansomerset/astral/pull/171). Nothing has landed. Your call: patch the script to use `gh api -X PATCH`, upgrade gh, or merge #171 yourself. Reassign to Chuckles when ready.

---

_Implementation detail may live in git history on `origin/dev`._
