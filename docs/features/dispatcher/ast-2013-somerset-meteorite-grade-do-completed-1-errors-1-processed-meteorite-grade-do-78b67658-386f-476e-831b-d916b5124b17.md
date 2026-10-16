# AST-2013 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-78b67658-386f-476e-831b-d916b5124b17

<!-- linear-archive: AST-2013 archived 2026-10-16 -->

## Linear archive (AST-2013)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2013/somerset-meteorite-grade-do-completed-1-errors-1-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Add "duplicate vector codes" as a validation check on the scheduled actions page, not just empty tokens.  Don't run the job if the rubric is bad/duped.

## As-is

The Scheduled Actions page (`AdminScheduledActions.tsx`, fed by `list_dtasks` in `src/ui/api/api_admin.py`) marks a row Invalid in two cases: its prompt tokens render empty for the candidate (AST-1766 / AST-1780 / AST-1819), or the candidate has no platform API key (AST-1880). In both cases the server sets `empty_render` plus `empty_tokens` / `invalid_reason`. The UI disables AUTO and Run/Sweep and shows the reason in the tooltip. `PUT` AUTO-on and `POST …/run` return 400, and a row that is already AUTO-on gets forced off.

Nothing checks the rubric behind a scored task. Somerset's Do rubric has two current `TP` rows (`duplicate rubric codes: TP→['Hands-On Technical Partnership With Engineers', 'Hands-On Technical Partnership With Engineers']`), so it presents 12 vectors where 11 are unique. `meteorite_grade_do` still ran. Job `bf81c81e-15e7-4ef2-b61b-e6181a9b8891` came back with every grade `X` on two runs in a row, and on the second the AST-1760 guard sent it to `METEORITE_FAILED_TECHNICAL_DO` (batch `meteorite_grade_do-78b67658-…`, `error:1`). `_vector_labels_map` (`consult.py`) only logs a warning and keeps the first duplicate. The dispatch proceeds anyway, and every grading call against that rubric is wasted.

Separately, `dispatcher.run_task` (the scheduler's spawn point) has no validation gate at all. A row that already has AUTO on keeps sweeping until someone loads Scheduled Actions and the list enrichment turns AUTO off.

## To-be

A rubric-backed task row (any `task_key` whose `TASK_CONFIG` entry names a `rubric_artifact`, such as `grade_do` / `meteorite_grade_do` → `do_rubric`) is **Invalid** on Scheduled Actions when that candidate's current rubric is bad. Bad means:

* **duplicate vector codes** — two or more current criteria share a code (case-insensitive, matching `_vector_labels_map`), or
* **empty** — the task is rubric-backed but the candidate has zero current criteria.

An Invalid row behaves exactly like an empty-token row:

* AUTO and Run/Sweep are disabled.
* The tooltip names the problem, for example `Rubric 'do_rubric' has duplicate vector codes: TP`.
* AUTO-on and Run return 400.
* An AUTO-on row is forced off with a warning.
* The scheduler refuses to start the job.

Re-saving the rubric repairs the duplicates through AST-2008's uptick, and the row becomes valid again on the next list load.

## Proposed steps

1. **Shared check.** Add a pure helper in `src/core/candidate.py`, next to `_uptick_duplicate_rubric_codes`. Given `(candidate_id, task_key)`, it resolves the task's `rubric_artifact` → owner task, loads `rubric_criteria_for_task`, and returns a short user-facing reason: duplicate codes listed, or empty rubric. It returns `None` when the rubric is fine or the task isn't rubric-backed.
2. **Scheduled Actions list.** In `list_dtasks` (`api_admin.py`, AST-1780 block around line 964), call the helper beside `_candidate_dispatch_api_key_error`. Fold its result into `row["empty_render"]` and `row["invalid_reason"]` the same way `key_err` is folded in (AST-1880). The existing AUTO-forced-off branch then covers it, with the reason in its warning.
3. **API gates.** Return 400 with the same reason from the AUTO-on create/update paths (`api_admin.py` around lines 1173 and 1381) and from `run_dtask`, beside the existing key and empty-render checks.
4. **Scheduler gate.** In `dispatcher.run_task`, before spawning the thread, refuse to start a row that fails the helper. Return `False`, log one warning with the reason, and force `auto_mode` off. A stored duplicate then can't keep sweeping on AUTO while nobody has the page open.
5. **Data.** Re-save somerset's Do rubric once in Artifacts. AST-2008 renames the duplicate `TP` → `TX` and retires the extra row, so the row turns valid. Then re-run `meteorite_grade_do` for `bf81c81e…` from `METEORITE_PASSED_JD`. (Staging operation, not code.)

## Component scope

* `src/core/candidate.py` — modified — new rubric-validity helper beside `_uptick_duplicate_rubric_codes` / `rubric_criteria_for_task`. Rubric loading and code normalization already live here.
* `src/ui/api/api_admin.py` — modified — `list_dtasks` enrichment, the AUTO-on gates, and the `run_dtask` gate call the new helper, using the same pattern as `_candidate_dispatch_api_key_error`.
* `src/core/dispatcher.py` — modified — `run_task` refuses to start (and forces AUTO off) when the rubric is bad, so scheduled sweeps honor the check without a page load.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — not expected to change. It already blocks on `empty_render` and shows `invalid_reason` in the Invalid tooltip.
* Somerset `rubric_vector` rows — data re-save via Artifacts (no code).

## Technical scope

* `src/core/candidate.py`: **new function**. It returns an optional reason string for a `(candidate_id, task_key)` rubric: duplicate codes (listed) or empty rubric for a rubric-backed task. Pure read, no writes, so the list, the gates, and the scheduler share one definition of "bad".
* `src/ui/api/api_admin.py`: **modified functions** `list_dtasks`, the dispatch-task create/update handlers, and `run_dtask`. Each needs one more reason source in the existing Invalid / 400 plumbing. No new response fields: `empty_render` and `invalid_reason` already carry it.
* `src/core/dispatcher.py`: **modified function** `run_task`. An early refusal plus AUTO-off persist when the helper returns a reason, because AUTO rows are spawned here without going through the admin API.
* No new tables, fields, job states, or `TASK_CONFIG` keys. AST-1760 all-X routing, `_render_score` math, and AST-1513's first-wins `_vector_labels_map` warning stay unchanged.

## Ancestor candidates

- [ ] [AST-1766](https://linear.app/astralcareermatch/issue/AST-1766) — Dispatch validation (`docs/features/dispatcher/ast-1766-dispatch-validation.md`). The epic that built the Scheduled Actions empty-token Invalid gate (list flag, AUTO-on and Run 400s, AUTO forced off). This ask adds another check to that gate.
- [ ] [AST-1819](https://linear.app/astralcareermatch/issue/AST-1819) — Invalid button tooltip listing missing prompt tokens (`docs/features/interface/ast-1819-invalid-button-needs-a-tooltip-listing-the-missing-prompt-tokens.md`). Owns the tooltip that would show the duplicate-code reason.
- [ ] [AST-1852](https://linear.app/astralcareermatch/issue/AST-1852) — Scheduled action validation is flawed (`docs/features/dispatcher/ast-1852-scheduled-action-validation-is-flawed.md`). The most recent fix to the same validation path.
- [ ] [AST-2007](https://linear.app/astralcareermatch/issue/AST-2007) / [AST-2008](https://linear.app/astralcareermatch/issue/AST-2008) — rubric code uptick + sync duplicate retire (`docs/features/consult/ast-1513-reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing.md` § AST-2008). Repairs duplicates on save. The stored somerset `TP` duplicate is still waiting for that re-save.
- [ ] [AST-1510](https://linear.app/astralcareermatch/issue/AST-1510) / [AST-1513](https://linear.app/astralcareermatch/issue/AST-1513) — reject duplicate DO rubric codes (same doc). Origin of the duplicate-`TP` warning on this rubric.
- [ ] [AST-1759](https://linear.app/astralcareermatch/issue/AST-1759) / [AST-1760](https://linear.app/astralcareermatch/issue/AST-1760) — all-X scored grades → retry holding (`docs/features/consult/ast-1760-all-x-scored-grades-retry-holding.md`). The guard that fired. Working as designed; context only.

## Original report

```
2026-10-07 02:23:05  [WARNING]  duplicate rubric codes: TP→['Hands-On
Technical Partnership With Engineers', 'Hands-On Technical Partnership
With Engineers']
2026-10-07 02:23:05  [INFO]  somerset | dispatch job starting
meteorite_grade_do — 1 available (batch:
meteorite_grade_do-78b67658-386f-476e-831b-d916b5124b17)
2026-10-07 02:24:33  [INFO]  somerset | dispatch job task completed:
meteorite_grade_do pass:0 fail:0 error:1 (batch:
meteorite_grade_do-78b67658-386f-476e-831b-d916b5124b17)
2026-10-07 02:24:33  [ERROR]  bf81c81e-15e7-4ef2-b61b-e6181a9b8891 ->
METEORITE_FAILED_TECHNICAL_DO [_render_score: all literal X grades (12
vectors)]
2026-10-07 02:24:33  [INFO]  LLM openrouter host=DeepInfra
task=meteorite_grade_do 85.6s stop=end_turn tokens in=14290 out=4596
```

### Comments

#### chuckles — 2026-10-09T02:51:32.804Z
Heads-up from [AST-2097](https://linear.app/astralcareermatch/issue/AST-2097) (Susan picked **A**): the empty-rubric case is owned by [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092) on `ftr/AST-2019-rubric-empty-render-gate`. There, the Scheduled Actions token gate now flags an empty `{$RUBRIC_VECTORS}` / pinned rubric token. [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091) was to narrow to **duplicate codes**, plus a `run_task` refusal reusing the same `empty_render` check. As landed on PR #277, `rubric_dispatch_error` (`src/core/candidate.py`) still returns `Rubric '<rk>' is empty for this candidate.` If both PRs land, an empty rubric shows two Invalid reasons. Flag it `[bug]` in this UAT if you want that branch dropped here.

#### chuckles — 2026-10-09T02:49:03.509Z
Ready for UAT once [PR #277](https://github.com/susansomerset/astral/pull/277) (`ftr/AST-2013-rubric-dup-dispatch-gate` → `dev`) is merged. Fix child: [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091) (Hedy). Radia's review was clean, and all 28 repro tests pass.

**What to check on staging:**
1. Scheduled Actions: somerset's `meteorite_grade_do` / `grade_do` row shows **Invalid**, and the tooltip reads `Rubric 'do_rubric' has duplicate vector codes: TP`. AUTO and Run are disabled, and AUTO has been turned off.
2. Re-save somerset's Do rubric once in Artifacts. AST-2008's uptick renames the second `TP` to `TX`, and the row becomes valid again.
3. Re-run `meteorite_grade_do` for `bf81c81e-15e7-4ef2-b61b-e6181a9b8891` from `METEORITE_PASSED_JD`.
4. Expect AUTO to be forced off on any other rubric-backed row whose candidate has a duplicate or empty rubric. That's intended.

**Two pipeline issues to look at (no product impact):**
- Betty's AST-2091 test commit isn't on `origin/tests` yet. Several Betty sessions were sharing the `astral-tests` worktree at once, and `validate-tests-branch.sh` is failing on a stray merge commit. `resync-tests` at finish-up should settle it, but parallel Betty sessions on one worktree need a rule: one worktree per session, or run them serially.
- make-fix was spawned twice on AST-2091, 20 seconds apart, and I couldn't find the second caller. Both runs produced the same commit, `64bcc1935`.

---

_Implementation detail may live in git history on `origin/dev`._
