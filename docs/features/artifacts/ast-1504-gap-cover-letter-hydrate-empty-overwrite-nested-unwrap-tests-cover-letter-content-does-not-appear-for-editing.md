# AST-1504 — Gap: cover letter hydrate empty-overwrite / nested unwrap tests (Cover Letter content does not appear for editing)

<!-- linear-archive: AST-1504 archived 2026-09-09 -->

## Linear archive (AST-1504)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1504/gap-cover-letter-hydrate-empty-overwrite-nested-unwrap-tests-cover  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1491 — Cover Letter content does not appear for editing  
**Blocked by / blocks / related:** parent: AST-1491

### Description

## What this implements

Test-gap sibling of AST-1499 (orphaned-bug fix-board TESTS: REVISE — not run inline on the fix child). Land repro coverage for cover-letter display hydrate gaps Betty named so Subject/Letter/signature empty-overwrite / nested hop unwrap / pin leave-on-miss cannot regress without a red test.

## As-is

`docs/test-bible/core/tracker.md` (AST-1116 hydrate) / `TestAst1116HydrateCoverLetterNormalize` does not exercise the repro gaps: pin leave-on-miss, nested hop unwrap, nonempty gate vs empty Subject·Letter·signature overwrite.

## To-be

At least one test fails against the pre-fix product tree for the empty Cover Letter editor hydrate symptom (or the named hydrate gaps) and passes once AST-1499's hydrate fix lands. Bible entry names that coverage.

## Acceptance criteria

- [X] `TestAst1504CoverLetterHydrateDisplayGaps` covers nested unwrap, empty-spine gate, and pin leave-on-miss.
- [X] Pin leave-on-miss is red-first: resolve `{"unrelated": "meta"}` → assert overlay keeps `"pin-cover"` (Radia fix-now).
- [X] Manifest green on tip with AST-1499 product present (`b5847de3`).
- [X] Does not implement product hydrate fix (AST-1499).

## Board brief (from AST-1499)

```
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md (AST-1116 hydrate) — missing coverage — repro gaps (pin leave-on-miss / nested hop unwrap / nonempty gate vs empty Subject·Letter·signature overwrite) not exercised by TestAst1116HydrateCoverLetterNormalize; Blast radius expects Betty extend before make-fix.
```

## Citations

AST-1499 plan-fix patch on `docs/features/artifacts/ast-1116-cover-letter-field-defs.md`. Betty board REVISE on AST-1499.

## Boundaries

Does not implement the product hydrate fix (AST-1499). Does not expand into a bible sweep beyond the named gap.

## Scope

## Component scope

* `docs/test-bible/core/tracker.md` — modified: name the hydrate repro coverage Betty flagged.
* Tests under Betty's tree for tracker hydrate — new/modified to fail pre-fix and pass post-fix.

## Technical scope

* Bible + test nodes only — `TestAst1504CoverLetterHydrateDisplayGaps` for pin leave-on-miss / nested unwrap / empty-overwrite nonempty gate; no product code on this child.

## Git branch (authoritative)

parent `ftr/AST-1491-cover-letter-content-does-not-appear-for-editing`, child `sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests`.

## QA test manifest

1. Bug-repro (nested unwrap + empty-spine gate + pin leave-on-miss): `tests/component/core/test_tracker.py::TestAst1504CoverLetterHydrateDisplayGaps`
   * Pin leave-on-miss red-first: `::test_hydrate_leaves_pin_when_resolve_misses` — resolve `{"unrelated": "meta"}` → assert overlay keeps `"pin-cover"` (Radia fix-now / return pass)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1504CoverLetterHydrateDisplayGaps \
  -q
```

**Bible shasum: **`docs/test-bible/core/tracker.md` → `c8285aa02050af9d72bc033f0f062fbba8499a1d`

**Verified return pass:** all three nodes red on pre-AST-1499 product; pin-miss green on post-AST-1499. Resolve §9a clean (dev + ftr).

**Publish: **`origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `b5847de3` ← `origin/tests` `595ccaca`

### Comments

#### betty — 2026-08-26T16:18:33.502Z
[qa-handoff]
Pin leave-on-miss strengthened (Radia fix-now).

`test_hydrate_leaves_pin_when_resolve_misses` now resolves `{"unrelated": "meta"}` and asserts overlay keeps `"pin-cover"` — red on pre-AST-1499 (empty spine); green after AST-1499 helper. Bible AST-1504 updated.

`origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `b5847de3` · merge-tests ← `origin/tests` `595ccaca`

Stay Review Posted — reassigned Katherine to finish resolve → User Testing. Epic worktree synced to sub tip.

#### katherine — 2026-08-26T16:14:00.664Z
[qa-handoff]
@Betty White

Radia fix-now on AST-1504 (Review Posted → resolve): `TestAst1504CoverLetterHydrateDisplayGaps::test_hydrate_leaves_pin_when_resolve_misses` is green on **pre-AST-1499** product (resolve `None` already left the pin before the fix). It is not a red→green [bug-repro] gate.

**Please strengthen or reclassify on astral-tests, then merge-tests(AST-1504) to** `origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests`:

Preferred strengthen (Radia’s example): change that node so resolve returns a **nonempty non-cover** body (e.g. `{"unrelated": "meta"}`) and assert the overlay keeps the pin string `"pin-cover"` — pre-fix installed empty Subject/Letter/signature spine (or the raw body); post-AST-1499 leaves the pin. That makes pin leave-on-miss red-first.

Alternatively: drop/reclassify that node out of the [bug-repro] red→green set (nested unwrap + empty-spine gate nodes already carry the gate) and update `docs/test-bible/core/tracker.md` AST-1504 accordingly.

Do **not** rewrite foreign AST-1493/AST-1500 history; keep AST-1504-owned test commit clean.

When landed: reassign Katherine; she re-syncs and advances User Testing.

#### radia — 2026-08-26T16:12:44.367Z
[code-rubric] REVIEW (Commit: 4ff9654b) Pin-miss repro not red-first

#### katherine — 2026-08-26T16:10:09.839Z
`origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `4ff9654b` · [bug-repro] green (3 passed)

#### betty — 2026-08-26T16:03:25.009Z
[bug-repro]
`origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests` @ `85ee1c89` · repro lands red, awaits fix

#### chuckles — 2026-08-26T15:56:31.825Z
Test-gap sibling of AST-1499. Betty's board on AST-1499:

[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md (AST-1116 hydrate) — missing coverage — repro gaps (pin leave-on-miss / nested hop unwrap / nonempty gate vs empty Subject·Letter·signature overwrite) not exercised by TestAst1116HydrateCoverLetterNormalize; Blast radius expects Betty extend before make-fix.

qa-fix runs here (orphaned-bug REVISE is not inline on the fix child). Use that brief.

---

_Implementation detail may live in git history on `origin/dev`._
