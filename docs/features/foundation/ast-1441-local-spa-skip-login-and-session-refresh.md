# Local SPA skip login and session refresh

**Linear:** [AST-1441](https://linear.app/astralcareermatch/issue/AST-1441/local-spa-skip-login-and-session-refresh)
**Parent:** [AST-1438](https://linear.app/astralcareermatch/issue/AST-1438/disable-authentication-on-localhost) — Disable authentication on localhost
**Publish ref:** `sub/AST-1438/AST-1441-local-spa-skip-login-and-session-refresh`

When `GET /api/auth_passthrough` returns `local_auth_passthrough: true` (sibling **AST-1440**, already on this epic's `ftr`), the SPA does not wait for a Stytch session, does not mount Login or Log-off for a missing session, does not start session extend/refresh, and loads identity from `GET /api/me`. When the signal is `false` or the fetch fails closed, Login / Log-off / extend stay as they are today.

**Depends on:** AST-1440 public `GET /api/auth_passthrough` — present on `origin/ftr/AST-1438-disable-authentication-on-localhost` (Ada at User Testing).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/authPassthrough.ts` | **New** — typed raw `fetch` of `GET /api/auth_passthrough`; fail-closed `false` | ui |
| `src/ui/frontend/src/contexts/AuthContext.tsx` | Resolve the signal first; on `true` call `/api/me` with no Stytch session and skip the extend loop | ui |
| `src/ui/frontend/src/components/RequireAuth.tsx` | On `true`, render children (no Login / Log-off / Stytch `isInitialized` wait) | ui |
| `src/ui/frontend/src/pages/Authenticate.tsx` | On `true`, `navigate("/")` without `completeAuthenticateFromUrl` | ui |

**Out of this ticket (do not touch):** Flask `@require_auth` / `@require_admin` / `local_operator_user` / `GET /api/auth_passthrough` implementation (sibling **AST-1440**). `canon/patterns/auth/pattern.auth.local-deploy-passthrough.md`. `docs/ASTRAL_CODE_RULES.md` (sibling 1's §2.9 sentence that SPA consumption is a separate ticket stays; this ticket *is* that consumption). `Login.tsx`, `LogOffScreen.tsx`, `sessionExtend.ts`, `authSessionPolicy.ts`, `stytchAuthenticateHandoff.ts`, `stytchClient.ts`, `api.ts`, `App.tsx` (`StytchProvider` stays), `routes.tsx`, `sessionAuthMark.ts`, `CandidateContext.tsx`, `AdminRoute.tsx`, `NavigationShell.tsx`. Surfer / extension auth. Hostname `localhost` as a gate. `@require_ip`. Stytch Dashboard. Do not edit `tests/` or `docs/test-bible/**`.

## Stage 1: Public-signal fetch helper

**Done when:** `fetchAuthPassthrough()` exists in `src/ui/frontend/src/lib/authPassthrough.ts`, uses raw `fetch` (not `api()`), and returns `true` only when the JSON field `local_auth_passthrough` is the boolean `true`. Non-200, network error, invalid JSON, missing field, or any other value returns `false`. No React code consumes it yet.

1. Create `src/ui/frontend/src/lib/authPassthrough.ts` with **exactly** this content:

```typescript
export interface AuthPassthrough {
  local_auth_passthrough: boolean
}

/** Public non-secret local-auth signal (AST-1440). Raw fetch — not api() — so the pre-login gate is free of Bearer/401 log-off coupling. Fail closed: only boolean true counts. */
export async function fetchAuthPassthrough(): Promise<boolean> {
  try {
    const r = await fetch("/api/auth_passthrough", { credentials: "include" })
    if (!r.ok) return false
    const data = (await r.json()) as Partial<AuthPassthrough>
    return data.local_auth_passthrough === true
  } catch {
    return false
  }
}
```

2. Do **not** add a hostname check. Do **not** fold this into `fetchAuthSessionPolicy`. Do **not** throw on failure (unlike session policy — a missing signal must not break staging Login).

⚠️ **Decision:** Fail closed to `false` rather than throw. Staging/production/unset must keep Login if the endpoint is missing, the proxy is down, or the payload is wrong. `=== true` so a string `"true"` or a missing key cannot skip Login.

⚠️ **Decision:** Raw `fetch`, not `api()`, same as AST-1373's `/api/auth_session_policy` consumer. `api()` injects Bearer and trips 401 → log-off; this read happens before login.

## Stage 2: AuthContext — `/api/me` without a Stytch session; skip extend

**Done when:** On first paint, `AuthProvider` keeps `loading === true` until `fetchAuthPassthrough()` settles. When the result is `true`, it calls `GET /api/me` even with no Stytch session, sets `user` from that JSON (`user_id` / `name` / `is_admin` — local operator from sibling 1 is `local-operator` / `Local Operator` / `true`), does not call `markHadSession`, does not call `fetchAuthSessionPolicy`, and does not call `startSessionExtendLoop`. When the result is `false`, the existing session-present `/api/me` path and AST-1374 extend loop are unchanged. `refreshMe()` calls `loadMe()` when passthrough is on even if `session` is null.

1. In `src/ui/frontend/src/contexts/AuthContext.tsx`:
   - Add import: `import { fetchAuthPassthrough } from "../lib/authPassthrough"`
   - Extend `AuthCtx` with `localAuthPassthrough: boolean | null` (`null` = fetch not settled). Add the same field to the `createContext` default (`null`) and to the `Provider` `value`.
   - Inside `AuthProvider`, after the existing `sessionPresent` line, add:

```typescript
  const [localAuthPassthrough, setLocalAuthPassthrough] = useState<boolean | null>(null)
```

   - Add this effect **before** the existing session/`loadMe` effect. It runs once on mount:

```typescript
  useEffect(() => {
    let cancelled = false
    void (async () => {
      const on = await fetchAuthPassthrough()
      if (!cancelled) setLocalAuthPassthrough(on)
    })()
    return () => {
      cancelled = true
    }
  }, [])
```

2. Replace the existing session/`loadMe` effect (`if (!sessionPresent) { identityResolvedRef... }`) with:

```typescript
  useEffect(() => {
    if (localAuthPassthrough === null) {
      setLoading(true)
      return
    }
    if (localAuthPassthrough) {
      loadMe()
      return
    }
    if (!sessionPresent) {
      identityResolvedRef.current = false
      setUser(null)
      setLoading(false)
      return
    }
    markHadSession()
    loadMe()
  }, [localAuthPassthrough, sessionPresent, sessionJwt, loadMe])
```

3. In `loadMe`, wrap the 401 log-off so a local `/api/me` failure cannot write `server-rejection` into sessionStorage. Keep the rest of `loadMe` (identityResolvedRef, `/api/me`, `setUser`, `finally`) as it is today. Change only the 401 branch and add `localAuthPassthrough` to the `useCallback` dependency list:

```typescript
        if (r.status === 401) {
          if (localAuthPassthrough !== true) {
            setLogOffReason("server-rejection")
            setAuthEpoch((n) => n + 1)
          }
          setUser(null)
          return
        }
```

4. At the top of the AST-1374 extend-loop effect, immediately **before** the existing `if (!sessionPresent) return`, add:

```typescript
    if (localAuthPassthrough !== false) return
```

   Add `localAuthPassthrough` to that effect's dependency array. Do **not** edit `sessionExtend.ts` or `authSessionPolicy.ts`. Do **not** start the loop when the signal is `true`, and do **not** start it while the signal is still `null`.

5. Change `refreshMe` to:

```typescript
  const refreshMe = useCallback(() => {
    if (localAuthPassthrough || session) loadMe()
  }, [localAuthPassthrough, session, loadMe])
```

6. Leave `useLayoutEffect` token wiring unchanged. A leftover Stytch JWT on localhost may still be sent; sibling 1's decorator ignores Bearer on local. Do **not** clear `setAuthTokenGetter` on passthrough.

⚠️ **Decision:** Keep `StytchProvider` in `App.tsx`. Unwrapping it would throw in `useStytch` / `useStytchSession` on Authenticate and the non-local path. AC for this ticket is that **our** code does not call Stytch session authenticate, extend, or refresh when the signal is on — that is the extend-loop skip plus Stage 3's Authenticate short-circuit. Do not treat SDK construction as in-scope.

⚠️ **Decision:** Skip extend even when a leftover Stytch cookie makes `sessionPresent` true. A stale localhost session is what currently triggers `session.authenticate` / `session_not_found`; the signal, not `sessionPresent`, is the gate.

## Stage 3: RequireAuth + Authenticate honor the same signal

**Done when:** With `localAuthPassthrough === true`, `RequireAuth` renders `children` without waiting for Stytch `isInitialized` and without mounting `Login` or `LogOffScreen`, even when `session` is null and even when `sessionStorage` still has `astral-had-stytch-session` / `astral-logoff-reason`. With `localAuthPassthrough === false`, Login / Log-off / `isInitialized` wait are byte-for-byte the current logic. Visiting `/authenticate` while the signal is on navigates to `/` and does not call `completeAuthenticateFromUrl`. While the signal is `null`, both surfaces show their existing loading paragraph (no Login flash).

1. In `src/ui/frontend/src/components/RequireAuth.tsx`:
   - Add `import { useAuth } from "../contexts/AuthContext"`
   - At the top of `RequireAuth`, after `useStytchSession()`, add `const { localAuthPassthrough } = useAuth()`
   - **Before** the existing `if (!isInitialized && !session)` block, insert:

```typescript
  if (localAuthPassthrough === null) {
    return <p>Loading…</p>
  }
  if (localAuthPassthrough) {
    return children
  }
```

   - Leave the rest of the function (`isInitialized` wait, `getLogOffReason` / `getHadSession` Log-off, `Login` when `!session`) unchanged. Do **not** edit `Login.tsx` or `LogOffScreen.tsx`.

2. In `src/ui/frontend/src/pages/Authenticate.tsx`:
   - Add `import { useAuth } from "../contexts/AuthContext"`
   - Inside `Authenticate`, after the existing hooks, add `const { localAuthPassthrough } = useAuth()`
   - At the top of the existing `useEffect`, **before** `if (!isInitialized)`, insert:

```typescript
    if (localAuthPassthrough === null) {
      return
    }
    if (localAuthPassthrough) {
      navigate("/", { replace: true })
      return
    }
```

   - Add `localAuthPassthrough` to the effect dependency array. Do **not** call `completeAuthenticateFromUrl` on the passthrough-true branch. Do **not** edit `stytchAuthenticateHandoff.ts`. When the signal is `false`, the existing `isInitialized` / `session` / handoff path stays.

⚠️ **Decision:** Short-circuit `/authenticate` on the same signal. Parent AC: with deploy env `local`, the SPA does not call Stytch session authenticate. Leaving the handoff live would still call `authenticateByUrl` if a leftover magic-link URL is opened on localhost.

### Hand verify (builder, after Stage 3)

Flask API on `:5001` and Vite on `:5173` from the epic worktree (`launch.sh`). Browser Network tab open.

1. `ASTRAL_DEPLOY_ENV=local`, no valid Stytch session (clear site data for localhost, or private window): open the app → jobs/nav, **not** Login, **not** Log-off. Network: `GET /api/auth_passthrough` → `{"local_auth_passthrough": true}`; `GET /api/me` 200 with `is_admin: true`. No request to Stytch `sessions/authenticate` (or equivalent session extend/refresh). `/api/nav_config` 200.

2. Same local deploy, leftover `astral-logoff-reason` in sessionStorage (set in DevTools then reload): still the app, not Log-off.

3. With deploy env `staging` (or unset): no Stytch session → Login still shows. With a live Stytch session, the extend loop still starts (`fetchAuthSessionPolicy` + interval). `GET /api/auth_passthrough` → `{"local_auth_passthrough": false}`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1441
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1438/AST-1441-local-spa-skip-login-and-session-refresh` @ `9f9b1a69cd00bcf7f6e03e55f677efeff5433a13`

## Traceability
AC1→S2+S3; AC2→S2+S3; AC3→S1+S2+S3. Parent AC1 API 200 / AC2 logs / AC4 401 / AC5 decorators → N/A — “Does not own Flask `@require_auth` internals, local-operator identity, or the public local-auth signal (sibling 1).”

## Findings

**discuss** — Stage 2 Decision (`StytchProvider` stays) vs child AC2 / parent AC3 (“SPA does not call Stytch session authenticate, extend, or refresh”). Plan skips the extend loop and `/authenticate` handoff and treats SDK construction as out of scope. `useStytch` / `useStytchSession` remain; a leftover Stytch cookie may still SDK-hydrate. Happy path (cleared site data) is specified. Does not block: unwrapping `StytchProvider` would throw, and sibling 1 already ignores Bearer on local. If leftover-cookie client authenticate is in AC2, suppress SDK recovery when the signal is on; if not, the Decision is enough.

No `fix-now` findings. Consumes AST-1440’s public boolean (fail-closed, raw `fetch`, not hostname). Login / Log-off unmounted via `RequireAuth`, not edited. `authPassthrough.ts` belongs in `lib/`. `pattern.auth.local-deploy-passthrough` is `proposed`; this child reads the endpoint, not the pattern id. Inner shells already wait on `authLoading` / `user`.

context_tokens≈40000

## Review (build)

**Built @ `f8d33808`** — `origin/sub/AST-1438/AST-1441-local-spa-skip-login-and-session-refresh`

- Stage 1: `fetchAuthPassthrough()` raw `GET /api/auth_passthrough`, fail-closed
- Stage 2: AuthContext loads `/api/me` without Stytch session; skip extend loop
- Stage 3: RequireAuth skips Login/Log-off; Authenticate skips `authenticateByUrl`
