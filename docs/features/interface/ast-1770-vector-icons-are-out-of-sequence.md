# AST-1770 — Vector Icons are out of sequence

<!-- linear-archive: AST-1770 archived 2026-09-24 -->

## Linear archive (AST-1770)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1770/vector-icons-are-out-of-sequence  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators reading a Recommended Job Analysis phase should scan vectors in a consistent, meaningful order — highest-importance and strongest grades first — both in the compact header grade row and in the expanded per-vector detail. Today those surfaces follow consult payload order (or importance-only column sort in headers), so vectors appear out of sequence relative to rubric importance and letter grade. This epic aligns display order and makes grade-dot hover text identify the vector before rubric context.

## Functional scope

* **Analysis section header grade row.** On the Recommended Job Report modal Analysis tab, each phase section header that shows horizontal grade dots lists vectors left-to-right in descending rubric importance, then descending letter grade (A best through X worst) when importance ties.
* **Analysis detail vector list.** Expanding a phase section shows the same vector order in the per-vector rubric body (`AgentAnalysisHeader` rows) — not consult response array order.
* **Grade-dot tooltips name the vector.** Hover tooltips on grade dots in the Recommended Job Report Analysis header row prefix the vector label (job-carried rubric label when present) before the existing rubric/confidence tooltip body.

## Component scope

* `src/ui/frontend/src/lib/rubricDisplay.ts` — **modified** — shared grade-rank comparator and display-order sort that considers rubric importance plus per-vector letter grade; optional vector-name prefix for grade-dot tooltip text.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx` — **modified** — phase header grade row uses the new sort and prefixed tooltips.
* `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` — **modified** — render grades in the same importance-then-grade order using job-carried rubric metadata.
* `tests/component/frontend/lib/test_rubricDisplay.test.ts` — **modified** — sort + tooltip prefix coverage.
* `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` — **modified** — header row order assertions.
* `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx` — **modified** — detail list order assertions.
* `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — **modified** — end-to-end Recommended Analysis header/detail order on fixture job.

## Technical scope

* `rubricDisplay.ts`: add a letter-grade rank map (A best → X worst, matching existing list-table `GRADE_ORDER` semantics) and a sort helper that orders rubric columns or grade rows by importance descending, then grade rank ascending (better letter first), then code ascending as final tiebreaker; extend or wrap `formatGradeDotTooltip` so callers can prepend the vector label when building Recommended-report grade-dot `title` text.
* `recommendedJobReport.tsx`: in `buildPhaseSectionGradeConfidenceRow`, build columns from job-carried rubric as today, then sort with the new helper using live grades for the secondary grade key; pass vector label into tooltip formatting.
* `AgentAnalysisHeader.tsx`: before mapping grades, sort the normalized grade list using the same helper and `rubricItems` / labelList metadata so header row and expanded body stay aligned.
* Tests: fixture with at least two vectors where consult array order disagrees with importance+grade order (e.g. AST-1328 meteorite jd_rubric: QC importance 5 grade B before EFW importance 1 grade A); assert DOM order and tooltip prefix string.

## Architectural definition

* **Patterns to reuse** — no established pattern applies; this extends existing AST-437 / AST-950 / AST-1063 `rubricDisplay.ts` helpers and job-carried rubric consumers without a new catalog arc.
* **New patterns proposed** — none.
* **Applicable statutes** — none in the active catalog directly govern rubric display ordering; frontend-only presentation over existing job-carried `*_rubric` + `*_grades` payloads (AST-1063 / AST-1321 convention). No API, persistence, config, or core consult changes.

## Acceptance criteria

1. On a Recommended Job Report Analysis phase with job-carried rubric + grades where consult array order differs from importance+grade order, the section header `.recommended-report-phase-grade-row` grade dots appear left-to-right with higher importance first; when importance ties, better letter grade first (verify with AST-1328-style fixture: QC/5/B before EFW/1/A when consult array lists EFW first — failing result: EFW dot appears left of QC).
2. Expanding that same phase shows `AgentAnalysisHeader` rows in the identical vector order as criterion 1 (failing result: first `.analysis-vector` text is the lower-importance vector while header dots were corrected).
3. Hovering a header grade dot whose tooltip includes rubric text shows the vector label before the rubric/confidence body (e.g. title starts with `Quality Check` or formatted header label — failing result: tooltip is rubric text only with no vector name prefix).
4. `grep -rn 'sortJobListRubricColumns' src/ui/frontend/src/pages/JobsInReview.tsx src/ui/frontend/src/pages/JobsSkipped.tsx` still references the helper unchanged for list-table column order — this epic does not change Skipped/In Review list sort semantics unless a shared helper change is explicitly scoped to Recommended report call sites only (failing result: list-table column order tests regress without a deliberate scope decision).

## Open questions

none

## Proposed child tickets

**Monolith check:** three capabilities share one sort contract and two render sites; one child keeps header row and detail body from drifting at UAT.

#### 1: **Recommended Analysis vector order and tooltips - Katherine**

Sort Recommended Job Report Analysis phase header grade dots and expanded `AgentAnalysisHeader` rows by job-carried rubric importance descending then letter grade descending (A best); prefix vector name on header grade-dot hover tooltips. Does **not** change Skipped/In Review list tables, consult scoring, rubric persistence, or Summary/Artifacts tabs.
**Citations:** none (active catalog); honor AST-1063 / AST-1321 job-carried rubric law.
**Scope:** `src/ui/frontend/src/lib/rubricDisplay.ts` (grade-rank comparator, display-order sort, tooltip prefix); `src/ui/frontend/src/lib/recommendedJobReport.tsx` (`buildPhaseSectionGradeConfidenceRow` sort + tooltips); `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` (matching detail order); listed component tests.
**Estimate: 2**

---

## Original brief

On the recommended job page, the order of the vectors from left to right should be in descending order of importance and DESCENDING order of Grade, and the same should be in that order in the analysis detail.

Additionally, prefix the tool tip with the vector name before showing the rubric context of the grade.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
