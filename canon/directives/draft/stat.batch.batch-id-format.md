---
id: astral.batch.batch-id-format
title: batch_id format
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

`batch_id` format is `f"{task_key}-{uuid}"` (or the function-context prefix for non-dispatch calls).

## Rationale

Readable prefixes make foreign-key trails greppable across agent_data and ledgers.

## Examples

### Conforming

- `batch_id = f"{task_key}-{uuid4()}"` before claim.

### Violating

- A runner uses a bare UUID with no task_key prefix for a dispatch batch.
