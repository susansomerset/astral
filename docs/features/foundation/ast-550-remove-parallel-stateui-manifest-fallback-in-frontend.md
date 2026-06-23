<!-- linear-archive: AST-550 archived 2026-06-15 -->

## Linear archive (AST-550)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-550/remove-parallel-stateui-manifest-fallback-in-frontend-strengthen-the  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-484 — Strengthen the relationships between lookup lists in the UI and live values in config  
**Blocked by / blocks / related:** parent: AST-484

### Description

## What this implements

Remove the parallel `StateUiContext.tsx` `EMPTY` constant that duplicates the full shape of `build_state_ui_manifest()`. The frontend must consume `/api/state_ui_manifest` only, with a minimal loading state while the manifest loads. Preserve a legacy/unmapped affordance for stored row values that are no longer present in the current config manifest.

## Acceptance criteria

1. `StateUiContext.tsx` no longer defines a full duplicate manifest (`EMPTY` or equivalent hardcoded manifest shape).
2. Jobs/companies UI consumes the API manifest as the sole source of state vocabulary (G1 pattern preserved).
3. Loading state is minimal (no fake manifest used as fallback).
4. Stored rows with legacy state values not in the current manifest display a clear legacy/unmapped affordance rather than breaking or silently hiding data.
5. Adding a new key to in-scope config state tuples surfaces in the UI without editing a separate frontend seed list.
6. Component tests updated so mocks reflect API-driven manifest (Betty manifest pass as usual).

## Boundaries

* Does **not** retire backend dispatch seeds — sibling **AST-549** (Ada).
* Does **not** refactor `config.py` into a package (\[AST-346\]).
* Does **not** change business rules for jobs/companies state transitions — only manifest consumption in the UI layer.
* Does **not** touch board search UI (Boards iceboxed).

## Notes for planning

* Primary files: `StateUiContext.tsx` and consumers of state UI manifest in React.
* Precedent: `GET /api/state_ui_manifest` + `build_state_ui_manifest()` already correct on backend — this ticket is frontend-only.
* **Blocked by AST-549** only if shared admin/dispatch work must land first; primary dependency is none for manifest API (already exists). Blocking set for epic sequencing per dispatch.
* Secondary domain: Katherine owns React; coordinate with Ada if admin surfaces share types.

## Git branch (authoritative)

Per **orientation-astral** Branch law: parent `ftr/ast-484-strengthen-lookup-config-ui`, child `sub/AST-484/AST-550-remove-stateui-manifest-fallback`. Created at **dispatch-linear**. Engineers cherry-pick to `origin/<ftr-ref>` or `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-06-03T00:18:07.725Z
**Review** — `origin/dev...origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` @ `a67db974` (product); review doc @ `480aeded` on publish ref.

**Plan fidelity (AST-550):** All acceptance criteria met on the product diff — `EMPTY` deleted, API-only `StateUiContext` with `loadState`, per-page guards, legacy sections via `stateUiSections.ts`, test fixture + updated component tests. Scope stays frontend-only; no AST-549 / config.py smuggle.

**ASTRAL_CODE_RULES**
- **§2.1 / G1 (§3.2):** Sole runtime vocabulary from `GET /api/state_ui_manifest`; no parallel TS state machine. **Solid.**
- **§1.3 DRY:** Shared `unmappedJobStates` / `legacyStateSectionLabel` across three job list pages. **Solid.**
- **Epic AST-484 fail-loud:** Fetch error → `loadState: "error"`, `manifest: null`, user-facing “State UI manifest unavailable.” — no `EMPTY` restore. **Solid.**

**advisory**
- `ArtifactEditor.tsx`, `ArtifactsCompanySearchTerms.tsx` — `manifest?.candidate.artifact_generate_states ?? []` before render guard disables Generate during manifest load; acceptable unless Katherine wants stricter gating.

**fix-now:** none — happy path to **`resolve-astral`** on `dev-kath`.

**discuss:** none.

**Doc:** `docs/features/foundation/ast-550-remove-parallel-stateui-manifest-fallback-in-frontend.md` (Radia section) on `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` @ `480aeded`.

#### betty — 2026-06-03T00:11:20.091Z
**QA manifest (AST-550)** — `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` @ `a67db974`

Coverage: **§7.13zq** (parent **AST-484**). Katherine’s component tests on the publish tip; bible maps manifest below.

1. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx`
   — API load → `loadState: ready`; failed fetch → `loadState: error`, `manifest: null` (no `EMPTY` fallback).

2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx`
   — §6c routed page; legacy section for `RETIRED_EXAMPLE_STATE` not in manifest fixture.

3. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx`
   — §6c routed Recommended page regression (manifest via `installBaseApiMocks` / `STATE_UI_MANIFEST_FIXTURE`).

4. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/test_App.test.tsx`
   — index redirect smoke with `StateUiProvider` (manifest reject path on shell only).

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `3a3dc43bf5abf1fb2c77a751154fe174ef74cc47`

#### katherine — 2026-06-02T22:34:15.870Z
Plan: `docs/features/foundation/ast-550-remove-parallel-stateui-manifest-fallback-in-frontend.md`

GitHub: https://github.com/susansomerset/astral/blob/sub/AST-484/AST-550-remove-stateui-manifest-fallback/docs/features/foundation/ast-550-remove-parallel-stateui-manifest-fallback-in-frontend.md (`origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` @ `3bc1048e`)

**Scope:** `Single-Component` — Removes the duplicated `EMPTY` manifest in `StateUiContext`, loads only from `/api/state_ui_manifest`, and adds shared legacy-section helpers on the three job list pages.

**Conf:** `high` — G1 backend manifest is already correct; this is deleting drift-prone TS and wiring loading guards on existing consumers.

**Risk:** `Medium` — In Review / Skipped / Recommended depend on manifest load timing; mistakes could briefly blank those pages until fetch completes.

Four stages: (1) context + `stateUiSections.ts`, (2) job pages + legacy sections, (3) company/artifact/modal guards, (4) test fixture + `page-mocks` + context/page tests. No `config.py` changes.

---

# Remove parallel StateUi manifest fallback in frontend

**Linear (this ticket):** [AST-550](https://linear.app/astralcareermatch/issue/AST-550/remove-parallel-stateui-manifest-fallback-in-frontend-strengthen-the)  
**Parent:** [AST-484](https://linear.app/astralcareermatch/issue/AST-484/strengthen-the-relationships-between-lookup-lists-in-the-ui-and-live-values-in-config)  
**Publish ref:** `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback`

## Summary

`StateUiContext.tsx` still ships a ~100-line `EMPTY` constant that mirrors `build_state_ui_manifest()` in `src/utils/config.py`. That duplicate vocabulary drifts (today `EMPTY` omits `PASSED_LIKE` / `PASSED_LIKE_RETRY` in-review rows present in config). This ticket deletes the parallel manifest, loads vocabulary only from `GET /api/state_ui_manifest`, uses a minimal loading/error surface until the API responds, and adds a **legacy / unmapped** affordance on job list pages so rows whose `state` is absent from the current manifest still render instead of disappearing.

**Out of scope:** Backend `build_state_ui_manifest()` changes, dispatch seed retirement (**AST-549** / Ada), `config.py` package refactor (**AST-346**), board search UI, business rules for state transitions, `docs/ASTRAL_TEST_BIBLE.md` (Betty after Code Complete).

**Dependency note:** Linear lists **blockedBy AST-549** for epic sequencing; manifest API and G1 backend manifest already exist — implementation does not require AST-549 to land first.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/contexts/StateUiContext.tsx` | Remove `EMPTY`; expose `loadState` + nullable `manifest`; API-only load; no catch fallback to fake manifest | ui |
| `src/ui/frontend/src/lib/stateUiSections.ts` | New helpers: legacy label, collect unmapped job states, append legacy sections | ui |
| `src/ui/frontend/src/pages/JobsInReview.tsx` | Guard on `loadState`; build sections from API manifest + legacy append | ui |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Same pattern for skipped `section_order` / `section_labels` | ui |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Same pattern for `recommended.sections` | ui |
| `src/ui/frontend/src/pages/CompaniesWatchList.tsx` | Manifest load guard before using `bulk_transitions` | ui |
| `src/ui/frontend/src/pages/CompaniesInactiveList.tsx` | Manifest load guard | ui |
| `src/ui/frontend/src/pages/CompaniesIgnored.tsx` | Manifest load guard | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | Manifest load guard for `artifact_generate_states` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Manifest load guard | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Optional legacy hint on State row when state ∉ manifest grade/detail keys (read-only) | ui |
| `src/ui/frontend/src/components/CompanyDetailModal.tsx` | Manifest load guard for `watch_readonly_states` | ui |
| `tests/component/frontend/fixtures/stateUiManifestFixture.ts` | Test-only manifest JSON (not imported by production code) | tests |
| `tests/component/frontend/pages/page-mocks.ts` | Return fixture on `/api/state_ui_manifest` instead of rejecting | tests |
| `tests/component/frontend/contexts/test_StateUiContext.test.tsx` | Assert loading → ready; assert error leaves `manifest` null | tests |
| `tests/component/frontend/pages/test_JobsInReview.test.tsx` | Legacy section test; drop reliance on EMPTY offline fallback | tests |
| Other `tests/component/frontend/**` touching `/api/state_ui_manifest` | Only if a test fails after `page-mocks` change — align handlers to fixture | tests |

**Not in scope:** `src/utils/config.py`, `api_system.py`, admin dispatch UI, CSS theme files (reuse existing `list-page-status`).

## Stage 1: API-only `StateUiContext` + section helpers

**Done when:** `EMPTY` is deleted; `npx tsc -b --noEmit` passes under `src/ui/frontend`; provider never assigns a fake manifest on fetch failure.

1. Create `src/ui/frontend/src/lib/stateUiSections.ts` with:

   ```typescript
   export const LEGACY_STATE_LABEL_SUFFIX = " (legacy — not in current manifest)"

   export function legacyStateSectionLabel(state: string): string {
     return `${state.replace(/_/g, " ")}${LEGACY_STATE_LABEL_SUFFIX}`
   }

   /** States present on rows but not listed in the manifest vocabulary for this view. */
   export function unmappedJobStates(rows: Array<{ state: string }>, knownStates: Iterable<string>): string[] {
     const known = new Set(knownStates)
     const extra = new Set<string>()
     for (const row of rows) {
       if (row.state && !known.has(row.state)) extra.add(row.state)
     }
     return [...extra].sort()
   }
   ```

2. In `src/ui/frontend/src/contexts/StateUiContext.tsx`:
   - Delete the entire `EMPTY` constant (lines 30–128) and the comment *"Until GET returns — mirrors …"*.
   - Change context type to:

     ```typescript
     export type StateUiLoadState = "loading" | "ready" | "error"

     export type StateUiContextValue = {
       manifest: StateUiManifest | null
       loadState: StateUiLoadState
     }
     ```

   - Default context value: `{ manifest: null, loadState: "loading" }`.
   - In `StateUiProvider`, `useState` initial `{ manifest: null, loadState: "loading" }`.
   - `useEffect` fetch:

     ```typescript
     api("/api/state_ui_manifest")
       .then(r => { if (!r.ok) throw new Error(String(r.status)); return r.json() })
       .then((body: StateUiManifest) => setValue({ manifest: body, loadState: "ready" }))
       .catch(() => setValue({ manifest: null, loadState: "error" }))
     ```

     **Do not** call `setManifest(EMPTY)` in `catch`.

   - Replace `useStateUi(): StateUiManifest` with `useStateUi(): StateUiContextValue` (export type).

3. Run `cd src/ui/frontend && npx tsc -b --noEmit` — expect errors listing consumers; Stage 2–3 fix them. Stage 1 commit may be deferred until Stage 2 if Susan prefers one green `tsc` commit — **build-astral** should land Stage 1+2 together before first publish commit if `tsc` is enforced pre-commit.

⚠️ **Decision:** No app-wide blocking spinner in `App.tsx` — each page that calls `useStateUi()` shows existing `list-page-status` loading/error copy (minimal blast radius, matches other pages’ data loading).

## Stage 2: Job list pages — loading guard + legacy sections

**Done when:** In Review / Skipped / Recommended render manifest-driven sections only after `loadState === "ready"`; jobs whose `state` is not in the manifest vocabulary for that view appear in legacy sections at the bottom; empty manifest vocabulary still shows list loading, not fake sections.

1. **`JobsInReview.tsx`**
   - Destructure `const { manifest, loadState } = useStateUi()`.
   - After existing `loading` (jobs fetch) check, add:

     ```typescript
     if (loadState === "loading") return <div className="list-page-status">Loading...</div>
     if (loadState === "error" || !manifest) return <div className="list-page-status">State UI manifest unavailable.</div>
     ```

   - Replace `stateUi` with `manifest` in `useMemo` for `sections`.
   - Build `knownStates` from `manifest.jobs.in_review_sections.map(r => r.state)`.
   - After building `normal` sections (existing `order.filter(…)` logic), call `unmappedJobStates(rows, knownStates)` and for each extra state append:

     ```typescript
     { state, label: legacyStateSectionLabel(state), jobs: byState[state], gradeKey: manifest.jobs.grade_field_by_job_state[state] || "" }
     ```

     Append legacy sections **after** manifest-ordered sections.

2. **`JobsSkipped.tsx`**
   - Same `loadState` / `manifest` guards at top of render.
   - `knownStates` = `[manifest.jobs.skipped.below_dispatch_key, ...manifest.jobs.skipped.section_order]`.
   - Append legacy sections for row states not in `knownStates` (exclude `virtual_skip` floor rows from legacy grouping — they stay in below-dispatch section only).

3. **`JobsRecommended.tsx`**
   - Same guards.
   - `knownStates` = `manifest.jobs.recommended.sections.map(r => r.state)`.
   - Append legacy sections for unmapped states (same helper pattern; no grade columns).

4. Re-run `cd src/ui/frontend && npx tsc -b --noEmit`.

⚠️ **Decision:** Legacy section labels use raw `state` with underscores replaced by spaces plus the fixed suffix (no second TS label table). Manifest-known labels still come from API `label` fields.

## Stage 3: Remaining manifest consumers

**Done when:** No consumer reads `manifest.jobs` / `manifest.company` / `manifest.candidate` while `loadState !== "ready"`; modals remain usable once manifest is ready.

1. **`CompaniesWatchList.tsx`**, **`CompaniesInactiveList.tsx`**, **`CompaniesIgnored.tsx`**: at start of component body (before hooks that use manifest), `const { manifest, loadState } = useStateUi()`; if `loadState !== "ready" || !manifest`, return `<div className="list-page-status">` with Loading / unavailable strings matching Stage 2; else use `manifest` instead of bare `stateUi`.

2. **`ArtifactsCompanySearchTerms.tsx`** and **`ArtifactEditor.tsx`**: same guard; `new Set(manifest.candidate.artifact_generate_states)` only when ready.

3. **`CompanyDetailModal.tsx`**: if `loadState !== "ready" || !manifest`, show loading inside modal shell (reuse modal loading pattern) until manifest ready; then `watchReadonly = new Set(manifest.company.watch_readonly_states)`.

4. **`JobDetailModal.tsx`**: after `const { manifest, loadState } = useStateUi()`, when rendering State row, if `loadState === "ready" && manifest` and `job.state` is not a key in `manifest.jobs.grade_field_by_job_state` and not equal to `manifest.jobs.detail.already_skipped_state`, append a muted span: ` (legacy — not in current manifest)` next to `{job.state}`. If manifest not ready, show state string only (no suffix).

5. `cd src/ui/frontend && npx tsc -b --noEmit`.

## Stage 4: Component tests and shared manifest fixture

**Done when:** `npm test` (or project frontend component test command Betty documents) passes for touched files; no test depends on `EMPTY` offline fallback.

1. Add `tests/component/frontend/fixtures/stateUiManifestFixture.ts` exporting `STATE_UI_MANIFEST_FIXTURE: StateUiManifest` — copy the **current** shape from `build_state_ui_manifest()` output (one-time; run locally: `python3 -c "import json; from src.utils.config import build_state_ui_manifest; print(json.dumps(build_state_ui_manifest(), indent=2))"` from repo root and paste into fixture). This file is **test-only**; it does not ship to production and is not a second runtime seed.

2. In `tests/component/frontend/pages/page-mocks.ts`, change `installBaseApiMocks` so `/api/state_ui_manifest` returns `jsonResponse(STATE_UI_MANIFEST_FIXTURE)` instead of `Promise.reject(…)`.

3. Rewrite `tests/component/frontend/contexts/test_StateUiContext.test.tsx`:
   - **loads manifest:** mock API resolves fixture; `waitFor` `loadState === "ready"` and `manifest.jobs.in_review_sections[0].label` matches fixture.
   - **error path:** mock rejected; `waitFor` `loadState === "error"` and `manifest === null` (do not assert label `"New"`).

4. In `tests/component/frontend/pages/test_JobsInReview.test.tsx`:
   - Update **shows empty and fallback grade-column** test: remove manifest reject override; rely on `installBaseApiMocks` fixture.
   - Add test **legacy section for unmapped state**: mock jobs view with one row `state: "RETIRED_EXAMPLE_STATE"` not in fixture `in_review_sections`; expect section header matching `/RETIRED EXAMPLE STATE.*legacy/i` and row visible.

5. Run frontend component tests for `contexts/test_StateUiContext`, `pages/test_JobsInReview`, `pages/test_JobsRecommended`, `test_App.test.tsx` — fix any handler that still rejects manifest by adopting fixture import.

**Betty:** full bible/manifest pass remains out of scope here; only touch tests required for this ticket’s behavior.

## Self-Assessment

**Scope:** `Single-Component` — All edits sit in the React frontend (`StateUiContext`, one small `lib` helper, job/company pages, component tests); no Python or config changes.

**Conf:** `high` — Backend manifest and G1 pattern are established; AST-522 set the consumer pattern; work is deleting duplicate TS and wiring guards/helpers already used on list pages.

**Risk:** `Medium` — In Review / Skipped / Recommended are high-traffic; a loading-guard mistake could blank pages until manifest loads, but blast radius is limited to manifest consumers and is reversible.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.4 / §2.1 config as source of truth | Removes TS duplicate of `build_state_ui_manifest()`; runtime vocabulary from API only. |
| §1.3 DRY | Shared `stateUiSections.ts` for legacy grouping across three job pages. |
| §3.5 frontend placement | New helper in `lib/`; no new nested component folders. |
| G1 manifest pattern | Preserved — `GET /api/state_ui_manifest` remains sole vocabulary; no parallel state machine in TS. |
| Epic AST-484 “no silent fallback” | Fetch error surfaces explicit message; no `EMPTY` restore. |

No `conf-!!-NONE` conflicts identified.

## Review (Radia — 2026-06-02)

**Baseline:** `origin/dev`  
**Publish ref:** `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` @ `a67db974`  
**Diff:** 18 files, +508 / −182 (frontend manifest consumers, `stateUiSections.ts`, component tests, bible §7.13zq)

### What's solid

- **`EMPTY` removed**; `StateUiContext` is API-only with explicit `loadState` (`loading` | `ready` | `error`) and **no** catch-path restore of a fake manifest — matches AST-484 “fail loud” and acceptance criteria 1–3.
- **G1 / §3.2:** Runtime vocabulary comes only from `GET /api/state_ui_manifest`; `stateUiSections.ts` centralizes legacy grouping (DRY) without a second state machine.
- **Legacy affordance:** In Review / Skipped / Recommended append unmapped row states; `JobDetailModal` shows muted “(legacy — not in current manifest)” when state ∉ `grade_field_by_job_state` — AC 4.
- **Plan fidelity:** All staged consumers in the plan file are updated with load guards; test fixture is test-only (`STATE_UI_MANIFEST_FIXTURE`) and includes `PASSED_LIKE` / `PASSED_LIKE_RETRY` (fixes the drift the old `EMPTY` had).
- **Tests:** Context tests assert error → `manifest === null`; `JobsInReview` legacy section test; `page-mocks` serves fixture instead of rejecting manifest.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | `ArtifactEditor.tsx`, `ArtifactsCompanySearchTerms.tsx` | `generateStates` uses `manifest?.candidate.artifact_generate_states ?? []` before the render guard, so **Generate** stays disabled during manifest load (not wrong, but a brief UX flicker if shape loads first). No change required unless Katherine wants generate hidden until manifest ready. |
| advisory | `docs/ASTRAL_TEST_BIBLE.md` | §7.13zq / §7.13zm edits on publish tip — appropriate for Betty’s handoff; not a review blocker. |

No **fix-now** or **discuss** items for `resolve-astral`.

### Recommended actions

| Action | Owner |
|--------|-------|
| Proceed **`resolve-astral`** on `dev-kath` (happy path — no code changes requested from review). | Katherine |
| Optional: cherry-pick review doc SHA from Joan publish if the team wants the combined plan file on the sub tip. | Katherine / Chuckles |

## Resolution (Katherine — 2026-06-02)

**Review ref:** Radia comment on AST-550 (2026-06-03); plan doc @ `480aeded` on publish ref.

No product code changes required — Radia reported zero **fix-now** and zero **discuss** items. Advisory notes on artifact generate gating during manifest load accepted as-is (acceptable UX per review).

**Actions taken:**

- Merged `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` into `dev-kath` after `origin/dev`; plan doc aligned with publish ref Radia review section.
- Appended this Resolution section; no additional frontend or test-tree edits.

**Outcome:** Ticket advances to **User Testing**; resolution doc published via Joan on `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback`.

## Execution contract (build-astral)

- Execute stages in order; one commit per stage on `dev-kath`, then `git-store-code-commit` with `--session bc8dc9c9-e39f-40c6-82a4-af04978e55cd`.
- Before build: `git fetch origin && git merge origin/dev` on `dev-kath`; merge `origin/sub/AST-484/AST-550-remove-stateui-manifest-fallback` when Joan has published prior commits.
- Do not edit `src/utils/config.py` or dispatch admin files.
- Blocking ambiguity → `🛑` comment on **AST-550** (not parent) per plan-astral format.
