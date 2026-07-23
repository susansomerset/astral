---
id: orch.roles.betty-owns-test-tree
title: Betty owns the test tree
tier: universal
checkable: judgment
status: active
applies_when:
  layers: []
  paths: ["tests/**", "docs/test-bible/**", "docs/ASTRAL_TEST_BIBLE.md", "scripts/test_*.py", "scripts/testing/**"]
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_TEAM_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Only Betty commits under `tests/`, `scripts/test_*.py`, `scripts/testing/`, and `docs/test-bible/**` (and the monolith bible until retirement). Engineers file `[qa-handoff]` instead of patching tests.

## Rationale

Single test-tree owner keeps manifests and bible honest across tickets.

## Examples

### Conforming

- Engineer posts `[qa-handoff]` when a manifest assertion is wrong.

### Violating

- Engineer "just fixes" a brittle assert in `tests/component/...`.
