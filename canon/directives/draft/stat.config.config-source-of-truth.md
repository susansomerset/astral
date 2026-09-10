---
id: astral.config.config-source-of-truth
title: Config as source of truth
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

Behavior-driving non-secret values live as plain literals in organized blocks in `src/utils/config.py` — not scattered across modules or split with env lookups.

## Rationale

One config module is how agents and humans find limits, states, and task specs.

## Examples

### Conforming

- A new batch size default is added to the relevant config block.

### Violating

- A core module defines its own `DEFAULT_BATCH_SIZE = 25` constant used for dispatch.
