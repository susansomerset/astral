---
id: astral.dispatch.run-next-is-chain-authority
title: run_next is dispatch chain authority
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/**", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/dispatcher/ast-1110-statute-run-next-is-chain-authority.md
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

When `agent_task.run_next` already encodes a dispatch multi-hop chain, config must not define a parallel allowed-key set, hop-order list, or membership frozenset that restates that chain’s membership or succession. Chain membership and hop succession for those flows come from current `agent_task.run_next` rows (and helpers that read them). Config may still name graduation maps, trigger registries, task specs, and other true config-owned catalogs that do **not** duplicate `run_next` topology. Putting such a shadow list in `config.py` does **not** satisfy `astral.standards.no-hardcoded-sets`.

## Rationale

Config frozensets that copy `run_next` look statute-compliant while drifting from the live database topology and inventing carve-outs (e.g. excluding a hop from a membership set). The documented §2.6.0 carve-out already uses `run_next`; shadow lists create a second authority and hide that drift.

## Examples

### Conforming

- Hop-label claim/graduation helpers that derive parent/child eligibility from `agent_task.run_next` (e.g. `_agent_task_parents_with_run_next`, `_current_agent_task_run_next`) without consulting a config hop-membership frozenset.
- Config that owns `DISPATCH_CHAIN_TERMINAL_GRADUATION` / trigger→registry maps without listing every hop task key as chain membership.

### Violating

- `JOB_ARTIFACT_ENTRY_TASK_KEYS` (or any wrapper) used as authority for which consult hops are “in” the job-artifact chain while `run_next` already encodes those hops.
- `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` used as authority for resume/artifact hop succession instead of `run_next`.
- `CANDIDATE_STAGE_DISPATCH[…]["craft_task_keys"]` used as authority for craft daisy-chain succession instead of `run_next`.

## Notes

Does not delete the named shadows (AST-1111–AST-1113). Does not change Manage Tasks UI, `dispatch_tasks` uniqueness, or AUTO/CLICK semantics. Complements `astral.state.no-daisy-chain-in-run` (carve-out exists) by requiring the carve-out’s **data** be the membership authority. Archie approved working id on parent AST-1109 Architectural definition (2026-07-31); statute body lands with this child.
