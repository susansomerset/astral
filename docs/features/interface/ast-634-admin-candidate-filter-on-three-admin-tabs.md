<!-- linear-archive: AST-634 archived 2026-06-23 -->

## Linear archive (AST-634)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-628 — Remove "Selected Candidate" filter on admin tabs  
**Blocked by / blocks / related:** parent: AST-628

### Description

## What this implements

Add a consistent **Candidate** dropdown filter (**All** + full global candidate list) on **Scheduled Actions**, **Execution History**, and **Agent Timesheets**. Remove silent left-nav-only filtering on Scheduled Actions; replace free-text candidate input on Agent Timesheets; fix Execution History to use the full candidate list (not only candidates in the loaded result set). Default each screen's filter to the left-nav selected candidate (or **All** when none selected). Implement nav-sync: while the on-page filter is still at default, left-nav changes update the dropdown; after manual selection, the on-page filter stays until changed again.

## Acceptance criteria

1. On **Scheduled Actions**, with left-nav candidate **A** selected and no manual filter change yet, the **Candidate** filter shows **A** and the table lists only dispatch tasks for **A**; choosing **All** shows tasks for every candidate; choosing **B** shows only **B**'s tasks. No hidden nav-only filtering remains.
2. On **Execution History**, with left-nav candidate **A** selected on first visit (no `candidate_id` in URL), the **Candidate** filter defaults to **A** and the ledger list is scoped to **A**; **All** shows all candidates (within other active filters); the dropdown lists every candidate from the global list, including candidates with zero rows in the current date window.
3. On **Agent Timesheets**, with left-nav candidate **A** selected, the **Candidate** dropdown defaults to **A**; **All** shows all candidates within date/other filters; totals bars and **Export CSV** match the active candidate filter.
4. With no candidate selected in the left nav, all three screens default the **Candidate** filter to **All**.
5. All three screens use the same **Candidate** / **All** dropdown pattern and readable candidate labels.
6. **Nav sync:** With the on-page filter still at default on a screen, switching left-nav from **A** to **B** updates that screen's **Candidate** filter to **B** without a page reload. After Susan manually sets the on-page filter to **All** or a specific candidate other than the current default, subsequent left-nav changes do **not** change the on-page filter until she changes the dropdown.

## Boundaries

* Does **not** change the left-nav candidate selector or other candidate-scoped screens.
* Does **not** add server-side authorization changes or new admin APIs unless a plan discovers an existing endpoint cannot support **All** — prefer client-side filtering and existing list endpoints.
* Does **not** redesign table columns, phase grouping, run/stop behavior, or non-candidate filters on these three screens.

## Notes for planning

* Primary files: `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, `AdminPerformanceMonitor.tsx`, `AdminAgentTimesheets.tsx`; `useCandidate` from `CandidateContext`.
* Consider a shared hook or small component for candidate dropdown + nav-sync default tracking if it reduces duplication.
* plan-child: Vitest coverage per screen or shared filter hook.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-628-remove-selected-candidate-filter-on-admin-tabs`, child `sub/AST-628/<child-id>-<slug>`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-14T19:11:36.974Z
**Review** — `origin/dev...origin/sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs` (product tip `87911345`; doc `7eb0b981`)

Plan doc: `docs/features/interface/ast-634-admin-candidate-filter-on-three-admin-tabs.md` (Review section)

### Solid
- Stages 1–4 match plan: shared `candidateLabel` / `useAdminCandidateFilter` / `AdminCandidateFilterControl`; Scheduled Actions explicit client filter (silent nav filter removed); Execution History + Timesheets URL-backed with one-time nav default effect.
- Betty manifest covers default-from-nav, All, manual pin, global candidate list (Execution History), export `candidate_id` (Timesheets).
- §3.3 clean — frontend-only; label logic aligns with `NavigationShell.tsx`.

### discuss
- **`useAdminCandidateFilter.ts`** — `applyFilter` depends on inline `urlBacked` object identity from callers; nav-sync `useEffect` may re-run every parent render while `syncWithNav` and repeatedly call `setSearchParams`. Tests seed `candidate_id` on mount (`withCandidateQuery`) to avoid RTL hang. Consider stabilizing deps (`setValue`/`value` as separate args) before UAT on first visit with no `candidate_id` query param.
- **Duplicate URL helpers** in `AdminPerformanceMonitor.tsx` + `AdminAgentTimesheets.tsx` — acceptable for this scope; extract only if a fourth admin screen needs the same pattern.

### advisory
- Execution History `tz` still follows **nav** `selectedId`, not on-page filter (pre-existing).
- `candidateLabel.ts` `candidate_data || {}` — bounded display use, matches nav shell.

**Verdict:** No fix-now blockers — proceed to `resolve-child` / UAT. Optional hardening on hook deps if first-load URL default flickers in staging.

#### betty — 2026-06-14T19:08:14.768Z
**QA test manifest** — `origin/sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs` @ `849595b8` (`merge-tests(AST-634): origin/tests d4652222`)

1. `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` — nav default, manual pin blocks nav sync, URL-backed mode
2. `tests/component/frontend/lib/test_candidateLabel.test.ts` — label formatting + sort order
3. `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-634`** describe: default from nav, **All**, manual **All** blocks nav sync, nav sync before manual change
4. `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — **`AST-634`** describe: global candidate list in dropdown; `candidate_id` in ledger fetch URL
5. `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` — **`AST-634`** describe: Candidate `<select>` + export URL includes `candidate_id`

**Regression guard:** full `test_AdminPerformanceMonitor.test.tsx` (helper seeds `candidate_id=c1` when absent — see bible RTL note).

**Narrowed run:**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx \
  ../../../tests/component/frontend/lib/test_candidateLabel.test.ts \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx \
  -t "AST-634|useAdminCandidateFilter|candidateLabel"
```

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` §7.13zzn — shasum on publish ref: `afda00e35ba70acee48d2cce5912fb71a0ed1c0e`

#### katherine — 2026-06-14T18:23:54.552Z
Plan: [`docs/features/interface/ast-634-admin-candidate-filter-on-three-admin-tabs.md`](https://github.com/susansomerset/astral/blob/sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs/docs/features/interface/ast-634-admin-candidate-filter-on-three-admin-tabs.md)

Four build stages: shared `useAdminCandidateFilter` + label helper + control, then wire Scheduled Actions (remove silent nav filter), Execution History (full candidate list + URL default/sync), Agent Timesheets (dropdown replaces free text). Betty QA manifest covers nav-sync pin, zero-row candidates in dropdown, and export URL parity — no engineer commits under `tests/`.

**Self-assessment**
- **Scope:** Single-Component — three admin pages plus shared hook/control; frontend only.
- **Conf:** high — mirrors existing `NavigationShell` labels and URL filter patterns; AC fully specified on AST-628/634.
- **Risk:** Medium — wrong default/sync would mis-scope admin list views but not dispatch or DB state.

---

# Admin candidate filter on three admin tabs (Remove "Selected Candidate" filter on admin tabs)

**Linear:** [AST-634](https://linear.app/astralcareermatch/issue/AST-634/admin-candidate-filter-on-three-admin-tabs-remove-selected-candidate)  
**Parent:** [AST-628](https://linear.app/astralcareermatch/issue/AST-628/remove-selected-candidate-filter-on-admin-tabs)  
**Publish ref:** `sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs`

Susan needs explicit **Candidate** filters on three admin screens — **All** plus the full global candidate list — defaulting to whoever is selected in the left nav, with nav sync until she manually picks a different on-page value. Today Scheduled Actions silently filters by left-nav selection, Execution History builds candidate options only from loaded ledger rows, and Agent Timesheets uses a free-text candidate field.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/candidateLabel.ts` | New helper: human-readable candidate labels with collision disambiguation (same rules as left nav) | ui |
| `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts` | New hook: default from nav, manual pin, nav-sync effect, sorted candidate options from `useCandidate()` | ui |
| `src/ui/frontend/src/components/AdminCandidateFilterControl.tsx` | New shared `<label>Candidate<select>…</select></label>` for admin filter bars | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Remove silent `selectedId` row filter; add on-page Candidate filter via shared hook | ui |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Full candidate list in dropdown; URL default + nav sync via hook; remove row-derived `candidateOptions` | ui |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Replace free-text Candidate input with shared dropdown; URL default + nav sync | ui |

**QA manifest (Betty — not engineer commits):** extend Vitest in `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`, `test_AdminPerformanceMonitor.test.tsx`, and `test_AdminAgentTimesheets.test.tsx` (or one focused `test_useAdminCandidateFilter.test.tsx` if hook is tested in isolation) for: default-from-nav, All shows cross-candidate rows, manual pin blocks nav sync, Execution History dropdown includes a candidate with zero ledger rows.

## Stage 1: Shared candidate label + admin filter hook + control

**Done when:** `candidateLabel.ts`, `useAdminCandidateFilter.ts`, and `AdminCandidateFilterControl.tsx` exist; hook exports stable API used by all three pages; no page wiring yet.

1. Create `src/ui/frontend/src/lib/candidateLabel.ts` with:
   ```ts
   import type { CandidateInfo } from "../contexts/CandidateContext" // export CandidateInfo from CandidateContext if not already exported
   ```
   - Export `candidateBaseLabel(c: CandidateInfo): string` — same logic as `NavigationShell.tsx` lines 84–86: `[cd.first, cd.last].filter(Boolean).join(" ") || c.astral_candidate_id` where `cd = c.candidate_data || {}`.
   - Export `candidateOptionLabel(c: CandidateInfo, all: CandidateInfo[]): string` — if more than one candidate in `all` shares the same `candidateBaseLabel(c)`, return `` `${base} (${c.astral_candidate_id})` ``; else return `base`.
   - Export `sortCandidatesForSelect(candidates: CandidateInfo[]): CandidateInfo[]` — copy sorted by `candidateOptionLabel` ascending (localeCompare), tie-break `astral_candidate_id`.

2. In `src/ui/frontend/src/contexts/CandidateContext.tsx`, export the `CandidateInfo` interface (it is currently file-private) so `candidateLabel.ts` and the hook can type against it without duplicating shape.

3. Create `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts`:
   - Import `useCandidate`, `useCallback`, `useEffect`, `useMemo`, `useRef`, `useState`.
   - Type `AdminCandidateFilterValue = "" | string` where `""` means **All**.
   - Export `navDefaultCandidateFilter(selectedId: string | null): AdminCandidateFilterValue` as `selectedId ?? ""`.
   - Hook signature:
     ```ts
     type UrlBacked = {
       value: AdminCandidateFilterValue
       setValue: (next: AdminCandidateFilterValue) => void
     }
     type Options = {
       urlBacked?: UrlBacked
       /** When true on first mount, do not treat existing URL value as user-pinned (Execution History / Timesheets). */
       urlPresentDisablesSync?: boolean
     }
     export function useAdminCandidateFilter(options?: Options)
     ```
   - Internal state: `syncWithNav` boolean, init `true` unless `options.urlBacked?.value` is non-empty on first render **and** `urlPresentDisablesSync` is true — then init `syncWithNav` to `false` (explicit URL bookmark).
   - Internal state: `candidateFilter` — when `options.urlBacked` provided, treat `urlBacked.value` as source of truth for reads; when local-only (Scheduled Actions), use `useState(navDefaultCandidateFilter(selectedId))`.
   - `setCandidateFilter(next)` — always sets `syncWithNav = false`, then updates local state or calls `urlBacked.setValue(next)`.
   - `useEffect` on `[selectedId]` (deps also include `syncWithNav`): when `syncWithNav === true`, set filter to `navDefaultCandidateFilter(selectedId)` without marking manual (do not flip `syncWithNav`).
   - Return `{ candidateFilter, setCandidateFilter, syncWithNav, candidates: sortCandidatesForSelect(candidates from useCandidate()) }`.

4. Create `src/ui/frontend/src/components/AdminCandidateFilterControl.tsx`:
   - Props: `{ value: AdminCandidateFilterValue; onChange: (v: AdminCandidateFilterValue) => void; candidates: CandidateInfo[] }`.
   - Render matching existing admin filter markup:
     ```tsx
     <label>
       Candidate
       <select value={value} onChange={e => onChange(e.target.value)}>
         <option value="">All</option>
         {candidates.map(c => (
           <option key={c.astral_candidate_id} value={c.astral_candidate_id}>
             {candidateOptionLabel(c, candidates)}
           </option>
         ))}
       </select>
     </label>
     ```
   - Do not add new CSS classes; use existing `admin-filters` parent styling.

⚠️ **Decision:** One hook supports both local state (Scheduled Actions) and URL-backed state (Execution History, Agent Timesheets) so nav-sync and manual-pin rules stay identical. URL pages pass `setValue` that already updates `searchParams` (existing `setFilter` helpers).

⚠️ **Decision:** Once Susan manually changes the on-page Candidate dropdown, `syncWithNav` stays `false` for the remainder of that page mount — nav changes do not override until full page reload/navigation away. Matches parent AC6 parenthetical (no re-enable on picking nav-default again).

## Stage 2: Scheduled Actions — explicit Candidate filter, remove silent nav filter

**Done when:** Scheduled Actions shows **Candidate** dropdown next to **Task** filter; table rows filter only by on-page Candidate + Task filters; with nav candidate **c1** selected and default sync, only **c1** rows show; **All** shows every candidate's tasks.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, import `useAdminCandidateFilter` and `AdminCandidateFilterControl`.
2. Replace bare `const { selectedId } = useCandidate()` with hook usage **without** `urlBacked`:
   ```ts
   const { candidateFilter, setCandidateFilter, candidates } = useAdminCandidateFilter()
   ```
   Keep `selectedId` from `useCandidate()` only where still needed (`openAdd` form default at line ~227).
3. In `filteredRows` `useMemo` (~lines 138–143), **remove** `if (selectedId) filtered = filtered.filter(r => r.candidate_id === selectedId)`.
4. Add candidate filtering: `if (candidateFilter) filtered = filtered.filter(r => r.candidate_id === candidateFilter)`.
5. Update `useMemo` deps: replace `selectedId` with `candidateFilter`.
6. In the `admin-filters` block (~324–332), insert `<AdminCandidateFilterControl value={candidateFilter} onChange={setCandidateFilter} candidates={candidates} />` **before** the existing Task `<label>`.
7. Do not change API calls, phase sections, modals, thread polling, or Add Task modal candidate field (still uses nav `selectedId`).

## Stage 3: Execution History — full candidate list, nav default, URL behavior

**Done when:** Candidate dropdown lists every entry from `/api/candidates` (via context), including candidates with zero rows in the current date window; first visit without `candidate_id` URL param defaults filter to left-nav candidate; **All** clears param and shows all candidates within other filters; task/status/date URL params unchanged.

1. In `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, import hook + control; keep `useCandidate()` for `candidates`/`selectedId`/`tz`.
2. **Delete** the `candidateOptions` `useMemo` (~lines 139–142) that derives options from `rows`.
3. Wire URL-backed filter before `filters` `useMemo`:
   - Add helper `function candidateIdFromParams(sp: URLSearchParams): AdminCandidateFilterValue { return sp.get("candidate_id") || "" }`.
   - Define `setCandidateParam = useCallback((next: AdminCandidateFilterValue) => { setSearchParams(prev => { const n = new URLSearchParams(prev); if (next) n.set("candidate_id", next); else n.delete("candidate_id"); return n }, { replace: true }) }, [setSearchParams])`.
   - Call hook:
     ```ts
     const urlCandidate = candidateIdFromParams(searchParams)
     const { candidateFilter, setCandidateFilter, candidates } = useAdminCandidateFilter({
       urlBacked: { value: urlCandidate, setValue: setCandidateParam },
       urlPresentDisablesSync: true,
     })
     ```
4. Add mount effect (after existing `date_from` default effect, ~122–132): when `!searchParams.get("candidate_id")` **and** hook reports `syncWithNav` still true **and** `selectedId` is set, call `setCandidateParam(selectedId)` once (use a `useRef` guard `initialCandidateDefaultApplied` to avoid fighting manual clears). When `selectedId` is null and param absent, leave param absent (**All**).
5. Replace Candidate `<select>` (~262–268) with `<AdminCandidateFilterControl value={candidateFilter} onChange={setCandidateFilter} candidates={candidates} />`.
6. Leave `filters` `useMemo` reading `candidate_id` from `searchParams` unchanged — ledger fetch already respects URL query string.
7. Do not change Skip Checks, log expand, batch modal, sort, or date default logic.

⚠️ **Decision:** Keep server-side filtering via existing `/api/admin/dispatch_ledger?candidate_id=` query param rather than client-only filtering of `rows`, so pagination/date windows stay consistent with backend.

## Stage 4: Agent Timesheets — dropdown + nav default + export parity

**Done when:** Candidate filter is a dropdown (**All** + full list); defaults to nav selection when no `candidate_id` in URL; totals bars and Export CSV use the same `filters` object including active candidate filter.

1. In `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx`, import hook + control; import `useCandidate` for `selectedId`.
2. Add `setCandidateParam` mirroring Stage 3 step 3 (same URLSearchParams set/delete pattern).
3. Wire `useAdminCandidateFilter` with `urlBacked` + `urlPresentDisablesSync: true`.
4. Add the same one-time initial default effect as Stage 3 step 4 when `candidate_id` absent and `selectedId` set.
5. Replace Candidate free-text `<input>` block (~163–167) with `<AdminCandidateFilterControl … />`.
6. Do not change date/batch filters, `ListPage`, selection totals, or export URL construction — `handleExport` already passes `filters` query string; verify no code path strips `candidate_id` after this change (no edit needed if already generic).

## Self-Assessment

**Scope:** `Single-Component` — frontend-only changes in three admin pages plus two small shared modules; no backend, config, or nav shell edits.

**Conf:** `high` — reuses existing `useCandidate`, `admin-filters` markup, and URL filter patterns already present on Execution History and Agent Timesheets; behavior is fully specified in AST-628/634 AC.

**Risk:** `Medium` — incorrect nav-sync or URL default logic would show wrong candidate scope on admin ops screens, but would not affect dispatch execution or data integrity.

## Rules self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Shared hook + label helper + control avoid triplicating nav-sync logic. |
| §2.1 config | No new config keys; candidate list from existing `/api/candidates`. |
| §2.4 batch | N/A — UI-only. |
| §2.6 state machine | N/A. |
| §3.3 imports | New files stay under `src/ui/frontend/`; no cross-layer violations. |
| §3.5 naming | `useAdminCandidateFilter`, `AdminCandidateFilterControl`, `candidateOptionLabel` match existing frontend conventions. |

No conflicts requiring `conf-!!-NONE`.

## QA manifest (Betty)

When picking tests in **qa-child**, cover at minimum:

1. **Scheduled Actions:** with `localStorage astral_selected_candidate=c1` and tasks for c1+c2, default view shows only c1; select **All** shows both; change nav to c2 while still at default updates dropdown to c2; after manual **All**, nav change does not alter dropdown.
2. **Execution History:** mock `/api/candidates` with c1+c2 but ledger rows only for c1 — Candidate dropdown still lists c2; first visit without URL param scopes fetch to c1 when nav is c1.
3. **Agent Timesheets:** Candidate control is `<select>` not text input; export URL includes `candidate_id` when filtered.

## Execution contract

- Execute stages 1→4 in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs`.
- Do not edit `tests/` or `docs/ASTRAL_TEST_BIBLE.md` (Betty owns tests).
- Blocking ambiguity → comment on **AST-628** with 🛑 template from **plan-child**.

## Review (build)

**Branch:** `origin/sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs`  
**Tip:** `aeda4fdc`  
**Built:** Stage 1 — `candidateLabel.ts`, `useAdminCandidateFilter`, `AdminCandidateFilterControl`, export `CandidateInfo`. Stage 2 — `AdminScheduledActions` client filter + control. Stage 3 — `AdminPerformanceMonitor` full candidate list, URL default/sync. Stage 4 — `AdminAgentTimesheets` dropdown + URL parity. Component tests deferred to Betty per build-child test-tree ban.

**Betty manifest (Code Complete):** see **QA manifest (Betty)** above.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-628/AST-634-admin-candidate-filter-on-three-admin-tabs` (tip `87911345`)  
**Reviewed:** 2026-06-14

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–4 land as specified: shared `candidateLabel` / `useAdminCandidateFilter` / `AdminCandidateFilterControl`; Scheduled Actions client filter replaces silent nav filter; Execution History + Timesheets URL-backed with nav default effect. |
| AC coverage | Betty manifest exercises default-from-nav, All, manual pin, global candidate list on Execution History, export `candidate_id` on Timesheets. |
| §3.3 layers | Frontend-only; no `data` / `external` imports. |
| §1.3 DRY | Nav-sync + label logic centralized; label rules match `NavigationShell.tsx` name join. |
| §2.1 config | Candidate list from existing `/api/candidates` context — no duplicate state strings. |

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| discuss | `useAdminCandidateFilter.ts` L37–43, L53–56; callers pass inline `urlBacked` object | `applyFilter` depends on `urlBacked` identity; parent re-renders recreate the object → nav-sync `useEffect` may re-fire and call `setSearchParams` every render while `syncWithNav`. Tests work around RTL hangs via seeded `candidate_id` (`withCandidateQuery`). Stabilize deps (`setValue` + `value` as separate hook args, or memoize `urlBacked` at call site) before UAT on “first visit, no URL param”. |
| discuss | `AdminPerformanceMonitor.tsx` + `AdminAgentTimesheets.tsx` | Duplicate `candidateIdFromParams` / `setCandidateParam` — fine for this ticket; extract only if a fourth admin screen needs the same pattern. |
| advisory | `AdminPerformanceMonitor.tsx` `tz` useMemo | Date defaults still use **nav** `selectedId` timezone, not on-page candidate filter — pre-existing; acceptable unless Susan wants filter-scoped TZ. |
| advisory | `candidateLabel.ts` L338 | `(c.candidate_data \|\| {})` cast for display labels — bounded UI use, matches nav shell pattern. |

### Recommended actions

| Priority | Action |
|----------|--------|
| resolve-child | Optional hardening: decouple `applyFilter` from inline `urlBacked` object identity; smoke first visit to Execution History / Timesheets with empty `candidate_id` query (nav candidate set). |
| UAT | Confirm AC6 nav-sync + manual pin on all three screens in staging. |

**Verdict:** Approve for `resolve-child` / UAT — no fix-now blockers; one discuss item on hook dependency stability worth addressing if first-load URL default flickers in staging.

## Resolution

**Date:** 2026-06-14 · **Review:** Radia @ `7eb0b981` · **Product tip:** `87911345`

| Item | Outcome |
|------|---------|
| fix-now | None — ship as reviewed. |
| discuss — `urlBacked` object identity / nav-sync `useEffect` | Deferred optional hardening; smoke first visit (nav candidate set, no `candidate_id` URL param) in UAT before extracting `urlValue`/`setUrlValue` args. |
| discuss — duplicate URL helpers on Execution History + Timesheets | Accepted for this ticket; extract only if a fourth admin screen needs the pattern. |
| advisory — `tz` follows nav not filter | Pre-existing; no change unless UAT asks for filter-scoped timezone. |
| advisory — `candidate_data \|\| {}` in labels | Display-only; matches nav shell. |

**Tests:** Betty manifest green @ `87911345` (Katherine `test-child`).
