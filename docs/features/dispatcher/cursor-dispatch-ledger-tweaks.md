# Cursor — dispatch ledger envelope + live cost from timesheets

- **Branch:** `cursor-dispatch-ledger-tweaks` (laptop / Cursor; base `origin/dev`)
- **Linear:** none yet — ad-hoc Susan + Cursor integration checkout
- **Status:** **plan only — nothing implemented.** Verified against `origin/dev` @ `c58774be6` (2026-10-16): no `agent_envelope` anywhere, no `refresh_ledger_batch_cost`, and no commit in any ref has ever added either.
- **Rebased onto AST-2215 (2026-10-16):** AST-2217 renamed `agent_timesheets` → **`service_timesheet`** and added ledger **`timesheet_state`** (`NEW` → `FETCHING` → `RECEIPTED`); AST-2218 **retired the background platform reconcile** — vendor cost now lands only via `run_fetch_timesheet` → `_apply_receipt`. Names and hook points below are updated to match. **Stage 2 re-anchored (2026-10-16):** the original text assumed the envelope was available at the post-`_send_to_server` ledger write; it is not (see Stage 2 anchors + Open question).
- **Goal:** Finish the ledger’s role as the **batch audit row**: persist the agent **envelope** on `dispatch_ledger`, and keep **`total_cost` / `entity_cost`** in sync with **`service_timesheet`** whenever a row is inserted or a receipt applies its platform cost.

## Problem (as-built vs intent)

| Expectation | Today |
|-------------|--------|
| Full `{ agent_performance, agent_payload }` envelope visible from Execution History’s ledger row | Envelope lives in **`agent_data`** RESPONSE blocks (when stored); ledger columns `agent_performance` / `agent_note` / `prompt_blocks` are **never written** |
| Ledger cost tracks children in **`service_timesheet`** (`batch_id` join) | Cost set at **batch close** (`_persist_dispatch_ledger_close` / hop finalize). After that, the only refresh is `_refresh_closed_ledger_totals` in `run_fetch_timesheet` (once, when every row of the batch is receipted), and it **returns early unless `completed_at` is set**. No refresh happens on timesheet insert, so RUNNING rows show zero cost until close |
| Parent/child by `batch_id` | **Logical 1:N** already (`dispatch_ledger.batch_id` ↔ `service_timesheet.batch_id`); no FK |

AST-330 planned ledger **`prompt_blocks`** refs and perf summary; AST-1960 / AST-2008 added **host** and **last-call LLM telemetry** on the same row. This ticket completes the **envelope + cost rollup** story without moving prompt bodies back onto the ledger (those stay in **`agent_data`**).

## Scope

### In scope

1. **`agent_envelope` column** on `dispatch_ledger` — JSON text of the standard two-key envelope (see **Decision E1**).
2. **`do_task`** writes envelope + existing call-outcome cols (`host`, `llm_call_seconds`, `llm_failure_class`) on the active `log_batch_id` row when an envelope exists or when we have a storable failure snapshot (see **Decision E2**).
3. **`refresh_ledger_batch_cost(batch_id)`** in core/timesheets — recompute `total_cost` / `entity_cost` from `sum_cost_by_batch` and current ledger `total_processed`; call after **every** timesheet insert (`record_timesheet_entry`) and after **every applied receipt** (`_apply_receipt`), for **RUNNING and closed** rows (see **Decision C1**).
4. Component tests for schema, envelope write, and cost refresh (engineer on this branch; Betty can fold into test-bible if this later lands via Linear).

### Out of scope (follow-ups)

- Execution History UI column / expander for envelope (API will already return the field via `SELECT *`).
- SQLite FK `service_timesheet.batch_id` → `dispatch_ledger.batch_id`.
- Backfill historical rows (DDL only; old rows stay NULL).
- Changing timesheet **`agent_performance`** (still status string + `failure_note`; not the full envelope).
- Multi-call **aggregation** of envelopes (see **Decision E3** — last call wins).

## Decisions (Susan-aligned)

**E1 — Column name `agent_envelope`.**  
Do not overload ledger `agent_performance TEXT` (name collides mentally with timesheet’s string status). New nullable `agent_envelope TEXT` holds `json.dumps({"agent_performance": …, "agent_payload": …})` with UTF-8 JSON (same shapes `do_task` already validates). Empty or non-envelope failures: leave NULL; `llm_failure_class` + agent_data RESPONSE still carry audit detail.

**E2 — Write envelope from `do_task` only.**  
Provider probe rows (`get_batch_host` → `_record_probe`) record timesheets but never produce an envelope — no envelope write. The host / `llm_*` write stays where it is (right after `_send_to_server`, before parsing); the envelope is written by a **second** `update_dispatch_ledger` once the response has been parsed — the envelope does not exist at the first write.

**E3 — Shared ledger row: last call wins (envelope).**  
Same rule as AST-2008 for `llm_call_seconds` / `llm_failure_class`: multi-entity dispatch loops and multiple LLM calls on one `batch_id` **overwrite** `agent_envelope` each time so the column always matches the **same call** as the latest LLM telemetry. No array merge on the ledger row.

**E4 — Validation failure.**  
Capture the raw envelope dict **before** validation and the `agent_payload` unwrap. If validation then fails, the captured dict is what gets stored (so Susan can see what the model returned). If only raw text exists, envelope stays NULL (RESPONSE block in agent_data unchanged).

**E5 — `structured=True` graders (AST-2172) have no envelope.**  
Structured-output calls skip the envelope entirely (`not structured` guards in `do_task`). `agent_envelope` stays NULL for them by design; their audit detail is the structured response in `agent_data`.

**C1 — Refresh cost whenever timesheets change.**  
Replace the “closed only” guard in `_refresh_closed_ledger_totals` (AST-2218) with **`refresh_ledger_batch_cost(batch_id)`**:
- If `get_dispatch_ledger(batch_id)` is missing → no-op (adhoc/probe/orphan ids).
- Else `total_cost = sum_cost_by_batch([batch_id]).get(batch_id, 0.0)`, `entity_cost = total_cost / total_processed` when `total_processed > 0`, else `total_cost`.
- Invoke from `record_timesheet_entry` after `_add_timesheet_entry` (live calc cost on RUNNING rows), and from `_apply_receipt` after `update_timesheet_platform` (vendor `platform_cost` replaces calc cost per row in `sum_cost_by_batch`). Hook in `core/timesheets.py`, not in the `database.py` primitive. Keep the `run_fetch_timesheet` end-of-batch call, now pointing at the shared helper.
- Receipt cost can arrive **after** the ledger closed (`timesheet_state` NEW → RECEIPTED); the refresh must therefore be allowed on closed rows — that is the case the old guard was written for. Cost refresh does **not** touch `timesheet_state` (that stays owned by the claim/receipt flow).

**C2 — Do not double-close semantics.**  
Mid-run `_run_dispatch_loop` count updates stay as today; cost refresh is independent and safe on RUNNING rows (Execution History live refresh).

## Files changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `agent_envelope TEXT` on CREATE + migrations (after `llm_failure_class`, before `timesheet_state`); `_LEDGER_UPDATE_COLS += "agent_envelope"`; module docstring | data |
| `src/core/agent.py` | Add `_ledger_envelope_json`; capture the raw envelope after parse and before unwrap/validation; write `agent_envelope` in a second ledger update (success and validation-failure exits) | core |
| `src/core/timesheets.py` | Add `refresh_ledger_batch_cost`; call from `record_timesheet_entry` + `_apply_receipt`; replace `_refresh_closed_ledger_totals` body (or delete it and call the shared helper from `run_fetch_timesheet`) | core |
| `tests/component/data/database/test_dispatch_ledger.py` | Column + update whitelist | tests |
| `tests/component/core/test_agent.py` | Envelope on ledger under `log_batch_id`; last-call-wins if cheap to extend existing AST-2008 class | tests |
| `tests/component/core/test_timesheets.py` | Insert timesheet → RUNNING ledger cost updates; `_apply_receipt` → cost updates (RUNNING and closed); existing AST-2218 `run_fetch_timesheet` tests still green | tests |

Readers (`get_dispatch_ledger`, `list_dispatch_ledger`): **no code change** (`SELECT *`).

## Stage 1: `agent_envelope` column

**Done when:** Fresh DB and legacy table without column both accept `update_dispatch_ledger(batch_id, agent_envelope='{"agent_performance":{},"agent_payload":null}')`; unknown keys still raise.

1. `_ensure_dispatch_ledger_schema`: add `agent_envelope TEXT` to CREATE (after `llm_failure_class`) and to `migrations` list with comment `# cursor-dispatch-ledger-tweaks: full agent envelope JSON`.
2. `_LEDGER_UPDATE_COLS`: add `"agent_envelope"`.
3. Module docstring: note envelope on ledger row.
4. Verify: `python3 -m py_compile src/data/database.py` + temp-DB snippet (mirror AST-1960 verify style).

**Commit:** `code: dispatch ledger — agent_envelope column`

## Stage 2: Persist envelope from `do_task`

**Anchors on dev (verified 2026-10-16 @ `c58774be6`):**
- The AST-2008 / AST-1960 ledger write (`agent.py` ~2183–2210, immediately after `_send_to_server`) runs **before** any parsing; `parsed` is first assigned at ~2270. The envelope cannot be added to that `cols` dict.
- `envelope_snapshot` (~2277) is taken only for **vector-feedback consumer tasks** (`is_vector_feedback_task`), not for every enveloped task. For other tasks the raw `result["parsed_response"]` is all there is until the unwrap at ~2380 (`parsed = parsed["agent_payload"]`).
- Envelope validation (`{agent_performance, agent_payload}`) is the function at ~1463.
- `structured=True` graders (AST-2172) carry no envelope → NULL by design (E5).

**Open question for Susan (decide before building):** capture the raw envelope for **every** enveloped task (deepcopy `result["parsed_response"]` right after ~2270, before normalization/validation), or **only vector-feedback tasks** (reuse the existing `envelope_snapshot`, smaller change)? Plan below assumes **every enveloped task**; the vector-only variant just swaps the capture line.

**Done when:** Under `log_batch_id` with a saved ledger row, a `do_task` call whose response is an envelope leaves `get_dispatch_ledger(id)["agent_envelope"]` as JSON with both keys; a provider failure leaves it NULL (may still set `llm_failure_class`); a validation failure stores the raw captured dict; a `structured=True` call leaves it NULL.

1. Add helper `_ledger_envelope_json(parsed: Any) -> Optional[str]` in `agent.py`:
   - Input must be a `dict` with both `agent_performance` and `agent_payload` keys present (payload may be null); else `None`.
   - `json.dumps(..., separators=(",", ":"), default=str)` — compact; no truncation.
2. Right after `parsed = result.get("parsed_response")` (~2270): `raw_envelope = copy.deepcopy(parsed)` when not `structured` and it is a dict (before normalization / validation / unwrap).
3. Write it with a **second** `update_dispatch_ledger(ledger_batch_id, agent_envelope=...)` — only when `log_batch_id` is set and the helper returns non-None. Same try/except shape as the AST-2008 write (a ledger hiccup must never change the call outcome; off-loop via `asyncio.to_thread`). Place it once, after the validation step on both the success and validation-failure exits, rather than at each early return.
4. Provider failure (no parse): nothing written. **Hop finalize** (`_finalize_run_next_hop_ledger`): no envelope duplication — the hop row already got per-call writes during `do_task`.

**Verify:** `pytest tests/component/core/test_agent.py -k 'Ast1960 or Ast2008 or envelope' -q` (extend tests as needed).

**Commit:** `code: persist agent envelope on dispatch_ledger from do_task`

## Stage 3: Live ledger cost from timesheets

**Done when:** Saving a ledger row RUNNING, inserting a `service_timesheet` row with that `batch_id` via `record_timesheet_entry` updates `total_cost` / `entity_cost` without waiting for dispatch close; applying a receipt (`_apply_receipt`) updates the same fields for RUNNING and COMPLETED rows.

1. In `timesheets.py`, implement:

```python
def refresh_ledger_batch_cost(batch_id: Optional[str]) -> None:
    bid = str(batch_id or "").strip()
    if not bid:
        return
    ledger = get_dispatch_ledger(bid)
    if not ledger:
        return
    total_cost = sum_cost_by_batch([bid]).get(bid, 0.0)
    n = int(ledger.get("total_processed") or 0)
    entity_cost = round(total_cost / n, 7) if n > 0 else round(total_cost, 7)
    update_dispatch_ledger(bid, total_cost=total_cost, entity_cost=entity_cost)
```

   - Never raise to callers; log exception on failure (same pattern as ledger host write).

2. `record_timesheet_entry`: after `_add_timesheet_entry`, call `refresh_ledger_batch_cost(kwargs.get("batch_id"))`. (`record_search_timesheet_entry` goes through it, so search rows are covered.)

3. `_apply_receipt`: after `update_timesheet_platform`, look up the row's `batch_id` and call `refresh_ledger_batch_cost`. (`_apply_receipt` receives only `agent_req_id` + receipt — fetch `batch_id` from the row the caller already holds in `run_fetch_timesheet`, or pass it in; decide at implement time, prefer passing it in.)

4. Replace body of `_refresh_closed_ledger_totals` with `refresh_ledger_batch_cost(batch_id)` (delete `completed_at` guard) and keep its call after `set_ledger_timesheet_state(..., "RECEIPTED")`.

5. Confirm `_persist_dispatch_ledger_close` still calls `compute_batch_cost` at close — idempotent with refresh; keep close path so counts + status + cost land atomically at end even if refresh missed.

**Verify:** `pytest tests/component/core/test_timesheets.py tests/component/data/database/test_dispatch_ledger.py -q`

**Commit:** `code: refresh dispatch_ledger cost on timesheet insert and receipt apply`

## Stage 4: Regression pass

**Done when:** Targeted component suites green; no edits to `dispatcher.py` required unless a test proves mid-run cost drift (expected: RUNNING rows show non-zero cost after first LLM call).

```bash
python3 -m py_compile src/data/database.py src/core/agent.py src/core/timesheets.py
python3 -m pytest tests/component/data/database/test_dispatch_ledger.py \
  tests/component/core/test_timesheets.py \
  tests/component/core/test_agent.py -k 'ledger or timesheet or Ast1960 or Ast2008 or Ast2218' -q
```

**Commit (if test-only delta):** `test: dispatch ledger envelope and live cost`

## Test plan (UAT)

1. **Workbench Test** (single batch): run adhoc test → Execution History row shows non-zero cost while RUNNING if inspect DB/API; after complete, `agent_envelope` parses with perf + payload; Agent Timesheets (`service_timesheet`) filter by `batch_id` shows one child row; ledger `total_cost` equals sum of child row(s) (platform or calc).
2. **Dispatch multi-entity** (e.g. consult batch): one outer ledger, N timesheet rows — ledger `total_cost` increases after each call without waiting for batch end; `agent_envelope` reflects **last** entity’s call.
3. **OpenRouter receipt:** after `fetch_timesheet` runs for the candidate (ledger `timesheet_state` NEW → RECEIPTED), ledger `total_cost` switches to the vendor `platform_cost` sum (RUNNING or after close). No background reconcile exists any more — if `fetch_timesheet` hasn't run, cost stays at the calc value.

## Risks / notes

- **Large payloads:** `agent_payload` for big consult responses can make `agent_envelope` large — acceptable for SQLite TEXT; if size becomes an issue, follow-up could store envelope perf-only on ledger and keep payload in agent_data only.
- **`INSERT OR IGNORE` timesheets:** duplicate `agent_req_id` does not change sums — refresh is harmless.
- **Possible overlap with AST-2215/2217:** those tickets own `timesheet_state` and the receipt queue. This plan only adds cost writes alongside them; if the receipt flow is reworked, re-check the `_apply_receipt` hook.
- **No ledger row:** craft paths with `run_next` only hop ledgers — timesheet `batch_id` is hop id; refresh no-ops if row missing (should not happen when `log_batch_id` set correctly).

## For Betty (if promoted to Linear)

Primary manifest suggestion: `docs/test-bible/data/database/dispatch_ledger.md` + pointers in `docs/test-bible/core/agent.md` and `docs/test-bible/core/timesheets.md`. Integration tier: none.
