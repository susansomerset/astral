# AST-1486 — FEEDBACK block_type still has null entity_id in agent_data batch

<!-- linear-archive: AST-1486 archived 2026-09-09 -->

## Linear archive (AST-1486)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1486/feedback-block-type-still-has-null-entity-id-in-agent-data-batch  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1423 — entity_id is not populated for all agent_data rows in a batch  
**Blocked by / blocks / related:** parent: AST-1423

### Description

[bug] still null on 'FEEDBACK' block_type.

## As-is

FEEDBACK `agent_data` rows in a batch still have `entity_id` null after the AST-1429 stamp (SYSTEM / CACHE_* / TASK / NO_CACHE were fixed; FEEDBACK was not).

## To-be

When the entity index is known, FEEDBACK rows written in the same batch should carry the same `entity_id` as the other prompt/response blocks.

## Acceptance criteria

- [X] `store_feedback_block` passes `entity_id=index if index else None` into `save_agent_data` (matches `_store_response_block`; no caller / hash / id changes).
- [X] `docs/ASTRAL_CODE_RULES.md` §2.4.1 names `store_feedback_block` / FEEDBACK alongside the other stamped block types.
- [X] Betty `[bug-repro]` `TestAst1486FeedbackEntityIdStamp` green against this product fix (verified locally pre-commit; test-fix owns formal run).

## Suggested engineer

Ada Lovelace (AST-1429 / AST-1431 implementer on this parent)

### Comments

#### radia — 2026-08-26T16:49:54.155Z
[review-fix] CLEAN / PROCEED — FEEDBACK `entity_id` stamp via `store_feedback_block`; [bug-repro] OK; What must still hold OK. Advisory only: optional `[bug-repro]` docstring tag. → Review Posted → User Testing (§3h shortcut).

#### ada — 2026-08-26T16:32:01.121Z
`origin/sub/AST-1423/AST-1486-feedback-block-type-still-has-null-entity-id` @ `e9a7cb35` · stamp FEEDBACK entity_id

#### betty — 2026-08-26T16:14:49.096Z
[bug-repro]
`origin/sub/AST-1423/AST-1486-feedback-block-type-still-has-null-entity-id` @ `cebd7aea` · repro lands red, awaits fix

#### betty — 2026-08-26T16:01:23.554Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — store_feedback_block/FEEDBACK never asserts entity_id stamp when index is known (AST-724/862 only assert block presence)

#### ada — 2026-08-26T15:48:20.555Z
`origin/sub/AST-1423/AST-1486-feedback-block-type-still-has-null-entity-id` @ `5d052049` · stamp FEEDBACK entity_id

---

_Implementation detail may live in git history on `origin/dev`._
