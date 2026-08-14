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

## Radia review

## Radia review — AST-1369

**Publish ref:** `origin/sub/AST-1361/AST-1369-pin-left-nav-logo-and-candidate-chrome` @ `4de418048dcf15d81bf3df5fbe99cf5dc23b298d`  
**Baseline:** `origin/dev`  
**Product commit:** `8413f4ce` (`NavigationShell.tsx`, `App.css` only)  
**Tests commit:** `54012807` merged via single `merge-tests(AST-1369)` @ `4de41804`

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1369
**Publish ref:** 4de418048dcf15d81bf3df5fbe99cf5dc23b298d
**Overall:** DISCUSS
```

## Statutes checked

64 active statutes scored in-session (registry lists 65; corpus has 64 `status: active`).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | diff layers ui/docs only |
| astral.agent.do-task-delegation | scoped | not-applicable | diff layers ui/docs only |
| astral.agent.grade-vector-validation | scoped | not-applicable | diff layers ui/docs only |
| astral.batch.batch-id-first | scoped | not-applicable | diff layers ui/docs only |
| astral.batch.batch-id-format | scoped | not-applicable | diff layers ui/docs only |
| astral.batch.claim-process-release | scoped | not-applicable | diff layers ui/docs only |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | diff layers ui/docs only |
| astral.config.config-source-of-truth | scoped | conforms | no config surface changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env handling in diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | conforms | no debug artifact paths touched |
| astral.debug.spikes-under-debug-dir | scoped | conforms | no spike paths touched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | diff layers ui/docs only |
| astral.dispatch.seed-auto-false | scoped | not-applicable | diff layers ui/docs only |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `docs/features/interface/ast-1369-…md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty paths only on merge-tests |
| astral.git.engineer-test-tree-ban | scoped | conforms | product commit `8413f4ce` did not touch test-tree; Betty via merge-tests |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | diff layers ui/docs only |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | diff layers ui/docs only |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | no API/auth handler changes |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | diff layers ui/docs only |
| astral.layers.import-direction | scoped | conforms | ui-only; no layer violations |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | diff layers ui/docs only |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | layout/CSS only; no new business rules |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | diff layers ui/docs only |
| astral.seed.archie-catalog-wins | scoped | not-applicable | diff layers ui/docs only |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | diff layers ui/docs only |
| astral.seed.define-approved | scoped | conforms | no seed/bootstrap changes |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | diff layers ui/docs only |
| astral.seed.other-via-coverage-join | scoped | not-applicable | diff layers ui/docs only |
| astral.standards.data-raises-caller-logs | scoped | conforms | no data-layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | diff layers ui/docs only |
| astral.standards.debug-contract-gated | scoped | conforms | no backend debug surfaces |
| astral.standards.dry-and-focused-functions | scoped | conforms | structural wrap; no duplicated logic |
| astral.standards.in-scope-only | scoped | conforms | footprint matches plan table |
| astral.standards.logging-via-utils | scoped | conforms | no logging added |
| astral.standards.names-not-ticket-ids | scoped | conforms | `sidebar-chrome`/`sidebar-scroll` kebab CSS; ticket id only in section comments (existing pattern) |
| astral.standards.no-cross-contamination | scoped | conforms | nav shell slice only |
| astral.standards.no-hardcoded-sets | scoped | conforms | no new hardcoded sets |
| astral.standards.public-then-helpers | scoped | conforms | no new public/helper ordering issues |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | diff layers ui/docs only |
| astral.state.core-decides-transitions | scoped | not-applicable | diff layers ui/docs only |
| astral.state.job-prior-states-enforced | scoped | not-applicable | diff layers ui/docs only |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | diff layers ui/docs only |
| astral.ui.frontend-file-placement | scoped | conforms | edits in `components/` + `App.css` only |
| astral.ui.naming-conventions | scoped | conforms | no new files; PascalCase component unchanged |
| astral.ui.single-gunicorn-worker | scoped | conforms | no server/worker changes |
| orch.git.betty-merge-tests-one-sha | universal | conforms | exactly one `merge-tests(AST-1369): origin/tests 54012807` |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `merge-tests` / `docs` vocabulary correct |
| orch.git.flow-direction-inviolable | universal | conforms | sub branch topology respected |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1361/AST-1369-…` publish ref |
| orch.git.merge-on-checkout | universal | conforms | no merge violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops in diff |
| orch.git.no-dev-agent-branches | universal | conforms | no dev agent branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1361 epic worktree pattern |
| orch.git.three-permanent-branches | universal | conforms | dev/tests/sub flow intact |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-decision scope creep |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches Stage 1 plan |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to diff |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review path |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test/bible delta via merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | product commit path-clean |

**Straggler (C4):** Joan plan-rubric APPROVED attached; no Excluded-statute list — no stragglers.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Parent/plan: no established pinned-chrome pattern; flex+overflow structural split is appropriate |

## Plan adherence

Stage 1 delivered as specified:

- `NavigationShell.tsx`: exact `sidebar-chrome` (logo + candidate wide select / narrow menu) + `sidebar-scroll` (loading/error/groups + `AdminDeployFooter` / spacer) nesting; handlers, fetch, drawer, `NAV_WIDE_MIN_PX`, and admin gating unchanged.
- `App.css`: TOC `4c` appended; `.sidebar` `overflow-y: auto` → `overflow: hidden`; `.sidebar-chrome` / `.sidebar-scroll` rules with `flex: 1`, `min-height: 0`, `overflow-y: auto`; no sticky positioning.
- Boundaries held: no `NAV_CONFIG`, candidate APIs, footer redesign, breakpoint literals, or extra files on product commit.
- Estimate **2** fits actual footprint (two product files, structural DOM/CSS only).
- Betty: three AST-1369 DOM-split tests + bible entry; AST-1286 block retained for responsive regression.

## Findings

### discuss

- **Location:** Plan Stage 1 “Done when” (≥1024px scroll pinning) vs `test_NavigationShell.test.tsx` AST-1369 block  
  **Finding:** Plan done-when requires that when nav groups overflow, scrolling moves groups/footer while logo + candidate stay visible. Betty’s new tests assert chrome/scroll **DOM placement** only — no test drives overflow height or asserts chrome remains visible after scroll.  
  **Recommendation:** Treat as UAT smoke (expand groups until overflow, scroll `.sidebar-scroll`, confirm chrome fixed) unless Betty adds a scroll-behavior case in a follow-up. Not a product-code defect given CSS is correct.

### advisory

- **Location:** `App.css` — `.sidebar-chrome` (plan Stage 1 step 7)  
  **Finding:** Plan allows `.sidebar-chrome { overflow: visible; }` if narrow open candidate menu clips under `.sidebar { overflow: hidden }`. Implementation has only `flex-shrink: 0`; Betty’s narrow test covers menu-in-chrome DOM, not open-menu clipping.  
  **Recommendation:** UAT narrow drawer — open candidate menu with long list; if clipped, add `overflow: visible` on chrome only (per plan).

- **Location:** `NavigationShell.tsx` `loadExpanded` / `saveExpanded` (pre-existing)  
  **Finding:** Bare `catch { }` on localStorage paths unchanged by this ticket.  
  **Recommendation:** No action for AST-1369; grandfather per §5a silent-failure table.

## What’s solid

- Clean structural split — no duplicated logo/candidate trees, no sticky hacks.
- Product commit isolated to UI/CSS; test-tree changes Betty-owned via single merge-tests SHA.
- CSS flex/overflow pattern matches plan and should pin chrome at wide viewports.
- Responsive shell paths (hamburger, backdrop, close-on-navigate, wide select / narrow menu) preserved; AST-1286 tests still in manifest.

## Recommended actions (downstream — not Radia lane)

1. **UAT:** Wide viewport — expand nav until overflow; confirm logo + candidate stay fixed while groups scroll.
2. **UAT:** Narrow drawer — open candidate menu; confirm list not clipped (add `overflow: visible` on chrome if needed).
3. **Optional Betty follow-up:** Component test asserting scroll pinning if team wants automated AC1 coverage.

## Frame diff

(none) — child plan and parent AST-1361 chrome-pin intent align with diff; no scope smuggling or description-frame drift.

## Notes

- Joan validate APPROVED present; no statute exclusions to straggle-check.
- Product SHA `8413f4ce`; tip SHA `4de41804` includes docs + Betty merge.

context_tokens≈48000

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] REVIEW (Commit: 4de41804) scroll pinning UAT
```

**C7:** Complete — Chuckles may append full artifact to issue doc, push `docs(AST-1369): Radia review — findings`, post slim upshot, move to **Review Posted** → **resolve-child** not required (no fix-now); datt routes REVIEW per skill. If Susan wants zero discuss items before UT, UAT scroll smoke closes the discuss gap without code changes.

## Resolution (Katherine / resolve) — 2026-08-14

**Publish tip before resolve:** `origin/sub/AST-1361/AST-1369-pin-left-nav-logo-and-candidate-chrome` @ `46b7750d` (Radia `docs()` intake via sync-child)

| Finding | Action |
|---------|--------|
| **discuss** — plan Done-when scroll pinning vs Betty DOM-only tests | No product change. Accept Radia recommendation: UAT smoke (expand groups until overflow, scroll `.sidebar-scroll`, confirm chrome fixed). Optional Betty scroll-behavior test is out of engineer lane. |
| **advisory** — `.sidebar-chrome` `overflow: visible` if narrow menu clips | No preemptive CSS. Leave `flex-shrink: 0` only; add `overflow: visible` only if UAT shows clipping (plan Stage 1 step 7). |
| **advisory** — bare `catch` on localStorage | No action (grandfather; pre-existing). |

No `fix-now`. Product tree unchanged this pass.
