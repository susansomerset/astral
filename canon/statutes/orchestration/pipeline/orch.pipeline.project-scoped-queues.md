---
id: orch.pipeline.project-scoped-queues
title: Project-scoped queues
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

Engineer plan/build/test/resolve queues filter to the session Linear project unless Susan passes an explicit ticket id.

## Rationale

Project scope prevents agents from grabbing unrelated program work.

## Examples

### Conforming

- `list_issues` for Plan Approved uses `project: Team Chuckles` for this session.

### Violating

- Queue mode silently builds tickets from another Linear project.
