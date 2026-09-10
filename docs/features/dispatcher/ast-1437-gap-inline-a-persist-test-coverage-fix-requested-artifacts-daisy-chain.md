# AST-1437 — Gap: inline A== persist test coverage (Fix REQUESTED_ARTIFACTS daisy chain)

<!-- linear-archive: AST-1437 archived 2026-09-09 -->

## Linear archive (AST-1437)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1437/gap-inline-a-persist-test-coverage-fix-requested-artifacts-daisy-chain  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1426 — craft_jobdesc_rubric fails in the REQUESTED_ARTIFACTS chain  
**Blocked by / blocks / related:** parent: AST-1426

### Description

## What this implements

Test-hole gap from AST-1434 fix-board: inline A== persist has no bible/test node; TestAst972CandidateStageConsultRouting is entry-hop-only and will break when consult passes task_key/trigger/skip.

## Citations

none — test coverage gap named by [board-betty] on AST-1434

## Acceptance criteria

* A repro test for pasted one-line `A ==` / `B ==` persist (plan-fix Repro step 1) exists and was red on the pre-fix tree.
* Consult routing tests are not entry-hop-only against the AST-1434 proposed change.

## Boundaries

Does not implement the product fix (AST-1434). Does not revive AST-1109.

## Notes for planning

Betty's board What line is the entire brief. qa-fix lands [bug-repro] here.

## Git branch (authoritative)

parent `ftr/AST-1426-craft-jobdesc-rubric-requested-artifacts`, child `sub/AST-1426/<this-id>-gap-inline-aeq-persist-coverage`.

## QA test manifest

1. Inline A== persist (bug-repro): `tests/component/utils/test_rubric_text.py::TestAst1437InlineGradePersist::test_inline_aeq_one_physical_line_parses_and_rewrites`
2. Mid-hop consult routing (bug-repro): `tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting::test_mid_hop_with_run_next_routes_to_daisy_chain_worker`
3. Entry-hop worker kwargs (revised, not repro): `tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting::test_routes_requested_artifacts_via_stage_task_key`

Pre-fix: 1 raises ValueError "at least two lines"; 2 returns zeros with `unhandled candidate task_key=craft_joblist_rubric`. Flip green after AST-1434 `make-fix`.

**AST-1437** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_rubric_text.py::TestAst1437InlineGradePersist \
  tests/component/core/test_consult.py::TestAst972CandidateStageConsultRouting \
  -q
```

Bible shasums (`origin/sub/AST-1426/AST-1437-gap-inline-aeq-persist-coverage`):

* `docs/test-bible/utils/rubric_text.md` `a122c970313b0223ef0d9ba6ab5b50177066fca7`
* `docs/test-bible/core/candidate.md` `7a4590e7ea3c7dc4a6403d7aab553711ae206061`

### Comments

#### betty — 2026-08-19T00:45:53.733Z
[bug-repro]
`origin/sub/AST-1426/AST-1437-gap-inline-aeq-persist-coverage` @ `09f8acfd6be0e8ec30e15a82923ec5de4ef9cd59` · repro lands red, awaits fix

#### chuckles — 2026-08-19T00:40:29.696Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/rubric_text.md — missing coverage — pasted one-line A== B== persist (repro step 1) has no node; TestAst972CandidateStageConsultRouting is entry-hop-only and will break when consult passes task_key/trigger/skip

Relocated from sibling AST-1434 fix-board. This gap child is the test-hole vehicle (orphaned mini-parent AST-1426). Land the named coverage on this ticket via qa-fix; do not fold it into AST-1434's product commits.

---

_Implementation detail may live in git history on `origin/dev`._
