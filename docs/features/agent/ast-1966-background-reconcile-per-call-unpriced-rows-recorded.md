<!-- linear-archive: AST-1966 archived 2026-10-08 -->

## Linear archive (AST-1966)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1966/background-reconcile-per-call-unpriced-rows-recorded-query-llm  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1963 — Query LLM Platform for Timesheet Data to Finish Batch  
**Blocked by / blocks / related:** parent: AST-1963

### Description

## What this implements

After #1 and #2. `record_timesheet_entry` starts a background reconcile for each `openrouter`-routed row (retries, platform write, closed-ledger refresh), and `llm_compat` stops skipping rows it can't price.

## Citations

`patt.entity.batch-processing`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.debug`.

## Scope

* `src/external/llm_compat.py` — **modified**. A row whose local cost can't be computed is still recorded instead of skipped.
  * **Modified function** `send_to_llm_compat` (its timesheet-kwargs helper) — when catalog pricing or token counting raises, returns row values with the available token counts and zero calculated cost instead of no row.
* `src/core/timesheets.py` — **modified**. `record_timesheet_entry` starts the background reconcile for `openrouter`-routed rows; the reconcile (key lookup, retries, row write, ledger refresh) lives here.
  * **Modified function** `record_timesheet_entry` — after the row is written, when the row's routing type (config helper, from its server id and SKU) is `openrouter` and it has a generation id, starts the background reconcile and returns at once.
  * **New function (background reconcile)** — resolves the key for the row's server from the row's candidate (same source as `agent._candidate_server_key`; no key → warn and stop), calls the OpenRouter lookup up to the configured count with exponential backoff (configured base wait, doubling each try), writes the platform columns on success, then, if the row's batch has a `dispatch_ledger` row with `completed_at` set, recomputes that row's `total_cost` (`sum_cost_by_batch`) and `entity_cost` (total ÷ `total_processed`, same rule as the dispatcher) via `update_dispatch_ledger`. Runs off the caller's event loop so it outlives the batch's loop and never blocks a call. The ledger refresh recomputes from the table every time, so it is safe to run more than once and safe against the batch-close write.
* `tests/component/external/test_llm_compat.py`, `docs/test-bible/external/llm_compat.md`, `tests/component/core/test_timesheets.py`, `docs/test-bible/core/timesheets.md` — **modified**.

## Acceptance criteria

"Stubbed lookup" = the component-test stub of the OpenRouter generation-stats HTTP call.

3. **Unpriced calls still get a row.**
   * **Check (**`test_llm_compat.py`**):** with catalog pricing stubbed to raise, a successful call invokes `record_timesheet` once, with `calc_cost_*` all 0 and the response's token counts. (`test_timesheets.py`, database): `_add_timesheet_entry` with a SKU the catalog doesn't price returns `True` and the row exists.
   * **Fails if:** `record_timesheet` isn't called, or the insert is refused.
   * **This child:** the `llm_compat` half (`test_llm_compat.py`). The database half is #2.
4. **Recording never waits on the platform.**
   * **Check (**`core/test_timesheets.py`**):** with the stubbed lookup blocked, `record_timesheet_entry` for an `openrouter`-routed row returns before the lookup completes and the row exists with null platform cost. For a `direct`-routed row, the stub is never called.
   * **Fails if:** it blocks, or a direct row is looked up.
5. **Retry then give up.**
   * **Check (same file, sleep stubbed and recorded):** stub returns not-ready 4 times then 200 → exactly 5 calls and the row's platform columns are set. Stub fails every time → exactly 5 calls (the configured count), platform cost stays null, `calc_cost_*` unchanged, one WARNING naming the row's `agent_req_id` and batch id. With base wait 2, the recorded waits between tries are `[2, 4, 8, 16]`.
   * **Check (**`test_config.py`**):** retry count constant is `5` and backoff base constant is `2`.
   * **Fails if:** call count ≠ 5 in either case, the row is wrong, warnings ≠ 1, or the waits are not doubling from the base (e.g. a fixed interval).
   * **This child:** the reconcile checks in `core/test_timesheets.py`; the `test_config.py` constant check is #1.
6. **Late cost refreshes a closed ledger row.**
   * **Check (**`core/test_timesheets.py`**):** a `dispatch_ledger` row with `completed_at` set, `total_processed = 2`, `total_cost = 0.02`; reconciling its one row to platform 0.06 leaves `total_cost = 0.06` and `entity_cost = 0.03`. Same with `completed_at` null → ledger row unchanged.
   * **Fails if:** the closed row isn't refreshed, the open row is touched, or `entity_cost` ≠ total ÷ processed.

## Boundaries

* Does **not** change `compute_batch_cost`, `dispatcher.py` or any batch-close path — reconciliation is per call, decoupled from batch close.
* Does **not** add config fields, the lookup function (#1) or table columns / writer (#2).
* Direct models (Anthropic, DeepSeek, Kimi) are never looked up.

## Notes for planning

* Cite `patt.entity.batch-processing`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.debug` — parent Architectural definition has the links.
* Platform facts (parent § Platform research): OpenRouter `GET /api/v1/generation?id=<gen-id>`, bearer key; `total_cost`, `native_tokens_prompt` / `_completion` / `_cached` / `_reasoning`, `provider_name`; stats can lag the response by a few seconds.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T02:47:12.120Z
[code-rubric] PROCEED (Commit: f4fd568df) background reconcile per call

#### betty — 2026-10-04T02:43:30.216Z
`origin/sub/AST-1963/AST-1966-background-reconcile` @ `f4fd568df` · reconcile tests ready

#### joan — 2026-10-04T02:35:34.881Z
[plan-rubric] PROCEED (Commit: ad8068282) reconcile and unpriced rows

#### ada — 2026-10-04T02:34:04.714Z
`origin/sub/AST-1963/AST-1966-background-reconcile` @ `ad8068282` · plan ready, prototype-verified

---

# AST-1966 — Background reconcile per call, unpriced rows recorded

- **Ticket:** [AST-1966](https://linear.app/astralcareermatch/issue/AST-1966) · **Parent:** [AST-1963](https://linear.app/astralcareermatch/issue/AST-1963) Query LLM Platform for Timesheet Data to Finish Batch
- **Publish ref:** `sub/AST-1963/AST-1966-background-reconcile` (origin only)
- **Canon Scope:** `patt.entity.batch-processing`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.debug`

Two changes. First, `send_to_llm_compat`'s timesheet helper stops returning `None` when catalog pricing (or token counting) raises. It logs the fault and returns a full row with zero calculated cost (and zero counts if the counts couldn't be read), so the call is always recorded. Second, `record_timesheet_entry` writes the row exactly as today. Then, when the row's model routing (`get_model_routing(server id, SKU)`, AST-1964) is not `direct` and the row has a generation id, it starts `reconcile_timesheet_platform` on a daemon thread and returns at once. The reconcile does four things:
- looks up the candidate's key for the row's server
- calls `get_generation_stats` up to `TIMESHEET_RECONCILE_RETRIES` times, waiting `TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS` before the 2nd try and doubling the wait before each later one
- writes the platform columns with `update_timesheet_platform` (AST-1965)
- if the row's batch has a closed `dispatch_ledger` row, re-totals it from `sum_cost_by_batch`, using the dispatcher's `entity_cost` rule

Out of scope here: config fields, the lookup function, table columns and the writer (all already on ftr from AST-1964 and AST-1965). This ticket also doesn't touch `compute_batch_cost`, `dispatcher.py` or any batch-close path, and direct models are never looked up.

## Scope gate

Product files: `src/external/llm_compat.py` and `src/core/timesheets.py`, both named in this ticket's `## Scope`. Each change matches a kind its Technical scope lists:
- `send_to_llm_compat`'s timesheet-kwargs helper (`_timesheet_kwargs_for`) returns zero-cost row values instead of no row when pricing or token counting raises. The `CALC_COST_KEYS` import is the only other line in that file the change forces.
- `record_timesheet_entry` starts the background reconcile for rows whose routing isn't `direct` and that carry a generation id.
- New function `reconcile_timesheet_platform`: key lookup, retries with exponential backoff, row write, closed-ledger refresh, run off the caller's event loop.

The test files and bible pages listed in Scope (`test_llm_compat.py`, `llm_compat.md`, `core/test_timesheets.py`, `core/timesheets.md`) belong to Betty (`qa-child`). No test-tree edits happen here.

## AC boundaries

| AC (parent #) | Check | Closed here by | Closes on ftr after |
|----|-------|----------------|---------------------|
| 3 (`llm_compat` half) | Catalog pricing stubbed to raise → `record_timesheet` called once, `calc_cost_*` all 0, the response's token counts | Stage 1 | The database half shipped in AST-1965 |
| 4 | Lookup blocked → `record_timesheet_entry` returns first, row exists with null platform cost; direct row → stub never called | Stage 2 step 1 | — |
| 5 (reconcile half) | 4× not-ready then 200 → 5 calls, columns set; always failing → 5 calls, platform null, calc unchanged, one WARNING naming `agent_req_id` + batch id; waits `[2, 4, 8, 16]` | Stage 2 step 1 | The `test_config.py` constants half shipped in AST-1964 |
| 8 | Closed ledger (`total_processed 2`, `total_cost 0.02`) + row reconciled to 0.06 → `total_cost 0.06`, `entity_cost 0.03`; open ledger unchanged | Stage 2 step 1 | — |
| 1 (grep) | `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` returns nothing | Both stages' Done-when | — |

(This ticket's description numbers the closed-ledger check "6"; it is the parent's AC 8.)

## Contract used from siblings (already on ftr)

| Name | Module | Shape |
|------|--------|-------|
| `get_model_routing(server_id, sku)` | `src.utils.config` | `"direct"` \| the OpenRouter routing value; `ValueError` when no model has that server + SKU |
| `TIMESHEET_RECONCILE_RETRIES` / `TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS` | `src.utils.config` | `5` / `2.0` |
| `get_generation_stats(generation_id, api_key)` | `src.external.openrouter` | `{"success": True, "total_cost", "native_tokens_prompt", "native_tokens_completion", "native_tokens_cached", "native_tokens_reasoning", "provider_name"}` or `{"success": False, "error"}`; never raises, logs call/response at debug |
| `update_timesheet_platform(agent_req_id, platform_cost, native_tokens_prompt, native_tokens_completion, native_tokens_cached, native_tokens_reasoning, host) -> int` | `src.data.database` | stamps `platform_reconciled_at`; raises on DB error |
| `sum_cost_by_batch(batch_ids)` | `src.data.database` | `{batch_id: total}`, platform cost per row when present |
| `get_dispatch_ledger(batch_id)` / `update_dispatch_ledger(batch_id, **cols)` / `get_candidate(candidate_id)` | `src.data.database` | unchanged existing functions; `get_candidate(None)` returns `None` |

## Test impact (for Betty, `qa-child`)

- **Breaks:** `tests/component/core/test_timesheets.py::TestRecordTimesheetEntry::test_delegates_to_database_add` calls `record_timesheet_entry(agent_req_id="req-1", batch_id="batch-1", batch_size=1)` with no `model_code`/`provider`. After Stage 2 the routing lookup raises `ValueError: No LLM model for server 'anthropic' and SKU None`, because a row with a generation id must name a catalog model. Fix it in the test: pass a direct model (e.g. `provider="deepseek", model_code="deepseek-v4-pro"`) or stub `timesheets_mod.get_model_routing`. Verified against a prototype of this plan: that is the only new failure across `test_llm_compat.py`, `core/test_timesheets.py` and `core/test_agent*.py`. The 43 `test_agent.py` failures are pre-existing on the clean tree.
- **Patch points in `src.core.timesheets`:** `get_generation_stats`, `get_candidate`, `time` (the reconcile calls `time.sleep(wait)`, so `monkeypatch.setattr(timesheets_mod.time, "sleep", waits.append)` records the waits), `reconcile_timesheet_platform` (looked up at call time, so a stub sees the thread start), `logger` (one `warning` on give-up / no key).
- **Background thread in tests:** an openrouter-routed `record_timesheet_entry` in any test starts a real daemon thread. Unless `get_generation_stats` is stubbed, it hits the external-I/O guard / network and sleeps 2+4+8+16 s before warning. AC 4 tests should stub the lookup with a gate (`threading.Event`) and poll for the row's `platform_cost`. AC 5 and AC 8 tests can call `reconcile_timesheet_platform(agent_req_id, server_id, candidate_id, batch_id)` directly (synchronously) after `_add_timesheet_entry`.
- **AC 3 `llm_compat` check:** stub `llm_compat.calculate_cost_components_from_counts` to raise. The row arrives with `calc_cost_*` all `0.0` and the usage's counts, and one `logger.exception` record is emitted.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/llm_compat.py` | `_timesheet_kwargs_for` always returns a row (zero counts / zero cost on a raise, each logged once); import `CALC_COST_KEYS` | external |
| `src/core/timesheets.py` | `record_timesheet_entry` starts the reconcile thread for non-`direct` rows; new `reconcile_timesheet_platform`; module docstring line | core |

## Stage 1: Unpriced calls still get a row

**Done when:** the command below prints `STAGE1 OK` (the `ValueError: Unknown SKU` traceback above it is the new `logger.exception` record, expected). `python3 -m py_compile src/external/llm_compat.py` is clean, and `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` returns nothing.

```bash
python3 -c "
import asyncio, types, src.external.llm_compat as lc
resp = types.SimpleNamespace(id='gen-1', stop_reason='end_turn', provider=None,
    content=[types.SimpleNamespace(type='text', text='ok')],
    usage=types.SimpleNamespace(input_tokens=100, output_tokens=25, cache_read_input_tokens=50, cache_creation_input_tokens=5))
lc._create = lambda *a, **k: resp
def boom(*a, **k): raise ValueError('Unknown SKU')
lc.calculate_cost_components_from_counts = boom
rows = []
out = asyncio.run(lc.send_to_llm_compat([{'type':'text','text':'hi'}], server_id='kimi', sku='kimi-k2.6', tier={}, api_key='k', record_timesheet=lambda **kw: rows.append(kw)))
assert out['success'] and len(rows) == 1, (out, rows)
r = rows[0]
assert (r['calc_cost_cache_write'], r['calc_cost_cache_read'], r['calc_cost_no_cache_input'], r['calc_cost_output']) == (0.0, 0.0, 0.0, 0.0)
assert (r['cache_read_tokens'], r['total_no_cache_input_tokens'], r['total_output_tokens'], r['cache_write_tokens']) == (50, 100, 25, 5)
assert (r['agent_req_id'], r['provider'], r['model_code']) == ('gen-1', 'kimi', 'kimi-k2.6')
print('STAGE1 OK')
"
```

1. **Import.** In `src/external/llm_compat.py`, replace

   ```python
   from src.utils.cost_calculator import calculate_cost_components_from_counts, usage_to_token_counts
   ```

   with

   ```python
   from src.utils.cost_calculator import CALC_COST_KEYS, calculate_cost_components_from_counts, usage_to_token_counts
   ```

2. **Helper always returns a row.** In `send_to_llm_compat`, replace the head of `_timesheet_kwargs_for`, from its `def` line through the `except Exception: return None` block:

   ```python
           def _timesheet_kwargs_for(response: Any) -> Optional[Dict[str, Any]]:
               # None when cost can't be computed — callers then skip the timesheet row (unchanged behaviour).
               counts = usage_to_token_counts(response.usage)
               try:
                   cost_parts = calculate_cost_components_from_counts(
                       counts["cache_read"],
                       counts["cache_miss"],
                       counts["output"],
                       counts["cache_write"],
                       sku=sku,
                       server_id=server_id,
                   )
               except Exception:
                   return None
   ```

   with

   ```python
           def _timesheet_kwargs_for(response: Any) -> Dict[str, Any]:
               # Always a row (AST-1966): counts that can't be read are 0, cost that can't be priced is 0 —
               # platform-routed rows get their billed cost from the background reconcile either way.
               try:
                   counts = usage_to_token_counts(response.usage)
               except Exception as exc:
                   logger.exception(
                       "%s | timesheet token counts on %s %s\n  %s: %s\n  Recording the row with zero tokens",
                       getattr(response, "id", None) or "-", server_id, sku, type(exc).__name__, exc,
                   )
                   counts = {"cache_read": 0, "cache_miss": 0, "output": 0, "cache_write": 0}
               try:
                   cost_parts = calculate_cost_components_from_counts(
                       counts["cache_read"],
                       counts["cache_miss"],
                       counts["output"],
                       counts["cache_write"],
                       sku=sku,
                       server_id=server_id,
                   )
               except Exception as exc:
                   logger.exception(
                       "%s | timesheet catalog price on %s %s\n  %s: %s\n  Recording the row with zero calculated cost",
                       getattr(response, "id", None) or "-", server_id, sku, type(exc).__name__, exc,
                   )
                   cost_parts = dict.fromkeys(CALC_COST_KEYS, 0.0)
   ```

   The `return dict(...)` that follows stays byte-for-byte unchanged.

   ⚠️ **Decision (log level):** `logger.exception` with live facts (generation id, server, SKU), the exception, and the product next step. A raise caught here has no retry route and only happens when the catalog is out of step with a live call, so `stat.logging.error` applies, not the warning carve-out (that is for dispatch-batch retry holdings). Rejected: keeping today's silent swallow (it hides a catalog gap, and `stat.logging.error` forbids it); `logger.warning` (the statute bars warning for a thrown, unrouted exception).

   ⚠️ **Decision (call-site guards left alone):** the six `if _timesheet_kwargs is not None and record_timesheet is not None:` checks and `_record_probe`'s `if kw is not None:` become always-true on their first half. They stay untouched. Rewriting seven call sites widens the diff with no change in behaviour, and Scope names only the helper. Token counting already runs once in the main path before the helper (`counts = usage_to_token_counts(response.usage)` just after the call). So the helper's zero-count branch only changes behaviour on the probe's record path. It is there because Scope names it.

3. `python3 -m py_compile src/external/llm_compat.py`, run the Done-when command and the `rg` check, then commit `code(AST-1966): unpriced calls still get a timesheet row` and push `git push origin HEAD:sub/AST-1963/AST-1966-background-reconcile`.

## Stage 2: Background reconcile per call

**Done when:** the command below prints `STAGE2 OK`, `python3 -m py_compile src/core/timesheets.py` is clean, and `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` returns nothing.

```bash
ASTRAL_DB_DIR=$(mktemp -d) python3 -c "
import threading, time, types
import src.core.timesheets as ts, src.data.database as d
ts.get_candidate = lambda cid: {'candidate_api_keys': {'openrouter': 'k'}}
warns = []
ts.logger = types.SimpleNamespace(debug=lambda *a, **k: None, exception=lambda *a, **k: None, warning=lambda *a, **k: warns.append(a))
ok = {'success': True, 'total_cost': 0.06, 'native_tokens_prompt': 1, 'native_tokens_completion': 2, 'native_tokens_cached': 3, 'native_tokens_reasoning': 4, 'provider_name': 'DeepInfra'}
bad = {'success': False, 'error': 'Generation stats not ready: no total_cost'}
def row(rid, b, sku='z-ai/glm-4.7', srv='openrouter'):
    return dict(agent_req_id=rid, task_key_uuid='t', model_code=sku, candidate_id='c', batch_id=b, batch_size=1,
        cache_write_tokens=0, cache_read_tokens=0, no_cache_prompt_tokens=0, no_cache_live_tokens=0,
        total_no_cache_input_tokens=10, total_output_tokens=5, calc_cost_cache_write=0.0, calc_cost_cache_read=0.0,
        calc_cost_no_cache_input=0.02, calc_cost_output=0.0, provider=srv)
get = lambda rid, b: [r for r in d.list_timesheets(batch_id=b) if r['agent_req_id'] == rid][0]
# AC 4: returns before a blocked lookup completes; a direct row is never looked up
gate, calls = threading.Event(), []
ts.get_generation_stats = lambda gid, key: (calls.append(gid), gate.wait(5), ok)[2]
ts.record_timesheet_entry(**row('r4', 'b4'))
assert get('r4', 'b4')['platform_cost'] is None
gate.set()
for _ in range(50):
    if get('r4', 'b4')['platform_cost'] is not None: break
    time.sleep(0.1)
assert get('r4', 'b4')['platform_cost'] == 0.06 and calls == ['r4']
ts.record_timesheet_entry(**row('rd', 'bd', sku='deepseek-v4-pro', srv='deepseek'))
time.sleep(0.2)
assert calls == ['r4']
# AC 5: not-ready x4 then 200 -> 5 calls, columns set, waits [2, 4, 8, 16]; all fail -> 5 calls, one warning, calc unchanged
waits = []
ts.time = types.SimpleNamespace(sleep=waits.append)
seq = [bad] * 4 + [ok]
ts.get_generation_stats = lambda gid, key: (calls.append(gid), seq.pop(0))[1]
d._add_timesheet_entry(**row('r5', 'b5'))
calls.clear(); ts.reconcile_timesheet_platform('r5', 'openrouter', 'c', 'b5')
assert len(calls) == 5 and waits == [2, 4, 8, 16] and get('r5', 'b5')['host'] == 'DeepInfra'
ts.get_generation_stats = lambda gid, key: (calls.append(gid), bad)[1]
d._add_timesheet_entry(**row('r5f', 'b5f'))
calls.clear(); ts.reconcile_timesheet_platform('r5f', 'openrouter', 'c', 'b5f')
r = get('r5f', 'b5f')
assert len(calls) == 5 and r['platform_cost'] is None and r['calc_cost_no_cache_input'] == 0.02
assert len(warns) == 1 and 'r5f' in warns[0] and 'b5f' in warns[0]
# AC 8: closed ledger re-totalled; open ledger untouched
ts.get_generation_stats = lambda gid, key: ok
for b, closed in (('bc', True), ('bo', False)):
    d.save_dispatch_ledger(b, 'task', 'c', '2026-10-04 00:00:00')
    d.update_dispatch_ledger(b, total_processed=2, total_cost=0.02, **({'completed_at': '2026-10-04 00:01:00'} if closed else {}))
    d._add_timesheet_entry(**row('r6' + b, b))
    ts.reconcile_timesheet_platform('r6' + b, 'openrouter', 'c', b)
lc, lo = d.get_dispatch_ledger('bc'), d.get_dispatch_ledger('bo')
assert (lc['total_cost'], lc['entity_cost']) == (0.06, 0.03), lc
assert (lo['total_cost'], lo['entity_cost']) == (0.02, 0.0), lo
print('STAGE2 OK')
"
```

1. **Replace `src/core/timesheets.py` in full** with:

   ```python
   # -*- coding: utf-8 -*-
   """Core-owned persistence for API cost / timesheet rows (data layer write path).

   External `anthropic.send_to_anthropic` stays utils-only; core passes this as
   `record_timesheet` so inline token accounting still lands immediately after each call.

   Platform cost (AST-1966): after the insert, a row whose model is platform-routed gets its billed cost,
   native token counts and serving host looked up on a background thread (reconcile_timesheet_platform).
   The call never waits on it; a batch whose ledger row already closed is re-totalled when the cost lands.
   """

   import contextvars
   import threading
   import time
   from typing import Any, Optional

   from src.data.database import (
       _add_timesheet_entry,
       get_candidate,
       get_dispatch_ledger,
       sum_cost_by_batch,
       update_dispatch_ledger,
       update_timesheet_platform,
   )
   from src.external.openrouter import get_generation_stats
   from src.utils.config import (
       TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS,
       TIMESHEET_RECONCILE_RETRIES,
       get_model_routing,
   )
   from src.utils.logging import get_logger

   logger = get_logger(__name__)


   def record_timesheet_entry(**kwargs: Any) -> None:
       _add_timesheet_entry(**kwargs)
       agent_req_id = kwargs.get("agent_req_id")
       server_id = kwargs.get("provider", "anthropic")
       # The model's routing decides eligibility; "direct" keeps catalog cost only. Every caller builds
       # (server, SKU) from LLM_MODEL_CONFIG, so get_model_routing's ValueError here means config drift.
       if not agent_req_id or get_model_routing(server_id, kwargs.get("model_code")) == "direct":
           return
       # Own thread, not a task on the caller's loop: it outlives the batch's loop and never blocks the call.
       # copy_context carries log_debug / log_batch_id so the reconcile's debug lines follow the batch's flag.
       # Daemon: a process exit drops an in-flight lookup (no later sweep — parent decision).
       threading.Thread(
           target=contextvars.copy_context().run,
           args=(reconcile_timesheet_platform, agent_req_id, server_id, kwargs.get("candidate_id"), kwargs.get("batch_id")),
           daemon=True,
       ).start()


   def reconcile_timesheet_platform(
       agent_req_id: str, server_id: str, candidate_id: Optional[str], batch_id: Optional[str]
   ) -> None:
       """Background: one row's billed stats → its platform columns, then re-total its batch's ledger row
       if that batch already closed. Never raises; a thrown fault is logged here once."""
       try:
           # Same key source as agent._candidate_server_key (agent imports this module, so it can't be reused).
           key = ((get_candidate(candidate_id) or {}).get("candidate_api_keys") or {}).get(server_id)
           if not key:
               logger.warning(
                   "%s | batch %s -> no platform cost [candidate %s has no API key for server %s]. The row keeps its calculated cost",
                   agent_req_id, batch_id or "-", candidate_id or "-", server_id,
               )
               return
           logger.debug("Beginning generation-stats loop on %s tries for %s", TIMESHEET_RECONCILE_RETRIES, agent_req_id)
           for attempt in range(TIMESHEET_RECONCILE_RETRIES):
               if attempt:
                   # Base wait before the 2nd try, doubled before each later one (2, 4, 8, 16 s by default).
                   wait = TIMESHEET_RECONCILE_BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)
                   logger.debug("Retrying get_generation_stats for %s in %s s (try %s)", agent_req_id, wait, attempt + 1)
                   time.sleep(wait)
               logger.debug("Calling get_generation_stats: id=%s", agent_req_id)
               stats = get_generation_stats(agent_req_id, key)
               logger.debug("Response from get_generation_stats: %s", stats)
               if stats["success"]:
                   break
           logger.debug("End generation-stats loop after %s tries for %s", attempt + 1, agent_req_id)
           if not stats["success"]:
               logger.warning(
                   "%s | batch %s -> no platform cost after %s tries [%s]. The row keeps its calculated cost",
                   agent_req_id, batch_id or "-", TIMESHEET_RECONCILE_RETRIES, stats["error"],
               )
               return
           update_timesheet_platform(
               agent_req_id, stats["total_cost"], stats["native_tokens_prompt"], stats["native_tokens_completion"],
               stats["native_tokens_cached"], stats["native_tokens_reasoning"], stats["provider_name"],
           )
           ledger = get_dispatch_ledger(batch_id) if batch_id else None
           # Closed rows only — an open row is totalled by the batch-close write, which re-sums the table.
           # Recomputed from the table every time, so running it again is harmless.
           if ledger and ledger.get("completed_at"):
               total_cost = sum_cost_by_batch([batch_id]).get(batch_id, 0.0)
               total_processed = ledger.get("total_processed") or 0
               # Same rule as the dispatcher's batch close.
               entity_cost = total_cost / total_processed if total_processed > 0 else total_cost
               update_dispatch_ledger(batch_id, total_cost=total_cost, entity_cost=round(entity_cost, 7))
       except Exception as exc:
           logger.exception(
               "%s | batch %s platform cost reconcile\n  %s: %s\n  Stopping this row's reconcile; the call and batch are unaffected",
               agent_req_id, batch_id or "-", type(exc).__name__, exc,
           )
   ```

   ⚠️ **Decision (off-loop runner):** one daemon `threading.Thread` per eligible row, its target wrapped in `contextvars.copy_context().run`. A thread outlives the batch's event loop. It fits `get_generation_stats`' blocking `httpx.get` and a plain `time.sleep` backoff (AST-1964 chose sync for exactly this). The copied context carries `log_debug` / `log_batch_id`, so debug lines follow the batch's flag (`stat.logging.debug`: call sites don't gate, the ContextVar decides). Rejected:
   - `asyncio.create_task` on the caller's loop — it dies when the batch's loop closes.
   - A module `ThreadPoolExecutor` — it brings a worker cap nobody approved.
   - A dedicated background event-loop thread — more code for the same result.

   Daemon means a deploy or restart drops lookups still in flight. Those rows keep their calculated cost, which matches "no later sweep is required". A non-daemon thread would hold process exit for up to ~30 s per row.

   ⚠️ **Decision (routing test):** eligibility is `get_model_routing(...) != "direct"`, written as an early return on `== "direct"`. Parent AC 1's grep forbids the `"openrouter"` literal in this file, and Boundaries forbid adding a config constant. `LLM_MODEL_ROUTING_TYPES` validation guarantees exactly two values today. Rejected: `LLM_MODEL_ROUTING_TYPES[1]` (it silently breaks if someone reorders the tuple). Residual risk: a future third routing type would be looked up on OpenRouter until this line learns about it. Whoever adds that type touches the reconcile anyway.

   ⚠️ **Decision (no catch around routing):** `get_model_routing`'s `ValueError` is not caught in `record_timesheet_entry`. The only caller (`agent._send_to_server`) builds both server id and SKU from `LLM_MODEL_CONFIG`, so an unknown pair means config drift. The row is already written by then, and the existing `try/except` around every `record_timesheet(...)` call in `llm_compat` / `anthropic` keeps the LLM call unaffected.

   ⚠️ **Decision (key lookup inline):** the reconcile reads `get_candidate(candidate_id)["candidate_api_keys"][server_id]`, the same source `agent._candidate_server_key` uses when no ctx map is passed. Importing that helper would be a cycle (`core.agent` imports `core.timesheets` at module load). A session-paste call (ctx keys, no candidate id) therefore gets the "no API key" warning and no platform cost.

   ⚠️ **Decision (log levels):**
   - No key, or every try failed: one `logger.warning` naming the generation id, batch id and reason, plus the product consequence (`stat.logging.warning`, configured miss, no throw). `get_generation_stats` logs each try at debug only, so a give-up is exactly one warning.
   - Anything thrown (DB write, ledger read): one `logger.exception` at the reconcile's own handler (`stat.logging.error`), and it never propagates.
   - Loop begin/end, each call in/out and each retry wait: `logger.debug`.

   ⚠️ **Decision (residual race, not fixed here):** batch close runs `compute_batch_cost` and then `update_dispatch_ledger(..., completed_at=...)`. If a reconcile writes its platform cost between those two steps, it sees `completed_at` still null and skips the refresh. The close then writes a total that misses that one row. Closing that window needs a change to the batch-close path, which Boundaries exclude. The window is the two DB calls only.

2. `python3 -m py_compile src/core/timesheets.py`, run the Done-when command and the `rg` check, then commit `code(AST-1966): background platform cost reconcile per call` and push `git push origin HEAD:sub/AST-1963/AST-1966-background-reconcile`.

## Execution contract

The plan is binding. Run steps in order within each stage, and stages in order. Do not add files, functions or dependencies that aren't listed here. If a step is ambiguous, a referenced line has drifted, or a Done-when command fails when run literally: stop, post `🛑 Stage N blocked: …` on [AST-1963](https://linear.app/astralcareermatch/issue/AST-1963), and wait. Each stage ends in one `code(AST-1966): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-1963/AST-1966-background-reconcile`.

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-1966
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1963/AST-1966-background-reconcile` @ `ad8068282`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | B | | Stage 2: closed-ledger refresh via `sum_cost_by_batch` + `batch_id` matches audit-trail cost; documented close-window race excluded per Boundaries |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |
| stat.logging.debug | B | | Stage 2: retry loop begin/end, per-try call/response at debug, `copy_context` for ContextVar; call-in omits API key by design |

## Traceability

AC3 (`llm_compat`)→Stage 1; AC4→Stage 2 step 1 (non-blocking thread + direct skip); AC5 (reconcile)→Stage 2 step 1; parent AC8→Stage 2 step 1 (closed vs open ledger); parent AC1 grep→both stages Done-when. Config constant checks correctly deferred to AST-1964; DB unpriced-row half to AST-1965. No orphan stages.

## Findings

### discuss — Residual race (acceptable for this child)

- **Location:** Stage 2 step 1, “Decision (residual race, not fixed here)”
- **Finding:** Platform write between batch-close total and `completed_at` can miss one closed-ledger refresh until a later reconcile; Boundaries exclude `dispatcher` / batch-close changes.
- **Recommendation:** Accept for AST-1966 scope; track as known limitation if UAT hits the narrow window (Susan/Archie), not a plan revise for this ticket.

### acceptable — Definition fidelity

- **Location:** Scope gate / intro
- **Finding:** Only `llm_compat.py` and `timesheets.py` for product code; no new config, lookup, or schema; direct models never looked up; routing via `get_model_routing != "direct"` satisfies grep AC without `"openrouter"` literal.
- **Recommendation:** None.

### acceptable — Sibling contracts

- **Location:** `## Contract used from siblings`
- **Finding:** Names and shapes match AST-1964/1965 plans; reconcile maps `provider_name` → `host` on writer as specified.
- **Recommendation:** None.

### acceptable — Betty handoff

- **Location:** `## Test impact`
- **Finding:** `test_delegates_to_database_add` breakage, thread stubbing, direct `reconcile_timesheet_platform` for AC5/8, and `time.sleep` patch points are explicit.
- **Recommendation:** None.

### discuss — Canon Scope gap (not scored)

- **Location:** Stage 2 imports (`core` → `external.openrouter`, `data.database`)
- **Finding:** `astral.layers.import-direction` may govern layer edges; not on this ticket’s frozen list.
- **Recommendation:** Archie may amend at Discussion if a layer pass is required; plan follows existing core/data/external patterns.

## Review

- **Branch:** `sub/AST-1963/AST-1966-background-reconcile`
- **Build commits:** `6669ea8e6` (Stage 1 unpriced calls still get a timesheet row) · `563eae750` (Stage 2 background platform cost reconcile per call)
- **Build notes:** Both stages executed as written; both Done-when commands printed `STAGE1 OK` / `STAGE2 OK`, and `rg -n '"openrouter"' src/external/ src/core/timesheets.py src/data/database.py` finds nothing. `py_compile` is clean; no Python linter is installed on this host. Touched-area run (`test_llm_compat.py`, `core/test_timesheets.py`, `core/test_agent*.py`): 444 passed, 44 failed — 43 are pre-existing `test_agent.py` failures on the clean tree, and the 44th is `TestRecordTimesheetEntry::test_delegates_to_database_add`, the expected break flagged in § Test impact (no `model_code` on a row with a generation id). `validate-sub-log.sh --stage=build`: ok. No deviations.


## Radia review

[code-rubric]
**Ticket:** AST-1966
**Publish ref:** `f4fd568df21a2c7a3ba6ee3abe8fcb43bcddadd2` (`origin/sub/AST-1963/AST-1966-background-reconcile`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |
| stat.logging.debug | A | | |

## Column diff vs plan stage

- `patt.entity.batch-processing` — Joan **B** → Radia **A** (closed-ledger refresh uses `sum_cost_by_batch` + `batch_id`; residual close-window race is documented and out of Boundaries, not a pattern violation in this diff)
- `stat.logging.debug` — Joan **B** → Radia **A** (ungated loop begin/end, per-try call/response, retry-wait debug; `copy_context` on thread start; lookup call-in omits API key)
- (aligned) — `stat.logging.warning`, `stat.logging.error` — Joan **A**, Radia **A**

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling stacked ref:** Three-dot diff vs `origin/dev` includes AST-1964/1965 product, tests, and docs on the same sub tip. Expected epic stacking / `merge-tests`. **Canon and plan fidelity for AST-1966** target Ada commits `6669ea8e6`, `563eae750`, `b44f5f650` (`llm_compat.py`, `timesheets.py`, related tests/bibles).
- **Dependencies:** Spawn `Relations: blockedBy AST-1964, AST-1965 (both User Testing)` — sibling contracts (`get_model_routing`, reconcile constants, `get_generation_stats`, `update_timesheet_platform`, platform-first `sum_cost_by_batch`) are present on this ref.
- **Canon Scope (off-list, not scored):** Joan flagged `astral.layers.import-direction` for `core` → `external.openrouter` / `data.database` imports. **Default:** keep as planned; Archie amends Discussion only if a layer pass is required.
- **Residual race:** Platform write between batch-close total and `completed_at` can miss one closed-ledger refresh (plan § Decision). **Default:** accept for AST-1966; parent/dispatcher work if UAT hits the narrow window (Susan/Archie).
- **Plan fidelity:** Stage 1 — `_timesheet_kwargs_for` always returns a row; zero counts/cost on raise with `logger.exception` per plan. Stage 2 — non-blocking daemon thread with `copy_context`; routing via `get_model_routing != "direct"` (no `"openrouter"` literal); retry/backoff from config constants; `provider_name` → writer `host`; closed-ledger-only refresh with dispatcher `entity_cost` rule; outer `logger.exception` swallows reconcile faults.
- **AC grep:** `'"openrouter"'` absent from `src/external/`, `src/core/timesheets.py`, `src/data/database.py` on tip.
- **Estimate:** Confirm **3** — two product modules + Betty core/external tests fits.
- **Tests:** `test_delegates_to_database_add` revised with direct model + reconcile stub; AC 3–6 coverage in `test_llm_compat.py` / `core/test_timesheets.py` per plan § Test impact.

## What's solid

- Recording path never blocks on platform lookup; reconcile isolation keeps LLM callers unaffected.
- Exactly one give-up `warning` per failed reconcile (after five tries); no-key path is a single warning with id + batch.
- Ledger refresh recomputes from `sum_cost_by_batch` only when `completed_at` is set — idempotent and aligned with platform-first totals from AST-1965.

## Recommended actions (downstream — not for Radia)

- Chuckles: append artifact, `docs(AST-1966): Radia review — clean`, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** to **User Testing**.
- If parent UAT exercises batch-close vs late reconcile timing, track Joan’s residual-race note on AST-1963 — not resolve-child on this frozen canon list.
