# AST-2056 — gap: tests for resume editor autosave (retarget header-Save cases)

<!-- linear-archive: AST-2056 archived 2026-10-16 -->

## Linear archive (AST-2056)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2056/gap-tests-for-resume-editor-autosave-retarget-header-save-cases  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2041 — Autosave resume artifacts for base and job resumes  
**Blocked by / blocks / related:** parent: AST-2041

### Description

## What this implements

Test gap filed from Betty's `[board-betty] TESTS: REVISE` on [AST-2051](https://linear.app/astralcareermatch/issue/AST-2051). The resume editors (structure mode / jobPersistence) no longer render header Save/Cancel outside Generate review; section bodies autosave after `AUTOSAVE_MS`. This ticket retargets the existing tests that click header Save on those paths, and adds the missing autosave coverage. Product change lives on AST-2051 only.

## Scope

**Component scope**

* `tests/component/frontend/components/test_ArtifactEditor.test.tsx`: **modified**. Retarget the header-Save tests outside review on structure-mode/jobPersistence resume editors to autosave (advance `AUTOSAVE_MS`, assert PUT). Cases: AST-553 job persistence PUT, AST-996/AST-1351 experience array Save, AST-1351 legacy experience Save aborts, AST-1382 content Save bundles resume_structure, AST-1476 page-break + content Save, AST-1410 no-snapshot Cancel re-GET (retarget to a shapesKey job editor), AST-1480 rename + Save, AST-1593 job_resume Save, AST-1480 structure bodies editable + Save, AST-1577 bodyShape resume_content Save. Add new coverage: body edit → PUT after `AUTOSAVE_MS` with no Save button outside review; Save/Cancel present during Generate review; a timer queued before Generate does not fire during review (AST-905); an in-flight autosave keeps dirty when a newer edit is pending; jobPersistence autosave does not call `onSaved` (unmount flush still does).
* `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`: **modified**. Retarget the AST-1577 "Save PUTs base_resume leaf" case to autosave.
* `docs/test-bible/frontend/components.md` / `docs/test-bible/frontend/pages.md`: **modified**. Bible entries for ArtifactEditor / ArtifactsBaseResumeContent reflect autosave in place of header Save on resume editors.

**Technical scope**

* Test files: modified test cases (fake timers + PUT assertions in place of Save clicks) and new test cases for the autosave / review-guard / in-flight-dirty contract. No product src.
* Bible: modified entries only.

## Boundaries

Test tree + bible only, no product src (AST-2051 owns `ArtifactEditor.tsx`). Unaffected suites stay untouched: the shapesKey fixed-shape Cancel, rubric/criteria review-mode Save, and the JobAnalysisReportModal suite.

## Notes for planning

Plan context: `docs/features/artifacts/ast-1459-resume-editor-is-not-working-properly.md` `## Bug: AST-2051`. The tests must be red against pre-fix product and green once AST-2051 lands (`[bug-repro]`).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-2041-resume-autosave`, child `sub/AST-2041/AST-2056-resume-autosave-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-08T20:49:59.441Z
[code-rubric] PROCEED (Commit: 4cf623ac4) Bug-repro locks autosave contract

#### ada — 2026-10-08T20:48:39.145Z
`origin/sub/AST-2041/AST-2056-resume-autosave-tests` @ `4cf623ac4` · test-fix (nothing new pushed)

- `[bug-repro]` gate (`vitest -t AST-2051`): origin/dev `ArtifactEditor.tsx` → 6 failed / 2 passed (the 2 AST-905 review guards pass trivially pre-fix); this tip → 8/8 green.
- Full manifest (ArtifactEditor + ArtifactsBaseResumeContent + JobAnalysisReportModal): 105 passed, 3 failed.
- The 3 failures are pre-existing, identical on a clean origin/dev worktree, not touched here:
  - JobAnalysisReportModal AST-1546 / AST-1350 Print Resume ×2: no "Print Resume" button
  - ArtifactsBaseResumeContent AST-1577 ui-consistency: ENOENT `canon/directives/draft/patt.artifact.ui-consistency.md`

#### betty — 2026-10-08T20:42:19.294Z
[bug-repro]
`origin/sub/AST-2041/AST-2056-resume-autosave-tests` @ `b6138b17d` · repro lands red, awaits fix

#### ada — 2026-10-08T20:36:14.236Z
`origin/sub/AST-2041/AST-2056-resume-autosave-tests` @ `8dcf62bec` · autosave test contract planned

---

_Implementation detail may live in git history on `origin/dev`._
