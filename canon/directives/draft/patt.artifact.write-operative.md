---
id: patt.artifact.write-operative
kind: pattern
scope: [src/data/database.py, src/core/tracker.py, src/core/candidate.py]
point: >
  Persist operator bodies in artifacts with agent_task-style current rotation and return the row id — skip invoke when body is identical to current.
---

# Abstract

An **operative write** stores (or replaces) the current version of an artifact body for a specific entity. When the validated body **differs** from the current row (or no current row exists), the write retires the prior `current=1` row, inserts a new UUID row with `current=1`, and returns **`artifact_id`** for pins. When the body is **identical** to the current row's `artifact_data`, the entity wrapper returns the existing `artifact_uuid` without calling `save_artifact` — no retire+insert and **not** an in-place UPDATE. Logical scope is **artifact type + entity_id + candidate_id** (candidate_id repeats entity_id when the entity is the candidate).

# Arc

1. **Before** — Caller holds validated body content (UI save, agent RESPONSE replication, batch land). Entity row exists; catalog key is registered.
2. **During** — Entity wrapper validates, then compares to read-current. If `artifact_data == body`, return existing pin (no data-layer write). Else `save_artifact(entity_type, entity_id, artifact_type, body)`: set prior current row to `current=0`, insert new row `current=1`. Grades and analysis records store returned `artifact_id` when explainability is required.
3. **After** — Consumers that need the body *as of that moment* use read-operative with the pin; editors use read-current for the latest.

# Applications

1. UI save from an artifact editor (after read-current loaded the draft).
2. Replicating agent_data RESPONSE into the first operative artifact version for a key.
3. Batch or consult land steps that finalize editable operator content.

# Exceptions

1. **Non-versioned metadata** on entity rows (state, timestamps) — not artifact writes.
2. **agent_data-only pins** — String pins in legacy blobs remain until migration; new work writes operative rows per this pattern.

# Implementation

1. **Invoke** — Call `save_artifact(entity_type, entity_id, artifact_type, body)` in the data layer when the body is new or changed; never UPDATE artifact rows in place.
2. **Scope** — Pass `candidate_id` when the catalog marks the key candidate-scoped (job/company keys still carry owning candidate).
3. **Validate** — Caller checks body shape against catalog contract before invoke; skip write when empty or invalid.
4. **Identical no-op** — Entity wrapper (`save_candidate_data` str-path, job equivalent when adopted): after validate, `get_current_artifact` (or scoped read-current). If a current row exists and `current_row["artifact_data"] == body` (Python `==` on deserialized body vs validated blob), return `current_row["artifact_uuid"]` without calling `save_artifact`. No retire+insert; not an in-place UPDATE. First save (no current row) or changed body falls through to invoke.
5. **Version** — On invoke, data layer sets prior `current=1` row to `current=0`, inserts new UUID row with `current=1`.
6. **Pin** — Persist returned `artifact_id` on grades, analysis upshots, or dispatch metadata when downstream explainability is required.
7. **Replicate** — After agent_data RESPONSE land, call write-operative to create the first operative row; do not leave new keys as agent_data-only pins.

# Examples

Data-layer retire+insert when body is new or changed (returns new `artifact_uuid` / pin):

```python
# data layer — blind retire-by-key + insert; returns new artifact_uuid
# prior current=1 rows for the natural key → current=0; new row current=1
new_uuid = database.save_artifact(
    entity_type,   # e.g. "candidate"
    entity_id,     # candidate_id when entity is candidate
    artifact_type, # leaf, e.g. "base_resume"
    body,          # validated artifact_data
)
# pin new_uuid on grades / analysis when explainability applies
```

Entity-owned operative path (`src/core/candidate.py`) — validates via `ARTIFACT_CONFIG` + `BUILD_CONFIG["artifact_shapes"]`, identical-to-current no-op, else delegates to `database.save_artifact`:

```python
# returns artifact_uuid (existing pin on identical no-op, new pin after insert), or raises
new_uuid = save_candidate_data(
    candidate_id,
    "candidate.artifacts.base_resume",
    body,
)
```

Identical re-save (entity wrapper — no data-layer write):

```python
current_row = database.get_current_artifact(
    entry["entity_type"], candidate_id, artifact_type
)
if current_row is not None and current_row.get("artifact_data") == blob:
    return current_row.get("artifact_uuid")  # no save_artifact; not UPDATE
# else fall through to save_artifact retire+insert
```

Job-scoped operative writes use `tracker.save_job_artifact(astral_job_id, artifact_key, blob, …)` the same way (live on `origin/dev`) — not expanded here.

do not `UPDATE artifact SET artifact_data = …` (or any in-place body UPDATE) for operative writes; when the body changed, retire+insert via `save_artifact`; when identical to current, skip invoke at the entity wrapper.

# OPEN QUESTIONS / DECISIONS

1. Whether every write also mirrors a denormalized cache entry — default no; cache pattern is separate.
2. Concurrent writes on same key — SQLite transaction boundary in data layer; callers must not assume cross-process locking beyond DB.
3. Whether job/tracker operative paths adopt the identical-to-current gate — default defer per ticket scope; candidate entity wrapper is the reference implementation.
