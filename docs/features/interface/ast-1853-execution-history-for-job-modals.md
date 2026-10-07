# AST-1853 — Execution History for job modals

<!-- linear-archive: AST-1853 archived 2026-10-07 -->

## Linear archive (AST-1853)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1853/execution-history-for-job-modals  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The job modal's State History shows *what* happened to a job (each state and when) but not *why*. To see the prompt the agent got and the log lines the run wrote, Susan has to leave the modal, open Execution History, and hunt for the right batch by time and task. This ticket makes each state-history row a doorway to that run: click the row, and see the same agent prompt content and log content that Execution History shows when you expand that run. This makes debugging a job's path a single click from the job itself.

## Functional scope

1. **Clickable state rows (job modal only).** In the Job Detail modal, a State History row that was produced by a recorded run is clickable. Rows with no recorded run (manual skip, operator edit, legacy rows with no run id) render exactly as today and are not clickable. The Company modal's State History is unchanged.
2. **Run view from the row.** Clicking a row opens a view of that run showing (a) the agent prompt content: the same panes Execution History's batch link opens today, and (b) the log content: the same log table Execution History shows when a run row is expanded, including level colouring and the Copy control.
3. **Admin-only.** The run data comes from admin-gated endpoints, so rows are clickable only for admins. Non-admins see the plain timeline and the modal makes no admin API calls.
4. **Every new state row records the run that produced it.** When a job changes state inside a run, the history row records the id of the run that actually wrote the logs and agent data: the per-hop run for chained tasks, the dispatch batch for single-hop tasks. Today only the job's claim batch id is stored, and for chained tasks that id has no Execution History record. Forward-only: chained rows recorded before this ships are not back-matched (no timestamp heuristic) and may open an empty run view.

## Component scope

* `src/core/tracker.py`: **modified**. The job state transition writes each new state-history row, and it needs to record the executing run's id.
* `src/ui/frontend/src/components/BatchLogViewer.tsx`: **new**. The Execution History log table, moved out of the page so the job modal and Execution History share one component.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`: **modified**. Uses the shared log viewer instead of its private copy.
* `src/ui/frontend/src/components/BatchExecutionModal.tsx`: **new**. One modal for a single run id: agent prompt panes and log table.
* `src/ui/frontend/src/components/StateTimeline.tsx`: **modified**. Optional per-row click for rows that carry a run id. Callers that don't opt in (Company modal) are unchanged.
* `src/ui/frontend/src/components/JobDetailModal.tsx`: **modified**. Opts into clickable rows for admins and opens the run modal.

Tests and test-bible pages (`tests/component/core/test_tracker.py`, `tests/component/frontend/components/test_StateTimeline.test.tsx`, `test_JobDetailModal.test.tsx`, `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`, `docs/test-bible/core/tracker.md`, `docs/test-bible/frontend/components.md`, `docs/test-bible/frontend/pages.md`) belong to Betty in each child's `qa-child`. No file is deleted.

**Out of scope:** no new API route and no change under `src/ui/api/`. The existing `/api/agent_data/<batch_id>`, `/api/admin/timesheets`, `/api/admin/dispatch_ledger/<batch_id>` and `/api/admin/dispatch_ledger/<batch_id>/logs` already serve everything. No schema/column change. No change to Company modal or company transitions.

## Technical scope

* `src/core/tracker.py`: modified function (the job state-transition function that appends `state_history`). Each new history entry also records the current run's audit id (the active log batch context set per hop / per dispatch). The existing `batch_id` key stays as-is so nothing that reads it breaks. When no run context is active (manual/operator transitions), the new key is absent. Key name is `plan-child`'s call.
* `src/ui/frontend/src/components/BatchLogViewer.tsx`: new component. Takes the log rows, the loading flag, and an optional level filter, and renders the toolbar, Copy, and table exactly as `AdminPerformanceMonitor`'s private viewer does today (moved, not copied).
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`: modified. Its private log viewer function is removed and the shared component imported. Fetch, cache, and filter behaviour stay unchanged.
* `src/ui/frontend/src/components/BatchExecutionModal.tsx`: new component. Given a run id, renders the existing `BatchAgentDataPanes` (from `BatchAgentDataModal.tsx`, reused, not forked) plus the shared log viewer, fed from `GET /api/admin/dispatch_ledger/<id>/logs`. Closing it returns to the job modal.
* `src/ui/frontend/src/components/StateTimeline.tsx`: modified. Entry type gains the run-id key. New optional selection callback. A row is clickable only when a callback is supplied **and** the entry resolves a run id (the new key, falling back to `batch_id` for rows recorded before this ships).
* `src/ui/frontend/src/components/JobDetailModal.tsx`: modified. `state_history` entry type widened. Passes the callback only when `useAuth().isAdmin`. Holds the selected run id and renders `BatchExecutionModal`.

## Architectural definition

* **Patterns to reuse:** no established pattern applies. The in-force pattern roster (`canon_clerk.py index`) covers artifacts, entity batching and task chains, not UI modal composition.
* **New patterns proposed:** none.
* **Applicable statutes:**
  * `astral.entity.required-metadata`: `state_history` and `batch_id` are part of the fixed entity metadata set. This epic adds a key *inside* history entries and must not add, rename or drop a column. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.entity.required-metadata.md>)
  * `astral.standards.dry-and-focused-functions`: the log viewer moves to one shared component. A second copy in the job modal is a defect. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
  * `astral.ui.frontend-file-placement`: the two new components go in `src/ui/frontend/src/components/`. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>)

## Acceptance criteria

 1. **Single-hop run stamp.** Component test in `tests/component/core/test_tracker.py`: with the run context set to `X` and the job's `batch_id` also `X`, a transition appends an entry whose run-id key equals `X`. Fail = key missing or different.
 2. **Chained-hop run stamp.** Same test file: with the run context set to hop id `H` and the job's `batch_id` set to a different claim id `C`, the new entry's run-id key equals `H` (not `C`), and `batch_id` still equals `C`. Fail = run id equals `C` or is absent.
 3. **No run context → no stamp.** Transition with no run context (e.g. `POST /api/jobs/<id>/skip`) appends an entry with no run-id key. The row is not clickable in the modal. Fail = key present with a null/empty value, or row clickable.
 4. **Admin click opens the run.** `test_JobDetailModal.test.tsx`: as admin, clicking a row whose entry carries run id `R` calls `GET /api/admin/dispatch_ledger/R/logs` and `GET /api/agent_data/R`, and renders a returned log message and an agent-data block. Fail = either call missing or content not rendered.
 5. **Non-admin sees no link.** Same test, `isAdmin=false`: rows have no click affordance and no `/api/admin/` request is made. Fail = any `/api/admin/` fetch or a clickable row.
 6. **Legacy rows fall back to** `batch_id`**.** An entry with only `batch_id: "B"` (no run-id key) is clickable for admins and opens run `B`. An entry with neither is not clickable. Fail = either inverted.
 7. **One log viewer.** `grep -rn "dispatch-log-table" src/ui/frontend/src --include=*.tsx` matches only `components/BatchLogViewer.tsx`, and `grep -n "function LogViewer" src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` returns nothing. Fail = the table markup exists in two files (a copy-paste instead of the shared component).
 8. **Execution History unchanged.** `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` passes with no assertion edits beyond imports. Fail = any behavioural assertion had to change.
 9. **Company modal unchanged.** `tests/component/frontend/components/test_CompanyDetailModal.test.tsx` passes unedited, and Company State History rows are not clickable. Fail = test edit needed or rows clickable.
10. **No API or schema change.** `git diff origin/dev...<ftr> -- src/ui/api/ src/data/` is empty. Fail = any change there.

## Open questions

None.

## Proposed child tickets

#### 1!: **Record the producing run on each job state row - Katherine**

Job state transitions record the id of the run that actually wrote the logs and agent data (per-hop for chains, dispatch batch for single-hop) on each new state-history entry, alongside the existing `batch_id`. Backend only, with no UI. Child 2 reads the key this child names.
**Citations:** `astral.entity.required-metadata`.
**Scope:** `src/core/tracker.py`: modified function (the job state-transition function that appends `state_history`). Each new history entry also records the current run's audit id (the active log batch context set per hop / per dispatch). The existing `batch_id` key stays as-is so nothing that reads it breaks. When no run context is active (manual/operator transitions), the new key is absent. Key name is `plan-child`'s call.
Estimate: 2

#### 2: **Clickable job state history opens the run - Ada**

Admins can click a job modal State History row to open that run's agent prompt panes and log table, which are the same views Execution History uses. The log table is moved into one shared component. Non-admins and the Company modal are unchanged. Comes after #1, because it reads #1's run-id key and falls back to `batch_id`.
**Citations:** `astral.standards.dry-and-focused-functions`, `astral.ui.frontend-file-placement`.
**Scope:**

* `src/ui/frontend/src/components/BatchLogViewer.tsx`: new component. Takes the log rows, the loading flag, and an optional level filter, and renders the toolbar, Copy, and table exactly as `AdminPerformanceMonitor`'s private viewer does today (moved, not copied).
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`: modified. Its private log viewer function is removed and the shared component imported. Fetch, cache, and filter behaviour stay unchanged.
* `src/ui/frontend/src/components/BatchExecutionModal.tsx`: new component. Given a run id, renders the existing `BatchAgentDataPanes` (from `BatchAgentDataModal.tsx`, reused, not forked) plus the shared log viewer, fed from `GET /api/admin/dispatch_ledger/<id>/logs`. Closing it returns to the job modal.
* `src/ui/frontend/src/components/StateTimeline.tsx`: modified. Entry type gains the run-id key. New optional selection callback. A row is clickable only when a callback is supplied **and** the entry resolves a run id (the new key, falling back to `batch_id` for rows recorded before this ships).
* `src/ui/frontend/src/components/JobDetailModal.tsx`: modified. `state_history` entry type widened. Passes the callback only when `useAuth().isAdmin`. Holds the selected run id and renders `BatchExecutionModal`.
  Estimate: 3

**New patterns:** none.

**Monolith check:** Functional scope has 4 items and there are 2 children. Split: the backend run stamp (#1) and the UI (#2).

**Scope partition check:** `tracker.py` → #1. All five frontend files → #2. No file is unclaimed and none is claimed twice.

---

## Original brief

View the agent prompt content and log content when I click on the state history element on the job modal, just as if I was clicking open the execution history for the run.

### Comments

#### chuckles — 2026-09-29T18:03:59.624Z
AST-1864 estimate 2→1 — one helper, two call sites in tracker.py, no schema/API change.

#### chuckles — 2026-09-29T17:32:54.220Z
@susan

1. **Chained runs recorded before this ships.** Chained tasks (build-artifacts daisy chain, qualify → evaluate JD) write their logs under per-hop run ids that job state history doesn't store today. My proposal: record the hop's run id on new rows from now on. Old single-hop rows will still link, because their `batch_id` is the run id. Old chained rows will open an empty run view. Is forward-only OK? The alternative is back-matching old rows to runs by task and timestamp, which is a heuristic, so I won't add it without your go-ahead.
2. **Admin-only.** The prompt and log endpoints are admin-gated. Should clickable rows be admins-only (candidates see the plain timeline)?
3. **Linear project.** The ticket has no project. Should it be **Astral Interface** (plan docs under `docs/features/interface/`)?

---

_Implementation detail may live in git history on `origin/dev`._
