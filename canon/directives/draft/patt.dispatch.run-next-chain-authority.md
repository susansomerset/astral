---
id: pattern.dispatch.run-next-chain-authority
name: run_next as dispatch chain authority
status: proposed
proposed_in: AST-1109
approved_by: null
approved_at: null
canonical_refs:
  - path: src/core/agent.py
    symbol: _current_agent_task_run_next
  - path: src/utils/config.py
    symbol: _agent_task_parents_with_run_next
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.6.0"
related_statutes:
  - astral.dispatch.run-next-is-chain-authority
  - astral.state.no-daisy-chain-in-run
  - astral.config.config-source-of-truth
  - astral.standards.no-hardcoded-sets
supersedes: null
superseded_by: null
---

# Problem

Dispatch multi-hop membership and succession get restated as config frozensets / hop-order lists that drift from live `agent_task.run_next` rows and invent carve-outs.

# Solution shape

Treat current `agent_task.run_next` as the authority for chain membership and hop succession on job/candidate dispatch chains that already use the §2.6.0 carve-out. Read succession via existing helpers (`_current_agent_task_run_next`, `_agent_task_parents_with_run_next`, and claim/graduation helpers that already follow `run_next`). Config may own graduation maps and trigger registries; it must not restate hop sets. Point at `canonical_refs` — do not paste large code into this catalog entry. Sibling anomaly remediations (AST-1111–AST-1113) delete the named shadows end-to-end against `astral.dispatch.run-next-is-chain-authority`.

## When not to use

- True config-owned catalogs that are not `run_next` topology (grades, normalize gates, `TASK_CONFIG` specs, seed AUTO defaults).
- Replacing the §2.6.0 hop-label claim/graduation path with a new config list.
- Depending on this pattern id for implementation until `status: approved` (AUTHORING).

## Notes

Lands as `proposed` from AST-1109 / AST-1110. Archie may approve later; remediations bind to the statute first. Does not own AST-1108 seed cleanup.
