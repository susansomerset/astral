# AST-1369 — Pin left-nav logo and candidate chrome (Freeze the Astral Logo and the candidate selection)

**Linear:** [AST-1369](https://linear.app/astralcareermatch/issue/AST-1369/pin-left-nav-logo-and-candidate-chrome-freeze-the-astral-logo-and-the)  
**Parent:** [AST-1361](https://linear.app/astralcareermatch/issue/AST-1361/freeze-the-astral-logo-and-the-candidate-selection)  
**Publish ref:** `sub/AST-1361/AST-1369-pin-left-nav-logo-and-candidate-chrome`

On wide layouts the left nav scrolls as one pane, so the Astral logo and the selected-candidate control scroll out of view. This ticket restructures `NavigationShell` + sidebar CSS so logo and candidate chrome stay pinned at the top of the sidebar while nav groups (and the admin deploy footer / spacer below them) scroll in a dedicated region. Responsive shell behavior from AST-1286 (wide native select, narrow drawer/menu, hamburger/backdrop/close-on-navigate) stays intact. No `NAV_CONFIG`, candidate APIs, or footer redesign.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/NavigationShell.tsx` | Wrap logo + candidate control in pinned chrome; wrap loading/error/groups + admin footer/spacer in a scroll region. No behavior changes to fetch, expand, select, drawer, or candidate menu logic. | ui |
| `src/ui/frontend/src/App.css` | TOC entry `4c`; stop whole-sidebar vertical scroll; pin chrome; give scroll region `flex: 1` + `overflow-y: auto`. Preserve AST-1286 media queries and candidate-menu styles. | ui |

No API, config, `AdminDeployFooter.tsx`, auth, `CandidateContext`, logo asset, pages, or test-tree files.

## Stage 1: Pinned chrome + scrollable nav body

**Done when:** At ≥1024px with enough nav groups expanded that the left nav overflows its height, scrolling the left nav leaves the Astral logo and the candidate control fully visible at the top of the sidebar; the first content that moves under the scroll is the loading/error message or the first `.nav-group`; the admin deploy footer (when shown) or `.nav-footer-spacer` scrolls away with that body and is not sticky. At ≤1023px, hamburger open/close, backdrop dismiss, close-on-navigate, and narrow candidate menu still match today’s shell.

1. In `src/ui/frontend/src/components/NavigationShell.tsx`, keep all existing imports, constants (`NAV_STORAGE_KEY`, `NAV_WIDE_MIN_PX`), helpers, state, effects, and handlers unchanged. Do **not** change `api('/api/nav_config…')`, expand localStorage, `isAdmin` gating, `setSelectedId`, drawer/backdrop/hamburger markup outside the `<nav>`, or `AdminDeployFooter` props/usage.

2. Inside the single `<nav id="app-sidebar" …>`, restructure children to exactly this nesting (one chrome wrapper, one scroll wrapper — do not duplicate logo, candidate, or group trees):

   ```tsx
   <nav
     id="app-sidebar"
     className={"sidebar" + (drawerOpen ? " sidebar--open" : "")}
   >
     <div className="sidebar-chrome">
       <div className="sidebar-logo">
         <img src={astralLogo} alt="Astral" />
       </div>
       {candidates.length > 0 && (
         isWide ? (
           /* existing .sidebar-candidate-select + <select> — unchanged */
         ) : (
           /* existing .sidebar-candidate-menu + toggle + list — unchanged */
         )
       )}
     </div>
     <div className="sidebar-scroll">
       {loading ? (
         <p className="sidebar-loading">Loading...</p>
       ) : error ? (
         <p className="sidebar-error">Failed to load navigation. Check server connection.</p>
       ) : (
         /* existing navGroups.map → .nav-group / NavLink / disabled — unchanged */
       )}
       {isAdmin ? <AdminDeployFooter /> : <span className="nav-footer-spacer" />}
     </div>
   </nav>
   ```

   Class names must be exactly `sidebar-chrome` and `sidebar-scroll` (kebab, `sidebar-` prefix — matches existing sidebar naming).

3. Do **not** move `AdminDeployFooter` / `.nav-footer-spacer` into `sidebar-chrome`. Do **not** add `position: sticky` on the logo or candidate. Pinning is structural (flex + overflow), not sticky.

4. In `src/ui/frontend/src/App.css` TOC (top comment), after `4b. Responsive nav shell (AST-1286)`, add:
   `*  4c. Pinned left-nav chrome (AST-1369)`
   Append `4c`; do not renumber the rest of the TOC.

5. In section `/* === 4. Sidebar === */`, change `.sidebar` so the **nav column itself does not scroll**:
   - Keep `width: 240px`, `background`, `border-right`, `color`, `padding: 0`, `flex-shrink: 0`, `display: flex`, `flex-direction: column`.
   - Replace `overflow-y: auto` with `overflow: hidden`.
   - Do not change width, colors, or border.

6. Immediately after the existing `.sidebar-candidate-select select:focus` rule block (still in section 4, before `.sidebar-loading`), add section:

   ```css
   /* === 4c. Pinned left-nav chrome (AST-1369) === */
   ```

   With these rules:

   ```css
   .sidebar-chrome {
     flex-shrink: 0;
   }

   .sidebar-scroll {
     flex: 1;
     min-height: 0;
     overflow-y: auto;
     display: flex;
     flex-direction: column;
   }
   ```

   - `min-height: 0` is required so the flex child can shrink and scroll inside the `100vh` shell.
   - Keep `.sidebar-logo`, `.sidebar-candidate-select`, `.sidebar-candidate-menu*`, `.sidebar-loading` / `.sidebar-error`, `.nav-group*`, `.nav-link*`, `.nav-footer-spacer`, and `.nav-deploy-footer*` rules where they already live — do not relocate those blocks unless a selector break requires it.
   - Leave `.nav-deploy-footer { margin-top: auto; flex-shrink: 0; … }` as-is. Inside `.sidebar-scroll` that still parks the footer at the bottom of the **scroll region** when groups are short; when groups overflow, the footer scrolls away with them (not pinned). Do **not** add `position: sticky` / `fixed` to `.nav-deploy-footer`.

7. Do **not** edit section `4b` media queries (`max-width: 1023px` / `min-width: 1024px`), hamburger, backdrop, or drawer `transform` rules except if a conflict appears after step 5–6. If the narrow drawer clips the open candidate menu after the restructure: keep the menu markup in `sidebar-chrome` (in-flow list already expands chrome height); do **not** invent a portal. If clipping still happens because `.sidebar { overflow: hidden }`, set `.sidebar-chrome { overflow: visible; }` only — do not restore whole-sidebar `overflow-y: auto`.

8. Do **not** change `NAV_WIDE_MIN_PX`, breakpoint literals, logo asset path, candidate disable rules for non-admin, or any file outside the Files Changed table.

⚠️ **Decision:** Flex chrome + scroll region instead of `position: sticky` on logo/select — sticky fights nested overflow and the existing footer `margin-top: auto` flex pattern; one structural split matches parent “small shell/CSS structure” and §1.3 DRY (no duplicated sticky rules).

⚠️ **Decision:** Admin deploy footer stays inside `.sidebar-scroll` — parent Boundaries explicitly exclude pinning/redesigning that footer; `margin-top: auto` remains a short-list layout aid only.

⚠️ **Decision:** Same DOM structure for wide and narrow — AST-1286 already uses one `<nav>`; pinning is CSS/overflow, so narrow drawer inherits pinned chrome without a second markup path.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1369
**Overall:** APPROVED
**Publish ref:** `sub/AST-1361/AST-1369-pin-left-nav-logo-and-candidate-chrome` @ `e3a12a90578ac83a643ceae93a96d6b8a384df9c`

## Traceability
AC1–5 → Stage 1: restructure `<nav>` into `.sidebar-chrome` (logo + candidate, handlers unchanged) and `.sidebar-scroll` (loading/error/groups + admin footer/spacer); `.sidebar` `overflow: hidden`, `.sidebar-scroll` `flex:1; min-height:0; overflow-y:auto` pins chrome at ≥1024px; ≤1023px hamburger/backdrop/close-on-navigate/candidate-menu paths untouched; `isAdmin` / `setSelectedId` / disable rules untouched.

## Findings

### acceptable
- **Location:** Stage 1 — same DOM wide and narrow  
  **Finding:** Pinning applies on narrow as well as wide (logo/candidate stop scrolling inside the drawer); parent functional scope emphasizes wide viewports; child AC4 tests shell interactions, not narrow logo scroll.  
  **Recommendation:** Accept as structural consequence of one markup path; optional narrow smoke during UAT.

**R6 checklist (summary):** Definition fidelity ✓ — matches AST-1361 chrome-pin intent, respects boundaries (no NAV_CONFIG, candidate APIs, footer pin, asset/breakpoint changes). Layer/config ✓ — ui-only, no new business rules or config. File placement ✓ — existing `NavigationShell.tsx` + `App.css` only, flat components, TOC `4c` append. Patterns ✓ — parent cites no established pinned-chrome pattern; flex+overflow matches “small shell/CSS structure.” DRY ✓ — single structural split vs duplicated sticky rules. Self-assessment ✓ — estimate confirm present; ⚠️ decisions are specific and grounded.

**In-session R3 (not printed per §7):** All 17 universal `orch.*` statutes conform (plan is docs-shaped ui slice; no git/role/pipeline violations). Considered scoped: `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.ui.naming-conventions`, `astral.layers.import-direction` — all **conforms**. Hundreds of other scoped statutes excluded (layers/paths/change_types mismatch — e.g. batch, agent, data, config blocks).

context_tokens≈52000

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1361/AST-1369-pin-left-nav-logo-and-candidate-chrome`
**Product commits:** `8413f4ce` (sidebar-chrome + sidebar-scroll pin)

## QA test manifest

`origin/sub/AST-1361/AST-1369-pin-left-nav-logo-and-candidate-chrome` @ merge-tests → `origin/tests` `54012807ff6850c22a782e8752e911089bd1237e`

1. **Existing coverage (bible-backed):**
   - `tests/component/frontend/components/test_NavigationShell.test.tsx` — baseline groups/badges/candidate select + **AST-1286 responsive shell** (wide select, hamburger/backdrop, close-on-navigate, narrow candidate menu, non-admin lock) — AC4–5 regression
2. **Broken / obsolete:** none — wrappers do not break existing selectors
3. **Gaps (this pass):**
   - `AST-1369 pinned left-nav chrome` → wide chrome/scroll DOM split (logo+select in chrome; groups+footer in scroll)
   - narrow: same split; candidate menu stays in chrome
   - loading/error messages render inside sidebar-scroll, not chrome

**Integration:** `tests/integration/scenarios/test_candidate_nav_api.py` — API-only; no revision.

**Run:**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx
```

**Bible:** `docs/test-bible/frontend/components.md` shasum `29e2c20a771275d7e8335ff50fed59ab9bd7011c`

— Betty
