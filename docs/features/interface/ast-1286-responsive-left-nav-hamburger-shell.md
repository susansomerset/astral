<!-- linear-archive: AST-1286 archived 2026-08-19 -->

## Linear archive (AST-1286)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1286/responsive-left-nav-hamburger-shell-make-left-nav-responsive  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1284 — Make left nav responsive  
**Blocked by / blocks / related:** parent: AST-1284; related: AST-1273; related: AST-1166

### Description

## What this implements

Owns NavigationShell responsive behavior end-to-end: collapse below 1024px, hamburger + overlay drawer with backdrop dismiss, drawer carrying today's sidebar contents (checked candidate list/submenu, nav groups, admin footer), post-navigate close, and unchanged always-visible sidebar at ≥1024px. Does not own page-level mobile redesigns or nav-config content changes.

## In scope

- [X] `astral.ui.frontend-file-placement` — shell/CSS stay in `src/ui/frontend/src/components/NavigationShell.tsx` and `src/ui/frontend/src/App.css`
- [X] `astral.ui.naming-conventions` — existing PascalCase component / snake_case routes unchanged
- [X] `astral.layers.ui-config-driven-business-logic` — nav visibility/enablement stays `/api/nav_config`; no new business rules in React
- [X] `astral.standards.in-scope-only` — shell responsiveness only
- [X] `astral.standards.dry-and-focused-functions` — single shared `<nav>` tree (column vs overlay), not duplicated markup

## Considered but excluded

- [X] `pattern.ui.admin-endpoint` — no new admin HTTP surface; deploy footer data sources unchanged (`AdminDeployFooter` / existing API)
- [X] `astral.config.config-source-of-truth` / new `config.py` breakpoint key — 1024px is presentation chrome (TS constant + CSS media query), not business eligibility
- [X] proposed `pattern.ui.responsive-nav-shell` citation — dropped from In scope until Archie authors + approves a canon file under `canon/patterns/**` (behavior already shipped; not catalog law)
- [X] Canon file for `pattern.ui.responsive-nav-shell` — Archie approval before catalog law; this ticket implements parent-defined behavior only
- [X] NAV_CONFIG / nav group labels / routes / badges — out of bounds
- [X] Page-level mobile redesigns, tables, modals — out of bounds
- [X] Auth / who may change candidate / admin deploy-footer data sources — out of bounds
- [X] [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency) button consistency, [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page) Recommended page — related, not owned

## Acceptance criteria

- [X] Below 1024px width, the persistent left sidebar is not occupying a fixed column; a hamburger control is visible and opens an overlay drawer over content.
- [X] Backdrop tap dismisses the open drawer without navigating away.
- [X] The open drawer shows the same nav groups/items Susan sees on desktop for the same candidate (including disabled items as disabled), plus admin deploy footer for admins only.
- [X] From the open drawer, Susan can select a different candidate via a checked list/submenu; the selected candidate is visually marked; admin/non-admin selection rules match desktop.
- [X] Choosing an enabled nav destination navigates successfully and leaves the content area usable at full width (drawer closed).
- [X] At 1024px and above, the left sidebar is always visible as today (including current candidate select); hamburger collapse is not required for normal use.
- [X] Non-admin sessions still omit the admin deploy footer in both desktop and collapsed modes.

## Boundaries

- [X] Does not redesign nav group labels, routes, badges, or NAV_CONFIG content.
- [X] Does not redesign individual page layouts, tables, or modals for mobile.
- [X] Does not change auth rules, who may change candidate, or admin deploy-footer data sources.
- [X] Does not own [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency) or [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page).

## Notes for planning

Breakpoint is 1024px; overlay drawer; backdrop dismiss; checked candidate list in drawer; desktop native select unchanged. Proposed pattern needs Archie approval before treated as catalog law.

## Git branch (authoritative)

`sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell` — ignore Linear `gitBranchName`.

### Comments

#### radia — 2026-08-08T20:26:56.678Z
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1286
**Publish ref:** `sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell` @ `8441b2257d324973e7e8737b4d5c2283ac52c9b4`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|---|---|---|---|
| orch.git.betty-merge-tests-one-sha | universal | conforms | exactly one `merge-tests(AST-1286): origin/tests 5a98fb36...` commit for one `origin/tests` SHA |
| orch.git.commit-vocabulary | universal | conforms | only `docs()`/`code()`/`test()`/`merge-tests()` used; no `feat()`/`fix()` |
| orch.git.flow-direction-inviolable | universal | conforms | tests→sub via merge-tests only; no tests↔dev crossing |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1284/AST-1286-...` matches child-under-parent topology |
| orch.git.merge-on-checkout | universal | conforms | sub tip's merge-base with dev/ftr is dev HEAD itself — already current |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear commit history, no rebase/cherry-pick evidence |
| orch.git.no-dev-agent-branches | universal | conforms | branch is `sub/AST-1284/...`, not agent-named |
| orch.git.one-epic-worktree-per-parent | universal | conforms | reviewed from `astral-AST-1284/` (parent AST-1284) |
| orch.git.three-permanent-branches | universal | conforms | `origin/dev`, `origin/main`, `origin/tests` all present |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no unresolved product-decision bypass found |
| orch.pipeline.plan-is-bible | universal | conforms | diff matches Stage 1/2 plan steps (hamburger/drawer/backdrop/close-on-nav; checked candidate list) |
| orch.pipeline.project-scoped-queues | universal | conforms | reviewed via explicit ticket id, not a mis-scoped queue pull |
| orch.pipeline.status-gates-skill-entry | universal | conforms | entered review-child only at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | diff does not touch `canon/statutes/**` |
| orch.roles.betty-owns-test-tree | universal | conforms | `tests/**`/`docs/test-bible/**` changes arrive only via `test()`/`merge-tests()` commits, not engineer `code()` commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee is Katherine Johnson |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | assignee unchanged through Tests Passed; left as-is |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer `code()` commits touch only `src/ui/frontend/**` |
| astral.config.config-source-of-truth | scoped | conforms | `NAV_WIDE_MIN_PX` is a documented presentation-chrome constant, not a business/eligibility value; plan explicitly excluded a `config.py` key with reasoning |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env-specific values introduced |
| astral.debug.spikes-under-debug-dir | scoped | conforms | `docs/features/interface/ast-1286-...md` is a production feature plan, not a spike deliverable |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single file carries plan + review stub |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty's `test()`/`merge-tests()` commits touch only `tests/`+`docs/test-bible/`, not `src/`/`docs/features/` |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code()` commits never touch `tests/` or `docs/test-bible/**` |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | diff adds no new API endpoints |
| astral.layers.import-direction | scoped | conforms | `NavigationShell.tsx` imports only react/react-router-dom, sibling components, contexts, `lib/api` — no `src.data`/`src.external` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | candidate/admin gating reuses existing `CandidateContext`/`useAuth`; no new hardcoded visibility rules in React |
| astral.seed.define-approved | scoped | conforms | no product seed/catalog rows invented; `docs/features` path match is the plan doc, not seed behavior |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer or error-raising code touched |
| astral.standards.debug-contract-gated | scoped | conforms | frontend-only diff; backend debug contract (§1.5.1) is backend-only |
| astral.standards.dry-and-focused-functions | scoped | conforms | one shared `<nav>` tree toggled by `isWide`, not duplicated markup (plan's own ⚠️ Decision) |
| astral.standards.in-scope-only | scoped | conforms | touches only `NavigationShell.tsx` + `App.css`; no `NAV_CONFIG`/API/auth/page-layout edits |
| astral.standards.logging-via-utils | scoped | conforms | no logging/print introduced |
| astral.standards.names-not-ticket-ids | scoped | conforms | `NAV_WIDE_MIN_PX`, `candidateLabel`, `sidebar-candidate-menu-*` — no ticket ids embedded in identifiers |
| astral.standards.no-cross-contamination | scoped | conforms | no imports outside the layered structure |
| astral.standards.no-hardcoded-sets | scoped | conforms | breakpoint is a named module constant with a doc comment; no inline magic-number sprawl |
| astral.standards.public-then-helpers | scoped | conforms | `candidateLabel` grouped with pre-existing `loadExpanded`/`saveExpanded` helpers above the component, consistent with the file's established layout |
| astral.ui.frontend-file-placement | scoped | conforms | shell/CSS changes stay in `components/NavigationShell.tsx` and `App.css` per placement table |
| astral.ui.naming-conventions | scoped | conforms | PascalCase component unchanged; new CSS classes kebab-case |
| astral.ui.single-gunicorn-worker | scoped | conforms | diff doesn't touch server startup/worker config |
| astral.agent.confidence-bounds | scoped | not-applicable | layers core/utils don't intersect diff layers (ui, docs) |
| astral.agent.do-task-delegation | scoped | not-applicable | layer core not in diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | layer core not in diff |
| astral.batch.batch-id-first | scoped | not-applicable | layers data/core not in diff |
| astral.batch.batch-id-format | scoped | not-applicable | layers core/data not in diff |
| astral.batch.claim-process-release | scoped | not-applicable | layers core/data not in diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers core/data not in diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no `artifacts/**`/`scripts/spikes/**` path in diff |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | layers core/utils not in diff |
| astral.dispatch.seed-auto-false | scoped | not-applicable | layers core/utils not in diff; `dispatcher.py`/`config.py` untouched |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | layer core not in diff |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | layer core not in diff |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers core/external not in diff |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layer scripts not in diff; no `scripts/**` path touched |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | paths (`data/admin/**`, `repo_admin_json.py`, `config.py`, `bootstrap.py`) not touched |
| astral.seed.archie-catalog-wins | scoped | not-applicable | paths (`dispatcher.py`, `config.py`, `data/admin/**`) not touched |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | layers core/data/utils/scripts not in diff |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | layers core/data/utils not in diff |
| astral.seed.other-via-coverage-join | scoped | not-applicable | layers core/data/utils not in diff |
| astral.standards.database-header-inventory | scoped | not-applicable | layer data not in diff |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layer utils not in diff |
| astral.state.core-decides-transitions | scoped | not-applicable | layers core/data not in diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers core/data/utils not in diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layer core not in diff |

Retired (ignored per algorithm step 4): `astral.config.pass-threshold-vs-score-floor`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.patterns.require-auth-on-protected-endpoints`.

## Pattern conformance

| id | verdict | one-line |
|---|---|---|
| pattern.ui.responsive-nav-shell | discuss | Not found under `canon/patterns/**` — per C5 text a missing id reads as invalid citation, but the ticket self-discloses it as proposed/pending ("Considered but excluded: Canon file for pattern.ui.responsive-nav-shell — Archie approval before catalog law"), not a false catalog claim. Diff behavior matches the described shape. Routing as discuss rather than fix-now since there is no code fix — resolution is Archie authoring+approving the canon file (or the plan dropping the id until it lands). |

## Plan adherence

- Stage 1 (hamburger, overlay drawer, backdrop dismiss, close-on-navigate, desktop parity ≥1024px) and Stage 2 (narrow checked candidate list, admin/non-admin gate, native `<select>` unchanged on wide) both land exactly as specced, one `<nav>` tree shared between modes per the plan's own DRY decision.
- Self-Assessment (`Single-Component`, `Conf: high`) matches the real footprint — only `NavigationShell.tsx` + `App.css` in the product commits.
- No scope creep into `NAV_CONFIG`, `AdminDeployFooter.tsx`, auth, or page layouts; AST-1166/AST-1273 boundaries respected.

## Findings

**discuss:** Pattern conformance table above — `pattern.ui.responsive-nav-shell` has no canon file yet.

Notes: no plan-rubric (Joan) verdict attachment on this ticket — C4 straggler check has nothing to cross-check against; not a block.

## What's solid

- Single shared `<nav>` markup toggled by `isWide`/`sidebar--open` — no duplicated tree.
- `matchMedia` listener correctly forces `drawerOpen`/`candidateMenuOpen` closed on resize-to-wide, so a desktop resize never leaves an orphan open drawer.
- Wide-mode `<select>` markup/logic is untouched byte-for-byte in behavior (just factored through `candidateLabel`).

context_tokens≈9000
— Radia

#### betty — 2026-08-08T20:18:22.646Z
## QA test manifest

**Publish:** `origin/sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell` @ `8441b225`
**Betty delivery:** `merge-tests(AST-1286): origin/tests 5a98fb36c1f56ebe1b2ab0d274622d5aa7ac203e`

### Run

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx
```

### Manifest

1. **Existing (revised):** `tests/component/frontend/components/test_NavigationShell.test.tsx` — wide-mode nav groups/badges/combobox + admin footer; non-admin disabled select + no deploy footer; loading/error — needs `stubNavViewport(true)` after Stage 1 `matchMedia`.
2. **Existing (revised via stub):** `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` — AST-709 nav-escape under `NavigationShell` (jsdom `matchMedia` default wide in `test-utils`).
3. **Gap — AST-1286 wide:** native `<select>` still used; checked candidate menu absent.
4. **Gap — AST-1286 narrow drawer:** hamburger opens overlay; backdrop dismiss leaves pathname unchanged; drawer closed.
5. **Gap — AST-1286 close-on-navigate:** enabled `NavLink` changes route and closes drawer.
6. **Gap — AST-1286 narrow candidate list (admin):** checked list marks current (`✓` / `is-selected`); admin select updates `astral_selected_candidate`.
7. **Gap — AST-1286 narrow non-admin:** menu rows disabled; selection unchanged; deploy footer omitted.

**Broken / obsolete:** all prior `NavigationShell` mounts crashed on `window.matchMedia is not a function` — fixed with `stubNavViewport` in `tests/component/frontend/test-utils.tsx`.

**Integration:** no existing scenario asserts shell/CSS; `test_candidate_nav_api.py` unchanged; no new integration coverage.

**Bible (on publish ref):**
`docs/test-bible/frontend/components.md` sha1 `9dea96c7cb5e6c29ccb7f7a7ed943b37d4e34010`

— Betty

#### joan — 2026-08-08T20:13:21.781Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1286
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell` @ `2d98108f`

## Traceability

AC1→S1; AC2→S1; AC3→S1+S2.4; AC4→S2; AC5→S1; AC6→S1+S2; AC7→S1+S2.4. No unmapped AC, no orphan stage — both stages trace to parent Functional scope (breakpoint/overlay/backdrop/close-on-navigate; checked candidate list) and Purpose (full-width content on narrow viewports).

**Considered:** 37 active statutes (18 universal + 19 scoped on layer `ui`, paths `src/ui/frontend/**`, change_type `modify`); all scored `conforms`. 27 scoped actives excluded (non-`ui` layers or non-matching paths — core/data/external/utils/scripts/docs). Scored in-session per R7; no table pasted here.

## Findings

**discuss — Stage 1 steps 9/10 contradict each other on backdrop z-index.** Step 9 says `backdrop 30`, step 10 writes `z-index: 40` for `.nav-backdrop`, which equals the hamburger's `40`. Since the backdrop is later in the DOM, it paints over the button, so the `aria-label="Close navigation"` state is unreachable while the drawer is open. AC2 (backdrop dismiss) still works either way, so this does not block. Recommend fixing one stack in the plan before build — e.g. backdrop 40, sidebar 50, hamburger 60 — so the plan stays binding without the builder guessing.

**discuss — close-on-navigate misses the same-route tap.** Stage 1 step 5 closes the drawer on `location.pathname` change and claims that "covers enabled nav destination clicks". Tapping the nav item for the route you are already on does not change the pathname, so the drawer stays open over the content. AC5's precondition ("navigates successfully") is not met in that case, so it is not a strict violation, but it is a cheap gap to close. Recommend adding `onClick={() => setDrawerOpen(false)}` to the enabled `NavLink` in addition to the pathname effect.

**discuss — fractional-width seam between the JS and CSS breakpoints.** JS matches `(min-width: 1024px)` and CSS matches `(max-width: 1023px)`. A viewport of 1023.5px (browser zoom, some device pixel ratios) satisfies neither, so React renders the narrow-mode checked candidate list while CSS still renders the desktop column. Recommend `max-width: 1023.98px` in the media query so the two agree at every width.

**discuss — non-admin drawer shows the whole roster where desktop does not.** Stage 2 says "Always allow open/close for reading the list", but today's desktop control is a `disabled` `<select>` a non-admin cannot open at all. Selection rules do match desktop (rows `disabled`, and `setSelectedId` is already gated on `isAdmin` inside `CandidateContext`), and `/api/candidates` already ships the full list to every authenticated client, so this is a visibility delta rather than an auth-rule change — outside AC4's letter but worth Susan's eye. Recommend either collapsing the narrow list to the current candidate for non-admins, or confirming the roster is fine to display.

**discuss — proposed `pattern.ui.responsive-nav-shell` is flagged but not drafted.** `canon/patterns/ui/` holds only `pattern.ui.admin-endpoint`; there is no `status: proposed` file for the responsive shell. Parent and plan both correctly defer to Archie before treating it as catalog law, so this is a corpus gap, not a plan defect (plan-rubric R6). No approved pattern matches this plan's shape, so the parent's "no established pattern applies" holds.

**acceptable — plan assumptions verified against the tree at the publish ref.** `.shell` is `display: flex`, `.sidebar` is `width: 240px` with `overflow-y: auto` and `flex-shrink: 0`, the App.css TOC and the section 4 / section 5 boundary are where step 8 and step 9 expect them, all cited design tokens exist, and `{isAdmin ? <AdminDeployFooter /> : <span className="nav-footer-spacer" />}` is the single footer branch. No codebase drift.

**acceptable — breakpoint literal stays out of `config.py`.** `NAV_WIDE_MIN_PX` as a documented module-level TS constant satisfies §1.4 ("named constants from config or module-level constants") and `astral.config.config-source-of-truth` is not engaged: 1024px is presentation chrome, and nav visibility/enablement stays resolved server-side at `/api/nav_config`. The `AST-1286` references live in comments and CSS section headers, which is inside the `astral.standards.names-not-ticket-ids` carve-out.

**acceptable — self-assessment is honest.** `Single-Component` matches a two-file frontend change; `high` conf is justified because AC and the parent Architectural definition pin every behavior; `Medium` risk correctly names nav chrome as app-wide blast radius with containment to the shell.

context_tokens≈64000

— Joan

#### katherine — 2026-08-08T20:09:16.797Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell/docs/features/interface/ast-1286-responsive-left-nav-hamburger-shell.md (`origin/sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell` @ `2d98108f`)

**Scope:** Single-Component — only `NavigationShell.tsx` + `App.css`; no API/core/data.

**Conf:** high — AC and parent architectural definition pin breakpoint, overlay drawer, backdrop, checked list, and desktop parity on the existing shell.

**Risk:** Medium — nav chrome regression would block every route, but blast radius stays in the shell component/CSS.

---

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

## Radia review — [code-rubric] revision=2

**Publish ref tip:** `8441b2257d324973e7e8737b4d5c2283ac52c9b4`
**Overall:** DISCUSS

Full active statute set scored in-session (64 active leaves; 4 retired ignored) — conforms across the board on the applicable subset (frontend layer + config/naming/import/DRY/in-scope/test-tree-ownership statutes); everything else not-applicable to a shell/CSS-only diff. Linear comment carries the full `## Statutes checked` table per code-rubric.v2.

**Pattern conformance:** `pattern.ui.responsive-nav-shell` — discuss. No file under `canon/patterns/**` yet; the ticket already self-discloses this ("Considered but excluded: Canon file... Archie approval before catalog law"), so it isn't a false catalog claim, but C5 still flags a missing id. Resolution is Archie authoring + approving the canon file (or dropping the citation until it lands) — not a code change.

**Plan adherence:** Stage 1 + Stage 2 land exactly as specced — single shared `<nav>` tree, `matchMedia` listener resets drawer/candidate-menu state on resize-to-wide, wide `<select>` behavior untouched. No scope creep into `NAV_CONFIG`, `AdminDeployFooter.tsx`, auth, or page layouts.

Full verdict + statute table: Linear comment on AST-1286.

— Radia

## Resolution

**Date:** 2026-08-08  
**Review:** [code-rubric] revision=2 — Overall DISCUSS; zero fix-now.

| Finding | Action |
|---------|--------|
| **discuss** — `pattern.ui.responsive-nav-shell` missing under `canon/patterns/**` | Closed by Radia's alternate path: **drop the citation until Archie lands the canon file**. Linear **In scope** no longer lists the proposed pattern id; **Considered but excluded** records the citation deferral. Product behavior (hamburger/drawer/backdrop/checked list) unchanged — no code change required. |

No product files touched on resolve. Tip after this commit includes Radia's `docs(AST-1286): Radia review — discuss` (`999d4796`) plus this Resolution.
