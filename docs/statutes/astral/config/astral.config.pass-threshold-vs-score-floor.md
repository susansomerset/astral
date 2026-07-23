---
id: astral.config.pass-threshold-vs-score-floor
title: pass_threshold vs score_floor
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

`pass_threshold` (TASK_CONFIG) decides pass vs fail from model output after a run. `score_floor` on `dispatch_task` rows gates dispatch eligibility only. Neither replaces the other.

## Rationale

Mixing grading math with dispatch gating breaks consult scoring and eligibility in opposite directions.

## Examples

### Conforming

- Dispatcher filters with `score_floor`; `render_verdict` uses `pass_threshold`.

### Violating

- Dispatch eligibility reads `pass_threshold` instead of the row's `score_floor`.
