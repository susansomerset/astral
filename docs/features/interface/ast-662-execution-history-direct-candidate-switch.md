<!-- linear-archive: AST-662 archived 2026-06-23 -->

## Linear archive (AST-662)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-662/execution-history-direct-candidate-switch-execution-history-candidate  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-656 — Execution History Candidate Select Issue  
**Blocked by / blocks / related:** parent: AST-656

### Description

## What this implements

Fix the Execution History (`/admin/performance`) on-page **Candidate** dropdown so selecting a different candidate immediately applies the filter without requiring an intermediate **All** selection. The dropdown display, ledger fetch, table rows, total-cost summary, and URL `candidate_id` param must stay in sync on every direct candidate-to-candidate change. Add or extend component-level regression coverage for direct A→B selection.

## Acceptance criteria

1. With two or more candidates in the system and Execution History showing rows for the nav-default candidate, selecting a different candidate in the on-page **Candidate** dropdown updates the visible rows and total cost to that candidate's ledger entries (within current date/task/status filters) without first selecting **All**.
2. Selecting **All** shows cross-candidate rows within the other filters; then selecting a specific candidate filters correctly (existing workaround path remains valid).
3. The dropdown displayed value always matches the active filter after each change (no silent snap-back to the previous candidate).
4. The browser URL's `candidate_id` param matches the active selection (**All** → param absent; specific candidate → param set to that id).
5. Task, Status, date, and Skip Checks filters remain unchanged when only Candidate changes.
6. Automated tests cover direct switch from one candidate id to another on Execution History (in addition to existing AST-634 cases for global candidate list and URL-seeded fetch).

## Boundaries

* Execution History only — do not change Scheduled Actions or Agent Timesheets unless a shared fix is strictly required and verified not to regress those screens.
* Does not change left-nav candidate selection, nav visibility rules, or `/api/nav_config`.
* Does not change dispatch ledger API semantics, backend filtering, or debug logging (UI-only bug).
* Does not redesign the filter bar or table layout.

## Notes for planning

* AST-634 introduced the shared admin candidate filter — inspect how nav sync vs manual pin interacts with state updates on Execution History.
* Likely files: React admin performance/execution history components and existing AST-634 test coverage.
* plan-child §3.5 — new components go in `src/components/` flat.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-656-execution-history-candidate-select`, child `sub/AST-656/<child-id>-execution-history-candidate-switch`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-15T02:15:21.355Z
**Review (Radia)** — `origin/dev...origin/sub/AST-656/AST-662-execution-history-candidate-switch` @ `8e9998d8`

Doc: `docs/features/interface/ast-662-execution-history-direct-candidate-switch.md` § Review (Radia)

### fix-now
None.

### discuss
None.

### advisory
- `useAdminCandidateFilter.ts` — `manualPinRef` is never cleared; fine in practice because `syncWithNav === false` after manual pick already disables nav-sync for the session. Ref only covers the stale-`syncWithNav` render window.
- `AdminAgentTimesheets.tsx` (unchanged) — still uses inline `urlBacked`; if UAT sees the same direct-switch bug there, apply the same `useMemo` one-liner from Execution History.

### What's solid
- Stages 1–2 match plan; Betty manifest covers AC6 (hook + page direct c1→c2 tests).
- Closes AST-634 Radia **discuss** items: memoized `urlBacked` + `manualPinRef` nav-sync guard.
- UI-only; boundaries respected (no backend / other admin tabs).

**Verdict:** Clean — `resolve-child` / UAT.

#### betty — 2026-06-15T02:12:28.848Z
## QA test manifest (AST-662)

**Publish ref:** `origin/sub/AST-656/AST-662-execution-history-candidate-switch` @ `bfc6d846`  
**Tests SHA:** `8a5bfa67` (`merge-tests(AST-662): origin/tests 8a5bfa67`)  
**Bible shasum (`origin/sub/...`):** `docs/ASTRAL_TEST_BIBLE.md` → see §7.13zzna

### 1. Existing coverage (bible-backed — run for regression)

- **§7.13zzn (AST-634):** full `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx`; `test_AdminPerformanceMonitor.test.tsx` **AST-634** describe (global candidate list + URL-seeded fetch); sibling admin page **AST-634** describes if touching shared hook behavior.

### 2. Broken / obsolete tests

- None — AST-634 cases remain valid; no assertion rewrites required.

### 3. Gaps (new this pass)

| # | Path | What it proves |
|---|------|----------------|
| 1 | `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` — `direct urlBacked switch from c1 to c2 does not revert to nav default` | **`manualPinRef`** blocks nav-sync effect from overwriting direct A→B selection after URL update |
| 2 | `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — `direct candidate switch c1 to c2 refetches ledger without All intermediate step` | Routed page: dropdown c1→c2 refetches ledger with `candidate_id=c2`, table shows `task_c2` only, select value stays `c2` (**§6c** routed page + filter UX) |

### Narrowed run (test-child)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "AST-634|direct urlBacked|direct candidate switch"
```

Full page file recommended before **User Testing** (date blur cases + AST-532 chain UI).

— Betty

#### chuckles — 2026-06-15T02:08:12.714Z
## Validate Plan — APPROVED

**Verdict:** APPROVED → Plan Approved

| # | Severity | Finding |
|---|----------|---------|
| — | — | Plan matches AST-656 definition; hook ref guard + memoized `urlBacked` addresses the nav-sync race Radia flagged on AST-634; tests cover direct A→B. Boundaries respected (Execution History primary; shared hook fix is minimal and safe). |

— Chuckles

#### katherine — 2026-06-15T02:08:00.113Z
Plan: [ast-662-execution-history-direct-candidate-switch.md](https://github.com/susansomerset/astral/blob/sub/AST-656/AST-662-execution-history-candidate-switch/docs/features/interface/ast-662-execution-history-direct-candidate-switch.md) @ `a3404dd7`

**Scope:** `Single-Component` — shared hook guard + Execution History `urlBacked` memo + two frontend test files; no backend or sibling admin tabs.

**Conf:** `high` — AST-634 pattern is in place; Radia's deferred `urlBacked`/nav-sync race matches Susan's "All first" workaround; fix is a synchronous manual-pin ref plus stable `urlBacked` memo.

**Risk:** `Medium` — hook is shared across three admin screens; ref guard only fires after explicit dropdown change and must not break first-visit nav-default on Scheduled Actions.

---

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

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-656/AST-662-execution-history-candidate-switch` (tip `bfc6d846`)  
**Reviewed:** 2026-06-14

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–2 match plan; Stage 3 tests landed via Betty manifest (`test_useAdminCandidateFilter`, `test_AdminPerformanceMonitor`). |
| AST-634 follow-through | Closes Radia **discuss** on `urlBacked` identity (`useMemo` on Execution History) and nav-sync race (`manualPinRef` before `setSyncWithNav`). |
| AC coverage | Hook test locks direct c1→c2 without snap-back; page test asserts ledger refetch, row swap, and dropdown value. |
| Boundaries | Execution History page + shared hook only; no backend, nav config, or other admin tabs touched. |
| §3.3 layers | Frontend-only; imports at module top (`useRef`, existing `useMemo`). |
| §2.1 config | No hardcoded candidate state strings. |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| advisory | `useAdminCandidateFilter.ts` `manualPinRef` | Ref is never cleared after manual pick; harmless because `syncWithNav === false` already disables nav-sync for the rest of the session. Ref only covers the stale-`syncWithNav` render window. |
| advisory | `AdminAgentTimesheets.tsx` (unchanged) | Still passes inline `urlBacked`; plan defers memoization there. If UAT reports the same direct-switch bug on Timesheets, apply the same one-liner. |

### Recommended actions

| Priority | Action |
|----------|--------|
| UAT | Smoke direct candidate-to-candidate switch on Execution History in staging; confirm All → specific path still works. |
| follow-up | Only if Timesheets shows same defect: memoize `urlBacked` on that page (no hook change needed). |

**Verdict:** Clean — approve for `resolve-child` / UAT. No fix-now or discuss blockers.

## Resolution

**Date:** 2026-06-15 · **Review:** Radia @ `8e9998d8` · **Product tip:** `24495c35`

| Item | Outcome |
|------|---------|
| fix-now | None — ship as reviewed. |
| discuss | None. |
| advisory — `manualPinRef` never cleared | Accepted; `syncWithNav === false` after manual pick covers session; ref only guards stale render window. |
| advisory — `AdminAgentTimesheets` inline `urlBacked` | Deferred per plan boundary; follow-up only if UAT reports same defect on Timesheets. |

**Tests:** Betty manifest green (Katherine `test-child`); Radia diff clean @ `8e9998d8`.
