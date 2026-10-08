# AST-1817 — Invalid vs 0 Avail scheduled actions.

<!-- linear-archive: AST-1817 archived 2026-10-07 -->

## Linear archive (AST-1817)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1817/invalid-vs-0-avail-scheduled-actions  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

Scheduled Actions currently hides every dispatch task with zero available entities by default, and paints an *invalid* task (one whose prompt tokens don't resolve — `empty_render`) with the same faded, unlabeled Run button it would use for any other blocked row. Susan can't tell at a glance which tasks are broken versus simply idle, and the zero-avail rows she needs to see aren't on screen until she clears a filter. This epic makes the Run column say *why* a row can't run (Invalid vs nothing to do), shows the whole task list by default, and gives the table's horizontal scroll back to every column except Task.

## Functional scope

1. **Invalid label.** When a dispatch task is invalid (prompt tokens not found — the existing `empty_render` flag), its Run button reads **Invalid**, uses the light-purple secondary button styling already used elsewhere in the UI (e.g. modal Cancel), stays disabled and unclickable, and is shown at full opacity so the purple is legible.
2. **Zero-avail blocks Run.** When a dispatch task is valid but its available count is 0, the Run button is disabled and faded exactly as invalid rows are muted today; the label stays **Run**. A row that is already running still shows its Stop / Draining… control.
3. **Avail filter defaults to All.** Scheduled Actions loads with every dispatch task visible (no Avail > 0 default). The Avail filter and its `> 0` option remain for Susan to set manually.
4. **Only Task is frozen.** In each section table, only the Task column stays pinned on horizontal scroll; Entity and State scroll with the rest of the columns.

## Component scope

* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — Run-button label/class/blocked logic, Avail filter default, frozen-column count.
* `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **modified** — frozen-column assertions (AST-647 / AST-746 / AST-760 cases), Avail default assertions (AST-887 / AST-894 cases), AST-1782 empty_render Run assertions (button now named Invalid), new zero-avail Run-disabled case.
* `tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx` — **modified** — landing Avail value assertion changes from `gt0` to All.
* `docs/test-bible/frontend/pages.md` — **modified** — Scheduled Actions entries for Avail default, frozen columns, Invalid / zero-avail Run states.
* `src/ui/api/api_admin.py` — **modified** (AST-1819) — `list_dtasks` rows carry the missing-token list alongside `empty_render`.
* `tests/component/ui/api/test_api_admin.py` — **modified** (AST-1819) — list enrich asserts the token list on invalid / valid rows.
* `docs/test-bible/ui/api/api_admin.md` — **modified** (AST-1819) — list_dtasks entry for the token list field.

## Technical scope

* `AdminScheduledActions.tsx`, frozen columns: the page-level frozen-data-column constant passed to `resolveFrozenDataColumns` changes from 3 to 1 so only the Task column receives `list-table-cell-frozen` and a sticky `left`; no change to `listTableLayout.ts` or the shared `list_table_frozen_data_columns` UI config (other list pages keep their own setting).
* `AdminScheduledActions.tsx`, Avail filter: the initial value of the Avail filter state changes from `"gt0"` to `""` (All); the filter predicate, the `> 0` option, and the `always_visible_under_avail_gt0` escape hatch stay as they are.
* `AdminScheduledActions.tsx`, row Run button in `ScheduledPhaseTable`: modified blocked/label logic — (a) when `empty_render` is true the button renders with the existing shared `btn secondary in-row` classes instead of `btn primary in-row`, label **Invalid**, `disabled`, `pointer-events: none`, full opacity; Invalid wins over Run/Sweep labelling. (b) When `empty_render` is false and `available_count` is 0, the row is added to the existing run-blocked condition, so it gets the same `disabled` + 0.25 opacity + `pointer-events: none` treatment invalid rows get today. The running-row Stop/Draining overlay is unchanged. No new CSS class, no inline color literals, no `App.css` edit — reuse of the existing shared button role classes only.
* Tests / bible (Betty, `qa-child`): update the assertions listed in Component scope; add a case proving a valid row with `available_count: 0` has a disabled Run button that fires no `/run` POST, and a case proving an `empty_render` row's button has accessible name Invalid and classes `btn secondary in-row`.
* `api_admin.py`, `list_dtasks` (AST-1819): modified row enrichment — alongside the existing `empty_render` flag, stamp the `empty_tokens` list `_evaluate_dispatch_empty_render` already returns (empty list when valid, or when prompts could not be validated). No new evaluation, no change to the AUTO force-off or its log line.
* `AdminScheduledActions.tsx`, Invalid button (AST-1819): modified — hovering Invalid shows a tooltip with the row's missing tokens comma-separated; when the list is empty it reads `Could not validate prompts`. The tooltip must show although the button is disabled / `pointer-events: none` (e.g. `title` on a wrapping element); the button stays unclickable.

No config, core, or persistence changes: `empty_render` and `available_count` are already served by `GET /api/admin/dispatch_tasks` (`api_admin.list_dtasks`); the only API change is the AST-1819 token-list row field, and the server-side 400 gate on `/run` for empty_render rows stays as-is.

## Architectural definition

* **Patterns to reuse** — no established pattern applies in the active catalog. The shared labeled-button role classes (`.btn.primary` / `.btn.secondary` / `.btn.in-row` in `App.css`) are reused as existing code, not cited as law — their directive (`pattern.ui.shared-button-roles`) sits in `canon/directives/draft/` and is not in force.
* **New patterns proposed** — none.
* **Applicable statutes** — none in the active catalog govern this change: it is a frontend-only presentation change over fields `ui/api` already resolves (`empty_render`, `available_count`). The AST-1819 addition is one extra field on an existing `ui/api` row (no new route, no logging change). No logging, dispatch, batch, entity-metadata, or config surface is touched, so the active `stat.logging.*`, `stat.dispatch.*`, `stat.batch.*`, and `stat.entity.*` statutes do not apply.

## Acceptance criteria

 1. With a row whose `empty_render` is true, the Run cell's button has accessible name **Invalid**, has classes `btn secondary in-row` (not `primary`), is `disabled`, and clicking it (including `fireEvent.click` bypassing pointer-events) sends no `POST …/run` — failing result: button text is Run/Sweep, carries `primary`, is enabled, or a `/run` POST is observed.
 2. That Invalid button's inline style does not set `opacity: 0.25` — failing result: `toHaveStyle({ opacity: "0.25" })` passes on the Invalid button.
 3. With a row whose `empty_render` is false and `available_count` is 0 (not running), the button is named **Run**, is `disabled`, has `opacity: 0.25` and `pointer-events: none`, and a click sends no `POST …/run` — failing result: button enabled, full opacity, or a `/run` POST fires.
 4. With a row whose `empty_render` is false and `available_count` > 0 and AUTO off, Run is enabled and a click POSTs `/run` (existing behaviour preserved) — failing result: button disabled or no POST.
 5. A running row with `available_count` 0 still renders the Stop button and a click POSTs `…/stop` — failing result: Stop missing or disabled while `draining` is false.
 6. On first render the Avail filter `<select>` has value `""` (All) and rows with `available_count` 0 are visible without touching any filter — failing result: value is `gt0` or a zero-avail row is absent until the filter is changed.
 7. Selecting Avail `> 0` still hides zero-avail rows (AST-887 predicate unchanged) — failing result: zero-avail rows remain visible under `> 0`.
 8. In an expanded section table, `columnheader[0]` (Task) and its body cell have class `list-table-cell-frozen`; `columnheader[1]` (Entity) and `columnheader[2]` (State) and their cells do **not**, and have no inline `left` — failing result: Entity or State carries the frozen class or a sticky `left`.
 9. `git diff origin/dev -- src/ui/frontend/src/App.css src/ui/frontend/src/lib/listTableLayout.ts src/utils/config.py` is empty, and `git diff origin/dev -- src/ui/api` touches only `list_dtasks` in `api_admin.py` (AST-1819) — failing result: any diff in the first set, or any other `src/ui/api` change.
10. `grep -nE "#[0-9a-fA-F]{3,6}|rgb\(" src/ui/frontend/src/pages/AdminScheduledActions.tsx` reports no new matches versus `origin/dev` — failing result: an inline color literal added for the Invalid button instead of the shared `btn secondary` class.
11. `npm run build` and `npm run lint` in `src/ui/frontend` pass, and the full `test_AdminScheduledActions*.test.tsx` suite is green — failing result: any build/lint error or red test.
12. (AST-1819) `GET /api/admin/dispatch_tasks` rows include `empty_tokens`: a list of token names for an invalid row whose evaluation found tokens (e.g. `["FIRST_NAME"]`), `[]` for a valid row — failing result: key missing, or a non-list value.
13. (AST-1819) An `empty_render` row with `empty_tokens: ["FIRST_NAME", "GET_RUBRIC"]` renders a tooltip reading `FIRST_NAME, GET_RUBRIC` on the Invalid control; with `empty_tokens: []` it reads `Could not validate prompts`; the Invalid button is still `disabled` and a click sends no `/run` POST — failing result: no tooltip, wrong text, or button clickable.

## Open questions

none

## Proposed child tickets

**Monolith check:** Functional scope has 4 capabilities and there is 1 child — intentional. All four changes land in the same component file (`AdminScheduledActions.tsx`) and the same two test files; splitting would have two or more children claiming the same file, which the scope partition forbids, and each change is only a few lines.

#### 1: **Scheduled Actions Invalid label, zero-avail Run block, Avail All default, Task-only freeze - Hedy**

Ships all four Functional scope capabilities on the Scheduled Actions page: Invalid-labelled secondary-styled disabled button for `empty_render` rows, disabled/faded Run for valid zero-avail rows, Avail filter defaulting to All, and only the Task column frozen. Does not touch the API, config, shared list-table layout helpers, or `App.css`.
**Citations:** none — no active pattern or statute governs a frontend-only presentation change over already-resolved API fields (see Architectural definition).
**Scope:** `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified**; `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **modified**; `tests/component/frontend/pages/test_AdminScheduledActions_AST1104.test.tsx` — **modified**; `docs/test-bible/frontend/pages.md` — **modified**. Technical scope, verbatim: the page-level frozen-data-column constant passed to `resolveFrozenDataColumns` changes from 3 to 1 so only the Task column receives `list-table-cell-frozen` and a sticky `left`; no change to `listTableLayout.ts` or the shared `list_table_frozen_data_columns` UI config (other list pages keep their own setting). The initial value of the Avail filter state changes from `"gt0"` to `""` (All); the filter predicate, the `> 0` option, and the `always_visible_under_avail_gt0` escape hatch stay as they are. Row Run button in `ScheduledPhaseTable`: modified blocked/label logic — (a) when `empty_render` is true the button renders with the existing shared `btn secondary in-row` classes instead of `btn primary in-row`, label **Invalid**, `disabled`, `pointer-events: none`, full opacity; Invalid wins over Run/Sweep labelling. (b) When `empty_render` is false and `available_count` is 0, the row is added to the existing run-blocked condition, so it gets the same `disabled` + 0.25 opacity + `pointer-events: none` treatment invalid rows get today. The running-row Stop/Draining overlay is unchanged. No new CSS class, no inline color literals, no `App.css` edit. Tests / bible (Betty, `qa-child`): update the assertions listed in Component scope; add a case proving a valid row with `available_count: 0` has a disabled Run button that fires no `/run` POST, and a case proving an `empty_render` row's button has accessible name Invalid and classes `btn secondary in-row`.
**Estimate: 2**

---

## Original brief

When the dispatch_task is considered invalid (the tokens aren't found), turn the button to the light purple color of other buttons in the UI with "Invalid" on the button text, still disabled/unclickable.

When the dispatch_task is valid but the avail count is 0, then disable the run button (as we currently do for invalid tasks).

Remove the default Avail >0 on scheduled actions filter, display all dispatch tasks (but allow the avail filter to be set by the user)

Reset the frozen columns to include only the task key, not the entity type and trigger state.  Let those columns scroll horizontally with the other columns in the table.

### Comments

#### chuckles — 2026-09-27T05:17:05.407Z
[fix-intake] Invalid-button tooltip [bug] → filed as AST-1819 (in the fix lane now).

#### susan — 2026-09-27T05:04:59.514Z
\[bug\] Add a tool tip to the Invalid button with a comma separated list of tokens that are missing for the prompt.

#### chuckles — 2026-09-27T04:27:04.241Z
[prep-uat] blocked: polluted publish ref — `7954d0fa test(AST-1768): bug-repro …` rode onto `sub/AST-1817/AST-1818-…` (and `ftr/AST-1817-…`) via the `origin/tests` merge. Its AST-1768 `[bug-repro]` tests are red until AST-1768's fix lands, so landing this ftr would turn dev red (8 failing frontend tests; AST-1818's own suites are 71/71 green).

@Betty White — test tree / bible, revert `7954d0fa` on the AST-1818 sub:
- tests/component/frontend/contexts/test_CandidateContext.test.tsx
- tests/component/frontend/lib/test_sessionAuthMark.test.ts
- tests/component/frontend/pages/test_Authenticate.test.tsx
- tests/component/frontend/pages/test_JobsJobDetail.test.tsx
- tests/component/frontend/stytchMock.tsx
- tests/component/ui/api/test_api_candidate.py
- docs/test-bible/frontend/lib.md
- docs/test-bible/ui/api/api_candidate.md

---

_Implementation detail may live in git history on `origin/dev`._
