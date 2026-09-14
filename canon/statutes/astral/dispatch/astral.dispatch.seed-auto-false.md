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
  - docs/features/foundation/ast-1456-do-not-overwrite-dispatch-task.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

AST-1456 / AST-1496 ban boot and scheduler-start provision of `dispatch_task` rows. Catalogs that document desired shapes (`METEORITE_DISPATCH_TASKS`, mailbox/fetch config, `SEED_CONFIG` `dispatch_task-*`) must still list `auto_mode` false (CLICK).

If any remaining or future seed/provision path is Archie-approved to insert or reconcile a `dispatch_task` row, it must leave `auto_mode` false. Operators may turn AUTO on later via Task Dispatcher; seed paths must not write Auto true. No automatic path may insert `dispatch_task` at all under the ban.

## Rationale

AUTO-true seeds cause every-tick scheduler claims; failures then drown deploy logs. Seed law is CLICK; AUTO is an operator choice after create. The boot ban removes silent inserts entirely for `dispatch_task`.

## Examples

### Conforming

- Config catalog literals document `auto_mode` false for meteorite / mailbox / fetch shapes.
- Admin create/PATCH may set AUTO true after the row exists (not a seed path).
- No automatic boot path inserts any `dispatch_task` row.

### Violating

- A config or ensure path inserts a new `dispatch_task` with `auto_mode` true.
- Boot or scheduler-start provision re-inserts `dispatch_task` rows (regardless of `auto_mode`).

## Notes

Does not require rewriting every historical row. Schema DDL-only ensure and runtime bookkeeping are out of scope. Archie approved id on parent AST-1093 (2026-07-31); AST-1456 carve-out supersedes any reading that required live provision reconcile.
