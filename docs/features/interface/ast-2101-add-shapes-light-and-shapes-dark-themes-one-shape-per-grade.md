# AST-2101 — Add "Shapes - Light" and "Shapes - Dark" themes (one shape per grade)

<!-- linear-archive: AST-2101 archived 2026-10-16 -->

## Linear archive (AST-2101)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2101/add-shapes-light-and-shapes-dark-themes-one-shape-per-grade  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Colour is the only thing that tells grades apart today, and for colour-blind users that fails: under deuteranopia, Light's A (green) and D (red) are about 6 apart in OKLab distance, which reads as the same mark. Two new themes, **Shapes - Light** and **Shapes - Dark**, keep the Light and Dark colours exactly and give each grade its own shape. That makes every grade readable without relying on hue. Light and Dark stay as they are, so nobody's current look changes unless they pick a Shapes theme. This builds on [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100)'s grade settings model (grade base, lettered and confidence settings declared in full by each theme block). [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette) is in User Testing and not yet on `origin/dev`, so this epic dispatches only after it lands.

## Functional scope

1. **Two new themes.** The profile Theme select offers Shapes - Light and Shapes - Dark alongside Dark and Light.
2. **Same colours, shared, not copied.** Shapes - Light uses exactly the Light colours and Shapes - Dark exactly the Dark colours (fills, rings, letter colours, confidence bullets, backgrounds). Each pair shares one declaration, so the twins cannot drift.
3. **One shape per grade.** In either Shapes theme, every grade mark, compact (unlettered) and lettered, is drawn with its grade's shape from the brief: A circle, B diamond, C rounded square, D up triangle, F down triangle, X cross. The geometry is the brief's SVG paths.
4. **Ring as stroke.** In Shapes - Light, each shape's edge ring is a stroke in the grade's ring colour, about 1.5px on compact marks and 2.5px on lettered marks. Shapes - Dark draws no ring.
5. **Lettered layout.** In either Shapes theme, the letter sits at the shape's centroid (about y 63/100 in the up triangle and 39/100 in the down triangle). It is smaller in triangles (about 38/100 of the box, against 46/100 elsewhere). X draws the cross only, with no visible letter.
6. **Accessible name.** Every grade mark, in every theme and in both layouts, has the grade letter as its accessible name.
7. **Light and Dark unchanged.** On Light and Dark, every mark stays the [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette) circle, with the same fill, ring and letter.

## Component scope

* `src/ui/frontend/src/components/GradeMark.tsx`: **new**. The single shared grade mark. It renders today's grade-dot classes and letter, adds the accessible name, and carries its grade's shape geometry.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx`: **modified**. Its local grade-dot helper renders the shared mark. This covers the report phase tabs, the report header grade cells, and the Recommended/Review list lines and Job Detail Info tab (through `PhaseAnalysisLines`, which itself is unchanged).
* `src/ui/frontend/src/components/AgentAnalysisHeader.tsx`: **modified**. The analysis header dot renders the shared mark.
* `src/ui/frontend/src/pages/JobsProcessing.tsx`: **modified**. Its local grade-dot helper renders the shared mark.
* `src/ui/frontend/src/pages/JobsSkipped.tsx`: **modified**. Its local grade-dot helper renders the shared mark.
* `src/utils/config.py`: **modified**. `UI_CONFIG["themes"]` gains the two Shapes entries.
* `src/ui/frontend/src/App.css`: **modified**. The Dark and Light token blocks also apply to their Shapes twin and declare the shape ring settings. New §9b rules draw the shapes in the two Shapes themes only.
* `tests/component/frontend/components/test_GradeMark.test.tsx`: **new**. Covers the shared mark.
* `tests/component/frontend/test_AppCss.test.tsx`: **modified**. Its theme mirror and block parser learn the four ids and the shared-block selectors, and its Light-pairwise-differ check exempts the Light/Shapes - Light twins.
* `tests/component/utils/test_config.py`: **modified**. `TestAst2047ThemeRegistry` asserts the four ids, labels and select options.
* `docs/test-bible/frontend/components.md`: **modified**. New GradeMark entries.
* `docs/test-bible/frontend/root.md`: **modified**. `test_AppCss` entries reflect the shared twin blocks and the shape rules.
* `docs/test-bible/utils/config.md`: **modified**. The theme registry pointer reflects four ids.

## Technical scope

* `GradeMark.tsx`: new component. It takes a grade letter, an optional tooltip and a letterless flag. It renders the existing `grade-dot dot-<g>` (+ `grade-dot-letterless`) span with the grade letter as its only text (none when letterless). The span carries an image role whose accessible name is the grade letter. It also holds an inline SVG (hidden from assistive tech) with that grade's shape path from the brief, in a geometry map keyed by grade letter. The letter is rendered once, so a lettered mark's text content stays the single grade letter and existing call-site tests that read `.grade-dot` classes or text stay valid.
* `recommendedJobReport.tsx`, `AgentAnalysisHeader.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`: modified render. Each local grade-dot span or helper is replaced by the shared mark with the same props it has today. There is no other behaviour change.
* `config.py` `UI_CONFIG["themes"]`: modified data. Add `shapes_light` ("Shapes - Light") and `shapes_dark` ("Shapes - Dark"), both `profile_selectable`. `default_theme` stays `dark`.
* `App.css` **token blocks**: modified selectors and new tokens. The Dark block's selector becomes `:root, [data-theme="dark"], [data-theme="shapes_dark"]`. The Light block's selector becomes `[data-theme="light"], [data-theme="shapes_light"]`. Both blocks declare the per-grade shape ring widths, compact and lettered (Light 1.5px / 2.5px, Dark 0), following AST-2100's per-grade layering. No colour token is duplicated.
* `App.css` **§9b Grade Dots**: new rules scoped to the two Shapes theme ids. The circle background and inset ring are dropped and the shape SVG is shown. The path fills with the grade fill (X: stroked in the grade fill at 24, or 20 when lettered, viewBox units, round caps, no fill). The ring strokes in the grade ring colour at the shape ring width, without scaling with the viewBox and without being clipped at the box edge, using `stroke-linejoin: round`. The letter is placed at the centroid at the brief's sizes and is hidden on X. Outside the Shapes themes the SVG is not displayed, so the [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette) circle rules are untouched.
* **Tests and bible (Betty,** `qa-child`**)**: a new GradeMark test covers per-grade path, accessible name, text content and the letterless case. `test_AppCss` handles selector-list blocks and twin exemptions. `test_config` asserts four ids. The three bible pages are updated to match.

## Architectural definition

* **Patterns to reuse**: `no established pattern applies`. The only in-force frontend pattern, `patt.artifact.ui-consistency`, covers artifact editors, and this epic touches a display component, stylesheet tokens and the theme registry. It follows the [AST-2042](https://linear.app/astralcareermatch/issue/AST-2042) / [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette) local conventions without citing them as law: a theme is one registry entry plus a `[data-theme]` token block, every block declares the same names, and grade settings are per-grade theme tokens.
* **New patterns proposed**: none. (A "twin theme" that shares its sibling's token block through a selector list is a new local convention. Flag it if Archie wants it codified.)
* **Applicable statutes**: none. There is no new route handler, logging, entity-state, dispatch or batch surface.

**Canon Scope:** none. Locked at Discussion.

## Acceptance criteria

 1. **Four themes.** `GET /api/ui_config` lists exactly `dark`, `light`, `shapes_light`, `shapes_dark` under `themes`, with labels Dark, Light, Shapes - Light, Shapes - Dark, all `profile_selectable`. The profile Theme select shows those four options. **Fail:** a missing, extra or mislabelled entry, or a Shapes theme absent from the select.
 2. **Colours shared, not copied.** `git grep -c -e '--grade-a:' -- src/ui/frontend/src/App.css` returns 2. The block containing the Light `--grade-a: #2f9e44` opens with `[data-theme="light"], [data-theme="shapes_light"] {`, and the Dark block opens with `:root, [data-theme="dark"], [data-theme="shapes_dark"] {`. **Fail:** a count of 4 (copied twin blocks), or either twin missing from its sibling's selector.
 3. **Shapes per grade.** With the profile on either Shapes theme, on the Recommended list and in the Job Analysis Report, each `.grade-dot.dot-<g>` shows a displayed SVG path whose `d` is the brief's path for that grade (A circle, B diamond, C rounded square, D up, F down, X cross). The span's computed `background-color` is `rgba(0, 0, 0, 0)` and `box-shadow` is `none`. Non-X paths compute `fill` = the grade fill, and X computes `fill: none` with `stroke` = the X fill. **Fail:** a visible circle background, a wrong path, or the wrong colour.
 4. **Ring.** In Shapes - Light, a compact mark's path computes `stroke` = the grade ring colour and `stroke-width` 1.5px, and a lettered mark's computes 2.5px, with the ring not clipped (`overflow` on the SVG is visible). In Shapes - Dark the ring stroke width is 0. **Fail:** a missing or wrong-coloured ring on Shapes - Light, or any visible ring on Shapes - Dark.
 5. **Lettered layout.** In either Shapes theme, on a 22px lettered D mark the letter's computed `font-size` is about 8.4px (38/100) and its box centre sits at 63% ±3% of the mark height. On F it sits at 39% ±3%. On A, B and C the size is about 10.1px (46/100), centred at 50% ±3%. On X the letter computes `visibility: hidden` or `display: none`. **Fail:** any letter off by more than the tolerance, or a visible letter on X.
 6. **Accessible name.** In `test_GradeMark`, for each of A, B, C, D, F and X, both lettered and letterless, `getByRole("img", { name: <grade> })` finds the mark and the SVG is `aria-hidden`. **Fail:** no image role, or an empty or different name.
 7. **Text content unchanged.** A lettered mark's `textContent` equals its grade letter and a letterless mark's is empty. The existing Vitests `test_recommendedJobReport`, `test_JobsProcessing`, `test_JobsSkipped`, `test_JobsRecommended`, `test_JobAnalysisReportModal` and `test_JobDetailModal` pass unchanged. **Fail:** doubled letters, or any of those suites needing edits for markup reasons.
 8. **One mark.** `git grep -n 'grade-dot dot-' -- src/ui/frontend/src` returns hits only in `GradeMark.tsx`. **Fail:** any other file still builds its own grade-dot span (a parallel shape path per page).
 9. **Light and Dark unchanged.** With the profile on Light or Dark, a `.dot-c` mark computes `border-radius: 50%`, `background-color` = the C fill, and the [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette) ring `box-shadow`, and its SVG computes `display: none`. **Fail:** any shape, a missing circle, or a ring or colour change.
10. **Builds clean.** `npx tsc --noEmit` in `src/ui/frontend` exits 0, `python -c "import src.utils.config"` exits 0, and `test_AppCss.test.tsx` and `test_config.py::TestAst2047ThemeRegistry` pass. **Fail:** a non-zero exit or a failing case.

## Open questions

1. **How the shape gets drawn.** This definition is written for **(A)**:
   * **(A, recommended)** The shared mark always carries its grade's shape SVG. CSS rules scoped to the two Shapes theme ids show it and drop the circle. No JS knows the theme, the registry type is unchanged, and Light/Dark CSS is untouched.
     * This one.
   * **(B)** Each registry entry gets a mark-geometry field, and the mark reads the current theme and renders either the circle or the SVG. The DOM is leaner, but `uiConfig.ts` and `CandidateContext.tsx` join scope, and every mark depends on theme context.
   * **(C)** CSS-only `mask-image` per grade on today's span, with no markup change. The ring can't be a true stroke and the X cross can't take one, so it misses the brief's stroke spec.
2. **X ring in Shapes - Light.** The cross is stroke-only, drawn in the X fill.
   * **(a, recommended)** It gets a ring like the other grades: a wider under-stroke in `--grade-x-ring`. This definition is written for (a).
     * This one.
   * **(b)** X has no ring.

## Proposed child tickets

#### 1!: **Shared grade mark - Hedy**

Moves every grade mark onto one shared component. The component renders today's classes and letter, gives each mark the grade letter as its accessible name, and carries the hidden shape SVG for its grade. There is no visual change on any theme, because nothing displays the SVG yet. Does **not** add themes or CSS; that is #2. Blocked by [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100) landing on dev.
**Citations:** none. No in-force pattern or statute governs frontend display components (see Architectural definition).
**Scope:**

* `src/ui/frontend/src/components/GradeMark.tsx`: **new**. The single shared grade mark. It renders today's grade-dot classes and letter, adds the accessible name, and carries its grade's shape geometry.
* `src/ui/frontend/src/lib/recommendedJobReport.tsx`, `src/ui/frontend/src/components/AgentAnalysisHeader.tsx`, `src/ui/frontend/src/pages/JobsProcessing.tsx`, `src/ui/frontend/src/pages/JobsSkipped.tsx`: **modified**. Each renders the shared mark.
* `tests/component/frontend/components/test_GradeMark.test.tsx`: **new**. `docs/test-bible/frontend/components.md`: **modified**.

Technical scope: the `GradeMark.tsx` bullet, the four call-site bullet, and the GradeMark test and bible part of the Tests and bible bullet.
Estimate: 3

#### 2: **Shapes - Light and Shapes - Dark themes - Ada**

Registers the two Shapes themes. Each one shares its sibling's token block, and both declare the shape ring settings. Adds the Shapes-only §9b rules that draw the shape, ring and centroid letter, and hide the circle. Runs after #1, because its rules style the mark #1 renders. Blocked by [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100) landing on dev.
**Citations:** none. No in-force pattern or statute governs stylesheet tokens or the theme registry (see Architectural definition).
**Scope:**

* `src/utils/config.py`: **modified**. `UI_CONFIG["themes"]` gains the two Shapes entries.
* `src/ui/frontend/src/App.css`: **modified**. The Dark and Light token blocks also apply to their Shapes twin and declare the shape ring settings. New §9b rules draw the shapes in the two Shapes themes only.
* `tests/component/frontend/test_AppCss.test.tsx`, `tests/component/utils/test_config.py`, `docs/test-bible/frontend/root.md`, `docs/test-bible/utils/config.md`: **modified**, as in Component scope.

Technical scope: the `config.py` `UI_CONFIG["themes"]`, `App.css` token blocks and `App.css` §9b bullets, and the `test_AppCss` / `test_config` / bible part of the Tests and bible bullet.
Estimate: 3

**New patterns:** none.

**Monolith check:** Functional scope has N = 7 and there are M = 2 children. #1 owns the accessible name and the shared markup (capability 6, and the markup half of 3). #2 owns themes, shared colours, shape drawing, ring, lettered layout and no regression (capabilities 1–5 and 7), because they all live in the registry and the one stylesheet.

**Scope partition check:** #1 claims `GradeMark.tsx`, the four call sites, `test_GradeMark.test.tsx` and `components.md`. #2 claims `config.py`, `App.css`, `test_AppCss.test.tsx`, `test_config.py`, `root.md` and `config.md`. Every Component scope file and Technical scope item appears in exactly one child. There are no gaps and no overlaps.

---

## Original brief

## Why

Colour alone can't separate grades for colour-blind users. Under deuteranopia, the light palette's A (green) and D (red) are about 6 apart in OKLab distance, which is effectively the same mark. A distinct shape per grade makes every grade readable without relying on hue.

## Change

Add two new themes to the theme selector, alongside the existing Light and Dark:

* **Shapes - Light**: same colours as Light (the "Bright + ring" set from [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette)), drawn with grade shapes
* **Shapes - Dark**: same colours as Dark (existing dark tokens, unchanged), drawn with grade shapes

Colours do not change. Only the mark geometry changes.

| Grade | Shape |
| -- | -- |
| A | Circle |
| B | Diamond |
| C | Rounded square |
| D | Up triangle |
| F | Down triangle |
| X | Cross (×) |

Diamond was chosen over hexagon for B. At compact size a hexagon reads as a circle, and A/B are the most frequent pair.

## Geometry (SVG, 0 0 100 100 viewBox)

```
circle   M50 6a44 44 0 1 0 0.01 0Z
diamond  M50 3L97 50L50 97L3 50Z
square   M18 9H82Q91 9 91 18V82Q91 91 82 91H18Q9 91 9 82V18Q9 9 18 9Z
up       M50 6L96 90H4Z          (letter centre y≈63)
down     M4 10H96L50 94Z         (letter centre y≈39)
cross    M20 20L80 80M80 20L20 80, stroke-width 24 (20 when lettered), round caps, no fill
```

* Use `stroke-linejoin: round` to soften triangle and diamond corners.
* In Shapes - Light, the edge ring becomes an SVG stroke in `--grade-*-ring`, about 1.5px at compact size and 2.5px when lettered (`vector-effect` or a size-scaled stroke width). Shapes - Dark has no ring.
* Lettered view: draw the letter at the shape's centroid. Use a smaller letter in triangles, about 38/100 against 46/100 elsewhere. For X, the cross itself is the letter, so draw no text.

## Known trade-offs (accepted)

* Triangles carry about 30% less ink than a circle in the same box, so D and F read slightly smaller and lighter in compact rows.
* Letters inside triangles are cramped and sit off-centre.

## Acceptance

* Given the Shapes - Light theme, when a compact summary row renders, then each grade is drawn with its shape from the table in Light theme colours with rings.
* Given the Shapes - Dark theme, when a compact summary row renders, then each grade is drawn with its shape in the existing dark colours.
* Given either Shapes theme, when the lettered layout renders, then the letter appears at the shape's centroid, and X shows the cross only.
* Given any Shapes mark, when read by a screen reader, then its accessible name is the grade letter.
* Given the Light or Dark theme, when either layout renders, then marks remain circles (no regression).

Depends on [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100/light-theme-replace-grade-colours-with-bright-ring-palette) for the light colours. Reference: Grade Palette Lab canvas (Shapes → "One per grade", B as Diamond).

### Comments

#### chuckles — 2026-10-10T06:12:33.334Z
[check-linear] User Testing — dispatched after the AST-2100 merge; both children through, [PR #298](https://github.com/susansomerset/astral/pull/298) ready for review (@susan)

#### chuckles — 2026-10-10T06:10:09.827Z
@susan AST-2129 is at User Testing and merged to ftr. One decision for UAT: Shapes - Light uses the Light colours but still shows the dark wordmark, because `NavigationShell.tsx` only switches the logo when the theme is exactly `"light"`. That file is outside both children's Scope, so it needs either a scope amendment on this epic or a follow-up ticket. The shape, ring and letter checks (AC 3–5) are only pinned against `App.css` text, so a browser check on both Shapes themes in UAT is the backstop.

#### chuckles — 2026-10-10T05:55:26.973Z
@susan AST-2128 AC 9 is partly blocked by an existing failure: two `test_AppCss` cases fail on `--tp-lvl` (Task Performance commit `5f4850a20` on dev declares `hsla()` colours outside the theme token blocks). Betty skipped both by name in the manifest. Pick one:
- relax `test_AppCss` to allow locally declared `App.css` variables (test file owned by AST-2129's revision), or
- move those colours into the theme token blocks (file a product Bug).

#### chuckles — 2026-10-10T05:48:53.197Z
AST-2128 estimate 3→2 — one component plus four mechanical call-site swaps.

#### susan — 2026-10-10T05:43:49.097Z
@chuckles I just merged it.

#### chuckles — 2026-10-10T05:42:45.607Z
@susan

Your Open questions picks (A, a) match the definition, so that part is ready. Dispatch is held because one prerequisite is missing:

* **AST-2100 isn't on `origin/dev`.** [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100) is still User Testing, and [PR #295](https://github.com/susansomerset/astral/pull/295) is open with 20 commits not on dev. Dispatch seeds `ftr/AST-2101` from `origin/dev`, so both children would build against the pre-AST-2100 stylesheet. That means none of the grade ring/lettered tokens, and the old Theme Examples blocks are still there. Both children would also collide with AST-2100 on `App.css`, `config.py`, `test_AppCss` and `test_config`.
* **To proceed:** land PR #295 (finish-up AST-2100), then move this back to Todo + Chuckles. Or, if you'd rather stack, say so here and I'll seed `ftr/AST-2101` from `origin/ftr/AST-2100-bright-ring-grade-palette` instead of dev. That's a one-off exception to branch law, and AST-2101 then can't land before AST-2100.

#### chuckles — 2026-10-10T05:07:33.683Z
@susan

1. **How the shape gets drawn.** The definition is written for **(A)**:
   * **(A, recommended)** The shared mark always carries its grade's shape SVG. CSS rules scoped to the two Shapes theme ids show it and hide the circle. No JS needs to know the theme, the registry type doesn't change, and Light/Dark CSS isn't touched.
   * **(B)** Each registry entry gets a mark-geometry field, and the mark reads the current theme and renders either the circle or the SVG. The DOM is leaner, but `uiConfig.ts` and `CandidateContext.tsx` join scope, and every mark depends on theme context.
   * **(C)** CSS-only `mask-image` on today's span, with no markup change. The ring can't be a true stroke and the X cross can't take one, so it misses the brief's stroke spec.
2. **X ring in Shapes - Light.** The cross is stroke-only, drawn in the X fill.
   * **(a, recommended)** It gets a ring like the other grades: a wider under-stroke in `--grade-x-ring`. The definition is written for (a).
   * **(b)** X has no ring.

#### chuckles — 2026-10-10T05:05:06.634Z
[thread-missing] Cursor chat `a7ecd44b-c9d3-4bd6-9d80-d5099722f71b` has no local `store.db` on **chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/a7ecd44b-c9d3-4bd6-9d80-d5099722f71b/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `c0715ad4-2681-4dd4-b8c4-f5cd2d2fe531`.

Watcher rule `define` on `AST-2101` (Thread owner `AST-2101`).

---

_Implementation detail may live in git history on `origin/dev`._
