---
id: orch.git.one-epic-worktree-per-parent
title: One epic worktree per parent
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

Each in-flight parent gets one `<reponame>-<parent-id>/` epic worktree. Subs are branches checked out one at a time in that worktree — not separate worktrees per child.

## Rationale

One worktree per epic avoids AGENTS.md/hook thrash and path sprawl.

## Examples

### Conforming

- AST-912 work happens in `astral-AST-912/` with one active `sub/*`.

### Violating

- Creating `astral-AST-921/` as a second worktree for a child of AST-912.
