---
id: orch.git.betty-merge-tests-one-sha
title: Betty merge-tests one SHA
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

Betty delivers exactly one `origin/tests` SHA per child via exactly one `merge-tests(AST-NNN): origin/tests <sha>` commit on the sub, then pushes the sub.

## Rationale

One SHA pins the test corpus for the ticket and avoids interleaved duplicate merges.

## Examples

### Conforming

- One `merge-tests(AST-920): origin/tests <sha>` on the child publish ref.

### Violating

- Two `merge-tests` commits for the same child after revising tests.
