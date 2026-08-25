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

3. Add a `useEffect` that runs when **all** of the following hold:
   - `localAuthPassthrough === false` (not `null`, not `true` — only capture when real Stytch auth is required),
   - Stytch is initialized **or** there is no session (match existing gate timing — do not capture while `localAuthPassthrough === null` or initial loading),
   - User is blocked: either `logOffReason` is set **or** (`!session` and no `logOffReason` — Login path),
   - Call `captureAuthReturnPath(location.pathname, location.search)`.

   Dependencies: `[localAuthPassthrough, session, isInitialized, logOffReason, location.pathname, location.search]` — derive `logOffReason` the same way the component already does (including timeout inference from `getHadSession()`).

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
