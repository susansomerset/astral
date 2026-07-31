# Fix Scheduled Actions blank page on Candidate All + Avail All

**Linear:** [AST-1104](https://linear.app/astralcareermatch/issue/AST-1104/fix-scheduled-actions-blank-page-on-candidate-all-avail-all-bug-when)
**Parent:** [AST-1102](https://linear.app/astralcareermatch/issue/AST-1102/bug-when-select-all-candidates-and-all-avail-count)
**Publish ref:** `sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all`

On Admin → Scheduled Actions, setting **Candidate: All** together with **Avail: All** tears the SPA down to an empty `#root` (black page, no header/nav). View-source still shows the Vite shell with an empty root div — classic uncaught React render/effect exception with no ErrorBoundary. This ticket reproduces that path, pins the throw site, and fixes only what the crash requires so chrome + Scheduled Actions content (list or existing empty-filter status) stay mounted. Avail All / Candidate All semantics from AST-887 / AST-888 / AST-894 stay intact; defaults (Avail `> 0`) and other filter combos must keep working.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Only if Stage 1 pins the throw here: harden the offending render/effect path (cell format, expand/prune, or table mount) so Candidate All + Avail All cannot unmount the tree | ui |
| `src/ui/frontend/src/lib/fmt.ts` | Only if Stage 1 pins `fmtTime` / invalid `timeZone`: catch `RangeError` (and equivalent) from `toLocaleString` and fall back to UTC formatting (or raw ISO when the date itself is unusable) so Last Run cells cannot blank the SPA | ui |
| `src/ui/frontend/src/components/Time.tsx` | Only if Stage 1 pins `<Time>` / candidate timezone: coerce missing/invalid IANA timezone to `"UTC"` before calling `fmtTime` (same fallback rule as `fmt.ts`) | ui |

**Out of scope (this ticket):** Available calculation / claim / dispatch; Avail column formatting semantics (zero/empty still em dash); new Avail modes or filter-bar redesign; Run / Stop / AUTO / edit-modal / Manage Tasks; Recommended Jobs or other sectioned screens; a new global React error-boundary epic; API / `api_admin.py` payload changes unless Stage 1 proves a server fault as root cause (then stop and comment — do not invent backend work); `tests/` and `docs/test-bible/**` (Betty at Code Complete).

**QA note (Betty — not engineer commits):** Extend `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` (and/or `test_Time.test.tsx` / `test_fmt.test.ts` if the pin is timezone) so Candidate All + Avail All keeps header/title and list-or-empty-status mounted; preserve AST-887/AST-894 Avail default + zero-row visibility; regression smoke `AST-1104|AST-894|AST-887|AST-893|AST-751|AST-768|AST-785`.

---

## Stage 1: Reproduce and pin the throw

**Done when:** The Candidate All + Avail All failure is reproduced (or a fixture-backed component/lib test that throws the same way), and a Linear comment on **AST-1104** records the exact exception name/message plus stack top (`file:line`). No product fix lands in this stage’s commit unless the pin is already known from an existing failing assertion written in this stage.

1. On the epic worktree (`astral-AST-1102/`), confirm checkout is `sub/AST-1102/AST-1104-fix-sa-blank-candidate-all-avail-all`, `origin/dev` is an ancestor of `HEAD`, and `origin/ftr/AST-1102-bug-when-select-all-candidates-and-all-avail-count` has been merged (no-op if current).

2. Reproduce with the live admin UI when available:
   - Run Flask + Vite per `ASTRAL_CODE_RULES` §3.5.
   - Open Admin → Scheduled Actions (landing defaults: Avail `> 0`, Expand All).
   - Set **Candidate** to All, then **Avail** to All (or the reverse).
   - Confirm the viewport goes blank / `#root` empty and capture the **browser console** first error + stack.

3. If live data does not blank locally, pin with a focused failing harness instead (still Stage 1 — no silent guessing). Prefer the smallest of:
   - **A — invalid timezone + Last Run visible only under All+All:** mount Scheduled Actions (or `<Time>`) with nav-selected candidate `candidate_data.contact.timezone` set to a non-IANA string (e.g. `"Not/AZone"`), and at least one dispatch-task row with non-null `last_run_at` that is hidden under default Avail `gt0` (e.g. `available_count: 0`) but visible after `selectAvailAll()` + `selectAllCandidatesFilter()`. Expect uncaught `RangeError: Invalid time zone specified: …` from `fmtTime` / `<Time>` (confirmed: `fmtTime(iso, "Not/AZone")` throws today; there is no root ErrorBoundary in `main.tsx`).
   - **B — non-number `score_floor` on a newly visible scored row:** mount a scored row with `score_floor` as a string (e.g. `"1.00"`) that only appears under Candidate All + Avail All; expect `TypeError` from `(row.score_floor ?? 1).toFixed(2)` in `ScheduledPhaseTable`.
   - **C — expand / measure update-depth:** fixture with multiple sections + Expand All + All+All row growth; expect React “Maximum update depth exceeded” (or equivalent) from the expand-prune effect and/or `useListTableColumnMeasure` — only treat as the pin if the console stack points there.

4. Post a comment on **AST-1104** (not the parent) with:
   - Repro path (live UI vs harness A/B/C)
   - Exact exception + top of stack
   - Which Files Changed row will be edited in Stage 2

5. If none of A–C match the live stack and the page still blanks only in an environment you cannot capture, **stop** with the 🛑 Stage format on the **parent** AST-1102 and wait — do not invent a fourth root cause.

⚠️ **Decision:** Treat empty `#root` as an **uncaught exception**, not a CSS/black-background bug and not “missing data.” Do not add a global ErrorBoundary in this ticket (parent boundary). Stage 1 must name one throw site before Stage 2 edits product code.

**Ritual:** `docs(AST-1104):` only if this stage adds harness notes inside the plan; otherwise no commit — proceed to Stage 2 in the same build session after the Linear pin comment. (Plan-child publishes this plan doc separately; build-child owns product commits.)

---

## Stage 2: Fix only the pinned throw

**Done when:** Candidate All + Avail All keeps app chrome and Scheduled Actions content mounted; zero/empty Avail rows that exist in loaded data remain visible under Avail All with no other narrowing filters; fresh load still defaults Avail to `> 0`; switching Candidate/Avail among All / specific / `> 0` does not blank the page. `cd src/ui/frontend && npx tsc -b --noEmit` passes.

Execute **exactly one** branch matching the Stage 1 pin. Do not apply the other branches “just in case.”

### Branch A — `fmtTime` / `<Time>` invalid timezone

1. In `src/ui/frontend/src/lib/fmt.ts`, inside `fmtTime`, keep the existing null/empty → `"—"` and invalid-date → `String(iso)` behavior. Wrap the `toLocaleString(..., { timeZone })` call in `try/catch`. On failure (invalid time zone or other locale error), retry once with `timeZone: "UTC"`. If that also fails, return `String(iso)`. Do not change the happy-path format options (en-US, 2-digit year, etc.).

2. In `src/ui/frontend/src/components/Time.tsx`, when reading `contact?.timezone`, if the value is missing/blank use `"UTC"` (already true). Optionally pass through `fmt.ts` only — do **not** duplicate a second try/catch in `Time.tsx` if `fmtTime` already absorbs the RangeError. Prefer single absorption in `fmt.ts` (§1.3 DRY).

3. Do **not** change `CandidateContext` timezone sync unless Stage 1 stack shows the throw outside `fmtTime`/`Time` (unlikely). Do not validate timezone lists in config.

### Branch B — `score_floor.toFixed` TypeError in ScheduledPhaseTable

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx` `ScheduledPhaseTable` Floor cell, replace `(row.score_floor ?? 1).toFixed(2)` with a number-safe format: `const floor = Number(row.score_floor ?? 1);` then display `Number.isFinite(floor) ? floor.toFixed(2) : "—"` (still only when the row is scored). Do not change Floor filter math, score_floor persistence, or non-scored blank cells.

2. Do not widen `DispatchTask.score_floor` typing beyond what the fix needs; do not change the API.

### Branch C — expand / measure maximum update depth

1. In `AdminScheduledActions.tsx` and/or `useListTableColumnMeasure.ts` / `useSectionExpandPolicy.ts`, apply the **minimal** stability fix indicated by the stack (e.g. avoid `setExpandedKeys` when the pruned set equals current membership; keep `widthsEqual` guard; do not re-expand on every filter change — AST-894 once-gate stays). Touch only the file(s) named in the Stage 1 pin comment.

2. Do not change Expand All policy defaults or Avail filter predicates.

### Shared constraints (all branches)

1. Do **not** change `filteredRows` Avail predicate (`availGtZeroFilter === "gt0"` → `(r.available_count ?? 0) > 0`) or Candidate filter equality.
2. Do **not** change `formatAvailableCount` em-dash rules for null/0.
3. Do **not** redesign the filter bar or add recovery UI beyond stopping the throw.
4. If the pinned stack is in API/backend code, **stop** and comment — frontend-only unless root cause proves otherwise.

⚠️ **Decision:** Primary planning hypothesis is **Branch A** (invalid candidate timezone + first non-null `last_run_at` becoming visible when filters widen), because `fmtTime` throws today, `main.tsx` has no ErrorBoundary, and Last Run uses `<Time>` on every table row. Stage 1 still wins if the live stack says B or C.

**Ritual:** `code(AST-1104): stop SA blank page on Candidate All + Avail All`

---

## Stage 3: Verify filter survival (manual / existing tests)

**Done when:** Builder has smoke-checked the AC combinations on the fixed tip; existing component file still runs for the suites listed below (or failures are clearly pre-existing / test-only and handed to Betty via `[qa-handoff]` only after product AC is met).

1. Manual smoke on Admin → Scheduled Actions:
   - Landing: Avail defaults to `> 0`, page usable, chrome present.
   - Candidate All + Avail All: header, nav, Scheduled Actions title/filters remain; list shows zero/empty Avail rows when present in data (or existing empty-filter status if nothing matches other filters — not a blank `#root`).
   - Candidate specific + Avail All; Candidate All + Avail `> 0`; back to defaults — none blank the page.
2. Run (product sanity, not Betty ownership of new cases):
   ```bash
   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
     --testNamePattern="AST-894|AST-887|AST-893|AST-751|AST-768|AST-785"
   ```
   If green, proceed. If red only because a new AST-1104 assertion is missing, leave test authorship to Betty. If red because the product fix broke Avail/expand semantics, fix product code (still this ticket) — do not “fix” tests in `tests/`.
3. `cd src/ui/frontend && npx tsc -b --noEmit`

**Ritual:** no separate commit unless Stage 2 needed a follow-up product fix; otherwise Stage 2 commit is sufficient before Code Complete.

---

## Self-Assessment

**Scope:** `Single-Component` — Scheduled Actions blank-page survival; expected touch is SA page and/or shared `fmtTime`/`Time` used by Last Run cells, not Avail math or dispatch.

**Conf:** `Medium` — empty `#root` plus confirmed `fmtTime` RangeError on bad `timeZone` strongly suggest an uncaught render throw when wider filters mount more Last Run cells, but Stage 1 must pin the live stack before coding (B/C remain possible).

**Risk:** `Medium` — wrong fix could mask a different throw or soften timezone display; Avail/Candidate semantics regressions would break AST-887/AST-894 operator triage. Bounded to UI formatting/stability, not claim/dispatch.

## Code Rules Check

| Rule | Status |
|------|--------|
| §1.1 in-scope only | Pass — only the pinned throw site + listed files; no filter-bar redesign, no global ErrorBoundary epic |
| §1.3 DRY | Pass — timezone absorption prefers `fmt.ts` once; no duplicate catch in every page |
| §2.1 config | N/A — no new config keys; timezone fallback is UTC literal already used by `Time`/`fmtTime` |
| §2.4 batch | N/A — no batch/claim changes |
| §2.6 state machine | N/A |
| §3.3 imports | Pass — frontend-only; no new layer violations |
| §3.5 naming / file placement | Pass — stay in `pages/` / `lib/` / `components/` |
| `astral.layers.ui-config-driven-business-logic` | Pass — no new business rules in React; formatting/error absorption only |

