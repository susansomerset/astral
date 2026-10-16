# AST-2042 — User Theme

<!-- linear-archive: AST-2042 archived 2026-10-16 -->

## Linear archive (AST-2042)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2042/user-theme  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Astral only has one look today: the dark purple palette in `App.css`. Some candidates will find a light screen easier to read for long sessions, and the product should let them choose. This epic adds a per-candidate **Theme** preference on the Candidate Profile, with **Dark** (today's palette, the default) and **Light**. The whole SPA repaints to match. It also adds an admin **Theme Examples** page that renders the same sample UI in every theme side by side. Dark appears there next to three proposed Light variations, so Susan can pick the Light she wants to keep without clicking through the app.

## Functional scope

1. **Theme registry.** One server config lists every palette (id → label + whether it is offered on the profile) and the default (`dark`). Two palettes are profile-selectable: `dark` and `light`. Two more Light alternates are examples-only: they show on Theme Examples but are never offered on the profile. Adding or retiring a palette means one registry entry plus one palette block, with no page code changes.
2. **Theme choice on the profile.** Candidate Profile → Contact Information gains a **Theme** select (Dark / Light). It saves with the existing profile Save. The value is stored on the candidate, and any value not in the registry is rejected.
3. **App repaints to the selected candidate's theme.** After the candidates list loads, the SPA applies the selected candidate's theme to the whole page. A candidate with no stored theme gets Dark. Switching candidates in the admin picker repaints to that candidate's theme, the same way timezone follows the selected candidate today. The login and logged-off screens, and the moment before candidates load, show Dark.
4. **Three proposed Light palettes.** Three distinct Light variations each cover every existing design token (backgrounds, borders, text, accents, CTA, danger, grade dots, confidence bullets) with readable contrast. The first variation *is* `light` (what the profile's "Light" applies today). The other two are the examples-only alternates. When Susan picks a winner, a follow-up ticket moves that palette into `light` and retires the alternates. That follow-up is not part of this epic. Dark stays exactly as it looks today.
5. **No hard-coded colors left behind.** Every UI color that would stay dark-only in Light (literal hex colors in the stylesheet and in inline `style={{…}}` props, plus references to custom properties no token block defines) is moved onto a defined token. Neutral shadows and overlays (`rgba(0,0,0,…)`) stay as they are.
6. **Admin Theme Examples page.** A new admin-only page under **Tools** shows one panel per registered palette, side by side: Dark, Light, and the two Light alternates, each labeled. Each panel renders a fixed sample: nav links, the shared button roles, a short list table, form fields (text / select / toggle), grade dots A–F/X, confidence bullets, a toast, and a modal-style card, all painted in that theme. It is read-only and does not change anyone's stored theme.

**Out of scope:** the Astral Surfer browser extension, generated resume / cover-letter HTML and print output, the env-colored logo band (AST-2040's `logo_background_by_deploy_env`), and any per-admin-user preference storage. The logo is out of scope too: it stays the current asset on its current background in Light. Susan will supply a light-variant logo once the Light scheme is locked.

**Sequencing:** run this after [AST-2040](https://linear.app/astralcareermatch/issue/AST-2040) lands on `dev`. It is in User Testing and edits `config.py` and the sidebar logo chrome. [AST-2041](https://linear.app/astralcareermatch/issue/AST-2041) (Discussion) may touch `ArtifactEditor.tsx`. If both are dispatched together, child #3 runs after it.

## Component scope

* `src/utils/config.py` — **modified** — theme registry and default inside `UI_CONFIG`. A **Theme** select field in `DATA_SHAPES` candidates `detail.profile` Contact Information, with its options built from the registry. A **Theme Examples** item in the `NAV_CONFIG` **Tools** group.
* `src/ui/frontend/src/lib/uiConfig.ts` — **modified** — `UiConfig` type gains the theme registry and default keys.
* `src/ui/frontend/src/App.css` — **modified** — token block becomes the Dark theme (`:root` and the dark theme selector). Three new Light palette blocks (`light` + two alternates) each override every token. New semantic tokens are added where literals or undefined references need one. Every literal color outside the token blocks is moved onto a token or kept as a neutral shadow/overlay. New section styles for the Theme Examples page.
* `src/ui/frontend/src/pages/AdminThemeExamples.tsx` — **new** — admin Theme Examples page.
* `src/ui/frontend/src/routes.tsx` — **modified** — `admin/theme_examples` route wrapped in `AdminRoute`.
* `src/core/candidate.py` — **modified** — rejects a theme value that is not a registry id on candidate data save.
* `src/ui/frontend/src/pages/CandidateProfile.tsx` — **modified** — loads and saves the theme value. Its own inline literal colors move onto tokens.
* `src/ui/frontend/src/contexts/CandidateContext.tsx` — **modified** — applies the selected candidate's theme to the document root.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — inline literal colors onto tokens.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **modified** — inline `#fff` loading/empty text onto a token.
* `src/ui/frontend/src/components/NavigationShell.tsx` — **modified** — one inline literal (nav badge text) onto a token.
* `src/ui/frontend/src/components/ProfileTextPage.tsx` — **modified** — inline `#fff` loading/empty text onto a token.
* `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` — **modified** — undefined `--error` references (with hex fallbacks) onto a defined token.
* `src/ui/frontend/src/components/StateTimeline.tsx` — **modified** — literals and undefined `--accent` onto tokens.
* `src/ui/frontend/src/components/TabbedTextArea.tsx` — **modified** — inline literal color onto a token.
* `src/ui/frontend/src/pages/AdminCostReconciliation.tsx` — **modified** — literals and undefined references onto tokens.
* `src/ui/frontend/src/pages/AdminDataManagement.tsx` — **modified** — undefined `--accent-gold-dim` onto a defined token.
* `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — **modified** — literals and undefined `--success` / `--warning` onto tokens.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — drop the hex fallback on a defined token.
* `src/ui/frontend/src/pages/AdminScheduledQueries.tsx` — **modified** — undefined references and hex fallbacks onto tokens.
* `src/ui/frontend/src/pages/AdminSessionCoverLetter.tsx` — **modified** — inline literal color and hex fallback onto tokens.
* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — **modified** — inline literal colors and hex fallback onto tokens.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` — **modified** — literals and undefined `--color-pass` onto tokens.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — drop the hex fallback on `--danger`.
* `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` — **modified** — inline literal colors onto tokens.
* `src/ui/frontend/src/pages/CompaniesNewList.tsx` — **modified** — inline literal colors onto tokens.
* `src/ui/frontend/src/pages/CompaniesWatchHistory.tsx` — **modified** — undefined `--success` onto a defined token.

No new API route. The theme rides the existing `PUT /api/candidates/<id>/data` and the existing candidates list, and the registry rides `/api/system/ui_config` (it serves `UI_CONFIG` wholesale). `TokenTextarea.tsx` and `AdminAnthropicAdHoc.tsx` stay unchanged because they only use neutral `rgba(0,0,0,…)` shadows. `JobsProcessing.tsx` / `JobsSkipped.tsx` match a naive hex grep only because of the `&#9660;` entity, so they stay unchanged too.

## Technical scope

* `config.py` — new `UI_CONFIG` keys: the theme registry, a dict keyed by palette id (`dark`, `light`, plus two Light alternate ids), each with a label and a profile-selectable flag (true only for `dark` and `light`), and the default theme id (`dark`), plus an assert that the default is a selectable registry key. The profile shape gains one `select` field on top-level candidate-data key `theme`, with options generated from the selectable registry entries, so there is no second list. `NAV_CONFIG` Tools gains one item for `/admin/theme_examples`.
* `uiConfig.ts` — `UiConfig` gains the two optional keys. No new resolver is needed beyond what the page and profile read directly.
* `App.css` — the existing token block is modified so its selector also matches the dark theme attribute. Three new blocks, one per Light palette attribute (`light` and the two alternates), each redefine every token with a visibly distinct Light variation. New semantic tokens are added only where a literal or undefined reference needs one (for example success, warning, text on colored chips, accent-dim). Each literal color in rules outside the token blocks is modified to use a token, except neutral `rgba(0,0,0,…)` shadows/overlays. Each `var(--x, …)` whose `--x` no token block defines is repointed to a defined token. New `.theme-examples-*` styles lay out the side-by-side panels.
* `AdminThemeExamples.tsx` — new page. It reads the theme registry from UI config and renders one labeled panel per id, selectable or not. Each panel carries that theme's attribute, so tokens cascade inside it. The fixed sample in each panel uses the real shared classes (nav link, button roles, list table, form field, grade dots, confidence bullets, toast, modal card), not look-alike markup.
* `routes.tsx` — one new route entry under Admin, wrapped in `AdminRoute`, matching the `NAV_CONFIG` path.
* `candidate.py` — the candidate-data update path gains a validation: when the payload carries `theme`, its value must be a profile-selectable registry id, otherwise it raises `ValueError` (the same shape as the existing pronouns check), which the API already returns as 400.
* `CandidateProfile.tsx` — `editValuesFromCandidate` gains `theme`, read from `candidate_data.theme` and falling back to the served default theme id, so it round-trips through the existing save and dirty-compare. Its inline literal colors (loading/help text, error line) are modified to tokens.
* `CandidateContext.tsx` — a new effect, beside the timezone and tab-title effects, sets the document root's theme attribute from the selected candidate's `candidate_data.theme`. It removes the attribute when there is none, so Dark tokens apply.
* The eighteen remaining component/page files — each inline literal color, each hex fallback inside `var(--x, #…)`, and each undefined custom-property reference is modified to a token that `App.css` defines. No layout or behavior change.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. Of the 21 in-force directives (`canon_clerk.py index`), the only frontend pattern is `patt.artifact.ui-consistency`, which covers artifact editors, and this epic adds no artifact surface. `patt.artifact.manage-catalog` governs new **artifact** keys, and `theme` is a display preference stored as a candidate-data meta key, like `surfer_consent`, not an artifact. Local precedents followed without citing as law: config-served UI values (`UI_CONFIG` → `uiConfig.ts`), the timezone-follows-selected-candidate effect in `CandidateContext`, and the pronouns allowlist check in `candidate.py`.
* **New patterns proposed** — none. (Theme tokens via a root attribute are a stylesheet convention, not a catalog pattern. Flag it if Archie wants it codified.)
* **Applicable statutes** — none. No new route, so `stat.logging.info.api` is not reached. No logging, entity-state, dispatch, or batch surface is touched.

**Canon Scope:** none — locked at Discussion.

## Acceptance criteria

 1. **Registry served.** `GET /api/system/ui_config` returns a theme registry of exactly four ids, `dark`, `light`, and two Light alternates, where only `dark` and `light` are flagged profile-selectable, and the default is `dark`. `python -c "import src.utils.config"` exits 0. **Fail:** a different id count, an alternate flagged selectable, another default, or an import error.
 2. **One list of themes.** The profile shape's Theme select options (`GET /api/shapes/candidates` → `detail.profile[0]`) are exactly Dark and Light, the selectable registry entries. Flipping an alternate's selectable flag locally (reverted) adds it to the select with no other file edited. `rg -n "\"light\"" src/ui/frontend/src` returns no hit added by this epic outside `App.css` selectors. **Fail:** an alternate offered on the profile, or a second hard-coded theme list.
 3. **Profile saves the theme.** On Candidate Profile, choose Light and Save. `GET /api/candidates/<id>` then returns `candidate_data.theme == "light"`, and reloading the page shows Light selected. **Fail:** the value is not persisted or the select resets.
 4. **Bad values rejected.** `PUT /api/candidates/<id>/data` with `{"theme": "neon"}`, or with an examples-only alternate id, returns 400, and the stored theme is unchanged. **Fail:** 2xx, or the value stored.
 5. **App repaints.** With the selected candidate on Light, `document.documentElement` carries the light theme attribute, and `getComputedStyle(document.body).backgroundColor` differs from the Dark value `rgb(15, 11, 24)`. A candidate with no stored theme gets no theme attribute or the dark one, and the body background is `rgb(15, 11, 24)`. **Fail:** no attribute change, or an unchanged background on Light.
 6. **Picker follows the candidate.** As admin, switching from a Light candidate to a Dark candidate in the picker flips the root attribute and body background without a reload. **Fail:** the theme sticks to the previous candidate.
 7. **Dark unchanged.** On Dark, every token in `App.css` resolves to the same value as on `origin/dev` at branch point (compare `getComputedStyle(document.documentElement)` for each token name on both builds). **Fail:** any token value differs.
 8. **Every Light palette covers every token, and they differ.** Each of the three Light blocks defines exactly the same `--*:` name set as the Dark block (script-compared). No two Light blocks are identical: for each pair, `--bg-deep`, `--bg-card`, or `--accent-gold` differs. **Fail:** a missing token in any Light block, or two identical variations.
 9. **No stray colors.** `rg -n "[\"' ,(]#[0-9a-fA-F]{3,8}\b" src/ui/frontend/src --glob '*.{ts,tsx}' --glob '!*.test.*'` returns nothing (HTML entities like `&#9660;` are excluded by the leading character class). In `App.css`, every hex literal, including `var(--x, #…)` fallbacks, sits inside a theme token block. Every `var(--name` in `src/ui/frontend/src` names a property defined in a token block. **Fail:** any hex in a `.ts`/`.tsx`, a hex in an `App.css` rule body, or a reference to an undefined property.
10. **Theme Examples page.** As admin, Tools → Theme Examples opens `/admin/theme_examples` and shows four labeled panels, one per registry id (Dark, Light, and both alternates). Each panel contains a button using the shared primary role, a table row, a select, grade dots A, B, C, D, F, X, and a toast-styled element. The four panels' computed backgrounds are pairwise different. As a non-admin, the nav item is absent and the route redirects like other admin routes. Viewing the page does not change `candidate_data.theme`. **Fail:** a missing panel or sample element, identical panel colors, non-admin access, or a stored-theme change.
11. **Builds clean; no new lint.** In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that is absent on `origin/dev` (diff the problem lists). **Fail:** a non-zero exit or a new lint problem.

## Open questions

none

Resolved (Susan, 2026-10-08): three Light variations on Theme Examples (Functional scope 4 and 6). The picker repaints to the selected candidate's theme (item 3). The logo stays as-is on Light, and Susan supplies a light-variant logo after the scheme is locked (Out of scope).

## Proposed child tickets

#### 1!: **Theme registry, palettes, and Theme Examples page - Ada**

After [AST-2040](https://linear.app/astralcareermatch/issue/AST-2040) lands. Owns all config (registry, profile select field, nav item), the Dark token block plus three Light palette blocks (`light` + two examples-only alternates), the full `App.css` literal sweep, and the admin Theme Examples page, so Susan can compare the three Light variations as soon as this ships. Does not persist or apply a candidate's theme (#2), and does not touch component inline styles (#3).
**Citations:** none — frontend and `UI_CONFIG` / `DATA_SHAPES` / `NAV_CONFIG` values only; no in-force directive reaches these files.
**Scope:** `src/utils/config.py` (new `UI_CONFIG` theme registry dict keyed by palette id — `dark`, `light`, two Light alternates — each with label + profile-selectable flag (true only for `dark`/`light`), default id with assert; profile shape `select` on `theme` with options generated from the selectable entries; `NAV_CONFIG` Tools item `/admin/theme_examples`); `src/ui/frontend/src/lib/uiConfig.ts` (`UiConfig` gains registry + default keys); `src/ui/frontend/src/App.css` (token block also matches the dark attribute; three Light palette blocks (`light` + two alternates) each redefining every token, visibly distinct; new semantic tokens where needed; every literal outside token blocks onto a token except neutral shadows/overlays; undefined `var(--x…)` repointed; `.theme-examples-*` styles); `src/ui/frontend/src/pages/AdminThemeExamples.tsx` (**new** — one panel per registry id carrying that theme's attribute, fixed sample built from real shared classes); `src/ui/frontend/src/routes.tsx` (`admin/theme_examples` in `AdminRoute`).
Estimate: 5

#### 2: **Save and apply the candidate's theme - Hedy**

After #1. Validates and persists `candidate_data.theme` through the existing profile save, and repaints the SPA to the selected candidate's theme (picker-follow like timezone). Does not touch config, `App.css`, or the examples page (#1), or other components' colors (#3).
**Citations:** none — one allowlist check in `candidate.py` on an existing route; no logging/entity/dispatch surface.
**Scope:** `src/core/candidate.py` (candidate-data update rejects a `theme` that is not a profile-selectable registry id with `ValueError`, same shape as pronouns); `src/ui/frontend/src/pages/CandidateProfile.tsx` (`editValuesFromCandidate` gains `theme` from `candidate_data.theme`, defaulting to the served default id; inline literal colors onto tokens); `src/ui/frontend/src/contexts/CandidateContext.tsx` (new effect sets or removes the document root theme attribute from the selected candidate).
Estimate: 2

#### 3: **Move component inline colors onto tokens - Katherine**

After #1 (needs its tokens). If [AST-2041](https://linear.app/astralcareermatch/issue/AST-2041) is in flight, run after it (shared `ArtifactEditor.tsx`). Replaces every inline literal color, hex fallback, and undefined custom-property reference in the listed components/pages with `App.css` tokens, with no layout or behavior change. Does not touch `App.css` (#1) or `CandidateProfile.tsx` (#2).
**Citations:** none — frontend style props only.
**Scope:** `src/ui/frontend/src/components/ArtifactEditor.tsx`, `ContextTextPage.tsx`, `NavigationShell.tsx`, `ProfileTextPage.tsx`, `RepoJsonDivergenceBanner.tsx`, `StateTimeline.tsx`, `TabbedTextArea.tsx`; `src/ui/frontend/src/pages/AdminCostReconciliation.tsx`, `AdminDataManagement.tsx`, `AdminManageCandidates.tsx`, `AdminScheduledActions.tsx`, `AdminScheduledQueries.tsx`, `AdminSessionCoverLetter.tsx`, `AdminSessionResumePaste.tsx`, `AdminTaskPrompts.tsx`, `ArtifactsBaseResumeContent.tsx`, `ArtifactsCompanySearchTerms.tsx`, `CompaniesNewList.tsx`, `CompaniesWatchHistory.tsx` (each inline literal color, each hex fallback inside `var(--x, #…)`, and each undefined custom-property reference onto a token `App.css` defines).
Estimate: 3

**New patterns:** none.

**Monolith check:** Functional scope has 6 items across 3 children. #1 owns items 1, 4, 6 and the stylesheet half of 5. #2 owns items 2 and 3. #3 owns the component half of 5. #2 and #3 both depend on #1 and can run in parallel with each other.

**Scope partition check:** all 26 Component scope files are claimed exactly once. #1 claims `config.py`, `uiConfig.ts`, `App.css`, `AdminThemeExamples.tsx`, and `routes.tsx`. #2 claims `candidate.py`, `CandidateProfile.tsx`, and `CandidateContext.tsx`. #3 claims the remaining 18 component/page files. Every Technical scope item maps to the child that owns its file.

---

## Original brief

Let the user select the theme style for their candidate profile, where the current/default theme is "Dark", and the alternate theme would be "Light".  Propose alternates to the current coloring with a theme example page in the admin navigation menu.

### Comments

#### chuckles — 2026-10-08T23:56:40.742Z
Filed [AST-2077](https://linear.app/astralcareermatch/issue/AST-2077) at Discussion, assigned to you. Confirm the as-is/to-be (including which "three samples" you meant), then reassign it to Chuckles to release it into the fix lane.

#### susan — 2026-10-08T23:55:20.153Z
@chuckles That was my bad.  I've updated the text for the fix.

#### chuckles — 2026-10-08T23:54:50.150Z
@susan — this `[fix]` has no text, so I didn't file it. If it was a double-post of the nav one, nothing to do ([AST-2076](https://linear.app/astralcareermatch/issue/AST-2076)). Otherwise reply here with what's wrong and I'll file it.

#### chuckles — 2026-10-08T23:54:49.520Z
Filed [AST-2076](https://linear.app/astralcareermatch/issue/AST-2076) at Discussion, assigned to you. Confirm the as-is/to-be, then reassign it to Chuckles to release it into the fix lane.

#### susan — 2026-10-08T23:54:07.954Z
\[fix\]  Please include three samples of the compact grade dots as seen on the Recommended Job List.

#### susan — 2026-10-08T23:53:40.603Z
\[fix\]

Oh dear.  That section header font color should be used consistently in nav headers, and selected navigation text and highlight left-border (everywhere the dark yellow is currently used), because I'm still seeing dark yellow in the nav.

#### chuckles — 2026-10-08T23:40:45.543Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **[AST-2063](https://linear.app/astralcareermatch/issue/AST-2063)** | Light themes: header text is dark yellow — use the Dark theme's background purple |
| **[AST-2064](https://linear.app/astralcareermatch/issue/AST-2064)** | Light themes need their own grade-color set, with options on Theme Examples |
| **[AST-2065](https://linear.app/astralcareermatch/issue/AST-2065)** | Theme Examples page never loads (UI config fetched from non-existent /api/system/ui_config) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**[AST-2063](https://linear.app/astralcareermatch/issue/AST-2063)** — _Light themes: header text is dark yellow — use the Dark theme's background purple_
- **Quick check:** re-run the failure you reported for **[AST-2063](https://linear.app/astralcareermatch/issue/AST-2063)**.

**[AST-2064](https://linear.app/astralcareermatch/issue/AST-2064)** — _Light themes need their own grade-color set, with options on Theme Examples_
- **Quick check:** re-run the failure you reported for **[AST-2064](https://linear.app/astralcareermatch/issue/AST-2064)**.

**[AST-2065](https://linear.app/astralcareermatch/issue/AST-2065)** — _Theme Examples page never loads (UI config fetched from non-existent /api/system/ui_config)_
- **Quick check:** re-run the failure you reported for **[AST-2065](https://linear.app/astralcareermatch/issue/AST-2065)**.

Fixes are on `ftr/AST-2042-user-theme` in [PR #267](https://github.com/susansomerset/astral/pull/267) (ftr → dev). Staging picks them up once you merge it.

#### chuckles — 2026-10-08T22:50:02.492Z
Filed [AST-2065](https://linear.app/astralcareermatch/issue/AST-2065) at Discussion, assigned to you. Confirm the as-is/to-be, then reassign it to Chuckles to release it into the fix lane.

#### chuckles — 2026-10-08T22:50:01.348Z
Filed [AST-2064](https://linear.app/astralcareermatch/issue/AST-2064) at Discussion, assigned to you. Confirm the as-is/to-be, then reassign it to Chuckles to release it into the fix lane.

#### chuckles — 2026-10-08T22:50:00.106Z
Filed [AST-2063](https://linear.app/astralcareermatch/issue/AST-2063) at Discussion, assigned to you. Confirm the as-is/to-be, then reassign it to Chuckles to release it into the fix lane.

#### susan — 2026-10-08T22:49:04.781Z
\[fix\]

The Theme Examples page is not loading and not emitting console errors.

#### susan — 2026-10-08T22:48:29.348Z
\[fix\]

The light theme will need a parallel set of grade colors, this set does not appear very well. Please include options in the theme examples page.

#### susan — 2026-10-08T22:46:43.729Z
\[fix\]

Instead of a dark yellow color for header text, use the background purple color from the dark theme.

#### chuckles — 2026-10-08T21:46:22.134Z
@susan — confirmed Betty's finding on `origin/ftr/AST-2042-user-theme`: `system_bp` is `url_prefix="/api"`, so only `/api/ui_config` exists. `uiConfig.ts` still fetches `/api/system/ui_config`, and so does the Theme Examples test mock, which is why the test passes. In a browser, Tools → Theme Examples will sit on "Loading..." (AC 10). `ArtifactEditor.tsx` and `ArtifactsBaseResumeContent.tsx` call the same wrong path, and that bug predates this epic.

Recommended route: I'm packaging the epic for UAT now. When you test, mark this `[bug]` on the parent, and fix-intake files a Bug child for the fix lane: a one-line `uiConfig.ts` fix plus Betty retargeting the mock. If you'd rather it be fixed before you look at UAT at all, say so here and I'll hold.

#### chuckles — 2026-10-08T21:25:54.864Z
AST-2049 estimate 3→2 — plan is 49 mechanical token swaps, no new tokens or logic.

#### betty — 2026-10-08T21:14:09.861Z
@susan — product bug in AST-2047 (already on ftr): `src/ui/frontend/src/lib/uiConfig.ts` `loadUiConfig` fetches `/api/system/ui_config`, but Flask only serves `/api/ui_config` (`system_bp` url_prefix `/api`). At runtime `getUiConfig()?.themes` is undefined, so Tools → Theme Examples stays on "Loading..." (AC6 fails in a browser). Pre-existing since AST-647 for other `getUiConfig()` readers too. Hedy's AST-2048 plan spotted it; my AST-2047 page test mocked the wrong URL and missed it. Recommendation: one-line fix in `uiConfig.ts` (→ `/api/ui_config`) as an AST-2042 bug before UAT, plus I retarget the AST-2047 test mock. Your call on routing.

#### chuckles — 2026-10-08T20:58:59.536Z
AST-2048 plan surfaced a likely AST-2047 bug: `src/ui/frontend/src/lib/uiConfig.ts` fetches `/api/system/ui_config`, but `system_bp` is prefixed `/api`, so only `/api/ui_config` exists — `getUiConfig()` gets the SPA HTML and never sees `themes`/`default_theme` (Theme Examples page likely stuck on Loading). Pre-dates AST-647 (`ArtifactsBaseResumeContent.tsx` has the same path). AST-2048 does not depend on it.

#### chuckles — 2026-10-08T18:03:56.556Z
@susan

1. **"Propose alternates":** should Theme Examples show only Dark (current) next to **one** proposed Light palette, or several Light candidates (for example 2–3 variations) so you pick one, with only the winner shipping as "Light"? Default if unanswered: one Light palette.
2. **Admin view:** when you switch candidates in the picker, should the UI repaint to that candidate's theme (as drafted, same as timezone), or should admins always see their own fixed theme? An admin-owned preference would need storage that doesn't exist today, because a theme lives on a candidate.
3. **Logo in Light:** the logo is gold on a transparent background, and "Career Match" is pale gold, low contrast on a light sidebar. In production (no env color), should the logo band stay dark in the Light theme, or should we accept it on light and maybe add a light-variant logo asset later?

---

_Implementation detail may live in git history on `origin/dev`._
