# AST-1496 — Ban automatic dispatch_task seed and provision writers

<!-- linear-archive: AST-1496 archived 2026-09-09 -->

## Linear archive (AST-1496)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1496/ban-automatic-dispatch-task-seed-and-provision-writers  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1456 — DO NOT OVERWRITE DISPATCH_TASK IN ANY ENVIRONMENT EVER  
**Blocked by / blocks / related:** parent: AST-1456

### Description

## What this implements

Stop every automatic path that inserts or updates live `dispatch_task` rows (scheduler-start provision, seed/upsert scripts, ensure-time content writers). Operator-curated schedule rows must survive restart in every environment. When new rows are needed, SQL goes in a Linear comment for Susan to run after restart — no seed scripts.

## As-is

Automatic paths still insert or update live `dispatch_task` rows; curated schedule data has been overwritten incorrectly and work was lost.

## To-be

No product/boot/scheduler/seed path may create, update, or recreate `dispatch_task` rows. Needed seed SQL is delivered only as Linear comment text for Susan.

## Boundaries

Does not redesign Manage Dispatch UI. Does not change dispatcher claim/runtime bookkeeping (`last_run_at`, max_runs disable). Schema DDL for `dispatch_task` may remain; content seed must not.

## Scope

## Component scope

* `src/core/dispatcher.py` — modified: remove/disable scheduler-start provision that inserts `dispatch_task` rows via `save_dispatch_task`.
* `src/data/database.py` — modified: keep schema ensure; stop any remaining automatic content INSERT/UPDATE of live `dispatch_task` rows beyond operator APIs and harmless runtime bookkeeping (`last_run_at` / max_runs disable).
* `src/utils/config.py` — modified: retire or clearly demote `SEED_CONFIG` `dispatch_task-*` and Python meteorite dispatch catalogs so they are not an executable seed path.
* `scripts/push_tables_to_prod.py` — modified: refuse `dispatch_task` (or remove as a supported table) so push never overwrites schedule rows.
* `scripts/upsert_tables_from_prod.py` — modified: same ban for `dispatch_task`.
* `debug/startup_db_inventory.md` — modified: document the ban and remaining writers so the inventory matches reality.

## Technical scope

* `src/core/dispatcher.py` — modified function(s): `start_scheduler` and/or `provision_meteorite_dispatch_tasks` / `provision_meteorite_email_dispatch_tasks` — stop calling `database.save_dispatch_task` on tick-daemon start so restart cannot invent or alter schedule rows.
* `src/data/database.py` — modified function(s): `_ensure_dispatch_task_schema` and any sibling ensure helpers — no recurring content seed/upsert of `dispatch_task`; operator `save_dispatch_task` / `update_dispatch_task` and dispatcher bookkeeping remain.
* `src/utils/config.py` — modified catalog/register: `SEED_CONFIG` entries keyed `dispatch_task-*` and related provision catalogs — not wired for auto-execution; SQL text may live only as copy-paste material for Linear comments, not as a boot path.
* `scripts/push_tables_to_prod.py` / `scripts/upsert_tables_from_prod.py` — modified CLI/table gate: hard-fail or skip when the table is `dispatch_task`.
* `debug/startup_db_inventory.md` — modified doc: automatic `dispatch_task` writer list emptied / marked removed so future audits do not miss a path.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1456-do-not-overwrite-dispatch-task`, child `sub/AST-1456/<this-id>-fix-ban-dispatch-task-auto-writers`. Created at bug-fix dispatch.

## Notes for planning

Orphaned mini-parent AST-1456. No ancestor checkbox was approved — plan from this Description / ## Scope only. Prior related history (context only, not binding parent): AST-741/AST-745 (stop retry auto-seed + inventory), AST-1108 (SQL-first SEED_CONFIG).

## Proposed change (make-fix)

- [X] `start_scheduler` no longer calls meteorite / meteorite_email / fetch_email provision
- [X] `_ensure_dispatch_task_schema` is DDL-only (content backfills/retargets removed)
- [X] `SEED_CONFIG` dispatch_task-* / `METEORITE_DISPATCH_TASKS` demoted (Linear paste / non-executable)
- [X] push/upsert scripts hard-fail on `dispatch_task`
- [X] `debug/startup_db_inventory.md` refreshed for AST-1496 ban

### Comments

#### radia — 2026-08-26T16:06:18.657Z
[code-rubric] REVIEW (Commit: 8256593d) Ban dispatch auto-writers OK

discuss: archie-catalog-wins carve-out → sibling AST-1501. Hold-bullet vs retire-delete wording. Dead helpers / default-all script ergonomics advisory only.

#### joan — 2026-08-26T15:47:20.022Z
[board-joan]  CANON: REVISE
What: astral.seed.archie-catalog-wins — dispatch_task boot/catalog ensure banned; operator curation sole content writer — carve out AST-1456 policy (+ sibling seed statutes)

context_tokens≈12000

#### betty — 2026-08-26T15:45:40.233Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/dispatcher.md — broken TestAst1054/TestAst1088 start_scheduler provision asserts (+ TestAst703 ensure content migrations) — missing ban coverage for no-write restart / script hard-fail

#### hedy — 2026-08-26T15:44:15.582Z
`origin/sub/AST-1456/AST-1496-fix-ban-dispatch-task-auto-writers` @ `36252ae6fb9428f1c7f6fa30b41ec76c2e818bc8` · ban auto writers planned

#### chuckles — 2026-08-26T15:38:17.453Z
[bug-fix] Authorized stub plan doc for this mini-epic (no ancestor checkbox):

`docs/features/foundation/ast-1456-do-not-overwrite-dispatch-task.md`

on `origin/sub/AST-1456/AST-1496-fix-ban-dispatch-task-auto-writers`. Re-spawning plan-fix with that path.

#### hedy — 2026-08-26T15:37:36.468Z
[plan-fix] Doc resolve blocked — @chuckles

No ancestor checkbox was approved on AST-1456, and there is no existing `docs/features/**` plan doc for AST-1456 or AST-1496 to patch. plan-fix never creates a new plan doc.

Three unchecked ancestor candidates (cannot pick without guessing):
- `docs/features/roster/ast-741-stop-rebuilding-unnecessary-dispatch-task-data.md`
- `docs/features/roster/ast-745-stop-dispatch-retry-auto-seed-and-startup-db-inventory.md`
- `docs/features/foundation/ast-1108-fix-broken-seed-data.md`

Need either (a) one approved ancestor path seeded into the plan-fix prompt, or (b) a stub plan doc path Chuckles authorizes for this mini-epic. Re-spawn after that.

---

_Implementation detail may live in git history on `origin/dev`._
