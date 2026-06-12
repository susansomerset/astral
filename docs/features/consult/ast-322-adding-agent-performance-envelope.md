# AST-322 — Adding Agent Performance Envelope

<!-- linear-archive: AST-322 archived 2026-06-03 -->

## Linear archive (AST-322)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-322/adding-agent-performance-envelope  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

# Issue: Add response envelope to all agent calls

## Problem

Agent responses have no standard contract. A task like `find_job_site` can return `{"jobs": []}` — technically valid JSON, technically matching the schema — and the system treats it as success. There is no way for an agent to signal "I tried and couldn't do this" without the caller second-guessing the empty result.

This also means:

* Silent failures are invisible in logs and cost reports
* Adding a universal field (e.g. `confidence`, `model_note`) requires touching every individual `response_schema`
* Prompt instructions about failure handling are inconsistent across tasks — some tasks mention it, some don't

## What we want

Every agent response, regardless of task, should include:

```json
{
  "status": "success | failure",
  "failure_note": "<reason, if failure>",
  ...task-specific fields...
}
```

The `{$RESPONSE_SCHEMA}` token in every prompt should render this envelope automatically — agents should always see the contract. Validation should check `status` first and surface `failure_note` as a clean error before it ever touches task fields.

## Acceptance criteria

* `BASE_SCHEMA` constant in `config.py` defines the universal envelope fields (`status`, `failure_note`)
* `stringify_response_schema(task_key)` merges `BASE_SCHEMA` into the rendered example — envelope fields appear first in every prompt
* `_validate_response_schema` in `anthropic.py` imports and merges `BASE_SCHEMA`, short-circuits with a clean error message when `status == "failure"`
* No individual `response_schema` entries in `TASK_CONFIG` need to change
* Adding a new universal field in future = one line in `BASE_SCHEMA`, zero other changes

## Implementation notes

Landed in two commits on `chuckles/ast-293-in-process-dispatch-scheduler`, merged to `main` via PR #107 (Mar 11 2026):

* `97aa64d` — initial `BASE_SCHEMA` + flat envelope in schema/validation
* `8fadad1` — follow-up: nested the envelope into `agent_performance` / `agent_payload` structure; `do_task` unwraps `agent_payload` so all downstream code sees flat task fields unchanged; tolerates flat responses from agents that haven't adopted the envelope yet

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
