# AST-1379 — Response truncated after 289 tokens?

<!-- linear-archive: AST-1379 archived 2026-08-31 -->

## Linear archive (AST-1379)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1379/response-truncated-after-289-tokens  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

`craft_get_rubric` for candidate `abrams` (batch `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948`) stores a RESPONSE whose `block_data` cuts mid-criteria string after ~289 tokens (`token_size: 289`). `agent_performance.status` is `success` with a full `vector_reviews` list, but `agent_payload.criteria` is incomplete JSON (first criterion `content` ends mid-sentence). Downstream parse/use sees truncated rubric output treated like a finished hop.

## To-be

A successful `craft_get_rubric` RESPONSE is complete, parseable JSON with every crafted criterion fully written — or the hop fails loudly under the existing `max_tokens` / unusable-response failure class instead of persisting a truncated payload as success.

## Proposed steps

1. Confirm whether this run hit provider `stop_reason=max_tokens` (or equivalent) and what `max_tokens` / brain setting `do_task` actually sent for this hop (AST-903 shipped a `CRAFT_RUBRIC_MAX_TOKENS=32000` floor for craft rubric UI keys — check regression or a path that bypasses it).
2. If the floor is skipped or undercut on this entry path, restore/apply it for `craft_get_rubric` (and sibling craft rubric keys if the same hole exists).
3. Ensure truncated JSON cannot land as `agent_performance.status=success` + partial `agent_payload` — hard-fail before persist when stop is max_tokens / content is unterminated, matching AST-903's provider gate.
4. Re-run `craft_get_rubric` for `abrams` (or equivalent) and verify a full criteria array persists with RESPONSE `token_size` well above a mid-vector cut.

## Evidence (filing dump, condensed)

* Title symptom: response truncated after 289 tokens.
* `task_key`: `craft_get_rubric`
* `entity_id`: `abrams`
* RESPONSE `agent_data_id`: `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948-response-86ff123a40218dbb`
* RESPONSE `token_size`: `289`
* Cut point (first criterion `content`): ends at `…even though no title` mid-grade row; remaining criteria never written.

### Comments

#### chuckles — 2026-08-15T00:42:10.867Z
Ancestor candidates (ranked — pick one, ask about one, or reject the set):

1. **AST-903** (parent **AST-900**) — strongest match. Prior UAT: `craft_get_rubric` truncated mid-`criteria[].content`, `Unterminated string` / success-shaped payload. Shipped `CRAFT_RUBRIC_MAX_TOKENS=32000` floor + provider JSON `max_tokens` hard-fail. This looks like a regression or a path that misses that floor.
2. **AST-1377** / parent **AST-1376** — live neighbor. Plan explicitly parked `craft_do_rubric max_tokens / truncated JSON` as **out of epic**; same symptom family named next to current agent_data ensure work.
3. **AST-1190** (parent **AST-1164**, archived) — empty/unusable provider response surfacing; shares `max_tokens` failure vocabulary with the craft truncate path, but owns hollow/empty classification not craft token budget.
4. **AST-1191** (parent **AST-1164**, archived) — artifact hop failure release + debug trail for provider failures including `max_tokens`; downstream handling, not the truncate root.
5. **AST-1368** — wires Ideal Day into craft prompts including `craft_get_rubric`; same task key, different problem (prompt tokens, not RESPONSE truncation).

Reply with a pick (or “none / orphan mini-parent”) and reassign Chuckles when ready; move to Todo to release bug-fix.

---

_Implementation detail may live in git history on `origin/dev`._
