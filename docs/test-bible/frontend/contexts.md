# Contexts

**Test tree:** `tests/component/frontend/contexts/`

_(Vitest RTL tests; see §6b in [README](README.md). Manifest blocks below.)_

| Ticket | Behavior | Sources | Manifest |
| --- | --- | --- | --- |
| **AST-1311** | `document.title` from selected list-row `full`; reset `Astral` on unmount | `src/ui/frontend/src/contexts/CandidateContext.tsx` | **`test_CandidateContext.test.tsx`** (`CandidateProvider — AST-1311 browser tab title`); formatter map in [`lib.md`](lib.md) |

### AST-1408 · AST-1406

**Parent:** [AST-1406 — Page refreshes and modals are closed (lost!)](https://linear.app/astralcareermatch/issue/AST-1406). **Publish:** `origin/sub/AST-1406/AST-1408-keep-the-spa-mounted-across-session-revalidation`.

Session-shell half of proposed `pattern.ui.in-place-live-refresh`: after first `/api/me` for the current Stytch session, JWT rotation re-reads identity silently (`loading` stays false). `RequireAuth` / `AdminRoute` keep an already-authenticated tree mounted. Extend loop is keyed on `sessionPresent`, not session-object identity. Does **not** own list/toggle live update (**AST-1409** / **AST-1410**); does **not** change cadence integers or log-off copy.

| Area | Source | Component tests |
| --- | --- | --- |
| First-resolution-only `loading`; silent JWT re-read; extend loop on `sessionPresent` | `AuthContext.tsx` | **`test_AuthContext.test.tsx`** — **`AST-1408:*`** (+ AST-1374 extend-start regression) |
| Loading only when uninitialized **and** no session | `RequireAuth.tsx` | **`test_RequireAuth.test.tsx`** — **`AST-1408:*`** (+ existing Login / LogOffScreen) |
| Loading only while `user === null` | `AdminRoute.tsx` | **`test_AdminRoute.test.tsx`** — **`AST-1408:*`** (+ existing admin / non-admin / first-paint Loading) |
| Stable `useStytch()` client (extend-loop identity) | `stytchMock.tsx` | same AuthContext cases |

**Broken / obsolete:** none — first-paint Loading (`user` null) and log-off routes stay. AST-1374 extend-start still applies; loop restart is now asserted against a stable mock client.

**§6c:** no page-file product diff — session-shell gates are the UI coverage.

**Integration:** no existing scenario asserts SPA session remount / overlay survival — no revision. Do not invent new integration coverage.

## QA test manifest

1. AuthContext silent JWT revalidation + extend-loop identity + session-loss loading: `tests/component/frontend/contexts/test_AuthContext.test.tsx`
2. RequireAuth first-boot Loading vs keep-mounted: `tests/component/frontend/components/test_RequireAuth.test.tsx`
3. AdminRoute keep-mounted + known non-admin redirect while loading: `tests/component/frontend/components/test_AdminRoute.test.tsx`

**AST-1408** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/contexts/test_AuthContext.test.tsx \
  ../../../tests/component/frontend/components/test_RequireAuth.test.tsx \
  ../../../tests/component/frontend/components/test_AdminRoute.test.tsx
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

Local-deploy SPA skip Login / extend: **`docs/test-bible/frontend/lib.md`** § AST-1441.
