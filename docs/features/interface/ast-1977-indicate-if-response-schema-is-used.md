# AST-1977 — Indicate if {$RESPONSE_SCHEMA} is used

<!-- linear-archive: AST-1977 archived 2026-10-08 -->

## Linear archive (AST-1977)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1977/indicate-if-dollarresponse-schema-is-used  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Every task that returns structured output depends on its prompt carrying the `{$RESPONSE_SCHEMA}` token. A missing token blanks the contract the model is told to match (the AST-345 failure mode), and a duplicated token pays for the same schema text twice. Today Susan can only check this by opening each task's prompt editor. An "RSC" (response schema count) column on Manage Tasks makes it visible across every task in one glance, next to the System size it adds to.

## Functional scope

1. **Response schema count per task.** For each task on the Manage Tasks list, count how many times the literal token `{$RESPONSE_SCHEMA}` appears in the task's raw (unresolved) prompt text. The text counted is every segment that task sends: the effective system block (the task's own system prompt when it is non-empty, otherwise the agent's content, which is the same fallback the System column already uses), cache blocks A–D, the no-cache segment, and the user prompt. The count does not depend on which candidate is selected.
2. **RSC column.** The Manage Tasks table shows that count in a new right-aligned column headed **RSC**, placed directly to the left of the **System** column. A task whose prompts never use the token shows `0`.

## Component scope

* `src/ui/api/api_admin.py`: **modified**. The `/api/admin/tasks` row builder adds the response-schema count to each task row it serves.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`: **modified**. The task row type gains the new field, and the table gains the RSC header and cell to the left of System.

## Technical scope

* `src/ui/api/api_admin.py`: **modified function**. The Manage Tasks row enrichment (`_enrich_tasks`) already loads the full current task row and its agent for every task. It adds one integer field per row: the token's occurrence count summed across the raw prompt segments in Functional scope item 1. It counts the raw text before `resolve_tokens` runs, because resolution substitutes the token away. The token name comes from the existing token registry (`RESPONSE_SCHEMA` in `TOKEN_SOURCES`, `src/utils/config.py`) or one named reference, not a bare string literal copied into the function. The count is computed on the server. React only displays it.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`: **modified component**. Add the new field to the task row type, add a right-aligned `RSC` header between `Model` and `System`, and add the matching cell rendering the served integer. Change nothing else on the page.

## Architectural definition

* **Patterns to reuse:** no established pattern applies. No active pattern governs admin list columns. `patt.ui.admin-endpoint` is still a draft, so it is not cited.
* **New patterns proposed:** none.
* **Applicable statutes:**
  * [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>): the count is computed in `src/ui/api/` and served. React must not regex prompt text for the token itself.
  * [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>): the token name comes from the registry or one named reference, not a magic string literal in the row builder.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>): leave the other Manage Tasks columns, their token math, and the prompt editor untouched.
  * [`astral.ui.naming-conventions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.naming-conventions.md>): the new served field and TS property follow the existing row field naming (snake_case, like `system_prompt_tokens`).

## Acceptance criteria

1. **API field present.** `GET /api/admin/tasks` (as an admin) returns every row with an integer response-schema count field. **Fail:** any row lacks the field, or its value is not an integer.
2. **Count is correct.** For a task whose raw prompt segments contain `{$RESPONSE_SCHEMA}` exactly N times in total, counted on the DB row with `SELECT` + a manual count across `system_prompt` (or agent `content` when `system_prompt` is empty), `cache_prompt`, `cache_prompt_b`–`_d`, `nocache_prompt`, and `user_prompt`, the served field equals N. **Fail:** the served value differs from the manual count. This includes returning `0` because it counted resolved text after substitution.
3. **Agent fallback counted.** A task with an empty `system_prompt`, whose agent `content` contains the token once and whose other segments contain none, serves a count of `1`. **Fail:** it serves `0`.
4. **Candidate-independent.** The served count for a task is identical with and without `?candidate_id=<id>`. **Fail:** the values differ.
5. **Column placement.** On Manage Tasks, the header order reads `… Model | RSC | System | Base Cache …`, and each row's RSC cell shows the served integer, `0` included. **Fail:** RSC is missing, sits anywhere other than immediately left of System, or shows blank for `0`.
6. **No client-side counting.** `grep -n "RESPONSE_SCHEMA" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` returns nothing. **Fail:** any match, which means React is deriving the count itself.
7. **No bare literal in the row builder.** In the `_enrich_tasks` diff, the token appears only through a registry lookup or a single named reference, never as an inline `"{$RESPONSE_SCHEMA}"` / `"RESPONSE_SCHEMA"` string literal inside the loop. **Fail:** a bare literal appears in the function body.

## Open questions

none

## Proposed child tickets

#### 1: **RSC column on Manage Tasks - Ada**

Serve a per-task count of `{$RESPONSE_SCHEMA}` occurrences across the raw prompt segments from `/api/admin/tasks`, and show it as an **RSC** column immediately left of **System** on Manage Tasks. It does not change any other column, the token-estimate math, or the prompt editor.
**Citations:** `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.ui.naming-conventions`.
**Scope:**

* `src/ui/api/api_admin.py`: **modified function**. The Manage Tasks row enrichment (`_enrich_tasks`) already loads the full current task row and its agent for every task. It adds one integer field per row: the token's occurrence count summed across the raw prompt segments in Functional scope item 1. It counts the raw text before `resolve_tokens` runs, because resolution substitutes the token away. The token name comes from the existing token registry (`RESPONSE_SCHEMA` in `TOKEN_SOURCES`, `src/utils/config.py`) or one named reference, not a bare string literal copied into the function. The count is computed on the server. React only displays it.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`: **modified component**. Add the new field to the task row type, add a right-aligned `RSC` header between `Model` and `System`, and add the matching cell rendering the served integer. Change nothing else on the page.

Estimate: 2

**New patterns:** none.

**Monolith check:** Functional scope N = 2, children M = 1. One child is intentional: the served field and the column that shows it are one inseparable vertical slice, and neither is testable at UAT without the other.

**Scope partition check:** both Component scope files and both Technical scope items are claimed by child 1 only.

---

## Original brief

On the Manage Tasks list, show the number of occurences of {$RESPONSE_SCHEMA} in the task prompt content as a column for "RSC" (response schema count) for each task. to teh left of System prompt size.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
