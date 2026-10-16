# AST-2114 — Resume editor search shows every Experience job instead of only the matching ones

<!-- linear-archive: AST-2114 archived 2026-10-16 -->

## Linear archive (AST-2114)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2114/resume-editor-search-shows-every-experience-job-instead-of-only-the  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-2046 — Resume Edit Overhaul  
**Blocked by / blocks / related:** parent: AST-2046

### Description

## Susan's UAT comment (verbatim)

> \[fix\]
>
> When searching, where patterns match within experience subelements, display only the subelements that match the pattern, so I would see "Core Competencies" and "Experience", but within "Experience" I would only see one or two of the sections that match the pattern.

## As-is

A search that matches text inside one or more Experience jobs keeps the Experience section visible with every job entry inside it shown.

## To-be

Inside the Experience section, only the job entries (subelements) whose content matches the search are shown. Other matching sections, such as Core Competencies, still show as today.

## Suggested engineer

Katherine Johnson. Owner of `ResumeContentEditor` / `ResumeSectionRow` / `ExperienceJobsEditor` in [AST-2083](https://linear.app/astralcareermatch/issue/AST-2083).

Parent: [AST-2046](https://linear.app/astralcareermatch/issue/AST-2046) (Resume Edit Overhaul).

### Comments

#### radia — 2026-10-10T04:02:36.616Z
[code-rubric] PROCEED (Commit: d0f64342a) Experience job search filter

#### katherine — 2026-10-10T03:48:36.585Z
`origin/sub/AST-2046/AST-2114-search-experience-subelements` @ `d0f64342a` · tests passed

Repro gate: both `[bug-repro]` cases (test_ExperienceJobsEditor "renders only visible indexes…", test_ResumeContentEditor "a job-text match shows only matching jobs…") fail with the three product files at their pre-fix versions (`304535727^1`) and pass at `304535727`.
Manifest item 1: 42 passed (42). Item 2: `tsc -b --noEmit` clean; eslint on the three files shows only the pre-existing `ExperienceJobsEditor.tsx` set-state-in-effect error (AST-2083 baseline, L65 → L67), not touched by this fix.

#### betty — 2026-10-10T02:46:38.461Z
[bug-repro]
`origin/sub/AST-2046/AST-2114-search-experience-subelements` @ `0eb45a64b` · repro lands red, awaits fix

#### joan — 2026-10-10T02:44:29.840Z
[board-joan]  CANON: OK

#### betty — 2026-10-10T02:39:30.093Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § AST-2083 — missing coverage — no test filters Experience jobs by search: `test_ResumeContentEditor` "search filters…" checks rows only, and its `JOBS` fixture has one job. Needed: a two-job repro (search `acme`, expand Experience, only Acme renders; empty query or a title match like `exper` shows all; hidden jobs kept in the saved array, no PUT on filter) plus `test_ExperienceJobsEditor` `visible` cases (filtered render, original indexes kept, Add role hidden). No existing test breaks.

#### katherine — 2026-10-10T02:25:38.498Z
`origin/sub/AST-2046/AST-2114-search-experience-subelements` @ `7fa34f445` · per-job search filter planned

---

_Implementation detail may live in git history on `origin/dev`._
