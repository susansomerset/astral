---
id: astral.standards.logging-via-utils
title: Logging via utils
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "external", "utils", "ui"]
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

Backend logging goes through `src/utils/logging.py` (debug contract in CODE_RULES §1.5.1).

## Rationale

A single logging facade keeps batch correlation and debug contracts consistent.

## Examples

### Conforming

- Core uses `get_logger` from `src.utils.logging`.

### Violating

- A core module calls the stdlib `logging.getLogger` directly for product paths.
