# AST-1830 — Sweep interval in admin API + Scheduled Actions UI

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1830
- **Parent:** [AST-1824](https://linear.app/astralcareermatch/issue/AST-1824) — Add a sweep interval to dispatch_task
- **Publish ref:** `sub/AST-1824/AST-1830-sweep-interval-admin-api-ui`
- **Depends on:** AST-1829 (already on `origin/ftr/AST-1824-add-a-sweep-interval-to-dispatch-task`)

Sibling AST-1829 added the nullable `dispatch_task.sweep_hrs` column (hours; NULL/0 = off) and wired it into `save_dispatch_task(sweep_hrs=)`, `_DISPATCH_TASK_UPDATE_COLS`, and template copy. This ticket exposes that column to Susan: the admin create/update routes accept and validate `sweep_hrs`, the list column metadata advertises it, and the Scheduled Actions page gets a numeric modal input (create + edit) and a sortable list column that shows `—` when the value is empty. The manual Run/Sweep button rule is not touched. Ships parent AC 11, 13, 14 (this ticket's AC 11–13).

## Explicit scope gate

This ticket's **## Scope** names exactly two files:

- `src/ui/api/api_admin.py` — create route takes optional float (null/empty → NULL, negative → 400); update route adds it to the allowed set with the same parsing, AUTO edit lock unchanged; `_DISPATCH_TASK_COLUMNS` adds the column.
- `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — row/form types, modal numeric input (create + edit), sortable list column showing `—` when empty; Run/Sweep button logic unchanged.

No other files. Do **not** edit `src/data/database.py` or `src/core/dispatcher.py` (AST-1829). Do not touch `tests/`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md`.

## Frozen names (from AST-1829 — consumed, not changed)

- **Column / JSON key:** `sweep_hrs` — `REAL`, nullable. Both API routes and the UI use exactly this key.
- **Insert:** `database.save_dispatch_task(..., sweep_hrs: Optional[float] = None)` (verified on ftr, `src/data/database.py` ~L8214).
- **Update:** `update_dispatch_task(task_id, sweep_hrs=...)` — `sweep_hrs` is already in `_DISPATCH_TASK_UPDATE_COLS` (~L8601).
- **List:** `list_dispatch_tasks()` uses `SELECT *`, so `sweep_hrs` is already present on every row returned by `GET /api/admin/dispatch_tasks`. No list-route code change is needed beyond the column metadata.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | `_DISPATCH_TASK_COLUMNS` += `sweep_hrs`; new `_parse_sweep_hrs` helper; `create_dtask` parses/validates + passes `sweep_hrs=` to `save_dispatch_task`; `update_dtask` adds `sweep_hrs` to `allowed`, parses/validates before the update loop | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `DispatchTask.sweep_hrs`; `DispatchFormState.sweep_hrs`; `DATA_COL_KEYS` += `sweep_hrs`; list header + cell; form defaults (2 literals) + `openEdit`; PUT + POST bodies; modal input | ui |

## Stage 1: Admin API — create/update accept `sweep_hrs`, column metadata

**Done when:** `POST /api/admin/dispatch_tasks` with `sweep_hrs: 2.5` persists 2.5; `PUT` on an AUTO-off row with `4` persists 4 and with `null` persists NULL; a negative value returns 400 on both routes; `GET /api/admin/dispatch_tasks` returns `columns` containing `{"key": "sweep_hrs", ...}`. `python3 -m py_compile src/ui/api/api_admin.py` exits 0.

1. In `src/ui/api/api_admin.py`, in `_DISPATCH_TASK_COLUMNS` (~L892), insert this entry **immediately after** the `freq_hrs` entry:
   ```python
   {"key": "sweep_hrs",      "label": "Sweep (hrs)", "type": "float"},
   ```
   Keep the existing column-aligned spacing style.

2. In `src/ui/api/api_admin.py`, add a new module-level helper **immediately above** `@admin_bp.route("/dispatch_tasks", methods=["POST"])` (`create_dtask`, ~L1128):
   ```python
   def _parse_sweep_hrs(raw: Any) -> tuple[float | None, str | None]:
       """sweep_hrs from admin JSON (AST-1830): None/"" → NULL; else a non-negative float.
       Returns (value, error); error is a 400 message. 0 is kept as 0.0 (off, same as NULL)."""
       if raw is None or (isinstance(raw, str) and raw.strip() == ""):
           return None, None
       try:
           val = float(raw)
       except (TypeError, ValueError):
           return None, "sweep_hrs must be a non-negative number"
       if val < 0:
           return None, "sweep_hrs must be a non-negative number"
       return val, None
   ```
   `Any` is already imported (`from typing import Any, Dict, Optional`, L8); do not add imports.

   ⚠️ **Decision:** One shared helper, not inline parsing in each route, so create and update can't drift apart. Non-numeric input (for example `"abc"` or a list) gets the same 400 as a negative, instead of the unhandled `float()` 500 that `freq_hrs` produces today. That's the smallest reading of "parsed as float … negative → 400" that never returns a 500. `patt.entity.batch-criteria` Arc 1 says dispatch_task rows are "validated through execution, not by code logic"; the ticket's Scope and AC 11 explicitly require the negative → 400 gate, so the ticket wins for this one field. No other field's validation changes.

   ⚠️ **Decision:** `0` persists as `0.0`, not NULL. Scope maps only null/empty → NULL, and AST-1829's `dispatch_task_sweep_due` already treats 0 as off.

3. In `create_dtask`, **immediately after** the `score_floor = ...` line (~L1151) and before `if bool(data.get("auto_mode", False)):`, add:
   ```python
   sweep_hrs, sweep_err = _parse_sweep_hrs(data.get("sweep_hrs"))
   if sweep_err:
       return jsonify({"error": sweep_err}), 400
   ```

4. In `create_dtask`, in the `save_dispatch_task(...)` call (~L1167), add `sweep_hrs=sweep_hrs,` as the last keyword argument, after `score_floor=score_floor,`.

5. In `update_dtask` (~L1257), add `"sweep_hrs"` to the `allowed` set literal (append after `"entity_type",` on the last line of the set). Do **not** change the AUTO-on edit-lock check above it (`if row.get("auto_mode") and (set(data.keys()) - {"auto_mode"})`). It already rejects `sweep_hrs` edits on AUTO-on rows.

6. In `update_dtask`, **immediately before** the line `trigger_state = data.get("trigger_state", row.get("trigger_state"))` (~L1332), add:
   ```python
   if "sweep_hrs" in data:
       sweep_hrs, sweep_err = _parse_sweep_hrs(data["sweep_hrs"])
       if sweep_err:
           return jsonify({"error": sweep_err}), 400
   ```

7. In `update_dtask`, in the `for k in allowed:` loop, add a branch **immediately before** the existing `elif k == "score_floor":  # pragma: no branch` line, so `score_floor` stays the final branch and keeps its pragma:
   ```python
   elif k == "sweep_hrs":
       updates[k] = sweep_hrs
   ```
   (`sweep_hrs` is always bound here because the loop only reaches this branch when `"sweep_hrs" in data`, which step 6 already parsed.)

8. Verify: `python3 -m py_compile src/ui/api/api_admin.py` exits 0. No Python linter is installed in this environment (`ruff` / `pyflakes` absent), so `py_compile` is the Python gate. Commit: `code(AST-1830): admin API sweep_hrs create/update/columns`.

## Stage 2: Scheduled Actions UI — types, modal input, list column

**Done when:** On Scheduled Actions, the create and edit modals show a "Sweep (hrs)" numeric input, and saving sends `sweep_hrs` (a number, or `null` when blank) in both POST and PUT bodies. The list shows a sortable "Sweep" column right after "Freq", with the value or `—`. `grep -n "sweepDisabled" src/ui/frontend/src/pages/AdminScheduledActions.tsx` still shows `!!row.auto_mode && avail >= (row.min_count || 1)`. In `src/ui/frontend`, `npx eslint src/pages/AdminScheduledActions.tsx` and `npm run build` both succeed.

1. In the `DispatchTask` interface (~L71), add after `freq_hrs: number`:
   ```ts
   sweep_hrs?: number | null
   ```

2. In the `DispatchFormState` type (~L30), add after `freq_hrs: string`:
   ```ts
   sweep_hrs: string
   ```

3. In `DATA_COL_KEYS` (~L108), insert `"sweep_hrs"` **immediately after** `"freq_hrs"`, giving `... "debug", "freq_hrs", "sweep_hrs", "min_count", ...`.
   ⚠️ **Decision:** This array must stay in the same order as the `<th>` cells, because `useListTableColumnMeasure` / `stickyLeftPx` index widths by position. The new header in step 4 goes in the matching slot.

4. In `ScheduledPhaseTable`'s `<thead>`, insert this header **immediately after** the `Freq` `<th>` (~L182):
   ```tsx
   <th className="sortable" style={{ textAlign: "right" }} title="Scheduled sweep interval (hrs): AUTO row with 0 < Avail < Min runs one batch this often since Last Run" onClick={() => toggleSort("sweep_hrs")}>Sweep{sortIcon("sweep_hrs")}</th>
   ```
   Sorting needs no other change. The generic comparator (~L460) reads `a[sortCol as keyof DispatchTask]` and already puts nulls last.

5. In the `<tbody>` row, insert this cell **immediately after** the `freq_hrs` `<td>` (~L283–285):
   ```tsx
   <td style={{ textAlign: "right" }}>
     <ListTableTruncatedCell text={row.sweep_hrs ? String(row.sweep_hrs) : "—"} maxChars={truncateChars} />
   </td>
   ```
   (NULL and 0 both display `—`, matching the Freq cell and the "NULL/0 = off" meaning.)

6. Do **not** edit the `isSweep`, `sweepDisabled`, `runBlocked` lines (~L205–210) or `handleRun`. That is AC 13.

7. Form defaults: in **both** full form literals, the `useState({...})` initializer (~L336) and the `setForm({...})` in `openAdd` (~L651), add `sweep_hrs: ""` right after `freq_hrs: "0"`. The task-key `onChange` `setForm({...form, ...})` (~L964) spreads `form` and needs no change.

8. In `openEdit` (~L661), add after the `freq_hrs:` line:
   ```ts
   sweep_hrs: row.sweep_hrs != null ? String(row.sweep_hrs) : "",
   ```

9. In `handleSave`, add this property to **both** the PUT body (after `freq_hrs:` ~L688) and the POST body (after `freq_hrs:` ~L724):
   ```ts
   sweep_hrs: form.sweep_hrs !== "" ? parseFloat(form.sweep_hrs) : null,
   ```
   Blank clears the value to NULL server-side, which is how edit meets AC 11's "null clears it" case.

10. In the modal, insert this row **immediately after** the `Freq (hrs)` `modal-detail-row` (~L1008–1011):
    ```tsx
    <div className="modal-detail-row">
      <span className="modal-detail-label">Sweep (hrs)</span>
      <input type="number" min="0" step="0.25" placeholder="off" value={form.sweep_hrs} onChange={e => setForm({ ...form, sweep_hrs: e.target.value })}
        title="When AUTO is on and 0 < Avail < Min Count, run one batch (min 1) every N hours since Last Run. Blank or 0 = off." />
    </div>
    ```
    The same modal serves create and edit, so this one insertion covers both.

11. Verify, from `src/ui/frontend`: `npx eslint src/pages/AdminScheduledActions.tsx` shows no new errors, and `npm run build` succeeds. Run `grep -n "sweepDisabled" src/pages/AdminScheduledActions.tsx` and confirm the rule text is unchanged. Commit: `code(AST-1830): Scheduled Actions sweep_hrs modal input + list column`.

## AC trace (this ticket)

| AC | Where |
|----|-------|
| 11 — API round-trip, negative 400, column metadata | Stage 1 steps 1–7 |
| 12 — UI modal input (create + edit), sent on save, sortable list column with `—`, build passes | Stage 2 steps 1–5, 7–11 |
| 13 — Manual Sweep unchanged | Stage 2 step 6 (no edit) + step 11 grep; no dispatcher change in this ticket |

## Canon

- `patt.entity.batch-criteria` — `sweep_hrs` is claim-cadence criteria stored as `dispatch_task` row data and edited through the admin UI. This ticket adds the edit surface only; no caller literal. The one validation gate (negative → 400) is ticket-mandated; see the Stage 1 step 2 Decision.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1830
**Overall:** APPROVED
**Corpus:** a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6
**Publish ref:** `origin/sub/AST-1824/AST-1830-sweep-interval-admin-api-ui` @ `de6c5fdedac6ff3f00c792416695672f0531c788`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | B | | |

## Traceability

AC 11 (child) / parent AC 11 → S1 steps 1–7 · AC 12 (child) / parent AC 13 → S2 steps 1–5, 7–11 · AC 13 (child) / parent AC 14 → S2 step 6 + step 11 grep · Parent AC 1–10, 12, 15 → N/A (AST-1829 or out of slice)

## Findings

### discuss

- **Location:** Stage 1 step 2 (`_parse_sweep_hrs` Decision)
- **Finding:** `patt.entity.batch-criteria` Arc 1 says dispatch_task rows are not code-validated; this plan adds a narrow API gate (non-negative float, negative/non-numeric → 400). Parent AST-1824 technical scope and child AC 11 require that gate; the Decision documents ticket-over-Arc-1 for `sweep_hrs` only.
- **Recommendation:** No plan change required for approval; keep the Decision so Radia can see the intentional exception. Archie need not widen Canon Scope for a single AC-mandated field.

### acceptable

- **Location:** Explicit scope gate / Files Changed
- **Finding:** Two-file footprint matches ticket `## Scope`; AST-1829 frozen `sweep_hrs` key respected; no `database.py` / `dispatcher.py` edits; AUTO-on edit lock unchanged (S1 step 5).
- **Recommendation:** None.

- **Location:** Stage 2 / AST-1829 contract
- **Finding:** List rows already carry `sweep_hrs` via `SELECT *`; plan limits API work to column metadata + create/update — consistent with Frozen names.
- **Recommendation:** None.

- **Location:** Identity / status
- **Finding:** AST-1830 **Plan Ready**, assignee Joan; no `[plan-discuss]` rounds; depends-on AST-1829 noted on ftr (implementation ordering, not a plan defect).

context_tokens≈32000

## Review

- **Branch:** `origin/sub/AST-1824/AST-1830-sweep-interval-admin-api-ui`
- **Stage 1:** `0f3f2428` — `code(AST-1830): admin API sweep_hrs create/update/columns`
- **Stage 2:** `9d93d03d` — `code(AST-1830): Scheduled Actions sweep_hrs modal input + list column`
- **Build notes:** `py_compile` clean on `api_admin.py`; `_parse_sweep_hrs` smoke-checked in isolation (None/""/whitespace → NULL, 2.5/"4"/0 accepted, -1/"abc"/list → 400 message). `tsc -b --noEmit` clean, `npm run build` succeeds. `eslint` on the page reports only two pre-existing `no-extra-boolean-cast` errors (`!!row.empty_render` in the Run/toggle handlers) — present on the pre-change file, untouched per plan. `grep -n "sweepDisabled"` still shows `!!row.auto_mode && avail >= (row.min_count || 1)`. `tests/component/ui/api/test_api_admin.py` does not collect in this env (`ModuleNotFoundError: asyncpg`, same on the clean tree) — flag for Betty.

## Radia review

[code-rubric]
**Ticket:** AST-1830
**Publish ref:** `a41038c0a8bbd0d0813893d94d17766f104d52c0` (`origin/sub/AST-1824/AST-1830-sweep-interval-admin-api-ui`)
**Corpus:** a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | B | | |

## Column diff vs plan stage

(aligned) — Joan **APPROVED** with **B** on `patt.entity.batch-criteria` (narrow API validation vs Arc 1 “validated through execution”); tip implements the documented Stage 1 step 2 Decision and AC 11 gate.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Three-dot diff vs `origin/dev` includes sibling AST-1829 product work** (`src/data/database.py`, `src/core/dispatcher.py`) and AST-1829/merge-tests carry — expected while #1 is not on `dev`; **AST-1830’s own code commits** (`0f3f2428`, `9d93d03d`) touch only `src/ui/api/api_admin.py` and `AdminScheduledActions.tsx`, matching **## Scope**.
- **sibling test carry:** same sub tip bundles `TestAst1829*`, frontend candidate/session tests, `test_api_candidate.py`, etc. — Betty merge-tests; not AST-1830 product scope.
- **`_parse_sweep_hrs` and `NaN`:** `float("nan")` is non-negative in Python and would pass the helper; AC 11 does not require rejecting it. **Default (if ever tightened):** reject non-finite floats in `_parse_sweep_hrs` only — no UI change unless Susan wants client-side guards too.
- **Build notes (issue doc):** `test_api_admin.py` collection may fail locally without `asyncpg` — environment flag from implementer, not a canon finding.

## What's solid

- Frozen **`sweep_hrs`** key end-to-end: `_DISPATCH_TASK_COLUMNS`, shared `_parse_sweep_hrs`, create → `save_dispatch_task(sweep_hrs=...)`, update `allowed` + parse-before-loop branch, AUTO-on edit lock unchanged (`test_update_auto_row_edit_lock_unchanged`).
- UI: types, `DATA_COL_KEYS` / header / cell order after Freq, modal input (create + edit), PUT/POST bodies with blank → `null`; list shows value or `—` (0/NULL off).
- **AC 13:** `sweepDisabled` still `!!row.auto_mode && avail >= (row.min_count || 1)` (lines 209–213); no `handleRun` / dispatcher edits in this ticket.
- Tests on tip: `TestAst1830SweepHrsAdminApi` and `AST-1830 sweep_hrs modal input + list column` Vitest block cover AC 11–12 paths described in the plan.

## Recommended actions (downstream only)

- Chuckles: append artifact, `docs()` on sub, post slim upshot `--as radia`, **Review Posted**; **PROCEED** → UT when datt routes after sibling #1 is already UT-safe on ftr.
- No canon-scope or Archie escalation unless you want Arc 1 vs API-validation policy written into canon (Joan already marked optional at plan).

```
[code-rubric] PROCEED (Commit: a41038c0) admin sweep_hrs UI+API
```

context_tokens≈22000
