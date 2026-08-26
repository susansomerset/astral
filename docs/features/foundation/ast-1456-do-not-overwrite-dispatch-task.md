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
