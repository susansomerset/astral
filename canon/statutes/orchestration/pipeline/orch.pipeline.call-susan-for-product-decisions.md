---
id: orch.pipeline.call-susan-for-product-decisions
title: Call Susan for product decisions
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

Product, priority, and cross-feature contracts escalate with `@susan` in Linear. Do not invent missing decisions.

## Rationale

Architect ownership of product calls prevents agent improvisation on scope.

## Examples

### Conforming

- Agent stops and `@susan` when two features need a shared contract.

### Violating

- Agent picks a product behavior unilaterally and ships it.
