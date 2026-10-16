# AST-2051 — fix: resume editors autosave section bodies; drop header Save outside Generate review

<!-- linear-archive: AST-2051 archived 2026-10-16 -->

## Linear archive (AST-2051)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2051/fix-resume-editors-autosave-section-bodies-drop-header-save-outside  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2041 — Autosave resume artifacts for base and job resumes  
**Blocked by / blocks / related:** parent: AST-2041

### Description

## What this implements

Base Resume Content and the Job Analysis Report → Job Resume tab stop relying on a header Save button that scrolls out of reach. Section body edits autosave through `ArtifactEditor`'s existing debounced autosave (same `AUTOSAVE_MS` the criteria pages use). The header shows the existing status text instead of Save/Cancel, except during Generate/Regenerate review, where Save/Cancel stays as the accept/reject step (AST-905 no-silent-persist rule).

## Resolved open questions (Susan approved the bug's To-be by reassigning; she skipped the explicit pick)

* **Versioning (bug step 3):** option **(a)**. Use the same 2s debounce as the criteria pages and accept one `astral_artifacts` version row per autosave. No longer debounce, no backend split. The backend Component scope line (`candidate.py` / `database.py`) is therefore **out**.
* **Save sections (bug step 4):** **out of scope.** The approved To-be covers section *body* edits only. The structure-row **Save sections** button and `ArtifactsBaseResumeContent.tsx` stay unchanged.

## Scope

## Component scope

* `src/ui/frontend/src/components/ArtifactEditor.tsx`: **modified**. It owns the autosave gate, the header Save/Cancel rendering, and the structure-row Save sections button. The whole fix lives here.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`: **modified only if** Save sections is in scope (step 4). It owns `saveStructure` / `persistStructureRows` for structure rows.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: **probably unchanged**. It passes `jobPersistence` with `onSaved: load`. A reload after every autosave may need softening if it disrupts typing.
* `src/core/candidate.py` / `src/data/database.py`: **modified only if** option (c) in step 3 is chosen. They own the save path that writes the `astral_artifacts` snapshot.

## Technical scope

* `ArtifactEditor.tsx`: modify `handleChange` so its autosave condition keys off body editability and not-in-review, instead of `tabChromeEditable`. Modify the header render so Save/Cancel show only in review mode. The reason is to make the resume editors use the existing debounced-save mechanism rather than adding a new one.
* `ArtifactsBaseResumeContent.tsx` (conditional): modify the structure-row change handler to debounce into the existing persist function in place of the Save sections button, so structure edits stop depending on a manual click.
* Backend save path (conditional, option c only): modify the base/job resume save so the live blob write is separate from the `astral_artifacts` version snapshot. Without that, autosave cadence would multiply version history.

## Boundaries

Does not change the structure-row Save sections flow, the backend save path / `astral_artifacts` versioning, the Generate/Regenerate review Save/Cancel, or the criteria pages' existing autosave. Tests / bible are Betty's: fix-board decides whether a gap child is needed.

## Notes for planning

AST-2041 Description (As-is / To-be / Proposed steps) is authoritative. Approved ancestor: AST-1459 (Archive), "Resume editor is not working properly". Its plan said "do not rely on structure-mode autosave", which this fix deliberately reverses at Susan's request. Plan-doc patch target: `docs/features/artifacts/ast-1459-resume-editor-is-not-working-properly.md`. Watch `JobAnalysisReportModal`'s `onSaved: load` reload after each autosave: it must not wipe in-progress typing.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-2041-resume-autosave`, child `sub/AST-2041/AST-2051-resume-autosave`. Created at bug-fix.

### Comments

#### radia — 2026-10-08T20:45:35.802Z
[code-rubric] PROCEED (Commit: 9fb7b99b1) Resume autosave matches plan

#### ada — 2026-10-08T20:43:40.629Z
`origin/sub/AST-2041/AST-2051-resume-autosave` @ `9fb7b99b1` · test-fix lighter check (no qa-fix on this ticket)

- `npx tsc -b --noEmit` OK; `npx eslint src/components/ArtifactEditor.tsx` OK
- vitest ArtifactEditor / ArtifactsBaseResumeContent / JobAnalysisReportModal: 88 passed, 14 failed
  - 11 expected header-Save cases → owned by AST-2056 (Betty)
  - 3 pre-existing, also red on pre-fix `ArtifactEditor.tsx` (`ea1344c43`), unrelated to AST-2051:
    - JobAnalysisReportModal AST-1546 / AST-1350 Print Resume ×2: no "Print Resume" button found
    - ArtifactsBaseResumeContent AST-1577 ui-consistency: ENOENT `canon/directives/draft/patt.artifact.ui-consistency.md` (directive now under `active/`)

#### joan — 2026-10-08T20:35:15.899Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T20:34:24.703Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md + pages.md (ArtifactEditor / ArtifactsBaseResumeContent) — broken tests + missing coverage — header Save clicked outside review on structure-mode/jobPersistence resume editors; no autosave coverage for resume bodies.

Broken (header Save/Cancel no longer renders outside review once `autosaveBodies` = `tabChromeEditable || structureMode`):
- `tests/component/frontend/components/test_ArtifactEditor.test.tsx`: AST-553 job persistence PUT (L278), AST-996/AST-1351 experience array Save (L555), AST-1351 legacy experience Save aborts (L618), AST-1382 [bug-repro] content Save bundles resume_structure (L1100), AST-1476 page-break + content Save (L1176), AST-1410 no-snapshot Cancel re-GET (L1265 — targets resume_content structure-mode jobPersistence; per plan AST-1410 now lives only on shapesKey job editors, so retarget), AST-1480 rename + Save (L1307), AST-1593 job_resume Save (L1529), AST-1480 structure bodies editable + Save (L1572), AST-1577 bodyShape resume_content Save (L1664).
- `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`: AST-1577 Save PUTs base_resume leaf (L890).

Unaffected: L228 fixed-shape Cancel (shapesKey, no structureMode), rubric/criteria review-mode Save cases, JobAnalysisReportModal suite (no header Save clicks on Job Resume).

Missing coverage (repro + What must still hold): structure-mode and jobPersistence resume body edit → PUT after AUTOSAVE_MS with no Save button outside review; Save/Cancel present during Generate review; timer queued pre-Generate doesn't fire during review (AST-905); in-flight autosave keeps dirty when a newer edit is pending; jobPersistence autosave doesn't call onSaved (unmount flush still does).

#### ada — 2026-10-08T20:33:23.031Z
`origin/sub/AST-2041/AST-2051-resume-autosave` @ `53c1b59b1` · gate narrowed to resume editors

---

_Implementation detail may live in git history on `origin/dev`._
