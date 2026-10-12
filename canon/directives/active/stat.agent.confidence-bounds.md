---
id: stat.agent.confidence-bounds
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
approved_at: "2026-10-12"
---

# Statement

Every graded row carries integer `confidence`: `1`–`5` for letter grades `A`–`F`, and `0` with `X`. `X` is always no signal, whether or not the vector's rubric has an `X` row; rubric hydrate never fails on `X` (it uses the rubric's `X` text when present, else a fixed no-signal reason). One sanctioned exception at hydrate: the structured grade hydrate (`src/core/grade_schema.py`, non-vet paths) rewrites a letter grade returned with confidence `0` (`{A-F}0`) to `X0`, rather than failing the entity. No other out-of-bounds confidence is coerced. At scoring, confidence `1` (including `F1`) is treated as no signal; multipliers live in `CONFIDENCE_MULTIPLIERS`.

## Rationale

Confidence is part of the scoring contract; inventing bounds per task breaks consult math.

## Examples

### Conforming

- Scoring uses `CONFIDENCE_MULTIPLIERS` from config for conf 2–5.
- The structured grade hydrate turns tool input `"CF": {"grade": "C", "confidence": 0}` into `{"grade": "X", "confidence": 0}`; the row is no signal and the entity is not a decode failure.

### Violating

- A consult step treats `F1` as a hard dealbreaker instead of no signal.
- Hydrate raises on an `X` grade because the vector's rubric has no `X` row.
