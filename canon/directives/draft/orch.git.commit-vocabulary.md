---
id: orch.git.commit-vocabulary
title: Commit vocabulary
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

Use only the named commit types (`plan`, `code`, `park-wip`, `merge-resume`, `test`, `docs`, `resolve`, `merge-child`, `finish-up`) with their listed owners, plus the `sync(dev|ftr|publish-ref): …` merge subjects that `sync-child.sh`, `merge-child.sh` and `refresh-ftr.sh` write. `test()` is the engineer's src fix in test-child or Betty's test-tree commit; one commit never carries both. Do not use deprecated `feat()`, `fix()`, `push-tests()`, or (on new work) `merge-tests()`, and never git's default "Merge remote-tracking branch …" subject.

## Rationale

Shared vocabulary makes sub-log validation and rollups mechanical.

## Examples

### Conforming

- Build stage commits `code(AST-921): …`.

### Violating

- New work lands as `feat(ast-921): …`.
