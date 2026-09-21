# AST-1497 — Shut off automatic table content updates on deploy (updates to candidate are happening when we deploy)

<!-- linear-archive: AST-1497 archived 2026-09-09 -->

## Linear archive (AST-1497)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1497/shut-off-automatic-table-content-updates-on-deploy-updates-to  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1492 — updates to candidate are happening when we deploy  
**Blocked by / blocks / related:** parent: AST-1492

### Description

## What this implements

Kill-switch: shut off automatic **table content** updates on deploy/boot so operator-managed rows (including `somerset` candidate state) survive restart. Inventory then disable ensure-time content writers / repo-JSON apply / blank sync inserts; schema DDL may remain if still approved. Does **not** design future seed/ops.

## Citations

`astral.seed.operator-rows-stay-deleted`; `astral.seed.define-approved`; bootstrap ensure contract from AST-842/AST-843 (schema only — do not replace data).

## Scope

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

## Proposed change (make-fix)

- [X] `bootstrap_runtime`: keep validation → schema ensure → `start_scheduler`; remove repo-JSON apply and `sync_agent_tasks` boot calls
- [X] `apply_repo_admin_json_at_startup`: unconditional no-op (boot apply disabled); export/loaders intact
- [X] `_ensure_candidate_schema`: DDL-only — no candidate_data/library migrates or legacy state remap on ensure
- [X] Registry ensure handlers: DDL-only (agent / agent_task / job / dispatch_task / company_search_terms / agent_data content blocks stripped)
- [X] `sync_agent_tasks`: no boot caller (function left for explicit/script use)
- [X] `config.py`: no change (no new boot content flag)

## Acceptance criteria

- [X] After a staging deploy/restart, `somerset.state` (and other live candidates) remain at their pre-deploy values — not forced to `NEW_CANDIDATE`.
- [X] Boot path does not automatically INSERT/UPDATE operator table **content** (candidate remaps, candidate_data migrates, repo JSON apply, blank `agent_task` sync inserts) unless an explicit remaining exception is documented in the plan.
- [X] Schema ensure may still create missing tables/columns if the plan keeps that exception; content mutates on boot are off.
- [X] Future seed/ops redesign is out of scope for this child.

## Boundaries

* Does not invent a new seed management system.
* Does not resurrect archived ancestor AST-842 as a live parent.
* Does not change runtime business writes from dispatch/consult/admin saves.

## Notes for planning

Orphaned mini-parent AST-1492. Approved ancestor checklist: AST-842 (archived — feature doc only). Feature doc context: `docs/features/foundation/ast-842-database-updates-are-not-running-on-production-deployments.md` (+ sibling `ast-843-bootstrap-schema-ensure-at-server-startup.md`).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1492-updates-to-candidate-are-happening-when-we-deploy`, child `sub/AST-1492/<child-segment>`. Created at bug-fix.

### Comments

#### radia — 2026-08-26T16:26:50.235Z
[code-rubric] REVIEW (Commit: 10f28324) kill-switch clean; canon/tests discuss

#### betty — 2026-08-26T16:10:39.671Z
Tests updated for [qa-handoff]
`origin/sub/AST-1492/AST-1502-cover-bootstrap-kill-switch-test-hole` @ `ad35e94dbb60527c9891c75e1b88d9d67280f65a` · bootstrap order monkeypatch fixed; green vs 10f28324

#### hedy — 2026-08-26T16:07:39.675Z
[qa-handoff]
@Betty White

**Product tip:** `origin/sub/AST-1492/AST-1497-shut-off-automatic-table-content-updates-on-deploy` @ `10f28324`

**[bug-repro] flip:** green on fixed product; red on pre-fix `f31c9c7b` (content_calls non-empty). Command:

```bash
./scripts/testing/run_component_tests.sh \
  'tests/component/data/database/test_candidates.py::TestAst1502EnsureLeavesLiveCandidateContent::test_ensure_candidate_schema_leaves_artifacts_ready_without_content_migrates' \
  -q --no-cov
```

**Manifest failure (test defect, not product):** `TestBootstrapRuntime.test_runs_validation_schema_ensure_and_scheduler_in_order` on AST-1502 tip raises:

`AttributeError: ... bootstrap ... has no attribute 'apply_repo_admin_json_at_startup'`

AST-1497 make-fix removed the unused import/call of `apply_repo_admin_json_at_startup` and `sync_agent_tasks` from `bootstrap.py` per plan ("drop unused imports"). The AST-1502 test still `monkeypatch.setattr(bootstrap_mod, "apply_repo_admin_json_at_startup", ...)` (and sync) on the bootstrap module. Those names are intentionally absent.

**Please revise** the bootstrap order test to assert kill-switch order (`validate` → `schema_ensure` → `scheduler`) without requiring those symbols to remain imported on `src.core.bootstrap` — e.g. drop the setattr for removed names, or patch only what `bootstrap_runtime` still references. Stay on AST-1502; reassign Hedy when green against `10f28324`.

`TestApplyRepoAdminJsonAtStartup` (noop all envs) passed against the product tip.

#### joan — 2026-08-26T15:55:35.217Z
[board-joan]  CANON: REVISE
What: astral.seed.agent-tables-in-repo-json — boot repo-wins apply disabled — record kill-switch carve-out until explicit ops/seed design

#### betty — 2026-08-26T15:53:44.796Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/bootstrap.md (+ repo_admin_json.md) — broken TestBootstrapRuntime order (expects repo_json+sync) and TestApplyRepoAdminJsonAtStartup (expects non-local apply); missing coverage that ensure/boot leaves live candidate state (ARTIFACTS_READY) alone — the repro

#### hedy — 2026-08-26T15:41:30.383Z
`origin/sub/AST-1492/AST-1497-shut-off-automatic-table-content-updates-on-deploy` @ `b46d66df` · boot content kill-switch

---

_Implementation detail may live in git history on `origin/dev`._
