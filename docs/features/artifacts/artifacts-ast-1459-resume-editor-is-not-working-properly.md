# AST-1459 — Resume editor is not working properly
**Component:** artifacts  
**Children:** AST-1480  
**Linear archived:** AST-1459 2026-09-09; AST-1480 2026-09-09

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-25 11:40 | AST-1480 | docs | `9ca353577` | docs(AST-1480): plan — restore structure-mode resume body edit loop |
| 2026-08-25 11:44 | AST-1480 | docs | `8940406b2` | docs(AST-1480): Joan validate — APPROVED |
| 2026-08-25 11:50 | AST-1480 | docs | `1ca41eaa5` | docs(AST-1480): review stub — Code Complete handoff |
| 2026-08-25 11:50 | AST-1480 | code | `b16a93d36` | code(AST-1480): restore structure-mode body hydrate and edit |
| 2026-08-25 12:00 | AST-1480 | docs | `d928a796d` | docs(AST-1480): Radia review — FIX-NOW bodiesEditable |
| 2026-08-25 12:02 | AST-1480 | resolve | `56359afb6` | resolve(AST-1480): — findings addressed |
| 2026-08-25 12:07 | AST-1480 | resolve | `506ecb1ec` | resolve(AST-1480): — clean |
| 2026-08-25 12:11 | AST-1480 | test | `93d9ebd6a` | test(AST-1480): structure-mode + rubric free-form body edit coverage |
| 2026-08-25 12:11 | AST-1480 | merge-tests | `eaed624f4` | merge-tests(AST-1480): origin/tests 93d9ebd6a7dd41d354d7dc3e224699d29836de45 |
| 2026-08-25 17:39 | AST-1459 | docs | `2e4122d3c` | docs(AST-1459): mirror epic registry Threads |
| 2026-09-09 17:57 | AST-1480 | docs | `be2bc6ea2` | docs(AST-1480): archive Linear issue content |
| 2026-09-09 18:06 | AST-1459 | docs | `71b8f9cd3` | docs(AST-1459): archive Linear issue content |

_`ast-1480-…md` also carried an appended `## Bug: AST-1490 — Print Resume contact-only after section reorder` section whose real Linear parent is AST-1483 — a different, later epic in this same family (planned separately in this consolidation, not part of AST-1459). That content has been left untouched in place for that family's own archive and is not reproduced here; a pointer to it was saved to the session scratchpad._

## Epic — AST-1459
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1459/resume-editor-is-not-working-properly · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: None / 3 · Blocked by / blocks / related: —_

### Purpose

Operators use structure-driven resume editors on Base Resume Content and in the Job Analysis Report (Job Resume tab) to view and edit persisted section text before Save. Susan reports those surfaces render section chrome (collapsible panels / structure headers) but do not present editable section body text — persisted `base_resume` / `resume_content` content is missing, non-interactive, or otherwise unusable. Susan confirmed the failure on both Base Resume Content and JAR Job Resume (no specific candidate/job id for repro). This epic restores the end-to-end edit loop on every `useCandidateResumeStructure` ArtifactEditor instance without regressing AST-1323 structure authoring on headers, AST-1351 experience job-array editing, or AST-1410 in-place Cancel reload.

### Functional scope

* **Load persisted section bodies.** When a candidate or job already has resume artifact data, each enabled structure section panel shows that section's saved text (or job-array UI for Experience) on first expand — not blank placeholders when data exists server-side.
* **Edit section bodies in structure mode.** Operators can type in prose section textareas and in Experience job-array fields while structure authoring controls remain on panel headers; tab add/remove/rename stays out of scope (structure catalog owns section list).
* **Save edits on both persistence paths.** Base Resume Content Save writes `artifacts.base_resume`; JAR Job Resume Save writes `job_data.artifacts.resume_content` via existing job persistence PUT — edited bodies round-trip after reload.
* **No regression on adjacent resume UX.** Generate/Regenerate, Print, structure header authoring (name/format/enabled/Job Edit/reorder), and accent color bar on Base Resume Content continue to behave as on current `origin/dev`.

### Architectural definition

* **Patterns to reuse** — `pattern.ui.admin-endpoint` (existing candidate/job GET + artifact PUT routes; no new API surface unless load bug is server-side); `pattern.ui.in-place-live-refresh` (AST-1410 Cancel re-GET without full reload must remain intact on job persistence path); `pattern.ui.dirty-leave-save-then-navigate` (explicit Save/Cancel on fixed-field and job-persistence modes; do not rely on structure-mode autosave).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.git.engineer-test-tree-ban`.

### Acceptance criteria

1. **Base Resume Content** — with a candidate that has non-empty `artifacts.base_resume` section values, expanding each enabled structure section shows the saved text (or populated Experience job-array UI) and allows editing; Save persists changes visible after page reload.
2. **JAR Job Resume** — with a recommended job that has non-empty `job_data.artifacts.resume_content`, expanding structure sections shows saved text, allows editing, and Save persists via job artifact PUT visible after modal re-open.
3. **Structure headers unchanged** — AST-1323 header authoring controls still render and Save sections still writes `resume_structure` independently of body Save.
4. **Experience path** — valid job-array Experience sections remain editable via ExperienceJobsEditor; unsupported legacy shapes still show the configured unsupported message.
5. **Component tests** — `test_ArtifactEditor.test.tsx` structure-mode + jobPersistence cases pass on publish ref.
6. **No backend scope creep** — if the fix is frontend-only, no changes under `src/core/` or `src/ui/api/` unless Susan confirms a separate API hydration bug.

### Open questions

none

### Proposed child tickets

**1: Restore structure-mode resume section body edit loop — Ada** — Delivers loaded, editable, savable section bodies on Base Resume Content and JAR Job Resume through shared ArtifactEditor structure mode. Does **not** own craft-base generation, Print HTML, builder emit, or resume_structure catalog schema changes.
**Citations:** `pattern.ui.admin-endpoint`, `pattern.ui.in-place-live-refresh`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`.
**Scope:** `ArtifactEditor.tsx` (structure-mode load through `tabs[].content`, body edit gating, Save payload); conditional touch of `LabeledTextArea.tsx`, `ExperienceJobsEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`, `App.css` only if needed for the repro.
**Estimate: 3**

Monolith check: three functional capabilities (load, edit, save) share one root component and one hydration/editability gate — single vertical slice intentional.

### Original brief

Resumes render but don't have the editable text.

#### Comments

##### chuckles — 2026-08-24T21:59:38.017Z
@susan

1. Which surface did you hit first — **Artifacts → Base Resume Content**, **JAR → Job Resume tab**, or both — and do you have a candidate/job id that reproduces empty/non-editable bodies?

##### chuckles — 2026-08-25T18:32:54.110Z
@susan

Dispatch blocked — what's missing:

* **Linear project** on AST-1459 is unset. Assign a project (likely **Astral Artifacts**) so children inherit it, then move to **Todo** and assign **Chuckles** to re-dispatch.

##### chuckles — 2026-08-25T19:00:43.228Z
AST-1480 REVIEW — Radia fix-now: bodiesEditable locks rubric free-form bodies; Ada resolve-child.

##### chuckles — 2026-08-25T19:08:30.132Z
AST-1480 REVIEW — merge-child blocked; recalling Betty for duplicate merge-tests(AST-1480).

### Files changed (plan vs actual)

_No direct product commit trail on the parent — the epic worktree carries only the epic-registry Threads mirror commit and the `docs(AST-1459)` archive commit. Implementation landed entirely via the sub-issue below._

## Sub-issues

### AST-1480 — Restore structure-mode resume section body edit loop
_Archived: 2026-09-09 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1480/restore-structure-mode-resume-section-body-edit-loop-resume-editor-is · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1459_

#### What this implements

Delivers loaded, editable, savable section bodies on Base Resume Content and JAR Job Resume through shared ArtifactEditor structure mode. Does **not** own craft-base generation, Print HTML, builder emit, or resume_structure catalog schema changes.

#### Acceptance criteria

- [X] 1. Base Resume Content — expanding each enabled structure section shows saved text and allows editing; Save persists visible after page reload.
- [X] 2. JAR Job Resume — expanding structure sections shows saved text, allows editing, Save persists via job artifact PUT visible after modal re-open.
- [X] 3. Structure headers unchanged — AST-1323 header authoring controls still render; Save sections stays independent of body Save.
- [X] 4. Experience path — valid job-array Experience sections remain editable via ExperienceJobsEditor; unsupported legacy shapes still show the unsupported message.
- [X] 5. Component tests — structure-mode + jobPersistence cases pass; any new repro case is green.
- [X] 6. No backend scope creep unless Susan confirms a separate API hydration bug.

#### Boundaries

Does not own craft-base generation, Print HTML, builder emit, or resume_structure catalog schema changes.

#### Explicit scope gate

Required: `ArtifactEditor.tsx` — structure-mode load through `tabs[].content`, body edit gating, Save payload. Conditional (only if repro needs them): `LabeledTextArea.tsx`, `ExperienceJobsEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`, `App.css`. Tests (Betty owns tree): `test_ArtifactEditor.test.tsx`, `test_ArtifactsBaseResumeContent.test.tsx` if page wiring touched — engineer does not edit `tests/` or bible at build-child. Stages must not invent `src/core/` or `src/ui/api/` work unless Stage 1 proves an API hydration bug — then stop and comment on the parent (AC6 / no-cross-contamination).

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `ArtifactEditor.tsx` | Split structure-mode tab-chrome vs section-body editability; fix structure-mode load guards/races so `tabs[].content` hydrates from candidate/job artifact blobs; keep Save for `fixedFields`/`jobPersistence`; preserve Experience unsupported path | ui |
| `LabeledTextArea.tsx` | Only if bodies hydrate but stay non-interactive for a reason owned by this component | ui (conditional) |
| `ExperienceJobsEditor.tsx` | Only if Experience panels share the same empty/read-only failure after prose sections are fixed | ui (conditional) |
| `ArtifactsBaseResumeContent.tsx` | Only if `structureSections`/`allSections`/`handleStructureRowsChange` contributes to empty or non-editable bodies | ui (conditional) |
| `JobAnalysisReportModal.tsx` | Only if JAR-only timing blocks hydration after the ArtifactEditor fix | ui (conditional) |
| `App.css` | Only if a rule blocks interaction or hides body content in structure mode | ui (conditional) |

**Out of scope:** craft-base generation, Print HTML, builder emit, `resume_structure` catalog schema, new API routes, tab add/remove/rename chrome in structure mode.

#### Stage 1 — Diagnose, then split chrome vs body editability, then fix hydration races

**1.1 Diagnosis (mandatory before fixing):** trace `useCandidateResumeStructure` → `structureMode` → `structureSections` effect → `resume_structure` fetch → `shapeFields`/`fixedFields`; confirm candidate/job load gates both early-return when `(shapesKey || structureMode) && !fixedFields` and re-run once `fixedFields` is set, calling `applyCandidateArtifactResponse`/`applyJobArtifactResponse` → `mapFixedFieldsFromRaw` → `tabs[].content`; confirm the existing `editable = !shapesKey && !structureMode` correctly disables tab chrome/autosave while prose `LabeledTextArea` still receives `onChange`. The build agent must identify which failure mode is live — (A) empty `tabs[].content` after load, (B) body controls non-interactive, (C) Save missing/broken, or (D) page/CSS outside this file — then fix (A)–(C) here; (D) goes to Stage 2.

⚠️ **Decision:** prefer fixing shared gating/hydration inside `ArtifactEditor.tsx`; do not add a new prop from pages for body editability unless Stage 1 cannot restore both surfaces.

**1.2 Split chrome from body editability:** keep structure mode disabling tab chrome (rename, add criterion, remove, reorder, rubric code/importance) via a clearly named flag derived from the current `editable` meaning (`tabChromeEditable = !shapesKey && !structureMode`); introduce an explicit body affordance for structure/shapes/job-fixed-field modes (`bodiesEditable = !!(fixedFields || jobPersistence) && !inReview`) and wire prose `LabeledTextArea` and Experience `ExperienceJobsEditor` `onChange` through it, disabling only the existing unsupported-experience path, never happy-path bodies in structure mode. Autosave stays gated on tab-chrome/`editable` semantics — structure mode keeps explicit Save, not autosave. Save/Cancel header branch continues showing when `fixedFields || inReview || jobPersistence`.

**1.3 Fix hydration races/guards:** fix `mapFixedFieldsFromRaw`/`sectionValueToTabContent` mapping if it drops persisted values for structure keys; fix effect dependencies/guards if structure-mode load returns early forever or remounts with empty tabs after `structureSections` updates (never clear `tabs` to empty placeholders after a successful hydrate when only structure header metadata changed); preserve AST-1410 Cancel re-GET without full page reload on both paths; preserve Experience (`type: "experience_jobs"` on the experience `shapeFields` key; valid arrays → `ExperienceJobsEditor`; parse failure → unsupported message + disabled raw textarea, Save still aborts with that message).

**1.4 Regression checklist:** structure mode must still not call `/api/shapes/candidates` when `useCandidateResumeStructure` is set; still show AST-1323 header controls with Save sections separate from content Save; expand-one policy for non-rubric rails must still work (content present in the DOM even while `hidden` before Expand).

#### Stage 2 — Conditional page/CSS/child-component wiring (skip if Stage 1 restores both ACs)

Skip entirely (with a Linear stage comment stating "Stage 2 skipped — ArtifactEditor-only") when Stage 1 alone satisfies both ACs — do not touch conditional files "for cleanliness." If a gap remained, apply only the matching branch (`ArtifactsBaseResumeContent.tsx` tab-key alignment, `JobAnalysisReportModal.tsx` fetch/mount timing, `LabeledTextArea.tsx`/`ExperienceJobsEditor.tsx` forced-disabled/dropped-`onChange`, or `App.css` interaction-blocking rule). If the gap turned out to be server-side, stop and comment on the parent with the 🛑 Stage-blocked format rather than inventing API changes.

#### Plan review — Joan (PROCEED)

**discuss** — `pattern.ui.in-place-live-refresh` is cited under "Patterns to reuse" while its catalog entry is still `status: proposed`, not approved; non-blocking since Stage 1.3 explicitly preserves the AST-1410 Cancel re-GET shape and invents no new refresh semantics — optional Archie approval or hygiene swap to the AST-1410 canonical ref later. **acceptable** — the Files Changed table lists `tests/component/...` rows as "modified" even though the engineer is barred from touching `tests/` at build-child; correct for this workflow, Betty owns the test tree at qa-child and Stage 3 names the failure mode (A/B/C/D) so she can target coverage.

#### Review (build stub)

Built: Stage 1 only in `ArtifactEditor.tsx` — diagnosis confirmed **(A)** empty/stale bodies from label-churn re-GET + weak dict coerce, plus **(B)** chrome-vs-body edit split needed. Stage 2 skipped (no page/CSS/LabeledTextArea/ExperienceJobsEditor edits) — frontend-only, satisfying AC6.

#### Radia review — code-rubric.v1, FIX-NOW → resolved

Full 65-statute active-set sweep: all conforms/not-applicable except one fix-now. Plan adherence otherwise confirmed: chrome/body split, `fixedFieldKeys` load guards, label-only label-sync effect, dict-coerce hardening, and a `job_resume` → `resume_content` sibling overlay for JAR all delivered exactly per plan; Stage 2 correctly skipped.

**fix-now — `bodiesEditable` excluded rubric/free-form mode, a real functional regression.** `bodiesEditable = !!(fixedFields || jobPersistence) && !inReview` did **not** cover rubric/free-form mode: when `fixedFields` is null and `jobPersistence` is absent (e.g. `artifactKey="rubric"`, `joblist_rubric`, criteria pages), `bodiesEditable` was `false` while `tabChromeEditable` was `true` — prose bodies got `disabled={!bodiesEditable}` and a no-op `onChange`, **locking criterion body editing outside structure/shapes/job-fixed-field paths**. Pre-change code used the same `editable` flag for both bodies and chrome, so rubric bodies had stayed interactive before this ticket touched the file. Severity B — a functional regression on a major shared editor surface, and the existing manifest didn't assert rubric body-edit persistence at all (the existing `joblist_rubric` expand-one test typed into a field but never asserted the content actually changed). **Recommendation:** extend the gate to `!inReview && (tabChromeEditable || !!fixedFields || !!jobPersistence)` (or equivalent preserving the structure-mode chrome lock while restoring rubric/shapes-adjacent free-form bodies), and add a component test that types into a rubric body and asserts the PUT payload.

**discuss** — same proposed-pattern-status note as Joan's plan review, non-blocking once `bodiesEditable` is fixed. **advisory** — an intentional `eslint-disable-next-line react-hooks/exhaustive-deps` omitting `fixedFields` from deps in favor of `fixedFieldKeys` is explained by an in-code comment about label-churn — acceptable if the comment survives resolve. **advisory** — the manifest was strong for structure/job paths but had no rubric-body regression guard before this finding.

**What's solid:** structure-mode fix logic itself was sound (`fixedFieldKeys` prevents label-only re-GET wipes; label-sync effect preserves `tabs[].content`; dict coerce rejects pin strings; JAR `job_resume`/`resume_content` overlay matched the Betty handoff); scope discipline held (ArtifactEditor-only, no API/core creep); the new tests directly exercised the two reported failure modes.

#### Resolution (2026-08-25)

**Product fix-now addressed:** `bodiesEditable` changed to `!inReview && (tabChromeEditable || !!fixedFields || !!jobPersistence)` — restores rubric/free-form body editing while keeping structure-mode chrome locked and bodies on when `fixedFields`/`jobPersistence` are set. **Test-tree fix-now (Betty):** landed "AST-1480: rubric free-form body edit PUTs edited content" + a bible line; full AST-1480 manifest re-run — 6 green (4× AST-1480 + AST-553 job persistence + AST-1410 Cancel). Discuss/advisory items (proposed-pattern citations, the `eslint-disable` comment) left unchanged, already accepted as non-blocking.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/frontend/src/components/ArtifactEditor.tsx` | Chrome/body split, hydration-race fixes, `bodiesEditable` gate (including the post-review fix) | `b16a93d36` — +83/-24 |
| | _tests_ | structure-mode + jobPersistence + rubric free-form body-edit coverage | `93d9ebd6a`; bible `docs/test-bible/frontend/components.md` § AST-1480 |
