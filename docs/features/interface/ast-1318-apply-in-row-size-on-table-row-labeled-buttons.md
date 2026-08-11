# AST-1318 — Apply in-row size on table-row labeled buttons (Add a button style for in-row buttons)

- **Linear:** [AST-1318](https://linear.app/astralcareermatch/issue/AST-1318/apply-in-row-size-on-table-row-labeled-buttons-add-a-button-style-for)
- **Parent:** [AST-1309](https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons)
- **Publish ref:** `sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons`

After AST-1317 landed unused `.btn.in-row` and amended `pattern.ui.shared-button-roles`, add the `in-row` size class on every labeled shared-role button that already sits in a data-table row. On this tree that is exactly two controls: Scheduled Actions row Run and row Stop (including the in-row busy label `Draining…`). Presentation only — do not change handlers, enablement, labels, overlay positioning, or any full-size / icon-control surface.

## Traceability

| Parent / child item | This plan |
|---------------------|-----------|
| Purpose — compact in-row size so lists stay dense | Stage 1 (consume AST-1317 size; do not restyle CSS) |
| Functional scope 1 — in-row size on the labeled family | N/A — AST-1317 already landed `.btn.in-row` + catalog |
| Functional scope 2 — apply to every labeled shared-role button in a data-table row, including SA Run / Stop | Stage 1 |
| Functional scope 3 — leave full-size and icon-only alone | Stage 1 leave-alone list |
| Child AC2 / parent AC2 — labeled button in a data-table row uses in-row size (~60% of page/toolbar labeled height) | Stage 1 (shared `.btn.in-row` already is that height) |
| Child AC3 / parent AC3 — SA row Run / Stop (including in-row busy/stop label) use in-row size and no longer set row height to full labeled-button size | Stage 1 |
| Child AC4 / parent AC4 — page, toolbar, modal, card-footer labeled buttons stay full size | Stage 1 leave-alone (do not add `in-row` there) |
| Child AC5 / parent AC5 — icon-only row actions stay icon-controls | Stage 1 leave-alone (`CandidateJobRowActions`, Manage Candidates glyphs, modal ×) |
| Child AC6 / parent AC6 — no enablement or action change (including SA auto-mode / running gating) | Stage 1 hard rule: className token only |
| Child AC1 / parent AC1 — catalog documents `in-row` | N/A — AST-1317 |
| In-row size lock (token, pairings, ~60% height, not a fifth role) | Consume existing `.btn.in-row`; markup `btn <role> in-row` |
| Boundary — does not land catalog/style | Do not edit `App.css` or `canon/patterns/**` |
| Boundary — does not restyle page/toolbar/modal-footer/card-footer | Leave-alone list |
| Boundary — does not convert labeled ↔ icon-control | Leave-alone list |
| Notes — after #1; presentation only | Prerequisite: AST-1317 on this worktree; Stage 1 className only |

## Inventory (this worktree)

Exhaustive pass: every `className` containing `btn` under `src/ui/frontend/src/**/*.tsx`, crossed with every file that contains a `<td>`.

**In scope — labeled `btn` inside a data-table `<td>` (the complete set):**

| File | Control | Current `className` | New `className` |
|------|---------|---------------------|-----------------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Row Run (label `Run`) | `btn primary` | `btn primary in-row` |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Row Stop / busy (label `Stop` or `Draining…`) | `btn danger` | `btn danger in-row` |

There is no `btn secondary` and no `btn primary in-flight` in a data-table row on this tree. Do not invent those call sites.

**Not a data-table row (do not add `in-row`):**

- Scheduled Actions toolbar: Stop All (`btn danger`), `+ Add Task` (`btn primary`).
- Scheduled Actions modals: Cancel / confirm Stop All / Save (`btn secondary` / `btn danger` / `btn primary`).
- `ListPage` bulk bar (`btn primary` / `btn danger`) — toolbar, not a `<td>`.
- Admin Scheduled Queries Edit / Deactivate / Delete (`btn secondary` / `btn danger`) — card body actions, not a `<table>` row. Parent AC4 / boundary leave card-footer labeled buttons full size.
- Every other `btn primary` / `btn secondary` / `btn danger` / `btn primary in-flight` in pages, toolbars, modal footers, and card/header action bars.

**Not a labeled button (do not convert or restyle):**

- SA AUTO / Dbg cells: `dispatch-status-badge` toggles (parent: do not restyle AUTO / Debug status-badge toggles).
- Job-list row actions: `CandidateJobRowActions.tsx` (`icon-control`).
- Manage Candidates row View / Edit / Delete: `icon-control`.
- Modal close × and section chevrons: `icon-control`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Add `in-row` to the two row Run / Stop `className` strings only | ui |

**Do not touch:** `src/ui/frontend/src/App.css` (`.btn.in-row` already exists); `canon/patterns/**`; any other `*.tsx` / `*.ts`; `src/ui/api/**`; `src/utils/config.py`; `docs/ASTRAL_CODE_RULES.md`; `tests/**`; `docs/test-bible/**`; `CandidateJobRowActions.tsx`; `.icon-control` CSS; `.btn` / role / in-flight / disabled declarations.

**Do not add:** `Button.tsx`, a second stylesheet, a `:root` size token, a `config.py` size enum, a fifth role, a wrapper component, a `td .btn` descendant rule, or per-call-site `padding` / `fontSize` / `minHeight`.

---

## Stage 1: Add `in-row` on Scheduled Actions row Run / Stop

**Done when:** The Run button in the Scheduled Actions data-table Run column has `className="btn primary in-row"`. The overlay Stop button has `className="btn danger in-row"`. Labels remain `Run`, `Stop`, and `Draining…`. `disabled`, `onClick`, `style`, and the `{isRunning && (…)}` overlay are unchanged. Toolbar Stop All / Add Task and both modal footers still use full-size `btn` classes with no `in-row`. `rg -n 'in-row' src/ui/frontend/src --glob '*.tsx'` matches only those two `className` lines in `AdminScheduledActions.tsx`.

1. Confirm prerequisite on this worktree (do not edit these files): `src/ui/frontend/src/App.css` already contains `.btn.in-row { padding: 3px 20px; line-height: 1.2; }` (AST-1317). `canon/patterns/ui/pattern.ui.shared-button-roles.md` already documents optional `in-row` paired with a role. If either is missing, stop and comment on parent AST-1309 — do not invent CSS or catalog text.

2. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, in the Run column `<td>` (the cell whose header is `Run`, the `<div style={{ position: "relative", display: "inline-block" }}>` wrapper), change **only** the Run button's `className` from `"btn primary"` to `"btn primary in-row"`. Keep every other attribute exactly as written today:

```tsx
                    <button
                      className="btn primary in-row"
                      style={{ whiteSpace: "nowrap", opacity: isRunning ? 0 : (row.auto_mode ? 0.25 : 1), pointerEvents: (isRunning || row.auto_mode) ? "none" : "auto" }}
                      disabled={isRunning || !!row.auto_mode}
                      onClick={e => handleRun(e, row)}
                    >
                      Run
                    </button>
```

3. In the same wrapper, change **only** the Stop overlay button's `className` from `"btn danger"` to `"btn danger in-row"`. Keep `{isRunning && (…)}`, `style={{ position: "absolute", inset: 0, whiteSpace: "nowrap" }}`, `onClick`, `disabled={isDraining}`, and the label `{isDraining ? "Draining…" : "Stop"}` exactly as written:

```tsx
                      <button
                        className="btn danger in-row"
                        style={{ position: "absolute", inset: 0, whiteSpace: "nowrap" }}
                        onClick={e => handleStop(e, row)}
                        disabled={isDraining}
                      >
                        {isDraining ? "Draining…" : "Stop"}
                      </button>
```

4. Do **not** add `in-row` to any other `className` in this file. Leave these exact current strings:

   - Toolbar Stop All: `className="btn danger"` (the button whose label is `Stop All`).
   - Toolbar add: `className="btn primary"` (the button whose label is `+ Add Task`).
   - Stop-all modal footer: `className="btn secondary"` (Cancel) and `className="btn danger"` (confirm kill).
   - Edit/add task modal footer: `className="btn secondary"` (Cancel) and `className="btn primary"` (Save).
   - AUTO / Dbg cells: `className={\`dispatch-status-badge …\`}`.
   - Modal close: `className="icon-control"`.

5. Do **not** change `handleRun`, `handleStop`, `toggleAutoMode`, `toggleDebug`, `disabled` expressions, `opacity` / `pointerEvents` gating, overlay `position` / `inset`, or visible label text.

6. Do **not** edit any other file.

⚠️ **Decision:** Apply by adding the catalog size token on the two existing `className` strings. Rejected alternatives: (a) a `td .btn` / table-descendant CSS rule — that bypasses `pattern.ui.shared-button-roles` markup (`btn <role> in-row`) and the AST-1317 unused-selector contract; (b) a wrapper component or `Button.tsx` — forbidden by the parent lock and AST-1317; (c) per-call-site padding — violates `astral.standards.no-hardcoded-sets` (size lives in `.btn.in-row`); (d) shrinking Scheduled Queries card actions — those are not data-table rows (parent AC4 / card-footer boundary).

⚠️ **Decision:** The Stop overlay is `position: absolute; inset: 0` over the always-mounted Run button. The wrapper sizes to Run. Adding `in-row` to both keeps the overlay the same compact box; do not change overlay CSS to “fix” height.

⚠️ **Decision:** No `in-flight` on Run/Stop. Run already uses opacity-0 + Stop overlay for the busy state; AST-1301 left that as text/`btn danger`, not `btn primary in-flight`. This ticket does not reopen that pairing.

---

## Execution contract

The plan is binding. Execute Stage 1 in order; one commit on the epic worktree; publish to `origin/sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons`. Do not edit `App.css`, `canon/patterns/**`, `tests/`, or `docs/test-bible/**`. On ambiguity or codebase drift (a third labeled `btn` appears inside a `<td>`, or `.btn.in-row` is missing), stop and comment on the **parent** [AST-1309](https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons) with the Stage blocked format from plan-child.

## Self-Assessment

**Scope:** `Single-Component` — two `className` tokens on one page; shared size CSS and catalog already exist from AST-1317.

**Conf:** `high` — inventory is closed (only two labeled `btn`s in any `<td>`); markup pairings are locked by the approved pattern; enablement stays byte-identical.

**Risk:** `low` — presentation-only class addition; overlay still sizes to Run; full-size and icon-control surfaces are explicitly listed as leave-alone.

## Rules self-review

| Rule | Status |
|------|--------|
| §1.1 / `astral.standards.in-scope-only` | Only the two SA row labeled buttons; no catalog/CSS (AST-1317); no icon-control convert; no full-size restyle |
| §1.3 DRY | Reuse existing `.btn.in-row`; no second size rule |
| §1.4 / `astral.standards.no-hardcoded-sets` | Size stays in shared `App.css`; no per-site padding |
| §2.1 config | No `config.py`; no new token |
| §2.4 / §2.6 | N/A — no batch or state machine |
| §3.3 imports | No new imports |
| §3.5 / `astral.ui.frontend-file-placement` | No new file; no second CSS file |
| `astral.ui.naming-conventions` | Token is `in-row` (already catalog law) |
| `astral.standards.names-not-ticket-ids` | No ticket id in class names |
| `astral.layers.ui-config-driven-business-logic` | Presentation only; auto-mode / running gating unchanged |
| `pattern.ui.shared-button-roles` | Markup `btn primary in-row` / `btn danger in-row`; always paired with a role |
| `pattern.ui.icon-control` (boundary) | Row glyphs stay `icon-control` |
| Test-tree ban | No `tests/` or bible edits |

No unresolved rule conflicts.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1318
**Overall:** APPROVED
**Publish ref:** `sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons` @ `ac4b1bd3`

## Traceability
Child AC2 (labeled button in a data-table row uses in-row size ~60% of full labeled height) → Stage 1 (`btn primary in-row` / `btn danger in-row` consume AST-1317 `.btn.in-row`). Child AC3 (SA row Run / Stop including busy `Draining…` label; no longer full labeled-button row height) → Stage 1 (both Run-column buttons). Child AC4 (page/toolbar/modal/card-footer labeled buttons stay full size) → Stage 1 leave-alone list. Child AC5 (icon-only row actions stay icon-controls) → Stage 1 leave-alone (`CandidateJobRowActions`, Manage Candidates glyphs, modal ×). Child AC6 (no enablement/action change; SA auto-mode/running gating unchanged) → Stage 1 hard rule (className token only). Child AC1 / parent AC1 (catalog documents `in-row`) → N/A — AST-1317. Parent functional scope 2 → Stage 1 exhaustive inventory (only two labeled `btn`s inside any `<td>` on this tree: `AdminScheduledActions.tsx` Run + Stop overlay).

**Considered:** Universal orch.* set + scoped `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.layers.ui-config-driven-business-logic` — all `conforms` (in-session; no statute-table rows required).

context_tokens≈48000
```

**Gate summary:** AST-1318 is **Plan Ready**, assignee Joan, publish tip `ac4b1bd3`. Prerequisite AST-1317 is present on the epic worktree (`.btn.in-row` in `App.css`; pattern amended). Independent inventory pass confirms the plan's closed set: only `AdminScheduledActions.tsx` row Run / Stop labeled buttons live inside `<td>`; all other `btn` usages are toolbar, modal, card-body, or bulk-bar; row actions elsewhere are `icon-control`. Stage 1 is presentation-only (`className` token add), rejects `td .btn` descendant rules and per-call-site sizing, and preserves overlay geometry and enablement gating. Self-assessment (`Single-Component`, high conf, low risk) matches footprint. No `fix-now` or blocking `discuss` findings. Plan Discuss round count: 0 (first pass from Plan Ready).

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons`  
**Product commits:** `b0dfa249` (SA row Run / Stop `in-row` className)

## Radia review

# Radia review — AST-1318

**Status gate:** Tests Passed (spawn prompt; trusted)  
**Baseline:** `origin/dev`  
**Publish ref:** `origin/sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons` @ `7e75f0e487a9d3bc0dcb647025c830b6202ba2b1`  
**AST-1318 product delta:** `b0dfa249` — two `className` tokens in `AdminScheduledActions.tsx` only  
**Diff change set (publish tip):** layers `ui` + `docs`; paths include predecessor AST-1317 canon/CSS plus AST-1318 TSX apply, issue docs, Betty test-bible/tests via `merge-tests`

---

```
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1318
**Publish ref:** origin/sub/AST-1309/AST-1318-apply-in-row-size-on-table-row-labeled-buttons @ 7e75f0e4
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent-layer diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent-layer diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no agent-layer diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-layer diff |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-layer diff |
| astral.batch.claim-process-release | scoped | not-applicable | no batch-layer diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch-layer diff |
| astral.config.config-source-of-truth | scoped | not-applicable | no config-layer diff |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug-artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug/spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch-layer diff |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch-layer diff |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | predicate paths `docs/features/**` not in AST-1318 engineer delta |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty test/bible commits only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commit `b0dfa249` touches only `AdminScheduledActions.tsx`; tests/bible via Betty merge |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no core/external diff |
| astral.layers.import-direction | scoped | not-applicable | no Python imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts-layer diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | `className` token only; handlers, `disabled`, opacity/pointerEvents, overlay geometry unchanged |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no data/coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render/consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth diff |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed/json diff |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed/catalog conflict |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed/boot paths |
| astral.seed.define-approved | scoped | not-applicable | no define/seed paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed/data diff |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data-layer diff |
| astral.standards.database-header-inventory | scoped | not-applicable | no database/migration diff |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging diff |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses AST-1317 `.btn.in-row`; no per-call-site sizing or wrapper |
| astral.standards.in-scope-only | scoped | conforms | closed inventory: only SA row Run/Stop; no App.css/canon edits in engineer commit |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging diff |
| astral.standards.names-not-ticket-ids | scoped | conforms | catalog token `in-row` only |
| astral.standards.no-cross-contamination | scoped | conforms | single-file presentation change |
| astral.standards.no-hardcoded-sets | scoped | conforms | size consumed from shared `.btn.in-row`; no inline padding/fontSize |
| astral.standards.public-then-helpers | scoped | not-applicable | no Python module structure diff |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils/data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no state-machine diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job-state diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/dispatcher diff |
| astral.ui.frontend-file-placement | scoped | conforms | edit in existing `pages/AdminScheduledActions.tsx`; no new CSS file or wrapper |
| astral.ui.naming-conventions | scoped | conforms | `in-row` paired with `btn primary` / `btn danger` per catalog |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server/worker config diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1318)` on publish tip |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` vocabulary respected |
| orch.git.flow-direction-inviolable | universal | conforms | sub-branch publish |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/AST-1309/AST-1318-…` |
| orch.git.merge-on-checkout | universal | conforms | no merge/checkout violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear stage commits |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1309` worktree |
| orch.git.three-permanent-branches | universal | conforms | no fourth permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no unresolved product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 executed per binding plan |
| orch.pipeline.project-scoped-queues | universal | conforms | child scope matches AST-1309 child #2 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed gate |
| orch.roles.archie-approves-statutes | universal | conforms | consumes approved `pattern.ui.shared-button-roles` amendment |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible edits via Betty merge + qa-handoff fix |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a to diff content |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy product commit scoped to plan file |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer commit avoids banned test-tree paths |

**Straggler (C4):** Joan APPROVED attachment lists no Excluded statutes — no straggler rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.shared-button-roles | conforms | `btn primary in-row` / `btn danger in-row` on SA table-row labeled controls; toolbar/modal/card buttons leave full size |
| pattern.ui.icon-control | conforms (boundary) | AUTO/Dbg badges and modal × remain `icon-control` / `dispatch-status-badge`; no labeled↔icon conversion |

## Plan adherence

- **Stage 1:** Run column Run → `btn primary in-row`; overlay Stop/Draining → `btn danger in-row`; all other attributes byte-identical to plan snippets.
- **Leave-alone:** Toolbar Stop All / `+ Add Task`, both modal footers, AUTO/Dbg badges, modal × — no `in-row` (verified in source).
- **Boundaries:** Engineer did not edit `App.css`, `canon/patterns/**`, or other TSX; prerequisite `.btn.in-row` consumed from AST-1317 on branch.
- **Inventory:** Independent pass confirms only labeled `btn` inside any `<td>` on this tree is the SA Run/Stop pair — exhaustive set covered.
- **Estimate (2):** footprint matches — two-token single-file apply.
- **C6 aids (§5a–§5g):** N/A beyond presentation/className — no imports, logging, debug contract, external layer, batch, or API changes.

## Findings

**fix-now:** none  

**discuss:** none  

**advisory:** Publish-tip three-dot diff includes predecessor AST-1317 canon/CSS commits on the same sub branch — expected rollup shape; AST-1318 product scope remains the two `className` lines in `b0dfa249`.

## What’s solid

- Presentation-only apply exactly as catalog specifies — no enablement, handler, overlay CSS, or label changes.
- Closed inventory honored; no `td .btn` descendant rule or per-call-site sizing shortcuts.
- Betty tests cover row Run/Stop/Draining `in-row` plus toolbar/modal leave-alone; qa-handoff corrected `mockApi(true)` for Stop All modal path.

## Frame diff

`AdminScheduledActions.tsx` → `ScheduledPhaseTable` Run column `<td>`: Run button `className` gains `in-row`; conditional Stop overlay `className` gains `in-row`. No structural/DOM/routing changes; row height driven by compact labeled buttons via shared CSS.

## Notes

Joan plan-rubric verdict attached (APPROVED @ `ac4b1bd3`). Prerequisite AST-1317 present on branch (`.btn.in-row` in `App.css`; pattern amended). Betty `merge-tests` + qa-handoff fix (`9b2b44a1` / `7e75f0e4`) align manifest with leave-alone modal assertions.

context_tokens≈48000

---

```
[code-rubric] PROCEED (Commit: 7e75f0e4) SA row in-row apply
```

**C7:** Complete — Chuckles may append to the issue doc, push `docs(AST-1318): Radia review — clean`, post slim upshot `--as radia`, and move to **Review Posted** → **User Testing** (PROCEED, no fix-now/discuss).
