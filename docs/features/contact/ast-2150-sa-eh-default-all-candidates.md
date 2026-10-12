# AST-2150 — Default Scheduled Actions and Execution History to All candidates

**Parent:** [AST-2148](https://linear.app/astralcareermatch/issue/AST-2148) · **Ticket:** [AST-2150](https://linear.app/astralcareermatch/issue/AST-2150)
**Publish ref:** `origin/sub/AST-2148/AST-2150-sa-eh-default-all-candidates`
**Canon Scope:** empty (no pattern or statute applies — frontend filter default only).

Scheduled Actions and Execution History currently seed their **Candidate** filter from the left-nav candidate through the shared `useAdminCandidateFilter` hook and keep tracking it as the nav changes (AST-634 nav-sync). Execution History additionally writes the nav candidate into the URL on first visit. Astral is multitenant now, so both screens must open on **All** and only narrow when the operator picks a candidate. This ticket detaches both pages from the hook. The hook, the shared `AdminCandidateFilterControl`, the other three screens using the hook, the Add Task pre-fill, Execution History's timezone, and the API stay untouched.

## Scope gate

Every Files Changed row below is one of the two files in this ticket's `## Scope`; each change is the kind its Technical scope names (drop hook → plain page state on Scheduled Actions; drop hook + first-visit effect → URL-param value on Execution History). No gap.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Replace `useAdminCandidateFilter()` with page `useState("")` + sorted candidate list from `useCandidate()` | ui (frontend) |
| `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | Replace `useAdminCandidateFilter({ urlBacked, … })` with URL param read/write; delete first-visit nav→URL effect and its ref | ui (frontend) |

No other file changes. `tests/` and `docs/test-bible/` are Betty's (`qa-child`).

## Lint baseline (AC10)

Whole-tree `npm run lint` is **already red** on the synced tip (`c4f0d3a59`, includes `origin/dev`): **25 errors, 4 warnings** across about 20 files. These include `hooks/useAdminCandidateFilter.ts:58`, `AdminAgentTimesheets.tsx` and `AdminVectorFeedback.tsx`, which AC2 forbids touching. `AdminScheduledActions.tsx` has 2 pre-existing errors (`no-extra-boolean-cast` at lines 600 and 628, `if (!!row.empty_render)`). `AdminPerformanceMonitor.tsx` lints clean.

⚠️ **Decision:** AC10's "`npm run lint` passes" cannot hold literally without editing AC2-forbidden files. The lint gate for this ticket is therefore **no new findings**:
- `npx eslint src/pages/AdminScheduledActions.tsx` (run from `src/ui/frontend`) reports exactly the 2 pre-existing `no-extra-boolean-cast` errors and nothing else.
- `npx eslint src/pages/AdminPerformanceMonitor.tsx` reports nothing.
- Whole-tree `npm run lint` totals are **≤ 25 errors, ≤ 4 warnings**.

The 2 `!!` errors in Scheduled Actions are **not** fixed here, because they are outside this ticket's Technical scope. If Chuckles or Susan want them folded in, that is a Scope amendment. `npm run build` (`tsc -b && vite build`) **is** green on the baseline and must stay green.

## Stage 1: Scheduled Actions — filter starts at All, ignores nav

**Done when:** `AdminScheduledActions.tsx` no longer references `useAdminCandidateFilter`; the Candidate dropdown starts at **All** regardless of left-nav, nav changes do not touch it, picking a candidate still narrows rows, and Add Task still pre-fills from `selectedId`. `npm run build` passes in `src/ui/frontend` and the **Lint baseline** gate holds.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, delete line 4: `import { useAdminCandidateFilter } from "../hooks/useAdminCandidateFilter"`.
2. Directly below the `import { useCandidate } from "../contexts/CandidateContext"` line (line 2), add:
   `import { sortCandidatesForSelect } from "../lib/candidateLabel"`
3. In `export default function ScheduledActions()` replace these two lines (currently 335–336):
   ```tsx
   const { selectedId } = useCandidate()
   const { candidateFilter, setCandidateFilter, candidates } = useAdminCandidateFilter()
   ```
   with:
   ```tsx
   const { selectedId, candidates: navCandidates } = useCandidate()
   // AST-2150: filter is page-local and starts at All — never seeded from or synced to the left nav.
   const [candidateFilter, setCandidateFilter] = useState("")
   // Same ordering AdminCandidateFilterControl gets from the shared hook on other admin screens.
   const candidates = useMemo(() => sortCandidatesForSelect(navCandidates), [navCandidates])
   ```
   `useState` and `useMemo` are already imported on line 1 — do not change line 1.
4. Change nothing else in the file. In particular these stay byte-identical: the `!candidateFilter` Avail-desc branch in the `_default` sort (~line 487), the `if (candidateFilter) filtered = …` row filter (~line 506), the `AdminCandidateFilterControl` JSX (~lines 846–850; it still receives `value={candidateFilter}`, `onChange={setCandidateFilter}`, `candidates={candidates}`), and `openAdd`'s `candidate_id: selectedId ?? ""` (~line 700).
5. Run `rg -n "useAdminCandidateFilter" src/ui/frontend/src/pages/AdminScheduledActions.tsx` — must return nothing.
6. In `src/ui/frontend`: `npm run build` must pass, and the **Lint baseline** gate above must hold. Any lint finding beyond the baseline → fix it if it is in a line this stage wrote; otherwise **stop and comment**.

⚠️ **Decision:** Plain `useState("")` on the page rather than a new option flag on the hook (e.g. `syncWithNav: false`). AC1 explicitly fails on the flag approach, and Boundaries forbid editing the hook. A tiny local `useAllCandidatesFilter` helper was also considered and rejected — that would be a new file outside Scope, for three lines of state.

⚠️ **Decision:** `setCandidateFilter` is the raw `useState` setter. `AdminCandidateFilterControl`'s `onChange: (v: string) => void` accepts it as-is, because `AdminCandidateFilterValue` is `"" | string`, i.e. `string`.

## Stage 2: Execution History — URL-only filter, no nav default

**Done when:** `AdminPerformanceMonitor.tsx` no longer references `useAdminCandidateFilter` (including the type import); with no `candidate_id` in the URL the ledger fetch and URL carry no `candidate_id` and the dropdown shows **All**; an explicit `?candidate_id=B` is honored; picking a candidate writes it to the URL (and the fetch follows); the timezone still derives from the left-nav candidate. `npm run build` passes in `src/ui/frontend` and the **Lint baseline** gate holds.

1. In `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`, delete lines 9–12 (the multi-line `import { type AdminCandidateFilterValue, useAdminCandidateFilter } from "../hooks/useAdminCandidateFilter"` block). Add directly below `import { useCandidate } from "../contexts/CandidateContext"` (line 5):
   `import { sortCandidatesForSelect } from "../lib/candidateLabel"`
2. Change `function candidateIdFromParams(sp: URLSearchParams): AdminCandidateFilterValue {` (line 35) to `function candidateIdFromParams(sp: URLSearchParams): string {`. Body unchanged.
3. Change `const { selectedId } = useCandidate()` (line 86) to `const { selectedId, candidates: navCandidates } = useCandidate()`.
4. Delete line 101: `const initialCandidateDefaultApplied = useRef(false)`.
5. Change the `setCandidateParam` signature (line 103) from `useCallback((next: AdminCandidateFilterValue) => {` to `useCallback((next: string) => {`. Body and deps unchanged.
6. Replace the block from `const urlCandidate = candidateIdFromParams(searchParams)` through the closing `})` of the `useAdminCandidateFilter({ … })` call (currently lines 112–120) with:
   ```tsx
   // AST-2150: the URL is the only source of the Candidate filter — absent = All; the left nav never writes it.
   const candidateFilter = candidateIdFromParams(searchParams)
   const setCandidateFilter = setCandidateParam
   const candidates = useMemo(() => sortCandidatesForSelect(navCandidates), [navCandidates])
   ```
7. Leave the `tz` `useMemo` (currently lines 122–125) exactly as written. It still reads `candidates.find(x => x.astral_candidate_id === selectedId)`, now against the sorted list. Order does not affect `find` by id, and the timezone keeps deriving from the left-nav `selectedId`.
8. Delete the whole first-visit effect (currently lines 161–167):
   ```tsx
   useEffect(() => {
     if (initialCandidateDefaultApplied.current) return
     if (searchParams.get("candidate_id")) return
     if (!syncWithNav || !selectedId) return
     initialCandidateDefaultApplied.current = true
     setCandidateParam(selectedId)
   }, [searchParams, syncWithNav, selectedId, setCandidateParam])
   ```
   Also delete the one blank line that separated it from the next block, so the file keeps single-blank-line spacing.
9. Change nothing else. The `AdminCandidateFilterControl` JSX (~lines 293–297) stays byte-identical and now binds to the local `candidateFilter` / `setCandidateFilter` / `candidates`. `filters` keeps reading `candidate_id` from `searchParams` via `FILTER_KEYS`, so the ledger fetch follows the URL unchanged. The `date_from` default effect is untouched.
10. Imports on line 1: `useRef` stays (still used by `userSetDateFrom` / `userSetDateTo`), `useCallback`, `useMemo` and `useEffect` stay. If `npm run lint` or `tsc` reports any line-1 import as unused, **stop and comment** — do not guess.
11. Run `rg -n "useAdminCandidateFilter|AdminCandidateFilterValue|syncWithNav|initialCandidateDefaultApplied" src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` — must return nothing.
12. In `src/ui/frontend`: `npm run build` must pass, and the **Lint baseline** gate above must hold. Any lint finding beyond the baseline → fix it if it is in a line this stage wrote; otherwise **stop and comment**.

⚠️ **Decision:** `setCandidateFilter` aliases the existing `setCandidateParam` (`replace: true` history). That matches today's behavior, because the hook's URL-backed path called the same setter. The alternative — routing through `setFilter("candidate_id", …)` (a push-history entry) — was rejected: it would change back-button behavior, which is out of scope.

⚠️ **Decision:** Keep a sorted `candidates` list (rather than passing the context's raw `candidates` to the control) so the dropdown order is identical to today's; the tz lookup is order-insensitive.

## Cross-stage verification (before Code Complete)

1. AC1: `rg -n "useAdminCandidateFilter" src/ui/frontend/src/pages/AdminScheduledActions.tsx src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` → no output.
2. AC2: `git diff origin/dev -- src/ui/frontend/src/hooks/useAdminCandidateFilter.ts src/ui/frontend/src/components/AdminCandidateFilterControl.tsx src/ui/frontend/src/pages/AdminAgentTimesheets.tsx src/ui/frontend/src/pages/AdminVectorFeedback.tsx src/ui/frontend/src/pages/AdminTaskPerformance.tsx src/ui/api/` → empty.
3. `git diff origin/dev --stat` shows only the two page files plus this plan doc.

**Vitest note for build/test:** the `AST-634 admin candidate filter` describes in `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` (~line 474) and `test_AdminPerformanceMonitor.test.tsx` (~line 517), plus the AST-634 setup note at line 49 of the latter, assert the nav-default behavior this ticket removes. Red there after Stage 1/2 is expected. Betty rewrites them in `qa-child`. The engineer does **not** edit `tests/`. `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` must stay green (hook unchanged).

## Estimate

Confirm Chuckles estimate: 2 — agree
