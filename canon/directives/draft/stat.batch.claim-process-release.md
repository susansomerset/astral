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
approved_at: "2026-08-07"
---

# Statement

Every `ENTITY_TYPES` member used as a dispatch claim queue (`candidate`, `company`, `job`) must use claim → process → release with a row `batch_id` lock and **pool** claim parity: claim up to `limit` unclaimed rows in the claimable state set under one `batch_id`, process only those rows, and clear the lock in `finally` (and on every early-exit path **on which rows were actually claimed** — a zero-row claim needs no release). Do not select by state or single-ctx and process without batch locking. Silent per-entity carve-outs that skip pool claim for any `ENTITY_TYPES` claim queue are review defects unless Archie has an explicit approved exception statute.

## Rationale

Batch locking is the concurrency and audit spine for dispatch. Candidate is an `ENTITY_TYPES` claim queue peer of job and company — not a single-row unlocked special case.

## Examples

### Conforming

- Dispatcher claims candidates via `get_new_candidate_batch` / `claim_candidate_batch`, processes claimed rows, then `clear_candidate_batch` in `finally` (same shape as job/company).
- Job or company claim → process → `clear_*_batch` in `finally`.

### Violating

- A candidate dispatch branch sets `entities = [ctx]` when the ctx state is claimable and never locks `candidate.batch_id`.
- A runner `SELECT`s jobs (or candidates) by state and updates them with no claim/clear.
- Docs or statutes bless a candidate-only unlocked / non-pool claim path.

## Notes

Non-`ENTITY_TYPES` pollers (e.g. `gaze_email`, meteorite mailbox shells) are not dispatch claim queues and stay outside this statute’s claim-lock duty. Do not use that exception to skip candidate pool claim.

A zero-row claim locks no rows; company's empty-batch early exit without `clear_company_batch` is known-conforming under this Statement.
