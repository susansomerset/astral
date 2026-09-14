---
id: astral.seed.archie-catalog-wins
title: Archie seed catalogs win over live DB edits
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/dispatcher.py", "src/utils/config.py", "data/admin/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-771-seed-audit.md
  - docs/features/foundation/ast-1456-do-not-overwrite-dispatch-task.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Archie-named seed catalogs in the codebase are authoritative for their row shapes. On boot (or explicit provision), missing catalog rows are ensured — **except for `dispatch_task`**.

**`dispatch_task` carve-out (AST-1456 / AST-1496):** Catalogs such as `METEORITE_DISPATCH_TASKS`, `SEED_CONFIG` keys `dispatch_task-*`, and related mailbox/fetch catalog literals are **not** authoritative for live row presence. Boot and scheduler-start provision must **not** ensure or re-insert missing `dispatch_task` catalog rows. Lasting `dispatch_task` content changes are operator Manage Dispatch and/or SQL posted in Linear for Susan — not catalog ensure. Catalog SQL/shape text may remain in-repo as Linear copy-paste / documentation only.

For other Archie-named seed catalogs still in scope (non-`dispatch_task`), lasting content changes are made by editing and committing the catalog (or `data/admin/*.json`), not by relying on live DB edits alone.

## Rationale

Seed changes for non-`dispatch_task` catalogs land in git; the DB is a projection. For `dispatch_task`, operator-curated schedule rows must survive restart in every environment — auto overwrite from catalogs is forbidden (AST-1456).

## Examples

### Conforming

- Operator deletes or edits a `dispatch_task` row in Scheduled Actions; it stays as curated across restart (no catalog re-insert).
- When new `dispatch_task` rows are needed, copy catalog SQL/shape text into a Linear comment for Susan to run after restart.
- Change a non-`dispatch_task` catalog field in `config.py` or repo JSON and commit; provision projects the new shape.

### Violating

- Boot or `start_scheduler` re-inserts deleted meteorite / `meteorite_email` / `fetch_email` (or any) `dispatch_task` rows from a Python/`SEED_CONFIG` catalog.
- Treat a Scheduled Actions edit to a `dispatch_task` row as temporary because “the catalog will win on next boot.”
- Treat a Scheduled Actions edit to a non-`dispatch_task` catalog row as permanent with no config or JSON commit.
- Stop ensuring a named **non-`dispatch_task`** catalog without Archie retire of that catalog.
