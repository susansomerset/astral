---
id: orch.roles.chuckles-never-ticket-assignee
title: Chuckles never ticket assignee
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

Chuckles coordinates (define/dispatch/merge/prep-uat/finish-up) but is never the Linear assignee on child implementation tickets.

## Rationale

Assignee must be the implementing engineer for accountability through resolve.

## Examples

### Conforming

- AST-921 assignee remains Ada through build/test/resolve.

### Violating

- Child ticket reassigned to Chuckles so he "owns" the build.
