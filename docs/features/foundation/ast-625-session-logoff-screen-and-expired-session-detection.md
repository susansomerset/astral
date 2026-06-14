# AST-625 — Session log-off screen and expired-session detection (Log-off screen)

- **Linear (this ticket):** [AST-625](https://linear.app/astralcareermatch/issue/AST-625/session-log-off-screen-and-expired-session-detection-log-off-screen)
- **Parent:** [AST-624](https://linear.app/astralcareermatch/issue/AST-624/log-off-screen)
- **Publish ref:** `origin/sub/AST-624/AST-625-session-logoff-screen`
- **Depends on:** [AST-612](https://linear.app/astralcareermatch/issue/AST-612/react-stytch-login-and-admin-ui-gating-use-stytch-for-user) / [AST-613](https://linear.app/astralcareermatch/issue/AST-613/stytch-login-redirect-urls) (Stytch login, `RequireAuth`, `AuthContext`, `api.ts` token injection) — already on `origin/dev`.

## Summary

When a user **previously had** a valid Stytch session but no longer does (idle/session expiry) or the Flask API returns **401** while they are using the app, show a dedicated **log-off screen** with reason-specific copy and a working **Refresh** control — instead of dropping them straight into the Stytch login widget. First-time visitors (never authenticated in this browser tab) continue to see the existing `Login` page unchanged.

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/ui/frontend/src/lib/sessionAuthMark.ts` | **New** — `sessionStorage` helpers for had-session + log-off reason | frontend only |
| `src/ui/frontend/src/lib/api.ts` | Centralized 401 detection + unauthorized callback | frontend only |
| `src/ui/frontend/src/contexts/AuthContext.tsx` | Mark had-session; register unauthorized re-render | frontend only |
| `src/ui/frontend/src/components/RequireAuth.tsx` | Route among `LogOffScreen`, `Login`, children | frontend only |
| `src/ui/frontend/src/pages/LogOffScreen.tsx` | **New** — full-page log-off UI | frontend only |
| `src/utils/auth.py`, `src/ui/api/*`, Stytch Dashboard config | **Read-only** | do not modify |

⚠️ **Decision:** Track **“had session”** and **log-off reason** in **`sessionStorage`** (not `localStorage`) via a tiny dedicated module. Tab-scoped storage matches “this browsing session had auth”; clearing both keys on Refresh guarantees the post-refresh **Login** flow per AC without touching Stytch SDK revoke APIs (out of scope).

⚠️ **Decision:** Two log-off reasons only — **`timeout`** (Stytch session gone while had-session flag set) and **`server-rejection`** (any `api()` response with HTTP 401 while had-session flag set). No other error codes or retry logic in this ticket.

⚠️ **Decision:** **`LogOffScreen` layout** mirrors `Login.tsx` — same outer `div.content` flex centering and padding. No new CSS file; reuse existing auth shell classes. Copy is inline in the component (two reason branches), not config-driven (UI-only, no server endpoint).

⚠️ **Decision:** On **401**, persist `server-rejection` in `sessionStorage` and bump React state so `RequireAuth` re-renders **even if Stytch still reports a client session** (server rejected the JWT/cookie). Do **not** call `stytch.session.revoke()` — out of scope; Refresh + Login is the recovery path.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| Stytch session duration / idle policy / Dashboard changes | Susan / ops |
| Manual sign-out UX, MFA, password login | Future |
| Flask `@require_auth`, `/api/me` shape changes | **AST-611** (frozen) |
| Committing under `tests/` or `docs/ASTRAL_TEST_BIBLE.md` | **Betty** (`qa-child`) — engineer pre-commit hook blocks |
| Broad non-401 API error handling | Future |

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/ui/frontend/src/lib/sessionAuthMark.ts` | **New** — `sessionStorage` keys + getters/setters/clear | frontend | Katherine (build) |
| `src/ui/frontend/src/lib/api.ts` | 401 branch; `setUnauthorizedHandler` | frontend | Katherine (build) |
| `src/ui/frontend/src/contexts/AuthContext.tsx` | Mark had-session; wire unauthorized handler | frontend | Katherine (build) |
| `src/ui/frontend/src/components/RequireAuth.tsx` | Log-off vs Login routing | frontend | Katherine (build) |
| `src/ui/frontend/src/pages/LogOffScreen.tsx` | **New** — reason copy + Refresh button | frontend | Katherine (build) |
| `tests/component/frontend/lib/test_sessionAuthMark.test.ts` | **New** — storage helpers | tests | Betty (qa-child) |
| `tests/component/frontend/lib/test_api.test.ts` | 401 → handler + reason flag | tests | Betty (qa-child) |
| `tests/component/frontend/components/test_RequireAuth.test.tsx` | Log-off vs Login matrix | tests | Betty (qa-child) |
| `tests/component/frontend/components/test_LogOffScreen.test.tsx` | **New** — copy + Refresh | tests | Betty (qa-child) |
| `tests/component/frontend/contexts/test_AuthContext.test.tsx` | Had-session marking | tests | Betty (qa-child) |
| `tests/component/frontend/stytchMock.tsx` | Reset `sessionStorage` in `resetStytchTestState` if needed | tests | Betty (qa-child) |
| `docs/ASTRAL_TEST_BIBLE.md` | AST-625 manifest rows | bible | Betty (qa-child) |

## Stage 1: Session marks module and `api.ts` 401 hook

**Done when:** `sessionAuthMark.ts` exports stable helpers; `api.ts` calls the unauthorized handler on 401 when the had-session flag is set; `npm run build` in `src/ui/frontend/` still passes; no UI routing changes yet.

1. Create `src/ui/frontend/src/lib/sessionAuthMark.ts` with these **exact** exports and keys:

```typescript
const HAD_SESSION_KEY = "astral-had-stytch-session"
const LOGOFF_REASON_KEY = "astral-logoff-reason"

export type LogOffReason = "timeout" | "server-rejection"

export function markHadSession(): void {
  try { sessionStorage.setItem(HAD_SESSION_KEY, "1") } catch { /* private mode */ }
}

export function getHadSession(): boolean {
  try { return sessionStorage.getItem(HAD_SESSION_KEY) === "1" } catch { return false }
}

export function getLogOffReason(): LogOffReason | null {
  try {
    const v = sessionStorage.getItem(LOGOFF_REASON_KEY)
    return v === "timeout" || v === "server-rejection" ? v : null
  } catch { return null }
}

export function setLogOffReason(reason: LogOffReason): void {
  try { sessionStorage.setItem(LOGOFF_REASON_KEY, reason) } catch { /* private mode */ }
}

/** Clears both keys — call before Refresh reload so Login appears after reload. */
export function clearSessionAuthMarks(): void {
  try {
    sessionStorage.removeItem(HAD_SESSION_KEY)
    sessionStorage.removeItem(LOGOFF_REASON_KEY)
  } catch { /* private mode */ }
}
```

2. In `src/ui/frontend/src/lib/api.ts`, add after `setAuthTokenGetter`:

```typescript
type UnauthorizedHandler = () => void
let unauthorizedHandler: UnauthorizedHandler | null = null

/** Registered by AuthContext — triggers re-render when api() sees 401. */
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  unauthorizedHandler = handler
}
```

3. Import `getHadSession`, `setLogOffReason` from `./sessionAuthMark` at top of `api.ts`.

4. Change the `api()` function body to capture the response, inspect status, then return it:

```typescript
async function api(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers)
  const token = authTokenGetter()
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }
  const response = await fetch(path, { ...options, headers, credentials: "include" })
  if (response.status === 401 && getHadSession()) {
    setLogOffReason("server-rejection")
    unauthorizedHandler?.()
  }
  return response
}
```

5. From `src/ui/frontend/`: run `npm run build`.

## Stage 2: `LogOffScreen` page

**Done when:** `LogOffScreen.tsx` renders reason-specific copy, a Refresh button that clears marks and reloads, and uses the same outer layout as `Login.tsx`; `npm run build` passes.

1. Create `src/ui/frontend/src/pages/LogOffScreen.tsx`:

```typescript
import type { LogOffReason } from "../lib/sessionAuthMark"
import { clearSessionAuthMarks } from "../lib/sessionAuthMark"

const COPY: Record<LogOffReason, { title: string; body: string }> = {
  timeout: {
    title: "You were signed out",
    body: "Your session expired after a period of inactivity. Refresh the page to sign in again and return to Astral.",
  },
  "server-rejection": {
    title: "Your session is no longer valid",
    body: "The server rejected your request while you were using the app. Refresh the page to sign in again and return to Astral.",
  },
}

export default function LogOffScreen({ reason }: { reason: LogOffReason }) {
  const { title, body } = COPY[reason]

  function handleRefresh() {
    clearSessionAuthMarks()
    window.location.reload()
  }

  return (
    <div
      className="content"
      style={{ display: "flex", justifyContent: "center", padding: "2rem" }}
      data-testid="logoff-screen"
    >
      <div style={{ maxWidth: "28rem", textAlign: "center" }}>
        <h1 style={{ marginBottom: "1rem" }}>{title}</h1>
        <p style={{ marginBottom: "1.5rem", color: "var(--text-secondary)" }}>{body}</p>
        <button type="button" onClick={handleRefresh} data-testid="logoff-refresh">
          Refresh
        </button>
      </div>
    </div>
  )
}
```

2. Do **not** import or render `StytchLogin` on this page.

3. From `src/ui/frontend/`: run `npm run build`.

## Stage 3: `AuthContext` had-session marking and unauthorized re-render

**Done when:** Successful Stytch session marks had-session; 401 from `api()` forces context consumers to re-render; existing admin/`/api/me` behavior unchanged when session is valid.

1. In `src/ui/frontend/src/contexts/AuthContext.tsx`, import `markHadSession`, `setLogOffReason`, `getHadSession` from `../lib/sessionAuthMark` and `setUnauthorizedHandler` from `../lib/api`.

2. Add state inside `AuthProvider`:

```typescript
const [, setAuthEpoch] = useState(0)
```

3. Add a `useEffect` that registers the unauthorized handler (runs once):

```typescript
useEffect(() => {
  setUnauthorizedHandler(() => setAuthEpoch((n) => n + 1))
  return () => setUnauthorizedHandler(null)
}, [])
```

4. In the existing `useEffect` that depends on `[session, sessionJwt, loadMe]`, when `session` is truthy, call `markHadSession()` **before** `loadMe()`.

5. In `loadMe`, when `!r.ok` and `r.status === 401`, call `setLogOffReason("server-rejection")` and `setAuthEpoch((n) => n + 1)` before `setUser(null)` and return. (Covers `/api/me` 401; `api.ts` also handles other endpoints.)

6. Do **not** add new fields to `AuthCtx` unless a consumer needs them — `RequireAuth` reads `sessionStorage` directly for log-off reason; `authEpoch` bump is only to force subtree re-render after 401.

7. From `src/ui/frontend/`: run `npm run build`.

## Stage 4: `RequireAuth` routing (log-off vs login vs children)

**Done when:** Matrix matches acceptance criteria — first visit → Login; session loss after auth → LogOff timeout; 401 while using app → LogOff server-rejection; valid session → children unchanged.

1. In `src/ui/frontend/src/components/RequireAuth.tsx`, import `LogOffScreen`, and from `../lib/sessionAuthMark`: `getLogOffReason`, `getHadSession`, `setLogOffReason`.

2. Replace the component body with this logic (preserve `Loading…` for `!isInitialized`):

```typescript
if (!isInitialized) {
  return <p>Loading…</p>
}

let logOffReason = getLogOffReason()
if (!logOffReason && !session && getHadSession()) {
  setLogOffReason("timeout")
  logOffReason = "timeout"
}
if (logOffReason) {
  return <LogOffScreen reason={logOffReason} />
}
if (!session) {
  return <Login />
}
return children
```

3. Do **not** change `routes.tsx` — `RequireAuth` remains the gate for authenticated shell routes; `/authenticate` stays outside it (AST-612).

4. From `src/ui/frontend/`: run `npm run build` and `npm run lint` (if defined in `package.json` scripts).

## Self-Assessment

**Scope:** `scope-Single-Component` — Touches five frontend files in the auth gate layer (`sessionAuthMark`, `api`, `AuthContext`, `RequireAuth`, `LogOffScreen`) with no backend or config changes.

**Conf:** `conf-high` — Extends established AST-612 Stytch patterns (`RequireAuth` → full-page auth states, `api()` wrapper, `sessionStorage` for tab-scoped UX) with explicit routing rules and copy.

**Risk:** `risk-Medium` — Incorrect had-session or 401 routing could show Login to returning users who expect explanation, or show LogOff to first-time visitors; auth gate regressions would block all protected routes.

## Self-review against ASTRAL_CODE_RULES

| Rule | Status |
|------|--------|
| §1.3 DRY | Pass — single `sessionAuthMark` module; no duplicated storage key strings |
| §2.1 config | Pass — no new config blocks; copy inline in component (UI-only ticket) |
| §2.4 batch | N/A |
| §2.6 state machine | N/A |
| §2.9 auth decorator | Pass — no Flask changes; frontend continues Bearer + cookies via `api.ts` |
| §3.3 imports | Pass — frontend-only imports |
| §3.5 UI stack | Pass — React/Vite component; matches Login layout; no new routes |

No conflicts — plan is implementable as written.

## Review (Radia)

- **Ref:** `606c0100` on `origin/sub/AST-624/AST-625-session-logoff-screen` (diff `origin/dev...origin/sub/AST-624/AST-625-session-logoff-screen`)
- **Built:** Katherine — stages 1–4 (sessionAuthMark, api 401 hook, LogOffScreen, AuthContext, RequireAuth)

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | All four stages match plan; acceptance matrix covered by component tests |
| Layer contract (§3.3) | Frontend-only; no Flask, config, or backend debug surfaces touched |
| Auth gate routing | `RequireAuth` correctly orders LogOff → Login → children; first-time visitors skip log-off |
| 401 centralization | `api()` sets `server-rejection` + handler only when `getHadSession()`; `/api/me` path duplicated safely in `loadMe` |
| UX copy | Distinct timeout vs server-rejection messaging; Refresh clears marks before reload |
| Tests | Manifest in bible §7.13zzk; five focused Vitest files + `stytchMock` sessionStorage reset |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | `RequireAuth.tsx` L19–21 | `setLogOffReason("timeout")` runs during render (side effect). Plan Stage 4 prescribes this pattern; sessionStorage write is idempotent and tests pass — acceptable with plan exception. If Strict Mode double-invoke ever surfaces duplicate telemetry, move to `useEffect`. |
| **advisory** | Plan decision (no revoke) | After server-rejection **Refresh**, if Stytch client session still exists, user may loop LogOff → `/api/me` 401 → LogOff until Stytch session expires. Explicit out-of-scope (`stytch.session.revoke()`); Susan UAT should confirm recovery path is acceptable. |

**fix-now:** none  
**discuss:** none

### Recommended actions

| Action | Owner |
|--------|-------|
| Proceed to `resolve-child` (no code changes required from review) | Katherine |
| UAT: simulate timeout + 401 paths; confirm Refresh lands on Login for first-time tab after clear | Susan (AST-624) |
