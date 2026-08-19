# AST-1327 — fix: Missing Vector Grades in Rubric headers (AST-1321)

<!-- linear-archive: AST-1327 archived 2026-08-19 -->

## Linear archive (AST-1327)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1327/fix-missing-vector-grades-in-rubric-headers-ast-1321  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1321 — Missing Vector Grades in Rubric headers  
**Blocked by / blocks / related:** parent: AST-1321

### Description

## What this implements

Fix missing per-vector grade icons in Recommended Job Analysis tab section headers for meteorite jobs (gazer jobs OK), sourcing header/body vectors from analysis-time job_data / job-carried rubric rather than the live candidate rubric; collapse all Analysis-tab sections by default.

## Ancestor context (Susan-approved)

AST-1063 — job-carried rubric hydration (`docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md`). Patch that existing plan doc (plan-fix — never create a new features doc).

## As-is

Analysis tab phase headers miss the full per-vector grade row on meteorites; JD Analysis opens expanded by default.

## To-be

Every graded vector's grade shows in Analysis section headers (meteorites included) from job-carried / job_data rubric; all Analysis-tab sections start collapsed (other tabs unchanged).

## Proposed change

- [X] `buildPhaseSectionGradeConfidenceRow` columns from job-carried `*_rubric` / grades-only via `buildJobListRubricColumnsForGroup` (no live candidate artifacts)
- [X] `JobAnalysisReportModal` Analysis metadata + body labels from job-carried rubric; live artifact only for “show rubric” content
- [X] All Analysis-tab sections `default_expanded: false` (Summary/Artifacts unchanged)
- [X] `JobDetail` typing includes optional `*_rubric` fields

## Citations

AST-1063 job-carried `*_rubric` law; Analysis tab header chrome from AST-950 era UI.

## Boundaries

Does not resurrect AST-1059/1063 ftr names. Does not own unrelated list-table grouping (AST-1064) unless required by this header bug.

## Git branch (authoritative)

Parent `ftr/AST-1321-missing-vector-grades-rubric-headers`, child `sub/AST-1321/<this-id>-fix-missing-vector-grades-headers`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-12T04:55:21.189Z
[code-rubric] REVIEW (Commit: a4549715) Job-carried headers; test gap

fix-now: none. Discuss: stale AST-950 tests → AST-1328; meteorite rubric-modal content still live-key (headers fixed). Clean product path for Analysis header grades + collapse-all.

#### ada — 2026-08-12T04:52:44.774Z
`origin/sub/AST-1321/AST-1327-fix-missing-vector-grades-headers` @ `a45497157d422dd9194830c9e7c8edd740cd95f4`

Lighter check (no qa-fix/[bug-repro] on this ticket): `tsc -b --noEmit` green. Existing AST-950 suite red as Betty flagged (signature + JD collapse) — owned by sibling gap AST-1328, not patched here.

#### ada — 2026-08-12T04:51:42.379Z
`origin/sub/AST-1321/AST-1327-fix-missing-vector-grades-headers` @ `a45497157d422dd9194830c9e7c8edd740cd95f4`

#### betty — 2026-08-12T04:49:21.663Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/lib.md + components.md (AST-950) — missing job-carried/meteorite header mismatch coverage; signature change + collapse-all breaks existing AST-950 asserts (live jobdesc_rubric arity; JD default-expanded)

#### joan — 2026-08-12T04:49:12.604Z
[board-joan]  CANON: OK

Frontend-only fix extends the existing AST-1064 job-carried rubric consumer (`buildJobListRubricColumnsForGroup` / `jobCarriedRubricKey`) to the Recommended Analysis tab — aligns with `pattern.layers.import-discipline` and `astral.layers.import-direction` (UI paints flattened API payload, no live-artifact column identity). Grade-field → `*_rubric` pairing stays config-derived; no consult/API or `JOBS_UI_GRADE_RUBRIC` map changes. No statute or pattern update required.

context_tokens≈18000

#### ada — 2026-08-12T04:48:09.640Z
`origin/sub/AST-1321/AST-1327-fix-missing-vector-grades-headers` @ `39aa6d40b9afb9bbd43ed38388c86e76e57c45b9` · job-carried Analysis headers

---

_Implementation detail may live in git history on `origin/dev`._
