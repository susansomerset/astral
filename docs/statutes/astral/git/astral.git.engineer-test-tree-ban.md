---
id: astral.git.engineer-test-tree-ban
title: Engineers must not commit test-tree paths
tier: scoped
checkable: hook
status: active
applies_when:
  layers: []
  paths:
    - "tests/**"
    - "docs/test-bible/**"
    - "docs/ASTRAL_TEST_BIBLE.md"
    - "scripts/test_*.py"
    - "scripts/testing/**"
  change_types: ["add", "modify", "delete"]
source_docs:
  - docs/ASTRAL_TEAM_WORKFLOW.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-22"
---

# Statement

Engineer commits must not add, edit, or delete Betty-owned test-tree paths (`tests/`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md`, `scripts/test_*.py`, `scripts/testing/`). If a test or manifest is wrong, file `[qa-handoff]` and leave the paths to Betty.

## Rationale

Betty owns coverage truth. Engineer edits to the test tree create rollup noise and hide whether a failure is product or harness. Pre-commit already enforces this class of ban — hence `checkable: hook`.

## Examples

### Conforming

- An engineer’s product fix fails Betty’s manifest; they post `[qa-handoff]` and stay on Tests Ready without touching `tests/`.

### Violating

- An engineer “just tweaks one assertion” under `tests/component/` in the same commit as a product fix.
