# AST-1492 — updates to candidate are happening when we deploy

<!-- linear-archive: AST-1492 archived 2026-09-09 -->

## Linear archive (AST-1492)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1492/updates-to-candidate-are-happening-when-we-deploy  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

On staging deploy / server restart, the `somerset` candidate row is rewritten to `NEW_CANDIDATE` even when it had already progressed to `ARTIFACTS_READY` or `ACTIVE_SEARCH`. Broader pattern: deploy/bootstrap still runs automatic table content updates (not just schema DDL), so operator-managed row state does not stay put across deploys.

## To-be

Deploy and process bootstrap do **not** automatically mutate table **content**. Operator-managed rows (candidate state included) survive deploy unchanged. Schema ensure may still create missing tables/columns if that stays the approved exception; content inserts/updates/remaps on boot are off until a later, explicit seed/ops design lands.

## Proposed steps

1. Inventory every automatic writer on the deploy/boot path (`bootstrap_runtime` → repo JSON apply, upsert-registry schema ensures that also run data migrations, `sync_agent_tasks`, plus any provision/ensure still hooked from scheduler start) and list each as keep-DDL / disable-content.
2. Shut content writers off first: no-op or gate the ensure-time data migrates (candidate legacy remap / candidate_data rewrites), startup repo JSON apply for non-local, and blank-row `sync_agent_tasks` inserts — so a restart cannot reset `somerset.state` or re-seed related rows.
3. Confirm with a staging restart that `somerset` (and other live candidates) keep their pre-deploy `state` and that no unexpected INSERT/UPDATE volume hits operator tables.
4. Leave future seed/ops design out of this bug — this pass is kill-switch only.

## Component scope

* `src/core/bootstrap.py` — modified: single orchestrator for deploy/boot side effects; gate or strip content steps while leaving process validation / scheduler start behavior explicit.
* `src/core/repo_admin_json.py` — modified: `apply_repo_admin_json_at_startup` is a boot-time table rewrite for `agent` / `agent_task`; must stop (or stay local-skip only) under the kill-switch.
* `src/data/database.py` — modified: `_ensure_candidate_schema` still runs content migrates (`_legacy_candidate_migrate_conn` phases BC, candidate_data/library migrates) on first ensure; `ensure_all_upsert_registry_schemas_at_startup` / other `_ensure_*_schema` handlers that UPDATE/INSERT rows; `sync_agent_tasks` INSERT of missing `agent_task` rows — all content paths in scope to disable or hard-gate.
* `src/utils/config.py` — modified only if a boot kill-switch / seed-execution flag must live next to `SEED_CONFIG` (SEED_CONFIG itself is not executed today; do not expand it here).

## Technical scope

* `src/core/bootstrap.py` — modified function `bootstrap_runtime`: drop or flag-gate content steps after validation so restart no longer chains repo-json + ensure-with-data + sync inserts as unconditional deploy behavior.
* `src/core/repo_admin_json.py` — modified function `apply_repo_admin_json_at_startup`: stop applying repo JSON row sets on non-local boot (or make apply operator-only), so deploy cannot replace `agent` / `agent_task` content.
* `src/data/database.py` — modified `_ensure_candidate_schema` / `_legacy_candidate_migrate_conn` (and sibling ensure-time candidate migrates): stop remapping or rewriting candidate rows on schema ensure so live states like `ARTIFACTS_READY` / `ACTIVE_SEARCH` cannot be forced toward `NEW_CANDIDATE` (or otherwise rewritten) just because the process restarted.
* `src/data/database.py` — modified `ensure_all_upsert_registry_schemas_at_startup` and/or per-table `_ensure_*_schema` handlers: keep DDL-only if still approved; remove or gate embedded UPDATE/INSERT seed/migration blocks that run on every boot.
* `src/data/database.py` — modified `sync_agent_tasks`: stop automatic INSERT of blank `agent_task` rows on boot.
* `src/utils/config.py` — new or modified config flag only if plan-fix needs an explicit “no content on boot” switch; exact name is plan-fix’s call under statute.

## Ancestor candidates

- [X] AST-842 — Database updates are not running on production deployments (parent epic that introduced deploy/boot schema ensure; Susan: schema only, do not replace data)
- [ ] AST-843 — Bootstrap schema ensure at server startup (child of AST-842; `ensure_all_upsert_registry_schemas_at_startup` on every boot)
- [ ] AST-771 — Seed audit (inventory of automatic startup writers; dispositions for relocate/remove of ensure-time content mutates)
- [ ] AST-1108 — Fix broken seed data (SEED_CONFIG scaffolding + hot-path seed/migration thrash on ensure)
- [ ] AST-782 — Startup repo JSON upsert and export (`apply_repo_admin_json_at_startup` rewrites `agent` / `agent_task` on non-local boot)
- [ ] AST-745 — Stop dispatch retry auto-seed and startup DB inventory (prior “stop automatic table rebuilds on restart” for `dispatch_task`)
- [ ] AST-973 — Legacy candidate migration (ensure-time `_legacy_candidate_migrate_conn` remaps unknown/`NEW` → `NEW_CANDIDATE`)

## Original report

the somerset candidate in staging is set to "NEW_CANDIDATE" when it was previously "ARTIFACTS_READY" or "ACTIVE_SEARCH".

REMOVE ALL AUTOMATIC TABLE UPDATES ON DEPLOY.

Start with shutting it all off.  We will work on how to manage seed data and updates in the future.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
