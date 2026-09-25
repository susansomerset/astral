# AST-1339 — gap: METEORITE_NEW_RETRY fail-dest/claim tests (AST-1319)

<!-- linear-archive: AST-1339 archived 2026-08-19 -->

## Linear archive (AST-1339)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1339/gap-meteorite-new-retry-fail-destclaim-tests-ast-1319  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1319 — Implement _RETRY for new meteorite states  
**Blocked by / blocks / related:** parent: AST-1319

### Description

## What this implements

gap (tests): Cover METEORITE_NEW → METEORITE_NEW_RETRY fail-dest / claim companions and update TestAst1053MeteoriteGdlJobStates / BOT_BLOCKED prior equality for the new holding — Betty board REVISE on AST-1338.

## Board source

[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md (+ core/consult.md) — missing METEORITE_NEW→METEORITE_NEW_RETRY fail-dest/claim coverage (repro not in TestConsultBatchFailDest / no AST-898 twin); Blast radius breaks TestAst1053MeteoriteGdlJobStates priors/UI + BOT_BLOCKED prior equality

## As-is

No bible/test coverage for meteorite NEW_RETRY fail-dest/claim twin of AST-898; existing AST-1053 / BOT_BLOCKED asserts will break when METEORITE_NEW_RETRY priors/UI land.

## To-be

Bible + tests assert METEORITE_NEW→METEORITE_NEW_RETRY / second-strike ERROR_QUALIFY and claim companions; AST-1053 / BOT_BLOCKED priors updated for the new holding.

## Proposed change (make-fix)

1. [x] Product already on parent ftr via AST-1338 — no further `src/` delta (repro passable against current tree)
2. [x] Betty qa-fix landed `[bug-repro]` + bible (`TestAst1339MeteoriteNewRetryQualifyHolding`, `TestConsultBatchFailDest` rows, AST-1053 / AST-1195 revisions)

## Related

Sibling of AST-1338 (fix child). Parent AST-1319.

## Git branch (authoritative)

Parent `ftr/AST-1319-implement-retry-for-new-meteorite-states`, child `sub/AST-1319/<this-id>-gap-meteorite-new-retry-tests`.

### Comments

#### radia — 2026-08-12T15:16:50.286Z
[code-rubric] PROCEED (Commit: 8d8876d1) METEORITE retry tests locked

CLEAN — test/bible gap for METEORITE_NEW_RETRY. No fix-now. [bug-repro] asserts first-strike→holding / second-strike→ERROR_QUALIFY.

#### betty — 2026-08-12T15:12:58.346Z
[bug-repro]
`origin/sub/AST-1319/AST-1339-gap-meteorite-new-retry-tests` @ `8d8876d1` · repro lands red, awaits fix

#### betty — 2026-08-12T15:07:02.381Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md (+ core/consult.md) — missing METEORITE_NEW→METEORITE_NEW_RETRY fail-dest/claim twin + AST-1053/BOT_BLOCKED prior/UI cutover still red — plan Proposed change is the gap; no coverage on tip yet

#### joan — 2026-08-12T15:06:48.709Z
[board-joan]  CANON: OK

context_tokens≈8000

#### hedy — 2026-08-12T15:06:07.086Z
`origin/sub/AST-1319/AST-1339-gap-meteorite-new-retry-tests` @ `52dfe5fb` · test/bible gap plan

---

_Implementation detail may live in git history on `origin/dev`._
