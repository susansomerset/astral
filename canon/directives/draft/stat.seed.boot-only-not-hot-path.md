---
id: astral.seed.boot-only-not-hot-path
title: Seed runs at boot or migration scripts only
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "utils", "scripts"]
  paths: ["src/**", "scripts/migrations/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-771-seed-audit.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Product seed and catalog provision run at server boot (or via an explicit operator or CI script under `scripts/migrations/`). They must not run as side effects of per-request work or recurring `_ensure_*_schema` hot paths. Naming of seed or migration helpers follows `astral.standards.names-not-ticket-ids`.

## Rationale

Hot-path “migrations” re-fire forever and hide one-shot intent.

## Examples

### Conforming

- `start_scheduler` or `bootstrap_runtime` calls provision once; one-shot backfill lives in `scripts/migrations/`.

### Violating

- A prompt-seed helper inside schema ensure on every connection open.
- Auto-insert seed rows from an API request handler.
