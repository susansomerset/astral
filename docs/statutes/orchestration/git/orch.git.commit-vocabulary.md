---
id: orch.git.commit-vocabulary
title: Commit vocabulary
tier: universal
checkable: judgment
status: active
applies_when:
  layers: []
  paths: []
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_GIT_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Use only the ten named commit types (`plan`, `code`, `park-wip`, `merge-resume`, `merge-tests`, `test`, `docs`, `resolve`, `merge-child`, `finish-up`) with their listed owners. Do not use deprecated `feat()`, `fix()`, or `push-tests()` on new work.

## Rationale

Shared vocabulary makes sub-log validation and rollups mechanical.

## Examples

### Conforming

- Build stage commits `code(AST-921): …`.

### Violating

- New work lands as `feat(ast-921): …`.
