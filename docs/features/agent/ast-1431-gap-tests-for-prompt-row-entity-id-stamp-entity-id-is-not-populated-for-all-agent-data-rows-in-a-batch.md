# AST-1431 — gap: tests for prompt-row entity_id stamp (entity_id is not populated for all agent_data rows in a batch)

<!-- linear-archive: AST-1431 archived 2026-09-09 -->

## Linear archive (AST-1431)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1431/gap-tests-for-prompt-row-entity-id-stamp-entity-id-is-not-populated  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1423 — entity_id is not populated for all agent_data rows in a batch  
**Blocked by / blocks / related:** parent: AST-1423

### Description

## What this implements

Test-hole gap filed from AST-1429 fix-board `[board-betty] TESTS: REVISE`. Cover `do_task` / `_store_prompt_blocks` stamping `entity_id` on SYSTEM / CACHE_* / TASK / NO_CACHE (not only RESPONSE). Bible: `docs/test-bible/core/agent.md`. Patch the existing AST-984 plan doc with `## Bug: <this-id>` — do not create a new plan doc.

## Citations

Betty: docs/test-bible/core/agent.md — missing coverage — do_task/*store_prompt_blocks never asserts prompt-row entity_id stamp (SYSTEM/CACHE**/TASK/NO_CACHE)

## Acceptance criteria

- [X] A test exists that fails against pre-fix product (prompt rows `entity_id` null) and passes once AST-1429's stamp lands.
- [X] Bible `docs/test-bible/core/agent.md` names that coverage.

## Boundaries

Does not implement the product stamp (AST-1429). Does not amend canon (Joan CANON: OK).

## Notes for planning

blockedBy AST-1429 — product fix first. Orphaned-bug gap child (fix-intake bug-fix): not qa-fix inline on AST-1429.

### Comments

#### radia — 2026-08-19T00:44:56.853Z
[code-rubric] REVIEW (Commit: 917d9145) prompt entity_id tests OK

#### ada — 2026-08-19T00:39:18.800Z
`origin/sub/AST-1423/AST-1431-gap-tests-for-prompt-row-entity-id-stamp` @ `917d9145`

#### betty — 2026-08-19T00:36:27.082Z
[bug-repro]
`origin/sub/AST-1423/AST-1431-gap-tests-for-prompt-row-entity-id-stamp` @ `917d9145` · repro lands red, awaits fix

#### joan — 2026-08-19T00:30:14.796Z
[board-joan] CANON: OK

#### betty — 2026-08-19T00:29:37.710Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — TestAst984EntityColumnRetired still RESPONSE-only; no prompt-row entity_id stamp or Ad Hoc call-site assertion

#### ada — 2026-08-19T00:28:18.085Z
`origin/sub/AST-1423/AST-1431-gap-tests-for-prompt-row-entity-id-stamp` @ `5dda9288` · bible names prompt stamp

---

_Implementation detail may live in git history on `origin/dev`._
