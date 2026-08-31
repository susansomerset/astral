---
id: astral.state.job-prior-states-enforced
title: Job prior_states enforced
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "utils"]
  paths: ["src/core/**", "src/data/**", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Job transitions enforce `JOB_STATES.prior_states` via tracker — raising if the current state is not allowed to enter the target.

## Rationale

Illegal jumps corrupt the job pipeline and dispatch eligibility.

## Examples

### Conforming

- `transition_job_state` raises `ValueError` when prior_states are violated.

### Violating

- A shortcut UPDATE sets job state without prior_states checks.
