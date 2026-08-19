<!-- linear-archive: AST-625 archived 2026-06-23 -->

## Linear archive (AST-625)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-625/session-log-off-screen-and-expired-session-detection-log-off-screen  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-624 — Log-off screen  
**Blocked by / blocks / related:** parent: AST-624

### Description

## What this implements

When the React SPA detects that a user previously had a valid Stytch session but no longer does, show a dedicated log-off screen instead of the normal Login page. The screen uses reason-specific copy for inactivity/session timeout vs API 401 server rejection, includes a visible Refresh control that reloads the page, and matches existing full-page auth styling. Detection runs in the frontend only — wire session expiry and centralized 401 handling so first-time visitors still see Login.

## Acceptance criteria

* With a valid session, using the app normally works unchanged.
* After Stytch session expiry or inactivity logout (simulated or real), the user sees the log-off screen with **inactivity/timeout** messaging — not the Stytch login widget and not an empty shell.
* After an API 401 while authenticated, the user sees the same log-off screen with **server rejection** messaging (wording distinct from the timeout case).
* The log-off screen includes copy that the user should refresh to log in again, plus a working Refresh control that reloads the page.
* After refresh, the standard Login flow appears and the user can authenticate and reach the app.
* A user who opens the site without ever having logged in still sees the existing Login page, not the log-off screen.
* No regression to magic-link/OAuth login (AST-612/613) or admin UI gating.

## Boundaries

* Does not change Stytch session duration, idle timeout policy, or Dashboard configuration.
* Does not add manual sign-out UX, account settings, or session management controls.
* Does not build MFA, password login, or broad session-refresh error handling beyond this log-off screen.
* Does not alter Flask auth decorators, `/api/me`, or admin gating from AST-611.
* No backend debug-logging requirements (UI-only feature).

## Notes for planning

Primary touchpoints: `RequireAuth.tsx`, `AuthContext.tsx`, `Login.tsx`, shared `api.ts` fetch layer, and a new log-off page/component. Follow AST-612 Stytch patterns. Track "had session" vs never-authenticated to avoid showing log-off to first-time visitors.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-624-log-off-screen`, child `sub/AST-624/AST-625-session-logoff-screen`. Created at dispatch-parent.

### Comments

#### katherine — 2026-06-14T05:42:58.053Z
**Review** — diff `origin/dev...origin/sub/AST-624/AST-625-session-logoff-screen` @ `606c0100` (+ doc `d0cf799c`)

Plan doc: [ast-625-session-logoff-screen-and-expired-session-detection.md](https://github.com/susansomerset/astral/blob/sub/AST-624/AST-625-session-logoff-screen/docs/features/foundation/ast-625-session-logoff-screen-and-expired-session-detection.md)

### fix-now
None.

### discuss
None.

### Advisory
- **`RequireAuth.tsx` L19–21** — `setLogOffReason("timeout")` during render is a side effect; plan Stage 4 prescribes it, write is idempotent, tests green. Acceptable with plan exception; move to `useEffect` only if Strict Mode ever misbehaves.
- **Server-rejection Refresh loop** — if Stytch client session survives after Refresh, user may see LogOff again until Stytch expires (no `session.revoke()` per plan). Flag for Susan UAT on AST-624.

### Solid
- All four plan stages delivered; frontend-only (§3.3).
- Had-session gating prevents log-off for first-time visitors; 401 hook gated on `getHadSession()`.
- Distinct timeout vs server-rejection copy; Refresh clears marks.
- Betty manifest §7.13zzk + five Vitest files cover routing matrix.

#### betty — 2026-06-14T05:39:50.987Z
## QA test manifest (AST-625)

**Publish ref:** `origin/sub/AST-624/AST-625-session-logoff-screen` @ `606c0100` (`merge-tests(AST-625): origin/tests 675534ba`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `31e764e74252fcddb0b0972e6dfadb598ad873b1` — see **§7.13zzk**

**Classification:** new Vitest coverage for frontend-only session log-off gate (extends AST-612 patterns). No Python tests; no backend changes.

### Run (numbered)

From `src/ui/frontend/`:

1. `npm run test:component -- ../tests/component/frontend/lib/test_sessionAuthMark.test.ts`
2. `npm run test:component -- ../tests/component/frontend/lib/test_api.test.ts`
3. `npm run test:component -- ../tests/component/frontend/contexts/test_AuthContext.test.tsx`
4. `npm run test:component -- ../tests/component/frontend/components/test_RequireAuth.test.tsx`
5. `npm run test:component -- ../tests/component/frontend/components/test_LogOffScreen.test.tsx`

Or single narrowed run (§7.13zzk):

6. `npm run test:component -- ../tests/component/frontend/lib/test_sessionAuthMark.test.ts ../tests/component/frontend/lib/test_api.test.ts ../tests/component/frontend/contexts/test_AuthContext.test.tsx ../tests/component/frontend/components/test_RequireAuth.test.tsx ../tests/component/frontend/components/test_LogOffScreen.test.tsx`

### Coverage matrix

| AC area | Test |
| --- | --- |
| First-time visitor → Login (not log-off) | `test_RequireAuth` — no session, no had-session |
| Session loss after auth → timeout log-off | `test_RequireAuth` — had-session + null session |
| API 401 while authenticated → server-rejection | `test_api` 401 + handler; `test_AuthContext` `/api/me` 401; `test_RequireAuth` with reason set |
| Reason-specific copy + Refresh clears marks | `test_LogOffScreen` |
| Valid session → children unchanged | `test_RequireAuth` — session present |
| `sessionStorage` helpers | `test_sessionAuthMark` |

### Regression spot-check (after manifest green)

7. `npm run test:component -- ../tests/component/frontend/pages/test_Login.test.tsx ../tests/component/frontend/components/test_AdminRoute.test.tsx`

— Betty

#### katherine — 2026-06-14T05:34:37.664Z
Plan doc: [ast-625-session-logoff-screen-and-expired-session-detection.md](https://github.com/susansomerset/astral/blob/sub/AST-624/AST-625-session-logoff-screen/docs/features/foundation/ast-625-session-logoff-screen-and-expired-session-detection.md)

**Approach:** Tab-scoped `sessionStorage` marks (`had session` + log-off reason `timeout` | `server-rejection`). `RequireAuth` routes to new `LogOffScreen` before `Login` when a reason is set or Stytch session drops after auth. `api.ts` centralizes 401 → `server-rejection` when had-session is set. Refresh clears marks and reloads so Login appears post-refresh.

**Self-assessment**
- **Scope:** `scope-Single-Component` — five frontend auth-gate files, no backend changes.
- **Conf:** `conf-high` — extends AST-612 Stytch gate patterns with explicit routing and copy.
- **Risk:** `risk-Medium` — auth routing mistakes could block protected routes or show LogOff to first-time visitors.

Four stages: (1) `sessionAuthMark` + `api` 401 hook, (2) `LogOffScreen`, (3) `AuthContext` marking/re-render, (4) `RequireAuth` routing + lint/build.

---

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

## Resolution (Katherine)

**Date:** 2026-06-14  
**Review ref:** `d0cf799c` on `origin/sub/AST-624/AST-625-session-logoff-screen`

Radia posted **fix-now: none**, **discuss: none**. Two **advisory** items accepted per plan (render-time `setLogOffReason` per Stage 4; no `session.revoke()` per plan decision). No product or test changes in this resolve pass.

**§9a dry-run:** publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-624-log-off-screen`.

**Status:** → **User Testing** (implementer assignee unchanged).

## Bug: AST-1433 — Expired-session deeplink refresh 404

### As-is

When the Stytch session has expired, a hard refresh or paste of an in-app path (e.g. `/candidate/backstory` on staging) returns a white page whose body is `{"error":"Not found"}`. The SPA never boots, so neither Login nor `LogOffScreen` runs.

The same JSON 404 happens on refresh of any `/candidate/…` **SPA** route even with a live session — Flask does not inspect the session. Expired-session is the UAT scenario (deeplink refresh after idle), not a separate auth branch.

### To-be

An expired or missing session on any in-app URL lands on an auth page — Login, or the existing log-off screen if this tab had a session — never a JSON 404. After they authenticate they can use the app again. Returning to the original path after sign-in is nicer; **not required** for this cut (`Authenticate` may keep navigating to `/`).

### Repro

1. Staging (`https://astral-staging.up.railway.app`) or Flask serving `frontend/dist/` (`:5001`).
2. While on a candidate SPA route (literal example: `/candidate/backstory`), let the Stytch session expire **or** open that path in a tab with no session.
3. Hard-refresh, or paste the URL into the address bar (document GET, not in-app React navigation).
4. **Broken:** white page, body exactly `{"error":"Not found"}`. **Expected:** SPA `index.html` loads; `RequireAuth` shows Login (no had-session) or `LogOffScreen` (had-session in this tab).

Same 404 without expiry: refresh `/candidate/backstory` while still signed in. Client-side nav to that path still works; only the document request fails.

### Root cause

AST-625’s gate (`RequireAuth` / `LogOffScreen` / `sessionAuthMark`) never runs because Flask answers the **document** request before the SPA loads.

`src/ui/server.py` `serve_react` (AST-1117 print-HTML guard) returns JSON 404 for **every** path `candidate` or `candidate/…`:

```python
if path == "candidate" or path.startswith("candidate/"):
    return jsonify({"error": "Not found"}), 404
```

That body is the white page. AST-1117 needed it so unmatched `/candidate/resume/…` and `/candidate/cover/…` would not get `index.html` (React `*` then `<Navigate to="/jobs/recommended">`). The guard is too broad: React client routes live under the same prefix (`routes.tsx`: `candidate/backstory`, `candidate/profile`, …). Print HTML is the only Flask owner of `/candidate` (`resume_html_bp` in `api_resume_html.py`); those blueprint routes already match first when the URL is a real print path.

Local Vite compounds it: `vite.config.ts` proxies the entire `'/candidate'` prefix to Flask, so `:5173/candidate/backstory` hits the same 404 instead of the Vite SPA.

`ASTRAL_CODE_RULES.md` §3.5: Flask catch-all serves `index.html` for any non-API, non-file path. The AST-1117 blanket is the exception that broke candidate SPA refreshes.

### Proposed change

No frontend auth-gate edits. Once `index.html` loads, AST-625 Stage 4 already routes Login vs LogOff vs children. Do not add return-to-original-path storage; Stytch still redirects to `/authenticate`, which still `navigate("/", { replace: true })`.

**1. `src/ui/server.py` `serve_react`** — narrow the JSON 404 to print-HTML prefixes only (`resume_html_bp`: `/candidate/resume…`, `/candidate/cover…`). SPA `/candidate/backstory` (and siblings) fall through to `index.html`.

Replace the current `candidate` / `candidate/` block with:

```python
    # Print HTML (resume_html_bp). Blueprint matches first for real print
    # routes; unmatched print-shaped paths must not SPA-fallback (AST-1117:
    # React `*` → /jobs/recommended). Candidate SPA routes share /candidate/.
    if (
        path == "candidate/resume"
        or path.startswith("candidate/resume/")
        or path == "candidate/cover"
        or path.startswith("candidate/cover/")
    ):
        return jsonify({"error": "Not found"}), 404
```

Update the function docstring: it currently says “Never steal `/candidate/*` HTML routes” — that must mean **print** HTML only, not the candidate SPA section.

Keep the existing static-file then `index.html` fallback unchanged. Do not auth-gate document serving (`@require_auth` stays on the print blueprint and `/api/*` only — AST-611 / AST-625 frozen Flask auth).

**2. `src/ui/frontend/vite.config.ts`** — stop proxying the whole `/candidate` prefix. Proxy only the print HTML prefixes so local UAT Print / Materials still hit Flask, while `/candidate/backstory` stays on Vite:

```ts
    proxy: {
      '/api': 'http://localhost:5001',
      // AST-1117 / AST-1433: print HTML only — not candidate SPA routes.
      '/candidate/resume': 'http://localhost:5001',
      '/candidate/cover': 'http://localhost:5001',
    },
```

Vite prefix-matches those keys, so `/candidate/resume/base`, `/candidate/resume/<job_id>`, and `/candidate/cover/<job_id>` still proxy (JAR / Materials `api()` fetches and `window.open` included).

**3. Do not change** `RequireAuth.tsx`, `LogOffScreen.tsx`, `sessionAuthMark.ts`, `AuthContext.tsx`, `api.ts`, `Login.tsx`, `Authenticate.tsx`, `routes.tsx`, `api_resume_html.py`, or Stytch Dashboard / session duration.

**4. Compile:** `cd src/ui/frontend && npm run build` (Vite config) and `python3 -m py_compile src/ui/server.py`.

⚠️ **Decision:** Narrow the AST-1117 guard by **print path prefix**, not an allowlist of SPA routes copied from `routes.tsx` (new candidate pages would 404 again). Rejected: redirect-to-login in Flask (session-blind document 404 is the bug; valid-session refresh must also get the SPA). Rejected: return-URL after authenticate (AC optional; extra Stytch/Dashboard surface).

### Blast radius

- **Touches:** `src/ui/server.py` `serve_react`; `src/ui/frontend/vite.config.ts` `server.proxy`.
- **Print HTML (must keep working):** `resume_html_bp` (`/candidate/resume/base`, `/candidate/resume/<job_id>`, `/candidate/cover/<job_id>`); JAR / Materials open those URLs. Blueprint still wins when the route matches. Unmatched print-shaped paths still JSON 404, not recommended-jobs SPA.
- **SPA candidate section:** every `routes.tsx` `candidate/…` child (profile, backstory, intake, …) document GET now receives `index.html` — same as `/jobs/recommended` today.
- **Tests (Betty / qa-fix — engineer must not edit `tests/`):** `tests/component/ui/test_server.py` `TestAst1117CandidateSpaGuard` currently expects JSON 404 for `/candidate/not-a-real-html-route` and `/candidate`; those become SPA 200 after this change. `TestAst1117ViteCandidateProxy` asserts `'/candidate': 'http://localhost:5001'` and must assert the resume/cover keys instead. Bible `docs/test-bible/ui/server.md` AST-1117 row (“404 JSON for unmatched `candidate/*`”) is the same over-broad contract. New cases that should exist: GET `/candidate/backstory` → 200 `index.html`; print prefixes without a blueprint match still 404 JSON; Vite still proxies `/candidate/resume` and `/candidate/cover`.
- **AST-625 tests:** `test_RequireAuth` / `test_LogOffScreen` / `test_sessionAuthMark` unchanged — product files they cover are not edited.
- **Siblings:** AST-1117 print delivery; AST-612/613 login + `/authenticate`; no other `/candidate` Flask blueprint.

### What must still hold

- AST-625 AC: valid session → app unchanged; timeout / 401 → log-off with distinct copy + Refresh; first-time visitor → Login not LogOff; no Stytch duration / Dashboard / manual sign-out; no Flask `@require_auth` / `/api/me` shape change.
- AST-1117 AC: Print Resume / Print Cover Letter still open Flask HTML, not `/jobs/recommended`.
- §3.5: non-API, non-file, non-print document paths serve `index.html`.
- Vite local: `/api` and print HTML still proxy to `:5001`; candidate SPA pages are Vite-owned again.
- After Refresh on LogOff, Login appears (marks cleared) and the user can authenticate and reach the app.

### Board (AST-1433)

**Joan CANON: OK** — Narrowing AST-1117 `serve_react` / Vite proxy from all `/candidate/*` to print-HTML prefixes restores §3.5 (Flask catch-all serves `index.html` for non-API, non-file paths). `astral.idioms.require-auth-on-protected-endpoints` is API-scoped; document serving stays session-blind. `astral.standards.no-hardcoded-sets` does not bind print URL prefixes. No `canon/patterns/**` match. No statute/pattern amend; no Archie fork.

**Betty TESTS: REVISE** — `docs/test-bible/ui/server.md` — broken test — `TestAst1117CandidateSpaGuard` / `TestAst1117ViteCandidateProxy` assert blanket `/candidate` 404+proxy; repro GET `/candidate/backstory` → 200 `index.html` uncovered. Test hole filed as a sibling gap child (orphaned-branch rule: not qa-fix inline on this ticket). Test-tree delivery is AST-1435 (`test(AST-1435)` / `merge-tests(AST-1435)`); this ticket is docs-acceptance for merge-child.

## Radia review (AST-1433)

`[code-rubric] PROCEED (Commit: 9103d105) narrow print guard SPA`

**Overall: CLEAN.** Diff `origin/ftr/AST-1424-refresh-from-deeplink-error...origin/sub/AST-1424/AST-1433-expired-session-deeplink-refresh-404` @ `9103d105`. Full-set C1–C7: no fix-now, no discuss.

**Plan adherence:** `serve_react` + Vite proxy narrowed to print prefixes only; no auth-gate edits; AST-1117 unmatched print paths still JSON 404; candidate SPA document GET → `index.html`.

**[bug-repro]:** `TestAst1117CandidateSpaGuard::test_candidate_backstory_serves_index` — 200, `index.html` marker, `not resp.is_json`. Would fail pre-fix. OK.

**What must still hold:** AST-625 AC, AST-1117 print HTML, §3.5 catch-all, Vite proxy split, LogOff Refresh — all OK (no auth/session-mark edits).

**Advisory:** stacked `test(AST-1430)` / `test(AST-1431)` commits on this publish ref (foreign `origin/tests` pile-up); `/candidate` exact path now SPA `index.html` (plan + AST-1435 tests expect this).
