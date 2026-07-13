# Hooks

**Test tree:** `tests/component/frontend/hooks/`

_(Vitest RTL tests; see §6b in [README](../README.md). Manifest blocks below.)_

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
