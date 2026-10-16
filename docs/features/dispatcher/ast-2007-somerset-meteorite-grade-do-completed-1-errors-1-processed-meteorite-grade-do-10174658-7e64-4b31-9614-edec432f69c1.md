# AST-2007 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-10174658-7e64-4b31-9614-edec432f69c1

<!-- linear-archive: AST-2007 archived 2026-10-13 -->

## Linear archive (AST-2007)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2007/somerset-meteorite-grade-do-completed-1-errors-1-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Susan's direction (round 2)

Great analysis, Chuck!  First, let's validate the rubric codes to be unique two letter codes both in the UI and in the craft.  Do not generate an error when this happens, just uptick the last letter of the code (X, Y, Z, A, B…) until the duplicate is cleared.  Make this a helper function to stand in front of the rubric save event (again, both for UI and craft prompts)

Second, provider call timeout should get a retry.  It's possible the timeout could have been related to the janky rubric codes.

Third, why it's taking 8 minutes is a mystery, for sure, but make sure it's updated in the dispatch ledger the time and timeout status of the run.  We can perform analysis on that.

## As-is

**Rubric codes.** The somerset Do rubric has two stored `rubric_vector` rows that share code `TP` (both labeled "Hands-On Technical Partnership With Engineers"). Every dispatch logs `duplicate rubric codes: TP→[…]`, and the prompt's `{$RUBRIC_VECTORS}` likely lists `TP` twice. Both rubric write paths go through `normalize_rubric_artifacts_on_save` then `apply_rubric_vectors_save`: the UI save in `src/ui/api/api_candidate.py` (\~407) and craft persist in `src/core/candidate.py` (\~3619). AST-1513's `_assert_unique_rubric_codes` **raises** on a duplicate (HTTP 400 on UI; craft persist fails). It also runs *before* `apply_rubric_vectors_save` merges the embedded QC/GC/RC vectors, so a merge-introduced collision is never checked.

**Timeout routing.** A `meteorite_grade_do` OpenRouter call ran 613.9s and hit the 600s budget (AST-1189), returning `failure_class=provider_call_timeout`. Consult only special-cases balance refusal. In the single-job render-verdict path (`src/core/consult.py` \~1451–1466), any other `do_task` failure calls the local `_fail`, which transitions **straight to** `error_state` (`METEORITE_FAILED_TECHNICAL_DO`) with no retry hop. The batch path (`_run_batch_consult` \~1650) does route per-entity via `_consult_batch_fail_dest` (primary → retry holding, retry → terminal). Either way the timeout is treated like a verdict and job `db358880-…` ended terminal.

**Ledger.** `dispatch_ledger` records batch `started_at` / `completed_at`, counts, cost and served `host` ([AST-1960](https://linear.app/astralcareermatch/issue/AST-1960/record-the-serving-host-on-the-dispatch-ledger-add-host-discovery), written from `src/core/agent.py` \~2293 on **successful** calls only). It records neither the provider call's duration nor whether the call timed out. A timed-out run is indistinguishable from any other error there.

**Generation stats.** `Generation stats HTTP 404 … no platform cost after 5 tries` comes from the AST-1963 background platform-cost reconcile. `record_timesheet_entry` (`src/core/timesheets.py` \~47) spawns a daemon thread for every openrouter-routed call. `reconcile_timesheet_platform` waits 30s, then polls `get_generation_stats` (`src/external/openrouter.py`) up to 5 times, and logs this warning when the lookup never resolves. Tunables live in `src/utils/config.py` (`TIMESHEET_RECONCILE_*`, \~5091). No on/off switch exists.

The generation stats are obviously broken.  Let's deactivate them with this issue and revisit in a new epic.

## To-be

1. **Rubric codes self-heal, never error.** A single helper runs in front of every rubric save, UI and craft alike. When two criteria share a two-letter code, it keeps the first and changes the later one's **last letter** in the sequence X, Y, Z, A, B, … (wrapping) until the code is unique within that rubric. Then it saves. No `ValueError` and no 400.
2. **A provider call-budget timeout gets a retry.** On a consult task, a job whose call times out goes to its retry holding (e.g. `METEORITE_PASSED_JD` → its `_RETRY` state), same as AST-642's per-entity routing. It is not sent straight to `METEORITE_FAILED_TECHNICAL_DO`. A timeout while already on retry follows the existing retry → `error_state` rule, so one retry, no infinite loop.
3. **The ledger shows the call's time and timeout status.** For each run, `dispatch_ledger` carries the LLM call duration and whether it ended in `provider_call_timeout`, written for failed calls too. That supports later analysis of the slow runs.
4. **Generation-stats lookup is deactivated.** No background `get_generation_stats` reconcile runs after a call, and no `no platform cost after N tries` warnings appear. Timesheet rows keep their calculated (catalog) cost. The reconcile code stays in place behind a config-owned switch so a future epic can revisit it. The OpenRouter host probe (`get_batch_host`, AST-1960) is **not** touched.

## Proposed steps

1. Add a rubric-code dedupe helper in `src/core/candidate.py` that bumps the last letter (X→Y→Z→A→B…) of any later duplicate until unique. Call it in `apply_rubric_vectors_save` immediately before `database.sync_rubric_vectors_from_criteria`, after the embedded QC/GC/RC merge, so both UI and craft saves pass through it. Retire the raise in `_assert_unique_rubric_codes` (remove it from `normalize_rubric_artifacts_on_save`).
2. In `src/core/consult.py`'s single-job render-verdict path, route a `failure_class == PROVIDER_CALL_BUDGET["failure_class"]` result through `_consult_batch_fail_dest(job state, error_state)` (primary → retry holding) instead of `_fail`'s direct `error_state`. Confirm `_run_batch_consult` and the \~1264 consult path already reach retry holding for a timeout. Add the same branch if not.
3. Add two `dispatch_ledger` columns in `src/data/database.py` (create + migration list, [AST-1960](https://linear.app/astralcareermatch/issue/AST-1960/record-the-serving-host-on-the-dispatch-ledger-add-host-discovery) style, no backfill): one for LLM call duration (seconds), one for the failure class or timeout status. In `src/core/agent.py`, write them next to the existing host write, for successful and failed calls alike.
4. Add a config-owned on/off flag beside `TIMESHEET_RECONCILE_*` in `src/utils/config.py`, set **off**. `record_timesheet_entry` in `src/core/timesheets.py` returns before spawning the reconcile thread when it's off.
5. Data: re-save somerset's Do rubric (UI) once step 1 lands so the stored `TP` duplicate is re-coded. Re-run `meteorite_grade_do` on staging and check whether the slow call recurs with clean codes (Susan's hunch).

## Component scope

* `src/core/candidate.py`: modified. Home of the new pre-save rubric code dedupe helper, wired into `apply_rubric_vectors_save` (shared by UI and craft). `_assert_unique_rubric_codes`'s raise is retired.
* `src/core/consult.py`: modified. The single-job render-verdict failure branch must send a provider timeout to retry holding instead of directly to `error_state`.
* `src/data/database.py`: modified. `dispatch_ledger` schema gains call-duration and timeout/failure-class columns (create + idempotent migration). `update_dispatch_ledger`'s column allowlist picks them up.
* `src/core/agent.py`: modified. After `_send_to_server`, record call duration and failure class on the active ledger row for failed calls too, not just the success-only host write.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx`: modified, optional. Shows the new ledger columns if Susan wants them visible in the Performance Monitor rather than DB-only.
* `src/utils/config.py`: modified. Holds the new switch that deactivates the generation-stats platform-cost reconcile, next to its existing tunables.
* `src/core/timesheets.py`: modified. `record_timesheet_entry` must honor that switch and stop spawning the reconcile thread.
* `src/data/database.py` (rubric sync, amended per AST-2008 \[scope-gate\]): modified. `sync_rubric_vectors_from_criteria` must retire extra current `rubric_vector` rows that share a code, so stored duplicates (like somerset's `TP` pair) actually clear on the next save instead of piling up upticked copies.

## Technical scope

* `src/core/candidate.py`: new function, a pure code-dedupe helper (criteria list in, same list with later duplicate codes re-lettered). `apply_rubric_vectors_save` is modified to call it before sync. `normalize_rubric_artifacts_on_save` is modified to drop the raising duplicate check, so collisions are repaired rather than rejected.
* `src/core/consult.py`: modified function. The single-job render-verdict path adds a timeout branch that resolves its destination through the existing `_consult_batch_fail_dest`, so the timeout gets a retry hop, consistent with batch routing.
* `src/data/database.py`: modified functions and new fields. `_ensure_dispatch_ledger_schema` adds two columns, and the update path accepts them. Old rows stay NULL.
* `src/core/agent.py`: modified function. `do_task`'s post-call ledger write records duration and failure class from the provider result on every outcome. It stays off the event loop and non-fatal, like the host write.
* `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` (optional): modified component, adding two columns to the ledger table.
* `src/utils/config.py`: new field. A boolean enable flag for the timesheet platform-cost reconcile, default off, so deactivation is config-owned rather than deleted code.
* `src/core/timesheets.py`: modified function. `record_timesheet_entry` gets an early return when the flag is off. `reconcile_timesheet_platform` and `get_generation_stats` stay unchanged for the future epic.
* `src/data/database.py` (rubric sync): modified function. When several `current = 1` rows for one (candidate, task_key) share a code, `sync_rubric_vectors_from_criteria` keeps the first (rowid order) and retires the rest through the existing retire helper. Without this, the dict keyed by code masks the older duplicate and it is never retired.

**Defaults carried into plan-fix** (Susan approved this reading without overriding; plan-fix raises a Plan Discuss if either turns out wrong):

* Duplicate codes are always upticked per Susan's direction, including identical-label pairs like today's `TP` (one becomes e.g. `TX`). Nothing is collapsed.
* "Get a retry" means one retry-holding hop (AST-642 convention), not an immediate in-call re-send to the provider.

## Ancestor candidates

- [X] AST-1510 / AST-1513: meteorite_grade_do failing / reject duplicate Do rubric codes (`docs/features/consult/ast-1510-meteorite-grade-do-is-failing.md`, `ast-1513-reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing.md`). Built the `_assert_unique_rubric_codes` raise that this fix turns into an auto-uptick. Same somerset `TP` collision.
- [ ] AST-1189: Provider call budget + timeout failure class (`docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md`). Introduced the 600s budget and `provider_call_timeout`, but left core routing out of scope.
- [ ] AST-642: per-entity retry vs error routing in mixed batch consult (`docs/features/dispatcher/ast-642-per-entity-retry-vs-error-routing-in-mixed-batch-consult-auto-retry.md`). Owns `_consult_batch_fail_dest`, the routing the timeout should reuse.
- [ ] AST-1960: record the serving host on the dispatch ledger (`docs/features/foundation/ast-1960-record-the-serving-host-on-the-dispatch-ledger.md`). Exact precedent for adding a ledger column plus the agent-side write.
- [ ] AST-1155 / AST-1760: incomplete grades / all-X grades retry holding (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`, `ast-1760-all-x-scored-grades-retry-holding.md`). Consult retry-holding family.
- [ ] AST-1842: roster holds state on balance refusal + call-budget timeout (cited in `src/core/roster.py`; no doc under `docs/features/`). Roster-side timeout handling precedent.
- [ ] AST-1283: Grade_do is erroring (`docs/features/consult/ast-1283-grade-do-is-erroring.md`). Same meteorite grade_do failure family.
- [ ] [AST-1964](https://linear.app/astralcareermatch/issue/AST-1964/model-routing-type-and-openrouter-generation-stats-lookup-query-llm) / AST-1966: OpenRouter generation-stats lookup / reconcile unpriced rows (`docs/features/agent/ast-1964-…`, `ast-1966-…`). Source of the 404 cost warning; the AST-1963 reconcile is what this fix switches off, pending a new epic.

---

## Original report

```
2026-10-06 18:40:08  [WARNING]  duplicate rubric codes: TP→['Hands-On Technical Partnership With Engineers', 'Hands-On Technical Partnership With Engineers']
2026-10-06 18:40:08  [INFO]  somerset | dispatch job starting meteorite_grade_do — 1 available (batch: meteorite_grade_do-10174658-7e64-4b31-9614-edec432f69c1)
2026-10-06 18:45:20  [WARNING]  gen-1791312009-t5e6pQB6lYED0dZluC2M | batch meteorite_grade_do-10174658-7e64-4b31-9614-edec432f69c1 -> no platform cost after 5 tries [Generation stats HTTP 404: {"error":{"message":"Generation gen-1791312009-t5e6pQB6lYED0dZluC2M not found","code":404}}]. The row keeps its calculated cost
2026-10-06 18:50:24  [INFO]  somerset | dispatch job task completed: meteorite_grade_do pass:0 fail:0 error:1 (batch: meteorite_grade_do-10174658-7e64-4b31-9614-edec432f69c1)
2026-10-06 18:50:24  [WARNING]  db358880-2052-4126-b714-97fc6c6e54c5 -> METEORITE_FAILED_TECHNICAL_DO [Provider call exceeded per-call time budget (600s)]
2026-10-06 18:50:24  [WARNING]  LLM openrouter task=meteorite_grade_do 613.9s error=Provider call exceeded per-call time budget (600s)
```

### Comments

#### chuckles — 2026-10-06T19:49:04.296Z
Heads-up: `tests/component/core/test_timesheets.py::TestAst1966RetryThenGiveUp` has 5 failing cases on `origin/dev` today, and the same 5 fail on this ftr. They're pre-existing and not caused by [AST-2008](https://linear.app/astralcareermatch/issue/AST-2008), but they live in the reconcile code this fix switches off. Worth folding into the generation-stats revisit epic.

#### susan — 2026-10-06T19:31:41.938Z
A pleas

#### chuckles — 2026-10-06T19:23:25.028Z
@susan: one process call is needed before [AST-2008](https://linear.app/astralcareermatch/issue/AST-2008) can build.

Plan is done (Hedy). Fix-board came back **Joan CANON: OK**, **Betty TESTS: REVISE**:
- 3 existing tests break: the AST-1513 raise test, an AST-1966 reconcile-thread test, and an AST-1960 ledger-message test.
- No coverage exists for the new branches, and candidate/consult/agent/timesheets are locked at 100% coverage.

bug-fix's orphaned rule says a REVISE should file a separate sibling "gap" child instead of running qa-fix. That doesn't work cleanly for tests: AST-2008's test-fix and the coverage gate can't pass until Betty's tests are on AST-2008's own branch, and a gap child that lands afterward leaves AST-2008 red. Options:
- **A (my pick):** Betty runs `qa-fix` on AST-2008 itself, landing the tests red-first on its branch. That's the normal fix-board REVISE path. No gap child.
- **B:** file the gap child as the tracker for Betty's work, but she still lands the tests on AST-2008's branch via qa-fix. The gap child closes alongside it.
- **C:** a true separate gap child, sequenced first with AST-2008 blocked by it, and its tests merged into the ftr before AST-2008 builds.

AST-2008 is parked at Plan Discuss. Reply with A, B or C and reassign AST-2007 to Chuckles to resume.

---

_Implementation detail may live in git history on `origin/dev`._
