# Modal shell, horizontal tabs, sticky header (Redesign Recommended Job Modal)

**Linear:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`

Rebuild the Recommended Job Report chrome: replace the left `SideTabPanel` rail with three horizontal top tabs (**Summary** / **Analysis** / **Artifacts**, Summary default), introduce a shared collapsible section-list pattern (empty bodies for siblings), and restyle the sticky header for deeplinked job title + company, Copy Application Email / Copy LinkedIn Profile, and Print Resume / Print Cover Letter (AST-605 HTML routes in a new tab). List row-click entry and Skip stay unchanged. Does **not** implement Summary / Analysis / Artifacts section bodies (AST-949 / AST-950 / AST-951) and does **not** change consult scoring, dispatch, or the artifact pipeline.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `report_fixed_tabs` with `report_top_tabs`; add `report_summary_sections`; update phase/artifact `nav_label`s for section chrome; expose all via `build_state_ui_manifest` | utils |
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Type manifest: `report_top_tabs`, `report_summary_sections`; drop `report_fixed_tabs` | ui |
| `src/ui/frontend/src/components/ReportSectionList.tsx` | **New** — Expand-All `CollapsiblePanel` stack driven by section defs + `renderSection` | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Sticky header: deeplinked job title + company; Copy Application Email / LinkedIn; Print Resume / Cover; remove Preview Materials + primary-action chrome | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Horizontal `TabBar` shell; wire `ReportSectionList` per top tab with empty bodies; park Generate/Cancel in Artifacts action strip; drop `SideTabPanel` + `MaterialsPreviewModal` usage | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Helpers for print visibility / top-tab ids; drop or stop using `materialsPreviewVisible` from the modal path | ui |
| `src/ui/frontend/src/App.css` | Styles for horizontal report tabs + section stack under recommended-report; adjust header title link | ui |

**Out of scope (this ticket):** section body content for Summary / Analysis / Artifacts (siblings); deleting `MaterialsPreviewModal.tsx` or `SideTabPanel.tsx` (other screens still use them); `JobsRecommended.tsx` list/Skip behavior; any edit under `tests/` or `docs/test-bible/**` (Betty at Code Complete).

**QA note (Betty — not engineer commits):** Manifest + frontend tests that still assert left-rail `report_fixed_tabs` / `.side-tab-list` for this modal must be updated for horizontal Summary/Analysis/Artifacts and sticky header print/copy controls.

---

## Stage 1: Manifest — top tabs + section chrome defs

**Done when:** `GET /api/state_ui_manifest` → `jobs.recommended` exposes `report_top_tabs` (Summary / Analysis / Artifacts), `report_summary_sections` (five section rows with `default_expanded`), and updated phase/artifact `nav_label`s for section headers. `report_fixed_tabs` is gone.

1. In `src/utils/config.py`, near `JOBS_RECOMMENDED_REPORT_PHASE_TABS` / `JOBS_RECOMMENDED_ARTIFACT_TABS`:

   - Add:

     ```python
     JOBS_RECOMMENDED_REPORT_TOP_TABS = [
         {"tab_id": "summary", "nav_label": "Summary"},
         {"tab_id": "analysis", "nav_label": "Analysis"},
         {"tab_id": "artifacts", "nav_label": "Artifacts"},
     ]

     JOBS_RECOMMENDED_REPORT_SUMMARY_SECTIONS = [
         {"section_id": "job_summary", "nav_label": "Job Summary", "default_expanded": True},
         {"section_id": "company_upshot", "nav_label": "Company Upshot", "default_expanded": True},
         {"section_id": "caveats", "nav_label": "Noteworthy Caveats", "default_expanded": True},
         {"section_id": "questions", "nav_label": "Questions to Ask", "default_expanded": True},
         {"section_id": "raw_jd", "nav_label": "Raw Job Description", "default_expanded": False},
     ]
     ```

   - Update `JOBS_RECOMMENDED_REPORT_PHASE_TABS` `nav_label` values to exactly: `"JD Analysis"`, `"DO Analysis"`, `"GET Analysis"`, `"LIKE Analysis"` (keep `tab_id` / `grades_field` / `take_key` unchanged — these rows are now **Analysis tab sections**, not top tabs).

   - Update `JOBS_RECOMMENDED_ARTIFACT_TABS` `nav_label` values to exactly: `"Job Resume"`, `"Cover Letter"`, `"Application Questions"` (keep `tab_id` / `artifact_key` / `shapes_key` / `use_resume_structure`).

2. In `build_state_ui_manifest()` under `jobs.recommended`:

   - Remove the inline `report_fixed_tabs` list.
   - Add `"report_top_tabs": list(JOBS_RECOMMENDED_REPORT_TOP_TABS)`.
   - Add `"report_summary_sections": list(JOBS_RECOMMENDED_REPORT_SUMMARY_SECTIONS)`.
   - Keep `"report_phase_tabs"` and `"report_artifact_tabs"` as today (same list sources; labels updated above).

3. In `src/ui/frontend/src/contexts/StateUiContext.tsx`, update `jobs.recommended` types:

   - Remove `report_fixed_tabs`.
   - Add `report_top_tabs?: Array<{ tab_id: string; nav_label: string }>`.
   - Add `report_summary_sections?: Array<{ section_id: string; nav_label: string; default_expanded: boolean }>`.
   - Leave `report_phase_tabs` / `report_artifact_tabs` types unchanged.

⚠️ **Decision:** Keep `report_phase_tabs` / `report_artifact_tabs` key names (semantic shift: top-level tabs → sections inside Analysis / Artifacts). Avoids renaming churn for sibling plans and existing helpers; only `report_fixed_tabs` → `report_top_tabs` is a breaking rename.

---

## Stage 2: Shared `ReportSectionList` + CSS chrome

**Done when:** `ReportSectionList` compiles; App.css has recommended-report horizontal-tab + section-stack rules. No modal behavior change yet (component unused until Stage 3).

1. Create `src/ui/frontend/src/components/ReportSectionList.tsx`:

   ```tsx
   export type ReportSectionDef = {
     section_id: string
     nav_label: string
     default_expanded: boolean
   }

   export type ReportSectionListProps = {
     sections: readonly ReportSectionDef[]
     /** Body for one section — AST-948 passes empty/null; siblings replace. */
     renderSection: (sectionId: string) => ReactNode
     /** Optional slot above the stack (e.g. Artifacts Generate/Cancel strip). */
     leading?: ReactNode
   }
   ```

   Implementation requirements:

   - Import `CollapsiblePanel` and `useSectionExpandPolicy`.
   - Call `useSectionExpandPolicy({ expandAll: true, sectionKeys })` where `sectionKeys = sections.map(s => s.section_id)`.
   - On mount and whenever `sectionKeys` / `default_expanded` set changes, `setExpandedKeys(new Set(sections.filter(s => s.default_expanded).map(s => s.section_id)))`.
   - Render `leading` (if any), then one `CollapsiblePanel` per section: `label={nav_label}`, controlled `expanded={isExpanded(section_id)}`, `onExpandedChange={(next) => onExpandedChange(section_id, next)}`, children = `renderSection(section_id)`.
   - Do **not** render `SectionExpandChrome` (no Expand all / Collapse all chrome in this modal).
   - Do **not** put grade/metadata slots here — AST-950 owns Analysis header metadata via `CollapsiblePanel` `metadata` later; AST-948 leaves `metadata` / `actions` unset.

2. In `src/ui/frontend/src/App.css` (recommended-report block / TOC):

   - Add rules so `.recommended-report-body` hosts a horizontal tab strip (reuse existing `.tabbed-ta-bar` / `.tabbed-ta-tab` visually, optionally scoped under `.recommended-report-tabs`) and a scrollable `.recommended-report-tab-pane` below it.
   - Ensure sticky stack works: header sticky at top; tab bar sticky directly under the header (`position: sticky` with an appropriate `top` matching header height, or wrap header+tabs in one sticky chrome container). Section list scrolls inside `.recommended-report-tab-pane` (`overflow: auto`, `min-height: 0`, flex child of the shell).
   - Add `.recommended-report-title-link` for the deeplinked job title (inherit title weight/size from `.recommended-report-title`; accent/underline only on hover — match existing `.recommended-report-company-link` density).
   - Remove or stop relying on `.recommended-report-body .side-tab-panel` for this modal (leave global `.side-tab-panel` rules intact for other screens).

⚠️ **Decision:** Expand All (`expandAll: true`) matches parent AC that sections open/close independently. Seed from `default_expanded` so first paint matches parent defaults (e.g. Raw JD collapsed).

---

## Stage 3: Sticky header — deeplinks, copy, print

**Done when:** Header shows deeplinked job title (apply URL), deeplinked company (homepage when known), **Copy Application Email**, **Copy LinkedIn Profile**, and **Print Resume** / **Print Cover Letter** only when those artifacts exist. Preview Materials and header primary-action buttons are gone from this component.

1. Rewrite `RecommendedJobReportHeader` props to:

   ```tsx
   interface Props {
     jobTitle: string
     jobLink: string | null
     companyName: string
     companyWebsite: string | null
     applicationEmail: string | null  // raw email; parent applies plus-tag on copy
     linkedInUrl: string | null
     copyFeedback?: string | null
     onCopyApplicationEmail?: () => void
     onCopyLinkedIn?: () => void
     showPrintResume: boolean
     showPrintCover: boolean
     onPrintResume?: () => void
     onPrintCover?: () => void
   }
   ```

2. Layout (single sticky header card, no state chip, no Generate/Cancel/Apply, no Preview Materials):

   - Row 1: Job title — if `jobLink` trim nonempty, `<a href={jobLink} target="_blank" rel="noopener noreferrer" className="recommended-report-title-link">`; else `<span className="recommended-report-title">`. Display text = `jobTitle` (fallback already resolved by parent to company or `"Recommended Job Report"`).
   - Same row or immediately under: company — website link when known (existing pattern), else plain span.
   - Row 2: Copy buttons — render **Copy Application Email** only when `applicationEmail` nonempty; **Copy LinkedIn Profile** only when `linkedInUrl` nonempty. Exact visible labels. Show `copyFeedback` beside them when set.
   - Row 3: Print buttons — **Print Resume** when `showPrintResume`; **Print Cover Letter** when `showPrintCover`. Use existing `modal-btn cancel` (or secondary) class; `type="button"`.

3. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`:

   - Add `printResumeVisible(artifacts)` → `artifactHasContent(artifacts, "resume_content")`.
   - Add `printCoverVisible(artifacts)` → `artifactHasContent(artifacts, "cover_letter")`.
   - Stop calling `materialsPreviewVisible` from `JobAnalysisReportModal` (function may remain exported for now — do not delete unless nothing else imports it; if unused after this ticket, leave it for Betty/cleanup rather than expanding scope).

4. Print handlers (owned by modal, passed into header): `window.open(`/candidate/resume/${encodeURIComponent(jobId)}`, "_blank", "noopener,noreferrer")` and `/candidate/cover/...` respectively. Do **not** open `MaterialsPreviewModal`. Do **not** add print for application questions.

⚠️ **Decision:** Application email = `candidate_data.profile.contact_email` if nonempty, else `reply_email` if nonempty, else null. Plus-tag copy continues via existing `emailWithJobPlusTag` + `external_job_id` / `astral_job_id` logic in the modal. LinkedIn = `profile.linkedin_url` only — drop GitHub / extra profile copy chips from this header (AC names two copy controls).

---

## Stage 4: Wire modal shell — horizontal tabs, empty sections, Artifacts action strip

**Done when:** Opening a Recommended job shows horizontal **Summary** / **Analysis** / **Artifacts** (Summary default); each tab shows the configured collapsible section chrome with empty bodies; sticky header matches Stage 3; Generate/Cancel remain reachable on the Artifacts tab; `SideTabPanel` and `MaterialsPreviewModal` are unused by this modal; `JobsRecommended` list entry/Skip untouched.

1. In `JobAnalysisReportModal.tsx`:

   - Remove imports/usage of `SideTabPanel`, `MaterialsPreviewModal`, `AgentAnalysisHeader`, `ArtifactEditor`, and phase-tab grade-dot label helpers used only for the old rail (`renderTabLabel` / `buildPhaseTabGradeDots` / `formatPhaseTabNavLabel` / `jobGradesForField` / structure-fetch effect for resume editor). Keep `parseAnalysisUpshot` only if still needed — for AST-948 empty bodies it is **not** needed; remove upshot-driven pane rendering.
   - Import `TabBar` from `./TabbedTextArea` and `ReportSectionList`.
   - Modal `title` prop: use `job?.company || "Recommended Job Report"` (job title lives in sticky header only — avoid duplicate titles).
   - Build top tabs from `manifest.jobs.recommended.report_top_tabs` (fallback empty → show `recommended-report-empty` “Report layout unavailable…”).
   - Local state `activeTopTab` initialized to `"summary"`; when tabs load, if current id missing from list, reset to first tab (Summary).
   - Persist tab selection while the modal is open (do not reset `activeTopTab` on `load()` refresh). Reset to `"summary"` when `jobId` changes (new open).
   - Shell structure:

     ```tsx
     <div className="recommended-report-shell">
       <RecommendedJobReportHeader … />
       <div className="recommended-report-body">
         <div className="recommended-report-tabs">
           <TabBar tabs={…} active={activeTopTab} onChange={setActiveTopTab} />
         </div>
         <div className="recommended-report-tab-pane">
           {activeTopTab === "summary" && (
             <ReportSectionList
               sections={summarySections /* map manifest rows to ReportSectionDef */}
               renderSection={() => null}
             />
           )}
           {activeTopTab === "analysis" && (
             <ReportSectionList
               sections={analysisSections /* from report_phase_tabs: section_id=tab_id, default_expanded = (tab_id === "phase_jd") */}
               renderSection={() => null}
             />
           )}
           {activeTopTab === "artifacts" && (
             <ReportSectionList
               leading={/* primary actions strip — see below */}
               sections={artifactSections /* from report_artifact_tabs; default_expanded false for all */}
               renderSection={() => null}
             />
           )}
         </div>
       </div>
     </div>
     ```

   - **Analysis default expand:** only `phase_jd` → `default_expanded: true`; other phase sections `false` (parent: JD Analysis expanded by default).
   - **Artifacts sections:** always render all three section chrome rows from manifest (do **not** gate on `artifactHasContent` — visibility of editors is AST-951). Bodies stay empty.
   - **Artifacts `leading` action strip:** using existing `primaryActionsForState(manifest, job.state)`:
     - Render every action **except** `action_key === "apply"` (apply is the job-title deeplink).
     - Keep Generate / Cancel POST behavior, busy/`in-flight` class, and AST-591 close-on-generate/cancel behavior exactly as today.
     - If no remaining actions, omit `leading`.
   - Wire header props from Stage 3 (print flags via new helpers; email/LinkedIn from profile; copy handlers).
   - Do **not** edit `JobsRecommended.tsx`.

2. Confirm compile: `cd src/ui/frontend && npx tsc -b --noEmit` (and Python syntax for config if touched). Fix only type errors caused by this plan’s files.

⚠️ **Decision:** Empty section bodies are intentional — AST-949/950/951 own content. Parking Generate/Cancel on the Artifacts tab leading strip (not header) prevents Generate regression before AST-951 while matching the redesign’s header AC. Apply is not duplicated as a button.

⚠️ **Decision:** Always show all three Artifacts section headers in the shell (empty). AST-951 will decide empty vs populated body / Generate-only layout; shell only establishes the section list pattern.

---

## Self-Assessment

**Scope:** Single-Component — config manifest slice plus Recommended Job Report modal chrome (`JobAnalysisReportModal`, header, new `ReportSectionList`, CSS); no core/data/dispatch changes.

**Conf:** high — reuses shipped `TabBar`, `CollapsiblePanel`, `useSectionExpandPolicy`, AST-605 `/candidate/resume|cover/<job_id>` routes, and existing primary-action helpers; scope boundaries vs AST-949/950/951 are explicit.

**Risk:** Medium — temporary empty tab bodies until siblings land, and Generate/Cancel move from header to Artifacts strip; wrong wiring would regress Recommended triage UX (open/copy/print/generate) even though list Skip/row-click are untouched.

---

## Code rules check

- **§1.3 DRY:** Shared section stack is one `ReportSectionList`; print visibility reuses `artifactHasContent`; no duplicated expand logic outside `useSectionExpandPolicy`.
- **§1.4 / §2.1:** Top tabs + summary section defaults live in `config.py` / manifest — not hardcoded tab id arrays in React beyond reading the manifest.
- **§2.4 / §2.6:** N/A — no batch or state-machine changes.
- **§3.3:** UI edits stay in `src/ui/frontend` + `config.py` manifest; no `data`/`external` imports from React.
- **§3.5:** New component flat under `components/`; styles only in `App.css`.
- **Tests / bible:** Not touched by engineer (Betty).
