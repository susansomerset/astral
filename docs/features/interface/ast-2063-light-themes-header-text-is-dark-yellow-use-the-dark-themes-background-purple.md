# AST-2063 — Light themes: header text is dark yellow — use the Dark theme's background purple

<!-- linear-archive: AST-2063 archived 2026-10-16 -->

## Linear archive (AST-2063)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2063/light-themes-header-text-is-dark-yellow-use-the-dark-themes-background  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-2042 — User Theme  
**Blocked by / blocks / related:** parent: AST-2042

### Description

## Susan's report

\[fix\]

Instead of a dark yellow color for header text, use the background purple color from the dark theme.

## As-is

In the Light palettes (`light`, `light_parchment`, `light_slate`), headers that are colored with `var(--accent-gold)` (page titles `.list-page-title` / `.dep-title`, `.modal-title`, `.dep-section-label`, `.job-analysis-upshot-heading`, …) render in a dark yellow/gold.

## To-be

In the Light palettes, that header text renders in the Dark theme's background purple (Chuckles' read: the Dark `--bg-card` `#1a1424` / `--bg-elevated` `#241b33` family — confirm which purple you mean), and Dark theme headers stay gold as today.  

(Your read is correct.)

## Suggested engineer

Ada Lovelace — owner of [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047) (theme registry, `App.css` palettes, Theme Examples page, `uiConfig.ts`).

### Comments

#### radia — 2026-10-08T23:02:07.725Z
[code-rubric] PROCEED (Commit: 8bcf57c98) Light headings use --heading

#### radia — 2026-10-08T23:01:22.186Z
[code-rubric] REVIEW (Commit: 85582d39c) Sub branch stacks extra fixes

#### joan — 2026-10-08T22:56:47.524Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T22:56:19.916Z
[board-betty] TESTS: OK

#### ada — 2026-10-08T22:55:36.127Z
`origin/sub/AST-2042/AST-2063-light-header-purple` @ `a0e5c5d7c` · --heading token, six rules

---

_Implementation detail may live in git history on `origin/dev`._
