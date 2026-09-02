---
id: patt.artifact.write-operative
kind: pattern
scope: [src/data/database.py, src/core/tracker.py, src/core/candidate.py]
point: >
  Persist operator bodies in artifacts with agent_task-style current rotation and return the new row id.
---

# Abstract

An **operative write** stores (or replaces) the current version of an artifact body for a specific entity. The write retires the prior `current=1` row, inserts a new UUID row with `current=1`, and returns **`artifact_id`** for pins. Logical scope is **artifact type + entity_id + candidate_id** (candidate_id repeats entity_id when the entity is the candidate).

# Arc

1. **Before** — Caller holds validated body content (UI save, agent RESPONSE replication, batch land). Entity row exists; catalog key is registered.
2. **During** — `save_artifact(entity_type, entity_id, artifact_type, body)` (or equivalent data-layer API): set prior current row to `current=0`, insert new row `current=1` with serialized body. Grades and analysis records store returned `artifact_id` when explainability is required.
3. **After** — Consumers that need the body *as of that moment* use read-operative with the pin; editors use read-current for the latest.

# Applications

1. UI save from an artifact editor (after read-current loaded the draft).
2. Replicating agent_data RESPONSE into the first operative artifact version for a key.
3. Batch or consult land steps that finalize editable operator content.

# Exceptions

1. **Non-versioned metadata** on entity rows (state, timestamps) — not artifact writes.
2. **agent_data-only pins** — String pins in legacy blobs remain until migration; new work writes operative rows per this pattern.

# Implementation

1. **Invoke** — Call `save_artifact(entity_type, entity_id, artifact_type, body)` in the data layer; never UPDATE artifact rows in place.
2. **Scope** — Pass `candidate_id` when the catalog marks the key candidate-scoped (job/company keys still carry owning candidate).
3. **Validate** — Caller checks body shape against catalog contract before invoke; skip write when empty or invalid.
4. **Version** — Data layer sets prior `current=1` row to `current=0`, inserts new UUID row with `current=1`.
5. **Pin** — Persist returned `artifact_id` on grades, analysis upshots, or dispatch metadata when downstream explainability is required.
6. **Replicate** — After agent_data RESPONSE land, call write-operative to create the first operative row; do not leave new keys as agent_data-only pins.

# OPEN QUESTIONS / DECISIONS

1. Whether every write also mirrors a denormalized cache entry — default no; cache pattern is separate.
2. Concurrent writes on same key — SQLite transaction boundary in data layer; callers must not assume cross-process locking beyond DB.
