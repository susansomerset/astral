---
id: astral.dispatch.seed-auto-false
title: Seeded dispatch tasks are auto=false
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/dispatcher.py", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-1098-seed-gaze-email-click-statute-seed-auto-false.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Product seed/provision paths that insert or reconcile `dispatch_task` rows must leave `auto_mode` false (CLICK). Operators may turn AUTO on later via Task Dispatcher; seed paths must not write Auto true.

## Rationale

AUTO-true seeds (e.g. shared `gaze_email`) cause every-tick scheduler claims; failures then drown deploy logs. Seed law is CLICK; AUTO is an operator choice after seed.

## Examples

### Conforming

- `GAZE_EMAIL_CONFIG["auto_mode"]` is false; `ensure_gaze_email_dispatch_task` inserts and reconciles the shared null-candidate row as CLICK.
- Meteorite and candidate-stage seed catalogs seed `auto_mode` false.

### Violating

- A config or ensure path inserts a new `dispatch_task` with `auto_mode` true.
- Provision skips correcting a shared bad-seed AUTO-on `gaze_email` row.

## Notes

Admin create/PATCH may still set AUTO true after seed (not a seed path). Does not require rewriting every historical row beyond shared `gaze_email` reconcile. Archie approved id on parent AST-1093 (2026-07-31).
