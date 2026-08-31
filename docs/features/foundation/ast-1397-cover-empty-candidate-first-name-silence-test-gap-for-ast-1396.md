# AST-1397 — Cover empty-candidate FIRST_NAME silence (test gap for AST-1396)

<!-- linear-archive: AST-1397 archived 2026-08-31 -->

## Linear archive (AST-1397)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1397/cover-empty-candidate-first-name-silence-test-gap-for-ast-1396  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1395 — loading ad hoc agent screen spills log warnings to the console  
**Blocked by / blocks / related:** parent: AST-1395

### Description

## What this implements

Land the test hole `fix-board` named on AST-1396: `docs/test-bible/utils/config.md` / `TestResolveTokens` has no FIRST_NAME-only empty-`cd` silence assert (`mixed any()` still passes). Add coverage that `resolve_tokens("{$FIRST_NAME}", {}, …)` does **not** emit the candidate-source empty-token WARNING, while a truthy candidate token view with blank `first` still does.

## Citations

Sibling AST-1396 `## Bug: AST-1396` plan-fix patch in `docs/features/artifacts/ast-513-token-gap-correction.md`. `[board-betty] TESTS: REVISE` on AST-1396.

## Acceptance criteria

1. A FIRST_NAME-only empty-`cd` (`{}`) resolve does not log `Token {$FIRST_NAME} resolved to empty`.
2. A candidate token view with `first=""` / `full=""` still logs that WARNING.
3. Bible `docs/test-bible/utils/config.md` records the node.

## Boundaries

Does not implement the product gate (AST-1396 / `make-fix`). Does not change job/chain empty-token warning tests except as needed to keep them honest.

## Notes for planning

Orphaned-bug `fix-board` REVISE → sibling gap child (`fix-intake` § bug-fix). Betty owns this slice. Board What: `docs/test-bible/utils/config.md — missing coverage — TestResolveTokens has no FIRST_NAME-only empty-cd silence assert (mixed any() still passes)`.

## QA test manifest

1. `[bug-repro]` empty-cd FIRST_NAME silence: `tests/component/utils/test_config.py::TestResolveTokens::test_empty_candidate_data_does_not_warn_on_first_name` — red on pre-fix (`Token {$FIRST_NAME} resolved to empty`); awaits AST-1396 gate.
2. Keep-hold truthy blank first: `tests/component/utils/test_config.py::TestResolveTokens::test_blank_first_name_on_truthy_view_still_warns`
3. Mixed any() still honest: `tests/component/utils/test_config.py::TestResolveTokens::test_logs_and_returns_empty_for_missing_candidate_and_chain_values`
4. Bible: `docs/test-bible/utils/config.md` shasum `17a301b55d427ed6219d2452ec54ca6ca2d4d63d`

### Comments

#### betty — 2026-08-16T02:46:44.856Z
[bug-repro]
`origin/sub/AST-1395/AST-1397-cover-empty-candidate-first-name-silence` @ `5f4d8309` · repro lands red, awaits fix

#### chuckles — 2026-08-16T02:34:50.583Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md — missing coverage — TestResolveTokens has no FIRST_NAME-only empty-cd silence assert (mixed any() still passes)
Copied from sibling AST-1396 board; this gap child is the test-hole slice.

---

_Implementation detail may live in git history on `origin/dev`._
