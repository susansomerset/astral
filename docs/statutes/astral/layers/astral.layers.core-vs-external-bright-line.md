---
id: astral.layers.core-vs-external-bright-line
title: Core vs external bright line
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "external"]
  paths: ["src/core/**", "src/external/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

External owns all I/O (navigation, DOM, HTTP, API calls) and returns data. Core orchestrates business logic and calls external for I/O.

## Rationale

Keeping I/O out of core keeps domain logic testable and side-effect-free at the boundary.

## Examples

### Conforming

- Playwright navigation lives in `src/external/playwright.py`; core calls it.

### Violating

- Core opens an httpx client and posts to Anthropic directly.
