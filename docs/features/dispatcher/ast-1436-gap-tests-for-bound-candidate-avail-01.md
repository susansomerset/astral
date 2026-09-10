# AST-1436 — gap: tests for bound-candidate Avail 0/1

<!-- linear-archive: AST-1436 archived 2026-09-09 -->

## Linear archive (AST-1436)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1436/gap-tests-for-bound-candidate-avail-01  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1425 — dispatch tasks with entity_type = 'candidate' do not filter properly  
**Blocked by / blocks / related:** parent: AST-1425

### Description

## What this implements

Test hole named by [board-betty] TESTS: REVISE on sibling AST-1432: existing `TestAst1258CandidatePoolEligibility::test_pool_count_zero_when_all_matching_rows_locked` asserts pool 2 on a bound row; missing coverage of the two-candidate repro (bound Avail 1; lock bound / other unclaimed → 0).

Land the repro-first test(s) against the pre-fix tree (red), rewrite the invalidated pool-2 assertion, bible note for `docs/test-bible/data/database/dispatch_tasks.md` § AST-1258. Product Avail change stays on AST-1432.

## Citations

(none — test gap from fix-board)

## Acceptance criteria

* At least one test fails on the pre-fix tree for the two-candidate bound Avail repro and will pass once AST-1432's make-fix lands.
* `TestAst1258CandidatePoolEligibility` no longer asserts pool 2 for a single bound row.

## Boundaries

Does not implement the Avail product change (AST-1432). Does not change job/company or gaze_email mailbox tests except as required by the named assertion.

## Notes for planning

Board brief is AST-1432's [board-betty] TESTS: REVISE. Plan-fix patch is on `docs/features/dispatcher/ast-1258-candidate-batch-lock-schema-and-pool-claim-apis.md`.

### Comments

#### radia — 2026-08-19T01:03:29.491Z
[code-rubric] REVIEW (Commit: de96f741) owned OK; restacked on ftr without sibling tests-branch collateral

#### betty — 2026-08-19T00:47:43.689Z
[bug-repro]
`origin/sub/AST-1425/AST-1436-gap-tests-bound-candidate-avail` @ `0e5dd4b4` · repro lands red, awaits fix

---

_Implementation detail may live in git history on `origin/dev`._
