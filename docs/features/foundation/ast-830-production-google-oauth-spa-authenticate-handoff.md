<!-- linear-archive: AST-830 archived 2026-07-22 -->

## Linear archive (AST-830)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-830/production-google-oauth-spa-authenticate-handoff-using-google-to-login  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-829 — Using Google to login on production doesn't work  
**Blocked by / blocks / related:** parent: AST-829

### Description

## What this implements

Fix the production Google OAuth user experience on [**https://astral.up.railway.app**](<https://astral.up.railway.app>): after Google redirects back, the React SPA must complete the `/authenticate` handoff and establish a Stytch client session — not show Stytch's **Login Error** page. Susan's Stytch live-project activity log shows **SessionsGet** succeeding while the browser still displays "There was an error logging you in." This ticket closes the frontend gap between OAuth completion and an authenticated app shell.

## Acceptance criteria

1. On [**https://astral.up.railway.app**](<https://astral.up.railway.app>), clicking **Google** on the Login page completes OAuth and lands the user in the authenticated app — not the Stytch **Login Error** page, not Login, and not a Stytch URL validation error page.
2. Email magic-link login on production still completes successfully (same live Stytch project).
3. Non-admin Stytch users signing in via Google on production still receive `is_admin: false` and cannot access admin routes (**403** / UI gating per **AST-612**).
4. Railway production env vars and Stytch Dashboard live-project settings are documented (in the dev agent plan or ops notes) so a future host change does not silently break OAuth again.

## Boundaries

* Does **not** replace Stytch or redesign the auth stack (**AST-609** / **AST-612** / **AST-613**).
* Does **not** change Flask backend token validation — sibling **Ada** ticket owns backend alignment.
* Does **not** add new OAuth providers beyond Google already on Login.
* Does **not** change session duration, idle timeout, or log-off screen behavior.

## Notes for planning

* Primary touchpoints: `Login.tsx`, `Authenticate.tsx`, `stytchRedirect.ts`, `stytchClient.ts`, `AuthContext.tsx` per **AST-612** / **AST-613**.
* Production redirect URL: `https://astral.up.railway.app/authenticate` — must match Stytch Dashboard live project and `VITE_STYTCH_REDIRECT_URL` at Vite build time.
* Live project id: **project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a**.
* Plan Stage 3: Susan must confirm Stytch Dashboard live project has Google OAuth enabled, redirect URLs (Login + Sign-up), and Authorized environments for production origin.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-829-production-google-oauth-stytch-live`, child `sub/AST-829/<child-segment>`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-27T19:40:16.800Z
### Radia review — `origin/dev...origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff` @ `0a9df2c`

Plan doc: `docs/features/foundation/ast-830-production-google-oauth-spa-authenticate-handoff.md` (Radia review section)

**fix-now:** None.

**discuss:**
- Branch diff vs `origin/dev` includes **AST-832** test/bible rows (`test_consult.py`, `docs/test-bible/core/consult.md`) outside AST-830 layer contract — no `consult.py` product in diff; likely ftr rollup on publish ref. Confirm merge-child narrative or split before parent close.
- Plan Stage 3 Susan ops checklist (Stytch Dashboard live project + Railway) still pending — production Google OAuth sign-off needs Susan confirmation; if SPA handoff succeeds but `/api/me` 401 / `session_not_found`, defer to **AST-831** per plan.

**advisory:**
- `SESSION_DURATION_MINUTES = 60` in helper matches Login `loginExpirationMinutes` / `signupExpirationMinutes`; not a shared constant — plan waived config block; low drift risk.
- StrictMode dev remount can reset `useRef` single-flight guard; production does not double-invoke effects — acceptable for production OAuth target.

**What's solid (§3.3 / §1.3 / §D2):** Frontend-only; `completeAuthenticateFromUrl` + hardened `Authenticate.tsx` (init gate, single-flight, in-app error + Try again, query strip on failure); `parseAuthenticateUrl` on client root per v19 types; Betty manifest covers helper outcomes and page states.

#### betty — 2026-06-27T19:35:20.725Z
## QA test manifest (AST-830)

**Publish ref:** `origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff` @ `8930265` (`merge-tests(AST-830): origin/tests 9d78794`)

**Bible shasums on publish ref:**
- `docs/test-bible/frontend/lib.md` → `32c062c70a5ed450d773994a749cf8bf205db5e6`
- `docs/test-bible/frontend/components.md` → `f28e38e55aa3e596842ca289911abbfbf238661b`

### Manifest (test-child)

1. **Typecheck (required):**
```bash
cd src/ui/frontend && npx tsc -b --noEmit
```

2. **Handoff helper unit tests (required):**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts
```

3. **Authenticate routed page (required — §6c):**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_Authenticate.test.tsx
```

4. **Regression spot-check (required):** green on **`test_stytchRedirect.test.ts`** + **`test_Login.test.tsx`** — redirect URL wiring unchanged.

**Pass criterion:** items 1–4 green on publish ref after merge-on-checkout from parent ftr.

**Out of scope:** Flask JWT / `session_not_found` → **AST-831**; Susan Stage 3 Dashboard checklist is manual UAT, not pytest.

#### katherine — 2026-06-27T19:32:27.456Z
`origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff` @ `9c8928f`

**Susan — Stage 3 ops checklist (pending your confirmation):**
1. Stytch **live** project `project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a` — Redirect URLs (Login + Sign-up): `https://astral.up.railway.app/authenticate`
2. Authorized environment: `https://astral.up.railway.app`
3. OAuth → Google enabled
4. Railway production build: `VITE_STYTCH_PUBLIC_TOKEN=public-token-live-…`, `VITE_STYTCH_REDIRECT_URL=https://astral.up.railway.app/authenticate` (no trailing slash)
5. Re-test Google + magic link on production after deploy

If `/api/me` still 401 after client session lands, that's **AST-831** — not patched here.

#### katherine — 2026-06-27T19:27:20.854Z
Plan: [docs/features/foundation/ast-830-production-google-oauth-spa-authenticate-handoff.md](https://github.com/susansomerset/astral/blob/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff/docs/features/foundation/ast-830-production-google-oauth-spa-authenticate-handoff.md) @ `origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff` @ `839f65a`

**Approach:** Harden `/authenticate` — `completeAuthenticateFromUrl()` helper with `parseAuthenticateUrl` pre-check, awaited `authenticateByUrl`, single-flight guard (StrictMode / double-call → Stytch Login Error), and in-app error UI instead of hosted Stytch failure page. Stage 3 documents production live-project Dashboard + Railway checklist for `https://astral.up.railway.app`. Flask JWT / `session_not_found` stays **AST-831**.

**Self-assessment**
- **Scope:** Single-Component — frontend handoff helper + `Authenticate.tsx` + `env.example` ops block only.
- **Conf:** Medium — SDK contract is clear and double-invoke matches Susan's symptom; full production repro needs live env.
- **Risk:** Medium — auth callback is critical path, but changes are isolated to one route with guarded single-flight.

---

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

---

## Radia review (2026-06-27)

**Diff:** `origin/dev...origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff` (`8930265`)

**Session:** `fa43d223-42ec-491f-af77-c0f209a3e4d9`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–2: `completeAuthenticateFromUrl` helper with success / no-token / unsupported-token / error outcomes; `Authenticate.tsx` init gate (`isInitialized`), existing-session short-circuit, `useRef` single-flight, in-app error + **Try again**, query strip on failure; `env.example` production live-project checklist. |
| SDK contract | `parseAuthenticateUrl` on client root (not `session`) per `@stytch/vanilla-js` v19 — documented in build stub; tests mock matches implementation. |
| Layering (§3.3) | Frontend-only delta; no Flask / `src/external/stytch.py` / backend auth changes — AST-831 boundary respected. |
| DRY (§1.3) | Handoff logic in `stytchAuthenticateHandoff.ts`; page is thin orchestration. |
| Error handling (§D2) | `authenticateByUrl` rejections and unhandled outcomes become typed results — no swallowed exceptions on auth path. |
| Session duration | `SESSION_DURATION_MINUTES = 60` matches `Login.tsx` `loginExpirationMinutes` / `signupExpirationMinutes` (60). |
| Tests / bible | Betty manifest covers helper outcomes, page loading / redirect / error / single-flight; bible rows in `frontend/lib.md` and `components.md` match diff. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | Branch diff vs `origin/dev` | **`AST-832`** artifacts present: `tests/component/core/test_consult.py` additions + `docs/test-bible/core/consult.md` row — outside AST-830 layer contract (no `consult.py` product in diff). Likely ftr rollup on publish ref; confirm merge-child narrative or split before parent close. |
| **discuss** | Plan Stage 3 | Susan ops checklist (Stytch Dashboard live project + Railway) still pending — not a code defect; production Google OAuth sign-off needs Susan confirmation per plan before parent UAT closes AST-829. |
| **advisory** | `stytchAuthenticateHandoff.ts` | `SESSION_DURATION_MINUTES` is a module constant, not shared with `Login.tsx` — same value (60), plan explicitly waived new config block; drift risk is low. |
| **advisory** | `Authenticate.tsx` `useRef` guard | React StrictMode dev remount resets ref (double-invoke possible in dev only); production StrictMode does not double-invoke effects — matches plan's production OAuth target. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child`. |
| discuss | Stage 3 Susan checklist on **AST-830** before production Google OAuth re-test; note `/api/me` + **AST-831** if session JWT validation still fails after SPA handoff succeeds. |
| discuss | AST-832 test/bible rows on publish ref — acceptable ftr rollup or cherry-pick hygiene at merge-child. |
| advisory | Optional: extract shared `60` to a frontend auth constant if Login duration changes later. |

**Publish tip:** `8930265` (product `ffcce3c` + env `0b224ff` + tests `8930265`)

## Resolution (2026-06-27)

**Review tip:** `0a9df2c` (`docs(AST-830): Radia review — clean SPA authenticate handoff`)

**fix-now:** None — no product changes required.

**discuss (closed for resolve):**
- **AST-832 test/bible rows on publish ref** — ftr rollup from sibling merge on epic worktree; AST-830 product diff is frontend-only. Chuckles **`merge-child`** narrative covers rollup; no Katherine split.
- **Stage 3 Susan ops** — remains Susan manual UAT on production (`https://astral.up.railway.app`); checklist posted on Linear 2026-06-27. `/api/me` 401 after successful SPA handoff → **AST-831**, not AST-830.

**advisory:** Accepted as-is (shared `60` constant drift risk low; StrictMode dev-only double-invoke acceptable).

**§9a dry-run:** `origin/sub/AST-829/AST-830-production-google-oauth-spa-authenticate-handoff` @ `0a9df2c` merges cleanly into `origin/dev` and `origin/ftr/AST-829-production-google-oauth-stytch-live`.

**Manifest:** Betty items 1–4 green on publish ref (17 tests).
