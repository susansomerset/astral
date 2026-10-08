# AST-2047 — Theme registry, palettes, and Theme Examples page (User Theme)

- **Parent:** [AST-2042](https://linear.app/astralcareermatch/issue/AST-2042) — User Theme
- **Ticket:** [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047)
- **Publish ref:** `origin/sub/AST-2042/AST-2047-theme-registry-palettes`
- **Canon Scope:** none (locked at Discussion). No directive applies to these files.

Astral has one look today: the dark purple token block in `App.css`. This ticket adds the pieces every other User Theme child builds on. It adds a server-side theme registry in `UI_CONFIG` (four palettes: `dark`, `light`, and two examples-only Light alternates) with `dark` as the default. It adds a profile **Theme** select whose options are generated from that registry, and a **Theme Examples** item under **Tools**. In `App.css`, the existing token block also matches the dark theme attribute, and three Light palette blocks redefine every token. Every color literal in `App.css` rules moves onto a token, and undefined `var(--x)` references are repointed. A new admin page renders the same sample UI once per registered palette, side by side. Saving and applying a candidate's theme is child #2's job (Save and apply the candidate's theme), and component inline styles belong to child #3 (Move component inline colors onto tokens). This plan does neither.

## Codebase facts the plan relies on (verified at branch tip `dff04eb4d`)

- [AST-2040](https://linear.app/astralcareermatch/issue/AST-2040) is on `origin/dev` (`b8f45f7a1`). `origin/ftr/AST-2042-user-theme` is not on origin yet. `sync-child.sh` skipped it and exited 0.
- `UI_CONFIG` starts at `src/utils/config.py:5662` and closes at `:5684`, after `"adhoc_import_picker_visible_rows": 5,`. `DATA_SHAPES` starts at `:5809`, after `UI_CONFIG`, so the profile field can read `UI_CONFIG` at import time.
- `GET /api/system/ui_config` (`src/ui/api/api_system.py:197`) returns `{**UI_CONFIG, ...}`, so new top-level keys are served with no API change. Python dicts keep insertion order, and JSON object order for non-numeric keys survives `jsonify` → `r.json()`. The page relies on that order.
- The profile `pronouns` select is at `config.py:5861–5868`, followed by `contact.reason_codes` at `:5869`.
- `NAV_CONFIG` **Tools** (`admin_only: True`) is at `config.py:5774–5784`. Its last item is `{"label": "Cover Letter Paste", "path": "/admin/session_cover_letter"},`. `/api/nav_config` already omits `admin_only` groups for non-admins.
- `routes.tsx:146` is the last admin route (`admin/manage_slack`). `AdminRoute` redirects non-admins to `/`.
- `uiConfig.ts` exposes `getUiConfig()` / `loadUiConfig(onReady)`. The established page pattern is `useEffect(() => { loadUiConfig(() => force(n => n + 1)) }, [])` (`JobTitleText.tsx:12`, `AdminScheduledActions.tsx:368`).
- The `App.css` token block is `:root { … }` at lines 36–61, with 22 custom properties. `--confidence-bullet-active` / `-inactive` are `var(--text-secondary)` / `var(--text-muted)`. A custom property's `var()` is resolved where it is **declared**, and descendants inherit the resolved value. So every theme block must redeclare these two aliases, or a Light panel inherits Dark bullet colors. AC 4's "same name set" rule already forces this.
- `:root` and `[data-theme="…"]` have the same specificity (0,1,0). The Light blocks must come **after** the Dark block so a root `data-theme="light"` wins.
- `App.css` rule bodies hold 21 hex literals outside the token block, plus 7 non-black `rgba()` tints. There are 5 undefined references (`--accent-green`, `--border-color`, `--muted`, `--surface-muted`, `--text-dim`) and no named color keywords. The full list is in the Stage 2 table.
- `.toast` sets `color: #fff` for every variant, including `.toast-info`, whose background is `--bg-elevated`. On a Light palette, that is white text on a light surface.
- `.btn.primary` / `.dispatch-status-running` / `-warn` use `color: var(--bg-deep)` on green/gold. On Light palettes `--bg-deep` is near-white, which stays readable on the darker Light greens/golds below.
- Shared sample markup: `FormFields.tsx` renders `.dep-field` > `.dep-field-label` + `.dep-input` / `.dep-input dep-select` / `label.dep-toggle` > `input[type=checkbox]` + `.dep-toggle-label`. Grade dots are `span.grade-dot.dot-<g>`. `ConfidenceBullets` (`components/ConfidenceBullets.tsx`) takes `{ confidence?: number }`. Nav links are `.nav-link`, `.nav-link.active`, and `span.nav-link.disabled`. Modal chrome is `.modal-card` > `.modal-header` > `h2.modal-title`, then `.modal-body` and `.modal-footer`. Toast is `.toast.toast-<variant>.toast-visible` (`position: fixed`). Buttons are `.btn.primary|secondary|danger`. The table is `.list-page-table-wrap` > `table.list-page-table`.
- `rg -n '"light"' src/ui/frontend/src` returns nothing at the tip. The `dark` / `light` / alternate ids must never appear as string literals in `.ts` / `.tsx` (AC 2).
- Interim behavior between this ticket and #2: `CandidateProfile.editValuesFromCandidate` has no `theme` key yet, so the new select renders with `value=""`. The browser shows the first option (Dark), and nothing is sent unless the user changes it. If they do, `update_candidate_data` merges `theme` into the blob unvalidated (valid ids only, since the select offers no others). #2 adds load and validation. This ticket does not touch `CandidateProfile.tsx` or `candidate.py`.

## Contract for siblings (reference only — no work here)

- **Root attribute:** `data-theme="<registry id>"`. #2 sets it on `document.documentElement` or removes it. No attribute means Dark (`:root`).
- **Served keys:** `UiConfig.themes: Record<string, { label: string; profile_selectable: boolean }>` and `UiConfig.default_theme: string`.
- **Tokens this ticket adds** that #3 can target (child #3 cannot edit `App.css`): `--success`, `--warning`, `--error`, `--accent-gold-dim`, `--text-on-color`, plus the existing `--text-*`, `--bg-*`, `--border*`, `--danger`, `--accent-gold`. After this ticket, `.tsx` files still reference `--accent`, `--bg-secondary`, `--border-color`, and `--color-pass`, which no block defines. Repointing those is #3's work (Boundaries: the `.ts`/`.tsx` half of the stray-color AC is #2/#3's).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `UI_CONFIG["themes"]` + `UI_CONFIG["default_theme"]` + assert; profile `theme` select generated from selectable entries; `NAV_CONFIG` Tools item `/admin/theme_examples` | utils |
| `src/ui/frontend/src/lib/uiConfig.ts` | `ThemeEntry` interface; `UiConfig.themes?` + `UiConfig.default_theme?` | ui (lib) |
| `src/ui/frontend/src/App.css` | Dark selector gains `[data-theme="dark"]`; 16 new semantic tokens; three Light blocks; literal/undefined-ref sweep; `.toast-info` text color; `.theme-examples-*` styles | ui (style) |
| `src/ui/frontend/src/pages/AdminThemeExamples.tsx` | **New** admin page: one labeled panel per registry id | ui (page) |
| `src/ui/frontend/src/routes.tsx` | `admin/theme_examples` in `AdminRoute` | ui (routes) |

**Scope gate:** every row above is named in this ticket's `## Scope`, and each change is the kind Scope describes. No other files. `CandidateProfile.tsx`, `CandidateContext.tsx`, `candidate.py`, and every component/page inline style stay untouched.

## Stage 0: Lint baseline (no commit)

**Done when:** `debug/spikes/ast-2047/lint-before.txt` holds the `npm run lint` output from the synced tree, before any edits.

1. In `src/ui/frontend`, run `mkdir -p ../../../debug/spikes/ast-2047 && npm run lint > ../../../debug/spikes/ast-2047/lint-before.txt 2>&1; true`. `debug/` is gitignored. Do not commit it.
2. Save the Dark token values for AC 3. From the repo root, run `git show HEAD:src/ui/frontend/src/App.css > debug/spikes/ast-2047/App.before.css`.

## Stage 1: Theme registry, profile select, nav item, `UiConfig` type

**Done when:** `python -c "import src.utils.config"` exits 0. `python -c "from src.utils.config import UI_CONFIG, DATA_SHAPES as D; print(list(UI_CONFIG['themes']), UI_CONFIG['default_theme'], [f['options'] for f in D['candidates']['detail']['profile'][0]['fields'] if f['key']=='theme'])"` prints the four ids, `dark`, and exactly the Dark/Light options. `npm run build` exits 0.

1. In `src/utils/config.py`, directly after the line `    "adhoc_import_picker_visible_rows": 5,` (inside `UI_CONFIG`, before its closing `}`), insert:

   ```python
       # AST-2042: theme registry — palette id -> label + whether the profile Theme select offers it.
       # Each id needs a matching [data-theme="<id>"] block in App.css; ids not profile_selectable
       # only appear on Tools -> Theme Examples. Adding/retiring a palette = one entry here + one CSS block.
       "themes": {
           "dark": {"label": "Dark", "profile_selectable": True},
           "light": {"label": "Light", "profile_selectable": True},
           "light_parchment": {"label": "Light (Parchment)", "profile_selectable": False},
           "light_slate": {"label": "Light (Slate)", "profile_selectable": False},
       },
       # Theme applied when a candidate has none stored (and before candidates load).
       "default_theme": "dark",
   ```

   ⚠️ **Decision:** Alternate ids are `light_parchment` (warm cream) and `light_slate` (cool gray-blue). They are snake_case like every other config key, and each label says what it looks like, so Susan can name her pick in the follow-up ticket.

2. Directly after the `}` line that closes `UI_CONFIG`, insert:

   ```python
   # Default must be a registered, profile-selectable palette (it is what candidates without a stored theme get).
   assert UI_CONFIG["themes"].get(UI_CONFIG["default_theme"], {}).get("profile_selectable"), (
       "UI_CONFIG default_theme must be a profile_selectable key of UI_CONFIG themes"
   )
   ```

3. In `DATA_SHAPES["candidates"]["detail"]["profile"]` → `Contact Information` → `fields`, directly after the `pronouns` select's closing `]},` and before `{"key": "contact.reason_codes", …}`, insert:

   ```python
                           # AST-2042: options come from the registry so there is no second theme list.
                           {"key": "theme", "label": "Theme", "type": "select", "options": [
                               {"value": tid, "label": t["label"]}
                               for tid, t in UI_CONFIG["themes"].items()
                               if t["profile_selectable"]
                           ]},
   ```

   ⚠️ **Decision:** No empty `(not set)` option. AC 2 requires exactly Dark and Light, and #2 makes a missing value read as the served default.

4. In `NAV_CONFIG` → the `"Tools"` group's `items`, directly after `{"label": "Cover Letter Paste", "path": "/admin/session_cover_letter"},`, insert:

   ```python
               {"label": "Theme Examples", "path": "/admin/theme_examples"},
   ```

5. In `src/ui/frontend/src/lib/uiConfig.ts`, directly after the `ColumnTypeConfig` interface line, insert:

   ```ts
   /** AST-2042: one theme registry entry served from UI_CONFIG.themes (keyed by palette id). */
   export interface ThemeEntry { label: string; profile_selectable: boolean }
   ```

   Then inside `UiConfig`, after `job_title_truncate_chars?: number`, insert:

   ```ts
     /** AST-2042: palette id -> entry; each id has a matching [data-theme] block in App.css. */
     themes?: Record<string, ThemeEntry>
     /** AST-2042: palette applied when the selected candidate has no stored theme. */
     default_theme?: string
   ```

6. Run `python -c "import src.utils.config"`, the Done-when print, and `npm run build` in `src/ui/frontend`. Commit: `code(AST-2047): theme registry, profile select, nav item`.

## Stage 2: Theme token blocks and `App.css` literal sweep

**Done when:** The four checks under step 6 pass. `npm run build` exits 0. With no `data-theme` set, the app renders exactly as before, apart from the four repointed-reference rules flagged ⚠️ below.

1. In `App.css` section 1, change the selector line `:root {` (line 36) to `:root, [data-theme="dark"] {`. Do **not** edit any of the 22 existing declarations. Directly above it, insert the comment:

   ```css
   /* Dark is the default palette (:root) and also [data-theme="dark"] so a Dark panel can sit inside a Light page.
      Each [data-theme] block must declare the SAME custom-property names as this one — aliases like
      --confidence-bullet-* included, since var() inside a custom property resolves where it is declared. */
   ```

2. In the same Dark block, directly after `  --confidence-bullet-inactive: var(--text-muted);`, add these 16 tokens. Each value is the exact literal it replaces, so Dark rendering is unchanged:

   ```css
     /* AST-2042: semantic tokens for former literals / undefined refs (values = the literals they replaced) */
     --nav-group-label: #f0d690;
     --accent-gold-dim: rgba(212, 168, 67, 0.15);
     --paper-bg: #ffffff;
     --text-on-grade: #1a1424;
     --text-on-grade-f: #e8e4f0;
     --text-on-color: #ffffff;
     --status-interrupted-bg: #7a5c1e;
     --status-interrupted-text: #f5d98b;
     --danger-tint: rgba(220, 53, 69, 0.1);
     --warning-tint: rgba(255, 193, 7, 0.07);
     --tint-subtle: rgba(255, 255, 255, 0.03);
     --tint-soft: rgba(255, 255, 255, 0.04);
     --tint-medium: rgba(255, 255, 255, 0.06);
     --success: #4caf50;
     --warning: #ff9800;
     --error: #f87171;
   ```

   The Dark block then holds 38 names (22 existing + 16 new). `--success`, `--warning`, `--error`, and `--accent-gold-dim` reuse the names and fallback values that `.tsx` files already reference. Those references become defined with no visual change, and #3 can keep or repoint them.

   ⚠️ **Decision:** Defining `--error` (soft red text, `#f87171`) is separate from `--danger` (button/fill red). The `.tsx` error lines use soft reds (`#f87171`, `#ff6b6b`), and #3 cannot add tokens, so it needs one to land on without darkening Dark's error text.

3. Directly after the Dark block's closing `}`, before `/* === 2. Base / Reset === */`, insert the three Light blocks. Each declares the same 38 names:

   ```css
   /* AST-2042: Light palettes. "light" is what the profile's Light applies; the other two are
      examples-only alternates shown on Tools -> Theme Examples (UI_CONFIG themes). */
   [data-theme="light"] {
     --bg-deep: #f5f3fa;
     --bg-card: #ffffff;
     --bg-elevated: #ece8f4;
     --border: #d6cfe6;
     --border-subtle: #e6e1ef;
     --text-primary: #1f1830;
     --text-secondary: #5a5070;
     --text-muted: #857b99;
     --accent-gold: #9a7314;
     --accent-gold-hover: #b0851c;
     --cta-green: #1e7e34;
     --cta-green-hover: #23913c;
     --danger: #c82333;
     --danger-hover: #a71d2a;
     --grade-a: #28a745;
     --grade-b: #e0a800;
     --grade-c: #e8690b;
     --grade-d: #c82333;
     --grade-f: #8b0000;
     --grade-x: #8b6fe0;
     --confidence-bullet-active: var(--text-secondary);
     --confidence-bullet-inactive: var(--text-muted);
     --nav-group-label: #7a5a10;
     --accent-gold-dim: rgba(154, 115, 20, 0.15);
     --paper-bg: #ffffff;
     --text-on-grade: #1f1830;
     --text-on-grade-f: #ffffff;
     --text-on-color: #ffffff;
     --status-interrupted-bg: #f3e3b5;
     --status-interrupted-text: #6b4e12;
     --danger-tint: rgba(200, 35, 51, 0.08);
     --warning-tint: rgba(224, 168, 0, 0.12);
     --tint-subtle: rgba(31, 24, 48, 0.03);
     --tint-soft: rgba(31, 24, 48, 0.04);
     --tint-medium: rgba(31, 24, 48, 0.06);
     --success: #2e7d32;
     --warning: #b26a00;
     --error: #c62828;
   }

   [data-theme="light_parchment"] {
     --bg-deep: #f6f0e4;
     --bg-card: #fffbf2;
     --bg-elevated: #efe6d4;
     --border: #dccfb4;
     --border-subtle: #e9dfca;
     --text-primary: #2b2116;
     --text-secondary: #6b5a43;
     --text-muted: #94826a;
     --accent-gold: #8a5a00;
     --accent-gold-hover: #a06c08;
     --cta-green: #2f7d32;
     --cta-green-hover: #388e3c;
     --danger: #b3261e;
     --danger-hover: #921f18;
     --grade-a: #2f8f3a;
     --grade-b: #d49b00;
     --grade-c: #d9650f;
     --grade-d: #b3261e;
     --grade-f: #7a0b0b;
     --grade-x: #7e63c9;
     --confidence-bullet-active: var(--text-secondary);
     --confidence-bullet-inactive: var(--text-muted);
     --nav-group-label: #7a4f00;
     --accent-gold-dim: rgba(138, 90, 0, 0.15);
     --paper-bg: #ffffff;
     --text-on-grade: #2b2116;
     --text-on-grade-f: #fffbf2;
     --text-on-color: #ffffff;
     --status-interrupted-bg: #ecd9a8;
     --status-interrupted-text: #5c3f06;
     --danger-tint: rgba(179, 38, 30, 0.08);
     --warning-tint: rgba(212, 155, 0, 0.12);
     --tint-subtle: rgba(43, 33, 22, 0.03);
     --tint-soft: rgba(43, 33, 22, 0.04);
     --tint-medium: rgba(43, 33, 22, 0.06);
     --success: #2e7d32;
     --warning: #a35a00;
     --error: #b3261e;
   }

   [data-theme="light_slate"] {
     --bg-deep: #eef1f6;
     --bg-card: #ffffff;
     --bg-elevated: #e3e8f0;
     --border: #c9d2df;
     --border-subtle: #dde3ec;
     --text-primary: #18202e;
     --text-secondary: #4a5568;
     --text-muted: #7a8699;
     --accent-gold: #2b6cb0;
     --accent-gold-hover: #3182ce;
     --cta-green: #2f855a;
     --cta-green-hover: #38a169;
     --danger: #c53030;
     --danger-hover: #9b2c2c;
     --grade-a: #38a169;
     --grade-b: #d69e2e;
     --grade-c: #dd6b20;
     --grade-d: #c53030;
     --grade-f: #822727;
     --grade-x: #805ad5;
     --confidence-bullet-active: var(--text-secondary);
     --confidence-bullet-inactive: var(--text-muted);
     --nav-group-label: #2c5282;
     --accent-gold-dim: rgba(43, 108, 176, 0.15);
     --paper-bg: #ffffff;
     --text-on-grade: #18202e;
     --text-on-grade-f: #ffffff;
     --text-on-color: #ffffff;
     --status-interrupted-bg: #fbe7b5;
     --status-interrupted-text: #744210;
     --danger-tint: rgba(197, 48, 48, 0.08);
     --warning-tint: rgba(214, 158, 46, 0.12);
     --tint-subtle: rgba(24, 32, 46, 0.03);
     --tint-soft: rgba(24, 32, 46, 0.04);
     --tint-medium: rgba(24, 32, 46, 0.06);
     --success: #2f855a;
     --warning: #b7791f;
     --error: #c53030;
   }
   ```

   ⚠️ **Decision — the three variations:** `light` (Lilac) keeps Astral's purple cast on white cards with a deep gold accent. `light_parchment` is warm cream and sepia with an amber accent. `light_slate` is cool gray-blue, and its `--accent-gold` is a **blue** (`#2b6cb0`), so Susan sees one Light that drops gold entirely. The token keeps its name. Renaming it would touch every rule that uses gold, which is out of scope. Every pair differs on `--bg-deep` (AC 4). The Light white tints become dark tints, because a white overlay is invisible on a light surface. `--paper-bg` stays white in every palette because the resume preview iframe shows paper (generated resume HTML is out of epic scope).

4. Literal and undefined-reference sweep. Edit exactly these rule values (line numbers are at tip `dff04eb4d`, **before** steps 1–3 shift them down; find each by selector):

   | Line | Selector | Old value | New value |
   |------|----------|-----------|-----------|
   | 337 | `.nav-group-label` | `color: #f0d690;` | `color: var(--nav-group-label);` |
   | 545 | `.list-page-search:focus` | `box-shadow: 0 0 0 2px rgba(212, 168, 67, 0.15);` | `box-shadow: 0 0 0 2px var(--accent-gold-dim);` |
   | 918 | `.materials-preview-iframe` | `border: 1px solid var(--border-subtle, #ddd);` | `border: 1px solid var(--border-subtle);` |
   | 920 | `.materials-preview-iframe` | `background: #fff;` | `background: var(--paper-bg);` |
   | 1149 | `.grade-dot` | `color: #1a1424;` | `color: var(--text-on-grade);` |
   | 1157 | `.dot-f` | `color: #e8e4f0;` | `color: var(--text-on-grade-f);` |
   | 1422 | `.agent-model-costs` | `color: var(--text-muted, #999);` | `color: var(--text-muted);` |
   | 1425 | `.agent-model-costs` | `background: rgba(255,255,255,0.04);` | `background: var(--tint-soft);` |
   | 1495 | `.dep-input:focus` | `box-shadow: 0 0 0 2px rgba(212, 168, 67, 0.15);` | `box-shadow: 0 0 0 2px var(--accent-gold-dim);` |
   | 1861 | `.experience-jobs-editor-role-label` | `color: var(--text-muted, #999);` | `color: var(--text-muted);` |
   | 1870 | `.experience-jobs-editor-unsupported` | `color: var(--danger, #c44);` | `color: var(--danger);` |
   | 1968 | `.toast` | `color: #fff;` | `color: var(--text-on-color);` |
   | 1989 | `.toast-info` | `{ background: var(--bg-elevated); border: 1px solid var(--border); }` | `{ background: var(--bg-elevated); border: 1px solid var(--border); color: var(--text-primary); }` |
   | 2094 | `.dispatch-status-ok` | `color: #fff;` | `color: var(--text-on-color);` |
   | 2095 | `.dispatch-status-fail` | `color: #fff;` | `color: var(--text-on-color);` |
   | 2097 | `.dispatch-status-interrupted` | `background: #7a5c1e; color: #f5d98b;` | `background: var(--status-interrupted-bg); color: var(--status-interrupted-text);` |
   | 2099 | `.dispatch-status-muted` | `color: var(--text-dim);` | `color: var(--text-muted);` |
   | 2148 | `.dispatch-log-error` | `background: rgba(220, 53, 69, 0.1);` | `background: var(--danger-tint);` |
   | 2149 | `.dispatch-log-warn` | `background: rgba(255, 193, 7, 0.07);` | `background: var(--warning-tint);` |
   | 2245 | `.batch-feedback-hydrated-table th, td` | `border: 1px solid var(--border-color, #ccc);` | `border: 1px solid var(--border);` |
   | 2252 | `.batch-feedback-hydrated-table th` | `background: var(--surface-muted, #f5f5f5);` | `background: var(--bg-elevated);` |
   | 2339 | `.manage-email-outcome--skip` | `color: var(--text-muted, var(--text-secondary, #888));` | `color: var(--text-muted);` |
   | 2432 | `.entity-story-perf` | `color: var(--accent-green, #4caf50);` | `color: var(--success);` |
   | 2441 | `.entity-story-content` | `background: var(--bg-deep, #0d0d1a);` | `background: var(--bg-deep);` |
   | 2485 | (intake transcript, `border-top`) | `border-top: 1px solid var(--border, #333);` | `border-top: 1px solid var(--border);` |
   | 2501 | `.intake-msg--user` | `background: rgba(255, 255, 255, 0.06);` | `background: var(--tint-medium);` |
   | 2506 | `.intake-msg--assistant` | `background: rgba(255, 255, 255, 0.03);` | `background: var(--tint-subtle);` |
   | 2535 | `.intake-hold` | `color: var(--muted, #888);` | `color: var(--text-muted);` |
   | 2642 | `.btn.danger` | `color: #fff;` | `color: var(--text-on-color);` |

   Leave every `rgba(0, 0, 0, …)` / `rgba(0,0,0,…)` shadow and overlay unchanged (Scope: neutral shadows/overlays stay).

   ⚠️ **Decision — rules whose Dark look changes slightly** (they referenced undefined properties, so the browser used the fallback or inherited color; Scope requires repointing them):
   - `.dispatch-status-muted` used `--text-dim` (undefined, no fallback), so it inherited its color. It is now `--text-muted`.
   - `.batch-feedback-hydrated-table` borders were `#ccc` and header cells `#f5f5f5` (a light-gray header on the dark theme). They are now `--border` / `--bg-elevated`, which matches the rest of the dark tables.
   - `.intake-hold` was `#888` and is now `--text-muted` (`#6b6280`).
   - `.entity-story-perf` already rendered `#4caf50`, which `--success` equals, so there is no change.

   ⚠️ **Decision — `.toast-info` text:** `.toast` text moves to `--text-on-color` (white in every palette, for green/red toasts). `.toast-info` gains `color: var(--text-primary)` because its surface is `--bg-elevated`, and white on a Light surface is unreadable. On Dark, info-toast text goes from `#fff` to `#e8e4f0`.

5. Run `npm run build` in `src/ui/frontend`.

6. From the repo root, run these checks. Each must print `OK`:

   ```bash
   # AC 4 + Dark AC 3: every theme block has the Dark name set; Dark's original 22 values unchanged; Lights pairwise differ.
   python3 - <<'EOF'
   import re
   css = open("src/ui/frontend/src/App.css").read()
   old = open("debug/spikes/ast-2047/App.before.css").read()
   blk = lambda src, sel: dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", src.split(sel, 1)[1].split("}", 1)[0]))
   dark = blk(css, ':root, [data-theme="dark"] {')
   before = blk(old, ":root {")
   assert all(dark[k] == v for k, v in before.items()), "Dark token value changed"
   lights = {t: blk(css, f'[data-theme="{t}"] {{') for t in ("light", "light_parchment", "light_slate")}
   for t, b in lights.items():
       assert set(b) == set(dark), (t, set(dark) ^ set(b))
   ids = list(lights)
   for i in range(3):
       for j in range(i + 1, 3):
           a, b = lights[ids[i]], lights[ids[j]]
           assert any(a[k] != b[k] for k in ("--bg-deep", "--bg-card", "--accent-gold")), (ids[i], ids[j])
   print("OK")
   EOF

   # AC 5 (App.css half): no hex or non-black rgba outside token blocks; every var(--x) in App.css is defined.
   python3 - <<'EOF'
   import re
   css = open("src/ui/frontend/src/App.css").read()
   body = re.sub(r'(:root, \[data-theme="dark"\]|\[data-theme="[\w]+"\]) \{[^}]*\}', "", css)
   body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
   assert not re.findall(r"#[0-9a-fA-F]{3,8}\b", body), re.findall(r"#[0-9a-fA-F]{3,8}\b", body)
   assert not re.findall(r"rgba?\((?!\s*0\s*,\s*0\s*,\s*0\s*,)", body), "non-black rgba outside token blocks"
   defined = set(re.findall(r"(--[\w-]+)\s*:", css))
   missing = set(re.findall(r"var\((--[\w-]+)", css)) - defined
   assert not missing, missing
   print("OK")
   EOF
   ```

   Run both again after Stage 3. The Stage 3 `.theme-examples-*` rules must also pass.

7. Commit: `code(AST-2047): dark/light token blocks and App.css literal sweep`.

## Stage 3: Theme Examples page and route

**Done when:** `npm run build` exits 0. As admin, Tools → Theme Examples opens `/admin/theme_examples` with four labeled panels (Dark, Light, Light (Parchment), Light (Slate)), each with the sample listed below and a different background. A non-admin sees no Tools group and is redirected from the URL. The Stage 2 checks still print `OK`. `rg -n '"light"' src/ui/frontend/src --glob '*.{ts,tsx}'` returns nothing.

1. Create `src/ui/frontend/src/pages/AdminThemeExamples.tsx` with exactly:

   ```tsx
   import { useEffect, useState } from "react"
   import { ConfidenceBullets } from "../components/ConfidenceBullets"
   import { getUiConfig, loadUiConfig } from "../lib/uiConfig"

   // AST-2042: fixed sample, rendered once per registered palette. Built from the real shared
   // classes (not look-alikes) so a token change shows here exactly as it does in the app.
   const GRADES = ["A", "B", "C", "D", "F", "X"]
   const SAMPLE_ROWS = [
     { company: "Acme Robotics", title: "Staff Engineer", grade: "A" },
     { company: "Globex", title: "Engineering Manager", grade: "C" },
   ]

   export default function AdminThemeExamples() {
     const [, forceUpdate] = useState(0)
     useEffect(() => { loadUiConfig(() => forceUpdate(n => n + 1)) }, [])
     const themes = getUiConfig()?.themes

     if (!themes) return <p className="theme-examples-status">Loading...</p>

     return (
       <div className="theme-examples">
         <h1 className="dep-title">Theme Examples</h1>
         <div className="theme-examples-grid">
           {/* Registry order; each panel's data-theme scopes that palette's tokens to the panel. Read-only: no API writes. */}
           {Object.entries(themes).map(([id, theme]) => (
             <section key={id} className="theme-examples-panel" data-theme={id}>
               <h2 className="theme-examples-label">{theme.label}</h2>

               <div className="theme-examples-row">
                 <span className="nav-link active">Ready</span>
                 <span className="nav-link">Review</span>
                 <span className="nav-link disabled">Applied</span>
               </div>

               <div className="theme-examples-row">
                 <button type="button" className="btn primary">Save</button>
                 <button type="button" className="btn primary in-flight">Generating</button>
                 <button type="button" className="btn secondary">Cancel</button>
                 <button type="button" className="btn danger">Delete</button>
               </div>

               <div className="list-page-table-wrap">
                 <table className="list-page-table">
                   <thead>
                     <tr><th>Company</th><th>Title</th><th>Grade</th></tr>
                   </thead>
                   <tbody>
                     {SAMPLE_ROWS.map(r => (
                       <tr key={r.company}>
                         <td>{r.company}</td>
                         <td>{r.title}</td>
                         <td><span className={`grade-dot dot-${r.grade.toLowerCase()}`}>{r.grade}</span></td>
                       </tr>
                     ))}
                   </tbody>
                 </table>
               </div>

               <div className="dep-field">
                 <label className="dep-field-label">Full Name</label>
                 <input className="dep-input" readOnly value="Ada Lovelace" />
               </div>
               <div className="dep-field">
                 <label className="dep-field-label">Timezone</label>
                 <select className="dep-input dep-select" defaultValue="pacific">
                   <option value="eastern">Eastern</option>
                   <option value="pacific">Pacific</option>
                 </select>
               </div>
               <div className="dep-field">
                 <label className="dep-toggle">
                   <input type="checkbox" defaultChecked />
                   <span className="dep-toggle-label">Enabled</span>
                 </label>
               </div>

               <div className="theme-examples-row">
                 {GRADES.map(g => (
                   <span key={g} className="theme-examples-grade">
                     <span className={`grade-dot dot-${g.toLowerCase()}`}>{g}</span>
                     <ConfidenceBullets confidence={3} />
                   </span>
                 ))}
               </div>

               <div className="toast toast-success toast-visible">Profile saved</div>
               <div className="toast toast-error toast-visible">Save failed</div>
               <div className="toast toast-info toast-visible">Copied to clipboard</div>

               <div className="modal-card">
                 <div className="modal-header"><h2 className="modal-title">Confirm</h2></div>
                 <div className="modal-body">Discard unsaved changes?</div>
                 <div className="modal-footer">
                   <button type="button" className="btn secondary">Keep editing</button>
                   <button type="button" className="btn danger">Discard</button>
                 </div>
               </div>
             </section>
           ))}
         </div>
       </div>
     )
   }
   ```

   ⚠️ **Decision:** Inputs are uncontrolled or `readOnly` and buttons have no handlers. The page performs no fetch except `ui_config`, so it cannot change `candidate_data.theme` (AC 6). Theme ids are never written as literals. They come from `Object.entries(themes)` (AC 2).

2. In `routes.tsx`, after `import AdminManageSlack from "./pages/AdminManageSlack"`, add `import AdminThemeExamples from "./pages/AdminThemeExamples"`. After the line `{ path: "admin/manage_slack", element: <AdminRoute><AdminManageSlack /></AdminRoute> },`, add:

   ```tsx
             { path: "admin/theme_examples", element: <AdminRoute><AdminThemeExamples /></AdminRoute> },
   ```

3. In `App.css`, update the table of contents: after ` * 15. Icon control` add ` * 16. Theme Examples (AST-2042)`. At the end of the file, append:

   ```css
   /* === 16. Theme Examples (AST-2042) === */

   .theme-examples {
     padding: 20px;
   }

   .theme-examples-status {
     padding: 20px;
     color: var(--text-primary);
   }

   .theme-examples-grid {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
     gap: 16px;
   }

   /* Each panel carries data-theme, so its own background/text come from that palette's tokens. */
   .theme-examples-panel {
     display: flex;
     flex-direction: column;
     gap: 14px;
     padding: 16px;
     background: var(--bg-deep);
     color: var(--text-primary);
     border: 1px solid var(--border);
     border-radius: 10px;
   }

   .theme-examples-label {
     margin: 0;
     font-size: 16px;
     color: var(--accent-gold);
   }

   .theme-examples-row {
     display: flex;
     flex-wrap: wrap;
     align-items: center;
     gap: 8px;
   }

   .theme-examples-grade {
     display: inline-flex;
     flex-direction: column;
     align-items: center;
     gap: 3px;
   }

   /* Toast and modal card are fixed/overlay chrome in the app; pin them into the panel flow here. */
   .theme-examples-panel .toast {
     position: static;
   }

   .theme-examples-panel .modal-card {
     width: auto;
     max-width: none;
     max-height: none;
   }
   ```

4. Run `npm run build`, then `npm run lint > ../../../debug/spikes/ast-2047/lint-after.txt 2>&1; true`. Compare the problem lines with `lint-before.txt`. Any problem in `lint-after.txt` that is absent from `lint-before.txt` must be fixed in the file this plan touched. If the fix needs a change this plan does not list, stop and comment (execution contract). Re-run the two Stage 2 step 6 checks and the `"light"` grep from Done-when.

5. Commit: `code(AST-2047): admin Theme Examples page and route`.

## Acceptance criteria map

| AC | Satisfied by | Verified by |
|----|--------------|-------------|
| 1 Registry served | Stage 1 steps 1–2 | Stage 1 Done-when print; `GET /api/system/ui_config` |
| 2 One list of themes | Stage 1 step 3 (comprehension), Stage 3 step 1 (no id literals) | Done-when print; `"light"` grep |
| 3 Dark unchanged | Stage 2 steps 1–2 (no existing declaration edited) | Stage 2 step 6 check 1 (`before` values) |
| 4 Light coverage + distinct | Stage 2 step 3 | Stage 2 step 6 check 1 |
| 5 No stray colors (App.css half) | Stage 2 step 4 | Stage 2 step 6 check 2 |
| 6 Theme Examples page | Stage 1 step 4, Stage 3 | Manual as admin / non-admin |
| 7 Builds clean; no new lint | Every stage | `npm run build`; Stage 3 step 4 lint diff |

## Execution contract

Execute steps in order. Do not add files, tokens, or rules not listed here. If a step's anchor line is missing, a selector in the Stage 2 table no longer holds the listed old value, or a check fails after following the steps literally, stop. Comment on [AST-2042](https://linear.app/astralcareermatch/issue/AST-2042) in the `🛑 Stage N blocked:` format and wait.

## Estimate

Confirm Chuckles estimate: 5 — agree
