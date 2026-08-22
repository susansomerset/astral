---
id: orch.git.no-cherry-pick-rebase-force
title: No cherry-pick, rebase, or force-push
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

Do not cherry-pick onto branches, rebase branches already pushed to origin, or force-push to any branch on origin.

## Rationale

These operations rewrite shared history and break sibling/agent coordination.

## Examples

### Conforming

- Publish with fast-forward `git push origin HEAD:sub/…`.

### Violating

- `git push --force` to `origin/sub/…` after a local rebase.
