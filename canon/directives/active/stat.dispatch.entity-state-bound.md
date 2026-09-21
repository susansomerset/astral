---
id: astral.dispatch.entity-state-bound
title: dispatch_task entity_type and trigger_state are real and matching
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["data", "core", "ui"]
  paths: ["src/data/database.py", "src/core/dispatcher.py", "src/ui/api/api_admin.py", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs: []
supersedes: null
superseded_by: null
approved_by: Susan
approved_at: "2026-09-20"
---

# Statement

Every `dispatch_task` row's `entity_type` is a real `ENTITY_TYPES` member, its `trigger_state` is a real state in that entity type's own registry, and that pair is the thing the entity row is actually claimed and dispatched by. All dispatch_task data has a direct candidate_id field, and when the entity_type is `candidate` then the trigger_state is a candidate trigger state.  

# Rationale

`entity_type`/`trigger_state` are read by every claim helper (`dispatch_claim_states`, `count_eligible_for_dispatch_task`) as the live description of how a row is claimed. If a row can carry a valid-looking pair that its own runner doesn't claim by, the field lies to the next person who reads it.

## Examples



### Conforming

- `qualify_meteorite`: `entity_type="meteorite"`, `trigger_state="METEORITE_NEW"` — both real, both what `count_eligible_for_dispatch_task` claims against.
- A candidate_id-bound poller task_key: `entity_type=None`, `trigger_state=None`, set only by its own catalog default.



### Violating

- A row carries `entity_type`/`trigger_state` that pass registry validation but that the row's runner never reads to claim.
- A save path lets a caller-supplied `entity_type`/`trigger_state` override a task_key's catalog default instead of the catalog winning.

