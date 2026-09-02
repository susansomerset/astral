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

1. **Before** — Product scope names a new versioned body (UI-editable, grade input, or agent output). Ticket states entity type, consumers, and whether grades must pin `artifact_id`.
2. **During** — Engineer registers the key in catalog config, wires read-current / write-operative (and read-operative pins where required), and removes new blob reads for that content in the same change.
3. **After** — Runtime code resolves the key only through artifact APIs; missing rows trigger ingestion states, not coat-check.

# Applications

1. Ticket titled "Support `<entity>.artifacts.<new_key>`" — canonical shape for catalog work.
2. Moving UI-editable content out of `*_data` JSON into the artifacts table.
3. Introducing a new agent-produced body that grades or downstream steps must cite by id.

# Exceptions

1. **agent_data RESPONSE** — Ephemeral LLM output may land in agent_data first; operative artifact replication is a separate write (see write-operative). Catalog does not replace agent_data storage — it governs versioned operator bodies.
2. **Migration/backfill tickets** — May touch blobs directly under a dedicated migration scope; not a pattern exception for runtime code.

# Implementation

1. **Register** — Add catalog metadata in config (entity type, artifact type string, candidate-scoped flag, body shape contract, owning component for ingestion). Config is the authoritative key list; this pattern does not enumerate keys.
2. **Read path** — UI/API GET handlers call read-current; batch/consult/Contact callers call read-current or read-operative per use case. No new `entity["*_data"]` reads for this key.
3. **Write path** — Saves and agent lands call write-operative; grades/analysis persist returned `artifact_id` when explainability applies.
4. **Ingestion** — When content may be absent at dispatch, wire a trigger state or contact handler to populate the first operative row (no-coat-check). Do not register coat-check fetchers for greenfield keys.
5. **Verify** — Component test or manifest row: empty → write-operative → read-current → read-operative pin round-trip before switching production consumers.
6. **Retire blob** — Same ticket removes or gates legacy blob writes for that content; migration tickets may backfill historical rows separately.

# OPEN QUESTIONS / DECISIONS

1. Whether catalog metadata lives beside `ARTIFACT_CONFIG` or a dedicated registry module — implementation detail; process unchanged.
2. Cross-entity keys (same logical content visible on job and candidate) — resolve per ticket; catalog entry must name primary entity SoT.
