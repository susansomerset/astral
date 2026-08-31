---
id: astral.standards.no-hardcoded-sets
title: No hardcoded sets or magic numbers
tier: scoped
checkable: ci
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

State lists, enums, and allowed value sets live in `src/utils/config.py`. Validate against config; do not define inline. Magic numbers use named constants from config or module-level constants with documented meaning.

## Rationale

Inline sets drift from the single source of truth and break dispatch/state machines silently.

## Examples

### Conforming

- A new job state is added only in `JOB_STATES` in config.py.

### Violating

- A core function hardcodes `("NEW", "WATCH")` instead of reading `COMPANY_STATES`.
