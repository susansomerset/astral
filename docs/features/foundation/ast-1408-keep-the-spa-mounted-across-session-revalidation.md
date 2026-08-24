# Keep the SPA mounted across session revalidation

**Linear:** [AST-1408](https://linear.app/astralcareermatch/issue/AST-1408)
**Parent:** [AST-1406](https://linear.app/astralcareermatch/issue/AST-1406) — Page refreshes and modals are closed (lost!)
**Publish ref:** `sub/AST-1406/AST-1408-keep-the-spa-mounted-across-session-revalidation`

When Stytch extends the client session on the activity-extension cadence (AST-1374), or when `/api/me` is re-read while a session already exists, the authenticated React tree stays mounted. Loading placeholders are only for first session/identity resolution. Open overlays and in-progress edits survive those background ticks. This is the session-shell half of proposed `pattern.ui.in-place-live-refresh` — sibling **AST-1409** authors that pattern for Scheduled Actions; sibling **AST-1410** applies it to remaining list surfaces. This ticket does not change session duration, cadence values, log-off, or Vite HMR.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/contexts/AuthContext.tsx` | First-resolution-only `loading`; silent `/api/me` on later revalidation; keep extend-loop interval from restarting on JWT/session-object identity changes | ui |
| `src/ui/frontend/src/components/RequireAuth.tsx` | Show `Loading…` only when Stytch has not initialized **and** there is no session; keep children mounted when a session already exists | ui |
| `src/ui/frontend/src/components/AdminRoute.tsx` | Show `Loading…` only while identity is unresolved (`loading && user === null`); keep admin children mounted once `user` is known | ui |

**Out of this ticket (do not touch):** `src/ui/frontend/src/lib/sessionExtend.ts` (interval math stays), `src/ui/frontend/src/lib/authSessionPolicy.ts`, `src/utils/config.py` / `AUTH_CONFIG` literals, `LogOffScreen.tsx`, `sessionAuthMark.ts`, `Login.tsx`, `Authenticate.tsx`, `vite.config.ts`, list pages (including `AdminScheduledActions.tsx`, `AdminTaskPrompts.tsx`, `ListPage.tsx`), `AdminPerformanceMonitor.tsx`, `StateUiContext.tsx`, `CandidateContext.tsx`, `NavigationShell.tsx`. List/toggle live update is **AST-1409** / **AST-1410**. Do not add `pattern.ui.in-place-live-refresh` to the catalog — **AST-1409** owns that.

## Stage 1: AuthContext — loading is first identity resolution only

**Done when:** After `/api/me` has succeeded once for the current Stytch session, a later `session` object identity change or `sessionJwt` rotation (activity-extend `stytch.session.authenticate`) does **not** set `loading` back to `true`. The activity-extend `setInterval` is not cleared/restarted solely because the session object or JWT identity changed. First visit (no identity yet) still shows `loading === true` until `/api/me` finishes. Session loss still clears `user` and does not leave `loading` stuck true. Cadence integers in `AUTH_CONFIG` are unchanged.

1. In `src/ui/frontend/src/contexts/AuthContext.tsx`, add `useRef` to the existing `react` import (file already imports `useCallback`, `useContext`, `useEffect`, `useLayoutEffect`, `useState`).

2. Inside `AuthProvider`, immediately after the `loading` / `setAuthEpoch` state declarations, add:

```typescript
  const identityResolvedRef = useRef(false)
  const sessionPresent = Boolean(session)
```

3. Replace the `loadMe` body so it sets `loading` to `true` **only** when identity has not yet resolved for this session. Keep the rest of the try/401/catch/finally behavior (401 still calls `setLogOffReason("server-rejection")` and `setAuthEpoch`; failures still `setUser(null)`). Exact shape:

```typescript
  const loadMe = useCallback(async () => {
    if (!identityResolvedRef.current) {
      setLoading(true)
    }
    try {
      const r = await api("/api/me")
      if (!r.ok) {
        if (r.status === 401) {
          setLogOffReason("server-rejection")
          setAuthEpoch((n) => n + 1)
        }
        setUser(null)
        return
      }
      const data = await r.json() as MeUser
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      identityResolvedRef.current = true
      setLoading(false)
    }
  }, [])
```

4. Replace the session → `loadMe` effect (the one that currently depends on `[session, sessionJwt, loadMe]`) with:

```typescript
  useEffect(() => {
    if (!sessionPresent) {
      identityResolvedRef.current = false
      setUser(null)
      setLoading(false)
      return
    }
    markHadSession()
    loadMe()
  }, [sessionPresent, sessionJwt, loadMe])
```

Keep `sessionJwt` in this dependency list so a background identity re-read still happens when the JWT rotates — it must run through the silent `loadMe` path above, not a loading-gate remount. Keep the existing `useLayoutEffect` that calls `setAuthTokenGetter(() => sessionJwt)` unchanged (Bearer token must still update when the JWT rotates).

5. Change the AST-1374 extend-loop effect dependency array from `[session, stytch]` to `[sessionPresent, stytch]`. Keep the `if (!session)` / `if (!sessionPresent)` early return, the `cancelled` + `clear` race handling, `fetchAuthSessionPolicy()`, and `startSessionExtendLoop(stytch, policy)` call as they are today. Do not change the interval length, do not add an immediate tick, do not edit `sessionExtend.ts`.

⚠️ **Decision:** Do not split `loading` into a second context field (`revalidating`). Consumers already treat `loading` as “block the tree.” Changing its meaning to first-resolution-only is the smallest contract that keeps `AdminRoute` / `CandidateContext` / `StateUiContext` / `NavigationShell` from treating a JWT tick as a fresh boot. A new flag would require every consumer to be taught, which is sibling-shaped scope.

⚠️ **Decision:** Keep `/api/me` on JWT rotation (silent). The ticket names “identity is re-read in the background” as a real path; dropping the re-read would leave `user` stale if roles ever change mid-session. The defect is the loading-gate remount, not the GET.

⚠️ **Decision:** Key the extend loop on `sessionPresent` (boolean), not `session` object identity. `stytch.session.authenticate` replaces the session object; restarting the interval on every tick would reset the cadence clock and violate “does not change … activity-extension cadence.”

## Stage 2: Session-shell gates keep an already-authenticated tree mounted

**Done when:** `RequireAuth` still shows `Loading…` on first Stytch boot when there is no session, and still routes to `Login` / `LogOffScreen` when there is no session after init. If a session already exists, a transient `isInitialized === false` does not replace children with `Loading…`. `AdminRoute` still shows `Loading…` while `/api/me` has not produced a `user`, still redirects non-admins, and does not unmount admin children merely because `loading` is true after `user` is known. Log-off copy and branching in `LogOffScreen` are unchanged.

1. In `src/ui/frontend/src/components/RequireAuth.tsx`, replace the first-boot gate:

```typescript
  if (!isInitialized) {
    return <p>Loading…</p>
  }
```

with:

```typescript
  if (!isInitialized && !session) {
    return <p>Loading…</p>
  }
```

Leave the `logOffReason` / `getHadSession()` timeout promotion / `LogOffScreen` / `Login` / `return children` sequence exactly as it is after that gate. Do not edit `LogOffScreen.tsx` or `sessionAuthMark.ts`.

2. In `src/ui/frontend/src/components/AdminRoute.tsx`, destructure `user` from `useAuth()` alongside `isAdmin` and `loading`. Replace:

```typescript
  if (loading) {
    return <p>Loading…</p>
  }
```

with:

```typescript
  if (loading && user === null) {
    return <p>Loading…</p>
  }
```

Leave the `if (!isAdmin) { return <Navigate to="/jobs/recommended" replace /> }` and `return children` branches unchanged.

⚠️ **Decision:** Gate `AdminRoute` on `user === null`, not `!isAdmin`. A known non-admin (`user` set, `isAdmin` false) must still redirect, including if `loading` is somehow true. A known admin (`user` set, `isAdmin` true) must keep children mounted during a silent revalidation. First paint (`user` null, `loading` true) still shows `Loading…` so admin routes do not flash the jobs redirect before `/api/me` returns.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.** No fix-on-the-fly.
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-1406/AST-1408-keep-the-spa-mounted-across-session-revalidation`, then proceeds.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Traceability

- AC1 (overlay still open with in-progress edits after activity-extension cadence; page is not replaced by a loading placeholder) → Stage 1 (no `loading` flip / no extend-loop restart on JWT tick) + Stage 2 (RequireAuth / AdminRoute do not unmount an already-authenticated tree)
- AC2 (log-off still clears the session; Vite still reloads when frontend source files change) → RequireAuth log-off path untouched except the `isInitialized` conjunct; `LogOffScreen` / Vite config not edited
- Boundaries: no list/toggle live update (AST-1409 / AST-1410); no `AUTH_CONFIG` / `sessionExtend.ts` cadence edits; no overlay-draft persistence across intentional close

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1408
**Overall:** APPROVED
**Publish ref:** `sub/AST-1406/AST-1408-keep-the-spa-mounted-across-session-revalidation` @ `f894f2d5`

## Traceability

- AC1 → Stage 1 (`identityResolvedRef` + first-resolution-only `loading`; extend loop keyed on `sessionPresent`) + Stage 2 (`RequireAuth` / `AdminRoute` keep authenticated children mounted)
- AC2 → Stage 2 (`RequireAuth` log-off branch untouched; `LogOffScreen` / `vite.config.ts` explicitly out of scope)
- Boundaries → Files Changed exclusions + stage decisions (no `AUTH_CONFIG` / `sessionExtend.ts` / list pages / catalog pattern)

## Findings

### acceptable

- **Location:** Citations — `pattern.ui.in-place-live-refresh` (proposed)
- **Finding:** No `canon/patterns/**` draft exists yet; parent assigns catalog authoring to AST-1409.
- **Recommendation:** Accept for this child — plan explicitly defers catalog entry and limits scope to the session-shell half per parent sequencing.

### acceptable

- **Location:** Stage 1 — `loading` semantic shift
- **Finding:** `CandidateContext`, `StateUiContext`, `NavigationShell`, and `AdminDeployFooter` gate fetches on `authLoading`; first-resolution-only `loading` means they will not re-run on JWT rotation (by design).
- **Recommendation:** No plan change — matches stated decision to avoid teaching every consumer a new `revalidating` flag.

No `fix-now` or `discuss` blockers. R1–R5 pass. Layer placement (`contexts/` + `components/`, flat, no new dirs), in-scope-only exclusions, and DRY/minimal-diff approach conform. Current `AuthContext.tsx` root cause confirmed: `loadMe` always `setLoading(true)` and extend-loop deps include `session` object identity — plan targets both correctly. Status `Plan Ready`, assignee Joan — gate satisfied. Zero completed `[plan-discuss]` rounds.

context_tokens≈42000

## Review (build)

**Built @ `e1562b40`** — `origin/sub/AST-1406/AST-1408-keep-the-spa-mounted-across-session-revalidation`

- Stage 1 (`b1e82876`): `AuthContext` first-resolution-only `loading`; silent `/api/me` on JWT rotation; extend loop keyed on `sessionPresent`
- Stage 2 (`e1562b40`): `RequireAuth` loads only when uninitialized and no session; `AdminRoute` loads only while `user === null`

## Radia review

# Radia review — AST-1408

**Ticket:** AST-1408  
**Parent:** AST-1406  
**Publish ref:** `sub/AST-1406/AST-1408-keep-the-spa-mounted-across-session-revalidation` @ `d3381158`  
**Baseline:** `origin/dev`  
**Status gate:** Tests Passed (spawn prompt — trusted)  
**Overall:** CLEAN

---

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1408  
**Publish ref:** `d3381158` (`origin/sub/AST-1406/AST-1408-keep-the-spa-mounted-across-session-revalidation`)

## Statutes checked

Diff change set: paths `docs/features/foundation/ast-1408-*.md`, `docs/test-bible/frontend/{components,contexts,lib}.md`, `src/ui/frontend/src/{contexts/AuthContext,components/RequireAuth,components/AdminRoute}.tsx`, `tests/component/frontend/**`; layers **ui**, **docs**; change_types **add**, **modify**.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Tip `merge-tests(AST-1408)` pins Betty test SHA `6ef0d65b`. |
| `orch.git.commit-vocabulary` | universal | conforms | `docs` / `code` / `test` / `merge-tests` prefixes with ticket id. |
| `orch.git.flow-direction-inviolable` | universal | conforms | Sub-branch work; no reverse merges in diff. |
| `orch.git.ftr-sub-topology` | universal | conforms | Child publish ref `sub/AST-1406/AST-1408-…` used correctly. |
| `orch.git.merge-on-checkout` | universal | conforms | No evidence of dirty merge artifacts in reviewed diff. |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history; no rebase/force signals. |
| `orch.git.no-dev-agent-branches` | universal | conforms | No `dev-*` agent branch refs in publish path. |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1406 epic worktree; child scoped correctly. |
| `orch.git.three-permanent-branches` | universal | conforms | Changes live on sub publish ref, not main/dev conflation. |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Plan decisions documented; no unresolved product forks in diff. |
| `orch.pipeline.plan-is-bible` | universal | conforms | Implementation matches binding Stage 1–2 steps verbatim. |
| `orch.pipeline.project-scoped-queues` | universal | conforms | N/A to code content; pipeline placement correct. |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Review at Tests Passed per gate. |
| `orch.roles.archie-approves-statutes` | universal | conforms | No statute corpus edits. |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Test/bible changes in `test(AST-1408)` + `merge-tests`; product commits touch `src/` only. |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Ada; Radia read-only. |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Engineer product commits (`b1e82876`, `e1562b40`) scoped to plan files. |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path violations visible in engineer `code()` commits. |
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent/LLM grading paths in diff. |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No `do_task` / agent dispatch paths. |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector logic. |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch/dispatcher paths. |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch id emission. |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/release helpers. |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No agent-responses writes. |
| `astral.config.config-source-of-truth` | scoped | not-applicable | No config module edits. |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env wiring changes. |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifact paths. |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike files added. |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | `applies_when` paths not in diff. |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No core dispatch chain edits. |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single feature doc `docs/features/foundation/ast-1408-…md`. |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty commit touches tests/bible only, not `src/` or new feature docs. |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer `code()` commits: `AuthContext`, `RequireAuth`, `AdminRoute` only. |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | No core/external layer paths. |
| `astral.layers.import-direction` | scoped | conforms | UI imports unchanged in direction (React, Stytch, local `lib/`). |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/**` changes. |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No new hardcoded business-state strings; session policy still fetched from API. |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No core coat-check paths. |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No consult/render-verdict core paths. |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | Frontend session gates preserved/tightened; no backend route changes. |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed JSON edits. |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No catalog/seed conflicts. |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No seed hot-path changes. |
| `astral.seed.define-approved` | scoped | not-applicable | No define/seed work. |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No seed row mutations. |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage-join seed logic. |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No data-layer changes. |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No `src/data/**` changes. |
| `astral.standards.debug-contract-gated` | scoped | conforms | No new debug emission; extend-loop catch pre-existing. |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Minimal `useRef` + boolean dep swap; no scope creep. |
| `astral.standards.in-scope-only` | scoped | conforms | Product diff limited to three planned UI files; exclusions honored. |
| `astral.standards.logging-via-utils` | scoped | conforms | No `print()` / new loggers. |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | Runtime symbols unchanged; ticket id only in test descriptions. |
| `astral.standards.no-cross-contamination` | scoped | conforms | No unrelated module rewrites. |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | No new hardcoded domain sets. |
| `astral.standards.public-then-helpers` | scoped | conforms | Provider/export surface unchanged. |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No `src/utils/**` changes. |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state-machine transitions. |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state logic. |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run-chain paths. |
| `astral.ui.frontend-file-placement` | scoped | conforms | Edits in existing `contexts/` and `components/` paths. |
| `astral.ui.naming-conventions` | scoped | conforms | `identityResolvedRef`, `sessionPresent` follow local naming. |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No worker/process config touched. |

**Sweep count:** 65 active statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan references proposed `pattern.ui.in-place-live-refresh` (AST-1409 catalog owner); Joan accepted deferral — not an approved-catalog citation. |

## Plan adherence

Implementation matches Joan-approved plan Stages 1–2 exactly:

- **Stage 1 (`AuthContext.tsx`):** `identityResolvedRef` gates first-resolution-only `loading`; `sessionPresent` replaces `session` object identity in extend-loop and loadMe effect deps; `sessionJwt` retained for silent background `/api/me` re-read; `useLayoutEffect` token getter unchanged.
- **Stage 2:** `RequireAuth` loading gate is `!isInitialized && !session`; `AdminRoute` loading gate is `loading && user === null`.
- **Boundaries respected:** No edits to `sessionExtend.ts`, `AUTH_CONFIG`, list pages, `LogOffScreen`, Vite, or catalog pattern authoring.
- **Estimate (3):** Footprint matches — three UI files + tests/bible; no scope inflation.
- **Cross-ticket:** No AST-1409/1410 list-live-update work smuggled in.
- **Joan straggler (C4):** Plan-rubric APPROVED attached; no Excluded-statute list — no stragglers.

Betty manifest (`docs/test-bible/frontend/contexts.md`) aligns with added `AST-1408:*` cases and stable `stytchMock` client (needed to assert extend-loop identity without false restarts).

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `tests/component/frontend/contexts/test_AuthContext.test.tsx`
- **Finding:** No component test covers silent revalidation **failure** (network error or non-401 `/api/me` failure) while JWT rotates — only success and in-flight-with-prior-user paths.
- **Recommendation:** Optional follow-up for Betty if UAT wants explicit regression on `setUser(null)` during background revalidation; not blocking — failure path is pre-existing `loadMe` behavior and end-state matches prior code after request completes.

## What's solid

- Root cause directly addressed: `loadMe` no longer flips `loading` on every JWT tick; extend loop no longer restarts on session object identity churn.
- Gate components (`RequireAuth`, `AdminRoute`) correctly distinguish first-resolution vs already-authenticated tree — the session-shell half of AST-1406 AC1.
- Engineer/test separation clean: `code()` commits touch plan UI files only; Betty owns test tree + bible.
- Component tests exercise the three behaviors the ticket names (silent JWT re-read, extend-loop stability, session-loss loading reset, gate keep-mounted paths).

## Frame diff

(none) — first Radia code-rubric pass on this child. Prior issue-doc sections: plan @ `f894f2d5`, Joan APPROVED, build stub @ `e1562b40`; tip now `d3381158` after `merge-tests(AST-1408)`.

## Notes

- Joan plan-rubric verdict attached (APPROVED); no Excluded-statute table to straggler-check.
- `CandidateContext` / `StateUiContext` / `NavigationShell` / `AdminDeployFooter` will not re-fetch on JWT rotation — explicitly accepted in plan Stage 1 decision; not a defect for this ticket.
- §5f (debug contract) and §5g (external LLM cleanliness) not triggered — UI-only diff.

context_tokens≈38000
