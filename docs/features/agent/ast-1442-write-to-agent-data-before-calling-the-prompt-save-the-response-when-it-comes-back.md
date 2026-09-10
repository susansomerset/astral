# AST-1442 — write to agent_data BEFORE calling the prompt, save the response when it comes back.

<!-- linear-archive: AST-1442 archived 2026-09-09 -->

## Linear archive (AST-1442)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1442/write-to-agent-data-before-calling-the-prompt-save-the-response-when  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When a job is killed or the server restarts during a provider call, Astral has no durable record of the prompt that was actually sent. Prompt segments are written to agent_data only after the call returns, so an interrupted run leaves a hole. This epic makes the sent prompt recoverable: commit assembled prompt segments before the provider is called, then save the response when it comes back.

## Functional scope

* For every stored LLM call (production task runs and Ad Hoc workbench Test), assembled prompt segments are committed to agent_data before the provider is invoked.
* The RESPONSE block is written only after the provider returns — success payload or failure-audit body, same outcomes as today.
* After a kill or process restart during the call, those prompt rows remain queryable by batch even when no RESPONSE row exists.
* Storage-off paths stay storage-off: a call that is not supposed to write agent_data still does not.
* When debug is on, the pre-call persist logs what was found and what was recorded per stored prompt block (index N/M, identifier, outcome) before the provider call; RESPONSE persist still logs after return. Long payloads follow the backend debug contract (first 15 / omitted / last 15). Quiet when debug is off.

## Architectural definition

**Patterns to reuse**

* `pattern.batch.entity-agent-responses` — latest-per-task refs stay RESPONSE-gated; prompt-only interrupted rows are audit state, not a new latest index.
* `pattern.layers.import-discipline` — persist stays in core orchestration; external still owns provider I/O; data still owns the write.
* `pattern.batch.entity-claim-process-release` — `batch_id` remains the golden ticket tying prompt rows, RESPONSE, ledger, and timesheets.

**New patterns proposed**

* `pattern.agent.prompt-persist-before-provider` — when agent_data storage is on, commit assembled prompt segments before the external provider call; commit RESPONSE after the call returns. Prompt writes must be durable before the await. A failed prompt write does not abort the provider call (best-effort, same as today). Archie approval required before implementation depends on the catalog id.

**Applicable statutes**

* `astral.agent.do-task-delegation` — core still delegates AI through the existing task entry; this epic reorders persist vs I/O inside that orchestration and does not let callers talk to the provider.
* `astral.batch.entity-agent-responses-latest-only` — RESPONSE still tagged with entity_id when known; list API still RESPONSE-only.
* `astral.layers.core-vs-external-bright-line` — provider I/O stays in external; persist stays in core.
* `astral.layers.import-direction` — no new cross-layer imports.
* `astral.standards.debug-contract-gated` — found/recorded only when debug is on; no data-layer debug noise.
* `astral.standards.data-raises-caller-logs` — data raises; core decides what to log.
* `astral.standards.in-scope-only` — sequencing + durability of existing agent_data writes only.
* `astral.standards.database-header-inventory` — no new tables; existing agent_data only.
* `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — reuse existing persist helpers; do not fork a second store path.
* `astral.standards.no-hardcoded-sets` — `BLOCK_TYPES` unchanged.
* `astral.standards.logging-via-utils` — debug via the shared logger helpers.
* `astral.standards.no-cross-contamination`
* `astral.batch.batch-id-first` — prompt and RESPONSE rows still keyed by the existing batch id.
* `astral.config.config-source-of-truth` — block types and entity types stay in config.

## Boundaries

* Does not add UI for prompt-only (in-flight or killed) batches. Agent story and latest-per-task stay RESPONSE-gated.
* Does not change block types, compression, content-dedup refs, or entity_id stamping on prompt and RESPONSE rows (AST-1423 / AST-1429 / AST-1431).
* Does not persist on bare Ad Hoc runs that are defined as storage-off.
* Does not write timesheets before the provider returns.
* Does not make prompt persist a hard gate: a failed prompt write still does not abort the provider call.
* Does not change entity state-machine behavior on kill (existing claim/release and balance-refusal hold rules stay as they are).
* Does not import agent data (AST-1439) or change Ad Hoc seven-segment editors (AST-1403).

## Acceptance criteria

* On a stored production task run, agent_data contains the prompt segments for that batch before the provider call is issued — verifiable by reading the batch while a call is in flight, or by killing mid-call and reading afterward.
* On a stored Ad Hoc workbench Test, the same: prompt segments are present even if the call is interrupted and no RESPONSE exists.
* When the provider returns successfully, a RESPONSE row is written with the same success body rules as today.
* When the provider returns a failure, a RESPONSE failure-audit row is written as today.
* After kill or restart mid-call: prompt rows for that batch are present; RESPONSE may be absent; a later successful run writes its own prompt and RESPONSE without corrupting the interrupted batch's prompt rows.
* A storage-off call writes no agent_data rows.
* When debug is on, prompt persist emits per-block found/recorded (index N/M) before the provider call; RESPONSE persist still emits after return. When debug is off, no new debug-contract lines.
* Latest-per-task and agent story still require a RESPONSE — a prompt-only interrupted batch does not become the latest story entry.

## Dependencies and blockers

none.

Adjacent in flight on the same persist surface: AST-1423 / AST-1429 / AST-1431 (entity_id on prompt rows, User Testing) and AST-1403 (Ad Hoc seven-segment, User Testing). This epic must preserve prompt-row entity_id stamps and seven-segment persist; it is not blocked by them.

## Open questions

none

## Proposed child tickets

#### 1: **Persist prompt before provider - Ada**

Every stored LLM call (production task run and Ad Hoc workbench Test) commits assembled prompt segments to agent_data before the provider is called, and writes RESPONSE only after return. Kill or restart mid-call leaves those prompt rows queryable by batch. Does not own UI, timesheets, state transitions, storage-off Ad Hoc, or a new table.
**Citations:** `pattern.agent.prompt-persist-before-provider` (proposed), `pattern.batch.entity-agent-responses`, `astral.agent.do-task-delegation`, `astral.batch.entity-agent-responses-latest-only`, `astral.standards.debug-contract-gated`, `astral.layers.core-vs-external-bright-line`.
**Estimate: 3**

**Monolith check:** Functional scope has five capabilities; one child is intentional — one inseparable sequencing invariant across the two stored call sites, which share persist helpers in one orchestration module. Splitting would collide on the same surface and leave kill-during-call UAT incomplete.

**New patterns:** this child introduces `pattern.agent.prompt-persist-before-provider` once Archie approves the catalog id.

---

## Original brief

Prompt data is only saved to agent data when the prompt returns, no way to know what was actually sent if we kill a job or the server restarts.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
