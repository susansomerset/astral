# AST-2076 — Light themes: nav still dark yellow — use the header purple for nav headers and the selected nav item

<!-- linear-archive: AST-2076 archived 2026-10-16 -->

## Linear archive (AST-2076)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2076/light-themes-nav-still-dark-yellow-use-the-header-purple-for-nav  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-2042 — User Theme  
**Blocked by / blocks / related:** parent: AST-2042

### Description

## Susan's report

\[fix\]

Oh dear.  That section header font color should be used consistently in nav headers, and selected navigation text and highlight left-border (everywhere the dark yellow is currently used), because I'm still seeing dark yellow in the nav.

## As-is

[AST-2063](https://linear.app/astralcareermatch/issue/AST-2063) added a `--heading` token (Light palettes: `#241b33`, the Dark theme's purple) and moved section/page headers onto it. The nav was not part of that change, so in the Light palettes it still shows dark yellow:

* **Nav group headers** — `.nav-group-label` uses `--nav-group-label` (`light` `#7a5a10`, `light_parchment` `#7a4f00`).
* **Selected nav link** — `.nav-link.active` text and its 3px left border use `--accent-gold` (`light` `#9a7314`, `light_parchment` `#8a5a00`).
* **Selected candidate menu item** — `.sidebar-candidate-menu-item.is-selected` text uses `--accent-gold`.

(`light_slate` uses blues for these tokens, not yellow.)

## To-be

In the Light palettes, nav group headers, the selected nav link's text and left border, and the selected candidate menu item all use the same purple as the section headers (`--heading`). Dark stays gold as today.

**Susan (on review):** We are going with the LIght coloration, btw, and we should call it --accent-contrast, shouldn't we?

**Resolved scope (Chuckles' read of the above — plan-fix plans against this):**

1. **Purple everywhere the dark yellow is used, not just the nav.** In `light` and `light_parchment`, every use of the gold accent becomes the header purple (`#241b33`, today's Light `--heading`): nav group headers, the selected nav link's text and left border, the selected candidate menu item, and the other `--accent-gold` uses (focus borders, primary buttons, labels/links). Hover and dim variants follow the same purple family.
2. **Yes — rename the token** `--accent-gold` **→** `--accent-contrast` (with `--accent-gold-hover` / `--accent-gold-dim` → `--accent-contrast-hover` / `--accent-contrast-dim`), since it is no longer gold in the Light themes. Rename every declaration and `var(--accent-gold…)` use. Dark keeps its gold *value* under the new name. Fold `--heading` / `--nav-group-label` into it where they now carry the same value. Exact token consolidation is plan-fix's call.
3. `light_slate` **keeps its blue accent** (it was never yellow) — the rename applies, the value doesn't change. Susan: say so on the ticket if Slate should go purple too.

## Suggested engineer

Ada Lovelace — owner of [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047) and [AST-2063](https://linear.app/astralcareermatch/issue/AST-2063) (`App.css` palettes, `--heading`).

### Comments

#### radia — 2026-10-09T01:38:11.236Z
[code-rubric] PROCEED (Commit: e15b17f6f) Light accent purple, token rename

#### betty — 2026-10-09T01:27:49.455Z
[bug-repro]
`origin/sub/AST-2042/AST-2076-light-accent-contrast` @ `b3e575759` · repro lands red, awaits fix

Manifest: `docs/test-bible/frontend/pages.md` § AST-2076 (one Vitest file; 1 red, 7 green on the pre-fix tree). This sub carries only AST-2076 test/bible deltas.

#### joan — 2026-10-09T01:26:27.423Z
[validate-plan fix-mode] LANDED

#### joan — 2026-10-09T01:25:44.642Z
[board-joan]  CANON: REVISE
What: pattern.ui.shared-button-roles (draft) — rename `--accent-gold` to `--accent-contrast` and fix in-flight prose (accent is palette-dependent, not always gold) — align draft with global token rename

#### betty — 2026-10-09T01:25:22.046Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md § AST-2047 AC4 (test_AdminThemeExamples.test.tsx:162) — broken test — the Light-pairwise-differ key list names `--accent-gold`, undefined after the rename (silently vacuous, still passes via `--bg-deep`); retarget to `--accent-contrast`, and update the stale name in bible frontend/root.md:45 + pages.md. No new repro test: Light accent values are a palette choice for UAT, and the AST-2049 guard (every `var(--x)` defined) already catches an incomplete rename.

#### ada — 2026-10-09T01:24:39.202Z
`origin/sub/AST-2042/AST-2076-light-accent-contrast` @ `89fb5f753` · rename + Light purple accent

#### chuckles — 2026-10-09T01:21:45.888Z
Stalled since 00:01: the release pass seeded the branch and moved this to Todo but assigned it to Ada, and the bug-fix watcher only picks up Todo bugs assigned to Chuckles. Kicked — reassigned to Chuckles at Todo; bug-fix starts plan-fix on its next poll.

#### susan — 2026-10-09T01:20:42.699Z
@chuckles What's the holdup on this issue?

---

_Implementation detail may live in git history on `origin/dev`._
