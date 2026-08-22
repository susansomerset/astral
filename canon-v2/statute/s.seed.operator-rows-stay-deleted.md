---
id: astral.seed.operator-rows-stay-deleted
title: Non-catalog dispatch rows stay deleted
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "utils"]
  paths: ["src/core/dispatcher.py", "src/data/**", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-771-seed-audit.md
  - docs/features/roster/ast-745-stop-dispatch-retry-auto-seed-and-startup-db-inventory.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

`dispatch_task` rows that are not members of an Archie-named seed catalog are operator-owned. If the operator deletes them, product code must not re-insert them on restart or schema ensure.

## Rationale

Resurrected schedule rows undo Admin intent and surprise staging.

## Examples

### Conforming

- Operator deletes a hand-built `qualify_job_listings@NEW` row; it stays gone after reboot.

### Violating

- Startup rebuilds a full pipeline seed for every candidate, or re-inserts deleted non-catalog retry companions.

## Notes

Catalog membership is the bright line with `astral.seed.archie-catalog-wins`. Form defaults (`dispatch_task_admin_defaults`) are not inserts.
