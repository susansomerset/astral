# AST-1491 — Cover Letter content does not appear for editing

<!-- linear-archive: AST-1491 archived 2026-09-09 -->

## Linear archive (AST-1491)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1491/cover-letter-content-does-not-appear-for-editing  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

When I print a cover letter, I see content, but when I click on the Cover letter content sections on the job details page, the text blocks are empty, so I can't edit the content.

## As-is

On the job details (JAR) page, Cover Letter content sections (Subject / Letter / Signature) open with empty text blocks, so the operator cannot see or edit the letter. Print Cover Letter for the same job still renders letter content.

## To-be

Opening Cover Letter content on the job details page shows the same letter body that Print uses (Subject / Letter / Signature populated from the job’s cover-letter artifact), and the operator can edit and save those fields.

## Proposed steps

1. On a job that prints a non-empty cover letter, compare `GET /api/jobs/<id>` `job_data.artifacts.cover_letter` after `hydrate_job_artifacts_for_display` with what `builder._resolve_cover_letter` uses for Print — confirm whether the editor path gets a pin string, an empty Subject/Letter/signature dict, or a nested hop body that `normalize_cover_letter_artifact` flattens to blanks.
2. Fix the failing path so ArtifactEditor’s `shapes_key=cover_letter` load receives a non-empty Subject/Letter/signature dict (likely in `hydrate_job_artifacts_for_display` / pin unwrap before normalize, or in `ArtifactEditor.applyJobArtifactResponse` / `mapFixedFieldsFromRaw` if the API already returns the right blob and the client drops it).
3. Re-check Print still resolves content; Confirm Save PUT still writes the Subject/Letter/signature spine.

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

## Ancestor candidates

- [X] AST-1116 — Cover letter field defs + JAR hydrate normalize (`DATA_SHAPES` cover_letter + `normalize_cover_letter_artifact`); closest shipped work for empty Cover Letter tabs vs resolved body
- [ ] AST-1100 — Resolve pinned `agent_data_id` bodies for UAT surfaces including `cover_letter` on job GET
- [ ] AST-1091 — Parent epic: job resume / cover letter / suggested responses persisted as job_data artifact pins
- [ ] AST-1480 (under AST-1459) — Same ArtifactEditor “sections visible, bodies empty” failure class for resume structure mode; shared component, different mode (`shapesKey` cover vs structure resume)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
