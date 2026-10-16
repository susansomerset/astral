<!-- linear-archive: AST-2150 archived 2026-10-16 -->

## Linear archive (AST-2150)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2150/default-scheduled-actions-and-execution-history-to-all-candidates  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-2148 — Remove autofilter by candidate from Execution history & Scheduled Actions  
**Blocked by / blocks / related:** parent: AST-2148

### Description

## What this implements

Removes the left-nav candidate auto-filter (initial default and nav-sync) from Scheduled Actions and Execution History so both open on **All** and only narrow when the operator picks a candidate; Execution History still honors an explicit `candidate_id` URL. Does not touch the shared hook, the other screens that use it, the Add Task pre-fill, or any API.

## Citations

none — Canon Scope is empty (frontend filter default only; no in-force pattern or statute applies).

## Scope

* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — drop the nav-synced candidate filter default; filter starts at All. Technical: stop using the nav-synced `useAdminCandidateFilter` hook; hold the Candidate filter as plain page state that starts at All (empty), with the candidate option list taken from the candidate context sorted the same way the shared control expects. The existing client-side row filter, the All-candidate default sort (by Avail desc), and the Add Task modal's `selectedId` pre-fill are unchanged.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` — **modified** (Execution History) — drop the nav-synced candidate filter default and the first-visit effect that writes the nav candidate into the URL. Technical: stop using the nav-synced hook; the Candidate filter value is read straight from the URL `candidate_id` param (absent = All) and written back through the existing URL setter; remove the first-visit effect that copies the left-nav candidate into the URL. Timezone derivation from the left-nav candidate is unchanged.

## Acceptance criteria

 1. **Wrong-shape guard:** `rg -n "useAdminCandidateFilter" src/ui/frontend/src/pages/AdminScheduledActions.tsx src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` returns nothing. Fail: either page still imports the nav-synced hook (including via a new option flag on it).
 2. **Hook and other screens untouched:** `git diff origin/dev -- src/ui/frontend/src/hooks/useAdminCandidateFilter.ts src/ui/frontend/src/components/AdminCandidateFilterControl.tsx src/ui/frontend/src/pages/AdminAgentTimesheets.tsx src/ui/frontend/src/pages/AdminVectorFeedback.tsx src/ui/frontend/src/pages/AdminTaskPerformance.tsx src/ui/api/` is empty. Fail: any diff.
 3. **Scheduled Actions default All:** with left-nav candidate **A** selected and dispatch tasks for **A** and **B**, first load shows the Candidate dropdown at **All** and rows for both **A** and **B**. Fail: dropdown shows **A** or **B**'s rows are hidden.
 4. **Scheduled Actions ignores nav:** switching left-nav from **A** to **B** leaves the Candidate dropdown and visible rows unchanged. Fail: dropdown changes or rows narrow.
 5. **Execution History default All:** opening Execution History with left-nav **A** selected and no `candidate_id` in the URL issues `/api/admin/dispatch_ledger` without a `candidate_id` query param, leaves the page URL without `candidate_id`, and shows the dropdown at **All**. Fail: the fetch or URL carries `candidate_id=A`, or the dropdown shows **A**.
 6. **Execution History ignores nav:** switching left-nav from **A** to **B** does not add/change `candidate_id` in the URL or the ledger fetch. Fail: either changes.
 7. **Bookmark honored:** opening Execution History with `?candidate_id=B` (left-nav **A**) fetches the ledger with `candidate_id=B` and shows **B** in the dropdown. Fail: fetch unscoped, scoped to **A**, or dropdown not **B**.
 8. **Manual filter still works:** on both screens, choosing **B** in the dropdown narrows to **B** (Scheduled Actions rows all have `candidate_id` **B**; Execution History refetches with `candidate_id=B`), and choosing **All** restores every candidate. Fail: selection has no effect or All does not restore.
 9. **Add Task pre-fill unchanged:** on Scheduled Actions with left-nav **A**, **Add Task** opens with Candidate **A**; with no left-nav candidate, Save stays disabled (`save disabled on add when no candidate selected` stays green). Fail: pre-fill is blank with **A** selected, or Save enables with no candidate.
10. **Build:** `npm run build` passes and `npm run lint` reports no findings in the changed files beyond those already on `origin/dev` (dev carries pre-existing lint errors); the Vitest files named in Technical scope pass. Fail: build error, a new lint finding in a changed file, or a failing Vitest.

## Boundaries

Single child of AST-2148 — no siblings. Does not touch `src/ui/frontend/src/hooks/useAdminCandidateFilter.ts`, `src/ui/frontend/src/components/AdminCandidateFilterControl.tsx`, Agent Timesheets / Vector Feedback / Task Performance, the Add Task modal candidate pre-fill, Execution History timezone derivation, or any backend/API file.

## Notes for planning

Canon Scope is empty. Test impact (Betty, `qa-child`): the AST-634 nav-default / nav-sync cases in `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` and the AST-634 setup note in `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` assert the behavior being removed; the AST-628 summary in `docs/test-bible/frontend/pages.md` describes it. `tests/component/frontend/hooks/test_useAdminCandidateFilter.test.tsx` stays as-is.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-2148-sa-eh-default-all-candidates`, child `sub/AST-2148/AST-2150-sa-eh-default-all-candidates`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-12T18:46:41.366Z
[code-rubric] PROCEED (Commit: 1d360ee85) SA/EH default All

#### betty — 2026-10-12T18:44:25.514Z
`origin/sub/AST-2148/AST-2150-sa-eh-default-all-candidates` @ `1d360ee85` · All-default tests, bible updated

#### joan — 2026-10-12T18:36:14.713Z
[plan-rubric] PROCEED (Commit: e2af6d87) two pages, All default

#### katherine — 2026-10-12T18:34:32.189Z
`origin/sub/AST-2148/AST-2150-sa-eh-default-all-candidates` @ `e2af6d87b` · plan; lint baseline flagged

---

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


## Joan validate

[plan-rubric]

**Ticket:** AST-2150
**Overall:** APPROVED
**Corpus:** 26c4e86a4d08addcefdbc3be68116703fedf6762 (`canon/` tree at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `origin/sub/AST-2148/AST-2150-sa-eh-default-all-candidates` @ `e2af6d87bb09805284f13a0152d5de05c52a769a`

## Canon scores

Frozen list empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion with rationale). No directive rows to score; not a §4a list-missing **ESCALATE** because the parent explicitly declared empty scope.

## Traceability

AC1→S1.5–6,S2.11,cross-stage·1 · AC2→cross-stage·2 · AC3→S1 · AC4→S1 · AC5→S2 · AC6→S2 · AC7→S2.2,6 · AC8→S1.4,S2.9 · AC9→S1.4 · AC10→Lint baseline,S1.6,S2.12,build; page Vitest→cross-stage Vitest note/`qa-child` · Parent Purpose/Functional scope 1–3→Stages 1–2; no orphan stages.

### Findings

**acceptable** | `## Scope gate` / Files Changed · Two page files only; matches child `## Scope` and parent Component/Technical scope; hook, control, other admin pages, and API explicitly out of bounds.

**acceptable** | Stage 1 / Stage 2 decisions · Page-local `useState("")` and URL-only filter reject hook flags and new helpers — consistent with AC1 wrong-shape guard and Boundaries.

**acceptable** | `## Lint baseline (AC10)` · Honest reconciliation of whole-tree lint red on `origin/dev` vs AC2-forbidden files; per-file gates and “no new findings” are executable; build must stay green.

**discuss** | Child AC10 vs plan gates · Ticket text still says whole-tree `npm run lint` and Vitest pass; plan substitutes lint-baseline + Betty-owned page test rewrites. Workflow-consistent for this repo; optional future AC wording tweak so Radia/UAT do not read AC10 literally before `qa-child`.

**discuss** | Lint baseline SHA `c4f0d3a59` · Baseline counts are pinned to a cited dev tip; engineer should re-snapshot error/warning totals at implementation time if `origin/dev` moved materially (plan already says stop-and-comment if totals worsen).

**acceptable** | Canon Scope gap skim (`astral.standards.in-scope-only`, `astral.ui.frontend-file-placement`) · Plan stays inside two existing page files and reuses `sortCandidatesForSelect`; parent locked **none** at Discussion — §4b observation only, not scored.

### R6 (summary)

Definition fidelity: implements parent Purpose and all functional bullets without hook or sibling creep. DRY: mirrors hook’s sort path via shared `candidateLabel` helper instead of duplicating sort logic. Stages cite concrete line anchors verified against current tree (`AdminScheduledActions.tsx` 335–336, `AdminPerformanceMonitor.tsx` 101–120 / 161–167). Self-assessment: Estimate confirm 2 is proportionate; ⚠️ Decision blocks are specific. No `!!-NONE` conf gap.

**Identity:** Plan Ready · assignee Joan Clarke · 0 completed `[plan-discuss]` rounds.

context_tokens≈18500

**Upshot:** `[plan-rubric] PROCEED (Commit: e2af6d87) two pages, All default`

## Review

Built on `origin/sub/AST-2148/AST-2150-sa-eh-default-all-candidates`:

- `50a867380` code(AST-2150): Stage 1 — Scheduled Actions Candidate filter is page state starting at All; nav no longer seeds or syncs it
- `5224779ae` code(AST-2150): Stage 2 — Execution History Candidate filter read/written only via URL `candidate_id`; first-visit nav→URL effect removed

Build notes:

- **Lint baseline held:** `AdminScheduledActions.tsx` shows only the 2 pre-existing `no-extra-boolean-cast` errors (shifted to lines 603/631 by the 3-line import/state edit); `AdminPerformanceMonitor.tsx` clean; whole tree still 25 errors / 4 warnings. `origin/dev` did not move since the `c4f0d3a59` snapshot. `tsc -b --noEmit` and `npm run build` green.
- AC1 grep empty; AC2 diff empty; `git diff origin/dev --stat` = the two pages + this doc.
- **Parent ref name:** the parent is `origin/ftr/AST-2148-sa-eh-default-all-candidates` (at `c4f0d3a59`, already in this sub). `sync-child.sh --ftr AST-2148` reports it "not found" because it looks up the short name; harmless here. `validate-sub-log.sh --stage=build` run with the full ftr name: status=ok.
- Page Vitest AST-634 cases are expected red until `qa-child` (see Vitest note above); not run as a build gate.


## Radia review

[code-rubric]

**Ticket:** AST-2150  
**Publish ref:** `1d360ee85f7babe7b6d7fd180fe4a558348b96d9` (`origin/sub/AST-2148/AST-2150-sa-eh-default-all-candidates`)  
**Corpus:** `26c4e86a4d08addcefdbc3be68116703fedf6762`  
**Overall:** CLEAN

## Canon scores

Frozen list empty (Linear **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not a §5.3 **ESCALATE** (explicit empty scope, same as Joan plan stage).

## Column diff vs plan stage

(aligned) — Joan recorded no per-directive rows; code review matches empty frozen list.

## Frame diff

- [ ] **Acceptance criteria AC10:** Consider aligning ticket text with the plan’s **lint-baseline** gate (“no new findings” on the two page files + whole-tree totals ≤ baseline) rather than literal whole-tree `npm run lint` passes — bible manifest § AST-2150 already documents the substitute; optional wording tweak before **User Testing** if UAT reads AC10 literally.

## Findings

**fix-now:** (none)

**discuss:** (none requiring `@susan` — Tests Passed + bible manifest already encode AC10/lint and Vitest scope.)

**advisory**

- **Plan fidelity:** Product diff is exactly the two pages (`AdminScheduledActions.tsx`, `AdminPerformanceMonitor.tsx`): hook removed, SA uses `useState("")` + `sortCandidatesForSelect(navCandidates)`, EH uses URL-only `candidate_id` with first-visit nav→URL effect removed; `openAdd` still sets `candidate_id: selectedId ?? ""`. AC1 grep clean; AC2 forbidden-path diff empty (0 bytes).
- **QA / bible:** `test_AdminScheduledActions.test.tsx` AST-2150 describe (3 cases), `test_AdminPerformanceMonitor.test.tsx` AST-2150 describe (4 cases) + `renderPerformanceMonitor` no longer injects `candidate_id`; retained AST-634 EH cases remain URL-driven. `docs/test-bible/frontend/pages.md` AST-2150 block maps manifest to ACs including AC9 via existing Add Task tests.
- **Canon Scope observation (off-list, not scored):** `astral.standards.in-scope-only` / `astral.ui.frontend-file-placement` — changes stay in existing page files and reuse `sortCandidatesForSelect`; no hook/sibling/API creep.
- **Ticket vs plan:** Linear AC10 still says full-tree lint + “Vitest files named in Technical scope”; implementation and Betty manifest correctly use lint-baseline + listed component suites — workflow-consistent; frame-diff row above is optional hygiene only.

## What's solid

- Minimal, plan-faithful detach from `useAdminCandidateFilter` on both screens; EH keeps `setCandidateParam` / `replace: true` and timezone `useMemo` on `selectedId`.
- Test rewrites target the removed AST-634 nav-default behavior without dropping EH URL-scoping regression cases.
- Estimate **2** matches footprint (two small page edits + expected test/bible carry).

## Recommended actions (downstream — not for Radia)

- Chuckles: append this artifact, `docs()` commit, post slim upshot `--as radia`, **Review Posted**.
- **resolve-child:** Only if Susan wants AC10 description wording updated — tick frame-diff row; no product change required for canon/plan compliance on this tip.

**Upshot:** `[code-rubric] PROCEED (Commit: 1d360ee85) SA/EH default All`
