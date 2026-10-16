<!-- linear-archive: AST-1818 archived 2026-10-07 -->

## Linear archive (AST-1818)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1818/scheduled-actions-invalid-label-zero-avail-run-block-avail-all-default  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1817 — Invalid vs 0 Avail scheduled actions.  
**Blocked by / blocks / related:** parent: AST-1817

### Description

## What this implements

Ships all four Functional scope capabilities on the Scheduled Actions page: Invalid-labelled secondary-styled disabled button for `empty_render` rows, disabled/faded Run for valid zero-avail rows, Avail filter defaulting to All, and only the Task column frozen. Does not touch the API, config, shared list-table layout helpers, or `App.css`.

## Citations

none — no active pattern or statute governs a frontend-only presentation change over already-resolved API fields (see Architectural definition).

## Scope

`src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified**; `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **modified**; `tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx` — **modified**; `docs/test-bible/frontend/pages.md` — **modified**. Technical scope, verbatim: the page-level frozen-data-column constant passed to `resolveFrozenDataColumns` changes from 3 to 1 so only the Task column receives `list-table-cell-frozen` and a sticky `left`; no change to `listTableLayout.ts` or the shared `list_table_frozen_data_columns` UI config (other list pages keep their own setting). The initial value of the Avail filter state changes from `"gt0"` to `""` (All); the filter predicate, the `> 0` option, and the `always_visible_under_avail_gt0` escape hatch stay as they are. Row Run button in `ScheduledPhaseTable`: modified blocked/label logic — (a) when `empty_render` is true the button renders with the existing shared `btn secondary in-row` classes instead of `btn primary in-row`, label **Invalid**, `disabled`, `pointer-events: none`, full opacity; Invalid wins over Run/Sweep labelling. (b) When `empty_render` is false and `available_count` is 0, the row is added to the existing run-blocked condition, so it gets the same `disabled` + 0.25 opacity + `pointer-events: none` treatment invalid rows get today. The running-row Stop/Draining overlay is unchanged. No new CSS class, no inline color literals, no `App.css` edit. Tests / bible (Betty, `qa-child`): update the assertions listed in Component scope; add a case proving a valid row with `available_count: 0` has a disabled Run button that fires no `/run` POST, and a case proving an `empty_render` row's button has accessible name Invalid and classes `btn secondary in-row`.

## Acceptance criteria

 1. With a row whose `empty_render` is true, the Run cell's button has accessible name **Invalid**, has classes `btn secondary in-row` (not `primary`), is `disabled`, and clicking it (including `fireEvent.click` bypassing pointer-events) sends no `POST …/run` — failing result: button text is Run/Sweep, carries `primary`, is enabled, or a `/run` POST is observed.
 2. That Invalid button's inline style does not set `opacity: 0.25` — failing result: `toHaveStyle({ opacity: "0.25" })` passes on the Invalid button.
 3. With a row whose `empty_render` is false and `available_count` is 0 (not running), the button is named **Run**, is `disabled`, has `opacity: 0.25` and `pointer-events: none`, and a click sends no `POST …/run` — failing result: button enabled, full opacity, or a `/run` POST fires.
 4. With a row whose `empty_render` is false and `available_count` > 0 and AUTO off, Run is enabled and a click POSTs `/run` (existing behaviour preserved) — failing result: button disabled or no POST.
 5. A running row with `available_count` 0 still renders the Stop button and a click POSTs `…/stop` — failing result: Stop missing or disabled while `draining` is false.
 6. On first render the Avail filter `<select>` has value `""` (All) and rows with `available_count` 0 are visible without touching any filter — failing result: value is `gt0` or a zero-avail row is absent until the filter is changed.
 7. Selecting Avail `> 0` still hides zero-avail rows (AST-887 predicate unchanged) — failing result: zero-avail rows remain visible under `> 0`.
 8. In an expanded section table, `columnheader[0]` (Task) and its body cell have class `list-table-cell-frozen`; `columnheader[1]` (Entity) and `columnheader[2]` (State) and their cells do **not**, and have no inline `left` — failing result: Entity or State carries the frozen class or a sticky `left`.
 9. `git diff origin/dev -- src/ui/frontend/src/App.css src/ui/frontend/src/lib/listTableLayout.ts src/ui/api src/utils/config.py` is empty — failing result: any diff in those paths (the change must reuse existing classes and must not alter shared list-table config or the API).
10. `grep -nE "#[0-9a-fA-F]{3,6}|rgb\(" src/ui/frontend/src/pages/AdminScheduledActions.tsx` reports no new matches versus `origin/dev` — failing result: an inline color literal added for the Invalid button instead of the shared `btn secondary` class.
11. `npm run build` and `npm run lint` in `src/ui/frontend` pass, and the full `test_AdminScheduledActions*.test.tsx` suite is green — failing result: any build/lint error or red test.

## Boundaries

Sole child of AST-1817 — no siblings. Does not touch `src/ui/api/`, `src/utils/config.py`, `src/ui/frontend/src/lib/listTableLayout.ts`, or `src/ui/frontend/src/App.css`; the server-side `/run` empty_render 400 gate stays as-is.

## Notes for planning

No active pattern or statute applies (parent Architectural definition). Reuse existing `btn secondary in-row` classes for Invalid — the shared button role directive is draft-only, reference not law. `empty_render` and `available_count` are already on every `GET /api/admin/dispatch_tasks` row.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1817-invalid-vs-0-avail-scheduled-actions`, child `sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block`. Created at dispatch-parent.

## QA test manifest

Publish tip: `origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block` @ `81ac239f` (`merge-tests(AST-1818): origin/tests 42030efb`). Bible block: `docs/test-bible/frontend/pages.md` § **AST-1818 · AST-1817**.

1. **Full Scheduled Actions routed-page suite (§6c; AC 1–8, 11)** — both `tests/component/frontend/pages/test_AdminScheduledActions*.test.tsx` files, 71 cases, all green on Betty's sync of this tip.
   * Revised: AST-647 (renamed `…freezes only the Task column`), AST-746, AST-760 (AC 8); AST-887 ×4, AST-894 ×2 (describe renamed `AST-894 expand-all on landing (Avail default All per AST-1818)`), AST-1104 landing (AC 6–7); AST-1782 `blocks AUTO toggle and shows disabled Invalid button when empty_render is true` (AC 1–2).
   * New: `AST-1818 zero-avail Run block` — zero-avail Run muted/disabled/no POST (AC 3); running zero-avail row Stop POSTs (AC 5). AC 4 = existing AST-1782 `allows…`.
   * Pre-existing drift fixed: AST-751 + AST-768 default-sort cases read Candidate at `cells[11]` (Mode column shifted it) → `cells[length - 3]`.
2. **AC 9 / AC 10 gates** — both commands print nothing.
3. **Build + lint (AC 11)** — `npm run build` green; `npm run lint` no new problems vs `origin/dev` (engineer baseline 33).

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts test_AdminScheduledActions
git diff origin/dev -- src/ui/frontend/src/App.css src/ui/frontend/src/lib/listTableLayout.ts src/ui/api src/utils/config.py
git diff origin/dev -- src/ui/frontend/src/pages/AdminScheduledActions.tsx | rg -n '^\+.*(#[0-9a-fA-F]{3,6}|rgb\()'
cd src/ui/frontend && npm run build && npm run lint
```

**Integration:** none — no existing scenario exercises Scheduled Actions frontend.

**Bible shasums (publish tip):**

* `docs/test-bible/frontend/pages.md` — `ceb6dc761378cd5617305da4d4349d0fd26fabb3`
* `docs/test-bible/frontend/components.md` — `bf377b57a468daf7f67a8240cc90f30961fcadd2`

### Comments

#### betty — 2026-09-27T04:28:06.091Z
[check-linear] Leaked AST-1768 bug-repro (7954d0fa) reverted on `origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block` @ `4a9d769f` — 8 paths restored to origin/dev; 6 frontend files green (110 tests).

#### radia — 2026-09-27T04:22:45.432Z
[code-rubric] PROCEED (Commit: cedb7ac7) Plan-faithful, empty canon OK

#### betty — 2026-09-27T04:19:53.192Z
`origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block` @ `81ac239f` · suite revised, 71 green

#### hedy — 2026-09-27T04:09:20.041Z
`origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block` @ `05e084dd`

#### joan — 2026-09-27T04:01:00.973Z
[plan-rubric] PROCEED (Commit: efe85d0a) Plan faithful, empty canon OK

#### hedy — 2026-09-27T03:59:13.516Z
`origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block` @ `efe85d0a` · plan ready, two stages

---

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

## Review

- **Branch:** `origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block`
- **Stage 1:** `2c1f8416` — Task-only freeze, Avail default All
- **Stage 2:** `0a723a3a` — Invalid label, zero-avail Run block
- **Build:** `npm run build` green. AC 9 diff empty; AC 10 grep empty.
- **Lint (AC 11):** `npm run lint` reports 33 problems both before and after this change (same count on `origin/dev`). None are new. Two are in this file: `no-extra-boolean-cast` on the pre-existing `if (!!row.empty_render) return` guards in `toggleAutoMode` / `handleRun`. Those guards are outside plan scope and were left alone.
- **Suite (for Betty, `qa-child`):** `test_AdminScheduledActions*.test.tsx` → 13 failed / 56 passed.
  - **11 expected** (behaviour changed by this ticket): AST-647, AST-746, AST-760 (frozen columns); AST-887 ×4 and AST-894 ×2 (Avail default was `gt0`); AST-1104 landing (Avail default); AST-1782 `blocks AUTO toggle and Run when empty_render is true` (button is now named Invalid).
  - **2 pre-existing, also red on unmodified `origin/dev`:** AST-751 `All-candidate default sort orders same task by available count descending` and AST-768 `with Candidate All, group filter narrows sections and default sort by avail desc`. Both read `cells[11]` (Runs, `∞`) where they expect the Candidate column.
- **Missing cases (AC 1–3):** Invalid button name/classes/full opacity; valid zero-avail row Run disabled at 0.25 with no `/run` POST.

## Radia review

[code-rubric]

**Ticket:** AST-1818  
**Publish ref:** `cedb7ac7814b728e87a91cb65237813d893e5b2d` (`origin/sub/AST-1817/AST-1818-scheduled-actions-invalid-label-zero-avail-run-block`)  
**Corpus:** `a0bc2f0e5b5810448cf465ebeff84ffb6f1d60b6`  
**Overall:** CLEAN  

## Canon scores

*(Frozen list empty — Linear **Citations:** none; parent Architectural definition records no applicable statutes/patterns. Nothing to score.)*

## Column diff vs plan stage

(aligned) — Joan’s plan-stage column also used an empty frozen list; no per-id grades to compare.

## Frame diff

(none) — Product and Betty’s test/bible updates cover AC 1–11; no Description checklist rows need adding for `resolve-child` beyond what the engineer will tick at UT.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sibling test carry:** `origin/dev...origin/sub/...` also includes merge-tests baggage from `origin/tests` (not AST-1818 product scope): `docs/test-bible/frontend/lib.md`, `docs/test-bible/ui/api/api_candidate.md`, `tests/component/frontend/contexts/test_CandidateContext.test.tsx`, `tests/component/frontend/lib/test_sessionAuthMark.test.ts`, `tests/component/frontend/pages/test_Authenticate.test.tsx`, `tests/component/frontend/pages/test_JobsJobDetail.test.tsx`, `tests/component/frontend/stytchMock.tsx`, `tests/component/ui/api/test_api_candidate.py`. Score only `AdminScheduledActions.tsx` + this ticket’s Scheduled Actions test/bible rows; do not treat those paths as cross-ticket product scope.
- **Plan fidelity:** Three-dot diff matches Stages 1–2 verbatim (`FROZEN_DATA_COLUMNS` 1 + comment, `useState("")` for Avail, `zeroAvail` / Invalid secondary label / opacity split). AC 9 verified empty on shared paths; AC 10 no new colour literals on added lines. **Tests Passed** + manifest on tip implies AC 11 (71-case suite, build, lint baseline 33) — Radia did not re-run Vitest in Ask mode.
- **Estimate footprint:** Confirm **2** still fits (single product file + expected assertion churn + two new zero-avail/Invalid cases + AST-751/768 column-index drift fix).
- **Lint:** Two pre-existing `no-extra-boolean-cast` hits on `!!row.empty_render` in `toggleAutoMode` / `handleRun` remain out of plan scope (engineer note in issue doc stands).

## What’s solid

- Invalid vs zero-avail split matches plan decisions: `emptyRender ? "Invalid"` + `btn secondary in-row` at full opacity; `zeroAvail` reuses muted primary Run at 0.25 with `pointer-events: none`; Stop overlay untouched (AC 5 covered in new describe block).
- Betty’s revisions align with AC 6–8 (Avail default, frozen Task-only, AST-1782 Invalid assertions) and document superseded AST-894/887/1104 defaults in `pages.md`.

## Recommended actions (downstream — not executed by Radia)

(none) — Chuckles: append this artifact, `docs(AST-1818): Radia review — clean`, post slim upshot `--as radia`, move **Review Posted**; datt **§3h** **PROCEED** → **User Testing** (no `resolve-child` unless Susan wants the optional Joan self-assessment discuss, which was plan-only).

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] PROCEED (Commit: cedb7ac7) Plan-faithful, empty canon OK
```

context_tokens≈28000

## Bug: AST-1819 — Invalid button needs a tooltip listing the missing prompt tokens

Publish ref: `sub/AST-1817/AST-1819-invalid-button-missing-token-tooltip`. Scope: the parent AST-1817 Component/Technical scope as amended for AST-1819 (`api_admin.py` `list_dtasks` row field + Invalid tooltip; parent ACs 9, 12, 13). Canon Scope: none, same as AST-1818.

### As-is
On Scheduled Actions, an `empty_render` row shows the disabled **Invalid** button (AST-1818 Stage 2) with no tooltip. `GET /api/admin/dispatch_tasks` rows carry only the `empty_render` boolean, so the UI has no way to say which tokens failed.

### To-be
Hovering the Invalid control shows the row's missing prompt tokens comma-separated (e.g. `FIRST_NAME, GET_RUBRIC`). When the list is empty (prompts could not be validated), it reads `Could not validate prompts`. The button stays `disabled` and unclickable.

### Repro
Fixture row from `GET /api/admin/dispatch_tasks` (frontend mock), not running, AUTO off:

```json
{ "id": 1, "task_key": "scan_jobs", "entity_type": "job", "trigger_state": "NEW",
  "auto_mode": 0, "available_count": 3, "empty_render": true, "candidate_id": "c1" }
```

Expand its section and hover the **Invalid** button: no tooltip. API side: with `_evaluate_dispatch_empty_render` monkeypatched to return `{"empty_render": True, "empty_tokens": ["FIRST_NAME"]}`, the `list_dtasks` output row has no `empty_tokens` key.

### Root cause
1. `src/ui/api/api_admin.py` `list_dtasks` (lines 966–968) calls `_evaluate_dispatch_empty_render`, which returns `{"empty_render": bool, "empty_tokens": list[str]}`. The loop stamps only `row["empty_render"]`; `empty_tokens` feeds the AUTO-forced-off log line (line 972) and is then dropped.
2. `AdminScheduledActions.tsx` never sets a tooltip on the Invalid control. The button itself can't host a hover tooltip because it has `pointer-events: none` (AST-1818), which suppresses hover on the button.

### Proposed change

**A. API — `src/ui/api/api_admin.py`, `list_dtasks` only.** Directly after line 968 (`row["empty_render"] = bool(er.get("empty_render"))`), add:

```python
        # AST-1819: missing prompt tokens for the Invalid tooltip ([] when valid or unvalidatable).
        row["empty_tokens"] = list(er.get("empty_tokens") or [])
```

Do not change `_evaluate_dispatch_empty_render`, the AUTO force-off `if` block, its `tokens`/`why` locals, or the `logger.warning` line. There is no new evaluation, since `er` is already computed per row. Every return path of `_evaluate_dispatch_empty_render` yields a list (early returns `[]`; `empty_render_for_prompts` returns a deduped `list[str]`), and `list(... or [])` guarantees the list type for AC 12.

**B. Frontend — `src/ui/frontend/src/pages/AdminScheduledActions.tsx`.**

1. In the `DispatchTask` interface, directly after `empty_render?: boolean` (line 92), add `empty_tokens?: string[]`.
2. In `ScheduledPhaseTable`'s `rows.map` body, directly after `const runBlocked = …` (line 209), add:

   ```tsx
   // AST-1819: Invalid tooltip — missing tokens, or a fallback when prompts could not be validated.
   const invalidTitle = emptyRender && !isRunning
     ? (row.empty_tokens?.length ? row.empty_tokens.join(", ") : "Could not validate prompts")
     : undefined
   ```

3. On the Run cell wrapper at line 245, change `<div style={{ position: "relative", display: "inline-block" }}>` to:

   ```tsx
   <div title={invalidTitle} style={{ position: "relative", display: "inline-block" }}>
   ```

   Leave the Invalid/Run `<button>` itself unchanged (class, style, `disabled`, `pointer-events: none`, label). Because the button has `pointer-events: none`, hover lands on the wrapper and the browser shows the wrapper's native `title`. Adding `title` to the button instead would never show, and loosening its pointer-events would make it hoverable/clickable again, so both are rejected.

⚠️ **Decision:** Use a native `title` on the existing wrapper `<div>`. The amended Technical scope names this option, it needs no new component, CSS class, or `App.css` edit, and it's the smallest diff. Rejected alternatives: a custom tooltip component (new UI surface, out of scope); toggling pointer-events (reopens clicks, breaks AST-1818 AC 1).

⚠️ **Decision:** No tooltip while the row is running (`!isRunning`). In that state the Invalid button is at opacity 0 under the Stop/Draining overlay, so a token tooltip over Stop would describe a control the user can't see. `title` is `undefined` for every non-Invalid row, so the wrapper renders no `title` attribute there.

⚠️ **Decision:** Join with `", "` (comma + space). This matches Susan's example `FIRST_NAME, GET_RUBRIC` and parent AC 13's literal text. Tokens render in API order (first-seen order across prompt texts), with no client-side sort.

**Compile / lint / checks (make-fix):** `python3 -m py_compile src/ui/api/api_admin.py`; in `src/ui/frontend`, `npm run build` and `npm run lint`. Lint must stay at the 33-problem baseline, with nothing new.
- **Parent AC 9:** `git diff origin/dev -- src/ui/frontend/src/App.css src/ui/frontend/src/lib/listTableLayout.ts src/utils/config.py` is empty, and `git diff origin/dev -- src/ui/api` shows only the two added `list_dtasks` lines.
- **Colour literals:** the AST-1818 AC 10 grep on `AdminScheduledActions.tsx` stays empty.

Commits: `code(AST-1819): list_dtasks empty_tokens row field` (A), then `code(AST-1819): Invalid tooltip lists missing tokens` (B), each built/linted before commit.

### Blast radius
- **`list_dtasks` consumers:** only `AdminScheduledActions.tsx` reads `empty_render`, and no other frontend file references either field. The extra key is additive JSON; no test asserts an exact row key set (`test_api_admin.py` AST-1780 cases check `out[0]["empty_render"]` and monkeypatch `_evaluate_dispatch_empty_render`, which already returns `empty_tokens`).
- **Untouched:** `_candidate_dispatch_empty_render_error` (create/PUT/run 400 gates) and the `/run` server gate.
- **Tests (Betty, `qa-fix`/`qa-child`):**
  - `test_api_admin.py` list-enrich cases gain an `empty_tokens` assertion (parent AC 12).
  - `test_AdminScheduledActions.test.tsx` gains tooltip cases (AC 13), e.g. `getByTitle("FIRST_NAME, GET_RUBRIC")` and `getByTitle("Could not validate prompts")`.
  - The AST-1782/1818 Invalid-button assertions (accessible name **Invalid**, `btn secondary in-row`, `disabled`, no `/run` POST) are unaffected: `title` is on the wrapper, so the button's accessible name stays "Invalid".
  - Bible: `docs/test-bible/ui/api/api_admin.md` and `frontend/pages.md`.

### What must still hold
- **AST-1818 AC 1–2:** the Invalid button keeps accessible name **Invalid**, classes `btn secondary in-row`, `disabled`, `pointer-events: none`, and full opacity (no 0.25), and a click (including `fireEvent.click`) sends no `/run` POST.
- **AST-1818 AC 3–5:** zero-avail Run stays muted/disabled, avail > 0 Run still POSTs, and a running row's Stop still POSTs.
- **AST-1818 AC 6–8:** Avail default All, `> 0` still filters, only Task is frozen.
- **AUTO force-off:** the `list_dtasks` force-off for `empty_render` rows and its warning log text are unchanged.
- **No other changes:** no new CSS class, no inline colour literal, no `App.css` / `listTableLayout.ts` / `config.py` diff.


## Joan fix-board (AST-1819)

[board-joan]  CANON: OK

AST-1819 board-joan done — CANON: OK.

**Read:** `plan-fix` § Bug: AST-1819 on `origin/sub/AST-1817/AST-1819-invalid-button-missing-token-tooltip` (`As-is` / `To-be` / `Repro` / `Root cause` / `Proposed change` A–B / `Blast radius` / `What must still hold`). Roster skim: `stat.logging.info.api` (no new route completion info on this GET enrich), `stat.dispatch.entity-state-bound` (paths include `api_admin.py` but law is entity_type/trigger_state binding — unchanged), dispatch/batch patterns (claim/count shape untouched). Canon Scope on the patch: **none** (same as AST-1818).

**Why OK:** Proposed change surfaces data `_evaluate_dispatch_empty_render` already computes; it does not contradict any in-force statute or pattern, and it does not need a roster carve-out or new directive. Wrapper `title` is presentation-only; draft `pattern.ui.shared-button-roles` is not law. `What must still hold` preserves AST-1818 button contract without loosening `pointer-events` on the button itself.


## Radia review (AST-1819)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Scope note:** Parent AST-1817 AC 9 originally forbade `src/ui/api` changes; Susan’s confirmed bug intake widens scope to the single `list_dtasks` row field — plan-fix documents this; diff matches **Proposed change A**, not scope creep vs sibling AST-1818.
- **Plan doc location:** `plan-fix` patch lives under `docs/features/interface/ast-1818-scheduled-actions-invalid-label-zero-avail-run-block.md` § **Bug: AST-1819** (expected fix-lane pattern on shared parent/child doc).
- **Board context:** Betty **TESTS: REVISE** at F2; qa-fix `[bug-repro]` @ `57c3f343`; make-fix/test-fix landed on tip `4ef31239`. **Tests Passed** implies manifest green; Radia did not re-run suites in Ask mode.
- **Estimate:** Linear **2** still fits (2-line API enrich + small TS + targeted repro/regression tests).

## What’s solid

- Implementation matches plan verbatim: `list(er.get("empty_tokens") or [])`, `invalidTitle` with `join(", ")`, wrapper-native `title`, no `title` while running.
- Repro tests assert values tied to **To-be**, not presence-only.

## Chuckles branching (read-only)

| Gate | Action |
|------|--------|
| **PROCEED** (clean, artifact complete) | → **Review Posted** → fix-lane clean shortcut → **User Testing** directly; **`resolve-child` skipped**. |
| Merge | Normal parent — **not** orphaned; do **not** merge straight to `dev` from this review alone. |

---

**Slim Linear upshot:**

```
[code-rubric] PROCEED (Commit: 4ef31239) Tooltip repro OK, holds OK
```

context_tokens≈32000
