---
id: astral.patterns.require-auth-on-protected-endpoints
title: require_auth on protected endpoints
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["ui"]
  paths: ["src/ui/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Protected UI API endpoints use `@require_auth`. Endpoints without the decorator are intentionally open (e.g. health). Authenticated identity is `flask.g.user`.

## Rationale

Explicit decorator marking prevents accidental open admin surfaces.

## Examples

### Conforming

- `/api/jobs` uses `@require_auth`; `/api/health` does not.

### Violating

- A new `/api/admin/...` route ships without `@require_auth`.
