---
id: patt.artifacts.traceability
kind: pattern
scope: [src/data/database.py, src/core/candidate.py, src/core/contact.py]
point: >
  Record which versioned agent + agent_task and which seed artifact ids produced a
  derived artifact; manual edits inherit originating task sources.
---

# Abstract

**Traceability** records the **generation circumstances** of a derived artifact
version: the **versioned `agent_id`**, the **versioned `agent_task_id`**
(`task_key_uuid`), and the **array of artifact ids** whose bodies seeded prompt
tokens for that write. Later **manual** edits (UI or Estelle) create a new
artifact version marked manual while **inheriting** those originating task
sources — so explainability can still name the generative lineage after human
revision. This pattern is **documentation only** until a dedicated implement
ticket lands; read-operative / write-operative do **not** persist seed ids by
themselves.

# Arc

1. **Before** — An agent (or craft chain) is about to write a derived operative
   artifact, holding the active agent row, agent_task row, and the current
   artifact ids used as prompt inputs.
2. **During** — Persist provenance beside the new artifact version (exact column
   / sidecar shape is implement-ticket work): versioned agent_id, versioned
   agent_task_id, seed `artifact_id[]`.
3. **After** — A UI or Estelle manual edit writes a new version via write-operative,
   marks the version as manual, and copies forward the inherited originating
   task sources (does not clear generative lineage).

# Applications

1. Explaining which prompt inputs seeded a job artifact build.
2. Contact answers that must cite generative lineage after a human touch-up.
3. Future grade/analysis explainability that needs seed pins beyond a single
   output pin.

# Exceptions

1. **This epic (AST-1571)** — Draft only; no product persist/wire.
2. **Read-operative / write-operative alone** — Pins identify a body; they do not
   replace the seed-id array documented here.
3. **Library blob fields** — Not a substitute for versioned provenance.

# Implementation

1. **Draft** — Land this file under `canon/directives/draft/`; cite from define /
   plan tickets; do not treat as approved runtime law until Archie promotes.
2. **Capture at generative write** — When an agent-produced operative write lands,
   record versioned `agent_id`, versioned `agent_task_id`, and the seed
   `artifact_id[]` that fed tokens (implement ticket).
3. **Manual edit inheritance** — UI / Estelle write-operative paths that create a
   new version after a human edit mark the version manual and copy inherited
   originating task sources forward (implement ticket).
4. **Consumers** — Prefer provenance records over reconstructing seeds from live
   current rows.
5. **Non-goal here** — No schema, no API field, no Contact/UI wire in AST-1584 /
   AST-1585.

# OPEN QUESTIONS / DECISIONS

1. Storage shape (columns on `artifacts` vs sidecar table) — deferred to the
   implement ticket Archie approves after this draft.
2. Whether every manual edit must require a non-empty inherited seed array when
   the prior version had none (legacy rows) — deferred.
