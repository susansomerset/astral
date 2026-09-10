---
id: orch.git.three-permanent-branches
title: Three permanent branches
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

Only three permanent branches exist on origin: `main` (Susan/production), `dev` (Chuckles/integration), and `tests` (Betty/test corpus).

## Rationale

Extra permanent branches fragment integration and ownership.

## Examples

### Conforming

- Day-to-day integration lands on `origin/dev`.

### Violating

- A long-lived `origin/staging` becomes a second integration line.
