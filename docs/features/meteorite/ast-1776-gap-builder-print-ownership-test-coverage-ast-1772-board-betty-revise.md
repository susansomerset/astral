# AST-1776 — gap: builder print ownership test coverage (AST-1772 board-betty REVISE)

<!-- linear-archive: AST-1776 archived 2026-09-24 -->

## Linear archive (AST-1776)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1776/gap-builder-print-ownership-test-coverage-ast-1772-board-betty-revise  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1763 — Remove company name validation error on Print Resume and Print Cover letter  
**Blocked by / blocks / related:** parent: AST-1763

### Description

## What this implements

Test-hole gap from \[board-betty\] TESTS: REVISE on AST-1772 — builder print ownership tests and bible rows still assume company short name is mandatory.

## Scope

## Component scope

* `docs/test-bible/core/builder.md` — modified: TestBuildResume / TestBuildCoverLetterDebugPaths rows must match post-fix ownership (candidate_id-first, null company_id allowed).
* astral-tests `tests/component/core/test_builder.py` (or existing builder component suite) — new or revised nodes for null `company_id` + populated `candidate_id` print success and updated failure expectations.

## Technical scope

* Revise broken assertions that still expect "Job missing company short name" when `candidate_id` is present on the job dict.
* Add at least one \[bug-repro\]-style test that fails pre-AST-1772 product and passes once builder resolves via `candidate_id`.
* Bible entry updated to name the nodes. No product code in this gap ticket (product is AST-1772).

## Acceptance criteria

- [X] Builder component tests cover null company + candidate_id print success for resume and cover letter entry points.
- [X] Obsolete "missing company" assertions updated for candidate_id-first ownership.
- [X] Bible § builder names the revised/new nodes.
- [X] Does not change product code (that is AST-1772).

## Boundaries

Product shell fix is AST-1772. This gap is tests + bible only.

## Notes for planning

Betty board: docs/test-bible/core/builder.md — TestBuildResume / TestBuildCoverLetterDebugPaths broken + missing null-company success coverage.

## Git branch (authoritative)

Parent `ftr/AST-1763-remove-company-name-validation-error-on-print-resume-and-print-cover-letter`. Child ref recorded in epic registry at bug-fix dispatch.

### Comments

#### betty — 2026-09-22T01:50:54.121Z
[qa-handoff]
Tip republished clean for merge-child: `origin/sub/AST-1763/AST-1776-gap-builder-print-ownership-test-coverage` @ `c9e0bdd4` — ftr…sub is only docs(AST-1776) plan section + test/merge-tests(AST-1776) bible+test_builder + empty code(AST-1776). Dropped sync(dev), AST-1772 absorb, Avail/dispatcher, AST-1771 bleed. Manifest 6/6 green on ftr product. Radia trim finding addressed → User Testing.

#### katherine — 2026-09-22T01:47:36.158Z
[qa-handoff]
@Betty White — Radia fix-now on AST-1776: trim publish tip to test-tree only.

Rebuild `origin/sub/AST-1763/AST-1776-gap-builder-print-ownership-test-coverage` from `origin/ftr/AST-1763-remove-company-name-validation-error-on-print-resume-and-print-cover-letter` so `ftr…sub` is only:
1. `docs(AST-1776): plan-fix` — Bug AST-1776 section
2. `test(AST-1776)` / `merge-tests(AST-1776)` — **only** `docs/test-bible/core/builder.md` + `tests/component/core/test_builder.py` (keep `TestAst1776BuilderPrintOwnership` + revised ownership ladders)
3. optional empty `code(AST-1776): — test-tree only`
4. then reassign me for resolve → UT

**Drop:** `sync(dev)`, `sync(AST-1776): absorb AST-1772 product`, dispatcher/database Avail smuggle, AST-1771 interface/frontend bleed. Product stays on AST-1772/ftr — not this gap tip.

Current tip (docs resolve only): `2845003e94740d6f3ef09e3e1bab17f46f856b7c`. Status left **Review Posted**.

#### radia — 2026-09-22T01:44:37.622Z
[code-rubric] REVIEW (Commit: 552145cd) trim tip to test-tree only — drop sync(dev)/product absorb smuggle

#### katherine — 2026-09-22T01:43:22.598Z
`origin/sub/AST-1763/AST-1776-gap-builder-print-ownership-test-coverage` @ `552145cded09702eca9899e4feb7582f6d2ddb19` · [bug-repro] red→green; manifest 9 passed

#### betty — 2026-09-22T01:37:57.824Z
[bug-repro]
`origin/sub/AST-1763/AST-1776-gap-builder-print-ownership-test-coverage` @ `894eb5e6` · repro lands red, awaits fix

#### betty — 2026-09-22T01:37:54.819Z
[bug-repro]
`origin/sub/AST-1763/AST-1776-gap-builder-print-ownership-test-coverage` @ `894eb5e6` · repro lands red, awaits fix

#### betty — 2026-09-22T01:32:21.028Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/builder.md / tests/component/core/test_builder.py — TestBuildResume + TestBuildCoverLetterDebugPaths still assert "missing company"; null-company + candidate_id success and [bug-repro] TestAst1776BuilderPrintOwnership not landed

#### joan — 2026-09-22T01:31:47.882Z
[board-joan]  CANON: OK

#### katherine — 2026-09-22T01:31:04.230Z
`origin/sub/AST-1763/AST-1776-gap-builder-print-ownership-test-coverage` @ `58ac42ee43a5d9f89438d4386e0cd6883e30b692` · gap ownership test plan

---

_Implementation detail may live in git history on `origin/dev`._
