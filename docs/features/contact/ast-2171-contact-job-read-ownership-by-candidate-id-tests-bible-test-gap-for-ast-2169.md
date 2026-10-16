# AST-2171 — Contact job-read ownership-by-candidate_id tests + bible (test gap for AST-2169)

<!-- linear-archive: AST-2171 archived 2026-10-16 -->

## Linear archive (AST-2171)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2171/contact-job-read-ownership-by-candidate-id-tests-bible-test-gap-for  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2167 — /check-status for an explicit job link failed  
**Blocked by / blocks / related:** parent: AST-2167

### Description

## What this implements

Test-tree and bible coverage for [AST-2169](https://linear.app/astralcareermatch/issue/AST-2169): Estelle's job reads (`/check-status`, `get_job_by_pattern`, `get_job_data`) decide ownership from `job["candidate_id"]` instead of the company owner. Routed here from Betty's fix-board `[board-betty] TESTS: REVISE` on AST-2169. No product source change.

## Scope

## Component scope

* `tests/component/core/test_tracker.py` (modified). The `TestAst1518ContactTaskReads` and `TestAst2151ContactCommandCheckStatus` fixtures (`_job()`, `_stub(owners)`) build rows without `candidate_id` and fake ownership through `get_company`. They get `candidate_id` on the rows, and the cross-candidate cases vary `job["candidate_id"]` instead of the company owner. Add `[bug-repro]` coverage for a meteorite row (`company: None`) whose `candidate_id` is the sender: check-status returns a single match and `get_job_data` returns ok. Its counterpart, a row whose `candidate_id` is another candidate, is still refused.
* `docs/test-bible/core/tracker.md` (modified). The § AST-1518 and § AST-2151 blocks plus a new `AST-2169` block, matching the tests.

## Technical scope

* `tests/component/core/test_tracker.py`: modified fixture helpers and the affected test functions so ownership is driven by `candidate_id`, plus new test function(s) for the null-company repro and the cross-candidate refusal.
* `docs/test-bible/core/tracker.md`: modified and new manifest rows so the bible matches the tests.

## Acceptance criteria

* The repro tests pass on the AST-2169 tip and would have failed before it (a meteorite job with `company: None` is filtered out / not found for its owner).
* The cross-candidate refusal still holds on all three paths.
* Every existing `TestAst1518ContactTaskReads` / `TestAst2151ContactCommandCheckStatus` node is green on the tip.
* The bible blocks match the tests.

## Boundaries

* No `src/` or `data/` change. AST-2169 owns the product fix.
* Pre-existing reds on `ftr` outside these two test classes are out of scope.

## Notes for planning

Betty's verdict comment on AST-2169 (`[board-betty] TESTS: REVISE`) names the exact gap. Doc to patch: `docs/features/contact/ast-2151-check-status-registry-handler.md`, with a `## Bug: <this id>` block next to AST-2169's. This ticket is blocked by AST-2169 so the tests run against the fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2167-check-status-ownership-candidate-id`; this child `sub/AST-2167/AST-2171-check-status-ownership-candidate-id-tests`. Registry is authoritative.

### Comments

#### radia — 2026-10-12T22:41:03.219Z
[code-rubric] PROCEED (Commit: 01a617810) repro + fixtures green

#### betty — 2026-10-12T22:38:24.772Z
[bug-repro]
`origin/sub/AST-2167/AST-2171-check-status-ownership-candidate-id-tests` @ `345f5957a` · repro red pre-fix, green tip

#### joan — 2026-10-12T22:36:29.468Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T22:36:16.125Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md § AST-1518 / § AST-2151 — broken tests + missing repro — this ticket is the test work: 9 red nodes plus 2 false-green nodes (`test_style_d_debug_on_job_data`, `test_ac6[listed_not_owned]`) need fixtures moved to `job["candidate_id"]`, and `_stub` must drop `owners`. Add 2 `[bug-repro]` nodes for the null-company meteorite job (red on `1a9f2a3c6`, green on tip) and a new bible block. The plan-fix spec checks out against the tree (7 + 12 = 19 nodes). I'll take both ⚠️ defaults: the `get_company` raise-guard, and keeping the repros inside the existing classes. qa-fix lands it as written.

#### ada — 2026-10-12T22:35:40.976Z
`origin/sub/AST-2167/AST-2171-check-status-ownership-candidate-id-tests` @ `a2626c52d` · fixtures, repros, bible planned

---

_Implementation detail may live in git history on `origin/dev`._
