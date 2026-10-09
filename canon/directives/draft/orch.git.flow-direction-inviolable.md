---
id: orch.git.flow-direction-inviolable
title: Git flow direction inviolable
tier: universal
checkable: judgment
applies_when:
  layers: []
  paths: []
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_GIT_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-10-08"
---

# Statement

Flow is `dev→ftr→sub`, `sub→ftr→dev`, `dev→main`. Tests and the test bible travel with product code on that same path: Betty commits them on the sub. Nothing merges into or out of the retired `tests` branch.

## Rationale

One-way flow keeps production and integration from contaminating each other; one path per test means one copy per test.

## Examples

### Conforming

- Betty commits `test(AST-NNN): …` on the child's `sub`; it reaches `dev` only through `merge-child` and `finish-up`.

### Violating

- Someone merges `origin/tests` into a sub, an ftr, or `dev`.
