# AST-443 — Quickie: Scheduled Actions Avail Refresh After Manual Run

**Linear:** https://linear.app/astralcareermatch/issue/AST-443/quickie-bugs-scheduled-actions-avail-refresh-after-manual-run  
**Feature ref:** `sub/AST-436/AST-443-quickie-bugs-scheduled-actions-avail-refresh-after-manual-run` (origin only)

After Susan clicks **Run** on a Task Dispatcher row and the manual batch **finishes**, refresh that row’s **Avail** (`available_count`) without a full page reload. In-progress runs may keep the prior count until completion.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Detect thread `running` → idle per row; call `loadData()` on transition | ui |

---

## Stage 1: Refresh dispatch tasks when a manual run completes

**Done when:** Completing a manual **Run** updates **Avail** on that row without browser reload; no backend changes.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add `const prevRunningRef = useRef<Record<number, boolean>>({})` next to existing `pollRef`.

2. Add `useEffect` that depends on `[threadStatus, data, loadData]`:
   - For each `row` in `data` (current filtered list is fine — use `data` so all configured tasks are tracked):
     - `const running = threadStatus[row.id]?.running ?? false`
     - `const wasRunning = prevRunningRef.current[row.id] ?? false`
     - If `wasRunning && !running`, call `loadData()` (no spinner: default `showSpinner` is false).
     - Set `prevRunningRef.current[row.id] = running`
   - Do **not** call `loadData()` on initial mount when `wasRunning` is false (only on true → false transition).

3. Leave `handleRun` as-is (`setTimeout(loadThreadStatus, 500)` only). The new effect handles Avail refresh when the scheduler thread stops.

⚠️ **Decision:** Refresh on **any** row’s running→idle transition (manual or auto), not only manual runs — same `loadData()` cost, keeps Avail accurate for auto batches too; matches “when the run ends” in the ticket.

---

## Stage 2: Verify

**Done when:** TypeScript clean; manual or observed Avail update after run completes.

1. `cd src/ui/frontend && npx tsc -b --noEmit`
2. Manual: Scheduled Actions → pick a row with Avail > 0 → **Run** → when Stop/draining finishes and Run button returns, **Avail** updates without F5 (use a task that changes eligible count if possible).

---

## Self-Assessment

**Scope:** `scope-minor` — One `useEffect` in a single admin page.

**Conf:** `conf-high` — Ticket notes describe this pattern explicitly; `loadData` already reloads `/api/admin/dispatch_tasks`.

**Risk:** `risk-low` — Extra list fetch at most once per completed run; no dispatch semantics changed.

---

## Resolution (resolve-astral 2026-05-22)

- **fix-now:** none.
- **discuss:** none (Chuckles note on brief loading during `loadData` refresh — optional polish, not implemented).
- Radia review 2026-05-22: approve. No product changes on resolve pass.
