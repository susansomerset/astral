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

Every graded row carries integer `confidence`: `1`–`5` for letter grades `A`–`F`, and `0` with `X`. One sanctioned exception at decode: the encoded grade decoder (`_decode_payload`, non-vet paths) normalises a letter segment written with confidence `0` (`{A-F}0`) to the same letter with confidence `1`, rather than failing the line. No other out-of-bounds confidence is coerced. At scoring, confidence `1` (including `F1`) is treated as no signal; multipliers live in `CONFIDENCE_MULTIPLIERS`.

## Rationale

Confidence is part of the scoring contract; inventing bounds per task breaks consult math.

## Examples

### Conforming

- Scoring uses `CONFIDENCE_MULTIPLIERS` from config for conf 2–5.
- `_decode_payload` turns encoded `CFC0` into `{"grade": "C", "confidence": 1}`; the row scores as no signal and the line is not a decode failure.

### Violating

- A consult step treats `F1` as a hard dealbreaker instead of no signal.
