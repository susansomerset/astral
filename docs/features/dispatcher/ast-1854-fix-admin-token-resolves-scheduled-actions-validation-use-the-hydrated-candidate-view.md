# AST-1854 — fix: admin token resolves (Scheduled Actions validation) use the hydrated candidate view

<!-- linear-archive: AST-1854 archived 2026-10-07 -->

## Linear archive (AST-1854)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1854/fix-admin-token-resolves-scheduled-actions-validation-use-the-hydrated  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1852 — Scheduled Action Validation is flawed  
**Blocked by / blocks / related:** parent: AST-1852

### Description

## What this implements

The admin-side token resolves in `src/ui/api/api_admin.py` see the same candidate view the real run path does. Scheduled Actions validation (the dispatch empty-render / AUTO-Run gate), Task Manager token enrichment, and the ad hoc run all load the candidate through the hydrated `src.core.candidate.get_candidate`, which overlays the operative artifact rows, instead of the raw `database.get_candidate` row. A candidate whose Ideal Day (or any other migrated context artifact) lives only in the artifacts table, like somerset, then validates clean for `craft_do_rubric`. A candidate with a truly empty Ideal Day still fails.

## Scope

## Component scope

* `src/ui/api/api_admin.py` (modified): the dispatch empty-render gate, Task Manager enrichment, and the ad hoc run all read the raw DB candidate row. They need to read the hydrated one.
* `tests/component/ui/api/test_api_admin.py` (modified; Betty's call on the exact file): repro for an artifact-only Ideal Day passing the gate.

## Technical scope

* `src/ui/api/api_admin.py`: modified functions `_evaluate_dispatch_empty_render`, `_enrich_tasks`, and the ad hoc run handler. Switch the candidate load from `database.get_candidate` to the hydrated `src.core.candidate.get_candidate` (import alongside the existing `build_candidate_token_view` import) so artifact-table values overlay `candidate_data` before token resolution. No new function, table, or field.
* Test file: new test function(s) covering artifact-only and truly empty Ideal Day through the gate.

## Boundaries

Product code only. Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). The runtime path in `src/core/agent.py` already hydrates, so leave it alone. Don't change `empty_render_for_prompts` / `resolve_tokens` semantics in `src/utils/config.py`, and don't change the `hydrate_operative_*` helpers in `src/core/candidate.py`. The fix is which loader the three admin call sites use. No new limits, caps, or shortcuts.

## Notes for planning

Parent bug AST-1852's Description (As-is / To-be / Proposed steps) is authoritative. Susan approved the whole read, including step 2 (the two sibling call sites in the same file). No ancestor box was checked, so there's no related-issue link. Feature doc to patch (Chuckles' best read): `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`, which introduced `_evaluate_dispatch_empty_render`. Call sites on dev: `_evaluate_dispatch_empty_render` (raw `database.get_candidate` then `build_candidate_token_view`), `_enrich_tasks`, and the ad hoc run handler (around line 1580).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1852-dispatch-gate-hydrated-candidate`, child `sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate`. Created at bug-fix.

### Comments

#### radia — 2026-09-29T17:48:00.997Z
[code-rubric] PROCEED (Commit: b5a72977) Three hydrated loader swaps clean

#### hedy — 2026-09-29T17:43:08.061Z
`origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate` @ `b5a72977` · lighter check (no qa-fix on this tip; repro is AST-1855).
`pytest tests/component/ui/api/test_api_admin.py` → 173 passed / 5 failed; the same 5 fail identically on origin/dev `3dd7f249` (pre-existing, not AST-1854): TestAst781…zero_available_count, TestDispatchTasks::test_list_dispatch_tasks_and_keys, TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key, TestAst783RepoJsonApi::test_repo_json_revert_invalid_table_key, TestAst1214…mailbox_trigger_null_only_and_unsupported_craft_wording.

#### hedy — 2026-09-29T17:37:20.537Z
`origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate` @ `b5a72977` · py_compile + import OK; no linter installed (venv/system) — ruff/pyflakes not run.

#### joan — 2026-09-29T17:35:24.370Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T17:35:00.070Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md § AST-1780/1792/1795 — missing coverage — every existing empty-render test either monkeypatches `_evaluate_dispatch_empty_render` or stubs raw `database.get_candidate` + `build_candidate_token_view`, so nothing asserts the hydrated view; need a [bug-repro] per plan § Repro (c1 artifact-only Ideal Day → `empty_render: False`, red pre-fix), plus contrasts c2 (no artifact, no blob → True + `IDEAL_DAY`) and c3 (legacy blob only → False). `_enrich_tasks` / `_resolve_adhoc` swaps are covered by the same loader change; one `_evaluate_dispatch_empty_render` repro is the gate. Blast radius: existing `admin_mod.database.get_candidate` stubs still bite (the hydrated loader calls it on the same module object); the hydrate misses fall through to `get_current_artifact` on the test DB, so qa-fix should confirm those 11 stubs stay green, but I'm not naming any of them as broken.

#### hedy — 2026-09-29T17:33:31.368Z
`origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate` @ `e7c7c96a` · three loader swaps planned

---

_Implementation detail may live in git history on `origin/dev`._
