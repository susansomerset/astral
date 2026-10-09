---
id: astral.git.betty-no-src-or-features
title: Betty must not commit src or features
tier: scoped
checkable: hook
status: active
applies_when:
  layers: []
  paths: ["src/**", "docs/features/**"]
  change_types: ["add", "modify", "delete"]
source_docs:
  - docs/ASTRAL_GIT_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-10-08"
---

# Statement

Betty must not commit changes to `src/` or `docs/features/`. In a merge commit (a `sync-child` merge on the sub) those paths may only be staged byte-identical to a merge parent or to git's own clean auto-merge — Betty never resolves a product conflict.

## Rationale

Betty owns the test corpus; product and plan docs stay with engineers/Chuckles.

## Examples

### Conforming

- Betty commits under `tests/` and `docs/test-bible/` on the child's `sub` in the epic worktree.

### Violating

- Betty edits `src/core/dispatcher.py` to make a test pass.
