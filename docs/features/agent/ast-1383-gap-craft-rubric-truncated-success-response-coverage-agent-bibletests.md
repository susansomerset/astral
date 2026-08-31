# AST-1383 — Gap: craft rubric truncated-success RESPONSE coverage (agent bible/tests)

<!-- linear-archive: AST-1383 archived 2026-08-31 -->

## Linear archive (AST-1383)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1383/gap-craft-rubric-truncated-success-response-coverage-agent-bibletests  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1379 — Response truncated after 289 tokens?  
**Blocked by / blocks / related:** parent: AST-1379

### Description

## What this implements

Close the test/bible gap flagged by fix-board `[board-betty] TESTS: REVISE` on AST-1380: add coverage in `docs/test-bible/core/agent.md` (and matching component tests) for Decision A — thinking-off / truncated success RESPONSE on craft rubrics (AST-903 floor + max_tokens gate present; abrams-shaped path uncovered).

## Acceptance criteria

- [X] Bible + tests cover craft rubric RESPONSE truncation treated as success / thinking-off path named in Betty's board verdict.
- [X] A repro-shaped case exists for truncated craft_get_rubric RESPONSE (`token_size` mid-criteria cut) that fails pre-fix and passes once AST-1380's product fix lands (or documents the hard-fail gate).
- [X] Publish to this child's `sub/*` only (Betty/astral-tests conventions via fix-lane stages as applicable).

## Proposed change (make-fix)

- [X] No product code — AST-1380 Decision A + failure banner already on tip (`64042fb2` ancestor).
- [X] Betty bible + `TestAst1380CraftRubricThinkingOffAndFailureBanner` on sub via `merge-tests(AST-1383)` @ `8dceeec4`.
- [X] `[bug-repro]` class green against current tip (3 passed).

## Boundaries

* Does not re-implement the product fix on AST-1380; lands test/bible work only.
* Does not change canon (Joan board was CANON: OK).

## Notes for planning

* Source verdict: AST-1380 `[board-betty] TESTS: REVISE` — docs/test-bible/core/agent.md — Decision A thinking-off / truncated success RESPONSE for craft rubrics.
* Sibling fix child: AST-1380. Ancestor doc: docs/features/consult/ast-903-uat-craft-get-json-parse.md.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1379-response-truncated-after-289-tokens`, child `sub/AST-1379/AST-1383-gap-craft-get-truncation-tests`. Created at bug-fix.

### Comments

#### ada — 2026-08-15T01:05:40.672Z
`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `8c9edcca26b2e7867db7b327c25d87ca79cb1ce0` · validate-sub-log ok

#### radia — 2026-08-15T01:04:29.196Z
[review-fix] CLEAN

Gap bible + Decision A / failure-banner tests lock AST-1380. [bug-repro] OK. No product delta. → User Testing (clean-review shortcut).

#### ada — 2026-08-15T01:02:18.955Z
`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `8dceeec4` · repro green, no product delta

#### betty — 2026-08-15T01:01:10.165Z
[bug-repro]
`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `8dceeec4` · repro lands red, awaits fix

#### betty — 2026-08-15T00:58:20.258Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — Decision A thinking-off + Provider-failed RESPONSE banner (AST-903 suite only; gap not landed yet)

#### joan — 2026-08-15T00:58:08.815Z
[board-joan]  CANON: OK

context_tokens≈8000

#### ada — 2026-08-15T00:57:42.989Z
`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `190870f4c334d1abebc01e32c9569c7d8e0eb15d` · test gap planned

---

_Implementation detail may live in git history on `origin/dev`._
