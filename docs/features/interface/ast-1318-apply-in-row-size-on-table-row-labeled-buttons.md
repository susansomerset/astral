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
