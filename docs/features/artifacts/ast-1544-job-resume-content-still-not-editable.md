# AST-1544 — Job Resume Content still not editable

<!-- linear-archive: AST-1544 archived 2026-09-09 -->

## Linear archive (AST-1544)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1544/job-resume-content-still-not-editable  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-1547

### Description

The Base Resume content is editable for the candidate, but the job's job_resume content is NOT appearing in the artifact screen. Every section is blank.

## As-is

On Artifacts → Base Resume Content, enabled structure sections show the candidate's persisted `artifacts.base_resume` bodies and are editable. On the job artifact screen (JAR Job Resume / `job_resume` tab), structure chrome still renders but every section body is blank — persisted job resume content does not appear for view or edit.

## To-be

Opening the job's Job Resume artifact surface shows the same non-empty section bodies the job already has (from `resume_content` and/or the hydrated `job_resume` pin path), matching what Print/builder would use for that job; operators can read and edit those bodies the same way Base Resume Content already works.

## Proposed steps

1. Confirm on a repro job whether `job_data.artifacts.resume_content` is non-empty on disk and whether GET job detail's hydrated `artifacts.job_resume` overlay actually carries section ids (vs pin envelope / empty dict).
   1. the job is in the railway database in staging.  Here is the job_data.artifacts.resume_content for the problem record:
2. If the blob exists but the UI shows blanks: trace JAR `use_resume_structure` → `ArtifactEditor` job load (`applyJobArtifactResponse` / `mapFixedFieldsFromRaw` / structure `fixedFields` gate) and fix the job-only hydrate or mount timing path (Base already works).
3. If the blob is missing or the overlay leaves top-level section keys empty: fix `hydrate_job_artifacts_for_display` / `_resume_payload_body` preference of `resume_content` over pin unwrap so JAR receives section-shaped content.
4. Re-verify Save still PUTs `resume_content` only (pin slot untouched) and Base Resume Content stays green.

## Component scope

* `src/ui/frontend/src/components/ArtifactEditor.tsx` — modified — jobPersistence / structure-mode load into `tabs[].content` is the shared editor Base already uses successfully; Job Resume blanks point here first if GET payload is non-empty.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — modified — only if JAR-specific `structureSections` / `jobPersistence` mount timing blocks job hydrate while Base page wiring is fine.
* `src/core/tracker.py` — modified — only if GET hydrate overlay for `job_resume` / `resume_content` is what leaves section keys empty for the editor (`hydrate_job_artifacts_for_display`, `_resume_payload_body`).
* `src/ui/api/` job detail GET path that calls that hydrate (exact module as on tip) — modified — only if the API response omits the overlay the UI expects; no new routes.

## Technical scope

* `ArtifactEditor.tsx` — modified function(s) on the job artifact load / structure-mode gate so non-empty job section values land in `tabs[].content` when `jobPersistence` + structure fields are present (same loop Base already uses).
* `JobAnalysisReportModal.tsx` — modified wiring only if the Job Resume `ArtifactEditor` mounts before structure/job payload is ready and never reloads bodies.
* `tracker.py` — modified `hydrate_job_artifacts_for_display` / `_resume_payload_body` (or sibling helpers) so display overlay prefers nonempty `resume_content` and otherwise unwraps pin body to section ids the editor keys on.
* Job detail GET handler — modified call/return only if hydrate result is dropped or keyed wrong before JSON out.

## Ancestor candidates

- [ ] [AST-1459](https://linear.app/astralcareermatch/issue/AST-1459/resume-editor-is-not-working-properly) — Resume editor is not working properly (Done parent; blank/missing section bodies on Base + JAR structure editors)
- [ ] [AST-1480](https://linear.app/astralcareermatch/issue/AST-1480/restore-structure-mode-resume-section-body-edit-loop-resume-editor-is) — Restore structure-mode resume section body edit loop (Done child of AST-1459; claimed JAR Job Resume hydrate + edit + Save)
- [ ] AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data (Archive parent; pin + UAT surface resolve for `job_resume`)
- [ ] AST-1100 — Resolve artifact bodies from pinned agent_data_id for UAT surfaces (Archive child of AST-1091; JAR Job Resume blank when pin/hydrate leaves section keys empty)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
