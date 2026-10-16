# AST-2060 — Show rubric hydrated-content tests + bible (test gap for AST-2059)

<!-- linear-archive: AST-2060 archived 2026-10-16 -->

## Linear archive (AST-2060)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2060/show-rubric-hydrated-content-tests-bible-test-gap-for-ast-2059  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2058 — the "show rubric" link on the job analysis tab does not open the rubric successfully.  
**Blocked by / blocks / related:** parent: AST-2058

### Description

## What this implements

Test-tree and bible coverage for [AST-2059](https://linear.app/astralcareermatch/issue/AST-2059)'s fix, where the show rubric modal reads content from the hydrated `GET /api/candidates/<id>` detail. Routed here from Betty's fix-board `TESTS: REVISE` on AST-2059 (the same shape as AST-2057 for AST-2053). No product source change.

## Scope

## Component scope

* `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx` (modified). Route the `api` mock by URL (list → array; `/api/candidates/<id>` → `{ ok: true, candidate_data: { artifacts: { <rubric_key>: [...] } } }`) and await modal content in the two tests that will break ("renders grades with rubric links and opens the modal", "matches rubric rows by code and handles missing modal content"). Switch "opens the rubric modal with no matching row" to `findByText`. Add the bug-repro: the list payload has no rubric, the detail payload has `content`, and the modal shows that content. Add coverage that a `!r.ok` or rejected detail fetch ends on the fallback text.
* `tests/component/frontend/components/test_RubricModal.test.tsx` (modified). Add a test that `loading` renders the loading text, and keep the null-content fallback test.
* `docs/test-bible/frontend/components.md` (modified). Update the Analysis/job surfaces row for the hydrated-detail content source, and add a `RubricModal` entry.

## Technical scope

* `test_AgentAnalysisHeader.test.tsx`: two modified test functions, one modified assertion, and new test functions for the repro and the failed-fetch fallback, so the suite asserts the shipped content source instead of the list-payload bug path.
* `test_RubricModal.test.tsx`: new test function for the loading state.
* `docs/test-bible/frontend/components.md`: modified and new bible rows, so the bible matches the tests.

## Acceptance criteria

* The repro test passes on the AST-2059 tip and fails on the pre-fix tree (the modal shows `No rubric found for this vector.`).
* The two named broken tests and the no-matching-row test pass against the shipped fix.
* The loading and failed-fetch tests pass. The bible matches.

## Boundaries

* No `src/` change: AST-2059 owns the product fix.
* The meteorite rubric-key mismatch Ada flagged in plan-fix (Analysis tab requests `jobdesc_rubric` on meteorite jobs) is out of scope.

## Notes for planning

Betty's verdict comment on AST-2059 (`[board-betty] TESTS: REVISE`) names the exact gaps. Doc to patch: `docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md`, with a `## Bug: <this id>` block alongside AST-2059's. Blocked by AST-2059 so the tests run against the shipped fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2058-show-rubric-content`; this child `sub/AST-2058/AST-2060-show-rubric-tests`. Registry is authoritative.

### Comments

#### radia — 2026-10-08T22:01:00.815Z
[code-rubric] PROCEED (Commit: 1537b4b8b) Hydrated-detail rubric tests

#### betty — 2026-10-08T21:57:32.325Z
[bug-repro]
`origin/sub/AST-2058/AST-2060-show-rubric-tests` @ `266b9be9c` · red pre-fix, green ftr tip

#### joan — 2026-10-08T21:54:58.788Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T21:54:46.758Z
[board-betty] TESTS: REVISE
What: tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx + test_RubricModal.test.tsx + docs/test-bible/frontend/components.md (Analysis / job surfaces row, new AST-2060 block, no RubricModal entry yet) — the fix is test-tree and bible only. qa-fix lands plan-fix #1–#3 as written. The [bug-repro] is `AST-2059: show rubric reads content from hydrated candidate detail, not the list payload`, which is red on pre-fix 06df211db (no `loading` prop there) and green on 4ee1d7029.

Notes (verified on ftr tip 4ee1d7029):
- Correction to my AST-2059 verdict: the two header tests did not go red. They stayed green through the `labelRow` fallback reading `content` from the list fixture. The plan's root cause is right, and the fix is a realistic fixture (list carries no rubric), not just `findByText`.
- The shipped code lines up with the plan: `contentLoading` is derived, so "Loading rubric…" is present on the first frame after the click, and the deferred-promise check works. `closeRubric` clears `detail`, so each failed-fetch case refetches after Close. `api` is called with one argument, so `toHaveBeenCalledWith("/api/candidates/c1")` holds.
- Failed-fetch case: supply the rejection lazily (`detail: () => Promise.reject(new Error("network"))`), not as an eager `Promise.reject(...)` value. An eager rejection can trip Vitest's unhandled-rejection guard before the click.
- Holds: AST-1771 order test, "falls back to raw vector labels", "normalizes an empty vector key", the existing RubricModal null-content fallback, and `test_JobAnalysisReportModal.test.tsx` (never clicks show rubric).

#### ada — 2026-10-08T21:53:55.838Z
`origin/sub/AST-2058/AST-2060-show-rubric-tests` @ `ffb81e6b8` · realistic fixtures, repro, loading

---

_Implementation detail may live in git history on `origin/dev`._
