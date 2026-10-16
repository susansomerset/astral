---
id: orch.git.three-permanent-branches
title: Three permanent branches
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
approved_at: "2026-10-08"
---

# Statement

Only two permanent branches exist on origin: `main` (Susan/production) and `dev` (Chuckles/integration, including the cumulative test corpus). `tests` is retired: it stays on origin as frozen history and is never written to or merged.

## Rationale

Extra permanent branches fragment integration and ownership. A separate `tests` line gave every test two routes onto a sub (via `merge-tests` and via `dev`), and the copies drifted into conflicts and silent test deletions (AST-2083, AST-2033).

## Examples

### Conforming

- Day-to-day integration lands on `origin/dev`.

### Violating

- A long-lived `origin/staging` becomes a second integration line.
