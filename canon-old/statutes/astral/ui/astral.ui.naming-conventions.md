---
id: astral.ui.naming-conventions
title: UI naming conventions
tier: scoped
checkable: ci
status: active
applies_when:
  layers: ["ui"]
  paths: ["src/ui/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

React component files use PascalCase. Route paths and API endpoints use snake_case. Python remains snake_case.

## Rationale

Consistent naming reduces routing/import mistakes across Flask and React.

## Examples

### Conforming

- Component `JobsRecommended.tsx` with route `/jobs/recommended` and API `/api/jobs`.

### Violating

- Component file `jobs-recommended.tsx` with route `/Jobs/Recommended`.
