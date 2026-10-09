<!-- linear-archive: AST-1874 archived 2026-10-08 -->

## Linear archive (AST-1874)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1874/modal-wiring-analysis-default-list-score-in-headers-skip-action  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1862 — Recommended Job Modal Changes  
**Blocked by / blocks / related:** parent: AST-1862

### Description

## What this implements

Wires everything into the report modal. The default tab comes from config (Analysis). Analysis headers show the list score through one shared formatter that the Recommended list also uses. The skip handler posts, refreshes, and closes, and is shown only when #1's flag is true. The header gets the job-link text and href that #2's props expect. Comes after #1 (flag and template) and #2 (header props).

## Citations

`astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`.

## Scope

* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: modified component. The initial and per-job reset active tab come from the first manifest top tab instead of the literal `"summary"`. The Analysis section header labels pass the phase's list score (the `<prefix>_score` field matching each phase's `grades_field`, already flattened onto the detail GET) into the title formatter. There is a new skip handler: it calls the existing `postSkipJob`, then `onRefresh?.()` and `onClose()` on success, and shows the error toast on failure. It is wired to the header only when the detail response's skip-legal flag is true. The header gets the job-link display text (`listing_href` when http(s), else raw `job_link`) plus the http href.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx`: new exported function, the list's phase-score formatter (number to one decimal, else em dash), moved here from `JobsRecommended.tsx`, not copied. Modified function: the phase header title formatter takes an optional score and fills the new placeholder. Its no-template fallback string gets the same score segment. When the score is absent, the ` - {score}` segment is dropped, not rendered as an em dash.
* `src/ui/frontend/src/pages/JobsRecommended.tsx`: modified. The page-local phase-score formatter is removed and the shared one imported. Column output is unchanged.

## Acceptance criteria

1. **Analysis is first and default.** `JOBS_RECOMMENDED_REPORT_TOP_TABS` in `src/utils/config.py` lists `analysis` at index 0 and `summary` at index 1. In `test_JobAnalysisReportModal.test.tsx`, opening the modal with the manifest renders the Analysis pane (phase sections visible) and the tab bar order is Analysis, Summary, Artifacts, Discussion. Switching to a different `jobId` after selecting Summary returns to Analysis. Fail = Summary pane shown on open, or wrong order.
2. **No hard-coded default tab.** `grep -n 'useState("summary")\|setActiveTopTab("summary")' src/ui/frontend/src/components/JobAnalysisReportModal.tsx` returns nothing. Fail = either literal still present (a reorder in React instead of config).
3. **Score in Analysis header.** With a job whose `jd_score` is `3.66` and `jd_score_breakdown` is `{earned: 42, possible: 50, max: 60}`, the JD Analysis section header reads exactly `JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)`. With `jd_score` absent, it reads `JD Analysis - score: 42 out of 50 possible (60 max total)`. Fail = score missing, misplaced, or not one decimal, or an empty `-` segment / em dash rendered when the score is absent.
4. **One score formatter.** `grep -rn "toFixed(1)" src/ui/frontend/src/pages/JobsRecommended.tsx` returns nothing, and the Recommended list JD/DO/GET/LIKE cells still render `3.7` / `—` exactly as before (existing page tests pass without behavioral edits). Fail = the formatter exists in both files, or list output changed.
5. **Skip button visibility.** In `test_RecommendedJobReportHeader.test.tsx` / `test_JobAnalysisReportModal.test.tsx`, **Skip this Job** is the last button in the header button row when the detail flag is `true`, and absent when `false`. `grep -n "CANDIDATE_REVIEW\|REVIEW_LIKE" src/ui/frontend/src/components/JobAnalysisReportModal.tsx src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` returns nothing. Fail = the button is shown for a non-skippable job, is not last, or the modal carries its own state list.
6. **Skip acts and closes.** Clicking **Skip this Job** sends `POST /api/jobs/<id>/skip`. On `200`, `onRefresh` is called once and `onClose` is called once. On `409`, the error toast shows the server message and `onClose` is not called. Fail = no POST, modal stays open on success, or closes on failure.

## Boundaries

Does not change header markup/CSS or labels (#2) or config/API/tracker (#1). No change to `Modal.tsx`, `CandidateJobRowActions.tsx`, `JobDetailModal.tsx`, `JobsJobDetail.tsx`.

## Notes for planning

After #1 (skip flag + template) and #2 (header props). Citations above are this child's Canon Scope subset of the parent's Architectural definition.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1862-recommended-job-modal-changes`, child `sub/AST-1862/<child-id>-modal-wiring-analysis-default-score-skip`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-29T20:56:21.749Z
[code-rubric] PROCEED (Commit: 8787e464) Modal wiring, shared formatter

#### betty — 2026-09-29T20:52:54.298Z
`origin/sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip` @ `8787e464f` · manifest in components bible

#### joan — 2026-09-29T20:37:16.441Z
[plan-rubric] PROCEED (Commit: 777031de) Modal wiring plan sound

#### ada — 2026-09-29T20:35:12.674Z
`origin/sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip` @ `777031de2` · plan ready, two stages

---

# AST-1874 — Modal wiring: Analysis default, list score in headers, Skip action (Recommended Job Modal Changes)

- **Linear:** [AST-1874](https://linear.app/astralcareermatch/issue/AST-1874) · parent [AST-1862](https://linear.app/astralcareermatch/issue/AST-1862) — Recommended Job Modal Changes
- **Publish ref:** `sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip` (origin only)
- **Assignee:** Ada
- **Canon Scope:** `astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`

This ticket wires the sibling work into `JobAnalysisReportModal`. AST-1872 (#1) already put Analysis first in `JOBS_RECOMMENDED_REPORT_TOP_TABS`, added ` - {score}` to `PHASE_SCORE_HEADER_TITLE_TEMPLATE`, and returns `can_skip` on `GET /api/jobs/<id>`. AST-1873 (#2) already gave `RecommendedJobReportHeader` the `jobLinkText`, `onSkip`, and `skipBusy` props. Both are merged into this branch through `ftr/AST-1862`. This ticket does four things. The modal's default and per-job reset tab come from the first manifest tab instead of the literal `"summary"`. Analysis section headers show the phase's list score through one shared formatter, which the Recommended list also uses. The modal gets a skip handler, and it's shown only when `can_skip` is true. The header gets the job-link display text.

## Scope check

Every file below is named in this ticket's `## Scope`, and every change is the kind Scope describes:

- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: **modified component**. Default/reset tab, score into the header title formatter, skip handler, `jobLinkText`, and the `onSkip`/`skipBusy` wiring.
- `src/ui/frontend/src/lib/recommendedJobReport.tsx`: **new exported function** `formatPhaseScore`, moved from the page. **Modified function** `formatPhaseSectionScoreTitle` takes an optional score.
- `src/ui/frontend/src/pages/JobsRecommended.tsx`: **modified**. The local `formatPhaseScore` is removed and the shared one is imported.

No scope gap. `RecommendedJobReportHeader.tsx`, `App.css`, `config.py`, `api_jobs.py`, `Modal.tsx`, `CandidateJobRowActions.tsx`, `JobDetailModal.tsx`, and `JobsJobDetail.tsx` are not touched.

## Canon Scope (id-only at plan)

All three ids are statutes under `canon/statutes/astral/{config,layers,standards}/`, and none is a pattern. They stay id-only until build-child §8 expands them. How this plan honors them:

- `config-source-of-truth` / `ui-config-driven-business-logic`: the default tab is `topTabs[0]` (from manifest `report_top_tabs`). No tab name is chosen in React. Skip visibility is the server's `can_skip`. The modal carries no state list.
- `dry-and-focused-functions`: the phase-score formatter exists once, in `lib/recommendedJobReport.tsx`. The list cells and the Analysis header both call it.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Add exported `formatPhaseScore` (moved from the page). `formatPhaseSectionScoreTitle` gains an optional `score` param that fills `{score}` or drops ` - {score}`. | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Delete local `formatPhaseScore` and import it from `../lib/recommendedJobReport` | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Default/reset tab from the first manifest tab, pass `<prefix>_score` into the title formatter, `handleSkip` + `skipBusy`, `can_skip` on `JobDetail`, header `jobLinkText` / `onSkip` / `skipBusy` | ui |

No other files.

## Stage 1: Shared score formatter and header title score

**Done when:** `formatPhaseScore` is exported from `lib/recommendedJobReport.tsx`, and `JobsRecommended.tsx` imports it with no local copy. `formatPhaseSectionScoreTitle("JD Analysis", {earned: 42, possible: 50, max: 60}, "{phase_label} - {score} - score: {earned} out of {possible} possible ({max} max total)", 3.66)` returns `JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)`. The same call with the score omitted returns `JD Analysis - score: 42 out of 50 possible (60 max total)`. `npm run build` passes (the modal's existing 3-arg call still compiles).

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, directly **above** the `/** Analysis section header title with score chrome (AST-1348). */` comment, add:

   ```tsx
   /** Recommended list phase score (JD/DO/GET/LIKE): one decimal, else em dash (AST-522, AST-1874). */
   export function formatPhaseScore(value: unknown): string {
     if (typeof value === "number" && Number.isFinite(value)) return value.toFixed(1)
     return "\u2014"
   }
   ```

   The body is byte-identical to the page's current function (`JobsRecommended.tsx` lines 29–32), so list output can't change.

2. In the same file, replace the whole `formatPhaseSectionScoreTitle` function, including its doc comment, with:

   ```tsx
   /** Analysis section header title with score chrome (AST-1348); list score fills {score} (AST-1874). */
   export function formatPhaseSectionScoreTitle(
     phaseLabel: string,
     breakdown: { earned: number; possible: number; max: number },
     template: string,
     score?: unknown,
   ): string {
     const e = String(Math.round(breakdown.earned))
     const p = String(Math.round(breakdown.possible))
     const m = String(Math.round(breakdown.max))
     // No list score → drop the whole " - {score}" segment; never render an em dash here.
     const hasScore = typeof score === "number" && Number.isFinite(score)
     const s = hasScore ? formatPhaseScore(score) : ""
     const tpl = template.trim()
     if (!tpl) {
       return `${phaseLabel}${hasScore ? ` - ${s}` : ""} - score: ${e} out of ${p} possible (${m} max total)`
     }
     return (hasScore ? tpl : tpl.replaceAll(" - {score}", ""))
       .replaceAll("{phase_label}", phaseLabel)
       .replaceAll("{score}", s)
       .replaceAll("{earned}", e)
       .replaceAll("{possible}", p)
       .replaceAll("{max}", m)
   }
   ```

   ⚠️ **Decision (`score?: unknown`):** The caller passes the raw `job[<prefix>_score]` value, and the formatter decides presence with the same finite-number test `formatPhaseScore` uses. The alternative was a `number | null` param with a narrowing cast in the modal. That puts the same test in two places, so it was rejected.

   ⚠️ **Decision (drop rule):** When the score is absent, the literal ` - {score}` is removed first, then the trailing `.replaceAll("{score}", s)` blanks any stray `{score}`. With the config template from AST-1872, that gives exactly `{phase_label} - score: …` (AC 3). The ` - {score}` unit comes from AST-1872's plan decision (the template carries the separator, and the UI drops it as one unit).

3. In `src/ui/frontend/src/pages/JobsRecommended.tsx`:
   - Delete the `function formatPhaseScore(value: unknown): string { … }` block (lines 29–32) and the blank line after it.
   - Add `import { formatPhaseScore } from "../lib/recommendedJobReport"` directly after the existing `import api from "../lib/api"` line.
   - Leave the call site `{formatPhaseScore(job[col.field])}` (line ~217) unchanged.

4. Validate in `src/ui/frontend/`. Run `npm ci` first only if `node_modules/` is absent, and never commit it. Then run `npm run build` and `npm run lint`. The build must pass. Lint must add no new problems on the three touched files: compare `npx eslint src/lib/recommendedJobReport.tsx src/pages/JobsRecommended.tsx` before and after. AST-1873 recorded 32 pre-existing repo-wide problems.
5. Self-check from the repo root. This must return nothing: `grep -rn "toFixed(1)" src/ui/frontend/src/pages/JobsRecommended.tsx`.
6. Commit `code(AST-1874): shared phase-score formatter; header title takes list score`, then publish with `git push origin HEAD:sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip`.

## Stage 2: Modal wiring — default tab, header score, Skip, job-link text

**Done when:** the modal opens on Analysis, and it returns to Analysis when `jobId` changes after Summary was selected. The JD Analysis header reads `JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)` for `jd_score: 3.66`. **Skip this Job** shows only when `can_skip` is `true`. A successful skip calls `onRefresh` once and `onClose` once, and a failed skip shows the error toast and keeps the modal open. The job-link line shows `listing_href` (linked) when it is http(s), else the raw `job_link` (plain). The AC 2 and AC 5 greps return nothing, and `npm run build` passes.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, add `import { postSkipJob } from "../lib/candidateJobActions"` directly after the existing `import api from "../lib/api"` line.
2. In `interface JobDetail`, add `can_skip?: boolean` directly after `related_meteorite?: RelatedMeteorite | null`, with the trailing comment `// AST-1872: server-resolved Skip legality`.
3. Default tab: replace `const [activeTopTab, setActiveTopTab] = useState("summary")` with:

   ```tsx
   // Empty until the manifest tabs resolve — the effect below picks topTabs[0] (config order, AST-1874).
   const [activeTopTab, setActiveTopTab] = useState("")
   ```

4. Directly after `const [snapshotCopying, setSnapshotCopying] = useState(false)`, add `const [skipBusy, setSkipBusy] = useState(false)`.
5. Per-job reset: in the `// Reset top tab when opening a different job.` effect, replace `setActiveTopTab("summary")` with `setActiveTopTab("")`. Change the comment to `// Reset top tab when opening a different job; the fallback effect re-picks the first manifest tab.`
6. Leave the existing fallback effect (`if (!topTabs.some(t => t.key === activeTopTab)) setActiveTopTab(topTabs[0].key)`) **unchanged**. It is what turns `""` into the first manifest tab, both on open and after a reset.

   ⚠️ **Decision (default tab mechanism), three options considered:**
   (a) **Chosen:** `""` sentinel plus the existing fallback effect. There are no new effects, no new dependencies, and no tab literal. `topTabs[0]` is manifest order, filtered only to hide Meteorite (always last), so it is `analysis`.
   (b) Rejected: `useState(manifest…report_top_tabs[0].tab_id)`. The manifest can arrive after mount, so it still needs the fallback effect, and the per-job reset would need `topTabs` in an effect keyed on `jobId`, which trips `react-hooks/exhaustive-deps`.
   (c) Rejected: resetting inside `load()`. It mixes tab UI state into data fetching.

7. Header score: in `analysisSections`, replace the line `nav_label = formatPhaseSectionScoreTitle(base, breakdown, template)` with:

   ```tsx
          // List score is flattened top-level on the detail GET as <prefix>_score (jd_grades → jd_score).
          const score = jobRec[p.grades_field.replace(/_grades$/, "_score")]
          nav_label = formatPhaseSectionScoreTitle(base, breakdown, template, score)
   ```

   This line sits inside `if (breakdown)`. `jobScoreBreakdownForGradesField` returns `null` unless `grades_field` ends in `_grades`, so the replace always yields a `<prefix>_score` key. A phase with no breakdown keeps its plain title, which is unchanged.

   ⚠️ **Decision (no job_data fallback for score):** Read top-level only. `_flatten_grades` in `api_jobs.py` already lifts `jd_score`/`do_score`/`get_score`/`like_score` onto the detail response, and Scope says "already flattened onto the detail GET". A lib helper that mirrors `jobScoreBreakdownForGradesField` was rejected, because Scope names no new lib function beyond `formatPhaseScore`.

8. Skip handler: directly **after** `handleCopyDetailLink()` and **before** `handleCopyApplicationEmail()`, add:

   ```tsx
   // AST-1874: server already gated visibility via can_skip; 409 etc. surface as a toast, modal stays open.
   async function handleSkip() {
     if (!jobId || skipBusy) return
     setSkipBusy(true)
     try {
       await postSkipJob(jobId)
       onRefresh?.()
       onClose()
     } catch (e) {
       setToast({ text: e instanceof Error ? e.message : "Skip failed", variant: "error" })
     } finally {
       setSkipBusy(false)
     }
   }
   ```

   `postSkipJob` throws `Error(body.error || "Skip failed")` on any non-2xx, so a 409 toast shows the server message (AC 6).

9. Header props: in the `<RecommendedJobReportHeader … />` element:
   - Keep `jobLink={httpListingHref(job.listing_href)}` as it is, since that is the http href.
   - Directly after it, add `jobLinkText={httpListingHref(job.listing_href) ?? job.job_link ?? null}`.
   - Directly after `snapshotCopying={snapshotCopying}`, add:

     ```tsx
                 onSkip={job.can_skip ? () => { void handleSkip() } : undefined}
                 skipBusy={skipBusy}
     ```

   The header renders **Skip this Job** last in the button row only when `onSkip` is defined (AST-1873).

10. Validate in `src/ui/frontend/` with `npm run build` and `npm run lint`. The build must pass, and there must be no new eslint problems on `src/components/JobAnalysisReportModal.tsx` (compare before and after, as in Stage 1 step 4).
11. Self-check greps from the repo root. All must return nothing:
    - `grep -n 'useState("summary")\|setActiveTopTab("summary")' src/ui/frontend/src/components/JobAnalysisReportModal.tsx`
    - `grep -n "CANDIDATE_REVIEW\|REVIEW_LIKE" src/ui/frontend/src/components/JobAnalysisReportModal.tsx src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`
    - `git diff origin/ftr/AST-1862-recommended-job-modal-changes -- src/ui/frontend/src/components/RecommendedJobReportHeader.tsx src/ui/frontend/src/App.css src/utils/config.py src/ui/api/api_jobs.py src/ui/frontend/src/components/Modal.tsx`
12. Commit `code(AST-1874): modal — Analysis default from config, list score in headers, Skip action`, then publish with `git push origin HEAD:sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip`.

## Test fallout (Betty — qa-child; engineer does not touch `tests/`)

- `test_JobAnalysisReportModal.test.tsx`: any assert that expects the Summary pane on open, or after a `jobId` switch, now fails by design (AC 1). New coverage is needed for Analysis default and reset, the header score (with and without `jd_score`), Skip visible or absent by `can_skip`, POST plus `onRefresh`/`onClose` on 200, and a toast with no close on 409 (AC 1, 3, 5, 6). Sibling reviews deferred the modal-side AC 1, AC 5, and AC 6 proof to this ticket.
- `tests/component/frontend/lib/` for `recommendedJobReport`: `formatPhaseScore` moved here, and `formatPhaseSectionScoreTitle` has the new `score` param and drop rule.
- `JobsRecommended` page tests must pass unedited (AC 4).

## Execution contract

This plan is binding. Execute the steps in order, and the stages in order. Do not add files, imports beyond Stage 2 step 1 and Stage 1 step 3, helpers, or props. If a referenced line, name, or signature has drifted from what's written here, stop and comment on parent AST-1862. Examples: the header lacks `jobLinkText`/`onSkip`/`skipBusy`, `can_skip` is absent from the detail route, or the template lacks ` - {score}`.

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage is one commit on the epic worktree, published to `origin/sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip` before the next stage starts.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1874
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip` @ `777031de2a5349272c44220ffc399959a71e75d3`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.config.config-source-of-truth | A | | |
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.standards.dry-and-focused-functions | A | | |

## Traceability

AC1→Stage2 (manifest-first tab + modal tests; config order via #1 on `ftr`); AC2→Stage2 steps 3–6; AC3→Stages1–2; AC4→Stage1; AC5→Stage2 step 9; AC6→Stage2 step 8.

### Findings

- **discuss** — **Prerequisites** · Finding: Plan binds on AST-1872/1873 merged into `ftr/AST-1862` before Stage 2 (execution contract 🛑). · Recommendation: Chuckles confirms `ftr` rollup before Ada builds; no plan change.

- **discuss** — **AC1 vs Scope** · Finding: AC1 cites `config.py` tab list; this child touches only modal/lib/page. · Recommendation: Split proof: #1 config tests + this ticket’s modal AC1 asserts.

- **acceptable** — **Stages 1–2** · Finding: Scope-limited three-file footprint; `can_skip`/`topTabs[0]`/`formatPhaseScore` move match parent definition and frozen canon list. · Recommendation: None.

context_tokens≈36000

[plan-rubric] PROCEED (Commit: 777031de) Modal wiring plan sound

## Review

- **Code commits on `origin/sub/AST-1862/AST-1874-modal-wiring-analysis-default-score-skip`:** `4af70ecd9` (Stage 1, shared formatter and header title score) and `c75622b2f` (Stage 2, modal wiring).
- **Diff:** 3 files, all listed in Files Changed, and there are no deviations from the plan. `RecommendedJobReportHeader.tsx`, `App.css`, `config.py`, `api_jobs.py`, and `Modal.tsx` show no diff against `origin/ftr/AST-1862-recommended-job-modal-changes`.
- **Checks:** `tsc -b --noEmit` and `npm run build` are clean. eslint on the three touched files adds no problems: the only remaining items are the pre-existing `react-hooks/exhaustive-deps` warning in the modal (the `handlePrintResume` useCallback) and the `react-hooks/set-state-in-effect` error in `JobsRecommended.tsx` (the `actions.error` toast effect). All Stage 1 and Stage 2 self-check greps return nothing. A scratch esbuild run of `formatPhaseSectionScoreTitle` with the config template returned `JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)` with `score=3.66` and `JD Analysis - score: 42 out of 50 possible (60 max total)` with no score.
- **Existing tests (read-only run, for Betty's `qa-child`):** related Vitest files show 90 passed and 5 failed. Three of the failures also fail on the tree before Stage 2, the same pre-existing trio AST-1873 recorded: AST-1546 Print Resume success, AST-1350 Print Resume unsupported toast, and AST-1704 breadcrumb. Two are expected revisions for AC 1, because they assume Summary opens by default: the AST-948 "Summary default" test and the AST-949 "Summary empty-state" test. `test_JobsRecommended` and `test_recommendedJobReport` pass unedited (AC 4).
- **Canon (§8):** `config-source-of-truth` and `ui-config-driven-business-logic` hold. The default tab is manifest `topTabs[0]`, Skip visibility is the server's `can_skip`, and there is no state list in React. `dry-and-focused-functions` holds, with one formatter shared by the list and the header. Advisory: the plan's Stage 2 step 9 calls `httpListingHref(job.listing_href)` twice in the header props, once each for `jobLink` and `jobLinkText`. It's trivial and was kept as the plan wrote it.
- **Sync note:** `sync-child.sh --ftr` wants the bare segment (`AST-1862-recommended-job-modal-changes`). Both spawn forms skipped the ftr merge: `AST-1862` has no match, and `ftr/…` becomes `ftr/ftr/…`. Each pass was re-run with the bare segment.

## Radia review

[code-rubric]
**Ticket:** AST-1874
**Publish ref:** 8787e464fd38bf513e5b7e6f3d162ebc8f8667f1
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51 · `canon_clerk.py expand` rejects all three frozen ids (statutes under `canon/statutes/` scored directly; clerk migration gap unchanged)
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.config.config-source-of-truth | A | | |
| astral.layers.ui-config-driven-business-logic | A | | |
| astral.standards.dry-and-focused-functions | A | | |

## Column diff vs plan stage

(aligned) — Joan APPROVED all three at A; `4af70ecd9` / `c75622b2f` match plan Stages 1–2.

## Frame diff

- [ ] **Acceptance criteria 1 (config slice):** Tab order at index 0/1 remains proven on AST-1872 (`config.py` + component config tests on `ftr`); this ticket’s AC1 proof is modal + `stateUiManifestFixture` (`analysis` first) and the AST-1874 block in `test_JobAnalysisReportModal.test.tsx`.

## Findings

### fix-now

(none)

### discuss

(none requiring product call) — Prerequisites (#1/#2 on `ftr`) are satisfied on this publish ref via sync/resolve history; Betty landed modal AC1/3/5/6 coverage in `81dd0c445`.

### advisory

- **sibling product carry (expected):** Tip-vs-dev and three-dot diffs include AST-1872/1873 work (`tracker.py`, `api_jobs.py`, `config.py`, `RecommendedJobReportHeader.tsx`, `App.css`) stacked ahead of Ada’s three files. Audit AST-1874 product with `4af70ecd9^..c75622b2f` (3 files only) or the ftr delta on those three paths (+43/−12 vs `origin/ftr/AST-1862-recommended-job-modal-changes`).

- **sibling test carry:** `8787e464 merge-tests(AST-1874)` / `81dd0c445` — modal, lib, fixture, bible; branch history also carries AST-1877 test commits (`test_llm_compat.py`, `test_cost_calculator.py`, extra `test_config.py` hunks) unrelated to AST-1874 scope.

- **Duplicate `httpListingHref` in header props:** `jobLink` and `jobLinkText` each call `httpListingHref(job.listing_href)` — trivial duplication, plan-explicit; optional micro-refactor in a later pass, not blocking.

- **Pane routing literals:** Modal still compares `activeTopTab === "summary"` / `"analysis"` for pane bodies; AC2 forbids hard-coded **default/reset** (`useState("summary")` / `setActiveTopTab("summary")`), not tab-id routing. Greps clean.

## What's solid

- **Stage 1:** `formatPhaseScore` exported from `recommendedJobReport.tsx`; page local copy removed; `formatPhaseSectionScoreTitle` optional `score` with ` - {score}` drop rule matches AST-1872 template; `JobsRecommended.tsx` has no `toFixed(1)`.
- **Stage 2:** Default/reset use `""` + existing fallback to `topTabs[0]` (manifest order); `can_skip` on `JobDetail`; score from flattened `<prefix>_score`; `handleSkip` → `postSkipJob` → refresh/close on success, error toast on failure (409 message via thrown `Error`); header wired with `jobLinkText`, conditional `onSkip`/`skipBusy`.
- **Boundaries:** `Modal.tsx`, `CandidateJobRowActions.tsx`, `JobDetailModal.tsx`, `JobsJobDetail.tsx` unchanged tip-vs-dev; no `CANDIDATE_REVIEW` / `REVIEW_LIKE` in modal or header.
- **Tests:** `test_recommendedJobReport` covers AC3/4; modal AST-1874 block covers Analysis default, jobId reset, `3.7` header string, `can_skip` visibility, POST/refresh/close on 200, toast + stay open on 409; fixture manifest lists `analysis` before `summary`.
- **Integration:** `origin/dev` vs sub tip shows **no** `monitor.py` drift (AST-1877 hotfix on branch history); backend delta vs dev is AST-1872-only (`can_skip` + config tabs/template).

## Recommended actions (downstream — not for Radia)

1. Chuckles: append artifact to `docs/features/interface/ast-1874-modal-wiring-analysis-default-score-skip.md`, commit `docs(AST-1874): Radia review — clean`, post slim upshot, move to **Review Posted**.
2. `merge-child` / `prep-uat`: roll sub into `ftr/AST-1862` with siblings; three-dot stat is noisy — gate rollup on scoped file deltas and green manifest, not raw three-dot file count alone.
3. Optional: tick frame-diff AC1 split when resolving to User Testing.

```
[code-rubric] PROCEED (Commit: 8787e464) Modal wiring, shared formatter
```

context_tokens≈52000
