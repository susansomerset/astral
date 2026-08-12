# AST-1335 — Dirty-leave save-then-navigate helper

**Linear:** [AST-1335](https://linear.app/astralcareermatch/issue/AST-1335)
**Parent:** [AST-1315](https://linear.app/astralcareermatch/issue/AST-1315) — Do not navigate away from dirty content
**Publish ref:** `sub/AST-1315/AST-1335-dirty-leave-save-then-navigate-helper`

Shared in-app dirty-leave affordance for pages that own unsaved drafts: when dirty, block SPA navigation, show the themed confirm with Save as primary/default, on affirm run a caller-provided save then continue, on cancel stay with the draft intact, on save failure stay so the caller can surface the error. Lands proposed `pattern.ui.dirty-leave-save-then-navigate` for Archie. Does **not** wire Candidate Profile (sibling AST-1336).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/App.tsx` | Replace `BrowserRouter` + `useRoutes` with `createBrowserRouter(routes)` + `RouterProvider` so `useBlocker` works | ui |
| `src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts` | New shared hook — dirty gate, `useBlocker`, themed Save confirm, save-then-proceed / cancel-stay / fail-stay | ui |
| `canon/patterns/ui/pattern.ui.dirty-leave-save-then-navigate.md` | New catalog entry — `status: proposed`, `proposed_in: AST-1315` | docs |
| `canon/patterns/README.md` | List the new proposed id in Harvested corpus | docs |
| `canon/patterns/HARVEST.md` | Crosswalk row for the new proposed pattern | docs |

**Out of scope (do not touch):** `CandidateProfile.tsx`, `Modal.tsx` discard-on-close, ArtifactEditor autosave/`beforeunload`, other Save pages, `tests/**`, `docs/test-bible/**`.

## Stage 1: Data router so navigation blocking works

**Done when:** The production app boots through `createBrowserRouter` + `RouterProvider` with the existing `routes` tree unchanged. No page behavior changes. `tsc -b` and eslint for the frontend still pass.

1. In `src/ui/frontend/src/App.tsx`, replace the current shell:

   - Remove `BrowserRouter` and the inner `AppRoutes` / `useRoutes(routes)` helper.
   - Keep `StytchProvider` and `AuthProvider` as parents of the router (they do not need router context today).
   - At module scope (outside the component), create:

     ```ts
     const router = createBrowserRouter(routes)
     ```

   - Render:

     ```tsx
     <StytchProvider stytch={stytchClient}>
       <AuthProvider>
         <RouterProvider router={router} />
       </AuthProvider>
     </StytchProvider>
     ```

2. Do **not** edit `routes.tsx` route paths, elements, or provider nesting (`RequireAuth` / `CandidateProvider` / `NavigationShell` stay as they are).
3. Do **not** add route `loader` / `action` APIs, basename, or future flags beyond what `createBrowserRouter(routes)` needs to compile.
4. From `src/ui/frontend`, run `npm run build` (or at least `tsc -b`) and `npm run lint`. Fix only type/lint breaks caused by this App.tsx change.

⚠️ **Decision:** Migrate `App.tsx` to a data router so React Router’s `useBlocker` can intercept left-nav **and** other in-app SPA transitions (programmatic `navigate`, `<Link>`, history back/forward inside the SPA). Rejected: NavLink-click-only interception in `NavigationShell` — that misses non-nav in-app route changes required by the parent epic. Rejected: inventing a custom history stack. Hard browser tab close/refresh / `beforeunload` stays out of scope (parent boundary).

## Stage 2: Shared `useDirtyLeaveSaveThenNavigate` hook

**Done when:** `src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts` exists with the exact public contract below, uses `useUserConfirm` + `useBlocker`, and no page imports it yet (Profile wiring is AST-1336). Frontend `tsc -b` / lint still pass.

1. Create `src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts` (same folder as `useSectionExpandPolicy.ts` — shared affordance hooks).

2. Public types and defaults (module-level constants, not inline magic strings at call sites inside the hook):

   ```ts
   export type DirtyLeaveSaveThenNavigateOptions = {
     /** When false, navigation is never blocked and no prompt shows. */
     isDirty: boolean
     /**
      * Persist the draft. Must resolve on success and reject on failure.
      * Caller owns toasts / inline error UI on rejection (same as ordinary Save).
      * On success, caller must clear dirty (update snapshot) before the promise resolves
      * so a follow-on navigation is not re-blocked on stale dirty=true.
      */
     onSave: () => Promise<void>
     message?: string
     title?: string
     confirmLabel?: string
     cancelLabel?: string
   }

   const DEFAULT_MESSAGE = "You have unsaved changes. Save before leaving?"
   const DEFAULT_TITLE = "Save changes?"
   const DEFAULT_CONFIRM_LABEL = "Save"
   const DEFAULT_CANCEL_LABEL = "Cancel"
   ```

3. Hook body requirements (literal behavior — do not invent extra UI):

   - Call `const confirm = useUserConfirm()` from `../components/UserPrompt`.
   - Call `useBlocker` from `react-router-dom` with a `BlockerFunction` that returns `true` only when `isDirty` is true **and** `currentLocation.pathname !== nextLocation.pathname` (in-page Profile text tabs do not change pathname — they must not trip this helper; search/hash-only changes also do not block).
   - When `blocker.state === "blocked"`, run **one** confirm cycle (guard with a ref so React Strict Mode / effect re-entry does not open two dialogs for the same block):

     ```ts
     const ok = await confirm(message, {
       title,
       confirmLabel,
       cancelLabel,
       variant: "default", // → btn primary for Save; cancel stays btn secondary via UserPrompt
     })
     ```

   - If `ok === false`: call `blocker.reset()` and return (stay; draft untouched).
   - If `ok === true`: `try { await onSave(); blocker.proceed() } catch { blocker.reset() }` — do **not** call `proceed` on rejection; do **not** add a second toast inside the hook.
   - Export `useDirtyLeaveSaveThenNavigate(options: DirtyLeaveSaveThenNavigateOptions): void` (no return value).
   - Callers pass a stable `onSave` (`useCallback`). The hook may list `onSave` / `isDirty` / confirm copy in effect deps; do not add logging.

4. Do **not** import or edit `CandidateProfile.tsx`, `Modal.tsx`, or `NavigationShell.tsx` in this stage.
5. Re-run frontend `tsc -b` and lint.

⚠️ **Decision:** Save is the affirmative primary (`variant: "default"` → `btn primary`); Cancel is secondary. This is the opposite of Modal’s discard-on-close danger confirm — do not unify them. Error surfacing stays on the caller’s `onSave` (Profile already toasts on PUT failure); the helper only refuses to navigate.

⚠️ **Decision:** File lives under `src/hooks/`, matching `useSectionExpandPolicy` / `useCandidateJobActions`, not under `components/` (not a visual widget) and not as a parallel confirm provider (reuses `UserPrompt`).

## Stage 3: Propose `pattern.ui.dirty-leave-save-then-navigate`

**Done when:** The pattern file exists as `status: proposed` with SCHEMA-required frontmatter and body section order; README + HARVEST index the id; implementation does not treat the id as approved law (AUTHORING).

1. Create `canon/patterns/ui/pattern.ui.dirty-leave-save-then-navigate.md` with **exactly** this content:

   ```markdown
   ---
   id: pattern.ui.dirty-leave-save-then-navigate
   name: Dirty-leave save-then-navigate
   status: proposed
   proposed_in: AST-1315
   approved_by: null
   approved_at: null
   canonical_refs:
     - path: src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts
       symbol: useDirtyLeaveSaveThenNavigate
     - path: src/ui/frontend/src/App.tsx
       symbol: createBrowserRouter
   related_statutes:
     - astral.ui.frontend-file-placement
     - astral.ui.naming-conventions
     - astral.standards.dry-and-focused-functions
   supersedes: null
   superseded_by: null
   ---

   # Problem

   Operators lose in-progress page drafts when they leave via in-app navigation. Pages reinvent leave prompts, or wipe silently. Modal discard-on-close and ArtifactEditor autosave/`beforeunload` solve different problems and must not be overloaded for route leave.

   # Solution shape

   Shared hook `useDirtyLeaveSaveThenNavigate` (pointer in `canonical_refs`):

   - Caller owns dirty detection and the persist function (`onSave` → resolve success / reject failure).
   - When dirty and the SPA pathname would change, block with React Router `useBlocker` (requires a data router — `createBrowserRouter` in `App.tsx`).
   - Themed confirm via `useUserConfirm`: primary/default action is Save (`btn primary`); Cancel is `btn secondary`.
   - Affirm → await `onSave` → `blocker.proceed()`. Cancel → `blocker.reset()` (stay; draft intact). Save rejection → `blocker.reset()` (stay; caller surfaces error the same way as ordinary Save).
   - Do not treat same-pathname in-page chrome (e.g. Profile text tabs) as leave.
   - Do not change Modal discard-on-close or add Profile autosave.

   ## When not to use

   - Modal close with unsaved edits — keep Modal’s discard-oriented confirm.
   - ArtifactEditor / criteria editors that already autosave or use `beforeunload`.
   - Hard browser tab close/refresh — out of scope for this pattern (browser-native if addressed later).
   - Citing this pattern id as catalog law until `status: approved` (AUTHORING).

   ## Notes

   Proposed in parent AST-1315 Architectural definition. Helper lands with AST-1335; Candidate Profile wiring is AST-1336. Archie approves the id separately; remediations may use the hook before approval without treating the catalog id as approved.
   ```

2. In `canon/patterns/README.md`, in the **Harvested corpus** table, add one row after the existing UI pattern rows:

   | `pattern.ui.dirty-leave-save-then-navigate` | proposed | `ui/pattern.ui.dirty-leave-save-then-navigate.md` |

   Also bump the prose count line above that table if it still says “Nine catalog entries… one is `status: proposed`” so it stays accurate (ten approved-or-proposed entries; two proposed if run-next is still proposed).

3. In `canon/patterns/HARVEST.md` Crosswalk table, append one row:

   | create (AST-1335) | `pattern.ui.dirty-leave-save-then-navigate` | ui | `ui/pattern.ui.dirty-leave-save-then-navigate.md` | AST-1315 | proposed — dirty-leave save-then-navigate; Archie approval pending |

4. Do **not** set `status: approved` or invent `approved_by` / `approved_at`. Do **not** edit `pattern.ui.shared-button-roles.md` beyond citing it from related behavior (Save = primary) in the new file’s Solution shape only.

## Execution contract

- Stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1315/AST-1335-dirty-leave-save-then-navigate-helper`.
- Do not wire Profile, change Modal discard, or add autosave.
- If `useBlocker` throws because the data-router migration was skipped or incomplete — stop and comment on parent AST-1315; do not invent a NavLink-only fallback.
- If the codebase cannot import `useBlocker` from `react-router-dom` at the locked package version — stop and comment on parent AST-1315.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1335
**Overall:** APPROVED
**Publish ref:** `sub/AST-1315/AST-1335-dirty-leave-save-then-navigate-helper` @ `2e6037f73b8cb4bcf018976988dff25f274744b6`

### Traceability
AC1→S1+S2 (data router + `useBlocker`/`useUserConfirm`, Save=`btn primary` via `variant: "default"`); AC2→S2 (`ok===false` → `blocker.reset()`); AC3→S2 (`onSave` reject → `blocker.reset()`, no `proceed`); AC4→S2 (`isDirty` gate); parent AC6 (in-page tab switches)→S2 (`pathname` change only — sibling AST-1336 wires Profile); parent AC1–5 Profile-visible outcomes→AST-1336 per child boundary; parent AC7→AST-1336 (header Save/Cancel untouched here).

### Findings

#### acceptable — `src/hooks/` vs statute table `src/lib/`
**Location:** Stage 2 file placement; `astral.ui.frontend-file-placement`
**Finding:** ASTRAL_CODE_RULES §3.5 table still lists shared hooks under `lib/`, but the live tree already uses `src/hooks/` (`useSectionExpandPolicy`, `useCandidateJobActions`). Plan follows established convention with an explicit decision note.
**Recommendation:** Proceed as written; optional follow-up to amend the statute/table separately (out of AST-1335 scope).

#### acceptable — no explicit self-assessment block
**Location:** plan doc overall
**Finding:** Plan omits a formal self-assessment/conf section, but stages, decisions, execution contract, and estimate confirm line are specific and match complexity.
**Recommendation:** None required before build.

context_tokens≈38000

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1315/AST-1335-dirty-leave-save-then-navigate-helper`  
**Product commits:** `e9123957` (data router), `f8e55aa7` (hook), `d1545f4b` (proposed pattern + README/HARVEST)

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1335
**Publish ref:** `origin/sub/AST-1315/AST-1335-dirty-leave-save-then-navigate-helper` @ `0452b5489a560f9c657b2f3852c6f30700af22f3`
**Overall:** CLEAN

**Scope note:** Full `origin/dev...origin/sub/...` three-dot diff reports multiple merge bases and carries broad epic integration noise (400+ files). This review scores **AST-1335 product commits** (`e9123957`, `f8e55aa7`, `d1545f4b`) plus Betty test land on the publish tip (`d3a87345`, `0452b548`). Unrelated sibling canon/product paths in the wide diff are **not** attributed to this ticket.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent/LLM confidence surfaces in diff |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no dispatch/agent task changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grading/vector paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch claim paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process/release helpers |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity agent_responses paths |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config.py / config block changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env wiring |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact dirs |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed paths |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run_next chain edits |
| `astral.docs.features-single-file-per-ticket` | scoped | not-applicable | product commits did not add/duplicate feature docs |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty commits touch tests/bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Ada product commits exclude `tests/` and `docs/test-bible/**`; test land is Betty merge-tests |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no core/external layer changes |
| `astral.layers.import-direction` | scoped | conforms | hook imports React Router + `UserPrompt` only (UI-internal) |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no new hardcoded job/company/candidate state strings |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API endpoint changes |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON edits in ticket scope |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog conflicts |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed boot paths |
| `astral.seed.define-approved` | scoped | not-applicable | no define-approved seed flow |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage-join seed logic |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no database.py changes |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no backend `debug=` surfaces |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | single-purpose hook; no duplicated leave-prompt logic |
| `astral.standards.in-scope-only` | scoped | conforms | product footprint matches plan; Profile/Modal/NavigationShell untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | no `print`/ad-hoc logging added |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | symbols are descriptive (`useDirtyLeaveSaveThenNavigate`) |
| `astral.standards.no-cross-contamination` | scoped | conforms | no unrelated module rewrites |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no new backend hardcoded sets |
| `astral.standards.public-then-helpers` | scoped | conforms | exported types + hook; internals are module-private |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state machine edits |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state transitions |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run/daisy-chain paths |
| `astral.ui.frontend-file-placement` | scoped | conforms | `src/hooks/` matches established affordance-hook convention (Joan acceptable); statute prose still lists `lib/` |
| `astral.ui.naming-conventions` | scoped | conforms | hook file/symbol naming follows UI conventions |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server/worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests commit present on publish ref |
| `orch.git.commit-vocabulary` | universal | conforms | `code(AST-1335)` / `test(AST-1335)` / `docs(AST-1335)` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub-branch publish; no dev/main direct commits |
| `orch.git.ftr-sub-topology` | universal | conforms | child `sub/AST-1315/AST-1335-...` topology |
| `orch.git.merge-on-checkout` | universal | not-applicable | not verifiable from diff alone |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no evidence of forbidden git ops in ticket commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/...`, not agent branch |
| `orch.git.one-epic-worktree-per-parent` | universal | not-applicable | worktree discipline not diff-scored |
| `orch.git.three-permanent-branches` | universal | conforms | changes on sub publish ref only |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no new product forks beyond approved plan decisions |
| `orch.pipeline.plan-is-bible` | universal | conforms | three stages delivered in order per plan |
| `orch.pipeline.project-scoped-queues` | universal | not-applicable | queue/orchestration N/A to code diff |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | review at Tests Passed gate |
| `orch.roles.archie-approves-statutes` | universal | not-applicable | no statute authoring in product commits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test/bible changes on Betty commits, not Ada product commits |
| `orch.roles.chuckles-never-ticket-assignee` | universal | not-applicable | assignee discipline N/A to diff |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada remains assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path product edits observed |

**Sweep count:** 65 active statutes scored.

### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.dirty-leave-save-then-navigate` | conforms | Proposed catalog entry matches landed hook + data-router boot; `status: proposed` per plan |
| `pattern.ui.shared-button-roles` | conforms | Save/Cancel use `UserPrompt` `variant: "default"` → `btn primary` / `btn secondary` |

### Plan adherence

All three stages match the plan bible (data router, hook contract, proposed pattern). Estimate 3 fits. Cross-ticket: no Profile/Modal/NavigationShell/routes edits.

### Findings

#### advisory — App mount smoke replaced by source contract
**Location:** `tests/component/frontend/test_App.test.tsx`
**Finding:** Behavioral routing regression signal weaker; bible documents RR7+jsdom AbortSignal constraint.
**Recommendation:** Accept for this tip; consider routed smoke with AST-1336.

#### advisory — Optional chaining on blocker methods
**Location:** `useDirtyLeaveSaveThenNavigate.ts`
**Finding:** `blocker.reset?.()` / `blocker.proceed?.()` vs plan literals without `?.`.
**Recommendation:** Harmless; no action required.

#### advisory — Uncited `pattern.ui.shared-button-roles`
**Location:** hook confirm path via `UserPrompt`
**Recommendation:** Optional cite when AST-1336 wires Profile.

### What's solid
Clean separation (hook + data router now; wiring AST-1336). Hook matches parent AC intent. Strict Mode guarded. Betty tests cover predicates and outcomes. Engineer respects test-tree ban.

context_tokens≈42000
