---
id: astral.standards.public-then-helpers
title: Public functions then helpers
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Organize files with public functions first, then helpers. Do not scatter public and helper functions; group by responsibility with clear section comments.

## Rationale

Predictable file layout speeds review and keeps the public API obvious.

## Examples

### Conforming

- Module lists public entrypoints, then a Helpers section with private functions.

### Violating

- Public and private functions alternate randomly through a 800-line module.
