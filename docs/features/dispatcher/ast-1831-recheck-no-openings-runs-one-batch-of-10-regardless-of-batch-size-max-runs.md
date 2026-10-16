# AST-1831 — recheck_no_openings runs one batch of 10 regardless of batch_size / max_runs

<!-- linear-archive: AST-1831 archived 2026-10-07 -->

## Linear archive (AST-1831)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1831/recheck-no-openings-runs-one-batch-of-10-regardless-of-batch-size-max  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1820 — recheck_no_openings avail count  
**Blocked by / blocks / related:** parent: AST-1820

### Description

## Susan's comment (verbatim)

\[bug\] recheck no openings only runs a single batch of 10 no matter what the batch_size or max_runs are set to.  Is this getting special handling for some reason?  Why isn't it working like all the other dispatch tasks?

## As-is

A `recheck_no_openings` dispatch run (company, trigger `NO_OPENINGS`) claims and processes one batch of 10 companies and stops, whatever the row's `batch_size` and `max_runs` are set to.

## To-be

`recheck_no_openings` behaves like every other dispatch task: each batch claims `batch_size` companies, and the run keeps looping until `max_runs` is reached (0 = until drained) or Available runs out.

## First read (Chuckles, from `origin/dev` @ 31846c28, no prod DB)

* The dispatcher has no special routing for recheck_no_openings. It goes through the generic `_run_unified` company path like every other company task.
* **Batch of 10:** `_run_unified` passes the row's `batch_size` as the claim `limit`. `get_new_company_batch` falls back to `COMPANY_STATES["NO_OPENINGS"].batch_criteria.limit` (10) **only when** `batch_size` **is NULL**. Suspect: the stored recheck row has `batch_size` NULL (or the edit doesn't persist for this row) while the UI shows a value.
* **Single run:** `_run_dispatch_loop` stops after one run when `max_runs` is NULL (`max_runs is None or run_count >= max_runs`), and forces `max_runs = 1` for a manual Sweep on an AUTO row. Suspect: the same NULL/persist problem on `max_runs`, or the runs Susan watched were Sweeps.
* First check for plan-fix: read the live `dispatch_task` row for `recheck_no_openings` (`batch_size`, `max_runs`, `auto_mode`) and the ledger or log lines for one run (`Calling get_new_company_batch: [... limit=...]` and the `loop stop:` reason).

## Suggested engineer

Hedy Lamarr (sibling AST-1821 owner; roster / dispatch cadence).

### Comments

#### radia — 2026-09-28T21:06:14.215Z
**review-fix: CLEAN.** No fix-now items.

- **[bug-repro]:** `TestAst1831CreateMaxRuns` is correct. It asserts `update_dispatch_task(id, max_runs=int)` for 0, 5, and "3", and no follow-up call when `max_runs` is absent or null. The tests were red before the fix and are green now.
- **What must still hold:** unchanged. Only the `create_dtask` follow-up was touched. Dispatcher, roster, database, and batch_size NULL behaviour are untouched.
- **Advisory:** `debug` still isn't sent on Add (a frontend follow-up). The 100% branch coverage on `api_admin.py` needs a re-check on a clean test environment.

#### hedy — 2026-09-28T21:05:12.191Z
test-fix — `origin/sub/AST-1820/AST-1831-recheck-no-openings-batch-size-max-runs` @ `78f1b395`

- [bug-repro] `TestAst1831CreateMaxRuns`: pre-fix `16432462` → 3 failed (`test_create_persists_max_runs[drain|cap|numeric_str]`) / 2 passed; tip → 5 passed. Flip confirmed.
- `test_api_admin.py` full: no new failures vs pre-fix; 5 pre-existing reds unchanged (incl. `TestDispatchTasks::test_list_dispatch_tasks_and_keys`).
- `api_admin.py` branch lock: **not verifiable to 100% in this environment.** The full component tree has 5 collection errors that are on `origin/dev` too (orphan tests: `test_surfer.py`, `test_meteorite_email.py`, `test_page_intake.py`, `test_meteorites.py`, `test_surfer_batches.py` import product modules that aren't present; added by `merge-tests(AST-1239)` d486fd0f), plus ~320 env failures. Like-for-like full-tree run (runner env, `--continue-on-collection-errors`): pre-fix 368/430 → tip 370/432, missing branches unchanged at 62. The fix's two new branches are covered; no regression.

#### betty — 2026-09-28T20:54:59.139Z
[bug-repro]
`origin/sub/AST-1820/AST-1831-recheck-no-openings-batch-size-max-runs` @ `16432462` · repro lands red, awaits fix

Repro node: `tests/component/ui/api/test_api_admin.py::TestAst1831CreateMaxRuns::test_create_persists_max_runs` (0 / 5 / "3") — red on pre-fix tip (`update_dispatch_task` not called); `test_create_without_max_runs_skips_follow_up` (absent / null) green both sides. Plan's 3-line fix applied in a throwaway → all 5 green. `TestDispatchTasks::test_list_dispatch_tasks_and_keys` is red with and without the fix (pre-existing, not this ticket). Bible: `docs/test-bible/ui/api/api_admin.md` § AST-1831 · AST-1820.

#### joan — 2026-09-28T20:53:03.126Z
[board-joan]  CANON: OK

Persisting `max_runs` on admin create brings the stored row back in line with `patt.entity.batch-criteria` (the operator sets criteria; the row must not lie). No directive change, no F3.

#### betty — 2026-09-28T20:52:51.757Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md (tests/component/ui/api/test_api_admin.py `test_create_dispatch_task_paths`) — missing coverage — no create POST sends `max_runs`, so the repro (POST `max_runs: 0` stored as 1) is uncovered and the new follow-up's true arm leaves `api_admin.py` (LOCKED_AT_100) under 100% branch. Need a create node that posts `max_runs` 0 and N and asserts `update_dispatch_task(task_id, max_runs=<int>)`, plus absent/null asserting no max_runs follow-up. Existing create/retired-key tests don't send `max_runs`, so they're unaffected.

#### hedy — 2026-09-28T20:52:08.069Z
`origin/sub/AST-1820/AST-1831-recheck-no-openings-batch-size-max-runs` @ `5f7122bc` · create persists max_runs

#### chuckles — 2026-09-28T20:51:10.508Z
[check-linear] Plan Discuss — `src/ui/api/api_admin.py` (`create_dtask` persists `max_runs`) added to AST-1820 Component/Technical scope; the scope-gate blocker is answered. Assigned to Chuckles, so it resumes at Plan Discuss and re-plans with the admin fix included.

#### susan — 2026-09-28T20:49:25.643Z
@chuckles if there's a bug in the admin ui, then add it to the scope of this bug, then resolve the problems.

#### chuckles — 2026-09-28T20:46:44.737Z
@susan two things before this can be planned (see Hedy’s [scope-gate] above): (1) the stored batch_size / max_runs / auto_mode / min_count / sweep_hrs on the live recheck_no_openings row, and whether those runs were Sweep clicks or AUTO ticks; (2) OK to add `src/ui/api/api_admin.py` (the create handler drops `max_runs`) to AST-1820’s scope? Answer here and reassign to Chuckles; it resumes at Plan Discuss.

#### hedy — 2026-09-28T20:46:16.839Z
[scope-gate]

`origin/sub/AST-1820/AST-1831-recheck-no-openings-batch-size-max-runs` @ `e93b64cb` — full trace in the plan doc, § Bug: AST-1831.

**Finding:** no code path special-cases `recheck_no_openings`. `batch_size` → claim limit and `max_runs` → loop stop are the same generic dispatcher/roster path every company task uses. "10 per batch, one run" = the row's **stored** `batch_size` is NULL (falls back to NO_OPENINGS limit 10) and `max_runs` is NULL/1, or the runs were Sweeps (one batch by design, AST-1829).

**Real defect found (generic, all task keys):** Admin → Scheduled Actions **Add** drops `max_runs`. `POST /api/admin/dispatch_tasks` calls `save_dispatch_task(...)`, which has no `max_runs` param, and never follows up with `update_dispatch_task(max_runs=…)`, so every form-created row gets the column DEFAULT 1.

**Scope gap:** the fix is one guarded follow-up call in `src/ui/api/api_admin.py` (create handler), mirroring the existing `skip_daisy_chain` / `batch_call_mode` follow-ups. AST-1820's declared scope covers only `src/core/roster.py` (`process_recheck_no_openings`) and `src/data/database.py` (`count_eligible_for_dispatch_task`). Neither covers admin create persistence, and the fix can't be done inside them. @chuckles: small omission; amend AST-1820's scope to add `src/ui/api/api_admin.py` (create handler persists `max_runs`), then assign this bug to Chuckles.

@susan: to confirm this is your case before building, from the environment where you saw it, what are the recheck row's stored `batch_size`, `max_runs`, `auto_mode`, `min_count`, `sweep_hrs`? And were those runs Sweep clicks or AUTO ticks? (Heads-up: an AUTO row rejects edits with "Turn AUTO mode off before editing this row" until AUTO is off.) If the stored values already match what you set and a non-Sweep run still logs `limit=10`, I'll re-plan.

---

_Implementation detail may live in git history on `origin/dev`._
