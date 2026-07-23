---
id: astral.patterns.coat-check-never-store-empty
title: Coat-check never stores empty
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core"]
  paths: ["src/core/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Coat-check handlers must not store empty or failed values. Return `None` so the next attempt can re-trigger fetch after the underlying issue is fixed.

## Rationale

Caching failures permanently disables lazy population.

## Examples

### Conforming

- Failed JD scrape returns `None` without writing job_description.

### Violating

- Handler saves `""` for website_content on Playwright timeout.
