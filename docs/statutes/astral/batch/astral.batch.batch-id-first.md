---
id: astral.batch.batch-id-first
title: Batch claim APIs take batch_id first
tier: scoped
checkable: ci
status: active
applies_when:
  layers: ["data", "core"]
  paths: ["src/data/**", "src/core/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-22"
---

# Statement

Entity batch helpers use claim / get / clear with `batch_id` as the first parameter (ASTRAL_CODE_RULES §2.4). New batch APIs follow that signature order; callers pass the golden-ticket `batch_id` through claim → process → release.

## Rationale

`batch_id` ties row locks, agent_data, ledger, and timesheets. Inconsistent parameter order invites silent misuse and breaks dispatcher bookkeeping. Flagged `checkable: ci` as a future signature/lint candidate — not implemented in this ticket.

## Examples

### Conforming

- `claim_job_batch(batch_id, state, limit, …)` then `get_job_batch(batch_id)` then `clear_job_batch(batch_id)`.

### Violating

- A new `claim_company_batch(state, limit, batch_id)` that puts `batch_id` last “because state is more important.”
