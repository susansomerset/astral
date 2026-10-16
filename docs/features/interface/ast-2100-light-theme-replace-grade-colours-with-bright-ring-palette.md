# AST-2100 — Light theme: replace grade colours with "Bright + ring" palette

<!-- linear-archive: AST-2100 archived 2026-10-16 -->

## Linear archive (AST-2100)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2101

### Description

## Purpose

On the Light theme the grade dots are hard to tell apart. B, C, D and F sit in one dark brown-red band, and the closest pairs are only about 7 apart in OKLab distance (B–C 7.1, C–D 7.2 on today's `origin/dev` values). That defeats the point of a grade dot, which is to show the grade at a glance. The "Bright + ring" set picked in the Grade Palette Lab keeps the bright hues that already work on Dark and adds a thin darker ring so each dot keeps its edge on a light background. Its closest pair is C–D at 15.7. Dark looks exactly as it does today.

This epic makes every grade-mark setting an explicit theme setting, in two complete sets (Light and Dark):

* each grade's base settings;
* the lettered dot's added settings, which build on the base;
* the global confidence-rating settings.

With the palette chosen, the comparison scaffolding goes:

* the Tools → Theme Examples screen;
* its grade-colour candidate rows from [AST-2064](https://linear.app/astralcareermatch/issue/AST-2064) / [AST-2077](https://linear.app/astralcareermatch/issue/AST-2077);
* the examples-only Light alternates (Parchment, Slate).

Dark and Light are then the only palettes. Grade shapes are out of scope; [AST-2101](https://linear.app/astralcareermatch/issue/AST-2101) handles them and builds on these settings, so it needs this ticket first.

## Grade settings model

There are three layers of settings, and both themes declare every layer in full.

1. **Grade base (per grade).** These are what an unlettered compact dot shows: fill, ring colour and ring width.
2. **Lettered (per grade).** A lettered dot takes all of its grade's base settings and adds letter colour, letter size, letter weight and a lettered ring width.
3. **Confidence rating (global).** These cover the five bullets under a grade: on colour, off colour, off opacity, bullet size and gap. They are the same for every grade.

The setting labels below are the CSS custom properties each theme block declares, with `<g>` = a, b, c, d, f or x. The class labels stay as they are today; the markup does not change.

### 1. Grade base settings: Light set vs Dark set

| Grade | Setting | Label | Light | Dark |
| -- | -- | -- | -- | -- |
| all | Ring width, compact | `--grade-<g>-ring-width` | 1.5px | 0 (no ring) |
| A | Fill | `--grade-a` | `#2f9e44` rgb(47, 158, 68) | `#28a745` rgb(40, 167, 69) |
| A | Ring colour | `--grade-a-ring` | `#006200` rgb(0, 98, 0) | `#28a745` (same as fill; width 0) |
| B | Fill | `--grade-b` | `#f5b700` rgb(245, 183, 0) | `#ffc107` rgb(255, 193, 7) |
| B | Ring colour | `--grade-b-ring` | `#b57700` rgb(181, 119, 0) | `#ffc107` (same as fill; width 0) |
| C | Fill | `--grade-c` | `#f76707` rgb(247, 103, 7) | `#fd7e14` rgb(253, 126, 20) |
| C | Ring colour | `--grade-c-ring` | `#b41400` rgb(180, 20, 0) | `#fd7e14` (same as fill; width 0) |
| D | Fill | `--grade-d` | `#c92a3a` rgb(201, 42, 58) | `#dc3545` rgb(220, 53, 69) |
| D | Ring colour | `--grade-d-ring` | `#850000` rgb(133, 0, 0) | `#dc3545` (same as fill; width 0) |
| F | Fill | `--grade-f` | `#5c1414` rgb(92, 20, 20) | `#8b0000` rgb(139, 0, 0) |
| F | Ring colour | `--grade-f-ring` | `#210000` rgb(33, 0, 0) | `#8b0000` (same as fill; width 0) |
| X | Fill | `--grade-x` | `#7048e8` rgb(112, 72, 232) | `#a78bfa` rgb(167, 139, 250) |
| X | Ring colour | `--grade-x-ring` | `#4100a8` rgb(65, 0, 168) | `#a78bfa` (same as fill; width 0) |

### 2. Lettered settings (inherit the grade base, then add): Light set vs Dark set

| Grade | Setting | Label | Light | Dark |
| -- | -- | -- | -- | -- |
| all | Letter size | `--grade-<g>-letter-size` | 12px | 12px |
| all | Letter weight | `--grade-<g>-letter-weight` | 700 | 700 |
| all | Ring width, lettered | `--grade-<g>-ring-width-lettered` | 2px | 0 (no ring) |
| A | Letter colour | `--grade-a-ink` | `#ffffff` rgb(255, 255, 255) | `#1a1424` rgb(26, 20, 36) |
| B | Letter colour | `--grade-b-ink` | `#2b2000` rgb(43, 32, 0) | `#1a1424` rgb(26, 20, 36) |
| C | Letter colour | `--grade-c-ink` | `#1f0d00` rgb(31, 13, 0) | `#1a1424` rgb(26, 20, 36) |
| D | Letter colour | `--grade-d-ink` | `#ffffff` rgb(255, 255, 255) | `#1a1424` rgb(26, 20, 36) |
| F | Letter colour | `--grade-f-ink` | `#ffffff` rgb(255, 255, 255) | `#e8e4f0` rgb(232, 228, 240) |
| X | Letter colour | `--grade-x-ink` | `#ffffff` rgb(255, 255, 255) | `#1a1424` rgb(26, 20, 36) |

"all" rows are declared once per grade (six labels), all carrying the value shown.

### 3. Confidence rating settings (global): Light set vs Dark set

| Setting | Label | Light | Dark |
| -- | -- | -- | -- |
| On bullet colour | `--confidence-bullet-active` | `#5a5070` rgb(90, 80, 112) (Light text-secondary) | `#9a8fb8` rgb(154, 143, 184) (Dark text-secondary) |
| Off bullet colour | `--confidence-bullet-inactive` | `#857b99` rgb(133, 123, 153) (Light text-muted) | `#6b6280` rgb(107, 98, 128) (Dark text-muted) |
| Off bullet opacity | `--confidence-bullet-inactive-opacity` | 0.55 | 0.55 |
| Bullet size | `--confidence-bullet-size` | 4px | 4px |
| Bullet gap | `--confidence-bullet-gap` | 3px | 3px |

Every confidence value is today's, so nothing changes visually. The two colour settings already exist. Opacity, size and gap move out of the `.confidence-bullet*` rules and into the theme sets.

### Widgets that use these settings

| Widget | Class label | Where it renders | Dot size | Uses |
| -- | -- | -- | -- | -- |
| Compact dot (unlettered) | `.grade-dot.dot-<g>.grade-dot-letterless` | Recommended / Review list analysis lines and the Job Detail modal Info tab (`PhaseAnalysisLines`) | 12px | grade base |
| Lettered dot | `.grade-dot.dot-<g>` | Agent analysis header, Processing and Skipped grade columns | 22px | grade base + lettered |
| Lettered dot, report tab | `.recommended-report-tab-label .grade-dot.dot-<g>` | Job Analysis Report phase tabs | 22px | grade base + lettered, letter size held at 11px by context |
| Lettered dot, report header cell | `.recommended-report-phase-grade-cell .grade-dot.dot-<g>` | Job Analysis Report grade + confidence row | 22px | grade base + lettered, letter size held at 11px by context |
| Confidence bullets | `.confidence-bullets` / `.confidence-bullet` / `.confidence-bullet--on` | Under graded dots in the report header, agent analysis header, and Processing and Skipped grade cells | 4px | confidence |

### Backgrounds the marks sit on (unchanged)

| Surface | Token | Light | Dark |
| -- | -- | -- | -- |
| Page (lists) | `--bg-deep` | `#f5f3fa` rgb(245, 243, 250) | `#0f0b18` rgb(15, 11, 24) |
| Card (modals, report) | `--bg-card` | `#ffffff` rgb(255, 255, 255) | `#1a1424` rgb(26, 20, 36) |
| Elevated (hover, table header) | `--bg-elevated` | `#ece8f4` rgb(236, 232, 244) | `#241b33` rgb(36, 27, 51) |

## Functional scope

1. **Light grade base.** On Light, every grade mark uses the Light fill, ring colour and 1.5px compact ring from the grade base table.
2. **Lettered builds on base.** On both themes, a lettered dot shows its grade's base fill and ring colour, and adds its own letter colour, letter size, letter weight and lettered ring width (2px on Light) from the lettered table.
3. **Confidence as theme settings.** Confidence bullets read every setting in the confidence table from the theme. They look exactly as they do today.
4. **Dark unchanged.** On Dark, every widget keeps today's fills, letter colours and confidence look. Ring widths are 0, so no ring shows.
5. **Two complete sets.** The Light and Dark theme blocks each declare every label in all three settings tables, so no setting falls back to the other theme.
6. **Retire Theme Examples.** The Tools → Theme Examples screen is removed entirely, along with its candidate grade-colour sets. Its nav item and route are removed, and nothing else in the Tools group changes.
7. **Retire the Light alternates.** Light (Parchment) and Light (Slate) are removed, so Dark and Light are the only palettes.

## Component scope

* `src/utils/config.py`: **modified**. The `light_parchment` and `light_slate` entries and the `theme_example_grade_sets` key leave `UI_CONFIG`, the Theme Examples item leaves the `Tools` nav group, and the registry comments drop their Theme Examples wording.
* `src/ui/frontend/src/lib/uiConfig.ts`: **modified**. Drops the grade-set entry type and the `theme_example_grade_sets` field from the UI config type.
* `src/ui/frontend/src/routes.tsx`: **modified**. Drops the `admin/theme_examples` route and its page import (nav ↔ routes SYNC).
* `src/ui/frontend/src/pages/AdminThemeExamples.tsx`: **deleted**. This is the Theme Examples screen.
* `tests/component/frontend/pages/test_AdminThemeExamples.test.tsx`: **deleted**. It covers the deleted page.
* `tests/component/utils/test_config.py`: **modified**. The registry-id and Tools-nav assertions in `TestAst2047ThemeRegistry` change, and `TestAst2064ThemeExampleGradeSets` is retired.
* `docs/test-bible/frontend/pages.md`: **modified**. The AST-2047, AST-2049, AST-2064, AST-2065, AST-2076 and AST-2077 entries that cite `test_AdminThemeExamples` / Theme Examples are retired or repointed.
* `docs/test-bible/frontend/components.md`: **modified**. The AST-2049 entries citing `test_AdminThemeExamples` are repointed.
* `docs/test-bible/utils/config.md`: **modified**. The AST-2047 `UI_CONFIG["themes"]` pointer reflects two ids and no grade sets.
* `src/ui/frontend/src/App.css`: **modified**. The Dark and Light Design Tokens blocks declare the full grade base, lettered and confidence settings sets. The `[data-theme="light_parchment"]` and `[data-theme="light_slate"]` blocks and the §16 Theme Examples section (plus its table-of-contents line) are removed. The §9b Grade Dots and confidence-bullet rules read every value from those settings.

## Technical scope

* `config.py` `UI_CONFIG["themes"]`: modified data. Remove the `light_parchment` and `light_slate` entries, leaving `dark` and `light`. `default_theme` stays `dark`. Neither alternate was profile-selectable, so no candidate can have one stored. The `profile_selectable` flag stays.
* `config.py` `UI_CONFIG["theme_example_grade_sets"]`: deleted key, with its comment.
* `config.py` `NAV_CONFIG` **Tools group**: modified data. Remove the Theme Examples item; the other six Tools items are unchanged.
* `uiConfig.ts`: modified type. Remove the grade-set entry interface and the optional `theme_example_grade_sets` field from `UiConfig`.
* `routes.tsx`: modified routes. Remove the `admin/theme_examples` route and the `AdminThemeExamples` import.
* `AdminThemeExamples.tsx`: deleted page.
* `App.css` **Light block (**`[data-theme="light"]`**)**: modified and new tokens. The six fills take the Light values. Add every per-grade ring colour, ring width, lettered ring width, letter colour, letter size and letter weight label, plus the three new confidence labels, all with the Light values from the settings tables. Its header comment drops the alternates wording.
* `App.css` **Dark block (**`:root, [data-theme="dark"]`**)**: new tokens. Declare the same labels with the Dark values from the settings tables, because the stylesheet header requires every `[data-theme]` block to declare the same custom-property names. The fills stay as they are.
* `App.css` `[data-theme="light_parchment"]` **/** `[data-theme="light_slate"]`: deleted blocks.
* `App.css` **§16 Theme Examples**: deleted section (every `.theme-examples*` rule) and its table-of-contents line.
* `App.css` `--text-on-grade` **/** `--text-on-grade-f`: retired tokens. Their only consumers are `.grade-dot` and `.dot-f`, so remove them once those rules read the per-grade letter colour.
* `App.css` **§9b Grade Dots**: modified rules. Each `.dot-<g>` rule draws its fill and an inset ring (`box-shadow: inset 0 0 0 <ring width> <ring colour>`) from its grade base settings. Lettered dots (not `.grade-dot-letterless`) add the grade's letter colour, size and weight, and use the lettered ring width. Because Dark ring widths are 0, no theme-scoped selector is needed. The two report-context rules keep their 11px letter size.
* `App.css` **confidence bullets (**`.confidence-bullets`**,** `.confidence-bullet`**,** `.confidence-bullet--on`**)**: modified rules. Gap, size and off opacity read the new confidence settings instead of literals.
* **Tests and bible (Betty,** `qa-child`**)**: the deleted page's test file is deleted. `test_config.py` asserts the two-id registry and no Theme Examples nav item, and drops the grade-set class. The three bible pages above are retired or repointed to match.

## Architectural definition

* **Patterns to reuse**: `no established pattern applies`. The only in-force frontend pattern, `patt.artifact.ui-consistency`, covers artifact editors, and this epic touches stylesheet tokens, config registry entries and an admin-only examples page. It follows the [AST-2042](https://linear.app/astralcareermatch/issue/AST-2042) local conventions without citing them as law: a theme is one registry entry plus one `[data-theme]` token block, every block declares the same names, and `NAV_CONFIG` and `routes.tsx` stay in SYNC.
* **New patterns proposed**: none. (The three-layer grade settings model is a stylesheet convention. Flag it if Archie wants it codified for AST-2101 and later themes.)
* **Applicable statutes**: none. There is no new route handler, logging, entity-state, dispatch or batch surface.

**Canon Scope:** none. Locked at Discussion.

## Acceptance criteria

 1. **Two complete sets.** Every label in the three settings tables (with `<g>` expanded to a, b, c, d, f and x) appears exactly once in `:root, [data-theme="dark"]` and exactly once in `[data-theme="light"]`, checked with `git grep -c -- '<label>:' src/ui/frontend/src/App.css` = 2 per label. **Fail:** any label missing from either block, or declared twice in one block.
 2. **Light values.** The Light block's values match the Light columns of the settings tables exactly. With the profile on Light, `getComputedStyle` on a `.dot-c` dot gives `background-color: rgb(247, 103, 7)`. **Fail:** any value differs, or the block still carries `#a06500` / `#c05621` / `#c53030`.
 3. **Separation.** The OKLab distance between every pair of the six Light fills, computed by the standard sRGB→OKLab formula, is ≥ 15 (the closest is C–D at 15.7). **Fail:** any pair below 15.
 4. **Compact ring.** On Light, a `.grade-dot.dot-<g>.grade-dot-letterless` dot on the Recommended Job List gives computed `box-shadow` = `inset 0 0 0 1.5px <that grade's ring colour>`, for each of A, B, C, D, F and X. **Fail:** no shadow, a different width, or another grade's ring colour.
 5. **Lettered builds on base, all three variants.** On Light, a plain lettered dot, a report tab dot and a report header cell dot each give:
    * computed `background-color` = the grade's base fill;
    * `color` = the grade's letter colour (B is `rgb(43, 32, 0)` and C is `rgb(31, 13, 0)`; the rest are white);
    * `font-weight` 700;
    * `box-shadow` = `inset 0 0 0 2px <ring colour>`.

    The plain dot's `font-size` is 12px, and the two report variants are 11px. **Fail:** a fill that differs from the compact dot of the same grade, shared ink across grades, or a 1.5px ring on any lettered variant.
 6. **Dark unchanged, no ring.** On Dark, every widget in the widgets table keeps the Dark fills and letter colours in the settings tables, and the computed `box-shadow` spread is 0px, so no ring is drawn. **Fail:** any colour change or a visible ring.
 7. **Confidence unchanged, sourced from settings.** In both themes, `.confidence-bullet` computes `width` and `height` 4px and `opacity` 0.55 (1 when `--on`), the gap is 3px, and the colours match the confidence table. `git grep -n -A6 '^\.confidence-bullet' -- src/ui/frontend/src/App.css` shows `var(--confidence-bullet-` for gap, size and opacity, and no `4px`, `3px` or `0.55` literals. **Fail:** any visual change, or a literal left in those rules.
 8. **Theme Examples gone.** `git grep -n -i -e theme_examples -e ThemeExamples -e theme-examples -e 'Theme Examples' -e theme_example_grade_sets -- src tests` returns nothing. `GET /api/nav_config` as admin lists the Tools group with exactly Data Management, Agent Ad Hoc, Telescope, Cost Reconciliation, Resume Paste and Cover Letter Paste. Browsing to `/admin/theme_examples` no longer renders the page. **Fail:** any hit, a seventh Tools item, or the page still rendering.
 9. **Alternates gone.** `git grep -n -e light_parchment -e light_slate -- src tests` returns nothing. `GET /api/ui_config` lists exactly `dark` and `light` under `themes` and has no `theme_example_grade_sets` key. **Fail:** any leftover reference or key.
10. **Old ink tokens gone.** `git grep -n 'text-on-grade' -- src/ui/frontend/src src/utils` returns nothing. **Fail:** any hit.
11. **Backgrounds untouched.** With the profile on Light, `getComputedStyle(document.querySelector('.modal-card')).backgroundColor` is `rgb(255, 255, 255)`. **Fail:** any other value.
12. **Builds clean.** `npx tsc --noEmit` in `src/ui/frontend` exits 0 and `python -c "import src.utils.config"` exits 0. **Fail:** a type error from a dangling `theme_example_grade_sets` / page import, or an import error.

## Open questions

None.

## Proposed child tickets

#### 1!: **Retire Theme Examples and the Light alternates - Hedy**

Removes the Tools → Theme Examples screen end to end: its nav item, route, page, grade-colour candidate sets and the UI config type for them. Removes the Light (Parchment) and Light (Slate) registry entries, so Dark and Light are the only palettes. Does **not** touch `App.css`; #2 deletes the matching CSS blocks and §16. The unused CSS left on dev in between is harmless.
**Citations:** none. No in-force pattern or statute governs config registry entries or an admin examples page (see Architectural definition).
**Scope:**

* `src/utils/config.py`: **modified**. The `light_parchment` and `light_slate` entries and the `theme_example_grade_sets` key leave `UI_CONFIG`, the Theme Examples item leaves the `Tools` nav group, and the registry comments drop their Theme Examples wording.
* `src/ui/frontend/src/lib/uiConfig.ts`: **modified**. Drops the grade-set entry type and the `theme_example_grade_sets` field from the UI config type.
* `src/ui/frontend/src/routes.tsx`: **modified**. Drops the `admin/theme_examples` route and its page import (nav ↔ routes SYNC).
* `src/ui/frontend/src/pages/AdminThemeExamples.tsx`: **deleted**. This is the Theme Examples screen.
* `tests/component/frontend/pages/test_AdminThemeExamples.test.tsx`: **deleted**. It covers the deleted page.
* `tests/component/utils/test_config.py`: **modified**. The registry-id and Tools-nav assertions in `TestAst2047ThemeRegistry` change, and `TestAst2064ThemeExampleGradeSets` is retired.
* `docs/test-bible/frontend/pages.md`, `docs/test-bible/frontend/components.md`, `docs/test-bible/utils/config.md`: **modified**, as in Component scope.

Technical scope: the `config.py` `UI_CONFIG["themes"]`, `UI_CONFIG["theme_example_grade_sets"]` and `NAV_CONFIG` Tools bullets, plus the `uiConfig.ts`, `routes.tsx`, `AdminThemeExamples.tsx`, and Tests and bible bullets.
Estimate: 2

#### 2: **Grade settings sets (Light Bright + ring, Dark as-is) - Ada**

Declares the full grade base, lettered and confidence settings in both theme blocks, with Light on Bright + ring and Dark visually unchanged. Points the grade-dot and confidence-bullet rules at those settings. Deletes the now-unregistered alternate theme blocks and the §16 Theme Examples CSS. Runs after #1, because deleting the alternate blocks first would fail `test_every_registry_id_has_an_app_css_block`. Does **not** add shapes; that is [AST-2101](https://linear.app/astralcareermatch/issue/AST-2101).
**Citations:** none. No in-force pattern or statute governs stylesheet tokens (see Architectural definition).
**Scope:** `src/ui/frontend/src/App.css`: **modified**. The Dark and Light Design Tokens blocks declare the full grade base, lettered and confidence settings sets. The `[data-theme="light_parchment"]` and `[data-theme="light_slate"]` blocks and the §16 Theme Examples section (plus its table-of-contents line) are removed. The §9b Grade Dots and confidence-bullet rules read every value from those settings. Technical scope: every `App.css` bullet above.
Estimate: 3

**New patterns:** none.

**Monolith check:** Functional scope has N = 7 and there are M = 2 children. #1 owns retirement (capabilities 6–7, except their CSS), and #2 owns the grade settings (capabilities 1–5) plus the CSS removal, because it owns the one stylesheet.

**Scope partition check:** #1 claims `config.py`, `uiConfig.ts`, `routes.tsx`, `AdminThemeExamples.tsx`, the deleted test file, `test_config.py` and the three bible pages. #2 claims `App.css`. Every Component scope file and Technical scope item appears in exactly one child. There are no gaps and no overlaps.

---

## Original brief

## Problem

On the light theme the grade dots (A, B, C, D, F, X) are hard to tell apart. B, C, D and F were all darkened into one brown-red band at about the same lightness. In OKLab distance, B–C and C–D are each about 7, which is effectively the same colour at compact (\~22px) dot size. Contrast against the background was never the problem; every current dot already clears 4:1.

## Change

Light theme only. **The dark theme set stays as it is.**

Keep the bright hues that work on dark. Add a thin inset ring in a darker shade of each fill so the dot holds its edge against the light card background (#f1f0f7).

| Grade | Fill | Letter ink | Ring |
| -- | -- | -- | -- |
| A | `#2f9e44` | `#ffffff` | `#006200` |
| B | `#f5b700` | `#2b2000` | `#b57700` |
| C | `#f76707` | `#1f0d00` | `#b41400` |
| D | `#c92a3a` | `#ffffff` | `#850000` |
| F | `#5c1414` | `#ffffff` | `#210000` |
| X | `#7048e8` | `#ffffff` | `#4100a8` |

Ring: `box-shadow: inset 0 0 0 1.5px var(--grade-x-ring)` on compact dots, 2px on large lettered dots. Scope the ring to the light theme only.

```css
/* light theme */
--grade-a: #2f9e44; --grade-a-ink: #ffffff; --grade-a-ring: #006200;
--grade-b: #f5b700; --grade-b-ink: #2b2000; --grade-b-ring: #b57700;
--grade-c: #f76707; --grade-c-ink: #1f0d00; --grade-c-ring: #b41400;
--grade-d: #c92a3a; --grade-d-ink: #ffffff; --grade-d-ring: #850000;
--grade-f: #5c1414; --grade-f-ink: #ffffff; --grade-f-ring: #210000;
--grade-x: #7048e8; --grade-x-ink: #ffffff; --grade-x-ring: #4100a8;
```

## Applies to

* Compact letterless dot rows (summary)
* Large lettered dots (relaxed layout)

## Acceptance

* Given the light theme, when a compact summary row renders, then every grade uses the fill and ring above, and the closest pair (C–D) has an OKLab distance of at least 15.
* Given the light theme, when lettered dots render, then letters use the ink colours above and the ring is 2px.
* Given the dark theme, when either layout renders, then the colours are unchanged from today and no ring appears.

Reference: Grade Palette Lab canvas (candidate "Bright + ring").

### Comments

#### chuckles — 2026-10-10T04:36:30.023Z
AST-2122 REVIEW — Joan: AC 9 grep covers `tests`; four test files outside Scope (test_api_system.py, test_candidate.py, test_api_candidate.py, test_NavigationShell.test.tsx) still hit light_parchment/light_slate. Scope extended to Betty; Hedy revising plan.

#### chuckles — 2026-10-10T03:48:25.963Z
@susan The pipeline is stopped on a tooling deadlock, not on anything in this ticket. Dispatch is done: [AST-2122](https://linear.app/astralcareermatch/issue/AST-2122) (Hedy) blocks [AST-2123](https://linear.app/astralcareermatch/issue/AST-2123) (Ada). Both are still Todo.

- **What happens:** the skill requires the sub-chuck drone to run in the epic worktree (`astral-AST-2100`). `datt_trace.py run` then takes the exclusive worktree lock (`worktree_lock.py`) for the drone itself. The drone's nested Hedy `plan-child` spawn targets the same worktree, so it waits behind its own parent until the 45-minute timeout. `datt-trace.log` shows the same self-hold on the AST-2046, AST-2073 and AST-2102 drones.
- **Decision needed (pick one):**
  1. Patch `datt_trace.py` so a Chuckles sub-chuck spawn (`--role sub-chuck`) doesn't take the worktree lock (it doesn't write the tree; its nested engineer/Betty spawns still lock). This is a small change in `team-chuckles`.
  2. Run drones with `CHUCKLES_WORKTREE_LOCK=0`. That turns the lock off for every nested spawn too, so I don't recommend it.
- Once it's fixed, move this back to Todo and assign Chuckles to resume. Dispatch won't re-run because the children already exist.

#### chuckles — 2026-10-09T21:50:49.237Z
@susan Yes, that's the model, and it's now in the Description as two complete sets, Light and Dark. Each grade has base settings (fill, ring colour, ring width, shape). The lettered dot takes those and adds letter colour, size, weight and a lettered ring width. The confidence settings (on/off colour, off opacity, size, gap) are global. The Light card stays `#ffffff`.

1. **Theme Examples "Grade color options" rows.** Pick one: (a) keep them faithful by moving them to the new setting labels with ring width 0 (draft assumption); (b) retire them; or (c) do (a) and also add Bright + ring as a fourth row.
2. **Class labels.** In today's markup, plain `.grade-dot` is the 22px lettered dot, and compact adds `.grade-dot-letterless`. Keep that (CSS-only), or flip it so `.grade-dot` is the compact base and lettered adds `grade-dot-lettered`? Flipping matches the model but edits the six components and pages that render dots, plus their tests.
3. **Shape.** Shape is listed as circle for every grade with no setting built, because [AST-2101](https://linear.app/astralcareermatch/issue/AST-2101) draws shapes as SVG and can't use a CSS shape token. Is that right, or do you want a shape setting added here?

#### susan — 2026-10-09T21:49:19.076Z
I think you're recommending that the ink, shape, and ring settings are defined for each grade, and that the lettered version would INHERIT those settings and add font size, font color, etc. for each grade option, plus global confidence rating settings.

For all of those, I want two sets, one light theme and one for dark theme.

#### chuckles — 2026-10-09T21:22:53.519Z
@susan Parchment and Slate are now retired in scope. The grade widget reference table (class labels, Dark vs Light colours with RGB, and the card / page backgrounds) is in the Description.

1. **Light card RGB.** Should the Light card stay `#ffffff` rgb(255, 255, 255), or move to the brief's `#f1f0f7` rgb(241, 240, 247)? `#f1f0f7` is very close to the Light page `#f5f3fa`, so cards would barely stand out from the page.
2. **Theme Examples "Grade color options" rows.** Pick one: (a) keep them faithful by moving them to the new token names with no ring (draft assumption); (b) retire them, since the palette is chosen; or (c) do (a) and also add Bright + ring as a fourth row.
3. **Class labels.** Keep the existing labels in the table (lettered dots are plain `.grade-dot`, compact is `.grade-dot-letterless`), or define explicit ones such as `grade-dot-lettered`? New labels would mean editing the six components and pages that render dots.

#### chuckles — 2026-10-09T03:56:50.783Z
@susan

1. **Which Light blocks?** Should Bright + ring go into all three Light palettes (`light`, `light_parchment`, `light_slate`, which share one grade set today), or only into the profile-selectable `light`? The draft assumes all three.
2. **Theme Examples "Grade color options" rows (AST-2064 / AST-2077).** Per-grade ink and the Light ring break those rows: their letter overrides go dead, and on Light panels they'd show Bright rings. Pick one:
 (a) keep the rows faithful by moving them to the new token names with no ring (draft assumption);
 (b) retire the rows, since the palette is chosen;
 (c) do (a) and also add Bright + ring as a fourth row.
3. **Card background.** The brief says the light card is `#f1f0f7`, but in the repo it's `#ffffff` (page `#f5f3fa`). Should the backgrounds stay as they are, with only the grade tokens changing? The draft assumes yes.

---

_Implementation detail may live in git history on `origin/dev`._
