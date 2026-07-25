---
id: pattern.batch.entity-claim-process-release
name: Entity claim / process / release
status: approved
proposed_in: AST-913
approved_by: Archie
approved_at: "2026-07-23"
canonical_refs:
  - path: src/data/database.py
    symbol: claim_job_batch
  - path: src/data/database.py
    symbol: clear_job_batch
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.4"
related_statutes:
  - astral.batch.claim-process-release
  - astral.batch.batch-id-first
  - astral.batch.batch-id-format
supersedes: null
superseded_by: null
---

# Problem

Dispatch and entity runners need a concurrency-safe way to select work, process it, and release the claim without racing other workers or losing auditability.

# Solution shape

Claim a batch with a `batch_id` (first parameter on claim/get/clear helpers), process only claimed rows, and clear the batch in `finally` (or equivalent release). Core decides transitions; data owns claim/clear. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- One-off admin scripts that intentionally bypass dispatch locking.
- Read-only queries that never mutate claimed rows.
- Non-entity work with no batch table.
