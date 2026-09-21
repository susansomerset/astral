---
id: astral.entity.required-metadata
title: every entity table carries the identical batch/state metadata set
tier: scoped
checkable: mechanical
status: active
applies_when:
  layers: ["data"]
  paths: ["src/data/database.py"]
  change_types: ["add", "modify"]
source_docs: []
supersedes: null
superseded_by: null
approved_by: Susan
approved_at: "2026-09-20"
---

# Statement

Every entity table (`job`, `company`, `candidate`, `meteorite`, and any future one) carries the identical column set: `state`, `state_history`, `state_changed_at`, `batch_id`, `batch_created_at`, `created_at`, `updated_at`. Same names, same set, no entity table may omit or rename a member of it.

## Rationale

Any entity may be claimed by a dispatch_task batch. `patt.entity.batch-processing`'s claim/release/audit cycle reads and writes these columns by that exact name on every entity it touches. An entity missing one, or spelling one differently, can't be claimed, released, or audited the same way as its siblings — and the gap stays invisible until the one run that needs it.

## Examples



### Conforming

- `entity data definition has`: `state`, `state_history`, `state_changed_at`, `batch_id`, `batch_created_at`, `created_at`, `updated_at` — full set, identical names.



### Violating

- `similar-not-identical field names`
- `missing field names`
- `mutated fields for additional purposes.`

