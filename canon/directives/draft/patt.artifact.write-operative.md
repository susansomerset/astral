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

1. Versioning matches **agent_task**: retire + insert, never in-place overwrite of historical rows.
2. Always pass **candidate_id** for candidate-scoped artifacts (Contact cache, Estelle context) even when `entity_id` is a job or company id.
3. Empty or invalid bodies must not create a current row (callers validate before write).
4. Return value is the new **`artifact_id`**; callers that need audit trails persist it on grades, analysis upshots, or dispatch metadata.
5. Writable shapes follow catalog contracts (JSON dict, structured sections); serialization lives in the data layer.

# OPEN QUESTIONS / DECISIONS

1. Whether every write also mirrors a denormalized cache entry — default no; cache pattern is separate.
2. Concurrent writes on same key — SQLite transaction boundary in data layer; callers must not assume cross-process locking beyond DB.
