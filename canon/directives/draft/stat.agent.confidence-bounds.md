---
id: astral.agent.confidence-bounds
title: Confidence bounds
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/**", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Every graded row carries integer `confidence`: `1`–`5` for letter grades `A`–`F`, and `0` with `X`. At scoring, confidence `1` (including `F1`) is treated as no signal; multipliers live in `CONFIDENCE_MULTIPLIERS`.

## Rationale

Confidence is part of the scoring contract; inventing bounds per task breaks consult math.

## Examples

### Conforming

- Scoring uses `CONFIDENCE_MULTIPLIERS` from config for conf 2–5.

### Violating

- A consult step treats `F1` as a hard dealbreaker instead of no signal.
