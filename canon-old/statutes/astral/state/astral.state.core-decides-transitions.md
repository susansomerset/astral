---
id: astral.state.core-decides-transitions
title: Core decides state transitions
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data"]
  paths: ["src/core/**", "src/data/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

State transitions are decided by the core layer. Data/tracker accept the target state as a parameter and perform the update — they do not choose the next state.

## Rationale

Keeping transition policy in core prevents divergent next-state logic in the data layer.

## Examples

### Conforming

- `tracker.transition_job_state(job, target)` is called with a core-chosen target.

### Violating

- `database.py` inspects grades and picks `PASSED_DO` vs `FAILED_DO` itself.
