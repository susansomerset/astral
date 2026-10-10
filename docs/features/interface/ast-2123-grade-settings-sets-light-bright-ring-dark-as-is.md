# AST-2123 — Grade settings sets (Light Bright + ring, Dark as-is)

- **Parent:** [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100) — Light theme: replace grade colours with "Bright + ring" palette
- **Ticket:** [AST-2123](https://linear.app/astralcareermatch/issue/AST-2123)
- **Publish ref:** `origin/sub/AST-2100/AST-2123-grade-settings-sets`
- **Canon Scope:** none (locked at Discussion). No directive applies to stylesheet tokens.
- **Blocked by:** [AST-2122](https://linear.app/astralcareermatch/issue/AST-2122) — already merged into `origin/ftr/AST-2100-bright-ring-grade-palette` and carried onto this sub by `sync-child.sh`.

Every grade-mark setting becomes an explicit theme token, declared in full in both the Dark and the Light token blocks of `App.css`: the per-grade base (fill, ring colour, compact ring width), the per-grade lettered layer (letter colour, size, weight, lettered ring width), and the global confidence-bullet settings. Light moves to the Bright + ring palette. Dark keeps today's look (its ring widths are 0). The §9b grade-dot rules and the confidence-bullet rules read every value from those tokens. The now-unregistered `light_parchment` / `light_slate` blocks, the §16 Theme Examples CSS, and the `--text-on-grade*` tokens are deleted. Only `src/ui/frontend/src/App.css` changes. Tests and the test bible belong to Betty (`qa-child`).

## Codebase facts the plan relies on (verified at branch tip `ef64fa7cb`)

- `sync-child.sh … --ftr AST-2100-bright-ring-grade-palette` exited 0 and fast-forwarded the sub to the ftr tip (AST-2122's code, tests and review are present). Use the full parent segment `AST-2100-bright-ring-grade-palette` for `--ftr`; `--ftr AST-2100` silently skips the parent merge because `origin/ftr/AST-2100` does not exist.
- `UI_CONFIG["themes"]` is now `dark` + `light` only (AST-2122), so deleting the two alternate CSS blocks cannot fail the "every registry id has a block" check.
- `App.css` layout (line numbers at `ef64fa7cb`; edit by content, not by number):
  - Table of contents line 31: ` * 16. Theme Examples (AST-2042)`.
  - Dark block `:root, [data-theme="dark"] {` lines 40–83. Grade fills lines 56–62, confidence aliases 63–65, `--text-on-grade` / `--text-on-grade-f` lines 70–71.
  - Light block comment lines 85–86, `[data-theme="light"] {` lines 87–127. Grade fills 103–108, confidence aliases 109–110, `--text-on-grade` / `--text-on-grade-f` lines 114–115.
  - `[data-theme="light_parchment"]` lines 129–169, `[data-theme="light_slate"]` lines 171–211, then a blank line and `/* === 2. Base / Reset === */` at 213.
  - Report-context rules: `.recommended-report-tab-label .grade-dot { font-size: 11px; … }` (line 1111) and `.recommended-report-phase-grade-cell .grade-dot { font-size: 11px; }` (line 1133). Both are specificity (0,2,0).
  - §9b Grade Dots lines 1287–1315: `.grade-dot` (font-size 12px, weight 700, `color: var(--text-on-grade)`), six `.dot-<g>` rules, `.grade-dot-letterless` (12px box, `font-size: 0`).
  - Confidence rules lines 1348–1369: `.confidence-bullets` (`gap: 3px`), `.confidence-bullet` (`width: 4px; height: 4px; opacity: 0.55`), `.confidence-bullet--on` (`opacity: 1`).
  - §16 Theme Examples lines 3002–3084, running to end of file. Line 3000 is the closing `}` of `.icon-control:disabled`, line 3001 is blank.
- Markup (unchanged by this ticket): every grade dot is `grade-dot dot-<g>` (`JobsSkipped.tsx`, `JobsProcessing.tsx`, `AgentAnalysisHeader.tsx`, `recommendedJobReport.tsx`), and the compact variant adds `grade-dot-letterless` (`recommendedJobReport.tsx` only). No `.dot-<g>` element exists without `.grade-dot`.
- `--text-on-grade` / `--text-on-grade-f` have no consumers outside `App.css` (`git grep text-on-grade -- src` hits only the token blocks and §9b).
- `tests/component/frontend/test_AppCss.test.tsx` parses each token block with `\{([^}]*)\}` (so a block body must not contain `}`), requires every Light block to declare exactly the Dark token names, bans hex outside token blocks, and requires every `var(--x)` to be defined in some token block.
- **Known pre-existing red, not this ticket:** two `test_AppCss` cases ("no hex … every var(--x) is defined" and "AST-2049: … every var(--x) in source is defined") fail at `ef64fa7cb` on `--tp-lvl`, a local custom property from `origin/dev`'s §12b Task Performance rules (`5f4850a20`). Do not touch §12b. After each stage, those two cases may only fail on `--tp-lvl`; any other name in the failure output is a defect in this ticket.
- The Light fills give a minimum pairwise OKLab distance of 15.7 (C–D), computed with the standard sRGB → OKLab formula (next closest B–C 18.0). AC 3 holds by value.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/App.css` | Delete TOC §16 line, `light_parchment` / `light_slate` blocks and §16 rules; rewrite Light block comment; Light fills → Bright + ring; declare grade base, lettered and confidence settings in Dark and Light blocks; retire `--text-on-grade*`; §9b and confidence rules read the settings | ui (styles) |

**Betty (`qa-child`): not in this ticket's Scope, so not planned here.** For her manifest, noted only: `test_AppCss.test.tsx` line 27–29 has a superset check that the comment says AST-2123 restores to exact equality, and jsdom does not load `App.css`, so the computed-style ACs (2, 4, 5, 6, 7, 11) cannot be asserted by rendering in vitest.

## Stage 1: Delete the retired CSS

**Done when:** `git grep -n -i -e theme_examples -e ThemeExamples -e theme-examples -e 'Theme Examples' -e theme_example_grade_sets -e light_parchment -e light_slate -- src` returns nothing, `App.css` has exactly two token blocks (Dark, Light), and `npm run build` in `src/ui/frontend` exits 0.

1. In `src/ui/frontend/src/App.css`, delete the table-of-contents line ` * 16. Theme Examples (AST-2042)`. The TOC then ends with ` * 15. Icon control` followed by ` */`.

2. Replace the two-line comment above `[data-theme="light"] {`:

   ```css
   /* AST-2042: Light palettes. "light" is what the profile's Light applies; the other two are
      examples-only alternates shown on Tools -> Theme Examples (UI_CONFIG themes). */
   ```

   with exactly:

   ```css
   /* AST-2042: Light palette — what the profile's Light applies (UI_CONFIG themes). */
   ```

3. Delete the whole `[data-theme="light_parchment"] { … }` block and the blank line after it, then the whole `[data-theme="light_slate"] { … }` block. After the deletion, the Light block's closing `}` is followed by one blank line and then `/* === 2. Base / Reset === */`.

4. Delete everything from the blank line after `.icon-control:disabled { … }` (after line 3000 at `ef64fa7cb`) to the end of the file: the `/* === 16. Theme Examples (AST-2042) === */` heading and every `.theme-examples*` rule and comment under it. The file ends with the `.icon-control:disabled` rule's `}` and a single trailing newline.

5. Verify, from `src/ui/frontend`: `npm run build` exits 0, `npm run lint` exits 0, and `npm run test:component -- test_AppCss` fails only on `--tp-lvl` (see Codebase facts). Run the Done-when grep from the repo root.

6. Commit only `src/ui/frontend/src/App.css`: `code(AST-2123): delete Light alternate blocks and §16 Theme Examples CSS`. Publish per `build-child`.

## Stage 2: Grade settings sets and the rules that read them

**Done when:** each of the 47 settings labels below appears exactly twice in `App.css` as a declaration (`git grep -c -- '<label>:' src/ui/frontend/src/App.css` = 2), `git grep -n 'text-on-grade' -- src/ui/frontend/src src/utils` returns nothing, `git grep -n -A6 '^\.confidence-bullet' -- src/ui/frontend/src/App.css` shows no `4px`, `3px` or `0.55`, and `npm run build` exits 0. In a browser on Light, a `.dot-c` dot computes `background-color: rgb(247, 103, 7)`.

The labels (with `<g>` = a, b, c, d, f, x where shown): `--grade-<g>` (6, fills, already exist), `--grade-<g>-ring` (6), `--grade-<g>-ring-width` (6), `--grade-<g>-ink` (6), `--grade-<g>-letter-size` (6), `--grade-<g>-letter-weight` (6), `--grade-<g>-ring-width-lettered` (6), `--confidence-bullet-active`, `--confidence-bullet-inactive` (already exist), `--confidence-bullet-inactive-opacity`, `--confidence-bullet-size`, `--confidence-bullet-gap`. That is 6 × 7 + 5 = 47 declarations per block.

⚠️ **Decision:** Ring colours and letter colours are written as hex literals from the settings tables, including Dark rings that equal their fill (e.g. `--grade-a-ring: #28a745`), rather than `var(--grade-a)`. The tables give literal values, and literals keep each block self-contained. The two existing confidence colour aliases stay `var(--text-secondary)` / `var(--text-muted)`, because they already resolve to the table values in both blocks and the ticket says they "already exist".

⚠️ **Decision:** Dark ring widths are the unitless `0` from the table. In `box-shadow: inset 0 0 0 0 <colour>` that is a valid zero spread, which computes to `0px` and draws nothing (AC 6). No theme-scoped selector is added.

⚠️ **Decision:** Comments added inside token blocks must not contain `}` or a `<label>:` string, so the `test_AppCss` block parser and the AC 1 `git grep -c` count stay correct.

1. In the Dark block (`:root, [data-theme="dark"]`), leave the six fill lines (`--grade-a: #28a745;` … `--grade-x: #a78bfa;`) unchanged. Directly after `--grade-x: #a78bfa;` and before `/* Confidence bullets (AST-357) … */`, insert exactly:

   ```css
     /* AST-2123: grade base settings — ring colour + compact ring width (Dark: width 0, no ring; colour = fill) */
     --grade-a-ring: #28a745;
     --grade-b-ring: #ffc107;
     --grade-c-ring: #fd7e14;
     --grade-d-ring: #dc3545;
     --grade-f-ring: #8b0000;
     --grade-x-ring: #a78bfa;
     --grade-a-ring-width: 0;
     --grade-b-ring-width: 0;
     --grade-c-ring-width: 0;
     --grade-d-ring-width: 0;
     --grade-f-ring-width: 0;
     --grade-x-ring-width: 0;
     /* AST-2123: lettered settings — a lettered dot takes its grade base and adds these */
     --grade-a-ink: #1a1424;
     --grade-b-ink: #1a1424;
     --grade-c-ink: #1a1424;
     --grade-d-ink: #1a1424;
     --grade-f-ink: #e8e4f0;
     --grade-x-ink: #1a1424;
     --grade-a-letter-size: 12px;
     --grade-b-letter-size: 12px;
     --grade-c-letter-size: 12px;
     --grade-d-letter-size: 12px;
     --grade-f-letter-size: 12px;
     --grade-x-letter-size: 12px;
     --grade-a-letter-weight: 700;
     --grade-b-letter-weight: 700;
     --grade-c-letter-weight: 700;
     --grade-d-letter-weight: 700;
     --grade-f-letter-weight: 700;
     --grade-x-letter-weight: 700;
     --grade-a-ring-width-lettered: 0;
     --grade-b-ring-width-lettered: 0;
     --grade-c-ring-width-lettered: 0;
     --grade-d-ring-width-lettered: 0;
     --grade-f-ring-width-lettered: 0;
     --grade-x-ring-width-lettered: 0;
   ```

2. In the Dark block, directly after `--confidence-bullet-inactive: var(--text-muted);`, insert exactly:

   ```css
     --confidence-bullet-inactive-opacity: 0.55;
     --confidence-bullet-size: 4px;
     --confidence-bullet-gap: 3px;
   ```

3. In the Dark block, delete the two lines `--text-on-grade: #1a1424;` and `--text-on-grade-f: #e8e4f0;`.

4. In the Light block (`[data-theme="light"]`), replace the six fill lines (`--grade-a: #1e7b34;` … `--grade-x: #6b46c1;`) with exactly:

   ```css
     /* AST-2123: Bright + ring — grade base settings: fill, ring colour, compact ring width */
     --grade-a: #2f9e44;
     --grade-b: #f5b700;
     --grade-c: #f76707;
     --grade-d: #c92a3a;
     --grade-f: #5c1414;
     --grade-x: #7048e8;
     --grade-a-ring: #006200;
     --grade-b-ring: #b57700;
     --grade-c-ring: #b41400;
     --grade-d-ring: #850000;
     --grade-f-ring: #210000;
     --grade-x-ring: #4100a8;
     --grade-a-ring-width: 1.5px;
     --grade-b-ring-width: 1.5px;
     --grade-c-ring-width: 1.5px;
     --grade-d-ring-width: 1.5px;
     --grade-f-ring-width: 1.5px;
     --grade-x-ring-width: 1.5px;
     /* AST-2123: lettered settings — a lettered dot takes its grade base and adds these */
     --grade-a-ink: #ffffff;
     --grade-b-ink: #2b2000;
     --grade-c-ink: #1f0d00;
     --grade-d-ink: #ffffff;
     --grade-f-ink: #ffffff;
     --grade-x-ink: #ffffff;
     --grade-a-letter-size: 12px;
     --grade-b-letter-size: 12px;
     --grade-c-letter-size: 12px;
     --grade-d-letter-size: 12px;
     --grade-f-letter-size: 12px;
     --grade-x-letter-size: 12px;
     --grade-a-letter-weight: 700;
     --grade-b-letter-weight: 700;
     --grade-c-letter-weight: 700;
     --grade-d-letter-weight: 700;
     --grade-f-letter-weight: 700;
     --grade-x-letter-weight: 700;
     --grade-a-ring-width-lettered: 2px;
     --grade-b-ring-width-lettered: 2px;
     --grade-c-ring-width-lettered: 2px;
     --grade-d-ring-width-lettered: 2px;
     --grade-f-ring-width-lettered: 2px;
     --grade-x-ring-width-lettered: 2px;
   ```

5. In the Light block, directly after `--confidence-bullet-inactive: var(--text-muted);`, insert the same three lines as step 2 (`0.55`, `4px`, `3px`).

6. In the Light block, delete the two lines `--text-on-grade: #ffffff;` and `--text-on-grade-f: #ffffff;`.

7. In §9b, replace the comment line `/* Grade dot badge — circular, colored background, dark centered letter */` and the `.grade-dot { … }` rule with exactly:

   ```css
   /* Grade dot badge — circular. Fill, ring and letter all come from the per-grade theme settings (AST-2123). */
   .grade-dot {
     display: inline-flex;
     align-items: center;
     justify-content: center;
     width: 22px;
     height: 22px;
     border-radius: 50%;
     flex-shrink: 0;
   }
   ```

   ⚠️ **Decision:** `font-size: 12px`, `font-weight: 700` and `color` leave `.grade-dot`, so the letter is sourced only from the per-grade settings (AC 5). Every rendered `.grade-dot` carries a `.dot-<g>` class (Codebase facts), so no dot loses its letter styling.

8. In §9b, replace the six one-line `.dot-a` … `.dot-x` rules with exactly:

   ```css
   /* Lettered (default): grade base fill + ring colour, plus the grade's lettered settings.
      Specificity 0,1,0 on purpose: the report-context .grade-dot rules (0,2,0) keep their 11px letter size. */
   .dot-a {
     background: var(--grade-a);
     color: var(--grade-a-ink);
     font-size: var(--grade-a-letter-size);
     font-weight: var(--grade-a-letter-weight);
     box-shadow: inset 0 0 0 var(--grade-a-ring-width-lettered) var(--grade-a-ring);
   }
   .dot-b {
     background: var(--grade-b);
     color: var(--grade-b-ink);
     font-size: var(--grade-b-letter-size);
     font-weight: var(--grade-b-letter-weight);
     box-shadow: inset 0 0 0 var(--grade-b-ring-width-lettered) var(--grade-b-ring);
   }
   .dot-c {
     background: var(--grade-c);
     color: var(--grade-c-ink);
     font-size: var(--grade-c-letter-size);
     font-weight: var(--grade-c-letter-weight);
     box-shadow: inset 0 0 0 var(--grade-c-ring-width-lettered) var(--grade-c-ring);
   }
   .dot-d {
     background: var(--grade-d);
     color: var(--grade-d-ink);
     font-size: var(--grade-d-letter-size);
     font-weight: var(--grade-d-letter-weight);
     box-shadow: inset 0 0 0 var(--grade-d-ring-width-lettered) var(--grade-d-ring);
   }
   .dot-f {
     background: var(--grade-f);
     color: var(--grade-f-ink);
     font-size: var(--grade-f-letter-size);
     font-weight: var(--grade-f-letter-weight);
     box-shadow: inset 0 0 0 var(--grade-f-ring-width-lettered) var(--grade-f-ring);
   }
   .dot-x {
     background: var(--grade-x);
     color: var(--grade-x-ink);
     font-size: var(--grade-x-letter-size);
     font-weight: var(--grade-x-letter-weight);
     box-shadow: inset 0 0 0 var(--grade-x-ring-width-lettered) var(--grade-x-ring);
   }

   /* Compact (letterless): same fill + ring colour, compact ring width */
   .grade-dot-letterless.dot-a { box-shadow: inset 0 0 0 var(--grade-a-ring-width) var(--grade-a-ring); }
   .grade-dot-letterless.dot-b { box-shadow: inset 0 0 0 var(--grade-b-ring-width) var(--grade-b-ring); }
   .grade-dot-letterless.dot-c { box-shadow: inset 0 0 0 var(--grade-c-ring-width) var(--grade-c-ring); }
   .grade-dot-letterless.dot-d { box-shadow: inset 0 0 0 var(--grade-d-ring-width) var(--grade-d-ring); }
   .grade-dot-letterless.dot-f { box-shadow: inset 0 0 0 var(--grade-f-ring-width) var(--grade-f-ring); }
   .grade-dot-letterless.dot-x { box-shadow: inset 0 0 0 var(--grade-x-ring-width) var(--grade-x-ring); }
   ```

   ⚠️ **Decision:** The lettered settings sit on the plain `.dot-<g>` rule and the compact variant overrides only the ring width, instead of a `.dot-<g>:not(.grade-dot-letterless)` lettered rule. A `:not()` selector raises specificity to (0,2,0) or more and, being declared after the report-context rules, would override their 11px letter size (AC 5). This layout needs no change to the report-context rules or to markup.

9. Leave the existing `/* AST-1968: … */` comment and `.grade-dot-letterless { width: 12px; height: 12px; font-size: 0; }` rule byte-identical and **after** the rules from step 8. Its `font-size: 0` beats `.dot-<g>`'s `font-size` only by source order at equal specificity (0,1,0), so it must not move above them.

10. In `.confidence-bullets`, replace `gap: 3px;` with `gap: var(--confidence-bullet-gap);`.

11. In `.confidence-bullet`, replace `width: 4px;` with `width: var(--confidence-bullet-size);`, `height: 4px;` with `height: var(--confidence-bullet-size);`, and `opacity: 0.55;` with `opacity: var(--confidence-bullet-inactive-opacity);`. Leave `border-radius: 50%` and `background` unchanged. Leave `.confidence-bullet--on` (`opacity: 1`) unchanged.

12. Leave the two report-context rules (`.recommended-report-tab-label .grade-dot`, `.recommended-report-phase-grade-cell .grade-dot`) byte-identical.

13. Verify, from the repo root:
    - For each of the 47 labels, `git grep -c -- '<label>:' src/ui/frontend/src/App.css` prints `2`. Run it as one loop, for example:
      `for g in a b c d f x; do for s in "" -ring -ring-width -ink -letter-size -letter-weight -ring-width-lettered; do echo "--grade-$g$s: $(git grep -c -- "--grade-$g$s:" src/ui/frontend/src/App.css)"; done; done; for s in active inactive inactive-opacity size gap; do echo "--confidence-bullet-$s: $(git grep -c -- "--confidence-bullet-$s:" src/ui/frontend/src/App.css)"; done`
      Every count must read `src/ui/frontend/src/App.css:2`.
    - `git grep -n 'text-on-grade' -- src/ui/frontend/src src/utils` returns nothing.
    - `git grep -n -e '#a06500' -e '#c05621' -e '#c53030' -- src/ui/frontend/src/App.css` returns nothing.
    - `git grep -n -A6 '^\.confidence-bullet' -- src/ui/frontend/src/App.css` shows `var(--confidence-bullet-` for gap, size and opacity, and no `4px`, `3px` or `0.55`.
    - From `src/ui/frontend`: `npm run build` exits 0, `npm run lint` exits 0, and `npm run test:component -- test_AppCss` fails only on `--tp-lvl`.
    - Browser spot check (`zsh -l ~/astral/launch.sh` is Susan's launcher; any local dev server on this worktree is fine): with the profile on Light, a Recommended list compact `.dot-c` dot computes `background-color: rgb(247, 103, 7)` and `box-shadow: rgb(180, 20, 0) 0px 0px 0px 1.5px inset`. A report tab dot computes `font-size: 11px` and a 2px spread. On Dark, the same dots show today's fills and a `0px` spread.

14. Commit only `src/ui/frontend/src/App.css`: `code(AST-2123): grade base, lettered and confidence settings sets in Dark and Light; §9b and bullets read them`. Publish per `build-child`.

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

**Ticket:** AST-2123
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2100/AST-2123-grade-settings-sets` @ `d648e8416d757965cf886201ecdda0cd8fefab61`

## Canon scores

_(empty — parent and child Canon Scope locked **none** at Discussion; no directive ids to score.)_

## Traceability

AC1→Stage 2 (1–2, 5, 13); AC2→Stage 2 (4, 13 browser); AC3→Stage 2 (4 values; plan documents OKLab ≥15); AC4→Stage 2 (8 letterless overrides, 13); AC5→Stage 2 (7–9, 12, 13); AC6→Stage 2 (1, 8 Dark widths 0, 13); AC7→Stage 2 (2, 5, 10–11, 13); AC8→Stage 1 (1–4, 5); AC9→Stage 1 (3–4, 5); AC10→Stage 2 (3, 6, 13 grep); AC11→Stage 2 (4 Light fills only; 13 spot-check); builds→Stage 1–2 `npm run build` / lint.

## Findings

### discuss

- **Location:** Linear assignee vs validate-plan §1
- **Finding:** Ticket assignee is Ada Lovelace, not Joan; spawn still requested Joan review. Plan content is unaffected.
- **Recommendation:** Chuckles may reassign Joan only for the validate gate if your workflow requires it; no plan doc change.

- **Location:** Child AC 2–7, 11; plan `Files Changed` / Betty note
- **Finding:** Computed-style and OKLab ACs are not automatable in vitest (`test_AppCss` structural only); Stage 2 step 13 browser spot-check + parent UAT carry visual proof. Consistent with App.css-only Scope.
- **Recommendation:** None for approval; keep step 13 in the build checklist.

### acceptable

- **Location:** AST-2122 dependency; Stage 1 before Stage 2; `test_every_registry_id_has_an_app_css_block`
- **Finding:** Ordering matches parent partition; post-sync two-theme registry before deleting alternate CSS blocks.
- **Recommendation:** None.

- **Location:** §9b specificity (`:not()` avoided); report-context 11px rules unchanged
- **Finding:** Plan explicitly addresses AC 5 letter-size regression risk.
- **Recommendation:** None.

- **Location:** `test_AppCss` / `--tp-lvl` pre-existing red
- **Finding:** Documented carve-out; stage verify gates limit failures to `--tp-lvl` only.
- **Recommendation:** None.

context_tokens≈32000
