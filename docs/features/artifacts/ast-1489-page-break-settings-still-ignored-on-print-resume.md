# AST-1489 — Page break settings still ignored on Print Resume

<!-- linear-archive: AST-1489 archived 2026-09-09 -->

## Linear archive (AST-1489)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1489/page-break-settings-still-ignored-on-print-resume  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1483 — Resume page break settings don't work  
**Blocked by / blocks / related:** parent: AST-1483

### Description

Still isn't working.  It is rendering on the fly, correct?  A change to the text or a change to the page break setting is incorporated every time I click "Print Resume", right?

## As-is

After AST-1487, builder emit honors **saved **`page_break_policy`, but Base/JAR Print Resume always `GET`s persisted structure and ignores unsaved page-break dropdown edits in the structure editor — so Print still looks like settings “don’t work” unless Save sections ran first.

## To-be

Clicking Print Resume applies the operator’s current page-break dropdown choices (Keep block together / New page before / Flow uninterrupted), including when they have not clicked Save sections since the last edit — via auto-save before print and/or printing from live structure rows. Susan approved widen-to-UI (Option 1) on 2026-08-26.

## Suggested engineer

Hedy Lamarr (AST-1487 sibling)

### Comments

#### radia — 2026-08-26T18:27:39.060Z
[code-rubric] PROCEED (Commit: d119eb2c) auto-persist before Print

#### betty — 2026-08-26T18:21:41.373Z
[bug-repro]
`origin/sub/AST-1483/AST-1489-page-break-settings-still-ignored-on-print` @ `9225ae33` · repro lands red, awaits fix

#### joan — 2026-08-26T18:18:21.506Z
[board-joan]  CANON: OK

#### betty — 2026-08-26T18:08:34.118Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md + components.md — no print-without-save structure PUT coverage; AST-1337/AST-1350 Print mocks break — add Base+JAR print-before-PUT cases; extend Print mock handlers

#### hedy — 2026-08-26T18:07:56.574Z
origin/sub/AST-1483/AST-1489-page-break-settings-still-ignored-on-print @ `4df25b08` · auto-save before print

#### susan — 2026-08-26T16:04:25.048Z
Option 1

#### chuckles — 2026-08-26T16:00:36.836Z
@susan — scope gate on AST-1489 (Hedy plan-fix).

AST-1487 emit is correct for **saved** `page_break_policy`. Print Resume always builds from persisted structure (`GET /candidate/resume/base`), not the live page-break dropdown. Unsaved dropdown changes never reach print — that matches your “on the fly?” question.

Parent AST-1483 Component/Technical scope is builder-only (“no UI changes”). Fixing the residual UAT fail needs UI work (auto-save before Print, or print from live `structureRows`, and/or an operator signal that Print uses saved structure only).

Need your call:
1. **Widen scope** — amend AST-1489 / parent to include Base + JAR Print/structure-authoring UI, then Hedy re-plans Plan Ready, or
2. **Works as designed** — operators must Save sections before Print; close AST-1489 (and keep the prior answer on the parent).

Holding at Plan Discuss, assignee → you.

#### hedy — 2026-08-26T15:49:50.802Z
[scope-gate]

After AST-1487, `_print_section_page_break_css` on tip maps saved `page_break_policy` correctly (verified: `build_base_resume` / session emit — no hard `#prior-experience` always-break; `page_break_before` on `education_certifications` → `#education { page-break-before: always; }`).

Residual UAT failure is the Print wire path, not emit:

- Base Print (`ArtifactsBaseResumeContent.handlePrint`) always `GET /candidate/resume/base` → `build_base_resume` → **persisted** `artifacts.resume_structure` only (comment in code: "not editor buffer").
- JAR Print Resume same pattern: `GET /candidate/resume/<job_id>` → candidate structure from DB.
- Page-break dropdown edits live in `structureRows` until **Save sections** (or content Save with structure authoring). Unsaved policy changes never reach `_print_section_page_break_css`.
- Susan’s question on the parent (“rendering on the fly… every time I click Print Resume?”) matches this gap.

**Proposed fix kind (needs scope amend):** frontend — e.g. auto-save structure before Print, or print from live `structureRows` (session-style), and/or clear operator signal that Print uses saved structure only. Possibly touch `ArtifactsBaseResumeContent.tsx` / `JobAnalysisReportModal.tsx` (and only builder if a new print payload is required).

**Parent AST-1483 scope that does not cover this:**

> Component: `src/core/builder.py` — restore structure→print page-break CSS helper…
> Technical: `_print_section_page_break_css` + `_emit_html_document` print-block injection only.
> “No config/API/UI changes expected”

Cannot Plan Ready a builder-only re-do of AST-1487 — emit already honors **saved** policies. Need Component/Technical scope widened to the Print/structure-authoring UI (or Chuckles/Archie confirm operator-must-Save is intended and this bug should close as works-as-designed).

@chuckles

---

_Implementation detail may live in git history on `origin/dev`._
