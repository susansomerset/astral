---
id: astral.seed.operator-rows-stay-deleted
title: Operator dispatch_task rows stay deleted
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
  - docs/features/foundation/ast-1456-do-not-overwrite-dispatch-task.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Under AST-1456, **all** live `dispatch_task` rows are operator-owned for presence and content. If the operator deletes them (including rows that match an Archie-named catalog shape), product code must not re-insert them on restart or schema ensure. Catalog membership does **not** license resurrection of `dispatch_task` rows.

## Rationale

Resurrected schedule rows undo Admin intent, surprise staging, and violate the no-auto-overwrite ban.

## Examples

### Conforming

- Operator deletes a hand-built `qualify_job_listings@NEW` row; it stays gone after reboot.
- Operator deletes a meteorite-catalog-shaped row; it stays gone after reboot (no `METEORITE_DISPATCH_TASKS` re-insert).

### Violating

- Startup or schema ensure re-inserts any deleted `dispatch_task` row — catalog-shaped or hand-built — including retry companions or meteorite pairs.

## Notes

Bright line with `astral.seed.archie-catalog-wins`: that statute’s `dispatch_task` carve-out bans boot/catalog ensure; this statute bans resurrection of every live schedule row. Form defaults (`dispatch_task_admin_defaults`) are not inserts. Schema DDL-only ensure and runtime bookkeeping (`last_run_at`, max_runs disable) are not content re-inserts.
