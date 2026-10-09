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

## Joan validate

[plan-rubric]
**Ticket:** AST-2047
**Overall:** APPROVED
**Corpus:** cc0ca67ac7e3ffd6f9067ccd857cb47fdb2c6f50 (`canon/` at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `fe9850b9784a5700e7e29cdd586579941be3309e` (`origin/sub/AST-2042/AST-2047-theme-registry-palettes`)

## Canon scores

Frozen list empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not §4a ESCALATE (parent and child both explicitly declare empty scope with the same rationale as AST-1983).

## Traceability

Child AC1→Stage 1; AC2→Stage 1+3; AC3→Stage 2; AC4→Stage 2; AC5→Stage 2 (App.css half per Boundaries); AC6→Stage 1+3; AC7→Stages 0–3. Parent AC3–AC6 → N/A (child #2); parent AC1–2,7–11 → covered by the same child AC mapping.

## Findings

### fix-now

(none)

### discuss

- **acceptable — Intentional Dark tweaks on formerly undefined `var()`** (Stage 2 step 4 ⚠️ decisions: `.dispatch-status-muted`, batch-feedback table borders, `.intake-hold`). Plan documents them; aligns with parent Functional scope 5 and child Boundaries (App.css half only). Not a definition slip.

- **acceptable — No `## Self-assessment` block** — Estimate confirm present (`5 — agree`); footprint is heavily anchored; no `!!-NONE` conf gap.

- **acceptable — AC3 verification path** — Ticket AC3 cites `getComputedStyle` vs `origin/dev`; plan uses `App.before.css` + token-block equality script (Stage 0–2). Equivalent for declared token values at plan stage; manual UAT can still use parent wording.

### acceptable

- **Identity gates:** AST-2047 `Plan Ready`, assignee Joan Clarke; parent AST-2042 definition read; 0/2 `[plan-discuss]` rounds.
- **Scope fidelity:** Files Changed matches ticket `## Scope` and parent partition for child #1; explicit exclusions for #2/#3 (`candidate.py`, `CandidateProfile`, `CandidateContext`, component inline styles).
- **DRY / registry:** Single `UI_CONFIG["themes"]` drives profile select and Theme Examples panels; assert on `default_theme`; no second theme list in TS.
- **Sibling contract:** Root `data-theme`, served keys, and interim unvalidated merge behavior documented without implementing #2.

context_tokens≈32000

**Upshot:** `[plan-rubric] PROCEED (Commit: fe9850b97) Registry, palettes, examples`

## Review

- **Branch:** `origin/sub/AST-2042/AST-2047-theme-registry-palettes`
- **Build commits:** `18f58fc6b` (Stage 1: `UI_CONFIG` themes + default + assert, profile Theme select, Tools nav item, `UiConfig` types), `d3ebaa141` (Stage 2: Dark selector + 16 semantic tokens, three Light blocks, 29-row `App.css` sweep), `147e17c43` (Stage 3: `AdminThemeExamples.tsx`, `admin/theme_examples` route, `.theme-examples-*` styles)
- **Build notes:** `python3 -c "import src.utils.config"` exits 0. The registry prints `['dark', 'light', 'light_parchment', 'light_slate']` with default `dark`, and the profile Theme options are exactly Dark and Light. `npx tsc -b --noEmit` and `npm run build` exit 0. Both Stage 2 step 6 checks print `OK` after Stage 3: the Dark values match `App.before.css`, the Light name sets equal Dark's 38, the Lights differ pairwise, there is no hex or non-black `rgba` outside token blocks, and there are no undefined `var()` in `App.css`. `rg '"light"'` over `.ts`/`.tsx` returns nothing. `npm run lint` before/after: 31 problems both, the line:col-stripped diff is empty, and none are in touched files.
- **Deviation:** none in product code. The plan's CSS/TSX blocks and the 29-row table were applied by script straight from this doc. Environment only: the epic worktree had no `node_modules`, so `npm ci` ran from the lockfile before the Stage 0 baseline (no tracked changes). `python` is not on PATH, so `python3` was used for the Done-when commands.
- **For QA:** AC 6 needs a browser: four panels with pairwise-different computed backgrounds, non-admin redirect, Tools item hidden for non-admins, and no `candidate_data.theme` change. No manual smoke run was done in this headless build. `.tsx` files still reference `--accent`, `--bg-secondary`, `--border-color`, and `--color-pass` (child #3's half of the stray-color AC, per Boundaries).

## Radia review

[code-rubric]
**Ticket:** AST-2047
**Publish ref:** `55a3fcd697b19b85ec7b2a0d0db0c1f1f472e309` (`origin/sub/AST-2042/AST-2047-theme-registry-palettes`)
**Corpus:** `cc0ca67ac7e3ffd6f9067ccd857cb47fdb2c6f50` (canon tree at publish tip; frozen **Citations** / **Canon Scope** both **none** — same as Joan)
**Overall:** CLEAN

## Canon scores

Frozen list empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not §5.3 ESCALATE (explicit empty scope, same pattern as AST-1983 / Joan §4a).

## Column diff vs plan stage

(aligned) — Joan recorded empty list with no rows; code review confirms no applicable directives on the diff.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sibling test carry:** `merge-tests(AST-2047)` includes non–AST-2047 manifest deltas: `tests/component/core/test_agent.py` (AST-2053 letter-conf-0 normalisation + CRX2 decode expectation), `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (AST-2051/2056 autosave clock harness), `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` — expected `origin/tests` merge; not product scope for #2047.
- **AC6 / AC3 verification gap (documented, not a defect):** Component tests cover registry panels, sample markup, GET-only behavior, and `App.css` token-block contract (`test_AdminThemeExamples.test.tsx`, `TestAst2047ThemeRegistry`, `test_ui_config_serves_theme_registry`). Bible § AST-2047 already lists jsdom gaps: pairwise **computed** panel backgrounds, non-admin route redirect (generic `AdminRoute`), Tools hidden for non-admins (generic `admin_only` / `test_nav_config_omits_admin_group_for_non_admin`). AC3 “unchanged Dark” was validated at build via `App.before.css` / token equality scripts (build notes), not a durable runtime pin — aligns with Joan’s plan-stage **acceptable** on AC3 wording.
- **Interim #2 behavior (plan contract):** Profile `theme` select can merge an unvalidated id if the user changes it before child #2; plan documents this; no `candidate.py` / `CandidateProfile` / `CandidateContext` in the `src/**` diff — boundaries hold.
- **Residual #3 tokens:** `.tsx` still references `--accent`, `--bg-secondary`, `--border-color`, `--color-pass` per plan **Contract for siblings**; out of this ticket’s Boundaries.

## What's solid

- **Product footprint matches plan gate:** Only `src/utils/config.py`, `uiConfig.ts`, `App.css`, `AdminThemeExamples.tsx`, `routes.tsx` changed under `src/**` — no smuggled sibling product files.
- **Single source of truth:** `UI_CONFIG["themes"]` + `default_theme` with import-time assert; profile Theme options generated from `profile_selectable` entries; Tools item appended under existing admin-only Tools group; `ui_config` spread serves registry keys (component test asserts set + shape).
- **Palette work:** Dark block is `:root, [data-theme="dark"]`; three Light blocks with full token name parity and pairwise distinction on `--bg-deep` / `--bg-card` / `--accent-gold` enforced in tests; literal sweep and `var(--*)` definition checks in vitest + build notes.
- **Theme Examples page:** Registry-driven panels with `data-theme` scoping, shared-class sample, read-only API pattern in test.

## Recommended actions (for Chuckles / resolve-child / UAT — not Radia)

- Post this artifact + slim upshot; move to **Review Posted**; route **PROCEED** → **User Testing** per datt §3h after resolve-child ticks any frame rows (none proposed).
- **Susan UAT:** AC6 panel background pairwise difference in a real browser; quick admin vs non-admin Tools + `/admin/theme_examples` smoke (tests delegate to generic admin/nav coverage).

context_tokens≈42000

---

`[code-rubric] PROCEED (Commit: 55a3fcd69) Theme registry, palettes, examples`

## Bug: AST-2063 — Light themes: header text is dark yellow — use the Dark theme's background purple

### As-is

In the Light palettes (`light`, `light_parchment`, `light_slate`), heading text colored by `var(--accent-gold)` renders in that palette's dark gold or amber (`#9a7314` / `#8a5a00`), or blue on Slate (`#2b6cb0`). That covers page titles, modal titles, profile section labels, and the Theme Examples panel labels.

### To-be

In all three Light palettes, that heading text renders in the Dark theme's background purple, `#241b33` (Dark `--bg-elevated`; Susan confirmed the `--bg-card` / `--bg-elevated` family). Dark headings stay gold (`#d4a843`). Every other `--accent-gold` use (active nav link, active tabs, links, hovers, focus rings, statuses, cost totals, in-flight buttons) is unchanged in every palette.

### Repro

1. Apply a Light theme. Either select a candidate whose stored `theme` is `light`, or open Tools → Theme Examples (`/admin/theme_examples`) and look at the Light, Light (Parchment), and Light (Slate) panels.
2. The page title (`h1.list-page-title` / `h1.dep-title`), `h2.modal-title` in the sample modal card, and the panel label `h2.theme-examples-label` are gold or amber (blue on Slate), not purple.

### Root cause

AST-2047 never gave headings their own color role. They read `--accent-gold` directly, the same token that drives links, active tabs, and focus rings. A Light palette therefore cannot recolor headings without recoloring every accent.

### Proposed change

One file, `src/ui/frontend/src/App.css`, named in AST-2042's Component scope. The change adds one semantic token where a heading needs its own role (Technical scope: "new semantic tokens are added only where … needs one"). Line numbers are at `ftr/AST-2042-user-theme` tip `2fd5c63e7`. Find each line by selector.

1. **New token `--heading` in all four token blocks**, inserted directly after the block's `--accent-gold-hover: …;` line:
   - `:root, [data-theme="dark"]`: `  --heading: var(--accent-gold);`
   - `[data-theme="light"]`: `  --heading: #241b33;`
   - `[data-theme="light_parchment"]`: `  --heading: #241b33;`
   - `[data-theme="light_slate"]`: `  --heading: #241b33;`

   ⚠️ **Decision — Dark is an alias, not a hex copy:** `var(--accent-gold)` resolves to `#d4a843`, so Dark headings are pixel-identical, and they keep tracking gold if Dark's accent is ever retuned. The pattern matches `--confidence-bullet-*`, and like those, every block redeclares the name (AST-2047 AC 4 name-set equality).

   ⚠️ **Decision — one purple, `#241b33`, for all three Lights:** It is the more visibly purple of the two confirmed values (`#1a1424` reads as near-black on white). Using it in every Light block makes headings look the same across palettes, matching Susan's single-color ask. Its contrast is at least 13:1 on every Light `--bg-deep` / `--bg-card` / `--bg-elevated` (lowest: 13.2:1 on Parchment `--bg-elevated` `#efe6d4`).

   ⚠️ **Decision — insert position:** Insert after `--accent-gold-hover`, its semantic neighbor. That keeps four unchanged lines between this insert and the `--grade-*` lines that sibling bug AST-2064 edits in the same Light blocks, so the two merges do not touch adjacent lines.

2. **Repoint the six heading rules** from `color: var(--accent-gold);` to `color: var(--heading);`. Change only that one declaration in each rule:

   | Line | Selector | Rendered as |
   |------|----------|-------------|
   | 659 | `.list-page-title` | `h1` page titles on list pages (12 uses) |
   | 888 | `.job-analysis-upshot-heading` | heading class (no current markup; repointed so it stays a heading if reused) |
   | 1223 | `.modal-title` | `h2` in `Modal`, `UserPrompt`, `CandidateIntake`; `span` titles in `AdminScheduledActions` |
   | 1534 | `.dep-title` | `h1` page titles on detail/edit pages (7 uses) |
   | 1595 | `.dep-section-label` | `h2` section headers (DetailsEditPage) |
   | 2862 | `.theme-examples-label` | `h2` panel labels on Theme Examples |

   Do **not** change any other `var(--accent-gold)` / `var(--accent-gold-hover)` use. This includes `.nav-link.active`, `.tabbed-ta-tab.active`, `.side-tab-item.active .side-tab-label`, `.expand-toggle`, link hovers, `.analysis-rubric-link`, focus borders, `.dispatch-*`, `.perf-total-cost`, `.batch-cost-total`, and `.btn.primary.in-flight`. These are accents or interactive states, not headings.

   ⚠️ **Decision — `.nav-group-label` is untouched:** sidebar group labels already have their own token (`--nav-group-label`), and Susan's report is about header text in page content.

3. **Verify:**
   - In `src/ui/frontend`: `npx tsc -b --noEmit` and `npm run build` exit 0, and `npm run lint` shows no problem absent before the change.
   - Re-run AST-2047 Stage 2 step 6 checks 1 and 2 after `git show origin/dev:src/ui/frontend/src/App.css > debug/spikes/ast-2047/App.before.css`. Both must print `OK`.
   - Run `npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx` (4 passed).
   - `rg -n "color: var\(--heading\)" src/ui/frontend/src/App.css` returns exactly the six selectors above.
   - `rg -c -- "--heading:" src/ui/frontend/src/App.css` returns `4`.

### Blast radius

- Only `App.css` changes. No `.tsx`, config, or API change.
- Under Light, every page title, modal title (including the span-based Scheduled Actions modal titles), DetailsEditPage section label, and Theme Examples panel label turns purple. Under Dark nothing changes visually.
- Sibling AST-2064 (Light grade colors) edits the `--grade-*` / `--text-on-grade*` values in the same three Light blocks. This change only inserts a line four lines above those, so the two do not overlap. Both bugs append a `## Bug:` block to the end of this plan doc, so `merge-child` may see an adjacent-append conflict here. Resolve it by keeping both blocks.
- Tests: `test_AdminThemeExamples.test.tsx` passes unchanged. `--heading` is declared in all four blocks (name-set equality holds), its only reference is defined (no undefined `var`), and no hex is added outside `[data-theme]` blocks. No test asserts a heading's color.

### What must still hold

- AST-2047 AC 3: none of Dark's existing 38 values changes. The added `--heading` resolves to the same `#d4a843` headings used before.
- AST-2047 AC 4: each Light block declares exactly Dark's token names (now 39), and the Lights still differ pairwise on `--bg-deep`.
- AST-2047 AC 5 / AST-2049 AC 9: no hex or non-black `rgba()` in `App.css` outside `[data-theme]` blocks, and every `var(--x)` is defined in a token block.
- Every non-heading `--accent-gold` use renders exactly as before in every palette.

### AST-2063 fix-board (F2)

- **Betty — TESTS: OK.** App.css-only change; no existing test reads the six repointed heading rules or `--accent-gold` values. AST-2047 App.css contract tests already cover `--heading` declared in all four theme blocks, every `var()` resolving, and no hex outside theme blocks. Light-heading purple is a UAT visual check. Note: `test_AdminThemeExamples.test.tsx` has 5 tests (not 4) since the AST-2049 guard.
- **Joan — CANON: OK.** Parent Canon Scope is none. No in-force statute governs theme token names, heading vs accent roles, or palette hex sets. `astral.ui.frontend-file-placement` satisfied (styles stay in App.css). Draft UI patterns (`patt.ui.shared-button-roles`, in-flight gold) are not in force and not amended.

### AST-2063 Radia review-fix — round 1

[code-rubric]
**Ticket:** AST-2063
**Publish ref:** `85582d39cbc7c61e8fed3cb6165ce25466ba0a93` (`origin/sub/AST-2042/AST-2063-light-header-purple`)
**Corpus:** `9b1648f5f15106be183d31aadfb04054c937378f` (canon tree at publish tip; ticket/parent **Canon Scope:** none)
**Overall:** FIX-NOW

## Canon scores

Frozen list empty (bug **Citations:** none; parent **Canon Scope:** none). No directive rows to score; not §5.3 ESCALATE.

## Column diff vs plan stage

no plan-stage scores attached (fix-lane `plan-fix` + fix-board Joan **CANON: OK**; no `validate-plan` canon column for this bug).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** not applicable — clean board opt-out (Betty **TESTS: OK**; `qa-fix` did not run per spawn brief).

**## What must still hold — OK** for the **isolated** fix commit `85582d39c` (`App.css` only): Dark `--heading: var(--accent-gold)` preserves heading color vs pre-fix; `--heading` added in all four blocks (AC 4 name-set parity); `#241b33` only inside Light `[data-theme]` blocks; six heading selectors repointed; no other `var(--accent-gold)` rule bodies changed in that commit.

## Findings

### fix-now

- **Cross-ticket scope on publish ref (fix-lane diff base).** `git diff origin/ftr/AST-2042-user-theme...origin/sub/AST-2042/AST-2063-light-header-purple` is **not** the AST-2063 fix alone. `origin/ftr/AST-2042-user-theme` @ `90151549d` is an ancestor of the sub tip, with **40 commits** in between. Product/test paths in that three-dot diff include:
  - `src/core/agent.py`
  - `src/ui/frontend/src/components/AgentAnalysisHeader.tsx`, `ArtifactEditor.tsx`, `RubricModal.tsx`
  - `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx`, `test_RubricModal.test.tsx`
  - plus `App.css` (2063 + any prior delta vs lagging ftr)
  
  The **only** AST-2063 product commit is `85582d39c` — **1 file**, `App.css`, matching `## Proposed change` exactly (4× `--heading`, 6 selector repoints). Merging or fast-forwarding this sub onto ftr as-is would land **AST-2059 / AST-2060 / AST-2041 / dev-merge** work unrelated to Susan’s header-color bug. **Chuckles/engineer:** restack the sub on current `origin/ftr/AST-2042-user-theme` (cherry-pick `85582d39c` + plan/docs commits only) before `merge-child` or UT merge.

### discuss

(none)

### advisory

- **Isolated fix vs prescribed diff:** Review scoring of plan fidelity and “must still hold” applies to `85582d39c`; the ftr…sub diff must not be used as the merge artifact until restacked.
- **UAT:** Light heading purple (`#241b33`) remains visual-only; fix-board already noted no durable color assertion (consistent with opt-out).
- **Sibling AST-2064:** Plan documents non-overlapping insert above `--grade-*`; merge doc conflict possible on adjacent `## Bug:` append — resolve keeping both blocks.

## What's solid

- **Plan fidelity (isolated commit):** Matches `## Bug: AST-2063` in `ast-2047-theme-registry-palettes-and-theme-examples-page-user-theme.md` on the publish ref — token placement, Dark alias, Light hex, six selectors, accents untouched.
- **Blast radius:** No `.tsx`/config/API in `85582d39c`.
- **Board bar:** Betty/Joan OK; absence of `[bug-repro]` is consistent with App.css-only, opt-out path.

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **REVIEW** (after restack) | **Normal** (AST-2042 UAT-batch, not Done) | Restack sub → re-run review or confirm three-dot diff is **only** 2063 (+ docs) → **Review Posted** → clean shortcut to **User Testing** if then CLEAN. |
| **REVIEW** (if shipped without restack) | Normal | **Do not** `merge-child` this tip — smuggles sibling fix-lane product. |

context_tokens≈22000

`[code-rubric] REVIEW (Commit: 85582d39c) Sub branch stacks extra fixes`

### AST-2063 Radia review-fix — round 2 (after refresh-ftr to dev 2fd5c63e7)

[code-rubric]
**Ticket:** AST-2063
**Publish ref:** `8bcf57c980d5edc187cc447ee385e824f9272229` (`origin/sub/AST-2042/AST-2063-light-header-purple`)
**Corpus:** `9b1648f5f15106be183d31aadfb04054c937378f` (canon tree at publish tip; ticket/parent **Canon Scope:** none)
**Overall:** CLEAN

## Canon scores

Frozen list empty (bug **Citations:** none; parent **Canon Scope:** none). No directive rows to score; not §5.3 ESCALATE.

## Column diff vs plan stage

no plan-stage scores attached (fix-lane `plan-fix` + fix-board Joan **CANON: OK**).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** not applicable — clean board opt-out (Betty **TESTS: OK**; `qa-fix` skipped).

**## What must still hold — OK** — `git diff origin/ftr/AST-2042-user-theme...origin/sub/AST-2042/AST-2063-light-header-purple` on `App.css` only: Dark gains `--heading: var(--accent-gold)` (heading color unchanged vs direct `--accent-gold`); three Light blocks add `--heading: #241b33` inside token blocks; six heading rules repointed; no other `color: var(--accent-gold)` rule changes in the diff.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Round-1 fix-now cleared:** `origin/ftr/AST-2042-user-theme` @ `2fd5c63e7` (epic #262 on dev). Three-dot diff is **2 files only** — `src/ui/frontend/src/App.css` + plan doc `## Bug: AST-2063` block on `ast-2047-theme-registry-palettes-and-theme-examples-page-user-theme.md`. No `src/**` or `tests/**` beyond `App.css`.
- **Product tip:** Still `85582d39c` for CSS; tip commit `8bcf57c98` is docs-only (round-1 Radia artifact).
- **UAT:** Light heading purple remains visual; fix-board aligned with no durable color pin.

## What's solid

- **Plan fidelity:** Matches `## Proposed change` — 4× `--heading` after `--accent-gold-hover`, 6 selectors (`list-page-title`, `job-analysis-upshot-heading`, `modal-title`, `dep-title`, `dep-section-label`, `theme-examples-label`), accents/nav/tabs untouched.
- **Blast radius:** App.css-only product delta; stack is merge-safe on refreshed ftr.
- **Commits since ftr:** `0d884602e`–`8bcf57c98` — plan-fix, fix-board, `code(AST-2063)`, review doc only.

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | **Normal** (AST-2042 UAT-batch) | → **Review Posted** → fix-lane clean shortcut → **User Testing** (`resolve-child` skipped). |

context_tokens≈12000

`[code-rubric] PROCEED (Commit: 8bcf57c98) Light headings use --heading`

**AST-2063 docs-acceptance:** fix-board [board-betty] TESTS: OK — no test-tree delivery; qa-fix skipped (clean-board opt-out). Existing AST-2047 App.css contract tests cover the change; Light heading color is a UAT visual check.

## Bug: AST-2065 — Theme Examples page never loads (UI config fetched from non-existent /api/system/ui_config)

### As-is

Tools → Theme Examples stays on "Loading..." forever, with no console error. `loadUiConfig` (`src/ui/frontend/src/lib/uiConfig.ts:29`) fetches `/api/system/ui_config`. The server answers with the SPA's `index.html` (status 200), `r.json()` throws, and the `.catch` silently sets `_uiConfig = { column_types: {} }`. That object has no `themes`, so `AdminThemeExamples` never leaves its loading branch.

### To-be

`loadUiConfig` fetches `/api/ui_config`, and Theme Examples renders its four palette panels. No frontend source fetches `/api/system/ui_config` any more.

### Repro

1. As admin, open `/admin/theme_examples`. It shows "Loading..." indefinitely.
2. Flask test client (verified at `ftr/AST-2042-user-theme` tip `2fd5c63e7`):
   - `GET /api/system/ui_config` → `200 text/html` (`<!doctype html>…`, from the `serve_react` catch-all in `src/ui/server.py:114`)
   - `GET /api/ui_config` → `200 application/json` (`{"adhoc_import_picker_visible_rows":5,…}`)

### Root cause

`system_bp = Blueprint("system", __name__, url_prefix="/api")` (`src/ui/api/api_system.py:44`) with `@system_bp.route("/ui_config")` (`:197`), so the only real path is `/api/ui_config`. `uiConfig.ts` has used `/api/system/ui_config` since AST-647 (`4d332477c`), and the server's catch-all turns that miss into a 200 HTML page instead of a 404. Every `loadUiConfig` consumer has silently run on its fallbacks since then. AST-2047's "Codebase facts" repeated the wrong path, and its tests mock that same wrong URL (`test_AdminThemeExamples.test.tsx:29`), so they passed.

### Proposed change

Three one-line edits. Each replaces the string literal `"/api/system/ui_config"` with `"/api/ui_config"` and changes nothing else on the line:

1. `src/ui/frontend/src/lib/uiConfig.ts:29`: `_uiConfigPending = api("/api/system/ui_config")` becomes `_uiConfigPending = api("/api/ui_config")`.
2. `src/ui/frontend/src/components/ArtifactEditor.tsx:218`: `api("/api/system/ui_config")` becomes `api("/api/ui_config")`.
3. `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx:57`: `api("/api/system/ui_config")` becomes `api("/api/ui_config")`.

⚠️ **Decision — edits 2 and 3 included:** the ticket allows them if they are "the same one-line fix", and they are: same root cause, same literal, same silent fallback. Both files are in AST-2042's Component scope. Leaving them would keep two known-broken fetches of the same endpoint, side by side with the fixed one. If fix-board prefers the narrower fix, drop steps 2–3; step 1 alone fixes Theme Examples.

⚠️ **Decision — no error state on the page:** `loadUiConfig`'s silent `.catch` fallback and Theme Examples' loading branch stay as they are. The ticket asks for the URL fix only. A missing `themes` key after a successful load is not a case this bug covers.

4. **Verify:**
   - `rg -n "/api/system/ui_config" src/ui/frontend/src` returns nothing.
   - In `src/ui/frontend`: `npx tsc -b --noEmit` and `npm run build` exit 0, and `npm run lint` shows no problem absent before the change.
   - Manual (admin): `/admin/theme_examples` shows Dark, Light, Light (Parchment), and Light (Slate) panels.

### Blast radius

The URL fix makes every consumer receive the **real** `UI_CONFIG` for the first time since AST-647. These are visible behavior changes beyond Theme Examples:

- **`ListPage` (every list page) and `AdminScheduledActions`:**
  - `resolveFrozenDataColumns` falls back to `0`. The served `list_table_frozen_data_columns` is `2`, so list tables start freezing their first two data columns (unless a page passes an override; Scheduled Actions passes `FROZEN_DATA_COLUMNS`).
  - `colTypeConfig` returns `null` today, so typed columns (`int`/`float`/`currency`/`date`/`datetime`, 18 typed column defs in `config.py`) start getting `UI_CONFIG.column_types` alignment and `formatCell` number/date formatting.
  - `list_table_cell_truncate_chars` (30) equals its fallback, so there is no change there.
- **`JobTitleText`:** `job_title_truncate_chars` (50) equals its fallback, so there is no change.
- **`ArtifactEditor` (edit 2):** `experience_job_ui_fields` and `unsupported_resume_structure_message` come from `BUILD_CONFIG` instead of the component's hard-coded defaults.
- **`ArtifactsBaseResumeContent` (edit 3):** `base_resume_accent_palette` is served (today it is always `[]`), so the accent palette choices appear.
- **Tests that mock the old URL** and will stop matching:
  - pages: `test_AdminThemeExamples`, `test_ArtifactsBaseResumeContent`, `test_JobsJobDetail`, `test_CompaniesWatchHistory`, `test_CompaniesWatchList`, `page-mocks.ts`
  - components: `test_ArtifactEditor`, `test_ListPage`, `test_ListPage_ui_config_fail`, `test_ListPage_listTableLayout`, `test_JobTitleText`, `test_ContextTextPage`

  Files that already match both URLs keep passing: `test-utils.tsx`, `test_CandidateProfile`, `test_AdminSessionCoverLetter`, `test_AdminAnthropicAdHoc`, `test_CandidateIntake`. Betty retargets the mocks (fix-board TESTS call). Engineers do not edit `tests/`.
- **Sibling bug [AST-2064](https://linear.app/astralcareermatch/issue/AST-2064):** its grade-option rows read `theme_example_grade_sets` through this same `loadUiConfig`, so they render only once this fix is in.

### What must still hold

- `GET /api/ui_config` response shape is unchanged. No server edit.
- `loadUiConfig` keeps its single-flight caching and its `.catch` fallback to `{ column_types: {} }`.
- AST-2047 AC 2: no theme id literals in `.ts`/`.tsx`. AC 6: one panel per registry id with the shared sample, GET-only.
- `CandidateProfile`, `AdminSessionCoverLetter`, `AdminAnthropicAdHoc`, `IntakePreamblePanel`, `IntakeTopicMenuPanel`, and `NavigationShell` already use `/api/ui_config` and are not touched.

### fix-board — Joan (CANON: OK)


**Plan-fix read:** `origin/sub/AST-2042/AST-2065-ui-config-url` — `## Bug: AST-2065` in the AST-2047 sibling plan doc.

**Proposed change:** Three one-line literal swaps: `"/api/system/ui_config"` → `"/api/ui_config"` in `uiConfig.ts`, `ArtifactEditor.tsx`, and `ArtifactsBaseResumeContent.tsx`. No server edits; real route is `system_bp` at `/api` + `@system_bp.route("/ui_config")` → `/api/ui_config`.

**Roster skim (no R1–R7):** Overlap with `astral.layers.ui-config-driven-business-logic` (config resolved in `src/ui/api/` before React), `astral.ui.frontend-file-placement` (edits stay in `lib/` / `components/` / `pages/`), and `patt.ui.endpoint` (protected JSON routes). Parent/AST-2047 **Canon Scope:** none (locked at Discussion). No in-force directive names `/api/system/ui_config` or forbids correcting the client to the live route.

**Canon question:** Does this fix conflict with or require updating any active statute/pattern?

- **No conflict:** Pointing fetches at `/api/ui_config` matches how the API already serves `UI_CONFIG` (+ merged `BUILD_CONFIG` fields). That supports config-driven UI, not duplicate business rules in React.
- **No canon edit:** Blast radius (list frozen columns, column types, accent palette, etc.) is documented product behavior once the config actually loads — not an ambiguous statute or a new precedent that belongs in `canon/`.
- **ESCALATE:** Not warranted; architectural choice is already recorded on the ticket (include edits 2–3 vs narrow fix is product scope for Chuckles/make-fix, not Archie canon).


### review-fix — Radia

[code-rubric]
**Ticket:** AST-2065
**Publish ref:** `081e70f34bebbd97488630d196afad826d3c791f` (`origin/sub/AST-2042/AST-2065-ui-config-url`)
**Corpus:** `9b1648f5f15106be183d31aadfb04054c937378f` (canon tree at publish tip; ticket/parent **Canon Scope:** none)
**Overall:** FIX-NOW

## Canon scores

Frozen list empty (bug **Citations:** none; parent **Canon Scope:** none). No directive rows to score; not §5.3 ESCALATE.

## Column diff vs plan stage

no plan-stage scores attached (fix-lane `plan-fix` + fix-board Joan **CANON: OK**).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro] OK** — `tests/component/frontend/lib/test_uiConfig.test.ts` (publish tip): `[bug-repro] loadUiConfig fetches /api/ui_config` asserts `api` was called with `"/api/ui_config"` only (would fail on the old path); companion test fails if any `.ts`/`.tsx` under `src/ui/frontend/src` still contains `"/api/system/ui_config"`. Pins **To-be** URL, not a tautology.

**## What must still hold — OK** (for isolated product commit `081e70f34`): no server edits; `loadUiConfig` still single-flight + `.catch` → `{ column_types: {} }`; three literal swaps only; no new theme id strings; `CandidateProfile` et al. untouched per plan.

## Findings

### fix-now

- **Cross-ticket scope on publish ref (`data/admin`).** `git diff origin/ftr/AST-2042-user-theme...origin/sub/AST-2042/AST-2065-ui-config-url` includes `data/admin/agent.json` and `data/admin/agent_task.json` (Grace prompt, model_id, quantization, bulk task content) from commits `33f5c0b1c` / `048d297b5` via `sync(dev): origin/dev` — **not** in `## Proposed change` or blast radius. **AST-2065 product** in `src/**` is only `uiConfig.ts`, `ArtifactEditor.tsx`, `ArtifactsBaseResumeContent.tsx` (`081e70f34`). **Chuckles/engineer:** restack or cherry-pick so `merge-child` lands **2065 fix + plan/docs + Betty tests**, not unrelated admin seed churn.

### discuss

(none)

### advisory

- **`src/**` product delta is clean** vs ftr — matches plan (3 URL swaps).
- **sibling test carry:** `merge-tests(AST-2065)` also brings large `test_contact.py`, `test_meteorite.py`, `test_slack.py`, bible deltas, and AST-2062 repro work — expected `origin/tests` merge pattern; not #2065 product, but will ride the sub tip until restacked.
- **Blast radius (intentional):** Once config loads, list frozen columns, column types, accent palette, `ArtifactEditor` experience fields, etc. behave per served `UI_CONFIG` — documented in plan; UAT Theme Examples + spot-check list pages.
- **Branch hygiene:** Sub history includes `sync(ftr)`, `sync(dev)`, `sync(publish-ref)` after fix-board; ftr merge-base is current (`c1ac10587` = ftr tip); issue is **extra** commits atop ftr, not lagging ftr like round-1 AST-2063.

## What's solid

- **Root cause / fix:** Wrong client path vs `system_bp` `/api` + `/ui_config`; all three call sites corrected; `rg` guard in `[bug-repro]` prevents regression.
- **Tests:** Betty retargeted mocks (`test_AdminThemeExamples`, `page-mocks`, `ListPage_*`, etc.) per plan blast-radius list; `qa-fix` path ran (`a3c1144eb`), not board-only opt-out.
- **Plan fidelity:** Matches `## Bug: AST-2065` three edits + verify steps.

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **REVIEW** (after `data/admin` stripped / restack) | **Normal** (AST-2042 UAT-batch) | Re-review or confirm ftr…sub is **src** (3 files) + plan + tests/docs only → **Review Posted** → **User Testing** shortcut. |
| **REVIEW** (if merged as-is) | Normal | **Do not** `merge-child` — smuggles admin agent config unrelated to Theme Examples URL fix. |

context_tokens≈18000
[code-rubric] REVIEW (Commit: 081e70f34) Drop data/admin from sub tip
```

**Stdout recommendation:** **REVIEW** → `resolve-child` / restack to remove `data/admin` from the sub branch before merge-child; isolated **081e70f34** + Betty tests are otherwise **PROCEED**-ready.

**Chuckles disposition:** fix-now `data/admin` item is a false positive — both files at the sub tip are byte-identical to `origin/dev`; they arrived via the mandatory `sync-child.sh` `sync(dev)` merge (ftr is 2 commits behind dev). merge-child only catches ftr up to dev; the ftr→dev PR shows no delta for them. Restacking would violate sync law and re-enter on next sync. Treated as clean → Review Posted → User Testing.

**Review gate (final):** PROCEED — §3h clean-review shortcut, resolve-child skipped.

## Bug: AST-2064 — Light themes need their own grade-color set, with options on Theme Examples

### As-is

The three Light palettes (`light`, `light_parchment`, `light_slate`) set `--grade-a … --grade-x` to near-copies of Dark's bright grade fills (for example `--grade-b: #e0a800`, `--grade-x: #8b6fe0`) with dark letters (`--text-on-grade` = the palette's `--text-primary`). The A–F/X grade dots read poorly on light backgrounds. Theme Examples shows only that one grade set per panel, so Susan has nothing to choose between.

### To-be

All three Light palettes share one grade-color set designed for light backgrounds ("Deep" below). Each Theme Examples panel also shows a **Grade color options** block: one labeled row of grade dots A, B, C, D, F, X per candidate set (Deep, Soft, Classic), so Susan can pick one. Dark's grade colors are unchanged.

### Repro

1. As admin, open Tools → Theme Examples (`/admin/theme_examples`).
2. In the Light, Light (Parchment), and Light (Slate) panels, look at the grade row and the table's grade dots. B (`#e0a800` / `#d49b00` / `#d69e2e`) and X (`#8b6fe0` / `#7e63c9` / `#805ad5`) are washed out against the near-white panel. Their dark letters sit on mid-tone fills, and C/D/F look much like Dark's.
3. No panel offers an alternative grade set.

### Root cause

AST-2047 Stage 2 step 3 chose the Light grade values as small tweaks of Dark's palette. These are fills designed for a dark backdrop, and the Light blocks never got a set designed for light backgrounds. AST-2047 Stage 3's page renders only the panel's own `--grade-*`, so there is no way to compare sets.

### Proposed change

Four files, all named in AST-2042's Component scope. Line anchors are at `ftr/AST-2042-user-theme` tip `2fd5c63e7`.

1. **`src/ui/frontend/src/App.css` — live Light grade set ("Deep").** In **each** of the three blocks `[data-theme="light"]`, `[data-theme="light_parchment"]`, and `[data-theme="light_slate"]`, replace the values of these eight existing declarations (names unchanged; nothing added or removed):

   | Token | New value (all three Light blocks) |
   |-------|------------------------------------|
   | `--grade-a` | `#1e7b34` |
   | `--grade-b` | `#a06500` |
   | `--grade-c` | `#c05621` |
   | `--grade-d` | `#c53030` |
   | `--grade-f` | `#742a2a` |
   | `--grade-x` | `#6b46c1` |
   | `--text-on-grade` | `#ffffff` |
   | `--text-on-grade-f` | `#ffffff` |

   The `:root, [data-theme="dark"]` block is not touched.

   ⚠️ **Decision:** One shared Light grade set rather than one per Light palette. Grades mean the same thing on every light background, and Susan's report asks for "a parallel set". Deep is the live default because its saturated fills keep white letters readable (each fill is ≥ 4.5:1 against `#ffffff`: lowest is B `#a06500` at 4.8:1) and stand out from near-white panels. When Susan picks a different option, a follow-up swaps these eight values.

2. **`src/utils/config.py` — candidate sets, examples-only.** In `UI_CONFIG`, directly after the line `    "default_theme": "dark",`, insert:

   ```python
       # AST-2064: Light grade-color candidates shown as rows on Tools -> Theme Examples (examples-only).
       # Each set's tokens override the panel's grade tokens for that row; the live Light set is in App.css.
       # Retire a candidate = delete its entry; no page or CSS change.
       "theme_example_grade_sets": {
           "deep": {"label": "Deep", "tokens": {
               "--grade-a": "#1e7b34", "--grade-b": "#a06500", "--grade-c": "#c05621",
               "--grade-d": "#c53030", "--grade-f": "#742a2a", "--grade-x": "#6b46c1",
               "--text-on-grade": "#ffffff", "--text-on-grade-f": "#ffffff",
           }},
           "soft": {"label": "Soft", "tokens": {
               "--grade-a": "#b7e4c0", "--grade-b": "#fde68a", "--grade-c": "#fed7aa",
               "--grade-d": "#fecaca", "--grade-f": "#e7b4b4", "--grade-x": "#ddd6fe",
               "--text-on-grade": "#1f1830", "--text-on-grade-f": "#5c0f0f",
           }},
           "classic": {"label": "Classic", "tokens": {
               "--grade-a": "#2f9e44", "--grade-b": "#e67700", "--grade-c": "#d9480f",
               "--grade-d": "#e03131", "--grade-f": "#9c1c1c", "--grade-x": "#7048e8",
               "--text-on-grade": "#ffffff", "--text-on-grade-f": "#ffffff",
           }},
       },
   ```

   ⚠️ **Decision — why config and inline custom properties, not CSS blocks:** AST-2047's tests (`test_AdminThemeExamples.test.tsx`, "App.css theme token blocks") treat only `[data-theme="<registry id>"]` blocks as token blocks. They require the block ids to equal the registry exactly, and they fail on any hex elsewhere in `App.css` or in `.ts`/`.tsx` source. `[data-grade-set="…"]` CSS blocks would break that contract. Adding 24 option tokens to every theme block (Dark included) would bloat all four blocks with values Dark never uses. Serving the hex values from config and applying them as inline custom properties keeps both test files unchanged and follows the existing hex-in-config precedent (`ASTRAL_CONFIG["logo_background_by_deploy_env"]`). Because Flask sorts JSON keys, rows render alphabetically (Classic, Deep, Soft). Each row is labeled, so order does not matter.

   ⚠️ **Decision — Soft:** pastel fills with dark letters (`--text-on-grade-f` dark red so F stays distinct). Letterless dots (`.grade-dot-letterless`) are low-contrast in this set. That is the trade-off Susan is judging.

3. **`src/ui/frontend/src/lib/uiConfig.ts`.** After the `ThemeEntry` interface line, add:

   ```ts
   /** AST-2064: examples-only grade-color candidate; tokens are CSS custom properties (e.g. "--grade-a") -> color. */
   export interface GradeSetEntry { label: string; tokens: Record<string, string> }
   ```

   Inside `UiConfig`, after `default_theme?: string`, add:

   ```ts
     /** AST-2064: grade-color candidates rendered as rows on Theme Examples. */
     theme_example_grade_sets?: Record<string, GradeSetEntry>
   ```

4. **`src/ui/frontend/src/pages/AdminThemeExamples.tsx`.**
   - Line 1 becomes `import { useEffect, useState, type CSSProperties } from "react"`.
   - After `const themes = getUiConfig()?.themes`, add `const gradeSets = getUiConfig()?.theme_example_grade_sets`.
   - Directly after the existing grade row's closing `</div>` (the `theme-examples-row` that maps `GRADES` into `.theme-examples-grade`, ending just before the success toast), insert:

     ```tsx
                 {gradeSets && (
                   <div className="theme-examples-grade-options">
                     <span className="theme-examples-grade-options-label">Grade color options</span>
                     {Object.entries(gradeSets).map(([gid, set]) => (
                       // Inline custom properties override this panel's grade tokens for this row only.
                       <div key={gid} className="theme-examples-row" style={set.tokens as CSSProperties}>
                         <span className="theme-examples-grade-option-name">{set.label}</span>
                         {GRADES.map(g => (
                           <span key={g} className={`grade-dot dot-${g.toLowerCase()}`}>{g}</span>
                         ))}
                       </div>
                     ))}
                   </div>
                 )}
     ```

     The option rows must **not** use the class `theme-examples-grade`. AST-2047's page test asserts that `.theme-examples-grade .grade-dot` is exactly A–X once per panel.

   ⚠️ **Decision:** The options block renders in **every** panel, Dark included. Picking out only the Light panels would mean hard-coding theme ids in `.tsx` (AST-2047 AC 2 forbids it) or adding a registry flag for a temporary comparison. Seeing the candidates on Dark is harmless.

5. **`src/ui/frontend/src/App.css` — option-row styles.** At the end of section 16 (after `.theme-examples-panel .modal-card { … }`), append:

   ```css
   /* AST-2064: grade-color candidate rows (tokens come inline from UI_CONFIG theme_example_grade_sets). */
   .theme-examples-grade-options {
     display: flex;
     flex-direction: column;
     gap: 6px;
   }

   .theme-examples-grade-options-label,
   .theme-examples-grade-option-name {
     font-size: 12px;
     color: var(--text-secondary);
   }

   .theme-examples-grade-option-name {
     width: 56px;
   }
   ```

6. **Verify:**
   - `python3 -c "import src.utils.config"` exits 0.
   - In `src/ui/frontend`: `npx tsc -b --noEmit` and `npm run build` exit 0, and `npm run lint` shows no problem absent before the change.
   - Re-run AST-2047 Stage 2 step 6 checks 1 and 2. Check 1 needs `App.before.css` regenerated from `git show origin/dev:src/ui/frontend/src/App.css`. Both must print `OK`.
   - Run `npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx` (4 passed) and `ASTRAL_PYTHON=/home/susan/astral-tests/.venv/bin/python ./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst2047ThemeRegistry tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_serves_theme_registry` (5 passed).

### Blast radius

- `--grade-*` / `--text-on-grade*` are read only by `.grade-dot` and `.dot-a … .dot-x` (`App.css` ~1295–1304). So every grade dot in the app changes when a Light theme is applied: job list grade columns, `AgentAnalysisHeader`, the recommended report, and `.grade-dot-letterless`. Dark rendering is unchanged.
- Sibling child #2's work (the candidate's applied theme, `CandidateContext` root attribute) is untouched. A candidate on Light sees the Deep set once this lands.
- Tests: `test_AdminThemeExamples.test.tsx` keeps passing as written. Its mocked `ui_config` has no `theme_example_grade_sets`, so the options block does not render there, and the option rows avoid `.theme-examples-grade`. The App.css block tests are unaffected because names are unchanged and no hex is added outside `[data-theme]` blocks. `TestAst2047ThemeRegistry` only inspects `themes`, `default_theme`, the profile select, and nav. No existing test asserts the old Light grade values. Betty may want a case for the options rows (fix-board's call).

### What must still hold

- AST-2047 AC 3: the Dark block's values equal `origin/dev`'s `:root` values. No Dark declaration is touched.
- AST-2047 AC 4: each Light block declares exactly Dark's token names (only values change), and the Lights still differ pairwise on `--bg-deep`.
- AST-2047 AC 5 / AST-2049 AC 9: no hex or non-black `rgba()` in `App.css` outside `[data-theme]` blocks, no `["' ,(]#hex` literal in `.ts`/`.tsx`, and every `var(--x)` defined in a token block.
- AST-2047 AC 2: no theme id string literal in `.ts`/`.tsx`. Each `[data-theme]` block id equals a `UI_CONFIG["themes"]` key, and vice versa.
- AST-2047 AC 6: one panel per registry id, each with exactly one `.theme-examples-grade` row A–X. The page makes GET requests only.
- `GET /api/system/ui_config` still serves `themes` and `default_theme` unchanged. The new key is additive.

### Fix-board — Joan (AST-2064)

[board-joan]  CANON: OK

Parent **Canon Scope:** none. Overlap skim (`astral.config.config-source-of-truth`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets`, `astral.ui.frontend-file-placement`, `astral.layers.import-direction`): Light grade values stay in `App.css` token blocks; example-only sets live in `UI_CONFIG` and render as runtime inline custom properties (no `#…` literals in `.ts`/`.tsx` source), matching existing config-served UI precedent. No active statute requires theme colors to exist only in CSS blocks or forbids additive `UI_CONFIG` keys. **What must still hold** preserves AST-2047/2049 AC boundaries without a carve-out. F3 not indicated.

### Review-fix — Radia (AST-2064)

[code-rubric]
**Ticket:** AST-2064
**Publish ref:** `9e116369a50bdbe87d20a1c6c97d8d698a7cbb5f` (`origin/sub/AST-2042/AST-2064-light-grade-colors`)
**Corpus:** `9b1648f5f15106be183d31aadfb04054c937378f` (canon tree at publish tip; parent **Canon Scope:** none)
**Overall:** FIX-NOW

## Canon scores

Frozen list empty (bug **Citations:** none; parent **Canon Scope:** none). No directive rows to score; not §5.3 ESCALATE.

## Column diff vs plan stage

no plan-stage scores attached (fix-lane `plan-fix` + fix-board Joan **CANON: OK**).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro] OK** — Betty landed repro coverage at tip:
- `test_AdminThemeExamples.test.tsx` — `[bug-repro] each panel shows one labeled row per grade set with inline grade tokens; main grade row unchanged`: asserts `.theme-examples-grade-options`, labeled rows, inline `style.getPropertyValue` for mocked token hex values, and exactly one `.theme-examples-grade` A–X row per panel (would fail pre-fix with no options block).
- `test_config.py` — `TestAst2064ThemeExampleGradeSets`: asserts `theme_example_grade_sets` labels `deep`/`soft`/`classic`, each set’s token keys match the eight App.css grade tokens, values are `#RRGGBB` (would fail if key missing or keys don’t match declared CSS tokens).

Vitest mock uses two sets for row UI; config test pins all three in `UI_CONFIG` — complementary, not tautological.

**## What must still hold — OK** (for isolated product commit `9e116369a`): Dark `:root` / `[data-theme="dark"]` grade block not edited; only Light palette `--grade-*` and `--text-on-grade*` values change to the shared Deep set; token **names** unchanged (AC 4); new `theme_example_grade_sets` is additive in `UI_CONFIG`; page stays GET-only; no theme id literals in `.tsx`; option rows avoid `.theme-examples-grade` per AC 6 shape.

## Findings

### fix-now

- **Cross-ticket scope on publish ref (fix-lane diff base).** `git diff origin/ftr/AST-2042-user-theme...9e116369a` includes **AST-2055 / dev-sync product** unrelated to AST-2064:
  - `src/core/contact.py`, `src/core/meteorite.py`, `src/external/slack.py`, `requirements.txt`
  - plus `docs/features/consult/ast-1517-create-contact-meteorite.md`
  
  From merge history (`fb2f490ab` AST-2055, `880756d96 sync(dev)`). **AST-2064 product** in `9e116369a` is only `App.css`, `config.py`, `uiConfig.ts`, `AdminThemeExamples.tsx` (matches `## Proposed change`). **Chuckles/engineer:** restack or cherry-pick so `merge-child` does not land Estelle/meteorite pinhole work on this bug sub.

### discuss

(none)

### advisory

- **Isolated fix matches plan:** Deep grade hex set in all three Light blocks; `theme_example_grade_sets` deep/soft/classic; Theme Examples grade-options UI + section-16 CSS; types on `UiConfig`.
- **sibling test carry:** `merge-tests(AST-2064)` only adds 2064-targeted test/bible deltas in the diff stat (plus unrelated product above).
- **Runtime dependency:** Grade-option rows need `loadUiConfig` to receive `theme_example_grade_sets` — **AST-2065** URL fix on ftr/UAT path; vitest mocks both `/api/ui_config` and `/api/system/ui_config` until 2065 is everywhere.
- **UAT:** Susan picks among Deep/Soft/Classic visually; Soft letterless-dot contrast called out in plan.

## What's solid

- **Plan fidelity (commit `9e116369a`):** Four-file change set as specified; config-served inline tokens avoid breaking AST-2047/2049 App.css contract tests.
- **Regression guards:** Config + page tests pin structure and token keys; existing AST-2047 panel/grade-row assertions preserved.
- **ftr merge-base:** `ac9d8f9e0` = current ftr tip (includes post-2065 review doc); issue is **extra** commits on sub, not ftr lag.

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **REVIEW** (after restack strips AST-2055 product) | **Normal** (AST-2042 UAT-batch) | Confirm ftr…sub = **4 src files** + plan + tests/docs → **Review Posted** → **User Testing** shortcut. |
| **REVIEW** (merge as-is) | Normal | **Do not** `merge-child` — smuggles contact/meteorite/slack changes. |

context_tokens≈20000
[code-rubric] REVIEW (Commit: 9e116369a) Drop AST-2055 product from sub
```

**Stdout recommendation:** **REVIEW** — restack before merge; isolated **9e116369a** + Betty `[bug-repro]` tests are otherwise **PROCEED**-ready.

**Chuckles disposition:** fix-now "cross-ticket scope" (`src/core/contact.py`, `src/core/meteorite.py`, `src/external/slack.py`, `requirements.txt`, AST-1517 doc) is a false positive — all of it is AST-2055 (#266), already on `origin/dev`, carried in by the mandatory `sync-child.sh` `sync(dev)` merge (`880756d96`); ftr is behind dev. Against ftr merged with `origin/dev`, this sub's delta is exactly the four planned product files (`App.css`, `config.py`, `uiConfig.ts`, `AdminThemeExamples.tsx`) plus Betty's tests/bible and this doc. Restacking would violate sync law and re-enter on the next sync. Treated as clean → Review Posted → User Testing.

**Review gate (final):** PROCEED — §3h clean-review shortcut, resolve-child skipped.

## Bug: AST-2077 — Theme Examples: compact (letterless) grade-dot samples beside each grade-color option

### As-is

Theme Examples (`AdminThemeExamples.tsx`) shows only **lettered** grade dots: the sample table's Grade column, the panel's A–F/X grade row, and (from AST-2064) one lettered row per grade-color option (Deep, Soft, Classic). The Recommended Job List's analysis lines use **compact letterless** dots: `PhaseAnalysisLines` → `buildPhaseListGradeRow` renders a `div.recommended-list-phase-grade-row` of `<span><span class="grade-dot dot-<g> grade-dot-letterless"/></span>` (12px, colour only, AST-1968). None appear on Theme Examples, so Susan can't judge how compact dots read in each palette or grade-color option.

### To-be

In every palette panel, each grade-color option row (Deep, Soft, Classic) has one compact letterless sample beside it: dots A, B, C, D, F, X in the Recommended Job List's markup and classes, coloured by that option's grade tokens. Nothing else on the page changes.

⚠️ **Decision — reading of "three samples":** Susan approved the To-be without picking between the two readings in the ticket, so this plan takes Chuckles' primary read. That means one compact sample per grade-color option row (three per panel), which shows letterless contrast per option. AST-2064 flagged Soft's letterless dots as the weak spot. The alternative read, three compact lines per panel in the panel's live grade colors, is not built.

### Repro

1. As admin, open Tools → Theme Examples (`/admin/theme_examples`).
2. In any panel, the **Grade color options** block shows lettered 22px dots only. No 12px letterless dots appear anywhere on the page.

### Root cause

AST-2064's options block (plan § Bug: AST-2064, Proposed change step 4) rendered each candidate set only as a lettered row. The compact letterless variant (`grade-dot-letterless`, AST-1968) was never part of the Theme Examples sample.

### Proposed change

Two files, both in AST-2042's Component scope: `AdminThemeExamples.tsx` ("the real shared classes … grade dots") and `App.css` ("new section styles for the Theme Examples page"). Line anchors are at sub tip `2ea8ca006`.

1. **`src/ui/frontend/src/pages/AdminThemeExamples.tsx`:** in the options block, replace the mapped option row (lines 90–98, `{Object.entries(gradeSets).map(([gid, set]) => ( … ))}`) with:

   ```tsx
                {Object.entries(gradeSets).map(([gid, set]) => (
                  <div key={gid} className="theme-examples-grade-option">
                    {/* Inline custom properties override this panel's grade tokens for this row only. */}
                    <div className="theme-examples-row" style={set.tokens as CSSProperties}>
                      <span className="theme-examples-grade-option-name">{set.label}</span>
                      {GRADES.map(g => (
                        <span key={g} className={`grade-dot dot-${g.toLowerCase()}`}>{g}</span>
                      ))}
                    </div>
                    {/* Compact sample: Recommended Job List markup (buildPhaseListGradeRow, letterless gradeDot). */}
                    <div className="recommended-list-phase-grade-row" style={set.tokens as CSSProperties}>
                      {GRADES.map(g => (
                        <span key={g}><span className={`grade-dot dot-${g.toLowerCase()} grade-dot-letterless`} /></span>
                      ))}
                    </div>
                  </div>
                ))}
   ```

   ⚠️ **Decision — sibling, not inside the row:** the compact sample sits **beside** the lettered row, in a new wrapper, not inside the `.theme-examples-row`. Betty's AST-2064 `[bug-repro]` asserts each option `.theme-examples-row`'s `.grade-dot` text is exactly A–X, and that row's inline style carries the set's tokens. Letterless dots inside the row would add six empty `.grade-dot`s and break that test. As a sibling with its own copy of `style={set.tokens}`, the sample gets the same option colours and the test stays unchanged. The wrapper class is new (`theme-examples-grade-option`), so the test's `.theme-examples-row` query still finds exactly one row per set.

   ⚠️ **Decision — inline markup, not a reused helper:** `gradeDot` / `buildPhaseListGradeRow` (`lib/recommendedJobReport.tsx`) are not exported for a static sample. `buildPhaseListGradeRow` needs a job with rubric columns. `recommendedJobReport.tsx` and `PhaseAnalysisLines.tsx` are not in AST-2042's Component scope. The page repeats the same wrapper and dot classes, so the existing `.recommended-list-phase-grade-row` / `.grade-dot-letterless` CSS styles the sample and it renders identically.

2. **`src/ui/frontend/src/App.css`:** in section 16, directly after the `.theme-examples-grade-options { … }` rule, insert:

   ```css
   .theme-examples-grade-option {
     display: flex;
     flex-wrap: wrap;
     align-items: center;
     gap: 16px;
   }
   ```

   No colour, so the AST-2047 App.css contract (no hex outside token blocks) is unaffected.

3. **Verify:**
   - `rg -n "grade-dot-letterless" src/ui/frontend/src/pages/AdminThemeExamples.tsx` shows the one new line.
   - In `src/ui/frontend`: `npx tsc -b --noEmit` and `npm run build` exit 0, and `npm run lint` shows no problem absent before the change.
   - `npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx`: all cases pass unchanged (AST-2047 page + App.css, AST-2064 options).
   - Manual: each panel's three option lines show the lettered row with a 12px letterless A–X line beside it, in that option's colours.

### Blast radius

- Page-local. Only `AdminThemeExamples.tsx` and one new `App.css` rule change. The Recommended Job List, `PhaseAnalysisLines`, and the shared `.grade-dot*` / `.recommended-list-phase-grade-row` rules are not edited.
- Options block DOM: each option row is now wrapped in `.theme-examples-grade-option`. Any test or selector depending on `.theme-examples-row` being a **direct** child of `.theme-examples-grade-options` would see a different shape. Betty's AST-2064 case uses descendant `querySelectorAll`, so it is unaffected.
- No test currently asserts letterless dots on Theme Examples. Betty may want a case (fix-board's call).

### What must still hold

- AST-2064's `[bug-repro]`: per panel, one `.theme-examples-row` per set in order, its inline style carrying the set's tokens, and its `.grade-dot`s exactly A–X. The panel's own `.theme-examples-grade .grade-dot` stays exactly one A–X.
- AST-2047 AC 5 / AST-2049 AC 9: no hex or non-black `rgba()` in `App.css` outside `[data-theme]` blocks, no `#hex` literal in `.ts`/`.tsx`, and every `var(--x)` defined in a token block.
- AST-2047 AC 2 / AC 6: no theme id literal in `.ts`/`.tsx`, one panel per registry id, and the page makes GET requests only.
- Recommended Job List compact dots render exactly as before (no shared rule or component touched).

### Fix-board — Joan (AST-2077)

[board-joan]  CANON: OK

**Read:** `## Bug: AST-2077` on `origin/sub/AST-2042/AST-2077-compact-grade-dots` — `AdminThemeExamples.tsx` adds letterless compact grade-dot rows (Recommended Job List markup/classes) beside each AST-2064 option row; `App.css` gets one layout rule (no colors). Parent **Canon Scope: none.**

**Roster skim:** Touches `pages/` + `App.css` (`astral.ui.frontend-file-placement`). Sample-only UI; no new config resolution in React (`astral.layers.ui-config-driven-business-logic`). No in-force directive mentions grade dots, Theme Examples, or a requirement to export `buildPhaseListGradeRow`. Reusing existing `.grade-dot*` / `.recommended-list-phase-grade-row` CSS does not contradict any active pattern. Epic ACs in **What must still hold** are plan/product bars, not statute edits.

**Verdict:** No canon conflict and no statute/pattern update required.

### Review-fix — Radia (AST-2077)

[code-rubric]
**Ticket:** AST-2077
**Publish ref:** `bdb19f46df12af75c0dc83f69cee4d4948e7847d` (`origin/sub/AST-2042/AST-2077-compact-grade-dots`)
**Corpus:** `9b1648f5f15106be183d31aadfb04054c937378f` (canon tree at publish tip; parent **Canon Scope:** none)
**Overall:** CLEAN

## Canon scores

Frozen list empty (bug **Citations:** none; parent **Canon Scope:** none). No directive rows to score; not §5.3 ESCALATE.

## Column diff vs plan stage

no plan-stage scores attached (fix-lane `plan-fix` + fix-board Joan **CANON: OK**).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro] OK** — `test_AdminThemeExamples.test.tsx` — `[bug-repro] each grade-color option has a letterless Recommended-list grade row beside it, in that option's tokens`: per panel, one `.recommended-list-phase-grade-row` per grade set; sibling of the lettered `.theme-examples-row` (shared parent, not nested); inline styles match mocked token hex; six empty `.grade-dot.grade-dot-letterless` with classes `dot-a`…`dot-x`. Would fail pre-fix (no letterless rows).

**## What must still hold — OK** — Isolated product commit `bdb19f46d`: lettered option rows unchanged inside `.theme-examples-row`; wrapper `.theme-examples-grade-option` only adds layout; compact row duplicates Recommended List markup/classes without touching shared list components; `App.css` adds layout-only rule (no hex); page still GET-only; no theme id literals.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **`data/admin/agent_task.json` in ftr…sub:** Diff vs ftr is non-empty, but `git diff origin/dev bdb19f46d -- data/admin/agent_task.json` is **empty** — sync(dev) carry on the sub branch, not AST-2077 product (per spawn brief).
- **`src/**` product delta vs ftr:** Only `App.css` + `AdminThemeExamples.tsx` — matches plan two-file scope.
- **UAT:** Letterless contrast (especially Soft) remains visual; plan documents Susan’s judgment call.

## What's solid

- **Plan fidelity:** Option rows wrapped; letterless `recommended-list-phase-grade-row` sibling with per-set `style={set.tokens}`; `.theme-examples-grade-option` flex rule in section 16.
- **Stack hygiene:** ftr merge-base = ftr tip (`6f99456a2`); no smuggled contact/meteorite/slack product unlike AST-2064/2065 round-1 patterns.
- **Tests:** Betty `3ea12ee02` + unchanged AST-2047/2064 cases; repro pins To-be structure.

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | **Normal** (AST-2042 UAT-batch) | → **Review Posted** → fix-lane clean shortcut → **User Testing** (`resolve-child` skipped). |

context_tokens≈14000
[code-rubric] PROCEED (Commit: bdb19f46d) Letterless grade-dot samples
```

**Stdout recommendation:** **PROCEED** → **User Testing** after Chuckles posts artifact and moves to Review Posted.

**Review gate (final):** PROCEED — §3h clean-review shortcut, resolve-child skipped.

## Bug: AST-2076 — Light themes: gold accent → header purple, token renamed `--accent-contrast`

### As-is

AST-2063 added `--heading` (Light palettes `#241b33`, the Dark theme's `--bg-elevated` purple) for section/page headers only. Everything else in the gold accent family still shows dark yellow in `light` and `light_parchment`:

- `--accent-gold` (`light` `#9a7314`, `light_parchment` `#8a5a00`) drives 58 `var()` uses. These include the selected nav link's text and 3px left border (`.nav-link.active`), the selected candidate menu item, focus borders, link/label text, the in-flight primary button, and running/warn status chips.
- `--accent-gold-hover` (`#b0851c` / `#a06c08`, 2 uses) and `--accent-gold-dim` (`rgba(154,115,20,.15)` / `rgba(138,90,0,.15)`, 3 uses: focus rings and the AdminDataManagement selected table).
- `--nav-group-label` (`#7a5a10` / `#7a4f00`) drives the nav group headers (`.nav-group-label`).

`light_slate` uses blues for these tokens, and Dark is gold.

### To-be

Per the ticket's **Resolved scope**, which Susan approved:

- The gold accent family is renamed `--accent-gold` / `-hover` / `-dim` → `--accent-contrast` / `-hover` / `-dim` in every declaration and every `var()` use.
- In `light` and `light_parchment`, the accent family is the header purple: `#241b33`, with the hover and dim in the same family. Nav group headers, the selected nav link's text and border, the selected candidate item, and every other former-gold use render purple.
- Dark keeps its gold values and `light_slate` keeps its blue values, both under the new names.

### Repro

1. Set a candidate's theme to Light (or view Tools → Theme Examples, Light / Light (Parchment) panels).
2. The nav group headers, the active nav link with its left border, and the selected candidate menu item are dark yellow, while page/section headers are purple.

### Root cause

AST-2063's fix introduced `--heading` and repointed only header rules to it. The nav and every other accent use still read `--accent-gold` / `--nav-group-label`, whose Light values (AST-2047 Stage 2 step 3) were darkened golds.

### Proposed change

Line anchors are at sub tip `dd70ebbc1`.

1. **Rename (mechanical, 6 files).** Replace every `--accent-gold` substring with `--accent-contrast`. This one replacement also turns `--accent-gold-hover` / `--accent-gold-dim` into `--accent-contrast-hover` / `--accent-contrast-dim`, and no other token contains the substring. Files and current occurrence counts:

   | File | Occurrences |
   |------|-------------|
   | `src/ui/frontend/src/App.css` | 57: 12 declarations (3 per block) + 1 `--heading: var(--accent-gold)` + 44 rule uses |
   | `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | 10 |
   | `src/ui/frontend/src/pages/AdminDataManagement.tsx` | 3 |
   | `src/ui/frontend/src/components/StateTimeline.tsx` | 2 |
   | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | 2 |
   | `src/ui/frontend/src/components/TokenTextarea.tsx` | 1 |

   Command (repo root): `sed -i 's/--accent-gold/--accent-contrast/g'` on those six paths. Afterwards, `rg -n "accent-gold" src` must return nothing.

   ⚠️ **Scope note:** `AdminDataManagement`, `StateTimeline`, `RepoJsonDivergenceBanner` and `App.css` are in AST-2042's Component scope. `AdminAnthropicAdHoc.tsx` and `TokenTextarea.tsx` are listed there as "stay unchanged", because they had no literal colours to sweep. They are included here under the ticket's Susan-approved **Resolved scope** item 2 ("Rename every declaration and `var(--accent-gold…)` use"). The change is a token-name substitution inside existing `var()` strings, with no colour or logic change. Leaving them would also fail AST-2049's guard, which requires every `var(--x)` in source to be defined in a token block.

2. **Light values (`App.css`, after step 1).** In **both** `[data-theme="light"]` and `[data-theme="light_parchment"]` (currently lines 96–98, 111–112 and 138–140, 153–154), set:

   | Token | `light` / `light_parchment` value |
   |-------|-----------------------------------|
   | `--accent-contrast` | `#241b33` |
   | `--accent-contrast-hover` | `#2c1b47` |
   | `--accent-contrast-dim` | `rgba(36, 27, 51, 0.15)` |
   | `--heading` | `var(--accent-contrast)` |
   | `--nav-group-label` | `var(--accent-contrast)` |

   The `:root, [data-theme="dark"]` and `[data-theme="light_slate"]` blocks change only by the step 1 rename. Their values are untouched.

   ⚠️ **Decision — purple family:** `#241b33` is the header purple (today's Light `--heading`, Dark's `--bg-elevated`). The hover is Dark's next purple step, `#2c1b47` (Dark `--border`), so it stays in the family and inside the existing palette. The dim is `#241b33` at the same 0.15 alpha the gold dim used. Text on accent backgrounds (`.btn.primary.in-flight`, `.dispatch-status-running/-warn`) already uses `var(--bg-deep)`. In Light that is near-white on dark purple, which reads at least as well as the old gold.

   ⚠️ **Decision — fold `--heading` / `--nav-group-label` by reference, not by deletion:** neither token can be removed. Slate's `--heading` is `#241b33` but its accent stays blue (Resolved scope item 3), and Dark's `--nav-group-label` (`#f0d690`) is a paler gold than its accent. Both tokens stay declared in all four blocks, so AST-2047 AC 4's "same token names" still holds. In the two purple Lights they become `var(--accent-contrast)`, which leaves one source value per block. That is the same pattern Dark already uses for `--heading`.

3. **Verify:**
   - `rg -n "accent-gold" src` is empty, and `rg -c "accent-contrast" src/ui/frontend/src` shows the same total as the old count (63 `var()` uses + 12 declarations).
   - In `src/ui/frontend`: `npx tsc -b --noEmit` and `npm run build` exit 0, and `npm run lint` shows no problem absent before the change.
   - `npx vitest run --config vite.config.ts ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx` passes (see Blast radius for the one stale key).
   - Re-run AST-2047 Stage 2 step 6 check 2 (no stray colours / undefined `var()`). Check 1's Dark-equality compares token **names** against the pre-epic baseline `889c8252f`, so it will flag the renamed Dark tokens. Compare instead with the three names mapped back (`--accent-contrast*` → `--accent-gold*`). Dark values must be identical.
   - Manual: in Light and Light (Parchment), nav group headers, the active nav link with its left border, the selected candidate item, and focus rings are purple. Dark and Slate look unchanged.

### Blast radius

- Every former `--accent-gold*` use changes colour in `light` and `light_parchment`. This covers nav, focus rings, links/labels, the in-flight button, status chips, the column-resize handle, and the hamburger bars. Dark and Slate rendering is unchanged.
- **Tests (Betty's call):** `test_AdminThemeExamples.test.tsx` line 162 lists `"--accent-gold"` among the keys the Lights must pairwise differ on. After the rename that key is undefined in every block. The case still passes (via `--bg-deep`), but the key is stale and should become `--accent-contrast`. Note that `light` and `light_parchment` will now share the same accent value. `docs/test-bible/frontend/root.md` line 45 (`.btn.primary.in-flight` uses `var(--accent-gold)`) and the `pages.md` mentions also need the new name. No other test names these tokens.
- **Canon (Joan's call):** `canon/directives/draft/patt.ui.shared-button-roles.md` (draft) names `--accent-gold`.
- The AST-2049 source-wide guard (every `var(--x)` defined; no hex in `.ts`/`.tsx`) holds only if the rename covers all six files together.

### What must still hold

- AST-2047 AC 3: Dark's **values** are unchanged. Only the three accent names change.
- AST-2047 AC 4: all four blocks declare exactly the same token names, and the Lights still differ pairwise on `--bg-deep`.
- AST-2047 AC 5 / AST-2049 AC 9: no hex or non-black `rgba()` outside token blocks, no `#hex` in `.ts`/`.tsx`, and every `var(--x)` defined in a token block.
- AST-2063: section/page headers stay `#241b33` in all three Lights. Slate keeps its literal value, and light/parchment get it via `var(--accent-contrast)`.
- AST-2064 / AST-2077: grade tokens and Theme Examples option rows are untouched.

### Fix-board — Joan (AST-2076)

[board-joan]  CANON: REVISE
What: pattern.ui.shared-button-roles (draft) — rename `--accent-gold` to `--accent-contrast` and fix in-flight prose (accent is palette-dependent, not always gold) — align draft with global token rename

**Read:** `## Bug: AST-2076` on `origin/sub/AST-2042/AST-2076-light-accent-contrast` — mechanical `--accent-gold*` → `--accent-contrast*` across six frontend files; Light / Light (Parchment) accent values set to the header purple family; `--heading` / `--nav-group-label` alias `--accent-contrast` in those blocks only. Parent **Canon Scope: none.**

**Roster skim:** Touches `App.css` and scoped `.tsx` files (`astral.ui.frontend-file-placement`). No new React-side business rules (`astral.layers.ui-config-driven-business-logic`). No **active** directive in `canon/directives/active/` names `--accent-gold`. The plan’s blast radius flags `canon/directives/draft/patt.ui.shared-button-roles.md` (`pattern.ui.shared-button-roles`, Archie-approved draft): solution shape still says in-flight primary is “Gold (`--accent-gold`)”, which the product rename and Light purple accents will falsify even though behavior still goes through the renamed token in `App.css`.

**Verdict:** Active in-force canon is not contradicted, but the corpus still needs a small draft-pattern update so the token name and palette-dependent accent prose match the ship. That is F3 (`validate-plan` fix mode), not an Archie escalate.

### Review-fix — Radia (AST-2076)

[code-rubric]
**Ticket:** AST-2076
**Publish ref:** `e15b17f6f66df8c1ed8716e5917f3a828a359363` (`origin/sub/AST-2042/AST-2076-light-accent-contrast`)
**Corpus:** `d245392c31f516562e70e3771abcfdd1192de869` (canon tree at publish tip includes Joan F3 draft-pattern doc commit; ticket/parent **Canon Scope:** none)
**Overall:** CLEAN

## Canon scores

Frozen list empty (bug **Citations:** none; parent **Canon Scope:** none). No directive rows to score; not §5.3 ESCALATE. Fix-board Joan **CANON: REVISE** (draft `patt.ui.shared-button-roles`) addressed on sub by `f3186d4c5` (`--accent-contrast` prose + palette-dependent in-flight note) — advisory context only, not a ticket canon row.

## Column diff vs plan stage

no plan-stage scores attached (fix-lane `plan-fix` + fix-board; F3 canon doc on sub).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro] OK** — `test_AdminThemeExamples.test.tsx`: `[bug-repro] AST-2076: in light and light_parchment, the accent and nav group label resolve to the header colour` resolves `var()` chains in parsed token blocks and asserts `--accent-contrast` and `--nav-group-label` equal `--heading` for `light` / `light_parchment` (fails when accents stayed dark gold). Betty also retargeted AC4 pairwise key to `--accent-contrast` (line 162).

**## What must still hold — OK** — Product commit `e15b17f6f`: mechanical rename across six files; Light / Light (Parchment) accent family `#241b33` / hover / dim; `--heading` and `--nav-group-label` alias `var(--accent-contrast)` in those blocks; Dark / Slate values unchanged aside from token names; grade tokens and Theme Examples option/letterless rows untouched in this commit; no `#hex` added in `.tsx`.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sync(dev) carry:** `git diff origin/ftr/AST-2042-user-theme...e15b17f6f` is large (AST-2043, contact, tracker, etc.), but **`git diff origin/dev e15b17f6f -- src/**` differs only on the six AST-2076 files** listed in plan; other `src/**` paths match `origin/dev` (e.g. `candidate.py` 0-line diff). Do not treat sync(dev) blobs as #2076 product scope.
- **Canon on sub:** Only `canon/directives/draft/patt.ui.shared-button-roles.md` differs from dev (+18 lines) — matches Joan F3 / plan blast radius; corpus SHA moves at tip.
- **AC4 nuance:** `light` and `light_parchment` now share the same accent value; Lights still differ pairwise on `--bg-deep` (and `--bg-card`); plan documents shared purple accent as intentional.
- **UAT:** Nav active link, selected candidate, focus rings, in-flight button — visual purple check in Light / Parchment.

## What's solid

- **Plan fidelity (`e15b17f6f`):** Six-file rename; Light purple accent family; alias pattern for `--heading` / `--nav-group-label`; `accent-gold` absent at tip.
- **Stack hygiene vs dev:** Isolated product delta is exactly #2076 scope (+ draft canon doc), not a smuggled fix-lane product commit on top of stale ftr.
- **Tests:** `473ff6bc7` bug-repro + bible renames; AST-2047/2049 guards still in same file.

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | **Normal** (AST-2042 UAT-batch) | → **Review Posted** → fix-lane clean shortcut → **User Testing** (`resolve-child` skipped). |

context_tokens≈16000
[code-rubric] PROCEED (Commit: e15b17f6f) Light accent purple, token rename
```

**Stdout recommendation:** **PROCEED** → **User Testing** after Chuckles posts artifact and moves to Review Posted.

**Review gate (final):** PROCEED — §3h clean-review shortcut, resolve-child skipped.
