# Shapes - Light and Shapes - Dark themes

- **Ticket:** [AST-2129](https://linear.app/astralcareermatch/issue/AST-2129) — child of [AST-2101](https://linear.app/astralcareermatch/issue/AST-2101) (Add "Shapes - Light" and "Shapes - Dark" themes)
- **Publish ref:** `origin/sub/AST-2101/AST-2129-shapes-themes`
- **Canon Scope:** none (parent Architectural definition — no in-force pattern or statute governs stylesheet tokens or the theme registry).
- **Depends on:** [AST-2128](https://linear.app/astralcareermatch/issue/AST-2128) (shared `GradeMark`, already merged into `origin/ftr/AST-2101-shapes-themes` and on this sub) and [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100) (grade settings model, on `origin/dev`).

Registers two new palettes, **Shapes - Light** (`shapes_light`) and **Shapes - Dark** (`shapes_dark`), in `UI_CONFIG["themes"]`. Each twin shares its sibling's App.css token block through a selector list, so the colours cannot drift. Both blocks gain per-grade shape ring widths. New §9b rules, scoped to the two Shapes theme ids only, hide the circle and reveal the shape SVG that `GradeMark` already renders (AST-2128). They fill the shape, stroke its ring, and put the letter at the shape's centroid. Light and Dark rules are untouched, so those themes keep today's circle.

## Scope gate

Every row below is a file this ticket's `## Scope` names, and every change is the kind its Technical scope describes:
- registry data in `config.py` `UI_CONFIG["themes"]`;
- selector-list changes and new shape ring tokens in the App.css token blocks;
- new Shapes-only §9b rules.

`test_AppCss.test.tsx`, `test_config.py`, `root.md` and `config.md` are in Scope but belong to Betty (`qa-child`). Engineers do not touch `tests/` or `docs/test-bible/**`, so they are **not** in Files Changed.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `UI_CONFIG["themes"]` + `shapes_light`, `shapes_dark`; registry comment updated | utils |
| `src/ui/frontend/src/App.css` | Dark/Light token-block selectors gain their Shapes twin; both blocks + 12 shape ring tokens; new §9b Shapes rules | ui (frontend stylesheet) |

No `GradeMark.tsx`, call-site, `uiConfig.ts`, `CandidateContext.tsx` or `candidate.py` change. `candidate.py` validates a saved theme against the registry's selectable ids, and `CandidateContext` writes any id to `<html data-theme>`, so both pick up the new ids with no edit.

## Stage 1: Register the two Shapes themes

**Done when:** `python -c "from src.utils.config import UI_CONFIG; print(list(UI_CONFIG['themes']))"` prints `['dark', 'light', 'shapes_light', 'shapes_dark']`, and `default_theme` is still `dark`.

1. In `src/utils/config.py`, replace the three comment lines directly above `"themes": {` (currently lines 6043–6045) with:

   ```python
       # AST-2042: theme registry — palette id -> label + whether the profile Theme select offers it.
       # Each id needs a [data-theme="<id>"] selector on an App.css token block; a Shapes twin (AST-2129)
       # shares its sibling's block, so Shapes - Light/Dark can never drift from Light/Dark colours.
   ```

2. In the same dict, after `"light": {"label": "Light", "profile_selectable": True},`, add exactly these two lines (same indentation), so the order is dark, light, shapes_light, shapes_dark (AC 1):

   ```python
           "shapes_light": {"label": "Shapes - Light", "profile_selectable": True},
           "shapes_dark": {"label": "Shapes - Dark", "profile_selectable": True},
   ```

   Leave `"default_theme": "dark"` and the `assert` below it unchanged.

3. Verify from repo root:
   - `python -c "import src.utils.config"` exits 0.
   - The Done-when print above matches exactly.
   - `ruff check src/utils/config.py` reports **102** errors. That is the baseline on this branch before any change. Any increase is new and must be fixed in this stage. The whole-file count is the gate because the file was never ruff-clean.

## Stage 2: Token blocks — twins share, shape ring widths declared

**Done when:**
- `git grep -c -e '--grade-a:' -- src/ui/frontend/src/App.css` prints `src/ui/frontend/src/App.css:2`.
- The Dark block opens `:root, [data-theme="dark"], [data-theme="shapes_dark"] {` and the Light block opens `[data-theme="light"], [data-theme="shapes_light"] {` (AC 2).
- Both blocks declare the same 12 new `--grade-<g>-shape-ring-width[-lettered]` tokens.

1. In `src/ui/frontend/src/App.css` §1 Design Tokens, replace the Dark block's 3-line comment and selector line (currently lines 36–39):

   ```css
   /* Dark is the default palette (:root) and also [data-theme="dark"] so a Dark panel can sit inside a Light page.
      Each [data-theme] block must declare the SAME custom-property names as this one — aliases like
      --confidence-bullet-* included, since var() inside a custom property resolves where it is declared. */
   :root, [data-theme="dark"] {
   ```

   with:

   ```css
   /* Dark is the default palette (:root) and also [data-theme="dark"] so a Dark panel can sit inside a Light page.
      Shapes - Dark (AST-2129) shares this block: same colours, one declaration, no drift.
      Each [data-theme] block must declare the SAME custom-property names as this one — aliases like
      --confidence-bullet-* included, since var() inside a custom property resolves where it is declared. */
   :root, [data-theme="dark"], [data-theme="shapes_dark"] {
   ```

2. Replace the Light block's comment and selector line (currently lines 123–124):

   ```css
   /* AST-2042: Light palette — what the profile's Light applies (UI_CONFIG themes). */
   [data-theme="light"] {
   ```

   with:

   ```css
   /* AST-2042: Light palette — what the profile's Light applies (UI_CONFIG themes).
      Shapes - Light (AST-2129) shares this block: same colours, one declaration, no drift. */
   [data-theme="light"], [data-theme="shapes_light"] {
   ```

3. In the **Dark** block, directly after `--grade-x-ring-width-lettered: 0;`, insert:

   ```css
     /* AST-2129: Shapes ring — SVG stroke width per grade, compact then lettered (Dark: no ring) */
     --grade-a-shape-ring-width: 0px;
     --grade-b-shape-ring-width: 0px;
     --grade-c-shape-ring-width: 0px;
     --grade-d-shape-ring-width: 0px;
     --grade-f-shape-ring-width: 0px;
     --grade-x-shape-ring-width: 0px;
     --grade-a-shape-ring-width-lettered: 0px;
     --grade-b-shape-ring-width-lettered: 0px;
     --grade-c-shape-ring-width-lettered: 0px;
     --grade-d-shape-ring-width-lettered: 0px;
     --grade-f-shape-ring-width-lettered: 0px;
     --grade-x-shape-ring-width-lettered: 0px;
   ```

   ⚠️ **Decision — `0px`, not `0`:** the X ring (Stage 3 step 4) multiplies the width inside `calc()`. `calc(0 * 0.7071)` is a unitless number, which makes the whole `filter` declaration invalid. `calc(0px * 0.7071)` is a valid zero length. The existing `--grade-*-ring-width: 0` tokens stay as they are; they are substituted literally into `box-shadow`, where a bare `0` is legal.

4. In the **Light** block, directly after `--grade-x-ring-width-lettered: 2px;`, insert:

   ```css
     /* AST-2129: Shapes ring — SVG stroke width per grade, compact then lettered */
     --grade-a-shape-ring-width: 1.5px;
     --grade-b-shape-ring-width: 1.5px;
     --grade-c-shape-ring-width: 1.5px;
     --grade-d-shape-ring-width: 1.5px;
     --grade-f-shape-ring-width: 1.5px;
     --grade-x-shape-ring-width: 1.5px;
     --grade-a-shape-ring-width-lettered: 2.5px;
     --grade-b-shape-ring-width-lettered: 2.5px;
     --grade-c-shape-ring-width-lettered: 2.5px;
     --grade-d-shape-ring-width-lettered: 2.5px;
     --grade-f-shape-ring-width-lettered: 2.5px;
     --grade-x-shape-ring-width-lettered: 2.5px;
   ```

   ⚠️ **Decision — separate shape tokens, not reuse of `--grade-*-ring-width`:** Light's compact box-shadow ring is already 1.5px, but its lettered ring is 2px against the brief's 2.5px stroke. Technical scope asks both blocks to declare the shape ring widths compact **and** lettered, per grade (AST-2100 layering). So all 12 are declared and Light/Dark's circle tokens stay untouched (AC 6).

5. Verify: the three Done-when checks above, and `rg -c -e '-shape-ring-width' src/ui/frontend/src/App.css` prints `24` before Stage 3 adds its references.

## Stage 3: §9b Shapes rules — shape, ring, centroid letter

**Done when:**
- `npm run build` in `src/ui/frontend` exits 0. Vite parses App.css, so a malformed rule fails here.
- `npx tsc --noEmit` there exits 0.
- `git diff origin/ftr/AST-2101-shapes-themes -- src/ui/frontend/src/App.css` shows no deleted or modified line in any existing §9b rule; every §9b change is an addition.

1. In `src/ui/frontend/src/App.css` §9b, insert the block below **directly after** the rule

   ```css
   .grade-dot-letterless {
     width: 12px;
     height: 12px;
     font-size: 0;
   }
   ```

   and before `.analysis-header {`. Leave one blank line on each side. The insert is all of steps 2–5, in order, as one contiguous block.

   ⚠️ **Decision — placement is load-bearing:** the Shapes `background`/`box-shadow` reset (`:is(…) .grade-dot`, specificity 0,2,0) ties `.grade-dot-letterless.dot-<g>` (0,2,0) and wins only on source order. So it **must** follow the letterless rules. Every other Shapes rule out-specifies what it overrides.

   ⚠️ **Decision — theme scope selector:** every Shapes rule is prefixed `:is([data-theme="shapes_light"], [data-theme="shapes_dark"])`. `CandidateContext` sets `data-theme` on `<html>`, so a descendant selector reaches every mark. `:is()` counts as one attribute selector (0,1,0) and avoids writing each rule twice.

2. SVG visibility and the circle reset:

   ```css
   /* AST-2129: Shapes themes — each grade is drawn as GradeMark's SVG shape instead of the circle.
      Light and Dark keep the circle: the SVG is never displayed outside the two Shapes themes. */
   .grade-dot > svg {
     display: none;
   }

   /* Drop the circle (fill + inset ring) and lay the shape under the letter. Must follow the letterless
      rules above: background/box-shadow here tie their 0,2,0 specificity and win on source order.
      isolation keeps the z-index -1 SVG in front of the page but behind the mark's own letter. */
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot {
     position: relative;
     isolation: isolate;
     background: none;
     box-shadow: none;
   }

   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot > svg {
     display: block;
     position: absolute;
     inset: 0;
     width: 100%;
     height: 100%;
     overflow: visible; /* the ring stroke straddles the shape edge — never clip it at the box */
     z-index: -1;
   }
   ```

   ⚠️ **Decision — explicit `.grade-dot > svg { display: none }`:** AST-2128's `display="none"` presentation attribute already hides the SVG. This one rule repeats that in the stylesheet, so AC 6 ("SVG computes `display: none`" on Light/Dark) is visible in App.css and no longer depends only on markup. The Shapes rule (0,2,1) outranks it (0,1,1).

   ⚠️ **Decision — `z-index: -1` + `isolation: isolate`:** the letter is a bare text node in the span (AST-2128), so it cannot be layered on its own. An absolutely positioned SVG paints above in-flow text by default. `z-index: -1` sends it under the text, and `isolation` stops it from dropping behind the card background.

3. Fill and ring for A, B, C, D and F:

   ```css
   /* Fill = grade fill; ring = stroke in the grade ring colour at the shape ring width, in screen px
      (non-scaling, so 1.5px stays 1.5px at 12px and 22px); round joins soften diamond/triangle corners. */
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot path {
     vector-effect: non-scaling-stroke;
     stroke-linejoin: round;
   }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .dot-a path { fill: var(--grade-a); stroke: var(--grade-a-ring); stroke-width: var(--grade-a-shape-ring-width-lettered); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .dot-b path { fill: var(--grade-b); stroke: var(--grade-b-ring); stroke-width: var(--grade-b-shape-ring-width-lettered); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .dot-c path { fill: var(--grade-c); stroke: var(--grade-c-ring); stroke-width: var(--grade-c-shape-ring-width-lettered); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .dot-d path { fill: var(--grade-d); stroke: var(--grade-d-ring); stroke-width: var(--grade-d-shape-ring-width-lettered); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .dot-f path { fill: var(--grade-f); stroke: var(--grade-f-ring); stroke-width: var(--grade-f-shape-ring-width-lettered); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot-letterless.dot-a path { stroke-width: var(--grade-a-shape-ring-width); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot-letterless.dot-b path { stroke-width: var(--grade-b-shape-ring-width); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot-letterless.dot-c path { stroke-width: var(--grade-c-shape-ring-width); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot-letterless.dot-d path { stroke-width: var(--grade-d-shape-ring-width); }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot-letterless.dot-f path { stroke-width: var(--grade-f-shape-ring-width); }
   ```

   The one-line-per-grade form matches the existing `.grade-dot-letterless.dot-<g>` rules just above.

4. X, the cross and its ring:

   ```css
   /* X: the cross is a stroke in the X fill — 20 viewBox units lettered, 24 compact, so it scales with the
      box — round caps, no fill. Its ring (Susan's option a: a wider under-stroke in --grade-x-ring) is four
      diagonal drop-shadows offset ring-width × 1/√2: both arms run at 45°, so the shadow pair across each
      arm widens it by exactly the ring width on each side, painted under the cross. Dark's 0px draws nothing. */
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .dot-x path {
     fill: none;
     stroke: var(--grade-x);
     stroke-width: 20;
     stroke-linecap: round;
     vector-effect: none;
   }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot-letterless.dot-x path {
     stroke-width: 24;
   }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .dot-x > svg {
     filter:
       drop-shadow(calc(var(--grade-x-shape-ring-width-lettered) * 0.7071) calc(var(--grade-x-shape-ring-width-lettered) * 0.7071) 0 var(--grade-x-ring))
       drop-shadow(calc(var(--grade-x-shape-ring-width-lettered) * -0.7071) calc(var(--grade-x-shape-ring-width-lettered) * -0.7071) 0 var(--grade-x-ring))
       drop-shadow(calc(var(--grade-x-shape-ring-width-lettered) * 0.7071) calc(var(--grade-x-shape-ring-width-lettered) * -0.7071) 0 var(--grade-x-ring))
       drop-shadow(calc(var(--grade-x-shape-ring-width-lettered) * -0.7071) calc(var(--grade-x-shape-ring-width-lettered) * 0.7071) 0 var(--grade-x-ring));
   }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot-letterless.dot-x > svg {
     filter:
       drop-shadow(calc(var(--grade-x-shape-ring-width) * 0.7071) calc(var(--grade-x-shape-ring-width) * 0.7071) 0 var(--grade-x-ring))
       drop-shadow(calc(var(--grade-x-shape-ring-width) * -0.7071) calc(var(--grade-x-shape-ring-width) * -0.7071) 0 var(--grade-x-ring))
       drop-shadow(calc(var(--grade-x-shape-ring-width) * 0.7071) calc(var(--grade-x-shape-ring-width) * -0.7071) 0 var(--grade-x-ring))
       drop-shadow(calc(var(--grade-x-shape-ring-width) * -0.7071) calc(var(--grade-x-shape-ring-width) * 0.7071) 0 var(--grade-x-ring));
   }
   ```

   ⚠️ **Decision — X ring as diagonal drop-shadows on the SVG.** Option (a) asks for a wider under-stroke in `--grade-x-ring`. AC 3 fixes the X path's own stroke to the X fill, and `GradeMark` renders a single `<path>`, which Boundaries say this ticket may not change. So a second stroke has to come from CSS on the SVG. Each `drop-shadow` paints a copy of the cross, offset and in the ring colour, beneath it. Offsets of ±w/√2 along both diagonals shift each 45° arm perpendicular to itself by exactly `w`. The result is an under-ring of the full ring width along both arms; at the caps it is up to √2·w (about 2.1px for compact). Dark's `0px` tokens give zero-offset shadows hidden under the cross, so there is no ring (AC 4).
   Rejected alternatives:
   - a second `<path>` in `GradeMark.tsx`: out of Boundaries; sibling AST-2128 owns that file.
   - a `::before` with a `mask-image` data-URL cross: repeats the geometry in CSS and cannot read the ring-width token.
   - a ring-coloured X path stroke: contradicts AC 3.
   No local custom property is used for `w/√2`. `test_AppCss` requires every `var(--x)` to be defined in a token block, and a rule-local property would fail that.

   ⚠️ **Decision — `vector-effect: none` on X:** the brief's 24/20 cross widths are viewBox units and must scale with the box. The general `.grade-dot path` rule's `non-scaling-stroke` is meant only for the 1.5/2.5px rings. `.dot-x path` (0,2,1) ties that rule and follows it, so it wins.

5. Lettered layout — the letter at the centroid, and no letter on X:

   ```css
   /* Lettered: the letter sits at the shape's centroid, at the brief's sizes on the 22px box (46/100; 38/100 in
      triangles). The letter is the span's own text node, so size and offset go on the span: padding moves the
      flex-centred letter while border-box keeps the mark 22px. 0,3,0 beats the report-context 11px rules. */
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot:is(.dot-a, .dot-b, .dot-c) {
     font-size: calc(22px * 0.46);
   }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot:is(.dot-d, .dot-f) {
     font-size: calc(22px * 0.38);
   }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot.dot-d {
     padding-top: calc(22px * 0.26); /* up triangle: centre 63/100 = 50 + 26/2 */
   }
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot.dot-f {
     padding-bottom: calc(22px * 0.22); /* down triangle: centre 39/100 = 50 − 22/2 */
   }
   /* X: the cross is the letter, so no glyph. font-size 0, not visibility, so the mark keeps its image role and name. */
   :is([data-theme="shapes_light"], [data-theme="shapes_dark"]) .grade-dot.dot-x {
     font-size: 0;
   }
   ```

   ⚠️ **Decision — letter centring math:** `.grade-dot` is `inline-flex` with `align-items: center`, and the global `*, *::before, *::after { box-sizing: border-box; }` reset applies. So padding shrinks the content box and the 22px mark stays 22px. The letter centre sits at `p_top + (22 − p_top − p_bottom)/2`:
   - D: `padding-top 5.72px` → 13.86px = 63%.
   - F: `padding-bottom 4.84px` → 8.58px = 39%.
   - A, B, C: no padding → 50%.
   Sizes: 22 × 0.46 = 10.12px and 22 × 0.38 = 8.36px (AC 5). `22px` is the `.grade-dot` box; the 12px letterless marks render no text, so these sizes do not affect them. Percentage padding is not used because it resolves against the parent's width, not the mark's.

   ⚠️ **Decision — X letter hidden with `font-size: 0`, not `visibility: hidden`:** AC 5's pass line names `visibility: hidden` or `display: none` for the X letter. The letter is the span's own text node, so either property would have to go on the span. That would remove the `role="img"` / `aria-label` mark from the accessibility tree and break parent capability 6 (accessible name on every mark). `font-size: 0` leaves no visible glyph, which satisfies AC 5's fail condition ("a visible letter on X"), and keeps the name. It is the same technique `.grade-dot-letterless` already uses. **Betty:** assert X's span computes `font-size: 0px`, not visibility.

6. Verify (in `src/ui/frontend` unless noted):
   - `npx tsc --noEmit` exits 0.
   - `npm run build` exits 0. It writes `dist/`, which `src/ui/frontend/.gitignore` ignores; do not commit build output.
   - From repo root: `git grep -c -e '--grade-a:' -- src/ui/frontend/src/App.css` still prints `src/ui/frontend/src/App.css:2`.
   - From repo root: `git grep -n '#[0-9a-fA-F]\{3,8\}' -- src/ui/frontend/src/App.css` — any new hit must be inside a token block. The Stage 3 insert adds none.
   - From repo root: `python -c "import src.utils.config"` exits 0.
   - **Expected reds, not this stage's to fix.** Betty updates these in `qa-child` per Scope; do **not** edit `tests/`:
     - `test_config.py::TestAst2047ThemeRegistry` pins `["dark", "light"]` and `["Dark", "Light"]`.
     - In `test_AppCss.test.tsx`, `blockRe` does not recognise a selector-list block. So "one block per registry id", "Light block token names", the AST-2076 bug-repro and "no hex … outside token blocks" can fail until her selector-list / twin update lands.
     Record the exact failing test names in the build-child Review stub for Betty. Any other red is a product bug in this stage.

## Integration notes (reference only — not this ticket's work)

- **Mark DOM (from AST-2128):** `span.grade-dot.dot-<g>[.grade-dot-letterless][role=img][aria-label=<G>] > svg[viewBox="0 0 100 100"][aria-hidden][display=none] > path[d]`, then the letter as a bare text node (lettered marks only).
- **Betty (`qa-child`), AC 4 on X:** X's ring is the SVG `filter` (four `drop-shadow`s in `--grade-x-ring`), not the path stroke. AC 3 fixes X's path `stroke` to `--grade-x`. Assert X's ring on `.dot-x > svg` `filter`.
- **Betty, AC 5 on X:** assert `font-size: 0px` on the X span (see the Stage 3 step 5 decision).
- **Betty, `test_AppCss`:** the two token blocks now open with selector lists (`:root, [data-theme="dark"], [data-theme="shapes_dark"] {` and `[data-theme="light"], [data-theme="shapes_light"] {`). Every registry id maps to a selector on exactly one block. The Shapes ids are twins with no block of their own.

## Out-of-scope observations (for Chuckles / Susan — not planned here)

- **Shapes - Light wordmark:** `NavigationShell.tsx` swaps in the light wordmark only when `theme === "light"`. With Shapes - Light selected, the page gets Light colours but keeps the dark-palette logo. `NavigationShell.tsx` is in neither child's Scope; fixing it is a one-line widening (e.g. `"light"` or `"shapes_light"`) that needs a Scope amendment or a follow-up ticket.
- **Pre-existing `test_AppCss` reds:** AST-2128's Radia review asked whether AST-2129 should close the two `test_AppCss` failures (AC5/AC9 hex on `--tp-lvl`) that exist on `origin/dev`. They are not in this ticket's Scope or ACs and are not planned here. AC 7's "`test_AppCss.test.tsx` passes" therefore depends on Betty's manifest carrying the same named exclusions as AST-2128's did.

## Estimate

Confirm Chuckles estimate: 3 — agree
