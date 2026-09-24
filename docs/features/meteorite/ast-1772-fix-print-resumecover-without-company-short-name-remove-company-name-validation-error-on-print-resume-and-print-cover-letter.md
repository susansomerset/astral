# AST-1772 — fix: print resume/cover without company short name (Remove company name validation error on Print Resume and Print Cover letter)

<!-- linear-archive: AST-1772 archived 2026-09-24 -->

## Linear archive (AST-1772)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1772/fix-print-resumecover-without-company-short-name-remove-company-name  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1763 — Remove company name validation error on Print Resume and Print Cover letter  
**Blocked by / blocks / related:** parent: AST-1763

### Description

## What this implements

Fix Print Resume and Print Cover Letter on Recommended (and shared builder entry points) so jobs with null `company_id` / `company` but a populated `candidate_id` still render HTML — missing employer short name alone must not hard-fail print.

## Scope

## Component scope

* `src/core/builder.py` — modified: `build_resume` and `build_cover_letter` still gate on `job.get("company")` and fail with "Job missing company short name"; that is the reported error string and the ownership lookup that breaks null-`company_id` jobs.
* `src/ui/api/api_resume_html.py` — unchanged unless error mapping needs a touch; it already forwards `ValueError` from builder into the JSON `error` body the cover tab shows.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — unchanged expected; Recommended Print Resume / Print Cover Letter already fetch-then-blob and surface API `error` text — fixing builder removes the bad payload.
* `src/core/tracker.py` — modified only if plan-fix chooses to reuse / harden `_candidate_id_for_job` (it already prefers `candidate_id` but still falls back via `job.get("company")` only) instead of duplicating resolve logic in builder; otherwise leave tracker alone.

## Technical scope

* `builder.build_resume` — modified function: stop requiring a non-empty company short name before load; resolve candidate via job `candidate_id` first, company_id/company → company row second; only then raise if candidate cannot be resolved.
* `builder.build_cover_letter` — modified function: same ownership resolve change as `build_resume` (identical gate today at the "Job missing company short name" check).
* Optional `tracker._candidate_id_for_job` — modified function only if builder is wired to call it (or its company fallback is updated to read `company_id`); exact naming/wiring is plan-fix's call under statute.
* No new tables or fields — `job.candidate_id` and nullable `job.company_id` already exist post AST-1598 / AST-1701.

## Acceptance criteria

- [X] On `/jobs/recommended`, Print Resume and Print Cover Letter for a job whose `candidate_id` is set but employer `company_id` / `company` is null produce printable HTML (not `{"error":"Job missing company short name"}`).
- [X] Normal company-parent jobs still print resume and cover letter unchanged.
- [X] Builder raises a clear error only when neither `candidate_id` nor company lookup can resolve the owning candidate.

## Boundaries

Does not change HTML emit (`build_*_from_job`), frontend print buttons, or database schema. Scope is explicit above — plan-fix plans against it.

## Notes for planning

Parent bug AST-1763 Description has As-is / To-be / Proposed steps. No ancestor ticket was checked — grep `docs/features/**` for builder print / AST-1117 / AST-1701 context; patch the best-matching existing plan doc (likely `docs/features/artifacts/ast-1117-print-html-blobs.md` or meteorite source-entity docs). Work from parent bug Description if no single doc fits.

## Git branch (authoritative)

Parent `ftr/AST-1763-remove-company-name-validation-error-on-print-resume-and-print-cover-letter`. Child ref recorded in epic registry at bug-fix dispatch.

### Comments

#### radia — 2026-09-22T01:34:41.309Z
[code-rubric] REVIEW (Commit: 8d96e8c2) builder tests red — product OK; gap AST-1776 owns test flip

#### betty — 2026-09-22T01:27:45.758Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/builder.md (TestBuildResume / TestBuildCoverLetterDebugPaths) — broken assertions on "missing company" / "Company not found" / "no candidate_id", and no coverage for null company + candidate_id print success

#### joan — 2026-09-22T01:27:41.682Z
[board-joan]  CANON: OK

#### katherine — 2026-09-22T01:26:31.049Z
`origin/sub/AST-1763/AST-1772-fix-print-resume-cover-without-company-short-name` @ `882bb9462d9f5f775a69455bd399971ac32cb3fd` · builder owns via candidate_id

---

_Implementation detail may live in git history on `origin/dev`._
