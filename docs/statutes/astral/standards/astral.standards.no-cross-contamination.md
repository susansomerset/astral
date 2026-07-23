---
id: astral.standards.no-cross-contamination
title: No cross-contamination
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Do not reference, import from, or depend on any code or data outside the layered structure (`src/core`, `src/data`, `src/external`, `src/utils`, `src/ui`).

## Rationale

Out-of-layer dependencies recreate the monolith the architecture forbids.

## Examples

### Conforming

- Core imports data/external/utils only.

### Violating

- A core module imports a helper from a repo-root scratch package.
