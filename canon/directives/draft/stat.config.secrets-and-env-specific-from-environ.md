---
id: astral.config.secrets-and-env-specific-from-environ
title: Secrets and env-specific from environ
tier: scoped
checkable: ci
status: active
applies_when:
  layers: ["utils", "core", "external", "ui", "scripts"]
  paths: ["src/**", "scripts/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Secrets and environment-specific values (paths/URLs that differ by environment) are read with `os.environ["KEY"]` — no `.get()`, no fallback. Missing vars crash at startup. Never put secrets in `config.py`.

## Rationale

Silent defaults for secrets hide misconfiguration until production fails subtly.

## Examples

### Conforming

- API key loaded via `os.environ["ANTHROPIC_API_KEY"]` at import/startup.

### Violating

- `os.environ.get("ANTHROPIC_API_KEY", "")` with an empty-string fallback.
