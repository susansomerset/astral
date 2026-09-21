---
id: astral.state.no-daisy-chain-in-run
title: No daisy-chain across a dispatch run
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core"]
  paths: ["src/core/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Entities are not automatically flowed through multiple registered states within a single dispatch run. Each cycle claims one state, processes, and transitions; the next cycle picks them up. Documented `run_next` hop chains (CODE_RULES §2.6.0) are the carve-out.

## Rationale

Daisy-chaining hides failures and couples unrelated steps into one fragile run.

## Examples

### Conforming

- A grade_do batch transitions jobs once and ends; the next task claims the new state later.

### Violating

- One runner loops a job through PASSED_JD → grade_do → grade_get without separate dispatch cycles (outside the documented run_next carve-out).

## Notes

Detailed `run_next` hop-label rules remain in CODE_RULES §2.6.0 narrative; see HARVEST.md.
