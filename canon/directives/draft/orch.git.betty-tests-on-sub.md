---
id: orch.git.betty-tests-on-sub
title: Betty commits tests on the sub
tier: universal
checkable: hook
applies_when:
  layers: []
  paths: []
  change_types: ["any"]
source_docs:
  - docs/ASTRAL_GIT_WORKFLOW.md
supersedes: orch.git.betty-merge-tests-one-sha
superseded_by: null
approved_by: Archie
approved_at: "2026-10-08"
---

# Statement

Betty delivers tests and test-bible changes as `test(AST-NNN): …` (or `docs(AST-NNN): test bible — …`) commits made directly on the child's `sub/*` in the epic worktree, after `sync-child.sh`, and pushes the sub. Revisions are new additive commits. Test-tree and product changes never share a commit. Betty never pushes tests to `ftr/*`, `dev`, a sibling `sub/*`, or `tests`.

## Rationale

One path per test (sub → ftr → dev) means one copy of every test: no drift between a test branch and `dev`, no duplicate deliveries, and no git-rule exceptions to replace a bad delivery (AST-2107).

## Examples

### Conforming

- Betty runs `sync-child.sh sub/AST-2046/AST-2083-resume-editor --ftr AST-2046-…`, commits `test(AST-2083): resume editor tests + bible`, and pushes the sub; after a `[qa-handoff]` she adds `test(AST-2083): fix stale snapshot`.

### Violating

- Betty commits tests on a separate branch and merges or copies them onto the sub.
- A single commit changes `src/core/tracker.py` and `tests/component/core/test_tracker.py`.
