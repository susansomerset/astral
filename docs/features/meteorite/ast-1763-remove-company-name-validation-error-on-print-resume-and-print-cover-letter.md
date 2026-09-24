# AST-1763 — Remove company name validation error on Print Resume and Print Cover letter

<!-- linear-archive: AST-1763 archived 2026-09-24 -->

## Linear archive (AST-1763)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1763/remove-company-name-validation-error-on-print-resume-and-print-cover  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Astral error diagnostic
timestamp: 2026-09-21T23:53:39.335Z
message: Job missing company short name
route: /jobs/recommended
astral_candidate_id: somerset

```
Cover letter displays:

{"error":"Job missing company short name"}
```

## As-is

On Recommended (`/jobs/recommended`), Print Resume and Print Cover Letter call `builder.build_resume` / `builder.build_cover_letter`, which still require `job.get("company")` (employer short name) to load the owning candidate via `get_company`. After AST-1701, `job.company` is only a compat alias of nullable `company_id`; meteorite (and other) jobs can have a null employer while `candidate_id` is already on the job row (AST-1598). Those prints fail with `{"error":"Job missing company short name"}` and the cover/resume tab shows that JSON instead of HTML.

## To-be

Print Resume and Print Cover Letter on Recommended (and the same builder entry points elsewhere) render the job's resume/cover HTML for the owning candidate whenever the job is loadable, including when `company_id` / `company` is null — using the job's denormalized `candidate_id` (with company lookup only as a fallback when needed). Missing employer short name alone must not hard-fail print.

## Proposed steps

1. In `src/core/builder.py` `build_resume` and `build_cover_letter`, resolve the owning candidate via `job["candidate_id"]` first (same preference as `tracker._candidate_id_for_job`), then fall back to `company_id` / `company` → `get_company` → `candidate_id` only when the direct field is absent.
2. Raise "Job missing company short name" only when neither path can resolve a candidate — or drop that message when `candidate_id` is present and load the candidate directly; keep real "job not found" / "candidate not found" errors.
3. Leave the HTML emit paths (`build_resume_from_job` / `build_cover_letter_from_job`) and the frontend print buttons alone unless a call site still assumes a non-null company key after the builder fix.
4. Spot-check Recommended JAR Print Resume + Print Cover Letter for a somerset job with null `company_id` (meteorite or stripped employer) and for a normal company-parent job so both still print.

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

## Ancestor candidates

- [ ] AST-1701 — job source-entity schema / `company` → nullable `company_id` + compat alias (root of null employer on print lookup)
- [ ] AST-1598 — denormalize owning `candidate_id` onto job (the field print should use instead of requiring company)
- [ ] AST-1704 — track routing / job-detail / jobs API consumers after source-entity schema (sibling consumer sweep that may have missed builder print)
- [ ] AST-1702 — tracker land / parent writes after source-entity schema
- [ ] AST-1117 — Print HTML blobs (job Print Resume / Cover Letter HTML entry path)
- [ ] AST-1138 — job cover HTML SomersetCover emit (`build_cover_letter_from_job` / builder cover path)
- [ ] no ancestor candidate found

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
