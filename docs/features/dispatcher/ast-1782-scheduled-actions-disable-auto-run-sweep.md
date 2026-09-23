# AST-1782 — Scheduled Actions disable AUTO and Run/Sweep

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1782
- **Parent:** AST-1766 — Dispatch Validation
- **Publish ref:** `sub/AST-1766/AST-1782-scheduled-actions-disable-auto-run-sweep`

UI-only: honor sibling #2’s list boolean `empty_render` on Scheduled Actions so AUTO and Run/Sweep are non-interactive and visually muted when the flag is true. Stop/Drain and Debug stay unchanged. No client-side `resolve_tokens` / `TOKEN_SOURCES`. Does not own the predicate (AST-1779) or API 400 / force-off (AST-1780).

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — disable AUTO and Run/Sweep from the list flag only.

No other files. Do not edit `api_admin.py`, `config.py`, `database.py`, `candidate.py`, or any other frontend page/component.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Type `empty_render`; mute + block AUTO badge and Run/Sweep when true; handlers no-op; Debug/Stop/Drain untouched | ui |

## Stage 1: Honor `empty_render` on list AUTO + Run/Sweep

**Done when:** With a list row whose JSON includes `empty_render: true`, the AUTO badge does not fire `PUT` with `auto_mode: true` (or any AUTO toggle), and the Run/Sweep control does not fire `POST …/run` — both look muted (≈ same visual language as today’s Sweep-blocked Run: reduced opacity + non-pointer). Debug and Stop/Drain still work. A row with `empty_render: false` (or missing/falsy) keeps current AUTO + Run/Sweep behavior subject to existing `isRunning` / Sweep/`min_count` rules. Grep of this file shows no `resolve_tokens` / `TOKEN_SOURCES` string.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, on `interface DispatchTask`, add optional:

   ```typescript
   empty_render?: boolean
   ```

   after `always_visible_under_avail_gt0?: boolean` (or beside other enrichment fields). Do **not** invent a second flag name — the list field is exactly `empty_render` (frozen by AST-1779 / shipped by AST-1780).

2. In `ScheduledPhaseTable`’s row map (where `isSweep` / `sweepDisabled` are computed), add:

   ```typescript
   const emptyRender = !!row.empty_render
   ```

   Derive control disable flags (names optional; behavior mandatory):

   - AUTO blocked when `emptyRender` is true.
   - Run/Sweep blocked when `isRunning || sweepDisabled || emptyRender` (preserve today’s running + Sweep/`min_count` rules; add empty-render as an additional gate).

3. **AUTO badge** (`dispatch-status-badge` in the AUTO column):

   - When `emptyRender`:
     - Do **not** call `toggleAutoMode` (omit `onClick` handler or make it `e => { e.stopPropagation() }` only — no `toggleAutoMode`).
     - Visually mute: keep the ON/OFF label accurate to `row.auto_mode`, but force muted styling — use `dispatch-status-muted` for the className when blocked (even if AUTO is somehow still ON), set `style` to `{ cursor: "default", border: "none", opacity: 0.25 }` (or opacity on par with Sweep-blocked Run), and set `disabled={true}` if the element supports it; if `button` + `disabled` fights badge CSS, prefer `pointerEvents: "none"` + `opacity: 0.25` + `cursor: "default"` without changing label text.
   - When not `emptyRender`: leave today’s clickable badge (`toggleAutoMode`, `cursor: "pointer"`) unchanged.

4. **Run/Sweep button** (the `btn primary in-row` control):

   - Extend `disabled` to `isRunning || sweepDisabled || emptyRender`.
   - Extend `style.opacity` / `pointerEvents` the same way: when `emptyRender` (and not already hidden by `isRunning`), use the muted opacity (`0.25`) and `pointerEvents: "none"` — same as `sweepDisabled` today.
   - Stop overlay (when `isRunning`) stays as today — empty-render does **not** disable Stop/Drain.

5. **Handlers** (defense in depth so a stray click cannot PUT/POST):

   - At the top of `toggleAutoMode`, after the function opens: if `!!row.empty_render`, `return` immediately (no `api` call).
   - At the top of `handleRun`, after `e.stopPropagation()`: if `!!row.empty_render`, `return` immediately (no `api` call).

6. **Do not change:** Debug toggle, Stop/Drain, Kill-all, filters, create/edit modal `auto_mode` checkbox, row `openEdit` rules, or Available counts. Server already 400s AUTO-on / run when empty-render (AST-1780); this ticket only stops the UI from sending those clicks.

7. **Do not** import or reimplement `resolve_tokens`, `TOKEN_SOURCES`, or any token-resolution helper in this file (parent AC 8 / child AC 3).

⚠️ **Decision:** Read only `empty_render` from the list payload — no client-side re-check of prompts. Sibling #2 owns truth; UI trusts the boolean.

⚠️ **Decision:** Mute both directions of AUTO (cannot turn on **or** off from the badge while flagged). Force-off persistence is already AST-1780 list enrichment; the badge should not be a workaround click path.

⚠️ **Decision:** Create/edit modal AUTO checkbox is out of scope (Scope: list flag / row controls). Modal AUTO-on still fails closed via AST-1780 API 400 if someone checks it.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1782
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `ff280dda6d25e945c25e78291b29244a66df74ac`

## Canon scores

| slug | grade | effort | note |
|------|-------|--------|------|
| astral.dispatch.entity-state-bound | X | | Presentational client-only slice; `AdminScheduledActions.tsx` not in statute `applies_when` paths. Plan conforms to epic partition by trusting sibling #2 per-row `empty_render` and forbidding client token resolution — no `dispatch_task` / entity_type persistence edits. |

## Traceability

AC2→Stage 1 (mute + block list AUTO badge and Run/Sweep when `empty_render`; handler no-ops); AC3→Stage 1 step 7 (no `resolve_tokens` / `TOKEN_SOURCES`); AC4→Stage 1 (`emptyRender` gate only — falsy/missing preserves existing `sweepDisabled` / `min_count` behavior; job-token truth owned by sibling #2). Parent AC 2, 8 → Stage 1; parent AC 10 UI slice → Stage 1 (trust boolean); parent AC 1, 3–7, 9 → out of scope (siblings #1–#3 / API).

## Findings

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Ticket Citations vs plan footprint
- **Finding:** `astral.ui.frontend-file-placement` and `astral.standards.in-scope-only` plainly govern a single-page frontend change but are absent from the frozen one-id list.
- **Recommendation:** Plan is compliant via `## Explicit scope gate` (one file only). Archie may amend Canon Scope for Radia comparability; no plan change required.

### acceptable — AUTO badge blocks toggle-off while flagged

- **Severity:** acceptable
- **Location:** Stage 1 step 3 + Decision “Mute both directions”
- **Finding:** Child AC 2 fail text names `PUT` `auto_mode: true`; plan also blocks turning AUTO off from the list badge while `empty_render` is true.
- **Recommendation:** Reasonable fail-closed UX (no badge workaround); AST-1780 already force-offs persisted AUTO. No plan change required.

### acceptable — Create/edit modal AUTO unchanged

- **Severity:** acceptable
- **Location:** Stage 1 step 6 + Decision on modal checkbox
- **Finding:** Modal AUTO-on remains possible in UI; AST-1780 API 400 is the backstop.
- **Recommendation:** Matches ticket Scope (“list flag / row controls only”). No plan change required.

context_tokens≈42000
