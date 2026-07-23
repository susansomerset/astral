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
approved_at: "2026-07-23"
---

# Statement

Betty must not commit to `src/` or `docs/features/` (except the `merge-tests` merge commit on a sub).

## Rationale

Betty owns the test corpus; product and plan docs stay with engineers/Chuckles.

## Examples

### Conforming

- Betty commits under `tests/` and `docs/test-bible/` on `astral-tests`.

### Violating

- Betty edits `src/core/dispatcher.py` to make a test pass.
