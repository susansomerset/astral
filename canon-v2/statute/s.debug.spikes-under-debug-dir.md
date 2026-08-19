---
id: astral.debug.spikes-under-debug-dir
title: Spikes under debug/
tier: scoped
checkable: hook
status: active
applies_when:
  layers: []
  paths: ["debug/**", "docs/features/**", "scripts/spikes/**"]
  change_types: ["add", "modify", "delete"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Spike/R&D output lives under `debug/spikes/<issue-id>/…` and must not be committed (`debug/` is gitignored). Spike findings go on the Linear issue, not under `docs/features/`.

## Rationale

Keeping scratch out of git and features/ prevents plan-doc pollution.

## Examples

### Conforming

- Playwright dump written to `debug/spikes/AST-414/phase1/`.

### Violating

- Spike run notes committed as `docs/features/roster/a16z-spike-notes.md`.
