---
id: astral.layers.scripts-exempt-from-layer-rules
title: Scripts exempt from layer rules
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["scripts"]
  paths: ["scripts/**"]
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

`scripts/` are exempt from layer import rules and may import any layer for one-off operations, builds, and deployment. They are not runtime product paths.

## Rationale

Build/deploy helpers need cross-layer access without weakening the runtime graph.

## Examples

### Conforming

- `scripts/start_server.py` reads config and launches gunicorn.

### Violating

- Treating a script module as a runtime import target from `src/ui`.
