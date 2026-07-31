---
id: orch.git.flow-direction-inviolable
title: Git flow direction inviolable
tier: universal
checkable: judgment
status: active
applies_when:
  layers: []
  paths: []
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_GIT_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Flow is `dev→ftr→sub`, `tests→sub`, `sub→ftr→dev`, `dev→main`. `tests` never merges into `dev` or `main`; `dev` never merges into `tests`.

## Rationale

One-way flow keeps production, integration, and test corpus from contaminating each other.

## Examples

### Conforming

- Betty delivers tests via `merge-tests` onto `sub`, not onto `dev`.

### Violating

- Someone merges `origin/tests` into `origin/dev`.
