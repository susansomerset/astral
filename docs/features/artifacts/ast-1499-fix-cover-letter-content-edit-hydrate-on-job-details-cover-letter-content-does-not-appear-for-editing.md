# AST-1499 — Fix cover letter content edit hydrate on job details (Cover Letter content does not appear for editing)

<!-- linear-archive: AST-1499 archived 2026-09-09 -->

## Linear archive (AST-1499)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1499/fix-cover-letter-content-edit-hydrate-on-job-details-cover-letter  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1491 — Cover Letter content does not appear for editing  
**Blocked by / blocks / related:** parent: AST-1491

### Description

## What this implements

Restore JAR Cover Letter content sections so Subject / Letter / Signature show the same letter body Print uses, and the operator can edit and save them. Orphaned-bug fix under mini-parent AST-1491. Approved ancestor (archived): AST-1116 — use its feature doc for plan-fix context only; do not re-parent under it.

## As-is

On the job details (JAR) page, Cover Letter content sections (Subject / Letter / Signature) open with empty text blocks, so the operator cannot see or edit the letter. Print Cover Letter for the same job still renders letter content.

## To-be

Opening Cover Letter content on the job details page shows the same letter body that Print uses (Subject / Letter / Signature populated from the job’s cover-letter artifact), and the operator can edit and save those fields.

## Citations

AST-1116 cover-letter field defs + JAR hydrate normalize; AST-1100 pin-body resolve for UAT surfaces; `hydrate_job_artifacts_for_display` / `normalize_cover_letter_artifact` / ArtifactEditor `shapesKey=cover_letter`.

## Acceptance criteria

- [X] On a job whose Print Cover Letter shows non-empty letter content, opening Cover Letter content on the job details page shows Subject / Letter / Signature populated (not empty placeholders).
- [X] Operator can edit those fields and Save; reload still shows the saved values.
- [X] Print Cover Letter still renders the letter after the editor hydrate/fix.
- [X] No change to resume structure-mode editing or unrelated JAR tabs beyond cover_letter fixed fields.

## Proposed change (make-fix)

- [X] Path A — `cover_letter_artifact_for_display` + hydrate: pin/dict → nonempty Subject/Letter/signature overlay only; no empty overwrite of usable pin; one nested unwrap for hop envelopes.
- [X] FE / api_jobs / builder shared extract skipped (probe: tracker path sufficient; detail already hydrates).

## Boundaries

Does not redesign cover-letter print HTML/CSS. Does not re-open AST-1116 as a live parent. Does not change resume structure-mode ArtifactEditor behavior except if a shared hydrate path must stay consistent.

## Scope

## Component scope

* `src/core/tracker.py` — modified: display hydrate / normalize for `artifacts.cover_letter` so JAR GET leaves Subject/Letter/signature bodies the editor can bind (same contract AST-1116/AST-1100 intended).
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — modified only if client load/mapping for `shapesKey=cover_letter` + `jobPersistence` is what blanks tabs after a good hydrate (e.g. pin-string reject or key map miss).
* `src/ui/api/api_jobs.py` — modified only if job detail stops calling or mishandles `hydrate_job_artifacts_for_display` for the cover slot.
* `src/core/builder.py` — read/align only if Print and hydrate need a shared unwrap; do not change print CSS or emit layout unless required for parity of field read.

## Technical scope

* `src/core/tracker.py` — modified function(s): `hydrate_job_artifacts_for_display` and/or `normalize_cover_letter_artifact` (and possibly pin-body unwrap before normalize) so a printable cover pin or dict becomes a Subject/Letter/signature dict for display; no empty overwrite of a usable pin.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — modified function(s): `applyJobArtifactResponse` / `mapFixedFieldsFromRaw` (and load effect only if needed) so fixed cover fields populate from the hydrated blob instead of staying empty placeholders.
* `src/ui/api/api_jobs.py` — modified function only if `detail` must change how artifacts are attached after hydrate.
* `src/core/builder.py` — optional shared helper extract from `_resolve_cover_letter` / `_cover_letter_fields_for_read` if hydrate should reuse the same nonempty read rules as Print.

## Notes for planning

Patch the existing AST-1116 feature doc at `docs/features/artifacts/ast-1116-cover-letter-field-defs.md` (plan-fix: never create a new plan doc). Mini-parent is AST-1491 (orphaned bug; its own ftr off origin/dev).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1491-cover-letter-content-does-not-appear-for-editing`, child `sub/AST-1491/AST-1499-fix-cover-letter-content-edit-hydrate`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-26T16:08:06.394Z
[code-rubric] PROCEED (Commit: 435cd11a) Nonempty cover hydrate fix

#### joan — 2026-08-26T15:55:23.699Z
[board-joan]  CANON: OK

context_tokens≈12000

#### betty — 2026-08-26T15:55:09.783Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md (AST-1116 hydrate) — missing coverage — repro gaps (pin leave-on-miss / nested hop unwrap / nonempty gate vs empty Subject·Letter·signature overwrite) not exercised by TestAst1116HydrateCoverLetterNormalize; Blast radius expects Betty extend before make-fix.

#### katherine — 2026-08-26T15:46:06.445Z
`origin/sub/AST-1491/AST-1499-fix-cover-letter-content-edit-hydrate` @ `26733bb4` · hydrate/Print cover parity

---

_Implementation detail may live in git history on `origin/dev`._
