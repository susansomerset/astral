# AST-1382 — gap: Base Resume Issues tests/bible (board-betty REVISE)

<!-- linear-archive: AST-1382 archived 2026-08-31 -->

## Linear archive (AST-1382)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1382/gap-base-resume-issues-testsbible-board-betty-revise  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1362 — Base Resume Issues  
**Blocked by / blocks / related:** parent: AST-1362

### Description

## What this implements

Close the test/bible gap flagged by fix-board `[board-betty] TESTS: REVISE` on AST-1381:

* Retarget docs/test-bible/frontend/components.md (+ core/builder.md, core/candidate.md) — AST-1351/996 fixtures assert `accomplishments:str` (will break under string[]).
* Add repro coverage for: string[] single-bullet emit; contact/competencies `|`→`•`; content-Save persisting `prior_experience` format / free_prose print.

## Acceptance criteria

1. Bible + component fixtures no longer assume accomplishments is a single str where the product contract is string[].
2. At least one [bug-repro]-style coverage path for each of: string[]→single bullet emit, contact/competencies pipe markers, prior_experience format persist→print.
3. Publishes to origin/sub/AST-1362/<this-child> only.

## Make-fix checklist

- [X] No additional product delta required — AST-1381 product already on this sub greens Betty's `[bug-repro]`
- [X] `TestAst1382BugReproBaseResumeIssues` (4) green
- [X] ArtifactEditor `AST-1382` content-Save `resume_structure` bundling green
- [X] ExperienceJobsEditor / ArtifactEditor AST-1351|996 retargets green
- [X] `TestAst996ExperienceJobArrayConfig` + `TestAst1349ExperienceArrayContract` green
- [X] Did not edit `tests/` or `docs/test-bible/**` (Betty owns)

## Notes

Product fix lands on sibling AST-1381. This gap child owns test/bible only (or test+minimal product test harness), not a second product rewrite.

### Comments

#### radia — 2026-08-15T01:08:46.207Z
[code-rubric] REVIEW (Commit: df202bf6) gap clean; frame discuss

Gap deliverable (tests+bible) is complete. Discuss: publish-ref frame also carries AST-1381 product (expected) plus an unrelated AST-1383 test commit — merge attribution hygiene only, no fix-now.

#### katherine — 2026-08-15T01:05:53.728Z
`origin/sub/AST-1362/AST-1382-gap-base-resume-tests` @ `df202bf62be5ff87f7d930d2f76ee03aa108568c` · [bug-repro] green + manifest green

#### katherine — 2026-08-15T01:05:03.656Z
`origin/sub/AST-1362/AST-1382-gap-base-resume-tests` @ `df202bf62be5ff87f7d930d2f76ee03aa108568c` · bug-repro green, no product delta

#### betty — 2026-08-15T01:03:46.869Z
[bug-repro]
`origin/sub/AST-1362/AST-1382-gap-base-resume-tests` @ `df202bf62be5ff87f7d930d2f76ee03aa108568c` · repro lands red, awaits fix

#### joan — 2026-08-15T00:58:26.076Z
[board-joan] CANON: OK

Test/bible-only gap: fixture retarget + bible rows for accomplishments string[], collapsible headers, `|`→`•`, format-Save→print. No src/ edits; no canon statute/pattern update.

#### betty — 2026-08-15T00:58:12.389Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md (+ core/builder.md, core/candidate.md, utils/config.md) — retarget AST-996/1349/1351 accomplishments:str fixtures; missing [bug-repro] for string[] single-bullet emit, contact/competencies |→•, and content-Save prior_experience format→print

#### katherine — 2026-08-15T00:57:17.986Z
`origin/sub/AST-1362/AST-1382-gap-base-resume-tests` @ `323ba711f36acb6eba00f1f69ddb4975ba95b8e3` · gap fixture plan-fix

---

_Implementation detail may live in git history on `origin/dev`._
