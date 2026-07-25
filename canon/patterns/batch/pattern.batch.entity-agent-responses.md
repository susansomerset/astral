---
id: pattern.batch.entity-agent-responses
name: Entity agent_responses (latest-only)
status: approved
proposed_in: AST-913
approved_by: Archie
approved_at: "2026-07-24"
canonical_refs:
  - path: src/core/agent.py
    symbol: _store_agent_response
  - path: src/core/roster.py
    symbol: dedupe_agent_responses_latest
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.4.1"
related_statutes:
  - astral.batch.entity-agent-responses-latest-only
supersedes: null
superseded_by: null
---

# Problem

Callers need a lightweight latest-only pointer from entity rows to `agent_data` without bloating the entity or retaining every historical ref.

# Solution shape

After successful `do_task`, upsert one `agent_responses` entry per `task_key` (latest wins); keep full blocks in `agent_data`. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Persisting full prompt/response blobs on the entity row.
- Appending unbounded history on the entity.
- Writing refs on failed `do_task`.
