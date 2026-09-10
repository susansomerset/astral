# AST-1554 — gap: job resume body-replica tests (flip keep-pin; cover replica)

<!-- linear-archive: AST-1554 archived 2026-09-09 -->

## Linear archive (AST-1554)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1554/gap-job-resume-body-replica-tests-flip-keep-pin-cover-replica  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** betty  
**Priority / estimate:** None / —  
**Parent:** AST-1547 — Job resume content is not saving to the job record  
**Blocked by / blocks / related:** parent: AST-1547

### Description

## What this implements

Close the test/bible gap named by fix-board on AST-1548: flip keep-pin assertions and add body-on-slot + cover replica / no-hydrate-pin-resolve coverage for the AST-1548 repro.

## Scope

### Component scope

* `tests/` (and `docs/test-bible/core/agent.md` § AST-1430, `docs/test-bible/ui/api/api_jobs.md` § AST-1430) — modified/new: replace keep-pin nodes (`test_finalize_copies_resume_content_keeps_pin`, `test_put_job_resume_writes_resume_content_keeps_pin`) that assert pin on `job_resume`; add coverage for body-on-slot + cover replica and no hydrate pin-resolve matching AST-1548 To-be.
* Product `src/**` — out of scope for this gap child (owned by AST-1548 fix child).

### Technical scope

* Test modules covering finalize hop persist + job artifact PUT/hydrate — modified/new tests and bible rows so keep-pin contracts are retired and body-replica / no-pin-resolve behavior is asserted. Why: Betty board REVISE on AST-1548 named these broken/missing nodes.

## Notes for planning

Sibling of AST-1548. Board: [board-betty] TESTS: REVISE — docs/test-bible/core/agent.md § AST-1430 + ui/api/api_jobs.md § AST-1430 — keep-pin nodes assert pin on job_resume; missing body-on-slot + cover replica / no-hydrate-pin-resolve for AST-1548 repro.

## Git branch (authoritative)

Parent `ftr/AST-1547-job-resume-content-not-saving`, child `sub/AST-1547/<this-id>-gap-job-resume-body-replica-tests`.

### Comments

#### chuckles — 2026-08-31T21:19:42.111Z
Test/bible flip for body-replica landed via `test(AST-1548)` + `merge-tests(AST-1548)` onto the fix child tip and is already on `origin/ftr/AST-1547-job-resume-content-not-saving`. Gap sub lacks a product `code(AST-1554)` sequence by design (test-only sibling). Canceling this gap ticket so prep-uat/finish-up can proceed on the mini-parent; coverage is not lost.

#### betty — 2026-08-31T21:18:07.323Z
`origin/sub/AST-1547/AST-1554-gap-job-resume-body-replica-tests` @ `c866cd2b` · body-replica tests green

#### betty — 2026-08-31T21:09:34.091Z
[board-betty] TESTS: OK

#### joan — 2026-08-31T21:09:14.319Z
[board-joan]  CANON: OK

context_tokens≈14000

#### ada — 2026-08-31T21:07:54.203Z
`origin/sub/AST-1547/AST-1554-gap-job-resume-body-replica-tests` @ `e804efe8267ff10a8c667498686f4ae27b421f3d` · flip keep-pin test gap

---

_Implementation detail may live in git history on `origin/dev`._
