---
id: astral.ui.single-gunicorn-worker
title: Single gunicorn worker
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["ui", "scripts", "utils"]
  paths: ["scripts/**", "src/utils/config.py", "src/ui/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Production uses a single gunicorn worker because the in-process dispatch scheduler runs per-worker.

## Rationale

Multiple workers duplicate schedulers and corrupt in-process thread registries.

## Examples

### Conforming

- `RAILWAY_CONFIG` workers set to 1 for production start.

### Violating

- Ops bumps gunicorn workers to 4 without moving the scheduler out-of-process.
