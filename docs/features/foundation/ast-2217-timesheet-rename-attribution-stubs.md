# AST-2217 — Timesheet rename, call-time attribution and receipt stubs

- **Linear:** [AST-2217](https://linear.app/astralcareermatch/issue/AST-2217)
- **Parent:** [AST-2215](https://linear.app/astralcareermatch/issue/AST-2215) — Add task `fetch_timesheet`
- **Publish ref:** `sub/AST-2215/AST-2217-timesheet-rename-attribution-stubs`

Rename `agent_timesheets` → `service_timesheet` with call-time attribution columns, add a nullable ledger timesheet-state column plus queue helpers, land `fetch_timesheet` config registries, thread request-type / entity attribution into every recorded Anthropic and compat call (probes included), and add zero-stub `get_receipt` on those two externals (receipt cost left null). Does **not** implement the runner, dispatcher due path, OpenRouter billed receipts, daemon retirement, Google search recording, or contact ledger wrapping (siblings AST-2218 / AST-2219 / AST-2220).

## UAT fitness

- **AC restored:** Parent AC **2** (“The table is `service_timesheet`”), AC **5** stub half (`test_anthropic.py` / `test_llm_compat.py`: `get_receipt` returns shared keys, token/status filled, **receipt / platform cost null**, no HTTP), AC **8** (“Attribution is recorded at call time, probes included; multi-entity leaves entity id empty”).
- **Correct outcome:** After schema ensure, every DB has `service_timesheet` (rows preserved from any prior `agent_timesheets`); each Anthropic / compat recorded call (including OpenRouter probes) stores request type, entity type, entity id (empty when one call covers many entities), call start/stop, response size, and completion status; stub `get_receipt` returns the config receipt field list with null platform/receipt cost so later batch totals keep calculated cost.
- **Sibling check:** AST-2218 still owns runner / OpenRouter billed `get_receipt` / daemon retire / ledger close → `NEW` / provision; AST-2219 Google search rows + CSE stub; AST-2220 contact ledger open/close. This plan leaves `TIMESHEET_*_RECONCILE*` constants and pending-gen helpers in place, does not touch `openrouter.py` / `timesheets.py` runner / `dispatcher.py` close / `roster.py` / `contact.py` / `google_cse.py`. Verified by Files Changed + Boundaries below.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Renaming the table in SQL only (or aliasing reads) without attribution columns, call-time stamping, registry, stubs, and queue helpers would leave AC 5/8 and sibling #2’s data contracts unmet. Inventing OpenRouter billed receipts or retiring the daemon here would steal AST-2218 scope.

## Explicit scope gate

Files and change kinds below are exactly this ticket’s **## Scope** / parent Technical scope for child #1. Test / bible paths in Scope are Betty (`qa-child`); engineer stages commit **product** files only (pre-commit bans `tests/` / `docs/test-bible/**`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `FETCH_TIMESHEET_CONFIG`; request-type / receipt-field / ledger timesheet-state registries; search server id constant for timesheet provider allow; leave `TIMESHEET_*_RECONCILE*` untouched | utils |
| `src/data/database.py` | Rename table + schema ensure; attribution columns; ledger `timesheet_state`; `_add_timesheet_entry` + queue/list/state helpers; `update_timesheet_platform` null-cost OK; header inventory; pending-gen helpers left in place | data |
| `src/core/task_performance.py` | Raw SQL → `service_timesheet` | core |
| `src/ui/api/api_admin.py` | Raw SQL → `service_timesheet` | ui |
| `src/core/agent.py` | Pass request type + entity type/id into `_send_to_server` (multi-entity → empty entity id) | core |
| `src/external/anthropic.py` | Timing/size/status/attribution on recorded rows; zero-stub `get_receipt` | external |
| `src/external/llm_compat.py` | Same on real + probe rows; zero-stub `get_receipt` for direct servers | external |
| `tests/component/utils/test_config.py` | Betty — config registries | test |
| `docs/test-bible/utils/config.md` | Betty | bible |
| `tests/component/data/database/test_timesheets.py` | Betty — rename migration + attribution writers | test |
| `docs/test-bible/data/database/timesheets.md` | Betty | bible |
| `tests/component/core/test_agent.py`, `tests/component/core/test_agent_ast1879.py` | Betty — attribution into recorded call | test |
| `docs/test-bible/core/agent.md` | Betty | bible |
| `tests/component/external/test_anthropic.py`, `docs/test-bible/external/anthropic.md` | Betty — stub `get_receipt` + attribution | test/bible |
| `tests/component/external/test_llm_compat.py`, `docs/test-bible/external/llm_compat.md` | Betty — stub + probe attribution | test/bible |

**Out of this ticket (siblings):** `src/core/timesheets.py` runner / daemon remove, `src/core/dispatcher.py`, `src/external/openrouter.py`, `src/external/google_cse.py`, `src/core/roster.py`, `src/core/contact.py`, `data/admin/agent_task.json`, provision script.

## Stage 1: Config registries

**Done when:** `FETCH_TIMESHEET_CONFIG` and the three registries are importable from `config.py`; reconcile constants are byte-identical to tip before this stage; no product caller uses the new registries yet.

1. In `src/utils/config.py`, near `METEORITE_EMAIL_MAILBOX_CONFIG` (candidate-bound poller peer), add:

```python
# AST-2217 / AST-2215: candidate-bound fetch_timesheet dispatch-row defaults.
# entity_type / trigger_state None — poller, not ENTITY_TYPES claim (stat.dispatch.entity-state-bound).
# freq_hrs None, auto_mode False — Susan 2026-10-15. Provision/due path is AST-2218.
FETCH_TIMESHEET_CONFIG = {
    "task_key": "fetch_timesheet",
    "entity_type": None,
    "trigger_state": None,
    "freq_hrs": None,
    "auto_mode": False,
    "min_count": 1,
    "batch_size": 1,
}
```

2. Same file, next to timesheet / `ALLOWED_TIMESHEET_PROVIDERS`, add registries (exact keys — builders and stubs must use these, not invent parallel lists):

```python
TIMESHEET_REQUEST_TYPES = (
    "DISPATCH_AGENT",
    "DISPATCH_SEARCH",
    "CONTACT_AGENT",
)

# Vendor half filled by get_receipt; Astral half (request_type, candidate_id, entity_*)
# comes from the recorded call. Shared shape for every billing external (AST-2215 AC5).
TIMESHEET_RECEIPT_FIELDS = (
    "request_type",
    "call_start",
    "call_stop",
    "platform_cost",
    "candidate_id",
    "entity_type",
    "entity_id",
    "native_tokens_prompt",
    "native_tokens_completion",
    "native_tokens_cached",  # cache read
    "cache_write_tokens",
    "response_item_count",
    "response_char_length",
    "completion_status",
)

LEDGER_TIMESHEET_STATES = (
    "NEW",
    "FETCHING",
    "RECEIPTED",
)

# Search timesheet rows (AST-2219 writer); not an LLM_SERVER_CONFIG id.
TIMESHEET_SEARCH_SERVER_ID = "google_cse"
```

3. Asserts: `FETCH_TIMESHEET_CONFIG["task_key"] == "fetch_timesheet"`; `entity_type` / `trigger_state` / `freq_hrs` are `None`; `auto_mode is False`; `set(TIMESHEET_REQUEST_TYPES) == {"DISPATCH_AGENT", "DISPATCH_SEARCH", "CONTACT_AGENT"}`; `set(LEDGER_TIMESHEET_STATES) == {"NEW", "FETCHING", "RECEIPTED"}`; `"platform_cost" in TIMESHEET_RECEIPT_FIELDS`.

4. Do **not** edit `TIMESHEET_RECONCILE_*` / `TIMESHEET_BATCH_RECONCILE_*` (Technical scope — go dead in AST-2218).

⚠️ **Decision:** Receipt field names reuse AST-1965 platform column names (`platform_cost`, `native_tokens_*`) plus attribution/timing columns so `update_timesheet_platform` and stubs share one vocabulary. `cache_write_tokens` is the Astral-recorded cache-write count (stubs may zero it); OpenRouter’s billed half still lands on `native_tokens_*` / `platform_cost` in AST-2218.

## Stage 2: `service_timesheet` schema, attribution writers, ledger state helpers

**Done when:** A DB that had `agent_timesheets` with rows, after `_ensure_timesheets_schema`, has `service_timesheet` with the same row count and no `agent_timesheets` table; fresh creates use `service_timesheet`; attribution columns exist; `dispatch_ledger.timesheet_state` is nullable; queue helpers exist; `sum_cost_by_batch` SQL still prefers non-null `platform_cost`; pending-gen helpers still exist and still query the new table name.

1. In `src/data/database.py` header inventory: replace the `agent_timesheets` bullet with `service_timesheet` — same meaning (unified token/cost ledger for LLM + search/contact calls), list new attribution columns (`request_type`, `entity_type`, `entity_id`, `call_start`, `call_stop`, `response_item_count`, `response_char_length`, `completion_status`) and keep AST-1965 platform columns. Note `anthropic_timesheets` untouched.

2. Rename create helper `_create_agent_timesheets_table` → `_create_service_timesheet_table`. `CREATE TABLE service_timesheet` with all prior columns **plus** attribution:

| Column | Type | Notes |
|--------|------|-------|
| `request_type` | `TEXT` | one of `TIMESHEET_REQUEST_TYPES` |
| `entity_type` | `TEXT` | nullable |
| `entity_id` | `TEXT` | nullable; empty string or NULL when multi-entity |
| `call_start` | `TIMESTAMP` | |
| `call_stop` | `TIMESTAMP` | |
| `response_item_count` | `INTEGER` | default 0 |
| `response_char_length` | `INTEGER` | default 0 |
| `completion_status` | `TEXT` | e.g. success / failure class |

3. In `_ensure_timesheets_schema`:
   - If `agent_timesheets` exists and `service_timesheet` does not: `ALTER TABLE agent_timesheets RENAME TO service_timesheet`, then commit.
   - If neither exists: `_create_service_timesheet_table`.
   - If only `service_timesheet` exists: skip rename.
   - Never leave both tables. Never touch `anthropic_timesheets`.
   - After the table is present under `service_timesheet`, `PRAGMA table_info` + `ALTER TABLE … ADD COLUMN` for any missing attribution columns and any missing `_AGENT_TIMESHEET_PLATFORM_COLUMNS` (same loop pattern as AST-1965).
   - Rewrite every SQL string in this module that named `agent_timesheets` to `service_timesheet` (inserts, updates, selects, pending-gen helpers, `get_agent_timesheets` / list helpers, `backfill_agent_timesheet_costs`, `sum_cost_by_batch`). **Keep** function names that say `agent_timesheets` in Python identifiers only if changing them would fan out beyond Scope — prefer renaming public readers only when this file is the sole definer; SQL table name must be `service_timesheet`.

4. Extend `_add_timesheet_entry` kwargs with the attribution fields (defaults `None` / `0` so existing call sites compile until Stage 3/4 land). Validation: `provider` must be in `ALLOWED_TIMESHEET_PROVIDERS` **or** equal `TIMESHEET_SEARCH_SERVER_ID`. Search-shaped rows: all token and `calc_cost_*` fields may be 0; `model_code` may be null. INSERT includes the new columns. Anthropic mirror into `anthropic_timesheets` stays as today (attribution columns are **not** added to `anthropic_timesheets`).

5. Modify `update_timesheet_platform`:
   - `platform_cost: Optional[float]` (was required `float`) — stubs pass `None`.
   - Still stamps `platform_reconciled_at` when a receipt is applied (null cost is still a completed stub receipt for sibling runner semantics).
   - Still keys by `agent_req_id` / external id; never touches `calc_cost_*` or Astral attribution columns.
   - Docstring: null `platform_cost` means stub / not billed, not “row missing”.

6. `sum_cost_by_batch`: keep `COALESCE(platform_cost, calc_cost_* sum)` on `service_timesheet`. No preference change (Technical scope). Docstring may note stub null cost falls through to calc.

7. `_ensure_dispatch_ledger_schema`: add migration `("timesheet_state", "TEXT")` (nullable — historical rows stay null). Add `"timesheet_state"` to `_LEDGER_UPDATE_COLS`.

8. New functions (exact responsibilities; names may match these):

| Function | Behavior |
|----------|----------|
| `count_ledger_timesheet_state(candidate_id, state="NEW") -> int` | Count that candidate’s `dispatch_ledger` rows with `timesheet_state = state`. Null state never matches. |
| `claim_ledger_timesheet_fetching(candidate_id) -> List[str]` | Atomically set that candidate’s `NEW` rows to `FETCHING`; return their `batch_id`s. |
| `set_ledger_timesheet_state(batch_id, state) -> None` | Set one ledger row’s `timesheet_state` (must be in `LEDGER_TIMESHEET_STATES`). |
| `list_timesheet_rows_for_batches(batch_ids) -> List[dict]` | Rows for those `batch_id`s with at least `agent_req_id`, `provider` (server id), `batch_id`, plus attribution columns needed by the runner. |

⚠️ **Decision:** Lightweight ledger state batching (Susan) — no `batch_id` / `batch_created_at` lock columns on `dispatch_ledger`. `claim_ledger_timesheet_fetching` is the claim; sibling runner releases via `set_ledger_timesheet_state` / `finally` back to `NEW` (`patt.entity.batch-processing` at ledger-row grain).

9. Leave `count_pending_gen_platform_timesheets` and `list_pending_gen_platform_timesheets` in place; only retarget SQL to `service_timesheet`.

## Stage 3: Call-time attribution (agent → externals)

**Done when:** A `do_task` LLM call records `request_type=DISPATCH_AGENT`, `entity_type` from the task, `entity_id=index` when `batch_size == 1` (or a single entity), and empty/`NULL` `entity_id` when `batch_size > 1` or multiple `ctx["batch_entities"]`; probe rows in `llm_compat` get the same attribution fields as the real call; `call_stop >= call_start`; `response_char_length` equals `len` of the response text used for the row; readers in `task_performance.py` / `api_admin.py` query `service_timesheet`.

1. In `src/core/agent.py`, extend `_send_to_server` with kwargs: `request_type: str`, `entity_type: Optional[str]`, `entity_id: Optional[str]`. Pass them through `common` into both `send_to_anthropic` and `send_to_llm_compat`.

2. At the `do_task` call site (~2151): set `request_type="DISPATCH_AGENT"`; `entity_type` from the existing `_effective_entity_type(...)`; `entity_id` = `index` when the call covers one entity, else `None` or `""`. Multi-entity rule: if `batch_size > 1` **or** `len((ctx or {}).get("batch_entities") or []) > 1`, leave `entity_id` empty. Ad-hoc `_send_to_server` (~3258): `request_type="DISPATCH_AGENT"`, `entity_type`/`entity_id` as available (often null) — do **not** invent `CONTACT_AGENT` (AST-2220).

3. In `src/external/anthropic.py` `send_to_anthropic`: accept the three attribution kwargs; when building `_timesheet_kwargs`, set `call_start=start_time` (ISO/`_utc_now`-style string consistent with existing timestamps), `call_stop` at record time, `response_char_length` from the parsed/response text length used elsewhere for the success path (0 on hard fail before body), `response_item_count` default `1` for a single completion (0 if no usable response), `completion_status` from success/failure, plus `request_type` / `entity_type` / `entity_id`. Pass them into `record_timesheet(...)`.

4. In `src/external/llm_compat.py`: same fields in `_timesheet_kwargs_for` and on `_record_probe` (probe is its own row, same `batch_id` via `log_batch_id`, same attribution as the outer call’s kwargs). Pass attribution into `send_to_llm_compat` signature from agent.

5. In `src/core/task_performance.py` and `src/ui/api/api_admin.py`: change the one raw SQL each that reads `agent_timesheets` to `service_timesheet`. No other logic changes.

## Stage 4: Zero-stub `get_receipt` (Anthropic + llm_compat)

**Done when:** `get_receipt(["x","y"], key)` on each module returns a list/dict of two receipts whose keys are exactly `TIMESHEET_RECEIPT_FIELDS`; token/status fields are filled (zeros / a stub completion status OK); `platform_cost` is `None`; no HTTP / SDK call is made; invalid key handling does not raise out of the function (per-id error entries OK if shape still carries the field list + an error marker — prefer one receipt dict per id with `completion_status` / optional `error` key only if that key is added to the registry; **do not** add undeclared keys — if per-id failure needs a signal, use `completion_status="error"` and leave cost null).

1. In `src/external/anthropic.py`, add:

```python
def get_receipt(external_ids: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Zero-stub receipts (AST-2217). No network. platform_cost always None."""
```

   For each id in `external_ids`, return a dict with every `TIMESHEET_RECEIPT_FIELDS` key: Astral half empty/`None`, tokens `0`, `platform_cost=None`, `completion_status` stub-success (e.g. `"stub"`), timing null or epoch-noop. Do not call Anthropic. `api_key` is accepted for signature parity with OpenRouter’s future `get_receipt` and ignored.

2. In `src/external/llm_compat.py`, add the same `get_receipt` (direct-server stub). Docstring: OpenRouter-routed generation ids are answered by `openrouter.get_receipt` (AST-2218), not this stub.

3. Do **not** wire these into the runner (AST-2218). Do **not** edit `openrouter.py`.

## Boundaries

- No `threading.Thread` / reconcile retirement in `timesheets.py`.
- No dispatcher provision / due / `_persist_dispatch_ledger_close` → `NEW`.
- No Google / roster / contact / `agent_task.json` / provision script.
- Engineer does not commit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 5 — agree
