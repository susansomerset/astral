---
id: orch.git.no-dev-agent-branches
title: No dev-<agent> branches
tier: universal
checkable: hook
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

Do not create `dev-<agent>` branches locally or on origin. Work in the epic worktree on the ticket `sub/*` (or permanent `dev`/`tests` for Chuckles/Betty).

## Rationale

Agent-named integration branches duplicated work and diverged from `dev`.

## Examples

### Conforming

- Ada works on `sub/AST-912/AST-921-…` in `astral-AST-912/`.

### Violating

- Creating and pushing `origin/dev-ada`.
