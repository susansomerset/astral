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

---

## Bug: AST-2051 — resume editors autosave section bodies; drop header Save outside Generate review

Parent: AST-2041 (orphaned Bug mini-parent). This deliberately reverses the AST-1459 **Architectural definition** line under `pattern.ui.dirty-leave-save-then-navigate` ("explicit Save/Cancel on fixed-field and job-persistence modes; do not rely on structure-mode autosave"), at Susan's request. The draft directive `canon/directives/draft/patt.ui.dirty-leave-save-then-navigate.md` § When not to use already exempts ArtifactEditor autosave/`beforeunload`, so no canon conflict. Canon Scope: none listed on AST-2041 / AST-2051. `patt.artifact.ui-consistency` (active, scoped to ArtifactEditor.tsx) is cited by id only.

### As-is

On **Artifacts → Base Resume Content** (`structureMode` via `bodyShape="resume_content"`) and **JAR → Job Resume** (`useCandidateResumeStructure` + `jobPersistence`), `ArtifactEditor` renders Cancel/Save inside `.dep-header`. The header scrolls away with the section panels, so Save is unreachable after scrolling, and nothing persists until Save is clicked. The 2 s debounced autosave (`AUTOSAVE_MS`, `handleChange`) only runs when `tabChromeEditable` (`!shapesKey && !structureMode`), which means the criteria/rubric pages only.

### To-be

On both resume editors, section **body** edits autosave through the existing `handleChange` debounce (same `AUTOSAVE_MS = 2000`). The header shows the existing status text ("Saving..." / "Unsaved changes" / "All changes saved") instead of Save/Cancel. During Generate/Regenerate review (`inReview`, `snapshot !== null`), Save/Cancel stays as the accept/reject step (AST-905 no-silent-persist rule). The unmount flush and `beforeunload` guard are unchanged. Structure-row **Save sections**, the backend save path / `astral_artifacts` version rows (one row per autosave is accepted), and the criteria pages' autosave are unchanged.

### Repro

Fixture: a candidate whose `candidate_data.artifacts.base_resume` is `{"summary": "Old summary", "experience": [{"company": "Acme", "title": "Eng", "dates": "2020-2024", "location": "Remote", "accomplishments": ["Shipped X"]}]}`, with `resume_structure` sections `summary` + `experience` enabled. Plus a recommended job whose `job_data.artifacts.resume_content` is the same dict.

1. Artifacts → Base Resume Content. Expand Summary. Scroll down until `.dep-header` is out of view. Type into the Summary body.
2. Observe: no Save is reachable without scrolling back up. Wait more than 2 s, then reload the page: the edit is gone (no PUT `/api/candidates/<id>/data` fired).
3. JAR → Artifacts → Job Resume. Edit a section body and wait more than 2 s: no PUT `/api/jobs/<id>/artifacts/resume_content`. Close and re-open the modal: the edit is gone.

### Root cause

`ArtifactEditor.handleChange` gates the debounce on `tabChromeEditable`, which is false whenever `structureMode` is true. The header render shows Save/Cancel whenever `fixedFields || inReview || jobPersistence` is truthy, and both resume editors always have `fixedFields` (and Job Resume also has `jobPersistence`). So both editors depend on a header Save that scrolls out of reach.

### Proposed change

All edits are in `src/ui/frontend/src/components/ArtifactEditor.tsx`. `JobAnalysisReportModal.tsx` and `ArtifactsBaseResumeContent.tsx` are **unchanged**.

**Decision: narrowed gate (not "all editable bodies").** The JAR modal mounts a *second* `ArtifactEditor` for cover letter / application responses (`shapesKey` + `jobPersistence`, `JobAnalysisReportModal.tsx` ~L559). If the gate keyed only off `bodiesEditable`, as the Technical scope's literal wording suggests, those editors would also start autosaving and lose their Save/Cancel. That is outside the To-be ("both resume editors"). So the gate keys off `tabChromeEditable || structureMode`.

1. **New const** directly after `bodiesEditable` (~L302):
   ```ts
   // Criteria (free-form) and resume structure editors autosave bodies; shapesKey job editors keep explicit Save/Cancel.
   const autosaveBodies = tabChromeEditable || structureMode
   ```
2. **`handleChange`** (~L717): replace `if (tabChromeEditable && !inReview)` with `if (autosaveBodies && bodiesEditable)`. `bodiesEditable` already includes `!inReview`, so criteria pages get an identical condition. Change the timer body to
   `timerRef.current = setTimeout(() => { if (snapshotRef.current === null) void doSave(next, true) }, AUTOSAVE_MS)`.
   This guards a timer queued *before* Generate from firing *during* review. Without it, `doSave` would `setSnapshot(null)` mid-generation and drop the review gate, which would let the generated content be silently persisted by the next edit or by the unmount flush (AST-905).
3. **`doSave`** (~L619): change the signature to `async (t: SideTab[], autosave = false)`. In the `jobPersistence` branch, replace `jobPersistence.onSaved?.()` with `if (!autosave) jobPersistence.onSaved?.()`.
   - Why: JAR's `onSaved` is `load`, which sets `loading=true`. The modal renders `{job && !loading && …}`, so every autosave would **unmount** the Job Resume editor: collapsing the panel, dropping focus, and losing keystrokes typed during the re-GET. The explicit Save (review) and the unmount flush (`doSave(tabsRef.current)`, `autosave` defaults to false) still call `onSaved`, so the modal's `job` refreshes when the operator leaves.
   - Alternative not taken: soften `load` in the modal into a silent refetch. That adds lines in a second file, and a silent refetch can still unmount the editor when `populatedArtifactSections` changes (all content cleared).
4. **`doSave` dirty clear, both branches** (~L654 job, ~L695 candidate): replace `setDirty(false)` with `if (tabsRef.current === t) setDirty(false)`.
   - Why: if the operator types while an autosave PUT is in flight, the response currently clears `dirty` even though a newer edit is pending on the timer. An unmount inside that window then skips the flush (`dirtyRef.current` false) and loses the edit.
   - This race exists today on criteria pages. It becomes routine on resume editors, where typing is long-form. Explicit Save and the unmount flush pass the current `tabs` / `tabsRef.current`, so their behavior is unchanged.
5. **Header render** (~L998): replace `{(fixedFields || inReview || jobPersistence) ? (` with `{(inReview || !autosaveBodies) ? (`. The Cancel/Save markup and the status `<span>` stay as they are.
   - Resume editors show status outside review and Save/Cancel during review.
   - Criteria pages are unchanged (status outside review).
   - `shapesKey` job editors are unchanged (`!autosaveBodies` means Save/Cancel always), so `handleCancel`'s non-snapshot re-GET branches stay live for them (AST-1410).
6. **No other changes.** The "Saved" toast keeps firing per autosave, same as criteria pages today. `Save sections`, `structureAuthoring` persistence of `resume_structure` inside `doSave` (AST-1381), the unmount flush, and `beforeunload` are untouched.

### Blast radius

- **Criteria/rubric pages** (`Artifacts*Criteria.tsx`): the gate expression is equivalent. Steps 2 and 4 guards now also apply here: no autosave fires into review, and `dirty` stays true when a newer edit is pending. Both are strict improvements with no visible change on the happy path.
- **JAR cover letter / application responses** (`shapesKey` + `jobPersistence`): no change. They keep explicit Save/Cancel and `onSaved: load`.
- **JAR Job Resume**: `canGenerate` is false under `jobPersistence`, and the recovery effect skips it, so `inReview` never happens there. The header never shows Save/Cancel. `onSaved` fires only on the unmount flush.
- **Base Resume `structureAuthoring`**: every body autosave also writes `resume_structure` from the current `structureRows` (existing AST-1381 behavior of `doSave`), so unsaved header edits ride along. This is the same as today's explicit body Save, just more frequent. Rows with `_pending_N` ids are re-slugged from the title server-side (`prepare_resume_structure_sections_for_save`), and repeated autosaves overwrite rather than duplicate.
- **Versioning**: one `astral_artifacts` version row per autosave on base resume (AST-1353). Susan accepted option (a). No backend change.
- **Print (Base Resume)**: `handlePrint` prints the saved blob. Edits from the last ≤2 s may not be included until the debounce fires (previously the operator had to click Save first).
- **Unsupported Experience**: `doSave` refuses with an error toast. Under autosave, that toast fires on each typing pause and the status stays "Unsaved changes". This is the same refusal explicit Save gave; Regenerate remains the escape (`baseResumeUnsupportedEscape`).
- **Tests (Betty, fix-board)**: the ArtifactEditor structure-mode / jobPersistence cases that click the header **Save**, the AST-1410 Cancel-reload case if it targets a structure-mode jobPersistence editor, and any `test_ArtifactsBaseResumeContent.test.tsx` case that clicks the header Save. These now need fake timers plus `AUTOSAVE_MS`, and should assert the absence of Save outside review.

### What must still hold

- AST-1459 AC1/AC2: persisted bodies load, are editable, and round-trip after reload/re-open. Persistence is now triggered by the debounce instead of a Save click.
- AST-1459 AC3 / AST-1480: the structure header authoring controls and **Save sections** still render and still write `resume_structure` independently.
- AST-1459 AC4: Experience job-array editing still works, and the unsupported shape still shows the configured message.
- AST-905: no silent persist of Generate/Regenerate/recovered output. Save/Cancel shows during review, autosave never fires while `snapshot !== null`, and the unmount flush still skips review.
- AST-1410: in-place Cancel re-GET on the `shapesKey` job-persistence editors is unchanged.
- Criteria pages: same autosave cadence, same status text, same "+ Add" / rename / reorder chrome.
- Unmount flush and `beforeunload` guard are unchanged.


## Fix-board Joan findings (AST-2051)

### Verdict

```
[board-joan]  CANON: OK
```

### Triage notes

Read `## Bug: AST-2051` on `origin/sub/AST-2041/AST-2051-resume-autosave` in `docs/features/artifacts/ast-1459-resume-editor-is-not-working-properly.md` (As-is through What must still hold). AST-2041 / AST-2051 carry **no Canon Scope**; roster skim focused on UI dirty-leave and artifact editor patterns touched by `ArtifactEditor.tsx`.

| Directive | In force? | vs proposed change |
|-----------|-----------|-------------------|
| `pattern.ui.dirty-leave-save-then-navigate` | **Draft** (`canon/directives/draft/patt.ui.dirty-leave-save-then-navigate.md`, `status: proposed`) | **No conflict.** Problem text separates route dirty-leave from “ArtifactEditor autosave/`beforeunload`”; **When not to use** explicitly exempts ArtifactEditor/criteria autosave. Enabling structure-mode body debounce is inside that carve-out, not overloading `useDirtyLeaveSaveThenNavigate`. |
| `patt.artifact.ui-consistency` | Active path, body still marks draft | **No update required.** Still PUT via existing candidate/job artifact leaf keys; no new storage fork. Autosave vs header Save is UX, not a violation of Implementation §4–6. |
| `patt.artifact.write-operative` | Active (backend) | **No conflict.** More frequent PUTs when body changes matches retire+insert versioning; plan notes Susan accepted per-autosave version rows (AST-1353). Identical-body no-op unchanged. |

The AST-1459 **Architectural definition** bullet (“do not rely on structure-mode autosave”) lives in the **feature plan**, not in the draft dirty-leave directive on `origin/dev` (legacy `canon/patterns/ui/…` is not on dev; only the draft directive exists). Susan’s reversal is product/plan intent, already acknowledged in the bug section; it does **not** contradict an approved statute or pattern.

AST-905 / AST-1410 items in **What must still hold** are ticket behavioral gates; the plan’s `snapshotRef` guard and unchanged `shapesKey` Save/Cancel path address them in product code, not via canon edits.

**ESCALATE** not warranted: bounded blast radius, explicit Susan precedent, no ambiguous active law.

**F3 (`validate-plan` fix mode):** not triggered by this board outcome (Joan **OK**). Chuckles still branches on Betty’s `[board-betty]` line per the fix-board table.


## Radia review (AST-2051)

[code-rubric]

**Ticket:** AST-2051  
**Publish ref:** `9fb7b99b1ab37cab4bf4c9b73f94f152ebc0b018` (`origin/sub/AST-2041/AST-2051-resume-autosave`)  
**Corpus:** (no `docs/canon-index.md` on publish ref; directive bodies read from `canon/directives/**` at tip)  
**Overall:** CLEAN  

## Canon scores

Frozen **Canon Scope** on Linear AST-2051 / AST-2041: **none** (issue doc agrees). No directive ids to score; roll-up from canon grades is vacuously clean.

**Fix-board Joan overlap (informational — not on frozen list; per fix-lane precedent when scope is empty):**

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| `patt.ui.dirty-leave-save-then-navigate` (draft) | — | — | Not scored (off-list); Joan: carve-out for ArtifactEditor autosave — no conflict with enabling structure-mode debounce |
| `patt.artifact.ui-consistency` | — | — | Not scored (cited id-only in plan); diff keeps existing PUT/GET leaf paths, no storage fork — consistent with Implementation §4–6 |
| `patt.artifact.write-operative` | — | — | Not scored (off-list); no backend diff; more frequent client PUTs matches accepted versioning (AST-1353) |

**Notes (Canon Scope):** Missing frozen list on the bug ticket is a **process gap for Archie** (comparability with feature children), not a product defect on this tip. `patt.artifact.ui-consistency` plainly governs `ArtifactEditor.tsx` but was intentionally **not** frozen — Joan F2 already triaged; **ESCALATE** not warranted.

## Column diff vs plan stage

`no plan-stage scores attached` (F3 `validate-plan` fix mode not run; Joan fix-board `[board-joan] CANON: OK` is qualitative only — aligned with product diff).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** not applicable — clean board opt-out: Betty `[board-betty] TESTS: REVISE` routed repro/coverage to sibling **AST-2056**; no `[bug-repro]` on this ticket. Ada `test-fix` notes 11 header-Save failures expected on this tip until AST-2056 lands.

**## What must still hold — OK**

| Item | Verdict |
|------|---------|
| AST-1459 AC1/AC2 — load, edit, persist (debounce not Save click) | `autosaveBodies = tabChromeEditable \|\| structureMode` + `handleChange` debounce → `doSave(next, true)` on both Base Resume (`bodyShape="resume_content"`) and JAR Job Resume (`useCandidateResumeStructure` → `structureMode`) |
| AST-1459 AC3 / AST-1480 — structure headers + **Save sections** | No diff outside autosave/header gate; `structureAuthoring` / `onStructureSave` untouched |
| AST-1459 AC4 — Experience / unsupported message | `doSave` validation loop unchanged |
| AST-905 — no silent persist in Generate review | `bodiesEditable` excludes `inReview`; timer callback gates on `snapshotRef.current === null`; header `(inReview \|\| !autosaveBodies)` keeps Save/Cancel during review |
| AST-1410 — Cancel re-GET on `shapesKey` job editors | `autosaveBodies` false when `shapesKey` (no `structureMode`); header still Save/Cancel; `handleCancel` paths unchanged |
| Criteria pages — autosave cadence / chrome | Rubric path: `autosaveBodies && bodiesEditable` equivalent to prior `tabChromeEditable && !inReview`; gains `snapshotRef` timer guard + in-flight `setDirty` guard (plan blast radius) |
| Unmount flush + `beforeunload` | Unchanged (`dirtyRef` + `snapshotRef` guard; flush uses `doSave(tabsRef.current)` with `autosave=false` → JAR `onSaved` still on leave) |
| JAR Job Resume — autosave without modal reload | `if (!autosave) jobPersistence.onSaved?.()` in `doSave` job branch |

## Findings

**fix-now:** (none)

**discuss:** (none requiring @susan product call on this tip)

**advisory:**

- **Sibling test carry:** Product diff is `ArtifactEditor.tsx` + plan patch only; Betty’s broken header-Save cases and new autosave assertions belong on **AST-2056** — expected red on this sub until merged.
- **Frozen Canon Scope:** Archie may want explicit frozen ids on fix bugs for Radia comparability; does not block this review.
- **Per-autosave “Saved” toast** on resume editors matches criteria behavior (plan step 6); no change in this diff.

## What’s solid

- Plan-fix steps 1–5 implemented in one file; narrowed `autosaveBodies` gate correctly excludes JAR cover letter / application `shapesKey` editors.
- AST-905 race (pre-Generate timer during review) and in-flight PUT vs newer edits addressed as specified.
- Estimate **2** vs footprint: appropriate.

## Chuckles branching (read-only)

| Gate | Parent shape |
|------|----------------|
| **PROCEED** (C7 complete) | **Orphaned** mini-parent AST-2041 → **Review Posted** → fix-lane clean shortcut → **User Testing**; then merge `sub/AST-2041/AST-2051-resume-autosave` **straight to `origin/dev`** (no `merge-child` / `prep-uat`). |
| If downstream needs Radia re-pass | After **AST-2056** merges tests onto sub, optional re-review only if product tip changes — not required for this product-only tip. |

**Recommended actions for Chuckles (not Radia):** Append this artifact to `docs/features/artifacts/ast-1459-resume-editor-is-not-working-properly.md`, commit `docs(AST-2051): Radia review — clean`, push `sub/AST-2041/AST-2051-resume-autosave`, post slim upshot `--as radia`, move **Tests Passed** → **Review Posted** → **User Testing** per §3h.

context_tokens≈N

---

```
[code-rubric] PROCEED (Commit: 9fb7b99b1) Resume autosave matches plan
```

**Test carry (AST-2051):** docs-acceptance on this ref — the test/bible delivery for this fix (retargeted header-Save cases + autosave `[bug-repro]` coverage) lands via sibling test gap AST-2056 `merge-tests`, merged onto `ftr/AST-2041-resume-autosave` after this child.

---

## Bug: AST-2056 — tests for resume editor autosave

Parent: AST-2041. This is the test-gap sibling of AST-2051, filed from Betty's `[board-betty] TESTS: REVISE` on AST-2051. The product contract is in `## Bug: AST-2051` (merged ahead of this block on `ftr/AST-2041-resume-autosave`). Only the test tree and the bible change, and Betty lands them in qa-fix. The engineer touches no product src or test files on this ticket.

### As-is

The component tests for the structure-mode and jobPersistence resume editors persist edits by clicking the header **Save** outside Generate review. No test covers resume-body autosave. No test covers the AST-2051 guards: no autosave during review, keeping dirty while an autosave is in flight, and skipping `onSaved` on autosave ticks.

### To-be

The resume-editor cases persist via autosave (fake timers, advance `AUTOSAVE_MS`, assert the PUT), and assert that Save/Cancel is absent outside review. New cases lock the AST-2051 contract. They are red against pre-fix product and green once AST-2051 lands (`[bug-repro]`). The bible entries describe autosave instead of header Save for the resume editors.

### Repro

Against the AST-2051 product change, these header-Save clicks find no button:

- `tests/component/frontend/components/test_ArtifactEditor.test.tsx` cases:
  - AST-553 job persistence PUT (~L278)
  - AST-996/AST-1351 experience array Save (~L555)
  - AST-1351 legacy experience Save aborts (~L618)
  - AST-1382 content Save bundles `resume_structure` (~L1100)
  - AST-1476 page-break + content Save (~L1176)
  - AST-1410 no-snapshot Cancel re-GET (~L1265)
  - AST-1480 rename + Save (~L1307)
  - AST-1593 job_resume Save (~L1529)
  - AST-1480 structure bodies editable + Save (~L1572)
  - AST-1577 bodyShape resume_content Save (~L1664)
- `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`: AST-1577 "Save PUTs base_resume leaf" (~L890).

### Root cause

These tests encode the pre-AST-2051 contract (explicit header Save/Cancel on `fixedFields || jobPersistence`), which AST-2051 deliberately reverses for resume editors.

### Proposed change

Betty, in qa-fix. Test tree and bible only.

1. **Retarget to autosave** (`test_ArtifactEditor.test.tsx`): the cases listed in Repro, except AST-1410. Each one:
   - uses `vi.useFakeTimers()`
   - makes its edit
   - asserts no `Save` button in the header
   - calls `vi.advanceTimersByTime(AUTOSAVE_MS)` (2000) and flushes promises
   - asserts the same PUT URL/body the case asserts today. For the AST-1351 legacy case, assert no PUT plus the unsupported-message error toast.
2. **AST-1410 Cancel re-GET**: retarget from the `resume_content` structure-mode jobPersistence editor to a `shapesKey` + `jobPersistence` editor (cover-letter shape). That is now the only non-review Cancel path.
3. **AST-1577 page case** (`test_ArtifactsBaseResumeContent.test.tsx` ~L890): same autosave retarget, asserting the PUT to `/api/candidates/<id>/data` with the `base_resume` leaf.
4. **New cases** (`test_ArtifactEditor.test.tsx`):
   1. **Structure-mode body edit autosaves.** Edit a body, then:
      - no Save/Cancel; status text shows "Unsaved changes"
      - no PUT before `AUTOSAVE_MS`
      - exactly one PUT after it
      - "All changes saved" afterward
   2. **JobPersistence body edit autosaves.** Same assertions against `PUT /api/jobs/<id>/artifacts/<key>`.
   3. **Generate review keeps Save/Cancel.** After Generate resolves on base resume, Save and Cancel render. Advancing timers fires no PUT.
   4. **No autosave during review (AST-905).** Edit a body, then start Generate before `AUTOSAVE_MS` elapses. Advance timers while review is open: no PUT fires, and Save/Cancel still render.
   5. **In-flight autosave keeps dirty.** Make the first autosave PUT a deferred promise. Make a second edit, then resolve the first PUT. The status stays "Unsaved changes". Unmounting before the second timer fires still PUTs the second edit.
   6. **`onSaved` only on unmount flush.** An autosave PUT on jobPersistence does **not** call `onSaved`. Edit again and unmount before the timer fires: the flush PUT **does** call `onSaved`.
5. **Bible**: update the ArtifactEditor and ArtifactsBaseResumeContent rows in `docs/test-bible/frontend/components.md` and `docs/test-bible/frontend/pages.md`. They should say "autosave after AUTOSAVE_MS, Save/Cancel only in Generate review" for resume editors, and list the new cases.

### Blast radius

These suites stay untouched:

- the `shapesKey` fixed-shape Cancel case (~L228)
- the rubric/criteria review-mode Save cases
- the `JobAnalysisReportModal` suite (it never clicks header Save on Job Resume)

Fake timers must be restored per case (`vi.useRealTimers()` in `afterEach`) so the `findBy*` polling in neighboring cases isn't stalled.

### What must still hold

- Every retargeted case keeps its original assertion on the PUT payload, especially the AST-1382/AST-1476 `resume_structure` bundling and the AST-1593 job leaf key. Only the trigger changes (Save click becomes the timer).
- No product src on this ticket. AST-2051 owns `ArtifactEditor.tsx`.
- The new cases are red on pre-AST-2051 product and green after it lands.


## Radia review (AST-2056)

[code-rubric]

**Ticket:** AST-2056  
**Publish ref:** `4cf623ac4cd899915ebec5fda18c8566050014af` (`origin/sub/AST-2041/AST-2056-resume-autosave-tests`)  
**Corpus:** (no `docs/canon-index.md` on publish ref; test-only delivery)  
**Overall:** CLEAN  

## Canon scores

Frozen **Canon Scope** on AST-2056: **none** (test tree + bible only; product on AST-2051). No directive ids to score; roll-up vacuously clean.

**Notes:** `astral.git.engineer-test-tree-ban` / Betty ownership satisfied — this ticket’s entire diff is `tests/**`, `docs/test-bible/**`, and plan patch; **no `src/**`**.

## Column diff vs plan stage

`no plan-stage scores attached` (gap child from Betty `qa-fix`; no `validate-plan` / fix-board Joan artifact on AST-2056 — appropriate for test-only delivery).

## Frame diff

(none)

## Fix-specific checks

### `[bug-repro]` — OK (with advisory on AST-905 guards)

**Tagged `[bug-repro]` (4) — repro-first and To-be pinned:**

| Test | Asserts (not tautology) | Pre-fix fail? |
|------|-------------------------|---------------|
| `AST-2051 [bug-repro]: structure body edit autosaves…` | No Save/Cancel; `"Unsaved changes"`; **0 PUT** before full `AUTOSAVE_MS`; **1 PUT** with `professional_summary === "Struct body edited"`; `"All changes saved"` | Yes (no structure-mode autosave pre-AST-2051) |
| `AST-2051 [bug-repro]: jobPersistence Job Resume…` | Same pattern on `PUT /api/jobs/j1/artifacts/resume_content` with `hello edited` | Yes |
| `AST-2051 [bug-repro]: in-flight autosave keeps dirty…` | Deferred first PUT; second edit; **`"Unsaved changes"`** after first resolves; **unmount flush** → 2nd PUT with `"Struct body one two"` | Yes |
| `AST-2051 [bug-repro]: jobPersistence autosave skips onSaved…` | `onSaved` **not** called after autosave PUT; **called once** after unmount flush + 2nd PUT `hello a b` | Yes |

**Retarget with `[bug-repro]` in title:** `AST-1382 [bug-repro]: content autosave bundles resume_structure…` — autosave trigger + unchanged `resume_structure` / format bundling assertions (plan step 1 / **What must still hold**).

**AST-905 contract (2) — not `[bug-repro]`-tagged; bible documents as guard cases:**

- `AST-2051: Generate review keeps header Save/Cancel and never autosaves` — Save/Cancel present in review; `advanceAutosave()` → **0 PUTs**; explicit Save → 1 PUT.
- `AST-2051: autosave timer queued before Generate does not fire during review` — edit → Regenerate inside debounce window → timers advanced → **0 PUTs**; Save/Cancel still shown.

These two are **green on pre-fix structure-mode product** because pre-AST-2051 never queued body autosave in structure mode (timer never armed), so they do not flip red→green like the four `[bug-repro]` cases. They still assert post-AST-2051 behavior (especially the pre-Generate timer + `snapshotRef` path) and match the plan/bible “guard — green pre-fix” wording.

**advisory:** Repro-first gate is **4 explicit `[bug-repro]`** tests per bible manifest step 2; the two AST-905 guards are regression locks, not repro-first gates. Optional hardening (not blocking): spy `setTimeout` / assert a timer was scheduled before Generate so pre-fix fails for the wrong reason too — **Default if unpicked:** ship as documented.

**Retargeted header-Save cases (10 + page):** Use `startAutosaveClock` / `advanceAutosave`, `expectNoHeaderSaveCancel()`, and preserve PUT payload checks (e.g. AST-553 job PUT, AST-1351 legacy **no PUT** + unsupported toast + `"Unsaved changes"`, AST-1410 **shapesKey** cover letter Cancel re-GET, page `AST-1577 / AST-2051` autosave to `/api/candidates/c1/data` with `base_resume.professional_summary`). Matches plan § Proposed change 1–3.

**Harness:** `afterEach(vi.useRealTimers)` in both suites; page case uses `useFakeTimers({ shouldAdvanceTime: true })` per plan blast radius.

### `## What must still hold` — OK

| Item | Verdict |
|------|---------|
| Retargeted PUT payloads (AST-1382/1476 structure bundling, AST-1593 leaf, etc.) | Payload assertions retained; only trigger is timer vs Save click |
| No product `src` on this ticket | Diff: 5 files, **no `src/`** |
| New cases red pre-fix / green with AST-2051 | Betty/Ada report: 4 `[bug-repro]` red on ftr product; 8/8 `AST-2051`-named tests green with AST-2051 product overlaid; retargets red on missing Save / no autosave PUT |

## Findings

**fix-now:** (none)

**discuss:** (none requiring @susan)

**advisory:**

- **AST-905 guard tests** pass pre-fix without exercising autosave (see above); bible already labels them; not a merge blocker.
- **Pre-existing 3 reds** (Print Resume ×2, ui-consistency draft path) documented in bible § AST-2056; name-skipped in manifest — unchanged by this tip.
- **Frozen Canon Scope** missing on gap child — Archie process note only.

## Plan fidelity

Aligns with `## Bug: AST-2056` (retarget list, AST-1410 shapesKey, six new contract cases, bible updates). `docs/test-bible/frontend/components.md` § AST-2056 manifest matches Ada’s 105/108 pass + skip pattern.

## Chuckles branching (read-only)

| Gate | Parent shape |
|------|----------------|
| **PROCEED** (C7 complete) | **Orphaned** AST-2041 → **Review Posted** → **User Testing**; land **`merge-tests(AST-2056)`** onto stack with AST-2051 product before **straight-to-`origin/dev`** finish-up (per AST-2051 review note on test carry). |

**Recommended actions for Chuckles:** Append artifact to plan doc, `docs(AST-2056): Radia review — clean`, push `sub/AST-2041/AST-2056-resume-autosave-tests`, slim upshot `--as radia`, advance status per fix-lane §3h.

context_tokens≈N

---

```
[code-rubric] PROCEED (Commit: 4cf623ac4) Bug-repro locks autosave contract
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/58ada20669ec1b4eadf1fda92576b14b/f2b4d7de-53f9-4bdd-b150-7198ce186e81/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/e65177cf-998e-4ccc-ae81-d493ed68b29f/store.db` |
| Radia | review | `/home/susan/.cursor/chats/58ada20669ec1b4eadf1fda92576b14b/4b19ee38-0c64-484d-a4cf-1a8b3c57a305/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2041 (parent) | ftr/AST-2041-resume-autosave |
| AST-2051 | sub/AST-2041/AST-2051-resume-autosave |
| AST-2056 | sub/AST-2041/AST-2056-resume-autosave-tests |

**Epic worktree:** `astral-AST-2041/` — one active sub checked out at a time.
