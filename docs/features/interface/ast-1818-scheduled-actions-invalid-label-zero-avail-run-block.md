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
