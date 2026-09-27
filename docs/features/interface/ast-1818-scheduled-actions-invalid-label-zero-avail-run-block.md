# AST-1818 — Scheduled Actions Invalid label, zero-avail Run block, Avail All default, Task-only freeze

- **Parent:** [AST-1817 — Invalid vs 0 Avail scheduled actions](https://linear.app/astral/issue/AST-1817)
- **Ticket:** [AST-1818](https://linear.app/astral/issue/AST-1818)
- **Publish ref:** `sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block` (origin only)

Scheduled Actions paints an invalid dispatch task (`empty_render`) with the same faded, unlabeled Run button as any other blocked row, hides zero-avail tasks by default, and freezes Task + Entity + State. This ticket changes four things, all in `AdminScheduledActions.tsx`: invalid rows get a full-opacity `btn secondary in-row` button labelled **Invalid**; valid rows with `available_count` 0 get the existing muted/disabled Run treatment; the Avail filter starts at All; only the Task column is frozen. No API, config, shared layout helper, or CSS change.

## Canon

Canon Scope: **none** (ticket Citations + parent Architectural definition). `.btn.primary` / `.btn.secondary` / `.btn.in-row` in `App.css` are reused as existing code; `pattern.ui.shared-button-roles` is draft, not law.

## Scope gate

Every product row in Files Changed is `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, which this ticket's `## Scope` names as **modified**. Each stage below is one of the three change kinds its Technical scope describes (frozen-column constant; Avail filter initial state; Run button blocked/label logic in `ScheduledPhaseTable`). No gap.

## Verified codebase facts (origin/dev @ `cd7ca619`)

- `FROZEN_DATA_COLUMNS = 3` at line 105; passed as the override to `resolveFrozenDataColumns(uiConfig, FROZEN_DATA_COLUMNS)` at line 341. In `listTableLayout.ts` a numeric override `>= 0` wins over `ui.list_table_frozen_data_columns`, so changing the page constant leaves every other list page alone.
- Header and body cells for columns 0/1/2 already gate `list-table-cell-frozen` on `idx < frozenN`, and `scheduledFrozenStyle(idx)` gets `left` from `stickyLeftPx(..., frozenN)`. Setting `frozenN = 1` removes the class and the sticky `left` from Entity and State with no markup edit.
- `useState("gt0")` at line 361 is the **only** place `availGtZeroFilter` gets a non-user value (other hits: predicate at 476, deps at 496, `<select>` at 820). The `> 0` option and `always_visible_under_avail_gt0` predicate stay as they are.
- `GET /api/admin/dispatch_tasks` always sends `available_count` as an int (it falls back to `0` on a missing candidate/entity/state or a count exception). `always_visible_under_avail_gt0_dispatch_task_keys` is `()` in `config.py` (carve-out retired AST-1134), so no task is meant to run while its avail is 0.
- The Run button is at lines 244–251. Today: `runBlocked = isRunning || sweepDisabled || emptyRender`; class `btn primary in-row`; opacity `isRunning ? 0 : (runBlocked ? 0.25 : 1)`; label `isSweep ? "Sweep" : "Run"`.
- `App.css` `.btn:disabled` only sets `cursor: not-allowed` (no opacity), so a disabled `btn secondary in-row` button stays at full opacity with no CSS change.
- `handleRun` (line 582) already returns early on `empty_render`. React does not call `onClick` on a `disabled` `<button>`, and that holds for `fireEvent.click` too.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `FROZEN_DATA_COLUMNS` 3→1; Avail initial state `"gt0"`→`""`; Run button zero-avail block + Invalid label/class/opacity | ui (frontend) | Hedy (`build-child`) |
| `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | Update frozen / Avail-default / AST-1782 empty_render assertions; add zero-avail Run-disabled case and Invalid-button case | tests | Betty (`qa-child`) — **engineer does not edit** |
| `tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx` | Landing Avail value `gt0` → `""` | tests | Betty (`qa-child`) — **engineer does not edit** |
| `docs/test-bible/frontend/pages.md` | Scheduled Actions entries: Avail default, frozen columns, Invalid / zero-avail Run | bible | Betty (`qa-child`) — **engineer does not edit** |

The pre-commit hook blocks engineer commits to `tests/` and `docs/test-bible/**`. Those rows are listed so Betty's manifest and this plan line up.

## Stage 1: Task-only freeze and Avail defaults to All

**Done when:** On first load of Scheduled Actions the Avail `<select>` shows All (`""`) and zero-avail rows are visible, and in an expanded section only the Task header and cells carry `list-table-cell-frozen` / a sticky `left`.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, change line 105 from `const FROZEN_DATA_COLUMNS = 3` to `const FROZEN_DATA_COLUMNS = 1`. Add this trailing comment on that line: `// AST-1818: only Task pinned; Entity/State scroll with the rest`. Do not edit the `idx < frozenN` class gates or `scheduledFrozenStyle`.
2. In the same file, change line 361 from `useState("gt0") // "" | "gt0"` to `useState("") // "" (All, AST-1818 default) | "gt0"`. Do not touch the predicate at line 476, the dependency list at line 496, or the `<option value="gt0">` at line 822.
3. In `src/ui/frontend`, run `npm run build` and `npm run lint`. Both must pass before committing.
4. Commit only `AdminScheduledActions.tsx`: `code(AST-1818): stage 1 — Task-only freeze, Avail default All`. Publish per `build-child`.

⚠️ **Decision:** Change the page override and leave `list_table_frozen_data_columns` alone. Technical scope requires this, and it keeps other list pages on their own setting.

## Stage 2: Run button — zero-avail block and Invalid label

**Done when:** An `empty_render` row shows a full-opacity, disabled `btn secondary in-row` button named **Invalid**. A valid row with `available_count` 0 shows a disabled **Run** at opacity 0.25 with `pointer-events: none`. Valid rows with avail > 0 and running rows' Stop/Draining behave as before. Clicking either disabled button sends no `/run` POST.

1. In `ScheduledPhaseTable`'s `rows.map` body, replace these two lines (206–207):

   ```tsx
   const emptyRender = !!row.empty_render
   const runBlocked = isRunning || sweepDisabled || emptyRender
   ```

   with:

   ```tsx
   const emptyRender = !!row.empty_render
   // AST-1818: a valid task with nothing to claim gets the same muted, unclickable Run treatment.
   const zeroAvail = !emptyRender && avail === 0
   const runBlocked = isRunning || sweepDisabled || emptyRender || zeroAvail
   ```

   `avail` is the existing `row.available_count ?? 0` from line 203. Do not redeclare it.

2. Replace the Run `<button>` (lines 244–251, the one before the `{isRunning && (` Stop overlay) with:

   ```tsx
   <button
     // AST-1818: Invalid reuses the shared secondary role (no new class / colour literal).
     className={emptyRender ? "btn secondary in-row" : "btn primary in-row"}
     // Invalid stays full opacity so the secondary styling is readable; other blocked rows fade to 0.25.
     // isRunning still hides it (0) so the Stop/Draining overlay shows through.
     style={{ whiteSpace: "nowrap", opacity: isRunning ? 0 : (runBlocked && !emptyRender ? 0.25 : 1), pointerEvents: runBlocked ? "none" : "auto" }}
     disabled={runBlocked}
     onClick={e => handleRun(e, row)}
   >
     {emptyRender ? "Invalid" : (isSweep ? "Sweep" : "Run")}
   </button>
   ```

   Leave the `{isRunning && ( <button className="btn danger in-row" …> )}` Stop/Draining overlay exactly as it is. Leave the AUTO badge (lines 228–240) exactly as it is.

3. In `src/ui/frontend`, run `npm run build` and `npm run lint`. Both must pass.
4. Run the related suite and record the result in the stage Linear comment. Do not edit tests to make it green: `cd src/ui/frontend && npx vitest run --config vite.config.ts test_AdminScheduledActions` (substring filter matching every `test_AdminScheduledActions*.test.tsx`). Failures are expected in the AST-647/746/760 frozen cases, the AST-887/894/1104 Avail-default cases, and the AST-1782 empty_render "Run" name cases, because the behaviour they assert is changing. Betty owns those updates in `qa-child`. Any **other** failure is a blocker: stop and comment per the execution contract.
5. Check AC 9 and AC 10 by hand before committing:
   - `git diff origin/dev -- src/ui/frontend/src/App.css src/ui/frontend/src/lib/listTableLayout.ts src/ui/api src/utils/config.py` must be empty.
   - `git diff origin/dev -- src/ui/frontend/src/pages/AdminScheduledActions.tsx | rg -n '^\+.*(#[0-9a-fA-F]{3,6}|rgb\()'` must print nothing.
6. Commit only `AdminScheduledActions.tsx`: `code(AST-1818): stage 2 — Invalid label, zero-avail Run block`. Publish per `build-child`.

⚠️ **Decision:** `zeroAvail` uses `avail === 0` on the existing `?? 0` value. The API always sends an int, so `null` can't come from the server. Local `?? 0` treats a missing value as zero and blocks the row, which is the conservative reading of AC 3. When the server's count query throws, it reports 0, so the row is blocked. That matches "nothing to run" as the server sees it.

⚠️ **Decision:** Invalid overrides every other label (AC 1: "Invalid wins over Run/Sweep"). `empty_render` rows get AUTO forced off server-side, so `isSweep` would be false anyway. The explicit `emptyRender ?` branch keeps the label rule clear no matter what the server does.

⚠️ **Decision:** No zero-avail guard in `handleRun`. Technical scope limits this to the button's blocked/label logic in `ScheduledPhaseTable`. React doesn't run `onClick` on a disabled `<button>`, and that includes `fireEvent.click`, so AC 3's "no `/run` POST" is covered by `disabled={runBlocked}`. The existing `empty_render` early return in `handleRun` stays.

⚠️ **Decision:** Considered and rejected: (a) a separate `<button>` element for Invalid rows, which duplicates the wrapper/overlay markup; (b) a `runState` enum, which adds more code than the four branches need. An in-place conditional is the smallest diff that meets every AC.

## Acceptance criteria → stage

| AC | Stage |
|----|-------|
| 1, 2 (Invalid name/class/disabled/no POST; no 0.25 opacity) | 2 |
| 3 (zero-avail Run disabled, 0.25, pointer-events none, no POST) | 2 |
| 4 (avail > 0, AUTO off → Run enabled, POSTs) | 2 (unchanged path; verified by suite) |
| 5 (running, avail 0 → Stop POSTs) | 2 (overlay untouched) |
| 6, 7 (Avail default All; `> 0` still filters) | 1 |
| 8 (only Task frozen) | 1 |
| 9, 10 (no shared/API/config diff; no colour literals) | 2 step 5 |
| 11 (build, lint, suite green) | build/lint each stage; suite green after Betty's `qa-child` updates → `test-child` |

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1818
**Overall:** APPROVED
**Corpus:** a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6
**Publish ref:** `sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block` @ `efe85d0a`

## Canon scores

Frozen directive list is **empty** (child **Citations:** none; parent **Architectural definition** records no applicable statutes/patterns in the active catalog). No ids to score — not a missing Canon Scope: the parent already locked that decision at definition time, and Radia’s column will use the same empty list.

## Traceability

AC 1–5, 9–10 → Stage 2; AC 6–8 → Stage 1; AC 11 → per-stage build/lint, Betty `qa-child` test/bible updates, then `test-child` green suite (per plan AC table and Stages 1–2).

### Findings

**acceptable** — `## Scope gate` + Files Changed align with the child `## Scope` and parent Component/Technical scope; engineer product touch is only `AdminScheduledActions.tsx`; test/bible rows correctly attributed to Betty.

**acceptable** — Verified codebase facts match `origin/dev` in the epic worktree (`FROZEN_DATA_COLUMNS = 3`, `useState("gt0")`, Run button at 244–251, `handleRun` `empty_render` guard). Stage 2 JSX matches AC 1–3 opacity/label/class split (`emptyRender` → secondary **Invalid** full opacity; `zeroAvail` → existing muted Run).

**acceptable** — No `## Self-assessment` / conf block; Estimate confirm only. Low risk for this footprint; not `!!-NONE`.

**discuss** — Optional: a one-line self-assessment (`minor` conf) would match larger interface plans; not required for approval.

### R6 (summary)

- Definition fidelity: all four parent functional capabilities and all 11 child ACs are staged; no scope creep into API/config/`listTableLayout.ts`/`App.css`.
- DRY / scope: single-file conditional change; rejected alternatives documented; Betty owns assertion churn explicitly.
- Plan Discuss: status **Plan Ready**, assignee Joan; no `[plan-discuss]` rounds in thread.

context_tokens≈18500

[plan-rubric] PROCEED (Commit: efe85d0a) Plan faithful, empty canon OK
