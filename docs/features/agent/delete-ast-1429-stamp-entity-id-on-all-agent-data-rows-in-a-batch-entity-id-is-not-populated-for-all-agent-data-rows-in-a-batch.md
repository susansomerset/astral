# AST-1429 — Stamp entity_id on all agent_data rows in a batch (entity_id is not populated for all agent_data rows in a batch)

<!-- linear-archive: AST-1429 archived 2026-09-09 -->

## Linear archive (AST-1429)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1429/stamp-entity-id-on-all-agent-data-rows-in-a-batch-entity-id-is-not  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1423 — entity_id is not populated for all agent_data rows in a batch  
**Blocked by / blocks / related:** parent: AST-1423; blocks: AST-1431

### Description

## What this implements

Stamp `entity_id` on every `agent_data` row in a batch (SYSTEM / CACHE_* / TASK / NO_CACHE), not only RESPONSE. Approved ancestor: AST-984 (archived). Susan confirmed candidate 984. Parent AST-1423 is its own mini-epic (orphaned bug).

## Citations

`astral.batch.entity-agent-responses-latest-only` — AST-984 wrote RESPONSE-only `entity_id`; this ticket changes that write rule. Patch `docs/features/foundation/ast-984-retire-entity-agent-responses-columns.md` (do not create a new plan doc).

## Acceptance criteria

- [X] After a batch write (production `do_task` and Ad Hoc Test), SYSTEM / CACHE_* / TASK / NO_CACHE / RESPONSE rows that belong to that entity all carry the same `entity_id` as the RESPONSE.
- [X] `list_entity_latest_agent_refs` and hop/story readers still hold, or are updated if the RESPONSE-only index assumption breaks.
- [X] Historical backfill of old prompt rows is out of scope unless the plan says otherwise.

## Boundaries

Does not re-parent under AST-984/AST-975 (archived). Does not change UAT-batch filing. Does not invent a new `docs/features` file.

## Notes for planning

See parent AST-1423 Description As-is / To-be / Proposed steps. Dump: `craft_company_search_terms` batch; RESPONSE `entity_id=somerset`; prompt blocks null. AST-984 contract: `_store_response_block` sets `entity_id=index`; `_store_prompt_blocks` does not.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1423-entity-id-not-populated-for-all-agent-data-rows`, child `sub/AST-1423/<this-id>-<slug>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-19T00:24:53.071Z
[code-rubric] PROCEED (Commit: 4e1cfd4b) entity_id on prompt rows

#### joan — 2026-08-19T00:13:23.330Z
[board-joan] CANON: OK

#### betty — 2026-08-19T00:11:29.531Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — do_task/_store_prompt_blocks never asserts prompt-row entity_id stamp (SYSTEM/CACHE_*/TASK/NO_CACHE)

#### ada — 2026-08-19T00:08:35.252Z
`origin/sub/AST-1423/AST-1429-stamp-entity-id-on-all-agent-data-rows` @ `3da516d0` · stamp all batch rows

---

_Implementation detail may live in git history on `origin/dev`._
