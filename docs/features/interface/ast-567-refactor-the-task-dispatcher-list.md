# AST-567 — Refactor the Task Dispatcher List

<!-- linear-archive: AST-567 archived 2026-06-15 -->

## Linear archive (AST-567)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-567/refactor-the-task-dispatcher-list  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Scheduled Actions admin screen (route `/admin/scheduled_actions`) is the operational home for per-candidate dispatch_task rows: scheduling, manual run/stop, AUTO and debug toggles, and add/edit modals. As the task catalog grows across pipeline phases, a single flat table is hard to scan and does not reflect how tasks are ordered in the product configuration. This feature improves administrator usability by presenting dispatch rows in the same phase-grouped, sequence-ordered structure already used on Manage Tasks, and by aligning user-visible naming with the established route and screen identity ("Scheduled Actions") instead of the legacy "Task Dispatcher" label.

## Functional scope

* **Phase-grouped list:** Split the dispatch task list into collapsible sections keyed by each row's task catalog **phase** (the same phase labels used on Manage Tasks, e.g. pipeline letter prefixes), not a single monolithic table.
* **Sequence ordering within sections:** Within each phase section, order rows by task **seq** from the task catalog (ascending), then stable tie-breakers so Susan can see pipeline order when creating or reviewing dispatch records for a candidate.
* **Reuse existing UI patterns:** Use the same **CollapsiblePanel** section pattern as Manage Tasks—one panel per phase, each containing the existing Scheduled Actions table (columns, row click-to-edit, Run/Stop, AUTO, Dbg, Stop All, Add Task, and filters). No new bespoke section chrome unless a thin shared wrapper is warranted during implementation.
* **Collapsible behavior:** Support zero, one, or multiple expanded sections at once, consistent with Manage Tasks and CollapsiblePanel rules (including zero expanded).
* **Preserve current capabilities:** Candidate-scoped filtering, task-key filter, thread-status polling, modals, and API behavior remain unchanged; only list presentation and labeling change.
* **Navigation and title alignment:** Change the Admin sidebar label from "Task Dispatcher" to **Scheduled Actions** to match the route and screen code. Update the page heading to **Scheduled Actions** so nav, title, and URL naming are consistent. Do not change the URL path (`/admin/scheduled_actions`).
* **Task metadata for grouping/sort:** Ensure the admin UI can resolve **phase** and **seq** for each `task_key` when building sections and default sort (same catalog metadata Manage Tasks uses), including keys that appear only on existing dispatch rows.

## Boundaries

* Does not change dispatcher execution, scheduler threads, `dispatch_task` schema, or CRUD API contracts beyond exposing task-catalog phase/seq metadata if not already available to this screen.
* Does not refactor Manage Tasks or extract a mandatory shared "sectioned admin table" package—follow the Manage Tasks pattern locally unless duplication is clearly painful.
* Does not rename routes, move the screen under a different path, or redesign columns/modals.
* Does not add debug-logging requirements (frontend-only; [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) does not apply).
* Must not break existing component tests for Scheduled Actions; update expectations where titles change to Scheduled Actions.

## Acceptance criteria

1. Admin sidebar shows **Scheduled Actions** (not Task Dispatcher) linking to `/admin/scheduled_actions`.
2. Page primary heading reads **Scheduled Actions**.
3. With multiple dispatch rows spanning at least two phases, the list renders as separate collapsible phase sections; each section's table retains all current columns and interactions.
4. Within a phase section, rows appear in ascending **seq** order for their `task_key` per the task catalog.
5. Susan can collapse all sections (zero expanded) without UI errors.
6. Task filter and selected-candidate filter still restrict which rows appear; empty sections are omitted or show an appropriate empty state without breaking layout.
7. Stop All, Add Task, run/stop, AUTO, Dbg, and edit modal flows behave as before.

## Dependencies and blockers

* [AST-347](https://linear.app/astralcareermatch/issue/AST-347/task-dispatcher-sorting) (Task Dispatcher Sorting, Done) — prior sort-by-pipeline work; this feature adds visible phase sections and completes label alignment. No open blockers.

## Open questions

None.

---

## Original brief

Now that our tasks are getting broader, we should segment this table as we do for the manage tasks screen, and list them in order by task key sequence id.

Do we have an existing component that can handle the sections while reusing the special table component we already have on that "scheduled_actions" screen?

Also, this is a good time to align the navigation to "Scheduled Actions" to match the code for the UI.

### Comments

#### susan — 2026-06-03T20:32:41.102Z
Hubboy.  I think this is actually a symptom of a deeper problem.  Let's wrap this ticket up and I'll open another for the backlog.

#### chuckles — 2026-06-03T20:31:26.756Z
## Manual test steps (prep-uat re-run 2026-06-03)

Prerequisites: local **`dev`** @ **`8b5c73bc`** (land-ftr merged **`origin/ftr/ast-567`** @ **`fc7dbfb3`**). Restart Flask + Vite if already running.

1. Admin sidebar → **Scheduled Actions** (not Task Dispatcher); URL `/admin/scheduled_actions`; page heading **Scheduled Actions**.
2. Select a candidate with a **`consult_do`** dispatch row.
3. Confirm **`consult_do`** appears under **D. Job Analysis** (not `(unassigned)`), ordered by catalog **seq** with sibling job-analysis tasks.
4. Optional API: `GET /api/admin/dispatch_tasks/task_keys` → `consult_do.phase` = phase of **`grade_do`** in `TASK_CONFIG`; `consult_do.seq` = **3**.
5. With rows in **two+** phases, confirm collapsible phase sections; collapse all sections (zero expanded) — no layout errors.
6. Task filter + candidate filter still work; empty phases omitted or sensible empty state.
7. Exercise Run, Stop, AUTO, Dbg, row edit, Add Task, Stop All — unchanged behavior.

`origin/ftr/ast-567` @ `fc7dbfb3` · local `dev` merged @ `8b5c73bc`. Child **AST-568** stays User Testing / assignee Katherine.

Reset after UAT: `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-06-03T19:11:36.619Z
[check-linear]

**Your consult_do / grade_do question**

**Where the keys live**

- **`consult_do`** is a **dispatch** `task_key` — it appears on `dispatch_task` rows and in `DISPATCH_SCHEDULABLE_TASK_KEYS` (`src/utils/config.py`). It is the name Susan schedules and sees in the Scheduled Actions table column **Task**.
- **`grade_do`** is the **agent / TASK_CONFIG** entry that holds the real prompt, phases, seq, grading schema, pass/fail states, etc. (`TASK_CONFIG["grade_do"]` — phase **`D. Job Analysis`**, **seq 3**).

**Why consult_do runs grade_do (consult.py)**

This is intentional dispatch-vs-agent naming, not a bug in consult routing:

- `src/utils/config.py` maps dispatch wrappers → catalog keys via `resolve_dispatch_task_config_key()` (`consult_do` → `grade_do`, same for get/like).
- `src/core/consult.py` uses that mapping when building orchestration: e.g. `run_consult_task(..., dispatch_task_key="consult_do")` resolves the TASK_CONFIG row through `_consult_orchestration` / `resolve_dispatch_task_config_key`, then runs the **grade_do** batch path (`consult_do_batch` → grade_do prompts). The **row still stores `task_key = consult_do`**; execution follows the grade_do config.

So: **dispatch identity = `consult_do`**; **prompt/catalog identity = `grade_do`**. That split predates AST-568.

**What AST-568 changed (and the UAT gap you saw)**

AST-568 (child) added phase-grouped UI + nav rename. Grouping uses each **dispatch row’s `task_key`** (correct — that is the “calling” dispatch key), but metadata comes from **`GET /api/admin/dispatch_tasks/task_keys`**, which returns `phase` / `seq` per key.

**First UAT build (`6a998581`):** `_dispatch_task_key_form_meta` looked up `TASK_CONFIG.get(task_key)` **literally**. There is no `TASK_CONFIG["consult_do"]`, only `grade_do` — so `phase`/`seq` were null → UI bucket **`(unassigned)`** even though the row correctly said `consult_do`.

**Fix on `origin/ftr/ast-567` (`fc7dbfb3`):** phase/seq now resolve through the same catalog mapping consult already uses:

- `catalog_key = resolve_dispatch_task_config_key(task_key)` then `TASK_CONFIG[catalog_key]` for **phase** / **seq** (entity/trigger still use `dispatch_task_admin_defaults` for schedulable keys per AST-549).
- Component test: `test_ast549_task_keys_config_derivation_authoritative` asserts `consult_do` gets `grade_do`’s phase and seq.

**Files touched (AST-568 + UAT fix)**

| Area | File |
|------|------|
| Phase sections + title | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — sections from `allTaskKeys[row.task_key].phase` / seq sort within section |
| Nav label | `src/utils/config.py` (`NAV_CONFIG` → Scheduled Actions) |
| task_keys metadata | `src/ui/api/api_admin.py` — `_dispatch_task_key_form_meta`, `dispatch_task_keys` |
| Catalog mapping (existing) | `src/utils/config.py` — `resolve_dispatch_task_config_key`, `_CONSULT_TASK_TO_AGENT_TASK` |
| Runtime consult | `src/core/consult.py` — unchanged by AST-568; already maps consult_* → grade_* |
| Tests | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`, `tests/component/ui/api/test_api_admin.py` |

**UAT on `origin/ftr/ast-567` @ `fc7dbfb3`**

1. Restart app; merge/pull `origin/ftr/ast-567` (or local `dev` if already landed from prep-uat).
2. **Scheduled Actions** → pick a candidate with a **`consult_do`** dispatch row.
3. Row should appear under **`D. Job Analysis`** (not `(unassigned)`), ordered by **seq** with other job-analysis tasks.
4. Optional API check: `GET /api/admin/dispatch_tasks/task_keys` → `consult_do.phase` == `"D. Job Analysis"`, `consult_do.seq` == `3`.
5. Re-run prior acceptance steps (collapsible sections, filters, run/stop, modals) — unchanged scope.

No dispatcher/schema change; only admin metadata mapping for display.

— Chuckles

#### katherine — 2026-06-03T19:05:58.258Z
[check-linear] UAT concern — consult_do phase/seq via catalog mapping on origin/ftr/ast-567 (@susan)

#### susan — 2026-06-03T19:00:40.230Z
Hmm.  Something is not right.  Why do we have task_key of "consult_do" that actually runs "grade_do" task?  Is that a core consult.py thing?  Where are those two established?  In the config?  if so, that's fine, but the grouping should be on the dispatch task's "calling" task_key, not the consult key.

For example, "consult_do" appears under "unassigned", instead of under "Job Analysis".  We don't need to change anything significant, we just need to map the groups and sequences through to the dispatch wrappers.

#### chuckles — 2026-06-03T18:39:22.807Z
## Manual test steps

1. Restart the app if it is already running (local `dev` @ `6a998581`).
2. Log in as admin → open **Scheduled Actions** in the sidebar (label must not read "Task Dispatcher").
3. Confirm URL stays `/admin/scheduled_actions` and the page heading reads **Scheduled Actions**.
4. Pick a candidate with dispatch rows spanning **at least two** `TASK_CONFIG` phases → confirm rows appear in **collapsible phase sections** (same `CollapsiblePanel` feel as Manage Tasks).
5. Within one phase section, confirm row order follows ascending catalog **seq** for each `task_key`.
6. Collapse **all** sections (zero expanded) — no errors or layout break.
7. Use **task filter** and **candidate filter** — only matching rows/sections show; empty phases omitted or show sensible empty state.
8. Exercise **Run**, **Stop**, **AUTO**, **Dbg**, row click-to-edit, **Add Task**, and **Stop All** — same behavior as before the refactor.
9. (API spot-check, optional) `GET /api/admin/dispatch_tasks/task_keys` includes `phase` and `seq` for catalog keys (config-authoritative defaults per AST-549).

`origin/ftr/ast-567` @ `6a998581` · local `dev` merged (§8). Restart app if running.
Reset: `git reset --hard origin/dev`

— Chuckles

#### susan — 2026-06-03T18:30:33.733Z
Okay, Please work with Katherine (in her conversation context) to resolve merge conflicts between ftr/ast-567 and local dev, then push those changes to the ftr branch on origin and continue finishing prep-uat.

#### chuckles — 2026-06-03T14:49:01.344Z
@susan — prep-uat blocked: `land-ftr` merge of `origin/ftr/ast-567` into local `dev` conflicts in `docs/ASTRAL_TEST_BIBLE.md`, `src/ui/api/api_admin.py`. Resolve on `dev`, then re-run prep-uat AST-567.

— Chuckles

#### chuckles — 2026-06-03T14:29:35.339Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-567 (parent) | ftr/ast-567 |
| AST-568 | sub/AST-567/AST-568-scheduled-actions-phase-sections |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | fa11e2c3-995f-47e4-970c-adb019131a73 | AST-567 (parent) | git |
| Katherine | 0c573daa-659d-4844-99c6-b3c4b4473245 | AST-568 | engineer |
| Betty | ad02ae54-a3d3-4f80-8b75-bc433f1ce1a7 | AST-568 | qa |
| Radia | aab12b77-cb88-4d5c-aeaf-1a963ea762eb | AST-568 | review |

**Parent:** AST-567

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
