# AST-1336 — Candidate Profile dirty-leave wiring

**Linear:** [AST-1336](https://linear.app/astralcareermatch/issue/AST-1336)
**Parent:** [AST-1315](https://linear.app/astralcareermatch/issue/AST-1315) — Do not navigate away from dirty content
**Publish ref:** `sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring`

Wire Candidate Profile to the shared dirty-leave helper from AST-1335 so unsaved Profile edits cannot be silently discarded by in-app navigation: track dirty against the last loaded/saved snapshot, prompt with Save as primary, persist via the existing Profile PUT path, then continue to the requested destination. Profile only — does not implement the helper, does not expand to other Save pages, and does not treat in-page text-tab switches as leave.

**Prerequisite (already on this worktree via `origin/ftr/AST-1315-do-not-navigate-away-from-dirty-content`):** `useDirtyLeaveSaveThenNavigate` in `src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate.ts` and `createBrowserRouter` in `App.tsx`. Do not re-implement or fork that contract.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Dirty vs last loaded/saved snapshot; Promise-based save shared by header Save and dirty-leave `onSave`; call `useDirtyLeaveSaveThenNavigate` | ui |

**Do not touch:** `useDirtyLeaveSaveThenNavigate.ts`, `App.tsx`, `routes.tsx`, `NavigationShell.tsx`, `TabbedTextArea.tsx`, `Modal.tsx`, ArtifactEditor / other Save pages, API/shapes/config, `tests/**`, `docs/test-bible/**`, canon pattern files (owned by AST-1335).

## Stage 1: Dirty snapshot + Promise save + dirty-leave wiring

**Done when:** On Candidate Profile with unsaved edits, choosing another in-app left-nav / SPA destination shows the themed Save confirm (primary Save). Affirm persists via the existing `PUT /api/candidates/:id/data` path (reload Profile shows the same values) and then lands on the requested destination. Cancel on the prompt stays on Profile with the draft intact. Save failure stays on Profile with the same visible error/toast as header Save and does not navigate. Clean Profile leaves without a prompt. Switching only among Profile’s in-page text tabs does not show the leave prompt and keeps draft text. Header Cancel and header Save still work as today when the operator is not mid-navigation.

1. In `src/ui/frontend/src/pages/CandidateProfile.tsx`, add:

   ```ts
   import { useDirtyLeaveSaveThenNavigate } from "../hooks/useDirtyLeaveSaveThenNavigate"
   ```

   Place it with the other relative imports (after `api` / toast helpers is fine).

2. **Dirty detection** — after `const data = fetched?.id === selectedId ? fetched.data : null`, compute:

   ```ts
   const isDirty =
     data !== null && JSON.stringify(values) !== JSON.stringify(data)
   ```

   `data` is already the last successfully loaded or saved edit tree (`fetched` updated on load and on successful save). Do **not** introduce a separate `touched` flag, a new lib helper, or shapes-driven field walking. Do **not** compare against a second snapshot object.

   ⚠️ **Decision:** `JSON.stringify` equality against the existing `fetched` snapshot. Both trees are produced by `editValuesFromCandidate` / `setByPath` on the same shape, so structural stringify is enough for Profile. Rejected: Modal-style `touched` (parent AC is value-vs-snapshot, not “user typed”). Rejected: new `deepEqual` module (one-page use; out of scope).

3. **Promise save shared by header Save and dirty-leave** — replace the fire-and-forget `handleSave` body with a `useCallback` that returns `Promise<void>`:

   ```ts
   const persistProfile = useCallback((): Promise<void> => {
     if (!selectedId) {
       return Promise.reject(new Error("No candidate selected"))
     }
     setError(null)
     return api(`/api/candidates/${selectedId}/data`, {
       method: "PUT",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify(values),
     })
       .then(async r => {
         if (!r.ok) await readApiError(r, `/api/candidates/${selectedId}/data`, "PUT")
         return r.json()
       })
       .then(candidate => {
         const vals = editValuesFromCandidate(candidate)
         setFetched({ id: selectedId, data: vals })
         setValues({ ...vals })
         refreshCandidate()
         setToast({ text: "Profile saved", variant: "success" })
       })
       .catch(e => {
         setError(e.message)
         setToast(
           e instanceof ApiError
             ? errorToastFromApiError(e)
             : { text: "Save failed", variant: "error" },
         )
         throw e
       })
   }, [selectedId, values, refreshCandidate])
   ```

   Requirements literal to this contract:

   - Same URL, method, headers, and `JSON.stringify(values)` body as today’s `handleSave`.
   - On success: update `fetched` + `values` from `editValuesFromCandidate(candidate)`, call `refreshCandidate()`, success toast — **before** the promise resolves (clears `isDirty` so `blocker.proceed()` is not re-blocked).
   - On failure: set `error` + error toast **and rethrow** (`throw e`) so `useDirtyLeaveSaveThenNavigate` calls `blocker.reset()` and does not navigate.
   - Header Save becomes: `function handleSave() { void persistProfile() }` (or `onClick={() => { void persistProfile() }}`). Do not change button labels, classes (`btn primary` / `btn secondary`), or placement.

4. **Header Cancel unchanged** — keep `handleCancel` as today: `if (data) setValues({ ...data }); setError(null)`. Do not call the dirty-leave helper, do not navigate, do not discard via a confirm.

5. **Wire the helper** — call (hooks must run unconditionally before any early `return`; place with other hooks, not after the Loading / No candidate early returns):

   ```ts
   useDirtyLeaveSaveThenNavigate({
     isDirty,
     onSave: persistProfile,
   })
   ```

   Do **not** pass custom `message` / `title` / `confirmLabel` / `cancelLabel` unless a later Plan Discuss requires it — use the helper defaults (Save primary / Cancel secondary). Do **not** wrap `TabbedTextArea` or invent a leave handler for tab index changes: `TabbedTextArea` keeps active tab in local state and does not change `location.pathname`; the helper already blocks only on pathname change.

6. Do **not** add `beforeunload`, autosave, debounce save, or Modal discard semantics. Do **not** edit other pages.

7. From `src/ui/frontend`, run `npm run build` (or at least `tsc -b`) and `npm run lint`. Fix only type/lint breaks caused by this file’s changes.

⚠️ **Decision:** One `persistProfile` Promise for both header Save and dirty-leave `onSave` (DRY; same error surface). Rejected: duplicating the PUT in an inline `onSave` that diverges from header Save.

⚠️ **Decision:** Rely on AST-1335’s pathname-only `useBlocker` for AC6 (in-page text tabs). Do not add Profile-local tab guards or route search/hash logic.

## Execution contract

- Stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring`.
- If `useDirtyLeaveSaveThenNavigate` is missing from the tree after `sync-child.sh` with `--ftr AST-1315-do-not-navigate-away-from-dirty-content` — stop and comment on **parent** AST-1315; do not re-implement the helper.
- If `persistProfile` success updates snapshot after `proceed` would run (dirty still true) — stop and fix ordering so snapshot clear happens before the promise resolves (helper contract).
- Do not expand to other Save pages or change API/shapes contracts.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1336
**Overall:** APPROVED
**Publish ref:** `sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring` @ `fd57bab1f9ad0eadd90ee101d5eb24f4cfb936bf`

## Traceability
AC1→S1 (`isDirty` + `useDirtyLeaveSaveThenNavigate`); AC2→S1 (`persistProfile` success clears snapshot then helper `proceed`); AC3→S1 (helper cancel/`blocker.reset` + header Cancel unchanged); AC4→S1 (`persistProfile` rethrow + error/toast, no `proceed`); AC5→S1 (`isDirty` false when `values` matches `fetched.data`); AC6→S1 (AST-1335 pathname-only blocker; no tab guards); AC7→S1 (header Save/Cancel labels, classes, and Cancel revert behavior preserved).

## Findings

### acceptable — `JSON.stringify` dirty check
**Location:** Stage 1 step 2
**Finding:** Stringify equality is a blunt instrument, but both trees share `editValuesFromCandidate` / `setByPath` origin; plan documents the rejected alternatives explicitly.
**Recommendation:** Proceed as written; revisit only if Profile field shapes introduce ordering instability (unlikely on this page).

### acceptable — no explicit self-assessment block
**Location:** plan doc overall
**Finding:** Plan omits formal self-assessment/conf prose, but single-stage scope, prerequisite gate, hook-order rule, and `persistProfile` contract are specific and match estimate 2.
**Recommendation:** None required before build.

context_tokens≈52000

[plan-rubric] PROCEED (Commit: fd57bab1f9ad0eadd90ee101d5eb24f4cfb936bf) Profile wiring faithful

## Review (build)

**Built:** `origin/sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring` @ `dbe04caea8c6c7418b6b46cfba41ec7c022ab972`

Stage 1: Profile `isDirty` vs last loaded/saved snapshot; `persistProfile` Promise shared by header Save and `useDirtyLeaveSaveThenNavigate`; header Cancel unchanged. Tests deferred to Betty.

## Radia review

# Radia review — AST-1336

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1336  
**Publish ref:** `origin/sub/AST-1315/AST-1336-candidate-profile-dirty-leave-wiring` @ `92637061911e40ccd932f28448d09de1429c7a91`  
**Overall:** CLEAN

**Scope note:** Three-dot diff vs `origin/dev` includes AST-1315 prerequisite paths (`App.tsx`, `useDirtyLeaveSaveThenNavigate.ts`) from ftr rollup — **not** AST-1336 product commits. This review scores **AST-1336 product** (`dbe04cae` — `CandidateProfile.tsx` only) plus Betty test land (`b3d669fd`, `0433ab37`) on the publish tip.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no agent/LLM paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no dispatch/agent task changes |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no grading/vector paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch claim paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch id emission |
| `astral.batch.claim-process-release` | scoped | not-applicable | no claim/process/release helpers |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no entity agent_responses paths |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env wiring |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact dirs |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed paths |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no run_next chain edits |
| `astral.docs.features-single-file-per-ticket` | scoped | not-applicable | product commits did not add feature docs |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty commits touch tests/bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Katherine product commit excludes `tests/` and `docs/test-bible/**` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no core/external changes |
| `astral.layers.import-direction` | scoped | conforms | Profile imports hook + existing UI modules only |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts changes |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no new hardcoded state strings; shapes-driven Profile unchanged |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no new API endpoints |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON edits in ticket scope |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog conflicts |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed boot paths |
| `astral.seed.define-approved` | scoped | not-applicable | no define-approved seed flow |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no coverage-join seed logic |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no database.py changes |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no backend `debug=` surfaces |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | single `persistProfile` shared by header Save and dirty-leave `onSave` |
| `astral.standards.in-scope-only` | scoped | conforms | one file (`CandidateProfile.tsx`); plan out-of-scope paths untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | no logging added |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `persistProfile`, `isDirty` naming is descriptive |
| `astral.standards.no-cross-contamination` | scoped | conforms | no unrelated module rewrites |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no new backend hardcoded sets |
| `astral.standards.public-then-helpers` | scoped | conforms | wiring at page level; helper remains shared export |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state machine edits |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state transitions |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run/daisy-chain paths |
| `astral.ui.frontend-file-placement` | scoped | conforms | change confined to `pages/CandidateProfile.tsx` |
| `astral.ui.naming-conventions` | scoped | conforms | page/hook import paths follow UI conventions |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server/worker config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests + restore commits on publish ref |
| `orch.git.commit-vocabulary` | universal | conforms | `code(AST-1336)` / `test(AST-1336)` / `docs(AST-1336)` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub-branch publish |
| `orch.git.ftr-sub-topology` | universal | conforms | child `sub/AST-1315/AST-1336-...` topology |
| `orch.git.merge-on-checkout` | universal | not-applicable | not verifiable from diff alone |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no forbidden git ops in ticket commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/...` |
| `orch.git.one-epic-worktree-per-parent` | universal | not-applicable | worktree discipline not diff-scored |
| `orch.git.three-permanent-branches` | universal | conforms | changes on sub publish ref only |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no new product forks beyond approved plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | single stage delivered per plan |
| `orch.pipeline.project-scoped-queues` | universal | not-applicable | queue/orchestration N/A to code diff |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | review at Tests Passed gate |
| `orch.roles.archie-approves-statutes` | universal | not-applicable | no statute authoring in product commits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test/bible changes on Betty commits only |
| `orch.roles.chuckles-never-ticket-assignee` | universal | not-applicable | assignee discipline N/A to diff |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine remains assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path product edits observed |

**Sweep count:** 65 active statutes scored.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.dirty-leave-save-then-navigate` | conforms | Profile wires `isDirty` + `persistProfile` per proposed Solution shape (AST-1335 prerequisite) |
| `pattern.ui.shared-button-roles` | conforms | Header Save/Cancel labels, classes (`btn primary` / `btn secondary`), placement unchanged |
| *(plan cited)* | none cited | Consumes AST-1335 proposed pattern; no additional approved pattern ids cited |

## Plan adherence

Stage 1 delivered faithfully in `dbe04cae`:

- **Dirty detection:** `isDirty = data !== null && JSON.stringify(values) !== JSON.stringify(data)` against last loaded/saved `fetched` snapshot.
- **`persistProfile`:** Promise-based PUT with same URL/method/body; success updates `fetched`/`values`, `refreshCandidate()`, success toast **before** resolve; failure sets error + toast **and rethrows**.
- **Header Save:** `void persistProfile()` — labels/classes unchanged.
- **Header Cancel:** unchanged revert-to-snapshot behavior.
- **Helper wiring:** `useDirtyLeaveSaveThenNavigate({ isDirty, onSave: persistProfile })` with defaults; placed **before** Loading / No-candidate early returns (lines 142–145 vs 199–200).
- **Boundaries:** No edits to hook, `App.tsx`, `routes.tsx`, `NavigationShell`, `TabbedTextArea`, `Modal`, API/shapes, or other Save pages.

**Estimate (2):** Single-page wiring — footprint matches.

**Prerequisite (AST-1335):** Hook + data router present on publish ref; consumed, not forked.

**Joan straggler (C4):** Joan APPROVED verdict attached; no Excluded-statute conflicts.

## Findings

### advisory — Profile tests mock the helper (no real `useBlocker` navigation)

**Location:** `tests/component/frontend/pages/test_CandidateProfile.test.tsx`  
**Finding:** Suite mocks `useDirtyLeaveSaveThenNavigate` and asserts wiring via `latestDirtyLeave()` capture. No component test exercises Profile + real blocker + themed confirm + `proceed` on pathname change.  
**Recommendation:** Accept — bible documents MemoryRouter/jsdom constraint; AST-1335 hook suite owns blocker/confirm contract. Optional integration follow-on if parent UAT wants end-to-end leave prompt on Profile.

### advisory — Epic branch bible drift (`AST-1331` manifest missing vs `origin/dev`)

**Location:** `docs/test-bible/frontend/pages.md` on publish tip  
**Finding:** `origin/dev` retains `### AST-1331 · AST-1330` at ~line 1826; publish tip lacks it. Betty’s AST-1336 commit only **prepended** the AST-1336 block — deletion is epic merge-base integration debt, not Katherine product scope.  
**Recommendation:** Downstream for Chuckles at `merge-child` / `prep-uat`: restore `AST-1331` bible block when landing ftr on dev — **not** an AST-1336 resolve-child item.

### advisory — `JSON.stringify` dirty equality (Joan acceptable)

**Location:** `CandidateProfile.tsx` `isDirty`  
**Finding:** Blunt equality as Joan flagged; acceptable given shared `editValuesFromCandidate` / `setByPath` origin.  
**Recommendation:** Monitor only if Profile shapes introduce key-order instability.

## What's solid

- Minimal, focused diff: 24 insertions / 4 deletions in one page file.
- `persistProfile` correctly clears dirty before promise resolves — satisfies helper contract so `blocker.proceed()` is not re-blocked.
- Hook call order respects Rules of Hooks (all hooks before conditional returns).
- Betty tests cover: clean→dirty, in-page tab draft retention, Cancel revert, `onSave` success clears dirty, `onSave` failure stays dirty + surfaces error.
- Prior save-failure test updated to call `onSave()` directly — correct given `persistProfile` rethrow + `void handleSave()`.
- AST-1335 hook suite restored after merge-tests (`0433ab37`).

## Frame diff

| Planned | Landed |
|---------|--------|
| `handleSave` early `if (!selectedId) return` | `persistProfile` rejects when `!selectedId`; Save button not rendered in that state |
| No test changes in engineer scope | Betty mocked helper + AST-1336 wiring describe block |
| — | `0433ab37` restores AST-1335 hook test file post merge-tests |

## Notes

- §5f / §5g not triggered (UI page wiring only).
- `blockedBy AST-1335 (User Testing)` prerequisite satisfied on publish ref.
- Downstream for Chuckles: append artifact, `docs(AST-1336): Radia review — clean`, post slim upshot, Review Posted → PROCEED path.

context_tokens≈38000

---

```
[code-rubric] PROCEED (Commit: 92637061) Profile wiring clean
```
