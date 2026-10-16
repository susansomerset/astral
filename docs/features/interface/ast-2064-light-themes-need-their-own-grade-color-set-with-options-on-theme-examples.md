# AST-2064 — Light themes need their own grade-color set, with options on Theme Examples

<!-- linear-archive: AST-2064 archived 2026-10-16 -->

## Linear archive (AST-2064)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2064/light-themes-need-their-own-grade-color-set-with-options-on-theme  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2042 — User Theme  
**Blocked by / blocks / related:** parent: AST-2042

### Description

## Susan's report

\[fix\]

The light theme will need a parallel set of grade colors, this set does not appear very well. Please include options in the theme examples page.

## As-is

The Light palettes' `--grade-a … --grade-x` values are near-copies of Dark's bright grade colors, so the A–F/X grade dots read poorly on light backgrounds, and Theme Examples shows only that one set per palette.

## To-be

The Light themes get a separate grade-color set designed for light backgrounds, and Theme Examples shows 2–3 grade-color options side by side (grade dots A, B, C, D, F, X) so Susan can pick one. Dark's grade colors stay unchanged.

## Suggested engineer

Ada Lovelace — owner of [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047) (theme registry, `App.css` palettes, Theme Examples page, `uiConfig.ts`).

### Comments

#### chuckles — 2026-10-08T23:38:49.501Z
Radia fix-now (AST-2055 `contact.py` / `meteorite.py` / `slack.py` / `requirements.txt`) overridden: all of it is already on `origin/dev` (#266) and came in through the required `sync(dev)` merge, since ftr is behind dev. Merging into ftr just catches it up to dev; the ftr→dev PR shows no change. Product delta is the 4 planned files only. → User Testing.

#### radia — 2026-10-08T23:38:48.503Z
[code-rubric] REVIEW (Commit: 9e116369a) Drop AST-2055 product from sub

#### ada — 2026-10-08T23:34:03.915Z
[check-linear] blocked: sync-child ftr merge can't be committed — engineer pre-commit hook

`sync-child.sh sub/AST-2042/AST-2064-light-grade-colors --ftr AST-2042-user-theme` → exit 3, conflict in `docs/features/interface/ast-2047-…-user-theme.md` (AST-2063/2065 sections on ftr vs AST-2064 section on this sub — adjacent appends). Resolved (ftr sections, then AST-2064 last), but `git commit` of the merge trips the engineer hook: 15 `tests/` + `docs/test-bible/` paths inherited from ftr (Betty's AST-2065 tests), all byte-identical to `origin/ftr/AST-2042-user-theme`. Clean syncs never hit pre-commit, so this only bites on a conflicted ftr merge carrying test-tree changes.

Need a call: OK to commit this one `sync(ftr)` merge with `--no-verify` (no test-tree content authored), or route another way? Merge aborted, worktree clean; resolved doc saved at `debug/spikes/ast-2064/plan-doc-ftr-merge-resolved.md`. Ticket left at Tests Ready, no product edits made.

#### betty — 2026-10-08T23:32:51.343Z
[bug-repro]
`origin/sub/AST-2042/AST-2064-light-grade-colors` @ `29d3b5093` · repro lands red, awaits fix

Manifest: `docs/test-bible/frontend/pages.md` § AST-2064. Heads-up: `AdminThemeExamples — AST-2047 > renders one labeled panel…` is red on this sub because AST-2065 retargeted its mock to `/api/ui_config`. That is not AST-2064 scope; it turns green when AST-2065 merges, so leave `uiConfig.ts` alone.

#### joan — 2026-10-08T22:56:05.618Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T22:55:27.426Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md § AST-2047 — missing coverage — no test renders the new Grade color options rows (`test_AdminThemeExamples.test.tsx` ui_config mock has no `theme_example_grade_sets`, so the block never renders) and nothing checks each set's `tokens` keys are real token-block names (a typo silently no-ops); add one page case (labeled rows, inline `--grade-*` style, `.theme-examples-grade` still exactly A–X) + one `TestAst2047ThemeRegistry`-style config case. Product-scope note for Chuckles: `uiConfig.ts` still fetches `/api/system/ui_config` (404 → catch-all) on ftr and this sub, so the options block — and the page — never render in a browser until that URL is fixed; plan's "4 passed" is now 5 (AST-2049 guard).

#### ada — 2026-10-08T22:54:23.928Z
`origin/sub/AST-2042/AST-2064-light-grade-colors` @ `bcc35e8fe` · Deep Light grades, three options

---

_Implementation detail may live in git history on `origin/dev`._
