# AST-1482 — Return to detail URL after re-auth

**Parent:** [AST-1463 — Candidate single page job report](https://linear.app/astralcareermatch/issue/AST-1463/candidate-single-page-job-report)  
**Publish ref:** `sub/AST-1463/AST-1482-return-to-detail-url-after-re-auth`

When auth is required on a protected in-app URL (including `/jobs/detail/<astral_job_id>` from sibling AST-1481), persist that pathname (+ search) in `sessionStorage`, then after successful Stytch authenticate navigate back to it instead of always `/`. Does **not** own the detail route, modal host, or candidate alignment (AST-1481).

## UAT fitness

- **AC restored:** Parent AST-1463 AC 6 — "After session expiry on the deeplink (or opening it logged out), successful login returns to **that same** `/jobs/detail/<id>` URL and the modal opens again."
- **Correct outcome:** User opens or is already on `/jobs/detail/<valid_id>` without a session (fresh visit or after timeout/log-off refresh) → completes Stytch login via `/authenticate` → lands on the **same** detail URL → `JobsJobDetail` host opens `JobAnalysisReportModal` again. Same behavior for any other protected in-app path (generic return-path, not detail-only).
- **Sibling check:** AST-1481 (`JobsJobDetail`, `jobs/detail/:jobId` route, candidate alignment, error UI) must remain on `origin/ftr/AST-1463` (or merged into this branch) for end-to-end UAT of AC 6 — this ticket does not touch those files. Recommended list row-click and modal reuse unchanged. Until both ship, logged-out deeplink still shows Login then returns to detail after auth (not `/` or `/jobs/recommended`).
- **Not sufficient:** Authenticate reaching `/` without error; storing path but never reading it; only fixing OAuth while magic-link login still drops to `/`.
- **Wrong fix rejected:** Hardcoding `/jobs/detail/*` only in `Authenticate.tsx` instead of a reusable capture/consume helper; changing `JobsJobDetail` or `routes.tsx` (AST-1481); redirecting post-auth to `/jobs/recommended` instead of the stored URL.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/sessionAuthMark.ts` | Add auth return-path capture, validate, consume (sessionStorage) | ui |
| `src/ui/frontend/src/components/RequireAuth.tsx` | Capture intended path when showing Login or LogOffScreen | ui |
| `src/ui/frontend/src/pages/Authenticate.tsx` | After successful auth, navigate to consumed return path when safe | ui |

`Login.tsx` — **no change expected**; Stytch OAuth/magic-link already redirect to `/authenticate` via `getStytchAuthenticateRedirectUrl()`. Return-path restore happens in `Authenticate.tsx` after token exchange.

## Stage 1: Return-path helper on session storage

**Done when:** `sessionAuthMark.ts` exports capture/validate/consume functions; unit tests (Betty manifest) can assert safe paths are stored and unsafe paths rejected.

1. In `src/ui/frontend/src/lib/sessionAuthMark.ts`, add a third sessionStorage key `astral-auth-return-path` alongside the existing had-session and log-off keys.

2. Add `isSafeAuthReturnPath(path: string): boolean`:
   - Return `false` for empty/whitespace-only.
   - Return `false` unless path starts with exactly one `/` (reject `//…`, `http://…`, relative paths).
   - Return `false` when path is `/authenticate` or starts with `/authenticate?` or `/authenticate/` (avoid authenticate loop).
   - Otherwise return `true` (any other same-origin in-app path, including `/jobs/detail/<id>` with query string).

3. Add `captureAuthReturnPath(pathname: string, search: string): void`:
   - Build `path = \`${pathname}${search}\``.
   - If `!isSafeAuthReturnPath(path)`, return without writing.
   - Else `sessionStorage.setItem` the key (wrap in try/catch like sibling functions).

4. Add `peekAuthReturnPath(): string | null` — read key if present and still passes `isSafeAuthReturnPath`; do not remove.

5. Add `consumeAuthReturnPath(): string | null` — read, remove key, return value only if safe; else remove and return `null`.

   ⚠️ **Decision:** Reuse `sessionAuthMark.ts` (AST-625) rather than a new module — same sessionStorage namespace and private-mode try/catch pattern; ticket Scope allows "small existing session helper."

## Stage 2: Capture intended path when auth gate blocks the app

**Done when:** Visiting a protected route without a session (Login) or after session loss (LogOffScreen) stores the current URL path; authenticated children render without overwriting a pending return path; local-auth passthrough skips capture.

1. In `src/ui/frontend/src/components/RequireAuth.tsx`:
   - Import `useLocation` from `react-router-dom` and `captureAuthReturnPath` from `../lib/sessionAuthMark`.

2. Read `const location = useLocation()`.

3. Add a `useEffect` with **early returns** that mirror `RequireAuth`'s render order (lines 16–38). Derive `logOffReason` the same way the component already does (including timeout inference from `getHadSession()`):

   ```typescript
   useEffect(() => {
     if (localAuthPassthrough !== false) return // null = passthrough fetch; true = skip Stytch
     if (!isInitialized && !session) return // same guard as the Loading… return — do not capture yet
     const blocked = Boolean(logOffReason) || !session // LogOffScreen or Login
     if (!blocked) return // authenticated children
     captureAuthReturnPath(location.pathname, location.search)
   }, [
     localAuthPassthrough,
     session,
     isInitialized,
     logOffReason,
     location.pathname,
     location.search,
   ])
   ```

   **Gate order (mandatory):**
   1. **`localAuthPassthrough !== false`** — skip while passthrough is unresolved (`null`) or on (`true`).
   2. **`!isInitialized && !session`** — skip during Stytch bootstrap Loading… (must match the render `return` at `RequireAuth.tsx` lines 23–25). Equivalently: proceed only when **`isInitialized || session`**.
   3. **Blocked predicates** — `logOffReason` (LogOffScreen, including server-rejection while `session` may still exist) **or** `!session` (Login). Skip when neither applies (authenticated children).
   4. Call `captureAuthReturnPath` only when steps 1–3 pass.

   Dependencies include `logOffReason` so timeout inference re-runs capture when the gate flips from Loading to LogOffScreen.

   ⚠️ **Decision:** Capture on LogOffScreen as well as Login so session-expiry on a deeplink survives the Refresh → Login → `/authenticate` chain (Refresh clears had-session marks but browser URL stays on the deeplink; re-capture on Login is the backup).

4. Do **not** capture when `localAuthPassthrough === true` or when rendering authenticated children.

5. Do **not** modify `Login.tsx` or `LogOffScreen.tsx`.

## Stage 3: Restore return path after authenticate

**Done when:** Successful `/authenticate` handoff navigates to the stored path when present; all existing passthrough and error behaviors unchanged; default remains `/` when no valid stored path.

1. In `src/ui/frontend/src/pages/Authenticate.tsx`, import `consumeAuthReturnPath` from `../lib/sessionAuthMark`.

2. Add a small helper inside the file (not exported):

   ```typescript
   function postAuthNavigate(navigate: NavigateFunction): void {
     const returnPath = consumeAuthReturnPath()
     navigate(returnPath ?? "/", { replace: true })
   }
   ```

   (Use the actual `NavigateFunction` type from `react-router-dom`.)

3. Replace every success-path `navigate("/", { replace: true })` with `postAuthNavigate(navigate)` **except**:
   - **`localAuthPassthrough === true`** branches — keep `navigate("/", { replace: true })` (local dev has no Stytch round-trip; URL already reflects the intended page).
   - **Error phase** — keep the "Try again" `Link to="/"` unchanged.

   Success paths to update (current code):
   - Existing Stytch session on load (`session` already present).
   - `completeAuthenticateFromUrl` outcome `success` or `no-token`.

4. Do **not** change `stytchRedirect.ts` or Stytch Dashboard redirect URLs — in-app return is entirely post-`/authenticate`.

5. Confirm no changes to `routes.tsx`, `JobsJobDetail.tsx`, `JobAnalysisReportModal.tsx`, or `CandidateContext.tsx`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

Revision 1 — 2026-08-25  
Driven by: Joan `[plan-discuss] round=1 concern` — Stage 2 `useEffect` loading guard contradicts itself.  
Changes: Stage 2 step 3 rewritten with explicit early-return gate order: passthrough false, then `isInitialized || session` (mirror Loading… return), then blocked predicates (`logOffReason` or `!session`) before capture. Removed ambiguous "initialized or no session" bullet; server-rejection LogOffScreen with session still present must capture.

## Joan validate

```
[plan-discuss] round=1 concern
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1482
**Overall:** REVISE
**Publish ref:** `494ae7e07ae34496d093cc31eafc02564b33d5ad` (`origin/sub/AST-1463/AST-1482-return-to-detail-url-after-re-auth`)

## Traceability
AC6 (parent AST-1463 AC 6) → Stage 1 (capture/validate/consume helper), Stage 2 (persist path on Login/LogOffScreen gate), Stage 3 (`Authenticate.tsx` consume + navigate); AST-1481 route/modal host out of scope (sibling E2E dependency documented in UAT fitness).

## Findings

**fix-now** — **Stage 2 `useEffect` loading guard contradicts itself.** Bullet 2 requires "Stytch is initialized **or** there is no session," which is true during the existing `!isInitialized && !session` loading branch — the same branch the parenthetical says not to capture in. RequireAuth only exits that loading state when `isInitialized || session`. Stage 2 must gate capture on **`isInitialized || session`** (mirror the loading `return`), then apply the blocked predicates (`logOffReason` or Login `!session`). As written, an implementer can capture too early or misread the guard.

**discuss** — No formal **Self-assessment** block (Scope/Conf/Risk); stages are otherwise specific. Non-blocking.

**acceptable** — `clearSessionAuthMarks()` intentionally does not clear `astral-auth-return-path`; LogOffScreen Refresh → Login re-capture covers the timeout chain as described.

**acceptable** — `no-token` success-path navigation to consumed return path preserves current `Authenticate.tsx` behavior; protected URL without session falls back to Login again.

context_tokens≈48000
```
