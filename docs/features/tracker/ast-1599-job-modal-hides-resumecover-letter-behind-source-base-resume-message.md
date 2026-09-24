# AST-1599 — Job modal hides resume/cover letter behind source-base-resume message

<!-- linear-archive: AST-1599 archived 2026-09-24 -->

## Linear archive (AST-1599)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1599/job-modal-hides-resumecover-letter-behind-source-base-resume-message  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1588 — Support “job.artifacts.job_resume” and “job.artifacts.cover_letter”as artifacts  
**Blocked by / blocks / related:** parent: AST-1588

### Description

## Susan report (verbatim)

[bug]

Artifacts generated for a recommended job, all tasks completed successfully.  For some reason, the job modal for that job no longer shows the resume and cover letter, just a (wrong and stupid) message that there was no base resume to reference:

`**SummaryAnalysisArtifactsDiscussion**

### Source base resume

No pinned base resume for this build`

There was no request to change UI features or functionally beyond the support of the artifact table as the source for the job resume and cover letter. Do not reference the sources on the job modal.

## As-is

After successful artifact generation for a recommended job, the job modal no longer shows the resume and cover letter content; it shows a "Source base resume / No pinned base resume for this build" message instead.

## To-be

The job modal shows the resume and cover letter as before (artifact-table-backed bodies). The modal must not reference or display source / base-resume provenance UI.

## Suggested engineer

Ada Lovelace (sibling AST-1593 — job artifact consumer / JAR-UI inventory)

## Proposed change

- [X] Remove `renderSourceBaseResumeBlock` and all Artifacts-pane call sites (in-progress / empty / populated)
- [X] Remove source-base-resume state + fetch `useEffect` + related imports from `JobAnalysisReportModal.tsx`
- [X] Delete unused `jobBaseResumeArtifactId` / `fetchOperativeBaseResume` from `recommendedJobReport.tsx`
- [X] Keep Artifacts pane otherwise (Generate / Cancel / ArtifactEditor); no provenance UI; no `resume_content` SoT fallbacks

## QA test manifest (AST-1599)

1. **[bug-repro]** `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1599"`

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1599"
```

**Pass criterion (test-fix):** [bug-repro] flips red→green after make-fix removes the Source base resume panel.

**Bible:** `docs/test-bible/frontend/components.md` § AST-1599; `docs/test-bible/frontend/lib.md` § AST-1585 obsolete note.

### Comments

#### radia — 2026-09-06T15:55:25.455Z
[code-rubric] PROCEED (Commit: 292029f5) JAR provenance panel removed

#### betty — 2026-09-06T15:50:16.234Z
[bug-repro]
`origin/sub/AST-1588/AST-1599-job-modal-hides-resume-cover` @ `be6df5f4` · repro lands red, awaits fix

#### betty — 2026-09-06T15:45:39.100Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § AST-1585 + test_JobAnalysisReportModal — AST-1585 Source base resume (and lib AST-1585 helpers if exports deleted) — assert panel/gap copy the fix removes; no repro coverage that Artifacts tab omits Source base resume and shows job_resume/cover editors

#### joan — 2026-09-06T15:45:14.495Z
[board-joan]  CANON: OK

context_tokens≈68000

#### ada — 2026-09-06T15:43:51.388Z
`origin/sub/AST-1588/AST-1599-job-modal-hides-resume-cover` @ `6795552489ecf00d7be7c40631c613cc1f0ed2dd` · remove JAR provenance UI

---

_Implementation detail may live in git history on `origin/dev`._
