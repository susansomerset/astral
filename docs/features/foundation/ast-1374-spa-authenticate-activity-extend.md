<!-- linear-archive: AST-1374 archived 2026-08-31 -->

## Linear archive (AST-1374)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1374/spa-authenticate-duration-activity-session-extend-extend-stytch  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1372 — Extend Stytch sessions  
**Blocked by / blocks / related:** parent: AST-1372

### Description

## What this implements

Owns wiring login/authenticate handoff and in-app activity extension to the config-backed policy (Stytch authenticate with configured duration on cadence while a session exists); removes the hardcoded client session-duration constant. Does **not** own inventing the config keys or policy API (after sibling AUTH_CONFIG child). Must keep AST-624/625 log-off behavior intact when the session finally expires.

## Citations

`astral.standards.no-hardcoded-sets`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`

## Acceptance criteria

* Authenticate handoff (magic-link and Google OAuth) creates a Stytch session whose lifetime matches the configured duration — not a leftover hardcoded 60.
* With a valid session and the SPA open, session expiry is reset on the configured extension cadence via Stytch session authenticate using that same duration.
* If the user stops using the app long enough that no successful extend keeps the session alive, they see the existing log-off / timeout path rather than a silent broken shell.
* No regression to login, Bearer API calls, admin gating, or first-time visitor Login vs log-off distinction.

## Boundaries

* Does **not** invent config keys or the policy API (sibling).
* Does **not** redesign log-off screen; does not change Flask JWT validation or admin gating.

## Notes for planning

After AUTH_CONFIG sibling. Keep AST-624/625 log-off intact.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/ast-1372-extend-stytch-sessions`, child `sub/AST-1372/<this-id>-spa-authenticate-activity-extend`. Created at dispatch-parent.

## QA test manifest

1. Policy fetch: `tests/component/frontend/lib/test_authSessionPolicy.test.ts`
2. Extend loop helper: `tests/component/frontend/lib/test_sessionExtend.test.ts`
3. Handoff (configured duration + no fallback): `tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts`
4. Authenticate page §6c: `tests/component/frontend/pages/test_Authenticate.test.tsx`
5. AuthContext extend start: `tests/component/frontend/contexts/test_AuthContext.test.tsx`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_authSessionPolicy.test.ts \
  ../../../tests/component/frontend/lib/test_sessionExtend.test.ts \
  ../../../tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts \
  ../../../tests/component/frontend/pages/test_Authenticate.test.tsx \
  ../../../tests/component/frontend/contexts/test_AuthContext.test.tsx
```

**Bible shasums** (`origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend`):

* `docs/test-bible/frontend/lib.md` · `ee4daa3684208c12b66b4a937be9e21ea6744c0f`

### Comments

#### katherine — 2026-08-14T21:33:11.363Z
`origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend` @ `04f3d5c9ade1d01037220cb5dc01b1c58095f158` · §9a clean · ftr dry-run clean

#### radia — 2026-08-14T21:32:05.151Z
[code-rubric] PROCEED (Commit: adbbdade) SPA policy wiring clean

#### betty — 2026-08-14T21:29:03.783Z
`origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend` @ `adbbdade` · SPA session extend tests

#### joan — 2026-08-14T21:21:41.572Z
[plan-rubric] PROCEED (Commit: 6d2d3cbd) SPA policy wiring ready

#### katherine — 2026-08-14T21:20:20.952Z
`origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend` @ `6d2d3cbd9cf7b92a3cff6bb89c88f371e5b151d1` · plan ready for Joan

---

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

## Review (build)

**Built @ `0fa41ec6`** — `origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend`

- Stage 1: `authSessionPolicy.ts` + handoff fetches policy; hardcoded `60` removed
- Stage 2: `sessionExtend.ts` + `AuthContext` interval extend while session exists

## Radia review

# Radia review — AST-1374

**Status gate:** Tests Passed (spawn prompt; trusted).  
**Baseline:** `origin/dev`  
**Publish ref:** `origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend` @ `adbbdade`  
**Diff note:** `origin/dev...origin/sub/AST-1374-…` reports multiple merge bases (82 files — sibling epic noise). Scored against AST-1374 footprint: engineer `0fa41ec6` (4 frontend `src/` files) + Betty `dc0af136` + single `merge-tests(AST-1374)` @ `adbbdade`.

---

```
[code-rubric] revision=2
```

**Rubric:** code-rubric.v2  
**Ticket:** AST-1374  
**Publish ref:** `adbbdade15a7a9680a48afa9782466a4471932b2`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single `merge-tests(AST-1374)` @ `adbbdade` pins `origin/tests` `dc0af136`. |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `merge-tests` / `docs` vocabulary correct. |
| `orch.git.flow-direction-inviolable` | universal | conforms | Product on `sub/*`; tests from `origin/tests`. |
| `orch.git.ftr-sub-topology` | universal | conforms | Child publish ref `sub/AST-1372/AST-1374-…` correct. |
| `orch.git.merge-on-checkout` | universal | conforms | No merge/checkout violation evident. |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history. |
| `orch.git.no-dev-agent-branches` | universal | conforms | No agent publish refs. |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1372 epic pattern. |
| `orch.git.three-permanent-branches` | universal | conforms | `dev` / `tests` / `main` respected. |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Cadence/extend behavior pre-decided in plan/parent; no new forks. |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match implementation. |
| `orch.pipeline.project-scoped-queues` | universal | conforms | N/A to diff substance. |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child gate satisfied. |
| `orch.roles.archie-approves-statutes` | universal | conforms | N/A to diff substance. |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty `test(AST-1374)` + one merge-tests; engineer `src/` only. |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | N/A to diff substance. |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine assignee; review does not reassign. |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Engineer `0fa41ec6` — `src/ui/frontend/**` only. |
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent/core grading paths. |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No dispatch paths. |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector paths. |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch layer. |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch layer. |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/process paths. |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No batch responses paths. |
| `astral.config.config-source-of-truth` | scoped | not-applicable | No `config.py` / backend config edits (AST-1373). |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No backend config/env changes. |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug paths. |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike paths. |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch paths. |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No run-next paths. |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Plan at `docs/features/foundation/ast-1374-….md`. |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty `dc0af136` — test-bible + `tests/` only. |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer commit frontend `src/` only. |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | No core/external changes. |
| `astral.layers.import-direction` | scoped | not-applicable | Frontend-only; no cross-layer Python imports. |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/**`. |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Duration/cadence from `GET /api/auth_session_policy`; hardcoded `60` removed; plan documents raw-`fetch` pre-login exception. |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check paths. |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No render/consult paths. |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | No Flask route changes (AST-1373). |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed paths. |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No seed paths. |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No seed paths. |
| `astral.seed.define-approved` | scoped | not-applicable | No seed paths. |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No seed paths. |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No seed paths. |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No data layer. |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No `src/data/**`. |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | No `debug=` surfaces. |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Small focused modules (`authSessionPolicy`, `sessionExtend`) + thin AuthContext wiring. |
| `astral.standards.in-scope-only` | scoped | conforms | No `config.py`, `api_system.py`, RequireAuth, LogOffScreen, or Login TTL edits. |
| `astral.standards.logging-via-utils` | scoped | not-applicable | No logging added. |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Domain names (`fetchAuthSessionPolicy`, `startSessionExtendLoop`). |
| `astral.standards.no-cross-contamination` | scoped | conforms | Extend loop isolated; existing `/api/me` / log-off paths untouched. |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | `SESSION_DURATION_MINUTES = 60` removed; no fallback duration on policy failure. |
| `astral.standards.public-then-helpers` | scoped | not-applicable | New modules are all public exports; no helper scatter issue. |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No utils/data Python. |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state paths. |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state paths. |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run paths. |
| `astral.ui.frontend-file-placement` | scoped | conforms | New files in `lib/`; AuthContext edit in `contexts/`. |
| `astral.ui.naming-conventions` | scoped | conforms | camelCase TS modules/functions match existing frontend style. |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No server config. |

**Sweep count:** 65 active statutes scored (1 retired `astral.config.pass-threshold-vs-score-floor` ignored).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited in plan)* | — | No "Patterns to reuse" section; Joan informal refs align with implementation (config-backed policy, no SPA literals). |

## Plan adherence

- **Stage 1:** `authSessionPolicy.ts` matches plan; `completeAuthenticateFromUrl` fetches policy before `authenticateByUrl`; hardcoded `60` gone; policy failure → `outcome: "error"` with no `authenticateByUrl` call.
- **Stage 2:** `sessionExtend.ts` interval loop (no immediate tick, swallow extend rejections with comment); `AuthContext` starts loop when `session` truthy, clears on unmount; race guard after `await` (`cancelled` + immediate `clear()`).
- **Estimate 3:** Four frontend files + focused tests — fits.
- **AST-1373 dependency:** Consumes `GET /api/auth_session_policy` only; does not invent keys or backend routes.
- **AST-1372 boundaries:** `Login.tsx` `loginExpirationMinutes: 60` untouched (email-link TTL); RequireAuth / LogOffScreen / `sessionAuthMark` untouched.
- **Joan straggler (C4):** Joan verdict attached; no excluded-statute stragglers on this footprint.

## C6 judgment aids (§5a)

| Topic | Result |
|-------|--------|
| Imports (B1) | Clean module imports; no lazy-import issues. |
| Layer compliance (B2) | Frontend-only; no Python layer bends. |
| Silent failure (D2) | Extend-loop `.catch(() => { /* comment */ })` and AuthContext policy `catch` are plan-documented bounded swallow — acceptable per §5b. |
| Fallbacks (D3) | No fallback duration; policy validation rejects non-positive values. |
| Logging (E1) | None added. |
| Config in UI (G1) | Session policy read from server endpoint, not inlined business rules. |
| §5f / §5g | Not triggered. |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**
- **Duplicate policy fetch** — handoff and AuthContext each call `fetchAuthSessionPolicy()` independently (Joan already noted acceptable); optional shared cache later if latency matters.
- **Cadence invariant** — no client check that `activity_extension_interval_minutes < session_duration_minutes`; relies on server config (AST-1373). Fine at this footprint.
- **Three-dot diff pollution** — `origin/dev...publish-ref` unusable for scope (multiple merge bases). Downstream agents should use per-ticket commits or `f23fabf0..adbbdade` when reviewing this sub lineage.

## What's solid

- Hardcoded session lifetime fully removed from handoff path; tests explicitly assert configured `20`, not `60`.
- Raw `fetch` for pre-login policy avoids `api()` 401 → log-off coupling — matches plan decision.
- Extend loop tests use fake timers: no immediate tick, cadence authenticate, skip when `getSync` falsy, swallow rejection.
- `stytchMock` extended with `getSync` / `session.authenticate` for extend coverage.
- AuthContext tests stub policy fetch in `beforeEach` so existing cases stay stable.

## Frame diff

(none)

## Notes

- Joan plan-rubric verdict attached @ `6d2d3cbd`; no straggler.
- AST-1373 sibling dependency present on publish-ref tip (required).
- C7 complete; Chuckles may append to issue doc, commit `docs(AST-1374): Radia review — clean`, post slim upshot, advance to **Review Posted** → **User Testing** (PROCEED path).

context_tokens≈26000

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] PROCEED (Commit: adbbdade) SPA policy wiring clean
```

## Resolution

**2026-08-14** — Radia CLEAN (no fix-now / discuss). No product changes.
§9a: merged `origin/dev` onto this sub (`sync(dev)` @ `85960ea7`) so publish-ref dry-runs clean into `origin/dev` and `origin/ftr/ast-1372-extend-stytch-sessions`.
