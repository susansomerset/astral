# AST-2046 — Resume Edit Overhaul

<!-- linear-archive: AST-2046 archived 2026-10-16 -->

## Linear archive (AST-2046)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2046/resume-edit-overhaul  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Resume editing is the operator's most-used artifact surface, and today it is the clumsiest. Base Resume Content and the Job Analysis Report's Job Resume tab share one long `ArtifactEditor` stack. Every section header is a row of raw controls (name input, two dropdowns, two checkboxes, Up/Down/Remove words). Save scrolls out of reach, and structure has its own separate "Save sections" button. The only way to see the result is Print, which opens a new tab. And because a job resume shares the candidate's one structure, tailoring a section's layout for one job silently changes the base resume and every other job. This epic replaces all of that with a dedicated resume editor on a split pane: compact collapsible section rows on the left, the live print preview on the right, autosave on every field exit, and a structure that belongs to each job resume. The job editor opens as a stacked modal straight from the job's Artifacts tab and can show exactly where the job resume departs from the base. The outcome Susan expects: edit a resume and watch the printed result change beside it, with no Save button to chase, no tab-switching to check layout, and no cross-job side effects.

## Functional scope

 1. **Split-pane page type.** A reusable layout with a left and a right panel and a user-draggable bar between them that resizes both. As a page, the left panel starts at the right edge of the nav menu (or the screen's left edge when the nav is not shown) and the right panel ends at the screen's right edge. As a modal, it fills the screen.
 2. **Base resume on the split pane.** Artifacts → Base Resume Content becomes a split-pane page: the resume editor on the left, print preview on the right. Generate/Regenerate is removed from this page.
 3. **Job resume edit modal.** Each job's resume is edited in a stacked split-pane modal opened over the Job Analysis Report: from an Edit button on the job modal, or by clicking the job resume thumbnail (#4).
 4. **Artifact thumbnails on the job's Artifacts tab.** When a job resume or cover letter has been generated, the Artifacts tab shows a thumbnail of its print preview in place of that artifact's inline editor. Clicking the job resume thumbnail opens the job resume edit modal. Clicking the cover letter thumbnail opens a cover letter edit modal (split pane: the existing cover letter fields on the left, cover letter preview on the right — Decision 8). Application Questions stays inline as today.
 5. **Job-scoped resume structure.** A job resume has its own structure (sections, labels, formats, flow, order, accent color). Until the operator edits it, a job resume uses the candidate's base structure. Edits on the job resume never change the base resume or other jobs.
 6. **Left header.** Above the sections: a Search box (filters the section list to sections whose label or content contains the text; empty shows all), an Add Section button (appends a new section row at the bottom, expanded for editing), the Accent color swatches, a Compare to Base toggle (job resume only — see #11), and a Print button (opens the generated HTML in a new tab, as Print does today).
 7. **Collapsed section row (read-only).** One line per section: `<Section name>: <current value>`, with the value shown in the font of the section's selected format. It has up/down position arrows (plus click-and-drag reorder) and one flow icon showing whether the section is hidden, starts a new page, keeps together, or flows uninterrupted, with a tooltip naming that state. It also has a format label (Line, Prose, Word Cloud, Bullet List, …) whose tooltip describes that format's settings and rules, and a delete button that asks for confirmation. Required sections cannot be deleted or hidden (as today).
 8. **Expanded section row (editable).** The header row becomes editable: section label input, format dropdown, flow-type dropdown (Hidden / New page before / Keep together / Flow uninterrupted), up/down, delete. The Job Edit checkbox stays on the base resume's expanded header only. Below the header is the content edit block, sized to a single line for the Line format.
 9. **Line format.** A new section format, "Line", for a single line of text, rendered in the print HTML as one line. All existing formats stay.
10. **Autosave + versioning.** Every field saves itself when the operator leaves it. It also saves when a header control changes, a row moves or is added or deleted, a swatch is picked, or the page/modal is left. There is no Save button. Saved versions change at most every 60 seconds, through the operator-save coalescing on the candidate and job artifact writes in [AST-2043](https://linear.app/astralcareermatch/issue/AST-2043), which blocks this epic.
11. **Compare to Base (job resume only).** When on: every section whose job content differs from the candidate's current base resume content shows the base content read-only beneath it. A job section that has no counterpart in the base structure shows **"NEW SECTION: Not found in base"**. A base section that is missing from the job structure shows as a **"SECTION REMOVED: <preview of the base section>"** row, at its base position, with an **Add** button that re-adds it to the job resume (structure row + base content). Sections that match show nothing extra. When the toggle is off, none of these appear.
12. **Live print preview (right panel, no header).** Shows the same generated HTML that Print opens. It refreshes after each save, one field at a time and never per keystroke.
13. **Experience section.** Same collapsed/expanded behavior as every other section. Inside it, each job's header text uses the same color as the section header.

## Component scope

* `src/utils/config.py` — **modified** — `line` body format; format labels, tooltip descriptions, and preview fonts; Hidden flow label; new catalog key for the job resume structure; preview-thumbnail flag on the job resume and cover letter artifact tabs.
* `src/core/candidate.py` — **modified** — one shared builder for the structure-editor payload (`all_sections` + `catalog`), used by the candidate and job structure routes.
* `src/ui/api/api_candidate.py` — **modified** — `GET /api/candidates/<id>/resume_structure` builds its payload through the shared helper, so the catalog carries the new format and flow fields.
* `src/core/tracker.py` — **modified** — job-scoped structure: effective-structure read (job current, else the candidate's current structure), structure save through the job catalog write, and job resume content prep filtered to the job's effective structure.
* `src/ui/api/api_jobs.py` — **modified** — new `GET /api/jobs/<id>/resume_structure` and `PUT /api/jobs/<id>/artifacts/job_resume_structure` routes.
* `src/core/builder.py` — **modified** — renders `line`-format sections; job resume HTML uses the job's effective structure (sections, order, titles, accent).
* `src/ui/frontend/src/components/SplitPanePage.tsx` — **new** — the split-pane layout: left/right panels with a user-draggable divider, for page or modal use.
* `src/ui/frontend/src/components/PrintPreview.tsx` — **new** — shows generated resume or cover letter HTML; full panel or click-to-open thumbnail; refetches when told a save landed.
* `src/ui/frontend/src/lib/printHtml.ts` — **new** — one shared helper to fetch base resume, job resume, or cover letter HTML and to open it as a blob in a new tab (replaces the two copies of that logic in the base page and the JAR modal).
* `src/ui/frontend/src/components/Modal.tsx` — **modified** — full-screen size for split-pane modals.
* `src/ui/frontend/src/components/ResumeContentEditor.tsx` — **new** — the dedicated resume editor (left panel) for base and job resumes: header controls, section rows, autosave, Compare to Base, saved callback.
* `src/ui/frontend/src/components/ResumeSectionRow.tsx` — **new** — one section row: collapsed read-only header and expanded editable header + content block.
* `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` — **modified** — job header text uses the section-header color.
* `src/ui/frontend/src/App.css` — **modified** — styles for the editor header, section rows, icons and tooltips, compare/new/removed blocks, thumbnails, and the experience job header color.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — becomes a split-pane page: resume editor left, preview right.
* `src/ui/frontend/src/components/JobArtifactEditModal.tsx` — **new** — stacked full-screen split-pane modal that edits one job artifact: job resume (resume editor + preview) or cover letter (existing cover letter fields + preview).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — Artifacts tab shows thumbnails for generated job resume and cover letter that open the edit modal, plus an Edit button for the job resume; drops the inline resume/cover editors and its structure-authoring state; Print Resume uses the shared helper.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — resume structure mode retired (structure-authoring props, `useCandidateResumeStructure`, `resume_content` branches, base-resume Generate escape); rubric/criteria and shapes modes unchanged.

## Technical scope

* `config.py`: add `line` to the resume structure body-format tuple. Add config mapping each body format to a display label and a tooltip description (settings and rules), and to the `BUILD_CONFIG["default_style"]["fonts"]` stack it previews in. Add a Hidden flow-state label alongside the existing page-break policy labels. Register a new `ARTIFACT_CONFIG` key for the job resume structure (`entity_type` job, `candidate_scoped`, `body_shape` `resume_structure`, `ingestion_owner` tracker). Add a preview-thumbnail field on the job resume and cover letter rows of the recommended-job artifact tabs config. Formats, labels, fonts, and thumbnail eligibility live here only; the frontend never hardcodes them.
* `candidate.py`: new public helper that turns a resolved structure into the editor payload (`sections`, `all_sections`, `accent_color`, `catalog` with the new fields), lifted out of the candidate route so both routes share one builder.
* `api_candidate.py`: modify the resume-structure GET handler to call the shared helper. Response shape stays a superset of today's.
* `tracker.py`: new function returning a job's effective resume structure (the job structure's current read, else the owning candidate's current structure). `save_job_artifact` accepts the job resume structure key and validates the body like the candidate structure write. `_prepare_job_resume_content` filters to the job's effective structure instead of the candidate's, so job-only sections survive save.
* `api_jobs.py`: new authenticated GET returning the shared editor payload for the job's effective structure. New authenticated PUT writing the job resume structure through `save_job_artifact`. Both return 404 for a missing job and 400 for an invalid body.
* `builder.py`: add a `line` branch to the resume-section body emitter that emits the text as a single line (one paragraph, newlines collapsed); empty bodies skip like the other formats. Modify `build_resume_from_job` and the accent resolution it uses so job resume HTML takes sections, order, titles, and accent from the job's effective structure.
* `SplitPanePage.tsx`: new component taking left and right content. Divider drag updates the left panel width in component state. Page mode fills the content area from the nav edge to the viewport's right edge; modal mode fills its container. Layout uses inline styles because the width is drag-driven state.
* `PrintPreview.tsx`: new component taking a target (base resume for a candidate, job resume, or cover letter for a job) and a refresh signal. It fetches HTML through `printHtml.ts` and shows it in an iframe, with the builder's error text when the fetch fails. A thumbnail mode renders it scaled down and non-interactive, with an `onClick`.
* `printHtml.ts`: new helpers. One fetches HTML for base (`/candidate/resume/base?candidate_id=`), job resume (`/candidate/resume/<job_id>`), or cover letter (`/candidate/cover/<job_id>`), returning the text or the error message. One opens HTML as a blob in a new tab with the existing popup-blocked handling.
* `Modal.tsx`: add a full-screen size option alongside `wide`. Existing callers are unchanged.
* `ResumeContentEditor.tsx`: new component taking a target, either the candidate base resume or one job's resume.
  * Loads the body (candidate GET for `base_resume`, or job GET for `job_resume`) and the structure payload (candidate or job structure GET).
  * Renders the header: search, Add Section, accent swatches from `ui_config`, Compare to Base (job only), and Print via `printHtml.ts`.
  * Renders `ResumeSectionRow`s filtered by search, with up/down, drag reorder, and delete.
  * Saves on field exit and on any structure change. Base saves body and structure in one candidate `/data` PUT. Job saves the `job_resume` PUT plus the `job_resume_structure` PUT.
  * Calls a saved callback after each successful save.
  * Compare to Base fetches the candidate's current base resume and base structure, then derives the differs / NEW SECTION / SECTION REMOVED states by section id. Add re-inserts the base row and its base content into the job structure and body, then saves.
* `ResumeSectionRow.tsx`: new component for one structure row and its body.
  * Collapsed: title, a one-line value preview in the format's catalog font, flow icon + tooltip, format label + tooltip, up/down, drag handle, and delete with confirmation.
  * Expanded: label input, format select, and flow-type select (Hidden maps to `enabled=false`; the other three set `enabled=true` and `page_break_policy`). Also up/down, delete, and Job Edit (base only).
  * Content block: a single-line input for `line`, a text area otherwise, and `ExperienceJobsEditor` for experience.
  * Fires field-exit callbacks. Renders the compare / NEW SECTION blocks when given them.
* `ExperienceJobsEditor.tsx`: modify the job header markup/class so its text takes the section-header color.
* `App.css`: new rules for the editor header, section rows, collapsed line, icons, tooltips, compare/new/removed blocks, thumbnails, and experience job header color. Remove rules used only by the retired structure-authoring header.
* `ArtifactsBaseResumeContent.tsx`: rewrite to render `SplitPanePage` (page mode) with `ResumeContentEditor` (base) on the left and `PrintPreview` (base) on the right. The preview refreshes on the editor's saved callback. The accent bar, `ArtifactEditor`, and Generate are removed from this page.
* `JobArtifactEditModal.tsx`: new stacked, full-screen `Modal` for one job artifact.
  * Job resume: `SplitPanePage` (modal mode) with `ResumeContentEditor` (job) and `PrintPreview` (job resume).
  * Cover letter: `ArtifactEditor` (existing `cover_letter` shapes + job persistence, unchanged) and `PrintPreview` (cover), refreshing on its `onSaved`.
  * Closing it notifies the parent so the report reloads.
* `JobAnalysisReportModal.tsx`: on the populated Artifacts pane, render `PrintPreview` thumbnails for tabs flagged for thumbnails whose artifact has content, in place of their inline editors. A thumbnail click opens `JobArtifactEditModal` for that artifact. Add an Edit button on the job resume section that opens the same modal. Remove the candidate-structure state and handlers. Print Resume uses `printHtml.ts` with no structure persist. Reload on edit-modal close.
* `ArtifactEditor.tsx`: remove the resume structure mode. That covers the structure-authoring props and branches, `useCandidateResumeStructure`, the `resume_content` structure fetches, and the base-resume unsupported-experience Generate escape. Rubric/criteria and shapes (cover letter, application responses) paths are unchanged.

## Architectural definition

**Patterns to reuse**

* [`patt.artifact.ui-consistency`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.ui-consistency.md>) — the `resume_content` body shape gets one shared editor (`ResumeContentEditor`) used by both base and job resumes; cover letter keeps `ArtifactEditor` shapes mode. **Amendment requested:** Implementation #2–#3 name `ArtifactEditor` as the shared path for `resume_content`. Per Susan's direction, `resume_content` moves to its own dedicated component (still one path per shape, no base-only fork). Approved — Decision 7.
* [`patt.artifact.read-current`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.read-current.md>) — the editor loads current bodies and structures through the candidate/job GETs. The job's effective structure is a current read (job, else candidate), with no blob fallback. Preview and thumbnails render through the builder routes, which current-read.
* [`patt.artifact.write-operative`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.write-operative.md>) — the job resume structure is a new catalog key written through `save_job_artifact` (retire+insert, identical no-op). Autosave goes through the existing PUT writes. The 60-second version cadence comes from AST-2043's coalescing, not from this epic.
* [`patt.artifact.manage-catalog`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.manage-catalog.md>) — the job resume structure key is registered in `ARTIFACT_CONFIG` before any reader or writer uses it.

**New patterns proposed**

* none. The split pane is a reusable layout component, not a multi-step arc.

**Applicable statutes**

* [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — the two new job structure routes each log one completion line.
* [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — the new routes log a caught exception once, at the handler.
* [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — the builder's `line` branch and job-structure resolution report through the existing debug contract.
* The frontend statutes (`stat.ui.*`) are still drafts, so none are cited.

## Acceptance criteria

 1. **Split pane spans the content area.** On Base Resume Content, the left panel's left edge equals the nav menu's right edge (0 when the nav is hidden). The right panel's right edge equals `window.innerWidth`. In the job edit modal, both panels together span the viewport width. *Fail:* a gap or page padding on either side.
 2. **Divider resizes.** Dragging the divider 100 px right grows the left panel by 100 px (±2) and shrinks the right panel by the same. *Fail:* no change, or only one panel changes.
 3. **Preview = print HTML.** The right panel's iframe content equals the body of `GET /candidate/resume/base?candidate_id=<id>` (base), `GET /candidate/resume/<jobId>` (job resume), or `GET /candidate/cover/<jobId>` (cover letter). *Fail:* different HTML, or no iframe.
 4. **Refresh on field exit, not per keystroke.** Typing 10 characters into a section body fires zero PUTs and zero HTML GETs. Leaving the field fires the save PUT(s), then exactly one HTML GET, and the new text appears in the preview. *Fail:* any request during typing, or no refresh after leaving.
 5. **No Save buttons.** Neither resume editor shows a Save, Cancel, or "Save sections" button, and `git grep -n "Save sections" -- src/ui/frontend/src` returns nothing. *Fail:* any of them present.
 6. **Generate gone from Base Resume Content.** The page shows no Generate/Regenerate button, and `ArtifactsBaseResumeContent.tsx` has no `craft_resume_base` reference. *Fail:* either present.
 7. **Search filters.** Typing a word that appears in exactly two sections' label or content (case-insensitive) leaves exactly those two rows visible. Clearing the box restores all rows. *Fail:* other rows visible, or matches hidden.
 8. **Add Section.** Clicking Add Section appends one expanded row at the bottom with the catalog's `new_extra_default_format`. After you give it a label and leave the field, the last `all_sections` entry from the matching structure GET (candidate or job) has that title. *Fail:* row elsewhere, wrong format, or not persisted.
 9. **Collapsed row content.** Each collapsed row shows `<title>: <value>` on one line, plus up/down arrows and (non-required only) delete. Its flow icon tooltip equals the catalog label for its state, and its format label tooltip equals the catalog description for its format. The value's computed `font-family` equals the catalog preview font for its format. *Fail:* any element missing, or text not from the catalog.
10. **Flow type persists and renders.** Choosing Hidden sets `enabled=false` in `all_sections`, and the section disappears from the preview. Choosing New page before sets `enabled=true` + `page_break_policy=page_break_before`. Hidden is not offered on required sections. *Fail:* wrong stored values, preview unchanged, or Hidden offered on a required section.
11. **Delete confirms.** Delete opens a confirmation. Cancelling keeps the row; confirming removes it from `all_sections` and the preview. Required sections show no delete. *Fail:* deletion without confirmation, or a delete control on a required section.
12. **Reorder.** Moving a section with an arrow or by dragging changes its `order` in `all_sections` and its position in the preview HTML. *Fail:* order unchanged in either.
13. **Line format end to end.** `line` is in the catalog's `body_formats`, and every format there today is still present. A Line section edits in a single-line input, and the preview shows its text as one line. *Fail:* a format removed, a multi-line editor, or the section skipped as "missing format".
14. **Format text is config-driven.** `git grep -nE "Word Cloud|Bullet List|Flow uninterrupted" -- src/ui/frontend/src` returns nothing; those strings come from the catalog payload. *Fail:* any hardcoded hit.
15. **Job structure is isolated.** On job A's resume, rename a section, change its format, and reorder it. Afterwards, `GET /api/candidates/<id>/resume_structure` and `GET /api/jobs/<B>/resume_structure` (job B, never edited) are unchanged, `GET /api/jobs/<A>/resume_structure` shows the edits, and job A's print HTML reflects them. *Fail:* the candidate or job B changes, or job A's HTML does not.
16. **Job inherits until edited.** For a job with no job resume structure row, `GET /api/jobs/<id>/resume_structure` → `all_sections` equals the candidate's, and no job structure artifact row exists for that job. *Fail:* the sections differ, or a row was written by the GET.
17. **Job-only section survives save.** Add a section on a job resume, give it content, and leave the field. `GET /api/jobs/<id>` shows that section's content in `job_resume`, and the print HTML includes it. *Fail:* the content is dropped by the save filter.
18. **Job accent.** Picking a swatch on job A's resume changes job A's print HTML accent and leaves the base resume HTML accent unchanged. *Fail:* either is wrong.
19. **Compare to Base.** Set up a job resume where one shared section differs from base, one section exists only on the job, and one base section was deleted from the job. With Compare on, the job shows exactly one read-only base block (under the differing section), one "NEW SECTION: Not found in base", and one "SECTION REMOVED: …" row with Add. Clicking Add restores that section with its base content in `GET /api/jobs/<id>/resume_structure` and in the job's `job_resume`. With Compare off, none of these appear, and the base resume page has no Compare toggle. *Fail:* any count wrong, Add not persisted, or a toggle on the base page.
20. **Print.** Print opens a new tab whose HTML equals the preview's. If the popup is blocked, the existing "Popup blocked" toast appears. *Fail:* same-tab navigation, or different HTML.
21. **Thumbnails open the edit modal.** On a job with a generated job resume and cover letter, the Artifacts tab shows two thumbnails and no inline resume/cover editors. Clicking either opens a stacked modal over the report with that artifact's split pane, and the job resume Edit button opens the resume modal. A job with neither generated shows no thumbnails. *Fail:* inline editors remain, thumbnails shown for empty artifacts, or the modal replaces the report rather than stacking.
22. **Experience header color.** In the expanded Experience section, each job header's computed `color` equals the section header's computed `color`. *Fail:* different colors.
23. **Resume mode gone from ArtifactEditor.** `git grep -nE "useCandidateResumeStructure|structureCatalog|onStructureSave" -- src/ui/frontend/src` returns nothing. Both resume surfaces render `ResumeContentEditor`. *Fail:* any hit, or a resume surface still on `ArtifactEditor`.

## Decisions (Susan, 2026-10-08)

1. Job-scoped structure, with NEW SECTION / SECTION REMOVED (+ Add) under Compare to Base.
2. The job resume editor is a stacked modal from an Edit button on the job modal. Resume and cover letter previews show as thumbnails on the Job Artifacts tab once generated, and clicking one opens the edit modal.
3. All formats stay; Line is added.
4. [AST-2043](https://linear.app/astralcareermatch/issue/AST-2043/artifact-edit-enhancements) is about the artifact lists, not resume content, so the resume editor should be a completely different component. [AST-2043](https://linear.app/astralcareermatch/issue/AST-2043/artifact-edit-enhancements) and [AST-2041](https://linear.app/astralcareermatch/issue/AST-2041/autosave-resume-artifacts-for-base-and-job-resumes) block this epic, which waits in Todo until they land.
5. Drop Generate. The Accent color swatches join the header with Add Section and Compare to Base.
6. Project: Astral Interface.
7. Approved (2026-10-08): amend `patt.artifact.ui-consistency` so `resume_content` uses the dedicated resume editor. "While resume IS an artifact, this is a specialized artifact necessitating a specialized UX." This epic dispatches against the amended pattern, and the amendment text lands as its own canon ticket.
8. The cover letter thumbnail opens a cover letter edit modal on the same split pane: the existing cover letter fields on the left, the cover letter preview on the right.
9. AST-2043 and AST-2041 are linked as blocking this epic.

## Open questions

none

## Proposed child tickets

#### 1!!: **Job-scoped structure, Line format, format/flow catalog - Ada**

Ships the whole backend: the job resume structure (catalog key, effective read, save, routes, builder use), the Line format in print HTML, and the catalog fields the UI needs for format labels/tooltips/fonts, the Hidden label, and thumbnail eligibility. Does not own any UI (#2–#4).
**Citations:** `patt.artifact.manage-catalog`, `patt.artifact.read-current`, `patt.artifact.write-operative`, `stat.logging.info.api`, `stat.logging.error`, `stat.logging.debug`.
**Scope:** `src/utils/config.py` — **modified** — `line` body format; format labels, tooltip descriptions, and preview fonts; Hidden flow label; new catalog key for the job resume structure; preview-thumbnail flag on the job resume and cover letter artifact tabs. `src/core/candidate.py` — **modified** — one shared builder for the structure-editor payload (`all_sections` + `catalog`), used by the candidate and job structure routes. `src/ui/api/api_candidate.py` — **modified** — `GET /api/candidates/<id>/resume_structure` builds its payload through the shared helper, so the catalog carries the new format and flow fields. `src/core/tracker.py` — **modified** — job-scoped structure: effective-structure read (job current, else the candidate's current structure), structure save through the job catalog write, and job resume content prep filtered to the job's effective structure. `src/ui/api/api_jobs.py` — **modified** — new `GET /api/jobs/<id>/resume_structure` and `PUT /api/jobs/<id>/artifacts/job_resume_structure` routes. `src/core/builder.py` — **modified** — renders `line`-format sections; job resume HTML uses the job's effective structure (sections, order, titles, accent).
Technical:

* `config.py`: add `line` to the resume structure body-format tuple. Add config mapping each body format to a display label and a tooltip description (settings and rules), and to the `BUILD_CONFIG["default_style"]["fonts"]` stack it previews in. Add a Hidden flow-state label alongside the existing page-break policy labels. Register a new `ARTIFACT_CONFIG` key for the job resume structure (`entity_type` job, `candidate_scoped`, `body_shape` `resume_structure`, `ingestion_owner` tracker). Add a preview-thumbnail field on the job resume and cover letter rows of the recommended-job artifact tabs config. Formats, labels, fonts, and thumbnail eligibility live here only; the frontend never hardcodes them.
* `candidate.py`: new public helper that turns a resolved structure into the editor payload (`sections`, `all_sections`, `accent_color`, `catalog` with the new fields), lifted out of the candidate route so both routes share one builder.
* `api_candidate.py`: modify the resume-structure GET handler to call the shared helper. Response shape stays a superset of today's.
* `tracker.py`: new function returning a job's effective resume structure (the job structure's current read, else the owning candidate's current structure). `save_job_artifact` accepts the job resume structure key and validates the body like the candidate structure write. `_prepare_job_resume_content` filters to the job's effective structure instead of the candidate's, so job-only sections survive save.
* `api_jobs.py`: new authenticated GET returning the shared editor payload for the job's effective structure. New authenticated PUT writing the job resume structure through `save_job_artifact`. Both return 404 for a missing job and 400 for an invalid body.
* `builder.py`: add a `line` branch to the resume-section body emitter that emits the text as a single line (one paragraph, newlines collapsed); empty bodies skip like the other formats. Modify `build_resume_from_job` and the accent resolution it uses so job resume HTML takes sections, order, titles, and accent from the job's effective structure.
  Estimate: 5

#### 2!!: **Split-pane layout, print preview/thumbnail, full-screen modal - Hedy**

Ships the reusable split pane with its draggable divider, the print preview that doubles as a thumbnail, one shared fetch/open helper for print HTML, and the full-screen modal size. Does not own the resume editor (#3) or wire any page or modal (#4).
**Citations:** `patt.artifact.read-current` (preview renders through the existing current-reading builder routes).
**Scope:** `src/ui/frontend/src/components/SplitPanePage.tsx` — **new** — the split-pane layout: left/right panels with a user-draggable divider, for page or modal use. `src/ui/frontend/src/components/PrintPreview.tsx` — **new** — shows generated resume or cover letter HTML; full panel or click-to-open thumbnail; refetches when told a save landed. `src/ui/frontend/src/lib/printHtml.ts` — **new** — one shared helper to fetch base resume, job resume, or cover letter HTML and to open it as a blob in a new tab (replaces the two copies of that logic in the base page and the JAR modal). `src/ui/frontend/src/components/Modal.tsx` — **modified** — full-screen size for split-pane modals.
Technical:

* `SplitPanePage.tsx`: new component taking left and right content. Divider drag updates the left panel width in component state. Page mode fills the content area from the nav edge to the viewport's right edge; modal mode fills its container. Layout uses inline styles because the width is drag-driven state.
* `PrintPreview.tsx`: new component taking a target (base resume for a candidate, job resume, or cover letter for a job) and a refresh signal. It fetches HTML through `printHtml.ts` and shows it in an iframe, with the builder's error text when the fetch fails. A thumbnail mode renders it scaled down and non-interactive, with an `onClick`.
* `printHtml.ts`: new helpers. One fetches HTML for base (`/candidate/resume/base?candidate_id=`), job resume (`/candidate/resume/<job_id>`), or cover letter (`/candidate/cover/<job_id>`), returning the text or the error message. One opens HTML as a blob in a new tab with the existing popup-blocked handling.
* `Modal.tsx`: add a full-screen size option alongside `wide`. Existing callers are unchanged.
  Estimate: 3

#### 3!: **Dedicated resume editor: section rows, search/add/swatches/compare, autosave - Katherine**

After #1 and #2. Ships `ResumeContentEditor` and `ResumeSectionRow` for both base and job resumes: collapsed/expanded rows, search, Add Section, swatches, drag reorder, delete confirm, Compare to Base (differs / NEW SECTION / SECTION REMOVED + Add), autosave on field exit, Print, and the saved callback. Does not own page/modal composition (#4).
**Citations:** `patt.artifact.ui-consistency` (as amended — Decision 7), `patt.artifact.read-current`, `patt.artifact.write-operative`.
**Scope:** `src/ui/frontend/src/components/ResumeContentEditor.tsx` — **new** — the dedicated resume editor (left panel) for base and job resumes: header controls, section rows, autosave, Compare to Base, saved callback. `src/ui/frontend/src/components/ResumeSectionRow.tsx` — **new** — one section row: collapsed read-only header and expanded editable header + content block. `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` — **modified** — job header text uses the section-header color. `src/ui/frontend/src/App.css` — **modified** — styles for the editor header, section rows, icons and tooltips, compare/new/removed blocks, thumbnails, and the experience job header color.
Technical:

* `ResumeContentEditor.tsx`: new component taking a target, either the candidate base resume or one job's resume.
  * Loads the body (candidate GET for `base_resume`, or job GET for `job_resume`) and the structure payload (candidate or job structure GET).
  * Renders the header: search, Add Section, accent swatches from `ui_config`, Compare to Base (job only), and Print via `printHtml.ts`.
  * Renders `ResumeSectionRow`s filtered by search, with up/down, drag reorder, and delete.
  * Saves on field exit and on any structure change. Base saves body and structure in one candidate `/data` PUT. Job saves the `job_resume` PUT plus the `job_resume_structure` PUT.
  * Calls a saved callback after each successful save.
  * Compare to Base fetches the candidate's current base resume and base structure, then derives the differs / NEW SECTION / SECTION REMOVED states by section id. Add re-inserts the base row and its base content into the job structure and body, then saves.
* `ResumeSectionRow.tsx`: new component for one structure row and its body.
  * Collapsed: title, a one-line value preview in the format's catalog font, flow icon + tooltip, format label + tooltip, up/down, drag handle, and delete with confirmation.
  * Expanded: label input, format select, and flow-type select (Hidden maps to `enabled=false`; the other three set `enabled=true` and `page_break_policy`). Also up/down, delete, and Job Edit (base only).
  * Content block: a single-line input for `line`, a text area otherwise, and `ExperienceJobsEditor` for experience.
  * Fires field-exit callbacks. Renders the compare / NEW SECTION blocks when given them.
* `ExperienceJobsEditor.tsx`: modify the job header markup/class so its text takes the section-header color.
* `App.css`: new rules for the editor header, section rows, collapsed line, icons, tooltips, compare/new/removed blocks, thumbnails, and experience job header color. Remove rules used only by the retired structure-authoring header.
  Estimate: 5

#### 4: **Wire base page, job edit modal, thumbnails; retire resume mode in ArtifactEditor - Ada**

After #2 and #3. Puts Base Resume Content on the split pane, adds the stacked job artifact edit modal (job resume and cover letter), puts thumbnails and the Edit button on the job's Artifacts tab, and removes the now-unused resume mode from `ArtifactEditor`. Does not own the editor internals (#3), the split pane/preview (#2), or the backend (#1).
**Citations:** `patt.artifact.ui-consistency` (as amended — Decision 7).
**Scope:** `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — becomes a split-pane page: resume editor left, preview right. `src/ui/frontend/src/components/JobArtifactEditModal.tsx` — **new** — stacked full-screen split-pane modal that edits one job artifact: job resume (resume editor + preview) or cover letter (existing cover letter fields + preview). `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — Artifacts tab shows thumbnails for generated job resume and cover letter that open the edit modal, plus an Edit button for the job resume; drops the inline resume/cover editors and its structure-authoring state; Print Resume uses the shared helper. `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — resume structure mode retired (structure-authoring props, `useCandidateResumeStructure`, `resume_content` branches, base-resume Generate escape); rubric/criteria and shapes modes unchanged.
Technical:

* `ArtifactsBaseResumeContent.tsx`: rewrite to render `SplitPanePage` (page mode) with `ResumeContentEditor` (base) on the left and `PrintPreview` (base) on the right. The preview refreshes on the editor's saved callback. The accent bar, `ArtifactEditor`, and Generate are removed from this page.
* `JobArtifactEditModal.tsx`: new stacked, full-screen `Modal` for one job artifact.
  * Job resume: `SplitPanePage` (modal mode) with `ResumeContentEditor` (job) and `PrintPreview` (job resume).
  * Cover letter: `ArtifactEditor` (existing `cover_letter` shapes + job persistence, unchanged) and `PrintPreview` (cover), refreshing on its `onSaved`.
  * Closing it notifies the parent so the report reloads.
* `JobAnalysisReportModal.tsx`: on the populated Artifacts pane, render `PrintPreview` thumbnails for tabs flagged for thumbnails whose artifact has content, in place of their inline editors. A thumbnail click opens `JobArtifactEditModal` for that artifact. Add an Edit button on the job resume section that opens the same modal. Remove the candidate-structure state and handlers. Print Resume uses `printHtml.ts` with no structure persist. Reload on edit-modal close.
* `ArtifactEditor.tsx`: remove the resume structure mode. That covers the structure-authoring props and branches, `useCandidateResumeStructure`, the `resume_content` structure fetches, and the base-resume unsupported-experience Generate escape. Rubric/criteria and shapes (cover letter, application responses) paths are unchanged.
  Estimate: 3

**New patterns:** none (the `patt.artifact.ui-consistency` amendment is a change to an existing pattern — Decision 7).

**Monolith check:** Functional scope N=13, children M=4, split by layer: backend (#1), layout + preview (#2), resume editor (#3), page/modal wiring (#4).

**Scope partition check:** all 18 Component scope files are claimed exactly once.

* #1: `config.py`, `candidate.py`, `api_candidate.py`, `tracker.py`, `api_jobs.py`, `builder.py`
* #2: `SplitPanePage.tsx`, `PrintPreview.tsx`, `printHtml.ts`, `Modal.tsx`
* #3: `ResumeContentEditor.tsx`, `ResumeSectionRow.tsx`, `ExperienceJobsEditor.tsx`, `App.css`
* #4: `ArtifactsBaseResumeContent.tsx`, `JobArtifactEditModal.tsx`, `JobAnalysisReportModal.tsx`, `ArtifactEditor.tsx`

---

## Original brief

Create a new page type for a split pane view.  The left panel (adjustable in width) will start at the left edge of the screen (or the right edge of nav menu if displayed), the right panel will end at the right edge of the screen.  A user-movable bar will divide the two panels to resize them.

The left panel will contain the resume content in editable text.

* Header above left side content sections:
  * Search box to find text, filter the resume content sections to those that match the search pattern
  * Add Section button (adds a new row to the bottom
  * (job resume only) Compare to Base toggle button (adds a read-only display of the original base content below the section (collapsed or not) where any section has been changed from the base.)
  * Print button (opens the preview blob in a new tab to be saved as PDF)
* Collapsed section Header (read-only)
  * <Section Name>: <current value for the section> with selected format font
  * up / down position arrow (click and drag if possible)
  * Single icon to indicate the section is hidden, the section inserts a new page before it, the section keeps together, or the section flows uninterrupted, with tooltip for each.
  * Label with tooltip to describe format of the section (Line, Prose, Word Cloud, Bullet List), where the tooltip describes the settings and rules for that format.
    * Add "Line" for single line of text.
  * Delete section button (with confirmation prompt)
* Expanded section state:
  * Header Row becomes editable: Section Label Edit Input box, Dropdown select style, dropdown select flow-type (hidden/page, etc.), position up/down, delete.
  * Content edit block, sized to 1 line for the Line format
  * Autosave, and version changes every 60 seconds
  * Experience: Same, but make the text for the individual experience headers use the same color as the section header.

Right Panel, no header: Print Preview

* Displays the generated blob that currently opens in a new tab
* Refreshes when edits are made, after the user leaves the input box (not letter-by-letter, but one field at a time).

This is a very rudimentary sketch of the desired layout where all sections are collapsed.  Rendered HTML is "floor to ceiling" formatted HTML, Resume Content has expandable sections.

```
|--------------------------------|-----------------------------------|
| Resume Content [s] [+] [b] [p] | <Rendered HTML>                   |
|--------------------------------|                                   |
| <label>: <preview> * & % ^ v x |                                   |
| <label>: <preview> @ & $ ^ v x |                                   |
| <label>: <preview> @ - $ ^ v x |                                   |
| <label>: <preview> @ - $ ^ v x |                                   |
|--------------------------------|-----------------------------------|
```

### Comments

#### chuckles — 2026-10-09T22:02:31.496Z
Filed as [AST-2115](https://linear.app/astralcareermatch/issue/AST-2115) at Discussion, assigned to you. Check the as-is and to-be there, then reassign it to Chuckles to start the fix.

#### chuckles — 2026-10-09T22:02:29.381Z
Filed as [AST-2114](https://linear.app/astralcareermatch/issue/AST-2114) at Discussion, assigned to you. Check the as-is and to-be there, then reassign it to Chuckles to start the fix.

#### susan — 2026-10-09T22:00:43.021Z
\[fix\]

When editing a job resume, the modal goes edge-to-edge.  This is great for experienced users, but I would like to have it pop up as more obviously "over" the navigation and content behind it so the user doesn't think they have navigated away.  Better for the modal to be 80% screen width for this one.

#### susan — 2026-10-09T21:52:05.282Z
\[fix\]

When searching, where patterns match within experience subelements, display only the subelements that match the pattern, so I would see "Core Competencies" and "Experience", but within "Experience" I would only see one or two of the sections that match the pattern.

#### chuckles — 2026-10-09T05:42:42.774Z
@susan The new worktree lock (team-chuckles `2a1a25b`/`eb7eddd`, from about 04:21 UTC) deadlocks every sub-chuck drone. The drone's own `datt_trace run` takes the lock on the epic worktree, as §2c says it should, and then the engineer spawn it launches inside that worktree waits on the same lock until the 45-minute timeout (exit 75).

- **AST-2046:** my AST-2084 build sat in `worktree-wait` behind its own drone. I killed it and relaunched just that drone with the documented escape hatch `CHUCKLES_WORKTREE_LOCK=0`, so its spawns run one at a time like before today.
- **Still stuck:** AST-2073's Ada `test-child` on AST-2086 is in the same deadlock, and it's holding `Active/ada` while it waits. That blocks Ada's engineer slot for [AST-2084](https://linear.app/astralcareermatch/issue/AST-2084) and the fix lane's AST-2099 until it times out (around 06:16 UTC). After that it will probably deadlock again on retry. I haven't touched AST-2073, since it isn't my epic.
- **Suggested fix:** in `_hold_worktree`, skip the lock when `--role sub-chuck`, or let nested spawns inherit the parent's hold.

#### chuckles — 2026-10-09T04:02:49.580Z
[AST-2083](https://linear.app/astralcareermatch/issue/AST-2083) is gated on [AST-2107](https://linear.app/astralcareermatch/issue/AST-2107): Betty's merge-tests re-delivery needs @susan to pick a git-rule exception. AST-2084 waits behind AST-2083.

#### chuckles — 2026-10-09T03:37:09.294Z
AST-2083 blocked — test delivery 6af214f93 conflicts with origin/dev in tests/component/utils/test_config.py; recalling @Betty White to re-deliver merge-tests on current dev.

#### chuckles — 2026-10-09T03:02:00.911Z
AST-2083 publish ref STALE(dev+72) — @katherine refreshing sub/AST-2046/AST-2083-resume-editor (merge origin/dev + origin/ftr, republish) before build-child.

#### chuckles — 2026-10-08T20:18:03.773Z
@susan Holding dispatch. [AST-2043](https://linear.app/astralcareermatch/issue/AST-2043) (Discussion) and [AST-2041](https://linear.app/astralcareermatch/issue/AST-2041) (In Progress) still block this, so it stays Todo with me as assignee, as you asked. One catch: the datt watcher only skips parents blocked by `Task`-labeled gate tickets. It doesn't treat ordinary `blocks` links as a hold. So while this sits at Todo assigned to me, the watcher will keep spawning datt on it, and each run will just stop here again. If you don't want that, park it on your own assignee until the blockers land.

#### chuckles — 2026-10-08T19:29:52.773Z
@susan

1. **Canon amendment.** `patt.artifact.ui-consistency` names `ArtifactEditor` as the shared editor for `resume_content`. Moving resume editing to its own component, per your answer on AST-2043, means amending that pattern to name the dedicated resume editor. It would still be one path per shape, used by both base and job. Canon says amendments land as their own tickets. Do you approve the amendment now, so this epic can dispatch against it, with the amendment filed as a sibling canon ticket? Or should the canon ticket land first?
2. **Cover letter thumbnail target.** My default: clicking the cover letter thumbnail opens a cover letter edit modal on the same split pane, with the existing cover letter fields on the left and the cover letter preview on the right. Or should it open something else, such as the resume modal or just Print?
3. **Blocking links.** My Linear access can't set issue relations. Please add [AST-2043](https://linear.app/astralcareermatch/issue/AST-2043) and [AST-2041](https://linear.app/astralcareermatch/issue/AST-2041) as blocking AST-2046.

#### chuckles — 2026-10-08T19:03:14.631Z
@susan

1. **Job resume structure: shared or per job?** Today a job resume uses the candidate's one resume structure. That means renaming, reformatting, hiding, or reordering a section on a job resume also changes the base resume and every other job. Should it stay shared (my default, no schema change)? Or should each job get its own structure? That would add a job-scoped catalog key and builder changes, which is about one more child.
2. **Where should the job resume page live?** My default is a new page at `/jobs/resume/<jobId>`, opened by an "Edit resume" button that replaces the inline editor in the Job Analysis Report's Job Resume section. The alternatives are keeping the inline editor in the report too, or opening the split pane inside the report modal.
3. **Which formats stay?** You named Line, Prose, Word Cloud, and Bullet List. Today there are also Dual Column, Indented Bold Single, and Experience Detail (which is locked to Experience). My default is to keep all six and add Line. Or should we retire the ones you didn't name?
4. **Order relative to AST-2043 and AST-2041.** [AST-2043](https://linear.app/astralcareermatch/issue/AST-2043) owns the 60-second version coalescing, and it also edits `ArtifactEditor`. Without it, saving every time you leave a field would write a new version per field. I recommend landing AST-2043 first and dispatching this epic after it. [AST-2041](https://linear.app/astralcareermatch/issue/AST-2041) (autosave on the resume editors) is fully covered here. Should I fold it into this epic and cancel it?
5. **Current controls the brief doesn't mention.** These are Generate/Regenerate, the Accent color swatches, and the per-section Job Edit checkbox. My default is to keep all three: Generate and Accent in the left header, Job Edit in the expanded header row. Should any of them go?
6. **Linear project.** This ticket has no project. Should it go in Astral Artifacts?

---

_Implementation detail may live in git history on `origin/dev`._
