# AST-2091 — Scheduled Actions: block Auto/Run on duplicate or empty rubric (AST-2013 meteorite_grade_do all-X)

<!-- linear-archive: AST-2091 archived 2026-10-16 -->

## Linear archive (AST-2091)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2091/scheduled-actions-block-autorun-on-duplicate-or-empty-rubric-ast-2013  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-2013 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-78b67658-386f-476e-831b-d916b5124b17  
**Blocked by / blocks / related:** parent: AST-2013

### Description

## What this implements

The `fix` child for orphaned bug [AST-2013](https://linear.app/astralcareermatch/issue/AST-2013). Susan's ask: "Add 'duplicate vector codes' as a validation check on the scheduled actions page, not just empty tokens. Don't run the job if the rubric is bad/duped."

A rubric-backed Scheduled Actions row is **Invalid** when the candidate's current rubric for that task has duplicate vector codes or is empty. Invalid works the same way as the existing empty-token and missing-API-key checks:

* AUTO and Run/Sweep are disabled, with the reason in the tooltip.
* AUTO-on and Run return 400.
* An AUTO-on row is forced off.
* `dispatcher.run_task` refuses to start the job.

## To-be (from AST-2013)

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

## Scope

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

## Notes for planning

* No ancestor box was checked on AST-2013. The doc to patch is `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`, because AST-1780 built the list enrichment and the AUTO/Run gates this extends. Append a `## Bug: <this-id>` block there.
* Precedent: AST-1880 added the missing-API-key reason to the same `empty_render` / `invalid_reason` fields, and the UI already reads them.
* Must still hold: AST-2008's uptick on save, AST-1513's first-wins `_vector_labels_map` warning, and AST-1760's all-X routing.
* The full as-is, proposed steps, and original log are on parent AST-2013. Proposed step 5 there (re-save somerset's Do rubric) is a staging data step, not code.

## Git branch (authoritative)

Orphaned mini-parent: `ftr/AST-2013-rubric-dup-dispatch-gate`, child `sub/AST-2013/AST-2091-rubric-dup-dispatch-gate`. Seeded off `origin/dev` by bug-fix.

### Comments

#### radia — 2026-10-09T02:48:06.066Z
[code-rubric] PROCEED (Commit: 64bcc193) Rubric gate matches plan

#### betty — 2026-10-09T02:41:03.905Z
[bug-repro]
`origin/sub/AST-2013/AST-2091-rubric-dup-dispatch-gate` @ `2d6cd8eea` · repro lands red, awaits fix

#### joan — 2026-10-09T02:27:41.064Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:26:59.848Z
[board-betty] TESTS: REVISE
What: no bible entry (core/candidate.md, ui/api/api_admin.md, core/dispatcher.md) — missing [bug-repro] coverage for the rubric dispatch gate. Needs new tests for `rubric_dispatch_error` (duplicate and empty rubrics; craft and non-rubric tasks return None), for `list_dtasks` invalid_reason / AUTO forced off / key > rubric > tokens precedence, for AUTO-on create/update and Run returning 400, and for `run_task` returning False with AUTO forced off. Also needs a stub sweep of the existing AUTO-on / Run / `run_task` cases in test_api_admin.py and test_dispatcher.py (the evaluate_jd `run_task` cases read the rubric unstubbed).

#### hedy — 2026-10-09T02:26:03.799Z
`origin/sub/AST-2013/AST-2091-rubric-dup-dispatch-gate` @ `fb0e1801e` · rubric gate planned, three files

---

_Implementation detail may live in git history on `origin/dev`._
