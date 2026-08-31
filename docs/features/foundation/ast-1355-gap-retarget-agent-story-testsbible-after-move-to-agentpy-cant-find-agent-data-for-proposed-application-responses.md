# AST-1355 — Gap: retarget agent-story tests/bible after move to agent.py (Can't find agent data for proposed application responses)

<!-- linear-archive: AST-1355 archived 2026-08-31 -->

## Linear archive (AST-1355)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1355/gap-retarget-agent-story-testsbible-after-move-to-agentpy-cant-find  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1316 — Can't find agent data for proposed application responses  
**Blocked by / blocks / related:** parent: AST-1316

### Description

## What this implements

Close the test/bible gap flagged by fix-board `[board-betty] TESTS: REVISE` on AST-1354: retarget bible + tests for `get_entity_agent_story` → `agent.py`, plus dangling TASK sibling repro coverage.

## Acceptance criteria

- [X] 1. Bible + component tests retargeted to `agent.py` ownership / imports.
- [X] 2. Repro-shaped dangling `propose_application_responses` TASK sibling → partial story, no exception stack.
- [X] 3. Publish to this child's `sub/*` only.

## Proposed change / resolve

- [X] Product: none — empty `code(AST-1355)` gate commit; AST-1354 on ftr.
- [X] Betty test + merge-tests + bible retarget kept.
- [X] Publish tip rebuilt onto ftr keepers only (no sync(dev) / no Merge remote-tracking / no AST-134x). `validate-sub-log` status=ok.

## Boundaries

- [X] Does not re-implement AST-1354 product.
- [X] Does not change canon (Joan CANON: OK).

## Git branch (authoritative)

Parent `ftr/AST-1316-cant-find-agent-data-for-proposed-application-responses`, child `sub/AST-1316/AST-1355-gap-agent-story-tests`.

### Comments

#### ada — 2026-08-13T02:03:59.024Z
`origin/sub/AST-1316/AST-1355-gap-agent-story-tests` @ `fdae78c23b58cb6746440d5f0771fb00a0979c11` · validate-sub-log status=ok

#### ada — 2026-08-13T02:03:55.463Z
`origin/sub/AST-1316/AST-1355-gap-agent-story-tests` @ `fdae78c23b58cb6746440d5f0771fb00a0979c11` · validate-sub-log status=ok · §9a clean

#### ada — 2026-08-13T02:03:28.511Z
`origin/sub/AST-1316/AST-1355-gap-agent-story-tests` @ `f6a1a6236a5694b78c4030ac957e339f9e441b29` · validate-sub-log ok · §9a clean

#### ada — 2026-08-13T02:00:45.501Z
`origin/sub/AST-1316/AST-1355-gap-agent-story-tests` @ `2a159f5b4cf8dfbb450f1abb0f00a4545ed8de58` · §9a clean · ftr dry-run clean

#### radia — 2026-08-13T01:58:57.363Z
[code-rubric] REVIEW (Commit: 0402abdc) strip sync dev product

#### ada — 2026-08-13T01:56:07.619Z
`origin/sub/AST-1316/AST-1355-gap-agent-story-tests` @ `0402abdcea216c37093c087334f78bcb3894fda2` · product already green for bug-repro

#### betty — 2026-08-13T01:54:36.847Z
[bug-repro]
`origin/sub/AST-1316/AST-1355-gap-agent-story-tests` @ `0402abdcea216c37093c087334f78bcb3894fda2` · dangling sibling partial story

#### betty — 2026-08-13T01:49:02.978Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md + tests/component/core/test_roster.py (TestEntityAgentStory* / AST-1274 soft-fail / AST-726 story) — retarget to agent.md + test_agent.py; missing dangling propose_application_responses TASK sibling → partial story / no exception-stack coverage

#### joan — 2026-08-13T01:48:48.838Z
[board-joan]  CANON: OK

context_tokens≈8000

#### ada — 2026-08-13T01:48:16.002Z
`origin/sub/AST-1316/AST-1355-gap-agent-story-tests` @ `9e982b62f9bc24aec55f599bbc2ae983c1812347` · plan-fix test/bible gap

---

_Implementation detail may live in git history on `origin/dev`._
