# AST-2161 — Lone render_verdict no-row retry routing tests + bible (test gap for AST-2159)

<!-- linear-archive: AST-2161 archived 2026-10-16 -->

## Linear archive (AST-2161)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2161/lone-render-verdict-no-row-retry-routing-tests-bible-test-gap-for-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-2158 — [✅/Somerset] meteorite_grade_get COMPLETED: 1 error(s) / 4 processed | meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839  
**Blocked by / blocks / related:** parent: AST-2158

### Description

## What this implements

Test-tree and bible coverage for [AST-2159](https://linear.app/astralcareermatch/issue/AST-2159): the lone-job `render_verdict` path with no bindable row and no matching `decode_failure` goes through the retry fail-destination router instead of a hard `_fail`. Routed here from Betty's fix-board `[board-betty] TESTS: REVISE` on AST-2159 (same shape as AST-2095 for AST-2093). No product source change.

## Scope

## Component scope

* `tests/component/core/test_consult.py` (modified). Add `[bug-repro]` coverage in `TestRenderVerdict` for a stateful lone job whose reply has no bindable row and no `decode_failures` entry. A job in `METEORITE_PASSED_DO` moves to its retry holding with reason `omitted from response`. A job already in the retry holding moves to `ERROR_METEORITE_GRADE_GET`. Existing stateless `test_fails_when_job_row_is_missing` / `test_fails_when_grades_are_missing` stay green as written.
* `docs/test-bible/core/consult.md` (modified). New `AST-2159` block in `TestRenderVerdict` matching the tests.

## Technical scope

* `tests/component/core/test_consult.py`: new test function(s) for the stateful no-row lone retry routing (primary → retry holding, retry holding → error state).
* `docs/test-bible/core/consult.md`: new manifest rows so the bible matches the tests.

## Acceptance criteria

* The repro tests pass on the AST-2159 tip and would have failed before it (the stateful lone no-row job lands in `ERROR_METEORITE_GRADE_GET` on the first miss).
* `consult.py` stays at its locked branch coverage.
* Existing `TestRenderVerdict` nodes stay green as written.
* Bible blocks match the tests.

## Boundaries

* No `src/` or `data/` change. AST-2159 owns the product fix.
* Pre-existing reds on `ftr` are out of scope.

## Notes for planning

Betty's verdict comment on AST-2159 (`[board-betty] TESTS: REVISE`) names the exact gap. Doc to patch: `docs/features/agent/response-validation-layers.md`, with a `## Bug: <this id>` block next to AST-2159's. Blocked by AST-2159 so the tests run against the fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2158-lone-grade-unknown-index-retry`; this child `sub/AST-2158/AST-2161-lone-grade-unknown-index-retry-tests`. Registry is authoritative.

### Comments

#### radia — 2026-10-12T20:09:26.116Z
[code-rubric] PROCEED (Commit: 1e9344f9) Bug-repro pins AST-2159 routing

#### betty — 2026-10-12T20:06:47.477Z
[bug-repro]
`origin/sub/AST-2158/AST-2161-lone-grade-unknown-index-retry-tests` @ `37334f21b` · red pre-fix, green on tip

context_tokens≈95000

#### joan — 2026-10-12T20:04:36.621Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T20:04:27.702Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/consult.md (no AST-2159 block yet) — missing coverage — test-only ticket: qa-fix must land the 3 TestRenderVerdict nodes (2x [bug-repro]: primary→METEORITE_PASSED_DO_RETRY, retry→ERROR_METEORITE_GRADE_GET, reason+_log_fail_dest asserted; other-id decode_failure → omitted) + bible block after § AST-2093. Plan claims verified on tip; kept tests stay green. make-fix has nothing to do.

context_tokens≈52000

#### hedy — 2026-10-12T20:03:48.017Z
`origin/sub/AST-2158/AST-2161-lone-grade-unknown-index-retry-tests` @ `15fbfcf38` · three render_verdict tests planned

---

_Implementation detail may live in git history on `origin/dev`._
