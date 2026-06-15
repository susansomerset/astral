# Execution History direct candidate switch (Execution History Candidate Select Issue)

**Linear:** [AST-662](https://linear.app/astralcareermatch/issue/AST-662/execution-history-direct-candidate-switch-execution-history-candidate)  
**Parent:** [AST-656](https://linear.app/astralcareermatch/issue/AST-656/execution-history-candidate-select-issue)  
**Publish ref:** `sub/AST-656/AST-662-execution-history-candidate-switch`

Susan cannot switch the Execution History **Candidate** dropdown directly from one specific candidate to another — the click is accepted but the ledger does not refetch until she selects **All** first. This ticket fixes that UI-only defect on `/admin/performance` so dropdown display, URL `candidate_id`, ledger fetch, table rows, and total-cost summary stay in sync on every direct candidate-to-candidate change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts` | Synchronous manual-pin guard so nav-sync effect cannot overwrite a user selection during the URL update render | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Memoize `urlBacked` object passed to hook (stabilize `applyFilter` identity) | ui |
| `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` | Regression: direct A→B switch with `urlBacked` does not revert to nav default | ui (QA) |
| `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` | Regression: direct c1→c2 dropdown change refetches ledger and updates displayed rows | ui (QA) |

**Out of scope:** `AdminScheduledActions.tsx`, `AdminAgentTimesheets.tsx`, backend APIs, nav config, filter bar layout.

## Stage 1: Fix nav-sync race in `useAdminCandidateFilter`

**Done when:** Manual candidate selection via `setCandidateFilter` always wins over the nav-sync `useEffect`, even when `setSearchParams` triggers an intermediate render before `syncWithNav` state flushes. Hook tests pass including new direct A→B case.

1. In `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts`, add a ref immediately after the `syncWithNav` state declaration:
   ```ts
   const manualPinRef = useRef(false)
   ```
2. In `setCandidateFilter`, set the ref **synchronously before** any state or URL writes:
   ```ts
   const setCandidateFilter = useCallback(
     (next: AdminCandidateFilterValue) => {
       manualPinRef.current = true
       setSyncWithNav(false)
       applyFilter(next)
     },
     [applyFilter],
   )
   ```
3. In the nav-sync `useEffect` (~lines 53–56), guard with the ref so a URL-triggered re-render cannot re-apply nav default while `syncWithNav` is still stale `true`:
   ```ts
   useEffect(() => {
     if (!syncWithNav || manualPinRef.current) return
     applyFilter(navDefaultCandidateFilter(selectedId))
   }, [selectedId, syncWithNav, applyFilter])
   ```
4. Do **not** change hook return shape, `navDefaultCandidateFilter`, `urlPresentDisablesSync` init logic, or `AdminCandidateFilterControl`.

⚠️ **Decision:** Shared-hook fix is required — the race is in `setSyncWithNav` (hook state) vs `setSearchParams` (parent state) batching. Execution History is the reported screen, but the guard is safe for Scheduled Actions (local state only; ref set on manual pick) and Agent Timesheets (same URL-backed pattern). Radia deferred this as optional hardening on AST-634; AST-662 confirms it is a user-visible defect.

## Stage 2: Stabilize URL-backed hook input on Execution History

**Done when:** `useAdminCandidateFilter` on Execution History receives a stable `urlBacked` reference across renders when `urlCandidate` and `setCandidateParam` are unchanged.

1. In `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, add `useMemo` to the import from `react` (already present — verify `useMemo` is in the import list).
2. After `const urlCandidate = candidateIdFromParams(searchParams)` and `setCandidateParam` definition (~lines 117–121), replace the inline `urlBacked` object with:
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
3. Leave `initialCandidateDefaultApplied` effect, `filters` `useMemo`, `loadData`, and all other filter controls unchanged.

⚠️ **Decision:** Memoize only on Execution History per ticket boundary. Agent Timesheets may get the same one-liner in a follow-up if UAT reports the same defect there; do not touch Timesheets in this ticket.

## Stage 3: Component regression tests (engineer-owned per ticket AC6)

**Done when:** Vitest covers direct candidate A→B on Execution History and hook-level direct switch; existing AST-634 tests still pass.

1. In `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx`, add test `direct urlBacked switch from c1 to c2 does not revert to nav default`:
   - `localStorage.setItem("astral_selected_candidate", "c1")`
   - `let urlValue = "c1"`; `setValue` mock updates `urlValue`
   - Render hook with `urlBacked: { value: urlValue, setValue }` and `urlPresentDisablesSync: true`
   - `await waitFor(() => expect(result.current.candidateFilter).toBe("c1"))`
   - `act(() => result.current.setCandidateFilter("c2"))`
   - `expect(setValue).toHaveBeenCalledWith("c2")`
   - `rerender()` with `urlValue = "c2"` (simulate parent URL update)
   - `expect(result.current.candidateFilter).toBe("c2")`
   - `expect(result.current.syncWithNav).toBe(false)`
   - After `rerender()`, `candidateFilter` must remain `"c2"` (not snap back to `"c1"`)

2. In `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`, inside `describe("AST-634 admin candidate filter")`, add test `direct candidate switch c1 to c2 refetches ledger without All intermediate step`:
   - Define ledger rows:
     ```ts
     const rowC1 = { ...ledgerRow, batch_id: "b-c1", candidate_id: "c1", task_key: "task_c1" }
     const rowC2 = { ...ledgerRow, batch_id: "b-c2", candidate_id: "c2", task_key: "task_c2" }
     ```
   - `const calls: string[] = []`
   - `installBaseApiMocks` handler for `/api/admin/dispatch_ledger?`: push `url` to `calls`; if `url.includes("candidate_id=c2")` return `[rowC2]`; if `url.includes("candidate_id=c1")` return `[rowC1]`; else return `[rowC1, rowC2]`
   - `/api/candidates` returns `adminCandidates` (c1 + c2)
   - `renderPerformanceMonitor("/admin/performance?candidate_id=c1")` with nav context default c1 (existing `withCandidateQuery` helper seeds `candidate_id=c1`)
   - `await waitFor(() => expect(within(screen.getByRole("table")).getByText("task_c1")).toBeInTheDocument())`
   - `const candidateSelect = screen.getByLabelText("Candidate", { selector: "select" })`
   - `await userEvent.selectOptions(candidateSelect, "c2")`
   - `await waitFor(() => expect(calls.some(u => u.includes("candidate_id=c2"))).toBe(true))`
   - `await waitFor(() => expect(within(screen.getByRole("table")).getByText("task_c2")).toBeInTheDocument())`
   - `expect(within(screen.getByRole("table")).queryByText("task_c1")).not.toBeInTheDocument()`
   - `expect((candidateSelect as HTMLSelectElement).value).toBe("c2")`

3. Run from repo root:
   ```bash
   npm run test -- tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx
   ```
   All tests in those files must pass before `code()` commit.

## Self-Assessment

**Scope:** `Single-Component` — touches one shared hook plus Execution History page wiring and two frontend test files; no backend or other admin tabs.

**Conf:** `high` — AST-634 already established the filter pattern; Radia identified the `urlBacked` identity / nav-sync race as the likely cause; fix is a small ref guard and memoization matching deferred review notes.

**Risk:** `Medium` — the shared hook is used on three admin screens, but the manual-pin ref only blocks nav sync after explicit user action and should not change first-visit nav-default behavior; wrong guard logic could break nav sync on Scheduled Actions.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing hook and control; no duplicate filter logic. |
| §2.1 Config | No config changes. |
| §3.3 Imports | `useMemo` already used on page; hook adds `useRef` only. |
| §3.5 Naming | No new components; existing names preserved. |
| §3.6 Spike output | N/A — no investigation artifacts. |

No conflicts flagged. Plan is implementable as written.

## Review (build)

**Branch:** `origin/sub/AST-656/AST-662-execution-history-candidate-switch`  
**Tip:** `24495c35`  
**Built:** Stage 1 — `manualPinRef` guard in `useAdminCandidateFilter`. Stage 2 — memoized `urlBacked` on `AdminPerformanceMonitor`. Stage 3 component tests deferred to Betty per build-child test-tree ban (AC6 coverage in qa-child manifest).
