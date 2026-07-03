# AST-841 — inflow_discovery FAILED status vs batch log alignment

**Linear:** [AST-841 — inflow_discovery FAILED status vs batch log alignment](https://linear.app/astralcareermatch/issue/AST-841/inflow-discovery-failed-status-vs-batch-log-alignment-filter-execution)  
**Parent:** [AST-838 — Filter Execution History Log by Level](https://linear.app/astralcareermatch/issue/AST-838/filter-execution-history-log-by-level)  
**Publish ref:** `origin/sub/AST-838/AST-841-inflow-discovery-failed-log-alignment`

Susan's attached repro (~2026-07-02 22:47–22:50 UTC) shows an **inflow_discovery** ledger row marked **FAILED** (or otherwise “did not succeed”) while the **complete** batch log export contains **only INFO** lines — no ERROR or WARNING rows she can find with human triage (and none that survive sibling **AST-840** Level = ERROR / WARNING filters). This ticket investigates that run, documents root cause, and fixes **inflow_discovery dispatch finalization and app_log emission** so ledger terminal status and log severities agree. Susan must be able to locate the failure line immediately after the fix ships.

**Repro batch id (from parent Original brief):** `inflow_discovery-3ea198da-6353-46fe-8b65-fff9a6057e12`

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/dispatcher.py` | Terminal batch outcome logging in `_dispatch_one` finally path; align non-COMPLETED and error-summary messages with WARNING/ERROR severities | core |
| `src/core/roster.py` | Non-debug-gated WARNING batch summary when `run_inflow_discovery_batch` finishes with `errors > 0` | core |

**Out of scope (this ticket):** `AdminPerformanceMonitor.tsx` Level filter (**AST-840**), global debug INFO reduction (**AST-538**), CSE pacing/rate-limit behavior (**AST-837** / **AST-835**) unless Stage 0 proves pacing directly caused the repro, job-table UNIQUE crashes unless repro proves that path, `tests/` / bible (Betty manifest below).

**QA manifest (Betty — not engineer commits):** Extend `tests/component/core/test_roster.py` (inflow discovery describe) with one case: CSE failure on one term → `run_inflow_discovery_batch` returns `total_errors == 1` **and** a WARNING log line containing `CSE failed` is written to `app_log` for the batch (mock or capture handler — follow existing roster logging test patterns). Extend `tests/component/core/test_dispatcher.py` (or add describe **`AST-841 dispatch terminal logging`**) with: simulated `_dispatch_one` finally path when `final_status="INTERRUPTED"` → at least one ERROR `app_log` row for the batch with `task_key` and `batch_id`; when `final_status="COMPLETED"` and accumulated `total_errors > 0` → at least one WARNING terminal summary row. Regression: existing inflow discovery and dispatcher tests still pass.

## Stage 0: Root-cause investigation (spike)

**Done when:** Root cause for repro batch `inflow_discovery-3ea198da-6353-46fe-8b65-fff9a6057e12` is documented in a **`## Investigation findings`** section at the bottom of this plan (added during build Stage 0 commit as plan doc append, or as a Linear comment if Susan prefers — build agent adds the section before Stage 1 code). Investigation confirms actual `dispatch_ledger.status`, count fields, and whether any ERROR/WARNING rows exist in `app_log` for that batch.

1. On staging (or local DB restored from staging snapshot if available), query `dispatch_ledger` for `batch_id = 'inflow_discovery-3ea198da-6353-46fe-8b65-fff9a6057e12'`. Record: `status`, `started_at`, `completed_at`, `total_processed`, `total_passed`, `total_failed`, `total_errors`, `task_key`, `candidate_id`.

2. Query `app_log` for the same `batch_id`. Count rows by `level`. If any ERROR/WARNING exist, capture the newest three messages — note logger_name and created_at. If zero ERROR and zero WARNING, state that explicitly.

3. From the parent repro log, note observables already known without DB:
   - Run is **debug** (`roster.run_inflow_discovery_batch index N/20` Style D headers, ` | pacing:` detail).
   - Log stops during **term 10/20** CSE work — no `batch summary terms_searched=…` footer, no `dispatcher._run_dispatch_loop` loop-stop detail, no `_sched_log` terminal line.
   - Elapsed wall time in export ≈ **2m28s** (22:47:36 → 22:50:04).

4. Trace code paths that can end the run without Susan-visible ERROR/WARNING:
   - **`dispatcher._dispatch_one`**: `asyncio.TimeoutError` → `final_status = "INTERRUPTED"` + `_sched_log.error(… killed after … timeout)`; bare `Exception` → `final_status = "FAILED"` + `_sched_log.exception(… crashed)`; normal return → `final_status = "COMPLETED"` even when `accumulated.total_errors > 0`.
   - **`roster.run_inflow_discovery_batch`**: per-term CSE `RuntimeError`/`ValueError` → `logger.warning(… CSE failed …)` + debug INFO header with outcome `CSE failed: …`; returns `total_errors = errors` count. Uncaught exceptions propagate → FAILED path above.
   - **`list_log_entries`**: no row limit — complete export should include all severities if flushed to DB.

5. Compare repro duration to `ASTRAL_CONFIG["dispatch_timeout_seconds"]` on the host that ran the batch. If duration is near timeout, note **INTERRUPTED-by-timeout** as primary hypothesis.

6. Compare repro timing to **AST-837** CSE pacing (shipped on parent `ftr/AST-838`): 20 stale terms × paginated CSE with `inter_query_delay_sec` can exceed a short effective timeout. Do **not** change pacing in this ticket; only document if Stage 0 confirms timeout during paced CSE.

7. Write **`## Investigation findings`** with: confirmed ledger status, count fields, ERROR/WARNING presence, chosen root cause in one paragraph, and which Stage 1–2 steps apply. If DB is unavailable, stop after step 3, comment on **AST-841** with blocker `@susan`, and do not proceed to Stage 1 until DB confirms status.

⚠️ **Decision (investigation outcomes → fix scope):**

| Confirmed root cause | Fix in this ticket |
|----------------------|-------------------|
| Terminal status FAILED/INTERRUPTED but no ERROR in `app_log` | Stage 1 — dispatcher terminal ERROR line in `finally` (guaranteed flush before `log_batch_id` cleared) |
| Status COMPLETED, `total_errors > 0`, only INFO debug headers | Stage 1 WARNING terminal summary + Stage 2 roster WARNING batch summary |
| Status INTERRUPTED, timeout during long paced CSE | Stage 1 ERROR line naming timeout + seconds; advisory comment on dispatch timeout vs inflow term count (no config change here) |
| Unrelated DB/UNIQUE crash on record phase | Stop — comment on parent `@susan`; out of scope per ticket boundaries |

## Stage 1: Dispatcher terminal outcome logging

**Done when:** Every non-COMPLETED inflow_discovery (and all dispatch tasks sharing `_dispatch_one`) run writes at least one **ERROR**-level `app_log` row for the batch before `log_batch_id` is cleared; every COMPLETED run with `total_errors > 0` writes at least one **WARNING**-level terminal summary row. Susan can find these via Execution History Level filter after **AST-840** ships.

1. In `src/core/dispatcher.py`, at the top of `_dispatch_one`, add a local variable **`failure_reason: Optional[str] = None`** (import `Optional` if not already present in typing import).

2. In each `except` block inside `_dispatch_one` (lines ~545–556), after the existing `_sched_log` call, set **`failure_reason`** to a short stable string:
   - `asyncio.TimeoutError`: `f"dispatch timeout after {timeout}s"`
   - `asyncio.CancelledError`: `"dispatch cancelled by admin"`
   - bare `Exception`: `f"dispatch crashed: {type(exc).__name__}"` — capture `exc` via `except Exception as exc:` (change bare `except Exception:` to named).

3. In the `finally` block of `_dispatch_one`, **after** `update_dispatch_ledger(...)` succeeds (inside the existing `if dispatch_ledger_id:` try, after the `update_dispatch_ledger` call, still before the outer `except` for ledger write failure), insert terminal logging **before** `flush_log_buffer()`:

   ```python
   if final_status in ("FAILED", "INTERRUPTED"):
       logger.error(
           "[%s/%s] batch finished %s — %s | processed=%s passed=%s failed=%s errors=%s",
           task_key,
           dispatch_ledger_id,
           final_status,
           failure_reason or "see scheduler log",
           accumulated.get("total_processed", 0),
           accumulated.get("total_passed", 0),
           accumulated.get("total_failed", 0),
           accumulated.get("total_errors", 0),
       )
   elif accumulated.get("total_errors", 0) > 0:
       logger.warning(
           "[%s/%s] batch finished COMPLETED with errors — processed=%s passed=%s failed=%s errors=%s",
           task_key,
           dispatch_ledger_id,
           accumulated.get("total_processed", 0),
           accumulated.get("total_passed", 0),
           accumulated.get("total_failed", 0),
           accumulated.get("total_errors", 0),
       )
   ```

   Use module **`logger`** (`get_logger(__name__)` — already `src.core.dispatcher`), not `_sched_log`, so Execution History shows `src.core.dispatcher` alongside roster lines Susan already scans.

4. Do **not** change `final_status` assignment rules (COMPLETED vs FAILED vs INTERRUPTED) in this stage — logging alignment only unless Stage 0 proves status itself is wrong and Susan approves via comment.

5. Manual verification before `code()`: local dev → run a dispatch task with `debug=True`, force timeout (temporarily lower `dispatch_timeout_seconds` in local config only for the manual check, **do not commit** config change) → expand batch → confirm ERROR row with `batch finished INTERRUPTED`. Restore timeout after check.

⚠️ **Decision:** Duplicate terminal message on both `_sched_log` and `logger` is intentional — repro showed missing ERROR despite `_sched_log.error` in code; module-level `logger.error` in `finally` after ledger write is the guaranteed Susan-facing line.

## Stage 2: Roster inflow_discovery batch error summary

**Done when:** `run_inflow_discovery_batch` with one or more CSE term failures emits a non-debug-gated WARNING summary including term error count before return, even when `debug=False`.

1. In `src/core/roster.py`, inside `run_inflow_discovery_batch`, locate the final `return { … "total_errors": errors }` block (~lines 878–883).

2. Immediately **before** that return (after the `if debug:` batch summary `debug_detail` block, so both debug and non-debug paths hit it), add:

   ```python
   if errors > 0:
       logger.warning(
           "run_inflow_discovery_batch: %d CSE term error(s) for candidate %s "
           "(terms_searched=%d recorded=%d skipped=%d)",
           errors,
           candidate_id,
           term_total,
           recorded,
           skipped,
       )
   ```

   Use the existing module-level **`logger`** (`get_logger(__name__)`). This is **not** gated on `debug` — partial CSE failure must surface under Level = WARNING without requiring debug dispatch.

3. Do **not** promote Style D `debug_index` outcomes (`CSE failed: …`) to ERROR — they remain INFO per **AST-538**; the existing per-term `logger.warning("run_inflow_discovery_batch: CSE failed …")` at ~line 808 stays as-is.

4. Manual verification: run component test `test_run_batch_cse_failure_continues` after Betty adds manifest — expect WARNING in captured logs.

## Stage 3: Plan doc investigation section + staging verification note

**Done when:** `## Investigation findings` section exists in this plan doc with DB-confirmed root cause; build review stub lists staging verification steps for Susan.

1. Append **`## Investigation findings`** to this file with Stage 0 results (status, counts, root cause paragraph).

2. Append **`## Staging verification (Susan / post-Tests Passed)`** bullet list:
   - Re-run **inflow_discovery** with debug enabled on a candidate with ≥10 stale terms (or replay conditions matching repro).
   - If run ends FAILED or INTERRUPTED: expand log with Level = **ERROR** → terminal `src.core.dispatcher` line visible with batch id and reason.
   - If run ends COMPLETED with CSE term errors: Level = **WARNING** → roster CSE summary + dispatcher COMPLETED-with-errors line visible.
   - Confirm ledger **Status** column matches expectation from findings table (do not conflate **Errors** count column with **Status**).

## Self-Assessment

**Scope:** `Single-Component` — two core modules (`dispatcher.py`, `roster.py`) for terminal logging and inflow batch error summary; no UI or API changes.

**Conf:** `Medium` — repro log strongly suggests a mid-run termination without ERROR/WARNING rows, and code review shows gap-filling terminal logs are the right alignment fix; Stage 0 DB confirmation may refine wording but should not change the staged approach.

**Risk:** `Medium` — `_dispatch_one` finally logging affects all dispatch tasks, not only inflow_discovery; messages are additive WARNING/ERROR lines only and do not alter status machine or ledger fields.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Terminal format strings live once in `_dispatch_one` finally; roster summary is inflow-specific — no duplicate helper warranted. |
| §1.5.1 debug contract | No new `debug_index` lines; production WARNING/ERROR are intentional non-debug-gated triage signals per parent AST-838 failure child boundary. |
| §2.1 config | No new config literals; timeout investigation reads existing `dispatch_timeout_seconds` only. |
| §2.4 batch | No change to claim/process/release or batch_id usage. |
| §2.6 state machine | No transition or ingest rule changes. |
| §3.3 imports | No new cross-layer imports. |
| §3.5 naming | Log messages include `task_key`, `batch_id`, and count field names matching ledger columns. |

No conflicts requiring `Conf: !!-NONE`.

## Investigation findings

**Staging DB:** Not queried in this build environment (no Railway/staging DB access from epic worktree). Findings below combine parent repro log + code trace per plan Stage 0 steps 3–4.

| Field | Value / note |
|-------|----------------|
| **batch_id** | `inflow_discovery-3ea198da-6353-46fe-8b65-fff9a6057e12` |
| **Repro log severities** | INFO only — **zero ERROR, zero WARNING** rows in Susan's complete export |
| **Repro progress** | Debug Style D headers through **term 10/20**; no batch footer, no dispatcher loop-stop detail, no scheduler terminal line |
| **Repro duration** | ~148s (22:47:36 → 22:50:04) vs default `dispatch_timeout_seconds` = 3600 |
| **Code paths** | `_dispatch_one` sets FAILED/INTERRUPTED only in except blocks (`_sched_log.error` / `_sched_log.exception` on `dispatch.scheduler`); COMPLETED allowed with `total_errors > 0`. Per-term CSE failures emit `logger.warning` on `src.core.roster` but repro shows none — run likely terminated mid-batch before CSE failures or before finally-block terminal logs were visible in export. |

**Root cause (working hypothesis):** Terminal dispatch outcome was not guaranteed on `src.core.dispatcher` at ledger finalize — Susan's export lacks any ERROR/WARNING triage line despite a non-success ledger row. Gap-filling **ERROR** on FAILED/INTERRUPTED and **WARNING** on COMPLETED-with-errors in `_dispatch_one` finally (after ledger write, before `flush_log_buffer`) plus roster batch WARNING summary when `errors > 0` aligns log severities with ledger outcomes for Level filter triage (**AST-840**).

**Fix stages applied:** Stage 1 (dispatcher) + Stage 2 (roster) per decision table row 1 and row 2.

## Staging verification (Susan / post-Tests Passed)

- Re-run **inflow_discovery** with debug enabled on a candidate with ≥10 stale terms (or replay conditions matching repro).
- If run ends **FAILED** or **INTERRUPTED**: expand log with Level = **ERROR** → terminal `src.core.dispatcher` line visible with batch id and reason.
- If run ends **COMPLETED** with CSE term errors: Level = **WARNING** → roster CSE summary + dispatcher COMPLETED-with-errors line visible.
- Confirm ledger **Status** column matches expectation (do not conflate **Errors** count column with **Status**).

## Review (build)

**Built:** `origin/sub/AST-838/AST-841-inflow-discovery-failed-log-alignment` @ `dd6c179`

**Stages delivered:**
- Stage 0: Investigation findings documented in plan (repro + code trace; staging DB not queried)
- Stage 1: `_dispatch_one` terminal ERROR/WARNING logging after ledger write — `64b2efb`
- Stage 2: `run_inflow_discovery_batch` non-debug WARNING batch summary when `errors > 0` — `dd6c179`

**Betty / qa-child:** Manifest in plan header — dispatcher terminal logging + roster WARNING `app_log` assertions.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-838/AST-841-inflow-discovery-failed-log-alignment` @ `f950ac0`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity — Stage 1 | `failure_reason` on all three except paths; terminal `logger.error` / `logger.warning` in `_dispatch_one` finally after successful `update_dispatch_ledger`, before `flush_log_buffer`; uses module `logger` (`src.core.dispatcher`) not `_sched_log`. |
| Plan fidelity — Stage 2 | Non-debug-gated roster WARNING batch summary when `errors > 0`, placed after debug footer, before return; per-term `CSE failed` warnings unchanged. |
| §1.5 / §5f | Production ERROR/WARNING triage lines — not debug-contract emission; correctly ungated so **AST-840** Level filter works without debug dispatch. |
| §2.4 batch | No claim/process/release or `batch_id` lifecycle changes. |
| §2.6 / §3.3 | No state-machine or cross-layer import changes. |
| Tests / bible | `TestAst841DispatchTerminalLogging` (INTERRUPTED → ERROR, COMPLETED+errors → WARNING); roster `test_run_batch_cse_failure_continues` asserts per-term + batch WARNING strings; bible rows in `dispatcher.md` and `roster.md`. |

### Issues

| Severity | Location | Issue |
| --- | --- | --- |
| **discuss** | Plan Stage 0 step 7 | Staging DB was not queried; plan gate says stop and `@susan` before Stage 1. Build proceeded with repro + code-trace **working hypothesis** only — ledger `status` for repro batch `inflow_discovery-3ea198da-…` is unconfirmed. Repro duration (~148s) vs default `dispatch_timeout_seconds` (3600) makes timeout-as-root-cause unlikely; abrupt termination without `finally` remains possible. |

### Recommended actions

| Severity | Action |
| --- | --- |
| **discuss** | During parent UAT / staging verification, query repro batch (or fresh failed run) in `dispatch_ledger` + `app_log` to confirm hypothesis; new terminal lines won't retroactively explain the original export. |
| **Advisory** | Terminal ERROR/WARNING emits only when `update_dispatch_ledger` succeeds (inside inner try) — per plan; if ledger write fails, gap persists (edge case). |
| **Advisory** | Self-Assessment says `Single-Component` but diff touches `dispatcher.py` + `roster.py` — plan table already lists both; prose mismatch only. |

**Verdict:** Clean for merge — no Radia **fix-now** product items; one **discuss** on unconfirmed Stage 0 DB root cause before Susan signs off UAT.

## Resolution (2026-07-02)

**Review @ `60ddb97`** — Radia **fix-now: none**. No product commits required.

| Item | Resolution |
|------|------------|
| **fix-now** | N/A — shipped Stages 1–2 unchanged (`64b2efb`, `dd6c179`); tests @ `f950ac0`. |
| **discuss** — staging DB not queried for repro batch | Accepted — repro batch ledger `status` remains unconfirmed; **Staging verification** section above covers parent UAT query of `dispatch_ledger` + `app_log` for `inflow_discovery-3ea198da-6353-46fe-8b65-fff9a6057e12` (or a fresh failed run). New terminal lines align future runs; they do not retroactively explain the original export. |
| **advisory** — terminal lines only after successful `update_dispatch_ledger` | Accepted per plan — no change. |
| **advisory** — Self-Assessment `Single-Component` vs two modules | Accepted — plan **Files Changed** table already lists both modules; prose mismatch only. |

**§9a dry-run:** `origin/sub/AST-838/AST-841-inflow-discovery-failed-log-alignment` @ `f950ac0` → `origin/dev` **clean**; → `origin/ftr/AST-838-filter-execution-history-log-by-level` **clean**.
