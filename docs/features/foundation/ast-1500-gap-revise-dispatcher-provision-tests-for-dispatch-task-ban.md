# AST-1500 — gap: revise dispatcher provision tests for dispatch_task ban

<!-- linear-archive: AST-1500 archived 2026-09-09 -->

## Linear archive (AST-1500)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1500/gap-revise-dispatcher-provision-tests-for-dispatch-task-ban  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1456 — DO NOT OVERWRITE DISPATCH_TASK IN ANY ENVIRONMENT EVER  
**Blocked by / blocks / related:** parent: AST-1456

### Description

## What this implements

gap (tests): Land the test/bible changes Betty named on AST-1496 fix-board — revise broken provision-on-start asserts and add ban coverage for no-write restart / script hard-fail.

## As-is

Existing TestAst1054/TestAst1088 start_scheduler provision asserts (and TestAst703 ensure content migrations) expect automatic dispatch_task writers; no coverage that restart leaves curated rows byte-stable or that push/upsert scripts hard-fail on dispatch_task.

## To-be

Bible + component tests match the ban: provision-on-start asserts removed/rewritten; restart no-write and script hard-fail coverage exist.

## Scope

## Component scope

* `docs/test-bible/core/dispatcher.md` — modified: revise provision-on-start / ensure content rows for the ban.
* `tests/component/core/test_dispatcher.py` — modified: flip/remove TestAst1054/TestAst1088 provision-on-start asserts; add ban coverage.
* Related ensure tests (e.g. TestAst703) — modified as named by Betty if they assert ensure content writers on dispatch_task.

## Technical scope

* Bible rows for dispatcher provision/ensure — modified: document no automatic dispatch_task content writers on start.
* TestAst1054 / TestAst1088 (and peers) — modified assertions: no longer expect start_scheduler provision inserts.
* New or extended tests — assert curated dispatch_task rows unchanged across restart simulation; scripts hard-fail when table is dispatch_task.

## Notes for planning

Sibling of AST-1496 (product ban). Betty board: docs/test-bible/core/dispatcher.md — broken TestAst1054/TestAst1088 start_scheduler provision asserts (+ TestAst703 ensure content migrations) — missing ban coverage for no-write restart / script hard-fail.

## QA test manifest

**Publish: **`origin/sub/AST-1456/AST-1500-gap-dispatcher-provision-tests` @ `cb803834` (`merge-tests(AST-1500): origin/tests 999cf2d1`).

**Bible: **`docs/test-bible/core/dispatcher.md` § AST-1500 (shasum `ac027e799f8af2442adf7edc4e4d8bce0013b555`); `docs/test-bible/data/database/dispatch_tasks.md` § AST-1500.

**[bug-repro] nodes (red on pre-fix; green after AST-1496 make-fix):**

1. `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision::test_start_scheduler_does_not_invoke_meteorite_provision`
2. `tests/component/core/test_dispatcher.py::TestAst1134MeteoriteEmailDispatchProvision::test_start_scheduler_does_not_invoke_gaze_provision`
3. `tests/component/scripts/test_ast1500_dispatch_task_script_ban.py::TestAst1500DispatchTaskScriptBan` (all three methods)
4. `tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision::test_schema_leaves_dual_prefilter_rows_unchanged`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision::test_start_scheduler_does_not_invoke_meteorite_provision \
  tests/component/core/test_dispatcher.py::TestAst1134MeteoriteEmailDispatchProvision::test_start_scheduler_does_not_invoke_gaze_provision \
  tests/component/scripts/test_ast1500_dispatch_task_script_ban.py::TestAst1500DispatchTaskScriptBan \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  -q
```

Primary flip gate: start_scheduler does-not-invoke + script hard-fail (DID NOT RAISE SystemExit / assert_not_called today).

## Resolve (2026-08-26)

- [X] Radia fix-now: reverted AST-1493 stack (`be1dc566`); kept AST-1500 ban coverage only
- [X] Bug-repro manifest green
- [X] §9a dev/ftr dry-run clean

### Comments

#### radia — 2026-08-26T16:25:14.701Z
[code-rubric] REVIEW (Commit: 3a176fe0) Drop AST-1493 stack; repro OK

#### betty — 2026-08-26T15:57:59.999Z
[bug-repro]
`origin/sub/AST-1456/AST-1500-gap-dispatcher-provision-tests` @ `42389b26` · repro lands red, awaits fix

---

_Implementation detail may live in git history on `origin/dev`._
