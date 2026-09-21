# AST-1328 — gap: Analysis header job-carried / collapse tests (AST-1321)

<!-- linear-archive: AST-1328 archived 2026-08-19 -->

## Linear archive (AST-1328)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1328/gap-analysis-header-job-carried-collapse-tests-ast-1321  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1321 — Missing Vector Grades in Rubric headers  
**Blocked by / blocks / related:** parent: AST-1321

### Description

## What this implements

gap (tests): Cover Recommended Job Analysis tab headers sourcing job-carried `*_rubric` (meteorite vs gazer) and all Analysis sections default-collapsed — Betty board REVISE on AST-1327.

## Board source

[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/lib.md + components.md (AST-950) — missing job-carried/meteorite header mismatch coverage; signature change + collapse-all breaks existing AST-950 asserts (live jobdesc_rubric arity; JD default-expanded)

## As-is

No bible/test coverage for Analysis header row keyed off job-carried rubric / meteorite mismatch; existing AST-950 asserts assume live jobdesc_rubric arity and JD default-expanded.

## To-be

Bible + tests assert job-carried header grades (meteorite path) and all Analysis sections start collapsed; obsolete AST-950 live-rubric / JD-expanded asserts revised.

## Proposed change

- [X] Bible lib.md + components.md AST-950 rows → job-carried header / collapse-all (Betty qa-fix)
- [X] Revise AST-950 lib + JAR asserts; meteorite underlap bug-repro (Betty qa-fix)
- [X] Product delta: none — AST-1327 already on ftr / this tip (`a4549715`); make-fix no `src/` churn
- [X] `[bug-repro]` green on tip: `AST-1328: Analysis header uses job-carried jd_rubric when live jobdesc_rubric underlaps`

## Related

Sibling of AST-1327 (fix child). Parent AST-1321.

## Git branch (authoritative)

Parent `ftr/AST-1321-missing-vector-grades-rubric-headers`, child `sub/AST-1321/<this-id>-gap-analysis-header-tests`.

## QA test manifest

**Publish:** `origin/sub/AST-1321/AST-1328-gap-analysis-header-tests` @ `585397a4` (`merge-tests(AST-1328): origin/tests dc070e845987eb0ad41d4cbdc07c1c5d192350bf`)

**Bug-repro (must stay green on ftr product / flip red on pre–AST-1327):**

* `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `AST-1328: Analysis header uses job-carried jd_rubric when live jobdesc_rubric underlaps` (expected 2 cells vs live underlap → 1)

**Also landed:**

* Lib: `recommendedJobReport — AST-950 grade+confidence header row` (+ `AST-1328: header shows every job-carried vector…`)
* JAR AST-950 collapse-all + job-carried fixtures; AST-948 chrome → all phases collapsed
* Bible: `docs/test-bible/frontend/lib.md` shasum `43ecc406734a0f6e7204a2fbeecfb227c59275b1`
* Bible: `docs/test-bible/frontend/components.md` shasum `5329df3958a72cd677b737bf86e5a18f1731f526`

**Run:**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_ReportSectionList.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  --testNamePattern="AST-950|AST-1328"
```

**Note:** Gap child — product already on `origin/ftr/AST-1321-missing-vector-grades-rubric-headers` (AST-1327). No further `src/` for make-fix; test-fix verifies green.

### Comments

#### radia — 2026-08-12T05:06:10.608Z
[code-rubric] PROCEED (Commit: 585397a4) Bug-repro + bible gap closed

fix-now: none. discuss: none. AST-950 suite + bible migrated to job-carried Analysis headers / collapse-all; [bug-repro] asserts meteorite header mismatch closed.

#### ada — 2026-08-12T05:04:48.583Z
`origin/sub/AST-1321/AST-1328-gap-analysis-header-tests` @ `585397a4`

[bug-repro] green; full manifest `AST-950|AST-1328` 10 passed.

#### ada — 2026-08-12T05:03:58.185Z
`origin/sub/AST-1321/AST-1328-gap-analysis-header-tests` @ `585397a4` · no src churn; bug-repro green

#### betty — 2026-08-12T05:02:51.726Z
[bug-repro]
`origin/sub/AST-1321/AST-1328-gap-analysis-header-tests` @ `585397a4` · meteorite header repro green on ftr

#### betty — 2026-08-12T04:57:55.054Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/lib.md + components.md (AST-950) — missing job-carried/meteorite header + collapse-all coverage; existing AST-950 asserts still live-artifact arity / JD default-expanded — gap child owns the revise

#### joan — 2026-08-12T04:57:42.168Z
[board-joan]  CANON: OK

Betty-only test/bible gap (no product `src/`): revises AST-950 component tests and `docs/test-bible/frontend/*` to assert AST-1327 job-carried `*_rubric` header identity and all-collapsed Analysis — documents behavior already required by `pattern.layers.import-discipline` and the AST-1063/1064 consumer contract. Role split intact (`orch.roles.betty-owns-test-tree`, `astral.git.engineer-test-tree-ban`). No statute or pattern corpus change needed.

context_tokens≈22000

#### ada — 2026-08-12T04:57:13.653Z
`origin/sub/AST-1321/AST-1328-gap-analysis-header-tests` @ `9fd51dbae6c64302a47db8b9902aba6ac530e461` · bible+tests gap planned

---

_Implementation detail may live in git history on `origin/dev`._
