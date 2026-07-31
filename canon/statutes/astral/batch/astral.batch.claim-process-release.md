---
id: astral.batch.claim-process-release
title: Claim process release
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data"]
  paths: ["src/core/**", "src/data/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Entity batches use claim → process → release with a `batch_id`. Do not select by state and process without batch locking.

## Rationale

Batch locking is the concurrency and audit spine for dispatch.

## Examples

### Conforming

- Dispatcher claims with `batch_id`, processes, then `clear_*_batch` in `finally`.

### Violating

- A runner `SELECT`s jobs by state and updates them with no claim/clear.
