---
id: astral.ui.frontend-file-placement
title: Frontend file placement
tier: scoped
checkable: ci
status: active
applies_when:
  layers: ["ui"]
  paths: ["src/ui/frontend/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Frontend files live in the prescribed flat locations: entry points in `src/` root; contexts in `contexts/`; shared modules in `lib/`; reusable components in `components/` (flat); pages in `pages/` (flat, section-prefixed); assets in `assets/`; styles in `App.css`.

## Rationale

Flat placement keeps imports predictable and matches the UI stack contract.

## Examples

### Conforming

- New page `AdminFoo.tsx` lands in `src/pages/`.

### Violating

- A nested `src/pages/admin/foo/FooPage.tsx` tree is introduced.
