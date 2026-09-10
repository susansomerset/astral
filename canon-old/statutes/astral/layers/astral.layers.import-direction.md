---
id: astral.layers.import-direction
title: Layer import direction
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-22"
---

# Statement

Imports obey ASTRAL_CODE_RULES §3.3 one-line-per-layer rules: ui → core + utils; core → data + external + utils; external → utils only; data → utils only; utils → utils only (except the documented `logging.py` late-import of `database` inside the DB log handler flush path).

## Rationale

Layer isolation keeps I/O in external, orchestration in core, and persistence in data. Cross-layer imports recreate the monolith the architecture was built to prevent.

## Examples

### Conforming

- `src/core/tracker.py` imports from `src.data`, `src.external`, and `src.utils` only.

### Violating

- `src/ui/api/api_jobs.py` imports a Playwright helper from `src.external` directly instead of going through core.
