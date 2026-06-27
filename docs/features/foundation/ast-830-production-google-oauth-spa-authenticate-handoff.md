# AST-830 — Production Google OAuth SPA authenticate handoff

- **Linear (this ticket):** [AST-830](https://linear.app/astralcareermatch/issue/AST-830/production-google-oauth-spa-authenticate-handoff-using-google-to-login-on)
- **Parent:** [AST-829](https://linear.app/astralcareermatch/issue/AST-829/using-google-to-login-on-production-doesnt-work)
- **Publish ref:** `origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff`
- **Sibling (backend — out of scope):** [AST-831](https://linear.app/astralcareermatch/issue/AST-831/backend-stytch-live-project-session-jwt-validation) — Flask JWT validation / `session_not_found` on `/api/me`

## Summary

Production Google OAuth on `https://astral.up.railway.app` fails after the Google redirect: Stytch's live-project activity log shows **SessionsGet** succeeding, but the browser lands on Stytch's **Login Error** page instead of Astral's authenticated shell. AST-612/613 shipped the `/authenticate` route and redirect helper; the handoff page still calls `stytch.authenticateByUrl()` fire-and-forget with no initialization gate, no single-flight guard, and no error handling — so OAuth token exchange failures (including double-invoke under React StrictMode) surface as Stytch's hosted error UI instead of an in-app recovery path. This ticket hardens the SPA OAuth/magic-link callback, documents production live-project env + Dashboard settings, and restores end-to-end Google sign-in on production without changing Flask auth (AST-831) or session timeout behavior (AST-624/625).

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/ui/frontend/src/lib/stytchAuthenticateHandoff.ts` | **New** — async `/authenticate` handoff helper | frontend only |
| `src/ui/frontend/src/pages/Authenticate.tsx` | Harden callback page (init gate, single-flight, error UI) | frontend only |
| `env.example` | Production **live** Stytch + Railway checklist | docs |
| `src/ui/frontend/src/pages/Login.tsx`, `stytchRedirect.ts`, `stytchClient.ts` | **Read-only** unless Stage 1 repro proves redirect wiring bug | frontend |
| `src/ui/frontend/src/contexts/AuthContext.tsx` | **Read-only** — already wires Bearer from `session.getTokens()` | frontend |
| `src/utils/auth.py`, `src/external/stytch.py` | **Out of scope** — **AST-831** | do not modify |
| `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, `docs/test-bible/**` | **Betty** (`qa-child`) | do not commit |

⚠️ **Decision:** Keep OAuth/magic-link handoff logic in a dedicated `stytchAuthenticateHandoff.ts` helper (parallel to `stytchRedirect.ts`) so Betty can unit-test outcomes without mounting the full page. Do **not** add a backend redirect-url endpoint.

⚠️ **Decision:** On handoff failure, render an **in-app** error state on `/authenticate` with a "Try again" link to `/` (which shows `Login` via `RequireAuth`). Do **not** leave the user on Stytch's hosted Login Error page or an infinite "Completing sign-in…" spinner.

⚠️ **Decision:** Use a `useRef` single-flight guard so `authenticateByUrl` runs **at most once** per page load. React `StrictMode` double-mount and effect re-runs must not consume the same OAuth token twice (second call → Stytch auth failure → Login Error).

⚠️ **Decision:** If handoff succeeds (Stytch client session established) but `GET /api/me` returns **401** with `session_not_found` in server logs, **stop** and comment on parent **AST-829** tagging **AST-831** — do not weaken Bearer validation or patch Flask from this ticket.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| Flask `@require_auth`, Stytch Python `authenticate_session_jwt`, Railway runtime `STYTCH_*` alignment | **AST-831** |
| Session duration, idle timeout, log-off screen | **AST-624** / **AST-625** |
| New OAuth providers | — |
| Component tests / bible rows | **Betty** |
| Stytch Dashboard clicks (Susan ops) | Susan — Stage 3 checklist |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/stytchAuthenticateHandoff.ts` | **New** — `completeAuthenticateFromUrl()` | frontend |
| `src/ui/frontend/src/pages/Authenticate.tsx` | Init gate, await handoff, error UI, navigate on success | frontend |
| `env.example` | Production live-project Stytch + Railway block | docs |
| `tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts` | Betty — handoff outcomes | tests (Betty) |
| `tests/component/frontend/pages/test_Authenticate.test.tsx` | Betty — page states | tests (Betty) |

## Stage 1: Authenticate handoff helper and hardened callback page

**Done when:** Visiting `/authenticate` with a mocked successful `authenticateByUrl` resolves to navigation home; with no URL token resolves to navigation home (Login); with rejected promise shows in-app error (not Stytch page); `npm run lint` and `npm run build` pass in `src/ui/frontend/`.

1. Create `src/ui/frontend/src/lib/stytchAuthenticateHandoff.ts`:

```typescript
/** Outcomes from /authenticate URL token exchange (AST-830). */
export type AuthenticateHandoffOutcome =
  | "success"
  | "no-token"
  | "unsupported-token"
  | "error"

export interface AuthenticateHandoffResult {
  outcome: AuthenticateHandoffOutcome
  /** Stytch token type when parseAuthenticateUrl found a token (oauth | magic_links | …). */
  tokenType?: string
  /** Human-readable message for error / unsupported-token UI. */
  message?: string
}

/** Minimal Stytch client surface used by Authenticate.tsx — matches @stytch/react useStytch(). */
export interface StytchAuthenticateClient {
  session: {
    parseAuthenticateUrl?: () => {
      token: string
      tokenType: string
      handled: boolean
    } | null
  }
  authenticateByUrl: (opts: {
    session_duration_minutes: number
  }) => Promise<{
    handled: boolean
    tokenType?: string
    token?: string
  } | null>
}

const SESSION_DURATION_MINUTES = 60

/**
 * Exchange OAuth / magic-link token from current URL params for a Stytch client session.
 * Call once per /authenticate page load.
 */
export async function completeAuthenticateFromUrl(
  stytch: StytchAuthenticateClient,
): Promise<AuthenticateHandoffResult> {
  const parsed = stytch.session.parseAuthenticateUrl?.() ?? null
  if (!parsed) {
    return { outcome: "no-token" }
  }
  if (!parsed.handled) {
    return {
      outcome: "unsupported-token",
      tokenType: parsed.tokenType,
      message: `Sign-in link type "${parsed.tokenType}" is not supported here.`,
    }
  }
  try {
    const result = await stytch.authenticateByUrl({
      session_duration_minutes: SESSION_DURATION_MINUTES,
    })
    if (result?.handled) {
      return { outcome: "success", tokenType: result.tokenType ?? parsed.tokenType }
    }
    return {
      outcome: "error",
      tokenType: parsed.tokenType,
      message: "Sign-in could not be completed.",
    }
  } catch (err) {
    const msg =
      err instanceof Error ? err.message : "Sign-in could not be completed."
    return { outcome: "error", tokenType: parsed.tokenType, message: msg }
  }
}
```

2. Replace `src/ui/frontend/src/pages/Authenticate.tsx` entirely with:

- Imports: `useEffect`, `useRef`, `useState` from React; `Link`, `useNavigate` from `react-router-dom`; `useStytch`, `useStytchSession` from `@stytch/react`; `completeAuthenticateFromUrl` from `../lib/stytchAuthenticateHandoff`.
- State: `phase: "loading" | "handoff" | "error"` (default `"loading"`), `errorMessage: string | null`.
- `const handoffStarted = useRef(false)` — single-flight guard.
- `const { session, isInitialized } = useStytchSession()`; `const stytch = useStytch()`; `const navigate = useNavigate()`.
- `useEffect` body (deps: `[stytch, session, isInitialized, navigate]`):
  1. If `!isInitialized` → return (keep `phase === "loading"`).
  2. If `session` → `navigate("/", { replace: true })`; return.
  3. If `handoffStarted.current` → return.
  4. Set `handoffStarted.current = true`, `setPhase("handoff")`.
  5. `void (async () => { const result = await completeAuthenticateFromUrl(stytch); ... })()`:
     - `"success"` → `navigate("/", { replace: true })`
     - `"no-token"` → `navigate("/", { replace: true })` (RequireAuth shows Login)
     - `"unsupported-token"` or `"error"` → `setPhase("error")`, `setErrorMessage(result.message ?? "Sign-in could not be completed.")`, and strip query params with `window.history.replaceState({}, document.title, window.location.pathname)` so refresh does not retry a consumed token.
- Render:
  - `phase === "loading"` or `"handoff"` → `<p>Completing sign-in…</p>`
  - `phase === "error"` → centered `content` div with `<p role="alert">{errorMessage}</p>` and `<Link to="/">Try again</Link>`

3. From `src/ui/frontend/`: run `npm run lint` then `npm run build`.

4. **Read-only verification** (no edits unless mismatch found): confirm `Login.tsx` still passes `getStytchAuthenticateRedirectUrl()` to all four redirect fields and that production Railway value is documented as `https://astral.up.railway.app/authenticate` in Stage 3. If `Login.tsx` redirect differs from browser origin at runtime, stop and comment on **AST-830** — PKCE `code_verifier` in localStorage is origin-scoped.

## Stage 2: Production live-project env documentation

**Done when:** `env.example` includes an explicit **production live** Stytch block naming `https://astral.up.railway.app` and `project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a`; no product code changed in this stage.

1. In `env.example`, after the existing Stytch Dashboard comment block (AST-613), append:

```
# --- Production live project (AST-829 / AST-830) ---
# Host: https://astral.up.railway.app
# Stytch live project: project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a
# Railway production (frontend build service running scripts/build_railway.sh):
#   VITE_STYTCH_PUBLIC_TOKEN=public-token-live-…   (must pair with live project above)
#   VITE_STYTCH_REDIRECT_URL=https://astral.up.railway.app/authenticate
# Railway production (backend runtime — configured in AST-831, listed here for host-change safety):
#   STYTCH_PROJECT_ID=project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a
#   STYTCH_SECRET=secret-live-…
# Stytch Dashboard → LIVE project (not test):
#   Redirect URLs → Login + Sign-up: https://astral.up.railway.app/authenticate
#   Authorized environments: https://astral.up.railway.app
#   OAuth → Google: enabled
# Prefix rule: public-token-live-* + project-live-* + secret-live-* must all belong to the SAME Stytch project.
```

2. Do **not** add secrets or real token values — placeholders only.

## Stage 3: Susan ops — Stytch Dashboard live project + Railway verification

**Done when:** Susan confirms (Linear comment on **AST-830**) that live-project Dashboard settings and Railway production env vars match the checklist below. Engineer does **not** click Dashboard; post the checklist in a Linear comment when code stages land and request Susan confirmation before marking **Code Complete**.

**Susan checklist (live project `project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a`):**

1. **Redirect URLs** — type **Login** and type **Sign-up**, exact URL:
   - `https://astral.up.railway.app/authenticate`
2. **Authorized environments** — origin only (no path):
   - `https://astral.up.railway.app`
3. **OAuth → Google** — provider **enabled** for the live project.
4. **Frontend SDK** page — max session duration ≥ **60** minutes (matches `session_duration_minutes: 60`).
5. **Railway production** — on the service that builds the SPA:
   - `VITE_STYTCH_PUBLIC_TOKEN` starts with `public-token-live-` and belongs to the live project above.
   - `VITE_STYTCH_REDIRECT_URL` is exactly `https://astral.up.railway.app/authenticate` (no trailing slash).
6. **Prefix sanity:** all three env families on production (`public-token-live-*`, `project-live-*`, `secret-live-*`) reference the **same** Stytch live project (backend secret alignment is **AST-831**, but Susan should verify while in Dashboard).

**Manual repro (Susan, production):**

1. Open `https://astral.up.railway.app` in a clean browser profile → Login → **Google** → complete OAuth.
2. **Pass:** lands on `/jobs/recommended` (or home redirect) inside Astral shell — **not** Stytch Login Error, not stuck on "Completing sign-in…".
3. **Magic link:** email login still completes (same live project).
4. **Non-admin:** Google sign-in for a non-admin Stytch user → no admin nav; `/admin/scheduled_actions` blocked per AST-612.
5. If step 2 passes visually but API calls fail with 401 / server logs show `session_not_found`, note in comment and wait for **AST-831** — do not patch backend from AST-830.

## Stage 4: Code Complete

**Done when:** Stages 1–2 committed and published; Stage 3 Susan confirmation recorded; Linear **Code Complete** with manual repro summary.

1. Post Linear comment on **AST-830** summarizing:
   - Handoff helper + Authenticate hardening approach
   - Stage 3 checklist status (confirmed / pending)
   - Manual Google + magic-link repro results on production
   - Whether `/api/me` succeeded or is deferred to **AST-831**
2. Move **AST-830** to **Code Complete** (keep assignee Katherine).

## Self-Assessment

**Scope:** `Single-Component` — touches only the frontend `/authenticate` handoff (`stytchAuthenticateHandoff.ts`, `Authenticate.tsx`) plus `env.example` ops docs; no Flask or Stytch Python changes.

**Conf:** `Medium` — Stytch SDK contract for `authenticateByUrl` / `parseAuthenticateUrl` is documented and the double-invoke failure mode matches Susan's Login Error symptom, but full production repro requires Susan's live environment.

**Risk:** `Medium` — `/authenticate` is on the auth critical path; a regression breaks all magic-link and OAuth login, though changes are isolated to the callback page and guarded by single-flight + error UI.

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Handoff logic extracted to `stytchAuthenticateHandoff.ts`; Authenticate.tsx is thin UI orchestration |
| §2.1 Config | `session_duration_minutes: 60` matches existing Login / AST-612 convention; no new config block needed |
| §2.4 Batch | N/A |
| §2.6 State machine | N/A |
| §3.3 Imports | Frontend-only; no cross-layer imports |
| §3.5 Naming | `stytchAuthenticateHandoff.ts` pairs with `stytchRedirect.ts` / `stytchClient.ts` |

No conflicts requiring plan revision.

## Review (build stub)

**Built:** `origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff` @ `0b224ff`.

**Stages delivered:**
- Stage 1: `stytchAuthenticateHandoff.ts`, hardened `Authenticate.tsx` — `ffcce3c`.
- Stage 2: `env.example` production live Stytch checklist — `0b224ff`.

**Plan note:** `parseAuthenticateUrl` lives on the Stytch client root (not `stytch.session`) per `@stytch/vanilla-js` v19 types; helper interface adjusted accordingly.

**UAT ops (Susan):** Stage 3 Stytch Dashboard live-project + Railway checklist in plan — confirm before production Google OAuth re-test.

**Betty:** `test_stytchAuthenticateHandoff.test.ts`, `test_Authenticate.test.tsx` per plan Files Changed table.
