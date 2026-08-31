---
id: astral.batch.entity-agent-responses-latest-only
title: Entity latest agent refs via agent_data.entity_id
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
approved_at: "2026-07-27"
---

# Statement

After each `do_task` RESPONSE write when an entity index is known, tag that `agent_data` RESPONSE row with `entity_id`. Latest-per-`task_key` refs are read via `list_entity_latest_agent_refs(entity_type, entity_id)`. Historical blocks remain in `agent_data`. Do not store latest-only refs on entity-row JSON `agent_responses` columns.

## Rationale

Entity rows stay free of confusing mirror columns; full prompt/response history stays queryable by batch; hop hydration and agent_story use one list API.

## Examples

### Conforming

- `_store_response_block` / `save_agent_data` set `entity_id` on RESPONSE when `index` is known.
- Hop / `get_entity_agent_story` call `list_entity_latest_agent_refs`.

### Violating

- Upserting latest-only refs onto entity JSON `agent_responses` columns after column retirement.
- Leaving RESPONSE rows without `entity_id` when an entity index was available.
