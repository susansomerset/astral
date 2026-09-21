---
id: astral.debug.no-repo-root-artifacts-dir
title: No repo-root artifacts/ directory
tier: scoped
checkable: hook
status: active
applies_when:
  layers: []
  paths: ["artifacts/**", "scripts/spikes/**"]
  change_types: ["add", "modify", "delete"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Do not create a top-level `artifacts/` directory. Spike scripts default `--out` / `--out-dir` to `debug/spikes/<issue-id>/…`. The name `artifacts/` is reserved for the Astral Artifacts program docs.

## Rationale

Avoids colliding with the Artifacts program and keeps spike output gitignored.

## Examples

### Conforming

- Spike CLI defaults `--out-dir debug/spikes/AST-414`.

### Violating

- Spike script writes to repo-root `artifacts/out.json`.
