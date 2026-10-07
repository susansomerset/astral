# AST-1855 — gap: artifact-only Ideal Day repro for the dispatch empty-render gate (AST-1854 board)

<!-- linear-archive: AST-1855 archived 2026-10-07 -->

## Linear archive (AST-1855)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1855/gap-artifact-only-ideal-day-repro-for-the-dispatch-empty-render-gate  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1852 — Scheduled Action Validation is flawed  
**Blocked by / blocks / related:** parent: AST-1852

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1854. No existing test checks the bug: every empty-render test either replaces `_evaluate_dispatch_empty_render` with a stub or stubs the raw `database.get_candidate` plus `build_candidate_token_view`, so none of them exercises the candidate view with artifact rows overlaid. Add a `[bug-repro]` that runs `_evaluate_dispatch_empty_render` for a prompt containing `{$IDEAL_DAY}` against three candidates: `c1` has Ideal Day only in the artifacts table and gives `empty_render: False` (must be red on the pre-fix product and green once AST-1854 lands); `c2` has neither an artifact nor a legacy `context.ideal_day` and still gives `empty_render: True` with `IDEAL_DAY` listed; `c3` has only the legacy `context.ideal_day` and gives `empty_render: False`. Confirm the 11 existing tests that stub `admin_mod.database.get_candidate` stay green now that the hydrated loader also reads the artifacts table.

## Scope

### Component scope

* `tests/component/ui/api/test_api_admin.py` (modified): the three-candidate `[bug-repro]` for the dispatch empty-render gate through the hydrated loader. Any extra artifact stub the existing 11 `database.get_candidate` stubs need to stay green.
* `docs/test-bible/ui/api/api_admin.md` (modified): bible entry for the new coverage.

### Technical scope

* Admin API tests: new test function(s). The repro must fail against the pre-fix product (origin/ftr base = origin/dev at fork) and pass after AST-1854. Existing cases change only if the hydrated loader's artifact reads need a stub.
* Test bible: modified entry naming the coverage.

## Boundaries

Test and bible only; product code stays on AST-1854. Betty lands the tests (engineers are banned from the test tree). No limits or caps.

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE on AST-1854 (see that comment). Plan doc: docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md (AST-1854's plan-fix patch, § Bug: AST-1854).

## Git branch (authoritative)

Parent `ftr/AST-1852-dispatch-gate-hydrated-candidate`, child `sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate-tests`.

### Comments

#### radia — 2026-09-29T17:52:30.827Z
[code-rubric] PROCEED (Commit: 4bbeabff) Bug-repro pins hydrated gate

#### hedy — 2026-09-29T17:50:33.068Z
`origin/sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate-tests` @ `4bbeabff` · ftr (AST-1854 fix) synced; plan-doc conflict kept both, AST-1854 sections first.
Manifest 10/10 green. [bug-repro] `TestAst1854HydratedCandidateEmptyRender::test_evaluate_artifact_only_ideal_day_empty_render_false` red with pre-fix `api_admin.py` (3dd7f249), green on tip. Full module 195 passed / 5 failed — same 5 pre-existing on origin/dev.
Attribution note: `merge-tests(AST-1855)` also carries `TestAst1830SweepHrsAdminApi` (AST-1830, other epic; all green) — not AST-1855 scope.

#### betty — 2026-09-29T17:46:06.419Z
[bug-repro]
`origin/sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate-tests` @ `6c083f3c` · red at 3dd7f249, green with b5a72977

#### joan — 2026-09-29T17:42:07.959Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T17:41:51.010Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md (no § AST-1855 yet) — missing coverage — planned `TestAst1854HydratedCandidateEmptyRender` (c1 [bug-repro] / c2 / c3) + bible section not landed; REVISE routes it to qa-fix (the AST-1846 gap-child precedent), not make-fix. The design itself is sound: stubbing only at the DB edges keeps the hydrated loader → `hydrate_operative_*` → token view → `empty_render_for_prompts` chain real, the must-not-stub list is right, and c1 goes red pre-fix because the raw row never calls `get_current_artifact`.
Stub call (plan step 3): stub all seven, not only where red. Add `get_current_artifact → None` to the four existing tests that stub a returned row (~243, ~1481, ~1496, plus `_stub_no_agent_task_prompts`, which covers the four `TestAst1791…` tests). Unstubbed, `database.get_current_artifact` runs `_ensure_artifact_table` DDL plus nine reads per load against the repo `data/astral.db` (default `ASTRAL_DB_DIR`). Green there only proves one machine's DB state (a synced local DB, a lock retry), so "only where red" is environment-dependent. Include all seven in the manifest re-run guard as planned.

#### hedy — 2026-09-29T17:40:39.550Z
`origin/sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate-tests` @ `6cb04ebd` · three-candidate bug-repro planned

---

_Implementation detail may live in git history on `origin/dev`._
