# Agent Timesheets nav escape and candidate filter stability (Nav Menu stops working while on agent timesheets)

**Linear:** [AST-709](https://linear.app/astralcareermatch/issue/AST-709/agent-timesheets-nav-escape-and-candidate-filter-stability-nav-menu)  
**Parent:** [AST-705](https://linear.app/astralcareermatch/issue/AST-705/nav-menu-stops-working-while-on-agent-timesheets)  
**Publish ref:** `sub/AST-705/AST-709-agent-timesheets-nav-and-candidate-filter`

Susan is trapped on `/admin/agent_timesheets`: sidebar clicks briefly change the address bar, then snap back. AST-634 added URL-backed candidate sync here; AST-662 fixed the shared hook race and memoized `urlBacked` on Execution History only. Agent Timesheets still passes an inline `urlBacked` object, so `applyFilter` identity changes every render, the nav-sync `useEffect` re-fires, and `setSearchParams(..., { replace: true })` races sidebar `NavLink` navigation. This ticket restores reliable nav escape and completes Timesheets parity for direct candidate-to-candidate switching and AST-634 filter semantics.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts` | Skip redundant `applyFilter` when value unchanged; nav-sync effect no-ops when filter already matches nav default | ui |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Memoize `urlBacked`; guard `setCandidateParam` against redundant URL writes | ui |
| `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` | Regression: nav-sync does not call `setValue` when filter already matches nav default | ui (QA) |
| `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` | Regression: nav-away to admin + non-admin routes; direct c1→c2 switch; return-visit filter behavior | ui (QA) |

**Out of scope:** timesheet API, nav config, sidebar layout, `AdminScheduledActions.tsx`, `AdminPerformanceMonitor.tsx` (unless hook hardening requires no page edits — hook-only change must stay safe for both).

## Stage 1: Harden shared hook against redundant URL writes

**Done when:** `useAdminCandidateFilter` does not call `urlBacked.setValue` or `setLocalFilter` when the target value equals the current filter; nav-sync effect does not re-apply when `candidateFilter` already equals `navDefaultCandidateFilter(selectedId)`. Existing hook tests pass; Scheduled Actions and Execution History behavior unchanged.

1. In `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts`, update `applyFilter` (~lines 38–44) to return early when the write would be a no-op:
   ```ts
   const applyFilter = useCallback(
     (next: AdminCandidateFilterValue) => {
       if (urlBacked) {
         if (urlBacked.value === next) return
         urlBacked.setValue(next)
       } else {
         if (localFilter === next) return
         setLocalFilter(next)
       }
     },
     [urlBacked, localFilter],
   )
   ```
   Add `localFilter` to the `useCallback` dependency array (local-only path).

2. In the nav-sync `useEffect` (~lines 55–58), compute the target once and skip when already applied:
   ```ts
   useEffect(() => {
     if (!syncWithNav || manualPinRef.current) return
     const next = navDefaultCandidateFilter(selectedId)
     if (candidateFilter === next) return
     applyFilter(next)
   }, [selectedId, syncWithNav, applyFilter, candidateFilter])
   ```
   Add `candidateFilter` to the dependency array.

3. Do **not** change hook return shape, `manualPinRef` / `setCandidateFilter` logic, `urlPresentDisablesSync` init, or `navDefaultCandidateFilter`.

⚠️ **Decision:** Shared-hook hardening is the minimal safe fix for all three admin tabs. Scheduled Actions uses local state only — early return prevents redundant `setState`. Execution History already memoizes `urlBacked`; this removes duplicate `setSearchParams` when nav default already matches URL. Agent Timesheets benefits most because inline `urlBacked` previously retriggered nav-sync every render.

## Stage 2: Stabilize URL-backed wiring on Agent Timesheets

**Done when:** `AdminAgentTimesheets` passes a stable `urlBacked` reference to the hook (matching `AdminPerformanceMonitor.tsx` post-AST-662) and `setCandidateParam` does not write `candidate_id` when it is already the requested value.

1. In `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx`, verify `useMemo` is imported from `react` (already used for `filters`).

2. After `const urlCandidate = candidateIdFromParams(searchParams)` and the existing `setCandidateParam` `useCallback` (~lines 107–120), replace the inline `urlBacked` passed to `useAdminCandidateFilter` with:
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

3. In `setCandidateParam` (~lines 107–114), add a redundant-write guard before `setSearchParams`:
   ```ts
   const setCandidateParam = useCallback((next: AdminCandidateFilterValue) => {
     const current = searchParams.get("candidate_id") || ""
     if (current === next) return
     setSearchParams(prev => {
       const nextParams = new URLSearchParams(prev)
       if (next) nextParams.set("candidate_id", next)
       else nextParams.delete("candidate_id")
       return nextParams
     }, { replace: true })
   }, [searchParams, setSearchParams])
   ```
   Add `searchParams` to the dependency array.

4. Leave `initialCandidateDefaultApplied` effect, `filters` `useMemo`, `loadData`, date/batch filters, totals, export, and `ListPage` unchanged.

⚠️ **Decision:** Memoize only on Agent Timesheets per ticket boundary — Execution History already has this from AST-662. Combined with Stage 1, nav-sync stops spamming `setSearchParams` during sidebar navigation away from Timesheets.

## Stage 3: Component regression tests (engineer-owned per ticket notes)

**Done when:** Vitest covers nav-away (admin + non-admin), direct candidate A→B on Timesheets, and return-visit filter semantics; existing AST-634 Timesheets tests still pass.

1. In `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx`, add test `nav-sync does not call setValue when filter already matches nav default`:
   - `localStorage.setItem("astral_selected_candidate", "c1")`
   - `let urlValue = "c1"`; `const setValue = vi.fn()`
   - Render hook with `urlBacked: { value: urlValue, setValue }`, `urlPresentDisablesSync: true`
   - `await waitFor(() => expect(result.current.candidateFilter).toBe("c1"))`
   - `setValue.mockClear()`
   - `rerender()` twice (simulate parent re-renders with stable url value)
   - `expect(setValue).not.toHaveBeenCalled()`
   - `expect(result.current.candidateFilter).toBe("c1")`

2. In `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx`, add imports: `Link`, `Route`, `Routes` from `react-router-dom`.

3. Add helper `adminCandidates` fixture (same shape as Performance Monitor tests):
   ```ts
   const adminCandidates = [
     { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { first: "Ada" } },
     { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: { first: "Betty" } },
   ]
   ```

4. Add helper `renderTimesheetsNavHarness(initialPath: string)` that renders:
   ```tsx
   <>
     <nav>
       <Link to="/admin/performance_monitor">Execution History</Link>
       <Link to="/jobs/recommended">Jobs</Link>
     </nav>
     <Routes>
       <Route path="/admin/agent_timesheets" element={<AgentTimesheets />} />
       <Route path="/admin/performance_monitor" element={<div data-testid="dest-perf">Execution History</div>} />
       <Route path="/jobs/recommended" element={<div data-testid="dest-jobs">Recommended Jobs</div>} />
     </Routes>
   </>
   ```
   via `renderWithProviders(..., { router: { initialEntries: [initialPath] } })`.

5. Inside `describe("AST-634 admin candidate filter")`, add test `nav away to admin route does not snap back to agent timesheets`:
   - `localStorage.setItem("astral_selected_candidate", "c1")`
   - `installBaseApiMocks` with `/api/candidates` → `adminCandidates`; `/api/admin/timesheets` → `[row]`
   - `renderTimesheetsNavHarness("/admin/agent_timesheets?candidate_id=c1")`
   - `await waitFor(() => expect(screen.getByText("Agent Timesheets")).toBeInTheDocument())`
   - `await userEvent.click(screen.getByRole("link", { name: "Execution History" }))`
   - `await waitFor(() => expect(screen.getByTestId("dest-perf")).toBeInTheDocument())`
   - `expect(screen.queryByText("Agent Timesheets")).not.toBeInTheDocument()`

6. Add test `nav away to non-admin route does not snap back to agent timesheets`:
   - Same mocks and harness as step 5
   - `renderTimesheetsNavHarness("/admin/agent_timesheets?candidate_id=c1")`
   - `await waitFor(() => expect(screen.getByText("Agent Timesheets")).toBeInTheDocument())`
   - `await userEvent.click(screen.getByRole("link", { name: "Jobs" }))`
   - `await waitFor(() => expect(screen.getByTestId("dest-jobs")).toBeInTheDocument())`
   - `expect(screen.queryByText("Agent Timesheets")).not.toBeInTheDocument()`

7. Add test `direct candidate switch c1 to c2 refetches timesheets without All intermediate step`:
   - `const rowC1 = { ...row, agent_req_id: "req-c1", candidate_id: "c1" }`
   - `const rowC2 = { ...row, agent_req_id: "req-c2", candidate_id: "c2" }`
   - `const calls: string[] = []`
   - `installBaseApiMocks` handler for `/api/admin/timesheets?`: push `url` to `calls`; if `url.includes("candidate_id=c2")` return `[rowC2]`; if `url.includes("candidate_id=c1")` return `[rowC1]`; else return `[rowC1, rowC2]`
   - `/api/candidates` → `adminCandidates`
   - `renderWithProviders(<AgentTimesheets />, { router: { initialEntries: ["/admin/agent_timesheets?candidate_id=c1"] } })`
   - `await waitFor(() => expect(screen.getByText("Agent Timesheets")).toBeInTheDocument())`
   - `const candidateSelect = screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement`
   - `await userEvent.selectOptions(candidateSelect, "c2")`
   - `await waitFor(() => expect(calls.some(u => u.includes("candidate_id=c2"))).toBe(true))`
   - `expect(candidateSelect.value).toBe("c2")`

8. Add test `return visit preserves manual All selection`:
   - `installBaseApiMocks` with timesheets + `adminCandidates`
   - `renderTimesheetsNavHarness("/admin/agent_timesheets?candidate_id=c1")`
   - `await waitFor(() => expect(screen.getByText("Agent Timesheets")).toBeInTheDocument())`
   - Select **All** in candidate dropdown: `await userEvent.selectOptions(screen.getByLabelText("Candidate", { selector: "select" }), "")`
   - Navigate away: `await userEvent.click(screen.getByRole("link", { name: "Execution History" }))`
   - `await waitFor(() => expect(screen.getByTestId("dest-perf")).toBeInTheDocument())`
   - Return: `await userEvent.click(screen.getByRole("link", { name: "Agent Timesheets" }))` — add a `Link to="/admin/agent_timesheets"` in the nav harness for this step only, or re-render harness at `/admin/agent_timesheets` without `candidate_id` and assert dropdown shows **All** (empty value) after manual pin cleared URL param on prior visit.
   - Simpler path: after selecting All, assert `candidate_id` removed from fetch URL (`calls` does not include `candidate_id=`); skip full round-trip if harness link overhead is high — **minimum AC:** manual All clears param and subsequent fetch omits `candidate_id`.

   Implement as:
   - Extend harness nav with `<Link to="/admin/agent_timesheets">Agent Timesheets</Link>`
   - After All selection + nav away + return via that link, `await waitFor` candidate select value `""` and timesheets fetch URL without `candidate_id=`.

9. Run from repo root:
   ```bash
   npm run test -- tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx
   ```
   All tests in those files must pass before `code()` commit.

## Self-Assessment

**Scope:** `Single-Component` — one shared hook plus Agent Timesheets page wiring and two frontend test files; no backend, nav config, or sibling admin page edits.

**Conf:** `high` — AST-662 and Radia review already identified inline `urlBacked` and nav-sync `setSearchParams` races as the likely cause; fix mirrors proven Execution History pattern plus redundant-write guards.

**Risk:** `Medium` — shared hook is used on three admin screens; redundant-write guards must not block legitimate nav-default updates when `selectedId` changes; wrong guard logic could freeze filter on Scheduled Actions when nav candidate changes while `syncWithNav` is true.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing hook and control; no duplicate filter logic. |
| §2.1 Config | No config changes. |
| §3.3 Imports | `useMemo` already on Timesheets page; hook adds `candidateFilter`/`localFilter` to deps only. |
| §3.5 Naming | No new components; existing names preserved. |
| §3.6 Spike output | N/A — no investigation artifacts. |

No conflicts flagged. Plan is implementable as written.

## Execution contract (for the developer agent)

The plan is binding. Execute stages in order. **Stop** on ambiguity — comment on **AST-709** with 🛑 template from plan-child §6. Do not touch `AdminPerformanceMonitor.tsx` or `AdminScheduledActions.tsx` unless a blocking regression appears in Stage 3 tests (then comment before editing).
