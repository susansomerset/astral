---
id: orch.git.ftr-sub-topology
title: ftr/sub topology
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

Parent features use `ftr/<ticket-id>-<slug>`; children use `sub/<parent-id>/<child-id>-<slug>`. Chuckles creates these refs at dispatch — agents never create `ftr/` or `sub/` refs.

## Rationale

Authoritative topology keeps publish refs discoverable and prevents rogue branches.

## Examples

### Conforming

- Child publishes to `origin/sub/AST-912/AST-921-harvest-astral-law-docs`.

### Violating

- An engineer runs `git push -u origin` inventing a new `ftr/AST-999-…` ref.
