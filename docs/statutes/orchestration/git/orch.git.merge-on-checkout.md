---
id: orch.git.merge-on-checkout
title: Merge ftr on sub checkout
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

Whenever an engineer (or Chuckles seeding) checks out a `sub/*` in the epic worktree: `git fetch origin`, checkout the sub, then `git merge origin/ftr/<parent-segment>`.

## Rationale

Subs must stack on the rolled-up parent tip, not a stale seed.

## Examples

### Conforming

- Before coding, merge `origin/ftr/AST-912-systemic-statutes` into the active sub.

### Violating

- Coding on a sub that has not merged an advanced ftr tip with sibling landings.
