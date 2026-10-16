# AST-2218 — `fetch_timesheet` task, OpenRouter receipts, daemon retired

- **Linear:** [AST-2218](https://linear.app/astralcareermatch/issue/AST-2218)
- **Parent:** [AST-2215](https://linear.app/astralcareermatch/issue/AST-2215) — Add task `fetch_timesheet`
- **Publish ref:** `sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire`

After AST-2217 (`service_timesheet`, attribution, stub `get_receipt` on Anthropic / llm_compat). Adds the per-candidate `fetch_timesheet` dispatch row (ensure / provision / AUTO due on `NEW` ledger count), OpenRouter billed `get_receipt`, the core runner that walks `NEW` → `FETCHING` → `RECEIPTED`/`NEW`, a search-call recorder for AST-2219, and retires the OpenRouter daemon reconcile threads. Does **not** wire Google search recording call sites (AST-2219) or contact ledger wrapping (AST-2220).

## Explicit scope gate

Files and change kinds below match this ticket’s amended **## Scope**. Test / bible paths are Betty (`qa-child`); engineer stages commit **product** files only (pre-commit bans `tests/` / `docs/test-bible/**`). Leave `TIMESHEET_*_RECONCILE*` in `config.py` (unused after daemon removal). Do **not** remove `count_pending_gen_platform_timesheets` / `list_pending_gen_platform_timesheets` in `database.py` (not in Scope — go dead by unused callers).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `dispatch_task_admin_defaults` fold for `fetch_timesheet`; optional `is_fetch_timesheet_task_key` | utils |
| `src/external/openrouter.py` | Billed `get_receipt`; retire `get_generation_stats` / `get_generation_record` | external |
| `src/core/timesheets.py` | Runner; search-call recorder; `record_timesheet_entry` thread-free; remove daemon reconcile | core |
| `src/core/dispatcher.py` | Ensure / provision; `_tick_loop` due merge; `_dispatch_one_body` routing; ledger close → `NEW`, no thread | core |
| `data/admin/agent_task.json` | `fetch_timesheet` row (empty prompts, `fetch_website` shape) | data |
| `scripts/migrations/provision_fetch_timesheet_dispatch_tasks.py` | **New** — call dispatcher provision once | scripts |
| `tests/component/external/test_openrouter.py`, `docs/test-bible/external/openrouter.md` | Betty | test/bible |
| `tests/component/core/test_timesheets.py`, `docs/test-bible/core/timesheets.md` | Betty | test/bible |
| `tests/component/core/test_dispatcher.py`, `docs/test-bible/core/dispatcher.md` | Betty | test/bible |

**Out of this ticket:** `google_cse.py` / `roster.py` (AST-2219), `contact.py` (AST-2220), schema rename / Anthropic stubs (AST-2217 already landed).

## Stage 1: Config fold + `agent_task.json` catalog row

**Done when:** `dispatch_task_admin_defaults("fetch_timesheet")` returns `{entity_type: None, trigger_state: None, sort_by: None, batch_call_mode: 0}` without KeyError; `data/admin/agent_task.json` contains one `fetch_timesheet` row with empty prompts; reconcile constants in `config.py` are byte-identical to tip before this stage.

1. In `src/utils/config.py`, in `dispatch_task_admin_defaults`, **immediately after** the meteorite-mailbox fold (before the `tk not in TASK_CONFIG` agent_task helper path), add:

```python
    if tk == FETCH_TIMESHEET_CONFIG["task_key"]:
        return {
            "entity_type": FETCH_TIMESHEET_CONFIG["entity_type"],
            "trigger_state": FETCH_TIMESHEET_CONFIG["trigger_state"],
            "sort_by": None,
            "batch_call_mode": 0,
        }
```

2. Same file, near `is_meteorite_email_mailbox_task_key`, add:

```python
def is_fetch_timesheet_task_key(task_key: str) -> bool:
    return (task_key or "").strip() == FETCH_TIMESHEET_CONFIG["task_key"]
```

3. Do **not** edit `TIMESHEET_RECONCILE_*` / `TIMESHEET_BATCH_RECONCILE_*`.

4. In `data/admin/agent_task.json`, append one object (stable `task_key_uuid` — mint once with `uuid4`, do not regenerate on edits):

| Field | Value |
|-------|-------|
| `task_key` / `task_name` | `fetch_timesheet` |
| `agent_id` | `""` |
| all prompt fields | `""` |
| `run_next` | `""` |
| `current` | `1` |
| `task_group_name` | `Service Timesheet` |
| `task_group_order` | `"7000"` |
| `task_seq` | `1` |
| `updated_at` | ISO-ish stamp consistent with peers |

⚠️ **Decision:** Catalog group `Service Timesheet` / `7000` — not Company Roster — so the poller is not mistaken for a website fetch hop. Shape (empty prompts, no agent) matches parent “same shape as `fetch_website`” without stealing that group.

## Stage 2: OpenRouter billed `get_receipt`

**Done when:** `get_receipt(["id-ok","id-404"], key)` with stubbed HTTP (200 body `data.total_cost=0.0123` vs 404) returns two dicts whose keys are exactly `TIMESHEET_RECEIPT_FIELDS`; first has `platform_cost=0.0123` and filled native token fields from the stub body; second has `platform_cost is None` and `completion_status` signaling error/not-ready; nothing raises; `get_generation_stats` / `get_generation_record` are gone from the module and `__all__`.

1. In `src/external/openrouter.py`, replace `get_generation_stats` and `get_generation_record` with:

```python
def get_receipt(external_ids: List[str], api_key: str) -> List[Dict[str, Any]]:
    """One receipt per generation id in TIMESHEET_RECEIPT_FIELDS shape. Never raises. No DB."""
```

2. For each id in `external_ids` (order preserved):
   - Call existing `_fetch_generation_data(id, api_key)` (keep that private helper; retarget its `require_controlled_external_io` label to `"openrouter.get_receipt"`).
   - On success with `data.get("total_cost") is not None`: build a dict with every `TIMESHEET_RECEIPT_FIELDS` key — Astral half (`request_type`, `candidate_id`, `entity_*`, timing, sizes) left `None` / `0` as appropriate; vendor half from `data` (`platform_cost=float(total_cost)`, `native_tokens_prompt` / `_completion` / `_cached` from data, `cache_write_tokens=0` if absent, `completion_status="success"`).
   - On HTTP failure / empty data / missing `total_cost`: same key set, `platform_cost=None`, `completion_status="error"` (or `"not_ready"` when the body is empty / no cost — pick one string and use it consistently). **Do not** add undeclared keys (no `"error"` field outside the registry).
   - Never raise out of `get_receipt`.

3. Update module docstring / `__all__` → `["probe_host", "get_batch_host", "get_receipt"]`. Delete `get_generation_stats` and `get_generation_record` entirely.

4. Grep `src/` for `get_generation_stats` / `get_generation_record` — only Stage 3 may still reference them until those call sites are removed in the same ticket; after Stage 3 both greps must be empty.

⚠️ **Decision:** Shared receipt shape is exactly `TIMESHEET_RECEIPT_FIELDS` (AC5). OpenRouter `provider_name` / `native_tokens_reasoning` are **not** on that list — Stage 3’s `update_timesheet_platform` write passes `host=None` and `native_tokens_reasoning=None` (or omit writing those columns’ prior values by passing None). Do not widen the registry here (`config.py` registries are AST-2217).

## Stage 3: Timesheets runner, search recorder, daemon retired

**Done when:** `rg` checks in parent AC1 pass for `src/core/timesheets.py` (no reconcile symbols, no `threading.Thread`); `run_fetch_timesheet(candidate_id)` (name may match) implements AC6/7/10 behavior against stubbed `get_receipt`; `record_timesheet_entry` only writes; search recorder exists for AST-2219.

1. Rewrite `src/core/timesheets.py` module docstring: candidate-bound `fetch_timesheet` runner; no daemon threads.

2. **`record_timesheet_entry`:** call `_add_timesheet_entry(**kwargs)` only. Remove the `TIMESHEET_RECONCILE_ENABLED` branch and any `threading.Thread` start.

3. **Delete** entirely: `start_batch_openrouter_platform_reconcile`, `reconcile_pending_gen_platform`, `reconcile_timesheet_platform`, `_sleep_until`, `_try_reconcile_gen_row`, `_refresh_closed_batch_ledger_total` (refresh lives inside the runner), and imports of `get_generation_*`, reconcile config flags, `contextvars`, `threading`, `time` if unused, `count_pending_gen_*` / `list_pending_gen_*`.

4. **Keep / add** `_openrouter_key_for_candidate` (or equivalent) reading `candidate_api_keys[server_id]`.

5. **Search-call recorder** — new function (exact name flexible), e.g. `record_search_timesheet_entry(candidate_id, batch_id, hit_count: int, **optional)`:
   - Writes one `service_timesheet` row via `_add_timesheet_entry` / `record_timesheet_entry` with `request_type="DISPATCH_SEARCH"`, `provider=TIMESHEET_SEARCH_SERVER_ID` (`google_cse`), all token / `calc_cost_*` = 0, `response_item_count=hit_count`, attribution timing/status as available.
   - **Do not** call it from `roster.py` here (AST-2219).

6. **Runner** — `run_fetch_timesheet(candidate_id: str) -> Dict[str, int]` returning dispatcher summary keys (`total_processed`, `total_passed`, `total_failed`, `total_errors`):

   a. `batch_ids = claim_ledger_timesheet_fetching(candidate_id)` (`NEW` → `FETCHING`). If empty, return zeros.
   b. `rows = list_timesheet_rows_for_batches(batch_ids)`.
   c. Group rows by `provider` (server id). Resolve API key per server from `get_candidate(candidate_id)["candidate_api_keys"]`.
   d. Per server group, choose `get_receipt`:
      - `provider == "openrouter"` → `src.external.openrouter.get_receipt`
      - `provider == "anthropic"` → `src.external.anthropic.get_receipt`
      - else → `src.external.llm_compat.get_receipt` (direct DeepSeek/Kimi/etc.)
   e. **Logging (statutes by id):** `logger.debug` begin/end of the run and each `get_receipt` request/response; `logger.warning` when a server has no candidate key (skip that group’s ids — leave unreceipted) and when an id fails (error / not-ready, not merely stub); on thrown exception once at the handler via `logger.exception` / `error_exc` pattern used elsewhere in core.
   f. For each receipt result aligned to an `agent_req_id`:
      - **Receipted (billed):** `completion_status` success-like and `platform_cost is not None` → `update_timesheet_platform(agent_req_id, platform_cost, native_tokens_*, None, None, host=None)` (map token fields from receipt; `cache_write_tokens` is not a platform column — ignore for this write).
      - **Stub-complete:** receipt applied with `platform_cost is None` and `completion_status` not error/not_ready (Anthropic / llm_compat stubs use `"stub"`) → still call `update_timesheet_platform(..., platform_cost=None, ...)` so `platform_reconciled_at` stamps; counts as receipted for ledger state.
      - **Not receipted:** error / not_ready → do **not** write platform columns; row stays unreceipted.
   g. Per `batch_id` in the claim set: if **every** timesheet row for that batch is receipted (including vacuously when the batch has zero timesheet rows) → `set_ledger_timesheet_state(batch_id, "RECEIPTED")`; else → `set_ledger_timesheet_state(batch_id, "NEW")`.
   h. For each batch that ended `RECEIPTED` (or any closed ledger among the claim set that gained platform cost): if `get_dispatch_ledger(batch_id)` has `completed_at`, recompute `total_cost = sum_cost_by_batch([batch_id])[batch_id]`, `entity_cost = total_cost / total_processed` (or total when processed is 0), `update_dispatch_ledger(...)`.
   i. **`finally`:** any ledger row still in `FETCHING` for this candidate (exception / early exit) → `set_ledger_timesheet_state(..., "NEW")` (`patt.entity.batch-processing` release at ledger-row grain).
   j. Counts: `total_processed` = number of timesheet rows considered; `total_passed` = receipted; `total_failed` = not-ready/error ids; `total_errors` = 1 if the run raised before completion else 0.

7. If `get_receipt` **raises** (must not for OpenRouter/stubs, but defend): `finally` restores `NEW`; do not leave `FETCHING`.

⚠️ **Decision:** Routing by `provider` column (server id), not `get_model_routing` — OpenRouter-routed calls already store `provider="openrouter"`; direct servers store their own id. Matches AC6 “no other candidate’s row is passed to the stub” (only this candidate’s claimed batch rows are listed).

## Stage 4: Dispatcher ensure / due / route / ledger close

**Done when:** Provision over N candidates yields exactly one `fetch_timesheet` row each with `entity_type`/`trigger_state`/`freq_hrs` NULL and `auto_mode=0`; second provision adds 0; AUTO due merge includes the row iff `count_ledger_timesheet_state(cid, "NEW") >= min_count`; completing any dispatch ledger sets `timesheet_state="NEW"` and starts no reconcile thread; `_dispatch_one_body` routes `fetch_timesheet` to the runner.

1. In `src/core/dispatcher.py`, import `FETCH_TIMESHEET_CONFIG`, `is_fetch_timesheet_task_key` from config. **Remove** `from src.core.timesheets import start_batch_openrouter_platform_reconcile`.

2. **`ensure_fetch_timesheet_dispatch_task(candidate_id) -> dict`** — twin of `ensure_meteorite_email_dispatch_task`:
   - Require non-empty `candidate_id`.
   - **Do not** gate on `task_key in TASK_CONFIG` (mailbox’s check always skips pollers excluded from `TASK_CONFIG` — that bug must not be copied). Gate only on config task_key present.
   - If a row with `task_key == FETCH_TIMESHEET_CONFIG["task_key"]` already exists for the candidate → `{added: 0, skipped: 1, id: ...}`.
   - Else `database.save_dispatch_task(candidate_id=cid, task_key=tk, min_count=int(FETCH_TIMESHEET_CONFIG["min_count"]), auto_mode=bool(FETCH_TIMESHEET_CONFIG["auto_mode"]), entity_type=FETCH_TIMESHEET_CONFIG["entity_type"], trigger_state=FETCH_TIMESHEET_CONFIG["trigger_state"], batch_size=int(FETCH_TIMESHEET_CONFIG["batch_size"]), freq_hrs=FETCH_TIMESHEET_CONFIG["freq_hrs"])` — pass **`freq_hrs=None`** so the column is SQL NULL (AC3). `save_dispatch_task` already INSERT-binds the value; admin-defaults fold from Stage 1 supplies null entity/trigger.

3. **`provision_fetch_timesheet_dispatch_tasks() -> dict`** — twin of mailbox provision without retire/rewrite: ensure on `template_candidate_id()` then every `list_candidates()` id; return aggregated `added` / `skipped` / `candidates_touched` / `template_candidate_id`.

4. **`_fetch_timesheet_due_tasks() -> List[dict]`** — parallel to `_meteorite_email_due_tasks`, simpler (no inbox bind, no sweep):
   - AUTO rows where `is_fetch_timesheet_task_key` and bound `candidate_id`.
   - `avail = database.count_ledger_timesheet_state(cid, "NEW")`.
   - Include when `avail >= (task.min_count or 1)` and `database.dispatch_task_freq_allows(task)` (`freq_hrs` NULL → always allows).
   - Set `task["available_count"] = avail`. No sweep branch.

5. In `_tick_loop`, change due merge to:
   ```python
   due = list(database.get_due_tasks()) + _meteorite_email_due_tasks() + _fetch_timesheet_due_tasks()
   ```

6. In `_dispatch_one_body`, add a branch **before** mailbox / unified (peer mailbox structure):
   - When `is_fetch_timesheet_task_key(task_key)`: require bound `candidate_id`; mint `entity_batch_id`; `save_dispatch_ledger(..., entity_type=None)`; call `run_fetch_timesheet(ledger_cid)` (sync function — `await asyncio.to_thread(...)` or call directly if the runner is sync and the event loop allows; prefer `asyncio.to_thread` to avoid blocking the loop); fold summary into `accumulated`; `_persist_dispatch_ledger_close` in `finally`; update `last_run_at`. Task-completed INFO line stays on `_persist_dispatch_ledger_close` / `_log_dispatch_task_completed` (`stat.logging.info.dispatcher`).

7. In `_persist_dispatch_ledger_close`:
   - Add `timesheet_state="NEW"` to the `update_dispatch_ledger(...)` kwargs (every close after deploy; historical null rows untouched).
   - **Delete** the `start_batch_openrouter_platform_reconcile(...)` call.

## Stage 5: Provision migration script

**Done when:** `python scripts/migrations/provision_fetch_timesheet_dispatch_tasks.py` from repo root prints the provision return dict and exits 0 (idempotent).

1. Create `scripts/migrations/provision_fetch_timesheet_dispatch_tasks.py`:

```python
#!/usr/bin/env python3
"""One-off: ensure every candidate (and template) has a fetch_timesheet dispatch_task row (AST-2218)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.core.dispatcher import provision_fetch_timesheet_dispatch_tasks

if __name__ == "__main__":
    print(provision_fetch_timesheet_dispatch_tasks())
```

## Boundaries

- No `roster.py` / `google_cse.py` / `contact.py`.
- No removal of reconcile **constants** in `config.py` or pending-gen **helpers** in `database.py`.
- Engineer does not commit `tests/` or `docs/test-bible/**`.
- Parent AC2 / AC8 already satisfied by AST-2217 (regression only). Parent AC9 is AST-2220 — out of scope.

## Traceability

| Parent AC | This plan |
|-----------|-----------|
| 1 No cost threads | Stage 3 delete + Stage 4 drop import/call |
| 2 `service_timesheet` | AST-2217 (no change; do not regress) |
| 3 One row per candidate | Stages 1, 4, 5 |
| 4 `NEW` availability / due | Stage 4 due merge + ledger close `NEW` |
| 5 Shared `get_receipt` shape | Stage 2 (OpenRouter billed); stubs already AST-2217 |
| 6 Runner state walk | Stage 3 |
| 7 Stub null cost keeps calc | Stage 3 + existing `sum_cost_by_batch` |
| 8 Attribution | AST-2217 |
| 9 Contact ledger | AST-2220 |
| 10 Closed ledger catch-up | Stage 3 recompute |

## Estimate

Confirm Chuckles estimate: 5 — agree

## Review (build)

**Built @ `bcfc70a72`** — `origin/sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire` (`bcfc70a72db7154e79897a673d5eaff2f5e4a66d`)

- Stage 1: `dispatch_task_admin_defaults` fold + `is_fetch_timesheet_task_key`; `agent_task.json` `fetch_timesheet` row; reconcile constants untouched.
- Stage 2: OpenRouter billed `get_receipt` (shared `TIMESHEET_RECEIPT_FIELDS`); `get_generation_stats` / `get_generation_record` retired.
- Stage 3: `run_fetch_timesheet` NEW→FETCHING→RECEIPTED/NEW; search recorder; `record_timesheet_entry` thread-free; daemon reconcile removed.
- Stage 4: ensure/provision; `_fetch_timesheet_due_tasks` + tick merge; `_dispatch_one_body` route; ledger close sets `timesheet_state=NEW`, no reconcile thread.
- Stage 5: `scripts/migrations/provision_fetch_timesheet_dispatch_tasks.py`.
- Out of scope: Google/roster (AST-2219), contact ledger (AST-2220). Betty owns test/bible in Scope.

## Joan validate

```text
[plan-rubric]
**Ticket:** AST-2218
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire` @ `2beb713da2b44e3f3862186af0215f4079b35806`

## Canon scores

patt.entity.batch-processing | A | | 
stat.dispatch.entity-state-bound | A | | 
stat.logging.info.dispatcher | A | | 
stat.logging.warning | A | | 
stat.logging.error | A | | 
stat.logging.debug | A | | 

## Traceability

Child AC 1→S3–S4; 2→N/A (#1 regression); 3→S1,S4,S5; 4→S4; 5→S2 (+#1 stubs); 6–7,10→S3; 8→N/A (#1); 9→N/A (#4); plan `## Traceability` table matches; no orphan stages.

## Findings

### acceptable — Scope gate (`dispatch_task_admin_defaults`)

- **Severity:** acceptable
- **Location:** `[scope-gate]`; Stage 1; ticket `## Scope`
- **Finding:** `fetch_timesheet` KeyError without mailbox-style fold would break AC3; amended Scope + Stage 1 mirror `METEORITE_EMAIL_MAILBOX_CONFIG` pattern with `FETCH_TIMESHEET_CONFIG`.
- **Recommendation:** None.

### discuss — Build ordering vs AST-2217

- **Severity:** discuss
- **Location:** Preamble; Stages 2–4 (`TIMESHEET_*`, `claim_ledger_*`, stubs)
- **Finding:** Runner assumes AST-2217 schema/helpers and Anthropic/llm_compat stubs on the integration branch.
- **Recommendation:** Merge/build #1 before #2; Betty AC2/8 are regression-only on this sub.

### discuss — Canon Scope gap (`astral.config.config-source-of-truth`)

- **Severity:** discuss
- **Location:** Stage 1 (`config.py` fold); `agent_task.json`
- **Finding:** New catalog row + admin defaults fold are config SSOT work; id not on frozen Citations list.
- **Recommendation:** Archie may amend Canon Scope for Radia comparability; plan already centralizes in `config.py` / `agent_task.json`.

### discuss — Vacuous `RECEIPTED` when a batch has zero timesheet rows

- **Severity:** discuss
- **Location:** Stage 3g (`every row receipted` including empty batch)
- **Finding:** Logical ∀ over zero rows marks `RECEIPTED`; parent AC6 wording is “all its **calls**” — edge case if a closed ledger has no rows yet.
- **Recommendation:** Engineer/Betty: if AC6 test uses batches with calls only, no change; else tighten g to require ≥1 row or explicit product rule.

### acceptable — Search recorder without roster wiring

- **Severity:** acceptable
- **Location:** Stage 3.5; Boundaries
- **Finding:** `record_search_timesheet_entry` lands for AST-2219; no scope creep into `roster.py`.
- **Recommendation:** None.

### acceptable — Child AC carries parent slices owned by siblings

- **Severity:** acceptable
- **Location:** Ticket AC 2, 5 (CSE stub), 8, 9
- **Finding:** Copied parent AC set for epic parity; plan Boundaries + Traceability mark #1/#3/#4 ownership correctly.
- **Recommendation:** Betty manifests should scope tests to this sub’s greps/files where possible.

context_tokens≈42000
```

## Radia review

```text
[code-rubric]
**Ticket:** AST-2218
**Publish ref:** `6d2a28e8a040ffc6f5892ccf37be7af5e84bc9b4` (`origin/sub/AST-2215/AST-2218-fetch-timesheet-openrouter-daemon-retire`)
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Overall:** CLEAN

## Canon scores

patt.entity.batch-processing | A | |
stat.dispatch.entity-state-bound | A | |
stat.logging.info.dispatcher | A | |
stat.logging.warning | A | |
stat.logging.error | A | |
stat.logging.debug | A | |

## Column diff vs plan stage

(aligned) — Joan: all A @ plan tip `2beb713da2b44e3f3862186af0215f4079b35806`; build lands Stages 1–5 through tip `6d2a28e8a` (+ Betty tests/bibles).

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Provision `auto_mode=False` vs due filter** — `ensure_fetch_timesheet_dispatch_task` saves `auto_mode` from `FETCH_TIMESHEET_CONFIG` (false); `_fetch_timesheet_due_tasks` only considers rows with `auto_mode` true (same shape as `_meteorite_email_due_tasks`). Betty due test seeds `auto_mode=True` with an explicit comment. Fresh provision alone never enters the tick due merge until AUTO is enabled on the row (admin / ops).
  - **@susan:** Is CLICK-seeded `fetch_timesheet` + manual AUTO enable the intended production path, or should provision or due logic treat this poller like a special case?
  - **Default:** keep current behavior (matches mailbox seed law + plan Stage 4 “`auto_mode=0`” on provision); document ops step to enable AUTO when ready.

- **Vacuous `RECEIPTED` on zero timesheet rows** — `run_fetch_timesheet` Stage 3g: empty `batch_rows` → `all_done` true → `RECEIPTED` (comment cites plan). Joan flagged vs parent AC6 “all its calls.”
  - **Default:** no product change unless UAT hits a closed ledger with zero `service_timesheet` rows; Betty tests use batches with calls.

### advisory

- **Sibling stack in three-dot diff:** vs `origin/dev`, diff includes AST-2217 + AST-2220 (resolved) product/tests/docs plus epic plan docs — expected before siblings merge to `dev`. AST-2218-owned product surface (commits `9d92ace18`…`bcfc70a72`, plus test bible): `config.py` fold/helpers, `openrouter.py`, `timesheets.py`, `dispatcher.py`, `agent_task.json`, provision script; `contact.py` delta in range is AST-2220 resolve carry (+16 lines), not 2218 scope.
- **Canon Scope observation:** `astral.config.config-source-of-truth` governs Stage 1 fold + `agent_task.json` but is off the frozen list (Joan plan discuss unchanged).
- **Runner internal exception:** `run_fetch_timesheet` catches, logs `logger.exception`, returns `total_errors=1` without re-raising; dispatcher `fetch_timesheet` branch may still close its own run ledger as `COMPLETED` while summary carries errors — counts are in `accumulated`; confirm UAT expectations if “failed run” should flip dispatch ledger status.
- **`get_receipt` length mismatch:** `zip(ids, receipts)` silently drops trailing ids if a stub returns fewer receipts than ids — low risk if externals preserve order/length; worth a defensive assert or failed count if seen in UT.

## What's solid

- **AC1 / daemon retire:** No `threading.Thread` in `timesheets.py`; no `start_batch_openrouter_platform_reconcile` in `src/`; `get_generation_stats` / `get_generation_record` removed (comment-only mention in `openrouter.py` docstring).
- **Stage 2:** OpenRouter `get_receipt` uses `TIMESHEET_RECEIPT_FIELDS`, never raises; success / `not_ready` / `error` paths; `__all__` updated.
- **Stage 3:** `record_timesheet_entry` write-only; `run_fetch_timesheet` claim → receipt by `provider` → `update_timesheet_platform` for applied receipts (including stub null cost); per-batch `RECEIPTED` vs `NEW`; `finally` releases only rows still `FETCHING`; `record_search_timesheet_entry` for AST-2219 without roster wiring.
- **Stage 4:** `ensure_*` / `provision_*`; `_fetch_timesheet_due_tasks` + tick merge; dedicated `_dispatch_one_body` branch with `asyncio.to_thread(run_fetch_timesheet, …)`; `_persist_dispatch_ledger_close` sets `timesheet_state="NEW"` and drops reconcile thread start.
- **Stage 5:** Provision script matches plan.
- **Boundaries:** No `google_cse` / `roster` / contact ledger work in 2218 commits; reconcile constants / pending-gen DB helpers not removed.
- **Logging:** Debug joints on runner and `get_receipt`; warnings for missing keys and not-receipted ids; `error_exc` / `exception` on dispatch and runner failure paths; task-completed INFO via existing `_persist_dispatch_ledger_close` path.

## Recommended actions (Chuckles / downstream — not executed by Radia)

- Append artifact; `docs(AST-2218): Radia review — clean`; push; post slim upshot `--as radia`; **Review Posted** → datt PROCEED to User Testing if no other gates.
- Optional: capture Susan answer on `auto_mode` / due in parent or ops doc when she weighs in.

context_tokens≈45000
```
