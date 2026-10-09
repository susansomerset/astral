# AST-2084 — Wire base page, job edit modal, thumbnails; retire resume mode in ArtifactEditor (Resume Edit Overhaul)

- **Parent:** [AST-2046 Resume Edit Overhaul](https://linear.app/astralcareermatch/issue/AST-2046)
- **Ticket:** [AST-2084](https://linear.app/astralcareermatch/issue/AST-2084)
- **Publish ref:** `sub/AST-2046/AST-2084-wire-resume-surfaces` (origin only)
- **Depends on:** #1 [AST-2081](https://linear.app/astralcareermatch/issue/AST-2081) (job structure routes, `preview_thumbnail` tab flag), #2 [AST-2082](https://linear.app/astralcareermatch/issue/AST-2082) (`SplitPanePage`, `PrintPreview`, `printHtml.ts`, `Modal size="fullscreen"`), #3 [AST-2083](https://linear.app/astralcareermatch/issue/AST-2083) (`ResumeContentEditor`). All three are on `ftr/AST-2046-resume-edit-overhaul` and merged into this branch. None of their files are touched here.
- **Canon Scope:** `patt.artifact.ui-consistency` (as amended — parent Decision 7).

This ticket mounts the new resume pieces and removes the old resume path. Base Resume Content becomes a split pane: `ResumeContentEditor` on the left and the live `PrintPreview` on the right, and the preview refreshes after each save. The page loses its accent bar, `ArtifactEditor`, Generate, and its own print copy. A new `JobArtifactEditModal` is a stacked, full-screen split pane over the Job Analysis Report. For the job resume it shows `ResumeContentEditor` with the job resume preview; for the cover letter it shows the existing cover letter `ArtifactEditor` with the cover preview. On the report's Artifacts tab, the tabs that config flags with `preview_thumbnail` show a print-preview thumbnail instead of an inline editor. Clicking a thumbnail opens the edit modal; the job resume also gets an Edit button. Application Questions stays inline. Job Print Resume moves onto `printHtml.ts`, and the report's candidate-structure state goes away. Finally, `ArtifactEditor` loses its resume structure mode: the structure-authoring props, header, and "Save sections" strip, `useCandidateResumeStructure` / `bodyShape`, the internal structure fetches, and the base-resume unsupported-experience Generate escape. Rubric/criteria and shapes modes are unchanged.

## Ground truth (verified on this branch at `49d4a3017`)

- **Siblings (on this branch):**
  - `src/ui/frontend/src/components/SplitPanePage.tsx`: `export default function SplitPanePage({ left, right })`. It fills its parent (`width/height: 100%`).
  - `src/ui/frontend/src/components/PrintPreview.tsx`: `PrintPreview({ target, refreshKey = 0, thumbnail = false, onClick })`, where `target: PrintTarget = { kind: "base" | "job_resume" | "cover", id }`. It refetches on `kind` / `id` / `refreshKey`. Thumbnail mode is a 204 × 264 `.print-preview-thumb` box.
  - `src/ui/frontend/src/lib/printHtml.ts`: `fetchPrintHtml(target) → { ok: true, html } | { ok: false, error }` (never throws), and `openHtmlInNewTab(html) → POPUP_BLOCKED_MESSAGE | null`.
  - `src/ui/frontend/src/components/Modal.tsx`: `size?: "wide" | "fullscreen"`, `stacked?`, `showFooter?`. The discard prompt only fires when `onSave` is passed.
  - `src/ui/frontend/src/components/ResumeContentEditor.tsx`: `ResumeContentEditor({ target: { kind: "base" | "job", id }, onSaved? })`. It remounts per target, flushes pending edits on unmount, and calls `onSaved` after each successful save **while mounted** (L293). It owns its own Print, accent swatches, and toasts.
- **Layout:** `.shell` (App.css L240) is `display: flex; height: 100vh`. `.content` (L613) is `flex: 1; overflow-y: auto` with no padding on desktop, and NavigationShell L262 renders `<main className="content"><Outlet /></main>`. So `SplitPanePage` returned straight from a page spans from the nav's right edge to `window.innerWidth` (AC1). `.modal-overlay--stacked` (L1202) is `z-index: 2000`.
- **Base page:** `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` (257 lines) is the accent bar, structure state, its own `handlePrint` blob copy, and `<ArtifactEditor … taskKey="craft_resume_base" bodyShape="resume_content" structure…>`. Its route is `routes.tsx` L108 `artifacts/base_resume_content` (default import; unchanged).
- **Job report:** `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (803 lines).
  - L10–13 imports `Catalog`, `SectionRow` from `./ResumeStructureEditor`, and L39–45 is `catalogFromPayload`.
  - L100–105 is the structure state; L159–186 the candidate `resume_structure` GET effect; L188–242 `handleStructureRowsChange` / `persistStructureRows` / `saveStructure`.
  - L244–286 is `handlePrintResume`, which persists structure, then does a blob copy. It is the file's only eslint finding: L286 `exhaustive-deps` on `persistStructureRows`.
  - L386 is `artifactTabs = manifest?.jobs.recommended.report_artifact_tabs`. L391–400 `populatedArtifactSections` already filters tabs to those whose artifact has content. L530–569 is `renderArtifactSection`, L800 the `<Toast>`, and L718 the `{job && !loading && (…)}` shell.
- **Tab flag:** `src/utils/config.py` L3622–3647: `artifact_resume` (`use_resume_structure: True`, `preview_thumbnail: True`), `artifact_cover` (`shapes_key: "cover_letter"`, `preview_thumbnail: True`), `artifact_application` (`preview_thumbnail: False`). It is served through the manifest. The frontend type `StateUiContext.tsx` L41–47 does **not** declare `preview_thumbnail`, and that file is outside this ticket's Scope (see Stage 2 Decision).
- **ArtifactEditor:** `src/ui/frontend/src/components/ArtifactEditor.tsx` (1470 lines).
  - Resume-mode pieces: L4 import; L94 `StructureSection`; props L101–111; destructure L149–157; `structureMode` / `structureAuthoring` / add-row state L205–219; catalog effect + row helpers L256–306; `inflightHideStates` L402–405; `experienceUnsupported` L415–423; escape + `canGenerate` L426–434; structure effects L448–493; `structureMode` in load/reload guards (L594, L606, L611, L622, L1024, L1031); `buildPayload` L663; the `resume_structure` add in `doSave` L738–754 (+ deps L789–790); shape-error label L1112; render header branch L1158–1255 + actions L1280; "Save sections" strip L1371–1399.
  - Its only other callers pass none of these props: the seven `Artifacts*Criteria` pages (rubric mode) and the JAR cover/application tabs (shapes / job dict mode).
- **Experience path stays:** `DATA_SHAPES` still declares `base_resume_structure` with an `experience` field of `type: "experience_jobs"` (config.py L6038–6049). `ArtifactEditor`'s `isExperienceTab` / `parseExperienceJobs` / `ExperienceJobsEditor` rendering therefore stays reachable through shapes mode and is not removed (it is not named in Scope).
- **ESLint** (`cd src/ui/frontend && npx eslint <file>`): ArtifactsBaseResumeContent 0, JobAnalysisReportModal 1 (warning, L286 above), ArtifactEditor 0. `react-refresh/only-export-components` is on, so component files export only components and types. **tsc** (`npx tsc -b --noEmit`) exits 0.
- **AC greps today:** `useCandidateResumeStructure|structureCatalog|onStructureSave` has 31 hits (ArtifactEditor 26, JAR 3, base page 2). `Save sections` has 1 hit (ArtifactEditor L1395).
- **Plan dry run:** Stages 1–3 were applied literally (by script, at the line numbers below) in a scratch worktree at this tip. `tsc -b --noEmit` exits 0, eslint reports 0 problems on all four files, and every Done-when grep is empty. Nothing from the dry run was committed.

### Known test drift (Betty — not fixed here)

These existing frontend tests exercise the surfaces this ticket rewrites or removes, and **will fail by design**:

- `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`: the whole page is rewritten (accent bar, structure authoring, `ArtifactEditor`, its own Print — 45 structure-related references).
- `tests/component/frontend/components/test_ArtifactEditor.test.tsx`: the resume structure mode tests (`useCandidateResumeStructure`, `bodyShape`, `structure*` props, `.structure-authoring-*`, "Save sections", the unsupported-experience Generate escape — 98 references). Rubric/criteria and shapes tests should be unaffected.
- `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`: the candidate `resume_structure` fetch, inline resume/cover editors, and Print Resume's structure persist (17 references).

## Canon conformance — `patt.artifact.ui-consistency` (as amended, Decision 7)

The amended pattern says the `resume_content` body shape gets **one** dedicated editor, `ResumeContentEditor`, used by both the base and the job resume, and the cover letter keeps `ArtifactEditor` shapes mode. This ticket makes that true at the call sites. Both resume surfaces (base page, job edit modal) render `ResumeContentEditor` with a `target`; there is no second resume component and no base-only fork. The cover letter in the edit modal is the same `ArtifactEditor` `shapesKey` + `jobPersistence` path the report uses today. Retiring `ArtifactEditor`'s `resume_content` mode removes the old parallel path, so one shape has one editor. Persist and reload stay with the editors' existing entity API contracts; this ticket adds no client storage keys and no frontend catalog fetch. The pattern's Exception 2 (job report on legacy props) no longer applies, because the report now adopts the shared resume editor. The pre-amendment text that names `ArtifactEditor` as the `resume_content` path is superseded by Decision 7; that amendment lands as its own canon ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Rewrite: `SplitPanePage` with `ResumeContentEditor` (base) left and `PrintPreview` (base) right, refresh on `onSaved`; accent bar, `ArtifactEditor`, Generate, and print copy removed | ui |
| `src/ui/frontend/src/components/JobArtifactEditModal.tsx` | New: stacked full-screen `Modal` + `SplitPanePage`; job resume → `ResumeContentEditor` (job) + `PrintPreview` (job_resume); cover letter → `ArtifactEditor` (shapes + job persistence) + `PrintPreview` (cover) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Thumbnails + resume Edit button for `preview_thumbnail` tabs open `JobArtifactEditModal`; reload on close; candidate-structure state/handlers removed; Print Resume on `printHtml.ts` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Resume structure mode removed (props, `useCandidateResumeStructure` / `bodyShape`, structure fetches/effects/helpers, authoring header, "Save sections" strip, base-resume Generate escape); rubric/criteria and shapes modes unchanged | ui |

**Scope gate:** all four rows are files this ticket's `## Scope` names, and each change is the kind its Technical scope describes. No other file is touched. `StateUiContext.tsx`, `App.css`, `ResumeStructureEditor.tsx`, and the sibling components stay as they are. Thumbnail layout uses the existing `.print-preview-thumb` hook plus one inline flex wrapper (App.css is #3's file).

## Stage 1: Base Resume Content on the split pane

**Done when:** `/artifacts/base_resume_content` renders the editor on the left and the base print preview on the right, spanning from the nav's right edge to the viewport's right edge. Leaving an edited field refreshes the preview once. The file has no `craft_resume_base`, `ArtifactEditor`, or `structureCatalog` / `onStructureSave` reference. `npx tsc -b --noEmit` exits 0, and `npx eslint src/pages/ArtifactsBaseResumeContent.tsx` reports 0 problems.

1. Replace the entire contents of `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` with:

   ```tsx
   import { useState } from "react"
   import PrintPreview from "../components/PrintPreview"
   import ResumeContentEditor from "../components/ResumeContentEditor"
   import SplitPanePage from "../components/SplitPanePage"
   import { useCandidate } from "../contexts/CandidateContext"

   /** AST-2084: base resume editor (left) + live base print preview (right); the editor owns accent, Print, and autosave. */
   export default function BaseResumeContent() {
     const { selectedId } = useCandidate()
     // Bumped after each editor save so the preview refetches once (never per keystroke).
     const [refreshKey, setRefreshKey] = useState(0)

     if (!selectedId) return <p style={{ padding: 20, color: "var(--text-primary)" }}>No candidate selected.</p>
     return (
       <SplitPanePage
         left={<ResumeContentEditor target={{ kind: "base", id: selectedId }} onSaved={() => setRefreshKey(k => k + 1)} />}
         right={<PrintPreview target={{ kind: "base", id: selectedId }} refreshKey={refreshKey} />}
       />
     )
   }
   ```

   ⚠️ **Decision:** The page keeps no state beyond the refresh counter. The accent swatches, Print (through `printHtml.ts`), and saves all live in `ResumeContentEditor` (#3), so the old accent bar, `handlePrint`, and structure state are deleted rather than moved. The "No candidate selected." copy matches what `ArtifactEditor` showed on this page. A candidate switch remounts the editor (it keys on `kind:id`) and refetches the preview (it keys on `id`), so neither carries one candidate's state onto another.

2. Run `cd src/ui/frontend && npx tsc -b --noEmit` and `npx eslint src/pages/ArtifactsBaseResumeContent.tsx` (must be 0 problems). Run `git grep -nE "craft_resume_base|ArtifactEditor|structureCatalog|onStructureSave" -- src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` (must be empty). Commit: `code(AST-2084): base resume content on split pane — editor + live preview`.

## Stage 2: Job artifact edit modal + report thumbnails

**Done when:** On a job with a generated job resume and cover letter, the report's Artifacts tab shows two thumbnails (and the inline Application Questions editor when it has content), plus an Edit button beside the resume thumbnail. Clicking the resume thumbnail or Edit opens a stacked full-screen modal over the report with the job resume editor and preview. Clicking the cover thumbnail opens the cover letter fields with the cover preview. Saving refreshes that preview. Closing the modal reloads the report. A job with no generated resume or cover shows no thumbnails. Print Resume opens the job resume HTML through `printHtml.ts` (popup-blocked → the existing toast). `JobAnalysisReportModal.tsx` has no `structureCatalog` / `onStructureSave` / `useCandidateResumeStructure` / `persistStructureRows` / `ResumeStructureEditor` reference. `npx tsc -b --noEmit` exits 0, and eslint reports 0 problems on both files.

1. Create `src/ui/frontend/src/components/JobArtifactEditModal.tsx` with exactly:

   ```tsx
   import { useState } from "react"
   import ArtifactEditor from "./ArtifactEditor"
   import Modal from "./Modal"
   import PrintPreview from "./PrintPreview"
   import ResumeContentEditor from "./ResumeContentEditor"
   import SplitPanePage from "./SplitPanePage"

   /** One manifest `report_artifact_tabs` row. `preview_thumbnail` (AST-2081 config) is not on the shared StateUi type yet. */
   export interface JobArtifactTab {
     tab_id: string
     nav_label: string
     artifact_key: string
     shapes_key: string | null
     use_resume_structure: boolean
     preview_thumbnail?: boolean
   }

   interface Props {
     jobId: string
     /** Tab being edited; null keeps the modal closed. */
     tab: JobArtifactTab | null
     onClose: () => void
   }

   /** AST-2084: stacked full-screen split pane over the Job Analysis Report — the artifact's editor left, its live print preview right. */
   export default function JobArtifactEditModal({ jobId, tab, onClose }: Props) {
     // Bumped after each save so the preview refetches once.
     const [refreshKey, setRefreshKey] = useState(0)
     const bump = () => setRefreshKey(k => k + 1)

     return (
       <Modal open={!!tab} onClose={onClose} title={tab?.nav_label ?? ""} size="fullscreen" stacked showFooter={false}>
         {tab && (
           <SplitPanePage
             left={tab.use_resume_structure
               ? <ResumeContentEditor target={{ kind: "job", id: jobId }} onSaved={bump} />
               // Cover letter: the report's existing shapes + job persistence editor, unchanged (Decision 8).
               : <ArtifactEditor
                   title={tab.nav_label}
                   artifactKey={tab.artifact_key}
                   taskKey="craft_cover_letter"
                   shapesKey={tab.shapes_key ?? undefined}
                   jobPersistence={{ jobId, artifactKey: tab.artifact_key, onSaved: bump }}
                 />}
             right={
               // Thumbnail-eligible tabs are the job resume (structure tab) and the cover letter.
               <PrintPreview target={{ kind: tab.use_resume_structure ? "job_resume" : "cover", id: jobId }} refreshKey={refreshKey} />
             }
           />
         )}
       </Modal>
     )
   }
   ```

   ⚠️ **Decision:** The modal takes the manifest tab row, not a hardcoded artifact name. Which editor to show and which print route to use both follow `use_resume_structure`, the config flag that already marks the resume tab. The cover editor's `shapesKey` and `artifactKey` come from the same row. `taskKey="craft_cover_letter"` repeats the report's existing cover mapping (L556–559); `ArtifactEditor` never shows Generate under `jobPersistence`, so it is inert here. No `onSave` is passed to `Modal`, so closing never shows the discard prompt. `ResumeContentEditor` flushes its own pending edits on unmount, and the cover `ArtifactEditor` saves dirty fields on unmount (L847–852). `react-refresh/only-export-components` allows the exported `interface`. A helper function export would be flagged, which is why the print-kind ternary is inline here and in the report.

2. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (line numbers are pre-edit; match on the quoted text, or edit bottom-up):
   1. **Imports.** Delete L10–13 (`import { type Catalog, type SectionRow } from "./ResumeStructureEditor"`). After `import JobDiscussionPane from "./JobDiscussionPane"` (L5), add `import JobArtifactEditModal, { type JobArtifactTab } from "./JobArtifactEditModal"`. After `import Modal from "./Modal"` (L7), add `import PrintPreview from "./PrintPreview"`. After `import { postSkipJob } from "../lib/candidateJobActions"` (L19), add `import { fetchPrintHtml, openHtmlInNewTab } from "../lib/printHtml"`. Keep the `ArtifactEditor` import; Application Questions still uses it.
   2. Delete `catalogFromPayload` (L39–45, including the blank line after it).
   3. Replace the six structure `useState` lines (L100–105, `structureSections` through `structureSaveError`) with:
      ```tsx
      // AST-2084: artifact tab open in the stacked edit modal (null = closed).
      const [editTab, setEditTab] = useState<JobArtifactTab | null>(null)
      ```
   4. Delete the structure effect with its leading comment (L159–186, from `// Resume section labels + structure authoring …` through `}, [selectedId])`). Then delete `handleStructureRowsChange`, `persistStructureRows`, and `saveStructure` (L188–242).
   5. Replace `handlePrintResume` with its leading comment (L244–286) with:
      ```tsx
      // AST-2084: shared print helper; the job's structure is saved by the resume editor, so nothing persists first.
      const handlePrintResume = useCallback(async () => {
        if (!jobId) return
        const r = await fetchPrintHtml({ kind: "job_resume", id: jobId })
        const err = r.ok ? openHtmlInNewTab(r.html) : r.error
        if (err) setToast({ text: err, variant: "error" })
      }, [jobId])
      ```
   6. Change L386 `const artifactTabs = manifest?.jobs.recommended.report_artifact_tabs` to `const artifactTabs: JobArtifactTab[] | undefined = manifest?.jobs.recommended.report_artifact_tabs`.
   7. In `renderArtifactSection`, replace the whole `if (artTab.use_resume_structure) { … }` block (L534–555) with:
      ```tsx
      // AST-2084: config-flagged tabs show the print preview; a click (or Edit, resume only) opens the stacked edit modal.
      if (artTab.preview_thumbnail) {
        return (
          <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
            <PrintPreview
              target={{ kind: artTab.use_resume_structure ? "job_resume" : "cover", id: jobId }}
              thumbnail
              onClick={() => setEditTab(artTab)}
            />
            {artTab.use_resume_structure && (
              <button type="button" className="btn secondary" onClick={() => setEditTab(artTab)}>
                Edit
              </button>
            )}
          </div>
        )
      }
      ```
      Leave the rest of the function (the `taskKey` mapping and the inline `ArtifactEditor` for the remaining tabs) unchanged.
   8. Directly above `<Toast message={toast} onDone={clearToast} />` (L800), add:
      ```tsx
      {/* Outside the job shell so the reload on close cannot unmount it mid-flush; close reloads the report (thumbnails refetch on remount). */}
      {jobId && (
        <JobArtifactEditModal jobId={jobId} tab={editTab} onClose={() => { setEditTab(null); void load() }} />
      )}
      ```

   ⚠️ **Decision:** Thumbnails need no content check of their own. `ReportSectionList` only renders `populatedArtifactSections`, which already drops tabs whose artifact is empty (L391–400), so "thumbnails for generated artifacts only" (AC4) holds through the existing filter.

   ⚠️ **Decision:** `preview_thumbnail` is read through the local `JobArtifactTab` type instead of editing `StateUiContext.tsx`, which is not in this ticket's Scope. This follows #3's precedent of extending `UiConfig` locally (`ResumeContentEditor.tsx` L23–28). The manifest row type is assignable to `JobArtifactTab[]` because the extra field is optional, so no cast is needed.

   ⚠️ **Decision:** Closing the edit modal calls `load()`, which is the ticket's "reload on close". `load()` briefly unmounts the report shell, so the thumbnails remount and refetch the print HTML. That also collapses the Artifacts sections, the same as today's explicit-Save reload (`jobPersistence.onSaved: load`). Print Cover (L743–750) is not changed; the Scope moves only Print Resume onto the helper.

   ⚠️ **Decision (known limit, not fixed here):** `ResumeContentEditor` only calls `onSaved` while mounted (L293). Clicking the modal's × first blurs the field, which starts the save. If that PUT is still in flight when the modal unmounts, the report's reload can race it and a thumbnail may show the pre-save page until the next reload. Fixing that needs an awaited flush from the editor, which is #3's component. This ticket does not add a timer or retry (no unrequested heuristics).

3. Run `cd src/ui/frontend && npx tsc -b --noEmit` and `npx eslint src/components/JobAnalysisReportModal.tsx src/components/JobArtifactEditModal.tsx` (both 0 problems; the JAR's L286 warning goes with the old `handlePrintResume`). Run `git grep -nE "structureCatalog|onStructureSave|useCandidateResumeStructure|persistStructureRows|ResumeStructureEditor" -- src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (must be empty). Commit: `code(AST-2084): job artifact edit modal; report thumbnails + Edit; print resume via printHtml`.

## Stage 3: Retire resume mode in ArtifactEditor

**Done when:** `git grep -nE "useCandidateResumeStructure|structureCatalog|onStructureSave" -- src/ui/frontend/src` and `git grep -n "Save sections" -- src/ui/frontend/src` are both empty. `git grep -nE "structureMode|structureAuthoring|bodyShape|baseResumeUnsupportedEscape|experienceUnsupported|inflightHideStates|StructureSection|ResumeStructureEditor" -- src/ui/frontend/src/components/ArtifactEditor.tsx` is empty. The criteria pages, the cover letter editor, and Application Questions behave as before. `npx tsc -b --noEmit` exits 0, and `npx eslint src/components/ArtifactEditor.tsx` reports 0 problems.

All line numbers are for `src/ui/frontend/src/components/ArtifactEditor.tsx` as it is at the start of this stage; Stages 1–2 do not touch it. Make the edits bottom-up (step 13 first, step 1 last) so earlier line numbers stay valid, or match on the quoted text.

1. Delete L4 `import type { Catalog, SectionRow } from "./ResumeStructureEditor"`.
2. L85: change the comment `// experience_jobs from DATA_SHAPES, or structureMode tabs that only carry key/label` to `// experience_jobs from DATA_SHAPES (e.g. base_resume_structure)`.
3. Delete L94 `interface StructureSection { id: string; label: string }` and the blank line after it.
4. In `ArtifactEditorProps`, delete L101–111 (`useCandidateResumeStructure?: boolean` through `structureError?: string | null`, including the two doc comments on `bodyShape` and `structureCatalog`).
5. In the destructuring, delete L149–157 (`useCandidateResumeStructure = false,` through `structureError = null,`).
6. Replace L205–219 (from `const structureMode =` through the closing `)` of the `addFormat` `useState`) with:
   ```tsx
   // Tab chrome (rename/add/remove/rubric) stays off in shapes mode; bodies use bodiesEditable.
   const tabChromeEditable = !shapesKey
   ```
7. Delete L256–306: the `useEffect` on `structureCatalog`, and `reindexStructureRows`, `patchStructureRow`, `moveStructureRow`, `removeStructureRow`, and `addStructureSection`. Stop at the blank line before `const fixedFields =`.
8. Edit these comments and the line that follows:
   - L311: `// Bodies editable in rubric chrome mode OR structure/shapes/job fixed tabs; …` → `// Bodies editable in rubric chrome mode OR shapes/job fixed tabs; never during Generate review.`
   - Replace L313–314 with:
     ```tsx
     // Criteria (free-form) editors blur-save bodies; shapesKey job editors keep explicit Save/Cancel.
     const autosaveBodies = tabChromeEditable
     ```
   - L319: `(resume_content structure, cover_letter shape)` → `(shapes mode, e.g. cover_letter)`.
9. Delete the `inflightHideStates` `useMemo` (L402–405). Delete the `experienceUnsupported` `useMemo` with its comment (L415–423). Replace the escape and `canGenerate` (L426–434, from `// Base Resume: show Generate/Regenerate …` through `&& (generateStates.has(candidateState) || baseResumeUnsupportedEscape)`) with:
   ```tsx
   const canGenerate = !jobPersistence && generateStates.has(candidateState)
   ```
10. Delete both structure effects with their comments (L448–493, from `// Per-candidate structure: prefer authoring rows …` through `}, [structureMode, structureSections, selectedId, structureAuthoring])`). L515: change `reorder tabs to match structure rows without re-GET` to `reorder tabs to match shape fields without re-GET`.
11. Remove `structureMode` from the load and reload guards:
    - L594, L1024: `if ((shapesKey || structureMode) && !fixedFieldKeys) return` → `if (shapesKey && !fixedFieldKeys) return`.
    - L611, L1031: `((shapesKey || structureMode) && !fixedFieldKeys)` → `(shapesKey && !fixedFieldKeys)`.
    - L606: drop `structureMode` from the dependency array, giving `[jobPersistJobId, artifactKey, fixedFieldKeys, shapesKey]`.
    - L622: drop `structureMode`, giving `[jobPersistence, selectedId, artifactKey, fixedFieldKeys, shapesKey, chainArtifactKeys]`.
    - L663: `if (fixedFields || (jobPersistence && !shapesKey && !structureMode)) {` → `if (fixedFields || (jobPersistence && !shapesKey)) {`.
12. In `doSave`:
    - L679: change the comment to `// Save to backend: job artifact PUT, or candidate /data PUT under the leaf key.`
    - Replace L738–754 (`const arts: Record<string, unknown> = { [artifactKey]: payload }` and the whole `if (structureAuthoring && structureRows) { … }` block) with `const arts = { [artifactKey]: payload }`.
    - In the dependency array, delete the `structureAuthoring,` and `structureRows,` lines (L789–790).
13. Render:
    - L1112: `const shapeLabel = shapesKey ?? (structureMode ? "resume structure" : "fields")` → `const shapeLabel = shapesKey ?? "fields"`.
    - In `tabsForRail.map`, change `{tabsForRail.map((tab, i) => {` (L1157) to `{tabsForRail.map((tab, i) => (`. Delete L1158–1171 (the `structureRow` / `formatValue` / `structureRowIndex` consts and `return (`), and change the closing `)` + `})}` after `</CollapsiblePanel>` (L1368–1369) to `))}`.
    - In `label={…}`, delete the `structureRow ? ( <div className="structure-authoring-header"> … </div> ) :` branch (L1175–1256), so the expression starts at `tabChromeEditable && editingId === tab.id ? (`.
    - In `actions={…}`, change `structureRow ? undefined : tabChromeEditable ? (` (L1280) to `tabChromeEditable ? (`.
    - Delete the `{structureAuthoring && ( <div className="base-resume-structure-add"> … </div> )}` block (L1371–1399).
    - Reindent the touched JSX to the surrounding two-space style.

⚠️ **Decision:** These pieces stay: `isExperienceTab` / `parseExperienceJobs` / `ExperienceJobsEditor`, the experience-field `ui_config` load, `unsupportedExperienceMessage`, and the save-time experience validation. `DATA_SHAPES.base_resume_structure` still declares an `experience_jobs` field, so shapes mode can still reach them, and the Scope names only the structure props/branches, `useCandidateResumeStructure`, the structure fetches, and the Generate escape. The `headerActions` prop also stays; it is generic chrome, not resume mode. `candidateState`, `generateStates`, and `isChainHandoff` still drive Generate on the criteria pages.

14. Run `cd src/ui/frontend && npx tsc -b --noEmit` (exit 0) and `npx eslint src/components/ArtifactEditor.tsx` (0 problems). Run the three greps from **Done when** (all empty). Commit: `code(AST-2084): retire resume structure mode in ArtifactEditor`.

## Acceptance mapping (this ticket's AC 1–5)

| AC | Covered by |
|----|-----------|
| 1 Split pane spans the content area | Stage 1: the page returns `SplitPanePage` straight into padding-free `.content`. Stage 2: modal `size="fullscreen"` (100vw body, no padding) |
| 2 No Save buttons | Stage 1 (base page has no `ArtifactEditor`), Stage 2 (job resume modal uses `ResumeContentEditor`), Stage 3 ("Save sections" strip deleted → grep empty). The cover letter modal keeps its existing shapes-mode Save, but it is not a resume editor |
| 3 Generate gone from Base Resume Content | Stage 1 (no `ArtifactEditor` and no `craft_resume_base` on the page) |
| 4 Thumbnails open the edit modal | Stage 2: thumbnails for populated `preview_thumbnail` tabs, resume Edit button, stacked modal, no thumbnails when nothing is generated |
| 5 Resume mode gone from ArtifactEditor | Stage 3 (grep empty); Stages 1–2 (both resume surfaces render `ResumeContentEditor`) |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2084
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** `origin/sub/AST-2046/AST-2084-wire-resume-surfaces` @ `8778d5883`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |

## Traceability

AC1→S1,S2 · AC2→S1–S3 · AC3→S1 · AC4→S2 · AC5→S1–S3

## Findings

### discuss — Modal close vs in-flight autosave (known race)
- **Severity:** discuss
- **Location:** Stage 2 Decision (known limit); `ResumeContentEditor` `onSaved` while mounted
- **Finding:** Closing the stacked modal can reload the report before a blur-started PUT finishes, so a thumbnail may lag one save until the next reload.
- **Recommendation:** Accept for this ticket (plan defers flush/await to #3) or open a small #3 follow-up if Susan wants close-to-block until save settles.

### discuss — `preview_thumbnail` typed locally, not on `StateUiContext`
- **Severity:** discuss
- **Location:** `JobArtifactEditModal` / Stage 2 Decision
- **Finding:** Manifest field is read via `JobArtifactTab` optional field; shared UI context type unchanged (out of scope).
- **Recommendation:** Fine for ship; optional hygiene ticket to extend `StateUiContext` when someone touches that file.

### acceptable — Frontend test drift called out
- **Severity:** acceptable
- **Location:** `### Known test drift (Betty — not fixed here)`
- **Finding:** Base page, `ArtifactEditor` resume-mode, and JAR tests will fail until Betty rewrites them against new surfaces.
- **Recommendation:** Expected; not a plan defect.

### acceptable — Cover letter modal keeps shapes Save/Cancel
- **Severity:** acceptable
- **Location:** AC2 mapping table, `JobArtifactEditModal` cover branch
- **Finding:** Child AC2 targets **resume** editors only; cover `ArtifactEditor` is unchanged shapes mode.
- **Recommendation:** Matches parent functional scope (Decision 8).

### acceptable — No `## Self-assessment` block
- **Severity:** acceptable
- **Location:** Plan doc structure
- **Finding:** Estimate confirm only.
- **Recommendation:** Optional; not blocking.

## R6 (summary)

Definition fidelity: Exactly four scoped files; siblings untouched. Stage 1 rewires base page to `SplitPanePage` + `ResumeContentEditor` + `PrintPreview` with `refreshKey` on save. Stage 2 adds stacked fullscreen `JobArtifactEditModal` (resume vs cover via `use_resume_structure`), thumbnails + Edit for `preview_thumbnail` tabs gated by existing populated-artifact filter, drops JAR structure authoring and print blob copy for `printHtml`, reload on modal close. Stage 3 bottom-up excision of `ArtifactEditor` resume structure mode with explicit preservation list for shapes/rubric/experience paths. Dry-run + grep Done-when gates match child AC 2/3/5. Wiring completes amended Decision 7: one `ResumeContentEditor` for both resume surfaces, cover on shapes `ArtifactEditor`, parallel resume path removed.

context_tokens≈75000

## Review (build)

- **Branch:** `origin/sub/AST-2046/AST-2084-wire-resume-surfaces`
- **Commits:** `3ba28d33a` (Stage 1, base page split pane), `85982422f` (Stage 2, `JobArtifactEditModal` + report thumbnails/Edit + print via `printHtml`), `1475d32b6` (Stage 3, `ArtifactEditor` resume structure mode retired)
- **Gates:** `npx tsc -b --noEmit` exit 0 and eslint 0 problems after every stage; all Done-when greps empty; `validate-sub-log.sh --stage=build` ok.
- **Deviations:** none — files match the plan's stage code.
- **Known test drift for Betty:** `test_ArtifactsBaseResumeContent`, resume-mode cases in `test_ArtifactEditor`, `test_JobAnalysisReportModal` (structure authoring / blob print paths removed by plan).

## Radia review

[code-rubric]
**Ticket:** AST-2084
**Publish ref:** `f04b6c6563bb00fc2b02b2238ed7176927bf347d` (`origin/sub/AST-2046/AST-2084-wire-resume-surfaces`)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.ui-consistency | A | | |

## Column diff vs plan stage

(aligned) — Joan **A**; code **A**.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Modal close vs in-flight autosave** — Closing `JobArtifactEditModal` calls `load()` on close while `ResumeContentEditor` may still have a blur-started PUT in flight; thumbnail/report can lag one save (Joan plan discuss).
  - **@susan:** Accept for overhaul UAT or ask **AST-2083** for close-blocking / await flush?
  - **Default:** Accept; next report reload or re-open refreshes.

- **`preview_thumbnail` not on `StateUiContext`** — JAR reads `preview_thumbnail` via local `JobArtifactTab` optional field; shared manifest type unchanged (Joan plan discuss).
  - **Default:** Ship as-is; extend `StateUiContext` in a hygiene pass when that file is touched.

### advisory

- **Sibling product carry on publish ref:** `origin/dev...f04b6c656` still includes **AST-2081–2083** (and dev-merge) product outside this ticket. **2084 `code()` commits** (`3ba28d33a`, `85982422f`, `1475d32b6`) touch only the four scoped frontend files; siblings are not modified by 2084.
- **Dependencies:** Spawn lists **AST-2082** / **AST-2083** blocked-by at UT; this ref composes their primitives (`SplitPanePage`, `PrintPreview`, `ResumeContentEditor`, `printHtml`) as planned.
- **Tests:** Tip commit `f04b6c656` rewrites base page, JAR, and retires `ArtifactEditor` resume-mode tests (plan-known drift addressed by Betty on this ref).

## What’s solid

- **Decision 7 wiring:** Base page is `SplitPanePage` + `ResumeContentEditor` (`kind: "base"`) + `PrintPreview` with `refreshKey` on `onSaved`; job resume uses the same editor (`kind: "job"`) in `JobArtifactEditModal`; cover stays `ArtifactEditor` shapes + `jobPersistence`.
- **Retirement:** Product greps empty for `Save sections`, `useCandidateResumeStructure`, `structureCatalog`, `onStructureSave`, `bodyShape`/`resume_content` resume-mode surface (AC5/AC13-style cleanup on `src/ui/frontend`).
- **JAR:** `preview_thumbnail` tabs → thumbnail `PrintPreview` + Edit (resume); application tab stays inline `ArtifactEditor`; candidate structure authoring and blob print copy removed; `handlePrintResume` uses `fetchPrintHtml` / `openHtmlInNewTab`.
- **No new client storage keys or frontend catalog fetch** — persist/reload remain on existing editor API contracts.

## Recommended actions (for Chuckles — not Radia)

- Append artifact to `docs/features/interface/ast-2084-wire-resume-surfaces.md`; commit `docs(AST-2084): Radia review — clean`; push publish ref.
- Post slim upshot via `linear_proxy.py --as radia save-comment`.
- **Review Posted** → **PROCEED** toward UT (parent AC1–5 integration UAT on this ref).

```
[code-rubric] PROCEED (Commit: f04b6c656) One resume editor wired
```

context_tokens≈30000

## Resolution

**2026-10-09 · Ada** — Radia review at `c68deb396` (PROCEED, CLEAN): no fix-now items, no product changes.

- **Discuss — modal close vs in-flight autosave:** no direction from Susan in the thread, so took the review's **Default:** accept for overhaul UAT. The next report reload or re-open of the modal picks up the save. Susan can reverse this by routing close-blocking / await-flush to AST-2083.
- **Discuss — `preview_thumbnail` not on `StateUiContext`:** took the **Default:** ship as-is on the local `JobArtifactTab` type, and extend `StateUiContext` in a hygiene pass the next time that file is touched.
- **Advisory:** no action needed. Sibling carry is expected, and the dependencies and test drift were already handled on this ref.
