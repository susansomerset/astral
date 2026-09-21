---
id: astral.layers.ui-config-driven-business-logic
title: UI business logic is config-driven
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["ui", "utils"]
  paths: ["src/ui/**", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

When the frontend needs conditional behavior (visibility, enablement, filtering, shaping), that logic is declared in config and resolved in `src/ui/api/` before serving. React renders the resolved response without duplicating business rules.

## Rationale

Duplicating state rules in React diverges from backend truth.

## Examples

### Conforming

- `/api/nav_config` resolves visibility from `NAV_CONFIG` against candidate state.

### Violating

- A React page hardcodes which candidate states show a menu item.
