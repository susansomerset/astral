# AST-1487 — Restore builder page-break print CSS from structure

<!-- linear-archive: AST-1487 archived 2026-09-09 -->

## Linear archive (AST-1487)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1487/restore-builder-page-break-print-css-from-structure  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1483 — Resume page break settings don't work  
**Blocked by / blocks / related:** parent: AST-1483

### Description

## What this implements

Restore builder print CSS mapping from `artifacts.resume_structure.sections[*].page_break_policy` so operator page-break settings affect printed base and job resumes. Regression fix for AST-1462 / AST-1475 work dropped from `origin/dev` tip.

## Boundaries

Does not change config catalog, API, or React structure editor — those slices remain as shipped on `origin/dev`.

## Scope

## Component scope

- [X] `src/core/builder.py` — **modified** — restore structure→print page-break CSS helper; remove hard-coded Prior Experience always-break so saved policies win on emit.
- [X] `tests/component/core/test_builder.py` — **modified** (Betty) — restore/keep AST-1475 print-policy coverage and stop asserting unconditional `#prior-experience { page-break-before: always }`.
- [X] `docs/test-bible/core/builder.md` — **modified** (Betty) — manifest rows for the restored builder assertions.

## Technical scope

- [X] `src/core/builder.py` — **new function** `_print_section_page_break_css` (or equivalent): for each structure-ordered body section, read `page_break_policy`, map `page_break_before` / `avoid_split` / `normal` to print CSS via `_html_section_dom_id`; soft-default invalid/missing to `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`.
- [X] `src/core/builder.py` — **modified function** `_emit_html_document`: drop hard-coded `#prior-experience { page-break-before: always; }`; inject the helper CSS in the print block; leave `.role { page-break-inside: avoid; }` unconditional.
- [X] No config/API/UI changes expected — AST-1474 tokens/labels and AST-1476 dropdown persistence are already on `origin/dev`; this bug is the missing emit half.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1483-resume-page-break-settings-dont-work`, child `sub/AST-1483/<this-id>-fix-restore-builder-page-break-print-css`. Created at bug-fix dispatch.

## Notes for planning

Ancestor context: AST-1475 (Done). Prior implementation commit `7fb201ea`. Susan symptom: all `Keep block together` still forces break before Prior Experience; `New page before` on Education and Certifications has no effect.

### Comments

#### radia — 2026-08-26T05:05:54.933Z
[code-rubric] PROCEED (Commit: f2d3a0d0) restore structure print CSS

#### hedy — 2026-08-26T05:01:13.214Z
ORPHANED — parent Done, no origin/ftr. Lands straight to dev after review-fix clears, not via merge-child/prep-uat.

#### betty — 2026-08-26T04:59:43.580Z
[bug-repro]
`origin/sub/AST-1483/AST-1487-fix-restore-builder-page-break-print-css` @ `4092da2e` · repro lands red, awaits fix

#### joan — 2026-08-26T04:57:29.766Z
[board-joan] CANON: OK

#### betty — 2026-08-26T04:52:35.922Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/builder.md — no AST-1475 page-break coverage; TestAst1020GoldenStylesheet breaks — restore TestAst1475PageBreakPrintCss + flip AST-1020 prior-break assert

#### hedy — 2026-08-26T04:51:48.139Z
`origin/sub/AST-1483/AST-1487-fix-restore-builder-page-break-print-css` @ `a510ed3f2560f39c6aa5888bf8ca82bd16efabee` · restore print CSS mapping

---

_Implementation detail may live in git history on `origin/dev`._
