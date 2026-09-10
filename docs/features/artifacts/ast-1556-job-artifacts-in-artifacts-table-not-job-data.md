# AST-1556 — Job artifacts in artifacts table, not job_data

<!-- linear-archive: AST-1556 archived 2026-09-09 -->

## Linear archive (AST-1556)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1556/job-artifacts-in-artifacts-table-not-job-data  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1547 — Job resume content is not saving to the job record  
**Blocked by / blocks / related:** parent: AST-1547

### Description

[bug]

Please have the job-related artifacts persist in artifacts table, not in the job_data of the job record.

## As-is

Job-related editable artifacts (job resume / cover letter) are persisted under `job_data.artifacts.*` on the job record (AST-1548 body-replica path), so editable content is buried in the job JSON rather than hosted as first-class artifact rows.

## To-be

Persist those job-related editable drafts in the `artifacts` table (current row keyed by `entity_type` / `entity_id` / `artifact_type`); UI load/save uses that table by entity id — not `job_data` blob fields for the editable body.

## Proposed change

- [X] Config: `JOB_EDITABLE_ARTIFACT_TYPES` / `JOB_ARTIFACT_ENTITY_TYPE`
- [X] Tracker: `save_artifact` / `get_current_artifact` SoT for job_resume + cover_letter; hydrate + `get_job` overlay; cancel retires table currents
- [X] Data: `retire_current_artifact` (no schema change)
- [X] API PUT job_resume / cover_letter / resume_content → table writers; GET via overlaid `get_job`

## Suggested engineer

Ada Lovelace

### Comments

#### radia — 2026-08-31T22:19:18.255Z
[code-rubric] REVIEW (Commit: 17445a51) consult resume_content gate vs table SoT

#### betty — 2026-08-31T22:11:56.353Z
[bug-repro]
`origin/sub/AST-1547/AST-1556-job-artifacts-in-artifacts-table` @ `0705de4b` · repro lands red, awaits fix

#### betty — 2026-08-31T22:07:47.706Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md § AST-1554 + ui/api/api_jobs.md § AST-1554 — broken test + missing coverage — dual-write/job_data SoT nodes must flip to artifacts-table save_artifact/get_current_artifact for (job, job_resume|cover_letter); no bible entry for job table persist/hydrate/cancel-retire

#### joan — 2026-08-31T22:07:31.321Z
[board-joan]  CANON: OK

context_tokens≈16000

#### ada — 2026-08-31T22:06:48.174Z
`origin/sub/AST-1547/AST-1556-job-artifacts-in-artifacts-table` @ `37610ba4d3692a3b016f03dcae5f8cf67076d0e2` · artifacts table SoT

---

_Implementation detail may live in git history on `origin/dev`._
