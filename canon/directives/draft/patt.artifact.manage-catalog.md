---
id: patt.artifact.manage-catalog
kind: pattern
scope: [src/utils/config.py, src/data/database.py]
point: >
  New artifact keys enter through catalog registration and a scoped implementation ticket — never ad hoc blob fields.
---

# Abstract

Every versioned content slot the platform reads or writes is an **artifact key** bound to an **entity type**. Keys are registered in the central catalog (code config), not discovered at runtime from JSON blobs. Adding a key is a deliberate engineering change: register, implement read-current + write-operative paths, wire consumers — then retire direct blob access for that content.

# Arc

1. **Before** — A use case needs durable, versioned, or UI-editable content for an entity. The planner names entity type, logical key path, and consumers (batch, UI, consult grade, Contact).
2. **During** — Engineer adds catalog entry (entity type, artifact type string, scope metadata). Implements `read-current` for edit surfaces and `write-operative` for persistence. Grades or analysis that must explain *which* body was used store an **operative pin** (`artifact_id`), not a blob snapshot.
3. **After** — All new reads for that content go through artifact APIs. Legacy blob paths are migration targets, not approved shortcuts.

# Applications

1. Ticket titled "Support `<entity>.artifacts.<new_key>`" — canonical shape for catalog work.
2. Moving UI-editable content out of `*_data` JSON into the artifacts table.
3. Introducing a new agent-produced body that grades or downstream steps must cite by id.

# Exceptions

1. **agent_data RESPONSE** — Ephemeral LLM output may land in agent_data first; operative artifact replication is a separate write (see write-operative). Catalog does not replace agent_data storage — it governs versioned operator bodies.
2. **Migration/backfill tickets** — May touch blobs directly under a dedicated migration scope; not a pattern exception for runtime code.

# Implementation

1. Catalog entry declares: entity type, artifact type identifier, which read/write patterns apply, and owning component for ingestion when content is missing.
2. Do **not** document keys inside pattern prose — only the registration *process* and ticket template.
3. Entity examples (candidate, job, company) are allowed; enumerating every registered key is not.
4. Config holds the authoritative key list; patterns describe how engineers extend that list safely.
5. New keys must have a test or manifest row proving read-current + write-operative round-trip before consumers switch.

# OPEN QUESTIONS / DECISIONS

1. Whether catalog metadata lives beside `ARTIFACT_CONFIG` or a dedicated registry module — implementation detail; process unchanged.
2. Cross-entity keys (same logical content visible on job and candidate) — resolve per ticket; catalog entry must name primary entity SoT.
