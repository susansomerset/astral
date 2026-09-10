# AST-1502 — Cover bootstrap kill-switch test hole (gap for AST-1497)

<!-- linear-archive: AST-1502 archived 2026-09-09 -->

## Linear archive (AST-1502)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1502/cover-bootstrap-kill-switch-test-hole-gap-for-ast-1497  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1492 — updates to candidate are happening when we deploy  
**Blocked by / blocks / related:** parent: AST-1492

### Description

## What this implements

Land the test hole fix-board named on AST-1497: update/break-and-fix `docs/test-bible/core/bootstrap.md` (+ `repo_admin_json.md`) coverage that still expects boot repo-JSON apply + `sync_agent_tasks`, and add repro coverage that ensure/boot leaves a live candidate state (`ARTIFACTS_READY`) alone.

## Citations

Sibling AST-1497 plan-fix patch in `docs/features/foundation/ast-842-database-updates-are-not-running-on-production-deployments.md`. `[board-betty] TESTS: REVISE` on AST-1497.

## Scope

## Component scope

* `docs/test-bible/core/bootstrap.md` — modified: bible rows for bootstrap_runtime order after kill-switch.
* `docs/test-bible/core/repo_admin_json.md` (or adjacent bible path Betty named) — modified: startup apply expectations under kill-switch.
* `tests/component/core/test_bootstrap.py` / related component tests — modified or new: assert boot leaves live candidate state alone; update stale order assertions.

## Technical scope

* Bible + component tests: revise `TestBootstrapRuntime` / `TestApplyRepoAdminJsonAtStartup` expectations; add coverage that ensure/boot does not rewrite a candidate already in `ARTIFACTS_READY` (or equivalent live state).

## Acceptance criteria

1. Bootstrap/repo-admin-json tests match kill-switch (no expected boot content apply / sync insert).
2. A repro test fails pre-fix / passes post-fix showing live candidate state survives ensure/boot.

## Boundaries

Does not implement the product kill-switch (AST-1497 / make-fix). Orphaned-bug fix-board REVISE → sibling gap (`fix-intake` § bug-fix).

## Notes for planning

Board What: docs/test-bible/core/bootstrap.md (+ repo_admin_json.md) — broken TestBootstrapRuntime order (expects repo_json+sync) and TestApplyRepoAdminJsonAtStartup (expects non-local apply); missing coverage that ensure/boot leaves live candidate state (ARTIFACTS_READY) alone — the repro.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1492-updates-to-candidate-are-happening-when-we-deploy`, child `sub/AST-1492/<child-segment>`.

## QA test manifest

**[bug-repro] **`tests/component/data/database/test_candidates.py::TestAst1502EnsureLeavesLiveCandidateContent::test_ensure_candidate_schema_leaves_artifacts_ready_without_content_migrates`

Also:

* `tests/component/core/test_bootstrap.py::TestBootstrapRuntime::test_runs_validation_schema_ensure_and_scheduler_in_order` — patches only validate / schema_ensure / scheduler (no setattr on removed boot imports; [qa-handoff] revise)
* `tests/component/core/test_repo_admin_json.py::TestApplyRepoAdminJsonAtStartup`

Narrowed run: see `docs/test-bible/core/bootstrap.md` § AST-1502.

Tip @ `origin/sub/AST-1492/AST-1502-cover-bootstrap-kill-switch-test-hole` `ad35e94dbb60527c9891c75e1b88d9d67280f65a` (return-pass cherry-pick after merge-tests).

* `docs/test-bible/core/bootstrap.md` `0885c7299b36ac64e056eb5235b39d7bbcf39d14`

Confirmed green against AST-1497 product tip `10f28324`.

### Comments

#### radia — 2026-08-26T16:26:55.231Z
[code-rubric] REVIEW (Commit: ad35e94d) in-scope tests clean; merge-tests discuss

#### betty — 2026-08-26T16:10:43.358Z
`origin/sub/AST-1492/AST-1502-cover-bootstrap-kill-switch-test-hole` @ `ad35e94dbb60527c9891c75e1b88d9d67280f65a` · handoff bootstrap patch fixed

#### betty — 2026-08-26T16:02:43.922Z
[bug-repro]
`origin/sub/AST-1492/AST-1502-cover-bootstrap-kill-switch-test-hole` @ `e4ce134862ff0b24726b67f1cf5585b74e68bdd1` · repro lands red, awaits fix

#### betty — 2026-08-26T15:56:46.043Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/bootstrap.md (+ repo_admin_json.md) — broken TestBootstrapRuntime order (expects repo_json+sync) and TestApplyRepoAdminJsonAtStartup (expects non-local apply); missing coverage that ensure/boot leaves live candidate state (ARTIFACTS_READY) alone — the repro
Copied from sibling AST-1497 board; this gap child is the test-hole slice.

---

_Implementation detail may live in git history on `origin/dev`._
