<!-- linear-archive: AST-1973 archived 2026-10-08 -->

## Linear archive (AST-1973)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1973/job-modal-info-tab-analysis-via-shared-phase-lines-component-add-full  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1972 — Add full analysis to job modal Info tab  
**Blocked by / blocks / related:** parent: AST-1972

### Description

## What this implements

Extracts the Recommended/Review list's phase-lines block into one shared component and renders it in the Job Detail modal's Info tab above State History, with em dashes for phases not yet graded. Ships Functional scope 1–4. It does not touch the Job Analysis Report modal, the list's toggle or click behavior, or any backend route. If AST-1970 lands first, merge its `JobsRecommended.tsx` changes before editing the analysis row.

## Citations

`astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`.

## Scope

* `src/ui/frontend/src/components/PhaseAnalysisLines.tsx` (**new**): a new component that takes one job record. It derives its phase lines from `manifest.jobs.recommended.report_phase_tabs`, using that order and each tab's `grades_field`. Each line's short label comes from the matching `phase_score_columns` entry, falling back to the tab's `nav_label`. This derivation moves here from `JobsRecommended.tsx` unchanged. For each line, the component renders the label plus `buildPhaseListGradeRow(job, gradesField)`, or an em dash when that returns nothing. It reads the manifest through `useStateUi`.
* `src/ui/frontend/src/pages/JobsRecommended.tsx` (**modified**): a modified page render. The `phaseLines` memo and the inline `recommended-analysis-lines` markup inside the analysis row are replaced by the shared component. The surrounding row, `colSpan`, click-to-open-report, and Analysis toggle stay as they are.
* `src/ui/frontend/src/components/JobDetailModal.tsx` (**modified**): a modified `InfoTab`. The right-hand column gets an **Analysis** section label (the same `entity-section-label` style as State History) with the shared component under it, placed before the State History label. `JobDetail` gains an index signature or cast so the job record can be passed. The block is not gated on state.

## Acceptance criteria

1. **Block present and placed.** Open any job from Skipped or In Review. On the Info tab, the right column shows an **Analysis** label, then the phase lines, then the **State History** label, in that DOM order. **Fail:** block missing, or rendered below State History or in the left column.
2. **Lines follow the manifest.** The block has exactly one line per `report_phase_tabs` entry, in manifest order, labeled JD, DO, GET, LIKE. **Fail:** a missing, extra, or out-of-order line.
3. **Partial analysis shows em dashes.** For a job with `jd_grades` and `do_grades` but no `get_grades` or `like_grades`, the JD and DO lines show circles and the GET and LIKE lines show `—`. For a job with no phase grades, all four lines show `—` and the modal still renders. **Fail:** a crash, a hidden block, or circles on an ungraded phase.
4. **Dots match the list.** For a job present on both Recommended/Review (Analysis toggle on) and in the Job Detail modal, each phase line has the same circle count, `dot-*` color classes, left-to-right order, and `title` text in both places. **Fail:** any mismatch.
5. **No letters, no confidence.** Every grade circle inside the modal's Analysis block has empty text content, and the block contains zero `ConfidenceBullets` elements. **Fail:** a visible letter or a confidence bullet.
6. **One shared component.** `rg -n "PhaseAnalysisLines" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/JobDetailModal.tsx` returns a hit in each file. `rg -n "report_phase_tabs|buildPhaseListGradeRow" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/JobDetailModal.tsx` returns nothing. **Fail:** either host still derives phase lines or calls the row builder itself (a copy instead of the shared component).
7. **Recommended list unchanged.** On Recommended/Review with the Analysis toggle on, each job still has one expanded row with four lines in JD, DO, GET, LIKE order, and clicking it still opens the Job Analysis Report. Toggling off still removes every expanded row. **Fail:** any change in line count, order, circles, toggle, or click behavior compared with `origin/dev`.
8. **No backend change.** `git diff origin/dev...<publish-ref> --stat -- src/ui/api src/core src/data src/utils` is empty. **Fail:** any file listed.
9. **Builds clean; no new lint.** In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that `origin/dev` does not already report. **Fail:** a non-zero build or any new lint problem.

## Boundaries

Single child of AST-1972 — no siblings. Does not change `JobAnalysisReportModal.tsx`, `recommendedJobReport.tsx`, `App.css`, any API/core/data/config file, or the Recommended list's toggle, columns, selection, or click-to-open behavior.

## Notes for planning

Detail payload already carries `{jd,do,get,like}_grades` + `_rubric` (`api_jobs.detail` → `_flatten_grades`); `buildPhaseListGradeRow` reads `job_data` first, then top-level. Only `JobsSkipped` and `JobsInReview` open `JobDetailModal`. AST-1970 (Todo) also modifies `JobsRecommended.tsx` and replaces `JobsInReview` with `JobsProcessing` — keep the list edit to the analysis-row block.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T16:41:20.834Z
[code-rubric] PROCEED (Commit: b7949750) shared phase lines clean

#### betty — 2026-10-04T16:39:05.437Z
`origin/sub/AST-1972/AST-1973-job-modal-info-tab-analysis` @ `b79497507` · modal analysis tests + bible

#### joan — 2026-10-04T16:33:12.744Z
[plan-rubric] PROCEED (Commit: 41eb0553) Shared phase-lines plan clean

#### ada — 2026-10-04T16:31:15.308Z
`origin/sub/AST-1972/AST-1973-job-modal-info-tab-analysis` @ `41eb0553a` · shared component, modal mount

---

# AST-1973 — Job modal Info-tab analysis via shared phase-lines component (Add full analysis to job modal Info tab)

- **Parent:** [AST-1972](https://linear.app/astralcareermatch/issue/AST-1972) — Add full analysis to job modal Info tab
- **Ticket:** [AST-1973](https://linear.app/astralcareermatch/issue/AST-1973)
- **Publish ref:** `sub/AST-1972/AST-1973-job-modal-info-tab-analysis` (origin only)
- **Canon Scope:** `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`
- **Depends on:** none. AST-1970 (Todo, also edits `JobsRecommended.tsx`) has not landed on `origin/dev`; `sync-child.sh` merges it automatically if it lands before build.

The Recommended/Review list draws each job's analysis as letterless grade dots on JD / DO / GET / LIKE
lines (AST-1967 / AST-1968). That block is moved out of `JobsRecommended.tsx` into one shared
`PhaseAnalysisLines` component (moved, not copied), and the Job Detail modal's Info tab renders the same
component in its right column under an **Analysis** label, directly above **State History**. Phases
without grades show an em dash, exactly as the list does. Frontend only: no API, core, data, config, or
`App.css` change.

## Code facts this plan relies on (verified on this ref, tip `e0cb0a540`)

- `src/ui/frontend/src/pages/JobsRecommended.tsx`
  - Line 12: `import { buildPhaseListGradeRow, formatPhaseScore, primaryActionsForState } from "../lib/recommendedJobReport"`.
  - Lines 131–141: comment (2 lines) + `const phaseLines = useMemo(() => { … }, [manifest])` — derives
    `{ gradesField, label }[]` from `manifest.jobs.recommended.report_phase_tabs`, label from the matching
    `phase_score_columns` entry (`grades_field` with `_grades` → `_score`), else `tab.nav_label`.
  - Lines 340–353: `{showAnalysis && (<tr className="clickable recommended-analysis-row" onClick={() => openJobReport(…)}><td colSpan={columnCount}><div className="recommended-analysis-lines">{phaseLines.map(p => (<div key={p.gradesField} className="recommended-analysis-line"><span className="recommended-analysis-line-label">{p.label}</span>{buildPhaseListGradeRow(job, p.gradesField) ?? "\u2014"}</div>))}</div></td></tr>)}`.
  - `phaseLines` and `buildPhaseListGradeRow` are used nowhere else in the file. `useMemo` and `Fragment` are still used elsewhere.
  - `interface Job` has `[key: string]: unknown`, so `Job` is assignable to `Record<string, unknown>`.
- `src/ui/frontend/src/lib/recommendedJobReport.tsx:245` — `export function buildPhaseListGradeRow(job: Record<string, unknown>, gradesField: string): ReactNode`; returns `null` when there are no cells; dots are rendered via `gradeDot(grade, tooltip, true)` (letterless: empty text, `grade-dot-letterless` class, `title` = tooltip). No `ConfidenceBullets`.
- `src/ui/frontend/src/components/JobDetailModal.tsx`
  - `interface JobDetail` (lines 21–35) has **no** index signature, so it is not assignable to `Record<string, unknown>`.
  - `InfoTab` (line 263 on) already calls `useStateUi()`; right column (lines 406–410):
    `<div className="entity-summary-col"><p className="entity-section-label">State History</p><StateTimeline … /></div>`.
- `src/ui/frontend/src/contexts/StateUiContext.tsx` — `useStateUi()` is a plain `useContext`; manifest types
  `report_phase_tabs?: Array<{ …; nav_label: string; grades_field: string }>` and
  `phase_score_columns: Array<{ field: string; label: string }>`.
- `src/ui/api/api_jobs.py:219` — `GET /api/jobs/<id>` runs `_flatten_grades`, lifting `{jd,do,get,like}_grades`
  and `_rubric` to the top level; `buildPhaseListGradeRow` reads `job_data` first, then top level. Detail payload
  therefore feeds the component the same data the list rows do. No API change needed.
- `src/ui/frontend/src/App.css` — `.recommended-analysis-lines` / `-line` / `-line-label` are not scoped to the
  table (only `tr.recommended-analysis-row td` padding is). `.entity-summary-col` is a flex column with `gap: 2px`;
  `.entity-section-label` has `margin: 0 0 8px 0` (no top margin).
- `docs/canon-index.md` is not present on this ref; the placement statute was read directly at
  `canon/statutes/astral/ui/astral.ui.frontend-file-placement.md`. No patterns are cited; the other three ids stay id-only until build.
- Existing tests: `tests/component/frontend/pages/test_JobsRecommended.test.tsx`,
  `tests/component/frontend/components/test_JobDetailModal.test.tsx`. Runner: `npm run test:component` in `src/ui/frontend`.

## Scope gate

Every file below is named in this ticket's `## Scope`, and each change is the kind Scope describes (new
shared component that owns the moved derivation + markup; list page swaps its memo + inline markup for it;
`InfoTab` right column gains the Analysis label + component before State History; `JobDetail` gains an index
signature). No `App.css`, API, core, data, config, `JobAnalysisReportModal.tsx`, or `recommendedJobReport.tsx`
change. Tests and bible are Betty's.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/PhaseAnalysisLines.tsx` | **New.** Default-export component `PhaseAnalysisLines({ job })`: `phaseLines` memo + `recommended-analysis-lines` markup moved verbatim from the list page | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Remove `phaseLines` memo (+ its comment) and inline lines markup; render `<PhaseAnalysisLines job={job} />` in the analysis row; drop `buildPhaseListGradeRow` from the import | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | `JobDetail` gains `[key: string]: unknown`; `InfoTab` right column renders **Analysis** label + `<PhaseAnalysisLines job={job} />` before the State History label | ui |

## Stage 1: Shared component + list swap (move, not copy)

**Done when:** `PhaseAnalysisLines.tsx` exists in `components/`; `rg -n "report_phase_tabs|buildPhaseListGradeRow" src/ui/frontend/src/pages/JobsRecommended.tsx`
returns nothing; Recommended/Review with Analysis on still shows one expanded row per job with JD, DO, GET, LIKE
lines (same dots / em dashes), clicking it opens the Job Analysis Report, and toggling off removes every row.

1. Create `src/ui/frontend/src/components/PhaseAnalysisLines.tsx` with exactly:

   ```tsx
   import { useMemo } from "react"
   import { useStateUi } from "../contexts/StateUiContext"
   import { buildPhaseListGradeRow } from "../lib/recommendedJobReport"

   /** One letterless grade-dot line per manifest phase, em dash when ungraded (AST-1973).
    *  Shared by the Recommended/Review analysis row and the Job Detail modal Info tab. */
   export default function PhaseAnalysisLines({ job }: { job: Record<string, unknown> }) {
     const { manifest } = useStateUi()

     // Line order + grades_field from report_phase_tabs (modal order); short label from the
     // matching phase_score_columns entry (jd_grades → jd_score → "JD"), else the tab nav_label.
     const phaseLines = useMemo(() => {
       const rec = manifest?.jobs.recommended
       return (rec?.report_phase_tabs ?? []).map(tab => ({
         gradesField: tab.grades_field,
         label: rec?.phase_score_columns.find(
           c => c.field === tab.grades_field.replace(/_grades$/, "_score"),
         )?.label ?? tab.nav_label,
       }))
     }, [manifest])

     return (
       <div className="recommended-analysis-lines">
         {phaseLines.map(p => (
           <div key={p.gradesField} className="recommended-analysis-line">
             <span className="recommended-analysis-line-label">{p.label}</span>
             {buildPhaseListGradeRow(job, p.gradesField) ?? "\u2014"}
           </div>
         ))}
       </div>
     )
   }
   ```

   The memo body, comment, class names, and `"\u2014"` fallback are the page's lines 131–141 and 343–350 cut
   verbatim; only the wrapper function is new.
2. In `src/ui/frontend/src/pages/JobsRecommended.tsx`:
   - Line 12: change to `import { formatPhaseScore, primaryActionsForState } from "../lib/recommendedJobReport"`.
   - Add `import PhaseAnalysisLines from "../components/PhaseAnalysisLines"` directly after the
     `import JobAnalysisReportModal from "../components/JobAnalysisReportModal"` line.
   - Delete lines 131–141 (the two-line `// Line order + grades_field …` comment and the whole `const phaseLines = useMemo(…)` block) and the blank line that follows it.
   - In the analysis row, replace the entire `<div className="recommended-analysis-lines"> … </div>` element
     (lines 343–350) with `<PhaseAnalysisLines job={job} />`. Leave the `{showAnalysis && (`, the
     `<tr className="clickable recommended-analysis-row" onClick={() => openJobReport(job.astral_job_id)}>`, and the
     `<td colSpan={columnCount}>` exactly as they are.
   - Touch nothing else in the file (in-scope-only; AST-1970 is queued against this page).
3. In `src/ui/frontend`: `npx tsc -b` and `npm run lint` — both clean (no problem `origin/dev` doesn't already report).

⚠️ **Decision:** The component owns its own `useMemo` over `manifest` rather than taking `phaseLines` as a prop.
Scope says the derivation "moves here … unchanged" and the component "reads the manifest through `useStateUi`";
a prop would leave the derivation in each host and fail AC6. Cost is one memo per rendered row instead of one per
page — trivial array mapping over four tabs, and the memo still only recomputes when the manifest changes.

⚠️ **Decision:** Prop type is `Record<string, unknown>`, the exact parameter type of `buildPhaseListGradeRow`, so
the component adds no type of its own and both hosts pass their job record directly.

⚠️ **Decision:** The file default-exports only the component (no helper exports), so
`react-refresh/only-export-components` stays clean.

## Stage 2: Job Detail modal Info tab

**Done when:** Opening any job from Skipped or In Review, the Info tab's right column shows the **ANALYSIS** label,
then four lines (JD, DO, GET, LIKE) with the same dots as the list (em dash for ungraded phases, all em dashes when
there are no grades), then the **STATE HISTORY** label and timeline. The left column is unchanged.

1. In `src/ui/frontend/src/components/JobDetailModal.tsx`:
   - Add `import PhaseAnalysisLines from "./PhaseAnalysisLines"` directly after the `import AgentStoryTab, { type AgentStoryEntry } from "./AgentStoryTab"` line.
   - In `interface JobDetail`, add `[key: string]: unknown` as the last member (after `legal_next_states?: string[]`),
     the same shape as `JobsRecommended.tsx`'s `Job`.
   - In `InfoTab`, replace the right column:

     ```tsx
             {/* Right column: state history */}
             <div className="entity-summary-col">
               <p className="entity-section-label">State History</p>
     ```

     with:

     ```tsx
             {/* Right column: analysis + state history */}
             <div className="entity-summary-col">
               <p className="entity-section-label">Analysis</p>
               <div style={{ marginBottom: 16 }}>
                 <PhaseAnalysisLines job={job} />
               </div>
               <p className="entity-section-label">State History</p>
     ```

     The `<StateTimeline … />` line and closing tags stay unchanged. No state check, no `manifest` check, no
     click handler around the block.
2. In `src/ui/frontend`: `npx tsc -b`, `npm run lint`, `npm run build` — all exit 0 / no new lint problem.
3. Run existing tests (read-only; do not edit): in `src/ui/frontend`,
   `npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx`.
   Record pass/fail in the issue doc `## Review`; any failure that also fails on `origin/dev` is pre-existing and
   noted, not fixed. A new failure caused by this change stops the stage (comment on parent per Execution contract).

⚠️ **Decision:** `JobDetail` gets an index signature rather than a cast at the call site. It matches the list's
`Job` interface, avoids a `job as unknown as Record<string, unknown>` double cast, and every existing field is
already assignable to `unknown`. Scope allows either.

⚠️ **Decision:** A `<div style={{ marginBottom: 16 }}>` wrapper separates the lines from the State History label.
Without it the label sits 2px under the last line (`.entity-summary-col` gap 2px; `.entity-section-label` has no
top margin). `App.css` is out of scope, and `InfoTab` already uses inline spacing (`marginTop: 20` on the Skip
block). 16px is twice the label's own 8px bottom margin, enough to read as a new section.

⚠️ **Decision:** Block is not gated on state or on the manifest being loaded (Scope: "not gated on state";
`astral.layers.ui-config-driven-business-logic` forbids a React-side state rule). Before the manifest loads the
component renders an empty lines container under the label, the same thing the list does in that window.

## Acceptance criteria mapping

| AC | Covered by |
|----|------------|
| 1 Block present and placed | Stage 2 step 1 (Analysis label → lines → State History label, right column) |
| 2 Lines follow the manifest | Stage 1 step 1 (`report_phase_tabs` order, `phase_score_columns` labels) |
| 3 Partial analysis em dashes | Stage 1 step 1 (`?? "\u2014"`); Stage 2 (no gate; detail payload carries grades) |
| 4 Dots match the list | Stage 1 (one component, same `buildPhaseListGradeRow` call, same data via `_flatten_grades`) |
| 5 No letters, no confidence | Stage 1 (letterless `gradeDot`; no `ConfidenceBullets` in the component) |
| 6 One shared component | Stage 1 step 2 + Stage 2 step 1 (import in both hosts; derivation and row-builder only in the component) |
| 7 Recommended list unchanged | Stage 1 step 2 (row, `colSpan`, click, toggle untouched; verbatim markup) |
| 8 No backend change | Files Changed has only `src/ui/frontend/src/**` rows |
| 9 Builds clean; no new lint | Stage 1 step 3, Stage 2 step 2 |

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1973
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref tip:** 41eb0553aa899048c00de43b74bba90735ba5679

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.ui.frontend-file-placement | A | | |
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.standards.dry-and-focused-functions | A | | |
| astral.standards.in-scope-only | A | | |

## Traceability

AC1–9 → Stage 2 (placement), Stage 1 (manifest lines, dashes, dots, shared component, list parity), Files Changed (frontend-only), Stage 1–2 build/lint gates (AC9); no unmapped AC or orphan stage.

## Findings

### acceptable

- **Location:** `## Code facts this plan relies on` — tip `e0cb0a540`
- **Finding:** Publish ref tip on origin is `41eb0553a`; Ada’s handoff comment matches the latter. One stale SHA in code facts is cosmetic.
- **Recommendation:** Optional one-line refresh on next plan edit; not blocking build.

### R6 (definition fidelity / adversarial)

- Plan matches parent Purpose, functional scope 1–4, component/technical scope, and all nine ACs.
- Files Changed and stages stay inside ticket `## Scope`; explicit scope gate documents AST-1970 collision boundary on `JobsRecommended.tsx`.
- DRY: move into `PhaseAnalysisLines`, two hosts, no modal copy of derivation.
- No sibling scope; monolith child is intentional per parent partition check.
- `## Estimate` confirm line present; no `!!-NONE` self-assessment gap.

context_tokens≈42000

## Review

- **Code commits on `origin/sub/AST-1972/AST-1973-job-modal-info-tab-analysis`:** `355e18687` (Stage 1), `49d5b789d` (Stage 2).
- **Diff:** 3 frontend files, as planned in Files Changed; executed literally, no deviations.
  `git diff origin/dev...HEAD --stat -- src/ui/api src/core src/data src/utils` empty (AC8).
  AC6: `rg -n "report_phase_tabs|buildPhaseListGradeRow"` on both hosts returns nothing; `PhaseAnalysisLines` hits in both.
- **Compile / lint / build:** `npx tsc -b --noEmit` clean; `npm run build` exit 0; `npm run lint` reports the same
  31 problems as the pre-change tree (none in the three touched files) — no new lint (AC9).
- **Existing tests (read-only run):** `test_JobsRecommended` 22/22 pass. `test_JobDetailModal` 14/15 — the one failure,
  "AST-1695 read-only: null listing_href → no Link <a>", fails identically with Stage 2 stashed (pre-existing, also noted on AST-1865).
- **For Betty (qa-child):** AC1–AC5 modal coverage is new work in `test_JobDetailModal.test.tsx`. The Analysis block is the
  `.recommended-analysis-lines` element between the `Analysis` and `State History` `.entity-section-label`s in the Info tab;
  `InfoTab` reads `report_phase_tabs` / `phase_score_columns` from the StateUi manifest, so the test needs a manifest provider.
- **Git note:** parent ref is `ftr/AST-1972-job-modal-info-analysis` (registry), not `ftr/AST-1972`; `sync-child --ftr AST-1972`
  skipped it, but it sits at `origin/dev` tip `e0cb0a540`, so nothing was missed. `validate-sub-log.sh --stage=build` with the full ref → ok.

## Radia review

[code-rubric]
**Ticket:** AST-1973
**Publish ref:** `b794975073c04a857743f12870aaaf76dfc00648` (`origin/sub/AST-1972/AST-1973-job-modal-info-tab-analysis`)
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.ui.frontend-file-placement | A | | |
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.standards.dry-and-focused-functions | A | | |
| astral.standards.in-scope-only | A | | |

## Column diff vs plan stage

(aligned) — Joan graded all four **A** at plan; code diff matches those promises (shared `PhaseAnalysisLines` in `components/`, manifest-driven lines, move-not-copy, three scoped frontend files only).

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `canon/canon_clerk.py expand` vs frozen statute ids
- **Finding:** `expand` only serves `directives/active/`; these four ids resolve from `canon/statutes/**` at corpus tip (same SHA Joan used). Verdict is reproducible; optional downstream clerk roster gap only.
- **Location:** diff includes `tests/component/frontend/components/test_JobDetailModal.test.tsx` + `docs/test-bible/frontend/{components,pages}.md`
- **Finding:** Expected **Tests Passed** carry from Betty (`qa-child` / `test-child`), not sibling product scope; AC1–AC5 modal coverage aligns with plan handoff.

## What's solid

- `PhaseAnalysisLines.tsx` matches the plan snippet verbatim (memo, classes, em-dash fallback, `buildPhaseListGradeRow`).
- AC6 hygiene: hosts import the shared component only; no `report_phase_tabs` / `buildPhaseListGradeRow` in `JobsRecommended.tsx` or `JobDetailModal.tsx`.
- Info tab: **Analysis** → lines → **State History** in the right column; `JobDetail` index signature; block not state-gated (manifest-driven display only).
- AC8: three-dot diff empty under `src/ui/api`, `src/core`, `src/data`, `src/utils`.

## Recommended actions (for Chuckles / downstream — not executed here)

- Append this artifact to `docs/features/interface/ast-1973-job-modal-info-tab-analysis.md`, commit `docs(AST-1973): Radia review — clean`, push publish ref, post slim upshot `--as radia`, move **Review Posted**; datt **PROCEED** → **User Testing** (no `resolve-child` canon work).

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] PROCEED (Commit: b794975073c04a857743f12870aaaf76dfc00648) shared phase lines clean
```

context_tokens≈28000

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/33022c9e6a1608e804235716dc9cbd1b/84abd99b-cb58-49de-af9c-c6dc660f406e/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/dea146a0-9b7f-496c-a041-d3a651fd10d8/store.db` |
| Radia | review | `/home/susan/.cursor/chats/33022c9e6a1608e804235716dc9cbd1b/7a1eb455-42cb-4b6a-9cb9-1c53ed98970f/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1972 (parent) | ftr/AST-1972-job-modal-info-analysis |
| AST-1973 | sub/AST-1972/AST-1973-job-modal-info-tab-analysis |

**Epic worktree:** `astral-AST-1972/` — one active sub checked out at a time.
