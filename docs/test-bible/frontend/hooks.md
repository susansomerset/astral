# Hooks

**Test tree:** `tests/component/frontend/hooks/`

_(Vitest RTL tests; see §6b in [README](../README.md). Manifest blocks below.)_

### AST-1335 · AST-1315

Shared dirty-leave save-then-navigate helper (`useDirtyLeaveSaveThenNavigate`) + data-router boot in `App.tsx` so `useBlocker` works. Does **not** wire Candidate Profile (sibling **AST-1336**). Proposed catalog id `pattern.ui.dirty-leave-save-then-navigate` (Archie approval pending) — not treated as approved law here.

| Area | Source | Component tests |
| --- | --- | --- |
| Dirty-leave hook | `src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts` | `tests/component/frontend/hooks/test_useDirtyLeaveSaveThenNavigate.test.tsx` — BlockerFunction clean/dirty/same-pathname; Cancel → reset; Save → onSave → proceed; save reject → reset; Save = `btn primary` (mocked `useBlocker`; real `UserPromptProvider`) |
| App data router | `src/ui/frontend/src/App.tsx` (`createBrowserRouter` + `RouterProvider`) | `tests/component/frontend/test_App.test.tsx` — **source contract** (createBrowserRouter / RouterProvider / no BrowserRouter). Full `<App />` mount left unhandled AbortSignal under RR7+jsdom/Node 24 (exit 1) — do not reintroduce mount smoke on this tip |

**§6c:** N/A — no `pages/` change; Profile leave UX is **AST-1336**.

**Broken / obsolete:** `test_App.test.tsx` — replace mount smoke with source contract so `npm run test:component` exits **0** ([qa-handoff] Ada).

**Integration:** no existing `tests/integration/` scenario asserts `BrowserRouter` / leave prompts — no drift revision.

**AST-1335** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useDirtyLeaveSaveThenNavigate.test.tsx \
  ../../../tests/component/frontend/test_App.test.tsx
```

### AST-893 · AST-886

Shared section expand policy: **Expand One** (default / `expandAll` omitted or false) vs **Expand All** (`expandAll: true`) plus bulk chrome on opted-in pages.

| Area | Source | Component tests |
| --- | --- | --- |
| Expand policy hook | `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` | `tests/component/frontend/hooks/test_useSectionExpandPolicy.test.tsx` — Expand One accordion + zero; Expand All multi-open, collapse sibling-safe, `expandAllSections` / `collapseAllSections`, `showBulkChrome` |

**Page + chrome:** `docs/test-bible/frontend/pages.md` (**AST-893**), `docs/test-bible/frontend/components.md` (**AST-893**).

**AST-893** narrowed Vitest (hook only):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useSectionExpandPolicy.test.tsx
```
