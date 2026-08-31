# AST-1385 — gap: tests for craft_* vector_feedback exclusion

<!-- linear-archive: AST-1385 archived 2026-08-31 -->

## Linear archive (AST-1385)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1385/gap-tests-for-craft-vector-feedback-exclusion  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1378 — feedback rubric returned on a craft prompt  
**Blocked by / blocks / related:** parent: AST-1378

### Description

## What this implements

Test/bible gap sibling for AST-1384: cover `is_vector_feedback_task` / craft exclusion so craft_* is not taught or captured under the old `is_rubric_backed_task` vector-feedback path. Filed from [board-betty] TESTS: REVISE on AST-1384 (orphaned mini-parent AST-1378 — gap child instead of inline qa-fix).

## Citations

Betty board: docs/test-bible/utils/config.md § AST-724 — missing coverage — no is_vector_feedback_task / craft exclusion.

## Acceptance criteria

- [X] Bible + component tests assert craft_* keys are excluded from vector-feedback teach/capture (`is_vector_feedback_task` or equivalent), while grade/evaluate consumers remain included.
- [X] Repro shape from AST-1378 (craft returning TRRACAVK-style reviews) is gated by a failing-then-passing test once AST-1384 lands.

## Proposed change (make-fix)

- [X] Betty landed bible § AST-724 gate prose + table + narrowed run (`docs/test-bible/utils/config.md`).
- [X] Betty landed `TestAst724RubricBackedTask::test_is_vector_feedback_consumers_only_excludes_craft` (`[bug-repro]`).
- [X] Product `is_vector_feedback_task` + three `do_task` gates already present from AST-1384 — engineer make-fix: no product re-implement, no test-tree edits.

## Boundaries

* Does not re-implement the product fix (AST-1384).
* Does not raise max_tokens.

## Notes for planning

Parent: AST-1378. Sibling fix: AST-1384. Plan doc: docs/features/auditor/ast-724-runtime-vector-feedback-capture.md ## Bug: AST-1385.

## Git branch (authoritative)

parent ftr/AST-1378-no-feedback-reviews-on-craft; child sub/AST-1378/AST-1385-gap-craft-vector-feedback-tests.

## QA test manifest

* **\[bug-repro\]** `TestAst724RubricBackedTask::test_is_vector_feedback_consumers_only_excludes_craft` — `tests/component/utils/test_config.py`
* Bible: `docs/test-bible/utils/config.md` § AST-724 (gate prose + table row + narrowed run)
* Narrowed run: `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst724RubricBackedTask -q`
* Note: gap sibling — product helper already on ftr via AST-1384; repro green on publish tip (not pre-fix red).

### Comments

#### radia — 2026-08-15T01:12:10.658Z
[code-rubric] PROCEED after restack — gap tests OK on clean ftr tip

Discuss (sibling stack on publish-ref) resolved by Chuckles restack: only plan + test(AST-1385) + merge-tests remain above ftr. → Review Posted → User Testing (§3h).

#### betty — 2026-08-15T01:08:16.257Z
[bug-repro]
`origin/sub/AST-1378/AST-1385-gap-craft-vector-feedback-tests` @ `4e77f401` · craft gate covered, green on AST-1384 tip

#### betty — 2026-08-15T01:05:42.339Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md § AST-724 + test_config.py — missing coverage — is_vector_feedback_task / craft exclusion (Proposed change only; no further beyond it)

#### joan — 2026-08-15T01:05:05.159Z
[board-joan]  CANON: OK

context_tokens≈4200

#### ada — 2026-08-15T01:04:23.648Z
`origin/sub/AST-1378/AST-1385-gap-craft-vector-feedback-tests` @ `13b66b88e689317728797321fa972d272ad2d192` · bible test gap planned

---

_Implementation detail may live in git history on `origin/dev`._
