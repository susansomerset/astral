---
id: astral.standards.data-raises-caller-logs
title: Data raises; caller logs
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["data", "core", "ui"]
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

Data layer raises exceptions and does not log. Core raises domain exceptions; the dispatcher catches and logs at batch level. UI API returns JSON error responses.

## Rationale

Logging ownership at the right layer prevents double-logging and silent swallows in data.

## Examples

### Conforming

- `database.py` raises on constraint failure; dispatcher logs the batch error.

### Violating

- A data-layer helper catches and `print`s / logs errors instead of raising.
