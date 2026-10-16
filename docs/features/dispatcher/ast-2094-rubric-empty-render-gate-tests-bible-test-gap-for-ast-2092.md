# AST-2094 — rubric empty-render gate tests + bible (test gap for AST-2092)

<!-- linear-archive: AST-2094 archived 2026-10-16 -->

## Linear archive (AST-2094)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2094/rubric-empty-render-gate-tests-bible-test-gap-for-ast-2092  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2019 — [✅/Abrams] qualify_job_listings COMPLETED: 10 error(s) / 10 processed | qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e  
**Blocked by / blocks / related:** parent: AST-2019

### Description

## What this implements

Test gap for [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092) (fix-board `[board-betty] TESTS: REVISE`): flip the pinned AST-1779 rubric-seam test to the new default (rubric tokens scored as candidate-scoped) and add a `[bug-repro]` for an empty `RUBRIC_VECTORS` on `qualify_job_listings`, plus a filled-rubric control. Bible entry in `docs/test-bible/utils/config.md`.

## Betty's verdict (verbatim)

\[board-betty\] TESTS: REVISE
What: docs/test-bible/utils/config.md (TestAst1779EmptyRenderForPrompts) — broken test + missing repro — `test_rubric_scored_only_via_entity_contexts` default-call assertion (False) flips to True/\["GET_RUBRIC"\]; no existing test covers rubric-empty with `_astral_candidate_id` + stubbed `rubric_criteria_for_token` → `[]` (needs \[bug-repro\] for RUBRIC_VECTORS on qualify_job_listings + one-criterion AC 3 control). test_api_admin.py empty-render cases all stub prompt texts (no rubric tokens) — unaffected.

## Citations

none — test tree + bible only.

## Scope

### Component scope

* `tests/component/utils/test_config.py` — modified: flip `TestAst1779EmptyRenderForPrompts::test_rubric_scored_only_via_entity_contexts` default-call assertion; new `[bug-repro]` rubric-empty test and a filled-rubric control (red pre-fix, green on the AST-2092 tip).
* `docs/test-bible/utils/config.md` — modified: `TestAst1779EmptyRenderForPrompts` entry updated for rubric-by-default scoring and the new tests.

### Technical scope

* `tests/component/utils/test_config.py`: modified test + new tests in `TestAst1779EmptyRenderForPrompts` — candidate view with `_astral_candidate_id`, stubbed `rubric_criteria_for_token` returning `[]` (empty → `empty_render: True`, `RUBRIC_VECTORS` in `empty_tokens`) and one criterion (→ `empty_render: False`).
* `docs/test-bible/utils/config.md`: modified section — manifest nodes for the flipped and new tests.

## Boundaries

No product `src/` change — the product fix is AST-2092. Test-tree work is Betty's (qa-fix); engineer side is a no-product-src marker plus test-fix verification.

## Git branch (authoritative)

Mini-parent `ftr/AST-2019-rubric-empty-render-gate`, child `sub/AST-2019/AST-2094-rubric-empty-render-gate-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-09T02:55:14.778Z
[code-rubric] PROCEED (Commit: b3d69a18) Rubric gate tests+bible

#### betty — 2026-10-09T02:52:49.652Z
[bug-repro]
`origin/sub/AST-2019/AST-2094-rubric-empty-render-gate-tests` @ `fc69dfc5c` · repro red pre-fix, green on sub

Repro node: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_empty_rubric_vectors_sets_empty_render`. Manifest: `docs/test-bible/utils/config.md` § AST-1779 lines 1–9 (whole class; shasum `050b0723`).

#### betty — 2026-10-09T02:29:08.039Z
@susan qa-fix blocked at publish (merge-tests) — need your call.

- Test landed on `origin/tests` @ `9ead623ca` (`5d0cc5aaa`): flipped/renamed seam test + `[bug-repro]` `test_empty_rubric_vectors_sets_empty_render` + AC 3 control; bible `utils/config.md` § AST-1779. Red on `823d37605` (2 failed, 7 passed — repro + flipped seam, right reason), green on sub+tests (9 passed). Pre-existing red set doesn't grow (my commit only removes the old seam failure).
- Not pushed to `origin/sub/AST-2019/AST-2094-rubric-empty-render-gate-tests`: `merge origin/tests` would also drag in `docs/features/dispatcher/ast-1780-…md` (+140, AST-2091 plan-fix `fb0e1801e`/`be1f4b0c5` that leaked onto `origin/tests`) and 7 unrelated reds (AST-2081 / AST-2088 tests whose product isn't on dev). 28 → 35 in test_config/test_api_admin.
- Also: local `tests` held an unpublished AST-2090 qa-fix pass atop a forbidden sync merge; parked as tag `backup/ast-2090-qa-fix` (`8f51ba95a`), local `tests` reset to `origin/tests`.

Options: (1) merge-tests anyway, (2) cherry-pick `5d0cc5aaa` alone onto the sub, (3) clean AST-2091 doc off `origin/tests` first. Status left Plan Approved.

#### joan — 2026-10-09T02:26:14.683Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:26:01.802Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md (AST-1779 · TestAst1779EmptyRenderForPrompts) — broken test + missing repro — `test_rubric_scored_only_via_entity_contexts` is red on ftr (flip + rename); no `[bug-repro]` for empty RUBRIC_VECTORS on qualify_job_listings and no one-criterion AC 3 control; bible row + manifest line 7 still state the old rule. Plan's stub target is right: `resolve_tokens` imports `src.core.candidate.rubric_criteria_for_token` at call time on the ftr. No test_api_admin.py change.

#### ada — 2026-10-09T02:25:35.413Z
`origin/sub/AST-2019/AST-2094-rubric-empty-render-gate-tests` @ `6401a098` · flip, repro, control planned

---

_Implementation detail may live in git history on `origin/dev`._
