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
