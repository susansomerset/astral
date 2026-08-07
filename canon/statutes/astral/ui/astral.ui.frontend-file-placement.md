---
id: astral.ui.frontend-file-placement
title: Frontend file placement
tier: scoped
checkable: ci
status: active
applies_when:
  layers: ["ui"]
  paths: ["src/ui/frontend/**", "src/ui/extension/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-08-07"
---

# Statement

Client files under `src/ui/` live in prescribed locations — never outside `src/ui/`.

**SPA (`src/ui/frontend/`):** entry points in `src/` root; contexts in `contexts/`; shared modules in `lib/`; reusable components in `components/` (flat); pages in `pages/` (flat, section-prefixed); assets in `assets/`; styles in `App.css`.

**Extension (`src/ui/extension/`):** WXT `src/entrypoints/` for runtime entrypoints; `src/lib/` for shared non-entrypoint modules. Build output under `.output/` (gitignored); not served by Flask.

## Rationale

Flat SPA placement keeps imports predictable. The extension is a second client surface under `src/ui/` (sibling to `frontend/`) so Manifest V3 tooling stays inside the UI layer without a top-level `extension/` exemption.

## Examples

### Conforming

- New page `AdminFoo.tsx` lands in `src/pages/`.
- Extension background entrypoint at `src/ui/extension/src/entrypoints/background.ts`.

### Violating

- A nested `src/pages/admin/foo/FooPage.tsx` tree is introduced.
- Repo-root `extension/` or `src/extension/` for the browser client.
