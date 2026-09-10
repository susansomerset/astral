# AST-1459 — Resume editor is not working properly

<!-- linear-archive: AST-1459 archived 2026-09-09 -->

## Linear archive (AST-1459)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1459/resume-editor-is-not-working-properly  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** None / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators use structure-driven resume editors on **Base Resume Content** and in the **Job Analysis Report** (Job Resume tab) to view and edit persisted section text before Save. Susan reports those surfaces **render section chrome** (collapsible panels / structure headers) but **do not present editable section body text** — persisted `base_resume` / `resume_content` content is missing, non-interactive, or otherwise unusable. Susan confirmed the failure on **both** Base Resume Content and JAR Job Resume (no specific candidate/job id for repro). This epic restores the end-to-end edit loop on every `useCandidateResumeStructure` **ArtifactEditor** instance without regressing AST-1323 structure authoring on headers, AST-1351 experience job-array editing, or AST-1410 in-place Cancel reload.

## Functional scope

* **Load persisted section bodies.** When a candidate or job already has resume artifact data, each enabled structure section panel shows that section's saved text (or job-array UI for Experience) on first expand — not blank placeholders when data exists server-side.
* **Edit section bodies in structure mode.** Operators can type in prose section textareas and in Experience job-array fields while structure authoring controls remain on panel headers; tab add/remove/rename stays out of scope (structure catalog owns section list).
* **Save edits on both persistence paths.** Base Resume Content Save writes `artifacts.base_resume`; JAR Job Resume Save writes `job_data.artifacts.resume_content` via existing job persistence PUT — edited bodies round-trip after reload.
* **No regression on adjacent resume UX.** Generate/Regenerate, Print, structure header authoring (name/format/enabled/Job Edit/reorder), and accent color bar on Base Resume Content continue to behave as on current `origin/dev`.

## Component scope

* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — structure-mode load/hydration, editability gating, and panel body rendering for resume sections.
* `src/ui/frontend/src/components/LabeledTextArea.tsx` — **modified** — only if the root cause requires explicit disabled/readOnly wiring for structure-mode bodies (prefer fixing gating in ArtifactEditor).
* `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` — **modified** — only if Experience sections share the same failure mode as prose sections.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — only if props/effects passed into ArtifactEditor contribute to empty or non-editable bodies (e.g. structureSections vs allSections mismatch).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — only if JAR-specific structure fetch or jobPersistence wiring blocks editor hydration.
* `src/ui/frontend/src/App.css` — **modified** — only if CSS blocks interaction or hides `.side-tab-textarea` / `.collapsible-panel-body` content in structure mode.
* `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — **modified** — lock structure-mode body display + edit + save for candidate and job persistence paths.
* `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` — **modified** — routed-page regression if page-level wiring is touched.
* `docs/test-bible/frontend/components.md` — **modified** — manifest row update if test scope changes (Betty at qa-child).

## Technical scope

* **ArtifactEditor.tsx** — trace structure-mode (`useCandidateResumeStructure`) load effects (`fixedFields` / `structureSections` gate, candidate GET vs job GET) through `mapFixedFieldsFromRaw` / `applyJobArtifactResponse` into `tabs[].content`; fix any race or guard that leaves panels rendered with empty `content` or blocks `updateTab` / Save while headers render; reconcile `editable = !shapesKey && !structureMode` so structure mode disables tab chrome edits but **not** section body editing or Save when `fixedFields || jobPersistence`.
* **LabeledTextArea.tsx** — if bodies are present but non-interactive, ensure structure-mode panels pass through `onChange` and do not set `disabled` unless Experience is explicitly unsupported.
* **ExperienceJobsEditor.tsx** — if Experience panels show structure headers but job-array fields are empty or read-only, align parse/hydrate path with `parseExperienceJobs` + persisted blob shape.
* **ArtifactsBaseResumeContent.tsx** — if enabled-section tabs diverge from `artifacts.base_resume` keys, align `structureSections` prop with hydrated enabled ids without dropping extras already on the artifact.
* **JobAnalysisReportModal.tsx** — if JAR Job Resume alone fails, align `structureSections` fetch timing with `jobPersistence` load so ArtifactEditor does not render bodies before `fixedFields` exist.
* **App.css** — remove or narrow any rule that sets `pointer-events: none` or zero effective height on structure-mode textarea bodies inside `.collapsible-panel-body`.
* **test_ArtifactEditor.test.tsx** — extend or fix AST-553 / AST-1410 cases so expanded structure-mode panels assert non-empty `displayValue` from persisted mocks and successful edit→Save PUT; add Base Resume structure-authoring case if header+body combo is the repro shape.
* **test_ArtifactsBaseResumeContent.test.tsx** — assert expanded section shows saved base_resume text when structure GET + candidate GET both return data (page-level gate if touched).

## Architectural definition

* **Patterns to reuse**
  * [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — existing candidate/job GET + artifact PUT routes; no new API surface unless load bug is server-side (out of scope unless repro proves otherwise).
  * [`pattern.ui.in-place-live-refresh`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.in-place-live-refresh.md>) — [AST-1410](https://linear.app/astralcareermatch/issue/AST-1410/apply-silent-refetch-on-remaining-loading-gate-surfaces-page-refreshes) Cancel re-GET without full reload must remain intact on job persistence path.
  * [`pattern.ui.dirty-leave-save-then-navigate`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.dirty-leave-save-then-navigate.md>) — explicit Save/Cancel on fixed-field and job-persistence modes; do not rely on structure-mode autosave (disabled when `editable` is false).
* **New patterns proposed** — none.
* **Applicable statutes**
  * [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — resume structure catalog and experience field labels come from config/API, not hardcoded React allowlists.
  * [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — fix the shared editor; do not expand into craft-base prompts, builder emit, or new artifact shapes.
  * [`astral.standards.no-cross-contamination`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md>) — frontend-only unless repro proves API hydration gap.
  * [`astral.git.engineer-test-tree-ban`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>) — Betty owns test-tree manifest updates at qa-child.

## Acceptance criteria

1. **Base Resume Content** — with a candidate that has non-empty `artifacts.base_resume` section values, expanding each enabled structure section shows the saved text (or populated Experience job-array UI) and allows editing; Save persists changes visible after page reload.
2. **JAR Job Resume** — with a recommended job that has non-empty `job_data.artifacts.resume_content`, expanding structure sections shows saved text, allows editing, and Save persists via job artifact PUT visible after modal re-open.
3. **Structure headers unchanged** — AST-1323 header authoring controls (name, format, Enabled, Job Edit, Up/Down, Remove) still render and Save sections still writes `resume_structure` independently of body Save.
4. **Experience path** — valid job-array Experience sections remain editable via ExperienceJobsEditor; unsupported legacy shapes still show the configured unsupported message (not silent blank panels).
5. **Component tests** — `test_ArtifactEditor.test.tsx` structure-mode + jobPersistence cases pass on publish ref; any new repro case added for the reported failure shape is green.
6. **No backend scope creep** — if the fix is frontend-only, no changes under `src/core/` or `src/ui/api/` unless Susan confirms a separate API hydration bug.

## Open questions

none

## Proposed child tickets

**Monolith check:** three functional capabilities (load, edit, save) share one root component and one hydration/editability gate — single vertical slice intentional.

#### 1: **Restore structure-mode resume section body edit loop - Ada**

Delivers loaded, editable, savable section bodies on Base Resume Content and JAR Job Resume through shared ArtifactEditor structure mode. Does **not** own craft-base generation, Print HTML, builder emit, or resume_structure catalog schema changes.

**Citations:** `pattern.ui.admin-endpoint`, `pattern.ui.in-place-live-refresh`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`.

**Scope:** `ArtifactEditor.tsx` (structure-mode load through `tabs[].content`, body edit gating, Save payload); conditional touch `LabeledTextArea.tsx`, `ExperienceJobsEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`, `App.css` only if needed for the repro; `test_ArtifactEditor.test.tsx` + `test_ArtifactsBaseResumeContent.test.tsx` if page wiring touched.

**Estimate: 3**

---

## Original brief

Resumes render but don't have the editable text.

### Comments

#### chuckles — 2026-08-25T19:08:30.132Z
AST-1480 REVIEW — merge-child blocked; recalling Betty for duplicate merge-tests(AST-1480).

#### chuckles — 2026-08-25T19:00:43.228Z
AST-1480 REVIEW — Radia fix-now: bodiesEditable locks rubric free-form bodies; Ada resolve-child.

#### chuckles — 2026-08-25T18:32:54.110Z
@susan

Dispatch blocked — what's missing:

* **Linear project** on AST-1459 is unset. Assign a project (likely **Astral Artifacts**) so children inherit it, then move to **Todo** and assign **Chuckles** to re-dispatch.

#### chuckles — 2026-08-24T21:59:38.017Z
@susan

1. Which surface did you hit first — **Artifacts → Base Resume Content**, **JAR → Job Resume tab**, or both — and do you have a candidate/job id that reproduces empty/non-editable bodies?

---

_Implementation detail may live in git history on `origin/dev`._
