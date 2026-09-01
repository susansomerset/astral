---
id: patt.artifact.read-current
kind: pattern
scope: [src/data/database.py, src/ui/api, src/core/tracker.py]
point: >
  Return the current artifacts-table body for edit and live display — never stale blob copies.
---

# Abstract

A **current read** returns the **`current=1`** artifact row for a catalog key and scope: artifact type, **candidate_id**, and **entity_id** (when entity is candidate, entity_id equals candidate_id). This is the only supported path for UI editors and for agents that need the latest operator-approved body before a new write.

# Arc

1. **Before** — UI or API opens an edit surface, or a turn assembles prompt content that must reflect latest saved operator data.
2. **During** — `get_current_artifact(entity_type, entity_id, artifact_type)` (or scoped equivalent) returns deserialized body or empty when no row exists.
3. **After** — User or agent edits; save flows through write-operative. Display layers must not cache blob copies that bypass this read on save boundaries.

# Applications

1. Artifact editor tabs loading draft content for human revision.
2. Contact Estelle surgical fetch after candidate-scoped cache freshen on conversation start.
3. Batch steps that need latest rubric or resume structure before generation (when catalog says current, not pinned).

# Exceptions

1. **Historical / explainability views** — read-operative with pin, not read-current.
2. **Content not yet migrated to artifacts** — tracked as debt; do not add new blob readers. Ingestion components populate first operative row instead of coat-check.

# Implementation

1. API handlers: read-current on GET, write-operative on POST/PUT for the same key.
2. Candidate-scoped cache (Contact): freshen candidate artifact subset on conversation start; fetch by id/key surgically — not full-table preload.
3. Missing current row returns empty shape per catalog contract; **no** lazy fetch from `*_data` blob in new code.
4. Frontend receives already-resolved bodies from API — server performs read-current, not client-side blob traversal.

# OPEN QUESTIONS / DECISIONS

1. Cache invalidation events on write-operative — component-owned; default invalidate candidate scope for touched keys.
2. Read-through from legacy blob during migration window — migration tickets only, not runtime pattern.
