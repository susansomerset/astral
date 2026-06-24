<!-- linear-archive: AST-613 archived 2026-06-23 -->

## Linear archive (AST-613)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-613/uat-stytch-magic-link-and-google-oauth-redirect-url-mismatch-use  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-609 — Use stytch for user authentication  
**Blocked by / blocks / related:** parent: AST-609

### Description

## What failed

On the Login page, entering `susan@susansomerset.com` for magic link returns Stytch error: *The magic_link_url in the request did not match any redirect URLs set for this project.*

Clicking Google SSO returns HTTP 400 `no_match_for_provided_oauth_url` — *The oauth redirect url in the request did not match any redirect URLs set for this project.*

## Expected

Magic link and Google OAuth complete successfully; user lands on `/authenticate` then the authenticated app with Bearer on API calls.

## Repro

1. Open the app (Railway staging or local) → Login page.
2. Enter email for magic link **or** click Google — observe Stytch redirect URL validation error.
3. App currently sends redirect `${window.location.origin}/authenticate` from `Login.tsx`.

## Parent AC (quoted inline)

> Unauthenticated users see login; authenticated users reach the app with valid Bearer on all API calls.

> It is time to implement proper user authentication and I want to use the STYTCH platform for this purpose.

## Boundaries

* This bug does **not** change: Flask auth decorators (**AST-611**), Stytch Python client (**AST-610**), admin UI gating logic beyond login redirect configuration.
* Does **not** replace Stytch with another provider.

## Git branch (authoritative)

Parent `ftr/ast-609-use-stytch-for-user-authentication`, child `sub/AST-609/AST-613-stytch-login-redirect-urls`.

### Comments

#### radia — 2026-06-13T00:00:16.594Z
**Review (Radia)** — `origin/dev...origin/sub/AST-609/AST-613-stytch-login-redirect-urls` @ `cb671bbe`

Doc: `docs/features/foundation/ast-613-stytch-login-redirect-urls.md` (Review section)

### fix-now

None.

### discuss

None.

### Advisory

- **Stage 3 ops (Susan):** Stytch Dashboard must register exact redirect URLs (Login + Sign-up) and Railway must set `VITE_STYTCH_REDIRECT_URL` to the same string — code cannot bypass Stytch allowlist validation. See plan Stage 3 and `env.example`.
- **`Login.tsx`:** `stytchLoginConfig` is rebuilt each render; fine at this scale. Consider `useMemo` only if Stytch re-init becomes visible in profiling.

### Signed off

| Check | Result |
|-------|--------|
| Plan Stages 1–2 | `stytchRedirect.ts`, env contract, `Login.tsx` all four redirect fields |
| §1.3 DRY / §2.1 Config | Single helper; Vite env + origin fallback matches AST-612 pattern |
| §3.3 Layers | Frontend-only; no scope creep into AST-610/611/612 |
| Betty tests | Env trim/slash, fallback, Login config wiring covered |

#### betty — 2026-06-12T23:58:50.919Z
## QA test manifest (AST-613)

**Publish ref:** `origin/sub/AST-609/AST-613-stytch-login-redirect-urls` @ `c12b9af8`

**`docs/ASTRAL_TEST_BIBLE.md` shasum:** `075a7200eda2218752169855cf2bb9ab8b2e2980`

1. `tests/component/frontend/lib/test_stytchRedirect.test.ts` — `VITE_STYTCH_REDIRECT_URL` trimmed (no trailing slash); fallback `${origin}/authenticate` when env unset
2. `tests/component/frontend/pages/test_Login.test.tsx` — renders `Login` page; asserts magic-link + OAuth redirect URLs wired through helper (§6c routed page)

**Narrowed run** (from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../tests/component/frontend/lib/test_stytchRedirect.test.ts \
  ../tests/component/frontend/pages/test_Login.test.tsx
```

**Existing coverage (unchanged):** AST-612 manifest rows in bible §7.13zza — no regressions expected on auth gate components.

**Note:** Stytch Dashboard allowlist + Railway `VITE_STYTCH_REDIRECT_URL` remain operator prerequisites for manual UAT; tests mock Stytch and do not hit the live API.

#### katherine — 2026-06-12T23:55:07.234Z
Plan: [docs/features/foundation/ast-613-stytch-login-redirect-urls.md](https://github.com/susansomerset/astral/blob/sub/AST-609/AST-613-stytch-login-redirect-urls.md) @ `origin/sub/AST-609/AST-613-stytch-login-redirect-urls` @ `0c7a3b6c`

**Approach:** Stytch requires an exact allowlist match for magic-link and OAuth redirect URLs. AST-612 sent `${window.location.origin}/authenticate` at runtime; this fails when the dashboard still has Stytch defaults (`localhost:3000`) or when Railway needs a build-time pin. Plan adds `getStytchAuthenticateRedirectUrl()` (`VITE_STYTCH_REDIRECT_URL` → fallback to current origin), wires `Login.tsx`, and expands `env.example` with the precise Dashboard checklist (Login + Sign-up redirect types, Authorized environments, Google OAuth).

**Self-assessment**
- **Scope:** `scope-minor` — one helper, `Login.tsx`, env typings/docs only.
- **Conf:** `conf-high` — Stytch exact-match rules are documented; change reuses AST-612 `StytchLogin` shape.
- **Risk:** `risk-Medium` — login remains critical-path; wrong URL blocks entire auth flow (same as current UAT failure).

**Susan ops (required for UAT):** Register `http://localhost:5173/authenticate` and `https://<railway-host>/authenticate` (Login + Sign-up) plus matching Authorized environment origins before re-testing.

---

# AST-613 — UAT: Stytch magic link and Google OAuth redirect URL mismatch (Use stytch for user authentication)

- **Linear (this ticket):** [AST-613](https://linear.app/astralcareermatch/issue/AST-613/uat-stytch-magic-link-and-google-oauth-redirect-url-mismatch-use)
- **Parent:** [AST-609](https://linear.app/astralcareermatch/issue/AST-609/use-stytch-for-user-authentication)
- **Publish ref:** `origin/sub/AST-609/AST-613-stytch-login-redirect-urls`
- **Depends on:** [AST-612](https://linear.app/astralcareermatch/issue/AST-612/react-stytch-login-and-admin-ui-gating-use-stytch-for-user) (`Login.tsx`, `Authenticate.tsx`, `@stytch/react` prebuilt login) on `origin/ftr/ast-609-use-stytch-for-user-authentication`

## Summary

Stytch rejects magic-link and Google OAuth requests because the redirect URL sent from `Login.tsx` does not **exactly** match any URL allowlisted in the Stytch project (test/live). AST-612 used runtime `${window.location.origin}/authenticate`, which is correct in theory but fails when the allowlist was never updated from Stytch’s default (`http://localhost:3000`) or when Railway’s public URL must be pinned at **Vite build time** to match dashboard entries. This ticket adds a single canonical redirect helper (`VITE_STYTCH_REDIRECT_URL` with safe fallback), wires `Login.tsx` through it, and documents the precise Stytch Dashboard URLs Susan must register. No Flask, Python Stytch client, or admin-gating changes.

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/ui/frontend/src/lib/stytchRedirect.ts` | **New** — canonical `/authenticate` redirect URL | frontend only |
| `src/ui/frontend/src/pages/Login.tsx` | Use helper for all four redirect fields | frontend only |
| `env.example`, `src/ui/frontend/src/vite-env.d.ts` | Document + type `VITE_STYTCH_REDIRECT_URL` | docs / frontend |
| `src/utils/auth.py`, `src/external/stytch.py`, `Authenticate.tsx`, decorators | **Read-only** — AST-610/611/612 | do not modify |

⚠️ **Decision:** Prefer **`VITE_STYTCH_REDIRECT_URL`** (full URL including `/authenticate`, no trailing slash) at build time on Railway so the value baked into the SPA matches Stytch Dashboard allowlist exactly. Fallback to `${window.location.origin}/authenticate` when unset (local Vite dev).

⚠️ **Decision:** Do **not** add a backend redirect-url endpoint — keeps scope frontend-only and matches AST-612’s Vite env pattern for `VITE_STYTCH_PUBLIC_TOKEN`.

⚠️ **Decision:** Stytch Dashboard configuration is **required** for UAT pass (not optional ops). Code cannot bypass allowlist validation; the plan includes a verification checklist Susan runs once URLs are registered.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| Flask `@require_auth` / `@require_admin`, Stytch Python client | **AST-610** / **AST-611** |
| Admin UI gating, `AuthContext`, Bearer injection | **AST-612** |
| `tests/` or `docs/ASTRAL_TEST_BIBLE.md` commits | **Betty** (`qa-child`) |
| Replacing Stytch with another provider | — |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/stytchRedirect.ts` | **New** — `getStytchAuthenticateRedirectUrl()` | frontend |
| `src/ui/frontend/src/pages/Login.tsx` | Build `stytchLoginConfig` via helper (inside component) | frontend |
| `src/ui/frontend/src/vite-env.d.ts` | Add optional `VITE_STYTCH_REDIRECT_URL` to `ImportMetaEnv` | frontend |
| `env.example` | Add `VITE_STYTCH_REDIRECT_URL` + expanded Stytch Dashboard checklist | docs |

## Stage 1: Redirect URL helper and env contract

**Done when:** `getStytchAuthenticateRedirectUrl()` returns env value when set (trimmed, no trailing slash); returns `${origin}/authenticate` when env unset; `npm run build` in `src/ui/frontend/` passes.

1. Create `src/ui/frontend/src/lib/stytchRedirect.ts`:

```typescript
/** Canonical Stytch login/signup/OAuth redirect (AST-613). Must match Stytch Dashboard allowlist exactly. */
export function getStytchAuthenticateRedirectUrl(): string {
  const fromEnv = import.meta.env.VITE_STYTCH_REDIRECT_URL?.trim()
  if (fromEnv) {
    return fromEnv.replace(/\/$/, "")
  }
  const origin = window.location.origin.replace(/\/$/, "")
  return `${origin}/authenticate`
}
```

2. In `src/ui/frontend/src/vite-env.d.ts`, extend `ImportMetaEnv`:

```typescript
readonly VITE_STYTCH_REDIRECT_URL?: string
```

(Keep existing `VITE_STYTCH_PUBLIC_TOKEN`.)

3. In `env.example`, after the `VITE_STYTCH_PUBLIC_TOKEN` line, add:

```
# Full redirect URL for Stytch magic link + OAuth (Vite build). Must EXACTLY match Stytch Dashboard → Redirect URLs (Login + Sign-up).
# Local dev (Vite default port):
VITE_STYTCH_REDIRECT_URL=http://localhost:5173/authenticate
# Railway staging: set to https://<your-railway-public-host>/authenticate (same string in Stytch Dashboard test project)
```

4. Replace the existing Stytch Dashboard comment block (lines starting `# Stytch Dashboard → Redirect URLs`) with:

```
# Stytch Dashboard (Consumer test project) — required for AST-612/613 login:
# Redirect URLs → add BOTH types "Login" and "Sign-up" for EACH URL below:
#   http://localhost:5173/authenticate
#   https://<your-railway-public-host>/authenticate
# Authorized environments → add origins (no path, no trailing slash):
#   http://localhost:5173
#   https://<your-railway-public-host>
# OAuth → Google: enable provider; redirect URLs above must include the /authenticate paths.
```

5. From `src/ui/frontend/`: `npm run build`.

## Stage 2: Wire Login.tsx through helper

**Done when:** Magic link and OAuth config in `Login.tsx` all use `getStytchAuthenticateRedirectUrl()`; no module-level `const redirect = …` remains; `npm run lint` and `npm run build` pass.

1. In `src/ui/frontend/src/pages/Login.tsx`:

- Import `getStytchAuthenticateRedirectUrl` from `../lib/stytchRedirect`.
- Remove top-level `const redirect = …` and top-level `stytchLoginConfig`.
- Inside `Login` component, before `return`:

```typescript
const redirect = getStytchAuthenticateRedirectUrl()
const stytchLoginConfig = {
  products: [Products.emailMagicLinks, Products.oauth],
  emailMagicLinksOptions: {
    loginRedirectURL: redirect,
    loginExpirationMinutes: 60,
    signupRedirectURL: redirect,
    signupExpirationMinutes: 60,
  },
  oauthOptions: {
    providers: [{ type: "google" as const }],
    loginRedirectURL: redirect,
    signupRedirectURL: redirect,
  },
}
```

- Pass `config={stytchLoginConfig}` to `<StytchLogin />` unchanged.

2. From `src/ui/frontend/`: `npm run lint` then `npm run build`.

## Stage 3: Verification and Code Complete

**Done when:** Manual happy path on staging **and** local dev: magic link email sends without `magic_link_url` error; Google OAuth completes without `no_match_for_provided_oauth_url`; user lands on `/authenticate` then app with Bearer on API calls. Linear **Code Complete** comment includes Stytch Dashboard checklist confirmation.

1. **Susan / operator (before or during UAT):** In Stytch Dashboard (test project matching `STYTCH_PROJECT_ID` / `VITE_STYTCH_PUBLIC_TOKEN`):

   - **Redirect URLs:** Register **Login** and **Sign-up** for each exact URL:
     - `http://localhost:5173/authenticate` (local)
     - `https://<railway-public-host>/authenticate` (staging — must match `VITE_STYTCH_REDIRECT_URL` on Railway frontend build)
   - **Authorized environments:** `http://localhost:5173` and `https://<railway-public-host>` (origins only).
   - **OAuth → Google:** Provider enabled; same redirect URLs apply.

2. **Railway:** Set `VITE_STYTCH_REDIRECT_URL=https://<railway-public-host>/authenticate` on the service that runs `scripts/build_railway.sh` (same host users open in the browser).

3. **Manual repro (staging):** Login page → enter `susan@susansomerset.com` → no Stytch redirect error; click Google → no HTTP 400 `no_match_for_provided_oauth_url`; complete flow → `/authenticate` → home with API calls authorized.

4. Post Linear comment on **AST-613** summarizing:
   - Helper + env var approach
   - Exact redirect URLs registered in Stytch
   - Railway `VITE_STYTCH_REDIRECT_URL` value used
   - Betty optional test note: unit test `getStytchAuthenticateRedirectUrl` with `vi.stubEnv` (not required for build)

5. Move **AST-613** to **Code Complete** (assignee stays Katherine).

### Betty QA spec (optional — manifest for `qa-child`)

| Case | File | Assertion |
|------|------|-----------|
| Env redirect | `tests/component/frontend/lib/test_stytchRedirect.test.ts` | With `VITE_STYTCH_REDIRECT_URL` stubbed → exact value (no trailing slash) |
| Fallback | same | Without env → `${origin}/authenticate` |

Mock `window.location.origin` in Vitest. Do not call real Stytch.

## Self-Assessment

**Scope:** `scope-minor` — Three frontend/doc files plus one new ~10-line helper; no backend or routing changes.

**Conf:** `conf-high` — Stytch’s exact-match redirect rules are documented; AST-612 already established the `/authenticate` path and `StytchLogin` config shape.

**Risk:** `risk-Medium` — Incorrect redirect URL still blocks all login paths; fix is narrow but login is on the critical path for the epic.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Single helper replaces duplicated redirect string in `Login.tsx` |
| §2.1 Config | Vite env for build-time URL (not `config.py`) — matches AST-612 public-token pattern |
| §3.3 Imports | Frontend-only; no cross-layer imports |
| §3.5 Naming | `getStytchAuthenticateRedirectUrl` mirrors `stytchClient.ts` module naming |
| §2.9 Auth | Unchanged — Bearer flow remains AST-612 |

No `conf-!!-NONE` conflicts identified.

## Review (build stub)

**Built:** `origin/sub/AST-609/AST-613-stytch-login-redirect-urls` @ `7ab12d53`.

**Stages delivered:**
- Stage 1: `stytchRedirect.ts`, `vite-env.d.ts`, `env.example` — `544aea8d`.
- Stage 2: `Login.tsx` via `getStytchAuthenticateRedirectUrl()` — `7ab12d53`.

**UAT ops (Susan):** Register Stytch Dashboard redirect URLs + set Railway `VITE_STYTCH_REDIRECT_URL` per Stage 3 checklist before re-test.

**Betty:** Optional `test_stytchRedirect.test.ts` in Betty QA spec above.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-609/AST-613-stytch-login-redirect-urls` @ `c12b9af8`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–2 delivered: `stytchRedirect.ts`, `vite-env.d.ts`, `env.example`, `Login.tsx` wired through `getStytchAuthenticateRedirectUrl()` for all four redirect fields |
| §1.3 DRY | Single canonical helper replaces module-level redirect string |
| §2.1 Config | `VITE_STYTCH_REDIRECT_URL` at build time with origin fallback matches AST-612 public-token pattern |
| §3.3 Layers | Frontend-only; no backend or cross-layer imports |
| Boundaries | No AST-610/611/612 scope smuggled in |
| Tests | Betty manifest covers env trim/slash, origin fallback, and Login config wiring |

### Issues

None — **fix-now** or **discuss**.

### Recommended actions

| Severity | Item | Location |
|----------|------|----------|
| Advisory | Stage 3 UAT still requires Susan: Stytch Dashboard redirect URLs (Login + Sign-up) and Railway `VITE_STYTCH_REDIRECT_URL` must match exactly — code cannot bypass allowlist | Plan Stage 3; `env.example` |
| Advisory | `stytchLoginConfig` rebuilt each render inside `Login` — acceptable at this scale; `useMemo` only if profiling shows unnecessary Stytch re-init | `Login.tsx` |

## Resolution

**Date:** 2026-06-13 · **Publish ref:** `origin/sub/AST-609/AST-613-stytch-login-redirect-urls` @ `cb671bbe`

Radia review had no fix-now or discuss items. No product code changes in resolve — Radia doc commit `cb671bbe` already on publish ref; product tip `7ab12d53` (Stages 1–2) + Betty tests `c12b9af8`.

**§9a dry-run:** publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-609-use-stytch-for-user-authentication`.

**Outcome:** Ready for User Testing; Susan must complete Stage 3 Stytch Dashboard + Railway `VITE_STYTCH_REDIRECT_URL` ops before manual login re-test.
