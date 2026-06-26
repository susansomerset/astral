<!-- linear-archive: AST-619 archived 2026-06-23 -->

## Linear archive (AST-619)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-619/consult-claim-loop-and-grading-path-debug-instrumentation-debug  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-543 — Debug logging backfill: consult  
**Blocked by / blocks / related:** parent: AST-543

### Description

## What this implements

Backfill the **AST-538** debug logging contract across **consult** batch and grading paths in `src/core/consult.py`: consult claim loops, encoded rubric evaluation, job consult stages, and state transitions with index headers and `|` detail lines. Debug runs must show per-job inputs, grading branches, and pass/fail reasons — not only batch totals.

## Acceptance criteria

1. A representative **consult** batch with **debug=True** shows, **before** the batch summary line, index headers and `|` detail for each claimed job in that pass plus grading branch context (pass/fail reason).
2. Rubric evaluation paths (`_render_pass_fail`, `_render_score`, verdict rendering) emit `|` detail explaining branch taken when **debug=True**.
3. **debug=False** produces no new debug-only log lines on touched consult paths (spot-check one consult batch).
4. Radia review treats missing or inadequate debug instrumentation on touched consult **debug** surfaces as **fix-now** per **AST-538**.

## Boundaries

* Does **not** instrument dispatcher, roster, agent, gazer, builder, or external LLM modules — sibling backfill tickets **AST-540**–**AST-546**.
* Does **not** change consult scoring, state machine, or business logic.
* Does **not** add Betty log-string tests.

## Notes for planning

* Use shared debug helper from **AST-538** (`src/utils/logging.py`); retire hand-rolled `logger.debug` / `[DEBUG]` INFO lines in touched consult code where the AST-538 contract applies.
* Primary file: `src/core/consult.py`.
* Lazy-import patterns unchanged; logging only.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-543-debug-logging-backfill-consult`, child `sub/AST-543/<child-id>-consult-claim-loop-grading-debug`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-14T04:45:09.658Z
**Review** — `origin/dev...origin/sub/AST-543/AST-619-consult-claim-loop-grading-debug` @ `08b8f377`

Plan doc: `docs/features/foundation/ast-619-consult-claim-loop-and-grading-debug-instrumentation.md` (Review section)

### fix-now

- **`src/core/agent.py`** (~86 lines vs `origin/dev`) — **§5d / plan execution contract.** Ticket forbids `agent.py`. Publish ref drops `_resume_hop_debug_index`, resume-hop `debug_detail`, and legacy `[DEBUG]` while keeping partial `_do_task_debug_*` from a sibling merge. **Revert `agent.py` to byte-match `origin/dev`** on this ref (agent backfill is AST-541/618).

### discuss

- **Grading detail order (§1.5.1):** `_render_pass_fail` / `_render_score` emit `debug_detail` inside `process_fn` before `_run_batch_consult` emits the per-job `debug_index`. OK for UAT if branch-then-index is acceptable; otherwise reorder in resolve.
- **Sticky `set_debug_flag`:** No reset on batch exit — confirm debug=False spot-check after a debug batch in the same worker.

### solid (consult.py)

- `_LOG_DEBUG` / `[DEBUG]` retired; contract via `set_debug_flag` + helpers.
- `_run_batch_consult`: batch start, per-job indices (incl. failures), missing IDs, batch-end detail ordering.
- `qualify_job_listings` / `evaluate_jd_batch`: input + JD-readiness indices; legacy INFO gated `if not debug:`.
- Scored dispatch skip indices; `render_verdict` + `_apply_render_verdict_decoded_job(debug=…)`.
- No batch claim/clear or transition semantic changes (§2.4/§2.6).

### advisory

- Betty bible + `enable_debug_log` fixture — appropriate for `_LOG_DEBUG` removal.

#### betty — 2026-06-14T04:41:22.433Z
## QA test manifest (§7.13zzg)

**Publish:** `origin/sub/AST-543/AST-619-consult-claim-loop-grading-debug` @ `9cb5a5bb` (`merge-tests(AST-619): origin/tests 74b5ea01`)

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref = `77b8f02f472a6a367ff0915c5484a364cd27fad2`

Instrumentation-only child — **no new log-string tests** per ticket AC. Existing **`LOCKED_AT_100`** + §7.13zt contract regression.

1. **`tests/component/core/test_consult.py`** — full file (branch lock on `src/core/consult.py`)
2. **`tests/component/utils/test_debug_logging.py`** — §7.13zt gating/truncation regression
3. **`tests/component/utils/test_logging_batch.py`** — batch helper regression

**Narrowed run (pytest-only):**

```bash
.venv/bin/python -m pytest tests/component/core/test_consult.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

**Manifest focus (existing classes):**

| Touched path | Existing tests |
| --- | --- |
| `_render_pass_fail` / `_render_score` | `TestRenderPassFail`, `TestRenderPassFailDebug`, `TestRenderScore`, `TestRenderScoreBranches` |
| `_run_batch_consult` | `TestRunBatchConsult`, `TestRunBatchConsultBranches` |
| `qualify_job_listings` / `evaluate_jd_batch` | `TestQualifyJobListings`, `TestEvaluateJdBatch` |
| `render_verdict` | `TestRenderVerdict` |
| Encoded DO/GET/LIKE batches | `TestAst503`, `TestRunConsultTask` batch rows |
| `debug=False` unchanged | `TestRemainingConsultBranches::test_runs_without_debug_logging` |

**Betty test fix:** `enable_debug_log` fixture now uses `logger.set_debug_flag(True)` — product removed `_LOG_DEBUG` / `isEnabledFor` guards in favor of `debug_detail`.

— Betty

#### hedy — 2026-06-14T04:34:53.323Z
Plan doc: [ast-619-consult-claim-loop-and-grading-debug-instrumentation.md](https://github.com/susansomerset/astral/blob/sub/AST-543/AST-619-consult-claim-loop-grading-debug/docs/features/foundation/ast-619-consult-claim-loop-and-grading-debug-instrumentation.md)

Five stages: (1) `_consult_job_identifier` + grading helpers `_render_pass_fail` / `_render_score` → `debug_detail` branches; (2) `_run_batch_consult` per-job indices, missing-ID headers, batch-end detail, retire `[DEBUG]`; (3) `qualify_job_listings` / `evaluate_jd_batch` input + JD-readiness skips; (4) encoded consult prep skips + `render_verdict` / `_apply_render_verdict_decoded_job`; (5) manual UAT spot-checks.

**Self-Assessment**
- **Scope:** `Single-Component` — only `src/core/consult.py`; existing logging helpers, no new modules.
- **Conf:** `high` — AST-538 contract and sibling dispatcher backfill patterns; every current `[DEBUG]` / `_LOG_DEBUG` site mapped to explicit steps.
- **Risk:** `Medium` — consult batch/grading is production-critical; flag gating must stay strict so `debug=False` stays quiet.

---

# AST-619 — Consult claim, loop, and grading-path debug instrumentation (Debug logging backfill: consult)

- **Linear (this ticket):** [AST-619](https://linear.app/astralcareermatch/issue/AST-619/consult-claim-loop-and-grading-path-debug-instrumentation-debug)
- **Parent:** [AST-543](https://linear.app/astralcareermatch/issue/AST-543/debug-logging-backfill-consult)
- **Publish ref:** `origin/sub/AST-543/AST-619-consult-claim-loop-grading-debug` (child of AST-543; not Linear `gitBranchName`)
- **Depends on:** [AST-538](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging) / [AST-554](https://linear.app/astralcareermatch/issue/AST-554/debug-logging-contract-and-shared-helper) — shared helper + §1.5.1 on integration line; [AST-615](https://linear.app/astralcareermatch/issue/AST-615/dispatcher-claim-loop-and-guard-path-debug-instrumentation-debug) — dispatcher passes `debug` into `run_consult_task` (unchanged here).

## Summary

Backfill the **AST-538** debug logging contract across **consult** batch and grading paths in `src/core/consult.py`: Pattern-A batch scaffolding (`_run_batch_consult`), qualify/evaluate wrappers, encoded scored consult batches (`consult_do` / `consult_get` / `consult_like`), single-job `render_verdict`, and rubric grading helpers (`_render_pass_fail`, `_render_score`, `_apply_render_verdict_decoded_job`). Debug runs must show per-job index headers and `|` detail (inputs, grading branch, pass/fail reason) **before** batch summary lines — not only batch totals. Retire hand-rolled `logger.debug` / `logger.info("[DEBUG] …")` in touched consult blocks. **No** consult business logic, scoring math, or state-machine changes.

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Dispatcher, roster, agent, gazer, builder, external LLM modules | **AST-540**–**AST-546** (siblings) |
| `analysis_upshot`, job artifact entry batches, cover-letter batches | Agent/artifact hops — not grading-path consult |
| `run_consult_task` entity routing for company/board/candidate/gazer | Other modules own those paths |
| Betty log-string tests | Forbidden per parent |
| `src/data/` logging | Forbidden per Code Rules |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Contract debug across grading helpers, `_run_batch_consult`, qualify/evaluate, encoded consult batches, `render_verdict`; retire `[DEBUG]` and `_LOG_DEBUG` guards in touched blocks | core |

## Stage 1: Job identifier helper and grading-path contract (`_render_pass_fail`, `_render_score`)

**Done when:** With `logger.set_debug_flag(True)` (set by callers in later stages), `_render_pass_fail` and `_render_score` emit `|` detail naming the branch taken (empty grades, F2+, all X, low confidence, pass, scored fail, threshold pass/fail); with flag unset, **no** new lines from these helpers; all `logger.isEnabledFor(_LOG_DEBUG)` blocks in these two functions removed.

1. After `logger = get_logger(__name__)` (~line 42), add:

```python
def _consult_job_identifier(job: Dict[str, Any]) -> str:
    """Primary debug identifier for a consult job row (§1.5.1 style D)."""
    return str(job.get("astral_job_id") or job.get("job_title") or "?")
```

2. In `_render_pass_fail`, **remove** the import usage of `_LOG_DEBUG` and every `if logger.isEnabledFor(_LOG_DEBUG): logger.debug(...)` block. Replace each branch with **one** `logger.debug_detail(...)` at the point of decision:

   - Empty `grades`: `logger.debug_detail(f"pass_fail task_key={task_key} branch=empty_grades -> fail")`
   - F2+ dealbreaker: `logger.debug_detail(f"pass_fail task_key={task_key} branch=F2_dealbreaker -> fail grades={grades!r}")`
   - All literal X: `logger.debug_detail(f"pass_fail task_key={task_key} branch=all_literal_X -> fail")`
   - No confidence > 1: `logger.debug_detail(f"pass_fail task_key={task_key} branch=no_confidence_gt_1 -> fail grades={grades!r}")`
   - Pass: `logger.debug_detail(f"pass_fail task_key={task_key} branch=pass -> {cfg['pass_state']}")`

3. In `_render_score`, **remove** all `logger.isEnabledFor(_LOG_DEBUG)` blocks. Replace with `logger.debug_detail(...)`:

   - F2+ instant fail (before return): `branch=F2_dealbreaker scored_fail`
   - Per counted vector loop (~481): keep one detail line per vector: `vec=… grade=… conf=… base=… density=… imp=… contrib=…`
   - After score computed (~493): `rubric_score=… score=… threshold=… v=…`
   - Before each return: `branch=below_threshold -> fail` or `branch=pass -> {pass_state}` with `score=` and `threshold=`

4. **Do not** add a `debug: bool` parameter to `_render_pass_fail` / `_render_score`. Callers set `logger.set_debug_flag(True)` once per debug batch/single-job entry (Stage 2–4).

5. Remove `from logging import DEBUG as _LOG_DEBUG` (~line 17) when grep confirms zero remaining uses in `consult.py`.

⚠️ **Decision:** Grading helpers rely on module-level `logger.set_debug_flag` set by batch entry points — avoids threading `debug` through every internal call while keeping §1.5.1 gating (`debug_detail` no-ops when flag is False).

## Stage 2: `_run_batch_consult` — batch loop, per-job indices, batch end

**Done when:** AC 1 satisfied on Pattern-A consult batches: with `debug=True`, batch start context, per-response-job index headers + detail (outcome, grading path via process_fn), missing/fabricated ID detail, token summary, and batch-end summary appear **in that order**; all `logger.info("[DEBUG] …")` lines in `_run_batch_consult` removed; with `debug=False`, no new contract lines.

1. At `_run_batch_consult` entry (~881), immediately after `cfg = _consult_orchestration(task_key)`:

```python
if debug:
    logger.set_debug_flag(True)
    job_total = len(jobs)
    logger.debug_index(
        func=f"consult._run_batch_consult({task_key})",
        index=1,
        total=1,
        identifier=task_key,
        outcome=f"batch start n={job_total}",
    )
    logger.debug_detail(
        f"batch_id={batch_id} input_state={input_state!r} "
        f"batch_chunk_index={batch_chunk_index!r} astral_ids={astral_ids}"
    )
```

   Move `astral_ids = [...]` above this block if needed so the name exists (currently ~882 — reorder: compute `astral_ids`, `input_by_id`, `input_state`, `retry_state`, `error_state` first, then debug batch header).

2. **Envelope failure** (~905–909): before `return`, when `debug`:

```python
logger.debug_index(
    func=f"consult._run_batch_consult({task_key})",
    index=1,
    total=1,
    identifier=task_key,
    outcome="do_task failed — batch error transition",
)
logger.debug_detail(f"error={result.get('error')!r} error_state={error_state!r}")
```

3. **Replace** the block at ~928–930:

```python
if debug:
    ts = result.get("timesheet", {})
    logger.info(f"[DEBUG] {task_key}: got {len(response_jobs)} job objects back | tokens: ...")
```

   with:

```python
if debug:
    ts = result.get("timesheet", {})
    logger.debug_detail(
        f"do_task returned jobs={len(response_jobs)} "
        f"tokens input={ts.get('inputtotal')} cached={ts.get('inputcached')} output={ts.get('outputtotal')}"
    )
```

4. **Replace** ~946–950 missing/fabricated `[DEBUG]` logger.info lines with `logger.debug_detail(...)` (same facts: counts + sorted id lists).

5. **Per-job processing loop** (~955–969): replace the bare loop with indexed iteration. After `to_state = process_fn(...)` succeeds (inside `try`, after line assigning `to_state`):

```python
if debug:
    job_idx = sum(1 for rj in response_jobs[: response_jobs.index(response_job) + 1] if rj["astral_job_id"] not in fabricated)
    # Prefer enumerate: `for job_idx, response_job in enumerate(response_jobs, start=1):` and skip fabricated before index emit
```

   Use `for job_idx, response_job in enumerate(response_jobs, start=1):` with `continue` on fabricated **before** index emit. After successful `process_fn`:

```python
if debug:
    logger.debug_index(
        func=f"consult._run_batch_consult({task_key})",
        index=job_idx,
        total=len(response_jobs),
        identifier=_consult_job_identifier(input_job),
        outcome=str(to_state),
    )
    logger.debug_detail(
        f"astral_job_id={aid} pass_state={cfg['pass_state']!r} fail_state={cfg['fail_state']!r} "
        f"grades={response_job.get('grades')!r}"
    )
```

   On `process_fn` exception (~962–965), when `debug`, emit index with `outcome="process_fn failed"` and `debug_detail` with `{e}` and grades **before** `continue`.

6. **Missing IDs** (after loop, ~937–945): when `debug` and `missing`, for each `mid` in sorted(missing):

```python
logger.debug_index(
    func=f"consult._run_batch_consult({task_key})",
    index=mi,
    total=len(missing),
    identifier=mid,
    outcome=f"missing from response -> {dest or input_state}",
)
```

   Use `enumerate(sorted(missing), start=1)` for `mi`.

7. **Batch end** (~999–1000): **replace** `logger.info(f"[DEBUG] {task_key}: processed=…")` with:

```python
if debug:
    logger.debug_detail(
        f"batch end processed={len(jobs)} passed={passed} failed={failed} "
        f"bad_grades={len(bad_grades)} missing={len(missing)} fabricated={len(fabricated)}"
    )
```

   This line must remain **after** all per-job and missing-id headers (AC 1 / §1.5.1 batch-end rule).

8. Keep existing `logger.warning` / `logger.error` production lines unchanged.

## Stage 3: `qualify_job_listings` and `evaluate_jd_batch`

**Done when:** Qualify and evaluate debug runs show input-job context before `do_task`, JD-readiness skips as index headers, and per-job grading detail flows through Stage 2 loop; all `[DEBUG] ==========` banner lines removed; legacy per-job `logger.info(f"  {title} -> …")` lines gated with `if not debug:` so debug runs use contract only (no duplicate traces).

1. **`qualify_job_listings`** (~1037–1043): **delete** the START banner and per-job `[DEBUG]` listing loop. When `debug` at wrapper entry (before `_run_batch_consult`):

```python
if debug:
    logger.set_debug_flag(True)
    logger.debug_detail(f"qualify_job_listings batch_id={batch_id} job_count={len(jobs)}")
    for ji, j in enumerate(jobs, start=1):
        listing_len = len(j.get("job_data", {}).get("raw_job_listing", "") or "")
        logger.debug_index(
            func="consult.qualify_job_listings",
            index=ji,
            total=len(jobs),
            identifier=_consult_job_identifier(j),
            outcome="input job",
        )
        logger.debug_detail(
            f"title={j.get('job_title', 'UNKNOWN TITLE')!r} listing_chars={listing_len} "
            f"link={j.get('job_link', 'NO LINK')!r}"
        )
    total_chars = sum(len(j.get("job_data", {}).get("raw_job_listing", "") or "") for j in jobs)
    logger.debug_detail(f"total_listing_chars≈{total_chars}")
```

2. In `qualify_job_listings` `process()` (~1070–1093): wrap each `logger.info(f"  {…} -> …")` with `if not debug:` so contract lines from Stage 2 + `_render_pass_fail` detail are the debug trace. When `debug` and branch-specific detail is useful **before** `_render_pass_fail` returns, add `debug_detail` for title-too-short and relative-link skips inside those branches.

3. **Delete** END banner ~1098–1099.

4. **`evaluate_jd_batch`** (~1125–1126, 1206–1207): delete START/END `[DEBUG]` banners.

5. In `evaluate_jd_batch`, when `debug` after splitting ready/not_ready (~1128–1134):

```python
if debug:
    logger.set_debug_flag(True)
    logger.debug_detail(
        f"evaluate_jd batch_id={batch_id} ready={len(ready_jobs)} not_ready={len(not_ready_jobs)} min_chars={min_chars}"
    )
```

6. For each `not_ready_jobs` transition (~1136–1148), when `debug`:

```python
logger.debug_index(
    func="consult.evaluate_jd_batch",
    index=ni,
    total=len(not_ready_jobs),
    identifier=_consult_job_identifier(job),
    outcome=f"jd readiness skip -> {not_ready_state}",
)
logger.debug_detail(f"jd_chars={len(jd)} min_chars={min_chars}")
```

   Use `enumerate(not_ready_jobs, start=1)` for `ni`. Gate existing `logger.info("  %s -> %s [jd readiness skip]", …)` with `if not debug:`.

7. In `evaluate_jd_batch` `process()` (~1187–1191): gate `logger.info(f"  {title} -> …")` with `if not debug:` (same pattern as qualify).

8. Early return when `not ready_jobs` (~1150–1157): when `debug`, emit one `debug_detail(f"evaluate_jd batch_id={batch_id} all jobs not JD-ready skipped={len(not_ready_jobs)}")` before return.

## Stage 4: Encoded scored consult and single-job `render_verdict`

**Done when:** `_consult_scored_dispatch_batch_encoded` logs eligibility skips as contract indices; `render_verdict` / `_apply_render_verdict_decoded_job` emit single-job verdict context when `debug=True`; no new lines when `debug=False`.

1. **`_consult_scored_dispatch_batch_encoded`** (~1224): at function entry when `debug`:

```python
if debug:
    logger.set_debug_flag(True)
    logger.debug_detail(
        f"{dispatch_task_key} batch_id={batch_id} claimed={len(jobs)} agent_task={agent_tk}"
    )
```

2. Inside the eligibility loop (~1229–1252), when a job is skipped (`continue` paths for missing company or empty live_content), when `debug`:

```python
logger.debug_index(
    func=f"consult._consult_scored_dispatch_batch_encoded({dispatch_task_key})",
    index=skipped + 1,  # use running skip counter before increment, or enumerate skips separately
    total=len(jobs),
    identifier=aid,
    outcome="skipped — prep failed",
)
logger.debug_detail(f"reason={'no_company' if not company else 'no_live_content'} state={fresh.get('state')!r}")
```

   ⚠️ **Decision:** Use `total=len(jobs)` (claimed batch size) for skip indices so UAT can reconcile skips against dispatcher claim count; `index` is 1-based skip ordinal within the pass.

3. When `not eligible` (~1254–1255) and `debug`, `debug_detail(f"no eligible rows after prep skipped={skipped}")` before return.

4. **`render_verdict`** (~781): at entry after `cfg = _consult_orchestration(task_type)` when `debug`:

```python
if debug:
    logger.set_debug_flag(True)
    logger.debug_index(
        func="consult.render_verdict",
        index=1,
        total=1,
        identifier=astral_job_id,
        outcome="single-job consult start",
    )
    logger.debug_detail(f"task_type={task_type} agent_task={agent_task}")
```

5. On each early `_fail(...)` return (~797–814, 826–845, 854–859), when `debug`, emit `debug_detail(f"render_verdict failed: {error}")` **before** return (index header already emitted at start).

6. After successful `_apply_render_verdict_decoded_job` (~851–861), when `debug`:

```python
logger.debug_index(
    func="consult.render_verdict",
    index=1,
    total=1,
    identifier=astral_job_id,
    outcome=str(to_state),
)
logger.debug_detail(f"score={score} grades_count={len(grades_out or [])}")
```

7. **`_apply_render_verdict_decoded_job`** (~730): at entry when `logger._debug_flag` is True (flag set by caller), emit one `debug_detail` before grading:

```python
if logger._debug_flag:
    logger.debug_detail(
        f"apply_verdict dispatch_task_key={dispatch_task_key} mode={mode} "
        f"grades={grades!r}"
    )
```

   Use the public pattern: check debug by calling a small local — **prefer** `if debug` by adding optional `debug: bool = False` parameter to `_apply_render_verdict_decoded_job` only, default False, pass `debug=debug` from `render_verdict` and from `_consult_scored_dispatch_batch_encoded` `process()` closure (capture outer `debug`). When `debug`, call `logger.set_debug_flag(True)` at top of `_apply_render_verdict_decoded_job`.

   Updated signature:

```python
def _apply_render_verdict_decoded_job(
    dispatch_task_key: str,
    astral_job_id: str,
    response_job: Dict[str, Any],
    cfg: Dict[str, Any],
    ctx: Optional[Dict[str, Any]],
    debug: bool = False,
) -> Tuple[str, Optional[Any], List[Any]]:
```

   Update both call sites (`render_verdict`, `_consult_scored_dispatch_batch_encoded` `process`).

## Stage 5: Manual verification (build agent / Susan UAT)

**Done when:** Build agent documents spot-check notes in Linear comment or accepts parent AC without automated log tests.

1. **debug=False spot-check:** Run one `qualify_job_listings` and one `evaluate_jd` batch with `debug=False` — confirm **no** new contract headers (`index N/M` with ` -> `) and **no** new ` | ` detail lines from touched consult paths. Existing WARNING / non-debug INFO may still appear.

2. **debug=True qualify batch:** Run with ≥2 claimed jobs — confirm input-job indices appear, then per-response-job indices with grading `|` detail, then `batch end` detail.

3. **debug=True evaluate_jd:** Include at least one not-ready job — confirm readiness-skip index headers before ready-batch consult output.

4. **debug=True scored consult:** Run `consult_get` or `render_verdict` single-job with `debug=True` — confirm `_render_pass_fail` / `_render_score` branch detail in ` | ` lines.

(No new pytest files — parent forbids Betty log-string tests.)

## Self-Assessment

**Scope:** `Single-Component` — Only `src/core/consult.py` changes; instrumentation uses existing `src/utils/logging.py` helpers with no new modules.

**Conf:** `high` — AST-538/554/615 establish the contract and dispatcher→consult `debug` passthrough; this ticket maps known `[DEBUG]` and `_LOG_DEBUG` sites to explicit per-function steps.

**Risk:** `Medium` — Consult grading and batch transitions are production-critical; incorrect `set_debug_flag` or unguarded contract emission could add console noise when `debug=False` or omit traces during UAT.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.5.1 | Contract gated on `debug=True` via `set_debug_flag` + helpers; per-job indices before batch-end detail; retire `[DEBUG]` in touched blocks |
| §1.3 DRY | One `_consult_job_identifier` helper; reuse `debug_index` / `debug_detail` throughout |
| §2.1 config | No new config keys; reads existing orchestration only |
| §2.4 batch | Per-job indices inside existing batch loops; no claim/clear semantic changes |
| §2.6 state machine | No transition rules changed |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | `func=` strings use `consult.*` prefix consistently |
| §3.6 spikes | No spike output |

No conflicts requiring `conf-!!-NONE`.

## Execution contract

- Stages **1 → 5** in order; one `code()` commit per stage 1–4 on epic worktree, then publish to **`origin/sub/AST-543/AST-619-consult-claim-loop-grading-debug`**.
- Stage 5 is manual verification only — no commit unless product fix required.
- Blocking questions → parent **AST-543** with 🛑 format from **plan-child**.
- **Passthrough:** Do not modify `dispatcher.py`, `agent.py`, or `src/utils/logging.py` — helpers already exist on integration line.

## Review (build stub)

**Built:** `origin/sub/AST-543/AST-619-consult-claim-loop-grading-debug` @ `527feb98`.

**Stages delivered:**
- Stage 1: `_consult_job_identifier` + `_render_pass_fail` / `_render_score` contract detail; retire `_LOG_DEBUG` — `cac02ee1`.
- Stage 2: `_run_batch_consult` batch start, per-job indices, missing/fabricated detail, batch end — `929d6674`.
- Stage 3: `qualify_job_listings` / `evaluate_jd_batch` input context, JD-readiness skips, gated legacy INFO — `b84feb14`.
- Stage 4: `render_verdict`, `_apply_render_verdict_decoded_job`, `_consult_scored_dispatch_batch_encoded` — `527feb98`.

**Stage 5 (manual):** Susan UAT — `debug=False` spot-check; qualify/evaluate/scored consult with `debug=True`. No Betty log-string tests per parent.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-543/AST-619-consult-claim-loop-grading-debug` @ `ae0685ef`

### What's solid

| Area | Notes |
|------|--------|
| **§1.5.1 consult paths** | `_LOG_DEBUG` / hand-rolled `[DEBUG]` retired in `consult.py`; contract uses `set_debug_flag` + `debug_index` / `debug_detail`. |
| **Pattern-A batch** | `_run_batch_consult`: batch-start header, per-response-job indices (incl. `process_fn` failure), missing-ID indices, batch-end detail after per-job headers. |
| **Wrappers** | `qualify_job_listings` input-job indices; `evaluate_jd_batch` JD-readiness skip indices; legacy per-job `logger.info` gated with `if not debug:`. |
| **Scored / single-job** | `_consult_scored_dispatch_batch_encoded` skip indices; `render_verdict` start + outcome indices; `_apply_render_verdict_decoded_job(debug=…)`. |
| **Grading helpers** | `_render_pass_fail` / `_render_score` branch detail via `debug_detail` (no-op when flag unset). |
| **§2.4 / §2.6** | No claim/clear or transition rule changes observed in diff. |
| **§3.3** | No new cross-layer imports. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `src/core/agent.py` (whole file vs `origin/dev`, ~86 lines) | **§5d / plan execution contract:** ticket and plan forbid `agent.py` changes. Publish ref still diffs from `origin/dev`: drops `_resume_hop_debug_index`, resume-hop `debug_detail`, and legacy `[DEBUG]` blocks while retaining partial `_do_task_debug_*` from a sibling merge. **Revert `agent.py` to byte-match `origin/dev`** on this publish ref; agent instrumentation belongs to **AST-541 / AST-618**, not AST-619. |
| **discuss** | `_render_pass_fail` / `_render_score` inside `_run_batch_consult` `process_fn` | Grading `debug_detail` lines emit **before** the per-job `debug_index` for that response row (§1.5.1 prefers detail under index header). Accept branch-then-index for UAT, or reorder in resolve. |
| **discuss** | Batch entry points (`set_debug_flag(True)`) | No `set_debug_flag(False)` on exit; module logger may stay hot across back-to-back calls in one worker. Confirm `debug=False` spot-check includes a non-debug batch after a debug batch in-process. |

### Recommended actions (resolve-child)

1. **`git checkout origin/dev -- src/core/agent.py`** (or equivalent) on epic worktree; republish — **zero** `agent.py` diff vs `origin/dev`.
2. Optional: reorder grading detail vs per-job index if Susan wants strict §1.5.1 header-first ordering.
3. Stage 5 manual UAT per plan (debug=True qualify/evaluate/scored; debug=False spot-check).

## Resolution (resolve-child)

**Date:** 2026-06-14 · **Publish after resolve:** `origin/sub/AST-543/AST-619-consult-claim-loop-grading-debug`

| Radia item | Action |
| --- | --- |
| **fix-now** — `agent.py` out of scope | Reverted to byte-match **`origin/dev`** (removed accidental `test(AST-619)` partial AST-618 merge from publish ref). Zero `agent.py` diff vs dev. |
| **discuss** — grading detail before per-job index | **No change** — branch-then-index acceptable for UAT per Radia review; strict header-first reorder deferred unless Susan asks. |
| **discuss** — sticky `set_debug_flag` | **No change** — Stage 5 spot-check should run `debug=False` batch after `debug=True` in same worker; documented here for UAT. |

**§9a:** publish ref dry-run merge into `origin/dev` and `origin/ftr/ast-543-debug-logging-backfill-consult` verified clean before **User Testing**.
