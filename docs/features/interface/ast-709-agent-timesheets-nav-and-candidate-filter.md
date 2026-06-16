# Agent Timesheets nav escape and candidate filter stability (Nav Menu stops working while on agent timesheets)

**Linear:** [AST-709](https://linear.app/astralcareermatch/issue/AST-709/agent-timesheets-nav-escape-and-candidate-filter-stability-nav-menu-stops)  
**Parent:** [AST-705](https://linear.app/astralcareermatch/issue/AST-705/nav-menu-stops-working-while-on-agent-timesheets)  
**Publish ref:** `sub/AST-705/AST-709-agent-timesheets-nav-and-candidate-filter`

Susan is trapped on Agent Timesheets: sidebar clicks briefly change the address bar, then snap back to `/admin/agent_timesheets`. AST-634 added URL-backed candidate sync here; AST-662 fixed the same class of race on Execution History (`manualPinRef` + memoized `urlBacked`) but deferred Agent Timesheets. This ticket restores reliable nav escape from Agent Timesheets and completes candidate-filter stability (nav default, **All**, manual pin, direct candidate-to-candidate switch) without changing timesheet APIs, export semantics, or nav config.

## Root cause (plan-time)

`AdminAgentTimesheets.tsx` passes an **inline** `urlBacked` object to `useAdminCandidateFilter` on every render. The hook's `applyFilter` `useCallback` depends on `[urlBacked]`, so `applyFilter` gets a new identity every render. The nav-sync `useEffect` depends on `applyFilter` and, while `syncWithNav === true`, calls `setCandidateParam(selectedId)` → `setSearchParams(..., { replace: true })` on the **current** route every render cycle. That fights React Router `NavLink` navigation and produces the flicker-and-revert Susan reported. Execution History already avoids this via memoized `urlBacked` (AST-662); Agent Timesheets does not.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts` | Stabilize `applyFilter` deps: depend on `urlBacked?.setValue` instead of whole `urlBacked` object | ui |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Memoize `urlBacked` passed to hook (parity with `AdminPerformanceMonitor.tsx` post-AST-662) | ui |
| `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` | Regression: inline `urlBacked` object identity churn does not spam `setValue` from nav-sync | ui (QA) |
| `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` | Regression: direct c1→c2 switch refetches; nav click away from Timesheets sticks on destination | ui (QA) |

**Out of scope:** `NavigationShell.tsx`, nav config, timesheet API, `AdminPerformanceMonitor.tsx`, `AdminScheduledActions.tsx`, backend.

## Stage 1: Stabilize `applyFilter` in shared hook

**Done when:** `applyFilter` identity is stable across re-renders when `urlBacked.setValue` is unchanged (even if parent passes a new inline `urlBacked` object each render). Nav-sync effect no longer fires on every render while `syncWithNav === true`. Existing hook tests pass unchanged.

1. In `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts`, after `const urlBacked = options?.urlBacked`, add:
   ```ts
   const urlSetValue = urlBacked?.setValue
   ```
2. Replace `applyFilter` implementation and deps:
   ```ts
   const applyFilter = useCallback(
     (next: AdminCandidateFilterValue) => {
       if (urlSetValue) urlSetValue(next)
       else setLocalFilter(next)
     },
     [urlSetValue],
   )
   ```
3. Do **not** change `manualPinRef`, `setCandidateFilter`, hook return shape, or nav-sync effect guard logic beyond what falls out of stable `applyFilter`.
4. Run from repo root:
   ```bash
   npm run test -- tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx
   ```
   All tests in that file must pass before stage commit.

⚠️ **Decision:** Fix at the hook layer (not page-only memoization) because the unstable `urlBacked` object dependency is the root defect; `setCandidateParam` is already a stable `useCallback`, so depending on `urlSetValue` stops nav-sync spam for Agent Timesheets **and** any future URL-backed consumer. Safe for Scheduled Actions (no `urlBacked`) and Execution History (already memoized — behavior unchanged).

## Stage 2: Memoize `urlBacked` on Agent Timesheets

**Done when:** `AdminAgentTimesheets` passes a memoized `urlBacked` to the hook, matching the AST-662 pattern on Execution History. Page renders and existing AST-634 filter behavior unchanged.

1. In `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx`, verify `useMemo` is imported from `react` (add if missing).
2. After `const urlCandidate = candidateIdFromParams(searchParams)` and `setCandidateParam` definition (~lines 107–116), replace the inline `urlBacked` argument with:
   ```ts
   const urlBacked = useMemo(
     () => ({ value: urlCandidate, setValue: setCandidateParam }),
     [urlCandidate, setCandidateParam],
   )
   const { candidateFilter, setCandidateFilter, syncWithNav, candidates } = useAdminCandidateFilter({
     urlBacked,
     urlPresentDisablesSync: true,
   })
   ```
3. Leave `initialCandidateDefaultApplied` effect, `filters` `useMemo`, `loadData`, date/batch filters, totals bars, export, and `ListPage` wiring unchanged.
4. Run from repo root:
   ```bash
   npm run test -- tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx
   ```
   All tests in that file must pass before stage commit.

⚠️ **Decision:** Belt-and-suspenders parity with `AdminPerformanceMonitor.tsx` lines 118–125 even though Stage 1 makes inline objects safe — keeps both URL-backed admin pages structurally identical for future readers.

## Stage 3: Component regression tests (Betty manifest — AC coverage)

**Done when:** Vitest covers nav-sync stability under inline `urlBacked`, direct candidate switch on Timesheets, and sidebar nav escape; existing AST-634 Timesheets tests still pass.

1. In `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx`, add test `inline urlBacked identity churn does not spam setValue from nav sync`:
   - `localStorage.setItem("astral_selected_candidate", "c1")`
   - `let urlValue = ""`
   - `const setValue = vi.fn((next: string) => { urlValue = next })`
   - Render hook with inline factory: `() => useAdminCandidateFilter({ urlBacked: { value: urlValue, setValue }, urlPresentDisablesSync: false })`
   - `await waitFor(() => expect(setValue).toHaveBeenCalled())` — initial nav default may call once
   - Record `setValue.mock.calls.length` as `afterInit`
   - `rerender()` five times (simulate parent re-renders with new inline object)
   - Assert `setValue.mock.calls.length === afterInit` (no additional nav-sync spam)

2. In `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx`, inside `describe("AST-634 admin candidate filter")` or a new `describe("AST-709 nav and candidate filter")`, add test `direct candidate switch c1 to c2 refetches timesheets without All intermediate step`:
   - Define rows:
     ```ts
     const rowC1 = { ...row, agent_req_id: "req-c1", candidate_id: "c1" }
     const rowC2 = { ...row, agent_req_id: "req-c2", candidate_id: "c2" }
     ```
   - `const calls: string[] = []`
   - `installBaseApiMocks` handler for `/api/admin/timesheets`: push `url` to `calls`; if `url.includes("candidate_id=c2")` return `[rowC2]`; if `url.includes("candidate_id=c1")` return `[rowC1]`; else return `[rowC1, rowC2]`
   - `/api/candidates` returns c1 + c2 (reuse pattern from existing AST-634 test)
   - `renderWithProviders(<AgentTimesheets />, { router: { initialEntries: ["/admin/agent_timesheets?candidate_id=c1"] } })`
   - `await waitFor(() => expect(screen.getByText("req-c1")).toBeInTheDocument())` (or match on candidate_id column cell `"c1"`)
   - `await userEvent.selectOptions(screen.getByLabelText("Candidate", { selector: "select" }), "c2")`
   - `await waitFor(() => expect(calls.some(u => u.includes("candidate_id=c2"))).toBe(true))`
   - `await waitFor(() => expect(screen.getByText("c2")).toBeInTheDocument())` in table body
   - `expect((screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement).value).toBe("c2")`

3. In the same describe block, add test `nav click away from Agent Timesheets stays on destination` (jsdom integration):
   - Import `createMemoryRouter`, `RouterProvider` from `react-router-dom`
   - Import `NavigationShell` from `../../../../src/ui/frontend/src/components/NavigationShell`
   - Stub destination: `function ScheduledStub() { return <div>Scheduled Actions Page</div> }`
   - Build router:
     ```ts
     const router = createMemoryRouter(
       [
         {
           element: (
             <AuthProvider>
               <CandidateProvider>
                 <NavigationShell />
               </CandidateProvider>
             </AuthProvider>
           ),
           children: [
             { path: "admin/agent_timesheets", element: <AgentTimesheets /> },
             { path: "admin/scheduled_actions", element: <ScheduledStub /> },
           ],
         },
       ],
       { initialEntries: ["/admin/agent_timesheets?candidate_id=c1"] },
     )
     ```
   - Wrap with same providers as `test-utils` (`StytchProvider`, `UserPromptProvider`, `StateUiProvider`) — mirror `AllProviders` minus inner `MemoryRouter` (router is external).
   - Mock `/api/nav_config` to return one expanded Admin group:
     ```ts
     [{ label: "Admin", items: [
       { label: "Agent Timesheets", path: "/admin/agent_timesheets", enabled: true },
       { label: "Scheduled Actions", path: "/admin/scheduled_actions", enabled: true },
     ]}]
     ```
   - Mock timesheets + candidates APIs as in step 2
   - `render(<RouterProvider router={router} />)`
   - Expand Admin group if collapsed (`await userEvent.click(screen.getByText("Admin"))`)
   - `await userEvent.click(screen.getByRole("link", { name: "Scheduled Actions" }))`
   - `await waitFor(() => expect(router.state.location.pathname).toBe("/admin/scheduled_actions"))`
   - `expect(screen.getByText("Scheduled Actions Page")).toBeInTheDocument()`
   - `expect(router.state.location.pathname).not.toContain("agent_timesheets")`

4. Run from repo root:
   ```bash
   npm run test -- tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx
   ```

⚠️ **Decision:** Nav-escape test uses `createMemoryRouter` (first use in this repo's frontend tests) because `MemoryRouter` alone cannot assert post-click pathname without a location probe; minimal two-route tree under `NavigationShell` is sufficient for AC1 without pulling the full `routes.tsx` graph.

## Self-Assessment

**Scope:** `Single-Component` — one shared hook dependency fix plus Agent Timesheets page wiring; frontend-only, two production files.

**Conf:** `high` — AST-662 established the same root cause and fix pattern on Execution History; Agent Timesheets differs only by missing memoization and inheriting the unstable `applyFilter` dependency.

**Risk:** `Medium` — the shared hook is used on three admin screens; stabilizing `applyFilter` deps is low-risk (depends on stable `setValue` callbacks), but incorrect changes to nav-sync logic could regress AST-634/662 filter behavior on Execution History or Scheduled Actions.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Hook-level fix removes need for per-page workarounds; Timesheets memoization matches Execution History pattern. |
| §2.1 config | No config changes; candidate list from existing `/api/candidates`. |
| §2.4 batch | N/A — UI-only. |
| §2.6 state machine | N/A. |
| §3.3 imports | Changes stay in `src/ui/frontend/`; no cross-layer violations. |
| §3.5 naming | No new modules; existing hook/page names preserved. |
| §3.6 spike output | N/A — no investigation artifacts. |

No conflicts flagged. Plan is implementable as written.

## QA manifest (Betty)

When picking tests in **qa-child**, cover at minimum the Stage 3 tests above plus existing AST-634 Timesheets filter tests. Manual UAT on staging:

1. Agent Timesheets active → click Scheduled Actions and Execution History → destination renders, no snap-back.
2. Agent Timesheets active → click one non-admin nav item (e.g. Jobs Recommended) → same no-revert behavior.
3. Navigate away and back → empty URL defaults candidate from nav; manual pin persists; **All** shows cross-candidate rows.
4. Direct candidate dropdown switch c1→c2 without **All** intermediate step.
5. No new console errors during nav-away.

## Execution contract

- Execute stages 1→2 in order during **build-child**; one commit per stage on epic worktree; publish each to `origin/sub/AST-705/AST-709-agent-timesheets-nav-and-candidate-filter`.
- Stage 3 tests are Betty-owned per test-tree ban unless Susan directs engineer to land them in build.
- Do not edit `tests/` during plan-child or build stages 1–2 (Betty owns test-tree).
- Blocking ambiguity → comment on **AST-705** with 🛑 template from **plan-child**.

## Review (build)

**Branch:** `origin/sub/AST-705/AST-709-agent-timesheets-nav-and-candidate-filter`  
**Tip:** `13aa5e4`  
**Built:** Stage 1 — `useAdminCandidateFilter`: `applyFilter` depends on `urlSetValue` not `urlBacked` object. Stage 2 — `AdminAgentTimesheets`: memoized `urlBacked` (AST-662 parity). Stage 3 component tests deferred to Betty per build-child test-tree ban.

**Betty manifest (Code Complete):** see **QA manifest (Betty)** above.

---

## Radia review (2026-06-16)

**Diff:** `origin/dev...origin/sub/AST-705/AST-709-agent-timesheets-nav-and-candidate-filter` @ `b512ac1`  
**Verdict:** Clean — no fix-now items.

### What's solid

| Stage | Check |
|-------|-------|
| 1 | `useAdminCandidateFilter`: `applyFilter` depends on `urlSetValue` (`urlBacked?.setValue`) instead of whole `urlBacked` object — stops nav-sync effect from re-firing on every parent re-render |
| 2 | `AdminAgentTimesheets`: memoized `urlBacked` matches `AdminPerformanceMonitor.tsx` AST-662 pattern |
| 3 | Hook test `inline urlBacked identity churn does not spam setValue from nav sync`; page tests for c1→c2 refetch and nav click to Scheduled Actions with pathname assertion |

**Plan fidelity:** Diff footprint matches Self-Assessment (`Single-Component`, two production files + Betty manifest tests). Out-of-scope items untouched (NavigationShell, nav config, timesheet API, backend).

**Rubric (§5a):** UI-only changes; imports at module top; no cross-layer violations; no new logging, silent catches, or hardcoded candidate state strings.

### Advisory

- Nav-escape test uses `renderWithProviders` + nested `Routes` under `NavigationShell` instead of plan’s `createMemoryRouter`/`RouterProvider` stack — simpler, still exercises sidebar `NavLink` navigation and AC1; acceptable deviation.
- Manual UAT item 2 (non-admin nav item, e.g. Jobs Recommended) remains staging-only per plan QA manifest — not required in component tests.

### Recommended actions

None — **resolve-child** may proceed.

## Resolution

**Date:** 2026-06-16 · **Review:** Radia @ `d19a6a0` · **Product tip:** `13aa5e4` · **Tests tip:** `b512ac1`

| Item | Outcome |
|------|---------|
| fix-now | None — ship as reviewed. |
| discuss | None. |
| advisory — nav-escape test uses `renderWithProviders` + nested `Routes` | Accepted; still covers sidebar `NavLink` + pathname AC1. |
| advisory — non-admin nav escape (Jobs Recommended, etc.) | Manual UAT per plan QA manifest; no component test required. |

**Tests:** Betty manifest green (Katherine `test-child`); Radia diff clean @ `d19a6a0`.
