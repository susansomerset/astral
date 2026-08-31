---
id: pattern.agent.prompt-persist-before-provider
name: Persist assembled prompt before provider call
status: proposed
proposed_in: AST-1442
approved_by: null
approved_at: null
canonical_refs:
  - path: src/core/agent.py
    symbol: do_task
  - path: src/core/agent.py
    symbol: run_adhoc_workbench_test
  - path: src/core/agent.py
    symbol: _store_prompt_blocks
related_statutes:
  - astral.agent.do-task-delegation
  - astral.batch.entity-agent-responses-latest-only
  - astral.layers.core-vs-external-bright-line
  - astral.standards.debug-contract-gated
  - astral.batch.batch-id-first
supersedes: null
superseded_by: null
---

# Problem

Prompt segments are only written after the provider returns, so a kill or process restart during the await leaves no durable record of what was sent.

# Solution shape

When `agent_data` storage is on, commit assembled prompt segments via existing `_store_prompt_blocks` / `save_agent_data` **before** the external provider await; write RESPONSE after return (success body or failure-audit, same as today). Prompt writes are best-effort: a failed prompt write must not abort the provider call. Persist stays in core; provider I/O stays in external. Latest-per-task and agent story remain RESPONSE-gated. Point at `canonical_refs` — do not paste large code.

## When not to use

- Storage-off calls (`store_agent_data=False`, bare `run_adhoc`).
- Writing timesheets before the provider returns.
- Treating a prompt-only interrupted batch as latest story / latest-per-task.
- Aborting the provider call because prompt persist failed.
- Adding a new table or block type.
- UI for prompt-only batches.

## Notes

Implementation must not depend on this catalog id until `status: approved` (AUTHORING). This child lands the file as proposed and implements the sequencing invariant; Archie sets approved later.
