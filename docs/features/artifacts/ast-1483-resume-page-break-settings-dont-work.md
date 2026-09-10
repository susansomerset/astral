# AST-1483 — Resume page break settings don't work

<!-- linear-archive: AST-1483 archived 2026-09-09 -->

## Linear archive (AST-1483)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1483/resume-page-break-settings-dont-work  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Report

When everything is set to "Keep block together", there is still a page break above the Prior Experience section. When I add "New Page Before" to the section Education and Certifications, it does not page break as expected.

## As-is

Structure authoring exposes per-section page-break policies (`Keep block together` / `New page before` / `Flow uninterrupted`). After AST-1487, builder emit honors **persisted **`page_break_policy`, but Base/JAR Print Resume always rebuilds from saved structure via `GET /candidate/resume/...` — unsaved page-break dropdown edits in the structure editor never reach print, so operators still see “settings ignored” when they Print without Save sections first.

## To-be

Print Resume reflects the operator’s current page-break choices when they click Print (auto-save structure before print, or print from live structure rows), including Keep block together and New page before on Education and Certifications / Prior Experience. Experience `.role` chunks still always stay together. Builder emit for already-saved policies remains correct (AST-1487).

## Proposed steps

1. Keep AST-1487 builder mapping as landed (no re-do of emit).
2. On Base + JAR Print Resume, either auto-persist structure (including `page_break_policy`) before the resume GET/build, or pass live structure rows into the print path so unsaved dropdown changes affect the printed HTML.
3. Optionally surface that Print uses the structure about to be printed (saved or live) so operators are not surprised.
4. Cover with frontend tests for Print after page-break change without a separate Save click (Betty).

## Component scope

* `src/core/builder.py` — **modified** (AST-1487 done) — structure→print page-break CSS helper; hard-coded Prior Experience always-break removed.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — Print Resume path must apply current structure page-break policies (auto-save before print and/or print from live `structureRows`), not only a prior DB snapshot after an explicit Save.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — same Print Resume behavior for JAR Job Resume structure authoring.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** only if shared print/structure helpers need to expose live `page_break_policy` rows to the Print path.
* `tests/component/core/test_builder.py` — **modified** (Betty, AST-1487) — page-break print CSS coverage.
* `docs/test-bible/core/builder.md` — **modified** (Betty, AST-1487).
* Frontend component/page tests + bible rows (Betty) — Print after page-break edit without separate Save.

## Technical scope

* `src/core/builder.py` — `_print_section_page_break_css` + `_emit_html_document` print injection (AST-1487) — leave as landed unless Print gains a new structure payload shape.
* `ArtifactsBaseResumeContent.tsx` — **modified function **`handlePrint` (or equivalent): before `GET /candidate/resume/base`, persist current structure including `page_break_policy`, or supply live structure to the build path so print matches the editor.
* `JobAnalysisReportModal.tsx` — **modified function** Print Resume handler: same persist-or-live-structure behavior for job resume print.
* `ArtifactEditor.tsx` — **modified** only if needed to share live structure rows / save helper with Print callers.
* No new config tokens expected — AST-1474/1476 catalog and dropdown remain.

## Ancestor candidates

- [X] AST-1475 — Builder print CSS from structure page-break policies (Done child of AST-1462; landed the mapping that tip is missing after a later merge-resume)
- [ ] AST-1462 — Create and position page break (Done parent epic for operator page-break control)
- [ ] AST-1476 — Structure editor page-break dropdown on base and job (Done UI/persist slice; merge-resume onto this line reintroduced the golden hard-coded prior break)
- [ ] AST-1474 — Page-break policy config and resume_structure schema (Done catalog/normalize; still present on tip — weaker fit unless schema/default drift is found)

### Comments

#### chuckles — 2026-08-26T14:50:43.580Z
Yes — Print Resume builds HTML from the candidate’s current saved `base_resume` content and `resume_structure` (including each section’s page-break policy) at click time. A text or page-break change only shows up after that change is saved; then the next Print Resume should pick it up.

Filed from your `[bug]` comment:
- AST-1489 — page-break settings still ignored
- AST-1490 — Print Resume only contact after section reorder

Both at Discussion assigned to you for diagnosis confirm before the fix lane runs.

#### susan — 2026-08-26T14:44:21.354Z
\[bug\]

Still isn't working.  It is rendering on the fly, correct?  A change to the text or a change to the page break setting is incorporated every time I click "Print Resume", right?

Separate bug, if I move a section up or down, the print render only includes the contact information and no other content appears.

---

_Implementation detail may live in git history on `origin/dev`._
