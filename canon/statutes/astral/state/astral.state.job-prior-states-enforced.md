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
approved_at: "2026-09-27"
---

# Statement

Job transitions enforce `JOB_STATES.prior_states` via tracker — raising if the current state is not allowed to enter the target.

**Skipped-job operator edit carve-out (AST-1809 / AST-1811):** exactly one caller may skip the prior_states check — `persist_skipped_job_edits` in `src/core/tracker.py`, which calls `transition_job_state(..., enforce_prior_states=False)` only when the job's current state is in `SKIPPED_STATES` and the target is a `JOB_STATES` key (not an implicit `{base}_RETRY`, not a runtime dispatch-hop label). The hop still goes through `transition_job_state` (registry check, `state_history`, `state_changed_at`). Every other caller uses the default `enforce_prior_states=True`; passing `False` anywhere else is a violation.

## Rationale

Illegal jumps corrupt the job pipeline and dispatch eligibility.

## Examples

### Conforming

- `transition_job_state` raises `ValueError` when prior_states are violated.
- `persist_skipped_job_edits` on a job in `SKIPPED_STATES` moves it to any `JOB_STATES` key via `transition_job_state(..., enforce_prior_states=False)` (the carve-out above).

### Violating

- A shortcut UPDATE sets job state without prior_states checks.
- Any caller other than `persist_skipped_job_edits` passes `enforce_prior_states=False`, or the skipped-edit path accepts a target that is not a `JOB_STATES` key.
