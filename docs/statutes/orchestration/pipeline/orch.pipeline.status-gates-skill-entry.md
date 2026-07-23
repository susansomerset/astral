---
id: orch.pipeline.status-gates-skill-entry
title: Status gates skill entry
tier: universal
checkable: judgment
status: active
applies_when:
  layers: []
  paths: []
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_TEAM_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Enter each pipeline skill only from its listed Linear status (e.g. Todo→plan-child, Plan Approved→build-child, Tests Ready→test-child).

## Rationale

Status gates keep handoffs ordered and prevent skipped stages.

## Examples

### Conforming

- build-child refuses a ticket still in Plan Ready.

### Violating

- Engineer runs build-child while status is still Todo.
