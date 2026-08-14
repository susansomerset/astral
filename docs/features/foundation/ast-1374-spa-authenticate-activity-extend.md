# SPA authenticate duration + activity session extend

**Linear:** [AST-1374](https://linear.app/astralcareermatch/issue/AST-1374)
**Parent:** [AST-1372](https://linear.app/astralcareermatch/issue/AST-1372) — Extend Stytch sessions
**Publish ref:** `sub/AST-1372/AST-1374-spa-authenticate-activity-extend`

Wire the SPA authenticate handoff and in-app session-extend loop to the config-backed policy from sibling **AST-1373** (`GET /api/auth_session_policy`: `session_duration_minutes`, `activity_extension_interval_minutes`). Remove the hardcoded client `SESSION_DURATION_MINUTES = 60`. Keep AST-624/625 log-off behavior when the session finally expires. Does **not** invent config keys or the policy API.

**Depends on:** AST-1373 (AUTH_CONFIG + public policy API) — already on `origin/ftr/ast-1372-extend-stytch-sessions` / merged into this sub tip.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/authSessionPolicy.ts` | **New** — type + `fetchAuthSessionPolicy()` for `GET /api/auth_session_policy` | ui |
| `src/ui/frontend/src/lib/stytchAuthenticateHandoff.ts` | Remove `SESSION_DURATION_MINUTES = 60`; fetch policy; pass `session_duration_minutes` into `authenticateByUrl` | ui |
| `src/ui/frontend/src/lib/sessionExtend.ts` | **New** — start/clear interval that calls `stytch.session.authenticate` while a client session exists | ui |
| `src/ui/frontend/src/contexts/AuthContext.tsx` | While Stytch session exists, start the extend loop from policy; clear on session loss / unmount | ui |

**Out of this ticket (do not touch):** `src/utils/config.py`, `src/ui/api/api_system.py`, `Login.tsx` magic-link `loginExpirationMinutes` (email-link TTL, not Stytch session lifetime), `LogOffScreen.tsx` / `RequireAuth.tsx` copy or branching, Flask JWT validation, admin gating, `/api/me`, Stytch Dashboard.

## Stage 1: Policy fetch + authenticate handoff uses configured duration

**Done when:** `completeAuthenticateFromUrl` no longer contains a hardcoded `60` (or any other inline session-duration literal). On success it calls `authenticateByUrl({ session_duration_minutes })` with the integer from `GET /api/auth_session_policy`. If the policy request fails or the JSON lacks a positive `session_duration_minutes`, handoff returns `outcome: "error"` (no fallback duration). Magic-link and OAuth both go through this same path.

1. Create `src/ui/frontend/src/lib/authSessionPolicy.ts` with:

```typescript
export interface AuthSessionPolicy {
  session_duration_minutes: number
  activity_extension_interval_minutes: number
}

/** Public non-secret policy (AST-1373). Use raw fetch — not api() — so pre-login handoff stays free of Bearer/401 log-off coupling. */
export async function fetchAuthSessionPolicy(): Promise<AuthSessionPolicy> {
  const r = await fetch("/api/auth_session_policy", { credentials: "include" })
  if (!r.ok) {
    throw new Error(`Session policy unavailable (${r.status})`)
  }
  const data = (await r.json()) as Partial<AuthSessionPolicy>
  const session_duration_minutes = Number(data.session_duration_minutes)
  const activity_extension_interval_minutes = Number(
    data.activity_extension_interval_minutes,
  )
  if (
    !Number.isFinite(session_duration_minutes) ||
    session_duration_minutes <= 0 ||
    !Number.isFinite(activity_extension_interval_minutes) ||
    activity_extension_interval_minutes <= 0
  ) {
    throw new Error("Session policy response invalid")
  }
  return { session_duration_minutes, activity_extension_interval_minutes }
}
```

2. In `src/ui/frontend/src/lib/stytchAuthenticateHandoff.ts`:
   - Delete `const SESSION_DURATION_MINUTES = 60`.
   - Import `fetchAuthSessionPolicy`.
   - Inside `completeAuthenticateFromUrl`, **after** the `parsed.handled` check succeeds and **before** `authenticateByUrl`, call `await fetchAuthSessionPolicy()` inside the existing `try` (or wrap so policy failures become `outcome: "error"` with `message` from the thrown error / a short default).
   - Pass `{ session_duration_minutes: policy.session_duration_minutes }` to `authenticateByUrl`.
   - Do **not** add a hardcoded fallback duration on fetch/parse failure.

3. Leave `Authenticate.tsx` unchanged — it already calls `completeAuthenticateFromUrl(stytch)` once per mount.

⚠️ **Decision:** Raw `fetch` for policy, not `api()`, so authenticate handoff works with no Bearer token and does not trip `api()`'s 401 → log-off side effects on a public route.

⚠️ **Decision:** No fallback to `60` (or any other literal) when policy is unavailable — that would reintroduce the hardcoded duration this ticket removes and violate AC.

## Stage 2: Activity session extend while SPA session exists

**Done when:** With a live Stytch client session, `AuthProvider` starts a timer whose period is `activity_extension_interval_minutes * 60_000` ms. Each tick, if `stytch.session.getSync()` is truthy, calls `stytch.session.authenticate({ session_duration_minutes })` with the same policy duration used at login. Timer clears when the session becomes null or the provider unmounts. Failed extend calls do **not** redesign log-off — leave Stytch session state alone; when the session eventually disappears, existing `RequireAuth` + `LogOffScreen` (timeout / server-rejection) still apply. First extend waits until the first interval elapses (no immediate tick on start).

1. Create `src/ui/frontend/src/lib/sessionExtend.ts` with a minimal Stytch surface and a start helper:

```typescript
export interface StytchSessionExtendClient {
  session: {
    getSync: () => unknown
    authenticate: (opts: {
      session_duration_minutes: number
    }) => Promise<unknown>
  }
}

/** Returns clear() for the interval. Does not fire immediately — first tick after intervalMs. */
export function startSessionExtendLoop(
  stytch: StytchSessionExtendClient,
  opts: {
    session_duration_minutes: number
    activity_extension_interval_minutes: number
  },
): () => void {
  const intervalMs = opts.activity_extension_interval_minutes * 60_000
  const tick = () => {
    if (!stytch.session.getSync()) return
    void stytch.session
      .authenticate({
        session_duration_minutes: opts.session_duration_minutes,
      })
      .catch(() => {
        /* leave session as-is; natural expiry → existing log-off path */
      })
  }
  const id = window.setInterval(tick, intervalMs)
  return () => window.clearInterval(id)
}
```

2. In `src/ui/frontend/src/contexts/AuthContext.tsx`:
   - Import `fetchAuthSessionPolicy` and `startSessionExtendLoop`.
   - Add a `useEffect` that depends on `session` (truthiness) and `stytch`:
     - If `!session`, return (no loop).
     - Let a local `cancelled = false`.
     - `void (async () => { try { const policy = await fetchAuthSessionPolicy(); if (cancelled) return; clear = startSessionExtendLoop(stytch, policy) } catch { /* no loop if policy unavailable; session still expires on create-time duration */ } })()`.
     - Cleanup: set `cancelled = true`; call `clear?.()`.
   - Do **not** change `/api/me` loading, Bearer wiring, `markHadSession`, or unauthorized handling.

3. Do **not** edit `RequireAuth.tsx`, `LogOffScreen.tsx`, or `sessionAuthMark.ts`.

⚠️ **Decision:** Cadence is a quiet `setInterval` while a Stytch session exists (parent brief + AST-1373 contract), not pointer/keyboard activity debounce (archived AST-1202 discussion). Product rule for this epic is config-backed interval extend while the SPA tab keeps a live session.

⚠️ **Decision:** Swallow extend `authenticate` rejections in the tick — do not call `setLogOffReason` from the extend loop. When the session is actually gone, existing RequireAuth timeout / api 401 paths remain the only log-off triggers.

### Sibling contract (AST-1373 — consume only)

| Field | Type | SPA use |
|-------|------|---------|
| `session_duration_minutes` | int | `authenticateByUrl` + `session.authenticate` |
| `activity_extension_interval_minutes` | int | `setInterval` period (minutes → ms) |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Traceability

- AC1 (authenticate uses configured duration) → Stage 1
- AC2 (extend on cadence while session exists) → Stage 2
- AC3 (idle → existing log-off) → Stage 2 decisions + untouched RequireAuth/LogOffScreen
- AC4 (no regression login / Bearer / admin / Login vs log-off) → no edits to those surfaces; handoff + AuthContext only

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1374
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend` @ `6d2d3cbd9cf7b92a3cff6bb89c88f371e5b151d1`

## Traceability
AC1→Stage 1; AC2→Stage 2; AC3→Stage 2 (swallow extend errors + untouched RequireAuth/LogOffScreen); AC4→scoped footprint only — AUTH_CONFIG/policy API N/A (AST-1373).

## Findings

### acceptable — missing `## Self-Assessment`
**Location:** plan doc tail  
**Finding:** No formal self-assessment block (scope/conf axes).  
**Recommendation:** Optional at this footprint; not blocking.

### acceptable — duplicate policy fetch
**Location:** Stage 1 handoff + Stage 2 AuthContext  
**Finding:** `fetchAuthSessionPolicy()` called independently in handoff and extend-loop setup.  
**Recommendation:** Fine for clarity; optional shared cache later if needed.

context_tokens≈22000

---

[plan-rubric] PROCEED (Commit: 6d2d3cbd) SPA policy wiring ready

AST-1374 plan approved.

---

**Gate:** Plan Ready, assignee Joan — OK. No `[plan-discuss]` rounds.

**Dependency:** `GET /api/auth_session_policy` present on publish-ref tip (AST-1373 landed). `SESSION_DURATION_MINUTES = 60` confirmed in `stytchAuthenticateHandoff.ts` — plan targets the right constant; `Login.tsx` `loginExpirationMinutes` correctly left alone (email-link TTL ≠ session lifetime).

**R6:** Four frontend files, correct placement (`lib/`, `contexts/`). Raw `fetch` for pre-login policy (not `api()`) is justified. No fallback duration on policy failure — conforms to `astral.standards.no-hardcoded-sets`. Policy-driven cadence/duration — conforms to `astral.layers.ui-config-driven-business-logic`. Boundaries hold (`config.py`, `api_system.py`, log-off surfaces untouched).

**In-session R3:** Cited statutes + universals — all `conforms`; no `fix-now`.
