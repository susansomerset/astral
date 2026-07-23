---
id: orch.roles.pre-commit-path-bans
title: Pre-commit path bans by role
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

Pre-commit hooks enforce role path bans: engineers cannot commit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`; Betty cannot commit `src/` or `docs/features/`; Radia cannot commit `src/` or `tests/`.

## Rationale

Structural enforcement beats prose reminders for ownership boundaries.

## Examples

### Conforming

- Engineer commit touching only `docs/statutes/` succeeds.

### Violating

- Engineer stages `tests/component/...` and the hook must fail the commit.
