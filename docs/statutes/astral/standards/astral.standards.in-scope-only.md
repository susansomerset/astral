---
id: astral.standards.in-scope-only
title: In-scope only
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Touch only what ASTRAL_CODE_RULES or a module header explicitly scopes. Do not expand scope silently.

## Rationale

Silent scope creep turns a focused change into an unplanned refactor and breaks plan fidelity.

## Examples

### Conforming

- A ticket to fix batch claim only edits claim helpers named in the plan.

### Violating

- While fixing claim helpers, the agent also rewrites unrelated roster scoring "because it was nearby."
