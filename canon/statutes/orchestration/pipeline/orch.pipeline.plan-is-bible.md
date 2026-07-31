---
id: orch.pipeline.plan-is-bible
title: Plan is the bible
tier: universal
checkable: judgment
status: active
applies_when:
  layers: []
  paths: ["docs/features/**"]
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_TEAM_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-22"
---

# Statement

The ticket plan doc is binding for build, test, and resolve. Agents execute stages and steps as written — they do not skip, reorder, combine, expand, or improvise. Ambiguity, contradiction, or drift from the plan stops work and escalates; it is not fixed on the fly.

## Rationale

Pipeline agents share one execution contract. If the plan is optional, each stage reinvents scope and acceptance. Binding the plan keeps Joan validation, Betty manifests, and Radia review aligned to the same script.

## Examples

### Conforming

- Build-child follows Stage 2 file paths exactly and stops when a referenced helper is missing, commenting on the parent with proposed resolutions.

### Violating

- An engineer “improves” the plan mid-build by adding an undeclared module because it seemed cleaner.
