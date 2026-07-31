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
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Archie-named seed catalogs in the codebase are authoritative for their row shapes. On boot (or explicit provision), missing catalog rows are ensured. Lasting content changes are made by editing and committing the catalog (or `data/admin/*.json`), not by relying on live DB edits alone.

## Rationale

Seed changes land in git; the DB is a projection. Operator deletes of catalog rows are temporary until the next ensure.

## Examples

### Conforming

- Delete one meteorite pair in Scheduled Actions; next boot re-inserts it from `METEORITE_DISPATCH_TASKS`.
- Change a catalog field in `config.py` or repo JSON and commit; provision projects the new shape.

### Violating

- Treat a Scheduled Actions edit to a catalog row as permanent with no config or JSON commit.
- Stop ensuring a named catalog without Archie retire of that catalog.
