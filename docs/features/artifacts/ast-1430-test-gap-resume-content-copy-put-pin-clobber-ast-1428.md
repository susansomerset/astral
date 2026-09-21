# AST-1430 — Test gap: resume_content copy + PUT pin-clobber (AST-1428)

<!-- linear-archive: AST-1430 archived 2026-08-31 -->

## Linear archive (AST-1430)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1430/test-gap-resume-content-copy-put-pin-clobber-ast-1428  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1422 — Finalize job resume isn't getting parsed into the job_resume renderer  
**Blocked by / blocks / related:** parent: AST-1422

### Description

## What this implements

Test-hole gap for AST-1428 / AST-1422 (orphaned-bug fix-board TESTS: REVISE). Land the repro-first tests Betty named so make-fix on AST-1428 implements against an already-raised bar.

## Citations

fix-intake orphaned bug-fix: fix-board REVISE files a sibling gap child instead of qa-fix inline. Board brief copied from AST-1428.

## Acceptance criteria

- [X] 1. `PUT …/artifacts/job_resume` no longer asserted as writing a body dict onto the pin (`TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_body_dict` must match keep-pin: blob in `resume_content`, pin stays an id string).
- [X] 2. Coverage exists for sibling `resume_content` copy/unwrap after a successful `finalize_job_resume` pin (`docs/test-bible/core/agent.md` AST-1099 — currently missing).
- [X] 3. At least one `[bug-repro]` test fails on the pre-fix tree and will pass once AST-1428 make-fix lands.

## Boundaries

Does not implement the product copy/keep-pin (AST-1428). Does not touch cover letter / proposed_answers.

## Notes for planning

Betty board on AST-1428:
What: docs/test-bible/ui/api/api_jobs.md — broken test — TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_body_dict asserts dict onto pin; docs/test-bible/core/agent.md AST-1099 — currently missing coverage — no sibling resume_content copy/unwrap after finalize pin

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1422-finalize-job-resume-not-parsed`, child `sub/AST-1422/<this-id>-test-gap-resume-content-copy-put-pin`.

### Comments

#### radia — 2026-08-19T00:44:50.206Z
[code-rubric] REVIEW (Commit: 8d35b2ae) gap repro wiring-only

#### betty — 2026-08-19T00:14:55.093Z
[bug-repro]
`origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin` @ `c5dd7b40` · repro lands red, awaits fix

#### chuckles — 2026-08-19T00:07:19.295Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_jobs.md — broken test — TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_body_dict asserts dict onto pin; docs/test-bible/core/agent.md AST-1099 — missing coverage — no sibling resume_content copy/unwrap after finalize pin

---

_Implementation detail may live in git history on `origin/dev`._
