# AST-612 — React Stytch login and admin UI gating (Use stytch for user authentication)

- **Linear (this ticket):** [AST-612](https://linear.app/astralcareermatch/issue/AST-612/react-stytch-login-and-admin-ui-gating-use-stytch-for-user)
- **Parent:** [AST-609](https://linear.app/astralcareermatch/issue/AST-609/use-stytch-for-user-authentication)
- **Publish ref:** `origin/sub/AST-609/AST-612-react-login-and-admin-ui`
- **Depends on:** [AST-611](https://linear.app/astralcareermatch/issue/AST-611/flask-stytch-auth-admin-role-and-api-enforcement-use-stytch-for-user) on `origin/ftr/ast-609-use-stytch-for-user-authentication` (`@require_auth`, `@require_admin`, `/api/me` with `is_admin`, Admin nav omitted server-side for non-admin)

## Summary

Replace the React `api.ts` stub token with the Stytch B2C **session JWT** from `@stytch/react`. Gate the SPA behind Stytch login (happy path: Email Magic Links + OAuth via prebuilt `StytchLogin`). After login, call `/api/me` to learn `is_admin`. Hide Admin nav (defense in depth — server already filters `/api/nav_config`), block `/admin/*` routes client-side, and make the candidate `<select>` read-only for non-admins. **Happy path only** — no exhaustive offline/error UX beyond existing shell loading/error patterns.

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/ui/frontend/src/lib/api.ts` | Bearer injection via registered token getter | frontend only |
| `src/ui/frontend/src/contexts/AuthContext.tsx` | `/api/me` + `is_admin` for UI gating | frontend only |
| `src/ui/frontend/src/contexts/CandidateContext.tsx` | Non-admin `setSelectedId` noop | frontend only |
| `src/ui/api/*`, `src/utils/auth.py`, `src/external/stytch.py` | **Read-only** — shipped in AST-610/611 | do not modify |

⚠️ **Decision:** Use **`@stytch/react`** prebuilt **`StytchLogin`** (Email Magic Links + OAuth) — matches Stytch B2C Consumer SPA docs and `stytch-react-example`. Headless custom UI is out of scope for happy path.

⚠️ **Decision:** **`Authorization: Bearer <session_jwt>`** on every `api()` call — matches AST-611 / `ASTRAL_CODE_RULES` §2.9 and `stytch.authenticate_session_jwt` on the server. Do **not** rely on cookies alone even though Stytch also stores cookies; explicit Bearer keeps Flask validation path identical to Betty’s component tests.

⚠️ **Decision:** **`VITE_STYTCH_PUBLIC_TOKEN`** at Vite build time (Railway frontend build). No backend endpoint for public token in this ticket — keeps AST-612 frontend-only.

⚠️ **Decision:** Non-admin **candidate selector** is UI-only (disabled `<select>` + `setSelectedId` noop). Server already returns 403 on admin candidate mutations (AST-611). Non-admins may still read/update `candidate_data` for ids they already hold — no per-user candidate scoping in this epic.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| Flask auth decorators, Stytch Python client | **AST-610** / **AST-611** (already on `ftr`) |
| Committing under `tests/` or `docs/ASTRAL_TEST_BIBLE.md` | **Betty** (`qa-child`) — engineer pre-commit hook blocks |
| HttpOnly Stytch cookies, custom domain cookie tuning | Future hardening |
| Password login, MFA, session refresh error UX | Happy path only |
| `ASTRAL_CODE_RULES.md` §2.9 stub wording update | **Radia** (optional doc pass) |

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/ui/frontend/package.json` | Add `@stytch/react` dependency | frontend | Katherine (build) |
| `env.example` | Document `VITE_STYTCH_PUBLIC_TOKEN` + Stytch redirect URL notes | docs | Katherine (build) |
| `src/ui/frontend/src/vite-env.d.ts` | `ImportMetaEnv` for `VITE_STYTCH_PUBLIC_TOKEN` | frontend | Katherine (build) |
| `src/ui/frontend/src/lib/api.ts` | Remove stub; `setAuthTokenGetter`; inject Bearer when token present | frontend | Katherine (build) |
| `src/ui/frontend/src/contexts/AuthContext.tsx` | **New** — Stytch session + `/api/me` → `user`, `isAdmin`, `loading` | frontend | Katherine (build) |
| `src/ui/frontend/src/pages/Login.tsx` | **New** — `StytchLogin` prebuilt UI | frontend | Katherine (build) |
| `src/ui/frontend/src/pages/Authenticate.tsx` | **New** — `stytch.authenticateByUrl` OAuth/magic-link callback | frontend | Katherine (build) |
| `src/ui/frontend/src/components/RequireAuth.tsx` | **New** — session gate → `Login` or children | frontend | Katherine (build) |
| `src/ui/frontend/src/components/AdminRoute.tsx` | **New** — redirect non-admin away from `/admin/*` | frontend | Katherine (build) |
| `src/ui/frontend/src/App.tsx` | `StytchProvider` + `AuthProvider` wrapper | frontend | Katherine (build) |
| `src/ui/frontend/src/routes.tsx` | `/authenticate`, auth shell, `AdminRoute` wrappers on admin paths | frontend | Katherine (build) |
| `src/ui/frontend/src/components/NavigationShell.tsx` | Read-only candidate select when `!isAdmin` | frontend | Katherine (build) |
| `src/ui/frontend/src/contexts/CandidateContext.tsx` | `setSelectedId` noop when non-admin (via `useAuth`) | frontend | Katherine (build) |
| `tests/component/frontend/test-utils.tsx` | Mock `AuthProvider` defaults (`isAdmin: true`) in `AllProviders` | tests | Betty (qa-child) |
| `tests/component/frontend/lib/test_api.test.ts` | Token getter instead of hardcoded stub | tests | Betty (qa-child) |
| `tests/component/frontend/contexts/test_AuthContext.test.tsx` | **New** — `/api/me` happy path | tests | Betty (qa-child) |
| `tests/component/frontend/components/test_RequireAuth.test.tsx` | **New** — login gate | tests | Betty (qa-child) |
| `tests/component/frontend/components/test_AdminRoute.test.tsx` | **New** — admin route redirect | tests | Betty (qa-child) |
| `tests/component/frontend/components/test_NavigationShell.test.tsx` | Non-admin candidate select disabled | tests | Betty (qa-child) |
| `tests/component/frontend/contexts/test_CandidateContext.test.tsx` | Non-admin `setSelectedId` noop | tests | Betty (qa-child) |
| `docs/ASTRAL_TEST_BIBLE.md` | §7.13zza AST-612 manifest rows | bible | Betty (qa-child) |

## Stage 1: Stytch dependency, env, and `api.ts` token injection

**Done when:** `npm install` succeeds in `src/ui/frontend/`; `api.ts` injects `Bearer` from a registered getter (no hardcoded stub); missing public token fails fast at Stytch client init with a clear console error; `npm run build` in frontend passes.

1. In `src/ui/frontend/package.json`, under `"dependencies"`, add `"@stytch/react": "^19.0.0"` (bump only if install fails on Railway nixpacks).

2. In `env.example`, after the `STYTCH_SECRET` block, add:

```
# Stytch public token for React SPA (Vite build — not secret, but project-specific)
# Dashboard: API Keys → Public token. Required for AST-612 frontend build on Railway.
VITE_STYTCH_PUBLIC_TOKEN=public-token-test-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Stytch Dashboard → Redirect URLs (types Login + Sign-up):
#   http://localhost:5173/authenticate  (Vite dev)
#   https://<your-railway-host>/authenticate
# Stytch Dashboard → Authorized environments: same origins as above (no trailing path).
```

3. In `src/ui/frontend/src/vite-env.d.ts`, extend `ImportMetaEnv`:

```typescript
interface ImportMetaEnv {
  readonly VITE_STYTCH_PUBLIC_TOKEN: string
}
```

4. Replace contents of `src/ui/frontend/src/lib/api.ts`:

```typescript
type TokenGetter = () => string | null | undefined

let authTokenGetter: TokenGetter = () => null

/** Registered by AuthContext when Stytch session is active. */
export function setAuthTokenGetter(getter: TokenGetter): void {
  authTokenGetter = getter
}

async function api(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers)
  const token = authTokenGetter()
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }
  return fetch(path, { ...options, headers })
}

export default api
```

Remove the `AUTH_TOKEN` stub and Auth0 TODO.

5. Run from `src/ui/frontend/`: `npm install` then `npm run build`.

## Stage 2: Stytch provider, auth context, and login gate

**Done when:** Unauthenticated users see only the Stytch login UI; authenticated users reach `NavigationShell`; every `api()` call during authenticated use includes `Bearer <session_jwt>`; `/api/me` loads once per session and exposes `isAdmin` to descendants.

1. Create `src/ui/frontend/src/lib/stytchClient.ts`:

```typescript
import { createStytchUIClient } from "@stytch/react"

const publicToken = import.meta.env.VITE_STYTCH_PUBLIC_TOKEN
if (!publicToken) {
  console.error("VITE_STYTCH_PUBLIC_TOKEN is not set — Stytch login will not work")
}

export const stytchClient = createStytchUIClient(publicToken ?? "")
```

2. Create `src/ui/frontend/src/contexts/AuthContext.tsx`:

- Export types:

```typescript
export interface MeUser {
  user_id: string
  name: string
  is_admin: boolean
}

interface AuthCtx {
  user: MeUser | null
  isAdmin: boolean
  loading: boolean
  refreshMe: () => void
}
```

- `AuthProvider` children wrapper:
  - Use `useStytchSession()` from `@stytch/react`.
  - On mount and when `session?.session_jwt` changes:
    - If no JWT: set `user = null`, `loading = false`, call `setAuthTokenGetter(() => null)`.
    - If JWT present: call `setAuthTokenGetter(() => session.session_jwt)`, then `api("/api/me")` → `r.json()` on success; set `user` from body; on non-OK set `user = null`.
  - `isAdmin = Boolean(user?.is_admin)`.
  - Export `useAuth()` hook (same pattern as `useCandidate`).

3. Create `src/ui/frontend/src/pages/Authenticate.tsx`:

- `useStytch()`, `useStytchSession()`.
- `useEffect`: if `session` exists, `navigate("/", { replace: true })`; else `stytch.authenticateByUrl({ session_duration_minutes: 60 })`.
- Render `<p>Completing sign-in…</p>` (happy path only).

4. Create `src/ui/frontend/src/pages/Login.tsx`:

- Import `StytchLogin` from `@stytch/react` and `Products` from `@stytch/vanilla-js`.
- `const redirect = `${window.location.origin}/authenticate``.
- `config` prop:

```typescript
{
  products: [Products.emailMagicLinks, Products.oauth],
  emailMagicLinksOptions: {
    loginRedirectURL: redirect,
    loginExpirationMinutes: 60,
    signupRedirectURL: redirect,
    signupExpirationMinutes: 60,
  },
  oauthOptions: {
    providers: [{ type: "google" }],
    loginRedirectURL: redirect,
    signupRedirectURL: redirect,
  },
}
```

- Centered layout using existing shell CSS classes where possible (`content` / minimal wrapper div).

5. Create `src/ui/frontend/src/components/RequireAuth.tsx`:

- If `useStytchSession().session` is undefined and Stytch client still initializing → show `<p>Loading…</p>` (match NavigationShell loading tone).
- If no session → render `<Login />`.
- Else render `children`.

6. Update `src/ui/frontend/src/App.tsx`:

```tsx
import { StytchProvider } from "@stytch/react"
import { stytchClient } from "./lib/stytchClient"
import { AuthProvider } from "./contexts/AuthContext"

export default function App() {
  return (
    <BrowserRouter>
      <StytchProvider stytch={stytchClient}>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </StytchProvider>
    </BrowserRouter>
  )
}
```

Keep `StateUiProvider` and `CandidateProvider` **inside** the authenticated route tree (not wrapping login).

7. Update `src/ui/frontend/src/routes.tsx`:

- Add top-level routes **before** `NavigationShell`:

```tsx
{ path: "authenticate", element: <Authenticate /> },
{
  element: <RequireAuth><Outlet /></RequireAuth>,
  children: [
    {
      element: <NavigationShell />,
      children: [ /* existing index + job/company/... routes */ ],
    },
  ],
},
```

- Remove the old single `NavigationShell` root without `RequireAuth`.

8. Run `npm run build` from `src/ui/frontend/`.

## Stage 3: Admin route guard and navigation gating

**Done when:** Non-admin navigating to `/admin/scheduled_actions` (or any `/admin/*` path) is redirected to `/jobs/recommended`; admin users reach admin pages; Admin nav group still comes from `/api/nav_config` (server-filtered) — no duplicate Admin filtering logic in React beyond route guard.

1. Create `src/ui/frontend/src/components/AdminRoute.tsx`:

- `useAuth()`.
- If `loading` → `<p>Loading…</p>`.
- If `!isAdmin` → `<Navigate to="/jobs/recommended" replace />`.
- Else → `children`.

2. In `src/ui/frontend/src/routes.tsx`, wrap **each** admin page element:

```tsx
{ path: "admin/scheduled_actions", element: <AdminRoute><ScheduledActions /></AdminRoute> },
```

Apply to all nine existing `admin/*` routes (scheduled_actions, performance_monitor, agent_timesheets, cost_reconciliation, manage_candidates, agent_prompts, task_prompts, anthropic_ad_hoc, data_management).

3. Do **not** add client-side Admin nav filtering in `NavigationShell` — rely on `/api/nav_config` from AST-611. Route guard is defense in depth for direct URL entry.

## Stage 4: Candidate selector lock for non-admins

**Done when:** Non-admin sees candidate name in sidebar but cannot change `<select>`; `setSelectedId` does not update state or localStorage; admin retains full selector behavior.

1. In `src/ui/frontend/src/components/NavigationShell.tsx`:

- Import `useAuth`.
- In the candidate block (`candidates.length > 0`):
  - If `isAdmin`: keep existing `<select>` with `onChange`.
  - If `!isAdmin`: render `<select disabled value={selectedId ?? ""}>` with same `<option>` labels (read-only display). Do not attach `onChange`.

2. In `src/ui/frontend/src/contexts/CandidateContext.tsx`:

- Import `useAuth` inside `CandidateProvider` (provider must render under `AuthProvider` — enforced by route tree in Stage 2).
- In `setSelectedId(id)`:

```typescript
if (!isAdmin) return
```

before `_setSelectedId` / `localStorage.setItem`.

3. Run `npm run build` from `src/ui/frontend/`.

## Stage 5: Build verification and Code Complete

**Done when:** `npm run build` and `npm run lint` pass in `src/ui/frontend/`; manual happy path on staging: login → app loads → `/api/me` shows `is_admin` for Susan admin account → non-admin test user sees no Admin nav and cannot change candidate; Linear **Code Complete** comment lists Betty QA spec below.

1. From `src/ui/frontend/`: `npm run lint` then `npm run build`.

2. Post Linear comment on **AST-612** (not parent) summarizing:
   - Stytch login + Bearer `session_jwt` on all `api()` calls
   - Admin route redirect + disabled candidate select for non-admin
   - Betty test manifest (bullet list from **Betty QA spec** section below)

3. Move **AST-612** to **Code Complete** (assignee stays Katherine).

### Betty QA spec (manifest for `qa-child` — do not commit in build)

Add to `docs/ASTRAL_TEST_BIBLE.md` §7.13zza and implement:

| Case | File | Assertion |
|------|------|-----------|
| Token getter | `test_api.test.ts` | `setAuthTokenGetter` → `Authorization: Bearer <jwt>` |
| Auth context | `test_AuthContext.test.tsx` | Mock Stytch session + `/api/me` → `isAdmin` true/false |
| Login gate | `test_RequireAuth.test.tsx` | No session → Login visible; session → children |
| Admin routes | `test_AdminRoute.test.tsx` | `isAdmin: false` → redirect away |
| Nav shell | `test_NavigationShell.test.tsx` | `isAdmin: false` → combobox disabled |
| Candidate ctx | `test_CandidateContext.test.tsx` | `setSelectedId` noop when non-admin |

Update `tests/component/frontend/test-utils.tsx` with `AuthProvider` mock (`isAdmin` default `true`) so existing page tests keep passing without Stytch.

Mock `@stytch/react` in component tests (`vi.mock("@stytch/react")`) — do not call real Stytch in Vitest.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches the shared API client, new auth context, App routing shell, all nine admin routes, and candidate selection across multiple frontend modules (single layer, wide surface).

**Conf:** `Medium` — `@stytch/react` is new in this repo but AST-611/backend contract is fixed; Stytch’s prebuilt SPA pattern and `session_jwt` Bearer match shipped Flask validation.

**Risk:** `Medium` — Incorrect gating could lock out all users or expose admin routes in the UI; server-side `@require_admin` still enforces API, but login regression blocks the whole app.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §2.9 Auth decorator / React `api()` Bearer | Plan replaces stub with session JWT getter — aligns with intended pattern |
| §3 UI business logic in API | Admin nav visibility stays server-driven (`nav_config`); client only route-guards `/admin/*` |
| §3.3 Imports | No new cross-layer imports; frontend-only |
| §3.5 Naming | `AuthContext`, `RequireAuth`, `AdminRoute` match existing `CandidateContext` / provider patterns |
| §1.3 DRY | Single `setAuthTokenGetter` + `useAuth` — no duplicate admin checks beyond route + selector |

No `conf-!!-NONE` conflicts identified.

## Review (Radia)

- **Built:** pending
- **Branch:** `sub/AST-609/AST-612-react-login-and-admin-ui`
- **Scope delivered:** Stytch login gate, Bearer `session_jwt` on `api()`, `/api/me` admin gating, `AdminRoute` on `/admin/*`, non-admin candidate selector lock.
