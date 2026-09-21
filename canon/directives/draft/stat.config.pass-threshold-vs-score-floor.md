---
id: astral.config.pass-threshold-vs-score-floor
title: pass_threshold vs score_floor
tier: scoped
checkable: judgment
status: retired
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

**Retired (AST-1279).** Former rule that split `TASK_CONFIG.pass_threshold` (post-run grading) from `dispatch_task.score_floor` (claim gating only) is withdrawn. Authority for the numeric floor is pattern `pattern.dispatch.score-floor` — sole floor on the candidate’s `dispatch_task` row for both eligibility and scored soft-fail. Do not resurrect `pass_threshold` on `TASK_CONFIG`.

## Rationale

Kept for citation history only. Active consumers must not treat this file as binding.

## Examples

### Conforming

- (retired — see `pattern.dispatch.score-floor`)

### Violating

- (retired — see `pattern.dispatch.score-floor`)
