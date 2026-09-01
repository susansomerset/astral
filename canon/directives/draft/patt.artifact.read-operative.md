---
id: patt.artifact.read-operative
kind: pattern
scope: [src/data/database.py, src/core/consult.py, src/core/tracker.py]
point: >
  Fetch the exact artifact row pinned at generation time — by id or by entity scope plus type.
---

# Abstract

An **operative read** returns the artifact body that was **current when some downstream action ran** — typically referenced by **`artifact_id`** stored on a grade, analysis record, or job_data pin field. It replaces "read this key from the entity's `*_data` JSON blob" for explainability paths. Inputs: pinned `artifact_id`, or `(entity_type, entity_id, candidate_id, artifact_type)` when resolving a known operative row without a pin.

# Arc

1. **Before** — A consumer holds an `artifact_id` pin from an earlier write or grade, or needs the operative row that was current at a recorded timestamp (prefer pin when available).
2. **During** — Direct table fetch by primary key or by scoped query; deserialize `artifact_data`. No coat-check, no lazy hydration from blob siblings.
3. **After** — Caller uses body for display, re-grade comparison, or Contact answer grounded in the pinned version.

# Applications

1. Explaining why a grade scored as it did (body at scoring time).
2. Rendering analysis upshot tied to stored pins in job entity metadata.
3. Contact tasks that must answer about content **as it was**, not the latest edit.

# Exceptions

1. **UI edit surfaces** — Use read-current, not operative read, unless showing historical diff.
2. **Missing pin** — Do not fall back to blob or coat-check; surface missing-data through component/state ingestion (see no-coat-check).

# Implementation

1. Primary path: load row by **`artifact_id`** when pin present.
2. Secondary path: query artifacts table with entity_type, entity_id, artifact_type, and `current=1` **only** when reproducing a write-time snapshot without a stored pin — prefer storing pins at write time instead.
3. Pass **candidate_id** when the catalog entry is candidate-scoped.
4. agent_data string pins in legacy blobs resolve through agent_data RESPONSE lookup first, then replicate to operative artifacts on migration — operative read does not re-parse agent markup at runtime for new code.
5. Partially replaces `get_<entity>_data` dotted-path reads for **pinned** content only.

# OPEN QUESTIONS / DECISIONS

1. Timestamp-based operative read without pin — avoid for new code; pins are SoT for explainability.
2. Job vs candidate entity_id when both apply — follow catalog primary entity for the key.
