---
id: astral.standards.dry-and-focused-functions
title: DRY and focused functions
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "external", "utils", "ui", "scripts"]
  paths: ["src/**", "scripts/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Honor Don't Repeat Yourself: before adding code, consider the whole file and extract shared logic. Keep functions focused; extract complex logic into helpers.

## Rationale

Duplication multiplies bugs; oversized functions hide the unit of change.

## Examples

### Conforming

- Two call sites share one helper for identical claim formatting.

### Violating

- The same five-line state-transition block is copy-pasted into three functions in one file.
