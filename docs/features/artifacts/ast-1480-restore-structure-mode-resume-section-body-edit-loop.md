# AST-1480 — Restore structure-mode resume section body edit loop

**Linear:** [AST-1480](https://linear.app/astralcareermatch/issue/AST-1480/restore-structure-mode-resume-section-body-edit-loop-resume-editor-is) (child of [AST-1459](https://linear.app/astralcareermatch/issue/AST-1459/resume-editor-is-not-working-properly))

**Publish ref:** `sub/AST-1459/AST-1480-restore-structure-mode-resume-section-body-edit-loop`

**Summary:** Operators see structure chrome (collapsible headers / AST-1323 authoring controls) on Base Resume Content and JAR Job Resume, but persisted section bodies are missing, empty, or not usable for edit→Save. This ticket restores the shared `ArtifactEditor` structure-mode load → body edit → Save loop for both candidate `artifacts.base_resume` and job `job_data.artifacts.resume_content`, without regressing structure header authoring, Experience job-array editing, or Cancel in-place reload (AST-1410).

---

## Explicit scope gate

Ticket **## Scope** (and parent Component/Technical scope partitioned onto this child) names:

- **Required:** `ArtifactEditor.tsx` — structure-mode load through `tabs[].content`, body edit gating, Save payload.
- **Conditional (only if repro needs them):** `LabeledTextArea.tsx`, `ExperienceJobsEditor.tsx`, `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`, `App.css`.
- **Tests (Betty owns tree):** `test_ArtifactEditor.test.tsx`, `test_ArtifactsBaseResumeContent.test.tsx` if page wiring touched — engineer does **not** edit `tests/` or bible at build-child; note expected repro in Code Complete for Betty.

Every Files Changed row below is named in Scope. Stages must not invent `src/core/` or `src/ui/api/` work unless Stage 1 proves an API hydration bug — then **stop** and comment on the parent (AC 6 / `no-cross-contamination`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Split structure-mode **tab chrome** vs **section body** editability; fix structure-mode load guards/races so `tabs[].content` hydrates from candidate/job artifact blobs; keep Save for `fixedFields` / `jobPersistence`; preserve Experience unsupported path | ui |
| `src/ui/frontend/src/components/LabeledTextArea.tsx` | **Only if** bodies hydrate but stay non-interactive for a reason owned by this component (explicit `disabled` / missing `onChange` wiring). Prefer ArtifactEditor fix first | ui |
| `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` | **Only if** Experience panels share the same empty/read-only failure after prose sections are fixed | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | **Only if** `structureSections` vs `allSections` / `handleStructureRowsChange` contributes to empty or non-editable bodies (e.g. tab key list diverges from `base_resume` keys incorrectly) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | **Only if** JAR-only timing (`structureSections` fetch vs `jobPersistence` mount) blocks hydration after ArtifactEditor fix | ui |
| `src/ui/frontend/src/App.css` | **Only if** a rule blocks interaction or hides `.side-tab-textarea` / `.collapsible-panel-body` content in structure mode (no drive-by restyle) | ui |
| `tests/component/frontend/components/test_ArtifactEditor.test.tsx` | Betty at qa-child — structure-mode body display + edit + save; engineer must not edit | tests |
| `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` | Betty at qa-child — only if page wiring touched | tests |

**Out of scope:** craft-base generation, Print HTML, builder emit, `resume_structure` catalog schema, new API routes, tab add/remove/rename chrome in structure mode.

---

## Stage 1: ArtifactEditor — hydrate bodies + body editability (not tab chrome)

**Done when:** On a structure-mode mount with non-empty mocked/persisted section values, expanding a prose panel shows that text in `LabeledTextArea` and typing updates `tabs[].content`; Save still appears and PUTs the artifact dict; structure header controls remain; `editable`-gated tab rename / add / remove / rubric chrome stay **off** in structure mode; Experience valid arrays still use `ExperienceJobsEditor`, legacy non-array still shows the unsupported message + disabled textarea.

### 1.1 Diagnose against current code (read-only, then fix in this file)

Trace these paths in `ArtifactEditor.tsx` before changing behavior; the build agent must confirm which failure mode is live, then apply the matching fix below (do not skip diagnosis):

1. **Structure → fields:** `useCandidateResumeStructure` → `structureMode`; parent `structureSections` effect (~L413–430) and internal `resume_structure` fetch (~L433–446) → `shapeFields` / `fixedFields`.
2. **Load gates:** candidate load (~L531–543) and job load (~L517–528) both early-return when `(shapesKey \|\| structureMode) && !fixedFields`. Confirm they re-run once `fixedFields` is set and call `applyCandidateArtifactResponse` / `applyJobArtifactResponse` → `mapFixedFieldsFromRaw` → `tabs[].content` via `sectionValueToTabContent`.
3. **Edit gate:** `const editable = !shapesKey && !structureMode` (~L193). Today this correctly disables tab chrome and autosave, and prose `LabeledTextArea` still receives `onChange={v => updateTab(...)}` (~L1146). Confirm whether the live bug is (A) empty `tabs[].content` after load, (B) body controls non-interactive, (C) Save missing/broken, or (D) page/CSS outside this file — then fix (A)–(C) here; for (D) proceed to Stage 2.

⚠️ **Decision:** Prefer fixing shared gating/hydration inside `ArtifactEditor.tsx`. Do not add a new prop from pages for body editability unless Stage 1 cannot restore both Base and JAR surfaces.

### 1.2 Split chrome editability from body editability

In `ArtifactEditor.tsx`:

1. Keep structure mode disabling **tab chrome** (rename, add criterion, remove, reorder controls, rubric code/importance) via a clearly named flag derived from the current `editable` meaning, e.g. `tabChromeEditable = !shapesKey && !structureMode` (name is the implementer’s call; meaning is mandatory).
2. Introduce an explicit **body** affordance for structure / shapes / job fixed-field modes, e.g. `bodiesEditable = !!(fixedFields \|\| jobPersistence) && !inReview` (or equivalent that stays true in structure mode whenever fixed-field tabs are mounted and not in Generate review). Wire prose `LabeledTextArea` `onChange` and Experience `ExperienceJobsEditor` `onChange` through `bodiesEditable` (when false, use no-op / `disabled` only for the existing unsupported-experience path — do not disable happy-path bodies in structure mode).
3. Leave autosave gated on tab-chrome/`editable` semantics (`if (editable && !inReview)` ~L666) — structure mode continues to use **explicit Save**, not autosave (`pattern.ui.dirty-leave-save-then-navigate`).
4. Keep the Save/Cancel header branch that already shows when `fixedFields \|\| inReview \|\| jobPersistence` (~L943). Do not hide Save in structure mode.

### 1.3 Fix hydration races / guards that leave empty bodies

Still in `ArtifactEditor.tsx`, apply only what diagnosis requires:

1. If `mapFixedFieldsFromRaw` / `sectionValueToTabContent` drops persisted values for structure keys (dict or legacy `{label,content}[]`), fix mapping so each `fixedFields` key gets the matching artifact value into `tabs[].content`.
2. If structure-mode load returns early forever or remounts with empty tabs after `structureSections` updates, fix the effect dependencies / guards so a successful candidate GET or job GET always remaps once `fixedFields` is non-null. Do **not** clear `tabs` to empty placeholders after a successful hydrate when only structure header metadata changed.
3. Preserve AST-1410 Cancel: `handleCancel` must still re-GET and re-apply artifact response without full page reload on job and candidate paths.
4. Preserve Experience: `type: "experience_jobs"` on `experience` in structure `shapeFields`; valid arrays → `ExperienceJobsEditor`; `parseExperienceJobs` failure → unsupported message + disabled raw textarea; Save still aborts with that message.

### 1.4 Regression checklist (manual / existing component expectations)

After the edit, structure mode must still:

- Not call `/api/shapes/candidates` when `useCandidateResumeStructure` is set (existing AST structure tests).
- Show AST-1323 header controls when `structureCatalog` + `structureRows` + change/save callbacks are passed; **Save sections** remains separate from content Save.
- Expand-one policy for non-rubric rails (bodies may stay `hidden` until Expand — content must still be present in the DOM / appear after expand).

**Out of this stage:** edits under `ArtifactsBaseResumeContent.tsx`, `JobAnalysisReportModal.tsx`, `App.css`, `LabeledTextArea.tsx`, `ExperienceJobsEditor.tsx` unless diagnosis proved they are required — those are Stage 2.

---

## Stage 2: Conditional page / CSS / child-component wiring (skip if Stage 1 restores both ACs)

**Done when:** Either (a) Stage 1 alone satisfies Base Resume Content and JAR Job Resume ACs and this stage is a no-op commit skipped with a Linear stage comment stating “Stage 2 skipped — ArtifactEditor-only”, or (b) the minimal extra file(s) named below are patched and both surfaces hydrate + edit + Save.

⚠️ **Decision:** Skip entire Stage 2 when Stage 1 verification shows both surfaces working. Do not touch conditional files “for cleanliness.”

If Stage 1 leaves a gap, apply **only** the matching branch:

1. **`ArtifactsBaseResumeContent.tsx`** — If `handleStructureRowsChange` remapping `structureSections` to **all** rows (including disabled) blanks or desyncs body tabs relative to `artifacts.base_resume`, keep tab field keys aligned with enabled (or hydrated) section ids for body load while `structureRows` / `allSections` remain the authoring list. Do not change Print, accent bar, or structure PUT shape.
2. **`JobAnalysisReportModal.tsx`** — If JAR alone fails because `ArtifactEditor` mounts before `structureSections` is ready or remounts wipe job hydrate, align fetch/mount so `useCandidateResumeStructure` + `structureSections` + `jobPersistence` are present together for `use_resume_structure` artifact tabs. Do not change Generate/Cancel artifact strip or non-structure artifact tabs.
3. **`LabeledTextArea.tsx` / `ExperienceJobsEditor.tsx`** — Only if ArtifactEditor already passes interactive handlers but the child forces `disabled` or drops `onChange` in the structure-mode happy path.
4. **`App.css`** — Only if a rule sets `pointer-events: none`, zero height, or `visibility`/`display` that hides `.collapsible-panel-body .side-tab-textarea` (or experience editor) in structure mode. Narrow the fix; do not restyle the stack.

If the gap is server-side (candidate/job GET omits `base_resume` / `resume_content` that exists in DB), **stop** — comment on parent AST-1459 with the 🛑 Stage blocked format; do not invent API changes under this ticket.

---

## Stage 3: Compile and lint (product only)

**Done when:** Frontend TypeScript build and lint for touched UI files succeed on the epic worktree; no `tests/` or bible edits in the engineer commit(s).

1. From `src/ui/frontend`, run the repo’s usual compile/lint for the touched TS/TSX (and CSS if Stage 2 touched it).
2. Fix any type/lint errors introduced by this ticket only.
3. In the Code Complete / stage comment trail, name the failure mode found in §1.1 (A/B/C/D) and which files landed, so Betty can target `test_ArtifactEditor.test.tsx` (and page test if Base wiring changed) for structure-mode body display + edit + Save on both persistence paths.

---

## Estimate

Confirm Chuckles estimate: 3 — agree

Single shared component vertical slice (load/edit/save) with known patterns; conditional page/CSS only if needed; no schema/API by default.
