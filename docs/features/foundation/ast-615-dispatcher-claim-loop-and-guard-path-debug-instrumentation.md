# AST-615 — Dispatcher claim, loop, and guard-path debug instrumentation (Debug logging backfill: dispatcher)

- **Linear (this ticket):** [AST-615](https://linear.app/astralcareermatch/issue/AST-615/dispatcher-claim-loop-and-guard-path-debug-instrumentation-debug)
- **Parent:** [AST-540](https://linear.app/astralcareermatch/issue/AST-540/debug-logging-backfill-dispatcher)
- **Publish ref:** `origin/sub/AST-540/AST-615-dispatcher-claim-loop-guard-debug` (child of AST-540; not Linear `gitBranchName`)
- **Depends on:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) / [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — shared helper + §1.5.1 on integration line; [AST-557](https://linear.app/astralcareermatch/issue/AST-557/inflow-discovery-representative-debug-instrumentation) — representative `inflow_discovery` dispatcher branches to unify, not regress.

## Summary

Backfill the **AST-538** debug logging contract across **all** dispatcher orchestration paths in `src/core/dispatcher.py`: task start context in the scheduler handoff, per-entity claim index headers and `|` detail lines, batch loop drain iteration context, skip/guard early exits, batch-end summaries **after** per-index detail, and unchanged **debug** passthrough into `consult.run_consult_task`. Retire hand-rolled `logger.info("[DEBUG] …")` lines everywhere this ticket touches. **AST-557** already instrumented `inflow_discovery` behind `_INFLOW_DISCOVERY_KEY` guards — this ticket **generalizes** those branches to all task keys and removes the inflow-only gates so one code path serves every dispatch task.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Consult, roster, agent, gazer, builder, external LLM modules | **AST-541**–**AST-546** |
| Hop-boundary logging (`run_next hop: …`, AST-527/530) | Unchanged — INFO, not debug-gated |
| Dispatch business logic, batch sizes, ledger schema, scheduler threading | Forbidden per parent |
| Betty log-string tests | Forbidden per parent |
| `src/data/` logging | Forbidden per Code Rules |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/dispatcher.py` | Contract debug across `_dispatch_one`, `_run_dispatch_loop`, `_run_task`, `_run_unified`, `_check_circuit_breaker`; retire `[DEBUG]` in touched blocks; remove `_INFLOW_DISCOVERY_KEY`-only contract gates once generalized | core |

## Stage 1: Entity identifier helper and scheduler task start (`_dispatch_one`)

**Done when:** With `debug=True`, every dispatch thread start logs task identity (task key, candidate, available count, batch id, auto vs click mode, run_next chain flag) before the existing `_sched_log.info("Dispatching …")`; missing candidate/API key skip emits contract detail; with `debug=False`, no new contract lines on these paths.

1. After `_INFLOW_DISCOVERY_KEY = …` (line ~42), add a module-private helper:

```python
def _dispatch_entity_identifier(entity_type: str, row: Dict[str, Any]) -> str:
    """Primary debug identifier for a claimed entity row (§1.5.1 style D)."""
    if entity_type == "job":
        return str(row.get("astral_job_id") or row.get("company") or "?")
    if entity_type == "company":
        return str(row.get("short_name") or row.get("company") or "?")
    if entity_type == "board_search":
        return str(row.get("board_search_id") or row.get("board_key") or "?")
    if entity_type == "candidate":
        return str(row.get("astral_candidate_id") or row.get("candidate_id") or "?")
    return str(row.get("id") or "?")
```

2. In `_dispatch_one`, immediately after `is_click = not bool(task.get("auto_mode"))` (~line 416), add:

```python
debug = bool(task.get("debug"))
if debug:
    logger.set_debug_flag(True)
```

3. Replace the early return at ~418–421 (no candidate or API key) with:

   - When `debug`: before `return`, call `logger.debug_index(func="dispatcher._dispatch_one", index=1, total=1, identifier=task_key, outcome="skipped — no candidate or API key")` and `logger.debug_detail(f"candidate_id={candidate_id!r}")`.
   - When not `debug`: keep existing `_sched_log.error(...)` only (unchanged message).

4. After `entity_batch_id = f"{task_key}-{uuid.uuid4()}"` and `has_run_next_chain = …` (~426–427), when `debug`:

```python
logger.debug_index(
    func="dispatcher._dispatch_one",
    index=1,
    total=1,
    identifier=task_key,
    outcome="task start",
)
logger.debug_detail(
    f"candidate_id={candidate_id} available_count={task.get('available_count', 0)} "
    f"entity_batch_id={entity_batch_id} mode={'AUTO' if not is_click else 'CLICK'} "
    f"run_next_chain={has_run_next_chain} entity_type={task_entity_type!r} "
    f"trigger_state={task.get('trigger_state')!r}"
)
```

5. Do **not** remove existing `_sched_log.info("Dispatching …")` — production scheduler INFO coexists per §1.5.1.

## Stage 2: Batch loop drain instrumentation (`_run_dispatch_loop`)

**Done when:** With `debug=True`, each loop iteration logs iteration index, available count, effective min_count, and post-batch summary counts; every loop exit path (first-pass min_count skip, post-run min_count, drain flag, zero processed, max_runs) emits a `|` detail explaining why the loop stopped; with `debug=False`, behavior unchanged.

1. At `_run_dispatch_loop` entry (~518), after `debug = bool(task.get("debug"))`, when `debug`:

```python
logger.set_debug_flag(True)
```

2. Before the `if available < effective_min:` block (~529), when `debug` and `run_count == 0`:

   - If `available < effective_min`: emit `logger.debug_index(func="dispatcher._run_dispatch_loop", index=1, total=1, identifier=task_key, outcome="skipped — below min_count")` and `logger.debug_detail(f"available={available} effective_min={effective_min} is_auto={is_auto}")` **before** the existing `_sched_log.info("Skipping …")` and `break`.

3. At the top of each loop iteration (after drain check passes, immediately before `summary = await _run_task(...)` ~543), when `debug`:

```python
loop_iter = run_count + 1
logger.debug_index(
    func="dispatcher._run_dispatch_loop",
    index=loop_iter,
    total=loop_iter,  # total unknown until loop ends — use current iter as both until exit
    identifier=task_key,
    outcome=f"loop iteration {loop_iter} starting",
)
logger.debug_detail(
    f"available={available} effective_min={effective_min} max_runs={max_runs!r} "
    f"draining={draining} entity_batch_id={entity_batch_id}"
)
```

⚠️ **Decision:** Loop iteration headers use `index=loop_iter, total=loop_iter` during the pass because final iteration count is unknown mid-loop; on loop exit add one `debug_detail` with `total_runs={run_count}` — acceptable per §1.5.1 (operational unit = one drain pass).

4. After `summary = await _run_task(...)` and accumulator update (~543–545), when `debug`:

```python
logger.debug_detail(
    f"iteration {loop_iter} summary processed={summary.get('total_processed', 0)} "
    f"passed={summary.get('total_passed', 0)} failed={summary.get('total_failed', 0)} "
    f"errors={summary.get('total_errors', 0)} accumulated={accumulated}"
)
```

5. On each `break` path after a run (`available < effective_min` with `run_count > 0`, `draining`, `total_processed == 0`, `max_runs` hit), when `debug`, emit **one** `logger.debug_detail(...)` naming the stop reason **before** `break` (do not duplicate `_sched_log.info` text — contract detail is additive):

   - `"loop stop: remaining below min_count"` with `available`, `effective_min`, `run_count`
   - `"loop stop: drain flag set"` with `run_count`
   - `"loop stop: zero processed this iteration"` with `run_count`
   - `"loop stop: max_runs reached"` with `max_runs`, `run_count`

## Stage 3: `_run_task` — all task keys, retire `[DEBUG]`

**Done when:** Every `_run_task` call with `debug=True` uses `debug_index` / `debug_detail` for start and end; all `logger.info("[DEBUG] _run_task …")` lines in this function are removed; `inflow_discovery`-only gates (`task_key == _INFLOW_DISCOVERY_KEY`) are removed here in favor of unconditional debug contract when `debug=True`.

1. Replace the entire block ~368–388 with:

```python
if debug:
    logger.set_debug_flag(True)
    logger.debug_index(
        func="dispatcher._run_task",
        index=1,
        total=1,
        identifier=task_key or "?",
        outcome="running batch",
    )
    logger.debug_detail(
        f"batch_size={task.get('batch_size')} batch_id={bid} "
        f"entity_type={task.get('entity_type')!r} trigger_state={task.get('trigger_state')!r}"
    )
summary = await _run_unified(task, ctx, debug)
if debug:
    logger.debug_detail(f"runner returned summary={summary}")
return summary
```

2. Delete both `elif debug: logger.info("[DEBUG] _run_task …")` branches — no grandfather `[DEBUG]` in `_run_task` after this stage.

## Stage 4: `_run_unified` — guards, claim phase, chunks, batch end

**Done when:** AC 1–3 satisfied on dispatcher paths: company/job/board/candidate batches show per-entity index headers before batch summary; chunk-exhaust job consult shows per-chunk headers; network/min_count/trigger_state skips show `|` detail; all `[DEBUG] _run_unified` lines removed; `_INFLOW_DISCOVERY_KEY` contract gates removed; `debug=False` unchanged.

1. At `_run_unified` entry after local variables (~170), replace:

```python
if debug and dispatch_task_key == _INFLOW_DISCOVERY_KEY:
    logger.set_debug_flag(True)
```

with:

```python
if debug:
    logger.set_debug_flag(True)
```

2. **Network unreachable** (~150–156): before `return dict(_SUMMARY_ZERO)`, when `debug`:

```python
logger.debug_index(
    func="dispatcher._run_unified",
    index=1,
    total=1,
    identifier=dispatch_task_key or "?",
    outcome="skipped — network unreachable",
)
logger.debug_detail(f"entity_type={entity_type!r} trigger_state={input_state!r}")
```

Keep existing `_sched_log.warning(...)` unchanged.

3. **Trigger state mismatch** (~171–180): before `return dict(_SUMMARY_ZERO)`, when `debug`:

```python
logger.debug_index(
    func="dispatcher._run_unified",
    index=1,
    total=1,
    identifier=dispatch_task_key,
    outcome="skipped — trigger_state mismatch",
)
logger.debug_detail(f"expected={expected!r} got={input_state!r}")
```

Keep existing `_sched_log.warning(...)` unchanged.

4. **No entities claimed** (~244–255): replace the `_INFLOW_DISCOVERY_KEY` / `elif debug` split with a single block when `debug`:

```python
logger.debug_index(
    func="dispatcher._run_unified",
    index=1,
    total=1,
    identifier=f"{entity_type}/{input_state}",
    outcome="no entities claimed",
)
logger.debug_detail(
    f"task_key={dispatch_task_key} batch_id={bid} batch_call_mode={batch_call_mode} "
    f"dispatch batch_size={limit!r}"
)
```

Delete `logger.info("[DEBUG] _run_unified[...]: no entities claimed", ...)`.

5. **Entities claimed** (~257–277): replace `_INFLOW_DISCOVERY_KEY` / `elif debug` split with:

   - When `debug`, first emit one aggregate header (batch-level context):

```python
entity_total = len(entities)
logger.debug_index(
    func="dispatcher._run_unified",
    index=1,
    total=1,
    identifier=f"{entity_type}/{input_state}",
    outcome=f"claimed {entity_total} entity/entities",
)
logger.debug_detail(
    f"task_key={dispatch_task_key} batch_id={bid} batch_call_mode={batch_call_mode} "
    f"dispatch batch_size={limit!r} claim_cap={claim_cap!r}"
)
```

   - Use `claim_cap` only in the job branch — for the detail line in other branches pass `claim_cap=None` in an f-string as `None` (define `claim_cap = None` before the `if entity_type == "board_search"` chain so the name always exists).

   - Then loop `for ei, entity in enumerate(entities, start=1):` when `debug`:

```python
logger.debug_index(
    func="dispatcher._run_unified",
    index=ei,
    total=entity_total,
    identifier=_dispatch_entity_identifier(entity_type, entity),
    outcome="claimed",
)
logger.debug_detail(
    f"entity_type={entity_type} trigger_state={input_state} state={entity.get('state')!r}"
)
```

   - Delete `logger.info("[DEBUG] _run_unified[...]: claimed %d entities …")`.

6. **Chunk exhaustion** (~288–313): inside `if use_chunk_split:`, before `head = await _consult_chunk(0, chunks[0])`, when `debug`:

```python
chunk_total = len(chunks)
for ci, chunk_rows in enumerate(chunks):
    logger.debug_index(
        func="dispatcher._run_unified",
        index=ci + 1,
        total=chunk_total,
        identifier=f"chunk task_key={dispatch_task_key}",
        outcome=f"consult chunk size={len(chunk_rows)}",
    )
    logger.debug_detail(
        f"batch_id={bid} batch_chunk_index={ci} chunk_width={chunk_sz} "
        f"entities_in_chunk={len(chunk_rows)}"
    )
```

   Emit chunk headers **before** downstream consult output (AC 2). Do not re-log inside `_consult_chunk` closure.

7. **Batch end** (~331–341, before `return s` in the `try` path): when `debug` and `entity_total > 0`:

```python
logger.debug_detail(f"batch end summary={s}")
```

   This line must appear **after** all per-entity and per-chunk headers from steps 5–6 (AC 1 / parent batch-end rule).

8. Remove unused `_INFLOW_DISCOVERY_KEY` import usage for debug gating only if no other references remain — **keep** the constant if still referenced elsewhere in the file; if debug is the only use, remove the constant and the `INFLOW_CONFIG` import **only when** grep confirms zero remaining references.

## Stage 5: Circuit breaker debug context (`_check_circuit_breaker`)

**Done when:** When `debug=True` and the circuit breaker auto-disables a task, a contract `debug_detail` precedes the existing `logger.warning`; when breaker does not fire or `debug=False`, no new lines.

1. In `_check_circuit_breaker`, inside the `if all(...)` block (~356–361), before `logger.warning("CIRCUIT BREAKER: …")`, when `debug`:

```python
logger.set_debug_flag(True)
logger.debug_detail(
    f"circuit breaker: task_key={task_key} candidate_id={candidate_id} "
    f"task_id={task_id} consecutive_zero_progress={_CIRCUIT_BREAKER_THRESHOLD}"
)
```

2. Do **not** change disable logic or threshold.

## Stage 6: Manual verification (build agent / Susan UAT)

**Done when:** Build agent documents spot-check notes in Linear comment or accepts parent AC 4 without automated log tests.

1. **debug=False spot-check:** Run one company-batch dispatch and one job-batch dispatch with `debug=False` on the task row — confirm **no** new lines matching contract headers (`index N/M` with ` -> `) and **no** new ` | ` detail lines from touched dispatcher paths. Existing `_sched_log` / WARNING / hop lines may still appear.

2. **debug=True company batch:** Run `inflow_resolve_website` or another company `entity_type` batch with ≥1 claimed entity — confirm per-entity index headers appear **before** `batch end summary=…`.

3. **debug=True job chunk exhaust:** Run a scored consult task in `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` with eligible count > `batch_size` — confirm per-chunk index headers before consult output.

4. **debug=True skip paths:** With network stub unreachable (or min_count gate on AUTO task with empty queue), confirm `|` detail explains skip when `debug=True`.

(No new pytest files — parent forbids Betty log-string tests.)

## Self-Assessment

**Scope:** `Single-Component` — Only `src/core/dispatcher.py` changes; all instrumentation uses existing `src/utils/logging.py` helpers without new modules.

**Conf:** `high` — AST-554/557 established the contract and a representative dispatcher pattern; this ticket generalizes known gates to full coverage with explicit per-path steps.

**Risk:** `Medium` — Dispatcher is shared production infrastructure; incorrect `set_debug_flag` or missing `if debug` guards could add console noise when `debug=False` or omit traces during UAT.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.5.1 | All contract emission gated on `debug=True` via `set_debug_flag` + helpers; batch summary after per-index detail; retire `[DEBUG]` in touched blocks |
| §1.3 DRY | One `_dispatch_entity_identifier` helper; reuse `debug_index` / `debug_detail` throughout |
| §2.1 config | No new config keys; reads existing task row fields only |
| §2.4 batch | Per-entity and per-chunk indices inside batch loops; no claim/clear semantic changes |
| §2.6 state machine | No state transitions changed |
| §3.3 imports | No new cross-layer imports; helper is local to dispatcher |
| §3.5 naming | `func=` strings use `dispatcher.*` prefix consistently |
| §3.6 spikes | No spike output |

No conflicts requiring `conf-!!-NONE`.

## Execution contract

- Stages **1 → 6** in order; one `code()` commit per stage 1–5 on epic worktree, then publish to **`origin/sub/AST-540/AST-615-dispatcher-claim-loop-guard-debug`**.
- Stage 6 is manual verification only — no commit unless product fix required.
- Blocking questions → parent **AST-540** with 🛑 format from **plan-child**.
- **Passthrough:** Do not modify `consult.run_consult_task`, roster, or agent signatures — `debug` argument passing already exists on consult calls (~299, 316, 324); leave unchanged.

## Review (build stub)

**Built:** `origin/sub/AST-540/AST-615-dispatcher-claim-loop-guard-debug` @ `05cd51b9`.

**Stages delivered:**
- Stage 1: `_dispatch_entity_identifier` + `_dispatch_one` task start / skip debug — `ddfd1756`.
- Stage 2: `_run_dispatch_loop` iteration and loop-exit debug — `f5c522ca`.
- Stage 3: `_run_task` generalized contract, retire `[DEBUG]` — `39711a34`.
- Stage 4: `_run_unified` guards, claim, chunk, batch-end debug; remove `_INFLOW_DISCOVERY_KEY` — `05cd51b9`.
- Stage 5: `_check_circuit_breaker` debug context (same commit as stage 4) — `05cd51b9`.

**Stage 6 (manual):** Susan UAT — `debug=False` spot-check; company batch + job chunk + skip paths with `debug=True`. No Betty log-string tests per parent.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-540/AST-615-dispatcher-claim-loop-guard-debug` @ `f8d5b3a8` — `src/core/dispatcher.py`, `src/utils/config.py`, plan doc, test bible manifest.

### What's solid

| Area | Notes |
|------|--------|
| Plan fidelity | Stages 1–5 delivered: `_dispatch_entity_identifier`, `_dispatch_one` start/skip, `_run_dispatch_loop` iteration + exit detail, `_run_task` / `_run_unified` generalized contract, `_check_circuit_breaker` context, chunk headers before consult. |
| §1.5.1 / AST-538 | Contract emission gated on `debug=True` + `set_debug_flag`; per-entity `index N/M` under claim; chunk indices before `_consult_chunk`; `batch end summary=` after per-index detail; hand-rolled `[DEBUG]` retired in touched blocks. |
| `debug=False` | Helpers only under `if debug`; existing `TestRunUnified::test_returns_zero_without_debug_logging` and `TestRunTask::test_runs_without_debug_logging` cover passthrough. |
| §2.4 batch | Claim/clear semantics unchanged; instrumentation inside existing loops only. |
| Layers | No new cross-layer imports beyond existing `config` / `data` patterns in dispatcher. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `src/utils/config.py` + `_trigger_state_scored` | Adds `dispatch_claim_uses_score_floor` and switches claim gating from `trigger_state_used_by_scored_dispatch_task` (`f8d5b3a8`). Correct per **§2.1** / **AST-586** (VALID_TITLE must not apply score floor at claim), but ticket boundary says *no dispatch business logic* and plan Self-Assessment says *dispatcher.py only*. Confirm intentional co-land vs split to **AST-586**; note on parent if kept here. |
| **advisory** | `_run_dispatch_loop` loop headers | `index=loop_iter, total=loop_iter` mid-loop — plan Stage 2 documents this; acceptable for UAT scan. |
| **advisory** | Build stub tip | Stub cites `05cd51b9`; branch tip is `f8d5b3a8` (test commit for discuss row above). |

### Recommended actions

| Priority | Action |
|----------|--------|
| — | **resolve-child:** no fix-now on debug instrumentation. |
| **discuss** | Engineer or Susan: confirm `dispatch_claim_uses_score_floor` co-land on **AST-615** vs sibling **AST-586** ticket; update parent comment if intentional. |
| Optional | Susan UAT Stage 6: company batch + job chunk + skip paths per plan. |

## Resolution (Ada)

**Date:** 2026-06-14 · **Publish ref tip:** `f1921df1` (pre-resolve)

| Review item | Resolution |
|-------------|------------|
| **fix-now** | None — debug instrumentation accepted as-is. |
| **discuss** (`dispatch_claim_uses_score_floor` in `config.py`) | **Intentional co-land on AST-615.** Betty's manifest includes `test_qualify_valid_title_claim_without_score_floor` (AST-586 regression in the locked dispatcher suite). `test-child` required adding the helper + `_trigger_state_scored` wiring to pass manifest; aligns with **§2.1** / parent **AST-540** claim-path correctness. Full AST-586 admin/database call sites remain sibling scope — note on parent **AST-540** if rollup needs tracking. |
| **advisory** (loop `total=loop_iter`) | No change — plan Stage 2 decision stands. |

**§9a:** publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-540-debug-logging-backfill-dispatcher`.
