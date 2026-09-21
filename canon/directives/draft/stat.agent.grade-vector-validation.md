---
id: astral.agent.grade-vector-validation
title: Grade vector validation
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core"]
  paths: ["src/core/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

When TASK_CONFIG defines `vectors`, after schema validation `do_task` requires all expected vector names, rejects unexpected vectors, and requires grade values in `{A,B,C,D,F,X}`.

## Rationale

Catches AI creativity (e.g. A+) before invalid grades reach core scoring.

## Examples

### Conforming

- A response missing a required vector returns an error result from `do_task`.

### Violating

- Core accepts `"A+"` as a grade because schema JSON was loosely typed.
