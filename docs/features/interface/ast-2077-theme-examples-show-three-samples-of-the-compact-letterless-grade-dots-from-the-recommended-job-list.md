# AST-2077 — Theme Examples: show three samples of the compact (letterless) grade dots from the Recommended Job List

<!-- linear-archive: AST-2077 archived 2026-10-16 -->

## Linear archive (AST-2077)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2077/theme-examples-show-three-samples-of-the-compact-letterless-grade-dots  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-2042 — User Theme  
**Blocked by / blocks / related:** parent: AST-2042

### Description

## Susan's report

\[fix\]  Please include three samples of the compact grade dots as seen on the Recommended Job List.

## As-is

Theme Examples (`AdminThemeExamples.tsx`) shows only **lettered** grade dots (`grade-dot dot-<g>` with the letter inside): the sample table's Grade column, the A–F/X grade row, and (from [AST-2064](https://linear.app/astralcareermatch/issue/AST-2064)) one row per grade-color option (Deep, Soft, Classic). The Recommended Job List's compact dots are **letterless** (`grade-dot-letterless`, drawn by `PhaseAnalysisLines` / `recommendedJobReport.tsx` `gradeDot(…, letterless)`, one line of dots per analysis phase). None appear on Theme Examples, so there's no way to judge how the compact dots read in each palette or grade-color option.

## To-be

Theme Examples shows three samples of the compact letterless grade dots, rendered with the same markup/classes the Recommended Job List uses, so they inherit each panel's (and each option row's) grade colors.

**Confirm — Chuckles' read of "three samples":** one compact sample next to each of the three grade-color option rows (Deep, Soft, Classic), in every palette panel, so the letterless contrast of each option is visible (the AST-2064 plan flagged Soft's letterless dots as the weak spot). Alternative read: three sample compact lines (like three jobs' phase lines) per panel, in the panel's live grade colors. Say which.

## Suggested engineer

Ada Lovelace — owner of [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047) and [AST-2064](https://linear.app/astralcareermatch/issue/AST-2064) (Theme Examples page, grade-color options).

### Comments

#### radia — 2026-10-09T00:06:26.608Z
[code-rubric] PROCEED (Commit: bdb19f46d) Letterless grade-dot samples

#### betty — 2026-10-09T00:03:28.446Z
[bug-repro]
`origin/sub/AST-2042/AST-2077-compact-grade-dots` @ `83ccb6be2` · repro lands red, awaits fix

Manifest: `docs/test-bible/frontend/pages.md` § AST-2077 (one Vitest file; 1 red, 6 green on the pre-fix tree). This sub carries only AST-2077 test/bible deltas.

#### joan — 2026-10-09T00:01:55.722Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T00:01:34.152Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md § AST-2064 (test_AdminThemeExamples.test.tsx) — missing coverage — no case asserts a per-option `.recommended-list-phase-grade-row` of letterless `grade-dot dot-<g> grade-dot-letterless` A–X carrying the set's inline tokens; existing AST-2047/2064 cases are unaffected by the sibling wrapper.

#### ada — 2026-10-09T00:00:46.077Z
`origin/sub/AST-2042/AST-2077-compact-grade-dots` @ `de2459c38` · compact sample beside options

---

_Implementation detail may live in git history on `origin/dev`._
