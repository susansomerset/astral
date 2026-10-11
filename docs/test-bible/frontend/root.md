# App and routes

**Test tree:** `tests/component/root/`

## Coverage map

Vitest tests live under **`tests/component/frontend/`** (mirror `components/`, `pages/`, `contexts/`, `lib/`, and higher-level **`test_App`** / **`test_routes`** as needed).

There is **no** per-source-file branch-lock table (**§6b**). Prefer adding or extending tests beside the modules they guard. Coverage artifacts land in **`tests/.coverage/frontend/`** when `./scripts/testing/run_component_tests.sh` runs the Vitest **coverage** target.

| Ticket | Behavior | Sources | Manifest |
| --- | --- | --- | --- |
| **AST-2129** | Shapes - Light / Shapes - Dark: twins on the Light / Dark token-block selector lists; per-grade shape ring width tokens; Shapes-only §9b shape, ring and centroid-letter rules | `src/ui/frontend/src/App.css`, `src/utils/config.py` | **`test_AppCss.test.tsx`** (revised parser + 9 new cases), **`TestAst2047ThemeRegistry`**, **`test_api_system`** theme registry — § AST-2129 below |
| **AST-2123** | Grade base / lettered / confidence settings tokens in Dark + Light; §9b and confidence rules read them; alternate blocks, §16 and `--text-on-grade*` deleted | `src/ui/frontend/src/App.css` | **`test_AppCss.test.tsx`** (exact block ↔ registry restored) + AC greps — § AST-2123 below |
| **AST-2122** | `App.css` theme token-block contract + AST-2049 epic-wide hex / `var()` guard (moved from the retired Theme Examples page test) | `src/ui/frontend/src/App.css`, all non-test `src/ui/frontend/src/**/*.{ts,tsx,css}` | **`tests/component/frontend/test_AppCss.test.tsx`** (5) — § AST-2122 below |
| **AST-1317** | Amend `pattern.ui.shared-button-roles` with optional `in-row` size; unused `.btn.in-row` in `App.css` | `src/ui/frontend/src/App.css`, `canon/patterns/ui/pattern.ui.shared-button-roles.md`, `canon/patterns/HARVEST.md` | docs-acceptance (grep/read) — no pytest; call-site apply is **AST-1318** |
| **AST-1300** | Approved `pattern.ui.shared-button-roles` + `pattern.ui.icon-control`; unused `.btn` / `.icon-control` in `App.css` | `src/ui/frontend/src/App.css`, `canon/patterns/ui/pattern.ui.shared-button-roles.md`, `canon/patterns/ui/pattern.ui.icon-control.md`, `canon/patterns/README.md`, `canon/patterns/HARVEST.md` | docs-acceptance (grep/read) — no pytest; call-site remediations are **AST-1301** / **AST-1302** |

---

### AST-2129 · AST-2101 (Shapes - Light and Shapes - Dark themes)

**Publish:** `origin/sub/AST-2101/AST-2129-shapes-themes`. `UI_CONFIG["themes"]` gains `shapes_light` and `shapes_dark`, both profile-selectable, and the default stays `dark`. There is no new token block. The Dark block opens `:root, [data-theme="dark"], [data-theme="shapes_dark"]` and the Light block opens `[data-theme="light"], [data-theme="shapes_light"]`. Each block declares 12 shape ring width tokens (`--grade-<g>-shape-ring-width[-lettered]`): Light 1.5px / 2.5px, Dark 0px. New §9b rules apply only under `:is([data-theme="shapes_light"], [data-theme="shapes_dark"])`. They drop the circle, show `GradeMark`'s SVG (AST-2128), fill the path with the grade fill, and stroke the ring as a non-scaling stroke. X is a stroke-only cross with a four-`drop-shadow` ring. Letters are sized and padded to the triangle centroids, and X gets `font-size: 0`. One unscoped rule, `.grade-dot > svg { display: none }`, keeps Light and Dark on the circle.

| Behavior | Test |
| --- | --- |
| Token-block parser reads selector lists; blocks keyed by first `[data-theme]` id; Shapes twins have no block of their own | **`test_AppCss.test.tsx`** › **`Dark is :root and [data-theme=dark]; one block per registry id`** (revised: `blockRe` + twin exemption) |
| AC 2: the two exact selector lists; every registry id on exactly one block; twin on its sibling's block; `--grade-a:` declared twice | › **`AST-2129 AC2: each Shapes twin sits on its sibling's block…`** (new) |
| Light names = Dark names; AST-2076 accent equality | existing cases, unchanged (now parse the selector-list blocks) |
| AC 4, token half: shape ring widths per grade (Light 1.5/2.5px, Dark 0px) | › **`AST-2129 AC4 (token half)…`** (new) |
| AC 6, static half: unscoped `.grade-dot > svg { display: none }` is the only unscoped SVG/path grade rule | **`App.css Shapes grade marks — AST-2129`** › **`AC6…`** (new) |
| AC 3: circle dropped (`background`/`box-shadow: none`); SVG `display: block`, `overflow: visible`, 100% box; non-scaling stroke + round joins | › **`AC3: the circle is dropped…`** (new) |
| AC 3/4 A–F: path `fill: var(--grade-<g>)`, `stroke: var(--grade-<g>-ring)`, lettered/compact `stroke-width` tokens | › **`AC3/AC4 <g>…`** (new, 5 cases) |
| AC 3/4 X: `fill: none`, `stroke: var(--grade-x)`, 20 / 24 units, round caps; ring = 4 `drop-shadow`s in `--grade-x-ring` on `.dot-x > svg` at the matching width token | › **`AC3/AC4 X…`** (new) |
| AC 5: font-size ratios 0.46 / 0.38; D/F centre = 50 ± padding/2 within ±3 of 63 / 39; X `font-size: 0` (keeps the img role, per the plan's Stage 3 decision, not `visibility`) | › **`AC5…`** (new) |
| AC 1: registry exactly four ids, labels, selectable, default `dark`; profile Theme select options = selectable entries | **`test_config.py::TestAst2047ThemeRegistry`** (2 revised) |
| AC 1: `GET /api/ui_config` serves exactly the four entries | **`test_api_system.py::TestSystemAuthRoutes::test_ui_config_serves_theme_registry`** (revised) |

**Repro check:** against the pre-change ftr `App.css`, 13 of 16 `test_AppCss` cases are red: all 9 new AST-2129 cases, the 2 `--tp-lvl` cases, plus the AC2 selector and AC4 token cases that need the twins. Against the product, 14 pass and only the 2 `--tp-lvl` cases are red.

**Not covered by component tests (jsdom has no cascade, `:is()` or `var()` resolution):** computed `fill`, `stroke`, `stroke-width`, `background-color`, `box-shadow`, `display`, letter box centre, and the pixel ring width at 12px and 22px (AC 3–6, computed half). These go to browser / parent UAT, as with AST-2123. The static cases above pin the declarations that produce them.

**Broken / obsolete (revised this pass):** `test_AppCss` (selector-list `blockRe`, four-id `THEMES` mirror), `TestAst2047ThemeRegistry::test_registry_ids_selectable_and_default` and `::test_profile_theme_select_options_are_the_selectable_entries` (two → four ids), and `test_api_system` `test_ui_config_serves_theme_registry` (two → four; not named in the plan, but it pins AC 1's API half). **Pre-existing red, not this ticket:** `test_AppCss` AC5 and AST-2049 cases on `--tp-lvl` (dev `5f4850a20`), the same named exclusion as **AST-2128** (`components.md` § AST-2128). AC 7's "`test_AppCss` passes" holds with that exclusion, per the plan's Out-of-scope note. **Integration:** none; no scenario reads themes or `App.css`.

#### QA test manifest (AST-2129)

1. **Vitest:**

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts \
  ../../../tests/component/frontend/test_AppCss.test.tsx \
  ../../../tests/component/frontend/components/test_GradeMark.test.tsx \
  -t '^(?!.*(no hex or non-black rgba outside token blocks|AST-2049: no hex in \.ts/\.tsx source)).*$'
```

Expect 53 passed and 2 skipped. Without `-t`, exactly those 2 fail, and they name only `--tp-lvl`.

2. **Pytest (6):** `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst2047ThemeRegistry tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_serves_theme_registry`. Set `ASTRAL_PYTHON` if the worktree has no `.venv`.
3. **AC 2:** `git grep -c -e '--grade-a:' -- src/ui/frontend/src/App.css` → `2`.
4. **AC 7:** `cd src/ui/frontend && npx tsc -b --noEmit` exits 0; `python -c "import src.utils.config"` exits 0.

**Pass criterion:** items 1–4 hold.

### AST-2123 · AST-2100 (grade settings sets — Light Bright + ring, Dark as-is)

**Publish:** `origin/sub/AST-2100/AST-2123-grade-settings-sets`. `App.css` only: both token blocks declare the 47 grade settings (per grade: fill, `-ring`, `-ring-width`, `-ink`, `-letter-size`, `-letter-weight`, `-ring-width-lettered`; confidence: `-active`, `-inactive`, `-inactive-opacity`, `-size`, `-gap`). Light takes the Bright + ring values; Dark's ring widths are 0. `.dot-<g>` and `.grade-dot-letterless.dot-<g>` draw fill and inset ring from them; the confidence rules read gap, size and opacity from them. The `light_parchment` / `light_slate` blocks, §16 Theme Examples CSS and `--text-on-grade*` are deleted.

| Area | Component tests |
| --- | --- |
| Blocks equal the registry exactly (`dark`, `light`) | **`test_AppCss.test.tsx`** › **`Dark is :root and [data-theme=dark]; one block per registry id`** (revised: AST-2122's superset check tightened back to exact) |
| Every Light block declares exactly the Dark names (stylesheet header rule) | **`test_AppCss.test.tsx`** › **`every Light block declares exactly the Dark token names…`** (unchanged; covers the 47 new names in both blocks) |
| No hex outside token blocks; every `var(--x)` defined (new `var(--grade-*)` / `var(--confidence-bullet-*)` refs) | **`test_AppCss.test.tsx`** AC5 + AST-2049 cases (unchanged) |
| AC 1, 7, 8, 9, 10 (label counts, no confidence literals, no retired names, no `text-on-grade`) | grep lines in the manifest — structural, no new test |

**Not covered by component tests (jsdom has no cascade):** AC 2, 4, 5, 6, 7 (computed half) and 11 are computed-style checks. AC 3 is OKLab arithmetic on palette values. All go to browser / parent UAT, as the plan and Joan's validate note say.

**Broken / obsolete:** only the superset check above. No other test reads `.grade-dot`, `.dot-*`, `.confidence-bullet*` or `--text-on-grade*` from `App.css`. The other `App.css`-reading Vitests (`AdminDeployFooter`, `CandidateJobRowActions`, `JobTitleText`, `ListPage`, `Modal`, `ResumeContentEditor`, `AdminManageEmail`, `AdminPerformanceMonitor`) and the confidence-bullet markup tests (`ConfidenceBullets`, `recommendedJobReport`) are green. `test_config.py::TestAst2047ThemeRegistry::test_every_registry_id_has_an_app_css_block` stays green. No integration scenario reads `App.css`.

#### QA test manifest (AST-2123)

1. **Vitest (required):**

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts \
  ../../../tests/component/frontend/test_AppCss.test.tsx \
  ../../../tests/component/frontend/components/test_{AdminDeployFooter,CandidateJobRowActions,ConfidenceBullets,JobTitleText,ListPage,Modal,ResumeContentEditor}.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/pages/test_{AdminManageEmail,AdminPerformanceMonitor}.test.tsx
```

Expect 151 passed, 2 failed. The 2 known reds are the `test_AppCss` AC5 and AST-2049 cases. They may name **only** `--tp-lvl` (dev `5f4850a20`, §12b — see § AST-2122). Any other name is an AST-2123 defect.

2. **Pytest:** `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst2047ThemeRegistry` — 5 passed.

3. **AC 1 (each of 47 labels exactly twice):**

```bash
for g in a b c d f x; do for s in "" -ring -ring-width -ink -letter-size -letter-weight -ring-width-lettered; do
  echo "--grade-$g$s $(git grep -c -- "--grade-$g$s:" src/ui/frontend/src/App.css | cut -d: -f2)"; done; done
for s in active inactive inactive-opacity size gap; do
  echo "--confidence-bullet-$s $(git grep -c -- "--confidence-bullet-$s:" src/ui/frontend/src/App.css | cut -d: -f2)"; done
```

Every line ends in `2`.

4. **AC 7 / 8 / 9 / 10 greps (each returns nothing):**

```bash
git grep -n -A6 '^\.confidence-bullet' -- src/ui/frontend/src/App.css | grep -E '4px|3px|0\.55'
git grep -n -i -e theme_examples -e ThemeExamples -e theme-examples -e 'Theme Examples' -e theme_example_grade_sets -- src tests
git grep -n -e light_parchment -e light_slate -- src tests
git grep -n 'text-on-grade' -- src/ui/frontend/src src/utils
```

AC 8 / AC 9 have no `App.css` carve-out any more; that was only for AST-2122.

5. **Build:** `cd src/ui/frontend && npx tsc -b --noEmit && npm run build` exit 0.

**Pass criterion:** items 1–5 hold. Narrowed runs, not the zero-arg harness. AC 2–7 computed / 11 are UAT.

---

### AST-2122 · AST-2100 (App.css token tests rehomed)

**Publish:** `origin/sub/AST-2100/AST-2122-retire-theme-examples`. The Theme Examples page and its test file are retired (manifest: [`pages.md`](pages.md) § AST-2122). That file also held the `App.css` token-block tests, which guard the whole SPA rather than the page, so they moved here unchanged except for the retired ids.

| Case | Guards | Change in the move |
| --- | --- | --- |
| `Dark is :root and [data-theme=dark]; every registry id has a block` | Dark block selector; registry ⊆ blocks | was exact "one block per registry id". The unregistered alternate blocks stay in `App.css` until **AST-2123** deletes them, so AST-2123's qa pass restores exact equality |
| `every Light block declares exactly the Dark token names, and the Lights pairwise differ (AC4)` | token-name parity across blocks (AST-2047) | none |
| `[bug-repro] AST-2076: in light, the accent and nav group label resolve to the header colour` | AST-2076 | `light` only (parchment id retired) |
| `no hex or non-black rgba outside token blocks; every var(--x) is defined…` | AST-2047 AC5, `App.css` half | none |
| `AST-2049: no hex in .ts/.tsx source and every var(--x) in source is defined…` | AST-2049 AC9, epic-wide | none |

**Known red, not AST-2122:** the last two cases fail on `App.css: --tp-lvl` from dev commit `5f4850a20` (Task Performance page: `--tp-lvl` with `hsla()` values in `.tp-*` rule bodies). They failed the same way in the old file. Manifest: [`pages.md`](pages.md) § AST-2122.

---

### AST-1317 · AST-1309 (codify in-row labeled-button size)

**Parent:** [AST-1309 — Add a button style for in-row buttons](https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons). **Publish:** `origin/sub/AST-1309/AST-1317-codify-in-row-labeled-button-size`.

**Catalog + unused size CSS.** Live edits: `canon/patterns/ui/pattern.ui.shared-button-roles.md` (`status: approved`, `proposed_in: AST-1166`, `approved_by: Archie`, `approved_at: "2026-08-11"`, `canonical_refs` adds `.btn.in-row`, `related_statutes` adds `astral.standards.no-hardcoded-sets`); HARVEST Crosswalk notes cell only; `src/ui/frontend/src/App.css` section 14 `.btn.in-row` (`padding: 3px 20px; line-height: 1.2`) after `.btn.danger:disabled`, before section 15. No TSX call-site apply (sibling **AST-1318**). Does not restyle `.icon-control` or reopen AST-1166 roles. `canon/patterns/README.md` and `pattern.ui.icon-control.md` unchanged.

**No new component or integration tests.** §6c N/A (no page / filter UX). Existing **AST-1301** catalog-class tests and **AST-645** `.in-flight` wiring stay valid — this tip does not add `in-row` to any `className`. Integration scenarios do not assert button-class catalogs — no drift.

**`test-child`:** docs-acceptance (grep/read on publish tip) — no pytest / zero-arg harness / branch-lock gate.

1. **Pattern amend** — `pattern.ui.shared-button-roles.md`: `status: approved`, `approved_by: Archie`, `proposed_in: AST-1166`, `approved_at: "2026-08-11"`; `canonical_refs` includes `.btn.in-row` plus the four role selectors; `related_statutes` includes `astral.standards.no-hardcoded-sets`; Solution shape documents optional `in-row` (never a fifth role; pairings `btn primary in-row` / `btn secondary in-row` / `btn danger in-row` / `btn primary in-flight in-row`; ~60% height; keep 14px label).
2. **HARVEST notes** — existing `pattern.ui.shared-button-roles` Crosswalk notes cell is `approved — labeled \`btn\` roles + \`in-row\` size (AST-1317); CSS in \`App.css\``. No second Crosswalk row. README harvested-corpus row unchanged (same id).
3. **App.css contract** — `.btn.in-row` exists with `padding: 3px 20px` and `line-height: 1.2`; `.btn` still `padding: 8px 20px` and `font-size: 14px`; role / in-flight / `.icon-control` declarations unchanged.
4. **Scope gate** — `rg -n 'in-row' src/ui/frontend/src --glob '*.tsx'` is empty; no `Button.tsx`; `pattern.ui.icon-control.md` and `canon/patterns/README.md` unchanged vs `origin/dev`.

---

### AST-1300 · AST-1166 (codify button + icon-control patterns)

**Canon + unused shared CSS.** Live edits on **`origin/sub/AST-1166/AST-1300-codify-button-icon-control-patterns`**: `canon/patterns/ui/pattern.ui.shared-button-roles.md` + `canon/patterns/ui/pattern.ui.icon-control.md` (`status: approved`, `proposed_in: AST-1166`, `approved_by: Archie`); `canon/patterns/README.md` / `HARVEST.md` index rows; `src/ui/frontend/src/App.css` TOC **14–15** plus `.btn` / `.btn.primary` / `.btn.secondary` / `.btn.danger` / `.btn.primary.in-flight` / `.icon-control`. No TSX call-site remediations (siblings **AST-1301** / **AST-1302**). Leftover families (`modal-btn`, `dep-btn`, `job-list-icon-btn`, `list-page-bulk-btn`, …) stay until those siblings retire them.

**No new component or integration tests.** §6c N/A (no page / filter UX). Existing **AST-645** `.in-flight` wiring tests stay valid for leftover families — not in this manifest. Integration scenarios do not assert button-class catalogs — no drift.

**`test-child`:** docs-acceptance (grep/read on publish tip) — no pytest / zero-arg harness / branch-lock gate.

1. **Patterns approved** — both files `status: approved`, `approved_by: Archie`, `proposed_in: AST-1166`; `canonical_refs` point at `src/ui/frontend/src/App.css` symbols `.btn.primary` / `.btn.secondary` / `.btn.danger` / `.btn.primary.in-flight` and `.icon-control`.
2. **Catalog indexes** — README harvested-corpus rows list both ids as `approved`; HARVEST has supporting-package + Crosswalk `create (AST-1300)` rows (no define-parent AC cite-map rows).
3. **App.css contract** — TOC lines `14. Shared button roles` / `15. Icon control`; selectors above exist; `.btn.primary` uses `var(--cta-green)`; `.btn.primary.in-flight` uses `var(--accent-contrast)` (was `--accent-gold`; renamed by AST-2076); `.btn.danger` uses `var(--danger)` + `#fff`; leftover `.modal-btn` / `.dep-btn` / `.job-list-icon-btn` / `.list-page-bulk-btn` still present.
4. **Scope gate** — no TSX `className` uses catalog `btn primary|secondary|danger` or `icon-control`; no `Button.tsx` / `IconControl.tsx`.

---

### AST-649 · AST-648 (historical — SUNSET AST-757)

**Historical (AST-649):** Candidate **Board Searches** nav/route/page retired; **`gaze_board`** hidden from Admin Scheduled Actions APIs. Backend boards module and **`/api/boards`** removed **AST-765**; schema dropped **AST-766**. No active boards manifest. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.
