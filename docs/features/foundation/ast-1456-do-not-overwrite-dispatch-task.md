<!-- linear-archive: AST-1456 archived 2026-09-09 -->

## Linear archive (AST-1456)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1456/do-not-overwrite-dispatch-task-in-any-environment-ever  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Automatic paths (scheduler-start provision catalogs, seed/upsert scripts, and any remaining ensure-time writers) still insert or update live `dispatch_task` rows. Operator-curated schedule rows have been overwritten or recreated incorrectly across environments, and Susan has already lost real work from a bad auto-update.

## To-be

Nothing in product code, boot, scheduler start, or seed/upsert scripts may create, update, or recreate `dispatch_task` rows in any environment. When new schedule rows are genuinely needed, the only delivery mechanism is SQL statements posted in a Linear comment for Susan to run herself after restart — no seed scripts, no silent provision, no table push/upsert of `dispatch_task`.

## Proposed steps

1. Remove or hard-disable every automatic `dispatch_task` writer that still runs on scheduler start or boot — starting with `provision_meteorite_dispatch_tasks` / `provision_meteorite_email_dispatch_tasks` (and any sibling provision/ensure that calls `save_dispatch_task` without an operator action).
2. Ban `dispatch_task` as a target of seed/upsert/push scripts (`scripts/push_tables_to_prod.py`, `scripts/upsert_tables_from_prod.py`, and any other table-copy path that upserts that table).
3. Leave schema DDL alone; stop content-mutating ensure/backfill that rewrites live schedule fields. Refresh `debug/startup_db_inventory.md` so the automatic column for `dispatch_task` is empty (operator + runtime bookkeeping only).
4. Retire in-repo `SEED_CONFIG` / catalog-driven seed for `dispatch_task-*` as an executable path; when rows must be added, post the SQL in the Linear ticket comment for Susan — do not ship a script that runs it.
5. Smoke: restart local (and staging once landed) and confirm curated `dispatch_task` rows are byte-stable across restart with no new inserts/updates from provision or seed.

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

## Ancestor candidates

- [ ] AST-741 — Stop rebuilding unnecessary dispatch_task data (`docs/features/roster/ast-741-stop-rebuilding-unnecessary-dispatch-task-data.md`) — parent epic whose purpose was exactly "automatic writers must not override Susan's dispatch curation"
- [ ] AST-745 — Stop dispatch retry auto-seed and startup DB inventory (`docs/features/roster/ast-745-stop-dispatch-retry-auto-seed-and-startup-db-inventory.md`) — child that removed `*_RETRY` / `gaze_board` auto-INSERT and produced `debug/startup_db_inventory.md`
- [ ] AST-1108 — Fix broken seed data (`docs/features/foundation/ast-1108-fix-broken-seed-data.md`) — seed-policy home; SQL-first `SEED_CONFIG` for non-JSON tables including `dispatch_task`, with deferred Track 1 audit of remaining ensure-time writers

## Original report

OH MY GOD I HAVE LOST WORK BECAUSE WE AUTO UPDATED RECORDS IN DISPATCH TASKS AND DID IT WRONG ON TOP OF THAT.

NO MORE SEED SCRIPTS.  ONLY SQL COMMANDS IN THE LINEAR COMMENT WITH SEED  CONTENT FOR SUSAN TO RUN AFTER RESTART.  DO NOT TOUCH IT AGAIN.  EVER.

ARE WE CLEAR?

### Comments

#### chuckles — 2026-08-19T20:52:04.810Z
[thread-missing] Cursor chat `6cb67498-3fd6-4fee-9d87-5e679e4e1a9d` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/6cb67498-3fd6-4fee-9d87-5e679e4e1a9d/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `4347aade-434b-4e37-bb53-2b209272c13a`.

Watcher rule `bug-find` on `AST-1456` (Thread owner `AST-1456`).

---

# AST-1456 — Do not overwrite dispatch_task in any environment ever

Orphaned Bug mini-epic. Stub authorized by Chuckles at bug-fix so plan-fix has a doc to patch (no ancestor checkbox approved; plan-fix never creates a new plan doc).

## Purpose

Operator-curated `dispatch_task` rows must never be created, updated, or recreated by automatic product/boot/scheduler/seed paths. Needed seed SQL is delivered only as Linear comment text for Susan to run after restart.

## Related history (context only)

- AST-741 / AST-745 — stop retry / gaze_board auto-seed; startup inventory
- AST-1108 — SQL-first SEED_CONFIG scaffolding (not an executable auto path for this ban)

## Bug: AST-1496 — Ban automatic dispatch_task seed and provision writers

### As-is

On every scheduler start, `start_scheduler` still runs `provision_meteorite_dispatch_tasks`, `provision_meteorite_email_dispatch_tasks`, and `ensure_fetch_email_dispatch_task`, each of which calls `database.save_dispatch_task` and can invent or recreate schedule rows. `_ensure_dispatch_task_schema` still runs recurring NULL-column / `score_floor` backfills and legacy content UPDATE/DELETE retargets on live rows. `scripts/push_tables_to_prod.py` and `scripts/upsert_tables_from_prod.py` still accept `dispatch_task` (including when defaulting to all `ALLOWED_CONFIG_TABLES`). `SEED_CONFIG` `dispatch_task-*` SQL and `METEORITE_DISPATCH_TASKS` remain the catalogs those provision helpers execute against. Inventory `debug/startup_db_inventory.md` is stale (last AST-745) and omits these provision writers.

### To-be

No product/boot/scheduler/seed/upsert path may create, update, or recreate `dispatch_task` rows. Restart leaves curated rows byte-stable aside from harmless runtime bookkeeping (`last_run_at`, max_runs → `enabled=False`). Schema DDL ensure may remain. Operator Manage Dispatch create/edit and Susan-run SQL remain the only content writers. When new rows are needed, SQL is posted in a Linear comment for Susan — no seed script, no silent provision.

### Repro

1. Note current `dispatch_task` row set for a candidate that already has curated rows (or deliberately omit a meteorite / `fetch_email` row Susan does not want).
2. Restart the app so `start_scheduler` runs (local or staging).
3. Observe new or altered `dispatch_task` rows from meteorite / meteorite_email / fetch_email provision, and/or ensure-time backfill UPDATEs on NULL / legacy fields.
4. Optionally run `python3 scripts/push_tables_to_prod.py dispatch_task` or `python3 scripts/upsert_tables_from_prod.py dispatch_task` (or either with no table args) and observe schedule rows overwritten across environments.

### Root cause

Scheduler boot still treats Python catalogs (`METEORITE_DISPATCH_TASKS`, `METEORITE_EMAIL_MAILBOX_CONFIG`, `FETCH_EMAIL_CONFIG`) and ensure-time backfills as authority over the live `dispatch_task` table. Seed/push/upsert scripts still treat `dispatch_task` as a normal config table. Operator curation is not the sole writer of schedule content.

### Proposed change

1. **`src/core/dispatcher.py` — `start_scheduler`:** Remove the try/except blocks that call `provision_meteorite_dispatch_tasks()`, `provision_meteorite_email_dispatch_tasks()`, and `ensure_fetch_email_dispatch_task()`. After this change, tick-daemon start must not call `database.save_dispatch_task` (directly or via those helpers). Leave the helper functions in the module for now but unused from boot (no alternate automatic caller exists today); do not wire them to any other start/bootstrap path. Do **not** change dispatcher claim/runtime bookkeeping (`update_dispatch_task` for `last_run_at` / max_runs disable) or Manage Dispatch wrappers.

2. **`src/data/database.py` — `_ensure_dispatch_task_schema`:** Keep table CREATE, `ALTER TABLE … ADD COLUMN`, and structural unique-index / table rebuilds that copy existing cell values unchanged. Remove recurring content writers inside this helper:
   - NULL-column backfill loop that `UPDATE`s from `dispatch_task_admin_defaults`
   - `score_floor IS NULL` → `1.0` backfill on scored triggers
   - Legacy content UPDATE/DELETE retargets (e.g. gaze `sort_by`, `locate_job_page` → `find_job_page`, prefilter / `prefilter_company` / consult→grade key rewrites, and sibling DELETE/UPDATE blocks of the same kind)
   Leave `save_dispatch_task` / `update_dispatch_task` (operator + runtime bookkeeping) unchanged. Do not remove `dispatch_task` from `ALLOWED_CONFIG_TABLES` in this ticket (API operator upsert stays; scripts gate separately).

3. **`src/utils/config.py`:** Demote `SEED_CONFIG` keys `dispatch_task-meteorite` and `dispatch_task-fetch-email` — keep the SQL strings as Linear copy-paste material only; update the register comment so they are explicitly **not** an executable boot/provision path and must never be wired to auto-execution. Banner `METEORITE_DISPATCH_TASKS` the same way (catalog may remain for documentation / asserts; not an executable seed path once provision call sites are gone). Do not add a runner that executes `SEED_CONFIG` for these keys.

4. **`scripts/push_tables_to_prod.py` and `scripts/upsert_tables_from_prod.py`:** Hard-fail before any DB/network work when `dispatch_task` is in the resolved table list (explicit CLI arg **or** default-all). Print a clear ERROR that `dispatch_task` is banned and exit non-zero. Default-all must therefore never push/upsert `dispatch_task` (either exclude it from the default set then still hard-fail if named, or hard-fail whenever the resolved list contains it — prefer hard-fail on presence so an explicit `dispatch_task` arg cannot sneak through).

5. **`debug/startup_db_inventory.md`:** Refresh the `dispatch_task` **Automatic (recurring)** section so it no longer lists provision/ensure content writers as live. Document the ban: automatic INSERT/content-UPDATE paths for `dispatch_task` are removed (AST-1496); remaining automatic touches are runtime bookkeeping only (`last_run_at`, max_runs disable). Note schema DDL ensure remains. Bump **Last updated** to AST-1496.

### Blast radius

- Scheduler start no longer auto-creates meteorite / meteorite_email / fetch_email schedule rows — environments that relied on provision after adding a candidate will need Susan-run SQL (post the `SEED_CONFIG` SQL or equivalent in a Linear comment).
- `retire_candidate_requested_wrapper_dispatch_tasks()` still runs from `start_scheduler` and **deletes** retired wrapper keys; that path is outside this ticket's Technical scope (no `save_dispatch_task`) and is left as-is — call out only, do not expand scope here.
- Operator Admin upsert / table_copy / raw SQL paths still can write `dispatch_task` by design (operator).
- Tests or docs that assume provision-on-start creates meteorite/`fetch_email` rows will fail or lie until Betty/qa-fix adjusts them — product fix does not touch `tests/`.
- Context-only history AST-741/AST-745/AST-1108 is not reopened; this is a ban delta on the remaining writers only.

### What must still hold

- Schema ensure still creates/migrates `dispatch_task` DDL so the app boots on empty or older DBs.
- Manage Dispatch create/edit (`save_dispatch_task` / `update_dispatch_task` via admin API) still works.
- Dispatcher runtime bookkeeping (`last_run_at`, max_runs → disable) still works.
- No redesign of Manage Dispatch UI.
- Curated schedule rows are byte-stable across restart for content fields (aside from the bookkeeping above).
- Needed new-row SQL is delivered only as Linear comment text for Susan — not as an auto-run script.

## Radia review (AST-1496)

Clean review on `8256593d` — ban auto-writers OK. Discuss items (archie-catalog-wins carve-out, hold-bullet vs retire-delete) owned by sibling gap AST-1501 / wording follow-ups. **docs-acceptance:** component test delivery for this ban lives on sibling gap AST-1500 (Betty qa-fix), not this product sub.

## Resolution: AST-1500 — gap dispatcher provision tests

**2026-08-26 (resolve-child):** Radia fix-now on `3a176fe0` — removed AST-1493 test/bible stack (`be1dc566`: meteorite stem/config coverage) from publish ref; retained AST-1500 ban delta (`999cf2d1` + `merge-tests`) and ftr merge for AST-1496 product ban. Bug-repro manifest green; §9a dev/ftr dry-run clean.

## Bug: AST-1500 — gap revise dispatcher provision tests

### As-is
Provision-on-start asserts and ensure content migrations expect automatic dispatch_task writers; no ban coverage for restart no-write / script hard-fail.

### To-be
Bible + component tests match the AST-1496 ban (Betty qa-fix [bug-repro]).

### Notes
Radia fix-now addressed: AST-1493 stack file content reverted on tip (`resolve` cb803834).

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Hedy | engineer | `/home/susan/.cursor/chats/0d2c08e5d1935d9efdab86887f440265/39fa4286-03b0-4a21-9850-81366ca09ad5/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/f08258b4-6c23-4682-88f1-097e2e20f6cf/store.db` |
| Radia | review | `/home/susan/.cursor/chats/0d2c08e5d1935d9efdab86887f440265/683c3b5c-e811-4b01-aa01-3f6a4a055902/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1456 (parent) | ftr/AST-1456-do-not-overwrite-dispatch-task |
| AST-1496 | sub/AST-1456/AST-1496-fix-ban-dispatch-task-auto-writers |
| AST-1500 | sub/AST-1456/AST-1500-gap-dispatcher-provision-tests |
| AST-1501 | sub/AST-1456/AST-1501-gap-seed-statute-carveout |

**Epic worktree:** `astral-AST-1456/` — one active sub checked out at a time.
