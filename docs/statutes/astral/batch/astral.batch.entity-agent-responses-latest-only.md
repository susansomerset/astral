---
id: astral.batch.entity-agent-responses-latest-only
title: Entity agent_responses latest-only
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
approved_at: "2026-07-23"
---

# Statement

After each successful `do_task`, upsert a lightweight `agent_responses` reference by `task_key` (latest wins). Historical blocks remain in `agent_data`.

## Rationale

Entity rows stay small while full prompt/response history stays queryable by batch.

## Examples

### Conforming

- `agent.py` upserts the latest entry for `task_key` after success.

### Violating

- Entity JSON appends every historical response blob inline forever.
