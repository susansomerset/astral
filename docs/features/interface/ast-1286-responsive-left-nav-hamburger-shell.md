# AST-1286 — Responsive left-nav hamburger shell (Make left nav responsive)

**Linear:** [AST-1286](https://linear.app/astralcareermatch/issue/AST-1286/responsive-left-nav-hamburger-shell-make-left-nav-responsive)  
**Parent:** [AST-1284](https://linear.app/astralcareermatch/issue/AST-1284/make-left-nav-responsive)  
**Publish ref:** `sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell`

On viewports below 1024px the always-visible left sidebar steals horizontal space. This ticket makes `NavigationShell` collapse that chrome into a hamburger + overlay drawer (backdrop dismiss, close after navigate) while keeping the same config-resolved nav groups, admin deploy footer rules, and desktop always-visible sidebar at ≥1024px. Candidate pick in the drawer uses a checked list/submenu; desktop keeps today's native select.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/NavigationShell.tsx` | Wide/narrow shell state; hamburger; drawer open/close; backdrop; close on pathname change; narrow checked candidate list; desktop select unchanged | ui |
| `src/ui/frontend/src/App.css` | TOC entry + responsive shell / drawer / backdrop / hamburger chrome / candidate-list styles under `@media (max-width: 1023px)` | ui |

No API, config, auth, `NAV_CONFIG`, `AdminDeployFooter.tsx`, or page-layout files.

## Stage 1: Collapse shell, hamburger, overlay drawer, backdrop, close-on-navigate

**Done when:** At a viewport width of 1023px or less, the left nav is not a fixed flex column; a hamburger control opens an overlay drawer over content; tapping the backdrop closes the drawer without changing the route; choosing an enabled `NavLink` navigates and leaves the drawer closed so `.content` is full width; at 1024px and above the sidebar remains the always-visible column as today (hamburger chrome not required for normal use).

1. In `src/ui/frontend/src/components/NavigationShell.tsx`, add imports: `useLocation` from `react-router-dom` (keep existing `NavLink`, `Outlet`); keep all other existing imports.

2. At module scope (above the component), add:
   ```ts
   /** Viewport width at/above which the left sidebar stays a persistent column (AST-1286). */
   const NAV_WIDE_MIN_PX = 1024
   ```
   Use this constant only for `matchMedia` / JS behavior. CSS uses the matching media query in Stage 1 step 10 (literal `1023px` max-width). Do not invent a config.py key for this chrome breakpoint.

3. Inside `NavigationShell`, after existing hooks, add:
   - `const location = useLocation()`
   - `const [drawerOpen, setDrawerOpen] = useState(false)`
   - `const [isWide, setIsWide] = useState(() =>
       typeof window !== "undefined"
         ? window.matchMedia(`(min-width: ${NAV_WIDE_MIN_PX}px)`).matches
         : true
     )`

4. Add a `useEffect` that subscribes to `window.matchMedia(\`(min-width: ${NAV_WIDE_MIN_PX}px)\`)`:
   - On mount and on `change`, call `setIsWide(mq.matches)`.
   - When `mq.matches` becomes `true`, also `setDrawerOpen(false)` so a resize to desktop never leaves an orphan open drawer.
   - Cleanup: `mq.removeEventListener("change", handler)` (or `removeListener` only if the environment lacks `addEventListener` on MediaQueryList — prefer the modern API).

5. Add a `useEffect` depending on `[location.pathname]` that calls `setDrawerOpen(false)` whenever the pathname changes (covers enabled nav destination clicks and any other in-app route change).

6. Restructure the JSX under `.shell` to this shape (keep `UserPromptProvider` wrapper). Do **not** duplicate nav group markup — one `<nav>` only:
   ```tsx
   <div className="shell">
     <button
       type="button"
       className="nav-hamburger"
       aria-label={drawerOpen ? "Close navigation" : "Open navigation"}
       aria-expanded={drawerOpen}
       aria-controls="app-sidebar"
       onClick={() => setDrawerOpen(o => !o)}
     >
       {/* three horizontal bars via CSS, or a minimal unicode ☰ — prefer CSS bars in .nav-hamburger for consistency */}
     </button>
     {drawerOpen && !isWide && (
       <div
         className="nav-backdrop"
         aria-hidden="true"
         onClick={() => setDrawerOpen(false)}
       />
     )}
     <nav
       id="app-sidebar"
       className={"sidebar" + (drawerOpen ? " sidebar--open" : "")}
     >
       {/* existing logo, candidate select (Stage 1 keeps native select), loading/error/groups, admin footer/spacer — unchanged behavior */}
     </nav>
     <main className="content">
       <Outlet />
     </main>
   </div>
   ```
   Candidate select, nav fetch, expand/collapse, `NavLink` / disabled spans, and `{isAdmin ? <AdminDeployFooter /> : <span className="nav-footer-spacer" />}` stay inside this single `<nav>` with the same logic as today.

7. Do **not** change `api('/api/nav_config…')`, expand localStorage key, `AdminDeployFooter`, or candidate context APIs in this stage.

8. In `src/ui/frontend/src/App.css` TOC (top comment), add a line after `4. Sidebar`:
   `*  4b. Responsive nav shell (AST-1286)`
   Renumber is optional — append `4b` rather than renumbering the whole TOC.

9. After the existing `.sidebar` / sidebar child rules (end of section 4, before `/* === 5. Nav Groups`), add section `/* === 4b. Responsive nav shell (AST-1286) === */` with **base** (all viewports) rules:
   - `.nav-hamburger` — visually hidden by default (`display: none`). Style when shown: fixed `top`/`left`, z-index above content but below open drawer (e.g. button `z-index: 40`, backdrop `30`, open sidebar `50`), ~40×40 hit target, uses design tokens (`--bg-card`, `--border`, `--text-primary` / `--accent-gold`). Three bar spans as children if using CSS bars: empty `<span>`×3 inside the button in TSX.
   - `.nav-backdrop` — `display: none` by default.
   - Do not change desktop `.sidebar { width: 240px; … }` rules outside the media query.

10. In the same `4b` section, add:
    ```css
    @media (max-width: 1023px) {
      /* matches NAV_WIDE_MIN_PX - 1 */
    }
    ```
    Inside that block:
    - `.nav-hamburger { display: flex; … }` (visible).
    - `.shell {` keep flex; `.content` must take full width (sidebar not in document flow as a column).
    - `.sidebar` becomes a fixed overlay drawer: `position: fixed; top: 0; left: 0; height: 100vh; width: 240px; z-index: 50; transform: translateX(-100%); transition: transform 0.2s ease;` (or equivalent). When `.sidebar.sidebar--open`, `transform: translateX(0)`.
    - `.nav-backdrop` when present: `display: block; position: fixed; inset: 0; z-index: 40; background: rgba(0,0,0,0.45);` (token-adjacent opacity is fine; no new purple glow).
    - `.content` — add top padding (e.g. `padding-top: 52px`) so the hamburger does not cover page chrome; do **not** redesign page internals.

11. At `@media (min-width: 1024px)` (or by relying on base rules): ensure `.nav-hamburger` and `.nav-backdrop` stay hidden/non-interactive, `.sidebar` keeps today's static column behavior, and `.sidebar--open` has no layout effect (drawer class is inert on wide viewports). Prefer: wide rules reset `position`/`transform` on `.sidebar` so a leftover `sidebar--open` class cannot break desktop.

⚠️ **Decision:** One `<nav>` toggled between column and overlay via CSS + `sidebar--open`, not two copies of the nav tree — honors §1.3 DRY and keeps expand-state / nav fetch shared.

⚠️ **Decision:** Breakpoint literal `1024` / `1023` lives in TS constant + CSS media query with cross-comments; not `config.py` — this is presentation chrome, not business/config-driven eligibility (`astral.layers.ui-config-driven-business-logic` stays on `/api/nav_config`).

⚠️ **Decision:** Proposed `pattern.ui.responsive-nav-shell` is followed in behavior per parent Architectural definition; this ticket does **not** add a canon pattern markdown file (Archie approval before catalog law).

## Stage 2: Narrow-mode checked candidate list (desktop select unchanged)

**Done when:** Below 1024px, the drawer shows a candidate control that is a checked list/submenu (selected candidate visually marked); admin can change candidate; non-admin cannot change candidate (same rules as today's disabled select). At ≥1024px the native `<select>` remains exactly as today. Nav groups, disabled items, and admin footer visibility are unchanged in both modes.

1. In `NavigationShell.tsx`, add local state for the narrow candidate submenu only:
   ```ts
   const [candidateMenuOpen, setCandidateMenuOpen] = useState(false)
   ```
   When `drawerOpen` becomes `false` or `isWide` becomes `true`, set `candidateMenuOpen` to `false` (same effects as Stage 1 or a small dedicated effect).

2. Replace the candidate block currently gated by `candidates.length > 0` with branching on `isWide`:

   **Wide (`isWide === true`):** keep the existing markup:
   ```tsx
   <div className="sidebar-candidate-select">
     <select
       value={selectedId ?? ""}
       disabled={!isAdmin}
       onChange={e => isAdmin && setSelectedId(e.target.value)}
     >
       {candidates.map(/* same label logic as today */)}
     </select>
   </div>
   ```

   **Narrow (`isWide === false`):** render a checked list/submenu instead of `<select>`:
   - Wrapper: `div.sidebar-candidate-menu`
   - Toggle button (type=`button`, class `sidebar-candidate-menu-toggle`): label = current candidate display name (same `[first, last].filter(Boolean).join(" ") || astral_candidate_id` as option labels today); `aria-expanded={candidateMenuOpen}`; `onClick` toggles `candidateMenuOpen`. Always allow open/close for reading the list; selection rules are on the rows.
   - When `candidateMenuOpen`, render `ul.sidebar-candidate-menu-list` of `li` > `button` (type=`button`) per candidate:
     - Text: same label as desktop options.
     - Selected row: add class `is-selected` and a visible check mark character `✓` (or CSS `::before`) before/after the label.
     - `onClick`: if `isAdmin`, call `setSelectedId(c.astral_candidate_id)` then `setCandidateMenuOpen(false)` (leave drawer open — only pathname close closes the drawer). If `!isAdmin`, do not call `setSelectedId` (no-op); rows may use `disabled={!isAdmin}` so non-admins cannot change candidate, matching desktop `disabled={!isAdmin}` on the select.
   - Do not call any new API; `setSelectedId` remains the CandidateContext gate.

3. In `App.css` section `4b`, add styles for `.sidebar-candidate-menu`, `.sidebar-candidate-menu-toggle`, `.sidebar-candidate-menu-list`, button rows, and `.is-selected` using existing tokens (`--bg-deep`, `--border`, `--accent-gold`, `--text-primary`). Keep the list visually inside the drawer width (240px). No cards, no pill clusters.

4. Confirm `AdminDeployFooter` / `nav-footer-spacer` remain the sole admin/non-admin footer branch inside the shared `<nav>` (satisfies AC3/AC7 with no file change to `AdminDeployFooter.tsx`).

5. Manually verify against acceptance criteria (builder checklist — not new product files):
   - <1024: no fixed sidebar column; hamburger opens drawer; backdrop dismiss; checked candidate list; nav click closes drawer; disabled items still disabled.
   - ≥1024: persistent sidebar + native select; no hamburger required.
   - Non-admin: no deploy footer; cannot change candidate in either mode.

⚠️ **Decision:** Native `<select>` stays on wide viewports (AC6 “including current candidate select”); checked list is narrow-only so desktop UAT does not change control type.

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on the epic worktree; publish each stage to `origin/sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell`. Do not edit `NAV_CONFIG`, auth, page layouts, or `tests/` / `docs/test-bible/**`. On ambiguity or codebase drift, stop and comment on the **parent** [AST-1284](https://linear.app/astralcareermatch/issue/AST-1284/make-left-nav-responsive) with the Stage blocked format from plan-child.

## Self-Assessment

**Scope:** `Single-Component` — only `NavigationShell.tsx` and `App.css` (shell presentation); no API/core/data.

**Conf:** `high` — AC and parent architectural definition pin breakpoint, overlay drawer, backdrop, checked list, and desktop parity; existing shell already owns nav fetch, expand memory, and admin footer gating.

**Risk:** `Medium` — nav is the app chrome; a broken drawer close or desktop regression would block every route, but blast radius stays in the shell CSS/component.

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | One nav tree; shared expand/fetch state |
| §2.1 config | No new config key for CSS breakpoint (chrome only); nav eligibility stays `/api/nav_config` |
| §2.4 / §2.6 | N/A — no batch or state machine |
| §3.3 imports | Frontend-only; no layer violations |
| §3.5 placement / naming | Components flat; styles in `App.css` with TOC `4b`; PascalCase component file unchanged |
| `astral.standards.in-scope-only` | No page mobile redesigns; no NAV_CONFIG edits |
| `astral.layers.ui-config-driven-business-logic` | No new business rules in React |
| Proposed `pattern.ui.responsive-nav-shell` | Behavior implemented; canon file not added |

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell`  
**Product commits:** `74304164` (hamburger overlay drawer + CSS shell), `ac099886` (narrow checked candidate list)
