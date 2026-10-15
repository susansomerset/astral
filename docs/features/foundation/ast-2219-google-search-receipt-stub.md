# AST-2219 — Google search calls and receipt stub

- **Linear:** [AST-2219](https://linear.app/astralcareermatch/issue/AST-2219)
- **Parent:** [AST-2215](https://linear.app/astralcareermatch/issue/AST-2215) — Add task `fetch_timesheet`
- **Publish ref:** `sub/AST-2215/AST-2219-google-search-receipt-stub`

After AST-2217 / AST-2218: each Google CSE query writes one `DISPATCH_SEARCH` `service_timesheet` row (via the existing `record_search_timesheet_entry`), `google_cse.get_receipt` is the zero stub (receipt cost empty), and the fetch runner routes / key-gates `google_cse` so those rows can stub-receipt. Does **not** own provision, OpenRouter billed receipts, daemon retirement, or contact ledger wrapping.

## Explicit scope gate

Files and change kinds match this ticket’s amended **## Scope** (includes `timesheets.py` after Chuckles cleared `[scope-gate]`). Test / bible paths are Betty (`qa-child`); engineer commits product only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/google_cse.py` | Zero-stub `get_receipt`; `search_google_cse` returns hits + call_start / call_stop / hit_count | external |
| `src/core/timesheets.py` | Route `google_cse` in `_get_receipt_fn`; key exception for search provider; optional entity on `record_search_timesheet_entry` | core |
| `src/core/roster.py` | Both CSE call sites record through `record_search_timesheet_entry` using returned timing + entity | core |
| `tests/component/external/test_google_cse.py`, `docs/test-bible/external/google_cse.md` | Betty | test/bible |
| `tests/component/core/test_roster.py`, `docs/test-bible/core/roster.md` | Betty | test/bible |
| `tests/component/core/test_timesheets.py`, `docs/test-bible/core/timesheets.md` | Betty | test/bible |

## Stage 1: `google_cse` return shape + zero-stub `get_receipt`

**Done when:** `get_receipt(["x","y"], key)` returns two dicts whose keys are exactly `TIMESHEET_RECEIPT_FIELDS`, tokens/status filled, `platform_cost is None`, no HTTP; `search_google_cse` returns a structured result with `hits`, `call_start`, `call_stop`, `hit_count` (and early/empty paths still fill timing).

1. In `src/external/google_cse.py`, add a `TypedDict` (name flexible, e.g. `GoogleCseSearchResult`) with keys:
   - `hits: list[GoogleCseHit]`
   - `call_start: str` (UTC ISO)
   - `call_stop: str` (UTC ISO, ≥ start)
   - `hit_count: int` (equal to `len(hits)` after any max_results trim)

2. Change `search_google_cse` return type from `list[GoogleCseHit]` to that TypedDict. Capture `call_start` at function entry (`datetime.now(timezone.utc).isoformat()`); set `call_stop` on every exit path (success, empty items, max-results trim, pagination break). Prefer one helper that builds `{hits, call_start, call_stop, hit_count}` so early `return hits[:max_results]` sites do not forget timing.

3. Update `__all__` to export `get_receipt` and the result TypedDict (keep `GoogleCseHit`, `search_google_cse`).

4. Add `get_receipt(external_ids: list[str], api_key: str) -> list[dict]` matching AST-2217 Anthropic stub: one row per id, keys exactly `TIMESHEET_RECEIPT_FIELDS`, token fields `0`, `platform_cost=None`, `completion_status="stub"`, no network, `api_key` ignored. Docstring: zero stub until search pricing exists (AST-2215).

⚠️ **Decision:** Structured return object (not a bare list + side channel). Only in-repo product callers of `search_google_cse` are the two `roster.py` sites (Scope); both are updated in Stage 3. Tests that call CSE are Betty’s.

## Stage 2: Timesheets — route, key exception, entity on recorder

**Done when:** `_get_receipt_fn(TIMESHEET_SEARCH_SERVER_ID)` returns `google_cse.get_receipt`; `run_fetch_timesheet` does **not** skip `google_cse` for missing candidate API key (calls stub with `""`); `record_search_timesheet_entry(..., entity_type=..., entity_id=...)` persists those columns.

1. In `src/core/timesheets.py` `record_search_timesheet_entry`, add optional kwargs `entity_type: Optional[str] = None`, `entity_id: Optional[str] = None` and pass them into `record_timesheet_entry` (replace the hard-coded `None`s). Defaults keep prior behavior for any existing callers/tests.

2. In `_get_receipt_fn`, before the llm_compat fallback:

```python
if provider == TIMESHEET_SEARCH_SERVER_ID:  # "google_cse"
    from src.external.google_cse import get_receipt
    return get_receipt
```

3. In `run_fetch_timesheet`’s per-provider loop, when resolving the key: if `provider == TIMESHEET_SEARCH_SERVER_ID`, set `key = ""` (or `_api_key_for_server(...) or ""`) and **do not** `continue` on missing candidate key. All other providers keep the existing warning + skip. Stub ignores the key; shared `get_receipt(ids, key)` signature stays.

⚠️ **Decision:** Key exception is provider-specific only — do not weaken the candidate-key gate for LLM servers. Empty string satisfies the call signature without inventing a fake CSE secret in `candidate_api_keys`.

**Boundaries (this stage):** Do not change OpenRouter / Anthropic / llm_compat routing, claim/`finally` logic, provision, or config.

## Stage 3: Roster — both CSE sites record search rows

**Done when:** After a successful `search_google_cse` in either site, one `DISPATCH_SEARCH` row exists for the candidate + current `batch_id` with `response_item_count == hit_count`, all token/`calc_cost_*` zero, and entity filled per site; existing `logger.debug` Calling/Response lines remain (`stat.logging.debug`); skipped-website path (no CSE call) records nothing.

1. Import `record_search_timesheet_entry` from `src.core.timesheets` in `src/core/roster.py`.

2. **`resolve_company_website`** (CSE call ~692):
   - Unpack `result = search_google_cse(...)` → `hits = result["hits"]` (rest of function keeps using `hits` as today).
   - After a successful return from CSE (including zero hits), call:

```python
record_search_timesheet_entry(
    candidate_id=(entity.get("candidate_id") or "").strip() or None,
    batch_id=log_batch_id.get(),
    hit_count=result["hit_count"],
    call_start=result["call_start"],
    call_stop=result["call_stop"],
    entity_type="company",
    entity_id=short_name,
)
```

   - On `RuntimeError` / `ValueError` from CSE: do **not** record (no completed call). Keep existing warn + failure return.
   - Early skip when `company_website` already set: no CSE, no timesheet row.

3. **`run_inflow_discovery_batch`** (CSE call ~804, per term):
   - Same unpack; after each successful CSE (including zero hits for that term), record:

```python
record_search_timesheet_entry(
    candidate_id=candidate_id,
    batch_id=batch_id,
    hit_count=result["hit_count"],
    call_start=result["call_start"],
    call_stop=result["call_stop"],
    entity_type="candidate",
    entity_id=candidate_id,
)
```

   - On per-term CSE exception: no record for that term (existing continue path).

⚠️ **Decision:** Record on zero-hit successes too — the query is still a billable/attributable call (tokens 0, item count 0). Matches “each Google search query writes one row.”

## Boundaries

- No `dispatcher.py` / OpenRouter billed path / contact ledger / config registries.
- No daemon reconcile work.
- Engineer does not commit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 2 — agree
