---
id: pattern.batch.entity-agent-responses
name: Entity latest agent refs (agent_data.entity_id)
status: approved
proposed_in: AST-984
approved_by: Archie
approved_at: "2026-07-27"
canonical_refs:
  - path: src/core/agent.py
    symbol: _store_response_block
  - path: src/data/database.py
    symbol: list_entity_latest_agent_refs
  - path: src/data/database.py
    symbol: save_agent_data
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.4.1"
related_statutes:
  - astral.batch.entity-agent-responses-latest-only
supersedes: null
superseded_by: null
---

# Problem

Callers need a lightweight latest-only pointer from an entity to `agent_data` without entity-row JSON mirror columns or unbounded history on the entity.

# Solution shape

Tag RESPONSE rows with `entity_id` on write; reconstruct latest-per-`task_key` refs via `list_entity_latest_agent_refs`. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Persisting full prompt/response blobs on the entity row.
- Reintroducing entity JSON `agent_responses` upserts after AST-984 cutover.
- Inventing a parallel audit/refs table.
