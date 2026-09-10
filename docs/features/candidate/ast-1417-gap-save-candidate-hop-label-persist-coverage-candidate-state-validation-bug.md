# AST-1417 — Gap: save_candidate hop-label persist coverage (Candidate state validation bug)

<!-- linear-archive: AST-1417 archived 2026-09-09 -->

## Linear archive (AST-1417)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1417/gap-save-candidate-hop-label-persist-coverage-candidate-state  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1415 — Candidate state validation bug  
**Blocked by / blocks / related:** parent: AST-1415

### Description

## What this implements

Test-gap sibling of AST-1416 (orphaned-bug fix-board TESTS: REVISE — not run inline on the fix child). Land repro coverage for `save_candidate` persist of `REQUESTED_ARTIFACTS.<hop>` so the hop-label membership carve-out cannot regress without a red test.

## As-is

`docs/test-bible/data/database/candidates.md` / `TestSaveCandidate` only rejects `NOT_A_STATE`. AST-1389 mocks the hop-label write. `save_candidate` persist of a real `REQUESTED_ARTIFACTS.<hop>` compound label is uncovered — that is the membership error AST-1416 fixes.

## To-be

At least one test fails against the pre-fix tree when `save_candidate` is asked to persist `REQUESTED_ARTIFACTS.craft_get_rubric` (or equivalent hop label) and passes once AST-1416's carve-out lands. Bible entry names that coverage.

## Board brief (from AST-1416)

```
[board-betty] TESTS: REVISE
What: docs/test-bible/data/database/candidates.md — missing coverage — save_candidate persist of REQUESTED_ARTIFACTS.<hop> (AST-1389 mocks the write; TestSaveCandidate only rejects NOT_A_STATE)
```

## Citations

AST-1416 plan-fix patch on `docs/features/candidate/ast-1252-artifacts-dispatch-chain-persistence-and-retire-wrappers.md`. Betty board REVISE on AST-1416.

## Boundaries

Does not implement the product carve-out (AST-1416). Does not expand into a bible sweep.

## Git branch (authoritative)

parent `ftr/AST-1415-candidate-state-validation-bug`, child `sub/AST-1415/<this-id>-save-candidate-hop-label-coverage`.

## QA test manifest

1. Hop-label persist (bug-repro): `tests/component/data/database/test_candidates.py::TestAst1417SaveCandidateHopLabelPersist::test_update_persists_requested_artifacts_hop_label`

Bible: `docs/test-bible/data/database/candidates.md` shasum `7145874cd236dc6256c49e985e9b7fa560dc3494`

Narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1417SaveCandidateHopLabelPersist \
  -q
```

Pass criterion: fails on pre-fix tree (`Invalid candidate state 'REQUESTED_ARTIFACTS.craft_get_rubric'`); flips green after AST-1416 make-fix.

### Comments

#### radia — 2026-08-17T06:08:52.094Z
[code-rubric] REVIEW (Commit: 655fc40f) hop-label bug-repro OK

#### betty — 2026-08-17T05:52:49.054Z
[bug-repro]
`origin/sub/AST-1415/AST-1417-save-candidate-hop-label-coverage` @ `22c76cc3` · repro lands red, awaits fix

#### chuckles — 2026-08-17T05:43:16.400Z
Test-gap sibling of AST-1416. Betty's board on AST-1416:

[board-betty] TESTS: REVISE
What: docs/test-bible/data/database/candidates.md — missing coverage — save_candidate persist of REQUESTED_ARTIFACTS.<hop> (AST-1389 mocks the write; TestSaveCandidate only rejects NOT_A_STATE)

qa-fix runs here (orphaned-bug REVISE is not inline on the fix child). Use that brief.

---

_Implementation detail may live in git history on `origin/dev`._
