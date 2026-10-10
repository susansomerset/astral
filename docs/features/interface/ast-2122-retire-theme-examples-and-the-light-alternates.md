# AST-2122 — Retire Theme Examples and the Light alternates

- **Parent:** [AST-2100](https://linear.app/astralcareermatch/issue/AST-2100) — Light theme: replace grade colours with "Bright + ring" palette
- **Ticket:** [AST-2122](https://linear.app/astralcareermatch/issue/AST-2122)
- **Publish ref:** `origin/sub/AST-2100/AST-2122-retire-theme-examples`
- **Canon Scope:** none (locked at Discussion). No directive applies to these files.

The Bright + ring palette has been picked, so the comparison scaffolding goes. This ticket removes the Tools → Theme Examples screen end to end: its `NAV_CONFIG` item, its route, the page, the `theme_example_grade_sets` candidate rows, and the UI config type that described them. It also removes the examples-only `light_parchment` and `light_slate` registry entries, which leaves `dark` and `light` as the only palettes. `App.css` is not touched. The alternate theme blocks, the §16 `.theme-examples*` rules and their comments belong to [AST-2123](https://linear.app/astralcareermatch/issue/AST-2123). Tests and the test bible belong to Betty (`qa-child`).

## Codebase facts the plan relies on (verified at branch tip `266642874`)

- `sync-child.sh` exited 0. `origin/ftr/AST-2100` is not on origin yet, so the script skipped it.
- `UI_CONFIG["themes"]` is at `src/utils/config.py:6043–6051`. Its comment (`:6043–6045`) says that ids that are not `profile_selectable` "only appear on Tools -> Theme Examples".
- `UI_CONFIG["theme_example_grade_sets"]` is at `config.py:6054–6073`: a 3-line comment (`:6054–6056`) and then the `deep` / `soft` / `classic` dict, which closes at `:6073` just before `UI_CONFIG`'s closing `}` at `:6074`.
- The `default_theme` assert (`config.py:6075–6078`) needs `dark` to stay registered and `profile_selectable`. It does, so the assert holds unchanged.
- `NAV_CONFIG` Tools group (`config.py:6169–6181`): the Theme Examples item is the last item (`:6179`). The other six items stay unchanged.
- `src/ui/frontend/src/lib/uiConfig.ts`: `GradeSetEntry` and its doc comment are on lines 6–7. `UiConfig.theme_example_grade_sets?` and its doc comment are on lines 19–20. `GradeSetEntry` is referenced nowhere else in `src` (`git grep GradeSetEntry -- src` only hits `uiConfig.ts`).
- `src/ui/frontend/src/routes.tsx`: the import is on line 71 and the route on line 150. With the route gone, `/admin/theme_examples` falls through to the catch-all `{ path: "*", element: <JobsHomeRedirect /> }`, so the page no longer renders (AC 8).
- `src/ui/frontend/src/pages/AdminThemeExamples.tsx` is the only `src` consumer of `theme_example_grade_sets`.
- `tsconfig.app.json` has `"include": ["src"]`, so deleting the page does **not** break `tsc` even though `tests/component/frontend/pages/test_AdminThemeExamples.test.tsx` still imports it. That test fails under vitest until Betty deletes it at Code Complete. This is expected.
- `GET /api/ui_config` returns `{**UI_CONFIG, ...}` and `GET /api/nav_config` serves `NAV_CONFIG`, so removing the keys and the item needs no API change.
- After this ticket, `git grep` for the AC 8 / AC 9 terms over `src` hits only `src/ui/frontend/src/App.css`. Those hits are [AST-2123](https://linear.app/astralcareermatch/issue/AST-2123)'s, as the ticket allows.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Remove `light_parchment` / `light_slate` from `UI_CONFIG["themes"]`; rewrite the registry comment; delete `UI_CONFIG["theme_example_grade_sets"]` and its comment; remove the Theme Examples item from `NAV_CONFIG` Tools | utils |
| `src/ui/frontend/src/lib/uiConfig.ts` | Delete `GradeSetEntry` and the `theme_example_grade_sets?` field (with their doc comments) | ui (lib) |
| `src/ui/frontend/src/routes.tsx` | Delete the `AdminThemeExamples` import and the `admin/theme_examples` route | ui |
| `src/ui/frontend/src/pages/AdminThemeExamples.tsx` | Delete the file | ui (page) |

`tests/component/frontend/pages/test_AdminThemeExamples.test.tsx`, `tests/component/utils/test_config.py` and the three bible pages are in this ticket's Scope, but they belong to **Betty** (`qa-child`). The engineer does not touch them (test-tree ban).

## Stage 1: Retire Theme Examples and the Light alternates

**Done when:** `GET /api/ui_config` lists only `dark` and `light` under `themes` and has no `theme_example_grade_sets` key. `GET /api/nav_config` (admin) shows six Tools items, ending with Cover Letter Paste. `/admin/theme_examples` redirects to the jobs home. The AC 8 / AC 9 greps over `src` hit only `App.css`.

1. In `src/utils/config.py`, replace the three registry comment lines above `"themes": {` (currently `:6043–6045`) with exactly:

   ```python
       # AST-2042: theme registry — palette id -> label + whether the profile Theme select offers it.
       # Each id needs a matching [data-theme="<id>"] block in App.css.
       # Adding/retiring a palette = one entry here + one CSS block.
   ```

2. In `src/utils/config.py` `UI_CONFIG["themes"]`, delete these two lines and nothing else:

   ```python
           "light_parchment": {"label": "Light (Parchment)", "profile_selectable": False},
           "light_slate": {"label": "Light (Slate)", "profile_selectable": False},
   ```

   `dark` and `light` stay byte-identical, as does the `profile_selectable` flag on both. Leave the `default_theme` line, its comment and the assert after `UI_CONFIG` unchanged.

   ⚠️ **Decision:** Keep `profile_selectable` even though both remaining ids are `True`, per the parent Technical scope ("The `profile_selectable` flag stays"). Do not simplify the profile select generator or the assert.

3. In `src/utils/config.py`, delete the whole `theme_example_grade_sets` block: the three `# AST-2064: …` / `# Each set's tokens …` / `# Retire a candidate …` comment lines, and the `"theme_example_grade_sets": { … },` entry through its closing `},` (currently `:6054–6073`). After the deletion, the line before `UI_CONFIG`'s closing `}` is `"default_theme": "dark",`.

4. In `src/utils/config.py` `NAV_CONFIG`, in the `Tools` group, delete this line and nothing else:

   ```python
               {"label": "Theme Examples", "path": "/admin/theme_examples"},
   ```

5. In `src/ui/frontend/src/lib/uiConfig.ts`, delete these two lines (currently 6–7):

   ```ts
   /** AST-2064: examples-only grade-color candidate; tokens are CSS custom properties (e.g. "--grade-a") -> color. */
   export interface GradeSetEntry { label: string; tokens: Record<string, string> }
   ```

   Then delete these two lines from `UiConfig` (currently 19–20):

   ```ts
     /** AST-2064: grade-color candidates rendered as rows on Theme Examples. */
     theme_example_grade_sets?: Record<string, GradeSetEntry>
   ```

   `ThemeEntry`, `themes?` and `default_theme?` stay unchanged.

6. In `src/ui/frontend/src/routes.tsx`, delete line 71, `import AdminThemeExamples from "./pages/AdminThemeExamples"`, and the route line `{ path: "admin/theme_examples", element: <AdminRoute><AdminThemeExamples /></AdminRoute> },` (currently 150). Leave the blank line and the `// Catch-all` comment that follow it in place.

7. Delete `src/ui/frontend/src/pages/AdminThemeExamples.tsx` with `git rm`.

8. Compile and lint (all must pass before commit):
   - `python3 -m py_compile src/utils/config.py`
   - `python3 -c "import src.utils.config"` (run from the repo root; the `default_theme` assert runs at import)
   - `cd src/ui/frontend && npx tsc -b --noEmit && npx tsc --noEmit` (exit 0 each)
   - `cd src/ui/frontend && npx eslint src/routes.tsx src/lib/uiConfig.ts` (exit 0)

9. Verify the greps (expected: only `src/ui/frontend/src/App.css` lines):
   - `git grep -n -i -e theme_examples -e ThemeExamples -e theme-examples -e 'Theme Examples' -e theme_example_grade_sets -- src`
   - `git grep -n -e light_parchment -e light_slate -- src`
   - `git grep -n GradeSetEntry -- src` → no output.

   Any hit outside `App.css` → stop and comment on the parent (execution contract).

10. Commit only the four files: `git commit -m "code(AST-2122): retire Theme Examples page and Light alternates"`, then `git push origin HEAD:sub/AST-2100/AST-2122-retire-theme-examples`.

## Notes for qa-child (Betty) — test-scope gap, not engineer work

This ticket's Scope names only `test_AdminThemeExamples.test.tsx` and `test_config.py` under `tests/`. At tip `266642874`, four more test files reference the retired ids. AC 9's `git grep … -- src tests` will hit them, and one will **fail**:

| File | Line | Effect after this ticket |
|------|------|--------------------------|
| `tests/component/ui/api/test_api_system.py` | 75–76 | **Fails**: asserts the four-id set and the `light_slate` entry |
| `tests/component/core/test_candidate.py` | 352 | Still passes (the ids are now invalid anyway), but it is an AC 9 grep hit |
| `tests/component/ui/api/test_api_candidate.py` | 290 | Still passes, but it is an AC 9 grep hit |
| `tests/component/frontend/components/test_NavigationShell.test.tsx` | 390 | Still runs, but it is an AC 9 grep hit |

Betty and Chuckles need to decide whether these files join the test scope. The engineer does not edit them.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate — round 1

[plan-rubric]
**Ticket:** AST-2122
**Overall:** REVISE
**Corpus:** c04b07deda8f5a750afd473ec847d06ed2207065
**Publish ref:** `origin/sub/AST-2100/AST-2122-retire-theme-examples` @ `033044a705c05ca051ad9d11f552dae0b59b8793`

## Canon scores

_(empty — parent and child Canon Scope locked **none** at Discussion; no directive ids to score.)_

## Traceability

AC8→Stage 1 (steps 1–7, 9) + Betty in-scope tests/bible; AC9→Stage 1 (config/ui_config) + Betty `test_config.py` only — **four other test files still violate AC9 grep and `test_api_system.py` fails runtime** (not in Scope); AC10→Stage 1 step 8.

## Findings

### fix-now

- **Location:** Child AC 9; plan `## Notes for qa-child (Betty)`; ticket `## Scope` (tests)
- **Finding:** AC 9 requires `git grep -n -e light_parchment -e light_slate -- src tests` with **no** hits (App.css carve-out applies only under `src`, not `tests`). After engineer Stage 1, grep still hits `tests/component/ui/api/test_api_system.py`, `tests/component/core/test_candidate.py`, `tests/component/ui/api/test_api_candidate.py`, and `tests/component/frontend/components/test_NavigationShell.test.tsx`. `test_api_system.py` also **fails** asserting the four-theme registry. Ticket Scope names only `test_AdminThemeExamples.test.tsx` (delete) and `test_config.py` (modify); the plan flags the gap but leaves Betty/Chuckles to “decide” without adding those files to Scope or Betty stages—so the frozen child AC cannot be met at User Testing.
- **Recommendation:** Before Plan Approved, extend this child’s `## Scope` and the plan (Files Changed + explicit Betty/`qa-child` steps) to cover all four files—or repartition with a sibling ticket that lands **before** UT on AST-2122. Do not approve a plan whose stated AC 9 grep is known to fail outside `App.css`.

### discuss

- **Location:** Plan `## Notes for qa-child` vs workflow
- **Finding:** Honest gap documentation is good; approval still needs a **committed** test footprint, not an open decision.
- **Recommendation:** Chuckles closes the decision in the plan doc (same publish ref) when Scope is amended.

### acceptable

- **Location:** Boundaries (`App.css` → AST-2123); engineer-only four product files; `test_every_registry_id_has_an_app_css_block` interim green
- **Finding:** Matches parent partition and ticket boundaries; interim CSS/registry mismatch is documented in parent/child notes.
- **Recommendation:** None.

- **Location:** Canon Scope none
- **Finding:** Aligns with parent Architectural definition (“Applicable statutes: none”); not a missing Canon Scope escalate case.
- **Recommendation:** None.

context_tokens≈18500
